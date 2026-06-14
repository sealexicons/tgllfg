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
from dataclasses import dataclass, field

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
    merge_multiword_compounds,
    normalize_parens,
    normalize_quoted_spans,
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
    # Phase 14.B.6: c-node → f-node correspondence (id(CNode) → id(FStructure
    # object)); see SolveResult.correspondence. None when not computed.
    correspondence: dict[int, int] | None = None


@dataclass(frozen=True)
class ParseResult:
    """The full output of :func:`parse_text_with_fragments`. At
    most one of ``parses`` and ``fragments`` is non-empty: complete
    parses suppress fragment output (the user wanted a parse, they
    got one); fragments only surface when no complete parse exists."""
    parses: list[tuple[CNode, FStructure, AStructure, list[Diagnostic]]]
    fragments: list[Fragment]
    # Phase 14.B.6/.7: per-parse c-node → f-node correspondence, aligned 1:1
    # with ``parses`` (empty list when not computed). Solve-path parses get it
    # from ``solve`` (.6); glued split-path parses compose it from their halves
    # (.7, see :func:`_glued_result` and the ``_glue_*`` functions).
    correspondences: list[dict[int, int] | None] = field(default_factory=list)


# Phase 14.B.7: the internal 5-tuple threaded through the split-and-glue path —
# a parse plus its φ correspondence (``id(CNode)`` → ``id(FStructure)``). The
# public :class:`ParseResult` splits this back into ``parses`` (4-tuples) +
# ``correspondences`` via :func:`_glued_result`; the glue functions compose a
# child's map by unioning the two halves' maps and pinning each synthetic
# c-node to the f-structure it projects to.
_GluedParse = tuple[CNode, FStructure, AStructure, list[Diagnostic], dict[int, int]]


def _glued_result(glued: list[_GluedParse]) -> ParseResult:
    """Build a :class:`ParseResult` from the split-path 5-tuples, peeling the
    φ correspondence off each into ``correspondences`` (aligned 1:1 with
    ``parses``)."""
    return ParseResult(
        parses=[(ct, fs, a, d) for ct, fs, a, d, _corr in glued],
        fragments=[],
        correspondences=[corr for _ct, _fs, _a, _d, corr in glued],
    )


def _fstructure_signature(value: object, _ancestors: tuple[int, ...] = ()) -> str:
    """A cycle-safe structural signature of an f-structure value.

    Two f-structures that are structurally equal (same attributes, same
    atomic values, same nesting / set membership) get the same string,
    regardless of object identity or the per-graph ``FStructure.id``
    counter. Reentrant back-edges within the current DFS path collapse to a
    fixed ``@cycle`` marker (keeps the walk finite); shared (DAG) subgraphs
    expand identically in identical inputs, so equal structures still match.

    Phase 14.final.post-9: used by :func:`_dedup_glued` to collapse the
    spuriously-ambiguous parses the split-and-glue cross-product produces
    (distinct objects, identical content) before they fan out into matrix
    parses — the source of the colon/em-dash APP leak on PANAHON sent-2.
    """
    if isinstance(value, FStructure):
        if id(value) in _ancestors:
            return "@cycle"
        nxt = _ancestors + (id(value),)
        body = ",".join(
            f"{k}={_fstructure_signature(v, nxt)}"
            for k, v in sorted(value.feats.items())
        )
        return "{" + body + "}"
    if isinstance(value, (frozenset, set)):
        return "[" + ",".join(sorted(
            _fstructure_signature(m, _ancestors) for m in value
        )) + "]"
    return repr(value)


def _dedup_glued(parses: list[_GluedParse]) -> list[_GluedParse]:
    """Drop parses whose f-structure is structurally identical to an earlier
    one, keeping the first occurrence (so rank order is preserved).

    Deduping the *halves* a split feeds into its glue loop is what keeps the
    cumulative in-place APP / set writes correct: when the spurious copies
    collapse to one, each ``pre_fs`` is glued at most once, so its set-valued
    feats accumulate exactly one member instead of leaking every sibling
    glue's contribution (PANAHON sent-2's APP held 4 near-duplicate
    coordinations, only one of which any c-node projected to — hence the
    φ-orphaned appositive f-nodes the inspector couldn't cross-highlight).
    """
    seen: set[str] = set()
    out: list[_GluedParse] = []
    for parse in parses:
        sig = _fstructure_signature(parse[1])
        if sig in seen:
            continue
        seen.add(sig)
        out.append(parse)
    return out


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
    # Phase 10.J.post-12.6: convert balanced ASCII quote pairs to
    # curly variants so the chart's quotation rules consume them.
    # See :func:`tgllfg.text.quotes.normalize_quoted_spans` for the
    # clitic-protection and inner-content classification rules
    # (mention / direct-speech / opaque). Stray ASCII apostrophes
    # (abbreviation prefixes like ``'yon`` and unbalanced singletons)
    # stay ASCII so the existing ``_strip_non_content`` ``_UNK``-strip
    # path preserves their parse coverage. Runs before
    # :func:`normalize_parens` so quote-bracket positions are
    # established before paren-gloss stripping; the two pre-passes
    # are independent (no paren-quote nesting in audited corpora).
    text = normalize_quoted_spans(text)
    # Phase 10.J.post-12.3: strip pedagogical-gloss parens
    # (``mag-aaral (estudyante)`` → ``mag-aaral``) and the paren
    # delimiters around sentence-wrap parentheticals
    # (``(Kaibigan ko siya.)`` → ``Kaibigan ko siya.``). See
    # :func:`tgllfg.text.tokenizer.normalize_parens` for the
    # single-word-gloss vs multi-word discrimination.
    text = normalize_parens(text)
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
    # Phase 10.J.post-12.4: collapse fixed multi-word expressions
    # (``oras Pilipino`` "Filipino time"; ``ibig sabihin`` "meaning")
    # into a single token whose joined norm matches a multi-word
    # citation in nouns.yaml. Runs after the linker pre-pass (so
    # vowel-final left tokens carry no surplus ``-ng`` token that
    # would block the bigram match) and before the hyphen-compound
    # merger.
    toks = merge_multiword_compounds(toks)
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

    # === Phase 10.J.post-12.4: single-em-dash split fast path ==============
    #
    # Single em-dash (`--`, double hyphen-minus in plain text) followed
    # by a continuation clause / appositive functions like a colon —
    # introduces an apposition or consequence. Per user note 2026-05-31:
    # ``EM DASH may appear singularly with subsequent text before a
    # FULL STOP or SEMICOLON ... functions similarly to a COLON or
    # introduces an apposition.``
    #
    # The pre-em-dash half parses as ``S``, the post half as one of
    # :data:`_POST_EMDASH_CATEGORIES` — mirroring the colon-split's
    # three appositive shapes (S / N / NP[NOM]). The matrix is glued
    # via the same APP set-membership pattern as the chart-level
    # 9.X.c25 em-dash rule in ``cfg/discourse.py:878``.
    #
    # **Single vs paired discrimination**: paired em-dashes (``X -- Y --
    # Z``) encode parenthetical / apposition where ``Y`` is the
    # insertion in ``X Z`` — a different semantic that this split
    # cannot handle and must defer to a different mechanism. The
    # activation gate :func:`_looks_single_emdash` requires exactly one
    # ``-{2,}`` run in the input; paired patterns fall through to the
    # chart (where the existing em-dash rules also don't handle paired
    # uses — both single and paired cases are unattested or OCR-noise
    # in the audit corpus).
    #
    # **Post-half linker strip**: when the post-em-dash content begins
    # with the relativizer / complementizer ``na`` (PANAHON sent-41's
    # ``-- na ang ibig sabihin ay laging huli``), the bare-S parse of
    # the post-half fails (no chart rule admits ``na + S → S``). The
    # retry strips a leading ``na ``/``Na `` and re-attempts as S —
    # equivalent to treating ``na`` as a soft RC/CP boundary that the
    # em-dash apposition subsumes.
    if _looks_single_emdash(text) and "emdash" not in splits_applied:
        split_result = _try_emdash_split(
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
    # the chart's 9.X.c13 ``S → PP[PREP_TYPE=X] PUNCT[COMMA] S``
    # fronted-PP construction. The pre-comma PP and post-comma
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
    # lex entry advertises a PREP_TYPE that is a key in
    # ``_FRONTED_PP_LEMMA_TYPES`` (``dahil`` / ``dahilan`` → REASON;
    # ``mula`` → SOURCE — see post-7.4) and (2) contain a
    # sentence-internal comma. The pre-comma half is parsed against
    # ``PP[PREP_TYPE=<type>]`` (chart-side feat from the post-2 LHS
    # refactor); the post-comma half against ``S``. If either fails
    # the split is dropped and the chart attempt runs as fallback.
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

    # === Phase 10.J.post-7: fronted-SubordClause-comma split ============
    #
    # Same split-and-glue pattern as post-2's fronted-PP-comma split
    # but with the pre-half parsed as ``SubordClause`` (post-2 was
    # gated to PP[PREP_TYPE=REASON] only). Activates on a broader
    # head set: subordinating conjunctions attested in waves 2/3/5 as
    # sentence-initial with internal comma (``bago``, ``kapag``,
    # ``habang``, ``noong``, ``pagkatapos``, ``mula``, ``kahit``,
    # ``dahil`` — `dahil` shared with post-2; routes by category).
    #
    # Glue mirrors subordination.py's ``S → SubordClause
    # PUNCT[PUNCT_CLASS=COMMA] S`` chart rule (line 187):
    # ``(↑) = ↓3``, ``↓1 ∈ (↑ ADJUNCT)``. Simpler than the PP-comma
    # glue — no TOPIC binding, no ADJ-set membership (SubordClause
    # adjuncts go to a separate ADJUNCT slot per Phase 5l).
    #
    # Audit-attested closures (post-7 audit; multi-wave):
    # - ``Noong minsan, huli ka rin.`` (wave-2 rg-int)
    # - ``Dahil gusto nilang... binibisita, nagsasalita sila...``
    #   (wave-1 PANAHON; `dahil` here is SubordClause-introducing
    #   rather than the canonical PP[REASON] `dahil sa X`)
    # - other 1-hit heads close when both halves parse.
    if "," in text and "fronted_subord_comma" not in splits_applied:
        split_result = _try_fronted_subord_comma_split(
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

    # === Phase 10.J.post-8.5.5.1: lalo-na't post-matrix SubordClause split ===
    #
    # Same split-and-glue pattern as the fronted-SubordClause-comma split
    # (post-7) but for the post-matrix direction — the discourse-emphasis
    # marker ``lalo na 't`` introduces a reason-clause adjunct AFTER the
    # matrix S. Detected by the ``, lalo na 't `` separator in the text.
    #
    # Pre-half parses as ``S`` (the matrix); post-half parses as ``S``
    # (the lalo-na't body). The result is synthesized as
    # ``S → S COMMA SubordClause(lalo na 't S)`` where SubordClause's
    # f-structure shares the post-S's identity (per the chart rule's
    # ``(↑) = ↓4``) overlaid with ``SUBORD_TYPE='REAS'`` and
    # ``EMPHASIS='ESPECIALLY'``; the SubordClause joins the matrix-S's
    # ADJUNCT set.
    #
    # **Motivation** (PAMILYA/sent-14): the chart-level lalo-na't rule
    # (subordination.py) composes with the existing
    # ``S → S COMMA SubordClause`` matrix-attachment rule across many
    # matrix-S forest configurations when the matrix carries internal
    # `at`-coord N (``ang lolo at lola``). The cross-product blows past
    # the 5000-tree iteration cap (sent-16 §6.2 cap-raise forbidden).
    # The pipeline-level split bypasses the cross-product entirely: each
    # half parses against its own chart with the lalo-na't construction
    # accounted for at glue time.
    if (", lalo na't " in text or ", lalo na 't " in text
            or ", lalo na at " in text or ",lalo na't " in text
            or ", lalo na ’t " in text or ", lalo na·t " in text
            or ", lalo na•t " in text):
        if "lalo_nat" not in splits_applied:
            split_result = _try_lalo_nat_split(
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
        reorder_roots=True,
    )

    # Walk candidate trees, collect well-formed ones, then rank.
    # Phase 9.X.c38: ``max_candidates`` early-exits the loop once that
    # many non-blocking parses are accumulated. ``max_tree_iterations``
    # bounds the total number of trees attempted regardless of whether
    # any were accepted (the failsafe for forests dominated by
    # blocking parses, where ``max_candidates`` alone can't escape).
    # Ranking still operates over the bounded pool.
    candidates: list[
        tuple[CNode, FStructure, AStructure, list[Diagnostic], dict[int, int]]
    ] = []
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
        candidates.append(
            (ctree, result.fstructure, a, diagnostics, result.correspondence)
        )
        if max_candidates is not None and len(candidates) >= max_candidates:
            break
    candidates.sort(key=lambda r: _rank_key(r[0]))
    top = candidates[:n_best]

    if top:
        return ParseResult(
            parses=[(ct, fs, a, d) for ct, fs, a, d, _corr in top],
            fragments=[],
            correspondences=[corr for _ct, _fs, _a, _d, corr in top],
        )

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
            correspondence=result.correspondence,
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


# === Phase 10.J.post-12.4: em-dash split helpers =========================

_POST_EMDASH_CATEGORIES: tuple[str, ...] = (
    "S",
    "N",
    "NP[CASE=NOM]",
)


def _looks_single_emdash(text: str) -> bool:
    """Detect a single em-dash boundary (one ``-{2,}`` run, flanked by
    non-empty content on both sides). Returns ``False`` for paired
    em-dashes (``X -- Y -- Z``, parenthetical / apposition — different
    semantic) and for em-dashes at sentence boundaries.
    """
    import re
    runs = list(re.finditer(r"-{2,}", text))
    if len(runs) != 1:
        return False
    m = runs[0]
    pre = text[: m.start()].strip()
    post = text[m.end():].strip()
    return bool(pre) and bool(post)


def _split_on_emdash(text: str) -> tuple[str, str] | None:
    """Find the sole ``--`` (or longer hyphen run) and return
    ``(pre, post)`` with the em-dash itself dropped.

    Returns ``None`` when there isn't exactly one em-dash boundary
    flanked by content. Mirrors :func:`_split_on_colon` for the colon
    split path.
    """
    import re
    m = re.search(r"\s*-{2,}\s*", text)
    if m is None or m.start() == 0 or m.end() == len(text):
        return None
    pre = text[: m.start()].strip()
    post = text[m.end():].strip()
    if not pre or not post:
        return None
    return pre, post


def _strip_post_emdash_linker(text: str) -> str:
    """Strip a leading ``na ``/``Na `` relativizer/complementizer from
    the post-em-dash segment for the bare-S retry path.

    PANAHON/sent-41's post half ``na ang ibig sabihin ay laging huli``
    can't parse as a bare S (no chart rule admits ``PART[LINK=NA] +
    S → S``); stripping the linker yields ``ang ibig sabihin ay laging
    huli`` which is a canonical ay-fronted S. The em-dash apposition
    semantically subsumes the linker — the post-dash content
    elaborates the matrix concept just as a relative clause would.
    """
    s = text.lstrip()
    for prefix in ("na ", "Na "):
        if s.startswith(prefix):
            return s[len(prefix):]
    return text


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
    # Collapse spuriously-ambiguous halves before the cross-product glue
    # (post-9): the appositive glue adds the post-half to a set on the
    # shared pre_fs in place, so gluing one pre-half against N
    # structurally-identical post-halves would leak all N into APP. With
    # each half deduped to its distinct structures, every pre_fs is glued
    # at most once per post and APP carries exactly the real appositive.
    pre_parses = _dedup_glued(pre_parses)

    # Try each post-colon category in order; the first that yields a
    # parse wins. This mirrors the three chart-level colon-appositive
    # variants in cfg/discourse.py — we don't enumerate post-NP and
    # post-S parses, the first success short-circuits.
    post_parses: list[_GluedParse] = []
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
    post_parses = _dedup_glued(post_parses)

    # Synthesize one glued parse per (pre × post) combination, capped
    # at ``n_best``. Both halves must keep passing well-formedness on
    # the glued f-structure or the candidate is dropped.
    glued: list[_GluedParse] = []
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
    return _glued_result(glued)


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
) -> list[_GluedParse]:
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
            # Re-attach each parse's φ correspondence (14.B.7) so an outer
            # glue can compose it. ``correspondences`` aligns 1:1 with
            # ``parses`` (populated by the chart loop and the split
            # detectors); pad defensively if it is short / absent.
            corrs = chained_result.correspondences
            return [
                (ct, fs, a, d, (corrs[i] or {}) if i < len(corrs) else {})
                for i, (ct, fs, a, d) in enumerate(chained_result.parses)
            ]
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
        reorder_roots=True,
        start_symbol=start_symbol,
    )

    candidates: list[_GluedParse] = []
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
        candidates.append(
            (ctree, result.fstructure, a, diagnostics, result.correspondence)
        )
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
    pre_parse: _GluedParse,
    post_parse: _GluedParse,
) -> _GluedParse | None:
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
    pre_ctree, pre_fs, pre_a, pre_diags, pre_corr = pre_parse
    post_ctree, post_fs, _post_a, post_diags, post_corr = post_parse
    # Synthetic colon PUNCT leaf — no equations, syncategorematic in
    # the chart rule too.
    colon_leaf = CNode(
        label="PUNCT[PUNCT_CLASS=COLON]",
        children=[],
        equations=[],
    )
    # Carry the chart-rule equations the synthesis stands in for (post-9),
    # so the inspector's c-node popover shows the appositive's functional
    # structure instead of "No functional equations": the matrix is the
    # pre-half ((↑) = ↓1) with the post-half added to its APP set
    # (↓3 ∈ (↑ APP)). The colon leaf is syncategorematic (no equations).
    matrix_ctree = CNode(
        label="S",
        children=[pre_ctree, colon_leaf, post_ctree],
        equations=["(↑) = ↓1", "↓3 ∈ (↑ APP)"],
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
    # φ (14.B.7): union the halves' c→f maps; the synthetic matrix S and
    # the colon leaf both project to the matrix f-structure (= pre_fs).
    glued_corr = {**pre_corr, **post_corr}
    glued_corr[id(matrix_ctree)] = id(pre_fs)
    glued_corr[id(colon_leaf)] = id(pre_fs)
    return matrix_ctree, pre_fs, pre_a, diagnostics, glued_corr


def _try_emdash_split(
    text: str,
    *,
    n_best: int,
    chart_state_cap: int | None,
    max_candidates: int | None,
    max_tree_iterations: int | None,
    precheck_defining: bool,
    splits_applied: frozenset[str] = frozenset(),
) -> ParseResult | None:
    """Parse the pre-em-dash half as ``S`` and the post half as one of
    :data:`_POST_EMDASH_CATEGORIES`, then synthesize a matrix ``S
    → S PUNCT[DASH] X`` whose APP set carries the post constituent.

    Returns ``None`` when the split isn't applicable, when the
    pre-half doesn't yield an ``S`` parse, or when no post-category
    succeeds (even after the leading ``na``-linker retry). Otherwise
    returns a :class:`ParseResult` with one or more glued parses
    (pre n-best × post categories that succeeded).

    Mirrors :func:`_try_colon_split` end-to-end; the differences are
    (a) em-dash boundary discrimination via :func:`_looks_single_emdash`
    (paired em-dashes deferred), and (b) the leading-``na``-linker retry
    on the post-half (sent-41 ``-- na ang ibig sabihin ...``).
    """
    halves = _split_on_emdash(text)
    if halves is None:
        return None
    pre_text, post_text = halves
    pre_text = _normalize_terminal_punct(pre_text)
    post_text = _normalize_terminal_punct(post_text)

    pre_parses = _parse_segment_as(
        pre_text,
        start_symbol="S",
        n_best=n_best,
        chart_state_cap=chart_state_cap,
        max_candidates=max_candidates,
        max_tree_iterations=max_tree_iterations,
        precheck_defining=precheck_defining,
        splits_applied=splits_applied | frozenset({"emdash"}),
    )
    if not pre_parses:
        return None
    # Collapse spurious duplicates before the in-place APP glue (post-9 —
    # see _try_colon_split / _dedup_glued).
    pre_parses = _dedup_glued(pre_parses)

    # Try the post half against each category in order — first match wins.
    post_parses: list[_GluedParse] = []
    for category in _POST_EMDASH_CATEGORIES:
        post_parses = _parse_segment_as(
            post_text,
            start_symbol=category,
            n_best=n_best,
            chart_state_cap=chart_state_cap,
            max_candidates=max_candidates,
            max_tree_iterations=max_tree_iterations,
            precheck_defining=precheck_defining,
            splits_applied=splits_applied | frozenset({"emdash"}),
        )
        if post_parses:
            break

    # Retry with leading-linker strip if the post-half didn't parse.
    if not post_parses:
        stripped = _strip_post_emdash_linker(post_text)
        if stripped != post_text:
            for category in _POST_EMDASH_CATEGORIES:
                post_parses = _parse_segment_as(
                    stripped,
                    start_symbol=category,
                    n_best=n_best,
                    chart_state_cap=chart_state_cap,
                    max_candidates=max_candidates,
                    max_tree_iterations=max_tree_iterations,
                    precheck_defining=precheck_defining,
                    splits_applied=splits_applied | frozenset({"emdash"}),
                )
                if post_parses:
                    break

    if not post_parses:
        return None
    post_parses = _dedup_glued(post_parses)

    glued: list[_GluedParse] = []
    for pre_parse in pre_parses:
        for post_parse in post_parses:
            g = _glue_emdash_appositive(pre_parse, post_parse)
            if g is not None:
                glued.append(g)
                if len(glued) >= n_best:
                    break
        if len(glued) >= n_best:
            break

    if not glued:
        return None
    return _glued_result(glued)


def _glue_emdash_appositive(
    pre_parse: _GluedParse,
    post_parse: _GluedParse,
) -> _GluedParse | None:
    """Synthesize the matrix ``S → S PUNCT[DASH] X`` parse from two
    independently-parsed halves. Mirrors :func:`_glue_colon_appositive`
    with the punct class set to DASH.

    Returns ``None`` when the synthesized f-structure fails the same
    well-formedness check the chart-level em-dash rule would have run.
    """
    pre_ctree, pre_fs, pre_a, pre_diags, pre_corr = pre_parse
    post_ctree, post_fs, _post_a, post_diags, post_corr = post_parse
    dash_leaf = CNode(
        label="PUNCT[PUNCT_CLASS=DASH]",
        children=[],
        equations=[],
    )
    # Same chart-rule equations as the colon glue (post-9): the matrix is
    # the pre-half ((↑) = ↓1) with the post constituent in its APP set
    # (↓3 ∈ (↑ APP)). The dash leaf is syncategorematic.
    matrix_ctree = CNode(
        label="S",
        children=[pre_ctree, dash_leaf, post_ctree],
        equations=["(↑) = ↓1", "↓3 ∈ (↑ APP)"],
    )
    existing_app = pre_fs.feats.get("APP")
    if existing_app is None:
        new_app: frozenset[FStructure] = frozenset({post_fs})
    elif isinstance(existing_app, frozenset):
        new_app = existing_app | {post_fs}
    else:  # pragma: no cover — APP is set-valued in every grammar path
        return None
    pre_fs.feats["APP"] = new_app
    _lift_in_situ_q_type(pre_fs)
    _, wf_diags = lfg_well_formed(pre_fs, matrix_ctree)
    if any(d.is_blocking() for d in wf_diags):
        if existing_app is None:
            del pre_fs.feats["APP"]
        else:
            pre_fs.feats["APP"] = existing_app
        return None
    diagnostics = list(pre_diags) + list(post_diags) + list(wf_diags)
    # φ (14.B.7): the synthetic matrix S and the dash leaf both project
    # to the matrix f-structure (= pre_fs); union the halves' maps.
    glued_corr = {**pre_corr, **post_corr}
    glued_corr[id(matrix_ctree)] = id(pre_fs)
    glued_corr[id(dash_leaf)] = id(pre_fs)
    return matrix_ctree, pre_fs, pre_a, diagnostics, glued_corr


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
) -> list[_GluedParse] | None:
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
    glued: list[_GluedParse] = []
    for pre_parse in pre_parses:
        for post_parse in post_parses:
            g = _glue_comma_at_np(pre_parse, post_parse, case=case)
            if g is not None:
                glued.append(g)
                if len(glued) >= n_best:
                    break
        if len(glued) >= n_best:
            break
    # Drop spurious duplicates from the conjuncts' cross-product (post-9):
    # each glue builds a fresh matrix f-structure, so structurally-equal
    # coordinations are safe to collapse here — and collapsing them keeps a
    # one-coordination appositive from fanning out into N identical APP
    # members when this result feeds an enclosing colon / em-dash glue.
    return _dedup_glued(glued) or None


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
    pre_parse: _GluedParse,
    post_parse: _GluedParse,
    *,
    case: str,
) -> _GluedParse | None:
    """Synthesize ``NP[CASE=case, COORD=AND] → NP[CASE=case]
    PUNCT[COMMA] PART[COORD=AND] NP[CASE=case]`` from two parsed
    halves. The matrix f-structure is a fresh node (neither
    conjunct IS the matrix — both are CONJUNCTS members) carrying
    ``CASE``, ``COORD='AND'``, and ``NUM='PL'``.

    Returns ``None`` if the synthesized f-structure fails the
    chart-equivalent well-formedness check.
    """
    pre_ctree, pre_fs, _pre_a, pre_diags, pre_corr = pre_parse
    post_ctree, post_fs, post_a, post_diags, post_corr = post_parse
    comma_leaf = CNode(
        label="PUNCT[PUNCT_CLASS=COMMA]", children=[], equations=[],
    )
    # The coordinator carries the COORD value it contributes; the comma is
    # syncategorematic (post-9 — populate the synthetic c-nodes' equations
    # so the inspector popover shows the coordination's functional
    # structure rather than "No functional equations").
    at_leaf = CNode(
        label="PART[COORD=AND]", children=[], equations=["(↑ COORD) = 'AND'"],
    )
    # The matrix is a fresh node carrying CASE / NUM with each conjunct a
    # CONJUNCTS member (children: pre=↓1, comma=↓2, at=↓3, post=↓4).
    matrix_ctree = CNode(
        label=f"NP[CASE={case},COORD=AND]",
        children=[pre_ctree, comma_leaf, at_leaf, post_ctree],
        equations=[
            f"(↑ CASE) = '{case}'",
            "(↑ NUM) = 'PL'",
            "↓1 ∈ (↑ CONJUNCTS)",
            "↓4 ∈ (↑ CONJUNCTS)",
        ],
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
    # φ (14.B.7): both conjuncts keep their own maps; the synthetic coord
    # matrix node, comma, and coordinator all project to the fresh matrix
    # f-structure.
    glued_corr = {**pre_corr, **post_corr}
    for _syn in (matrix_ctree, comma_leaf, at_leaf):
        glued_corr[id(_syn)] = id(matrix_fs)
    return matrix_ctree, matrix_fs, post_a, diagnostics, glued_corr


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
    # Activation: input must start with a known fronted-PP-head lemma.
    # We restrict to attested fronted-PP heads (``dahil``/``dahilan``
    # → REASON; ``mula`` → SOURCE; see ``_FRONTED_PP_LEMMA_TYPES``) —
    # a broader trigger (any PREP head) would over-activate on
    # sentences where the leading PREP isn't actually being fronted
    # (e.g., a clause-internal PP).
    stripped = text.lstrip()
    if not stripped:
        return None
    first_word = stripped.split(None, 1)[0]
    prep_type = _FRONTED_PP_LEMMA_TYPES.get(first_word.casefold())
    if prep_type is None:
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
        start_symbol=f"PP[PREP_TYPE={prep_type}]",
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

    glued: list[_GluedParse] = []
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
    return _glued_result(glued)


# Phase 10.J.post-7.2: ``dahilan`` is the nominal-form variant of
# ``dahil`` — both head REASON-PPs (``dahilan sa ulan``, ``dahil sa
# ulan``) and route through the same fronted-PP-comma split.
#
# Phase 10.J.post-7.4 generalises to a per-lemma → PREP_TYPE mapping
# so the same split-and-glue path handles SOURCE-PPs (``mula sa X``).
# The lemma's PREP_TYPE is used both to gate activation and to choose
# the pre-half start-symbol (``PP[PREP_TYPE=<type>]``). Adding a new
# fronted-PP head means adding one row here plus including the
# PREP_TYPE in the discourse.py c13 ``S → PP[PREP_TYPE=X] PUNCT[COMMA]
# S`` rule loop. Lemma overlap with ``_FRONTED_SUBORD_HEADS`` (e.g.,
# ``mula`` heads both ``mula sa NP`` PPs and ``mula nang S``
# SubordClauses) is benign — the PP-comma split runs first and falls
# through when the pre-half can't parse as a PP.
_FRONTED_PP_LEMMA_TYPES: dict[str, str] = {
    "dahil": "REASON",
    "dahilan": "REASON",
    "mula": "SOURCE",
    "tungo": "GOAL",
    "tungkol": "TOPIC",
}


# === Phase 10.J.post-7: fronted-SubordClause-comma split ===============
#
# Subordinating heads attested in the audit corpus as sentence-initial
# with an internal comma. Each fronts a SubordClause that joins the
# matrix's ADJUNCT set via subordination.py's ``S → SubordClause
# PUNCT[COMMA] S`` rule. ``dahil`` and ``mula`` overlap with
# ``_FRONTED_PP_LEMMA_TYPES`` (post-7.4 generalisation of the
# post-2 ``_REASON_PREP_LEMMAS``) — when the pre-half parses as
# ``PP[PREP_TYPE=X]``, the PP path wins (called first); the
# SubordClause path catches non-PP variants (``dahil + S-clause``
# without ``sa``; ``mula nang + S-clause``).
_FRONTED_SUBORD_HEADS: frozenset[str] = frozenset({
    "dahil",
    "palibhasa",       # Phase 10.J.post-7.1
    "bago", "kapag", "habang", "noong",
    "pagkatapos", "matapos",
    "mula",
    "kahit",
    "kung",
    "samantalang",
})


def _try_fronted_subord_comma_split(
    text: str,
    *,
    n_best: int,
    chart_state_cap: int | None,
    max_candidates: int | None,
    max_tree_iterations: int | None,
    precheck_defining: bool,
    splits_applied: frozenset[str] = frozenset(),
) -> ParseResult | None:
    """If ``text`` looks like ``SUBORD-HEAD ... , S`` (e.g.,
    ``Bago kayo pumasok sa eskuwela, mag-almusal muna kayo.``),
    parse the pre-comma half as ``SubordClause`` and the post-comma
    half as ``S``, then synthesize the matrix ``S → SubordClause
    PUNCT[COMMA] S`` parse mirroring the chart rule in subordination.py.

    Returns ``None`` when the activation pattern doesn't match, when
    either half fails to parse, or when the synthesized f-structure
    fails well-formedness.
    """
    stripped = text.lstrip()
    if not stripped:
        return None
    first_word = stripped.split(None, 1)[0].casefold()
    if first_word not in _FRONTED_SUBORD_HEADS:
        return None
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
        start_symbol="SubordClause",
        n_best=n_best,
        chart_state_cap=chart_state_cap,
        max_candidates=max_candidates,
        max_tree_iterations=max_tree_iterations,
        precheck_defining=precheck_defining,
        splits_applied=splits_applied | frozenset({"fronted_subord_comma"}),
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
        splits_applied=splits_applied | frozenset({"fronted_subord_comma"}),
    )
    if not post_parses:
        return None

    glued: list[_GluedParse] = []
    for pre_parse in pre_parses:
        for post_parse in post_parses:
            g = _glue_fronted_subord_comma(pre_parse, post_parse)
            if g is not None:
                glued.append(g)
                if len(glued) >= n_best:
                    break
        if len(glued) >= n_best:
            break
    if not glued:
        return None
    return _glued_result(glued)


def _glue_fronted_subord_comma(
    pre_parse: _GluedParse,
    post_parse: _GluedParse,
) -> _GluedParse | None:
    """Synthesize ``S → SubordClause PUNCT[COMMA] S`` from two parsed
    halves, mirroring subordination.py's chart rule: ``(↑) = ↓3``,
    ``↓1 ∈ (↑ ADJUNCT)``.

    Simpler than the fronted-PP-comma glue — no TOPIC binding, no
    ADJ-set membership (SubordClause adjuncts use the ADJUNCT slot,
    not the ADJ set).

    Returns ``None`` if the assembled f-structure fails the
    well-formedness check.
    """
    pre_ctree, pre_fs, _pre_a, pre_diags, pre_corr = pre_parse
    post_ctree, post_fs, post_a, post_diags, post_corr = post_parse
    comma_leaf = CNode(
        label="PUNCT[PUNCT_CLASS=COMMA]", children=[], equations=[],
    )
    matrix_ctree = CNode(
        label="S",
        children=[pre_ctree, comma_leaf, post_ctree],
        equations=[],
    )
    # Matrix f-structure shares identity with the post-comma S
    # (chart rule's ``(↑) = ↓3``); add the SubordClause to ADJUNCT.
    existing_adj = post_fs.feats.get("ADJUNCT")
    if existing_adj is None:
        new_adj: frozenset[FStructure] = frozenset({pre_fs})
    elif isinstance(existing_adj, frozenset):
        new_adj = existing_adj | {pre_fs}
    else:  # pragma: no cover — ADJUNCT is set-valued
        return None
    post_fs.feats["ADJUNCT"] = new_adj
    _lift_in_situ_q_type(post_fs)
    _, wf_diags = lfg_well_formed(post_fs, matrix_ctree)
    if any(d.is_blocking() for d in wf_diags):
        # Restore so subsequent candidates don't see our writes.
        if existing_adj is None:
            del post_fs.feats["ADJUNCT"]
        else:
            post_fs.feats["ADJUNCT"] = existing_adj
        return None
    diagnostics = list(pre_diags) + list(post_diags) + list(wf_diags)
    # φ (14.B.7): matrix = post-comma S (= post_fs); the synthetic matrix
    # S and the comma leaf project to it; the SubordClause keeps its map.
    glued_corr = {**pre_corr, **post_corr}
    glued_corr[id(matrix_ctree)] = id(post_fs)
    glued_corr[id(comma_leaf)] = id(post_fs)
    return matrix_ctree, post_fs, post_a, diagnostics, glued_corr


def _glue_fronted_pp_comma(
    pre_parse: _GluedParse,
    post_parse: _GluedParse,
) -> _GluedParse | None:
    """Synthesize ``S → PP[PREP_TYPE=REASON] PUNCT[COMMA] S`` from
    two parsed halves, mirroring the chart-level c13 rule:
    ``(↑) = ↓3``, ``(↑ TOPIC) = ↓1``, ``↓1 ∈ (↑ ADJ)``.

    Returns ``None`` if the assembled f-structure fails the
    well-formedness check the chart rule would have run.
    """
    pre_ctree, pre_fs, _pre_a, pre_diags, pre_corr = pre_parse
    post_ctree, post_fs, post_a, post_diags, post_corr = post_parse
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
    # φ (14.B.7): matrix = post-comma S (= post_fs); the synthetic matrix
    # S and the comma leaf project to it; the fronted PP keeps its map.
    glued_corr = {**pre_corr, **post_corr}
    glued_corr[id(matrix_ctree)] = id(post_fs)
    glued_corr[id(comma_leaf)] = id(post_fs)
    return matrix_ctree, post_fs, post_a, diagnostics, glued_corr


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

    glued: list[_GluedParse] = []
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
    return _glued_result(glued)


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
    pre_parse: _GluedParse,
    post_parse: _GluedParse,
) -> _GluedParse | None:
    """Synthesize ``S → NP[CASE=NOM] PART[LINK=AY] S_GAP`` from
    two parsed halves, mirroring the Phase 4 §7.4 chart rule:
    ``(↑) = ↓3`` (matrix = inner S_GAP),
    ``(↑ TOPIC) = ↓1`` (fronted NP is the topic),
    ``(↓3 REL-PRO) = ↓1`` (REL-PRO bound to fronted NP),
    ``(↓3 REL-PRO) =c (↓3 SUBJ)`` (constraining — gap is SUBJ).

    Returns ``None`` if the synthesized f-structure fails the
    well-formedness check.
    """
    pre_ctree, pre_fs, _pre_a, pre_diags, pre_corr = pre_parse
    post_ctree, post_fs, post_a, post_diags, post_corr = post_parse
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
    # φ (14.B.7): matrix = inner S_GAP (= post_fs); the synthetic matrix
    # S and the ay leaf project to it; the fronted NP keeps its map.
    glued_corr = {**pre_corr, **post_corr}
    glued_corr[id(matrix_ctree)] = id(post_fs)
    glued_corr[id(ay_leaf)] = id(post_fs)
    return matrix_ctree, post_fs, post_a, diagnostics, glued_corr


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


# === Phase 10.J.post-8.5.5.1: lalo-na't post-matrix split ============
#
# Pipeline-level synthesis for ``S, lalo na 't S`` — the discourse-
# emphasis reason-clause adjunct. The matrix ``lalo na 't S`` chart
# rule (subordination.py) composes with ``S → S COMMA SubordClause``
# matrix-attachment across many matrix-S forest configurations
# when the matrix carries internal ``at``-coord N (PAMILYA/sent-14:
# ``ang lolo at lola``). The cross-product overflows the 5000-tree
# iteration cap (sent-16 §6.2 cap-raise forbidden).
#
# This split bypasses the cross-product: pre-comma half parses as
# ``S`` (matrix), post-marker half parses as ``S`` (the lalo-na't
# body), and the result is synthesized as ``S → S COMMA
# SubordClause(lalo na 't S)`` with the SubordClause carrying
# ``SUBORD_TYPE='REAS'`` and ``EMPHASIS='ESPECIALLY'`` overlay on
# the post-S f-structure.


_LALO_NAT_SEPARATORS = (
    ", lalo na't ",
    ", lalo na 't ",
    ", lalo na at ",
    ",lalo na't ",
    ",lalo na 't ",
    ", lalo na ’t ",        # right single quotation mark
    ", lalo na·t ",         # middle dot
    ", lalo na•t ",         # bullet
)


def _try_lalo_nat_split(
    text: str,
    *,
    n_best: int,
    chart_state_cap: int | None,
    max_candidates: int | None,
    max_tree_iterations: int | None,
    precheck_defining: bool,
    splits_applied: frozenset[str] = frozenset(),
) -> ParseResult | None:
    """Split ``S, lalo na 't S`` on the separator and synthesize the
    matrix ``S → S COMMA SubordClause(lalo na 't S)`` parse.

    Returns ``None`` when no separator is found, when either half
    fails to parse, or when the synthesized f-structure fails
    well-formedness.
    """
    sep_idx = -1
    sep_len = 0
    for sep in _LALO_NAT_SEPARATORS:
        idx = text.find(sep)
        if idx >= 0 and (sep_idx < 0 or idx < sep_idx):
            sep_idx = idx
            sep_len = len(sep)
    if sep_idx < 0:
        return None
    pre_text = text[:sep_idx].strip()
    post_text = text[sep_idx + sep_len:].strip()
    if not pre_text or not post_text:
        return None
    pre_text = _normalize_terminal_punct(pre_text)
    post_text = _normalize_terminal_punct(post_text)

    pre_parses = _parse_segment_as(
        pre_text,
        start_symbol="S",
        n_best=n_best,
        chart_state_cap=chart_state_cap,
        max_candidates=max_candidates,
        max_tree_iterations=max_tree_iterations,
        precheck_defining=precheck_defining,
        splits_applied=splits_applied | frozenset({"lalo_nat"}),
    )
    if not pre_parses:
        # Fallback: the pre-half itself may have a bare-comma 2-way
        # SUBJ-coord (PAMILYA/sent-14 shape: ``<pred> ang X, ang Y``
        # where the SUBJ is two ang-NPs separated by a bare comma).
        # Try a deeper SUBJ-bare-comma synthesis before giving up.
        fallback_parses = _try_subj_bare_comma_np_coord(
            pre_text,
            n_best=n_best,
            chart_state_cap=chart_state_cap,
            max_candidates=max_candidates,
            max_tree_iterations=max_tree_iterations,
            precheck_defining=precheck_defining,
            splits_applied=splits_applied | frozenset({"lalo_nat"}),
        )
        if not fallback_parses:
            return None
        pre_parses = fallback_parses
    post_parses = _parse_segment_as(
        post_text,
        start_symbol="S",
        n_best=n_best,
        chart_state_cap=chart_state_cap,
        max_candidates=max_candidates,
        max_tree_iterations=max_tree_iterations,
        precheck_defining=precheck_defining,
        splits_applied=splits_applied | frozenset({"lalo_nat"}),
    )
    if not post_parses:
        return None

    glued: list[_GluedParse] = []
    for pre_parse in pre_parses:
        for post_parse in post_parses:
            g = _glue_lalo_nat(pre_parse, post_parse)
            if g is not None:
                glued.append(g)
                if len(glued) >= n_best:
                    break
        if len(glued) >= n_best:
            break
    if not glued:
        return None
    return _glued_result(glued)


# Right-edge separators between two case-marker-led NPs. Used only by
# ``_try_subj_bare_comma_np_coord`` to detect the bare-comma 2-way
# SUBJ-coord shape in PAMILYA/sent-14's pre-lalo-na't half.
_SUBJ_BARE_COMMA_SEPS = (
    (", ang ", "ang"),
    (", si ", "si"),
    (", sina ", "sina"),
    (", ng ", "ng"),
    (", sa ", "sa"),
    (", ang mga ", "ang"),
    (", si mga ", "si"),
)


def _try_subj_bare_comma_np_coord(
    text: str,
    *,
    n_best: int,
    chart_state_cap: int | None,
    max_candidates: int | None,
    max_tree_iterations: int | None,
    precheck_defining: bool,
    splits_applied: frozenset[str],
) -> list[_GluedParse] | None:
    """Deeper SUBJ-bare-comma synthesis: detect ``<pred-text> <ang-NP1>,
    <ang-NP2>`` and synthesize a matrix S where the SUBJ is a coord-NP
    holding NP1 and NP2 as CONJUNCTS.

    Scope: invoked only by ``_try_lalo_nat_split`` for the pre-half
    when direct S parsing fails. The bare-comma 2-way pattern is not
    attested in waves 1-5 outside the PAMILYA/sent-14 lalo-na't
    context, so we keep this synthesis tightly scoped to that fast
    path rather than generalizing to all S-level parses.

    **Future corpus pressure to watch**: if attested exemplars of
    standalone ``<pred> ang X, ang Y.`` (bare-comma 2-way without
    a following discourse continuation like ``lalo na't``) emerge in
    future audit waves, the decision point is whether to widen this
    function's activation gate (e.g., trigger from a top-level
    pipeline check on ``, ang ``/``, si `` followed by sentence-final
    punctuation) or revisit a chart rule with cleaner gates. The
    standalone shape currently ZPFs by design.

    Strategy: find the rightmost ``, <case-marker> `` separator in the
    text; split into pre (matrix-pred + first NP) and post (second NP);
    parse pre as ``S`` (with a single NP SUBJ) and post as ``NP[CASE=X]``
    where X matches the second NP's case marker; synthesize the matrix
    S by adding the post NP to the pre SUBJ's CONJUNCTS set.

    Returns a list of parses (potentially empty) or ``None`` when no
    separator is found.
    """
    # Find the rightmost separator (so the split picks the last
    # comma-NP boundary, leaving the first NP and its modifiers in
    # the matrix-S pre-half).
    best_idx = -1
    best_sep = ""
    best_case_marker = ""
    for sep, case_marker in _SUBJ_BARE_COMMA_SEPS:
        idx = text.rfind(sep)
        if idx > best_idx:
            best_idx = idx
            best_sep = sep
            best_case_marker = case_marker
    if best_idx < 0 or not best_sep:
        return None
    pre_text = text[:best_idx].strip()
    # Reattach the case marker to the post text (it's part of the
    # separator we found; the start of the second NP includes it).
    post_text = best_sep.lstrip(", ") + text[best_idx + len(best_sep):].strip()
    post_text = post_text.strip()
    if not pre_text or not post_text:
        return None
    pre_text_norm = _normalize_terminal_punct(pre_text)
    post_text_norm = _normalize_terminal_punct(post_text)

    case_map = {
        "ang": "NOM",
        "si": "NOM",
        "sina": "NOM",
        "ng": "GEN",
        "sa": "DAT",
    }
    np_case = case_map.get(best_case_marker, "NOM")

    pre_parses = _parse_segment_as(
        pre_text_norm,
        start_symbol="S",
        n_best=n_best,
        chart_state_cap=chart_state_cap,
        max_candidates=max_candidates,
        max_tree_iterations=max_tree_iterations,
        precheck_defining=precheck_defining,
        splits_applied=splits_applied | frozenset({"subj_bare_comma"}),
    )
    if not pre_parses:
        return None
    post_parses = _parse_segment_as(
        post_text_norm,
        start_symbol=f"NP[CASE={np_case}]",
        n_best=n_best,
        chart_state_cap=chart_state_cap,
        max_candidates=max_candidates,
        max_tree_iterations=max_tree_iterations,
        precheck_defining=precheck_defining,
        splits_applied=splits_applied | frozenset({"subj_bare_comma"}),
    )
    if not post_parses:
        return None

    glued: list[_GluedParse] = []
    for pre_parse in pre_parses:
        for post_parse in post_parses:
            g = _glue_subj_bare_comma(pre_parse, post_parse, case=np_case)
            if g is not None:
                glued.append(g)
                if len(glued) >= n_best:
                    break
        if len(glued) >= n_best:
            break
    return glued or None


def _glue_subj_bare_comma(
    pre_parse: _GluedParse,
    post_parse: _GluedParse,
    *,
    case: str,
) -> _GluedParse | None:
    """Synthesize a matrix S whose SUBJ is a coord-NP holding the
    pre-half's existing SUBJ and the post-half NP as CONJUNCTS.

    The matrix S c-structure shares the pre-half's c-tree with the
    SUBJ NP replaced by a synthetic ``NP[CASE=case, COORD=AND]`` whose
    children are the original SUBJ NP + ``PUNCT[COMMA]`` + the new NP.
    """
    pre_ctree, pre_fs, _pre_a, pre_diags, pre_corr = pre_parse
    post_ctree, post_fs, post_a, post_diags, post_corr = post_parse
    pre_subj = pre_fs.feats.get("SUBJ")
    if pre_subj is None or not isinstance(pre_subj, FStructure):
        return None
    # Build the coord SUBJ f-structure (CONJUNCTS = {pre_subj, post_fs}).
    coord_subj = FStructure(feats={
        "CASE": case,
        "COORD": "AND",
        "NUM": "PL",
        "CONJUNCTS": frozenset({pre_subj, post_fs}),
    })
    # Replace pre_fs.SUBJ with coord_subj. (Don't restore on WF
    # failure — the pre_parse was a candidate snapshot; the caller
    # discards on None return.)
    prev_subj = pre_fs.feats.get("SUBJ")
    pre_fs.feats["SUBJ"] = coord_subj
    # c-structure: replace the SUBJ NP in pre_ctree with a synthetic
    # coord-NP node. We don't bother locating the exact SUBJ position;
    # instead, wrap the post NP at the top level as a sibling. The
    # f-structure carries the canonical analysis; the c-tree's
    # visualization is approximate (downstream consumers read the
    # f-structure).
    comma_leaf = CNode(
        label="PUNCT[PUNCT_CLASS=COMMA]", children=[], equations=[],
    )
    coord_np_ctree = CNode(
        label=f"NP[CASE={case},COORD=AND]",
        children=[pre_ctree, comma_leaf, post_ctree],
        equations=[],
    )
    matrix_ctree = CNode(
        label="S",
        children=[coord_np_ctree],
        equations=[],
    )
    _, wf_diags = lfg_well_formed(pre_fs, matrix_ctree)
    if any(d.is_blocking() for d in wf_diags):
        # Restore SUBJ; subsequent post_parse candidates may glue.
        if prev_subj is None:
            del pre_fs.feats["SUBJ"]
        else:
            pre_fs.feats["SUBJ"] = prev_subj
        return None
    diagnostics = list(pre_diags) + list(post_diags) + list(wf_diags)
    # φ (14.B.7): matrix S → pre_fs; the synthetic coord-NP wrapper and its
    # comma project to the fresh coord SUBJ f-structure. The pre-half's own
    # SUBJ c-node keeps its map to its NP (now the first CONJUNCT).
    glued_corr = {**pre_corr, **post_corr}
    glued_corr[id(matrix_ctree)] = id(pre_fs)
    glued_corr[id(coord_np_ctree)] = id(coord_subj)
    glued_corr[id(comma_leaf)] = id(coord_subj)
    return matrix_ctree, pre_fs, post_a, diagnostics, glued_corr


def _glue_lalo_nat(
    pre_parse: _GluedParse,
    post_parse: _GluedParse,
) -> _GluedParse | None:
    """Synthesize ``S → S COMMA SubordClause(lalo na 't S)`` mirroring
    the chart rules: matrix-attachment ``(↑) = ↓1, ↓3 ∈ (↑ ADJUNCT)``
    + SubordClause builder ``(↑) = ↓4, (↑ SUBORD_TYPE) = 'REAS',
    (↑ EMPHASIS) = 'ESPECIALLY'``.

    Returns ``None`` if the assembled f-structure fails the
    well-formedness check.
    """
    pre_ctree, pre_fs, _pre_a, pre_diags, pre_corr = pre_parse
    post_ctree, post_fs, post_a, post_diags, post_corr = post_parse
    # SubordClause f-structure shares identity with the post-comma S
    # (chart rule's ``(↑) = ↓4``); add the SUBORD_TYPE + EMPHASIS
    # overlay so downstream consumers can distinguish this from a
    # bare reason clause.
    pre_emphasis = post_fs.feats.get("EMPHASIS")
    pre_subord_type = post_fs.feats.get("SUBORD_TYPE")
    post_fs.feats["SUBORD_TYPE"] = "REAS"
    post_fs.feats["EMPHASIS"] = "ESPECIALLY"
    # Matrix f-structure shares identity with the pre-comma S
    # (chart rule's ``(↑) = ↓1``); add the SubordClause f-structure
    # to ADJUNCT (``↓3 ∈ (↑ ADJUNCT)``).
    existing_adj = pre_fs.feats.get("ADJUNCT")
    if existing_adj is None:
        new_adj: frozenset[FStructure] = frozenset({post_fs})
    elif isinstance(existing_adj, frozenset):
        new_adj = existing_adj | {post_fs}
    else:  # pragma: no cover — ADJUNCT is set-valued
        # Restore overlay before returning
        if pre_emphasis is None:
            post_fs.feats.pop("EMPHASIS", None)
        else:
            post_fs.feats["EMPHASIS"] = pre_emphasis
        if pre_subord_type is None:
            post_fs.feats.pop("SUBORD_TYPE", None)
        else:
            post_fs.feats["SUBORD_TYPE"] = pre_subord_type
        return None
    pre_fs.feats["ADJUNCT"] = new_adj
    # c-structure: S → S COMMA SubordClause(lalo na 't S)
    lalo_leaf = CNode(
        label="PART[LEMMA=lalo]", children=[], equations=[],
    )
    na_leaf = CNode(label="PART[LINK=NA]", children=[], equations=[])
    at_leaf = CNode(label="PART[COORD=AND]", children=[], equations=[])
    subord_ctree = CNode(
        label="SubordClause",
        children=[lalo_leaf, na_leaf, at_leaf, post_ctree],
        equations=[],
    )
    comma_leaf = CNode(
        label="PUNCT[PUNCT_CLASS=COMMA]", children=[], equations=[],
    )
    matrix_ctree = CNode(
        label="S",
        children=[pre_ctree, comma_leaf, subord_ctree],
        equations=[],
    )
    _lift_in_situ_q_type(pre_fs)
    _, wf_diags = lfg_well_formed(pre_fs, matrix_ctree)
    if any(d.is_blocking() for d in wf_diags):
        # Restore so subsequent candidates don't see our writes.
        if existing_adj is None:
            del pre_fs.feats["ADJUNCT"]
        else:
            pre_fs.feats["ADJUNCT"] = existing_adj
        if pre_emphasis is None:
            post_fs.feats.pop("EMPHASIS", None)
        else:
            post_fs.feats["EMPHASIS"] = pre_emphasis
        if pre_subord_type is None:
            post_fs.feats.pop("SUBORD_TYPE", None)
        else:
            post_fs.feats["SUBORD_TYPE"] = pre_subord_type
        return None
    diagnostics = list(pre_diags) + list(post_diags) + list(wf_diags)
    # φ (14.B.7): matrix S and its comma → pre_fs; the synthetic
    # SubordClause wrapper and the lalo/na/at leaves → post_fs (the
    # SubordClause f-structure, shared with the post-half S).
    glued_corr = {**pre_corr, **post_corr}
    glued_corr[id(matrix_ctree)] = id(pre_fs)
    glued_corr[id(comma_leaf)] = id(pre_fs)
    for _syn in (subord_ctree, lalo_leaf, na_leaf, at_leaf):
        glued_corr[id(_syn)] = id(post_fs)
    return matrix_ctree, pre_fs, post_a, diagnostics, glued_corr


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
