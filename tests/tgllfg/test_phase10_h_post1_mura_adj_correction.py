# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.H.post-1 — scalar-ADJ ``mura`` analysis (still in force);
the curse-VERB retraction that 10.H.post-1 ALSO performed has been
reversed by Phase 10.final.pre-1 (see notes below).

Phase 10.H landed ``mura`` as a VERB "curse" (``mag`` / ``v_iter_redup``)
→ ``mura-mura`` ITER, justified as "collision-free" because the scalar
adjective was absent. The justification was the bug: the curse reading is
unattested across all eight project references, while the scalar ADJ
``mura`` "cheap" is canonical — S&O 1972 contrasts it with ``mahal``
(``Mahal ang damit na ito. Pero mura ang damit na iyan.``) and glosses
``mura-mura`` as "rather cheap" (the scalar-moderate redup). The original
10.H.post-1 informant (2026-05-26) confirmed two frequent, contrastive
ADJ senses — "cheap" (price, antonym of ``mahal``) and "young / tender /
unripe" — and reported never having met the curse VERB.

The 10.H.post-1 scalar-ADJ correction stands: ``mura`` is a single scalar
ADJ carrying both "cheap" and "young/tender/unripe" senses (no grammatical
reflex distinguishes them → a single PRED avoids spurious ambiguity),
opted into ``adj_redup`` so ``mura-mura`` is ``REDUP=FULL`` with
``REDUP_SEM`` left underspecified (the scalar-moderate "rather cheap"
reading the cell intends, not ITER).

**Phase 10.final.pre-1 update (2026-06-03)**: a multi-speaker native-
informant panel (Tagalog + Waray speakers + a linguist/language engineer)
reversed the curse-VERB retraction. The expert summary attests both an AV
mag- paradigm (``magmura`` / ``nagmumura``) and an OV -in/-hin paradigm
(``murahin`` / ``minura`` / ``mumurahin``) plus the ``pagmumura`` gerund —
all of which are productive in modern Tagalog. The curse senses now ship
as TWO separate lex entries (NOUN ``mura`` "profanity" in nouns.yaml,
VERB ``mura`` "to curse" in verbs.yaml — both semantically unrelated to
the ADJ "cheap" root, per the expert's mura₁/mura₂ analysis). The
``test_curse_verb_retracted`` test below is updated to assert the new
shipped state (the curse-VERB IS present, as 10.final.pre-1 added it)
and the ADJ ``mura-mura`` ``REDUP_SEM=None`` invariant is preserved.
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
    """The ADJ-derived ``mura-mura`` reaches ``REDUP=FULL`` with degree
    underspecified — the scalar-moderate "rather cheap" the ``adj_redup``
    cell intends, not ITER. The 10.H.post-1 ADJ analysis stands.

    **Phase 11.Y update (2026-06-04)**: post-11.Y the surface ``muramura``
    also has a VERB-iter-derived ADJ entry (``v_iter_redup`` POS-flip,
    ``lemma='mura-mura'`` carrying ``REDUP=FULL`` ``REDUP_SEM=ITER``).
    Both entries co-exist intentionally — disambiguated by lemma /
    ``REDUP_SEM`` / ``AV_ABSOL``. This test narrows to the ADJ-derived
    entry (``lemma='mura'``, no ``AV_ABSOL``) to assert the original
    invariant — the VERB-iter entry is verified separately in
    ``tests/tgllfg/test_phase11_y_mura_curse_iter.py``."""
    entries = _get_default()._index.adjectives.get("muramura", [])
    full = [e for e in entries if e.feats.get("REDUP") == "FULL"]
    assert full, f"expected REDUP=FULL adj for muramura; got {entries!r}"
    # Narrow to the ADJ-derived entry (10.H.post-1 adj_redup output).
    adj_derived = [e for e in full if e.feats.get("LEMMA") == "mura"]
    assert adj_derived, (
        f"expected ADJ-derived (lemma='mura') REDUP=FULL entry; "
        f"got {full!r}"
    )
    assert all(e.feats.get("REDUP_SEM") is None for e in adj_derived), (
        f"expected ADJ-derived muramura REDUP_SEM=None; got {adj_derived!r}"
    )


def test_curse_verb_shipped_under_10_final_pre_1() -> None:
    """**10.final.pre-1 update**: the curse-VERB is now shipped under a
    different paradigm than 10.H originally used. 10.H opted into
    ``v_iter_redup`` which would have produced ``mura-mura`` ITER —
    the surface-collision concern with the ADJ's ``adj_redup``
    ``mura-mura`` "rather cheap" that motivated the 10.H.post-1
    retraction in part. 10.final.pre-1 shipped the curse-VERB without
    ``v_iter_redup`` — only ``[mag, in_oblig, pag_gerund]`` — so
    inflected curse-VERB surfaces like ``nagmura`` / ``magmura`` /
    ``minura`` / ``murahin`` exist.

    **Phase 11.Y update (2026-06-04)**: ``v_iter_redup`` is now opted
    into the curse-VERB on attestation-pressure landing (informant
    pass confirms ``mura-mura`` curse-iter is productive parallel to
    ``iyak-iyak`` / ``tawa-tawa``). The surface-collision is now
    intentional — both the ADJ-derived ``REDUP_SEM=None`` reading
    and the VERB-iter ``REDUP_SEM=ITER`` reading co-exist at
    ``muramura``, disambiguated by lemma / ``REDUP_SEM`` / ``AV_ABSOL``.
    Both invariants below remain true post-11.Y because they pick
    the ADJ-derived entry specifically.

    This test asserts the invariants that hold across 10.final.pre-1
    and 11.Y:

    1. Inflected curse-VERB surfaces resolve to lemma=mura, POS=VERB
       (the curse-VERB IS shipped — reverses the 10.H.post-1 absence
       sentinel under native-informant evidence).
    2. The ADJ ``mura-mura`` (``muramura``) ADJ-derived entry has
       REDUP=FULL with REDUP_SEM=None — the 10.H.post-1 scalar-
       moderate analysis stands for the ADJ reading. (The 11.Y
       VERB-iter coexisting entry is verified in
       ``test_phase11_y_mura_curse_iter.py``.)
    """
    idx = _get_default()._index
    # 1. Inflected curse-VERB forms IS present (10.final.pre-1).
    nagmura = idx.verb_forms.get("nagmura") or []
    assert any(a.lemma == "mura" and a.pos == "VERB" for a in nagmura), (
        f"expected curse-VERB nagmura under 10.final.pre-1; got {nagmura!r}"
    )
    # 2. ADJ mura-mura still REDUP=FULL with REDUP_SEM=None (the
    #    10.H.post-1 scalar-moderate-not-ITER analysis is preserved).
    muramura_adj = idx.adjectives.get("muramura", [])
    full_no_sem = [
        e for e in muramura_adj
        if e.feats.get("REDUP") == "FULL" and e.feats.get("REDUP_SEM") is None
    ]
    assert full_no_sem, (
        f"expected ADJ muramura REDUP=FULL REDUP_SEM=None (no ITER); "
        f"got {muramura_adj!r}"
    )


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
