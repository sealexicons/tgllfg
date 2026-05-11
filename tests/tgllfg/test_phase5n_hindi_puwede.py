"""Phase 5n.A Commit 12 — hindi puwede standalone (§18 L68).

Pre-Commit-12 the modal predicates only parsed when accompanied by
a NOM-NP SUBJ + linker + S_XCOMP (Phase 5j Commit 7 modal control
wrap). The bare-modal forms (``Hindi puwede.`` "Not allowed",
``Hindi dapat.`` "Not necessary") 0-parsed because no rule admitted
``V[CTRL_CLASS=MODAL]`` as a standalone S head.

Phase 5n.A Commit 12 adds a single-daughter modal-as-predicate
rule in cfg/control.py:

    S → V[CTRL_CLASS=MODAL]
        (↑) = ↓1
        (↑ SUBJ PRED) = 'PRO'
        (↑ XCOMP PRED) = 'PRO'
        (↑ MODAL_STANDALONE) = 'YES'
        (↓1 CTRL_CLASS) =c 'MODAL'
        (↓1 MODAL) =c 'YES'

The rule provides impersonal-PRO fillers for both arguments declared
by the modal lex's PRED template (``PUWEDE <SUBJ, XCOMP>`` etc.) so
completeness is satisfied without breaking the analytical commitment.
``MODAL_STANDALONE: YES`` flag distinguishes the standalone reading
from the multi-daughter modal-control wrap output for downstream
consumers.

Composes with the Phase 4 §7.2 hindi-wrap (``S → PART[POLARITY=NEG]
S``) to yield ``Hindi puwede.`` etc. without explicit changes to
the negation rule.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Bare modal as predicate ==============================================


class TestBareModalPredicate:
    """Each modal lex (``puwede`` / ``dapat`` / ``maaari`` /
    ``kailangan``) parses as a standalone S."""

    @pytest.mark.parametrize("modal", [
        "Puwede.",
        "Pwede.",       # alt spelling, routes via LEMMA collapse
        "Dapat.",
        "Maaari.",
        "Kailangan.",
    ])
    def test_bare_modal_parses(self, modal: str) -> None:
        parses = parse_text(modal)
        assert len(parses) >= 1


# === Hindi-wrapped modal ==================================================


class TestHindiWrappedModal:
    """``Hindi`` + bare modal composes via the Phase 4 §7.2
    hindi-wrap onto the new standalone-modal S."""

    @pytest.mark.parametrize("sentence", [
        "Hindi puwede.",
        "Hindi pwede.",
        "Hindi dapat.",
        "Hindi maaari.",
        "Hindi kailangan.",
    ])
    def test_hindi_modal_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === Diagnostic flag verification =========================================


class TestModalStandaloneFlag:
    """The standalone parse carries ``MODAL_STANDALONE=YES`` to
    distinguish it from the modal-control-wrap output."""

    def test_bare_puwede_carries_flag(self) -> None:
        parses = parse_text("Puwede.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("MODAL_STANDALONE") is True

    def test_hindi_puwede_carries_flag(self) -> None:
        parses = parse_text("Hindi puwede.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("MODAL_STANDALONE") is True
        assert fs.feats.get("POLARITY") == "NEG"


# === Modal-with-XCOMP regression ==========================================


class TestModalWithXcompRegression:
    """The Phase 5j Commit 7 modal-with-XCOMP wrap and the Phase 5n.A
    Commit 11 nested-MODAL S_XCOMP rule must continue to work — the
    standalone rule is a single-daughter alternative; the multi-
    daughter wraps fire when XCOMP material is present."""

    @pytest.mark.parametrize("sentence", [
        # Single-modal patterns (Commit 7):
        "Puwede akong kumain.",
        "Dapat akong kumain.",
        "Maaari akong kumain.",
        "Kailangan akong kumain.",
        "Hindi ako puwedeng kumain.",
        # Stacked-modal patterns (Commit 11):
        "Dapat akong puwedeng kumain.",
        "Puwede akong dapat na kumain.",
    ])
    def test_modal_with_xcomp_still_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
