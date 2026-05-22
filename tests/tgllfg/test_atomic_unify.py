# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 6.A — atomic unify via :class:`Snapshot` / :meth:`rollback`.

C1: smoke tests for the snapshot / rollback API itself.
C2: :meth:`FGraph.unify` switches to snapshot-on-entry /
rollback-on-failure; symmetric-failure tests verify the atomic
contract end-to-end including recursive ComplexValue child failures.
C3 (this commit): Hypothesis property battery covering observable-
state preservation under arbitrary post-snapshot mutations, atomic
failure for arbitrary atom clashes, idempotent rollback under
mutation, reentrancy preservation across snapshot boundaries, and
nested snapshot stacks.
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from tgllfg.fstruct import (
    AtomValue,
    ComplexValue,
    Diagnostic,
    FGraph,
    SetValue,
    Snapshot,
)


atoms = st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=5)


class TestSnapshotRollback:
    def test_empty_graph_snapshot_rollback_is_noop(self) -> None:
        g = FGraph()
        snap = g.snapshot()
        assert isinstance(snap, Snapshot)
        g.rollback(snap)
        assert g._next_id == 0
        assert g._parent == {}
        assert g._rank == {}
        assert g._store == {}

    def test_rollback_reverts_fresh(self) -> None:
        g = FGraph()
        n0 = g.fresh()
        snap = g.snapshot()
        n1 = g.fresh()
        n2 = g.fresh()
        assert g._next_id == 3
        g.rollback(snap)
        assert g._next_id == 1
        # n1 / n2 are stale post-rollback; n0 is still valid.
        assert g.find(n0) == n0
        # Re-allocating should reuse the rolled-back ids.
        assert g.fresh() == n1
        assert g.fresh() == n2

    def test_rollback_reverts_set_atom(self) -> None:
        g = FGraph()
        n = g.fresh()
        snap = g.snapshot()
        assert g.set_atom(n, "NOM") is None
        assert isinstance(g.value(n), AtomValue)
        g.rollback(snap)
        assert g.value(n) is None

    def test_rollback_reverts_resolve_path_attrs(self) -> None:
        g = FGraph()
        root = g.fresh()
        snap = g.snapshot()
        # Walking a path mutates `root`'s ComplexValue and allocates
        # a child node. Both should be reverted by rollback.
        child, err = g.resolve_path(root, ("SUBJ",))
        assert err is None and child is not None
        assert isinstance(g.value(root), ComplexValue)
        g.rollback(snap)
        assert g.value(root) is None
        # Child node id was allocated post-snapshot; rolled back.
        assert g._next_id == snap.next_id

    def test_rollback_reverts_add_to_set(self) -> None:
        g = FGraph()
        container = g.fresh()
        member = g.fresh()
        snap = g.snapshot()
        new_member = g.fresh()
        assert g.add_to_set(container, member) is None
        assert g.add_to_set(container, new_member) is None
        v = g.value(container)
        assert isinstance(v, SetValue)
        assert v.members == {member, new_member}
        g.rollback(snap)
        assert g.value(container) is None

    def test_rollback_reverts_unify_link(self) -> None:
        g = FGraph()
        a, b = g.fresh(), g.fresh()
        assert g.set_atom(a, "X") is None
        assert g.set_atom(b, "X") is None
        snap = g.snapshot()
        assert g.unify(a, b) is None
        assert g.equiv(a, b)
        g.rollback(snap)
        assert not g.equiv(a, b)
        # Both still carry their atom values (set pre-snapshot).
        va, vb = g.value(a), g.value(b)
        assert isinstance(va, AtomValue) and va.atom == "X"
        assert isinstance(vb, AtomValue) and vb.atom == "X"

    def test_rollback_is_idempotent(self) -> None:
        """Calling :meth:`rollback` twice with the same snapshot is a
        no-op on the second call; the snapshot is non-consuming and the
        FGraph state matches the snapshot after either call."""
        g = FGraph()
        a, b = g.fresh(), g.fresh()
        snap = g.snapshot()
        # Mutate after snapshot.
        assert g.set_atom(a, "X") is None
        c = g.fresh()
        assert g.unify(a, b) is None
        # First rollback.
        g.rollback(snap)
        state_after_first = (
            g._next_id,
            dict(g._parent),
            dict(g._rank),
            {n: type(v) for n, v in g._store.items()},
        )
        # Second rollback to the same snapshot.
        g.rollback(snap)
        state_after_second = (
            g._next_id,
            dict(g._parent),
            dict(g._rank),
            {n: type(v) for n, v in g._store.items()},
        )
        assert state_after_first == state_after_second
        # Stale `c` was post-snapshot — must not be in _parent / _rank.
        assert c not in g._parent
        assert c not in g._rank

    def test_rollback_restores_complex_attrs_to_pre_snapshot_keys(self) -> None:
        """After arbitrary post-snapshot ``ComplexValue.attrs``
        mutations, rollback restores the attrs to their pre-snapshot
        key set. Replaces the C1 defensive-copy test — the journal-
        based implementation in 6.A C5 has no separate snapshot copy
        to introspect; the equivalent observable property is the
        rollback semantics itself.
        """
        g = FGraph()
        root = g.fresh()
        _, err = g.resolve_path(root, ("F",))
        assert err is None
        snap = g.snapshot()
        # Mutate the live ComplexValue.attrs dict in place via a
        # second resolve_path step.
        _, err = g.resolve_path(root, ("G",))
        assert err is None
        # Pre-rollback: the live ComplexValue has both F and G.
        live_root_before = g.value(root)
        assert isinstance(live_root_before, ComplexValue)
        assert set(live_root_before.attrs.keys()) == {"F", "G"}
        g.rollback(snap)
        # Post-rollback: G removed, F preserved. The ComplexValue
        # instance is the same object — journal-based rollback
        # mutates in place via the undo log, preserving Python
        # identity for downstream reentrancy.
        live_root_after = g.value(root)
        assert live_root_after is live_root_before
        assert set(live_root_after.attrs.keys()) == {"F"}

    def test_multiple_snapshots_can_target_distinct_points(self) -> None:
        g = FGraph()
        n0 = g.fresh()
        assert g.set_atom(n0, "A") is None
        snap_a = g.snapshot()
        n1 = g.fresh()
        assert g.set_atom(n1, "B") is None
        snap_b = g.snapshot()
        n2 = g.fresh()
        assert g.set_atom(n2, "C") is None
        # Rollback to the *earlier* snapshot — both n1 and n2 should
        # be dropped.
        g.rollback(snap_a)
        assert g._next_id == 1
        v0 = g.value(n0)
        assert isinstance(v0, AtomValue) and v0.atom == "A"
        # `snap_b` is still a valid snapshot value; rolling back to it
        # restores the state at snap_b creation time (n0 + n1 bound).
        # This requires re-creating n1 first, since rollback to snap_a
        # dropped it — the snapshot is opaque so the user *can* try, but
        # after rollback to an earlier snapshot a later one points at
        # ids that have been re-issued. We only check snap_b's recorded
        # next_id is consistent with its capture point.
        assert snap_b.next_id == 2

    def test_snapshot_is_frozen_dataclass(self) -> None:
        """The :class:`Snapshot` dataclass is declared ``frozen=True``;
        clients that try to rebind a field should get a ``FrozenInstanceError``
        rather than silently corrupting the capture."""
        g = FGraph()
        snap = g.snapshot()
        import dataclasses
        try:
            snap.next_id = 99  # type: ignore[misc]
        except dataclasses.FrozenInstanceError:
            return
        raise AssertionError("Snapshot should be frozen")


# === C2 — atomic unify contract ============================================

class TestUnifyAtomicOnFailure:
    """:meth:`FGraph.unify` snapshots on entry and rolls back on
    failure: the public call is atomic regardless of where in the
    recursion the failure surfaces.
    """

    def test_atom_clash_leaves_graph_unchanged(self) -> None:
        g = FGraph()
        a, b = g.fresh(), g.fresh()
        assert g.set_atom(a, "X") is None
        assert g.set_atom(b, "Y") is None
        # Pre-call: distinct roots, distinct atoms.
        assert not g.equiv(a, b)
        err = g.unify(a, b)
        assert isinstance(err, Diagnostic)
        assert err.kind == "atom-mismatch"
        # Atomic: graph unchanged.
        assert not g.equiv(a, b)
        va, vb = g.value(a), g.value(b)
        assert isinstance(va, AtomValue) and va.atom == "X"
        assert isinstance(vb, AtomValue) and vb.atom == "Y"

    def test_recursive_child_clash_rolls_back_parent_link(self) -> None:
        """The key C2 win: when a ComplexValue overlap fails on a child
        unify, the outer parent link and the merged attrs must also be
        rolled back. Pre-C2 mutate-then-fail leaves the parent linked.
        """
        g = FGraph()
        a, b = g.fresh(), g.fresh()
        a_f, err = g.resolve_path(a, ("F",))
        assert err is None and a_f is not None
        b_f, err = g.resolve_path(b, ("F",))
        assert err is None and b_f is not None
        assert g.set_atom(a_f, "X") is None
        assert g.set_atom(b_f, "Y") is None
        # Also add a unique daughter on `a` (not on `b`) to confirm
        # the attribute-merge step is also rolled back.
        _, err = g.resolve_path(a, ("ONLY_ON_A",))
        assert err is None
        # Pre-call: a, b distinct; a.F and b.F distinct.
        assert not g.equiv(a, b)
        assert not g.equiv(a_f, b_f)
        a_val_before = g.value(a)
        assert isinstance(a_val_before, ComplexValue)
        a_attrs_before = set(a_val_before.attrs.keys())
        err = g.unify(a, b)
        assert isinstance(err, Diagnostic)
        assert err.kind == "atom-mismatch"
        assert err.path == ("F",)
        # Atomic: outer parent link rolled back; attrs rolled back;
        # child F clash rolled back; atoms preserved.
        assert not g.equiv(a, b)
        assert not g.equiv(a_f, b_f)
        a_val_after = g.value(a)
        b_val_after = g.value(b)
        assert isinstance(a_val_after, ComplexValue)
        assert isinstance(b_val_after, ComplexValue)
        assert set(a_val_after.attrs.keys()) == a_attrs_before
        assert "ONLY_ON_A" not in b_val_after.attrs
        va_f, vb_f = g.value(a_f), g.value(b_f)
        assert isinstance(va_f, AtomValue) and va_f.atom == "X"
        assert isinstance(vb_f, AtomValue) and vb_f.atom == "Y"

    def test_type_mismatch_atom_vs_complex_rolls_back(self) -> None:
        g = FGraph()
        a, b = g.fresh(), g.fresh()
        assert g.set_atom(a, "X") is None
        _, err = g.resolve_path(b, ("F",))
        assert err is None
        err = g.unify(a, b)
        assert isinstance(err, Diagnostic)
        assert err.kind == "type-mismatch"
        # Atomic.
        assert not g.equiv(a, b)
        va, vb = g.value(a), g.value(b)
        assert isinstance(va, AtomValue) and va.atom == "X"
        assert isinstance(vb, ComplexValue)

    def test_unify_success_persists(self) -> None:
        """Atomic-on-failure must not roll back successful unifications.
        Sanity check.
        """
        g = FGraph()
        a, b = g.fresh(), g.fresh()
        assert g.set_atom(a, "X") is None
        assert g.set_atom(b, "X") is None
        err = g.unify(a, b)
        assert err is None
        assert g.equiv(a, b)

    @given(atom_a=atoms, atom_b=atoms)
    @settings(max_examples=50)
    def test_atom_clash_is_symmetric_under_failure(
        self, atom_a: str, atom_b: str,
    ) -> None:
        """Property: for distinct-atom nodes, unify in either order
        fails and leaves the graph in the pre-call state. The atomic
        contract is symmetric under failure.
        """
        if atom_a == atom_b:
            return
        g = FGraph()
        a, b = g.fresh(), g.fresh()
        assert g.set_atom(a, atom_a) is None
        assert g.set_atom(b, atom_b) is None
        # Forward order.
        err_forward = g.unify(a, b)
        assert isinstance(err_forward, Diagnostic)
        assert err_forward.kind == "atom-mismatch"
        assert not g.equiv(a, b)
        va, vb = g.value(a), g.value(b)
        assert isinstance(va, AtomValue) and va.atom == atom_a
        assert isinstance(vb, AtomValue) and vb.atom == atom_b
        # Reverse order: same outcome on the unchanged graph.
        err_reverse = g.unify(b, a)
        assert isinstance(err_reverse, Diagnostic)
        assert err_reverse.kind == "atom-mismatch"
        assert not g.equiv(a, b)
        va, vb = g.value(a), g.value(b)
        assert isinstance(va, AtomValue) and va.atom == atom_a
        assert isinstance(vb, AtomValue) and vb.atom == atom_b


# === C3 — Hypothesis property battery ======================================

# Reuse the atom-character-set strategy for feature names (same shape).
features = atoms


def _serialize_value(v: object) -> tuple:
    """Hashable, comparable snapshot of an FValue for state equality.

    ``ComplexValue.attrs`` keys are sorted; ``SetValue.members`` are
    sorted so the comparison is insensitive to insertion order.
    """
    if v is None:
        return ("None",)
    if isinstance(v, AtomValue):
        return ("Atom", v.atom)
    if isinstance(v, ComplexValue):
        return ("Complex", tuple(sorted(v.attrs.items())))
    assert isinstance(v, SetValue)
    return ("Set", tuple(sorted(v.members)))


def _describe(g: FGraph, nodes: list) -> tuple:
    """Observable state of ``g`` restricted to ``nodes``.

    Captures each node's canonical root (via :meth:`FGraph.find`) plus
    the value at each distinct root. Insensitive to internal pointer
    state (path-compression order, post-snapshot allocations, etc.);
    two graphs producing equal :func:`_describe` outputs are
    observationally indistinguishable from the perspective of the
    given node set.
    """
    if not nodes:
        return ()
    roots = [(n, g.find(n)) for n in nodes]
    distinct = sorted({r for _, r in roots})
    values = tuple((r, _serialize_value(g.value(r))) for r in distinct)
    return (tuple(sorted(roots)), values)


@st.composite
def _small_graphs(draw: st.DrawFn, max_nodes: int = 4):
    """Hypothesis strategy yielding ``(FGraph, list[NodeId])``.

    Each node is independently left unbound, atom-bound, or made into
    a ComplexValue with 1-2 attributes. After binding, 0-2 random
    unifications are attempted (the call is atomic post-C2 — failures
    leave the graph unchanged).
    """
    g = FGraph()
    n = draw(st.integers(min_value=1, max_value=max_nodes))
    nodes = [g.fresh() for _ in range(n)]

    for i in range(n):
        choice = draw(st.sampled_from(["unbound", "atom", "complex"]))
        if choice == "atom":
            g.set_atom(nodes[i], draw(atoms))
        elif choice == "complex":
            for _ in range(draw(st.integers(min_value=1, max_value=2))):
                g.resolve_path(nodes[i], (draw(features),))

    n_unifies = draw(st.integers(min_value=0, max_value=2))
    for _ in range(n_unifies):
        i = draw(st.integers(min_value=0, max_value=n - 1))
        j = draw(st.integers(min_value=0, max_value=n - 1))
        g.unify(nodes[i], nodes[j])

    return g, nodes


class TestPropertySnapshotRollback:
    @given(state=_small_graphs())
    @settings(max_examples=50)
    def test_snapshot_rollback_preserves_observable_state(self, state) -> None:
        """Snapshot, mutate (allocate + atom-bind + attempt unify with
        a pre-snapshot node), rollback. The observable state for the
        pre-snapshot nodes is exactly the pre-snapshot state.
        """
        g, nodes = state
        pre = _describe(g, nodes)
        snap = g.snapshot()
        extra = g.fresh()
        g.set_atom(extra, "Z")
        if nodes:
            g.unify(extra, nodes[0])  # may fail atomically; either way rolled back
        g.rollback(snap)
        post = _describe(g, nodes)
        assert pre == post

    @given(atom_a=atoms, atom_b=atoms)
    @settings(max_examples=50)
    def test_failed_unify_preserves_observable_state(
        self, atom_a: str, atom_b: str,
    ) -> None:
        """For any pair of clashing atoms, ``unify`` returns a
        :class:`Diagnostic` and the observable state is unchanged.
        """
        if atom_a == atom_b:
            return
        g = FGraph()
        a, b = g.fresh(), g.fresh()
        g.set_atom(a, atom_a)
        g.set_atom(b, atom_b)
        pre = _describe(g, [a, b])
        err = g.unify(a, b)
        assert isinstance(err, Diagnostic)
        post = _describe(g, [a, b])
        assert pre == post

    @given(state=_small_graphs())
    @settings(max_examples=50)
    def test_idempotent_rollback_under_arbitrary_mutations(
        self, state,
    ) -> None:
        """Calling :meth:`rollback` twice with the same snapshot is a
        no-op on the second call, regardless of what mutations occurred
        between snapshot and first rollback.
        """
        g, nodes = state
        snap = g.snapshot()
        extra = g.fresh()
        g.set_atom(extra, "Q")
        if nodes:
            g.unify(extra, nodes[-1])
        g.rollback(snap)
        first = _describe(g, nodes)
        g.rollback(snap)
        second = _describe(g, nodes)
        assert first == second


class TestPropertyReentrancyPreservation:
    @given(atom=atoms)
    @settings(max_examples=50)
    def test_pre_snapshot_equivalence_survives_rollback(
        self, atom: str,
    ) -> None:
        """Two nodes unified before a snapshot remain unified after a
        rollback to that snapshot, regardless of mutations in between.
        """
        g = FGraph()
        a, b = g.fresh(), g.fresh()
        g.set_atom(a, atom)
        g.set_atom(b, atom)
        assert g.unify(a, b) is None
        assert g.equiv(a, b)
        snap = g.snapshot()
        c = g.fresh()
        g.set_atom(c, "DIFFERENT")
        g.unify(a, c)  # may fail atomically; either way rolled back
        g.rollback(snap)
        assert g.equiv(a, b)

    def test_complex_value_reentrancy_preserved_across_rollback(self) -> None:
        """A ComplexValue with a shared child (the canonical reentrancy
        case) survives a snapshot/rollback intact: the post-rollback
        graph still has the two parent nodes' ``F`` attributes pointing
        at the same canonical root.
        """
        g = FGraph()
        a, b = g.fresh(), g.fresh()
        a_f, err = g.resolve_path(a, ("F",))
        assert err is None and a_f is not None
        b_f, err = g.resolve_path(b, ("F",))
        assert err is None and b_f is not None
        assert g.set_atom(a_f, "SHARED") is None
        assert g.set_atom(b_f, "SHARED") is None
        assert g.unify(a_f, b_f) is None
        assert g.equiv(a_f, b_f)
        snap = g.snapshot()
        c = g.fresh()
        assert g.set_atom(c, "OTHER") is None
        err = g.unify(b_f, c)
        assert isinstance(err, Diagnostic)
        # Atomic-on-failure: a_f and b_f are still equivalent.
        assert g.equiv(a_f, b_f)
        g.rollback(snap)
        # And after rollback to a snapshot that captured the reentrancy.
        assert g.equiv(a_f, b_f)


class TestPropertyNestedSnapshots:
    def test_two_level_rollback_to_inner(self) -> None:
        """Take two nested snapshots; rolling back to the inner one
        lands at the inner state and leaves nodes allocated between
        the two snapshots intact.
        """
        g = FGraph()
        a = g.fresh()
        _outer = g.snapshot()
        assert g.set_atom(a, "X") is None
        b = g.fresh()
        inner = g.snapshot()
        assert g.set_atom(b, "Y") is None
        c = g.fresh()
        g.rollback(inner)
        assert g._next_id == 2
        va = g.value(a)
        vb = g.value(b)
        assert isinstance(va, AtomValue) and va.atom == "X"
        # `b` was allocated pre-inner-snapshot; rollback to inner keeps
        # it but drops the set_atom that came after.
        assert vb is None
        assert c not in g._parent

    def test_two_level_rollback_to_outer(self) -> None:
        """The outer snapshot is non-consuming and unaffected by the
        existence of inner snapshots; rolling back to it reverts the
        inner mutations as well.
        """
        g = FGraph()
        a = g.fresh()
        outer = g.snapshot()
        assert g.set_atom(a, "X") is None
        b = g.fresh()
        _inner = g.snapshot()
        assert g.set_atom(b, "Y") is None
        g.rollback(outer)
        assert g._next_id == 1
        assert g.value(a) is None
        assert b not in g._parent

    @given(state=_small_graphs())
    @settings(max_examples=30)
    def test_outer_snapshot_unaffected_by_inner_rollback(
        self, state,
    ) -> None:
        """An outer snapshot survives an inner rollback intact; rolling
        back to the outer snapshot reverts the whole sequence.
        """
        g, nodes = state
        outer = g.snapshot()
        baseline = _describe(g, nodes)
        # Inner: allocate + bind + snapshot + bind more.
        extra = g.fresh()
        g.set_atom(extra, "I")
        inner = g.snapshot()
        more = g.fresh()
        g.set_atom(more, "J")
        # Rollback to inner; the outer is still valid.
        g.rollback(inner)
        # Rollback to outer; the whole sequence is reverted.
        g.rollback(outer)
        assert _describe(g, nodes) == baseline
