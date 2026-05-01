"""Phase 5 §8.2 — per-voice mapping corpus.

Regression net for the LMT engine. Each test corresponds to a
Phase 4 anchor pattern from :mod:`tgllfg.lexicon` and asserts that
:func:`tgllfg.lmt.compute_mapping` produces the expected role-to-GF
mapping for the per-voice ``[±r, ±o]`` profile attached to the
corresponding lex entry.

The Phase 4 ``gf_defaults`` mappings are listed alongside each case
for traceability; the LMT mappings differ for non-AV ``ng``-non-pivots
(``OBJ`` → ``OBJ-θ`` per the Phase 5 upgrade decision).

If a test here fails after touching :mod:`tgllfg.lmt.principles`,
treat the failure as load-bearing — it means the per-voice pivot
selection has shifted and downstream parses will produce different
GF assignments.
"""

from __future__ import annotations

import pytest

from tgllfg.lmt import (
    IntrinsicClassification,
    IntrinsicFeatures,
    Role,
    compute_mapping,
)


def _ic(
    role: Role, r: bool | None = None, o: bool | None = None
) -> IntrinsicClassification:
    return IntrinsicClassification(role=role, intrinsics=IntrinsicFeatures(r=r, o=o))


# === Plain voice — transitive and intransitive ============================


class TestPlainVoiceTransitives:
    """The four-voice system on a regular transitive verb. Phase 4
    anchor patterns: kain, bili, basa, sulat, gawa, tapon."""

    def test_av_transitive(self) -> None:
        # kumain ng isda — "ate fish".
        # Phase 4 gf_defaults: {AGENT: SUBJ, PATIENT: OBJ}.
        result = compute_mapping([
            _ic(Role.AGENT, r=False, o=False),
            _ic(Role.PATIENT, r=False, o=True),
        ])
        assert result.mapping == {Role.AGENT: "SUBJ", Role.PATIENT: "OBJ"}
        assert result.diagnostics == ()

    def test_av_transitive_with_theme(self) -> None:
        # bumili ng aklat — "bought a book". Anchor verbs bili/basa/
        # sulat use THEME instead of PATIENT.
        # Phase 4 gf_defaults: {AGENT: SUBJ, THEME: OBJ}.
        result = compute_mapping([
            _ic(Role.AGENT, r=False, o=False),
            _ic(Role.THEME, r=False, o=True),
        ])
        assert result.mapping == {Role.AGENT: "SUBJ", Role.THEME: "OBJ"}
        assert result.diagnostics == ()

    def test_ov_transitive(self) -> None:
        # kinain ng bata ang isda — "the child ate the fish".
        # Phase 4 gf_defaults: {PATIENT: SUBJ, AGENT: OBJ}.
        # LMT (post-upgrade): AGENT → OBJ-AGENT.
        result = compute_mapping([
            _ic(Role.AGENT, r=True, o=True),
            _ic(Role.PATIENT, r=False, o=False),
        ])
        assert result.mapping == {
            Role.AGENT: "OBJ-AGENT",
            Role.PATIENT: "SUBJ",
        }
        assert result.diagnostics == ()

    def test_ov_transitive_with_theme(self) -> None:
        # binili ng bata ang aklat — "the child bought the book".
        result = compute_mapping([
            _ic(Role.AGENT, r=True, o=True),
            _ic(Role.THEME, r=False, o=False),
        ])
        assert result.mapping == {
            Role.AGENT: "OBJ-AGENT",
            Role.THEME: "SUBJ",
        }
        assert result.diagnostics == ()

    def test_dv_transitive_recipient_pivot(self) -> None:
        # sinulatan ni Juan ang kanyang ina — "Juan wrote to his mother".
        # Phase 4 gf_defaults: {RECIPIENT: SUBJ, AGENT: OBJ}.
        # LMT: AGENT → OBJ-AGENT.
        result = compute_mapping([
            _ic(Role.AGENT, r=True, o=True),
            _ic(Role.RECIPIENT, r=False, o=False),
        ])
        assert result.mapping == {
            Role.AGENT: "OBJ-AGENT",
            Role.RECIPIENT: "SUBJ",
        }
        assert result.diagnostics == ()

    def test_iv_conveyed_pivot(self) -> None:
        # itinapon niya ang basura — "he threw out the garbage".
        # Phase 4 gf_defaults: {CONVEYED: SUBJ, AGENT: OBJ}.
        # LMT: AGENT → OBJ-AGENT.
        result = compute_mapping([
            _ic(Role.AGENT, r=True, o=True),
            _ic(Role.CONVEYED, r=False, o=False),
        ])
        assert result.mapping == {
            Role.AGENT: "OBJ-AGENT",
            Role.CONVEYED: "SUBJ",
        }
        assert result.diagnostics == ()


class TestPlainVoiceIntransitives:
    """AV-intransitive entries added in Phase 4 §7.10 for bili/basa/
    sulat to support sentences like "Bumili siya sa palengke" without
    an explicit patient. The lex entry uses a single ACTOR or AGENT
    role — both should pivot to SUBJ."""

    def test_av_intransitive_actor(self) -> None:
        # kumain — "ate" (intransitive). kain's intrans entry uses ACTOR.
        result = compute_mapping([_ic(Role.ACTOR, r=False, o=False)])
        assert result.mapping == {Role.ACTOR: "SUBJ"}
        assert result.diagnostics == ()

    def test_av_intransitive_agent(self) -> None:
        # bumili — "bought" (intransitive). bili/basa/sulat's intrans
        # entries use AGENT.
        result = compute_mapping([_ic(Role.AGENT, r=False, o=False)])
        assert result.mapping == {Role.AGENT: "SUBJ"}
        assert result.diagnostics == ()


# === Applicatives (§7.7 IV-BEN) ===========================================


class TestBenefactiveApplicative:
    """ipag- BEN applicative IV (Phase 4 §7.7): the pivot is the
    beneficiary; the agent demotes to OBJ-AGENT. Multi-GEN-NP
    frames (with patient still in play) are deferred to Phase 5b."""

    def test_ipag_ben_applicative(self) -> None:
        # ipinaggawa niya ako — "he made [it] for me".
        # Phase 4 gf_defaults: {BENEFICIARY: SUBJ, AGENT: OBJ}.
        # LMT: AGENT → OBJ-AGENT.
        result = compute_mapping([
            _ic(Role.AGENT, r=True, o=True),
            _ic(Role.BENEFICIARY, r=False, o=False),
        ])
        assert result.mapping == {
            Role.AGENT: "OBJ-AGENT",
            Role.BENEFICIARY: "SUBJ",
        }
        assert result.diagnostics == ()


# === Causatives (§7.7 pa- / magpa-) =======================================


class TestDirectCausative:
    """pa- direct (monoclausal) causative OV: causee is pivot
    (NOM-marked), causer demotes to OBJ-CAUSER. Single-clause; the
    embedded eventuality is folded into the matrix PRED."""

    def test_pa_in_direct_causative(self) -> None:
        # pinakain niya ang bata — "he fed the child".
        # Phase 4 gf_defaults: {CAUSEE: SUBJ, CAUSER: OBJ}.
        # LMT: CAUSER → OBJ-CAUSER.
        result = compute_mapping([
            _ic(Role.CAUSER, r=True, o=True),
            _ic(Role.CAUSEE, r=False, o=False),
        ])
        assert result.mapping == {
            Role.CAUSER: "OBJ-CAUSER",
            Role.CAUSEE: "SUBJ",
        }
        assert result.diagnostics == ()


class TestIndirectCausative:
    """magpa- indirect (biclausal) causative AV: causer is matrix
    SUBJ, the caused event is XCOMP. Re-uses §7.6 control
    infrastructure — the engine sees [CAUSER, EVENT] with EVENT
    stipulated as XCOMP. The causee surfaces inside the XCOMP
    f-structure as its SUBJ; the matrix LMT only handles CAUSER and
    EVENT."""

    def test_magpa_indirect_causative(self) -> None:
        # nagpakain siya ng aso — "he had the dog fed" / "he fed the dog
        # via someone else".
        # Phase 4 gf_defaults: {CAUSER: SUBJ, EVENT: XCOMP}.
        result = compute_mapping(
            [
                _ic(Role.CAUSER, r=False, o=False),
                _ic(Role.EVENT),
            ],
            stipulated_gfs={Role.EVENT: "XCOMP"},
        )
        assert result.mapping == {
            Role.CAUSER: "SUBJ",
            Role.EVENT: "XCOMP",
        }
        assert result.diagnostics == ()


# === Control verbs (§7.6) =================================================


class TestPsychControl:
    """Psych predicates (gusto / ayaw / kaya): GEN-experiencer maps
    to matrix SUBJ — a deviation from the NOM→SUBJ default that is
    encoded by giving EXPERIENCER the [-r, -o] intrinsic in the lex
    entry. PRED is <SUBJ, XCOMP> (no OBJ)."""

    @pytest.mark.parametrize("lemma", ["gusto", "ayaw", "kaya"])
    def test_psych_predicate_experiencer_subj(self, lemma: str) -> None:
        # Gusto kong kumain — "I want to eat".
        # Phase 4 gf_defaults: {EXPERIENCER: SUBJ, COMPLEMENT: XCOMP}.
        result = compute_mapping(
            [
                _ic(Role.EXPERIENCER, r=False, o=False),
                _ic(Role.COMPLEMENT),
            ],
            stipulated_gfs={Role.COMPLEMENT: "XCOMP"},
            pred_name=lemma.upper(),
        )
        assert result.mapping == {
            Role.EXPERIENCER: "SUBJ",
            Role.COMPLEMENT: "XCOMP",
        }
        assert result.diagnostics == ()


class TestIntransitiveControl:
    """Intransitive control (payag → pumayag): AV-only, NOM-NP is
    matrix SUBJ. AGREE <SUBJ, XCOMP>."""

    def test_intransitive_control(self) -> None:
        # Pumayag siyang kumain — "he agreed to eat".
        # Phase 4 gf_defaults: {AGENT: SUBJ, COMPLEMENT: XCOMP}.
        result = compute_mapping(
            [
                _ic(Role.AGENT, r=False, o=False),
                _ic(Role.COMPLEMENT),
            ],
            stipulated_gfs={Role.COMPLEMENT: "XCOMP"},
        )
        assert result.mapping == {
            Role.AGENT: "SUBJ",
            Role.COMPLEMENT: "XCOMP",
        }
        assert result.diagnostics == ()


class TestTransitiveControl:
    """Transitive control: pivot is forcee/orderee (matrix SUBJ in
    OV / DV), GEN-NP is forcer/orderer (matrix OBJ-AGENT). 3-arg
    PRED <SUBJ, OBJ, XCOMP>."""

    def test_ov_transitive_control_pilit(self) -> None:
        # Pinilit siyang kumain — "she was forced to eat".
        # Phase 4 gf_defaults: {PATIENT: SUBJ, AGENT: OBJ, COMPLEMENT: XCOMP}.
        # LMT: AGENT → OBJ-AGENT.
        result = compute_mapping(
            [
                _ic(Role.AGENT, r=True, o=True),
                _ic(Role.PATIENT, r=False, o=False),
                _ic(Role.COMPLEMENT),
            ],
            stipulated_gfs={Role.COMPLEMENT: "XCOMP"},
        )
        assert result.mapping == {
            Role.AGENT: "OBJ-AGENT",
            Role.PATIENT: "SUBJ",
            Role.COMPLEMENT: "XCOMP",
        }
        assert result.diagnostics == ()

    def test_dv_transitive_control_utos(self) -> None:
        # Inutusan siyang kumain — "she was ordered to eat".
        # Phase 4 gf_defaults: {RECIPIENT: SUBJ, AGENT: OBJ, COMPLEMENT: XCOMP}.
        # LMT: AGENT → OBJ-AGENT.
        result = compute_mapping(
            [
                _ic(Role.AGENT, r=True, o=True),
                _ic(Role.RECIPIENT, r=False, o=False),
                _ic(Role.COMPLEMENT),
            ],
            stipulated_gfs={Role.COMPLEMENT: "XCOMP"},
        )
        assert result.mapping == {
            Role.AGENT: "OBJ-AGENT",
            Role.RECIPIENT: "SUBJ",
            Role.COMPLEMENT: "XCOMP",
        }
        assert result.diagnostics == ()


# === Multi-GEN-NP frames (engine-side mappings) ===========================


class TestMultiGenFrames:
    """Multi-GEN-NP applicative / causative frames (ipag-BEN with
    patient still in play, pa-CAUS with causer + causee + patient).
    Phase 4 §7.7 deferred them; Phase 5b lifted both shapes via
    grammar + lex additions (IV-BEN multi-GEN, pa-OV-direct
    multi-GEN). These tests assert the LMT engine's mapping for
    those profiles — the engine has handled them all along; the
    earlier deferral was at the grammar/lex layer.
    """

    def test_iv_ben_three_arg_multi_gen(self) -> None:
        # Hypothetical: ipinaggawa niya ng silya ang kapatid niya —
        # "he made a chair for his sibling" (ng-AGENT, ng-PATIENT,
        # ang-BENEFICIARY).
        result = compute_mapping([
            _ic(Role.AGENT, r=True, o=True),
            _ic(Role.PATIENT, r=True, o=True),
            _ic(Role.BENEFICIARY, r=False, o=False),
        ])
        assert result.mapping == {
            Role.AGENT: "OBJ-AGENT",
            Role.PATIENT: "OBJ-PATIENT",
            Role.BENEFICIARY: "SUBJ",
        }
        assert result.diagnostics == ()

    def test_pa_in_direct_causative_three_arg_multi_gen(self) -> None:
        # Hypothetical: pinakain niya ng kanin ang bata — "he fed the
        # child rice" (ng-CAUSER, ng-PATIENT, ang-CAUSEE).
        result = compute_mapping([
            _ic(Role.CAUSER, r=True, o=True),
            _ic(Role.PATIENT, r=True, o=True),
            _ic(Role.CAUSEE, r=False, o=False),
        ])
        assert result.mapping == {
            Role.CAUSER: "OBJ-CAUSER",
            Role.PATIENT: "OBJ-PATIENT",
            Role.CAUSEE: "SUBJ",
        }
        assert result.diagnostics == ()


# === sa-NP OBL-θ classification ===========================================


class TestObliqueThetaClassification:
    """:mod:`tgllfg.lmt.oblique_classifier` reclassifies ADJUNCT
    members (sa-NPs) into typed OBL-θ slots based on the verb's
    a-structure. The LMT engine produces OBL-θ outputs from the
    [+r, -o] truth-table entry; these tests document the expected
    engine outputs that the post-solve classifier consumes."""

    def test_iv_convey_with_oblique_recipient(self) -> None:
        # ibinigay niya sa kanya ang pera — "he gave the money to her".
        # The sa-NP is the RECIPIENT/GOAL (OBL-θ); the pivot is
        # the conveyed entity (CONVEYED → SUBJ); ng-AGENT is OBJ-AGENT.
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

    def test_av_motion_with_oblique_location(self) -> None:
        # lumakad siya sa palengke — "she walked to the market".
        # AV-intransitive motion verb; the sa-NP is LOCATION,
        # classified as OBL-LOC by the post-solve classifier.
        result = compute_mapping([
            _ic(Role.ACTOR, r=False, o=False),
            _ic(Role.LOCATION, r=True, o=False),
        ])
        assert result.mapping == {
            Role.ACTOR: "SUBJ",
            Role.LOCATION: "OBL-LOC",
        }
        assert result.diagnostics == ()
