# Lexicon (Phase 3)

This document is the developer reference for the Postgres-backed lexicon
introduced in Phase 3 of the evolution plan. It will grow alongside the
phase; this initial revision records the test-harness choices made in
Commit 1 so later commits don't relitigate them.

## Test harness

Lexicon tests run against a real Postgres 17 instance, started on demand
by [`testcontainers-python`][tc] from the `postgres:17` Docker image.
Async tests use SQLAlchemy 2.x's `asyncio` extension (`asyncpg` driver).
Per-test isolation is provided by a transactional fixture
(`pg_session`) that wraps each test in a transaction and rolls back on
exit — schema creation amortizes across the session.

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

## Schema

Defined by the Alembic baseline migration (lands in Commit 2). See
plan §6.2 for the canonical specification.
