# tgllfg/cfg/grammar.py

"""Default Tagalog grammar.

The grammar is V-initial. Sentences are flat ``S → V (NP)*`` rules
that distinguish:

* the verb's voice (``AV`` / ``OV`` / ``DV`` / ``IV``);
* the case of each post-verbal NP (``NOM`` / ``GEN`` / ``DAT``);
* the relative order of the post-verbal NPs (Tagalog freely permits
  ``ang``-NP and ``ng``-NP in either order).

The grammar's case→GF mapping is uniform across all four voices —
``ang``-NP (``NOM``) is SUBJ; ``ng``-NP (``GEN``) is OBJ; ``sa``-NP
(``DAT``) attaches as a member of the f-structure's ``ADJUNCT`` set.
The OBJ analysis of the *ng*-non-pivot in transitive non-AV is
established in Phase 1; Phase 4 generalises it to DV and IV
(``docs/analysis-choices.md`` "ng-non-pivot in transitive non-AV →
OBJ" + "Phase 4 §7.1: voice and case extensions").

``OBL-LOC`` / ``OBL-GOAL`` / ``OBL-BEN`` classification of *sa*-NPs
is deferred to Phase 5 (LMT-driven mapping); for now they ride
through the f-structure as a non-governable ``ADJUNCT`` set, which
sidesteps coherence by design.

The argument-structure secondary features ``APPL ∈ {INSTR, BEN,
REASON, CONVEY, ∅}`` and ``CAUS ∈ {DIRECT, INDIRECT, ∅}`` are
recognised by the grammar (lex_entry templates may carry them), but
no Phase 4 grammar rule consumes them yet — applicatives and
causatives proper land in §7.7.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass
class Rule:
    lhs: str
    rhs: list[str]          # nonterminals/terminals with feature labels like NP[CASE=NOM]
    equations: list[str]    # LFG equations using ↑ and ↓i (i = child index, 1-based)


# Equations every clausal rule emits to percolate verb features up
# to the matrix f-structure. ``↓1`` is always the verb in our
# V-initial rules.
_VERB_PERCOLATION: tuple[str, ...] = (
    "(↑ PRED) = ↓1 PRED",
    "(↑ VOICE) = ↓1 VOICE",
    "(↑ ASPECT) = ↓1 ASPECT",
    "(↑ MOOD) = ↓1 MOOD",
    "(↑ LEX-ASTRUCT) = ↓1 LEX-ASTRUCT",
)


def _eqs(*extras: str) -> list[str]:
    """Build an equation list: verb percolation followed by extras."""
    return [*_VERB_PERCOLATION, *extras]


class Grammar:
    def __init__(self, rules: Sequence[Rule]) -> None:
        self.rules: list[Rule] = list(rules)

    @staticmethod
    def load_default() -> "Grammar":
        rules: list[Rule] = []

        # --- NP shells (case from determiner / personal-name marker) ---
        rules.append(Rule(
            "NP[CASE=NOM]",
            ["DET[CASE=NOM]", "N"],
            ["(↑ CASE) = 'NOM'", "(↑ PRED) = ↓2 PRED"],
        ))
        rules.append(Rule(
            "NP[CASE=GEN]",
            ["ADP[CASE=GEN]", "N"],
            ["(↑ CASE) = 'GEN'", "(↑ PRED) = ↓2 PRED"],
        ))
        rules.append(Rule(
            "NP[CASE=DAT]",
            ["ADP[CASE=DAT]", "N"],
            ["(↑ CASE) = 'DAT'", "(↑ PRED) = ↓2 PRED"],
        ))

        # Pronominal NPs: case carried on PRON itself.
        rules.append(Rule(
            "NP[CASE=NOM]",
            ["PRON[CASE=NOM]"],
            ["(↑) = ↓1"],
        ))
        rules.append(Rule(
            "NP[CASE=GEN]",
            ["PRON[CASE=GEN]"],
            ["(↑) = ↓1"],
        ))
        rules.append(Rule(
            "NP[CASE=DAT]",
            ["PRON[CASE=DAT]"],
            ["(↑) = ↓1"],
        ))

        # --- N from NOUN (toy PRED; Phase 5 will lexicalise properly) ---
        rules.append(Rule(
            "N",
            ["NOUN"],
            ["(↑ PRED) = 'NOUN(↑ FORM)'"],
        ))

        # --- Sentential rules: V-initial, flat ---
        #
        # SUBJ ← NP[CASE=NOM]; OBJ ← NP[CASE=GEN]. ADJUNCT ∋ NP[CASE=DAT].
        # Both post-verbal NP orders are admitted (Tagalog free order).

        # AV intransitive (no OBJ).
        rules.append(Rule(
            "S",
            ["V[VOICE=AV]", "NP[CASE=NOM]"],
            _eqs("(↑ SUBJ) = ↓2"),
        ))
        rules.append(Rule(
            "S",
            ["V[VOICE=AV]", "NP[CASE=NOM]", "NP[CASE=DAT]"],
            _eqs("(↑ SUBJ) = ↓2", "↓3 ∈ (↑ ADJUNCT)"),
        ))

        # Transitive frames per voice, two NP orderings each, with and
        # without a trailing sa-oblique (ADJUNCT).
        for voice in ("AV", "OV", "DV", "IV"):
            v_cat = f"V[VOICE={voice}]"
            # NOM-GEN order
            rules.append(Rule(
                "S",
                [v_cat, "NP[CASE=NOM]", "NP[CASE=GEN]"],
                _eqs("(↑ SUBJ) = ↓2", "(↑ OBJ) = ↓3"),
            ))
            # GEN-NOM order
            rules.append(Rule(
                "S",
                [v_cat, "NP[CASE=GEN]", "NP[CASE=NOM]"],
                _eqs("(↑ SUBJ) = ↓3", "(↑ OBJ) = ↓2"),
            ))
            # NOM-GEN-DAT
            rules.append(Rule(
                "S",
                [v_cat, "NP[CASE=NOM]", "NP[CASE=GEN]", "NP[CASE=DAT]"],
                _eqs("(↑ SUBJ) = ↓2", "(↑ OBJ) = ↓3", "↓4 ∈ (↑ ADJUNCT)"),
            ))
            # GEN-NOM-DAT
            rules.append(Rule(
                "S",
                [v_cat, "NP[CASE=GEN]", "NP[CASE=NOM]", "NP[CASE=DAT]"],
                _eqs("(↑ SUBJ) = ↓3", "(↑ OBJ) = ↓2", "↓4 ∈ (↑ ADJUNCT)"),
            ))

        return Grammar(rules)
