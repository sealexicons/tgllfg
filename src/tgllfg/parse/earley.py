# tgllfg/earley.py

"""Earley chart parser with LFG-annotated rules.

Algorithm
---------

Standard Earley over ``n+1`` chart columns (where ``n`` is the input
length after stripping non-content tokens). The parser drives an
agenda of (column, state) pairs through three operations:

* **PREDICT** — when a state's dot is before a non-terminal, add an
  ``(rule, dot=0, start=col)`` state for every grammar rule whose
  LHS matches the expected category. PREDICT also runs a
  retroactive COMPLETE: if some completed state with a compatible
  LHS already lives in the chart starting at this column, advance
  the new state immediately. This keeps the algorithm correct in
  the presence of unary chains and would extend to ε-rules too.

* **SCAN** — when the dot is before a terminal/preterminal, look up
  the lexical analyses for the current input position; for every
  ``(MorphAnalysis, LexicalEntry?)`` pair whose category pattern
  matches the rule's expectation, advance the state to the next
  column. Lex equations are derived from the analysis and entry by
  :func:`_lex_equations`.

* **COMPLETE** — when a state's dot is at the end of its RHS, find
  every state in the start column waiting for a category compatible
  with this state's LHS, and advance each one. Each advance records
  a backpointer ``(completion, predecessor)`` so the packed forest
  can be enumerated later.

Packed forest
-------------

Each state carries a list of ``(completion, predecessor)`` pairs
recording the *most recent* advance that produced it. Tree
extraction walks the graph backwards: at each state, pick one
advance, recurse into the predecessor for the prefix history,
recurse into the completion for the sub-derivation. Multiple
advances at one state encode local ambiguity; the first advance is
visited first by ``best_k``, giving deterministic output that
matches the order rules were added to the grammar.
"""

from __future__ import annotations

import itertools
from collections import deque
from dataclasses import dataclass, field
from typing import Iterator

from ..cfg import (
    CategoryPattern,
    CompiledGrammar,
    CompiledRule,
    Grammar,
    compile_grammar,
    matches,
)
from ..common import CNode, LexicalEntry, MorphAnalysis


# Treat morph POS tag VERB as the grammar category V; nothing else
# currently differs.
_POS_ALIASES: dict[str, str] = {"VERB": "V"}


@dataclass(frozen=True)
class LeafCompletion:
    """A scanned token at a chart column. ``category`` is the lex
    pattern (full features); the c-tree label uses just
    ``category.category``. Equations are the LFG annotations
    contributed by the morph analysis and the lexical entry."""
    surface: str
    category: CategoryPattern
    equations: tuple[str, ...]
    span: tuple[int, int]


@dataclass
class StateInfo:
    """An Earley state plus its packed-forest backpointers."""
    rule: CompiledRule
    dot: int
    start: int
    end: int
    # Each advance is (completion that filled rhs[dot-1], predecessor).
    # For predicted states (dot=0) the list is empty.
    advances: list[tuple["Completion", "StateInfo | None"]] = field(default_factory=list)


type Completion = LeafCompletion | StateInfo


class PackedForest:
    """A view over completed start-symbol states. ``best_k(k)`` walks
    the forest deterministically, optionally truncated by the size
    cap configured at parse time.

    Phase 4 §7.9 also exposes the underlying chart (``chart``) so the
    pipeline can extract fragments — the largest non-root completed
    states — when full-sentence parsing fails.
    """

    def __init__(
        self,
        roots: list[StateInfo],
        *,
        size_cap: int | None = None,
        chart: list[dict[tuple[int, int, int], StateInfo]] | None = None,
        sentence_length: int = 0,
    ) -> None:
        self.roots: list[StateInfo] = list(roots)
        self.size_cap: int | None = size_cap
        self.chart: tuple[dict[tuple[int, int, int], StateInfo], ...] = (
            tuple(chart) if chart is not None else ()
        )
        self.sentence_length: int = sentence_length

    def best_k(self, k: int) -> list[CNode]:
        out: list[CNode] = []
        for cn in self.iter_trees():
            if len(out) >= k:
                break
            out.append(cn)
        return out

    def iter_trees(self) -> Iterator[CNode]:
        emitted = 0
        for root in self.roots:
            for cnode in _iter_cnodes(root):
                if self.size_cap is not None and emitted >= self.size_cap:
                    return
                yield cnode
                emitted += 1

    def __len__(self) -> int:
        # Counts trees, not states. Use sparingly on large forests.
        return sum(1 for _ in self.iter_trees())

    @property
    def trees(self) -> list[CNode]:
        return list(self.iter_trees())

    def iter_fragments(self) -> Iterator[tuple[tuple[int, int], CNode]]:
        """Yield ``(span, cnode)`` for every non-root completed state
        in the chart, ranked by decreasing span size. Phase 4 §7.9
        fragment extraction: when no full-sentence parse exists, the
        pipeline emits the largest sub-spans the parser was able to
        complete, with their partial f-structures, for diagnostic
        debugging."""
        n = self.sentence_length
        seen: set[tuple[str, int, int]] = set()
        # Collect completed states across all columns. A "completed"
        # state has dot at end-of-RHS. We rank by span size.
        candidates: list[StateInfo] = []
        for col_chart in self.chart:
            for state in col_chart.values():
                if state.dot != len(state.rule.rhs):
                    continue
                span_len = state.end - state.start
                # Skip states that span the whole sentence (those
                # would be roots; they're already in ``roots`` if
                # they passed the start-symbol filter, otherwise
                # they're not interesting fragments).
                if state.start == 0 and state.end == n:
                    continue
                if span_len <= 0:
                    continue
                candidates.append(state)
        # Sort: largest span first; break ties on start column.
        candidates.sort(
            key=lambda s: (-(s.end - s.start), s.start, s.rule.lhs.category),
        )
        for state in candidates:
            key = (state.rule.lhs.category, state.start, state.end)
            if key in seen:
                continue
            seen.add(key)
            for cnode in _iter_cnodes(state):
                yield (state.start, state.end), cnode
                # One CNode per (label, span) is enough for fragment
                # debugging; more would dilute the signal.
                break


def parse_with_annotations(
    sentence_lex: list[list[tuple[MorphAnalysis, LexicalEntry | None]]],
    grammar: Grammar | CompiledGrammar,
    *,
    forest_size_cap: int | None = None,
) -> PackedForest:
    """Parse the input lexical lattice against the grammar, returning a
    packed forest of c-tree derivations."""
    cg = grammar if isinstance(grammar, CompiledGrammar) else compile_grammar(grammar)
    content = _strip_non_content(sentence_lex)
    return _Earley(content, cg, forest_size_cap=forest_size_cap).run()


# === Internal: Earley state machine =======================================

class _Earley:
    def __init__(
        self,
        tokens: list[list[tuple[MorphAnalysis, LexicalEntry | None]]],
        grammar: CompiledGrammar,
        *,
        forest_size_cap: int | None,
    ) -> None:
        self.tokens = tokens
        self.grammar = grammar
        self.cap = forest_size_cap
        n = len(tokens)
        self._chart: list[dict[tuple[int, int, int], StateInfo]] = [
            {} for _ in range(n + 1)
        ]
        self._agenda: deque[tuple[int, StateInfo]] = deque()
        # Index completed states for retroactive COMPLETE during PREDICT.
        self._completed_by_start: dict[tuple[str, int], list[StateInfo]] = {}

    def run(self) -> PackedForest:
        # Seed: every rule with an LHS compatible with the start symbol.
        for r in self.grammar.rules_for(self.grammar.start):
            self._add(0, StateInfo(rule=r, dot=0, start=0, end=0, advances=[]))
        while self._agenda:
            col, state = self._agenda.popleft()
            self._step(col, state)
        n = len(self.tokens)
        roots: list[StateInfo] = []
        for state in self._chart[n].values():
            if (
                state.start == 0
                and state.dot == len(state.rule.rhs)
                and matches(self.grammar.start, state.rule.lhs)
            ):
                roots.append(state)
        return PackedForest(
            roots,
            size_cap=self.cap,
            chart=self._chart,
            sentence_length=n,
        )

    def _step(self, col: int, state: StateInfo) -> None:
        if state.dot < len(state.rule.rhs):
            expected = state.rule.rhs[state.dot]
            if self.grammar.is_nonterminal(expected):
                self._predict(col, expected)
                # Retroactive complete: a fitting completion may already exist.
                for done in self._completed_by_start.get(
                    (expected.category, col), []
                ):
                    if matches(expected, done.rule.lhs):
                        self._advance(state, done, done.end)
            else:
                self._scan(col, state, expected)
        else:
            self._complete(state)

    def _predict(self, col: int, expected: CategoryPattern) -> None:
        for r in self.grammar.rules_for(expected):
            self._add(
                col,
                StateInfo(rule=r, dot=0, start=col, end=col, advances=[]),
            )

    def _scan(
        self,
        col: int,
        state: StateInfo,
        expected: CategoryPattern,
    ) -> None:
        if col >= len(self.tokens):
            return
        for ma, le in self.tokens[col]:
            lex_pat = _ma_to_pattern(ma)
            if not matches(expected, lex_pat):
                continue
            leaf = LeafCompletion(
                surface=ma.lemma,
                category=lex_pat,
                equations=_lex_equations(ma, le),
                span=(col, col + 1),
            )
            self._advance(state, leaf, col + 1)

    def _complete(self, state: StateInfo) -> None:
        # Index for retroactive completion
        key = (state.rule.lhs.category, state.start)
        self._completed_by_start.setdefault(key, []).append(state)
        # Find waiting parents
        for waiter in list(self._chart[state.start].values()):
            if waiter.dot >= len(waiter.rule.rhs):
                continue
            expected = waiter.rule.rhs[waiter.dot]
            if matches(expected, state.rule.lhs):
                self._advance(waiter, state, state.end)

    def _advance(
        self,
        src: StateInfo,
        completion: Completion,
        new_col: int,
    ) -> None:
        new_state = StateInfo(
            rule=src.rule,
            dot=src.dot + 1,
            start=src.start,
            end=new_col,
            advances=[(completion, src)],
        )
        existing = self._add(new_col, new_state)
        if existing is not new_state:
            # Merge advances; deduplicate by (completion, predecessor identity).
            for adv in new_state.advances:
                if not any(
                    a[0] == adv[0] and a[1] is adv[1] for a in existing.advances
                ):
                    existing.advances.append(adv)

    def _add(self, col: int, state: StateInfo) -> StateInfo:
        key = (id(state.rule), state.dot, state.start)
        chart_col = self._chart[col]
        if key in chart_col:
            return chart_col[key]
        chart_col[key] = state
        self._agenda.append((col, state))
        return state


# === Tree extraction ======================================================

def _iter_histories(state: StateInfo) -> Iterator[tuple[Completion, ...]]:
    """Yield every tuple of completions of length ``state.dot``
    consistent with the recorded advances."""
    if state.dot == 0:
        yield ()
        return
    for completion, pred in state.advances:
        assert pred is not None
        for prefix in _iter_histories(pred):
            yield prefix + (completion,)


def _iter_cnodes(state: StateInfo) -> Iterator[CNode]:
    """Yield every CNode for ``state``, expanding sub-history
    alternatives at every nonterminal slot. This propagates lex
    ambiguity (e.g. AV-intransitive vs AV-transitive entries for
    ``kumain``) outwards through nested rule completions, where the
    earlier first-sub-history shortcut would have collapsed it."""
    for hist in _iter_histories(state):
        slot_options: list[list[CNode]] = []
        for c in hist:
            if isinstance(c, LeafCompletion):
                slot_options.append([
                    CNode(
                        label=c.category.category,
                        children=[],
                        equations=list(c.equations),
                    )
                ])
            else:
                slot_options.append(list(_iter_cnodes(c)))
        if not slot_options:
            yield CNode(
                label=_format_pattern(state.rule.lhs),
                children=[],
                equations=list(state.rule.equations),
            )
            continue
        for combo in itertools.product(*slot_options):
            yield CNode(
                label=_format_pattern(state.rule.lhs),
                children=list(combo),
                equations=list(state.rule.equations),
            )


# === Lexical interface ====================================================

def _strip_non_content(
    sentence_lex: list[list[tuple[MorphAnalysis, LexicalEntry | None]]],
) -> list[list[tuple[MorphAnalysis, LexicalEntry | None]]]:
    """Remove tokens whose only analysis is the fallback POS ``'_UNK'``.

    Punctuation, unknown words, and other orthographic noise pass
    through morphology as ``_UNK``; the parser ignores them. Tokens
    with at least one non-_UNK analysis stay (with all analyses kept,
    including any _UNK) so ambiguity is preserved."""
    keep: list[list[tuple[MorphAnalysis, LexicalEntry | None]]] = []
    for cands in sentence_lex:
        if any(ma.pos != "_UNK" for ma, _ in cands):
            keep.append(cands)
    return keep


def _ma_to_pattern(ma: MorphAnalysis) -> CategoryPattern:
    cat = _POS_ALIASES.get(ma.pos, ma.pos)
    feats: list[tuple[str, str]] = []
    for k, v in ma.feats.items():
        if isinstance(v, str):
            feats.append((k, v))
    feats.sort(key=lambda kv: kv[0])
    return CategoryPattern(cat, tuple(feats))


def _lex_equations(
    ma: MorphAnalysis, le: LexicalEntry | None
) -> tuple[str, ...]:
    """Derive the LFG equations contributed by a lex token."""
    eqs: list[str] = []
    for k, v in ma.feats.items():
        if isinstance(v, str):
            eqs.append(f"(↑ {k}) = '{v}'")
    if le is not None:
        eqs.append(f"(↑ PRED) = '{le.pred}'")
        if le.a_structure:
            eqs.append(
                f"(↑ LEX-ASTRUCT) = '{','.join(le.a_structure)}'"
            )
    return tuple(eqs)


def _format_pattern(p: CategoryPattern) -> str:
    if not p.features:
        return p.category
    body = ",".join(f"{k}={v}" for k, v in p.features)
    return f"{p.category}[{body}]"


__all__ = [
    "PackedForest",
    "LeafCompletion",
    "StateInfo",
    "parse_with_annotations",
]
