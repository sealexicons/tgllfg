# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 14.final.post-9 — dedup helpers behind the appositive/coordination
φ-completeness fix.

The colon / em-dash appositive glues add the post-half to the pre-half's
APP set in place, so gluing one pre-half against N structurally-identical
(spuriously-ambiguous) post-halves used to leak all N into the shared APP —
N-1 of them φ-orphaned. :func:`_dedup_glued` collapses the structural
duplicates before the glue loop so each pre_fs is glued exactly once; it
keys on :func:`_fstructure_signature`, a cycle-safe structural fingerprint.

The end-to-end inspector-facing behaviour (APP holds one coordination,
every coordination f-node maps back to a c-node, synthetic c-nodes carry
equations) is asserted over the ``/parse`` response in
``test_api_parse.py``; these are the unit tests for the two helpers.
"""

from tgllfg.core.common import AStructure, CNode, FStructure
from tgllfg.core.pipeline import _dedup_glued, _fstructure_signature


def _parse(fs: FStructure) -> tuple[CNode, FStructure, AStructure, list, dict]:
    """A minimal _GluedParse 5-tuple wrapping ``fs`` (the only field
    :func:`_dedup_glued` inspects)."""
    return (CNode(label="S"), fs, AStructure(pred="X", roles=[], mapping={}), [], {})


class TestFStructureSignature:
    def test_matches_structural_equals_ignoring_object_id(self) -> None:
        # Same attributes / values, different .id and Python identity.
        a = FStructure(feats={"CASE": "NOM", "NUM": "PL"}, id=1)
        b = FStructure(feats={"NUM": "PL", "CASE": "NOM"}, id=99)
        assert _fstructure_signature(a) == _fstructure_signature(b)

    def test_distinguishes_different_content(self) -> None:
        a = FStructure(feats={"CASE": "NOM", "NUM": "PL"}, id=1)
        c = FStructure(feats={"CASE": "GEN", "NUM": "PL"}, id=2)
        assert _fstructure_signature(a) != _fstructure_signature(c)

    def test_set_membership_is_order_independent(self) -> None:
        m1 = FStructure(feats={"PRED": "a"}, id=10)
        m2 = FStructure(feats={"PRED": "b"}, id=11)
        a = FStructure(feats={"CONJUNCTS": frozenset({m1, m2})}, id=1)
        b = FStructure(feats={"CONJUNCTS": frozenset({m2, m1})}, id=2)
        assert _fstructure_signature(a) == _fstructure_signature(b)

    def test_is_cycle_safe(self) -> None:
        a = FStructure(feats={}, id=1)
        a.feats["SELF"] = a  # reentrant back-edge
        sig = _fstructure_signature(a)  # must terminate, not recurse forever
        assert "@cycle" in sig


class TestDedupGlued:
    def test_drops_structural_duplicate_keeps_first(self) -> None:
        a1 = FStructure(feats={"CASE": "NOM"}, id=1)
        a2 = FStructure(feats={"CASE": "NOM"}, id=2)  # structural dup of a1
        b = FStructure(feats={"CASE": "GEN"}, id=3)
        out = _dedup_glued([_parse(a1), _parse(a2), _parse(b)])
        # a2 is dropped (dup of a1); first-occurrence order preserved.
        assert [g[1] for g in out] == [a1, b]

    def test_passes_through_all_distinct(self) -> None:
        parses = [
            _parse(FStructure(feats={"CASE": "NOM"}, id=1)),
            _parse(FStructure(feats={"CASE": "GEN"}, id=2)),
            _parse(FStructure(feats={"CASE": "DAT"}, id=3)),
        ]
        assert _dedup_glued(parses) == parses

    def test_empty_input(self) -> None:
        assert _dedup_glued([]) == []
