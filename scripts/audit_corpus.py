# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Parallel multi-wave audit over the naturalistic + unattributed corpora.

Replaces the per-sub-PR sequential ``tmp/regen_*.py`` scripts.
Spawns ``N`` worker processes (default: ``min(cpu_count - 1, 11)``)
and distributes per-sentence parse tasks across them. Each worker
lazily imports :func:`tgllfg.core.pipeline.parse_text_with_fragments`
on first call so the parser-load cost is amortised over all the
tasks the worker handles.

Tasks come from these wave files under ``data/tgl/exemplars/``:

- ``wave1-exemplars.jsonl``         (R&G 1981 PANAHON + ANG MANOK)
- ``wave1-rb86-verbs.jsonl``        (Ramos & Bautista 1986 verb forms)
- ``wave2-ramos1971.jsonl``         (Ramos 1971)
- ``wave2-rc1990.jsonl``            (Ramos & Cena 1990)
- ``wave2-rg-intermediate.jsonl``   (R&G Intermediate)
- ``wave3-rg-conversational.jsonl`` (R&G Conversational)
- ``wave3-so1972.jsonl``            (Schachter & Otanes 1972)
- ``wave4-kroeger1991.jsonl``       (Kroeger 1991 — native PDF)
- ``wave5-zamar2023.jsonl``         (Zamar 2023 — native PDF)
- ``unattributed-constructions.jsonl`` (constructed gap-illustrating
  exemplars; the audit's "9th wave" per
  ``feedback_audit_includes_unattributed``)

Output: one parse-results JSONL per wave at
``data/tgl/exemplars/<wave>-parse-results.jsonl`` with the schema
``{source, locator, bucket, text}`` where ``bucket`` is one of
``parse-success-1``, ``parse-success-N``, ``zero-parse-fragment``,
``zero-parse-no-fragment``, ``parse-timeout``, ``parse-error``.
Writes are atomic (``.tmp`` → :func:`os.replace`); a partial run
won't leave half-written files.

Pair with ``tmp/wave_diff_locator.py`` (or
``tmp/wave1_diff.py`` for wave-1 only) to compute closures /
regressions / bucket-only shifts against a saved baseline.

Performance: ~88-90s wall on a 12-core CPU for the full 9-wave +
unattributed audit (~6000 sentences). The sequential equivalent
takes 7-10 minutes — switch to this script for all post-PR audits.

Usage:

    # Full audit (all 10 wave files):
    hatch run python scripts/audit_corpus.py

    # Subset (comma-separated wave ids):
    hatch run python scripts/audit_corpus.py --waves wave1-exemplars,unattributed-constructions

    # Tune worker count (default: min(cpu_count-1, 11)):
    hatch run python scripts/audit_corpus.py --workers 6
"""

import argparse
import json
import multiprocessing as mp
import os
import signal
import sys
import time
from pathlib import Path

EXEMPLARS = Path(__file__).resolve().parents[1] / "data" / "tgl" / "exemplars"

# Canonical 9-wave + unattributed list. Each entry: (wave_id, source_jsonl).
# Order matches the historical sequential audit's reporting order.
WAVE_FILES: list[tuple[str, str]] = [
    ("wave1-exemplars",           "wave1-exemplars.jsonl"),
    ("wave1-rb86-verbs",          "wave1-rb86-verbs.jsonl"),
    ("wave2-ramos1971",           "wave2-ramos1971.jsonl"),
    ("wave2-rc1990",              "wave2-rc1990.jsonl"),
    ("wave2-rg-intermediate",     "wave2-rg-intermediate.jsonl"),
    ("wave3-rg-conversational",   "wave3-rg-conversational.jsonl"),
    ("wave3-so1972",              "wave3-so1972.jsonl"),
    ("wave4-kroeger1991",         "wave4-kroeger1991.jsonl"),
    ("wave5-zamar2023",           "wave5-zamar2023.jsonl"),
    ("unattributed-constructions","unattributed-constructions.jsonl"),
]

# Per-sentence parse timeout (seconds). Phase 10.J.post-7.4 raised the
# limit from 10s to 11s (+10%) to move the §6.2 PANAHON sent-16 timing
# edge away from the parallel-mode threshold. Phase 10.K commit 3
# raises it further from 11s to 12s — under the 11-worker parallel
# audit, PANAHON sent-16 lands at ~8.2s in single-process timing but
# OS scheduling jitter still pushes it past the 11s SIGALRM threshold
# occasionally (1-vs-2 wave-1 timeouts between runs). The +10% bump
# absorbs the jitter without changing the cap on
# ``max_tree_iterations`` (the §6.2 sent-16 hard constraint).
_TIMEOUT_S = 12

# Worker-local parser cache. Lazy-init on first task so the parser is
# loaded once per worker process (not once per task).
_PARSE_FN = None


def _get_parse_fn():
    """Return the cached :func:`parse_text_with_fragments`,
    importing it on first call within this worker process."""
    global _PARSE_FN
    if _PARSE_FN is None:
        # Lazy import keeps the parent process light and ensures each
        # worker incurs the parser-load cost exactly once.
        from tgllfg.core.pipeline import parse_text_with_fragments
        _PARSE_FN = parse_text_with_fragments
    return _PARSE_FN


def _alarm(_s, _f):
    raise TimeoutError()


def _parse_one(args: tuple[str, str, str, str]) -> tuple[str, str, str, str, str]:
    """Parse one sentence in a worker process.

    ``args`` is ``(wave_id, source, locator, text)``. Returns
    ``(wave_id, source, locator, bucket, text)``.
    """
    wave_id, source, locator, text = args
    parse_fn = _get_parse_fn()
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(_TIMEOUT_S)
    try:
        r = parse_fn(text, n_best=2)
        signal.alarm(0)
        if r.parses:
            bucket = (
                "parse-success-1" if len(r.parses) == 1
                else "parse-success-N"
            )
        elif r.fragments:
            bucket = "zero-parse-fragment"
        else:
            bucket = "zero-parse-no-fragment"
    except TimeoutError:
        bucket = "parse-timeout"
        signal.alarm(0)
    except Exception:
        bucket = "parse-error"
        signal.alarm(0)
    return (wave_id, source, locator, bucket, text)


def _load_tasks(
    wave_filter: set[str] | None = None,
) -> list[tuple[str, str, str, str]]:
    """Build the flat task list across all (or filtered) wave files.

    Filters out entries marked ``marked_ungrammatical`` and entries
    with empty / missing text (those don't have anything to parse).
    """
    tasks: list[tuple[str, str, str, str]] = []
    for wave_id, fn in WAVE_FILES:
        if wave_filter is not None and wave_id not in wave_filter:
            continue
        path = EXEMPLARS / fn
        if not path.exists():
            continue
        with path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ex = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ex.get("marked_ungrammatical"):
                    continue
                # Phase 10.J.post-12.15: curator-level skip flag.
                # Ignored exemplars don't count toward wave totals
                # and don't gate as regressions. See
                # ``scripts/harvest_exemplars.py:_IGNORED_EXEMPLARS``
                # for the registry and rationale.
                if ex.get("ignore"):
                    continue
                text = (
                    ex.get("text_normalized")
                    or ex.get("text")
                    or ex.get("text_raw")
                    or ""
                )
                if not text:
                    continue
                source = ex.get("source", "")
                locator = ex.get("locator", "")
                tasks.append((wave_id, source, locator, text))
    return tasks


def _write_results(by_wave: dict[str, list[tuple]]) -> None:
    """Atomically write per-wave parse-results files."""
    for wave_id, records in by_wave.items():
        out = EXEMPLARS / f"{wave_id}-parse-results.jsonl"
        tmp_out = out.with_suffix(out.suffix + ".tmp")
        with tmp_out.open("w") as f:
            for _wid, source, locator, bucket, text in records:
                rec = {
                    "source": source,
                    "locator": locator,
                    "bucket": bucket,
                    "text": text,
                }
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        os.replace(tmp_out, out)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n", 1)[0],
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="worker process count (default: min(cpu_count-1, 11))",
    )
    parser.add_argument(
        "--waves",
        type=str,
        default=None,
        help="comma-separated wave ids to audit (default: all)",
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=8,
        help="Pool.map chunksize (default: 8)",
    )
    args = parser.parse_args()

    n_workers = args.workers
    if n_workers is None:
        n_workers = min(max(mp.cpu_count() - 1, 1), 11)

    wave_filter = (
        set(args.waves.split(",")) if args.waves else None
    )

    tasks = _load_tasks(wave_filter)
    print(
        f"workers={n_workers}  chunksize={args.chunksize}  "
        f"tasks={len(tasks)}",
        flush=True,
    )

    t0 = time.monotonic()
    with mp.Pool(n_workers) as pool:
        results = pool.map(_parse_one, tasks, chunksize=args.chunksize)
    elapsed = time.monotonic() - t0

    by_wave: dict[str, list[tuple]] = {}
    for r in results:
        by_wave.setdefault(r[0], []).append(r)

    _write_results(by_wave)

    # Per-wave summary.
    for wave_id, _fn in WAVE_FILES:
        if wave_id not in by_wave:
            continue
        records = by_wave[wave_id]
        ok = sum(
            1 for r in records if r[3].startswith("parse-success")
        )
        to = sum(1 for r in records if r[3] == "parse-timeout")
        total = len(records)
        pct = 100.0 * ok / total if total else 0.0
        print(
            f"  {wave_id:<32}: {ok:>4}/{total:>4} ({pct:5.2f}%)  "
            f"timeout={to}"
        )

    # Grand total.
    grand_total = sum(len(rs) for rs in by_wave.values())
    grand_ok = sum(
        1
        for rs in by_wave.values()
        for r in rs
        if r[3].startswith("parse-success")
    )
    grand_pct = (
        100.0 * grand_ok / grand_total if grand_total else 0.0
    )
    print(
        f"  {'XWAVE TOTAL':<32}: {grand_ok:>4}/{grand_total:>4} "
        f"({grand_pct:5.2f}%)"
    )
    print(f"  elapsed: {elapsed:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
