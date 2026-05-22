# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.C.3 Commit 4 — productive ``tag_season`` paradigm.

Migrates the Phase 5f Commit 14 hand-coded ``tag*`` season NOUN
entries (``taginit`` / ``tagulan`` / ``taglamig`` / ``tagaraw``
/ ``taggutom``) to a productive paradigm via:

* New ``tag_season`` paradigm cell in
  ``data/tgl/paradigms.yaml`` (``base_pos: NOUN``, single
  ``prefix tag`` op, ``feats: {SEM_CLASS: SEASON}``).
* ``affix_class: [tag_season]`` added to the 3 existing NOUN
  roots (``araw`` / ``gutom`` / ``ulan``).
* Two new NOUN roots ``init`` and ``lamig`` in
  ``data/tgl/nouns.yaml`` — they previously existed only as ADJ
  roots; the NOUN-pos counterparts are conventional
  nominalizations ("heat" / "cold") and don't conflict with the
  existing ADJ paradigm (which still produces ``mainit`` /
  ``malamig`` via ``ma_adj``).
* Removed the 5 hand-coded ``tag*`` NOUN entries from
  ``nouns.yaml`` — the productive paradigm now provides them.

Closes the third piece of §18 L31 (productive paradigm classes).
"""

import pytest

from tgllfg.core.common import Token
from tgllfg.morph.analyzer import Analyzer


# === Productive cell fires on each season base ===========================


@pytest.mark.parametrize("surface,base", [
    ("taginit",  "init"),
    ("tagulan",  "ulan"),
    ("taglamig", "lamig"),
    ("tagaraw",  "araw"),
    ("taggutom", "gutom"),
])
def test_tag_season_productive(surface: str, base: str) -> None:
    """Each ``tag<X>`` form analyses as a NOUN with
    SEM_CLASS=SEASON. Lemma points to the base noun (Phase
    5n.C.3 Commit 1 convention)."""
    a = Analyzer.from_default()
    token = Token(surface=surface, norm=surface, start=0, end=len(surface))
    results = a.analyze_one(token)
    season_nouns = [r for r in results
                    if r.pos == "NOUN"
                    and r.feats.get("SEM_CLASS") == "SEASON"]
    assert len(season_nouns) >= 1, (
        f"expected ≥1 SEM_CLASS=SEASON NOUN analysis for {surface!r}"
    )
    r = season_nouns[0]
    assert r.lemma == base


# === Base nouns indexed ==================================================


@pytest.mark.parametrize("base", ["init", "lamig"])
def test_new_base_nouns_indexed(base: str) -> None:
    """``init`` and ``lamig`` previously analyzed as _UNK at the
    NOUN level (they existed only as ADJ roots); after this
    commit they also have NOUN analyses."""
    a = Analyzer.from_default()
    token = Token(surface=base, norm=base, start=0, end=len(base))
    results = a.analyze_one(token)
    nouns = [r for r in results if r.pos == "NOUN"]
    assert len(nouns) >= 1


# === ADJ paradigm unaffected ==============================================


def test_ma_init_still_produced() -> None:
    """The ``ma_adj`` paradigm continues to produce ``mainit`` from
    the ADJ-root ``init``; adding the NOUN-root ``init`` doesn't
    disturb the existing ADJ derivation."""
    a = Analyzer.from_default()
    token = Token(surface="mainit", norm="mainit", start=0, end=6)
    results = a.analyze_one(token)
    adjs = [r for r in results if r.pos == "ADJ"]
    assert len(adjs) >= 1
    assert adjs[0].lemma == "init"


# === Hand-coded tag* entries removed =====================================


def test_old_hand_coded_season_entries_removed() -> None:
    """The 5 hand-coded ``tag*`` NOUN entries (Phase 5f Commit 14)
    are removed from nouns.yaml — verified by checking that no
    NOUN root with those citations exists at the loaded-data
    level."""
    a = Analyzer.from_default()
    tag_citations = {"taginit", "tagulan", "taglamig", "tagaraw", "taggutom"}
    for r in a._data.roots:
        if r.pos == "NOUN":
            assert r.citation not in tag_citations, (
                f"unexpected hand-coded season NOUN: {r.citation!r}; "
                f"these should be removed and produced productively"
            )
