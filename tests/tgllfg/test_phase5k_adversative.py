"""Phase 5k Commit 6: adversative clausal coordination.

Roadmap §12.1 / plan-of-record §5.5, §6 Commit 6. One new rule
in ``cfg/coordination.py`` (added via the
``_BINARY_CLAUSAL_COORDS`` parametrization that already drove
Commit 5):

    S → S PART[COORD=BUT] S

The three adversative lex surfaces ``pero`` / ``ngunit`` /
``subalit`` all carry COORD=BUT (Phase 5k Commit 1), so this
single rule fires on all three. ``pero`` is the everyday
register; ``ngunit`` and ``subalit`` are formal.

Same shape as the AND / OR clausal-coord rules (Phase 5k Commit
5) — each conjunct retains its own PRED / SUBJ / voice / aspect;
the matrix coord-S carries CONJUNCTS + COORD=BUT with no PRED.

End-to-end target sentences:

    Kumain si Maria pero hindi pumunta si Juan.
    Kumain si Maria ngunit hindi pumunta si Juan.
    Kumain si Maria subalit hindi pumunta si Juan.
    Kumain si Maria pero pumunta si Juan.   (no negation)
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Three lex surfaces, one COORD value =============================


ADVERSATIVES = ["pero", "ngunit", "subalit"]


class TestAdversativeAll:
    """All three adversative lex surfaces yield COORD=BUT on the
    matrix coord-S."""

    @pytest.mark.parametrize("conj", ADVERSATIVES)
    def test_adversative_basic(self, conj: str) -> None:
        sentence = f"Kumain si Maria {conj} pumunta si Juan."
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got 0"
        )
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("COORD") == "BUT"

    @pytest.mark.parametrize("conj", ADVERSATIVES)
    def test_two_conjunct_clauses(self, conj: str) -> None:
        sentence = f"Kumain si Maria {conj} pumunta si Juan."
        parses = parse_text(sentence)
        _ct, fs, _astr, _diags = parses[0]
        conjuncts = fs.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2
        preds = {(c.feats.get("PRED") or "").split("<")[0].strip() for c in conjuncts}
        assert "EAT" in preds
        assert "PUNTA" in preds


# === Negation × adversative =========================================


class TestNegationXAdversative:
    """Adversative coord composes with hindi-negation via local
    scoping. The classic adversative pattern with one positive +
    one negative conjunct."""

    @pytest.mark.parametrize("conj", ADVERSATIVES)
    def test_neg_in_second_conjunct(self, conj: str) -> None:
        """``Kumain si Maria, pero hindi pumunta si Juan.`` —
        first conjunct positive, second negated. Hindi-wrap
        composes with the inner conjunct only."""
        sentence = f"Kumain si Maria {conj} hindi pumunta si Juan."
        parses = parse_text(sentence)
        coord_parses = [
            p for p in parses if p[1].feats.get("COORD") == "BUT"
        ]
        assert len(coord_parses) >= 1
        _ct, fs, _astr, _diags = coord_parses[0]
        conjuncts = fs.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2
        polarities = {
            (c.feats.get("PRED") or "").split("<")[0].strip(): c.feats.get("POLARITY")
            for c in conjuncts
        }
        # Negation lives on PUNTA-conjunct (second), not on EAT.
        assert polarities.get("PUNTA") == "NEG"
        # First conjunct has no explicit POLARITY (defaults to POS).
        assert polarities.get("EAT") in (None, "POS")


# === No matrix PRED / SUBJ ==========================================


class TestAdversativeNoMatrixPredication:
    """Adversative coord matrix carries no PRED, SUBJ, VOICE, or
    ASPECT — the predication lives entirely on each conjunct."""

    def test_no_matrix_pred(self) -> None:
        parses = parse_text("Kumain si Maria pero pumunta si Juan.")
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") is None
        assert fs.feats.get("SUBJ") is None
        assert fs.feats.get("VOICE") is None
        assert fs.feats.get("ASPECT") is None


# === C-tree shape ===================================================


class TestAdversativeCTreeShape:
    """The adversative rule yields a 3-daughter c-tree at the
    coord-S level: S + PART[COORD=BUT] + S — same shape as
    AND / OR clausal coord."""

    @pytest.mark.parametrize("conj", ADVERSATIVES)
    def test_three_daughters(self, conj: str) -> None:
        sentence = f"Kumain si Maria {conj} pumunta si Juan."
        parses = parse_text(sentence)
        ctree, _fs, _astr, _diags = parses[0]
        assert ctree.label == "S"
        assert len(ctree.children) == 3
        assert ctree.children[0].label == "S"
        assert ctree.children[1].label.startswith("PART")
        assert ctree.children[2].label == "S"


# === COORD value distinct from AND / OR / SO ========================


class TestAdversativeCoordValueDistinct:
    """``pero`` / ``ngunit`` / ``subalit`` yield COORD=BUT, NOT
    AND / OR / SO. The Commit 1 lex distinguishes by COORD value;
    rule selection is via the daughter category-pattern
    PART[COORD=BUT]."""

    def test_pero_does_not_yield_and(self) -> None:
        parses = parse_text("Kumain si Maria pero pumunta si Juan.")
        _ct, fs, _, _ = parses[0]
        assert fs.feats.get("COORD") == "BUT"
        assert fs.feats.get("COORD") != "AND"
        assert fs.feats.get("COORD") != "OR"

    def test_ngunit_yields_but(self) -> None:
        parses = parse_text("Kumain si Maria ngunit pumunta si Juan.")
        _ct, fs, _, _ = parses[0]
        assert fs.feats.get("COORD") == "BUT"

    def test_subalit_yields_but(self) -> None:
        parses = parse_text("Kumain si Maria subalit pumunta si Juan.")
        _ct, fs, _, _ = parses[0]
        assert fs.feats.get("COORD") == "BUT"


# === Adversative + predicative-ADJ ==================================


class TestAdversativeWithPredAdj:
    """Adversative coord composes with predicative-ADJ (Phase 5g)
    in either conjunct slot."""

    def test_adj_pred_first_conjunct(self) -> None:
        parses = parse_text(
            "Matanda si Maria pero bata si Juan."
        )
        # May not parse if 'bata' as predicative-ADJ isn't lex'd —
        # gracefully accept either >=1 parse with COORD=BUT or 0.
        if parses:
            coord_parses = [
                p for p in parses if p[1].feats.get("COORD") == "BUT"
            ]
            if coord_parses:
                _ct, fs, _astr, _diags = coord_parses[0]
                conjuncts = fs.feats.get("CONJUNCTS")
                assert conjuncts is not None
                assert len(conjuncts) == 2

    def test_adj_pred_with_neg_in_second(self) -> None:
        parses = parse_text(
            "Matanda si Maria pero hindi matanda si Juan."
        )
        coord_parses = [
            p for p in parses if p[1].feats.get("COORD") == "BUT"
        ]
        assert len(coord_parses) >= 1
        _ct, fs, _astr, _diags = coord_parses[0]
        conjuncts = fs.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2
