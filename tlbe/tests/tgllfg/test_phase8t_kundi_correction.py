# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 8.T: kundi-introduced phrasal correction.

Audit-named construction (Wave 3, S&O 1972 §7.20 page 656):
``Hindi si Juan ang darating kundi si Pedro.`` — "It's not Juan who's
coming but (rather) Pedro." A NEG-marked matrix clause (hindi-cleft
or wala-existential) admits a corrective NP/PP introduced by
``kundi`` "but, except".

Two new rules in ``cfg/coordination.py``:

  S → S[POLARITY=NEG]  PART[COORD=BUT_NOT]  NP   (NP correction)
  S → S[POLARITY=NEG]  PART[COORD=BUT_NOT]  PP   (PP correction)

The matrix f-structure is inherited from the negated clause via
``(↑) = ↓1``; the corrective NP/PP rides on the matrix's ADJUNCT
set with ``ROLE: CORRECTION`` (mirroring the Phase 5h
``EQUATIVE_STANDARD`` convention).

Distinct from the Phase 5l Commit 14 correlative-clausal-coord
``hindi lang … kundi pati S`` (which coordinates two clauses via
CONJUNCTS); this is phrasal correction inside a single matrix.

Lex addition: ``ben`` proper-name NOUN (S&O 1972 §7.20 sent
``Walang tao doon kundi si Ben.``).
"""

import pytest


def _correction_adjunct(fstructure):
    """Return the unique ADJUNCT member with ROLE=CORRECTION, or
    None if absent."""
    adj = fstructure.feats.get("ADJUNCT")
    if adj is None:
        return None
    matches = [
        m for m in adj
        if hasattr(m, "feats")
        and str(m.feats.get("ROLE")) == "CORRECTION"
    ]
    if not matches:
        return None
    assert len(matches) == 1, (
        f"expected one CORRECTION adjunct, got {len(matches)}"
    )
    return matches[0]


class TestPhase8tNpCorrection:
    """Rule (a): ``Hindi …  kundi  NP``."""

    def test_audit_hit_hindi_cleft(self) -> None:
        """S&O 1972 page 656 / sent-1290 verbatim audit closure."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Hindi si Juan ang darating kundi si Pedro.",
            n_best=3,
        )
        assert len(parses) >= 1
        # Matrix carries POLARITY=NEG (inherited from the cleft)
        # and a CORRECTION adjunct
        for _ct, f, _astr, _diags in parses:
            assert str(f.feats.get("POLARITY")) == "NEG"
            corr = _correction_adjunct(f)
            assert corr is not None, "missing CORRECTION adjunct"
            assert str(corr.feats.get("LEMMA")) == "pedro"

    def test_wala_existential_np_correction(self) -> None:
        """``Walang tao doon kundi si Ben.`` — wala-existential
        with kundi-NP correction (Ben proper-name lex add)."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Walang tao doon kundi si Ben.", n_best=3,
        )
        assert len(parses) >= 1
        f = parses[0][1]
        assert str(f.feats.get("POLARITY")) == "NEG"
        corr = _correction_adjunct(f)
        assert corr is not None
        assert str(corr.feats.get("LEMMA")) == "ben"


class TestPhase8tPpCorrection:
    """Rule (b): ``Hindi …  kundi  PP``."""

    @pytest.mark.parametrize("sentence", [
        "Walang tao kundi sa bayan.",
        "Wala siyang pera kundi sa bahay.",
    ])
    def test_kundi_pp_correction_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse for {sentence!r}"
        f = parses[0][1]
        assert str(f.feats.get("POLARITY")) == "NEG"
        corr = _correction_adjunct(f)
        assert corr is not None


class TestPhase8tNegGate:
    """The rule constrains on the matrix carrying POLARITY=NEG.
    Affirmative matrix + kundi-NP is blocked."""

    def test_affirmative_matrix_blocks_kundi(self) -> None:
        """``Si Juan ang darating kundi si Pedro.`` (affirmative
        cleft + kundi-NP) must not parse via the Phase 8.T rule —
        kundi requires a negated antecedent to correct."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Si Juan ang darating kundi si Pedro.", n_best=3,
        )
        # No CORRECTION adjunct on any parse
        for _ct, f, _astr, _diags in parses:
            assert _correction_adjunct(f) is None, (
                "affirmative matrix admitted a CORRECTION adjunct "
                "— POLARITY=NEG gate failed"
            )


class TestPhase8tCorrelativeClausalRegression:
    """The Phase 5l Commit 14 correlative-clausal coord
    (``S , kundi pati S``, ``S kundi pati S``, ``S , kundi S``)
    still parses; the new phrasal rule does not shadow or
    spuriously double-count those parses."""

    @pytest.mark.parametrize("sentence", [
        # Phase 5l C14 Rule (a): Hindi lang X, kundi pati Y.
        "Hindi lang kumain si Maria, kundi pati pumunta si Juan.",
        # Phase 5l C14 Rule (c): Hindi lang X, kundi Y. (no pati)
        "Hindi lang kumain si Maria, kundi pumunta si Juan.",
    ])
    def test_correlative_clausal_unaffected(
        self, sentence: str,
    ) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"regression on {sentence!r}"
        # At least one parse carries CONJUNCTS at matrix (clausal
        # coord) — distinct from the phrasal CORRECTION adjunct
        clausal_parse_found = any(
            f.feats.get("CONJUNCTS") is not None
            for _ct, f, _astr, _diags in parses
        )
        assert clausal_parse_found, (
            f"{sentence!r} lost its clausal-coord parse"
        )


class TestPhase8tOutOfScope:
    """Audit candidates that remain zero-parse after 8.T — pinned
    as separate construction classes beyond 8.T scope."""

    def test_sentence_medial_pp_cleft_closed_in_9q(self) -> None:
        """``Hindi dito kundi sa bayan ang pulong.`` (S&O 1972
        page 656 / sent-1289) — PP-cleft + kundi-PP with the
        correction sentence-medial (before ang-pivot).

        Phase 9.Q B3.D closes this via a dedicated 5-daughter
        rule in cfg/clause.py:

            S → PART[NEG] NP[CASE=DAT] PART[COORD=BUT_NOT]
                  NP[CASE=DAT] NP[CASE=NOM]
                ``(↑ PRED) = 'BE-LOC <SUBJ>'``
                ``(↑ LOC) = ↓4``  (corrective PP — actual location)
                ``↓2 ∈ (↑ ADJUNCT)`` with ROLE='NEG_CORRECTION'

        Pre-9.Q this asserted ``len == 0`` (out-of-scope).
        Post-9.Q the sentence parses with the corrected PP
        (``sa bayan``) as the locative predicate and the negated
        alternative (``dito``) as a NEG_CORRECTION adjunct."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Hindi dito kundi sa bayan ang pulong.", n_best=2,
        )
        assert len(parses) >= 1, (
            "PP-cleft + kundi-PP should parse post-9.Q"
        )

    def test_kundi_verb_forcing(self) -> None:
        """``Wala kang magagawa kundi umalis.`` "You have no
        choice but to leave." — ``kundi VERB`` (forcing course of
        action) is a distinct construction; 8.T only handles
        ``kundi NP`` / ``kundi PP``. Flip when a kundi-V sub-PR
        lands."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Wala kang magagawa kundi umalis.", n_best=2,
        )
        assert len(parses) == 0, (
            "kundi + VERB closed — flip if a kundi-V "
            "construction sub-PR added the rule."
        )
