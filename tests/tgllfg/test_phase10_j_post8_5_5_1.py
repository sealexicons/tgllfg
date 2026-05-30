# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-8.5.5.1: PAMILYA/sent-14 closure.

Closes PAMILYA/sent-14 ``Kasama rin sa pag-aalala ng pamilya ang
lolo at lola, ang mga kapatid ng ama at ina, lalo na't ang mga
ito'y nakababata.`` — wave-1 88/123 → 89/123 (84.55% → 85.37%).

Three mechanisms layered:

1. **`lalo na't S` SubordClause** (chart rule + pipeline-level fast
   path). Reason-emphasis discourse marker introducing a clause-final
   adjunct. Lexicalized as ``PART[LEMMA=lalo] PART[LINK=NA]
   PART[COORD=AND] S`` (the apostrophe pre-pass normalizes ``na't``
   to ``na`` + ``at``; the 9.X.c20 clitic-placement disambiguator
   forces post-lalo ``na`` to LINK=NA).

2. **`Kasama sa X` matrix-LOC variant** (chart rule). Parallel to
   the existing ``S → N NP[GEN] NP[NOM]`` rule (kasama+companion),
   adds ``S → N NP[DAT] NP[NOM]`` with the DAT-NP bound as LOC.
   Tightly gated to ``(↓1 KA_PRED) =c true`` so only ka-N companion
   nominals (kasama / kasabay / katabi) can head the construction.

3. **`pag-aalala` paradigm** (alala opts into pag_gerund). The
   nominalization ``pag- + cv-redup + alala = pagaalala``
   (canonical), accepting the hyphenated written form ``pag-aalala``
   via the tokenizer's hyphen-merge pre-pass.

4. **SUBJ-bare-comma 2-way coord** (pipeline-level fast path —
   NOT chart-level). The ``<pred> ang X, ang Y`` pattern has ZERO
   attestations in waves 1-5 outside the PAMILYA/sent-14 lalo-na't
   context (attributed-exemplar scan, post-8.5.5.1 development).
   Therefore, the synthesis is scoped to ``_try_lalo_nat_split``'s
   pre-half fallback: only when text contains ``, lalo na 't `` AND
   the pre-half S parse fails, the deeper SUBJ-bare-comma split
   activates. This avoids polluting the chart grammar with a
   construction that has no broader corpus support.

## Anti-regression discipline

The chart's existing NP-coord rules (binary at-coord, 3-flat Oxford
/ non-Oxford, 4+ NP_LONG_LIST) remain untouched — no new gates, no
new features. The 3-conjunct non-Oxford test (``Kumain si Maria,
si Juan at si Pedro.``) continues to produce exactly 1 flat
3-conjunct parse.

## Audit signal (post-8.5.5 → post-8.5.5.1)

Targeted PAMILYA/sent-14 closure: wave-1 +1 → 89/123. Other waves
unchanged (the lalo-na't and KA_PRED+DAT shapes don't attest
elsewhere; corpus scan confirms).
"""

from tgllfg.core.pipeline import parse_text


class TestLaloNatSubordClause:
    """Chart-level ``SubordClause → PART[lalo] PART[LINK=NA]
    PART[COORD=AND] S`` (subordination.py:543+) + matrix-attach via
    the existing ``S → S COMMA SubordClause`` rule."""

    def test_lalo_nat_simple(self) -> None:
        """Simplest case — matrix-S + comma + lalo-na't + body S."""
        parses = parse_text(
            "Maganda siya, lalo na't ang anak ay matalino.", n_best=1,
        )
        assert len(parses) >= 1

    def test_lalo_nat_with_at_form(self) -> None:
        """``lalo na at`` (explicit ``at`` instead of ``'t``)
        should parse identically — the apostrophe pre-pass
        normalizes ``'t`` to ``at``."""
        parses = parse_text(
            "Maganda siya, lalo na at ang anak ay matalino.", n_best=1,
        )
        assert len(parses) >= 1


class TestKasamaSaMatrixLoc:
    """Chart-level ``S → N NP[CASE=DAT] NP[CASE=NOM]`` rule
    (clause.py) gated to ``KA_PRED=c true``. Parallel to the
    existing GEN-companion variant."""

    def test_kasama_sa_simple(self) -> None:
        """``Kasama sa pamilya ang ina.`` — basic KA_PRED+DAT-LOC+NOM."""
        parses = parse_text("Kasama sa pamilya ang ina.", n_best=1)
        assert len(parses) >= 1

    def test_kasama_ng_preserved(self) -> None:
        """The existing GEN-companion variant continues to parse —
        the new DAT-LOC rule is additive."""
        parses = parse_text("Kasama ng aso ang pusa.", n_best=1)
        assert len(parses) >= 1

    def test_kasabay_sa_dat_variant(self) -> None:
        """``kasabay`` also has KA_PRED=true; same DAT-LOC rule fires."""
        parses = parse_text("Kasabay sa pamilya ang ama.", n_best=1)
        assert len(parses) >= 1


class TestAlalaPagGerund:
    """``alala`` opts into ``pag_gerund``: ``pagaalala`` / ``pag-aalala``
    canonical nominalization."""

    def test_pagaalala_in_dat_pp(self) -> None:
        """``sa pag-aalala ng pamilya`` — the hyphenated written
        form is tokenizer-normalized to ``pagaalala`` via the
        hyphen-merge pre-pass."""
        parses = parse_text(
            "Kasama sa pag-aalala ng pamilya ang ina.", n_best=1,
        )
        assert len(parses) >= 1

    def test_pagaalala_unhyphenated(self) -> None:
        parses = parse_text(
            "Kasama sa pagaalala ng pamilya ang ina.", n_best=1,
        )
        assert len(parses) >= 1


class TestSubjBareCommaPipelineSynthesis:
    """Pipeline-level SUBJ-bare-comma fallback inside
    ``_try_lalo_nat_split`` (pipeline.py). Activates only when the
    pre-lalo-na't half itself ZPFs — corpus-scoped to PAMILYA/sent-14
    shapes."""

    def test_pamilya_sent14_full(self) -> None:
        """The full PAMILYA/sent-14."""
        parses = parse_text(
            "Kasama rin sa pag-aalala ng pamilya ang lolo at lola, "
            "ang mga kapatid ng ama at ina, lalo na't ang mga ito'y "
            "nakababata.",
            n_best=1,
        )
        assert len(parses) >= 1

    def test_pamilya_sent14_simpler(self) -> None:
        """A simpler variant with the same coord-SUBJ + lalo-na't
        shape."""
        parses = parse_text(
            "Kasama ang lolo at lola, ang mga kapatid ng ama at ina, "
            "lalo na't ang mga ito'y nakababata.",
            n_best=1,
        )
        assert len(parses) >= 1


class TestAntiRegression:
    """The pipeline-only approach preserves all existing chart
    behavior — no chart-rule additions to NP-coord, no gates on
    existing at-coord rules."""

    def test_three_conjunct_non_oxford_unchanged(self) -> None:
        """``Kumain si Maria, si Juan at si Pedro.`` — 3-flat
        non-Oxford continues to produce exactly 1 parse with 3
        flat conjuncts."""
        parses = parse_text(
            "Kumain si Maria, si Juan at si Pedro.", n_best=10,
        )
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        conj = subj.feats.get("CONJUNCTS")
        assert conj is not None and len(conj) == 3

    def test_ten_conjunct_unchanged(self) -> None:
        """10-conjunct non-Oxford continues to flat-parse."""
        parses = parse_text(
            "Kumain ang tatay, ang nanay, ang kuya, ang ate, "
            "ang lolo, ang lola, ang tito, ang tita, "
            "ang pinsan at ang kapatid."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        conj = subj.feats.get("CONJUNCTS")
        assert conj is not None and len(conj) == 10

    def test_standalone_bare_comma_2way_zpfs(self) -> None:
        """``Kasama ang lolo, ang ama.`` ZPFs standalone — the
        pipeline-level synthesis only fires inside the lalo-na't
        context (corpus-scoped). Standalone bare-comma 2-way is
        unattested in waves 1-5."""
        parses = parse_text("Kasama ang lolo, ang ama.", n_best=1)
        assert len(parses) == 0
