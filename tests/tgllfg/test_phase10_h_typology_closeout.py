# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.H — reduplication typology close-out.

The cumulative close of the R-bucket (10.A-10.G + the E-series) against
the reviewer's 2026-05-26 typology, alongside the docs roll-up
(``docs/analysis-choices.md`` § "Phase 10.H").

Capstone reachability check: every ``REDUP_SEM`` value the typology maps
to is reachable, plus the ``LEXICALIZED`` frozen-residue marker —
confirming the enum is fully populated by shipped lexicon / grammar.

``mura`` was originally landed here as a VERB "curse" → ``mura-mura``
(ITER); Phase 10.H.post-1 retracted that reading (unattested across all
eight references) in favour of the scalar ADJ ``mura`` "cheap" / "young",
whose ``mura-mura`` is "rather cheap" (S&O 1972). The mura-specific tests
moved with it — see ``test_phase10_h_post1_mura_adj_correction``.

REDUP_SEM index homes (verified Phase 10.H): FREQ / DISTR → ``particles``
(NOUN→ADV / NUM→ADV cells), QUANT / LEXICALIZED → ``nouns``, ATTEN /
CASUAL / ITER → ``adjectives``; INTENS is grammar-produced (10.E.2
``ma-X na ma-X``).
"""

import pytest

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import _get_default


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
