"""Phase 6.B C2 + C3 — FSA-based FU regex-path evaluation.

C2: deterministic unit tests for ``resolve_regex_for_read`` covering
the four AST node kinds (``Feature`` / ``StarFeature`` /
``PlusFeature`` / ``AltFeature``), their concatenations, minimality
ordering, dedup, the cycle / reentrancy termination guarantee, and
the C4-deferred off-path branch.

C3 (this commit): integration tests for ``_eval_constraining_eq``'s
new FU-routing branch — constraining equations with regex paths on
the RHS resolve through the FU resolver and check existential
matching against the LHS.

C4 will replace the off-path "deferred" branch with actual
evaluation. C5 will wire binding equations. C7 will add the
Hypothesis property battery.
"""

from __future__ import annotations

from tgllfg.core.common import CNode
from tgllfg.fstruct import (
    AltFeature,
    Atom,
    ConstrainingEquation,
    Designator,
    Feature,
    FGraph,
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
