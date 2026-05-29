# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.I forest-density per-rule budgets — opt-in + closure guards.

The mechanism itself is unit-tested in ``test_earley.py::TestRuleBudget``.
Here we guard the rule opt-ins and the concrete sentence closure the
budgets deliver (docs/diagnostics.md §6.2)."""

import pytest

from tgllfg.cfg import Grammar
from tgllfg.core.pipeline import parse_text


class TestForestBudgetOptIn:
    def test_ss_pp_rules_carry_budget(self) -> None:
        # The six recursive ``S → S PP`` adjunct-attachment rules
        # (TIME_FRAME / EXCEPTIVE / BENEFICIARY / TOPIC / GOAL / REASON)
        # opt into a per-span emission budget (Phase 10.I). Guards
        # against a seventh S→S PP rule being added without considering
        # the fan-out budget. REASON was added by Phase 10.J.post-7.2
        # (lifting the Phase 9.X.c12 deferral) — see the loop comment
        # in cfg/discourse.py.
        g = Grammar.load_default()
        ss_pp = [r for r in g.rules if r.lhs == "S" and r.rhs == ["S", "PP"]]
        assert len(ss_pp) == 6
        assert all(r.budget == 200 for r in ss_pp)


class TestSent29Closure:
    @pytest.mark.slow
    def test_sent29_closes_within_default_cap(self) -> None:
        # ANG MANOK sent-29. The ``S → S PP`` per-span budget pulls the
        # lone valid V[CAUS=DIRECT] 4-arg parse from forest position
        # #8684 to #1004, so it now closes within the default
        # ``max_tree_iterations=5000`` (previously a 0-parse, which had
        # needed the cap raised to 10000 — regressing PANAHON sent-16 past
        # the 10s audit timeout). Regression guard for the §6.2 tradeoff.
        parses = parse_text("Pinakain niya ang manok ng isang tasang palay.")
        assert len(parses) >= 1
