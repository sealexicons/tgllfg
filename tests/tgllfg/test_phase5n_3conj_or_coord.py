"""Phase 5n.A Commit 20 — disjunctive 3-conjunct flat NP coord (§18 L86).

The Phase 5k Commit 4 3-conjunct rules covered AND only; this commit
adds the parallel ``PART[COORD=OR]`` form across NOM/GEN/DAT × Oxford
and non-Oxford comma conventions, closing the §18 L86 deferral.

Surface examples:

    Kumain si Maria, si Juan, o si Pedro.   NOM-coord SUBJ (Oxford)
    Kumain si Maria, si Juan o si Pedro.    NOM-coord SUBJ (non-Oxford)
    Bumili ako ng aklat, ng lapis, o ng papel.   GEN-coord OBJ
    Pumunta si Maria sa palengke, sa bahay o sa simbahan.  DAT-coord ADJUNCT

NUM percolation mirrors the binary OR rule — ``(↑ NUM) = ↓1 NUM``
(one underspecified referent) — distinct from AND's
``(↑ NUM) = 'PL'`` (n referents).
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Oxford-comma form (6 daughters) =================================


class TestOxfordCommaThreeConjunctOR:
    """``Maria, Juan, o Pedro`` — Oxford-comma disjunctive form."""

    def test_nom_three_conjunct_oxford(self) -> None:
        parses = parse_text("Kumain si Maria, si Juan, o si Pedro.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "OR"
        assert subj.feats.get("CASE") == "NOM"
        # Disjunctive NUM is underspecified (not forced PL).
        assert subj.feats.get("NUM") != "PL"
        conjuncts = subj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 3
        lemmas = {c.feats.get("LEMMA") for c in conjuncts}
        assert lemmas == {"maria", "juan", "pedro"}

    def test_gen_three_conjunct_oxford(self) -> None:
        parses = parse_text(
            "Bumili ako ng aklat, ng lapis, o ng papel."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        obj = fs.feats.get("OBJ")
        assert obj is not None
        assert obj.feats.get("COORD") == "OR"
        assert obj.feats.get("CASE") == "GEN"
        assert obj.feats.get("NUM") != "PL"
        conjuncts = obj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 3
        lemmas = {c.feats.get("LEMMA") for c in conjuncts}
        assert lemmas == {"aklat", "lapis", "papel"}

    def test_dat_three_conjunct_oxford(self) -> None:
        parses = parse_text(
            "Pumunta si Maria sa palengke, sa bahay, o sa simbahan."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        adjuncts = fs.feats.get("ADJUNCT")
        assert adjuncts is not None
        coord_adjuncts = [
            a for a in adjuncts if a.feats.get("COORD") == "OR"
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


class TestNonOxfordThreeConjunctOR:
    """``Maria, Juan o Pedro`` — non-Oxford disjunctive form."""

    def test_nom_three_conjunct_non_oxford(self) -> None:
        parses = parse_text("Kumain si Maria, si Juan o si Pedro.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "OR"
        assert subj.feats.get("CASE") == "NOM"
        assert subj.feats.get("NUM") != "PL"
        conjuncts = subj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 3


# === Flat structure (no nesting) ====================================


class TestFlatStructureOR:
    """Three-conjunct OR rules produce a FLAT 3-element CONJUNCTS
    set, NOT a nested binary structure."""

    def test_no_nested_conjuncts(self) -> None:
        parses = parse_text("Kumain si Maria, si Juan, o si Pedro.")
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        conjuncts = subj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        for c in conjuncts:
            assert c.feats.get("CONJUNCTS") is None
            assert c.feats.get("LEMMA") is not None
            assert c.feats.get("CASE") == "NOM"


# === C-tree shape ===================================================


class TestCTreeShapeOR:
    """Oxford form has a 6-daughter coord-NP node; non-Oxford form
    has a 5-daughter coord-NP node."""

    def test_oxford_six_daughters(self) -> None:
        parses = parse_text("Kumain si Maria, si Juan, o si Pedro.")
        ctree, _fs, _astr, _diags = parses[0]

        def find_coord_np(n):
            if (
                n.label.startswith("NP[CASE=NOM")
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
            "expected a 6-daughter coord-NP node (Oxford OR form)"
        )
        labels = [c.label for c in coord_np.children]
        assert labels[0].startswith("NP")
        assert labels[1].startswith("PUNCT")
        assert labels[2].startswith("NP")
        assert labels[3].startswith("PUNCT")
        assert labels[4].startswith("PART")
        assert labels[5].startswith("NP")

    def test_non_oxford_five_daughters(self) -> None:
        parses = parse_text("Kumain si Maria, si Juan o si Pedro.")
        ctree, _fs, _astr, _diags = parses[0]

        def find_coord_np(n):
            if (
                n.label.startswith("NP[CASE=NOM")
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
            "expected a 5-daughter coord-NP node (non-Oxford OR form)"
        )
        labels = [c.label for c in coord_np.children]
        assert labels[0].startswith("NP")
        assert labels[1].startswith("PUNCT")
        assert labels[2].startswith("NP")
        assert labels[3].startswith("PART")
        assert labels[4].startswith("NP")


# === Composition with ADJ-pred + negation ===========================


class TestCompositionsOR:
    """3-conjunct OR coord composes with predicative-ADJ (Phase 5g)
    and hindi-negation (Phase 4 §7.2) unchanged."""

    def test_predicative_adj_three_conjunct(self) -> None:
        parses = parse_text("Matanda si Maria, si Juan, o si Pedro.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith("ADJ")
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "OR"
        conjuncts = subj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 3

    def test_negation_three_conjunct(self) -> None:
        parses = parse_text(
            "Hindi kumain si Maria, si Juan, o si Pedro."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("POLARITY") == "NEG"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "OR"
        conjuncts = subj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 3


# === AND-form regression (Phase 5k Commit 4) ========================


class TestAndFormRegression:
    """The Phase 5k Commit 4 3-conjunct AND form continues to fire
    after the Commit 20 OR generalization."""

    @pytest.mark.parametrize("sentence", [
        "Kumain si Maria, si Juan, at si Pedro.",
        "Kumain si Maria, si Juan at si Pedro.",
    ])
    def test_3_conjunct_and_still_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "AND"
        assert subj.feats.get("NUM") == "PL"
        conjuncts = subj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 3


# === Binary-OR regression (Phase 5k Commit 1) =======================


class TestBinaryOrRegression:
    """The binary disjunctive NP coord rule continues to fire after
    the 3-conjunct OR generalization."""

    def test_binary_or_still_parses(self) -> None:
        parses = parse_text("Kumain si Maria o si Juan.")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "OR"
        assert subj.feats.get("NUM") != "PL"
        conjuncts = subj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2
