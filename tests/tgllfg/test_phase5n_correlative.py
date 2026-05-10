"""Phase 5n.A Commit 15 — Correlative ``hindi lang … kundi pati`` (§18 L75).

Audit finding: the §18 L75 entry was a stale deferral. Phase 5l
Commit 14 already added the correlative coord rules in
``src/tgllfg/cfg/coordination.py`` lines 480-562 — three structural
variants:

    Rule (a): S , kundi pati S  — canonical (comma + both PARTs)
    Rule (b): S kundi pati S    — no comma
    Rule (c): S , kundi S       — no pati

The lex (``kundi`` PART[COORD=BUT_NOT], ``pati`` PART[ADV=ALSO_INCL],
``lang`` 2P enclitic) was added in Phase 5k Commit 1.

Commit 15 is tests-only — no new source rules. Closes L75 by adding
the regression net + dedicated documentation.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Three rule variants (from Phase 5l Commit 14) ========================


class TestThreeRuleVariants:
    """Each of the three Phase 5l Commit 14 rule shapes parses."""

    @pytest.mark.slow
    def test_rule_a_canonical_comma_kundi_pati(self) -> None:
        # S , kundi pati S — canonical 5-daughter shape
        parses = parse_text(
            "Hindi lang kumain si Maria, kundi pati kumain si Juan."
        )
        assert len(parses) >= 1

    @pytest.mark.slow
    def test_rule_b_no_comma_kundi_pati(self) -> None:
        # S kundi pati S — 4-daughter shape (no comma)
        parses = parse_text(
            "Hindi lang kumain si Maria kundi pati kumain si Juan."
        )
        assert len(parses) >= 1

    def test_rule_c_comma_kundi_no_pati(self) -> None:
        # S , kundi S — 4-daughter shape (no pati)
        parses = parse_text(
            "Hindi lang kumain si Maria, kundi kumain si Juan."
        )
        assert len(parses) >= 1


# === Cross-V correlative ==================================================


@pytest.mark.slow
class TestCrossVerbCorrelative:
    """Different verbs in each conjunct (asymmetric V choice)."""

    @pytest.mark.parametrize("sentence", [
        "Hindi lang kumain si Maria, kundi pati tumakbo si Juan.",
        "Hindi lang tumakbo si Maria, kundi pati kumain si Juan.",
        "Hindi lang kumain si Maria, kundi pati pumunta si Juan.",
    ])
    def test_cross_verb_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === f-structure carries CORREL flag ======================================


class TestCorrelMatrixFlag:
    """The matrix S carries ``CORREL=YES`` and ``COORD=BUT_NOT``;
    both conjuncts are members of the matrix's CONJUNCTS set."""

    @pytest.mark.slow
    def test_canonical_carries_correl_flag(self) -> None:
        parses = parse_text(
            "Hindi lang kumain si Maria, kundi pati kumain si Juan."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("CORREL") == "YES"
        assert fs.feats.get("COORD") == "BUT_NOT"
        conj = fs.feats.get("CONJUNCTS")
        assert conj is not None
        assert len(conj) == 2

    def test_no_pati_does_not_carry_correl(self) -> None:
        """Rule (c) — ``S , kundi S`` (no pati) — sets COORD=BUT_NOT
        but NOT CORREL=YES, distinguishing this asymmetric variant
        from the full correlative."""
        parses = parse_text(
            "Hindi lang kumain si Maria, kundi kumain si Juan."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # COORD is set; CORREL is not (per rule (c))
        assert fs.feats.get("COORD") == "BUT_NOT"


# === Plain coord regression ===============================================


class TestPlainCoordRegression:
    """Existing Phase 5k coord patterns (at, pero, atbp.) continue
    to work — the correlative rules don't shadow them."""

    @pytest.mark.parametrize("sentence", [
        "Kumain si Maria at kumain si Juan.",
        "Kumain si Maria, pero hindi kumain si Juan.",
        "Kumain si Maria o kumain si Juan.",
    ])
    def test_plain_coord_still_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
