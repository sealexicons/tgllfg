# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.G — lexicalized reduplication residue.

Reduplicated forms that are synchronically FROZEN (idiosyncratic meaning,
not productively derived) are stored as static lexical entries carrying
``LEXICALIZED=true`` — distinct from the productive R-bucket cells
(10.A-10.E), which derive their surfaces via paradigm cells. Four forms
the refs flag as lexicalized:

- ``halo-halo``  NOUN — the shaved-ice dessert / "mixture" (≠ a productive
  redup of ``halo`` "mix").
- ``sari-sari``  ADJ  — "assorted, various" (``sari-saring tindahan``).
- ``uli-uli``    NOUN — "whirlpool" (≠ the iterative adverb ``uli-uli``
  "again and again" from ``uli``).
- ``tabi-tabi``  NOUN — the courtesy formula ``tabi-tabi po`` ("by your
  leave"); a ``FRAGMENT_HOST`` noun (sibling of ``salamat``), so the
  Phase 5n.B L96 fragment-S rule + po-clitic absorption parse
  ``Tabi-tabi po.`` with no new grammar rule.

``kanya-kanya`` (the ledger's fourth original candidate) is already
covered productively by the Phase 5n.C.3 ``kani_redup`` cell, so it is
not re-added here.

The citations are the merged surfaces (``halohalo`` …) the hyphen-merge
tokenizer produces, so both ``halo-halo`` and ``halohalo`` input reach
the same entry.
"""

import pytest

from tgllfg.core.feats import BINARY_FEATS
from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import _get_default


def test_lexicalized_feat_registered() -> None:
    """``LEXICALIZED`` is a registered binary feat (Phase 10.G, 64→65)."""
    assert "LEXICALIZED" in BINARY_FEATS


@pytest.mark.parametrize(
    "surface,pos,index",
    [
        ("halohalo", "NOUN", "nouns"),
        ("uliuli", "NOUN", "nouns"),
        ("tabitabi", "NOUN", "nouns"),
        ("sarisari", "ADJ", "adjectives"),
    ],
)
def test_lexicalized_entry_present(surface: str, pos: str, index: str) -> None:
    """Each form is a static lexical entry flagged ``LEXICALIZED=true``."""
    entries = getattr(_get_default()._index, index).get(surface, [])
    hits = [e for e in entries if e.feats.get("LEXICALIZED") is True]
    assert len(hits) == 1, (
        f"expected one LEXICALIZED {pos} for {surface!r}; got {entries!r}"
    )
    assert hits[0].pos == pos


def test_lexicalized_are_frozen_not_productive() -> None:
    """The residue is frozen — it carries no ``REDUP_SEM`` (the marker of
    a productive R-bucket derivation), distinguishing it from 10.A-10.E."""
    idx = _get_default()._index
    for surf, index in [
        ("halohalo", "nouns"), ("uliuli", "nouns"),
        ("tabitabi", "nouns"), ("sarisari", "adjectives"),
    ]:
        for e in getattr(idx, index).get(surf, []):
            if e.feats.get("LEXICALIZED") is True:
                assert "REDUP_SEM" not in e.feats, (
                    f"{surf!r} unexpectedly carries REDUP_SEM"
                )


def test_tabitabi_is_fragment_host() -> None:
    """``tabi-tabi`` is a ``FRAGMENT_HOST`` noun, so the courtesy formula
    parses via the existing L96 fragment-S rule — no new grammar rule."""
    entries = _get_default()._index.nouns.get("tabitabi", [])
    assert any(e.feats.get("FRAGMENT_HOST") is True for e in entries)


@pytest.mark.parametrize(
    "text",
    [
        "Masarap ang halo-halo.",               # NOUN subject (dessert)
        "Halo-halo ang prutas.",                # NOUN predicate
        "Malakas ang uliuli.",                  # NOUN (whirlpool)
        "Sari-sari ang prutas.",                # ADJ predicative
        "Sari-saring aklat ang binili niya.",   # ADJ attributive (linker)
        "Tabi-tabi po.",                        # FRAGMENT_HOST formula + po
        "Tabi-tabi.",                           # bare fragment
    ],
)
def test_lexicalized_forms_parse(text: str) -> None:
    """Each lexicalized form parses in its typical frame (hyphenated
    input; the tokenizer merges to the citation)."""
    assert len(parse_text(text)) >= 1, text
