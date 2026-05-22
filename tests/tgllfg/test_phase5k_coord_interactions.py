# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

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
        assert fs.feats.get("HAVE") is True
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
        # Phase 5n.C.4: the defensive ``pytest.skip`` clauses that
        # used to gate this test were dead code by the time this
        # phase ran — three-way composition (cardinal + ADJ + coord
        # in a single NP) parses cleanly. The earlier scaffolding is
        # removed so a regression fails loudly instead of silently
        # downgrading to "skipped".
        assert parses, "three-way composition (cardinal + ADJ + coord) failed to parse"
        _ct, fs, _astr, _diags = parses[0]
        obj = fs.feats.get("OBJ")
        assert obj is not None, "three-way composition did not yield an OBJ"
        assert obj.feats.get("COORD") == "AND", (
            "three-way composition did not fire the coord rule"
        )
        conjuncts = obj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2


# Phase 5j HAVE-mayroon-with-linker pin closed by Phase 5n.A
# Commit 21 — see test_phase5n_have_mayroon_linker.py for positive
# coverage of ``Mayroong aklat si Maria.`` and the N-coord
# composition ``Mayroong aklat at lapis si Maria.``.
