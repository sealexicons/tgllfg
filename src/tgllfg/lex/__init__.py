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
from tgllfg.lex.adapter import cache_to_morph_data
from tgllfg.lex.loader import (
    aload_morph_data_from_url,
    load_morph_data_from_url,
    resolve_morph_data,
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
    "aload_morph_data_from_url",
    "build_alembic_config",
    "build_cache",
    "cache_to_morph_data",
    "load_morph_data_from_url",
    "resolve_morph_data",
]
