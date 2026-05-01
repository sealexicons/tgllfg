"""Phase 5 §8 — lex-entry intrinsic profiles + LMT bridges.

Exercises the bridges between :mod:`tgllfg.lexicon` and the LMT
engine: every BASE entry carries an ``intrinsic_classification``,
:func:`tgllfg.lmt.intrinsics_for` reads it back into a role frame,
:func:`tgllfg.lmt.stipulated_gfs_for` extracts XCOMP/COMP slots, and
the synthesizer fallback (:func:`tgllfg.lexicon._synthesize_verb_entry`)
attaches a per-voice profile so verbs not in BASE still produce
typed mappings.
"""

from __future__ import annotations

import pytest

from tgllfg.common import LexicalEntry, MorphAnalysis
from tgllfg.fstruct.checks import parse_pred_template
from tgllfg.lexicon import BASE, _synthesize_verb_entry
from tgllfg.lmt import (
    IntrinsicFeatures,
    Role,
    compute_mapping,
    default_intrinsics,
    intrinsics_for,
    stipulated_gfs_for,
)


# === Coverage: every BASE entry has intrinsics ============================


class TestBaseCoverage:
    """Every hand-authored entry in :data:`tgllfg.lexicon.BASE`
    declares ``intrinsic_classification`` for every role in its
    ``a_structure``. A failure here means a new lex entry was
    added without per-voice intrinsics — the LMT bridge will fall
    back to defaults, which is rarely what we want for transitives."""

    def test_intrinsic_classification_is_present(self) -> None:
        missing: list[str] = []
        for lemma, entries in BASE.items():
            for entry in entries:
                if not entry.intrinsic_classification:
                    missing.append(f"{lemma}: {entry.pred}")
        assert missing == [], (
            "lex entries missing intrinsic_classification:\n  - "
            + "\n  - ".join(missing)
        )

    def test_intrinsic_keys_match_a_structure(self) -> None:
        # The intrinsics dict shouldn't carry stale keys; every key
        # should appear in a_structure.
        mismatches: list[str] = []
        for lemma, entries in BASE.items():
            for entry in entries:
                a_structure = set(entry.a_structure)
                ic_keys = set(entry.intrinsic_classification.keys())
                extra = ic_keys - a_structure
                if extra:
                    mismatches.append(
                        f"{lemma} ({entry.pred}): intrinsic keys "
                        f"{extra} not in a_structure"
                    )
        assert mismatches == [], "\n".join(mismatches)


# === Engine round-trip on every BASE entry ================================


class TestBaseRoundTrip:
    """For every BASE entry, the LMT engine produces a complete
    role→GF mapping with no diagnostics. The exact mapping per
    pattern is locked in by ``test_lmt_voice_mappings.py``; this
    test asserts the structural invariants that hold across all
    entries."""

    def test_every_entry_yields_complete_mapping(self) -> None:
        failures: list[str] = []
        for lemma, entries in BASE.items():
            for entry in entries:
                frame = intrinsics_for(entry)
                stipulated = stipulated_gfs_for(entry)
                result = compute_mapping(
                    frame,
                    stipulated_gfs=stipulated,
                    pred_name=entry.pred.split()[0],
                )
                expected_roles = {Role[r] for r in entry.a_structure}
                actual_roles = set(result.mapping.keys())
                if actual_roles != expected_roles:
                    failures.append(
                        f"{lemma} ({entry.pred}): expected roles "
                        f"{expected_roles}, got {actual_roles}"
                    )
                # Engine-emitted diagnostics are normally a smell. The
                # one exception is raising verbs (Phase 5c §7.6
                # follow-on, Commit 5): their PRED declares SUBJ as
                # non-thematic (outside ``<...>``), so the engine's
                # ``subject-condition-failed`` fires correctly — that's
                # the engine telling us no thematic role maps to SUBJ.
                # The non-thematic SUBJ is supplied structurally by the
                # raising-binding equation in the grammar.
                tmpl = parse_pred_template(entry.pred)
                is_raising = bool(tmpl.non_thematic)
                non_subj_diags = [
                    d for d in result.diagnostics
                    if not (
                        is_raising
                        and d.kind == "subject-condition-failed"
                    )
                ]
                if non_subj_diags:
                    failures.append(
                        f"{lemma} ({entry.pred}): diagnostics "
                        f"{[d.kind for d in non_subj_diags]}"
                    )
        assert failures == [], "\n".join(failures)

    def test_every_entry_has_a_subj(self) -> None:
        # Subject Condition is structural; every PRED-bearing entry
        # must produce SUBJ either (a) via the engine's thematic-role
        # mapping, or (b) as a non-thematic arg in the PRED template
        # (raising verbs — Phase 5c §7.6 follow-on, Commit 5).
        for lemma, entries in BASE.items():
            for entry in entries:
                frame = intrinsics_for(entry)
                stipulated = stipulated_gfs_for(entry)
                result = compute_mapping(frame, stipulated_gfs=stipulated)
                subj_from_mapping = sum(
                    1 for gf in result.mapping.values() if gf == "SUBJ"
                )
                tmpl = parse_pred_template(entry.pred)
                subj_from_non_thematic = sum(
                    1 for a in tmpl.non_thematic if a == "SUBJ"
                )
                assert subj_from_mapping + subj_from_non_thematic == 1, (
                    f"{lemma} ({entry.pred}): expected exactly 1 SUBJ "
                    f"source, got {subj_from_mapping} from mapping + "
                    f"{subj_from_non_thematic} from non-thematic"
                )


# === Specific patterns: end-to-end through BASE ===========================


def _entry_for(lemma: str, **constraints: str) -> LexicalEntry:
    """Pick the unique BASE entry for `lemma` matching every
    feature in `constraints`. Helper for the per-pattern tests."""
    for entry in BASE[lemma]:
        if all(
            entry.morph_constraints.get(k) == v
            for k, v in constraints.items()
        ):
            return entry
    raise KeyError(f"no BASE entry for {lemma!r} with {constraints!r}")


class TestBasePatternMappings:
    """Spot-check that the LMT engine produces the expected mapping
    for each Phase 4 anchor pattern when invoked through the lex
    entry. Mirrors ``test_lmt_voice_mappings.py`` but exercises the
    full ``BASE → intrinsics_for → compute_mapping`` chain."""

    def test_kain_av_intransitive(self) -> None:
        # AV-intr has no TR constraint; the entry without TR is the
        # intransitive ACTOR template (the only entry in BASE["kain"]
        # whose a_structure contains ACTOR).
        intr_entry = next(
            e for e in BASE["kain"]
            if "TR" not in e.morph_constraints and "ACTOR" in e.a_structure
        )
        frame = intrinsics_for(intr_entry)
        result = compute_mapping(frame)
        assert result.mapping == {Role.ACTOR: "SUBJ"}
        # The TR-AV transitive entry should also work.
        tr_entry = _entry_for("kain", VOICE="AV", TR="TR", APPL="NONE", CAUS="NONE")
        result = compute_mapping(intrinsics_for(tr_entry))
        assert result.mapping == {Role.AGENT: "SUBJ", Role.PATIENT: "OBJ"}

    def test_kain_ov_transitive(self) -> None:
        entry = _entry_for("kain", VOICE="OV", TR="TR", APPL="NONE", CAUS="NONE")
        result = compute_mapping(intrinsics_for(entry))
        # Per Q1 upgrade: AGENT → OBJ-AGENT in non-AV.
        assert result.mapping == {
            Role.AGENT: "OBJ-AGENT",
            Role.PATIENT: "SUBJ",
        }
        assert result.diagnostics == ()

    def test_sulat_dv_transitive(self) -> None:
        entry = _entry_for("sulat", VOICE="DV")
        result = compute_mapping(intrinsics_for(entry))
        assert result.mapping == {
            Role.AGENT: "OBJ-AGENT",
            Role.RECIPIENT: "SUBJ",
        }

    def test_sulat_iv_conveyed(self) -> None:
        entry = _entry_for("sulat", VOICE="IV", APPL="CONVEY")
        result = compute_mapping(intrinsics_for(entry))
        assert result.mapping == {
            Role.AGENT: "OBJ-AGENT",
            Role.CONVEYED: "SUBJ",
        }

    def test_gawa_iv_ben_applicative(self) -> None:
        entry = _entry_for("gawa", VOICE="IV", APPL="BEN")
        result = compute_mapping(intrinsics_for(entry))
        assert result.mapping == {
            Role.AGENT: "OBJ-AGENT",
            Role.BENEFICIARY: "SUBJ",
        }

    def test_kain_pa_in_direct_causative(self) -> None:
        entry = _entry_for("kain", VOICE="OV", CAUS="DIRECT")
        result = compute_mapping(intrinsics_for(entry))
        assert result.mapping == {
            Role.CAUSER: "OBJ-CAUSER",
            Role.CAUSEE: "SUBJ",
        }

    def test_kain_magpa_indirect_causative(self) -> None:
        entry = _entry_for(
            "kain", VOICE="AV", CAUS="INDIRECT", CTRL_CLASS="INTRANS"
        )
        result = compute_mapping(
            intrinsics_for(entry),
            stipulated_gfs=stipulated_gfs_for(entry),
        )
        assert result.mapping == {
            Role.CAUSER: "SUBJ",
            Role.EVENT: "XCOMP",
        }

    def test_gusto_psych_control(self) -> None:
        entry = BASE["gusto"][0]
        result = compute_mapping(
            intrinsics_for(entry),
            stipulated_gfs=stipulated_gfs_for(entry),
        )
        assert result.mapping == {
            Role.EXPERIENCER: "SUBJ",
            Role.COMPLEMENT: "XCOMP",
        }

    def test_payag_intransitive_control(self) -> None:
        entry = BASE["payag"][0]
        result = compute_mapping(
            intrinsics_for(entry),
            stipulated_gfs=stipulated_gfs_for(entry),
        )
        assert result.mapping == {
            Role.AGENT: "SUBJ",
            Role.COMPLEMENT: "XCOMP",
        }

    def test_pilit_ov_transitive_control(self) -> None:
        entry = BASE["pilit"][0]
        result = compute_mapping(
            intrinsics_for(entry),
            stipulated_gfs=stipulated_gfs_for(entry),
        )
        assert result.mapping == {
            Role.AGENT: "OBJ-AGENT",
            Role.PATIENT: "SUBJ",
            Role.COMPLEMENT: "XCOMP",
        }

    def test_utos_dv_transitive_control(self) -> None:
        entry = BASE["utos"][0]
        result = compute_mapping(
            intrinsics_for(entry),
            stipulated_gfs=stipulated_gfs_for(entry),
        )
        assert result.mapping == {
            Role.AGENT: "OBJ-AGENT",
            Role.RECIPIENT: "SUBJ",
            Role.COMPLEMENT: "XCOMP",
        }


# === Synthesizer fallback =================================================


def _ma(lemma: str, voice: str | None = None, tr: str | None = None) -> MorphAnalysis:
    feats: dict[str, object] = {}
    if voice is not None:
        feats["VOICE"] = voice
    if tr is not None:
        feats["TR"] = tr
    return MorphAnalysis(lemma=lemma, pos="VERB", feats=feats)


class TestSynthesizerIntrinsics:
    """Verbs not in BASE are still parseable thanks to
    :func:`_synthesize_verb_entry`. The synthesizer attaches per-voice
    intrinsics matching the anchor pattern profiles, so the LMT
    engine produces typed mappings end-to-end."""

    def test_av_intransitive_actor(self) -> None:
        entry = _synthesize_verb_entry(_ma("foo"))
        assert entry.intrinsic_classification == {"ACTOR": (False, False)}
        result = compute_mapping(intrinsics_for(entry))
        assert result.mapping == {Role.ACTOR: "SUBJ"}

    def test_av_transitive_agent_patient(self) -> None:
        entry = _synthesize_verb_entry(_ma("foo", voice="AV", tr="TR"))
        result = compute_mapping(intrinsics_for(entry))
        assert result.mapping == {Role.AGENT: "SUBJ", Role.PATIENT: "OBJ"}

    def test_ov_transitive(self) -> None:
        entry = _synthesize_verb_entry(_ma("foo", voice="OV", tr="TR"))
        result = compute_mapping(intrinsics_for(entry))
        assert result.mapping == {
            Role.AGENT: "OBJ-AGENT",
            Role.PATIENT: "SUBJ",
        }

    def test_dv_transitive(self) -> None:
        entry = _synthesize_verb_entry(_ma("foo", voice="DV", tr="TR"))
        result = compute_mapping(intrinsics_for(entry))
        assert result.mapping == {
            Role.AGENT: "OBJ-AGENT",
            Role.GOAL: "SUBJ",
        }

    def test_iv_transitive(self) -> None:
        entry = _synthesize_verb_entry(_ma("foo", voice="IV", tr="TR"))
        result = compute_mapping(intrinsics_for(entry))
        assert result.mapping == {
            Role.AGENT: "OBJ-AGENT",
            Role.CONVEYED: "SUBJ",
        }

    def test_unknown_voice_falls_back_to_ov_shape(self) -> None:
        # The pre-Phase-5 fallback for unknown voice was the OV shape.
        # Synthesizer preserves that.
        entry = _synthesize_verb_entry(_ma("foo", voice="ZZZ", tr="TR"))
        result = compute_mapping(intrinsics_for(entry))
        assert result.mapping == {
            Role.AGENT: "OBJ-AGENT",
            Role.PATIENT: "SUBJ",
        }


# === intrinsics_for / stipulated_gfs_for unit tests =======================


class TestIntrinsicsFor:

    def test_uses_lex_entry_intrinsics(self) -> None:
        # A direct LexicalEntry construction with explicit intrinsics
        # is read back exactly.
        entry = LexicalEntry(
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
        frame = intrinsics_for(entry)
        assert [ic.role for ic in frame] == [Role.AGENT, Role.PATIENT]
        assert frame[0].intrinsics == IntrinsicFeatures(r=False, o=False)
        assert frame[1].intrinsics == IntrinsicFeatures(r=False, o=True)

    def test_falls_back_to_default_intrinsics_when_unset(self) -> None:
        # Empty intrinsic_classification → per-role defaults from
        # the Bresnan & Kanerva 1989 canonical table.
        entry = LexicalEntry(
            lemma="foo",
            pred="EAT <SUBJ, OBJ>",
            a_structure=["AGENT", "PATIENT"],
            morph_constraints={},
            gf_defaults={},
        )
        frame = intrinsics_for(entry)
        assert frame[0].role is Role.AGENT
        assert frame[0].intrinsics == default_intrinsics(Role.AGENT)
        assert frame[1].role is Role.PATIENT
        assert frame[1].intrinsics == default_intrinsics(Role.PATIENT)

    def test_partial_intrinsics_falls_back_per_role(self) -> None:
        # If only some roles have intrinsics declared, the rest fall
        # back individually.
        entry = LexicalEntry(
            lemma="foo",
            pred="GIVE <SUBJ, OBJ-θ, OBL-θ>",
            a_structure=["AGENT", "THEME", "GOAL"],
            morph_constraints={},
            gf_defaults={},
            intrinsic_classification={"THEME": (True, True)},
        )
        frame = intrinsics_for(entry)
        # AGENT: default [-o].
        assert frame[0].intrinsics == default_intrinsics(Role.AGENT)
        # THEME: explicit [+r, +o].
        assert frame[1].intrinsics == IntrinsicFeatures(r=True, o=True)
        # GOAL: default [-o].
        assert frame[2].intrinsics == default_intrinsics(Role.GOAL)

    def test_unknown_role_raises(self) -> None:
        entry = LexicalEntry(
            lemma="foo",
            pred="X <SUBJ>",
            a_structure=["GIBBERISH"],
            morph_constraints={},
            gf_defaults={},
        )
        with pytest.raises(ValueError, match=r"unknown role 'GIBBERISH'"):
            intrinsics_for(entry)

    def test_list_value_shape_accepted(self) -> None:
        # JSONB-loaded entries come back as lists (no JSON tuples);
        # the bridge must accept both.
        entry = LexicalEntry(
            lemma="foo",
            pred="EAT <SUBJ, OBJ>",
            a_structure=["AGENT"],
            morph_constraints={},
            gf_defaults={},
            intrinsic_classification={"AGENT": [False, False]},  # type: ignore[dict-item]
        )
        frame = intrinsics_for(entry)
        assert frame[0].intrinsics == IntrinsicFeatures(r=False, o=False)


class TestStipulatedGfsFor:

    def test_extracts_xcomp(self) -> None:
        entry = BASE["gusto"][0]
        stipulated = stipulated_gfs_for(entry)
        assert stipulated == {Role.COMPLEMENT: "XCOMP"}

    def test_ignores_subj_obj_obl(self) -> None:
        entry = BASE["pilit"][0]
        stipulated = stipulated_gfs_for(entry)
        # Only COMPLEMENT (XCOMP) should appear; PATIENT (SUBJ),
        # AGENT (OBJ) are LMT-derived.
        assert stipulated == {Role.COMPLEMENT: "XCOMP"}

    def test_empty_when_no_stipulated_gfs(self) -> None:
        # AV-tr lex entry: nothing stipulated.
        entry = next(
            e for e in BASE["kain"]
            if e.morph_constraints.get("VOICE") == "AV"
            and e.morph_constraints.get("TR") == "TR"
            and e.morph_constraints.get("APPL") == "NONE"
            and e.morph_constraints.get("CAUS") == "NONE"
        )
        assert stipulated_gfs_for(entry) == {}

    def test_unknown_role_silently_skipped(self) -> None:
        # Legacy lex entries with role names not in the Role enum
        # are silently skipped (intrinsics_for would catch the same
        # case loudly).
        entry = LexicalEntry(
            lemma="foo",
            pred="X <SUBJ>",
            a_structure=["AGENT"],
            morph_constraints={},
            gf_defaults={"GIBBERISH": "XCOMP"},
        )
        assert stipulated_gfs_for(entry) == {}
