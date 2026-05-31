# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-9: wave-2/3 OCR cleanup pass.

The corpus reference ``.txt`` files in ``data/tgl/references/`` are
gitignored. Phase 9.X.pre-3 established the workflow: targeted
surface-level OCR substitutions on those .txt files, then
re-extract the .jsonl exemplars (also gitignored), then re-audit.
The fixes themselves are personal-machine state, so this test file
is the only git-visible artifact of the cleanup.

This module asserts that a representative subset of OCR-corrected
surfaces parses successfully under the post-9 corpus state. Each
sentence below previously appeared in the wave-2/3 ZPF residue at
the post-8.5.8 baseline as an OCR-damaged surface; the cleanup
corrected the surface text, and the corrected sentence now parses.

## Audit numbers (post-8.5.8 → post-9)

* Wave 1 exemplars             : 106/123 unchanged (no regression)
* Wave 2 ramos1971             : 75/209  → 78/209  (+3)
* Wave 2 rc1990                : 217/1022 → 218/1022 (+1)
* Wave 2 rg-intermediate       : 464/1919 → 465/1919 (+1)
* Wave 3 rg-conversational     : 316/666  → 321/666  (+5)
* Wave 3 so1972                : 299/1265 → 312/1265 (+13)
* Wave 4 kroeger1991           : 54/215   unchanged
* Wave 5 zamar2023             : 149/498  unchanged
* Unattributed                 : 145/145  unchanged
* XWAVE TOTAL                  : 1824/6055 → 1848/6062 (+24 abs, +23 text-keyed)

## Fix categories

* Colon-for-`a` OCR: ``M:iynila`` → ``Maynila``; ``Siy:i`` → ``Siya``
  ``Kamukh:i`` → ``Kamukha``; ``Tawagan natin si Helen``; …
* Letter-pair OCR: ``Sumulal`` → ``Sumulat``; ``aJam`` → ``alam``;
  ``Jyon`` → ``Iyon``; ``s1Juan`` → ``si Juan``
* Digit-for-letter OCR: ``a11g`` → ``ang``; ``hi11di`` → ``hindi``;
  ``M3ria`` → ``Maria``; ``S3 palengke`` → ``sa palengke``;
  ``t1•ak`` → ``trak``
* Parens / token-join cleanup: ``(Amerikano nga si Jorge)`` →
  ``Amerikano nga si Jorge``; ``Bibilhins:manila`` → ``Bibilhin sa
  Manila``; ``kulang:mgpera`` → ``kulang ang pera``

The fix table is held in the gitignored ``tmp/post9_ocr_fixes.py``;
this test pins a sample of the resulting parse-success surfaces so
later work doesn't lose them silently.
"""

from tgllfg.core.pipeline import parse_text


class TestSO1972ColonOCRClosures:
    """S&O 1972 — colon-for-`a` and related OCR-noise closures."""

    def test_maynila_ang_bayan_ko(self) -> None:
        """Was ``M:iynila ang bayan ko.`` → ``Maynila ang bayan ko.``."""
        assert parse_text("Maynila ang bayan ko.", n_best=1)

    def test_tawagan_natin_si_helen(self) -> None:
        """Was ``Taw:igan natin si Helen.``."""
        assert parse_text("Tawagan natin si Helen.", n_best=1)

    def test_mahal_ang_damit_na_ito(self) -> None:
        """Was ``Mahal ang d:imit na ito.``."""
        assert parse_text("Mahal ang damit na ito.", n_best=1)

    def test_kailangan_ng_amerikano_iyon(self) -> None:
        """Was ``Kailangan ng Amerik:mo iyon.``."""
        assert parse_text("Kailangan ng Amerikano iyon.", n_best=1)

    def test_nakita_ko_lalaki_at_si_juan(self) -> None:
        """Was ``Nakita ko ang l:tlaki at si Juan.``."""
        assert parse_text("Nakita ko ang lalaki at si Juan.", n_best=1)


class TestSO1972LetterPairOCRClosures:
    """S&O 1972 — letter-pair OCR-noise closures."""

    def test_sumulat_si_juan_kahapon(self) -> None:
        """Was ``Sumulal ng liham kay Maria s1Juan k:ihapon.``."""
        assert parse_text(
            "Sumulat ng liham kay Maria si Juan kahapon.", n_best=1,
        )

    def test_sasayaw_din_sila(self) -> None:
        """Was ``Sasayaw din sil:i ng pand:inggo bukas ng gabi.``."""
        assert parse_text(
            "Sasayaw din sila ng pandanggo bukas ng gabi.", n_best=1,
        )

    def test_ako_sana_ang_yumaman(self) -> None:
        """Was ``Ako S3na ang yumaman.``."""
        assert parse_text("Ako sana ang yumaman.", n_best=1)

    def test_juan_bukas_ng_gabi(self) -> None:
        """Was ``...ni Jua11bttkas ng gabi.``."""
        assert parse_text(
            "Darating ang doktor sa bahay ni Juan bukas ng gabi.",
            n_best=1,
        )

    def test_makararating_ba_tayo(self) -> None:
        """Was ``Makararaling ba tayo S3 palengke?``."""
        assert parse_text(
            "Makararating ba tayo sa palengke?", n_best=1,
        )


class TestRGConversationalClosures:
    """R&G Conversational — alnum and colon OCR closures.

    The ``kapete:ya`` → ``kapeterya`` fix lands in the source .txt
    but the corrected sentence ``Naghahapunan ako sa kapeterya ng
    alas sais.`` does not close because ``kapeterya`` is not in lex.
    The original ZPF parse-success bucket was an artifact of the
    OCR-unknown drop. This is the post-8.2 lesson redux: lex
    additions (or OCR fixes that admit a token to the parser's
    vocab path) can flip an OCR-damaged sentence from
    ``parse-success`` (via ``_UNK``-drop) to honest ZPF. Per
    anti-deferral discipline, ``kapeterya`` NOUN is a lex-addition
    candidate for a future sub-PR — not in scope for an OCR-only
    cleanup pass.
    """

    def test_ituro_mo_ang_noo_mo(self) -> None:
        """Was ``Ituro mo ang noo m6.``."""
        assert parse_text("Ituro mo ang noo mo.", n_best=1)

    def test_alin_ang_libro_mo(self) -> None:
        """Was ``A1.in ang 1.ibro mo?``."""
        assert parse_text("Alin ang libro mo?", n_best=1)

    def test_pakiabot_mo_ang_libro_sa_mesa(self) -> None:
        """Was ``Pakiabot m6 ang libr6 sa mesa.``."""
        assert parse_text("Pakiabot mo ang libro sa mesa.", n_best=1)


class TestRG_IntermediateClosures:
    """R&G Intermediate — alnum-mash OCR closures."""

    def test_tumawag_ka_ng_trak(self) -> None:
        """Was ``Tumawag ka ng t1•ak.``."""
        assert parse_text("Tumawag ka ng trak.", n_best=1)


class TestRC1990Closures:
    """RC1990 — parens removal closures."""

    def test_oo_amerikano_nga_si_jorge(self) -> None:
        """Was ``Oo, (Amerikano nga si Jorge).``."""
        assert parse_text("Oo, Amerikano nga si Jorge.", n_best=1)

    def test_hiniram_ko_ang_bisikleta(self) -> None:
        """Was ``(hiramj ko ang bisikleta para sa kaniya.``."""
        assert parse_text(
            "Hiniram ko ang bisikleta para sa kaniya.", n_best=1,
        )


class TestAntiRegression:
    """Spot-check that nothing in the wave-1 baseline regressed.

    Wave-1 has no OCR damage (hand-transcribed source); the audit
    count stays at 106/123. These two pin specific canonical wave-1
    surfaces that should never regress.
    """

    def test_ang_manok_sent1_preserved(self) -> None:
        """Phase 9 wave-1 ANG MANOK sent-1 canonical surface."""
        assert parse_text(
            "May isang mamang nakatira sa isang bahay sa bukid.",
            n_best=1,
        )

    def test_ang_pamilya_sent14_preserved(self) -> None:
        """Phase 10.J.post-8.5.5.1 PAMILYA sent-14 closure stays in
        place (the ``lalo na't`` + multi-NP coord construction)."""
        assert parse_text(
            "Kasama rin sa pag-aalala ng pamilya ang lolo at lola, "
            "ang mga kapatid ng ama at ina, lalo na't ang mga ito'y "
            "nakababata.",
            n_best=1,
        )
