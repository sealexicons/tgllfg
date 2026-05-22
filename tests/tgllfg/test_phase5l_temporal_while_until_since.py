# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5l Commit 7: temporal subordination — habang / hanggang / mula nang.

Roadmap §12.1 / plan-of-record §5.3, §6 Commit 7. Three new
rules in ``cfg/subordination.py``, completing the temporal
subord-type family started in Commit 6:

    SubordClause → PART[COMP_TYPE=TEMP_WHILE] S      (habang)
    SubordClause → PART[COMP_TYPE=TEMP_UNTIL] S      (hanggang)
    SubordClause → PREP[PREP_TYPE=SOURCE]            (mula nang;
                   PART[COMP_TYPE=TEMP_SINCE] S       multi-word)

The ``mula nang`` rule reuses the existing Phase 5e ``mula``
PREP entry (PREP_TYPE=SOURCE) — no new lex for mula. The
multi-word shape is structurally distinct from ``mula sa NP``
(the PP source) so the chart disambiguates by constituent type.

End-to-end target sentences:

    Habang kumain si Maria, pumunta si Juan.
        # "While Maria ate, Juan went."          (TEMP_WHILE)
    Pumunta si Juan habang kumain si Maria.
        # "Juan went while Maria ate."
    Hanggang pumunta si Maria, kumain si Juan.
        # "Until Maria went, Juan ate."          (TEMP_UNTIL)
    Mula nang kumain si Maria, pumunta si Juan.
        # "Since Maria ate, Juan went."          (TEMP_SINCE)
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


# === habang — TEMP_WHILE ==============================================


class TestHabangWhile:
    """``habang`` "while" embeds a clause as a temporal-while
    adjunct. SUBORD_TYPE=TEMP_WHILE."""

    def test_habang_pre_matrix(self) -> None:
        parses = parse_text("Habang kumain si Maria, pumunta si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith("PUNTA")
        whilst = _adjunct_with_subord_type(fs, "TEMP_WHILE")
        assert whilst is not None
        assert (whilst.feats.get("PRED") or "").startswith("EAT")

    def test_habang_post_matrix(self) -> None:
        parses = parse_text("Pumunta si Juan habang kumain si Maria.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        whilst = _adjunct_with_subord_type(fs, "TEMP_WHILE")
        assert whilst is not None

    def test_habang_pre_post_same_fstruct(self) -> None:
        pre = parse_text("Habang kumain si Maria, pumunta si Juan.")[0][1]
        post = parse_text("Pumunta si Juan habang kumain si Maria.")[0][1]
        pre_w = _adjunct_with_subord_type(pre, "TEMP_WHILE")
        post_w = _adjunct_with_subord_type(post, "TEMP_WHILE")
        assert pre_w is not None and post_w is not None
        assert (pre_w.feats.get("PRED") or "")[:3] == (
            post_w.feats.get("PRED") or ""
        )[:3]


# === hanggang — TEMP_UNTIL ============================================


class TestHanggangUntil:
    """``hanggang`` "until" embeds a clause as a temporal-until
    adjunct. SUBORD_TYPE=TEMP_UNTIL."""

    def test_hanggang_pre_matrix(self) -> None:
        parses = parse_text("Hanggang pumunta si Maria, kumain si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        until = _adjunct_with_subord_type(fs, "TEMP_UNTIL")
        assert until is not None
        assert (until.feats.get("PRED") or "").startswith("PUNTA")

    def test_hanggang_post_matrix(self) -> None:
        parses = parse_text("Kumain si Juan hanggang pumunta si Maria.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        until = _adjunct_with_subord_type(fs, "TEMP_UNTIL")
        assert until is not None


# === mula nang — TEMP_SINCE ===========================================


class TestMulaNangSince:
    """``mula nang`` "since" is a multi-word subordinator —
    PREP[mula] + PART[nang TEMP_SINCE] + S. The chart consumes
    both PREP and PART daughters structurally."""

    def test_mula_nang_pre_matrix(self) -> None:
        parses = parse_text(
            "Mula nang kumain si Maria, pumunta si Juan."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        since = _adjunct_with_subord_type(fs, "TEMP_SINCE")
        assert since is not None
        assert (since.feats.get("PRED") or "").startswith("EAT")

    def test_mula_nang_post_matrix(self) -> None:
        parses = parse_text(
            "Pumunta si Juan mula nang kumain si Maria."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        since = _adjunct_with_subord_type(fs, "TEMP_SINCE")
        assert since is not None

    def test_mula_nang_three_daughter_subord_clause(self) -> None:
        """The SubordClause node for ``mula nang S`` has 3
        daughters (PREP + PART + S), unlike single-word
        subordinators which have 2 (PART + S)."""
        parses = parse_text(
            "Pumunta si Juan mula nang kumain si Maria."
        )
        ctree, _fs, _astr, _diags = parses[0]
        # Top is post-matrix attachment: [S, SubordClause].
        sub = next(
            c for c in ctree.children
            if c.label.startswith("SubordClause")
        )
        labels = [c.label for c in sub.children]
        assert len(labels) == 3
        assert labels[0].startswith("PREP")
        assert labels[1].startswith("PART")
        assert labels[2].startswith("S")


# === TEMP × negation ==================================================


class TestNegatedInner:
    """Inner clause of a TEMP_<X> subord can be negated."""

    def test_habang_negated_inner(self) -> None:
        parses = parse_text(
            "Habang hindi kumain si Maria, pumunta si Juan."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        whilst = _adjunct_with_subord_type(fs, "TEMP_WHILE")
        assert whilst is not None
        assert whilst.feats.get("POLARITY") == "NEG"


class TestNegatedMatrix:
    """Matrix-clause negation composes orthogonally with TEMP_<X>."""

    def test_hanggang_negated_matrix(self) -> None:
        parses = parse_text(
            "Hindi kumain si Juan hanggang pumunta si Maria."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("POLARITY") == "NEG"
        until = _adjunct_with_subord_type(fs, "TEMP_UNTIL")
        assert until is not None
        assert until.feats.get("POLARITY") != "NEG"


# === TEMP × NP-coord inside ===========================================


class TestNPCoordInside:
    """Phase 5k NP-coord SUBJ inside a habang clause."""

    def test_habang_inner_np_coord(self) -> None:
        parses = parse_text(
            "Habang kumain si Maria at si Juan, pumunta si Pedro."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        whilst = _adjunct_with_subord_type(fs, "TEMP_WHILE")
        assert whilst is not None
        inner_subj = whilst.feats.get("SUBJ")
        assert inner_subj is not None
        assert inner_subj.feats.get("COORD") == "AND"


# === SUBORD_TYPE disjointness =========================================


class TestSubordTypeDisjoint:
    """The five temporal SUBORD_TYPEs and the COND/CONC types are
    pairwise disjoint on a single sentence's adjuncts."""

    def test_habang_only_temp_while(self) -> None:
        parses = parse_text("Habang kumain si Maria, pumunta si Juan.")
        _ct, fs, _astr, _diags = parses[0]
        assert _adjunct_with_subord_type(fs, "TEMP_WHILE") is not None
        for other in ("TEMP_BEFORE", "TEMP_AFTER", "TEMP_UNTIL",
                      "TEMP_SINCE", "COND", "CONC"):
            assert _adjunct_with_subord_type(fs, other) is None

    def test_mula_nang_only_temp_since(self) -> None:
        parses = parse_text(
            "Mula nang kumain si Maria, pumunta si Juan."
        )
        _ct, fs, _astr, _diags = parses[0]
        assert _adjunct_with_subord_type(fs, "TEMP_SINCE") is not None
        for other in ("TEMP_BEFORE", "TEMP_AFTER", "TEMP_WHILE",
                      "TEMP_UNTIL", "COND", "CONC"):
            assert _adjunct_with_subord_type(fs, other) is None


# === C-tree shape =====================================================


class TestCTreeShape:
    """Pre/post matrix attachment shapes match the Commits 2/4/6
    invariants. The mula-nang rule changes the SubordClause's
    INTERNAL daughter count (3 vs 2) but not the matrix's."""

    def test_habang_post_matrix_two_daughters(self) -> None:
        parses = parse_text("Pumunta si Juan habang kumain si Maria.")
        ctree, _fs, _astr, _diags = parses[0]
        labels = [c.label for c in ctree.children]
        assert labels[0].startswith("S")
        assert labels[1].startswith("SubordClause")

    def test_mula_nang_pre_matrix_three_top_level(self) -> None:
        parses = parse_text(
            "Mula nang kumain si Maria, pumunta si Juan."
        )
        ctree, _fs, _astr, _diags = parses[0]
        labels = [c.label for c in ctree.children]
        # Top-level is still SubordClause + PUNCT + S (3 daughters);
        # the multi-word shape lives INSIDE the SubordClause.
        assert labels[0].startswith("SubordClause")
        assert labels[1].startswith("PUNCT")
        assert labels[2].startswith("S")
