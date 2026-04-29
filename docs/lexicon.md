# Lexicon (Phase 3)

The Phase 3 lexicon is a Postgres 17 database authored from two
sources:

* **Project-owned YAML** under `data/tgl/`: roots, paradigms,
  particles, pronouns, sandhi rules, affix inventory. Loaded into
  the DB by `tgllfg lex seed`. The YAML is the source of truth for
  these tables; re-seeding overwrites them.
* **External CSV imports** with citation tracking, e.g. public-domain
  wordlists or OCR'd dictionaries. Loaded by `tgllfg lex import`,
  attributed to a `source` row. Idempotent UPSERT on
  `(language_id, citation_form, pos)`.

## Components

| Module                    | Purpose                                                          |
|---------------------------|------------------------------------------------------------------|
| `alembic/`                | Schema migrations. Migration 0001 is the §6.2 baseline; 0002 adds `paradigm_cell` and `lemma.transitivity` / `lemma.affix_class`. |
| `src/tgllfg/lex/models.py`     | SQLAlchemy 2.x ORM mirroring the migrations.               |
| `src/tgllfg/lex/cache.py`      | Frozen-dataclass `LexCache` + `build_cache(session)`. Parser-facing, no SQLAlchemy types leak. |
| `src/tgllfg/lex/repo.py`       | `AsyncLexRepository` for ad-hoc reads.                     |
| `src/tgllfg/lex/seed.py`       | YAML → DB upsert (whole-tree, idempotent).                 |
| `src/tgllfg/lex/import_csv.py` | CSV → DB import with `source` attribution.                 |
| `src/tgllfg/lex/adapter.py`    | `cache_to_morph_data(cache)` → parser-shape `MorphData`.   |
| `src/tgllfg/lex/loader.py`     | `resolve_morph_data()` backend switch + data-version gate. |
| `src/tgllfg/cli.py`            | `tgllfg` CLI entry point.                                  |

## CLI

```sh
# Apply pending migrations.
tgllfg lex migrate --database-url postgresql://user:pw@host/tgl

# Load the project YAML seed (idempotent).
tgllfg lex seed

# Import an external CSV with explicit source.
tgllfg lex import \
    --source-short-name Kaufman1939 \
    --source-full-citation "Kaufman 1939, Visayan-English Dictionary" \
    /path/to/lemmas.csv
```

`DATABASE_URL` is read from the environment when `--database-url` is
omitted. CSV format for `lex import`:

```csv
citation_form,pos,gloss,transitivity,affix_class
halimbawa,NOUN,example,,
linis,VERB,clean,TR,mag;maka
```

`affix_class` is a semicolon-delimited list (matches the
`lemma.affix_class` JSONB array). `transitivity`, `gloss`, and
`affix_class` may be empty.

## Test harness

Lexicon tests run against a real Postgres 17 instance, started on demand
by [`testcontainers-python`][tc] from the `postgres:17` Docker image.
Async tests use SQLAlchemy 2.x's `asyncio` extension (`asyncpg` driver).
Per-test isolation is provided by a transactional fixture (`pg_session`)
that wraps each test in a transaction and rolls back on exit — schema
creation amortizes across the session.

[tc]: https://testcontainers-python.readthedocs.io/

### Why testcontainers (not `pytest-postgresql`)

The plan §6.5 lists both options. We chose `testcontainers` because:

- The user already runs Docker Desktop, so there is no extra system
  dependency on `pg_ctl` or a host Postgres install.
- The same image (`postgres:17`) runs in CI, in dev, and in tests — no
  drift between a host-installed Postgres and the deployment image.
- Extension availability (`pg_trgm`, `pgcrypto`) is determined by the
  image rather than the host package set, eliminating a class of
  "works-on-my-machine" failures.

### Marker

All Postgres-backed tests are marked `@pytest.mark.postgres`. To skip
them locally when Docker isn't running:

```sh
pytest -m "not postgres"
```

## Backend selection

The parser picks its lexicon backend from `TGLLFG_LEX_BACKEND`:

| Backend          | Source                                  | Default? |
|------------------|-----------------------------------------|----------|
| `yaml` (default) | `data/tgl/*.yaml`                       | yes      |
| `db`             | Postgres at `DATABASE_URL`              | no       |

`Analyzer.from_default()` honors this. The demo and offline contexts
keep working without any database (`TGLLFG_LEX_BACKEND` unset →
`yaml`). When `TGLLFG_LEX_BACKEND=db`, `DATABASE_URL` is required.

## Data-version compatibility

`tgllfg lex seed` writes a `data_version` row into `lex_metadata`. At
parser startup the DB-backed loader checks this against
`MIN_COMPATIBLE_DATA_VERSION` (defined in `src/tgllfg/lex/loader.py`).
If the DB's version is older than the parser requires, the loader
raises `IncompatibleDataVersionError` with a recovery hint
(`re-run \`tgllfg lex seed\``). The check fires only on the `db`
backend; the YAML path has no version concept.

When introducing a breaking change to the seed shape:

1. Bump `DATA_VERSION` in `src/tgllfg/lex/seed.py`.
2. Bump `MIN_COMPATIBLE_DATA_VERSION` in `src/tgllfg/lex/loader.py`
   to match.
3. Re-run `tgllfg lex seed` to update existing databases.

## Adding a lemma end-to-end

The path you take depends on whether the lemma is project-owned (the
team is the authority for the data) or externally sourced (citations
matter).

**Project-owned (the common case):** add to the YAML, re-seed.

```yaml
# data/tgl/roots.yaml
- citation: linis
  pos: VERB
  gloss: clean
  transitivity: TR
  affix_class: [mag, maka]
```

```sh
tgllfg lex seed
```

**Externally sourced (with citation):** drop a CSV, run import.

```sh
echo 'citation_form,pos,gloss,transitivity,affix_class
linis,VERB,clean,TR,mag;maka' > /tmp/external.csv

tgllfg lex import \
    --source-short-name Kaufman1939 \
    --source-full-citation "Kaufman, J. 1939. Visayan-English Dictionary" \
    /tmp/external.csv
```

Either way, the lemma becomes visible to the parser on the next
`Analyzer.from_default()` call (no in-process cache invalidation
needed — the cache is built fresh on each load).

## Schema overview

See `alembic/versions/0001_baseline.py` and `0002_paradigm_cell.py`
for the canonical specification. Tables: `language`, `source`,
`lemma`, `lex_entry`, `affix`, `paradigm`, `paradigm_slot`,
`paradigm_cell`, `sandhi_rule`, `particle`, `pronoun`, `example`,
`voice_alias`, `lex_metadata`. Plan §6.2 has the rationale for each;
`docs/analysis-choices.md` records the deviations made when
finalising the schema.
