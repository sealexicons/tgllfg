# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.C.3 Commit 3 — productive ``tig_distrib`` paradigm.

Migrates the Phase 5f Commit 19 hand-coded ``tig*`` particles
(``tigisa`` / ``tigdalawa`` / ... / ``tigsampu``) to a productive
paradigm via:

* New NUM-pos roots in ``data/tgl/numerals.yaml`` (10 cardinal
  numerals 1-10) with ``affix_class: [tig_distrib]`` and per-root
  ``CARDINAL_VALUE``.
* New ``tig_distrib`` paradigm cell in ``data/tgl/paradigms.yaml``
  (``base_pos: NUM``, single ``prefix tig`` op, cell.feats:
  ``{DISTRIB: YES, CARDINAL: YES, NUM: PL}``).
* Extended ``_index_paradigm_via_base_pos`` (analyzer.py) to
  handle NUM-pos roots by indexing derived surfaces into the
  ``particles`` table.
* Removed the 10 hand-coded ``tig*`` particles from
  ``data/tgl/particles.yaml``.

Closes the second piece of §18 L31 (productive paradigm classes).
"""

import pytest

from tgllfg.core.common import Token
from tgllfg.morph.analyzer import Analyzer


# === Productive cell fires on every cardinal 1-10 ========================


@pytest.mark.parametrize("surface,value", [
    ("tigisa",    "1"),
    ("tigdalawa", "2"),
    ("tigtatlo",  "3"),
    ("tigapat",   "4"),
    ("tiglima",   "5"),
    ("tiganim",   "6"),
    ("tigpito",   "7"),
    ("tigwalo",   "8"),
    ("tigsiyam",  "9"),
    ("tigsampu",  "10"),
])
def test_tig_distrib_productive(surface: str, value: str) -> None:
    """Each ``tigN`` form analyses as a NUM with DISTRIB=YES,
    CARDINAL=YES, CARDINAL_VALUE=N. Lemma points to the base
    numeral (``isa`` / ``dalawa`` / ... ) — the productive
    derivation makes the lemma the canonical root, not the
    surface (Commit 1 convention)."""
    a = Analyzer.from_default()
    token = Token(surface=surface, norm=surface, start=0, end=len(surface))
    results = a.analyze_one(token)
    num_results = [r for r in results if r.pos == "NUM"]
    distrib = [r for r in num_results if r.feats.get("DISTRIB") is True]
    assert len(distrib) >= 1, (
        f"expected ≥1 DISTRIB=YES NUM analysis for {surface!r}"
    )
    r = distrib[0]
    assert r.feats.get("CARDINAL") is True
    assert r.feats.get("CARDINAL_VALUE") == value
    assert r.feats.get("NUM") == "PL"


# === Bare cardinals unchanged ============================================


@pytest.mark.parametrize("surface,value,num", [
    ("isa",    "1",  "SG"),
    ("dalawa", "2",  "PL"),
    ("sampu",  "10", "PL"),
])
def test_bare_cardinals_unchanged(
    surface: str, value: str, num: str
) -> None:
    """Bare cardinals come from particles.yaml (unchanged). The
    productive ``tig_distrib`` paradigm does NOT shadow them
    because NUM Roots are paradigm-only inputs."""
    a = Analyzer.from_default()
    token = Token(surface=surface, norm=surface, start=0, end=len(surface))
    results = a.analyze_one(token)
    num_results = [r for r in results
                   if r.pos == "NUM"
                   and r.feats.get("CARDINAL") is True
                   and r.feats.get("DISTRIB") is not True]
    assert len(num_results) >= 1
    r = num_results[0]
    assert r.feats.get("CARDINAL_VALUE") == value
    assert r.feats.get("NUM") == num


# === Hand-coded tig* entries removed =====================================


def test_old_hand_coded_tig_entries_removed() -> None:
    """The 10 hand-coded ``tig*`` particles (Phase 5f Commit 19)
    are removed from particles.yaml — verified by checking that
    no particle with those surfaces exists at the loaded-data
    level. Productive analyses come only from the paradigm cell
    + NUM Root path."""
    a = Analyzer.from_default()
    tig_surfaces = {f"tig{base}" for base in (
        "isa", "dalawa", "tatlo", "apat", "lima",
        "anim", "pito", "walo", "siyam", "sampu",
    )}
    for p in a._data.particles:
        assert p.surface not in tig_surfaces, (
            f"unexpected hand-coded tig- particle: {p.surface!r}; "
            f"these should be removed and produced productively"
        )


# === NUM Root non-bare-indexing ==========================================


def test_num_root_does_not_shadow_bare_numeral() -> None:
    """The new NUM Roots in numerals.yaml are paradigm inputs
    only — they must NOT add a duplicate bare-NUM analysis. The
    bare ``isa`` analysis count comes solely from particles.yaml."""
    a = Analyzer.from_default()
    token = Token(surface="isa", norm="isa", start=0, end=3)
    results = a.analyze_one(token)
    # Each result is one analysis; bare ``isa`` should have exactly
    # the particle analysis (CARDINAL=YES + CARDINAL_VALUE=1) — no
    # duplicate from a NUM-Root-as-bare path.
    cardinal_nums = [r for r in results
                     if r.pos == "NUM"
                     and r.feats.get("CARDINAL") is True
                     and r.feats.get("CARDINAL_VALUE") == "1"]
    assert len(cardinal_nums) == 1, (
        f"expected exactly 1 bare-NUM analysis for 'isa'; got "
        f"{len(cardinal_nums)}: {cardinal_nums}"
    )
