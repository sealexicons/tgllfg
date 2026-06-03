# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.X.pre-1: lex/morph prereqs for PAMILYA/sent-8.

Two prereq fixes shipped together as one sub-PR:

1. **``also_medial_vowel_syncope`` sandhi flag** — variant-generation
   flag on the analyzer that emits BOTH the no-syncope variant AND
   the syncope variant for vowel-initial suffix cells. Parallel to
   ``also_n_epenthesis`` (Phase 10.J.post-7.4). Opt-in on ``bigay``
   produces both ``binigayan`` (formal) and ``binigyan`` (modern
   principal per Zamar 2023 §13.4). Closes the DV-with-syncope
   sub-blocker of PAMILYA/sent-8's second V-conjunct ``bigyan ng
   matitirhan ang mga miyembro``.

2. **CAUSE-STUDY lex entry for ``aral``** — parallel to existing
   ``CAUSE-EAT`` (kain) and ``CAUSE-READ`` (basa) in
   ``data/tgl/lexicon/causative.yaml``. The 2-arg OV shape with
   CAUSER pivot → OBJ-CAUSER and CAUSEE → SUBJ. Closes the third
   V-conjunct's lex blocker ``pag-aralin ang mga miyembro`` (the
   ``pag_in`` paradigm cell on ``aral`` shipped in Phase 10.J.post-
   12.11; this commit completes it with the CAUS=DIRECT PRED
   template).

Net audit-corpus delta from this sub-PR: **+5 closures across
waves 2/3/4/5** (all ``bigyan`` / ``binigyan`` syncope-form
``give``-sentences). The CAUSE-STUDY entry has no direct audit-
corpus closure today (it's the prereq for the eventual
PAMILYA/sent-8 closure under 10.X proper's V-V-V gapping coord).

PAMILYA/sent-8 itself remains pinned to 10.X proper — the third
remaining blocker is the shared-NOM V-V-V gapping coord at the
S_XCOMP body level with per-V REL-PRO routing.
"""

import pytest

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import analyze_tokens
from tgllfg.text.tokenizer import tokenize


# === C1: also_medial_vowel_syncope sandhi flag ===========================

class TestBigayMedialVowelSyncope:
    """Phase 10.X.pre-1 C1: ``bigay`` opted into
    ``also_medial_vowel_syncope`` produces both the no-syncope
    variant (``binigayan``, formal) and the syncope variant
    (``binigyan``, modern principal) across the -an paradigm cells."""

    @pytest.mark.parametrize("surface", [
        "binigayan",   # PFV DV no-syncope (pre-10.X.pre-1)
        "binigyan",    # PFV DV with syncope (NEW)
        "bibigayan",   # CTPL DV no-syncope (pre-10.X.pre-1)
        "bibigyan",    # CTPL DV with syncope (NEW)
        "bigyan",      # bare INF / CTPL-SOC with syncope (NEW)
    ])
    def test_bigay_dv_an_surface_analyzes(self, surface: str) -> None:
        """Each surface analyzes to ``bigay`` as a VERB."""
        toks = tokenize(surface)
        analyses_lists = analyze_tokens(toks)
        assert analyses_lists and analyses_lists[0], (
            f"{surface!r} should analyze to a VERB form"
        )
        verb_analyses = [
            a for a in analyses_lists[0]
            if a.pos == "VERB" and a.lemma == "bigay"
        ]
        assert verb_analyses, (
            f"{surface!r} should have a bigay VERB analysis; "
            f"got: {analyses_lists[0]}"
        )


# === Bonus closures from C1 (5 audit-corpus sentences) ====================

class TestBigayBonusClosures:
    """5 audit-corpus sentences across waves 2/3/4/5 close as
    bonus from the ``also_medial_vowel_syncope`` flag — all use
    syncope-form ``give`` constructions that didn't analyze pre-
    10.X.pre-1."""

    @pytest.mark.parametrize("sent", [
        # wave2-rg-intermediate page-84/prose/sent-579
        "Bigyan mo nga kami ng pansit at litson.",
        # wave3-so1972 page-220/sent-257
        "Bigyan mo kami ng tigalawang lapis.",
        # wave4-kroeger1991 page-93/ex-30b
        "Bigyan mo siya ng kape.",
        # wave4-kroeger1991 page-217/ex-5a
        "Sino ang binigyan mo ng pera?",
        # wave5-zamar2023 page-29/sent-15
        "Binigyan nila kami ng pera.",
    ])
    def test_bigay_syncope_sentence_parses(self, sent: str) -> None:
        parses = parse_text(sent, n_best=2)
        assert len(parses) >= 1, (
            f"syncope-form give-sentence should parse: {sent!r}; "
            f"got {len(parses)} parses"
        )


# === C2: CAUSE-STUDY lex entry for aral ===================================

class TestAralCauseStudy:
    """Phase 10.X.pre-1 C2: ``aral``'s 2-arg OV CAUSE-STUDY lex
    entry (parallel to ``kain`` CAUSE-EAT) lets ``pag-aralin`` /
    ``pagaralin`` parse as a causative under control verbs.

    The standalone imperative ``Pag-aralin ang X.`` (no matrix
    control) does NOT close with just C2 — that path needs an
    imperative chart rule that fires on OV CAUS=DIRECT (separate
    work, not in 10.X.pre-1 scope).
    """

    @pytest.mark.parametrize("sent", [
        # Under N-pred control (Tungkulin niyang ...)
        "Tungkulin niyang pag-aralin ang mga bata.",
        "Tungkulin niyang pagaralin ang mga bata.",
        # Under PSYCH control (Gusto niyang ...)
        "Gusto niyang pag-aralin ang mga bata.",
        # With a NOM-NP with PP-modifier (sent-8 sub-shape)
        "Tungkulin niyang pag-aralin ang mga miyembro ng kanyang pamilya.",
    ])
    def test_pag_aralin_under_control(self, sent: str) -> None:
        parses = parse_text(sent, n_best=2)
        assert len(parses) >= 1, (
            f"pag-aralin causative under control should parse: "
            f"{sent!r}; got {len(parses)} parses"
        )

    def test_pag_aralin_pred_is_cause_study(self) -> None:
        """Confirm the PRED template is CAUSE-STUDY, not the base
        ARAL — the C2 lex entry has CAUS=DIRECT and the matching
        causative PRED template."""
        sent = "Tungkulin niyang pag-aralin ang mga bata."
        parses = parse_text(sent, n_best=2)
        assert parses
        _ctree, fs, _astr, _diags = parses[0]
        xcomp = fs.feats.get("XCOMP")
        assert xcomp is not None
        xcomp_pred = xcomp.feats.get("PRED")
        assert xcomp_pred == "CAUSE-STUDY <SUBJ, OBJ-CAUSER>", (
            f"expected CAUSE-STUDY <SUBJ, OBJ-CAUSER>; got "
            f"{xcomp_pred!r}"
        )


# === Integration: PAMILYA/sent-8 sub-strings ==============================

class TestPamilyaSent8SubStrings:
    """Phase 10.X.pre-1 enables the first two V-conjuncts of
    PAMILYA/sent-8 (``pakainin`` was already working pre-10.X.pre-1;
    ``bigyan ng matitirhan`` works post-C1; ``pag-aralin`` works
    post-C2). The full sentence with all three V-conjuncts joined
    by gapping coord still requires 10.X proper's structural fix."""

    @pytest.mark.parametrize("sent", [
        # First conjunct (was already working)
        "Tungkulin niyang pakainin ang mga miyembro.",
        # Second conjunct (NEW — needs C1's syncope variant)
        "Tungkulin niyang bigyan ng matitirhan ang mga miyembro.",
        # Third conjunct (NEW — needs C2's CAUSE-STUDY)
        "Tungkulin niyang pag-aralin ang mga miyembro.",
        # With ay-fronted SOURCE PP head (sent-8 shape)
        (
            "Sa kabilang dako ay tungkulin niyang pakainin ang mga "
            "miyembro ng kanyang pamilya."
        ),
    ])
    def test_sent_8_subconjunct_parses(self, sent: str) -> None:
        parses = parse_text(sent, n_best=2)
        assert len(parses) >= 1, (
            f"sent-8 sub-conjunct should parse: {sent!r}; "
            f"got {len(parses)} parses"
        )
