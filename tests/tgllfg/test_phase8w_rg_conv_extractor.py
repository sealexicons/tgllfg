"""Phase 8.W: R&G Conv harvest-extractor improvements.

Closes the audit-surfaced noise classes in
``data/tgl/exemplars/wave3-rg-conversational.jsonl``:

1. **Speaker-tag widening.** ``_DIALOG_SPEAKER_RE`` previously
   required all-uppercase speaker labels, so numbered-speaker dialog
   lines ``S1: ...`` / ``S2: ...`` and their OCR variants ``Sl:`` /
   ``Sll:`` (digit ``1`` mis-rendered as lowercase ``l``) fell
   through into ``prose`` mode and retained the ``S2:`` prefix in
   the emitted exemplar.

2. **Parenthetical-direction strip.** Dialog lines like
   ``S1 (to S2): Ano sa Tagalog ang "classroom"?`` previously fell
   through too. A new ``_DIRECTION_PREFIX_RE`` strips the
   parenthetical-direction prefix; the residual utterance is
   classified as dialog.

3. **Title-abbreviation split protection.** ``_split_sentences``
   previously split after ``Gng.`` (Mrs.) and ``Bb.`` (Miss),
   yielding fragments like ``"Ito si Bb."``. The split regex now
   suppresses the split when the period closes one of the common
   Tagalog / English title abbreviations.

4. **Column-gutter bleed filter.** R&G Conv's pdftotext layout
   sometimes joins adjacent columns into a single line separated
   by a wide whitespace gutter. The filter trims everything after
   the first ≥10-char internal whitespace run on R&G Conv lines.

5. **Parenthesized English-gloss strip.** Lines of the form
   ``(Kaibigan ko siya.)    (A friend of mine.)`` previously
   passed through with the English gloss attached. The strip
   leaves only the Tagalog half.

Items 1-2 are tested in this file as part of the C1 commit; items
3-5 are tested in subsequent commits.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import harvest_exemplars as he  # type: ignore[import-not-found]  # noqa: E402


class TestPhase8wSpeakerRegex:
    """The widened ``_DIALOG_SPEAKER_RE`` accepts numbered-speaker
    labels (``S1`` / ``S2`` / ``S3`` / ``S4``) and their OCR
    variants (``Sl`` / ``Sll``), in addition to the existing
    all-uppercase tags (``BEN`` / ``LINDA`` / ``A`` / ``B``)."""

    @pytest.mark.parametrize("line,expected_body", [
        ("BEN: Hello",                "Hello"),
        ("LINDA: Kumusta",            "Kumusta"),
        ("A: Magandang umaga",        "Magandang umaga"),
        ("B: Magandang gabi",         "Magandang gabi"),
        ("S1: Marunong ang kaibigan ko.",
         "Marunong ang kaibigan ko."),
        ("S2: Sa downtown.",          "Sa downtown."),
        ("S3: Sa bahay.",             "Sa bahay."),
        ("S4: Aiam ko na",            "Aiam ko na"),
        ("Sl: ang pangalan ko",       "ang pangalan ko"),
        ("Sll: Ano",                  "Ano"),
    ])
    def test_speaker_match_body(
        self, line: str, expected_body: str
    ) -> None:
        m = he._DIALOG_SPEAKER_RE.match(line)
        assert m is not None, f"speaker regex did not match {line!r}"
        assert m.group(2).strip() == expected_body

    @pytest.mark.parametrize("line", [
        "Person pronoun kayo when greeting",  # English heading
        "Saan ka galing?",                      # bare interrogative
        "Maganda umaga po, Gng. Cruz.",       # title abbrev inline
        "Kumusta ka?",                          # no colon
    ])
    def test_non_speaker_does_not_match(self, line: str) -> None:
        assert he._DIALOG_SPEAKER_RE.match(line) is None


class TestPhase8wDirectionPrefix:
    """``_DIRECTION_PREFIX_RE`` strips parenthetical-direction
    speaker prefixes (``S1 (to S2):`` / ``B (to C):`` / ``(to S3):``
    / ``(To S2)``), including the OCR-degenerate ``B (to Cl:`` form
    where the closing paren is mis-OCR'd as a colon."""

    @pytest.mark.parametrize("line,expected_residual", [
        ("S1 (to S2): Ano sa Tagalog ang classroom?",
         "Ano sa Tagalog ang classroom?"),
        ("S2 (to S1): ang pangalan ko.",
         "ang pangalan ko."),
        ("S3 ( to S4): Ano ang noon sa Tagalog?",
         "Ano ang noon sa Tagalog?"),
        ("B (to C): Ano ang sinabi niya?",
         "Ano ang sinabi niya?"),
        ("B (to Cl: Ano ang pangalan niya?",
         "Ano ang pangalan niya?"),
        ("(to S3): Puti ba ang kulay nito?",
         "Puti ba ang kulay nito?"),
        ("(To S2) Ano ang ginawa ni X?",
         "Ano ang ginawa ni X?"),
        # Sentence-type-label variants (S1 (Sentence): / S3 (Response):)
        ("S1 (Sentence): Ihahagis ko ang bola.",
         "Ihahagis ko ang bola."),
        ("S3 (Response): Bola ang ihahagis niya.",
         "Bola ang ihahagis niya."),
    ])
    def test_direction_prefix_strips(
        self, line: str, expected_residual: str
    ) -> None:
        m = he._DIRECTION_PREFIX_RE.match(line)
        assert m is not None, (
            f"direction-prefix regex did not match {line!r}"
        )
        residual = line[m.end():].strip()
        assert residual == expected_residual

    @pytest.mark.parametrize("line", [
        "Maganda umaga po, Gng. Cruz.",  # no parenthetical
        "Ito si Bb. Santos.",             # title abbreviations only
        "May (Mayroong) kotse sa garahe.",  # paren mid-sentence
        "(Magandang umaga.)",              # paren-wrapped Tagalog
    ])
    def test_direction_prefix_does_not_match_normal_lines(
        self, line: str
    ) -> None:
        assert he._DIRECTION_PREFIX_RE.match(line) is None


class TestPhase8wTitleAbbrevSplitProtection:
    """``_split_sentences`` no longer splits after Tagalog or English
    title abbreviations (``Gng.``, ``Bb.``, ``Mr.``, ``Mrs.``, ``Dr.``,
    etc.). Before 8.W the splitter treated each as a sentence
    terminator and emitted truncated fragments like ``"Ito si Bb."``."""

    @pytest.mark.parametrize("text,expected_parts", [
        ("Hello. World.",          ["Hello.", "World."]),
        ("Saan ka galing? Sa bahay.",
         ["Saan ka galing?", "Sa bahay."]),
        ("Ito si Bb. Santos.",     ["Ito si Bb. Santos."]),
        ("Ano ang ginawa ni Gng. Cruz?",
         ["Ano ang ginawa ni Gng. Cruz?"]),
        ("Sino ang guro mo sa Si Gng. Santos",
         ["Sino ang guro mo sa Si Gng. Santos"]),
        ("Si Mr. Smith. Si Mrs. Brown.",
         ["Si Mr. Smith.", "Si Mrs. Brown."]),
        ("Si Dr. Reyes ay doktor.",
         ["Si Dr. Reyes ay doktor."]),
        ("Magandang umaga. Magandang gabi.",
         ["Magandang umaga.", "Magandang gabi."]),
        ("Si Sr. Dela Cruz. Maganda.",
         ["Si Sr. Dela Cruz.", "Maganda."]),
    ])
    def test_split_protects_title_abbrev(
        self, text: str, expected_parts: list[str]
    ) -> None:
        assert he._split_sentences(text) == expected_parts


class TestPhase8wTrailingEnglishGlossStrip:
    """``_strip_trailing_english_gloss`` removes pedagogical-aid
    English translations from the end of a Tagalog line. Mid-sentence
    parens and Tagalog-marker-bearing parens are left alone."""

    @pytest.mark.parametrize("text,expected", [
        ("Magandang umaga po. (Good morning.)",
         "Magandang umaga po."),
        ("Kaibigan ko siya. (A friend of mine.)",
         "Kaibigan ko siya."),
        ("Si Ben ito. (This is Ben.)",
         "Si Ben ito."),
        ("Maganda ang araw.",
         "Maganda ang araw."),                  # no paren — unchanged
        ("May (Mayroong) kotse sa garahe.",
         "May (Mayroong) kotse sa garahe."),    # mid-sentence — unchanged
        ("Pumupunta ako (sa tindahan).",
         "Pumupunta ako (sa tindahan)."),       # Tagalog 'sa' — unchanged
        ("(Kaibigan ko siya.) (A friend of mine.)",
         "(Kaibigan ko siya.)"),                # only trailing stripped
        ("Hello. (Sentence)",
         "Hello. (Sentence)"),                  # single token — unchanged
    ])
    def test_strip_trailing_english_gloss(
        self, text: str, expected: str
    ) -> None:
        assert he._strip_trailing_english_gloss(text) == expected

    def test_clean_sentence_text_strips_trailing_gloss(self) -> None:
        # End-to-end via _clean_sentence_text — the gloss strip runs
        # inside the cleanup pipeline.
        result = he._clean_sentence_text(
            "Kaibigan ko siya. (A friend of mine.)"
        )
        assert result == "Kaibigan ko siya."


class TestPhase8wColumnGutterSplit:
    """``_split_column_gutter`` splits a line on internal ≥ 10-char
    whitespace runs. This is the pdftotext-layout column-gutter
    signature for the R&G Conversational two-column dialog pages.
    Junk halves filter out via downstream sentence-shape / Tagalog-
    marker checks."""

    @pytest.mark.parametrize("line,expected_segments", [
        # No gutter — single segment.
        ("Magandang umaga po.", ["Magandang umaga po."]),
        # Wide gutter — two segments.
        ("Saan ka galing?                                         ko.",
         ["Saan ka galing?", "ko."]),
        # English-heading bleed.
        ("Person pronoun kayo when greeting          LINDA: Kumusta ka, Ben.",
         ["Person pronoun kayo when greeting", "LINDA: Kumusta ka, Ben."]),
        # Three columns (rare but seen in S2:/S3: blocks).
        ("S2: Sa downtown.              S3: Sa bahay.              S4: Aiam ko na",
         ["S2: Sa downtown.", "S3: Sa bahay.", "S4: Aiam ko na"]),
        # Border case: 9-space run shouldn't trigger.
        ("a b c         d e f",       # 9 spaces
         ["a b c         d e f"]),
    ])
    def test_split_segments(
        self, line: str, expected_segments: list[str]
    ) -> None:
        assert he._split_column_gutter(line) == expected_segments

    def test_idempotent_on_no_gutter(self) -> None:
        text = "Maganda ang araw."
        once = he._split_column_gutter(text)
        twice = he._split_column_gutter(once[0])
        assert once == twice == [text]
