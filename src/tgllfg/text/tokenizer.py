# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

# tgllfg/text/tokenizer.py

"""Word-level tokenizer for Tagalog text.

The default rule is ``\\w+|\\S`` — match maximal word-character runs
or single non-whitespace characters. A surgical exception handles
the orthographic convention where Tagalog verbal / derivational
prefixes attach to vowel-initial stems via a hyphen:

  ``Nag-uusap``      ← mag- IPFV of usap, hyphen-glued because the
                       stem ``uusap`` is vowel-initial (CV-redup of
                       ``usap``).
  ``pag-aaral``      ← deverbal nominalization of mag-aral.
  ``mag-aral``       ← mag- AV-INF of aral.
  ``pakikipag-usap`` ← reciprocal nominalization.

Without the surgical case, these would split into three tokens
(``Nag`` / ``-`` / ``uusap``), and the morphological analyzer
would fail to find the inflected surface (which is indexed without
the hyphen: ``naguusap`` etc.).

Compound nouns and non-verbal hyphenated forms (``tabing-dagat``
"seashore", ``kasing-bilis`` equative, ``well-known``) intentionally
stay split — they're either handled by other mechanisms (the
``tabing`` linker-decomposition path; the ``kasing`` equative
paradigm cell) or aren't Tagalog at all (English compounds).

The ``norm`` field of the rejoined token strips the internal
hyphen so the analyzer's surface index (which keys on
``naguusap`` / ``pagaaral`` / ``magaral`` without hyphens) finds it.

Apostrophe-clitic contractions (``Maria't`` → ``Maria at``,
``rito'y`` → ``rito ay``, ``Kahi't`` → ``Kahit``, ``hangga't`` →
``hanggang``, ``Kadalasa'y`` → ``Kadalasan`` + ``ay``) are
handled by the dedicated pre-passes :func:`split_apostrophe_t`
and :func:`split_apostrophe_y` in :mod:`tgllfg.text.clitics`
(running after :func:`tokenize` in the pipeline).
"""

import re

from ..core.common import Token

# Tagalog verbal / derivational prefixes that conventionally attach
# to vowel-initial stems with an orthographic hyphen. Listed longest-
# first in the alternation so that ``pakikipag-`` is tried before
# ``pag-`` and ``magpa-`` before ``mag-``.
_TGL_HYPHEN_PREFIXES = (
    "pakikipag", "makipag", "nakipag",
    "magpa", "nagpa", "magsi", "nagsi",
    "maka", "naka", "mapa", "napa", "paka", "paki",
    "mang", "nang", "pang",
    "mag", "nag", "pag",
    "ma", "na", "pa", "ka",
)
_PFX_ALT = "(?:" + "|".join(_TGL_HYPHEN_PREFIXES) + ")"

_WORD = re.compile(
    _PFX_ALT + r"-[aeiou]\w*"   # Tagalog prefix + - + vowel-initial stem
    r"|\w+"                       # ordinary word
    r"|-{2,}"                     # double-hyphen / em-dash surrogate
    r"|\S",                       # standalone non-word
    re.IGNORECASE,
)

# Phase 10.J.post-12.3 — parenthetical-normalization regexes.
# Match a paren-bracketed region (no nesting; ``[^()]*``); capture
# the inner content for the dispatch below.
_PAREN_REGION = re.compile(r"\s*\(\s*([^()]*?)\s*\)\s*")
# A single-word inner: alphanumeric run, optionally hyphenated.
# Used to discriminate pedagogical single-word glosses (drop both
# delimiters AND content) from multi-word parentheticals (keep
# content). See :func:`normalize_parens`.
_SINGLE_WORD = re.compile(r"\w[\w-]*")


def normalize_parens(text: str) -> str:
    """Pre-tokenize pass — normalize parenthetical glosses.

    Parenthetical regions in the audit-corpus reference works
    (R&G 1981 Intermediate, R&C 1990, S&O 1972, etc.) come in
    three flavors:

    1. **Single-word in-line gloss** — e.g.,
       ``mag-aaral (estudyante)`` (R&G 1981 Intermediate
       PAG-AARAL/sent-13). Parens enclose a synonym (often an
       English / Spanish-loan equivalent) as a translator's gloss.
       Metalinguistic; not part of the syntactic structure. The
       pass drops the parens AND the contents.

    2. **Sentence-wrap** — e.g., ``(Kaibigan ko siya.)`` (R&G 1981
       Conversational page-13/prose/sent-1), ``(Nagkita sa daan
       ang magkaibigan.)`` (R&G 1981 Intermediate page-13). Parens
       wrap an entire example sentence as a presentation device.
       The pass drops the parens, keeps the content.

    3. **Morpheme-decomposition notation** — e.g., ``(mang+bili)``
       (R&C 1990 Ch5 Exercise/sent-155). Parens enclose linguistic-
       analysis notation. Content preserved (parens stripped); the
       inner notation typically doesn't parse, but no regression
       from the bare-text baseline.

    Discrimination: a paren region whose inner content matches
    a single word (``\\w[\\w-]*``) is treated as case 1 and
    stripped entirely; all other contents are preserved (parens
    stripped, content kept).

    The pass is whitespace-folding: any run of whitespace around a
    paren region collapses to a single space, and a global
    final collapse removes any extra spaces introduced by the
    substitution.
    """
    def _replace(m: re.Match[str]) -> str:
        inner = m.group(1)
        if _SINGLE_WORD.fullmatch(inner):
            return " "
        return f" {inner} "

    out = _PAREN_REGION.sub(_replace, text)
    return re.sub(r"\s+", " ", out).strip()


def tokenize(s: str) -> list[Token]:
    out: list[Token] = []
    for m in _WORD.finditer(s.strip()):
        t = m.group(0)
        # Strip INTERNAL hyphens from the norm (so the analyzer's
        # surface index, keyed on hyphen-free forms, finds tokens
        # like ``Nag-uusap`` via norm ``naguusap``). Bare hyphens
        # (length-1 ``-`` tokens) keep their norm as ``-`` so the
        # punctuation / arithmetic-minus path still sees them.
        # All-hyphen runs (``--`` / ``---``; the em-dash surrogate
        # added 9.X.c25) preserve their literal norm so the PUNCT
        # lex entry for ``--`` can match.
        if len(t) > 1 and "-" in t and t != "-" * len(t):
            norm = t.lower().replace("-", "")
        else:
            norm = t.lower()
        out.append(Token(surface=t, norm=norm, start=m.start(), end=m.end()))
    return out
