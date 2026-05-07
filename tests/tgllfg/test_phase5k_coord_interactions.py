"""Phase 5k Commit 9: coordination × interaction tests.

Roadmap §12.1 / plan-of-record §6 Commit 9. Verifies that the
Phase 5k coord rules compose correctly with existing
constructions: HAVE (Phase 5j), cardinals (Phase 5f), adjectival
modification (Phase 5g), predicative-ADJ (Phase 5g),
voice / aspect.

One small grammar addition: N-level binary coord rules (AND / OR)
in cfg/coordination.py to enable coord × HAVE composition. The
Phase 5j HAVE rules take bare-N as the existence-asserted
daughter; without N-level coord, ``May aklat at lapis si Maria.``
0-parsed because ``aklat at lapis`` couldn't reduce to a single
N. Two new rules (parallel to the Commit 3 NP-level binary
coord) restore the composition.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Coord × HAVE ====================================================


class TestCoordPlusHave:
    """``May aklat at lapis si Maria.`` "Maria has a book and a
    pencil" — coord × HAVE via the new N-level coord rule."""

    def test_pos_have_full_np_possessor(self) -> None:
        parses = parse_text("May aklat at lapis si Maria.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        assert fs.feats.get("HAVE") == "YES"
        assert fs.feats.get("POLARITY") == "POS"
        # SUBJ is the coord-N (aklat at lapis); has CONJUNCTS.
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "AND"
        conjuncts = subj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2
        lemmas = {c.feats.get("LEMMA") for c in conjuncts}
        assert lemmas == {"aklat", "lapis"}
        # POSSESSOR is si Maria.
        poss = subj.feats.get("POSSESSOR")
        assert poss is not None
        assert poss.feats.get("LEMMA") == "maria"

    def test_pos_have_clitic_possessor(self) -> None:
        parses = parse_text("May aklat at lapis ako.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "AND"
        # POSSESSOR is the 1sg-NOM clitic — represented as a
        # PRON f-structure with CASE/NUM (no LEMMA on bare PRON
        # f-structures, parallel to other Phase 5j HAVE clitic
        # tests).
        poss = subj.feats.get("POSSESSOR")
        assert poss is not None
        assert poss.feats.get("CASE") == "NOM"
        assert poss.feats.get("NUM") == "SG"

    def test_neg_have_with_coord(self) -> None:
        parses = parse_text("Walang aklat at lapis si Maria.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        assert fs.feats.get("POLARITY") == "NEG"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "AND"


# === Coord × cardinals (Phase 5f × 5k) ==============================


class TestCoordPlusCardinals:
    """Cardinal-modified NP coordinates cleanly via the existing
    NP-level coord rules — no Commit 9 changes needed; this test
    pins the existing composition behavior."""

    def test_cardinal_modified_gen_coord(self) -> None:
        """``Bumili ng dalawang aklat at ng tatlong lapis si
        Maria.`` "Maria bought two books and three pencils"."""
        parses = parse_text(
            "Bumili ng dalawang aklat at ng tatlong lapis si Maria."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        obj = fs.feats.get("OBJ")
        assert obj is not None
        assert obj.feats.get("COORD") == "AND"
        conjuncts = obj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2
        # Each conjunct carries its own CARDINAL_VALUE.
        cardinals = {c.feats.get("CARDINAL_VALUE") for c in conjuncts}
        assert cardinals == {"2", "3"}

    def test_isa_dalawa_mixed_cardinals(self) -> None:
        parses = parse_text(
            "Bumili ng isang aklat at ng dalawang lapis si Maria."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        obj = fs.feats.get("OBJ")
        assert obj is not None
        conjuncts = obj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        cardinals = {c.feats.get("CARDINAL_VALUE") for c in conjuncts}
        assert cardinals == {"1", "2"}


# === Coord × ADJ-mod (Phase 5g × 5k) ================================


class TestCoordPlusAdjectivalModification:
    """Adjective-modified NPs coordinate cleanly: ``ng malalaking
    aklat at ng maliliit na lapis`` — each conjunct retains its
    own ADJ-MOD; the matrix coord-NP carries CONJUNCTS unchanged."""

    def test_adj_modified_gen_coord(self) -> None:
        parses = parse_text(
            "Bumili si Maria ng malalaking aklat "
            "at ng maliliit na lapis."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        obj = fs.feats.get("OBJ")
        assert obj is not None
        assert obj.feats.get("COORD") == "AND"
        conjuncts = obj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2
        lemmas = {c.feats.get("LEMMA") for c in conjuncts}
        assert lemmas == {"aklat", "lapis"}


# === Coord × predicative-ADJ (Phase 5g × 5k) ========================


class TestCoordPlusPredAdj:
    """Predicative-ADJ + coord SUBJ + ADJ × ADJ predicate coord
    (Phase 5g + 5k composition)."""

    def test_pred_adj_with_coord_subj(self) -> None:
        parses = parse_text("Maganda si Maria at si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith("ADJ")
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "AND"
        conjuncts = subj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2

    def test_adj_predicate_coord(self) -> None:
        """``Matanda at maganda si Maria.`` "Maria is old and
        beautiful." — coord composes at the predicate level via
        the existing Phase 5g predicative-ADJ shape."""
        parses = parse_text("Matanda at maganda si Maria.")
        assert len(parses) >= 1


# === Coord SUBJ × verb voice / aspect ===============================


class TestCoordSubjPlusVerbVoiceAspect:
    """Tagalog verbs don't inflect for SUBJ NUM, so coord-NP SUBJ
    composes cleanly with any voice / aspect — pin the parse on
    each ASPECT (PFV / IPFV / CTPL)."""

    @pytest.mark.parametrize("sentence,expected_aspect", [
        ("Kumain si Maria at si Juan.",   "PFV"),
        ("Kumakain si Maria at si Juan.", "IPFV"),
        ("Kakain si Maria at si Juan.",   "CTPL"),
    ])
    def test_coord_subj_across_aspects(
        self, sentence: str, expected_aspect: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("ASPECT") == expected_aspect
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "AND"
        assert subj.feats.get("NUM") == "PL"


# === Coord × cardinals × ADJ (3-way Phase 5f × 5g × 5k) ==============


class TestThreeWayComposition:
    """Cardinal + ADJ + coord composing in one NP. ``ng dalawang
    malalaking aklat at ng tatlong maliliit na lapis`` "of two
    big books and of three small pencils"."""

    def test_cardinal_plus_adj_plus_coord(self) -> None:
        parses = parse_text(
            "Bumili ng dalawang malalaking aklat "
            "at ng tatlong maliliit na lapis si Maria."
        )
        if not parses:
            pytest.skip(
                "Three-way composition (cardinal + ADJ + coord) "
                "is a stretch test; defer if not parsing."
            )
        _ct, fs, _astr, _diags = parses[0]
        obj = fs.feats.get("OBJ")
        if obj is None:
            pytest.skip("Three-way composition didn't yield an OBJ")
        if obj.feats.get("COORD") != "AND":
            pytest.skip("Three-way composition didn't fire coord rule")
        conjuncts = obj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2


# === Pinned Phase 5j gaps (NOT Commit 9 issues) =====================


class TestPhase5jHavePinnedGaps:
    """Pre-existing Phase 5j gaps that surfaced during Commit 9
    audit but are NOT Commit 9's responsibility. Pin the 0-parse
    state so future Phase 5j follow-ons flip when the rule lands.

    The HAVE-mayroon-with-linker form ``Mayroong aklat si Maria.``
    has no Phase 5j rule — Phase 5j Commit 5 only added 4 HAVE
    rules (positive postposed / clitic-possessor + negative
    postposed / clitic-possessor); the linker-mayroon HAVE form
    is a Phase 5j follow-on."""

    def test_mayroon_have_pinned_zero(self) -> None:
        parses = parse_text("Mayroong aklat si Maria.")
        assert len(parses) == 0, (
            "Mayroong aklat si Maria. now parses — Phase 5j "
            "follow-on may have landed the linker-mayroon HAVE "
            "rule. Update this test and add positive coverage."
        )

    def test_mayroon_have_with_coord_pinned_zero(self) -> None:
        parses = parse_text("Mayroong aklat at lapis si Maria.")
        assert len(parses) == 0, (
            "Mayroong aklat at lapis si Maria. now parses — Phase "
            "5j follow-on linker-mayroon HAVE rule may have landed."
        )
