# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.H — reduplication typology close-out.

The cumulative close of the R-bucket (10.A-10.G + the E-series) against
the reviewer's 2026-05-26 typology. Two concrete deliverables alongside
the docs roll-up (``docs/analysis-choices.md`` § "Phase 10.H"):

1. ``mura`` "curse" — the one native iterative-affective root from the
   reviewer's speech / noise class that had not landed in 10.E.4 (it is
   collision-free: the scalar ADJ ``mura`` "cheap" is not in the
   lexicon). Added as a VERB (``mag`` / ``v_iter_redup``) → ``mura-mura``
   (ITER) + the inflected ``nagmura-mura``, completing the native
   affective inventory.

2. A capstone reachability check: every ``REDUP_SEM`` value the typology
   maps to is reachable, plus the ``LEXICALIZED`` frozen-residue marker —
   confirming the enum is fully populated by shipped lexicon / grammar.

REDUP_SEM index homes (verified Phase 10.H): FREQ / DISTR → ``particles``
(NOUN→ADV / NUM→ADV cells), QUANT / LEXICALIZED → ``nouns``, ATTEN /
CASUAL / ITER → ``adjectives``; INTENS is grammar-produced (10.E.2
``ma-X na ma-X``).
"""

import pytest

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import _get_default


# === mura — native affective-inventory completion =====================


def test_mura_bare_iter_adj() -> None:
    """``mura`` "curse" produces the bare ITER redup ``mura-mura``."""
    adjs = _get_default()._index.adjectives.get("muramura", [])
    hits = [a for a in adjs if a.feats.get("REDUP_SEM") == "ITER"]
    assert len(hits) == 1, f"expected one ITER ADJ for muramura; got {adjs!r}"
    assert hits[0].feats.get("LEMMA") == "mura-mura"


def test_mura_inflected_moderative() -> None:
    """The 10.E.3.post-2 post-pass yields the inflected ``nagmura-mura``."""
    forms = _get_default()._index.verb_forms.get("nagmuramura", [])
    assert [a for a in forms if a.feats.get("REDUP_SEM") == "ITER"]


def test_mura_keeps_plain_inflection() -> None:
    """The opt-in is additive — ``magmura`` PFV ``nagmura`` is intact."""
    assert _get_default()._index.verb_forms.get("nagmura")


@pytest.mark.parametrize("text", ["Mura-mura siya.", "Nagmura-mura siya."])
def test_mura_clause_parses(text: str) -> None:
    assert len(parse_text(text)) >= 1, text


# === capstone: REDUP_SEM inventory fully reachable ====================

# One representative merged surface per morphological REDUP_SEM value,
# with the index it lands in (verified Phase 10.H).
_MORPH_REPS = [
    ("arawaraw", "particles", "FREQ"),        # 10.A time_redup_freq
    ("isaisa", "particles", "DISTR"),         # 10.C num_redup_distr
    ("daandaan", "nouns", "QUANT"),           # 10.D card_redup
    ("magandaganda", "adjectives", "ATTEN"),  # 10.E.1 redup_intens_adj
    ("lakadlakad", "adjectives", "CASUAL"),   # 10.E.3 v_casual_redup
    ("iyakiyak", "adjectives", "ITER"),       # 10.E.3 v_iter_redup
]


@pytest.mark.parametrize("surface,index,sem", _MORPH_REPS)
def test_morphological_redup_sem_reachable(surface: str, index: str, sem: str) -> None:
    """Each morphological ``REDUP_SEM`` value is reachable from a shipped
    lexicon form — the typology's nominal / numeral / adjectival / verbal
    classes all populate the enum."""
    entries = getattr(_get_default()._index, index).get(surface, [])
    assert any(e.feats.get("REDUP_SEM") == sem for e in entries), (
        f"{sem} unreachable via {surface!r} in {index}"
    )


def test_lexicalized_reachable() -> None:
    """The frozen-residue marker (10.G) is reachable."""
    entries = _get_default()._index.nouns.get("halohalo", [])
    assert any(e.feats.get("LEXICALIZED") is True for e in entries)


def test_intens_reachable_via_grammar() -> None:
    """INTENS is grammar-produced (10.E.2 ``ma-X na ma-X``); it surfaces
    at the matrix f-structure of ``Mabait na mabait ang bata.``."""
    sems = set()
    for _ct, fs, _a, _d in parse_text("Mabait na mabait ang bata."):
        v = fs.feats.get("REDUP_SEM")
        if isinstance(v, str):
            sems.add(v)
    assert "INTENS" in sems
