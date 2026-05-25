# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.C.3 Commit 2 — ``card_redup`` productive paradigm.

Replaces the Phase 5f Commit 18 hand-coded ``daandaan`` /
``libulibo`` NOUN entries with productive derivation via the
``card_redup`` paradigm cell (``data/tgl/paradigms.yaml``):
``base_pos: NOUN``, ``affix_class: card_redup``, single
reduplication op, ``feats: {MEASURE: true, ...}``. NOUN roots
``libo`` / ``daan`` (and Phase 10.D ``milyon``) carry
``affix_class: [card_redup]`` + root-side ``COLL_VALUE``
(THOUSANDS / HUNDREDS / MILLIONS).

**Phase 10.D migration**: the cell was unified onto the
``redup_root`` op (the former bespoke ``full_redup`` op +
``sandhi.full_reduplicate`` were removed — card_redup was their
sole user). First-copy /o/→/u/ raising is now the per-root
``redup_o_raise`` sandhi flag rather than baked into the op:
``libo`` opts in (→ ``libulibo``); ``daan`` has no stem /o/
(→ ``daandaan``); the Spanish-loan ``milyon`` opts out
(→ ``milyonmilyon``). Surfaces for daan/libo are byte-identical
to the pre-10.D output. See ``test_phase10_d_card_quantitative``
for the op-level surface tests + the milyon coverage.

The ``tokenize`` hyphen-merge pre-pass continues to fold
``daan-daan`` / ``libu-libo`` into single tokens matching the
derived ``daandaan`` / ``libulibo`` surfaces.

Closes the first piece of §18 L31 (productive paradigm classes
for compound cardinals).
"""

from tgllfg.core.common import Token
from tgllfg.morph.analyzer import Analyzer


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
    # Phase 10.D cross-cutting redup feats.
    assert n.feats.get("REDUP") == "FULL"
    assert n.feats.get("REDUP_SEM") == "QUANT"


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
    # Phase 10.D cross-cutting redup feats.
    assert n.feats.get("REDUP") == "FULL"
    assert n.feats.get("REDUP_SEM") == "QUANT"


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
