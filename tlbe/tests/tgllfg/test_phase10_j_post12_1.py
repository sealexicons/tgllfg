# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-12.1: PAMILYA/sent-17 Kapag-fronted SubordClause.

First sub-PR in the post-12.N stack — closing all 16 remaining
wave-1 ZPFs in implementation-order, smallest-blast-radius first
(per user 2026-05-30 directive: anti-deferral required; if stuck,
converse before continuing).

Target: PAMILYA/sent-17
``Kapag ganitong kumpleto ang pamilya'y tatlong salin-lahi ang
nakatira sa iisang bahay.``  "When the family is this complete,
three generations live in one house."

## Gap analysis

Post-half ``Tatlong salin-lahi ang nakatira sa iisang bahay.``
parses (NUM-LINK-N + ang-RC). Pre-half
``Kapag ganitong kumpleto ang pamilya`` was missing two pieces:

1. **`kumpleto` ADJ lex** — Spanish-loan ``completo`` "complete /
   whole / full". Modern-Tagalog standard, not previously lex'd.
   Bare predicative ADJ, no affix-class extensions.

2. **Manner-DEM pre-ADJ modifier** (cfg/nominal.py) — the
   ``ganito`` / ``ganon`` / ``gayon`` family modifying an ADJ
   "to this/that extent" — a degree-DEM construction. Phase
   9.X.c28 added the parallel ``ganitong N`` rule; this PR adds
   the ADJ counterpart.

## Rule added (cfg/nominal.py)

``ADJ[PREDICATIVE] → PART PART[LINK={NA,NG}] ADJ[PREDICATIVE]``
gated by ``(↓1 LEMMA) =c '<ganito|ganon|gayon>'``. Matrix ADJ
inherits via ``(↑) = ↓3``; manner-DEM rides in ADJUNCT. Six rule
instances (3 lemmas × 2 linkers).

LHS category-pattern ``ADJ[PREDICATIVE]`` is critical: the matrix
must project as PREDICATIVE so the downstream ADJ-pred rule
(``S → ADJ[PREDICATIVE] NP[CASE=NOM]``) can consume it. Without
this category-feature propagation the rule fires but the wider
ADJ doesn't get picked up by the S rule (initial probe showed
two non-chaining fragments — the post-10 lesson about
category-feat propagation applies here too).

## Audit (post-11 → post-12.1)

* Wave 1 exemplars             : 107/123 → 108/123 (+1 — sent-17)
* Wave 2 ramos1971             :  78/209 unchanged
* Wave 2 rc1990                : 219/1022 unchanged
* Wave 2 rg-intermediate       : 474/1919 → 476/1919 (+2 — ganitong-ADJ broader reach)
* Wave 3 rg-conversational     : 322/666  unchanged
* Wave 3 so1972                : 314/1265 unchanged
* Wave 4 kroeger1991           :  58/215  unchanged
* Wave 5 zamar2023             : 151/498  unchanged
* Unattributed                 : 145/145  unchanged
* XWAVE TOTAL                  : 1868 → 1871 (+3 absolute)
* True regressions (text-keyed): 0
"""

from tgllfg.core.pipeline import parse_text


class TestPAMILYASent17Closure:
    """Wave-1 closure target."""

    def test_pamilya_sent17_full(self) -> None:
        """``Kapag ganitong kumpleto ang pamilya'y tatlong salin-lahi
        ang nakatira sa iisang bahay.`` — the full sentence."""
        assert parse_text(
            "Kapag ganitong kumpleto ang pamilya'y tatlong salin-lahi "
            "ang nakatira sa iisang bahay.",
            n_best=1,
        )

    def test_kapag_kumpleto_ang_pamilya_y_post_half_parses(self) -> None:
        """The simpler form with no manner-DEM also parses (sanity
        check that the apostrophe-ay + Kapag pieces compose)."""
        assert parse_text(
            "Kapag kumpleto ang pamilya'y tatlong salin-lahi "
            "ang nakatira sa iisang bahay.",
            n_best=1,
        )


class TestKumpletoLex:
    """``kumpleto`` ADJ lex addition."""

    def test_kumpleto_predicative(self) -> None:
        """``Kumpleto ang pamilya.`` — bare predicative ADJ."""
        assert parse_text("Kumpleto ang pamilya.", n_best=1)

    def test_kumpleto_ay_fronted(self) -> None:
        """``Ang pamilya ay kumpleto.`` — ay-fronted variant."""
        assert parse_text("Ang pamilya ay kumpleto.", n_best=1)

    def test_kumpleto_apostrophe_ay(self) -> None:
        """``Ang pamilya'y kumpleto.`` — apostrophe-ay (post-8.4
        clitic pre-pass)."""
        assert parse_text("Ang pamilya'y kumpleto.", n_best=1)


class TestMannerDEMOnADJ:
    """``ganitong / ganong / gayong + ADJ`` degree-DEM construction."""

    def test_ganitong_kumpleto(self) -> None:
        """``Ganitong kumpleto ang pamilya.`` — PROX manner-DEM."""
        assert parse_text("Ganitong kumpleto ang pamilya.", n_best=1)

    def test_ganitong_maganda(self) -> None:
        """``Ganitong maganda ang ina.`` — PROX manner-DEM + canonical
        ADJ."""
        assert parse_text("Ganitong maganda ang ina.", n_best=1)

    def test_ay_fronted_ganitong(self) -> None:
        """``Ang ina ay ganitong maganda.`` — ay-fronted form
        (manner-DEM-ADJ as ay-predicate)."""
        assert parse_text("Ang ina ay ganitong maganda.", n_best=1)


class TestKapagFrontedSubordClause:
    """``Kapag ADJ-pred-clause, main-clause`` SubordClause
    composing with the manner-DEM ADJ rule."""

    def test_kapag_ganitong_with_comma(self) -> None:
        """``Kapag ganitong kumpleto ang pamilya, tatlong
        salin-lahi ang nakatira sa iisang bahay.``"""
        assert parse_text(
            "Kapag ganitong kumpleto ang pamilya, tatlong salin-lahi "
            "ang nakatira sa iisang bahay.",
            n_best=1,
        )


class TestAntiRegression:
    """Existing ganitong + N rule (Phase 9.X.c28) preserved + base
    ADJ-pred rule preserved."""

    def test_ganitong_panahon_n_rule_preserved(self) -> None:
        """``Ganitong panahon ang Hunyo.`` — Phase 9.X.c28 manner-DEM
        + N rule still works (we added an ADJ companion; N rule
        unchanged)."""
        assert parse_text(
            "Ganitong panahon ang Hunyo.", n_best=1,
        )

    def test_bare_adj_pred_preserved(self) -> None:
        """``Maganda ang ina.`` — base ADJ-pred rule still works."""
        assert parse_text("Maganda ang ina.", n_best=1)

    def test_wave1_pamilya_sent14_preserved(self) -> None:
        """Phase 10.J.post-8.5.5.1 PAMILYA/sent-14 still parses."""
        assert parse_text(
            "Kasama rin sa pag-aalala ng pamilya ang lolo at lola, "
            "ang mga kapatid ng ama at ina, lalo na't ang mga ito'y "
            "nakababata.",
            n_best=1,
        )

    def test_wave1_pamilya_sent18_post11_preserved(self) -> None:
        """Phase 10.J.post-11 PAMILYA/sent-18 still parses."""
        assert parse_text(
            "Tulung-tulong sila sa mga gawain at sa paghahanap-buhay.",
            n_best=1,
        )
