# tgllfg/cfg/compile.py

"""Grammar compilation: category-pattern parsing and rule indexing.

Surface notation
----------------

A category pattern in a rule's LHS or RHS is written as either a bare
identifier (``NP``) or an identifier followed by feature constraints
in square brackets (``NP[CASE=NOM]``, ``V[VOICE=PV,ASPECT=PFV]``).

Compilation
-----------

* ``parse_pattern(s)`` parses a surface string into a
  :class:`CategoryPattern` whose features are sorted by key (so that
  equal patterns hash equally).
* ``compile_grammar(g)`` turns a :class:`tgllfg.cfg.Grammar`
  into a :class:`CompiledGrammar` with rules indexed by LHS category
  for fast Earley prediction.

Matching
--------

The parser asks "does pattern A match pattern B?" in three contexts:

* SCAN — does the rule's RHS expectation match a lex token's pattern?
* PREDICT — does a rule's LHS pattern match a pending RHS expectation?
* COMPLETE — does a completing edge's LHS match a waiting parent's
  RHS expectation?

In all three the relation is *non-conflict*: the categories must be
equal and any feature shared between the two sides must have the
same value. Either side may carry features the other does not — a
rule may be specialised (``NP[CASE=NOM]``) or generic (``NP``), and
a token's analysis is typically richer than the rule's expectation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from tgllfg.core.feats import BINARY_FEATS

from .grammar import Grammar, Rule


@dataclass(frozen=True)
class CategoryPattern:
    """A category with optional feature constraints.

    Features are stored as a tuple of ``(key, value)`` pairs sorted by
    key. Two patterns with the same category and same features
    (regardless of construction order) are equal and hash the same.

    Values are typically ``str`` (for enum feats like ``CASE=NOM``)
    or ``bool`` (for binary feats — ``PART[WH=true]``, the
    ``PART[WH]`` shorthand). Phase 5n.C.4 Commit 8 removed the
    legacy ``YES`` / ``NO`` aliases; binary feats now accept only
    ``true`` / ``false`` or the shorthand form.
    """
    category: str
    features: tuple[tuple[str, str | bool], ...] = ()


_PATTERN_RE = re.compile(
    r"^\s*([A-Za-z][A-Za-z0-9_-]*)\s*(?:\[\s*([^\]]*?)\s*\])?\s*$"
)
_FEATURE_PAIR_RE = re.compile(
    r"^\s*([A-Za-z][A-Za-z0-9_-]*)\s*=\s*([A-Za-z0-9_-]+)\s*$"
)
_FEATURE_SHORTHAND_RE = re.compile(
    r"^\s*([A-Za-z][A-Za-z0-9_-]*)\s*$"
)


def _normalize_value(
    feat: str, value: str, pattern_src: str
) -> str | bool:
    """Translate ``true`` / ``false`` literals on binary feats to
    Python ``bool``. Enum feats keep their literal string value
    (including the legacy ``"YES"`` enum tag on ``INDEF`` / ``PRED``).
    Reject ``=true`` / ``=false`` on enum feats and reject any other
    value on binary feats — Phase 5n.C.4 Commit 8 removed the legacy
    ``YES`` / ``NO`` aliases."""
    if feat in BINARY_FEATS:
        if value == "true":
            return True
        if value == "false":
            return False
        raise ValueError(
            f"`{feat}={value}` in pattern {pattern_src!r}: binary "
            f"feats accept only `true`, `false`, or the `[{feat}]` "
            f"shorthand (see docs/feats-binary-audit.md)"
        )
    if value in {"true", "false"}:
        raise ValueError(
            f"`{feat}={value}` in pattern {pattern_src!r}: bool "
            f"literal not allowed on non-binary feat (see "
            f"docs/feats-binary-audit.md for the binary-feat list)"
        )
    return value


def parse_pattern(s: str) -> CategoryPattern:
    """Parse a category pattern from surface notation.

    Accepts ``NP``, ``NP[CASE=NOM]``, ``V[VOICE=PV,ASPECT=PFV]`` and
    Phase 5n.C.4 syntactic forms:

    * ``PART[WH=true]`` / ``PART[WH=false]`` — Python bool literals
      on binary feats; produces ``("WH", True)`` / ``("WH", False)``.
    * ``PART[WH]`` — shorthand for ``PART[WH=true]``. Permitted only
      when the feat is in ``tgllfg.core.feats.BINARY_FEATS``;
      rejected on enum feats because ``[CASE]`` for ``CASE=NOM`` /
      ``CASE=GEN`` / ... would be ambiguous.

    Whitespace around brackets, equals signs, and commas is
    tolerated. Empty bracket bodies (``NP[]``) and empty input are
    rejected.
    """
    m = _PATTERN_RE.match(s)
    if m is None:
        raise ValueError(f"malformed category pattern: {s!r}")
    category = m.group(1)
    feature_body = m.group(2)
    if feature_body is None:
        return CategoryPattern(category, ())
    if not feature_body.strip():
        raise ValueError(f"empty feature body in pattern: {s!r}")
    feats: list[tuple[str, str | bool]] = []
    for pair_src in feature_body.split(","):
        pm = _FEATURE_PAIR_RE.match(pair_src)
        if pm is not None:
            feat, value = pm.group(1), pm.group(2)
            feats.append((feat, _normalize_value(feat, value, s)))
            continue
        sm = _FEATURE_SHORTHAND_RE.match(pair_src)
        if sm is not None:
            feat = sm.group(1)
            if feat not in BINARY_FEATS:
                raise ValueError(
                    f"shorthand `{feat}` in pattern {s!r}: only "
                    f"permitted on binary feats (see "
                    f"docs/feats-binary-audit.md)"
                )
            feats.append((feat, True))
            continue
        raise ValueError(
            f"malformed feature constraint {pair_src!r} in pattern {s!r}"
        )
    feats.sort(key=lambda kv: kv[0])
    return CategoryPattern(category, tuple(feats))


def matches(expected: CategoryPattern, candidate: CategoryPattern) -> bool:
    """Non-conflict matching: same category and no disagreement on
    any feature shared between the two sides."""
    if expected.category != candidate.category:
        return False
    e = dict(expected.features)
    c = dict(candidate.features)
    for k in e.keys() & c.keys():
        if e[k] != c[k]:
            return False
    return True


def merge_features(
    a: CategoryPattern, b: CategoryPattern
) -> CategoryPattern:
    """Combine two compatible patterns into a single pattern with the
    union of their feature constraints. Caller must have verified
    compatibility via :func:`matches`."""
    assert a.category == b.category
    merged: dict[str, str | bool] = dict(a.features)
    for k, v in b.features:
        merged[k] = v
    return CategoryPattern(
        a.category,
        tuple(sorted(merged.items(), key=lambda kv: kv[0])),
    )


@dataclass(frozen=True)
class CompiledRule:
    """A rule with parsed LHS / RHS patterns and equation strings.

    Equations are kept as raw strings; the unifier parses them
    lazily via :func:`tgllfg.equations.parse_equation` so that
    parse errors surface only on rules that actually appear on
    a successful derivation.
    """
    lhs: CategoryPattern
    rhs: tuple[CategoryPattern, ...]
    equations: tuple[str, ...]


class CompiledGrammar:
    """Indexed view of a grammar suitable for Earley prediction."""

    def __init__(
        self,
        rules: Iterable[CompiledRule],
        start: CategoryPattern = CategoryPattern("S", ()),
    ) -> None:
        self.rules: tuple[CompiledRule, ...] = tuple(rules)
        self.start: CategoryPattern = start
        # Index by LHS category. Feature-level filtering happens at
        # prediction time via `matches`; the category bucket is the
        # cheap discriminator.
        by_cat: dict[str, list[CompiledRule]] = {}
        for r in self.rules:
            by_cat.setdefault(r.lhs.category, []).append(r)
        self._by_lhs_cat: dict[str, tuple[CompiledRule, ...]] = {
            cat: tuple(rs) for cat, rs in by_cat.items()
        }
        # Categories that ever appear as a rule LHS are non-terminals;
        # everything else (V, NOUN, DET, ADP, PART, ...) is treated as
        # a lex preterminal during SCAN.
        self._nonterminal_cats: frozenset[str] = frozenset(self._by_lhs_cat)

    def rules_for(self, expected: CategoryPattern) -> tuple[CompiledRule, ...]:
        """Return rules whose LHS is non-conflict-compatible with the
        given expectation. The empty tuple is returned for unknown
        categories."""
        bucket = self._by_lhs_cat.get(expected.category, ())
        return tuple(r for r in bucket if matches(expected, r.lhs))

    def is_nonterminal(self, pattern: CategoryPattern) -> bool:
        """True iff `pattern.category` is the LHS of some rule."""
        return pattern.category in self._nonterminal_cats


def compile_grammar(
    grammar: Grammar,
    start: CategoryPattern = CategoryPattern("S", ()),
) -> CompiledGrammar:
    """Compile a :class:`tgllfg.grammar.Grammar` to a
    :class:`CompiledGrammar`, parsing every LHS and RHS string and
    indexing rules by LHS category."""
    compiled: list[CompiledRule] = []
    for r in grammar.rules:
        lhs = parse_pattern(r.lhs)
        rhs = tuple(parse_pattern(s) for s in r.rhs)
        compiled.append(CompiledRule(lhs=lhs, rhs=rhs, equations=tuple(r.equations)))
    return CompiledGrammar(compiled, start=start)


def compile_rule(rule: Rule) -> CompiledRule:
    """Compile a single rule. Useful for tests."""
    return CompiledRule(
        lhs=parse_pattern(rule.lhs),
        rhs=tuple(parse_pattern(s) for s in rule.rhs),
        equations=tuple(rule.equations),
    )


__all__ = [
    "CategoryPattern",
    "CompiledRule",
    "CompiledGrammar",
    "compile_grammar",
    "compile_rule",
    "matches",
    "merge_features",
    "parse_pattern",
]
