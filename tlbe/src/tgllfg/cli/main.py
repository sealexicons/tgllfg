# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Top-level ``tgllfg`` CLI dispatcher.

Subcommands:

* ``tgllfg lex migrate`` — apply Alembic migrations to head against
  ``DATABASE_URL`` (or ``--database-url``).
* ``tgllfg lex seed`` — load the YAML seed under ``data/tgl/`` (or
  ``--data-dir``) into the Postgres lexicon. Idempotent.
* ``tgllfg lex import`` — import a CSV of lemma data with citation.
* ``tgllfg parse`` — parse a Tagalog sentence and print its
  c-/f-structure summary. With ``--strict`` it suppresses fragment
  output on full-parse failure (Phase 4 §7.9).
* ``tgllfg audit run|diff|baseline`` — run the naturalistic-tier
  corpus audit, diff a run against the checked-in baseline (exit 1
  on regression — the CI gate), or (re)write that baseline
  (Phase 12.F).
* ``tgllfg docs grammar`` — (re)generate ``docs/grammar.md`` from the
  cfg rule corpus; ``--check`` verifies it is in sync (exit 1 on
  drift) instead of writing (Phase 12.final).
"""

import argparse
import asyncio
import json
import os
import sys
from collections.abc import Sequence

from pathlib import Path

from alembic import command

from tgllfg.lex.import_csv import import_lemmas_csv
from tgllfg.lex.migrations import build_alembic_config
from tgllfg.lex.seed import seed_database


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tgllfg")
    sub = parser.add_subparsers(dest="cmd", required=True)

    lex = sub.add_parser("lex", help="lexicon database commands")
    lex.add_argument(
        "--database-url",
        default=None,
        help="Postgres connection URL (default: $DATABASE_URL)",
    )
    lex_sub = lex.add_subparsers(dest="lex_cmd", required=True)

    lex_sub.add_parser("migrate", help="apply Alembic migrations to head")

    seed = lex_sub.add_parser("seed", help="upsert the YAML seed into the database")
    seed.add_argument(
        "--data-dir",
        default=None,
        help="path to data/tgl/ (default: shipped seed)",
    )

    imp = lex_sub.add_parser(
        "import",
        help="import a CSV of additive lemma data with source citation",
    )
    imp.add_argument("path", help="path to a CSV file with the lemma rows")
    imp.add_argument(
        "--source-short-name",
        required=True,
        help="short_name to record in the `source` table (e.g. 'Kaufman1939')",
    )
    imp.add_argument(
        "--source-full-citation",
        required=True,
        help="full bibliographic citation for the source",
    )

    parse_p = sub.add_parser("parse", help="parse a Tagalog sentence")
    parse_p.add_argument("sentence", help="the sentence to parse")
    parse_p.add_argument(
        "--strict",
        action="store_true",
        help=(
            "suppress fragment output on full-parse failure "
            "(default: emit fragments for debugging; see Phase 4 §7.9)"
        ),
    )
    parse_p.add_argument(
        "--n-best",
        type=int,
        default=5,
        help="cap on the number of complete parses returned (default: 5)",
    )

    audit = sub.add_parser(
        "audit", help="run / diff / baseline the naturalistic-tier corpus audit"
    )
    audit_sub = audit.add_subparsers(dest="audit_cmd", required=True)

    def _add_audit_common(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--waves",
            default=None,
            help="comma-separated wave ids to audit (default: all)",
        )
        p.add_argument(
            "--workers",
            type=int,
            default=None,
            help="worker count (default: min(cpu_count-1, 11); 1 = in-process)",
        )
        p.add_argument(
            "--exemplars-dir",
            default=None,
            help="corpus dir (default: data/tgl/exemplars or $TGLLFG_EXEMPLARS_DIR)",
        )

    a_run = audit_sub.add_parser(
        "run", help="parse the corpus, writing per-wave parse-results"
    )
    _add_audit_common(a_run)

    a_diff = audit_sub.add_parser(
        "diff", help="diff current parses against a baseline; exit 1 on regression"
    )
    _add_audit_common(a_diff)
    a_diff.add_argument(
        "--baseline",
        default=None,
        help="baseline JSONL (default: tests/tgllfg/data/audit-baseline.jsonl)",
    )
    a_diff.add_argument(
        "--run",
        action="store_true",
        help="parse fresh instead of reading existing parse-results",
    )

    a_base = audit_sub.add_parser(
        "baseline", help="(re)write the compact, text-free baseline artifact"
    )
    _add_audit_common(a_base)
    a_base.add_argument(
        "--output",
        default=None,
        help="output path (default: tests/tgllfg/data/audit-baseline.jsonl)",
    )
    a_base.add_argument(
        "--run",
        action="store_true",
        help="parse fresh instead of reading existing parse-results",
    )

    docs = sub.add_parser("docs", help="documentation generators")
    docs_sub = docs.add_subparsers(dest="docs_cmd", required=True)
    g = docs_sub.add_parser(
        "grammar", help="(re)generate docs/grammar.md from the cfg rules"
    )
    g.add_argument(
        "--check",
        action="store_true",
        help="verify docs/grammar.md is in sync (exit 1 on drift); do not write",
    )

    serve_p = sub.add_parser("serve", help="run the REST API under uvicorn")
    serve_p.add_argument(
        "--host", default="127.0.0.1", help="bind host (default: 127.0.0.1)"
    )
    serve_p.add_argument(
        "--port", type=int, default=8000, help="bind port (default: 8000)"
    )
    serve_p.add_argument(
        "--workers", type=int, default=1, help="uvicorn worker count (default: 1)"
    )
    serve_p.add_argument(
        "--reload", action="store_true", help="auto-reload on code changes (dev)"
    )

    openapi_p = sub.add_parser(
        "openapi", help="(re)generate the committed openapi.json from the app"
    )
    openapi_p.add_argument(
        "--output", default=None, help="output path (default: top-level openapi.json)"
    )
    openapi_p.add_argument(
        "--check",
        action="store_true",
        help="verify openapi.json is in sync (exit 1 on drift); do not write",
    )

    bench_p = sub.add_parser("bench", help="parser performance benchmark")
    bench_p.add_argument(
        "--check",
        action="store_true",
        help="full local gate: forest-size hard-fail + soft wall-clock warning",
    )
    bench_p.add_argument(
        "--check-counts",
        action="store_true",
        help="CI gate: fast, deterministic forest-size regression check (no timing)",
    )
    bench_p.add_argument(
        "--update", action="store_true", help="(re)write the committed baseline"
    )
    bench_p.add_argument(
        "--json", action="store_true", help="emit the raw results as JSON"
    )

    return parser


def _resolve_db_url(args: argparse.Namespace) -> str:
    url = args.database_url or os.environ.get("DATABASE_URL")
    if not url:
        sys.stderr.write(
            "tgllfg: DATABASE_URL is not set; pass --database-url or export it\n"
        )
        sys.exit(2)
    return url


def main(argv: Sequence[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)

    if args.cmd == "parse":
        _cmd_parse(args)
        return

    if args.cmd == "audit":
        _cmd_audit(args)
        return

    if args.cmd == "docs":
        _cmd_docs(args)
        return

    if args.cmd == "serve":
        _cmd_serve(args)
        return

    if args.cmd == "openapi":
        _cmd_openapi(args)
        return

    if args.cmd == "bench":
        _cmd_bench(args)
        return

    if args.cmd != "lex":
        raise AssertionError(f"unhandled cmd: {args.cmd}")  # argparse rejects others

    db_url = _resolve_db_url(args)

    if args.lex_cmd == "migrate":
        cfg = build_alembic_config(db_url)
        command.upgrade(cfg, "head")
        return

    if args.lex_cmd == "seed":
        report = asyncio.run(seed_database(db_url, args.data_dir))
        sys.stdout.write(
            f"seeded: language={report.languages} lemma={report.lemmas} "
            f"affix={report.affixes} paradigm_cell={report.paradigm_cells} "
            f"sandhi_rule={report.sandhi_rules} particle={report.particles} "
            f"pronoun={report.pronouns} voice_alias={report.voice_aliases} "
            f"metadata={report.metadata_keys}\n"
        )
        return

    if args.lex_cmd == "import":
        import_report = asyncio.run(
            import_lemmas_csv(
                db_url,
                Path(args.path),
                source_short_name=args.source_short_name,
                source_full_citation=args.source_full_citation,
            )
        )
        sys.stdout.write(
            f"imported: rows_read={import_report.rows_read} "
            f"rows_upserted={import_report.rows_upserted} "
            f"source={import_report.source_short_name}\n"
        )
        return

    raise AssertionError(f"unhandled lex_cmd: {args.lex_cmd}")  # argparse rejects others


def _cmd_parse(args: argparse.Namespace) -> None:
    """Phase 4 §7.9: parse a sentence and print a summary.

    Default mode emits a complete parse if found; otherwise emits
    fragment summaries to help debug the failure. ``--strict``
    suppresses fragment output (empty stdout, exit 0).
    """
    from tgllfg.core.pipeline import parse_text_with_fragments

    result = parse_text_with_fragments(args.sentence, n_best=args.n_best)

    if result.parses:
        for i, (_, f, _, diags) in enumerate(result.parses, start=1):
            sys.stdout.write(f"Parse #{i}:\n")
            sys.stdout.write(f"  PRED: {f.feats.get('PRED')}\n")
            sys.stdout.write(f"  VOICE: {f.feats.get('VOICE')}\n")
            sys.stdout.write(f"  ASPECT: {f.feats.get('ASPECT')}\n")
            non_blocking = [d for d in diags if not d.is_blocking()]
            if non_blocking:
                sys.stdout.write(f"  diagnostics ({len(non_blocking)} info):\n")
                for d in non_blocking[:3]:
                    sys.stdout.write(f"    [{d.kind}] {d.message}\n")
        return

    if args.strict:
        # Strict mode: empty stdout on failure. Exit 0 (Unix-tool
        # convention: nothing printed = nothing matched).
        sys.stderr.write("(no complete parse)\n")
        return

    if not result.fragments:
        sys.stderr.write("(no parse, no fragments recoverable)\n")
        return

    sys.stdout.write(f"(partial: {len(result.fragments)} fragment(s))\n")
    for i, frag in enumerate(result.fragments, start=1):
        start, end = frag.span
        sys.stdout.write(
            f"Fragment #{i} [tokens {start}..{end}]: {frag.ctree.label}\n"
        )
        blocking = [d for d in frag.diagnostics if d.is_blocking()]
        for d in blocking[:2]:
            sys.stdout.write(f"  blocked: [{d.kind}] {d.message}\n")


def _cmd_audit(args: argparse.Namespace) -> None:
    """Phase 12.F: run / diff / (re)baseline the naturalistic-tier audit.

    ``run`` parses the corpus and writes per-wave parse-results.
    ``diff`` compares the current parses against a checked-in baseline
    and exits non-zero on any regression (the CI gate). ``baseline``
    (re)writes the compact, text-free baseline artifact. ``diff`` and
    ``baseline`` reuse the per-wave parse-results on disk unless
    ``--run`` parses fresh.
    """
    from tgllfg.audit import (
        default_baseline_path,
        default_exemplars_dir,
        diff_run,
        format_diff,
        format_summary,
        load_baseline,
        load_results_dir,
        run_audit,
        write_baseline,
        write_results,
    )

    exemplars_dir = (
        Path(args.exemplars_dir) if args.exemplars_dir else default_exemplars_dir()
    )
    waves = args.waves.split(",") if args.waves else None
    wave_set = set(waves) if waves else None

    if args.audit_cmd == "run":
        run = run_audit(exemplars_dir=exemplars_dir, waves=waves, workers=args.workers)
        write_results(run.by_wave, exemplars_dir=exemplars_dir)
        sys.stdout.write(format_summary(run) + "\n")
        return

    if args.run:
        by_wave = run_audit(
            exemplars_dir=exemplars_dir, waves=waves, workers=args.workers
        ).by_wave
    else:
        by_wave = load_results_dir(exemplars_dir=exemplars_dir)
        if wave_set is not None:
            by_wave = {w: r for w, r in by_wave.items() if w in wave_set}

    if args.audit_cmd == "baseline":
        out = Path(args.output) if args.output else default_baseline_path()
        n = write_baseline(by_wave, out)
        sys.stdout.write(f"wrote baseline: {n} rows -> {out}\n")
        return

    if args.audit_cmd == "diff":
        baseline_path = (
            Path(args.baseline) if args.baseline else default_baseline_path()
        )
        baseline = load_baseline(baseline_path, waves=wave_set)
        diff = diff_run(baseline, by_wave)
        sys.stdout.write(format_diff(diff) + "\n")
        if diff.has_regressions:
            sys.stderr.write(
                f"audit diff: {len(diff.regressions)} regression(s) — failing\n"
            )
            sys.exit(1)
        return

    raise AssertionError(f"unhandled audit_cmd: {args.audit_cmd}")  # argparse rejects others


def _cmd_docs(args: argparse.Namespace) -> None:
    """Phase 12.final: documentation generators.

    ``grammar`` (re)generates ``docs/grammar.md`` from the cfg rule
    corpus; with ``--check`` it verifies the committed file matches a
    fresh render and exits 1 on drift (a pre-commit / CI gate) without
    writing.
    """
    from tgllfg.docs import GRAMMAR_DOC_PATH, render_grammar_doc, write_grammar_doc

    if args.docs_cmd == "grammar":
        if args.check:
            expected = render_grammar_doc()
            actual = (
                GRAMMAR_DOC_PATH.read_text(encoding="utf-8")
                if GRAMMAR_DOC_PATH.exists()
                else ""
            )
            if actual != expected:
                sys.stderr.write(
                    "docs/grammar.md is out of sync — run `tgllfg docs grammar`\n"
                )
                sys.exit(1)
            sys.stdout.write("docs/grammar.md is in sync\n")
            return
        path = write_grammar_doc()
        sys.stdout.write(f"wrote {path}\n")
        return

    raise AssertionError(f"unhandled docs_cmd: {args.docs_cmd}")  # argparse rejects others


def _cmd_serve(args: argparse.Namespace) -> None:
    """Phase 13.D: run the REST API under uvicorn.

    Uses the ``tgllfg.api:create_app`` factory via import string so
    ``--workers`` / ``--reload`` work (uvicorn needs an import target,
    not an app instance, for those).
    """
    import uvicorn

    uvicorn.run(
        "tgllfg.api:create_app",
        factory=True,
        host=args.host,
        port=args.port,
        workers=args.workers,
        reload=args.reload,
    )


def _cmd_openapi(args: argparse.Namespace) -> None:
    """Phase 13.D: (re)generate or verify the committed ``openapi.json``.

    Default writes the schema (``app.openapi()``, natural key order) to
    the top-level ``openapi.json``; ``--check`` verifies the committed file
    matches a fresh render and exits 1 on drift (the openapi-sync gate),
    mirroring ``tgllfg docs grammar --check``.
    """
    from tgllfg.api import OPENAPI_PATH, render_openapi, write_openapi

    if args.check:
        expected = render_openapi()
        actual = (
            OPENAPI_PATH.read_text(encoding="utf-8") if OPENAPI_PATH.exists() else ""
        )
        if actual != expected:
            sys.stderr.write("openapi.json is out of sync — run `tgllfg openapi`\n")
            sys.exit(1)
        sys.stdout.write("openapi.json is in sync\n")
        return

    if args.output:
        out = Path(args.output)
        out.write_text(render_openapi(), encoding="utf-8")
    else:
        out = write_openapi()
    sys.stdout.write(f"wrote {out}\n")


def _cmd_bench(args: argparse.Namespace) -> None:
    """Phase 13.J: run the parser performance benchmark.

    The hard gate is **deterministic forest size** (machine-independent
    over-generation count), so it's CI-safe; wall-clock time is reported
    but only a soft warning (machine-variable). ``--check-counts`` is the
    fast, timing-free count gate for CI; ``--check`` is the full local gate
    (counts hard + time warning); ``--update`` rewrites the baseline;
    ``--json`` emits the raw results.
    """
    from tgllfg.bench import (
        BASELINE_PATH,
        TOLERANCE,
        compare_counts,
        compare_to_baseline,
        load_baseline,
        run_bench,
        run_counts,
        write_baseline,
    )

    if args.check_counts:
        grown = compare_counts(run_counts(), load_baseline())
        if grown:
            sys.stderr.write("forest-size regressions (over-generation):\n")
            for rid, cur_n, base_n in grown:
                sys.stderr.write(f"  {rid}: {cur_n} vs {base_n}\n")
            sys.exit(1)
        sys.stdout.write("no forest-size regressions vs baseline\n")
        return

    results = run_bench()

    if args.json:
        sys.stdout.write(json.dumps(results, indent=2) + "\n")
        return

    if args.update:
        write_baseline(results)
        sys.stdout.write(f"wrote baseline: {BASELINE_PATH}\n")
        return

    for rid, r in results.items():
        sys.stdout.write(
            f"{rid:22s} {r['total_ms']:8.2f} ms  "
            f"(morph {r['morph_ms']:.2f} / lex {r['lex_ms']:.2f} / "
            f"build {r['build_ms']:.2f}; forest={r['forest_size']}; "
            f"parses={r['parses']})\n"
        )

    if args.check:
        baseline = load_baseline()
        # Soft: machine-variable wall-clock — warn, never fail.
        slow = compare_to_baseline(results, baseline)
        if slow:
            sys.stdout.write(
                f"\ntime over baseline +{int(TOLERANCE * 100)}% "
                "(informational — machine-variable):\n"
            )
            for rid, cur_ms, base_ms in slow:
                sys.stdout.write(f"  {rid}: {cur_ms:.2f} ms vs {base_ms:.2f} ms\n")
        # Hard: deterministic forest-size growth (over-generation).
        grown = compare_counts(
            {rid: r["forest_size"] for rid, r in results.items()}, baseline
        )
        if grown:
            sys.stderr.write("\nforest-size regressions (over-generation):\n")
            for rid, cur_n, base_n in grown:
                sys.stderr.write(f"  {rid}: {cur_n} vs {base_n}\n")
            sys.exit(1)
        sys.stdout.write("\nno forest-size regressions vs baseline\n")


if __name__ == "__main__":
    main()
