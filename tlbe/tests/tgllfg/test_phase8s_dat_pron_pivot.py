# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 8.S: DAT-PRON possessive-pivot cleft.

Audit-named construction (S&O 1972 §4.2 / R&G 1981 §10). A bare
DAT-PRON or sa+DAT-PRON serves as the possessive predicate; the
ang-NP is the NOM-pivot SUBJ (the possessed item):

    Akin ang tinapay.    "The bread is mine."
    Sa akin ang lapis.   "The pencil is mine." (sa-PP variant)
    Iyo ang aklat.       "The book is yours."
    Kanila ang bahay.    "The house is theirs."

Phase 8.X (PR #60) docstring explicitly named this remaining 8.S
residual after closing the noun-pivot subset (``Ako ang guro.``).

New rule in ``cfg/clause.py`` adjacent to the Phase 8.X non-wh
PRON-pivot rule:

    S → NP[CASE=DAT]  NP[CASE=NOM]
      (↑ PRED)        = 'BE-DAT <SUBJ>'
      (↑ SUBJ)        = ↓2
      (↑ POSSESSOR)   = ↓1
      (↑ PREDICATIVE) = true
      ¬ (↓1 PRED)                      (NOUN-headed DAT excluded)
      ¬ (↓1 WH)                        (wh-DAT-PRON excluded)

The ``¬ (↓1 PRED)`` gate distinguishes PRON-headed DAT-NPs
(which lack PRED at the NP[DAT] level) from NOUN-headed DAT-NPs
(which carry ``PRED='NOUN(↑ FORM)'``). This keeps the locative
reading ``Sa bahay ang lapis.`` outside 8.S scope — it needs a
separate locative-cleft rule.

The ``¬ (↓1 WH)`` gate excludes wh-DAT-PRONs (``kanino``,
``saan``), which route through the Phase 5i wh-cleft rules.

Lex addition: ``relos`` NOUN (Spanish loan; S&O 1972 page 284
sent-397 audit hit ``Akin ang relos.``).
"""

import pytest


class TestPhase8sDatPronPivot:
    """``DAT-PRON ang NP`` and ``Sa DAT-PRON ang NP``."""

    @pytest.mark.parametrize("sentence,subj_lemma", [
        # S&O 1972 audit hits
        ("Akin ang tinapay.", "tinapay"),
        ("Akin ang lapis.", "lapis"),
        ("Akin ang relos.", "relos"),
        # R&G Intermediate audit hits
        ("Akin ang bahay.", "bahay"),
        ("Akin ang bulaklak.", "bulaklak"),
        # sa-PP variant (S&O 1972 page 145 sent-168)
        ("Sa akin ang lapis.", "lapis"),
        # Other DAT-PRONs
        ("Iyo ang aklat.", "aklat"),
        ("Sa iyo ang aklat.", "aklat"),
        ("Kanila ang bahay.", "bahay"),
        ("Sa kanila ang bahay.", "bahay"),
    ])
    def test_dat_pron_pivot_parses(
        self, sentence: str, subj_lemma: str,
    ) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse for {sentence!r}"
        f = parses[0][1]
        assert str(f.feats.get("PRED")) == "BE-DAT <SUBJ>"
        subj = f.feats.get("SUBJ")
        assert subj is not None
        assert str(subj.feats.get("LEMMA")) == subj_lemma
        possessor = f.feats.get("POSSESSOR")
        assert possessor is not None
        assert str(possessor.feats.get("CASE")) == "DAT"


class TestPhase8sLocativeNotViaDatPronCleft:
    """The 8.S DAT-PRON-pivot rule's ``¬ (↓1 PRED)`` gate keeps
    NOUN-headed DAT-NPs out — ``Sa bahay ang lapis.`` does NOT
    fire 8.S's ``BE-DAT <SUBJ>`` analysis. Phase 9.Q B3.D adds
    the locative-cleft rule (with PRED ``BE-LOC <SUBJ>``) for
    NOUN-headed DAT-NPs; the 8.S gate remains correct — the
    8.S and 9.Q rules partition the NP[CASE=DAT] daughter
    space cleanly (8.S: ``¬ (↓1 PRED)`` admits PRON only;
    9.Q: ``(↓1 PRED)`` admits NOUN/DEM only)."""

    @pytest.mark.parametrize("sentence", [
        "Sa bahay ang lapis.",
        "Sa mesa ang aklat.",
    ])
    def test_locative_cleft_via_9q_not_8s(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        # Locative-cleft now parses post-9.Q with BE-LOC PRED;
        # the 8.S DAT-PRON rule must NOT fire on these (its
        # BE-DAT PRED would mean a possessive cleft, semantically
        # wrong here — that's the 8.S/9.Q partition).
        assert len(parses) >= 1, (
            f"locative cleft should parse post-9.Q: {sentence!r}"
        )
        for _ct, f, _astr, _diags in parses:
            assert str(f.feats.get("PRED")) != "BE-DAT <SUBJ>", (
                f"locative cleft {sentence!r} fired the DAT-PRON "
                "rule — 8.S/9.Q gate-partition failed"
            )


class TestPhase8sWhDatBlocked:
    """The ``¬ (↓1 WH)`` gate prevents double-firing on
    wh-DAT-PRON clefts (``Sa kanino ang aklat?``) which already
    route through the Phase 5i wh-cleft rules."""

    def test_wh_cleft_unaffected(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Sa kanino ang aklat?", n_best=3)
        assert len(parses) >= 1
        # The wh-cleft route does NOT produce a BE-DAT predicate
        # (Phase 5i uses a wh-specific cleft PRED).
        for _ct, f, _astr, _diags in parses:
            assert str(f.feats.get("PRED")) != "BE-DAT <SUBJ>", (
                "wh-DAT-PRON cleft fired the non-wh DAT-PRON rule "
                "— ¬ (↓1 WH) gating failed"
            )


class TestPhase8sRegressions:
    """Phase 8.X PRON-pivot + DEM-pivot + Phase 5j C4 locative
    existential parses remain unaffected by the new rule."""

    @pytest.mark.parametrize("sentence", [
        # Phase 8.X non-wh PRON-pivot
        "Ako ang guro.",
        # Phase 8.X DEM-pivot
        "Ito ang aklat.",
        # Phase 5j C4 nasa-locative-existential
        "Nasa bahay ang lapis.",
        # Phase 8.X V-headed pivot (was named for 8.S but
        # already covered)
        "Tayo ang lumakad.",
        "Tayo ang kakain.",
    ])
    def test_regression_parses_hold(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"regression on {sentence!r}"
