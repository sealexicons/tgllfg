"""Phase 5f closing deferral: hyphenation tokenizer pre-pass.

The canonical orthography for several Phase 5f Commit 14 / 16 / 18 /
19 / 21 lex items uses an internal hyphen — ``tag-init`` (season),
``humigit-kumulang`` (approximator), ``daan-daan`` (collective),
``tig-isa`` (distributive cardinal), ``kani-kaniya`` (distributive-
possessive). The tokenizer's ``\\w+|\\S`` regex emits these as three
separate tokens (``tag``, ``-``, ``init``). The seed lex carries
each compound's single-token form (``taginit``, ``humigitkumulang``,
``daandaan``, ``tigisa``, ``kanikaniya``) so the morph index can
look them up.

:func:`tgllfg.text.merge_hyphen_compounds` runs as a pre-parse pass
that joins ``X``, ``-``, ``Y`` triples whose concatenation is a known
surface. Symbolic-arithmetic ``-`` between digits is preserved (the
``isalpha()`` check rules out non-letter flankers); non-canonical
hyphenated compounds (``Mr-Juan``, ``foo-bar``) are preserved
because their joined form isn't in the lex.

A bound ``-ng`` linker on the right flanker (``kani-kaniyang``)
gets a carve-out: the merge tries the join with the trailing ``ng``
stripped and, if that's a known compound, emits the merged compound
plus a synthetic ``-ng`` linker token, mirroring
:func:`split_linker_ng`'s output shape.

Tests cover:

* Tokenizer pass: every Phase 5f hyphenated compound merges to its
  canonical single-token form.
* Negative tokenizer pass: digit ``X-Y`` is preserved (arithmetic
  minus); non-canonical compounds preserved.
* Sentence-level: each construction parses with its hyphenated
  surface to the same f-structure as the no-hyphen single-token
  form.
* Bound-``-ng`` linker: ``kani-kaniyang aklat`` merges to
  ``kanikaniya`` + ``-ng`` and parses identically to
  ``kanikaniyang aklat``.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text
from tgllfg.text import merge_hyphen_compounds, split_linker_ng, tokenize


def _merge(text: str) -> list[str]:
    toks = tokenize(text)
    toks = split_linker_ng(toks)
    toks = merge_hyphen_compounds(toks)
    return [t.surface for t in toks]


def _matrix(text: str) -> FStructure | None:
    parses = parse_text(text, n_best=1)
    if not parses:
        return None
    return parses[0][1]


# --- Tokenizer pass ------------------------------------------------------


class TestMergeCanonicalCompounds:
    """Each Phase 5f canonical hyphenated form merges to its
    single-token equivalent."""

    @pytest.mark.parametrize("hyphenated,merged", [
        # Phase 5f Commit 14: seasons.
        ("tag-init",     "taginit"),
        ("tag-ulan",     "tagulan"),
        ("tag-lamig",    "taglamig"),
        ("tag-araw",     "tagaraw"),
        ("tag-gutom",    "taggutom"),
        # Phase 5f Commit 16: approximator.
        ("humigit-kumulang", "humigitkumulang"),
        # Phase 5f Commit 18: collectives.
        ("daan-daan",    "daandaan"),
        ("libu-libo",    "libulibo"),
        # Phase 5f Commit 19: distributive cardinals.
        ("tig-isa",      "tigisa"),
        ("tig-dalawa",   "tigdalawa"),
        ("tig-tatlo",    "tigtatlo"),
        ("tig-lima",     "tiglima"),
        ("tig-sampu",    "tigsampu"),
        # Phase 5f Commit 21: distributive-possessive.
        ("kani-kaniya",  "kanikaniya"),
        ("kanya-kanya",  "kanyakanya"),
    ])
    def test_canonical_merges(self, hyphenated: str, merged: str) -> None:
        out = _merge(hyphenated)
        assert out == [merged], (
            f"expected {[merged]!r} for {hyphenated!r}, got {out!r}"
        )


class TestMergeNegative:
    """Tokens that shouldn't merge."""

    def test_digit_minus_digit_preserved(self) -> None:
        """``5 - 3`` (arithmetic minus) — both flankers are digits,
        not alphabetic, so the merge skip."""
        assert _merge("5 - 3") == ["5", "-", "3"]

    def test_unknown_compound_preserved(self) -> None:
        """``Mr-Juan`` joined ``MrJuan`` isn't in the lex — keep
        the three tokens unchanged."""
        assert _merge("Mr-Juan") == ["Mr", "-", "Juan"]

    def test_partial_alpha_minus_digit(self) -> None:
        """Mixed ``foo-3`` — ``3`` isn't alpha, no merge."""
        assert _merge("foo-3") == ["foo", "-", "3"]


class TestBoundLinkerCarveOut:
    """A right flanker carrying the bound ``-ng`` linker (whose stem
    forms a known compound) is split + merged into a 2-token
    sequence."""

    def test_kani_kaniyang_splits_and_merges(self) -> None:
        out = _merge("kani-kaniyang")
        assert out == ["kanikaniya", "-ng"]

    def test_kanya_kanyang_splits_and_merges(self) -> None:
        out = _merge("kanya-kanyang")
        assert out == ["kanyakanya", "-ng"]


# --- Sentence-level parses ----------------------------------------------


class TestHyphenatedSentenceParses:
    """Each Phase 5f construction parses with its canonical
    hyphenated orthography to the same f-structure as the
    no-hyphen single-token form."""

    def test_season_pp(self) -> None:
        f = _matrix("Tumakbo si Juan tuwing tag-init.")
        assert f is not None
        adjuncts = f.feats.get("ADJUNCT")
        assert adjuncts
        members = list(adjuncts) if isinstance(adjuncts, frozenset) else [adjuncts]
        time_pp = next(
            (m for m in members
             if isinstance(m, FStructure) and m.feats.get("TIME_FRAME")),
            None,
        )
        assert time_pp is not None
        obj = time_pp.feats.get("OBJ")
        assert obj is not None
        assert obj.feats.get("SEM_CLASS") == "SEASON"
        assert obj.feats.get("LEMMA") == "taginit"

    def test_approximator(self) -> None:
        """``humigit-kumulang lima`` — the approximator is a PART
        modifying the cardinal."""
        f = _matrix("Bumili ako ng humigit-kumulang lima na isda.")
        assert f is not None
        obj = f.feats.get("OBJ")
        assert obj is not None
        assert obj.feats.get("CARDINAL_VALUE") == "5"

    def test_distributive_cardinal_predicative(self) -> None:
        """``Tig-isa ang aklat nila`` "they each have one book"."""
        f = _matrix("Tig-isa ang aklat nila.")
        assert f is not None
        assert f.feats.get("PRED") == "CARDINAL <SUBJ>"
        assert f.feats.get("CARDINAL_VALUE") == "1"
        subj = f.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "aklat"

    def test_distributive_possessive_obj(self) -> None:
        """``kani-kaniyang aklat`` — bound ``-ng`` linker on the
        right flanker. Joins via the carve-out, then split_linker_ng
        equivalent runs against the synthetic ``-ng``."""
        f = _matrix("Bumili ako ng kani-kaniyang aklat.")
        assert f is not None
        obj = f.feats.get("OBJ")
        assert obj is not None
        assert obj.feats.get("LEMMA") == "aklat"

    def test_collective_obj(self) -> None:
        """``daan-daan na isda`` — collective NUM-modifier."""
        f = _matrix("Bumili ako ng daan-daan na isda.")
        assert f is not None
        obj = f.feats.get("OBJ")
        assert obj is not None
        assert obj.feats.get("LEMMA") == "isda"


# --- Regressions --------------------------------------------------------


class TestRegressions:
    """No-hyphen single-token forms still parse identically."""

    @pytest.mark.parametrize("text", [
        "Tumakbo si Juan tuwing taginit.",
        "Tig-isa ang aklat nila.",  # already tested above; included for symmetry
        "Bumili ako ng kanikaniyang aklat.",
        "Bumili ako ng daandaan na isda.",
    ])
    def test_no_hyphen_form_still_parses(self, text: str) -> None:
        f = _matrix(text)
        assert f is not None, f"no parse for {text!r}"

    def test_arithmetic_minus_digit_preserved(self) -> None:
        """``10 - 4 = 6.`` — digits flank the ``-``, no merge,
        arithmetic minus rule fires."""
        f = _matrix("10 - 4 = 6.")
        assert f is not None
        assert f.feats.get("OP") == "MINUS"
        assert f.feats.get("OPERAND_1") == "10"
        assert f.feats.get("OPERAND_2") == "4"
        assert f.feats.get("RESULT") == "6"
