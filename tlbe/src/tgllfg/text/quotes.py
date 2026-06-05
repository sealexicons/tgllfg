# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Quotation-bracket normalization pre-pass (Phase 10.J.post-12.6).

Converts balanced ASCII quote pairs (``'X'`` / ``"X"``) into their
curly counterparts (``‘X’`` / ``"X"``) so the chart's quotation
rules (``N → PART[QUOT_OPEN] N PART[QUOT_CLOSE]`` and the parallel
``S → ...`` for direct speech) admit them.

ASCII vs curly handling
-----------------------

Curly quote characters (U+2018 / U+2019 / U+201C / U+201D) are
surface-unambiguous — left forms always open and right forms always
close. They get dedicated ``PART[QUOT_ROLE=OPEN|CLOSE, QUOT_TYPE=X]``
lex entries (see ``data/tgl/particles.yaml``).

ASCII apostrophe ``'`` and double-quote ``"`` are surface-ambiguous —
the same character opens AND closes. Additionally, ASCII ``'``
collides with:

* **Clitic contractions** (``Maria't`` = ``Maria at``, ``rito'y`` =
  ``rito ay``, ``Kahi't`` = ``Kahit``) — handled by the dedicated
  pre-passes :func:`tgllfg.text.clitics.split_apostrophe_t` and
  :func:`split_apostrophe_y` running after :func:`tokenize`.
* **Abbreviation prefixes** (``'yon`` = ``iyon``, ``'kako`` =
  ``wika ko``, ``'kamo`` = ``wika mo``) — these are stray
  apostrophes attached to the front of an abbreviated form.
  Currently they fall through morphology as ``_UNK`` and get
  stripped by :func:`tgllfg.parse.earley._strip_non_content`,
  leaving the bare abbreviated form to parse.

This pre-pass converts ASCII pairs to curly **only when the pair is
balanced and the inner content is well-formed for a quotation
context**:

1. **Clitic-protect**: identify ASCII ``'`` positions matching the
   pre-tokenize shapes for ``Xt`` and ``Xy`` clitic contractions
   (preceded by a vowel-final character, followed by ``t`` or ``y``
   then word-end). Mark these apostrophes as "off-limits" before
   pairing.
2. **Sequential pairing**: walk the remaining (non-clitic) ASCII
   ``'`` and ``"`` characters in left-to-right order, pairing
   alternately as open / close.
3. **Inner-content discrimination**: a balanced ASCII pair is
   converted to curly only if its inner content is either:

   * **Single token** (no internal whitespace), e.g., ``'monsoon'``,
     ``"classroom"``. The chart's ``N → PART[QUOT_OPEN] N
     PART[QUOT_CLOSE]`` rule consumes it.
   * **Multi-token containing a sentence-terminator** (``.``, ``?``,
     ``!``), e.g., ``"Hindi tayo aalis."``. The chart's
     ``S → PART[QUOT_OPEN] S PART[QUOT_CLOSE]`` rule consumes it.

   **Multi-token without terminator** (e.g., ``"birthday party"``,
   ``"eye make-up"``) are left as ASCII — preserving the current
   ``_strip_non_content`` ``_UNK``-strip behavior. Proper opaque-NP
   handling is deferred to a future sub-PR.

4. **Stray (unpaired) apostrophes**: left as ASCII; they fall
   through to ``_UNK`` analysis and the strip pass.

The pre-pass is therefore **conservative**: it only converts when
both endpoints are present and the inner content is structurally
admissible by the chart. Cases it doesn't recognize remain
untouched, preserving baseline parse coverage.
"""

import re

_ASCII_SINGLE = "'"
_ASCII_DOUBLE = '"'
_CURLY_OPEN_SINGLE = "‘"
_CURLY_CLOSE_SINGLE = "’"
_CURLY_OPEN_DOUBLE = "“"
_CURLY_CLOSE_DOUBLE = "”"

_VOWELS = set("aeiouAEIOU")

# A balanced ASCII quote pair: opener, captured inner content
# (no nested quotes of the same type, no newlines), closer. Inner
# content is bounded to a reasonable span to avoid matching across
# sentences.
_ASCII_SINGLE_PAIR = re.compile(r"'([^'\n]{1,200})'")
_ASCII_DOUBLE_PAIR = re.compile(r'"([^"\n]{1,200})"')

# Sentence-terminator characters allowed inside a direct-speech
# quoted span. Periods serve double duty (decimal separator,
# abbreviation marker, sentence terminator) so we treat ``.`` as
# a terminator when it appears in quoted-inner content — the chart
# will reject ungrammatical inners.
_TERMINATORS = re.compile(r"[.?!]")


def _classify_inner(inner: str) -> str:
    """Decide whether a balanced inner content should be curlified.

    Returns one of:

    * ``"mention"`` — single-token (no whitespace); maps to the
      chart's ``N → PART[QUOT_OPEN] N PART[QUOT_CLOSE]`` rule.
    * ``"speech"`` — multi-token with at least one sentence-
      terminator; maps to ``S → PART[QUOT_OPEN] S PART[QUOT_CLOSE]``.
    * ``"opaque"`` — multi-token without terminator; leave as
      ASCII so the ``_strip_non_content`` baseline behavior
      persists. A future sub-PR may add proper opaque-NP handling.
    """
    stripped = inner.strip()
    if not stripped:
        return "opaque"
    if not any(ch.isspace() for ch in stripped):
        return "mention"
    if _TERMINATORS.search(stripped):
        return "speech"
    return "opaque"


def _is_clitic_apostrophe(text: str, idx: int) -> bool:
    """Detect ``'`` at position ``idx`` that's part of a clitic
    contraction (``Xt`` or ``Xy`` where X ends in a vowel).

    Matches the surface patterns consumed by
    :func:`tgllfg.text.clitics.split_apostrophe_t` and
    :func:`split_apostrophe_y` AFTER tokenization. Done here at
    the text level to protect these positions from pairing.
    """
    if idx <= 0 or idx + 1 >= len(text):
        return False
    prev = text[idx - 1]
    nxt = text[idx + 1]
    if prev not in _VOWELS:
        return False
    if nxt not in ("t", "T", "y", "Y"):
        return False
    # Confirm the t/y is at a word boundary (followed by space,
    # punct, or end-of-string).
    after = text[idx + 2] if idx + 2 < len(text) else ""
    if after and (after.isalnum() or after == "-"):
        return False
    return True


def normalize_quoted_spans(text: str) -> str:
    """Convert balanced ASCII quote pairs to curly variants.

    See module docstring for the full classification rules.
    """
    # Process double quotes first (they don't collide with clitics).
    def _replace_double(m: re.Match[str]) -> str:
        inner = m.group(1)
        kind = _classify_inner(inner)
        if kind in ("mention", "speech"):
            return f"{_CURLY_OPEN_DOUBLE}{inner}{_CURLY_CLOSE_DOUBLE}"
        return m.group(0)

    text = _ASCII_DOUBLE_PAIR.sub(_replace_double, text)

    # Process single quotes with clitic-protection. We can't use a
    # simple sub() because each `'` needs context inspection. Walk
    # the string finding candidate pairs whose endpoints aren't
    # clitic apostrophes.
    out_chars: list[str] = list(text)
    i = 0
    n = len(out_chars)
    while i < n:
        if out_chars[i] != _ASCII_SINGLE or _is_clitic_apostrophe(text, i):
            i += 1
            continue
        # Look for a matching close `'` skipping clitic positions.
        j = i + 1
        while j < n:
            if out_chars[j] == _ASCII_SINGLE and not _is_clitic_apostrophe(
                text, j
            ):
                break
            if out_chars[j] == "\n":
                j = n  # disqualify multi-line
                break
            j += 1
        if j >= n or j - i > 200:
            i += 1
            continue
        inner = "".join(out_chars[i + 1 : j])
        kind = _classify_inner(inner)
        if kind in ("mention", "speech"):
            out_chars[i] = _CURLY_OPEN_SINGLE
            out_chars[j] = _CURLY_CLOSE_SINGLE
            i = j + 1
        else:
            i += 1
    return "".join(out_chars)
