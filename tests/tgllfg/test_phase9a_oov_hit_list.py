# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 9.A: tests for ``scripts/oov_hit_list.py`` helper.

The helper feeds Phase 9 lex-pass sub-PRs (9.B-9.J). Tests cover:

* Heuristic POS recognition (proper-name, VERB-prefix, VERB-suffix,
  unknown).
* ENGLISH? false-positive guard — common Tagalog tokens with native
  vowel clusters (``oo``, ``ii``) shouldn't be flagged.
* TSV/markdown emission shapes.
* Wave filter substring-matching.
"""

import io
import sys
from pathlib import Path

import pytest

# Import the script as a module.
SCRIPT_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import oov_hit_list as oh  # type: ignore[import-not-found]  # noqa: E402

sys.path.pop(0)


class TestHeuristicPOS:
    """POS-hint heuristics from token + sample context."""

    def test_proper_name_in_sentence_internal_position(self) -> None:
        # Capital-cased non-sentence-initial → proper name
        h = oh._heuristic_pos("david", "Si David ang bumili ng motorsiklo.")
        assert h == "NOUN(proper)?"

    def test_proper_name_when_token_is_sentence_initial_doesnt_overfit(
        self,
    ) -> None:
        # Sentence-initial capitalization is just sentence-casing,
        # not a proper-name signal.
        h = oh._heuristic_pos("david", "David ang bumili.")
        # The hit list still sees "David" cased — but the heuristic
        # explicitly excludes the first-word case to avoid over-fit.
        # Returns whichever later rule matches (none here → "?").
        assert h == "?"

    def test_verb_prefix_nag(self) -> None:
        # Verb-prefix patterns produce VERB?(prefix+base)
        h = oh._heuristic_pos("nagbasa", "Nagbasa siya.")
        assert h.startswith("VERB?(nag+")

    def test_verb_prefix_mag(self) -> None:
        h = oh._heuristic_pos("magluto", "Magluto siya.")
        assert h.startswith("VERB?(mag+")

    def test_verb_prefix_naka_before_nag(self) -> None:
        # ``naka`` is longer than ``na``; pattern order matters
        h = oh._heuristic_pos("nakatulog", "Nakatulog na siya.")
        assert h.startswith("VERB?(naka+")

    def test_verb_suffix_an(self) -> None:
        h = oh._heuristic_pos("luagan", "Luagan mo.")
        assert h.startswith("VERB?(") and h.endswith("+an)")

    def test_verb_suffix_in(self) -> None:
        h = oh._heuristic_pos("kanin", "Kanin niya.")
        assert h.startswith("VERB?(") and h.endswith("+in)")

    def test_short_token_no_verb_match(self) -> None:
        # ``in`` / ``an`` matches need base ≥ 3 chars
        h = oh._heuristic_pos("man", "Pero kahit man.")
        assert h == "?"

    def test_english_signature_ea(self) -> None:
        h = oh._heuristic_pos("read", "Read this.")
        assert h == "ENGLISH?"

    def test_english_signature_ie(self) -> None:
        h = oh._heuristic_pos("piece", "A piece.")
        assert h == "ENGLISH?"

    def test_tagalog_oo_not_english_false_positive(self) -> None:
        # ``loob`` (inside) has native ``oo`` — must NOT flag as English
        h = oh._heuristic_pos("loob", "mahina ang loob.")
        assert h != "ENGLISH?"

    def test_tagalog_magkaroon_not_english(self) -> None:
        h = oh._heuristic_pos("magkaroon", "Magkaroon ka ng pasensya.")
        # Hits VERB? prefix pattern before ENGLISH? check, and
        # ``magka`` is more specific than ``mag`` so it matches first.
        assert h.startswith("VERB?(")
        assert "magka" in h or "mag" in h

    def test_tagalog_ng_no_match(self) -> None:
        h = oh._heuristic_pos("xyz123", "xyz123 test.")
        assert h == "?"


class TestWaveFilter:
    """``--wave`` substring filter."""

    def _rows(self):
        return [
            oh.HitRow(rank=1, token="david", count=19,
                      sample_locator="Ch5/sent-1", sample_text="x"),
            oh.HitRow(rank=2, token="rosa", count=17,
                      sample_locator="page-94/sent-1", sample_text="x"),
            oh.HitRow(rank=3, token="bob", count=12,
                      sample_locator="wave2-rc1990/sent-1", sample_text="x"),
        ]

    def test_all_filter_keeps_everything(self) -> None:
        kept = oh._filter_by_wave(self._rows(), "all")
        assert len(kept) == 3

    def test_wave2_filter_substring(self) -> None:
        kept = oh._filter_by_wave(self._rows(), "wave2-rc1990")
        assert len(kept) == 1
        assert kept[0].token == "bob"

    def test_no_matches(self) -> None:
        kept = oh._filter_by_wave(self._rows(), "wave9-unknown")
        assert len(kept) == 0


class TestEmission:
    """TSV and markdown emission shapes."""

    def _hits(self):
        return [
            (oh.HitRow(rank=1, token="david", count=19,
                       sample_locator="Ch5/sent-1",
                       sample_text="Si David ang bumili."),
             "_UNK", "NOUN(proper)?"),
        ]

    def test_tsv_emission_format(self) -> None:
        buf = io.StringIO()
        oh.emit_tsv(self._hits(), out=buf)
        text = buf.getvalue()
        # Header + 1 row
        lines = text.strip().split("\n")
        assert len(lines) == 2
        header = lines[0].split("\t")
        assert header == ["rank", "token", "count", "morph",
                          "heuristic", "sample_locator", "sample_text"]
        cells = lines[1].split("\t")
        assert cells[1] == "david"
        assert cells[3] == "_UNK"
        assert cells[4] == "NOUN(proper)?"

    def test_markdown_emission_shape(self) -> None:
        buf = io.StringIO()
        oh.emit_markdown(self._hits(), out=buf)
        text = buf.getvalue()
        assert text.startswith("| Rank | Token |")
        assert "| 1 | `david` | 19 |" in text


class TestEndToEnd:
    """Smoke test: the helper runs against the cached
    ``oov-frequency.tsv`` artifact (if present)."""

    def test_runs_against_real_tsv(self) -> None:
        from pathlib import Path
        tsv = (Path(__file__).resolve().parents[2]
               / "data" / "tgl" / "exemplars" / "oov-frequency.tsv")
        if not tsv.exists():
            pytest.skip("oov-frequency.tsv not present; "
                        "run xwave-report first")
        rows = oh._load_tsv(tsv)
        assert len(rows) > 0
        # First row sanity: known-OOV token from corpus
        first = rows[0]
        assert first.rank == 1
        assert first.count >= 1
        assert first.token  # non-empty
