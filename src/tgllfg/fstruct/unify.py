# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

# tgllfg/unify.py

"""F-structure construction by two-pass equation solving.

This module orchestrates equation evaluation over a c-tree. It walks
the tree assigning a fresh f-graph node to each c-node, then runs
two passes over the parsed equations:

1. **Defining pass.** Apply ``DefiningEquation`` and ``SetMembership``
   against the f-graph, growing structure and unifying nodes. The
   unifier in :mod:`tgllfg.fstruct.graph` enforces uniqueness, type
   compatibility, and the occurs check on this pass. Per Phase 6.A
   C2, :meth:`FGraph.unify` is **atomic** — a failed unification
   rolls the graph back to its pre-call state via an internal
   :meth:`FGraph.snapshot` / :meth:`FGraph.rollback` pair, so a
   failed defining equation does not corrupt the graph for the
   equations that follow on the same c-node. :meth:`FGraph.set_atom`,
   :meth:`FGraph.add_to_set`, and :meth:`FGraph.resolve_path` are
   each atomic by construction (they detect the type clash before
   mutating). The orchestration here therefore does not snapshot
   around individual equation calls; it simply records diagnostics
   and proceeds.
2. **Constraint pass.** Apply ``ConstrainingEquation``,
   ``ExistentialConstraint``, ``NegExistentialConstraint``, and
   ``NegEquation`` against the *solved* graph. These never grow the
   graph; they only check that it has the required shape.

After both passes the graph is projected to a tree-shaped
:class:`FStructure` for downstream consumers (LMT, renderers, the
existing percolation test). Sub-nodes become nested ``FStructure``
objects keyed by the canonical node id, so reentrancy is detectable
by Python identity.

Public API
----------

* :func:`build_f_structure(root)` — legacy entry point used by
  :mod:`tgllfg.pipeline`. Returns the projected ``FStructure``.
* :func:`solve(root)` — full result with the live ``FGraph``, the
  root ``NodeId``, and the diagnostic list. The chart parser and the
  well-formedness module surface diagnostics through this entry
  point.

Functional uncertainty (regular-path designators) and off-path
constraints parse correctly but evaluate to a ``deferred``
diagnostic at :func:`_path_features` today; full evaluation lands
in Phase 6.B per :file:`.claude/plans/tgllfg-phase-6.md` §5.2
(``_resolve_regex_for_read``, K&Z 1989 §3 path enumeration).
"""

from dataclasses import dataclass, field, replace

from ..core.common import CNode, FStructure
from .equations import (
    Atom,
    ConstrainingEquation,
    DefiningEquation,
    Designator,
    Down,
    Equation,
    ExistentialConstraint,
    Feature,
    NegEquation,
    NegExistentialConstraint,
    ParseError,
    Right,
    SetMembership,
    Up,
    parse_equation,
    unparse,
)
from .fu import resolve_regex_for_read
from .graph import (
    AtomValue,
    ComplexValue,
    Diagnostic,
    FGraph,
    NodeId,
    SetValue,
)


type ProjectedValue = str | bool | FStructure | frozenset


@dataclass
class SolveResult:
    """Full output of the two-pass solver."""
    fstructure: FStructure
    graph: FGraph
    root: NodeId
    diagnostics: list[Diagnostic] = field(default_factory=list)


# Phase 10.M: Deferred FU defining-equation queue entry.
#
# When a defining-equation with FU-regex RHS fires during the
# parent-first walk, the regex-path target may not exist yet (the
# sibling/body equations that build it haven't run). The FU resolver
# returns no endpoint, and the legacy behavior was to fail the parse
# with ``constraint-failed``. 10.M instead queues such failures with
# enough context to re-evaluate them after the full defining pass
# completes — each retry sees the post-pass-1 graph, where missing
# path targets may now be populated.
@dataclass(frozen=True)
class _DeferredFuDef:
    up: NodeId
    children: tuple[NodeId, ...]
    eq: DefiningEquation
    eq_str: str
    cnode_label: str


def build_f_structure(root: CNode) -> FStructure:
    """Solve and return the projected f-structure (legacy API)."""
    return solve(root).fstructure


def solve(root: CNode) -> SolveResult:
    """Run the two-pass solver over a c-tree, returning the graph,
    the projected f-structure, and the diagnostic list."""
    graph = FGraph()
    diagnostics: list[Diagnostic] = []

    nid_for: dict[int, NodeId] = {}
    parsed_for: dict[int, list[tuple[str, Equation | None]]] = {}

    _assign_ids(root, graph, nid_for)
    _parse_equations(root, parsed_for, diagnostics)
    deferred_fu: list[_DeferredFuDef] = []
    _pass_defining(root, graph, nid_for, parsed_for, diagnostics, deferred_fu)
    # Phase 10.M: re-pass deferred FU defining-equations to fixpoint.
    # No-op when the queue is empty (the common case).
    _repass_deferred_fu(deferred_fu, graph, diagnostics)
    _pass_constraining(root, graph, nid_for, parsed_for, diagnostics)

    fstr = _project(graph, nid_for[id(root)])
    return SolveResult(
        fstructure=fstr,
        graph=graph,
        root=nid_for[id(root)],
        diagnostics=diagnostics,
    )


# === Phase 10.J: monotone defining-clash subtree precheck ==================

# Unification-failure kinds that **cannot be undone** by any later
# defining equation, regardless of which containing tree the subtree
# appears in. Constraining-side failures (``constraint-failed``,
# ``existential-failed``, ``neg-existential-failed``, ``neg-equation-
# failed``) are **NOT** in this set: a feature absent in this subtree
# can be defined by an ancestor's equation, making a ``=c`` pass or an
# existential check satisfy that previously failed. Likewise the
# well-formedness kinds (``completeness-failed`` etc.) are global and
# not safe to check at the subtree level.
_MONOTONE_DEF_CLASH_KINDS: frozenset[str] = frozenset({
    "atom-mismatch",
    "type-mismatch",
    "occurs-check",
    "set-membership-clash",
    "path-through-non-complex",
})


def precheck_defining_subtree(
    root: CNode,
    cache: dict[int, bool] | None = None,
) -> bool:
    """Return ``True`` iff the subtree rooted at ``root`` contains a
    blocking **monotone** defining-equation clash — meaning no
    containing tree can satisfy this subtree's defining equations
    either, so the subtree can be pruned from the forest with **no
    parse-set change**. Returns ``False`` when the defining pass is
    clean (the subtree is potentially viable; :func:`solve` over a
    containing tree may still reject it via constraining /
    well-formedness, which are non-monotone and not safe to check
    here).

    Reuses :func:`solve`'s defining pass on a fresh, isolated graph
    — same ``_assign_ids`` / ``_parse_equations`` / ``_pass_defining``
    helpers — and does **not** run the constraining pass.

    Phase 10.J (commit 3): if ``cache`` is provided, results are
    memoized keyed by ``id(root)``. The cache **must be scoped to a
    single parse session** — passing the same cache across
    independent parses risks ``id`` collision on garbage-collected
    CNodes. ``parse/earley.py:_iter_cnodes`` creates a fresh cache
    per top-level call when ``precheck_defining=True``. Hit rate is
    low when each candidate combo builds a fresh ``CNode`` (the
    current materialization pattern) but the scaffolding is in
    place for future structural-interning changes.
    """
    if cache is not None:
        cached = cache.get(id(root))
        if cached is not None:
            return cached
    graph = FGraph()
    nid_for: dict[int, NodeId] = {}
    parsed_for: dict[int, list[tuple[str, Equation | None]]] = {}
    diagnostics: list[Diagnostic] = []
    _assign_ids(root, graph, nid_for)
    _parse_equations(root, parsed_for, diagnostics)
    # Phase 10.M: precheck doesn't care about FU defer/re-pass; pass an
    # empty queue and discard it. ``fu-no-endpoint`` is not in
    # ``_MONOTONE_DEF_CLASH_KINDS``, so an FU defining-eq failing in
    # subtree isolation never inadvertently prunes a viable subtree —
    # the full ``solve`` will retry it in the containing tree.
    _deferred_fu_scratch: list[_DeferredFuDef] = []
    _pass_defining(
        root, graph, nid_for, parsed_for, diagnostics, _deferred_fu_scratch,
    )
    result = any(d.kind in _MONOTONE_DEF_CLASH_KINDS for d in diagnostics)
    if cache is not None:
        cache[id(root)] = result
    return result


# === Tree walks ============================================================

def _assign_ids(c: CNode, graph: FGraph, nid_for: dict[int, NodeId]) -> None:
    nid_for[id(c)] = graph.fresh()
    for ch in c.children:
        _assign_ids(ch, graph, nid_for)


def _parse_equations(
    c: CNode,
    parsed_for: dict[int, list[tuple[str, Equation | None]]],
    diagnostics: list[Diagnostic],
) -> None:
    out: list[tuple[str, Equation | None]] = []
    for eq_str in c.equations:
        try:
            out.append((eq_str, parse_equation(eq_str)))
        except ParseError as e:
            diagnostics.append(Diagnostic(
                "parse-error",
                e.message,
                equation=eq_str,
                cnode_label=c.label,
            ))
            out.append((eq_str, None))
    parsed_for[id(c)] = out
    for ch in c.children:
        _parse_equations(ch, parsed_for, diagnostics)


def _pass_defining(
    c: CNode,
    graph: FGraph,
    nid_for: dict[int, NodeId],
    parsed_for: dict[int, list[tuple[str, Equation | None]]],
    diagnostics: list[Diagnostic],
    deferred_fu: list[_DeferredFuDef],
) -> None:
    up = nid_for[id(c)]
    children = [nid_for[id(ch)] for ch in c.children]
    for eq_str, eq in parsed_for[id(c)]:
        if eq is None:
            continue
        if isinstance(eq, DefiningEquation):
            d = _eval_defining_eq(graph, up, children, eq)
        elif isinstance(eq, SetMembership):
            d = _eval_set_member(graph, up, children, eq)
        else:
            continue
        if d is not None:
            if d.kind == "fu-no-endpoint":
                # Phase 10.M: defer — the regex-path target may be
                # built by sibling/descendant equations later in the
                # defining pass. Captured for re-pass after the full
                # tree walk completes. The kind is only emitted by
                # ``_eval_defining_eq``'s FU branch, so the equation
                # is necessarily a ``DefiningEquation``.
                assert isinstance(eq, DefiningEquation)
                deferred_fu.append(_DeferredFuDef(
                    up=up,
                    children=tuple(children),
                    eq=eq,
                    eq_str=eq_str,
                    cnode_label=c.label or "",
                ))
            else:
                diagnostics.append(
                    replace(d, equation=eq_str, cnode_label=c.label),
                )
    for ch in c.children:
        _pass_defining(ch, graph, nid_for, parsed_for, diagnostics, deferred_fu)


def _repass_deferred_fu(
    queue: list[_DeferredFuDef],
    graph: FGraph,
    diagnostics: list[Diagnostic],
) -> None:
    """Phase 10.M: re-evaluate deferred FU defining-equations to fixpoint.

    A defining-equation with FU on the RHS may fire before the
    sibling / descendant defining-equations that build its regex-path
    target — the parent-first walk in :func:`_pass_defining` doesn't
    delay them. The FU resolver returns no endpoint, the equation is
    captured into ``queue`` instead of emitted, and this re-pass
    retries each captured item against the post-pass-1 graph.

    Each retry that succeeds may extend the graph further (the LHS
    unifies with the canonical endpoint, creating reentrancy), which
    can unblock other still-deferred items. The loop iterates until
    no progress is made in a single pass, then survivors emit a
    legacy ``constraint-failed`` diagnostic — same end-state as
    pre-10.M for genuinely unsatisfiable FU defining-equations.

    The bounded retry guard (``len(queue) + 2``) protects against
    weird non-monotonic interactions; in practice each successful
    retry strictly removes an item from the queue, so convergence is
    fast.
    """
    if not queue:
        return
    max_iters = len(queue) + 2
    for _ in range(max_iters):
        progress = False
        remaining: list[_DeferredFuDef] = []
        for item in queue:
            d = _eval_defining_eq(
                graph, item.up, list(item.children), item.eq,
            )
            if d is None:
                progress = True
            elif d.kind == "fu-no-endpoint":
                remaining.append(item)
            else:
                # The retry produced a non-FU-no-endpoint diagnostic
                # (e.g., unify clash on the now-existing endpoint).
                # Emit immediately and treat as progress so the loop
                # doesn't spin on it.
                diagnostics.append(replace(
                    d, equation=item.eq_str, cnode_label=item.cnode_label,
                ))
                progress = True
        queue[:] = remaining
        if not queue or not progress:
            break
    for item in queue:
        # Surviving items: emit the legacy ``constraint-failed``
        # diagnostic, matching pre-10.M behavior for genuinely
        # unsatisfiable FU defining-equations.
        diagnostics.append(Diagnostic(
            "constraint-failed",
            f"FU binding equation has no endpoint after deferred "
            f"re-pass: {unparse(item.eq)}",
            equation=item.eq_str,
            cnode_label=item.cnode_label,
        ))


def _pass_constraining(
    c: CNode,
    graph: FGraph,
    nid_for: dict[int, NodeId],
    parsed_for: dict[int, list[tuple[str, Equation | None]]],
    diagnostics: list[Diagnostic],
) -> None:
    up = nid_for[id(c)]
    children = [nid_for[id(ch)] for ch in c.children]
    for eq_str, eq in parsed_for[id(c)]:
        if eq is None or isinstance(eq, (DefiningEquation, SetMembership)):
            continue
        if isinstance(eq, ConstrainingEquation):
            d = _eval_constraining_eq(graph, up, children, eq)
        elif isinstance(eq, ExistentialConstraint):
            d = _eval_existential(graph, up, children, eq)
        elif isinstance(eq, NegExistentialConstraint):
            d = _eval_neg_existential(graph, up, children, eq)
        elif isinstance(eq, NegEquation):
            d = _eval_neg_equation(graph, up, children, eq)
        else:
            d = Diagnostic(
                "unsupported",
                f"unsupported equation kind: {type(eq).__name__}",
            )
        if d is not None:
            diagnostics.append(replace(d, equation=eq_str, cnode_label=c.label))
    for ch in c.children:
        _pass_constraining(ch, graph, nid_for, parsed_for, diagnostics)


# === Designator resolution =================================================

def _resolve_base(
    base: Up | Down | Right,
    up: NodeId,
    children: list[NodeId],
    *,
    right: NodeId | None = None,
) -> tuple[NodeId | None, Diagnostic | None]:
    """Resolve a base metavariable to a NodeId.

    The optional ``right`` parameter binds ``→`` to a specific node;
    it is set when evaluating off-path constraints during FU
    regex-path traversal (Phase 6.B C4). Outside an off-path
    context, ``right`` is ``None`` and ``→`` surfaces an
    ``unsupported`` diagnostic.
    """
    if isinstance(base, Up):
        return up, None
    if isinstance(base, Down):
        if base.idx is None:
            # Bare ↓ is degenerate in our lifted representation (where
            # equations live on the parent); treat it as ↑ — equivalent
            # to "the current c-node's f-structure".
            return up, None
        idx = base.idx - 1
        if 0 <= idx < len(children):
            return children[idx], None
        return None, Diagnostic(
            "unsupported",
            f"↓{base.idx}: child index out of range (have {len(children)})",
        )
    if isinstance(base, Right):
        if right is not None:
            return right, None
        return None, Diagnostic(
            "unsupported",
            "→ outside an off-path constraint",
        )
    return None, Diagnostic(
        "unsupported",
        f"unknown designator base: {type(base).__name__}",
    )


def _path_features(
    designator: Designator,
) -> tuple[tuple[str, ...] | None, Diagnostic | None]:
    """Extract a plain-feature path; deferred constructs return a
    diagnostic instead of feature names."""
    feats: list[str] = []
    for elem in designator.path:
        if not isinstance(elem, Feature):
            return None, Diagnostic(
                "deferred",
                f"regular-path step ({type(elem).__name__}) deferred to a "
                f"later phase",
            )
        if elem.off_path:
            return None, Diagnostic(
                "deferred",
                "off-path constraints deferred to a later phase",
            )
        feats.append(elem.name)
    return tuple(feats), None


def _resolve_for_write(
    graph: FGraph,
    designator: Designator,
    up: NodeId,
    children: list[NodeId],
    *,
    right: NodeId | None = None,
) -> tuple[NodeId | None, Diagnostic | None]:
    """Resolve the designator with get-or-create semantics. Used for
    the lhs of defining equations and both sides of set membership."""
    base_node, err = _resolve_base(designator.base, up, children, right=right)
    if err is not None:
        return None, err
    feats, err = _path_features(designator)
    if err is not None:
        return None, err
    assert feats is not None
    assert base_node is not None
    return graph.resolve_path(base_node, feats)


def _resolve_for_read(
    graph: FGraph,
    designator: Designator,
    up: NodeId,
    children: list[NodeId],
    *,
    right: NodeId | None = None,
) -> tuple[NodeId | None, Diagnostic | None]:
    """Resolve the designator without creating intermediate nodes.
    Returns (None, None) when the path is not defined; that is not an
    error in itself, just absence."""
    base_node, err = _resolve_base(designator.base, up, children, right=right)
    if err is not None:
        return None, err
    feats, err = _path_features(designator)
    if err is not None:
        return None, err
    assert feats is not None
    assert base_node is not None
    return graph.lookup_path(base_node, feats), None


# === Pass 1 evaluators =====================================================

def _eval_defining_eq(
    graph: FGraph,
    up: NodeId,
    children: list[NodeId],
    eq: DefiningEquation,
    *,
    right: NodeId | None = None,
) -> Diagnostic | None:
    lhs_node, err = _resolve_for_write(graph, eq.lhs, up, children, right=right)
    if err is not None:
        return err
    assert lhs_node is not None

    if isinstance(eq.rhs, Atom):
        return graph.set_atom(lhs_node, eq.rhs.value)

    # Phase 6.B C5: binding-equation context. A defining equation
    # with a regex path on the RHS is a *binding* equation in K&Z
    # 1989 terms — the RHS regex enumerates endpoints (read-only),
    # K&Z minimality selects the canonical (shortest-depth) endpoint,
    # and the equation unifies the LHS with it. The write happens via
    # ``graph.unify`` between existing nodes; the path is not
    # extended. (Regex on the LHS of a defining equation remains
    # out-of-scope per ``docs/fu-evaluation.md`` §5.3 — handled by
    # the ``_resolve_for_write`` ``deferred`` short-circuit above.)
    rhs_has_regex = any(
        not isinstance(e, Feature) for e in eq.rhs.path
    )

    if rhs_has_regex:
        base_node, err = _resolve_base(
            eq.rhs.base, up, children, right=right,
        )
        if err is not None:
            return err
        assert base_node is not None

        def off_path_eval(
            intermediate: NodeId,
            equations: tuple[Equation, ...],
        ) -> Diagnostic | None:
            return _eval_off_path(
                graph, up, children, intermediate, equations,
            )

        endpoints, err = resolve_regex_for_read(
            graph, base_node, eq.rhs.path,
            off_path_eval=off_path_eval,
        )
        if err is not None:
            return err
        if not endpoints:
            # Phase 10.M: tag with the transient ``fu-no-endpoint`` kind
            # so ``_pass_defining`` can defer (regex-path target may be
            # built by sibling / descendant equations later in pass 1).
            # Survivors of the re-pass loop get this upgraded to
            # ``constraint-failed`` (legacy kind) and emitted.
            return Diagnostic(
                "fu-no-endpoint",
                f"FU binding equation has no endpoint: {unparse(eq)}",
            )
        # K&Z 1989 §3 minimality: endpoints come back shortest-first.
        # The canonical endpoint is the first one — the shortest-depth
        # node reachable by the regex. Unify LHS with it.
        target = endpoints[0]
        return graph.unify(lhs_node, target)

    rhs_node, err = _resolve_for_write(graph, eq.rhs, up, children, right=right)
    if err is not None:
        return err
    assert rhs_node is not None
    return graph.unify(lhs_node, rhs_node)


def _eval_set_member(
    graph: FGraph,
    up: NodeId,
    children: list[NodeId],
    eq: SetMembership,
    *,
    right: NodeId | None = None,
) -> Diagnostic | None:
    elem_node, err = _resolve_for_write(
        graph, eq.element, up, children, right=right,
    )
    if err is not None:
        return err
    container_node, err = _resolve_for_write(
        graph, eq.container, up, children, right=right,
    )
    if err is not None:
        return err
    assert elem_node is not None and container_node is not None
    return graph.add_to_set(container_node, elem_node)


# === Pass 2 evaluators =====================================================

def _eval_constraining_eq(
    graph: FGraph,
    up: NodeId,
    children: list[NodeId],
    eq: ConstrainingEquation,
    *,
    right: NodeId | None = None,
) -> Diagnostic | None:
    lhs_node, err = _resolve_for_read(graph, eq.lhs, up, children, right=right)
    if err is not None:
        return err
    if lhs_node is None:
        return Diagnostic(
            "constraint-failed",
            f"constraining equation lhs is undefined: {unparse(eq)}",
        )
    lhs_val = graph.value(lhs_node)

    if isinstance(eq.rhs, Atom):
        if isinstance(lhs_val, AtomValue) and lhs_val.atom == eq.rhs.value:
            return None
        return Diagnostic(
            "constraint-failed",
            f"constraining equation does not hold: {unparse(eq)}",
            detail={
                "expected": eq.rhs.value,
                "actual": _value_summary(lhs_val),
            },
        )

    # Phase 6.B C3/C4: regex-path RHS routes through the FU resolver
    # in :mod:`tgllfg.fstruct.fu`. C4 also supplies an off-path
    # evaluator so elements bearing off-path constraints filter the
    # FSA traversal per K&Z 1989 §3 (off-path constraints live on
    # the intermediate nodes themselves).
    rhs_has_regex = any(
        not isinstance(e, Feature) for e in eq.rhs.path
    )

    if rhs_has_regex:
        base_node, err = _resolve_base(
            eq.rhs.base, up, children, right=right,
        )
        if err is not None:
            return err
        assert base_node is not None

        def off_path_eval(
            intermediate: NodeId,
            equations: tuple[Equation, ...],
        ) -> Diagnostic | None:
            return _eval_off_path(
                graph, up, children, intermediate, equations,
            )

        endpoints, err = resolve_regex_for_read(
            graph, base_node, eq.rhs.path,
            off_path_eval=off_path_eval,
        )
        if err is not None:
            return err
        if not endpoints:
            return Diagnostic(
                "constraint-failed",
                f"constraining equation rhs FU path has no endpoint: "
                f"{unparse(eq)}",
            )
        # K&Z 1989 §3 minimality: endpoints come back shortest-first,
        # but the constraining-eq is existential (holds iff *any*
        # endpoint matches the LHS). Walk in minimality order so the
        # cheapest-match path is the one that satisfies, but
        # otherwise treat all endpoints as equally valid candidates.
        for ep in endpoints:
            if graph.equiv(lhs_node, ep):
                return None
            ep_val = graph.value(ep)
            if (
                isinstance(lhs_val, AtomValue)
                and isinstance(ep_val, AtomValue)
                and lhs_val.atom == ep_val.atom
            ):
                return None
        return Diagnostic(
            "constraint-failed",
            f"constraining equation does not hold "
            f"(no FU endpoint matches LHS): {unparse(eq)}",
            detail={
                "lhs": _value_summary(lhs_val),
                "endpoint_count": len(endpoints),
            },
        )

    rhs_node, err = _resolve_for_read(graph, eq.rhs, up, children, right=right)
    if err is not None:
        return err
    if rhs_node is None:
        return Diagnostic(
            "constraint-failed",
            f"constraining equation rhs is undefined: {unparse(eq)}",
        )
    if graph.equiv(lhs_node, rhs_node):
        return None
    rhs_val = graph.value(rhs_node)
    if (
        isinstance(lhs_val, AtomValue)
        and isinstance(rhs_val, AtomValue)
        and lhs_val.atom == rhs_val.atom
    ):
        return None
    return Diagnostic(
        "constraint-failed",
        f"constraining equation does not hold: {unparse(eq)}",
        detail={
            "lhs": _value_summary(lhs_val),
            "rhs": _value_summary(rhs_val),
        },
    )


def _eval_existential(
    graph: FGraph,
    up: NodeId,
    children: list[NodeId],
    eq: ExistentialConstraint,
    *,
    right: NodeId | None = None,
) -> Diagnostic | None:
    node, err = _resolve_for_read(
        graph, eq.designator, up, children, right=right,
    )
    if err is not None:
        return err
    if node is None:
        return Diagnostic(
            "existential-failed",
            f"path is not defined: {unparse(eq)}",
        )
    return None


def _eval_neg_existential(
    graph: FGraph,
    up: NodeId,
    children: list[NodeId],
    eq: NegExistentialConstraint,
    *,
    right: NodeId | None = None,
) -> Diagnostic | None:
    node, err = _resolve_for_read(
        graph, eq.designator, up, children, right=right,
    )
    if err is not None:
        return err
    if node is not None:
        return Diagnostic(
            "neg-existential-failed",
            f"path is unexpectedly defined: {unparse(eq)}",
        )
    return None


def _eval_neg_equation(
    graph: FGraph,
    up: NodeId,
    children: list[NodeId],
    eq: NegEquation,
    *,
    right: NodeId | None = None,
) -> Diagnostic | None:
    lhs_node, err = _resolve_for_read(graph, eq.lhs, up, children, right=right)
    if err is not None:
        return err
    # Strict reading: if lhs is undefined we fail. The classical
    # vacuous-truth reading is also defensible; the choice is logged
    # in docs/analysis-choices.md (see §4.6 follow-up).
    if lhs_node is None:
        return Diagnostic(
            "neg-equation-failed",
            f"neg equation lhs is undefined: {unparse(eq)}",
        )
    lhs_val = graph.value(lhs_node)
    if isinstance(eq.rhs, Atom):
        if not isinstance(lhs_val, AtomValue) or lhs_val.atom != eq.rhs.value:
            return None
        return Diagnostic(
            "neg-equation-failed",
            f"neg equation does not hold: {unparse(eq)}",
            detail={"value": lhs_val.atom},
        )
    rhs_node, err = _resolve_for_read(graph, eq.rhs, up, children, right=right)
    if err is not None:
        return err
    if rhs_node is None:
        return None
    if graph.equiv(lhs_node, rhs_node):
        return Diagnostic(
            "neg-equation-failed",
            f"neg equation does not hold (aliased): {unparse(eq)}",
        )
    rhs_val = graph.value(rhs_node)
    if (
        isinstance(lhs_val, AtomValue)
        and isinstance(rhs_val, AtomValue)
        and lhs_val.atom == rhs_val.atom
    ):
        return Diagnostic(
            "neg-equation-failed",
            f"neg equation does not hold: {unparse(eq)}",
        )
    return None


def _eval_off_path(
    graph: FGraph,
    up: NodeId,
    children: list[NodeId],
    intermediate: NodeId,
    equations: tuple[Equation, ...],
) -> Diagnostic | None:
    """Evaluate off-path constraint equations against ``intermediate``.

    Dispatches each equation to the appropriate read-only evaluator
    with ``right=intermediate`` bound; returns the first failure
    diagnostic, or ``None`` if all equations succeed. Used as the
    ``off_path_eval`` callback by
    :func:`tgllfg.fstruct.fu.resolve_regex_for_read` during FSA
    traversal — failures prune the traversal branch silently.

    Phase 6.B C4: supports the four read-only equation kinds. Write
    equations (``DefiningEquation`` / ``SetMembership``) in an
    off-path context are rejected with an ``unsupported`` diagnostic
    — K&Z 1989 off-path constraints are inherently read-only filters.
    """
    for eq in equations:
        if isinstance(eq, ConstrainingEquation):
            d = _eval_constraining_eq(
                graph, up, children, eq, right=intermediate,
            )
        elif isinstance(eq, ExistentialConstraint):
            d = _eval_existential(
                graph, up, children, eq, right=intermediate,
            )
        elif isinstance(eq, NegExistentialConstraint):
            d = _eval_neg_existential(
                graph, up, children, eq, right=intermediate,
            )
        elif isinstance(eq, NegEquation):
            d = _eval_neg_equation(
                graph, up, children, eq, right=intermediate,
            )
        elif isinstance(eq, (DefiningEquation, SetMembership)):
            return Diagnostic(
                "unsupported",
                f"off-path write equation "
                f"({type(eq).__name__}) is not allowed",
            )
        else:
            return Diagnostic(
                "unsupported",
                f"unsupported off-path equation kind: "
                f"{type(eq).__name__}",
            )
        if d is not None:
            return d
    return None


def _value_summary(v: object) -> str:
    if v is None:
        return "<unset>"
    if isinstance(v, AtomValue):
        return f"atom {v.atom!r}"
    if isinstance(v, ComplexValue):
        return f"complex with attrs {sorted(v.attrs)}"
    if isinstance(v, SetValue):
        return f"set with {len(v.members)} members"
    return repr(v)


# === Projection ============================================================

def _project(graph: FGraph, root: NodeId) -> FStructure:
    """Project the graph rooted at `root` to a tree-shaped FStructure.
    Shared subgraphs become shared FStructure objects (Python identity)
    so reentrancy is preserved for downstream renderers.
    """
    seen: dict[NodeId, ProjectedValue] = {}

    def go(n: NodeId) -> ProjectedValue:
        n = graph.find(n)
        if n in seen:
            return seen[n]
        v = graph.value(n)
        if v is None:
            f = FStructure(feats={}, id=n)
            seen[n] = f
            return f
        if isinstance(v, AtomValue):
            seen[n] = v.atom
            return v.atom
        if isinstance(v, ComplexValue):
            f = FStructure(feats={}, id=n)
            seen[n] = f
            for feat, child in v.attrs.items():
                f.feats[feat] = go(child)
            return f
        # SetValue: project members. Cycles through sets are not
        # excluded by occurs-check, so we cache before recursing.
        placeholder = FStructure(feats={}, id=n)
        seen[n] = placeholder
        members = frozenset(go(m) for m in v.members)
        seen[n] = members
        return members

    n = graph.find(root)
    result = go(n)
    if isinstance(result, FStructure):
        return result
    # Root projects to an atom or set — wrap in a degenerate FStructure
    # so the public API always returns an FStructure.
    return FStructure(feats={"_": result}, id=n)


__all__ = [
    "SolveResult",
    "build_f_structure",
    "solve",
]
