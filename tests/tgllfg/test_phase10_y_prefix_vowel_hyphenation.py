# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.Y: prefix-vowel-initial hyphenation regression tests.

Tagalog conventionally hyphenates a CC-final prefix (``mag-`` /
``nag-`` / ``pag-`` / ``maka-`` / ``naka-`` / ``paki-`` / …) against
a vowel-initial root: ``mag-aral`` / ``nag-uusap`` / ``pag-aaral`` /
``naka-upo`` / ``paki-abot``. Phase 10.Y aligns the engine with that
convention. The per-prefix-family policy lives in
:mod:`tgllfg.morph.prefix_policy`:

* ``mag`` / ``nag`` / ``pag`` / ``magpa`` / ``nagpa`` / ``magsi`` /
  ``nagsi`` / ``pakikipag``  — **hyphenated-only**: only the
  hyphenated surface key is indexed; legacy hyphenless input no
  longer resolves. This is the disambiguation lever for ``alit``
  "quarrel" (``mag-alit``) vs ``galit`` "anger" (``magalit`` =
  ``ma`` + ``galit`` ADJ-predicative).

* ``maka`` / ``naka`` / ``paki`` / ``paka`` / ``mapa`` / ``napa`` /
  ``makipag`` / ``nakipag`` / ``magka`` / ``nagka`` / ``pagka``  —
  **dual-keyed**: hyphenated canonical AND hyphen-stripped back-compat
  key, since references are mixed on this family's orthography
  (K91 prefers ``nakaupo``; S&O 1972 mixes both).

CV-final prefixes (``ma`` / ``na`` / ``pa`` / ``ka`` / ``i`` /
``si``) plain-concatenate as before — out of scope.

This test file establishes the regression sentinels:

* canonical engine output for every CC-prefix family × representative
  vowel-initial root pair;
* dual-key back-compat for the ``maka`` / ``naka`` / ``paki``
  family;
* tokenizer norm preserves the hyphen for CC-final cases and strips
  it for CV-final cases;
* collision sentry: ``nag-alit`` is OOV today (the ``alit`` VERB
  ships in 10.Y.C6 next commit); bare ``nagalit`` continues to
  resolve only to ``galit`` ADJ-predicative;
* multiword pre-pass hyphen-aware fallback (``Nagarte-arte`` triple
  merges to ``Nag-artearte`` via the post-10.Y join-with-hyphen
  variant in :func:`merge_hyphen_compounds`).
"""

import pytest

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import Analyzer
from tgllfg.morph.prefix_policy import (
    CC_FINAL_PREFIXES,
    DUAL_KEYED_PREFIXES,
    HYPHENATED_ONLY_PREFIXES,
    is_cc_final,
    is_dual_keyed,
    is_hyphenated_only,
    is_vowel_initial,
    should_hyphenate,
)
from tgllfg.text.multiword import merge_hyphen_compounds
from tgllfg.text.tokenizer import tokenize


@pytest.fixture(scope="module")
def analyzer() -> Analyzer:
    return Analyzer.from_default()


# === Policy module sanity =================================================


class TestPrefixPolicy:
    """The two prefix sets are disjoint, their union is CC_FINAL_PREFIXES,
    and the predicate helpers agree."""

    def test_families_are_disjoint(self) -> None:
        assert not (HYPHENATED_ONLY_PREFIXES & DUAL_KEYED_PREFIXES), (
            f"prefix-family sets overlap: "
            f"{HYPHENATED_ONLY_PREFIXES & DUAL_KEYED_PREFIXES}"
        )

    def test_union_is_cc_final(self) -> None:
        assert (
            HYPHENATED_ONLY_PREFIXES | DUAL_KEYED_PREFIXES
            == CC_FINAL_PREFIXES
        )

    @pytest.mark.parametrize("prefix", sorted(HYPHENATED_ONLY_PREFIXES))
    def test_hyphenated_only_is_cc_final(self, prefix: str) -> None:
        assert is_cc_final(prefix)
        assert is_hyphenated_only(prefix)
        assert not is_dual_keyed(prefix)

    @pytest.mark.parametrize("prefix", sorted(DUAL_KEYED_PREFIXES))
    def test_dual_keyed_is_cc_final(self, prefix: str) -> None:
        assert is_cc_final(prefix)
        assert is_dual_keyed(prefix)
        assert not is_hyphenated_only(prefix)

    @pytest.mark.parametrize(
        "prefix",
        ["ma", "na", "pa", "ka", "i", "si", "pinaka", "kasing"],
    )
    def test_cv_final_is_not_cc(self, prefix: str) -> None:
        assert not is_cc_final(prefix)

    def test_should_hyphenate_truth_table(self) -> None:
        # CC-final + vowel-init = hyphenate
        assert should_hyphenate("mag", "aral")
        assert should_hyphenate("naka", "upo")
        # CC-final + consonant-init = no hyphen
        assert not should_hyphenate("mag", "kain")
        # CV-final + vowel-init = no hyphen (out of scope)
        assert not should_hyphenate("ma", "init")
        assert not should_hyphenate("pa", "alagad")
        # Empty / non-prefix
        assert not should_hyphenate("", "aral")
        assert not should_hyphenate("xyz", "aral")

    @pytest.mark.parametrize(
        "base,expected",
        [
            ("aral", True),
            ("upo", True),
            ("Init", True),
            ("kain", False),
            ("g", False),
            ("", False),
        ],
    )
    def test_is_vowel_initial(self, base: str, expected: bool) -> None:
        assert is_vowel_initial(base) is expected


# === Canonical engine output ==============================================


class TestHyphenatedOnlyFamilyEmitsHyphen:
    """Phase 10.Y: the mag/nag/pag family emits the hyphenated form as
    the only canonical surface — no back-compat hyphenless key."""

    @pytest.mark.parametrize(
        "canonical,lemma,index_attr",
        [
            ("nag-aral",      "aral",   "verb_forms"),
            ("nag-aaral",     "aral",   "verb_forms"),
            ("mag-aaral",     "aral",   "verb_forms"),
            ("nag-uusap",     "usap",   "verb_forms"),
            ("mag-uusap",     "usap",   "verb_forms"),
            ("nag-isip",      "isip",   "verb_forms"),
            ("nag-iisip",     "isip",   "verb_forms"),
            ("nag-iyak",      "iyak",   "verb_forms"),
            ("nag-aalala",    "alaala", "verb_forms"),
            ("pag-aalaga",    "pag-aalaga", "nouns"),
        ],
    )
    def test_canonical_hyphenated_surface_indexed(
        self,
        analyzer: Analyzer,
        canonical: str,
        lemma: str,
        index_attr: str,
    ) -> None:
        idx = getattr(analyzer._index, index_attr)
        assert canonical in idx, f"{canonical!r} not in {index_attr}"

    @pytest.mark.parametrize(
        "hyphenless_surface,index_attr",
        [
            # mag/nag/pag family is hyphenated-only — these old keys gone
            ("nagaral",       "verb_forms"),
            ("nagaaral",      "verb_forms"),
            ("magaaral",      "verb_forms"),
            ("naguusap",      "verb_forms"),
            ("maguusap",      "verb_forms"),
            ("nagisip",       "verb_forms"),
            ("nagiyak",       "verb_forms"),
            ("nagaalala",     "verb_forms"),
        ],
    )
    def test_hyphenless_surface_is_oov(
        self,
        analyzer: Analyzer,
        hyphenless_surface: str,
        index_attr: str,
    ) -> None:
        # Phase 10.Y per-family policy: hyphenated-only family loses
        # the legacy hyphenless key. No back-compat.
        idx = getattr(analyzer._index, index_attr)
        # ``pagaalaga`` is the special case where the 9.X.c31 NOUN
        # citation hyphen-strip path keeps a hyphenless back-compat
        # alias even for the hyphenated-only family (citation-level
        # dual-keying, not paradigm-level). Excluded above. All other
        # paradigm-produced surfaces below must be absent.
        assert hyphenless_surface not in idx, (
            f"{hyphenless_surface!r} unexpectedly still in {index_attr}"
        )


class TestDualKeyedFamilyHasBothKeys:
    """Phase 10.Y: the maka/naka/paki family emits the hyphenated form
    as canonical AND keeps a hyphen-stripped back-compat key so
    legacy hyphenless input continues to resolve."""

    @pytest.mark.parametrize(
        "canonical,hyphenless",
        [
            ("naka-upo",   "nakaupo"),    # ADJ resultative
            ("naka-ilag",  "nakailag"),
            ("naka-amoy",  "nakaamoy"),
            ("naka-alis",  "nakaalis"),
            ("maka-akyat", "makaakyat"),
            ("maka-alis",  "makaalis"),
            ("paki-abot",  "pakiabot"),
        ],
    )
    def test_both_keys_present(
        self,
        analyzer: Analyzer,
        canonical: str,
        hyphenless: str,
    ) -> None:
        present_in = lambda s: any(  # noqa: E731
            s in idx
            for idx in (
                analyzer._index.verb_forms,
                analyzer._index.nouns,
                analyzer._index.adjectives,
            )
        )
        assert present_in(canonical), f"{canonical!r} (canonical) missing"
        assert present_in(hyphenless), f"{hyphenless!r} (back-compat) missing"


class TestCvPrefixUnchanged:
    """CV-final prefixes (ma/na/pa/ka/i/si) are out of scope — surfaces
    plain-concatenate as before."""

    @pytest.mark.parametrize(
        "surface,index_attr",
        [
            ("mainit",   "adjectives"),   # ma + init
            ("maganda",  "adjectives"),   # ma + ganda (consonant root anyway)
            ("masaya",   "adjectives"),
            ("paaralan", "nouns"),        # pa + aralan
        ],
    )
    def test_cv_prefix_hyphenless_still_indexed(
        self,
        analyzer: Analyzer,
        surface: str,
        index_attr: str,
    ) -> None:
        idx = getattr(analyzer._index, index_attr)
        assert surface in idx, (
            f"CV-prefix surface {surface!r} should still index"
        )


# === Tokenizer norm behavior =============================================


class TestTokenizerHyphenInNorm:
    """Phase 10.Y: tokenizer preserves the internal hyphen in ``norm``
    for CC-final-prefix + vowel-initial-stem tokens; CV-final-prefix
    and compound tokens strip as before."""

    @pytest.mark.parametrize(
        "text,expected_norm",
        [
            # CC-final + vowel-init: hyphen preserved
            ("mag-aral",       "mag-aral"),
            ("Nag-uusap",      "nag-uusap"),
            ("pag-aaral",      "pag-aaral"),
            ("naka-upo",       "naka-upo"),
            ("paki-abot",      "paki-abot"),
            ("makipag-usap",   "makipag-usap"),
            ("pakikipag-usap", "pakikipag-usap"),
        ],
    )
    def test_cc_final_norm_preserves_hyphen(
        self, text: str, expected_norm: str,
    ) -> None:
        toks = tokenize(text)
        assert len(toks) == 1
        assert toks[0].norm == expected_norm

    @pytest.mark.parametrize(
        "text,expected_norm",
        [
            # CV-final + vowel-init: hyphen stripped (legacy)
            ("ma-aga",         "maaga"),
        ],
    )
    def test_cv_final_norm_strips_hyphen(
        self, text: str, expected_norm: str,
    ) -> None:
        toks = tokenize(text)
        assert len(toks) == 1
        assert toks[0].norm == expected_norm


# === Multiword pre-pass hyphen-aware fallback ===========================


class TestMultiwordHyphenAwareMerge:
    """Phase 10.Y: ``merge_hyphen_compounds`` now tries a hyphen-inserted
    variant when the bare ``x + y`` join doesn't hit the analyzer
    index. Closes the ``Nagarte-arte`` (and similar
    inflected-moderative) paths whose canonical index key flipped
    from hyphenless ``nagartearte`` to hyphenated ``nag-artearte``."""

    def test_nagarte_arte_merges_via_hyphen_variant(self) -> None:
        toks = tokenize("Nagarte-arte siya.")
        merged = merge_hyphen_compounds(toks)
        # The first 3 tokens (Nagarte, -, arte) should fold into one.
        assert merged[0].norm == "nag-artearte"
        assert merged[0].surface == "Nag-artearte"


# === Collision sentry (pre-C6) ==========================================


class TestAlitGalitDisambiguation:
    """Post-C6: ``mag-alit`` / ``nag-alit`` resolve to the new ``alit``
    VERB (mag-class symmetric "quarrel"); bare ``nagalit`` continues
    to resolve only to ``galit`` AV-NVOL "got angry" — no collision.
    The 10.Y per-family policy makes this work: ``mag``/``nag``/``pag``
    are hyphenated-only, so ``alit`` (hyphenated key) and ``galit``
    (hyphenless key) never share a lookup slot."""

    def test_mag_alit_resolves_to_alit_verb(
        self, analyzer: Analyzer,
    ) -> None:
        assert analyzer.is_known_surface("mag-alit")
        verbs = analyzer._index.verb_forms.get("mag-alit", [])
        lemmas = {a.lemma.lower() for a in verbs}
        assert "alit" in lemmas
        assert "galit" not in lemmas

    def test_nag_alit_resolves_to_alit_verb(
        self, analyzer: Analyzer,
    ) -> None:
        assert analyzer.is_known_surface("nag-alit")
        verbs = analyzer._index.verb_forms.get("nag-alit", [])
        lemmas = {a.lemma.lower() for a in verbs}
        assert "alit" in lemmas
        assert "galit" not in lemmas

    def test_nagalit_resolves_to_galit(
        self, analyzer: Analyzer,
    ) -> None:
        """``nagalit`` (hyphenless) — the ``na`` + ``galit`` VERB-
        AV-PFV-NVOL of ``galit`` — must continue to resolve to
        ``galit``, not to any ``alit`` VERB analysis. The ADJ
        predicative is ``magalit`` (``ma`` + ``galit``); both
        live under ``galit``. Adding ``alit`` as a VERB in C6 must
        NOT pollute ``nagalit`` (10.E.6 deferral motivation)."""
        # ``na`` is a CV-final prefix → no hyphen on ``na + galit``.
        # ``nagalit`` indexes in verb_forms (NVOL of galit ma-class).
        assert "nagalit" in analyzer._index.verb_forms
        verbs = analyzer._index.verb_forms["nagalit"]
        lemmas = {a.lemma.lower() for a in verbs}
        assert "galit" in lemmas
        assert "alit" not in lemmas, (
            f"``nagalit`` must NOT analyze to ``alit`` (pre-C6 sentry); "
            f"lemmas: {lemmas}"
        )
        # The ADJ predicative ``magalit`` (= ``ma`` + ``galit``)
        # also resolves only to ``galit``.
        assert "magalit" in analyzer._index.adjectives
        adjs = analyzer._index.adjectives["magalit"]
        adj_lemmas = {a.lemma.lower() for a in adjs}
        assert "galit" in adj_lemmas
        assert "alit" not in adj_lemmas


# === End-to-end parse smoke ============================================


class TestEndToEndParse:
    """The new canonical hyphenated surfaces parse end-to-end."""

    @pytest.mark.parametrize(
        "sent",
        [
            # mag-/nag-/pag- + vowel-init: hyphenated-only family
            "Nag-aaral si Maria ng wika.",  # nag-AV-IPFV with OBJ
            "Nag-aaral siya ng wika.",      # nag-AV-IPFV pronoun pivot
            "Mag-aaral siya ng wika.",      # mag-AV-CTPL with OBJ
            # naka- + vowel-init: dual-keyed family
            "Nakaupo si Pedro.",            # naka- (hyphenless input ok)
            "Naka-upo si Pedro.",           # naka- (hyphenated input)
            # mag-isa ADV: post-10.Y lex (canonical hyphenated key)
            "Nakatira siyang mag-isa.",
        ],
    )
    def test_canonical_sentence_parses(self, sent: str) -> None:
        parses = parse_text(sent, n_best=1)
        assert len(parses) >= 1, f"should parse: {sent!r}"
