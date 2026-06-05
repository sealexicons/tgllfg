# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 8.L Commit 2: magkakasing- intensive distributive equative.

The ``magkakasing-`` prefix is the 3+-comparee intensive form of
``magkasing-`` (Phase 8.L Commit 1). S&O 1972 §5 documents that
"magkasing- is duplicated, the vowel or the duplicating syllable
being short: e.g., nagkakasingtalino" — i.e., the ``ka`` of
``magkasing-`` CV-reduplicates, yielding ``magka`` + ``ka`` +
``sing-`` + root. Semantically: ``magkakasing-X`` extends the
``magkasing-X`` equal-X-ness assertion to a set of three or more
comparees.

Wave 3 audit hit: S&O 1972 page 249 —
  ``Binigyan ng premyo ang lahat ng magkakasingbuti ng grado.``
  "All those who had equally good grades were given prizes."

The predicative ADJ ``magkakasingbuti`` selects the set of
comparees from the ``lahat ng ...`` floor-quantifier matrix NP.

The CV-redup is internal to the prefix (``ka`` → ``kaka``), not to
the root, so the cell is encoded as a single complex-prefix
operation rather than as ``cv_redup`` + ``magkasing`` (the L38
``cv_redup`` operation reduplicates the root, not the prefix).

The ADJ surfaces carry:
* ``COMP_DEGREE=EQUATIVE`` (shared with the ``magkasing-`` cell)
* ``DISTRIB=true`` (joint / multi-comparee semantics)
* ``INTENS=STRONG`` (the new STRONG value parallels the
  Phase 5n.C.3 ``redup_intens_adj`` cell's ``INTENS=MILD``)

The predicative-ADJ clause rule (Phase 5n.C.3 INTENS lift + Phase
8.L Commit 1 DISTRIB lift) propagates both INTENS and DISTRIB to
the matrix S so downstream consumers see the construction at
clause level.
"""

import pytest


class TestPhase8lMagkakasingProductive:
    """The ``magkakasing-`` cell fires on every ``ma_adj`` root."""

    @pytest.mark.parametrize("sentence,adj_lemma", [
        ("Magkakasingganda ang mga aso.", "ganda"),
        ("Magkakasingtaas ang mga aso.", "taas"),
        ("Magkakasinglaki ang mga aso.", "laki"),
        ("Magkakasingtalino sila.", "talino"),
    ])
    def test_magkakasing_fires(
        self, sentence: str, adj_lemma: str,
    ) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse for {sentence!r}"
        f = parses[0][1]
        assert str(f.feats.get("ADJ_LEMMA")) == adj_lemma, (
            f"{sentence!r} parsed but ADJ_LEMMA != {adj_lemma!r}"
        )


class TestPhase8lMagkakasingFeats:
    """Matrix carries DISTRIB=true and INTENS=STRONG."""

    def test_distrib_and_intens_lifted(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Magkakasingganda ang mga aso.", n_best=2)
        assert len(parses) >= 1
        f = parses[0][1]
        assert f.feats.get("DISTRIB") is True, (
            "DISTRIB=true expected on magkakasing- ADJ predicate"
        )
        assert str(f.feats.get("INTENS")) == "STRONG", (
            "INTENS=STRONG expected on magkakasing- ADJ predicate"
        )


class TestPhase8lMagkakasingVsMagkasing:
    """Surface contrast: ``magkasing-`` carries INTENS undefined;
    ``magkakasing-`` carries INTENS=STRONG. Both share DISTRIB=true."""

    def test_intens_distinguishes_the_two_cells(self) -> None:
        from tgllfg.core.pipeline import parse_text
        plain = parse_text("Magkasingganda ang mga aso.", n_best=2)
        intens = parse_text("Magkakasingganda ang mga aso.", n_best=2)
        assert plain and intens
        # Both DISTRIB
        assert plain[0][1].feats.get("DISTRIB") is True
        assert intens[0][1].feats.get("DISTRIB") is True
        # Only intens carries INTENS=STRONG
        assert plain[0][1].feats.get("INTENS") is None or (
            str(plain[0][1].feats.get("INTENS")) != "STRONG"
        )
        assert str(intens[0][1].feats.get("INTENS")) == "STRONG"


class TestPhase8lMagkakasingRegressions:
    """Phase 5n.C.3 ``INTENS=MILD`` regression (redup-intens-adj)
    and Phase 5h ``kasing-`` / ``sing-`` regressions stay intact."""

    @pytest.mark.parametrize("sentence", [
        # Phase 5n.C.3 §18 L37 redup-intens-adj
        "Magandaganda si Maria.",
        # Phase 5h kasing- / sing-
        "Kasingganda si Maria.",
        "Singganda si Maria.",
        # Phase 8.L Commit 1 magkasing-
        "Magkasingganda ang mga aso.",
        "Magkasingtaas si Maria at si Ana.",
    ])
    def test_regression_parses_unaffected(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"regression on {sentence!r}"
