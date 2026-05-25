# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.F — grammar-compiler dead-bracket lint.

A bracketed RHS daughter ``Cat[feat=val]`` is statically unsatisfiable
(a silently dead rule) when ``Cat`` is neither a lexical preterminal
category nor a category whose rule-LHS supplies the bracketed feat —
because the matcher gates on the candidate's *c-structure category
pattern*, and a derived non-terminal (e.g. ``N`` reached via
``N → NOUN``) carries no lexical feats there (``SEM_CLASS`` / ``Q_TYPE``
/ ... live only in the f-structure). The fix is a constraining equation
on a bare-category daughter, or a wrapper non-terminal (``TimeAdv`` /
``QualityN``).

Guards against re-introduction of the ``N[SEM_CLASS=TIME]`` /
``S[Q_TYPE=YES_NO]`` footgun repaired in 10.F.
"""

import pytest

from tgllfg.cfg import Grammar, Rule
from tgllfg.cfg.compile import compile_grammar, find_unsatisfiable_brackets
from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import _get_default
from tgllfg.parse.earley import _POS_ALIASES


def _lexical_categories() -> frozenset[str]:
    """Categories that lexical tokens scan as = POS tags (after
    ``_POS_ALIASES``) drawn from the loaded morph index. Index buckets
    are ``dict[str, list[MorphAnalysis]]`` (content words) or
    ``dict[str, MorphAnalysis]`` (pronouns) — handle both shapes."""
    idx = _get_default()._index
    pos: set[str] = set()
    for bucket in vars(idx).values():
        if not isinstance(bucket, dict):
            continue
        for v in bucket.values():
            for ma in (v if isinstance(v, list) else [v]):
                p = getattr(ma, "pos", None)
                if isinstance(p, str):
                    pos.add(p)
    return frozenset(_POS_ALIASES.get(p, p) for p in pos)


def test_lexical_categories_cover_core_pos() -> None:
    """Drift guard: the lexicon-derived lexical-category set includes
    the core preterminals. A shrunk set would false-flag live brackets
    in ``test_no_dead_brackets`` — so this localises a derivation
    regression to a clear failure."""
    lc = _lexical_categories()
    assert {"NOUN", "V", "ADJ", "ADV", "PART", "PRON", "DET", "ADP",
            "NUM", "Q"} <= lc, sorted(lc)


def test_no_dead_brackets() -> None:
    """The shipped grammar has no statically-unsatisfiable category
    brackets. Guards the ``N[SEM_CLASS=TIME]`` / ``S[Q_TYPE=YES_NO]``
    footgun repaired in 10.F (and any future re-introduction)."""
    cg = compile_grammar(Grammar.load_default())
    dead = find_unsatisfiable_brackets(cg.rules, _lexical_categories())
    assert not dead, (
        "statically-unsatisfiable (silently dead) category brackets — gate "
        "the feat with a constraining equation or a wrapper non-terminal: "
        + "; ".join(
            f"{d.category}{list(d.features)} (rule for {r.lhs.category})"
            for r, d in dead
        )
    )


def test_compile_grammar_raises_on_dead_bracket() -> None:
    """``compile_grammar(..., lexical_categories=...)`` raises on a dead
    bracket: ``Z[FOO=BAR]`` where ``Z`` is neither a lexical category
    nor a rule LHS supplying ``FOO``."""
    g = Grammar([Rule("S", ["Z[FOO=BAR]"], ["(↑) = ↓1"])])
    with pytest.raises(ValueError, match="unsatisfiable"):
        compile_grammar(g, lexical_categories=frozenset({"NOUN", "V"}))


def test_compile_grammar_accepts_satisfiable_brackets() -> None:
    """The lint passes a bracket on a lexical category (scan path) and
    one whose feat a rule LHS supplies (complete path)."""
    # scan path: ADJ is a lexical category
    g1 = Grammar([Rule("S", ["ADJ[PREDICATIVE]"], ["(↑) = ↓1"])])
    compile_grammar(g1, lexical_categories=frozenset({"ADJ"}))
    # complete path: a rule LHS supplies the bracketed feat
    g2 = Grammar([
        Rule("S", ["Foo[BAR=BAZ]"], ["(↑) = ↓1"]),
        Rule("Foo[BAR=BAZ]", ["ADJ"], ["(↑) = ↓1"]),
    ])
    compile_grammar(g2, lexical_categories=frozenset({"ADJ"}))


# === Repaired dead rules now function (10.F) ===========================


def test_embedded_ba_reported_yes_no_q() -> None:
    """The repaired ``S_INTERROG_COMP → PART[COMP_TYPE=INTERROG] S``
    rule (a), plus the complementizer clitic-domain fix in
    ``_enclosing_anchor_for_clitic``, make the embedded ba-reported
    yes/no-Q parse with the correct reading — some parse's COMP carries
    ``Q_TYPE=YES_NO`` ("I know WHETHER he ate"). Was 0 parses before
    10.F (dead ``S[Q_TYPE=YES_NO]`` bracket + ``ba``/``siya`` hoisted
    across ``kung`` into the matrix cluster)."""
    parses = parse_text("Alam ko kung kumain ba siya.")
    assert len(parses) >= 1
    assert any(
        fs.feats.get("COMP") is not None
        and fs.feats.get("COMP").feats.get("Q_TYPE") == "YES_NO"
        for _ct, fs, _a, _d in parses
    ), "expected an embedded yes/no-Q reading (COMP.Q_TYPE=YES_NO)"


def test_declarative_indirect_q_unaffected() -> None:
    """The declarative indirect-Q (rule (b), bare ``S`` + ``¬(↓2
    Q_TYPE)``) still parses — the complementizer clitic-domain fix
    leaves a clitic-free embedded clause untouched."""
    assert len(parse_text("Alam ko kung kumain siya.")) >= 1


def test_pag_time_na_subordinate_unregressed() -> None:
    """R&G sent-53 (``... pag tanghali na``, the pag-N[TIME]-na
    SubordClause whose ``N[SEM_CLASS=TIME]`` bracket 10.F repaired)
    still parses."""
    assert len(parse_text("Puno na ang mga bus pag tanghali na.")) >= 1
