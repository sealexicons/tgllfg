# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.A Commit 21 — HAVE-mayroon-with-linker (§18 L87).

Closes the §18 L87 deferral. The Phase 5j Commit 5 HAVE rules covered
the consonant-final ``may`` shape (Commits 5a / 5b) and the linker-
required ``wala`` negative shape (Commits 5c / 5d), but the
positive vowel-final ``mayroon`` HAVE forms with leading bound
``-ng`` linker were deferred. Two new clause rules close this gap:

  Commit 5e (positive HAVE — postposed possessor with linker):
    S → PART[POS] PART[LINK=NG] N NP[CASE=NOM]
    ``Mayroong aklat si Maria.``  "Maria has a book."

  Commit 5f (positive HAVE — internal clitic possessor with linker):
    S → PART[POS] PART[LINK=NG] PRON[CASE=NOM] PART[LINK=NG] N
    ``Mayroong akong aklat.``    "I have a book."

5e mirrors 5c (negative postposed with linker) with POS polarity;
5f mirrors 5b (positive internal clitic) with the extra leading
linker that ``mayroon`` requires.

F-structure shape (both rules) is identical to the existing 5a/5b
pattern: PRED='EXIST <SUBJ>', SUBJ=existence-asserted N,
SUBJ POSSESSOR=possessor, CLAUSE_TYPE='EXISTENTIAL',
HAVE='YES', POLARITY='POS'.
"""

import pytest

from tgllfg.core.pipeline import parse_text


# === Positive HAVE — mayroon postposed possessor (Commit 5e) =========


class TestMayroonHavePostposedFullNP:
    """``Mayroong aklat si Maria.`` — postposed full-NP possessor
    with leading -ng linker."""

    @pytest.mark.parametrize("sentence,subj_lemma,poss_lemma", [
        ("Mayroong aklat si Maria.",  "aklat", "maria"),
        ("Mayroong aklat si Juan.",   "aklat", "juan"),
        ("Mayroong bahay si Maria.",  "bahay", "maria"),
        ("Mayroong aklat ang lalaki.", "aklat", "lalaki"),
    ])
    def test_full_np_possessor(
        self, sentence: str, subj_lemma: str, poss_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        ex_parses = [
            p for p in parses if p[1].feats.get("HAVE") is True
        ]
        assert len(ex_parses) >= 1
        _ct, fs, _astr, _diags = ex_parses[0]
        assert fs.feats.get("PRED") == "EXIST <SUBJ>"
        assert fs.feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        assert fs.feats.get("POLARITY") == "POS"
        assert fs.feats.get("HAVE") is True
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma
        poss = subj.feats.get("POSSESSOR")
        assert poss is not None
        assert poss.feats.get("LEMMA") == poss_lemma


class TestMayroonHavePostposedClitic:
    """``Mayroong aklat ako.`` — postposed clitic-PRON possessor
    with leading -ng linker."""

    @pytest.mark.parametrize("sentence,subj_lemma", [
        ("Mayroong aklat ako.",  "aklat"),
        ("Mayroong aklat siya.", "aklat"),
        ("Mayroong bahay siya.", "bahay"),
    ])
    def test_clitic_pron_possessor_postposed(
        self, sentence: str, subj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        ex_parses = [
            p for p in parses if p[1].feats.get("HAVE") is True
        ]
        assert len(ex_parses) >= 1
        _ct, fs, _astr, _diags = ex_parses[0]
        assert fs.feats.get("HAVE") is True
        assert fs.feats.get("POLARITY") == "POS"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma
        poss = subj.feats.get("POSSESSOR")
        assert poss is not None
        # Clitic PRONs project to NP[CASE=NOM] but don't carry
        # LEMMA in this codebase — assert CASE instead.
        assert poss.feats.get("CASE") == "NOM"


# === Positive HAVE — mayroon internal clitic (Commit 5f) =============


class TestMayroonHaveInternalClitic:
    """``Mayroong akong aklat.`` — internal clitic-PRON possessor
    with two -ng linker daughters (one after mayroon, one after
    the clitic-PRON)."""

    @pytest.mark.parametrize("sentence,subj_lemma", [
        ("Mayroong akong aklat.",  "aklat"),
        ("Mayroong akong bahay.",  "bahay"),
        ("Mayroong siyang aklat.", "aklat"),
    ])
    def test_internal_clitic(
        self, sentence: str, subj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        ex_parses = [
            p for p in parses if p[1].feats.get("HAVE") is True
        ]
        assert len(ex_parses) >= 1
        _ct, fs, _astr, _diags = ex_parses[0]
        assert fs.feats.get("PRED") == "EXIST <SUBJ>"
        assert fs.feats.get("POLARITY") == "POS"
        assert fs.feats.get("HAVE") is True
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma
        poss = subj.feats.get("POSSESSOR")
        assert poss is not None
        assert poss.feats.get("CASE") == "NOM"


# === Existential (no possessor) regression ==========================


class TestExistentialNoPossessorRegression:
    """``Mayroong tao sa labas.`` — bare existential with locative
    PP, no HAVE reading. Verifies the new HAVE rules don't fire on
    existential-only inputs (HAVE flag absent)."""

    def test_mayroon_existential_no_have(self) -> None:
        parses = parse_text("Mayroong tao sa labas.")
        assert len(parses) >= 1
        # No parse should carry HAVE=YES on this sentence.
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("HAVE") is not True
        # The existential reading does parse.
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        assert fs.feats.get("PRED") == "EXIST <SUBJ>"


# === Composition: mayroon HAVE + N-coord ============================


class TestMayroonHaveWithNCoord:
    """``Mayroong aklat at lapis si Maria.`` — mayroon HAVE composes
    with N coordination on the existence-asserted N (closes the
    Phase 5k Commit 9 ``test_mayroon_have_with_coord_pinned_zero``
    pin)."""

    def test_mayroon_have_n_coord_full_np(self) -> None:
        parses = parse_text("Mayroong aklat at lapis si Maria.")
        ex_parses = [
            p for p in parses if p[1].feats.get("HAVE") is True
        ]
        assert len(ex_parses) >= 1
        _ct, fs, _astr, _diags = ex_parses[0]
        assert fs.feats.get("HAVE") is True
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        conjuncts = subj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2
        poss = subj.feats.get("POSSESSOR")
        assert poss is not None
        assert poss.feats.get("LEMMA") == "maria"


# === may regression (Phase 5j Commit 5a / 5b) =======================


class TestMayBareRegression:
    """The Phase 5j Commit 5 ``may`` HAVE rules continue to fire
    after the Commit 21 ``mayroon`` additions."""

    @pytest.mark.parametrize("sentence,poss_lemma", [
        ("May aklat si Maria.", "maria"),
        ("May bahay si Juan.",  "juan"),
    ])
    def test_may_postposed_full_np_still_parses(
        self, sentence: str, poss_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        ex_parses = [
            p for p in parses if p[1].feats.get("HAVE") is True
        ]
        assert len(ex_parses) >= 1
        _ct, fs, _astr, _diags = ex_parses[0]
        assert fs.feats.get("HAVE") is True
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        poss = subj.feats.get("POSSESSOR")
        assert poss is not None
        assert poss.feats.get("LEMMA") == poss_lemma

    def test_may_internal_clitic_still_parses(self) -> None:
        parses = parse_text("May akong aklat.")
        ex_parses = [
            p for p in parses if p[1].feats.get("HAVE") is True
        ]
        assert len(ex_parses) >= 1
