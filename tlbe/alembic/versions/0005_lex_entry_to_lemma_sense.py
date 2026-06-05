# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Drop lex_entry.lemma_id; enforce NOT NULL on lemma_sense_id.

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-11

Phase 5n.C.4 Commit 9: completes the ``lex_entry`` FK migration
started in 0004. After this commit:

* ``lex_entry.lemma_sense_id`` is NOT NULL and the only FK from
  lex_entry into the lemma/sense hierarchy.
* ``lex_entry.lemma_id`` is gone (was kept as a dual-FK during the
  additive window).

Pre-condition: every existing ``lex_entry`` row already has its
``lemma_sense_id`` populated (the 0004 backfill set every existing
row to its lemma's sense_index=0 row).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0005"
down_revision: str | Sequence[str] | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("lex_entry", "lemma_sense_id", nullable=False)
    op.drop_index("ix_lex_entry_lemma", table_name="lex_entry")
    op.drop_constraint("lex_entry_lemma_id_fkey", "lex_entry", type_="foreignkey")
    op.drop_column("lex_entry", "lemma_id")


def downgrade() -> None:
    op.add_column(
        "lex_entry",
        sa.Column(
            "lemma_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lemma.id"),
            nullable=True,
        ),
    )
    op.execute(
        "UPDATE lex_entry SET lemma_id = ls.lemma_id "
        "FROM lemma_sense ls "
        "WHERE ls.id = lex_entry.lemma_sense_id"
    )
    op.alter_column("lex_entry", "lemma_id", nullable=False)
    op.create_index("ix_lex_entry_lemma", "lex_entry", ["lemma_id"])
    op.alter_column("lex_entry", "lemma_sense_id", nullable=True)
