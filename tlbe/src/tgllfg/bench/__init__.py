# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Parser performance benchmark (Phase 13.J)."""

from .inputs import BENCH_INPUTS
from .runner import (
    BASELINE_PATH,
    CEILING_MS,
    FOREST_SIZE_CAP,
    TOLERANCE,
    compare_counts,
    compare_to_baseline,
    load_baseline,
    run_bench,
    run_counts,
    write_baseline,
)

__all__ = [
    "BASELINE_PATH",
    "BENCH_INPUTS",
    "CEILING_MS",
    "FOREST_SIZE_CAP",
    "TOLERANCE",
    "compare_counts",
    "compare_to_baseline",
    "load_baseline",
    "run_bench",
    "run_counts",
    "write_baseline",
]
