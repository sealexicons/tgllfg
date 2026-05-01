"""Phase 5b Commit 2 — multi-GEN-NP pa-OV-direct causative frames.

Three-argument direct causatives like ``Pinakain niya ng kanin ang
bata`` ("he fed the child rice") have two ng-marked non-pivots
(CAUSER + PATIENT) plus the ang-marked pivot (CAUSEE). Same shape
as the IV-BEN multi-GEN frames from Commit 1; the role names
differ — CAUSER instead of AGENT, CAUSEE instead of BENEFICIARY —
so the grammar binds to typed ``OBJ-CAUSER`` rather than
``OBJ-AGENT``.

Word-order convention is identical: first ng-NP after V is CAUSER
(the agentive instigator), second is PATIENT (the affected entity).
"""

from __future__ import annotations

from typing import Any

from tgllfg.common import AStructure, FStructure
from tgllfg.fstruct import Diagnostic
from tgllfg.pipeline import parse_text


def _parses(text: str) -> list[
    tuple[Any, FStructure, AStructure, list[Diagnostic]]
]:
    return parse_text(text)


def _multi_gen_parse(
    results: list[tuple[Any, FStructure, AStructure, list[Diagnostic]]],
) -> tuple[Any, FStructure, AStructure, list[Diagnostic]] | None:
    """Pick the parse that uses the 3-arg PRED template (multi-GEN
    binding to OBJ-CAUSER + OBJ-PATIENT)."""
    for parse in results:
        _, f, _, _ = parse
        if "OBJ-CAUSER" in f.feats and "OBJ-PATIENT" in f.feats:
            return parse
    return None


# === kain pa-OV-direct three-arg ==========================================


class TestKainPaInThreeArg:

    def test_gen_gen_nom_order(self) -> None:
        # "Pinakain niya ng kanin ang bata" — CAUSER, PATIENT,
        # CAUSEE-pivot. The most natural Tagalog ordering for
        # three-arg pa-OV-direct.
        results = _parses("Pinakain niya ng kanin ang bata.")
        parse = _multi_gen_parse(results)
        assert parse is not None, (
            f"no 3-arg parse with OBJ-CAUSER + OBJ-PATIENT; "
            f"got {[(p[1].feats.get('PRED'), sorted(p[1].feats.keys())) for p in results]}"
        )
        _, f, a, diags = parse
        assert f.feats.get("PRED") == "CAUSE-EAT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>"
        assert "OBJ-CAUSER" in f.feats
        assert "OBJ-PATIENT" in f.feats
        assert "SUBJ" in f.feats
        assert a.mapping == {
            "CAUSEE": "SUBJ",
            "CAUSER": "OBJ-CAUSER",
            "PATIENT": "OBJ-PATIENT",
        }
        # No mismatch: engine and grammar agree.
        assert not any(d.kind == "lmt-mismatch" for d in diags)

    def test_gen_nom_gen_order(self) -> None:
        # "Pinakain niya ang bata ng kanin" — CAUSER, CAUSEE-pivot,
        # PATIENT.
        results = _parses("Pinakain niya ang bata ng kanin.")
        parse = _multi_gen_parse(results)
        assert parse is not None
        _, _, a, _ = parse
        assert a.mapping == {
            "CAUSEE": "SUBJ",
            "CAUSER": "OBJ-CAUSER",
            "PATIENT": "OBJ-PATIENT",
        }


# === basa / inom — same shape =============================================


class TestBasaPaInThreeArg:

    def test_three_arg_pa_ov(self) -> None:
        # "Pinabasa niya ng libro ang bata" — CAUSER reads child book.
        results = _parses("Pinabasa niya ng libro ang bata.")
        parse = _multi_gen_parse(results)
        assert parse is not None
        _, f, a, _ = parse
        assert (
            f.feats.get("PRED")
            == "CAUSE-READ <SUBJ, OBJ-CAUSER, OBJ-PATIENT>"
        )
        assert a.mapping == {
            "CAUSEE": "SUBJ",
            "CAUSER": "OBJ-CAUSER",
            "PATIENT": "OBJ-PATIENT",
        }


class TestInomPaInThreeArg:

    def test_three_arg_pa_ov(self) -> None:
        # "Pinainom niya ng tubig ang bata" — CAUSER caused-drink
        # child water.
        results = _parses("Pinainom niya ng tubig ang bata.")
        parse = _multi_gen_parse(results)
        assert parse is not None
        _, f, a, _ = parse
        assert (
            f.feats.get("PRED")
            == "CAUSE-DRINK <SUBJ, OBJ-CAUSER, OBJ-PATIENT>"
        )
        assert a.mapping == {
            "CAUSEE": "SUBJ",
            "CAUSER": "OBJ-CAUSER",
            "PATIENT": "OBJ-PATIENT",
        }


# === Two-arg pa-OV-direct still parses (no regression) ====================


class TestTwoArgPaInStillParses:
    """The pre-existing two-arg pa-OV-direct entries still match
    sentences with only the CAUSER + CAUSEE arguments. The
    multi-GEN addition shouldn't suppress them."""

    def test_two_arg_pinakain(self) -> None:
        # "Pinakain niya ang bata" — CAUSER (niya) + CAUSEE-pivot
        # (bata). No PATIENT in the sentence; only the 2-arg lex
        # entry should match (the 3-arg's PRED requires OBJ-PATIENT,
        # which completeness rejects without a third NP).
        results = _parses("Pinakain niya ang bata.")
        assert results, "no parse for two-arg pa-OV-direct"
        # Find at least one parse with the 2-arg PRED.
        two_arg = next(
            (p for p in results
             if p[1].feats.get("PRED") == "CAUSE-EAT <SUBJ, OBJ>"),
            None,
        )
        assert two_arg is not None
        _, f, a, _ = two_arg
        assert "OBJ-PATIENT" not in f.feats
        assert a.mapping == {"CAUSEE": "SUBJ", "CAUSER": "OBJ-CAUSER"}


# === Plain OV transitive untouched ========================================


class TestPlainOvTransitiveUnaffected:
    """The new pa-OV-direct rules match V[VOICE=OV, CAUS=DIRECT]
    specifically. Plain OV transitives (CAUS=NONE) should be
    unaffected — no spurious 3-arg parse fires."""

    def test_plain_ov_kinain_unchanged(self) -> None:
        results = _parses("Kinain ng aso ang isda.")
        assert results
        # No multi-GEN parse should be present (no OBJ-CAUSER).
        for _, f, _, _ in results:
            assert "OBJ-CAUSER" not in f.feats
            assert "OBJ-PATIENT" not in f.feats

    def test_plain_ov_three_np_with_sa_unchanged(self) -> None:
        # "Kinain ng aso ang isda sa kusina" — plain OV-tr + sa-NP.
        # Should still parse (existing 4-token rule handles it),
        # and nothing should fire OBJ-CAUSER/OBJ-PATIENT.
        results = _parses("Kinain ng aso ang isda sa kusina.")
        # Plain OV with sa-NP — sa-NP goes to ADJUNCT (no OBL-θ
        # role on the 2-arg lex entry).
        for _, f, _, _ in results:
            assert "OBJ-CAUSER" not in f.feats
