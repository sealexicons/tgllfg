# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 9.Q: locative cleft + NEG'd cleft + sentence-medial kundi-PP
correction (B3.D).

Closes two Phase 8 pins:

* **8.S** ``Sa bahay ang lapis.`` / ``Sa mesa ang aklat.``
  ("The pencil is at home." / "The book is on the table.") —
  locative cleft with NOUN-headed DAT-NP, deliberately blocked
  by the 8.S DAT-PRON-pivot rule's ``¬ (↓1 PRED)`` gate.

* **8.T** ``Hindi dito kundi sa bayan ang pulong.`` (S&O 1972
  p.656 / sent-1289) — sentence-medial kundi-PP correction
  inside a NEG'd locative cleft.

S&O 1972 §4.2 / R&G 1981 §10.5 — the locative-cleft construction
class. A DAT-marked NP (the ground / location) serves as a
copular locative predicate; the NOM-pivot is the figure being
located.

Rule shape (cfg/clause.py, two rules):

1. **Simple locative cleft**:

   ``S → NP[CASE=DAT] NP[CASE=NOM]``
       ``(↑ PRED) = 'BE-LOC <SUBJ>'``
       ``(↑ SUBJ) = ↓2``  (figure)
       ``(↑ LOC) = ↓1``   (ground)
       ``(↑ PREDICATIVE) = true``
       ``(↑ CLAUSE_TYPE) = 'LOCATIVE_CLEFT'``
       ``(↓1 PRED)``        (NOUN-headed or DEM-headed DAT-NP)
       ``¬ (↓1 WH)``

2. **NEG'd cleft + sentence-medial kundi-PP correction**
   (8.T pin):

   ``S → PART[NEG] NP[CASE=DAT] PART[COORD=BUT_NOT]
           NP[CASE=DAT] NP[CASE=NOM]``
       ``(↑ PRED) = 'BE-LOC <SUBJ>'``
       ``(↑ SUBJ) = ↓5``
       ``(↑ LOC) = ↓4``       (corrective PP — actual location)
       ``(↑ POLARITY) = 'NEG'``
       ``↓2 ∈ (↑ ADJUNCT)``    (negated alternative)
       ``(↓2 ROLE) = 'NEG_CORRECTION'``

The 8.S DAT-PRON cleft (PRED='BE-DAT <SUBJ>') and the 9.Q
locative cleft (PRED='BE-LOC <SUBJ>') partition the
NP[CASE=DAT] daughter space cleanly:

* 8.S admits ``Sa akin``/``Akin`` (PRON-headed; no NP-level PRED)
* 9.Q admits ``Sa bahay``/``dito`` (NOUN- or DEM-headed; has PRED)
"""

import pytest


# -----------------------------------------------------------
# Class A: 8.S pin closure (basic locative cleft)
# -----------------------------------------------------------

class TestPhase8sPinClosure:
    """The 8.S `Sa <place> ang <NP>` pin sentences now parse
    via the 9.Q locative-cleft rule with PRED='BE-LOC <SUBJ>'."""

    @pytest.mark.parametrize("sentence", [
        "Sa bahay ang lapis.",
        "Sa mesa ang aklat.",
        "Sa kotse ang aklat.",
        "Sa bata ang aklat.",
        "Sa Nanay ang relos.",
    ])
    def test_locative_cleft_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"no parse: {sentence!r}"
        for _ct, f, *_ in parses:
            assert str(f.feats.get("PRED")) == "BE-LOC <SUBJ>", (
                f"expected BE-LOC PRED; got "
                f"{f.feats.get('PRED')!r} for {sentence!r}"
            )


# -----------------------------------------------------------
# Class B: temporal cleft (Sa + day-of-week / time)
# -----------------------------------------------------------

class TestTemporalCleft:
    """``Sa Sabado ang aklat.`` / ``Sa Linggo ang aklat.`` —
    same construction with a temporal-N as ground. PRED is
    still BE-LOC (covers both spatial and temporal location)."""

    @pytest.mark.parametrize("sentence", [
        "Sa Sabado ang aklat.",
        "Sa Linggo ang aklat.",
    ])
    def test_temporal_cleft(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"no parse: {sentence!r}"


# -----------------------------------------------------------
# Class C: multi-token DAT-NP cleft (with GEN-NP possessor)
# -----------------------------------------------------------

class TestMultiTokenDatCleft:
    """``Sa tabi ng bahay ang lapis.`` — the locative ground is
    a complex DAT-NP with a GEN-NP possessor. The 9.Q rule
    composes with the Phase 4 §7.8 NP-possessive rule."""

    @pytest.mark.parametrize("sentence", [
        "Sa tabi ng bahay ang lapis.",
        "Sa ilalim ng mesa ang lapis.",
    ])
    def test_multi_token_dat_ground(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"no parse: {sentence!r}"


# -----------------------------------------------------------
# Class D: DEM-loc cleft (dito/diyan/doon)
# -----------------------------------------------------------

class TestDemLocCleft:
    """The DEM-locative ``dito`` / ``diyan`` / ``doon`` is
    NP[CASE=DAT] with PRED='PRO', so the 9.Q (↓1 PRED) gate
    admits them. ``Dito ang aklat.`` — "The book is here.\""""

    @pytest.mark.parametrize("sentence", [
        "Dito ang aklat.",
        "Diyan ang aklat.",
        "Doon ang aklat.",
    ])
    def test_dem_loc_cleft(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"no parse: {sentence!r}"


# -----------------------------------------------------------
# Class E: NEG-wrap composition
# -----------------------------------------------------------

class TestNegWrapComposition:
    """``Hindi sa bahay ang lapis.`` — NEG-wrap on the locative
    cleft. Falls out of the existing
    ``S → PART[POLARITY=NEG] S`` rule applying to 9.Q's cleft."""

    @pytest.mark.parametrize("sentence", [
        "Hindi sa bahay ang lapis.",
        "Hindi sa mesa ang aklat.",
        "Hindi dito ang aklat.",
    ])
    def test_neg_locative_cleft(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"no parse: {sentence!r}"
        for _ct, f, *_ in parses:
            assert str(f.feats.get("POLARITY")) == "NEG", (
                f"expected POLARITY=NEG; got "
                f"{f.feats.get('POLARITY')!r} for {sentence!r}"
            )


# -----------------------------------------------------------
# Class F: 8.T pin — NEG cleft + sentence-medial kundi-PP
# -----------------------------------------------------------

class TestPhase8tPinClosure:
    """The 8.T pin ``Hindi dito kundi sa bayan ang pulong.``
    (S&O 1972 p.656 / sent-1289) parses post-9.Q via the
    dedicated 5-daughter rule. The corrective PP ``sa bayan``
    is the actual location (LOC); the negated alternative
    ``dito`` rides on ADJUNCT with ROLE='NEG_CORRECTION'."""

    def test_8t_pin_parses(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Hindi dito kundi sa bayan ang pulong.", n_best=2,
        )
        assert len(parses) >= 1, "8.T pin should parse post-9.Q"
        # Verify f-structure shape
        _ct, f, *_ = parses[0]
        assert str(f.feats.get("PRED")) == "BE-LOC <SUBJ>"
        assert str(f.feats.get("POLARITY")) == "NEG"
        assert str(f.feats.get("CLAUSE_TYPE")) == "LOCATIVE_CLEFT"

    @pytest.mark.parametrize("sentence", [
        # Variants with lex'd nouns
        "Hindi dito kundi sa bahay ang aklat.",
        "Hindi sa mesa kundi sa silya ang aklat.",
    ])
    def test_neg_correction_variants(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"no parse: {sentence!r}"


# -----------------------------------------------------------
# Class G: f-structure shape
# -----------------------------------------------------------

class TestLocativeCleftFstruct:
    """The locative cleft's f-structure has SUBJ (figure),
    LOC (ground), PRED='BE-LOC <SUBJ>', and
    CLAUSE_TYPE='LOCATIVE_CLEFT'."""

    def test_simple_cleft_fstruct(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Sa bahay ang lapis.", n_best=2)
        assert len(parses) >= 1
        _ct, f, *_ = parses[0]
        assert str(f.feats.get("PRED")) == "BE-LOC <SUBJ>"
        assert str(f.feats.get("CLAUSE_TYPE")) == "LOCATIVE_CLEFT"
        subj = f.feats.get("SUBJ")
        assert subj is not None, "no SUBJ"
        assert subj.feats.get("LEMMA") == "lapis"
        loc = f.feats.get("LOC")
        assert loc is not None, "no LOC"
        assert loc.feats.get("LEMMA") == "bahay"

    def test_kundi_correction_fstruct(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Hindi dito kundi sa bahay ang aklat.", n_best=2,
        )
        assert len(parses) >= 1
        _ct, f, *_ = parses[0]
        # The corrected (right-side) PP is the actual LOC
        loc = f.feats.get("LOC")
        assert loc is not None
        assert loc.feats.get("LEMMA") == "bahay"
        # The negated PP (`dito`) is in ADJUNCT with ROLE
        adjunct = f.feats.get("ADJUNCT")
        assert adjunct is not None
        members = list(adjunct)
        roles = {m.feats.get("ROLE") for m in members}
        assert "NEG_CORRECTION" in roles, (
            f"NEG_CORRECTION not in ADJUNCT roles; got {roles!r}"
        )


# -----------------------------------------------------------
# Class H: regressions / scope guards
# -----------------------------------------------------------

class TestRuleScopeGuards:
    """Baseline parses retained; the 9.Q rule doesn't shadow
    pre-existing locative / cleft constructions."""

    @pytest.mark.parametrize("sentence,expected_pred", [
        # 8.S DAT-PRON cleft retained — PRED='BE-DAT <SUBJ>'
        ("Sa akin ang lapis.", "BE-DAT <SUBJ>"),
        # nasa-locative-existential retained — PRED='LOC <SUBJ>'
        ("Nasa bahay ang lapis.", "LOC <SUBJ>"),
    ])
    def test_existing_locatives_retain_pred(
        self, sentence: str, expected_pred: str
    ) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1
        preds = {str(f.feats.get("PRED")) for _ct, f, *_ in parses}
        assert expected_pred in preds, (
            f"expected {expected_pred!r} in {preds!r} for {sentence!r}"
        )

    @pytest.mark.parametrize("sentence", [
        # Verb-headed clauses unaffected
        "Bumili si Maria ng aklat.",
        "Kumain ang bata.",
        # Predicative-N retained
        "Aklat ito.",
        "Iyon ang aklat.",
        # Wh-cleft retained
        "Sa kanino ang aklat?",
    ])
    def test_baseline_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"baseline regression: {sentence!r}"


# -----------------------------------------------------------
# Class I: out-of-scope (deferred to follow-on sub-PRs)
# -----------------------------------------------------------

class TestPhase9qOutOfScope:
    """Construction-class variants NOT closed by 9.Q. Pin each;
    flip when the relevant follow-on sub-PR closes it."""

    def test_sa_fronted_ay_cleft_now_parses(self) -> None:
        """``Sa tag-init ay manaka-naka lamang ang ulan.`` —
        Sa-fronted temporal adverbial + ay-fronted ADV-pred.
        Closed by 9.X.c10 (``S → NP[CASE=DAT] PART[LINK=AY] S``)
        composed with the 9.X.c7 ADV-predicate rule and the
        9.X.c3 X-Y reduplication tokenizer rejoin
        (``manaka-naka`` → ``manakanaka``).

        Pin: ``== 1`` (was ``== 2``). The 9.X.c8 NP-internal sa-PP
        modifier reading and the canonical topic-adjunct reading are a
        *c-structure* attachment ambiguity that neutralizes in the
        f-structure — ``sa tag-init`` lands in the matrix ``ADJ`` set
        either way, so the two parses carry identical f-structures. The
        Phase 14.final.post-12 solve-path f-structure dedup collapses
        them to one."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Sa tag-init ay manaka-naka lamang ang ulan.", n_best=5,
        )
        assert len(parses) == 1, (
            f"expected 1 parse (the topic-adjunct + NP-internal sa-PP "
            f"c-structure ambiguity neutralizes in f-structure); "
            f"got {len(parses)}"
        )

    def test_sa_wh_cleft(self) -> None:
        """``Sa anong paraan ...`` — Sa-fronted wh-PP cleft. Phase
        5i wh-cleft family doesn't cover Sa+wh-NP-fronted shape.
        Distinct from the simple locative cleft; defer."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Sa anong paraan kapareho ng Smith ang Santos?", n_best=2,
        )
        assert len(parses) == 0, (
            "Sa-wh-cleft may have closed; review and flip."
        )
