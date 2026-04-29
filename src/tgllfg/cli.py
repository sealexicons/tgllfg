"""Top-level ``tgllfg`` CLI dispatcher.

Subcommands:

* ``tgllfg lex migrate`` — apply Alembic migrations to head against
  ``DATABASE_URL`` (or ``--database-url``).
* ``tgllfg lex seed`` — load the YAML seed under ``data/tgl/`` (or
  ``--data-dir``) into the Postgres lexicon. Idempotent.

Both subcommands require ``DATABASE_URL`` to be set in the environment
or passed via ``--database-url``. Commit 6 adds ``tgllfg lex import``
for CSV/TSV ingestion with explicit citation tracking.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from collections.abc import Sequence

from alembic import command

from tgllfg.lex.migrations import build_alembic_config
from tgllfg.lex.seed import seed_database


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tgllfg")
    sub = parser.add_subparsers(dest="cmd", required=True)

    lex = sub.add_parser("lex", help="lexicon database commands")
    lex.add_argument(
        "--database-url",
        default=None,
        help="Postgres connection URL (default: $DATABASE_URL)",
    )
    lex_sub = lex.add_subparsers(dest="lex_cmd", required=True)

    lex_sub.add_parser("migrate", help="apply Alembic migrations to head")

    seed = lex_sub.add_parser("seed", help="upsert the YAML seed into the database")
    seed.add_argument(
        "--data-dir",
        default=None,
        help="path to data/tgl/ (default: shipped seed)",
    )

    return parser


def _resolve_db_url(args: argparse.Namespace) -> str:
    url = args.database_url or os.environ.get("DATABASE_URL")
    if not url:
        sys.stderr.write(
            "tgllfg: DATABASE_URL is not set; pass --database-url or export it\n"
        )
        sys.exit(2)
    return url


def main(argv: Sequence[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)
    if args.cmd != "lex":
        raise AssertionError(f"unhandled cmd: {args.cmd}")  # argparse rejects others

    db_url = _resolve_db_url(args)

    if args.lex_cmd == "migrate":
        cfg = build_alembic_config(db_url)
        command.upgrade(cfg, "head")
        return

    if args.lex_cmd == "seed":
        report = asyncio.run(seed_database(db_url, args.data_dir))
        sys.stdout.write(
            f"seeded: language={report.languages} lemma={report.lemmas} "
            f"affix={report.affixes} sandhi_rule={report.sandhi_rules} "
            f"particle={report.particles} pronoun={report.pronouns} "
            f"metadata={report.metadata_keys}\n"
        )
        return

    raise AssertionError(f"unhandled lex_cmd: {args.lex_cmd}")  # argparse rejects others


if __name__ == "__main__":
    main()
