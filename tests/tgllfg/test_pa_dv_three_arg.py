"""Phase 5e Commit 10: 3-arg pa-DV (with overt PATIENT).

Phase 5d Commit 2 introduced pa-DV (``pa-...-an``) with a 2-arg
PRED ``CAUSE-X-AT <SUBJ, OBJ-CAUSER>``. Phase 5d Commits 8 / 9
made pa-OV (CAUS=DIRECT) work at 3-arg under control, but pa-DV
stayed 2-arg because the lex profile didn't admit a third
argument. This commit fills in the parallel:

* New intrinsic profile ``_DV_CAUS_DIRECT_THREE_ARG`` —
  CAUSER + PATIENT + LOCATION, with both CAUSER and PATIENT at
  [+r, +o] (typed OBJ-θ slots) and LOCATION at [-r, -o] (the
  pivot).
* Three new BASE entries (kain / basa / inom DV CAUS=DIRECT
  3-arg) with PRED ``CAUSE-X-AT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>``.
* Three new top-level multi-GEN-NP pa-DV grammar rules
  (NOM-GEN-GEN / GEN-NOM-GEN / GEN-GEN-NOM permutations,
  parallel to the Phase 5b multi-GEN-NP pa-OV rules).
* Two new ``S_XCOMP`` rules for 3-arg pa-DV under control
  (NOM-GEN and GEN-NOM orders, parallel to the pa-OV variants
  added in Phase 5d Commit 8).
* Two new ``S_GAP_OBJ_CAUSER`` rules for 3-arg pa-DV
  ay-fronting with CAUSER extracted (lifting the deferral from
  Phase 5e Commit 1).
* ``S_GAP_OBJ_PATIENT`` is extended to admit
  ``V[VOICE=DV, CAUS=DIRECT]`` so pa-DV PATIENT-fronting works
  in the existing 3-arg-multi-GEN ay-fronting pattern from
  Phase 5e Commit 2.

Sentences enabled:

* ``Pinakainan ng nanay ng kanin ang bata.``
  "Mother fed rice to the child." (top-level 3-arg pa-DV)
* ``Gusto kong pakakainan ang bata ng kanin.``
  "I want to feed rice to the child." (3-arg pa-DV under
  control)
* ``Ng nanay ay pinakainan ang bata ng kanin.``
  "It was mother who fed rice to the child." (CAUSER-fronted)
* ``Ng kanin ay pinakainan ng nanay ang bata.``
  "It was rice that mother fed to the child." (PATIENT-fronted)
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.pipeline import parse_text


def _first(text: str) -> FStructure:
    rs = parse_text(text)
    assert rs, f"no parse for {text!r}"
    return rs[0][1]


def _find(
    text: str,
    *,
    pred: str,
    subj_lemma: str | None = None,
    causer_lemma: str | None = None,
    patient_lemma: str | None = None,
    topic_lemma: str | None = None,
    inner: bool = False,
) -> FStructure | None:
    """Find the first parse with the given role bindings. Set
    ``inner=True`` to look inside the matrix's XCOMP (for
    under-control cases)."""
    rs = parse_text(text, n_best=15)
    for _, f, _, _ in rs:
        target = f.feats.get("XCOMP") if inner else f
        if not isinstance(target, FStructure):
            continue
        if target.feats.get("PRED") != pred:
            continue
        if subj_lemma is not None:
            s = target.feats.get("SUBJ")
            if not (isinstance(s, FStructure) and s.feats.get("LEMMA") == subj_lemma):
                continue
        if causer_lemma is not None:
            oc = target.feats.get("OBJ-CAUSER")
            if not (isinstance(oc, FStructure) and oc.feats.get("LEMMA") == causer_lemma):
                continue
        if patient_lemma is not None:
            op = target.feats.get("OBJ-PATIENT")
            if not (isinstance(op, FStructure) and op.feats.get("LEMMA") == patient_lemma):
                continue
        if topic_lemma is not None:
            t = f.feats.get("TOPIC")
            if not (isinstance(t, FStructure) and t.feats.get("LEMMA") == topic_lemma):
                continue
        return f
    return None


# === Top-level 3-arg pa-DV =============================================


class TestTopLevelThreeArg:
    """Three-argument pa-DV at the matrix level. The pivot
    (``ang bata``) maps to LOCATION; the two GEN-NPs map
    positionally to OBJ-CAUSER (first) and OBJ-PATIENT (second).
    All three NP-order permutations parse."""

    def test_nom_gen_gen_order(self) -> None:
        # ``Pinakainan ang bata ng nanay ng kanin.``
        f = _find(
            "Pinakainan ang bata ng nanay ng kanin.",
            pred="CAUSE-EAT-AT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>",
            subj_lemma="bata",
            causer_lemma="nanay",
            patient_lemma="kanin",
        )
        assert f is not None

    def test_gen_nom_gen_order(self) -> None:
        # ``Pinakainan ng nanay ang bata ng kanin.``
        f = _find(
            "Pinakainan ng nanay ang bata ng kanin.",
            pred="CAUSE-EAT-AT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>",
            subj_lemma="bata",
            causer_lemma="nanay",
            patient_lemma="kanin",
        )
        assert f is not None

    def test_gen_gen_nom_order(self) -> None:
        # ``Pinakainan ng nanay ng kanin ang bata.``
        f = _find(
            "Pinakainan ng nanay ng kanin ang bata.",
            pred="CAUSE-EAT-AT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>",
            subj_lemma="bata",
            causer_lemma="nanay",
            patient_lemma="kanin",
        )
        assert f is not None

    def test_basa_three_arg(self) -> None:
        # ``Pinabasahan ng nanay ng libro ang bata.``
        f = _find(
            "Pinabasahan ng nanay ng libro ang bata.",
            pred="CAUSE-READ-AT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>",
            subj_lemma="bata",
            causer_lemma="nanay",
            patient_lemma="libro",
        )
        assert f is not None

    def test_inom_three_arg(self) -> None:
        # ``Pinainuman ng nanay ng kanin ang bata.`` (rice-as-drink
        # is semantically odd but structurally fine)
        f = _find(
            "Pinainuman ng nanay ng kanin ang bata.",
            pred="CAUSE-DRINK-AT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>",
            subj_lemma="bata",
            causer_lemma="nanay",
            patient_lemma="kanin",
        )
        assert f is not None

    def test_two_arg_regression(self) -> None:
        """The 2-arg pa-DV reading still parses (no overt
        PATIENT)."""
        f = _find(
            "Pinakainan ng nanay ang bata.",
            pred="CAUSE-EAT-AT <SUBJ, OBJ-CAUSER>",
            subj_lemma="bata",
            causer_lemma="nanay",
        )
        assert f is not None


# === 3-arg pa-DV under control ==========================================


class TestUnderControl:
    """3-arg pa-DV embedded under control verbs. The XCOMP slot
    holds the pa-DV's f-structure; the controller chains to the
    embedded ``OBJ-CAUSER`` (the CAUSER is the gap)."""

    def test_psych_control_psych_3arg(self) -> None:
        """``Gusto kong pakakainan ang bata ng kanin.`` The
        controller (matrix SUBJ = ko) routes to the embedded
        ``OBJ-CAUSER`` slot."""
        f = _find(
            "Gusto kong pakakainan ang bata ng kanin.",
            pred="CAUSE-EAT-AT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>",
            subj_lemma="bata",
            patient_lemma="kanin",
            inner=True,
        )
        assert f is not None
        # Verify the controller chain: matrix.SUBJ === XCOMP.OBJ-CAUSER.
        m_subj = f.feats["SUBJ"]
        xcomp = f.feats["XCOMP"]
        assert isinstance(xcomp, FStructure)
        oc = xcomp.feats["OBJ-CAUSER"]
        assert isinstance(m_subj, FStructure)
        assert isinstance(oc, FStructure)
        assert m_subj.id == oc.id

    def test_intrans_control_psych_3arg(self) -> None:
        """``Pumayag akong pakakainan ang bata ng kanin.`` Same
        with INTRANS control."""
        f = _find(
            "Pumayag akong pakakainan ang bata ng kanin.",
            pred="CAUSE-EAT-AT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>",
            subj_lemma="bata",
            patient_lemma="kanin",
            inner=True,
        )
        assert f is not None

    def test_3arg_padv_inner_order_alt(self) -> None:
        """Inner GEN-NOM order:
        ``Gusto kong pakakainan ng kanin ang bata.``"""
        f = _find(
            "Gusto kong pakakainan ng kanin ang bata.",
            pred="CAUSE-EAT-AT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>",
            subj_lemma="bata",
            patient_lemma="kanin",
            inner=True,
        )
        assert f is not None


# === ay-fronting 3-arg pa-DV ============================================


class TestAyFronting:
    """3-arg pa-DV with the CAUSER or PATIENT fronted via ``ay``."""

    def test_causer_fronted(self) -> None:
        """``Ng nanay ay pinakainan ang bata ng kanin.`` "It was
        mother who fed rice to the child." Fronted GEN = CAUSER;
        retained GEN = PATIENT."""
        f = _find(
            "Ng nanay ay pinakainan ang bata ng kanin.",
            pred="CAUSE-EAT-AT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>",
            subj_lemma="bata",
            causer_lemma="nanay",
            patient_lemma="kanin",
            topic_lemma="nanay",
        )
        assert f is not None

    def test_patient_fronted(self) -> None:
        """``Ng kanin ay pinakainan ng nanay ang bata.`` "It was
        rice that mother fed to the child." Fronted GEN = PATIENT;
        retained GEN = CAUSER. Routes through ``S_GAP_OBJ_PATIENT``
        with the new pa-DV branch."""
        f = _find(
            "Ng kanin ay pinakainan ng nanay ang bata.",
            pred="CAUSE-EAT-AT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>",
            subj_lemma="bata",
            causer_lemma="nanay",
            patient_lemma="kanin",
            topic_lemma="kanin",
        )
        assert f is not None


# === LMT diagnostics ====================================================


class TestLmtDiagnostics:
    """The new construction produces no blocking LMT diagnostics
    (``apply_lmt_with_check`` validates the new
    ``_DV_CAUS_DIRECT_THREE_ARG`` profile against the 3-GF
    f-structure)."""

    def test_no_blocking_top_level(self) -> None:
        rs = parse_text("Pinakainan ng nanay ng kanin ang bata.", n_best=5)
        for _, _f, _c, diags in rs:
            blocking = [d for d in diags if d.kind != "lmt-mismatch"]
            assert blocking == [], f"unexpected blocking diags: {blocking}"

    def test_no_blocking_under_control(self) -> None:
        rs = parse_text(
            "Gusto kong pakakainan ang bata ng kanin.", n_best=5
        )
        for _, _f, _c, diags in rs:
            blocking = [d for d in diags if d.kind != "lmt-mismatch"]
            assert blocking == [], f"unexpected blocking diags: {blocking}"

    def test_no_blocking_ay_fronting(self) -> None:
        rs = parse_text(
            "Ng nanay ay pinakainan ang bata ng kanin.", n_best=5
        )
        for _, _f, _c, diags in rs:
            blocking = [d for d in diags if d.kind != "lmt-mismatch"]
            assert blocking == [], f"unexpected blocking diags: {blocking}"


# === Regression: 2-arg pa-DV unchanged ==================================


class TestRegression2Arg:
    """The Phase 5d Commit 2 / Commit 8 2-arg pa-DV
    constructions still work."""

    def test_2arg_top_level(self) -> None:
        f = _first("Pinakainan ng nanay ang bata.")
        assert f.feats.get("PRED") == "CAUSE-EAT-AT <SUBJ, OBJ-CAUSER>"

    def test_2arg_under_control(self) -> None:
        rs = parse_text("Gusto kong pakakainan ang bata.", n_best=10)
        seen = False
        for _, fl, _, _ in rs:
            x = fl.feats.get("XCOMP")
            if isinstance(x, FStructure) and x.feats.get("PRED") == "CAUSE-EAT-AT <SUBJ, OBJ-CAUSER>":
                seen = True
                break
        assert seen

    def test_2arg_ay_fronting(self) -> None:
        f = _find(
            "Ng nanay ay pinakainan ang bata.",
            pred="CAUSE-EAT-AT <SUBJ, OBJ-CAUSER>",
            subj_lemma="bata",
            causer_lemma="nanay",
            topic_lemma="nanay",
        )
        assert f is not None
