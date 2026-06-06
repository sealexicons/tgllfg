# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

# tgllfg/fgraph.py

"""F-structure graph and unification primitive.

An f-structure is a directed graph of nodes with feature-labelled
edges. Two distinct paths from a root may reach the same node — that
is *reentrancy*, and equation solving must preserve it. The data
type is therefore not a tree of dictionaries; it is a graph of
identity-bearing nodes manipulated through a union-find disjoint-set
forest.

This module provides the graph data type (`FGraph`), value classes
(`AtomValue`, `ComplexValue`, `SetValue`), the `Diagnostic` record
returned on failure, and the unification primitive itself
(`FGraph.unify`). The orchestration that walks a c-tree applying
equations lives in :mod:`tgllfg.unify`.

Algorithm
---------

* Each node has a stable integer id allocated by `FGraph.fresh`.
* Nodes form equivalence classes under unification, maintained by a
  union-find with path compression and union-by-rank.
* The canonical root of each class carries at most one *value*
  (`AtomValue`, `ComplexValue`, or `SetValue`); other class members
  carry nothing in the value store.
* `unify(a, b)` walks both nodes to their roots, type-checks the
  values, runs an occurs-check whenever an unset slot is about to
  absorb a structured value, links by rank, transfers the merged
  value to the new root, and (for complex values) recursively
  unifies overlapping attributes.

Failure
-------

On failure the unifier returns a `Diagnostic` rather than raising.
:meth:`FGraph.unify` is atomic: on failure the graph is restored to
its pre-call state. Per Phase 6.A C5, atomicity is backed by a
**per-mutation undo journal** rather than an eager whole-graph copy.
:meth:`snapshot` is O(1) (it stores the current journal length);
:meth:`rollback` is O(mutations-since-snapshot). When no snapshot is
outstanding the journal is empty and mutations are committed by
construction. Callers that want to wrap *sequences* of unifies under
a shared rollback boundary can take their own snapshot before the
first call and roll back if any member of the sequence returns a
failure.

Path compression in :meth:`find` is skipped while a snapshot is
outstanding (``_snapshot_depth > 0``). Compressing during a
transaction could leave dangling `_parent[X] = Y` entries after a
rollback that drops `Y`, so we forgo the optimization until the
graph is back at depth 0. Find remains correct in either mode —
compression is a pure optimization.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal


type NodeId = int


# === Values ================================================================

@dataclass
class AtomValue:
    """A leaf value such as ``'NOM'`` or ``'EAT <SUBJ, OBJ>'``, or —
    Phase 5n.C.4 — a Python ``bool`` for binary feats.
    """
    atom: str | bool


@dataclass
class ComplexValue:
    """An attribute-value matrix mapping feature names to other nodes.

    The contained ``NodeId``s are not necessarily canonical roots; the
    unifier uses :meth:`FGraph.find` whenever it reads them.
    """
    attrs: dict[str, NodeId] = field(default_factory=dict)


@dataclass
class SetValue:
    """A set of f-structure nodes (used for ADJ and similar features)."""
    members: set[NodeId] = field(default_factory=set)


type FValue = AtomValue | ComplexValue | SetValue


# === Diagnostics ===========================================================

DiagKind = Literal[
    "atom-mismatch",
    "type-mismatch",
    "occurs-check",
    "constraint-failed",
    # Phase 10.M: transient marker for FU defining-eq "no endpoint"
    # failures. ``_pass_defining`` intercepts this kind and queues the
    # equation for a fixpoint re-pass after the rest of the defining
    # pass completes (parent-first evaluation may have fired the FU eq
    # before sibling/body eqs created the regex-path target). Survivors
    # of the re-pass get upgraded to ``constraint-failed`` and emitted.
    # NOT in ``NON_BLOCKING_KINDS`` — if it ever leaks past the intercept
    # it still blocks the parse, matching pre-10.M behavior.
    "fu-no-endpoint",
    # Phase 10.N: inside-out designator resolution found no parent
    # f-structure with the named feat pointing at the inner target.
    # Dalrymple 2001 ch. 14 / 15 inside-out base ``(FEAT INNER)``
    # resolves to a parent node via ``FGraph.parents_via``; when no
    # parent exists, the resolver returns this diagnostic. NOT in
    # ``NON_BLOCKING_KINDS`` — a failed inside-out resolution blocks
    # the parse (matches the legacy ``constraint-failed`` semantics
    # for binding-related failures).
    "inside-out-no-parent",
    "existential-failed",
    "neg-existential-failed",
    "neg-equation-failed",
    "set-membership-clash",
    "path-through-non-complex",
    "parse-error",
    # Well-formedness (§4.4):
    "completeness-failed",
    "coherence-failed",
    "subject-condition-failed",
    # LMT (Phase 5 §8): emitted by the LMT engine when its derived
    # role-to-GF mapping disagrees with the parsed f-structure, or
    # when biuniqueness fails. ``lmt-mismatch`` is informational
    # (the Phase 4 grammar still emits bare ``OBJ`` for non-AV
    # ng-non-pivots while the engine produces ``OBJ-θ``);
    # Subject-slot mismatches and biuniqueness violations are
    # promoted to blocking by surfacing them through
    # ``subject-condition-failed`` and ``lmt-biuniqueness-violated``
    # instead.
    "lmt-mismatch",
    "lmt-biuniqueness-violated",
    # Informational only — do not block a parse from being returned.
    "deferred",
    "unsupported",
]


# Diagnostic kinds that are informational rather than fatal: parses
# carrying only these may still be returned by the pipeline. Add
# new informational kinds here to keep the policy in one place.
NON_BLOCKING_KINDS: frozenset[str] = frozenset({
    "deferred", "unsupported", "lmt-mismatch",
})


@dataclass(frozen=True)
class Diagnostic:
    """Structured failure record. Producers populate `kind`, `message`,
    and (when meaningful) `path` and `detail`; the orchestrator in
    :mod:`tgllfg.unify` annotates `equation` and `cnode_label` so
    callers see the originating context.

    Phase 13.B breadcrumb (``/parse`` response schema): this record is
    what the API serializes for the tlfe inspector. ``cnode_label`` is
    set on equation diagnostics (``unify.py``) but not on the
    well-formedness diagnostics
    (:func:`tgllfg.fstruct.checks.lfg_well_formed`). The inspector's
    diagnostic-to-c-node anchoring wants the full c-node ↔ f-node
    correspondence (stable node refs), not a label string — design it
    with the response schema. The Phase 4 §7.9 / Phase 12.G
    ``cnode_label`` item is closed OBE in favour of that."""
    kind: DiagKind
    message: str
    path: tuple[str, ...] = ()
    equation: str | None = None
    cnode_label: str | None = None
    detail: Mapping[str, object] = field(default_factory=dict)

    def is_blocking(self) -> bool:
        """True iff this diagnostic should suppress the parse from
        being returned. Informational kinds (``deferred``,
        ``unsupported``) are non-blocking."""
        return self.kind not in NON_BLOCKING_KINDS


# === Snapshot ==============================================================

# Sentinel for "no prior entry" in journal records. Distinguishes
# "this key was missing from the dict" from "the value was None" —
# important because ``None`` is a legitimate ``_store`` absence
# marker (unset nodes don't appear in ``_store`` at all).
_MISSING: object = object()


@dataclass(frozen=True)
class Snapshot:
    """Opaque capture of an :class:`FGraph` state, suitable for rollback.

    Returned by :meth:`FGraph.snapshot` and consumed by
    :meth:`FGraph.rollback`. Internally, a snapshot is a high-water
    mark into the FGraph's undo journal: rollback unwinds all
    mutations recorded after the snapshot was taken.

    Both fields are public-but-opaque — callers should treat them as
    identifying tokens, not as introspectable graph state. A single
    snapshot may be rolled back to any number of times so long as no
    new mutations have been recorded since the previous rollback to
    it (idempotent and non-consuming under that condition).

    Node ids allocated after the snapshot become invalid after a
    rollback to that snapshot: ``_next_id`` is reset and the parent /
    rank / store entries for the dropped nodes are gone. Callers
    should not retain references to such ids across a rollback.
    """
    next_id: int
    journal_length: int


# === Graph =================================================================

class FGraph:
    """An f-structure graph with union-find and value storage.

    Atomic unify is backed by the ``_journal``: when one or more
    snapshots are outstanding (``_snapshot_depth > 0``) every
    mutation appends an undo entry to ``_journal`` before applying.
    :meth:`rollback` pops entries past the snapshot's
    ``journal_length`` and applies them. When ``_snapshot_depth``
    returns to 0 the journal is dropped — mutations outside any
    transaction are committed by construction and don't pay the
    journal cost.
    """

    def __init__(self) -> None:
        self._next_id: int = 0
        self._parent: dict[NodeId, NodeId] = {}
        self._rank: dict[NodeId, int] = {}
        self._store: dict[NodeId, FValue] = {}
        # Undo journal entries. Each is a tuple ``(kind, *args)``;
        # see :meth:`_undo` for the per-kind unwind logic.
        self._journal: list[tuple] = []
        self._snapshot_depth: int = 0

    # --- Allocation and traversal -----------------------------------------

    def fresh(self) -> NodeId:
        """Allocate a new unset node and return its id."""
        n = self._next_id
        if self._snapshot_depth:
            j = self._journal
            j.append(("next_id", self._next_id))
            j.append(("parent", n, _MISSING))
            j.append(("rank", n, _MISSING))
        self._next_id += 1
        self._parent[n] = n
        self._rank[n] = 0
        return n

    def find(self, n: NodeId) -> NodeId:
        """Return the canonical root for `n`.

        Path compression runs only outside any outstanding snapshot
        (``_snapshot_depth == 0``); inside a transaction we forgo it
        to avoid introducing dangling parent entries when the
        compression target is a post-snapshot node that gets dropped
        by a rollback.
        """
        parent = self._parent
        if self._snapshot_depth:
            while parent[n] != n:
                n = parent[n]
            return n
        path: list[NodeId] = []
        while parent[n] != n:
            path.append(n)
            n = parent[n]
        for p in path:
            parent[p] = n
        return n

    def value(self, n: NodeId) -> FValue | None:
        """Return the canonical value of `n`, or None if unset."""
        return self._store.get(self.find(n))

    # --- Direct bindings ---------------------------------------------------

    def set_atom(self, n: NodeId, atom: str | bool) -> Diagnostic | None:
        """Bind `n` to an atomic value. Idempotent if `n` already
        carries the same atom; fails with a diagnostic if it carries
        an incompatible value."""
        n = self.find(n)
        v = self._store.get(n)
        if v is None:
            if self._snapshot_depth:
                self._journal.append(("store", n, _MISSING))
            self._store[n] = AtomValue(atom)
            return None
        if isinstance(v, AtomValue):
            if v.atom == atom:
                return None
            return Diagnostic(
                "atom-mismatch",
                f"cannot bind atom {atom!r}: node already bound to {v.atom!r}",
                detail={"existing": v.atom, "new": atom},
            )
        return Diagnostic(
            "type-mismatch",
            f"cannot bind atom {atom!r}: node already has a "
            f"{type(v).__name__}",
            detail={"existing_kind": type(v).__name__, "new_kind": "AtomValue"},
        )

    def add_to_set(self, container: NodeId, member: NodeId) -> Diagnostic | None:
        """Add `member` to the set value at `container`, allocating an
        empty set first if `container` is unset."""
        container = self.find(container)
        v = self._store.get(container)
        if v is None:
            if self._snapshot_depth:
                self._journal.append(("store", container, _MISSING))
            self._store[container] = SetValue(members={member})
            return None
        if isinstance(v, SetValue):
            if member not in v.members:
                if self._snapshot_depth:
                    self._journal.append(("members", v, member))
                v.members.add(member)
            return None
        return Diagnostic(
            "set-membership-clash",
            f"cannot add to set: container already has a {type(v).__name__}",
            detail={"existing_kind": type(v).__name__},
        )

    # --- Path resolution ---------------------------------------------------

    def resolve_path(
        self,
        base: NodeId,
        features: tuple[str, ...],
    ) -> tuple[NodeId | None, Diagnostic | None]:
        """Walk a feature path from `base`, *creating* intermediate
        complex nodes as needed. Returns ``(node, None)`` on success or
        ``(None, diagnostic)`` on type clash (path through atom or set).
        Used for the lhs of defining equations."""
        cur = base
        for i, feat in enumerate(features):
            cur = self.find(cur)
            v = self._store.get(cur)
            if v is None:
                child = self.fresh()
                if self._snapshot_depth:
                    self._journal.append(("store", cur, _MISSING))
                self._store[cur] = ComplexValue(attrs={feat: child})
                cur = child
            elif isinstance(v, ComplexValue):
                if feat in v.attrs:
                    cur = v.attrs[feat]
                else:
                    child = self.fresh()
                    if self._snapshot_depth:
                        self._journal.append(("attrs", v, feat, _MISSING))
                    v.attrs[feat] = child
                    cur = child
            else:
                return None, Diagnostic(
                    "path-through-non-complex",
                    f"cannot descend through {type(v).__name__} at "
                    f"feature {feat!r}",
                    path=features[: i + 1],
                    detail={"existing_kind": type(v).__name__},
                )
        return cur, None

    def lookup_path(
        self,
        base: NodeId,
        features: tuple[str, ...],
    ) -> NodeId | None:
        """Walk a feature path from `base` *read-only*. Returns the
        final node if the full path is defined; ``None`` otherwise.
        Used for constraining/existential/negative checks in pass 2."""
        cur = base
        for feat in features:
            cur = self.find(cur)
            v = self._store.get(cur)
            if not isinstance(v, ComplexValue):
                return None
            if feat not in v.attrs:
                return None
            cur = v.attrs[feat]
        return cur

    # --- Cycle detection ---------------------------------------------------

    def occurs(self, target: NodeId, value: FValue) -> bool:
        """True if (the canonical root of) `target` is reachable from
        `value` through any chain of feature edges or set memberships."""
        target = self.find(target)
        seen: set[NodeId] = set()
        stack: list[FValue] = [value]
        while stack:
            v = stack.pop()
            if isinstance(v, AtomValue):
                continue
            children = (
                v.attrs.values() if isinstance(v, ComplexValue) else v.members
            )
            for child in children:
                root = self.find(child)
                if root == target:
                    return True
                if root in seen:
                    continue
                seen.add(root)
                cv = self._store.get(root)
                if cv is not None:
                    stack.append(cv)
        return False

    # --- Snapshot / rollback ----------------------------------------------

    def snapshot(self) -> Snapshot:
        """Capture a snapshot of the current graph state.

        Returns an opaque :class:`Snapshot` value that can be passed
        to :meth:`rollback` to undo any mutations made after this
        call. The snapshot itself is O(1): it records the current
        journal high-water mark and increments the snapshot-depth
        counter. The first outstanding snapshot is what activates the
        journal-recording fast path in mutators.
        """
        self._snapshot_depth += 1
        return Snapshot(
            next_id=self._next_id,
            journal_length=len(self._journal),
        )

    def rollback(self, snap: Snapshot) -> None:
        """Restore the graph to the state captured by ``snap``.

        Pops journal entries from the end down to
        ``snap.journal_length``, applying each undo in reverse order.
        Decrements ``_snapshot_depth``; when it returns to zero (no
        outstanding snapshots) the journal is cleared.

        Idempotent: calling :meth:`rollback` twice with the same
        ``snap`` value is a no-op on the second call when no new
        mutations have been recorded in between. ``_snapshot_depth``
        is clamped at zero on extra rollbacks so the bookkeeping
        stays consistent.
        """
        journal = self._journal
        target = snap.journal_length
        while len(journal) > target:
            self._undo(journal.pop())
        if self._snapshot_depth > 0:
            self._snapshot_depth -= 1
        if self._snapshot_depth == 0:
            journal.clear()

    def _commit(self, snap: Snapshot) -> None:
        """Discard ``snap`` without rolling back; its mutations
        become permanent (subject to any outer outstanding snapshot
        still being able to roll them back).

        Used internally by :meth:`unify` on the success path. Not part
        of the public API — external callers that want to drop a
        snapshot just let the reference go out of scope; any mutations
        they made stay in the journal until the next rollback or
        until ``_snapshot_depth`` returns to zero by some other path.
        """
        if self._snapshot_depth > 0:
            self._snapshot_depth -= 1
        if self._snapshot_depth == 0:
            self._journal.clear()

    def _undo(self, entry: tuple) -> None:
        """Apply a single journal entry's undo action."""
        kind = entry[0]
        if kind == "parent":
            _, n, old = entry
            if old is _MISSING:
                self._parent.pop(n, None)
            else:
                self._parent[n] = old
        elif kind == "rank":
            _, n, old = entry
            if old is _MISSING:
                self._rank.pop(n, None)
            else:
                self._rank[n] = old
        elif kind == "store":
            _, n, old = entry
            if old is _MISSING:
                self._store.pop(n, None)
            else:
                self._store[n] = old
        elif kind == "attrs":
            _, cv, feat, old = entry
            if old is _MISSING:
                cv.attrs.pop(feat, None)
            else:
                cv.attrs[feat] = old
        elif kind == "members":
            _, sv, member = entry
            sv.members.discard(member)
        elif kind == "next_id":
            _, old = entry
            self._next_id = old
        else:
            raise AssertionError(f"unknown journal entry kind: {kind!r}")

    # --- Unification -------------------------------------------------------

    def unify(self, a: NodeId, b: NodeId) -> Diagnostic | None:
        """Unify two nodes, returning ``None`` on success or a
        :class:`Diagnostic` on failure.

        Atomic: on failure the graph is restored to the state it held
        immediately before the call, via :meth:`snapshot` /
        :meth:`rollback`. The snapshot is committed on success
        (via :meth:`_commit`) — mutations remain in the journal only
        while an outer transaction is still outstanding. Recursive
        child unifications proceed without further snapshots; a
        single outer snapshot brackets the whole tree of child
        unifications.

        Fast path: when the two arguments already share a canonical
        root, no mutation is possible and the snapshot is skipped.
        """
        if self.find(a) == self.find(b):
            return None
        snap = self.snapshot()
        err = self._unify_inner(a, b, path=())
        if err is not None:
            self.rollback(snap)
        else:
            self._commit(snap)
        return err

    def _unify_inner(
        self,
        a: NodeId,
        b: NodeId,
        *,
        path: tuple[str, ...],
    ) -> Diagnostic | None:
        """Non-atomic core of :meth:`unify`. Mutates the graph in
        place; on failure the partial state is left intact (the
        public :meth:`unify` rolls back the outer snapshot). Recurses
        on itself, not on :meth:`unify`, so a single snapshot
        brackets the whole tree of child unifications.
        """
        ra = self.find(a)
        rb = self.find(b)
        if ra == rb:
            return None

        va = self._store.get(ra)
        vb = self._store.get(rb)

        # --- both unset
        if va is None and vb is None:
            self._link(ra, rb)
            return None

        # --- exactly one unset: occurs-check, then absorb the value
        if va is None:
            assert vb is not None
            if self.occurs(ra, vb):
                return Diagnostic(
                    "occurs-check",
                    f"unifying node {ra} would create a cycle",
                    path=path,
                    detail={"target": ra},
                )
            new_root = self._link(ra, rb)
            if new_root == ra:
                if self._snapshot_depth:
                    self._journal.append(("store", ra, _MISSING))
                    self._journal.append(("store", rb, vb))
                self._store[ra] = vb
                self._store.pop(rb, None)
            return None
        if vb is None:
            if self.occurs(rb, va):
                return Diagnostic(
                    "occurs-check",
                    f"unifying node {rb} would create a cycle",
                    path=path,
                    detail={"target": rb},
                )
            new_root = self._link(ra, rb)
            if new_root == rb:
                if self._snapshot_depth:
                    self._journal.append(("store", rb, _MISSING))
                    self._journal.append(("store", ra, va))
                self._store[rb] = va
                self._store.pop(ra, None)
            return None

        # --- both have values: type compatibility
        if type(va) is not type(vb):
            return Diagnostic(
                "type-mismatch",
                f"cannot unify {type(va).__name__} with {type(vb).__name__}",
                path=path,
                detail={
                    "left_kind": type(va).__name__,
                    "right_kind": type(vb).__name__,
                },
            )

        if isinstance(va, AtomValue):
            assert isinstance(vb, AtomValue)
            if va.atom != vb.atom:
                return Diagnostic(
                    "atom-mismatch",
                    f"cannot unify atoms {va.atom!r} and {vb.atom!r}",
                    path=path,
                    detail={"left": va.atom, "right": vb.atom},
                )
            self._link(ra, rb)
            return None

        if isinstance(va, ComplexValue):
            assert isinstance(vb, ComplexValue)
            new_root = self._link(ra, rb)
            other_root = rb if new_root == ra else ra
            new_value = va if new_root == ra else vb
            other_value = vb if new_root == ra else va
            # ``_store[new_root]`` is already ``new_value`` (the value
            # at the winning root pre-link), so the assignment is a
            # no-op and we skip journalling it. Only the pop of the
            # losing root's store entry is a real mutation.
            if self._snapshot_depth:
                self._journal.append(("store", other_root, other_value))
            self._store.pop(other_root, None)

            # Snapshot the overlap before mutating new_value.attrs so
            # recursive unifies see the unmerged child ids.
            overlap = [
                (feat, new_value.attrs[feat], other_value.attrs[feat])
                for feat in other_value.attrs
                if feat in new_value.attrs
            ]
            depth = self._snapshot_depth
            for feat, child_id in other_value.attrs.items():
                if feat not in new_value.attrs:
                    if depth:
                        self._journal.append(("attrs", new_value, feat, _MISSING))
                    new_value.attrs[feat] = child_id
            for feat, left, right in overlap:
                err = self._unify_inner(left, right, path=path + (feat,))
                if err is not None:
                    return err
            return None

        # SetValue
        assert isinstance(va, SetValue) and isinstance(vb, SetValue)
        new_root = self._link(ra, rb)
        other_root = rb if new_root == ra else ra
        new_set = va if new_root == ra else vb
        other_set = vb if new_root == ra else va
        # ``_store[new_root]`` is already ``new_set`` — same no-op
        # pattern as the ComplexValue case above.
        depth = self._snapshot_depth
        if depth:
            self._journal.append(("store", other_root, other_set))
        self._store.pop(other_root, None)
        for m in other_set.members:
            if m not in new_set.members:
                if depth:
                    self._journal.append(("members", new_set, m))
                new_set.members.add(m)
        return None

    def _link(self, ra: NodeId, rb: NodeId) -> NodeId:
        """Union-by-rank link between two distinct canonical roots.
        Returns the new root."""
        ranka = self._rank[ra]
        rankb = self._rank[rb]
        depth = self._snapshot_depth
        if ranka < rankb:
            if depth:
                self._journal.append(("parent", ra, self._parent[ra]))
            self._parent[ra] = rb
            return rb
        if ranka > rankb:
            if depth:
                self._journal.append(("parent", rb, self._parent[rb]))
            self._parent[rb] = ra
            return ra
        if depth:
            self._journal.append(("parent", rb, self._parent[rb]))
            self._journal.append(("rank", ra, self._rank[ra]))
        self._parent[rb] = ra
        self._rank[ra] = ranka + 1
        return ra

    # --- Inspection (for tests / debugging) -------------------------------

    def equiv(self, a: NodeId, b: NodeId) -> bool:
        """True if `a` and `b` belong to the same equivalence class."""
        return self.find(a) == self.find(b)

    def parents_via(self, target: NodeId, feat: str) -> list[NodeId]:
        """Phase 10.N: reverse-lookup for inside-out designators.

        Return the canonical roots of all nodes whose
        :class:`ComplexValue` has ``feat → target`` (modulo canonical
        equivalence). Deterministic insertion order — iteration over
        ``self._store`` follows CPython dict insertion order.

        Phase 11.B.4.eng extends the scan to **set-valued feats**:
        when ``v.attrs[feat]`` points to a :class:`SetValue`,
        ``target`` may appear as one of its members rather than as
        the direct edge endpoint. The extended scan checks both
        cases — direct-edge equivalence (Phase 10.N original) and
        set-membership (Phase 11.B.4.eng). The extension is
        additive: existing direct-edge consumers (10.N's sarili and
        L47-style use cases) see no behavior change. Audit doc:
        ``docs/fu-extension-audit.md`` §B.1 (shipped Phase 11.B.4.eng).

        O(N + sum-of-set-sizes) scan over the live store —
        sufficient for prototype scale (typical sentence f-graphs
        have ≤50 ComplexValue nodes and small ADJUNCT / CONJUNCTS
        sets); a materialized reverse index can replace this if
        corpus pressure on inside-out designators surfaces.

        Inside-out designators (Dalrymple 2001 ch. 14 / 15;
        ``(FEAT INNER)``-style surface form) need to traverse "upward"
        in the f-graph from a known child node to its containing
        f-structure. The graph stores attrs top-down only — the reverse
        direction is a scan.

        Multiple parents are possible when the target node is
        structure-shared across f-structures (e.g., a SUBJ shared
        between matrix and XCOMP via functional control), or when the
        target appears as a member of multiple set-valued feats; the
        resolver returns all of them in insertion order and picks the
        first for the canonical inside-out result. K&Z 1989 §3
        minimality on inside-out resolution is documented as future
        work — gated on corpus pressure.
        """
        target_root = self.find(target)
        seen: set[NodeId] = set()
        result: list[NodeId] = []
        for n, v in self._store.items():
            if not isinstance(v, ComplexValue):
                continue
            child = v.attrs.get(feat)
            if child is None:
                continue
            child_value = self._store.get(self.find(child))
            if isinstance(child_value, SetValue):
                # Phase 11.B.4.eng: target may be a SetValue member.
                # The SetValue's members are NodeIds that may not be
                # canonical roots; canonicalize before comparison.
                matched = any(
                    self.find(m) == target_root
                    for m in child_value.members
                )
                if not matched:
                    continue
            else:
                if self.find(child) != target_root:
                    continue
            n_root = self.find(n)
            if n_root not in seen:
                seen.add(n_root)
                result.append(n_root)
        return result


__all__ = [
    "NodeId",
    "AtomValue",
    "ComplexValue",
    "SetValue",
    "FValue",
    "DiagKind",
    "NON_BLOCKING_KINDS",
    "Diagnostic",
    "Snapshot",
    "FGraph",
]
