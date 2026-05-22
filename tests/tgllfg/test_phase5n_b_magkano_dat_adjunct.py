# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.B Commit 14: Magkano cleft with trailing DAT-NP ADJUNCT
(§18 L58).

Closes §18.1 deferral L58 by extending the Phase 5i Commit 9 (a)
predicative-Q cleft to admit a trailing DAT-NP as ADJUNCT:

    Magkano ito sa kanya?           "How much is it for him?"
    Magkano ang aklat sa palengke?  "How much is the book at the market?"
    Magkano ang isda sa bata?       "How much is the fish for the child?"

Two grammar additions:

  (1) ``cfg/clause.py``: new sibling rule
      ``S → Q[WH=YES] NP[CASE=NOM] NP[CASE=DAT]`` that adds the
      DAT-NP to the matrix's ADJUNCT set
      (``↓3 ∈ (↑ ADJUNCT)``). Same f-structure shape as Phase 5i
      C9 (a) — PRED='WH <SUBJ>', Q_TYPE=WH, WH_LEMMA from the Q.

  (2) ``cfg/nominal.py``: new sibling shell rule
      ``NP[CASE=DAT] → ADP[CASE=DAT] PRON[CASE=DAT]`` (with
      ``¬ (↓2 WH)``). Required because the canonical target
      ``Magkano ito sa kanya?`` couldn't otherwise parse: the
      bare DAT-PRON (kanya) is itself an NP[CASE=DAT], but the
      explicit-DAT-marker form (``sa kanya``) had no shell rule
      — only Phase 5i C3's wh-PRON shell existed. The new rule
      generalises the explicit-DAT form to non-wh PRONs.

Although Magkano is the primary motivation, the cleft+ADJUNCT
rule generalises to any Q[WH=YES] head. Test coverage covers
Magkano + variants and a small Ilan check.
"""

import pytest

from tgllfg.core.pipeline import parse_text


def _wh_parse(text: str):
    """Return the parse with PRED='WH <SUBJ>' and an ADJUNCT set,
    or None if no such parse exists."""
    parses = parse_text(text, n_best=10)
    for p in parses:
        if p[1].feats.get("PRED") == "WH <SUBJ>" and p[1].feats.get("ADJUNCT"):
            return p
    return None


# === Magkano + DAT-NP ADJUNCT ========================================


class TestMagkanoDatAdjunct:
    """The canonical target: Magkano + NOM-NP + DAT-NP."""

    @pytest.mark.parametrize("sentence", [
        "Magkano ito sa kanya?",
        "Magkano ang aklat sa palengke?",
        "Magkano ang isda sa palengke?",
        "Magkano ang aklat sa bata?",
        "Magkano ang aklat sa kanya?",
    ])
    def test_magkano_with_trailing_dat_np(self, sentence: str) -> None:
        result = _wh_parse(sentence)
        assert result is not None, (
            f"{sentence!r} did not produce a wh-cleft parse with "
            f"a DAT-NP ADJUNCT"
        )
        _ct, fs, _astr, _diags = result
        assert fs.feats.get("WH_LEMMA") == "magkano"
        assert fs.feats.get("Q_TYPE") == "WH"
        adjuncts = fs.feats.get("ADJUNCT")
        assert adjuncts is not None
        assert len(adjuncts) == 1
        # The ADJUNCT carries CASE=DAT (the trailing DAT-NP).
        adj = next(iter(adjuncts))
        assert adj.feats.get("CASE") == "DAT"


# === Generalises to other wh-Q heads =================================


class TestIlanDatAdjunct:
    """The cleft+ADJUNCT rule is keyed on ``Q[WH=YES]`` so it
    fires on any wh-Q, not just magkano. Validate with ilan."""

    def test_ilan_with_trailing_dat_np(self) -> None:
        result = _wh_parse("Ilan ang aklat sa palengke?")
        assert result is not None
        _ct, fs, _astr, _diags = result
        assert fs.feats.get("WH_LEMMA") == "ilan"
        adjuncts = fs.feats.get("ADJUNCT")
        assert adjuncts is not None
        assert len(adjuncts) == 1


# === sa + non-wh DAT-PRON shell ======================================


class TestSaDatPronShell:
    """The new ``NP[CASE=DAT] → ADP[CASE=DAT] PRON[CASE=DAT]``
    shell makes ``sa kanya`` (and kin) parse as a DAT-NP. Test
    standalone usage (V + DAT-OBLIQUE) so the shell's contribution
    is visible separately from the cleft+ADJUNCT rule."""

    @pytest.mark.parametrize("sentence", [
        "Bumili ako sa kanya.",
        "Bumili ako sa atin.",
    ])
    def test_v_plus_sa_pron(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === Phase 5i C9 (a) regression =======================================


class TestPhase5iC9aPreserved:
    """The original Phase 5i C9 (a) rule (Q[WH=YES] NOM-NP, no
    trailing DAT-NP) continues to fire unchanged."""

    @pytest.mark.parametrize("sentence,wh_lemma", [
        ("Magkano ang isda?",   "magkano"),
        ("Magkano ang aklat?",  "magkano"),
        ("Ilan ang aklat?",     "ilan"),
    ])
    def test_bare_q_cleft_unchanged(
        self, sentence: str, wh_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        # Find the wh-cleft parse (PRED='WH <SUBJ>' with no
        # ADJUNCT — the original 2-daughter rule).
        good = [
            p for p in parses
            if p[1].feats.get("PRED") == "WH <SUBJ>"
            and p[1].feats.get("WH_LEMMA") == wh_lemma
            and not p[1].feats.get("ADJUNCT")
        ]
        assert len(good) >= 1
