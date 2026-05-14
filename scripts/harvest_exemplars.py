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


# === Tagalog-sentence heuristic ==========================================


# Common Tagalog function words / particles that almost any Tagalog
# sentence will contain. If a line contains none of these, it's
# probably English (or a vocabulary entry, or a noisy OCR line).
_TGL_MARKERS = {
    "ang", "ng", "sa", "mga", "si", "ni", "kay", "nang", "at", "o",
    "pa", "na", "ba", "nga", "po", "ho", "daw", "raw", "pala",
    "naman", "lang", "lamang", "din", "rin", "may", "mayroon",
    "wala", "ako", "ikaw", "ka", "siya", "kami", "tayo", "kayo",
    "sila", "ko", "mo", "niya", "namin", "natin", "ninyo", "nila",
    "akin", "iyo", "kanya", "amin", "atin", "inyo", "kanila",
    "ito", "iyan", "iyon", "ng-",
}

# English function words that suggest the line is English prose.
_EN_MARKERS = {
    "the", "of", "and", "or", "to", "in", "is", "are", "was",
    "were", "this", "that", "these", "those", "with", "from",
    "for", "but", "not", "be", "have", "has", "had",
}


def _looks_like_tagalog(text: str) -> bool:
    """Heuristic: tokens overlap with Tagalog function-word set and
    not (only) English. Requires at least 2 distinct Tagalog markers
    to reject ambiguous lines (``may`` is both Tagalog and English)."""
    toks = re.findall(r"[a-zA-Z']+", text.lower())
    if not toks or len(toks) < 3:
        return False
    # Reject OCR-character-spaced lines — many single-letter "tokens"
    # signal letter-by-letter spacing (common in Ramos 1971 OCR).
    single_char = sum(1 for t in toks if len(t) == 1)
    if single_char > len(toks) * 0.4:
        return False
    tgl = {t for t in toks if t in _TGL_MARKERS}
    en = {t for t in toks if t in _EN_MARKERS}
    if len(tgl) < 2:
        return False
    if len(en) > len(tgl):
        return False
    return True


def _is_sentence_shape(text: str) -> bool:
    """First char uppercase or quoted; ends with terminal punctuation;
    has at least 3 tokens."""
    t = text.strip()
    if len(t) < 4:
        return False
    if not (t[0].isupper() or t[0] in "\"'("):
        return False
    if not t.rstrip(")\"'").endswith((".", "?", "!")):
        return False
    return len(t.split()) >= 3


# === Source 3: R&C 1990 (sentence harvest) ================================


_RC_CHAPTER_RE = re.compile(r"^Chapter\s+(\d+)\.\s+(.+?)\s*$")


def extract_rc1990() -> Iterator[Exemplar]:
    """Walk Modern Tagalog (R&C 1990) for Tagalog example sentences.

    Skips: front matter (before "Chapter 1"); vocabulary tables; word-
    pair drill blocks (root + affix -> form).
    Picks up: sentence-shaped lines in chapter bodies, exercise
    blocks, and grammar-note example panels.
    """
    path = REFERENCES_DIR / "901132785-Modern-Tagalog.txt"
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    chapter = None
    section = None
    sent_idx = 0
    in_body = False
    seen_chapters: set[str] = set()

    for raw in lines:
        line = raw.rstrip()
        m = _RC_CHAPTER_RE.match(line.strip())
        if m:
            # Skip TOC entries: chapter heading in TOC ends with a page
            # number (digit run at end), while body-chapter headings
            # don't. Also skip chapter we've already seen in body.
            label = f"Ch{m.group(1)}-{m.group(2)[:40]}"
            if re.search(r"\d+\s*$", m.group(2)):
                continue
            if label in seen_chapters:
                continue
            seen_chapters.add(label)
            chapter = label
            section = None
            in_body = True
            continue
        if not in_body:
            continue
        stripped = line.strip()
        if not stripped:
            continue
        # Skip page footer lines like "4        Tagalog Sounds" (digit
        # at line start followed by spaces).
        if re.match(r"^\s*\d+\s{2,}", line):
            continue
        if stripped == stripped.title() and len(stripped) < 60 and ":" not in stripped:
            if len(stripped.split()) <= 8 and not stripped.endswith((".", "?", "!")):
                section = stripped
                continue

        m = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if m:
            sent = m.group(1).strip()
        else:
            sent = stripped

        if not _is_sentence_shape(sent):
            continue
        if not _looks_like_tagalog(sent):
            continue

        sent_idx += 1
        loc = f"{chapter}"
        if section:
            loc += f"/{section}"
        loc += f"/sent-{sent_idx}"
        yield Exemplar(
            source="rc1990",
            locator=loc,
            text_raw=sent,
            text_normalized=normalize_orthography(sent),
            has_gloss=False,
            gloss_en=None,
            marked_ungrammatical=sent.startswith(("*", "?")),
            ocr_quality="clean-ocr",
        )


# === Source 4: R&G 1981 Intermediate (sentence harvest) ===================


_RG_PAGE_RE = re.compile(r"^---\s*Page\s+(\d+)\s*---\s*$")
_RG_SPEAKER_RE = re.compile(r"^([A-Z])(?:\d+)?:\s+(.+)$")


def extract_rg_intermediate() -> Iterator[Exemplar]:
    """Walk R&G 1981 Intermediate for Tagalog sentences.

    Sources of sentences in this book:
    - Dialog lines: ``A: ...`` / ``B: ...`` (speaker-tagged).
    - Exercise items: ``1. ...`` / ``2. ...`` (numbered).
    - Pedagogical-unit titles in the TOC (gold; clean sentences).

    Skips: English explanatory prose (filtered by Tagalog-marker
    heuristic), Vocabulary lists (mostly word→gloss pairs).
    """
    path = REFERENCES_DIR / "Intermediate-Tagalog-developing-cultural-awareness-through-language_compress.txt"
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    page = 0
    sent_idx = 0

    for raw in lines:
        line = raw.rstrip()
        m = _RG_PAGE_RE.match(line)
        if m:
            page = int(m.group(1))
            continue

        stripped = line.strip()
        if not stripped:
            continue

        m = _RG_SPEAKER_RE.match(stripped)
        if m:
            sent = m.group(2).strip()
            kind = "dialog"
        else:
            mn = re.match(r"^\s*\d+\.\s+(.+)$", line)
            if mn:
                sent = mn.group(1).strip()
                kind = "numbered"
            else:
                sent = stripped
                kind = "prose"

        if not _is_sentence_shape(sent):
            continue
        if not _looks_like_tagalog(sent):
            continue

        sent_idx += 1
        yield Exemplar(
            source="rg-intermediate",
            locator=f"page-{page}/{kind}/sent-{sent_idx}",
            text_raw=sent,
            text_normalized=normalize_orthography(sent),
            has_gloss=False,
            gloss_en=None,
            marked_ungrammatical=sent.startswith(("*", "?")),
            ocr_quality="clean-ocr",
        )


# === Source 5: Ramos 1971 Dictionary (verb-example sentences) =============


_RAMOS_ENTRY_RE = re.compile(r"^([a-zàáâèéêìíîòóôùúûñ'-]+(?:\s+\([A-Za-z]+\))?)\s+(n\.|v\.|adj\.|adv\.|conj\.|interj\.|prep\.|pron\.|part\.)\s*(.+)?$")


def extract_ramos1971() -> Iterator[Exemplar]:
    """Walk Ramos 1971 Dictionary for Tagalog example sentences.

    The dictionary lists ~4000 headwords; each verb entry has an
    inline Tagalog example. Extract those (skip word-pair gloss
    fragments; skip headword + POS metadata lines).
    """
    path = REFERENCES_DIR / "746927054-OceanofPDF-com-Tagalog-Dictionary-Teresita-v-Ramos.txt"
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    current_headword: str | None = None
    sent_idx = 0
    in_body = False

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()

        if not in_body:
            if re.match(r"^[a-z]+\s+[a-z]+'?", stripped) and ("n." in stripped or "v." in stripped or "adj." in stripped):
                in_body = True
            else:
                continue

        m = _RAMOS_ENTRY_RE.match(stripped)
        if m:
            current_headword = m.group(1).split()[0]
            continue

        if not _is_sentence_shape(stripped):
            continue
        if not _looks_like_tagalog(stripped):
            continue
        if not current_headword:
            continue

        sent_idx += 1
        yield Exemplar(
            source="ramos1971",
            locator=f"entry-{current_headword}/sent-{sent_idx}",
            text_raw=stripped,
            text_normalized=normalize_orthography(stripped),
            has_gloss=False,
            gloss_en=None,
            marked_ungrammatical=stripped.startswith(("*", "?")),
            ocr_quality="clean-ocr",
        )


# === Source 2: R&B 1986 (verb-base inventory) =============================


_HEADWORD_RE = re.compile(r"^[A-Z][A-Z()]*[A-Z](?:[\-'][A-Z()]+)*'?$")


def _canonicalize_headword(h: str) -> str:
    """``ALA(A)LA`` → ``alaala``; ``ALAGA'`` → ``alaga``; strip
    optional-letter parens and trailing glottal-stop apostrophe."""
    h = re.sub(r"[()]", "", h)
    h = h.rstrip("'")
    return h.lower()


# OCR-corruption fixups for R&B 1986 glosses. The patterns are
# OCR-engine artifacts on the source's italicized gloss text:
#
#   ``»`` and ``*``  → comma (column-rendering of italic comma)
#   ``r `` / ``f ``  → ``, `` (italic-comma-after-letter context)
#   ``ì`` / ``ó``    → ``l`` (italic-l body with serif noise)
#
# The trailing-letter patterns are anchored to specific observed
# substitutions; applying them blindly would corrupt legitimate
# English words ending in ``r`` (e.g., ``changer`` IS a real word
# but in this corpus only appears as the OCR'd ``change,``).
_GLOSS_LETTER_FIXUPS = {
    "dor make": "do, make",
    "sendr bring": "send, bring",
    "changer replace": "change, replace",
    "selfr insist": "self, insist",
    "lifer live": "life, live",
    "expectf rely": "expect, rely",
    "pulì": "pull",
    "cióse": "close",
}


def _clean_gloss(g: str) -> str:
    """Apply OCR-corruption fixups + spacing normalization to a
    R&B 1986 gloss."""
    g = g.replace("»", ",").replace("*", ",")
    for bad, good in _GLOSS_LETTER_FIXUPS.items():
        g = g.replace(bad, good)
    g = re.sub(r"\s*/\s*", " / ", g)
    g = re.sub(r",(\S)", r", \1", g)
    g = re.sub(r"\s+", " ", g).strip()
    return g


def _clean_affix_class(a: str) -> str:
    """Spacing normalization around ``/`` separators in affix-class
    signatures (e.g. ``-um-/mag-`` → ``-um- / mag-``)."""
    a = re.sub(r"\s*/\s*", " / ", a)
    a = re.sub(r"\s+", " ", a).strip()
    return a
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
                affix_class_raw=_clean_affix_class(affix_sig),
                gloss=_clean_gloss(gloss),
                locator=f"page-{page_idx}/{pending_headword}",
            )


# === Stages: extract, parse, report ======================================


def _write_jsonl(path: Path, items: Iterator) -> int:
    n = 0
    with path.open("w", encoding="utf-8") as fh:
        for item in items:
            fh.write(json.dumps(asdict(item), ensure_ascii=False) + "\n")
            n += 1
    return n


def cmd_extract() -> None:
    EXEMPLARS_DIR.mkdir(parents=True, exist_ok=True)

    pairs: list[tuple[str, Iterator]] = [
        ("wave1-exemplars.jsonl", extract_transcriptions()),
        ("wave1-rb86-verbs.jsonl", extract_rb86_verb_inventory()),
        ("wave2-rc1990.jsonl", extract_rc1990()),
        ("wave2-rg-intermediate.jsonl", extract_rg_intermediate()),
        ("wave2-ramos1971.jsonl", extract_ramos1971()),
    ]
    for fname, it in pairs:
        path = EXEMPLARS_DIR / fname
        n = _write_jsonl(path, it)
        print(f"  → {path.relative_to(REPO_ROOT)} ({n})")


_PARSE_SOURCES = [
    ("wave1-exemplars.jsonl", "wave1-parse-results.jsonl", None),
    ("wave2-rc1990.jsonl", "wave2-rc1990-parse-results.jsonl", 500),
    ("wave2-rg-intermediate.jsonl", "wave2-rg-intermediate-parse-results.jsonl", 500),
    ("wave2-ramos1971.jsonl", "wave2-ramos1971-parse-results.jsonl", 500),
]


def cmd_parse() -> None:
    from tgllfg.core.pipeline import parse_text_with_fragments

    import random
    rng = random.Random(42)

    for in_name, out_name, sample_cap in _PARSE_SOURCES:
        in_path = EXEMPLARS_DIR / in_name
        out_path = EXEMPLARS_DIR / out_name
        if not in_path.exists():
            print(f"  (skip {in_name}; not found)")
            continue
        print(f"\n[parse] {in_name}")
        _parse_one(in_path, out_path, parse_text_with_fragments, sample_cap, rng)


def _parse_one(
    in_path: Path,
    out_path: Path,
    parse_fn,
    sample_cap: int | None,
    rng,
) -> None:
    """Inner parser-driver loop for a single JSONL input file."""

    n = 0
    bucket_counts: Counter[str] = Counter()
    with in_path.open(encoding="utf-8") as in_fh:
        records = [line for line in in_fh]
    if sample_cap is not None and len(records) > sample_cap:
        records = rng.sample(records, sample_cap)
        print(f"  sampling {sample_cap} of {len(records)} records (seed=42)")

    with out_path.open("w", encoding="utf-8") as out_fh:
        for line in records:
            ex = json.loads(line)
            text = ex["text_normalized"]
            try:
                result = parse_fn(text, n_best=3)
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
            if n % 50 == 0:
                print(f"  …parsed {n}", file=sys.stderr)

    print(f"  → {out_path.relative_to(REPO_ROOT)} ({n} records)")
    for b, c in bucket_counts.most_common():
        print(f"      {b:30s} {c:4d}  ({c / n:5.1%})")


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
