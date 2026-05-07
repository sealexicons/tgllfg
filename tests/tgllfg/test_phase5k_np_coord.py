"""Phase 5k Commit 3: binary NP coordination — at / o.

Roadmap §12.1 / plan-of-record §5.1, §5.2, §6 Commit 3. Six new
rules in ``cfg/coordination.py`` (new module):

    NP[CASE=X] → NP[CASE=X] PART[COORD=AND] NP[CASE=X]
    NP[CASE=X] → NP[CASE=X] PART[COORD=OR]  NP[CASE=X]

for each X ∈ {NOM, GEN, DAT}.

Both conjuncts must share CASE — enforced structurally by the
parallel category-pattern daughters; mismatched-CASE coord
sentences fail at the chart layer with no rule firing. The
matrix is a fresh f-structure: neither conjunct IS the matrix,
both are ELEMENTS of the CONJUNCTS set. Non-distributive features
(COORD, NUM=PL for additive, CASE) live on the matrix.

Additive ``at`` forces NUM=PL on the matrix (semantically two-
or-more); disjunctive ``o`` percolates NUM from the first
conjunct (``Maria o Juan`` is sg-with-disjunct).

End-to-end target sentences:

    Kumain si Maria at si Juan.            NOM-coord SUBJ
    Kumain si Maria o si Juan.             NOM-coord disjunctive
    Kumain ng aklat at ng lapis si Maria.  GEN-coord OBJ
    Pumunta si Maria sa palengke at sa bahay.  DAT-coord ADJUNCT
    Matanda si Maria at si Juan.           ADJ-pred + NOM coord
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === NOM-coord (SUBJ position) =======================================


class TestNomCoordAdditive:
    """``Si Maria at si Juan`` as the SUBJ of a verbal clause —
    additive NOM coord with NUM=PL on the matrix."""

    def test_kumain_si_maria_at_si_juan(self) -> None:
        parses = parse_text("Kumain si Maria at si Juan.")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "AND"
        assert subj.feats.get("CASE") == "NOM"
        assert subj.feats.get("NUM") == "PL"

    def test_subj_carries_two_conjuncts_in_set(self) -> None:
        parses = parse_text("Kumain si Maria at si Juan.")
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        conjuncts = subj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2
        lemmas = {c.feats.get("LEMMA") for c in conjuncts}
        assert lemmas == {"maria", "juan"}

    def test_subj_no_pred_on_coord_matrix(self) -> None:
        """Coord matrix is non-predicational — no PRED on the
        matrix coord SUBJ; PRED lives on each individual conjunct."""
        parses = parse_text("Kumain si Maria at si Juan.")
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        # The matrix has no PRED slot on the coord NP itself.
        assert subj.feats.get("PRED") is None

    def test_each_conjunct_retains_own_case_marker(self) -> None:
        """Each conjunct in CONJUNCTS retains its own MARKER (si)
        — the matrix doesn't strip per-conjunct lex feats."""
        parses = parse_text("Kumain si Maria at si Juan.")
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        conjuncts = subj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        for conj in conjuncts:
            assert conj.feats.get("CASE") == "NOM"
            assert conj.feats.get("MARKER") == "SI"


class TestNomCoordDisjunctive:
    """``Si Maria o si Juan`` — disjunctive NOM coord; NUM
    percolates from the first conjunct (not forced to PL)."""

    def test_kumain_si_maria_o_si_juan(self) -> None:
        parses = parse_text("Kumain si Maria o si Juan.")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "OR"
        assert subj.feats.get("CASE") == "NOM"
        # NUM is left empty when the first conjunct doesn't carry NUM
        # — the percolation `↓1 NUM` resolves to no value, which is
        # the correct underspecified behavior for a disjunct of two
        # singular proper names.
        assert subj.feats.get("NUM") != "PL"

    def test_subj_carries_two_conjuncts(self) -> None:
        parses = parse_text("Kumain si Maria o si Juan.")
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        conjuncts = subj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2


# === GEN-coord (OBJ position) ========================================


class TestGenCoordAdditive:
    """``ng aklat at ng lapis`` as the OBJ of an AV verb —
    additive GEN coord."""

    def test_kumain_ng_aklat_at_ng_lapis(self) -> None:
        parses = parse_text("Kumain ng aklat at ng lapis si Maria.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        obj = fs.feats.get("OBJ")
        assert obj is not None
        assert obj.feats.get("COORD") == "AND"
        assert obj.feats.get("CASE") == "GEN"
        assert obj.feats.get("NUM") == "PL"

    def test_gen_coord_conjuncts(self) -> None:
        parses = parse_text("Kumain ng aklat at ng lapis si Maria.")
        _ct, fs, _astr, _diags = parses[0]
        obj = fs.feats.get("OBJ")
        assert obj is not None
        conjuncts = obj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2
        lemmas = {c.feats.get("LEMMA") for c in conjuncts}
        assert lemmas == {"aklat", "lapis"}
        for c in conjuncts:
            assert c.feats.get("CASE") == "GEN"
            assert c.feats.get("MARKER") == "NG"


# === DAT-coord (ADJUNCT position) ====================================


class TestDatCoordAdditive:
    """``sa palengke at sa bahay`` as a sa-PP ADJUNCT —
    additive DAT coord composed with the existing Phase 4 §7.7
    sa-PP machinery."""

    def test_pumunta_sa_palengke_at_sa_bahay(self) -> None:
        parses = parse_text("Pumunta si Maria sa palengke at sa bahay.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        adjuncts = fs.feats.get("ADJUNCT")
        assert adjuncts is not None
        # The single ADJUNCT element is the coord-DAT NP.
        coord_adjuncts = [
            a for a in adjuncts if a.feats.get("COORD") == "AND"
        ]
        assert len(coord_adjuncts) == 1
        coord = coord_adjuncts[0]
        assert coord.feats.get("CASE") == "DAT"
        assert coord.feats.get("NUM") == "PL"

    def test_dat_coord_conjuncts(self) -> None:
        parses = parse_text("Pumunta si Maria sa palengke at sa bahay.")
        _ct, fs, _astr, _diags = parses[0]
        adjuncts = fs.feats.get("ADJUNCT")
        assert adjuncts is not None
        coord = next(a for a in adjuncts if a.feats.get("COORD") == "AND")
        conjuncts = coord.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2
        lemmas = {c.feats.get("LEMMA") for c in conjuncts}
        assert lemmas == {"palengke", "bahay"}


# === ADJ-predicative + NOM-coord ====================================


class TestPredAdjPlusNomCoord:
    """Predicative-ADJ (Phase 5g) clause with a coord NOM SUBJ —
    composes via the existing predicative-ADJ rule plus the new
    Phase 5k Commit 3 NOM-coord rule."""

    def test_matanda_si_maria_at_si_juan(self) -> None:
        parses = parse_text("Matanda si Maria at si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # ADJ-predicative matrix.
        assert (fs.feats.get("PRED") or "").startswith("ADJ")
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "AND"
        assert subj.feats.get("NUM") == "PL"
        conjuncts = subj.feats.get("CONJUNCTS")
        assert len(conjuncts) == 2


# === Apostrophe-t pre-pass × coord ==================================


class TestApostropheTComposesWithCoord:
    """The Phase 5k Commit 2 ``'t`` pre-pass synthesizes ``at``,
    so ``Maria't Juan`` parses as ``Maria at Juan`` (subject to
    bare-name lex availability — currently ``Maria`` and ``Juan``
    require ``si`` to be NP[CASE=NOM])."""

    def test_apostrophe_t_yields_coord_subj(self) -> None:
        """``Kumain si Maria't si Juan.`` — bound 't between two
        si-marked NPs collapses to ``at``, then the NOM-coord
        rule fires."""
        parses = parse_text("Kumain si Maria't si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "AND"
        conjuncts = subj.feats.get("CONJUNCTS")
        assert len(conjuncts) == 2


# === C-tree shape ===================================================


class TestCoordCTreeShape:
    """The binary coord rule yields a 3-daughter c-tree at the
    coord-NP level: NP + PART + NP."""

    def test_nom_coord_three_daughters(self) -> None:
        parses = parse_text("Kumain si Maria at si Juan.")
        ctree, _fs, _astr, _diags = parses[0]
        # Walk the c-tree to find the coord NP node.
        def find_coord_np(n):
            if n.label.startswith("NP[CASE=NOM]") and len(n.children) == 3:
                labels = [c.label for c in n.children]
                if any(lbl.startswith("PART") for lbl in labels):
                    return n
            for c in n.children:
                got = find_coord_np(c)
                if got is not None:
                    return got
            return None

        coord_np = find_coord_np(ctree)
        assert coord_np is not None, "expected a 3-daughter coord-NP node"
        labels = [c.label for c in coord_np.children]
        assert labels[0].startswith("NP")
        assert labels[1].startswith("PART")
        assert labels[2].startswith("NP")


# === Disambiguation: AND vs OR =====================================


class TestCoordValueDisambiguation:
    """The ``=c 'AND'`` / ``=c 'OR'`` constraints + the
    daughter category patterns (PART[COORD=AND] vs PART[COORD=OR])
    ensure each rule fires on its own coordinator only — no
    cross-fire."""

    def test_at_does_not_yield_or_coord(self) -> None:
        parses = parse_text("Kumain si Maria at si Juan.")
        _ct, fs, _, _ = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "AND"
        assert subj.feats.get("COORD") != "OR"

    def test_o_does_not_yield_and_coord(self) -> None:
        parses = parse_text("Kumain si Maria o si Juan.")
        _ct, fs, _, _ = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "OR"
        assert subj.feats.get("COORD") != "AND"


# === Negation × coord (composition) =================================


class TestNegationXCoord:
    """Phase 4 §7.2 hindi-wrap composes with NOM-coord SUBJ
    unchanged — the matrix carries POLARITY=NEG and the SUBJ is
    still a coord NP."""

    @pytest.mark.parametrize("sentence", [
        "Hindi kumain si Maria at si Juan.",
        "Hindi kumain si Maria o si Juan.",
    ])
    def test_hindi_with_coord_subj(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("POLARITY") == "NEG"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") in ("AND", "OR")
        conjuncts = subj.feats.get("CONJUNCTS")
        assert len(conjuncts) == 2
