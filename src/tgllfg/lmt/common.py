# tgllfg/lmt/common.py

"""Phase 5 §8.1 — Lexical Mapping Theory data types.

Defines the role inventory, intrinsic feature representation, and
mapping-result containers that the Phase 5 LMT engine builds on. The
engine itself (the Bresnan–Kanerva principles) lives in
``tgllfg.lmt.principles`` and is added in commit 2; this module is
purely declarative.

Design notes
------------

* :class:`Role` is an ``Enum`` with string values. The values match
  the role names already in use throughout :mod:`tgllfg.lexicon`'s
  ``a_structure`` and ``gf_defaults`` fields, so the LMT engine can
  consume and emit existing lexical entries without translation. The
  inventory unions the plan §8.1 core (10 textbook roles) with the
  Tagalog augmentation that surfaced during Phase 4 (CONVEYED for
  IV-conveyed pivots; CAUSER/CAUSEE/EVENT for §7.7 causatives;
  COMPLEMENT for §7.6 control; ACTOR for intransitives that the
  Phase 4 fallback emits). The augmentation is documented in
  ``docs/lmt.md`` (added in commit 8).

* :class:`IntrinsicFeatures` is the Bresnan–Kanerva ``[±r, ±o]``
  feature pair. Each component is a ternary ``True`` (``+``),
  ``False`` (``-``), or ``None`` (unspecified — to be filled by
  defaults in step 3 of the BK algorithm). Frozen + slot-poor so
  instances are hashable and serializable.

* :class:`IntrinsicClassification` pairs a role with its intrinsics.
  Lex entries store an ordered list of these (the verb's a-structure
  with intrinsics attached); the LMT engine consumes the list and
  returns a :class:`MappingResult`.

* :class:`MappingResult` is what ``compute_mapping`` returns: the
  role→GF assignment plus any diagnostics from the Subject Condition
  and biuniqueness checks. GFs are kept as plain strings (matching
  the rest of the codebase), with helpers :func:`obj_theta` /
  :func:`obl_theta` producing the typed forms ``OBJ-θ`` / ``OBL-θ``
  used by the BK truth table. The string forms align with
  :func:`tgllfg.fstruct.checks.is_governable_gf` which already
  recognizes the ``OBJ-`` and ``OBL-`` prefixes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

from ..common import LexicalEntry
from ..fstruct import Diagnostic


# === Role inventory ========================================================


class Role(Enum):
    """Theta roles. Values match the uppercase strings already in use
    throughout :mod:`tgllfg.lexicon` (``gf_defaults`` keys, ``a_structure``
    list members) so the LMT engine and the lexicon share a vocabulary."""

    # --- Plan §8.1 core inventory -----------------------------------------
    AGENT = "AGENT"
    PATIENT = "PATIENT"
    THEME = "THEME"
    GOAL = "GOAL"
    RECIPIENT = "RECIPIENT"
    BENEFICIARY = "BENEFICIARY"
    INSTRUMENT = "INSTRUMENT"
    LOCATION = "LOCATION"
    EXPERIENCER = "EXPERIENCER"
    STIMULUS = "STIMULUS"

    # --- Tagalog augmentation (Phase 4 §7 surface) -------------------------
    # Documented in docs/lmt.md (commit 8). The augmentation is kept
    # rather than folded back into the core because each carries a
    # distinct intrinsic-classification profile that the BK engine
    # consults: CONVEYED behaves like THEME but is voice-marked
    # differently in IV; CAUSER/CAUSEE/EVENT participate in causative
    # frames whose mapping diverges from monoclausal transitives;
    # ACTOR is the intransitive fallback emitted by
    # :func:`tgllfg.lexicon._synthesize_verb_entry`.
    ACTOR = "ACTOR"
    CONVEYED = "CONVEYED"
    CAUSER = "CAUSER"
    CAUSEE = "CAUSEE"
    EVENT = "EVENT"
    COMPLEMENT = "COMPLEMENT"

    @property
    def gf_suffix(self) -> str:
        """Short suffix used in ``OBJ-X`` / ``OBL-X`` typed GF strings.

        The suffix follows Tagalog-LFG convention (LOC for LOCATION,
        BEN for BENEFICIARY, INSTR for INSTRUMENT, RECIP for RECIPIENT)
        rather than the bare role name, so the typed GFs match the
        labels already used in :mod:`docs/analysis-choices` and the
        commit-1 grammar rules."""
        return _GF_SUFFIX.get(self, self.value)


_GF_SUFFIX: dict[Role, str] = {
    Role.LOCATION: "LOC",
    Role.BENEFICIARY: "BEN",
    Role.INSTRUMENT: "INSTR",
    Role.RECIPIENT: "RECIP",
}


# === Intrinsic features ====================================================


@dataclass(frozen=True)
class IntrinsicFeatures:
    """The Bresnan–Kanerva ``[±r, ±o]`` feature pair.

    ``r`` is the *restricted* feature: ``True`` (``+r``) means the
    role cannot map to SUBJ; ``False`` (``-r``) means it can.
    ``o`` is the *objective* feature: ``True`` (``+o``) means the
    role is object-like (OBJ or OBJ-θ); ``False`` (``-o``) means it
    is non-objective (SUBJ or OBL-θ).

    Either component may be ``None`` to indicate "unspecified by the
    lexical entry" — step 3 of the BK algorithm fills unspecified
    components from the default-classification table.

    The truth table over fully-specified features is::

        [-r, -o] → SUBJ        [-r, +o] → OBJ
        [+r, -o] → OBL-θ       [+r, +o] → OBJ-θ
    """

    r: bool | None = None
    o: bool | None = None

    def is_complete(self) -> bool:
        """True iff both components are specified (``True`` or
        ``False`` rather than ``None``)."""
        return self.r is not None and self.o is not None

    def merged_with(self, other: "IntrinsicFeatures") -> "IntrinsicFeatures":
        """Return a new :class:`IntrinsicFeatures` with `other`'s
        specified components overriding `self`'s ``None`` slots.

        Raises :class:`ValueError` if `other` specifies a value that
        conflicts with a value already specified on `self`. Voice
        morphology calls this to layer voice-imposed constraints on
        top of lexical intrinsics (step 2 of the BK algorithm)."""
        return IntrinsicFeatures(
            r=_merge_component(self.r, other.r, "r"),
            o=_merge_component(self.o, other.o, "o"),
        )


def _merge_component(
    a: bool | None, b: bool | None, name: str
) -> bool | None:
    if a is None:
        return b
    if b is None:
        return a
    if a != b:
        raise ValueError(
            f"intrinsic feature {name!r} conflict: {a} vs {b}"
        )
    return a


# === Classification + mapping result =======================================


@dataclass(frozen=True)
class IntrinsicClassification:
    """A single (role, intrinsics) pair from a verb's a-structure."""

    role: Role
    intrinsics: IntrinsicFeatures

    def with_intrinsics(
        self, intrinsics: IntrinsicFeatures
    ) -> "IntrinsicClassification":
        """Return a copy with the intrinsics replaced. Convenience
        for the BK steps that progressively refine the feature
        pair."""
        return IntrinsicClassification(role=self.role, intrinsics=intrinsics)


@dataclass(frozen=True)
class MappingResult:
    """The output of ``compute_mapping``.

    ``mapping`` is the role-to-GF assignment after all seven BK
    principles have been applied. ``diagnostics`` carries any Subject
    Condition or biuniqueness violations as :class:`Diagnostic`
    records; the caller decides whether they are blocking."""

    mapping: Mapping[Role, str]
    diagnostics: tuple[Diagnostic, ...] = field(default_factory=tuple)


# === GF helpers ============================================================


def obj_theta(role: Role) -> str:
    """The typed-OBJ GF string for `role` (e.g., ``OBJ-BEN``)."""
    return f"OBJ-{role.gf_suffix}"


def obl_theta(role: Role) -> str:
    """The typed-OBL GF string for `role` (e.g., ``OBL-LOC``)."""
    return f"OBL-{role.gf_suffix}"


# === Default intrinsic table ==============================================

# Bresnan & Kanerva 1989 canonical intrinsic feature per role. Used
# by :func:`intrinsics_for` to fill empty
# ``LexicalEntry.intrinsic_classification`` slots; the runtime LMT
# engine doesn't consult this directly — it expects each lex entry
# to supply a per-voice intrinsic profile (since Tagalog voice
# morphology targets a specific argument per voice form).

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

    Used by :func:`intrinsics_for` to fill empty
    ``intrinsic_classification`` slots. The runtime engine does not
    consult this — it expects each lex entry to supply a complete
    per-voice intrinsic profile (since Tagalog voice morphology
    targets a specific argument per voice form).
    """
    return _DEFAULT_INTRINSICS.get(role, IntrinsicFeatures())


# === Lex-entry bridges =====================================================


# Non-LMT GFs that lex entries may stipulate directly (XCOMP for
# control / causative complements, COMP for closed clausal
# complements). These bypass the LMT [±r, ±o] truth table and are
# passed through to :func:`tgllfg.lmt.compute_mapping` via
# ``stipulated_gfs``.
_STIPULATED_GFS: frozenset[str] = frozenset({"XCOMP", "COMP"})


def intrinsics_for(
    lex_entry: LexicalEntry,
) -> list[IntrinsicClassification]:
    """Build a list of :class:`IntrinsicClassification` ordered by
    ``lex_entry.a_structure``.

    Each role's intrinsics come from
    ``lex_entry.intrinsic_classification`` if present; otherwise from
    :func:`default_intrinsics`. Roles whose name is not a member of
    :class:`Role` raise :class:`ValueError` (signals a typo in the
    lex entry).

    Both tuple ``(r, o)`` and list ``[r, o]`` value shapes are
    accepted so JSONB-loaded entries (where JSON has no tuple type)
    work without conversion.
    """
    out: list[IntrinsicClassification] = []
    for role_name in lex_entry.a_structure:
        try:
            role = Role[role_name]
        except KeyError as exc:
            raise ValueError(
                f"unknown role {role_name!r} in lex_entry "
                f"a_structure for {lex_entry.lemma!r}"
            ) from exc
        ic_value = lex_entry.intrinsic_classification.get(role_name)
        if ic_value is None:
            features = default_intrinsics(role)
        else:
            r, o = ic_value
            features = IntrinsicFeatures(r=r, o=o)
        out.append(IntrinsicClassification(role=role, intrinsics=features))
    return out


def stipulated_gfs_for(lex_entry: LexicalEntry) -> dict[Role, str]:
    """Extract the roles whose GF is stipulated by the lex entry's
    ``gf_defaults`` (XCOMP, COMP — the off-truth-table GFs).

    These roles bypass the LMT engine's role-to-GF truth table; the
    pipeline calls :func:`tgllfg.lmt.compute_mapping` with the result
    of this function as ``stipulated_gfs`` so the engine still
    accounts for them in the Subject Condition and biuniqueness
    checks. Roles with names not in :class:`Role` are skipped silently
    so legacy lex entries with unknown roles don't crash; the
    :func:`intrinsics_for` companion would catch the same case
    loudly when the engine actually consumes the entry.
    """
    out: dict[Role, str] = {}
    for role_name, gf in lex_entry.gf_defaults.items():
        if gf not in _STIPULATED_GFS:
            continue
        try:
            role = Role[role_name]
        except KeyError:
            continue
        out[role] = gf
    return out
