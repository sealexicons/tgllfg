# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.C.3 Commit 2 — ``card_redup`` productive paradigm.

Replaces the Phase 5f Commit 18 hand-coded ``daandaan`` /
``libulibo`` NOUN entries with productive derivation via:

* New ``full_redup`` op (``src/tgllfg/morph/sandhi.py``
  ``full_reduplicate``): whole-root redup with first-copy /o/→/u/
  raising. ``libo`` → ``libulibo``; ``daan`` → ``daandaan``.
* New ``card_redup`` paradigm cell
  (``data/tgl/paradigms.yaml`` end of file): ``base_pos: NOUN``,
  ``affix_class: card_redup``, single ``full_redup`` op,
  ``feats: {MEASURE: YES}``.
* New NOUN roots ``libo`` and ``daan`` in
  ``data/tgl/nouns.yaml`` with ``affix_class: [card_redup]`` and
  root-side ``COLL_VALUE`` (THOUSANDS / HUNDREDS).

The Phase 5n.B Commit 11.5 ``tokenize`` hyphen-merge pre-pass
continues to fold ``daan-daan`` and ``libu-libo`` into single
tokens that match the derived ``daandaan`` / ``libulibo``
surfaces.

Closes the first piece of §18 L31 (productive paradigm classes
for compound cardinals).
"""

from tgllfg.core.common import Token
from tgllfg.morph.analyzer import Analyzer
from tgllfg.morph.sandhi import full_reduplicate


# === Sandhi op ===========================================================


def test_full_reduplicate_o_raise() -> None:
    """``libo`` → ``libulibo`` (final /o/ raises to /u/ in the
    first copy)."""
    assert full_reduplicate("libo") == "libulibo"


def test_full_reduplicate_no_o() -> None:
    """``daan`` → ``daandaan`` (no /o/ in stem; nothing to raise)."""
    assert full_reduplicate("daan") == "daandaan"


def test_full_reduplicate_baka() -> None:
    """Sanity: ``baka`` → ``bakabaka`` (no /o/, no special sandhi)."""
    assert full_reduplicate("baka") == "bakabaka"


# === Productive cell fires ================================================


def test_libo_root_indexed_as_noun() -> None:
    """The new ``libo`` NOUN root is indexed both bare and via the
    ``card_redup`` cell."""
    a = Analyzer.from_default()
    # Bare ``libo`` surface — indexed via the standard bare-noun path.
    token = Token(surface="libo", norm="libo", start=0, end=4)
    bare_results = a.analyze_one(token)
    nouns = [r for r in bare_results if r.pos == "NOUN"]
    assert len(nouns) >= 1
    assert nouns[0].lemma == "libo"
    assert nouns[0].feats.get("COLL_VALUE") == "THOUSANDS"


def test_libulibo_produced_by_paradigm() -> None:
    """The ``libulibo`` surface is produced by the ``card_redup``
    cell (not the hand-coded entry which was removed). Analysis
    carries MEASURE=YES (from cell.feats) and COLL_VALUE=THOUSANDS
    (from root.feats), and the lemma is the ``libo`` citation
    (LEMMA defaults to root.citation per the
    ``_index_paradigm_via_base_pos`` convention)."""
    a = Analyzer.from_default()
    token = Token(surface="libulibo", norm="libulibo", start=0, end=8)
    results = a.analyze_one(token)
    nouns = [r for r in results if r.pos == "NOUN"]
    assert len(nouns) >= 1
    measure_nouns = [r for r in nouns if r.feats.get("MEASURE") is True]
    assert len(measure_nouns) >= 1
    n = measure_nouns[0]
    assert n.lemma == "libo"
    assert n.feats.get("COLL_VALUE") == "THOUSANDS"


def test_daandaan_produced_by_paradigm() -> None:
    """Same for ``daandaan``: produced productively from the
    ``daan`` cardinal NOUN root."""
    a = Analyzer.from_default()
    token = Token(surface="daandaan", norm="daandaan", start=0, end=8)
    results = a.analyze_one(token)
    measure_nouns = [r for r in results
                     if r.pos == "NOUN"
                     and r.feats.get("MEASURE") is True]
    assert len(measure_nouns) >= 1
    n = measure_nouns[0]
    assert n.lemma == "daan"
    assert n.feats.get("COLL_VALUE") == "HUNDREDS"


def test_old_hand_coded_entries_removed() -> None:
    """``daandaan`` and ``libulibo`` are no longer present as
    citation forms in ``self._data.roots``; only the productive
    ``daan`` / ``libo`` roots."""
    a = Analyzer.from_default()
    citations = {r.citation for r in a._data.roots if r.pos == "NOUN"}
    assert "libo" in citations
    assert "daan" in citations
    assert "libulibo" not in citations
    assert "daandaan" not in citations
