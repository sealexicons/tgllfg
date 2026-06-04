# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5l Commit 8: purpose subordination — para / upang.

Roadmap §12.1 / plan-of-record §5.4, §6 Commit 8. One new rule
in ``cfg/subordination.py``:

    SubordClause → PART[COMP_TYPE=PURP] S       (builder)

Both purpose PART entries (para / upang — Commit 1 lex) feed
this single builder. ``upang`` carries REGISTER=FORMAL on its
PART f-structure; the feat percolates onto the SubordClause
f-structure via ``(↑) = ↓2``.

``para`` is polysemous with the Phase 5e PREP[BENEFICIARY]
entry (``para sa NP`` "for X"). The chart resolves by immediate
constituent — PREP path takes a DAT-NP; PART path takes an S.
The two contexts don't overlap structurally.

End-to-end target sentences:

    Pumunta si Juan para kumain si Maria.
        # "Juan went so that Maria ate."           (post-matrix para)
    Para kumain si Maria, pumunta si Juan.
        # "In order for Maria to eat, Juan went."  (pre-matrix para)
    Pumunta si Juan upang kumain si Maria.
        # "Juan went in order for Maria to eat."   (post-matrix upang)
"""

from tgllfg.core.pipeline import parse_text


def _adjunct_with_subord_type(fs, subord_type: str):
    adjuncts = fs.feats.get("ADJUNCT")
    if adjuncts is None:
        return None
    for adj in adjuncts:
        if adj.feats.get("SUBORD_TYPE") == subord_type:
            return adj
    return None


# === para — purpose ==================================================


class TestParaPurpose:
    """``para`` "in order to / so that" embeds a clause as a
    purpose adjunct. SUBORD_TYPE=PURP."""

    def test_para_post_matrix(self) -> None:
        parses = parse_text("Pumunta si Juan para kumain si Maria.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith("PUNTA")
        purp = _adjunct_with_subord_type(fs, "PURP")
        assert purp is not None
        assert (purp.feats.get("PRED") or "").startswith("EAT")

    def test_para_pre_matrix(self) -> None:
        parses = parse_text("Para kumain si Maria, pumunta si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        purp = _adjunct_with_subord_type(fs, "PURP")
        assert purp is not None
        assert (purp.feats.get("PRED") or "").startswith("EAT")

    def test_para_pre_post_same_fstruct(self) -> None:
        pre = parse_text("Para kumain si Maria, pumunta si Juan.")[0][1]
        post = parse_text("Pumunta si Juan para kumain si Maria.")[0][1]
        pre_p = _adjunct_with_subord_type(pre, "PURP")
        post_p = _adjunct_with_subord_type(post, "PURP")
        assert pre_p is not None and post_p is not None
        assert (pre_p.feats.get("PRED") or "")[:3] == (
            post_p.feats.get("PRED") or ""
        )[:3]


# === upang — formal purpose ==========================================


class TestUpangPurpose:
    """``upang`` is the formal-register variant of ``para``.
    Same syntactic distribution; carries REGISTER=FORMAL on its
    PART daughter."""

    def test_upang_post_matrix(self) -> None:
        parses = parse_text("Pumunta si Juan upang kumain si Maria.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        purp = _adjunct_with_subord_type(fs, "PURP")
        assert purp is not None
        assert (purp.feats.get("PRED") or "").startswith("EAT")

    def test_upang_pre_matrix(self) -> None:
        parses = parse_text("Upang kumain si Maria, pumunta si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        purp = _adjunct_with_subord_type(fs, "PURP")
        assert purp is not None


# === para PREP/PART polysemy ========================================


class TestParaPolysemy:
    """Both ``para[PREP]`` (Phase 5e) and ``para[PART]`` (Phase 5l)
    surface in the lex; the grammar consumes the right one per
    immediate-constituent context."""

    def test_para_part_consumed_in_subord_context(self) -> None:
        # ``para kumain si Maria`` — PART path fires (S complement),
        # produces SUBORD_TYPE=PURP on adjunct.
        parses = parse_text("Pumunta si Juan para kumain si Maria.")
        _ct, fs, _astr, _diags = parses[0]
        purp = _adjunct_with_subord_type(fs, "PURP")
        assert purp is not None
        # No PREP_TYPE=BENEFICIARY artifact on the matrix or adjunct.
        assert fs.feats.get("PREP_TYPE") != "BENEFICIARY"
        assert purp.feats.get("PREP_TYPE") != "BENEFICIARY"


# === PURP × negation =================================================


class TestNegatedInnerPurpose:
    """Inner clause of a PURP subord can be negated."""

    def test_para_negated_inner(self) -> None:
        parses = parse_text(
            "Pumunta si Juan para hindi kumain si Maria."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        purp = _adjunct_with_subord_type(fs, "PURP")
        assert purp is not None
        assert purp.feats.get("POLARITY") == "NEG"


class TestNegatedMatrixPurpose:
    """Matrix-clause negation composes orthogonally with PURP."""

    def test_para_negated_matrix(self) -> None:
        parses = parse_text(
            "Hindi pumunta si Juan para kumain si Maria."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("POLARITY") == "NEG"
        purp = _adjunct_with_subord_type(fs, "PURP")
        assert purp is not None
        assert purp.feats.get("POLARITY") != "NEG"


# === SUBORD_TYPE disjointness ========================================


class TestSubordTypeDisjoint:
    """PURP doesn't leak to other SUBORD_TYPEs."""

    def test_para_only_purp(self) -> None:
        parses = parse_text("Pumunta si Juan para kumain si Maria.")
        _ct, fs, _astr, _diags = parses[0]
        assert _adjunct_with_subord_type(fs, "PURP") is not None
        for other in ("COND", "CONC", "TEMP_BEFORE", "TEMP_AFTER",
                      "TEMP_WHILE", "TEMP_UNTIL", "TEMP_SINCE"):
            assert _adjunct_with_subord_type(fs, other) is None


# === C-tree shape ====================================================


class TestCTreeShape:
    """Pre-matrix has 3 daughters (SubordClause + PUNCT + S);
    post-matrix has 2 daughters (S + SubordClause)."""

    def test_para_post_matrix_two_daughters(self) -> None:
        parses = parse_text("Pumunta si Juan para kumain si Maria.")
        ctree, _fs, _astr, _diags = parses[0]
        labels = [c.label for c in ctree.children]
        assert labels[0].startswith("S")
        assert labels[1].startswith("SubordClause")

    def test_para_pre_matrix_three_daughters(self) -> None:
        parses = parse_text("Para kumain si Maria, pumunta si Juan.")
        ctree, _fs, _astr, _diags = parses[0]
        labels = [c.label for c in ctree.children]
        assert labels[0].startswith("SubordClause")
        assert labels[1].startswith("PUNCT")
        assert labels[2].startswith("S")


# === NP-coord inside =================================================


class TestNPCoordInsidePurp:
    """Phase 5k NP-coord SUBJ inside a purpose clause."""

    def test_para_inner_np_coord(self) -> None:
        parses = parse_text(
            "Pumunta si Juan para kumain si Maria at si Pedro."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        purp = _adjunct_with_subord_type(fs, "PURP")
        assert purp is not None
        inner_subj = purp.feats.get("SUBJ")
        assert inner_subj is not None
        assert inner_subj.feats.get("COORD") == "AND"


# === Phase 11.B.3 — bare-V purposive PRO inside-out binding ============


class TestPurposivePROBinding:
    """Phase 11.B.3 c2: closes Candidate E in
    ``docs/fu-extension-audit.md`` §2.5. The bare-V purposive
    variants (subordination.py:458-501) replaced the prior
    ``(↑ SUBJ PRED) = 'PRO'`` placeholder with the inside-out
    binding ``(↑ SUBJ) = ((ADJUNCT ↑) SUBJ)``. The SubordClause's
    SUBJ is now structurally identified with the matrix SUBJ
    (functional control via the Dalrymple 2001 §11 idiom).

    Uses the set-valued ``parents_via`` extension (Phase 11.B.4.eng,
    PR #207) since matrix attachment puts the SubordClause in the
    matrix's ADJUNCT set.

    Covers all four sub-rules:

    * (a) bare-V INTR (``para makatapos``)
    * (b) V-TR with no overt OBJ (``para magluto``, OBJ stays PRO
          — Class-1 absorbed patient)
    * (c) V-TR + GEN-NP OBJ (``para makatapos ng trabaho``)
    * (d) V + DAT-NP adjunct (``para makakain sa kanya``)

    Plus all three matrix-attachment shapes (post-matrix-no-comma,
    pre-matrix-with-comma, post-matrix-with-comma)."""

    def _purp(self, sent: str):
        parses = parse_text(sent)
        assert len(parses) >= 1, f"no parse for {sent!r}"
        _ct, fs, _astr, _diags = parses[0]
        purp = _adjunct_with_subord_type(fs, "PURP")
        assert purp is not None, f"no PURP adjunct in {sent!r}"
        return fs, purp

    def test_purp_bare_V_INTR_pron_subject(self) -> None:
        # Variant (a): PART + V[INTR]; matrix SUBJ is PRON `ako`.
        fs, purp = self._purp("Kumain ako para makatapos.")
        matrix_subj = fs.feats.get("SUBJ")
        purp_subj = purp.feats.get("SUBJ")
        assert matrix_subj is not None and purp_subj is not None
        # Inside-out binding: SAME f-structure (identity check).
        assert id(matrix_subj) == id(purp_subj)
        # No PRED='PRO' placeholder anymore.
        assert purp_subj.feats.get("PRED") != "PRO"
        # Matrix SUBJ features percolate to purp SUBJ.
        assert matrix_subj.feats.get("CASE") == purp_subj.feats.get("CASE")

    def test_purp_V_TR_no_overt_obj(self) -> None:
        # Variant (b): PART + V[TR]; matrix SUBJ is PRON `ako`.
        # OBJ stays PRED='PRO' (Class-1 absorbed patient).
        fs, purp = self._purp("Kumain ako para magluto.")
        matrix_subj = fs.feats.get("SUBJ")
        purp_subj = purp.feats.get("SUBJ")
        assert id(matrix_subj) == id(purp_subj)
        # OBJ slot intentionally still PRO (no overt object).
        purp_obj = purp.feats.get("OBJ")
        assert purp_obj is not None
        assert purp_obj.feats.get("PRED") == "PRO"

    def test_purp_V_TR_with_gen_obj(self) -> None:
        # Variant (c): PART + V + GEN-NP; matrix SUBJ is PRON `ako`.
        fs, purp = self._purp("Kumain ako para makatapos ng trabaho.")
        matrix_subj = fs.feats.get("SUBJ")
        purp_subj = purp.feats.get("SUBJ")
        assert id(matrix_subj) == id(purp_subj)
        # OBJ now bound to overt GEN-NP, not PRO.
        purp_obj = purp.feats.get("OBJ")
        assert purp_obj is not None
        assert purp_obj.feats.get("LEMMA") == "trabaho"

    def test_purp_named_subj_post_matrix(self) -> None:
        # Variant (a) with NAME subject: matrix SUBJ has LEMMA='juan'.
        fs, purp = self._purp("Pumunta si Juan para makatapos.")
        matrix_subj = fs.feats.get("SUBJ")
        purp_subj = purp.feats.get("SUBJ")
        assert id(matrix_subj) == id(purp_subj)
        # Both share LEMMA from matrix.
        assert matrix_subj.feats.get("LEMMA") == "juan"
        assert purp_subj.feats.get("LEMMA") == "juan"

    def test_purp_pre_matrix_with_comma(self) -> None:
        # Pre-matrix attachment via the comma rule — still resolves
        # because matrix ADJUNCT contains the SubordClause regardless
        # of c-structure surface order.
        fs, purp = self._purp("Para makatapos, kumain ako.")
        matrix_subj = fs.feats.get("SUBJ")
        purp_subj = purp.feats.get("SUBJ")
        assert id(matrix_subj) == id(purp_subj)

    def test_purp_upang_formal_variant(self) -> None:
        # ``upang`` (REGISTER=FORMAL) shares the same purposive
        # builder and inherits the inside-out binding.
        fs, purp = self._purp("Kumain ako upang makatapos.")
        matrix_subj = fs.feats.get("SUBJ")
        purp_subj = purp.feats.get("SUBJ")
        assert id(matrix_subj) == id(purp_subj)


# === Phase 11.B.3 — extended verification on unattested grammatical
#                    Class-3 edge cases =================================


class TestPurposivePROBindingEdgeCases:
    """Phase 11.B.3 c2 extended verification. The base
    ``TestPurposivePROBinding`` class covers attested forms from the
    Phase 9.X.c50 introduction; this class adds **unattested but
    grammatical** Class-3 edge cases to exercise the inside-out
    binding under feature-rich matrix SUBJs (coordinated, 3SG pron,
    negation-wrapped).

    These cases are not present in the audit corpus but are licit
    Tagalog per S&O 1972 §6.6. They verify the binding's robustness
    under matrix features that did not appear in the original
    fixture set."""

    def _purp(self, sent: str):
        parses = parse_text(sent)
        assert len(parses) >= 1, f"no parse for {sent!r}"
        _ct, fs, _astr, _diags = parses[0]
        purp = _adjunct_with_subord_type(fs, "PURP")
        assert purp is not None, f"no PURP adjunct in {sent!r}"
        return fs, purp

    def test_purp_coord_np_matrix_subj(self) -> None:
        # Unattested: matrix SUBJ is a NP-COORD ``si Juan at si
        # Maria``. The inside-out binding must propagate the COORD
        # f-structure to the purposive's SUBJ — both should report
        # COORD='AND' and share the same CONJUNCTS set.
        fs, purp = self._purp(
            "Kumain si Juan at si Maria para makatapos."
        )
        matrix_subj = fs.feats.get("SUBJ")
        purp_subj = purp.feats.get("SUBJ")
        assert id(matrix_subj) == id(purp_subj)
        # COORD feature propagates through the binding.
        assert matrix_subj.feats.get("COORD") == "AND"
        assert purp_subj.feats.get("COORD") == "AND"

    def test_purp_3sg_pron_matrix_subj(self) -> None:
        # Unattested in the original corpus: 3SG clitic pronoun
        # ``siya`` as matrix SUBJ. Verifies the binding works for
        # non-1SG pronouns (the original fixture used ``ako``).
        fs, purp = self._purp("Kumain siya para makatapos.")
        matrix_subj = fs.feats.get("SUBJ")
        purp_subj = purp.feats.get("SUBJ")
        assert id(matrix_subj) == id(purp_subj)
        # Clitic features propagate.
        assert matrix_subj.feats.get("is_clitic") == purp_subj.feats.get(
            "is_clitic"
        )

    def test_purp_neg_wrapped_matrix(self) -> None:
        # Unattested: matrix S is wrapped by the Phase 4 §7.2
        # ``S → PART[NEG] S`` hindi-rule. The purposive attachment
        # fires on the OUTER S (post-NEG-wrap), so ``(ADJUNCT ↑)``
        # finds the wrapped matrix. The binding must still resolve
        # to the matrix SUBJ regardless of NEG layering.
        fs, purp = self._purp("Hindi kumain si Juan para makatapos.")
        matrix_subj = fs.feats.get("SUBJ")
        purp_subj = purp.feats.get("SUBJ")
        assert id(matrix_subj) == id(purp_subj)
        # NEG polarity sits on the matrix, not the purposive.
        assert fs.feats.get("POLARITY") == "NEG"
        assert purp.feats.get("POLARITY") != "NEG"


# === Phase 11.B.3 — Class-2 scope-verification negative tests ==========


class TestUnflippedClass2PreservedAsPRO:
    """Phase 11.B.3 c2 scope verification. The per-instance audit
    in ``docs/fu-extension-audit.md`` Appendix C identifies 10
    Class-2 (anaphoric / discourse-bound) PRO sites that are
    INTENTIONALLY NOT flipped to inside-out binding — the rule
    comments explicitly select anaphoric resolution to avoid
    feature-clash hazards (e.g., the canonical
    ``clause.py:5292`` Wala-RC CASE-conflict avoidance).

    These tests anchor the scope decision by asserting that
    Class-2 sites still produce ``PRED='PRO'`` on the relevant
    SUBJ slot. A regression here would mean the 11.B.3 change
    inadvertently broadened beyond Class-3."""

    def test_class2_tough_construction_inner_subj_stays_pro(self) -> None:
        # clause.py:1514 (tough): ``Mahirap kumain.`` — the V-INF
        # ``kumain`` is matrix SUBJ; its inner SUBJ is the absorbed
        # PRO (generic "for anyone to eat"). The rule's
        # ``(↓2 SUBJ PRED) = 'PRO'`` equation must keep firing.
        parses = parse_text("Mahirap kumain.")
        _ct, fs, _astr, _diags = parses[0]
        matrix_subj = fs.feats.get("SUBJ")
        assert matrix_subj is not None
        inner_subj = matrix_subj.feats.get("SUBJ")
        assert inner_subj is not None
        assert inner_subj.feats.get("PRED") == "PRO"

    def test_class2_tough_with_gen_obj_inner_subj_stays_pro(self) -> None:
        # clause.py:1527 (tough + GEN-OBJ): ``Mahirap kumain ng aso.``
        # Same as above but the V-INF takes an overt OBJ.
        parses = parse_text("Mahirap kumain ng aso.")
        _ct, fs, _astr, _diags = parses[0]
        matrix_subj = fs.feats.get("SUBJ")
        assert matrix_subj is not None
        inner_subj = matrix_subj.feats.get("SUBJ")
        assert inner_subj is not None
        assert inner_subj.feats.get("PRED") == "PRO"

    def test_class2_wala_rc_matrix_subj_stays_pro(self) -> None:
        # clause.py:5292 (Wala-RC): ``Wala siyang kinakausap.`` —
        # "She has no one to talk to." The matrix SUBJ is the
        # negated entity (the missing one); the comment at
        # clause.py:5263-5265 is explicit about anaphoric
        # resolution to avoid spurious NOM-vs-GEN CASE conflict
        # between the possessor (``siya``) and the actor.
        parses = parse_text("Wala siyang kinakausap.")
        _ct, fs, _astr, _diags = parses[0]
        matrix_subj = fs.feats.get("SUBJ")
        assert matrix_subj is not None
        assert matrix_subj.feats.get("PRED") == "PRO"
