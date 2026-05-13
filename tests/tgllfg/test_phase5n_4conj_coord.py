"""Phase 5n.A Commit 19 — N-conjunct flat NP coord (§18 L85, L85+).

The Phase 5k Commit 4 3-conjunct rules produce flat CONJUNCTS sets
for exactly 3 conjuncts. Phase 5n.A Commit 19 added explicit
4-conjunct rules (Oxford + non-Oxford × NOM/GEN/DAT). Phase 5n.A
Commit 32 added the left-recursive ``NP_LONG_LIST_<case>`` +
4+-wrap infrastructure for unbounded N — composing under the
Phase 6.C graph-constraint matcher, which is what unlocked the
5+-conjunct case (L85+).

5+-conjunct surfaces are covered:
* The 4+-wrap rule (``NP[CASE=X, COORD=AND] → NP_LONG_LIST_<X>
  PART[COORD=AND] NP``) consumes the recursive list and emits a
  flat ``CONJUNCTS`` set of arbitrary arity.
* Earlier diagnostics blamed a parser-level recursion bug; the
  actual blocker was the non-conflict matcher admitting spurious
  binary parses (mismo NP-emphatic / 2P clitic absorption) that
  failed late and crowded out the wrap completion. The Phase 6.C
  strict matcher prunes those at predict time, leaving the wrap
  free to compose.
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


# === 5/6/7-conjunct flat NP coord (Phase 6.C strict-matcher unlock) =======


class TestFivePlusConjunctNomCoord:
    """5+-conjunct NOM coord — left-recursive ``NP_LONG_LIST_NOM`` +
    4+-wrap, unlocked by the Phase 6.C strict matcher (L85+)."""

    @pytest.mark.parametrize("sentence", [
        "Kumain si Maria, si Juan, si Pedro, si Ana at si Lola.",
        "Kumain ang tatay, ang nanay, ang kuya, ang ate at ang lolo.",
    ])
    def test_5_conjunct_nom(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


class TestSixSevenConjunctNomCoord:
    """6/7-conjunct stress fixtures. The recursive ``NP_LONG_LIST_NOM``
    must compose three or four times respectively before the wrap
    rule consumes the trailing ``at NP``. Confirms the recursion is
    unbounded under the strict matcher."""

    def test_6_conjunct_nom(self) -> None:
        parses = parse_text(
            "Kumain ang tatay, ang nanay, ang kuya, ang ate, "
            "ang lolo at ang lola."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        conj = subj.feats.get("CONJUNCTS")
        assert conj is not None
        assert len(conj) == 6, (
            f"expected 6 conjuncts, got {len(conj)}"
        )
        assert subj.feats.get("COORD") == "AND"

    def test_7_conjunct_nom(self) -> None:
        parses = parse_text(
            "Kumain ang tatay, ang nanay, ang kuya, ang ate, "
            "ang lolo, ang lola at ang tito."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        conj = subj.feats.get("CONJUNCTS")
        assert conj is not None
        assert len(conj) == 7, (
            f"expected 7 conjuncts, got {len(conj)}"
        )


# === 8/9/10-conjunct stress fixtures (Phase 6.H C3) =======================


class TestEightNineTenConjunctNomCoord:
    """8/9/10-conjunct stress fixtures — push the left-recursive
    ``NP_LONG_LIST_NOM`` rule to compose five / six / seven times
    before the 4+-wrap rule consumes the trailing ``at NP``.
    Confirms the Phase 6.C strict-matcher prediction that the
    recursion generalizes to arbitrary N past the 5/6/7-conjunct
    sweet spot landed in 6.C C6 (§18.1.2 L85+ stress verification
    per Phase 6.H plan §5.8 C2)."""

    def test_8_conjunct_nom(self) -> None:
        parses = parse_text(
            "Kumain ang tatay, ang nanay, ang kuya, ang ate, "
            "ang lolo, ang lola, ang tito at ang tita."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        conj = subj.feats.get("CONJUNCTS")
        assert conj is not None
        assert len(conj) == 8, (
            f"expected 8 conjuncts, got {len(conj)}"
        )
        assert subj.feats.get("COORD") == "AND"

    def test_9_conjunct_nom(self) -> None:
        parses = parse_text(
            "Kumain ang tatay, ang nanay, ang kuya, ang ate, "
            "ang lolo, ang lola, ang tito, ang tita "
            "at ang pinsan."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        conj = subj.feats.get("CONJUNCTS")
        assert conj is not None
        assert len(conj) == 9, (
            f"expected 9 conjuncts, got {len(conj)}"
        )
        assert subj.feats.get("COORD") == "AND"

    def test_10_conjunct_nom(self) -> None:
        parses = parse_text(
            "Kumain ang tatay, ang nanay, ang kuya, ang ate, "
            "ang lolo, ang lola, ang tito, ang tita, "
            "ang pinsan at ang kapatid."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        conj = subj.feats.get("CONJUNCTS")
        assert conj is not None
        assert len(conj) == 10, (
            f"expected 10 conjuncts, got {len(conj)}"
        )
        assert subj.feats.get("COORD") == "AND"
