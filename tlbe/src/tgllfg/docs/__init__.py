# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Documentation generators.

Tools that emit the tracked reference docs under ``tlbe/docs/`` from the
source of truth, kept in sync by tests / the ``tgllfg docs`` CLI.
Currently the c-structure grammar reference
(:mod:`tgllfg.docs.grammar`); a home for future docs tooling.
"""

from .grammar import GRAMMAR_DOC_PATH, render_grammar_doc, write_grammar_doc

__all__ = ["GRAMMAR_DOC_PATH", "render_grammar_doc", "write_grammar_doc"]
