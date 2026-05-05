"""Phase 5d Commit 4: multi-GEN-NP IV-INSTR / IV-REASON 3-arg frames.

Phase 5b added three-arg IV-BEN frames (``ipinaggawa niya ng silya
ang kapatid`` — agent + patient + beneficiary, with beneficiary as
the SUBJ pivot). Phase 5c Commit 4 added the two-arg IV-INSTR /
IV-REASON entries (``ipinambili ng nanay ang pera`` — agent +
instrument-pivot, no overt patient). The 3-arg variants follow
the IV-BEN pattern mechanically: PATIENT joins AGENT in the
ng-NP slots, both demoted to typed OBJ-θ; INSTRUMENT / REASON
takes the SUBJ pivot.

The grammar's existing Phase 5b multi-GEN-NP rules
(``V[VOICE=IV] NP[NOM] NP[GEN] NP[GEN]`` and the two
permutations) are voice-restricted to IV without an APPL
constraint, so they fire for IV-INSTR and IV-REASON alongside
IV-BEN. Only new lex entries + intrinsic profiles are needed.

These tests cover:

* 3-arg IV-INSTR (bili, tahi) producing
  ``BUY-WITH <SUBJ, OBJ-AGENT, OBJ-PATIENT>`` etc.
* 3-arg IV-REASON (kain, sulat) producing
  ``EAT-FOR-REASON <SUBJ, OBJ-AGENT, OBJ-PATIENT>`` etc.
* Multi-GEN positional binding: first ng-NP → AGENT
  (OBJ-AGENT), second → PATIENT (OBJ-PATIENT).
* Pivot is INSTRUMENT (or REASON) → SUBJ.
* Regression: 2-arg IV-INSTR / IV-REASON (Phase 5c) still work
  when only one ng-NP is present.
* Regression: 3-arg IV-BEN (Phase 5b) still works.
* LMT diagnostics clean.

Note: each 3-arg sentence admits at least one structural
ambiguity (``ng nanay ng isda`` could be parsed as a possessive
"mother's fish" via the existing NP-internal possessive rule).
The tests assert that AT LEAST ONE parse has the
multi-GEN-binding structure, mirroring how Phase 5b's IV-BEN
tests handle the same ambiguity.
"""

from __future__ import annotations

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _find_multi_gen_parse(
    text: str, expected_pred: str
) -> FStructure | None:
    """Return the first parse with PRED == expected_pred and both
    OBJ-AGENT and OBJ-PATIENT present (i.e., the multi-GEN
    binding fired), else None."""
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        if f.feats.get("PRED") != expected_pred:
            continue
        oa = f.feats.get("OBJ-AGENT")
        op = f.feats.get("OBJ-PATIENT")
        if isinstance(oa, FStructure) and isinstance(op, FStructure):
            return f
    return None


# === 3-arg IV-INSTR =====================================================


class TestThreeArgIvInstr:

    def test_bili_three_arg(self) -> None:
        # ``Ipinambili ng nanay ng isda ang pera`` —
        # "money is what mother bought (fish) with".
        # AGENT = nanay, PATIENT = isda, INSTRUMENT = pera (pivot).
        f = _find_multi_gen_parse(
            "Ipinambili ng nanay ng isda ang pera.",
            "BUY-WITH <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
        )
        assert f is not None
        assert f.feats["OBJ-AGENT"].feats.get("LEMMA") == "nanay"  # type: ignore[union-attr]
        assert f.feats["OBJ-PATIENT"].feats.get("LEMMA") == "isda"  # type: ignore[union-attr]
        assert f.feats["SUBJ"].feats.get("LEMMA") == "pera"  # type: ignore[union-attr]

    def test_tahi_three_arg(self) -> None:
        # ``Ipinantahi ng nanay ng isda ang karayom`` —
        # "needle is what mother sewed (fish) with".
        f = _find_multi_gen_parse(
            "Ipinantahi ng nanay ng isda ang karayom.",
            "SEW-WITH <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
        )
        assert f is not None
        assert f.feats["SUBJ"].feats.get("LEMMA") == "karayom"  # type: ignore[union-attr]
        assert f.feats["OBJ-AGENT"].feats.get("LEMMA") == "nanay"  # type: ignore[union-attr]
        assert f.feats["OBJ-PATIENT"].feats.get("LEMMA") == "isda"  # type: ignore[union-attr]


# === 3-arg IV-REASON ====================================================


class TestThreeArgIvReason:

    def test_kain_three_arg(self) -> None:
        # ``Ikinakain ng bata ng isda ang gutom`` —
        # "hunger is the reason the child ate fish".
        # AGENT = bata, PATIENT = isda, REASON = gutom (pivot).
        f = _find_multi_gen_parse(
            "Ikinakain ng bata ng isda ang gutom.",
            "EAT-FOR-REASON <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
        )
        assert f is not None
        assert f.feats["SUBJ"].feats.get("LEMMA") == "gutom"  # type: ignore[union-attr]

    def test_sulat_three_arg(self) -> None:
        # ``Ikinasulat ng bata ng isda ang gutom`` —
        # "hunger is the reason the child wrote (about) fish".
        f = _find_multi_gen_parse(
            "Ikinasulat ng bata ng isda ang gutom.",
            "WRITE-FOR-REASON <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
        )
        assert f is not None
        assert f.feats["OBJ-AGENT"].feats.get("LEMMA") == "bata"  # type: ignore[union-attr]
        assert f.feats["OBJ-PATIENT"].feats.get("LEMMA") == "isda"  # type: ignore[union-attr]


# === Word order: positional AGENT-then-PATIENT ==========================


class TestPositionalBinding:
    """The Phase 5b multi-GEN convention is: the first ng-NP
    after V is AGENT, the second is PATIENT (per S&O 1972 §6.5,
    Kroeger 1993 §3.3). The new IV-INSTR and IV-REASON 3-arg
    entries inherit this convention via the same grammar
    rules."""

    def test_iv_instr_first_ng_is_agent(self) -> None:
        f = _find_multi_gen_parse(
            "Ipinambili ng nanay ng isda ang pera.",
            "BUY-WITH <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
        )
        assert f is not None
        # First ng-NP (nanay) is AGENT, not PATIENT.
        assert f.feats["OBJ-AGENT"].feats.get("LEMMA") == "nanay"  # type: ignore[union-attr]
        # Second ng-NP (isda) is PATIENT.
        assert f.feats["OBJ-PATIENT"].feats.get("LEMMA") == "isda"  # type: ignore[union-attr]


# === Regression: 2-arg entries still work ===============================


class TestTwoArgRegression:

    def test_iv_instr_two_arg(self) -> None:
        rs = parse_text("Ipinambili ng nanay ang pera.")
        assert rs
        _, f, _, _ = rs[0]
        assert f.feats.get("PRED") == "BUY-WITH <SUBJ, OBJ-AGENT>"
        # No OBJ-PATIENT in 2-arg form.
        assert f.feats.get("OBJ-PATIENT") is None

    def test_iv_reason_two_arg(self) -> None:
        rs = parse_text("Ikinasulat ng bata ang gutom.")
        assert rs
        _, f, _, _ = rs[0]
        assert f.feats.get("PRED") == "WRITE-FOR-REASON <SUBJ, OBJ-AGENT>"
        assert f.feats.get("OBJ-PATIENT") is None


# === Regression: Phase 5b IV-BEN 3-arg still works ======================


class TestIvBenRegression:

    def test_iv_ben_three_arg_still_works(self) -> None:
        f = _find_multi_gen_parse(
            "Ipinaggawa ng nanay ng isda ang bata.",
            "MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
        )
        assert f is not None
        assert f.feats["SUBJ"].feats.get("LEMMA") == "bata"  # type: ignore[union-attr]


# === LMT clean ==========================================================


class TestThreeArgLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Ipinambili ng nanay ng isda ang pera.",
            "Ipinantahi ng nanay ng isda ang karayom.",
            "Ikinakain ng bata ng isda ang gutom.",
            "Ikinasulat ng bata ng isda ang gutom.",
        ):
            rs = parse_text(s, n_best=10)
            assert rs
            # At least one parse must have no blocking diagnostics.
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
