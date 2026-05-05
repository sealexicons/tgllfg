from __future__ import annotations

import pytest

from tgllfg.core.common import FStructure
from tgllfg.fstruct import (
    PredTemplate,
    is_governable_gf,
    lfg_well_formed,
    parse_pred_template,
)


# === PRED template parsing ================================================

class TestParsePredTemplate:
    def test_zero_arg(self) -> None:
        assert parse_pred_template("WALK") == PredTemplate("WALK", (), (), ())

    def test_one_arg(self) -> None:
        assert parse_pred_template("WALK <SUBJ>") == PredTemplate(
            "WALK", ("SUBJ",), ("SUBJ",), ()
        )

    def test_two_args(self) -> None:
        assert parse_pred_template("EAT <SUBJ, OBJ>") == PredTemplate(
            "EAT", ("SUBJ", "OBJ"), ("SUBJ", "OBJ"), ()
        )

    def test_typed_obl_args(self) -> None:
        # Real grammars name OBL-AG, OBL-LOC, OBJ-GOAL etc.
        assert parse_pred_template(
            "GIVE <SUBJ, OBJ, OBL-GOAL>"
        ) == PredTemplate(
            "GIVE",
            ("SUBJ", "OBJ", "OBL-GOAL"),
            ("SUBJ", "OBJ", "OBL-GOAL"),
            (),
        )

    def test_whitespace_tolerated(self) -> None:
        assert parse_pred_template("  EAT   <  SUBJ ,  OBJ  >  ") == (
            PredTemplate("EAT", ("SUBJ", "OBJ"), ("SUBJ", "OBJ"), ())
        )

    def test_toy_noun_template(self) -> None:
        # The N → NOUN rule emits this placeholder; we accept it as a
        # 0-ary predicate so well-formedness skips it cleanly.
        assert parse_pred_template("NOUN(↑ FORM)") == PredTemplate(
            "NOUN(↑ FORM)", (), (), ()
        )

    def test_empty_arg_list(self) -> None:
        assert parse_pred_template("HELP <>") == PredTemplate(
            "HELP", (), (), ()
        )

    def test_non_thematic_subj(self) -> None:
        # Phase 5c §7.6 follow-on Commit 5: raising verbs declare a
        # non-thematic SUBJ outside the angle brackets.
        # ``governables`` is the union; ``thematic`` and
        # ``non_thematic`` separate the two flavors.
        assert parse_pred_template("SEEM <XCOMP> SUBJ") == PredTemplate(
            "SEEM", ("XCOMP", "SUBJ"), ("XCOMP",), ("SUBJ",)
        )

    def test_multiple_non_thematic(self) -> None:
        assert parse_pred_template(
            "WEATHER <> SUBJ, EXPL"
        ) == PredTemplate(
            "WEATHER", ("SUBJ", "EXPL"), (), ("SUBJ", "EXPL")
        )

    def test_missing_close_bracket_rejected(self) -> None:
        with pytest.raises(ValueError):
            parse_pred_template("EAT <SUBJ, OBJ")

    def test_empty_arg_in_list_rejected(self) -> None:
        with pytest.raises(ValueError):
            parse_pred_template("EAT <SUBJ, , OBJ>")


# === Governable GF predicate ==============================================

class TestIsGovernable:
    def test_bare_governable(self) -> None:
        for gf in ("SUBJ", "OBJ", "COMP", "XCOMP"):
            assert is_governable_gf(gf)

    def test_typed_obj(self) -> None:
        assert is_governable_gf("OBJ-GOAL")
        assert is_governable_gf("OBJ-θ")  # Greek-θ name

    def test_typed_obl(self) -> None:
        assert is_governable_gf("OBL-AG")
        assert is_governable_gf("OBL-LOC")
        assert is_governable_gf("OBL-BEN")

    def test_adjuncts_and_discourse_exempt(self) -> None:
        for gf in ("ADJ", "TOPIC", "FOCUS"):
            assert not is_governable_gf(gf)

    def test_features_not_governable(self) -> None:
        for f in ("CASE", "VOICE", "ASPECT", "MOOD", "TR", "PRED",
                  "LEX-ASTRUCT", "FORM", "NUM", "PER"):
            assert not is_governable_gf(f)


# === Helper to build minimal f-structures =================================

def _fs(feats: dict[str, object], id_: int = 1) -> FStructure:
    return FStructure(feats=dict(feats), id=id_)


# === Completeness =========================================================

class TestCompleteness:
    def test_passes_when_all_args_present(self) -> None:
        f = _fs({
            "PRED": "EAT <SUBJ, OBJ>",
            "SUBJ": _fs({"CASE": "NOM"}, id_=2),
            "OBJ": _fs({"CASE": "GEN"}, id_=3),
        })
        ok, diags = lfg_well_formed(f)
        assert ok
        assert diags == []

    def test_missing_required_subj(self) -> None:
        f = _fs({
            "PRED": "EAT <SUBJ, OBJ>",
            "OBJ": _fs({"CASE": "GEN"}, id_=2),
        })
        ok, diags = lfg_well_formed(f)
        assert not ok
        kinds = [d.kind for d in diags]
        assert "completeness-failed" in kinds
        miss = next(d for d in diags if d.kind == "completeness-failed")
        assert miss.detail.get("missing") == "SUBJ"

    def test_missing_obj_reports_obj(self) -> None:
        f = _fs({
            "PRED": "EAT <SUBJ, OBJ>",
            "SUBJ": _fs({"CASE": "NOM"}, id_=2),
        })
        ok, diags = lfg_well_formed(f)
        assert not ok
        miss = [d for d in diags if d.kind == "completeness-failed"]
        assert len(miss) == 1
        assert miss[0].detail.get("missing") == "OBJ"


# === Coherence ============================================================

class TestCoherence:
    def test_extra_governable_flagged(self) -> None:
        # PRED selects only SUBJ, but the f-structure also has an OBJ.
        f = _fs({
            "PRED": "WALK <SUBJ>",
            "SUBJ": _fs({"CASE": "NOM"}, id_=2),
            "OBJ": _fs({"CASE": "GEN"}, id_=3),
        })
        ok, diags = lfg_well_formed(f)
        assert not ok
        coh = [d for d in diags if d.kind == "coherence-failed"]
        assert len(coh) == 1
        assert coh[0].detail.get("extra") == "OBJ"

    def test_adj_exempt(self) -> None:
        f = _fs({
            "PRED": "WALK <SUBJ>",
            "SUBJ": _fs({"CASE": "NOM"}, id_=2),
            "ADJ": frozenset(),
        })
        ok, _ = lfg_well_formed(f)
        assert ok

    def test_topic_focus_exempt(self) -> None:
        topic = _fs({"CASE": "NOM"}, id_=3)
        f = _fs({
            "PRED": "WALK <SUBJ>",
            "SUBJ": _fs({"CASE": "NOM"}, id_=2),
            "TOPIC": topic,
            "FOCUS": _fs({"CASE": "NOM"}, id_=4),
        })
        ok, _ = lfg_well_formed(f)
        assert ok

    def test_attributes_exempt(self) -> None:
        # CASE / VOICE / ASPECT / MOOD aren't governable.
        f = _fs({
            "PRED": "WALK <SUBJ>",
            "SUBJ": _fs({"CASE": "NOM"}, id_=2),
            "VOICE": "AV",
            "ASPECT": "PFV",
            "MOOD": "IND",
            "CASE": "NOM",
            "LEX-ASTRUCT": "ACTOR",
        })
        ok, _ = lfg_well_formed(f)
        assert ok

    def test_obl_typed_governable(self) -> None:
        # If the PRED doesn't name OBL-AG, having one is incoherent.
        f = _fs({
            "PRED": "EAT <SUBJ, OBJ>",
            "SUBJ": _fs({"CASE": "NOM"}, id_=2),
            "OBJ": _fs({"CASE": "GEN"}, id_=3),
            "OBL-AG": _fs({"CASE": "GEN"}, id_=4),
        })
        ok, diags = lfg_well_formed(f)
        assert not ok
        coh = [d for d in diags if d.kind == "coherence-failed"]
        assert any(d.detail.get("extra") == "OBL-AG" for d in coh)


# === Subject condition ====================================================

class TestSubjectCondition:
    def test_missing_subj_with_args(self) -> None:
        # Conjure an f-structure where PRED wants SUBJ but has only OBJ.
        # Completeness will also fire; subject-condition is independent
        # and should fire too whenever a non-0-ary PRED lacks SUBJ.
        f = _fs({
            "PRED": "EAT <OBJ>",
            "OBJ": _fs({"CASE": "GEN"}, id_=2),
        })
        ok, diags = lfg_well_formed(f)
        assert not ok
        kinds = [d.kind for d in diags]
        assert "subject-condition-failed" in kinds

    def test_zero_ary_pred_exempt(self) -> None:
        # 0-ary PREDs (the noun placeholder, weather verbs, ...) are
        # exempt from the subject condition.
        f = _fs({"PRED": "RAIN"})
        ok, diags = lfg_well_formed(f)
        assert ok
        assert diags == []

    def test_subj_present_passes(self) -> None:
        f = _fs({
            "PRED": "EAT <SUBJ, OBJ>",
            "SUBJ": _fs({"CASE": "NOM"}, id_=2),
            "OBJ": _fs({"CASE": "GEN"}, id_=3),
        })
        ok, _ = lfg_well_formed(f)
        assert ok


# === Reentrancy dedup =====================================================

class TestReentrancy:
    def test_shared_subtree_visited_once(self) -> None:
        # The same FStructure object reachable via two paths.
        shared = _fs({"PRED": "WALK <SUBJ>"}, id_=2)
        # PRED is set but no SUBJ — should fail the subject condition,
        # but only once.
        f = _fs({"X": shared, "Y": shared})
        ok, diags = lfg_well_formed(f)
        assert not ok
        sc = [d for d in diags if d.kind == "subject-condition-failed"]
        assert len(sc) == 1


# === Demo end-to-end ======================================================

class TestDemoWellFormed:
    def test_demo_passes(self) -> None:
        from tgllfg.core.pipeline import parse_text
        results = parse_text("Kinain ng aso ang isda.")
        assert len(results) >= 1
        ctree, f, a, diags = results[0]
        # No blocking diagnostics — they would have suppressed the parse.
        assert all(not d.is_blocking() for d in diags)


# === Pipeline integration: blocking diagnostic suppresses parse ===========

class TestPipelineFiltering:
    def test_synthesised_coherence_violation_suppressed(self) -> None:
        # Build a c-tree by hand whose equations introduce a governable
        # GF (OBL-AG) that the PRED template doesn't name. The pipeline
        # should suppress this parse.
        from tgllfg.core.common import CNode
        from tgllfg.fstruct import lfg_well_formed
        from tgllfg.fstruct import solve

        node = CNode(
            label="S",
            equations=[
                "(↑ PRED) = 'EAT <SUBJ, OBJ>'",
                "(↑ SUBJ) = ↓1",
                "(↑ OBL-AG) = ↓2",  # not in PRED's args — incoherent
            ],
            children=[
                CNode(label="X1", equations=["(↑ CASE) = 'NOM'"]),
                CNode(label="X2", equations=["(↑ CASE) = 'GEN'"]),
            ],
        )
        result = solve(node)
        ok, diags = lfg_well_formed(result.fstructure)
        assert not ok
        kinds = [d.kind for d in diags]
        assert "coherence-failed" in kinds
        assert any(d.is_blocking() for d in diags)
        # Plus completeness should *not* fire — both SUBJ and OBJ
        # named by PRED must be present. SUBJ is. OBJ isn't, so
        # completeness fires too.
        assert any(d.kind == "completeness-failed" for d in diags)


# === Diagnostic shape =====================================================

class TestDiagnosticShape:
    def test_path_records_location(self) -> None:
        # Nested PRED-bearing f-structure with a coherence violation.
        nested = _fs({
            "PRED": "WALK <SUBJ>",
            "SUBJ": _fs({"CASE": "NOM"}, id_=3),
            "OBJ": _fs({"CASE": "GEN"}, id_=4),
        }, id_=2)
        f = _fs({
            "PRED": "EAT <SUBJ, OBJ>",
            "SUBJ": _fs({"CASE": "NOM"}, id_=5),
            "OBJ": _fs({"CASE": "GEN"}, id_=6),
            "XCOMP": nested,
        })
        ok, diags = lfg_well_formed(f)
        assert not ok
        # Top-level f also names XCOMP via no PRED arg → coherence
        # failure on root. The nested f has extra OBJ → coherence at
        # XCOMP path.
        coh = [d for d in diags if d.kind == "coherence-failed"]
        # The XCOMP-path violation should record path == ("XCOMP",).
        nested_violations = [d for d in coh if d.path == ("XCOMP",)]
        assert nested_violations
        assert nested_violations[0].detail["extra"] == "OBJ"

    def test_pred_recorded_in_detail(self) -> None:
        f = _fs({
            "PRED": "EAT <SUBJ, OBJ>",
            "OBJ": _fs({"CASE": "GEN"}, id_=2),
        })
        ok, diags = lfg_well_formed(f)
        assert not ok
        for d in diags:
            assert d.detail.get("pred") == "EAT"


# === is_blocking on Diagnostic ============================================

class TestIsBlocking:
    def test_well_formedness_kinds_block(self) -> None:
        from tgllfg.fstruct import Diagnostic
        for kind in (
            "completeness-failed",
            "coherence-failed",
            "subject-condition-failed",
        ):
            d = Diagnostic(kind=kind, message="x")  # type: ignore[arg-type]
            assert d.is_blocking()

    def test_deferred_does_not_block(self) -> None:
        from tgllfg.fstruct import Diagnostic
        d = Diagnostic(kind="deferred", message="x")
        assert not d.is_blocking()

    def test_unsupported_does_not_block(self) -> None:
        from tgllfg.fstruct import Diagnostic
        d = Diagnostic(kind="unsupported", message="x")
        assert not d.is_blocking()
