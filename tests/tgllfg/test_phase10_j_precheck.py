# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J commit 1 — ``precheck_defining_subtree`` predicate tests.

The precheck is the parse-set-preserving early-prune predicate the
follow-on commit will fold into ``parse/earley.py:_iter_cnodes`` (opt-in)
to skip provably-dead subtrees. These tests verify:

* clean subtrees return ``False`` (not prunable);
* each **monotone** defining-clash kind returns ``True`` (provably dead
  inside any containing tree);
* **constraining**-side failures return ``False`` — they're non-monotone
  (a feature absent in the subtree may be defined by an ancestor), so
  pruning on them would risk regressing the accepted-parse set.
"""

from tgllfg.core.common import CNode
from tgllfg.fstruct import precheck_defining_subtree


# === Clean subtrees =======================================================

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


# === Monotone defining-clash kinds (the prune-trigger set) ================

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


# === Constraining-side failures must NOT trigger the precheck =============

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
