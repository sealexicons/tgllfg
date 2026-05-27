# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.H.post-1 — correct the ``mura`` analysis.

Phase 10.H landed ``mura`` as a VERB "curse" (``mag`` / ``v_iter_redup``)
→ ``mura-mura`` ITER, justified as "collision-free" because the scalar
adjective was absent. The justification was the bug: the curse reading is
unattested across all eight project references, while the scalar ADJ
``mura`` "cheap" is canonical — S&O 1972 contrasts it with ``mahal``
(``Mahal ang damit na ito. Pero mura ang damit na iyan.``) and glosses
``mura-mura`` as "rather cheap" (the scalar-moderate redup). The informant
(2026-05-26) confirms two frequent, contrastive ADJ senses — "cheap"
(price, antonym of ``mahal``) and "young / tender / unripe" — and reports
never having met the curse VERB.

The correction: drop the VERB, add one scalar ADJ ``mura`` carrying both
senses (no grammatical reflex distinguishes them → a single PRED avoids
spurious ambiguity), opted into ``adj_redup``. ``mura-mura`` is therefore
``REDUP=FULL`` with ``REDUP_SEM`` left underspecified — the scalar-moderate
"rather cheap" reading the cell intends, no longer ITER.
"""

import pytest

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import _get_default


def test_mura_is_predicative_scalar_adj() -> None:
    """``mura`` is a bare predicative ADJ (the attested "cheap"/"young")."""
    entries = _get_default()._index.adjectives.get("mura", [])
    assert any(
        e.feats.get("PREDICATIVE") is True and e.feats.get("LEMMA") == "mura"
        for e in entries
    ), f"expected predicative ADJ mura; got {entries!r}"


def test_mura_redup_is_full_underspecified() -> None:
    """``mura-mura`` reaches ``REDUP=FULL`` with degree underspecified — the
    scalar-moderate "rather cheap" the ``adj_redup`` cell intends, not ITER."""
    entries = _get_default()._index.adjectives.get("muramura", [])
    full = [e for e in entries if e.feats.get("REDUP") == "FULL"]
    assert full, f"expected REDUP=FULL adj for muramura; got {entries!r}"
    assert all(e.feats.get("REDUP_SEM") is None for e in full)


def test_curse_verb_retracted() -> None:
    """The unattested curse VERB is gone — no inflected ``nagmura`` /
    ``nagmuramura`` forms, and no ITER reading on the redup adjective."""
    idx = _get_default()._index
    assert not idx.verb_forms.get("nagmura")
    assert not idx.verb_forms.get("nagmuramura")
    assert not [
        e
        for e in idx.adjectives.get("muramura", [])
        if e.feats.get("REDUP_SEM") == "ITER"
    ]


@pytest.mark.parametrize("text", ["Mura ang bahay.", "Mura ang damit."])
def test_bare_scalar_predicate_parses(text: str) -> None:
    """The bare scalar adjective predicates normally ("X is cheap")."""
    assert len(parse_text(text)) >= 1, text


def test_redup_feeds_exclamative() -> None:
    """``mura-mura`` feeds the 10.E.1 ``Ang X-X …`` exclamative (the redup
    surfaces here; bare predicative redup stays deferred, no audit pressure)."""
    assert len(parse_text("Ang mura-mura ng bahay!")) >= 1


@pytest.mark.parametrize(
    "text",
    [
        "Mura na mura ang bahay.",   # newly enabled by this entry
        "Mura na mura ito.",
        "Mahal na mahal ang bahay.",  # antonym, already an ADJ — same rule
    ],
)
def test_bare_adj_linked_intensive(text: str) -> None:
    """The 10.E.2 linked-intensive (``X na X``) rule is ADJ-generic, so the
    new scalar ADJ licenses ``mura na mura`` "very cheap" — ``REDUP_SEM=INTENS``
    lifted to the matrix — the intensifier the informant reports alongside
    ``mahal na mahal`` (parallel to the ``ma-X na ma-X`` of 10.E.2)."""
    sems = set()
    for _ct, fs, _a, _d in parse_text(text):
        v = fs.feats.get("REDUP_SEM")
        if isinstance(v, str):
            sems.add(v)
    assert "INTENS" in sems, f"{text}: expected INTENS, got {sems}"
