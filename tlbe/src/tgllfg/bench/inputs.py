# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Fixed benchmark inputs (Phase 13.J).

A small graded set spanning the cost range — short clause → multi-clause
coordination → relative clause (the LDD case that scales worst). Held
fixed so the committed baseline (`baseline.json`) stays comparable across
commits; the `tgllfg bench --check` gate flags a >20% per-input regression.
"""

#: Each: id (stable key for the baseline), category, and the Tagalog text.
BENCH_INPUTS: list[dict[str, str]] = [
    {"id": "tiny_intransitive", "category": "tiny", "text": "Kumain ang aso."},
    {"id": "short_transitive", "category": "short", "text": "Kumain ang aso ng tinapay."},
    {
        "id": "medium_locative",
        "category": "medium",
        "text": "Binili ng lalaki ang isda sa palengke.",
    },
    {
        "id": "coordination",
        "category": "multiclause",
        "text": "Kumain ang aso at uminom ang pusa.",
    },
    {
        "id": "relative_clause",
        "category": "ldd-rc",
        "text": "Nakita ko ang batang kumakain.",
    },
    {
        "id": "long_ditransitive",
        "category": "long",
        "text": "Ibinigay ng guro sa mga bata ang mga libro.",
    },
    {
        # The short_transitive base + two PPs -> attachment ambiguity, the
        # forest-fan-out stress case (where over-generation regressions
        # surface); gives the deterministic count gate a sensitive signal.
        "id": "deep_pp_attachment",
        "category": "attachment",
        "text": "Kumain ang aso ng tinapay sa bahay sa umaga.",
    },
]
