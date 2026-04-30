# tgllfg/lmt/principles.py

"""Phase 5 §8.2 — Bresnan–Kanerva LMT principles as named functions.

Each step of the canonical Bresnan & Kanerva (1989) procedure is one
pure function so the engine is testable in isolation. The orchestrator
:func:`compute_mapping` chains them; tests in
``tests/tgllfg/test_lmt_principles.py`` exercise each function against
textbook cases and the per-voice corpus lands in Commit 3.

Tagalog voice morphology is handled by storing per-voice intrinsic
profiles directly on the lex entry (Commit 4): each voice-affixed verb
form is a separate ``lex_entry`` row, so its
``intrinsic_classification`` JSONB already encodes which role is the
pivot. The engine therefore consumes pre-attached intrinsics —
``apply_voice_constraints`` exists for completeness, but the
runtime caller typically passes ``voice_constraints=None``.

XCOMP-bearing roles (COMPLEMENT, EVENT) are not in the
``[±r, ±o]`` truth table — they are open complements stipulated
by the lex entry's ``gf_defaults``. The orchestrator accepts a
``stipulated_gfs`` mapping that bypasses the truth table for those
roles while still letting them participate in the Subject Condition
(step 6) and biuniqueness (step 7) checks.
"""

from __future__ import annotations

from typing import Mapping, Sequence

from ..fstruct import Diagnostic
from .common import (
    IntrinsicClassification,
    IntrinsicFeatures,
    MappingResult,
    Role,
    obj_theta,
    obl_theta,
)


# === Role hierarchy ========================================================

ROLE_HIERARCHY: tuple[Role, ...] = (
    # Agent-like (highest)
    Role.AGENT,
    Role.ACTOR,
    Role.CAUSER,
    # Mid-thematic — beneficiaries, recipients, experiencers, goals.
    Role.BENEFICIARY,
    Role.RECIPIENT,
    Role.EXPERIENCER,
    Role.GOAL,
    Role.INSTRUMENT,
    Role.STIMULUS,
    # Patient-like (lower) — themes and patients of various flavors.
    Role.THEME,
    Role.CONVEYED,
    Role.PATIENT,
    Role.CAUSEE,
    Role.LOCATION,
    # Off-hierarchy clausal complements. Listed for completeness;
    # typically passed through via ``stipulated_gfs`` (XCOMP-bound).
    Role.COMPLEMENT,
    Role.EVENT,
)


def _hierarchy_index(role: Role) -> int:
    """Position of `role` in :data:`ROLE_HIERARCHY` (lower is higher).
    Roles not in the hierarchy sort last (treated as least
    SUBJ-eligible)."""
    try:
        return ROLE_HIERARCHY.index(role)
    except ValueError:
        return len(ROLE_HIERARCHY)


# === Default intrinsic table ===============================================

# Bresnan & Kanerva 1989 canonical intrinsic feature per role. Used by
# Commit 4 to bootstrap lex entries with empty
# ``intrinsic_classification`` JSONB; the runtime engine doesn't
# consult this directly — it expects the lex entry to carry a
# per-voice intrinsic profile because Tagalog voice morphology is
# voice-specific.

_DEFAULT_INTRINSICS: dict[Role, IntrinsicFeatures] = {
    # Non-objective intrinsic ([-o]) — the role cannot be OBJ-typed.
    Role.AGENT:        IntrinsicFeatures(o=False),
    Role.ACTOR:        IntrinsicFeatures(o=False),
    Role.CAUSER:       IntrinsicFeatures(o=False),
    Role.EXPERIENCER:  IntrinsicFeatures(o=False),
    Role.BENEFICIARY:  IntrinsicFeatures(o=False),
    Role.RECIPIENT:    IntrinsicFeatures(o=False),
    Role.GOAL:         IntrinsicFeatures(o=False),
    Role.INSTRUMENT:   IntrinsicFeatures(o=False),
    Role.LOCATION:     IntrinsicFeatures(o=False),
    # Unrestricted intrinsic ([-r]) — patient-like roles default to
    # the lex's natural OBJ candidate.
    Role.PATIENT:      IntrinsicFeatures(r=False),
    Role.THEME:        IntrinsicFeatures(r=False),
    Role.CONVEYED:     IntrinsicFeatures(r=False),
    Role.CAUSEE:       IntrinsicFeatures(r=False),
    Role.STIMULUS:     IntrinsicFeatures(r=False),
    # COMPLEMENT and EVENT are off-hierarchy XCOMP-bound roles; the
    # truth table doesn't apply, so we don't pre-classify.
}


def default_intrinsics(role: Role) -> IntrinsicFeatures:
    """Return `role`'s canonical intrinsic feature pair per
    Bresnan & Kanerva 1989.

    Used by Commit 4's lex-entry bootstrap to fill empty
    ``intrinsic_classification`` JSONB. The runtime engine does not
    consult this — it expects each lex entry to supply a complete
    per-voice intrinsic profile (since Tagalog voice morphology
    targets a specific argument per voice form).
    """
    return _DEFAULT_INTRINSICS.get(role, IntrinsicFeatures())


# === Step 2: voice constraint merge ========================================


def apply_voice_constraints(
    role_frame: Sequence[IntrinsicClassification],
    voice_constraints: Mapping[Role, IntrinsicFeatures] | None = None,
) -> list[IntrinsicClassification]:
    """Step 2: layer voice-imposed ``[±r, ±o]`` stamps on top of the
    lex entry's intrinsic profile.

    For Tagalog the lex entry typically already encodes voice-specific
    intrinsics (one ``lex_entry`` row per voice-affixed form), so
    ``voice_constraints`` is usually ``None`` and this is a no-op.
    The function exists so the seven-step BK pipeline is explicit at
    every stage and to support future voice-overlay use cases (e.g.,
    passive on a verb whose lex entry doesn't have its own
    passive-form row).

    Raises :class:`ValueError` (via
    :meth:`IntrinsicFeatures.merged_with`) if a constraint conflicts
    with a value already specified by the lex entry.
    """
    if not voice_constraints:
        return list(role_frame)
    new_frame: list[IntrinsicClassification] = []
    for ic in role_frame:
        constraint = voice_constraints.get(ic.role)
        if constraint is None:
            new_frame.append(ic)
        else:
            new_frame.append(
                ic.with_intrinsics(ic.intrinsics.merged_with(constraint))
            )
    return new_frame


# === Step 3: default classification ========================================


def fill_defaults(
    role_frame: Sequence[IntrinsicClassification],
) -> list[IntrinsicClassification]:
    """Step 3: fill remaining ``[±r, ±o]`` ``None`` slots from
    Bresnan & Kanerva 1989 defaults.

    Plan §8.2 wording: *"highest unmarked argument is [-o]; lower
    arguments default to [+o] or [+r] per role-hierarchy
    conventions."*

    Concretely:

    * If no role currently has ``o=False``, the highest-hierarchy
      role with ``o=None`` gets ``o=False`` (so step 4 has at least
      one SUBJ-via-[-o] candidate).
    * All remaining ``None`` ``o`` components default to ``True``
      (``+o``, objective).
    * All remaining ``None`` ``r`` components default to ``True``
      (``+r``, restricted).

    Lex entries that already supply complete per-voice profiles
    short-circuit this function (the Tagalog default after Commit 4).
    """
    new_frame = list(role_frame)
    has_minus_o = any(ic.intrinsics.o is False for ic in new_frame)
    if not has_minus_o:
        order = sorted(
            range(len(new_frame)),
            key=lambda i: _hierarchy_index(new_frame[i].role),
        )
        for i in order:
            ic = new_frame[i]
            if ic.intrinsics.o is None:
                new_frame[i] = ic.with_intrinsics(
                    IntrinsicFeatures(r=ic.intrinsics.r, o=False)
                )
                break
    for i, ic in enumerate(new_frame):
        r = ic.intrinsics.r if ic.intrinsics.r is not None else True
        o = ic.intrinsics.o if ic.intrinsics.o is not None else True
        if (r, o) != (ic.intrinsics.r, ic.intrinsics.o):
            new_frame[i] = ic.with_intrinsics(IntrinsicFeatures(r=r, o=o))
    return new_frame


# === Step 4: Subject Mapping ===============================================


def subject_mapping(
    role_frame: Sequence[IntrinsicClassification],
) -> int | None:
    """Step 4: pick the index of the role that maps to SUBJ.

    Returns ``None`` if no role qualifies (the Subject Condition,
    step 6, then fails). The selection cascade:

    1. Highest-hierarchy role with ``[-r, -o]`` (full
       SUBJ-eligibility — the Tagalog per-voice profile case).
    2. Otherwise, the highest-hierarchy role with ``o=False``
       (the plan's *"highest argument compatible with [-o]"*).
    3. Otherwise, the highest-hierarchy role with ``r=False``
       (the plan's fallback *"highest [-r]"*).
    4. ``None``.
    """
    # Primary: roles with both r=False and o=False.
    candidates = [
        i for i, ic in enumerate(role_frame)
        if ic.intrinsics.r is False and ic.intrinsics.o is False
    ]
    if candidates:
        return min(
            candidates,
            key=lambda i: _hierarchy_index(role_frame[i].role),
        )
    # Secondary: roles compatible with [-o].
    candidates = [
        i for i, ic in enumerate(role_frame)
        if ic.intrinsics.o is False
    ]
    if candidates:
        return min(
            candidates,
            key=lambda i: _hierarchy_index(role_frame[i].role),
        )
    # Tertiary: roles compatible with [-r].
    candidates = [
        i for i, ic in enumerate(role_frame)
        if ic.intrinsics.r is False
    ]
    if candidates:
        return min(
            candidates,
            key=lambda i: _hierarchy_index(role_frame[i].role),
        )
    return None


# === Step 5: non-subject mapping ===========================================


def non_subject_mapping(
    role: Role, intrinsics: IntrinsicFeatures
) -> str:
    """Step 5: GF assignment for a non-SUBJ role from its
    ``[±r, ±o]`` features.

    Truth table per Bresnan & Kanerva 1989:

    * ``[-r, +o]`` → ``OBJ`` (bare).
    * ``[+r, +o]`` → ``OBJ-θ`` (typed: ``OBJ-<role.gf_suffix>``).
    * ``[+r, -o]`` → ``OBL-θ`` (typed: ``OBL-<role.gf_suffix>``).
    * ``[-r, -o]`` → SUBJ (already taken by step 4; calling this
      indicates a duplicate-SUBJ situation that the orchestrator
      should have surfaced as a biuniqueness violation —
      :class:`ValueError`).

    Both `r` and `o` must be non-``None`` (step 3 ensures this).
    """
    r, o = intrinsics.r, intrinsics.o
    if r is None or o is None:
        raise ValueError(
            f"non_subject_mapping requires fully-specified intrinsics; "
            f"got r={r!r}, o={o!r}"
        )
    if r is False and o is True:
        return "OBJ"
    if r is True and o is True:
        return obj_theta(role)
    if r is True and o is False:
        return obl_theta(role)
    raise ValueError(
        f"role {role.value} has [-r, -o] (SUBJ-eligible) — "
        f"step 4 should have picked it, not step 5"
    )


# === Step 6: Subject Condition =============================================


def check_subject_condition(
    mapping: Mapping[Role, str],
    pred_name: str | None = None,
) -> Diagnostic | None:
    """Step 6: emit a ``subject-condition-failed`` diagnostic if no
    role maps to SUBJ.

    PRED-bearing f-structures must have a SUBJ. Step 4 returned
    ``None`` only when the lex entry's intrinsic profile didn't
    permit any SUBJ candidate — itself a lexicon bug, but the
    engine surfaces it as a structured diagnostic rather than
    asserting.
    """
    if any(gf == "SUBJ" for gf in mapping.values()):
        return None
    msg = "no role maps to SUBJ"
    if pred_name:
        msg = f"{msg} (PRED={pred_name})"
    return Diagnostic(kind="subject-condition-failed", message=msg)


# === Step 7: Biuniqueness ==================================================


def check_biuniqueness(
    mapping: Mapping[Role, str],
) -> tuple[Diagnostic, ...]:
    """Step 7: each role maps to exactly one GF and each GF receives
    at most one role.

    The role→GF dict structurally enforces "one role to one GF" (it's
    a Python ``dict`` keyed on roles). The function checks the GF
    arm: no two roles share a fully-qualified GF string. Typed forms
    ``OBJ-X`` and ``OBL-X`` are distinct GFs (e.g., ``OBJ-PATIENT``
    and ``OBJ-AGENT`` don't clash), so duplication only triggers
    when two roles map to the same exact string.
    """
    diagnostics: list[Diagnostic] = []
    seen: dict[str, Role] = {}
    for role, gf in mapping.items():
        prior = seen.get(gf)
        if prior is not None:
            diagnostics.append(Diagnostic(
                kind="lmt-biuniqueness-violated",
                message=(
                    f"GF {gf!r} is shared by roles {prior.value} "
                    f"and {role.value}"
                ),
            ))
        else:
            seen[gf] = role
    return tuple(diagnostics)


# === Orchestrator ==========================================================


def compute_mapping(
    role_frame: Sequence[IntrinsicClassification],
    voice_constraints: Mapping[Role, IntrinsicFeatures] | None = None,
    stipulated_gfs: Mapping[Role, str] | None = None,
    pred_name: str | None = None,
) -> MappingResult:
    """Compose the seven-step BK procedure.

    Step 1 (lex entry intrinsics) happens at the call site (Commit 4:
    the lexicon attaches per-voice intrinsics to lex entries). This
    function takes those intrinsics as ``role_frame`` and runs steps
    2 through 7.

    ``stipulated_gfs`` carves out roles whose GF the lex entry
    pre-determines (typically COMPLEMENT/EVENT → XCOMP for control
    verbs). They bypass the truth table but still participate in
    Subject Condition (a stipulated SUBJ counts) and biuniqueness
    checks.
    """
    stipulations = dict(stipulated_gfs or {})
    frame = apply_voice_constraints(role_frame, voice_constraints)
    frame = fill_defaults(frame)

    # Step 4: pick SUBJ from non-stipulated roles only. A stipulated
    # SUBJ can still satisfy the Subject Condition.
    free_indices = [
        i for i, ic in enumerate(frame) if ic.role not in stipulations
    ]
    free_frame = [frame[i] for i in free_indices]
    sub_idx_in_free = subject_mapping(free_frame)
    subj_idx: int | None = (
        free_indices[sub_idx_in_free] if sub_idx_in_free is not None else None
    )

    mapping: dict[Role, str] = dict(stipulations)
    if subj_idx is not None:
        mapping[frame[subj_idx].role] = "SUBJ"

    diagnostics: list[Diagnostic] = []
    # Step 5: truth-table the rest.
    for i, ic in enumerate(frame):
        if ic.role in stipulations:
            continue
        if i == subj_idx:
            continue
        if ic.intrinsics.r is False and ic.intrinsics.o is False:
            picked_role = (
                frame[subj_idx].role.value if subj_idx is not None else "<none>"
            )
            diagnostics.append(Diagnostic(
                kind="lmt-biuniqueness-violated",
                message=(
                    f"role {ic.role.value} has [-r, -o] but SUBJ went to "
                    f"{picked_role}; duplicate SUBJ candidate"
                ),
            ))
            continue
        mapping[ic.role] = non_subject_mapping(ic.role, ic.intrinsics)

    subj_diag = check_subject_condition(mapping, pred_name=pred_name)
    if subj_diag is not None:
        diagnostics.append(subj_diag)
    diagnostics.extend(check_biuniqueness(mapping))

    return MappingResult(mapping=mapping, diagnostics=tuple(diagnostics))
