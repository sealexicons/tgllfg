# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.A Commit 13 — Modal + sa-PP ADJUNCT in embedded XCOMP (§18 L70).

Pre-Commit-13 the Phase 4 §7.6 S_XCOMP AV-frames covered:

    S_XCOMP → V[VOICE=AV]                                  (no OBJ)
    S_XCOMP → V[VOICE=AV] NP[CASE=GEN]                     (V + GEN-OBJ)
    S_XCOMP → V[VOICE=AV] NP[CASE=GEN] NP[CASE=DAT]        (V + GEN-OBJ + DAT-ADJUNCT)

But not the 2-daughter ``V[VOICE=AV] NP[CASE=DAT]`` (intransitive
V + DAT-ADJUNCT) shape. So ``Dapat akong kumain sa labas.`` "I should
eat outside" 0-parsed: the embedded ``kumain sa labas`` has no GEN-OBJ
between V and the locative PP.

Phase 5n.A Commit 13 adds the missing 2-daughter S_XCOMP variant
that mirrors the 3-daughter form's ADJUNCT lift but drops the GEN-OBJ
slot. Composes with the Phase 5j Commit 7 modal control wrap to admit
the canonical ``modal + clitic + linker + V + sa-PP`` shape.
"""

import pytest

from tgllfg.core.pipeline import parse_text


# === Canonical modal + V + sa-PP =========================================


class TestModalWithSaPp:
    """Modal + clitic + linker + V[AV intransitive] + sa-PP composes
    via the new S_XCOMP variant for all four modals."""

    @pytest.mark.parametrize("sentence", [
        "Dapat akong kumain sa labas.",
        "Puwede akong kumain sa labas.",
        "Maaari akong kumain sa labas.",
        "Kailangan akong kumain sa labas.",
        # Different V + PP combinations:
        "Dapat akong pumunta sa palengke.",
        "Puwede akong pumunta sa bahay.",
        "Maaari akong tumakbo sa parke.",
        "Kailangan akong umalis sa kuwarto.",
    ])
    def test_modal_v_sa_pp(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === ADJUNCT attached to embedded XCOMP ==================================


class TestAdjunctOnXcomp:
    """The sa-PP ADJUNCT attaches to the embedded XCOMP (the inner
    clause), not the matrix S — verify by walking the f-structure."""

    def test_sa_labas_in_xcomp_adjunct(self) -> None:
        parses = parse_text("Dapat akong kumain sa labas.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # Matrix XCOMP carries the ADJUNCT
        xcomp = fs.feats.get("XCOMP")
        assert xcomp is not None
        adjunct = xcomp.feats.get("ADJUNCT")
        assert adjunct is not None, (
            f"sa-PP should be in XCOMP ADJUNCT; XCOMP feats: "
            f"{xcomp.feats}"
        )
        adj_member = next(iter(adjunct))
        # The ADJUNCT member is the sa-PP (CASE=DAT, headed by labas)
        assert adj_member.feats.get("CASE") == "DAT"
        assert adj_member.feats.get("LEMMA") == "labas"


# === Single-clause regression =============================================


class TestSingleClauseRegression:
    """Bare V + sa-PP (no modal) and modal + V (no PP) continue to
    work — the new rule only fires inside modal control wraps."""

    @pytest.mark.parametrize("sentence", [
        # Bare V + sa-PP (Phase 4 baseline):
        "Kumain ako sa labas.",
        "Pumunta ako sa palengke.",
        # Modal + V (no PP):
        "Dapat akong kumain.",
        "Puwede akong kumain.",
        # Modal + V + GEN-OBJ + sa-PP (existing 3-daughter S_XCOMP):
        "Dapat akong kumain ng kanin sa labas.",
    ])
    def test_baseline_unchanged(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
