# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.E.6 — noun → affective-redup cell (alit / bunganga).

The reviewer's 2026-05-26 ITER-affective inventory included two
noun-primary roots — ``alit`` "conflict" and ``bunganga`` "mouth" —
held out of 10.E.4 because ``v_iter_redup`` is ``base_pos: VERB`` and
neither is cleanly a verb. The new ``noun_affective_redup`` cell
(``base_pos: NOUN``, ``pos: ADJ``) gives them their bare affective redup
as a predicative ADJ — ``alit-alit`` "bickering / at odds",
``bunganga-bunganga`` "mouthy / all talk" — with NO verbal inflection.

That non-inflecting design sidesteps the homophony that blocked ``alit``
in 10.E.4: ``mag-alit`` "quarrel" PFV ``nagalit`` would collide with
``galit``'s ``nagalit`` "got angry" in our hyphenless prefix-concat
engine. The cell generates no verb form, so no ``nagalit`` is injected
(the full ``alit`` "quarrel" verb, needing the prefix-before-vowel hyphen
``nag-alit`` ≠ ``nagalit``, is a named engine follow-on — a ~436-form
orthography change, out of scope here).
"""

import pytest

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import _get_default


# === Morphology: the noun_affective_redup cell output =================


@pytest.mark.parametrize(
    "surface,lemma",
    [
        ("alitalit", "alit-alit"),
        ("bungangabunganga", "bunganga-bunganga"),
    ],
)
def test_noun_affective_redup_produces_iter_adj(surface: str, lemma: str) -> None:
    """Each opted-in NOUN root produces an ``ADJ[PREDICATIVE]`` surface
    carrying ``REDUP=FULL`` + ``REDUP_SEM=ITER``, with the noun root as
    the hyphenated LEMMA (POS-flip-hyphenates-LEMMA convention)."""
    adjs = _get_default()._index.adjectives.get(surface, [])
    hits = [a for a in adjs if a.feats.get("REDUP_SEM") == "ITER"]
    assert len(hits) == 1, f"expected one ITER ADJ for {surface!r}; got {adjs!r}"
    a = hits[0]
    assert a.pos == "ADJ"
    assert a.feats.get("PREDICATIVE") is True
    assert a.feats.get("REDUP") == "FULL"
    assert a.feats.get("LEMMA") == lemma


@pytest.mark.parametrize("surface", ["alit", "bunganga"])
def test_root_still_indexed_as_bare_noun(surface: str) -> None:
    """The opt-in is additive — the root keeps its bare NOUN entry."""
    nouns = _get_default()._index.nouns.get(surface, [])
    assert any(n.pos == "NOUN" for n in nouns), f"{surface!r} lost its bare NOUN"


def test_no_verb_form_generated() -> None:
    """The cell is non-inflecting (NOUN→ADJ, no um/mag) — it must inject
    no verb form. In particular ``alit`` must not produce ``nagalit``
    (which would collide with ``galit``'s PFV), nor ``umalit`` /
    ``alitalit`` as verbs; the 10.E.3.post-2 inflected-moderative
    post-pass (gated on ``v_*_redup``) must not fire on these roots."""
    vf = _get_default()._index.verb_forms
    assert not vf.get("alitalit")
    assert not vf.get("umalit")
    assert not vf.get("bungangabunganga")
    # nagalit stays galit-only — no alit lemma injected.
    assert all(a.lemma != "alit" for a in vf.get("nagalit", []))


@pytest.mark.parametrize("surface", ["bakabaka", "bunsobunso"])
def test_opt_in_required(surface: str) -> None:
    """A NOUN not opted into ``noun_affective_redup`` produces no
    affective-redup ADJ — the cell is per-root gated (``baka`` "cow",
    ``bunso`` "youngest sibling" carry no redup affix_class)."""
    adjs = _get_default()._index.adjectives.get(surface, [])
    assert not [a for a in adjs if a.feats.get("REDUP_SEM") == "ITER"]


# === Grammar: the bare affective-noun predicate ========================


@pytest.mark.parametrize(
    "text",
    [
        "Alit-alit sila.",          # "they are at odds / bickering"
        "Bunganga-bunganga siya.",  # "he is mouthy / all talk"
        "Alitalit sila.",           # merged-surface input also parses
    ],
)
def test_affective_noun_redup_clause_parses(text: str) -> None:
    """The bare doubled predicate heads a clause via the existing Phase
    5g predicative-ADJ-S rule (no new grammar rule)."""
    assert len(parse_text(text)) >= 1, text


def test_clause_lifts_redup_sem_iter() -> None:
    """The predicative-ADJ-S rule lifts ``REDUP_SEM`` to the matrix —
    ``Alit-alit sila`` surfaces ``REDUP_SEM=ITER`` at the clause root,
    confirming the NOUN-derived redup integrates like the VERB-derived
    one (10.E.3)."""
    sems = {
        fs.feats.get("REDUP_SEM")
        for _ct, fs, _a, _d in parse_text("Alit-alit sila.")
        if isinstance(fs.feats.get("REDUP_SEM"), str)
    }
    assert "ITER" in sems
