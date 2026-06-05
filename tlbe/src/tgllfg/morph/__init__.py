# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

# tgllfg/morph/__init__.py

from .analyzer import Analyzer, analyze_tokens, generate_form
from .loader import load_morph_data
from .paradigms import (
    AdjectiveCell,
    MorphData,
    Operation,
    ParadigmCell,
    Particle,
    Pronoun,
    Root,
    SandhiRule,
    VerbalCell,
)

__all__ = [
    "AdjectiveCell",
    "Analyzer",
    "MorphData",
    "Operation",
    "ParadigmCell",
    "Particle",
    "Pronoun",
    "Root",
    "SandhiRule",
    "VerbalCell",
    "analyze_tokens",
    "generate_form",
    "load_morph_data",
]
