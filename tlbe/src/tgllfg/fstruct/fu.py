# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Functional-uncertainty (FU) regex-path evaluation.

Implements the K&Z 1989 §3 / K&M 1988 finite-state algorithm for
evaluating regex paths against an f-graph. Compiles the
:mod:`tgllfg.fstruct.equations` path AST (``Feature`` /
``StarFeature`` / ``PlusFeature`` / ``AltFeature``) into a small NFA,
then traverses the f-graph in lock-step with the NFA, enumerating
the well-formed endpoints reachable by paths matching the regular
expression.

Phase 6.B C4: this commit adds off-path constraint evaluation. The
caller supplies an ``off_path_eval`` callback that the FSA traversal
invokes at every step consuming a labeled transition whose source
element carried off-path constraints; the callback evaluates the
constraints against the intermediate node and returns ``None`` to
admit the branch or a :class:`Diagnostic` to prune it. The orchestration
in :mod:`tgllfg.fstruct.unify` constructs the callback as a closure
over the surrounding ``(up, children)`` context so off-path designators
referring to ``↑`` / ``↓`` / ``→`` all bind correctly.

Restricted to read-only constraining / binding contexts;
defining-on-regex-LHS is out-of-scope per ``docs/fu-evaluation.md``
§5.3 and ``.claude/plans/tgllfg-out-of-scope.md`` §18.1.3 — no
``_resolve_regex_for_write`` counterpart will exist in 6.B.

The single entry point is :func:`resolve_regex_for_read`, consumed
by :mod:`tgllfg.fstruct.unify`'s constraining-equation evaluator
(wired in 6.B C3, off-path eval added in C4). The resolver takes a
pre-resolved ``base_node`` NodeId rather than a full ``Designator``
— base resolution (``Up`` / ``Down`` / ``Right``) stays in
``unify.py`` to avoid a circular import with the equation
orchestrator.
"""

from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field

from .equations import (
    AltFeature,
    Equation,
    Feature,
    PathElement,
    PlusAltFeature,
    PlusFeature,
    StarAltFeature,
    StarFeature,
)
from .graph import ComplexValue, Diagnostic, FGraph, NodeId


# Callback for evaluating off-path constraints on an intermediate
# node during FSA traversal. Receives the canonical-root NodeId
# of the just-stepped-to node and the tuple of off-path equations
# attached to the consuming path element; returns ``None`` to admit
# the branch, or a :class:`Diagnostic` to prune it (the resolver
# swallows the diagnostic — pruning is silent at the FU level).
OffPathEval = Callable[[NodeId, tuple[Equation, ...]], "Diagnostic | None"]


# === FSA ====================================================================

@dataclass
class _NFA:
    """A small NFA over feature labels for regex-path evaluation.

    States are int ids in ``[0, n_states)``. ``out[s]`` is the list of
    transitions from state ``s``; each entry is
    ``(label, to, off_path)`` where ``label is None`` denotes an
    ε-transition and ``off_path`` is the tuple of off-path equations
    attached to the originating path element (empty tuple for
    transitions that don't come from off-path-bearing elements,
    including all ε-transitions).

    Built by :func:`_compile` from a path AST; consumed by
    :func:`resolve_regex_for_read`. Not exported from the module —
    the compiled NFA is opaque to callers.
    """
    out: list[list[tuple[str | None, int, tuple[Equation, ...]]]] = field(
        default_factory=list,
    )
    start: int = 0
    accept: int = 0

    @property
    def n_states(self) -> int:
        return len(self.out)


def _compile(path: tuple[PathElement, ...]) -> _NFA:
    """Compile the path AST into an NFA.

    Construction is compositional in the style of Thompson 1968
    (state-count-optimized — each element introduces a small fixed
    sub-graph rather than the canonical four-states-per-element
    Thompson shape). The six AST node kinds compile as:

    * ``Feature(F)``: single labeled transition ``cur --F--> next``.
    * ``StarFeature(F)``: self-loop on ``cur`` consuming ``F`` +
      ε-transition ``cur --ε--> next`` (zero-iteration case).
      Zero or more F's are both reachable.
    * ``PlusFeature(F)``: ``cur --F--> mid`` (at least one F) +
      self-loop on ``mid`` + ε-transition ``mid --ε--> next``.
    * ``AltFeature((F, G, ...))``: parallel labeled transitions
      ``cur --Fi--> next`` for each name.
    * ``StarAltFeature((F, G, ...))`` (Phase 10.L): parallel
      self-loops on ``cur`` consuming each name + ε-transition
      ``cur --ε--> next``. Zero or more iterations of any name
      in the alternation are reachable.
    * ``PlusAltFeature((F, G, ...))`` (Phase 10.L): parallel
      ``cur --Fi--> mid`` transitions (at least one consumed) +
      parallel self-loops on ``mid`` + ε-transition
      ``mid --ε--> next``.

    Each labeled transition carries the originating element's
    ``off_path`` constraints (an empty tuple if the element has
    none). ε-transitions never carry off-path constraints — they
    don't consume a feature.

    Elements are concatenated by making the exit of element ``i`` the
    entry of element ``i+1``. The empty path compiles to a one-state
    NFA where ``start == accept``.
    """
    out: list[list[tuple[str | None, int, tuple[Equation, ...]]]] = [[]]
    cur = 0

    def new_state() -> int:
        out.append([])
        return len(out) - 1

    for elem in path:
        if isinstance(elem, Feature):
            nxt = new_state()
            out[cur].append((elem.name, nxt, elem.off_path))
            cur = nxt
        elif isinstance(elem, StarFeature):
            nxt = new_state()
            # Self-loop consuming F (one or more iterations).
            out[cur].append((elem.name, cur, elem.off_path))
            # ε-transition for the zero-iteration case (no off-path).
            out[cur].append((None, nxt, ()))
            cur = nxt
        elif isinstance(elem, PlusFeature):
            mid = new_state()
            nxt = new_state()
            # cur --F--> mid (at least one F consumed).
            out[cur].append((elem.name, mid, elem.off_path))
            # mid --F--> mid (additional iterations).
            out[mid].append((elem.name, mid, elem.off_path))
            # mid --ε--> nxt (accept after ≥1 F; no off-path).
            out[mid].append((None, nxt, ()))
            cur = nxt
        elif isinstance(elem, AltFeature):
            nxt = new_state()
            for name in elem.names:
                out[cur].append((name, nxt, elem.off_path))
            cur = nxt
        elif isinstance(elem, StarAltFeature):
            nxt = new_state()
            # Parallel self-loops: any name consumes one step.
            for name in elem.names:
                out[cur].append((name, cur, elem.off_path))
            # ε-transition for the zero-iteration case (no off-path).
            out[cur].append((None, nxt, ()))
            cur = nxt
        elif isinstance(elem, PlusAltFeature):
            mid = new_state()
            nxt = new_state()
            # cur --Fi--> mid for each name (≥1 consumed).
            for name in elem.names:
                out[cur].append((name, mid, elem.off_path))
            # mid --Fi--> mid for each name (additional iterations).
            for name in elem.names:
                out[mid].append((name, mid, elem.off_path))
            # mid --ε--> nxt (accept after ≥1; no off-path).
            out[mid].append((None, nxt, ()))
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
    *,
    off_path_eval: OffPathEval | None = None,
    exclude_cyclic_with: NodeId | None = None,
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

    Off-path constraints: if the path contains any off-path-bearing
    element, ``off_path_eval`` must be supplied. When the callback is
    supplied, every labeled transition consumed by such an element
    invokes it against the post-step intermediate node; on
    :class:`Diagnostic` return, that traversal branch is pruned
    silently. If off-path constraints are present but ``off_path_eval``
    is ``None``, the resolver returns ``([], Diagnostic("deferred",
    ...))`` — the legacy C2/C3 behavior preserved for direct callers
    that don't go through ``unify.py``.

    Cyclic-endpoint pruning (Phase 11.B.5): when ``exclude_cyclic_with``
    is supplied, endpoints whose canonical root equals
    ``graph.find(exclude_cyclic_with)`` are filtered out post-dedup.
    The use case is a defining equation ``(↑ X) = (↑ {SUBJ | OBJ})``
    where one of the alternation arms would resolve back to the LHS
    itself (e.g., reflexive's binder enumeration includes the
    reflexive's own position), triggering cyclic unification at the
    occurs-check downstream. Caller passes the LHS-canonical root;
    the resolver skips the cyclic endpoint and surfaces the
    non-cyclic complement at the head of the minimality-sorted list.
    The ``graph.find()`` canonicalization on both sides naturally
    covers the "or already in the unification chain of the LHS" case
    — any node previously unified with the LHS shares its root.
    Default behavior (``exclude_cyclic_with=None``) is unchanged;
    the prior reflexive-binding equation-side workaround at
    ``cfg/control.py:1097-1186`` (now removed by Phase 11.B.2's
    NP-layer pivot) and the post-11.B.2 Dalrymple-canonical NP-layer
    binding both bypass the resolver-side pruning entirely. The
    feature is shipped as a U-bucket prototype — no chart consumer
    in ``unify.py`` opts in yet; consumers will surface as
    constructions with alternation-form binding emerge.

    The resolver is read-only — it does not mutate ``graph``. Per the
    Phase 6.B contract, regex paths are only legal in constraining
    and binding contexts; defining-on-regex-LHS has no resolver
    counterpart in this module.
    """
    if off_path_eval is None:
        # Preserve the C2 contract for callers that don't supply an
        # evaluator: any off-path constraint short-circuits to
        # ``deferred`` so they don't silently overgenerate.
        for elem in path:
            if elem.off_path:
                return [], Diagnostic(
                    "deferred",
                    "off-path constraints require an evaluator "
                    "callback; provide ``off_path_eval`` to enable.",
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
        for label, nxt, off_path in fsa.out[state]:
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
                    # Off-path: evaluate against the intermediate
                    # (post-step) node; failure prunes silently.
                    if off_path and off_path_eval is not None:
                        if off_path_eval(child, off_path) is not None:
                            continue
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

    # Phase 11.B.5 cyclic-endpoint pruning: when an LHS-root is
    # supplied, filter out any endpoint that would unify cyclically
    # with the LHS. Done post-dedup so minimality ordering of the
    # surviving endpoints is preserved.
    if exclude_cyclic_with is not None:
        excl_root = graph.find(exclude_cyclic_with)
        result = [n for n in result if n != excl_root]

    return result, None


__all__ = ["OffPathEval", "resolve_regex_for_read"]
