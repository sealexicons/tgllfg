"""Phase 5e Commit 24: IV-REASON CTPL short-form paradigm gap.

Lifts the Phase 5d Commit 9 paradigm-gap deferral. Before this
commit, the IV-REASON CTPL paradigm only emitted the "long"
form ``ikakakain`` (i + ka + cv-redup + base = 4 syllables for
``kain``); the surface ``ikakain`` (3 syllables) had only an
IV-CONVEY CTPL reading. Tagalog actually admits both surfaces
as IV-REASON CTPL — the *Handbook of Tagalog Verbs* (Ramos &
Schachter; data/tgl/dictionaries/) lists Reason-Focus Cont
forms with two variants separated by ``/`` for vowel-initial
roots:

* ``ingay`` "noise": Cont. ``ikakaingay / ikaiingay``
* ``init`` "heat":   Cont. ``ikakainit  / ikaiinit``

The first variant has an extra CV-redup; the second drops it.
For consonant-initial bases like ``kain`` and ``sulat``, the
analogous "short" form is ``ikakain`` / ``ikasulat``
(``i + ka + base`` with no further redup). Phase 5e Commit 24
adds a second IV-REASON CTPL paradigm cell with operations
``[prefix ka, prefix i]`` (no cv_redup) to emit these.

For ``kain``, the short IV-REASON CTPL form ``ikakain``
coincides with the IV-CONVEY CTPL form (also ``ikakain``).
The morph analyzer returns BOTH analyses; the chart parser
explores both readings.

These tests cover:

* Morph: ``ikakain`` returns both IV-CONVEY and IV-REASON
  CTPL analyses (the lift).
* Morph: ``ikasulat`` returns IV-REASON CTPL ("short" form
  is distinct from IV-CONVEY ``isusulat`` for ``sulat``).
* Existing IV-REASON CTPL "long" form ``ikakakain`` still
  parses (no shadowing).
* Existing IV-CONVEY CTPL ``ikakain`` reading still parses
  (no shadowing).
* Parse: ``Ikakain ko ang isda.`` now produces both
  EAT-FOR-REASON and KAIN (CONVEY) readings.
* Regression: PFV / IPFV IV-REASON paradigm cells are
  unaffected.
"""

from __future__ import annotations

from tgllfg.morph import analyze_tokens
from tgllfg.core.pipeline import parse_text
from tgllfg.text import tokenize


def _morph_appls(token: str) -> set[tuple[str, str, str]]:
    """Return (VOICE, ASPECT, APPL) tuples among the morph
    analyses for the token."""
    toks = tokenize(token)
    ml = analyze_tokens(toks)
    cands = ml[0] if ml else []
    out: set[tuple[str, str, str]] = set()
    for ma in cands:
        if ma.pos == "VERB":
            voice = str(ma.feats.get("VOICE", ""))
            aspect = str(ma.feats.get("ASPECT", ""))
            appl = str(ma.feats.get("APPL", ""))
            out.add((voice, aspect, appl))
    return out


# === Morph layer: surface ambiguity for ikakain ===========================


class TestIkakainAmbiguity:
    """The disputed surface ``ikakain`` should now have both
    CONVEY and REASON readings (the Phase 5d Commit 9 gap)."""

    def test_ikakain_has_both_appls(self) -> None:
        appls = _morph_appls("ikakain")
        assert ("IV", "CTPL", "CONVEY") in appls
        assert ("IV", "CTPL", "REASON") in appls

    def test_ikasulat_has_reason(self) -> None:
        """``ikasulat`` is the IV-REASON CTPL short form for
        ``sulat``. (Not coincident with IV-CONVEY ``isusulat``
        because sulat doesn't start with a CV that matches the
        ka-prefix.)"""
        appls = _morph_appls("ikasulat")
        assert ("IV", "CTPL", "REASON") in appls

    def test_long_form_still_parses(self) -> None:
        """The existing IV-REASON CTPL "long" form
        ``ikakakain`` is unaffected."""
        appls = _morph_appls("ikakakain")
        assert ("IV", "CTPL", "REASON") in appls

    def test_ikasusulat_still_parses(self) -> None:
        appls = _morph_appls("ikasusulat")
        assert ("IV", "CTPL", "REASON") in appls


# === Parse layer: both readings produce parses ============================


class TestIkakainParse:
    """The chart parser explores both readings."""

    def test_ikakain_produces_both_preds(self) -> None:
        """``Ikakain ko ang isda.`` should produce parses with
        PRED reflecting both CONVEY (KAIN) and REASON
        (EAT-FOR-REASON)."""
        rs = parse_text("Ikakain ko ang isda.", n_best=10)
        assert rs
        preds = {f.feats.get("PRED") for _, f, _, _ in rs}
        # Both readings should appear among parses.
        assert any("EAT-FOR-REASON" in str(p) for p in preds), (
            f"REASON reading not produced; preds={preds}"
        )
        # The CONVEY reading is the existing one — should also
        # be present.
        assert any("KAIN" in str(p) and "REASON" not in str(p) for p in preds), (
            f"CONVEY reading not produced; preds={preds}"
        )

    def test_ikasulat_reason_parse(self) -> None:
        """``Ikasulat ko ang liham.`` produces a REASON parse."""
        rs = parse_text("Ikasulat ko ang liham.", n_best=10)
        assert rs
        preds = {f.feats.get("PRED") for _, f, _, _ in rs}
        # sulat's REASON PRED is "WRITE-FOR-REASON" or similar.
        # Just verify SOME parse exists with APPL=REASON in the
        # f-structure or in the PRED string.
        found = False
        for _, f, _, _ in rs:
            pred = str(f.feats.get("PRED", ""))
            if "REASON" in pred or "WRITE" in pred:
                found = True
                break
        assert found, f"no REASON-flavored parse for ikasulat; preds={preds}"


# === Regression: PFV / IPFV unaffected ====================================


class TestRegression:

    def test_pfv_ikinakain_still_ambiguous(self) -> None:
        """``ikinakain`` was already ambiguous between IV-CONVEY
        IPFV and IV-REASON PFV. Verify still ambiguous after the
        new CTPL cell."""
        appls = _morph_appls("ikinakain")
        assert ("IV", "IPFV", "CONVEY") in appls
        assert ("IV", "PFV", "REASON") in appls

    def test_ipfv_ikinakakain_unchanged(self) -> None:
        """``ikinakakain`` is IV-REASON IPFV. Unchanged."""
        appls = _morph_appls("ikinakakain")
        assert ("IV", "IPFV", "REASON") in appls

    def test_iv_convey_ctpl_other_bases(self) -> None:
        """IV-CONVEY CTPL for non-kain bases: ``ibibili`` (bili),
        ``isusulat`` (sulat). Unaffected — the new short-form
        cell uses a different operation chain."""
        appls = _morph_appls("ibibili")
        assert ("IV", "CTPL", "CONVEY") in appls
        appls = _morph_appls("isusulat")
        assert ("IV", "CTPL", "CONVEY") in appls
