from __future__ import annotations

from tgllfg.common import LexicalEntry, MorphAnalysis
from tgllfg.parse import (
    PackedForest,
    parse_with_annotations,
)
from tgllfg.cfg import Grammar, Rule


# === Helpers ===============================================================

def _tok(
    pos: str,
    lemma: str = "x",
    le: LexicalEntry | None = None,
    **feats: str,
) -> list[tuple[MorphAnalysis, LexicalEntry | None]]:
    """Build a single-analysis token with the given POS and features."""
    return [(MorphAnalysis(lemma=lemma, pos=pos, feats=dict(feats)), le)]


def _grammar(*rules: Rule) -> Grammar:
    return Grammar(list(rules))


def _labels(node) -> list[str]:
    """Flatten a c-tree to its labels, depth-first."""
    out = [node.label]
    for ch in node.children:
        out.extend(_labels(ch))
    return out


# === Trivial grammars =====================================================

class TestSingleRule:
    def test_one_token(self) -> None:
        g = _grammar(Rule("S", ["V"], []))
        forest = parse_with_annotations([_tok("V")], g)
        trees = forest.trees
        assert len(trees) == 1
        s = trees[0]
        assert s.label == "S"
        assert len(s.children) == 1
        assert s.children[0].label == "V"


class TestMultiTokenChain:
    def test_two_tokens_two_levels(self) -> None:
        g = _grammar(
            Rule("S", ["A", "B"], []),
            Rule("A", ["X"], []),
            Rule("B", ["Y"], []),
        )
        forest = parse_with_annotations([_tok("X"), _tok("Y")], g)
        trees = forest.trees
        assert len(trees) == 1
        assert _labels(trees[0]) == ["S", "A", "X", "B", "Y"]


class TestAmbiguous:
    def test_two_derivations(self) -> None:
        # Two different routes to S over the same input.
        g = _grammar(
            Rule("S", ["A"], []),
            Rule("S", ["B"], []),
            Rule("A", ["X"], []),
            Rule("B", ["X"], []),
        )
        forest = parse_with_annotations([_tok("X")], g)
        trees = forest.trees
        assert len(trees) == 2
        roots = sorted(_labels(t)[1] for t in trees)
        assert roots == ["A", "B"]


class TestEmptyProduction:
    def test_epsilon_rule(self) -> None:
        # Grammar: S → A, A → ε. Input is empty; one parse expected.
        g = _grammar(
            Rule("S", ["A"], []),
            Rule("A", [], []),
        )
        forest = parse_with_annotations([], g)
        trees = forest.trees
        assert len(trees) == 1
        assert _labels(trees[0]) == ["S", "A"]
        # The ε-derived A has no children.
        assert trees[0].children[0].children == []


class TestNoParse:
    def test_category_mismatch(self) -> None:
        g = _grammar(Rule("S", ["V"], []))
        forest = parse_with_annotations([_tok("N")], g)
        assert forest.trees == []

    def test_extra_tokens(self) -> None:
        g = _grammar(Rule("S", ["V"], []))
        forest = parse_with_annotations([_tok("V"), _tok("V")], g)
        assert forest.trees == []

    def test_missing_tokens(self) -> None:
        g = _grammar(
            Rule("S", ["A", "B"], []),
            Rule("A", ["X"], []),
            Rule("B", ["Y"], []),
        )
        forest = parse_with_annotations([_tok("X")], g)
        assert forest.trees == []


# === Feature handling =====================================================

class TestFeatureMatching:
    def test_feature_constraint_satisfied(self) -> None:
        g = _grammar(Rule("S", ["V[VOICE=PV]"], []))
        forest = parse_with_annotations([_tok("V", VOICE="PV", ASPECT="PFV")], g)
        assert len(forest.trees) == 1

    def test_feature_constraint_violated(self) -> None:
        g = _grammar(Rule("S", ["V[VOICE=PV]"], []))
        forest = parse_with_annotations([_tok("V", VOICE="AV")], g)
        assert forest.trees == []

    def test_pos_alias_verb_to_v(self) -> None:
        # Morph emits pos='VERB'; the grammar speaks 'V'. Verify the
        # alias.
        g = _grammar(Rule("S", ["V"], []))
        forest = parse_with_annotations([_tok("VERB")], g)
        assert len(forest.trees) == 1


# === Equation propagation onto c-tree ====================================

class TestEquationPropagation:
    def test_rule_equations_attached_to_internal_node(self) -> None:
        g = _grammar(Rule("S", ["V"], ["(↑) = ↓1"]))
        forest = parse_with_annotations([_tok("V")], g)
        s = forest.trees[0]
        assert "(↑) = ↓1" in s.equations

    def test_lex_equations_from_morph_features(self) -> None:
        g = _grammar(Rule("S", ["V"], []))
        forest = parse_with_annotations(
            [_tok("V", VOICE="PV", ASPECT="PFV", MOOD="IND")], g
        )
        v = forest.trees[0].children[0]
        eqs = set(v.equations)
        assert "(↑ VOICE) = 'PV'" in eqs
        assert "(↑ ASPECT) = 'PFV'" in eqs
        assert "(↑ MOOD) = 'IND'" in eqs

    def test_lex_equations_from_lexical_entry(self) -> None:
        g = _grammar(Rule("S", ["V"], []))
        le = LexicalEntry(
            lemma="kain",
            pred="EAT <SUBJ, OBJ>",
            a_structure=["AGENT", "PATIENT"],
            morph_constraints={"VOICE": "PV"},
            gf_defaults={},
        )
        forest = parse_with_annotations(
            [[(MorphAnalysis(lemma="kain", pos="V", feats={"VOICE": "PV"}), le)]],
            g,
        )
        v = forest.trees[0].children[0]
        assert "(↑ PRED) = 'EAT <SUBJ, OBJ>'" in v.equations
        assert "(↑ LEX-ASTRUCT) = 'AGENT,PATIENT'" in v.equations


# === Forest size cap ======================================================

class TestForestCap:
    def test_cap_truncates(self) -> None:
        g = _grammar(
            Rule("S", ["A"], []),
            Rule("S", ["B"], []),
            Rule("A", ["X"], []),
            Rule("B", ["X"], []),
        )
        forest = parse_with_annotations(
            [_tok("X")], g, forest_size_cap=1
        )
        assert len(forest.trees) == 1

    def test_no_cap_yields_all(self) -> None:
        g = _grammar(
            Rule("S", ["A"], []),
            Rule("S", ["B"], []),
            Rule("A", ["X"], []),
            Rule("B", ["X"], []),
        )
        forest = parse_with_annotations([_tok("X")], g)
        assert len(forest.trees) == 2

    def test_best_k(self) -> None:
        g = _grammar(
            Rule("S", ["A"], []),
            Rule("S", ["B"], []),
            Rule("S", ["C"], []),
            Rule("A", ["X"], []),
            Rule("B", ["X"], []),
            Rule("C", ["X"], []),
        )
        forest = parse_with_annotations([_tok("X")], g)
        assert len(forest.best_k(2)) == 2
        assert len(forest.best_k(10)) == 3


# === Non-content stripping ================================================

class TestStripNonContent:
    def test_unk_only_token_dropped(self) -> None:
        # Period-like junk gets pos='_UNK' from morphology fallback.
        # Parser should still succeed by skipping it.
        g = _grammar(Rule("S", ["V"], []))
        forest = parse_with_annotations(
            [_tok("V"), _tok("_UNK", lemma=".")], g
        )
        assert len(forest.trees) == 1


# === Demo grammar end-to-end ==============================================

class TestDemoGrammar:
    def test_kinain_sentence_via_pipeline(self) -> None:
        # Black-box: the full pipeline parses the demo sentence and
        # produces the c-/f-/a- structures the percolation test expects.
        from tgllfg.pipeline import parse_text
        results = parse_text("Kinain ng aso ang isda.")
        assert len(results) >= 1
        ctree, _, _, _ = results[0]
        assert ctree.label == "S"
        # S → VP_OV, VP_OV → V NP[CASE=GEN] NP[CASE=NOM].
        assert ctree.children[0].label == "VP_OV"
        vp = ctree.children[0]
        assert [c.label for c in vp.children] == [
            "V", "NP[CASE=GEN]", "NP[CASE=NOM]",
        ]

    def test_demo_c_tree_has_lex_equations(self) -> None:
        from tgllfg.pipeline import parse_text
        results = parse_text("Kinain ng aso ang isda.")
        ctree, _, _, _ = results[0]
        v = ctree.children[0].children[0]  # S → VP_OV → V
        assert v.label == "V"
        assert "(↑ VOICE) = 'OV'" in v.equations
        assert "(↑ ASPECT) = 'PFV'" in v.equations
        assert "(↑ PRED) = 'EAT <SUBJ, OBJ>'" in v.equations


# === LeafCompletion accessibility =========================================

class TestForestStructure:
    def test_forest_exposes_roots(self) -> None:
        g = _grammar(Rule("S", ["V"], []))
        forest = parse_with_annotations([_tok("V")], g)
        assert isinstance(forest, PackedForest)
        assert len(forest.roots) == 1
        # Root state is complete and starts at column 0.
        root = forest.roots[0]
        assert root.dot == len(root.rule.rhs)
        assert root.start == 0
        assert root.end == 1
