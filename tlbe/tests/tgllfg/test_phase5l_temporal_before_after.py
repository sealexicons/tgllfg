# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5l Commit 6: temporal subordination — bago / pagkatapos.

Roadmap §12.1 / plan-of-record §5.3, §6 Commit 6. Two new rules
in ``cfg/subordination.py``:

    SubordClause → PART[COMP_TYPE=TEMP_BEFORE] S    (bago)
    SubordClause → PART[COMP_TYPE=TEMP_AFTER] S     (pagkatapos)

Both feed the existing SUBORD_TYPE-agnostic matrix-attachment
rules from Commit 2. Each TEMP_<X> SUBORD_TYPE marks the
temporal relation between matrix and embedded clause:
TEMP_BEFORE for ``bago``, TEMP_AFTER for ``pagkatapos``.

End-to-end target sentences:

    Bago kumain si Maria, pumunta si Juan.
        # "Before Maria ate, Juan went."
    Pumunta si Juan bago kumain si Maria.
        # "Juan went before Maria ate."
    Pagkatapos kumain si Maria, pumunta si Juan.
        # "After Maria ate, Juan went."
    Pumunta si Juan pagkatapos kumain si Maria.
        # "Juan went after Maria ate."
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


# === bago — TEMP_BEFORE ===============================================


class TestBagoBefore:
    """``bago`` "before" embeds a clause as a temporal-before
    adjunct. SUBORD_TYPE=TEMP_BEFORE."""

    def test_bago_pre_matrix(self) -> None:
        parses = parse_text("Bago kumain si Maria, pumunta si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith("PUNTA")
        before = _adjunct_with_subord_type(fs, "TEMP_BEFORE")
        assert before is not None
        assert (before.feats.get("PRED") or "").startswith("EAT")

    def test_bago_post_matrix(self) -> None:
        parses = parse_text("Pumunta si Juan bago kumain si Maria.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith("PUNTA")
        before = _adjunct_with_subord_type(fs, "TEMP_BEFORE")
        assert before is not None
        assert (before.feats.get("PRED") or "").startswith("EAT")

    def test_bago_pre_post_same_fstruct(self) -> None:
        pre = parse_text("Bago kumain si Maria, pumunta si Juan.")[0][1]
        post = parse_text("Pumunta si Juan bago kumain si Maria.")[0][1]
        pre_b = _adjunct_with_subord_type(pre, "TEMP_BEFORE")
        post_b = _adjunct_with_subord_type(post, "TEMP_BEFORE")
        assert pre_b is not None and post_b is not None
        assert (pre_b.feats.get("PRED") or "")[:3] == (
            post_b.feats.get("PRED") or ""
        )[:3]


# === pagkatapos — TEMP_AFTER ==========================================


class TestPagkatapostAfter:
    """``pagkatapos`` "after" embeds a clause as a temporal-after
    adjunct. SUBORD_TYPE=TEMP_AFTER."""

    def test_pagkatapos_pre_matrix(self) -> None:
        parses = parse_text(
            "Pagkatapos kumain si Maria, pumunta si Juan."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith("PUNTA")
        after = _adjunct_with_subord_type(fs, "TEMP_AFTER")
        assert after is not None
        assert (after.feats.get("PRED") or "").startswith("EAT")

    def test_pagkatapos_post_matrix(self) -> None:
        parses = parse_text(
            "Pumunta si Juan pagkatapos kumain si Maria."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith("PUNTA")
        after = _adjunct_with_subord_type(fs, "TEMP_AFTER")
        assert after is not None
        assert (after.feats.get("PRED") or "").startswith("EAT")


# === TEMP × negation ==================================================


class TestNegatedInnerTemporal:
    """Inner clause of a TEMP_<X> subord can be negated."""

    def test_bago_negated_inner(self) -> None:
        parses = parse_text(
            "Bago hindi kumain si Maria, pumunta si Juan."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        before = _adjunct_with_subord_type(fs, "TEMP_BEFORE")
        assert before is not None
        assert before.feats.get("POLARITY") == "NEG"


class TestNegatedMatrixTemporal:
    """Matrix-clause negation composes orthogonally with TEMP_<X>."""

    def test_bago_negated_matrix(self) -> None:
        parses = parse_text(
            "Hindi pumunta si Juan bago kumain si Maria."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("POLARITY") == "NEG"
        before = _adjunct_with_subord_type(fs, "TEMP_BEFORE")
        assert before is not None
        assert before.feats.get("POLARITY") != "NEG"


# === TEMP × NP-coord inside ===========================================


class TestNPCoordInsideTemporal:
    """Phase 5k NP-coord SUBJ inside a temporal clause."""

    def test_pagkatapos_inner_np_coord(self) -> None:
        parses = parse_text(
            "Pagkatapos kumain si Maria at si Juan, pumunta si Pedro."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        after = _adjunct_with_subord_type(fs, "TEMP_AFTER")
        assert after is not None
        inner_subj = after.feats.get("SUBJ")
        assert inner_subj is not None
        assert inner_subj.feats.get("COORD") == "AND"


# === TEMP_BEFORE / TEMP_AFTER / COND / CONC are pairwise disjoint ====


class TestSubordTypeDisjoint:
    """Each subord-type-keyed adjunct is the only one of its kind
    on the matrix; bago/pagkatapos do not produce COND/CONC
    artifacts and vice versa."""

    def test_bago_only_temp_before(self) -> None:
        parses = parse_text("Bago kumain si Maria, pumunta si Juan.")
        _ct, fs, _astr, _diags = parses[0]
        assert _adjunct_with_subord_type(fs, "TEMP_BEFORE") is not None
        assert _adjunct_with_subord_type(fs, "TEMP_AFTER") is None
        assert _adjunct_with_subord_type(fs, "COND") is None
        assert _adjunct_with_subord_type(fs, "CONC") is None

    def test_pagkatapos_only_temp_after(self) -> None:
        parses = parse_text(
            "Pagkatapos kumain si Maria, pumunta si Juan."
        )
        _ct, fs, _astr, _diags = parses[0]
        assert _adjunct_with_subord_type(fs, "TEMP_AFTER") is not None
        assert _adjunct_with_subord_type(fs, "TEMP_BEFORE") is None
        assert _adjunct_with_subord_type(fs, "COND") is None


# === C-tree shape =====================================================


class TestCTreeShape:
    """Same daughter-count invariants as Commit 2 / 4 — pre-matrix
    has SubordClause + PUNCT + S; post-matrix has S + SubordClause."""

    def test_pre_matrix_three_daughters(self) -> None:
        parses = parse_text("Bago kumain si Maria, pumunta si Juan.")
        ctree, _fs, _astr, _diags = parses[0]
        labels = [c.label for c in ctree.children]
        assert labels[0].startswith("SubordClause")
        assert labels[1].startswith("PUNCT")
        assert labels[2].startswith("S")

    def test_post_matrix_two_daughters(self) -> None:
        parses = parse_text(
            "Pumunta si Juan pagkatapos kumain si Maria."
        )
        ctree, _fs, _astr, _diags = parses[0]
        labels = [c.label for c in ctree.children]
        assert labels[0].startswith("S")
        assert labels[1].startswith("SubordClause")
