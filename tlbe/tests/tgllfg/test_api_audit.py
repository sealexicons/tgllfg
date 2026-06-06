# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 13.C.3: /api/v1/audit/* — subprocess run + poll + diff + cancel.

The audit command / summarizer / differ are injected, so the HTTP layer,
the job lifecycle, and — critically — **lifespan-shutdown cancellation**
are tested without running a real corpus audit. The cancellation test
launches a real long-running subprocess, triggers lifespan shutdown, and
asserts the subprocess was terminated (not orphaned). Summarization is
unit-tested directly.

Uses the shared ``api_app`` fixture (conftest): each test sets its own
dependency overrides on it before wrapping it in a ``TestClient``; the
cancel test also reads ``api_app.state`` after the client context exits.
"""

import os
import sys
import time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tgllfg.api.v1.audit import (
    AuditDiffModel,
    RunSummaryModel,
    WaveSummaryModel,
    _summarize_by_wave,
    _summarize_diff,
    get_audit_command,
    get_audit_differ,
    get_summarizer,
)
from tgllfg.audit import AuditDiff, DiffEntry

_SLEEP_CMD = [sys.executable, "-c", "import time; time.sleep(30)"]
_OK_CMD = [sys.executable, "-c", "pass"]  # exits 0 immediately


def _fake_summarizer(
    *, waves: list[str] | None = None, elapsed_s: float = 0.0
) -> RunSummaryModel:
    return RunSummaryModel(
        elapsed_s=elapsed_s,
        n_workers=1,
        n_tasks=2,
        waves=[WaveSummaryModel(wave_id="wave1-exemplars", ok=1, total=2, pct=50.0, timeouts=0)],
        total_ok=1,
        total=2,
        total_pct=50.0,
    )


def _fake_differ(*, waves: list[str] | None = None) -> AuditDiffModel:
    return AuditDiffModel(
        has_regressions=False,
        counts={"regressions": 0, "improvements": 0, "shifts": 0, "new": 0, "removed": 0},
        regressions=[],
        improvements=[],
    )


def _wait_for(predicate, tries: int = 200, delay: float = 0.02) -> bool:
    for _ in range(tries):
        if predicate():
            return True
        time.sleep(delay)
    return False


# --- run lifecycle (fast subprocess + fake summarizer) ----------------


def test_audit_run_completes(api_app: FastAPI) -> None:
    api_app.dependency_overrides[get_audit_command] = lambda: list(_OK_CMD)
    api_app.dependency_overrides[get_summarizer] = lambda: _fake_summarizer
    with TestClient(api_app) as client:
        run_id = client.post("/api/v1/audit/run", json={}).json()["run_id"]
        body = client.get(f"/api/v1/audit/runs/{run_id}").json()
        for _ in range(200):
            if body["status"] != "running":
                break
            time.sleep(0.02)
            body = client.get(f"/api/v1/audit/runs/{run_id}").json()
    assert body["status"] == "completed"
    assert body["summary"]["total_pct"] == 50.0
    assert body["error"] is None


def test_audit_run_status_unknown_404(api_app: FastAPI) -> None:
    with TestClient(api_app) as client:
        assert client.get("/api/v1/audit/runs/does-not-exist").status_code == 404


def test_audit_run_conflict_409(api_app: FastAPI) -> None:
    api_app.dependency_overrides[get_audit_command] = lambda: list(_SLEEP_CMD)
    with TestClient(api_app) as client:
        first = client.post("/api/v1/audit/run", json={})
        assert first.status_code == 202
        second = client.post("/api/v1/audit/run", json={})
        assert second.status_code == 409
    # lifespan shutdown cancels the in-flight first run.


# --- lifespan-shutdown cancellation (real subprocess) -----------------


def test_lifespan_cancels_inflight_audit(api_app: FastAPI) -> None:
    api_app.dependency_overrides[get_audit_command] = lambda: list(_SLEEP_CMD)
    with TestClient(api_app) as client:
        started = client.post("/api/v1/audit/run", json={})
        assert started.status_code == 202
        run_id = started.json()["run_id"]
        job = api_app.state.audit_jobs[run_id]
        # Wait until the subprocess is actually launched.
        assert _wait_for(lambda: job.proc is not None), "subprocess never launched"
        pid = job.proc.pid
        assert job.proc.returncode is None  # still running
    # Exiting the TestClient context runs lifespan shutdown, which must
    # cancel the in-flight run and terminate its subprocess.
    assert job.status == "cancelled"
    assert job.proc.returncode is not None  # terminated + reaped, not orphaned
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)


# --- diff (fake differ) -----------------------------------------------


def test_audit_diff(api_app: FastAPI) -> None:
    api_app.dependency_overrides[get_audit_differ] = lambda: _fake_differ
    with TestClient(api_app) as client:
        resp = client.post("/api/v1/audit/diff", json={})
    assert resp.status_code == 200
    body = resp.json()
    assert body["has_regressions"] is False
    assert body["counts"]["regressions"] == 0


# --- summarization unit tests -----------------------------------------


def test_summarize_by_wave_counts_and_pct() -> None:
    by_wave = {
        "wave1-exemplars": [
            ("wave1-exemplars", "s", "l1", "parse-success-1", "t"),
            ("wave1-exemplars", "s", "l2", "zero-parse", "t"),
            ("wave1-exemplars", "s", "l3", "parse-timeout", "t"),
        ]
    }
    summary = _summarize_by_wave(by_wave, elapsed_s=1.0, n_workers=4)
    assert summary.n_workers == 4
    assert summary.n_tasks == 3
    assert len(summary.waves) == 1
    w = summary.waves[0]
    assert (w.wave_id, w.ok, w.total, w.timeouts) == ("wave1-exemplars", 1, 3, 1)
    assert w.pct == 33.33
    assert summary.total_ok == 1
    assert summary.total == 3
    assert summary.total_pct == 33.33


def test_summarize_diff_buckets() -> None:
    diff = AuditDiff(
        regressions=[DiffEntry("src", "loc", "parse-success-1", "zero-parse", "txt")],
        improvements=[DiffEntry("src", "l2", "zero-parse", "parse-success-1", "t2")],
    )
    model = _summarize_diff(diff)
    assert model.has_regressions is True
    assert model.counts["regressions"] == 1
    assert model.counts["improvements"] == 1
    assert model.regressions[0].source == "src"
    assert model.regressions[0].after == "zero-parse"
