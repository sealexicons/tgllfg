"""Phase 5f closing deferral: digit tokenization.

A bare digit string (``5``, ``1990``, ``42``) analyses as a NUM
with ``CARDINAL=YES``, ``CARDINAL_VALUE=<digits>``, ``DIGIT_FORM=YES``,
and ``NUM=SG`` for ``1`` / ``NUM=PL`` for everything else. The
existing cardinal-NP-modifier (Phase 5f Commit 1), predicative-
cardinal (Commit 4), arithmetic-predicate (Commit 9), and
decimal-NUM (Commit 6) rules consume the digit form unchanged —
they only check ``CARDINAL=YES``, not ``DIGIT_FORM``.

Hooked at the morph layer in :func:`tgllfg.morph.analyzer.Analyzer.analyze_one`
(no tokenizer change — the existing ``\\w+|\\S`` regex already
captures digit strings as single tokens). Per the §18 plan entry
on digit tokenization, this is "a clean isolated extension" that
unlocks deferred coverage in arithmetic, decimals, dates, and
NP-modifier contexts where a numeric value is more natural in
digit form than as a Spanish-borrowed or native word-form
cardinal.

Tests cover:

* Morph: digit tokens analyse with the right shape; ``1`` vs
  multi-digit gets the right NUM (SG vs PL); ``0``, ``42``,
  ``1990``, large multi-digit values all work.
* Negative morph: non-digit tokens (``bata``, ``5a``, ``a5``)
  do NOT get a digit-form analysis.
* Cardinal NP-modifier with digit form: NOM / GEN / DAT positions,
  always using the free ``na`` linker (digits aren't vowel-final
  for the bound ``-ng`` form).
* Predicative cardinal with digit form: ``5 ang aso`` matches
  ``Lima ang aso`` for f-structure shape.
* Arithmetic with digit operands and word operators
  (``5 dagdag 3 ay 8``): the existing arithmetic-predicate rule
  consumes digit operands unchanged.
* Decimal-NUM with digit operands and word ``punto`` separator
  (``5 punto 3 ang isda``): the existing decimal-NUM rule
  consumes digit operands unchanged.
* Regression: word-form cardinal / predicative / arithmetic /
  decimal patterns still parse identically.
* Word-form cardinals are unchanged at the morph layer (no spurious
  digit analysis on a non-digit lex entry).

Out of scope (truly separate constructions, follow-on commits in
this PR):

* ``Mayo 5`` day-month form — needs a new NP rule for
  ``MONTH N + NUM[CARDINAL=YES, DIGIT_FORM=YES]``.
* ``noong 1990`` year expression — needs the temporal-frame PP
  rule extended to admit NUM in place of N.
* Symbolic arithmetic operators (``5 + 3 = 8``) — needs
  ``+`` / ``-`` / ``=`` particles + arithmetic-predicate rule
  extension to accept symbolic operators alongside word ones.
* No-space digit decimals (``5.3``) — needs ``.`` particle as
  DECIMAL_SEP.
"""

from __future__ import annotations

import pytest

from tgllfg.common import FStructure, MorphAnalysis
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import tokenize


def _morph(text: str) -> list[MorphAnalysis]:
    toks = tokenize(text)
    return [m for ms in analyze_tokens(toks) for m in ms]


def _first_obj(text: str) -> FStructure | None:
    rs = parse_text(text)
    if not rs:
        return None
    _, f, _, _ = rs[0]
    obj = f.feats.get("OBJ")
    return obj if isinstance(obj, FStructure) else None


def _first_subj(text: str) -> FStructure | None:
    rs = parse_text(text)
    if not rs:
        return None
    _, f, _, _ = rs[0]
    subj = f.feats.get("SUBJ")
    return subj if isinstance(subj, FStructure) else None


def _matrix(text: str) -> FStructure | None:
    rs = parse_text(text)
    if not rs:
        return None
    return rs[0][1]


# --- Morph layer ----------------------------------------------------------


class TestDigitMorph:
    """Bare digits analyse as cardinal NUMs with DIGIT_FORM=YES."""

    @pytest.mark.parametrize("digit,num", [
        ("0",    "PL"),
        ("1",    "SG"),
        ("2",    "PL"),
        ("5",    "PL"),
        ("9",    "PL"),
        ("10",   "PL"),
        ("42",   "PL"),
        ("100",  "PL"),
        ("1990", "PL"),
        ("2026", "PL"),
    ])
    def test_digit_analyses(self, digit: str, num: str) -> None:
        ms = _morph(digit)
        digit_ms = [m for m in ms if m.pos == "NUM" and m.feats.get("DIGIT_FORM") == "YES"]
        assert len(digit_ms) == 1, f"expected exactly 1 digit-form NUM, got {ms}"
        m = digit_ms[0]
        assert m.lemma == digit
        assert m.feats.get("CARDINAL") == "YES"
        assert m.feats.get("CARDINAL_VALUE") == digit
        assert m.feats.get("NUM") == num

    def test_only_digit_analysis_for_bare_digit(self) -> None:
        """A bare digit produces only the digit-form NUM (no
        accidental particle / pronoun / verb / noun match)."""
        ms = _morph("5")
        assert len(ms) == 1
        assert ms[0].pos == "NUM"
        assert ms[0].feats.get("DIGIT_FORM") == "YES"

    @pytest.mark.parametrize("non_digit", ["bata", "5a", "a5", "5b3", "tatlo"])
    def test_non_digit_no_digit_form(self, non_digit: str) -> None:
        """Tokens that aren't pure ASCII digits don't get a
        digit-form analysis. ``tatlo`` analyses as a word-form NUM
        via particles.yaml; the digit-form path doesn't fire."""
        ms = _morph(non_digit)
        digit_ms = [m for m in ms if m.feats.get("DIGIT_FORM") == "YES"]
        assert digit_ms == [], f"unexpected digit-form analysis: {digit_ms}"


# --- Cardinal NP-modifier with digit form --------------------------------


class TestDigitNpModifierObj:
    """Digit-form cardinals modify a head N in OBJ position via the
    free ``na`` linker (digits aren't vowel-final for the bound
    ``-ng`` form). Mirrors ``test_cardinal_np_modifier.TestCardinalAsObj``
    with digit operands."""

    @pytest.mark.parametrize("digit", ["1", "2", "5", "10", "100"])
    def test_digit_in_obj(self, digit: str) -> None:
        text = f"Kumain ako ng {digit} na isda."
        obj = _first_obj(text)
        assert obj is not None, f"no parse for {text!r}"
        assert obj.feats.get("LEMMA") == "isda"
        assert obj.feats.get("CARDINAL_VALUE") == digit


class TestDigitNpModifierSubj:
    """Digit-form cardinals in SUBJ position via the free ``na``
    linker."""

    @pytest.mark.parametrize("digit", ["1", "3", "7", "42"])
    def test_digit_in_subj(self, digit: str) -> None:
        text = f"Tumakbo ang {digit} na aso."
        subj = _first_subj(text)
        assert subj is not None, f"no parse for {text!r}"
        assert subj.feats.get("LEMMA") == "aso"
        assert subj.feats.get("CARDINAL_VALUE") == digit


class TestDigitNpModifierDat:
    """Digit-form cardinals attach via DAT case-marker (``sa``).
    Lands in ADJUNCT, not SUBJ/OBJ. Confirm parse and CARDINAL_VALUE
    on the ADJUNCT NP."""

    def test_digit_in_dat(self) -> None:
        text = "Bumili ako sa 2 na tindahan."
        rs = parse_text(text)
        assert rs, f"no parse for {text!r}"
        _, f, _, _ = rs[0]
        adj = f.feats.get("ADJUNCT")
        assert adj is not None, "no ADJUNCT"
        # ADJUNCT is a frozenset; pull the first member.
        members = list(adj) if isinstance(adj, frozenset) else [adj]
        cardinals = [m for m in members
                     if isinstance(m, FStructure)
                     and m.feats.get("CARDINAL_VALUE") == "2"]
        assert cardinals, f"no DAT NP with CARDINAL_VALUE='2' in ADJUNCT={adj}"


# --- Predicative cardinal with digit form --------------------------------


class TestDigitPredicativeCardinal:
    """``5 ang aso`` "the dogs are five" — same construction as
    ``Lima ang aso`` but with digit operand."""

    @pytest.mark.parametrize("digit,num", [
        ("1",  "SG"),
        ("3",  "PL"),
        ("5",  "PL"),
        ("10", "PL"),
        ("42", "PL"),
    ])
    def test_predicative(self, digit: str, num: str) -> None:
        text = f"{digit} ang aso."
        f = _matrix(text)
        assert f is not None, f"no parse for {text!r}"
        assert f.feats.get("PRED") == "CARDINAL <SUBJ>"
        assert f.feats.get("CARDINAL_VALUE") == digit
        assert f.feats.get("NUM") == num
        subj = f.feats.get("SUBJ")
        assert subj is not None and subj.feats.get("LEMMA") == "aso"


# --- Arithmetic with digit operands --------------------------------------


class TestDigitArithmetic:
    """Word-operator arithmetic with digit operands. The existing
    arithmetic-predicate rule (Phase 5f Commit 9) consumes them
    unchanged."""

    def test_plus(self) -> None:
        f = _matrix("5 dagdag 3 ay 8.")
        assert f is not None
        assert f.feats.get("PRED") == "ARITHMETIC"
        assert f.feats.get("OP") == "PLUS"
        assert f.feats.get("OPERAND_1") == "5"
        assert f.feats.get("OPERAND_2") == "3"
        assert f.feats.get("RESULT") == "8"

    def test_minus(self) -> None:
        f = _matrix("10 bawas 4 ay 6.")
        assert f is not None
        assert f.feats.get("PRED") == "ARITHMETIC"
        assert f.feats.get("OP") == "MINUS"
        assert f.feats.get("OPERAND_1") == "10"
        assert f.feats.get("OPERAND_2") == "4"
        assert f.feats.get("RESULT") == "6"

    def test_word_form_regression(self) -> None:
        """Word-form arithmetic still works identically."""
        f = _matrix("Dalawa dagdag tatlo ay lima.")
        assert f is not None
        assert f.feats.get("PRED") == "ARITHMETIC"
        assert f.feats.get("OPERAND_1") == "2"
        assert f.feats.get("OPERAND_2") == "3"
        assert f.feats.get("RESULT") == "5"


# --- Decimals with digit operands ----------------------------------------


class TestDigitDecimal:
    """Word-``punto`` decimal with digit operands. Uses the
    predicative-cardinal frame to surface the decimal as a complete
    sentence."""

    def test_digit_decimal_predicative(self) -> None:
        f = _matrix("5 punto 3 ang isda.")
        assert f is not None
        assert f.feats.get("PRED") == "CARDINAL <SUBJ>"
        # Integer part lifts to the matrix CARDINAL_VALUE.
        assert f.feats.get("CARDINAL_VALUE") == "5"

    def test_word_form_decimal_regression(self) -> None:
        f = _matrix("Dos punto singko ang isda.")
        assert f is not None
        assert f.feats.get("PRED") == "CARDINAL <SUBJ>"
        assert f.feats.get("CARDINAL_VALUE") == "2"


# --- Word-form regression (no digit shape on word entries) ---------------


class TestWordFormRegression:
    """Word-form cardinals from particles.yaml don't accidentally
    get DIGIT_FORM=YES — only their canonical word-form analysis
    surfaces."""

    @pytest.mark.parametrize("word,value", [
        ("isa",    "1"),
        ("dalawa", "2"),
        ("tatlo",  "3"),
        ("lima",   "5"),
        ("sampu",  "10"),
    ])
    def test_word_card_no_digit_form(self, word: str, value: str) -> None:
        ms = _morph(word)
        nums = [m for m in ms if m.pos == "NUM"]
        assert len(nums) == 1, f"expected 1 NUM analysis for {word!r}, got {nums}"
        m = nums[0]
        assert m.feats.get("CARDINAL") == "YES"
        assert m.feats.get("CARDINAL_VALUE") == value
        assert m.feats.get("DIGIT_FORM") is None
