# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Parallel multi-wave audit over the naturalistic + unattributed corpora.

Thin CLI shim over :mod:`tgllfg.audit` — Phase 12.F extracted the audit
logic into the package so this script and the ``tgllfg audit run``
subcommand share one implementation. Prefer ``tgllfg audit run`` for new
workflows; this entry point is preserved for the established
``python scripts/audit_corpus.py`` invocation.

Output: one ``<wave>-parse-results.jsonl`` per wave under
``data/tgl/exemplars/`` (schema ``{source, locator, bucket, text}``),
plus a per-wave + grand-total summary on stdout. ~88-90s wall on a
12-core CPU for the full 9-wave + unattributed audit (~6000 sentences);
the sequential equivalent (``--workers 1``) takes 7-10 minutes.

Usage:

    python scripts/audit_corpus.py                        # full audit
    python scripts/audit_corpus.py --waves wave1-exemplars,unattributed-constructions
    python scripts/audit_corpus.py --workers 6
"""

import argparse
import sys

from tgllfg.audit.common import format_summary, run_audit, write_results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="worker process count (default: min(cpu_count-1, 11); 1 = in-process)",
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

    waves = args.waves.split(",") if args.waves else None
    run = run_audit(waves=waves, workers=args.workers, chunksize=args.chunksize)
    write_results(run.by_wave)
    print(format_summary(run))
    return 0


if __name__ == "__main__":
    sys.exit(main())
