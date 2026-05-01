"""Phase 5d Commit 2: pa-...-an DV causative.

Phase 4 §7.7 deferred ``pa-...-an`` and other less-common
causative variants alongside ``ipang-`` / ``ika-``. Phase 5c
Commit 4 lifted ``ipang-`` / ``ika-``; Phase 5d adds the
parallel pa-DV causative form, mirroring the existing pa-OV-
direct shape with the DV ``-an`` suffix.

The pa-...-an variant pivots the location / recipient of the
caused event (vs pa-...-in which pivots the causee). Surface
forms for ``kain``: ``pinakainan`` (PFV), ``pinakakainan``
(IPFV), ``pakakainan`` (CTPL).

These tests cover:

* Morph generation: pa-DV PFV/IPFV/CTPL across kain/inom/basa.
* Parse-level: NOM-marked pivot = location, GEN-marked CAUSER
  = OBJ-CAUSER.
* Regression: plain DV (sulatan, kinain-an) still binds to
  OBJ-AGENT when CAUS=NONE; pa-OV (pa-...-in) still binds to
  OBJ-CAUSER under its existing rule path.
* LMT diagnostics clean.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import tokenize


def _first(text: str) -> tuple[FStructure, list]:
    rs = parse_text(text)
    assert rs, f"no parse for {text!r}"
    _, f, _, diags = rs[0]
    return f, diags


def _morph(word: str, voice: str, aspect: str, caus: str | None = None):
    """Return the first MorphAnalysis matching the given features,
    or None."""
    toks = tokenize(word)
    ml = analyze_tokens(toks)
    for a in ml[0]:
        if a.pos != "VERB":
            continue
        if a.feats.get("VOICE") != voice:
            continue
        if a.feats.get("ASPECT") != aspect:
            continue
        if caus is not None and a.feats.get("CAUS") != caus:
            continue
        return a
    return None


# === Morph: pa-DV surface forms generate ===============================


class TestPaDvMorph:

    def test_pinakainan_pfv(self) -> None:
        a = _morph("pinakainan", "DV", "PFV", caus="DIRECT")
        assert a is not None
        assert a.lemma == "kain"

    def test_pinakakainan_ipfv(self) -> None:
        a = _morph("pinakakainan", "DV", "IPFV", caus="DIRECT")
        assert a is not None
        assert a.lemma == "kain"

    def test_pakakainan_ctpl(self) -> None:
        a = _morph("pakakainan", "DV", "CTPL", caus="DIRECT")
        assert a is not None
        assert a.lemma == "kain"

    def test_pinabasahan_pfv(self) -> None:
        # basa is vowel-final; -an triggers h-epenthesis.
        a = _morph("pinabasahan", "DV", "PFV", caus="DIRECT")
        assert a is not None
        assert a.lemma == "basa"

    def test_pinainuman_pfv(self) -> None:
        # inom + an → inuman (high-vowel-deletion-style sandhi).
        a = _morph("pinainuman", "DV", "PFV", caus="DIRECT")
        assert a is not None
        assert a.lemma == "inom"


# === Parse-level: pa-DV produces CAUSE-...-AT PRED =====================


class TestPaDvParse:

    def test_kain_pa_dv(self) -> None:
        f, _ = _first("Pinakainan ng nanay ang bata.")
        assert f.feats.get("PRED") == "CAUSE-EAT-AT <SUBJ, OBJ-CAUSER>"
        assert f.feats.get("VOICE") == "DV"
        # SUBJ = location pivot (NOM-marked bata)
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("CASE") == "NOM"
        # OBJ-CAUSER = the causer (GEN-marked nanay)
        oc = f.feats.get("OBJ-CAUSER")
        assert isinstance(oc, FStructure)
        assert oc.feats.get("CASE") == "GEN"
        assert oc.feats.get("LEMMA") == "nanay"

    def test_basa_pa_dv(self) -> None:
        f, _ = _first("Pinabasahan ng nanay ang bata.")
        assert f.feats.get("PRED") == "CAUSE-READ-AT <SUBJ, OBJ-CAUSER>"

    def test_inom_pa_dv(self) -> None:
        f, _ = _first("Pinainuman ng nanay ang bata.")
        assert f.feats.get("PRED") == "CAUSE-DRINK-AT <SUBJ, OBJ-CAUSER>"

    def test_ipfv_aspect(self) -> None:
        f, _ = _first("Pinakakainan ng nanay ang bata.")
        assert f.feats.get("ASPECT") == "IPFV"
        assert f.feats.get("PRED") == "CAUSE-EAT-AT <SUBJ, OBJ-CAUSER>"

    def test_ctpl_aspect(self) -> None:
        f, _ = _first("Pakakainan ng nanay ang bata.")
        assert f.feats.get("ASPECT") == "CTPL"
        assert f.feats.get("PRED") == "CAUSE-EAT-AT <SUBJ, OBJ-CAUSER>"


# === Regression: plain DV (CAUS=NONE) still routes to OBJ-AGENT ========


class TestPlainDvRegression:
    """The voice_specs entry for plain DV gained an explicit
    CAUS=NONE constraint to prevent the pa-DV (CAUS=DIRECT) forms
    from cross-firing it. Verify plain DV still works."""

    def test_sulatan_plain_dv(self) -> None:
        f, _ = _first("Sinulatan ng bata ang nanay.")
        assert f.feats.get("PRED") == "WRITE <SUBJ, OBJ-AGENT>"
        # OBJ-AGENT, not OBJ-CAUSER.
        assert isinstance(f.feats.get("OBJ-AGENT"), FStructure)
        assert "OBJ-CAUSER" not in f.feats


# === Regression: pa-OV (pa-...-in) still works =========================


class TestPaOvRegression:

    def test_pinakain_pa_ov(self) -> None:
        f, _ = _first("Pinakain ng nanay ang bata.")
        assert f.feats.get("PRED") == "CAUSE-EAT <SUBJ, OBJ-CAUSER>"
        assert f.feats.get("VOICE") == "OV"


# === LMT clean ==========================================================


class TestPaDvLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Pinakainan ng nanay ang bata.",
            "Pinabasahan ng nanay ang bata.",
            "Pinainuman ng nanay ang bata.",
        ):
            _, diags = _first(s)
            assert not any(d.is_blocking() for d in diags), (
                f"unexpected blocking diags on {s!r}: "
                f"{[d.kind for d in diags]}"
            )

    def test_no_lmt_mismatch(self) -> None:
        for s in (
            "Pinakainan ng nanay ang bata.",
            "Pinabasahan ng nanay ang bata.",
        ):
            _, diags = _first(s)
            assert not any(d.kind == "lmt-mismatch" for d in diags)
