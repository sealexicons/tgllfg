# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-8.5.6: kasya VERB extension closing PAMILYA/sent-11.

Closes PAMILYA/sent-11 ``Siya ang humahawak ng pera ng pamilya at
pinagkakasya ito sa panganga-ilangan ng pamilya.`` — wave-1 105/123
→ 106/123 (86.18%).

Three additions:

1. **`kasya` VERB** (verbs.yaml) — TR root for the transitive
   stretching/managing reading; separate from the existing
   ADJ entry (adjectives.yaml) following the dual-POS convention
   used for ``ganda`` / ``pagod``. Restricted to `pag_in_ov` only
   (no `mag-` AV opt-in — the intransitive ``magkasya`` "X fits" has
   a different argument frame; opting into `mag-` would force the
   TR PRED template ``KASYA <SUBJ, OBJ>`` on AV intransitive
   surfaces, failing completeness).

2. **`pag_in_ov` paradigm class** (paradigms.yaml) — OV (theme-
   pivot) form for verbs of distribution / sharing / stretching
   without the final `-an` suffix used by the canonical ``pag_an``
   DV class. Cells: PFV (pinagkasya), IPFV (pinagkakasya), CTPL
   (pagkakasya). Currently only ``kasya`` opts in; productive class
   for future audit pressure.

3. **`pangangailangan` NOUN** (nouns.yaml) — lexicalized abstract
   noun "need / necessity". Audit-pinned by PAMILYA/sent-11
   ``sa pangangailangan ng pamilya``. The OCR-original
   ``panganga-ilangan`` (hyphen in wrong position) is collapsed
   to ``pangangailangan`` by the tokenizer's hyphen-merge pre-pass
   — both surfaces parse.

## Audit signal (post-8.5.5.1 → post-8.5.6)

Wave-1 105→106/123 (+1: PAMILYA/sent-11). Other waves stable.
"""

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import _get_default


class TestKasyaPagInOvCell:
    """post-8.5.6 (1)+(2): `kasya` VERB + `pag_in_ov` paradigm cell."""

    def test_pinagkakasya_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("pinagkakasya")

    def test_pinagkasya_pfv_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("pinagkasya")

    def test_pagkakasya_ctpl_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("pagkakasya")

    def test_pinagkakasya_clause(self) -> None:
        """``Pinagkakasya niya ang pera.`` — OV-IPFV with GEN-AGENT
        + NOM-pivot (the theme being stretched)."""
        parses = parse_text("Pinagkakasya niya ang pera.", n_best=1)
        assert len(parses) >= 1

    def test_pinagkakasya_with_dat_pp(self) -> None:
        """The PAMILYA/sent-11 inner clause shape."""
        parses = parse_text(
            "Pinagkakasya niya ito sa pangangailangan.", n_best=1,
        )
        assert len(parses) >= 1


class TestPangangailanganNoun:
    """post-8.5.6 (3): `pangangailangan` NOUN."""

    def test_pangangailangan_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("pangangailangan")

    def test_pangangailangan_in_dat_pp(self) -> None:
        """``sa pangangailangan ng pamilya`` — DAT-PP with POSS."""
        parses = parse_text(
            "Kasama sa pangangailangan ng pamilya ang pera.", n_best=1,
        )
        assert len(parses) >= 1


class TestPamilyaSent11Closure:
    """post-8.5.6: full PAMILYA/sent-11 closure combining all three
    additions plus the post-8.5.2 V-V S_GAP coord rule (under ang
    headless-RC)."""

    def test_pamilya_sent11_normalized(self) -> None:
        """With ``pangangailangan`` (no hyphen) — the canonical form."""
        parses = parse_text(
            "Siya ang humahawak ng pera ng pamilya at pinagkakasya "
            "ito sa pangangailangan ng pamilya.",
            n_best=1,
        )
        assert len(parses) >= 1

    def test_pamilya_sent11_ocr_form(self) -> None:
        """The OCR-original ``panganga-ilangan`` (hyphen in wrong
        position) is collapsed to ``pangangailangan`` by the tokenizer
        hyphen-merge pre-pass — should parse equivalently."""
        parses = parse_text(
            "Siya ang humahawak ng pera ng pamilya at pinagkakasya "
            "ito sa panganga-ilangan ng pamilya.",
            n_best=1,
        )
        assert len(parses) >= 1


class TestAntiRegression:
    """Existing kasya ADJ + pag_an DV paradigm + pang- nouns
    unchanged — the new entries are additive."""

    def test_kasya_adj_preserved(self) -> None:
        """``Kasya ang aklat.`` — predicative ADJ reading still parses."""
        parses = parse_text("Kasya ang aklat.", n_best=1)
        assert len(parses) >= 1

    def test_pag_an_dv_preserved(self) -> None:
        """Existing pag_an DV paradigm: ``Pinagbintangan niya ang
        bata.`` still parses unchanged."""
        parses = parse_text("Pinagbintangan niya ang bata.", n_best=1)
        assert len(parses) >= 1

    def test_kailangan_adj_preserved(self) -> None:
        """``Kailangan ko ang pera.`` — kailangan ADJ STATIVE_PRED
        clause still parses."""
        parses = parse_text("Kailangan ko ang pera.", n_best=1)
        assert len(parses) >= 1
