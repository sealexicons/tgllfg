"""Postgres-backed lexicon backend (plan §6).

Phase 3 module hosting the SQLAlchemy models, async repository,
in-memory cache view, and Alembic migration helpers. This file holds
re-exports only; implementation lives in sibling modules.
"""

from tgllfg.lex.migrations import build_alembic_config

__all__ = ["build_alembic_config"]
