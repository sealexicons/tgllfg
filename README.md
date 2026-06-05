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

The top level holds material that belongs to neither tree — CI
configuration and the project licenses.

## License

Dual-licensed under [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE)
at your option. The SPDX expression `MIT OR Apache-2.0` appears in every
source file's header.

Copyright (c) 2025-2026 G & R Associates LLC.
