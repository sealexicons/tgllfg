"""Phase 7a.G: kahit-X wh-PRONs in non-NOM slots (§18.1.1 item 10).

New rule in ``cfg/nominal.py`` (parallel to the Phase 5i Commit 3
in-situ wh-PRON shell rules):

    NP[CASE=GEN, WH=true] → PART PRON[WH]
    NP[CASE=DAT, WH=true] → PART PRON[WH]
       (↑ PRED) = 'WH-PRO'
       (↑ INDEF) = 'YES'
       (↑ WH) = ↓2 WH
       (↑ LEMMA) = ↓2 LEMMA
       (↑ WH_LEMMA) = ↓2 LEMMA
       ↓1 ∈ (↑ ADJUNCT)
       (↓1 LEMMA) =c 'kahit'
       (↓2 WH) =c true
       (↓2 CASE) =c 'NOM'

Closes the non-NOM gap for kahit-X wh-PRONs (`ano`/`sino`/`alin`,
which are lex'd CASE=NOM only). The rule projects bare
``kahit + wh-PRON`` compositions directly into case-marked NPs
for GEN-OBJ and DAT-OBL slots, bypassing the analyzer's
single-surface-per-key indexing constraint that blocks adding
lex variants.

GT-empirical validation (2026-05-14): the three target surfaces
all produce canonical OBJ-reading translations:

    Kumain siya kahit ano.  → "He will eat anything."
    Kumain siya kahit sino. → "He ate anyone."
    Kumain siya kahit alin. → "He ate whatever."

Note on ambiguity: each target surface produces 3 parses today
(OBJ reading + ADJUNCT reading + a residual artifact). Tests
filter on the canonical OBJ reading via `INDEF=YES` +
`LEMMA` discriminator. Plan §3.8 documents the choice.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _obj_indef_parse(parses: list, expected_lemma: str):
    """Return the first parse with OBJ having INDEF=YES and the
    expected LEMMA. Filters spurious ADJUNCT / fragment readings."""
    for p in parses:
        obj = p[1].feats.get("OBJ")
        if (
            isinstance(obj, FStructure)
            and obj.feats.get("INDEF") == "YES"
            and obj.feats.get("LEMMA") == expected_lemma
        ):
            return p
    return None


# === kahit-X in OBJ position (the primary §3.8 target) ================


class TestKahitXInOBJ:
    """The new rule projects `kahit + wh-PRON` to NP[CASE=GEN,
    WH=true, INDEF=YES] which fills the GEN-OBJ slot in
    AV-transitive frames."""

    @pytest.mark.parametrize(
        "sentence,wh_lemma",
        [
            ("Kumain siya kahit ano.",   "ano"),
            ("Kumain siya kahit sino.",  "sino"),
            ("Kumain siya kahit alin.",  "alin"),
            ("Bumili siya kahit ano.",   "ano"),
            ("Bumili siya kahit alin.",  "alin"),
        ],
    )
    def test_kahit_x_obj_reading_present(
        self, sentence: str, wh_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert parses, f"{sentence!r} should parse"
        p = _obj_indef_parse(parses, wh_lemma)
        assert p is not None, (
            f"{sentence!r} should produce a parse with OBJ having "
            f"INDEF=YES and LEMMA={wh_lemma!r}"
        )
        obj = p[1].feats.get("OBJ")
        assert obj.feats.get("WH") is True


# === kanino preserved via existing C3d rule (NOM gate works) ============


class TestKaninoUnchanged:
    """The NOM-source gate (`(↓2 CASE) =c 'NOM'`) on the new
    rule ensures `kanino` (CASE=DAT lex variant) doesn't trigger
    the new rule; the existing Phase 6.C C3d DAT-IndefPRON rule
    handles `kahit kanino` natively. Parse count for
    `Nagsulat siya kahit kanino.` stays at 1 (was 1 pre-7a.G)."""

    def test_kahit_kanino_single_parse(self) -> None:
        parses = parse_text("Nagsulat siya kahit kanino.")
        assert len(parses) == 1, (
            "kahit kanino should have exactly 1 parse — the new "
            "Phase 7a.G rule's NOM-source gate prevents firing on "
            "the DAT-lex'd kanino (which is handled by the existing "
            "Phase 6.C C3d DAT-IndefPRON rule)"
        )


# === Pre-Phase-7a.G NOM forms regression =============================


class TestNOMFormsRegression:
    """Pre-Phase-7a.G NOM-position kahit-X surfaces are unaffected.
    The new rule produces only GEN / DAT outputs; NOM uses the
    existing Phase 6.C C3d NOM-IndefPRON rule."""

    @pytest.mark.parametrize(
        "sentence",
        [
            "Kumain kahit sino.",     # Phase 5m C8 post-V SUBJ
            "Kahit sino kumain.",     # Phase 7a.F pre-V SUBJ
            "Kahit sino ay kumain.",  # Phase 5n.B C20 ay-fronted
        ],
    )
    def test_nom_surface_unchanged(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert parses, f"NOM-position {sentence!r} should still parse"


# === kahit saan via Phase 5m IndefADV path (unchanged) ==============


class TestKahitSaanUnchanged:
    """`kahit saan` uses a separate IndefADV path (`saan` is ADV,
    not PRON). The new Phase 7a.G rule has PRON[WH] daughter
    constraint and doesn't fire on saan."""

    def test_pumunta_kahit_saan(self) -> None:
        # `Pumunta siya kahit saan.` "He went anywhere."
        parses = parse_text("Pumunta siya kahit saan.")
        assert parses, "kahit saan should still parse via IndefADV"
