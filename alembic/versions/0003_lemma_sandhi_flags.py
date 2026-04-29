"""Per-root sandhi flags on lemma.

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-30

Phase 2C adds opt-in phonological rules (currently ``d_to_r`` and
``high_vowel_deletion``) declared per root in
``data/tgl/roots.yaml`` as a list of strings. ``lemma.sandhi_flags``
holds those strings as a JSONB array so the DB-backed loader
preserves them when projecting :class:`LexCache` →
:class:`MorphData`.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0003"
down_revision: str | Sequence[str] | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "lemma",
        sa.Column(
            "sandhi_flags",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column("lemma", "sandhi_flags")
