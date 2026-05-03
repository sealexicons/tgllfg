"""Phase 5e Commit 12: mag-...-an reciprocal / social.

Schachter & Otanes 1972 §5.27 documents the ``mag-...-an``
pattern as the canonical Tagalog reciprocal / social form: an
action performed cooperatively or mutually by a plural SUBJ.
Examples: ``nag-iyak-an`` "cried together"; ``nag-bigay-an``
"exchanged"; ``nag-kain-an`` "ate together".

Plan §10.1 Group D originally flagged ``ka-...-an`` as the
"reciprocal causative" affix. Investigation against S&O 1972 +
Ramos 1971 + R&B 1986 confirmed that the well-attested
reciprocal pattern is ``mag-...-an``; ``ka-...-an`` is more
typically a noun-deriving pattern in Tagalog and isn't a verbal
voice/applicative. Phase 5e Commit 12 implements the attested
form rather than the speculative one.

Implementation:

* New ``mag_an`` affix class with three paradigm cells (PFV /
  IPFV / CTPL). Each cell carries ``MOOD=SOC`` (lifting the
  Phase 4 §7.2 SOC-as-inventory-only deferral) and ``RECP=YES``.
* New BASE entries for kain and bili reciprocal with PRED
  ``EAT-TOGETHER <SUBJ>`` and ``BUY-EXCHANGE <SUBJ>``.
* ``mag_an`` registered in kain's and bili's affix_class lists
  in ``data/tgl/roots.yaml``.

Ambiguity: the plain AV-intr lex entry (no MOOD constraint)
matches reciprocal MorphAnalyses too (per the parser's
non-conflict matcher), so reciprocal forms produce two parses
— one with the bare ``EAT`` PRED, one with ``EAT-TOGETHER``.
This mirrors the Phase 5d §7.6 raising / control ambiguity:
both readings are well-formed and the tests assert that the
reciprocal reading is among the n-best.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.pipeline import parse_text


def _find_pred(text: str, expected_pred: str) -> FStructure | None:
    rs = parse_text(text, n_best=15)
    for _, f, _, _ in rs:
        if f.feats.get("PRED") == expected_pred:
            return f
    return None


# === mag-...-an reciprocal across PFV / IPFV / CTPL =====================


class TestMagAnReciprocal:
    """The three aspect cells of the reciprocal paradigm produce
    distinct surface forms with the same PRED template."""

    def test_kain_pfv(self) -> None:
        f = _find_pred("Nagkainan sila.", "EAT-TOGETHER <SUBJ>")
        assert f is not None
        assert f.feats.get("ASPECT") == "PFV"
        assert f.feats.get("MOOD") == "SOC"

    def test_kain_ipfv(self) -> None:
        f = _find_pred("Nagkakainan sila.", "EAT-TOGETHER <SUBJ>")
        assert f is not None
        assert f.feats.get("ASPECT") == "IPFV"

    def test_kain_ctpl(self) -> None:
        f = _find_pred("Magkakainan sila.", "EAT-TOGETHER <SUBJ>")
        assert f is not None
        assert f.feats.get("ASPECT") == "CTPL"

    def test_bili_pfv(self) -> None:
        f = _find_pred("Nagbilihan sila.", "BUY-EXCHANGE <SUBJ>")
        assert f is not None

    def test_bili_ipfv(self) -> None:
        f = _find_pred("Nagbibilihan sila.", "BUY-EXCHANGE <SUBJ>")
        assert f is not None


# === Negation ===========================================================


class TestNegation:
    """Reciprocals compose with the §7.2 negation rules."""

    def test_neg_reciprocal(self) -> None:
        f = _find_pred(
            "Hindi nagkainan sila.", "EAT-TOGETHER <SUBJ>"
        )
        assert f is not None
        assert f.feats.get("POLARITY") == "NEG"


# === Discrimination =====================================================


class TestDiscrimination:
    """Plain mag- AV / -um- AV forms must not pick up the
    reciprocal PRED — the reciprocal lex only matches MOOD=SOC
    morph analyses."""

    def test_plain_kumain_not_reciprocal(self) -> None:
        rs = parse_text("Kumain ang bata.", n_best=10)
        preds = {str(f.feats.get("PRED")) for _, f, _, _ in rs}
        assert "EAT-TOGETHER <SUBJ>" not in preds

    def test_plain_naglinis_not_reciprocal(self) -> None:
        # Synthesizer fallback (linis isn't in BASE) — the plain
        # mag- form gets bare PRED.
        rs = parse_text("Naglinis ang bata.", n_best=10)
        preds = {str(f.feats.get("PRED")) for _, f, _, _ in rs}
        # No reciprocal PRED should surface for plain naglinis.
        assert not any("TOGETHER" in p or "EXCHANGE" in p for p in preds)


# === Regression =========================================================


class TestRegression:
    """Plain AV forms still parse identically to before."""

    def test_kumain_ang_bata(self) -> None:
        rs = parse_text("Kumain ang bata.", n_best=10)
        assert rs
        for _, f, _, _ in rs:
            if f.feats.get("PRED") == "EAT <SUBJ>":
                return
        raise AssertionError("expected plain EAT <SUBJ> reading")

    def test_kumain_ang_aso_ng_isda(self) -> None:
        rs = parse_text("Kumain ang aso ng isda.", n_best=10)
        seen = False
        for _, f, _, _ in rs:
            if f.feats.get("PRED") == "EAT <SUBJ, OBJ>":
                seen = True
                break
        assert seen


# === LMT diagnostics ====================================================


class TestLmtDiagnostics:
    """Reciprocal parses produce no blocking LMT diagnostics."""

    def test_no_blocking(self) -> None:
        rs = parse_text("Nagkainan sila.", n_best=5)
        for _, _f, _c, diags in rs:
            blocking = [d for d in diags if d.kind != "lmt-mismatch"]
            assert blocking == [], f"unexpected blocking diags: {blocking}"
