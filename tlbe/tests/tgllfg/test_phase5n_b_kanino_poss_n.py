# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.B Commit 15: Kanino predicative possessor over N (§18 L59).

Closes §18.1 deferral L59 by adding a 3-daughter sibling rule
to the Phase 5i Commit 9 (b) bare DAT-cleft:

    Kanino kaibigan ito?     "Whose friend is this?"
    Kanino aklat ito?        "Whose book is this?"
    Kanino bahay si Maria?   "Whose house is Maria?" (silly but
                              structural)

The new rule shape ``S → PRON[WH=YES, CASE=DAT] N NP[CASE=NOM]``
mirrors the Phase 5n.B C2 predicative-N rule
(``S → N NP[CASE=NOM]``) with an explicit DAT-PRON possessor
fronted before the predicate-N. The matrix carries:

  PRED        = 'BE-N <SUBJ>'
  SUBJ        = the NOM-NP (the possessee referent)
  N_LEMMA     = the predicate-N's lemma
  POSS        = the wh-PRON (kanino) f-structure
  WH_LEMMA    = 'kanino'
  Q_TYPE      = 'WH'
  PREDICATIVE = 'YES'

Coexistence with Phase 5i C9 wh-fronting: the existing
``S → PRON[WH=YES, CASE=DAT] S`` rule also fires here (because
``kaibigan ito`` parses as an S via the C2 predicative-N rule),
producing a parallel parse with kanino in ADJUNCT instead of
POSS. Both parses are linguistically valid; the new C15 rule
provides the cleaner POSS-slot semantics. Tests filter for the
POSS-slot parse to validate the new rule fires.
"""

import pytest

from tgllfg.core.pipeline import parse_text


def _poss_parse(text: str):
    """Return the parse with a POSS slot — i.e., the new C15
    parse — or None."""
    parses = parse_text(text, n_best=10)
    for p in parses:
        if p[1].feats.get("POSS"):
            return p
    return None


# === Kanino + N + NOM-NP =============================================


class TestKaninoPossOverN:
    """The 3-daughter cleft rule fires on a range of N + NOM-NP
    combinations."""

    @pytest.mark.parametrize("sentence,n_lemma", [
        ("Kanino kaibigan ito?",      "kaibigan"),
        ("Kanino aklat ito?",         "aklat"),
        ("Kanino bahay ito?",         "bahay"),
        ("Kanino kaibigan si Maria?", "kaibigan"),
        ("Kanino aklat si Maria?",    "aklat"),
    ])
    def test_kanino_n_nom_parses(
        self, sentence: str, n_lemma: str
    ) -> None:
        result = _poss_parse(sentence)
        assert result is not None, (
            f"{sentence!r} did not produce a parse with POSS slot"
        )
        _ct, fs, _astr, _diags = result
        assert fs.feats.get("PRED") == "BE-N <SUBJ>"
        assert fs.feats.get("N_LEMMA") == n_lemma
        assert fs.feats.get("Q_TYPE") == "WH"
        assert fs.feats.get("WH_LEMMA") == "kanino"
        assert fs.feats.get("PREDICATIVE") is True
        # POSS carries the wh-PRON's f-structure.
        poss = fs.feats.get("POSS")
        assert poss is not None
        assert poss.feats.get("LEMMA") == "kanino"
        assert poss.feats.get("WH") is True
        assert poss.feats.get("CASE") == "DAT"


# === Bare DAT-cleft regression =======================================


class TestBareDatCleftPreserved:
    """The Phase 5i C9 (b) bare DAT-cleft (``Kanino ang aklat?``)
    fires unchanged. The 3-daughter rule doesn't shadow it
    because the daughter counts differ."""

    def test_bare_kanino_cleft_unique(self) -> None:
        parses = parse_text("Kanino ang aklat?")
        # The bare cleft produces a single parse with no POSS slot
        # and no N_LEMMA on matrix (the 2-daughter shape).
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "WH <SUBJ>"
        assert fs.feats.get("WH_LEMMA") == "kanino"
        assert fs.feats.get("POSS") is None
        assert fs.feats.get("N_LEMMA") is None


# === Wh-fronting coexistence =========================================


class TestWhFrontingCoexists:
    """The existing Phase 5i C9 wh-fronting rule
    (``PRON[WH=YES, CASE=DAT] S``) also fires on these surfaces
    (the inner ``kaibigan ito`` parses as an S via C2 predicative-
    N). Both rules produce a parse — the new C15 rule with POSS
    slot, and the wh-fronting rule with kanino in ADJUNCT."""

    def test_two_parses_coexist(self) -> None:
        parses = parse_text("Kanino kaibigan ito?")
        assert len(parses) == 2
        # One parse has POSS, one has ADJUNCT.
        with_poss = [p for p in parses if p[1].feats.get("POSS")]
        with_adj_only = [
            p for p in parses
            if not p[1].feats.get("POSS")
            and p[1].feats.get("ADJUNCT")
        ]
        assert len(with_poss) == 1
        assert len(with_adj_only) == 1
