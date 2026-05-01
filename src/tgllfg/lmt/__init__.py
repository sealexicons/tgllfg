# tgllfg/lmt/__init__.py

"""Phase 5 §8 Lexical Mapping Theory.

A Bresnan–Kanerva ``[±r, ±o]`` engine that replaces the Phase 4
voice-aware heuristic. The package layers, in dependency order:

* :mod:`.common` — data types (:class:`Role`,
  :class:`IntrinsicFeatures`, :class:`IntrinsicClassification`,
  :class:`MappingResult`), the role-hierarchy intrinsic table, and
  bridges from :class:`tgllfg.common.LexicalEntry`
  (:func:`intrinsics_for`, :func:`stipulated_gfs_for`).
* :mod:`.principles` — the seven BK 1989 principles as named
  pure functions, plus the orchestrator :func:`compute_mapping`.
* :mod:`.oblique_classifier` — the post-solve mutation that
  reclassifies ``ADJUNCT`` members with ``CASE=DAT`` into typed
  ``OBL-θ`` slots based on the mapping the engine produces.
* :mod:`.check` — the pipeline-facing :func:`lmt_check` /
  :func:`apply_lmt_with_check` that locate the matrix lex entry,
  run the engine + classifier, and surface diagnostics.

The Phase 4 heuristic remains available via :func:`apply_lmt`
(re-exported from :mod:`.legacy`) as a defensive fallback for
:func:`apply_lmt_with_check` when :func:`find_matrix_lex_entry`
can't locate a lex entry (e.g., synthetic test fixtures with
empty ``lex_items``).
"""

from .check import (
    apply_lmt_with_check,
    find_matrix_lex_entry,
    lmt_check,
)
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
from .oblique_classifier import classify_oblique_slots
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
    # Data types
    "IntrinsicClassification",
    "IntrinsicFeatures",
    "MappingResult",
    "Role",
    "obj_theta",
    "obl_theta",
    # Principles
    "ROLE_HIERARCHY",
    "apply_voice_constraints",
    "check_biuniqueness",
    "check_subject_condition",
    "compute_mapping",
    "default_intrinsics",
    "fill_defaults",
    "non_subject_mapping",
    "subject_mapping",
    # Lex-entry bridges
    "intrinsics_for",
    "stipulated_gfs_for",
    # Pipeline-facing check
    "apply_lmt_with_check",
    "find_matrix_lex_entry",
    "lmt_check",
    # Oblique classifier
    "classify_oblique_slots",
    # Legacy heuristic (defensive fallback for no-lex-entry cases)
    "apply_lmt",
]
