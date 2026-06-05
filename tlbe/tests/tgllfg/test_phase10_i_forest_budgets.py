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
        # The nine recursive ``S → S PP[FEAT=X]`` adjunct-attachment
        # rules opt into a per-span emission budget (Phase 10.I).
        # Phase 10.K.post-1 commit 2 lifted each consumer's PP daughter
        # from bare ``PP`` to a per-type chart-symbol gate:
        #
        #   * TIME_FRAME: ``PP[TIME_FRAME=PERIODIC]`` + ``PP[TIME_FRAME=PAST]``
        #     (2 rules — split by value, replacing the pre-lift single
        #     rule with solve-time existential ``(↓2 TIME_FRAME)`` gate)
        #   * EXCEPTIVE: ``PP[PREP_TYPE=EXCEPTIVE]`` (1 rule)
        #   * BENEFICIARY / TOPIC / GOAL / REASON / SOURCE / ROLE:
        #     per-type ``PP[PREP_TYPE=X]`` (6 rules)
        #
        # Guards against a tenth S→S PP rule being added without
        # considering the fan-out budget. REASON was added by Phase
        # 10.J.post-7.2 (lifting the Phase 9.X.c12 REASON deferral);
        # SOURCE was added by Phase 10.J.post-7.4 (lifting the c12
        # SOURCE deferral — the posited Wackernagel/range risk is
        # structurally distinct from the 3-daughter SOURCE PP). GOAL
        # was already in the loop pre-post-7.5 (added 9.X.c29);
        # post-7.5 added the corresponding fronted-PP-comma chart
        # rule (cfg/discourse.py c13 loop) without changing the c12
        # S→S PP count. ROLE was added by Phase 10.J.post-12.10
        # (bilang N predicative-role complement for PAMILYA/sent-4).
        g = Grammar.load_default()
        ss_pp = [
            r for r in g.rules
            if r.lhs == "S"
            and len(r.rhs) == 2
            and r.rhs[0] == "S"
            and r.rhs[1].startswith("PP[")
        ]
        assert len(ss_pp) == 9
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
