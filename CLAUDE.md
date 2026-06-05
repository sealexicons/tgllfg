<!--
Copyright (c) 2025-2026 G & R Associates LLC
SPDX-License-Identifier: MIT OR Apache-2.0
-->

# tgllfg — Claude Code project notes

Prototype LFG parser for Tagalog. Python ≥ 3.14, Hatch-managed env, pytest-xdist,
optional Postgres testcontainer. Dual-licensed MIT OR Apache-2.0. Phase 9 is
the current effort — closing the naturalistic-tier audit corpus toward the
≥80% parse-rate milestone (Wave 1+2+3 harvest, 2327 sentences).

This file is the load-on-every-session brief for working in this repo. Personal
preferences live in auto-memory; this file is project-wide.

## Build, test, lint

Always go through Hatch — never invoke `pytest` or `ruff` directly. The Hatch
aliases pass `-n auto` for xdist parallelism; raw pytest is single-threaded and
~5× slower.

| Need                                | Command                   | Notes                                       |
| ----------------------------------- | ------------------------- | ------------------------------------------- |
| Pre-commit gate (Python changes)    | `hatch run test-both`     | T1 + T2 in parallel; ~130s wall             |
| Iteration loop (most tests)         | `hatch run test-fast`     | excludes `slow`, `xslow`, `postgres`; ~125s |
| Iteration loop (T2 / slow only)     | `hatch run test-slow`     | `slow` marker only; ~10s                    |
| Combinatorial regression check      | `hatch run test-xslow`    | on-demand only; ~300s for one test          |
| Postgres-backed only                | `hatch run test-postgres` | needs Docker                                |
| Lint + type check                   | `hatch run check`         | ruff + mypy over `src/tgllfg tests`         |
| Markdown lint (docs / `README.md`)  | `markdownlint <files>`    | `/opt/homebrew/bin/markdownlint`, not npx   |

The `xslow` bucket is reserved for tests whose single-test call duration
exceeds 60s (currently one: the R&G combined-essay parse, which scales
roughly cubically with rule count due to attachment ambiguity). It's
excluded from `test-fast` / `test-slow` / `test-both` and only runs via
`test-xslow`. Run it before cutting a phase PR; for per-commit iteration
the standard gates are enough.

Bash timeouts: 180000ms is enough for `test-fast` / `test-slow` /
`test-postgres` / `check`; use 240000ms for `test-both` (typical
wall ~155–170s post-Phase-9.X); bump to 600000ms for `test-xslow`.
Don't pad to the ceiling for the standard gates.

Capture-first idiom for failing runs:
`hatch run test-fast 2>&1 | tee ./tmp/pytest.log | tail -200`. Tee then tail —
never the reverse, or you lose the full log.

Docs-only diffs: skip pytest and `hatch run check`; run `markdownlint` only.
The repo has `.markdownlint.json` (line length 120, fenced code blocks,
sibling-only duplicate headings).

## Directory map

```text
src/tgllfg/
  cfg/          c-structure CFG modules, split by area
                (clause / nominal / coordination / subordination / clitic /
                control / discourse / extraction / negation; grammar.py is
                the entry point, compile.py is the rule compiler)
  core/         pipeline.py (parse_text), feats.py (BINARY_FEATS registry),
                lexicon loaders, common.py utilities
  lex/          Postgres-backed lex models, repo, loader, alembic seed
  morph/        morphological analyzer (paradigms, affix indexing)
  parse/        chart parser
  fstruct/      f-structure + unifier (atomic-unify primitive, FU evaluator)
  lmt/          Lexical Mapping Theory (post-parse validation, PRED pruning)
  audit/        corpus-audit run / diff / baseline (Phase 12.F; backs
                the `tgllfg audit` CLI + the `scripts/audit_corpus.py` shim)
  clitics/ text/ renderers/ cli/ examples/

data/tgl/       YAML lexicon: nouns / verbs / adjectives / numerals /
                particles / pronouns / clitics / paradigms / affixes /
                adj_paradigms / sandhi / voice_aliases; lexicon/ subdir for
                per-entry files; exemplars/ tracked (Phase 12.F — fair
                use, cited); references/ gitignored (licensed PDFs)

docs/           Architecture and analytical decisions:
                analysis-choices, diagnostics, definitions, lexicon, lmt,
                coverage (incl. naturalistic-tier audit history),
                feats-binary-audit, lex-yaml-schema, fu-evaluation,
                refactor-grammar-and-roots, root-yaml-metadata

tests/tgllfg/   Per-feature test modules; share fixtures from conftest.py

scripts/        harvest_exemplars.py, audit_corpus.py, audit_diff.py,
                generate_coverage_corpus.py, check_parses_unchanged.py
```

## Plans and references

- **Plans live in `.claude/plans/`** (gitignored — personal working notes, not
  project artifacts). Root: `tgllfg-evolution.md`. Per-phase plans-of-record:
  `tgllfg-phase-<n>.md`. Cross-cutting: `tgllfg-roadmap.md`,
  `tgllfg-completed.md`, `tgllfg-out-of-scope.md`,
  `tgllfg-testing-and-risks.md`, `tgllfg-harvest-audit.md`.
- **Tagalog reference works live in `data/tgl/references/`** (gitignored —
  licensed PDFs). Hand-transcribed excerpts at
  `data/tgl/references/transcriptions/` — cite preferentially over OCR.
- **Audit harvest output**: `data/tgl/exemplars/` — tracked as of
  Phase 12.F (fair use + per-exemplar citation); the source corpus ships
  with the repo (derived `*-parse-results.jsonl` stay gitignored).
  Generated by `scripts/harvest_exemplars.py`; audited by `tgllfg audit`.

## Coding conventions

- **SPDX header on every new tracked source file.** Every git-tracked
  `*.{ini,md,py,toml,yaml,yml}` file carries the two-line header
  `Copyright (c) 2025-2026 G & R Associates LLC` /
  `SPDX-License-Identifier: MIT OR Apache-2.0` at the top. Comment
  syntax: `#` for `.py / .toml / .yaml / .ini`; `<!-- ... -->` for
  `.md`. Shebangs on `scripts/*.py` stay on line 1; the header
  follows immediately after. Empty `__init__.py` files (no exports)
  stay empty — the header convention applies only to files with
  content. The corpus generator
  (`scripts/generate_coverage_corpus.py`) emits the header on
  regeneration so `tests/tgllfg/data/coverage_corpus.yaml` stays
  headed after re-running.
- **No `from __future__ import annotations`.** Python ≥ 3.14 ships
  PEP 649 lazy annotations as the default; the future import is
  redundant and removed across the tree.
- **`__init__.py` for exports only.** Module code goes in `module/common.py` or
  `module/utils.py` and is re-exported from `__init__.py`. Don't accumulate
  logic in `__init__.py`.
- **Binary feats must be registered.** Atoms used in `[X=true]` category
  patterns must first appear in `BINARY_FEATS` in
  `src/tgllfg/core/feats.py`. Failing to register surfaces as a `ValueError`
  at compile time. Update `docs/feats-binary-audit.md` and the corresponding
  test count in `tests/tgllfg/test_phase5n_c4_feats_audit.py` whenever the set
  changes.
- **Terse feature names.** Use compact atoms like `NEG_SCOPE`, not
  `POLARITY-WIDE-SCOPE`. Underscore-separated, ≤ 2 segments, terse values.
- **Orthographic variants point at a canonical lemma** via the `LEMMA`
  feature — don't duplicate `LexicalEntries`.
- **No half-finished implementations.** Don't introduce abstractions for
  hypothetical future requirements. Don't add backwards-compatibility shims
  for code that hasn't shipped yet.

## Phase + PR workflow

- **Each phase / sub-PR merges to `main` via its own PR.** Default is
  **merge-commit, not squash** — sub-PR history is part of the phase
  narrative.
- **PR descriptions omit the "Generated with Claude Code" footer.**
- **Wave nomenclature is split**: implementation plan uses `Wave A / B / C /
  …` (alphabetic). Audit work uses `Wave 1 / 2 / 3` (numeric). Don't conflate
  in branch names.
- **Audit-before-scheduling**: sentences-closed-per-PR is the gating metric
  for construction-class sub-PRs. If the audit shows 0 direct closures, the
  candidate goes to the Phase 9+ pile, not the current phase.
- **Anti-deferral**: close pinned variants in-PR or as a named in-Phase
  follow-on. Don't quietly leave variants out of scope without a written
  successor item.
- **Post-PR cleanup is routine** — after a PR merges, switch to `main`, pull,
  and delete the local + remote branches without asking.
- **Commit messages**: long-body by default, with `hatch run test-both`
  timing (the "N passed in Xs" line) included as evidence that the
  pre-commit gate ran clean.

## Process gotchas to avoid

- **Don't background `hatch run pytest` / `hatch run check`** — they're
  foreground commands. Tail-piping them hides the exit code.
- **No `$((expr))` arithmetic or `${PIPESTATUS[*]}` expansion in Bash
  one-liners** — both trip the permission prompt. pytest already prints its
  duration; trust the summary line.
- **No heredoc-wrapped hatch invocations** — write Python diagnostics to a
  `./tmp/probe_*.py` scratch file or use `python -c "…"`.
- **Pipe pytest output into `grep` / `tee` on the first run** — never re-run
  pytest just to grep the failure list.
- **`./tmp` ops are pre-authorized.** Read / write / execute / remove
  `./tmp/*` files freely (probes, logs, head/tail/cat/grep) without asking.
  The project-local `./tmp/` directory (gitignored) supersedes system `/tmp`
  as of 2026-05-24 — survives macOS reboot, stays portable across machines.

## Where to find context this file doesn't cover

- Linguistic decisions and analyses → `docs/analysis-choices.md` and
  `docs/diagnostics.md`
- Coverage history (curated + naturalistic-tier audit roll-up) →
  `docs/coverage.md` (audit snapshots were consolidated 2026-05-22;
  prior `docs/coverage-audit-*.md` files retired into the
  Phase 9 — Naturalistic-tier audit closures section)
- f-structure feat inventory → `docs/feats-binary-audit.md`
- Current Phase 9 plan-of-record → `.claude/plans/tgllfg-phase-9.md`
- The big picture / phase roadmap → `.claude/plans/tgllfg-evolution.md` +
  `tgllfg-roadmap.md`
- License: dual MIT OR Apache-2.0 — see `LICENSE-MIT` and
  `LICENSE-APACHE` at the repo root; the SPDX expression appears in
  `pyproject.toml` and every source file's header.
