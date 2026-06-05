# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 12.F — the ``tgllfg audit`` corpus-audit package + CLI.

Fast, parser-free coverage of the audit data layer (classify / baseline
roundtrip / diff / fingerprint disambiguation), the run plumbing (via a
stub parser, ``--workers 1`` in-process), the wave filter used by the
sharded CI gate, the CLI argument surface, and the checked-in baseline
artifact's well-formedness.
"""

import json

import pytest

from tgllfg.audit import (
    classify_change,
    default_baseline_path,
    diff_run,
    format_diff,
    load_baseline,
    load_results_dir,
    load_tasks,
    run_audit,
    text_fingerprint,
    write_baseline,
    write_results,
)
from tgllfg.audit import common as audit_common
from tgllfg.cli.main import _build_parser

S1 = "parse-success-1"
SN = "parse-success-N"
ZF = "zero-parse-fragment"
ZN = "zero-parse-no-fragment"


def _by_wave(*records: tuple) -> dict[str, list[tuple]]:
    d: dict[str, list[tuple]] = {}
    for r in records:
        d.setdefault(r[0], []).append(r)
    return d


class _StubResult:
    def __init__(self, parses: list, fragments: list) -> None:
        self.parses = parses
        self.fragments = fragments


def _stub_parse(text: str, n_best: int = 2) -> _StubResult:
    """Deterministic bucketing by text marker (no real parser)."""
    if "@N" in text:
        return _StubResult([1, 2], [])
    if "@1" in text:
        return _StubResult([1], [])
    if "@frag" in text:
        return _StubResult([], [object()])
    return _StubResult([], [])


class TestClassifyChange:
    def test_regression(self) -> None:
        assert classify_change(S1, ZF) == "REGRESSION"
        assert classify_change(SN, ZN) == "REGRESSION"

    def test_improvement(self) -> None:
        assert classify_change(ZF, S1) == "IMPROVEMENT"

    def test_shift(self) -> None:
        assert classify_change(S1, SN) == f"SHIFT-{S1}->{SN}"

    def test_zpf_shift(self) -> None:
        assert classify_change(ZN, ZF).startswith("ZPF-SHIFT-")

    def test_same(self) -> None:
        assert classify_change(S1, S1) == "SAME"
        assert classify_change(ZF, ZF) == "SAME"


class TestTextFingerprint:
    def test_stable(self) -> None:
        assert text_fingerprint("Mabait ka.") == text_fingerprint("Mabait ka.")

    def test_distinct(self) -> None:
        assert text_fingerprint("a") != text_fingerprint("b")

    def test_text_free(self) -> None:
        fp = text_fingerprint("Mabait na mabait ka.")
        assert len(fp) == 12
        assert all(c in "0123456789abcdef" for c in fp)
        assert "mabait" not in fp.lower()


class TestBaselineRoundtrip:
    def test_roundtrip(self, tmp_path) -> None:
        bw = _by_wave(
            ("w1", "src", "loc1", S1, "t1"),
            ("w1", "src", "loc2", ZF, "t2"),
        )
        p = tmp_path / "base.jsonl"
        assert write_baseline(bw, p) == 2
        base = load_baseline(p)
        assert base[("src", "loc1", text_fingerprint("t1"))] == S1
        assert base[("src", "loc2", text_fingerprint("t2"))] == ZF

    def test_colliding_locator_kept_distinct(self, tmp_path) -> None:
        # The wave4-kroeger1991 case: one locator, two distinct texts.
        bw = _by_wave(
            ("w4", "k91", "p126/25a", S1, "Mabait na mabait ka."),
            ("w4", "k91", "p126/25a", SN, "Linutu at kinain ko ang isda."),
        )
        p = tmp_path / "base.jsonl"
        assert write_baseline(bw, p) == 2
        base = load_baseline(p)
        assert len(base) == 2
        diff = diff_run(base, bw)
        assert not any(
            [diff.regressions, diff.improvements, diff.shifts, diff.new, diff.removed]
        )

    def test_text_free_artifact(self, tmp_path) -> None:
        bw = _by_wave(("w1", "src", "loc1", S1, "SECRET licensed text"))
        p = tmp_path / "base.jsonl"
        write_baseline(bw, p)
        assert "SECRET" not in p.read_text()
        row = json.loads(p.read_text().splitlines()[0])
        assert set(row) == {"wave", "source", "locator", "text_sha", "bucket"}


class TestDiffRun:
    def _baseline(self, tmp_path):
        bw = _by_wave(
            ("w1", "s", "a", S1, "ta"),
            ("w1", "s", "b", ZF, "tb"),
            ("w1", "s", "c", S1, "tc"),
        )
        p = tmp_path / "base.jsonl"
        write_baseline(bw, p)
        return load_baseline(p)

    def test_clean(self, tmp_path) -> None:
        base = self._baseline(tmp_path)
        cur = _by_wave(
            ("w1", "s", "a", S1, "ta"),
            ("w1", "s", "b", ZF, "tb"),
            ("w1", "s", "c", S1, "tc"),
        )
        d = diff_run(base, cur)
        assert not any([d.regressions, d.improvements, d.shifts, d.new, d.removed])
        assert not d.has_regressions

    def test_detects_all_change_kinds(self, tmp_path) -> None:
        base = self._baseline(tmp_path)
        cur = _by_wave(
            ("w1", "s", "a", ZN, "ta"),  # regression
            ("w1", "s", "b", S1, "tb"),  # improvement
            # c removed
            ("w1", "s", "d", S1, "td"),  # new
        )
        d = diff_run(base, cur)
        assert [e.locator for e in d.regressions] == ["a"]
        assert [e.locator for e in d.improvements] == ["b"]
        assert [e.locator for e in d.new] == ["d"]
        assert [e.locator for e in d.removed] == ["c"]
        assert d.has_regressions

    def test_edited_text_is_removed_plus_new(self, tmp_path) -> None:
        # Editing an exemplar's text (same locator) reads as removed+new,
        # not a silent shift — the fingerprint changed.
        base = self._baseline(tmp_path)
        cur = _by_wave(
            ("w1", "s", "a", S1, "ta-EDITED"),
            ("w1", "s", "b", ZF, "tb"),
            ("w1", "s", "c", S1, "tc"),
        )
        d = diff_run(base, cur)
        assert [e.locator for e in d.new] == ["a"]
        assert [e.locator for e in d.removed] == ["a"]
        assert not d.regressions

    def test_format_diff_reports_counts(self, tmp_path) -> None:
        base = self._baseline(tmp_path)
        cur = _by_wave(("w1", "s", "a", ZN, "ta"))
        out = format_diff(diff_run(base, cur))
        assert "REGRESSIONS=1" in out


class TestWaveFilter:
    def test_load_baseline_waves_filter(self, tmp_path) -> None:
        bw = _by_wave(
            ("w1", "s", "a", S1, "ta"),
            ("w2", "s", "b", S1, "tb"),
        )
        p = tmp_path / "base.jsonl"
        write_baseline(bw, p)
        only_w1 = load_baseline(p, waves={"w1"})
        assert ("s", "a", text_fingerprint("ta")) in only_w1
        assert ("s", "b", text_fingerprint("tb")) not in only_w1

    def test_shard_diff_no_spurious_removed(self, tmp_path) -> None:
        # A shard runs only w1; diffing its waves against the w1-filtered
        # baseline must not flag w2 exemplars as REMOVED.
        bw = _by_wave(
            ("w1", "s", "a", S1, "ta"),
            ("w2", "s", "b", S1, "tb"),
        )
        p = tmp_path / "base.jsonl"
        write_baseline(bw, p)
        shard_base = load_baseline(p, waves={"w1"})
        shard_cur = {"w1": [("w1", "s", "a", S1, "ta")]}
        d = diff_run(shard_base, shard_cur)
        assert not any([d.regressions, d.improvements, d.shifts, d.new, d.removed])


class TestRunAudit:
    def _corpus(self, tmp_path):
        d = tmp_path / "exemplars"
        d.mkdir()
        rows = [
            {"source": "s", "locator": "1", "text": "x @1"},
            {"source": "s", "locator": "2", "text": "x @N"},
            {"source": "s", "locator": "3", "text": "x @frag"},
            {"source": "s", "locator": "4", "text": "x none"},
            {"source": "s", "locator": "5", "text": "y", "marked_ungrammatical": True},
            {"source": "s", "locator": "6", "text": ""},
        ]
        with (d / "wave1-exemplars.jsonl").open("w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        return d

    def test_load_tasks_filters(self, tmp_path) -> None:
        d = self._corpus(tmp_path)
        tasks = load_tasks(d, wave_filter={"wave1-exemplars"})
        assert {t[2] for t in tasks} == {"1", "2", "3", "4"}

    def test_run_buckets(self, tmp_path, monkeypatch) -> None:
        d = self._corpus(tmp_path)
        monkeypatch.setattr(audit_common, "_PARSE_FN", _stub_parse)
        run = run_audit(exemplars_dir=d, waves=["wave1-exemplars"], workers=1)
        buckets = {r[2]: r[3] for r in run.by_wave["wave1-exemplars"]}
        assert buckets == {"1": S1, "2": SN, "3": ZF, "4": ZN}
        assert run.n_workers == 1
        assert run.n_tasks == 4

    def test_write_then_load_results(self, tmp_path, monkeypatch) -> None:
        d = self._corpus(tmp_path)
        monkeypatch.setattr(audit_common, "_PARSE_FN", _stub_parse)
        run = run_audit(exemplars_dir=d, waves=["wave1-exemplars"], workers=1)
        write_results(run.by_wave, exemplars_dir=d)
        reloaded = load_results_dir(exemplars_dir=d)
        assert {r[2]: r[3] for r in reloaded["wave1-exemplars"]} == {
            "1": S1,
            "2": SN,
            "3": ZF,
            "4": ZN,
        }


class TestCliParser:
    def test_audit_subcommands_parse(self) -> None:
        p = _build_parser()
        ns = p.parse_args(["audit", "run", "--waves", "w1", "--workers", "2"])
        assert ns.cmd == "audit"
        assert ns.audit_cmd == "run"
        assert ns.waves == "w1"
        assert ns.workers == 2
        ns = p.parse_args(["audit", "diff", "--run", "--baseline", "/b.jsonl"])
        assert ns.audit_cmd == "diff"
        assert ns.run is True
        assert ns.baseline == "/b.jsonl"
        ns = p.parse_args(["audit", "baseline", "--output", "/o.jsonl"])
        assert ns.audit_cmd == "baseline"
        assert ns.output == "/o.jsonl"

    def test_audit_requires_subcommand(self) -> None:
        p = _build_parser()
        with pytest.raises(SystemExit):
            p.parse_args(["audit"])


class TestBaselineArtifact:
    def test_committed_baseline_well_formed(self) -> None:
        p = default_baseline_path()
        assert p.exists(), f"missing committed baseline: {p}"
        rows = [
            json.loads(line) for line in p.read_text().splitlines() if line.strip()
        ]
        assert rows, "baseline is empty"
        for row in rows[:100]:
            assert set(row) >= {"wave", "source", "locator", "text_sha", "bucket"}
            assert len(row["text_sha"]) == 12
