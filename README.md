<!--
Copyright (c) 2025-2026 G & R Associates LLC
SPDX-License-Identifier: MIT OR Apache-2.0
-->

# tgllfg — monorepo

A prototype LFG (Lexical-Functional Grammar) parser for Tagalog, plus
its web inspector. Two top-level trees:

- **[`tlbe/`](tlbe/)** — *Tagalog LFG BackEnd*: the Python parser
  (lexicon → morphology → chart parser → unifier → LMT) and the
  `tgllfg` CLI. See [`tlbe/README.md`](tlbe/README.md).
- **[`tlfe/`](tlfe/)** — *Tagalog LFG FrontEnd*: the web inspector
  (Vite + React). See [`tlfe/README.md`](tlfe/README.md).

The top level holds material that belongs to neither tree — the local dev
stack (`compose.yaml`, `Dockerfile.tlbe` / `Dockerfile.tlfe`, `deploy/`,
`.env.template`), the committed `openapi.json` API contract, CI
configuration, and the project licenses.

## Running the dev stack

The whole stack runs on Docker Desktop via the top-level `compose.yaml`:

- **`docker compose up`** — the lean default: Postgres, the migrate/seed
  jobs, the API (`tlbe`), and the web frontend (`tlfe`, nginx), in
  **anonymous** auth mode. API at `http://localhost:8000` (OpenAPI at
  `/api/docs`); frontend at `http://localhost:8080`.
- **`AUTH_MODE=keycloak docker compose --profile auth up`** — adds Keycloak
  (realm imported on start; dev login `dev` / `dev`) and enforces JWT auth
  with role gates on the API.
- **observability** — set `OTEL_EXPORTER_OTLP_ENDPOINT=http://alloy:4317`
  and run `docker compose --profile observability up` to add the Grafana
  LGTM stack (Alloy → Tempo / Prometheus / Loki + Grafana at
  `http://localhost:3000`).

Copy `.env.template` to `.env` to override defaults (ports, credentials).
The service topology is in
[`tlbe/docs/architecture.md`](tlbe/docs/architecture.md).

## License

Dual-licensed under [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE)
at your option. The SPDX expression `MIT OR Apache-2.0` appears in every
source file's header.

Copyright (c) 2025-2026 G & R Associates LLC.
