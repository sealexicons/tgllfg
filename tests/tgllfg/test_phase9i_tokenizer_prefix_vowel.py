# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 9.I: tokenizer rejoin of Tagalog-prefix-vowelStem hyphenated forms.

The plan §B1.I scoped "Reduplicated/derived forms — ``aaral``
(CTPL of mag-aral), ``uusap`` (CTPL of mag-usap), nag- prefixed
missing roots". Investigation revealed these audit OOV surfaces
are tokenization artifacts: the audit corpus writes the
canonical hyphenated forms ``Nag-uusap`` / ``pag-aaral`` /
``Mag-aral``, but the raw tokenizer splits on internal hyphens
into three tokens (``Nag``, ``-``, ``uusap``), and the
post-hyphen reduplicated stem ``uusap`` / ``aaral`` is not
itself analyzable (only the de-hyphenated joined form
``naguusap`` / ``magaral`` is, via the existing mag-paradigm
cells).

Fix: extend the tokenizer regex to rejoin ``prefix-vowelStem``
patterns when the prefix is in a closed Tagalog inflection /
derivation list (``mag``, ``nag``, ``pag``, ``maka``, ``naka``,
``mapa``, ``napa``, ``paka``, ``paki``, ``magpa``, ``nagpa``,
``magsi``, ``nagsi``, ``makipag``, ``nakipag``, ``pakikipag``,
``mang``, ``nang``, ``pang``, ``mag`` / ``nag`` / ``pag``,
``ka``, ``na``, ``pa``, ``ma``). The matched token's ``norm``
strips the internal hyphen so the analyzer's surface index
(keyed on hyphen-free forms) finds it.

Compound nouns (``tabing-dagat``, ``well-known``) and
non-verbal hyphenated forms (``kasing-bilis``,
``humigit-kumulang``, ``daan-daan``, ``tag-init``) intentionally
stay split — they're handled by the existing
``merge_hyphen_compounds`` pre-pass (``src/tgllfg/text/multiword.py``).

The fix unblocks the surface layer; many of these forms still
fail to parse due to other pre-existing grammar gaps (TR-without-
OBJ for ``Mag-aral ka.``, ``Nag-uusap ang dalaga.``; missing
``pag-`` nominalization paradigm cell for ``pag-aaral``). Those
are deferred to 9.O / construction class.
"""

import pytest

from tgllfg.text.tokenizer import tokenize


# ---- Tokenizer rejoin behavior -----------------------------------

class TestTokenizerPrefixVowelRejoin:

    @pytest.mark.parametrize("text,expected_surface,expected_norm", [
        # mag- / nag- / pag- + vowel-initial stem
        ("Nag-uusap",     "Nag-uusap",     "naguusap"),
        ("nag-uusap",     "nag-uusap",     "naguusap"),
        ("pag-aaral",     "pag-aaral",     "pagaaral"),
        ("mag-aral",      "mag-aral",      "magaral"),
        ("mag-isa",       "mag-isa",       "magisa"),
        # Longest-first: pakikipag before pag
        ("pakikipag-usap", "pakikipag-usap", "pakikipagusap"),
        # Other Tagalog prefixes (vowel-initial stems only)
        ("paki-abot",     "paki-abot",     "pakiabot"),
        ("ma-aga",        "ma-aga",        "maaga"),
    ])
    def test_rejoin_when_vowel_initial_stem(
        self, text: str, expected_surface: str, expected_norm: str,
    ) -> None:
        toks = tokenize(text)
        assert len(toks) == 1, (
            f"{text!r}: expected single token, got "
            f"{[t.surface for t in toks]}"
        )
        assert toks[0].surface == expected_surface
        assert toks[0].norm == expected_norm


class TestTokenizerStaysSplit:
    """Compound nouns / non-verbal hyphen forms still split into
    3 tokens — handled by the merge_hyphen_compounds pre-pass."""

    @pytest.mark.parametrize("text,expected_count", [
        ("tabing-dagat", 3),       # consonant-stem; tabi-linker decomp downstream
        ("kasing-bilis", 3),       # equative prefix + consonant-stem
        ("daan-daan", 3),          # distributive; pre-pass handles
        ("tag-init", 3),           # tag-season; pre-pass handles
        ("humigit-kumulang", 3),   # approximator; pre-pass handles
        ("well-known", 3),         # English compound; harmless
    ])
    def test_consonant_stem_stays_split(
        self, text: str, expected_count: int,
    ) -> None:
        toks = tokenize(text)
        assert len(toks) == expected_count, (
            f"{text!r}: expected {expected_count} tokens, got "
            f"{[t.surface for t in toks]}"
        )


class TestTokenizerEdgeCases:

    def test_bare_hyphen_kept_as_hyphen_norm(self) -> None:
        """A standalone ``-`` token's norm is ``-`` (not empty
        string). Phase 9.I bug fix: an empty norm caused
        ``Kamag-anak siya ng mga Santos.`` to falsely parse as
        ``anak siya ng mga Santos.`` (the empty-norm token was
        silently dropped by the parser)."""
        toks = tokenize("Foo - bar")
        assert len(toks) == 3
        assert toks[1].surface == "-"
        assert toks[1].norm == "-"

    def test_arithmetic_minus_preserved(self) -> None:
        """``10 - 4 = 6.`` should tokenize digits and operators
        as separate tokens — no hyphen-join."""
        toks = tokenize("10 - 4 = 6.")
        norms = [t.norm for t in toks]
        assert norms == ["10", "-", "4", "=", "6", "."]

    def test_kamag_anak_does_not_collapse(self) -> None:
        """``Kamag-anak`` is NOT a Tagalog-prefix-vowelStem
        pattern — ``Kamag`` is not in the prefix list, and stem
        ``anak`` is preceded by ``g`` not by the hyphen. Stays
        split; remains OOV per Phase 9.B deferral pin."""
        toks = tokenize("Kamag-anak siya.")
        # 3 word/punct tokens for `Kamag` `-` `anak`, plus `siya` `.`
        assert [t.surface for t in toks[:3]] == ["Kamag", "-", "anak"]


# ---- Audit-corpus parse smoke ------------------------------------

class TestAuditCorpusReachability:
    """The tokenizer fix is necessary but not sufficient: many of
    these audit sentences also need grammar rules (TR-without-OBJ
    consumption, pag-nominalization paradigm) that are deferred
    to 9.O. The pinning here documents the unblocked-at-tokenizer
    level."""

    @pytest.mark.parametrize("text,surface,norm", [
        ("Nag-uusap ang dalaga.",       "Nag-uusap", "naguusap"),
        ("Ang pag-aaral ng wika.",      "pag-aaral", "pagaaral"),
        ("Mag-aral ka.",                "Mag-aral",  "magaral"),
    ])
    def test_audit_form_tokenizes_correctly(
        self, text: str, surface: str, norm: str,
    ) -> None:
        toks = tokenize(text)
        # Find the target token
        matches = [t for t in toks if t.surface == surface]
        assert matches, (
            f"expected token with surface {surface!r} in tokenization of "
            f"{text!r}; got {[t.surface for t in toks]}"
        )
        assert matches[0].norm == norm


# ---- No-regression ----------------------------------------------

class TestNoRegression:
    """Pre-existing parses still work after tokenizer change."""

    @pytest.mark.parametrize("sentence", [
        "Pumunta sila dito.",
        "Maganda si Maria.",
        "Sumulat siya.",
        "Mabuti ang aklat.",
        "Nagluto siya ng gulay.",  # mag-AV-PFV (TR with OBJ)
    ])
    def test_existing_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"regression: {sentence!r}"
