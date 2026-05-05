"""Phase 5b Commit 1 — multi-GEN-NP IV-BEN applicative frames.

Three-argument applicatives like ``Ipinaggawa niya ng silya ang
kapatid niya`` ("he made a chair for his sibling") have two
ng-marked non-pivots (AGENT + PATIENT) plus the ang-marked pivot
(BENEFICIARY). The Phase 5 LMT engine produces typed
``OBJ-AGENT`` + ``OBJ-PATIENT`` + ``SUBJ``; this commit adds the
grammar rules and lex entries that emit such f-structures.

Word-order convention: first ng-NP after V is AGENT, second is
PATIENT (S&O 1972 §6.5; Kroeger 1993 §3.3 on post-V positioning).
"""

from __future__ import annotations

from typing import Any

from tgllfg.core.common import AStructure, FStructure
from tgllfg.fstruct import Diagnostic
from tgllfg.core.pipeline import parse_text


def _parses(text: str) -> list[
    tuple[Any, FStructure, AStructure, list[Diagnostic]]
]:
    return parse_text(text)


def _multi_gen_parse(
    results: list[tuple[Any, FStructure, AStructure, list[Diagnostic]]],
) -> tuple[Any, FStructure, AStructure, list[Diagnostic]] | None:
    """Pick the parse that uses the 3-arg PRED template (multi-GEN
    binding to OBJ-AGENT + OBJ-PATIENT)."""
    for parse in results:
        _, f, _, _ = parse
        if "OBJ-AGENT" in f.feats and "OBJ-PATIENT" in f.feats:
            return parse
    return None


# === gawa IV-BEN three-arg ================================================


class TestGawaThreeArg:

    def test_gen_gen_nom_order(self) -> None:
        # "Ipinaggawa niya ng silya ang kapatid" — AGENT, PATIENT,
        # then BEN-pivot. The most natural Tagalog ordering for
        # three-arg IV-BEN.
        results = _parses("Ipinaggawa niya ng silya ang kapatid.")
        parse = _multi_gen_parse(results)
        assert parse is not None, (
            f"no 3-arg parse with OBJ-AGENT + OBJ-PATIENT; "
            f"got {[(p[1].feats.get('PRED'), sorted(p[1].feats.keys())) for p in results]}"
        )
        _, f, a, diags = parse
        assert f.feats.get("PRED") == "MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>"
        assert "OBJ-AGENT" in f.feats
        assert "OBJ-PATIENT" in f.feats
        assert "SUBJ" in f.feats
        assert a.mapping == {
            "BENEFICIARY": "SUBJ",
            "AGENT": "OBJ-AGENT",
            "PATIENT": "OBJ-PATIENT",
        }
        # No mismatch: engine and grammar agree (typed OBJ slots
        # populated by the multi-GEN rule).
        assert not any(d.kind == "lmt-mismatch" for d in diags)

    def test_gen_nom_gen_order(self) -> None:
        # "Ipinaggawa niya ang kapatid ng silya" — AGENT, BEN-pivot,
        # PATIENT. The pivot can sit between the two ng-NPs.
        results = _parses("Ipinaggawa niya ang kapatid ng silya.")
        parse = _multi_gen_parse(results)
        assert parse is not None
        _, f, a, _ = parse
        assert a.mapping == {
            "BENEFICIARY": "SUBJ",
            "AGENT": "OBJ-AGENT",
            "PATIENT": "OBJ-PATIENT",
        }


# === sulat / bili — same shape ===========================================


class TestSulatThreeArg:

    def test_three_arg_iv_ben(self) -> None:
        # "Ipinagsulat niya ng liham ang kapatid" — same structure
        # as gawa, different verb.
        results = _parses("Ipinagsulat niya ng liham ang kapatid.")
        parse = _multi_gen_parse(results)
        assert parse is not None
        _, f, a, _ = parse
        assert f.feats.get("PRED") == "WRITE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>"
        assert a.mapping == {
            "BENEFICIARY": "SUBJ",
            "AGENT": "OBJ-AGENT",
            "PATIENT": "OBJ-PATIENT",
        }


class TestBiliThreeArg:

    def test_three_arg_iv_ben(self) -> None:
        # "Ipinagbili niya ng libro ang kapatid" — buy-for variant.
        # (libro is in the morph corpus; aklat is not.)
        results = _parses("Ipinagbili niya ng libro ang kapatid.")
        parse = _multi_gen_parse(results)
        assert parse is not None
        _, f, a, _ = parse
        assert f.feats.get("PRED") == "BUY-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>"
        assert a.mapping == {
            "BENEFICIARY": "SUBJ",
            "AGENT": "OBJ-AGENT",
            "PATIENT": "OBJ-PATIENT",
        }


# === Two-arg IV-BEN still parses (no regression) ==========================


class TestTwoArgIvBenStillParses:
    """The pre-existing two-arg IV-BEN entries still match
    sentences with only the AGENT + BEN arguments. The multi-GEN
    addition shouldn't suppress them."""

    def test_two_arg_ipinaggawa(self) -> None:
        # "Ipinaggawa niya ako" — AGENT (niya) + BEN-pivot (ako).
        # No PATIENT in the sentence; only the 2-arg lex entry
        # should match (the 3-arg's PRED requires OBJ-PATIENT,
        # which completeness rejects without a third NP).
        results = _parses("Ipinaggawa niya ako.")
        assert results, "no parse for two-arg IV-BEN"
        # Find at least one parse with the 2-arg PRED (typed
        # OBJ-AGENT after the Phase 5b OBJ-θ-in-grammar alignment).
        two_arg = next(
            (p for p in results
             if p[1].feats.get("PRED") == "MAKE-FOR <SUBJ, OBJ-AGENT>"),
            None,
        )
        assert two_arg is not None
        _, f, a, _ = two_arg
        assert "OBJ-PATIENT" not in f.feats
        assert a.mapping == {"BENEFICIARY": "SUBJ", "AGENT": "OBJ-AGENT"}


# === Word-order convention ================================================


class TestPositionalAgentPatientConvention:
    """The grammar binds the leftmost ng-NP to AGENT and the next
    to PATIENT. The convention follows S&O 1972 §6.5 / Kroeger
    1993 §3.3 on post-V positioning.

    With current morph + grammar coverage, the AGENT slot is filled
    by a pronoun (no PRED on its f-projection) and the PATIENT
    slot by a det+noun (PRED-bearing). These tests verify the
    structural distinction and the surface case match (both GEN)
    rather than asserting on opaque lex contents.
    """

    def test_first_ng_np_binds_agent(self) -> None:
        # In "Ipinaggawa niya ng silya ang kapatid":
        # - first ng-NP after V is "niya" (a GEN pronoun) → OBJ-AGENT.
        # - second ng-NP is "ng silya" (a det+N) → OBJ-PATIENT.
        # The AGENT f-structure should be distinct from PATIENT
        # (different node ids), and both should carry CASE=GEN.
        results = _parses("Ipinaggawa niya ng silya ang kapatid.")
        parse = _multi_gen_parse(results)
        assert parse is not None
        _, f, _, _ = parse
        agent = f.feats["OBJ-AGENT"]
        patient = f.feats["OBJ-PATIENT"]
        assert isinstance(agent, FStructure)
        assert isinstance(patient, FStructure)
        # Distinct f-structures (different node ids).
        assert agent.id != patient.id
        # Both are GEN-marked (the two ng-NPs).
        assert agent.feats.get("CASE") == "GEN"
        assert patient.feats.get("CASE") == "GEN"
        # PATIENT carries the det+noun shell (MARKER=NG); AGENT
        # is the bare pronoun shell (no MARKER).
        assert patient.feats.get("MARKER") == "NG"
        assert "MARKER" not in agent.feats
