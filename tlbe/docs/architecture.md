<!-- Copyright (c) 2025-2026 G & R Associates LLC -->
<!-- SPDX-License-Identifier: MIT OR Apache-2.0 -->

# tgllfg architecture

`tgllfg` is a Lexical-Functional Grammar (LFG) parser for Tagalog. A
sentence is analysed in the classic LFG layers: a **c-structure**
(constituent tree) annotated with functional equations, projected to an
**f-structure** (attribute-value matrix) by unification, validated for
well-formedness, then mapped to an **a-structure** (argument structure)
by Lexical Mapping Theory. This is the condensed map; each layer links to
its component doc for depth.

## Monorepo topology

The repo is a two-tree monorepo (Phase 12.B):

- **`tlbe/`** — Tagalog LFG BackEnd: the parser package
  (`src/tgllfg/`), its tests, the YAML lexicon (`data/tgl/`), docs, and
  scripts. uv + poe manage the env and tasks; hatchling is the build
  backend.
- **`tlfe/`** — Tagalog LFG FrontEnd: the Vite + React web inspector
  (scaffold as of Phase 12.D; built out in Phase 14).
- **Top level** — cross-cutting plus the local dev stack (Phase 13):
  `compose.yaml` (profiles), `Dockerfile.tlbe` / `Dockerfile.tlfe`,
  `deploy/` (keycloak / postgres / observability configs), the committed
  `openapi.json` contract, CI workflows, licences, the monorepo README,
  `.claude/` (plans + memory).

Everything below lives under `tlbe/src/tgllfg/`.

## The parse pipeline

`core/pipeline.py:parse_text` orchestrates the stages; each surviving
parse is a `(c-structure, f-structure, a-structure, diagnostics)` tuple.
`parse_text_with_fragments` additionally returns partial fragments when
no complete parse exists.

```text
text
 │  text/         tokenise; normalise; merge multiword/hyphen compounds;
 │                split second-position clitics
 ▼
tokens
 │  morph/        paradigm + affix-index analysis (sandhi, prefix policy)
 ▼
 │  core/lexicon  lookup over the YAML lexicon (data/tgl/); optional
 │                Postgres-backed repo (lex/, Phase 3)
 ▼
lexical entries
 │  cfg/ + parse/ Earley chart parse against the compiled grammar,
 │                collecting LFG equations; clitics/ reorders clitics
 ▼
c-structure forest (CNode)
 │  fstruct/      two-pass equation solver over a union-find f-graph
 │                (atomic unify) + functional uncertainty
 ▼
f-structure (FStructure)
 │  fstruct/checks  completeness, coherence, subject condition
 ▼
 │  lmt/          LMT: [±r, ±o] classification, mapping principles, prune
 ▼
a-structure (AStructure)
 │  renderers/ + cli/   text / JSON; the `tgllfg` CLI
 ▼
rendered parse
```

### Tokenisation and normalisation — `text/`

`tokenizer.py`, `multiword.py`, `quotes.py`, `clitics.py`: split the
input, normalise parenthetical and quote forms, merge multiword and
hyphenated compounds, and split second-position clitic clusters.

### Morphology — `morph/`

A paradigm-driven analyser (`analyzer.py`, `paradigms.py`) with affix
indexing, sandhi (`sandhi.py`), and prefix policy (`prefix_policy.py`)
yields candidate `(lemma, features)` analyses per token. Paradigm and
affix data live in `data/tgl/`.

### Lexicon — `core/lexicon.py`, `lex/`, `data/tgl/`

The default path looks entries up from the YAML lexicon (`data/tgl/`,
loaded by `core/lexicon_loader.py`). `lex/` provides an optional
Postgres-backed repository (SQLAlchemy models, repo, seed, Alembic
migrations; Phase 3) for scale. See [`lexicon.md`](lexicon.md) and
[`lex-yaml-schema.md`](lex-yaml-schema.md).

### C-structure — `cfg/`, `parse/`

`cfg/` defines the V-initial chart grammar as `Rule`s across nine area
modules, composed by `Grammar.load_default` and compiled by
`compile.py`. `parse/earley.py` runs an Earley chart parse, building a
packed forest of `CNode` trees with their LFG equations; a per-rule
`budget` caps local-ambiguity fan-out. The full rule inventory is the
generated [`grammar.md`](grammar.md); the linguistic rationale is in
[`analysis-choices.md`](analysis-choices.md).

### F-structure — `fstruct/`

`unify.py:solve` assigns an f-graph node to each c-node and runs two
passes: defining equations grow and unify structure, constraining
equations check the solved graph. The unifier (`graph.py`) is a
union-find over an `FGraph` with **atomic** unify (snapshot / rollback,
so a failed equation never corrupts the graph). Functional uncertainty
(`fu.py`) resolves regular-path designators for long-distance
dependencies (Kaplan & Zaenen 1989). See
[`fu-evaluation.md`](fu-evaluation.md).

### Well-formedness — `fstruct/checks.py`

`lfg_well_formed` checks completeness, coherence, and the subject
condition over every PRED-bearing f-structure; uniqueness is enforced
during unification. Failures become `Diagnostic`s (`fstruct/graph.py`);
[`diagnostics.md`](diagnostics.md) covers the diagnostic policy.

### A-structure — `lmt/`

`apply_lmt_with_check` maps grammatical functions to thematic roles via
Lexical Mapping Theory: intrinsic role classification ([±r, ±o]),
mapping principles, and PRED pruning. See [`lmt.md`](lmt.md).

### Rendering — `renderers/`, `cli/`

`renderers/text.py` emits the c-/f-/a-structures as text and JSON;
`cli/main.py` is the `tgllfg` CLI (`parse`, `audit`, …). Interactive
AVM / tree / DOT rendering with reentrancy highlighting is the Phase 14
`tlfe` inspector's job.

## Core data types — `core/common.py`, `fstruct/graph.py`

- **`CNode`** — a c-structure node (`label`, `children`, `equations`).
- **`FStructure`** — a projected f-structure node (`feats`, `id`);
  reentrancy is identity on `id`.
- **`AStructure`** — argument structure (`pred`, `roles`, role→GF
  `mapping`).
- **`Diagnostic`** — a structured failure record (`kind`, `message`,
  `path`, `equation`, `cnode_label`, `detail`).

Binary f-structure features are registered in `core/feats.py` (the
inventory is audited in [`feats-binary-audit.md`](feats-binary-audit.md));
term definitions live in [`definitions.md`](definitions.md).

## Supporting infrastructure

- **Audit** — `audit/` + `tgllfg audit` run the parser over a tracked
  naturalistic corpus (`data/tgl/exemplars/`) and diff against a
  checked-in baseline; a CI matrix gates parse regressions (Phase 12.F).
  Coverage history is in [`coverage.md`](coverage.md).
- **Tests** — `tests/tgllfg/`, run via `uv run poe test-both` (xdist).
- **Build / CI** — uv + poe (Phase 12.C); path-filtered GitHub Actions
  (Phase 12.E): the static job on every push (lint + `openapi --check` +
  `bench --check-counts`), with `test-both` + audit on merge to `main`.
- **Perf** — `tgllfg bench` (`uv run poe bench`, Phase 13.J): fixed graded
  inputs, a committed baseline, and a deterministic forest-size regression
  gate (machine-independent — the CI gate) plus a soft wall-clock warning.

## REST API + dev stack (Phase 13)

`src/tgllfg/api/` is an async FastAPI service over the parser — the
contract the Phase 14 inspector consumes.

- **Routes** (`api/v1/`) — `POST /api/v1/parse` (the c-/f-/a-structures as
  a node table with `$ref` reentrancy), `GET /api/v1/lex/search` (pg_trgm
  fuzzy lookup), `POST /api/v1/audit/*` (run / poll / diff — the audit
  engine in a background subprocess). `/health` + `/ready` stay unversioned
  at the root. The schema is the committed top-level `openapi.json`
  (regenerated + sync-gated by `tgllfg openapi`).
- **DI + DTOs** (`api/deps.py`, Pydantic 2 models) — request-scoped async
  DB sessions, the `Principal` + `require_role` gates, `Settings`.
- **Auth** (`api/auth.py`) — `AUTH_MODE=anonymous` (open, the dev default)
  or `keycloak` (local JWT verification: cached JWKS via httpx2, RS256 +
  iss/aud/exp via pyjwt; role gates `parser:read` / `parser:write` /
  `lex:read`).
- **Observability** (`api/telemetry.py`) — env-gated OTel tracing (no
  endpoint → no-op) + structlog; gross spans segment compute (parse /
  audit) from DB I/O (SQLAlchemy auto-instrumentation).
- **CLI** (`cli/`) — `tgllfg serve` (uvicorn), `tgllfg openapi`
  (generate / check the contract), `tgllfg bench` (the perf gate).

The dev stack runs on Docker Desktop: two multi-stage non-root images
(`Dockerfile.tlbe` / `Dockerfile.tlfe`) and a top-level `compose.yaml` with
three profiles — **default** (Postgres + migrate/seed + tlbe + tlfe,
health-gated, anonymous), **`auth`** (+ Keycloak), **`observability`**
(+ Alloy → Tempo / Prometheus / Loki + Grafana). See the monorepo
`README.md` for the run commands.

## Web inspector (`tlfe`, Phase 14)

`tlfe/` is the single-page parse inspector (Vite + React 19 + TypeScript +
Tailwind + Radix) that consumes the Phase 13 API. The data layer is TanStack
Query + axios over a typed client generated from the committed `openapi.json`
by `@hey-api/openapi-ts` (committed under `tlfe/src/api/client/`, sync-gated
in CI); thin `useParse` / `useLexSearch` / audit hooks wrap the generated
helpers.

It renders the three projections of a parse plus its diagnostics:

- **c-structure** — an SVG tidy-tree (`views/cstructureLayout.ts` lays it out
  in a single bottom-up pass; `CStructureView` draws it).
- **f-structure** — a nested AVM (`FStructureView`); reentrant
  (structure-shared) nodes carry hoverable id tags.
- **a-structure** — the PRED + LMT role → GF mapping; **diagnostics** — the
  per-fragment failure detail (kind, message, blocking flag, and the
  `cnode_label` locating the failing equation in the c-structure).

The headline view is **C / F** (`CFStructureView`): the tree and AVM side by
side, linked by the **φ correspondence** the `/parse` endpoint returns
(c-node id → f-node id). The parser computes φ in `solve()` for ordinary
parses and composes it from the halves for glued split-path parses (see
*F-structure* above and `core/pipeline.py`); the inspector inverts it to
cross-highlight — hovering a c-node lights the f-node it projects to and all
co-projecting c-nodes, hovering an f-node lights every c-node projecting to
it.

The image (`Dockerfile.tlfe`) is a multi-stage build serving the static
bundle behind non-root nginx with SPA history fallback, a `/api` reverse
proxy to `tlbe`, immutable caching on hashed assets, and gzip; it runs as the
`tlfe` compose service.

## The road ahead

- **Phase 15** — production deployment: a prod compose, a Helm chart + k8s
  templates (initial single-node cluster), an arm64 `tlfe` image, and a
  redis-backed compiled-grammar cache.
