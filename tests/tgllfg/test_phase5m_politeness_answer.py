"""Phase 5m Commit 3: politeness ``opo`` / ``oho`` interjection-answer.

Roadmap §12.1 / plan-of-record §1 (politeness particles, third
sub-family). The Phase 5m Commit 1 lex entries

* ``opo``  — PRON[PRED='YES', INTERJ=YES, ANSWER=AFFIRM, REGISTER=POLITE]
* ``oho``  — PRON[PRED='YES', INTERJ=YES, ANSWER=AFFIRM, REGISTER=COLLOQUIAL_POLITE]

are fused affirmative-answer interjections (``opo`` = ``oo`` +
``po``; ``oho`` = ``oo`` + ``ho``). They form one-word answer
clauses via a new fragment-answer rule in ``cfg/clause.py``:

    S → PRON
        (↑) = ↓1
        (↑ INTERJ) =c 'YES'
        (↑ ANSWER) =c 'AFFIRM'
        (↑ CLAUSE_TYPE) = 'FRAGMENT_ANSWER'

The PRON's REGISTER lifts to the matrix S via ``(↑) = ↓1``.

Plan deviation from §1: the plan claimed ``opo`` / ``oho`` would
compose "via the existing fragment-answer mechanism (parallel to
``oo`` / ``hindi`` PRON entries)". That was wrong on three counts:
(i) ``oo`` was not lex'd at all (verified 2026-05-07; remains
deferred to Phase 5n); (ii) ``hindi`` is PART[POLARITY=NEG], not
PRON[INTERJ=YES]; (iii) there was no fragment-answer matrix-S rule
to compose against. Building the rule (5 lines) is preferable to
reducing scope to lex-only delivery (the Phase 5l Commit 10/11
precedent).

Coverage:
* ``Opo.`` parses with PRED='YES', REGISTER=POLITE,
  CLAUSE_TYPE=FRAGMENT_ANSWER.
* ``Oho.`` parses with PRED='YES', REGISTER=COLLOQUIAL_POLITE.
* The fragment-answer rule does NOT fire on ordinary PRONs
  (``Siya.``, ``Maria.``) — those lack INTERJ=YES.
* ``Oo.`` / ``Hindi.`` 0-parse (deferred — needs new lex entries
  + INTERJ-tagged readings; Phase 5n debt).
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Opo / Oho fragment-answer parses =================================


OPO_OHO_CASES = [
    # (sentence, expected_register)
    ("Opo.", "POLITE"),
    ("Oho.", "COLLOQUIAL_POLITE"),
]


class TestPolitenessAnswer:
    """``Opo.`` and ``Oho.`` form fragment-answer clauses."""

    @pytest.mark.parametrize("sent,register", OPO_OHO_CASES)
    def test_fragment_answer_clause(
        self, sent: str, register: str,
    ) -> None:
        parses = parse_text(sent)
        assert len(parses) >= 1, f"expected ≥1 parse for {sent!r}"
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "YES", (
            f"expected PRED='YES' for {sent!r}; got "
            f"{fs.feats.get('PRED')!r}"
        )
        assert fs.feats.get("CLAUSE_TYPE") == "FRAGMENT_ANSWER"
        assert fs.feats.get("INTERJ") == "YES"
        assert fs.feats.get("ANSWER") == "AFFIRM"
        assert fs.feats.get("REGISTER") == register


class TestSingleParse:
    """``Opo.`` and ``Oho.`` produce exactly one parse — the new
    fragment-answer rule doesn't double-fire."""

    def test_opo_single_parse(self) -> None:
        parses = parse_text("Opo.")
        assert len(parses) == 1

    def test_oho_single_parse(self) -> None:
        parses = parse_text("Oho.")
        assert len(parses) == 1


# === Selectional restriction: rule fires only on INTERJ=YES PRONs ====


class TestSelectionalRestriction:
    """The fragment-answer rule constrains on ``(↑ INTERJ) =c 'YES'``,
    so ordinary PRONs (``siya``, ``Maria`` would-be-PRON, etc.)
    don't form one-word clauses via this rule. Ordinary PRONs lack
    INTERJ, so the constraint fails. (Note: ``Siya.`` / ``Maria.``
    might 0-parse for unrelated reasons too; these tests just
    pin the negative as a regression marker.)"""

    def test_bare_pronoun_not_fragment_answer(self) -> None:
        """A bare 3SG-NOM pronoun does NOT form a fragment-answer
        S via the new rule (it lacks INTERJ=YES)."""
        parses = parse_text("Siya.")
        # Either 0 parses, or any parse that exists has CLAUSE_TYPE
        # ≠ FRAGMENT_ANSWER (no false-positive from the new rule).
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("CLAUSE_TYPE") != "FRAGMENT_ANSWER"


# === Deferred: Oo. / Hindi. ===========================================


DEFERRED_FRAGMENT_ANSWERS = [
    "Oo.",
    "Hindi.",
]


class TestOoHindiDeferred:
    """``Oo.`` ("yes") and ``Hindi.`` ("no") as standalone fragment-
    answer clauses are NOT in Phase 5m scope.

    * ``oo`` is not lex'd (would need a new PRON[INTERJ=YES,
      ANSWER=AFFIRM] entry; orthogonal to politeness work).
    * ``hindi`` is lex'd as PART[POLARITY=NEG], not PRON. A second
      PRON[INTERJ=YES, ANSWER=NEG] entry would be needed; the
      fragment-answer rule would also need a parallel
      ``(↑ ANSWER) =c 'NEG'`` rule.

    Both items are flagged for Phase 5n debt-clearing.
    """

    @pytest.mark.parametrize("sent", DEFERRED_FRAGMENT_ANSWERS)
    def test_zero_parse_deferred(self, sent: str) -> None:
        parses = parse_text(sent)
        assert len(parses) == 0, (
            f"{sent!r} parsed unexpectedly — fragment-answer "
            f"infrastructure has been extended; close the deferral "
            f"and un-pin this test."
        )
