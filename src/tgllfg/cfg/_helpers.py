# tgllfg/cfg/_helpers.py

"""Private utilities shared across the per-area rule modules.

This module is the home for constants and helpers that are used by
more than one rule module after the post-Phase-5f split (see
``docs/refactor-grammar-package.md``). Anything used by exactly one
rule module should live in that module; promote here only when a
second consumer appears.

Currently exports:

* ``_VERB_PERCOLATION`` — the canonical equation tuple every clausal
  rule emits to percolate the verb's lexical features (PRED, VOICE,
  ASPECT, MOOD, LEX-ASTRUCT) up to the matrix f-structure. ``↓1`` is
  always the verb in the V-initial S frames, so the equations are
  identical across rules.
* ``_eqs`` — equation-list builder: verb percolation followed by the
  rule-specific extras passed by the caller. Used 100+ times in the
  Phase 4 / 5 / 5f rule corpus; the only contract is that ``↓1`` is
  the verb.
"""

from __future__ import annotations

# Equations every clausal rule emits to percolate verb features up to
# the matrix f-structure. ``↓1`` is always the verb in our V-initial
# rules.
_VERB_PERCOLATION: tuple[str, ...] = (
    "(↑ PRED) = ↓1 PRED",
    "(↑ VOICE) = ↓1 VOICE",
    "(↑ ASPECT) = ↓1 ASPECT",
    "(↑ MOOD) = ↓1 MOOD",
    "(↑ LEX-ASTRUCT) = ↓1 LEX-ASTRUCT",
)


def _eqs(*extras: str) -> list[str]:
    """Build an equation list: verb percolation followed by extras."""
    return [*_VERB_PERCOLATION, *extras]
