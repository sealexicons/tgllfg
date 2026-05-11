# tgllfg/pipeline.py

"""End-to-end parse pipeline: text → c-/f-/a-structure with diagnostics.

:func:`parse_text` returns one tuple per parse that survives
well-formedness filtering. Each tuple carries the full diagnostic
list — both the unifier's diagnostics from :func:`tgllfg.fstruct.solve`
and the well-formedness diagnostics from
:func:`tgllfg.fstruct.lfg_well_formed`. A parse is suppressed when any
*blocking* diagnostic was produced; informational diagnostics
(``deferred``, ``unsupported``) pass through and accompany the
surviving parse.

Phase 4 §7.9 robustness:

* :func:`parse_text_with_fragments` returns a :class:`ParseResult`
  with both complete parses and partial fragments. When no complete
  parse exists, the parser walks the Earley chart for the largest
  non-root completed states and returns them as fragments — each
  with its partial f-structure and the diagnostics that prevented
  promotion.
* Heuristic ranking of complete parses: shorter c-trees first,
  AV-voice preferred over non-AV when no morphology disambiguates,
  more-specific lex entries (more morph_constraints keys) preferred
  over the generic synthesized fallback.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from ..cfg import Grammar
from ..clitics import reorder_clitics
from .common import AStructure, CNode, FStructure
from ..fstruct import Diagnostic, lfg_well_formed, solve
from .lexicon import lookup_lexicon
from ..lmt import apply_lmt_with_check
from ..morph import analyze_tokens
from ..parse import parse_with_annotations
from ..text import (
    merge_hyphen_compounds,
    split_apostrophe_t,
    split_enclitics,
    split_linker_ng,
    tokenize,
)


@dataclass(frozen=True)
class Fragment:
    """A partial parse covering a sub-span of the input. Phase 4
    §7.9 fragments are the largest non-root completed states from
    the Earley chart — the parser's best guess at what *did* parse
    when no complete sentence parse was found."""
    span: tuple[int, int]
    ctree: CNode
    fstructure: FStructure
    astructure: AStructure
    diagnostics: list[Diagnostic]


@dataclass(frozen=True)
class ParseResult:
    """The full output of :func:`parse_text_with_fragments`. At
    most one of ``parses`` and ``fragments`` is non-empty: complete
    parses suppress fragment output (the user wanted a parse, they
    got one); fragments only surface when no complete parse exists."""
    parses: list[tuple[CNode, FStructure, AStructure, list[Diagnostic]]]
    fragments: list[Fragment]


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

    Phase 4 §7.9: results are ranked by a heuristic key
    (:func:`_rank_key`) before truncating to ``n_best``. The ranker
    prefers shorter c-trees, AV-voice readings, and more-specific
    lex entries.
    """
    return parse_text_with_fragments(text, n_best=n_best).parses


def parse_text_with_fragments(
    text: str,
    *,
    n_best: int = 5,
    fragment_cap: int = 5,
) -> ParseResult:
    """Parse text, returning either complete parses (Phase 4 §7.9
    "happy path") or fragments (the failure-recovery mode).

    When at least one complete parse survives well-formedness
    filtering, ``parses`` contains up to ``n_best`` complete parses
    ranked by :func:`_rank_key`, and ``fragments`` is empty. When no
    complete parse exists, ``parses`` is empty and ``fragments``
    contains up to ``fragment_cap`` partial parses — the largest
    non-root completed states from the Earley chart, each with its
    partial f-structure and the diagnostics that prevented promotion.
    """
    toks = tokenize(text)
    # Phase 5k Commit 2: merge the post-vowel bound clitic ``'t`` (=
    # contracted ``at`` "and") into a synthetic ``at`` token so it
    # routes to the Phase 5k Commit 1 PART[COORD=AND] lex entry.
    # ``Maria't Juan`` → ``Maria`` / ``at`` / ``Juan``. Runs first
    # so all downstream pre-passes see the canonical ``at``
    # surface; ``at`` doesn't end in vowel + ``-ng`` so there is
    # no interaction with :func:`split_linker_ng`.
    toks = split_apostrophe_t(toks)
    # Phase 4 §7.5: detach the bound linker ``-ng`` from vowel-final
    # hosts (``batang`` → ``bata`` + ``-ng``) so the relativization
    # rules see a uniform ``PART[LINK=NA|NG]`` between the head NP
    # and the relative clause. Runs before
    # :func:`merge_hyphen_compounds` so a hyphenated compound with a
    # bound linker on the right half (``kani-kaniyang``) reaches the
    # merge as ``kani`` / ``-`` / ``kaniya`` / ``-ng`` and the
    # canonical join (``kani`` + ``kaniya`` = ``kanikaniya``) finds
    # a hit in the analyzer index.
    toks = split_linker_ng(toks)
    # Phase 5f closing deferral: collapse canonical hyphenated
    # compounds (``tag-init`` → ``taginit``, ``daan-daan`` →
    # ``daandaan``, etc.) into single tokens that match the
    # seed-lex single-token entries. Runs before
    # :func:`split_enclitics` so the merged compound is the unit
    # passed to all downstream pre-parse stages.
    toks = merge_hyphen_compounds(toks)
    toks = split_enclitics(toks)
    mlist = analyze_tokens(toks)
    # Phase 4 §7.3: pull Wackernagel clitics into their canonical
    # post-verbal cluster before lexicon lookup. Pronominal clitics
    # land immediately after V (and reach the grammar through the
    # NP[CASE=X] → PRON[CASE=X] shells); adverbial enclitics land at
    # the end of the clause and are absorbed by the recursive
    # S → S PART[CLITIC_CLASS=2P] rule.
    mlist = reorder_clitics(mlist)
    lex_items = lookup_lexicon(mlist)
    grammar = Grammar.load_default()
    forest = parse_with_annotations(lex_items, grammar)

    # Walk all candidate trees, collect well-formed ones, then rank.
    candidates: list[tuple[CNode, FStructure, AStructure, list[Diagnostic]]] = []
    for ctree in forest.iter_trees():
        result = solve(ctree)
        a, lmt_diags = apply_lmt_with_check(result.fstructure, lex_items)
        _, wf_diags = lfg_well_formed(result.fstructure, ctree)
        diagnostics = list(result.diagnostics) + wf_diags + lmt_diags
        if any(d.is_blocking() for d in diagnostics):
            continue
        # Phase 5n.B Commit 8 (§18 L50): in-situ Q_TYPE matrix lift.
        # Post-pass over the f-structure that detects WH=YES in any
        # embedded GF position and writes Q_TYPE=WH on the matrix.
        # Idempotent: matrices with Q_TYPE already set (wh-cleft,
        # tag-Q, yes/no-Q, Alt-Q from Commit 7) are skipped.
        _lift_in_situ_q_type(result.fstructure)
        candidates.append((ctree, result.fstructure, a, diagnostics))
    candidates.sort(key=lambda r: _rank_key(r[0]))
    parses = candidates[:n_best]

    if parses:
        return ParseResult(parses=parses, fragments=[])

    # No complete parse — emit fragments. Each fragment goes through
    # solve + lfg_well_formed too so the user sees what blocked it.
    fragments: list[Fragment] = []
    for span, frag_ctree in forest.iter_fragments():
        if len(fragments) >= fragment_cap:
            break
        try:
            result = solve(frag_ctree)
            a, lmt_diags = apply_lmt_with_check(result.fstructure, lex_items)
            _, wf_diags = lfg_well_formed(result.fstructure, frag_ctree)
        except Exception:  # noqa: BLE001
            # Fragment solve can fail for malformed sub-trees; skip
            # those rather than crashing the pipeline.
            continue
        diagnostics = list(result.diagnostics) + wf_diags + lmt_diags
        fragments.append(Fragment(
            span=span,
            ctree=frag_ctree,
            fstructure=result.fstructure,
            astructure=a,
            diagnostics=diagnostics,
        ))
    return ParseResult(parses=[], fragments=fragments)


# === Phase 5n.B Commit 8: in-situ Q_TYPE matrix lift (§18 L50) ============
#
# When a wh-marked element (WH=YES) sits in-situ inside a non-pivot
# GF — OBJ / OBJ-AGENT / OBL / ADJUNCT / XCOMP / COMP — the matrix
# clause is a wh-question even though no grammar rule fired on the
# wh-PRON / wh-N as the matrix predicate (the wh-cleft and wh-fronting
# rules in cfg/clause.py + cfg/extraction.py write Q_TYPE=WH directly
# on their matrix outputs; in-situ wh has no such grammar-rule path).
#
# This post-pass walks the matrix f-structure recursively and writes
# Q_TYPE=WH onto the matrix when any embedded GF carries WH=YES.
#
# **Filter — RC bodies**: a sub-f-structure with ``REL-PRO`` defined
# is the body of a relative clause (Phase 4 §7.5 relativization); the
# wh-marked head N is bound INSIDE the RC, not the matrix Q. The walk
# skips RC bodies so wh-PRONs nested in an RC don't promote to matrix
# Q_TYPE. Example: ``Nakita ko ang batang nakita ni Maria.`` (the wh
# inside an RC body is filtered).
#
# **Idempotent**: matrices with ``Q_TYPE`` already set (wh-cleft,
# wh-fronting, tag-Q, yes/no-Q, Phase 5n.B Commit 7 Alt-Q) are
# skipped — the grammar-rule lift is the canonical analysis; the
# post-pass only fills the gap for in-situ wh.

def _lift_in_situ_q_type(matrix: FStructure) -> None:
    """Phase 5n.B Commit 8 (§18 L50): write ``Q_TYPE='WH'`` onto a
    matrix that has a wh-marked element embedded in a GF. Idempotent
    on already-Q-marked matrices; filters out wh-marked elements
    inside relative-clause bodies (sub-f-structures with REL-PRO
    defined)."""
    if matrix.feats.get("Q_TYPE"):
        return
    visited: set[int] = {matrix.id}
    if _has_in_situ_wh(matrix.feats.values(), visited):
        matrix.feats["Q_TYPE"] = "WH"


def _has_in_situ_wh(
    values: "Iterable[object]", visited: set[int]
) -> bool:
    """Walk ``values`` (an iterable of ``FStructure.feats`` values)
    looking for a sub-f-structure with ``WH='YES'``. Skips
    relative-clause bodies (sub-f-structures with ``REL-PRO`` defined)
    and follows nested f-structures + sets uniformly. The ``visited``
    set protects against re-entrancy cycles."""
    for v in values:
        if isinstance(v, FStructure):
            if v.id in visited:
                continue
            visited.add(v.id)
            # RC body: relativization wrap binds REL-PRO on the inner
            # gapped clause's f-structure; wh inside is the relative-
            # head's binding, not a matrix wh-Q.
            if "REL-PRO" in v.feats:
                continue
            if v.feats.get("WH") is True:
                return True
            if _has_in_situ_wh(v.feats.values(), visited):
                return True
        elif isinstance(v, (set, frozenset, list, tuple)):
            if _has_in_situ_wh(v, visited):
                return True
    return False


# === Heuristic ranker (Phase 4 §7.9) ======================================

def _rank_key(ctree: CNode) -> tuple[int, int]:
    """Heuristic ranking key: smaller is better.

    Components, in priority order:

    1. ``depth`` — total number of nodes in the c-tree. Shorter
       derivations win. This breaks possessive-vs-relativization
       ambiguity (the possessive wrap nests one more layer deep).
    2. ``voice_score`` — 0 if the tree's root verb is AV, 1
       otherwise. Tagalog AV is the most-frequent voice; when the
       same surface ambiguates AV / non-AV, prefer AV.

    Lex-specificity ranking (synthesized vs hand-authored entries)
    was prototyped but dropped — distinguishing the two reliably
    needs marking on the LexicalEntry itself, not a heuristic over
    PRED templates. Revisit when the BASE / synthesizer split is
    more deterministic.
    """
    depth = _count_nodes(ctree)
    voice_score = 0 if _root_is_av(ctree) else 1
    return (depth, voice_score)


def _count_nodes(node: CNode) -> int:
    return 1 + sum(_count_nodes(c) for c in node.children)


def _root_is_av(ctree: CNode) -> bool:
    """Look for a V leaf with a ``(↑ VOICE) = 'AV'`` equation in the
    direct or first-level-nested children of the root. Searches
    only the leftmost spine — sufficient for V-initial Tagalog."""
    for child in ctree.children:
        if child.label == "V":
            for eq in child.equations:
                if "VOICE) = 'AV'" in eq:
                    return True
            return False
        for grandchild in child.children:
            if grandchild.label == "V":
                for eq in grandchild.equations:
                    if "VOICE) = 'AV'" in eq:
                        return True
                return False
    return False
