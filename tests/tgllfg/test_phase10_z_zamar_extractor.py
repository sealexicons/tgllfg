# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.Z: Zamar 2023 wave-5 harvest extractor.

Adds ``extract_zamar2023`` to ``scripts/harvest_exemplars.py``,
producing ``data/tgl/exemplars/wave5-zamar2023.jsonl`` from Sheila
Zamar's *Filipino: An Essential Grammar* (Routledge 2023) — the
fifth corpus source and second native-PDF (after PK91 wave 4).

Zamar's running examples follow a regular triplet layout under
"Examples of ..." headers:

    <Tagalog example sentence.>
    <interlinear gloss line>        ("Wash–gen.you–subjmark.dishes")
    <English translation.>

pdftotext's -layout rendering interleaves two contaminants into
the example lines, both separated by a column gap of 2+ spaces:
(a) a left-margin chapter sidebar label ("Nouns and", "Verbal
aspect"), and (b) a right-column English gloss. The extractor
splits each line on those gaps and keeps only the segment that is
a Tagalog sentence.

Conventions handled by the extractor:

1. **Column-gap split**: each physical line is split on runs of
   2+ spaces; margin labels + English glosses land in their own
   segments and fail the Tagalog-shape / sentence-shape filters.
2. **En-dash gloss reject**: the interlinear gloss line joins
   morpheme glosses with the en-dash U+2013 ("Eat–you"); natural
   Tagalog redup / compounding uses the ASCII hyphen ("araw-araw"),
   so any en-dash marks a segment as gloss notation → rejected.
3. **Phonemic /slash/ reject**: §1.6-style phonemic forms
   (``/araw-araw/``) are rejected via the shared ``_PHONETIC_RE``.
4. **Parenthetical stripping**: ``(Sa) Kanyang libro ito.`` →
   ``Kanyang libro ito.`` (bare variant).
5. **Terminal-punct truncation**: a same-segment English gloss
   tail joined by a single space (``... papel. I took ...``) is
   dropped by truncating at the first ``.``/``?``/``!``.
6. **Front-matter skip**: PDF pages 1-28 (endorsements / TOC /
   preface / chapter-1 phonology, whose only examples are
   phonemic /slash/ forms) are skipped; running syntax examples
   begin on PDF page 29.
"""

import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import harvest_exemplars as he  # type: ignore[import-not-found]  # noqa: E402


# === _zamar_clean_segment — segment cleaning ==========================


class TestZamarCleanSegmentEnDashReject:
    """En-dash (U+2013) gloss-morpheme joiner → segment rejected."""

    @pytest.mark.parametrize("inp", [
        "Eat–you",
        "Wash–gen.you–subjmark.dishes–oblmark.kitchen",
        "Can–subj.I.lnk–cook–genmark.chicken–later",
    ])
    def test_endash_rejected(self, inp: str) -> None:
        assert he._zamar_clean_segment(inp) is None

    def test_ascii_hyphen_redup_kept(self) -> None:
        """ASCII-hyphen reduplication (``araw-araw``) is NOT an
        en-dash, so the segment survives cleaning."""
        assert (
            he._zamar_clean_segment("May trabaho si Rosa araw-araw.")
            == "May trabaho si Rosa araw-araw."
        )


class TestZamarCleanSegmentPhonetic:
    """Phonemic /slash/ forms (lowercase-letter runs) are rejected by
    the shared ``_PHONETIC_RE`` inside ``_zamar_clean_segment``."""

    @pytest.mark.parametrize("inp", [
        "/araw-araw/",
        "May /araw-araw/ dito.",
    ])
    def test_phonetic_rejected(self, inp: str) -> None:
        assert he._zamar_clean_segment(inp) is None

    def test_notation_heavy_slash_rejected_downstream(self) -> None:
        """A prose line with a notation-heavy slash form
        (``/takbo + rep = tatakbo/``, containing ``+``/``=`` that
        ``_PHONETIC_RE`` doesn't match) survives ``_zamar_clean_segment``
        but is rejected at the page level by ``_looks_like_tagalog``
        (English prose, 0 Tagalog markers)."""
        line = "Some examples are /takbo + rep = tatakbo/ will run."
        assert list(he._zamar_extract_from_page(7, line)) == []


class TestZamarCleanSegmentParen:
    """Parenthetical optional elements are stripped (bare variant)."""

    @pytest.mark.parametrize("inp,expected", [
        ("(Sa) Kanyang libro ito.", "Kanyang libro ito."),
        ("Kumain (na) siya.", "Kumain siya."),
    ])
    def test_paren_stripped(self, inp: str, expected: str) -> None:
        assert he._zamar_clean_segment(inp) == expected


class TestZamarCleanSegmentTerminalTruncation:
    """A same-segment English gloss tail joined by a single space is
    dropped at the first terminal punctuation."""

    @pytest.mark.parametrize("inp,expected", [
        ("Kinuha ko ang kanilang mga papel. I took their papers.",
         "Kinuha ko ang kanilang mga papel."),
        ("Kumain ka? Eat-you", "Kumain ka?"),
        ("Tumakbo siya! He ran.", "Tumakbo siya!"),
    ])
    def test_truncate_at_terminal(self, inp: str, expected: str) -> None:
        assert he._zamar_clean_segment(inp) == expected

    def test_no_tail_unchanged(self) -> None:
        assert (
            he._zamar_clean_segment("Kumain ka sa kusina.")
            == "Kumain ka sa kusina."
        )


# === _zamar_extract_from_page — page-level extraction =================


class TestZamarExtractFromPage:
    """The page extractor splits column gaps and keeps only Tagalog
    sentences; margin labels and English glosses are dropped."""

    def test_margin_label_dropped(self) -> None:
        """A left-margin chapter sidebar label glued to the example
        by a column gap is dropped."""
        page = "Nouns and       Saan ka kumuha ng mga ito?"
        out = list(he._zamar_extract_from_page(31, page))
        assert len(out) == 1
        assert out[0].text_raw == "Saan ka kumuha ng mga ito?"

    def test_english_gloss_column_dropped(self) -> None:
        """A right-column English gloss separated by a column gap is
        dropped; the Tagalog segment survives."""
        page = "Ang papayat ng mga manok.           The chickens are very thin."
        out = list(he._zamar_extract_from_page(51, page))
        assert len(out) == 1
        assert out[0].text_raw == "Ang papayat ng mga manok."

    def test_interlinear_gloss_line_dropped(self) -> None:
        """The interlinear gloss line (en-dash joiner, 0 Tagalog
        function-word markers) yields nothing."""
        page = "Wash–gen.you–subjmark.dishes–oblmark.kitchen"
        assert list(he._zamar_extract_from_page(40, page)) == []

    def test_english_translation_line_dropped(self) -> None:
        """A plain English translation line fails the Tagalog-shape
        filter."""
        page = "You wash the dishes in the kitchen."
        assert list(he._zamar_extract_from_page(40, page)) == []

    def test_locator_and_fields(self) -> None:
        page = (
            "Kumain ka sa kusina.\n"
            "Manonood kami ng sine.\n"
        )
        out = list(he._zamar_extract_from_page(29, page))
        assert len(out) == 2
        assert out[0].locator == "page-29/sent-1"
        assert out[1].locator == "page-29/sent-2"
        for ex in out:
            assert ex.source == "zamar2023"
            assert ex.ocr_quality == "native-pdf"
            assert ex.has_gloss is True


# === extract_zamar2023 — integration ==================================


class TestZamarIntegration:
    """End-to-end harvest over the real source file."""

    @pytest.fixture(scope="class")
    def exemplars(self) -> list:
        return list(he.extract_zamar2023())

    def test_harvest_yields_reasonable_count(self, exemplars: list) -> None:
        # Observed ~498 at first harvest; guard a generous floor so
        # the test survives minor source/extractor drift but catches
        # a catastrophic extraction failure.
        assert len(exemplars) > 400

    def test_all_zamar_native_pdf(self, exemplars: list) -> None:
        for ex in exemplars:
            assert ex.source == "zamar2023"
            assert ex.ocr_quality == "native-pdf"

    def test_all_pass_shared_filters(self, exemplars: list) -> None:
        """Every harvested exemplar passes the shared sentence-shape
        + Tagalog-shape filters and carries no residual gloss
        notation (en-dash / phonemic slash)."""
        for ex in exemplars:
            assert he._is_sentence_shape(ex.text_raw)
            assert he._looks_like_tagalog(ex.text_raw)
            assert "–" not in ex.text_raw
            assert not he._PHONETIC_RE.search(ex.text_raw)

    def test_front_matter_skipped(self, exemplars: list) -> None:
        """All locators reference PDF pages past the front matter."""
        for ex in exemplars:
            page = int(ex.locator.split("/")[0].removeprefix("page-"))
            assert page > he._ZAMAR_FRONT_MATTER_PAGES

    def test_known_clean_examples_present(self, exemplars: list) -> None:
        """A few hand-verified clean examples from the survey are
        harvested (guards the core extraction path)."""
        texts = {ex.text_raw for ex in exemplars}
        assert "Kumain ka sa kusina." in texts
        assert "Malaki ang bahay nila." in texts
