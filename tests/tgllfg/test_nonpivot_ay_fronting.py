"""Phase 5d Commit 5: non-pivot ay-fronting (§7.4 deferral lifted).

Phase 4 §7.4 admitted only SUBJ-pivot ay-fronting via the wrap rule
``S → NP[CASE=NOM] PART[LINK=AY] S_GAP``. S&O §6 (Schachter & Otanes
1972) and Kroeger 1993 describe topicalization-style ay-fronting of
non-pivot phrases — OBJ-θ in any voice, plus DAT-marked obliques —
with similar topic-marking semantics. This commit adds three new
gap-category non-terminals (``S_GAP_OBJ``, ``S_GAP_OBJ_AGENT``,
``S_GAP_OBL``) plus three matching wrap rules.

The fronted NP's case marker disambiguates which gap-category the
parser uses:

* ``ang Maria ay ...`` (NOM)  → ``S_GAP``           (SUBJ extracted)
* ``ng isda ay ...``  (GEN, AV)  → ``S_GAP_OBJ``    (OBJ extracted)
* ``ni Maria ay ...`` (GEN, non-AV) → ``S_GAP_OBJ_AGENT``
  (OBJ-AGENT, the actor, extracted)
* ``sa bahay ay ...`` (DAT) → ``S_GAP_OBL``         (ADJUNCT-member
  extracted)

The voice / feature constraints on each S_GAP_X frame's V token
select the right gap-category in concert with the wrap rule's
fronted-NP case. Each fronted phrase fills the matrix ``TOPIC`` and
the inner clause's ``REL-PRO``; the inner clause's binding equation
then routes ``REL-PRO`` to the right GF (or set, for OBL).

These tests cover:

* AV OBJ-fronting (``Ng isda ay kumain si Maria``).
* Non-AV OBJ-AGENT-fronting in OV / DV / IV variants
  (CONVEY / INSTR / REASON).
* DAT-marked OBL-fronting in AV (intransitive and transitive) and
  OV.
* Per-construction TOPIC equals the fronted NP.
* Negation under fronting (``Ng isda ay hindi kumain si Maria``).
* Regression: SUBJ-fronting still produces the same f-structure
  shape as Phase 4.
* Regression: SUBJ-relativization still works (uses the unchanged
  ``S_GAP``, not the new gap-categories).
* LMT diagnostics: no blocking diagnostics on any new construction.
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
    TOPIC.LEMMA == topic_lemma, else None. Handles the Phase 4
    §7.8 NP-internal possessive ambiguity (``ng isda`` could be
    parsed as a possessor on a head NP) by skipping parses without
    a topic match."""
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        if f.feats.get("PRED") != expected_pred:
            continue
        topic = f.feats.get("TOPIC")
        if isinstance(topic, FStructure) and topic.feats.get("LEMMA") == topic_lemma:
            return f
    return None


# === AV OBJ-fronting (S_GAP_OBJ) =========================================


class TestAvObjFronting:
    """Phase 5d Commit 5: ``Ng isda ay kumain si Maria`` —
    fronted GEN-NP fills the inner AV clause's bare ``OBJ``."""

    def test_av_obj_basic(self) -> None:
        f = _first("Ng isda ay kumain si Maria.")
        assert f.feats.get("PRED") == "EAT <SUBJ, OBJ>"
        assert f.feats.get("VOICE") == "AV"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "isda"
        # OBJ is bound to TOPIC via REL-PRO.
        obj = f.feats["OBJ"]
        assert isinstance(obj, FStructure)
        assert obj.feats.get("LEMMA") == "isda"
        # SUBJ is overt in the inner clause.
        subj = f.feats["SUBJ"]
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "maria"

    def test_av_obj_with_adjunct(self) -> None:
        f = _first("Ng isda ay kumain si Maria sa bahay.")
        assert f.feats.get("PRED") == "EAT <SUBJ, OBJ>"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "isda"
        # The DAT-NP retained inside the inner clause becomes an
        # ADJUNCT member.
        adj = f.feats.get("ADJUNCT")
        assert adj is not None
        adj_lemmas = [m.feats.get("LEMMA") for m in adj]  # type: ignore[union-attr]
        assert "bahay" in adj_lemmas

    def test_av_obj_negated(self) -> None:
        f = _first("Ng isda ay hindi kumain si Maria.")
        assert f.feats.get("PRED") == "EAT <SUBJ, OBJ>"
        assert f.feats.get("POLARITY") == "NEG"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "isda"


# === Non-AV OBJ-AGENT-fronting (S_GAP_OBJ_AGENT) ========================


class TestNonAvObjAgentFronting:
    """The fronted GEN-NP in non-AV ay-fronting is the actor (the
    typed ``OBJ-AGENT`` slot under Phase 5b's OBJ-θ-in-grammar
    alignment); the inner SUBJ pivot (patient / recipient / theme)
    is overt."""

    def test_ov_obj_agent_basic(self) -> None:
        f = _first("Ni Maria ay kinain ang isda.")
        assert f.feats.get("PRED") == "EAT <SUBJ, OBJ-AGENT>"
        assert f.feats.get("VOICE") == "OV"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "maria"
        oa = f.feats["OBJ-AGENT"]
        assert isinstance(oa, FStructure)
        assert oa.feats.get("LEMMA") == "maria"
        subj = f.feats["SUBJ"]
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "isda"

    def test_dv_obj_agent_basic(self) -> None:
        # ``kinainan`` is DV (recipient pivot, "place where eaten").
        f = _first("Ng bata ay kinainan ang nanay.")
        assert f.feats.get("PRED") == "KAIN <SUBJ, OBJ-AGENT>"
        assert f.feats.get("VOICE") == "DV"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "bata"
        oa = f.feats["OBJ-AGENT"]
        assert isinstance(oa, FStructure)
        assert oa.feats.get("LEMMA") == "bata"

    def test_iv_convey_obj_agent(self) -> None:
        # IV-BEN (CONVEY): ``ipinaggawa`` "made for".
        f = _first("Ng nanay ay ipinaggawa ang bata.")
        assert f.feats.get("PRED") == "MAKE-FOR <SUBJ, OBJ-AGENT>"
        assert f.feats.get("VOICE") == "IV"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "nanay"

    def test_iv_instr_obj_agent(self) -> None:
        # IV-INSTR: ``ipinambili`` "bought with".
        f = _first("Ng nanay ay ipinambili ang pera.")
        assert f.feats.get("PRED") == "BUY-WITH <SUBJ, OBJ-AGENT>"
        assert f.feats.get("VOICE") == "IV"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "nanay"

    def test_iv_reason_obj_agent(self) -> None:
        # IV-REASON: ``ikinasulat`` "wrote because of".
        f = _first("Ng bata ay ikinasulat ang gutom.")
        assert f.feats.get("PRED") == "WRITE-FOR-REASON <SUBJ, OBJ-AGENT>"
        assert f.feats.get("VOICE") == "IV"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "bata"


# === DAT-marked OBL-fronting (S_GAP_OBL) ================================


class TestOblFronting:
    """Fronted DAT-NPs join ADJUNCT via set membership; the
    multi-OBL classifier (Phase 5c §8 follow-on) may then move
    them into typed ``OBL-LOC`` / ``OBL-RECIP`` slots based on the
    head-noun's lemma class."""

    def test_av_intransitive(self) -> None:
        f = _first("Sa bahay ay kumain si Maria.")
        assert f.feats.get("PRED") == "EAT <SUBJ>"
        assert f.feats.get("VOICE") == "AV"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "bahay"
        # The fronted DAT joins ADJUNCT (or moves to OBL-LOC via
        # the classifier; either landing spot satisfies the test).
        adj_or_obl_lemmas: set[object] = set()
        adj = f.feats.get("ADJUNCT")
        if adj is not None:
            adj_or_obl_lemmas |= {m.feats.get("LEMMA") for m in adj}  # type: ignore[union-attr]
        for slot in ("OBL-LOC", "OBL-RECIP", "OBL-GOAL"):
            v = f.feats.get(slot)
            if isinstance(v, FStructure):
                adj_or_obl_lemmas.add(v.feats.get("LEMMA"))
        assert "bahay" in adj_or_obl_lemmas

    def test_av_transitive(self) -> None:
        # ``Sa bahay ay kumain si Maria ng isda.`` — the AV-OBJ
        # (``ng isda``) is retained; the DAT (``sa bahay``) is
        # the fronted topic.
        f = _find_topic_parse(
            "Sa bahay ay kumain si Maria ng isda.",
            "EAT <SUBJ, OBJ>",
            "bahay",
        )
        assert f is not None
        assert f.feats.get("VOICE") == "AV"
        obj = f.feats["OBJ"]
        assert isinstance(obj, FStructure)
        assert obj.feats.get("LEMMA") == "isda"

    def test_ov_transitive(self) -> None:
        # OV: ``Sa bahay ay kinain ni Maria ang isda.`` — DAT
        # extracted; OV's typed OBJ-AGENT (``ni Maria``) and SUBJ
        # pivot (``ang isda``) are retained.
        f = _find_topic_parse(
            "Sa bahay ay kinain ni Maria ang isda.",
            "EAT <SUBJ, OBJ-AGENT>",
            "bahay",
        )
        assert f is not None
        assert f.feats.get("VOICE") == "OV"
        oa = f.feats["OBJ-AGENT"]
        assert isinstance(oa, FStructure)
        assert oa.feats.get("LEMMA") == "maria"
        subj = f.feats["SUBJ"]
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "isda"

    def test_obl_negated(self) -> None:
        f = _first("Sa bahay ay hindi kumain si Maria.")
        assert f.feats.get("PRED") == "EAT <SUBJ>"
        assert f.feats.get("POLARITY") == "NEG"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "bahay"


# === Regressions =========================================================


class TestRegressions:

    def test_subj_fronting_still_works(self) -> None:
        # Phase 4 §7.4 SUBJ-fronting via S_GAP must still produce
        # TOPIC=SUBJ with the same f-structure shape.
        f = _first("Si Maria ay kumain ng isda.")
        assert f.feats.get("PRED") == "EAT <SUBJ, OBJ>"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "maria"
        subj = f.feats["SUBJ"]
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "maria"
        # OBJ is the in-clause GEN-NP, NOT the topic.
        obj = f.feats["OBJ"]
        assert isinstance(obj, FStructure)
        assert obj.feats.get("LEMMA") == "isda"

    def test_subj_fronting_ov_still_works(self) -> None:
        f = _first("Ang isda ay kinain ng bata.")
        assert f.feats.get("PRED") == "EAT <SUBJ, OBJ-AGENT>"
        assert f.feats.get("VOICE") == "OV"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "isda"

    def test_subj_relativization_still_works(self) -> None:
        # Relativization uses S_GAP (unchanged). The new
        # gap-categories must not displace this parse.
        rs = parse_text("Tumakbo ang batang kumain ng isda.", n_best=10)
        assert rs
        # At least one parse must have SUBJ.ADJ containing an RC
        # with PRED=EAT <SUBJ, OBJ>.
        found = False
        for _, f, _, _ in rs:
            subj = f.feats.get("SUBJ")
            if not isinstance(subj, FStructure):
                continue
            adj = subj.feats.get("ADJ")
            if adj is None:
                continue
            for m in adj:  # type: ignore[union-attr]
                if isinstance(m, FStructure) and m.feats.get("PRED") == "EAT <SUBJ, OBJ>":
                    found = True
                    break
            if found:
                break
        assert found, "SUBJ relativization parse not found"

    def test_plain_av_transitive_unchanged(self) -> None:
        f = _first("Kumain si Maria ng isda.")
        assert f.feats.get("PRED") == "EAT <SUBJ, OBJ>"
        # No TOPIC on a plain (non-fronted) sentence.
        assert f.feats.get("TOPIC") is None


# === LMT diagnostics =====================================================


class TestNonPivotAyLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Ng isda ay kumain si Maria.",
            "Ni Maria ay kinain ang isda.",
            "Ng nanay ay ipinaggawa ang bata.",
            "Ng nanay ay ipinambili ang pera.",
            "Sa bahay ay kumain si Maria.",
            "Sa bahay ay kinain ni Maria ang isda.",
            "Ng isda ay hindi kumain si Maria.",
        ):
            rs = parse_text(s, n_best=10)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
