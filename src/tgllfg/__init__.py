# tgllfg/__init__.py

# SPDX-FileCopyrightText: 2025-present Glenn Adams <glenn@skynav.com>
# SPDX-License-Identifier: MIT

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

FeatureValue = Any  # atom | str | int | bool | list | dict | Reentrancy

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
    feats: dict[str, FeatureValue]  # e.g., {"VOICE":"PV","ASPECT":"PFV","TR":"TR","CASE":"NOM"}

@dataclass
class LexicalEntry:
    lemma: str
    pred: str                   # 'EAT <SUBJ, OBJ>'  (LFG-style)
    a_structure: list[str]      # ["AGENT", "PATIENT"] or ["ACTOR"] etc.
    morph_constraints: dict[str, FeatureValue]  # VOICE=PV, TR=TR, etc.
    gf_defaults: dict[str, str] # for bare forms if particles absent

@dataclass
class CNode:
    label: str
    children: list["CNode"] = field(default_factory=list)
    # LFG functional annotations as equations collected on this node:
    equations: list[str] = field(default_factory=list)  # e.g., ["(↑ PRED) = 'EAT <SUBJ,OBJ>'", "(↑ SUBJ) = ↓1"]

@dataclass
class FStructure:
    # AVM with reentrancy via ids; keys are LFG feature names
    feats: dict[str, FeatureValue] = field(default_factory=dict)
    id: int = 0

@dataclass
class AStructure:
    pred: str                   # normalised PRED, e.g., 'EAT'
    roles: list[str]            # theta roles in order, e.g., ["AGENT", "PATIENT"]
    mapping: dict[str, str]     # role→GF after LMT, e.g., {"PATIENT":"SUBJ","AGENT":"OBL-AG"}
