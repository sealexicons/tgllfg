"""Paradigm cells and root-level morph metadata on lemma.

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-29

§6.2's morphology tables (``affix`` + ``paradigm`` + ``paradigm_slot``)
describe affix inventories at the abstract level. The seed YAML
``paradigms.yaml`` describes paradigm cells *operationally* — an
ordered list of CV-redup / infix / suffix / prefix / nasal-substitute
operations per (voice, aspect, mood) cell. Those are at different
levels of description and don't reduce to each other; this revision
adds a dedicated ``paradigm_cell`` table for the operational view.

Two lemma columns are also added to carry root-level lexical
properties read by the analyzer: ``transitivity`` (TR / INTR /
empty for non-verbs) and ``affix_class`` (a JSONB list naming the
paradigm patterns the root participates in: um, mag, mang, maka,
in_oblig, an_oblig, i_oblig). §6.2 documents these as living in
``lex_entry.morph_constraints``, but lex_entry also requires
``pred_template`` / ``a_structure`` / ``intrinsic_classification``
which we don't have authored data for at root scope. Putting them on
``lemma`` keeps the lex_entry table reserved for properly authored
LFG predicates (Phase 4+).

The deviation from §6.2 is recorded in ``docs/analysis-choices.md``.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0002"
down_revision: str | Sequence[str] | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "lemma",
        sa.Column(
            "transitivity",
            sa.Text,
            nullable=False,
            server_default=sa.text("''"),
        ),
    )
    op.add_column(
        "lemma",
        sa.Column(
            "affix_class",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )

    op.create_table(
        "paradigm_cell",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "language_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("language.id"),
            nullable=False,
        ),
        sa.Column("voice", sa.Text, nullable=False),
        sa.Column("aspect", sa.Text, nullable=False),
        sa.Column("mood", sa.Text, nullable=False, server_default=sa.text("'IND'")),
        sa.Column(
            "transitivity",
            sa.Text,
            nullable=False,
            server_default=sa.text("''"),
        ),
        sa.Column(
            "affix_class",
            sa.Text,
            nullable=False,
            server_default=sa.text("''"),
        ),
        sa.Column("operations", postgresql.JSONB, nullable=False),
        sa.Column("ordering", sa.Integer, nullable=False),
        sa.Column("notes", sa.Text),
    )
    op.create_index("ix_paradigm_cell_lang", "paradigm_cell", ["language_id"])


def downgrade() -> None:
    op.drop_index("ix_paradigm_cell_lang", table_name="paradigm_cell")
    op.drop_table("paradigm_cell")
    op.drop_column("lemma", "affix_class")
    op.drop_column("lemma", "transitivity")
