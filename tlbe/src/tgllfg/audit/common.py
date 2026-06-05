# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Core logic for the naturalistic-tier corpus audit (Phase 12.F).

Extracted from ``scripts/audit_corpus.py`` so the script shim and the
``tgllfg audit`` CLI subcommand share one implementation. The public
surface is re-exported from :mod:`tgllfg.audit`.

The audit parses every exemplar in the corpus under
``data/tgl/exemplars/`` and classifies each into a parse ``bucket``:

- ``run_audit`` parses the corpus (parallel ``Pool``) into per-wave
  records;
- ``write_results`` persists per-wave ``*-parse-results.jsonl``;
- ``write_baseline`` / ``load_baseline`` handle the compact, text-free
  checked-in baseline artifact;
- ``diff_run`` compares a run against a baseline (regression /
  improvement / shift / new / removed).

Start-method-agnostic: the worker entry (``_parse_one``) is a
module-level function that lazily imports the parser, so it is correct
under both Linux ``fork`` and macOS ``spawn``. ``Pool`` is created only
inside ``run_audit`` (never at import), keeping ``spawn`` re-imports
side-effect free.
"""

import hashlib
import json
import multiprocessing as mp
import os
import signal
import time
from dataclasses import dataclass, field
from pathlib import Path

# Canonical 9-wave + unattributed corpus. Each entry: (wave_id, filename).
# Order matches the historical sequential audit's reporting order.
WAVE_FILES: list[tuple[str, str]] = [
    ("wave1-exemplars", "wave1-exemplars.jsonl"),
    ("wave1-rb86-verbs", "wave1-rb86-verbs.jsonl"),
    ("wave2-ramos1971", "wave2-ramos1971.jsonl"),
    ("wave2-rc1990", "wave2-rc1990.jsonl"),
    ("wave2-rg-intermediate", "wave2-rg-intermediate.jsonl"),
    ("wave3-rg-conversational", "wave3-rg-conversational.jsonl"),
    ("wave3-so1972", "wave3-so1972.jsonl"),
    ("wave4-kroeger1991", "wave4-kroeger1991.jsonl"),
    ("wave5-zamar2023", "wave5-zamar2023.jsonl"),
    ("unattributed-constructions", "unattributed-constructions.jsonl"),
]

# Per-sentence parse timeout (seconds). History (scripts/audit_corpus.py):
# raised 10 -> 11 -> 12 to absorb OS-scheduling jitter on the PANAHON
# sent-16 timing edge under the parallel audit, without changing the
# ``max_tree_iterations`` cap (the sent-16 hard constraint).
TIMEOUT_S = 12

_SUCCESS_PREFIX = "parse-success"

# Record tuple shape shared by run + load: (wave_id, source, locator, bucket, text).
Record = tuple[str, str, str, str, str]


def default_exemplars_dir() -> Path:
    """The exemplar corpus directory.

    Override with ``$TGLLFG_EXEMPLARS_DIR``. The fallback is computed
    relative to this module so it survives the Phase 12.B monorepo
    reorg (``data/`` moves under ``tlbe/`` alongside ``src/``,
    preserving the ``parents[3]`` relationship).
    """
    env = os.environ.get("TGLLFG_EXEMPLARS_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[3] / "data" / "tgl" / "exemplars"


def default_baseline_path() -> Path:
    """The checked-in, text-free audit baseline artifact.

    Override with ``$TGLLFG_AUDIT_BASELINE``.
    """
    env = os.environ.get("TGLLFG_AUDIT_BASELINE")
    if env:
        return Path(env)
    return (
        Path(__file__).resolve().parents[3]
        / "tests"
        / "tgllfg"
        / "data"
        / "audit-baseline.jsonl"
    )


def is_success(bucket: str) -> bool:
    """True if ``bucket`` is a parse-success bucket (1 or N)."""
    return bucket.startswith(_SUCCESS_PREFIX)


def text_fingerprint(text: str) -> str:
    """Short, stable, text-free fingerprint of an exemplar's text.

    Disambiguates exemplars that share a ``(source, locator)`` — locators
    are human-entered and occasionally collide (a harvest typo; e.g.
    Kroeger 1991 ``page-126/ex-25a`` was assigned to two distinct
    examples) — without storing the licensed text in the checked-in
    baseline.
    """
    return hashlib.sha1(
        text.encode("utf-8"), usedforsecurity=False
    ).hexdigest()[:12]


# --- run --------------------------------------------------------------

# Worker-local parser cache. Lazy-init on first task so the parser is
# loaded once per worker process (not once per task), under both fork
# (inherited None, re-imported once) and spawn (fresh import per worker).
_PARSE_FN = None


def _get_parse_fn():
    global _PARSE_FN
    if _PARSE_FN is None:
        from tgllfg.core.pipeline import parse_text_with_fragments

        _PARSE_FN = parse_text_with_fragments
    return _PARSE_FN


def _alarm(_s, _f):
    raise TimeoutError()


def _parse_one(task: tuple[str, str, str, str]) -> Record:
    """Parse one sentence in a worker process.

    ``task`` is ``(wave_id, source, locator, text)``; returns
    ``(wave_id, source, locator, bucket, text)``.
    """
    wave_id, source, locator, text = task
    parse_fn = _get_parse_fn()
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(TIMEOUT_S)
    try:
        r = parse_fn(text, n_best=2)
        signal.alarm(0)
        if r.parses:
            bucket = "parse-success-1" if len(r.parses) == 1 else "parse-success-N"
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


def load_tasks(
    exemplars_dir: Path,
    wave_filter: set[str] | None = None,
) -> list[tuple[str, str, str, str]]:
    """Build the flat ``(wave_id, source, locator, text)`` task list.

    Skips ``marked_ungrammatical`` / ``ignore`` exemplars and entries
    with empty text. Missing wave files are silently skipped.
    """
    tasks: list[tuple[str, str, str, str]] = []
    for wave_id, fn in WAVE_FILES:
        if wave_filter is not None and wave_id not in wave_filter:
            continue
        path = exemplars_dir / fn
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
                if ex.get("marked_ungrammatical") or ex.get("ignore"):
                    continue
                text = (
                    ex.get("text_normalized")
                    or ex.get("text")
                    or ex.get("text_raw")
                    or ""
                )
                if not text:
                    continue
                tasks.append(
                    (wave_id, ex.get("source", ""), ex.get("locator", ""), text)
                )
    return tasks


def default_workers() -> int:
    """Worker count: ``min(cpu_count - 1, 11)``, floored at 1."""
    return min(max(mp.cpu_count() - 1, 1), 11)


@dataclass
class AuditRun:
    """Result of :func:`run_audit`: per-wave records + timing."""

    by_wave: dict[str, list[Record]] = field(default_factory=dict)
    elapsed_s: float = 0.0
    n_workers: int = 1
    n_tasks: int = 0


def run_audit(
    exemplars_dir: Path | None = None,
    waves: list[str] | None = None,
    workers: int | None = None,
    chunksize: int = 8,
) -> AuditRun:
    """Parse the (optionally wave-filtered) corpus into per-wave records.

    With ``workers == 1`` the work runs in-process (no ``Pool``) — the
    constrained-runner / debugging fallback.
    """
    if exemplars_dir is None:
        exemplars_dir = default_exemplars_dir()
    if workers is None:
        workers = default_workers()
    wave_filter = set(waves) if waves else None
    tasks = load_tasks(exemplars_dir, wave_filter)

    t0 = time.monotonic()
    if workers <= 1:
        results = [_parse_one(t) for t in tasks]
    else:
        with mp.Pool(workers) as pool:
            results = pool.map(_parse_one, tasks, chunksize=chunksize)
    elapsed = time.monotonic() - t0

    by_wave: dict[str, list[Record]] = {}
    for r in results:
        by_wave.setdefault(r[0], []).append(r)
    return AuditRun(
        by_wave=by_wave, elapsed_s=elapsed, n_workers=workers, n_tasks=len(tasks)
    )


def write_results(
    by_wave: dict[str, list[Record]],
    exemplars_dir: Path | None = None,
) -> list[Path]:
    """Atomically write per-wave ``<wave>-parse-results.jsonl`` files."""
    if exemplars_dir is None:
        exemplars_dir = default_exemplars_dir()
    written: list[Path] = []
    for wave_id, records in by_wave.items():
        out = exemplars_dir / f"{wave_id}-parse-results.jsonl"
        tmp_out = out.with_suffix(out.suffix + ".tmp")
        with tmp_out.open("w") as f:
            for _wid, source, locator, bucket, text in records:
                f.write(
                    json.dumps(
                        {
                            "source": source,
                            "locator": locator,
                            "bucket": bucket,
                            "text": text,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        os.replace(tmp_out, out)
        written.append(out)
    return written


def load_results_dir(exemplars_dir: Path | None = None) -> dict[str, list[Record]]:
    """Read existing per-wave ``*-parse-results.jsonl`` into ``by_wave``.

    The inverse of :func:`write_results`; lets ``diff`` reuse a prior
    run rather than re-parsing.
    """
    if exemplars_dir is None:
        exemplars_dir = default_exemplars_dir()
    by_wave: dict[str, list[Record]] = {}
    for wave_id, _fn in WAVE_FILES:
        path = exemplars_dir / f"{wave_id}-parse-results.jsonl"
        if not path.exists():
            continue
        records: list[Record] = []
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                records.append(
                    (
                        wave_id,
                        rec.get("source", ""),
                        rec.get("locator", ""),
                        rec["bucket"],
                        rec.get("text", ""),
                    )
                )
        by_wave[wave_id] = records
    return by_wave


# --- baseline + diff --------------------------------------------------


def write_baseline(by_wave: dict[str, list[Record]], path: Path) -> int:
    """Write the compact, text-free baseline.

    Each row is ``{wave, source, locator, text_sha, bucket}`` — the
    licensed exemplar text is reduced to a fingerprint (see
    :func:`text_fingerprint`), so the artifact carries no exemplar text
    and is safe to check in. Returns the row count.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    n = 0
    with tmp.open("w") as f:
        for wave_id, records in by_wave.items():
            for _wid, source, locator, bucket, text in records:
                f.write(
                    json.dumps(
                        {
                            "wave": wave_id,
                            "source": source,
                            "locator": locator,
                            "text_sha": text_fingerprint(text),
                            "bucket": bucket,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                n += 1
    os.replace(tmp, path)
    return n


def load_baseline(
    path: Path,
    waves: set[str] | None = None,
) -> dict[tuple[str, str, str], str]:
    """Load a baseline JSONL into ``{(source, locator, text_sha): bucket}``.

    Keyed on ``text_sha`` as well as ``(source, locator)`` so colliding
    locators (see :func:`text_fingerprint`) stay distinct. ``waves``
    restricts to baseline rows whose ``wave`` is in the set — used by the
    sharded CI gate so a shard diffs only its own waves (otherwise every
    other wave's exemplar reads as REMOVED).
    """
    d: dict[tuple[str, str, str], str] = {}
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if waves is not None and rec.get("wave") not in waves:
                continue
            key = (
                rec.get("source", ""),
                rec.get("locator", ""),
                rec.get("text_sha", ""),
            )
            d[key] = rec["bucket"]
    return d


def classify_change(b1: str, b2: str) -> str:
    """Classify a baseline→current bucket transition for one exemplar."""
    p1, p2 = is_success(b1), is_success(b2)
    if p1 and not p2:
        return "REGRESSION"
    if not p1 and p2:
        return "IMPROVEMENT"
    if p1 and p2 and b1 != b2:
        return f"SHIFT-{b1}->{b2}"
    if not p1 and not p2 and b1 != b2:
        return f"ZPF-SHIFT-{b1}->{b2}"
    return "SAME"


@dataclass
class DiffEntry:
    """One exemplar's change between baseline and current run."""

    source: str
    locator: str
    before: str
    after: str
    text: str = ""


@dataclass
class AuditDiff:
    """Bucket-level diff of a run against a baseline."""

    regressions: list[DiffEntry] = field(default_factory=list)
    improvements: list[DiffEntry] = field(default_factory=list)
    shifts: list[DiffEntry] = field(default_factory=list)
    new: list[DiffEntry] = field(default_factory=list)
    removed: list[DiffEntry] = field(default_factory=list)

    @property
    def has_regressions(self) -> bool:
        return bool(self.regressions)


def diff_run(
    baseline: dict[tuple[str, str, str], str],
    by_wave: dict[str, list[Record]],
) -> AuditDiff:
    """Diff a current run against a baseline, keyed on ``(source, locator, text_sha)``.

    REGRESSION = success→zero; IMPROVEMENT = zero→success; SHIFT =
    success→success (different bucket); ZPF-SHIFT = zero→zero
    (different); NEW = present in run, absent from baseline; REMOVED =
    present in baseline, absent from run. Including the text fingerprint
    in the key keeps colliding locators distinct and treats an edited
    exemplar (text changed) as removed+new rather than a silent shift.
    """
    diff = AuditDiff()
    seen: set[tuple[str, str, str]] = set()
    for records in by_wave.values():
        for _wid, source, locator, bucket, text in records:
            key = (source, locator, text_fingerprint(text))
            seen.add(key)
            if key not in baseline:
                diff.new.append(DiffEntry(source, locator, "", bucket, text))
                continue
            change = classify_change(baseline[key], bucket)
            entry = DiffEntry(source, locator, baseline[key], bucket, text)
            if change == "REGRESSION":
                diff.regressions.append(entry)
            elif change == "IMPROVEMENT":
                diff.improvements.append(entry)
            elif change.startswith("SHIFT-") or change.startswith("ZPF-SHIFT-"):
                diff.shifts.append(entry)
    for key, b1 in baseline.items():
        if key not in seen:
            diff.removed.append(DiffEntry(key[0], key[1], b1, "", ""))
    return diff


# --- formatting -------------------------------------------------------


def wave_summary(
    by_wave: dict[str, list[Record]],
) -> list[tuple[str, int, int, int]]:
    """Per-wave ``(wave_id, ok, total, timeouts)`` in canonical order."""
    rows: list[tuple[str, int, int, int]] = []
    for wave_id, _fn in WAVE_FILES:
        if wave_id not in by_wave:
            continue
        records = by_wave[wave_id]
        ok = sum(1 for r in records if is_success(r[3]))
        timeouts = sum(1 for r in records if r[3] == "parse-timeout")
        rows.append((wave_id, ok, len(records), timeouts))
    return rows


def format_summary(run: AuditRun) -> str:
    """Human per-wave + grand-total summary of a run."""
    lines = [f"workers={run.n_workers}  tasks={run.n_tasks}"]
    grand_ok = 0
    grand_total = 0
    for wave_id, ok, total, timeouts in wave_summary(run.by_wave):
        pct = 100.0 * ok / total if total else 0.0
        lines.append(
            f"  {wave_id:<32}: {ok:>4}/{total:>4} ({pct:5.2f}%)  timeout={timeouts}"
        )
        grand_ok += ok
        grand_total += total
    gpct = 100.0 * grand_ok / grand_total if grand_total else 0.0
    lines.append(
        f"  {'XWAVE TOTAL':<32}: {grand_ok:>4}/{grand_total:>4} ({gpct:5.2f}%)"
    )
    lines.append(f"  elapsed: {run.elapsed_s:.1f}s")
    return "\n".join(lines)


def format_diff(diff: AuditDiff, examples: int = 5) -> str:
    """Human summary of a diff (counts + a few example transitions)."""
    lines = [
        f"REGRESSIONS={len(diff.regressions)}  "
        f"IMPROVEMENTS={len(diff.improvements)}  "
        f"SHIFTS={len(diff.shifts)}  NEW={len(diff.new)}  "
        f"REMOVED={len(diff.removed)}"
    ]
    for label, entries in (
        ("REGR", diff.regressions),
        ("IMP", diff.improvements),
    ):
        for e in entries[:examples]:
            lines.append(
                f"  {label} {e.locator}: {e.before} -> {e.after}: {e.text[:100]!r}"
            )
        if len(entries) > examples:
            lines.append(f"  ... +{len(entries) - examples} more {label}")
    for e in diff.shifts[:examples]:
        lines.append(
            f"  SHIFT {e.locator}: {e.before} -> {e.after}: {e.text[:80]!r}"
        )
    if len(diff.shifts) > examples:
        lines.append(f"  ... +{len(diff.shifts) - examples} more SHIFT")
    return "\n".join(lines)
