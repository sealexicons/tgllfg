# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Alembic config helper for tests and CLI use.

Builds an in-memory ``alembic.config.Config`` pointing at the project's
``alembic.ini`` and ``alembic/`` directory, with ``sqlalchemy.url``
overridden to the caller's value. Used by the test harness (against the
testcontainer URL) and by the eventual ``tgllfg lex migrate`` CLI
subcommand (against ``DATABASE_URL``).
"""

from pathlib import Path

from alembic.config import Config

_REPO_ROOT = Path(__file__).resolve().parents[3]
_ALEMBIC_INI = _REPO_ROOT / "alembic.ini"
_ALEMBIC_DIR = _REPO_ROOT / "alembic"


def build_alembic_config(database_url: str) -> Config:
    """Return an Alembic ``Config`` pointing at this project's
    ``alembic/`` tree, with ``sqlalchemy.url`` set to ``database_url``.
    """
    cfg = Config(str(_ALEMBIC_INI))
    cfg.set_main_option("script_location", str(_ALEMBIC_DIR))
    cfg.set_main_option("sqlalchemy.url", database_url)
    return cfg
