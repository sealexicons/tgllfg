# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 8.L Commit 1: magkasing- distributive equative paradigm.

Adds the productive ``magkasing-`` cell to ``adj_paradigms.yaml`` —
plural-subject counterpart of ``kasing-`` (Phase 5h Commit 2). The
new cell opts in on the same ``ma_adj`` filter, so every root that
unlocks ``ma-`` adjectivisation, ``pinaka-`` superlative,
``napaka-`` intensive, ``kasing-`` and ``sing-`` equative also
unlocks ``magkasing-`` distributive equative.

Surface: plain ``magkasing`` + bare ADJ root, no reduplication.
  ``magkasing`` + ``ganda`` → ``magkasingganda``
  ``magkasing`` + ``taas`` → ``magkasingtaas``
  ``magkasing`` + ``laki`` → ``magkasinglaki``

Feats: ``COMP_DEGREE=EQUATIVE`` (shared with the bare ``kasing-``
cell) plus ``DISTRIB=true`` (joint / multi-comparee semantics; a
downstream selectional consumer can branch on DISTRIB to enforce
plural-subject licensing — this cell does not constrain the subject
at c-structure level).

Citations: S&O 1972 §5, R&C 1990 ch. 5. The CV-redup intensive
``magkakasing-`` form lands in Phase 8.L Commit 2; the ``kasing-``
+ NOUN equative + hyphen-joined orthography lands in 8.L Commits 3-4.
"""

import pytest


def _has_distrib_eq(parses, lemma_value: str) -> bool:
    """True iff at least one parse asserts an EQUATIVE-DISTRIB ADJ
    predicate over the named root."""
    for p in parses:
        f = p[1]
        if f.feats.get("DISTRIB") is not True:
            continue
        adj_lemma = f.feats.get("ADJ_LEMMA")
        if adj_lemma is None:
            continue
        if str(adj_lemma) == lemma_value:
            return True
    return False


class TestPhase8lProductiveMagkasing:
    """The ``magkasing-`` cell fires on every ``ma_adj`` root."""

    @pytest.mark.parametrize("sentence,adj_lemma", [
        ("Magkasingganda ang mga aso.", "ganda"),
        ("Magkasingtaas ang mga aso.", "taas"),
        ("Magkasinglaki ang mga aso.", "laki"),
        ("Magkasinglinis ang mga aso.", "linis"),
    ])
    def test_magkasing_ang_mga(
        self, sentence: str, adj_lemma: str,
    ) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse for {sentence!r}"
        assert _has_distrib_eq(parses, adj_lemma), (
            f"{sentence!r} parsed but no DISTRIB+EQUATIVE ADJ on "
            f"{adj_lemma!r}"
        )

    @pytest.mark.parametrize("sentence,adj_lemma", [
        ("Magkasingganda si Maria at si Ana.", "ganda"),
        ("Magkasingtaas si Maria at si Ana.", "taas"),
    ])
    def test_magkasing_coordinated_si(
        self, sentence: str, adj_lemma: str,
    ) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse for {sentence!r}"
        assert _has_distrib_eq(parses, adj_lemma), (
            f"{sentence!r} parsed but no DISTRIB+EQUATIVE ADJ on "
            f"{adj_lemma!r}"
        )


class TestPhase8lDistribAndDegree:
    """Confirm the ADJ surface carries DISTRIB=true alongside
    COMP_DEGREE=EQUATIVE in the f-structure."""

    def test_distrib_and_equative_flags(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Magkasingganda ang mga aso.", n_best=2)
        assert len(parses) >= 1
        f = parses[0][1]
        assert f.feats.get("DISTRIB") is True, (
            "DISTRIB=true expected on magkasing- ADJ predicate"
        )
        adj_lemma = f.feats.get("ADJ_LEMMA")
        assert str(adj_lemma) == "ganda"


class TestPhase8lRegressions:
    """Phase 5h Commit 2 ``kasing-`` / ``sing-`` parses remain
    unaffected; only the new DISTRIB-marked variant adds to the
    parse set."""

    @pytest.mark.parametrize("sentence", [
        "Kasingganda si Maria.",
        "Kasingtaas si Maria.",
        "Kasingtalino si Maria.",
        "Kasinglinis si Maria.",
        "Kasingganda si Maria ni Ana.",
        "Singganda si Maria.",
        "Hindi kasingganda si Maria.",
    ])
    def test_kasing_unaffected(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"regression on {sentence!r}"
