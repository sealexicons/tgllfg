# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5l Commit 8: purpose subordination — para / upang.

Roadmap §12.1 / plan-of-record §5.4, §6 Commit 8. One new rule
in ``cfg/subordination.py``:

    SubordClause → PART[COMP_TYPE=PURP] S       (builder)

Both purpose PART entries (para / upang — Commit 1 lex) feed
this single builder. ``upang`` carries REGISTER=FORMAL on its
PART f-structure; the feat percolates onto the SubordClause
f-structure via ``(↑) = ↓2``.

``para`` is polysemous with the Phase 5e PREP[BENEFICIARY]
entry (``para sa NP`` "for X"). The chart resolves by immediate
constituent — PREP path takes a DAT-NP; PART path takes an S.
The two contexts don't overlap structurally.

End-to-end target sentences:

    Pumunta si Juan para kumain si Maria.
        # "Juan went so that Maria ate."           (post-matrix para)
    Para kumain si Maria, pumunta si Juan.
        # "In order for Maria to eat, Juan went."  (pre-matrix para)
    Pumunta si Juan upang kumain si Maria.
        # "Juan went in order for Maria to eat."   (post-matrix upang)
"""

from tgllfg.core.pipeline import parse_text


def _adjunct_with_subord_type(fs, subord_type: str):
    adjuncts = fs.feats.get("ADJUNCT")
    if adjuncts is None:
        return None
    for adj in adjuncts:
        if adj.feats.get("SUBORD_TYPE") == subord_type:
            return adj
    return None


# === para — purpose ==================================================


class TestParaPurpose:
    """``para`` "in order to / so that" embeds a clause as a
    purpose adjunct. SUBORD_TYPE=PURP."""

    def test_para_post_matrix(self) -> None:
        parses = parse_text("Pumunta si Juan para kumain si Maria.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith("PUNTA")
        purp = _adjunct_with_subord_type(fs, "PURP")
        assert purp is not None
        assert (purp.feats.get("PRED") or "").startswith("EAT")

    def test_para_pre_matrix(self) -> None:
        parses = parse_text("Para kumain si Maria, pumunta si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        purp = _adjunct_with_subord_type(fs, "PURP")
        assert purp is not None
        assert (purp.feats.get("PRED") or "").startswith("EAT")

    def test_para_pre_post_same_fstruct(self) -> None:
        pre = parse_text("Para kumain si Maria, pumunta si Juan.")[0][1]
        post = parse_text("Pumunta si Juan para kumain si Maria.")[0][1]
        pre_p = _adjunct_with_subord_type(pre, "PURP")
        post_p = _adjunct_with_subord_type(post, "PURP")
        assert pre_p is not None and post_p is not None
        assert (pre_p.feats.get("PRED") or "")[:3] == (
            post_p.feats.get("PRED") or ""
        )[:3]


# === upang — formal purpose ==========================================


class TestUpangPurpose:
    """``upang`` is the formal-register variant of ``para``.
    Same syntactic distribution; carries REGISTER=FORMAL on its
    PART daughter."""

    def test_upang_post_matrix(self) -> None:
        parses = parse_text("Pumunta si Juan upang kumain si Maria.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        purp = _adjunct_with_subord_type(fs, "PURP")
        assert purp is not None
        assert (purp.feats.get("PRED") or "").startswith("EAT")

    def test_upang_pre_matrix(self) -> None:
        parses = parse_text("Upang kumain si Maria, pumunta si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        purp = _adjunct_with_subord_type(fs, "PURP")
        assert purp is not None


# === para PREP/PART polysemy ========================================


class TestParaPolysemy:
    """Both ``para[PREP]`` (Phase 5e) and ``para[PART]`` (Phase 5l)
    surface in the lex; the grammar consumes the right one per
    immediate-constituent context."""

    def test_para_part_consumed_in_subord_context(self) -> None:
        # ``para kumain si Maria`` — PART path fires (S complement),
        # produces SUBORD_TYPE=PURP on adjunct.
        parses = parse_text("Pumunta si Juan para kumain si Maria.")
        _ct, fs, _astr, _diags = parses[0]
        purp = _adjunct_with_subord_type(fs, "PURP")
        assert purp is not None
        # No PREP_TYPE=BENEFICIARY artifact on the matrix or adjunct.
        assert fs.feats.get("PREP_TYPE") != "BENEFICIARY"
        assert purp.feats.get("PREP_TYPE") != "BENEFICIARY"


# === PURP × negation =================================================


class TestNegatedInnerPurpose:
    """Inner clause of a PURP subord can be negated."""

    def test_para_negated_inner(self) -> None:
        parses = parse_text(
            "Pumunta si Juan para hindi kumain si Maria."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        purp = _adjunct_with_subord_type(fs, "PURP")
        assert purp is not None
        assert purp.feats.get("POLARITY") == "NEG"


class TestNegatedMatrixPurpose:
    """Matrix-clause negation composes orthogonally with PURP."""

    def test_para_negated_matrix(self) -> None:
        parses = parse_text(
            "Hindi pumunta si Juan para kumain si Maria."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("POLARITY") == "NEG"
        purp = _adjunct_with_subord_type(fs, "PURP")
        assert purp is not None
        assert purp.feats.get("POLARITY") != "NEG"


# === SUBORD_TYPE disjointness ========================================


class TestSubordTypeDisjoint:
    """PURP doesn't leak to other SUBORD_TYPEs."""

    def test_para_only_purp(self) -> None:
        parses = parse_text("Pumunta si Juan para kumain si Maria.")
        _ct, fs, _astr, _diags = parses[0]
        assert _adjunct_with_subord_type(fs, "PURP") is not None
        for other in ("COND", "CONC", "TEMP_BEFORE", "TEMP_AFTER",
                      "TEMP_WHILE", "TEMP_UNTIL", "TEMP_SINCE"):
            assert _adjunct_with_subord_type(fs, other) is None


# === C-tree shape ====================================================


class TestCTreeShape:
    """Pre-matrix has 3 daughters (SubordClause + PUNCT + S);
    post-matrix has 2 daughters (S + SubordClause)."""

    def test_para_post_matrix_two_daughters(self) -> None:
        parses = parse_text("Pumunta si Juan para kumain si Maria.")
        ctree, _fs, _astr, _diags = parses[0]
        labels = [c.label for c in ctree.children]
        assert labels[0].startswith("S")
        assert labels[1].startswith("SubordClause")

    def test_para_pre_matrix_three_daughters(self) -> None:
        parses = parse_text("Para kumain si Maria, pumunta si Juan.")
        ctree, _fs, _astr, _diags = parses[0]
        labels = [c.label for c in ctree.children]
        assert labels[0].startswith("SubordClause")
        assert labels[1].startswith("PUNCT")
        assert labels[2].startswith("S")


# === NP-coord inside =================================================


class TestNPCoordInsidePurp:
    """Phase 5k NP-coord SUBJ inside a purpose clause."""

    def test_para_inner_np_coord(self) -> None:
        parses = parse_text(
            "Pumunta si Juan para kumain si Maria at si Pedro."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        purp = _adjunct_with_subord_type(fs, "PURP")
        assert purp is not None
        inner_subj = purp.feats.get("SUBJ")
        assert inner_subj is not None
        assert inner_subj.feats.get("COORD") == "AND"
