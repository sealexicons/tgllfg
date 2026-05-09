"""Phase 5n.B Commit 4: pinaka- on Q heads (§18 L40).

Closes §18.1 deferral L40 (``pinakamadalas``, ``pinakamarami``)
by adding direct lex entries in ``data/tgl/particles.yaml``
for the productive ``pinaka-`` superlative derivation on the
closed-class vague-Q inventory and on the FREQUENCY adverbs
(``madalas`` / ``minsan``).

Six new Q entries:
* ``pinakamarami`` Q[QUANT=MANY, VAGUE=YES, COMP_DEGREE=SUPERLATIVE]
* ``pinakakonti``  Q[QUANT=FEW]
* ``pinakakaunti`` Q[QUANT=FEW]
* ``pinakakakaunti`` Q[QUANT=VERY_FEW]
* ``pinakaiilan``  Q[QUANT=FEW]
* ``pinakakaramihan`` Q[QUANT=MOST]

Two new ADV entries:
* ``pinakamadalas`` ADV[FREQUENCY, FREQ_VALUE=HIGH, COMP_DEGREE=SUPERLATIVE]
* ``pinakaminsan``  ADV[FREQUENCY, FREQ_VALUE=SOMETIMES]

Each entry uses the orthographic-variant ``LEMMA`` convention
(Phase 5j Commit 7) — the analysis's lemma routes to the bare-Q
or bare-ADV canonical form.

The Phase 5n.B Commit 1 predicative-Q clause rule fires on the
new Q surfaces unchanged (``Pinakamarami ang aklat.`` →
``PRED='Q-PREDICATIVE <SUBJ>'``); the Phase 5f Commit 15
vague-Q NP-modifier rule fires on the linker-fused forms
(``pinakamaraming aklat`` "the most books") unchanged. Direct-
lex closes L40 without requiring a Q-paradigm-engine
infrastructure extension.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import analyze_tokens
from tgllfg.text.tokenizer import tokenize


def _morph_analyses(surface: str) -> list:
    toks = tokenize(surface)
    ml = analyze_tokens(toks)
    if not ml:
        return []
    return ml[0]


# === Morph analysis: pinaka- + Q ====================================


class TestPinakaQMorph:
    """Each ``pinaka-`` Q form is morph-analyzed as Q[VAGUE=YES,
    COMP_DEGREE=SUPERLATIVE] with the canonical bare-Q lemma."""

    @pytest.mark.parametrize("surface,expected_lemma,expected_quant", [
        ("pinakamarami",      "marami",    "MANY"),
        ("pinakakonti",       "konti",     "FEW"),
        ("pinakakaunti",      "kaunti",    "FEW"),
        ("pinakakakaunti",    "kakaunti",  "VERY_FEW"),
        ("pinakaiilan",       "iilan",     "FEW"),
        ("pinakakaramihan",   "karamihan", "MOST"),
    ])
    def test_pinaka_q_analysis(
        self,
        surface: str,
        expected_lemma: str,
        expected_quant: str,
    ) -> None:
        anals = _morph_analyses(surface)
        q_anals = [a for a in anals if a.pos == "Q"]
        assert len(q_anals) >= 1, (
            f"no Q analysis for {surface!r}; got {anals}"
        )
        a = q_anals[0]
        assert a.lemma == expected_lemma
        assert a.feats.get("QUANT") == expected_quant
        assert a.feats.get("VAGUE") == "YES"
        assert a.feats.get("COMP_DEGREE") == "SUPERLATIVE"


# === Morph analysis: pinaka- + ADV ==================================


class TestPinakaAdvMorph:
    """``pinakamadalas`` / ``pinakaminsan`` analyze as ADV[FREQUENCY,
    COMP_DEGREE=SUPERLATIVE] with the canonical bare-ADV lemma."""

    @pytest.mark.parametrize("surface,expected_lemma,expected_freq", [
        ("pinakamadalas",  "madalas", "HIGH"),
        ("pinakaminsan",   "minsan",  "SOMETIMES"),
    ])
    def test_pinaka_adv_analysis(
        self,
        surface: str,
        expected_lemma: str,
        expected_freq: str,
    ) -> None:
        anals = _morph_analyses(surface)
        adv_anals = [a for a in anals if a.pos == "ADV"]
        assert len(adv_anals) >= 1
        a = adv_anals[0]
        assert a.lemma == expected_lemma
        assert a.feats.get("ADV_TYPE") == "FREQUENCY"
        assert a.feats.get("FREQ_VALUE") == expected_freq
        assert a.feats.get("COMP_DEGREE") == "SUPERLATIVE"


# === Predicative-Q with pinaka- =====================================


class TestPinakaQPredicative:
    """Phase 5n.B Commit 1 predicative-Q clause rule fires on the
    new ``pinaka-`` Q surfaces. Per Phase 5g / 5h convention
    (predicative-ADJ doesn't lift COMP_DEGREE either) the
    Phase 5n.B Commit 1 predicative-Q rule lifts ``Q_LEMMA`` and
    ``QUANT`` but not ``COMP_DEGREE`` to the matrix; the
    superlative degree marking is verified at the morph layer
    (``TestPinakaQMorph`` above) and persists on the Q daughter
    in the c-tree."""

    @pytest.mark.parametrize("sentence,q_lemma,quant", [
        ("Pinakamarami ang aklat.",     "marami",    "MANY"),
        ("Pinakakonti ang isda.",       "konti",     "FEW"),
        ("Pinakakaramihan ang aklat.",  "karamihan", "MOST"),
    ])
    def test_predicative_q_pinaka(
        self, sentence: str, q_lemma: str, quant: str
    ) -> None:
        parses = parse_text(sentence)
        pred_parses = [
            p for p in parses
            if p[1].feats.get("PRED") == "Q-PREDICATIVE <SUBJ>"
        ]
        assert len(pred_parses) >= 1, (
            f"no predicative-Q parse for {sentence!r}"
        )
        _ct, fs, _astr, _diags = pred_parses[0]
        assert fs.feats.get("Q_LEMMA") == q_lemma
        assert fs.feats.get("QUANT") == quant
        assert fs.feats.get("PREDICATIVE") == "YES"


# === NP-modifier with pinaka- =======================================


class TestPinakaQNpModifier:
    """The Phase 5f Commit 15 vague-Q NP-modifier rule (``NP →
    DET/ADP Q PART[LINK] N``) fires on the new ``pinaka-`` Q
    surfaces; the linker-fused form ``pinakamaraming aklat`` is
    a well-formed NP."""

    def test_pinaka_q_in_obj_np(self) -> None:
        parses = parse_text("Bumili siya ng pinakamaraming aklat.")
        assert len(parses) >= 1
        # Top parse should have BUY PRED.
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith("BUY")

    def test_pinaka_q_in_subj_np(self) -> None:
        parses = parse_text("Kumain ang pinakamaraming bata.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith("EAT")


# === Negation composition ===========================================


class TestPinakaQNegation:
    """Phase 4 §7.2 hindi-wrap composes with predicative-Q +
    pinaka-."""

    def test_hindi_pinakamarami(self) -> None:
        parses = parse_text("Hindi pinakamarami ang aklat.")
        pred_parses = [
            p for p in parses
            if p[1].feats.get("PRED") == "Q-PREDICATIVE <SUBJ>"
        ]
        assert len(pred_parses) >= 1
        _ct, fs, _astr, _diags = pred_parses[0]
        assert fs.feats.get("POLARITY") == "NEG"


# === Regression: existing pinaka_adj cell unaffected =================


class TestPinakaAdjUnaffected:
    """``pinakamaganda`` continues to analyze via the existing
    Phase 5h Commit 1 ``pinaka_adj`` paradigm cell as ADJ
    [COMP_DEGREE=SUPERLATIVE]; the new lex-direct Q entries do
    not perturb the productive ADJ paradigm engine."""

    def test_pinakamaganda_unchanged(self) -> None:
        anals = _morph_analyses("pinakamaganda")
        adj_anals = [a for a in anals if a.pos == "ADJ"]
        assert len(adj_anals) >= 1
        a = adj_anals[0]
        assert a.lemma == "ganda"
        assert a.feats.get("COMP_DEGREE") == "SUPERLATIVE"
        assert a.feats.get("PREDICATIVE") == "YES"
