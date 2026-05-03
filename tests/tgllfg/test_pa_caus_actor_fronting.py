"""Phase 5e Commit 1: pa-OV / pa-DV (CAUS=DIRECT) actor-fronting.

Phase 5d Commit 5 added ``S_GAP_OBJ_AGENT`` for non-AV actor-fronting,
but only with ``CAUS=NONE`` — the constraint deliberately excluded
pa-OV / pa-DV (CAUS=DIRECT) because in monoclausal direct causatives
the actor's typed GF is ``OBJ-CAUSER``, not ``OBJ-AGENT``. Phase 5e
Commit 1 fills in the parallel extraction path with ``S_GAP_OBJ_CAUSER``
plus a matching wrap rule.

Construction shapes:

* 2-arg pa-OV: ``Ng nanay ay pinakain ang bata.``
  "It was mother who fed the child."
  PRED ``CAUSE-EAT <SUBJ, OBJ-CAUSER>``; SUBJ=bata (CAUSEE),
  OBJ-CAUSER=nanay (TOPIC).
* 3-arg pa-OV: ``Ng nanay ay pinakain ang bata ng kanin.``
  PRED ``CAUSE-EAT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>``; OBJ-PATIENT=kanin
  is overt inside the inner clause.
* 2-arg pa-DV: ``Ng nanay ay pinakainan ang bata.``
  PRED ``CAUSE-EAT-AT <SUBJ, OBJ-CAUSER>``; SUBJ=bata (LOCATION /
  recipient), OBJ-CAUSER=nanay (TOPIC).

The wrap rule disambiguates against ``S_GAP_OBJ_AGENT`` by the inner
V's CAUS feature: CAUS=DIRECT routes to ``S_GAP_OBJ_CAUSER``,
CAUS=NONE routes to ``S_GAP_OBJ_AGENT``.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.pipeline import parse_text


def _first(text: str) -> FStructure:
    rs = parse_text(text)
    assert rs, f"no parse for {text!r}"
    return rs[0][1]


def _find_topic_parse(
    text: str, expected_pred: str, topic_lemma: str
) -> FStructure | None:
    """Return the first parse with PRED == expected_pred and
    TOPIC.LEMMA == topic_lemma. The 3-arg construction is structurally
    ambiguous (a possessor reading on ``ng nanay ng kanin`` is
    available); the test asserts the actor-fronting parse is among
    the n-best."""
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        if f.feats.get("PRED") != expected_pred:
            continue
        topic = f.feats.get("TOPIC")
        if isinstance(topic, FStructure) and topic.feats.get("LEMMA") == topic_lemma:
            return f
    return None


# === 2-arg pa-OV (CAUSE-X <SUBJ, OBJ-CAUSER>) ===========================


class TestPaOvActorFronting:
    """``Ng nanay ay pinakain ang bata`` — fronted GEN-NP fills the
    inner pa-OV clause's typed ``OBJ-CAUSER``; the inner SUBJ
    (CAUSEE) stays overt."""

    def test_pa_ov_kain_pfv(self) -> None:
        f = _first("Ng nanay ay pinakain ang bata.")
        assert f.feats.get("PRED") == "CAUSE-EAT <SUBJ, OBJ-CAUSER>"
        assert f.feats.get("VOICE") == "OV"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "nanay"
        oc = f.feats["OBJ-CAUSER"]
        assert isinstance(oc, FStructure)
        assert oc.feats.get("LEMMA") == "nanay"
        # Topic and OBJ-CAUSER share f-node identity via REL-PRO.
        assert topic.id == oc.id
        subj = f.feats["SUBJ"]
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"

    def test_pa_ov_basa_pfv(self) -> None:
        f = _first("Ng nanay ay pinabasa ang bata.")
        assert f.feats.get("PRED") == "CAUSE-READ <SUBJ, OBJ-CAUSER>"
        assert f.feats.get("VOICE") == "OV"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "nanay"

    def test_pa_ov_inom_pfv(self) -> None:
        f = _first("Ng nanay ay pinainom ang bata.")
        assert f.feats.get("PRED") == "CAUSE-DRINK <SUBJ, OBJ-CAUSER>"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "nanay"

    def test_pa_ov_ipfv_aspect(self) -> None:
        """IPFV form ``pinakakain`` parses with the same fronting."""
        f = _first("Ng nanay ay pinakakain ang bata.")
        assert f.feats.get("PRED") == "CAUSE-EAT <SUBJ, OBJ-CAUSER>"
        assert f.feats.get("ASPECT") == "IPFV"

    def test_pa_ov_negated(self) -> None:
        """Inner negation under ay-fronting composes."""
        f = _first("Ng nanay ay hindi pinakain ang bata.")
        assert f.feats.get("PRED") == "CAUSE-EAT <SUBJ, OBJ-CAUSER>"
        assert f.feats.get("POLARITY") == "NEG"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "nanay"


# === 3-arg pa-OV (CAUSE-X <SUBJ, OBJ-CAUSER, OBJ-PATIENT>) ==============


class TestPaOvThreeArgActorFronting:
    """3-arg pa-OV with the actor (CAUSER) fronted leaves both the
    NOM pivot (CAUSEE) and a GEN OBJ-PATIENT inside the inner
    clause. Both NP orders parse via the two grammar variants."""

    def test_pa_ov_3arg_nom_gen_order(self) -> None:
        # Inner NP order: NOM first, GEN second.
        f = _find_topic_parse(
            "Ng nanay ay pinakain ang bata ng kanin.",
            "CAUSE-EAT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>",
            "nanay",
        )
        assert f is not None
        assert f.feats.get("VOICE") == "OV"
        subj = f.feats["SUBJ"]
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        op = f.feats["OBJ-PATIENT"]
        assert isinstance(op, FStructure)
        assert op.feats.get("LEMMA") == "kanin"
        oc = f.feats["OBJ-CAUSER"]
        assert isinstance(oc, FStructure)
        assert oc.feats.get("LEMMA") == "nanay"

    def test_pa_ov_3arg_gen_nom_order(self) -> None:
        # Inner NP order: GEN first, NOM second.
        f = _find_topic_parse(
            "Ng nanay ay pinakain ng kanin ang bata.",
            "CAUSE-EAT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>",
            "nanay",
        )
        assert f is not None
        subj = f.feats["SUBJ"]
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        op = f.feats["OBJ-PATIENT"]
        assert isinstance(op, FStructure)
        assert op.feats.get("LEMMA") == "kanin"

    def test_pa_ov_3arg_basa(self) -> None:
        f = _find_topic_parse(
            "Ng nanay ay pinabasa ang bata ng libro.",
            "CAUSE-READ <SUBJ, OBJ-CAUSER, OBJ-PATIENT>",
            "nanay",
        )
        assert f is not None


# === 2-arg pa-DV (CAUSE-X-AT <SUBJ, OBJ-CAUSER>) ========================


class TestPaDvActorFronting:
    """pa-DV (``pa-...-an``) actor-fronting parallels pa-OV: the
    actor (CAUSER, GEN) is fronted; the inner SUBJ pivot is the
    location/recipient (NOM)."""

    def test_pa_dv_kain(self) -> None:
        f = _first("Ng nanay ay pinakainan ang bata.")
        assert f.feats.get("PRED") == "CAUSE-EAT-AT <SUBJ, OBJ-CAUSER>"
        assert f.feats.get("VOICE") == "DV"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "nanay"
        oc = f.feats["OBJ-CAUSER"]
        assert isinstance(oc, FStructure)
        assert oc.feats.get("LEMMA") == "nanay"
        subj = f.feats["SUBJ"]
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"

    def test_pa_dv_basa(self) -> None:
        f = _first("Ng nanay ay pinabasahan ang bata.")
        assert f.feats.get("PRED") == "CAUSE-READ-AT <SUBJ, OBJ-CAUSER>"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "nanay"

    def test_pa_dv_inom(self) -> None:
        f = _first("Ng nanay ay pinainuman ang bata.")
        assert f.feats.get("PRED") == "CAUSE-DRINK-AT <SUBJ, OBJ-CAUSER>"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "nanay"


# === Discrimination: S_GAP_OBJ_AGENT vs S_GAP_OBJ_CAUSER ================


class TestGapDisambiguation:
    """The CAUS feature on the inner V disambiguates which
    gap-category fires. Plain non-AV verbs (CAUS=NONE) keep going
    through ``S_GAP_OBJ_AGENT``; pa-causative verbs (CAUS=DIRECT)
    go through the new ``S_GAP_OBJ_CAUSER``. The two paths produce
    different f-structures (``OBJ-AGENT`` vs ``OBJ-CAUSER``) so
    they don't cross-fire."""

    def test_plain_ov_routes_to_obj_agent(self) -> None:
        """Regression: ``Ni Maria ay kinain ang isda`` (Phase 5d
        Commit 5) still routes to OBJ-AGENT, NOT OBJ-CAUSER."""
        f = _first("Ni Maria ay kinain ang isda.")
        assert f.feats.get("PRED") == "EAT <SUBJ, OBJ-AGENT>"
        assert "OBJ-AGENT" in f.feats
        assert "OBJ-CAUSER" not in f.feats

    def test_pa_ov_routes_to_obj_causer(self) -> None:
        """The new construction routes to OBJ-CAUSER, NOT OBJ-AGENT."""
        f = _first("Ng nanay ay pinakain ang bata.")
        assert f.feats.get("PRED") == "CAUSE-EAT <SUBJ, OBJ-CAUSER>"
        assert "OBJ-CAUSER" in f.feats
        assert "OBJ-AGENT" not in f.feats

    def test_no_obj_agent_parse_for_pa_ov_fronting(self) -> None:
        """``Ng nanay ay pinakain ang bata`` should never produce a
        bare-OV ``EAT`` reading; the V is a pa-causative
        (CAUS=DIRECT), not a plain OV."""
        rs = parse_text("Ng nanay ay pinakain ang bata.", n_best=10)
        preds = {str(f.feats.get("PRED")) for _, f, _, _ in rs}
        assert all(
            "CAUSE" in p for p in preds
        ), f"plain non-causative reading leaked through: {preds}"


# === Top-level pa-causative regressions =================================


class TestRegressionTopLevelPaCausatives:
    """The new gap-category and wrap rule must not affect top-level
    pa-causative parses (Phase 4 §7.7 + Phase 5d Commits 2 / 8)."""

    def test_top_level_pa_ov_unchanged(self) -> None:
        f = _first("Pinakain ng nanay ang bata.")
        assert f.feats.get("PRED") == "CAUSE-EAT <SUBJ, OBJ-CAUSER>"
        assert f.feats.get("VOICE") == "OV"
        # No TOPIC — this isn't an ay-fronted clause.
        assert "TOPIC" not in f.feats

    def test_top_level_pa_dv_unchanged(self) -> None:
        f = _first("Pinakainan ng nanay ang bata.")
        assert f.feats.get("PRED") == "CAUSE-EAT-AT <SUBJ, OBJ-CAUSER>"
        assert f.feats.get("VOICE") == "DV"
        assert "TOPIC" not in f.feats

    def test_top_level_3arg_pa_ov_unchanged(self) -> None:
        # Phase 5b multi-GEN-NP three-arg pa-OV: ``Pinakain ng nanay
        # ng kanin ang bata`` should still parse with the 3-arg PRED
        # (top-level multi-GEN, not the new ay-fronting path).
        rs = parse_text("Pinakain ng nanay ng kanin ang bata.", n_best=10)
        preds = {str(f.feats.get("PRED")) for _, f, _, _ in rs}
        assert "CAUSE-EAT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>" in preds


# === LMT diagnostics ===================================================


class TestLmtDiagnostics:
    """The new construction should produce no blocking LMT
    diagnostics: the engine's mapping (CAUSER → OBJ-CAUSER, CAUSEE →
    SUBJ) matches the f-structure's GFs, and the wrap-rule
    constraining equation ``(↓3 REL-PRO) =c (↓3 OBJ-CAUSER)`` is
    satisfied because S_GAP_OBJ_CAUSER's binding equation supplies
    OBJ-CAUSER from REL-PRO."""

    def test_no_blocking_diagnostics_2arg_pa_ov(self) -> None:
        rs = parse_text("Ng nanay ay pinakain ang bata.", n_best=5)
        for _, _f, _c, diags in rs:
            blocking = [d for d in diags if d.kind != "lmt-mismatch"]
            assert blocking == [], f"unexpected blocking diags: {blocking}"

    def test_no_blocking_diagnostics_pa_dv(self) -> None:
        rs = parse_text("Ng nanay ay pinakainan ang bata.", n_best=5)
        for _, _f, _c, diags in rs:
            blocking = [d for d in diags if d.kind != "lmt-mismatch"]
            assert blocking == [], f"unexpected blocking diags: {blocking}"
