<!--
Copyright (c) 2025-2026 G & R Associates LLC
SPDX-License-Identifier: MIT OR Apache-2.0
-->

# tlfe — Tagalog LFG FrontEnd

The web inspector for the [`tlbe`](../tlbe/) Tagalog LFG parser: a
single-page explorer that renders a parse's c-structure, f-structure,
and a-structure side by side, with reentrancy hover-highlighting.

**Status: scaffold (Phase 12.D).** The Vite + React + TypeScript skeleton
is in place — it builds, lints, typechecks, and renders one placeholder
view (a stubbed parse panel with c-structure / f-structure / JSON tabs).
There is no parsing logic yet: the inspector is built out in Phase 14
against the Phase 13 REST API.

## Stack

- [Vite](https://vite.dev/) 8 + [React](https://react.dev/) 19 + TypeScript
- [Tailwind CSS](https://tailwindcss.com/) 4 (via `@tailwindcss/vite`)
- [Radix UI](https://www.radix-ui.com/) primitives — accessible tabs,
  tooltips, and the like; the tree / AVM renderers are custom
- [Vitest](https://vitest.dev/) + Testing Library; ESLint + Prettier

## Development

Requires Node ≥ 20.19 (CI and local dev target Node 24) and npm.

```sh
npm install        # install dependencies
npm run dev        # Vite dev server
npm run build      # tsc -b + production build → dist/
npm run lint       # eslint
npm run typecheck  # tsc -b (no emit)
npm test           # vitest (run mode)
npm run format     # prettier --write
```

All four CI gates (lint, typecheck, build, test) mirror these scripts.

## License

Dual-licensed under [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE)
at your option.

Copyright (c) 2025-2026 G & R Associates LLC.
