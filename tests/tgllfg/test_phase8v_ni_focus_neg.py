"""Phase 8.V: ``Ni X ay hindi Y`` focus-negation.

Audit-named construction (S&O 1972 §7.20). A NEG-marked
AV-V-headed clause admits a SUBJ-pivot fronted with a leading
``Ni`` "not even" focus particle:

    Ni si Juan ay hindi nakapunta.
        "Not even Juan went (anywhere)."
    Ni si Maria ay hindi umalis.
        "Not even Maria left."

New rule in ``cfg/extraction.py`` adjacent to the Phase 4 §7.4
SUBJ-ay-front rule:

    S → PART[FOCUS_NEG=true]  NP[CASE=NOM]  PART[LINK=AY]  S_GAP
      (↑) = ↓4
      (↑ TOPIC) = ↓2
      (↑ FOCUS_NEG) = true
      (↓4 REL-PRO) = ↓2
      (↓4 REL-PRO) =c (↓4 SUBJ)
      (↓4 POLARITY) =c 'NEG'
      (↓1 FOCUS_NEG) =c true

The ``ni`` particle gets a second entry in ``particles.yaml``
(distinct from the existing GEN proper-name marker ``ni``) with
``FOCUS_NEG=true``; the two readings disambiguate by the
following daughter shape.

New binary feat ``FOCUS_NEG`` (BINARY_FEATS 54 → 55).
"""

from __future__ import annotations

import pytest


class TestPhase8vNiSubjFocus:
    """Single Ni-NP[NOM] ay-fronting + hindi-VP — the canonical
    SUBJ-focus shape."""

    @pytest.mark.parametrize("sentence,topic_lemma", [
        ("Ni si Juan ay hindi kumain.", "juan"),
        ("Ni si Maria ay hindi kumain.", "maria"),
        ("Ni si Maria ay hindi umalis.", "maria"),
        # AV-V with GEN-OBJ
        ("Ni si Juan ay hindi kumain ng tinapay.", "juan"),
        # ABIL form
        ("Ni si Juan ay hindi nakapunta.", "juan"),
        # ABIL + locative-DAT adjunct (S&O 1972 page 640 /
        # sent-1260 audit-hit verbatim — closed by the new
        # S_GAP → V[AV] NP[DAT] frame in cfg/extraction.py)
        ("Ni si Juan ay hindi nakapunta doon.", "juan"),
        ("Ni si Juan ay hindi nakapunta sa bahay.", "juan"),
        # DEM-PRON Ni-focus (standalone DEM is NOM-NP via
        # Phase 5n.B.6 standalone-DEM rule)
        ("Ni ito ay hindi kumain.", None),
        ("Ni iyan ay hindi kumain.", None),
    ])
    def test_ni_subj_focus_parses(
        self, sentence: str, topic_lemma: str | None,
    ) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse for {sentence!r}"
        f = parses[0][1]
        assert f.feats.get("FOCUS_NEG") is True
        assert str(f.feats.get("POLARITY")) == "NEG"
        topic = f.feats.get("TOPIC")
        assert topic is not None
        # NOUN heads carry LEMMA; DEM-PRON heads carry
        # PRED='PRO' via the Phase 5n.B.6 standalone-DEM rule
        if topic_lemma is not None:
            assert str(topic.feats.get("LEMMA")) == topic_lemma


class TestPhase8vNegGate:
    """The rule constrains on the inner clause carrying
    POLARITY=NEG. Affirmative inner clause + Ni-focus is blocked
    (Ni "not even" semantically requires negation)."""

    def test_affirmative_inner_blocks_ni(self) -> None:
        from tgllfg.core.pipeline import parse_text
        # No hindi — Ni-focus should not fire
        parses = parse_text("Ni si Juan ay kumain.", n_best=2)
        # No parse should carry FOCUS_NEG=true
        for _ct, f, _astr, _diags in parses:
            assert f.feats.get("FOCUS_NEG") is not True, (
                "affirmative inner admitted a FOCUS_NEG matrix — "
                "POLARITY=NEG gate failed"
            )


class TestPhase8vNiVsGenNi:
    """The new ``ni`` PART[FOCUS_NEG=true] is structurally
    disjoint from the existing GEN proper-name marker ``ni``.
    The two readings disambiguate by the following daughter
    shape: GEN admits a bare proper-name NOUN ("ni Juan" in
    OBL-AGENT position); FOCUS_NEG admits a full NP + ay +
    S_GAP."""

    def test_gen_ni_still_works(self) -> None:
        """``Kumain ng tinapay ni Juan ang bata.`` — ni-NP as
        GEN-AGENT (regression). Note: this exercises the
        existing GEN ni entry, not the new FOCUS_NEG ni."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Kumain ng tinapay ni Juan ang bata.", n_best=2)
        assert len(parses) >= 1, "GEN ni regression"


class TestPhase8vVDatNomFreeOrder:
    """The new ``S → V[VOICE=AV] NP[CASE=DAT] NP[CASE=NOM]`` rule
    and the parallel ``S_GAP → V[VOICE=AV] NP[CASE=DAT]`` rule
    close the V-DAT-SUBJ free-word-order gap that blocked the
    8.V audit hit (anti-deferral discipline — the Phase 5e C3
    deferral on non-fronted AdvP/PP placement is not explicitly
    in the Phase 8 plan, so the gap is closed in-PR alongside
    the Ni-focus construction it blocks)."""

    @pytest.mark.parametrize("sentence", [
        # Matrix V[AV] DAT-NP SUBJ-NOM-pivot (free word order)
        "Pumunta sa bahay si Juan.",
        "Pumunta doon si Juan.",
        "Kumain sa bahay si Juan.",
        "Hindi nakapunta doon si Juan.",
        "Hindi nakapunta sa bahay si Juan.",
    ])
    def test_v_dat_nom_free_order(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"V-DAT-NOM order failed: {sentence!r}"

    @pytest.mark.parametrize("sentence", [
        # Existing V[AV] SUBJ-NOM DAT order — unchanged
        "Pumunta si Juan sa bahay.",
        "Pumunta si Juan doon.",
        "Hindi nakapunta si Juan.",
    ])
    def test_v_nom_dat_unchanged(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, (
            f"V-NOM-DAT regression: {sentence!r}"
        )


class TestPhase8vBinaryFeat:
    """``FOCUS_NEG`` is registered in BINARY_FEATS so the
    grammar compiler accepts ``[FOCUS_NEG]`` / ``[FOCUS_NEG=true]``
    shorthand in category patterns."""

    def test_focus_neg_in_binary_feats(self) -> None:
        from tgllfg.core.feats import BINARY_FEATS
        assert "FOCUS_NEG" in BINARY_FEATS


class TestPhase8vOutOfScope:
    """Audit candidates that remain zero-parse after 8.V — pinned
    as separate construction classes beyond the SUBJ-focus scope
    closed here. Each pin flips when the relevant follow-on
    sub-PR lands."""

    def test_non_subj_ni_focus_closed_in_9r(self) -> None:
        """``Ni ito ay hindi umiinom si Rosa.`` (S&O 1972 page
        603 / sent-1154) — DEM-PRON Ni-focus on a NON-SUBJ
        position with an in-clause NOM-pivot ``si Rosa``.

        Phase 9.R B3.E closes this via three new rules in
        cfg/extraction.py parallel to the 8.V SUBJ-focus rule
        but with non-SUBJ gap categories (S_GAP_OBJ /
        S_GAP_OBJ_AGENT / S_GAP_OBL). The 8.V SUBJ-focus and
        9.R non-SUBJ-focus rules are mutually exclusive on the
        inner-clause shape: 8.V requires S_GAP (SUBJ missing,
        no in-clause SUBJ); 9.R requires one of the non-SUBJ
        gap categories (the relevant non-SUBJ slot missing,
        in-clause SUBJ present)."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Ni ito ay hindi kumain si Maria.", n_best=2,
        )
        assert len(parses) >= 1, (
            "Non-SUBJ Ni-focus should parse post-9.R"
        )

    def test_paired_ni_correlative(self) -> None:
        """``Ni si Juan ni si Ben ay hindi bibilhin iyan.``
        (S&O 1972 page 604 / sent-1159) — paired Ni X ni Y
        correlative coordination of foci. Pin; flip when a
        paired-Ni sub-PR lands."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Ni si Juan ni si Maria ay hindi kumain.", n_best=2,
        )
        assert len(parses) == 0, (
            "Paired-Ni correlative closed — flip if a paired-Ni "
            "sub-PR landed."
        )

    def test_ni_hindi_no_ay(self) -> None:
        """``Ni hindi ko napapansin.`` (R&G Intermediate
        sent-1828) — ``Ni hindi V`` intensifier-negation
        (without ``ay``) is a DISTINCT construction from the
        ``Ni X ay hindi Y`` focus-negation closed here.
        Different scope; pinned for a future sub-PR."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Ni hindi ko napapansin.", n_best=2)
        assert len(parses) == 0, (
            "Ni-hindi (no ay) closed — flip if the intensifier-"
            "negation sub-PR landed."
        )
