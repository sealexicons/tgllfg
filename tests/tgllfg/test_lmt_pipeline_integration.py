"""Phase 5 §8 Commit 5 — end-to-end LMT pipeline integration.

Exercises the path :func:`tgllfg.pipeline.parse_text` →
:func:`tgllfg.lmt.apply_lmt_with_check`. Asserts:

* AStructure carries the LMT-engine-derived mapping (not the
  Phase 4 heuristic — non-AV ng-non-pivots become typed
  ``OBJ-θ``).
* ``lmt-mismatch`` diagnostic fires for the non-AV cases where the
  Phase 4 grammar emits bare ``OBJ`` but the engine predicts
  ``OBJ-θ``. The diagnostic is informational (in
  :data:`tgllfg.fstruct.NON_BLOCKING_KINDS`) so the parse survives.
* AV cases (transitive and intransitive) — and stipulated-XCOMP
  cases (control verbs, indirect causatives) — do **not** fire
  ``lmt-mismatch``.
* Synthesized-fallback verbs (lemmas absent from BASE) parse via
  the legacy heuristic path; no diagnostic emitted.
"""

from __future__ import annotations

from typing import Any

from tgllfg.common import AStructure, FStructure
from tgllfg.fstruct import Diagnostic
from tgllfg.pipeline import parse_text


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


# === OV / DV / IV — informational mismatch fires ==========================


class TestNonAvMismatch:
    """Non-AV transitives: the Phase 4 grammar emits bare ``OBJ`` for
    the ng-non-pivot, but the LMT engine produces typed ``OBJ-θ``
    (per Q1 upgrade decision). The mismatch is informational —
    surfaces as a diagnostic but the parse is preserved."""

    def test_ov_transitive_mismatch_informational(self) -> None:
        _, f, a, diags = _first("Kinain ng aso ang isda.")
        assert _has_diag(diags, "lmt-mismatch"), (
            f"expected lmt-mismatch on OV-tr: {diags}"
        )
        # Parse survived (informational, not blocking).
        assert f.feats.get("VOICE") == "OV"
        # AStructure carries LMT-derived typed mapping.
        assert a.mapping == {"PATIENT": "SUBJ", "AGENT": "OBJ-AGENT"}
        # Sanity: f-structure still has bare OBJ (grammar unchanged
        # in Commit 5).
        assert "OBJ" in f.feats
        assert "OBJ-AGENT" not in f.feats

    def test_dv_transitive_mismatch_informational(self) -> None:
        _, f, a, diags = _first("Sinulatan ng bata ang ina.")
        assert _has_diag(diags, "lmt-mismatch"), (
            f"expected lmt-mismatch on DV-tr: {diags}"
        )
        assert f.feats.get("VOICE") == "DV"
        assert a.mapping == {"RECIPIENT": "SUBJ", "AGENT": "OBJ-AGENT"}

    def test_iv_conveyed_mismatch_informational(self) -> None:
        _, f, a, diags = _first("Itinapon ng bata ang basura.")
        assert _has_diag(diags, "lmt-mismatch"), (
            f"expected lmt-mismatch on IV-CONVEY: {diags}"
        )
        assert f.feats.get("VOICE") == "IV"
        assert a.mapping == {"CONVEYED": "SUBJ", "AGENT": "OBJ-AGENT"}


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
    consumers (Commit 7 will gate blocking promotion off these
    fields)."""

    def test_mismatch_carries_expected_actual_pred(self) -> None:
        _, _, _, diags = _first("Kinain ng aso ang isda.")
        mismatches = [d for d in diags if d.kind == "lmt-mismatch"]
        assert len(mismatches) >= 1
        diag = mismatches[0]
        assert "expected" in diag.detail
        assert "actual" in diag.detail
        assert "pred" in diag.detail
        # OV-kain expectations.
        expected = diag.detail["expected"]
        actual = diag.detail["actual"]
        assert isinstance(expected, list)
        assert isinstance(actual, list)
        assert "OBJ-AGENT" in expected
        assert "SUBJ" in expected
        # OBJ-AGENT not in actual (grammar unchanged in Commit 5).
        assert "OBJ" in actual
        assert "OBJ-AGENT" not in actual

    def test_mismatch_is_informational(self) -> None:
        # The whole point of Commit 5: the parse survives despite
        # the mismatch.
        results = parse_text("Kinain ng aso ang isda.")
        assert results, "OV-tr parse was suppressed despite informational mismatch"
        # And is_blocking is False on the mismatch.
        for _, _, _, diags in results:
            for d in diags:
                if d.kind == "lmt-mismatch":
                    assert not d.is_blocking(), (
                        f"lmt-mismatch should be non-blocking: {d}"
                    )


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
