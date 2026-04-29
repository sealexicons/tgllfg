from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tgllfg.common import CNode, FStructure
from tgllfg.fstruct import (
    AtomValue,
    ComplexValue,
    Diagnostic,
    FGraph,
    NodeId,
    SetValue,
    build_f_structure,
    solve,
)


# Hypothesis strategies for atoms and feature names: short uppercase
# identifiers, no risk of clashing with the parser's syntactic tokens.
atoms = st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=5)
features = st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=5)


def _walk(graph: FGraph, base: NodeId, path: tuple[str, ...]) -> NodeId:
    """Resolve a path with assertions; suitable when the test setup
    knows resolution can't fail (which is most of them)."""
    node, err = graph.resolve_path(base, path)
    assert err is None
    assert node is not None
    return node


# === Atom unification ======================================================

class TestAtomUnification:
    @given(a=atoms, b=atoms)
    def test_unify_succeeds_iff_equal(self, a: str, b: str) -> None:
        g = FGraph()
        n1, n2 = g.fresh(), g.fresh()
        assert g.set_atom(n1, a) is None
        assert g.set_atom(n2, b) is None
        err = g.unify(n1, n2)
        if a == b:
            assert err is None
            assert g.equiv(n1, n2)
            v = g.value(n1)
            assert isinstance(v, AtomValue) and v.atom == a
        else:
            assert isinstance(err, Diagnostic)
            assert err.kind == "atom-mismatch"
            assert not g.equiv(n1, n2)

    @given(a=atoms, b=atoms)
    def test_symmetric(self, a: str, b: str) -> None:
        g1, g2 = FGraph(), FGraph()
        n1a, n1b = g1.fresh(), g1.fresh()
        n2a, n2b = g2.fresh(), g2.fresh()
        g1.set_atom(n1a, a)
        g1.set_atom(n1b, b)
        g2.set_atom(n2a, a)
        g2.set_atom(n2b, b)
        err1 = g1.unify(n1a, n1b)
        err2 = g2.unify(n2b, n2a)
        assert (err1 is None) == (err2 is None)
        if err1 is None:
            v1 = g1.value(n1a)
            v2 = g2.value(n2a)
            assert isinstance(v1, AtomValue) and isinstance(v2, AtomValue)
            assert v1.atom == v2.atom

    @given(a=atoms)
    def test_idempotent(self, a: str) -> None:
        g = FGraph()
        n = g.fresh()
        g.set_atom(n, a)
        err = g.unify(n, n)
        assert err is None
        v = g.value(n)
        assert isinstance(v, AtomValue) and v.atom == a

    def test_set_atom_idempotent_same_value(self) -> None:
        g = FGraph()
        n = g.fresh()
        assert g.set_atom(n, "X") is None
        assert g.set_atom(n, "X") is None  # idempotent
        v = g.value(n)
        assert isinstance(v, AtomValue) and v.atom == "X"

    def test_set_atom_rebind_different_value_fails(self) -> None:
        g = FGraph()
        n = g.fresh()
        g.set_atom(n, "X")
        d = g.set_atom(n, "Y")
        assert isinstance(d, Diagnostic)
        assert d.kind == "atom-mismatch"


# === Complex unification ===================================================

class TestComplexUnification:
    def test_disjoint_attrs_merge(self) -> None:
        g = FGraph()
        a, b = g.fresh(), g.fresh()
        a_f = _walk(g, a, ("F",))
        b_g = _walk(g, b, ("G",))
        g.set_atom(a_f, "1")
        g.set_atom(b_g, "2")
        err = g.unify(a, b)
        assert err is None
        v = g.value(a)
        assert isinstance(v, ComplexValue)
        assert set(v.attrs) == {"F", "G"}

    def test_overlapping_attrs_unify_recursively(self) -> None:
        g = FGraph()
        a, b = g.fresh(), g.fresh()
        a_f = _walk(g, a, ("F",))
        b_f = _walk(g, b, ("F",))
        g.set_atom(a_f, "X")
        g.set_atom(b_f, "X")
        err = g.unify(a, b)
        assert err is None
        # F nodes from both sides are now in the same class
        assert g.equiv(a_f, b_f)

    def test_overlapping_attrs_clash_propagates(self) -> None:
        g = FGraph()
        a, b = g.fresh(), g.fresh()
        a_f = _walk(g, a, ("F",))
        b_f = _walk(g, b, ("F",))
        g.set_atom(a_f, "X")
        g.set_atom(b_f, "Y")
        err = g.unify(a, b)
        assert isinstance(err, Diagnostic)
        assert err.kind == "atom-mismatch"
        # Path records the failing feature
        assert err.path == ("F",)

    def test_resolve_path_get_or_create(self) -> None:
        g = FGraph()
        a = g.fresh()
        f1 = _walk(g, a, ("F",))
        f2 = _walk(g, a, ("F",))
        # Same call returns the same node
        assert g.find(f1) == g.find(f2)


# === Set unification =======================================================

class TestSetUnification:
    def test_set_union(self) -> None:
        g = FGraph()
        a, b, m1, m2 = g.fresh(), g.fresh(), g.fresh(), g.fresh()
        g.add_to_set(a, m1)
        g.add_to_set(b, m2)
        err = g.unify(a, b)
        assert err is None
        v = g.value(a)
        assert isinstance(v, SetValue)
        assert {g.find(m) for m in v.members} == {g.find(m1), g.find(m2)}

    def test_set_atom_clash(self) -> None:
        g = FGraph()
        a, b, m = g.fresh(), g.fresh(), g.fresh()
        g.add_to_set(a, m)
        g.set_atom(b, "X")
        err = g.unify(a, b)
        assert isinstance(err, Diagnostic)
        assert err.kind == "type-mismatch"

    def test_add_to_set_clash_with_atom(self) -> None:
        g = FGraph()
        a, m = g.fresh(), g.fresh()
        g.set_atom(a, "X")
        d = g.add_to_set(a, m)
        assert isinstance(d, Diagnostic)
        assert d.kind == "set-membership-clash"


# === Type mismatch (atom vs complex, etc.) =================================

class TestTypeMismatch:
    @given(atom=atoms, feat=features)
    def test_atom_vs_complex_fails(self, atom: str, feat: str) -> None:
        g = FGraph()
        a, b = g.fresh(), g.fresh()
        g.set_atom(a, atom)
        g.resolve_path(b, (feat,))
        err = g.unify(a, b)
        assert isinstance(err, Diagnostic)
        assert err.kind == "type-mismatch"

    @given(atom=atoms)
    def test_atom_vs_set_fails(self, atom: str) -> None:
        g = FGraph()
        a, b, m = g.fresh(), g.fresh(), g.fresh()
        g.set_atom(a, atom)
        g.add_to_set(b, m)
        err = g.unify(a, b)
        assert isinstance(err, Diagnostic)
        assert err.kind == "type-mismatch"

    @given(feat=features)
    def test_complex_vs_set_fails(self, feat: str) -> None:
        g = FGraph()
        a, b, m = g.fresh(), g.fresh(), g.fresh()
        g.resolve_path(a, (feat,))
        g.add_to_set(b, m)
        err = g.unify(a, b)
        assert isinstance(err, Diagnostic)
        assert err.kind == "type-mismatch"


# === Occurs check ==========================================================

class TestOccursCheck:
    def test_simple_self_cycle_rejected(self) -> None:
        g = FGraph()
        a = g.fresh()
        # a.F is a fresh unset child node.
        f = _walk(g, a, ("F",))
        # Unify the F-child with a itself: would create a -> F -> a cycle.
        err = g.unify(f, a)
        assert isinstance(err, Diagnostic)
        assert err.kind == "occurs-check"

    def test_indirect_cycle_rejected(self) -> None:
        g = FGraph()
        a = g.fresh()
        f = _walk(g, a, ("F",))
        g_node = _walk(g, f, ("G",))
        # a.F.G would refer back to a → cycle.
        err = g.unify(g_node, a)
        assert isinstance(err, Diagnostic)
        assert err.kind == "occurs-check"

    def test_no_cycle_when_independent(self) -> None:
        g = FGraph()
        a, b = g.fresh(), g.fresh()
        f_a = _walk(g, a, ("F",))
        f_b = _walk(g, b, ("F",))
        # Unifying two unrelated branches should not trigger occurs-check.
        err = g.unify(f_a, f_b)
        assert err is None


# === Reentrancy preservation ==============================================

class TestReentrancy:
    def test_alias_transitively_preserved(self) -> None:
        g = FGraph()
        a, b, c = g.fresh(), g.fresh(), g.fresh()
        assert g.unify(a, b) is None
        assert g.equiv(a, b)
        assert g.unify(b, c) is None
        assert g.equiv(a, b) and g.equiv(b, c) and g.equiv(a, c)

    def test_value_propagates_through_alias(self) -> None:
        g = FGraph()
        a, b = g.fresh(), g.fresh()
        g.unify(a, b)
        # Setting an atom on either should be visible through both.
        g.set_atom(a, "Z")
        v = g.value(b)
        assert isinstance(v, AtomValue) and v.atom == "Z"

    def test_reentrancy_in_projection(self) -> None:
        # Two distinct features bound to the same child must project
        # to the same FStructure object (Python identity).
        child = CNode(label="C", equations=["(↑ A) = 'V'"])
        root = CNode(
            label="R",
            children=[child],
            equations=["(↑ X) = ↓1", "(↑ Y) = ↓1"],
        )
        f = build_f_structure(root)
        assert "X" in f.feats and "Y" in f.feats
        x = f.feats["X"]
        y = f.feats["Y"]
        assert x is y
        assert isinstance(x, FStructure)
        assert x.feats["A"] == "V"


# === Orchestration: c-tree with equations =================================

class TestOrchestration:
    def test_atom_assignment(self) -> None:
        n = CNode(label="N", equations=["(↑ CASE) = 'NOM'"])
        f = build_f_structure(n)
        assert f.feats["CASE"] == "NOM"

    def test_atom_clash_emits_diagnostic(self) -> None:
        n = CNode(label="N", equations=[
            "(↑ CASE) = 'NOM'",
            "(↑ CASE) = 'GEN'",
        ])
        result = solve(n)
        assert any(d.kind == "atom-mismatch" for d in result.diagnostics)

    def test_head_sharing(self) -> None:
        # (↑) = ↓1 binds the parent's f-structure to the first child's.
        v = CNode(label="V", equations=["(↑ PRED) = 'EAT'"])
        s = CNode(label="S", children=[v], equations=["(↑) = ↓1"])
        f = build_f_structure(s)
        assert f.feats["PRED"] == "EAT"

    def test_existing_demo_still_passes(self) -> None:
        # The percolation test in test_pv_features_percolate.py runs the
        # full pipeline; this is a redundant guard at the unification
        # layer to make a §4.2 regression visible immediately.
        from tgllfg.pipeline import parse_text
        results = parse_text("Kinain ng aso ang isda.")
        assert len(results) >= 1
        _, f, _, _ = results[0]
        assert f.feats["VOICE"] == "OV"
        assert f.feats["ASPECT"] == "PFV"
        assert f.feats["PRED"].startswith("EAT")
        assert "SUBJ" in f.feats and "OBJ" in f.feats


# === Set equations on c-trees =============================================

class TestSetEquations:
    def test_one_member(self) -> None:
        child = CNode(label="X", equations=["(↑ TAG) = 'a'"])
        root = CNode(
            label="R",
            children=[child],
            equations=["↓1 ∈ (↑ ADJ)"],
        )
        f = build_f_structure(root)
        adj = f.feats["ADJ"]
        assert isinstance(adj, frozenset)
        assert len(adj) == 1

    def test_two_members(self) -> None:
        c1 = CNode(label="X", equations=["(↑ TAG) = 'a'"])
        c2 = CNode(label="Y", equations=["(↑ TAG) = 'b'"])
        root = CNode(
            label="R",
            children=[c1, c2],
            equations=["↓1 ∈ (↑ ADJ)", "↓2 ∈ (↑ ADJ)"],
        )
        f = build_f_structure(root)
        adj = f.feats["ADJ"]
        assert isinstance(adj, frozenset)
        assert len(adj) == 2

    def test_set_then_assign_atom_clashes(self) -> None:
        child = CNode(label="X", equations=[])
        root = CNode(
            label="R",
            children=[child],
            equations=["↓1 ∈ (↑ ADJ)", "(↑ ADJ) = 'X'"],
        )
        result = solve(root)
        assert any(
            d.kind in ("type-mismatch", "set-membership-clash")
            for d in result.diagnostics
        )


# === Two-pass: constraining, existential, neg ============================

class TestConstraining:
    def test_constraining_holds(self) -> None:
        n = CNode(label="N", equations=[
            "(↑ CASE) = 'NOM'",
            "(↑ CASE) =c 'NOM'",
        ])
        result = solve(n)
        assert not result.diagnostics

    def test_constraining_fails_on_value_mismatch(self) -> None:
        n = CNode(label="N", equations=[
            "(↑ CASE) = 'NOM'",
            "(↑ CASE) =c 'GEN'",
        ])
        result = solve(n)
        assert any(d.kind == "constraint-failed" for d in result.diagnostics)

    def test_constraining_fails_on_undefined(self) -> None:
        n = CNode(label="N", equations=["(↑ CASE) =c 'NOM'"])
        result = solve(n)
        assert any(d.kind == "constraint-failed" for d in result.diagnostics)


class TestExistential:
    def test_existential_holds(self) -> None:
        n = CNode(label="N", equations=["(↑ CASE) = 'NOM'", "(↑ CASE)"])
        result = solve(n)
        assert not result.diagnostics

    def test_existential_fails(self) -> None:
        n = CNode(label="N", equations=["(↑ CASE)"])
        result = solve(n)
        assert any(d.kind == "existential-failed" for d in result.diagnostics)


class TestNegExistential:
    def test_neg_existential_holds_when_undefined(self) -> None:
        n = CNode(label="N", equations=["¬ (↑ CASE)"])
        result = solve(n)
        assert not result.diagnostics

    def test_neg_existential_fails_when_defined(self) -> None:
        n = CNode(label="N", equations=[
            "(↑ CASE) = 'NOM'",
            "¬ (↑ CASE)",
        ])
        result = solve(n)
        assert any(
            d.kind == "neg-existential-failed" for d in result.diagnostics
        )


class TestNegEquation:
    def test_neg_equation_holds(self) -> None:
        n = CNode(label="N", equations=[
            "(↑ CASE) = 'NOM'",
            "(↑ CASE) ≠ 'GEN'",
        ])
        result = solve(n)
        assert not result.diagnostics

    def test_neg_equation_fails(self) -> None:
        n = CNode(label="N", equations=[
            "(↑ CASE) = 'NOM'",
            "(↑ CASE) ≠ 'NOM'",
        ])
        result = solve(n)
        assert any(d.kind == "neg-equation-failed" for d in result.diagnostics)

    def test_neg_equation_strict_on_undefined(self) -> None:
        # Documented choice: undefined lhs fails (rather than vacuously
        # succeeding). See docs/analysis-choices.md follow-up.
        n = CNode(label="N", equations=["(↑ CASE) ≠ 'NOM'"])
        result = solve(n)
        assert any(d.kind == "neg-equation-failed" for d in result.diagnostics)


# === Diagnostic shape =====================================================

class TestDiagnostics:
    def test_equation_and_label_populated(self) -> None:
        n = CNode(label="MyNode", equations=[
            "(↑ CASE) = 'NOM'",
            "(↑ CASE) =c 'GEN'",
        ])
        result = solve(n)
        failed = [d for d in result.diagnostics if d.kind == "constraint-failed"]
        assert len(failed) == 1
        assert failed[0].equation == "(↑ CASE) =c 'GEN'"
        assert failed[0].cnode_label == "MyNode"

    def test_path_propagates_from_unifier(self) -> None:
        # Path tracking lives in the recursive unify primitive: build
        # two complex sub-structures separately, then unify their
        # roots; the leaf clash should record the feature path that
        # led to it.
        g = FGraph()
        a, b = g.fresh(), g.fresh()
        a_xy = _walk(g, a, ("X", "Y"))
        b_xy = _walk(g, b, ("X", "Y"))
        g.set_atom(a_xy, "A")
        g.set_atom(b_xy, "B")
        err = g.unify(a, b)
        assert isinstance(err, Diagnostic)
        assert err.kind == "atom-mismatch"
        assert err.path == ("X", "Y")

    def test_parse_error_diagnostic(self) -> None:
        n = CNode(label="N", equations=["(↑ F) @ 'X'"])
        result = solve(n)
        assert any(d.kind == "parse-error" for d in result.diagnostics)
        parse_errs = [d for d in result.diagnostics if d.kind == "parse-error"]
        assert parse_errs[0].equation == "(↑ F) @ 'X'"
        assert parse_errs[0].cnode_label == "N"


# === Functional uncertainty / off-path are deferred =======================

class TestDeferred:
    def test_star_path_emits_deferred(self) -> None:
        n = CNode(label="N", equations=["(↑ TOPIC) = (↑ COMP* GF)"])
        result = solve(n)
        assert any(d.kind == "deferred" for d in result.diagnostics)

    def test_off_path_emits_deferred(self) -> None:
        n = CNode(label="N", equations=[
            "(↑ COMP<(→ FIN) =c '+'>)",
        ])
        result = solve(n)
        assert any(d.kind == "deferred" for d in result.diagnostics)


# === Property: atom + unset symmetry ======================================

class TestAtomUnsetProperty:
    @given(atom=atoms)
    def test_unset_absorbs_atom_either_order(self, atom: str) -> None:
        # unify(unset, atom) should succeed and bind the unset to atom,
        # regardless of argument order.
        for order in (0, 1):
            g = FGraph()
            n_unset, n_atom = g.fresh(), g.fresh()
            g.set_atom(n_atom, atom)
            err = (
                g.unify(n_unset, n_atom) if order == 0
                else g.unify(n_atom, n_unset)
            )
            assert err is None
            v = g.value(n_unset)
            assert isinstance(v, AtomValue) and v.atom == atom


# === Property: unify(a, a) is a no-op =====================================

class TestSelfUnifyProperty:
    @given(atom=atoms, feat=features)
    @settings(max_examples=50)
    def test_self_unify_atom_node(self, atom: str, feat: str) -> None:
        g = FGraph()
        n = g.fresh()
        g.set_atom(n, atom)
        err = g.unify(n, n)
        assert err is None
        v = g.value(n)
        assert isinstance(v, AtomValue) and v.atom == atom

    @given(feats_list=st.lists(features, min_size=1, max_size=4, unique=True))
    @settings(max_examples=50)
    def test_self_unify_complex_node(self, feats_list: list[str]) -> None:
        g = FGraph()
        n = g.fresh()
        for f in feats_list:
            g.resolve_path(n, (f,))
        err = g.unify(n, n)
        assert err is None
        v = g.value(n)
        assert isinstance(v, ComplexValue)
        assert set(v.attrs) == set(feats_list)


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
