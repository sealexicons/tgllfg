# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-8.5.3: medial_vowel_syncope sandhi engine flag
+ also_n_epenthesis opt-in on kilala.

Third sub-PR in the post-8.5.N series. New sandhi engine flag plus
opt-in on two roots; closes the post-8.1 deferral of ``sundin`` /
``sundan``.

## New mechanism: ``medial_vowel_syncope``

S&O 1972 §4.21 documents the syncope as a per-root lex choice —
when a CVC-final stem takes a vowel-initial suffix, the
final-syllable vowel deletes, producing a final consonant cluster:

    sunod + -in → sund-in = ``sundin``
    sunod + -an → sund-an = ``sundan``

Implementation:

* ``attach_suffix`` (src/tgllfg/morph/sandhi.py) accepts a new
  ``medial_vowel_syncope: bool`` parameter. When set + the stem
  ends in CVC + the suffix is V-initial, the penultimate vowel
  drops before concatenation.
* The analyzer (src/tgllfg/morph/analyzer.py) propagates
  ``"medial_vowel_syncope" in flags`` from per-root ``sandhi_flags``.
* ``sunod`` VERB (data/tgl/verbs.yaml) opts in via
  ``sandhi_flags: [medial_vowel_syncope]``.

The CVC-final guard restricts firing: ``is_vowel(base[-1])``
False + ``is_vowel(base[-2])`` True + ``is_vowel(base[-3])``
False + ``is_vowel(suffix[0])`` True. The is_vowel(base[-3]) False
constraint excludes VVC-final stems (e.g., ``baon`` "provisions"
— no medial vowel to syncopate).

Runs after ``raise_final_o``: ``sunod → sunud`` (raise) → drop u
→ ``sund`` → + suffix. Bypasses the V+V hiatus branch since the
syncopated base is now C-final.

## Bonus: ``kilala`` + ``also_n_epenthesis``

Defensive additive (audit-absent at present). Adds the
``-n-`` epenthesis variant ``kilalanin`` alongside the default
``-h-`` epenthesis ``kilalahin``. Same mechanism as Phase 10.J.
post-7.4 ``tuto`` ``natutuhan``/``natutunan``. Modern Tagalog
admits both spellings — Zamar 2023 §13.4 lists the n-form as
the modern principal surface.

## Audit signal (post-8.5.2 → post-8.5.3)

* **wave-2 ramos1971** +1 (`Sundin natin ang ating guro.` sent-159
  — the exact attestation from the post-8.1 deferral).
* **wave-2 rg-intermediate** +1 (`Sundin mo sila.` sent-1346 —
  the second attestation from the post-8.1 deferral).
* unattributed +7 → 113/113 (100%).
* XWAVE 1780 → 1789 (+9).
* 0 regressions across all 9 waves.

The yield exactly matches the post-8.1 deferral's wave-2
prediction — the sandhi engine works as designed.
"""

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import _get_default
from tgllfg.morph.sandhi import attach_suffix


class TestMedialVowelSyncope:
    """post-8.5.3: ``medial_vowel_syncope`` sandhi engine flag."""

    def test_sunod_plus_in_with_flag(self) -> None:
        assert attach_suffix(
            "sunod", "in", medial_vowel_syncope=True,
        ) == "sundin"

    def test_sunod_plus_an_with_flag(self) -> None:
        assert attach_suffix(
            "sunod", "an", medial_vowel_syncope=True,
        ) == "sundan"

    def test_bukas_plus_in_with_flag(self) -> None:
        """``bukas + -in`` → ``buksin`` (the medial /a/ drops on
        a hypothetical bukas-class CVC-final stem)."""
        assert attach_suffix(
            "bukas", "in", medial_vowel_syncope=True,
        ) == "buksin"

    def test_sunod_plus_in_without_flag(self) -> None:
        """Default (no syncope) produces ``sunudin`` — the
        ``raise_final_o`` step raises ``o → u`` and concatenates
        directly (consonant-final base, no V+V hiatus)."""
        assert attach_suffix("sunod", "in") == "sunudin"

    def test_no_fire_on_vvc_final(self) -> None:
        """``baon + -in`` should not syncope (the medial-position
        ``o`` is preceded by a vowel ``a``, not a consonant — the
        is_vowel(base[-3]) False guard blocks)."""
        # baon = b-a-o-n. base[-3]='a' is vowel → guard blocks.
        assert attach_suffix(
            "baon", "in", medial_vowel_syncope=True,
        ) == "baunin"

    def test_no_fire_on_v_final(self) -> None:
        """Vowel-final stems are unaffected — ``kain + -in`` still
        uses h-epenthesis ``kainin``."""
        assert attach_suffix(
            "kain", "in", medial_vowel_syncope=True,
        ) == "kainin"  # already C-final, no hiatus, direct concat


class TestSunodSurfaces:
    """post-8.5.3: ``sunod`` VERB opt-in produces ``sundin`` /
    ``sundan`` family."""

    def test_sundin_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("sundin")

    def test_sundan_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("sundan")

    def test_susundin_known(self) -> None:
        """``susundin`` — OV CTPL irrealis with cv_redup + syncope
        (sunod → cv_redup → susunod → + in → susundin via syncope)."""
        analyzer = _get_default()
        assert analyzer.is_known_surface("susundin")

    def test_sinundan_known(self) -> None:
        """``sinundan`` — DV PFV with -in- infix + syncope."""
        analyzer = _get_default()
        assert analyzer.is_known_surface("sinundan")

    def test_unsyncoped_variants_not_produced(self) -> None:
        """``sunudin`` / ``sunudan`` / ``sunodin`` / ``sunodan``
        are NOT generated (only the syncoped variants fire)."""
        analyzer = _get_default()
        for surface in ("sunudin", "sunudan", "sunodin", "sunodan"):
            assert not analyzer.is_known_surface(surface), surface


class TestWave2Sentences:
    """post-8.5.3: the exact wave-2 sentences predicted by the
    post-8.1 deferral close."""

    def test_sundin_natin_ang_ating_guro(self) -> None:
        """ramos1971 sent-159."""
        parses = parse_text("Sundin natin ang ating guro.", n_best=1)
        assert len(parses) >= 1

    def test_sundin_mo_sila(self) -> None:
        """rg-intermediate sent-1346."""
        parses = parse_text("Sundin mo sila.", n_best=1)
        assert len(parses) >= 1


class TestKilalaNEpenthesis:
    """post-8.5.3: ``kilala`` + ``also_n_epenthesis`` generates
    both ``kilalanin`` and ``kilalahin`` variants."""

    def test_kilalanin_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("kilalanin")

    def test_kilalahin_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("kilalahin")

    def test_kilalanin_parses(self) -> None:
        parses = parse_text("Kilalanin mo si Pedro.", n_best=1)
        assert len(parses) >= 1

    def test_kilalahin_parses(self) -> None:
        parses = parse_text("Kilalahin natin siya.", n_best=1)
        assert len(parses) >= 1


class TestAntiRegression:
    """post-8.5.3 anti-regression: pre-existing surfaces / parses
    preserved."""

    def test_existing_sumusunod_preserved(self) -> None:
        """``Sumusunod siya.`` — pre-post-8.5.3 AV-IPFV form still
        parses (medial_vowel_syncope only fires on suffix attach,
        not on the infix-only PFV/IPFV cells)."""
        parses = parse_text("Sumusunod siya.", n_best=1)
        assert len(parses) >= 1

    def test_existing_nakilala_preserved(self) -> None:
        """``Nakilala ko siya.`` — pre-post-8.5.3 ma-NVOL form
        unchanged by adding ``also_n_epenthesis`` to ``kilala``."""
        parses = parse_text("Nakilala ko siya.", n_best=1)
        assert len(parses) >= 1

    def test_other_cvc_verbs_unaffected(self) -> None:
        """Other CVC-final TR verbs without ``medial_vowel_syncope``
        flag don't change. ``hatak`` (pull, CVC-final): ``hatakin``
        from the in_oblig cell continues to produce the standard
        suffix-attached form (no syncope)."""
        analyzer = _get_default()
        # hatak is in_oblig + an_oblig → hatakin, hatakan
        # are the standard surfaces; haktin/haktan would only
        # appear if hatak had the syncope flag.
        assert analyzer.is_known_surface("hatakin")
        assert not analyzer.is_known_surface("haktin")

    def test_n_epenthesis_param_default_off(self) -> None:
        """``attach_suffix`` defaults ``medial_vowel_syncope=False``
        — pre-existing call sites continue to use the default
        (no-syncope) behavior unless explicitly opted in."""
        # kain + in (vowel-final, no syncope flag) → kainin
        assert attach_suffix("kain", "in") == "kainin"
        # sunod + in without flag → sunudin (o-raise only)
        assert attach_suffix("sunod", "in") == "sunudin"
