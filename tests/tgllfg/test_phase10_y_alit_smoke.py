# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.Y C6: ``alit`` VERB ("quarrel") smoke.

This was the canonical motivating case for Phase 10.Y: the 10.E.6
deferral noted that adding ``alit`` as a mag-class VERB collides
with ``galit`` "anger" under hyphenless prefix-concat (both produce
``nagalit``). 10.Y moves the ``mag``/``nag``/``pag`` family to
hyphenated-only canonical surfaces, so ``mag-alit`` (the new
``alit`` VERB) and ``magalit`` (the existing ``galit`` ADJ-
predicative) live under DISTINCT surface keys. The same
disambiguation applies to ``nag-alit`` (``alit`` AV-PFV) vs
``nagalit`` (``galit`` AV-NVOL-PFV "got angry").

C5's collision sentry pins the lookup invariant; C6 here adds an
end-to-end parse smoke. Together they confirm the deferral
identified in 10.E.6 is unblocked.

References:
* S&O 1972 §3.10 (mag-V symmetric / reciprocal class)
* K&Z 1989 §2.4 (reciprocal voice)
* 10.E.6 close-out note (the deferral motivation)
"""

import pytest

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import Analyzer


@pytest.fixture(scope="module")
def analyzer() -> Analyzer:
    return Analyzer.from_default()


# === Lex-level smoke ====================================================


class TestAlitLexLevel:
    """The new ``alit`` VERB is indexed under the canonical
    hyphenated forms (``mag-alit`` / ``nag-alit`` / ``mag-aalit`` /
    ``nag-aalit``) — NOT under hyphenless variants, which would
    collide with ``galit``'s paradigm output."""

    @pytest.mark.parametrize(
        "surface,expected_aspect",
        [
            ("nag-alit",   "PFV"),
            ("nag-aalit",  "IPFV"),
            ("mag-aalit",  "CTPL"),
            ("mag-alit",   "INF"),    # or CTPL-SOC; both OK
        ],
    )
    def test_alit_canonical_surfaces_in_verb_forms(
        self, analyzer: Analyzer, surface: str, expected_aspect: str,
    ) -> None:
        """Each canonical hyphenated surface lives in verb_forms and
        carries the ``alit`` lemma. (We don't pin the exact ASPECT
        since the mag-class paradigm produces a few overlapping
        ASPECT/MOOD tuples per surface; just confirm ``alit`` is
        the lemma.)"""
        assert surface in analyzer._index.verb_forms, (
            f"{surface!r} should be indexed for the new alit VERB"
        )
        verbs = analyzer._index.verb_forms[surface]
        lemmas = {v.lemma.lower() for v in verbs}
        assert "alit" in lemmas, (
            f"{surface!r} should carry lemma=alit; got lemmas {lemmas}"
        )

    @pytest.mark.parametrize(
        "hyphenless_surface",
        [
            # mag/nag/pag family is hyphenated-only — these are NOT
            # back-compat keys for the new alit VERB.
            "nagalit",   # already galit AV-NVOL-PFV
            "nagaalit",
            "magaalit",
            "magalit",   # already galit ma-ADJ-predicative
        ],
    )
    def test_alit_hyphenless_surface_does_not_carry_alit(
        self, analyzer: Analyzer, hyphenless_surface: str,
    ) -> None:
        """Hyphenless input must NOT resolve to ``alit`` (only to
        ``galit`` / whichever pre-existing analysis was there)."""
        verbs = analyzer._index.verb_forms.get(hyphenless_surface, [])
        adjs = analyzer._index.adjectives.get(hyphenless_surface, [])
        all_lemmas = {x.lemma.lower() for x in verbs + adjs}
        assert "alit" not in all_lemmas, (
            f"hyphenless {hyphenless_surface!r} unexpectedly carries "
            f"alit reading; lemmas: {all_lemmas}"
        )


# === Sentence-level parse smoke =========================================


class TestAlitParseSmoke:
    """End-to-end: sentences with the new ``alit`` VERB parse."""

    @pytest.mark.parametrize(
        "sent",
        [
            "Nag-alit sila.",                    # PFV plural NOM
            "Nag-aalit sila.",                   # IPFV
            "Mag-aalit sila bukas.",             # CTPL
        ],
    )
    def test_alit_av_parses(self, sent: str) -> None:
        parses = parse_text(sent, n_best=1)
        assert len(parses) >= 1, (
            f"alit VERB clause should parse: {sent!r}"
        )


# === Anti-regression: galit still works =================================


class TestGalitUnchanged:
    """Adding ``alit`` must NOT regress ``galit``: ``magalit`` /
    ``nagalit`` / their f-structures stay routed to ``galit``."""

    @pytest.mark.parametrize(
        "sent",
        [
            "Galit si Maria.",       # bare ADJ predicative
            "Magalit si Maria.",     # ma-ADJ predicative
            "Nagalit si Maria.",     # AV-NVOL "got angry"
        ],
    )
    def test_galit_clauses_parse(self, sent: str) -> None:
        parses = parse_text(sent, n_best=1)
        assert len(parses) >= 1, (
            f"galit clause should still parse: {sent!r}"
        )
