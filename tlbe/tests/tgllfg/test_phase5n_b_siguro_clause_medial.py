# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.B Commit 18: clause-medial siguro / marahil (§18 L98).

Closes §18.1 deferral L98. Target sentences:

    Pumupunta siguro siya.   "He's probably going."
    Pumupunta marahil siya.  "He's probably going (formal)."
    Kumain siguro ang aso.   "The dog probably ate."

Two changes:

* ``data/tgl/particles.yaml``: add a polysemous second entry
  for each of ``siguro`` and ``marahil``:

    siguro / marahil  (PART[DISCOURSE_POS=SENTENCE_INITIAL])  — original
    siguro / marahil  (PART[CLITIC_CLASS=2P, is_clitic=true]) — new

  The existing Phase 5m discourse-initial entry remains; the
  new entry feeds the Phase 4 §7.3 generic 2P-clitic absorption
  (cfg/clitic.py Rule A) for clause-medial usage. Pattern
  parallels other Phase 5l/5m polysemy resolutions (kung — COND
  vs INTERROG; hindi — PART vs PRON in Phase 5n.B C17).

* ``src/tgllfg/clitics/placement.py``: add a pre-anchor
  sentence-initial particle skip in the ``adv_indices`` filter.
  Without this, the placement engine would treat clause-initial
  ``siguro`` / ``marahil`` as a 2P-clitic and reorder it to
  post-anchor — breaking the existing Phase 5m clause-initial
  parse path. The new gate (``not (i < anchor_idx and
  _is_sentence_initial_particle(cands))``) preserves the
  clause-initial position when a sentence-initial reading is
  present.

Disambiguation: rule context picks at parse time —
clause-initial siguro/marahil consumes the SENTENCE_INITIAL
entry; clause-medial consumes the 2P-clitic entry.

The ``CLITIC_CLASS=2P`` entry's ``EPISTEMIC=PROBABLY`` feat
ends up on the ADJ daughter (sub-FStructure), not lifted to
matrix top-level (Rule A doesn't lift custom feats — it only
adds the daughter to the ADJ set). Tests check ADJ contents
rather than matrix-top-level EPISTEMIC.
"""

import pytest

from tgllfg.core.pipeline import parse_text


def _has_epistemic_in_adj(fs, lemma: str) -> bool:
    """Return True if the matrix's ADJ set contains an entry with
    LEMMA==lemma and EPISTEMIC='PROBABLY'."""
    adj = fs.feats.get("ADJ") or set()
    for m in adj:
        if (
            getattr(m, "feats", {}).get("LEMMA") == lemma
            and getattr(m, "feats", {}).get("EPISTEMIC") == "PROBABLY"
        ):
            return True
    return False


# === Clause-medial siguro / marahil ===================================


class TestClauseMedial:
    """Clause-medial 2P-clitic position: V + siguro/marahil + SUBJ.
    The Phase 4 §7.3 Rule A generic 2P-clitic absorption fires."""

    @pytest.mark.parametrize("sentence,lemma", [
        ("Pumupunta siguro siya.",       "siguro"),
        ("Pumupunta marahil siya.",      "marahil"),
        ("Kumain siguro ang aso.",       "siguro"),
        ("Kumain marahil ang aso.",      "marahil"),
        ("Kakain siguro si Maria.",      "siguro"),
    ])
    def test_clause_medial_parses(
        self, sentence: str, lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert _has_epistemic_in_adj(fs, lemma), (
            f"expected EPISTEMIC=PROBABLY for lemma={lemma!r} in "
            f"matrix ADJ; got ADJ={fs.feats.get('ADJ')!r}"
        )


# === Sentence-final siguro (also enabled by 2P-clitic entry) =========


class TestSentenceFinal:
    """Sentence-final position is also admitted by the new
    2P-clitic entry — the placement engine groups all 2P clitics
    into the post-anchor cluster, so ``Pumupunta siya siguro.`` and
    ``Pumupunta siguro siya.`` are equivalent at parse time."""

    @pytest.mark.parametrize("sentence,lemma", [
        ("Pumupunta siya siguro.",   "siguro"),
        ("Pumupunta siya marahil.",  "marahil"),
    ])
    def test_sentence_final_parses(
        self, sentence: str, lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert _has_epistemic_in_adj(fs, lemma)


# === Phase 5m sentence-initial regression =============================


class TestSentenceInitialUnchanged:
    """Existing Phase 5m clause-initial siguro/marahil continues to
    parse — the placement-engine pre-anchor skip preserves the
    clause-initial position when a sentence-initial reading is
    present on the token."""

    @pytest.mark.parametrize("sentence", [
        "Siguro pumupunta siya.",
        "Marahil pumupunta siya.",
        "Siguro kumakain ang bata.",
        "Marahil kumakain ang bata.",
    ])
    def test_clause_initial(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # The clause-initial path puts the particle in ADJUNCT
        # (Phase 5m) or ADJ (the new 2P-clitic absorption — happens
        # because the placement engine doesn't reorder, but Rule A
        # still composes if there's a way for it to fire). Either
        # placement must hold the EPISTEMIC marker somewhere.
        # Walk both ADJUNCT and ADJ to find it.
        for slot in ("ADJUNCT", "ADJ"):
            members = fs.feats.get(slot) or set()
            for m in members:
                if (
                    getattr(m, "feats", {}).get("EPISTEMIC") == "PROBABLY"
                ):
                    return  # found
        pytest.fail(
            f"expected EPISTEMIC=PROBABLY somewhere in matrix's "
            f"ADJUNCT or ADJ for {parses[0][1].feats!r}"
        )
