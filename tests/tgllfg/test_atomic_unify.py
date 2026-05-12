"""Phase 6.A — atomic unify via :class:`Snapshot` / :meth:`rollback`.

C1 (this commit): smoke tests for the snapshot / rollback API itself.
C2 will wire snapshot-on-entry / rollback-on-failure into
:meth:`FGraph.unify` and add symmetric-failure property tests.
C3 will add the Hypothesis property battery (failed-unify rollback,
reentrancy preservation across snapshot boundaries, nested
snapshots).
"""

from __future__ import annotations

from tgllfg.fstruct import (
    AtomValue,
    ComplexValue,
    FGraph,
    SetValue,
    Snapshot,
)


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
