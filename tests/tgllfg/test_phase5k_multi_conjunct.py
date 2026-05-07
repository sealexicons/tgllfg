"""Phase 5k Commit 4: multi-conjunct NP coordination (3-flat).

Roadmap §12.1 / plan-of-record §5.3, §6 Commit 4. Six new rules
in ``cfg/coordination.py`` — Oxford-comma and non-Oxford-comma
3-conjunct flat additive coord, for each case
X ∈ {NOM, GEN, DAT}:

    Oxford:     NP[CASE=X] → NP COMMA NP COMMA AND NP    (6 daughters)
    Non-Oxford: NP[CASE=X] → NP COMMA NP AND NP          (5 daughters)

Both Oxford and non-Oxford comma conventions are attested in
modern Tagalog written practice. Both produce a flat 3-element
CONJUNCTS set on the matrix; the matrix carries COORD=AND, NUM=PL,
and the per-case CASE.

PUNCT[COMMA] daughters are syncategorematic (no equation refers
to them); the comma is now lex'd (Phase 5k Commit 1) so it
survives ``_strip_non_content`` and is consumed structurally
here.

Restricted to AND only; 4+ conjuncts are deferred to a Phase 5k
follow-on (see plan-of-record §5.3 / §9.2).

End-to-end target sentences:

    Kumain si Maria, si Juan, at si Pedro.    NOM-coord SUBJ (Oxford)
    Kumain si Maria, si Juan at si Pedro.     NOM-coord SUBJ (non-Oxford)
    Kumain ng aklat, ng lapis, at ng papel si Maria.  GEN-coord OBJ
    Pumunta si Maria sa palengke, sa bahay, at sa simbahan.  DAT-coord ADJUNCT
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Oxford-comma form (6 daughters) =================================


class TestOxfordCommaThreeConjunct:
    """``Maria, Juan, at Pedro`` — Oxford-comma form with two
    PUNCT[COMMA] daughters (between conj 1-2 and between conj 2-3
    + at). 3-element flat CONJUNCTS set."""

    def test_nom_three_conjunct_oxford(self) -> None:
        parses = parse_text("Kumain si Maria, si Juan, at si Pedro.")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "AND"
        assert subj.feats.get("CASE") == "NOM"
        assert subj.feats.get("NUM") == "PL"
        conjuncts = subj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 3
        lemmas = {c.feats.get("LEMMA") for c in conjuncts}
        assert lemmas == {"maria", "juan", "pedro"}

    def test_gen_three_conjunct_oxford(self) -> None:
        parses = parse_text(
            "Kumain ng aklat, ng lapis, at ng papel si Maria."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        obj = fs.feats.get("OBJ")
        assert obj is not None
        assert obj.feats.get("COORD") == "AND"
        assert obj.feats.get("CASE") == "GEN"
        assert obj.feats.get("NUM") == "PL"
        conjuncts = obj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 3
        lemmas = {c.feats.get("LEMMA") for c in conjuncts}
        assert lemmas == {"aklat", "lapis", "papel"}

    def test_dat_three_conjunct_oxford(self) -> None:
        parses = parse_text(
            "Pumunta si Maria sa palengke, sa bahay, at sa simbahan."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        adjuncts = fs.feats.get("ADJUNCT")
        assert adjuncts is not None
        coord_adjuncts = [
            a for a in adjuncts if a.feats.get("COORD") == "AND"
        ]
        assert len(coord_adjuncts) == 1
        coord = coord_adjuncts[0]
        assert coord.feats.get("CASE") == "DAT"
        conjuncts = coord.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 3
        lemmas = {c.feats.get("LEMMA") for c in conjuncts}
        assert lemmas == {"palengke", "bahay", "simbahan"}


# === Non-Oxford form (5 daughters) ===================================


class TestNonOxfordThreeConjunct:
    """``Maria, Juan at Pedro`` — non-Oxford form with one
    PUNCT[COMMA] daughter (between conj 1-2 only). 3-element
    flat CONJUNCTS set, identical f-structure to Oxford form."""

    def test_nom_three_conjunct_non_oxford(self) -> None:
        parses = parse_text("Kumain si Maria, si Juan at si Pedro.")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "AND"
        assert subj.feats.get("NUM") == "PL"
        conjuncts = subj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 3


# === Flat structure (no nesting) ====================================


class TestFlatStructure:
    """Three-conjunct rules produce a FLAT 3-element CONJUNCTS
    set, NOT a nested binary structure
    ``CONJUNCTS={(Maria, Juan), Pedro}``. Each top-level
    conjunct is its own f-structure with its own LEMMA / CASE /
    MARKER, no embedded CONJUNCTS."""

    def test_no_nested_conjuncts(self) -> None:
        parses = parse_text("Kumain si Maria, si Juan, at si Pedro.")
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        conjuncts = subj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        # Each top-level conjunct must NOT itself carry a
        # CONJUNCTS feature (no nesting).
        for c in conjuncts:
            assert c.feats.get("CONJUNCTS") is None
            # Each is a regular NOUN/proper-name f-structure.
            assert c.feats.get("LEMMA") is not None
            assert c.feats.get("CASE") == "NOM"


# === C-tree shape ===================================================


class TestCTreeShape:
    """Oxford form has a 6-daughter coord-NP node;
    non-Oxford form has a 5-daughter coord-NP node."""

    def test_oxford_six_daughters(self) -> None:
        parses = parse_text("Kumain si Maria, si Juan, at si Pedro.")
        ctree, _fs, _astr, _diags = parses[0]

        def find_coord_np(n):
            if (
                n.label.startswith("NP[CASE=NOM]")
                and len(n.children) == 6
            ):
                return n
            for c in n.children:
                got = find_coord_np(c)
                if got is not None:
                    return got
            return None

        coord_np = find_coord_np(ctree)
        assert coord_np is not None, (
            "expected a 6-daughter coord-NP node (Oxford form)"
        )
        labels = [c.label for c in coord_np.children]
        # NP, COMMA, NP, COMMA, PART, NP
        assert labels[0].startswith("NP")
        assert labels[1].startswith("PUNCT")
        assert labels[2].startswith("NP")
        assert labels[3].startswith("PUNCT")
        assert labels[4].startswith("PART")
        assert labels[5].startswith("NP")

    def test_non_oxford_five_daughters(self) -> None:
        parses = parse_text("Kumain si Maria, si Juan at si Pedro.")
        ctree, _fs, _astr, _diags = parses[0]

        def find_coord_np(n):
            if (
                n.label.startswith("NP[CASE=NOM]")
                and len(n.children) == 5
            ):
                return n
            for c in n.children:
                got = find_coord_np(c)
                if got is not None:
                    return got
            return None

        coord_np = find_coord_np(ctree)
        assert coord_np is not None, (
            "expected a 5-daughter coord-NP node (non-Oxford form)"
        )
        labels = [c.label for c in coord_np.children]
        # NP, COMMA, NP, PART, NP
        assert labels[0].startswith("NP")
        assert labels[1].startswith("PUNCT")
        assert labels[2].startswith("NP")
        assert labels[3].startswith("PART")
        assert labels[4].startswith("NP")


# === Composition with ADJ-pred + negation ===========================


class TestCompositions:
    """3-conjunct coord composes with predicative-ADJ (Phase 5g)
    and hindi-negation (Phase 4 §7.2) unchanged."""

    def test_predicative_adj_three_conjunct(self) -> None:
        parses = parse_text("Matanda si Maria, si Juan, at si Pedro.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith("ADJ")
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        conjuncts = subj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 3

    def test_negation_three_conjunct(self) -> None:
        parses = parse_text("Hindi kumain si Maria, si Juan, at si Pedro.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("POLARITY") == "NEG"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        conjuncts = subj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 3


# === Pinned 0-parses (deferred to Phase 5k follow-on) ===============


class TestDeferredArities:
    """The plan-of-record §5.3 / §9.2 defers disjunctive 3-conjunct
    (``Maria, Juan, o Pedro``) and 4+-conjunct constructions to a
    Phase 5k follow-on. These tests pin the 0-parse state so future
    follow-on work flips the assertion when the rules land."""

    @pytest.mark.parametrize("sentence", [
        # Disjunctive 3-conjunct — only AND form added in Commit 4.
        "Kumain si Maria, si Juan, o si Pedro.",
        # 4-conjunct flat — deferred to right-recursion follow-on.
        "Kumain si Maria, si Juan, si Pedro, at si Wendy.",
    ])
    def test_deferred_arities_zero_parse(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 0, (
            f"{sentence!r} now parses — Phase 5k follow-on may have "
            f"landed disjunctive 3-conjunct or 4+-conjunct support. "
            f"Update this test and add positive tests for the new "
            f"rule shape."
        )
