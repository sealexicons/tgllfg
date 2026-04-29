"""SQLAlchemy 2.x ORM models for the §6.2 lexicon schema.

These are authored *to match* the hand-written Alembic baseline
(``alembic/versions/0001_baseline.py``); the migration is the source
of truth, not the models. ``Base.metadata`` deliberately excludes the
``alembic_version`` table that Alembic manages on its own.

Naming: the plan's ``metadata`` table is ``lex_metadata`` here to
avoid collision with ``Base.metadata``. The plan's ``data_version``
field is the row keyed by ``data_version`` in ``lex_metadata.value``.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def _uuid_pk() -> Mapped[UUID]:
    return mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=None)


class Language(Base):
    __tablename__ = "language"
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    iso_code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class Source(Base):
    __tablename__ = "source"
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    short_name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    full_citation: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class Lemma(Base):
    __tablename__ = "lemma"
    __table_args__ = (
        UniqueConstraint("language_id", "citation_form", "pos", name="uq_lemma_lang_form_pos"),
    )
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    language_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("language.id"), nullable=False
    )
    citation_form: Mapped[str] = mapped_column(Text, nullable=False)
    pos: Mapped[str] = mapped_column(Text, nullable=False)
    gloss: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    source_ref: Mapped[str | None] = mapped_column(Text)


class LexEntry(Base):
    __tablename__ = "lex_entry"
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    lemma_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("lemma.id"), nullable=False
    )
    pred_template: Mapped[str] = mapped_column(Text, nullable=False)
    a_structure: Mapped[Any] = mapped_column(JSONB, nullable=False)
    morph_constraints: Mapped[Any] = mapped_column(JSONB, nullable=False)
    intrinsic_classification: Mapped[Any] = mapped_column(JSONB, nullable=False)
    default_mapping: Mapped[Any | None] = mapped_column(JSONB)
    notes: Mapped[str | None] = mapped_column(Text)


class Affix(Base):
    __tablename__ = "affix"
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    language_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("language.id"), nullable=False
    )
    shape: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    features: Mapped[Any] = mapped_column(JSONB, nullable=False)
    position: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)


class Paradigm(Base):
    __tablename__ = "paradigm"
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    language_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("language.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)


class ParadigmSlot(Base):
    __tablename__ = "paradigm_slot"
    paradigm_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("paradigm.id", ondelete="CASCADE"),
        primary_key=True,
    )
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    affix_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("affix.id"), nullable=False
    )


class SandhiRule(Base):
    __tablename__ = "sandhi_rule"
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    language_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("language.id"), nullable=False
    )
    pattern: Mapped[str] = mapped_column(Text, nullable=False)
    replacement: Mapped[str] = mapped_column(Text, nullable=False)
    conditions: Mapped[Any] = mapped_column(JSONB, nullable=False)
    ordering: Mapped[int] = mapped_column(Integer, nullable=False)


class Particle(Base):
    __tablename__ = "particle"
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    language_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("language.id"), nullable=False
    )
    surface: Mapped[str] = mapped_column(Text, nullable=False)
    pos: Mapped[str] = mapped_column(Text, nullable=False)
    features: Mapped[Any] = mapped_column(JSONB, nullable=False)
    is_clitic: Mapped[bool] = mapped_column(Boolean, nullable=False)
    clitic_class: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)


class Pronoun(Base):
    __tablename__ = "pronoun"
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    language_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("language.id"), nullable=False
    )
    surface: Mapped[str] = mapped_column(Text, nullable=False)
    features: Mapped[Any] = mapped_column(JSONB, nullable=False)
    is_clitic: Mapped[bool] = mapped_column(Boolean, nullable=False)


class Example(Base):
    __tablename__ = "example"
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    language_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("language.id"), nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source_ref: Mapped[str | None] = mapped_column(Text)
    expected_c: Mapped[Any | None] = mapped_column(JSONB)
    expected_f: Mapped[Any | None] = mapped_column(JSONB)
    expected_a: Mapped[Any | None] = mapped_column(JSONB)
    notes: Mapped[str | None] = mapped_column(Text)


class VoiceAlias(Base):
    __tablename__ = "voice_alias"
    __table_args__ = (
        UniqueConstraint("language_id", "label", name="uq_voice_alias_lang_label"),
    )
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    language_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("language.id"), nullable=False
    )
    label: Mapped[str] = mapped_column(Text, nullable=False)
    voice: Mapped[str] = mapped_column(Text, nullable=False)
    appl: Mapped[str | None] = mapped_column(Text)
    caus: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)


class LexMetadata(Base):
    __tablename__ = "lex_metadata"
    key: Mapped[str] = mapped_column(Text, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)


__all__ = [
    "Affix",
    "Base",
    "Example",
    "Language",
    "Lemma",
    "LexEntry",
    "LexMetadata",
    "Paradigm",
    "ParadigmSlot",
    "Particle",
    "Pronoun",
    "SandhiRule",
    "Source",
    "VoiceAlias",
]
