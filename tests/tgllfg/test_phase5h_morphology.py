"""Phase 5h Commit 1: ``pinaka-`` superlative + ``napaka-`` intensive cells.

Roadmap §12.1 analytical commitment: comparative / degree morphology
on adjectival heads. The two new cells in
``data/tgl/adj_paradigms.yaml`` mirror the Phase 5g ``ma_adj`` cell's
productive opt-in (``affix_class: ma_adj``) so any root carrying
``affix_class: [ma_adj]`` automatically unlocks both derivations:

* ``pinaka-`` superlative: ``pinaka`` + ``ma`` + root → e.g.
  ``pinakamaganda`` "most beautiful". Operation order: prefix
  ``ma`` first, then prefix ``pinaka``, mirroring the morphological
  layering (the superlative scopes over the adjectival stem).
  Feature: ``COMP_DEGREE: SUPERLATIVE``.
* ``napaka-`` intensive: ``napaka`` + root → e.g. ``napakaganda``
  "very beautiful". Attaches to the bare root (no ``ma-``).
  Features: ``COMP_DEGREE: INTENSIVE``, ``INTENSIFIER: YES``.

These tests exercise the analyzer-layer mechanics (per-cell ``feats``
ride into every generated MorphAnalysis, productive opt-in fires on
the full 30-root Phase 5g inventory, lemma policy unchanged from
Phase 5g, no surface collisions with the seed bare ``ma-`` surfaces).
End-to-end parses through the Phase 5g predicative-adj clause rule
fall out without grammar-rule changes — the new ADJ surfaces carry
``PREDICATIVE=YES`` intrinsically just like the bare ``ma-`` form.

Phase 5h Commit 2 adds ``kasing-`` / ``sing-`` equative cells on
the same productive opt-in. Phase 5h Commits 3+ introduce
PART-driven grammar rules for the free-word degree markers
(``mas``, ``kaysa``, particle intensifiers).
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import Token
from tgllfg.core.pipeline import parse_text
from tgllfg.morph import Analyzer


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === Phase 5g seed inventory + Phase 5h derivations =======================
#
# Subset of the 30 Phase 5g ADJ roots, picked to span all four
# dimensions (size / quality / sensory / evaluative). Used by every
# parametrised test below — cross-dimension coverage at low test
# count.

SAMPLE_INVENTORY = [
    # (root, dimension, gloss, ma_form, pinaka_form, napaka_form)
    ("laki",   "size",       "big, large",        "malaki",   "pinakamalaki",   "napakalaki"),
    ("liit",   "size",       "small",             "maliit",   "pinakamaliit",   "napakaliit"),
    ("taas",   "size",       "high, tall",        "mataas",   "pinakamataas",   "napakataas"),
    ("ganda",  "quality",    "beautiful",         "maganda",  "pinakamaganda",  "napakaganda"),
    ("talino", "quality",    "intelligent",       "matalino", "pinakamatalino", "napakatalino"),
    ("tanda",  "quality",    "old",               "matanda",  "pinakamatanda",  "napakatanda"),
    ("bilis",  "quality",    "quick, fast",       "mabilis",  "pinakamabilis",  "napakabilis"),
    ("lakas",  "quality",    "strong",            "malakas",  "pinakamalakas",  "napakalakas"),
    ("init",   "sensory",    "hot",               "mainit",   "pinakamainit",   "napakainit"),
    ("lamig",  "sensory",    "cold",              "malamig",  "pinakamalamig",  "napakalamig"),
    ("sarap",  "sensory",    "delicious",         "masarap",  "pinakamasarap",  "napakasarap"),
    ("saya",   "evaluative", "happy",             "masaya",   "pinakamasaya",   "napakasaya"),
    ("yaman",  "evaluative", "wealthy",           "mayaman",  "pinakamayaman",  "napakayaman"),
    ("hirap",  "evaluative", "poor, difficult",   "mahirap",  "pinakamahirap",  "napakahirap"),
]


# === Surface-generation: pinaka- ==========================================


class TestSuperlativeSurfaces:
    """Each Phase 5g root produces a productive ``pinaka-`` surface."""

    @pytest.mark.parametrize(
        "root,_dim,_gloss,_ma,pinaka,_napaka", SAMPLE_INVENTORY
    )
    def test_indexed_as_adj(
        self,
        root: str,
        _dim: str,
        _gloss: str,
        _ma: str,
        pinaka: str,
        _napaka: str,
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(pinaka))
        adj_analyses = [a for a in out if a.pos == "ADJ"]
        assert len(adj_analyses) == 1, (
            f"expected exactly one ADJ analysis for {pinaka!r}; "
            f"got {[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )
        assert adj_analyses[0].lemma == root

    @pytest.mark.parametrize(
        "root,_dim,_gloss,_ma,pinaka,_napaka", SAMPLE_INVENTORY
    )
    def test_carries_superlative_degree(
        self,
        root: str,
        _dim: str,
        _gloss: str,
        _ma: str,
        pinaka: str,
        _napaka: str,
    ) -> None:
        analyzer = Analyzer.from_default()
        adj = next(
            a for a in analyzer.analyze_one(_tok(pinaka)) if a.pos == "ADJ"
        )
        assert adj.feats.get("COMP_DEGREE") == "SUPERLATIVE"
        assert adj.feats.get("PREDICATIVE") == "YES"  # intrinsic
        assert adj.feats.get("LEMMA") == root         # lemma policy
        # The intensifier flag is napaka-specific; superlative does not set it.
        assert "INTENSIFIER" not in adj.feats


# === Surface-generation: napaka- ==========================================


class TestIntensiveSurfaces:
    """Each Phase 5g root produces a productive ``napaka-`` surface."""

    @pytest.mark.parametrize(
        "root,_dim,_gloss,_ma,_pinaka,napaka", SAMPLE_INVENTORY
    )
    def test_indexed_as_adj(
        self,
        root: str,
        _dim: str,
        _gloss: str,
        _ma: str,
        _pinaka: str,
        napaka: str,
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(napaka))
        adj_analyses = [a for a in out if a.pos == "ADJ"]
        assert len(adj_analyses) == 1, (
            f"expected exactly one ADJ analysis for {napaka!r}; "
            f"got {[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )
        assert adj_analyses[0].lemma == root

    @pytest.mark.parametrize(
        "root,_dim,_gloss,_ma,_pinaka,napaka", SAMPLE_INVENTORY
    )
    def test_carries_intensive_degree_and_intensifier_flag(
        self,
        root: str,
        _dim: str,
        _gloss: str,
        _ma: str,
        _pinaka: str,
        napaka: str,
    ) -> None:
        analyzer = Analyzer.from_default()
        adj = next(
            a for a in analyzer.analyze_one(_tok(napaka)) if a.pos == "ADJ"
        )
        assert adj.feats.get("COMP_DEGREE") == "INTENSIVE"
        assert adj.feats.get("INTENSIFIER") == "YES"
        assert adj.feats.get("PREDICATIVE") == "YES"  # intrinsic
        assert adj.feats.get("LEMMA") == root         # lemma policy


# === Cross-cell distinct surfaces / no collisions =========================


class TestParadigmCellSeparation:
    """Each root produces three distinct surfaces (ma- / pinaka- / napaka-)
    with disjoint feats. Confirms the three cells are independent and
    the productive opt-in fires all three on every ``ma_adj`` root."""

    @pytest.mark.parametrize(
        "_root,_dim,_gloss,ma,pinaka,napaka", SAMPLE_INVENTORY
    )
    def test_three_cells_three_surfaces(
        self,
        _root: str,
        _dim: str,
        _gloss: str,
        ma: str,
        pinaka: str,
        napaka: str,
    ) -> None:
        # All three surfaces are distinct strings.
        assert len({ma, pinaka, napaka}) == 3

    def test_bare_ma_surface_unaffected_by_phase5h_cells(self) -> None:
        """The Phase 5g ``maganda`` analysis carries no
        ``COMP_DEGREE`` and no ``INTENSIFIER`` — Phase 5h cells fire
        on the same root but produce a *different* surface."""
        analyzer = Analyzer.from_default()
        adj = next(
            a for a in analyzer.analyze_one(_tok("maganda")) if a.pos == "ADJ"
        )
        assert adj.feats.get("COMP_DEGREE") is None
        assert "INTENSIFIER" not in adj.feats
        assert adj.feats.get("PREDICATIVE") == "YES"  # unchanged
        assert adj.feats.get("LEMMA") == "ganda"      # unchanged

    def test_bare_pinaka_is_unk(self) -> None:
        """``pinaka`` standalone is a bound prefix, not a free word —
        no analyzer entry should match it as ADJ / NOUN / PART."""
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("pinaka"))
        assert all(a.pos == "_UNK" for a in out), (
            f"unexpected non-_UNK analysis for bare 'pinaka': "
            f"{[(a.pos, a.lemma) for a in out]}"
        )

    def test_bare_napaka_is_unk(self) -> None:
        """``napaka`` standalone is a bound prefix, not a free word."""
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("napaka"))
        assert all(a.pos == "_UNK" for a in out)


# === Productivity over the full Phase 5g inventory ========================
#
# All 30 Phase 5g ADJ roots declare ``affix_class: [ma_adj]`` so all
# three cells should fire. Spot-check that every root produces the
# pinaka- and napaka- forms by walking the lex.


class TestFullInventoryProductivity:
    """Every ``ma_adj`` root produces both new derivations."""

    def test_all_ma_adj_roots_produce_superlative(self) -> None:
        analyzer = Analyzer.from_default()
        ma_adj_roots = [
            r for r in analyzer._data.roots
            if r.pos == "ADJ" and "ma_adj" in r.affix_class
        ]
        assert len(ma_adj_roots) >= 30, (
            f"expected at least 30 ma_adj-opting ADJ roots from "
            f"Phase 5g; got {len(ma_adj_roots)}"
        )
        for root in ma_adj_roots:
            pinaka_surface = "pinakama" + root.citation
            out = analyzer.analyze_one(_tok(pinaka_surface))
            adj_analyses = [a for a in out if a.pos == "ADJ"]
            assert any(
                a.feats.get("COMP_DEGREE") == "SUPERLATIVE"
                and a.lemma == root.citation
                for a in adj_analyses
            ), (
                f"expected SUPERLATIVE analysis for {pinaka_surface!r} "
                f"(root {root.citation!r}); got "
                f"{[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
            )

    def test_all_ma_adj_roots_produce_intensive(self) -> None:
        analyzer = Analyzer.from_default()
        ma_adj_roots = [
            r for r in analyzer._data.roots
            if r.pos == "ADJ" and "ma_adj" in r.affix_class
        ]
        for root in ma_adj_roots:
            napaka_surface = "napaka" + root.citation
            out = analyzer.analyze_one(_tok(napaka_surface))
            adj_analyses = [a for a in out if a.pos == "ADJ"]
            assert any(
                a.feats.get("COMP_DEGREE") == "INTENSIVE"
                and a.feats.get("INTENSIFIER") == "YES"
                and a.lemma == root.citation
                for a in adj_analyses
            ), (
                f"expected INTENSIVE analysis for {napaka_surface!r} "
                f"(root {root.citation!r}); got "
                f"{[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
            )


# === End-to-end parse via Phase 5g predicative-adj clause rule ============
#
# The new ADJ surfaces carry ``PREDICATIVE=YES`` intrinsically (set
# by the analyzer for every adjective-paradigm cell), so the Phase
# 5g Commit 3 rule (``S → ADJ[PREDICATIVE=YES] NP[CASE=NOM]``)
# composes with them unchanged. No new grammar rules in Commit 1.


class TestEndToEndParse:
    """The new ADJ surfaces compose with the existing predicative-adj
    clause rule without any grammar-rule additions."""

    @pytest.mark.parametrize("sentence,lemma", [
        ("Pinakamaganda ang bata.",   "ganda"),
        ("Pinakamatalino siya.",       "talino"),
        ("Pinakamabilis ang kabayo.",  "bilis"),
        ("Pinakamaliit ang bahay.",    "liit"),
    ])
    def test_superlative_predicative_clause(
        self, sentence: str, lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 1, (
            f"expected one parse for {sentence!r}; got {len(parses)}"
        )
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED") == "ADJ <SUBJ>"
        assert fstruct.feats.get("ADJ_LEMMA") == lemma
        assert fstruct.feats.get("PREDICATIVE") == "YES"

    @pytest.mark.parametrize("sentence,lemma", [
        ("Napakaganda ang bahay.",   "ganda"),
        ("Napakatalino siya.",        "talino"),
        ("Napakaliit ang bahay.",     "liit"),
        ("Napakainit ang tubig.",     "init"),
    ])
    def test_intensive_predicative_clause(
        self, sentence: str, lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 1, (
            f"expected one parse for {sentence!r}; got {len(parses)}"
        )
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED") == "ADJ <SUBJ>"
        assert fstruct.feats.get("ADJ_LEMMA") == lemma
        assert fstruct.feats.get("PREDICATIVE") == "YES"

    def test_phase5g_baseline_still_parses(self) -> None:
        """Sanity: bare ``ma-`` predicative clauses still parse
        identically to Phase 5g — the new cells don't perturb the
        existing surfaces."""
        parses = parse_text("Maganda ang bata.")
        assert len(parses) == 1
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED") == "ADJ <SUBJ>"
        assert fstruct.feats.get("ADJ_LEMMA") == "ganda"
