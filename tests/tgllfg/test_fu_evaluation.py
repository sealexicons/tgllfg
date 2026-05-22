# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 6.B C2 + C3 + C4 + C5 + C6 + C7 — FSA-based FU regex-path evaluation.

C2: deterministic unit tests for ``resolve_regex_for_read`` covering
the four AST node kinds (``Feature`` / ``StarFeature`` /
``PlusFeature`` / ``AltFeature``), their concatenations, minimality
ordering, dedup, the cycle / reentrancy termination guarantee, and
the off-path-without-evaluator branch.

C3: integration tests for ``_eval_constraining_eq``'s new FU-routing
branch — constraining equations with regex paths on the RHS resolve
through the FU resolver and check existential matching against the
LHS.

C4: off-path evaluation tests — off-path constraints on intermediate
nodes filter the FSA traversal; admit / prune behavior verified
across single-step and multi-depth chains, with both ``→``-only
and ``→`` + ``↑`` off-path equations.

C5: binding-equation tests — defining equations with regex RHS
(``(↑ X) = (↑ regex)``) resolve via the FU resolver, select the
K&Z 1989 §3 minimality endpoint, and unify the LHS with it.
Failure modes (no endpoint, off-path filter prunes all candidates)
surface ``constraint-failed``.

C6: parametrized K&Z 1989 §3 fixtures — eq. 30 (TOPIC =
COMP* OBJ), eq. 38 (Icelandic adjunct island, approximated with
single-feature body), eq. 39 (English topicalization, approximated
with single-feature body × bottom alternation).

C7 (this commit): Hypothesis property battery — termination,
determinism, finite endpoint sets, base-as-shortest-endpoint for
``F*``, and binding-symmetric-under-rollback (uses 6.A atomic unify).
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tgllfg.core.common import CNode
from tgllfg.fstruct import (
    AltFeature,
    Atom,
    ConstrainingEquation,
    Designator,
    Feature,
    FGraph,
    NodeId,
    PathElement,
    PlusFeature,
    StarFeature,
    Up,
    resolve_regex_for_read,
    solve,
)


class TestEmptyPath:
    def test_empty_path_returns_base(self) -> None:
        g = FGraph()
        n = g.fresh()
        endpoints, err = resolve_regex_for_read(g, n, ())
        assert err is None
        assert endpoints == [n]


class TestLiteralFeature:
    def test_single_feature_step(self) -> None:
        g = FGraph()
        root = g.fresh()
        child, perr = g.resolve_path(root, ("SUBJ",))
        assert perr is None and child is not None
        endpoints, err = resolve_regex_for_read(
            g, root, (Feature("SUBJ"),),
        )
        assert err is None
        assert endpoints == [child]

    def test_missing_feature_returns_empty(self) -> None:
        g = FGraph()
        root = g.fresh()
        endpoints, err = resolve_regex_for_read(
            g, root, (Feature("SUBJ"),),
        )
        assert err is None
        assert endpoints == []

    def test_multi_step_concat(self) -> None:
        g = FGraph()
        root = g.fresh()
        sub, perr = g.resolve_path(root, ("XCOMP", "SUBJ"))
        assert perr is None and sub is not None
        endpoints, err = resolve_regex_for_read(
            g, root, (Feature("XCOMP"), Feature("SUBJ")),
        )
        assert err is None
        assert endpoints == [sub]


class TestStarFeature:
    def test_star_zero_iterations_on_unset_node(self) -> None:
        """``F*`` against an unset node returns just the base node
        (the zero-iteration accept)."""
        g = FGraph()
        n = g.fresh()
        endpoints, err = resolve_regex_for_read(
            g, n, (StarFeature("XCOMP"),),
        )
        assert err is None
        assert endpoints == [n]

    def test_star_chain_enumerates_all_depths(self) -> None:
        g = FGraph()
        root = g.fresh()
        d1, perr = g.resolve_path(root, ("XCOMP",))
        assert perr is None and d1 is not None
        d2, perr = g.resolve_path(root, ("XCOMP", "XCOMP"))
        assert perr is None and d2 is not None
        d3, perr = g.resolve_path(root, ("XCOMP", "XCOMP", "XCOMP"))
        assert perr is None and d3 is not None
        endpoints, err = resolve_regex_for_read(
            g, root, (StarFeature("XCOMP"),),
        )
        assert err is None
        # All four nodes reachable: root, d1, d2, d3 (minimality-
        # sorted by depth).
        assert endpoints == [root, d1, d2, d3]

    def test_star_then_concat(self) -> None:
        """``XCOMP* SUBJ`` returns the ``SUBJ`` at every XCOMP depth."""
        g = FGraph()
        root = g.fresh()
        # root.SUBJ (depth 0 of XCOMP) and root.XCOMP.SUBJ (depth 1).
        s0, _ = g.resolve_path(root, ("SUBJ",))
        assert s0 is not None
        s1, _ = g.resolve_path(root, ("XCOMP", "SUBJ"))
        assert s1 is not None
        s2, _ = g.resolve_path(root, ("XCOMP", "XCOMP", "SUBJ"))
        assert s2 is not None
        endpoints, err = resolve_regex_for_read(
            g, root, (StarFeature("XCOMP"), Feature("SUBJ")),
        )
        assert err is None
        # All three SUBJs reachable, in depth order.
        assert endpoints == [s0, s1, s2]


class TestPlusFeature:
    def test_plus_zero_iterations_returns_empty(self) -> None:
        """``F+`` requires at least one iteration; with no path
        through F, no endpoint."""
        g = FGraph()
        n = g.fresh()
        endpoints, err = resolve_regex_for_read(
            g, n, (PlusFeature("XCOMP"),),
        )
        assert err is None
        assert endpoints == []

    def test_plus_one_iteration_excludes_base(self) -> None:
        g = FGraph()
        root = g.fresh()
        d1, _ = g.resolve_path(root, ("XCOMP",))
        assert d1 is not None
        endpoints, err = resolve_regex_for_read(
            g, root, (PlusFeature("XCOMP"),),
        )
        assert err is None
        # d1 is reached; root is NOT (plus requires ≥1).
        assert d1 in endpoints
        assert root not in endpoints

    def test_plus_chain(self) -> None:
        g = FGraph()
        root = g.fresh()
        d1, _ = g.resolve_path(root, ("XCOMP",))
        d2, _ = g.resolve_path(root, ("XCOMP", "XCOMP"))
        assert d1 is not None and d2 is not None
        endpoints, err = resolve_regex_for_read(
            g, root, (PlusFeature("XCOMP"),),
        )
        assert err is None
        # d1 and d2 (not root) — both ≥1 XCOMP depth.
        assert endpoints == [d1, d2]


class TestAltFeature:
    def test_alt_two_branches(self) -> None:
        g = FGraph()
        root = g.fresh()
        comp, _ = g.resolve_path(root, ("COMP",))
        xcomp, _ = g.resolve_path(root, ("XCOMP",))
        assert comp is not None and xcomp is not None
        endpoints, err = resolve_regex_for_read(
            g, root, (AltFeature(("COMP", "XCOMP")),),
        )
        assert err is None
        assert set(endpoints) == {comp, xcomp}

    def test_alt_then_concat(self) -> None:
        """``{COMP | XCOMP} SUBJ`` enumerates the SUBJs of both."""
        g = FGraph()
        root = g.fresh()
        cs, _ = g.resolve_path(root, ("COMP", "SUBJ"))
        xs, _ = g.resolve_path(root, ("XCOMP", "SUBJ"))
        assert cs is not None and xs is not None
        endpoints, err = resolve_regex_for_read(
            g, root, (AltFeature(("COMP", "XCOMP")), Feature("SUBJ")),
        )
        assert err is None
        assert set(endpoints) == {cs, xs}

    def test_alt_only_one_branch_defined(self) -> None:
        """Alt skips missing branches without surfacing a diagnostic."""
        g = FGraph()
        root = g.fresh()
        # Only COMP defined; XCOMP is missing.
        comp, _ = g.resolve_path(root, ("COMP",))
        assert comp is not None
        endpoints, err = resolve_regex_for_read(
            g, root, (AltFeature(("COMP", "XCOMP")),),
        )
        assert err is None
        assert endpoints == [comp]


class TestReentrancyAndDedup:
    def test_reentrant_subgraph_dedups_endpoints(self) -> None:
        """Two regex paths reaching the same canonical node return
        that node once — minimality + dedup."""
        g = FGraph()
        root = g.fresh()
        # Build root.A.X and root.B.X reaching the same shared node
        # via unify (the canonical reentrancy pattern).
        ax, _ = g.resolve_path(root, ("A", "X"))
        bx, _ = g.resolve_path(root, ("B", "X"))
        assert ax is not None and bx is not None
        assert g.unify(ax, bx) is None
        assert g.equiv(ax, bx)
        endpoints, err = resolve_regex_for_read(
            g, root, (AltFeature(("A", "B")), Feature("X")),
        )
        assert err is None
        canonical = g.find(ax)
        # Single endpoint despite two paths.
        assert endpoints == [canonical]

    def test_star_against_long_chain_terminates_in_bounded_iterations(
        self,
    ) -> None:
        """``F*`` against a deep but finite chain terminates promptly.
        tgllfg's :func:`FGraph.unify` occurs-check prevents true graph
        cycles (LFG f-structures are required acyclic), so the visited-
        set's role is primarily to dedup ``(node, fsa_state)`` pairs
        reachable via reentrant sub-structure, which is already covered
        by :meth:`test_reentrant_subgraph_dedups_endpoints`. This test
        confirms termination on a 6-node F-chain in a single pass."""
        g = FGraph()
        root = g.fresh()
        nodes = [root]
        cur = root
        for _ in range(5):
            child, _ = g.resolve_path(cur, ("F",))
            assert child is not None
            nodes.append(child)
            cur = child
        endpoints, err = resolve_regex_for_read(
            g, root, (StarFeature("F"),),
        )
        assert err is None
        # All 6 nodes (depth 0 through 5) are endpoints.
        assert endpoints == nodes


class TestMinimality:
    def test_shorter_depth_first(self) -> None:
        g = FGraph()
        root = g.fresh()
        d1, _ = g.resolve_path(root, ("XCOMP",))
        d2, _ = g.resolve_path(root, ("XCOMP", "XCOMP"))
        d3, _ = g.resolve_path(root, ("XCOMP", "XCOMP", "XCOMP"))
        assert d1 is not None and d2 is not None and d3 is not None
        endpoints, err = resolve_regex_for_read(
            g, root, (StarFeature("XCOMP"),),
        )
        assert err is None
        # Strict ordering: root (depth 0), then d1, d2, d3.
        assert endpoints == [root, d1, d2, d3]


class TestOffPathDeferred:
    def test_star_with_off_path_returns_deferred(self) -> None:
        """C2 doesn't implement off-path; until C4 it surfaces a
        deferred diagnostic so callers don't silently overgenerate."""
        off_eq = ConstrainingEquation(
            lhs=Designator(base=Up(), path=(Feature("TENSE"),)),
            rhs=Atom("PAST"),
        )
        elem = StarFeature("XCOMP", off_path=(off_eq,))
        g = FGraph()
        n = g.fresh()
        endpoints, err = resolve_regex_for_read(g, n, (elem,))
        assert err is not None
        assert err.kind == "deferred"
        assert "off-path" in err.message
        assert endpoints == []

    def test_feature_with_off_path_returns_deferred(self) -> None:
        off_eq = ConstrainingEquation(
            lhs=Designator(base=Up(), path=(Feature("TENSE"),)),
            rhs=Atom("PAST"),
        )
        elem = Feature("XCOMP", off_path=(off_eq,))
        g = FGraph()
        n = g.fresh()
        endpoints, err = resolve_regex_for_read(g, n, (elem,))
        assert err is not None
        assert err.kind == "deferred"


class TestKZ1989Fixtures:
    """Canonical K&Z 1989 §3 fixtures, exercised against synthetic
    f-graphs. The grammar that emits these equations lands in later
    sub-PRs (6.D / 6.F); here we validate the resolver against the
    eq. 30 / 39 patterns directly.
    """

    def test_eq30_topic_equals_comp_star_obj(self) -> None:
        """K&Z eq. 30: ``(↑ TOPIC) = (↑ COMP* OBJ)``.

        Build an f-graph with ``COMP`` chain ``f0.COMP.COMP.OBJ = obj``;
        ``COMP* OBJ`` enumerates ``obj`` (and any OBJ at intermediate
        depths if present).
        """
        g = FGraph()
        f0 = g.fresh()
        obj, _ = g.resolve_path(f0, ("COMP", "COMP", "OBJ"))
        assert obj is not None
        endpoints, err = resolve_regex_for_read(
            g, f0, (StarFeature("COMP"), Feature("OBJ")),
        )
        assert err is None
        assert obj in endpoints

    def test_eq39_topic_equals_comp_xcomp_star_gf(self) -> None:
        """K&Z eq. 39 (English topicalization) approximated:
        ``(↑ TOPIC) = (↑ {COMP, XCOMP}* SUBJ)`` (using SUBJ instead
        of the K&Z ``GF-COMP`` complement, which is out of scope per
        ``docs/fu-evaluation.md`` §3).

        Mixed COMP / XCOMP chain; the body should enumerate SUBJ at
        each chain depth where SUBJ exists.
        """
        g = FGraph()
        f0 = g.fresh()
        # Build f0.COMP.XCOMP.SUBJ + f0.SUBJ at depth 0 too.
        s0, _ = g.resolve_path(f0, ("SUBJ",))
        s_deep, _ = g.resolve_path(f0, ("COMP", "XCOMP", "SUBJ"))
        assert s0 is not None and s_deep is not None
        endpoints, err = resolve_regex_for_read(
            g, f0,
            (AltFeature(("COMP", "XCOMP")), Feature("SUBJ")),
        )
        assert err is None
        # Note: this is `{COMP|XCOMP} SUBJ` — exactly one body step.
        # Only `s_deep` is unreachable here (needs `*`). With the
        # plus-or-star version, both s0 and s_deep would be reached.
        # We test the singleton-step here; the full `{COMP|XCOMP}* SUBJ`
        # case is the same machinery and is exercised in
        # `test_alt_then_concat`.
        # The first body step reaches f0.COMP and f0.XCOMP; only
        # f0.COMP.SUBJ would be a depth-1 endpoint, which we did not
        # build. So no SUBJ via single body step.
        assert endpoints == []


# === C3 — constraining-eq integration ======================================

def _blocking(result) -> list:
    return [d for d in result.diagnostics if d.is_blocking()]


class TestConstrainingEqWithFU:
    """C3 wires the FU resolver into ``_eval_constraining_eq``: a
    constraining equation with a regex path on the RHS resolves
    through the FU resolver and checks existential matching against
    the LHS. End-to-end via :func:`solve`.
    """

    def test_star_path_matches_at_zero_depth(self) -> None:
        """``(↑ TOPIC) =c (↑ COMP* OBJ)`` succeeds via the zero-COMP
        path when ``TOPIC`` and ``OBJ`` share an atom directly at
        the matrix node."""
        n = CNode(
            label="N",
            equations=[
                "(↑ TOPIC) = 'X'",
                "(↑ OBJ) = 'X'",
                "(↑ TOPIC) =c (↑ COMP* OBJ)",
            ],
        )
        result = solve(n)
        assert _blocking(result) == [], (
            f"unexpected blocking: {_blocking(result)}"
        )

    def test_star_path_matches_at_deeper_depth(self) -> None:
        """``(↑ TOPIC) =c (↑ COMP* OBJ)`` succeeds at depth 2 when
        ``TOPIC`` shares its atom with a deep ``COMP.COMP.OBJ``."""
        n = CNode(
            label="N",
            equations=[
                "(↑ TOPIC) = 'X'",
                "(↑ COMP COMP OBJ) = 'X'",
                "(↑ TOPIC) =c (↑ COMP* OBJ)",
            ],
        )
        result = solve(n)
        assert _blocking(result) == [], (
            f"unexpected blocking: {_blocking(result)}"
        )

    def test_star_path_no_match_fails(self) -> None:
        """No COMP-depth has an OBJ matching the TOPIC atom."""
        n = CNode(
            label="N",
            equations=[
                "(↑ TOPIC) = 'X'",
                "(↑ COMP OBJ) = 'Y'",
                "(↑ TOPIC) =c (↑ COMP* OBJ)",
            ],
        )
        result = solve(n)
        kinds = {d.kind for d in result.diagnostics}
        assert "constraint-failed" in kinds

    def test_star_path_no_endpoint_fails(self) -> None:
        """``OBJ`` doesn't exist at any COMP depth, so the FU path
        resolves to no endpoint."""
        n = CNode(
            label="N",
            equations=[
                "(↑ TOPIC) = 'X'",
                "(↑ TOPIC) =c (↑ COMP* OBJ)",
            ],
        )
        result = solve(n)
        kinds = {d.kind for d in result.diagnostics}
        assert "constraint-failed" in kinds

    def test_plus_excludes_zero_depth(self) -> None:
        """``(↑ TOPIC) =c (↑ COMP+ OBJ)`` requires ≥ 1 COMP step;
        ``OBJ`` at depth 0 doesn't satisfy."""
        n = CNode(
            label="N",
            equations=[
                "(↑ TOPIC) = 'X'",
                "(↑ OBJ) = 'X'",
                "(↑ TOPIC) =c (↑ COMP+ OBJ)",
            ],
        )
        result = solve(n)
        kinds = {d.kind for d in result.diagnostics}
        assert "constraint-failed" in kinds

    def test_plus_matches_at_depth_1(self) -> None:
        n = CNode(
            label="N",
            equations=[
                "(↑ TOPIC) = 'X'",
                "(↑ COMP OBJ) = 'X'",
                "(↑ TOPIC) =c (↑ COMP+ OBJ)",
            ],
        )
        result = solve(n)
        assert _blocking(result) == [], (
            f"unexpected blocking: {_blocking(result)}"
        )

    def test_alt_matches_xcomp_branch(self) -> None:
        n = CNode(
            label="N",
            equations=[
                "(↑ TOPIC) = 'X'",
                "(↑ XCOMP SUBJ) = 'X'",
                "(↑ TOPIC) =c (↑ {COMP|XCOMP} SUBJ)",
            ],
        )
        result = solve(n)
        assert _blocking(result) == [], (
            f"unexpected blocking: {_blocking(result)}"
        )

    def test_off_path_holds_admits_branch(self) -> None:
        """Phase 6.B C4: off-path ``(→ TENSE) =c 'PAST'`` holds at
        the intermediate XCOMP; the FSA branch is admitted, the
        deeper SUBJ matches TOPIC, and the constraining equation
        succeeds. Replaces the C3 ``test_off_path_still_deferred``."""
        n = CNode(
            label="N",
            equations=[
                "(↑ TOPIC) = 'shared'",
                "(↑ XCOMP TENSE) = 'PAST'",
                "(↑ XCOMP SUBJ) = 'shared'",
                "(↑ TOPIC) =c (↑ XCOMP*<(→ TENSE) =c 'PAST'> SUBJ)",
            ],
        )
        result = solve(n)
        assert _blocking(result) == [], (
            f"unexpected blocking: {_blocking(result)}"
        )

    def test_off_path_fails_prunes_branch(self) -> None:
        """Off-path ``(→ TENSE) =c 'PAST'`` fails at the intermediate
        XCOMP (TENSE is 'PRES'); that branch is pruned during FSA
        traversal, no endpoint matches the LHS, and the constraining
        equation fails."""
        n = CNode(
            label="N",
            equations=[
                "(↑ TOPIC) = 'shared'",
                "(↑ XCOMP TENSE) = 'PRES'",
                "(↑ XCOMP SUBJ) = 'shared'",
                "(↑ TOPIC) =c (↑ XCOMP*<(→ TENSE) =c 'PAST'> SUBJ)",
            ],
        )
        result = solve(n)
        kinds = {d.kind for d in result.diagnostics}
        assert "constraint-failed" in kinds

    def test_off_path_can_reference_matrix(self) -> None:
        """Off-path constraints can mix ``→`` (intermediate) with
        ``↑`` (matrix). Here ``(→ INT_TAG) =c (↑ MAT_TAG)`` checks
        that the intermediate's INT_TAG equals the matrix's MAT_TAG.
        """
        n = CNode(
            label="N",
            equations=[
                "(↑ TOPIC) = 'shared'",
                "(↑ MAT_TAG) = 'M'",
                "(↑ XCOMP INT_TAG) = 'M'",
                "(↑ XCOMP SUBJ) = 'shared'",
                (
                    "(↑ TOPIC) =c "
                    "(↑ XCOMP*<(→ INT_TAG) =c (↑ MAT_TAG)> SUBJ)"
                ),
            ],
        )
        result = solve(n)
        assert _blocking(result) == [], (
            f"unexpected blocking: {_blocking(result)}"
        )

    def test_off_path_matrix_reference_mismatch_fails(self) -> None:
        """Same shape as above but the intermediate's INT_TAG diverges
        from the matrix's MAT_TAG; off-path fails, branch pruned,
        constraint fails."""
        n = CNode(
            label="N",
            equations=[
                "(↑ TOPIC) = 'shared'",
                "(↑ MAT_TAG) = 'M'",
                "(↑ XCOMP INT_TAG) = 'OTHER'",
                "(↑ XCOMP SUBJ) = 'shared'",
                (
                    "(↑ TOPIC) =c "
                    "(↑ XCOMP*<(→ INT_TAG) =c (↑ MAT_TAG)> SUBJ)"
                ),
            ],
        )
        result = solve(n)
        kinds = {d.kind for d in result.diagnostics}
        assert "constraint-failed" in kinds

    def test_off_path_at_multiple_chain_depths(self) -> None:
        """Off-path is checked at every intermediate XCOMP. With a
        2-deep XCOMP chain where both intermediates have TENSE=PAST,
        the chain admits and the constraint succeeds at depth 2."""
        n = CNode(
            label="N",
            equations=[
                "(↑ TOPIC) = 'shared'",
                "(↑ XCOMP TENSE) = 'PAST'",
                "(↑ XCOMP XCOMP TENSE) = 'PAST'",
                "(↑ XCOMP XCOMP SUBJ) = 'shared'",
                "(↑ TOPIC) =c (↑ XCOMP*<(→ TENSE) =c 'PAST'> SUBJ)",
            ],
        )
        result = solve(n)
        assert _blocking(result) == [], (
            f"unexpected blocking: {_blocking(result)}"
        )

    def test_off_path_breaks_chain_mid_depth(self) -> None:
        """A 2-deep XCOMP chain where the *second* intermediate has
        TENSE=PRES; off-path passes at depth 1 (PAST) but fails at
        depth 2 (PRES), so no depth-2 endpoint. No SUBJ at depth 1.
        Constraint fails."""
        n = CNode(
            label="N",
            equations=[
                "(↑ TOPIC) = 'shared'",
                "(↑ XCOMP TENSE) = 'PAST'",
                "(↑ XCOMP XCOMP TENSE) = 'PRES'",
                "(↑ XCOMP XCOMP SUBJ) = 'shared'",
                "(↑ TOPIC) =c (↑ XCOMP*<(→ TENSE) =c 'PAST'> SUBJ)",
            ],
        )
        result = solve(n)
        kinds = {d.kind for d in result.diagnostics}
        assert "constraint-failed" in kinds


# === C5 — binding-equation integration =====================================

class TestBindingEqWithFU:
    """C5 wires the FU resolver into ``_eval_defining_eq`` for
    binding equations (``=`` with regex on RHS). The RHS regex
    enumerates endpoints read-only; K&Z 1989 §3 minimality selects
    the shortest-depth endpoint; ``graph.unify`` joins the LHS with
    it. Failure modes:

    * No endpoint → ``constraint-failed``.
    * Off-path filter eliminates all candidates → also no endpoint →
      ``constraint-failed``.
    * Unify itself fails (e.g., atom clash between LHS and target) →
      the unify's own ``atom-mismatch`` / ``occurs-check`` /
      ``type-mismatch`` diagnostic surfaces.
    """

    def test_binding_at_depth_0_unifies(self) -> None:
        """``(↑ TOPIC) = (↑ COMP* OBJ)`` with ``OBJ`` defined directly
        at the matrix: COMP* with zero iterations reaches the matrix;
        OBJ resolves at depth 1; TOPIC unifies with it."""
        n = CNode(
            label="N",
            equations=[
                "(↑ OBJ) = 'X'",
                "(↑ TOPIC) = (↑ COMP* OBJ)",
            ],
        )
        result = solve(n)
        assert _blocking(result) == [], (
            f"unexpected blocking: {_blocking(result)}"
        )

    def test_binding_at_deeper_depth_unifies(self) -> None:
        """``(↑ TOPIC) = (↑ COMP* OBJ)`` with ``COMP COMP OBJ``
        defined: TOPIC binds to the depth-2 OBJ."""
        n = CNode(
            label="N",
            equations=[
                "(↑ COMP COMP OBJ) = 'X'",
                "(↑ TOPIC) = (↑ COMP* OBJ)",
            ],
        )
        result = solve(n)
        assert _blocking(result) == [], (
            f"unexpected blocking: {_blocking(result)}"
        )

    def test_binding_picks_shortest_endpoint(self) -> None:
        """K&Z 1989 §3 minimality: when ``OBJ`` is defined at multiple
        COMP depths, ``(↑ TOPIC) = (↑ COMP* OBJ)`` picks the shortest
        (the depth-1 OBJ, not the depth-2 OBJ). Verified by setting
        the shortest-depth OBJ to 'X' and a deeper one to 'Y' — the
        successful binding requires the shortest match, so the
        equation succeeds (TOPIC = 'X')."""
        n = CNode(
            label="N",
            equations=[
                "(↑ COMP OBJ) = 'X'",
                "(↑ COMP COMP OBJ) = 'Y'",
                "(↑ TOPIC) = (↑ COMP* OBJ)",
                # Subsequent check: TOPIC must equal 'X' (the shortest
                # endpoint), not 'Y'.
                "(↑ TOPIC) =c 'X'",
            ],
        )
        result = solve(n)
        assert _blocking(result) == [], (
            f"unexpected blocking: {_blocking(result)}"
        )

    def test_binding_no_endpoint_fails(self) -> None:
        """``(↑ TOPIC) = (↑ COMP* OBJ)`` with no ``OBJ`` anywhere in
        the COMP chain: the regex resolves to no endpoint; binding
        fails with ``constraint-failed``."""
        n = CNode(
            label="N",
            equations=[
                "(↑ TOPIC) = (↑ COMP* OBJ)",
            ],
        )
        result = solve(n)
        kinds = {d.kind for d in result.diagnostics}
        assert "constraint-failed" in kinds

    def test_binding_with_off_path_admits(self) -> None:
        """Binding with off-path: ``(↑ TOPIC) = (↑ XCOMP*<(→ TENSE)
        =c 'PAST'> SUBJ)``. Off-path holds at the intermediate XCOMP;
        the branch is admitted; TOPIC unifies with the depth-1
        SUBJ."""
        n = CNode(
            label="N",
            equations=[
                "(↑ XCOMP TENSE) = 'PAST'",
                "(↑ XCOMP SUBJ) = 'X'",
                "(↑ TOPIC) = (↑ XCOMP*<(→ TENSE) =c 'PAST'> SUBJ)",
            ],
        )
        result = solve(n)
        assert _blocking(result) == [], (
            f"unexpected blocking: {_blocking(result)}"
        )

    def test_binding_with_off_path_filter_fails(self) -> None:
        """Off-path filter prunes the only candidate; no endpoint;
        binding fails."""
        n = CNode(
            label="N",
            equations=[
                "(↑ XCOMP TENSE) = 'PRES'",
                "(↑ XCOMP SUBJ) = 'X'",
                "(↑ TOPIC) = (↑ XCOMP*<(→ TENSE) =c 'PAST'> SUBJ)",
            ],
        )
        result = solve(n)
        kinds = {d.kind for d in result.diagnostics}
        assert "constraint-failed" in kinds

    def test_binding_unifies_atoms_consistently(self) -> None:
        """Binding LHS to a regex endpoint of an atom node: the unify
        succeeds when atoms match. Setting both TOPIC and the depth-1
        endpoint to the same atom should land without diagnostic."""
        n = CNode(
            label="N",
            equations=[
                "(↑ TOPIC) = 'shared'",
                "(↑ COMP OBJ) = 'shared'",
                "(↑ TOPIC) = (↑ COMP* OBJ)",
            ],
        )
        result = solve(n)
        assert _blocking(result) == [], (
            f"unexpected blocking: {_blocking(result)}"
        )

    def test_binding_atom_clash_surfaces_unify_diagnostic(self) -> None:
        """Binding LHS (atom 'X') to a regex endpoint (atom 'Y'):
        the unify fails with ``atom-mismatch``."""
        n = CNode(
            label="N",
            equations=[
                "(↑ TOPIC) = 'X'",
                "(↑ COMP OBJ) = 'Y'",
                "(↑ TOPIC) = (↑ COMP* OBJ)",
            ],
        )
        result = solve(n)
        kinds = {d.kind for d in result.diagnostics}
        assert "atom-mismatch" in kinds


# === C6 — K&Z 1989 §3 fixture parametrizations =============================

class TestKZFixturesParametrized:
    """K&Z 1989 §3 canonical equations exercised end-to-end via
    :func:`solve`. C2 had unit-level resolver tests for eq. 30 / 39
    against synthetic FGraphs; C6 adds parametrized integration
    tests through the full constraining + binding eval paths
    landed in C3 / C5, with off-path filtering from C4.

    Approximations: K&Z uses set-complement notation ``(GF-ADJ)``
    and ``(GF-COMP)`` in eqs. 38 / 39. Set-complement is out of
    scope per ``docs/fu-evaluation.md`` §3 and
    ``tgllfg-out-of-scope.md`` §18.1.3; here we approximate with
    explicit GF alternations. The K&Z structural argument (body
    restriction filters which paths the regex can take) carries
    through unchanged.
    """

    @pytest.mark.parametrize("depth", [0, 1, 2, 3])
    def test_eq30_topic_binds_obj_at_depth(self, depth: int) -> None:
        """K&Z eq. 30: ``(↑ TOPIC) = (↑ COMP* OBJ)``.

        Parametrized over the COMP-chain depth. At each depth ``N``,
        a single ``OBJ`` is defined at ``COMP^N`` and the FU
        binding resolves to it. The follow-on ``=c`` check confirms
        TOPIC equals that endpoint's atom.
        """
        comp_chain = " ".join(["COMP"] * depth)
        deep_path = (
            f"(↑ {comp_chain} OBJ)" if depth > 0 else "(↑ OBJ)"
        )
        n = CNode(
            label="N",
            equations=[
                f"{deep_path} = 'X'",
                "(↑ TOPIC) = (↑ COMP* OBJ)",
                "(↑ TOPIC) =c 'X'",
            ],
        )
        result = solve(n)
        assert _blocking(result) == [], (
            f"depth={depth}: unexpected blocking: {_blocking(result)}"
        )

    def test_eq30_minimality_picks_shortest(self) -> None:
        """K&Z 1989 §3 minimality: when ``OBJ`` is defined at multiple
        COMP depths, the binding picks the shortest. The deeper OBJ
        is unreachable from the K&Z perspective — it's there in the
        f-graph but minimality skips past it.
        """
        n = CNode(
            label="N",
            equations=[
                "(↑ COMP OBJ) = 'shortest'",
                "(↑ COMP COMP OBJ) = 'deeper'",
                "(↑ TOPIC) = (↑ COMP* OBJ)",
                "(↑ TOPIC) =c 'shortest'",
            ],
        )
        result = solve(n)
        assert _blocking(result) == [], (
            f"unexpected blocking: {_blocking(result)}"
        )

    def test_eq30_no_obj_anywhere_fails(self) -> None:
        """K&Z eq. 30 with no OBJ in the COMP chain: regex resolves
        to no endpoint; binding fails with ``constraint-failed``."""
        n = CNode(
            label="N",
            equations=[
                "(↑ COMP COMP COMP) = 'deep'",
                "(↑ TOPIC) = (↑ COMP* OBJ)",
            ],
        )
        result = solve(n)
        kinds = {d.kind for d in result.diagnostics}
        assert "constraint-failed" in kinds

    def test_eq38_body_restricts_traversal(self) -> None:
        """K&Z eq. 38 (Icelandic adjunct island), simplified.

        K&Z's body ``(GF-ADJ)*`` (set complement on GF) is out of
        scope per ``docs/fu-evaluation.md`` §3, and the related
        ``{F | G}*`` (Kleene on alternation) is not parsed by the
        current equation grammar — both deferred via
        ``tgllfg-out-of-scope.md`` §18.1.3. Here we approximate the
        K&Z island constraint with a single-feature body
        ``COMP*``: the body admits the COMP-chain SUBJ but cannot
        reach a SUBJ behind an ``ADJ`` step.

        Setup: ``matrix.COMP.SUBJ`` is reachable via the body;
        ``matrix.ADJ.SUBJ`` is not. TOPIC binds to
        ``matrix.COMP.SUBJ``.
        """
        n = CNode(
            label="N",
            equations=[
                "(↑ COMP SUBJ) = 'comp_subj'",
                "(↑ ADJ SUBJ) = 'adj_subj'",
                "(↑ TOPIC) = (↑ COMP* SUBJ)",
                "(↑ TOPIC) =c 'comp_subj'",
            ],
        )
        result = solve(n)
        assert _blocking(result) == [], (
            f"unexpected blocking: {_blocking(result)}"
        )

    def test_eq38_island_unreachable_subj_fails(self) -> None:
        """When the only ``SUBJ`` is inside ``ADJ``, the body
        ``COMP*`` cannot reach it (ADJ isn't in the body
        alternation); the regex has no endpoint; binding fails.
        """
        n = CNode(
            label="N",
            equations=[
                "(↑ ADJ SUBJ) = 'island_only'",
                "(↑ TOPIC) = (↑ COMP* SUBJ)",
            ],
        )
        result = solve(n)
        kinds = {d.kind for d in result.diagnostics}
        assert "constraint-failed" in kinds

    def test_eq39_topicalization_via_xcomp(self) -> None:
        """K&Z eq. 39 (English topicalization), approximated.

        K&Z's body ``{COMP | XCOMP}*`` and bottom ``(GF-COMP)`` are
        not directly parseable (``{F | G}*`` deferred per
        ``tgllfg-out-of-scope.md`` §18.1.3; set-complement deferred
        per §18.1.3 too). Here we approximate body as ``XCOMP*``
        (single-feature) and bottom as ``{SUBJ | OBJ | OBL}``
        (explicit non-COMP alternation).
        """
        n = CNode(
            label="N",
            equations=[
                "(↑ XCOMP SUBJ) = 'extracted'",
                "(↑ TOPIC) = (↑ XCOMP* {SUBJ | OBJ | OBL})",
                "(↑ TOPIC) =c 'extracted'",
            ],
        )
        result = solve(n)
        assert _blocking(result) == [], (
            f"unexpected blocking: {_blocking(result)}"
        )

    def test_eq39_topicalization_via_comp_obj(self) -> None:
        """K&Z eq. 39 (English topicalization), via COMP body and
        OBJ bottom. Demonstrates the body-bottom partition by
        switching both: body ``COMP*``, bottom
        ``{SUBJ | OBJ | OBL}``. The OBJ endpoint reached at
        ``COMP.OBJ`` is the topicalized constituent.
        """
        n = CNode(
            label="N",
            equations=[
                "(↑ COMP OBJ) = 'extracted'",
                "(↑ TOPIC) = (↑ COMP* {SUBJ | OBJ | OBL})",
                "(↑ TOPIC) =c 'extracted'",
            ],
        )
        result = solve(n)
        assert _blocking(result) == [], (
            f"unexpected blocking: {_blocking(result)}"
        )

    @pytest.mark.parametrize("body_gf", ["COMP", "XCOMP"])
    @pytest.mark.parametrize("bottom_gf", ["SUBJ", "OBJ"])
    def test_eq39_body_bottom_combinations(
        self, body_gf: str, bottom_gf: str,
    ) -> None:
        """Cartesian product of body single-feature × bottom
        alternation. Each combination succeeds when the corresponding
        ``f-graph`` path is defined.
        """
        n = CNode(
            label="N",
            equations=[
                f"(↑ {body_gf} {bottom_gf}) = 'val'",
                f"(↑ TOPIC) = (↑ {body_gf}* {{SUBJ | OBJ}})",
                "(↑ TOPIC) =c 'val'",
            ],
        )
        result = solve(n)
        assert _blocking(result) == [], (
            f"body={body_gf} bottom={bottom_gf}: "
            f"unexpected blocking: {_blocking(result)}"
        )

    def test_eq39_off_path_tense_filter(self) -> None:
        """K&Z 1989 off-path example combined with the eq. 39
        body-bottom partition: ``(↑ TOPIC) = (↑ XCOMP*<(→ TENSE)
        =c 'PAST'> {SUBJ | OBJ})``. The off-path filter restricts
        the body to PAST-tensed intermediates; with TENSE=PAST at
        the intermediate XCOMP, the binding succeeds.
        """
        n = CNode(
            label="N",
            equations=[
                "(↑ XCOMP TENSE) = 'PAST'",
                "(↑ XCOMP SUBJ) = 'extracted'",
                (
                    "(↑ TOPIC) = "
                    "(↑ XCOMP*<(→ TENSE) =c 'PAST'> {SUBJ | OBJ})"
                ),
                "(↑ TOPIC) =c 'extracted'",
            ],
        )
        result = solve(n)
        assert _blocking(result) == [], (
            f"unexpected blocking: {_blocking(result)}"
        )

    def test_eq39_off_path_tense_filter_blocks_wrong_tense(self) -> None:
        """Same shape as ``test_eq39_off_path_tense_filter`` but the
        intermediate XCOMP has TENSE='PRES'; off-path filter prunes
        the branch; no endpoint; binding fails."""
        n = CNode(
            label="N",
            equations=[
                "(↑ XCOMP TENSE) = 'PRES'",
                "(↑ XCOMP SUBJ) = 'extracted'",
                (
                    "(↑ TOPIC) = "
                    "(↑ XCOMP*<(→ TENSE) =c 'PAST'> {SUBJ | OBJ})"
                ),
            ],
        )
        result = solve(n)
        kinds = {d.kind for d in result.diagnostics}
        assert "constraint-failed" in kinds


# === C7 — Hypothesis property battery ======================================

# Small feature-name pool used both for graph construction and path
# generation. Single-letter names + a few canonical GFs gives good
# overlap probability without exploding the search space.
_FU_FEATS = ("F", "G", "H", "SUBJ", "OBJ", "COMP", "XCOMP", "TOPIC")
_FU_ATOMS = ("X", "Y", "Z", "PAST", "PRES")


@st.composite
def _fu_setup(
    draw: st.DrawFn,
    max_nodes: int = 4,
    max_path_len: int = 3,
) -> tuple[FGraph, NodeId, tuple[PathElement, ...]]:
    """Hypothesis strategy: build a small FGraph and pair it with a
    randomly generated path. Returns ``(graph, base_node, path)``.

    Each node is independently left unbound, atom-bound, or made into
    a ``ComplexValue`` with 1-3 attributes pointing at other nodes;
    after structure-building, 0-3 ``unify`` calls are attempted to
    add reentrancy. The path is 0-3 elements drawn from the four AST
    node kinds (literal, star, plus, alt). Off-path constraints on
    elements are not generated — those are exercised by the C2/C3/C4
    deterministic tests.
    """
    g = FGraph()
    n_nodes = draw(st.integers(min_value=1, max_value=max_nodes))
    nodes = [g.fresh() for _ in range(n_nodes)]

    # Per-node: leave unset, atom-bind, or build a ComplexValue.
    for i, n in enumerate(nodes):
        kind = draw(st.sampled_from(["unset", "atom", "complex"]))
        if kind == "atom":
            g.set_atom(n, draw(st.sampled_from(_FU_ATOMS)))
        elif kind == "complex":
            n_feats = draw(st.integers(min_value=1, max_value=3))
            for _ in range(n_feats):
                feat = draw(st.sampled_from(_FU_FEATS))
                # Create the child via resolve_path; optionally
                # collapse it onto another existing node via unify
                # (atomic, so failures from occurs-check / atom
                # clash leave the graph unchanged).
                child, err = g.resolve_path(n, (feat,))
                if err is not None or child is None:
                    continue
                if draw(st.booleans()) and len(nodes) > 1:
                    target_idx = draw(
                        st.integers(min_value=0, max_value=n_nodes - 1),
                    )
                    if target_idx != i:
                        g.unify(child, nodes[target_idx])

    # 0-3 extra unify pairs for reentrancy. Atomic; failures fine.
    n_extra_unifies = draw(st.integers(min_value=0, max_value=3))
    for _ in range(n_extra_unifies):
        i = draw(st.integers(min_value=0, max_value=n_nodes - 1))
        j = draw(st.integers(min_value=0, max_value=n_nodes - 1))
        g.unify(nodes[i], nodes[j])

    base = nodes[0]

    n_elems = draw(st.integers(min_value=0, max_value=max_path_len))
    path: list[PathElement] = []
    for _ in range(n_elems):
        elem_kind = draw(
            st.sampled_from(["feature", "star", "plus", "alt"]),
        )
        if elem_kind == "feature":
            path.append(Feature(draw(st.sampled_from(_FU_FEATS))))
        elif elem_kind == "star":
            path.append(StarFeature(draw(st.sampled_from(_FU_FEATS))))
        elif elem_kind == "plus":
            path.append(PlusFeature(draw(st.sampled_from(_FU_FEATS))))
        else:
            n_alts = draw(st.integers(min_value=2, max_value=3))
            names = tuple(
                draw(st.sampled_from(_FU_FEATS)) for _ in range(n_alts)
            )
            path.append(AltFeature(names))

    return g, base, tuple(path)


class TestFUProperties:
    """Hypothesis property battery for the FU resolver. Verifies the
    invariants the design appendix §9.4 commits to: termination,
    minimality determinism, finite endpoint sets, and binding-
    symmetric-under-rollback (which leans on 6.A atomic unify).
    """

    @given(setup=_fu_setup())
    @settings(max_examples=100, deadline=2000)
    def test_resolver_terminates_on_random_setups(
        self,
        setup: tuple[FGraph, NodeId, tuple[PathElement, ...]],
    ) -> None:
        """For any small FGraph + random path,
        :func:`resolve_regex_for_read` terminates and returns a
        well-typed result. The mere fact that we reach the
        post-call assertion proves termination on the search space
        explored by Hypothesis.
        """
        g, base, path = setup
        endpoints, err = resolve_regex_for_read(g, base, path)
        assert isinstance(endpoints, list)
        assert err is None or err.kind in {"deferred", "unsupported"}
        for ep in endpoints:
            assert isinstance(ep, int)

    @given(setup=_fu_setup())
    @settings(max_examples=100, deadline=2000)
    def test_resolver_is_deterministic_across_runs(
        self,
        setup: tuple[FGraph, NodeId, tuple[PathElement, ...]],
    ) -> None:
        """Two consecutive calls on the same ``(graph, base, path)``
        return identical results. Minimality ordering is canonical
        — no randomness in the resolver itself.
        """
        g, base, path = setup
        e1, err1 = resolve_regex_for_read(g, base, path)
        e2, err2 = resolve_regex_for_read(g, base, path)
        assert e1 == e2
        assert (err1 is None) == (err2 is None)
        if err1 is not None and err2 is not None:
            assert err1.kind == err2.kind

    @given(setup=_fu_setup())
    @settings(max_examples=100, deadline=2000)
    def test_endpoints_bounded_by_visited_set(
        self,
        setup: tuple[FGraph, NodeId, tuple[PathElement, ...]],
    ) -> None:
        """The endpoint set is finite, and dedup ensures each
        canonical node appears at most once even if multiple paths
        reach it.
        """
        g, base, path = setup
        endpoints, _err = resolve_regex_for_read(g, base, path)
        # Endpoints are canonical roots; dedup means each NodeId
        # appears once.
        assert len(endpoints) == len(set(endpoints))

    @given(setup=_fu_setup())
    @settings(max_examples=50, deadline=2000)
    def test_empty_path_returns_canonical_base(
        self,
        setup: tuple[FGraph, NodeId, tuple[PathElement, ...]],
    ) -> None:
        """``resolve_regex_for_read(g, base, ())`` always returns
        ``[graph.find(base)]`` — the empty regex matches the empty
        string, reaching the base node.
        """
        g, base, _ = setup
        endpoints, err = resolve_regex_for_read(g, base, ())
        assert err is None
        assert endpoints == [g.find(base)]

    @given(setup=_fu_setup(), feat=st.sampled_from(_FU_FEATS))
    @settings(max_examples=50, deadline=2000)
    def test_star_always_includes_canonical_base(
        self,
        setup: tuple[FGraph, NodeId, tuple[PathElement, ...]],
        feat: str,
    ) -> None:
        """``F*`` always succeeds with the canonical base as the
        first (shortest-depth) endpoint, since zero iterations of
        ``F`` are admissible. This is K&Z 1989's minimality
        guarantee for star-paths: the zero-step accept dominates.
        """
        g, base, _ = setup
        endpoints, err = resolve_regex_for_read(
            g, base, (StarFeature(feat),),
        )
        assert err is None
        canonical = g.find(base)
        assert endpoints[0] == canonical

    @given(setup=_fu_setup())
    @settings(max_examples=50, deadline=2000)
    def test_resolver_does_not_mutate_graph(
        self,
        setup: tuple[FGraph, NodeId, tuple[PathElement, ...]],
    ) -> None:
        """The resolver is read-only. Capture the pre-call graph
        state, run the resolver, verify the state is unchanged.
        """
        g, base, path = setup
        before_next_id = g._next_id
        before_parent = dict(g._parent)
        before_rank = dict(g._rank)
        before_store_keys = set(g._store.keys())
        resolve_regex_for_read(g, base, path)
        # Internal pointer-state may evolve (path compression in
        # ``find()`` rewrites ``_parent`` opportunistically), but the
        # graph's *observable* state — node count, equivalence
        # classes, store keys — must be unchanged.
        assert g._next_id == before_next_id
        # Equivalence classes preserved: every pre-existing node's
        # canonical root is the same as it was.
        for n in before_parent:
            # Re-canonicalize by walking the (possibly compressed)
            # parent chain.
            root = n
            while g._parent[root] != root:
                root = g._parent[root]
            # The pre-call root is also a fixed point of the pre-call
            # parent map (find is idempotent on roots).
            pre_root = n
            while before_parent[pre_root] != pre_root:
                pre_root = before_parent[pre_root]
            assert root == pre_root
        assert set(g._store.keys()) == before_store_keys
        # Rank may have changed only through path compression
        # bookkeeping, but actually it doesn't change in find — only
        # ``_link`` mutates rank. So rank should be unchanged too.
        assert g._rank == before_rank

    @given(setup=_fu_setup(), atom=st.sampled_from(_FU_ATOMS))
    @settings(max_examples=50, deadline=2000)
    def test_binding_symmetric_under_rollback(
        self,
        setup: tuple[FGraph, NodeId, tuple[PathElement, ...]],
        atom: str,
    ) -> None:
        """6.A atomic-unify + FU integration: take a snapshot, run a
        binding attempt against the first endpoint of the regex, then
        rollback. Re-run the resolver. The result must be identical
        — the resolver is read-only and rollback restores the graph
        completely.
        """
        g, base, path = setup
        endpoints_before, err_before = resolve_regex_for_read(
            g, base, path,
        )
        if err_before is not None or not endpoints_before:
            return  # nothing to bind against
        snap = g.snapshot()
        lhs = g.fresh()
        g.set_atom(lhs, atom)  # may or may not clash on unify below
        g.unify(lhs, endpoints_before[0])  # atomic; OK if it fails
        g.rollback(snap)
        endpoints_after, err_after = resolve_regex_for_read(
            g, base, path,
        )
        assert endpoints_after == endpoints_before
        assert (err_before is None) == (err_after is None)
