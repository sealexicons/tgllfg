# tgllfg/morph.py

from __future__ import annotations

import re
from typing import List

from . import Token, MorphAnalysis

"""
Minimal Tagalog morphology stub for the demo pipeline.

- Recognizes particles: ang/si/ng/ni/sa, and 'hindi'
- Handles basic verb forms in the kain-family:
    kinain  -> PV PFV TR
    kainin  -> PV IMPF TR
    kumain  -> AV PFV INTR
- Falls back to a tiny noun list; otherwise tags as X
"""

# --- Particles / function words ---
PARTICLES: dict[str, tuple[str, dict[str, object]]] = {
    "ang": ("DET", {"CASE": "NOM", "MARKER": "ANG"}),
    "si":  ("DET", {"CASE": "NOM", "MARKER": "SI", "HUMAN": True}),
    "ng":  ("ADP", {"CASE": "GEN", "MARKER": "NG"}),
    "ni":  ("ADP", {"CASE": "GEN", "MARKER": "NI", "HUMAN": True}),
    "sa":  ("ADP", {"CASE": "DAT", "MARKER": "SA"}),
    "hindi": ("PART", {"POLARITY": "NEG"}),
}

# --- Tiny demo noun list (extend as needed) ---
NOUNS: set[str] = {"aso", "isda", "bata", "maria", "juan"}

# --- Verb patterns for the 'kain' family used in the demo ---
V_KAIN_PATTERNS: list[tuple[re.Pattern[str], dict[str, object]]] = [
    (re.compile(r"^kinain$", re.IGNORECASE), {"VOICE": "PV", "ASPECT": "PFV", "TR": "TR"}),
    (re.compile(r"^kainin$", re.IGNORECASE), {"VOICE": "PV", "ASPECT": "IMPF", "TR": "TR"}),
    (re.compile(r"^kumain$", re.IGNORECASE), {"VOICE": "AV", "ASPECT": "PFV", "TR": "INTR"}),
]


def analyze_tokens(tokens: List[Token]) -> List[List[MorphAnalysis]]:
    """
    Return n-best analyses per token (here: just 1-best per token for simplicity).

    Each item in the outer list corresponds to a surface token and contains a list
    of possible MorphAnalysis candidates for that token.
    """
    analyses: List[List[MorphAnalysis]] = []

    for t in tokens:
        n = t.norm.lower()

        # Particles / function words
        if n in PARTICLES:
            pos, feats = PARTICLES[n]
            analyses.append([MorphAnalysis(lemma=n, pos=pos, feats=dict(feats))])
            continue

        # Verb patterns (demo: 'kain' family)
        matched = False
        for pat, feats in V_KAIN_PATTERNS:
            if pat.match(n):
                analyses.append([MorphAnalysis(lemma="kain", pos="VERB", feats=dict(feats))])
                matched = True
                break
        if matched:
            continue

        # Simple nouns
        if n in NOUNS:
            analyses.append([MorphAnalysis(lemma=n, pos="NOUN", feats={})])
            continue

        # Fallback unknown
        analyses.append([MorphAnalysis(lemma=n, pos="X", feats={})])

    return analyses
