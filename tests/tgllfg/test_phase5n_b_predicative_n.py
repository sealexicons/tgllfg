"""Phase 5n.B Commit 2: predicative-N clause (§18 L43).

Closes §18.1 deferral L43 (``Mas maraming aklat ako.``) by
adding a clausal rule

    S → N NP[CASE=NOM]
        (↑ PRED) = 'BE-N <SUBJ>'
        (↑ SUBJ) = ↓2
        (↑ N_LEMMA) = ↓1 LEMMA
        (↑ PREDICATIVE) = 'YES'
        ¬ (↓1 WH)

in ``cfg/clause.py``. Tagalog admits bare-NP predication with
no copula; the predicate is an N-headed phrase (bare N or N
modified by ADJ / Q via the existing N-level modifier rules)
and the SUBJ is a NOM-NP / NOM-PRON pivot.

Sibling rules:

* Phase 5g Commit 3 — predicative-ADJ
  (``S → ADJ[PREDICATIVE=YES] NP[CASE=NOM]``)
* Phase 5f Commit 4 — predicative-cardinal
  (``S → NUM[CARDINAL=YES] NP[CASE=NOM]``)
* Phase 5n.B Commit 1 — predicative-Q
  (``S → Q[VAGUE=YES] NP[CASE=NOM]``)

The single PRED template ``BE-N <SUBJ>`` covers both equational
and possessive readings of bare-NP predication; semantic
disambiguation is contextual.

The ``¬ (↓1 WH)`` constraint disambiguates the predicative-N
rule from the Phase 5i Commit 6 wh-N-cleft (``S → N[WH=YES]
NP[CASE=NOM]``).
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _predicative_n_parse(text: str) -> FStructure | None:
    parses = parse_text(text, n_best=10)
    for _ct, fs, _astr, _diags in parses:
        if fs.feats.get("PRED") == "BE-N <SUBJ>":
            return fs
    return None


# === Bare N predicate + NOM-PRON =====================================


class TestBareNPredicativeWithPron:
    """Bare-N predicate over a NOM-PRON pivot."""

    @pytest.mark.parametrize("sentence,n_lemma", [
        ("Doktor ako.",     "doktor"),
        ("Estudyante ka.",  "estudyante"),
        ("Doktor siya.",    "doktor"),
        ("Estudyante kami.", "estudyante"),
    ])
    def test_bare_n_with_pron(
        self, sentence: str, n_lemma: str
    ) -> None:
        fs = _predicative_n_parse(sentence)
        assert fs is not None, f"no predicative-N parse for {sentence!r}"
        assert fs.feats.get("N_LEMMA") == n_lemma
        assert fs.feats.get("PREDICATIVE") == "YES"
        subj = fs.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("CASE") == "NOM"


# === Bare N predicate + proper-noun NOM-NP ===========================


class TestBareNPredicativeWithProper:
    """Bare-N predicate + ``si <Name>`` proper-noun NOM-NP pivot."""

    @pytest.mark.parametrize("sentence,n_lemma", [
        ("Doktor si Maria.",      "doktor"),
        ("Estudyante si Juan.",   "estudyante"),
    ])
    def test_bare_n_with_proper(
        self, sentence: str, n_lemma: str
    ) -> None:
        fs = _predicative_n_parse(sentence)
        assert fs is not None
        assert fs.feats.get("N_LEMMA") == n_lemma
        subj = fs.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("CASE") == "NOM"
        assert subj.feats.get("MARKER") == "SI"


# === Q-modified N predicate ==========================================


class TestQModifiedNPredicative:
    """Q-modified N as predicate. ``Maraming aklat ako.`` "I have
    many books"; ``Mas maraming aklat ako.`` "I have more books".
    The N-level vague-Q rule (Phase 5f Commit 15 N companion)
    builds the modified N; the new clause rule consumes it."""

    def test_maraming_aklat_ako(self) -> None:
        fs = _predicative_n_parse("Maraming aklat ako.")
        assert fs is not None
        assert fs.feats.get("N_LEMMA") == "aklat"

    def test_mas_maraming_aklat_ako(self) -> None:
        # Phase 5h Commit 7 mas-wrapped Q feeds the N-level rule;
        # the N then heads the predicative-N clause.
        fs = _predicative_n_parse("Mas maraming aklat ako.")
        assert fs is not None
        assert fs.feats.get("N_LEMMA") == "aklat"


# === Negation composition ============================================


class TestPredicativeNWithNegation:
    """Phase 4 §7.2 hindi-wrap composes with predicative-N."""

    def test_hindi_doktor_ako(self) -> None:
        fs = _predicative_n_parse("Hindi doktor ako.")
        assert fs is not None
        assert fs.feats.get("N_LEMMA") == "doktor"
        assert fs.feats.get("POLARITY") == "NEG"


# === Disambiguation against wh-N cleft ===============================


class TestWhNDoesNotFirePredicativeN:
    """The Phase 5i Commit 6 wh-N cleft fires on N[WH=YES]; the
    predicative-N rule's ``¬ (↓1 WH)`` excludes wh-N from
    producing a parallel BE-N parse."""

    def test_aling_bata_only_wh_cleft(self) -> None:
        # ``Aling bata ang kumain?`` — wh-N cleft.
        parses = parse_text("Aling bata ang kumain?")
        assert len(parses) >= 1
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("PRED") != "BE-N <SUBJ>"
        wh_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1


# === Regression: sibling predicative rules unaffected ================


class TestSiblingPredicativeRulesUnaffected:
    """The new predicative-N rule does not perturb the existing
    Phase 5g predicative-ADJ, Phase 5f predicative-cardinal, or
    Phase 5n.B Commit 1 predicative-Q rules."""

    def test_predicative_adj_unaffected(self) -> None:
        parses = parse_text("Maganda ang bata.")
        adj_parses = [
            p for p in parses
            if p[1].feats.get("PRED") == "ADJ <SUBJ>"
        ]
        assert len(adj_parses) >= 1

    def test_predicative_cardinal_unaffected(self) -> None:
        parses = parse_text("Tatlo ang aklat.")
        card_parses = [
            p for p in parses
            if p[1].feats.get("PRED") == "CARDINAL <SUBJ>"
        ]
        assert len(card_parses) >= 1

    def test_predicative_q_unaffected(self) -> None:
        parses = parse_text("Marami ang aklat.")
        q_parses = [
            p for p in parses
            if p[1].feats.get("PRED") == "Q-PREDICATIVE <SUBJ>"
        ]
        assert len(q_parses) >= 1


# === Regression: V-headed clauses unaffected =========================


class TestVHeadedClausesUnaffected:
    """V-headed AV / OV clauses parse via the Phase 4 verb-frame
    rules, not predicative-N. The new rule's left daughter is
    ``N`` (not ``V``), so V-initial surfaces don't fire it."""

    def test_av_intransitive(self) -> None:
        parses = parse_text("Kumain ang bata.")
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("PRED") != "BE-N <SUBJ>"

    def test_av_transitive(self) -> None:
        parses = parse_text("Kumain ang bata ng isda.")
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("PRED") != "BE-N <SUBJ>"
