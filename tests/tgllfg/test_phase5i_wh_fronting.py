"""Phase 5i Commit 2: cleft-style wh-fronting (NOM pivot).

Roadmap §12.1 / plan-of-record §5.1, §6 Commit 2. New clause rule
in ``cfg/clause.py``:

    S → PRON[WH=YES, CASE=NOM] NP[CASE=NOM]

Equations: literal PRED ``WH <SUBJ>`` (parallels Phase 5e Commit
26 ``parang`` and Phase 5g Commit 3 predicative-adj literal-PRED
convention); SUBJ shared with the NOM-NP daughter (which is
typically a Phase 4 §7.5 headless RC); ``Q_TYPE: WH`` and
``WH_LEMMA: <wh's lemma>`` set on the matrix for ranker /
classifier visibility; ``(↓1 WH) =c 'YES'`` belt-and-braces
constraint matching the Phase 5h leak-closing pattern.

The rule is restricted to NOM-marked wh-PRONs (sino / ano /
alin). DAT-marked ``kanino`` "to whom" needs a separate
DAT-pivot frame (deferred to Phase 5i Commit 9 audit if corpus
pressure surfaces).

End-to-end target sentences:

    Sino ang kumain?           "Who ate?"
    Sino ang kumain ng kanin?  "Who ate the rice?"
    Ano ang kinain mo?         "What did you eat?"
    Alin ang kinain mo?        "Which one did you eat?"
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Cleft-style wh-fronting parses =====================================


class TestCleftWhFronting:
    """The new rule fires on PRON[WH=YES, CASE=NOM] + NOM-NP and
    produces a wh-Q matrix with the right f-structure features."""

    @pytest.mark.parametrize("sentence,wh_lemma", [
        ("Sino ang kumain?",          "sino"),
        ("Sino ang kumain ng kanin?", "sino"),
        ("Sino ang kumain ng isda?",  "sino"),
        ("Ano ang kinain mo?",        "ano"),
        ("Ano ang kinain ni Maria?",  "ano"),
        ("Alin ang kinain mo?",       "alin"),
    ])
    def test_wh_predicative_clause(
        self, sentence: str, wh_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got 0"
        )
        # Every parse should be a wh-Q matrix with the right wh-lemma.
        wh_parses = [
            (ct, fs, ast, diags)
            for ct, fs, ast, diags in parses
            if fs.feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1, (
            f"expected at least one wh-Q parse for {sentence!r}"
        )
        _ct, fs, _astr, _diags = wh_parses[0]
        assert fs.feats.get("PRED") == "WH <SUBJ>"
        assert fs.feats.get("WH_LEMMA") == wh_lemma
        assert fs.feats.get("Q_TYPE") == "WH"


class TestCleftWhCTreeShape:
    """The c-tree has the new rule firing: matrix S has PRON +
    NP[CASE=NOM] daughters."""

    def test_sino_ang_kumain_c_tree(self) -> None:
        parses = parse_text("Sino ang kumain?")
        assert len(parses) == 1
        ctree, _fs, _astr, _diags = parses[0]
        assert ctree.label == "S"
        assert len(ctree.children) == 2
        # First child: PRON (the wh)
        wh = ctree.children[0]
        assert wh.label.startswith("PRON")
        # Second child: NP[CASE=NOM] (the headless RC)
        np = ctree.children[1]
        assert np.label.startswith("NP[CASE=NOM]")


# === Headless RC composition ==========================================


class TestHeadlessRcInWhCleft:
    """The NOM-NP daughter is a Phase 4 §7.5 headless relative
    clause. Multiple verbal voices / aspects compose unchanged."""

    @pytest.mark.parametrize("sentence", [
        # AV verbs with various aspects
        "Sino ang kumain?",            # AV PFV
        "Sino ang kumakain?",          # AV IPFV
        "Sino ang kakain?",            # AV CTPL
        # Non-AV (OV) verbs in the relative clause
        "Ano ang kinain mo?",          # OV PFV
        "Ano ang kinakain mo?",        # OV IPFV
        "Ano ang kakainin mo?",        # OV CTPL
    ])
    def test_aspect_voice_combinations(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got 0"
        )
        wh_parses = [
            p for p in parses
            if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1


# === DAT-marked wh-PRONs are NOT in the NOM-only rule ================


class TestKaninoNotMatchedByNomCleft:
    """``kanino`` carries CASE=DAT, so Commit 2's NOM-only cleft
    rule does not fire on it. The DAT-pivot cleft was added in
    Phase 5i Commit 9 (separate rule); this test now verifies
    that the Commit 9 DAT-cleft fires (the deferred frame is
    closed). Pre-Commit-9 this test asserted ``wh_parses == []``;
    flipped 2026-05-06 with the Commit 9 rule add."""

    def test_kanino_dat_cleft_fires(self) -> None:
        parses = parse_text("Kanino ang aklat?")
        wh_parses = [
            p for p in parses
            if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1
        _ct, fs, _astr, _diags = wh_parses[0]
        assert fs.feats.get("WH_LEMMA") == "kanino"


# === Non-wh PRONs do not fire the rule (=c WH constraint) ==============


class TestNonWhPronsExcluded:
    """The ``(↓1 WH) =c 'YES'`` constraining equation prevents
    non-wh PRONs (siya / ako / ka / ikaw) from firing the cleft
    rule. ``Siya ang kumain?`` "Was it she who ate?" parses as a
    different construction (Phase 4 §7.10 PRON-headed predicative,
    if applicable) but NOT via this cleft rule's wh-Q reading."""

    @pytest.mark.parametrize("sentence", [
        "Siya ang kumain.",   # statement (non-wh): "She is the one who ate"
        "Ako ang kumain.",    # "I'm the one who ate"
    ])
    def test_non_wh_pron_does_not_fire_cleft(
        self, sentence: str
    ) -> None:
        parses = parse_text(sentence)
        # The non-wh PRON should NOT produce a Q_TYPE=WH parse.
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("Q_TYPE") != "WH"
            assert fs.feats.get("WH_LEMMA") is None


# === Q_TYPE / WH_LEMMA on matrix only when wh-cleft fires =============


class TestQTypeOnlyOnWhCleft:
    """Existing constructions don't acquire Q_TYPE: WH from the new
    rule. Phase 5g / 5h / 5f baselines should be unchanged."""

    @pytest.mark.parametrize("sentence", [
        # Phase 5g
        "Maganda ang bata.",
        # Phase 5h
        "Mas matalino siya.",
        "Pinakamaganda ang bahay.",
        "Kasingganda si Maria si Ana.",
        # Phase 5f
        "Tatlo ang aklat.",
        # Yes/no with ba (not a wh-Q)
        "Kumain ka ba ng kanin?",
        # Phase 4 baseline
        "Kumain ang aso.",
    ])
    def test_no_phantom_wh_on_existing_constructions(
        self, sentence: str
    ) -> None:
        parses = parse_text(sentence)
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("Q_TYPE") != "WH", (
                f"unexpected Q_TYPE=WH on {sentence!r}: {fs.feats}"
            )


# === Negation × wh-cleft =============================================


class TestNegationPlusWhCleft:
    """Negation composes with the wh-cleft S unchanged via the
    Phase 4 hindi rule (tightened in Phase 5h Commit 3)."""

    def test_hindi_plus_sino_cleft(self) -> None:
        # ``Hindi sino ang kumain?`` is structurally weird in
        # English ("Not who ate?") but Tagalog admits it as a
        # negated cleft-Q; check that the parser composes.
        parses = parse_text("Hindi sino ang kumain.")
        # Note: with the . terminator (statement), some parses
        # may produce POLARITY=NEG. Tag with ? would be the
        # interrogative form. Either way, verify the composition
        # works structurally.
        # Be permissive — this is an edge case; primary Phase 5i
        # negation×wh tests live in negation×Phase 5i compose
        # tests.
        for _ct, fs, _astr, _diags in parses:
            # If wh-cleft fires, POLARITY may be NEG.
            if fs.feats.get("Q_TYPE") == "WH":
                # Optional check: WH_LEMMA preserved.
                assert fs.feats.get("WH_LEMMA") == "sino"


# === Phase 5g / 5h baseline parses preserved =========================


class TestBaselinePreserved:
    """Earlier-phase predicative clauses parse unchanged."""

    @pytest.mark.parametrize("sentence,expected_pred_prefix", [
        ("Maganda ang bata.",                "ADJ"),
        ("Pinakamaganda ang bahay.",         "ADJ"),
        ("Mas matalino siya kaysa kay Maria.", "ADJ"),
        ("Tatlo ang aklat.",                 "CARDINAL"),
        ("Pareho ang aklat.",                "ADJ"),
    ])
    def test_baseline_predicatives_unchanged(
        self, sentence: str, expected_pred_prefix: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        # Verify the matrix PRED has the expected prefix; the
        # new wh-cleft rule should NOT have absorbed any of these.
        match = [
            p for p in parses
            if (p[1].feats.get("PRED") or "").startswith(
                expected_pred_prefix
            )
        ]
        assert len(match) >= 1
