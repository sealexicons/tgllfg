# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.E.3.post-2 — inflected moderative / iterative V-stem redup.

The eventive counterpart of the bare 10.E.3 forms (reviewer 2026-05-26):
an inflected first member + the bare root, e.g. ``lumakad`` →
``lumakad-lakad`` "walked around", ``umiyak`` → ``umiyak-iyak`` "kept
crying". Only the first member carries voice / aspect; the construction
is AV-primary (non-AV is lexically licensed, not productively generated).

Modeled as an inline post-pass in ``_index_verb_paradigms``: for each
basic AV form (``um`` / ``mag``) of a root already opted into the bare
V-stem redup cells, also emit ``surface + citation`` as a VERB carrying
the same VOICE / ASPECT + ``REDUP=FULL`` and the root's ``REDUP_SEM``
class (CASUAL for lakad/kain/inom; ITER for iyak/tawa). No new op
(the doubling reuses the ``redup_root`` "append to the inflected first
copy" semantics) and no new grammar rule (the existing AV-verb S frames
consume it).

Representation note (decision A, 2026-05-26): ``REDUP_SEM`` rides on the
VERB analysis as a predicate-level / lexical-aspectual property; it is
*not* percolated to the matrix f-structure root (that would require
adding it to the universal ``_VERB_PERCOLATION`` tuple, polluting every
verb clause with an empty node). The bare-ADJ path surfaces it at the
clause because there the ADJ *is* the predicate. Matrix percolation is
parked with the U-bucket empty-FStructure work.

The reviewer's canonical ``naglakad-lakad`` (mag-) needs ``mag`` on
``lakad``'s affix_class — a lexicon-inventory change folded into 10.E.4;
here ``lakad`` is um-only, so the produced form is ``lumakad-lakad``.
"""

import pytest

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import _get_default


# === Morphology: the inflected moderative VERB surfaces ===============


@pytest.mark.parametrize(
    "surface,lemma,aspect,sem",
    [
        ("lumakadlakad", "lakad", "PFV", "CASUAL"),
        ("lumalakadlakad", "lakad", "IPFV", "CASUAL"),
        ("lalakadlakad", "lakad", "CTPL", "CASUAL"),
        ("kumainkain", "kain", "PFV", "CASUAL"),
        ("uminominom", "inom", "PFV", "CASUAL"),
        ("umiyakiyak", "iyak", "PFV", "ITER"),
        ("tumawatawa", "tawa", "PFV", "ITER"),
    ],
)
def test_inflected_moderative_verb_surface(
    surface: str, lemma: str, aspect: str, sem: str
) -> None:
    """Each basic-AV form of an opted-in root yields a doubled VERB
    surface carrying VOICE=AV + its ASPECT + REDUP=FULL + the root's
    REDUP_SEM class, with the verb root as the (unhyphenated) lemma."""
    forms = _get_default()._index.verb_forms.get(surface, [])
    redups = [
        a for a in forms
        if a.feats.get("REDUP") == "FULL" and a.feats.get("REDUP_SEM") == sem
    ]
    assert len(redups) == 1, f"expected one {sem} moderative VERB for {surface!r}; got {forms!r}"
    a = redups[0]
    assert a.pos == "VERB"
    assert a.lemma == lemma
    assert a.feats.get("VOICE") == "AV"
    assert a.feats.get("ASPECT") == aspect


@pytest.mark.parametrize("surface", ["dumalodalo", "ginawginaw"])
def test_inflected_moderative_opt_in_required(surface: str) -> None:
    """A root NOT opted into the V-stem redup cells produces no inflected
    moderative VERB — the post-pass is gated on the shared opt-in.
    (``takbo`` is opted in as of 10.E.4.)"""
    forms = _get_default()._index.verb_forms.get(surface, [])
    assert not [a for a in forms if a.feats.get("REDUP_SEM") in ("CASUAL", "ITER")]


def test_inflected_moderative_is_av_only() -> None:
    """The post-pass fires only for AV cells — an OV-inflected stem does
    not gain a moderative-redup VERB (non-AV is lexically licensed, not
    productively generated). ``kinain`` (OV) yields no ``kinainkain``
    moderative."""
    forms = _get_default()._index.verb_forms.get("kinainkain", [])
    assert not [a for a in forms if a.feats.get("REDUP_SEM")]


# === Grammar: the inflected moderative heads an eventive clause =======


@pytest.mark.parametrize(
    "text,aspect",
    [
        ("Lumakad-lakad ang lalaki.", "PFV"),
        ("Lumalakad-lakad ang lalaki.", "IPFV"),
        ("Lalakad-lakad ang lalaki.", "CTPL"),
        ("Kumain-kain ang bata.", "PFV"),
        ("Umiyak-iyak ang bata.", "PFV"),
    ],
)
def test_inflected_moderative_clause_parses(text: str, aspect: str) -> None:
    """The doubled VERB heads an ordinary AV clause via the existing
    V-initial S frames (no new grammar rule); the hyphen-merge tokenizer
    collapses the input. The matrix carries VOICE=AV and the inflected
    ASPECT (REDUP_SEM stays verb-level per decision A)."""
    parses = parse_text(text)
    assert len(parses) >= 1, text
    matrix_ok = any(
        fs.feats.get("VOICE") == "AV" and fs.feats.get("ASPECT") == aspect
        for _ct, fs, _a, _d in parses
    )
    assert matrix_ok, f"no AV/{aspect} matrix for {text!r}"


def test_inflected_moderative_distinct_from_bare_adj() -> None:
    """The inflected moderative is a VERB; the bare 10.E.3 form is an
    ADJ. Distinct surfaces (``lumakadlakad`` vs ``lakadlakad``) keep the
    eventive-vs-property split clean."""
    idx = _get_default()._index
    assert any(a.pos == "VERB" for a in idx.verb_forms.get("lumakadlakad", []))
    assert "lumakadlakad" not in idx.adjectives
    assert any(a.pos == "ADJ" for a in idx.adjectives.get("lakadlakad", []))
