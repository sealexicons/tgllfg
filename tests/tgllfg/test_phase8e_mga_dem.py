"""Phase 8.E: ``mga`` + DEM PRON head.

Closes the audit-surfaced construction-class gap (10 corpus
candidates across 5342 exemplars) by adding one new rule to
``cfg/nominal.py``:

    NP[CASE=NOM] → DET[CASE=NOM] PART DET[CASE=NOM, DEM]

Parallel to the Phase 7a.A `mga` + N rule and the Phase 4 §7.8
standalone-DEM NP rule. Audit-driven scoping: corpus shows only
NOM-form candidates (`mga ito` / `mga iyan` / `mga iyon`); the
GEN/DAT variants (`ng mga nito`, `sa mga doon`, etc.) have 0
corpus pressure and are NOT in 8.E scope. Adding them would be
straightforward (parallel rules with ADP[CASE=GEN, DEM] /
ADP[CASE=DAT, DEM] daughters) — deferred until corpus pressure
emerges.

F-structure shape (mirrors Phase 4 §7.8 standalone-DEM + Phase
7a.A NUM=PL):

    (↑)            = ↓1            share with case-marker
    (↑ PRED)       = 'PRO'         synthesized DEM-PRED
    (↑ NUM)        = 'PL'          mga marks plural
    (↑ DEIXIS)     = ↓3 DEIXIS     lift DEM's deixis
    (↓2 PLURAL_MARKER) =c true     gate ↓2 to ``mga``

Direct corpus closures (verified by re-running
``/tmp/audit_mga_dem.py``):

- ``Kinakain niya ang mga ito.`` (wave1 ANG PAMILYA prose)
- ``[some] ang mga iyon`` (wave3 SO 1972 §X)

Other corpus candidates (`Itapon mo ang mga ito.`,
`Basahan mo ang mga iyan.`, etc.) remain zero-parse due to
OOV-verb / OCR-junk blockers — not within 8.E scope.
"""

from __future__ import annotations

import pytest


class TestPhase8eMgaDem:
    """The new rule produces clean parses on the canonical
    ``mga`` + DEM head construction across the three deixis
    values."""

    @pytest.mark.parametrize("sentence", [
        # Wave 1 audit target — clean ANG PAMILYA prose.
        "Kinakain niya ang mga ito.",
        # Constructed minimal-pair variants for each deixis.
        "Kinakain niya ang mga iyan.",
        "Kinakain niya ang mga iyon.",
    ])
    def test_sentence_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, (
            f"no parse for {sentence!r} after 8.E rule"
        )


class TestPhase8eFstructureShape:
    """The new rule sets the expected f-structure features on
    the matrix NP daughter: PRED='PRO', NUM='PL', DEIXIS=lifted."""

    def test_pred_pro_num_pl_deixis_prox(self) -> None:
        """``Kinakain niya ang mga ito.`` — OBJ NP has
        PRED='PRO', NUM='PL', DEIXIS='PROX'."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Kinakain niya ang mga ito.", n_best=3
        )
        assert len(parses) >= 1
        _, f, _, _ = parses[0]
        # SUBJ of OF verb is the OBJ semantically; the `ang mga
        # ito` NP fills SUBJ in OF voice. Walk to find the NP
        # with our expected features.
        subj = f.feats.get("SUBJ")
        assert subj is not None, "SUBJ not set"
        subj_feats = (
            subj.feats if hasattr(subj, "feats") else {}
        )
        assert subj_feats.get("PRED") == "PRO", (
            f"SUBJ.PRED={subj_feats.get('PRED')!r}, expected 'PRO'"
        )
        assert subj_feats.get("NUM") == "PL", (
            f"SUBJ.NUM={subj_feats.get('NUM')!r}, expected 'PL'"
        )
        assert subj_feats.get("DEIXIS") == "PROX", (
            f"SUBJ.DEIXIS={subj_feats.get('DEIXIS')!r}, "
            f"expected 'PROX'"
        )

    @pytest.mark.parametrize("dem,expected_deixis", [
        ("ito", "PROX"),
        ("iyan", "MED"),
        ("iyon", "DIST"),
    ])
    def test_deixis_lifts_correctly(
        self, dem: str, expected_deixis: str
    ) -> None:
        """The three NOM DEMs have distinct DEIXIS values
        (PROX / MED / DIST); the new rule lifts the correct one
        onto the matrix NP."""
        from tgllfg.core.pipeline import parse_text
        sentence = f"Kinakain niya ang mga {dem}."
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1
        _, f, _, _ = parses[0]
        subj = f.feats.get("SUBJ")
        assert subj is not None
        subj_feats = getattr(subj, "feats", {})
        assert subj_feats.get("DEIXIS") == expected_deixis, (
            f"{dem!r}: DEIXIS={subj_feats.get('DEIXIS')!r}, "
            f"expected {expected_deixis!r}"
        )


class TestPhase8eExistingPathsStillWork:
    """Non-regression: the Phase 7a.A ``mga`` + N rule and the
    Phase 4 §7.8 standalone-DEM rule still fire on their canonical
    inputs."""

    def test_mga_plus_n_unchanged(self) -> None:
        """Phase 7a.A: ``ang mga aklat`` "the books"."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Kinakain niya ang mga aklat.", n_best=3
        )
        assert len(parses) >= 1, "Phase 7a.A mga+N regressed"

    def test_standalone_dem_unchanged(self) -> None:
        """Phase 4 §7.8: bare DEM as NP."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Kinakain niya ito.", n_best=3)
        assert len(parses) >= 1, "Phase 4 §7.8 standalone-DEM regressed"


class TestPhase8eOutOfScope:
    """GEN/DAT variants (``ng mga nito``, ``sa mga doon``, etc.)
    have 0 corpus pressure (per the audit-mga-dem.py probe) and
    are NOT in 8.E scope. Pinned for visible signal if a future
    sub-PR adds them — but pinned here as a marker rather than as
    a queued-follow-on because the corpus-pressure-zero result
    means no scheduled work is justified."""

    @pytest.mark.parametrize("sentence", [
        # GEN variant: "Gusto niya ng mga nito" — not in corpus
        # and not a high-frequency construction. The Phase 4
        # standalone-DEM rule handles ``nito`` alone fine;
        # adding ``mga nito`` requires a parallel GEN rule.
        "Gusto niya ng mga nito.",
        # DAT variant: "Pumunta siya sa mga doon" — not in
        # corpus; analogous gap.
        "Pumunta siya sa mga doon.",
    ])
    def test_gen_dat_mga_dem_still_fails(
        self, sentence: str
    ) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) == 0, (
            f"GEN/DAT mga+DEM unexpectedly parses on {sentence!r} "
            f"— flip this pin if a future sub-PR added the variant."
        )
