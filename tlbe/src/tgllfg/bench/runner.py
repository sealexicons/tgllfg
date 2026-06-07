# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Benchmark runner + baseline gate (Phase 13.J).

:func:`run_bench` times the **total** parse (the gate metric) per fixed
input as a median over repeats, plus a *representative* per-stage
breakdown (morph / lex / chart) timed via the public stage functions —
diagnostic, not the exact pipeline path (it omits the fast-path token
splits + the n-best forest walk). The committed :data:`BASELINE_PATH`
holds the reference totals; :func:`compare_to_baseline` flags any input
whose total exceeds baseline x (1 + tolerance).
"""

import json
import statistics
import time
from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import Any

from ..clitics import reorder_clitics
from ..core.lexicon import lookup_lexicon
from ..core.pipeline import parse_text_with_fragments
from ..morph import analyze_tokens
from ..text import tokenize
from .inputs import BENCH_INPUTS

#: Committed perf reference (in-package; ships with the wheel).
BASELINE_PATH = Path(__file__).parent / "baseline.json"

#: Median over this many timed runs (after one warm-up).
REPEATS = 7

#: A per-input total above baseline x (1 + TOLERANCE) is a regression.
TOLERANCE = 0.20

#: Generous absolute ceiling (ms) for the CI-safe pytest smoke — catches a
#: catastrophic hang, not a perf regression (the product target is 200ms;
#: the precise +20% gate is `tgllfg bench --check`, run locally on a
#: consistent machine). 5s leaves ample headroom for loaded/parallel CI.
CEILING_MS = 5000.0


def _median_ms(fn: Callable[[], object], repeats: int) -> float:
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - start) * 1000.0)
    return statistics.median(samples)


def _stage_breakdown(text: str) -> tuple[float, float]:
    """Front-end stage timings (morph, lex) — single run, diagnostic. The
    dominant chart-parse + forest-walk cost is reported as ``build_ms``
    (total - morph - lex) by :func:`run_bench`, since isolating the chart
    from a capped, n-best parse run isn't apples-to-apples."""
    toks = tokenize(text)
    start = time.perf_counter()
    mlist = analyze_tokens(toks)
    morph_ms = (time.perf_counter() - start) * 1000.0

    start = time.perf_counter()
    lookup_lexicon(reorder_clitics(mlist))
    lex_ms = (time.perf_counter() - start) * 1000.0

    return morph_ms, lex_ms


def run_bench(repeats: int = REPEATS) -> dict[str, dict[str, Any]]:
    """Run every fixed input; return per-input total + breakdown + counts."""
    results: dict[str, dict[str, Any]] = {}
    for item in BENCH_INPUTS:
        text = item["text"]
        warm = parse_text_with_fragments(text, n_best=5)  # warm caches
        total_ms = _median_ms(
            partial(parse_text_with_fragments, text, n_best=5), repeats
        )
        morph_ms, lex_ms = _stage_breakdown(text)
        results[item["id"]] = {
            "category": item["category"],
            "tokens": len(text.split()),
            "parses": len(warm.parses),
            "total_ms": round(total_ms, 3),
            "morph_ms": round(morph_ms, 3),
            "lex_ms": round(lex_ms, 3),
            "build_ms": round(max(0.0, total_ms - morph_ms - lex_ms), 3),
        }
    return results


def load_baseline() -> dict[str, dict[str, Any]]:
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


def write_baseline(results: dict[str, dict[str, Any]]) -> Path:
    BASELINE_PATH.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return BASELINE_PATH


def compare_to_baseline(
    current: dict[str, dict[str, Any]],
    baseline: dict[str, dict[str, Any]],
    *,
    tolerance: float = TOLERANCE,
) -> list[tuple[str, float, float]]:
    """Return (id, current_ms, baseline_ms) for inputs over the tolerance."""
    regressions: list[tuple[str, float, float]] = []
    for rid, cur in current.items():
        base = baseline.get(rid)
        if base is None:
            continue
        cur_ms, base_ms = cur["total_ms"], base["total_ms"]
        if cur_ms > base_ms * (1.0 + tolerance):
            regressions.append((rid, cur_ms, base_ms))
    return regressions
