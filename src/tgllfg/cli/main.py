"""Top-level ``tgllfg`` CLI dispatcher.

Subcommands:

* ``tgllfg lex migrate`` — apply Alembic migrations to head against
  ``DATABASE_URL`` (or ``--database-url``).
* ``tgllfg lex seed`` — load the YAML seed under ``data/tgl/`` (or
  ``--data-dir``) into the Postgres lexicon. Idempotent.
* ``tgllfg lex import`` — import a CSV of lemma data with citation.
* ``tgllfg parse`` — parse a Tagalog sentence and print its
  c-/f-structure summary. With ``--strict`` it suppresses fragment
  output on full-parse failure (Phase 4 §7.9).
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from collections.abc import Sequence

from pathlib import Path

from alembic import command

from tgllfg.lex.import_csv import import_lemmas_csv
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

    imp = lex_sub.add_parser(
        "import",
        help="import a CSV of additive lemma data with source citation",
    )
    imp.add_argument("path", help="path to a CSV file with the lemma rows")
    imp.add_argument(
        "--source-short-name",
        required=True,
        help="short_name to record in the `source` table (e.g. 'Kaufman1939')",
    )
    imp.add_argument(
        "--source-full-citation",
        required=True,
        help="full bibliographic citation for the source",
    )

    parse_p = sub.add_parser("parse", help="parse a Tagalog sentence")
    parse_p.add_argument("sentence", help="the sentence to parse")
    parse_p.add_argument(
        "--strict",
        action="store_true",
        help=(
            "suppress fragment output on full-parse failure "
            "(default: emit fragments for debugging; see Phase 4 §7.9)"
        ),
    )
    parse_p.add_argument(
        "--n-best",
        type=int,
        default=5,
        help="cap on the number of complete parses returned (default: 5)",
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

    if args.cmd == "parse":
        _cmd_parse(args)
        return

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
            f"affix={report.affixes} paradigm_cell={report.paradigm_cells} "
            f"sandhi_rule={report.sandhi_rules} particle={report.particles} "
            f"pronoun={report.pronouns} voice_alias={report.voice_aliases} "
            f"metadata={report.metadata_keys}\n"
        )
        return

    if args.lex_cmd == "import":
        import_report = asyncio.run(
            import_lemmas_csv(
                db_url,
                Path(args.path),
                source_short_name=args.source_short_name,
                source_full_citation=args.source_full_citation,
            )
        )
        sys.stdout.write(
            f"imported: rows_read={import_report.rows_read} "
            f"rows_upserted={import_report.rows_upserted} "
            f"source={import_report.source_short_name}\n"
        )
        return

    raise AssertionError(f"unhandled lex_cmd: {args.lex_cmd}")  # argparse rejects others


def _cmd_parse(args: argparse.Namespace) -> None:
    """Phase 4 §7.9: parse a sentence and print a summary.

    Default mode emits a complete parse if found; otherwise emits
    fragment summaries to help debug the failure. ``--strict``
    suppresses fragment output (empty stdout, exit 0).
    """
    from tgllfg.core.pipeline import parse_text_with_fragments

    result = parse_text_with_fragments(args.sentence, n_best=args.n_best)

    if result.parses:
        for i, (_, f, _, diags) in enumerate(result.parses, start=1):
            sys.stdout.write(f"Parse #{i}:\n")
            sys.stdout.write(f"  PRED: {f.feats.get('PRED')}\n")
            sys.stdout.write(f"  VOICE: {f.feats.get('VOICE')}\n")
            sys.stdout.write(f"  ASPECT: {f.feats.get('ASPECT')}\n")
            non_blocking = [d for d in diags if not d.is_blocking()]
            if non_blocking:
                sys.stdout.write(f"  diagnostics ({len(non_blocking)} info):\n")
                for d in non_blocking[:3]:
                    sys.stdout.write(f"    [{d.kind}] {d.message}\n")
        return

    if args.strict:
        # Strict mode: empty stdout on failure. Exit 0 (Unix-tool
        # convention: nothing printed = nothing matched).
        sys.stderr.write("(no complete parse)\n")
        return

    if not result.fragments:
        sys.stderr.write("(no parse, no fragments recoverable)\n")
        return

    sys.stdout.write(f"(partial: {len(result.fragments)} fragment(s))\n")
    for i, frag in enumerate(result.fragments, start=1):
        start, end = frag.span
        sys.stdout.write(
            f"Fragment #{i} [tokens {start}..{end}]: {frag.ctree.label}\n"
        )
        blocking = [d for d in frag.diagnostics if d.is_blocking()]
        for d in blocking[:2]:
            sys.stdout.write(f"  blocked: [{d.kind}] {d.message}\n")


if __name__ == "__main__":
    main()
