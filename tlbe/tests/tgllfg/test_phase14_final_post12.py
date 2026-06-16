# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 14.final.post-12 — grammar coverage for user-reported gaps.

Three constructions the inspector surfaced as non-parsing (or mis-parsing):

* the ``ang`` + quality-noun exclamative for ``bilis`` (``Ang bilis ng
  panahon!`` "how fast time goes!") — a one-line ``SEM_CLASS=QUALITY`` lexical
  tag, since the Phase 10.E.1 exclamative already accepts a full ng-NP
  possessor;
* the solve-path f-structure dedup that collapses spurious *c-structure*
  ambiguity which neutralizes in the f-structure (the ``ng panahon`` TIME-noun
  double projection);
* the one-token grammaticalized ``diba`` tag question (with and without the
  comma).
"""

from tgllfg.core.pipeline import parse_text


class TestAngQualityNounExclamative:
    def test_bilis_ng_panahon(self) -> None:
        # `bilis` (now SEM_CLASS=QUALITY) heads the ang-exclamative with a full
        # ng-NP possessor; exactly one parse (the TIME-noun double projection is
        # collapsed by the solve-path dedup below).
        parses = parse_text("Ang bilis ng panahon.", n_best=5)
        assert len(parses) == 1
        fs = parses[0][1]
        assert fs.feats.get("PRED") == "ADJ <SUBJ>"
        assert fs.feats.get("EXCLAM") is True
        assert fs.feats.get("ADJ_LEMMA") == "bilis"

    def test_bang_form_parses(self) -> None:
        assert len(parse_text("Ang bilis ng panahon!", n_best=5)) == 1


class TestSolvePathFStructureDedup:
    def test_time_noun_possessor_single_parse(self) -> None:
        # ang + QualityN + ng-(TIME-noun): the head noun projects via both
        # N[N_CORE] and N[SEM_CLASS=TIME] into the one possessor NP, giving two
        # identical f-structures. The dedup keeps one. (`ganda` already carried
        # SEM_CLASS=QUALITY, so this duplicated even before the bilis fix.)
        assert len(parse_text("Ang ganda ng panahon.", n_best=5)) == 1

    def test_non_time_noun_unaffected(self) -> None:
        # A non-TIME possessor never double-projected — still one parse.
        assert len(parse_text("Ang ganda ng bata.", n_best=5)) == 1


class TestDibaTagQuestion:
    def test_comma_form(self) -> None:
        parses = parse_text("Maganda ang babae, diba?", n_best=5)
        assert len(parses) == 1
        assert parses[0][1].feats.get("Q_TYPE") == "TAG"

    def test_no_comma_form(self) -> None:
        parses = parse_text("Maganda ang babae diba?", n_best=5)
        assert len(parses) == 1
        assert parses[0][1].feats.get("Q_TYPE") == "TAG"

    def test_verbal_clause_tag(self) -> None:
        parses = parse_text("Kumain ka, diba?", n_best=5)
        assert len(parses) == 1
        assert parses[0][1].feats.get("Q_TYPE") == "TAG"

    def test_plain_clause_has_no_tag(self) -> None:
        # The same matrix without `diba` is not a tag question (and bare `di`
        # — NEG_TAG only — never satisfies the one-token NEG_TAG+QUESTION rule).
        parses = parse_text("Maganda ang babae.", n_best=5)
        assert parses[0][1].feats.get("Q_TYPE") is None


class TestMWEInfrastructure:
    def test_migrated_noun_mwes_still_parse(self) -> None:
        # oras Pilipino / ibig sabihin moved from nouns.yaml + the hardcoded
        # _MULTIWORD_NORMS bigram set to data-driven mwe.yaml; behaviour kept.
        assert len(parse_text("Ang ibig sabihin ay laging huli.", n_best=5)) >= 1
        assert len(parse_text("Maganda ang oras Pilipino.", n_best=5)) >= 1

    def test_ngram_merge_collapses_trigram(self) -> None:
        from tgllfg.text.multiword import merge_multiword_compounds
        from tgllfg.text.tokenizer import tokenize

        merged = merge_multiword_compounds(tokenize("Parang kailan lang, ang aso."))
        # The trigram collapses to a single token (bigram-only could not).
        assert "parang kailan lang" in [t.norm for t in merged]

    def test_multiword_norms_data_driven(self) -> None:
        from tgllfg.morph import Analyzer

        norms = Analyzer.from_default().multiword_norms()
        assert {"oras pilipino", "ibig sabihin", "parang kailan lang"} <= norms


class TestParangKailanLangMWE:
    def test_full_sentence_single_parse(self) -> None:
        # The user's sentence: the discourse-temporal MWE adverbial + comma + a
        # compositional ang-exclamative, parsed by the existing AdvP comma-
        # fronting rule (no new grammar rule). One parse (the inner TIME-noun
        # projection ambiguity is collapsed by the solve-path dedup).
        parses = parse_text("Parang kailan lang, ang bilis ng panahon.", n_best=5)
        assert len(parses) == 1
        fs = parses[0][1]
        assert fs.feats.get("PRED") == "ADJ <SUBJ>"
        assert fs.feats.get("EXCLAM") is True
        adj = fs.feats.get("ADJUNCT")
        assert adj and any(
            m.feats.get("LEMMA") == "parang kailan lang"
            for m in adj
            if hasattr(m, "feats")
        )

    def test_productive_over_a_clause(self) -> None:
        # The MWE is the minimal fixed core; the following clause is
        # compositional, so the adverbial prefaces other clauses too.
        assert len(parse_text("Parang kailan lang, kumain ang aso.", n_best=5)) == 1

    def test_non_mwe_parang_unaffected(self) -> None:
        # Bare `parang` (the comparative/raising verb) is untouched: the merge
        # only fires on the full `parang kailan lang` trigram.
        parses = parse_text("Parang aso ang bata.", n_best=5)
        assert parses and str(parses[0][1].feats.get("PRED", "")).startswith("LIKE")
