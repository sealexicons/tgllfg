# tgllfg/pipeline.py

from .tokenizer import tokenize
from .clitics import split_enclitics
from .morph import analyze_tokens
from .lexicon import lookup_lexicon
from .grammar import Grammar
from .earley import parse_with_annotations
from .unify import build_f_structure
from .lmt import apply_lmt
from .fs_checks import lfg_well_formed

def parse_text(text: str):
    # 1) tokenize & clitic handling
    toks = tokenize(text)
    toks = split_enclitics(toks)

    # 2) morphology (Tagalog voice/aspect; particles ang/ng/sa; proper nouns; pronouns)
    mlist = analyze_tokens(toks)  # list[list[MorphAnalysis]] (n-best analyses)

    # 3) lexical lookup adds PRED & a-structure candidates
    lex_items = lookup_lexicon(mlist)

    # 4) c-structure parse with functional annotations carried on rules
    grammar = Grammar.load_default()
    packed_forest = parse_with_annotations(lex_items, grammar)

    # 5) for each tree: build f-structure via equation collection + unification
    results = []
    for ctree in packed_forest.best_k(5):
        f = build_f_structure(ctree)
        a = apply_lmt(f)  # produce an AStructure from lexical info + VOICE
        ok, diagnostics = lfg_well_formed(f, ctree)
        if ok:
            results.append((ctree, f, a, diagnostics))
    return results
