"""Phase 5e Commit 5: headless / free relatives.

Phase 4 §7.5's "Out-of-scope" list flagged headless / free
relatives — a relative clause used directly as an NP, with no
overt head noun. Examples:

* ``Tumakbo ang kumain ng isda.`` "The one who ate fish ran."
* ``Nakita ko ang tumakbo.`` "I saw the one who ran."
* ``Tumakbo ang kinain ng aso.`` "The (one) eaten by the dog ran."

The construction is structurally three additive grammar rules
(one per case: NOM / GEN / DAT) of the shape
``NP[CASE=X] → DET-or-ADP[CASE=X, DEM=NO] S_GAP``. The DEM=NO
constraint prevents the rule from cross-firing on standalone
demonstratives (which use the existing Phase 4 §7.8 rule).

The headless NP gets PRED='PRO' (mirroring the standalone-
demonstrative analysis), with the gapped S attached as ADJ and
REL-PRO carrying PRED='PRO' plus the headless NP's CASE.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.pipeline import parse_text


def _find_pro_subj_with_rc(text: str, rc_pred_part: str) -> FStructure | None:
    """Return the first parse whose SUBJ is a PRED='PRO' f-structure
    with an ADJ member matching the RC's PRED."""
    rs = parse_text(text, n_best=15)
    for _, f, _, _ in rs:
        subj = f.feats.get("SUBJ")
        if not isinstance(subj, FStructure):
            continue
        if subj.feats.get("PRED") != "PRO":
            continue
        adj = subj.feats.get("ADJ")
        if adj is None:
            continue
        for m in adj:  # type: ignore[union-attr]
            pred = m.feats.get("PRED")  # type: ignore[union-attr]
            if isinstance(pred, str) and rc_pred_part in pred:
                return f
    return None


def _find_pro_obj_with_rc(text: str, rc_pred_part: str) -> FStructure | None:
    """Same shape as _find_pro_subj_with_rc but checks OBJ."""
    rs = parse_text(text, n_best=15)
    for _, f, _, _ in rs:
        obj = f.feats.get("OBJ")
        if not isinstance(obj, FStructure):
            continue
        if obj.feats.get("PRED") != "PRO":
            continue
        adj = obj.feats.get("ADJ")
        if adj is None:
            continue
        for m in adj:  # type: ignore[union-attr]
            pred = m.feats.get("PRED")  # type: ignore[union-attr]
            if isinstance(pred, str) and rc_pred_part in pred:
                return f
    return None


# === NOM-marked headless RCs ============================================


class TestHeadlessRcNom:
    """``ang`` + S_GAP forms a headless NP serving as SUBJ. The
    headless head's PRED is 'PRO' and the RC sits in ADJ."""

    def test_av_intr_rc_with_intr_matrix(self) -> None:
        """``Tumakbo ang tumakbo.`` "The one who ran ran." Both
        matrix and RC are AV-INTR; SUBJ is a headless NP whose RC
        is just the bare V."""
        f = _find_pro_subj_with_rc("Tumakbo ang tumakbo.", "TAKBO")
        assert f is not None
        assert f.feats.get("PRED") == "TAKBO <SUBJ>"
        subj = f.feats["SUBJ"]
        assert isinstance(subj, FStructure)
        assert subj.feats.get("CASE") == "NOM"
        assert subj.feats.get("MARKER") == "ANG"
        assert subj.feats.get("PRED") == "PRO"

    def test_av_tr_rc_with_intr_matrix(self) -> None:
        """``Tumakbo ang kumain ng isda.`` "The one who ate fish ran." """
        f = _find_pro_subj_with_rc(
            "Tumakbo ang kumain ng isda.", "EAT <SUBJ, OBJ>"
        )
        assert f is not None
        assert f.feats.get("PRED") == "TAKBO <SUBJ>"
        subj = f.feats["SUBJ"]
        assert isinstance(subj, FStructure)
        # The RC's OBJ is the GEN-NP `ng isda`.
        rc = next(iter(subj.feats["ADJ"]))  # type: ignore[arg-type]
        assert rc.feats.get("OBJ").feats.get("LEMMA") == "isda"

    def test_ov_rc_patient_pivot(self) -> None:
        """``Tumakbo ang kinain ng aso.`` "The one eaten by the
        dog ran." OV-RC: pivot is the patient (= REL-PRO);
        ng-NP is OBJ-AGENT (the eater)."""
        f = _find_pro_subj_with_rc(
            "Tumakbo ang kinain ng aso.", "EAT <SUBJ, OBJ-AGENT>"
        )
        assert f is not None
        rc = next(iter(f.feats["SUBJ"].feats["ADJ"]))  # type: ignore[arg-type]
        assert rc.feats.get("VOICE") == "OV"
        oa = rc.feats.get("OBJ-AGENT")
        assert isinstance(oa, FStructure)
        assert oa.feats.get("LEMMA") == "aso"

    def test_rel_pro_inherits_case(self) -> None:
        """REL-PRO inside the RC inherits the headless NP's CASE
        and PRED='PRO'."""
        f = _find_pro_subj_with_rc(
            "Tumakbo ang tumakbo.", "TAKBO"
        )
        assert f is not None
        rc = next(iter(f.feats["SUBJ"].feats["ADJ"]))  # type: ignore[arg-type]
        rel_pro = rc.feats.get("REL-PRO")
        assert isinstance(rel_pro, FStructure)
        assert rel_pro.feats.get("PRED") == "PRO"
        assert rel_pro.feats.get("CASE") == "NOM"

    def test_rel_pro_eq_subj(self) -> None:
        """The RC's SUBJ is bound to REL-PRO via S_GAP's
        ``(↑ SUBJ) = (↑ REL-PRO)``; Python-id equality holds."""
        f = _find_pro_subj_with_rc(
            "Tumakbo ang tumakbo.", "TAKBO"
        )
        assert f is not None
        rc = next(iter(f.feats["SUBJ"].feats["ADJ"]))  # type: ignore[arg-type]
        rel_pro = rc.feats.get("REL-PRO")
        rc_subj = rc.feats.get("SUBJ")
        assert isinstance(rel_pro, FStructure)
        assert isinstance(rc_subj, FStructure)
        assert rel_pro.id == rc_subj.id


# === GEN/DAT-marked headless RCs ========================================


class TestHeadlessRcOblique:
    """Headless RCs in OBJ / OBL position."""

    def test_headless_obj_av(self) -> None:
        """``Nakita ko ang tumakbo.`` "I saw the one who ran." The
        synthesized matrix nakita is AV-NVOL with SUBJ=ang-NP and
        OBJ=ng-PRON; ang-NP is the headless RC."""
        f = _find_pro_subj_with_rc(
            "Nakita ko ang tumakbo.", "TAKBO"
        )
        assert f is not None
        assert f.feats.get("PRED") == "KITA <SUBJ, OBJ>"


# === Discrimination =====================================================


class TestDiscrimination:
    """The headless-RC rule (DEM=NO) doesn't cross-fire with the
    standalone-demonstrative rule (DEM=YES)."""

    def test_demonstrative_does_not_form_headless(self) -> None:
        """``Kumain iyon.`` should still be the standalone-
        demonstrative reading (Phase 4 §7.8) — not a headless RC
        with a PRED='PRO' head plus an empty RC. The
        demonstrative carries DEM=YES; the headless rule
        requires DEM=NO."""
        rs = parse_text("Kumain iyon.", n_best=10)
        # At least one parse — it's the existing standalone-dem
        # reading.
        assert rs
        # The new headless-RC rule should NOT have introduced a
        # parse where the SUBJ has an empty ADJ. Sanity-check that
        # all parses have a non-empty SUBJ structure (DEM-shaped or
        # otherwise normal).
        for _, f, _, _ in rs:
            subj = f.feats.get("SUBJ")
            assert isinstance(subj, FStructure)
            # Standalone demonstrative carries DEIXIS.
            assert subj.feats.get("DEIXIS") in {"PROX", "MED", "DIST"}

    def test_regular_np_dem_no_unaffected(self) -> None:
        """Plain ``Kumain ang aso.`` still parses with the regular
        ``DET[CASE=NOM] N`` NP rule, not the new headless one
        (which would require an S_GAP, not a noun)."""
        rs = parse_text("Kumain ang aso.", n_best=10)
        assert rs
        for _, f, _, _ in rs:
            subj = f.feats.get("SUBJ")
            assert isinstance(subj, FStructure)
            # Regular noun NP has LEMMA from the head noun.
            if subj.feats.get("LEMMA") == "aso":
                # PRED is 'NOUN(↑ FORM)' (the noun shell), not 'PRO'.
                assert subj.feats.get("PRED") != "PRO"
                return
        raise AssertionError("expected a regular `aso` SUBJ parse")


# === Negation under headless RC =========================================


class TestNegationUnderHeadless:
    """Inner negation inside the headless RC composes via the
    existing S_GAP recursion."""

    def test_neg_inside_rc(self) -> None:
        """``Tumakbo ang hindi kumain ng isda.`` "The one who didn't
        eat fish ran." NEG inside the RC, not on the matrix."""
        f = _find_pro_subj_with_rc(
            "Tumakbo ang hindi kumain ng isda.", "EAT <SUBJ, OBJ>"
        )
        assert f is not None
        # Matrix POLARITY is NOT NEG (negation is inside the RC).
        assert f.feats.get("POLARITY") != "NEG"
        rc = next(iter(f.feats["SUBJ"].feats["ADJ"]))  # type: ignore[arg-type]
        assert rc.feats.get("POLARITY") == "NEG"


# === LMT diagnostics ====================================================


class TestLmtDiagnostics:
    """Headless RCs produce no blocking LMT diagnostics."""

    def test_no_blocking_av_rc(self) -> None:
        rs = parse_text("Tumakbo ang tumakbo.", n_best=5)
        for _, _f, _c, diags in rs:
            blocking = [d for d in diags if d.kind != "lmt-mismatch"]
            assert blocking == [], f"unexpected blocking diags: {blocking}"

    def test_no_blocking_ov_rc(self) -> None:
        rs = parse_text("Tumakbo ang kinain ng aso.", n_best=5)
        for _, _f, _c, diags in rs:
            blocking = [d for d in diags if d.kind != "lmt-mismatch"]
            assert blocking == [], f"unexpected blocking diags: {blocking}"


# === Regression: existing relativization unchanged ======================


class TestRegression:
    """The new headless-RC rule must not affect the existing
    head-initial relativization (Phase 4 §7.5)."""

    def test_head_initial_rc_unchanged(self) -> None:
        """``Tumakbo ang batang kumain ng isda.`` (head-initial
        RC) still parses — `bata` is the overt head, not a PRO."""
        rs = parse_text("Tumakbo ang batang kumain ng isda.", n_best=10)
        assert rs
        seen_overt_head = False
        for _, f, _, _ in rs:
            subj = f.feats.get("SUBJ")
            if (
                isinstance(subj, FStructure)
                and subj.feats.get("LEMMA") == "bata"
                and subj.feats.get("PRED") != "PRO"
            ):
                seen_overt_head = True
                break
        assert seen_overt_head
