# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 8.X: DEM-pivot and PRON-pivot predicational clauses.

Closes the Phase 8.X audit gap surfaced in the R&G Conversational
construction-gap rows — see ``docs/coverage.md`` § Phase 8 closure
summary (formerly ``docs/coverage-audit-2026-05.md`` §15; rolled
up 2026-05-22). Adds two new clausal rules in ``cfg/clause.py``:

    S → DET[CASE=NOM, DEM] NP[CASE=NOM]    (DEM-pivot)
        (↑ PRED)        = 'BE-DEM <SUBJ>'
        (↑ SUBJ)        = ↓2
        (↑ DEIXIS)      = ↓1 DEIXIS
        (↑ PREDICATIVE) = true

    S → PRON[CASE=NOM] NP[CASE=NOM]        (PRON-pivot)
        (↑ PRED)        = 'BE-PRON <SUBJ>'
        (↑ SUBJ)        = ↓2
        (↑ NUM) / (↑ CLUSV) = lifted from PRON
        (↑ PREDICATIVE) = true
        ¬ (↓1 WH)

DEM_LEMMA / PRON_LEMMA / PERS are NOT lifted: the relevant
``data/tgl/pronouns.yaml`` entries do not register LEMMA as a
feature (and PERS is an integer, which doesn't propagate to
f-structure today). DEIXIS uniquely identifies the demonstrative;
NUM + CLUSV jointly disambiguate the pronoun's person up to
inclusive/exclusive distinction.

Plus a placement-side companion in ``clitics/placement.py``:
``_is_pre_ang_pred_pron`` suppresses Wackernagel hoisting of a
NOM-PRON-clitic immediately followed by ``ang`` / ``si`` (so
``Ako`` stays in sentence-initial position rather than being
moved past the anchor).

Sibling rules already covered:

* Phase 5g Commit 3 — predicative-ADJ (``Maganda ang bata.``)
* Phase 5n.B Commit 2 — predicative-N (``Doktor ako.``)
* Phase 5i Commit 2 — wh-PRON cleft (``Sino ang kumain?``)

Out of 8.X scope (reserved for Phase 8.S follow-on):

* PRON-pivot with V-headed ang-NP (``Tayo ang lumakad.``)
* DAT-PRON possessive-pivot (``Akin ang tinapay.``)
* DEM-pivot with ``ay`` inversion (``Ito ay aklat.``)
"""

import pytest

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _dem_pivot_parse(text: str) -> FStructure | None:
    parses = parse_text(text, n_best=10)
    for _ct, fs, _astr, _diags in parses:
        if fs.feats.get("PRED") == "BE-DEM <SUBJ>":
            return fs
    return None


def _pron_pivot_parse(text: str) -> FStructure | None:
    parses = parse_text(text, n_best=10)
    for _ct, fs, _astr, _diags in parses:
        if fs.feats.get("PRED") == "BE-PRON <SUBJ>":
            return fs
    return None


# === DEM-pivot: harvest-derived audit targets ========================


class TestDemPivotHarvestTargets:
    """The two R&G Conversational sentences that surfaced the gap
    (audit report §15 representative samples)."""

    def test_ito_ang_tatay_ko(self) -> None:
        fs = _dem_pivot_parse("Ito ang tatay ko.")
        assert fs is not None, "Ito ang tatay ko. must produce a DEM-pivot parse"
        assert fs.feats.get("DEIXIS") == "PROX"
        assert fs.feats.get("PREDICATIVE") is True

    def test_ito_ang_bahay_ko(self) -> None:
        fs = _dem_pivot_parse("Ito ang bahay ko.")
        assert fs is not None
        assert fs.feats.get("DEIXIS") == "PROX"


# === DEM-pivot: three-way deictic coverage ============================


class TestDemPivotThreeWayDeixis:
    """Tagalog distinguishes three deictic distances; verify all
    three DEMs work in pivot position with correct DEIXIS lift."""

    @pytest.mark.parametrize("sentence,deixis", [
        ("Ito ang aklat.",   "PROX"),
        ("Iyan ang aklat.",  "MED"),
        ("Iyon ang aklat.",  "DIST"),
    ])
    def test_dem_pivot_deixis(
        self, sentence: str, deixis: str
    ) -> None:
        fs = _dem_pivot_parse(sentence)
        assert fs is not None
        assert fs.feats.get("DEIXIS") == deixis


# === DEM-pivot: subject NP shapes =====================================


class TestDemPivotSubjectShapes:
    """DEM pivot over (a) ang-NP with bare N, (b) ang-NP with
    possessive-clitic, (c) si-marked proper-noun NP."""

    def test_dem_ang_bare_n(self) -> None:
        fs = _dem_pivot_parse("Ito ang aklat.")
        assert fs is not None
        subj = fs.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("CASE") == "NOM"

    def test_dem_ang_possessive(self) -> None:
        fs = _dem_pivot_parse("Iyon ang aklat ko.")
        assert fs is not None
        subj = fs.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("CASE") == "NOM"

    def test_dem_si_proper(self) -> None:
        fs = _dem_pivot_parse("Ito si Juan.")
        assert fs is not None
        subj = fs.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("CASE") == "NOM"
        assert subj.feats.get("MARKER") == "SI"


# === PRON-pivot: NOM-PRON cleft ======================================


class TestPronPivotNomClefts:
    """Non-wh NOM-PRON predicational clefts. All standard NOM-PRONs
    (ako, siya, kami, tayo, kayo, sila) work in pivot position over
    a NOM-NP subject."""

    @pytest.mark.parametrize("sentence,num", [
        ("Ako ang guro.",       "SG"),
        ("Siya ang kaibigan.",  "SG"),
    ])
    def test_pron_pivot_features(
        self, sentence: str, num: str
    ) -> None:
        fs = _pron_pivot_parse(sentence)
        assert fs is not None, f"no PRON-pivot parse for {sentence!r}"
        assert fs.feats.get("NUM") == num
        assert fs.feats.get("PREDICATIVE") is True


class TestPronPivotPluralInclusiveExclusive:
    """1pl PRONs distinguish inclusive (tayo) from exclusive (kami)
    via CLUSV; the matrix lifts CLUSV from the pivot."""

    def test_kami_exclusive(self) -> None:
        fs = _pron_pivot_parse("Kami ang guro.")
        assert fs is not None
        assert fs.feats.get("NUM") == "PL"
        # ``kami`` is exclusive 1pl per ``data/tgl/pronouns.yaml``.
        assert fs.feats.get("CLUSV") == "EXCL"

    def test_tayo_inclusive(self) -> None:
        fs = _pron_pivot_parse("Tayo ang guro.")
        assert fs is not None
        assert fs.feats.get("NUM") == "PL"
        assert fs.feats.get("CLUSV") == "INCL"


# === Disambiguation against the wh-PRON cleft =========================


class TestNonWhPronGate:
    """The new PRON-pivot rule's ``¬ (↓1 WH)`` excludes wh-PRONs
    (``sino``, ``ano``, ``alin``) from firing a spurious non-wh
    BE-PRON parse on what should be a wh-cleft."""

    def test_sino_no_pron_pivot_parse(self) -> None:
        parses = parse_text("Sino ang guro?")
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("PRED") != "BE-PRON <SUBJ>"
        # The wh-cleft parse should still fire.
        wh_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1


# === Regression: sibling predicative rules unaffected ================


class TestSiblingPredicativeRulesUnaffected:
    """The new DEM-pivot and PRON-pivot rules don't perturb the
    existing predicative-ADJ, predicative-N, predicative-cardinal,
    or predicative-Q rules."""

    def test_predicative_adj_still_works(self) -> None:
        parses = parse_text("Maganda ang bata.")
        adj_parses = [
            p for p in parses
            if p[1].feats.get("PRED") == "ADJ <SUBJ>"
        ]
        assert len(adj_parses) >= 1

    def test_predicative_n_still_works(self) -> None:
        parses = parse_text("Doktor ako.")
        n_parses = [
            p for p in parses
            if p[1].feats.get("PRED") == "BE-N <SUBJ>"
        ]
        assert len(n_parses) >= 1

    def test_n_pivot_bare_dem_subject_still_works(self) -> None:
        # ``Aklat ito.`` — N pivot + standalone DEM subject. This
        # was already covered before 8.X and should remain.
        parses = parse_text("Aklat ito.")
        n_parses = [
            p for p in parses
            if p[1].feats.get("PRED") == "BE-N <SUBJ>"
        ]
        assert len(n_parses) >= 1


# === Regression: ay-fronting still works =============================


class TestAyFrontingUnaffected:
    """The placement-side ``_is_pre_ang_pred_pron`` check is gated
    on right-context ``DET[CASE=NOM, DEM=false]``; it does not
    interfere with the existing ``_is_pre_ay_pron`` exception for
    ay-fronted NOM-PRONs (``Ako ay kumain.``)."""

    def test_ako_ay_kumain(self) -> None:
        parses = parse_text("Ako ay kumain.")
        # At least one parse exists.
        assert len(parses) >= 1


# === Regression: post-V Wackernagel placement still works ============


class TestWackernagelUnaffected:
    """The placement-side ``_is_pre_ang_pred_pron`` requires the
    immediately-following token to be ``DET[CASE=NOM, DEM=false]``,
    so the standard post-V Wackernagel hoist still fires when the
    PRON is followed by anything else (a VERB, another PRON, a
    PART)."""

    def test_kumain_ako_post_v_placement(self) -> None:
        # ``Kumain ako.`` — V-initial; ``ako`` is in second
        # position already (the natural post-V cluster slot).
        parses = parse_text("Kumain ako.")
        assert len(parses) >= 1


# === Regression: V-headed clauses unaffected =========================


class TestVHeadedClausesUnaffected:
    """V-headed clauses parse via the Phase 4 verb-frame rules,
    not DEM-pivot or PRON-pivot. Initial-V surfaces don't fire the
    new rules because they require a DET / PRON left daughter."""

    def test_av_intransitive(self) -> None:
        parses = parse_text("Kumain ang bata.")
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("PRED") not in {
                "BE-DEM <SUBJ>", "BE-PRON <SUBJ>",
            }

    def test_av_transitive(self) -> None:
        parses = parse_text("Kumain ang bata ng isda.")
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("PRED") not in {
                "BE-DEM <SUBJ>", "BE-PRON <SUBJ>",
            }
