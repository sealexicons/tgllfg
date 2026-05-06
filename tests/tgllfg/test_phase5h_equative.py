"""Phase 5h Commit 2: ``kasing-`` / ``sing-`` equative cells +
non-productive equative-identity ADJ entries (``pareho``,
``magkapareho``, ``magkaiba``) + analyzer's bare-citation indexer.

Roadmap §12.1 / plan-of-record §4.2-4.3 / §6 Commit 2. Three
moving pieces:

1. Two new productive paradigm cells in
   ``data/tgl/adj_paradigms.yaml`` mirror the Phase 5g + 5h
   Commit 1 cells' productive opt-in (``affix_class: ma_adj``):

   * ``kasing-`` equative: ``kasing`` + bare root → e.g.
     ``kasingganda`` "as beautiful (as)".
     ``COMP_DEGREE: EQUATIVE``.
   * ``sing-`` equative (colloquial doublet): ``sing`` + bare
     root → ``singganda``. Same ``COMP_DEGREE: EQUATIVE``.

   Both attach to the bare root (no ``ma-``) — the standard
   Schachter–Otanes analysis.

2. Three new lex entries in ``data/tgl/adjectives.yaml`` declare
   ``affix_class: []`` — the citation IS the adjectival surface,
   no productive derivation. ``pareho`` "same/alike" is
   polysemous with the Phase 5f Commit 23 ``Q[QUANT=BOTH,
   DUAL=YES]`` floated-quantifier reading; the analyzer indexes
   both readings against the same surface and rule context
   disambiguates. ``magkapareho`` "alike" (formal doublet) and
   ``magkaiba`` "different" (contrastive) are new ADJ-only
   entries.

3. The analyzer dispatches on ``r.affix_class`` for ``r.pos ==
   "ADJ"``: a non-empty list goes through the productive
   ``_index_adjective_paradigms``; an empty list goes through
   the new ``_index_adjective_bare_root``. The split is needed
   because the legacy ``_affix_class_match`` treats an empty
   ``cell_class`` as a wildcard, so a YAML "bare cell" with
   ``affix_class: ""`` would inappropriately fire on every
   ``ma_adj`` root too.

End-to-end parses for the new surfaces compose with the Phase 5g
predicative-adj clause rule unchanged (no new grammar rules).
The two-NP standard-of-comparison construction
(``Kasingganda si Maria si Ana``) needs a separate frame
analysis and lands in Phase 5h Commit 6.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import Token
from tgllfg.core.pipeline import parse_text
from tgllfg.morph import Analyzer


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# Sample of Phase 5g ``ma_adj`` roots, one per dimension. The
# kasing- / sing- cells are productive on every ma_adj root, so
# this sample is sufficient for parametrised coverage. Full
# productivity is asserted by TestFullInventoryProductivity below.

EQUATIVE_INVENTORY = [
    # (root, kasing_form, sing_form)
    ("ganda",  "kasingganda",  "singganda"),
    ("talino", "kasingtalino", "singtalino"),
    ("liit",   "kasingliit",   "singliit"),
    ("taas",   "kasingtaas",   "singtaas"),
    ("bilis",  "kasingbilis",  "singbilis"),
    ("linis",  "kasinglinis",  "singlinis"),
    ("init",   "kasinginit",   "singinit"),
    ("saya",   "kasingsaya",   "singsaya"),
]


# === kasing- equative cells =============================================


class TestKasingEquative:
    """Each Phase 5g ``ma_adj`` root produces a productive
    ``kasing-`` equative surface."""

    @pytest.mark.parametrize("root,kasing,_sing", EQUATIVE_INVENTORY)
    def test_indexed_as_adj(
        self, root: str, kasing: str, _sing: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(kasing))
        adj_analyses = [a for a in out if a.pos == "ADJ"]
        assert len(adj_analyses) == 1, (
            f"expected exactly one ADJ analysis for {kasing!r}; "
            f"got {[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )
        assert adj_analyses[0].lemma == root

    @pytest.mark.parametrize("root,kasing,_sing", EQUATIVE_INVENTORY)
    def test_carries_equative_degree(
        self, root: str, kasing: str, _sing: str
    ) -> None:
        analyzer = Analyzer.from_default()
        adj = next(
            a for a in analyzer.analyze_one(_tok(kasing)) if a.pos == "ADJ"
        )
        assert adj.feats.get("COMP_DEGREE") == "EQUATIVE"
        assert adj.feats.get("PREDICATIVE") == "YES"  # intrinsic
        assert adj.feats.get("LEMMA") == root


# === sing- equative cells (colloquial doublet) ==========================


class TestSingEquative:
    """Each Phase 5g ``ma_adj`` root produces a productive ``sing-``
    equative surface (colloquial doublet of ``kasing-``)."""

    @pytest.mark.parametrize("_root,_kasing,sing", EQUATIVE_INVENTORY)
    def test_indexed_as_adj(
        self, _root: str, _kasing: str, sing: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(sing))
        adj_analyses = [a for a in out if a.pos == "ADJ"]
        assert len(adj_analyses) == 1, (
            f"expected exactly one ADJ analysis for {sing!r}; "
            f"got {[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )

    @pytest.mark.parametrize("root,_kasing,sing", EQUATIVE_INVENTORY)
    def test_carries_equative_degree(
        self, root: str, _kasing: str, sing: str
    ) -> None:
        analyzer = Analyzer.from_default()
        adj = next(
            a for a in analyzer.analyze_one(_tok(sing)) if a.pos == "ADJ"
        )
        assert adj.feats.get("COMP_DEGREE") == "EQUATIVE"
        assert adj.feats.get("PREDICATIVE") == "YES"
        assert adj.feats.get("LEMMA") == root


# === Productive equative cells fire on the full inventory ===============


class TestEquativeFullInventoryProductivity:
    """Every ``ma_adj`` root produces both equative derivations."""

    def test_all_ma_adj_roots_produce_kasing_equative(self) -> None:
        analyzer = Analyzer.from_default()
        ma_adj_roots = [
            r for r in analyzer._data.roots
            if r.pos == "ADJ" and "ma_adj" in r.affix_class
        ]
        for root in ma_adj_roots:
            kasing_surface = "kasing" + root.citation
            out = analyzer.analyze_one(_tok(kasing_surface))
            assert any(
                a.feats.get("COMP_DEGREE") == "EQUATIVE"
                and a.lemma == root.citation
                and a.pos == "ADJ"
                for a in out
            ), (
                f"expected EQUATIVE analysis for {kasing_surface!r} "
                f"(root {root.citation!r}); got "
                f"{[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
            )

    def test_all_ma_adj_roots_produce_sing_equative(self) -> None:
        analyzer = Analyzer.from_default()
        ma_adj_roots = [
            r for r in analyzer._data.roots
            if r.pos == "ADJ" and "ma_adj" in r.affix_class
        ]
        for root in ma_adj_roots:
            sing_surface = "sing" + root.citation
            out = analyzer.analyze_one(_tok(sing_surface))
            assert any(
                a.feats.get("COMP_DEGREE") == "EQUATIVE"
                and a.lemma == root.citation
                and a.pos == "ADJ"
                for a in out
            )


# === Equative-prefix attachment is to the BARE root, not ma- form =======


class TestEquativeAttachesBareRoot:
    """``kasing-`` and ``sing-`` attach to the bare ADJ root, not to
    the ma-prefixed form. ``kasingmaganda`` is ungrammatical /
    unattested; the analyzer should not produce an ADJ analysis."""

    @pytest.mark.parametrize("surface", [
        "kasingmaganda",
        "kasingmatalino",
        "singmaganda",
        "singmatalino",
    ])
    def test_double_prefix_unanalyzed(self, surface: str) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        assert all(a.pos == "_UNK" for a in out), (
            f"unexpected non-_UNK analysis for {surface!r}; "
            f"got {[(a.pos, a.lemma) for a in out]}"
        )

    @pytest.mark.parametrize("bound", ["kasing", "sing"])
    def test_bound_prefix_alone_is_unk(self, bound: str) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(bound))
        assert all(a.pos == "_UNK" for a in out)


# === Bare-citation indexer for non-productive ADJ entries ==============


class TestBareCitationIndexer:
    """Phase 5h §4.2: ADJ roots with ``affix_class: []`` are indexed
    via the new ``_index_adjective_bare_root`` path. Citation IS the
    surface; per-root feats ride into the MorphAnalysis."""

    def test_pareho_is_polysemous_q_and_adj(self) -> None:
        """``pareho`` carries both the Phase 5f Commit 23 Q reading
        and the new Phase 5h ADJ reading (different POS, same
        surface, indexed in parallel)."""
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("pareho"))
        by_pos = {a.pos: a for a in out}
        assert "Q" in by_pos, f"expected Q reading; got {[a.pos for a in out]}"
        assert "ADJ" in by_pos, (
            f"expected ADJ reading; got {[a.pos for a in out]}"
        )
        # Q reading: floated-quantifier shape from Phase 5f Commit 23.
        q = by_pos["Q"]
        assert q.feats.get("QUANT") == "BOTH"
        assert q.feats.get("DUAL") == "YES"
        # ADJ reading: equative-identity predicate, intrinsically PREDICATIVE.
        adj = by_pos["ADJ"]
        assert adj.feats.get("PREDICATIVE") == "YES"
        assert adj.feats.get("EQUATIVE") == "YES"
        assert adj.feats.get("COMP_DEGREE") == "EQUATIVE"
        assert adj.lemma == "pareho"

    def test_magkapareho_indexed_as_adj(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("magkapareho"))
        adj_analyses = [a for a in out if a.pos == "ADJ"]
        assert len(adj_analyses) == 1
        adj = adj_analyses[0]
        assert adj.lemma == "magkapareho"
        assert adj.feats.get("PREDICATIVE") == "YES"
        assert adj.feats.get("EQUATIVE") == "YES"
        assert adj.feats.get("COMP_DEGREE") == "EQUATIVE"

    def test_magkaiba_indexed_as_adj_with_contrastive(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("magkaiba"))
        adj_analyses = [a for a in out if a.pos == "ADJ"]
        assert len(adj_analyses) == 1
        adj = adj_analyses[0]
        assert adj.lemma == "magkaiba"
        assert adj.feats.get("PREDICATIVE") == "YES"
        assert adj.feats.get("EQUATIVE") == "YES"  # family flag
        assert adj.feats.get("COMP_DEGREE") == "CONTRASTIVE"  # semantic value

    def test_productive_ma_adj_root_bare_citation_still_unindexed(
        self,
    ) -> None:
        """Phase 5g lemma policy preserved: roots with non-empty
        ``affix_class`` (the productive ``ma_adj`` family) do NOT
        have their bare citation indexed as ADJ. Only roots with
        empty ``affix_class`` go through the bare-citation path."""
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("ganda"))
        adj_analyses = [a for a in out if a.pos == "ADJ"]
        assert adj_analyses == [], (
            f"unexpected ADJ analysis for bare 'ganda'; got "
            f"{[(a.pos, a.lemma, dict(a.feats)) for a in adj_analyses]}"
        )

    def test_productive_ma_adj_surfaces_unaffected(self) -> None:
        """Phase 5g + 5h Commit 1 cells continue to fire on ma_adj
        roots; the bare-citation path doesn't perturb them."""
        analyzer = Analyzer.from_default()
        # Each productive cell still produces its surface with the
        # right feats.
        ma = next(
            a for a in analyzer.analyze_one(_tok("maganda")) if a.pos == "ADJ"
        )
        assert ma.lemma == "ganda" and ma.feats.get("COMP_DEGREE") is None
        sup = next(
            a for a in analyzer.analyze_one(_tok("pinakamaganda"))
            if a.pos == "ADJ"
        )
        assert sup.feats.get("COMP_DEGREE") == "SUPERLATIVE"
        intens = next(
            a for a in analyzer.analyze_one(_tok("napakaganda"))
            if a.pos == "ADJ"
        )
        assert intens.feats.get("COMP_DEGREE") == "INTENSIVE"


# === End-to-end parse via Phase 5g predicative-adj rule ================


class TestEquativePredicativeParse:
    """The new ADJ surfaces compose with the existing predicative-adj
    clause rule (Phase 5g Commit 3) without grammar-rule changes —
    they all carry ``PREDICATIVE=YES`` intrinsically."""

    @pytest.mark.parametrize("sentence,lemma", [
        ("Pareho ang aklat.",      "pareho"),
        ("Pareho ang aklat ko.",   "pareho"),
        ("Magkapareho ang aklat.", "magkapareho"),
        ("Magkaiba ang aklat.",    "magkaiba"),
        ("Magkaiba ang aklat ko.", "magkaiba"),
    ])
    def test_equative_identity_predicative(
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
        ("Kasingganda ang bahay.",  "ganda"),
        ("Kasinglinis ang bahay.",  "linis"),
        ("Singganda ang bahay.",    "ganda"),
    ])
    def test_kasing_sing_predicative_single_np(
        self, sentence: str, lemma: str
    ) -> None:
        """Single-NP equative predicative — the standard-NP form
        ``Kasingganda si X si Y`` requires a new frame and is
        deferred to Phase 5h Commit 6."""
        parses = parse_text(sentence)
        assert len(parses) == 1
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED") == "ADJ <SUBJ>"
        assert fstruct.feats.get("ADJ_LEMMA") == lemma

    def test_pareho_q_reading_still_works(self) -> None:
        """``pareho`` polysemy: the Q (floated-quantifier) reading
        from Phase 5f Commit 23 continues to parse via the
        ``S → S Q`` float rule. Sanity check that the new ADJ
        polysemy doesn't break the Q path."""
        parses = parse_text("Kumain sila pareho.")
        assert len(parses) == 1
        _ctree, fstruct, _astr, _diags = parses[0]
        # Q-float reading: matrix PRED comes from the verb, not
        # from a predicative-adj rule.
        assert fstruct.feats.get("PRED") == "EAT <SUBJ>"
        assert fstruct.feats.get("ADJ_LEMMA") is None
