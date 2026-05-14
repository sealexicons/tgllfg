"""Phase 8.Z: generalize 8.Y Rule 2 to ang-pivot two-NP equational.

Drops the ``(↓1 MARKER) =c 'SI'`` gate that Phase 8.Y put on the
two-NP equational rule. The user verified ``Ang lalaki ang
doktor.`` "The man is the doctor." as the natural reading, so
the fully-general NP-pivot two-NP equational is closed here.

Adds ``¬ (↓1 WH)`` to the rule body to keep wh-PRON cleft
sentences (``Sino ang kumain?``) routed through the Phase 5i
Commit 2 wh-PRON cleft rule, avoiding a spurious BE-NP parse.

Pseudo-cleft (``Ang lalaki ang nagluto.``) remains zero-parsing
in this commit — the gap is the headless-RC ``ang nagluto`` not
wrapping to NP[CASE=NOM] under the current Phase 5e Commit 5
free-relative rule's gating. Out of 8.Z scope; tracked as
separate near-miss for future work.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _be_np_parse(text: str) -> FStructure | None:
    parses = parse_text(text, n_best=10)
    for _ct, fs, _astr, _diags in parses:
        if fs.feats.get("PRED") == "BE-NP <SUBJ>":
            return fs
    return None


# === Ang-pivot two-NP equational ====================================


class TestAngPivotEquational:
    """``S → NP[CASE=NOM] NP[CASE=NOM]`` ungated on the pivot's
    MARKER (still gated on ¬ WH). Covers user-verified
    ``Ang lalaki ang doktor.`` ("The man is the doctor.") and
    siblings."""

    @pytest.mark.parametrize("sentence", [
        "Ang lalaki ang doktor.",
        "Ang nanay ang guro.",
        "Ang tatay ang doktor.",
    ])
    def test_ang_pivot_ang_subject(self, sentence: str) -> None:
        fs = _be_np_parse(sentence)
        assert fs is not None, f"no BE-NP parse for {sentence!r}"
        assert fs.feats.get("PREDICATIVE") is True

    def test_pred_np_ang_marked(self) -> None:
        """The fronted ang-marked NP rides on PRED-NP and carries
        MARKER=ANG (consumer can inspect the pivot's case-marker
        category)."""
        fs = _be_np_parse("Ang lalaki ang doktor.")
        assert fs is not None
        pred_np = fs.feats.get("PRED-NP")
        assert isinstance(pred_np, FStructure)
        assert pred_np.feats.get("MARKER") == "ANG"


# === Regression: 8.Y Si-pivot still works =============================


class TestSiPivotRegression:
    """Phase 8.Y's si-marker cases continue to work after the gate
    is dropped (the new rule subsumes the SI-gated variant)."""

    def test_si_juan_ito(self) -> None:
        fs = _be_np_parse("Si Juan ito.")
        assert fs is not None
        pred_np = fs.feats.get("PRED-NP")
        assert isinstance(pred_np, FStructure)
        assert pred_np.feats.get("MARKER") == "SI"

    def test_si_juan_ang_doktor(self) -> None:
        fs = _be_np_parse("Si Juan ang doktor.")
        assert fs is not None


# === WH-cleft disambiguation ========================================


class TestWhCleftDisambiguation:
    """The new ``¬ (↓1 WH)`` gate on the generalized rule keeps
    wh-PRON cleft sentences (``Sino ang kumain?``) routed through
    the Phase 5i Commit 2 wh-PRON cleft. Without the gate, the
    new rule would fire on wh-PRONs (which wrap to NP[CASE=NOM]
    via the standalone-PRON NP rule) and produce a spurious
    BE-NP parse alongside the canonical wh-cleft parse."""

    @pytest.mark.parametrize("sentence", [
        "Sino ang kumain?",
        "Sino ang doktor?",
        "Ano ang kinain mo?",
        "Alin ang kinain mo?",
    ])
    def test_wh_cleft_no_be_np_parse(self, sentence: str) -> None:
        """Wh-cleft sentences must NOT produce a BE-NP parse — the
        ``¬ (↓1 WH)`` gate keeps them routed through the Phase 5i
        wh-PRON cleft. Other parses (e.g., the Phase 5i Q polysemy
        for ``Alin``) are unaffected; only the spurious BE-NP path
        is blocked."""
        parses = parse_text(sentence)
        assert len(parses) >= 1
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("PRED") != "BE-NP <SUBJ>", (
                f"spurious BE-NP parse for wh-cleft {sentence!r}"
            )


# === Out-of-scope: pseudo-cleft remains zero-parse ==================


class TestPseudoCleftOutOfScope:
    """``Ang lalaki ang nagluto.`` "The man is the one who
    cooked." (pseudo-cleft equational reading) remains zero-
    parsing. The blocker is the headless-RC ``ang nagluto`` not
    wrapping to NP[CASE=NOM] under the current Phase 5e Commit 5
    free-relative rule's gating — a separate gap, not in 8.Z
    scope. This test pins the current behavior so 8.Z's intent
    is unambiguous; flip to pass when the headless-RC gap is
    closed."""

    def test_pseudo_cleft_still_fails(self) -> None:
        parses = parse_text("Ang lalaki ang nagluto.")
        assert len(parses) == 0
