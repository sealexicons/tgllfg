"""Phase 5 §8 — end-to-end LMT pipeline integration.

Exercises the path :func:`tgllfg.pipeline.parse_text` →
:func:`tgllfg.lmt.apply_lmt_with_check`. Asserts:

* AStructure carries the LMT-engine-derived mapping (non-AV
  ng-non-pivots map to typed ``OBJ-θ``).
* The Phase 4 grammar's bare-``OBJ`` emission for non-AV
  transitives has been aligned with the LMT engine's typed
  prediction in Phase 5b: the f-structure now carries
  ``OBJ-AGENT`` / ``OBJ-CAUSER`` directly. As a result,
  ``lmt-mismatch`` no longer fires on regular transitives —
  the diagnostic is reserved for synthetic fixtures with
  deliberately mismatched f-structure / lex-entry pairs (see
  ``test_lmt_check_blocking.py``).
* AV cases, stipulated-XCOMP cases (control verbs, indirect
  causatives), and synthesized-fallback verbs all parse cleanly.
"""

from __future__ import annotations

from typing import Any

from tgllfg.core.common import AStructure, FStructure
from tgllfg.fstruct import Diagnostic
from tgllfg.core.pipeline import parse_text


def _first(text: str) -> tuple[Any, FStructure, AStructure, list[Diagnostic]]:
    results = parse_text(text)
    assert results, f"no parse for {text!r}"
    return results[0]


def _has_diag(diags: list[Diagnostic], kind: str) -> bool:
    return any(d.kind == kind for d in diags)


# === AV — no LMT mismatch =================================================


class TestAvNoMismatch:
    """AV transitives and intransitives: the Phase 4 grammar's
    ``(↑ SUBJ) = ...`` and ``(↑ OBJ) = ...`` equations match what
    the LMT engine predicts (AGENT → SUBJ, PATIENT → bare OBJ).
    No mismatch diagnostic should fire."""

    def test_av_intransitive_no_mismatch(self) -> None:
        _, f, a, diags = _first("Kumain ang aso.")
        assert not _has_diag(diags, "lmt-mismatch"), (
            f"unexpected mismatch on AV-intr: {diags}"
        )
        assert "SUBJ" in f.feats
        assert a.mapping == {"ACTOR": "SUBJ"}

    def test_av_transitive_no_mismatch(self) -> None:
        _, f, a, diags = _first("Kumain ang aso ng isda.")
        assert not _has_diag(diags, "lmt-mismatch"), (
            f"unexpected mismatch on AV-tr: {diags}"
        )
        assert a.mapping == {"AGENT": "SUBJ", "PATIENT": "OBJ"}


# === OV / DV / IV — engine and grammar agree (typed OBJ-θ) ================


class TestNonAvAligned:
    """Non-AV transitives: as of the Phase 5b OBJ-θ-in-grammar
    alignment, the f-structure carries ``OBJ-AGENT`` (or
    ``OBJ-CAUSER`` for pa-OV-direct) directly — matching the
    engine's typed prediction. No mismatch fires."""

    def test_ov_transitive_typed(self) -> None:
        _, f, a, diags = _first("Kinain ng aso ang isda.")
        assert not _has_diag(diags, "lmt-mismatch"), (
            f"unexpected mismatch on OV-tr: {diags}"
        )
        assert f.feats.get("VOICE") == "OV"
        assert a.mapping == {"PATIENT": "SUBJ", "AGENT": "OBJ-AGENT"}
        # F-structure carries typed OBJ-AGENT (no bare OBJ).
        assert "OBJ-AGENT" in f.feats
        assert "OBJ" not in f.feats

    def test_dv_transitive_typed(self) -> None:
        _, f, a, diags = _first("Sinulatan ng bata ang ina.")
        assert not _has_diag(diags, "lmt-mismatch")
        assert f.feats.get("VOICE") == "DV"
        assert a.mapping == {"RECIPIENT": "SUBJ", "AGENT": "OBJ-AGENT"}
        assert "OBJ-AGENT" in f.feats
        assert "OBJ" not in f.feats

    def test_iv_conveyed_typed(self) -> None:
        _, f, a, diags = _first("Itinapon ng bata ang basura.")
        assert not _has_diag(diags, "lmt-mismatch")
        assert f.feats.get("VOICE") == "IV"
        assert a.mapping == {"CONVEYED": "SUBJ", "AGENT": "OBJ-AGENT"}
        assert "OBJ-AGENT" in f.feats
        assert "OBJ" not in f.feats


# === Stipulated-XCOMP — no mismatch =======================================


class TestStipulatedXcomp:
    """Control verbs (gusto, payag, pilit) and indirect causatives
    (magpa-) stipulate XCOMP via gf_defaults. The LMT engine passes
    XCOMP through unchanged; the f-structure also has XCOMP from
    grammar equations. Sets agree → no mismatch."""

    def test_psych_control_no_mismatch(self) -> None:
        _, f, a, diags = _first("Gusto kong kumain.")
        assert not _has_diag(diags, "lmt-mismatch"), (
            f"unexpected mismatch on psych control: {diags}"
        )
        assert a.mapping == {"EXPERIENCER": "SUBJ", "COMPLEMENT": "XCOMP"}

    def test_intransitive_control_no_mismatch(self) -> None:
        _, f, a, diags = _first("Pumayag siyang kumain.")
        assert not _has_diag(diags, "lmt-mismatch"), (
            f"unexpected mismatch on intransitive control: {diags}"
        )
        assert a.mapping == {"AGENT": "SUBJ", "COMPLEMENT": "XCOMP"}

    def test_indirect_causative_no_mismatch(self) -> None:
        _, f, a, diags = _first("Nagpakain ang nanay na kumain.")
        assert not _has_diag(diags, "lmt-mismatch"), (
            f"unexpected mismatch on magpa- causative: {diags}"
        )
        assert a.mapping == {"CAUSER": "SUBJ", "EVENT": "XCOMP"}


# === Synthesizer fallback — no mismatch ===================================


class TestSynthesizerFallback:
    """Verbs absent from BASE parse via :func:`_synthesize_verb_entry`,
    which now attaches per-voice intrinsics. For these, the engine
    and the legacy heuristic agree (the synthesizer's intrinsics
    were chosen to match its gf_defaults), so no mismatch fires
    on AV-intr; non-AV synthesized verbs fire mismatch by the same
    rule as BASE non-AV entries."""

    def test_synthesized_av_intransitive(self) -> None:
        # 'lakad' (walk) is in the morph corpus but not in BASE — the
        # synthesizer fallback path produces the lex entry.
        _, f, a, diags = _first("Lumakad ang bata.")
        # Synthesized AV-intr: ACTOR → SUBJ, no OBJ. No mismatch.
        assert not _has_diag(diags, "lmt-mismatch"), (
            f"unexpected mismatch on synthesized AV-intr: {diags}"
        )
        assert a.mapping == {"ACTOR": "SUBJ"}

    def test_synthesized_av_transitive_no_mismatch(self) -> None:
        # 'luto' (cook) — synthesized AV-tr: AGENT → SUBJ,
        # PATIENT → OBJ. Matches Phase 4 grammar. No mismatch.
        _, f, a, diags = _first("Nagluto ang nanay ng kanin.")
        assert not _has_diag(diags, "lmt-mismatch"), (
            f"unexpected mismatch on synthesized AV-tr: {diags}"
        )
        assert a.mapping == {"AGENT": "SUBJ", "PATIENT": "OBJ"}


# === Diagnostic shape =====================================================


class TestMismatchDiagnosticShape:
    """The mismatch diagnostic carries useful detail for downstream
    consumers. After the Phase 5b OBJ-θ-in-grammar alignment, regular
    transitive parses no longer fire the diagnostic; the synthetic
    fixture below exercises the diagnostic via a lex entry whose
    intrinsic profile predicts a GF set the f-structure doesn't have.
    The is-non-blocking property is exercised in
    ``test_lmt_check_blocking.py``."""

    def test_mismatch_detail_fields_present(self) -> None:
        # Synthetic: lex entry predicts SUBJ + OBJ-PATIENT but the
        # f-structure carries SUBJ + OBJ (bare). The shape mismatch
        # surfaces as lmt-mismatch.
        from tgllfg.core.common import LexicalEntry
        from tgllfg.lmt import lmt_check
        lex = LexicalEntry(
            lemma="zzz",
            pred="ZZZ <SUBJ, OBJ-PATIENT>",
            a_structure=["AGENT", "PATIENT"],
            morph_constraints={},
            gf_defaults={"AGENT": "SUBJ", "PATIENT": "OBJ-PATIENT"},
            intrinsic_classification={
                "AGENT": (False, False),
                "PATIENT": (True, True),
            },
        )
        f = FStructure(feats={
            "PRED": "ZZZ <SUBJ, OBJ-PATIENT>",
            "VOICE": "AV",
            "SUBJ": FStructure(feats={"PRED": "S"}, id=1),
            "OBJ": FStructure(feats={"PRED": "O"}, id=2),
        })
        _astr, diags = lmt_check(f, lex)
        mismatches = [d for d in diags if d.kind == "lmt-mismatch"]
        assert len(mismatches) >= 1
        diag = mismatches[0]
        assert "expected" in diag.detail
        assert "actual" in diag.detail
        assert "pred" in diag.detail
        expected = diag.detail["expected"]
        actual = diag.detail["actual"]
        assert isinstance(expected, list)
        assert isinstance(actual, list)
        assert "OBJ-PATIENT" in expected
        assert "SUBJ" in expected
        assert "OBJ" in actual
        assert "OBJ-PATIENT" not in actual


# === Synthesizer-fallback path (lex_entry not in BASE) ====================


class TestNoLexEntryFallback:
    """When ``find_matrix_lex_entry`` can't locate a lex entry post-solve
    (e.g., test fixtures with synthetic f-structures), the pipeline
    falls back to the legacy heuristic and emits no diagnostic."""

    def test_apply_lmt_with_check_falls_back_when_no_lex_entry(self) -> None:
        # Direct unit test on apply_lmt_with_check with empty lex_items.
        # The legacy heuristic looks at f.feats: with OBJ present and
        # VOICE=OV, it returns the OV-shaped mapping.
        from tgllfg.lmt.check import apply_lmt_with_check
        sub_subj = FStructure()
        sub_obj = FStructure()
        f = FStructure(feats={
            "PRED": "EAT <SUBJ, OBJ>",
            "VOICE": "OV",
            "SUBJ": sub_subj,
            "OBJ": sub_obj,
        })
        a, diags = apply_lmt_with_check(f, lex_items=[])
        assert diags == []
        # Legacy heuristic for OV produces PATIENT pivot, AGENT OBJ
        # (bare; the heuristic does not apply the Phase 5 upgrade).
        assert a.mapping == {"PATIENT": "SUBJ", "AGENT": "OBJ"}
