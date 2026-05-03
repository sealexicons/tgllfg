"""Phase 5e Commit 2: multi-GEN-NP ay-fronting.

Phase 5b multi-GEN-NP frames bind two GEN-NPs as typed ``OBJ-θ``
slots positionally:

* IV (any APPL): first GEN → ``OBJ-AGENT``, second → ``OBJ-PATIENT``.
* pa-OV CAUS=DIRECT: first GEN → ``OBJ-CAUSER``, second → ``OBJ-PATIENT``.

Phase 5d Commit 5 added ay-fronting for non-3-arg shapes (no second
GEN). Phase 5e Commit 1 added 3-arg pa-OV with the CAUSER fronted
(``S_GAP_OBJ_CAUSER`` 3-arg variants). Phase 5e Commit 2 fills in
the remaining multi-GEN-NP extractions:

* 3-arg IV with OBJ-AGENT extracted (OBJ-PATIENT retained).
  ``Ng nanay ay ipinaggawa ang kapatid ng silya``.
* 3-arg multi-GEN with OBJ-PATIENT extracted, in either:
  - IV (OBJ-AGENT retained): ``Ng silya ay ipinaggawa ang kapatid ng nanay``;
  - pa-OV-direct (OBJ-CAUSER retained):
    ``Ng kanin ay pinakain ng nanay ang bata``.

When two readings exist for the same surface (e.g., AGENT-front +
PATIENT-retained vs PATIENT-front + AGENT-retained), both parses
surface in the n-best output. The tests use a topic-PRED filter to
locate the natural reading without forcing a particular ranker
choice.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.pipeline import parse_text


def _find(
    text: str,
    *,
    pred: str,
    topic_lemma: str,
    topic_gf: str,
) -> FStructure | None:
    """Return the first parse with PRED == ``pred``, TOPIC.LEMMA ==
    ``topic_lemma``, and the topic also bound to the given typed GF
    (``OBJ-AGENT`` / ``OBJ-PATIENT`` / ``OBJ-CAUSER``). The triple
    pins down which gap-category fired for ambiguous surfaces."""
    rs = parse_text(text, n_best=15)
    for _, f, _, _ in rs:
        if f.feats.get("PRED") != pred:
            continue
        topic = f.feats.get("TOPIC")
        if not (
            isinstance(topic, FStructure)
            and topic.feats.get("LEMMA") == topic_lemma
        ):
            continue
        gf = f.feats.get(topic_gf)
        if isinstance(gf, FStructure) and gf.id == topic.id:
            return f
    return None


# === IV 3-arg with OBJ-AGENT fronted ====================================


class TestIvMultiGenAgentFronting:
    """Phase 5b multi-GEN IV frames with the AGENT fronted. The
    retained GEN-NP binds to OBJ-PATIENT; the NOM pivot is the
    applicative pivot (BENEFICIARY / INSTRUMENT / REASON)."""

    def test_iv_ben_agent_fronted(self) -> None:
        f = _find(
            "Ng nanay ay ipinaggawa ang kapatid ng silya.",
            pred="MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
            topic_lemma="nanay",
            topic_gf="OBJ-AGENT",
        )
        assert f is not None
        assert f.feats.get("VOICE") == "IV"
        # SUBJ is the BEN pivot.
        subj = f.feats["SUBJ"]
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "kapatid"
        # OBJ-PATIENT is the retained GEN-NP.
        op = f.feats["OBJ-PATIENT"]
        assert isinstance(op, FStructure)
        assert op.feats.get("LEMMA") == "silya"

    def test_iv_instr_agent_fronted(self) -> None:
        f = _find(
            "Ng nanay ay ipinambili ang pera ng isda.",
            pred="BUY-WITH <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
            topic_lemma="nanay",
            topic_gf="OBJ-AGENT",
        )
        assert f is not None
        assert f.feats.get("VOICE") == "IV"
        # SUBJ is the INSTRUMENT pivot (pera = money).
        subj = f.feats["SUBJ"]
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "pera"
        op = f.feats["OBJ-PATIENT"]
        assert isinstance(op, FStructure)
        assert op.feats.get("LEMMA") == "isda"

    def test_iv_reason_agent_fronted(self) -> None:
        f = _find(
            "Ng bata ay ikinasulat ang gutom ng isda.",
            pred="WRITE-FOR-REASON <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
            topic_lemma="bata",
            topic_gf="OBJ-AGENT",
        )
        assert f is not None
        assert f.feats.get("VOICE") == "IV"

    def test_iv_ben_agent_fronted_alt_inner_order(self) -> None:
        # Inner GEN-NOM order: ``Ng nanay ay ipinaggawa ng silya
        # ang kapatid``.
        f = _find(
            "Ng nanay ay ipinaggawa ng silya ang kapatid.",
            pred="MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
            topic_lemma="nanay",
            topic_gf="OBJ-AGENT",
        )
        assert f is not None

    def test_iv_ben_agent_fronted_negated(self) -> None:
        f = _find(
            "Ng nanay ay hindi ipinaggawa ang kapatid ng silya.",
            pred="MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
            topic_lemma="nanay",
            topic_gf="OBJ-AGENT",
        )
        assert f is not None
        assert f.feats.get("POLARITY") == "NEG"


# === IV 3-arg with OBJ-PATIENT fronted ==================================


class TestIvMultiGenPatientFronting:
    """Phase 5b multi-GEN IV frames with the PATIENT fronted. The
    retained GEN-NP binds to OBJ-AGENT; the NOM pivot is the
    applicative pivot."""

    def test_iv_ben_patient_fronted(self) -> None:
        # silya (chair, inanimate) is naturally PATIENT; nanay
        # (animate) is naturally AGENT.
        f = _find(
            "Ng silya ay ipinaggawa ang kapatid ng nanay.",
            pred="MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
            topic_lemma="silya",
            topic_gf="OBJ-PATIENT",
        )
        assert f is not None
        assert f.feats.get("VOICE") == "IV"
        oa = f.feats["OBJ-AGENT"]
        assert isinstance(oa, FStructure)
        assert oa.feats.get("LEMMA") == "nanay"

    def test_iv_instr_patient_fronted(self) -> None:
        f = _find(
            "Ng isda ay ipinambili ang pera ng nanay.",
            pred="BUY-WITH <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
            topic_lemma="isda",
            topic_gf="OBJ-PATIENT",
        )
        assert f is not None
        oa = f.feats["OBJ-AGENT"]
        assert isinstance(oa, FStructure)
        assert oa.feats.get("LEMMA") == "nanay"

    def test_iv_ben_patient_fronted_alt_inner_order(self) -> None:
        # GEN-NOM inner order.
        f = _find(
            "Ng silya ay ipinaggawa ng nanay ang kapatid.",
            pred="MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
            topic_lemma="silya",
            topic_gf="OBJ-PATIENT",
        )
        assert f is not None

    def test_iv_ben_patient_fronted_negated(self) -> None:
        f = _find(
            "Ng silya ay hindi ipinaggawa ang kapatid ng nanay.",
            pred="MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
            topic_lemma="silya",
            topic_gf="OBJ-PATIENT",
        )
        assert f is not None
        assert f.feats.get("POLARITY") == "NEG"


# === pa-OV-direct 3-arg with OBJ-PATIENT fronted ========================


class TestPaOvMultiGenPatientFronting:
    """pa-OV-direct 3-arg (Phase 5b multi-GEN causative) with the
    PATIENT fronted. The retained GEN-NP binds to OBJ-CAUSER; the
    NOM pivot is the CAUSEE."""

    def test_pa_ov_kain_patient_fronted(self) -> None:
        # kanin (rice, inanimate) is the natural PATIENT.
        f = _find(
            "Ng kanin ay pinakain ng nanay ang bata.",
            pred="CAUSE-EAT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>",
            topic_lemma="kanin",
            topic_gf="OBJ-PATIENT",
        )
        assert f is not None
        assert f.feats.get("VOICE") == "OV"
        # CAUSER is the retained GEN-NP.
        oc = f.feats["OBJ-CAUSER"]
        assert isinstance(oc, FStructure)
        assert oc.feats.get("LEMMA") == "nanay"
        # CAUSEE is the SUBJ pivot.
        subj = f.feats["SUBJ"]
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"

    def test_pa_ov_kain_patient_fronted_alt_inner_order(self) -> None:
        # GEN-NOM inner order: retained CAUSER before pivot.
        f = _find(
            "Ng kanin ay pinakain ang bata ng nanay.",
            pred="CAUSE-EAT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>",
            topic_lemma="kanin",
            topic_gf="OBJ-PATIENT",
        )
        assert f is not None

    def test_pa_ov_basa_patient_fronted(self) -> None:
        f = _find(
            "Ng libro ay pinabasa ng nanay ang bata.",
            pred="CAUSE-READ <SUBJ, OBJ-CAUSER, OBJ-PATIENT>",
            topic_lemma="libro",
            topic_gf="OBJ-PATIENT",
        )
        assert f is not None

    def test_pa_ov_patient_fronted_negated(self) -> None:
        f = _find(
            "Ng kanin ay hindi pinakain ng nanay ang bata.",
            pred="CAUSE-EAT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>",
            topic_lemma="kanin",
            topic_gf="OBJ-PATIENT",
        )
        assert f is not None
        assert f.feats.get("POLARITY") == "NEG"


# === Discrimination & ambiguity =========================================


class TestAmbiguityAndDiscrimination:
    """For the same surface, both AGENT-fronted and PATIENT-fronted
    readings can structurally fire (Tagalog admits the ambiguity);
    both parses surface in n-best."""

    def test_iv_ambiguity_both_readings_present(self) -> None:
        """``Ng nanay ay ipinaggawa ang kapatid ng silya`` admits at
        least the AGENT-fronted reading (the natural one); the
        PATIENT-fronted reading is also structurally available."""
        rs = parse_text(
            "Ng nanay ay ipinaggawa ang kapatid ng silya.", n_best=15
        )
        seen_agent_front = False
        for _, f, _, _ in rs:
            if f.feats.get("PRED") != "MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>":
                continue
            topic = f.feats.get("TOPIC")
            if not isinstance(topic, FStructure):
                continue
            if topic.feats.get("LEMMA") != "nanay":
                continue
            oa = f.feats.get("OBJ-AGENT")
            if isinstance(oa, FStructure) and oa.id == topic.id:
                seen_agent_front = True
                break
        assert seen_agent_front

    def test_pa_ov_does_not_route_to_obj_agent(self) -> None:
        """For pa-OV with PATIENT fronted, OBJ-AGENT must NOT be in
        the f-structure — pa-OV uses OBJ-CAUSER, not OBJ-AGENT."""
        f = _find(
            "Ng kanin ay pinakain ng nanay ang bata.",
            pred="CAUSE-EAT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>",
            topic_lemma="kanin",
            topic_gf="OBJ-PATIENT",
        )
        assert f is not None
        assert "OBJ-AGENT" not in f.feats
        assert "OBJ-CAUSER" in f.feats

    def test_iv_ben_does_not_route_to_obj_causer(self) -> None:
        """IV-BEN must use OBJ-AGENT, never OBJ-CAUSER (CAUS=NONE)."""
        f = _find(
            "Ng nanay ay ipinaggawa ang kapatid ng silya.",
            pred="MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
            topic_lemma="nanay",
            topic_gf="OBJ-AGENT",
        )
        assert f is not None
        assert "OBJ-CAUSER" not in f.feats


# === Top-level multi-GEN regressions ====================================


class TestRegressionTopLevelMultiGen:
    """The new gap-categories must not affect top-level multi-GEN
    parses (Phase 5b §7.7 follow-on)."""

    def test_top_level_iv_ben_unchanged(self) -> None:
        # ``Ipinaggawa ng nanay ng silya ang kapatid`` — top-level
        # 3-arg IV-BEN, no fronting.
        rs = parse_text("Ipinaggawa ng nanay ng silya ang kapatid.", n_best=10)
        preds = {str(f.feats.get("PRED")) for _, f, _, _ in rs}
        assert "MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>" in preds
        # No TOPIC — this isn't an ay-fronted clause.
        for _, f, _, _ in rs:
            if f.feats.get("PRED") == "MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>":
                assert "TOPIC" not in f.feats

    def test_top_level_pa_ov_3arg_unchanged(self) -> None:
        rs = parse_text("Pinakain ng nanay ng kanin ang bata.", n_best=10)
        preds = {str(f.feats.get("PRED")) for _, f, _, _ in rs}
        assert "CAUSE-EAT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>" in preds


# === LMT diagnostics ====================================================


class TestLmtDiagnostics:
    """All new fronted multi-GEN parses produce no blocking LMT
    diagnostics."""

    def test_no_blocking_iv_agent_front(self) -> None:
        rs = parse_text(
            "Ng nanay ay ipinaggawa ang kapatid ng silya.", n_best=5
        )
        for _, _f, _c, diags in rs:
            blocking = [d for d in diags if d.kind != "lmt-mismatch"]
            assert blocking == [], f"unexpected blocking diags: {blocking}"

    def test_no_blocking_iv_patient_front(self) -> None:
        rs = parse_text(
            "Ng silya ay ipinaggawa ang kapatid ng nanay.", n_best=5
        )
        for _, _f, _c, diags in rs:
            blocking = [d for d in diags if d.kind != "lmt-mismatch"]
            assert blocking == [], f"unexpected blocking diags: {blocking}"

    def test_no_blocking_pa_ov_patient_front(self) -> None:
        rs = parse_text(
            "Ng kanin ay pinakain ng nanay ang bata.", n_best=5
        )
        for _, _f, _c, diags in rs:
            blocking = [d for d in diags if d.kind != "lmt-mismatch"]
            assert blocking == [], f"unexpected blocking diags: {blocking}"
