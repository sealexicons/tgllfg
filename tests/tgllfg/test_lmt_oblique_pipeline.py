"""Phase 5 §8 Commit 6 — sa-NP → typed OBL-θ end-to-end through the parser.

Pipeline-level tests for the oblique classifier. Adds the `lakad`
motion verb to BASE in two AV variants — intransitive (no
destination) and locative (sa-NP destination as ``OBL-LOC``) — so
``Lumakad ang bata sa palengke`` exercises the full chain:
parse → solve → ``classify_oblique_slots`` → ``lfg_well_formed``.
"""

from __future__ import annotations

from typing import Any

from tgllfg.common import AStructure, FStructure
from tgllfg.fstruct import Diagnostic
from tgllfg.pipeline import parse_text


def _parses(text: str) -> list[tuple[Any, FStructure, AStructure, list[Diagnostic]]]:
    return parse_text(text)


def _has_diag(diags: list[Diagnostic], kind: str) -> bool:
    return any(d.kind == kind for d in diags)


def _find_obl_loc_parse(
    results: list[tuple[Any, FStructure, AStructure, list[Diagnostic]]],
) -> tuple[Any, FStructure, AStructure, list[Diagnostic]] | None:
    for parse in results:
        _, f, _, _ = parse
        if "OBL-LOC" in f.feats:
            return parse
    return None


# === Base-case: motion verb without sa-NP =================================


class TestLakadIntransitive:
    """Without a sa-NP, only the bare intransitive lex entry matches
    (the locative entry's PRED requires OBL-LOC, so completeness
    suppresses it). The classifier is a no-op."""

    def test_lumakad_alone(self) -> None:
        results = _parses("Lumakad ang bata.")
        assert len(results) == 1
        _, f, a, diags = results[0]
        assert f.feats.get("PRED") == "WALK <SUBJ>"
        assert a.mapping == {"ACTOR": "SUBJ"}
        assert "OBL-LOC" not in f.feats
        assert "ADJUNCT" not in f.feats
        assert diags == []


# === Two-NP motion: sa-NP becomes OBL-LOC =================================


class TestLakadLocative:
    """The locative sentence parses two ways: the intransitive entry
    (sa-NP stays in ADJUNCT as a setting locative) and the locative
    entry (sa-NP gets reclassified into OBL-LOC). Both are valid;
    we assert the locative-classified parse is present."""

    def test_lumakad_with_sa_np_yields_obl_loc_parse(self) -> None:
        results = _parses("Lumakad ang bata sa palengke.")
        # Two parses survive: the bare intransitive (kept ADJUNCT)
        # and the locative (OBL-LOC).
        assert len(results) == 2
        obl_parse = _find_obl_loc_parse(results)
        assert obl_parse is not None, (
            f"no parse with OBL-LOC; results: "
            f"{[(p[1].feats.get('PRED'), sorted(p[1].feats.keys())) for p in results]}"
        )
        _, f, a, diags = obl_parse
        # PRED + governable features.
        assert f.feats.get("PRED") == "WALK <SUBJ, OBL-LOC>"
        assert "OBL-LOC" in f.feats
        assert "ADJUNCT" not in f.feats
        # AStructure mapping.
        assert a.mapping == {"ACTOR": "SUBJ", "LOCATION": "OBL-LOC"}
        # No mismatch — the engine and the f-structure (post-classify)
        # agree.
        assert not _has_diag(diags, "lmt-mismatch")

    def test_intransitive_parse_keeps_adjunct(self) -> None:
        # The companion parse (the bare intransitive) preserves the
        # sa-NP in ADJUNCT as a setting locative.
        results = _parses("Lumakad ang bata sa palengke.")
        intr_parse = next(
            (p for p in results if "OBL-LOC" not in p[1].feats), None
        )
        assert intr_parse is not None
        _, f, a, _ = intr_parse
        assert f.feats.get("PRED") == "WALK <SUBJ>"
        adjunct = f.feats.get("ADJUNCT")
        assert isinstance(adjunct, frozenset)
        assert len(adjunct) == 1
        # The sole ADJUNCT member is the sa-NP (CASE=DAT).
        sa_np = next(iter(adjunct))
        assert isinstance(sa_np, FStructure)
        assert sa_np.feats.get("CASE") == "DAT"
        assert a.mapping == {"ACTOR": "SUBJ"}


# === No-OBL verbs: the classifier is a no-op =============================


class TestNoObliqueRolesNoOp:
    """Verbs without OBL-θ roles (the bulk of Phase 4 BASE) parse
    unchanged. The classifier visits every parse but does nothing."""

    def test_av_transitive_unaffected(self) -> None:
        results = _parses("Kumain ang aso ng isda.")
        assert results
        _, f, a, _ = results[0]
        assert "OBL-LOC" not in f.feats
        assert "OBL-GOAL" not in f.feats
        assert a.mapping == {"AGENT": "SUBJ", "PATIENT": "OBJ"}

    def test_ov_transitive_unaffected(self) -> None:
        results = _parses("Kinain ng aso ang isda.")
        assert results
        _, f, _, _ = results[0]
        # No OBL-θ keys — the OV-tr lex entry has no OBL-θ roles.
        assert not any(k.startswith("OBL-") for k in f.feats)

    def test_psych_control_unaffected(self) -> None:
        # Control verbs stipulate XCOMP via gf_defaults, which is
        # NOT an OBL-θ slot. Classifier is a no-op.
        results = _parses("Gusto kong kumain.")
        assert results
        _, f, _, _ = results[0]
        assert not any(k.startswith("OBL-") for k in f.feats)
