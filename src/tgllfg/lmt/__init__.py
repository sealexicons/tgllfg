# tgllfg/lmt/__init__.py

"""Phase 5 §8 Lexical Mapping Theory.

Replaces the Phase 4 voice-aware heuristic with a Bresnan–Kanerva
``[±r, ±o]`` engine. Commit 1 lays down the data types
(:mod:`.common`); commits 2–8 add the principles, lexicon
integration, pipeline wiring, sa-NP reclassification, well-formedness
promotion, and documentation. The Phase 4 heuristic remains
available via :func:`apply_lmt` (re-exported from :mod:`.legacy`)
through commit 5; commit 8 deletes it.
"""

from .common import (
    IntrinsicClassification,
    IntrinsicFeatures,
    MappingResult,
    Role,
    obj_theta,
    obl_theta,
)
from .legacy import apply_lmt

__all__ = [
    "IntrinsicClassification",
    "IntrinsicFeatures",
    "MappingResult",
    "Role",
    "apply_lmt",
    "obj_theta",
    "obl_theta",
]
