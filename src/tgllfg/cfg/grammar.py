# tgllfg/cfg/grammar.py

from dataclasses import dataclass
from typing import Sequence

@dataclass
class Rule:
    lhs: str
    rhs: list[str]          # nonterminals/terminals with feature labels like NP[CASE=NOM]
    equations: list[str]    # LFG equations using ↑ and ↓i (i = child index, 1-based)

class Grammar:
    def __init__(self, rules: Sequence[Rule]): self.rules = list(rules)

    @staticmethod
    def load_default() -> "Grammar":
        R = []

        # Terminals (POS) as preterminals
        # NP shells
        R.append(Rule("NP[CASE=NOM]", ["DET[CASE=NOM]","N"], ["(↑ CASE)= 'NOM'", "(↑ PRED) = ↓2 PRED"]))
        R.append(Rule("NP[CASE=GEN]", ["ADP[CASE=GEN]","N"], ["(↑ CASE)= 'GEN'", "(↑ PRED) = ↓2 PRED"]))
        R.append(Rule("NP[CASE=DAT]", ["ADP[CASE=DAT]","N"], ["(↑ CASE)= 'DAT'", "(↑ PRED) = ↓2 PRED"]))

        # Lexical projections
        R.append(Rule("N", ["NOUN"], ["(↑ PRED) = '"+"NOUN"+"(↑ FORM)'" ]))  # toy; PRED from lexicon in Phase 3

        # VP and S (V-initial). Voice naming follows Kroeger 1993:
        # AV / OV / DV / IV. The legacy "PV" (Patient Voice) label
        # is identified with OV.
        R.append(Rule(
            "S",
            ["VP_OV"],
            ["(↑)=↓1"]
        ))

        # OV transitive: V NP(GEN ng-non-pivot) NP(NOM ang-pivot)
        R.append(Rule(
            "VP_OV",
            ["V[VOICE=OV]", "NP[CASE=GEN]", "NP[CASE=NOM]"],
            [
                "(↑ PRED) = ↓1 PRED",
                "(↑ VOICE) = ↓1 VOICE",
                "(↑ ASPECT) = ↓1 ASPECT",
                "(↑ MOOD) = ↓1 MOOD",
                "(↑ LEX-ASTRUCT) = ↓1 LEX-ASTRUCT",
                "(↑ SUBJ) = ↓3",           # NOM → SUBJ (patient pivot)
                "(↑ OBJ) = ↓2",            # ng-non-pivot as OBJ (Kroeger 1993)
            ],
        ))

        # Actor Voice intransitive: V NP(NOM actor)
        R.append(Rule(
            "S_AV",
            ["V[VOICE=AV]", "NP[CASE=NOM]"],
            [
                "(↑ PRED) = ↓1 PRED",
                "(↑ VOICE) = ↓1 VOICE",    # voice feature from verb
                "(↑ ASPECT) = ↓1 ASPECT",  # aspect feature from verb
                "(↑ MOOD) = ↓1 MOOD",      # aspect feature from verb
                "(↑ SUBJ) = ↓2",
            ],
        ))

        return Grammar(R)
