# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.E.5 — unattributed-construction corpus regression test.

Reads the hand-authored unattributed-construction corpus
(``data/tgl/exemplars/unattributed-constructions.jsonl``) and asserts
every entry still parses. The exemplars directory is gitignored
(licensed-PDF derivatives), so the corpus is exposed through a
``.gitignore`` override (``!data/tgl/exemplars/unattributed*.*``)
precisely so this test reads it on a fresh clone.

Purpose: a persistent regression home for productive R-bucket
(reduplication) forms the naturalistic audit corpora do not attest —
the bare/inflected casual + iterative V-stem redups (10.E.3 / 10.E.4),
time-noun frequency adverbs (10.A), distributive numerals (10.C), and
scalar-adjective degree redups (10.E.1). Per-sub-PR test files
(``test_phase10_*``) churn and get refactored away; this corpus + test
persist, mirroring the Phase 9.Z naturalistic-audit regression fixture.
The corpus is REPORTED SEPARATELY from the naturalistic ≥80% metric
(``harvest_exemplars.py unattributed-report``, kept out of
``_XWAVE_SOURCES``).
"""

import json
from pathlib import Path

import pytest

from tgllfg.core.pipeline import parse_text

_CORPUS_PATH = (
    Path(__file__).resolve().parents[2]
    / "data" / "tgl" / "exemplars" / "unattributed-constructions.jsonl"
)
_CORPUS = [
    json.loads(ln)
    for ln in _CORPUS_PATH.read_text(encoding="utf-8").splitlines()
    if ln.strip()
]

# Every clause-parseable R-bucket construction class (locator prefix).
# 10.B place-distributive is morphology-only (no AdvP[LOCATION] attach
# rule), so it is deliberately absent — covered by its own morph test.
_EXPECTED_CLASSES = frozenset({
    "casual-bare", "iter-bare", "casual-infl", "iter-infl",
    "freq-adv", "distr-num", "atten-adj",
})
_SCHEMA_FIELDS = frozenset({
    "source", "locator", "text_raw", "text_normalized",
    "has_gloss", "gloss_en", "marked_ungrammatical", "ocr_quality",
})


@pytest.mark.parametrize(
    "entry", _CORPUS, ids=[e["locator"] for e in _CORPUS],
)
def test_unattributed_construction_parses(entry: dict) -> None:
    """Each curated form must still parse with ≥1 tree. A failure is a
    regression against a productive construction the parser is supposed
    to support but the naturalistic corpora do not attest."""
    parses = parse_text(entry["text_normalized"])
    assert len(parses) >= 1, (
        f"unattributed-corpus regression on {entry['locator']}: "
        f"0 parses for {entry['text_normalized']!r}"
    )


def test_corpus_nonempty() -> None:
    """Guard against an accidental truncation of the tracked corpus."""
    assert len(_CORPUS) >= 30, f"corpus shrank unexpectedly: {len(_CORPUS)}"


def test_corpus_schema() -> None:
    """Every record carries the full Exemplar schema, is flagged
    ``ocr_quality=authored`` (hand-written, not OCR/transcription), is
    grammatical, and points at an ``unattributed/`` source."""
    for r in _CORPUS:
        assert frozenset(r) == _SCHEMA_FIELDS, (
            f"bad schema on {r.get('locator')!r}: "
            f"{frozenset(r) ^ _SCHEMA_FIELDS}"
        )
        assert r["ocr_quality"] == "authored"
        assert r["marked_ungrammatical"] is False
        assert r["text_raw"] == r["text_normalized"]
        assert r["source"].startswith("unattributed/")


def test_corpus_locators_unique() -> None:
    locs = [r["locator"] for r in _CORPUS]
    assert len(locs) == len(set(locs)), "duplicate locator in corpus"


def test_corpus_covers_redup_classes() -> None:
    """The corpus spans every clause-parseable R-bucket construction
    class. If a class drops out, a productive construction has lost its
    persistent regression home."""
    present = {r["locator"].split("/")[0] for r in _CORPUS}
    missing = _EXPECTED_CLASSES - present
    assert not missing, f"corpus missing construction classes: {missing}"
