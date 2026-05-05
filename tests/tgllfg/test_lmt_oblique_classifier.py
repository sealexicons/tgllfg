"""Phase 5 §8 — sa-NP → typed OBL-θ classifier.

Isolation tests that exercise
:func:`tgllfg.lmt.classify_oblique_slots` over synthetic
f-structures. Pipeline-level tests with a real Tagalog sentence
live in ``test_lmt_oblique_pipeline.py``.
"""

from __future__ import annotations

from tgllfg.core.common import FStructure
from tgllfg.lmt import Role, classify_oblique_slots


def _sa_np(node_id: int, pred: str = "X") -> FStructure:
    """Build a synthetic sa-NP f-structure (CASE=DAT)."""
    return FStructure(feats={"CASE": "DAT", "PRED": pred}, id=node_id)


def _adv(node_id: int, pred: str = "ADV") -> FStructure:
    """Build a non-sa ADJUNCT member (no CASE=DAT)."""
    return FStructure(feats={"PRED": pred}, id=node_id)


# === No-op cases ==========================================================


class TestNoOpCases:
    """The classifier should be a no-op when there's nothing to do."""

    def test_no_obl_roles_in_mapping(self) -> None:
        sa = _sa_np(1, "PALENGKE")
        f = FStructure(feats={"ADJUNCT": frozenset({sa})})
        diagnostics = classify_oblique_slots(
            f, mapping={Role.AGENT: "SUBJ", Role.PATIENT: "OBJ"}
        )
        assert diagnostics == []
        # ADJUNCT untouched.
        assert f.feats["ADJUNCT"] == frozenset({sa})
        assert "OBL-LOC" not in f.feats

    def test_no_adjunct_in_fstructure(self) -> None:
        f = FStructure(feats={"PRED": "X <SUBJ, OBL-LOC>"})
        diagnostics = classify_oblique_slots(
            f, mapping={Role.ACTOR: "SUBJ", Role.LOCATION: "OBL-LOC"}
        )
        assert diagnostics == []
        # Nothing to move; OBL-LOC stays unfilled (completeness will
        # flag downstream).
        assert "OBL-LOC" not in f.feats

    def test_adjunct_present_but_no_sa_np(self) -> None:
        # ADJUNCT contains a non-sa member (e.g., adverbial enclitic
        # from §7.3). Classifier should leave it alone.
        adv = _adv(1, "NA")
        f = FStructure(feats={"ADJUNCT": frozenset({adv})})
        diagnostics = classify_oblique_slots(
            f, mapping={Role.ACTOR: "SUBJ", Role.LOCATION: "OBL-LOC"}
        )
        # Diagnostic about unfilled OBL slot — but no sa to move.
        assert all(d.kind == "lmt-mismatch" for d in diagnostics)
        # The non-sa adjunct stays.
        assert f.feats["ADJUNCT"] == frozenset({adv})

    def test_empty_adjunct_set(self) -> None:
        f = FStructure(feats={"ADJUNCT": frozenset()})
        diagnostics = classify_oblique_slots(
            f, mapping={Role.ACTOR: "SUBJ", Role.LOCATION: "OBL-LOC"}
        )
        assert diagnostics == []
        # Empty ADJUNCT stays empty.
        assert f.feats.get("ADJUNCT") == frozenset()


# === Single-role classification ===========================================


class TestSingleObl:
    """One OBL-θ role + one or more sa-NPs in ADJUNCT."""

    def test_one_role_one_sa_np_moves(self) -> None:
        sa = _sa_np(1, "PALENGKE")
        f = FStructure(feats={"ADJUNCT": frozenset({sa})})
        diagnostics = classify_oblique_slots(
            f, mapping={Role.ACTOR: "SUBJ", Role.LOCATION: "OBL-LOC"}
        )
        assert diagnostics == []
        # sa-NP moved to OBL-LOC; ADJUNCT removed (was only member).
        assert f.feats["OBL-LOC"] is sa
        assert "ADJUNCT" not in f.feats

    def test_one_role_two_sa_nps_consumes_first_only(self) -> None:
        sa1 = _sa_np(1, "PALENGKE")
        sa2 = _sa_np(2, "BAHAY")
        f = FStructure(feats={"ADJUNCT": frozenset({sa1, sa2})})
        diagnostics = classify_oblique_slots(
            f, mapping={Role.ACTOR: "SUBJ", Role.LOCATION: "OBL-LOC"}
        )
        # One leftover sa-NP → informational diagnostic.
        assert len(diagnostics) == 1
        assert diagnostics[0].kind == "lmt-mismatch"
        # OBL-LOC filled with sa1 (lower id, consumed first).
        assert f.feats["OBL-LOC"] is sa1
        # sa2 stays in ADJUNCT as a locative modifier.
        assert f.feats["ADJUNCT"] == frozenset({sa2})

    def test_mixed_adjunct_only_sa_classified(self) -> None:
        # ADJUNCT has one sa-NP and one non-sa adverbial. Classifier
        # only consumes the sa-NP.
        sa = _sa_np(1, "PALENGKE")
        adv = _adv(2, "NA")
        f = FStructure(feats={"ADJUNCT": frozenset({sa, adv})})
        diagnostics = classify_oblique_slots(
            f, mapping={Role.ACTOR: "SUBJ", Role.LOCATION: "OBL-LOC"}
        )
        assert diagnostics == []
        assert f.feats["OBL-LOC"] is sa
        # adv stays in ADJUNCT.
        assert f.feats["ADJUNCT"] == frozenset({adv})


# === Multi-role classification ============================================


class TestMultipleObl:
    """Multiple OBL-θ roles. Cardinality matching by a-structure
    order vs sorted sa-NP id."""

    def test_two_roles_two_sa_nps_matched_in_order(self) -> None:
        sa1 = _sa_np(1, "PALENGKE")
        sa2 = _sa_np(2, "BAHAY")
        f = FStructure(feats={"ADJUNCT": frozenset({sa1, sa2})})
        # Mapping is a dict; iteration order matches insertion.
        # ROLE_HIERARCHY-friendly order: LOCATION first, then GOAL.
        mapping = {
            Role.ACTOR: "SUBJ",
            Role.LOCATION: "OBL-LOC",
            Role.GOAL: "OBL-GOAL",
        }
        diagnostics = classify_oblique_slots(f, mapping=mapping)
        assert diagnostics == []
        # OBL-LOC took sa1 (first in insertion order maps to first
        # in id order); OBL-GOAL took sa2.
        assert f.feats["OBL-LOC"] is sa1
        assert f.feats["OBL-GOAL"] is sa2
        assert "ADJUNCT" not in f.feats

    def test_two_roles_one_sa_np_emits_diagnostic(self) -> None:
        sa = _sa_np(1, "PALENGKE")
        f = FStructure(feats={"ADJUNCT": frozenset({sa})})
        mapping = {
            Role.ACTOR: "SUBJ",
            Role.LOCATION: "OBL-LOC",
            Role.GOAL: "OBL-GOAL",
        }
        diagnostics = classify_oblique_slots(f, mapping=mapping)
        assert len(diagnostics) == 1
        assert diagnostics[0].kind == "lmt-mismatch"
        # First role got the sa-NP; the second role is unfilled
        # (completeness will surface).
        assert f.feats["OBL-LOC"] is sa
        assert "OBL-GOAL" not in f.feats


# === Defensive cases ======================================================


class TestDefensive:
    """Edge cases that shouldn't break the classifier."""

    def test_target_gf_already_present_does_not_overwrite(self) -> None:
        # Defensive: if some other path pre-filled OBL-LOC, the
        # classifier does not overwrite. (No path currently writes
        # OBL-X before the classifier runs, but the guard exists.)
        sa = _sa_np(1, "PALENGKE")
        existing = FStructure(feats={"PRED": "PRE-FILLED"}, id=99)
        f = FStructure(feats={
            "ADJUNCT": frozenset({sa}),
            "OBL-LOC": existing,
        })
        diagnostics = classify_oblique_slots(
            f, mapping={Role.ACTOR: "SUBJ", Role.LOCATION: "OBL-LOC"}
        )
        # OBL-LOC unchanged.
        assert f.feats["OBL-LOC"] is existing
        # sa-NP stays in ADJUNCT (consumed slot guard skipped it).
        # No diagnostic for cardinality mismatch since the role
        # iteration consumed its target.
        assert sa in (f.feats.get("ADJUNCT") or frozenset())
        assert diagnostics == []

    def test_adjunct_value_not_a_frozenset(self) -> None:
        # Defensive: ADJUNCT might somehow be a non-set value.
        # Classifier should bail gracefully.
        f = FStructure(feats={"ADJUNCT": "not a set"})
        diagnostics = classify_oblique_slots(
            f, mapping={Role.LOCATION: "OBL-LOC"}
        )
        assert diagnostics == []
        # Untouched.
        assert f.feats["ADJUNCT"] == "not a set"

    def test_adjunct_member_without_case_feature(self) -> None:
        # An ADJUNCT member that happens to not have CASE at all
        # (e.g., an embedded clause) should be left alone.
        embedded = FStructure(feats={"PRED": "EMBEDDED"}, id=1)
        sa = _sa_np(2, "PALENGKE")
        f = FStructure(feats={"ADJUNCT": frozenset({embedded, sa})})
        diagnostics = classify_oblique_slots(
            f, mapping={Role.LOCATION: "OBL-LOC"}
        )
        assert diagnostics == []
        # sa moved to OBL-LOC; embedded stays in ADJUNCT.
        assert f.feats["OBL-LOC"] is sa
        assert f.feats["ADJUNCT"] == frozenset({embedded})
