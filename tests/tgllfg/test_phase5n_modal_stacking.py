"""Phase 5n.A Commit 11 — Modal stacking (§18 L67).

Pre-Commit-11 the Phase 5j Commit 7 modal control wrap admitted
single-modal sentences (``Dapat akong kumain.``) but stacked-modal
sentences (``Dapat akong puwedeng kumain.`` "I should be able to
eat") 0-parsed because the inner ``puwedeng kumain`` constituent had
no S_XCOMP rule that admits a modal-headed gapped clause.

Phase 5n.A Commit 11 adds a parallel nested-MODAL S_XCOMP rule to
``cfg/control.py`` mirroring the existing PSYCH / INTRANS / TRANS
nested rules:

    S_XCOMP → V[CTRL_CLASS=MODAL] PART[LINK=N{A,G}] S_XCOMP
        (↑ SUBJ) = (↑ REL-PRO)
        (↑ XCOMP) = ↓3
        (↑ SUBJ) = (↑ XCOMP REL-PRO)
        (↓1 CTRL_CLASS) =c 'MODAL'
        (↓1 MODAL) =c 'YES'

This binds the inner modal's SUBJ to its own REL-PRO (it is the gap),
chains its XCOMP to the inner-inner clause, and propagates the
controller through the equation chain. Composing across depth-N
gives a single f-node shared across SUBJ slots at every level.
Modal stacking falls out: outer-modal SUBJ = inner-modal SUBJ =
innermost-action SUBJ.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === 2-layer canonical stack ==============================================


class TestTwoLayerStack:
    """The canonical L67 target ``Dapat akong puwedeng kumain.``
    parses with two modal control wraps composed."""

    def test_canonical_dapat_puwede_stack(self) -> None:
        parses = parse_text("Dapat akong puwedeng kumain.")
        assert len(parses) >= 1

    def test_subj_reentrant_through_stack(self) -> None:
        """The matrix SUBJ (ako) is structurally shared with the
        inner modal's SUBJ AND the innermost action's SUBJ."""
        parses = parse_text("Dapat akong puwedeng kumain.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # Matrix is dapat
        assert "DAPAT" in (fs.feats.get("PRED") or "")
        # Matrix SUBJ is the NOM-PRON ako
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("CASE") == "NOM"
        assert subj.feats.get("NUM") == "SG"
        # Matrix XCOMP is the inner modal puwede
        xcomp = fs.feats.get("XCOMP")
        assert xcomp is not None
        assert "PUWEDE" in (xcomp.feats.get("PRED") or "")
        # Inner-modal SUBJ is the same f-node as matrix SUBJ
        assert xcomp.feats.get("SUBJ") is subj
        # Innermost XCOMP is kumain ("eat")
        innermost = xcomp.feats.get("XCOMP")
        assert innermost is not None
        assert "EAT" in (innermost.feats.get("PRED") or "")
        # Innermost SUBJ is also the same f-node
        assert innermost.feats.get("SUBJ") is subj


# === 2-layer with explicit `na` linker ====================================


class TestTwoLayerWithNaLinker:
    """Consonant-final inner modals (``dapat`` / ``kailangan``) take
    the standalone ``na`` linker rather than the bound ``-ng``."""

    @pytest.mark.parametrize("sentence", [
        "Puwede akong dapat na kumain.",
        "Maaari akong dapat na kumain.",
        "Kailangan akong dapat na kumain.",
    ])
    def test_outer_modal_inner_dapat(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === 3-layer stretch ======================================================


class TestThreeLayerStack:
    """Three-modal stacks compose by recursion through the new
    nested-MODAL S_XCOMP rule."""

    @pytest.mark.parametrize("sentence", [
        "Dapat akong puwedeng maaaring kumain.",
        "Maaari akong dapat na puwedeng kumain.",
    ])
    def test_three_layer_stack(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === Single-modal regression ==============================================


class TestSingleModalRegression:
    """The Phase 5j Commit 7 single-modal patterns must continue
    to work — Commit 11 adds the nested rule but doesn't change
    the matrix wrap."""

    @pytest.mark.parametrize("sentence", [
        "Dapat akong kumain.",
        "Puwede akong kumain.",
        "Maaari akong kumain.",
        "Kailangan akong kumain.",
    ])
    def test_single_modal_still_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
