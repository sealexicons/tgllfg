# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

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


class TestKahitXExcludedFromBareIndirectQ:
    """The ``¬ (↓1 INDEF)`` constraint on the Phase 5n.B C10
    bare-indirect-Q rule (``S → PRON[WH, NOM] V[AV]``) excludes
    kahit-X indefinite PRONs (Phase 5m kahit-WH composition
    produces ``PRON[INDEF=YES, WH=YES]``).

    **Phase 7a.F closure (2026-05-14):** ``Kahit sino kumain.``
    now parses via the new Phase 7a.F kahit-X no-ay colloquial
    rule (TOPIC-fronting with REGISTER=COLLOQUIAL), but NOT via
    the bare-indirect-Q rule (which would produce ``Q_TYPE=WH``).
    The exclusion this class pins is still active: kahit-X
    surfaces don't trigger the bare-indirect-Q wh-Q reading.
    """

    def test_kahit_sino_kumain_not_a_bare_indirect_q(self) -> None:
        parses = parse_text("Kahit sino kumain.")
        # Parse should exist (Phase 7a.F), and the surviving
        # parse must come from the Phase 7a.F TOPIC-fronting rule
        # (matrix has TOPIC bound to the kahit-X NP), NOT from
        # the Phase 5n.B C10 bare-indirect-Q rule (which would
        # bind SUBJ directly with no TOPIC).
        assert parses, (
            "Kahit sino kumain. should parse via Phase 7a.F "
            "no-ay colloquial rule"
        )
        # Every parse should have TOPIC set (Phase 7a.F rule
        # signature). The bare-indirect-Q rule would NOT set
        # TOPIC. If a parse has neither TOPIC nor REGISTER=
        # COLLOQUIAL, it's the bare-indirect-Q rule firing
        # incorrectly.
        for p in parses:
            fs = p[1]
            topic = fs.feats.get("TOPIC")
            register = fs.feats.get("REGISTER")
            assert topic is not None or register == "COLLOQUIAL", (
                "Kahit sino kumain. parses should all carry "
                "TOPIC (Phase 7a.F rule signature) — the Phase "
                "5n.B C10 bare-indirect-Q rule's ¬ (↓1 INDEF) "
                "constraint still excludes kahit-X"
            )


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
