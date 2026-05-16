"""Phase 8.L Commit 3: kasing-NOUN equative cell.

Adds the ``kasing_n_eq`` paradigm cell (paradigms.yaml) — a
NOUN→ADJ derivation that prefixes ``kasing-`` to a measurement-
attribute NOUN to produce an ADJ-shaped predicative-equative
surface:

  edad → kasingedad   "of the same age (as)"
  bigat → kasingbigat "of the same weight (as)"

The output ADJ carries:
* ``COMP_DEGREE: EQUATIVE`` (so the Phase 5h Commit 2 equative
  two-NP frame rules consume the surface unchanged)
* ``PREDICATIVE: true`` (so the Phase 5g predicative-adj clause
  rule fires on the surface)
* ``KASING_N: true`` (marker — surface originates from a NOUN
  base, distinguishing it from the ADJ-base ``kasing-`` cell of
  Phase 5h Commit 2). Lifted to matrix by Phase 8.L's
  predicative-ADJ rule extension alongside the equative-frame
  rules.

This commit also opens the cell with one NOUN opt-in (``edad`` —
the Wave 2/3 audit hit). Further NOUN opt-ins (``bigat``,
``haba``, ``tangkad``, ``tindi``, ``lakas``, ``tibay``,
``tigas``) land in Phase 8.L Commit 5 (lex pass).

The hyphen-joined orthographic variant ``Kasing-edad`` (the
audit's canonical surface — R&G Intermediate page 238) lands in
Phase 8.L Commit 4 as a c-structure rule, parallel to the 8.R
``alas-`` + NUM hyphen-joined N rule.
"""

from __future__ import annotations

import pytest


class TestPhase8lKasingNounSolid:
    """Solid-orthography ``kasingedad`` parses as predicative ADJ."""

    def test_kasingedad_predicative(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Kasingedad si Maria.", n_best=2)
        assert len(parses) >= 1
        f = parses[0][1]
        assert str(f.feats.get("ADJ_LEMMA")) == "edad"
        assert str(f.feats.get("PRED")) == "ADJ <SUBJ>"
        assert f.feats.get("KASING_N") is True, (
            "KASING_N=true expected on NOUN-derived equative"
        )

    @pytest.mark.parametrize("sentence", [
        # GEN standard, canonical Schachter-Otanes order
        "Kasingedad ni Maria si Ana.",
        # NOM standard, NOM comparee colloquial
        "Kasingedad si Maria si Ana.",
        # NOM comparee, GEN standard (alternate order)
        "Kasingedad si Maria ni Ana.",
        # Single-NP predicative
        "Kasingedad si Maria.",
    ])
    def test_kasingedad_equative_frames(
        self, sentence: str,
    ) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse for {sentence!r}"
        # KASING_N is lifted in all parses via the per-rule
        # extension. At least one parse must carry it.
        assert any(
            p[1].feats.get("KASING_N") is True for p in parses
        ), (
            f"{sentence!r} parsed but no parse carries "
            f"KASING_N=true"
        )


class TestPhase8lKasingNounVsKasingAdj:
    """The ADJ-base ``kasing-`` cell (Phase 5h C2) yields KASING_N
    undefined; the NOUN-base ``kasing_n_eq`` cell (this commit)
    yields KASING_N=true. This is the analytical contrast that
    downstream consumers can use to branch on the base-POS."""

    def test_kasing_adj_has_no_kasing_n_flag(self) -> None:
        from tgllfg.core.pipeline import parse_text
        # ADJ-base: ``kasingganda`` from ADJ root ``ganda``. The
        # lift equation ``(↑ KASING_N) = ↓1 KASING_N`` may surface
        # the feat at matrix level with an empty FStructure value
        # when the daughter lacks the feat (standard unifier
        # semantics). The contract is that the value is not
        # ``True`` — i.e., the matrix is not falsely tagged as a
        # NOUN-derived equative.
        parses = parse_text("Kasingganda si Maria.", n_best=2)
        assert len(parses) >= 1
        f = parses[0][1]
        assert f.feats.get("KASING_N") is not True, (
            "ADJ-base kasing- should not carry KASING_N=true"
        )

    def test_kasing_noun_carries_kasing_n_flag(self) -> None:
        from tgllfg.core.pipeline import parse_text
        # NOUN-base: ``kasingedad`` from NOUN root ``edad``
        parses = parse_text("Kasingedad si Maria.", n_best=2)
        assert len(parses) >= 1
        f = parses[0][1]
        assert f.feats.get("KASING_N") is True


class TestPhase8lKasingNounBinaryFeat:
    """``KASING_N`` is registered in BINARY_FEATS so the
    grammar compiler accepts ``[KASING_N]`` shorthand in
    category patterns."""

    def test_kasing_n_in_binary_feats(self) -> None:
        from tgllfg.core.feats import BINARY_FEATS
        assert "KASING_N" in BINARY_FEATS
