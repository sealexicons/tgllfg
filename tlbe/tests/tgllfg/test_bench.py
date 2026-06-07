# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 13.J: the perf benchmark harness works + nothing hangs.

This is a harness smoke, NOT the perf gate — absolute timings vary by
machine/load, so the precise >20%-vs-baseline regression check lives in
`tgllfg bench --check` (run locally on a consistent machine, like the
audit gate). Here we just assert every fixed input still parses and the
harness returns the expected shape, under a generous hang ceiling.
"""

from tgllfg.bench import BENCH_INPUTS, CEILING_MS, run_bench


def test_bench_harness_runs() -> None:
    results = run_bench(repeats=1)
    assert len(results) == len(BENCH_INPUTS)
    for rid, r in results.items():
        assert r["parses"] >= 1, f"{rid} produced no parse"
        assert r["total_ms"] > 0.0
        assert {"morph_ms", "lex_ms", "build_ms"} <= r.keys()
        # Coarse hang smoke (not a perf gate — see `tgllfg bench --check`).
        assert r["total_ms"] < CEILING_MS, (
            f"{rid} {r['total_ms']}ms exceeds the {CEILING_MS}ms hang ceiling"
        )
