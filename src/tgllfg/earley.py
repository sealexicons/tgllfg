# tgllfg/earley.py

# Plug in any chart parser; important bit is carrying node-local equations.
from . import CNode, MorphAnalysis, LexicalEntry
from .grammar import Grammar

class PackedForest:
    def __init__(self, trees: list[CNode]): self.trees = trees
    def best_k(self, k:int): return self.trees[:k]

def build_demo_tree(
    sentence_lex: list[list[tuple[MorphAnalysis, LexicalEntry|None]]],
    _grammar: Grammar,
) -> CNode:
    v_le = None

    for cand in sentence_lex:
        for ma, le in cand:
            if ma.pos == "VERB" and le is not None:
                v_le = le
                break
        if v_le is not None:
            break

    if v_le is None:
        # Helpful failure instead of AttributeError
        raise ValueError("No verbal lexical entry found in sentence_lex (check morphology/lexicon).")

    vnode = CNode("V", [], equations=[
        f"(↑ PRED) = '{v_le.pred}'",
        "(↑ VOICE) = 'PV'",
        "(↑ ASPECT) = 'PFV'",
        "(↑ MOOD) = 'IND'",
        f"(↑ LEX-ASTRUCT) = '{','.join(v_le.a_structure)}'",  # e.g., "AGENT,PATIENT"
    ])

    np_gen = CNode("NP[CASE=GEN]", [], equations=["(↑ CASE)='GEN'"])
    np_nom = CNode("NP[CASE=NOM]", [], equations=["(↑ CASE)='NOM'"])

    vp = CNode("VP_PV", [vnode, np_gen, np_nom], equations=[
        "(↑ PRED) = ↓1 PRED",
        "(↑ VOICE) = ↓1 VOICE",
        "(↑ ASPECT)= ↓1 ASPECT",
        "(↑ MOOD)  = ↓1 MOOD",
        "(↑ LEX-ASTRUCT)  = ↓1 LEX-ASTRUCT",
        "(↑ SUBJ) = ↓3",
        "(↑ OBL-AG) = ↓2",
    ])

    return CNode("S", [vp], equations=["(↑)=↓1"])

def parse_with_annotations(
    sentence_lex: list[list[tuple[MorphAnalysis, LexicalEntry|None]]],
    grammar: Grammar,
) -> PackedForest:
    """
    Return a packed forest object. Prototype: just build a single best tree if the
    toy sentence matches a hard-wired pattern.
    """
    # For outline purposes, pretend we matched: "Kinain ng aso ang isda ."
    # Build a CNode with equations copied from the matching rules.
    # In practice, implement an Earley parser that attaches equations per rule expansion.
    return PackedForest([build_demo_tree(sentence_lex, grammar)])
