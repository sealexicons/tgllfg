# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 8.M: ``nang`` temporal subordinator "when" + post-matrix-comma.

Commit 1 (TEMP_WHEN):
  Closes the audit-named ``Nang tamaan siya ng baseball...``
  (R&C 1990) / ``Nang dumating si Ben, ...`` (S&O 1972) construction
  class via a new ``nang`` PART lex entry with ``COMP_TYPE=TEMP_WHEN``
  + a new SubordClause builder rule parallel to Phase 5l C7
  ``mula nang`` TEMP_SINCE rule.

Commit 2 (post-matrix-comma):
  Phase 5l completion (anti-deferral). The original Phase 5l rule
  set covers pre-matrix-with-comma (``Kapag X, S``) and post-
  matrix-no-comma (``S kapag X``), but the post-matrix-WITH-comma
  shape (``S, kapag X``) was missing. Audit-driven: 68 corpus
  candidates across all temporal/causal/concessive subords (bago=15,
  para=13, kung=8, kahit=7, habang=7, dahil=6, kasi=4, hanggang=3,
  pagkatapos=3, nang=2). Adds ``S → S PUNCT[COMMA] SubordClause``
  parallel to the existing post-matrix-no-comma rule.

Direct audit-corpus closures: **0**. All 18-23 corpus candidates
with ``nang`` TEMPORAL have orthogonal blockers (OOV verbs
``bumuhos`` / ``lumiwanag`` / ``huminto`` / ``lumindol`` /
``nangyari`` / ``tamaan`` / ``naging`` / ``nanaginip`` /
``mapagtanto``; clitic-glue ``ano'ng``; NOM-PRON-pivot-post-comma
chart issue; OCR junk). Construction-class infrastructure becomes
available for future 8.B-class lex passes to unlock corpus
closures.

Constructed minimal-pair closures (this PR):
  * ``Nang kumain siya, umalis ako.`` (C1)
  * ``Umalis ako nang kumain siya.`` (C1, pre-existing post-matrix-
    no-comma rule)
  * ``Tumakbo ang aso, nang umalis si Juan.`` (C2 NEW shape)
  * ``Kumain si Juan, kapag aalis si Pedro.`` (C2 NEW, generalizes
    across all subords)
"""

import pytest


def _has_subord_type(parses, value):
    """True iff at least one parse has an ADJUNCT with SUBORD_TYPE=value."""
    for p in parses:
        adj = p[1].feats.get("ADJUNCT")
        if adj:
            for a in adj:
                if a.feats.get("SUBORD_TYPE") == value:
                    return True
    return False


class TestPhase8mNangTempWhen:
    """C1: ``nang`` PART[TEMP_WHEN] registration + new SubordClause rule.

    The new lex entry is distinct from the existing TEMP_SINCE entry
    (which only fires composed with the ``mula`` PREP via Phase 5l C7).
    Bare ``Nang VERB ..., S`` now builds a SubordClause with
    SUBORD_TYPE=TEMP_WHEN."""

    @pytest.mark.parametrize("sentence", [
        "Nang kumain siya, umalis ako.",
        "Nang dumating sila, kumain kami.",
        "Nang umalis ako, umalis siya.",
        "Nang kumain ang bata, umalis ang nanay.",
    ])
    def test_pre_matrix_comma(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse for {sentence!r}"
        assert _has_subord_type(parses, "TEMP_WHEN"), (
            f"{sentence!r} parsed but no TEMP_WHEN SUBORD_TYPE in any "
            f"ADJUNCT"
        )

    @pytest.mark.parametrize("sentence", [
        # Post-matrix, no comma — covered by existing Phase 5l rule (b).
        "Umalis ako nang kumain siya.",
        "Kumain ang bata nang umalis ang nanay.",
    ])
    def test_post_matrix_no_comma(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse for {sentence!r}"
        assert _has_subord_type(parses, "TEMP_WHEN"), (
            f"{sentence!r} parsed but no TEMP_WHEN SUBORD_TYPE in any "
            f"ADJUNCT"
        )


class TestPhase8mPostMatrixComma:
    """C2: new ``S → S , SubordClause`` rule (post-matrix WITH comma).

    Closes a Phase 5l-class gap that affected all temporal/causal/
    concessive subords. The new rule is SUBORD_TYPE-agnostic, parallel
    to the existing post-matrix-no-comma rule."""

    @pytest.mark.parametrize("sentence,subord_type", [
        ("Tumakbo ang aso, nang umalis si Juan.", "TEMP_WHEN"),
        ("Kumain si Juan, kapag aalis si Pedro.", "COND"),
        ("Tumakbo si Maria, habang umiyak si Pedro.", "TEMP_WHILE"),
        ("Umalis siya, bago kumain si Juan.", "TEMP_BEFORE"),
    ])
    def test_post_matrix_comma_across_subords(
        self, sentence: str, subord_type: str,
    ) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse for {sentence!r}"
        assert _has_subord_type(parses, subord_type), (
            f"{sentence!r} parsed but no {subord_type} SUBORD_TYPE"
        )


class TestPhase8mRegressions:
    """Phase 5l existing readings still parse after C1+C2."""

    def test_mula_nang_temp_since(self) -> None:
        """``Mula nang`` TEMP_SINCE composition still fires (Phase 5l C7)."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Mula nang kumain siya, umalis ako.", n_best=3
        )
        assert len(parses) >= 1
        assert _has_subord_type(parses, "TEMP_SINCE")

    def test_pre_matrix_comma_kapag(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Kapag kumain siya, umalis ako.", n_best=3)
        assert len(parses) >= 1
        assert _has_subord_type(parses, "COND")

    def test_post_matrix_no_comma_kapag(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Umalis ako kapag kumain siya.", n_best=3)
        assert len(parses) >= 1
        assert _has_subord_type(parses, "COND")


class TestPhase8mNangNotSpurious:
    """No spurious-ambiguity from the dual TEMP_SINCE/TEMP_WHEN
    ``nang`` lex entries.

    ``Mula nang ...`` must give only TEMP_SINCE; bare ``Nang ...``
    must give only TEMP_WHEN. The chart's ``=c`` constraints route
    each rule to its matching lex variant."""

    def test_mula_nang_gives_only_since(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Mula nang kumain siya, umalis ako.", n_best=5
        )
        types_seen = set()
        for p in parses:
            adj = p[1].feats.get("ADJUNCT")
            if adj:
                for a in adj:
                    st = a.feats.get("SUBORD_TYPE")
                    if st:
                        types_seen.add(st)
        assert "TEMP_SINCE" in types_seen
        assert "TEMP_WHEN" not in types_seen, (
            f"spurious TEMP_WHEN reading for `mula nang`; types={types_seen}"
        )

    def test_bare_nang_gives_only_when(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Nang kumain siya, umalis ako.", n_best=5)
        types_seen = set()
        for p in parses:
            adj = p[1].feats.get("ADJUNCT")
            if adj:
                for a in adj:
                    st = a.feats.get("SUBORD_TYPE")
                    if st:
                        types_seen.add(st)
        assert "TEMP_WHEN" in types_seen
        assert "TEMP_SINCE" not in types_seen, (
            f"spurious TEMP_SINCE reading for bare `nang`; types={types_seen}"
        )


class TestPhase8mOutOfScope:
    """Corpus candidates remaining zero-parse after 8.M — all blocked
    by orthogonal OOV or chart-level issues. Pin one representative
    of each cluster; flip if the relevant orthogonal sub-PR lands."""

    def test_oov_blocked_audit_target(self) -> None:
        """``Nang tamaan siya ng baseball sa ulo, ...`` — ``tamaan`` is
        OOV; ``naging`` in matrix is OOV; would close via a separate
        lex pass."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Nang tamaan siya ng baseball sa ulo, "
            "ano ang naging resulta?",
            n_best=3,
        )
        assert len(parses) == 0, (
            "OOV-blocked audit target unexpectedly parses — flip if "
            "tamaan/naging lex sub-PR added the missing entries."
        )

    def test_postcomma_nom_pron_pivot_chart_issue(self) -> None:
        """``Kapag X, tinawag niya ako.`` — matrix has ng-PRON +
        NOM-PRON pivot post-comma; fails at the chart level via a
        pre-existing clitic-placement issue affecting all temporal
        subords (not just nang). Documented as Phase 8.M follow-on
        for diagnostic deep-dive."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Kapag aalis ako, tinawag niya ako.", n_best=3
        )
        assert len(parses) == 0, (
            "Post-comma NOM-PRON-pivot now parses — flip if the "
            "underlying chart issue was fixed."
        )

    def test_postmatrix_comma_audit_oov_blocker(self) -> None:
        """``Nasa daan na si Max, nang bumuhos ang malakas na ulan.``
        — uses C2's new shape but ``bumuhos`` is OOV. C2 rule fires
        on minimal pairs (verified above); this audit corpus target
        needs the separate ``buhos`` lex addition."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Nasa daan na si Max, "
            "nang bumuhos ang malakas na ulan.",
            n_best=3,
        )
        assert len(parses) == 0, (
            "Audit target now parses — flip if buhos lex sub-PR "
            "added the missing entry."
        )
