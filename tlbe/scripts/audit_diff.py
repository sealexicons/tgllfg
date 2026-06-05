# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Closures / regressions / bucket-only diff for parse-results JSONLs.

Companions :mod:`scripts.audit_corpus`. Where ``audit_corpus.py`` runs
the parser across the corpus and writes per-wave parse-results JSONLs,
this script compares two such snapshots — a saved baseline (pre)
against the current tip (post) — and reports:

* **Closures** — entries that flipped from a ``zero-parse-*`` or
  ``parse-timeout`` bucket to a ``parse-success-*`` bucket.
* **Regressions** — entries that flipped the other way (a parse
  was lost; usually means a code change broke something).
* **Bucket-only changes** — same success/failure status, but the
  bucket label changed (e.g., ``parse-success-1`` →
  ``parse-success-N`` because the new chart rule added ambiguity).

Two invocation modes:

1. **Single file pair** (replaces ``tmp/wave1_diff.py``):

       hatch run python scripts/audit_diff.py PRE_FILE POST_FILE

2. **Multi-wave directory pair** (replaces the loop wrapper around
   ``tmp/wave_diff_locator.py``):

       hatch run python scripts/audit_diff.py \\
           --baseline-dir tmp/pre_<sub-pr>/ \\
           --current-dir data/tgl/exemplars/

   The directory mode iterates over the canonical 9-wave +
   unattributed file list (matching ``audit_corpus.py``'s
   ``WAVE_FILES``) and emits a per-wave diff followed by a grand-total
   summary.

Key matching: ``locator`` only (not ``source/locator``), so older
snapshots that lack a ``source`` field still match current snapshots
that include it. Both schemas are accepted.

Exit status: ``0`` if no regressions, ``1`` if regressions found.
Useful as a pre-merge gate.
"""

import argparse
import json
import sys
from pathlib import Path

WAVE_FILES: list[str] = [
    "wave1-exemplars",
    "wave1-rb86-verbs",
    "wave2-ramos1971",
    "wave2-rc1990",
    "wave2-rg-intermediate",
    "wave3-rg-conversational",
    "wave3-so1972",
    "wave4-kroeger1991",
    "wave5-zamar2023",
    "unattributed-constructions",
]


def _load(path: Path) -> dict[str, dict]:
    """Load a parse-results JSONL into a ``{locator: record}`` map."""
    out: dict[str, dict] = {}
    if not path.exists():
        return out
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            key = r.get("locator", "")
            if key:
                out[key] = r
    return out


def _is_success(r: dict) -> bool:
    return (r.get("bucket") or "").startswith("parse-success")


def _diff_one(
    pre: dict[str, dict],
    post: dict[str, dict],
    *,
    label: str,
    max_examples: int = 20,
) -> tuple[int, int, int]:
    """Print the diff for a single (pre, post) pair.

    Returns ``(n_closures, n_regressions, n_bucket_only)``.
    """
    common = sorted(set(pre) & set(post))
    only_pre = sorted(set(pre) - set(post))
    only_post = sorted(set(post) - set(pre))

    closures = []
    regressions = []
    bucket_only = []
    for k in common:
        a, b = pre[k], post[k]
        a_ok, b_ok = _is_success(a), _is_success(b)
        a_b = a.get("bucket", "")
        b_b = b.get("bucket", "")
        if a_ok != b_ok:
            if b_ok:
                closures.append((k, a_b, b_b, b.get("text", "")))
            else:
                regressions.append((k, a_b, b_b, b.get("text", "")))
        elif a_b != b_b:
            bucket_only.append((k, a_b, b_b, b.get("text", "")))

    pre_succ = sum(1 for r in pre.values() if _is_success(r))
    post_succ = sum(1 for r in post.values() if _is_success(r))

    print(f"=== {label} ===")
    print(
        f"  overlap: {len(common)}  only_pre: {len(only_pre)}  "
        f"only_post: {len(only_post)}"
    )
    print(f"  Closures: {len(closures)}")
    for k, pb, psb, txt in closures[:max_examples]:
        print(f"    + {k}  [{pb} → {psb}]  {txt[:80]}")
    if len(closures) > max_examples:
        print(f"    ... and {len(closures) - max_examples} more")
    print(f"  Regressions: {len(regressions)}")
    for k, pb, psb, txt in regressions[:max_examples]:
        print(f"    - {k}  [{pb} → {psb}]  {txt[:80]}")
    if len(regressions) > max_examples:
        print(f"    ... and {len(regressions) - max_examples} more")
    print(f"  Bucket-only: {len(bucket_only)}")
    for k, pb, psb, txt in bucket_only[:max_examples]:
        print(f"    ~ {k}  [{pb} → {psb}]  {txt[:80]}")
    if len(bucket_only) > max_examples:
        print(f"    ... and {len(bucket_only) - max_examples} more")
    print(
        f"  Totals: pre={pre_succ}/{len(pre)}, "
        f"post={post_succ}/{len(post)}"
    )
    print()
    return len(closures), len(regressions), len(bucket_only)


def _diff_dirs(
    baseline_dir: Path, current_dir: Path, max_examples: int,
) -> int:
    """Multi-wave diff over the canonical 9-wave + unattributed list."""
    total_cl = total_re = total_bo = 0
    pre_total_ok = post_total_ok = 0
    pre_total = post_total = 0
    for wave_id in WAVE_FILES:
        suffix = f"{wave_id}-parse-results.jsonl"
        pre_path = baseline_dir / suffix
        post_path = current_dir / suffix
        if not (pre_path.exists() and post_path.exists()):
            if pre_path.exists() != post_path.exists():
                missing = post_path if not post_path.exists() else pre_path
                print(f"=== {wave_id} === SKIP (missing {missing})\n")
            continue
        pre = _load(pre_path)
        post = _load(post_path)
        cl, re_, bo = _diff_one(
            pre, post, label=wave_id, max_examples=max_examples,
        )
        total_cl += cl
        total_re += re_
        total_bo += bo
        pre_total_ok += sum(1 for r in pre.values() if _is_success(r))
        post_total_ok += sum(1 for r in post.values() if _is_success(r))
        pre_total += len(pre)
        post_total += len(post)

    print("=== XWAVE TOTALS ===")
    print(
        f"  Closures: {total_cl}  Regressions: {total_re}  "
        f"Bucket-only: {total_bo}"
    )
    print(
        f"  Successes: pre={pre_total_ok}/{pre_total}  "
        f"post={post_total_ok}/{post_total}  "
        f"net Δ={post_total_ok - pre_total_ok}"
    )
    return 0 if total_re == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n", 1)[0],
    )
    parser.add_argument(
        "pre", nargs="?",
        help="single-pair mode: pre parse-results.jsonl path",
    )
    parser.add_argument(
        "post", nargs="?",
        help="single-pair mode: post parse-results.jsonl path",
    )
    parser.add_argument(
        "--baseline-dir", type=Path,
        help=(
            "multi-wave mode: directory containing baseline "
            "<wave>-parse-results.jsonl snapshots"
        ),
    )
    parser.add_argument(
        "--current-dir", type=Path,
        default=Path(__file__).resolve().parents[1]
        / "data" / "tgl" / "exemplars",
        help=(
            "multi-wave mode: directory containing current "
            "<wave>-parse-results.jsonl (default: data/tgl/exemplars/)"
        ),
    )
    parser.add_argument(
        "--max-examples", type=int, default=20,
        help="cap per-section example list (default: 20)",
    )
    args = parser.parse_args()

    # Validate exactly one mode.
    file_mode = args.pre is not None and args.post is not None
    dir_mode = args.baseline_dir is not None
    if file_mode == dir_mode:
        parser.error(
            "specify EITHER a single file pair (PRE POST) OR "
            "--baseline-dir (with optional --current-dir), not both"
        )

    if file_mode:
        pre = _load(Path(args.pre))
        post = _load(Path(args.post))
        _cl, re_, _bo = _diff_one(
            pre, post,
            label=f"{Path(args.pre).name} → {Path(args.post).name}",
            max_examples=args.max_examples,
        )
        return 0 if re_ == 0 else 1
    else:
        return _diff_dirs(
            args.baseline_dir, args.current_dir, args.max_examples,
        )


if __name__ == "__main__":
    sys.exit(main())
