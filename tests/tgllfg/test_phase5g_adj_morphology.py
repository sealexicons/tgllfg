"""Phase 5g Commit 1: ADJ analyzer dispatch and productive ``ma-`` derivation.

Roadmap §12.1 analytical commitment: ``ma-`` adjectives are
``POS=ADJ`` with intrinsic ``[PREDICATIVE+]``, NOT stative VERBs.
The seed inventory (``data/tgl/adjectives.yaml``) carries 6 high-
frequency roots — ``ganda`` / ``talino`` / ``tanda`` / ``liit`` /
``taas`` / ``bilis`` — each opting into the ``ma_adj`` paradigm
cell which prefixes ``ma-``.

These tests exercise the analyzer-layer mechanics (dispatch on
``r.pos == "ADJ"``, paradigm-driven surface generation, lemma
policy, intrinsic ``PREDICATIVE: YES``, multiple analyses across
POS classes). NP-internal modifier composition lands in Commit 2;
the predicative-adj clause rule lands in Commit 3.
"""

from __future__ import annotations

import pytest

from tgllfg.common import Token
from tgllfg.morph import (
    AdjectiveCell,
    Analyzer,
    MorphData,
    Operation,
    Root,
    load_morph_data,
)


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === Seed-inventory paired-assertion table ================================
#
# (root, expected_surface, expected_gloss). Mirrors the
# verb-paradigm test conventions in test_morph_paradigms.py.

SEED_INVENTORY = [
    ("ganda",  "maganda",  "beautiful"),
    ("talino", "matalino", "intelligent"),
    ("tanda",  "matanda",  "old"),
    ("liit",   "maliit",   "small"),
    ("taas",   "mataas",   "high, tall"),
    ("bilis",  "mabilis",  "quick, fast"),
]


class TestSeedInventorySurfaces:
    """Each seed root produces the expected ``ma+root`` surface."""

    @pytest.mark.parametrize("root,surface,_gloss", SEED_INVENTORY)
    def test_surface_indexed_as_adj(
        self, root: str, surface: str, _gloss: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        adj_analyses = [a for a in out if a.pos == "ADJ"]
        assert len(adj_analyses) == 1, (
            f"expected exactly one ADJ analysis for {surface!r}; "
            f"got {[(a.pos, a.lemma) for a in out]}"
        )
        assert adj_analyses[0].lemma == root

    @pytest.mark.parametrize("root,surface,_gloss", SEED_INVENTORY)
    def test_predicative_feature_is_intrinsic(
        self, root: str, surface: str, _gloss: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        adj = next(a for a in out if a.pos == "ADJ")
        assert adj.feats.get("PREDICATIVE") == "YES", (
            f"ADJ {surface!r} (lemma {root!r}) should carry "
            f"PREDICATIVE=YES intrinsically; feats={adj.feats}"
        )

    @pytest.mark.parametrize("root,surface,_gloss", SEED_INVENTORY)
    def test_is_known_surface(
        self, root: str, surface: str, _gloss: str
    ) -> None:
        analyzer = Analyzer.from_default()
        assert analyzer.is_known_surface(surface)


# === Lemma policy =========================================================


class TestLemmaPolicy:
    """ADJ lemmas are bare roots (parallel to the verbal convention
    where ``kumain`` → ``kain``). The bare root surface itself is
    NOT indexed as ADJ — the seed analytical position is that bare
    ``ganda`` is a noun ("beauty") and ``maganda`` is the
    productively-derived adjective."""

    def test_bare_root_not_indexed_as_adj(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("ganda"))
        adj_analyses = [a for a in out if a.pos == "ADJ"]
        assert adj_analyses == [], (
            f"bare root 'ganda' should not be indexed as ADJ; "
            f"got {[(a.pos, a.lemma) for a in out]}"
        )

    def test_lemma_is_root_not_surface(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("matalino"))
        adj = next(a for a in out if a.pos == "ADJ")
        assert adj.lemma == "talino"
        assert adj.lemma != "matalino"


# === Multi-POS coexistence ================================================


class TestMultiPosCoexistence:
    """Roots that appear both in verbs.yaml and adjectives.yaml
    (``ganda``, ``bilis``, ``taas``) coexist as separate analyses
    because the ADJ surface (``maganda``) and the verbal surfaces
    (``gumanda`` / ``naganda`` / ``gaganda`` / ...) are distinct
    strings. Phase 5g's additive policy (plan §4) leaves the verbal
    entries untouched."""

    def test_ganda_verbal_inchoative_still_parses(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("gumanda"))
        verb_analyses = [a for a in out if a.pos == "VERB"]
        assert len(verb_analyses) >= 1
        assert any(a.lemma == "ganda" for a in verb_analyses)

    def test_maganda_only_adj_not_verb(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("maganda"))
        # The bare ``ma + root`` surface is ADJ-only — the verbal
        # ``ma`` paradigm produces ``magaganda`` (CTPL NVOL),
        # ``naganda`` (PFV NVOL), etc., but not bare ``maganda``.
        verb_analyses = [a for a in out if a.pos == "VERB"]
        adj_analyses = [a for a in out if a.pos == "ADJ"]
        assert verb_analyses == []
        assert len(adj_analyses) == 1


# === MorphData loading ====================================================


class TestMorphDataLoading:
    """The seed YAML loads ADJ roots and adjective cells correctly."""

    def test_adjective_roots_loaded(self) -> None:
        data = load_morph_data()
        adj_roots = [r for r in data.roots if r.pos == "ADJ"]
        adj_lemmas = {r.citation for r in adj_roots}
        assert {"ganda", "talino", "tanda", "liit", "taas", "bilis"}.issubset(
            adj_lemmas
        )

    def test_adjective_cells_loaded(self) -> None:
        data = load_morph_data()
        ma_adj_cells = [
            c for c in data.adjective_cells if c.affix_class == "ma_adj"
        ]
        assert len(ma_adj_cells) == 1
        cell = ma_adj_cells[0]
        assert cell.operations == [Operation(op="prefix", value="ma")]


# === Affix-class filter (seed cell only fires for ma_adj roots) ==========


class TestAffixClassFilter:
    """The ``ma_adj`` cell only fires for roots whose ``affix_class``
    list contains ``ma_adj``. Verb roots with ``affix_class: [ma]``
    are filtered out — the verbal ``ma`` and the adjectival
    ``ma_adj`` are intentionally distinct strings."""

    def test_in_memory_root_with_no_ma_adj_class_skipped(self) -> None:
        # Construct a synthetic MorphData with one ADJ root that
        # does NOT declare ma_adj. The cell should not fire.
        data = MorphData(
            roots=[
                Root(citation="dummy", pos="ADJ", affix_class=["other_class"]),
            ],
            adjective_cells=[
                AdjectiveCell(
                    affix_class="ma_adj",
                    operations=[Operation(op="prefix", value="ma")],
                ),
            ],
        )
        analyzer = Analyzer(data)
        # No ADJ surfaces should be indexed for the dummy root.
        assert "madummy" not in analyzer._index.adjectives
        assert "dummy" not in analyzer._index.adjectives


# === Per-cell feats override the intrinsic PREDICATIVE ==================


class TestPerCellFeats:
    """Per-cell ``feats`` extend / override the intrinsic
    ``PREDICATIVE: YES`` — forward-looking for Phase 5h cells
    (``napaka-`` intensifier, ``pinaka-`` superlative) that may
    add an ``INTENSITY`` or ``DEGREE`` feature without disturbing
    the predicative slot."""

    def test_extra_feat_rides_into_analysis(self) -> None:
        data = MorphData(
            roots=[
                Root(citation="ganda", pos="ADJ", affix_class=["ma_adj"]),
            ],
            adjective_cells=[
                AdjectiveCell(
                    affix_class="ma_adj",
                    operations=[Operation(op="prefix", value="ma")],
                    feats={"DEGREE": "POSITIVE"},
                ),
            ],
        )
        analyzer = Analyzer(data)
        analyses = analyzer._index.adjectives["maganda"]
        assert len(analyses) == 1
        feats = analyses[0].feats
        assert feats["PREDICATIVE"] == "YES"
        assert feats["DEGREE"] == "POSITIVE"

    def test_per_cell_feat_can_override_predicative(self) -> None:
        # Hypothetical "modifier-only" cell that explicitly sets
        # PREDICATIVE: NO. Tests the override semantics — not in
        # the seed inventory.
        data = MorphData(
            roots=[
                Root(citation="ganda", pos="ADJ", affix_class=["mod_only"]),
            ],
            adjective_cells=[
                AdjectiveCell(
                    affix_class="mod_only",
                    operations=[Operation(op="prefix", value="ma")],
                    feats={"PREDICATIVE": "NO"},
                ),
            ],
        )
        analyzer = Analyzer(data)
        analyses = analyzer._index.adjectives["maganda"]
        assert analyses[0].feats["PREDICATIVE"] == "NO"


# === Per-root feats =======================================================


class TestPerRootFeats:
    """Per-root ``feats`` ride into every generated form (parallel
    to verb roots' CTRL_CLASS / APPL / CAUS handling). Phase 5h's
    SEM_CLASS subcategorization (SIZE / COLOUR / EVALUATIVE) will
    use this slot."""

    def test_root_feats_carry_through(self) -> None:
        data = MorphData(
            roots=[
                Root(
                    citation="ganda",
                    pos="ADJ",
                    affix_class=["ma_adj"],
                    feats={"SEM_CLASS": "EVALUATIVE"},
                ),
            ],
            adjective_cells=[
                AdjectiveCell(
                    affix_class="ma_adj",
                    operations=[Operation(op="prefix", value="ma")],
                ),
            ],
        )
        analyzer = Analyzer(data)
        feats = analyzer._index.adjectives["maganda"][0].feats
        assert feats["SEM_CLASS"] == "EVALUATIVE"
        assert feats["PREDICATIVE"] == "YES"
