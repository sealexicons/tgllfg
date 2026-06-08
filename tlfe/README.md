<!--
Copyright (c) 2025-2026 G & R Associates LLC
SPDX-License-Identifier: MIT OR Apache-2.0
-->

# tlfe — Tagalog LFG FrontEnd

The web inspector for the [`tlbe`](../tlbe/) Tagalog LFG parser: a
single-page explorer that parses a Tagalog sentence and renders its
c-structure, f-structure, and a-structure, with the c-structure tree and
f-structure AVM cross-highlighted by the φ correspondence.

**Status: built (Phase 14).** Enter a sentence and press Parse to inspect it:

- **C / F** — the c-structure tree (SVG) and the f-structure AVM side by
  side, linked by the φ correspondence the API returns: hovering a c-node
  highlights the f-node it projects to (and every co-projecting c-node);
  hovering an f-node highlights every c-node that projects to it. Reentrant
  (structure-shared) f-nodes are tagged and cross-highlight on hover.
- **A-structure** — the predicate's argument list and its LMT role → GF
  mapping.
- **Diagnostics** — for a failed parse, the per-fragment diagnostics (kind,
  message, blocking flag, and the c-structure label the failing equation
  came from).
- **JSON** — the raw `ParseResponse` payload.

When a sentence has more than one complete parse, a selector switches the
c-/f-/a- views between them.

## Stack

- [Vite](https://vite.dev/) 8 + [React](https://react.dev/) 19 + TypeScript
- [Tailwind CSS](https://tailwindcss.com/) 4 (via `@tailwindcss/vite`)
- [Radix UI](https://www.radix-ui.com/) primitives — accessible tabs and the
  like; the tree / AVM / cross-highlight renderers are custom
- Data layer: [TanStack Query](https://tanstack.com/query) + axios over a
  typed client generated from the committed root `openapi.json` by
  [`@hey-api/openapi-ts`](https://heyapi.dev/) (`npm run gen:api`)
- [Vitest](https://vitest.dev/) + Testing Library; ESLint + Prettier

## Development

Requires Node ≥ 24 (pinned in `.node-version`, which CI reads) and npm.

```sh
npm install        # install dependencies
npm run dev        # Vite dev server (proxies /api → http://127.0.0.1:8000)
npm run build      # tsc -b + production build → dist/
npm run lint       # eslint
npm run typecheck  # tsc -b (no emit)
npm test           # vitest (run mode)
npm run format     # prettier --write
npm run gen:api    # regenerate src/api/client/ from ../openapi.json
```

The generated `src/api/client/` is **committed** (so checkout, CI, and the
Docker build need no codegen step) and is regenerated with `npm run gen:api`
after any contract change. CI's `static` job runs lint + prettier + typecheck
and verifies the generated client is in sync with `openapi.json`; the `test`
job runs the build + vitest.

## Deployment

`docker build -f ../Dockerfile.tlfe -t tlfe .` builds a multi-stage,
non-root nginx image serving the static bundle with SPA history fallback, a
`/api` reverse proxy to `tlbe`, immutable caching on the content-hashed
assets, and gzip. It runs as the `tlfe` service in the top-level
`compose.yaml`; see the monorepo [`README.md`](../README.md) for the dev
stack.

## License

Dual-licensed under [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE)
at your option.

Copyright (c) 2025-2026 G & R Associates LLC.
