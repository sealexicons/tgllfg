# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 13.J: perf benchmark harness + the deterministic over-generation gate.

`test_bench_no_forest_size_regression` IS a real gate — forest size is the
post-budget `_iter_cnodes` tree count, which is deterministic and
machine-independent, so it catches parser/grammar over-generation
identically on any host or CI runner. A legitimate grammar change that
grows the forest re-baselines via `tgllfg bench --update`.

Wall-clock timing is *not* gated here (machine-variable); the harness smoke
just asserts every input still parses, under a generous hang ceiling. The
local time warning lives in `tgllfg bench --check`.
"""

from tgllfg.bench import (
    BENCH_INPUTS,
    CEILING_MS,
    compare_counts,
    load_baseline,
    run_bench,
    run_counts,
)


def test_bench_harness_runs() -> None:
    results = run_bench(repeats=1)
    assert len(results) == len(BENCH_INPUTS)
    for rid, r in results.items():
        assert r["parses"] >= 1, f"{rid} produced no parse"
        assert r["total_ms"] > 0.0
        assert {"morph_ms", "lex_ms", "build_ms", "forest_size"} <= r.keys()
        # Coarse hang smoke (not a perf gate — see `tgllfg bench --check`).
        assert r["total_ms"] < CEILING_MS, (
            f"{rid} {r['total_ms']}ms exceeds the {CEILING_MS}ms hang ceiling"
        )


def test_bench_no_forest_size_regression() -> None:
    # Deterministic, machine-independent over-generation gate (the CI gate).
    grown = compare_counts(run_counts(), load_baseline())
    assert not grown, f"forest-size grew vs baseline (over-generation): {grown}"
