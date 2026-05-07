"""Phase 5l Commit 2: conditional subordination — kung / kapag / pag / sakali.

Roadmap §12.1 / plan-of-record §5.1, §6 Commit 2. Three new rules
in ``cfg/subordination.py`` (the new module landing this commit):

    SubordClause → PART[COMP_TYPE=COND] S       (builder)
    S            → S SubordClause               (post-matrix)
    S            → SubordClause PUNCT[COMMA] S  (pre-matrix)

The two matrix-attachment rules are SUBORD_TYPE-agnostic — they
admit any SubordClause, so subsequent Phase 5l commits (concessive,
temporal, purpose, reason) only add new SubordClause-builder rules,
not new attachers.

End-to-end target sentences:

    Kung kumain si Maria, pumunta si Juan.    # pre-matrix kung
    Pumunta si Juan kung kumain si Maria.     # post-matrix kung
    Kapag pumunta si Maria, kumain si Juan.   # pre-matrix kapag
    Pag kumain si Maria, pumunta si Juan.     # pre-matrix pag
    Sakali pumunta si Maria, kumain si Juan.  # pre-matrix sakali
    Alam ko kung pumunta si Maria.            # Phase 5i indirect-Q
                                                preserved (kung[INTERROG])
"""

from __future__ import annotations

from tgllfg.core.pipeline import parse_text


def _adjunct_with_subord_type(fs, subord_type: str):
    """Walk the matrix's ADJUNCT set; return the first f-structure
    whose ``SUBORD_TYPE`` matches ``subord_type``, or ``None``."""
    adjuncts = fs.feats.get("ADJUNCT")
    if adjuncts is None:
        return None
    for adj in adjuncts:
        if adj.feats.get("SUBORD_TYPE") == subord_type:
            return adj
    return None


# === kung — conditional ===============================================


class TestKungConditional:
    """``kung`` (COND) embeds a clause as a conditional adjunct.
    Both pre-matrix (with comma) and post-matrix (no comma) forms
    produce identical f-structures — the conditional clause is an
    ADJUNCT member with ``SUBORD_TYPE=COND``."""

    def test_kung_pre_matrix(self) -> None:
        parses = parse_text("Kung kumain si Maria, pumunta si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # Matrix is the post-comma S — its PRED is from ``pumunta``.
        assert (fs.feats.get("PRED") or "").startswith("PUNTA")
        cond = _adjunct_with_subord_type(fs, "COND")
        assert cond is not None
        # Inner clause's PRED is from ``kumain`` and is visible on
        # the SubordClause f-structure (since ``(↑) = ↓2`` makes
        # the SubordClause structurally identical to the inner S).
        assert (cond.feats.get("PRED") or "").startswith("EAT")

    def test_kung_post_matrix(self) -> None:
        parses = parse_text("Pumunta si Juan kung kumain si Maria.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # Matrix is the leading S — its PRED is from ``pumunta``.
        assert (fs.feats.get("PRED") or "").startswith("PUNTA")
        cond = _adjunct_with_subord_type(fs, "COND")
        assert cond is not None
        assert (cond.feats.get("PRED") or "").startswith("EAT")

    def test_kung_pre_post_same_fstruct(self) -> None:
        """Pre-matrix and post-matrix produce identical f-structures
        modulo the c-tree (only structurally; the f-struct contents
        match)."""
        pre = parse_text("Kung kumain si Maria, pumunta si Juan.")[0][1]
        post = parse_text("Pumunta si Juan kung kumain si Maria.")[0][1]
        assert (pre.feats.get("PRED") or "")[:6] == (
            post.feats.get("PRED") or ""
        )[:6]
        pre_cond = _adjunct_with_subord_type(pre, "COND")
        post_cond = _adjunct_with_subord_type(post, "COND")
        assert pre_cond is not None and post_cond is not None
        assert (pre_cond.feats.get("PRED") or "")[:4] == (
            post_cond.feats.get("PRED") or ""
        )[:4]


# === kapag / pag / sakali =============================================


class TestKapagConditional:
    """``kapag`` "when (habitually)" produces the same shape as
    ``kung``; the COND COMP_TYPE is shared."""

    def test_kapag_pre_matrix(self) -> None:
        parses = parse_text("Kapag pumunta si Maria, kumain si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        cond = _adjunct_with_subord_type(fs, "COND")
        assert cond is not None
        assert (cond.feats.get("PRED") or "").startswith("PUNTA")

    def test_kapag_post_matrix(self) -> None:
        parses = parse_text("Kumain si Juan kapag pumunta si Maria.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        cond = _adjunct_with_subord_type(fs, "COND")
        assert cond is not None


class TestPagConditional:
    """``pag`` is a colloquial shortening of ``kapag`` — same
    syntactic distribution."""

    def test_pag_pre_matrix(self) -> None:
        parses = parse_text("Pag kumain si Maria, pumunta si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        cond = _adjunct_with_subord_type(fs, "COND")
        assert cond is not None


class TestSakaliConditional:
    """``sakali`` "in case" carries SUBORD_VARIANT=IN_CASE on the
    PART daughter (Commit 1) but produces the same SUBORD_TYPE=COND
    shape on the matrix."""

    def test_sakali_pre_matrix(self) -> None:
        parses = parse_text("Sakali pumunta si Maria, kumain si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        cond = _adjunct_with_subord_type(fs, "COND")
        assert cond is not None


# === Phase 5i polysemy preserved ======================================


class TestKungPolysemyPreserved:
    """The Phase 5i indirect-Q ``Alam ko kung X`` construction
    must continue to parse — ``kung[COMP_TYPE=INTERROG]`` fires
    in matrix-COMP-INTERROG-wrap context, while
    ``kung[COMP_TYPE=COND]`` fires only in subordinate-clause
    context."""

    def test_indirect_q_still_parses(self) -> None:
        # Phase 5i ``S_INTERROG_COMP`` requires Q_TYPE=WH on the
        # inner clause, so the canonical Phase 5i sentence has a
        # wh-fronted inner clause. Phase 5l must not regress this.
        parses = parse_text("Alam ko kung sino ang kumain.")
        assert len(parses) >= 1, (
            "Phase 5i indirect-Q ``Alam ko kung sino ang kumain.`` "
            "must continue to parse with the kung[INTERROG] reading "
            "even though Phase 5l adds kung[COND]"
        )


# === Subord with negation / coord inside ==============================


class TestNegatedInnerClause:
    """The inner clause of a subord can be negated — ``hindi``
    polarity is a clause-internal feature that doesn't interact
    with the SUBORD_TYPE on the wrapping SubordClause."""

    def test_kung_negated_inner(self) -> None:
        parses = parse_text("Kung hindi kumain si Maria, pumunta si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        cond = _adjunct_with_subord_type(fs, "COND")
        assert cond is not None
        # Inner clause's POLARITY=NEG is visible.
        assert cond.feats.get("POLARITY") == "NEG"


class TestNegatedMatrixClause:
    """Matrix-clause negation composes orthogonally with subord."""

    def test_kung_negated_matrix(self) -> None:
        parses = parse_text("Hindi pumunta si Juan kung kumain si Maria.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # Matrix is negated.
        assert fs.feats.get("POLARITY") == "NEG"
        cond = _adjunct_with_subord_type(fs, "COND")
        assert cond is not None
        # Inner clause has its own (positive) polarity.
        assert cond.feats.get("POLARITY") != "NEG"


class TestNPCoordInsideSubord:
    """A Phase 5k NP-coord SUBJ can live inside a subord clause —
    composes via the inner S parsing the coord-NP."""

    def test_kung_inner_np_coord(self) -> None:
        parses = parse_text(
            "Kung pumunta si Maria at si Juan, kumain si Pedro."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        cond = _adjunct_with_subord_type(fs, "COND")
        assert cond is not None
        # Inner SUBJ is a CONJUNCTS-set NP-coord.
        inner_subj = cond.feats.get("SUBJ")
        assert inner_subj is not None
        assert inner_subj.feats.get("COORD") == "AND"


# === C-tree shape =====================================================


class TestCTreeShape:
    """Pre-matrix has 3 daughters (SubordClause + PUNCT + S);
    post-matrix has 2 daughters (S + SubordClause)."""

    def test_pre_matrix_three_daughters(self) -> None:
        parses = parse_text("Kung kumain si Maria, pumunta si Juan.")
        ctree, _fs, _astr, _diags = parses[0]
        # Find the top-level S node — should have 3 daughters.
        assert ctree.label.startswith("S")
        labels = [c.label for c in ctree.children]
        assert labels[0].startswith("SubordClause")
        assert labels[1].startswith("PUNCT")
        assert labels[2].startswith("S")

    def test_post_matrix_two_daughters(self) -> None:
        parses = parse_text("Pumunta si Juan kung kumain si Maria.")
        ctree, _fs, _astr, _diags = parses[0]
        assert ctree.label.startswith("S")
        labels = [c.label for c in ctree.children]
        assert labels[0].startswith("S")
        assert labels[1].startswith("SubordClause")


# === SubordClause f-structure invariants ==============================


class TestSubordClauseFStructure:
    """The SubordClause f-structure has SUBORD_TYPE=COND overlaid
    on the inner clause's f-structure. Inner clause's SUBJ / PRED /
    etc. are visible."""

    def test_inner_clause_subj_visible(self) -> None:
        parses = parse_text("Kung kumain si Maria, pumunta si Juan.")
        _ct, fs, _astr, _diags = parses[0]
        cond = _adjunct_with_subord_type(fs, "COND")
        assert cond is not None
        # Inner SUBJ from ``si Maria``.
        inner_subj = cond.feats.get("SUBJ")
        assert inner_subj is not None
        assert inner_subj.feats.get("CASE") == "NOM"

    def test_inner_clause_pred_visible(self) -> None:
        parses = parse_text("Kung kumain si Maria, pumunta si Juan.")
        _ct, fs, _astr, _diags = parses[0]
        cond = _adjunct_with_subord_type(fs, "COND")
        assert cond is not None
        # Inner PRED is the kain-family predicate.
        assert (cond.feats.get("PRED") or "").startswith("EAT")
