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
The graph may be left in a partial state; callers that need atomic
behaviour should snapshot before unifying. Atomic rollback is not a
§4.2 deliverable.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal


type NodeId = int


# === Values ================================================================

@dataclass
class AtomValue:
    """A leaf value such as ``'NOM'`` or ``'EAT <SUBJ, OBJ>'``."""
    atom: str


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
    "existential-failed",
    "neg-existential-failed",
    "neg-equation-failed",
    "set-membership-clash",
    "path-through-non-complex",
    "parse-error",
    "deferred",
    "unsupported",
]


@dataclass(frozen=True)
class Diagnostic:
    """Structured failure record. Producers populate `kind`, `message`,
    and (when meaningful) `path` and `detail`; the orchestrator in
    :mod:`tgllfg.unify` annotates `equation` and `cnode_label` so
    callers see the originating context."""
    kind: DiagKind
    message: str
    path: tuple[str, ...] = ()
    equation: str | None = None
    cnode_label: str | None = None
    detail: Mapping[str, object] = field(default_factory=dict)


# === Graph =================================================================

class FGraph:
    """An f-structure graph with union-find and value storage."""

    def __init__(self) -> None:
        self._next_id: int = 0
        self._parent: dict[NodeId, NodeId] = {}
        self._rank: dict[NodeId, int] = {}
        self._store: dict[NodeId, FValue] = {}

    # --- Allocation and traversal -----------------------------------------

    def fresh(self) -> NodeId:
        """Allocate a new unset node and return its id."""
        n = self._next_id
        self._next_id += 1
        self._parent[n] = n
        self._rank[n] = 0
        return n

    def find(self, n: NodeId) -> NodeId:
        """Return the canonical root for `n`, with path compression."""
        path: list[NodeId] = []
        while self._parent[n] != n:
            path.append(n)
            n = self._parent[n]
        for p in path:
            self._parent[p] = n
        return n

    def value(self, n: NodeId) -> FValue | None:
        """Return the canonical value of `n`, or None if unset."""
        return self._store.get(self.find(n))

    # --- Direct bindings ---------------------------------------------------

    def set_atom(self, n: NodeId, atom: str) -> Diagnostic | None:
        """Bind `n` to an atomic value. Idempotent if `n` already
        carries the same atom; fails with a diagnostic if it carries
        an incompatible value."""
        n = self.find(n)
        v = self._store.get(n)
        if v is None:
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
            self._store[container] = SetValue(members={member})
            return None
        if isinstance(v, SetValue):
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
                self._store[cur] = ComplexValue(attrs={feat: child})
                cur = child
            elif isinstance(v, ComplexValue):
                if feat in v.attrs:
                    cur = v.attrs[feat]
                else:
                    child = self.fresh()
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

    # --- Unification -------------------------------------------------------

    def unify(
        self,
        a: NodeId,
        b: NodeId,
        *,
        path: tuple[str, ...] = (),
    ) -> Diagnostic | None:
        """Unify two nodes, returning ``None`` on success or a
        :class:`Diagnostic` on failure. Mutates the graph in place."""
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
            self._store[new_root] = new_value
            self._store.pop(other_root, None)

            # Snapshot the overlap before mutating new_value.attrs so
            # recursive unifies see the unmerged child ids.
            overlap = [
                (feat, new_value.attrs[feat], other_value.attrs[feat])
                for feat in other_value.attrs
                if feat in new_value.attrs
            ]
            for feat, child_id in other_value.attrs.items():
                if feat not in new_value.attrs:
                    new_value.attrs[feat] = child_id
            for feat, left, right in overlap:
                err = self.unify(left, right, path=path + (feat,))
                if err is not None:
                    return err
            return None

        # SetValue
        assert isinstance(va, SetValue) and isinstance(vb, SetValue)
        new_root = self._link(ra, rb)
        other_root = rb if new_root == ra else ra
        new_set = va if new_root == ra else vb
        other_set = vb if new_root == ra else va
        self._store[new_root] = new_set
        self._store.pop(other_root, None)
        new_set.members |= other_set.members
        return None

    def _link(self, ra: NodeId, rb: NodeId) -> NodeId:
        """Union-by-rank link between two distinct canonical roots.
        Returns the new root."""
        ranka = self._rank[ra]
        rankb = self._rank[rb]
        if ranka < rankb:
            self._parent[ra] = rb
            return rb
        if ranka > rankb:
            self._parent[rb] = ra
            return ra
        self._parent[rb] = ra
        self._rank[ra] = ranka + 1
        return ra

    # --- Inspection (for tests / debugging) -------------------------------

    def equiv(self, a: NodeId, b: NodeId) -> bool:
        """True if `a` and `b` belong to the same equivalence class."""
        return self.find(a) == self.find(b)


__all__ = [
    "NodeId",
    "AtomValue",
    "ComplexValue",
    "SetValue",
    "FValue",
    "DiagKind",
    "Diagnostic",
    "FGraph",
]
