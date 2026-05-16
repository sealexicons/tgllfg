#!/usr/bin/env python3
"""Phase 9.A: emit a Phase 9 lex-pass hit list from the OOV-frequency
artifact.

Reads ``data/tgl/exemplars/oov-frequency.tsv`` (produced by
``scripts/harvest_exemplars.py xwave-report``) and emits a filtered,
analyzer-annotated list of candidate lex entries for the next lex-pass
sub-PR.

Usage::

    python scripts/oov_hit_list.py --threshold 5
    python scripts/oov_hit_list.py --limit 50
    python scripts/oov_hit_list.py --wave wave2-rc1990 --threshold 3
    python scripts/oov_hit_list.py --format markdown > /tmp/hits.md

The morphological probe runs the same analyzer the parser uses
(``tgllfg.morph.analyzer._get_default``) so the POS hint surfaces
the same _UNK / known-POS verdict the parser sees. Heuristic POS
suggestions are layered on top to guide lex-pass authors:

* Starts with ``mag``/``nag``/``pag``/``nap``/``pakikipag`` → likely
  VERB (suggest ``affix_class: [<prefix>]``).
* Starts with ``naka``/``nakipag`` → likely VERB (aptative profile).
* Ends in ``-in``, ``-an``, ``-han`` → likely VERB (OV/LF/RV affix).
* Title-case in source sample → likely proper-name NOUN.
* English vocabulary signature (no Tagalog phonotactic match) →
  flag as harvest-noise candidate.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXEMPLARS_DIR = REPO_ROOT / "data" / "tgl" / "exemplars"
OOV_TSV = EXEMPLARS_DIR / "oov-frequency.tsv"

_VERB_PREFIX_PATTERNS = [
    (re.compile(r"^(pakikipag)(.+)$"), "pakikipag"),
    (re.compile(r"^(nakipag)(.+)$"), "nakipag"),
    (re.compile(r"^(makipag)(.+)$"), "makipag"),
    (re.compile(r"^(naka)(.+)$"), "naka"),
    (re.compile(r"^(maka)(.+)$"), "maka"),
    (re.compile(r"^(nagpa)(.+)$"), "nagpa"),
    (re.compile(r"^(magpa)(.+)$"), "magpa"),
    (re.compile(r"^(nagsi)(.+)$"), "nagsi"),
    (re.compile(r"^(magsi)(.+)$"), "magsi"),
    (re.compile(r"^(nagka)(.+)$"), "nagka"),
    (re.compile(r"^(magka)(.+)$"), "magka"),
    (re.compile(r"^(nag)(.+)$"), "nag"),
    (re.compile(r"^(mag)(.+)$"), "mag"),
    (re.compile(r"^(pag)(.+)$"), "pag"),
    (re.compile(r"^(um)(.+)$"), "um"),
    (re.compile(r"^(in)(.+)$"), "in"),
    (re.compile(r"^(i)(.+)$"), "i"),
    (re.compile(r"^(ma)(.+)$"), "ma"),
    (re.compile(r"^(na)(.+)$"), "na"),
    (re.compile(r"^(pa)(.+)$"), "pa"),
]
_VERB_SUFFIX_PATTERNS = [
    (re.compile(r"^(.+)(han)$"), "han"),
    (re.compile(r"^(.+)(an)$"), "an"),
    (re.compile(r"^(.+)(hin)$"), "hin"),
    (re.compile(r"^(.+)(in)$"), "in"),
]

# Pure English signature: token contains only letters AND has a
# vowel-cluster pattern Tagalog genuinely lacks. ``oo``/``ii`` are
# native (e.g. ``loob``, ``magkaroon``); only ``ee``/``ea``/``ou``/
# ``ie``/``ai`` (the last in -aid/-air patterns) are diagnostic.
_ENGLISH_VOWEL_PAT = re.compile(r"(ee|ea|ou|ie)", re.I)


@dataclass
class HitRow:
    rank: int
    token: str
    count: int
    sample_locator: str
    sample_text: str


def _load_tsv(path: Path) -> list[HitRow]:
    rows: list[HitRow] = []
    with path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for r in reader:
            rows.append(HitRow(
                rank=int(r["rank"]),
                token=r["token"],
                count=int(r["count"]),
                sample_locator=r.get("sample_locator", ""),
                sample_text=r.get("sample_text", ""),
            ))
    return rows


def _filter_by_wave(rows: list[HitRow], wave: str | None) -> list[HitRow]:
    """Keep rows whose sample-locator hints at the requested wave.

    Locators are coarse — wave1/wave2/wave3 are inferred from the
    locator prefix shape:

    * ``ANG MANOK/sent-N`` / ``ANG PAMILYA/sent-N`` etc. → Wave 1
    * ``page-NN/...`` → likely Wave 2 R&G Intermediate or Wave 3
      (need stem-pdf filename match — coarse heuristic)
    * ``Ch5-Some Changes/...`` → likely R&C 1990 (Wave 2)
    * Speaker-tag prefix → R&G Conversational (Wave 3)

    For now we just substring-match the wave name against the
    locator. The OOV-frequency TSV doesn't carry per-wave breakdown
    by design (sample is the first one seen across all waves).
    """
    if not wave or wave == "all":
        return rows
    keep = []
    for r in rows:
        if wave in r.sample_locator:
            keep.append(r)
    return keep


def _morph_verdict(token: str) -> str:
    """Run the parser's morphology analyzer on the token and report
    its verdict. Lazy-loaded so the import cost is paid once."""
    global _analyzer
    try:
        from tgllfg.morph.analyzer import _get_default
        from tgllfg.core.common import Token
        if _analyzer is None:
            _analyzer = _get_default()
        norm = token.lower()
        if _analyzer.is_known_surface(norm):
            tok = Token(surface=token, norm=norm,
                        start=0, end=len(token))
            analyses = _analyzer.analyze_one(tok)
            if not analyses:
                return "(known-no-analyses)"
            pos = sorted({
                getattr(a, "pos", "?") for a in analyses
            })
            return ",".join(pos)
        return "_UNK"
    except Exception as e:
        return f"(err:{type(e).__name__}:{e})"[:40]


def _heuristic_pos(token: str, sample_text: str) -> str:
    """Surface a heuristic POS hint to guide lex-pass authors.

    Output is suggestive only — verify against tagalog.com / S&O / R&C
    before adding lex entries. ``VERB?(prefix+base)`` means the token
    looks like an affixed verb, but the base isn't verified.
    """
    # Title-case in source sample → likely proper name
    if sample_text:
        words = sample_text.split()
        if words:
            first = words[0].lower().strip(".,!?:'\"")
            for w in words:
                w_clean = w.lower().strip(".,!?:'\"")
                if w_clean == token.lower() and w[:1].isupper():
                    if first != token.lower():
                        # In-sentence title-case → proper-name signal.
                        # Common-noun false positives: Tagalog content
                        # nouns in phrases like ``Mahal na Araw``,
                        # ``Bagong Taon`` — verify before adding.
                        return "NOUN(proper)?"
                    break
    # English signature (non-Tagalog vowel clusters)
    if _ENGLISH_VOWEL_PAT.search(token):
        return "ENGLISH?"
    # Verb-prefix patterns
    for pat, prefix in _VERB_PREFIX_PATTERNS:
        m = pat.match(token)
        if m and len(m.group(2)) >= 3:
            return f"VERB?({prefix}+{m.group(2)})"
    # Verb-suffix patterns
    for pat, suffix in _VERB_SUFFIX_PATTERNS:
        m = pat.match(token)
        if m and len(m.group(1)) >= 3:
            return f"VERB?({m.group(1)}+{suffix})"
    return "?"


def emit_tsv(hits: list[tuple[HitRow, str, str]], out=sys.stdout) -> None:
    w = csv.writer(out, delimiter="\t", lineterminator="\n")
    w.writerow(["rank", "token", "count", "morph", "heuristic",
                "sample_locator", "sample_text"])
    for r, morph, heur in hits:
        w.writerow([r.rank, r.token, r.count, morph, heur,
                    r.sample_locator, r.sample_text])


def emit_markdown(hits: list[tuple[HitRow, str, str]], out=sys.stdout) -> None:
    out.write("| Rank | Token | Count | Morph | Heuristic | Sample |\n")
    out.write("| ---: | --- | ---: | --- | --- | --- |\n")
    for r, morph, heur in hits:
        sample = r.sample_text.replace("|", "\\|")[:80]
        out.write(f"| {r.rank} | `{r.token}` | {r.count} | "
                  f"`{morph}` | {heur} | {sample} |\n")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--threshold", type=int, default=3,
                   help="minimum count (default: 3)")
    p.add_argument("--limit", type=int, default=200,
                   help="max rows to emit (default: 200)")
    p.add_argument("--wave", default="all",
                   help="filter by wave substring "
                        "(wave1/wave2/wave3/all; default: all)")
    p.add_argument("--format", choices=["tsv", "markdown"], default="tsv")
    p.add_argument("--no-morph", action="store_true",
                   help="skip the morph-analyzer probe (faster)")
    p.add_argument("--input", type=Path, default=OOV_TSV,
                   help="path to OOV-frequency TSV "
                        f"(default: {OOV_TSV.relative_to(REPO_ROOT)})")
    args = p.parse_args(argv)

    if not args.input.exists():
        print(f"ERROR: {args.input} not found. Run "
              "`python scripts/harvest_exemplars.py xwave-report` first.",
              file=sys.stderr)
        return 1

    rows = _load_tsv(args.input)
    rows = [r for r in rows if r.count >= args.threshold]
    rows = _filter_by_wave(rows, args.wave)
    rows = rows[: args.limit]

    hits: list[tuple[HitRow, str, str]] = []
    for r in rows:
        morph = "(skipped)" if args.no_morph else _morph_verdict(r.token)
        heur = _heuristic_pos(r.token, r.sample_text)
        hits.append((r, morph, heur))

    if args.format == "tsv":
        emit_tsv(hits)
    else:
        emit_markdown(hits)
    return 0


_analyzer = None  # lazy-loaded


if __name__ == "__main__":
    sys.exit(main())
