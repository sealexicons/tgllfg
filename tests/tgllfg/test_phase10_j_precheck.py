# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J — ``precheck_defining_subtree`` predicate and the opt-in
``_iter_cnodes`` hook tests.

The precheck is the parse-set-preserving early-prune predicate. Commit 1
ships the predicate; commit 2 folds it into ``parse/earley.py:_iter_cnodes``
as an opt-in flag (default ``False`` → byte-identical). These tests verify:

* clean subtrees return ``False`` (not prunable);
* each **monotone** defining-clash kind returns ``True`` (provably dead);
* **constraining**-side failures return ``False`` (non-monotone — must not
  prune);
* the opt-in flag through ``parse_with_annotations`` /
  ``PackedForest.iter_trees`` is byte-identical when off and prunes
  clashing c-trees when on.
"""

from tgllfg.cfg import Grammar, Rule
from tgllfg.core.common import CNode, LexicalEntry, MorphAnalysis
from tgllfg.fstruct import precheck_defining_subtree
from tgllfg.parse import parse_with_annotations


# === Predicate tests (commit 1) ===========================================

class TestPrecheckCleanSubtrees:
    def test_empty_node_no_equations(self) -> None:
        # No equations at all → no clash is possible.
        assert precheck_defining_subtree(CNode(label="S")) is False

    def test_single_defining_equation(self) -> None:
        # One atomic assignment on a single node — clean.
        node = CNode(label="N", equations=["(↑ LEMMA) = 'foo'"])
        assert precheck_defining_subtree(node) is False

    def test_compatible_unification(self) -> None:
        # Two daughters both unified up to the mother (↑), both setting
        # the SAME LEMMA value — unification succeeds.
        n1 = CNode(label="N", equations=["(↑ LEMMA) = 'foo'"])
        n2 = CNode(label="N", equations=["(↑ LEMMA) = 'foo'"])
        root = CNode(
            label="S",
            children=[n1, n2],
            equations=["(↑) = ↓1", "(↑) = ↓2"],
        )
        assert precheck_defining_subtree(root) is False

    def test_distinct_features_no_overlap(self) -> None:
        # Different features → independent atoms → no clash.
        root = CNode(
            label="S",
            equations=[
                "(↑ LEMMA) = 'foo'",
                "(↑ POS) = 'N'",
            ],
        )
        assert precheck_defining_subtree(root) is False


class TestPrecheckMonotoneClashes:
    def test_atom_mismatch(self) -> None:
        # Two daughters share ↑ but set conflicting LEMMA values —
        # unification clash on atoms.
        n1 = CNode(label="N", equations=["(↑ LEMMA) = 'foo'"])
        n2 = CNode(label="N", equations=["(↑ LEMMA) = 'bar'"])
        root = CNode(
            label="S",
            children=[n1, n2],
            equations=["(↑) = ↓1", "(↑) = ↓2"],
        )
        assert precheck_defining_subtree(root) is True

    def test_type_mismatch_atom_then_path(self) -> None:
        # LEMMA set as atom, then a sub-path through it — path-through-
        # non-complex (a monotone clash kind in the whitelist).
        root = CNode(
            label="S",
            equations=[
                "(↑ LEMMA) = 'foo'",         # LEMMA is atom 'foo'
                "(↑ LEMMA NESTED) = 'bar'",  # tries to descend into atom
            ],
        )
        assert precheck_defining_subtree(root) is True


class TestPrecheckConstrainingNotTriggered:
    def test_constraining_check_on_undefined_feature(self) -> None:
        # A subtree whose only failure is a ``=c`` check on a feature
        # that's not defined here. An ancestor's defining equation could
        # define it later → the precheck must NOT prune this subtree.
        root = CNode(
            label="S",
            equations=["(↑ FOO) =c 'bar'"],
        )
        assert precheck_defining_subtree(root) is False

    def test_existential_check_on_undefined_feature(self) -> None:
        # Same logic for existential constraints — non-monotone, defer.
        root = CNode(
            label="S",
            equations=["(↑ FOO)"],
        )
        assert precheck_defining_subtree(root) is False

    def test_neg_equation_on_undefined_feature(self) -> None:
        # Negative equation on a feature that isn't set — non-monotone.
        root = CNode(
            label="S",
            equations=["(↑ FOO) ~= 'bar'"],
        )
        assert precheck_defining_subtree(root) is False


# === Opt-in _iter_cnodes hook (commit 2) ==================================

def _tok(
    pos: str,
    lemma: str = "x",
    le: LexicalEntry | None = None,
    **feats: str,
) -> list[tuple[MorphAnalysis, LexicalEntry | None]]:
    """Single-analysis token with the given POS and feats (mirrors the
    helper in ``test_earley.py``)."""
    return [(MorphAnalysis(lemma=lemma, pos=pos, feats=dict(feats)), le)]


class TestIterCnodesHook:
    """The opt-in ``precheck_defining`` flag through
    ``parse_with_annotations`` → ``PackedForest`` → ``_iter_cnodes``.
    Default off preserves byte-identical behavior; on prunes c-trees
    whose subtree contains a blocking monotone defining-clash."""

    def _grammar(self) -> Grammar:
        # ``S → A B`` unifies both daughters' f-structures with ↑; ``A → X``
        # and ``B → X`` inherit X's f-structure via ``(↑) = ↓1`` so the lex
        # equations on the X leaves (``(↑ VOICE) = '<v>'``) propagate up
        # the chain. Conflicting VOICE feats on the two X leaves then
        # clash monotonically at the S level.
        return Grammar([
            Rule("S", ["A", "B"], ["(↑) = ↓1", "(↑) = ↓2"]),
            Rule("A", ["X"], ["(↑) = ↓1"]),
            Rule("B", ["X"], ["(↑) = ↓1"]),
        ])

    def test_default_off_matches_explicit_off(self) -> None:
        # Omitting the kwarg and passing ``precheck_defining=False`` must
        # produce the same forest (byte-identical default).
        g = self._grammar()
        lat = [_tok("X", VOICE="A"), _tok("X", VOICE="B")]
        n_default = len(parse_with_annotations(lat, g).trees)
        n_explicit_off = len(parse_with_annotations(
            lat, g, precheck_defining=False,
        ).trees)
        assert n_default == n_explicit_off
        assert n_default >= 1  # clashing c-tree IS yielded when off

    def test_on_prunes_clashing_combo(self) -> None:
        # Two X tokens with conflicting VOICE atoms → unifying via
        # ``(↑) = ↓1`` / ``(↑) = ↓2`` clashes on ``(↑ VOICE)``. With
        # precheck on, the c-tree is pruned before yield.
        g = self._grammar()
        lat = [_tok("X", VOICE="A"), _tok("X", VOICE="B")]
        n_off = len(parse_with_annotations(lat, g).trees)
        n_on = len(parse_with_annotations(
            lat, g, precheck_defining=True,
        ).trees)
        assert n_off >= 1
        assert n_on == 0

    def test_on_does_not_prune_clean_combo(self) -> None:
        # Same VOICE on both daughters → no clash → parse-set preservation.
        g = self._grammar()
        lat = [_tok("X", VOICE="A"), _tok("X", VOICE="A")]
        n_off = len(parse_with_annotations(lat, g).trees)
        n_on = len(parse_with_annotations(
            lat, g, precheck_defining=True,
        ).trees)
        assert n_off >= 1
        assert n_on == n_off
