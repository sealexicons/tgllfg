# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Naturalistic-tier corpus audit (Phase 12.F).

Shared by ``scripts/audit_corpus.py`` and the ``tgllfg audit`` CLI
subcommand. See :mod:`tgllfg.audit.common` for the implementation.
"""

from tgllfg.audit.common import (
    WAVE_FILES,
    AuditDiff,
    AuditRun,
    DiffEntry,
    classify_change,
    default_baseline_path,
    default_exemplars_dir,
    default_workers,
    diff_run,
    format_diff,
    format_summary,
    is_success,
    load_baseline,
    load_results_dir,
    load_tasks,
    run_audit,
    text_fingerprint,
    wave_summary,
    write_baseline,
    write_results,
)

__all__ = [
    "WAVE_FILES",
    "AuditDiff",
    "AuditRun",
    "DiffEntry",
    "classify_change",
    "default_baseline_path",
    "default_exemplars_dir",
    "default_workers",
    "diff_run",
    "format_diff",
    "format_summary",
    "is_success",
    "load_baseline",
    "load_results_dir",
    "load_tasks",
    "run_audit",
    "text_fingerprint",
    "wave_summary",
    "write_baseline",
    "write_results",
]
