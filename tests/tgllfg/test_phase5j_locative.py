"""Phase 5j Commit 4: locative existential clause (nasa).

Roadmap §12.1 / plan-of-record §5.3, §6 Commit 4. Two new clause
rules in ``cfg/clause.py``:

    S → PART[LOC_EXISTENTIAL=YES] N NP[CASE=NOM]
    S → PART[LOC_EXISTENTIAL=YES] N NP[CASE=GEN] NP[CASE=NOM]

The base form admits bare-N locative grounds (``Nasa labas ang
aso``); the possessor-of-ground variant admits N + GEN-NP
locative grounds (``Nasa tuktok ng bundok ang bahay`` — R&G
"Ang Manok" simple #7). The two-rule split is preferred over a
single rule with optional GEN-NP because the parser's category-
pattern matching can't express "optional" daughters.

Equations: literal PRED ``'LOC <SUBJ>'`` (one-place over the
figure); SUBJ shared with the NOM-NP pivot (the figure /
theme); LOCATION feature on the matrix carries the locative
ground; CLAUSE_TYPE='LOC_EXISTENTIAL' for classifier / ranker
visibility; ``(↓1 LOC_EXISTENTIAL) =c 'YES'`` belt-and-braces
constraint.

This commit unblocks two of the three remaining R&G "Ang Manok"
simple sentences (§8 of plan-of-record):

* Simple #5: ``Nasa bundok ang bahay.``
* Simple #7: ``Nasa tuktok ng bundok ang bahay.``

End-to-end target sentences:

    Nasa labas ang aso.            "The dog is outside."
    Nasa bundok ang bahay.         "The house is on the mountain."
    Nasa bahay si Maria.           "Maria is at the house."
    Nasa tuktok ng bundok ang bahay.  "The house is on top of
                                       the mountain."
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Base form: simple locative existential ============================


class TestSimpleLocativeExistential:
    """Base rule fires on PART[LOC_EXISTENTIAL=YES] + N +
    NP[CASE=NOM] and produces a LOC_EXISTENTIAL matrix with the
    NOM-NP as SUBJ and the bare-N as LOCATION."""

    @pytest.mark.parametrize("sentence,subj_lemma,loc_lemma", [
        ("Nasa bundok ang bahay.", "bahay", "bundok"),
        ("Nasa labas ang aso.",    "aso",   "labas"),
        ("Nasa bahay si Maria.",   "maria", "bahay"),
        ("Nasa labas si Juan.",    "juan",  "labas"),
        ("Nasa bukid ang bahay.",  "bahay", "bukid"),
    ])
    def test_simple_locative_parses(
        self,
        sentence: str,
        subj_lemma: str,
        loc_lemma: str,
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got 0"
        )
        loc_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "LOC_EXISTENTIAL"
        ]
        assert len(loc_parses) >= 1
        _ct, fs, _astr, _diags = loc_parses[0]
        assert fs.feats.get("PRED") == "LOC <SUBJ>"
        assert fs.feats.get("CLAUSE_TYPE") == "LOC_EXISTENTIAL"
        # SUBJ is the figure (NOM-NP)
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma
        # LOCATION is the locative ground
        loc = fs.feats.get("LOCATION")
        assert loc is not None
        assert loc.feats.get("LEMMA") == loc_lemma


class TestLocativeCTreeShape:
    """Base form has 3 immediate daughters: PART / N / NP[CASE=NOM]."""

    def test_nasa_bundok_ang_bahay_c_tree(self) -> None:
        parses = parse_text("Nasa bundok ang bahay.")
        loc_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "LOC_EXISTENTIAL"
        ]
        assert len(loc_parses) >= 1
        ctree, _fs, _astr, _diags = loc_parses[0]
        assert ctree.label == "S"
        assert len(ctree.children) == 3, (
            f"expected 3 daughters; got "
            f"{[c.label for c in ctree.children]}"
        )
        assert ctree.children[0].label == "PART"
        assert ctree.children[1].label.startswith("N")
        assert ctree.children[2].label.startswith("NP[CASE=NOM]")


# === Possessor-of-ground variant ===================================


class TestPossessorGroundVariant:
    """Possessor variant fires on PART[LOC_EXISTENTIAL=YES] + N +
    NP[CASE=GEN] + NP[CASE=NOM] — the GEN-NP is the possessor of
    the locative ground (``tuktok ng bundok``: tuktok possessed
    by bundok)."""

    @pytest.mark.parametrize("sentence,subj_lemma,loc_lemma,poss_lemma", [
        ("Nasa tuktok ng bundok ang bahay.", "bahay", "tuktok", "bundok"),
        ("Nasa tuktok ng bahay ang aso.",    "aso",   "tuktok", "bahay"),
    ])
    def test_possessor_ground_parses(
        self,
        sentence: str,
        subj_lemma: str,
        loc_lemma: str,
        poss_lemma: str,
    ) -> None:
        parses = parse_text(sentence)
        loc_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "LOC_EXISTENTIAL"
        ]
        assert len(loc_parses) >= 1
        _ct, fs, _astr, _diags = loc_parses[0]
        assert fs.feats.get("PRED") == "LOC <SUBJ>"
        # SUBJ
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma
        # LOCATION + POSS
        loc = fs.feats.get("LOCATION")
        assert loc is not None
        assert loc.feats.get("LEMMA") == loc_lemma
        poss = loc.feats.get("POSS")
        assert poss is not None
        assert poss.feats.get("LEMMA") == poss_lemma


class TestPossessorVariantCTreeShape:
    """Possessor variant has 4 immediate daughters: PART / N /
    NP[CASE=GEN] / NP[CASE=NOM]."""

    def test_nasa_tuktok_ng_bundok_c_tree(self) -> None:
        parses = parse_text("Nasa tuktok ng bundok ang bahay.")
        loc_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "LOC_EXISTENTIAL"
        ]
        assert len(loc_parses) >= 1
        ctree, _fs, _astr, _diags = loc_parses[0]
        assert ctree.label == "S"
        assert len(ctree.children) == 4, (
            f"expected 4 daughters; got "
            f"{[c.label for c in ctree.children]}"
        )
        assert ctree.children[0].label == "PART"
        assert ctree.children[1].label.startswith("N")
        assert ctree.children[2].label.startswith("NP[CASE=GEN]")
        assert ctree.children[3].label.startswith("NP[CASE=NOM]")


# === R&G "Ang Manok" simples #5 and #7 ==============================


class TestRgAngManokSimples:
    """Phase 5j unblocks R&G 1981 "Ang Manok" simple sentences
    #5 and #7 (per plan-of-record §8). Both are pure locative-
    existentials and should parse cleanly via the base / possessor
    variant rules.

    The combined essay-paragraph sentence (R&G p. 482) needs
    additional Phase 5j follow-on work (mama / mag-isa / nakatira
    resultative) — out of scope for Commit 4.
    """

    def test_simple_5_nasa_bundok_ang_bahay(self) -> None:
        """R&G simple #5: ``Nasa bundok ang bahay.``"""
        parses = parse_text("Nasa bundok ang bahay.")
        loc_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "LOC_EXISTENTIAL"
        ]
        assert len(loc_parses) >= 1
        _ct, fs, _astr, _diags = loc_parses[0]
        assert fs.feats.get("PRED") == "LOC <SUBJ>"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "bahay"
        loc = fs.feats.get("LOCATION")
        assert loc is not None
        assert loc.feats.get("LEMMA") == "bundok"

    def test_simple_7_nasa_tuktok_ng_bundok_ang_bahay(self) -> None:
        """R&G simple #7: ``Nasa tuktok ng bundok ang bahay.``"""
        parses = parse_text("Nasa tuktok ng bundok ang bahay.")
        loc_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "LOC_EXISTENTIAL"
        ]
        assert len(loc_parses) >= 1
        _ct, fs, _astr, _diags = loc_parses[0]
        assert fs.feats.get("PRED") == "LOC <SUBJ>"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "bahay"
        loc = fs.feats.get("LOCATION")
        assert loc is not None
        assert loc.feats.get("LEMMA") == "tuktok"
        poss = loc.feats.get("POSS")
        assert poss is not None
        assert poss.feats.get("LEMMA") == "bundok"


# === Disambiguation: nasa doesn't match EXIST <SUBJ> ===============


class TestNasaDoesNotMatchExistRule:
    """``nasa`` carries LOC_EXISTENTIAL=YES but NOT
    EXISTENTIAL=YES, so the Phase 5j Commit 2 / 3 existential
    rules don't fire on it. Conversely, ``may`` / ``wala`` carry
    EXISTENTIAL=YES but NOT LOC_EXISTENTIAL=YES, so Commit 4
    rules don't fire on them. The two clause-types are
    distinct."""

    def test_nasa_clause_is_not_existential(self) -> None:
        parses = parse_text("Nasa bundok ang bahay.")
        for _ct, fs, _astr, _diags in parses:
            ct = fs.feats.get("CLAUSE_TYPE")
            assert ct != "EXISTENTIAL", (
                f"unexpected EXISTENTIAL on nasa-clause: {fs.feats}"
            )

    def test_may_clause_is_not_loc_existential(self) -> None:
        parses = parse_text("May aklat.")
        for _ct, fs, _astr, _diags in parses:
            ct = fs.feats.get("CLAUSE_TYPE")
            assert ct != "LOC_EXISTENTIAL", (
                f"unexpected LOC_EXISTENTIAL on may-clause: {fs.feats}"
            )


# === No phantom locative-existentials ================================


class TestNoPhantomLocativeExistentials:
    """V-headed clauses with sa-PP shouldn't acquire
    CLAUSE_TYPE=LOC_EXISTENTIAL from the new rules."""

    @pytest.mark.parametrize("sentence", [
        "Kumain ang aso sa labas.",
        "Maganda ang bata.",
        "Sino ang kumain?",
    ])
    def test_no_phantom_loc(self, sentence: str) -> None:
        parses = parse_text(sentence)
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("CLAUSE_TYPE") != "LOC_EXISTENTIAL", (
                f"unexpected CLAUSE_TYPE=LOC_EXISTENTIAL on "
                f"{sentence!r}: {fs.feats}"
            )
