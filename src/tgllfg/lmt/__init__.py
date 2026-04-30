# tgllfg/lmt/__init__.py

"""Phase 5 §8 Lexical Mapping Theory.

Replaces the Phase 4 voice-aware heuristic with a Bresnan–Kanerva
``[±r, ±o]`` engine. Commit 1 lays down the data types
(:mod:`.common`); Commit 2 adds the principles
(:mod:`.principles`); Commits 3–8 add per-voice tests, lexicon
integration, pipeline wiring, sa-NP reclassification,
well-formedness promotion, and documentation. The Phase 4 heuristic
remains available via :func:`apply_lmt` (re-exported from
:mod:`.legacy`) through Commit 5; Commit 8 deletes it.
"""

from .common import (
    IntrinsicClassification,
    IntrinsicFeatures,
    MappingResult,
    Role,
    default_intrinsics,
    intrinsics_for,
    obj_theta,
    obl_theta,
    stipulated_gfs_for,
)
from .legacy import apply_lmt
from .principles import (
    ROLE_HIERARCHY,
    apply_voice_constraints,
    check_biuniqueness,
    check_subject_condition,
    compute_mapping,
    fill_defaults,
    non_subject_mapping,
    subject_mapping,
)

__all__ = [
    # Data types (Commit 1)
    "IntrinsicClassification",
    "IntrinsicFeatures",
    "MappingResult",
    "Role",
    "obj_theta",
    "obl_theta",
    # Principles (Commit 2)
    "ROLE_HIERARCHY",
    "apply_voice_constraints",
    "check_biuniqueness",
    "check_subject_condition",
    "compute_mapping",
    "default_intrinsics",
    "fill_defaults",
    "non_subject_mapping",
    "subject_mapping",
    # Lex-entry bridges (Commit 4)
    "intrinsics_for",
    "stipulated_gfs_for",
    # Legacy (deleted in Commit 8)
    "apply_lmt",
]
