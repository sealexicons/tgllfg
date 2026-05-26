# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.E.4 — iterative-affective + casual redup vocabulary.

Opts existing VERB roots into the 10.E.3.post-1 redup cells and adds 14
native roots from the reviewer's 2026-05-26 inventory: one CASUAL
(`gala`) and 13 ITER-affective (ubo, bahing, hikbi, daing, kaway,
kembot, daldal, reklamo, sumbong, tampo, arte, drama, emote). Each gets
a minimal `[<AV affix>, v_(casual|iter)_redup]` entry — the bare redup
(`gala-gala`, `arte-arte`) plus, via 10.E.3.post-2, the inflected
moderative (`gumala-gala`, `nagreklamo-reklamo`).

`lakad` gains `mag` so the reviewer's canonical `naglakad-lakad` surfaces
alongside the `um`-based `lumakad-lakad`. Modern code-switch
(text/chat/post/selfie) is out of scope per the user; the noun-primary
`alit` / `bunganga` are deferred to a `noun → affective-redup` follow-on
(alit's `mag-alit` collides with `magalit` in our hyphenless engine;
bunganga's verbal sense is unattested).
"""

import pytest

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import _get_default


# === Bare redup of the new roots (ADJ via the POS-flip cell) ==========


@pytest.mark.parametrize(
    "surface,lemma,sem",
    [
        ("galagala", "gala-gala", "CASUAL"),
        ("uboubo", "ubo-ubo", "ITER"),
        ("bahingbahing", "bahing-bahing", "ITER"),
        ("hikbihikbi", "hikbi-hikbi", "ITER"),
        ("daingdaing", "daing-daing", "ITER"),
        ("kawaykaway", "kaway-kaway", "ITER"),
        ("kembotkembot", "kembot-kembot", "ITER"),
        ("daldaldaldal", "daldal-daldal", "ITER"),
        ("reklamoreklamo", "reklamo-reklamo", "ITER"),
        ("sumbongsumbong", "sumbong-sumbong", "ITER"),
        ("tampotampo", "tampo-tampo", "ITER"),
        ("artearte", "arte-arte", "ITER"),
        ("dramadrama", "drama-drama", "ITER"),
        ("emoteemote", "emote-emote", "ITER"),
    ],
)
def test_new_root_bare_redup(surface: str, lemma: str, sem: str) -> None:
    """Each new root produces its bare redup as an `ADJ[PREDICATIVE,
    REDUP=FULL]` with the class `REDUP_SEM` and the hyphenated LEMMA."""
    adjs = _get_default()._index.adjectives.get(surface, [])
    hits = [a for a in adjs if a.feats.get("REDUP_SEM") == sem]
    assert len(hits) == 1, f"expected one {sem} ADJ for {surface!r}; got {adjs!r}"
    a = hits[0]
    assert a.pos == "ADJ"
    assert a.feats.get("PREDICATIVE") is True
    assert a.feats.get("REDUP") == "FULL"
    assert a.feats.get("LEMMA") == lemma


# === Existing-root opt-ins ============================================


@pytest.mark.parametrize(
    "surface,sem",
    [
        ("tingintingin", "CASUAL"),
        ("kuwentokuwento", "CASUAL"),
        ("takbotakbo", "CASUAL"),
        ("sigawsigaw", "ITER"),
        ("ngitingiti", "ITER"),
        ("galitgalit", "ITER"),
    ],
)
def test_existing_root_optin_redup(surface: str, sem: str) -> None:
    """The six existing VERB roots gain their bare redup via the new
    `affix_class` opt-in. `takbo` is CASUAL with no `/o/`-raise per
    reviewer Q4 (`takbo-takbo`, not `takbu-takbo`)."""
    adjs = _get_default()._index.adjectives.get(surface, [])
    assert [a for a in adjs if a.feats.get("REDUP_SEM") == sem], (
        f"{surface!r} missing {sem} redup ADJ; got {adjs!r}"
    )


# === Inflected moderatives (VERB via 10.E.3.post-2) ===================


@pytest.mark.parametrize(
    "surface,lemma,aspect,sem",
    [
        ("gumalagala", "gala", "PFV", "CASUAL"),
        ("umuboubo", "ubo", "PFV", "ITER"),
        ("nagreklamoreklamo", "reklamo", "PFV", "ITER"),
        ("nagartearte", "arte", "PFV", "ITER"),
        ("nagaartearte", "arte", "IPFV", "ITER"),
    ],
)
def test_new_root_inflected_moderative(
    surface: str, lemma: str, aspect: str, sem: str
) -> None:
    """The 10.E.3.post-2 post-pass produces the inflected moderative for
    the new roots — `gumala-gala`, `nagreklamo-reklamo`, and the reviewer's
    `nag-aarte` IPFV pattern."""
    forms = _get_default()._index.verb_forms.get(surface, [])
    hits = [
        a for a in forms
        if a.feats.get("REDUP") == "FULL" and a.feats.get("REDUP_SEM") == sem
    ]
    assert len(hits) == 1, f"expected one {sem} moderative VERB for {surface!r}; got {forms!r}"
    a = hits[0]
    assert a.lemma == lemma
    assert a.feats.get("VOICE") == "AV"
    assert a.feats.get("ASPECT") == aspect


def test_lakad_gains_mag_moderative() -> None:
    """Adding `mag` to `lakad` surfaces the reviewer's canonical
    `naglakad-lakad` (mag-) alongside the `um`-based `lumakad-lakad`."""
    forms = _get_default()._index.verb_forms
    for surface in ("naglakadlakad", "lumakadlakad"):
        hits = [
            a for a in forms.get(surface, [])
            if a.feats.get("REDUP") == "FULL" and a.lemma == "lakad"
        ]
        assert hits, f"{surface!r} missing as a lakad moderative VERB"
        assert hits[0].feats.get("REDUP_SEM") == "CASUAL"


# === Grammar: the new vocabulary heads clauses ========================


@pytest.mark.parametrize(
    "text",
    [
        "Gumala-gala sila.",        # inflected CASUAL VERB
        "Umubo-ubo ang bata.",      # inflected ITER VERB
        "Arte-arte siya.",          # bare ITER ADJ predicate
        "Reklamo-reklamo ang lalaki.",  # bare ITER ADJ predicate
    ],
)
def test_affective_vocab_clause_parses(text: str) -> None:
    assert len(parse_text(text)) >= 1, text
