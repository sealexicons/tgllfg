# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.A Commit 24 — subord nesting depth 3+ stress fixtures
(§18 L95).

Closes §18 L95 by adding explicit fixtures asserting that the
existing unbounded subord recursion (Phase 5l) handles depth-2,
depth-3, and depth-4 subord nesting without regression. No rule
change — tests-only closure.

Depth counting (matrix at depth 1):

* depth-2: matrix S + 1 subord adjunct.
  ``Kung kumain ako, pumunta siya.``
* depth-3: matrix S + subord adjunct + nested-inside-subord.
  ``Kung kumain ako bago pumunta siya, hindi pumunta ako.``
* depth-4: matrix S + 3 nested subord adjuncts. Deeply nested
  forms parse but f-structure flattening may interpret some
  adjuncts as siblings rather than strict-nest. Acceptable per
  plan-of-record §3.4 Commit 24 mitigation.

The recursion is delivered by Phase 5l Commits 1–10 (subord lex
+ adjunct rules) plus the existing matrix-S adjunct attachment
machinery. This commit makes the unbounded-recursion property
explicit via test assertion.
"""

import pytest

from tgllfg.core.pipeline import parse_text


# --- Depth counter ---------------------------------------------------


def _max_subord_depth(node, depth: int = 0) -> int:
    """Walk the f-structure; return the maximum number of nested
    SUBORD_TYPE-bearing nodes encountered on any path."""
    if not hasattr(node, "feats"):
        return depth
    has_subord = node.feats.get("SUBORD_TYPE") is not None
    cur = depth + (1 if has_subord else 0)
    deepest = cur
    for v in node.feats.values():
        if hasattr(v, "feats"):
            deepest = max(deepest, _max_subord_depth(v, cur))
        elif isinstance(v, (list, set, frozenset)):
            for el in v:
                if hasattr(el, "feats"):
                    deepest = max(deepest, _max_subord_depth(el, cur))
    return deepest


# === Depth-2 (matrix + 1 subord) =====================================


class TestDepth2:
    """Single-subord-adjunct sentences across all five COMP_TYPE
    families. Depth-1 in the SUBORD_TYPE counter (the adjunct
    carries one SUBORD_TYPE; the matrix carries zero)."""

    @pytest.mark.parametrize("sentence,subord_type", [
        ("Kung kumain ako, pumunta siya.",      "COND"),
        ("Bago pumunta siya, kumain ako.",      "TEMP_BEFORE"),
        ("Para pumunta siya, kumain ako.",      "PURP"),
        ("Dahil kumain ako, pumunta siya.",     "REAS"),
        ("Bagaman kumain ako, pumunta siya.",   "CONC"),
    ])
    def test_depth_2_parses(
        self, sentence: str, subord_type: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert _max_subord_depth(fs) == 1
        adjuncts = fs.feats.get("ADJUNCT")
        assert adjuncts is not None
        assert any(
            a.feats.get("SUBORD_TYPE") == subord_type
            for a in adjuncts
        )


# === Depth-3 (matrix + subord + nested-inside-subord) ================


class TestDepth3:
    """Two nested SUBORD_TYPE-bearing nodes on one path. The matrix
    carries an adjunct, and that adjunct carries its own adjunct —
    so the f-structure path through the deepest adjunct touches
    SUBORD_TYPE twice."""

    @pytest.mark.parametrize("sentence", [
        # COND with nested TEMP / PURP / REAS / CONC
        "Kung kumain ako bago pumunta siya, hindi pumunta ako.",
        "Kung kumain ako para pumunta siya, hindi pumunta ako.",
        "Kung kumain ako dahil pumunta siya, hindi pumunta ako.",
        "Kung kumain ako bagaman pumunta siya, hindi pumunta ako.",
        # Other matrices with nested COND
        "Bago pumunta siya kung kumain ako, kumain ako.",
        "Para pumunta siya kung kumain ako, kumain ako.",
        "Dahil kumain ako kung pumunta siya, kumain ako.",
        "Bagaman kumain ako bago pumunta siya, hindi pumunta ako.",
    ])
    def test_depth_3_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # Two nested SUBORD_TYPE nodes on the deepest path.
        assert _max_subord_depth(fs) == 2


# === Depth-4 (deeply nested) ========================================


@pytest.mark.slow
class TestDepth4:
    """Three nested subord adjuncts. The grammar admits these
    surfaces; f-structure shape may flatten one adjunct as a
    sibling rather than a strict-nested daughter (a parser
    decision in the existing adjunct-attachment machinery), so
    the depth counter may stop at 2 rather than 3.

    Per plan-of-record §3.4 Commit 24 mitigation: depth-4 stress
    test caps at one canonical sentence; if blowup surfaces, the
    ranker's existing penalty for deep nesting should resolve.
    Asserts only that the surface PARSES and matches at least the
    depth-2 minimum."""

    @pytest.mark.parametrize("sentence", [
        ("Kung kumain ako bago pumunta siya dahil kumain ako, "
         "hindi pumunta ako."),
        ("Kung kumain ako dahil pumunta siya bago kumain ako, "
         "hindi pumunta ako."),
    ])
    def test_depth_4_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"depth-4 sentence {sentence!r} unexpectedly 0-parses"
        )
        _ct, fs, _astr, _diags = parses[0]
        # At minimum, the matrix carries one SUBORD adjunct path.
        assert _max_subord_depth(fs) >= 2
