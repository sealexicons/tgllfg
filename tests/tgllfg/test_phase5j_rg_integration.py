"""Phase 5j Commit 9: R&G "Ang Manok" integration benchmark.

Roadmap §12.6 / plan-of-record §8, §6 Commit 9. Verifies the
Phase 5g + Phase 5j coverage of the R&G 1981 p. 482 "Ang Manok"
essay-paragraph integration benchmark — seven simple sentences
that combine into one complex narrative paragraph.

Status by simple (per the benchmark's per-phase plan):

  #1 May isang mamang nakatira sa isang bahay sa bukid.
        BLOCKED — needs ``mama`` lex, ``mag-isa`` ADV
        (tokenizer hyphen-split), ``nakatira`` resultative
        ``naka-`` paradigm. Phase 5j follow-on.

  #2 Matanda siya.                          ✓ Phase 5g (adj-pred)
  #3 Nakatira siyang mag-isa sa bahay.      BLOCKED (same as #1)
  #4 Maliit ang bahay.                      ✓ Phase 5g (adj-pred)
  #5 Nasa bundok ang bahay.                 ✓ Phase 5j Commit 4
  #6 Mataas ang bundok.                     ✓ Phase 5g (adj-pred)
  #7 Nasa tuktok ng bundok ang bahay.       ✓ Phase 5j Commit 4

This commit confirms that simples #5 and #7 land cleanly with
the Phase 5j Commit 4 locative-existential rules (base form
and possessor-of-ground variant) and that the four Phase 5g
simples continue to parse alongside.

Combined essay-paragraph sentence (R&G p. 482) remains pending
on the deferred items above.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Phase 5g simples (still parse) ====================================


PHASE_5G_SIMPLES = [
    # (sentence, simple_number, expected_pred_prefix)
    ("Matanda siya.",      2, "ADJ"),
    ("Maliit ang bahay.",  4, "ADJ"),
    ("Mataas ang bundok.", 6, "ADJ"),
]


class TestPhase5gSimpleSentences:
    """The four Phase 5g adjective-predicate R&G simples
    (#2, #4, #6) still parse as predicative-ADJ clauses."""

    @pytest.mark.parametrize("sentence,simple_num,expected_pred", PHASE_5G_SIMPLES)
    def test_phase5g_simple_parses(
        self, sentence: str, simple_num: int, expected_pred: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"R&G simple #{simple_num} {sentence!r} should parse"
        )
        adj_parses = [
            p for p in parses
            if (p[1].feats.get("PRED") or "").startswith(expected_pred)
        ]
        assert len(adj_parses) >= 1, (
            f"R&G simple #{simple_num} expected predicative-{expected_pred} "
            f"matrix; got {[p[1].feats.get('PRED') for p in parses]}"
        )


# === Phase 5j simples (newly unblocked) ==============================


class TestPhase5jSimple5:
    """R&G simple #5: ``Nasa bundok ang bahay.`` — base locative-
    existential rule (Phase 5j Commit 4)."""

    def test_simple_5_parses_as_loc_existential(self) -> None:
        parses = parse_text("Nasa bundok ang bahay.")
        assert len(parses) >= 1
        loc_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "LOC_EXISTENTIAL"
        ]
        assert len(loc_parses) >= 1
        _ct, fs, _astr, _diags = loc_parses[0]
        assert fs.feats.get("PRED") == "LOC <SUBJ>"
        # SUBJ = bahay (the figure)
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "bahay"
        # LOCATION = bundok (the ground)
        loc = fs.feats.get("LOCATION")
        assert loc is not None
        assert loc.feats.get("LEMMA") == "bundok"


class TestPhase5jSimple7:
    """R&G simple #7: ``Nasa tuktok ng bundok ang bahay.`` —
    possessor-of-ground variant (Phase 5j Commit 4)."""

    def test_simple_7_parses_as_loc_existential(self) -> None:
        parses = parse_text("Nasa tuktok ng bundok ang bahay.")
        assert len(parses) >= 1
        loc_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "LOC_EXISTENTIAL"
        ]
        assert len(loc_parses) >= 1
        _ct, fs, _astr, _diags = loc_parses[0]
        assert fs.feats.get("PRED") == "LOC <SUBJ>"
        # SUBJ = bahay (the figure)
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "bahay"
        # LOCATION = tuktok (the head of the locative ground)
        loc = fs.feats.get("LOCATION")
        assert loc is not None
        assert loc.feats.get("LEMMA") == "tuktok"
        # POSS on LOCATION = bundok (possessor of tuktok)
        poss = loc.feats.get("POSS")
        assert poss is not None
        assert poss.feats.get("LEMMA") == "bundok"


# === Cross-simple composition: #5 + #6 sub-essay slice =================


class TestRgEssaySliceComposability:
    """The R&G "Ang Manok" essay sentence combines the seven
    simples. While the full combination needs the deferred
    morphology, smaller slices that combine ONLY the Phase
    5g + 5j simples should also parse. This test verifies a
    sub-essay slice — ``Nasa mataas na bundok ang bahay.``
    "The house is on the high mountain" — combining simple #5's
    locative existential + simple #6's adjective modifier."""

    def test_locative_with_adj_modified_ground(self) -> None:
        """``Nasa mataas na bundok ang bahay.`` — adj-modified N
        as locative ground. The Phase 5g NP-internal modifier
        rules project ``mataas na bundok`` to N; the Phase 5j
        Commit 4 base rule consumes that N as the locative
        ground.
        """
        parses = parse_text("Nasa mataas na bundok ang bahay.")
        assert len(parses) >= 1
        loc_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "LOC_EXISTENTIAL"
        ]
        assert len(loc_parses) >= 1
        _ct, fs, _astr, _diags = loc_parses[0]
        assert fs.feats.get("PRED") == "LOC <SUBJ>"
        # Ground head is bundok (with mataas as ADJ-MOD)
        loc = fs.feats.get("LOCATION")
        assert loc is not None
        assert loc.feats.get("LEMMA") == "bundok"


# === R&G simples #1 / #3 — unblocked by Phase 5n.A Commits 5–7 ============
#
# Phase 5j pinned simples #1 and #3 at 0-parse pending three
# blockers (``nakatira`` resultative, ``mag-isa`` hyphen
# tokenization, ``mama`` lex). All three landed in Phase 5n.A:
#
#   * Commit 5 — ``mag-isa`` ADV tokenizer hyphen-split (§18 L60)
#   * Commit 6 — ``nakatira`` resultative ``naka-`` ADJ paradigm
#                (§18 L61)
#   * Commit 7 — ``mama`` NOUN lex + depictive secondary-predicate
#                rule (``NP[CASE=NOM] → PRON[CASE=NOM] PART[LINK=NG]
#                ADV[MAGISA=YES]``) (§18 L62 + L63)
#
# Positive integration tests for both simples now live in
# ``test_phase5n_rg_simples.py``. The combined essay-paragraph
# (R&G p. 482) is Commit 8's target.


class TestRgSimples1And3UnblockedInPhase5nA:
    """Pin that R&G simples #1 and #3 now parse, asserting the
    Phase 5n.A Commits 5-7 chain delivered the §18 L60 / L61 /
    L62 / L63 closures. If a future change re-breaks these,
    this is the regression detector."""

    @pytest.mark.parametrize("sentence,simple_num", [
        ("May isang mamang nakatira sa isang bahay sa bukid.", 1),
        ("Nakatira siyang mag-isa sa bahay.", 3),
    ])
    def test_unblocked_simple_parses(
        self, sentence: str, simple_num: int
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"R&G simple #{simple_num} {sentence!r} regressed to "
            f"0-parse — Phase 5n.A Commits 5-7 chain may have been "
            f"reverted; check mag-isa ADV / nakatira ADJ / mama NOUN / "
            f"depictive PRON+linker+ADV rule."
        )
