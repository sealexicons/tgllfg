"""Phase 8.Y: ay-inverted N-pivot + Si-NP-pivot two-NP equational.

Closes two near-misses surfaced during Phase 8.X probing
(see ``docs/analysis-choices.md`` "Phase 8.X" entry, "Out-of-
scope follow-ons surfaced"). Per the anti-deferral guidance,
these were promoted to 8.Y rather than left deferred. Adds two
new clausal rules in ``cfg/clause.py``:

    S → NP[CASE=NOM] PART[LINK=AY] N      (ay-inverted N-pivot)
        (↑ PRED)        = 'BE-N <SUBJ>'
        (↑ SUBJ)        = ↓1
        (↑ TOPIC)       = ↓1
        (↑ N_LEMMA)     = ↓3 LEMMA
        (↑ PREDICATIVE) = true
        ¬ (↓3 WH)

    S → NP[CASE=NOM] NP[CASE=NOM]         (Si-NP pivot two-NP)
        (↓1 MARKER) =c 'SI'
        (↑ PRED)        = 'BE-NP <SUBJ>'
        (↑ SUBJ)        = ↓2
        (↑ PRED-NP)     = ↓1
        (↑ PREDICATIVE) = true

Out of 8.Y scope (intentional; not in the audit zero-parse
list, kept as deferral until corpus pressure surfaces):

- ``Ito ay aklat ko.`` — ay-inverted N-pivot with possessor-
  modified N. The possessor rule binds at NP level
  (``NP[CASE=NOM] → NP[CASE=NOM] NP[CASE=GEN]``), so
  ``aklat ko`` is NP, not N. Widening the right daughter of
  the 8.Y Rule 1 from ``N`` to ``NP[CASE=NOM]`` would converge
  the rule with two-NP equational; a clean closure needs an
  N-level possessor rule, deferred.
- ``Ang lalaki ang doktor.`` — fully-general two-NP equational
  with ang-pivot. The Phase 5n.B N-pivot rule docstring
  explicitly defers this to corpus pressure; the Wave 3 audit
  did not surface it.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _be_n_parse(text: str) -> FStructure | None:
    parses = parse_text(text, n_best=10)
    for _ct, fs, _astr, _diags in parses:
        if fs.feats.get("PRED") == "BE-N <SUBJ>":
            return fs
    return None


def _be_np_parse(text: str) -> FStructure | None:
    parses = parse_text(text, n_best=10)
    for _ct, fs, _astr, _diags in parses:
        if fs.feats.get("PRED") == "BE-NP <SUBJ>":
            return fs
    return None


# === Rule 1: ay-inverted N-pivot =====================================


class TestAyInvertedNPivot:
    """``S → NP[CASE=NOM] PART[LINK=AY] N`` — the ay-inverted
    mirror of the Phase 5n.B Commit 2 N-pivot rule."""

    def test_ito_ay_aklat(self) -> None:
        """DEM subject + ay + bare-N predicate."""
        fs = _be_n_parse("Ito ay aklat.")
        assert fs is not None
        assert fs.feats.get("N_LEMMA") == "aklat"
        assert fs.feats.get("PREDICATIVE") is True

    def test_ako_ay_guro(self) -> None:
        """NOM-PRON subject + ay + bare-N predicate. Companion to
        the Phase 8.X PRON-pivot rule (which handles ``Ako ang
        guro.`` — pivot on the left); this handles the topicalized
        order."""
        fs = _be_n_parse("Ako ay guro.")
        assert fs is not None
        assert fs.feats.get("N_LEMMA") == "guro"

    def test_topic_lifts_to_subj(self) -> None:
        """The fronted NP is both SUBJ and TOPIC per ay-fronting
        topicalization semantics."""
        fs = _be_n_parse("Ito ay aklat.")
        assert fs is not None
        subj = fs.feats.get("SUBJ")
        topic = fs.feats.get("TOPIC")
        assert subj is not None
        assert topic is not None
        # SUBJ and TOPIC are the same f-structure node (both
        # reference ↓1) — verify via id equality.
        assert subj is topic

    @pytest.mark.parametrize("sentence,n_lemma", [
        ("Iyan ay aklat.",  "aklat"),
        ("Iyon ay bahay.",  "bahay"),
        ("Ito ay sapatos.", "sapatos"),
    ])
    def test_three_way_deixis_in_ay_inv(
        self, sentence: str, n_lemma: str
    ) -> None:
        """All three deictic DEMs work as the ay-fronted subject."""
        fs = _be_n_parse(sentence)
        assert fs is not None
        assert fs.feats.get("N_LEMMA") == n_lemma


# === Rule 2: Si-NP pivot two-NP equational ============================


class TestSiNpPivotTwoNpEquational:
    """``S → NP[CASE=NOM] NP[CASE=NOM]`` gated by
    ``(↓1 MARKER) =c 'SI'`` — si-marked proper-NP as predicate
    over a NOM-NP subject."""

    @pytest.mark.parametrize("sentence", [
        "Si Juan ito.",
        "Si Maria iyan.",
        "Si Pedro iyon.",
    ])
    def test_si_pivot_dem_subject(self, sentence: str) -> None:
        """Harvest-derived: Si-marked proper-NP pivot + DEM subject.
        This is the shape that surfaced in the Wave 3 audit (R&G
        Conversational ``Si Juan ito.``)."""
        fs = _be_np_parse(sentence)
        assert fs is not None
        assert fs.feats.get("PREDICATIVE") is True

    def test_si_pivot_ang_subject(self) -> None:
        """Si-marked proper-NP pivot + ang-NP subject. Generalizes
        the rule beyond the DEM-subject case surfaced in the audit."""
        fs = _be_np_parse("Si Juan ang doktor.")
        assert fs is not None
        assert fs.feats.get("PREDICATIVE") is True

    def test_pred_np_preserved(self) -> None:
        """The predicate NP rides on ``PRED-NP`` so consumers can
        access the proper-noun identity."""
        fs = _be_np_parse("Si Juan ito.")
        assert fs is not None
        pred_np = fs.feats.get("PRED-NP")
        assert pred_np is not None
        assert isinstance(pred_np, FStructure)
        # The fronted Si-NP's MARKER feat is preserved on PRED-NP.
        assert pred_np.feats.get("MARKER") == "SI"


# === Disambiguation: ang-pivot does not fire =========================


class TestAngPivotDoesNotFire:
    """The ``(↓1 MARKER) =c 'SI'`` constraint restricts Rule 2 to
    si-marked left daughters. ``Ang lalaki ang doktor.`` does not
    fire this rule (intentional — fully-general two-NP equational
    remains deferred per the Phase 5n.B docstring)."""

    def test_ang_pivot_ang_subject_still_fails(self) -> None:
        parses = parse_text("Ang lalaki ang doktor.")
        # No BE-NP parse should fire; the two-ang case is out of
        # scope.
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("PRED") != "BE-NP <SUBJ>"


# === Regression: existing rules unaffected ============================


class TestRegression:
    """The two 8.Y rules don't perturb the existing N-pivot,
    DEM-pivot (8.X Commit 1), PRON-pivot (8.X Commit 2), or
    ay-fronting rules."""

    def test_n_pivot_still_works(self) -> None:
        """``Aklat ito.`` — Phase 5n.B Commit 2."""
        parses = parse_text("Aklat ito.")
        n_parses = [
            p for p in parses
            if p[1].feats.get("PRED") == "BE-N <SUBJ>"
        ]
        assert len(n_parses) >= 1

    def test_dem_pivot_still_works(self) -> None:
        """``Ito ang aklat.`` — Phase 8.X Commit 1."""
        parses = parse_text("Ito ang aklat.")
        dem_parses = [
            p for p in parses
            if p[1].feats.get("PRED") == "BE-DEM <SUBJ>"
        ]
        assert len(dem_parses) >= 1

    def test_pron_pivot_still_works(self) -> None:
        """``Ako ang guro.`` — Phase 8.X Commit 2."""
        parses = parse_text("Ako ang guro.")
        pron_parses = [
            p for p in parses
            if p[1].feats.get("PRED") == "BE-PRON <SUBJ>"
        ]
        assert len(pron_parses) >= 1

    def test_v_ay_fronting_still_works(self) -> None:
        """``Ako ay kumain.`` — Phase 4 §7.4."""
        parses = parse_text("Ako ay kumain.")
        # At least one parse exists; this is V-headed ay-fronting.
        assert len(parses) >= 1
        for _ct, fs, _astr, _diags in parses:
            # The V-ay-fronting rule's f-structure is V-headed, not
            # BE-N or BE-NP.
            assert fs.feats.get("PRED") not in {"BE-N <SUBJ>", "BE-NP <SUBJ>"}

    def test_adj_ay_fronting_still_works(self) -> None:
        """``Si Maria ay maganda.`` — Phase 5n.B Commit 3 (ADJ-pivot
        ay-fronting via S_GAP_PREDADJ)."""
        parses = parse_text("Si Maria ay maganda.")
        # At least one parse exists.
        assert len(parses) >= 1
        # No spurious BE-NP parse should fire from ``Si Maria``
        # (the Rule 2 SI-pivot constraint requires NP[CASE=NOM] on
        # the right; ``ay maganda`` is PART + ADJ, not NP).
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("PRED") != "BE-NP <SUBJ>"
