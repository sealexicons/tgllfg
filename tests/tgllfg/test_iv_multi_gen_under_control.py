"""Phase 5d Commit 9: IV applicative multi-GEN frames under control.

Phase 5b §7.7 follow-on lifted top-level multi-GEN-NP applicative
frames for IV-BEN; Phase 5c §7.7 follow-on Commit 4 added 2-arg
IV-INSTR / IV-REASON; Phase 5d Commit 4 added 3-arg IV-INSTR /
IV-REASON. All three live at the ``S`` level. The Phase 5c §7.6
follow-on Commit 1 control complement (``S_XCOMP``) IV variant
had two practical limitations:

1. **APPL=CONVEY filter** — restricted the rule to bare-i (CONVEY)
   readings only. IV-BEN, IV-INSTR, IV-REASON have APPL=BEN /
   INSTR / REASON respectively, so the rule never fired for the
   common applicatives. Phase 5d Commit 9 drops the APPL filter
   so any IV applicative composes under control (the actor maps
   to OBJ-AGENT in all variants, so the binding is uniform).

2. **No 3-arg shape** — the rule was 2-arg only (``V[VOICE=IV]
   NP[CASE=NOM]``). Phase 5b's multi-GEN frames have three NPs at
   the top level (pivot + AGENT + PATIENT). Under control the
   AGENT is the gap, leaving SUBJ + GEN-PATIENT — a new 3-NP
   shape Commit 9 adds (``V[VOICE=IV] NP[CASE=NOM] NP[CASE=GEN]``
   plus the GEN-NOM variant for free post-V order).

These tests cover:

* IV-BEN 2-arg and 3-arg under PSYCH (gusto) and INTRANS
  (pumayag) control — verifies the dropped APPL filter lets
  IV-BEN through.
* IV-BEN 3-arg under TRANS control (pinilit) — composes with
  Phase 5c nested control + Phase 5b multi-GEN.
* IV-INSTR 2-arg and 3-arg under PSYCH control — verifies the
  generalisation extends to other applicatives.
* IV-REASON 3-arg under PSYCH control (uses PFV form because
  the CTPL form ``ikakain`` is analysed as IV-CONVEY in the
  current paradigms).
* Both NP orders for the 3-arg shape (NOM-GEN and GEN-NOM).
* SUBJ control identity: the embedded ``OBJ-AGENT`` is the same
  Python f-structure as the matrix controller — Python-id
  equality verified.
* Regression: top-level Phase 5b multi-GEN unchanged.
* LMT diagnostics clean.
"""

from __future__ import annotations

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _first(text: str) -> FStructure:
    rs = parse_text(text)
    assert rs, f"no parse for {text!r}"
    return rs[0][1]


def _find_xcomp_pred(text: str, expected_xcomp_pred: str) -> FStructure | None:
    """Return the first parse whose XCOMP.PRED matches; None if no
    such parse. Phase 4 §7.8 ambiguities can produce multiple
    parses with different XCOMP shapes."""
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        x = f.feats.get("XCOMP")
        if isinstance(x, FStructure) and x.feats.get("PRED") == expected_xcomp_pred:
            return f
    return None


# === IV-BEN under control ================================================


class TestIvBenUnderControl:
    """``Gusto kong ipaggagawa ang kapatid`` (2-arg) and
    ``Gusto kong ipaggagawa ng silya ang kapatid`` (3-arg).
    Pre-Commit-9 these failed because the IV S_XCOMP rule had
    APPL=CONVEY (BEN didn't match) and no 3-arg variant existed."""

    def test_two_arg_psych(self) -> None:
        f = _first("Gusto kong ipaggagawa ang kapatid.")
        assert f.feats.get("PRED") == "WANT <SUBJ, XCOMP>"
        x = f.feats["XCOMP"]
        assert isinstance(x, FStructure)
        assert x.feats.get("PRED") == "MAKE-FOR <SUBJ, OBJ-AGENT>"
        # Controller (gusto's SUBJ) === embedded OBJ-AGENT.
        outer_subj = f.feats["SUBJ"]
        inner_oa = x.feats["OBJ-AGENT"]
        assert isinstance(outer_subj, FStructure)
        assert isinstance(inner_oa, FStructure)
        assert outer_subj is inner_oa

    def test_two_arg_intrans(self) -> None:
        f = _first("Pumayag siyang ipaggagawa ang kapatid.")
        assert f.feats.get("PRED") == "AGREE <SUBJ, XCOMP>"
        x = f.feats["XCOMP"]
        assert isinstance(x, FStructure)
        assert x.feats.get("PRED") == "MAKE-FOR <SUBJ, OBJ-AGENT>"

    def test_three_arg_psych_gen_nom(self) -> None:
        # GEN-NOM order: ng silya ang kapatid.
        f = _first("Gusto kong ipaggagawa ng silya ang kapatid.")
        x = f.feats["XCOMP"]
        assert isinstance(x, FStructure)
        assert x.feats.get("PRED") == "MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>"
        assert x.feats["SUBJ"].feats.get("LEMMA") == "kapatid"  # type: ignore[union-attr]
        assert x.feats["OBJ-PATIENT"].feats.get("LEMMA") == "silya"  # type: ignore[union-attr]
        # Controller === embedded OBJ-AGENT.
        outer_subj = f.feats["SUBJ"]
        inner_oa = x.feats["OBJ-AGENT"]
        assert isinstance(outer_subj, FStructure)
        assert isinstance(inner_oa, FStructure)
        assert outer_subj is inner_oa

    def test_three_arg_psych_nom_gen(self) -> None:
        # NOM-GEN order: ang kapatid ng silya.
        f = _find_xcomp_pred(
            "Gusto kong ipaggagawa ang kapatid ng silya.",
            "MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
        )
        assert f is not None
        x = f.feats["XCOMP"]
        assert isinstance(x, FStructure)
        assert x.feats["SUBJ"].feats.get("LEMMA") == "kapatid"  # type: ignore[union-attr]
        assert x.feats["OBJ-PATIENT"].feats.get("LEMMA") == "silya"  # type: ignore[union-attr]

    def test_three_arg_intrans(self) -> None:
        f = _first("Pumayag siyang ipaggagawa ng silya ang kapatid.")
        assert f.feats.get("PRED") == "AGREE <SUBJ, XCOMP>"
        x = f.feats["XCOMP"]
        assert isinstance(x, FStructure)
        assert x.feats.get("PRED") == "MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>"

    def test_three_arg_trans_control(self) -> None:
        # ``Pinilit ng nanay ang batang ipaggagawa ng silya ang aso``
        # — TRANS forces the matrix-SUBJ (forcee) to control the
        # embedded OBJ-AGENT (the maker of the chair).
        f = _first("Pinilit ng nanay ang batang ipaggagawa ng silya ang aso.")
        assert f.feats.get("PRED") == "FORCE <SUBJ, OBJ-AGENT, XCOMP>"
        x = f.feats["XCOMP"]
        assert isinstance(x, FStructure)
        assert x.feats.get("PRED") == "MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>"
        # Controller is matrix.SUBJ (bata = forcee), NOT OBJ-AGENT (nanay).
        outer_subj = f.feats["SUBJ"]
        outer_oa = f.feats["OBJ-AGENT"]
        inner_oa = x.feats["OBJ-AGENT"]
        assert isinstance(outer_subj, FStructure)
        assert isinstance(outer_oa, FStructure)
        assert isinstance(inner_oa, FStructure)
        assert outer_subj is inner_oa
        assert outer_oa is not inner_oa


# === IV-INSTR under control ==============================================


class TestIvInstrUnderControl:
    """IV-INSTR (Phase 5c Commit 4 + Phase 5d Commit 4) — the same
    structural shape as IV-BEN, with INSTRUMENT pivoting to SUBJ."""

    def test_two_arg(self) -> None:
        f = _first("Gusto kong ipambibili ang pera.")
        x = f.feats["XCOMP"]
        assert isinstance(x, FStructure)
        assert x.feats.get("PRED") == "BUY-WITH <SUBJ, OBJ-AGENT>"
        outer_subj = f.feats["SUBJ"]
        inner_oa = x.feats["OBJ-AGENT"]
        assert isinstance(outer_subj, FStructure)
        assert isinstance(inner_oa, FStructure)
        assert outer_subj is inner_oa

    def test_three_arg(self) -> None:
        # Phase 5d Commit 4 added the 3-arg lex; Commit 9 lets it
        # parse under control.
        f = _first("Gusto kong ipambibili ng isda ang pera.")
        x = f.feats["XCOMP"]
        assert isinstance(x, FStructure)
        assert x.feats.get("PRED") == "BUY-WITH <SUBJ, OBJ-AGENT, OBJ-PATIENT>"
        assert x.feats["SUBJ"].feats.get("LEMMA") == "pera"  # type: ignore[union-attr]
        assert x.feats["OBJ-PATIENT"].feats.get("LEMMA") == "isda"  # type: ignore[union-attr]


# === IV-REASON under control =============================================


class TestIvReasonUnderControl:
    """IV-REASON 3-arg under control. Note: the CTPL form
    ``ikakain`` analyses as IV-CONVEY in the current paradigms;
    the PFV form ``ikinakain`` is what surfaces with the IV-REASON
    lex. Tests use PFV here."""

    def test_three_arg(self) -> None:
        f = _first("Gusto kong ikinakain ng isda ang gutom.")
        x = f.feats["XCOMP"]
        assert isinstance(x, FStructure)
        assert x.feats.get("PRED") == "EAT-FOR-REASON <SUBJ, OBJ-AGENT, OBJ-PATIENT>"
        assert x.feats["SUBJ"].feats.get("LEMMA") == "gutom"  # type: ignore[union-attr]
        assert x.feats["OBJ-PATIENT"].feats.get("LEMMA") == "isda"  # type: ignore[union-attr]


# === Regressions =========================================================


class TestRegressions:

    def test_top_level_iv_ben_three_arg_unchanged(self) -> None:
        # Phase 5b multi-GEN baseline must still produce the same
        # PRED + bindings.
        rs = parse_text("Ipinaggawa ng nanay ng silya ang kapatid.", n_best=10)
        assert rs
        for _, f, _, _ in rs:
            if f.feats.get("PRED") == "MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>":
                assert f.feats["SUBJ"].feats.get("LEMMA") == "kapatid"  # type: ignore[union-attr]
                assert f.feats["OBJ-AGENT"].feats.get("LEMMA") == "nanay"  # type: ignore[union-attr]
                assert f.feats["OBJ-PATIENT"].feats.get("LEMMA") == "silya"  # type: ignore[union-attr]
                return
        raise AssertionError("Phase 5b multi-GEN parse not found")

    def test_plain_ov_under_control_unchanged(self) -> None:
        # Phase 5c §7.6 follow-on Commit 1 OV-under-control still
        # works (CAUS=NONE filter unchanged).
        f = _first("Gusto kong kakainin ang isda.")
        x = f.feats["XCOMP"]
        assert isinstance(x, FStructure)
        assert x.feats.get("PRED") == "EAT <SUBJ, OBJ-AGENT>"

    def test_pa_ov_under_control_unchanged(self) -> None:
        # Phase 5d Commit 8 pa-OV-under-control still routes to
        # OBJ-CAUSER (CAUS=DIRECT filter unchanged).
        f = _first("Gusto niyang pakakainin ang bata.")
        x = f.feats["XCOMP"]
        assert isinstance(x, FStructure)
        assert x.feats.get("PRED") == "CAUSE-EAT <SUBJ, OBJ-CAUSER>"


# === LMT diagnostics =====================================================


class TestIvMultiGenLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Gusto kong ipaggagawa ang kapatid.",
            "Gusto kong ipaggagawa ng silya ang kapatid.",
            "Gusto kong ipaggagawa ang kapatid ng silya.",
            "Pumayag siyang ipaggagawa ng silya ang kapatid.",
            "Pinilit ng nanay ang batang ipaggagawa ng silya ang aso.",
            "Gusto kong ipambibili ng isda ang pera.",
            "Gusto kong ikinakain ng isda ang gutom.",
        ):
            rs = parse_text(s, n_best=10)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
