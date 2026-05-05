"""Phase 5e Commit 9: nested-control composition with multi-arg
embedded clauses.

Phase 5d Commits 8 and 9's deferral lists flagged two
compositions as available structurally but not pinned with
tests:

* **Nested pa-causatives under control** — Phase 5c §7.6 Commit 3
  added nested-S_XCOMP rules (a control verb's XCOMP is itself
  another control verb whose XCOMP is the action). When the
  innermost is a pa-OV (CAUS=DIRECT) clause introduced by
  Phase 5d Commit 8's S_XCOMP variants, the controller chains
  through the SUBJs to the embedded ``OBJ-CAUSER``.
  Example: ``Gusto kong pumayag na pakakainin ang bata.``
  "I want [him] to agree to feed the child."
* **IV multi-GEN under nested control** — Phase 5d Commit 9
  added 3-arg IV S_XCOMP rules. When stacked inside the
  Phase 5c Commit 3 nested-control, the controller chains to
  the embedded ``OBJ-AGENT`` while ``OBJ-PATIENT`` stays overt.
  Example: ``Gusto kong pumayag na ipaggagawa ang silya ng nanay.``
  "I want [him] to agree to make the chair (for) the mother."

Both compositions work via existing rules; this commit is
**test-only** — no grammar / lex changes — and adds explicit
assertions on the cross-level f-node identity chains.
"""

from __future__ import annotations

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _first(text: str) -> FStructure:
    rs = parse_text(text)
    assert rs, f"no parse for {text!r}"
    return rs[0][1]


def _find_inner_pred(text: str, inner_pred: str) -> FStructure | None:
    """Return the first parse where the matrix's XCOMP.XCOMP has
    PRED == ``inner_pred``."""
    rs = parse_text(text, n_best=15)
    for _, f, _, _ in rs:
        x = f.feats.get("XCOMP")
        if not isinstance(x, FStructure):
            continue
        xx = x.feats.get("XCOMP")
        if isinstance(xx, FStructure) and xx.feats.get("PRED") == inner_pred:
            return f
    return None


def _xcomp(f: FStructure) -> FStructure:
    x = f.feats["XCOMP"]
    assert isinstance(x, FStructure)
    return x


# === Nested pa-OV (CAUS=DIRECT) under control =============================


class TestNestedPaOvUnderControl:
    """Outer control verb's XCOMP is another control verb whose
    XCOMP is a pa-OV (CAUS=DIRECT) clause. The controller chains
    through three levels: matrix.SUBJ === XCOMP.SUBJ ===
    XCOMP.XCOMP.OBJ-CAUSER (the typed actor slot for monoclausal
    direct causatives)."""

    def test_psych_intrans_pa_ov(self) -> None:
        """``Gusto kong pumayag na pakakainin ang bata.`` Outer:
        gusto (PSYCH); middle: pumayag (INTRANS); inner: pakakainin
        (pa-OV CAUS=DIRECT, CTPL aspect)."""
        f = _find_inner_pred(
            "Gusto kong pumayag na pakakainin ang bata.",
            inner_pred="CAUSE-EAT <SUBJ, OBJ-CAUSER>",
        )
        assert f is not None
        # Three-level f-node identity for the controller.
        m_subj = f.feats["SUBJ"]
        mid = _xcomp(f)
        mid_subj = mid.feats["SUBJ"]
        inner = _xcomp(mid)
        inner_oc = inner.feats["OBJ-CAUSER"]
        assert isinstance(m_subj, FStructure)
        assert isinstance(mid_subj, FStructure)
        assert isinstance(inner_oc, FStructure)
        assert m_subj.id == mid_subj.id == inner_oc.id
        # The pa-OV's pivot (causee) is a separate slot.
        inner_subj = inner.feats["SUBJ"]
        assert isinstance(inner_subj, FStructure)
        assert inner_subj.feats.get("LEMMA") == "bata"
        assert inner_subj.id != m_subj.id

    def test_psych_intrans_pa_ov_3arg(self) -> None:
        """3-arg pa-OV under nested control: ``Gusto kong pumayag
        na pakakainin ang bata ng kanin.`` Inner has SUBJ=bata
        (causee), OBJ-PATIENT=kanin, OBJ-CAUSER=gap (controller)."""
        f = _find_inner_pred(
            "Gusto kong pumayag na pakakainin ang bata ng kanin.",
            inner_pred="CAUSE-EAT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>",
        )
        assert f is not None
        inner = _xcomp(_xcomp(f))
        # OBJ-PATIENT is overt.
        op = inner.feats.get("OBJ-PATIENT")
        assert isinstance(op, FStructure)
        assert op.feats.get("LEMMA") == "kanin"
        # OBJ-CAUSER chains to the matrix controller.
        m_subj = f.feats["SUBJ"]
        oc = inner.feats["OBJ-CAUSER"]
        assert isinstance(m_subj, FStructure)
        assert isinstance(oc, FStructure)
        assert m_subj.id == oc.id

    def test_intrans_intrans_pa_ov(self) -> None:
        """``Pumayag akong gustong pakakainin ang bata.`` Outer:
        pumayag (INTRANS); middle: gusto (PSYCH); inner: pa-OV.
        Different control-class ordering than the previous test."""
        f = _find_inner_pred(
            "Pumayag akong gustong pakakainin ang bata.",
            inner_pred="CAUSE-EAT <SUBJ, OBJ-CAUSER>",
        )
        assert f is not None
        m_subj = f.feats["SUBJ"]
        inner = _xcomp(_xcomp(f))
        inner_oc = inner.feats["OBJ-CAUSER"]
        assert isinstance(m_subj, FStructure)
        assert isinstance(inner_oc, FStructure)
        assert m_subj.id == inner_oc.id

    def test_psych_psych_pa_ov(self) -> None:
        """Psych + psych + pa-OV. ``Gusto kong gustong pakakainin
        ang bata.`` Two psych control verbs nested with pa-OV
        innermost."""
        f = _find_inner_pred(
            "Gusto kong gustong pakakainin ang bata.",
            inner_pred="CAUSE-EAT <SUBJ, OBJ-CAUSER>",
        )
        assert f is not None


# === IV multi-GEN under nested control ===================================


class TestIvMultiGenUnderNestedControl:
    """Outer control + middle control + inner IV multi-GEN.
    The controller chains to the embedded OBJ-AGENT; the
    OBJ-PATIENT (Phase 5d Commit 9 gap target = OBJ-AGENT)
    stays overt as a GEN-NP."""

    def test_iv_ben_3arg_under_nested(self) -> None:
        """``Gusto kong pumayag na ipaggagawa ang silya ng nanay.``
        Outer: gusto (PSYCH); middle: pumayag (INTRANS); inner:
        ipaggagawa (IV-BEN 3-arg, CTPL). SUBJ=silya (BEN pivot),
        OBJ-PATIENT=nanay (overt GEN), OBJ-AGENT=gap (= matrix
        controller)."""
        f = _find_inner_pred(
            "Gusto kong pumayag na ipaggagawa ang silya ng nanay.",
            inner_pred="MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
        )
        assert f is not None
        inner = _xcomp(_xcomp(f))
        # Three slots fully bound:
        subj = inner.feats["SUBJ"]
        op = inner.feats["OBJ-PATIENT"]
        oa = inner.feats["OBJ-AGENT"]
        assert isinstance(subj, FStructure)
        assert isinstance(op, FStructure)
        assert isinstance(oa, FStructure)
        # The gap (OBJ-AGENT) is the matrix controller.
        m_subj = f.feats["SUBJ"]
        assert isinstance(m_subj, FStructure)
        assert m_subj.id == oa.id

    def test_iv_ben_2arg_under_nested(self) -> None:
        """2-arg IV-BEN under nested control:
        ``Gusto kong pumayag na ipaggagawa ang kapatid.`` (no
        retained PATIENT). Innermost is the 2-arg PRED."""
        f = _find_inner_pred(
            "Gusto kong pumayag na ipaggagawa ang kapatid.",
            inner_pred="MAKE-FOR <SUBJ, OBJ-AGENT>",
        )
        assert f is not None


# === Negation composition ===============================================


class TestNegationComposition:
    """Negation at any level of the nested chain composes via
    the recursive PART[POLARITY=NEG] rules."""

    def test_neg_at_innermost_pa_ov(self) -> None:
        f = _find_inner_pred(
            "Gusto kong pumayag na hindi pakakainin ang bata.",
            inner_pred="CAUSE-EAT <SUBJ, OBJ-CAUSER>",
        )
        assert f is not None
        inner = _xcomp(_xcomp(f))
        assert inner.feats.get("POLARITY") == "NEG"

    def test_neg_at_middle(self) -> None:
        """``Gusto kong hindi pumayag na pakakainin ang bata.``
        Middle clause carries POLARITY=NEG."""
        f = _find_inner_pred(
            "Gusto kong hindi pumayag na pakakainin ang bata.",
            inner_pred="CAUSE-EAT <SUBJ, OBJ-CAUSER>",
        )
        assert f is not None
        mid = _xcomp(f)
        assert mid.feats.get("POLARITY") == "NEG"


# === LMT diagnostics ====================================================


class TestLmtDiagnostics:
    """All compositions produce no blocking LMT diagnostics —
    the recursive ``apply_lmt_with_check`` walker validates
    every embedded f-structure with its own PRED."""

    def test_no_blocking_pa_ov_under_nested(self) -> None:
        rs = parse_text("Gusto kong pumayag na pakakainin ang bata.", n_best=5)
        for _, _f, _c, diags in rs:
            blocking = [d for d in diags if d.kind != "lmt-mismatch"]
            assert blocking == [], f"unexpected blocking diags: {blocking}"

    def test_no_blocking_iv_ben_under_nested(self) -> None:
        rs = parse_text(
            "Gusto kong pumayag na ipaggagawa ang silya ng nanay.", n_best=5
        )
        for _, _f, _c, diags in rs:
            blocking = [d for d in diags if d.kind != "lmt-mismatch"]
            assert blocking == [], f"unexpected blocking diags: {blocking}"


# === Regression: single-level versions unchanged ========================


class TestRegression:
    """Phase 5d Commit 8 (pa-OV under control, single level) and
    Commit 9 (IV multi-GEN under control, single level) still
    work."""

    def test_single_level_pa_ov_under_control(self) -> None:
        # Single-level case: matrix WANT directly over the pa-OV
        # (no middle control verb) — XCOMP is the pa-OV directly,
        # so the nested-aware ``_find_inner_pred`` helper isn't
        # the right shape.
        rs = parse_text("Gusto kong pakakainin ang bata.", n_best=10)
        seen = False
        for _, fl, _, _ in rs:
            x = fl.feats.get("XCOMP")
            if isinstance(x, FStructure) and x.feats.get("PRED") == "CAUSE-EAT <SUBJ, OBJ-CAUSER>":
                seen = True
                break
        assert seen

    def test_single_level_iv_3arg_under_control(self) -> None:
        rs = parse_text("Gusto kong ipaggagawa ang kapatid ng silya.", n_best=10)
        seen = False
        for _, fl, _, _ in rs:
            x = fl.feats.get("XCOMP")
            if isinstance(x, FStructure) and x.feats.get("PRED") == "MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>":
                seen = True
                break
        assert seen
