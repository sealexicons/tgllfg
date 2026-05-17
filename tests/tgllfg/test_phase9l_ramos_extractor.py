"""Phase 9.L: Ramos 1971 harvest-extractor cleanup.

Extends ``_OCR_NOISE_CHAR_RE`` with three Ramos-dominant
mid-word OCR-substitution patterns that the 9.K filter didn't
cover:

1. **Mid-word ampersand** — Ramos OCR substitutes ``&`` for ``a``
   in many lowercase verb-paradigm forms (``Magb&on`` /
   ``Bil&ngin`` / ``Lin&pa`` / ``Tap&kan`` / ``Wilig&n`` /
   ``Magyak&g``). Six hits in wave2-ramos1971.jsonl.

2. **Digit between lowercase letters** — Ramos OCR substitutes
   digits for letters mid-word (``Iba6n`` for ``Ibaon`` —
   ``6`` for ``o``). Three hits in Ramos, but also affects
   other waves: 17 in S&O 1972 (``Iap1s`` / ``n3nay`` /
   ``k3tulong``), 12 in R&G Conv (``n1ya`` / ``s1yete`` /
   ``Mayro6ng`` / ``libr6``), 1 in R&G Int. Restricted to
   digits between two lowercase letters to avoid false
   positives on legitimate alphanumeric tokens.

3. **Slash followed by single trailing letter at word boundary**
   — Ramos OCR substitutes ``/`` for a missing letter when only
   one letter remains before the next space (``Iabant/e`` for
   ``Iabante``). The single-trailing-letter constraint
   distinguishes this from legitimate Tagalog alternation
   tokens (``mister/misis`` / ``ako/kami`` / ``po/ho`` /
   ``kanan/kaliwa``), where both sides of the slash are
   multi-letter Tagalog words.

The Ramos corpus drops from 220 → 209 (-11 noise lines).
Cumulative full-corpus impact: 669/5268 (12.70%) →
668/5226 (12.78%), -1 absolute / +0.08pp. The -1 absolute is
a quality improvement disguised as a regression: ``May sakit
ang nanay n1ya.`` (R&G Conv pre-9.L) parsed because the parser
treated ``n1ya.`` (OCR garbage for ``niya``) as a proper-noun
fallback. Removing the OCR-garbled line eliminates that
sampling fluke; same pattern as Phase 9.G's ``kagabi`` lex add.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import harvest_exemplars as he  # type: ignore[import-not-found]  # noqa: E402


class TestPhase9lAmpersandMidWord:
    """Mid-word ``&`` is the Ramos OCR substitution for ``a``."""

    @pytest.mark.parametrize("inp", [
        "Magb&on ka nang di ka gutumin.",
        "Bil&ngin mo ang mga sisiw.",
        "Lin&pa niya ang baka.",
        "Tap&kan mo ito.",
        "Wilig&n mo ang mga papiantsahin.",
        "Magyak&g tayo ng mga makakasama.",
        # Pre-leading-cap form too.
        "N&bangga' ang kotse sa pader.",
    ])
    def test_rejects_ampersand_mid_word(self, inp: str) -> None:
        assert he._clean_sentence_text(inp) is None


class TestPhase9lDigitMidLowercase:
    """Digit between lowercase letters is OCR garbage in every
    audit wave that has them: Ramos / S&O / R&G Conv / R&G Int."""

    @pytest.mark.parametrize("inp", [
        # Ramos
        "Iba6n mo ang patay na pusa.",
        "Ib6to natin ang mabuting kandidato.",
        "Maglib6t ka sa bayan.",
        # R&G Conv
        "May sakit ang nanay n1ya.",
        "Nagmimiting kami ng alas s1yete.",
        "Mayro6ng libr6 si Elsa.",
        # S&O
        "Magluluto ng pagkain ang n3nay bukas.",
    ])
    def test_rejects_digit_mid_lowercase(self, inp: str) -> None:
        assert he._clean_sentence_text(inp) is None


class TestPhase9lSlashSingleLetter:
    """Slash followed by exactly one letter at word boundary
    is OCR garbage; the constraint distinguishes this from
    legitimate alternation tokens where both sides are
    multi-letter."""

    @pytest.mark.parametrize("inp", [
        "Iabant/e mo ang kotse nang kaunti.",
    ])
    def test_rejects_slash_single_letter(self, inp: str) -> None:
        assert he._clean_sentence_text(inp) is None

    @pytest.mark.parametrize("inp,expected", [
        # Legitimate alternation — preserved.
        ("Kumusta ang mister/misis mo?",
         "Kumusta ang mister/misis mo?"),
        ("Pupunta po/ho ba kayo sa ospital?",
         "Pupunta po/ho ba kayo sa ospital?"),
        ("Lumiko ka sa kanan/kaliwa.",
         "Lumiko ka sa kanan/kaliwa."),
        ("Painom (ako/kami) ng tubig.",
         "Painom (ako/kami) ng tubig."),
    ])
    def test_preserves_legitimate_alternation(
        self, inp: str, expected: str
    ) -> None:
        assert he._clean_sentence_text(inp) == expected


class TestPhase9lDoesNotAffectCleanLines:
    """The new filter patterns must not affect clean Tagalog or
    legitimate proper-name lines."""

    @pytest.mark.parametrize("inp", [
        # Clean Ramos dictionary example sentence
        "Bumili ng bahay si Gng. Cruz.",
        "Aliwin mo siya.",
        "Buksan mo ang bintana.",
        # Proper-name with mid-cap letter — preserved (no & / digit
        # / single-letter slash)
        "Bumalik si McArthur sa Pilipinas.",
        # Plain Tagalog
        "Maganda ang araw.",
        "Maginhawa siyang naninirahan.",
    ])
    def test_clean_line_preserved(self, inp: str) -> None:
        assert he._clean_sentence_text(inp) == inp


class TestPhase9kRegressionStillHolds:
    """Phase 9.K patterns continue to be rejected after the 9.L
    extension."""

    @pytest.mark.parametrize("inp", [
        "Sumakay ng motors€clo si David.",
        "Nginttian n£ Amor si Marco.",
        "Kumain ka ng san\\palok.",
    ])
    def test_9k_pattern_still_rejected(self, inp: str) -> None:
        assert he._clean_sentence_text(inp) is None


class TestPhase9lEndToEnd:
    """End-to-end via ``extract_ramos1971()`` — verify the post-9.L
    Ramos corpus carries no & / mid-word-digit / slash-single-letter
    OCR-garbled lines."""

    @pytest.mark.slow
    def test_no_ampersand_mid_word_in_corpus(self) -> None:
        import re
        bad = re.compile(r"\w&\w")
        for ex in he.extract_ramos1971():
            assert not bad.search(ex.text_raw), (
                f"& mid-word leaked: {ex.locator} {ex.text_raw!r}"
            )

    @pytest.mark.slow
    def test_no_digit_mid_lowercase_in_corpus(self) -> None:
        import re
        bad = re.compile(r"[a-z][0-9][a-z]")
        for ex in he.extract_ramos1971():
            assert not bad.search(ex.text_raw), (
                f"digit mid-word leaked: {ex.locator} {ex.text_raw!r}"
            )

    @pytest.mark.slow
    def test_no_slash_single_letter_in_corpus(self) -> None:
        import re
        bad = re.compile(r"[a-z]/[a-z](?![a-z])")
        for ex in he.extract_ramos1971():
            assert not bad.search(ex.text_raw), (
                f"slash+single-letter leaked: "
                f"{ex.locator} {ex.text_raw!r}"
            )
