# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 6.G Commit 3: NP-from-N projection widening (§18.1 L32).

The simple NP-from-DET/ADP+N rules in ``cfg/nominal.py`` and the
dedicated cardinal-NP rule were extended in Phase 6.G to lift
modifier feats from the inner N / NUM daughter onto the matrix
NP via SHARE+SHARE (simple NP) and explicit lifts (cardinal-NP).
This test file verifies the per-modifier lifts:

* ``SEM_CLASS`` (incl. ``SEM_CLASS='SEASON'`` for tag- season
  nouns) — lifts via simple-NP SHARE+SHARE from the N daughter.
  Closes the Phase 6.F C2 SEM_CLASS-lift deferral as part of
  L32.
* ``CARDINAL_VALUE`` / ``NUM`` (size) — lift via dedicated
  cardinal-NP rule's explicit equations (existed pre-6.G;
  test exercises the path).
* ``ORDINAL_VALUE`` — lifts via dedicated ordinal-NP rule
  (existed pre-6.G).
* ``APPROX`` (Phase 5f Commit 16 approximator-wrap) — lifts via
  Phase 6.G C3 explicit ``(↑ APPROX) = ↓2 APPROX`` on the
  cardinal-NP rule.
* ``DISTRIB`` (Phase 5n.C.3 tig_distrib paradigm) — lifts via
  Phase 6.G C3 explicit ``(↑ DISTRIB) = ↓2 DISTRIB`` on the
  cardinal-NP rule.
* ``WHOLE`` — lifts via dedicated whole-NP rule (existed pre-6.G).

**Note on empty-f-node tolerance**: for bare cardinals (``isang
aklat`` without APPROX or DISTRIB modifiers), the cardinal-NP
rule's explicit lifts create empty ``FStructure`` placeholders
at ``NP.APPROX`` / ``NP.DISTRIB`` because the unifier's
``(↑ X) = ↓2 X`` is creating-if-absent semantics. Downstream
consumers checking ``is True`` skip these placeholders. The
TestEmptyFNodeTolerance class pins this convention.
"""

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _get_subj(s: str) -> FStructure | None:
    rs = parse_text(s)
    if not rs:
        return None
    v = rs[0][1].feats.get("SUBJ")
    return v if isinstance(v, FStructure) else None


def _get_obj(s: str) -> FStructure | None:
    rs = parse_text(s)
    if not rs:
        return None
    v = rs[0][1].feats.get("OBJ")
    return v if isinstance(v, FStructure) else None


# === SEM_CLASS (closes Phase 6.F C2 deferral) =========================


class TestSEMCLASSLifts:
    """``SEM_CLASS`` on the NOUN lex entry lifts to the matrix NP
    via the simple NP-from-DET+N rule's SHARE+SHARE projection."""

    def test_sarili_reflexive(self) -> None:
        # SEM_CLASS=REFLEXIVE on sarili → SUBJ.SEM_CLASS='REFLEXIVE'.
        subj = _get_subj("Nakita niya ang sarili niya.")
        assert subj is not None
        assert subj.feats.get("SEM_CLASS") == "REFLEXIVE"

    def test_season_taginit(self) -> None:
        # tag-init carries SEM_CLASS=SEASON (Phase 5f Commit 14
        # paradigm via paradigms.yaml). Lifts via the same
        # SHARE+SHARE path. Note: tag-init is parsed as init
        # (the root), with the SEASON feat on the resulting N.
        # The predicative-N rule then exposes the SUBJ.
        subj = _get_subj("Init ang tag-init.")
        assert subj is not None
        assert subj.feats.get("SEM_CLASS") == "SEASON"


# === Cardinal modifier feats ==========================================


class TestCardinalNPLifts:
    """The dedicated cardinal-NP rule (Phase 5f Commit 1) lifts
    CARDINAL_VALUE, NUM (size), APPROX (Phase 6.G), and DISTRIB
    (Phase 6.G) from the inner NUM daughter onto the matrix NP."""

    def test_cardinal_value_on_obj(self) -> None:
        obj = _get_obj("Bumili ako ng isang aklat.")
        assert obj is not None
        assert obj.feats.get("CARDINAL_VALUE") == "1"
        assert obj.feats.get("NUM") == "SG"

    def test_cardinal_value_on_subj(self) -> None:
        subj = _get_subj("Tumakbo ang dalawang bata.")
        assert subj is not None
        assert subj.feats.get("CARDINAL_VALUE") == "2"
        assert subj.feats.get("NUM") == "PL"

    def test_approx_lift(self) -> None:
        # Phase 6.G C3 closure: approximator-wrapped cardinal
        # lifts APPROX=true onto the matrix NP.
        obj = _get_obj("Bumili ako ng halos sampung aklat.")
        assert obj is not None
        assert obj.feats.get("APPROX") is True
        assert obj.feats.get("CARDINAL_VALUE") == "10"

    def test_distrib_lift(self) -> None:
        # Phase 6.G C3 closure: tig-distrib paradigm-derived
        # cardinal lifts DISTRIB=true onto the matrix NP.
        obj = _get_obj("Bumili ako ng tigisang aklat.")
        assert obj is not None
        assert obj.feats.get("DISTRIB") is True
        assert obj.feats.get("CARDINAL_VALUE") == "1"


# === Ordinal modifier feat ============================================


class TestOrdinalNPLift:
    """The dedicated ordinal-NP rule (Phase 5f Commit 7) lifts
    ORDINAL_VALUE onto the matrix NP."""

    def test_ordinal_value_on_subj(self) -> None:
        subj = _get_subj("Tumakbo ang unang anak.")
        assert subj is not None
        assert subj.feats.get("ORDINAL_VALUE") == "1"


# === Whole modifier feat ==============================================


class TestWholeNPLift:
    """The dedicated whole-NP rule (Phase 5f Commit 20 / 5h) lifts
    ``WHOLE=true`` onto the matrix NP."""

    def test_whole_on_obj(self) -> None:
        obj = _get_obj("Bumili ako ng buong aklat.")
        assert obj is not None
        assert obj.feats.get("WHOLE") is True


# === N-internal modifier composition propagation ======================


class TestNInternalCardinalToNP:
    """The N-level cardinal-composition rule (``N → NUM[CARDINAL]
    PART[LINK] N``, Phase 5f Commit 1 N-level companion)
    produces an N with CARDINAL_VALUE on N. Under Phase 6.G
    SHARE+SHARE on the simple NP rule, that N's CARDINAL_VALUE
    would propagate to NP — but the simple NP rule's
    ``¬ (↓2 CARDINAL_VALUE)`` constraint blocks it, leaving the
    dedicated NP-level cardinal rule (Phase 5f Commit 1) as the
    unique surface route for case-marked cardinal NPs."""

    def test_no_spurious_double_for_cardinal_np(self) -> None:
        # The cardinal-modified NP has ONE NP-side parse
        # (V-side ambiguity may produce >1 overall, but the
        # NP-with-cardinal reading is unique).
        rs = parse_text("Tumakbo ang dalawang bata.")
        # Filter parses where SUBJ has CARDINAL_VALUE=2.
        card_parses = [
            p for p in rs
            if isinstance(p[1].feats.get("SUBJ"), FStructure)
            and p[1].feats["SUBJ"].feats.get("CARDINAL_VALUE") == "2"
        ]
        assert len(card_parses) == 1


# === N-level RC tag-feat block ========================================


class TestNLevelRCTagBlock:
    """The Phase 5n.A C8 N-level RC rule sets ``N_RC=true`` on its
    output N (Phase 6.G C2). The simple NP rule's
    ``¬ (↓2 N_RC)`` blocks it from consuming N-level-RC'd Ns,
    leaving the NP-level RC wrap (Phase 4 §7.5) as the unique
    surface route for case-marked RCs while the N-level RC stays
    load-bearing for the existential bare-N case
    (``May bahay na nasa bundok``)."""

    def test_existential_bare_n_rc_intact(self) -> None:
        rs = parse_text("May bahay na nasa bundok.")
        assert rs, "Phase 5n.A C8 existential bare-N RC broken"

    def test_canonical_np_level_rc_intact(self) -> None:
        # Tumakbo ang batang kinain ko — OV-RC where the test
        # used to assert uniqueness pre-Phase-6.G (see
        # tests/tgllfg/test_rc_actor_pronoun.py).
        rs = parse_text("Tumakbo ang batang kinain ko.", n_best=10)
        rc_parses = [
            p for p in rs
            if isinstance(p[1].feats.get("SUBJ"), FStructure)
            and p[1].feats["SUBJ"].feats.get("ADJ")
        ]
        # Single NP-level RC parse expected.
        assert len(rc_parses) == 1


# === Empty-f-node tolerance ===========================================


class TestEmptyFNodeTolerance:
    """The cardinal-NP rule's explicit ``(↑ APPROX) = ↓2 APPROX``
    and ``(↑ DISTRIB) = ↓2 DISTRIB`` lifts use the unifier's
    creating-if-absent semantics. For bare cardinals (no APPROX
    or DISTRIB modifier wrap), an empty ``FStructure``
    placeholder is created at ``NP.APPROX`` / ``NP.DISTRIB``.
    Downstream consumers checking ``is True`` correctly skip the
    placeholder (an empty FStructure is not the bool ``True``).

    This test class pins the convention so future grammar
    changes that switch to a conditional-lift mechanism (if
    surfaced) detectably alter the behavior."""

    def test_bare_cardinal_approx_is_empty_fstructure(self) -> None:
        obj = _get_obj("Bumili ako ng isang aklat.")
        assert obj is not None
        approx = obj.feats.get("APPROX")
        # Convention: empty FStructure placeholder (NOT the bool
        # True), and NOT None.
        assert approx is not None
        assert approx is not True
        assert isinstance(approx, FStructure)
        assert not approx.feats  # empty placeholder

    def test_bare_cardinal_distrib_is_empty_fstructure(self) -> None:
        obj = _get_obj("Bumili ako ng isang aklat.")
        assert obj is not None
        distrib = obj.feats.get("DISTRIB")
        assert distrib is not None
        assert distrib is not True
        assert isinstance(distrib, FStructure)
        assert not distrib.feats
