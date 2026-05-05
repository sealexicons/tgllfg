# tgllfg/unify.py

"""F-structure construction by two-pass equation solving.

This module orchestrates equation evaluation over a c-tree. It walks
the tree assigning a fresh f-graph node to each c-node, then runs
two passes over the parsed equations:

1. **Defining pass.** Apply ``DefiningEquation`` and ``SetMembership``
   against the f-graph, growing structure and unifying nodes. The
   unifier in :mod:`tgllfg.fgraph` enforces uniqueness, type
   compatibility, and the occurs check on this pass.
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
  well-formedness module in §4.4 will surface diagnostics through
  this entry point.

Functional uncertainty (regular-path designators) and off-path
constraints parse correctly but evaluate to a ``deferred`` diagnostic
in §4.2; full evaluation lands with the chart parser in §4.3 / Phase 4.
"""

from __future__ import annotations

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
from .graph import (
    AtomValue,
    ComplexValue,
    Diagnostic,
    FGraph,
    NodeId,
    SetValue,
)


type ProjectedValue = str | FStructure | frozenset


@dataclass
class SolveResult:
    """Full output of the two-pass solver."""
    fstructure: FStructure
    graph: FGraph
    root: NodeId
    diagnostics: list[Diagnostic] = field(default_factory=list)


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
    _pass_defining(root, graph, nid_for, parsed_for, diagnostics)
    _pass_constraining(root, graph, nid_for, parsed_for, diagnostics)

    fstr = _project(graph, nid_for[id(root)])
    return SolveResult(
        fstructure=fstr,
        graph=graph,
        root=nid_for[id(root)],
        diagnostics=diagnostics,
    )


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
            diagnostics.append(replace(d, equation=eq_str, cnode_label=c.label))
    for ch in c.children:
        _pass_defining(ch, graph, nid_for, parsed_for, diagnostics)


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
) -> tuple[NodeId | None, Diagnostic | None]:
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
) -> tuple[NodeId | None, Diagnostic | None]:
    """Resolve the designator with get-or-create semantics. Used for
    the lhs of defining equations and both sides of set membership."""
    base_node, err = _resolve_base(designator.base, up, children)
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
) -> tuple[NodeId | None, Diagnostic | None]:
    """Resolve the designator without creating intermediate nodes.
    Returns (None, None) when the path is not defined; that is not an
    error in itself, just absence."""
    base_node, err = _resolve_base(designator.base, up, children)
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
) -> Diagnostic | None:
    lhs_node, err = _resolve_for_write(graph, eq.lhs, up, children)
    if err is not None:
        return err
    assert lhs_node is not None

    if isinstance(eq.rhs, Atom):
        return graph.set_atom(lhs_node, eq.rhs.value)

    rhs_node, err = _resolve_for_write(graph, eq.rhs, up, children)
    if err is not None:
        return err
    assert rhs_node is not None
    return graph.unify(lhs_node, rhs_node)


def _eval_set_member(
    graph: FGraph,
    up: NodeId,
    children: list[NodeId],
    eq: SetMembership,
) -> Diagnostic | None:
    elem_node, err = _resolve_for_write(graph, eq.element, up, children)
    if err is not None:
        return err
    container_node, err = _resolve_for_write(graph, eq.container, up, children)
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
) -> Diagnostic | None:
    lhs_node, err = _resolve_for_read(graph, eq.lhs, up, children)
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

    rhs_node, err = _resolve_for_read(graph, eq.rhs, up, children)
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
) -> Diagnostic | None:
    node, err = _resolve_for_read(graph, eq.designator, up, children)
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
) -> Diagnostic | None:
    node, err = _resolve_for_read(graph, eq.designator, up, children)
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
) -> Diagnostic | None:
    lhs_node, err = _resolve_for_read(graph, eq.lhs, up, children)
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
    rhs_node, err = _resolve_for_read(graph, eq.rhs, up, children)
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
    so reentrancy is preserved for downstream renderers."""
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
