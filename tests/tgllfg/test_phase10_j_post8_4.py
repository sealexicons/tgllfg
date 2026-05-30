# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-8.4: apostrophe-clitic pre-pass extensions.

Fourth implementation sub-PR in the post-8.[1-5] arc.

Survey misdiagnosis correction (third in this arc, fourth counting
post-7.7 misclassifications): the post-8 survey claimed the
``'y`` / ``'t`` apostrophe-clitic handling was missing entirely
and should be added at the tokenizer level. In fact the dedicated
pipeline pre-passes ``split_apostrophe_t`` (Phase 5k Commit 2)
and ``split_apostrophe_y`` (Phase 9.X.c4) already exist in
``src/tgllfg/text/clitics.py`` and are already wired in. The
``split_apostrophe_t`` pre-pass also has a Phase 9.X.c6 collapse
that handles ``sapagka't`` → ``sapagkat`` via a known-surface
lookup on ``<host>t``.

The actual gaps were narrower:

* ``hangga't`` (= ``hanggang`` "until/as long as") — Phase 9.X.c6
  only checked ``<host>t`` for the lookup-collapse. The canonical
  form for ``hangga't`` is ``hanggang`` (``-ng`` restore), not
  ``hangga + at`` (which would mean "as long as AND" — semantic
  nonsense). post-8.4 adds a small ``_T_NG_VARIANTS`` registry to
  ``split_apostrophe_t`` for this orthographic-variant family.
  The registry is intentionally explicit (single entry) rather
  than a generic ``<host>ng`` lookup — the unrestricted lookup
  would mis-collapse ``na't`` → ``nang`` (the desired reading is
  ``na + at``).
* ``Kadalasa'y`` / ``minsa'y`` / ``Karaniwa'y`` — the fixed
  adverbs ``kadalasan`` / ``minsan`` / ``karaniwan`` drop their
  final ``-n`` before the ``'y`` clitic, then ``split_apostrophe_y``
  saw ``[Kadalasa, ', y]`` and emitted ``[Kadalasa, ay]``. The
  bare ``Kadalasa`` is ``_UNK``. post-8.4 extends
  ``split_apostrophe_y`` with the analog of the c6 collapse: a
  known-surface lookup on ``<host>n`` that fires only when the
  bare ``<host>`` is unknown. Gates on bare-host-unknown so the
  productive vowel-final cases (``pamilya'y``, ``ito'y``) still
  split cleanly.

Wave-1 closure: PAG-AARAL/sent-6 (``Hindi sila magsasalita
hangga't sa palagay nila ay tamang-tama na ang sasabihin nila.``)
— first wave-1 close attributable to ``hangga't`` → ``hanggang``.

Anti-regression scope:

* The Phase 5k Commit 2 vowel-final-host gate is unchanged
  (``apat't kalahati`` consonant-final NUM-coord still keeps the
  separate ``'/t`` tokens; the cardinal-coord chart handles those
  downstream).
* Phase 9.X.c4 ``rito'y`` / ``Mangyari'y`` / vowel-final-host
  pass-through unchanged.
* Phase 9.X.c6 ``sapagka't`` / ``Kahi't`` known-``<host>t``
  collapse unchanged (``Kahi`` → ``Kahit`` because ``Kahit`` is a
  known surface, NOT because of ``_T_NG_VARIANTS``).
* ``na't`` → ``na at`` (default split, NOT ``nang``). The
  productive ``<host> + at`` reading is preserved.
"""

import pytest

from tgllfg.core.pipeline import parse_text
from tgllfg.morph import analyze_tokens
from tgllfg.text import (
    split_apostrophe_t,
    split_apostrophe_y,
    tokenize,
)


def _pipeline(text: str) -> list[str]:
    """Apply the apostrophe-clitic pre-passes; return token surfaces."""
    toks = tokenize(text)
    toks = split_apostrophe_t(toks)
    toks = split_apostrophe_y(toks)
    return [t.surface for t in toks]


# === T-side collapses ====================================================


class TestApostropheTNgRestore:
    """post-8.4: ``hangga't`` collapses to ``hanggang`` via
    ``_T_NG_VARIANTS`` registry."""

    def test_hangga_t_collapses_to_hanggang(self) -> None:
        """``hangga't`` → single ``hanggang`` token (PART
        "until/as long as")."""
        out = _pipeline("hangga't")
        assert out == ["hanggang"]

    def test_hangga_t_in_clause(self) -> None:
        """``hangga't`` mid-clause preserves the canonical
        ``hanggang`` reading."""
        out = _pipeline("hangga't sa palagay nila")
        assert out == ["hanggang", "sa", "palagay", "nila"]

    def test_hangga_t_case_preserved(self) -> None:
        """Capital-H preserved: ``Hangga't`` → ``Hanggang``."""
        out = _pipeline("Hangga't ngayon")
        assert out[0] == "Hanggang"


class TestApostropheTExistingCollapse:
    """post-8.4 anti-regression: Phase 9.X.c6 known-``<host>t``
    collapse continues to work."""

    def test_sapagka_t_collapses(self) -> None:
        """``sapagka't`` → ``sapagkat`` (single PART, c6 path)."""
        out = _pipeline("sapagka't")
        assert out == ["sapagkat"]

    def test_kahi_t_collapses(self) -> None:
        """``Kahi't`` → ``Kahit`` (single PART, c6 path)."""
        out = _pipeline("Kahi't")
        assert out == ["Kahit"]


class TestApostropheTDefaultSplit:
    """post-8.4 anti-regression: the productive ``<host> + at``
    split must remain the default (not get hijacked by the new
    ``_T_NG_VARIANTS`` lookup)."""

    def test_na_t_splits_default(self) -> None:
        """``na't`` → ``na`` + ``at`` (NOT ``nang``). ``nang`` is
        lex'd as a separate particle; the apostrophe-t spelling
        must NOT collapse via an unrestricted ``<host>ng`` lookup."""
        out = _pipeline("na't")
        assert out == ["na", "at"]

    def test_lalo_na_t_splits(self) -> None:
        """``lalo na't`` → ``lalo`` + ``na`` + ``at`` (the ``na``
        gets default-split as in :meth:`test_na_t_splits_default`)."""
        out = _pipeline("lalo na't")
        assert out == ["lalo", "na", "at"]

    def test_maria_t_juan_splits(self) -> None:
        """``Maria't Juan`` → ``Maria`` + ``at`` + ``Juan`` (the
        Phase 5k Commit 2 baseline case; ``Mariat`` is not a known
        surface so the c6 collapse doesn't fire)."""
        out = _pipeline("Maria't Juan")
        assert out == ["Maria", "at", "Juan"]


class TestApostropheTConsonantFinalGate:
    """post-8.4 anti-regression: the Phase 5k vowel-final-host gate
    is unchanged. NUM-coord ``apat 't kalahati`` keeps the bare
    apostrophe / t tokens (the cardinal-coord chart handles them
    downstream)."""

    @pytest.mark.parametrize("host", ["apat", "anim", "pitong"])
    def test_consonant_final_host_unaffected(self, host: str) -> None:
        """The apostrophe + t pair remains as separate tokens for
        consonant-final hosts (no collapse, no split)."""
        out = _pipeline(f"{host} 't kalahati")
        assert "'" in out
        assert out[-2:] == ["t", "kalahati"]


# === Y-side restores =====================================================


class TestApostropheYNRestore:
    """post-8.4: ``Kadalasa'y`` / ``minsa'y`` / ``Karaniwa'y``
    restore the truncated ``-n`` so the analyzer reaches the
    canonical adverb."""

    def test_kadalasa_y_restores(self) -> None:
        """``Kadalasa'y`` → ``Kadalasan`` + ``ay`` (ADV "usually")."""
        out = _pipeline("Kadalasa'y")
        assert out == ["Kadalasan", "ay"]

    def test_minsa_y_restores(self) -> None:
        """``minsa'y`` → ``minsan`` + ``ay`` (ADV "sometimes")."""
        out = _pipeline("minsa'y")
        assert out == ["minsan", "ay"]

    def test_karaniwa_y_restores(self) -> None:
        """``Karaniwa'y`` → ``Karaniwan`` + ``ay`` (ADJ "ordinary")."""
        out = _pipeline("Karaniwa'y")
        assert out == ["Karaniwan", "ay"]

    def test_kadalasa_y_in_clause(self) -> None:
        """``Kadalasa'y sama-sama`` — the ADV-ay-fronted topic
        construction surfaces with the canonical adverb."""
        out = _pipeline("Kadalasa'y sama-sama")
        assert out[:2] == ["Kadalasan", "ay"]

    def test_kadalasa_y_lex_is_adv(self) -> None:
        """The restored ``Kadalasan`` token analyzes as ADV (not
        ``_UNK``); confirms the restore reaches the canonical lex
        entry."""
        toks = tokenize("Kadalasa'y mahirap")
        toks = split_apostrophe_t(toks)
        toks = split_apostrophe_y(toks)
        ms = analyze_tokens(toks)
        assert any(a.pos == "ADV" for a in ms[0]), \
            f"expected Kadalasan→ADV, got {[a.pos for a in ms[0]]}"


class TestApostropheYDefaultSplit:
    """post-8.4 anti-regression: the Phase 9.X.c4 vowel-final-host
    default split must remain unchanged for known bare hosts."""

    @pytest.mark.parametrize("host,surface,expected", [
        ("pamilya", "pamilya'y", "pamilya"),
        ("ito",     "ito'y",     "ito"),
        ("nito",    "nito'y",    "nito"),
        ("rito",    "rito'y",    "rito"),
        ("Mangyari", "Mangyari'y", "Mangyari"),
        ("siya",    "siya'y",    "siya"),
        ("gabi",    "gabi'y",    "gabi"),
    ])
    def test_known_host_passes_through(
        self, host: str, surface: str, expected: str,
    ) -> None:
        out = _pipeline(surface)
        # Default split: bare host + synthetic ``ay``.
        assert out == [expected, "ay"]


class TestApostropheYConsonantFinalGate:
    """post-8.4 anti-regression: consonant-final hosts unaffected
    by the new ``-n`` restore (the vowel-final gate excludes them)."""

    def test_consonant_final_y_no_split(self) -> None:
        """``apat 'y`` (hypothetical consonant-final) — bare
        apostrophe / y kept as separate tokens."""
        out = _pipeline("apat 'y")
        assert "'" in out and "y" in out


# === Multi-clitic orthogonality ==========================================


class TestMultiClitic:
    """post-8.4: multiple apostrophe-clitics in one sentence each
    apply independently."""

    def test_kahi_t_and_gabi_y(self) -> None:
        """``Kahi't sa gabi'y nakikinig siya.`` — ``Kahi't``
        collapses; ``gabi'y`` splits."""
        out = _pipeline("Kahi't sa gabi'y nakikinig siya")
        assert out[:5] == ["Kahit", "sa", "gabi", "ay", "nakikinig"]

    def test_three_y_clitics(self) -> None:
        """``Pamilya'y ito'y nito'y`` — three independent vowel-
        final splits in sequence."""
        out = _pipeline("pamilya'y ito'y nito'y")
        assert out == ["pamilya", "ay", "ito", "ay", "nito", "ay"]


# === Wave-1 closure ======================================================


class TestPagAaralSent6:
    """post-8.4: wave-1 ANG PAG-AARAL/sent-6 — the closure
    targeted by ``hangga't`` → ``hanggang``."""

    def test_sent6_closes(self) -> None:
        """``Hindi sila magsasalita hangga't sa palagay nila ay
        tamang-tama na ang sasabihin nila.`` — first wave-1 close
        attributable to the ``hangga't`` collapse."""
        parses = parse_text(
            "Hindi sila magsasalita hangga't sa palagay nila ay tamang-tama"
            " na ang sasabihin nila.",
            n_best=2,
        )
        assert len(parses) >= 1


# === Quote-mark anti-regression =========================================


class TestQuoteMarkPreservation:
    """post-8.4: the existing vowel-final-host + bare-``y``/``t``
    guards leave quote-mark apostrophes alone."""

    def test_open_quote_apostrophe(self) -> None:
        """Leading apostrophe (open quote) — no preceding stem,
        not collapsed."""
        out = _pipeline("'ako Tarzan")
        assert out[0] == "'"

    def test_close_quote_apostrophe(self) -> None:
        """Trailing apostrophe (close quote) — no ``y``/``t``
        after, not collapsed."""
        out = _pipeline("Jane'.")
        assert "'" in out
