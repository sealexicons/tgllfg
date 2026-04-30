"""Phase 5 §8.1 — LMT data types.

Covers :class:`tgllfg.lmt.Role`, :class:`tgllfg.lmt.IntrinsicFeatures`,
:class:`tgllfg.lmt.IntrinsicClassification`,
:class:`tgllfg.lmt.MappingResult`, and the typed-GF helpers
:func:`tgllfg.lmt.obj_theta` / :func:`tgllfg.lmt.obl_theta`.
"""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from tgllfg.fstruct import Diagnostic, is_governable_gf
from tgllfg.lmt import (
    IntrinsicClassification,
    IntrinsicFeatures,
    MappingResult,
    Role,
    obj_theta,
    obl_theta,
)


# === Role inventory =======================================================


class TestRoleInventory:
    """The role inventory matches the plan §8.1 core plus the
    Tagalog augmentation that surfaced during Phase 4 §7."""

    def test_plan_core_roles_present(self) -> None:
        for name in (
            "AGENT", "PATIENT", "THEME", "GOAL", "RECIPIENT",
            "BENEFICIARY", "INSTRUMENT", "LOCATION", "EXPERIENCER",
            "STIMULUS",
        ):
            assert Role[name].value == name

    def test_tagalog_augmentation_present(self) -> None:
        for name in (
            "ACTOR", "CONVEYED", "CAUSER", "CAUSEE", "EVENT",
            "COMPLEMENT",
        ):
            assert Role[name].value == name

    def test_value_equals_name(self) -> None:
        # The LMT engine and the lexicon share role-name strings;
        # this invariant lets gf_defaults dicts (str -> str) map
        # losslessly into role-keyed dicts.
        for r in Role:
            assert r.value == r.name


class TestRoleGfSuffix:
    """``role.gf_suffix`` is the short tag used inside ``OBJ-X`` and
    ``OBL-X`` typed GF strings. Mapped roles use Tagalog-LFG
    convention; unmapped roles fall back to the bare role name."""

    @pytest.mark.parametrize("role,suffix", [
        (Role.LOCATION, "LOC"),
        (Role.BENEFICIARY, "BEN"),
        (Role.INSTRUMENT, "INSTR"),
        (Role.RECIPIENT, "RECIP"),
    ])
    def test_mapped_suffixes(self, role: Role, suffix: str) -> None:
        assert role.gf_suffix == suffix

    @pytest.mark.parametrize("role", [
        Role.AGENT, Role.PATIENT, Role.THEME, Role.GOAL,
        Role.EXPERIENCER, Role.STIMULUS, Role.ACTOR,
        Role.CONVEYED, Role.CAUSER, Role.CAUSEE, Role.EVENT,
        Role.COMPLEMENT,
    ])
    def test_unmapped_falls_back_to_name(self, role: Role) -> None:
        assert role.gf_suffix == role.value


# === IntrinsicFeatures ====================================================


class TestIntrinsicFeaturesIsComplete:
    def test_both_set_is_complete(self) -> None:
        assert IntrinsicFeatures(r=True, o=False).is_complete()
        assert IntrinsicFeatures(r=False, o=True).is_complete()

    def test_either_unset_is_incomplete(self) -> None:
        assert not IntrinsicFeatures(r=True).is_complete()
        assert not IntrinsicFeatures(o=False).is_complete()
        assert not IntrinsicFeatures().is_complete()


class TestIntrinsicFeaturesMerge:
    """``merged_with`` lets voice morphology layer constraints on
    top of lexical intrinsics (BK step 2)."""

    def test_merge_fills_unspecified_components(self) -> None:
        base = IntrinsicFeatures(r=False)
        voice = IntrinsicFeatures(o=True)
        merged = base.merged_with(voice)
        assert merged == IntrinsicFeatures(r=False, o=True)

    def test_merge_preserves_specified_components(self) -> None:
        base = IntrinsicFeatures(r=True, o=False)
        no_op = IntrinsicFeatures()
        assert base.merged_with(no_op) == base

    def test_merge_agrees_on_same_value(self) -> None:
        base = IntrinsicFeatures(r=True)
        voice = IntrinsicFeatures(r=True, o=False)
        assert base.merged_with(voice) == IntrinsicFeatures(r=True, o=False)

    def test_merge_conflict_raises(self) -> None:
        base = IntrinsicFeatures(r=True)
        voice = IntrinsicFeatures(r=False)
        with pytest.raises(ValueError, match=r"intrinsic feature 'r' conflict"):
            base.merged_with(voice)

    def test_merge_conflict_o_raises(self) -> None:
        base = IntrinsicFeatures(o=True)
        voice = IntrinsicFeatures(o=False)
        with pytest.raises(ValueError, match=r"intrinsic feature 'o' conflict"):
            base.merged_with(voice)


class TestIntrinsicFeaturesIdentity:
    """The dataclass is frozen — instances are hashable and value-equal."""

    def test_value_equality(self) -> None:
        assert IntrinsicFeatures(r=True, o=False) == IntrinsicFeatures(
            r=True, o=False
        )

    def test_hashable(self) -> None:
        s = {IntrinsicFeatures(r=True, o=False), IntrinsicFeatures(r=True, o=False)}
        assert len(s) == 1

    def test_inequality_on_different_features(self) -> None:
        assert IntrinsicFeatures(r=True) != IntrinsicFeatures(r=False)
        assert IntrinsicFeatures(r=True, o=True) != IntrinsicFeatures(r=True, o=False)


@given(
    r=st.sampled_from([None, True, False]),
    o=st.sampled_from([None, True, False]),
)
def test_intrinsic_features_construction_round_trip(
    r: bool | None, o: bool | None
) -> None:
    feats = IntrinsicFeatures(r=r, o=o)
    assert feats.r is r
    assert feats.o is o
    assert feats.is_complete() == (r is not None and o is not None)


# === IntrinsicClassification ==============================================


class TestIntrinsicClassification:
    def test_constructs_with_role_and_features(self) -> None:
        ic = IntrinsicClassification(
            role=Role.AGENT,
            intrinsics=IntrinsicFeatures(r=False, o=False),
        )
        assert ic.role is Role.AGENT
        assert ic.intrinsics == IntrinsicFeatures(r=False, o=False)

    def test_with_intrinsics_returns_copy(self) -> None:
        ic = IntrinsicClassification(
            role=Role.PATIENT,
            intrinsics=IntrinsicFeatures(r=False),
        )
        refined = ic.with_intrinsics(IntrinsicFeatures(r=False, o=True))
        assert refined.role is Role.PATIENT
        assert refined.intrinsics == IntrinsicFeatures(r=False, o=True)
        # Original is unchanged (frozen dataclass).
        assert ic.intrinsics == IntrinsicFeatures(r=False)


# === MappingResult ========================================================


class TestMappingResult:
    def test_no_diagnostics_default(self) -> None:
        result = MappingResult(mapping={Role.AGENT: "SUBJ", Role.PATIENT: "OBJ"})
        assert result.mapping[Role.AGENT] == "SUBJ"
        assert result.mapping[Role.PATIENT] == "OBJ"
        assert result.diagnostics == ()

    def test_carries_diagnostics(self) -> None:
        diag = Diagnostic(kind="lmt-mismatch", message="example")
        result = MappingResult(
            mapping={Role.ACTOR: "SUBJ"},
            diagnostics=(diag,),
        )
        assert result.diagnostics == (diag,)


# === Typed-GF helpers =====================================================


class TestTypedGfHelpers:
    """``obj_theta(role)`` / ``obl_theta(role)`` build the typed
    governable-function strings consumed by the BK truth table.
    Their output passes :func:`is_governable_gf` so the
    well-formedness checker accepts them as governable slots."""

    @pytest.mark.parametrize("role,expected", [
        (Role.LOCATION, "OBJ-LOC"),
        (Role.BENEFICIARY, "OBJ-BEN"),
        (Role.INSTRUMENT, "OBJ-INSTR"),
        (Role.RECIPIENT, "OBJ-RECIP"),
        (Role.PATIENT, "OBJ-PATIENT"),
        (Role.THEME, "OBJ-THEME"),
        (Role.GOAL, "OBJ-GOAL"),
    ])
    def test_obj_theta(self, role: Role, expected: str) -> None:
        assert obj_theta(role) == expected
        assert is_governable_gf(expected)

    @pytest.mark.parametrize("role,expected", [
        (Role.LOCATION, "OBL-LOC"),
        (Role.BENEFICIARY, "OBL-BEN"),
        (Role.INSTRUMENT, "OBL-INSTR"),
        (Role.RECIPIENT, "OBL-RECIP"),
        (Role.GOAL, "OBL-GOAL"),
    ])
    def test_obl_theta(self, role: Role, expected: str) -> None:
        assert obl_theta(role) == expected
        assert is_governable_gf(expected)


# === Re-export sanity =====================================================


def test_legacy_apply_lmt_still_re_exported() -> None:
    """Commits 1–4 keep the Phase 4 heuristic available so
    :mod:`tgllfg.pipeline` keeps working until commit 5 swaps the
    call site. Commit 8 deletes the wrapper and this test."""
    from tgllfg.lmt import apply_lmt

    assert callable(apply_lmt)
