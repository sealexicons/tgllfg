# tgllfg/grammar.py

from dataclasses import dataclass
from typing import Sequence
from . import CNode

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
        R.append(Rule("N", ["NOUN"], ["(↑ PRED) = '"+"NOUN"+"(↑ FORM)'" ]))  # toy; you’ll set PRED from lexicon

        # VP and S (V-initial)
        # Patient Voice transitive: V NP(GEN agent) NP(NOM patient)
        R.append(Rule(
            "S",
            ["VP_PV"],
            ["(↑)=↓1"]
        ))

        R.append(Rule(
            "VP_PV",
            ["V[VOICE=PV]", "NP[CASE=GEN]", "NP[CASE=NOM]"],
            [
                "(↑ PRED) = ↓1 PRED",
                "(↑ VOICE) = ↓1 VOICE",    # voice feature from verb
                "(↑ SUBJ) = ↓3",           # NOM → SUBJ (patient pivot)
                "(↑ OBL-AG) = ↓2",         # genitive agent as oblique/by-phrase
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
