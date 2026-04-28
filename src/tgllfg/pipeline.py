# tgllfg/pipeline.py

"""End-to-end parse pipeline: text → c-/f-/a-structure with diagnostics.

The function returns one tuple per parse that survives well-formedness
filtering. Each tuple carries the full diagnostic list — both the
unifier's diagnostics from :func:`tgllfg.fstruct.solve` and the
well-formedness diagnostics from :func:`tgllfg.fstruct.lfg_well_formed`.
A parse is suppressed when any *blocking* diagnostic was produced;
informational diagnostics (``deferred``, ``unsupported``) pass
through and accompany the surviving parse.
"""

from __future__ import annotations

from .cfg import Grammar
from .common import AStructure, CNode, FStructure
from .fstruct import Diagnostic, lfg_well_formed, solve
from .lexicon import lookup_lexicon
from .lmt import apply_lmt
from .morph import analyze_tokens
from .parse import parse_with_annotations
from .text import split_enclitics, tokenize


def parse_text(
    text: str,
    *,
    n_best: int = 5,
) -> list[tuple[CNode, FStructure, AStructure, list[Diagnostic]]]:
    """Parse a sentence end to end.

    Returns one ``(c-tree, f-structure, a-structure, diagnostics)`` per
    parse that survives well-formedness filtering. The diagnostic list
    contains every diagnostic produced for the surviving parse,
    including informational ones; a parse is dropped only when at
    least one diagnostic is *blocking* (see
    :attr:`tgllfg.fgraph.Diagnostic.is_blocking`).
    """
    toks = tokenize(text)
    toks = split_enclitics(toks)
    mlist = analyze_tokens(toks)
    lex_items = lookup_lexicon(mlist)
    grammar = Grammar.load_default()
    forest = parse_with_annotations(lex_items, grammar)

    results: list[tuple[CNode, FStructure, AStructure, list[Diagnostic]]] = []
    for ctree in forest.best_k(n_best):
        result = solve(ctree)
        a = apply_lmt(result.fstructure)
        _, wf_diags = lfg_well_formed(result.fstructure, ctree)
        diagnostics = list(result.diagnostics) + wf_diags
        if any(d.is_blocking() for d in diagnostics):
            continue
        results.append((ctree, result.fstructure, a, diagnostics))
    return results
