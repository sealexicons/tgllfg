# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.A Commit 30 — COND vs reported-Q vs indirect-speech
disambiguation sweep.

Closes the Phase 5n.A regression-sweep step. Verifies the
Commit 27 (SAY-class indirect-speech) and Commit 29 (ASK-class
reported-Q + kita-fusion tightening) changes don't regress:

* Phase 5l COND-adjunct uses for non-SAY / non-ASK matrix verbs.
* Phase 5i KNOW-class indirect-Q (alam) reading.
* Phase 5l other-COMP-TYPE adjunct families
  (TEMP / PURP / REAS / CONC).

And confirms there is no cross-pollination across the three
families (SAY-class indirect-speech, ASK-class reported-Q,
KNOW-class indirect-Q):

* Non-SAY OV verb + ``na`` + S doesn't get a SAY-style reading.
* Non-ASK OV verb + ``kung`` + S doesn't get an ASK-style reading.
* SAY-class verb + ``kung`` + S doesn't accidentally get an
  ASK-style reading.
* ASK-class verb + ``na`` + S doesn't accidentally get a
  SAY-style reading.

The Phase 5n.A baseline (``tests/tgllfg/data/parses.baseline.pkl``)
was recaptured in this commit to absorb the Commit 25-29 corpus
additions and the Commit 27 / 29 rule effects.
"""

import pytest

from tgllfg.core.pipeline import parse_text


# === Phase 5l COND-adjunct continues to fire for non-SAY/non-ASK ====


class TestCondAdjunctRegression:
    """Plain conditional surfaces (no SAY-class / ASK-class
    matrix V) continue to parse with the kung-clause as a
    COND-adjunct."""

    @pytest.mark.parametrize("sentence", [
        "Kung kumain ako, pumunta siya.",
        "Kapag kumain ako, pumunta siya.",
        "Pag kumain ako, pumunta siya.",
        "Kung pumunta si Maria, kumain ako.",
        "Kung kumain ako, hindi pumunta siya.",
    ])
    def test_cond_adjunct_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        adjuncts = fs.feats.get("ADJUNCT")
        assert adjuncts is not None
        assert any(
            a.feats.get("SUBORD_TYPE") == "COND" for a in adjuncts
        ), f"{sentence!r} should produce a COND-adjunct"


# === Phase 5l other-COMP-TYPE adjuncts unchanged =================


class TestOtherSubordTypesUnchanged:
    """TEMP / PURP / REAS / CONC adjunct families continue to
    fire after the Commit 27/29 changes."""

    @pytest.mark.parametrize("sentence,subord_type", [
        ("Bago pumunta siya, kumain ako.",     "TEMP_BEFORE"),
        ("Pagkatapos kumain ako, pumunta siya.", "TEMP_AFTER"),
        ("Habang kumain ako, pumunta siya.",   "TEMP_WHILE"),
        ("Para pumunta siya, kumain ako.",     "PURP"),
        ("Dahil kumain ako, pumunta siya.",    "REAS"),
        ("Bagaman kumain ako, pumunta siya.",  "CONC"),
    ])
    def test_subord_type_attaches(
        self, sentence: str, subord_type: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        adjuncts = fs.feats.get("ADJUNCT")
        assert adjuncts is not None
        assert any(
            a.feats.get("SUBORD_TYPE") == subord_type
            for a in adjuncts
        )


# === Phase 5i KNOW-class indirect-Q regression ===================


class TestKnowIndirectQRegression:
    """Phase 5i ``Alam ko kung sino ang kumain.`` — KNOW-class
    indirect-Q with COMP_TYPE=INTERROG complement — continues to
    parse."""

    @pytest.mark.parametrize("sentence", [
        "Alam ko kung sino ang kumain.",
        "Alam ko kung saan pumunta si Maria.",
        "Alam ko kung kailan pumunta si Maria.",
        "Alam ko kung paano kumain si Maria.",
    ])
    def test_alam_indirect_q_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        # The KNOW rule produces PRED='KNOW <SUBJ, COMP>' with
        # COMP.COMP_TYPE='INTERROG'.
        know_parses = [
            p for p in parses
            if p[1].feats.get("PRED") == "KNOW <SUBJ, COMP>"
        ]
        assert len(know_parses) >= 1
        _ct, fs, _astr, _diags = know_parses[0]
        comp = fs.feats.get("COMP")
        assert comp is not None
        assert comp.feats.get("COMP_TYPE") == "INTERROG"


# === No cross-pollination ========================================


class TestNoCrossPollination:
    """Verify the SAY/ASK/KNOW gates are tight: each rule fires
    only on its targeted matrix-V class."""

    def test_non_say_ov_with_na_no_say_reading(self) -> None:
        """``Kinain niya na pumunta si Maria.`` — non-SAY OV
        verb (kinain) + na + S doesn't get a SAY-style indirect-
        speech reading from the Commit 27 rule."""
        parses = parse_text("Kinain niya na pumunta si Maria.")
        # The Commit 27 SAY rule's ``(↓1 SAY_CLASS) =c 'YES'``
        # gate rejects kinain (no SAY_CLASS feat). Any parse
        # that does come through cannot have SUBJ.PRED='PUNTA'
        # via the SAY-class path.
        for p in parses:
            fs = p[1]
            pred = fs.feats.get("PRED", "")
            if not isinstance(pred, str) or not pred.startswith("EAT"):
                continue
            subj = fs.feats.get("SUBJ")
            if subj is None:
                continue
            assert subj.feats.get("PRED") != "PUNTA <SUBJ>", (
                "kinain (non-SAY) unexpectedly admits a "
                "SAY-class indirect-speech parse"
            )

    def test_non_ask_ov_with_kung_no_ask_reading(self) -> None:
        """``Kinain niya kung sino ang kumain.`` — non-ASK OV
        verb (kinain) + kung + S doesn't get a TANONG-style
        reported-Q reading from the Commit 29 rule."""
        parses = parse_text("Kinain niya kung sino ang kumain.")
        # If anything parses (the COND-adjunct path may still
        # fire), it should not carry COMP_TYPE=INTERROG via the
        # ASK-class rule.
        for p in parses:
            fs = p[1]
            # ASK-class rule path: SUBJ.COMP_TYPE=INTERROG.
            subj = fs.feats.get("SUBJ")
            if subj is not None:
                assert subj.feats.get("COMP_TYPE") != "INTERROG", (
                    "kinain (non-ASK) unexpectedly admits an "
                    "ASK-class reported-Q parse via SUBJ"
                )

    def test_say_class_with_kung_no_ask_reading(self) -> None:
        """``Sinabi niya kung sino ang kumain.`` — SAY-class
        verb (sinabi) + kung + S. Even if it parses (via
        COND-adjunct), the SUBJ should not carry
        COMP_TYPE=INTERROG (SAY rule expects ``na``, not ``kung``)."""
        parses = parse_text("Sinabi niya kung sino ang kumain.")
        for p in parses:
            fs = p[1]
            subj = fs.feats.get("SUBJ")
            if subj is not None:
                # The Commit 27 SAY rule requires PART[LINK=NA],
                # not kung — so SUBJ shouldn't carry COMP_TYPE=INTERROG.
                assert subj.feats.get("COMP_TYPE") != "INTERROG", (
                    "sinabi + kung unexpectedly produced an "
                    "ASK-style SUBJ.COMP_TYPE=INTERROG"
                )

    def test_ask_class_with_na_no_say_reading(self) -> None:
        """``Tinanong niya na pumunta si Maria.`` — ASK-class
        verb (tinanong) + na + S. The Commit 29 ASK rule
        requires S_INTERROG_COMP (kung-introduced); ``na``-S
        shouldn't trigger it. The Commit 27 SAY rule has its
        own SAY_CLASS=YES gate; tinanong is ASK_CLASS=YES, not
        SAY_CLASS=YES. Neither rule should fire."""
        parses = parse_text("Tinanong niya na pumunta si Maria.")
        for p in parses:
            fs = p[1]
            # ASK rule: SUBJ.COMP_TYPE=INTERROG (won't match na-S).
            # SAY rule: PRED='SABI' (won't match tinanong).
            assert fs.feats.get("PRED", "").startswith("TANONG") or \
                   fs.feats.get("PRED") is None
            subj = fs.feats.get("SUBJ")
            if subj is not None:
                assert subj.feats.get("COMP_TYPE") != "INTERROG"


# === kita-fusion still admits legitimate kita ====================


class TestKitaStillFires:
    """The Commit 29 ``(↓2 KITA) =c 'YES'`` tightening doesn't
    block legitimate ``kita`` (the 1sg-GEN + 2sg-NOM fused
    clitic)."""

    @pytest.mark.parametrize("sentence", [
        "Kinain kita.",
        "Binasahan kita.",
        "Pinakain kita ng kanin.",
        "Hindi kita kinain.",
        "Kinain na kita.",
    ])
    def test_kita_sentences_still_parse(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
