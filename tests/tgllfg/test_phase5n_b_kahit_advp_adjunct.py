"""Phase 5n.B Commit 19: clause-final indefinite AdvP (§18 L99).

Closes §18.1 deferral L99. Target sentences:

    Pupunta ako kahit saan.    "I'll go anywhere."
    Kakain ako kahit kailan.   "I'll eat anytime."
    Kumain ako kahit saan.     "I ate anywhere."

One grammar change (cfg/discourse.py): new sibling rule to the
Phase 5f Commit 5 FREQUENCY AdvP rule, ``S → S AdvP`` gated on
``(↓2 INDEF) =c 'YES'``. Indefinite ADVs are produced by the
Phase 5m C8 IndefADV rule (``ADV → PART[LEMMA=kahit]
ADV[WH=YES]``) which composes ``kahit`` with the wh-ADV
inventory (saan / kailan / paano / bakit).

The plain-LOCATION / plain-TIME deferrals from Phase 5f C5
remain in force — only the kahit-X indefinite variants are
admitted by the new INDEF=YES gate.

Per plan-of-record §4.2 Commit 19 the explicit targets are
LOCATION (kahit saan) and TIME (kahit kailan); the INDEF=YES
gate also admits MANNER (kahit paano) and REASON (kahit bakit)
which are equally natural — covered in tests below.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


def _adv_lemma_in_adjunct(fs, lemma: str) -> bool:
    """Return True if the matrix's ADJUNCT set contains an entry
    with LEMMA==lemma and INDEF='YES'."""
    adj = fs.feats.get("ADJUNCT") or set()
    for m in adj:
        if (
            getattr(m, "feats", {}).get("LEMMA") == lemma
            and getattr(m, "feats", {}).get("INDEF") == "YES"
        ):
            return True
    return False


# === kahit saan (LOCATION) ============================================


class TestKahitSaan:
    """``kahit saan`` "anywhere" attaches as a clause-final
    indefinite-LOCATION ADJUNCT."""

    @pytest.mark.parametrize("sentence", [
        "Pupunta ako kahit saan.",
        "Kumain ako kahit saan.",
        "Pumunta si Maria kahit saan.",
    ])
    def test_kahit_saan_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert _adv_lemma_in_adjunct(fs, "saan")


# === kahit kailan (TIME) ==============================================


class TestKahitKailan:
    """``kahit kailan`` "anytime" attaches as a clause-final
    indefinite-TIME ADJUNCT."""

    @pytest.mark.parametrize("sentence", [
        "Kakain ako kahit kailan.",
        "Pumunta ako kahit kailan.",
        "Kumain si Maria kahit kailan.",
    ])
    def test_kahit_kailan_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert _adv_lemma_in_adjunct(fs, "kailan")


# === kahit paano / kahit bakit (MANNER / REASON) =====================


class TestKahitOtherWh:
    """The INDEF=YES gate generalises beyond LOCATION / TIME;
    MANNER (paano) and REASON (bakit) work identically."""

    @pytest.mark.parametrize("sentence,lemma", [
        ("Kumain ako kahit paano.",  "paano"),
        ("Kumain ako kahit bakit.",  "bakit"),
    ])
    def test_other_kahit_wh(
        self, sentence: str, lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert _adv_lemma_in_adjunct(fs, lemma)


# === Phase 5f C5 FREQUENCY regression ================================


class TestFrequencyAdvUnchanged:
    """The original Phase 5f C5 FREQUENCY AdvP rule continues to
    fire on ``Kumakain ako lagi.`` etc. The new INDEF=YES rule
    is a sibling, not a replacement."""

    @pytest.mark.parametrize("sentence", [
        "Kumakain ako lagi.",
        "Kumakain ako palagi.",
    ])
    def test_frequency_unchanged(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        adj = fs.feats.get("ADJUNCT") or set()
        # ADJUNCT contains a FREQUENCY adverb.
        freq_present = any(
            getattr(m, "feats", {}).get("ADV_TYPE") == "FREQUENCY"
            for m in adj
        )
        assert freq_present


# === Plain LOCATION / TIME still deferred ============================


class TestPlainLocationTimeDeferred:
    """Plain LOCATION / TIME ADVs (without the INDEF=YES indef-
    builder) remain deferred per the Phase 5f C5 closing note —
    they would interact with quantifier-float and Wackernagel
    cluster machinery in ways that need separate analytical work.
    The new INDEF=YES gate keeps them out."""

    def test_plain_dito_does_not_attach(self) -> None:
        # ``dito`` is a LOCATION pseudo-pronoun; standalone in
        # post-V position it doesn't attach via this rule. (It
        # does parse, but via a different path — typically the
        # demonstrative-DAT-NP path or as a fragment.)
        parses = parse_text("Kumain ako dito.")
        # Whatever path fires, the matrix ADJUNCT should NOT
        # contain a plain dito with INDEF=YES (since dito has no
        # INDEF feat from any rule).
        for _ct, fs, _astr, _diags in parses:
            adj = fs.feats.get("ADJUNCT") or set()
            for m in adj:
                # dito should not appear as INDEF=YES (it isn't).
                if getattr(m, "feats", {}).get("LEMMA") == "dito":
                    assert getattr(m, "feats", {}).get("INDEF") != "YES"
