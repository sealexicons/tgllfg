#!/usr/bin/env python3
# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Harvest exemplars from data/tgl/references/ for parser-coverage audit.

Wave 1 (pilot): transcriptions/rg81-excerpts.md + R&B 1986.
See .claude/plans/tgllfg-harvest-audit.md for the plan-of-record.

Usage:
    python scripts/harvest_exemplars.py extract
    python scripts/harvest_exemplars.py parse
    python scripts/harvest_exemplars.py report
    python scripts/harvest_exemplars.py all
"""

import argparse
import json
import re
import signal
import sys
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterator

# Phase 9.X.pre-1.19: per-item parse timeout (SIGALRM) and live
# progress + latency logging. Without these, long sentences that
# trigger combinatorial chart-parse explosion could hang the whole
# audit (the original Phase 8/9 audits required > 1 hour wall on
# wave1 alone before the SIGALRM cap). The 10s cap is well above
# the observed p95 (~0.1s) so it only fires on pathological items.
ITEM_TIMEOUT_S = 10
AUDIT_MONITOR_LOG = Path("/tmp/audit_monitor.log")
AUDIT_LAST_ITEM = Path("/tmp/audit_monitor.last_item")


class ParseTimeout(Exception):
    """Raised by the SIGALRM handler when a parse exceeds the
    per-item timeout."""


def _alarm_handler(signum, frame):  # pragma: no cover - signal callback
    raise ParseTimeout()


signal.signal(signal.SIGALRM, _alarm_handler)

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
    diag_kinds: dict[str, int] = field(default_factory=dict)
    # Phase 9.X.pre-1.19: per-item parse latency (seconds, rounded
    # to 3 decimal places). Items that hit ITEM_TIMEOUT_S are tagged
    # with bucket="parse-timeout" and ``latency_s == ITEM_TIMEOUT_S``.
    latency_s: float = 0.0


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
# Phase 9.K: extended with imperative-prompt and instruction-line
# tokens (``add``, ``where``, ``following``, ``linkers``) so exercise-
# instruction lines like ``Add sa phrases or ang phrases or both where
# appropriate.`` are recognised as English-shaped and rejected by
# ``_looks_like_tagalog`` despite carrying 2 Tagalog markers (``sa``,
# ``ang``) in citation context.
#
# Phase 9.N: further extended with pedagogical-prose vocabulary
# (``occurs``, ``occurrence``, ``variant``, ``preceded``, ``followed``,
# ``consonant``, ``vowel``, ``alternant``, ``personal``, ``elsewhere``,
# ``always``, ``usually``, etc.) so descriptive grammar-prose lines
# like ``Note the occurrence of mo before nga and ninyo after nga.``
# tip ``_looks_like_tagalog``'s ``en > tgl`` test. These lines have
# 3 Tagalog markers cited (``mo``, ``nga``, ``ninyo``) but are English
# linguistic commentary, not natural Tagalog sentences.
_EN_MARKERS = {
    "the", "of", "and", "or", "to", "in", "is", "are", "was",
    "were", "this", "that", "these", "those", "with", "from",
    "for", "but", "not", "be", "have", "has", "had",
    "add", "where", "appropriate", "necessary", "following",
    "each", "using", "linkers", "phrases", "choose", "fill",
    "complete", "translate", "identify", "select",
    # 9.N pedagogical-prose additions
    "as", "also", "free",
    "note", "notice", "occur", "occurs", "occurrence", "occurred",
    "preceded", "preceding", "followed", "consonant", "consonants",
    "vowel", "vowels", "construction", "constructions",
    "alternant", "alternants", "variant", "variants",
    "phonemic", "phonetic", "context", "contexts",
    "elsewhere", "initially", "finally", "medially",
    "usually", "always", "often", "sometimes", "optional",
    "personal", "speaker", "speakers", "form", "forms",
    "describe", "describes", "compare", "compares", "observe",
    "indicates", "indicate",
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


def _pk91_looks_like_tagalog(text: str) -> bool:
    """PK91-specific Tagalog-shape check, relaxed from the strict
    :func:`_looks_like_tagalog` along two dimensions:

    1. **Joined-linker tolerance**: trailing ``-ng`` / ``-g``
       linker is stripped from each word when counting markers, so
       ``Mayroong`` (base ``mayroon`` + ``-ng``) and ``batang``
       (base ``bata`` + ``-ng``) contribute to the marker count.
    2. **Single-marker threshold**: ``≥ 1`` Tagalog marker
       qualifies (vs. strict's ``≥ 2``), provided there are zero
       English markers. Safe for PK91 because the cross-linguistic
       examples in PK91 (Welsh ``Gwelodd Sion ddraig.``, Irish,
       Chamorro citations) lack any Tagalog markers entirely; the
       block-structure context (sentences harvested only from
       numbered ``(N)`` example blocks) is a strong enough
       source-quality signal that ``Mapanganib lumapit sa ahas.``
       (4 tokens, 1 marker ``sa``) can be admitted without
       admitting wider noise.

    PK91-only because the broader (OCR-degraded) reference-grammar
    corpora accumulate substantial noise (~2100 additional
    exemplars including OCR fragments, English mixed-in, and
    bibliographic boilerplate) from the same relaxation."""
    toks = re.findall(r"[a-zA-Z']+", text.lower())
    if len(toks) < 3:
        return False
    single_char = sum(1 for t in toks if len(t) == 1)
    if single_char > len(toks) * 0.4:
        return False
    tgl: set[str] = set()
    for t in toks:
        if t in _TGL_MARKERS:
            tgl.add(t)
            continue
        # Joined -ng linker: try both ``X[:-2]`` (vowel-final stems
        # like batang → bata) and ``X[:-1]`` (n-final stems where
        # the linker n merges, like Mayroong → Mayroon).
        if t.endswith("ng") and len(t) > 3:
            if t[:-2] in _TGL_MARKERS:
                tgl.add(t[:-2])
            elif t[:-1] in _TGL_MARKERS:
                tgl.add(t[:-1])
    en = {t for t in toks if t in _EN_MARKERS}
    if len(tgl) >= 2:
        return len(en) <= len(tgl)
    if len(tgl) == 1:
        return len(en) == 0
    return False


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


# Phase 8.P cleanups for Wave 2.5 extractor noise.
#
# English-prefix labels seen in Ramos 1971 paradigm-example fields:
# ``Actor Focus:`` / ``Goal Focus:`` / etc.
_ENGLISH_PREFIX_RE = re.compile(
    r"^(?:Actor|Goal|Locative|Benefactive|Instrumental|Causative|Reciprocal|Distributive|Reason|Object|Directional|Aptative|Indicative|Intensive)\s+(?:Focus|Voice)?\s*:\s*",
    re.IGNORECASE,
)

# Parenthesized English-only prompts seen in R&C 1990 / R&G Intermediate
# exercises: ``(who) ang nagdala ng saging?`` (English-prompt slot).
# Detect a paren span containing 1-3 lowercase English words.
_ENGLISH_PAREN_RE = re.compile(r"\(\s*[a-z][a-z\s]{0,30}\s*\)")

# Quoted English-only spans: ``'men's wear'`` / ``'dialog'`` (single-
# quoted lowercase / mixed-case spans with at least one space inside or
# the whole span looking like one English word).
_QUOTED_ENGLISH_RE = re.compile(r"'[a-zA-Z][a-zA-Z\s']{1,30}'")

# Trailing parenthesized span at end of line, separated from the
# preceding text by whitespace. The match captures the inner content
# so ``_is_english_gloss`` can decide whether to strip.
_TRAILING_PAREN_RE = re.compile(r"\s+\(([^)]+?)\)\s*$")


# Phase 9.K cleanups for Wave 2 R&C 1990 extractor noise.
#
# Pedagogical grammar-tag prefix labels seen in R&C 1990 exercise
# blocks: ``Q:``, ``Question:``, ``Example:``, ``Sentence:``,
# ``Simple S:``, ``Conjunction:``, ``Negative:``, ``Counter-
# assumption:``, ``Affirmative command:``, etc. Closed list — the
# Tagalog idiom of using a noun-phrase + colon + clause (e.g.,
# ``Biyemes ngayon: ngumili ka naman.``) is preserved.
_GRAMMAR_TAG_PREFIX_RE = re.compile(
    r"^(?:"
    r"Affirmative\s+[Cc]ommand|Direct\s+[Cc]ommand|Indirect\s+[Cc]ommands?|"
    r"Question|Answer|Q|A|"
    r"Assertion|Assumption|Counter[-\s]?[Aa]ssumption|Counter[-\s]?[Ee]xpectation|"
    r"Awkward|Better|"
    r"Conjunction|Negatives?|"
    r"Example|Sentence|Simple\s+S(?:entences?)?|"
    r"In\s+Focus|Nominal(?:ized)?\s+[Cc]lause|"
    r"Statement|Active|Passive|Imperative|"
    # 9.M: S&O 1972 two-letter focus/voice abbreviations
    # (Actor/Object/Locative/Benefactive/Instrumental/Goal/
    # Reason/Directional/Causative/Reciprocal/Reflexive Focus
    # or Voice). 65 hits in wave3-so1972.jsonl.
    r"AF|OF|LF|BF|IF|GF|RF|DF|CF|PF|AV|OV|IV|DV|RV|LV|BV|CV|PV"
    r")\s*:\s+",
)

# 9.N: same two-letter focus/voice abbreviations, but the no-colon
# variant (S&O 1972 inconsistently uses ``AF Naghugas ng pinggan ang
# bata.`` interleaved with the colon-form ``AF: Naghugas …``). 19 hits
# in wave3-so1972. Also tolerates a hyphen-colon OCR-degenerate variant
# (``Of-: Abutin mo …``). Requires the abbreviation to be followed by
# at least one space + a capital letter, so we don't accidentally strip
# a 2-letter Tagalog word that's part of a longer sentence.
_FOCUS_VOICE_ABBREV_PREFIX_RE = re.compile(
    r"^(?:AF|OF|LF|BF|IF|GF|RF|DF|CF|PF|AV|OV|IV|DV|RV|LV|BV|CV|PV)"
    r"[-:]*\s+(?=[A-Z])"
)

# Leading paren-metadata that signals the predicate has been moved
# into the metadata block and the body is a bare argument-string
# (e.g., ``(verb tugtog. contemplated) si William ng gilara.``).
# Reject the whole line.
_LEADING_PAREN_REJECT_RE = re.compile(
    r"^\(\s*(?:verb|noun|adj|root|kuha)\b[^)]{0,80}\)\s+",
    re.IGNORECASE,
)

# Leading "(+ ...)" paren-metadata that prefixes a full sentence —
# e.g., ``(+ base reduplication) Lumakad siya nang dahan-dahan.``.
# Includes a malformed variant where the closing paren is missing
# and the prefix runs up to the first capitalized word:
# ``(+ pagka- and Umiyak siya nang pagkalakas-lakas.``. Strip the
# prefix, keep the rest.
_LEADING_PLUS_PAREN_RE = re.compile(
    r"^\(\s*\+\s+[^A-ZÑ)]{1,80}\)\s+"      # (+ ... ) closed
    r"|^\(\s*\+\s+[^A-ZÑ]{1,80}(?=[A-ZÑ])"  # (+ ... <Capital> open
)

# Mid-sentence parenthesized grammar-tag annotations:
# ``Bumuhos ang ulan kaya (Effect) nabasa si Jane.``. Closed list.
_MID_SENTENCE_TAG_RE = re.compile(
    r"\s*\(\s*(?:Effect|Cause|Result|Contrast|Purpose|Reproach|"
    r"Shift|Reason|Concession|Condition)\s*\)\s*",
)

# Trailing editor-annotation ``(?)`` marking the analyst's
# uncertainty about a form: ``binuksan (?)``. Strip including any
# adjacent terminal punctuation, restore a clean period below.
_TRAILING_PAREN_Q_RE = re.compile(r"\s*\(\s*\?\s*\)\s*\.?\s*$")

# Trailing exercise list-marker (``\.\s+a\.``, ``\s+f\.``, ``,\s+a\.``)
# appended to a complete sentence by the typesetter. Normalize to a
# single sentence-final period.
_TRAILING_LIST_MARKER_RE = re.compile(r"[.,]?\s+[a-z]\.\s*$")

# Slot-fill template patterns (paradigm tables): ``si / ang``,
# ``/ / X / .``. Lines containing them are slot-fill scaffolding,
# not real sentences.
_SLOT_FILL_RE = re.compile(r"\s/\s")

# Ungrammatical-marker mid-line: ``Nauntog ang mga *papandak.`` /
# ``Na-gong ang mga pangit ... *papangtt.``. Mid-line ``*<lower>`` is
# the analyst's "ungrammatical-as-shown" mark; the line is a
# starred-form citation, not a target parse.
_UNGRAM_MARKER_RE = re.compile(r"\*[a-z]")

# OCR-confidence-low characters in word-context.
#
# 9.K-original (RC1990):
# - ``€`` / ``£`` glyph substitutions for ``e`` / ``n``.
# - mid-word backslash (``san\palok``).
#
# 9.L additions (Ramos 1971 + general extractor robustness):
# - Mid-word ampersand (``Magb&on`` / ``Bil&ngin`` — ``&`` for ``a``).
# - Mid-lowercase digit (``Iba6n`` / ``n1ya`` / ``s1yete`` — digit
#   substituted for letter mid-word). Restricted to digits between
#   two lowercase letters to avoid false positives on legitimate
#   alphanumeric tokens (model numbers, addresses).
# - Slash followed by single trailing letter at word boundary
#   (``Iabant/e``). The single-trailing-letter constraint distinguishes
#   OCR garbage from legitimate alternation tokens
#   (``mister/misis`` / ``ako/kami`` / ``po/ho``) where both sides
#   of the slash are multi-letter Tagalog words.
_OCR_NOISE_CHAR_RE = re.compile(
    r"[€£]"                  # currency glyph substitution
    r"|\w\\\w"               # backslash mid-word
    r"|\w&\w"                # ampersand mid-word
    r"|[a-z][0-9][a-z]"      # digit between lowercase letters
    r"|[a-z]/[a-z](?![a-z])"  # slash + single-letter (not alternation)
)

# Truncation marker: line ends in ``...``. Trail-off indicates the
# original sentence is unfinished and not a target parse:
# ``Pinag-usapan nila ... kaya ...``.
_TRUNCATION_RE = re.compile(r"\.\.\.\s*$")

# Multi-space typesetter padding (paradigm-row alignment in OCR).
# Collapse to single space after all upstream cleanups.
_MULTI_SPACE_RE = re.compile(r"\s{2,}")


# 9.M (Wave 3 S&O 1972 extractor cleanup).
#
# Leading "(cf. ..." paren — pedagogical "compare with" marker
# wrapping a partially-OCR'd example sentence. 8 hits in
# wave3-so1972; the embedded Tagalog is uniformly heavily OCR-
# garbled and not worth retaining. Accept either trailing
# whitespace (``(cf. X``) or no whitespace (``(cf.JX`` — OCR-
# joined leading capital).
_CF_PAREN_LEADING_RE = re.compile(r"^\(\s*cf\.", re.IGNORECASE)

# Leading "(English-word ..." paren — pedagogical commentary in
# parens (``(Underlying sentence: ...)``, ``(Some speakers...``,
# ``(The same meanings...``). The line is linguistics-aside, not
# natural Tagalog. 7 hits in wave3-so1972 + 1 in wave3-rg-conv.
_ENGLISH_PAREN_LEADING_RE = re.compile(
    r"^\(\s*(?:Underlying|Some|Not|The|However|When|Where|While|"
    r"Most|All|This|These|That|Those|If|Note|Notice|Compare|"
    r"Observe|Hence|Therefore|There|See|For)\b",
)

# Section-reference character: linguistics text reaches the
# corpus when it has a ``§`` inline reference. Always pedagogical
# prose. 2 hits in wave3-so1972.
_SECTION_REF_RE = re.compile(r"§")

# Pedagogical-transformation arrows: ``A. ➔ B.`` / ``A. → B.``
# (S&O 1972 uses these to show pre→post-rule transformations).
# Both halves are typically valid Tagalog example sentences.
# Normalize the arrow to ``. `` so ``_split_sentences`` emits
# each half as a separate exemplar. 9 hits in wave3-so1972 +
# 1 in wave2-rg-intermediate.
_ARROW_RE = re.compile(r"\s*[→➔]\s*")


def _is_english_gloss(content: str) -> bool:
    """Heuristic: parenthesized span is an English gloss if it starts
    with an uppercase letter, contains ≥ 2 alphabetic tokens, and has
    no Tagalog markers. The capital-letter + ≥ 2-token gate keeps the
    rule from stripping legitimate Tagalog parentheticals (which tend
    to be single-word interjections or lowercase clitics) while still
    catching gloss spans like ``(A friend of mine.)`` or
    ``(Good morning.)`` that lack ``_EN_MARKERS`` function words."""
    text = content.strip()
    if not text or not text[0].isupper():
        return False
    toks = re.findall(r"[a-zA-Z']+", text.lower())
    if len(toks) < 2:
        return False
    tgl = {t for t in toks if t in _TGL_MARKERS}
    return len(tgl) == 0


def _strip_trailing_english_gloss(text: str) -> str:
    """Strip a trailing English-shaped parenthetical (e.g., a
    pedagogical-aid translation) from a line. The rest of the line
    (the Tagalog portion) is returned unchanged. Idempotent."""
    m = _TRAILING_PAREN_RE.search(text)
    if not m:
        return text
    if _is_english_gloss(m.group(1)):
        return text[:m.start()].rstrip()
    return text


def _clean_sentence_text(text: str) -> str | None:
    """Apply 8.P + 8.W + 9.K cleanups: strip English-prefix labels;
    strip Tagalog-source grammar-tag prefix labels; strip leading
    paren-metadata; strip mid-sentence and trailing tag annotations;
    reject paradigm-table / starred-form / OCR-garble lines. Return
    cleaned text, or ``None`` if the line should be dropped entirely."""
    text = text.strip()
    # 8.P Cleanup 1: strip English-prefix labels.
    text = _ENGLISH_PREFIX_RE.sub("", text)
    # 9.K Cleanup A: strip pedagogical grammar-tag prefixes
    # (``Q:``/``Example:``/``Simple S:``/``Counter-assumption:``).
    text = _GRAMMAR_TAG_PREFIX_RE.sub("", text)
    # 9.N: strip no-colon variant of S&O 1972 two-letter focus/
    # voice abbreviations (``AF Naghugas …`` / ``Of-: Abutin …``).
    text = _FOCUS_VOICE_ABBREV_PREFIX_RE.sub("", text)
    # 9.K Cleanup B: reject leading paren-metadata that pulled the
    # predicate out of the sentence body (``(verb tugtog. ...) ...``).
    if _LEADING_PAREN_REJECT_RE.match(text):
        return None
    # 9.M: reject S&O 1972 pedagogical paren-leading lines
    # (``(cf. ...``; ``(Underlying sentence: ...)``; ``(Some
    # speakers...``; ``(The same meanings...``); reject lines with
    # ``§`` section references (linguistics prose).
    if _CF_PAREN_LEADING_RE.match(text):
        return None
    if _ENGLISH_PAREN_LEADING_RE.match(text):
        return None
    if _SECTION_REF_RE.search(text):
        return None
    # 9.K Cleanup C: strip leading "(+ ...)" paren-metadata that
    # prefixes a complete sentence (closed and malformed variants).
    text = _LEADING_PLUS_PAREN_RE.sub("", text)
    # 9.K Cleanup D: strip mid-sentence grammar-tag annotations
    # (``kaya (Effect) nabasa``).
    text = _MID_SENTENCE_TAG_RE.sub(" ", text)
    # 9.K Cleanup E: strip trailing ``(?)`` editor-annotations and
    # 9.K Cleanup F: normalize trailing list-markers to ``.``.
    text = _TRAILING_PAREN_Q_RE.sub("", text)
    text = _TRAILING_LIST_MARKER_RE.sub(".", text)
    # 8.W: strip trailing parenthesized English glosses
    # (``(A friend of mine.)``) before the later paren-rejection check.
    text = _strip_trailing_english_gloss(text)
    # 8.P Cleanup 2: reject parenthesized English prompts (these are
    # exercise slots, not natural Tagalog).
    if _ENGLISH_PAREN_RE.search(text):
        return None
    # 8.P Cleanup 4: reject quoted English-only spans (foreign-word
    # citations the parser can't reasonably handle).
    if _QUOTED_ENGLISH_RE.search(text):
        return None
    # 9.K Cleanup G: reject slot-fill template rows (``si / ang``).
    if _SLOT_FILL_RE.search(text):
        return None
    # 9.K Cleanup H: reject lines with mid-line ungrammatical marker.
    if _UNGRAM_MARKER_RE.search(text):
        return None
    # 9.K Cleanup I: reject lines with OCR-noise characters.
    if _OCR_NOISE_CHAR_RE.search(text):
        return None
    # 9.K Cleanup J: reject lines ending in truncation ellipsis.
    if _TRUNCATION_RE.search(text):
        return None
    # 9.K Cleanup K: collapse multi-space typesetter padding.
    text = _MULTI_SPACE_RE.sub(" ", text)
    text = text.strip()
    if not text:
        return None
    return text


# Title abbreviations whose closing period must NOT trigger a
# sentence split. Tagalog: ``Gng.`` (Mrs.) / ``Bb.`` (Miss) / ``G.``
# (Ginoong — Mr.). English (in citations and loanwords): ``Mr.`` /
# ``Mrs.`` / ``Dr.`` / ``Sr.`` / ``Jr.`` / ``St.`` / ``Sgt.``. Each
# entry contributes a fixed-width negative lookbehind anchored at the
# closing period.
_TITLE_ABBREVS = ("Gng", "Bb", "Mrs", "Mr", "Dr", "Sr", "Jr", "St", "Sgt", "G")

_SENTENCE_SPLIT_RE = re.compile(
    "".join(f"(?<!\\b{a}\\.)" for a in _TITLE_ABBREVS)
    + r"(?<=[.!?])\s+(?=[A-Z\"'(])"
)


def _split_sentences(text: str) -> list[str]:
    """Cleanup 3: split multi-sentence captures on terminal punctuation
    followed by uppercase-or-quote. The closing period of a Tagalog or
    English title abbreviation (``Gng.``, ``Bb.``, ``Mr.``, etc.) is
    NOT treated as sentence-final — see ``_TITLE_ABBREVS``. Returns a
    list of one-sentence strings.

    9.M: pre-normalize S&O 1972 pedagogical-transformation arrows
    (``➔`` / ``→``) to a sentence boundary so each half (pre-arrow
    + post-arrow) is emitted as a separate exemplar. Both halves
    are typically valid Tagalog example sentences (S&O uses arrows
    to show pre→post-rule transformations). When the pre-arrow
    text already ends in terminal punctuation, replace the arrow
    with whitespace (not ``. ``) so we don't accumulate ``..``."""
    text = re.sub(r"([.!?])\s*[→➔]\s*", r"\1 ", text)
    text = _ARROW_RE.sub(". ", text)
    parts = _SENTENCE_SPLIT_RE.split(text)
    return [p.strip() for p in parts if p.strip()]


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
            raw = m.group(1).strip()
        else:
            raw = stripped

        for sent in _split_sentences(raw):
            cleaned = _clean_sentence_text(sent)
            if cleaned is None:
                continue
            if not _is_sentence_shape(cleaned):
                continue
            if not _looks_like_tagalog(cleaned):
                continue

            sent_idx += 1
            loc = f"{chapter}"
            if section:
                loc += f"/{section}"
            loc += f"/sent-{sent_idx}"
            yield Exemplar(
                source="rc1990",
                locator=loc,
                text_raw=cleaned,
                text_normalized=normalize_orthography(cleaned),
                has_gloss=False,
                gloss_en=None,
                marked_ungrammatical=cleaned.startswith(("*", "?")),
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
            raw = m.group(2).strip()
            kind = "dialog"
        else:
            mn = re.match(r"^\s*\d+\.\s+(.+)$", line)
            if mn:
                raw = mn.group(1).strip()
                kind = "numbered"
            else:
                raw = stripped
                kind = "prose"

        for sent in _split_sentences(raw):
            cleaned = _clean_sentence_text(sent)
            if cleaned is None:
                continue
            if not _is_sentence_shape(cleaned):
                continue
            if not _looks_like_tagalog(cleaned):
                continue

            sent_idx += 1
            yield Exemplar(
                source="rg-intermediate",
                locator=f"page-{page}/{kind}/sent-{sent_idx}",
                text_raw=cleaned,
                text_normalized=normalize_orthography(cleaned),
                has_gloss=False,
                gloss_en=None,
                marked_ungrammatical=cleaned.startswith(("*", "?")),
                ocr_quality="clean-ocr",
            )


# === Source 6: S&O 1972 + Source 7: R&G 1981 Conversational ===============
#
# Both are pdftotext -layout outputs of Acrobat-OCR'd PDFs. Pages are
# delimited by form-feed (``\f``). Front matter (TOC, preface, copyright)
# precedes the first numbered body page; the body extends to the index.


# Word-initial ``rn`` before a vowel was originally ``m`` (the Acrobat-OCR
# pass mis-renders the ``m`` glyph as ``rn`` in some italic body text).
# Conservative: word-initial only, vowel-following only — avoids the
# Spanish-loan stem ``barniz`` and the ``arnis`` martial-art term.
_OCR_RN_INITIAL_RE = re.compile(r"\brn(?=[aeiouAEIOU])")


def _ocr_cleanup(text: str) -> str:
    """OCR-cleanup pass for Acrobat-OCR Wave 3 sources: word-initial
    ``rn`` before a vowel → ``m``. Applied on top of the standard
    ``normalize_orthography`` so the parser sees ``mga`` not ``rnga``."""
    return _OCR_RN_INITIAL_RE.sub("m", text)


def _pages_from_pdftotext(path: Path) -> Iterator[tuple[int, str]]:
    """Yield ``(page_num, page_text)`` pairs from a pdftotext -layout
    file. Page numbers are 1-indexed PDF pages (not book pages — the
    PDF includes front matter the book's page numbering excludes)."""
    text = path.read_text(encoding="utf-8")
    for i, page in enumerate(text.split("\f"), start=1):
        if page.strip():
            yield i, page


# Page-header banner: ALL-CAPS chapter title + right-aligned page
# number, e.g. ``VERBALS  329`` or ``NOMINALS AND THEIR EXPANSIONS  91``.
_PAGE_HEADER_RE = re.compile(r"^[A-Z][A-Z'\- ]{2,40}\s+\d{1,3}\s*$")

# Phonetic notation: ``/ba·lu·n bah/`` etc. These are not natural
# sentences; reject anywhere they appear inside a line.
_PHONETIC_RE = re.compile(r"/[a-z'\- :·]+/")


def _looks_like_index_page(page_text: str) -> bool:
    """Heuristic for S&O 1972 index pages: > 40% of non-blank lines
    end in ``..., NNN`` (comma-separated page-number references)."""
    lines = [ln for ln in page_text.splitlines() if ln.strip()]
    if not lines:
        return False
    index_lines = sum(
        1 for ln in lines
        if re.search(r",\s*\d{1,3}\s*(?:[a-z]{0,3})?\s*$", ln)
    )
    return index_lines >= 0.4 * len(lines)


def _emit_sentence(raw_text: str) -> str | None:
    """Pass ``raw_text`` through the Wave-2.5 cleanup pipeline + the
    Tagalog-marker + sentence-shape filters. Return cleaned text or
    None if the line should be dropped.

    Caller is responsible for handling per-sentence splitting via
    ``_split_sentences`` before calling this."""
    cleaned = _clean_sentence_text(raw_text)
    if cleaned is None:
        return None
    if _PHONETIC_RE.search(cleaned):
        return None
    if not _is_sentence_shape(cleaned):
        return None
    if not _looks_like_tagalog(cleaned):
        return None
    return cleaned


def extract_so1972() -> Iterator[Exemplar]:
    """Walk S&O 1972 *Tagalog Reference Grammar* (pdftotext output)
    for Tagalog example sentences.

    Skip PDF pages 1-23 (front matter: cover, copyright, TOC, preface)
    and the INDEX (heuristic via ``_looks_like_index_page``). Reject
    lines containing brace-alternation paradigm content (``{`` / ``}``)
    or phonetic notation (slash-bracketed IPA-style strings)."""
    path = REFERENCES_DIR / "Tagalog-Reference-Grammar-Schachter-Otanes.txt"
    sent_idx = 0

    for page_num, page_text in _pages_from_pdftotext(path):
        if page_num < 24:
            continue
        if _looks_like_index_page(page_text):
            continue

        for raw_line in page_text.splitlines():
            stripped = raw_line.strip()
            if not stripped:
                continue
            if _PAGE_HEADER_RE.match(stripped):
                continue
            # Brace-alternation paradigm lines.
            if "{" in stripped or "}" in stripped:
                continue
            for sent in _split_sentences(stripped):
                cleaned = _emit_sentence(sent)
                if cleaned is None:
                    continue
                sent_idx += 1
                yield Exemplar(
                    source="so1972",
                    locator=f"page-{page_num}/sent-{sent_idx}",
                    text_raw=cleaned,
                    text_normalized=_ocr_cleanup(normalize_orthography(cleaned)),
                    has_gloss=False,
                    gloss_en=None,
                    marked_ungrammatical=cleaned.startswith(("*", "?")),
                    ocr_quality="acrobat-ocr",
                )


# Speaker-tagged dialog line: ``BEN:`` / ``LINDA:`` / ``A:`` and the
# numbered-speaker variants ``S1:`` / ``S2:`` / ``S3:`` / ``S4:`` used
# in R&G Conversational drill-exercise dialogs. Also tolerates the
# OCR-degenerate ``Sl:`` / ``Sll:`` (digit ``1`` mis-rendered as
# lowercase ``l``) which appear frequently in the Acrobat-OCR output.
# Up to 8 chars after the leading uppercase letter, all of which must
# be uppercase / digit / lowercase-l.
_DIALOG_SPEAKER_RE = re.compile(r"^([A-Z][A-Zl0-9]{0,8})\s*:\s+(.+)$")

# Parenthetical-direction speaker tag prefix: ``S1 (to S2):`` /
# ``B (to C):`` / ``(to S3):`` / ``(To S2)`` (without colon, seen in
# OCR), plus the sentence-type-label variants ``S1 (Sentence):`` /
# ``S3 (Response):`` used in some R&G Conv drill blocks. Strip the
# full prefix; what's left is the actual utterance. Closing-paren OCR
# variants tolerated: paren may be ``)`` or ``:`` (a common Acrobat-
# OCR misread on tight italic punctuation).
_DIRECTION_PREFIX_RE = re.compile(
    r"^(?:\(?\s*[A-Z][A-Zl0-9]{0,8}\s*)?"
    r"\(\s*(?:[Tt]o\s+[A-Z][A-Zl0-9]{0,8}|"
    r"(?:Sentence|Response|Question|Answer|Echo|Reply|Sagot))"
    r"\s*[\):]\s*[:)]?\s*"
)

# Column-gutter signature in pdftotext -layout output for two-column
# pages: ≥ 10 consecutive whitespace chars internal to a non-empty
# line. Beyond that threshold, the run almost always reflects a column
# boundary in the source PDF rather than rendered intra-sentence
# spacing (the latter is generally 1-3 chars even on justified text).
_COLUMN_GUTTER_RE = re.compile(r"\s{10,}")


def _split_column_gutter(line: str) -> list[str]:
    """Split a line on column-gutter-shaped whitespace runs (see
    ``_COLUMN_GUTTER_RE``). Returns one segment per column-segment;
    each is stripped but otherwise unchanged. Caller's downstream
    sentence-shape + Tagalog-marker filters reject the junk halves
    that frequently emerge from this split (English column-bleed,
    stray fragments)."""
    return [seg.strip() for seg in _COLUMN_GUTTER_RE.split(line) if seg.strip()]


def extract_rg_conversational() -> Iterator[Exemplar]:
    """Walk R&G 1981 Conversational Tagalog (pdftotext output).

    Sibling of ``extract_rg_intermediate`` — same authors, same era,
    similar pedagogical format (dialogs + drill exercises). Skip PDF
    pages 1-12 (cover, plan-of-text, intro, TOC). Recognize speaker-
    tagged dialog lines (``BEN: ...``, ``S1: ...``, ``S1 (to S2): ...``)
    and numbered exercises (``1. ...``)."""
    path = REFERENCES_DIR / "814610085-Conversational-Tagalog-a-Functional-Situational-Approach.txt"
    sent_idx = 0

    for page_num, page_text in _pages_from_pdftotext(path):
        if page_num < 13:
            continue

        for raw_line in page_text.splitlines():
            stripped = raw_line.strip()
            if not stripped:
                continue
            if _PAGE_HEADER_RE.match(stripped):
                continue

            # Split on column-gutter shape FIRST. R&G Conv's pdftotext
            # output frequently joins adjacent columns (e.g., an
            # English heading on the left and a dialog line on the
            # right) into a single physical line separated by a wide
            # whitespace gap. Treating each gutter-segment as an
            # independent line lets the speaker-tag / numbered /
            # direction-prefix checks below operate column-locally
            # rather than against the full bled line. Also extract a
            # leading-numbered prefix from the raw line, for the case
            # of a numbered drill item that fits in a single column.
            numbered_match = re.match(r"^\s*\d+\.\s+(.+)$", raw_line)
            for segment in _split_column_gutter(stripped):
                # Strip parenthetical-direction speaker tag prefix
                # (``S1 (to S2): ...`` / ``B (to C): ...``).
                dm = _DIRECTION_PREFIX_RE.match(segment)
                if dm:
                    line_text = segment[dm.end():].strip()
                    kind = "dialog"
                else:
                    m = _DIALOG_SPEAKER_RE.match(segment)
                    if m:
                        line_text = m.group(2).strip()
                        kind = "dialog"
                    elif numbered_match and segment == stripped:
                        line_text = numbered_match.group(1).strip()
                        kind = "numbered"
                    else:
                        line_text = segment
                        kind = "prose"

                for sent in _split_sentences(line_text):
                    cleaned = _emit_sentence(sent)
                    if cleaned is None:
                        continue
                    sent_idx += 1
                    yield Exemplar(
                        source="rg-conversational",
                        locator=f"page-{page_num}/{kind}/sent-{sent_idx}",
                        text_raw=cleaned,
                        text_normalized=_ocr_cleanup(normalize_orthography(cleaned)),
                        has_gloss=False,
                        gloss_en=None,
                        marked_ungrammatical=cleaned.startswith(("*", "?")),
                        ocr_quality="acrobat-ocr",
                    )


# === Source 5: Kroeger 1991 (Phrase Structure / LFG dissertation) =========
#
# PK91 = Paul Kroeger's 1991 Stanford PhD dissertation, "Phrase Structure
# and Grammatical Relations in Tagalog". LFG-native treatment; cleanly
# typeset (native PDF, not OCR). Examples follow the LFG dissertation
# convention: numbered example blocks ``(N)`` with optional sub-divisions
# ``a.``, ``b.``, ``c.``; three-line layout per example (Tagalog surface
# with `=`-clitic and `-`-morpheme boundaries / morpheme gloss in
# uppercase grammar labels / English translation indented further).
#
# Hand-curated dissertation examples are higher-signal than OCR'd
# reference-grammar prose. Expect 100-200 high-quality exemplars across
# the ~210 numbered blocks (each may have 1-4 sub-divisions; we filter
# to Tagalog-shaped surfaces only — PK91 also presents Welsh, Irish,
# and other cross-linguistic data).
#
# PK91 morpheme conventions to strip:
#   * ``=`` separates clitics (``ang=mga=bata``) → replace with space
#   * ``-`` separates affixes (``B-um-ili``, ``b-in-igy-an``,
#     ``Ma-ta-talino``) → remove between alphabetic chars
# The analyzer's ``merge_hyphen_compounds`` tokenizer handles the rare
# genuine orthographic hyphens (``araw-araw``, ``mag-isa``) downstream.

# Block label: ``(N)`` opens an example; ``(N) a.`` or ``a.``-indented
# lines enumerate sub-examples within the block.
_PK91_BLOCK_LABEL_RE = re.compile(r"^\((\d+)\)\s*(.*)$")
_PK91_SUBLABEL_RE = re.compile(r"^([a-h])\.\s+(.+)$")

# Gap-marker notation for abstract unbounded-dependency examples
# (``__nom``, ``__gen``, ``__dat`` — Kroeger ch. 7). These are
# theoretical f-structure abstractions, not parseable Tagalog —
# reject any exemplar containing them.
_PK91_GAP_MARKER_RE = re.compile(r"__\w+")

# Leading ungrammaticality / marginal-acceptance markers PK91 uses:
# ``(*)``, ``(?)``, ``(*?)`` — strip from surface and set
# ``marked_ungrammatical=True``.
_PK91_LEADING_MARKER_RE = re.compile(r"^\(\s*[*?]+\s*\)\s*")

# Subscript co-indexing notation (LFG binding/coreference): pronouns
# and a small closed list of proper names carry a subscript
# ``i``/``j``/``k`` that pdftotext renders adjacent to the word
# (``niyai`` for canonical ``niya``, ``Mariai`` for canonical
# ``Maria``). The strip is two-tier: (a) pronoun-base set anchors
# detection of which subscript letters are in use for this
# exemplar; (b) any word whose stripped stem matches the pronoun
# OR proper-name base set has the letter stripped. The proper-
# name set is kept short (the only PK91 proper names that
# actually appear with subscripts are Juan, Maria, Rosa) to
# avoid false-stripping Title-Case-initial verbs like ``Nahuli``
# / ``Sinabi`` that happen to end in subscript letters.
_PK91_PRONOUN_SUBSCRIPT_BASES = frozenset({
    "niya", "siya", "kaniya", "nila", "kanila", "ako", "akin",
    "sino", "kanino", "ano", "ikaw",
})
_PK91_PROPER_SUBSCRIPT_BASES = frozenset({
    "juan", "maria", "rosa",
})
_PK91_SUBSCRIPT_LETTERS = frozenset("ijk")


def _pk91_strip_subscripts(text: str) -> str:
    """Remove subscript co-indexing letters from a PK91 surface line.
    Detection is pronoun-triggered: a pronoun-base + subscript
    letter (``niyai``, ``kaniyaj``, ``Sinoi``) flags that letter as
    a binding index for the exemplar. Words whose stripped stem
    matches either the pronoun-base or the proper-name set
    (``Juan``, ``Maria``, ``Rosa``) get the letter stripped."""
    words = text.split()
    letters_used: set[str] = set()
    for w in words:
        bare = w.rstrip(".,;:!?")
        if len(bare) >= 4 and bare[-1].lower() in _PK91_SUBSCRIPT_LETTERS:
            stem = bare[:-1].lower()
            if stem in _PK91_PRONOUN_SUBSCRIPT_BASES:
                letters_used.add(bare[-1].lower())
    if not letters_used:
        return text

    def _strip(w: str) -> str:
        suffix_len = len(w) - len(w.rstrip(".,;:!?"))
        bare = w[:len(w) - suffix_len] if suffix_len else w
        if len(bare) < 4:
            return w
        if bare[-1].lower() not in letters_used:
            return w
        stem = bare[:-1].lower()
        if (stem in _PK91_PRONOUN_SUBSCRIPT_BASES
                or stem in _PK91_PROPER_SUBSCRIPT_BASES):
            return bare[:-1] + w[len(w) - suffix_len:]
        return w

    return " ".join(_strip(w) for w in words)


def _clean_pk91_surface(text: str) -> str:
    """Strip PK91 linguistic notation to recover the orthographic
    surface form. Order of operations:

    1. Mid-sentence parenthetical strip — PK91 marks optional
       constituents like ``(ang)`` / ``(na)`` / ``(ni Maria)`` in
       parentheses; the surface form excludes them.
    2. ``=g`` linker fold — PK91's ``=g`` after an n-final stem
       (``Mayroon=g`` / ``mayaman=g``) is the ``-ng`` linker
       allomorph where the stem's final ``n`` is already in place;
       join the ``g`` directly to the prior word (``Mayroong`` /
       ``mayamang``).
    3. ``=`` clitic boundaries → space (general case after the
       ``=g`` fold).
    4. ``-Ø`` / ``Ø`` zero-morpheme markers → dropped.
    5. ``-`` morpheme boundaries between alphabetic chars → removed.
    6. ``[...]`` constituent brackets → stripped (content preserved).
    7. Medial ``.`` between letters → space — handles PK91's
       compound-marker convention (``pambansang.awit`` =
       "national.anthem") and abbreviation forms (``Dr.Lopez`` =
       "Dr. Lopez") uniformly.
    8. Whitespace collapse.
    9. Pronoun-triggered subscript co-indexing removed."""
    text = re.sub(r"\s*\([^)]*\)\s*", " ", text)
    text = re.sub(r"=g\b", "g", text)
    text = text.replace("=", " ")
    text = text.replace("-Ø", "").replace("Ø", "")
    text = re.sub(r"(?<=[a-zA-Z])-(?=[a-zA-Z])", "", text)
    text = text.replace("[", "").replace("]", "")
    text = re.sub(r"(?<=[a-zA-Z])\.(?=[a-zA-Z])", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = _pk91_strip_subscripts(text)
    return text


def extract_kroeger1991() -> Iterator[Exemplar]:
    """Walk Kroeger 1991 PhD dissertation (PK91) for Tagalog example
    sentences. Native-PDF source (no OCR cleanup needed). Skip PDF
    pages 1-12 (front matter: title, abstract, TOC, dedication).
    Cross-linguistic examples (Welsh, Irish, Chamorro, etc.) are
    filtered by the standard ``_looks_like_tagalog`` heuristic."""
    path = REFERENCES_DIR / "PK91-Thesis-Revised.txt"

    for page_num, page_text in _pages_from_pdftotext(path):
        if page_num < 13:
            continue
        yield from _pk91_extract_from_page(page_num, page_text)


def _pk91_extract_from_page(
    page_num: int, page_text: str,
) -> Iterator[Exemplar]:
    """Extract example-block exemplars from one PK91 page. State
    machine tracks the current block index; for each subsequent
    non-blank line, check for sub-label or fall through to next-block
    transition."""
    current_block_n: str | None = None

    for line in page_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        block_m = _PK91_BLOCK_LABEL_RE.match(stripped)
        if block_m:
            current_block_n = block_m.group(1)
            rest = block_m.group(2).strip()
            if not rest:
                continue
            sub_m = _PK91_SUBLABEL_RE.match(rest)
            if sub_m:
                yield from _pk91_yield_exemplar(
                    page_num, current_block_n,
                    sub_m.group(1), sub_m.group(2),
                )
            else:
                yield from _pk91_yield_exemplar(
                    page_num, current_block_n, None, rest,
                )
            continue

        if current_block_n is None:
            continue

        sub_m = _PK91_SUBLABEL_RE.match(stripped)
        if sub_m:
            yield from _pk91_yield_exemplar(
                page_num, current_block_n,
                sub_m.group(1), sub_m.group(2),
            )


def _pk91_yield_exemplar(
    page_num: int, block_n: str, sub_letter: str | None, raw_surface: str,
) -> Iterator[Exemplar]:
    """Clean + filter a candidate PK91 surface line. Yields zero,
    one, or two Exemplars:

    * Zero if the line fails the Tagalog-shape / sentence-shape
      filters or contains theoretical gap markers.
    * One in the common case (no parenthetical optional elements).
    * Two when the raw surface contains a parenthetical optional
      element like ``(ang)`` / ``(na)`` / ``(ni Maria)`` — emits
      both the bare variant (parenthetical content excluded) at
      the canonical locator and the elaborated variant
      (parenthetical content included as a regular token) at a
      ``-paren``-suffixed locator. Per Kroeger's notation
      convention, both forms are grammatical."""
    # Reject abstract gap-marker examples (Kroeger ch. 7 unbounded-
    # dependency notation, not parseable Tagalog).
    if _PK91_GAP_MARKER_RE.search(raw_surface):
        return

    # Strip leading ungrammaticality marker ``(*)`` / ``(?)`` for the
    # surface, but capture it as marked_ungrammatical signal.
    leading_marker_m = _PK91_LEADING_MARKER_RE.match(raw_surface)
    if leading_marker_m:
        raw_surface = raw_surface[leading_marker_m.end():]
        explicit_ungram = True
    else:
        explicit_ungram = False

    has_parens = "(" in raw_surface and ")" in raw_surface

    if has_parens:
        # Bare variant: parenthetical content excluded.
        raw_bare = re.sub(r"\s*\([^)]*\)\s*", " ", raw_surface)
        ex_bare = _pk91_build_exemplar(
            page_num, block_n, sub_letter, raw_bare,
            explicit_ungram, variant_suffix=None,
        )
        if ex_bare is not None:
            yield ex_bare
        # Elaborated variant: parenthetical content kept inline.
        raw_elab = re.sub(r"\(([^)]+)\)", r"\1", raw_surface)
        ex_elab = _pk91_build_exemplar(
            page_num, block_n, sub_letter, raw_elab,
            explicit_ungram, variant_suffix="paren",
        )
        if ex_elab is not None:
            yield ex_elab
    else:
        ex = _pk91_build_exemplar(
            page_num, block_n, sub_letter, raw_surface,
            explicit_ungram, variant_suffix=None,
        )
        if ex is not None:
            yield ex


def _pk91_build_exemplar(
    page_num: int, block_n: str, sub_letter: str | None,
    raw_surface: str, explicit_ungram: bool,
    variant_suffix: str | None,
) -> Exemplar | None:
    """Internal: clean a raw PK91 surface, run the sentence-shape +
    Tagalog-shape filters, and construct an Exemplar. Returns None
    if filters fail. The ``variant_suffix`` is appended to the
    locator (e.g., ``-paren`` for the elaborated parenthetical
    variant); None means the canonical locator without suffix."""
    cleaned = _clean_pk91_surface(raw_surface)
    if not _is_sentence_shape(cleaned):
        return None
    if not _pk91_looks_like_tagalog(cleaned):
        return None

    base_locator = (
        f"page-{page_num}/ex-{block_n}{sub_letter}"
        if sub_letter else f"page-{page_num}/ex-{block_n}"
    )
    locator = (
        f"{base_locator}-{variant_suffix}" if variant_suffix
        else base_locator
    )
    return Exemplar(
        source="kroeger1991",
        locator=locator,
        text_raw=cleaned,
        text_normalized=normalize_orthography(cleaned),
        has_gloss=True,
        gloss_en=None,
        marked_ungrammatical=explicit_ungram or cleaned.startswith(("*", "?")),
        ocr_quality="native-pdf",
    )


# === Source 6: Ramos 1971 Dictionary (verb-example sentences) =============


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

        if not current_headword:
            continue

        for sent in _split_sentences(stripped):
            cleaned = _clean_sentence_text(sent)
            if cleaned is None:
                continue
            if not _is_sentence_shape(cleaned):
                continue
            if not _looks_like_tagalog(cleaned):
                continue

            sent_idx += 1
            yield Exemplar(
                source="ramos1971",
                locator=f"entry-{current_headword}/sent-{sent_idx}",
                text_raw=cleaned,
                text_normalized=normalize_orthography(cleaned),
                has_gloss=False,
                gloss_en=None,
                marked_ungrammatical=cleaned.startswith(("*", "?")),
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
        ("wave3-so1972.jsonl", extract_so1972()),
        ("wave3-rg-conversational.jsonl", extract_rg_conversational()),
        ("wave4-kroeger1991.jsonl", extract_kroeger1991()),
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
    ("wave3-so1972.jsonl", "wave3-so1972-parse-results.jsonl", 500),
    ("wave3-rg-conversational.jsonl", "wave3-rg-conversational-parse-results.jsonl", 500),
    ("wave4-kroeger1991.jsonl", "wave4-kroeger1991-parse-results.jsonl", None),
]


def oov_probe(text: str) -> list[str]:
    """Tokenize ``text`` and return surface forms whose morph
    analyses are all ``pos='_UNK'`` (the analyzer's fallback for
    words it cannot derive any paradigm form for). Used by Phase 8.J
    to surface lex-OOV signal even on zero-parse-no-fragment rows
    where the parser produces no diagnostics.

    Filters out pure-punctuation tokens (``'``, ``(``, ``:``, etc.)
    and single-character tokens (almost always OCR character-spacing
    artifacts, not real OOV words).

    **Phase 8.Q**: applies ``split_linker_ng`` between tokenization
    and morph analysis so the probe mirrors the actual parser
    pipeline (``src/tgllfg/core/pipeline.py`` line 130 — Phase 4
    §7.5 detaches the bound ``-ng`` linker before morph). Without
    this step, vowel-final clitic-glued forms like ``akong`` (=
    ``ako`` + ``-ng``), ``bang`` (= ``ba`` + ``-ng``), ``anong``
    (= ``ano`` + ``-ng``), ``magandang`` (= ``maganda`` + ``-ng``)
    were reported as OOV — the probe's pre-8.Q output overstated
    the lex-gap signal and produced a spurious "clitic-fused-token
    cluster" in the Wave 3 audit (covered in
    ``docs/coverage.md`` § Wave 1 pilot baseline + Phase 8 closure
    summary, and corrected in ``docs/analysis-choices.md``
    "Phase 8.Q").

    Module-level since Phase 8.Q so the probe is importable for
    testing.
    """
    from tgllfg.text.tokenizer import tokenize
    from tgllfg.text.clitics import (
        split_apostrophe_t,
        split_apostrophe_y,
        split_linker_ng,
    )
    from tgllfg.text.multiword import merge_hyphen_compounds
    from tgllfg.morph.analyzer import analyze_tokens

    try:
        toks = tokenize(text)
        # Phase 9.X.c5: full pre-parse pipeline applied so the OOV
        # report reflects the parser's actual view of the token
        # stream. Pre-9.X.c5 only ``split_linker_ng`` was applied,
        # which caused hyphen-rejoined compounds (``tag-init`` →
        # ``taginit``), X-Y reduplications (``manaka-naka`` →
        # ``manakanaka``), apostrophe-clitic contractions
        # (``rito'y`` → ``rito`` + ``ay``; ``Maria't`` →
        # ``Maria`` + ``at``) to be misreported as OOV on their
        # split halves even when the parser correctly handles the
        # joined / synthesised form. The full pipeline mirrors
        # ``src/tgllfg/core/pipeline.py``.
        toks = split_apostrophe_t(toks)
        toks = split_apostrophe_y(toks)
        toks = split_linker_ng(toks)
        toks = merge_hyphen_compounds(toks)
        analyses = analyze_tokens(toks)
        unk: list[str] = []
        for t, a_list in zip(toks, analyses):
            if not re.search(r"[a-zA-Z]", t.surface):
                continue
            if len(t.surface) < 2:
                continue
            # The synthetic linker token from split_linker_ng has
            # surface ``-ng`` and pos PART — not an OOV signal,
            # skip explicitly to avoid noise.
            if t.surface == "-ng":
                continue
            if not a_list:
                unk.append(t.surface)
                continue
            if all(getattr(a, "pos", None) == "_UNK" for a in a_list):
                unk.append(t.surface)
        return unk
    except Exception:
        return []


def cmd_parse() -> None:
    from tgllfg.core.pipeline import parse_text_with_fragments

    import random
    rng = random.Random(42)

    # Phase 9.X.pre-1.19: reset the monitor log + last-item file at
    # the start of each audit run so external tail / monitor loops
    # see fresh state.
    AUDIT_MONITOR_LOG.unlink(missing_ok=True)
    AUDIT_LAST_ITEM.unlink(missing_ok=True)
    grand_start = time.time()
    grand_latencies: list[float] = []
    grand_parsed = 0
    grand_total = 0
    _audit_log("=== Audit start ===")

    for in_name, out_name, sample_cap in _PARSE_SOURCES:
        in_path = EXEMPLARS_DIR / in_name
        out_path = EXEMPLARS_DIR / out_name
        if not in_path.exists():
            print(f"  (skip {in_name}; not found)")
            continue
        print(f"\n[parse] {in_name}")
        wave_parsed, wave_total, wave_latencies = _parse_one(
            in_path, out_path, parse_text_with_fragments,
            sample_cap, rng, oov_probe,
        )
        grand_parsed += wave_parsed
        grand_total += wave_total
        grand_latencies.extend(wave_latencies)

    grand_elapsed = time.time() - grand_start
    pct = grand_parsed / grand_total * 100 if grand_total else 0
    _audit_log(
        f"=== AUDIT COMPLETE: {grand_parsed}/{grand_total} "
        f"({pct:.2f}%)  wall={grand_elapsed:.0f}s ==="
    )
    if grand_latencies:
        mn = min(grand_latencies)
        mx = max(grand_latencies)
        avg = sum(grand_latencies) / len(grand_latencies)
        p95 = sorted(grand_latencies)[int(len(grand_latencies) * 0.95)]
        _audit_log(
            f"  GRAND latency: min={mn:.2f}s avg={avg:.2f}s "
            f"p95={p95:.2f}s max={mx:.2f}s"
        )
    AUDIT_LAST_ITEM.unlink(missing_ok=True)


def _audit_log(line: str) -> None:
    """Append a timestamped line to the audit monitor log (Phase
    9.X.pre-1.19) AND echo to stderr for live tail. Per-line flush
    so external monitors see updates immediately."""
    ts = time.strftime("%H:%M:%S")
    msg = f"[{ts}] {line}"
    with AUDIT_MONITOR_LOG.open("a", encoding="utf-8") as fh:
        fh.write(msg + "\n")
        fh.flush()
    print(msg, file=sys.stderr, flush=True)


def _write_last_item(payload: dict) -> None:
    """Atomically rewrite /tmp/audit_monitor.last_item with the
    sentence currently being parsed. External monitors can read
    this file to detect hangs (start_ts vs now)."""
    tmp = AUDIT_LAST_ITEM.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload), encoding="utf-8")
    import os as _os
    _os.replace(tmp, AUDIT_LAST_ITEM)


def _parse_one(
    in_path: Path,
    out_path: Path,
    parse_fn,
    sample_cap: int | None,
    rng,
    oov_probe,
) -> tuple[int, int, list[float]]:
    """Inner parser-driver loop for a single JSONL input file.

    Phase 9.X.pre-1.19: each parse is wrapped in a SIGALRM-based
    per-item timeout (ITEM_TIMEOUT_S seconds). Items that exceed
    the cap are recorded with ``bucket="parse-timeout"`` and the
    loop continues. Per-item latency is captured in the record
    (``latency_s``) and rolled up into periodic progress lines
    (every 25 items + at wave end) written to
    ``/tmp/audit_monitor.log``."""

    n = 0
    bucket_counts: Counter[str] = Counter()
    latencies: list[float] = []
    with in_path.open(encoding="utf-8") as in_fh:
        records = [line for line in in_fh]
    if sample_cap is not None and len(records) > sample_cap:
        records = rng.sample(records, sample_cap)
        _audit_log(f"[{in_path.name}] sampling {sample_cap} of "
                   f"{len(records)} records (seed=42)")

    _audit_log(f"=== Wave: {in_path.name} ({len(records)} sents) ===")
    wave_start = time.time()
    with out_path.open("w", encoding="utf-8") as out_fh:
        for i, line in enumerate(records, 1):
            ex = json.loads(line)
            text = ex["text_normalized"]
            t0 = time.time()
            _write_last_item({
                "wave": in_path.name, "i": i, "n": len(records),
                "locator": ex["locator"], "text": text[:120],
                "start_ts": t0,
            })
            signal.alarm(ITEM_TIMEOUT_S)
            try:
                result = parse_fn(text, n_best=3)
                signal.alarm(0)
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
                diag_kinds: Counter[str] = Counter()
                oov: list[str] = []
                if n_parses == 0:
                    # 8.J: walk all fragments, not just [0].
                    all_diags: list = []
                    for frag in result.fragments:
                        diags = getattr(frag, "diagnostics", []) or []
                        all_diags.extend(diags)
                    if all_diags:
                        diag_summary = str(all_diags[0])[:200]
                        for d in all_diags:
                            s = str(d)
                            m = re.search(
                                r"kind=['\"](\w[\w-]*)['\"]", s
                            )
                            if m:
                                diag_kinds[m.group(1)] += 1
                    # 8.J: probe lex-OOV via morph analyzer for ALL
                    # zero-parse rows (including zero-parse-no-fragment).
                    oov = oov_probe(text)
            except ParseTimeout:
                bucket = "parse-timeout"
                n_parses = 0
                n_fragments = 0
                diag_summary = f"timeout {ITEM_TIMEOUT_S}s"
                diag_kinds = Counter()
                oov = []
            except Exception as e:
                signal.alarm(0)
                bucket = "tokenizer-fail"
                n_parses = 0
                n_fragments = 0
                diag_summary = f"EXCEPTION: {type(e).__name__}: {e}"[:200]
                diag_kinds = Counter()
                oov = []
            latency = time.time() - t0
            latencies.append(latency)

            rec = ParseRecord(
                locator=ex["locator"],
                text=text,
                bucket=bucket,
                n_parses=n_parses,
                n_fragments=n_fragments,
                oov_tokens=oov,
                diag_summary=diag_summary,
                diag_kinds=dict(diag_kinds),
                latency_s=round(latency, 3),
            )
            out_fh.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")
            out_fh.flush()
            bucket_counts[bucket] += 1
            n += 1
            if latency > ITEM_TIMEOUT_S * 0.9:
                # Surface SLOW (>90% of timeout) items individually so
                # the monitor log shows which sentences need attention.
                _audit_log(f"  SLOW [{i}/{len(records)}] {latency:.1f}s "
                           f"{ex['locator']}: {text[:80]}")
            if n % 25 == 0:
                mn = min(latencies)
                mx = max(latencies)
                avg = sum(latencies) / len(latencies)
                elapsed = time.time() - wave_start
                rate = n / elapsed if elapsed else 0
                eta = (len(records) - n) / rate if rate else 0
                parsed = sum(
                    bucket_counts.get(b, 0)
                    for b in ("parse-success-N", "parse-success-1")
                )
                _audit_log(
                    f"  {n:4d}/{len(records)}  parsed={parsed}  "
                    f"min/avg/max latency = "
                    f"{mn:.2f}/{avg:.2f}/{mx:.2f}s  rate={rate:.1f}/s "
                    f" eta={eta:.0f}s"
                )

    wave_elapsed = time.time() - wave_start
    parsed = sum(
        bucket_counts.get(b, 0)
        for b in ("parse-success-N", "parse-success-1")
    )
    pct = parsed / n * 100 if n else 0
    _audit_log(
        f"=== {in_path.name} DONE: {parsed}/{n} ({pct:.2f}%)  "
        f"buckets={dict(bucket_counts)}  wall={wave_elapsed:.0f}s ==="
    )
    print(f"  → {out_path.relative_to(REPO_ROOT)} ({n} records)")
    for b, c in bucket_counts.most_common():
        print(f"      {b:30s} {c:4d}  ({c / n:5.1%})")
    return parsed, n, latencies


def cmd_report() -> None:
    parse_path = EXEMPLARS_DIR / "wave1-parse-results.jsonl"
    verbs_path = EXEMPLARS_DIR / "wave1-rb86-verbs.jsonl"
    # Output to gitignored exemplars dir; the version-controlled
    # roll-up lives in docs/coverage.md § "Phase 9 — Naturalistic-
    # tier audit closures" / Wave 1 pilot baseline.
    report_path = EXEMPLARS_DIR / "coverage-audit-wave1.md"

    if not parse_path.exists():
        print(f"ERROR: {parse_path} not found; run 'parse' first", file=sys.stderr)
        sys.exit(1)

    records = [json.loads(ln) for ln in parse_path.open(encoding="utf-8")]
    verbs = []
    if verbs_path.exists():
        verbs = [json.loads(ln) for ln in verbs_path.open(encoding="utf-8")]

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
    lines.append("<!-- markdownlint-disable MD013 -->")
    lines.append("")
    lines.append("| Locator | Text | Bucket | OOV tokens | Diagnostic |")
    lines.append("| --- | --- | --- | --- | --- |")
    for r in zero_parses[:30]:
        oov = ", ".join(r["oov_tokens"][:5]) or "—"
        diag = r["diag_summary"].replace("|", "\\|")[:80] or "—"
        text = r["text"].replace("|", "\\|")[:60]
        lines.append(f"| `{r['locator']}` | {text} | {r['bucket']} | {oov} | {diag} |")
    lines.append("")
    lines.append("<!-- markdownlint-enable MD013 -->")
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


_XWAVE_SOURCES = [
    ("Wave 1 — rg81 transcriptions", "wave1-parse-results.jsonl"),
    ("Wave 2 — RC 1990", "wave2-rc1990-parse-results.jsonl"),
    ("Wave 2 — Ramos 1971", "wave2-ramos1971-parse-results.jsonl"),
    ("Wave 2 — R&G Intermediate", "wave2-rg-intermediate-parse-results.jsonl"),
    ("Wave 3 — S&O 1972", "wave3-so1972-parse-results.jsonl"),
    ("Wave 3 — R&G Conversational", "wave3-rg-conversational-parse-results.jsonl"),
    ("Wave 4 — Kroeger 1991", "wave4-kroeger1991-parse-results.jsonl"),
]

# Harvest-noise OOV tokens (Phase 8/9 — not real OOV; surface from
# affix-only emissions, glossing-abbreviation tags, and English
# pedagogical prose).
_HARVEST_NOISE_OOV = frozenset({
    "nag", "mag", "of", "af", "the", "is", "or", "to", "i", "and",
    "example", "question", "sentence", "tag", "ov", "lf", "rv", "iv",
    "dv", "bv",
})


def _xwave_load_records() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for label, fname in _XWAVE_SOURCES:
        path = EXEMPLARS_DIR / fname
        if not path.exists():
            print(f"  (skip {fname}; not found — run 'parse' first)",
                  file=sys.stderr)
            out[label] = []
            continue
        out[label] = [
            json.loads(ln) for ln in path.open(encoding="utf-8") if ln.strip()
        ]
    return out


def _xwave_oov_yield_curve(
    by_wave: dict[str, list[dict]],
) -> list[tuple[int, int]]:
    """Cumulative OOV-clear yield as more tokens are registered."""
    failed_rows: list[list[str]] = []
    for recs in by_wave.values():
        for r in recs:
            if r.get("bucket", "").startswith("parse-success"):
                continue
            toks = [
                t.lower() for t in (r.get("oov_tokens") or [])
                if t.lower() not in _HARVEST_NOISE_OOV
            ]
            failed_rows.append(toks)
    freq: Counter[str] = Counter()
    for toks in failed_rows:
        for t in toks:
            freq[t] += 1
    ranked = [t for t, _c in freq.most_common(500)]

    def yield_at(n: int) -> int:
        closed = set(ranked[:n])
        return sum(1 for toks in failed_rows if not toks or all(t in closed for t in toks))

    return [(n, yield_at(n)) for n in (10, 30, 50, 75, 100, 150, 200, 300, 500)]


def _xwave_oov_frequency_tsv(
    by_wave: dict[str, list[dict]],
    out_path: Path,
    samples_per_token: int = 3,
) -> int:
    """Emit a TSV with: rank, token, count, sample-locator, sample-text."""
    freq: Counter[str] = Counter()
    samples: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for recs in by_wave.values():
        for r in recs:
            if r.get("bucket", "").startswith("parse-success"):
                continue
            for t in (r.get("oov_tokens") or []):
                key = t.lower()
                if key in _HARVEST_NOISE_OOV:
                    continue
                freq[key] += 1
                if len(samples[key]) < samples_per_token:
                    samples[key].append(
                        (r.get("locator", ""), r.get("text", ""))
                    )
    lines = ["rank\ttoken\tcount\tsample_locator\tsample_text"]
    for rank, (tok, count) in enumerate(freq.most_common(), 1):
        sample_locator, sample_text = (samples[tok][0] if samples[tok]
                                       else ("", ""))
        sample_text = sample_text.replace("\t", " ").replace("\n", " ")
        lines.append(
            f"{rank}\t{tok}\t{count}\t{sample_locator}\t{sample_text}"
        )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(freq)


def cmd_xwave_report() -> None:
    """Emit cross-wave audit summary at data/tgl/exemplars/coverage-audit-xwave.md (gitignored).

    Version-controlled roll-up lives in
    ``docs/coverage.md`` § "Phase 9 — Naturalistic-tier audit closures"
    (Cross-wave snapshot detail subsection).
    """
    by_wave = _xwave_load_records()
    total = sum(len(v) for v in by_wave.values())
    if total == 0:
        print("ERROR: no parse-results files found; run 'parse' first",
              file=sys.stderr)
        sys.exit(1)

    # Per-wave parse stats
    rows: list[tuple[str, int, int, float, Counter]] = []
    cumulative_buckets: Counter[str] = Counter()
    for label, recs in by_wave.items():
        b: Counter[str] = Counter(r.get("bucket", "?") for r in recs)
        n = len(recs)
        clean = sum(v for k, v in b.items() if k.startswith("parse-success"))
        rate = (100.0 * clean / n) if n else 0.0
        rows.append((label, clean, n, rate, b))
        cumulative_buckets.update(b)

    total_clean = sum(c for _l, c, _n, _r, _b in rows)

    # OOV-multiplicity distribution + yield curve
    oov_hist: Counter[int] = Counter()
    no_oov_failures = 0
    pure_noise_oov = 0
    for recs in by_wave.values():
        for r in recs:
            if r.get("bucket", "").startswith("parse-success"):
                continue
            toks = r.get("oov_tokens") or []
            real = [t for t in toks if t.lower() not in _HARVEST_NOISE_OOV]
            oov_hist[len(real)] += 1
            if not real:
                no_oov_failures += 1
                if toks:
                    pure_noise_oov += 1
    yield_curve = _xwave_oov_yield_curve(by_wave)

    # Sentence-length histogram
    def _len_bucket(n: int) -> str:
        if n <= 3:
            return "1-3"
        if n <= 5:
            return "4-5"
        if n <= 8:
            return "6-8"
        if n <= 12:
            return "9-12"
        if n <= 20:
            return "13-20"
        return "21+"

    len_passed: Counter[str] = Counter()
    len_failed: Counter[str] = Counter()
    for recs in by_wave.values():
        for r in recs:
            n = len(str(r.get("text", "")).split())
            b = _len_bucket(n)
            if r.get("bucket", "").startswith("parse-success"):
                len_passed[b] += 1
            else:
                len_failed[b] += 1

    # No-OOV failure equation frequency
    no_oov_eqn: Counter[str] = Counter()
    no_oov_kind: Counter[str] = Counter()
    for recs in by_wave.values():
        for r in recs:
            if r.get("bucket", "").startswith("parse-success"):
                continue
            toks = [t.lower() for t in (r.get("oov_tokens") or [])
                    if t.lower() not in _HARVEST_NOISE_OOV]
            if toks:
                continue
            ds = r.get("diag_summary", "") or ""
            m = re.search(r"equation=['\"]([^'\"]+)['\"]", ds)
            if m:
                no_oov_eqn[m.group(1)] += 1
            m = re.search(r"kind=['\"](\w[\w-]*)['\"]", ds)
            if m:
                no_oov_kind[m.group(1)] += 1

    # Top OOV tokens (real-OOV only)
    top_oov: Counter[str] = Counter()
    diag_kinds_all: Counter[str] = Counter()
    for recs in by_wave.values():
        for r in recs:
            if r.get("bucket", "").startswith("parse-success"):
                continue
            for t in r.get("oov_tokens") or []:
                if t.lower() in _HARVEST_NOISE_OOV:
                    continue
                top_oov[t.lower()] += 1
            for k, v in (r.get("diag_kinds") or {}).items():
                diag_kinds_all[k] += v

    # Emit TSV artifact
    tsv_path = EXEMPLARS_DIR / "oov-frequency.tsv"
    tsv_n = _xwave_oov_frequency_tsv(by_wave, tsv_path)
    print(f"  → {tsv_path.relative_to(REPO_ROOT)} ({tsv_n} unique tokens)")

    # Build the markdown doc
    out: list[str] = []
    out.append("# Coverage audit — cross-wave snapshot")
    out.append("")
    out.append("> **Status:** Cross-wave audit snapshot generated by")
    out.append("> `scripts/harvest_exemplars.py xwave-report`. Rolling")
    out.append("> baseline for Phase 9's ≥80% target — regenerated after")
    out.append("> each sub-PR closes (re-run `cmd_parse` then")
    out.append("> `xwave-report`).")
    out.append("")
    out.append("## Per-wave parse rate")
    out.append("")
    out.append("| Wave | Clean | Total | Rate |")
    out.append("| --- | ---: | ---: | ---: |")
    for label, clean, n, rate, _b in rows:
        out.append(f"| {label} | {clean} | {n} | {rate:.1f}% |")
    out.append(f"| **Cumulative** | **{total_clean}** | **{total}** | "
               f"**{100.0 * total_clean / total:.2f}%** |")
    out.append("")
    out.append("## Cumulative bucket distribution")
    out.append("")
    out.append("| Bucket | Count | Share |")
    out.append("| --- | ---: | ---: |")
    for b, c in sorted(cumulative_buckets.items(), key=lambda kv: -kv[1]):
        out.append(f"| {b} | {c} | {100.0 * c / total:.1f}% |")
    out.append("")
    out.append("## OOV-multiplicity (failed rows by number of real OOVs)")
    out.append("")
    out.append("Real OOV = surface OOV minus harvest-noise tokens")
    out.append(f"({len(_HARVEST_NOISE_OOV)} known noise tokens — `nag`,")
    out.append("`mag`, `af`, `of`, English/glossing fragments, etc.).")
    out.append("")
    out.append("| Real OOVs | Failed rows | Cumulative |")
    out.append("| --- | ---: | ---: |")
    cumsum = 0
    for k in sorted(oov_hist.keys()):
        cumsum += oov_hist[k]
        out.append(f"| {k} | {oov_hist[k]} | {cumsum} |")
    out.append("")
    out.append(f"- **No-real-OOV failures:** {no_oov_failures} rows "
               f"(pure grammar/feat blockers)")
    out.append(f"- **Pure-noise OOV** "
               "(OOV is 100% harvest noise; extractor cleanup would "
               f"unblock): {pure_noise_oov} rows")
    out.append("")
    out.append("## OOV-yield curve")
    out.append("")
    out.append("If the top-N tokens were registered, how many failed "
               "rows become OOV-clear?")
    out.append("")
    out.append("| Top-N tokens | OOV-clear rows | % of all rows |")
    out.append("| ---: | ---: | ---: |")
    for n, y in yield_curve:
        out.append(f"| {n} | {y} | {100.0 * y / total:.1f}% |")
    out.append("")
    out.append("> OOV-clear ≠ parses cleanly — conservative estimate is")
    out.append("> ~60-75% of OOV-clear rows actually parse; the rest hit")
    out.append("> grammar/feat gaps after lex resolves.")
    out.append("")
    out.append("## Sentence-length distribution")
    out.append("")
    out.append("| Length (words) | Passed | Failed | %-fail |")
    out.append("| --- | ---: | ---: | ---: |")
    for k in ("1-3", "4-5", "6-8", "9-12", "13-20", "21+"):
        p = len_passed.get(k, 0)
        f = len_failed.get(k, 0)
        tot = p + f
        fpct = (100.0 * f / tot) if tot else 0.0
        out.append(f"| {k} | {p} | {f} | {fpct:.1f}% |")
    out.append("")
    out.append("## Diagnostic-kind distribution (zero-parse rows)")
    out.append("")
    out.append("Multi-attempt counts — each parse attempt that fails "
               "with a given kind adds 1.")
    out.append("")
    out.append("| Kind | Count |")
    out.append("| --- | ---: |")
    for k, c in sorted(diag_kinds_all.items(), key=lambda kv: -kv[1]):
        out.append(f"| {k} | {c} |")
    out.append("")
    out.append("## No-OOV failure analysis "
               f"({no_oov_failures} rows)")
    out.append("")
    out.append("These are the highest-signal targets for "
               "construction-class sub-PRs — lex is sufficient but "
               "grammar/feat blocks the parse.")
    out.append("")
    out.append("### First-diag kind frequency")
    out.append("")
    out.append("| Kind | Count |")
    out.append("| --- | ---: |")
    for k, c in sorted(no_oov_kind.items(), key=lambda kv: -kv[1]):
        out.append(f"| {k} | {c} |")
    out.append("")
    out.append("### Top failing equations (top 20)")
    out.append("")
    out.append("| Equation | Count |")
    out.append("| --- | ---: |")
    for eqn, c in no_oov_eqn.most_common(20):
        safe = eqn.replace("|", "\\|").strip()
        if not safe:
            safe = "(empty)"
        out.append(f"| `{safe}` | {c} |")
    out.append("")
    out.append("## Top OOV tokens (real-OOV, top 50)")
    out.append("")
    out.append("Full ranking in `data/tgl/exemplars/oov-frequency.tsv`. "
               "Sample sentence locators included there for each token.")
    out.append("")
    out.append("| Rank | Token | Count |")
    out.append("| ---: | --- | ---: |")
    for rank, (tok, c) in enumerate(top_oov.most_common(50), 1):
        out.append(f"| {rank} | `{tok}` | {c} |")
    out.append("")
    out.append("## References")
    out.append("")
    out.append("- Phase 9 plan-of-record: "
               "`.claude/plans/tgllfg-phase-9.md` (Phase 9 strategy "
               "and sub-PR ledger).")
    out.append("- Phase 8 cumulative summary: "
               "`docs/analysis-choices.md` § \"Phase 8 cumulative "
               "summary\" (closing context).")
    out.append("- Version-controlled roll-up: "
               "`docs/coverage.md` § \"Phase 9 — Naturalistic-tier "
               "audit closures\".")
    out.append("")

    out_path = EXEMPLARS_DIR / "coverage-audit-xwave.md"
    out_path.write_text("\n".join(out), encoding="utf-8")
    print(f"  → {out_path.relative_to(REPO_ROOT)}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "stage",
        choices=["extract", "parse", "report", "xwave-report", "all"],
    )
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
    if args.stage in ("xwave-report", "all"):
        print("[xwave-report]")
        cmd_xwave_report()
    return 0


if __name__ == "__main__":
    sys.exit(main())
