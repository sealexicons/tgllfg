"""Phase 5d Commit 8: pa-OV / pa-DV (CAUS=DIRECT) under control.

Phase 5c §7.6 follow-on Commit 1 added non-AV ``S_XCOMP`` variants
that route ``REL-PRO`` to ``OBJ-AGENT`` for OV / DV / IV embedded
clauses. Those rules were specifically constrained with
``CAUS=NONE`` to keep them out of the actor-extraction path for
monoclausal direct causatives (``pa_in`` OV / ``pa_an`` DV), where
the typed actor slot is ``OBJ-CAUSER`` rather than ``OBJ-AGENT``.

Phase 5d Commit 8 adds the parallel ``CAUS=DIRECT`` variants. The
controllee in pa-OV / pa-DV is the causer (``OBJ-CAUSER``); the
causee is the SUBJ pivot. Under control the causer is the gap, so
the matrix control verb's controller binds the embedded causer:

  outer.SUBJ === XCOMP.OBJ-CAUSER  (Python id-equal)

Four new ``S_XCOMP`` rules cover the construction:

  * ``V[VOICE=OV, CAUS=DIRECT] NP[CASE=NOM]`` — 2-arg pa-OV
    (causee + gap-causer; no overt patient).
  * ``V[VOICE=OV, CAUS=DIRECT] NP[CASE=NOM] NP[CASE=GEN]`` —
    3-arg pa-OV in NOM-GEN order (causee + patient + gap-causer).
  * ``V[VOICE=OV, CAUS=DIRECT] NP[CASE=GEN] NP[CASE=NOM]`` —
    GEN-NOM order (NP order is free post-V).
  * ``V[VOICE=DV, CAUS=DIRECT] NP[CASE=NOM]`` — pa-DV (Phase 5d
    Commit 2 cells), location pivot + gap-causer.

These tests cover:

* pa-OV under PSYCH control (gusto), INTRANS (pumayag), TRANS
  (pinilit) — both 2-arg and 3-arg variants where applicable.
* pa-DV under PSYCH and INTRANS control.
* SUBJ control identity: the controller is structurally the same
  f-structure as the embedded ``OBJ-CAUSER``.
* CTPL form selection: ``pakakainin`` (cv-redup + pa- + -in) is
  the embedded form.
* Regression: standard OV under control still routes to
  OBJ-AGENT (CAUS=NONE).
* LMT diagnostics clean.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.pipeline import parse_text


def _first(text: str) -> FStructure:
    rs = parse_text(text)
    assert rs, f"no parse for {text!r}"
    return rs[0][1]


# === pa-OV under PSYCH control ===========================================


class TestPaOvUnderPsychControl:
    """``Gusto niyang pakakainin ang bata`` — gusto[PSYCH] + niya
    + -ng + pakakainin[OV CTPL CAUS=DIRECT] + ang bata. The
    controllee is the causer slot (``OBJ-CAUSER``) of the embedded
    pa-OV verb."""

    def test_two_arg_pa_ov(self) -> None:
        f = _first("Gusto niyang pakakainin ang bata.")
        assert f.feats.get("PRED") == "WANT <SUBJ, XCOMP>"
        xcomp = f.feats["XCOMP"]
        assert isinstance(xcomp, FStructure)
        assert xcomp.feats.get("PRED") == "CAUSE-EAT <SUBJ, OBJ-CAUSER>"
        assert xcomp.feats.get("VOICE") == "OV"
        # Causee is the SUBJ pivot.
        subj = xcomp.feats["SUBJ"]
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        # Controller (gusto's SUBJ) === embedded OBJ-CAUSER (the gap).
        outer_subj = f.feats["SUBJ"]
        inner_oc = xcomp.feats["OBJ-CAUSER"]
        assert isinstance(outer_subj, FStructure)
        assert isinstance(inner_oc, FStructure)
        assert outer_subj is inner_oc

    def test_three_arg_pa_ov_nom_gen(self) -> None:
        # ``Gusto niyang pakakainin ng kanin ang bata.`` — patient
        # (kanin) is also overt. Both NP orders admitted; this is
        # GEN-NOM order.
        f = _first("Gusto niyang pakakainin ng kanin ang bata.")
        xcomp = f.feats["XCOMP"]
        assert isinstance(xcomp, FStructure)
        assert xcomp.feats.get("PRED") == "CAUSE-EAT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>"
        assert xcomp.feats["SUBJ"].feats.get("LEMMA") == "bata"  # type: ignore[union-attr]
        assert xcomp.feats["OBJ-PATIENT"].feats.get("LEMMA") == "kanin"  # type: ignore[union-attr]

    def test_three_arg_pa_ov_nom_first(self) -> None:
        # NOM-GEN order: ``... pakakainin ang bata ng kanin.``
        f = _first("Gusto niyang pakakainin ang bata ng kanin.")
        xcomp = f.feats["XCOMP"]
        assert isinstance(xcomp, FStructure)
        assert xcomp.feats.get("PRED") == "CAUSE-EAT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>"
        assert xcomp.feats["SUBJ"].feats.get("LEMMA") == "bata"  # type: ignore[union-attr]
        assert xcomp.feats["OBJ-PATIENT"].feats.get("LEMMA") == "kanin"  # type: ignore[union-attr]


# === pa-OV under INTRANS control =========================================


class TestPaOvUnderIntransControl:
    """``Pumayag siyang pakakainin ang bata.`` — pumayag[INTRANS]
    + siya + -ng + pa-OV. The agentive matrix SUBJ controls the
    embedded causer."""

    def test_two_arg_pa_ov(self) -> None:
        f = _first("Pumayag siyang pakakainin ang bata.")
        assert f.feats.get("PRED") == "AGREE <SUBJ, XCOMP>"
        xcomp = f.feats["XCOMP"]
        assert isinstance(xcomp, FStructure)
        assert xcomp.feats.get("PRED") == "CAUSE-EAT <SUBJ, OBJ-CAUSER>"
        outer_subj = f.feats["SUBJ"]
        inner_oc = xcomp.feats["OBJ-CAUSER"]
        assert isinstance(outer_subj, FStructure)
        assert isinstance(inner_oc, FStructure)
        assert outer_subj is inner_oc


# === pa-OV under TRANS control ===========================================


class TestPaOvUnderTransControl:
    """``Pinilit ng nanay ang batang pakakainin ang aso.`` —
    pinilit[TRANS] + ng nanay (forcer) + ang bata (forcee/SUBJ) +
    -ng + pa-OV. The forcee is the controller of the embedded
    causer."""

    def test_two_arg_pa_ov_under_trans(self) -> None:
        f = _first("Pinilit ng nanay ang batang pakakainin ang aso.")
        assert f.feats.get("PRED") == "FORCE <SUBJ, OBJ-AGENT, XCOMP>"
        xcomp = f.feats["XCOMP"]
        assert isinstance(xcomp, FStructure)
        assert xcomp.feats.get("PRED") == "CAUSE-EAT <SUBJ, OBJ-CAUSER>"
        # Controller is matrix.SUBJ (the forcee = bata), not OBJ-AGENT
        # (the forcer = nanay).
        outer_subj = f.feats["SUBJ"]
        outer_oa = f.feats["OBJ-AGENT"]
        inner_oc = xcomp.feats["OBJ-CAUSER"]
        assert isinstance(outer_subj, FStructure)
        assert isinstance(outer_oa, FStructure)
        assert isinstance(inner_oc, FStructure)
        # SUBJ (bata) === XCOMP.OBJ-CAUSER
        assert outer_subj is inner_oc
        # OBJ-AGENT (nanay) is NOT the controller
        assert outer_oa is not inner_oc

    def test_three_arg_pa_ov_under_trans(self) -> None:
        # ``Pinilit ng nanay ang batang pakakainin ng tinapay ang aso.``
        f = _first("Pinilit ng nanay ang batang pakakainin ng tinapay ang aso.")
        xcomp = f.feats["XCOMP"]
        assert isinstance(xcomp, FStructure)
        assert xcomp.feats.get("PRED") == "CAUSE-EAT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>"
        # The patient (tinapay) is overt
        op = xcomp.feats.get("OBJ-PATIENT")
        assert isinstance(op, FStructure)
        assert op.feats.get("LEMMA") == "tinapay"


# === pa-DV under control =================================================


class TestPaDvUnderControl:
    """pa-DV (CAUS=DIRECT) — the location/recipient pivot is the
    SUBJ; the causer is the gap. Two-arg surface form (the patient
    is absent from pa-...-an's lex profile)."""

    def test_pa_dv_under_psych(self) -> None:
        f = _first("Gusto niyang pakakainan ang nanay.")
        assert f.feats.get("PRED") == "WANT <SUBJ, XCOMP>"
        xcomp = f.feats["XCOMP"]
        assert isinstance(xcomp, FStructure)
        assert xcomp.feats.get("PRED") == "CAUSE-EAT-AT <SUBJ, OBJ-CAUSER>"
        assert xcomp.feats.get("VOICE") == "DV"
        outer_subj = f.feats["SUBJ"]
        inner_oc = xcomp.feats["OBJ-CAUSER"]
        assert isinstance(outer_subj, FStructure)
        assert isinstance(inner_oc, FStructure)
        assert outer_subj is inner_oc

    def test_pa_dv_under_intrans(self) -> None:
        f = _first("Pumayag siyang pakakainan ang nanay.")
        xcomp = f.feats["XCOMP"]
        assert isinstance(xcomp, FStructure)
        assert xcomp.feats.get("PRED") == "CAUSE-EAT-AT <SUBJ, OBJ-CAUSER>"


# === Regression: standard OV under control unaffected ====================


class TestRegressions:

    def test_plain_ov_under_control_still_routes_to_obj_agent(self) -> None:
        # ``Gusto kong kakainin ang isda.`` — plain OV (CAUS=NONE)
        # still routes the controllee to OBJ-AGENT, not OBJ-CAUSER.
        f = _first("Gusto kong kakainin ang isda.")
        xcomp = f.feats["XCOMP"]
        assert isinstance(xcomp, FStructure)
        assert xcomp.feats.get("PRED") == "EAT <SUBJ, OBJ-AGENT>"
        # OBJ-AGENT exists; OBJ-CAUSER must not.
        assert isinstance(xcomp.feats.get("OBJ-AGENT"), FStructure)
        assert xcomp.feats.get("OBJ-CAUSER") is None

    def test_plain_pa_ov_top_level_unchanged(self) -> None:
        # Top-level pa-OV (no control wrapper) parses as before.
        f = _first("Pinakain ang bata ng nanay ng kanin.")
        assert f.feats.get("PRED") == "CAUSE-EAT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>"

    def test_psych_control_baseline(self) -> None:
        # Plain ``Gusto kong kumain.`` still works.
        f = _first("Gusto kong kumain.")
        assert f.feats.get("PRED") == "WANT <SUBJ, XCOMP>"


# === LMT clean ===========================================================


class TestPaCausativeLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Gusto niyang pakakainin ang bata.",
            "Gusto niyang pakakainin ng kanin ang bata.",
            "Gusto niyang pakakainin ang bata ng kanin.",
            "Pumayag siyang pakakainin ang bata.",
            "Pinilit ng nanay ang batang pakakainin ang aso.",
            "Pinilit ng nanay ang batang pakakainin ng tinapay ang aso.",
            "Gusto niyang pakakainan ang nanay.",
            "Pumayag siyang pakakainan ang nanay.",
        ):
            rs = parse_text(s, n_best=10)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
