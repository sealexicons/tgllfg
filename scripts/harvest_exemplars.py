#!/usr/bin/env python3
"""Harvest exemplars from data/tgl/references/ for parser-coverage audit.

Wave 1 (pilot): transcriptions/rg81-excerpts.md + R&B 1986.
See .claude/plans/tgllfg-harvest-audit.md for the plan-of-record.

Usage:
    python scripts/harvest_exemplars.py extract
    python scripts/harvest_exemplars.py parse
    python scripts/harvest_exemplars.py report
    python scripts/harvest_exemplars.py all
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterator

REPO_ROOT = Path(__file__).resolve().parent.parent
REFERENCES_DIR = REPO_ROOT / "data" / "tgl" / "references"
EXEMPLARS_DIR = REPO_ROOT / "data" / "tgl" / "exemplars"


@dataclass
class Exemplar:
    source: str
    locator: str
    text_raw: str
    text_normalized: str
    has_gloss: bool
    gloss_en: str | None
    marked_ungrammatical: bool
    ocr_quality: str


@dataclass
class VerbEntry:
    source: str
    base: str
    affix_class_raw: str
    gloss: str
    locator: str


@dataclass
class ParseRecord:
    locator: str
    text: str
    bucket: str
    n_parses: int
    n_fragments: int
    oov_tokens: list[str] = field(default_factory=list)
    diag_summary: str = ""


# === Orthography normalization ===========================================


_STRESS_MAP = str.maketrans({
    "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
    "à": "a", "è": "e", "ì": "i", "ò": "o", "ù": "u",
    "â": "a", "ê": "e", "î": "i", "ô": "o", "û": "u",
    "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
})


def normalize_orthography(text: str) -> str:
    text = text.translate(_STRESS_MAP)
    text = text.replace("ʔ", "'")
    text = re.sub(r"\s+", " ", text).strip()
    return text


# === Source 1: rg81-excerpts.md (sentence-harvest) =======================


def extract_transcriptions() -> Iterator[Exemplar]:
    """Walk rg81-excerpts.md, yield Exemplar per sentence.

    Skips: ``### Talasalitan`` vocab tables; ``### Uncorrected
    continuation of OCR'd text of ANG PAMILYA``; H2 ``## Notes``
    section.
    """
    path = REFERENCES_DIR / "transcriptions" / "rg81-excerpts.md"
    text = path.read_text(encoding="utf-8")

    current_chapter: str | None = None
    in_skip_subsection = False
    in_talasalitan = False
    sent_idx = 0

    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        if line.startswith("## "):
            current_chapter = line[3:].split(" (")[0].strip()
            in_skip_subsection = False
            in_talasalitan = False
            sent_idx = 0
            continue

        if line.startswith("### "):
            sub = line[4:].strip()
            in_talasalitan = "Talasalitan" in sub
            in_skip_subsection = "Uncorrected" in sub
            continue

        if not line:
            continue
        if in_skip_subsection or in_talasalitan:
            continue
        if current_chapter is None or current_chapter == "Notes":
            continue
        if line.startswith("|"):
            continue

        m = re.match(r"\d+\.\s+(.+)$", line)
        if m:
            sent = m.group(1)
            sent_idx += 1
            yield Exemplar(
                source="rg81/transcriptions",
                locator=f"{current_chapter}/sent-{sent_idx}",
                text_raw=sent,
                text_normalized=normalize_orthography(sent),
                has_gloss=False,
                gloss_en=None,
                marked_ungrammatical=sent.startswith(("*", "?")),
                ocr_quality="transcription",
            )
            continue

        for sent in re.split(r"(?<=[.!?])\s+", line):
            sent = sent.strip()
            if len(sent) < 3:
                continue
            sent_idx += 1
            yield Exemplar(
                source="rg81/transcriptions",
                locator=f"{current_chapter}/sent-{sent_idx}",
                text_raw=sent,
                text_normalized=normalize_orthography(sent),
                has_gloss=False,
                gloss_en=None,
                marked_ungrammatical=sent.startswith(("*", "?")),
                ocr_quality="transcription",
            )


# === Source 2: R&B 1986 (verb-base inventory) =============================


_HEADWORD_RE = re.compile(r"^[A-Z][A-Z()]*[A-Z](?:[\-'][A-Z()]+)*'?$")


def _canonicalize_headword(h: str) -> str:
    """``ALA(A)LA`` → ``alaala``; ``ALAGA'`` → ``alaga``; strip
    optional-letter parens and trailing glottal-stop apostrophe."""
    h = re.sub(r"[()]", "", h)
    h = h.rstrip("'")
    return h.lower()
_SLOT_TOKENS = {"ACT", "OBJ", "DIR", "BEN", "INS", "LOC", "REA", "RF", "BF",
                "DF", "OF", "AF", "IF", "LF", "ACTU"}


def _is_slot_header(line: str) -> bool:
    toks = line.split()
    return bool(toks) and all(t in _SLOT_TOKENS for t in toks)
_AFFIX_RE = re.compile(r'^([\w\-/^]+(?:\s+[\w\-/^]+)*)\s+"([^"]+)"\s*$')


def extract_rb86_verb_inventory() -> Iterator[VerbEntry]:
    """Walk HandbokOfTagalogVerbs.txt, yield one VerbEntry per
    (base, affix-class signature, gloss) triple.

    Skips Introduction (first ~7 pages — OCR-mangled italics).
    Picks up paradigm entries from page 1 onward.
    """
    path = REFERENCES_DIR / "HandbokOfTagalogVerbs.txt"
    text = path.read_text(encoding="utf-8")

    lines = text.splitlines()
    page_idx = 0
    pending_headword: str | None = None
    seen_pairs: set[tuple[str, str]] = set()

    for raw_line in lines:
        line = raw_line.rstrip()
        if line.startswith("=== page break ==="):
            page_idx += 1
            continue
        if page_idx < 8:
            continue

        stripped = line.strip()
        if not stripped:
            continue

        if _is_slot_header(stripped):
            continue

        if _HEADWORD_RE.match(stripped) and 3 <= len(stripped) <= 24:
            pending_headword = stripped
            continue

        m = _AFFIX_RE.match(stripped)
        if m and pending_headword:
            affix_sig = m.group(1).strip()
            gloss = m.group(2).strip()
            key = (pending_headword, gloss)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            yield VerbEntry(
                source="rb86",
                base=_canonicalize_headword(pending_headword),
                affix_class_raw=affix_sig,
                gloss=gloss,
                locator=f"page-{page_idx}/{pending_headword}",
            )


# === Stages: extract, parse, report ======================================


def cmd_extract() -> None:
    EXEMPLARS_DIR.mkdir(parents=True, exist_ok=True)

    exemplars_path = EXEMPLARS_DIR / "wave1-exemplars.jsonl"
    n_exemplars = 0
    with exemplars_path.open("w", encoding="utf-8") as fh:
        for ex in extract_transcriptions():
            fh.write(json.dumps(asdict(ex), ensure_ascii=False) + "\n")
            n_exemplars += 1
    print(f"  → {exemplars_path.relative_to(REPO_ROOT)} ({n_exemplars} exemplars)")

    verbs_path = EXEMPLARS_DIR / "wave1-rb86-verbs.jsonl"
    n_verbs = 0
    with verbs_path.open("w", encoding="utf-8") as fh:
        for ve in extract_rb86_verb_inventory():
            fh.write(json.dumps(asdict(ve), ensure_ascii=False) + "\n")
            n_verbs += 1
    print(f"  → {verbs_path.relative_to(REPO_ROOT)} ({n_verbs} verb entries)")


def cmd_parse() -> None:
    from tgllfg.core.pipeline import parse_text_with_fragments

    in_path = EXEMPLARS_DIR / "wave1-exemplars.jsonl"
    out_path = EXEMPLARS_DIR / "wave1-parse-results.jsonl"

    if not in_path.exists():
        print(f"ERROR: {in_path} not found; run 'extract' first", file=sys.stderr)
        sys.exit(1)

    n = 0
    bucket_counts: Counter[str] = Counter()
    with in_path.open(encoding="utf-8") as in_fh, out_path.open("w", encoding="utf-8") as out_fh:
        for line in in_fh:
            ex = json.loads(line)
            text = ex["text_normalized"]
            try:
                result = parse_text_with_fragments(text, n_best=3)
                n_parses = len(result.parses)
                n_fragments = len(result.fragments)
                if n_parses >= 2:
                    bucket = "parse-success-N"
                elif n_parses == 1:
                    bucket = "parse-success-1"
                elif n_fragments > 0:
                    bucket = "zero-parse-fragment"
                else:
                    bucket = "zero-parse-no-fragment"
                diag_summary = ""
                oov = []
                if n_parses == 0 and result.fragments:
                    frag = result.fragments[0]
                    diags = getattr(frag, "diagnostics", []) or []
                    if diags:
                        diag_summary = str(diags[0])[:200]
                        for d in diags:
                            s = str(d)
                            m = re.search(r"unknown (?:word|lexeme|token):\s*['\"]?(\w+)", s, re.IGNORECASE)
                            if m:
                                oov.append(m.group(1))
            except Exception as e:
                bucket = "tokenizer-fail"
                n_parses = 0
                n_fragments = 0
                diag_summary = f"EXCEPTION: {type(e).__name__}: {e}"[:200]
                oov = []

            rec = ParseRecord(
                locator=ex["locator"],
                text=text,
                bucket=bucket,
                n_parses=n_parses,
                n_fragments=n_fragments,
                oov_tokens=oov,
                diag_summary=diag_summary,
            )
            out_fh.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")
            bucket_counts[bucket] += 1
            n += 1
            if n % 25 == 0:
                print(f"  …parsed {n}", file=sys.stderr)

    print(f"  → {out_path.relative_to(REPO_ROOT)} ({n} records)")
    for b, c in bucket_counts.most_common():
        print(f"      {b:30s} {c:4d}  ({c/n:5.1%})")


def cmd_report() -> None:
    parse_path = EXEMPLARS_DIR / "wave1-parse-results.jsonl"
    verbs_path = EXEMPLARS_DIR / "wave1-rb86-verbs.jsonl"
    report_path = REPO_ROOT / "docs" / "coverage-audit-2026-05.md"

    if not parse_path.exists():
        print(f"ERROR: {parse_path} not found; run 'parse' first", file=sys.stderr)
        sys.exit(1)

    records = [json.loads(l) for l in parse_path.open(encoding="utf-8")]
    verbs = []
    if verbs_path.exists():
        verbs = [json.loads(l) for l in verbs_path.open(encoding="utf-8")]

    bucket_counts: Counter[str] = Counter(r["bucket"] for r in records)
    by_chapter: dict[str, Counter[str]] = defaultdict(Counter)
    for r in records:
        chapter = r["locator"].split("/")[0]
        by_chapter[chapter][r["bucket"]] += 1

    zero_parses = [r for r in records if r["bucket"].startswith("zero-parse") or r["bucket"] == "tokenizer-fail"]
    oov_counter: Counter[str] = Counter()
    for r in zero_parses:
        for tok in r["oov_tokens"]:
            oov_counter[tok.lower()] += 1

    verb_coverage = _verb_coverage_check(verbs)

    lines: list[str] = []
    lines.append("# Coverage audit — Wave 1 (transcriptions + R&B 1986)")
    lines.append("")
    lines.append("> **Status:** Wave 1 pilot snapshot (2026-05-14). See")
    lines.append("> ``.claude/plans/tgllfg-harvest-audit.md`` for the plan-of-record.")
    lines.append("> Wave 2 (R&G Intermediate + R&C 1990 + Ramos 1971) and Wave 3")
    lines.append("> (S&O 1972 + R&G Conversational) follow.")
    lines.append("")
    lines.append("## Wave 1 sources")
    lines.append("")
    lines.append("- ``data/tgl/references/transcriptions/rg81-excerpts.md`` —")
    lines.append("  hand-transcribed excerpts from Ramos & Goulet 1981")
    lines.append("  *Intermediate Tagalog*, four chapters (ANG MANOK, ANG")
    lines.append("  PAG-AARAL NG ISANG WIKA, PANAHON, ANG PAMILYA). Skipped:")
    lines.append("  Talasalitan vocab tables and the ``Uncorrected continuation``")
    lines.append("  subsection per user directive 2026-05-14.")
    lines.append("- ``data/tgl/references/HandbokOfTagalogVerbs.txt`` —")
    lines.append("  Ramos & Bautista 1986 *Handbook of Tagalog Verbs*; used for")
    lines.append("  verb-base inventory only (paradigm-cell extraction deferred;")
    lines.append("  OCR splits forms across lines too irregularly for Wave 1).")
    lines.append("")
    lines.append("## Sentence-parse buckets (rg81 transcriptions)")
    lines.append("")
    lines.append(f"Total sentences parsed: **{len(records)}**.")
    lines.append("")
    lines.append("| Bucket | Count | Share |")
    lines.append("| --- | ---: | ---: |")
    for b, c in bucket_counts.most_common():
        lines.append(f"| {b} | {c} | {c/len(records):.1%} |")
    lines.append("")
    lines.append("### Per-chapter breakdown")
    lines.append("")
    chapter_bucket_keys = sorted({b for chap in by_chapter.values() for b in chap})
    header = "| Chapter | " + " | ".join(chapter_bucket_keys) + " | Total |"
    sep = "| --- |" + " ---: |" * (len(chapter_bucket_keys) + 1)
    lines.append(header)
    lines.append(sep)
    for chap, counter in sorted(by_chapter.items()):
        row = [chap]
        total_c = sum(counter.values())
        for b in chapter_bucket_keys:
            row.append(str(counter.get(b, 0)))
        row.append(str(total_c))
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    lines.append("## Zero-parse examples (top 30)")
    lines.append("")
    lines.append("| Locator | Text | Bucket | OOV tokens | Diagnostic |")
    lines.append("| --- | --- | --- | --- | --- |")
    for r in zero_parses[:30]:
        oov = ", ".join(r["oov_tokens"][:5]) or "—"
        diag = r["diag_summary"].replace("|", "\\|")[:80] or "—"
        text = r["text"].replace("|", "\\|")[:60]
        lines.append(f"| `{r['locator']}` | {text} | {r['bucket']} | {oov} | {diag} |")
    lines.append("")
    lines.append("## OOV-token frequency (top 30)")
    lines.append("")
    if oov_counter:
        lines.append("| Token | Count |")
        lines.append("| --- | ---: |")
        for tok, c in oov_counter.most_common(30):
            lines.append(f"| `{tok}` | {c} |")
    else:
        lines.append("*No OOV tokens captured — parser diagnostics did not surface lex-OOV signal in this run; investigation needed.*")
    lines.append("")
    lines.append("## R&B 1986 verb-base inventory")
    lines.append("")
    lines.append(f"Extracted: **{len(verbs)}** verb entries (one per `(base, gloss)` pair).")
    lines.append("")
    if verb_coverage:
        lines.append("### Lex coverage")
        lines.append("")
        lines.append(f"- In our lex: **{verb_coverage['known']}**")
        lines.append(f"- Not in our lex: **{verb_coverage['missing']}**")
        lines.append(f"- Coverage: **{verb_coverage['known'] / max(verb_coverage['total'], 1):.1%}**")
        lines.append("")
        if verb_coverage["missing_examples"]:
            lines.append("### Missing-from-lex (top 50)")
            lines.append("")
            lines.append("| Base | Gloss | Affix class |")
            lines.append("| --- | --- | --- |")
            for ve in verb_coverage["missing_examples"][:50]:
                lines.append(f"| `{ve['base']}` | {ve['gloss']} | `{ve['affix_class_raw']}` |")
            lines.append("")
    lines.append("## Next steps")
    lines.append("")
    lines.append("1. Eyeball the top-30 zero-parse rows above; cluster by")
    lines.append("   construction class (manual triage).")
    lines.append("2. Triage the OOV-token list against the lex sources in")
    lines.append("   `data/tgl/lexicon/`; many will be proper nouns or")
    lines.append("   names of places (e.g. ``Pilipinas``).")
    lines.append("3. Triage the R&B-1986-missing verb list; identify productive")
    lines.append("   bases that are missing from `verbs.yaml`.")
    lines.append("4. Proceed to Wave 2 if signal-to-noise is acceptable.")
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  → {report_path.relative_to(REPO_ROOT)}")


def _verb_coverage_check(verbs: list[dict]) -> dict | None:
    """Cross-check R&B verb bases against our verbs.yaml lex.

    Returns ``None`` if verbs.yaml isn't loadable.
    """
    verbs_yaml = REPO_ROOT / "data" / "tgl" / "verbs.yaml"
    if not verbs_yaml.exists():
        return None
    import yaml
    data = yaml.safe_load(verbs_yaml.read_text(encoding="utf-8"))
    known_bases: set[str] = set()
    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict):
        entries = data.get("entries") or data.get("verbs") or []
    else:
        entries = []
    for e in entries:
        if isinstance(e, dict):
            lemma = (e.get("citation") or e.get("lemma")
                     or e.get("base") or e.get("root"))
            if lemma:
                known_bases.add(str(lemma).lower())
    total = len(verbs)
    known = sum(1 for v in verbs if v["base"] in known_bases)
    missing = total - known
    missing_examples = [v for v in verbs if v["base"] not in known_bases]
    missing_examples.sort(key=lambda v: v["base"])
    return {
        "total": total,
        "known": known,
        "missing": missing,
        "missing_examples": missing_examples,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("stage", choices=["extract", "parse", "report", "all"])
    args = p.parse_args(argv)

    if args.stage in ("extract", "all"):
        print("[extract]")
        cmd_extract()
    if args.stage in ("parse", "all"):
        print("[parse]")
        cmd_parse()
    if args.stage in ("report", "all"):
        print("[report]")
        cmd_report()
    return 0


if __name__ == "__main__":
    sys.exit(main())
