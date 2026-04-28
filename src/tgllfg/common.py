# tgllfg/common.py

"""Foundational data types shared across the tgllfg pipeline.

These are the value-bearing records passed between stages
(tokenizer, morphology, lexicon, parser, unifier, LMT, renderers).
The package's `__init__.py` re-exports them as the public surface;
new code should import from here directly when working inside the
package, and from `tgllfg` when consuming it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Feature values are deliberately broad: atoms (str/int/bool), nested
# f-structures, sets, and reentrancy markers all live here. Tightening
# this type is a §4.2 follow-up once the graph projection settles.
type FeatureValue = Any


@dataclass(frozen=True)
class Token:
    surface: str
    norm: str
    start: int
    end: int


@dataclass
class MorphAnalysis:
    lemma: str
    pos: str
    # e.g., {"VOICE": "PV", "ASPECT": "PFV", "TR": "TR", "CASE": "NOM"}
    feats: dict[str, FeatureValue]


@dataclass
class LexicalEntry:
    lemma: str
    pred: str                                       # 'EAT <SUBJ, OBJ>' (LFG-style)
    a_structure: list[str]                          # ["AGENT", "PATIENT"]
    morph_constraints: dict[str, FeatureValue]      # VOICE=PV, TR=TR, ...
    gf_defaults: dict[str, str]                     # bare-form fallbacks


@dataclass
class CNode:
    label: str
    children: list["CNode"] = field(default_factory=list)
    # LFG functional annotations as equation strings; parsed lazily by
    # the unifier via tgllfg.equations.parse_equation.
    equations: list[str] = field(default_factory=list)


@dataclass
class FStructure:
    # AVM with reentrancy via ids; keys are LFG feature names.
    feats: dict[str, FeatureValue] = field(default_factory=dict)
    id: int = 0


@dataclass
class AStructure:
    pred: str                       # normalised PRED, e.g., 'EAT'
    roles: list[str]                # theta roles in order
    mapping: dict[str, str]         # role → GF after LMT
