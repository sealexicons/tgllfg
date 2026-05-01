"""Phase 5c §8 follow-on (Commit 6): multi-OBL semantic
disambiguation.

Phase 5 §8 deferred multi-OBL ambiguity: when two OBL-θ roles
compete for two sa-NPs, the classifier matched positionally.
Phase 5c lifts that deferral by consulting each sa-NP's
``LEMMA`` (now percolated through the grammar's NP / N rules)
against small lemma → semantic-class tables (``_PLACE_LEMMAS``,
``_ANIMATE_LEMMAS``):

* PLACE-class lemmas (``palengke``, ``eskwela``, ``bahay``…)
  are preferred for ``OBL-LOC`` / ``OBL-GOAL`` slots.
* ANIMATE-class lemmas (``bata``, ``nanay``, ``lalaki``…) are
  preferred for ``OBL-RECIP`` / ``OBL-BEN`` slots.

Positional matching is the fallback when no semantic preference
applies (e.g., ``OBL-INSTR`` slots, sa-NPs with unknown lemmas,
or two sa-NPs of the same class).

These tests cover:

* ``LEMMA`` percolation: every NP's f-structure carries the
  head noun's lemma.
* Single-OBL behavior unchanged.
* Multi-OBL with both lemma classes known — order-independent
  semantic disambiguation: ``sa bata sa eskwela`` and
  ``sa eskwela sa bata`` both produce
  OBL-RECIP=bata, OBL-LOC=eskwela.
* Multi-OBL with same-class sa-NPs — positional fallback.
* Helper functions ``_semantic_class`` and ``_gf_prefers_class``.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.lmt.oblique_classifier import (
    _ANIMATE_LEMMAS,
    _PLACE_LEMMAS,
    _gf_prefers_class,
    _semantic_class,
)
from tgllfg.pipeline import parse_text


def _first(text: str) -> tuple[FStructure, list]:
    rs = parse_text(text)
    assert rs, f"no parse for {text!r}"
    _, f, _, diags = rs[0]
    return f, diags


def _find_with_obl(text: str, *gfs: str) -> FStructure | None:
    """Return the first parse whose matrix has all the named OBL-θ
    governable functions (e.g., OBL-RECIP and OBL-LOC). The 4-NP
    AV ditransitive rule is one of multiple parses for ditransitive
    sentences; this helper picks the canonical one."""
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        if all(isinstance(f.feats.get(gf), FStructure) for gf in gfs):
            return f
    return None


# === LEMMA percolation through the NP / N projections ===================


class TestLemmaPercolation:

    def test_subj_carries_lemma(self) -> None:
        f, _ = _first("Lumakad ang bata sa palengke.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"

    def test_obl_carries_lemma(self) -> None:
        f, _ = _first("Lumakad ang bata sa palengke.")
        # The locative parse has palengke as OBL-LOC.
        oloc = f.feats.get("OBL-LOC")
        if isinstance(oloc, FStructure):
            assert oloc.feats.get("LEMMA") == "palengke"
        else:
            adj = f.feats.get("ADJUNCT")
            assert adj is not None
            members = list(adj)  # type: ignore[arg-type]
            sa = next(
                m for m in members
                if isinstance(m, FStructure) and m.feats.get("CASE") == "DAT"
            )
            assert sa.feats.get("LEMMA") == "palengke"

    def test_obj_carries_lemma(self) -> None:
        f, _ = _first("Kumain ang bata ng isda.")
        obj = f.feats.get("OBJ")
        assert isinstance(obj, FStructure)
        assert obj.feats.get("LEMMA") == "isda"


# === Helpers: _semantic_class and _gf_prefers_class =====================


class TestClassifierHelpers:

    def test_place_class_lookup(self) -> None:
        np = FStructure(feats={"LEMMA": "palengke"})
        assert _semantic_class(np) == "PLACE"

    def test_animate_class_lookup(self) -> None:
        np = FStructure(feats={"LEMMA": "bata"})
        assert _semantic_class(np) == "ANIMATE"

    def test_unknown_lemma_returns_none(self) -> None:
        np = FStructure(feats={"LEMMA": "unknown_lemma"})
        assert _semantic_class(np) is None

    def test_no_lemma_returns_none(self) -> None:
        np = FStructure(feats={})
        assert _semantic_class(np) is None

    def test_obl_loc_prefers_place(self) -> None:
        assert _gf_prefers_class("OBL-LOC") == "PLACE"

    def test_obl_recip_prefers_animate(self) -> None:
        assert _gf_prefers_class("OBL-RECIP") == "ANIMATE"

    def test_obl_instr_no_preference(self) -> None:
        # OBL-INSTR has no semantic preference; positional applies.
        assert _gf_prefers_class("OBL-INSTR") is None


# === Single-OBL behaviour unchanged ======================================


class TestSingleOblPositional:
    """Single OBL-θ slot — semantic disambiguation doesn't fire;
    positional matching (which is trivially correct for a 1-element
    list) takes over."""

    def test_lakad_loc_unchanged(self) -> None:
        f = _find_with_obl("Lumakad ang bata sa palengke.", "OBL-LOC")
        assert f is not None
        assert f.feats["OBL-LOC"].feats.get("LEMMA") == "palengke"  # type: ignore[union-attr]


# === Multi-OBL with semantic disambiguation =============================


class TestMultiOblSemantic:
    """Both sa-NPs have known semantic classes — different classes,
    so the classifier matches each to its preferred slot regardless
    of surface order."""

    def test_recip_loc_idiomatic_order(self) -> None:
        # ``Nagbigay ang nanay ng libro sa bata sa eskwela`` —
        # idiomatic RECIP-LOC order. bata (animate) → OBL-RECIP;
        # eskwela (place) → OBL-LOC.
        f = _find_with_obl(
            "Nagbigay ang nanay ng libro sa bata sa eskwela.",
            "OBL-RECIP", "OBL-LOC",
        )
        assert f is not None
        assert f.feats["OBL-RECIP"].feats.get("LEMMA") == "bata"  # type: ignore[union-attr]
        assert f.feats["OBL-LOC"].feats.get("LEMMA") == "eskwela"  # type: ignore[union-attr]

    def test_loc_recip_reversed_surface_order(self) -> None:
        # ``Nagbigay ang nanay ng libro sa eskwela sa bata`` —
        # reversed surface order. The classifier must NOT match
        # positionally (which would put eskwela in OBL-RECIP) —
        # semantic disambiguation overrides surface position.
        f = _find_with_obl(
            "Nagbigay ang nanay ng libro sa eskwela sa bata.",
            "OBL-RECIP", "OBL-LOC",
        )
        assert f is not None
        assert f.feats["OBL-RECIP"].feats.get("LEMMA") == "bata"  # type: ignore[union-attr]
        assert f.feats["OBL-LOC"].feats.get("LEMMA") == "eskwela"  # type: ignore[union-attr]


# === Direct unit tests on the classifier =================================


class TestClassifierDirect:
    """Construct synthetic f-structures and exercise
    ``classify_oblique_slots`` directly. This avoids any noise
    from the larger parser pipeline."""

    def _setup(self):
        from tgllfg.lmt.oblique_classifier import classify_oblique_slots
        from tgllfg.lmt import Role
        return classify_oblique_slots, Role

    def test_two_sa_nps_known_classes_match_semantically(self) -> None:
        classify_oblique_slots, Role = self._setup()
        # Two sa-NPs: bata (animate) at id=1, eskwela (place) at id=2.
        # Mapping: AGENT→SUBJ, RECIPIENT→OBL-RECIP, LOCATION→OBL-LOC.
        sa_animate = FStructure(
            feats={"CASE": "DAT", "LEMMA": "bata"}, id=1
        )
        sa_place = FStructure(
            feats={"CASE": "DAT", "LEMMA": "eskwela"}, id=2
        )
        f = FStructure(feats={
            "ADJUNCT": frozenset({sa_animate, sa_place}),
        })
        diagnostics = classify_oblique_slots(
            f,
            mapping={
                Role.AGENT: "SUBJ",
                Role.RECIPIENT: "OBL-RECIP",
                Role.LOCATION: "OBL-LOC",
            },
        )
        assert diagnostics == []
        assert f.feats["OBL-RECIP"] is sa_animate
        assert f.feats["OBL-LOC"] is sa_place

    def test_reversed_id_order_still_matches_semantically(self) -> None:
        # Place id=1, animate id=2. Surface-order positional would
        # assign place to first OBL slot; semantic disambiguation
        # should still match by class.
        classify_oblique_slots, Role = self._setup()
        sa_place = FStructure(
            feats={"CASE": "DAT", "LEMMA": "eskwela"}, id=1
        )
        sa_animate = FStructure(
            feats={"CASE": "DAT", "LEMMA": "bata"}, id=2
        )
        f = FStructure(feats={
            "ADJUNCT": frozenset({sa_place, sa_animate}),
        })
        classify_oblique_slots(
            f,
            mapping={
                Role.AGENT: "SUBJ",
                Role.RECIPIENT: "OBL-RECIP",
                Role.LOCATION: "OBL-LOC",
            },
        )
        assert f.feats["OBL-RECIP"] is sa_animate
        assert f.feats["OBL-LOC"] is sa_place

    def test_same_class_falls_back_to_positional(self) -> None:
        # Both sa-NPs are PLACE — semantic preference can't break
        # the tie. Falls back to positional (a-structure order vs
        # id-sorted sa-NPs).
        classify_oblique_slots, Role = self._setup()
        sa1 = FStructure(
            feats={"CASE": "DAT", "LEMMA": "palengke"}, id=1
        )
        sa2 = FStructure(
            feats={"CASE": "DAT", "LEMMA": "eskwela"}, id=2
        )
        f = FStructure(feats={
            "ADJUNCT": frozenset({sa1, sa2}),
        })
        classify_oblique_slots(
            f,
            mapping={
                Role.AGENT: "SUBJ",
                Role.LOCATION: "OBL-LOC",
                Role.GOAL: "OBL-GOAL",
            },
        )
        # Both LOC and GOAL prefer PLACE; semantic match is
        # ambiguous (greedy picks the first un-consumed match for
        # each role in a-structure order). Positional intra-class
        # ordering kicks in.
        assert isinstance(f.feats.get("OBL-LOC"), FStructure)
        assert isinstance(f.feats.get("OBL-GOAL"), FStructure)
        # Both sa-NPs consumed.
        assert {f.feats["OBL-LOC"], f.feats["OBL-GOAL"]} == {sa1, sa2}

    def test_unknown_lemmas_fall_back_to_positional(self) -> None:
        # Neither sa-NP has a known semantic class; positional wins.
        classify_oblique_slots, Role = self._setup()
        sa1 = FStructure(
            feats={"CASE": "DAT", "LEMMA": "x_unknown"}, id=1
        )
        sa2 = FStructure(
            feats={"CASE": "DAT", "LEMMA": "y_unknown"}, id=2
        )
        f = FStructure(feats={
            "ADJUNCT": frozenset({sa1, sa2}),
        })
        classify_oblique_slots(
            f,
            mapping={
                Role.AGENT: "SUBJ",
                Role.RECIPIENT: "OBL-RECIP",
                Role.LOCATION: "OBL-LOC",
            },
        )
        # Positional: a-structure order is RECIPIENT before
        # LOCATION; sa-NPs sorted by id give sa1 (id=1) then
        # sa2 (id=2). So OBL-RECIP=sa1, OBL-LOC=sa2.
        assert f.feats["OBL-RECIP"] is sa1
        assert f.feats["OBL-LOC"] is sa2


# === Tables coverage =====================================================


class TestSemanticTables:

    def test_place_lemmas_nonempty(self) -> None:
        assert "palengke" in _PLACE_LEMMAS
        assert "eskwela" in _PLACE_LEMMAS

    def test_animate_lemmas_nonempty(self) -> None:
        assert "bata" in _ANIMATE_LEMMAS
        assert "nanay" in _ANIMATE_LEMMAS

    def test_tables_disjoint(self) -> None:
        # PLACE and ANIMATE should never overlap.
        assert _PLACE_LEMMAS.isdisjoint(_ANIMATE_LEMMAS)
