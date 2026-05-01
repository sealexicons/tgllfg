"""Phase 4 §7.7: applicatives + pa-causatives.

Three new affix classes are introduced:

* ``ipag`` — benefactive applicative IV (``APPL=BEN``):
  ``ipinaggawa`` "made-for" PFV; ``ipinaggagawa`` IPFV;
  ``ipaggagawa`` CTPL.
* ``pa_in`` — direct (monoclausal) causative OV (``CAUS=DIRECT``):
  ``pinakain`` "fed (cause-eat)" PFV; ``pinakakain`` IPFV;
  ``pakakainin`` CTPL.
* ``magpa`` — indirect (biclausal) causative AV (``CAUS=INDIRECT``,
  ``CTRL_CLASS=INTRANS``): ``nagpakain`` PFV; ``nagpapakain``
  IPFV; ``magpapakain`` CTPL. Re-uses the §7.6 intransitive
  control wrap rule.

Existing IV cells are annotated with ``APPL=CONVEY`` for the bare
conveyed-pivot reading. Non-IV verbs default to ``APPL=NONE``;
non-causative verbs default to ``CAUS=NONE``.

These tests cover:

* Surface generation for all 9 new aspect cells × representative
  verbs (gawa / sulat / bili for ipag, kain / basa / inom for
  pa_in and magpa).
* Parsing positively for each variant with correct PRED + APPL /
  CAUS features.
* Biclausal causative re-uses §7.6 control: matrix.SUBJ shares
  the f-node id of XCOMP.SUBJ.
* Negative cases: an existing AV / OV entry (e.g.
  ``EAT <SUBJ, OBJ>`` for kain) doesn't spuriously match a
  causative form.
"""

from __future__ import annotations

import pytest

from tgllfg.common import FStructure, Token
from tgllfg.morph.analyzer import _get_default
from tgllfg.pipeline import parse_text


def _first(text: str) -> FStructure:
    results = parse_text(text)
    assert results, f"no parse for {text!r}"
    return results[0][1]


def _xcomp(f: FStructure) -> FStructure:
    xc = f.feats.get("XCOMP")
    assert isinstance(xc, FStructure), f"no XCOMP on {f.feats}"
    return xc


def _analyse_one(surface: str) -> list:
    return _get_default().analyze_one(Token(surface, surface, 0, len(surface)))


# === Morphology generation =================================================


@pytest.mark.parametrize("surface,voice,aspect,appl,caus", [
    # ipag- benefactive applicative IV
    ("ipinaggawa",   "IV", "PFV",  "BEN", "NONE"),
    ("ipinaggagawa", "IV", "IPFV", "BEN", "NONE"),
    ("ipaggagawa",   "IV", "CTPL", "BEN", "NONE"),
    ("ipinagsulat",   "IV", "PFV",  "BEN", "NONE"),
    ("ipinagbili",   "IV", "PFV",  "BEN", "NONE"),
    # pa-...-in monoclausal direct causative OV
    ("pinakain",     "OV", "PFV",  "NONE", "DIRECT"),
    ("pinakakain",   "OV", "IPFV", "NONE", "DIRECT"),
    ("pakakainin",   "OV", "CTPL", "NONE", "DIRECT"),
    ("pinabasa",     "OV", "PFV",  "NONE", "DIRECT"),
    ("pinainom",     "OV", "PFV",  "NONE", "DIRECT"),
    # magpa- biclausal indirect causative AV
    ("nagpakain",    "AV", "PFV",  "NONE", "INDIRECT"),
    ("nagpapakain",  "AV", "IPFV", "NONE", "INDIRECT"),
    ("magpapakain",  "AV", "CTPL", "NONE", "INDIRECT"),
    ("nagpabasa",    "AV", "PFV",  "NONE", "INDIRECT"),
    ("nagpainom",    "AV", "PFV",  "NONE", "INDIRECT"),
])
def test_applicative_causative_morph_generation(
    surface: str, voice: str, aspect: str, appl: str, caus: str,
) -> None:
    """Each new applicative / causative form is recognised by the
    morph engine with the right voice / aspect / APPL / CAUS feats."""
    out = _analyse_one(surface)
    verbs = [ma for ma in out if ma.pos == "VERB"]
    assert verbs, f"{surface}: no VERB analysis"
    ma = verbs[0]
    assert ma.feats.get("VOICE") == voice
    assert ma.feats.get("ASPECT") == aspect
    assert ma.feats.get("APPL") == appl
    assert ma.feats.get("CAUS") == caus


def test_bare_iv_carries_appl_convey() -> None:
    """The pre-existing ``i-`` IV cells are annotated APPL=CONVEY
    so they discriminate against the new applicative variants."""
    out = _analyse_one("ikinain")
    iv = next(ma for ma in out if ma.pos == "VERB" and ma.feats.get("VOICE") == "IV")
    assert iv.feats.get("APPL") == "CONVEY"


def test_non_applicative_verb_appl_none() -> None:
    """Verbs without applicative morphology default to APPL=NONE."""
    out = _analyse_one("kumain")
    av = next(ma for ma in out if ma.feats.get("VOICE") == "AV")
    assert av.feats.get("APPL") == "NONE"
    assert av.feats.get("CAUS") == "NONE"


# === Benefactive applicative parsing =======================================


def test_benefactive_applicative_parse() -> None:
    """``Ipinaggawa ng nanay ang anak`` — agent=ng (OBJ-AGENT under
    Phase 5b OBJ-θ-in-grammar alignment), beneficiary=ang (SUBJ);
    PRED carries the BEN reading."""
    f = _first("Ipinaggawa ng nanay ang anak.")
    assert f.feats.get("PRED") == "MAKE-FOR <SUBJ, OBJ-AGENT>"
    assert f.feats.get("VOICE") == "IV"


def test_benefactive_applicative_ipfv() -> None:
    """IPFV form of the benefactive parses; ASPECT propagates."""
    f = _first("Ipinaggagawa ng nanay ang anak.")
    assert f.feats.get("ASPECT") == "IPFV"
    assert f.feats.get("PRED") == "MAKE-FOR <SUBJ, OBJ-AGENT>"


def test_benefactive_with_other_anchors() -> None:
    """sulat-BEN works the same way: ipinagsulat parses."""
    f = _first("Ipinagsulat ng bata ang nanay.")
    assert f.feats.get("PRED") == "WRITE-FOR <SUBJ, OBJ-AGENT>"


# === Monoclausal causative parsing =========================================


def test_direct_causative_parse() -> None:
    """``Pinakain ng nanay ang bata`` — causer=ng (OBJ-CAUSER under
    Phase 5b OBJ-θ-in-grammar alignment), causee=ang (SUBJ)."""
    f = _first("Pinakain ng nanay ang bata.")
    assert f.feats.get("PRED") == "CAUSE-EAT <SUBJ, OBJ-CAUSER>"
    assert f.feats.get("VOICE") == "OV"


def test_direct_causative_ipfv() -> None:
    """IPFV form of the direct causative parses."""
    f = _first("Pinakakain ng nanay ang bata.")
    assert f.feats.get("ASPECT") == "IPFV"


def test_direct_causative_basa() -> None:
    f = _first("Pinabasa ng nanay ang bata.")
    assert f.feats.get("PRED") == "CAUSE-READ <SUBJ, OBJ-CAUSER>"


# === Biclausal causative re-uses §7.6 control ===========================


def test_biclausal_causative_intrans_complement() -> None:
    """``Nagpakain ang nanay na kumain``: causer=NOM SUBJ;
    intransitive AV complement (gap = SUBJ controlled)."""
    f = _first("Nagpakain ang nanay na kumain.")
    assert f.feats.get("PRED") == "CAUSE-EAT <SUBJ, XCOMP>"
    assert _xcomp(f).feats.get("PRED") == "EAT <SUBJ>"


def test_biclausal_causative_trans_complement() -> None:
    """Transitive AV complement: ``Nagpakain ang nanay na kumain
    ng isda``."""
    f = _first("Nagpakain ang nanay na kumain ng isda.")
    xc = _xcomp(f)
    assert xc.feats.get("PRED") == "EAT <SUBJ, OBJ>"
    assert "OBJ" in xc.feats


def test_biclausal_causative_control_binding() -> None:
    """Matrix.SUBJ shares the f-node id of XCOMP.SUBJ — the §7.6
    control mechanism applies."""
    f = _first("Nagpakain ang nanay na kumain.")
    matrix_subj = f.feats.get("SUBJ")
    xcomp_subj = _xcomp(f).feats.get("SUBJ")
    assert isinstance(matrix_subj, FStructure)
    assert isinstance(xcomp_subj, FStructure)
    assert matrix_subj.id == xcomp_subj.id


def test_biclausal_causative_other_anchors() -> None:
    """basa has a biclausal-causative entry; complement with a
    transitive AV verb (which always has an OBJ slot) to satisfy
    completeness inside S_XCOMP."""
    f = _first("Nagpabasa ang nanay na bumasa ng isda.")
    assert f.feats.get("PRED") == "CAUSE-READ <SUBJ, XCOMP>"


# === Discrimination: existing entries don't capture new variants =========


def test_kumain_does_not_match_causative_entry() -> None:
    """Plain ``Kumain ang aso`` should still parse with PRED
    ``EAT <SUBJ>`` (or ``EAT <SUBJ, OBJ>`` if OBJ supplied) — not
    accidentally with the causative ``CAUSE-EAT`` PRED."""
    f = _first("Kumain ang aso.")
    pred = f.feats.get("PRED")
    assert pred is not None and "CAUSE" not in str(pred)


def test_nagpakain_only_matches_causative_entry() -> None:
    """``Nagpakain ang nanay na kumain`` parses only with the
    INDIRECT causative entry — the regular kain AV-tr / AV-intr
    entries do not match because they constrain CAUS=NONE."""
    results = parse_text("Nagpakain ang nanay na kumain.")
    preds = {str(f.feats.get("PRED")) for _, f, _, _ in results}
    assert preds == {"CAUSE-EAT <SUBJ, XCOMP>"}, (
        f"unexpected PREDs: {preds}"
    )
