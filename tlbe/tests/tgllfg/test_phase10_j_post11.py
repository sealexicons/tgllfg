# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-11: ADJ-pred + DAT-NP adjunct + companion lex.

Discovered while probing wave-1 residue post-PR-#175: there was no
chart rule for the canonical ``S → ADJ[PREDICATIVE] NP[CASE=NOM]
NP[CASE=DAT]`` shape, so ``Masaya ako sa Maynila.`` and
``Mahilig siya sa adobo.`` fragmented. With ``ang``-NP subjects
the construction was masked because the ``sa``-PP attached
NP-internally as an N-modifier; pronouns can't carry that
modifier so the construction surfaces as matrix-S-with-adjunct,
which had no rule.

(Sub-PR labelled ``post-11``; the earlier ``post-10`` ANG
NADADALIAN closure shipped out-of-order at PR #165 / commit
``c04bbcd`` before post-8.X / post-9, so this is the next
chronological slot in the dot-numbered ``post-N`` sequence.)

## Rules added (cfg/clause.py)

* ``S → ADJ[PREDICATIVE] NP[CASE=NOM] NP[CASE=DAT]`` — companion
  to the base bare-NOM ADJ-predicate rule
* ``S → ADV NP[CASE=NOM] NP[CASE=DAT]`` — companion to the base
  bare-NOM ADV-predicate rule (required for the
  ``v_collab_redup`` cell output ``tulungtulong`` which is
  POS=ADV not ADJ)

Both rules attach the DAT-NP as ADJUNCT (mirrors the V-AV
companion rule at clause.py:87).

## Lex additions

* ``gawain`` NOUN — "task / chore / work / assignment" (deverbal
  from ``gawa`` via ``-in`` instrument suffix, semantically
  narrowed). Tier-1 lexicalized abstract noun per post-8.5.7
  convention.
* ``hanap`` VERB gains ``pag_gerund`` opt-in — produces
  ``paghahanap`` + ``paghanap`` (NOUN). Required for the
  ``paghahanap-buhay`` N-N compound (productively composes via
  the post-8.5.8 N-N compound rule).
* ``lalake`` NOUN — orthographic variant of ``lalaki`` (Kroeger
  1991 spelling), via ``LEMMA: lalaki`` per orthographic-variant
  convention.
* ``Intsik`` NOUN — ethnonym "Chinese person".
* ``internet`` NOUN — English loanword (modern Tagalog).

## Transcription fix

``data/tgl/references/transcriptions/rg81-excerpts.md`` line 150:
``pahahanap-buhay`` → ``paghahanap-buhay`` (user-verified
2026-05-30 from R&G 1981 PDF screenshot). The hand-transcription
typo (missing ``g`` in ``pag-`` gerund prefix) blocked
PAMILYA/sent-18 closure.

## Audit (post-9 → post-11)

* Wave 1 exemplars             : 106/123 → 107/123 (+1 — sent-18)
* Wave 2 ramos1971             :  78/209 unchanged
* Wave 2 rc1990                : 218/1022 → 219/1022 (+1)
* Wave 2 rg-intermediate       : 465/1919 → 474/1919 (+9)
* Wave 3 rg-conversational     : 321/666  → 322/666  (+1)
* Wave 3 so1972                : 312/1265 → 314/1265 (+2)
* Wave 4 kroeger1991           :  54/215  → 58/215   (+4 — lalake)
* Wave 5 zamar2023             : 149/498  → 151/498  (+2 — internet)
* Unattributed                 : 145/145  unchanged
* XWAVE TOTAL                  : 1848 → 1868 (+20 absolute)
* True regressions (text-keyed) : 0
"""

from tgllfg.core.pipeline import parse_text


class TestADJPredDATAdjunct:
    """ADJ-pred + PRON-NOM + sa-PP DAT-adjunct closures."""

    def test_masaya_ako_sa_maynila(self) -> None:
        """``Masaya ako sa Maynila.`` — bare canonical."""
        assert parse_text("Masaya ako sa Maynila.", n_best=1)

    def test_maganda_siya_sa_maynila(self) -> None:
        assert parse_text("Maganda siya sa Maynila.", n_best=1)

    def test_mahilig_siya_sa_adobo(self) -> None:
        """``Mahilig siya sa adobo.`` — ADJ with subcategorized
        DAT-OBL argument (the food liked); DAT lands in ADJUNCT
        slot under the matrix-adjunct analysis (subcategorization
        refinement parked for a future PR — ADJUNCT is the
        functional-equivalent slot today)."""
        assert parse_text("Mahilig siya sa adobo.", n_best=1)

    def test_masaya_siya_sa_kapatid(self) -> None:
        assert parse_text("Masaya siya sa kapatid.", n_best=1)

    def test_dat_coord(self) -> None:
        """``Masaya ako sa Maynila at sa Cebu.`` — DAT-coord still
        works (rides the standard NP[CASE=DAT] coord)."""
        assert parse_text(
            "Masaya ako sa Maynila at sa Cebu.", n_best=1,
        )


class TestADVPredDATAdjunct:
    """ADV-pred + PRON-NOM + sa-PP DAT-adjunct closures (parallel
    to the ADJ-pred + DAT rule, for ``v_collab_redup`` cell output
    which is POS=ADV not ADJ)."""

    def test_tulung_tulong_sila_sa_gawain(self) -> None:
        """``Tulung-tulong sila sa mga gawain.`` — ADV-pred (collab
        redup) + PRON-NOM + DAT."""
        assert parse_text("Tulung-tulong sila sa mga gawain.", n_best=1)

    def test_tulung_tulong_dat_coord(self) -> None:
        """``Tulung-tulong sila sa mga gawain at sa hanapbuhay.``
        — ADV-pred + DAT-coord."""
        assert parse_text(
            "Tulung-tulong sila sa mga gawain at sa hanapbuhay.",
            n_best=1,
        )


class TestPAMILYASent18Closure:
    """Wave-1 closure target — PAMILYA/sent-18 from R&G 1981
    transcription. Requires four coordinated fixes: (a) ADV-pred
    + DAT rule, (b) ``gawain`` NOUN lex, (c) ``hanap``
    pag_gerund opt-in producing ``paghahanap`` (then the
    post-8.5.8 N-N compound rule composes ``paghahanap-buhay``),
    (d) rg81-excerpts.md transcription fix (``pahahanap-buhay``
    → ``paghahanap-buhay``, user-PDF-verified)."""

    def test_pamilya_sent18_full(self) -> None:
        """``Tulung-tulong sila sa mga gawain at sa paghahanap-buhay.``"""
        assert parse_text(
            "Tulung-tulong sila sa mga gawain at sa paghahanap-buhay.",
            n_best=1,
        )


class TestLexAdditions:
    """New lex entries close audit sentences in waves 2/3/4/5."""

    def test_gawain_in_clause(self) -> None:
        """``Maganda ang gawain.`` — gawain NOUN lex."""
        assert parse_text("Maganda ang gawain.", n_best=1)

    def test_hanap_pag_gerund_paghahanap(self) -> None:
        """``Maganda ang paghahanap.`` — paghahanap NOUN derived
        via the pag_gerund cell (with CV-redup)."""
        assert parse_text("Maganda ang paghahanap.", n_best=1)

    def test_hanap_pag_gerund_paghanap(self) -> None:
        """``Maganda ang paghanap.`` — paghanap NOUN derived via
        the pag_gerund cell (no CV-redup)."""
        assert parse_text("Maganda ang paghanap.", n_best=1)

    def test_lalake_orthographic_variant(self) -> None:
        """``Bumili ang lalake ng isda.`` — lalake variant of
        lalaki (Kroeger 1991 spelling)."""
        assert parse_text("Bumili ang lalake ng isda.", n_best=1)

    def test_intsik_in_clause(self) -> None:
        """``Matatalino ang mga Intsik.``"""
        assert parse_text("Matatalino ang mga Intsik.", n_best=1)

    def test_internet_in_dat(self) -> None:
        """``Binili ko iyan sa internet.`` — internet NOUN."""
        assert parse_text("Binili ko iyan sa internet.", n_best=1)


class TestAntiRegression:
    """Spot-checks that the new rules don't break existing
    constructions or unmask hidden spurious ambiguities."""

    def test_masaya_ang_lalaki_sa_maynila_still_parses(self) -> None:
        """``Masaya ang lalaki sa Maynila.`` — with ang-NP SUBJ,
        the sa-PP attaches NP-internally as an N-modifier; the
        new matrix-adjunct rule is ALSO licit (the surface is
        genuinely ambiguous between "the man-in-Manila is happy"
        and "the man is happy in-Manila"). Both readings are
        valid Tagalog analyses; downstream ranker / context picks.
        Asserts at least one parse."""
        assert parse_text("Masaya ang lalaki sa Maynila.", n_best=2)

    def test_masaya_ako_bare_preserved(self) -> None:
        """Bare ``Masaya ako.`` continues to parse without the
        new rule firing (which requires a DAT-NP daughter)."""
        assert parse_text("Masaya ako.", n_best=1)

    def test_tulung_tulong_sila_bare_preserved(self) -> None:
        """Bare ``Tulung-tulong sila.`` (ADV + NOM only, no DAT)
        still parses via the base ADV-pred rule."""
        assert parse_text("Tulung-tulong sila.", n_best=1)

    def test_wave1_ang_manok_sent1_preserved(self) -> None:
        """Wave-1 ANG MANOK sent-1 canonical surface."""
        assert parse_text(
            "May isang mamang nakatira sa isang bahay sa bukid.",
            n_best=1,
        )

    def test_wave1_pamilya_sent14_preserved(self) -> None:
        """Phase 10.J.post-8.5.5.1 PAMILYA/sent-14 closure stays."""
        assert parse_text(
            "Kasama rin sa pag-aalala ng pamilya ang lolo at lola, "
            "ang mga kapatid ng ama at ina, lalo na't ang mga ito'y "
            "nakababata.",
            n_best=1,
        )
