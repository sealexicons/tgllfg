"""Phase 5i Commit 8: indirect question embedding via ``kung``.

Roadmap §12.1 / plan-of-record §5.7, §6 Commit 8. Three pieces:

1. New uninflected stative predicate ``alam`` "know" added to
   ``data/tgl/particles.yaml`` with ``CTRL_CLASS=KNOW`` (parallel
   to gusto / ayaw / kaya's CTRL_CLASS=PSYCH but distinct so it
   doesn't cross-fire on the linker + S_XCOMP open-XCOMP wrap).
   PRED template ``KNOW <SUBJ, COMP>`` lives in
   ``src/tgllfg/core/lexicon.py``.

2. New non-terminal ``S_INTERROG_COMP`` in ``cfg/control.py``::

       S_INTERROG_COMP → PART[COMP_TYPE=INTERROG] S[Q_TYPE=WH]

   Lifts the inner S f-structure (``(↑) = ↓2``) and adds
   ``COMP_TYPE=INTERROG``. Belt-and-braces ``=c`` constraints
   close non-conflict-matcher leaks on both the complementizer's
   ``COMP_TYPE`` and the inner clause's ``Q_TYPE``.

3. New matrix wrap rule in ``cfg/control.py``::

       S → V[CTRL_CLASS=KNOW] NP[CASE=GEN] S_INTERROG_COMP

   The GEN-NP experiencer is matrix SUBJ (the same NOM→SUBJ
   deviation as PSYCH); the indirect-Q clause is matrix COMP. No
   linker between matrix and complement — ``alam`` is a stative
   and ``kung`` is the complementizer.

End-to-end target sentences (from plan §1):

    Hindi ko alam kung sino kumain.   "I don't know who ate."

The plan's bare-form ``kung sino kumain`` (no ``ang`` in inner)
is colloquial; this commit admits the standard form ``kung sino
ang kumain`` with the existing Phase 5i Commit 2 PRON-cleft on
the inner clause. Bare-form (``Sino kumain.`` as a stand-alone
embedded wh-Q without ``ang``) is deferred — see roadmap §18.

**Analytical note (XCOMP vs COMP)**: The plan-of-record §5.7
used the name ``XCOMP`` loosely. The actual LFG slot is
``COMP`` (closed sentential complement) because the embedded
clause has its own SUBJ (the wh-pivot) and there is no
SUBJ-control / linker. Documented in
docs/analysis-choices.md "Phase 5i §5.7".

**Out of scope this commit**:

* Bare-form colloquial ``kung sino kumain`` (no ``ang`` in
  inner) — needs a new wh-PRON-as-SUBJ rule for AV intransitive.
* Yes/no indirect-Q (``Alam ko kung kumain ang aso.``
  "I know whether the dog ate.") — current rule constrains
  ``S[Q_TYPE=WH]``; relaxing to admit declarative kung-clauses
  is a future commit.
* Other KNOW-class predicates (akala, isip, naaalala etc.) —
  only ``alam`` is added in this commit.
* Declarative-COMP factive embedding (``Alam kong kumain ang
  aso``) — Phase 5+ scope.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Basic indirect-Q parse with COMP_TYPE + COMP.Q_TYPE ==============


class TestIndirectQBasicShape:
    """``Alam ko kung sino ang kumain.`` — KNOW <SUBJ, COMP>;
    matrix COMP carries COMP_TYPE=INTERROG and Q_TYPE=WH (lifted
    from the embedded clause)."""

    def test_basic_shape(self) -> None:
        parses = parse_text("Alam ko kung sino ang kumain.")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "KNOW <SUBJ, COMP>"
        comp = fs.feats.get("COMP")
        assert comp is not None
        assert comp.feats.get("COMP_TYPE") == "INTERROG"
        assert comp.feats.get("Q_TYPE") == "WH"
        assert comp.feats.get("WH_LEMMA") == "sino"

    def test_subj_is_gen_pron(self) -> None:
        parses = parse_text("Alam ko kung sino ang kumain.")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("CASE") == "GEN"


# === Wh-PRON varieties inside the indirect-Q ==========================


class TestIndirectQWithVariousPronWh:
    """The inner clause is the existing PRON-cleft (Phase 5i
    Commit 2). ``sino`` (human), ``ano`` (thing), ``alin`` if
    used as PRON — all valid. WH_LEMMA on COMP reflects which
    wh-PRON was used."""

    @pytest.mark.parametrize("sentence,wh_lemma", [
        ("Alam ko kung sino ang kumain.",   "sino"),
        ("Alam ko kung ano ang kinain mo.", "ano"),
    ])
    def test_pron_wh_lemma(
        self, sentence: str, wh_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        comp = fs.feats.get("COMP")
        assert comp is not None
        assert comp.feats.get("WH_LEMMA") == wh_lemma


# === Adverbial wh inside indirect-Q ===================================


class TestIndirectQWithAdverbialWh:
    """Inner clause uses Phase 5i Commit 4's adverbial-wh
    fronting (saan / kailan / bakit / paano). The COMP carries
    Q_TYPE=WH and the WH_LEMMA matches the wh-ADV."""

    @pytest.mark.parametrize("sentence,wh_lemma", [
        ("Alam ko kung saan pumunta si Maria.",   "saan"),
        ("Alam ko kung kailan kumain ang aso.",   "kailan"),
        ("Alam ko kung bakit kumain ang aso.",    "bakit"),
        ("Alam ko kung paano kumain ang aso.",    "paano"),
    ])
    def test_adverbial_wh_lemma(
        self, sentence: str, wh_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        comp = fs.feats.get("COMP")
        assert comp is not None
        assert comp.feats.get("Q_TYPE") == "WH"
        assert comp.feats.get("WH_LEMMA") == wh_lemma


# === Wh-N cleft inside indirect-Q =====================================


class TestIndirectQWithWhNCleft:
    """Inner clause uses Phase 5i Commit 6's wh-N-cleft
    (``aling N ang ...``). COMP.WH_LEMMA = ``alin``."""

    def test_aling_inside(self) -> None:
        parses = parse_text("Alam ko kung aling bata ang kumain.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        comp = fs.feats.get("COMP")
        assert comp is not None
        assert comp.feats.get("Q_TYPE") == "WH"
        assert comp.feats.get("WH_LEMMA") == "alin"


# === Negation outside =================================================


class TestIndirectQUnderNegation:
    """``Hindi ko alam kung sino ang kumain.`` — POLARITY=NEG on
    matrix; the indirect-Q complement is unchanged."""

    def test_outer_negation(self) -> None:
        parses = parse_text("Hindi ko alam kung sino ang kumain.")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("POLARITY") == "NEG"
        assert fs.feats.get("PRED") == "KNOW <SUBJ, COMP>"
        comp = fs.feats.get("COMP")
        assert comp is not None
        assert comp.feats.get("COMP_TYPE") == "INTERROG"
        assert comp.feats.get("Q_TYPE") == "WH"

    def test_inner_negation(self) -> None:
        # Negation inside the indirect-Q complement: ``kung sino
        # ang hindi kumain`` — the inner SUBJ is a headless RC
        # whose verbal element is negated.
        parses = parse_text(
            "Alam ko kung sino ang hindi kumain."
        )
        assert len(parses) >= 1


# === Q_TYPE = WH constraint on inner ==================================


class TestIndirectQRequiresWhInner:
    """The S_INTERROG_COMP rule constrains ``(↓2 Q_TYPE) =c
    'WH'``. Declarative kung-clauses (no wh inside) and yes/no
    kung-clauses (Q_TYPE=YES_NO) do NOT match."""

    def test_declarative_kung_clause_rejected(self) -> None:
        # ``Alam ko kung kumain ang aso.`` — no wh inside.
        # The current rule rejects this; yes/no-indirect-Q is a
        # future commit. 0 parses expected.
        parses = parse_text("Alam ko kung kumain ang aso.")
        assert len(parses) == 0

    def test_yes_no_inside_kung_rejected(self) -> None:
        # ``Alam ko kung kumain ka ba.`` — yes/no Q inside.
        # 0 parses (Q_TYPE=YES_NO doesn't match Q_TYPE=WH).
        parses = parse_text("Alam ko kung kumain ka ba.")
        assert len(parses) == 0


# === KNOW-class doesn't cross-fire on PSYCH ===========================


class TestPsychDoesNotCrossFire:
    """gusto / ayaw / kaya carry CTRL_CLASS=PSYCH (not KNOW), so
    the new KNOW wrap rule does not match them. Conversely, the
    existing PSYCH wrap rule requires a linker + S_XCOMP, which
    the kung-S_INTERROG_COMP doesn't fit."""

    @pytest.mark.parametrize("sentence", [
        "Gusto ko kung sino ang kumain.",
        "Hindi ko gusto kung sino ang kumain.",
        "Ayaw ko kung sino ang kumain.",
        "Kaya ko kung sino ang kumain.",
    ])
    def test_psych_with_kung_rejected(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 0


# === Matrix SUBJ must be GEN ==========================================


class TestMatrixSubjMustBeGen:
    """The wrap rule requires ``NP[CASE=GEN]`` for the
    experiencer. NOM-marked SUBJ doesn't match (no NOM-experiencer
    rule for KNOW)."""

    def test_nom_experiencer_rejected(self) -> None:
        # ``Alam si Maria kung sino ang kumain.`` — si Maria is
        # NOM, but the rule wants GEN.
        parses = parse_text(
            "Alam si Maria kung sino ang kumain."
        )
        assert len(parses) == 0

    def test_gen_full_np_works(self) -> None:
        # ``Alam ng bata kung sino ang kumain.`` — full GEN-NP
        # ``ng bata`` (not just clitic ``ko``).
        parses = parse_text(
            "Alam ng bata kung sino ang kumain."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "KNOW <SUBJ, COMP>"


# === alam without complement does not parse ===========================


class TestAlamRequiresComplement:
    """``alam`` is uninflected and has no clause-level rule
    accepting it in isolation. ``Alam ko.`` (no complement) and
    ``Alam kong kumain.`` (linker + S_XCOMP — would require
    CTRL_CLASS=PSYCH, but alam is KNOW) both 0-parse."""

    def test_alam_alone(self) -> None:
        parses = parse_text("Alam ko.")
        assert len(parses) == 0

    def test_alam_with_linker_xcomp_rejected(self) -> None:
        # alam is CTRL_CLASS=KNOW, not PSYCH; the existing PSYCH
        # wrap won't match. The KNOW wrap requires
        # S_INTERROG_COMP, not S_XCOMP. 0 parses.
        parses = parse_text("Alam kong kumain.")
        assert len(parses) == 0


# === Earlier Phase 5i baselines preserved =============================


class TestPhase5iEarlierCommitsPreserved:
    """Adding the indirect-Q rule must not perturb earlier Phase
    5i constructions: cleft (Commit 2), in-situ (Commit 3),
    adverbial (Commit 4), yes/no (Commit 5), aling (Commit 6),
    tag (Commit 7)."""

    @pytest.mark.parametrize("sentence,q_type", [
        ("Sino ang kumain?",                 "WH"),
        ("Saan ka pumunta?",                 "WH"),
        ("Bakit ka kumain?",                 "WH"),
        ("Aling bata ang kumain?",           "WH"),
        ("Kumain ka ba ng kanin?",           "YES_NO"),
        ("Maganda ang bata, di ba?",         "TAG"),
    ])
    def test_q_types_preserved(
        self, sentence: str, q_type: str
    ) -> None:
        parses = parse_text(sentence)
        matching = [
            p for p in parses if p[1].feats.get("Q_TYPE") == q_type
        ]
        assert len(matching) >= 1


class TestEarlierPhaseBaselinePreserved:
    """Phase 4 / 5c control + Phase 5h declaratives unchanged."""

    @pytest.mark.parametrize("sentence", [
        "Maganda ang bata.",
        "Kumain ang aso ng isda.",
        "Hindi maganda ang bata.",
        "Gusto kong kumain.",
        "Hindi ko gustong kumain.",
        "Mas matalino siya.",
        "Pinakamaganda ang bahay.",
    ])
    def test_baseline_declaratives(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        for _ct, fs, _astr, _diags in parses:
            # No phantom COMP_TYPE on these.
            assert fs.feats.get("COMP_TYPE") is None
            comp = fs.feats.get("COMP")
            if comp is not None:
                # If any pre-existing COMP appears, it shouldn't
                # be an INTERROG one from this commit.
                assert comp.feats.get("COMP_TYPE") != "INTERROG"
