"""Phase 5n.B Commit 1: predicative-Q clause (§18 L42 + L52).

Closes §18.1 deferrals L42 (``Mas marami ang aklat.``) and L52
(``Marami ang aklat.``) by adding a single clausal rule

    S → Q[VAGUE=YES] NP[CASE=NOM]
        (↑ PRED) = 'Q-PREDICATIVE <SUBJ>'
        (↑ SUBJ) = ↓2
        (↑ Q_LEMMA) = ↓1 LEMMA
        (↑ QUANT) = ↓1 QUANT
        (↑ PREDICATIVE) = 'YES'
        (↓1 VAGUE) =c 'YES'
        ¬ (↓1 WH)

in ``cfg/clause.py``. Structurally analogous to the Phase 5g
Commit 3 predicative-ADJ rule and the Phase 5f Commit 4
predicative-cardinal rule. The rule fires on bare vague-Q
heads (``marami`` / ``konti`` / ``kakaunti`` / ``iilan`` /
``karamihan``) and on the Phase 5h Commit 7 ``mas``-wrapped
comparative variants (``mas marami`` / ``mas konti``).

The ``¬ (↓1 WH)`` neg-existential constraint disambiguates the
predicative-Q rule from the Phase 5i Commit 9 (a) wh-Q cleft
(which fires on Q[WH=YES] heads like ``magkano`` / ``ilan``-wh
/ ``alin``-wh and produces ``PRED='WH <SUBJ>'`` / ``Q_TYPE=WH``).
``ilan`` is double-lex'd: the wh entry feeds the cleft, the
non-wh ``FEW`` entry feeds the predicative-Q rule, so
``Ilan ang aklat?`` produces two parses.

Phase 5n.B Commit 1 also extends the morph-analyzer's auto-LEMMA
list to include ``Q`` so that bare vague-Q heads — which lack an
explicit ``LEMMA`` feat in ``data/tgl/particles.yaml`` — carry
``LEMMA = surface`` in their f-structure feats. This lets the
new rule's ``(↑ Q_LEMMA) = ↓1 LEMMA`` lift the lemma cleanly.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _predicative_q_parse(text: str) -> FStructure | None:
    """Find a parse with ``PRED='Q-PREDICATIVE <SUBJ>'``."""
    parses = parse_text(text, n_best=10)
    for _ct, fs, _astr, _diags in parses:
        if fs.feats.get("PRED") == "Q-PREDICATIVE <SUBJ>":
            return fs
    return None


# === Bare vague-Q + NOM-NP ===========================================


class TestBareVagueQPredicative:
    """Bare vague-Q heads as matrix predicate over a NOM-NP pivot."""

    @pytest.mark.parametrize("sentence,q_lemma,quant", [
        ("Marami ang aklat.",      "marami",    "MANY"),
        ("Konti ang isda.",        "konti",     "FEW"),
        ("Kaunti ang isda.",       "kaunti",    "FEW"),
        ("Kakaunti ang isda.",     "kakaunti",  "VERY_FEW"),
        ("Karamihan ang aklat.",   "karamihan", "MOST"),
        ("Iilan ang bata.",        "iilan",     "FEW"),
    ])
    def test_bare_vague_q(
        self, sentence: str, q_lemma: str, quant: str
    ) -> None:
        fs = _predicative_q_parse(sentence)
        assert fs is not None, f"no predicative-Q parse for {sentence!r}"
        assert fs.feats.get("Q_LEMMA") == q_lemma
        assert fs.feats.get("QUANT") == quant
        assert fs.feats.get("PREDICATIVE") is True
        subj = fs.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("CASE") == "NOM"


# === Bare vague-Q + NOM-PRON =========================================


class TestBareVagueQWithPron:
    """Bare vague-Q + NOM-PRON pivot — ``Marami sila`` "There are
    many of them"."""

    def test_marami_sila(self) -> None:
        fs = _predicative_q_parse("Marami sila.")
        assert fs is not None
        assert fs.feats.get("Q_LEMMA") == "marami"
        assert fs.feats.get("QUANT") == "MANY"
        subj = fs.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("CASE") == "NOM"
        assert subj.feats.get("NUM") == "PL"


# === mas-wrapped comparative-Q + NOM-NP ==============================


class TestMasComparativeQPredicative:
    """The Phase 5h Commit 7 ``mas`` wrapper produces a
    ``Q[VAGUE=YES, COMP_DEGREE=COMPARATIVE]`` head — the new
    predicative-Q rule fires on it because ``VAGUE=YES``
    percolates through the wrapper's ``(↑) = ↓2`` share."""

    @pytest.mark.parametrize("sentence,q_lemma,quant", [
        ("Mas marami ang aklat.",   "marami", "MANY"),
        ("Mas konti ang isda.",     "konti",  "FEW"),
        ("Mas kaunti ang bata.",    "kaunti", "FEW"),
    ])
    def test_mas_q_predicative(
        self, sentence: str, q_lemma: str, quant: str
    ) -> None:
        fs = _predicative_q_parse(sentence)
        assert fs is not None, f"no predicative-Q parse for {sentence!r}"
        assert fs.feats.get("Q_LEMMA") == q_lemma
        assert fs.feats.get("QUANT") == quant


# === Negation composition ============================================


class TestPredicativeQWithNegation:
    """The Phase 4 §7.2 hindi-wrap composes with the predicative-Q
    matrix without disturbing the Q-PREDICATIVE PRED."""

    def test_hindi_marami_ang_aklat(self) -> None:
        fs = _predicative_q_parse("Hindi marami ang aklat.")
        assert fs is not None
        assert fs.feats.get("Q_LEMMA") == "marami"
        assert fs.feats.get("POLARITY") == "NEG"


# === Disambiguation against Phase 5i Commit 9 (a) wh-Q cleft =========


class TestWhQDoesNotFirePredicativeQ:
    """The wh-Q cleft fires on Q[WH=YES]; the predicative-Q rule
    must NOT fire on wh-Qs (``¬ (↓1 WH)`` constraint). Wh surfaces
    continue to produce ``PRED='WH <SUBJ>'`` / ``Q_TYPE=WH``."""

    def test_magkano_only_wh_cleft(self) -> None:
        # ``magkano`` is Q[WH=YES, VAGUE=YES, QUANT=HOW_MUCH]; the
        # predicative-Q rule's ``¬ (↓1 WH)`` excludes it. Only the
        # wh-cleft fires.
        parses = parse_text("Magkano ang isda?")
        assert len(parses) >= 1
        # No Q-PREDICATIVE parse:
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("PRED") != "Q-PREDICATIVE <SUBJ>"
        # And there is a WH parse:
        wh_parses = [
            p for p in parses
            if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1


class TestIlanPolysemyProducesBothReadings:
    """``ilan`` is double-lex'd: Q[WH=YES, QUANT=HOW_MANY] (wh
    use) and Q[QUANT=FEW] (the 'a few' polysemy partner). The
    wh-cleft fires on the wh entry; the predicative-Q rule fires
    on the FEW entry. ``Ilan ang aklat?`` therefore produces two
    parses with distinct PREDs."""

    def test_ilan_ang_aklat_two_parses(self) -> None:
        parses = parse_text("Ilan ang aklat?")
        assert len(parses) >= 2
        preds = {p[1].feats.get("PRED") for p in parses}
        assert "Q-PREDICATIVE <SUBJ>" in preds
        assert "WH <SUBJ>" in preds


# === Regression: predicative-cardinal still works ====================


class TestPredicativeCardinalUnchanged:
    """``Tatlo ang aklat.`` continues to parse via the Phase 5f
    Commit 4 predicative-cardinal rule — no leak from the new
    predicative-Q rule. The cardinal head carries
    ``CARDINAL=YES`` (not ``VAGUE=YES``), so the new rule's
    category-pattern + ``(↓1 VAGUE) =c 'YES'`` constraint
    excludes it."""

    def test_tatlo_ang_aklat_predicative_cardinal(self) -> None:
        parses = parse_text("Tatlo ang aklat.")
        assert len(parses) >= 1
        cardinal_parses = [
            p for p in parses
            if p[1].feats.get("PRED") == "CARDINAL <SUBJ>"
        ]
        assert len(cardinal_parses) >= 1
        # And no Q-PREDICATIVE leak:
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("PRED") != "Q-PREDICATIVE <SUBJ>"


# === Regression: NP-modifier path still fires for vague-Q ============


class TestVagueQNpModifierUnchanged:
    """The Phase 5f Commit 15 vague-Q NP-modifier rule (``NP →
    Q[VAGUE=YES] PART[LINK] N``) continues to parse ``maraming
    aklat`` / ``kaunting aklat`` inside larger clauses without
    interference from the new clausal predicative-Q rule."""

    def test_maraming_aklat_in_obj(self) -> None:
        # ``Bumili siya ng maraming aklat.`` "He bought many books."
        parses = parse_text("Bumili siya ng maraming aklat.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # Matrix is V-headed (BUY), not predicative-Q.
        assert fs.feats.get("PRED", "").startswith("BUY")
