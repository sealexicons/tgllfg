# tgllfg/earley.py

# You can plug any chart parser; important bit is carrying node-local equations.
from . import CNode, MorphAnalysis, LexicalEntry

def parse_with_annotations(
    sentence_lex: list[list[tuple[MorphAnalysis, LexicalEntry|None]]], grammar
):
    """
    Return a packed forest object. Prototype: just build a single best tree if the
    toy sentence matches a hard-wired pattern.
    """
    # For outline purposes, pretend we matched: "Kinain ng aso ang isda ."
    # Build a CNode with equations copied from the matching rules.
    # In practice, implement an Earley parser that attaches equations per rule expansion.
    return PackedForest([
        build_demo_tree(sentence_lex, grammar)
    ])

class PackedForest:
    def __init__(self, trees: list[CNode]): self.trees = trees
    def best_k(self, k:int): return self.trees[:k]

def build_demo_tree(sentence_lex, grammar) -> CNode:
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
    ])

    np_gen = CNode("NP[CASE=GEN]", [], equations=["(↑ CASE)='GEN'"])
    np_nom = CNode("NP[CASE=NOM]", [], equations=["(↑ CASE)='NOM'"])

    vp = CNode("VP_PV", [vnode, np_gen, np_nom], equations=[
        "(↑ PRED) = ↓1 PRED",
        "(↑ SUBJ) = ↓3",
        "(↑ OBL-AG) = ↓2",
    ])
    return CNode("S", [vp], equations=["(↑)=↓1"])
