"""Phase 5e Commit 19: possessive-linker RC with non-pronominal possessor.

Phase 5d Commit 6 and Phase 5e Commit 18 lifted the dual-binding
possessive-linker RC construction for pronominal possessors:

* Commit 6: vowel-final PRON + bound ``-ng`` (``aklat kong binasa``).
* Commit 18: consonant-final PRON + standalone ``na``
  (``aklat namin na binasa``); plus vowel-final PRON + standalone
  ``na`` (``aklat ko na binasa``).

Phase 5e Commit 19 extends the same construction to **non-pronominal
possessors** — common nouns (``aklat ng batang binasa`` "the book
that the child read") and proper names (``aklat ni Juan na binasa``
"the book that Juan read"). The possessor's surface marker ``ng`` /
``ni`` and its phonotactic shape (vowel-final vs consonant-final)
determine which linker variant fires, but the dual-binding
semantics is identical: the GEN-marked possessor is BOTH the head
NP's POSS AND the embedded RC's OBJ-AGENT.

The grammar change is a one-token widening of the second daughter
in the wrap rule, from ``PRON[CASE=GEN]`` to ``NP[CASE=GEN]``. The
``NP[CASE=GEN] → PRON[CASE=GEN]`` rule already in the grammar
makes this a strict generalization that subsumes the PRON case.

A ``(↓1 LEMMA)`` existential constraint is added at the same time
to keep the rule from spuriously firing on PRON-headed NPs (e.g.,
``Kumain ako ng batang kinain niya`` would otherwise wrongly fire
the rule on ``ako + ng bata + -ng + kinain``, treating ``ako`` as
the dual-bound head — pronouns aren't possessable in this shape).
NOUNs / proper nouns carry LEMMA in their f-structure; PRONs and
headless-RC NPs do not.

These tests cover:

* Common-noun possessors (``ng batang binasa``,
  ``ng asong kinain``).
* Proper-noun possessors with ``ni`` (``ni Juan na binasa``,
  ``ni Maria na binasa``).
* Possessor in OBJ position (``Kumain ang aso ng libro ng batang
  binasa``).
* OV / DV / IV variants.
* Negation under the construction.
* POSS / OBJ-AGENT id-equality (the dual-binding signature).
* The ``(↓1 LEMMA)`` head-NP constraint blocks the spurious
  PRON-headed parse for sentences where a NOUN-poss + standard
  relativization composition is the intended reading.
* Regression: pronominal cases (Commit 6 / Commit 18) still work.
* Regression: standard NP-poss + standard relativization with
  overt actor (``libro na binasa ng bata``) still works.
"""

from __future__ import annotations

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _find_node_with_rc_and_poss(
    text: str, slot: str
) -> tuple[FStructure, FStructure, FStructure] | None:
    """Find a parse where ``f.feats[slot]`` has both POSS and an ADJ
    containing an RC. Returns (matrix, slot_node, poss_node) or None."""
    rs = parse_text(text, n_best=15)
    for _, f, _, _ in rs:
        node = f.feats.get(slot)
        if not isinstance(node, FStructure):
            continue
        poss = node.feats.get("POSS")
        adj = node.feats.get("ADJ")
        if isinstance(poss, FStructure) and adj:
            rcs = [m for m in adj if isinstance(m, FStructure) and "PRED" in m.feats]
            if rcs:
                return f, node, poss
    return None


# === Common-noun possessor + RC ===========================================


class TestCommonNounPossessorSubj:
    """``Lumakad ang libro ng batang binasa.`` — head NP is the
    matrix SUBJ; the GEN-NP ``ng bata`` is its possessor and the
    RC's actor."""

    def test_bata_as_possessor(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Lumakad ang libro ng batang binasa.", "SUBJ"
        )
        assert result is not None
        _, subj, poss = result
        assert subj.feats.get("LEMMA") == "libro"
        assert poss.feats.get("LEMMA") == "bata"
        assert poss.feats.get("CASE") == "GEN"
        assert poss.feats.get("MARKER") == "NG"

    def test_aso_as_possessor(self) -> None:
        """``Lumakad ang libro ng asong kinain.`` — different NOUN
        head, OV verb."""
        result = _find_node_with_rc_and_poss(
            "Lumakad ang libro ng asong kinain.", "SUBJ"
        )
        assert result is not None
        _, _, poss = result
        assert poss.feats.get("LEMMA") == "aso"

    def test_poss_and_obj_agent_share_node(self) -> None:
        """The defining structural property: POSS and the RC's
        OBJ-AGENT bind to the SAME f-structure (id-equality)."""
        result = _find_node_with_rc_and_poss(
            "Lumakad ang libro ng batang binasa.", "SUBJ"
        )
        assert result is not None
        _, subj, poss = result
        adj = subj.feats["ADJ"]
        rcs = [m for m in adj if isinstance(m, FStructure)]
        assert rcs
        rc = rcs[0]
        oa = rc.feats.get("OBJ-AGENT")
        assert isinstance(oa, FStructure)
        assert oa is poss

    def test_rc_is_ov(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Lumakad ang libro ng batang binasa.", "SUBJ"
        )
        assert result is not None
        _, subj, _ = result
        adj = subj.feats["ADJ"]
        rcs = [m for m in adj if isinstance(m, FStructure)]
        assert any(rc.feats.get("VOICE") == "OV" for rc in rcs)


# === Proper-noun possessor (ni) ===========================================


class TestProperNounPossessor:
    """Proper names take the ``ni`` GEN marker and the standalone
    ``na`` linker (proper names typically end in a consonant or a
    vowel-form that doesn't fuse with ``-ng`` in modern usage)."""

    def test_ni_juan_with_na_linker(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Lumakad ang libro ni Juan na binasa.", "SUBJ"
        )
        assert result is not None
        _, _, poss = result
        # Proper-noun fstructs carry LEMMA (the lowercased proper
        # name) and a GEN marker (NI rather than NG for personal).
        assert poss.feats.get("LEMMA") == "juan"
        assert poss.feats.get("CASE") == "GEN"

    def test_ni_maria(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Lumakad ang libro ni Maria na binasa.", "SUBJ"
        )
        assert result is not None
        _, _, poss = result
        assert poss.feats.get("LEMMA") == "maria"


# === OBJ-position case ====================================================


class TestNounPossessorObj:
    """``Kumain ang aso ng libro ng batang binasa.`` — the head NP
    ``ng libro`` is the matrix AV-OBJ; the GEN-NP ``ng bata`` is its
    possessor and the RC's actor."""

    def test_obj_position(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Kumain ang aso ng libro ng batang binasa.", "OBJ"
        )
        assert result is not None
        _, obj, poss = result
        assert obj.feats.get("LEMMA") == "libro"
        assert poss.feats.get("LEMMA") == "bata"


# === IV variant ===========================================================


class TestNounPossessorIv:
    """The construction works with IV verbs in S_GAP_NA, just like
    Commit 18's pronominal version. Use ``ipinaggawa`` (BEN bare)
    which has full analyzer coverage."""

    def test_iv_bare(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Lumakad ang libro ng batang ipinaggawa.", "SUBJ"
        )
        assert result is not None
        _, subj, _ = result
        adj = subj.feats["ADJ"]
        rcs = [m for m in adj if isinstance(m, FStructure)]
        assert any(rc.feats.get("VOICE") == "IV" for rc in rcs)


# === Negation under the construction ======================================


class TestNounPossessorNegation:

    def test_negated_rc(self) -> None:
        """``Lumakad ang libro ng batang hindi binasa.`` — RC is
        negated. The S_GAP_NA NEG-recursion handles this."""
        result = _find_node_with_rc_and_poss(
            "Lumakad ang libro ng batang hindi binasa.", "SUBJ"
        )
        assert result is not None
        _, subj, _ = result
        adj = subj.feats["ADJ"]
        rcs = [m for m in adj if isinstance(m, FStructure)]
        assert rcs
        rc = rcs[0]
        assert rc.feats.get("POLARITY") == "NEG"


# === Head-NP must have LEMMA constraint ===================================


class TestHeadLemmaConstraint:
    """The ``(↓1 LEMMA)`` existential constraint on the wrap rule
    blocks the rule from firing when the head NP doesn't carry
    LEMMA — i.e., when the head is a PRON or a headless-RC NP.
    Without this constraint, the widened ``NP[CASE=GEN]`` slot
    would let the rule wrongly absorb a NOUN GEN-NP as the
    "possessor" of a PRON-headed matrix argument."""

    def test_pron_head_blocked_for_construction(self) -> None:
        """``Kumain ako ng batang kinain niya.`` — ``ako`` is the
        matrix SUBJ (PRON, no LEMMA); ``ng batang kinain niya`` is
        the OBJ NP with internal standard RC. The wrap rule must
        NOT fire on ``ako + ng bata + -ng + kinain`` (PRON-headed
        head NP). Verify by finding a parse where OBJ.LEMMA=bata —
        the standard analysis where ``ng batang kinain niya`` is a
        single OBJ NP with internal RC."""
        rs = parse_text("Kumain ako ng batang kinain niya.", n_best=15)
        assert rs
        found = False
        for _, f, _, _ in rs:
            obj = f.feats.get("OBJ")
            if not isinstance(obj, FStructure):
                continue
            if obj.feats.get("LEMMA") != "bata":
                continue
            adj = obj.feats.get("ADJ")
            if not adj:
                continue
            for m in adj:
                if isinstance(m, FStructure) and "PRED" in m.feats:
                    found = True
                    break
            if found:
                break
        assert found, "expected OBJ=bata-with-RC parse"

    def test_pron_head_no_dual_binding(self) -> None:
        """No parse should have ``ako`` bound as the dual-binding
        head NP with ``ng bata`` as both POSS and OBJ-AGENT — that's
        the spurious parse the constraint blocks."""
        rs = parse_text("Kumain ako ng batang kinain niya.", n_best=15)
        for _, f, _, _ in rs:
            subj = f.feats.get("SUBJ")
            if not isinstance(subj, FStructure):
                continue
            # SUBJ.POSS-EXTRACTED would be set if the wrap rule fired
            # on a PRON-headed NP. The constraint should prevent this.
            assert subj.feats.get("POSS-EXTRACTED") != "YES", (
                "wrap rule fired on PRON-headed SUBJ"
            )


# === Regressions ==========================================================


class TestNounPossessorRegressions:

    def test_pronominal_commit_6_still_works(self) -> None:
        """Phase 5d Commit 6's vowel-final PRON + bound ``-ng`` form
        must still parse (the rule generalization preserves it via
        ``NP[CASE=GEN] → PRON[CASE=GEN]``)."""
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata kong kinain.", "SUBJ"
        )
        assert result is not None
        _, subj, poss = result
        assert subj.feats.get("LEMMA") == "bata"
        assert poss.feats.get("NUM") == "SG"
        # PRON possessor has no LEMMA.
        assert poss.feats.get("LEMMA") is None

    def test_pronominal_commit_18_still_works(self) -> None:
        """Phase 5e Commit 18's consonant-final PRON + standalone
        ``na`` form must still parse."""
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata namin na binasa.", "SUBJ"
        )
        assert result is not None
        _, _, poss = result
        assert poss.feats.get("NUM") == "PL"
        assert poss.feats.get("CLUSV") == "EXCL"

    def test_standard_np_poss_only(self) -> None:
        """``Lumakad ang libro ng bata.`` (no RC, just possessive)
        must still parse via the standard NP-poss rule. The wrap
        rule wouldn't fire (no PART[LINK=…] + S_GAP_NA), so the
        baseline isn't disturbed."""
        rs = parse_text("Lumakad ang libro ng bata.", n_best=10)
        assert rs
        found = False
        for _, f, _, _ in rs:
            subj = f.feats.get("SUBJ")
            if not isinstance(subj, FStructure):
                continue
            if subj.feats.get("LEMMA") != "libro":
                continue
            poss = subj.feats.get("POSS")
            if isinstance(poss, FStructure) and poss.feats.get("LEMMA") == "bata":
                found = True
                break
        assert found

    def test_standard_relativization_with_overt_actor(self) -> None:
        """``Lumakad ang libro na binasa ng bata.`` — standard
        relativization with overt GEN actor in the RC. Must still
        parse via the standard ``S_GAP`` wrap (the actor stays
        inside the RC, not extracted)."""
        rs = parse_text("Lumakad ang libro na binasa ng bata.", n_best=10)
        assert rs
        found = False
        for _, f, _, _ in rs:
            subj = f.feats.get("SUBJ")
            if not isinstance(subj, FStructure):
                continue
            adj = subj.feats.get("ADJ")
            if not adj:
                continue
            for m in adj:
                if not isinstance(m, FStructure):
                    continue
                if m.feats.get("PRED") != "READ <SUBJ, OBJ-AGENT>":
                    continue
                oa = m.feats.get("OBJ-AGENT")
                if isinstance(oa, FStructure) and oa.feats.get("LEMMA") == "bata":
                    found = True
                    break
            if found:
                break
        assert found, "expected RC.OBJ-AGENT=bata (overt actor) parse"

    def test_iterated_npposs_unaffected(self) -> None:
        """Right-associative iterated possessives like
        ``libro ng bata ng pamilya`` (libro.POSS=bata,
        bata.POSS=pamilya) must still produce the chain — the
        ``POSS-EXTRACTED`` guard only blocks NP-poss extension on
        wrap-rule outputs, not on regular NP-poss outputs."""
        rs = parse_text("Lumakad ang libro ng bata ng pamilya.", n_best=10)
        assert rs
        found = False
        for _, f, _, _ in rs:
            subj = f.feats.get("SUBJ")
            if not isinstance(subj, FStructure):
                continue
            poss1 = subj.feats.get("POSS")
            if not isinstance(poss1, FStructure):
                continue
            poss2 = poss1.feats.get("POSS")
            if (
                isinstance(poss2, FStructure)
                and poss1.feats.get("LEMMA") == "bata"
                and poss2.feats.get("LEMMA") == "pamilya"
            ):
                found = True
                break
        assert found


# === LMT diagnostics ======================================================


class TestNounPossessorLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Lumakad ang libro ng batang binasa.",
            "Lumakad ang libro ng asong kinain.",
            "Lumakad ang libro ni Juan na binasa.",
            "Lumakad ang libro ni Maria na binasa.",
            "Kumain ang aso ng libro ng batang binasa.",
            "Lumakad ang libro ng batang hindi binasa.",
            "Lumakad ang libro ng batang ipinaggawa.",
        ):
            rs = parse_text(s, n_best=10)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
