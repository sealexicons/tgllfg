"""Phase 5h Commit 3: comparative ``mas`` PART + ADJ-wrapper rule.

Roadmap §12.1 / plan-of-record §4.1, §5.1, §6 Commit 3. Three
moving pieces:

1. New ``mas`` PART entry in ``data/tgl/particles.yaml`` carrying
   ``COMP_DEGREE: COMPARATIVE``. Pre-state: ``mas`` was ``_UNK``.
   The parser's ``_strip_non_content`` silently dropped ``mas``-only
   tokens, so today's ``Mas matalino siya.`` "parsed" by
   silently ignoring ``mas`` and producing a single parse of the
   residue ``Matalino siya``. Once this entry lands, ``mas`` is a
   known PART; the strip no longer fires on it.

2. New comparative-ADJ wrapper rule in ``cfg/nominal.py``:

       ADJ → PART[COMP_DEGREE=COMPARATIVE] ADJ

   Equations: ``(↑) = ↓2`` (share the inner ADJ's f-structure),
   ``(↑ COMP_DEGREE) = 'COMPARATIVE'`` (write COMPARATIVE onto
   the matrix), ``(↓1 COMP_DEGREE) =c 'COMPARATIVE'``
   (belt-and-braces constraint matching the Phase 5g convention).
   The wrapped ADJ composes with the existing Phase 5g
   predicative-adj clause rule and NP-internal modifier rules
   without any new clausal / nominal rules.

   Unification clash for already-degree-marked ADJs: writing
   COMPARATIVE onto an inner f-structure that already carries
   SUPERLATIVE (``pinakamaganda``) or INTENSIVE (``napakaganda``)
   correctly fails — ``*mas pinakamaganda`` is ungrammatical.

3. Closes a latent leak in the Phase 4 hindi-negation rule
   (``cfg/negation.py``). ``S → PART[POLARITY=NEG] S`` matches by
   the non-conflict category-pattern matcher: a particle
   without ``POLARITY`` absorbs the constraint and matches
   inappropriately. Pre-state probes (2026-05-05) showed
   ``Halos kumain ang bata`` and ``Tuwing kumain ang bata``
   parsing today with bogus ``POLARITY: NEG``. Once Phase 5h
   adds ``mas`` (PART without POLARITY), the leak would let
   ``Mas matalino siya`` parse twice — once via the new wrapper
   rule and once via the leaky negation rule. The fix: add the
   explicit ``(↓1 POLARITY) =c 'NEG'`` constraining equation,
   matching the Phase 5g Commit 3 belt-and-braces ``=c``
   pattern.

Phase 5h Commits 4 / 5 / 7 build on this commit:
* Commit 4 adds the ``kaysa`` comparison-complement
  (``Mas matalino siya kaysa kay Maria``).
* Commit 5 adds particle-intensifier wrapper rules with the
  same shape (``sobrang``, ``talagang``, etc.).
* Commit 7 generalises this rule to ``Q[VAGUE=YES]`` heads
  (``mas marami`` / ``mas kaunti`` quantifier-comparative).
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import Token
from tgllfg.core.pipeline import parse_text
from tgllfg.morph import Analyzer


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === ``mas`` PART lex entry ============================================


class TestComparativePartLex:
    """``mas`` is now a known PART with COMP_DEGREE: COMPARATIVE."""

    def test_mas_indexed_as_part(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("mas"))
        part_analyses = [a for a in out if a.pos == "PART"]
        assert len(part_analyses) >= 1, (
            f"expected at least one PART analysis for 'mas'; "
            f"got {[(a.pos, a.lemma) for a in out]}"
        )

    def test_mas_carries_comparative_feature(self) -> None:
        analyzer = Analyzer.from_default()
        part = next(
            a for a in analyzer.analyze_one(_tok("mas")) if a.pos == "PART"
        )
        assert part.feats.get("COMP_DEGREE") == "COMPARATIVE"
        assert part.lemma == "mas"

    def test_mas_carries_no_polarity(self) -> None:
        """``mas`` is NOT a negation marker; it must not carry
        ``POLARITY: NEG``. The hindi-negation rule's belt-and-braces
        constraint depends on this."""
        analyzer = Analyzer.from_default()
        part = next(
            a for a in analyzer.analyze_one(_tok("mas")) if a.pos == "PART"
        )
        assert "POLARITY" not in part.feats


# === Predicative comparative-ADJ ========================================


class TestComparativePredicative:
    """The wrapper rule produces a comparative-ADJ that fires the
    Phase 5g predicative-adj clause rule unchanged."""

    @pytest.mark.parametrize("sentence,lemma", [
        ("Mas matalino siya.",        "talino"),
        ("Mas mabilis ang kabayo.",   "bilis"),
        ("Mas maganda ang bahay.",    "ganda"),
        ("Mas malaki ang bahay.",     "laki"),
        ("Mas mainit ang tubig.",     "init"),
        ("Mas masaya ang bata.",      "saya"),
    ])
    def test_predicative_comparative(
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
        # No phantom NEG polarity from the (now-fixed) hindi rule leak.
        assert fstruct.feats.get("POLARITY") is None

    def test_comparative_c_tree_shape(self) -> None:
        """The c-tree shows the wrapper rule firing: outer ADJ
        contains PART (``mas``) and inner ADJ; outer S has the
        wrapped ADJ as its predicative head."""
        parses = parse_text("Mas matalino siya.")
        assert len(parses) == 1
        ctree, _fs, _astr, _diags = parses[0]
        # Top-level S
        assert ctree.label == "S"
        assert len(ctree.children) == 2
        # First child: outer ADJ (the wrapper)
        outer_adj = ctree.children[0]
        assert outer_adj.label.startswith("ADJ")
        assert len(outer_adj.children) == 2
        # Inner: PART, then ADJ (the lex-token)
        part_node = outer_adj.children[0]
        assert part_node.label.startswith("PART")
        inner_adj = outer_adj.children[1]
        assert inner_adj.label.startswith("ADJ")
        # The inner ADJ wraps the matalino lex entry — no further
        # children at the c-tree level since ADJ is preterminal.
        assert inner_adj.children == []


# === Comparative-ADJ as NP-internal modifier ============================


class TestComparativeNpModifier:
    """The wrapped comparative-ADJ rides into the Phase 5g NP-internal
    modifier rules unchanged: it's an ADJ, so ``N → ADJ PART[LINK] N``
    fires on it."""

    @pytest.mark.parametrize("sentence,verb_pred", [
        # Pre-N with bound -ng linker
        ("Kumain ang mas matalinong bata.",  "EAT"),
        # Pre-N with NA linker
        ("Tumakbo ang mas mabilis na kabayo.", "TAKBO"),
        # Pre-N with consonant-final stem + bound -ng linker
        ("Bumili ang mas mayamang lalaki.",  "BUY"),
    ])
    def test_pre_n_comparative_modifier(
        self, sentence: str, verb_pred: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got {len(parses)}"
        )
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED", "").startswith(verb_pred)

    def test_post_n_comparative_modifier(self) -> None:
        """Post-N modifier with linker: ``kabayo na mas mabilis``."""
        parses = parse_text("Tumakbo ang kabayo na mas mabilis.")
        assert len(parses) >= 1
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED", "").startswith("TAKBO")


# === Unification clash on already-degree-marked ADJs ===================


class TestComparativeUnificationClashes:
    """Wrapping an ADJ that already carries a different COMP_DEGREE
    fails unification — ``*mas pinakamaganda`` (more most beautiful)
    and ``*mas napakaganda`` (more very-beautiful) are
    ungrammatical."""

    @pytest.mark.parametrize("sentence", [
        # SUPERLATIVE — Phase 5h Commit 1 morphology
        "Mas pinakamaganda ang bahay.",
        "Mas pinakamatalino siya.",
        # INTENSIVE — Phase 5h Commit 1 morphology
        "Mas napakaganda ang bahay.",
        "Mas napakatalino siya.",
        # EQUATIVE — Phase 5h Commit 2 morphology
        "Mas kasingganda ang bahay.",
        "Mas singganda ang bahay.",
        # CONTRASTIVE — Phase 5h Commit 2 lex
        "Mas magkaiba ang aklat.",
    ])
    def test_double_degree_marking_rejected(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 0, (
            f"expected zero parses (unification clash) for {sentence!r}; "
            f"got {len(parses)}"
        )


# === Composition with negation =========================================


class TestComparativeWithNegation:
    """Negation composes with comparative — ``Hindi mas matalino
    siya.`` "She is not more intelligent" — via the (now-tightened)
    hindi-negation rule wrapping a comparative-ADJ S."""

    def test_hindi_plus_mas_predicative(self) -> None:
        parses = parse_text("Hindi mas matalino siya.")
        assert len(parses) == 1
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED") == "ADJ <SUBJ>"
        assert fstruct.feats.get("ADJ_LEMMA") == "talino"
        assert fstruct.feats.get("POLARITY") == "NEG"


# === Hindi-negation rule still fires on actual hindi ===================


class TestHindiNegationStillWorks:
    """The Phase 5h Commit 3 belt-and-braces ``(↓1 POLARITY) =c 'NEG'``
    constraint must NOT block the actual hindi-negation use. ``hindi``
    has ``POLARITY: NEG`` in its lex entry so the constraint is
    satisfied; this is a regression-protection test."""

    @pytest.mark.parametrize("sentence", [
        "Hindi maganda ang bata.",
        "Hindi matalino siya.",
        "Hindi mabilis ang kabayo.",
        "Hindi kumain ang bata.",
    ])
    def test_hindi_negates(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got {len(parses)}"
        )
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("POLARITY") == "NEG"


# === Hindi-negation leak closed: phantom NEG parses gone ===============


class TestNegationLeakClosed:
    """Pre-Phase-5h, the hindi-negation rule's category-pattern-only
    filter let any sentence-leading PART produce a phantom NEG-polarity
    parse. The Phase 5h Commit 3 belt-and-braces constraint closes
    this leak. These sentences had bogus POLARITY=NEG parses
    pre-fix and should now produce zero parses (since no other rule
    handles the sentence-leading PART in question)."""

    @pytest.mark.parametrize("sentence", [
        "Halos kumain ang bata.",
        "Tuwing kumain ang bata.",
    ])
    def test_no_phantom_neg_parse(self, sentence: str) -> None:
        parses = parse_text(sentence)
        # No phantom POLARITY=NEG. Either zero parses or any parse
        # that exists has POLARITY unset (i.e., not NEG).
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("POLARITY") != "NEG", (
                f"phantom NEG polarity for {sentence!r}; "
                f"feats={fs.feats}"
            )


# === Phase 5g/5h baselines preserved ===================================


class TestBaselinePreserved:
    """Phase 5g Commit 3 + Phase 5h Commit 1 / 2 surfaces continue to
    parse identically — the new wrapper rule and negation tightening
    don't perturb the existing morphology / grammar."""

    @pytest.mark.parametrize("sentence,adj_lemma", [
        # Phase 5g bare ma-
        ("Maganda ang bata.",      "ganda"),
        # Phase 5h Commit 1
        ("Pinakamaganda ang bahay.", "ganda"),
        ("Napakaganda ang bahay.",   "ganda"),
        # Phase 5h Commit 2
        ("Pareho ang aklat.",       "pareho"),
        ("Magkaiba ang aklat.",     "magkaiba"),
        ("Kasingganda ang bahay.",  "ganda"),
    ])
    def test_phase5g_5h_predicative_unchanged(
        self, sentence: str, adj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 1
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED") == "ADJ <SUBJ>"
        assert fstruct.feats.get("ADJ_LEMMA") == adj_lemma
        assert fstruct.feats.get("POLARITY") is None
