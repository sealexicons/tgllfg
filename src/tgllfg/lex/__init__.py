"""Postgres-backed lexicon backend (plan §6).

Phase 3 module hosting the SQLAlchemy models, async repository,
in-memory cache view, and Alembic migration helpers. This file holds
re-exports only; implementation lives in sibling modules.
"""

from tgllfg.lex.cache import (
    AffixEntry,
    LanguageEntry,
    LemmaEntry,
    LexCache,
    LexEntryRow,
    ParadigmCellEntry,
    ParadigmEntry,
    ParadigmSlotEntry,
    ParticleEntry,
    PronounEntry,
    SandhiRuleEntry,
    SourceEntry,
    VoiceAliasEntry,
    build_cache,
)
from tgllfg.lex.migrations import build_alembic_config
from tgllfg.lex.repo import AsyncLexRepository

__all__ = [
    "AffixEntry",
    "AsyncLexRepository",
    "LanguageEntry",
    "LemmaEntry",
    "LexCache",
    "LexEntryRow",
    "ParadigmCellEntry",
    "ParadigmEntry",
    "ParadigmSlotEntry",
    "ParticleEntry",
    "PronounEntry",
    "SandhiRuleEntry",
    "SourceEntry",
    "VoiceAliasEntry",
    "build_alembic_config",
    "build_cache",
]
