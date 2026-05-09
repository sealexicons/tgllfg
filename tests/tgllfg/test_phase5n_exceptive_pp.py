"""Phase 5n.A Commit 18 — bukod sa / maliban sa exceptive PP (§18 L80).

Adds two new PREP entries (``bukod`` / ``maliban``) with
``PREP_TYPE: EXCEPTIVE``. The existing ``PP → PREP NP[CASE=DAT]``
rule (Phase 5e Commit 3) composes them into PPs unchanged. A new
clause-final attachment rule in cfg/discourse.py admits the
EXCEPTIVE PP as an ADJUNCT member of the matrix S — parallel to
the Phase 5f Commit 5 TIME_FRAME PP attachment but gated on
``PREP_TYPE=EXCEPTIVE`` to keep the other Phase 5e PREPs
(BENEFICIARY / TOPIC / SOURCE / REASON) restricted to ay-fronting
position.

``bukod`` is polysemous with the Phase 5m discourse-connective PART
``bukod`` (in ``bukod dito``); the PREP vs PART POS disambiguates
structurally — PREP fires only with a sa-NP complement.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === bukod sa exceptive ===================================================


class TestBukodSa:
    """``bukod sa NP`` "besides NP" composes as PP[PREP_TYPE=EXCEPTIVE]
    and attaches clause-finally as ADJUNCT."""

    @pytest.mark.parametrize("sentence", [
        "Kumain si Maria bukod sa Juan.",
        "Pumunta sila bukod sa bata.",
        "Bumili ako ng aklat bukod sa lapis.",
    ])
    def test_bukod_sa_clause_final(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === maliban sa exceptive =================================================


class TestMalibanSa:
    """``maliban sa NP`` "except NP" composes the same way."""

    @pytest.mark.parametrize("sentence", [
        "Kumain si Maria maliban sa Juan.",
        "Pumunta sila maliban sa bata.",
        "Bumili ako ng aklat maliban sa lapis.",
    ])
    def test_maliban_sa_clause_final(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === f-structure carries PREP_TYPE=EXCEPTIVE ==============================


class TestExceptiveFlag:
    """The PP's ``PREP_TYPE=EXCEPTIVE`` rides into the matrix's
    ADJUNCT set so downstream consumers can detect the construction."""

    def test_bukod_sa_carries_exceptive(self) -> None:
        parses = parse_text("Kumain si Maria bukod sa Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        adjunct = fs.feats.get("ADJUNCT")
        assert adjunct is not None
        adj_pp = next(iter(adjunct))
        assert adj_pp.feats.get("PREP_TYPE") == "EXCEPTIVE"


# === bukod polysemy regression ============================================


class TestBukodPolysemyRegression:
    """``bukod`` is polysemous: PART (Phase 5m discourse connective
    in ``bukod dito``) and PREP (Phase 5n.A Commit 18). Both must
    continue to fire in their respective contexts."""

    def test_bukod_dito_discourse_connective(self) -> None:
        # Phase 5m Commit 11 ``bukod dito`` connective.
        parses = parse_text("Bukod dito kumain si Maria.")
        assert len(parses) >= 1

    def test_bukod_sa_exceptive(self) -> None:
        # Phase 5n.A Commit 18 ``bukod sa`` exceptive.
        parses = parse_text("Kumain si Maria bukod sa Juan.")
        assert len(parses) >= 1


# === Existing PREP regression =============================================


class TestExistingPrepRegression:
    """The Phase 5e Commit 3 PREPs (para / tungkol / mula / dahil)
    continue to compose into PPs and ay-front. The new EXCEPTIVE
    rule doesn't admit them clause-finally (per the scoped lift)."""

    def test_para_sa_ay_fronted(self) -> None:
        parses = parse_text("Para sa bata ay bumili ako ng aklat.")
        assert len(parses) >= 1

    def test_tungkol_sa_ay_fronted(self) -> None:
        parses = parse_text("Tungkol sa bata ay nagsalita siya.")
        assert len(parses) >= 1
