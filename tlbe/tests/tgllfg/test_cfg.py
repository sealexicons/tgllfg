# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

import pytest

from tgllfg.cfg import (
    CategoryPattern,
    Grammar,
    Rule,
    compile_grammar,
    matches,
    merge_features,
    parse_pattern,
)


# === parse_pattern ========================================================

class TestParsePattern:
    def test_bare_category(self) -> None:
        assert parse_pattern("NP") == CategoryPattern("NP", ())

    def test_single_feature(self) -> None:
        assert parse_pattern("NP[CASE=NOM]") == CategoryPattern(
            "NP", (("CASE", "NOM"),)
        )

    def test_multiple_features_sorted(self) -> None:
        # Input order shuffled; output features sorted by key.
        p = parse_pattern("V[VOICE=PV,ASPECT=PFV]")
        assert p == CategoryPattern("V", (("ASPECT", "PFV"), ("VOICE", "PV")))

    def test_whitespace_tolerated(self) -> None:
        assert parse_pattern("  NP  [ CASE = NOM ]  ") == CategoryPattern(
            "NP", (("CASE", "NOM"),)
        )

    def test_hyphenated_identifiers(self) -> None:
        # OBL-AG is a real feature name in the grammar.
        p = parse_pattern("NP[FOO-BAR=X]")
        assert p.features == (("FOO-BAR", "X"),)

    def test_empty_brackets_rejected(self) -> None:
        with pytest.raises(ValueError):
            parse_pattern("NP[]")

    def test_empty_input_rejected(self) -> None:
        with pytest.raises(ValueError):
            parse_pattern("")

    def test_missing_equals_rejected(self) -> None:
        with pytest.raises(ValueError):
            parse_pattern("NP[CASE]")

    def test_unbalanced_bracket_rejected(self) -> None:
        with pytest.raises(ValueError):
            parse_pattern("NP[CASE=NOM")

    def test_double_equals_rejected(self) -> None:
        with pytest.raises(ValueError):
            parse_pattern("NP[CASE==NOM]")


# === matches (Phase 6.C graph-constraint matching) ========================

class TestMatches:
    """Graph-constraint matcher (Phase 6.C, post-C5): same category;
    every feature the expected pattern demands must be present in the
    candidate; shared features must agree. The candidate may carry
    features the expected doesn't (lex entries are typically richer
    than rule expectations). K&Z 1989 §3 c-structure-faithfulness:
    rules name what they need; candidates must provide.

    Pre-Phase-6.C the matcher was *non-conflict*: bracketed feats
    on the expected side were optional on the candidate side. C5
    removed the legacy implementation (see
    ``project_parser_nonconflict_matcher`` memory for the bug
    pattern that motivated the change).
    """

    def test_identical_match(self) -> None:
        a = parse_pattern("NP[CASE=NOM]")
        assert matches(a, a)

    def test_category_mismatch(self) -> None:
        assert not matches(
            parse_pattern("NP"), parse_pattern("VP"),
        )

    def test_feature_conflict(self) -> None:
        a = parse_pattern("NP[CASE=NOM]")
        b = parse_pattern("NP[CASE=GEN]")
        assert not matches(a, b)
        assert not matches(b, a)

    def test_expected_subset_of_candidate(self) -> None:
        """The headline case: rule expects ``V[VOICE=PV]``; lex
        provides ``V[VOICE=PV,ASPECT=PFV,TR=TR]``. Expected is a
        subset (by key) of candidate, and shared keys agree."""
        expected = parse_pattern("V[VOICE=PV]")
        candidate = parse_pattern("V[VOICE=PV,ASPECT=PFV,TR=TR]")
        assert matches(expected, candidate)

    def test_candidate_lacks_demanded_feat_fails(self) -> None:
        """The directional asymmetry of graph-constraint matching:
        expected demands ``CASE=NOM`` but candidate is bare ``NP``;
        the candidate doesn't satisfy the demand."""
        expected = parse_pattern("NP[CASE=NOM]")
        candidate = parse_pattern("NP")
        assert not matches(expected, candidate)

    def test_disjoint_features_fails(self) -> None:
        """Expected demands ``VOICE``; candidate has only ``ASPECT``.
        The matcher rejects because ``VOICE`` is absent on
        candidate."""
        expected = parse_pattern("V[VOICE=PV]")
        candidate = parse_pattern("V[ASPECT=PFV]")
        assert not matches(expected, candidate)

    def test_bare_expected_matches_anything_same_category(self) -> None:
        """Expected demands nothing (bare ``NP``); any same-category
        candidate matches, regardless of its feats."""
        expected = parse_pattern("NP")
        candidate_bare = parse_pattern("NP")
        candidate_rich = parse_pattern("NP[CASE=NOM,GENDER=M]")
        assert matches(expected, candidate_bare)
        assert matches(expected, candidate_rich)

    def test_candidate_extra_keys_admitted(self) -> None:
        """Candidate richer than expected — expected demands
        ``CASE=NOM``; candidate carries ``CASE=NOM,GENDER=M``. The
        extra ``GENDER`` doesn't gate the match.
        """
        expected = parse_pattern("NP[CASE=NOM]")
        candidate = parse_pattern("NP[CASE=NOM,GENDER=M]")
        assert matches(expected, candidate)

    def test_empty_features_both_sides(self) -> None:
        """Both bare: trivially matches."""
        assert matches(parse_pattern("S"), parse_pattern("S"))


# === merge_features =======================================================

class TestMergeFeatures:
    def test_disjoint_features(self) -> None:
        a = parse_pattern("V[VOICE=PV]")
        b = parse_pattern("V[ASPECT=PFV]")
        merged = merge_features(a, b)
        assert merged == parse_pattern("V[VOICE=PV,ASPECT=PFV]")

    def test_b_overrides_on_overlap(self) -> None:
        # merge_features doesn't enforce non-conflict; caller's job.
        a = parse_pattern("NP[CASE=NOM]")
        b = parse_pattern("NP[CASE=GEN]")
        merged = merge_features(a, b)
        assert merged == parse_pattern("NP[CASE=GEN]")


# === CompiledGrammar ======================================================

class TestCompiledGrammar:
    def test_indexes_by_lhs_category(self) -> None:
        rules = [
            Rule("NP[CASE=NOM]", ["DET", "N"], []),
            Rule("NP[CASE=GEN]", ["ADP", "N"], []),
            Rule("VP", ["V", "NP"], []),
        ]
        cg = compile_grammar(Grammar(rules))
        np_rules = cg.rules_for(parse_pattern("NP[CASE=NOM]"))
        assert len(np_rules) == 1
        assert np_rules[0].lhs == parse_pattern("NP[CASE=NOM]")

    def test_rules_for_returns_compatible_only(self) -> None:
        rules = [
            Rule("NP[CASE=NOM]", ["DET", "N"], []),
            Rule("NP[CASE=GEN]", ["ADP", "N"], []),
        ]
        cg = compile_grammar(Grammar(rules))
        # Asking for NP[CASE=NOM] should return only the NOM rule.
        np_nom = cg.rules_for(parse_pattern("NP[CASE=NOM]"))
        assert len(np_nom) == 1
        # Asking for bare NP should return both (no conflict).
        np_any = cg.rules_for(parse_pattern("NP"))
        assert len(np_any) == 2

    def test_rules_for_unknown_category(self) -> None:
        cg = compile_grammar(Grammar([Rule("S", ["X"], [])]))
        assert cg.rules_for(parse_pattern("UNKNOWN")) == ()

    def test_is_nonterminal(self) -> None:
        rules = [
            Rule("S", ["VP"], []),
            Rule("VP", ["V", "NP"], []),
            Rule("NP", ["DET", "N"], []),
        ]
        cg = compile_grammar(Grammar(rules))
        assert cg.is_nonterminal(parse_pattern("S"))
        assert cg.is_nonterminal(parse_pattern("VP"))
        assert cg.is_nonterminal(parse_pattern("NP"))
        # V, DET, N never appear as LHS → preterminals.
        assert not cg.is_nonterminal(parse_pattern("V"))
        assert not cg.is_nonterminal(parse_pattern("DET"))
        assert not cg.is_nonterminal(parse_pattern("N"))

    def test_default_grammar_compiles(self) -> None:
        # The shipped grammar must compile without errors.
        cg = compile_grammar(Grammar.load_default())
        assert len(cg.rules) > 0
        # S is the start symbol and must be a non-terminal.
        assert cg.is_nonterminal(CategoryPattern("S", ()))


# === Round-trip ===========================================================

class TestRoundTrip:
    def test_pattern_preserves_via_compile(self) -> None:
        rule = Rule("VP_PV", ["V[VOICE=PV]", "NP[CASE=GEN]", "NP[CASE=NOM]"], [])
        from tgllfg.cfg import compile_rule
        cr = compile_rule(rule)
        assert cr.lhs == parse_pattern("VP_PV")
        assert cr.rhs == (
            parse_pattern("V[VOICE=PV]"),
            parse_pattern("NP[CASE=GEN]"),
            parse_pattern("NP[CASE=NOM]"),
        )
