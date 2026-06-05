# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.A Commit 9 — maaari polysemous noun reading (§18 L65).

Pre-Commit-9 the surface ``maaari`` analyzed only as VERB[MODAL=YES]
(Phase 5j Commit 6 modal lex). The nominal reading
("the possible / possibility", as in ``Ang maaari ay X.``) was
deferred to corpus pressure per §18.1 L65.

Phase 5n.A Commit 9 adds a parallel NOUN entry in
``data/tgl/nouns.yaml``. Same lex-polysemy pattern as Phase 5j
Commit 6 ``kailangan`` (V[MODAL] + N): one surface, two analyses,
rule context disambiguates.

The nominal reading is marginal in modern Tagalog (the modal reading
dominates). The lex addition closes the §18.1 L65 deferral; downstream
parsers / consumers can read off the dual analyses without ambiguity
blowup because the rule contexts are structurally distinct.
"""

import pytest

from tgllfg.core.common import Token
from tgllfg.core.pipeline import parse_text
from tgllfg.morph import Analyzer


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === Bare-surface dual-analysis ===========================================


class TestMaaariDualAnalyses:
    """Bare ``maaari`` produces both VERB[MODAL=YES] (Phase 5j
    Commit 6) and NOUN (Phase 5n.A Commit 9) analyses."""

    def test_maaari_has_verb_modal_analysis(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("maaari"))
        verb_modal = [
            a for a in out
            if a.pos == "VERB" and a.feats.get("MODAL") is True
        ]
        assert len(verb_modal) == 1
        assert verb_modal[0].lemma == "maaari"

    def test_maaari_has_noun_analysis(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("maaari"))
        noun = [a for a in out if a.pos == "NOUN"]
        assert len(noun) == 1
        assert noun[0].lemma == "maaari"


# === NOUN context (the new reading) =======================================


class TestMaaariNounContext:
    """The nominal reading fires in NP-argument contexts."""

    @pytest.mark.parametrize("sentence", [
        "Kumain ang maaari.",         # AV with NOM-NP SUBJ headed by maaari
        "Maganda ang maaari.",        # predicative-ADJ with maaari SUBJ
        "Nakita ko ang maaari.",      # OV with NOM-NP OBJ headed by maaari
    ])
    def test_maaari_as_np_head(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === VERB[MODAL] context (regression) =====================================


class TestMaaariModalRegression:
    """The pre-Commit-9 modal use of ``maaari`` must continue to
    parse — the new NOUN entry must not break the VERB[MODAL]
    analysis."""

    @pytest.mark.parametrize("sentence", [
        "Maaari akong kumain.",       # modal + PRON-with-linker + V
        "Maaari kayong kumain.",      # 2pl variant
        "Maaari siyang kumain.",      # 3sg variant
    ])
    def test_maaari_as_modal(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === Same lex-polysemy pattern as kailangan ==============================


class TestKailanganPolysemyRegression:
    """The Phase 5j Commit 6 ``kailangan`` polysemy (V[MODAL] + N)
    must continue to work — Commit 9 follows the same pattern;
    this confirms the precedent is preserved."""

    def test_kailangan_dual_analyses(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("kailangan"))
        verb_modal = [
            a for a in out
            if a.pos == "VERB" and a.feats.get("MODAL") is True
        ]
        noun = [a for a in out if a.pos == "NOUN"]
        assert len(verb_modal) == 1
        assert len(noun) == 1

    def test_kailangan_modal_sentence(self) -> None:
        parses = parse_text("Kailangan akong kumain.")
        assert len(parses) >= 1
