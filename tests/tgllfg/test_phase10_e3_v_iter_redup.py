# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.E.3 — moderative / iterative V-stem full reduplication.

S&O 1972 §5.16 (moderative) + the native-reviewer productivity ruling
(2026-05-25): motion / activity / affective verb roots reduplicate fully
to a casual-iterative predicate — ``lakad`` → ``lakadlakad`` "walk
around / stroll", ``iyak`` → ``iyakiyak`` "crying repeatedly / whiny",
``kain`` → ``kainkain`` "snack / eat casually".

Modeled as a ``v_iter_redup`` paradigm cell (``base_pos: VERB``,
``pos: ADJ`` POS-flip, ``redup_root`` op) producing an
``ADJ[PREDICATIVE, REDUP=FULL, REDUP_SEM=ITER]`` surface — the verb root
rides up as the hyphenated LEMMA, the reserved ``REDUP_SEM=ITER`` marks
the construction. The existing Phase 5g predicative-ADJ-S rule consumes
it (``Iyak-iyak ang bata``) with no new grammar rule; the Phase 10.E.2
``REDUP_SEM`` matrix lift surfaces ITER at the clause root.

Productivity is per-root opt-in, semantically gated per the reviewer:
motion / activity / affective opt in (lakad, kain, inom, iyak, tawa);
formal/abstract verbs (``dumalo``) and weak adjectivals (``ginaw``) do
NOT. The *inflected* moderative (``gumala-gala`` / ``naglakad-lakad``)
is a separate paradigm-engine follow-on; ``tabi-tabi`` / ``uliuli`` are
lexicalized (Phase 10.G).
"""

import pytest

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import _get_default


# === Morphology: v_iter_redup cell output ==============================


@pytest.mark.parametrize(
    "surface,lemma",
    [
        ("lakadlakad", "lakad-lakad"),
        ("kainkain", "kain-kain"),
        ("iyakiyak", "iyak-iyak"),
        ("tawatawa", "tawa-tawa"),
        ("inominom", "inom-inom"),
    ],
)
def test_v_iter_redup_produces_iterative_adj(surface: str, lemma: str) -> None:
    """Each opted-in motion/activity/affective verb root produces a
    deverbal ``ADJ[PREDICATIVE]`` surface carrying ``REDUP=FULL`` +
    ``REDUP_SEM=ITER``, with the verb root as the hyphenated LEMMA
    (POS-flip-hyphenates-LEMMA convention)."""
    adjs = _get_default()._index.adjectives.get(surface, [])
    iters = [a for a in adjs if a.feats.get("REDUP_SEM") == "ITER"]
    assert len(iters) == 1, f"expected one ITER ADJ for {surface!r}; got {adjs!r}"
    a = iters[0]
    assert a.pos == "ADJ"
    assert a.feats.get("PREDICATIVE") is True
    assert a.feats.get("REDUP") == "FULL"
    assert a.feats.get("LEMMA") == lemma


@pytest.mark.parametrize("surface", ["ginawginaw", "dumalodalo", "dalodalo", "takbotakbo"])
def test_v_iter_redup_opt_in_required(surface: str) -> None:
    """Roots NOT opted into ``v_iter_redup`` produce no iterative-redup
    ADJ — the semantic-class gate holds. ``ginaw`` (weak adjectival) and
    ``dumalo`` (formal verb) are excluded per the reviewer ruling;
    ``takbo`` (``/o/``-final, raise-ambiguous) is deferred."""
    adjs = _get_default()._index.adjectives.get(surface, [])
    assert not [a for a in adjs if a.feats.get("REDUP_SEM") == "ITER"]


def test_opted_in_roots_still_inflect_normally() -> None:
    """Adding the ``v_iter_redup`` opt-in is additive — the roots keep
    their ordinary voice inflection (``kumain`` / ``umiyak`` / ... )."""
    idx = _get_default()._index
    for inflected in ("kumain", "umiyak", "lumakad", "uminom", "tumawa"):
        assert idx.verb_forms.get(inflected), f"{inflected!r} lost its inflection"


# === Grammar: the bare iterative predicate ============================


@pytest.mark.parametrize(
    "text",
    [
        "Iyak-iyak ang bata.",      # affective: "the child is whiny / crying"
        "Lakad-lakad ang lalaki.",  # motion: "the man strolls / walks around"
        "Kain-kain ang mga bata.",  # activity: "the children snack / eat casually"
        "Iyakiyak ang bata.",       # merged-surface input also parses
    ],
)
def test_iterative_predicate_parses(text: str) -> None:
    """The deverbal iterative ADJ heads a predicative clause via the
    existing Phase 5g predicative-ADJ-S rule (no new grammar rule)."""
    assert len(parse_text(text)) >= 1, text


@pytest.mark.parametrize("text", ["Iyak-iyak ka.", "Iyak-iyak siya."])
def test_iterative_predicate_with_2p_clitic(text: str) -> None:
    """A 2P pronominal subject (``ka`` / ``siya``) attaches to the bare
    iterative predicate like any predicative ADJ."""
    assert len(parse_text(text)) >= 1, text


def test_clause_lifts_redup_sem_iter() -> None:
    """The Phase 10.E.2 ``(↑ REDUP_SEM) = ↓1 REDUP_SEM`` lift on the
    predicative-ADJ-S rule generalises to ITER — ``Iyak-iyak ang bata``
    surfaces ``REDUP_SEM=ITER`` on the matrix f-structure."""
    sems = {
        fs.feats.get("REDUP_SEM")
        for _ct, fs, _a, _d in parse_text("Iyak-iyak ang bata.")
        if isinstance(fs.feats.get("REDUP_SEM"), str)
    }
    assert "ITER" in sems
