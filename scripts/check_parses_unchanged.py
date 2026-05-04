"""Guard the zero-ranker-diff invariant for the grammar.py refactor.

This is the gate the post-Phase-5f ``feature/refactor-grammar-package``
branch (see ``docs/refactor-grammar-package.md``) uses to prove that
splitting ``src/tgllfg/cfg/grammar.py`` into per-area modules
(``nominal.py`` / ``clause.py`` / ``clitic.py`` /
``negation.py`` / ``extraction.py`` / ``control.py``
/ ``discourse.py``) preserves the ranker's behaviour exactly.

For every sentence in ``tests/tgllfg/data/coverage_corpus.yaml`` the
script captures the **top-1 parse** (after the ranker's sort) as a
deterministic string serialisation:

* ``c`` — :func:`tgllfg.renderers.render_c` of the c-tree.
* ``f`` — :func:`tgllfg.renderers.render_f` of the f-structure
  (JSON form, with reentrancy back-references keyed by the per-parse
  ``FStructure.id`` counter; deterministic when rule firing order is
  preserved).
* ``a`` — :func:`tgllfg.renderers.render_a` of the a-structure.
* ``diagnostics`` — list of ``(kind, message, path, equation,
  cnode_label)`` tuples in the order they accumulated.

Sentences whose ``ParseResult.parses`` is empty (corpus
``expected: fragment`` or ``expected: fail`` entries, or any sentence
that loses its parse) serialise to ``None``.

Usage::

    hatch run python scripts/check_parses_unchanged.py --capture
    hatch run python scripts/check_parses_unchanged.py --check

``--capture`` writes ``tests/tgllfg/data/parses.baseline.pkl`` (commit
that file once, on main, before the per-module extractions begin).
``--check`` recomputes the parses and exits non-zero if any entry
differs from the baseline. The aligned-by-corpus-index layout is
deliberate: three sentences appear twice in ``coverage_corpus.yaml``,
so a dict keyed by text would silently drop duplicates.
"""

from __future__ import annotations

import argparse
import pickle
import sys
from pathlib import Path
from typing import Any

import yaml

from tgllfg.pipeline import parse_text
from tgllfg.renderers import render_a, render_c, render_f

_REPO_ROOT = Path(__file__).resolve().parent.parent
_CORPUS_PATH = _REPO_ROOT / "tests" / "tgllfg" / "data" / "coverage_corpus.yaml"
_BASELINE_PATH = _REPO_ROOT / "tests" / "tgllfg" / "data" / "parses.baseline.pkl"


def _serialize_top(text: str) -> dict[str, Any] | None:
    """Compute the ranker's top-1 parse for ``text`` and return a
    pickle-stable dict of its rendered c-/f-/a-structure plus
    diagnostics. Returns ``None`` when no complete parse exists.
    """
    parses = parse_text(text, n_best=1)
    if not parses:
        return None
    ctree, fstr, astr, diags = parses[0]
    return {
        "c": render_c(ctree),
        "f": render_f(fstr),
        "a": render_a(astr),
        "diagnostics": [
            (d.kind, d.message, d.path, d.equation, d.cnode_label)
            for d in diags
        ],
    }


def _load_corpus() -> list[dict[str, Any]]:
    with _CORPUS_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or []


def _build(corpus: list[dict[str, Any]]) -> list[dict[str, Any] | None]:
    """Run the pipeline over the corpus in order, returning one
    serialised top-1 parse per entry (or ``None`` for non-parse
    entries / parse losses)."""
    return [_serialize_top(entry["text"]) for entry in corpus]


def _capture() -> int:
    corpus = _load_corpus()
    parses = _build(corpus)
    with _BASELINE_PATH.open("wb") as fh:
        pickle.dump(parses, fh)
    rel = _BASELINE_PATH.relative_to(_REPO_ROOT)
    n_total = len(parses)
    n_parsed = sum(1 for p in parses if p is not None)
    print(f"Captured {n_parsed}/{n_total} top-1 parses to {rel}")
    return 0


def _check() -> int:
    if not _BASELINE_PATH.exists():
        print(
            f"ERROR: baseline missing at {_BASELINE_PATH}; "
            f"run with --capture on main first.",
            file=sys.stderr,
        )
        return 2
    with _BASELINE_PATH.open("rb") as fh:
        baseline: list[dict[str, Any] | None] = pickle.load(fh)
    corpus = _load_corpus()
    if len(baseline) != len(corpus):
        print(
            f"ERROR: corpus size changed "
            f"(baseline={len(baseline)}, corpus={len(corpus)}); "
            f"recapture the baseline.",
            file=sys.stderr,
        )
        return 2
    current = _build(corpus)
    diffs: list[int] = [
        i for i, (cur, ref) in enumerate(zip(current, baseline)) if cur != ref
    ]
    if diffs:
        print(
            f"FAIL: {len(diffs)} of {len(corpus)} top-1 parses differ "
            f"from baseline.",
            file=sys.stderr,
        )
        for i in diffs[:10]:
            text = corpus[i]["text"]
            print(f"  - [{i}] {text!r}", file=sys.stderr)
        if len(diffs) > 10:
            print(f"  ... and {len(diffs) - 10} more", file=sys.stderr)
        return 1
    print(f"OK: all {len(corpus)} top-1 parses match baseline.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument(
        "--capture", action="store_true",
        help="Recompute every top-1 parse and overwrite the baseline pickle.",
    )
    g.add_argument(
        "--check", action="store_true",
        help="Compare current top-1 parses against the baseline; exit non-zero on diff.",
    )
    args = p.parse_args(argv)
    return _capture() if args.capture else _check()


if __name__ == "__main__":
    raise SystemExit(main())
