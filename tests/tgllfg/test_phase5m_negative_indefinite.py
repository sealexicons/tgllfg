"""Phase 5m Commit 9: negative-indefinite ``walang sinuman``.

Roadmap §12.1 / plan-of-record §1. Wires the Commit 1 PRON entry
``sinuman`` (INDEF=NEG_INDEF) into the existing Phase 5j negative-
existential frame. Adds one new rule in cfg/clause.py:

    S → PART[EXISTENTIAL=YES, POLARITY=NEG]
        PART[LINK=NG]
        PRON[INDEF=NEG_INDEF]

This mirrors the existing Phase 5j ``walang N`` rule with a
PRON daughter constrained to ``INDEF=NEG_INDEF`` (so generic
PRONs like ``siya`` / ``niya`` don't fire here).

Plan deviation from §1: plan said "Phase 5m only adds the lex
entry for sinuman; no new grammar". That was wrong — the
existing Phase 5j ``walang N`` rule constrains specifically on
``N`` daughter and doesn't admit PRONs. The minimum delta is
one new rule; this commit adds it.

Coverage:
* ``Walang sinuman.`` "There is no one." — basic neg-indef
  existential; SUBJ.LEMMA=sinuman, SUBJ.INDEF=NEG_INDEF, matrix
  PRED=EXIST, POLARITY=NEG, CLAUSE_TYPE=EXISTENTIAL.
* Phase 5j ``walang N`` baseline preserved
  (``Walang bata.`` / ``Walang aklat.``).

Deferrals pinned:
* ``Walang sinumang dumating.`` — sinuman + bound -ng linker +
  V[finite] (relative-clause complement of sinuman). Needs the
  existing Phase 4 §7.5 N-headed relative-clause rule extended
  to PRON-headed RCs, or a parallel sinuman-specific rule.
  Phase 5n debt.
* ``Walang ano man.`` — productive ``wh-PRON + man`` indef-
  builder is a separate analytical commitment (one possibility:
  ``PRON[INDEF=NEG_INDEF] → PRON[WH=YES] PART[man, ADV=EVEN]``).
  ``anuman`` (lexicalized contracted form) is also unlex'd.
  Phase 5n debt.

Reference: R&G 1981 §6.6.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === walang sinuman ===================================================


class TestWalangSinuman:
    """``Walang sinuman.`` "There is no one." parses via the new
    PRON-variant rule."""

    def test_walang_sinuman_basic(self) -> None:
        parses = parse_text("Walang sinuman.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "EXIST <SUBJ>"
        assert fs.feats.get("POLARITY") == "NEG"
        assert fs.feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "sinuman"
        assert subj.feats.get("INDEF") == "NEG_INDEF"

    def test_walang_sinuman_single_parse(self) -> None:
        parses = parse_text("Walang sinuman.")
        assert len(parses) == 1


# === Phase 5j baseline preservation ===================================


PHASE_5J_BASELINE = [
    "Walang bata.",
    "Walang aklat.",
]


class TestPhase5jWalangBaseline:
    """The existing Phase 5j ``walang N`` rule is NOT broken by
    the new PRON-variant rule. Baseline existential-negation
    sentences still parse cleanly."""

    @pytest.mark.parametrize("sent", PHASE_5J_BASELINE)
    def test_walang_n_still_parses(self, sent: str) -> None:
        parses = parse_text(sent)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "EXIST <SUBJ>"
        assert fs.feats.get("POLARITY") == "NEG"


# === Selectional restriction: generic PRONs don't fire ================


class TestSelectionalRestriction:
    """The new rule constrains on ``(↓3 INDEF) =c 'NEG_INDEF'``,
    so generic PRONs (``siya`` / ``niya`` / ``ako``) don't form
    spurious ``Walang siya.`` / ``Walang niya.`` parses via this
    rule."""

    def test_walang_siya_zero_parse(self) -> None:
        """``Walang siya.`` is ungrammatical and 0-parses (no
        rule admits ``walang`` + 3sg-NOM PRON)."""
        parses = parse_text("Walang siya.")
        assert len(parses) == 0

    def test_walang_ako_zero_parse(self) -> None:
        parses = parse_text("Walang ako.")
        assert len(parses) == 0


# === Deferrals ========================================================


class TestNegativeIndefiniteDeferred:
    """Two construction families pinned at 0-parse for Phase 5n
    debt-clearing.

    1. ``Walang sinumang dumating.`` — sinuman + bound -ng linker
       + V[finite] relative-clause complement of the indef PRON.
       Needs the Phase 4 §7.5 N-headed RC rule extended to
       PRON-headed RCs (``PRON → PRON PART[LINK=NG] V[+finite]``)
       or a parallel sinuman-specific rule.

    2. ``Walang ano man.`` — productive ``wh-PRON + man`` indef-
       builder. Possible closure path:
       ``PRON[INDEF=NEG_INDEF] → PRON[WH=YES] PART[man,ADV=EVEN]``
       which would compose ``ano man`` into a virtual neg-indef
       PRON, then feed the new walang+PRON rule. ``anuman``
       (lexicalized contracted form) is also unlex'd — adding
       it as PRON[INDEF=NEG_INDEF] would unblock that surface.
    """

    def test_walang_sinumang_dumating_zero_parse(self) -> None:
        parses = parse_text("Walang sinumang dumating.")
        assert len(parses) == 0, (
            "Walang sinumang dumating. parsed unexpectedly — "
            "PRON-headed relative-clause infrastructure has "
            "landed; close the deferral and un-pin."
        )

    def test_walang_ano_man_zero_parse(self) -> None:
        parses = parse_text("Walang ano man.")
        assert len(parses) == 0, (
            "Walang ano man. parsed unexpectedly — wh-PRON+man "
            "indef-builder has landed; close the deferral and "
            "un-pin."
        )
