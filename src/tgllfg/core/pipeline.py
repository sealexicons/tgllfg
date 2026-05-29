# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

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
    split_apostrophe_y,
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
    chart_state_cap: int | None = None,
    max_candidates: int | None = None,
    max_tree_iterations: int | None = 5000,
    precheck_defining: bool = False,
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

    Phase 9.X.c35: ``chart_state_cap`` (default ``None``) caps Earley
    chart-state construction. When ``None``, chart construction is
    uncapped — preserves prior behavior. When set to an integer,
    ``run()`` stops processing the agenda once that many distinct
    chart states have been added, returning whatever roots have been
    built so far. The cap protects against pathological multi-rule ×
    ambiguity combinatorial explosions (e.g., the OV-INTR extension
    on sent-9 + colon list; the combined-essay test). Callers that
    need bounded latency pass an explicit cap.

    Phase 9.X.c38: ``max_candidates`` (default ``None``) early-exits
    the per-tree solve+LMT+WF loop once that many *complete*
    (non-blocking) parses have been accumulated. When ``None``, the
    pipeline walks every tree in the forest before ranking — preserves
    prior behavior. When set to an integer, the loop stops accepting
    new candidates after the budget is hit; ranking and ``n_best``
    truncation then operate over the bounded pool. Trades ranking
    breadth for bounded latency on sentences whose forests dominate
    parse time (e.g., sent-9-style colon-list × at-coord ambiguity).

    Phase 9.X.c38: ``max_tree_iterations`` (default ``5000``) caps
    the total number of forest trees visited — counting BOTH
    blocking and non-blocking parses. Complements ``max_candidates``:
    where that parameter bounds the *accepted* pool, this bounds the
    *attempted* pool. When the forest is dominated by blocking
    parses (each one consuming ~1ms of solve+LMT+WF before being
    rejected) and the valid parse lies deep in the iteration,
    ``max_candidates`` alone can't escape the loop. The iteration
    cap stops walking after the budget is exhausted regardless of
    whether any candidate was accepted; the pipeline returns
    whatever it found (possibly zero parses, in which case the
    caller falls back to fragments).

    The default ``5000`` corresponds to ~7.5s wall at ~1.5ms/tree —
    above the audit-corpus p100 latency for successful parses (so
    zero existing closures are excluded) but well under the typical
    10s SIGALRM ceiling. Set explicitly higher (or to ``None`` for
    unbounded) when investigating pathological inputs.

    Phase 10.J: ``precheck_defining`` (default ``False``) opts into
    the parse-set-preserving monotone defining-clash prune in
    ``parse/earley.py:_iter_cnodes``. The default is OFF because the
    per-combo precheck overhead is high on forests where
    defining-clashes are rare (per ``probe_10j_classify`` the audit
    corpus is mostly clash-free) — but the pruning win is large on
    forests dominated by defining-clashes (e.g., the bare-noun list
    inside PANAHON sent-9's colon appositive). Per-call selective
    use; see :func:`tgllfg.fstruct.precheck_defining_subtree`.
    """
    return parse_text_with_fragments(
        text,
        n_best=n_best,
        chart_state_cap=chart_state_cap,
        max_candidates=max_candidates,
        max_tree_iterations=max_tree_iterations,
        precheck_defining=precheck_defining,
    ).parses


def parse_text_with_fragments(
    text: str,
    *,
    n_best: int = 5,
    fragment_cap: int = 5,
    chart_state_cap: int | None = None,
    max_candidates: int | None = None,
    max_tree_iterations: int | None = 5000,
    precheck_defining: bool = False,
    splits_applied: frozenset[str] = frozenset(),
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
    # Phase 9.X.c4: bound clitic ``'y`` (post-vowel contracted ``ay``
    # topic-comment particle) gets the same triple-collapse: any
    # ``[X, ', y]`` where X is vowel-final becomes ``[X, ay]`` with a
    # synthetic ``ay`` token. ``rito'y siyesta`` → ``rito`` / ``ay``
    # / ``siyesta``. Runs after ``split_apostrophe_t`` (orderings
    # don't interact — no host produces both ``'t`` and ``'y``
    # simultaneously) and before linker-ng / hyphen-compound merges
    # so downstream consumers see the canonical ``ay``.
    toks = split_apostrophe_y(toks)
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

    # === Phase 10.J.post-1: colon-split fast path ===========================
    #
    # When the input contains a sentence-internal colon, try the
    # split-and-glue path **first**. Each half parses independently
    # against a fresh chart, then we synthesize the matrix ``S →
    # S PUNCT[COLON] X`` whose APP set carries the post-colon
    # constituent — structurally equivalent to the chart-level rule
    # in ``cfg/discourse.py:740-771`` but with no cross-colon span
    # fan-out.
    #
    # The full-chart attempt is the fallback: if the colon-split
    # fails (no NP[NOM] / S / N parses for the post-half, or the
    # glued f-structure fails well-formedness), we fall through.
    # This ordering keeps the fast path fast (sent-2 closes in 1.2s
    # vs. 12.2s under the chart-level rule, audit p100 cap is 10s)
    # while preserving the chart as the safety net for unusual
    # colon shapes the split doesn't handle.
    if ":" in text and "colon" not in splits_applied:
        split_result = _try_colon_split(
            text,
            n_best=n_best,
            chart_state_cap=chart_state_cap,
            max_candidates=max_candidates,
            max_tree_iterations=max_tree_iterations,
            precheck_defining=precheck_defining,
            splits_applied=splits_applied,
        )
        if split_result is not None and split_result.parses:
            return split_result

    # === Phase 10.J.post-2: fronted-PP-comma split fast path ===============
    #
    # Same split-and-glue pattern as the colon-split above, but for
    # the chart's 9.X.c13 ``S → PP[PREP_TYPE=REASON] PUNCT[COMMA] S``
    # fronted-Dahil-PP construction. The pre-comma PP and post-comma
    # matrix S are parsed independently against the chart, then the
    # matrix S is synthesized from the two halves. This bypasses the
    # ``(PP_internal_alts × matrix_S_alts)`` cross-product that the
    # chart-level c13 rule enumerates (sent-39's pre-comma
    # ``Dahil sa ganitong pagkakaayos ng panahon`` has 48 internal
    # NP[DAT] alternatives, post-comma matrix has 155 — product 7440
    # at one span, dominating the tree-iteration budget so the
    # canonical parse sat past cap 5000).
    #
    # Activation gates: the input must (1) start with a token whose
    # lex entry advertises ``PREP_TYPE=REASON`` (``Dahil``) and
    # (2) contain a sentence-internal comma. The pre-comma half is
    # parsed against ``PP[PREP_TYPE=REASON]`` (chart-side feat from
    # the post-2 LHS refactor); the post-comma half against ``S``.
    # If either fails the split is dropped and the chart attempt
    # runs as fallback.
    if "," in text and "fronted_pp_comma" not in splits_applied:
        split_result = _try_fronted_pp_comma_split(
            text,
            n_best=n_best,
            chart_state_cap=chart_state_cap,
            max_candidates=max_candidates,
            max_tree_iterations=max_tree_iterations,
            precheck_defining=precheck_defining,
            splits_applied=splits_applied,
        )
        if split_result is not None and split_result.parses:
            return split_result

    # === Phase 10.J.post-3: ay-fronting split fast path ====================
    #
    # Same split-and-glue pattern as the colon-split (post-1) and
    # fronted-PP-comma split (post-2), but for the chart's Phase 4
    # §7.4 ay-fronting rule ``S → NP[CASE=NOM] PART[LINK=AY] S_GAP``
    # (extraction.py:1130). Pre-``ay`` half parses as
    # ``NP[CASE=NOM]``, post-``ay`` half parses as ``S_GAP``
    # (a SUBJ-gapped clause whose REL-PRO binds to the fronted NP).
    # The matrix S is synthesized mirroring the chart rule's
    # equations.
    #
    # Motivation: sent-3 (``Ang natitirang limang buwan ay naroong
    # maghati sa init at ulan.``) was timing-blocked at cap 50000
    # (60.8s for 1 parse) because of (NP_alts × S_GAP_alts) cross-
    # product fan-out at the matrix span — plus a solve-time-only
    # ``S → NP[CASE=NOM] S_GAP`` colloquial-fronting rule (Phase
    # 5n.B C21, gated on ``(↓1 INDEF) =c 'YES'``) that the chart
    # over-predicted at every NP[NOM] + S_GAP position. The split
    # bypasses the matrix-span cross-product entirely; each half
    # parses against a small chart.
    #
    # Activation: input must contain a free-standing ``ay`` token
    # (or the bound contraction ``'y``) at a sentence-internal
    # position with non-trivial halves on each side. The detection
    # uses surface tokens (whitespace + the contraction marker)
    # rather than running the full pre-pass — fast and conservative.
    if _looks_ay_fronted(text) and "ay_fronting" not in splits_applied:
        split_result = _try_ay_fronting_split(
            text,
            n_best=n_best,
            chart_state_cap=chart_state_cap,
            max_candidates=max_candidates,
            max_tree_iterations=max_tree_iterations,
            precheck_defining=precheck_defining,
            splits_applied=splits_applied,
        )
        if split_result is not None and split_result.parses:
            return split_result

    forest = parse_with_annotations(
        lex_items, grammar,
        chart_state_cap=chart_state_cap,
        precheck_defining=precheck_defining,
    )

    # Walk candidate trees, collect well-formed ones, then rank.
    # Phase 9.X.c38: ``max_candidates`` early-exits the loop once that
    # many non-blocking parses are accumulated. ``max_tree_iterations``
    # bounds the total number of trees attempted regardless of whether
    # any were accepted (the failsafe for forests dominated by
    # blocking parses, where ``max_candidates`` alone can't escape).
    # Ranking still operates over the bounded pool.
    candidates: list[tuple[CNode, FStructure, AStructure, list[Diagnostic]]] = []
    iterations = 0
    for ctree in forest.iter_trees():
        iterations += 1
        if (max_tree_iterations is not None
                and iterations > max_tree_iterations):
            break
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
        if max_candidates is not None and len(candidates) >= max_candidates:
            break
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


# === Phase 10.J.post-1: colon-split helpers ===============================
#
# Sentence shapes covered: ``X : NP[CASE=NOM]`` (sent-2 enumeration
# head), ``X : S`` (resultative / consequence clause), ``X : N`` (bare
# N enumeration head). These parallel the three chart-level colon-
# appositive variants in ``cfg/discourse.py``: lines 748 / 756 / 764.


_POST_COLON_CATEGORIES: tuple[str, ...] = (
    "NP[CASE=NOM]",
    "S",
    "N",
)


def _split_on_colon(text: str) -> tuple[str, str] | None:
    """Find the first non-leaf ``:`` and return ``(pre, post)``.

    Returns ``None`` when the colon is at the very start / end (no
    matrix to glue) or absent. The ``:`` itself is dropped from the
    output halves.
    """
    idx = text.find(":")
    if idx <= 0 or idx >= len(text) - 1:
        return None
    pre = text[:idx].strip()
    post = text[idx + 1:].strip()
    if not pre or not post:
        return None
    return pre, post


def _normalize_terminal_punct(text: str) -> str:
    """Add a trailing ``.`` if the segment doesn't already end in
    sentence-terminal punctuation. The chart's matrix S rules expect
    a closing PUNCT[PUNCT_CLASS=PERIOD]; segments lifted out of a
    colon-split don't carry their own terminator, so we add one."""
    if text.endswith((".", "!", "?")):
        return text
    # Strip a trailing comma if the segment carries one (the pre-colon
    # half won't, but a post-colon half might if the source text had
    # ``... , ``: extra commas before the period). The synthesized
    # period replaces any trailing comma.
    if text.endswith(","):
        text = text[:-1].rstrip()
    return text + "."


def _try_colon_split(
    text: str,
    *,
    n_best: int,
    chart_state_cap: int | None,
    max_candidates: int | None,
    max_tree_iterations: int | None,
    precheck_defining: bool,
    splits_applied: frozenset[str] = frozenset(),
) -> ParseResult | None:
    """Parse ``pre`` (as ``S``) and ``post`` (as one of
    :data:`_POST_COLON_CATEGORIES`) independently, then synthesize a
    matrix ``S`` whose APP set contains the post constituent.

    Returns ``None`` when the split itself isn't possible, when the
    pre-half doesn't yield an ``S`` parse, or when no post-category
    succeeds. Otherwise returns a :class:`ParseResult` carrying one
    or more glued parses (one per post-category that succeeded × the
    pre-half's n-best alternatives).
    """
    halves = _split_on_colon(text)
    if halves is None:
        return None
    pre_text, post_text = halves
    pre_text = _normalize_terminal_punct(pre_text)
    post_text = _normalize_terminal_punct(post_text)

    # Parse the pre-colon half as ``S`` via the segment helper. We
    # deliberately avoid re-entering :func:`parse_text_with_fragments`
    # so multi-colon inputs don't recurse — the chart-level rules
    # handle any residual colon when the pre-half is solved as a
    # standalone clause.
    pre_parses = _parse_segment_as(
        pre_text,
        start_symbol="S",
        n_best=n_best,
        chart_state_cap=chart_state_cap,
        max_candidates=max_candidates,
        max_tree_iterations=max_tree_iterations,
        precheck_defining=precheck_defining,
        splits_applied=splits_applied | frozenset({"colon"}),
    )
    if not pre_parses:
        return None

    # Try each post-colon category in order; the first that yields a
    # parse wins. This mirrors the three chart-level colon-appositive
    # variants in cfg/discourse.py — we don't enumerate post-NP and
    # post-S parses, the first success short-circuits.
    post_parses: list[tuple[CNode, FStructure, AStructure, list[Diagnostic]]] = []
    for category in _POST_COLON_CATEGORIES:
        post_parses = _parse_segment_as(
            post_text,
            start_symbol=category,
            n_best=n_best,
            chart_state_cap=chart_state_cap,
            max_candidates=max_candidates,
            max_tree_iterations=max_tree_iterations,
            precheck_defining=precheck_defining,
            splits_applied=splits_applied | frozenset({"colon"}),
        )
        if post_parses:
            break
    if not post_parses:
        return None

    # Synthesize one glued parse per (pre × post) combination, capped
    # at ``n_best``. Both halves must keep passing well-formedness on
    # the glued f-structure or the candidate is dropped.
    glued: list[tuple[CNode, FStructure, AStructure, list[Diagnostic]]] = []
    for pre_parse in pre_parses:
        for post_parse in post_parses:
            glued_one = _glue_colon_appositive(pre_parse, post_parse)
            if glued_one is not None:
                glued.append(glued_one)
                if len(glued) >= n_best:
                    break
        if len(glued) >= n_best:
            break

    if not glued:
        return None
    return ParseResult(parses=glued, fragments=[])


def _parse_segment_as(
    text: str,
    *,
    start_symbol: str,
    n_best: int,
    chart_state_cap: int | None,
    max_candidates: int | None,
    max_tree_iterations: int | None,
    precheck_defining: bool,
    splits_applied: frozenset[str] = frozenset(),
) -> list[tuple[CNode, FStructure, AStructure, list[Diagnostic]]]:
    """Parse ``text`` against the grammar with a non-default start
    symbol (e.g., ``NP[CASE=NOM]``). Returns the surviving parses.

    Mirrors the pre-processing chain in :func:`parse_text_with_fragments`
    up through the chart call, then runs the same solve / LMT / WF
    loop but writes the start symbol into ``parse_with_annotations``.

    Phase 10.J.post-4: when called from inside a split (``splits_applied``
    is non-empty) with ``start_symbol == "S"``, route through
    :func:`parse_text_with_fragments` so the other (un-applied) splits
    can fire on this segment too. This gives sent-9's inner ay-clause
    (whose pre-half rides the colon-split path) access to post-3's
    ay-fronting-split, producing the same TOPIC == REL-PRO == SUBJ
    identity that a top-level ay-fronted sentence gets — a consistency
    fix more than just future-proofing. For non-S start symbols
    (``NP[X]``, ``S_GAP``, ``PP[X]``, ``N``) the splits' glue
    functions wouldn't fit so we go direct to chart.
    """
    if start_symbol == "S" and splits_applied:
        chained_result = parse_text_with_fragments(
            text,
            n_best=n_best,
            chart_state_cap=chart_state_cap,
            max_candidates=max_candidates,
            max_tree_iterations=max_tree_iterations,
            precheck_defining=precheck_defining,
            splits_applied=splits_applied,
        )
        if chained_result.parses:
            return list(chained_result.parses)
        # Pipeline routing returned no parses — the chart attempt
        # inside parse_text_with_fragments already tried and failed,
        # so no falling-through to a duplicate chart parse here.
        return []

    toks = tokenize(text)
    toks = split_apostrophe_t(toks)
    toks = split_apostrophe_y(toks)
    toks = split_linker_ng(toks)
    toks = merge_hyphen_compounds(toks)
    toks = split_enclitics(toks)
    mlist = analyze_tokens(toks)
    mlist = reorder_clitics(mlist)
    lex_items = lookup_lexicon(mlist)
    grammar = Grammar.load_default()
    forest = parse_with_annotations(
        lex_items, grammar,
        chart_state_cap=chart_state_cap,
        precheck_defining=precheck_defining,
        start_symbol=start_symbol,
    )

    candidates: list[tuple[CNode, FStructure, AStructure, list[Diagnostic]]] = []
    iterations = 0
    for ctree in forest.iter_trees():
        iterations += 1
        if (max_tree_iterations is not None
                and iterations > max_tree_iterations):
            break
        result = solve(ctree)
        a, lmt_diags = apply_lmt_with_check(result.fstructure, lex_items)
        _, wf_diags = lfg_well_formed(result.fstructure, ctree)
        diagnostics = list(result.diagnostics) + wf_diags + lmt_diags
        if any(d.is_blocking() for d in diagnostics):
            continue
        candidates.append((ctree, result.fstructure, a, diagnostics))
        if max_candidates is not None and len(candidates) >= max_candidates:
            break
    candidates.sort(key=lambda r: _rank_key(r[0]))
    if candidates:
        return candidates[:n_best]

    # Phase 10.J.post-1: pipeline-level comma+at NP split fallback.
    # When parsing an NP-shaped segment fails (e.g., the post-half of
    # a colon-split on PANAHON sent-2), try splitting on ``, at`` and
    # gluing the two NP halves as a COORD=AND coordination. This
    # avoids the chart-state-count cost of a binary comma+at coord
    # rule (which would push canonical short-c-tree parses past the
    # default tree-iteration cap on sentences without a comma) by
    # keeping the synthesis fully at pipeline level.
    if start_symbol.startswith("NP["):
        comma_at_result = _try_comma_at_np_split(
            text,
            start_symbol=start_symbol,
            n_best=n_best,
            chart_state_cap=chart_state_cap,
            max_candidates=max_candidates,
            max_tree_iterations=max_tree_iterations,
            precheck_defining=precheck_defining,
        )
        if comma_at_result:
            return comma_at_result
    return []


def _glue_colon_appositive(
    pre_parse: tuple[CNode, FStructure, AStructure, list[Diagnostic]],
    post_parse: tuple[CNode, FStructure, AStructure, list[Diagnostic]],
) -> tuple[CNode, FStructure, AStructure, list[Diagnostic]] | None:
    """Synthesize the matrix ``S → S PUNCT[COLON] X`` parse from two
    independently-parsed halves.

    Returns ``None`` if the synthesized f-structure fails the same
    well-formedness check the chart-level colon rule would have run.
    Otherwise returns the glued ``(ctree, fstruct, astruct, diags)``.

    The matrix f-structure shares identity with the pre-half (the
    chart rule's ``(↑) = ↓1``), so we mutate ``pre_fs.feats`` in
    place to add the post-half's f-structure to APP (the chart
    rule's ``↓3 ∈ (↑ APP)``). The pre-half's diagnostics already
    reflect its solve / WF / LMT passes; we just append the post's.
    """
    pre_ctree, pre_fs, pre_a, pre_diags = pre_parse
    post_ctree, post_fs, _post_a, post_diags = post_parse
    # Synthetic colon PUNCT leaf — no equations, syncategorematic in
    # the chart rule too.
    colon_leaf = CNode(
        label="PUNCT[PUNCT_CLASS=COLON]",
        children=[],
        equations=[],
    )
    matrix_ctree = CNode(
        label="S",
        children=[pre_ctree, colon_leaf, post_ctree],
        equations=[],
    )
    # Set-membership write: APP gets a new frozenset containing the
    # post f-structure (union with any prior APP membership, but the
    # pre-half typically has none — this is the first colon-appositive
    # to attach).
    existing_app = pre_fs.feats.get("APP")
    if existing_app is None:
        new_app: frozenset[FStructure] = frozenset({post_fs})
    elif isinstance(existing_app, frozenset):
        new_app = existing_app | {post_fs}
    else:  # pragma: no cover — APP is set-valued in every grammar path
        return None
    pre_fs.feats["APP"] = new_app
    # Re-run the in-situ Q_TYPE lift over the matrix f-structure (the
    # post-half's WH-bearing GFs may need to surface as Q_TYPE=WH).
    _lift_in_situ_q_type(pre_fs)
    # Verify the glued f-structure still passes well-formedness.
    _, wf_diags = lfg_well_formed(pre_fs, matrix_ctree)
    if any(d.is_blocking() for d in wf_diags):
        # Restore APP so subsequent glue attempts don't see our write.
        if existing_app is None:
            del pre_fs.feats["APP"]
        else:
            pre_fs.feats["APP"] = existing_app
        return None
    diagnostics = list(pre_diags) + list(post_diags) + list(wf_diags)
    return matrix_ctree, pre_fs, pre_a, diagnostics


# === Phase 10.J.post-1: comma+at NP coord split ==========================
#
# ``ang panahon ng tag-init mula Abril hanggang Hunyo, at ang
# panahon ng tag-ulan mula Hulyo hanggang Oktubre`` — binary
# Oxford-comma-style NP coord. Synthesized at pipeline level to
# avoid the chart-state count cost that a competing chart rule
# would incur on every NP[CASE=X, COORD=AND] prediction.


def _try_comma_at_np_split(
    text: str,
    *,
    start_symbol: str,
    n_best: int,
    chart_state_cap: int | None,
    max_candidates: int | None,
    max_tree_iterations: int | None,
    precheck_defining: bool,
) -> list[tuple[CNode, FStructure, AStructure, list[Diagnostic]]] | None:
    """If ``text`` looks like ``X, at Y`` (or ``X, at Y.``), parse each
    half as ``start_symbol`` (typically ``NP[CASE=NOM]``) and
    synthesize a COORD=AND coordination NP whose CONJUNCTS set
    holds both halves' f-structures.

    Returns ``None`` when no ``, at`` separator is found, when
    either half fails to parse, or when the case extracted from
    ``start_symbol`` is unrecognised. Otherwise returns the glued
    parses.
    """
    # Extract the CASE from the start symbol so the synthesized
    # matrix carries the same case. The colon-split fast path passes
    # ``NP[CASE=NOM]`` for sent-2-style enumerations; the same
    # synthesis applies to GEN and DAT NPs if a caller ever requests
    # them via that start symbol.
    case = _extract_case(start_symbol)
    if case is None:
        return None
    # Find a ``, at`` separator (or ``,at``) that's the binary
    # join's hinge. The split is conservative: at most one ``, at``
    # split, on the outermost (= leftmost) match. Trailing period /
    # whitespace is tolerated.
    work = text.rstrip().rstrip(".").rstrip()
    sep_idx = work.find(", at ")
    if sep_idx < 0:
        sep_idx = work.find(",at ")
        if sep_idx < 0:
            return None
        sep_len = len(",at ")
    else:
        sep_len = len(", at ")
    pre_text = work[:sep_idx].strip()
    post_text = work[sep_idx + sep_len:].strip()
    if not pre_text or not post_text:
        return None
    pre_text = _normalize_terminal_punct(pre_text)
    post_text = _normalize_terminal_punct(post_text)
    # Parse each conjunct independently with the requested start
    # symbol. We use ``_parse_segment_as`` directly — this triggers
    # the same fallback chain (so a conjunct may itself be another
    # comma+at split if the corpus ever needs it).
    pre_parses = _parse_segment_as(
        pre_text,
        start_symbol=start_symbol,
        n_best=n_best,
        chart_state_cap=chart_state_cap,
        max_candidates=max_candidates,
        max_tree_iterations=max_tree_iterations,
        precheck_defining=precheck_defining,
    )
    if not pre_parses:
        return None
    post_parses = _parse_segment_as(
        post_text,
        start_symbol=start_symbol,
        n_best=n_best,
        chart_state_cap=chart_state_cap,
        max_candidates=max_candidates,
        max_tree_iterations=max_tree_iterations,
        precheck_defining=precheck_defining,
    )
    if not post_parses:
        return None
    glued: list[tuple[CNode, FStructure, AStructure, list[Diagnostic]]] = []
    for pre_parse in pre_parses:
        for post_parse in post_parses:
            g = _glue_comma_at_np(pre_parse, post_parse, case=case)
            if g is not None:
                glued.append(g)
                if len(glued) >= n_best:
                    break
        if len(glued) >= n_best:
            break
    return glued or None


def _extract_case(start_symbol: str) -> str | None:
    """Parse the CASE feature out of an ``NP[CASE=X, ...]`` start
    symbol string; return ``X`` or ``None`` if not present.
    """
    if not start_symbol.startswith("NP["):
        return None
    bracket = start_symbol[len("NP["):].rstrip("]")
    for kv in bracket.split(","):
        k, _, v = kv.strip().partition("=")
        if k == "CASE":
            return v.strip()
    return None


def _glue_comma_at_np(
    pre_parse: tuple[CNode, FStructure, AStructure, list[Diagnostic]],
    post_parse: tuple[CNode, FStructure, AStructure, list[Diagnostic]],
    *,
    case: str,
) -> tuple[CNode, FStructure, AStructure, list[Diagnostic]] | None:
    """Synthesize ``NP[CASE=case, COORD=AND] → NP[CASE=case]
    PUNCT[COMMA] PART[COORD=AND] NP[CASE=case]`` from two parsed
    halves. The matrix f-structure is a fresh node (neither
    conjunct IS the matrix — both are CONJUNCTS members) carrying
    ``CASE``, ``COORD='AND'``, and ``NUM='PL'``.

    Returns ``None`` if the synthesized f-structure fails the
    chart-equivalent well-formedness check.
    """
    pre_ctree, pre_fs, _pre_a, pre_diags = pre_parse
    post_ctree, post_fs, post_a, post_diags = post_parse
    comma_leaf = CNode(
        label="PUNCT[PUNCT_CLASS=COMMA]", children=[], equations=[],
    )
    at_leaf = CNode(
        label="PART[COORD=AND]", children=[], equations=[],
    )
    matrix_ctree = CNode(
        label=f"NP[CASE={case},COORD=AND]",
        children=[pre_ctree, comma_leaf, at_leaf, post_ctree],
        equations=[],
    )
    matrix_fs = FStructure(feats={
        "CASE": case,
        "COORD": "AND",
        "NUM": "PL",
        "CONJUNCTS": frozenset({pre_fs, post_fs}),
    })
    # The matrix is structurally simple; the well-formedness pass
    # mostly verifies that the CONJUNCTS members don't themselves
    # carry blocking diagnostics — but since both halves already
    # passed their own WF/LMT checks during _parse_segment_as,
    # the union is well-formed by construction. We still run the
    # check to mirror the chart-rule equivalence and surface any
    # unexpected interaction.
    _, wf_diags = lfg_well_formed(matrix_fs, matrix_ctree)
    if any(d.is_blocking() for d in wf_diags):
        return None
    diagnostics = list(pre_diags) + list(post_diags) + list(wf_diags)
    return matrix_ctree, matrix_fs, post_a, diagnostics


# === Phase 10.J.post-2: fronted-PP-comma split ============================
#
# Same split-and-glue pattern as the colon-split, but for the
# chart's 9.X.c13 ``S → PP[PREP_TYPE=REASON] PUNCT[COMMA] S`` rule.
# Parses pre and post halves independently then synthesizes the
# matrix S — bypassing the cross-product fan-out the chart-level
# rule produces at the matrix span (PANAHON sent-39 had 7440
# trees at one span; the canonical parse sat past cap 5000 even
# after pushing PREP_TYPE / DISCOURSE_POS gates to chart-time).


def _try_fronted_pp_comma_split(
    text: str,
    *,
    n_best: int,
    chart_state_cap: int | None,
    max_candidates: int | None,
    max_tree_iterations: int | None,
    precheck_defining: bool,
    splits_applied: frozenset[str] = frozenset(),
) -> ParseResult | None:
    """If ``text`` looks like ``REASON-PREP X, Y`` (e.g.,
    ``Dahil sa ganitong pagkakaayos ng panahon, …``), parse the
    pre-comma half as ``PP[PREP_TYPE=REASON]`` and the post-comma
    half as ``S``, then synthesize the matrix ``S → PP PUNCT[COMMA]
    S`` parse.

    Returns ``None`` when the activation pattern doesn't match,
    when either half fails to parse, or when the synthesized
    f-structure fails well-formedness.
    """
    # Activation: input must start with a known REASON-PREP lemma.
    # We restrict to attested fronted-REASON-PP heads (currently
    # ``Dahil``) — a broader trigger (any PREP head) would over-
    # activate on sentences where the leading PREP isn't actually
    # being fronted (e.g., a clause-internal PP).
    stripped = text.lstrip()
    if not stripped:
        return None
    first_word = stripped.split(None, 1)[0]
    if first_word.casefold() not in _REASON_PREP_LEMMAS:
        return None
    # Find the leftmost top-level comma — we don't try to handle
    # nested fronted PPs (would need to track quotes / parens etc.).
    comma_idx = text.find(",")
    if comma_idx <= 0 or comma_idx >= len(text) - 1:
        return None
    pre_text = text[:comma_idx].strip()
    post_text = text[comma_idx + 1:].strip()
    if not pre_text or not post_text:
        return None
    pre_text = _normalize_terminal_punct(pre_text)
    post_text = _normalize_terminal_punct(post_text)

    pre_parses = _parse_segment_as(
        pre_text,
        start_symbol="PP[PREP_TYPE=REASON]",
        n_best=n_best,
        chart_state_cap=chart_state_cap,
        max_candidates=max_candidates,
        max_tree_iterations=max_tree_iterations,
        precheck_defining=precheck_defining,
        splits_applied=splits_applied | frozenset({"fronted_pp_comma"}),
    )
    if not pre_parses:
        return None
    post_parses = _parse_segment_as(
        post_text,
        start_symbol="S",
        n_best=n_best,
        chart_state_cap=chart_state_cap,
        max_candidates=max_candidates,
        max_tree_iterations=max_tree_iterations,
        precheck_defining=precheck_defining,
        splits_applied=splits_applied | frozenset({"fronted_pp_comma"}),
    )
    if not post_parses:
        return None

    glued: list[tuple[CNode, FStructure, AStructure, list[Diagnostic]]] = []
    for pre_parse in pre_parses:
        for post_parse in post_parses:
            g = _glue_fronted_pp_comma(pre_parse, post_parse)
            if g is not None:
                glued.append(g)
                if len(glued) >= n_best:
                    break
        if len(glued) >= n_best:
            break
    if not glued:
        return None
    return ParseResult(parses=glued, fragments=[])


_REASON_PREP_LEMMAS: frozenset[str] = frozenset({"dahil"})


def _glue_fronted_pp_comma(
    pre_parse: tuple[CNode, FStructure, AStructure, list[Diagnostic]],
    post_parse: tuple[CNode, FStructure, AStructure, list[Diagnostic]],
) -> tuple[CNode, FStructure, AStructure, list[Diagnostic]] | None:
    """Synthesize ``S → PP[PREP_TYPE=REASON] PUNCT[COMMA] S`` from
    two parsed halves, mirroring the chart-level c13 rule:
    ``(↑) = ↓3``, ``(↑ TOPIC) = ↓1``, ``↓1 ∈ (↑ ADJ)``.

    Returns ``None`` if the assembled f-structure fails the
    well-formedness check the chart rule would have run.
    """
    pre_ctree, pre_fs, _pre_a, pre_diags = pre_parse
    post_ctree, post_fs, post_a, post_diags = post_parse
    comma_leaf = CNode(
        label="PUNCT[PUNCT_CLASS=COMMA]", children=[], equations=[],
    )
    matrix_ctree = CNode(
        label="S",
        children=[pre_ctree, comma_leaf, post_ctree],
        equations=[],
    )
    # Matrix f-structure shares identity with the post-comma S
    # (c13's ``(↑) = ↓3``); we mutate post_fs.feats in place to
    # add TOPIC and ADJ-membership (``(↑ TOPIC) = ↓1``,
    # ``↓1 ∈ (↑ ADJ)``).
    if "TOPIC" in post_fs.feats:
        # Don't overwrite an existing TOPIC — the chart rule's
        # equality would fail-by-clash there too.
        return None
    post_fs.feats["TOPIC"] = pre_fs
    existing_adj = post_fs.feats.get("ADJ")
    if existing_adj is None:
        new_adj: frozenset[FStructure] = frozenset({pre_fs})
    elif isinstance(existing_adj, frozenset):
        new_adj = existing_adj | {pre_fs}
    else:  # pragma: no cover — ADJ is set-valued
        return None
    post_fs.feats["ADJ"] = new_adj
    _lift_in_situ_q_type(post_fs)
    _, wf_diags = lfg_well_formed(post_fs, matrix_ctree)
    if any(d.is_blocking() for d in wf_diags):
        # Restore if the glued state is rejected so subsequent
        # candidates don't see our writes.
        del post_fs.feats["TOPIC"]
        if existing_adj is None:
            del post_fs.feats["ADJ"]
        else:
            post_fs.feats["ADJ"] = existing_adj
        return None
    diagnostics = list(pre_diags) + list(post_diags) + list(wf_diags)
    return matrix_ctree, post_fs, post_a, diagnostics


# === Phase 10.J.post-3: ay-fronting split ================================
#
# Same split-and-glue pattern as the colon-split (post-1) and
# fronted-PP-comma split (post-2), but for the chart's Phase 4
# §7.4 ay-fronting rule ``S → NP[CASE=NOM] PART[LINK=AY] S_GAP``
# (extraction.py:1130). PANAHON sent-3 (``Ang natitirang limang
# buwan ay naroong maghati sa init at ulan.``) was timing-
# blocked at cap=50000 (60.8s) under the chart-level cross-product
# fan-out — the colloquial no-``ay`` variant (Phase 5n.B C21,
# solve-time INDEF=YES gate) over-predicted at every
# NP[NOM]+S_GAP position, compounding the matrix-span fan-out.
# Splitting on ``ay`` parses each half independently against a
# small chart (sent-3 halves: NP 0.7s + S_GAP 0.1s = 0.8s vs.
# >60s for the full sentence).


def _looks_ay_fronted(text: str) -> bool:
    """Cheap heuristic: ``text`` contains a free-standing ``ay``
    token (between whitespace boundaries) or the bound contraction
    ``'y``. False on pure leading ``ay`` (``Ay, sandali`` etc.) and
    purely trailing ``ay`` — the split needs non-trivial halves
    on each side.
    """
    # The split-pre-pass tokenizer would canonicalize ``'y`` to
    # ``ay``, but at the surface-string level we look for either.
    lowered = text.lower()
    # Bound contraction: e.g., ``rito'y siyesta``.
    if "'y " in lowered:
        return True
    # Free-standing ``ay`` token bounded by whitespace on both sides.
    parts = lowered.split()
    if "ay" in parts[1:-1]:  # not first / last token
        return True
    return False


def _try_ay_fronting_split(
    text: str,
    *,
    n_best: int,
    chart_state_cap: int | None,
    max_candidates: int | None,
    max_tree_iterations: int | None,
    precheck_defining: bool,
    splits_applied: frozenset[str] = frozenset(),
) -> ParseResult | None:
    """If ``text`` matches the ``NP ay S_GAP`` ay-fronting pattern,
    parse the pre-``ay`` half as ``NP[CASE=NOM]`` and the
    post-``ay`` half as ``S_GAP``, then synthesize the matrix
    ``S → NP PART[LINK=AY] S_GAP`` parse.

    Returns ``None`` when the split isn't possible, either half
    fails to parse, or the synthesized f-structure fails
    well-formedness.
    """
    halves = _split_on_ay(text)
    if halves is None:
        return None
    pre_text, post_text = halves
    if not pre_text or not post_text:
        return None
    pre_text = _normalize_terminal_punct(pre_text)
    post_text = _normalize_terminal_punct(post_text)

    pre_parses = _parse_segment_as(
        pre_text,
        start_symbol="NP[CASE=NOM]",
        n_best=n_best,
        chart_state_cap=chart_state_cap,
        max_candidates=max_candidates,
        max_tree_iterations=max_tree_iterations,
        precheck_defining=precheck_defining,
        splits_applied=splits_applied | frozenset({"ay_fronting"}),
    )
    if not pre_parses:
        return None
    post_parses = _parse_segment_as(
        post_text,
        start_symbol="S_GAP",
        n_best=n_best,
        chart_state_cap=chart_state_cap,
        max_candidates=max_candidates,
        max_tree_iterations=max_tree_iterations,
        precheck_defining=precheck_defining,
        splits_applied=splits_applied | frozenset({"ay_fronting"}),
    )
    if not post_parses:
        return None

    glued: list[tuple[CNode, FStructure, AStructure, list[Diagnostic]]] = []
    for pre_parse in pre_parses:
        for post_parse in post_parses:
            g = _glue_ay_fronted(pre_parse, post_parse)
            if g is not None:
                glued.append(g)
                if len(glued) >= n_best:
                    break
        if len(glued) >= n_best:
            break
    if not glued:
        return None
    return ParseResult(parses=glued, fragments=[])


def _split_on_ay(text: str) -> tuple[str, str] | None:
    """Find the leftmost free-standing ``ay`` (or bound ``'y``) and
    return ``(pre, post)`` with the splitter dropped. Returns
    ``None`` when the splitter is at an edge or absent.
    """
    # Bound ``'y`` contraction: split at the apostrophe, keep the
    # preceding vowel-final word in the pre-half. Surface example:
    # ``Rito'y siyesta`` → pre=``Rito``, post=``siyesta``.
    apos_idx = text.find("'y ")
    if apos_idx >= 0:
        pre = text[:apos_idx].rstrip()
        post = text[apos_idx + 3:].lstrip()
        return (pre, post) if pre and post else None
    # Free-standing ``ay`` between whitespace boundaries.
    # We use a word-aligned search: split on whitespace, find ``ay``,
    # then reassemble. Conservative — first hit only.
    parts = text.split()
    if len(parts) < 3:
        return None
    for i, w in enumerate(parts):
        if w.lower() == "ay" and 0 < i < len(parts) - 1:
            pre = " ".join(parts[:i])
            post = " ".join(parts[i + 1:])
            return pre, post
    return None


def _glue_ay_fronted(
    pre_parse: tuple[CNode, FStructure, AStructure, list[Diagnostic]],
    post_parse: tuple[CNode, FStructure, AStructure, list[Diagnostic]],
) -> tuple[CNode, FStructure, AStructure, list[Diagnostic]] | None:
    """Synthesize ``S → NP[CASE=NOM] PART[LINK=AY] S_GAP`` from
    two parsed halves, mirroring the Phase 4 §7.4 chart rule:
    ``(↑) = ↓3`` (matrix = inner S_GAP),
    ``(↑ TOPIC) = ↓1`` (fronted NP is the topic),
    ``(↓3 REL-PRO) = ↓1`` (REL-PRO bound to fronted NP),
    ``(↓3 REL-PRO) =c (↓3 SUBJ)`` (constraining — gap is SUBJ).

    Returns ``None`` if the synthesized f-structure fails the
    well-formedness check.
    """
    pre_ctree, pre_fs, _pre_a, pre_diags = pre_parse
    post_ctree, post_fs, post_a, post_diags = post_parse
    ay_leaf = CNode(
        label="PART[LINK=AY]", children=[], equations=[],
    )
    matrix_ctree = CNode(
        label="S",
        children=[pre_ctree, ay_leaf, post_ctree],
        equations=[],
    )
    # Matrix shares identity with the inner S_GAP (``(↑) = ↓3``);
    # mutate post_fs.feats in place.
    if "TOPIC" in post_fs.feats:
        return None
    # REL-PRO / SUBJ re-pointing: the chart rule's
    # ``(↓3 REL-PRO) = ↓1`` defining-unifies REL-PRO with the
    # fronted NP, and the S_GAP body's internal
    # ``(↑ SUBJ) = (↑ REL-PRO)`` makes SUBJ share identity with
    # REL-PRO. To mirror that — and to pass the test pin
    # ``TOPIC.id == SUBJ.id`` — re-point both slots to pre_fs.
    # The standalone S_GAP body's REL-PRO / SUBJ nodes were
    # empty placeholders (the gap), so no information is lost.
    snapshot: dict[str, object] = {}
    for slot in ("TOPIC", "REL-PRO", "SUBJ"):
        if slot in post_fs.feats:
            snapshot[slot] = post_fs.feats[slot]
    post_fs.feats["TOPIC"] = pre_fs
    post_fs.feats["REL-PRO"] = pre_fs
    post_fs.feats["SUBJ"] = pre_fs
    _lift_in_situ_q_type(post_fs)
    _, wf_diags = lfg_well_formed(post_fs, matrix_ctree)
    if any(d.is_blocking() for d in wf_diags):
        # Restore so subsequent glue attempts don't see our writes.
        for slot in ("TOPIC", "REL-PRO", "SUBJ"):
            if slot in snapshot:
                post_fs.feats[slot] = snapshot[slot]
            elif slot in post_fs.feats:
                del post_fs.feats[slot]
        return None
    diagnostics = list(pre_diags) + list(post_diags) + list(wf_diags)
    return matrix_ctree, post_fs, post_a, diagnostics


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
