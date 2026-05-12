"""Functional-uncertainty (FU) regex-path evaluation.

Implements the K&Z 1989 §3 / K&M 1988 finite-state algorithm for
evaluating regex paths against an f-graph. Compiles the
:mod:`tgllfg.fstruct.equations` path AST (``Feature`` /
``StarFeature`` / ``PlusFeature`` / ``AltFeature``) into a small NFA,
then traverses the f-graph in lock-step with the NFA, enumerating
the well-formed endpoints reachable by paths matching the regular
expression.

Phase 6.B C2: this module's first commit. Restricted to read-only
constraining / binding contexts; defining-on-regex-LHS is
out-of-scope per ``docs/fu-evaluation.md`` §5.3 and
``.claude/plans/tgllfg-out-of-scope.md`` §18.1.3 — no
``_resolve_regex_for_write`` counterpart will exist in 6.B. Off-path
constraints surface a ``deferred`` diagnostic until 6.B C4 wires
them into the FSA traversal.

The single entry point is :func:`resolve_regex_for_read`, consumed
by :mod:`tgllfg.fstruct.unify`'s constraining-equation evaluator
(wired in 6.B C3). The resolver takes a pre-resolved ``base_node``
NodeId rather than a full ``Designator`` — base resolution
(``Up`` / ``Down`` / ``Right``) stays in ``unify.py`` to avoid a
circular import with the equation orchestrator.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from .equations import (
    AltFeature,
    Feature,
    PathElement,
    PlusFeature,
    StarFeature,
)
from .graph import ComplexValue, Diagnostic, FGraph, NodeId


# === FSA ====================================================================

@dataclass
class _NFA:
    """A small NFA over feature labels for regex-path evaluation.

    States are int ids in ``[0, n_states)``. ``out[s]`` is the list of
    transitions from state ``s``; each entry is ``(label, to)`` where
    ``label is None`` denotes an ε-transition.

    Built by :func:`_compile` from a path AST; consumed by
    :func:`resolve_regex_for_read`. Not exported from the module —
    the compiled NFA is opaque to callers.
    """
    out: list[list[tuple[str | None, int]]] = field(default_factory=list)
    start: int = 0
    accept: int = 0

    @property
    def n_states(self) -> int:
        return len(self.out)


def _compile(path: tuple[PathElement, ...]) -> _NFA:
    """Compile the path AST into an NFA.

    Construction is Thompson-style assembly over the four AST node
    kinds:

    * ``Feature(F)``: single labeled transition ``cur --F--> next``.
    * ``StarFeature(F)``: self-loop on ``cur`` consuming ``F`` +
      ε-transition ``cur --ε--> next`` (zero-iteration case).
      Zero or more F's are both reachable.
    * ``PlusFeature(F)``: ``cur --F--> mid`` (at least one F) +
      self-loop on ``mid`` + ε-transition ``mid --ε--> next``.
    * ``AltFeature((F, G, ...))``: parallel labeled transitions
      ``cur --Fi--> next`` for each name.

    Elements are concatenated by making the exit of element ``i`` the
    entry of element ``i+1``. The empty path compiles to a one-state
    NFA where ``start == accept``.
    """
    out: list[list[tuple[str | None, int]]] = [[]]
    cur = 0

    def new_state() -> int:
        out.append([])
        return len(out) - 1

    for elem in path:
        if isinstance(elem, Feature):
            nxt = new_state()
            out[cur].append((elem.name, nxt))
            cur = nxt
        elif isinstance(elem, StarFeature):
            nxt = new_state()
            # Self-loop consuming F (one or more iterations).
            out[cur].append((elem.name, cur))
            # ε-transition for the zero-iteration case.
            out[cur].append((None, nxt))
            cur = nxt
        elif isinstance(elem, PlusFeature):
            mid = new_state()
            nxt = new_state()
            # cur --F--> mid (at least one F consumed).
            out[cur].append((elem.name, mid))
            # mid --F--> mid (additional iterations).
            out[mid].append((elem.name, mid))
            # mid --ε--> nxt (accept after ≥1 F).
            out[mid].append((None, nxt))
            cur = nxt
        elif isinstance(elem, AltFeature):
            nxt = new_state()
            for name in elem.names:
                out[cur].append((name, nxt))
            cur = nxt
        else:
            raise AssertionError(
                f"unknown path element: {type(elem).__name__}"
            )

    return _NFA(out=out, start=0, accept=cur)


# === Public resolver =======================================================

def resolve_regex_for_read(
    graph: FGraph,
    base_node: NodeId,
    path: tuple[PathElement, ...],
) -> tuple[list[NodeId], Diagnostic | None]:
    """Enumerate the well-formed endpoints reached by a regex path.

    Compiles ``path`` into an NFA and traverses ``graph`` in lock-step
    starting from ``base_node``, returning the **minimality-sorted**
    list of endpoint NodeIds (canonical roots, sorted by reach depth,
    then by NodeId for determinism). Each endpoint appears at most
    once even if reachable by multiple paths.

    The traversal uses a visited-set on ``(node_root, fsa_state)``
    pairs to prevent infinite enumeration on cyclic / reentrant
    graphs; the worklist runs out after at most
    ``|graph_nodes| × |fsa_states|`` iterations.

    Off-path constraints on any path element are not yet supported
    (Phase 6.B C4); if any element carries ``off_path``, returns
    ``([], Diagnostic("deferred", ...))``. Until C4 wires the off-
    path evaluation into the traversal, callers can rely on this
    diagnostic to detect the unsupported case.

    The resolver is read-only — it does not mutate ``graph``. Per the
    Phase 6.B contract, regex paths are only legal in constraining
    and binding contexts; defining-on-regex-LHS has no resolver
    counterpart in this module.
    """
    # Off-path constraints are 6.B C4 work. Surface a deferred
    # diagnostic until then so callers don't silently overgenerate.
    for elem in path:
        if elem.off_path:
            return [], Diagnostic(
                "deferred",
                "off-path constraints deferred to Phase 6.B C4",
            )

    fsa = _compile(path)
    visited: set[tuple[NodeId, int]] = set()
    worklist: deque[tuple[NodeId, int, int]] = deque()
    endpoints: list[tuple[int, NodeId]] = []

    start = graph.find(base_node)
    start_key = (start, fsa.start)
    visited.add(start_key)
    worklist.append((start, fsa.start, 0))

    while worklist:
        node, state, depth = worklist.popleft()
        if state == fsa.accept:
            endpoints.append((depth, node))
        for label, nxt in fsa.out[state]:
            if label is None:
                # ε-transition: same node, advance state, same depth.
                key = (node, nxt)
                if key not in visited:
                    visited.add(key)
                    worklist.append((node, nxt, depth))
            else:
                # Labeled transition: must descend through this
                # feature on the current node. Only ComplexValue
                # nodes have features; atom / set / unset nodes
                # silently skip.
                v = graph.value(node)
                if isinstance(v, ComplexValue) and label in v.attrs:
                    child = graph.find(v.attrs[label])
                    key = (child, nxt)
                    if key not in visited:
                        visited.add(key)
                        worklist.append((child, nxt, depth + 1))

    # Minimality sort: (depth, NodeId) ascending. Dedup by NodeId,
    # keeping the shortest-depth occurrence — K&Z 1989 §3 minimality
    # clause selects the canonical endpoint when multiple paths
    # reach the same node.
    endpoints.sort()
    seen: set[NodeId] = set()
    result: list[NodeId] = []
    for _depth, n in endpoints:
        if n not in seen:
            seen.add(n)
            result.append(n)
    return result, None


__all__ = ["resolve_regex_for_read"]
