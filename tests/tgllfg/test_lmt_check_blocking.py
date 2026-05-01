"""Phase 5 §8 — blocking diagnostics from lmt_check.

Phase 5 promotes two classes of LMT disagreement to blocking:

* **Subject-slot mismatch.** The engine predicts SUBJ for some role
  but the f-structure has no SUBJ feature. Surfaced as
  ``subject-condition-failed`` (already in the blocking set).

* **Biuniqueness violation.** The engine emits
  ``lmt-biuniqueness-violated`` when two roles map to the same GF in
  the lex profile (an inconsistent intrinsic profile). Surfaced
  as-is (also blocking).

Non-SUBJ GF differences (e.g. the Phase 4 grammar's bare ``OBJ`` vs
the engine's typed ``OBJ-θ`` for non-AV ng-non-pivots) stay
informational via ``lmt-mismatch``.

These tests construct synthetic ``LexicalEntry`` + ``FStructure``
fixtures and call :func:`tgllfg.lmt.lmt_check` directly. End-to-end
parse-level coverage (where the grammar normally always emits SUBJ)
lives in :mod:`test_lmt_pipeline_integration`.
"""

from __future__ import annotations

from tgllfg.common import FStructure, LexicalEntry
from tgllfg.fstruct import Diagnostic
from tgllfg.lmt import lmt_check


# === Subject-slot mismatch (blocking) =====================================


class TestSubjectSlotMismatchBlocks:
    """LMT predicts SUBJ but the f-structure has no SUBJ → block."""

    def test_subj_predicted_but_missing_emits_blocking_diag(self) -> None:
        # AV-tr profile: AGENT [-r,-o] → SUBJ, PATIENT [-r,+o] → OBJ.
        # Engine predicts SUBJ. F-structure deliberately has no SUBJ
        # (a hypothetical buggy parse).
        lex = LexicalEntry(
            lemma="foo",
            pred="EAT <SUBJ, OBJ>",
            a_structure=["AGENT", "PATIENT"],
            morph_constraints={},
            gf_defaults={"AGENT": "SUBJ", "PATIENT": "OBJ"},
            intrinsic_classification={
                "AGENT": (False, False),
                "PATIENT": (False, True),
            },
        )
        f = FStructure(feats={
            "PRED": "EAT <SUBJ, OBJ>",
            "VOICE": "AV",
            "OBJ": FStructure(feats={"PRED": "ISDA"}, id=1),
            # No SUBJ feature.
        })
        _astr, diagnostics = lmt_check(f, lex)
        # subject-condition-failed is present and blocking.
        subj_diags = [
            d for d in diagnostics if d.kind == "subject-condition-failed"
        ]
        assert len(subj_diags) == 1
        assert subj_diags[0].is_blocking()
        assert "SUBJ" in subj_diags[0].message
        assert "EAT" in subj_diags[0].message

    def test_subj_present_no_subject_diag(self) -> None:
        # Sanity: when SUBJ is present in both expected and actual,
        # no subject-condition-failed fires.
        lex = LexicalEntry(
            lemma="foo",
            pred="EAT <SUBJ, OBJ>",
            a_structure=["AGENT", "PATIENT"],
            morph_constraints={},
            gf_defaults={"AGENT": "SUBJ", "PATIENT": "OBJ"},
            intrinsic_classification={
                "AGENT": (False, False),
                "PATIENT": (False, True),
            },
        )
        f = FStructure(feats={
            "PRED": "EAT <SUBJ, OBJ>",
            "VOICE": "AV",
            "SUBJ": FStructure(feats={"PRED": "ASO"}, id=1),
            "OBJ": FStructure(feats={"PRED": "ISDA"}, id=2),
        })
        _astr, diagnostics = lmt_check(f, lex)
        assert not any(
            d.kind == "subject-condition-failed" for d in diagnostics
        )


# === Biuniqueness (blocking) ==============================================


class TestBiuniquenessBlocks:
    """When the engine emits ``lmt-biuniqueness-violated`` (two roles
    both [-r, -o] → both SUBJ-eligible → step 4 picks one and the
    other is leftover) lmt_check surfaces it as-is, blocking the
    parse."""

    def test_two_subj_candidates_emits_blocking_biuniq(self) -> None:
        # Construct a profile where AGENT and PATIENT are both
        # [-r, -o]. compute_mapping picks AGENT (higher hierarchy)
        # and surfaces PATIENT as a duplicate-SUBJ candidate via
        # lmt-biuniqueness-violated.
        lex = LexicalEntry(
            lemma="foo",
            pred="X <SUBJ, OBJ>",
            a_structure=["AGENT", "PATIENT"],
            morph_constraints={},
            gf_defaults={},
            intrinsic_classification={
                "AGENT": (False, False),
                "PATIENT": (False, False),
            },
        )
        f = FStructure(feats={
            "PRED": "X <SUBJ, OBJ>",
            "VOICE": "AV",
            "SUBJ": FStructure(feats={"PRED": "S"}, id=1),
        })
        _astr, diagnostics = lmt_check(f, lex)
        biuniq = [
            d for d in diagnostics if d.kind == "lmt-biuniqueness-violated"
        ]
        assert len(biuniq) == 1
        assert biuniq[0].is_blocking()


# === Informational lmt-mismatch (non-blocking) ============================


class TestInformationalMismatch:
    """Non-SUBJ GF differences (the OV/DV/IV ng-non-pivot OBJ ⇄
    OBJ-θ noise) remain informational. The parse survives."""

    def test_obj_vs_obj_theta_is_informational(self) -> None:
        # OV profile: AGENT [+r,+o] → OBJ-AGENT, PATIENT [-r,-o] → SUBJ.
        # F-structure has bare OBJ (Phase 4 grammar behavior).
        lex = LexicalEntry(
            lemma="kain",
            pred="EAT <SUBJ, OBJ>",
            a_structure=["AGENT", "PATIENT"],
            morph_constraints={},
            gf_defaults={"PATIENT": "SUBJ", "AGENT": "OBJ"},
            intrinsic_classification={
                "AGENT": (True, True),
                "PATIENT": (False, False),
            },
        )
        f = FStructure(feats={
            "PRED": "EAT <SUBJ, OBJ>",
            "VOICE": "OV",
            "SUBJ": FStructure(feats={"PRED": "ISDA"}, id=1),
            "OBJ": FStructure(feats={"PRED": "ASO"}, id=2),
        })
        _astr, diagnostics = lmt_check(f, lex)
        # Informational lmt-mismatch present.
        mismatches = [d for d in diagnostics if d.kind == "lmt-mismatch"]
        assert len(mismatches) >= 1
        for d in mismatches:
            assert not d.is_blocking()
        # No blocking diagnostics (SUBJ present in both, no biuniq).
        assert not any(d.is_blocking() for d in diagnostics)

    def test_av_perfect_match_no_diagnostics(self) -> None:
        # AV-tr: engine and grammar agree on SUBJ + bare OBJ.
        lex = LexicalEntry(
            lemma="kain",
            pred="EAT <SUBJ, OBJ>",
            a_structure=["AGENT", "PATIENT"],
            morph_constraints={},
            gf_defaults={"AGENT": "SUBJ", "PATIENT": "OBJ"},
            intrinsic_classification={
                "AGENT": (False, False),
                "PATIENT": (False, True),
            },
        )
        f = FStructure(feats={
            "PRED": "EAT <SUBJ, OBJ>",
            "VOICE": "AV",
            "SUBJ": FStructure(feats={"PRED": "ASO"}, id=1),
            "OBJ": FStructure(feats={"PRED": "ISDA"}, id=2),
        })
        _astr, diagnostics = lmt_check(f, lex)
        # Engine and grammar agree completely → no diagnostics.
        assert diagnostics == []


# === Engine SUBJ-condition handling =======================================


class TestEngineSubjConditionDropped:
    """The engine emits ``subject-condition-failed`` when the lex
    profile has no SUBJ candidate (all roles +r,+o or similar). We
    intentionally drop that diagnostic at lmt_check: the structural
    ``lfg_well_formed`` downstream catches the case where the
    f-structure also has no SUBJ; if the f-structure has SUBJ, the
    parse is structurally OK."""

    def test_engine_subj_condition_dropped_when_fstruct_has_subj(self) -> None:
        # Profile: AGENT [+r,+o], PATIENT [+r,+o]. No SUBJ candidate
        # → engine emits subject-condition-failed.
        lex = LexicalEntry(
            lemma="foo",
            pred="X <SUBJ, OBJ>",
            a_structure=["AGENT", "PATIENT"],
            morph_constraints={},
            gf_defaults={},
            intrinsic_classification={
                "AGENT": (True, True),
                "PATIENT": (True, True),
            },
        )
        # F-structure has SUBJ (grammar bound it); lex profile says no.
        f = FStructure(feats={
            "PRED": "X <SUBJ, OBJ>",
            "VOICE": "AV",
            "SUBJ": FStructure(feats={"PRED": "S"}, id=1),
        })
        _astr, diagnostics = lmt_check(f, lex)
        # No subject-condition-failed surfaced (engine's was dropped;
        # the structural one didn't fire because f-structure has SUBJ).
        assert not any(
            d.kind == "subject-condition-failed" for d in diagnostics
        )

    def test_engine_subj_condition_dropped_when_fstruct_lacks_subj(self) -> None:
        # Same lex, f-structure also has no SUBJ. lmt_check still
        # drops the engine diagnostic — but a different code path
        # (structural check via expected_gfs vs actual_gfs) doesn't
        # fire either because expected_gfs also lacks SUBJ. The
        # downstream lfg_well_formed catches the missing-SUBJ case
        # via its own structural Subject Condition check.
        lex = LexicalEntry(
            lemma="foo",
            pred="X <SUBJ, OBJ>",
            a_structure=["AGENT", "PATIENT"],
            morph_constraints={},
            gf_defaults={},
            intrinsic_classification={
                "AGENT": (True, True),
                "PATIENT": (True, True),
            },
        )
        f = FStructure(feats={"PRED": "X <SUBJ, OBJ>", "VOICE": "AV"})
        _astr, diagnostics = lmt_check(f, lex)
        # lmt_check itself doesn't emit subject-condition-failed
        # (expected_gfs lacks SUBJ since the lex profile had no
        # candidate, so the SUBJ-slot mismatch check doesn't fire).
        # The structural well-formedness check would emit it
        # downstream — that's tested in test_well_formedness.py.
        subj_diags = [
            d for d in diagnostics if d.kind == "subject-condition-failed"
        ]
        assert subj_diags == []


# === Existing pipeline parses unaffected ==================================


class TestExistingParsesNoNewBlocking:
    """End-to-end smoke check: parse the OV/DV/IV cases that
    produce informational lmt-mismatch and confirm the SUBJ-slot
    promotion logic doesn't accidentally block them."""

    def test_ov_transitive_parse_survives(self) -> None:
        from tgllfg.pipeline import parse_text
        results = parse_text("Kinain ng aso ang isda.")
        assert results, "OV-tr parse was suppressed"
        # The mismatch diagnostic is present (informational).
        diags = results[0][3]
        mismatches = [d for d in diags if d.kind == "lmt-mismatch"]
        assert mismatches and not any(d.is_blocking() for d in mismatches)
        # No blocking diagnostics overall.
        assert not any(d.is_blocking() for d in diags)

    def test_dv_transitive_parse_survives(self) -> None:
        from tgllfg.pipeline import parse_text
        results = parse_text("Sinulatan ng bata ang ina.")
        assert results, "DV-tr parse was suppressed"
        assert not any(d.is_blocking() for d in results[0][3])

    def test_iv_conveyed_parse_survives(self) -> None:
        from tgllfg.pipeline import parse_text
        results = parse_text("Itinapon ng bata ang basura.")
        assert results, "IV-CONVEY parse was suppressed"
        assert not any(d.is_blocking() for d in results[0][3])

    def test_av_intransitive_clean(self) -> None:
        from tgllfg.pipeline import parse_text
        results = parse_text("Kumain ang aso.")
        assert results
        # No diagnostics at all.
        assert results[0][3] == [] or all(
            not d.is_blocking() for d in results[0][3]
        )

    def test_motion_locative_parse_survives(self) -> None:
        # The lakad locative parse with OBL-LOC has no SUBJ mismatch
        # and no biuniqueness violation, so the promotion logic
        # doesn't suppress it.
        from tgllfg.pipeline import parse_text
        results = parse_text("Lumakad ang bata sa palengke.")
        # Find the OBL-LOC parse.
        obl_parse = next(
            (p for p in results if "OBL-LOC" in p[1].feats), None
        )
        assert obl_parse is not None, "OBL-LOC parse was suppressed"
        diags = obl_parse[3]
        assert not any(d.is_blocking() for d in diags)


# === Diagnostic shape is_blocking ========================================


def test_subject_condition_failed_is_blocking() -> None:
    # Sanity: the kind we're emitting from lmt_check is structurally
    # blocking (not in NON_BLOCKING_KINDS).
    d = Diagnostic(
        kind="subject-condition-failed",
        message="example",
    )
    assert d.is_blocking()


def test_lmt_biuniqueness_violated_is_blocking() -> None:
    d = Diagnostic(
        kind="lmt-biuniqueness-violated",
        message="example",
    )
    assert d.is_blocking()


def test_lmt_mismatch_is_not_blocking() -> None:
    d = Diagnostic(
        kind="lmt-mismatch",
        message="example",
    )
    assert not d.is_blocking()
