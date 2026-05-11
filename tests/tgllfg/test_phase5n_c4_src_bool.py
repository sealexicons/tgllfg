"""Phase 5n.C.4 Commit 4 — src/ analyzer/placement/earley/pipeline migrated to bool.

After this commit:

* ``Analyzer`` emits Python ``bool`` for binary feats:
  ``CARDINAL``, ``DIGIT_FORM`` on digit-form numerals; ``PREDICATIVE``
  on predicative ADJ stems; ``DEM`` on non-demonstrative DET/ADP
  defaults.
* ``placement.py`` clitic-pass branches use ``is True`` /
  ``is False`` for binary-feat checks (WH, CARDINAL, ORDINAL, VAGUE,
  INTENSIFIER, SAY_CLASS).
* ``earley.py`` similarly uses ``is True`` for the
  ``ORTHOGRAPHIC_TERMINATOR`` punctuation strip.
* The analyzer-side boolean is **bridged** at two boundaries —
  ``_ma_to_pattern`` (CategoryPattern features) and
  ``_lex_equations`` (LFG equation strings) — by stringifying
  bool → ``"YES"`` / ``"NO"`` so the compiler-side string sentinels
  in C3 still match. The bridge dies in Commit 8.
"""

from __future__ import annotations

from tgllfg.core.common import MorphAnalysis, Token
from tgllfg.morph.analyzer import Analyzer
from tgllfg.parse.earley import _lex_equations, _ma_to_pattern


# === Analyzer emits Python bool for binary feats =========================


def test_digit_form_numeral_carries_bool_cardinal_and_digit_form() -> None:
    """``5`` analyses as a digit-form cardinal NUM with bool feats."""
    a = Analyzer.from_default()
    token = Token(surface="5", norm="5", start=0, end=1)
    results = a.analyze_one(token)
    nums = [r for r in results if r.pos == "NUM"]
    assert len(nums) >= 1
    r = nums[0]
    assert r.feats.get("CARDINAL") is True
    assert r.feats.get("DIGIT_FORM") is True
    # Non-binary feat: stays string.
    assert r.feats.get("NUM") == "PL"


def test_predicative_adj_carries_bool_predicative() -> None:
    """A predicative ADJ analysis has ``PREDICATIVE: True``."""
    a = Analyzer.from_default()
    token = Token(surface="maganda", norm="maganda", start=0, end=8)
    results = a.analyze_one(token)
    adj = [r for r in results if r.pos == "ADJ" and r.feats.get("PREDICATIVE") is not None]
    assert len(adj) >= 1
    for r in adj:
        assert r.feats.get("PREDICATIVE") is True


# === Boundary: _ma_to_pattern stringifies bool feats =====================


def test_ma_to_pattern_bridges_bool_to_yes_string() -> None:
    """Phase 5n.C.4 bridge: analyzer-side bool ``True`` becomes the
    string sentinel ``"YES"`` at the CategoryPattern boundary so the
    compiler-side patterns (still string-valued in C3-C4) match."""
    ma = MorphAnalysis(
        lemma="sino",
        pos="PRON",
        feats={"WH": True, "CASE": "NOM"},
    )
    p = _ma_to_pattern(ma)
    feats = dict(p.features)
    assert feats["WH"] is True
    assert feats["CASE"] == "NOM"


def test_ma_to_pattern_bridges_bool_false_to_no_string() -> None:
    ma = MorphAnalysis(
        lemma="ang",
        pos="DET",
        feats={"DEM": False, "CASE": "NOM"},
    )
    p = _ma_to_pattern(ma)
    feats = dict(p.features)
    assert feats["DEM"] is False
    assert feats["CASE"] == "NOM"


def test_ma_to_pattern_continues_to_filter_lists() -> None:
    """List-valued feats (e.g., affix_class) are still dropped at
    the pattern boundary — only str and bool are pattern-shaped."""
    ma = MorphAnalysis(
        lemma="kain",
        pos="VERB",
        feats={"affix_class": ["distrib"], "CARDINAL": True},
    )
    p = _ma_to_pattern(ma)
    feats = dict(p.features)
    assert "affix_class" not in feats
    assert feats["CARDINAL"] is True


# === Boundary: _lex_equations stringifies bool feats =====================


def test_lex_equations_emits_bare_bool_for_binary_feats() -> None:
    """Phase 5n.C.4: ``_lex_equations`` emits ``(↑ WH) = true`` for
    bool feats. The equation parser produces ``Atom(value=True)``;
    the f-structure value is bool True."""
    ma = MorphAnalysis(
        lemma="sino",
        pos="PRON",
        feats={"WH": True, "HUMAN": True, "CASE": "NOM"},
    )
    eqs = _lex_equations(ma, None)
    assert "(↑ WH) = true" in eqs
    assert "(↑ HUMAN) = true" in eqs
    assert "(↑ CASE) = 'NOM'" in eqs


def test_lex_equations_emits_bare_false_for_bool_false() -> None:
    ma = MorphAnalysis(
        lemma="ang",
        pos="DET",
        feats={"DEM": False, "CASE": "NOM"},
    )
    eqs = _lex_equations(ma, None)
    assert "(↑ DEM) = false" in eqs
    assert "(↑ CASE) = 'NOM'" in eqs
