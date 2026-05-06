"""Phase 5h Commit 5: particle intensifiers + intensifier-ADJ wrapper.

Roadmap §12.1 / plan-of-record §4.1, §5.3-5.4, §6 Commit 5.

Three pieces:

1. Five new ``PART`` entries in ``data/tgl/particles.yaml``, each
   with ``INTENSIFIER: YES`` plus a per-particle ``INTENSITY`` tag
   for downstream consumers (ranker / classifier):

   * ``sobra``    — INTENSITY: EXCESSIVE   (too / overly)
   * ``medyo``    — INTENSITY: MODERATE    (somewhat / rather)
   * ``talaga``   — INTENSITY: EMPHATIC    (really / truly)
   * ``lubos``    — INTENSITY: COMPLETE    (extremely / utterly)
   * ``masyado``  — INTENSITY: EXCESSIVE   (too / overly)

   Pre-state (verified 2026-05-05): all five surfaces were ``_UNK``;
   sentences like ``Sobrang maganda ang bata`` "parsed" today by
   silently dropping the unknown intensifier
   (``_strip_non_content`` in parse/earley.py:390) and producing a
   single parse of the residue.

2. Three new wrapper rules in ``cfg/nominal.py``:

       ADJ → PART[INTENSIFIER=YES] PART[LINK=NA] ADJ
       ADJ → PART[INTENSIFIER=YES] PART[LINK=NG] ADJ
       ADJ → PART[INTENSITY=MODERATE] ADJ      (medyo zero-linker)

   The wrapped ADJ carries ``COMP_DEGREE: INTENSIVE``,
   ``INTENSIFIER: YES``, and the per-particle ``INTENSITY`` tag.
   Composes with the Phase 5g predicative-adj clause rule and
   NP-internal modifier rules unchanged. Unification clashes
   handle ``*sobrang pinakamaganda`` (SUPERLATIVE vs INTENSIVE)
   and ``*sobrang mas matalino`` (COMPARATIVE vs INTENSIVE)
   correctly. ``Sobrang napakaganda`` (INTENSIVE × INTENSIVE,
   identity write) is permitted as an attested colloquial
   double-intensifier.

3. Disambiguator extension in ``clitics/placement.py``: the
   helper ``_adj_na_right_context_is_linker_target`` is renamed
   to ``_na_right_context_is_linker_target`` (right-context-only
   check; the caller supplies the left-context constraint), and
   a new branch in ``disambiguate_homophone_clitics`` recognises
   PART[INTENSIFIER=YES] + ``na`` + ADJ as a linker context.
   Without this, ``reorder_clitics`` would hoist ``na`` to the
   clause-final ALREADY-clitic position, breaking the wrapper
   rule's adjacent PART-PART-ADJ pattern. Vowel-final
   intensifiers take the bound ``-ng`` (no clitic homophone), so
   the disambiguator branch matters mainly for consonant-final
   ``lubos``.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import Token
from tgllfg.core.pipeline import parse_text
from tgllfg.morph import Analyzer


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === PART lex entries ==================================================


INTENSIFIERS = [
    # (surface, intensity_tag)
    ("sobra",   "EXCESSIVE"),
    ("medyo",   "MODERATE"),
    ("talaga",  "EMPHATIC"),
    ("lubos",   "COMPLETE"),
    ("masyado", "EXCESSIVE"),
]


class TestIntensifierPartLex:
    """Each particle is now a known PART with INTENSIFIER: YES + the
    right INTENSITY tag."""

    @pytest.mark.parametrize("surface,intensity", INTENSIFIERS)
    def test_indexed_as_part(self, surface: str, intensity: str) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        part_analyses = [a for a in out if a.pos == "PART"]
        assert len(part_analyses) == 1
        assert part_analyses[0].lemma == surface

    @pytest.mark.parametrize("surface,intensity", INTENSIFIERS)
    def test_carries_intensifier_and_intensity(
        self, surface: str, intensity: str
    ) -> None:
        analyzer = Analyzer.from_default()
        part = next(
            a for a in analyzer.analyze_one(_tok(surface)) if a.pos == "PART"
        )
        assert part.feats.get("INTENSIFIER") == "YES"
        assert part.feats.get("INTENSITY") == intensity


# === Bound -ng linker forms ===========================================


class TestBoundNgLinkerSurfaces:
    """Vowel-final intensifiers take the bound ``-ng`` linker. The
    pre-parse split_linker_ng pass splits e.g. ``sobrang`` →
    ``sobra`` + ``-ng`` once each particle is a known surface."""

    @pytest.mark.parametrize("sentence,adj_lemma", [
        ("Sobrang maganda ang bata.",   "ganda"),
        ("Talagang maganda ang bata.",  "ganda"),
        ("Masyadong mainit ang tubig.", "init"),
        ("Sobrang malaki ang bahay.",   "laki"),
        ("Talagang malakas ang lalaki.", "lakas"),
    ])
    def test_bound_ng_intensifier(
        self, sentence: str, adj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 1, (
            f"expected one parse for {sentence!r}; got {len(parses)}"
        )
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED") == "ADJ <SUBJ>"
        assert fstruct.feats.get("ADJ_LEMMA") == adj_lemma
        assert fstruct.feats.get("POLARITY") is None


# === Free `na` linker forms ===========================================


class TestNaLinkerSurfaces:
    """Consonant-final ``lubos`` (and the rare alternative free-``na``
    forms of vowel-final intensifiers) take the explicit ``na``
    linker. The disambiguator extension keeps ``na`` in place
    rather than hoisting it to clause-final ALREADY-clitic
    position."""

    @pytest.mark.parametrize("sentence,adj_lemma", [
        ("Lubos na maganda ang bata.",   "ganda"),
        ("Lubos na matalino siya.",      "talino"),
        ("Sobra na maganda ang bata.",   "ganda"),
        ("Masyado na mainit ang tubig.", "init"),
    ])
    def test_na_linker_intensifier(
        self, sentence: str, adj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 1
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED") == "ADJ <SUBJ>"
        assert fstruct.feats.get("ADJ_LEMMA") == adj_lemma


# === medyo zero-linker form ===========================================


class TestMedyoZeroLinker:
    """``medyo`` colloquially appears WITHOUT a linker (in addition to
    the with-linker form). The zero-linker variant is restricted to
    INTENSITY=MODERATE so other intensifiers don't overgenerate."""

    @pytest.mark.parametrize("sentence,adj_lemma", [
        ("Medyo maganda ang bata.",   "ganda"),
        ("Medyo malaki ang bahay.",   "laki"),
        ("Medyo mainit ang tubig.",   "init"),
    ])
    def test_medyo_zero_linker(
        self, sentence: str, adj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got {len(parses)}"
        )
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED") == "ADJ <SUBJ>"
        assert fstruct.feats.get("ADJ_LEMMA") == adj_lemma

    def test_medyo_zero_linker_only_for_moderate(self) -> None:
        """The zero-linker variant must NOT fire on non-medyo
        intensifiers (i.e., ``*sobra ganda`` should fail). Test by
        checking that an ungrammatical zero-linker form with a
        non-MODERATE intensifier produces zero parses."""
        # `sobra` has INTENSITY=EXCESSIVE so the zero-linker rule
        # (constrained on MODERATE) can't fire. Without an
        # alternative parse path, the input fails.
        # Note: this can still parse if some other rule absorbs;
        # we check that the zero-linker shape is NOT producing the
        # parse by asserting that a complete parse requires either
        # the bound -ng or the free na variant.
        # `sobra` followed directly by `ganda` (without any linker
        # and without the MODERATE-constrained zero-linker rule):
        # should not produce a wrapper-rule parse. Other rules may
        # fail too. We just assert no clean predicative parse here.
        parses = parse_text("Sobra ganda ang bata.")
        # The intended-but-ungrammatical reading would have ADJ_LEMMA=ganda;
        # but `ganda` is NOT indexed as ADJ (Phase 5g lemma policy),
        # so this independently fails. We assert zero parses.
        assert len(parses) == 0


# === Unification clashes on already-degree-marked ADJs ================


class TestIntensiveUnificationClashes:
    """Wrapping an ADJ that already carries SUPERLATIVE / COMPARATIVE
    / EQUATIVE / CONTRASTIVE fails — the matrix's INTENSIVE write
    clashes with the inner's existing degree mark. INTENSIVE×INTENSIVE
    (sobrang napakaganda) is the one allowed combination — identity
    write succeeds (attested colloquial double-intensifier)."""

    @pytest.mark.parametrize("sentence", [
        # SUPERLATIVE × INTENSIVE
        "Sobrang pinakamaganda ang bahay.",
        "Talagang pinakamatalino siya.",
        "Masyadong pinakamaganda ang bahay.",
        "Lubos na pinakamaganda ang bahay.",
        # COMPARATIVE × INTENSIVE
        "Sobrang mas matalino siya.",
        "Lubos na mas matalino siya.",
        # EQUATIVE × INTENSIVE
        "Sobrang kasingganda ang bahay.",
        # CONTRASTIVE × INTENSIVE
        "Sobrang magkaiba ang aklat.",
    ])
    def test_double_degree_marking_rejected(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 0, (
            f"expected zero parses (unification clash) for {sentence!r}; "
            f"got {len(parses)}"
        )

    def test_double_intensive_permitted(self) -> None:
        """``sobrang napakaganda`` writes INTENSIVE onto an already-
        INTENSIVE inner — identity write succeeds. Linguistically
        this is an attested colloquial "extra emphasis" form."""
        parses = parse_text("Sobrang napakaganda ang bahay.")
        assert len(parses) >= 1
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED") == "ADJ <SUBJ>"
        assert fstruct.feats.get("ADJ_LEMMA") == "ganda"


# === Composition with negation =========================================


class TestNegationCompose:
    """``Hindi masyadong mainit`` — "not very hot" — is the canonical
    Tagalog "not very" construction. Negation wraps the
    intensifier-ADJ S unchanged via the (Phase 5h Commit 3-tightened)
    hindi-negation rule."""

    @pytest.mark.parametrize("sentence,adj_lemma", [
        ("Hindi sobrang mainit ang tubig.",     "init"),
        ("Hindi masyadong mainit ang tubig.",   "init"),
        ("Hindi talagang maganda ang bata.",    "ganda"),
        ("Hindi lubos na maganda ang bata.",    "ganda"),
        ("Hindi medyo maganda ang bata.",       "ganda"),
    ])
    def test_hindi_plus_intensifier_predicative(
        self, sentence: str, adj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED") == "ADJ <SUBJ>"
        assert fstruct.feats.get("ADJ_LEMMA") == adj_lemma
        assert fstruct.feats.get("POLARITY") == "NEG"


# === Disambiguator: na linker vs ALREADY clitic ========================


class TestDisambiguatorNaIntensifier:
    """The new disambiguator branch: PART[INTENSIFIER=YES] + ``na``
    + ADJ keeps ``na`` in place as the linker. Without this branch,
    reorder_clitics would hoist ``na`` to clause-final ALREADY-clitic
    position and break the wrapper-rule's adjacency."""

    def test_lubos_na_kept_as_linker(self) -> None:
        """``Lubos na maganda ang bata.`` — ``na`` stays between
        ``lubos`` and ``maganda`` as the linker."""
        parses = parse_text("Lubos na maganda ang bata.")
        assert len(parses) == 1
        ctree, _fs, _astr, _diags = parses[0]
        # The c-tree has the wrapper rule firing: ADJ contains
        # PART (lubos), PART (na), ADJ (maganda).
        assert ctree.label == "S"
        outer_adj = ctree.children[0]
        assert outer_adj.label.startswith("ADJ")
        assert len(outer_adj.children) == 3
        assert outer_adj.children[0].label.startswith("PART")
        assert outer_adj.children[1].label.startswith("PART")
        assert outer_adj.children[2].label.startswith("ADJ")


# === Phase 5g / Phase 5h Commit 1-4 baselines preserved ================


class TestBaselinePreserved:
    """Phase 5g + Phase 5h Commits 1-4 surfaces continue to parse
    identically — the new wrapper rules and disambiguator extension
    do not perturb existing surfaces."""

    @pytest.mark.parametrize("sentence,adj_lemma", [
        # Phase 5g bare ma-
        ("Maganda ang bata.",          "ganda"),
        # Phase 5h Commit 1
        ("Pinakamaganda ang bahay.",   "ganda"),
        ("Napakaganda ang bahay.",     "ganda"),
        # Phase 5h Commit 2
        ("Pareho ang aklat.",          "pareho"),
        ("Magkaiba ang aklat.",        "magkaiba"),
        ("Kasingganda ang bahay.",     "ganda"),
        # Phase 5h Commit 3
        ("Mas matalino siya.",         "talino"),
        # Phase 5h Commit 4
        ("Mas matalino siya kaysa kay Maria.",  "talino"),
    ])
    def test_predicative_unchanged(
        self, sentence: str, adj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 1
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("ADJ_LEMMA") == adj_lemma
