# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.C Commit 2 — L78 wide-scope hindi over coord-NP.

Closes §18 L78 (cross-conjunct negation scoping). The new rule in
``cfg/negation.py`` admits ``Hindi [si Maria at si Juan] kumain.``
(S-V word order with hindi at left edge and a coord-SUBJ before the
AV-intransitive verb), producing a parse with ``NEG_SCOPE=WIDE`` on
the matrix S to mark the wide-scope reading
(``¬(eat(M) ∧ eat(J))``).

Two parameterised rules cover AND-coord and OR-coord; both yield
"neither one" semantics by De Morgan. The default narrow-scope
hindi-wrap (Phase 4 §7.2) is unchanged — sentences without a
coord-SUBJ continue to parse as before with no ``NEG_SCOPE`` on
the matrix.

Design appendix: ``docs/analysis-choices.md`` Phase 5n.C Commit 1.
Reference: Schachter & Otanes 1972 §10.
"""

import pytest

from tgllfg.core.pipeline import parse_text


# === Wide-scope reading on coord-SUBJ ====================================


class TestWideScopeAND:
    """AND-coord SUBJ produces NEG_SCOPE=WIDE on the matrix."""

    def test_canonical_and_coord(self) -> None:
        parses = parse_text("Hindi si Maria at si Juan kumain.")
        assert len(parses) >= 1
        wide_parses = [
            (ct, fs, astr, diags) for ct, fs, astr, diags in parses
            if fs.feats.get("NEG_SCOPE") == "WIDE"
        ]
        assert len(wide_parses) >= 1, (
            "expected at least one wide-scope parse with NEG_SCOPE=WIDE"
        )
        _ct, fs, _astr, _diags = wide_parses[0]
        assert fs.feats.get("POLARITY") == "NEG"
        assert fs.feats.get("NEG_SCOPE") == "WIDE"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "AND"

    def test_three_conjunct_and_coord(self) -> None:
        """3-conjunct AND-coord SUBJ also produces wide scope."""
        parses = parse_text(
            "Hindi si Maria, si Juan at si Pedro kumain."
        )
        wide_parses = [
            (ct, fs, astr, diags) for ct, fs, astr, diags in parses
            if fs.feats.get("NEG_SCOPE") == "WIDE"
        ]
        assert len(wide_parses) >= 1
        _ct, fs, _astr, _diags = wide_parses[0]
        assert fs.feats.get("POLARITY") == "NEG"


class TestWideScopeOR:
    """OR-coord SUBJ produces NEG_SCOPE=WIDE; matrix carries
    COORD=OR on the SUBJ (vs AND for the additive variant)."""

    def test_canonical_or_coord(self) -> None:
        parses = parse_text("Hindi si Maria o si Juan kumain.")
        wide_parses = [
            (ct, fs, astr, diags) for ct, fs, astr, diags in parses
            if fs.feats.get("NEG_SCOPE") == "WIDE"
        ]
        assert len(wide_parses) >= 1, (
            "expected at least one wide-scope parse with NEG_SCOPE=WIDE"
        )
        _ct, fs, _astr, _diags = wide_parses[0]
        assert fs.feats.get("POLARITY") == "NEG"
        assert fs.feats.get("NEG_SCOPE") == "WIDE"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "OR"


# === Narrow-scope preservation (no coord-SUBJ) ===========================


class TestNarrowScopePreserved:
    """Sentences without a coord-SUBJ continue to parse via the Phase
    4 §7.2 hindi-wrap rule, with POLARITY=NEG on the matrix and no
    NEG_SCOPE feat (the absence of NEG_SCOPE encodes the default
    narrow / no-coord-interaction reading)."""

    @pytest.mark.parametrize("sentence", [
        "Hindi kumain si Maria.",
        "Hindi pumunta si Juan.",
        "Hindi tumakbo si Pedro.",
    ])
    def test_no_coord_subject(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("POLARITY") == "NEG"
            # No NEG_SCOPE on any parse — the new rule requires a
            # coord-SUBJ daughter, which these sentences don't have.
            assert "NEG_SCOPE" not in fs.feats


# === Disambiguation from Phase 5k asymmetric coord =======================


class TestAsymmetricCoordUnaffected:
    """The Phase 5k Commit 8 asymmetric coord rule (``Si Maria, hindi
    si Juan``) produces COORD=BUT_NOT, distinct from the AND/OR that
    the wide-scope rule constrains on. The two rules don't compete."""

    def test_asymmetric_coord_no_wide_scope_marker(self) -> None:
        """``Kumain si Maria, hindi si Juan.`` parses via the
        asymmetric coord rule; the matrix S should NOT carry
        NEG_SCOPE=WIDE because the rule that sets that feat only
        fires on COORD=AND/OR."""
        parses = parse_text("Kumain si Maria, hindi si Juan.")
        assert len(parses) >= 1
        for _ct, fs, _astr, _diags in parses:
            # Asymmetric coord puts POLARITY=NEG on the SECOND
            # conjunct, not on the matrix. The matrix carries
            # COORD=BUT_NOT but not NEG_SCOPE.
            assert fs.feats.get("NEG_SCOPE") is None


# === Multi-clause coord stays narrow ====================================


class TestMultiClauseCoordNarrow:
    """``Hindi kumain si Maria at uminom si Juan.`` (two-clause coord
    with hindi on the first clause) is the canonical narrow-scope
    case per ``cfg/coordination.py:355``. The wide-scope rule does
    NOT fire here because its daughter shape is
    ``PART NP[CASE=NOM, COORD] V`` (single V), not
    ``PART V NP at V NP`` (multi-clause)."""

    def test_two_clause_coord_no_wide_marker(self) -> None:
        """The wide-scope rule does NOT fire on multi-clause coord
        surfaces. Currently ``Hindi kumain si Maria at uminom si
        Juan.`` 0-parses under existing grammar (independent of
        L78 — the bare-V intransitive clausal-coord shape isn't
        admitted today; ``cfg/coordination.py:355`` flags this
        case as deferred). The test asserts the negative
        property: if / when the surface parses in the future, no
        ``NEG_SCOPE=WIDE`` should appear on the matrix because
        the L78 rule's daughter shape (``PART NP[COORD] V``)
        doesn't match the multi-clause shape (``PART V NP at V
        NP``)."""
        parses = parse_text(
            "Hindi kumain si Maria at uminom si Juan."
        )
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("NEG_SCOPE") is None


# === V-S word order: parse exists, narrow-scope unmarked surface 0-parses
# without coord ==========================================================


class TestVSWordOrderRequiresCoordSubject:
    """The wide-scope rule's daughter shape requires
    ``NP[CASE=NOM, COORD=AND/OR]``. A non-coord SUBJ in pre-V
    position (``Hindi si Maria kumain.``) should NOT compose via
    the wide-scope rule — the COORD constraining equation rejects
    a non-coord NP."""

    def test_pre_v_singular_subject_no_wide_scope(self) -> None:
        parses = parse_text("Hindi si Maria kumain.")
        # Either 0 parses (non-canonical without ay-fronting and
        # no coord) or some other path; in any case, no NEG_SCOPE
        # should appear on the matrix.
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("NEG_SCOPE") is None
