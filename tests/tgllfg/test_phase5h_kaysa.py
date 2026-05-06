"""Phase 5h Commit 4: ``kaysa`` PART + comparison-complement rule.

Roadmap §12.1 / plan-of-record §4.1, §5.5, §6 Commit 4. Two pieces:

1. New ``kaysa`` PART entry in ``data/tgl/particles.yaml`` carrying
   ``COMP_PHRASE: KAYSA`` (mirroring the Phase 5f Commit 17 numeric
   comparator family ``higit`` / ``kulang`` / ``bababa`` / ``hihigit``,
   all of which carry ``COMP_PHRASE`` tags). Pre-state: ``kaysa``
   was ``_UNK`` (verified 2026-05-05).

2. New comparison-complement rule in ``cfg/clause.py``:

       S → S PART[COMP_PHRASE=KAYSA] NP[CASE=DAT]

   Adjoins the kaysa-headed phrase to the matrix S's ADJUNCT set
   with ``ROLE: STANDARD``. The DAT-NP daughter is structured by
   the existing Phase 4 ``kay`` (HUMAN) / ``sa`` (default) ADP
   machinery — no new NP rules. Composes with the Phase 5h
   Commit 3 comparative-ADJ wrapper unchanged: ``Mas matalino
   siya kaysa kay Maria`` parses as the inner S ``Mas matalino
   siya`` plus the adjoined ``kaysa kay Maria``.

   The rule is permissive: the inner S's ``COMP_DEGREE`` is NOT
   constrained, so bare comparisons (``Matalino si Maria kaysa
   kay Juan``) parse alongside the canonical ``mas``-marked form.
   Tightening would need ``COMP_DEGREE`` to be lifted onto the
   matrix S by the Phase 5g predicative-adj clause rule (which
   currently keeps it on the ADJ daughter); deferred.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import FStructure, Token
from tgllfg.core.pipeline import parse_text
from tgllfg.morph import Analyzer


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


def _standard_adjunct(fstruct: FStructure) -> FStructure:
    """Walk the matrix S's ADJUNCT set and return the unique member
    whose ``ROLE == 'STANDARD'``. Raises if zero or multiple match."""
    adjunct_set = fstruct.feats.get("ADJUNCT")
    assert adjunct_set is not None, (
        f"matrix has no ADJUNCT set; feats={fstruct.feats}"
    )
    standards = [
        m for m in adjunct_set
        if isinstance(m, FStructure) and m.feats.get("ROLE") == "STANDARD"
    ]
    assert len(standards) == 1, (
        f"expected exactly one ROLE=STANDARD adjunct; got {len(standards)}"
    )
    return standards[0]


# === ``kaysa`` PART lex entry ==========================================


class TestKaysaPartLex:
    """``kaysa`` is now a known PART with COMP_PHRASE: KAYSA."""

    def test_kaysa_indexed_as_part(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("kaysa"))
        part_analyses = [a for a in out if a.pos == "PART"]
        assert len(part_analyses) == 1
        assert part_analyses[0].lemma == "kaysa"

    def test_kaysa_carries_comp_phrase_feature(self) -> None:
        analyzer = Analyzer.from_default()
        part = next(
            a for a in analyzer.analyze_one(_tok("kaysa")) if a.pos == "PART"
        )
        assert part.feats.get("COMP_PHRASE") == "KAYSA"


# === kaysa kay X (HUMAN proper noun) ===================================


class TestKaysaWithKay:
    """``kaysa kay X`` introduces a HUMAN proper-noun standard. The
    DAT-NP is structured by the existing Phase 4 ``kay`` ADP
    machinery."""

    @pytest.mark.parametrize("sentence,adj_lemma,standard_lemma", [
        ("Mas matalino siya kaysa kay Maria.", "talino", "maria"),
        ("Mas mabilis ang kabayo kaysa kay Juan.", "bilis", "juan"),
        ("Mas malaki ang bahay kaysa kay Pedro.", "laki", "pedro"),
    ])
    def test_kaysa_kay_predicative_comparative(
        self,
        sentence: str,
        adj_lemma: str,
        standard_lemma: str,
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 1, (
            f"expected one parse for {sentence!r}; got {len(parses)}"
        )
        _ctree, fstruct, _astr, _diags = parses[0]
        # Matrix f-structure: predicative-adj clause shape, propagated
        # through (↑) = ↓1 from the inner comparative S.
        assert fstruct.feats.get("PRED") == "ADJ <SUBJ>"
        assert fstruct.feats.get("ADJ_LEMMA") == adj_lemma
        # The kaysa-NP is in ADJUNCT with ROLE=STANDARD and DAT case
        # via kay (HUMAN marker).
        std = _standard_adjunct(fstruct)
        assert std.feats.get("CASE") == "DAT"
        assert std.feats.get("MARKER") == "KAY"
        assert std.feats.get("LEMMA") == standard_lemma


# === kaysa sa X (default DAT — generic / inanimate) ====================


class TestKaysaWithSa:
    """``kaysa sa X`` introduces a generic / inanimate DAT-NP standard
    via the default ``sa`` ADP marker."""

    @pytest.mark.parametrize("sentence,adj_lemma,standard_lemma", [
        ("Mas matalino siya kaysa sa bata.",   "talino", "bata"),
        ("Mas mabilis ang kabayo kaysa sa aso.", "bilis", "aso"),
        ("Mas maganda ang bahay kaysa sa aklat.", "ganda", "aklat"),
    ])
    def test_kaysa_sa_predicative_comparative(
        self,
        sentence: str,
        adj_lemma: str,
        standard_lemma: str,
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 1
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED") == "ADJ <SUBJ>"
        assert fstruct.feats.get("ADJ_LEMMA") == adj_lemma
        std = _standard_adjunct(fstruct)
        assert std.feats.get("CASE") == "DAT"
        assert std.feats.get("MARKER") == "SA"
        assert std.feats.get("LEMMA") == standard_lemma


# === Bare-comparison (no mas) ==========================================


class TestKaysaBareComparison:
    """The rule does not constrain the inner S's COMP_DEGREE, so bare
    comparisons (no ``mas``) also parse. This is permissive but
    consistent with attested colloquial usage."""

    def test_bare_comparison_parses(self) -> None:
        parses = parse_text("Matalino si Maria kaysa kay Juan.")
        assert len(parses) == 1
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED") == "ADJ <SUBJ>"
        assert fstruct.feats.get("ADJ_LEMMA") == "talino"
        std = _standard_adjunct(fstruct)
        assert std.feats.get("LEMMA") == "juan"


# === Possessive in kaysa-NP ============================================


class TestKaysaWithPossessive:
    """The kaysa-NP composes with the existing Phase 4 / 5g possessive
    construction inside the DAT-NP."""

    def test_kaysa_with_possessive_pronoun(self) -> None:
        parses = parse_text("Mas maganda ang bahay kaysa sa kapatid niya.")
        assert len(parses) == 1
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("ADJ_LEMMA") == "ganda"
        std = _standard_adjunct(fstruct)
        # The kaysa-NP head is `kapatid` with a possessive (POSS feature).
        assert std.feats.get("LEMMA") == "kapatid"
        assert std.feats.get("CASE") == "DAT"
        assert std.feats.get("POSS") is not None


# === Composition with negation =========================================


class TestKaysaWithNegation:
    """``Hindi mas matalino siya kaysa kay Maria`` — negation + comparative
    + kaysa-standard composes. The c-tree has a structural ambiguity
    (kaysa attaches inside or outside the negation) but the f-structure
    is identical in both readings: matrix carries POLARITY=NEG with a
    STANDARD adjunct."""

    def test_negation_plus_comparative_plus_kaysa(self) -> None:
        parses = parse_text("Hindi mas matalino siya kaysa kay Maria.")
        # Multiple parses are expected — left-vs-right attachment of
        # the kaysa adjunct relative to the hindi negation. Both
        # readings produce the same f-structure (POLARITY=NEG +
        # STANDARD adjunct).
        assert len(parses) >= 1
        for _ctree, fstruct, _astr, _diags in parses:
            assert fstruct.feats.get("PRED") == "ADJ <SUBJ>"
            assert fstruct.feats.get("ADJ_LEMMA") == "talino"
            assert fstruct.feats.get("POLARITY") == "NEG"
            std = _standard_adjunct(fstruct)
            assert std.feats.get("LEMMA") == "maria"


# === Baseline preservation =============================================


class TestPhase5hCommit3BaselinePreserved:
    """Phase 5h Commit 3 surfaces (mas without kaysa) continue to parse
    with one parse and no STANDARD adjunct — the new kaysa rule does
    not perturb existing comparatives."""

    @pytest.mark.parametrize("sentence,adj_lemma", [
        ("Mas matalino siya.", "talino"),
        ("Mas mabilis ang kabayo.", "bilis"),
        ("Mas maganda ang bahay.", "ganda"),
    ])
    def test_mas_without_kaysa_still_parses(
        self, sentence: str, adj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 1
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED") == "ADJ <SUBJ>"
        assert fstruct.feats.get("ADJ_LEMMA") == adj_lemma
        # No STANDARD adjunct — kaysa rule didn't fire.
        adjunct_set = fstruct.feats.get("ADJUNCT")
        if adjunct_set is not None:
            standards = [
                m for m in adjunct_set
                if isinstance(m, FStructure)
                and m.feats.get("ROLE") == "STANDARD"
            ]
            assert standards == []


class TestPhase5gBaselinePreserved:
    """Phase 5g bare ma- predicatives unchanged."""

    @pytest.mark.parametrize("sentence,adj_lemma", [
        ("Maganda ang bata.",   "ganda"),
        ("Matalino siya.",      "talino"),
        ("Mabilis ang kabayo.", "bilis"),
    ])
    def test_phase5g_predicative_unchanged(
        self, sentence: str, adj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 1
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("ADJ_LEMMA") == adj_lemma
        adjunct_set = fstruct.feats.get("ADJUNCT")
        # Phase 5g sentences have no ADJUNCT set or an empty one.
        assert adjunct_set is None or len(adjunct_set) == 0
