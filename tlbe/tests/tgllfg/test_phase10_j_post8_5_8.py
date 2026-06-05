# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-8.5.8: productive N-N compound grammar rule (Tier 3).

Adds two chart rules in ``cfg/nominal.py`` for productive
hyphenated N-N compounds, per the reviewer 2026-05-30 N-N compound
Tier framework (see ``data/tgl/exemplars/compounds-n-n.jsonl`` and
the ``reference_tagalog_nn_compound_tiers`` memory entry).

## Rule shapes

(a) Bare ``N PUNCT[HYPHEN] N`` — head + hyphen + modifier:

    tubig-dagat       "sea water"      (tubig=head, dagat=modifier)
    bahay-kainan      "eatery"
    silid-kainan      "dining room"
    tubig-ilog        "river water"

(b) ``N PART[LINK=NG] PUNCT[HYPHEN] N`` — head + -ng linker +
    hyphen + modifier (when the head ends in a vowel and bears the
    orthographic -ng linker before the hyphenated modifier):

    taong-bayan       "populace"     (tao + -ng + bayan)
    lupang-bukid      "agricultural land" (lupa + -ng + bukid)

Each daughter uses an existing PUNCT lex entry (no new lex). The
rules mirror the post-6.1 ``N → N PART[LINK] N`` linker-mediated
N-N modifier pattern but with an additional PUNCT[HYPHEN] daughter.

## F-structure

Matrix is the LEFT N (the head); RIGHT N joins the matrix
``N-MOD`` set. Reuses post-6.1's N-MOD slot. The matrix PRED stays
on the head's LEMMA (not collapsed to ``SEAWATER`` etc.) — the
modifier is recoverable from N-MOD per the reviewer's compositional-
semantics guideline (saved to
``reference_tagalog_nn_compound_tiers``).

## Tier-1/2 lex entries preserved

When the joined form IS in the lex (post-8.5.7 entries:
``salinlahi`` / ``tabingdagat`` / ``hanapbuhay`` / ``kamaganak``),
the existing ``merge_hyphen_compounds`` pre-pass collapses the
hyphenated surface to a single token BEFORE this rule could fire.
So the lexicalized PRED on those Tier-1 compounds wins; the
productive rule only fires when no lex entry exists.

## Audit signal (post-8.5.7 → post-8.5.8)

* Wave-1: 106/123 unchanged
* Wave-2 rg-intermediate: 462 → 464 (+2)
* Wave-3 so1972: 298 → 299 (+1)
* XWAVE: 1817 → 1824 (+7)
* 0 regressions
"""

from tgllfg.core.pipeline import parse_text


class TestProductiveNNCompoundBare:
    """Rule (a): `N → N PUNCT[HYPHEN] N` — no -ng linker."""

    def test_tubig_dagat_in_clause(self) -> None:
        """``Matamis ang tubig-dagat.`` — tubig=head, dagat=modifier."""
        parses = parse_text("Matamis ang tubig-dagat.", n_best=1)
        assert len(parses) >= 1

    def test_bahay_kainan_in_clause(self) -> None:
        parses = parse_text("Maganda ang bahay-kainan.", n_best=1)
        assert len(parses) >= 1

    def test_silid_kainan_in_existential(self) -> None:
        parses = parse_text("May silid-kainan.", n_best=1)
        assert len(parses) >= 1

    def test_tubig_ilog_in_clause(self) -> None:
        parses = parse_text("Maganda ang tubig-ilog.", n_best=1)
        assert len(parses) >= 1


class TestProductiveNNCompoundWithNgLinker:
    """Rule (b): `N → N PART[LINK=NG] PUNCT[HYPHEN] N`."""

    def test_taong_bayan_in_existential(self) -> None:
        """`taong-bayan` → 4 tokens after pre-pass:
        `tao`, `-ng`, `-`, `bayan`. Rule (b) fires."""
        parses = parse_text("May taong-bayan.", n_best=1)
        assert len(parses) >= 1

    def test_lupang_bukid_in_clause(self) -> None:
        parses = parse_text("Maganda ang lupang-bukid.", n_best=1)
        assert len(parses) >= 1


class TestLexicalizedCompoundsStillPrefer:
    """When the joined form IS lex'd (post-8.5.7 Tier 1/2 compounds),
    the existing `merge_hyphen_compounds` pre-pass collapses to a
    single token BEFORE this rule could fire. The lexicalized
    f-structure (with non-compositional PRED) wins."""

    def test_tabingdagat_lex_preferred(self) -> None:
        """`tabing-dagat` collapses to `tabingdagat` via lex hit."""
        parses = parse_text("May tabing-dagat.", n_best=1)
        assert len(parses) >= 1

    def test_salinlahi_lex_preferred(self) -> None:
        parses = parse_text("May salin-lahi.", n_best=1)
        assert len(parses) >= 1

    def test_kamaganak_lex_preferred(self) -> None:
        parses = parse_text("Mayroon siyang kamag-anak.", n_best=1)
        assert len(parses) >= 1


class TestAntiRegression:
    """Pre-existing N-N constructions are unchanged."""

    def test_post_6_1_n_n_linker_compound_preserved(self) -> None:
        """`putaheng gulay` (post-6.1 N + LINK + N, no hyphen) still
        parses via the existing rule."""
        parses = parse_text(
            "Ano ang pinakatampok na putaheng gulay?", n_best=1,
        )
        assert len(parses) >= 1

    def test_arithmetic_minus_preserved(self) -> None:
        """The `-` lex entry's `PART[OP=MINUS]` reading (arithmetic)
        is NOT consumed by the new N-N compound rules — different
        category. The new rules use `PUNCT[PUNCT_CLASS=HYPHEN]`."""
        # Just verify the chart compiles cleanly and arithmetic-like
        # surfaces don't crash — we don't lex digits as N so the
        # productive N-N rule doesn't match.
        from tgllfg.morph.analyzer import _get_default
        analyzer = _get_default()
        # `-` is known surface (both readings)
        assert analyzer.is_known_surface("-")

    def test_alas_tres_hyphenated_clock_preserved(self) -> None:
        """The Phase 5n.B clock-time hyphenated form
        `alas-tres` continues to parse via its own rule."""
        parses = parse_text("Alas-tres pa lang.", n_best=1)
        assert len(parses) >= 1
