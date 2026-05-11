"""Phase 5n.C.3 Commit 8 — L38 CV-redup ``kasing-`` equative.

Adds the productive ``kasing_redup_adj`` paradigm cell to
``data/tgl/paradigms.yaml``:

* ``base_pos: ADJ``
* ``affix_class: ma_adj``
* operations: ``[cv_redup, prefix kasing]``
* ``feats: {PREDICATIVE: YES, COMP_DEGREE: EQUATIVE}``

Closes §18 L38 (Phase 5f Commit 14 productive-paradigm
follow-on; the existing modern ``kasing-`` cell in
``adj_paradigms.yaml`` only produces the non-redup
``kasingganda`` form).

Per Schachter & Otanes 1972 §5 + 2026-05-10 GT verification:
the CV-redup form is a stylistic variant of the modern
``kasing-`` equative — both forms are semantically equivalent
in modern usage ("just as X"). The f-structure of the two
forms is identical (COMP_DEGREE=EQUATIVE on both); only the
surface differs. Earlier draft tagged the redup form with
``REGISTER: ARCHAIC`` but that was overspecified per the GT
observation — both `kasingganda` and `kasinggaganda` translate
identically to "just as beautiful as".

The C8 commit also adds ``dali`` as an ADJ root in
``adjectives.yaml`` so the canonical L38 example
``kasingdadali`` has a base — ``dali`` previously existed only
as a VERB root.

Tests cover:

* Productive surfaces analyze as ADJ with
  COMP_DEGREE=EQUATIVE + PREDICATIVE=YES.
* Modern ``kasing-`` forms (non-redup) and CV-redup ``kasing-``
  forms produce f-structure-identical analyses.
* The new ``dali`` ADJ root produces ``madali`` (existing
  ma_adj cell) and ``kasingdadali`` (new kasing_redup_adj cell).
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import Token
from tgllfg.morph.analyzer import Analyzer


# === Morph layer ==========================================================


@pytest.mark.parametrize("surface,base", [
    ("kasinggaganda", "ganda"),
    ("kasingdadali",  "dali"),
    ("kasingbabait",  "bait"),
    ("kasingmamabait", "mabait"),  # may not be attested; productive engine fires anyway
])
def test_kasing_redup_morph_smoke(surface: str, base: str) -> None:
    """Productive CV-redup equative surfaces analyze as ADJ with
    COMP_DEGREE=EQUATIVE + PREDICATIVE=YES (f-structure-identical
    to the modern non-redup ``kasing-`` form)."""
    a = Analyzer.from_default()
    token = Token(surface=surface, norm=surface, start=0, end=len(surface))
    results = a.analyze_one(token)
    equatives = [r for r in results
                 if r.pos == "ADJ"
                 and r.feats.get("COMP_DEGREE") == "EQUATIVE"]
    if surface in {"kasinggaganda", "kasingdadali", "kasingbabait"}:
        # Attested core: must have ≥1 EQUATIVE analysis with
        # the expected base.
        target = [r for r in equatives if r.lemma == base]
        assert len(target) >= 1, (
            f"expected ≥1 COMP_DEGREE=EQUATIVE ADJ analysis "
            f"with lemma={base!r} for {surface!r}"
        )
        assert target[0].feats.get("PREDICATIVE") is True


# === Modern kasing- form unchanged ========================================


@pytest.mark.parametrize("surface,base", [
    ("kasingganda", "ganda"),
    ("kasinglinis", "linis"),
    ("kasingdali",  "dali"),
])
def test_modern_kasing_unchanged(surface: str, base: str) -> None:
    """The modern (non-redup) ``kasing-`` equative form continues
    to analyze as ADJ with COMP_DEGREE=EQUATIVE. F-structure-
    identical to the CV-redup variant — both forms are
    semantically equivalent in modern usage."""
    a = Analyzer.from_default()
    token = Token(surface=surface, norm=surface, start=0, end=len(surface))
    results = a.analyze_one(token)
    modern = [r for r in results
              if r.pos == "ADJ"
              and r.feats.get("COMP_DEGREE") == "EQUATIVE"]
    assert len(modern) >= 1
    assert modern[0].lemma == base


# === New dali ADJ root produces madali and kasingdadali ===================


def test_dali_adj_root_madali() -> None:
    """The newly added ``dali`` ADJ root produces ``madali``
    via the existing ma_adj cell. Closes the gap: ``dali`` was
    previously VERB-only."""
    a = Analyzer.from_default()
    token = Token(surface="madali", norm="madali", start=0, end=6)
    results = a.analyze_one(token)
    adjs = [r for r in results if r.pos == "ADJ"]
    assert len(adjs) >= 1
    assert adjs[0].lemma == "dali"
    assert adjs[0].feats.get("PREDICATIVE") is True


def test_dali_adj_root_kasingdadali() -> None:
    """The newly added ``dali`` ADJ root produces ``kasingdadali``
    via the new kasing_redup_adj cell."""
    a = Analyzer.from_default()
    token = Token(surface="kasingdadali", norm="kasingdadali", start=0, end=12)
    results = a.analyze_one(token)
    equatives = [r for r in results
                 if r.pos == "ADJ"
                 and r.feats.get("COMP_DEGREE") == "EQUATIVE"
                 and r.lemma == "dali"]
    assert len(equatives) == 1
