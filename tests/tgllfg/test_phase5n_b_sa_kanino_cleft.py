"""Phase 5n.B Commit 9: sa-DAT NP cleft (§18 L51).

Closes §18.1 deferral L51 (``Sa kanino ang aklat?`` "Whose is
the book?" with explicit DAT marker) by adding a clausal rule

    S → NP[CASE=DAT, WH=YES] NP[CASE=NOM]
        (↑ PRED) = 'WH <SUBJ>'
        (↑ SUBJ) = ↓2
        (↑ Q_TYPE) = 'WH'
        (↑ WH_LEMMA) = ↓1 WH_LEMMA
        (↓1 WH) =c 'YES'
        (↓1 CASE) =c 'DAT'
        (↓1 PRED) =c 'WH-PRO'

in ``cfg/clause.py`` parallel to the Phase 5i Commit 9 (b)
bare-DAT-PRON cleft.

The ``(↓1 PRED) =c 'WH-PRO'`` constraint disambiguates the new
NP-shaped rule from the bare-PRON path: the Phase 5i Commit 3
explicit-DAT shell (``NP[CASE=DAT] → ADP[CASE=DAT]
PRON[WH=YES]``) sets ``PRED='WH-PRO'`` on the matrix NP,
whereas the Phase 4 §7.8 bare-PRON shell shares the PRON's
f-structure (no PRED). The bare-PRON cleft (Phase 5i Commit 9
(b)) remains the canonical path for ``Kanino ang aklat?``.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


def _wh_parse(text: str):
    parses = parse_text(text, n_best=10)
    for p in parses:
        if p[1].feats.get("Q_TYPE") == "WH":
            return p
    return None


# === Sa-kanino DAT-NP cleft ===========================================


class TestSaKaninoCleft:
    """``Sa kanino ang aklat?`` parses as a DAT-NP cleft via the
    new Phase 5n.B Commit 9 rule. ``WH_LEMMA='kanino'`` rides on
    the matrix from the inner NP[CASE=DAT, WH=YES]."""

    @pytest.mark.parametrize("sentence,subj_lemma", [
        ("Sa kanino ang aklat?",   "aklat"),
        ("Sa kanino ang aso?",     "aso"),
        ("Sa kanino ang bahay?",   "bahay"),
    ])
    def test_sa_kanino_cleft(
        self, sentence: str, subj_lemma: str
    ) -> None:
        result = _wh_parse(sentence)
        assert result is not None
        _ct, fs, _astr, _diags = result
        assert fs.feats.get("PRED") == "WH <SUBJ>"
        assert fs.feats.get("Q_TYPE") == "WH"
        assert fs.feats.get("WH_LEMMA") == "kanino"
        # Subj is the headless RC NP carrying the noun's lemma.
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma


# === Sa-sino DAT-marker cleft (NOM-by-default wh-PRON in DAT wrapper) ===


class TestSaSinoCleft:
    """``Sa sino ang aklat?`` — ``sino`` is lex'd as PRON[CASE=NOM,
    WH=YES] (HUMAN), but the Phase 5i Commit 3 ``NP[CASE=DAT] →
    ADP[CASE=DAT] PRON[WH=YES]`` shell admits any wh-PRON
    regardless of its inherent case (since the matrix CASE comes
    from the ADP wrapper). The new Phase 5n.B Commit 9 cleft
    fires the same way."""

    def test_sa_sino_cleft(self) -> None:
        result = _wh_parse("Sa sino ang aklat?")
        assert result is not None
        _ct, fs, _astr, _diags = result
        assert fs.feats.get("WH_LEMMA") == "sino"


# === Disambiguation: bare-PRON cleft path unchanged =================


class TestBareKaninoCleftUnchanged:
    """``Kanino ang aklat?`` continues to parse via the Phase 5i
    Commit 9 (b) PRON cleft only — the new NP-shaped cleft's
    ``(↓1 PRED) =c 'WH-PRO'`` constraint excludes the bare-PRON
    path (which lacks PRED on the wrapped NP)."""

    def test_bare_kanino_unique_parse(self) -> None:
        parses = parse_text("Kanino ang aklat?")
        wh_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) == 1
        _ct, fs, _astr, _diags = wh_parses[0]
        assert fs.feats.get("WH_LEMMA") == "kanino"
        # PRON daughter, not NP[CASE=DAT].
        assert _ct.children[0].label.startswith("PRON")
