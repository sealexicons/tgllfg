# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 9.X.post-1: stopwords-iso/stopwords-tl coverage test.

Asserts that every form in the vendored stopwords-iso/stopwords-tl
list (``tests/tgllfg/data/stopwords_iso_tl.txt``, 147 forms; MIT-
licensed, sourced from https://github.com/stopwords-iso/stopwords-tl)
is recognised by the pipeline-level lex / morphology stack.

Recognition is checked at the same level the parser operates: the
form is tokenised, then run through the post-tokenisation
normalisation passes (``split_apostrophe_t`` / ``split_apostrophe_y``
/ ``split_enclitics`` / ``split_linker_ng``), and every resulting
sub-token is required to be ``is_known_surface``. This matches what
the parser sees — a form like ``walang`` legitimately splits into
``wala`` + ``-ng`` and is "recognised" as long as both halves are.

EXCLUDED FORMS — both documented in ``EXCLUDED`` below:

* ``am`` — English contamination in the upstream source list (likely
  from corpus mixing); not a Tagalog stopword by any reference.
* ``napaka`` — the intensifier prefix ``napaka-`` attaches productively
  to ADJ roots (adj_paradigms.yaml line ~90); standalone bare-prefix
  usage lacks audit-corpus evidence as of 9.X.post-1. Re-evaluate if
  attested.

If a future lex change regresses coverage of any non-excluded form,
this test fails with the per-form sub-token breakdown so the
regression is immediately localised.
"""

from pathlib import Path

import pytest

from tgllfg.morph.analyzer import _get_default
from tgllfg.text import (
    split_apostrophe_t,
    split_apostrophe_y,
    split_enclitics,
    split_linker_ng,
    tokenize,
)


STOPWORDS_PATH = Path(__file__).parent / "data" / "stopwords_iso_tl.txt"

# Forms intentionally not asserted (see module docstring).
EXCLUDED: frozenset[str] = frozenset({"am", "napaka"})


def _load_stopwords() -> list[str]:
    return [
        line.strip()
        for line in STOPWORDS_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _pipeline_splits(form: str):
    """Mirror ``core/pipeline.py`` up through the analyzer-recognition
    boundary — every step before lex lookup that the parser applies."""
    toks = tokenize(form)
    toks = split_apostrophe_t(toks)
    toks = split_apostrophe_y(toks)
    toks = split_enclitics(toks)
    toks = split_linker_ng(toks)
    return toks


def test_stopwords_iso_tl_coverage() -> None:
    """Every non-excluded stopword's post-tokenisation sub-tokens are
    all ``is_known_surface``. Regressions surface with the full sub-
    token breakdown for the failing form so the gap is immediately
    actionable."""
    analyzer = _get_default()
    forms = _load_stopwords()
    assert len(forms) == 147, (
        f"vendored stopword list length drifted: expected 147, got "
        f"{len(forms)} — re-check tests/tgllfg/data/stopwords_iso_tl.txt"
    )

    failures: list[str] = []
    for form in forms:
        if form in EXCLUDED:
            continue
        toks = _pipeline_splits(form)
        sub = [(t.norm, analyzer.is_known_surface(t.norm)) for t in toks]
        if not all(known for _, known in sub):
            joined = " | ".join(
                f"{n}{'*' if not known else ''}" for n, known in sub
            )
            failures.append(f"{form!r}: {joined}")

    if failures:
        msg = "\n  ".join(
            ["stopword coverage regression — unrecognized sub-tokens (*):", *failures]
        )
        pytest.fail(msg)


def test_excluded_forms_documented() -> None:
    """Each form in EXCLUDED really is in the vendored list — guards
    against drift where an exclusion stops being meaningful (e.g., the
    upstream list removes it, or the exclusion typo'd a form that
    never existed)."""
    forms = set(_load_stopwords())
    missing = sorted(EXCLUDED - forms)
    assert not missing, (
        f"EXCLUDED entries no longer present in source list: {missing}"
    )
