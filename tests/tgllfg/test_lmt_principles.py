"""Phase 5 §8.2 — Bresnan–Kanerva LMT principles.

Unit tests for each principle as a standalone function plus
orchestrator smoke tests for :func:`compute_mapping`. The full
per-voice corpus (AV/OV/DV/IV transitives, intransitives, BEN
applicatives, causatives, psych control) lives in
``test_lmt_voice_mappings.py``; this file is the isolation-level
safety net for each principle.
"""

from __future__ import annotations

import pytest

from tgllfg.fstruct import Diagnostic
from tgllfg.lmt import (
    ROLE_HIERARCHY,
    IntrinsicClassification,
    IntrinsicFeatures,
    Role,
    apply_voice_constraints,
    check_biuniqueness,
    check_subject_condition,
    compute_mapping,
    default_intrinsics,
    fill_defaults,
    non_subject_mapping,
    subject_mapping,
)


def _ic(role: Role, r: bool | None = None, o: bool | None = None) -> IntrinsicClassification:
    """Test helper: build an :class:`IntrinsicClassification` with
    optional ternary features."""
    return IntrinsicClassification(role=role, intrinsics=IntrinsicFeatures(r=r, o=o))


# === Role hierarchy =======================================================


class TestRoleHierarchy:
    """The hierarchy is rarely load-bearing for fully-pinned Tagalog
    profiles, but step 3 default-fill and step 4 tiebreakers consult
    it. The invariants below catch typos and accidental reorderings."""

    def test_agent_is_highest(self) -> None:
        assert ROLE_HIERARCHY[0] is Role.AGENT

    def test_actor_and_causer_near_agent(self) -> None:
        # Tagalog augmentation: ACTOR ≅ AGENT (intransitive),
        # CAUSER ≅ AGENT (causative). They should sort directly
        # after AGENT so step 4 picks them as SUBJ candidates when
        # the lex entry is permissive.
        agent_idx = ROLE_HIERARCHY.index(Role.AGENT)
        actor_idx = ROLE_HIERARCHY.index(Role.ACTOR)
        causer_idx = ROLE_HIERARCHY.index(Role.CAUSER)
        assert actor_idx == agent_idx + 1
        assert causer_idx == agent_idx + 2

    def test_patient_above_location(self) -> None:
        # PATIENT/THEME above LOCATION matches B&K 1989 thematic
        # hierarchy; LOCATION is the bottom of the per-role table.
        assert ROLE_HIERARCHY.index(Role.PATIENT) < ROLE_HIERARCHY.index(Role.LOCATION)
        assert ROLE_HIERARCHY.index(Role.THEME) < ROLE_HIERARCHY.index(Role.LOCATION)

    def test_complement_event_at_bottom(self) -> None:
        # XCOMP-bound roles sort last so step 3 default-fill prefers
        # plain-thematic roles for the [-o] stamp.
        last_two = ROLE_HIERARCHY[-2:]
        assert set(last_two) == {Role.COMPLEMENT, Role.EVENT}

    def test_no_duplicates(self) -> None:
        assert len(set(ROLE_HIERARCHY)) == len(ROLE_HIERARCHY)

    def test_covers_all_roles(self) -> None:
        # Every Role enum member should appear in the hierarchy so
        # _hierarchy_index never returns the fallback value.
        assert set(ROLE_HIERARCHY) == set(Role)


# === default_intrinsics ===================================================


class TestDefaultIntrinsics:
    """The B&K 1989 canonical intrinsic table. Used by the lex-entry
    bootstrap to fill empty ``intrinsic_classification`` JSONB; the
    runtime engine doesn't consult it directly."""

    @pytest.mark.parametrize("role", [
        Role.AGENT, Role.ACTOR, Role.CAUSER,
        Role.EXPERIENCER, Role.BENEFICIARY, Role.RECIPIENT,
        Role.GOAL, Role.INSTRUMENT, Role.LOCATION,
    ])
    def test_non_objective_roles(self, role: Role) -> None:
        # [-o]: cannot be OBJ-typed.
        assert default_intrinsics(role) == IntrinsicFeatures(o=False)

    @pytest.mark.parametrize("role", [
        Role.PATIENT, Role.THEME, Role.CONVEYED,
        Role.CAUSEE, Role.STIMULUS,
    ])
    def test_unrestricted_roles(self, role: Role) -> None:
        # [-r]: patient-like, default OBJ-or-SUBJ candidates.
        assert default_intrinsics(role) == IntrinsicFeatures(r=False)

    @pytest.mark.parametrize("role", [Role.COMPLEMENT, Role.EVENT])
    def test_xcomp_roles_have_no_default(self, role: Role) -> None:
        # Off-truth-table: handled via stipulated_gfs.
        assert default_intrinsics(role) == IntrinsicFeatures()


# === apply_voice_constraints ==============================================


class TestApplyVoiceConstraints:

    def test_none_constraints_is_noop(self) -> None:
        frame = [_ic(Role.AGENT, o=False), _ic(Role.PATIENT, r=False)]
        assert apply_voice_constraints(frame) == frame
        assert apply_voice_constraints(frame, voice_constraints=None) == frame
        assert apply_voice_constraints(frame, voice_constraints={}) == frame

    def test_constraint_merges_into_unspecified(self) -> None:
        frame = [_ic(Role.AGENT, o=False)]
        result = apply_voice_constraints(
            frame, voice_constraints={Role.AGENT: IntrinsicFeatures(r=False)}
        )
        assert result == [_ic(Role.AGENT, r=False, o=False)]

    def test_constraint_unaffected_role_passes_through(self) -> None:
        frame = [_ic(Role.AGENT), _ic(Role.PATIENT, r=False)]
        result = apply_voice_constraints(
            frame, voice_constraints={Role.AGENT: IntrinsicFeatures(r=False)}
        )
        assert result == [_ic(Role.AGENT, r=False), _ic(Role.PATIENT, r=False)]

    def test_constraint_conflict_raises(self) -> None:
        frame = [_ic(Role.AGENT, r=True)]
        with pytest.raises(ValueError, match=r"intrinsic feature 'r' conflict"):
            apply_voice_constraints(
                frame, voice_constraints={Role.AGENT: IntrinsicFeatures(r=False)}
            )


# === fill_defaults ========================================================


class TestFillDefaults:

    def test_complete_frame_is_noop(self) -> None:
        # The Tagalog per-voice profile case: every (r, o) is pinned
        # by the lex entry. Step 3 has nothing to do.
        frame = [
            _ic(Role.AGENT, r=False, o=False),
            _ic(Role.PATIENT, r=False, o=True),
        ]
        assert fill_defaults(frame) == frame

    def test_highest_unmarked_gets_minus_o(self) -> None:
        # No role has o=False yet; step 3 stamps the highest-hierarchy
        # role with o=None as [-o] so step 4 has a SUBJ candidate.
        frame = [_ic(Role.PATIENT), _ic(Role.AGENT)]
        result = fill_defaults(frame)
        # AGENT got [-o]; PATIENT got default [+o] from the second pass.
        roles_to_o = {ic.role: ic.intrinsics.o for ic in result}
        assert roles_to_o[Role.AGENT] is False
        assert roles_to_o[Role.PATIENT] is True

    def test_minus_o_already_present_skips_first_pass(self) -> None:
        # AGENT has [-o] from intrinsics; PATIENT has [-r]. Step 3
        # only needs to fill PATIENT.o → +o, not stamp anyone with
        # [-o] (the first pass is a no-op).
        frame = [_ic(Role.AGENT, o=False), _ic(Role.PATIENT, r=False)]
        result = fill_defaults(frame)
        assert result == [
            _ic(Role.AGENT, r=True, o=False),
            _ic(Role.PATIENT, r=False, o=True),
        ]

    def test_unspecified_r_defaults_to_plus_r(self) -> None:
        frame = [_ic(Role.AGENT, o=False)]
        result = fill_defaults(frame)
        assert result == [_ic(Role.AGENT, r=True, o=False)]

    def test_unspecified_o_defaults_to_plus_o_when_minus_o_exists(self) -> None:
        frame = [_ic(Role.AGENT, o=False), _ic(Role.PATIENT, r=False)]
        result = fill_defaults(frame)
        # PATIENT.o defaults to +o because AGENT already supplies [-o].
        roles_to_o = {ic.role: ic.intrinsics.o for ic in result}
        assert roles_to_o[Role.PATIENT] is True

    def test_empty_frame(self) -> None:
        assert fill_defaults([]) == []


# === subject_mapping ======================================================


class TestSubjectMapping:

    def test_single_minus_r_minus_o(self) -> None:
        frame = [
            _ic(Role.AGENT, r=True, o=True),
            _ic(Role.PATIENT, r=False, o=False),
        ]
        assert subject_mapping(frame) == 1

    def test_highest_hierarchy_wins_among_minus_r_minus_o(self) -> None:
        # Two roles both [-r, -o]: hierarchy decides. AGENT is
        # higher than PATIENT.
        frame = [
            _ic(Role.PATIENT, r=False, o=False),
            _ic(Role.AGENT, r=False, o=False),
        ]
        assert subject_mapping(frame) == 1  # AGENT

    def test_falls_back_to_minus_o(self) -> None:
        # No role is [-r, -o] but AGENT has o=False.
        frame = [
            _ic(Role.AGENT, r=True, o=False),
            _ic(Role.PATIENT, r=True, o=True),
        ]
        assert subject_mapping(frame) == 0

    def test_falls_back_to_minus_r(self) -> None:
        # No role has o=False but PATIENT has r=False.
        frame = [
            _ic(Role.AGENT, r=True, o=True),
            _ic(Role.PATIENT, r=False, o=True),
        ]
        assert subject_mapping(frame) == 1

    def test_returns_none_when_no_candidate(self) -> None:
        # All roles [+r, +o]: none can be SUBJ.
        frame = [
            _ic(Role.AGENT, r=True, o=True),
            _ic(Role.PATIENT, r=True, o=True),
        ]
        assert subject_mapping(frame) is None

    def test_empty_frame_returns_none(self) -> None:
        assert subject_mapping([]) is None

    def test_minus_r_minus_o_outranks_lone_minus_o(self) -> None:
        # PATIENT [-r, -o] beats AGENT [+r, -o] (full SUBJ-eligibility
        # outranks compatible-with-[-o] alone). This is what makes
        # IV-CONVEY's CONVEYED win over its OBL-θ co-arguments.
        frame = [
            _ic(Role.AGENT, r=True, o=False),
            _ic(Role.PATIENT, r=False, o=False),
        ]
        assert subject_mapping(frame) == 1


# === non_subject_mapping ==================================================


class TestNonSubjectMapping:

    def test_minus_r_plus_o_is_bare_obj(self) -> None:
        assert non_subject_mapping(
            Role.PATIENT, IntrinsicFeatures(r=False, o=True)
        ) == "OBJ"

    def test_plus_r_plus_o_is_obj_theta(self) -> None:
        assert non_subject_mapping(
            Role.AGENT, IntrinsicFeatures(r=True, o=True)
        ) == "OBJ-AGENT"
        assert non_subject_mapping(
            Role.PATIENT, IntrinsicFeatures(r=True, o=True)
        ) == "OBJ-PATIENT"

    def test_plus_r_minus_o_is_obl_theta(self) -> None:
        assert non_subject_mapping(
            Role.LOCATION, IntrinsicFeatures(r=True, o=False)
        ) == "OBL-LOC"
        assert non_subject_mapping(
            Role.BENEFICIARY, IntrinsicFeatures(r=True, o=False)
        ) == "OBL-BEN"
        assert non_subject_mapping(
            Role.GOAL, IntrinsicFeatures(r=True, o=False)
        ) == "OBL-GOAL"

    def test_minus_r_minus_o_raises(self) -> None:
        # SUBJ-eligible roles must be picked by step 4.
        with pytest.raises(ValueError, match=r"SUBJ-eligible"):
            non_subject_mapping(
                Role.AGENT, IntrinsicFeatures(r=False, o=False)
            )

    def test_unspecified_features_raise(self) -> None:
        with pytest.raises(ValueError, match=r"requires fully-specified"):
            non_subject_mapping(Role.AGENT, IntrinsicFeatures(r=False))
        with pytest.raises(ValueError, match=r"requires fully-specified"):
            non_subject_mapping(Role.AGENT, IntrinsicFeatures(o=False))


# === check_subject_condition ==============================================


class TestCheckSubjectCondition:

    def test_subj_present_returns_none(self) -> None:
        mapping = {Role.AGENT: "SUBJ", Role.PATIENT: "OBJ"}
        assert check_subject_condition(mapping) is None

    def test_no_subj_emits_diagnostic(self) -> None:
        mapping = {Role.AGENT: "OBJ", Role.PATIENT: "OBJ-PATIENT"}
        diag = check_subject_condition(mapping)
        assert diag is not None
        assert diag.kind == "subject-condition-failed"
        assert "no role maps to SUBJ" in diag.message

    def test_pred_name_appears_in_message(self) -> None:
        mapping: dict[Role, str] = {}
        diag = check_subject_condition(mapping, pred_name="EAT")
        assert diag is not None
        assert "EAT" in diag.message


# === check_biuniqueness ===================================================


class TestCheckBiuniqueness:

    def test_distinct_gfs_no_diagnostic(self) -> None:
        mapping = {
            Role.AGENT: "SUBJ",
            Role.PATIENT: "OBJ",
            Role.LOCATION: "OBL-LOC",
        }
        assert check_biuniqueness(mapping) == ()

    def test_duplicate_gf_emits_diagnostic(self) -> None:
        mapping = {Role.AGENT: "OBJ", Role.PATIENT: "OBJ"}
        diags = check_biuniqueness(mapping)
        assert len(diags) == 1
        assert diags[0].kind == "lmt-biuniqueness-violated"
        assert "OBJ" in diags[0].message

    def test_typed_obj_distinct_from_other_typed_obj(self) -> None:
        # OBJ-AGENT and OBJ-PATIENT are distinct GFs; no clash.
        mapping = {Role.AGENT: "OBJ-AGENT", Role.PATIENT: "OBJ-PATIENT"}
        assert check_biuniqueness(mapping) == ()

    def test_typed_obj_distinct_from_bare_obj(self) -> None:
        mapping = {Role.AGENT: "OBJ-AGENT", Role.PATIENT: "OBJ"}
        assert check_biuniqueness(mapping) == ()


# === compute_mapping (orchestration) ======================================


class TestComputeMapping:
    """Smoke tests for the orchestrator. The per-voice corpus
    (AV/OV/DV/IV/applicatives/causatives) lives in
    ``test_lmt_voice_mappings.py``."""

    def test_av_transitive_profile(self) -> None:
        # AV-kain: AGENT [-r, -o] (pivot), PATIENT [-r, +o] (OBJ).
        result = compute_mapping([
            _ic(Role.AGENT, r=False, o=False),
            _ic(Role.PATIENT, r=False, o=True),
        ])
        assert result.mapping == {Role.AGENT: "SUBJ", Role.PATIENT: "OBJ"}
        assert result.diagnostics == ()

    def test_ov_transitive_profile(self) -> None:
        # OV-kain: PATIENT [-r, -o] (pivot), AGENT [+r, +o] (OBJ-AGENT).
        # Per question #1's "1 upgrade" decision, ng-non-pivot is
        # OBJ-θ, not bare OBJ.
        result = compute_mapping([
            _ic(Role.AGENT, r=True, o=True),
            _ic(Role.PATIENT, r=False, o=False),
        ])
        assert result.mapping == {
            Role.AGENT: "OBJ-AGENT",
            Role.PATIENT: "SUBJ",
        }
        assert result.diagnostics == ()

    def test_intransitive_profile(self) -> None:
        # AV-intr: ACTOR [-r, -o] only.
        result = compute_mapping([_ic(Role.ACTOR, r=False, o=False)])
        assert result.mapping == {Role.ACTOR: "SUBJ"}
        assert result.diagnostics == ()

    def test_iv_convey_three_arg_profile(self) -> None:
        # IV-bigay: AGENT [+r, +o], CONVEYED [-r, -o] (pivot),
        # GOAL [+r, -o] (OBL-θ via sa-marking).
        result = compute_mapping([
            _ic(Role.AGENT, r=True, o=True),
            _ic(Role.CONVEYED, r=False, o=False),
            _ic(Role.GOAL, r=True, o=False),
        ])
        assert result.mapping == {
            Role.AGENT: "OBJ-AGENT",
            Role.CONVEYED: "SUBJ",
            Role.GOAL: "OBL-GOAL",
        }
        assert result.diagnostics == ()

    def test_psych_control_with_stipulated_xcomp(self) -> None:
        # gusto: EXPERIENCER [-r, -o] (SUBJ), COMPLEMENT → XCOMP
        # stipulated by lex entry.
        result = compute_mapping(
            [
                _ic(Role.EXPERIENCER, r=False, o=False),
                _ic(Role.COMPLEMENT),
            ],
            stipulated_gfs={Role.COMPLEMENT: "XCOMP"},
        )
        assert result.mapping == {
            Role.EXPERIENCER: "SUBJ",
            Role.COMPLEMENT: "XCOMP",
        }
        assert result.diagnostics == ()

    def test_voice_constraints_layer(self) -> None:
        # Voice constraint: AGENT gets [-r] from voice morphology
        # in addition to its lex-entry [-o] intrinsic. Step 3
        # default-fills PATIENT.o → +o.
        result = compute_mapping(
            [_ic(Role.AGENT, o=False), _ic(Role.PATIENT, r=False)],
            voice_constraints={Role.AGENT: IntrinsicFeatures(r=False)},
        )
        assert result.mapping == {Role.AGENT: "SUBJ", Role.PATIENT: "OBJ"}
        assert result.diagnostics == ()

    def test_no_subject_emits_diagnostic(self) -> None:
        # All roles [+r, +o]: no SUBJ candidate.
        result = compute_mapping([
            _ic(Role.AGENT, r=True, o=True),
            _ic(Role.PATIENT, r=True, o=True),
        ])
        assert "SUBJ" not in result.mapping.values()
        assert any(
            d.kind == "subject-condition-failed" for d in result.diagnostics
        )

    def test_duplicate_subj_candidate_emits_biuniqueness_diag(self) -> None:
        # Two roles both [-r, -o]: step 4 picks AGENT, PATIENT is
        # leftover and surfaced as a biuniqueness violation.
        result = compute_mapping([
            _ic(Role.AGENT, r=False, o=False),
            _ic(Role.PATIENT, r=False, o=False),
        ])
        # AGENT wins step 4 by hierarchy.
        assert result.mapping[Role.AGENT] == "SUBJ"
        # PATIENT is the leftover SUBJ candidate.
        biuniq_diags = [
            d for d in result.diagnostics
            if d.kind == "lmt-biuniqueness-violated"
        ]
        assert len(biuniq_diags) >= 1
        assert "PATIENT" in biuniq_diags[0].message

    def test_pred_name_threads_through_to_subject_diag(self) -> None:
        result = compute_mapping(
            [_ic(Role.AGENT, r=True, o=True)],
            pred_name="GAWA",
        )
        diags = [
            d for d in result.diagnostics
            if d.kind == "subject-condition-failed"
        ]
        assert len(diags) == 1
        assert "GAWA" in diags[0].message

    def test_empty_frame(self) -> None:
        # No roles at all: trivially Subject Condition fails.
        result = compute_mapping([])
        assert result.mapping == {}
        assert any(
            d.kind == "subject-condition-failed" for d in result.diagnostics
        )

    def test_diagnostics_are_diagnostic_instances(self) -> None:
        # Sanity: the diagnostic field carries proper Diagnostic
        # records (matters for downstream is_blocking() dispatch).
        result = compute_mapping([])
        for d in result.diagnostics:
            assert isinstance(d, Diagnostic)
