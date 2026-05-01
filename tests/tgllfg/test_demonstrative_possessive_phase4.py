"""Phase 4 §7.8: demonstratives, possessives, quantifier float.

Three constructions added in this commit:

* **Demonstratives** (``ito`` / ``iyan`` / ``iyon``): a ``DEM=YES``
  feature added to all 9 demonstrative entries gates a per-case
  standalone-NP rule (``NP[CASE=X] → DET[CASE=X, DEM=YES]``) that
  admits demonstrative pronouns as bare NPs. The DET-N rule is
  also re-equated to ``(↑) = ↓1`` so DET features (CASE, MARKER,
  optional DEIXIS) percolate into the NP's f-structure.
* **Possessives**: a per-case ``NP[CASE=X] → NP[CASE=X] NP[CASE=GEN]``
  rule attaches a GEN-NP possessor with ``(↑ POSS) = ↓2``. The
  pronominal possessive form (``ang aklat ko``) was deferred in
  Phase 4 because the §7.3 clitic-placement pass moved the
  pronominal clitic to post-V; lifted in Phase 5c §7.8 follow-on
  via context-aware placement (see
  ``tests/tgllfg/test_pronominal_possessive.py``).
* **Quantifier float** (``lahat`` / ``iba``): a clause-level
  ``S → S Q`` rule attaches the floated quantifier as a matrix
  ADJ member, with a binding equation ``(↓2 ANTECEDENT) = (↑ SUBJ)``
  linking it to SUBJ. The pre-NP partitive form (``lahat ng bata``)
  is deferred — needs a QP non-terminal.

These tests cover:

* Standalone demonstrative as SUBJ / OBJ (3 deixis values).
* DEIXIS percolates onto the NP's f-structure.
* Possessive ``ng``-NP creates POSS feature.
* Floated quantifier creates ADJ member with QUANT and ANTECEDENT
  bound to SUBJ.
* Negative case: bare ``ang`` (no DEIXIS, no DEM=YES) does not
  trigger the standalone-demonstrative rule.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.pipeline import parse_text


def _first(text: str) -> FStructure:
    results = parse_text(text)
    assert results, f"no parse for {text!r}"
    return results[0][1]


# === Standalone demonstrative pronouns ====================================


def test_standalone_demonstrative_subj_prox() -> None:
    """``Kumain ito``: ``ito`` (PROX demonstrative) standalone as
    SUBJ. SUBJ.PRED is the synthesized 'PRO'; DEIXIS=PROX rides
    on the SUBJ."""
    f = _first("Kumain ito.")
    subj = f.feats.get("SUBJ")
    assert isinstance(subj, FStructure)
    assert subj.feats.get("PRED") == "PRO"
    assert subj.feats.get("DEIXIS") == "PROX"


def test_standalone_demonstrative_subj_med() -> None:
    f = _first("Tumakbo iyan.")
    subj = f.feats.get("SUBJ")
    assert isinstance(subj, FStructure)
    assert subj.feats.get("DEIXIS") == "MED"


def test_standalone_demonstrative_subj_dist() -> None:
    f = _first("Kumain iyon.")
    subj = f.feats.get("SUBJ")
    assert isinstance(subj, FStructure)
    assert subj.feats.get("DEIXIS") == "DIST"


def test_standalone_demonstrative_obj() -> None:
    """``Kinain iyan ng aso``: ``iyan`` (NOM-marked demonstrative,
    MED) is the OV pivot SUBJ; ``ng aso`` is OBJ-AGENT (typed in
    the Phase 5b OBJ-θ-in-grammar alignment). The pivot
    demonstrative is the relativized-out / topicalized argument
    in OV."""
    f = _first("Kinain iyan ng aso.")
    subj = f.feats.get("SUBJ")
    assert isinstance(subj, FStructure)
    assert subj.feats.get("DEIXIS") == "MED"
    assert "OBJ-AGENT" in f.feats


def test_standalone_demonstrative_genitive() -> None:
    """``Kumain ang aso niyon``: ``niyon`` (= ``ng iyon``, GEN
    demonstrative DIST) is OBJ in AV-tr. PRED=PRO; DEIXIS=DIST."""
    f = _first("Kumain ang aso niyon.")
    obj = f.feats.get("OBJ")
    assert isinstance(obj, FStructure)
    assert obj.feats.get("DEIXIS") == "DIST"
    assert obj.feats.get("PRED") == "PRO"


def test_bare_ang_not_demonstrative() -> None:
    """Plain ``ang`` (no DEM=YES) does not trigger the standalone
    demonstrative rule. ``Kumain ang.`` should fail to parse
    (``ang`` requires a noun head)."""
    results = parse_text("Kumain ang.")
    assert not results, f"unexpected parse: {results}"


# === Possessives ==========================================================


def test_possessive_ng_modifier() -> None:
    """``Kinain ng aso ang isda ng bata``: ``ng bata`` is possessor
    of ``isda`` (the SUBJ in OV)."""
    f = _first("Kinain ng aso ang isda ng bata.")
    subj = f.feats.get("SUBJ")
    assert isinstance(subj, FStructure)
    poss = subj.feats.get("POSS")
    assert isinstance(poss, FStructure)
    assert poss.feats.get("CASE") == "GEN"


def test_possessive_in_obj_position() -> None:
    """Possessor on a GEN-marked OBJ. ``Kumain ang aso ng isda ng
    bata`` parses ambiguously (POSS could attach to SUBJ or OBJ);
    verify at least one parse puts POSS on OBJ."""
    results = parse_text("Kumain ang aso ng isda ng bata.", n_best=10)
    assert results
    has_obj_poss = any(
        isinstance(f.feats.get("OBJ"), FStructure)
        and isinstance(f.feats["OBJ"].feats.get("POSS"), FStructure)  # type: ignore[union-attr]
        for _, f, _, _ in results
    )
    assert has_obj_poss


def test_no_possessive_when_no_extra_gen() -> None:
    """Without an extra GEN-NP, no POSS feature is set."""
    f = _first("Kumain ang aso.")
    subj = f.feats.get("SUBJ")
    assert isinstance(subj, FStructure)
    assert "POSS" not in subj.feats


# === Quantifier float =====================================================


def test_quantifier_float_lahat() -> None:
    """``Kumain ang bata lahat``: ``lahat`` floats to clause-final,
    rides into matrix ADJ as a sub-f-structure carrying QUANT=ALL,
    bound to SUBJ via ANTECEDENT."""
    f = _first("Kumain ang bata lahat.")
    adj = f.feats.get("ADJ")
    assert adj is not None
    members = list(adj)  # type: ignore[arg-type]
    quants = [
        m for m in members
        if isinstance(m, FStructure) and m.feats.get("QUANT") == "ALL"
    ]
    assert quants, f"no QUANT=ALL in matrix ADJ; members={[m.feats for m in members]}"
    # ANTECEDENT binds to matrix SUBJ.
    ante = quants[0].feats.get("ANTECEDENT")
    subj = f.feats.get("SUBJ")
    assert isinstance(ante, FStructure)
    assert isinstance(subj, FStructure)
    assert ante.id == subj.id


def test_quantifier_float_iba() -> None:
    """``iba`` floats the same way; QUANT=OTHER."""
    f = _first("Kumain ang bata iba.")
    adj = f.feats.get("ADJ")
    members = list(adj)  # type: ignore[arg-type]
    quants = [
        m for m in members
        if isinstance(m, FStructure) and m.feats.get("QUANT") == "OTHER"
    ]
    assert quants


def test_quantifier_float_with_transitive() -> None:
    """Quantifier float over a transitive clause."""
    f = _first("Kinain ng aso ang isda lahat.")
    adj = f.feats.get("ADJ")
    members = list(adj)  # type: ignore[arg-type]
    quants = [
        m for m in members
        if isinstance(m, FStructure) and m.feats.get("QUANT") == "ALL"
    ]
    assert quants


# === Combinations =========================================================


def test_demonstrative_with_possessive() -> None:
    """Demonstrative SUBJ with a possessor: ``Kumain iyon ng bata``.
    iyon is DEM[NOM, DIST] standalone NP; ng bata is the possessor.
    But this construction is ambiguous with iyon as SUBJ + ng bata
    as separate OBJ. Verify at least one parse has DEIXIS on SUBJ."""
    results = parse_text("Kumain iyon ng bata.", n_best=10)
    assert results
    has_dem = any(
        isinstance(f.feats.get("SUBJ"), FStructure)
        and f.feats["SUBJ"].feats.get("DEIXIS") == "DIST"  # type: ignore[union-attr]
        for _, f, _, _ in results
    )
    assert has_dem
