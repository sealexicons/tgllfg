# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 9.Y: Kroeger 1991 harvest extractor.

Adds ``extract_kroeger1991`` to ``scripts/harvest_exemplars.py``,
producing ``data/tgl/exemplars/wave4-kroeger1991.jsonl`` from
Paul Kroeger's 1991 Stanford PhD dissertation *Phrase Structure
and Grammatical Relations in Tagalog*. Native-PDF source (not
OCR), ~210 example blocks with sub-divisions; ~200 high-signal
exemplars per harvest run.

PK91 conventions handled by the extractor:

1. **Block labels**: ``(N)`` opens an example, with optional
   inline sub-division ``a.``/``b.``/``c.``; sub-divisions can
   also follow on subsequent lines.
2. **Clitic boundaries**: ``=`` separates clitics
   (``ang=mga=bata``) — replaced with space.
3. **Morpheme boundaries**: ``-`` between alphabetic chars marks
   affix boundaries (``B-um-ili``, ``b-in-igy-an``,
   ``Ma-ta-talino``) — removed.
4. **Zero-morpheme markers**: ``-Ø`` / ``Ø`` (overt zero in OV
   citation forms like ``b-in-ili-Ø``) — dropped entirely.
5. **Constituent brackets**: ``[...]`` mark structural
   constituents (Kroeger's plurality / clefting examples) —
   stripped, content preserved.
6. **Gap markers**: ``__nom`` / ``__gen`` / ``__dat`` (Kroeger
   ch. 7 unbounded-dependency notation) — exemplar rejected
   entirely (theoretical abstraction, not parseable Tagalog).
7. **Ungrammaticality markers**: leading ``(*)`` / ``(?)`` /
   ``(*?)`` — stripped from surface, ``marked_ungrammatical``
   set True.
8. **Subscript co-indexing**: LFG binding subscripts ``i`` /
   ``j`` / ``k`` that pdftotext renders adjacent to the word
   (``niyai`` / ``Mariai``) — stripped when a pronoun-base
   subscript form anchors the index, with co-indexed
   capitalized proper names also stripped of the same letter.
"""

import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import harvest_exemplars as he  # type: ignore[import-not-found]  # noqa: E402


# === _clean_pk91_surface — basic notation stripping ===================


class TestCleanPK91SurfaceClitics:
    """``=`` clitic boundaries become spaces."""

    @pytest.mark.parametrize("inp,expected", [
        ("ang=lalake", "ang lalake"),
        ("ang=mga=bata", "ang mga bata"),
        ("ni=Maria sa=asawa", "ni Maria sa asawa"),
        ("ang=mga=bata=ng Intsik", "ang mga bata ng Intsik"),
    ])
    def test_equals_to_space(self, inp: str, expected: str) -> None:
        assert he._clean_pk91_surface(inp) == expected


class TestCleanPK91SurfaceMorphemeHyphens:
    """Inter-alphabetic ``-`` (morpheme boundary) is removed."""

    @pytest.mark.parametrize("inp,expected", [
        ("B-um-ili", "Bumili"),
        ("b-in-igy-an", "binigyan"),
        ("Ma-ta-talino", "Matatalino"),
        ("Ip-in-am-bili", "Ipinambili"),
    ])
    def test_strip_morpheme_hyphens(self, inp: str, expected: str) -> None:
        assert he._clean_pk91_surface(inp) == expected


class TestCleanPK91SurfaceZeroMorpheme:
    """``-Ø`` and bare ``Ø`` zero-morpheme markers are dropped."""

    @pytest.mark.parametrize("inp,expected", [
        ("Binili-Ø", "Binili"),
        ("kain-Ø ang isda", "kain ang isda"),
        ("X Ø Y", "X Y"),
    ])
    def test_strip_zero_morpheme(self, inp: str, expected: str) -> None:
        assert he._clean_pk91_surface(inp) == expected


class TestCleanPK91SurfaceBrackets:
    """``[`` and ``]`` constituent brackets are stripped; content
    preserved."""

    @pytest.mark.parametrize("inp,expected", [
        ("[ang mga liham]", "ang mga liham"),
        ("Pumunta ka sa [tindahan ng [pinuntahan ko]].",
         "Pumunta ka sa tindahan ng pinuntahan ko."),
        ("X [Y] Z", "X Y Z"),
    ])
    def test_strip_brackets(self, inp: str, expected: str) -> None:
        assert he._clean_pk91_surface(inp) == expected


class TestCleanPK91SurfaceCombined:
    """End-to-end ``_clean_pk91_surface`` on representative PK91
    surface lines."""

    @pytest.mark.parametrize("inp,expected", [
        ("B-um-ili    ang=lalake ng=isda sa=tindahan.",
         "Bumili ang lalake ng isda sa tindahan."),
        ("Nag-bigay lahat ang=mga=guro ng=pera sa= mga=bata.",
         "Nagbigay lahat ang mga guro ng pera sa mga bata."),
        ("Ma-ta-talino   ang=mga=bata=ng Intsik.",
         "Matatalino ang mga bata ng Intsik."),
        ("Pagsu-sulat-in    ni=Linda      [ang=mga=liham].",
         "Pagsusulatin ni Linda ang mga liham."),
    ])
    def test_full_cleanup(self, inp: str, expected: str) -> None:
        assert he._clean_pk91_surface(inp) == expected


# === _pk91_strip_subscripts — co-indexing handling ====================


class TestPK91StripSubscriptsPronouns:
    """Pronoun forms with co-indexing subscript get the letter
    stripped: ``niyai`` → ``niya``, ``kaniyaj`` → ``kaniya``."""

    @pytest.mark.parametrize("inp,expected", [
        ("Itinago ng asawa niyai kay Mariai ang pera.",
         "Itinago ng asawa niya kay Maria ang pera."),
        ("Sinoi ang yumayapos sa anak niyai?",
         "Sino ang yumayapos sa anak niya?"),
        ("Nagmamahal ang nanay ni Juani sa kaniyai.",
         "Nagmamahal ang nanay ni Juan sa kaniya."),
    ])
    def test_pronoun_triggers_strip(
        self, inp: str, expected: str,
    ) -> None:
        assert he._pk91_strip_subscripts(inp) == expected


class TestPK91StripSubscriptsNoFalsePositives:
    """Exemplars without pronoun-base subscript triggers are not
    modified — `Bumili`/`Intsik`/`bili` ending in ``i``/``k`` are
    legitimate Tagalog words, not coreference markers."""

    @pytest.mark.parametrize("inp", [
        "Bumili ang lalake ng isda sa tindahan.",
        "Matatalino ang mga bata ng Intsik.",
        "Ipinagbili ng hari ang alipin sa sarili niya.",
        "Sinisisi ni Maria ang kaniya ng sarili.",
        "Tulungan mo ako!",
    ])
    def test_unchanged_without_trigger(self, inp: str) -> None:
        assert he._pk91_strip_subscripts(inp) == inp


class TestPK91StripSubscriptsMultiLetter:
    """When multiple distinct subscript letters appear
    (``i`` and ``j``), each is detected independently."""

    def test_distinct_letters(self) -> None:
        # Multi-binder pattern from PK91 ch. 3: niyai binds with
        # Mariai (letter i); kaniyaj binds with Juanj (letter j).
        # Both proper names are in the closed-list set.
        inp = "Itinago niyai kay Mariai ang sulat kaniyaj ni Juanj."
        expected = "Itinago niya kay Maria ang sulat kaniya ni Juan."
        assert he._pk91_strip_subscripts(inp) == expected

    def test_capitalized_verb_not_stripped(self) -> None:
        """Title-case-initial verbs / discourse words ending in
        ``i``/``j``/``k`` are NOT stripped when a subscript
        letter is in use — only words whose stem is in the
        pronoun-base or proper-name set get stripped."""
        # ``Nahuli`` (AV-NVOL "got caught") starts capitalized
        # and ends in ``i`` but is not a subscripted proper name.
        inp = "Nahuli si Mariai dahil sa pagkawala niyai."
        expected = "Nahuli si Maria dahil sa pagkawala niya."
        assert he._pk91_strip_subscripts(inp) == expected


# === _pk91_yield_exemplar — filter pass ===============================


class TestPK91YieldExemplarGapMarkerRejection:
    """Exemplars with ``__nom`` / ``__gen`` / ``__dat`` gap
    markers (Kroeger ch. 7 unbounded-dependency abstraction)
    are rejected entirely."""

    @pytest.mark.parametrize("raw", [
        "Binalak niya ng [magbigay __nom ng pera sa Nanay].",
        "Binalak niya ng [bigyan __gen ng pera ang Nanay].",
        "Iniwanan ko siya ng [sinususulat __gen ang liham].",
    ])
    def test_gap_marker_rejected(self, raw: str) -> None:
        result = he._pk91_yield_exemplar(99, "1", "a", raw)
        assert result is None


class TestPK91YieldExemplarUngramMarker:
    """Leading ``(*)`` / ``(?)`` / ``(*?)`` markers are stripped
    from the surface and ``marked_ungrammatical=True`` is set."""

    @pytest.mark.parametrize("raw,expected_text", [
        ("(*)May bata ng kinain ang litson.",
         "May bata ng kinain ang litson."),
        ("(?)Bumili ang lalake ng isda sa tindahan.",
         "Bumili ang lalake ng isda sa tindahan."),
        ("(*?)Matatalino ang mga bata ng Intsik.",
         "Matatalino ang mga bata ng Intsik."),
    ])
    def test_ungram_marker_stripped(
        self, raw: str, expected_text: str,
    ) -> None:
        result = he._pk91_yield_exemplar(99, "1", "a", raw)
        assert result is not None
        assert result.text_raw == expected_text
        assert result.marked_ungrammatical is True


class TestPK91YieldExemplarCleanCase:
    """Canonical clean PK91 surface produces a well-formed
    Exemplar with source / locator / ocr_quality set correctly."""

    def test_canonical_emit(self) -> None:
        raw = "B-um-ili    ang=lalake ng=isda sa=tindahan."
        result = he._pk91_yield_exemplar(21, "13", "a", raw)
        assert result is not None
        assert result.source == "kroeger1991"
        assert result.locator == "page-21/ex-13a"
        assert result.text_raw == "Bumili ang lalake ng isda sa tindahan."
        assert result.has_gloss is True
        assert result.marked_ungrammatical is False
        assert result.ocr_quality == "native-pdf"


class TestPK91YieldExemplarLocator:
    """Locator format: ``page-N/ex-NLETTER`` with sub-letter,
    ``page-N/ex-N`` without."""

    def test_sub_letter_present(self) -> None:
        result = he._pk91_yield_exemplar(
            32, "9", "b", "Bumili ang lalake ng isda sa tindahan.",
        )
        assert result is not None
        assert result.locator == "page-32/ex-9b"

    def test_sub_letter_absent(self) -> None:
        result = he._pk91_yield_exemplar(
            32, "9", None, "Bumili ang lalake ng isda sa tindahan.",
        )
        assert result is not None
        assert result.locator == "page-32/ex-9"


# === Block detection: _pk91_extract_from_page =========================


class TestPK91BlockOnSameLine:
    """``(N) Tagalog text...`` — single-line example."""

    def test_single_block(self) -> None:
        page = "(58) Gusto ko ang litson.\n"
        results = list(he._pk91_extract_from_page(56, page))
        assert len(results) == 1
        assert results[0].locator == "page-56/ex-58"
        assert results[0].text_raw == "Gusto ko ang litson."


class TestPK91BlockWithSublabelOnSameLine:
    """``(N) a. Tagalog text`` — inline sub-division."""

    def test_inline_sublabel(self) -> None:
        page = "(13) a. B-um-ili ang=lalake ng=isda sa=tindahan.\n"
        results = list(he._pk91_extract_from_page(21, page))
        assert len(results) == 1
        assert results[0].locator == "page-21/ex-13a"


class TestPK91BlockSublabelOnNextLine:
    """``(N)`` on its own line; ``a.``/``b.`` follow."""

    def test_following_sublabels(self) -> None:
        page = (
            "(3)\n"
            "    a. Nagbigay lahat ang=mga=guro ng=pera sa=mga=bata.\n"
            "    b. Binigyan lahat ng=mga=guro ng=pera ang=mga=bata.\n"
            "    c. Ibinigay lahat ng=mga=guro sa=mga=bata ang=pera.\n"
        )
        results = list(he._pk91_extract_from_page(30, page))
        assert len(results) == 3
        assert [r.locator for r in results] == [
            "page-30/ex-3a", "page-30/ex-3b", "page-30/ex-3c",
        ]


class TestPK91BlockTransition:
    """A new ``(N)`` ends accumulation of sub-divisions for the
    prior block."""

    def test_block_transitions(self) -> None:
        page = (
            "(5)\n"
            "    a. Matatalino ang=mga=bata=ng Intsik.\n"
            "(6)\n"
            "    a. Nagsisikain na ang=mga=bata ng=hapunan.\n"
        )
        results = list(he._pk91_extract_from_page(31, page))
        assert len(results) == 2
        assert results[0].locator == "page-31/ex-5a"
        assert results[0].text_raw == "Matatalino ang mga bata ng Intsik."
        assert results[1].locator == "page-31/ex-6a"


class TestPK91BlockBodyProseIgnored:
    """Non-Tagalog body prose between examples is silently
    ignored."""

    def test_prose_between_blocks(self) -> None:
        page = (
            "(58) Gusto ko ang litson.\n"
            "Some commentary about the example follows here.\n"
            "More English prose explaining the LFG analysis.\n"
            "(59) Ayaw ko ng pulutan.\n"
        )
        results = list(he._pk91_extract_from_page(56, page))
        assert len(results) == 2
        assert results[0].locator == "page-56/ex-58"
        assert results[1].locator == "page-56/ex-59"


# === Integration: extract_kroeger1991 smoke test ======================


class TestKroeger1991Integration:
    """Smoke test: the full extractor produces ≥150 high-signal
    exemplars from PK91 when run against the cached .txt. (The
    actual harvest run is gated on ``data/tgl/references/PK91-
    Thesis-Revised.txt`` being present; if absent — e.g., on a
    fresh clone before manual ``pdftotext`` — the test skips.)"""

    def test_smoke_yield(self) -> None:
        txt_path = (
            Path(__file__).resolve().parents[2]
            / "data" / "tgl" / "references"
            / "PK91-Thesis-Revised.txt"
        )
        if not txt_path.exists():
            pytest.skip(
                "PK91-Thesis-Revised.txt not present; "
                "run pdftotext -layout to generate."
            )

        results = list(he.extract_kroeger1991())
        assert len(results) >= 150, (
            f"expected ≥150 PK91 exemplars; got {len(results)}"
        )

        # All exemplars should be tagged correctly.
        for r in results:
            assert r.source == "kroeger1991"
            assert r.ocr_quality == "native-pdf"
            assert r.has_gloss is True
            # Cleanup is complete — no residual notation.
            assert "=" not in r.text_raw
            assert "[" not in r.text_raw
            assert "]" not in r.text_raw
            assert "Ø" not in r.text_raw
            assert "__" not in r.text_raw
            # Hyphens may remain on orthographic compounds like
            # ``mag-isa`` if they reach here, but morpheme-style
            # ``X-um-Y`` patterns should be cleaned.
