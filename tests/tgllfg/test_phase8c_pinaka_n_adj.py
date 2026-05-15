"""Phase 8.C: ``pinaka-`` superlative on N and ADJ heads.

Closes the audit-surfaced gap (§4 of ``docs/coverage-audit-2026-
05.md`` Wave 1 ANG PAMILYA prose + Wave 2 R&C 1990) by:

1. (C1) Adding a new ``pinaka_n`` paradigm cell with
   ``base_pos: NOUN`` in ``data/tgl/paradigms.yaml``. The cell
   generates ``pinaka-`` + NOUN surfaces with
   ``COMP_DEGREE: SUPERLATIVE``. Parallel to the existing
   Phase 5h ADJ-base ``pinaka-`` cell in
   ``data/tgl/adj_paradigms.yaml`` (which composes with the
   ``ma-`` derivational step: ``ma_adj`` + ``pinaka``) and the
   Phase 5n.B Commit 4 closed-class Q-head + ADV-FREQUENCY
   entries in ``particles.yaml``.

2. (C2) Wiring the cell to two NOUN bases: a new ``ubod``
   entry (citation "core/innermost") and an extension of the
   existing ``puno`` entry to add ``pinaka_n`` to its
   ``affix_class``. Also adds a new ``tigas`` ADJ entry with
   ``affix_class: [ma_adj]`` so the existing Phase 5h pinaka-
   on-ADJ cell fires on it (producing ``pinakamatigas``).

3. (C3) Closing docs in ``docs/analysis-choices.md`` Phase 8.C.

This file tests C1 — the cell exists and fires when the
analyzer is given a NOUN root declaring ``affix_class:
[pinaka_n]``. C2's sentence-level + lex coverage tests live
below in their own test classes.
"""

from __future__ import annotations

import pytest

from tgllfg.morph.analyzer import _get_default, analyze_tokens
from tgllfg.text.tokenizer import tokenize


_ANALYZER = _get_default()


def _first_analysis(form: str):
    toks = tokenize(form)
    analyses = analyze_tokens(toks)
    if not analyses or not analyses[0]:
        return None
    return analyses[0][0]


class TestPhase8cPinakaNCellShape:
    """The new ``pinaka_n`` cell in ``data/tgl/paradigms.yaml`` is
    registered with ``base_pos: NOUN`` and a single
    ``prefix pinaka`` operation."""

    def test_cell_loaded(self) -> None:
        cells = [
            c for c in _ANALYZER._data.paradigm_cells
            if c.affix_class == "pinaka_n"
        ]
        assert len(cells) == 1, (
            f"expected exactly one pinaka_n cell, got {len(cells)}"
        )
        cell = cells[0]
        assert cell.base_pos == "NOUN"
        assert cell.feats.get("COMP_DEGREE") == "SUPERLATIVE"
        # Single prefix-op; no reduplication / suffix / infix.
        assert len(cell.operations) == 1
        op = cell.operations[0]
        assert op.op == "prefix"
        assert op.value == "pinaka"


class TestPhase8cPinakaNounSurfaces:
    """The new ``ubod`` / ``buod`` NOUNs + the extended ``puno``
    NOUN produce superlative ``pinaka-`` surfaces via the new
    cell. ``ubod`` and ``buod`` are sibling relational nouns
    that both head the "the very-X / the essence-of" construction
    (GT cites ``pinakaubod`` "kernel/nucleus";
    ``pinakabuod`` "essence/crux")."""

    @pytest.mark.parametrize("form,base", [
        ("pinakaubod", "ubod"),
        ("pinakabuod", "buod"),
        ("pinakapuno", "puno"),
    ])
    def test_pinaka_noun_analysis(
        self, form: str, base: str
    ) -> None:
        """Every surface has at least one NOUN analysis with
        ``COMP_DEGREE: SUPERLATIVE``."""
        toks = tokenize(form)
        analyses = analyze_tokens(toks)
        assert analyses and analyses[0], (
            f"{form!r} produced no analyses"
        )
        noun_analyses = [a for a in analyses[0] if a.pos == "NOUN"]
        assert noun_analyses, (
            f"{form!r} has no NOUN analysis "
            f"(got: {[a.pos for a in analyses[0]]})"
        )
        a = noun_analyses[0]
        assert a.lemma == base, (
            f"{form!r} NOUN lemma={a.lemma!r}, expected {base!r}"
        )
        feats = dict(a.feats) if a.feats else {}
        assert feats.get("COMP_DEGREE") == "SUPERLATIVE"

    def test_pinakapuno_dual_pos(self) -> None:
        """``pinakapuno`` has BOTH a NOUN analysis (the head /
        principal one — relational-N reading) and an ADJ analysis
        (most important / principal — predicate / modifier
        reading; GT's primary translation). The new
        ``pinaka_adj_from_n`` cell drives the ADJ output via
        a ``cell.pos`` override on the NOUN base."""
        toks = tokenize("pinakapuno")
        analyses = analyze_tokens(toks)
        assert analyses and analyses[0]
        poses = {a.pos for a in analyses[0]}
        assert "NOUN" in poses, (
            f"pinakapuno missing NOUN analysis; got {poses}"
        )
        assert "ADJ" in poses, (
            f"pinakapuno missing ADJ analysis; got {poses}"
        )
        # The ADJ analysis carries PREDICATIVE so the Phase 5g
        # predicative-adj clause rule can consume it.
        adj = [a for a in analyses[0] if a.pos == "ADJ"][0]
        feats = dict(adj.feats) if adj.feats else {}
        assert feats.get("COMP_DEGREE") == "SUPERLATIVE"
        assert feats.get("PREDICATIVE") is True
        assert adj.lemma == "puno"

    def test_pinakaubod_pinakabuod_noun_only(self) -> None:
        """``pinakaubod`` / ``pinakabuod`` are NOUN-only — they do
        not unlock the ``pinaka_adj_from_n`` ADJ reading (the
        "core" / "essence" semantics doesn't lend itself to a
        predicate-ADJ "most important" interpretation). Pinned
        so a later widening of the affix_class is a visible
        signal."""
        for form in ("pinakaubod", "pinakabuod"):
            toks = tokenize(form)
            analyses = analyze_tokens(toks)
            assert analyses and analyses[0]
            poses = {a.pos for a in analyses[0]}
            assert poses == {"NOUN"}, (
                f"{form!r} has unexpected POS set {poses}; "
                "expected NOUN-only"
            )


class TestPhase8cPinakaAdjSurfaces:
    """The new ``tigas`` ADJ — registered with
    ``affix_class: [ma_adj]`` — picks up the existing Phase 5h
    ADJ ``pinaka-`` cell unchanged. Also sanity-checks
    ``pinakamatibay`` (already wired pre-8.C; verifies no
    regression)."""

    @pytest.mark.parametrize("form,base", [
        ("pinakamatigas",  "tigas"),
        ("pinakamatibay",  "tibay"),   # pre-8.C wiring; pinned.
        ("matigas",        "tigas"),   # plain ma_adj derivation.
    ])
    def test_pinaka_adj_analysis(
        self, form: str, base: str
    ) -> None:
        a = _first_analysis(form)
        assert a is not None, f"{form!r} produced no analysis"
        assert a.pos == "ADJ", (
            f"{form!r} pos={a.pos!r}, expected ADJ"
        )
        assert a.lemma == base, (
            f"{form!r} lemma={a.lemma!r}, expected {base!r}"
        )
        feats = dict(a.feats) if a.feats else {}
        if form.startswith("pinaka"):
            assert feats.get("COMP_DEGREE") == "SUPERLATIVE"
        else:
            assert feats.get("COMP_DEGREE") is None


class TestPhase8cSentencesParseable:
    """Audit-derived sentences using ``pinaka-`` heads now produce a
    clean parse. Covers the N-head case (``pinakapuno``) and the
    ADJ-head with predicate-fronted and N-modifier readings
    (``pinakamatigas``)."""

    @pytest.mark.parametrize("sentence", [
        # Wave 1 audit target (rg81 ANG PAMILYA prose) — N-head.
        "Ang ama ang pinakapuno ng pamilya.",
        # ADJ-head predicate use (constructed from the audit base).
        "Pinakamatigas ang bato.",
        # Wave 2 audit target (R&C 1990 §10) — ADJ as NP-modifier.
        # The wh-Q + locative-PP cousin
        # "Ano ang pinakamatigas na bato sa mundo?" is pinned as
        # out-of-scope below (sa-PP + WH-Q interaction).
        "Ano ang pinakamatigas na bato.",
    ])
    def test_sentence_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, (
            f"no parse for {sentence!r} after 8.C lex+paradigm work"
        )


class TestPhase8cNounsRegistered:
    """The new noun additions (``ubod``, ``mundo``, ``sandata``) are
    known bare-citation surfaces. ``mundo`` and ``sandata`` were
    OOV blockers exposed during 8.C sentence-level probing —
    folded into the lex pass to keep the audit-derived sentences
    clean."""

    @pytest.mark.parametrize("noun", [
        "ubod", "buod", "mundo", "sandata",
    ])
    def test_noun_known(self, noun: str) -> None:
        assert _ANALYZER.is_known_surface(noun), (
            f"noun {noun!r} not known after 8.C lex add"
        )


class TestPhase8cOutOfScope:
    """Two distinct construction gaps surfaced during 8.C probing.
    These are SEPARATE from the pinaka- paradigm-cell scope (which
    is fully closed by C1+C2) — pin them here so a future
    construction sub-PR flipping them to passing produces a
    visible signal."""

    def test_adj_headed_np_nominalization_still_fails(self) -> None:
        """``Ang matibay ay sandata.`` (ADJ-head NP nominalization
        + ay-inversion). The grammar does not yet admit
        ``ang ADJ`` as the head of a topic NP — separate
        Phase-8 construction-class work (nominalization rule)."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Ang matibay ay sandata.", n_best=3)
        assert len(parses) == 0, (
            "ADJ-head NP nominalization unexpectedly parses — "
            "flip this pin if a construction sub-PR closed it."
        )

    def test_sa_pp_plus_wh_q_still_fails(self) -> None:
        """``Ano ang pinakamatigas na bato sa mundo?`` (wh-Q +
        ADJ-modifier + N-head + locative-PP). The grammar's
        wh-Q constraint and a sa-PP downstream constituent are
        interacting in a way that surfaces as
        ``neg-existential-failed: ¬ (↓1 WH)`` — separate from
        the pinaka- paradigm-cell scope."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Ano ang pinakamatigas na bato sa mundo?", n_best=3
        )
        assert len(parses) == 0, (
            "sa-PP + wh-Q unexpectedly parses — flip this pin "
            "if a construction sub-PR closed it."
        )
