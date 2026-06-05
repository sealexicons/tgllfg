# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.A Commit 17 — Coordinated cardinals (§18 L79).

Adds a NUM-level coord rule to ``cfg/coordination.py`` that admits
two cardinals joined by ``at`` (or the bound ``'t`` clitic, via the
Phase 5k Commit 2 ``split_apostrophe_t`` pre-pass) as a single
NUM[CARDINAL=YES] node, recording both operand values and a
COORD_OP=SUM marker for downstream consumers.

The unifier's equation language has no arithmetic primitive — Atom
and Designator are the only value types. So the matrix CARDINAL_VALUE
isn't computed here; instead the rule records OPERAND_1 / OPERAND_2 /
COORD_OP=SUM (matching the Phase 5f Commit 9 arithmetic-predicates
precedent), and downstream consumers compute the sum from the
operand feats. A computed CARDINAL_VALUE would require either
extending the equation language or adding a post-unification
projection pass — both larger scope than this single L79 closure.

Surfaces that work:

* ``apatnapu't limang aklat`` 45 = 40 + 5
* ``dalawampu't limang aklat`` 25 = 20 + 5
* ``tatlumpu't tatlong aklat`` 33 = 30 + 3
* ``sandaan at dalawampung aklat`` 120 = 100 + 20
* ``sanlibo at limampu't tatlong aklat`` 1053 = 1000 + 53 (3-level)

Surfaces NOT covered (out of L79 scope):

* ``sandaa't dalawampu`` 120 — requires truncated ``sandaa`` lex
  (n-final ``sandaan`` drops final n before ``'t``). Separate
  sandhi/lex item.
* ``apat na pu't lima`` 45 — requires multi-word ``apat na pu`` →
  ``apatnapu`` collapse (per Phase 5f comment, single-token spelling
  is canonical; multi-word spellings are deferred).
"""

import pytest

from tgllfg.core.pipeline import parse_text


# === Two-level coord cardinals (decade + unit) ============================


class TestTwoLevelCoord:
    """The 't pre-pass + the new NUM-coord rule produce CARDINAL=YES
    on decade + unit compositions."""

    @pytest.mark.parametrize("sentence", [
        "Bumili ako ng apatnapu't limang aklat.",     # 45
        "Bumili ako ng dalawampu't limang aklat.",    # 25
        "Bumili ako ng tatlumpu't tatlong aklat.",    # 33
        "Bumili ako ng limampu't anim na aklat.",     # 56
        "Bumili ako ng walumpu't isang aklat.",       # 81
    ])
    def test_decade_unit_coord(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === Two-level coord with `at` (no contraction) ===========================


class TestAtCoord:
    """Coord cardinals using the standalone ``at`` (no ``'t``
    contraction) work for any host shape — including n-final
    hundreds."""

    @pytest.mark.parametrize("sentence", [
        "Bumili ako ng sandaan at dalawampung aklat.",  # 120
        "Bumili ako ng sanlibo at sandaang aklat.",     # 1100
        "Mayroon akong sandaan at dalawampung aklat.",  # 120 + HAVE
    ])
    def test_at_coord_cardinals(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === Three-level coord ====================================================


class TestThreeLevelCoord:
    """Coord cardinals can stack via right-recursion through the
    NUM-coord rule (e.g., 1000 + (50 + 3) = 1053)."""

    def test_thousand_decade_unit(self) -> None:
        # sanlibo at (limampu't tatlo) = 1000 + 53
        parses = parse_text(
            "Bumili ako ng sanlibo at limampu't tatlong aklat."
        )
        assert len(parses) >= 1


# === Note on OPERAND_1 / OPERAND_2 / COORD_OP propagation =================
#
# The new NUM-coord rule sets ``COORD_OP = 'SUM'`` and records
# ``OPERAND_1 = ↓1 CARDINAL_VALUE`` / ``OPERAND_2 = ↓3 CARDINAL_VALUE``
# on the matrix NUM[CARDINAL=YES] node. However, the Phase 5f
# Commit 1 cardinal-NP-modifier rule
# (``NP → DET[CASE=GEN] NUM[CARDINAL=YES] PART[LINK=N{A,G}] N``)
# only lifts ``CARDINAL_VALUE`` from the NUM daughter to the matrix
# NP — not COORD_OP / OPERAND_1 / OPERAND_2. So the operand feats
# don't surface at the NP level.
#
# Lifting them would require widening the cardinal-NP-modifier rule's
# projection in cfg/nominal.py, which is broader scope (the NP-from-N
# projection is a known L32 deferral — Phase 6 FU-extension territory).
# For L79 closure, the parse-success of ``apatnapu't limang aklat`` is
# the user-visible target; the COORD_OP feats would ride on the inner
# NUM if the projection were widened later.


# === Plain cardinal regression ============================================


class TestPlainCardinalRegression:
    """Single (non-coord) cardinals continue to parse — the new
    NUM-coord rule only fires on the 3-daughter shape."""

    @pytest.mark.parametrize("sentence", [
        "Bumili ako ng limang aklat.",      # 5
        "Bumili ako ng sampung aklat.",     # 10
        "Bumili ako ng dalawampung aklat.", # 20
        "Bumili ako ng sandaang aklat.",    # 100
        "Bumili ako ng sanlibong aklat.",   # 1000
    ])
    def test_plain_cardinal_still_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
