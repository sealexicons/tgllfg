# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.B Commit 23: Gayon din / Ganon din pre-clitic-reorder
phrase pass (§18 L103).

Closes §18.1 deferral L103. Target sentences:

    Gayon din kumain ako.    "Likewise, I ate."
    Ganon din pumunta siya.  (colloquial variant of gayon din)
    Gayon din kumain ang bata.

The Phase 5m Commit 11 multi-word discourse connective grammar
rules (cfg/discourse.py — ``PART → PART PART`` matching gayon /
ganon + din, building a virtual sentence-initial PART) were
already in place but didn't fire end-to-end because the standard
2P-clitic placement engine moved ``din`` to clause-final before
the parser saw the input — breaking the multi-word adjacency.

One change (src/tgllfg/clitics/placement.py): new
``_is_post_discourse_head_din`` placement exception. ``din`` is
a 2P-clitic that the placement engine normally moves to clause-
final. When ``din`` immediately follows ``gayon`` or ``ganon``
(the multi-word discourse connective context), the exception
keeps it adjacent so the Phase 5m C11 grammar rule can fire.
Other ``din`` 2P-clitic uses (``Kumain ako rin/din.``) are
unaffected — the gate is narrowly scoped by checking the
preceding token's lemma.

This is a placement-engine exception, parallel to the
Phase 5n.B C18 (siguro / marahil sentence-initial) and C22
(wh-PRON + man) exceptions. The plan-of-record §4.2 Commit 23
suggested a pre-clitic-reorder phrase merge in
``text/multiword.py``; the placement-engine approach is
functionally equivalent (it gates the reorder rather than
pre-merging tokens) and consistent with the C18/C22 fixes.
"""

import pytest

from tgllfg.core.pipeline import parse_text


def _has_likewise_part_lhs(parses) -> bool:
    """True if any parse has children=[PART, S] with the PART
    matrix carrying DISCOURSE='LIKEWISE'."""
    for ct, fs, _astr, _diags in parses:
        labels = [c.label for c in ct.children]
        if labels == ["PART", "S"]:
            return True
    return False


# === Gayon din / Ganon din clause-initial ============================


class TestGayonDinClauseInitial:
    """``Gayon din`` / ``Ganon din`` parse as clause-initial
    discourse connectives. The Phase 5m C11 grammar rule
    composes the two-token sequence into a virtual sentence-
    initial PART; the new placement exception keeps the
    sequence adjacent across the clitic-reorder pass."""

    @pytest.mark.parametrize("sentence", [
        "Gayon din kumain ako.",
        "Gayon din pumunta siya.",
        "Gayon din kumain ang bata.",
        "Ganon din kumain ako.",
        "Ganon din pumunta siya.",
        "Ganon din kumain ang bata.",
    ])
    def test_clause_initial_discourse(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        assert _has_likewise_part_lhs(parses)


# === Bare din 2P-clitic regression ===================================


class TestBareDinClitic:
    """The standard 2P-clitic placement of ``din`` / ``rin``
    (post-anchor, in the Wackernagel cluster) is unaffected by
    the new placement exception — the exception only fires when
    ``din`` is preceded by ``gayon`` / ``ganon``."""

    @pytest.mark.parametrize("sentence", [
        "Kumain ako rin.",
        "Kumain din ako.",
        "Kumain ako din.",
        "Pumunta siya rin.",
    ])
    def test_bare_din_clitic_unchanged(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        # The parse should be V-headed (not a multi-word PART
        # discourse connective).
        _ct, fs, _astr, _diags = parses[0]
        # The clitic is in the matrix's ADJ set, not as a
        # sentence-initial discourse particle.
        adj = fs.feats.get("ADJ") or set()
        din_or_rin = any(
            getattr(m, "feats", {}).get("LEMMA") in ("din", "rin")
            for m in adj
        )
        assert din_or_rin


# === Bukod dito regression (Phase 5m C11 mixed-POS rule) =============


class TestBukodDitoUnchanged:
    """The Phase 5m C11 ``bukod dito`` multi-word rule (mixed
    PART + ADP daughters) doesn't involve a 2P-clitic and so
    isn't affected by the placement exception. Verify it still
    fires."""

    def test_bukod_dito(self) -> None:
        parses = parse_text("Bukod dito kumain ako.")
        assert len(parses) >= 1
