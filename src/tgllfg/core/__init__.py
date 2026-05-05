# tgllfg/core/__init__.py

"""Core data types, in-process lexicon, and parse pipeline.

Re-exports the foundational records and entry points that callers
inside and outside the package import as the public surface of the
core layer. Implementations live in sibling modules — keep this file
exports-only.
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
from .pipeline import (
    Fragment,
    ParseResult,
    parse_text,
    parse_text_with_fragments,
)

__all__ = [
    "AStructure",
    "BASE",
    "CNode",
    "FStructure",
    "FeatureValue",
    "Fragment",
    "LexicalEntry",
    "MorphAnalysis",
    "ParseResult",
    "Token",
    "lookup_lexicon",
    "parse_text",
    "parse_text_with_fragments",
]
