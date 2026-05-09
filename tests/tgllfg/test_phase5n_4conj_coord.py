"""Phase 5n.A Commit 19 — 4-conjunct flat NP coord (§18 L85).

The Phase 5k Commit 4 3-conjunct rules produce flat CONJUNCTS sets
for exactly 3 conjuncts. Commit 19 adds explicit 4-conjunct rules
(Oxford + non-Oxford × NOM/GEN/DAT) producing flat 4-member
CONJUNCTS sets for ``Maria, Juan, Pedro, at Ana`` style surfaces.

5+-conjunct surfaces are NOT covered (a follow-on item):
* The right-recursive ``NP_LONG_LIST`` non-terminal approach
  builds the recursive list correctly but the wrap rule's
  ``(↑) = ↓1`` doesn't compose to a top-level S.
* Explicit 5-conjunct rules load but don't fire — possibly an
  Earley state-explosion interaction with the Phase 5m mismo
  NP-emphatic rule that ambiguously matches ``Ana at`` as
  ``NP + PART``.

Both routes are out of L85 scope to debug. 4-conjunct flat is
the primary attested 4+ form in R&G 1981 / S&O 1972 corpora;
5+-conjunct stays pinned at 0-parse as the trigger for follow-on.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === 4-conjunct Oxford and non-Oxford =====================================


class TestFourConjunctNomCoord:
    """4-conjunct NOM coord works in both Oxford and non-Oxford forms."""

    @pytest.mark.parametrize("sentence", [
        # Oxford comma:
        "Kumain si Maria, si Juan, si Pedro, at si Ana.",
        "Si Maria, si Juan, si Pedro, at si Ana ay kumain.",
        # Non-Oxford:
        "Kumain si Maria, si Juan, si Pedro at si Ana.",
        "Si Maria, si Juan, si Pedro at si Ana ay kumain.",
    ])
    def test_4_conjunct_nom(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


class TestFourConjunctGenCoord:
    """4-conjunct GEN coord (e.g., ``Bumili ako ng X, Y, Z, at W``)."""

    @pytest.mark.parametrize("sentence", [
        "Bumili ako ng aklat, ng lapis, ng papel, at ng libro.",
        "Bumili ako ng aklat, ng lapis, ng papel at ng libro.",
    ])
    def test_4_conjunct_gen(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === f-structure carries flat 4-element CONJUNCTS =========================


class TestFlatConjuncts:
    """The matrix CONJUNCTS set has exactly 4 members for 4-conjunct
    surfaces (not nested binary)."""

    def test_4_conjunct_carries_four_members(self) -> None:
        parses = parse_text(
            "Si Maria, si Juan, si Pedro, at si Ana ay kumain."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        topic = fs.feats.get("TOPIC")
        assert topic is not None
        conj = topic.feats.get("CONJUNCTS")
        assert conj is not None
        assert len(conj) == 4, (
            f"expected 4 conjuncts, got {len(conj)}"
        )
        assert topic.feats.get("COORD") == "AND"


# === 3-conjunct regression ================================================


class TestThreeConjunctRegression:
    """The Phase 5k Commit 4 3-conjunct rules continue to fire."""

    @pytest.mark.parametrize("sentence", [
        "Kumain si Maria, si Juan, at si Pedro.",
        "Kumain si Maria, si Juan at si Pedro.",
    ])
    def test_3_conjunct_still_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === 5+-conjunct deferred (pinned at 0-parse) =============================


class TestFivePlusConjunctDeferred:
    """5+-conjunct flat coord is a separate follow-on item — neither
    the right-recursive NP_LONG_LIST approach nor the explicit
    5-conjunct rules fire cleanly. Pinned at 0-parse as the trigger
    for follow-on work."""

    def test_5_conjunct_zero_parse_pinned(self) -> None:
        parses = parse_text(
            "Kumain si Maria, si Juan, si Pedro, si Ana at si Jose."
        )
        assert len(parses) == 0, (
            "5-conjunct coord unexpectedly parses — flip this "
            "assertion to >= 1 when the follow-on lands."
        )
