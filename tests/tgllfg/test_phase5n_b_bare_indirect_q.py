"""Phase 5n.B Commit 10: bare-form colloquial indirect-Q (§18 L53).

Closes §18.1 deferral L53. The colloquial Tagalog indirect-Q
drops ``ang`` from the canonical wh-cleft form (``Sino ang
kumain.``); the residue is a wh-PRON-as-SUBJ + bare-V
construction (``Sino kumain.``). New rule:

    S → PRON[WH=YES, CASE=NOM] V[VOICE=AV]
        (↑) = ↓2
        (↑ SUBJ) = ↓1
        (↑ Q_TYPE) = 'WH'
        (↑ WH_LEMMA) = ↓1 LEMMA
        (↓1 WH) =c 'YES'
        (↓2 VOICE) =c 'AV'
        ¬ (↓1 INDEF)

in ``cfg/clause.py``. The ``¬ (↓1 INDEF)`` constraint excludes
indefinite kahit-X PRONs (Phase 5m kahit-WH composition produces
PRON[INDEF=YES, WH=YES]) so ``Kahit sino kumain.`` continues to
0-parse — that surface is a Phase 5n.B Commit 20 deferral
(pre-V kahit-X SUBJ ay-fronted, L100).

Composes with the Phase 5i Commit 8 indirect-Q matrix wrap
(``Alam ko kung S[Q_TYPE=WH]``): the bare-form S produces
``Q_TYPE=WH`` on its f-structure, satisfying the
S_INTERROG_COMP rule's constraint, so embedded bare-form
composes seamlessly.
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


# === Standalone bare-form ===========================================


class TestStandaloneBareForm:
    """``Sino kumain.`` "Who ate?" — wh-PRON + bare V (no ang).
    Colloquial form attested across the wh-PRON inventory."""

    @pytest.mark.parametrize("sentence,wh_lemma,verb_pred", [
        ("Sino kumain.",     "sino", "EAT"),
        ("Ano kumain.",      "ano",  "EAT"),
        ("Alin kumain.",     "alin", "EAT"),
        ("Sino tumakbo.",    "sino", "TAKBO"),
        ("Sino pumunta.",    "sino", "PUNTA"),
    ])
    def test_bare_form_standalone(
        self, sentence: str, wh_lemma: str, verb_pred: str
    ) -> None:
        result = _wh_parse(sentence)
        assert result is not None, f"no wh parse for {sentence!r}"
        _ct, fs, _astr, _diags = result
        assert fs.feats.get("Q_TYPE") == "WH"
        assert fs.feats.get("WH_LEMMA") == wh_lemma
        assert (fs.feats.get("PRED") or "").startswith(verb_pred)


# === Embedded under KNOW-class verb =================================


class TestEmbeddedBareForm:
    """``Alam ko kung sino kumain.`` "I know who ate." — bare-form
    embedded in indirect-Q context. The Phase 5i Commit 8
    S_INTERROG_COMP rule fires on the bare-form S (which carries
    Q_TYPE=WH from the new rule)."""

    @pytest.mark.parametrize("sentence,wh_lemma", [
        ("Alam ko kung sino kumain.",   "sino"),
        ("Alam ko kung ano kumain.",    "ano"),
        ("Alam ko kung alin kumain.",   "alin"),
    ])
    def test_embedded_bare_form(
        self, sentence: str, wh_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        # Top parse should have KNOW PRED.
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith("KNOW")


# === Disambiguation: kahit-X excluded ================================


class TestKahitXExcluded:
    """The ``¬ (↓1 INDEF)`` constraint excludes kahit-X
    indefinite PRONs (Phase 5m kahit-WH composition produces
    PRON[INDEF=YES, WH=YES]). ``Kahit sino kumain.`` 0-parses;
    the canonical form is ``Kahit sino ay kumain.`` (Phase 5n.B
    Commit 20 deferral)."""

    def test_kahit_sino_kumain_zero_parse(self) -> None:
        parses = parse_text("Kahit sino kumain.")
        assert len(parses) == 0


# === Regression: existing wh-cleft (with ang) unchanged =============


class TestWhCleftUnchanged:
    """``Sino ang kumain?`` — full wh-cleft form continues to
    parse via the Phase 5i Commit 2 cleft rule."""

    def test_full_form_cleft(self) -> None:
        parses = parse_text("Sino ang kumain?")
        wh_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1
        _ct, fs, _astr, _diags = wh_parses[0]
        assert fs.feats.get("PRED") == "WH <SUBJ>"
        assert fs.feats.get("WH_LEMMA") == "sino"
