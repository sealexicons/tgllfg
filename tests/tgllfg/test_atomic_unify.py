"""Phase 6.A — atomic unify via :class:`Snapshot` / :meth:`rollback`.

C1: smoke tests for the snapshot / rollback API itself.
C2 (this commit): :meth:`FGraph.unify` switches to snapshot-on-entry /
rollback-on-failure; symmetric-failure tests verify the atomic
contract end-to-end including recursive ComplexValue child failures.
C3 will add the Hypothesis property battery (reentrancy preservation
across snapshot boundaries, nested snapshots).
"""

from __future__ import annotations

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

    def test_snapshot_independent_of_subsequent_mutations(self) -> None:
        """A snapshot taken at time T must not be affected by mutations
        between T and rollback; tests the defensive-copy contract."""
        g = FGraph()
        root = g.fresh()
        # Allocate a ComplexValue at `root` so we can mutate its attrs.
        child, err = g.resolve_path(root, ("F",))
        assert err is None
        snap = g.snapshot()
        # Mutate the live graph's ComplexValue.attrs dict in place via
        # a second resolve_path step.
        _, err = g.resolve_path(root, ("G",))
        assert err is None
        # Snapshot's stored ComplexValue should still have just {"F"}.
        snap_root = snap.store[root]
        assert isinstance(snap_root, ComplexValue)
        assert set(snap_root.attrs.keys()) == {"F"}
        # After rollback, the live graph's ComplexValue is also {"F"}.
        g.rollback(snap)
        live_root = g.value(root)
        assert isinstance(live_root, ComplexValue)
        assert set(live_root.attrs.keys()) == {"F"}

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
