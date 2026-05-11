"""LemmaSense child table for per-sense feats (Phase 5n.C.4 L34).

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-10

Phase 5n.C.4 Commit 1: Introduce ``lemma_sense`` as a child of
``lemma``. One ``lemma`` row per ``(language_id, citation_form, pos)``;
one ``lemma_sense`` row per linguistically distinct sense of that
lemma, carrying its own ``feats`` JSONB. Closes the Phase 5f
``kuwarto`` (room vs. fraction) deferral in §18 L34: the prior
``_upsert_lemmas`` workaround at ``seed.py`` dropped the second
sense because the schema couldn't carry per-sense ``feats``.

The migration is **strictly additive** — no existing columns are
dropped here and no NOT NULL is enforced on the new
``lex_entry.lemma_sense_id`` FK. The dual writes through both
``lex_entry.lemma_id`` and ``lex_entry.lemma_sense_id`` survive
until Commit 2 rewrites the seed / cache / adapter and a follow-on
migration (0005) drops ``lex_entry.lemma_id`` + enforces
``NOT NULL`` on ``lemma_sense_id``.

Backfill: one synthetic sense per existing lemma at
``sense_index = 0`` with ``feats = '{}'::jsonb``; existing lex_entry
rows point at that sense.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0004"
down_revision: str | Sequence[str] | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "lemma_sense",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "lemma_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lemma.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sense_index", sa.Integer, nullable=False),
        sa.Column(
            "feats",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("gloss", sa.Text),
        sa.Column("source_ref", sa.Text),
        sa.Column("notes", sa.Text),
        sa.UniqueConstraint(
            "lemma_id", "sense_index", name="uq_lemma_sense_lemma_index"
        ),
    )
    op.create_index("ix_lemma_sense_lemma", "lemma_sense", ["lemma_id"])

    op.execute(
        "INSERT INTO lemma_sense (lemma_id, sense_index, feats) "
        "SELECT id, 0, '{}'::jsonb FROM lemma"
    )

    op.add_column(
        "lex_entry",
        sa.Column(
            "lemma_sense_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lemma_sense.id"),
            nullable=True,
        ),
    )
    op.create_index("ix_lex_entry_lemma_sense", "lex_entry", ["lemma_sense_id"])

    op.execute(
        "UPDATE lex_entry SET lemma_sense_id = ls.id "
        "FROM lemma_sense ls "
        "WHERE ls.lemma_id = lex_entry.lemma_id "
        "AND ls.sense_index = 0"
    )


def downgrade() -> None:
    op.drop_index("ix_lex_entry_lemma_sense", table_name="lex_entry")
    op.drop_column("lex_entry", "lemma_sense_id")
    op.drop_index("ix_lemma_sense_lemma", table_name="lemma_sense")
    op.drop_table("lemma_sense")
