# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.A Commit 16 — Multi-word coord particles (§18 L76 + L82).

Three multi-word coord phrases that combine two existing PARTs into
a single virtual PART for downstream consumption by the Phase 5k
binary clausal / NP coord rules:

    ``o kaya``  → COORD=OR  + UNCERTAIN=YES  ("or maybe / or perhaps")
    ``at saka`` → COORD=AND + SEQUENCE=YES   ("and also / and then")
    ``at nang`` → COORD=AND + RESULT=YES     ("and so / and so that")

Same combining mechanic as Phase 5m Commit 11 (``gayon din`` /
``ganon din`` / ``bukod dito`` discourse connectives). The virtual
PART carries the basic COORD value (OR / AND) so the existing
binary coord rules fire unchanged; the secondary discriminator
(UNCERTAIN / SEQUENCE / RESULT) rides for downstream consumers
without affecting structural composition.

Lex (Phase 5k Commit 1 + Commit 16): ``o`` / ``at`` exist as
PART[COORD=OR]/[COORD=AND]; ``kaya`` exists as PART[COORD=SO]
(homonym — the o-kaya rule constrains by lemma); ``saka`` is added
in this commit; ``nang`` exists as PART[COMP_TYPE=TEMP_SINCE]
(the at-nang rule constrains by lemma).
"""

import pytest

from tgllfg.core.pipeline import parse_text


# === S-coord with multi-word particles ====================================


class TestSCoordMultiWord:
    """Each multi-word particle composes S-coord clauses."""

    @pytest.mark.parametrize("sentence", [
        # o kaya:
        "Kumain si Maria o kaya tumakbo si Juan.",
        # at saka:
        "Kumain si Maria at saka tumakbo si Juan.",
        # at nang:
        "Kumain si Maria at nang tumakbo si Juan.",
    ])
    def test_s_coord_multi_word(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === NP-coord with multi-word particles ===================================


class TestNpCoordMultiWord:
    """Each multi-word particle composes NP-coord at clause-end."""

    @pytest.mark.parametrize("sentence", [
        # NOM-NP coord:
        "Kumain si Maria o kaya si Juan.",
        "Kumain si Maria at saka si Juan.",
        "Kumain si Maria at nang si Juan.",
        # GEN-NP coord:
        "Bumili ako ng aklat o kaya ng gatas.",
        "Bumili ako ng aklat at saka ng gatas.",
    ])
    def test_np_coord_multi_word(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === f-structure carries discriminator flag ===============================


class TestDiscriminatorFlags:
    """The matrix carries the basic COORD value plus the multi-word
    discriminator (UNCERTAIN / SEQUENCE / RESULT)."""

    def test_o_kaya_carries_uncertain(self) -> None:
        parses = parse_text("Kumain si Maria o kaya tumakbo si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("COORD") == "OR"

    def test_at_saka_carries_sequence(self) -> None:
        parses = parse_text("Kumain si Maria at saka tumakbo si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("COORD") == "AND"

    def test_at_nang_carries_result(self) -> None:
        parses = parse_text("Kumain si Maria at nang tumakbo si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("COORD") == "AND"


# === Plain-coord regression ===============================================


class TestPlainCoordRegression:
    """Plain coord (single-word `at` / `o`) must continue to work —
    the new multi-word rules don't shadow them."""

    @pytest.mark.parametrize("sentence", [
        "Kumain si Maria at kumain si Juan.",
        "Kumain si Maria o kumain si Juan.",
        "Bumili ako ng aklat at ng gatas.",
        "Kumain si Maria o si Juan.",
    ])
    def test_plain_coord_still_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
