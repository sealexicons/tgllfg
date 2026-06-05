# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 11.Y — ``v_iter_redup`` opt-in on curse-VERB ``mura``.

Closes the deferral pinned by the 10.final.pre-1 ``verbs.yaml``
comment block ("v_iter_redup intentionally NOT opted-in ... Can be
added later under audit-corpus attestation pressure"). The
2026-06-04 informant / reviewer pass (see
``project_mura_mura_attestation`` memory) confirmed ``mura-mura``
from the curse-VERB is common, productive ITER/HABITUAL
reduplication parallel to ``iyak-iyak`` / ``tawa-tawa``. The
surface-collision with the ADJ ``adj_redup`` ``mura-mura`` "rather
cheap" is now intentional — both readings co-exist, distinguished
by lemma / ``REDUP_SEM`` / ``AV_ABSOL``.

Two attested exemplars (informant): one parses post-11.Y via the
existing predicative-ADJ + ``puro X ang Y`` path; the NP-head
possessor exemplar (``ang mura-mura niya``) is out of 11.Y scope
(nominalized-ITER-in-NP-head is a separate construction-class
question, flagged as a future follow-on).
"""

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import _get_default


# === Cross-POS sentry at the muramura surface ===========================


class TestMuramuraCrossPOSSentry:
    """The ``muramura`` surface admits BOTH ADJ-redup intensive (the
    pre-11.Y ``adj_redup`` reading) AND VERB-iter cursing (the new
    11.Y ``v_iter_redup`` opt-in). The two are distinguished by
    lemma / ``REDUP_SEM`` / ``AV_ABSOL`` — entry [0] from the VERB
    path carries ``lemma='mura-mura'``, ``REDUP=FULL``,
    ``REDUP_SEM=ITER``, ``AV_ABSOL=True``; entry [1] from the ADJ
    path carries ``lemma='mura'``, ``REDUP=FULL``, no
    ``REDUP_SEM``."""

    def test_both_lemma_paths_present(self) -> None:
        # Both ADJ-derived (lemma='mura', adj_redup) and
        # VERB-iter-derived (lemma='mura-mura', v_iter_redup POS-flip)
        # entries co-exist at the muramura surface — the cross-POS
        # invariant 11.Y delivers.
        entries = _get_default()._index.adjectives.get("muramura", [])
        adj_derived = [e for e in entries if e.feats.get("LEMMA") == "mura"]
        verb_derived = [e for e in entries if e.feats.get("LEMMA") == "mura-mura"]
        assert adj_derived, (
            f"expected ADJ-derived (LEMMA=mura) entry at muramura; "
            f"got {entries!r}"
        )
        assert verb_derived, (
            f"expected VERB-iter-derived (LEMMA=mura-mura) entry at "
            f"muramura; got {entries!r}"
        )

    def test_adj_derived_redup_sem_none(self) -> None:
        # The ADJ-derived entry preserves the 10.H.post-1
        # scalar-moderate analysis — REDUP=FULL, REDUP_SEM=None.
        entries = _get_default()._index.adjectives.get("muramura", [])
        adj_derived = [e for e in entries if e.feats.get("LEMMA") == "mura"]
        assert adj_derived
        for e in adj_derived:
            assert e.feats.get("REDUP") == "FULL"
            assert e.feats.get("REDUP_SEM") is None
            # The ADJ path is NOT AV_ABSOL (that's a VERB-side feat).
            assert not e.feats.get("AV_ABSOL")

    def test_verb_derived_redup_sem_iter(self) -> None:
        # The VERB-iter-derived entry carries the new productive ITER
        # reading per the 2026-06-04 informant attestation.
        entries = _get_default()._index.adjectives.get("muramura", [])
        verb_derived = [e for e in entries if e.feats.get("LEMMA") == "mura-mura"]
        assert verb_derived
        for e in verb_derived:
            assert e.feats.get("REDUP") == "FULL"
            assert e.feats.get("REDUP_SEM") == "ITER"
            # The VERB-iter path carries forward the AV_ABSOL feat from
            # the curse-VERB lex entry (Phase 9.O B3.A pattern).
            assert e.feats.get("AV_ABSOL") is True
            # And the PREDICATIVE feat from the v_iter_redup cell
            # (VERB→ADJ POS-flip → predicative-ADJ rule).
            assert e.feats.get("PREDICATIVE") is True


# === Bare predicative VERB-iter parses ==================================


class TestMuramuraVerbIterPredicative:
    """``Mura-mura X.`` "X keeps cursing" parses via the 11.Y opt-in:
    the v_iter_redup POS-flip produces a predicative ADJ, consumed by
    the standard predicative-ADJ rule with a NOM-NP SUBJ. Mirrors the
    canonical ``Iyak-iyak siya.`` / ``Tawa-tawa siya.`` parse shape."""

    def test_bare_predicative_with_pron_subj(self) -> None:
        # Canonical bare predicative VERB-iter — parallels
        # ``Iyak-iyak siya.`` (10.E.3 anchor).
        rs = parse_text("Mura-mura siya.", n_best=10)
        assert rs, "Mura-mura siya. should parse via 11.Y v_iter_redup opt-in"
        # At least one parse carries REDUP_SEM=ITER (the new path).
        sems = {parse[1].feats.get("REDUP_SEM") for parse in rs}
        assert "ITER" in sems, (
            f"expected ITER among REDUP_SEM readings; got {sems}"
        )

    def test_bare_predicative_with_full_np_subj(self) -> None:
        # Same shape with full-NP SUBJ instead of pronoun.
        rs = parse_text("Mura-mura ang lalaki.", n_best=10)
        assert rs, (
            "Mura-mura ang lalaki. should parse via 11.Y v_iter_redup opt-in"
        )
        sems = {parse[1].feats.get("REDUP_SEM") for parse in rs}
        assert "ITER" in sems


# === Informant-attested exemplar (the one that parses) ==================


class TestMuramuraInformantExemplar:
    """The 2026-06-04 informant supplied 3 attested exemplars. Two
    use the redup form ``mura-mura``; the third uses a different
    construction (``X nang X`` intensive-repetition,
    ``Mura nang mura siya sa referee.``) which is NOT 11.Y scope.

    Of the 2 redup-form exemplars, 1 parses via 11.Y (the
    ``puro X ang Y lumabas`` shape that admits ``mura-mura`` as
    predicative-ADJ daughter) and 1 does not (the NP-head possessor
    ``ang mura-mura niya`` requires a nominalized-ITER-in-NP-head
    rule that is out of 11.Y scope — flagged as separate
    construction-class follow-on)."""

    def test_puro_mura_mura_ang_lumabas_parses(self) -> None:
        # ``Puro mura-mura ang lumabas sa bibig niya.``
        # "Nothing but curses came out of his mouth."
        # Parses post-11.Y via the predicative-ADJ rule (v_iter_redup
        # output) embedded in the ``puro X ang Y`` construction.
        rs = parse_text(
            "Puro mura-mura ang lumabas sa bibig niya.",
            n_best=10,
        )
        assert rs, (
            "informant exemplar should parse via 11.Y predicative-ADJ "
            "path"
        )
        sems = {parse[1].feats.get("REDUP_SEM") for parse in rs}
        assert "ITER" in sems, f"expected ITER reading; got {sems}"


# === Scope preservation (existing paths unchanged) ======================


class TestMuramuraScopePreserved:
    """The 11.Y opt-in adds the VERB-iter path WITHOUT disrupting
    the existing ADJ paths. Each pre-11.Y form continues to parse
    with its original f-structure shape, possibly with additional
    parses from the new VERB-iter path co-existing in the forest."""

    def test_ang_exclamative_still_parses(self) -> None:
        # ``Ang mura-mura ng bahay!`` (10.E.1 exclamative) —
        # pre-11.Y produced 1 parse (REDUP_SEM=INTENS). Post-11.Y
        # produces multiple parses (forest expansion), but the
        # INTENS reading must still be present.
        rs = parse_text("Ang mura-mura ng bahay!", n_best=10)
        assert rs, "Ang mura-mura ng bahay! should still parse"
        sems = {parse[1].feats.get("REDUP_SEM") for parse in rs}
        assert "INTENS" in sems, (
            f"expected INTENS reading preserved at exclamative; got {sems}"
        )

    def test_bare_predicative_scalar_adj_still_parses(self) -> None:
        # ``Mura ang bahay.`` — bare scalar ADJ predicate (no redup);
        # unaffected by 11.Y (no v_iter_redup pathway at bare-stem).
        rs = parse_text("Mura ang bahay.", n_best=10)
        assert rs, "Mura ang bahay. should still parse (10.H.post-1 ADJ)"

    def test_inflected_curse_verb_still_parses(self) -> None:
        # ``Nagmura siya.`` "He cursed/swore." — pre-11.Y curse-VERB
        # AV mag- form; 11.Y only adds v_iter_redup to the affix_class
        # list, doesn't disturb mag/in_oblig/pag_gerund cells.
        rs = parse_text("Nagmura siya.", n_best=10)
        assert rs, "Nagmura siya. should still parse (10.final.pre-1 mag)"
