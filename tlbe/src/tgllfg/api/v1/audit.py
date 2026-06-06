# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""``/api/v1/audit/*`` — naturalistic-tier corpus audit over HTTP (13.C.3).

Wraps the Phase 12.F audit engine (:mod:`tgllfg.audit`):

* ``POST /audit/run`` kicks off an audit as a **background job** and
  returns a ``run_id`` immediately;
* ``GET /audit/runs/{run_id}`` polls the job's status + summary;
* ``POST /audit/diff`` diffs the latest on-disk parse-results against the
  checked-in baseline.

The run executes in a **fresh subprocess** (``asyncio.create_subprocess_exec``
of the ``tgllfg audit run`` CLI) rather than in-process: the CLI safely
uses the multiprocessing ``Pool`` (~89s all-waves) because it runs in a
clean process tree — a fork-based ``Pool`` spawned from inside the async
server would inherit the event loop + asyncpg sockets + threads. The
``await proc.communicate()`` is non-blocking, so the event loop stays
responsive for the whole run.

Lifecycle: the job is scheduled with ``asyncio.create_task`` and tracked
in ``app.state.audit_tasks`` so the app lifespan (:mod:`tgllfg.api.app`)
can **cancel in-flight runs on shutdown** — each job's ``finally``
terminates its subprocess, so none is orphaned. One run at a time
(``409`` otherwise). The in-process job registry + single-run guard are
single-worker assumptions; durable / cross-worker state is Phase 15.

The audit command + summarizer + differ are injected so the HTTP layer,
the job lifecycle, and shutdown cancellation are testable without running
a real corpus audit.
"""

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, Any, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from ...audit import (
    AuditDiff,
    default_baseline_path,
    default_workers,
    diff_run,
    load_baseline,
    load_results_dir,
    wave_summary,
)
from ...audit.common import Record

from ..telemetry import log, traced

audit_router = APIRouter(tags=["audit"])

AuditStatus = Literal["running", "completed", "failed", "cancelled"]


# --- DTOs (Pydantic 2) -------------------------------------------------


class AuditRunRequest(BaseModel):
    waves: list[str] | None = Field(
        None, description="Wave ids to audit (default: all waves)."
    )


class WaveSummaryModel(BaseModel):
    wave_id: str
    ok: int
    total: int
    pct: float
    timeouts: int


class RunSummaryModel(BaseModel):
    elapsed_s: float
    n_workers: int
    n_tasks: int
    waves: list[WaveSummaryModel]
    total_ok: int
    total: int
    total_pct: float


class AuditRunStatus(BaseModel):
    run_id: str
    status: AuditStatus
    summary: RunSummaryModel | None = None
    error: str | None = None


class AuditDiffRequest(BaseModel):
    waves: list[str] | None = Field(
        None, description="Wave ids to diff (default: all waves with results)."
    )


class DiffEntryModel(BaseModel):
    source: str
    locator: str
    before: str
    after: str
    text: str


class AuditDiffModel(BaseModel):
    has_regressions: bool
    counts: dict[str, int]
    regressions: list[DiffEntryModel]
    improvements: list[DiffEntryModel]


# --- summarization -----------------------------------------------------


def _summarize_by_wave(
    by_wave: dict[str, list[Record]], *, elapsed_s: float, n_workers: int
) -> RunSummaryModel:
    waves: list[WaveSummaryModel] = []
    total_ok = total = 0
    for wave_id, ok, tot, timeouts in wave_summary(by_wave):
        waves.append(
            WaveSummaryModel(
                wave_id=wave_id,
                ok=ok,
                total=tot,
                pct=round(100.0 * ok / tot, 2) if tot else 0.0,
                timeouts=timeouts,
            )
        )
        total_ok += ok
        total += tot
    return RunSummaryModel(
        elapsed_s=round(elapsed_s, 2),
        n_workers=n_workers,
        n_tasks=total,
        waves=waves,
        total_ok=total_ok,
        total=total,
        total_pct=round(100.0 * total_ok / total, 2) if total else 0.0,
    )


def _summarize_diff(diff: AuditDiff) -> AuditDiffModel:
    def _entries(entries: list) -> list[DiffEntryModel]:
        return [
            DiffEntryModel(
                source=e.source,
                locator=e.locator,
                before=e.before,
                after=e.after,
                text=e.text,
            )
            for e in entries
        ]

    return AuditDiffModel(
        has_regressions=diff.has_regressions,
        counts={
            "regressions": len(diff.regressions),
            "improvements": len(diff.improvements),
            "shifts": len(diff.shifts),
            "new": len(diff.new),
            "removed": len(diff.removed),
        },
        regressions=_entries(diff.regressions),
        improvements=_entries(diff.improvements),
    )


# --- injectables: command / summarizer / differ -----------------------

AuditCommand = list[str]
Summarizer = Callable[..., RunSummaryModel]
AuditDiffer = Callable[..., AuditDiffModel]


def default_audit_command() -> AuditCommand:
    # Run the audit in a fresh `tgllfg` process tree (safe Pool, ~89s).
    return ["tgllfg", "audit", "run"]


def default_summarizer(*, waves: list[str] | None, elapsed_s: float) -> RunSummaryModel:
    by_wave = load_results_dir()
    if waves:
        wanted = set(waves)
        by_wave = {w: r for w, r in by_wave.items() if w in wanted}
    return _summarize_by_wave(by_wave, elapsed_s=elapsed_s, n_workers=default_workers())


def default_audit_differ(*, waves: list[str] | None) -> AuditDiffModel:
    by_wave = load_results_dir()
    if waves:
        wanted = set(waves)
        by_wave = {w: r for w, r in by_wave.items() if w in wanted}
    baseline = load_baseline(
        default_baseline_path(), waves=set(waves) if waves else None
    )
    return _summarize_diff(diff_run(baseline, by_wave))


def get_audit_command() -> AuditCommand:
    return default_audit_command()


def get_summarizer() -> Summarizer:
    return default_summarizer


def get_audit_differ() -> AuditDiffer:
    return default_audit_differ


CommandDep = Annotated[AuditCommand, Depends(get_audit_command)]
SummarizerDep = Annotated[Summarizer, Depends(get_summarizer)]
DifferDep = Annotated[AuditDiffer, Depends(get_audit_differ)]


# --- job registry + background runner ---------------------------------


@dataclass
class _AuditJob:
    run_id: str
    status: AuditStatus = "running"
    summary: RunSummaryModel | None = None
    error: str | None = None
    proc: asyncio.subprocess.Process | None = None


async def _run_audit_job(
    app: Any,
    job: _AuditJob,
    waves: list[str] | None,
    command: AuditCommand,
    summarizer: Summarizer,
) -> None:
    argv = list(command) + (["--waves", ",".join(waves)] if waves else [])
    started = time.monotonic()
    proc: asyncio.subprocess.Process | None = None
    log.info("audit.run.start", run_id=job.run_id, waves=waves)
    try:
        with traced(app.state.tracer, "audit.run", run_id=job.run_id):
            proc = await asyncio.create_subprocess_exec(
                *argv,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            job.proc = proc
            _out, err = await proc.communicate()
        if proc.returncode == 0:
            job.summary = await asyncio.to_thread(
                summarizer, waves=waves, elapsed_s=time.monotonic() - started
            )
            job.status = "completed"
            log.info("audit.run.done", run_id=job.run_id, status="completed")
        else:
            job.status = "failed"
            job.error = (err or b"").decode(errors="replace").strip()[-2000:]
            log.warning("audit.run.done", run_id=job.run_id, status="failed")
    except asyncio.CancelledError:
        job.status = "cancelled"
        log.warning("audit.run.cancelled", run_id=job.run_id)
        raise
    except Exception as exc:  # noqa: BLE001 — surface any failure to the poller
        job.status = "failed"
        job.error = str(exc)
        log.error("audit.run.error", run_id=job.run_id, error=str(exc))
    finally:
        # Terminate the subprocess if it's still running (e.g. on cancel),
        # so it isn't orphaned past the job / server lifetime.
        if proc is not None and proc.returncode is None:
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), timeout=5.0)
            except (TimeoutError, asyncio.TimeoutError):
                proc.kill()
        app.state.audit_tasks.discard(asyncio.current_task())


# --- routes ------------------------------------------------------------


@audit_router.post(
    "/audit/run",
    response_model=AuditRunStatus,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start a corpus audit (background job)",
)
async def audit_run(
    req: AuditRunRequest,
    request: Request,
    command: CommandDep,
    summarizer: SummarizerDep,
) -> AuditRunStatus:
    app = request.app
    if any(not t.done() for t in app.state.audit_tasks):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="an audit run is already in progress",
        )
    job = _AuditJob(run_id=uuid4().hex)
    app.state.audit_jobs[job.run_id] = job
    task = asyncio.create_task(
        _run_audit_job(app, job, req.waves, command, summarizer)
    )
    app.state.audit_tasks.add(task)
    return AuditRunStatus(run_id=job.run_id, status="running")


@audit_router.get(
    "/audit/runs/{run_id}",
    response_model=AuditRunStatus,
    summary="Poll an audit run's status",
)
async def audit_run_status(run_id: str, request: Request) -> AuditRunStatus:
    job: _AuditJob | None = request.app.state.audit_jobs.get(run_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"unknown audit run: {run_id}"
        )
    return AuditRunStatus(
        run_id=job.run_id, status=job.status, summary=job.summary, error=job.error
    )


@audit_router.post(
    "/audit/diff",
    response_model=AuditDiffModel,
    summary="Diff the latest results against the baseline",
)
async def audit_diff(
    req: AuditDiffRequest, request: Request, differ: DifferDep
) -> AuditDiffModel:
    with traced(request.app.state.tracer, "audit.diff"):
        return await asyncio.to_thread(differ, waves=req.waves)
