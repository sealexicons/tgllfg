"""Phase 5n.B Commit 8: in-situ Q_TYPE matrix lift (§18 L50).

Closes §18.1 deferral L50 (in-situ wh-PRON inside an OBJ /
ADJUNCT NP doesn't surface ``Q_TYPE=WH`` on the matrix). Adds
a post-pass over the f-structure that walks the matrix's GFs
recursively and writes ``Q_TYPE=WH`` on the matrix when any
embedded element carries ``WH=YES``.

Idempotent: matrices already carrying ``Q_TYPE`` (wh-cleft,
wh-fronting, tag-Q, yes/no-Q, Phase 5n.B Commit 7 Alt-Q) are
skipped — the grammar-rule lift is the canonical analysis;
the post-pass only fills the gap for in-situ wh.

Filters out wh inside relative-clause bodies (sub-f-structures
with REL-PRO defined) — the wh-PRON binding inside an RC is
the relative-head's binding, not a matrix wh-Q.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


def _q_wh_parse(text: str):
    parses = parse_text(text, n_best=10)
    for p in parses:
        if p[1].feats.get("Q_TYPE") == "WH":
            return p
    return None


# === In-situ wh in OBJ / GEN-NP ======================================


class TestInSituObj:
    """``Kumain ka ng ano?`` "You ate what?" — in-situ wh-PRON
    inside the GEN-marked OBJ NP."""

    def test_in_situ_obj_wh(self) -> None:
        result = _q_wh_parse("Kumain ka ng ano?")
        assert result is not None
        _ct, fs, _astr, _diags = result
        assert fs.feats.get("Q_TYPE") == "WH"


# === In-situ wh in ADJUNCT (DAT-NP) ==================================


class TestInSituAdjunct:
    """``Pumunta ka kanino?`` "You went to whom?" — in-situ wh-PRON
    sits in the matrix's ADJUNCT set."""

    @pytest.mark.parametrize("sentence", [
        "Pumunta ka kanino?",
        "Sumulat ka kanino?",
        "Kumain ka kanino?",
    ])
    def test_in_situ_adjunct_wh(self, sentence: str) -> None:
        result = _q_wh_parse(sentence)
        assert result is not None
        _ct, fs, _astr, _diags = result
        assert fs.feats.get("Q_TYPE") == "WH"


# === In-situ wh-PRON in DAT-NP arguments =============================


class TestInSituDatPrep:
    """``Sumulat ka kay kanino?`` "You wrote to whom?" — in-situ
    wh-PRON inside an explicit DAT-NP via the Phase 5i Commit 3
    NP[CASE=DAT] → ADP[CASE=DAT] PRON[WH=YES] shell."""

    def test_in_situ_kay_kanino(self) -> None:
        result = _q_wh_parse("Sumulat ka kay kanino?")
        assert result is not None
        _ct, fs, _astr, _diags = result
        assert fs.feats.get("Q_TYPE") == "WH"


# === Idempotency: wh-cleft already-marked matrices unaffected =========


class TestIdempotentOnAlreadyMarked:
    """Matrices with ``Q_TYPE`` already set (wh-cleft, wh-fronting,
    tag-Q, yes/no-Q, Alt-Q) are skipped — the post-pass doesn't
    overwrite or duplicate."""

    def test_wh_cleft_unchanged(self) -> None:
        # ``Sino ang kumain?`` — wh-cleft (grammar rule sets Q_TYPE
        # = WH). Post-pass should not run on this matrix.
        parses = parse_text("Sino ang kumain?")
        wh = [p for p in parses if p[1].feats.get("Q_TYPE") == "WH"]
        assert len(wh) >= 1
        # WH_LEMMA must be present (set by the wh-cleft rule).
        _ct, fs, _astr, _diags = wh[0]
        assert fs.feats.get("WH_LEMMA") == "sino"

    def test_yes_no_q_unchanged(self) -> None:
        # ``Kumain ka ba?`` — yes/no Q via Phase 5i Commit 5 ba-rule.
        # Q_TYPE=YES_NO; post-pass should not overwrite.
        parses = parse_text("Kumain ka ba?")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("Q_TYPE") == "YES_NO"


# === Declarative without wh: Q_TYPE remains absent ===================


class TestDeclarativeUnaffected:
    """Declarative sentences with no wh-marked element receive no
    Q_TYPE — the post-pass only writes on matrices with embedded
    WH=YES."""

    @pytest.mark.parametrize("sentence", [
        "Kumain ang bata.",
        "Kumain si Maria ng isda.",
        "Maganda ang bata.",
        "Doktor si Maria.",
    ])
    def test_no_q_type_for_declarative(self, sentence: str) -> None:
        parses = parse_text(sentence)
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("Q_TYPE") is None
