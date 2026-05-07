"""Phase 5l Commit 9: reason subordination — dahil clausal.

Roadmap §12.1 / plan-of-record §5.5, §6 Commit 9. One new rule
in ``cfg/subordination.py``:

    SubordClause → PART[COMP_TYPE=REAS] S       (builder)

``dahil`` is polysemous with the Phase 5e PREP[REASON] entry
(``dahil sa NP`` "because of X"). Same disambiguation mechanic
as ``para`` (Commit 8): chart picks per immediate constituent —
PREP path takes a DAT-NP, PART path takes an S.

End-to-end target sentences:

    Pumunta si Juan dahil kumain si Maria.
        # "Juan went because Maria ate."          (post-matrix)
    Dahil kumain si Maria, pumunta si Juan.
        # "Because Maria ate, Juan went."          (pre-matrix)
"""

from __future__ import annotations

from tgllfg.core.pipeline import parse_text


def _adjunct_with_subord_type(fs, subord_type: str):
    adjuncts = fs.feats.get("ADJUNCT")
    if adjuncts is None:
        return None
    for adj in adjuncts:
        if adj.feats.get("SUBORD_TYPE") == subord_type:
            return adj
    return None


# === dahil — REAS ====================================================


class TestDahilReason:
    """``dahil`` "because" embeds a clause as a reason adjunct.
    SUBORD_TYPE=REAS."""

    def test_dahil_post_matrix(self) -> None:
        parses = parse_text("Pumunta si Juan dahil kumain si Maria.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith("PUNTA")
        reason = _adjunct_with_subord_type(fs, "REAS")
        assert reason is not None
        assert (reason.feats.get("PRED") or "").startswith("EAT")

    def test_dahil_pre_matrix(self) -> None:
        parses = parse_text("Dahil kumain si Maria, pumunta si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        reason = _adjunct_with_subord_type(fs, "REAS")
        assert reason is not None
        assert (reason.feats.get("PRED") or "").startswith("EAT")

    def test_dahil_pre_post_same_fstruct(self) -> None:
        pre = parse_text("Dahil kumain si Maria, pumunta si Juan.")[0][1]
        post = parse_text("Pumunta si Juan dahil kumain si Maria.")[0][1]
        pre_r = _adjunct_with_subord_type(pre, "REAS")
        post_r = _adjunct_with_subord_type(post, "REAS")
        assert pre_r is not None and post_r is not None
        assert (pre_r.feats.get("PRED") or "")[:3] == (
            post_r.feats.get("PRED") or ""
        )[:3]


# === dahil PREP/PART polysemy ========================================


class TestDahilPolysemy:
    """``dahil`` carries both readings in the lex; the grammar
    consumes the right one per immediate constituent."""

    def test_dahil_part_consumed_in_subord_context(self) -> None:
        parses = parse_text("Pumunta si Juan dahil kumain si Maria.")
        _ct, fs, _astr, _diags = parses[0]
        reason = _adjunct_with_subord_type(fs, "REAS")
        assert reason is not None
        # No PREP_TYPE=REASON artifact on matrix or adjunct.
        assert fs.feats.get("PREP_TYPE") != "REASON"
        assert reason.feats.get("PREP_TYPE") != "REASON"


# === REAS × negation =================================================


class TestNegatedInnerReason:
    """Inner clause of a REAS subord can be negated."""

    def test_dahil_negated_inner(self) -> None:
        parses = parse_text(
            "Pumunta si Juan dahil hindi kumain si Maria."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        reason = _adjunct_with_subord_type(fs, "REAS")
        assert reason is not None
        assert reason.feats.get("POLARITY") == "NEG"


class TestNegatedMatrixReason:
    """Matrix-clause negation composes orthogonally with REAS."""

    def test_dahil_negated_matrix(self) -> None:
        parses = parse_text(
            "Hindi pumunta si Juan dahil kumain si Maria."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("POLARITY") == "NEG"
        reason = _adjunct_with_subord_type(fs, "REAS")
        assert reason is not None
        assert reason.feats.get("POLARITY") != "NEG"


# === SUBORD_TYPE disjointness ========================================


class TestSubordTypeDisjoint:
    """REAS doesn't leak to other SUBORD_TYPEs."""

    def test_dahil_only_reas(self) -> None:
        parses = parse_text("Pumunta si Juan dahil kumain si Maria.")
        _ct, fs, _astr, _diags = parses[0]
        assert _adjunct_with_subord_type(fs, "REAS") is not None
        for other in ("COND", "CONC", "TEMP_BEFORE", "TEMP_AFTER",
                      "TEMP_WHILE", "TEMP_UNTIL", "TEMP_SINCE",
                      "PURP"):
            assert _adjunct_with_subord_type(fs, other) is None


# === C-tree shape ====================================================


class TestCTreeShape:
    """Pre-matrix has 3 daughters; post-matrix has 2."""

    def test_dahil_post_matrix_two_daughters(self) -> None:
        parses = parse_text("Pumunta si Juan dahil kumain si Maria.")
        ctree, _fs, _astr, _diags = parses[0]
        labels = [c.label for c in ctree.children]
        assert labels[0].startswith("S")
        assert labels[1].startswith("SubordClause")

    def test_dahil_pre_matrix_three_daughters(self) -> None:
        parses = parse_text("Dahil kumain si Maria, pumunta si Juan.")
        ctree, _fs, _astr, _diags = parses[0]
        labels = [c.label for c in ctree.children]
        assert labels[0].startswith("SubordClause")
        assert labels[1].startswith("PUNCT")
        assert labels[2].startswith("S")


# === NP-coord inside =================================================


class TestNPCoordInsideReas:
    """Phase 5k NP-coord SUBJ inside a reason clause."""

    def test_dahil_inner_np_coord(self) -> None:
        parses = parse_text(
            "Pumunta si Juan dahil kumain si Maria at si Pedro."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        reason = _adjunct_with_subord_type(fs, "REAS")
        assert reason is not None
        inner_subj = reason.feats.get("SUBJ")
        assert inner_subj is not None
        assert inner_subj.feats.get("COORD") == "AND"
