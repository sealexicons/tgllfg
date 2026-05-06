"""Phase 5h Commit 6: equative two-NP standard-of-comparison frames.

Roadmap §12.1 / plan-of-record §5.6, §6 Commit 6.

The Phase 5h Commit 2 ``kasing-`` / ``sing-`` cells produce ADJ
surfaces with ``COMP_DEGREE: EQUATIVE``. The Phase 5g predicative-
adj clause rule handles single-NP predicatives unchanged
(``Kasingganda ang bahay``, asserted in Commit 2 tests). This commit
adds three new clause-level rules in ``cfg/clause.py`` for the
two-NP standard-of-comparison construction:

    S → ADJ[COMP_DEGREE=EQUATIVE] NP[CASE=NOM] NP[CASE=GEN]
    S → ADJ[COMP_DEGREE=EQUATIVE] NP[CASE=GEN] NP[CASE=NOM]
    S → ADJ[COMP_DEGREE=EQUATIVE] NP[CASE=NOM] NP[CASE=NOM]

The comparee is the NOM-NP (matrix SUBJ); the standard is the
non-comparee NP, which rides on the matrix's ADJUNCT set with
``ROLE: EQUATIVE_STANDARD``. The constraining
``(↓1 COMP_DEGREE) =c 'EQUATIVE'`` restricts these rules to
equative-marked ADJ heads — comparative / superlative / intensive
ADJs go through the single-NP predicative route only.

Three rule variants because Tagalog freely permits NOM-then-GEN
and GEN-then-NOM order, plus the colloquial two-NOM variant. The
canonical Schachter-Otanes shape is ``kasing-X ng/ni STANDARD ang
COMPAREE`` (GEN first); the two-NOM ``kasing-X si COMPAREE si
STANDARD`` is colloquial. The DAT-standard variant
(``kasing-X kay STANDARD ang COMPAREE``) is marginal in modern
Tagalog and is deferred — if corpus pressure surfaces, a fourth
rule lands as a Phase 5h follow-on.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _equative_standard_adjunct(fstruct: FStructure) -> FStructure | None:
    """Walk the matrix's ADJUNCT set and return the unique member
    whose ``ROLE == 'EQUATIVE_STANDARD'``. Returns None if absent."""
    adjunct_set = fstruct.feats.get("ADJUNCT")
    if adjunct_set is None:
        return None
    standards = [
        m for m in adjunct_set
        if isinstance(m, FStructure)
        and m.feats.get("ROLE") == "EQUATIVE_STANDARD"
    ]
    if not standards:
        return None
    assert len(standards) == 1, (
        f"expected at most one EQUATIVE_STANDARD adjunct; "
        f"got {len(standards)}"
    )
    return standards[0]


# === Two-NOM kasing- construction ======================================


class TestKasingTwoNomVariant:
    """Colloquial two-NOM construction: ``kasing-X si COMPAREE si
    STANDARD``. Both NPs are NOM-marked via the personal-name marker
    ``si``; the first is the comparee (matrix SUBJ), the second is
    the standard (EQUATIVE_STANDARD adjunct)."""

    @pytest.mark.parametrize("sentence,adj_lemma,std_lemma", [
        ("Kasingganda si Maria si Ana.",  "ganda",  "ana"),
        ("Singganda si Maria si Ana.",    "ganda",  "ana"),
        ("Kasinglinis si Maria si Ana.",  "linis",  "ana"),
        ("Kasingbilis si Juan si Pedro.", "bilis",  "pedro"),
    ])
    def test_two_nom_equative(
        self, sentence: str, adj_lemma: str, std_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 1, (
            f"expected one parse for {sentence!r}; got {len(parses)}"
        )
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED") == "ADJ <SUBJ>"
        assert fstruct.feats.get("ADJ_LEMMA") == adj_lemma
        std = _equative_standard_adjunct(fstruct)
        assert std is not None, (
            f"missing EQUATIVE_STANDARD adjunct in {fstruct.feats}"
        )
        assert std.feats.get("LEMMA") == std_lemma
        assert std.feats.get("CASE") == "NOM"


# === GEN-standard + NOM-comparee (canonical S&O shape) ================


class TestKasingGenStandardNomComparee:
    """Canonical Schachter-Otanes shape: ``kasing-X ng/ni STANDARD
    ang/si COMPAREE``. GEN is the standard, NOM is the comparee."""

    @pytest.mark.parametrize("sentence,adj_lemma,std_lemma", [
        ("Kasingganda ni Maria si Ana.",   "ganda", "maria"),
        ("Kasingbilis ni Juan si Pedro.",  "bilis", "juan"),
        ("Kasinglakas ni Pedro si Juan.",  "lakas", "pedro"),
    ])
    def test_gen_nom_equative_proper(
        self, sentence: str, adj_lemma: str, std_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got 0"
        )
        # Find the parse with EQUATIVE_STANDARD adjunct (canonical
        # equative reading).
        equative_parses = [
            (ct, fs, ast, diags) for (ct, fs, ast, diags) in parses
            if _equative_standard_adjunct(fs) is not None
        ]
        assert len(equative_parses) >= 1
        _ctree, fstruct, _astr, _diags = equative_parses[0]
        assert fstruct.feats.get("ADJ_LEMMA") == adj_lemma
        std = _equative_standard_adjunct(fstruct)
        assert std is not None
        assert std.feats.get("LEMMA") == std_lemma
        assert std.feats.get("CASE") == "GEN"

    def test_gen_nom_equative_common_nouns(self) -> None:
        """``Kasingganda ng bahay mo ang bahay ko.`` — common-noun
        construction with GEN possessive on the standard NP."""
        parses = parse_text("Kasingganda ng bahay mo ang bahay ko.")
        # Multiple parses are fine — the f-structure with the
        # EQUATIVE_STANDARD adjunct is the equative reading.
        equative_parses = [
            (ct, fs, ast, diags) for (ct, fs, ast, diags) in parses
            if _equative_standard_adjunct(fs) is not None
        ]
        assert len(equative_parses) >= 1
        _ctree, fstruct, _astr, _diags = equative_parses[0]
        assert fstruct.feats.get("ADJ_LEMMA") == "ganda"
        std = _equative_standard_adjunct(fstruct)
        assert std is not None
        assert std.feats.get("LEMMA") == "bahay"
        assert std.feats.get("CASE") == "GEN"


# === NOM-comparee + GEN-standard (reversed order) =====================


class TestKasingNomCompareeGenStandard:
    """The other order: ``kasing-X ang/si COMPAREE ng/ni STANDARD``."""

    def test_nom_gen_common_nouns(self) -> None:
        """``Kasingganda ang bahay ko ng bahay mo.`` — comparee
        first, standard second."""
        parses = parse_text("Kasingganda ang bahay ko ng bahay mo.")
        equative_parses = [
            (ct, fs, ast, diags) for (ct, fs, ast, diags) in parses
            if _equative_standard_adjunct(fs) is not None
        ]
        assert len(equative_parses) >= 1
        _ctree, fstruct, _astr, _diags = equative_parses[0]
        assert fstruct.feats.get("ADJ_LEMMA") == "ganda"
        std = _equative_standard_adjunct(fstruct)
        assert std is not None
        assert std.feats.get("CASE") == "GEN"


# === The new rules fire only on EQUATIVE-marked ADJ heads ==============


class TestEquativeRulesNotPromiscuous:
    """The new rules constrain on COMP_DEGREE=EQUATIVE so other-degree-
    marked ADJs do NOT fire the two-NP equative frames. This is a
    regression-protection test: comparative (mas X), superlative
    (pinaka-X), intensive (napaka-X) ADJs must not get the
    EQUATIVE_STANDARD adjunct from the new rules."""

    @pytest.mark.parametrize("sentence", [
        # Comparative ADJ + 2 NPs — should NOT match equative rules.
        "Mas matalino si Maria si Ana.",
        # Superlative ADJ + 2 NPs.
        "Pinakamatalino si Maria si Ana.",
        # Intensive ADJ + 2 NPs.
        "Napakaganda si Maria si Ana.",
    ])
    def test_non_equative_two_nom_does_not_fire_equative_frame(
        self, sentence: str
    ) -> None:
        parses = parse_text(sentence)
        # If the input parses at all, no parse has an
        # EQUATIVE_STANDARD adjunct (the equative-frame rule is
        # constrained on COMP_DEGREE=EQUATIVE, which these ADJs lack).
        for _ct, fs, _astr, _diags in parses:
            std = _equative_standard_adjunct(fs)
            assert std is None, (
                f"unexpected EQUATIVE_STANDARD adjunct on "
                f"non-equative {sentence!r}: {fs.feats}"
            )


# === Equative-identity predicates with two-NP frames ===================


class TestPareohoMagkaibaTwoNpFrame:
    """``pareho`` (EQUATIVE), ``magkapareho`` (EQUATIVE), ``magkaiba``
    (CONTRASTIVE) carry COMP_DEGREE: EQUATIVE / CONTRASTIVE on their
    bare-citation feats. The new equative rules constrain on
    COMP_DEGREE=EQUATIVE specifically; CONTRASTIVE does NOT match
    so ``magkaiba`` does not get the equative frame.

    The result: ``pareho`` / ``magkapareho`` admit the two-NP frame;
    ``magkaiba`` admits only the single-NP predicative form."""

    def test_pareho_two_nom_admits_equative_frame(self) -> None:
        parses = parse_text("Pareho si Maria si Ana.")
        equative_parses = [
            (ct, fs, ast, diags) for (ct, fs, ast, diags) in parses
            if _equative_standard_adjunct(fs) is not None
        ]
        assert len(equative_parses) >= 1
        _, fstruct, _, _ = equative_parses[0]
        assert fstruct.feats.get("ADJ_LEMMA") == "pareho"

    def test_magkaiba_two_nom_does_not_admit_equative_frame(self) -> None:
        """``magkaiba`` carries COMP_DEGREE: CONTRASTIVE, not
        EQUATIVE, so the COMP_DEGREE=c constraint blocks the new
        rules. The two-NOM input may not parse at all (the
        CONTRASTIVE rule isn't part of this commit's scope)."""
        parses = parse_text("Magkaiba si Maria si Ana.")
        for _ct, fs, _astr, _diags in parses:
            std = _equative_standard_adjunct(fs)
            assert std is None


# === Negation × equative two-NP =======================================


class TestNegationPlusEquativeTwoNp:
    """The hindi-negation rule wraps the equative-two-NP S unchanged."""

    def test_hindi_kasingganda_two_nom(self) -> None:
        parses = parse_text("Hindi kasingganda si Maria si Ana.")
        equative_parses = [
            (ct, fs, ast, diags) for (ct, fs, ast, diags) in parses
            if _equative_standard_adjunct(fs) is not None
        ]
        assert len(equative_parses) >= 1
        _, fstruct, _, _ = equative_parses[0]
        assert fstruct.feats.get("ADJ_LEMMA") == "ganda"
        assert fstruct.feats.get("POLARITY") == "NEG"
        std = _equative_standard_adjunct(fstruct)
        assert std is not None
        assert std.feats.get("LEMMA") == "ana"


# === Phase 5g and earlier 5h baselines preserved ======================


class TestBaselinePreserved:
    """Single-NP equative predicatives (Phase 5h Commit 2) and earlier
    Phase 5g / 5h Commit 3-5 surfaces continue to parse — the new
    equative-frame rules are constrained tightly enough to avoid
    perturbing the pre-existing single-NP cases."""

    @pytest.mark.parametrize("sentence,adj_lemma", [
        ("Pareho ang aklat.",        "pareho"),
        ("Magkaiba ang aklat.",      "magkaiba"),
        ("Magkapareho ang aklat.",   "magkapareho"),
        ("Kasingganda ang bahay.",   "ganda"),
        ("Singganda ang bahay.",     "ganda"),
        # Phase 5h Commit 1 / 3 / 5 baselines
        ("Pinakamaganda ang bahay.", "ganda"),
        ("Napakaganda ang bahay.",   "ganda"),
        ("Mas matalino siya.",       "talino"),
        ("Sobrang maganda ang bata.", "ganda"),
        # Phase 5g
        ("Maganda ang bata.",        "ganda"),
    ])
    def test_single_np_predicative_still_parses(
        self, sentence: str, adj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        # All these are single-NP predicatives — no
        # EQUATIVE_STANDARD adjunct expected.
        assert len(parses) >= 1
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("ADJ_LEMMA") == adj_lemma
            std = _equative_standard_adjunct(fs)
            assert std is None, (
                f"unexpected EQUATIVE_STANDARD adjunct on single-NP "
                f"baseline {sentence!r}"
            )
