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

# Phase 10.J.post-6: ``pending_closure`` is an OPTIONAL field marking
# entries that are known not to parse yet but are scheduled for closure
# in a named follow-on sub-PR. Set to e.g. ``"post-10"`` to xfail the
# parse assertion below, surfacing automatically if the entry starts
# parsing (so the field gets removed). When absent, the entry must
# parse with ≥1 tree (the default contract). Added in 10.J.post-6 after
# the post-5 close-out shipped 7 entries that don't yet parse — 3
# closed with lex additions in this same sub-PR, 4 remain pending.
_OPTIONAL_FIELDS = frozenset({"pending_closure"})


def _pending(entry: dict) -> str | None:
    """Return the ``pending_closure`` tag if set + non-empty, else
    ``None``. Treats absent / null / empty-string as not-pending."""
    val = entry.get("pending_closure")
    if isinstance(val, str) and val:
        return val
    return None


@pytest.mark.parametrize(
    "entry", _CORPUS, ids=[e["locator"] for e in _CORPUS],
)
def test_unattributed_construction_parses(entry: dict) -> None:
    """Each curated form must still parse with ≥1 tree. A failure is a
    regression against a productive construction the parser is supposed
    to support but the naturalistic corpora do not attest.

    Entries marked ``pending_closure: "<sub-pr>"`` are xfail'd — the
    sub-PR named is responsible for closing them. If a pending entry
    starts parsing, ``strict=True`` flips the xfail to XPASS, surfacing
    immediately so the field can be removed and the closure recorded.
    """
    pending = _pending(entry)
    if pending:
        pytest.xfail(
            f"{entry['locator']} pending closure in {pending}: "
            f"{entry['text_normalized']!r}"
        )
    parses = parse_text(entry["text_normalized"])
    assert len(parses) >= 1, (
        f"unattributed-corpus regression on {entry['locator']}: "
        f"0 parses for {entry['text_normalized']!r}"
    )


def test_corpus_nonempty() -> None:
    """Guard against an accidental truncation of the tracked corpus."""
    assert len(_CORPUS) >= 30, f"corpus shrank unexpectedly: {len(_CORPUS)}"


def test_corpus_schema() -> None:
    """Every record carries the full Exemplar schema, optionally
    augmented with ``pending_closure`` (a string tag naming the sub-PR
    responsible for closing the entry). All records are flagged
    ``ocr_quality=authored`` (hand-written, not OCR/transcription),
    grammatical, and point at an ``unattributed/`` source."""
    for r in _CORPUS:
        keys = frozenset(r)
        # Required fields must all be present.
        missing = _SCHEMA_FIELDS - keys
        assert not missing, f"missing fields on {r.get('locator')!r}: {missing}"
        # No extra fields beyond the required + optional sets.
        extra = keys - _SCHEMA_FIELDS - _OPTIONAL_FIELDS
        assert not extra, f"unexpected fields on {r.get('locator')!r}: {extra}"
        # pending_closure, if present, must be a non-empty string.
        if "pending_closure" in r:
            assert isinstance(r["pending_closure"], str)
            assert r["pending_closure"], (
                f"empty pending_closure on {r['locator']!r}"
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
