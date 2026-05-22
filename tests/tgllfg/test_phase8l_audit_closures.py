# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 8.L Commits 5-6: audit-closure integration tests.

Closes the audit-named ``kasing-`` family of constructions
(Wave 2 + Wave 3 harvest) via the combined effect of:

* Phase 8.L Commit 1 — magkasing- distributive equative cell +
  DISTRIB lift on the predicative-ADJ clause rule
* Phase 8.L Commit 2 — magkakasing- intensive distributive cell
* Phase 8.L Commit 3 — kasing_n_eq NOUN→ADJ equative cell +
  KASING_N feat + lift on predicative-ADJ rule
* Phase 8.L Commit 4 — split_linker_ng left-flanker carve-out +
  subject-pro-drop equative + GEN-standard frame
* Phase 8.L Commit 5 — lex pass: ``bagsik`` / ``payat`` /
  ``buti`` ADJ; ``edad`` / ``grado`` NOUN; ``mary`` / ``john`` /
  ``karla`` / ``frank`` / ``nadette`` proper-name NOUN.

Each test cites its source corpus and the surface modifications
(if any — most audit hits parse verbatim; a few have OCR noise
trimmed off, noted inline).
"""

import pytest


# ============================================================
# Audit hits that close fully (lex + paradigm + structure)
# ============================================================
class TestPhase8lAuditClosuresFull:
    """Audit candidates that parse verbatim after 8.L."""

    @pytest.mark.parametrize("sentence,source", [
        # R&C 1990 ch. 5 — magkasing- distributive equative
        ("Magkasingbagsik ang mga aso natin.",
         "R&C 1990 simple-expansions/sent-199"),
        # S&O 1972 page 249 — kasing- with two proper names
        ("Hindi kasingtalino ni Mary si John.",
         "S&O 1972 page-249/sent-325"),
        # R&G Intermediate page 238 — hyphen-joined kasing-NOUN +
        # pro-drop SUBJ + GEN-standard + discourse pala
        ("Kasing-edad pala ni Nadette.",
         "R&G Intermediate page-238/sent-1707"),
    ])
    def test_audit_hit_parses(
        self, sentence: str, source: str,
    ) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, (
            f"audit hit {source!r} did not parse: {sentence!r}"
        )


# ============================================================
# Audit hits that need surface normalization (OCR noise trimmed)
# ============================================================
class TestPhase8lAuditClosuresNormalized:
    """R&C 1990 includes an OCR-noisy candidate
    (``Magkasingtaas si Karla at si Frank (stna Karla at Frankj.``).
    The relevant linguistic content (the ``magkasing-`` + coordinated
    proper-name subjects) parses cleanly once the OCR-introduced
    parenthetical is removed."""

    def test_magkasingtaas_karla_frank_clean(self) -> None:
        from tgllfg.core.pipeline import parse_text
        # Original audit text:
        #   "Magkasingtaas si Karla at si Frank (stna Karla at Frankj."
        # Cleaned form (the actual sentence content):
        sentence = "Magkasingtaas si Karla at si Frank."
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, (
            f"normalised R&C 1990 sent-198 form did not parse: "
            f"{sentence!r}"
        )


# ============================================================
# Paradigm-cell-only audit closures (lex was the original block)
# ============================================================
class TestPhase8lLexAdditionsClose:
    """Each newly-added ADJ / NOUN unblocks a corresponding
    construction shape that was already wired."""

    @pytest.mark.parametrize("sentence,reason", [
        # bagsik ADJ + magkasing- cell
        ("Magkasingbagsik ang mga aso.", "bagsik ADJ enables magkasing-"),
        # payat ADJ + kasing-
        ("Kasingpayat si Maria.", "payat ADJ + kasing-"),
        # buti ADJ — ``magkasingbuti`` and ``magkakasingbuti`` shapes
        ("Magkasingbuti sila.", "buti ADJ + magkasing-"),
        ("Magkakasingbuti ang mga estudyante.",
         "buti ADJ + magkakasing- + general subject"),
        # grado NOUN
        ("Magkakasingbuti ng grado.", "buti ADJ + grado NOUN + GEN-standard"),
    ])
    def test_audit_shape_parses(
        self, sentence: str, reason: str,
    ) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, (
            f"{reason!r} — {sentence!r} should parse"
        )


# ============================================================
# Proper-name lex adds
# ============================================================
class TestPhase8lProperNames:
    """Each new proper-name NOUN behaves as a standard SUBJ /
    STANDARD slot filler, parallel to the existing
    ``juan`` / ``pedro`` / ``maria`` / ``ana`` entries."""

    @pytest.mark.parametrize("name", [
        "mary", "john", "karla", "frank", "nadette",
    ])
    def test_proper_name_as_nom_subject(self, name: str) -> None:
        from tgllfg.core.pipeline import parse_text
        # Capitalise for orthographic correctness; the analyzer
        # norms to lowercase.
        cap = name.capitalize()
        parses = parse_text(f"Maganda si {cap}.", n_best=2)
        assert len(parses) >= 1, (
            f"proper name {cap!r} did not parse as NOM-pivot"
        )

    @pytest.mark.parametrize("name", [
        "mary", "john", "karla", "frank", "nadette",
    ])
    def test_proper_name_as_gen_standard(self, name: str) -> None:
        from tgllfg.core.pipeline import parse_text
        cap = name.capitalize()
        parses = parse_text(
            f"Kasingganda ni {cap} si Maria.", n_best=2,
        )
        assert len(parses) >= 1, (
            f"proper name {cap!r} did not parse as GEN-standard"
        )
