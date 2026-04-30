"""Phase 4 §7.2: aspect, mood, polarity.

Three deliverables:

* RECPFV ("recent-perfective" / "just-completed") aspect: ``ka-`` +
  CV-redup of the root produces ``kakakain`` / ``kabibili`` /
  ``kasusulat``. ASPECT=RECPFV percolates to the f-structure.
* Clausal negation: ``hindi`` (declarative) and ``huwag`` (imperative)
  attach as left-edge particles. Matrix POLARITY=NEG; for ``huwag``,
  matrix MOOD=IMP overrides the inner clause's IND.
* MOOD inventory expanded to {IND, IMP, ABIL, NVOL, SOC}. IMP is
  exercised here via huwag; SOC requires §7.3 clitics and is left as
  a pure inventory entry until then.
"""

from __future__ import annotations

from typing import Any

import pytest

from tgllfg.common import FStructure
from tgllfg.morph import Analyzer, generate_form, load_morph_data
from tgllfg.pipeline import parse_text


def _first(text: str) -> tuple[Any, FStructure, Any, list[Any]]:
    results = parse_text(text)
    assert results, f"no parse for {text!r}"
    return results[0]


def _all_fstructures(text: str) -> list[FStructure]:
    return [r[1] for r in parse_text(text)]


# === RECPFV aspect ========================================================


@pytest.mark.parametrize(
    "root,surface",
    [
        ("kain", "kakakain"),
        ("bili", "kabibili"),
        ("basa", "kababasa"),
        ("sulat", "kasusulat"),
        ("linis", "kalilinis"),
        ("tulog", "katutulog"),
    ],
)
def test_recpfv_generates(root: str, surface: str) -> None:
    """RECPFV cells generate the canonical ``ka-CV-root`` surface."""
    data = load_morph_data()
    root_obj = next(r for r in data.roots if r.citation == root)
    cells = [
        c
        for c in data.paradigm_cells
        if c.aspect == "RECPFV" and c.affix_class in root_obj.affix_class
    ]
    assert cells, f"no RECPFV cell fires for {root!r}"
    surfaces = {generate_form(root_obj, c) for c in cells}
    assert surface in surfaces


def test_recpfv_analyses_back() -> None:
    """``kakakain`` analyses back to (kain, AV, RECPFV)."""
    a = Analyzer.from_default()
    from tgllfg.common import Token

    out = a.analyze_one(Token(surface="kakakain", norm="kakakain", start=0, end=8))
    matches = [
        x for x in out
        if x.lemma == "kain" and x.feats.get("ASPECT") == "RECPFV"
    ]
    assert matches, f"no kain/AV/RECPFV analysis: {out}"


# === Polarity / clausal negation ==========================================


def test_hindi_negative_declarative() -> None:
    """``Hindi kumain ang aso`` parses with POLARITY=NEG, MOOD=IND."""
    fs = _all_fstructures("Hindi kumain ang aso.")
    assert fs, "no parse"
    matches = [f for f in fs if f.feats.get("POLARITY") == "NEG"]
    assert matches, "no parse with POLARITY=NEG"
    f = matches[0]
    assert f.feats.get("MOOD") == "IND"
    assert isinstance(f.feats.get("PRED"), str) and f.feats["PRED"].startswith("EAT")
    assert "SUBJ" in f.feats


def test_huwag_negative_polarity() -> None:
    """``Huwag kumain ang aso`` parses with POLARITY=NEG.

    Phase 4 §7.2 limitation: the matrix MOOD is *not* overridden to
    IMP from huwag's particle. The full inheritance equation
    ``(↑) = ↓2`` propagates the inner verb's MOOD=IND to matrix; an
    overlay would clash. Imperative-mood lifting from huwag is left
    to a Phase 4 §7.3 / §7.6 follow-up. The huwag particle's own
    f-structure does carry MOOD=IMP from its lex feats, but it is
    not reachable from the matrix in this commit. See
    ``docs/analysis-choices.md`` "Phase 4 §7.2"."""
    fs = _all_fstructures("Huwag kumain ang aso.")
    assert fs, "no parse"
    matches = [f for f in fs if f.feats.get("POLARITY") == "NEG"]
    assert matches, "no parse with POLARITY=NEG"


def test_negation_preserves_voice_features() -> None:
    """Negation lifts SUBJ/OBJ/VOICE/ASPECT/PRED from the inner clause."""
    fs = _all_fstructures("Hindi kinain ng aso ang isda.")
    matches = [f for f in fs if f.feats.get("POLARITY") == "NEG"]
    assert matches
    f = matches[0]
    assert f.feats.get("VOICE") == "OV"
    assert f.feats.get("ASPECT") == "PFV"
    assert "SUBJ" in f.feats and "OBJ" in f.feats


def test_affirmative_no_polarity() -> None:
    """A bare affirmative clause carries no POLARITY feature; this
    test pins down that NEG is added only by the negation particles."""
    _, f, _, _ = _first("Kumain ang aso.")
    assert "POLARITY" not in f.feats


def test_recpfv_in_negation() -> None:
    """``Hindi kakakain ang aso`` — negation composes with RECPFV."""
    fs = _all_fstructures("Hindi kakakain ang aso.")
    matches = [
        f for f in fs
        if f.feats.get("POLARITY") == "NEG" and f.feats.get("ASPECT") == "RECPFV"
    ]
    assert matches, "no NEG+RECPFV parse"


# === Mood inventory =======================================================


def test_mood_av_indicative_default() -> None:
    """The default MOOD on a finite -um-/-mag- AV verb is IND."""
    _, f, _, _ = _first("Kumain ang aso.")
    assert f.feats.get("MOOD") == "IND"


def test_mood_maka_abilitative() -> None:
    """The maka- abilitative class carries MOOD=ABIL (Phase 2C)."""
    _, f, _, _ = _first("Nakakain ang aso.")
    assert f.feats.get("MOOD") == "ABIL"


def test_mood_ma_non_volitional() -> None:
    """The ma- non-volitional class carries MOOD=NVOL (Phase 2C)."""
    _, f, _, _ = _first("Natulog ang bata.")
    assert f.feats.get("MOOD") == "NVOL"
