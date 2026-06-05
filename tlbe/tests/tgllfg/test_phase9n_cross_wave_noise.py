# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 9.N: cross-wave harvest-noise filter (B2.D).

Two targeted additions to ``scripts/harvest_exemplars.py``:

1. **No-colon variant of S&O 1972 two-letter focus/voice
   abbreviation prefix-strip.** Phase 9.M added the colon-form
   strip (``AF: Naghugas …``) but S&O inconsistently uses the
   no-colon form too (``AF Naghugas ng pinggan ang bata.``).
   A separate ``_FOCUS_VOICE_ABBREV_PREFIX_RE`` handles the
   no-colon variant with optional hyphen-colon for OCR-degenerate
   forms (``OF-: Abutin mo …``). 19 hits in wave3-so1972.

2. **Expand ``_EN_MARKERS`` with pedagogical-prose vocabulary.**
   Pre-9.N, descriptive linguistics lines like ``Note the
   occurrence of mo before nga and ninyo after nga.`` slipped
   through ``_looks_like_tagalog`` because they contained
   Tagalog markers (``mo``, ``nga``, ``ninyo``) as their topic,
   tying the English-vs-Tagalog marker count. The extended set
   adds: ``as``, ``also``, ``free``, ``note``, ``notice``,
   ``occur``/``occurs``/``occurrence``/``occurred``,
   ``preceded``/``preceding``/``followed``, ``consonant``/``vowel``
   (and plurals), ``construction``/``constructions``,
   ``alternant``/``alternants``, ``variant``/``variants``,
   ``phonemic``/``phonetic``, ``context``/``contexts``,
   ``elsewhere``/``initially``/``finally``/``medially``,
   ``usually``/``always``/``often``/``sometimes``/``optional``,
   ``personal``, ``speaker``/``speakers``, ``form``/``forms``,
   ``describe``/``describes``, ``compare``/``compares``,
   ``observe``, ``indicate``/``indicates``.

   With these additions, pedagogical-prose lines now have enough
   English-marker count to tip the ``en > tgl`` test and get
   rejected.

The plan §B2.D-original ``len(tokens) ≤ 2 + harvest-noise-token``
filter turned out to be obsolete: ``_is_sentence_shape`` already
requires ≥ 3 tokens (so the ``≤ 2`` clause never fires for non-
Wave-1 sources), and the LFG-glossing-abbreviation set has been
handled by 9.K/9.M's grammar-tag-prefix regexes.

Corpus impact: wave2-rc1990 1025 → 1022 (-3 pedagogical-prose
lines: ``Note the occurrence …`` / ``Raw, a variant form …`` /
``Ikaw usually occurs initially …``). wave3-so1972 1260 → 1253
(-7 pedagogical-prose lines like ``Some speakers use daw and raw
as free alternants …`` / ``The linker na/-ng has two different
forms.``). wave3-rg-conversational 666 → 665 (-1).

Full-corpus parse-rate impact: RC1990 94/1025 → 93/1022, -1 abs /
-0.07pp (false-positive parse on ``Ikaw usually occurs …``
eliminated). Cumulative 667/5197 (12.83%) → 666/5186 (12.84%),
-1 abs / +0.01pp. Same quality-improvement-as-near-zero-yield
pattern as 9.L / 9.M.
"""

import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import harvest_exemplars as he  # type: ignore[import-not-found]  # noqa: E402


class TestPhase9nFocusVoiceNoColon:
    """``_FOCUS_VOICE_ABBREV_PREFIX_RE`` strips the no-colon variant
    of S&O 1972's two-letter focus/voice abbreviations."""

    @pytest.mark.parametrize("inp,expected", [
        ("AF Naghugas ng pinggan ang bata.",
         "Naghugas ng pinggan ang bata."),
        ("OF Binabasa ng guro ang nobela.",
         "Binabasa ng guro ang nobela."),
        ("LF Hinugasan ng bata ang pinggan.",
         "Hinugasan ng bata ang pinggan."),
        ("DF Lalakipan ng istudyante ng kuwalta ang sulat.",
         "Lalakipan ng istudyante ng kuwalta ang sulat."),
        ("BF Ibinili niya ng bigas.",
         "Ibinili niya ng bigas."),
        # OCR-degenerate hyphen-colon variant
        ("OF-: Abutin mo ang mangga.",
         "Abutin mo ang mangga."),
        # OF- without colon
        ("OF- Abutin mo ang mangga.",
         "Abutin mo ang mangga."),
        # 9.M colon-form still works
        ("AF: Naligo siya ng mainit na tubig.",
         "Naligo siya ng mainit na tubig."),
    ])
    def test_strips_no_colon_prefix(
        self, inp: str, expected: str
    ) -> None:
        assert he._clean_sentence_text(inp) == expected

    @pytest.mark.parametrize("inp", [
        # Lookahead requires capital letter after the abbreviation —
        # don't strip if the next char is lowercase or non-letter.
        "AF naghugas ng pinggan.",  # lowercase next char
        "AF.",                       # end-of-line after
    ])
    def test_does_not_strip_without_capital_followup(
        self, inp: str
    ) -> None:
        # _clean_sentence_text may return None (sentence-shape gate)
        # or the original; the key invariant is that the AF prefix
        # is NOT stripped.
        result = he._clean_sentence_text(inp)
        if result is not None:
            assert result.startswith("AF"), (
                f"AF prefix should remain: {result!r}"
            )


class TestPhase9nPedagogicalProseRejection:
    """The extended ``_EN_MARKERS`` set tips ``_looks_like_tagalog``'s
    ``en > tgl`` test against descriptive grammar-prose lines that
    cite Tagalog particles as content."""

    @pytest.mark.parametrize("inp", [
        # RC1990 lines (English commentary citing Tagalog particles)
        "Note the occurrence of mo before nga and ninyo after nga.",
        "Raw, a variant form of daw, occurs after vowels.",
        "Ikaw usually occurs initially while ka occurs elsewhere.",
        # S&O lines
        "The linker na/-ng has two different forms.",
        "Daw and raw are free alternants, as are din and rin.",
        "Some speakers use daw and raw as free alternants in "
        "all phonemic contexts.",
        # Generated-from-pattern (synthetic)
        "These constructions occur in all phonemic contexts.",
        "Note that the personal speaker often uses these phrases.",
    ])
    def test_rejects_pedagogical_prose(self, inp: str) -> None:
        assert he._looks_like_tagalog(inp) is False

    @pytest.mark.parametrize("inp", [
        # Genuine Tagalog must still pass (≥ 2 _TGL_MARKERS tokens)
        "Bumili si Juan ng aklat sa palengke.",
        "Maganda ang araw, hindi ba?",
        "Nagluto si Karla ng pansit sa kusina.",
        "Pumunta po kayo sa amin.",
        "Ang ganda naman ng bahay mo.",
    ])
    def test_genuine_tagalog_still_passes(self, inp: str) -> None:
        assert he._looks_like_tagalog(inp) is True


class TestPhase9nEndToEndCorpusHygiene:
    """End-to-end via the wave-specific extractors — verify the
    targeted noise patterns are not leaking through post-9.N."""

    @pytest.mark.slow
    def test_no_focus_voice_no_colon_prefix_in_so_corpus(
        self
    ) -> None:
        import re
        bad = re.compile(
            r"^(AF|OF|LF|BF|IF|GF|RF|DF|CF|PF|"
            r"AV|OV|IV|DV|RV|LV|BV|CV|PV)"
            r"[-:]*\s+[A-Z]"
        )
        for ex in he.extract_so1972():
            assert not bad.match(ex.text_raw), (
                f"focus/voice prefix leaked: "
                f"{ex.locator} {ex.text_raw!r}"
            )

    @pytest.mark.slow
    def test_no_pedagogical_note_lines_in_rc1990(self) -> None:
        # The 3 pre-9.N RC1990 pedagogical-prose lines
        # ("Note the occurrence ...", "Raw, a variant form ...",
        # "Ikaw usually occurs ...") should be filtered.
        for ex in he.extract_rc1990():
            t = ex.text_raw.lower()
            # Trigger words that combine pedagogical-prose markers
            # with Tagalog particle citation:
            assert not (
                "occurrence" in t and "nga" in t
            ), f"pedagogical leaked: {ex.locator} {ex.text_raw!r}"
            assert "variant form of" not in t, (
                f"variant-form leaked: {ex.locator} {ex.text_raw!r}"
            )
