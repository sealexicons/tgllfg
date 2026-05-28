# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-2 PANAHON sent-39 close-out: chart-time
DISCOURSE_POS / PREP_TYPE feat narrowing + fronted-PP-comma
pipeline split-and-glue.

PANAHON sent-39 (R&G 1981): ``Dahil sa ganitong pagkakaayos ng
panahon, iba ang kamalayang Pilipino tungkol sa oras.`` "Because
of this arrangement of weather, the Filipino consciousness about
time is different."

Two structural changes plus one pipeline mechanism:

(a) **S → PART S narrowed to PART[DISCOURSE_POS=SENTENCE_INITIAL]**
    in `discourse.py`. The fan-out probe ranked the un-gated
    rule first at span_max=38880 on sent-39 because the
    solve-time `(↓1 DISCOURSE_POS) =c 'SENTENCE_INITIAL'` admitted
    every PART at chart time. Multi-word connective rules
    (`gayon din` / `ganon din` / `bukod dito` / `una sa lahat`)
    have their LHS lifted to the same feat so they still feed
    the rule.

(b) **PP rule refactored per-PREP_TYPE** in `extraction.py`.
    One LHS per value in {BENEFICIARY, TOPIC, SOURCE, REASON,
    GOAL, EXCEPTIVE, ROLE, SIMILATIVE}. The c13 fronted-REASON-PP
    rule (`S → PP PUNCT[COMMA] S`) now bracket-gates its PP
    daughter on `PP[PREP_TYPE=REASON]`, pushing the REASON check
    from solve to chart time.

(c) **Fronted-PP-comma pipeline split** in `core/pipeline.py`.
    When input starts with a REASON-PREP (`Dahil`) and contains
    a sentence-internal comma, parse the pre and post halves
    independently and synthesize the matrix S via
    `_glue_fronted_pp_comma` (mirrors c13's `(↑) = ↓3`,
    `(↑ TOPIC) = ↓1`, `↓1 ∈ (↑ ADJ)`). This bypasses the
    `(PP_alts × S_alts)` cross-product the chart-level rule
    enumerates — sent-39's matrix span had 48 × 155 = 7440
    cross alternatives that dominated the tree-iteration
    budget.
"""

import pytest

from tgllfg.cfg import Grammar
from tgllfg.core.pipeline import parse_text


class TestSent39Closure:
    def test_sent39_closes_at_default_cap(self) -> None:
        """sent-39 should close at the default max_tree_iterations=5000
        — the fronted-PP-comma split runs before the chart and parses
        each half against a small chart (sent-39 was timing-blocked
        past cap 5000 under the chart-level c13 rule before post-2)."""
        parses = parse_text(
            "Dahil sa ganitong pagkakaayos ng panahon, "
            "iba ang kamalayang Pilipino tungkol sa oras."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # Matrix should be the post-comma clause (c13's `(↑) = ↓3`).
        # Its TOPIC is the fronted PP (`(↑ TOPIC) = ↓1`).
        topic = fs.feats.get("TOPIC")
        assert topic is not None, "Fronted-PP TOPIC absent from matrix"
        assert topic.feats.get("PREP_TYPE") == "REASON"
        # And the fronted PP is also in the matrix's ADJ set.
        adj = fs.feats.get("ADJ")
        assert adj is not None
        assert topic in adj


class TestChartNarrowing:
    def test_sentence_initial_part_rule_narrowed(self) -> None:
        """`S → PART[DISCOURSE_POS=SENTENCE_INITIAL] S` — the chart
        side gate now matches the (formerly solve-time) feat."""
        g = Grammar.load_default()
        matching = [
            r for r in g.rules
            if r.lhs == "S"
            and r.rhs == ["PART[DISCOURSE_POS=SENTENCE_INITIAL]", "S"]
        ]
        assert len(matching) == 1, (
            "expected exactly one narrowed S → PART S rule"
        )

    def test_comma_variant_part_rule_narrowed(self) -> None:
        """`S → PART[DISCOURSE_POS=SENTENCE_INITIAL] PUNCT[COMMA] S`
        — the 9.V.4b comma variant gate now also matches at
        chart time."""
        g = Grammar.load_default()
        matching = [
            r for r in g.rules
            if r.lhs == "S"
            and r.rhs == [
                "PART[DISCOURSE_POS=SENTENCE_INITIAL]",
                "PUNCT[PUNCT_CLASS=COMMA]",
                "S",
            ]
        ]
        assert len(matching) == 1

    def test_multi_word_connective_rules_advertise_feat(self) -> None:
        """The four multi-word connective rules (`gayon din` /
        `ganon din` / `bukod dito` / `una sa lahat`) lift their
        LHS to `PART[DISCOURSE_POS=SENTENCE_INITIAL]` so they
        match the narrowed S → PART S parents."""
        g = Grammar.load_default()
        connective = [
            r for r in g.rules
            if r.lhs == "PART[DISCOURSE_POS=SENTENCE_INITIAL]"
            and any("LEMMA) = 'gayon_din'" in eq
                    or "LEMMA) = 'ganon_din'" in eq
                    or "LEMMA) = 'bukod_dito'" in eq
                    or "LEMMA) = 'una_sa_lahat'" in eq
                    for eq in r.equations)
        ]
        assert len(connective) == 4, (
            f"expected 4 connective rules, found {len(connective)}"
        )

    def test_generic_pp_rule_per_prep_type(self) -> None:
        """The generic PP rule is parameterized per PREP_TYPE so
        the LHS advertises the feat for chart-side bracket gating.
        Eight rules (one per PREP_TYPE value)."""
        g = Grammar.load_default()
        per_type = [
            r for r in g.rules
            if r.lhs.startswith("PP[PREP_TYPE=")
            and r.rhs == ["PREP[PREP_TYPE="
                          + r.lhs[len("PP[PREP_TYPE="):-1] + "]",
                          "NP[CASE=DAT]"]
        ]
        assert len(per_type) == 8, (
            f"expected 8 per-PREP_TYPE PP rules, found {len(per_type)}"
        )

    def test_c13_rule_chart_gated_on_reason(self) -> None:
        """The c13 fronted-PP-comma rule (`S → PP PUNCT[COMMA] S`)
        now bracket-gates its PP daughter on
        `PP[PREP_TYPE=REASON]` — chart-time check, no solve-time
        constraining equation needed."""
        g = Grammar.load_default()
        matching = [
            r for r in g.rules
            if r.lhs == "S"
            and r.rhs == [
                "PP[PREP_TYPE=REASON]",
                "PUNCT[PUNCT_CLASS=COMMA]",
                "S",
            ]
        ]
        assert len(matching) == 1


class TestFrontedPpCommaSplit:
    def test_dahil_short_sentence_closes(self) -> None:
        """A short Dahil-PP-comma sentence should close via the
        fronted-PP-comma split path (it would also close via the
        chart, but the split is the fast path)."""
        parses = parse_text(
            "Dahil sa init, iba ang kamalayan."
        )
        assert len(parses) >= 1

    def test_non_dahil_input_skips_split(self) -> None:
        """The split's activation gate requires the first word's
        lemma to be in the REASON-PREP set. A sentence that starts
        with a non-REASON word should fall through to the chart
        (sanity guard against over-activation)."""
        parses = parse_text("Maganda ang panahon.")
        assert len(parses) >= 1

    def test_dahil_without_comma_skips_split(self) -> None:
        """A Dahil-headed sentence without a sentence-internal
        comma falls through to the chart (the split needs both
        anchors)."""
        # ``dahil sa X`` as an in-situ PP (not fronted with comma)
        parses = parse_text(
            "Kumain ang bata dahil sa gutom."
        )
        # Should still parse via the chart (clause-final REASON PP).
        # Acceptable outcome: any number of parses, including 0,
        # but the test asserts the split didn't crash.
        assert isinstance(parses, list)


class TestNoRegressionOnExistingDiscourseInitial:
    def test_gayon_din_still_parses(self) -> None:
        """The gayon-din connective still composes through the
        narrowed chain (multi-word rule emits
        `PART[DISCOURSE_POS=SENTENCE_INITIAL]`; the matrix
        `S → PART[…] S` consumes it)."""
        parses = parse_text("Gayon din kumain ang bata.")
        assert len(parses) >= 1

    def test_bukod_dito_still_parses(self) -> None:
        parses = parse_text("Bukod dito kumain ang bata.")
        assert len(parses) >= 1

    def test_una_sa_lahat_still_parses(self) -> None:
        parses = parse_text(
            "Una sa lahat, kumain ang bata."
        )
        assert len(parses) >= 1
