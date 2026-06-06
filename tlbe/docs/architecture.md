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
- **Top level** — cross-cutting only: CI workflows, licences, the
  monorepo README, `.claude/` (plans + memory).

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
  (Phase 12.E): linting on every push, `test-both` + audit on merge to
  `main`.

## The road ahead

- **Phase 13** — an async FastAPI service under `src/tgllfg/api/`
  exposing `/parse`, `/audit/*`, and `/lex/search` (the contract the
  inspector consumes).
- **Phase 14** — the `tlfe` web inspector, rendering the c-/f-/a-
  structures with cross-highlighting against the Phase 13 API.
