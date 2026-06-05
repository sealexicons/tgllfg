# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.C.3 Commit 5 — productive ``kani_redup`` paradigm.

Migrates the Phase 5f Commit 21 hand-coded distributive-possessive
Q particles (``kanikaniya`` / ``kanyakanya``) to a productive
paradigm via:

* New ``kani_redup`` op
  (``src/tgllfg/morph/sandhi.py``
  ``kani_reduplicate``): 2-syllable bases get full redup;
  3-syllable bases get first-copy truncated to 2 syllables then
  concatenated with the full base.
* New ``kani_redup`` paradigm cell in
  ``data/tgl/paradigms.yaml`` with ``base_pos: PRON``, ``pos: Q``
  (POS-flip: PRON → Q), and ``feats: {QUANT: EACH_OWN,
  DISTRIB_POSS: YES}``.
* New ``pos`` field on :class:`ParadigmCell` (optional pos
  override for the derived MorphAnalysis).
* New ``affix_class`` field on :class:`Pronoun` (defaults to
  empty list).
* Extended ``_build_index`` + new ``_index_pronoun_paradigms``
  method dispatching pronouns with non-empty affix_class through
  paradigm cells with ``base_pos: PRON``.
* New 3sg DAT orthographic variant ``kaniya`` in
  ``data/tgl/pronouns.yaml`` (with ``LEMMA: kanya`` canonical
  routing) — needed as the paradigm input for the ``kanikaniya``
  productive form.
* ``affix_class: [kani_redup]`` added to the 3rd-person DAT
  pronouns ``kanya`` / ``kaniya`` / ``kanila``.
* Removed the hand-coded ``kanikaniya`` / ``kanyakanya``
  particles from ``data/tgl/particles.yaml`` — the productive
  paradigm now provides them.

Anti-deferral closure beyond the plan §5.2 description: the
productive paradigm fires for **3pl** ``kanila`` → ``kanikanila``
(attested in R&G 1981 corpus excerpts but not hand-coded by
Phase 5f Commit 21). Closes the third piece of §18 L31.
"""

import pytest

from tgllfg.core.common import Token
from tgllfg.morph.analyzer import Analyzer
from tgllfg.morph.sandhi import kani_reduplicate


# === Sandhi op ===========================================================


def test_kani_reduplicate_two_syllable() -> None:
    """2-syllable bases get full redup."""
    assert kani_reduplicate("kanya") == "kanyakanya"
    assert kani_reduplicate("akin") == "akinakin"


def test_kani_reduplicate_three_syllable() -> None:
    """3-syllable bases: first copy truncated to 2 syllables."""
    assert kani_reduplicate("kaniya") == "kanikaniya"
    assert kani_reduplicate("kanila") == "kanikanila"


# === Productive cell fires on each 3rd-person DAT pronoun ================


@pytest.mark.parametrize("surface,source_lemma", [
    ("kanyakanya",  "kanya"),
    ("kanikaniya",  "kanya"),   # via kaniya variant; canonical lemma kanya
    ("kanikanila",  "kanila"),
])
def test_kani_redup_productive(surface: str, source_lemma: str) -> None:
    """Each derived ``kani*`` form analyses as Q with
    QUANT=EACH_OWN + DISTRIB_POSS=YES; lemma points to the
    canonical PRON."""
    a = Analyzer.from_default()
    token = Token(surface=surface, norm=surface, start=0, end=len(surface))
    results = a.analyze_one(token)
    q_results = [r for r in results
                 if r.pos == "Q"
                 and r.feats.get("DISTRIB_POSS") is True]
    assert len(q_results) >= 1, (
        f"expected ≥1 Q DISTRIB_POSS analysis for {surface!r}"
    )
    r = q_results[0]
    assert r.feats.get("QUANT") == "EACH_OWN"
    assert r.lemma == source_lemma


# === Bare DAT pronouns unchanged ========================================


@pytest.mark.parametrize("surface,lemma", [
    ("kanya",  "kanya"),
    ("kaniya", "kanya"),  # orthographic variant; canonicalised
    ("kanila", "kanila"),
])
def test_bare_dat_prons_unchanged(surface: str, lemma: str) -> None:
    """Bare DAT pronouns continue to analyze as PRON. The new
    ``affix_class`` field on Pronoun doesn't shadow bare lookup."""
    a = Analyzer.from_default()
    token = Token(surface=surface, norm=surface, start=0, end=len(surface))
    results = a.analyze_one(token)
    pron_results = [r for r in results if r.pos == "PRON"]
    assert len(pron_results) >= 1
    assert pron_results[0].lemma == lemma
    assert pron_results[0].feats.get("CASE") == "DAT"


# === Hand-coded kani- particles removed =================================


def test_old_hand_coded_kani_particles_removed() -> None:
    """The 2 hand-coded ``kanikaniya`` / ``kanyakanya`` Q particles
    (Phase 5f Commit 21) are removed from particles.yaml — verified
    by checking that no Particle with those surfaces exists."""
    a = Analyzer.from_default()
    kani_surfaces = {"kanikaniya", "kanyakanya"}
    for p in a._data.particles:
        assert p.surface not in kani_surfaces, (
            f"unexpected hand-coded kani- particle: {p.surface!r}; "
            f"these should be removed and produced productively"
        )


# === 3pl form newly added ================================================


def test_3pl_kanikanila_newly_productive() -> None:
    """``kanikanila`` (3pl distributive-possessive) is now
    productively generated — it was NOT in the Phase 5f Commit 21
    hand-coded set. Closes the 3pl gap in the corpus excerpt
    ``sa kani-kanilang probinsiya`` (R&G 1981)."""
    a = Analyzer.from_default()
    token = Token(surface="kanikanila", norm="kanikanila", start=0, end=10)
    results = a.analyze_one(token)
    q_distrib = [r for r in results
                 if r.pos == "Q"
                 and r.feats.get("DISTRIB_POSS") is True]
    assert len(q_distrib) == 1
    r = q_distrib[0]
    assert r.feats.get("NUM") == "PL"
    assert r.feats.get("PERS") == 3
    assert r.lemma == "kanila"
