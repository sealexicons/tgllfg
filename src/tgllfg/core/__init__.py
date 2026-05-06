# tgllfg/core/__init__.py

"""Core data types and in-process lexicon.

Re-exports the foundational records (data shapes shared across the
pipeline) and the in-process verb lexicon. The end-to-end parse
pipeline (:mod:`tgllfg.core.pipeline`) is intentionally NOT
re-exported here — pipeline imports :mod:`tgllfg.morph`, and
:mod:`tgllfg.morph.analyzer` imports back into
:mod:`tgllfg.core.common`, so re-exporting pipeline at the package
level creates a circular import on the morph-first import path
(``from tgllfg.morph import Analyzer``). Callers that need the
pipeline use the explicit path ``from tgllfg.core.pipeline import
parse_text``.
"""

from .common import (
    AStructure,
    CNode,
    FStructure,
    FeatureValue,
    LexicalEntry,
    MorphAnalysis,
    Token,
)
from .lexicon import BASE, lookup_lexicon

__all__ = [
    "AStructure",
    "BASE",
    "CNode",
    "FStructure",
    "FeatureValue",
    "LexicalEntry",
    "MorphAnalysis",
    "Token",
    "lookup_lexicon",
]
