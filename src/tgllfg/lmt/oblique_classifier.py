# tgllfg/lmt/oblique_classifier.py

"""Phase 5 §8 — sa-NP → typed OBL-θ classification.

Phase 4 §7.1 leaves all *sa*-marked NPs (``NP[CASE=DAT]``) in the
matrix f-structure's ``ADJUNCT`` set, regardless of whether they are
arguments (locative goals, recipients, beneficiaries) or modifiers
(setting locatives, temporal adjuncts). Phase 5 §8 reclassifies the
argument *sa*-NPs into typed ``OBL-θ`` slots based on the LMT
engine's role-to-GF prediction.

This module implements that pass as a post-solve mutation:
:func:`classify_oblique_slots` walks the matrix f-structure, takes
each ``ADJUNCT`` member with ``CASE=DAT``, and moves it into the
typed slot the LMT engine predicted (``OBL-LOC`` /
``OBL-GOAL`` / ``OBL-BEN`` / ``OBL-INSTR`` / ``OBL-RECIP``). Members
that don't match any predicted ``OBL-θ`` role stay in ``ADJUNCT``
as locative modifiers. ADJUNCT members without ``CASE=DAT``
(adverbial enclitics from §7.3, demonstratives, etc.) are
untouched.

Why post-solve mutation, not grammar-rule rewrite: the §7.5
relativization, §7.3 clitic placement, §7.4 ay-inversion, and §7.8
quantifier float all consume the parser's c-tree and the same
``↓N ∈ (↑ ADJUNCT)`` equations as before. Rewriting the grammar
to emit ``OBL-X`` directly would require duplicating each rule per
verb-class and fight the non-conflict matcher. Post-solve mutation
contains the blast radius.

Multi-OBL semantic disambiguation (Phase 5c §8 follow-on, Commit 6)
augments the original positional matching with a noun-class lookup:
when multiple OBL-θ roles compete for multiple sa-NPs, each sa-NP's
``LEMMA`` is consulted against small lemma → semantic-class tables
(``_PLACE_LEMMAS``, ``_ANIMATE_LEMMAS``) to bias the assignment —
``palengke`` / ``eskwela`` prefer ``OBL-LOC`` / ``OBL-GOAL`` slots;
``bata`` / ``nanay`` prefer ``OBL-RECIP`` / ``OBL-BEN``. Positional
order is the fallback when no semantic preference applies, or when
both sa-NPs have the same class.
"""

from __future__ import annotations

from collections.abc import Mapping

from ..common import FStructure
from ..fstruct import Diagnostic
from .common import Role


def _is_obl_theta(gf: str) -> bool:
    """True iff `gf` is a typed-OBL governable function (e.g.,
    ``OBL-LOC``)."""
    return gf.startswith("OBL-")


def _sa_np_candidates(adjunct: frozenset) -> list[FStructure]:
    """Return ADJUNCT members that look like *sa*-NPs (CASE=DAT)
    sorted by canonical-node id (approximately surface order)."""
    out: list[FStructure] = []
    for member in adjunct:
        if isinstance(member, FStructure) and member.feats.get("CASE") == "DAT":
            out.append(member)
    out.sort(key=lambda m: m.id)
    return out


# Phase 5c §8 follow-on (Commit 6): small lemma → semantic class
# tables consulted for multi-OBL disambiguation. PLACE lemmas
# attract LOC / GOAL slots; ANIMATE lemmas attract RECIP / BEN
# slots. Both sets are deliberately small — a real corpus-driven
# classifier would consult a richer noun ontology, but the
# project's seed lexicon doesn't yet carry that information.
# Listed lemmas come from :file:`data/tgl/nouns.yaml`.
_PLACE_LEMMAS: frozenset[str] = frozenset({
    "palengke", "eskwela", "bahay", "simbahan", "tindahan",
    "parke",
})
_ANIMATE_LEMMAS: frozenset[str] = frozenset({
    "bata", "nanay", "tatay", "lalaki", "babae", "anak",
    "kapatid", "kaibigan", "tao", "aso", "pusa", "ibon",
    "isda", "kabayo", "baboy", "manok", "baka", "kambing",
    "pamilya",
})


def _semantic_class(np: FStructure) -> str | None:
    """Return ``"PLACE"`` / ``"ANIMATE"`` / ``None`` for an
    NP f-structure, based on its head-noun ``LEMMA`` (percolated
    by the Phase 5c grammar's NP / N rules)."""
    lemma = np.feats.get("LEMMA")
    if not isinstance(lemma, str):
        return None
    if lemma in _PLACE_LEMMAS:
        return "PLACE"
    if lemma in _ANIMATE_LEMMAS:
        return "ANIMATE"
    return None


def _gf_prefers_class(gf: str) -> str | None:
    """Return the semantic class an ``OBL-θ`` slot prefers, or
    ``None`` for slots without a clear preference. ``OBL-LOC`` /
    ``OBL-GOAL`` prefer PLACE; ``OBL-RECIP`` / ``OBL-BEN`` prefer
    ANIMATE; ``OBL-INSTR`` and unknown suffixes return ``None``
    (positional matching)."""
    if gf in ("OBL-LOC", "OBL-GOAL"):
        return "PLACE"
    if gf in ("OBL-RECIP", "OBL-BEN"):
        return "ANIMATE"
    return None


def classify_oblique_slots(
    f: FStructure,
    mapping: Mapping[Role, str],
) -> list[Diagnostic]:
    """Move ``ADJUNCT`` members with ``CASE=DAT`` into the typed
    ``OBL-θ`` slots predicted by `mapping`. Mutates `f` in place.

    The matching is positional in role iteration order (which is the
    lex entry's a-structure order, since
    :func:`tgllfg.lmt.compute_mapping` populates the result dict that
    way). When the count of ``OBL-θ`` roles exceeds the count of
    candidate sa-NPs, leftover roles stay unfilled — the
    well-formedness completeness check will flag them. When the count
    of sa-NPs exceeds the count of roles, leftover sa-NPs stay in
    ``ADJUNCT`` as locative modifiers.

    Returns a list of :class:`Diagnostic` records. Multi-OBL with
    cardinality mismatch produces an ``lmt-mismatch`` informational
    diagnostic that records the unfilled / leftover state so a future
    pass can disambiguate semantically.
    """
    obl_targets: list[str] = [
        gf for gf in mapping.values() if _is_obl_theta(gf)
    ]
    if not obl_targets:
        return []

    adj_value = f.feats.get("ADJUNCT")
    if not isinstance(adj_value, frozenset):
        return []

    sa_candidates = _sa_np_candidates(adj_value)
    non_sa_members = [
        m for m in adj_value
        if not (
            isinstance(m, FStructure) and m.feats.get("CASE") == "DAT"
        )
    ]

    if not sa_candidates:
        return []

    diagnostics: list[Diagnostic] = []

    # Phase 5c §8 follow-on (Commit 6): when multiple OBL-θ roles
    # compete for multiple sa-NPs, prefer semantic matching first
    # (PLACE lemma → LOC/GOAL slot; ANIMATE lemma → RECIP/BEN
    # slot), then fall back to positional. Pure positional remains
    # the only choice for single-OBL or when no semantic
    # preference applies.
    consumed_sa: list[int] = []
    pending_targets = list(enumerate(obl_targets))

    if len(obl_targets) >= 2 and len(sa_candidates) >= 2:
        sa_classes = [_semantic_class(np) for np in sa_candidates]
        # Greedy: walk targets in order; for each target with a
        # semantic preference, find the first un-consumed sa-NP
        # whose class matches. If found, consume it; otherwise
        # leave the target for the positional pass.
        deferred: list[tuple[int, str]] = []
        for ti, target_gf in pending_targets:
            if target_gf in f.feats:
                # Pre-existing slot from some other path; skip
                # without consuming an sa-NP. (Defensive — no
                # current path writes OBL-X before this pass.)
                continue
            preferred_class = _gf_prefers_class(target_gf)
            if preferred_class is None:
                deferred.append((ti, target_gf))
                continue
            match_idx: int | None = None
            for ci, cls in enumerate(sa_classes):
                if ci in consumed_sa:
                    continue
                if cls == preferred_class:
                    match_idx = ci
                    break
            if match_idx is None:
                deferred.append((ti, target_gf))
                continue
            f.feats[target_gf] = sa_candidates[match_idx]
            consumed_sa.append(match_idx)
        pending_targets = deferred

    # Positional pass for remaining targets / single-OBL case:
    # walk un-consumed sa-NPs in id order, assigning them to the
    # remaining targets in their original a-structure order.
    # Pre-filled targets are skipped (their sa-NP stays in
    # ADJUNCT).
    remaining_sa = [i for i in range(len(sa_candidates)) if i not in consumed_sa]
    sa_iter = iter(remaining_sa)
    for ti, target_gf in pending_targets:
        if target_gf in f.feats:
            continue
        try:
            si = next(sa_iter)
        except StopIteration:
            break
        f.feats[target_gf] = sa_candidates[si]
        consumed_sa.append(si)

    # Reassemble ADJUNCT: non-sa members + leftover sa-NPs.
    leftover_sa = [
        sa_candidates[i] for i in range(len(sa_candidates))
        if i not in consumed_sa
    ]
    new_members = non_sa_members + leftover_sa
    if new_members:
        f.feats["ADJUNCT"] = frozenset(new_members)
    else:
        # Empty ADJUNCT after classification — drop the key so the
        # f-structure looks clean.
        del f.feats["ADJUNCT"]

    # Diagnose cardinality mismatches that left OBL roles unfilled
    # or sa-NPs unmatched. Both cases are common in well-formed
    # natural language — leftover sa-NPs are locative modifiers,
    # unfilled OBL slots indicate a missing argument that
    # completeness will surface — so the diagnostic stays
    # informational.
    if len(obl_targets) > len(sa_candidates):
        diagnostics.append(Diagnostic(
            kind="lmt-mismatch",
            message=(
                f"OBL-θ classifier: {len(obl_targets)} role(s) "
                f"{obl_targets} but only {len(sa_candidates)} sa-NP(s) "
                "in ADJUNCT; leftover roles unfilled (completeness "
                "will flag)"
            ),
            detail={
                "roles": list(obl_targets),
                "sa_count": len(sa_candidates),
            },
        ))
    elif len(sa_candidates) > len(obl_targets):
        diagnostics.append(Diagnostic(
            kind="lmt-mismatch",
            message=(
                f"OBL-θ classifier: {len(sa_candidates)} sa-NP(s) "
                f"in ADJUNCT but only {len(obl_targets)} OBL role(s) "
                f"{obl_targets}; {len(sa_candidates) - len(obl_targets)} "
                "sa-NP(s) stay in ADJUNCT as locative modifiers"
            ),
            detail={
                "roles": list(obl_targets),
                "sa_count": len(sa_candidates),
            },
        ))

    return diagnostics
