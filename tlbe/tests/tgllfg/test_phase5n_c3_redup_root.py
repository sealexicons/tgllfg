# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.C.3 Commit 6 — ``redup_root`` op.

Adds the post-prefix root-reduplication op to the paradigm-engine
operation DSL. The op appends ``root.citation`` to the current
base, producing surfaces where the prefix is on the first copy
only:

* ``ganda`` + ``[prefix ma, redup_root]`` → ``magandaganda``
  (L37 reduplicated-intensive ``maganda-ganda``; canonical
  orthography with hyphen merges to the single-token form via
  the hyphen-merge tokenizer pre-pass).
* ``liit`` + ``[prefix ma, redup_root]`` → ``maliitliit``
  (L37 ``maliit-liit``).
* ``dali`` + ``[cv_redup, prefix kasing]`` → ``kasingdadali``
  (L38 ``kasing-`` redup; uses ``cv_redup`` + ``prefix`` — no
  ``redup_root`` needed because the redup is CV not full-root).
* ``ano`` + ``[cv_redup]`` → ``aano`` and similar wh-redup
  patterns are L49's domain — also handled via ``cv_redup``,
  not ``redup_root``.

The op REQUIRES root_citation context. ``generate_form`` passes
it automatically; standalone ``_apply`` callers must pass it
explicitly. Distinct from ``full_redup`` (Commit 2): that op
duplicates the whole current base (and applies o→u raising on
the first copy), whereas ``redup_root`` appends just the
original root with no sandhi.

Infrastructure-only — Commit 7 (L37 intensives) is the first
consumer.
"""

from tgllfg.morph.analyzer import _apply
from tgllfg.morph.paradigms import Operation


# === Op-level unit tests =================================================


def test_redup_root_appends_citation() -> None:
    """``maganda`` (current base) + redup_root with root=ganda
    → ``magandaganda``."""
    op = Operation(op="redup_root")
    assert _apply(op, "maganda", set(), "ganda") == "magandaganda"


def test_redup_root_with_short_root() -> None:
    """``maliit`` (after ma- prefix on ``liit``) + redup_root →
    ``maliitliit``."""
    op = Operation(op="redup_root")
    assert _apply(op, "maliit", set(), "liit") == "maliitliit"


def test_redup_root_on_three_syl_root() -> None:
    """``mabuhay`` (after ma- on ``buhay``) + redup_root →
    ``mabuhaybuhay``."""
    op = Operation(op="redup_root")
    assert _apply(op, "mabuhay", set(), "buhay") == "mabuhaybuhay"


def test_redup_root_no_root_raises() -> None:
    """The op requires root_citation context — calling without
    raises ValueError. Defensive belt-and-braces."""
    import pytest
    op = Operation(op="redup_root")
    with pytest.raises(ValueError, match="redup_root op requires"):
        _apply(op, "maganda", set(), "")


def test_redup_root_no_sandhi() -> None:
    """Distinct from ``full_redup``: no o→u raising. ``mabolong``
    (hypothetical) + redup_root with root=bolong → ``mabolongbolong``
    (not ``mabolongbulong``)."""
    op = Operation(op="redup_root")
    assert _apply(op, "mabolong", set(), "bolong") == "mabolongbolong"
