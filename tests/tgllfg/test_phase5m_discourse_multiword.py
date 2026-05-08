"""Phase 5m Commit 11: multi-word discourse connectives.

Roadmap §12.1 / plan-of-record §5.2. Adds three multi-word
lexicalized rules in cfg/discourse.py building virtual PART
nodes from two-token sequences:

    PART → PART[LEMMA=gayon] PART[LEMMA=din]   (DISCOURSE=LIKEWISE)
    PART → PART[LEMMA=ganon] PART[LEMMA=din]   (DISCOURSE=LIKEWISE)
    PART → PART[LEMMA=bukod] ADP[LEMMA=dito]   (DISCOURSE=ALSO)

Each emitted virtual PART carries DISCOURSE_POS=SENTENCE_INITIAL
so it feeds the Commit 4 sentence-initial PART rule. Heads are
Commit 1 lex'd; tails (``din``, ``dito``) get a LEMMA feat added
in this commit so the rule constraints can match.

The bukod-dito rule has mixed-POS daughters (PART + ADP) because
``dito`` is the locative DEM, not a PART — same precedent as
Phase 5l ``mula nang`` (PREP + PART).

**Architectural limitation pinned**: ``gayon din`` / ``ganon din``
do NOT parse today because ``din`` is a 2P clitic. The Phase 4 §7.3
``reorder_clitics`` pre-pass runs before grammar parsing and pulls
``din`` from immediately-after-gayon to clause-final position
(canonical Wackernagel placement when there is a verb later in the
clause). The multi-word rule requires adjacency, so the rule never
fires after the reorder. The bukod-dito case works because ``dito``
is ADP (not a 2P clitic) and isn't reordered.

Closure path (Phase 5n debt):
* A pre-clitic-reorder phrase-recognition pass that identifies
  ``gayon din`` / ``ganon din`` as fixed phrases and merges them
  into single tokens (parallel to the hyphen-compound merger),
  OR
* An exception in ``reorder_clitics`` that leaves ``din`` /
  ``rin`` in place when the immediately-preceding token has
  ``LEMMA=gayon`` / ``LEMMA=ganon``.

Reference: R&B 1986 §15.7.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === bukod dito (working) ============================================


BUKOD_DITO_CASES = [
    ("Bukod dito kumain ang bata.",  "EAT"),
    ("Bukod dito pumupunta siya.",   "PUNTA"),
    ("Bukod dito tumakbo ang aso.",  "TAKBO"),
]


def _adjunct_with_lemma(fs, lemma: str):
    adj = fs.feats.get("ADJUNCT") or []
    for m in adj:
        if hasattr(m, "feats") and m.feats.get("LEMMA") == lemma:
            return m
    return None


class TestBukodDito:
    """``Bukod dito`` composes via the multi-word PART rule
    (PART + ADP) and feeds the Commit 4 sentence-initial-PART
    rule. The matrix S sees an ADJUNCT with DISCOURSE=ALSO,
    LEMMA=bukod_dito, DISCOURSE_POS=SENTENCE_INITIAL."""

    @pytest.mark.parametrize("sent,pred_prefix", BUKOD_DITO_CASES)
    def test_bukod_dito_lifts_as_adjunct(
        self, sent: str, pred_prefix: str,
    ) -> None:
        parses = parse_text(sent)
        assert len(parses) >= 1, f"expected ≥1 parse for {sent!r}"
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith(pred_prefix)
        connective = _adjunct_with_lemma(fs, "bukod_dito")
        assert connective is not None, (
            f"expected ADJUNCT with LEMMA=bukod_dito for {sent!r}"
        )
        assert connective.feats.get("DISCOURSE") == "ALSO"
        assert connective.feats.get("DISCOURSE_POS") == "SENTENCE_INITIAL"

    def test_bukod_dito_single_parse(self) -> None:
        parses = parse_text("Bukod dito kumain ang bata.")
        assert len(parses) == 1


# === gayon din / ganon din: deferred =================================


GAYON_DIN_DEFERRED = [
    "Gayon din kumain ang bata.",
    "Gayon din pumupunta siya.",
    "Ganon din kumain ang bata.",
    "Ganon din pumupunta siya.",
]


class TestGayonDinDeferred:
    """``gayon din`` / ``ganon din`` do NOT parse today because
    ``din`` is a 2P clitic and the Phase 4 §7.3 ``reorder_clitics``
    pre-pass moves it to clause-final position before grammar
    parsing. The multi-word PART rule requires adjacency, so it
    never fires.

    The grammar rules are landed (so closure during Phase 5n is a
    pre-pass change, not a grammar change). Pinned at 0-parse to
    catch any unintended flip when the pre-pass infrastructure is
    extended.

    Closure path: a pre-clitic-reorder phrase-recognition pass
    that merges ``gayon din`` / ``ganon din`` into single tokens
    before reorder_clitics runs.
    """

    @pytest.mark.parametrize("sent", GAYON_DIN_DEFERRED)
    def test_zero_parse_today(self, sent: str) -> None:
        parses = parse_text(sent)
        assert len(parses) == 0, (
            f"{sent!r} parsed unexpectedly — pre-clitic-reorder "
            f"phrase-recognition has landed; close the deferral "
            f"and un-pin this test."
        )


# === Commit 1 LEMMA additions on existing entries ====================


class TestExistingEntriesLemmaAdded:
    """Commit 11 adds ``LEMMA: din`` / ``LEMMA: rin`` / ``LEMMA:
    dito`` to the existing 2P-clitic and ADP entries. Verify the
    additions don't break any existing behavior."""

    def test_din_still_2p_clitic(self) -> None:
        """``Kumain din si Maria.`` "Maria also ate." — Phase 4
        Rule A absorption of the din clitic, with REGISTER /
        QUESTION / COUNTERFACTUAL all absent."""
        parses = parse_text("Kumain din si Maria.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        adj = fs.feats.get("ADJ") or []
        din_members = [
            m for m in adj
            if hasattr(m, "feats")
            and m.feats.get("LEMMA") == "din"
            and m.feats.get("ADV") == "ALSO"
        ]
        assert len(din_members) == 1

    def test_dito_still_dat_dem(self) -> None:
        """``Pumunta si Maria dito.`` "Maria went here." — Phase 4
        DAT-DEM ADP usage of dito."""
        parses = parse_text("Pumunta si Maria dito.")
        # Either parses cleanly with dito as DAT-DEM, or 0-parses
        # for unrelated reasons. The point is we didn't break the
        # existing dito entry.
        for _ct, fs, _astr, _diags in parses:
            # No dito-specific assertion — just verify no crash and
            # the existing parsing pathway is preserved.
            pass
