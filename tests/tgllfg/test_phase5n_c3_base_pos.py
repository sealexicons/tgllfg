# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.C.3 Commit 1 — paradigm-engine ``base_pos`` generalization.

Adds ``base_pos`` to :class:`tgllfg.morph.paradigms.ParadigmCell`
(default ``"VERB"`` for backward compat). The
:meth:`tgllfg.morph.analyzer.Analyzer._build_index` loop now
dispatches NOUN / ADJ roots through the new
:meth:`_index_paradigm_via_base_pos` helper, which iterates
``paradigm_cells`` filtering by ``base_pos == root.pos``.

This commit is infrastructure-only — no new YAML cells are added.
Tests cover:

* Existing VERB-root paradigms continue to fire unchanged.
* The new ``_index_paradigm_via_base_pos`` correctly filters on
  ``base_pos == root.pos``.
* The ``base_pos`` default of ``"VERB"`` preserves backward
  compatibility (existing paradigms.yaml entries without
  ``base_pos`` keep working).
* A synthetic NOUN-base cell, when injected directly, fires on a
  NOUN root and produces a derived surface indexed under
  ``self._index.nouns``.
* A synthetic ADJ-base cell, when injected, fires on an ADJ root
  and the surface lands in ``self._index.adjectives``.
"""

from tgllfg.core.common import Token
from tgllfg.morph.analyzer import Analyzer
from tgllfg.morph.paradigms import (
    Operation,
    ParadigmCell,
    VerbalCell,
)


# === Backward-compat: existing VERB paradigms ============================


def test_verb_paradigm_unchanged() -> None:
    """A canonical VERB-paradigm surface (``kumain``) continues to
    analyse with VOICE=AV + ASPECT=PFV after the base_pos
    generalization."""
    a = Analyzer.from_default()
    token = Token(surface="Kumain", norm="kumain", start=0, end=6)
    results = a.analyze_one(token)
    av_pfv = [r for r in results
              if r.feats.get("VOICE") == "AV"
              and r.feats.get("ASPECT") == "PFV"]
    assert len(av_pfv) >= 1
    assert av_pfv[0].lemma == "kain"


def test_legacy_verb_cells_default_to_verb_base_pos() -> None:
    """Legacy AV/OV/DV/IV paradigm cells (those with non-empty
    ``voice``) all carry ``base_pos == 'VERB'``. The field default
    preserves the legacy paradigm semantics for cells written
    without an explicit base_pos.

    Phase 5n.C.3 Commit 2 onward introduces non-verbal cells
    (``base_pos: NOUN`` / ``ADJ`` / ``PRON``) that have empty
    voice/aspect — those are excluded from this check."""
    a = Analyzer.from_default()
    assert len(a._data.paradigm_cells) > 0
    verb_cells = [c for c in a._data.paradigm_cells if c.voice]
    assert len(verb_cells) > 0
    for cell in verb_cells:
        assert cell.base_pos == "VERB", (
            f"unexpected base_pos {cell.base_pos!r} on verbal cell "
            f"{cell.voice}/{cell.aspect}/{cell.affix_class}"
        )


def test_dataclass_default_is_verb() -> None:
    """The :class:`ParadigmCell` dataclass default is ``"VERB"`` so
    code that constructs cells without specifying base_pos retains
    the verbal-paradigm semantics."""
    pc = ParadigmCell()
    assert pc.base_pos == "VERB"
    vc = VerbalCell()
    assert vc.base_pos == "VERB"


# === Injection harness — synthetic NOUN paradigm cell ====================


def test_noun_base_pos_cell_fires() -> None:
    """A synthetic NOUN-base cell, when added to the analyzer's
    paradigm_cells list, fires on a NOUN root that matches the cell's
    affix_class."""
    a = Analyzer.from_default()
    # Pick an existing NOUN root with a known citation; assert it's
    # currently bare-indexed only.
    noun_root = next(r for r in a._data.roots
                     if r.pos == "NOUN" and r.citation == "aso")
    # Add a synthetic affix_class to the root so a cell can filter.
    # (Mutating in-place is fine here; the analyzer's index is
    # rebuilt below.)
    noun_root.affix_class = list(noun_root.affix_class) + ["test_noun"]
    cell = VerbalCell(
        base_pos="NOUN",
        affix_class="test_noun",
        operations=[Operation(op="prefix", value="x_")],
        feats={"TEST_FEAT": "YES"},
    )
    a._data.paradigm_cells.append(cell)
    # Rebuild the index.
    a._index = type(a._index)()
    a._build_index()
    # The synthetic surface ``x_aso`` should be indexed as NOUN.
    token = Token(surface="x_aso", norm="x_aso", start=0, end=5)
    results = a.analyze_one(token)
    noun_results = [r for r in results
                    if r.pos == "NOUN" and r.feats.get("TEST_FEAT") == "YES"]
    assert len(noun_results) >= 1
    assert noun_results[0].lemma == "aso"


def test_adj_base_pos_cell_fires() -> None:
    """Same as the NOUN test but for ADJ roots — confirms the ADJ
    branch of :meth:`_index_paradigm_via_base_pos` routes derived
    surfaces to ``self._index.adjectives``."""
    a = Analyzer.from_default()
    # Find an ADJ root with a non-empty affix_class (so the cell
    # filter matches).
    adj_root = next(
        r for r in a._data.roots
        if r.pos == "ADJ" and r.affix_class
    )
    adj_root.affix_class = list(adj_root.affix_class) + ["test_adj"]
    cell = VerbalCell(
        base_pos="ADJ",
        affix_class="test_adj",
        operations=[Operation(op="prefix", value="y_")],
        feats={"TEST_ADJ_FEAT": "YES"},
    )
    a._data.paradigm_cells.append(cell)
    a._index = type(a._index)()
    a._build_index()
    surface = f"y_{adj_root.citation}"
    token = Token(surface=surface, norm=surface, start=0, end=len(surface))
    results = a.analyze_one(token)
    adj_results = [r for r in results
                   if r.pos == "ADJ"
                   and r.feats.get("TEST_ADJ_FEAT") == "YES"]
    assert len(adj_results) >= 1


# === base_pos filter discrimination ======================================


def test_verb_cell_skips_noun_root() -> None:
    """A VERB-base cell should NOT fire on a NOUN root, even if the
    affix_class matches. Belt-and-braces verification that the
    base_pos filter actually filters."""
    a = Analyzer.from_default()
    noun_root = next(r for r in a._data.roots
                     if r.pos == "NOUN" and r.citation == "aso")
    noun_root.affix_class = list(noun_root.affix_class) + ["verb_only_test"]
    cell = VerbalCell(
        base_pos="VERB",  # explicit
        voice="AV",
        aspect="PFV",
        affix_class="verb_only_test",
        operations=[Operation(op="prefix", value="z_")],
    )
    a._data.paradigm_cells.append(cell)
    a._index = type(a._index)()
    a._build_index()
    # ``z_aso`` should NOT have a NOUN-indexed analysis because
    # the cell is base_pos=VERB and `aso` is pos=NOUN.
    token = Token(surface="z_aso", norm="z_aso", start=0, end=5)
    results = a.analyze_one(token)
    # Only _UNK should be returned for this synthetic surface.
    non_unk = [r for r in results if r.pos != "_UNK"]
    assert non_unk == [], (
        f"expected no non-_UNK analyses for z_aso (VERB cell on "
        f"NOUN root); got {non_unk}"
    )
