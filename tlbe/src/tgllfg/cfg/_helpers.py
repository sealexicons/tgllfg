# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

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

**Contract — ``↓1`` must be the verb.** ``_eqs`` is for V-initial clausal
rules only. A head-sharing *non-verb* lift (``AdvP → ADV``, ``PP → PREP
NP``, the post-modifier-DEM ``NP → NP PART DET[DEM]`` family, ``S_GAP →
S_GAP PP``) already unifies the daughter onto the matrix via ``(↑) = ↓1``,
which shares every feature the daughter actually carries. Routing such a
rule through ``_eqs`` then *also* copies the five verb features from a
daughter that has none of them — and ``(↑ PRED) = ↓1 PRED`` against an
undefined source auto-vivifies an **empty** ``PRED`` / ``VOICE`` /
``ASPECT`` / ``MOOD`` / ``LEX-ASTRUCT`` f-node on the lifted phrase (a
fronted ADV's TOPIC, a PP ADJUNCT, a demonstrative-marked SUBJ). Phase
14.final.post-13 stripped ``_eqs`` from every such head-sharing lift; use
a plain equation list there, never ``_eqs``.
"""

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
