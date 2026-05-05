"""Phase 5c §7.7 follow-on (Commit 4): ipang- instrumental and
ika- reason applicatives.

Phase 4 §7.7 deferred both applicatives because the existing
``nasal_substitute`` op replaces the base's first consonant
(``bili`` → ``mili``, the AV distributive ``mang-`` pattern) and
doesn't produce ``ipinambili`` (instrument-bought) where the
consonant is retained. Phase 5c lifts the deferral by adding a
new sandhi op ``nasal_assim_prefix`` that prepends the homorganic
nasal without dropping the consonant. ipang- cells use it; ika-
cells need no special phonology and follow the ipag- shape.

These tests cover:

* Sandhi unit tests for ``nasal_assim_prefix`` (b/p → m, t/d/s → n,
  k/g → ng vacuous, vowels and sonorants unchanged).
* Morph generation: ipinambili / ipinambibili / ipambibili
  (ipang- × bili PFV/IPFV/CTPL); ipinantahi (ipang- × tahi);
  ikinakain / ikinakakain / ikakakain (ika- × kain).
* Parse-level: instrumental and reason readings produce the
  expected PRED, with the actor as OBJ-AGENT and the
  instrument / reason as SUBJ.
* LMT diagnostic check: no spurious mismatches.
* Regression: the existing AV distributive ``mang-`` (which uses
  ``nasal_substitute``, the drop pattern) coexists on the same
  root with the new ipang- (the retain pattern). ``mamili`` "be a
  buyer" stays valid alongside ``ipinambili``.
"""

from __future__ import annotations

from tgllfg.core.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.morph.sandhi import nasal_assim_prefix
from tgllfg.core.pipeline import parse_text
from tgllfg.text import tokenize


def _first(text: str) -> tuple[FStructure, list]:
    rs = parse_text(text)
    assert rs, f"no parse for {text!r}"
    _, f, _, diags = rs[0]
    return f, diags


def _has_pred(text: str, pred: str) -> tuple[FStructure, list] | None:
    """Return the first parse whose matrix PRED is `pred`, or None.
    Used for ambiguous surfaces (e.g., `ikinakain` which has both
    a CONVEY-IPFV and a REASON-PFV reading)."""
    rs = parse_text(text, n_best=10)
    for _, f, _, diags in rs:
        if f.feats.get("PRED") == pred:
            return f, diags
    return None


def _morph_features(word: str, voice: str, appl: str, aspect: str) -> dict | None:
    """Return the first MorphAnalysis matching the requested
    voice / appl / aspect, or None."""
    toks = tokenize(word)
    ml = analyze_tokens(toks)
    if not ml:
        return None
    for a in ml[0]:
        if (
            a.pos == "VERB"
            and a.feats.get("VOICE") == voice
            and a.feats.get("APPL") == appl
            and a.feats.get("ASPECT") == aspect
        ):
            return dict(a.feats)
    return None


# === Sandhi: nasal_assim_prefix unit tests ===============================


class TestNasalAssimPrefix:
    """The new sandhi op: prepend an ng-final prefix to a base,
    place-assimilating the prefix's final nasal to the base's
    initial consonant — without dropping that consonant."""

    def test_bilabial_b(self) -> None:
        assert nasal_assim_prefix("pang", "bili") == "pambili"

    def test_bilabial_p(self) -> None:
        assert nasal_assim_prefix("pang", "putol") == "pamputol"

    def test_alveolar_t(self) -> None:
        assert nasal_assim_prefix("pang", "tahi") == "pantahi"

    def test_alveolar_d(self) -> None:
        assert nasal_assim_prefix("pang", "dalit") == "pandalit"

    def test_alveolar_s(self) -> None:
        assert nasal_assim_prefix("pang", "sulat") == "pansulat"

    def test_velar_k(self) -> None:
        # k → ng (vacuous: ng is already velar). k retained.
        assert nasal_assim_prefix("pang", "kuha") == "pangkuha"

    def test_velar_g(self) -> None:
        assert nasal_assim_prefix("pang", "gawa") == "panggawa"

    def test_vowel_initial_unchanged(self) -> None:
        # No assimilation: ng remains as ng before vowel.
        assert nasal_assim_prefix("pang", "ulan") == "pangulan"

    def test_sonorant_initial_unchanged(self) -> None:
        # No consonantal assimilation site; ng remains.
        assert nasal_assim_prefix("pang", "lakad") == "panglakad"

    def test_empty_base(self) -> None:
        assert nasal_assim_prefix("pang", "") == "pang"

    def test_non_ng_prefix_rejected(self) -> None:
        import pytest
        with pytest.raises(ValueError):
            nasal_assim_prefix("pag", "bili")


# === Morph generation: ipang- and ika- surface forms =====================


class TestIpangSurfaces:

    def test_pfv_bili(self) -> None:
        # PFV: pang- + bili → pambili → pinambili → ipinambili.
        feats = _morph_features("ipinambili", "IV", "INSTR", "PFV")
        assert feats is not None
        assert feats["MOOD"] == "IND"

    def test_ipfv_bili(self) -> None:
        # IPFV: cv-redup + pang-assim + -in- + i-.
        # bili → bibili → pambibili → pinambibili → ipinambibili.
        feats = _morph_features("ipinambibili", "IV", "INSTR", "IPFV")
        assert feats is not None

    def test_ctpl_bili(self) -> None:
        # CTPL: cv-redup + pang-assim + i-. No -in-.
        feats = _morph_features("ipambibili", "IV", "INSTR", "CTPL")
        assert feats is not None

    def test_pfv_tahi_alveolar_assim(self) -> None:
        # PFV: pang- + tahi → pantahi (t → n) → pinantahi →
        # ipinantahi.
        feats = _morph_features("ipinantahi", "IV", "INSTR", "PFV")
        assert feats is not None


class TestIkaSurfaces:

    def test_pfv_kain(self) -> None:
        # PFV: ka- + kain → kakain → kinakain → ikinakain.
        feats = _morph_features("ikinakain", "IV", "REASON", "PFV")
        assert feats is not None

    def test_ipfv_kain(self) -> None:
        # IPFV: cv-redup + ka- + -in- + i-.
        feats = _morph_features("ikinakakain", "IV", "REASON", "IPFV")
        assert feats is not None

    def test_ctpl_kain(self) -> None:
        feats = _morph_features("ikakakain", "IV", "REASON", "CTPL")
        assert feats is not None

    def test_pfv_sulat(self) -> None:
        feats = _morph_features("ikinasulat", "IV", "REASON", "PFV")
        assert feats is not None


# === Parse-level: ipang- instrumental ====================================


class TestIpangParse:
    """Instrumental applicative: SUBJ = INSTRUMENT (the thing
    used); OBJ-AGENT = the actor."""

    def test_bili_with_pronoun_actor(self) -> None:
        # ``Ipinambili ko ang pera`` — "money is what I bought
        # with" / "I bought [things] with money".
        f, _ = _first("Ipinambili ko ang pera.")
        assert f.feats.get("PRED") == "BUY-WITH <SUBJ, OBJ-AGENT>"
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("CASE") == "NOM"
        oa = f.feats.get("OBJ-AGENT")
        assert isinstance(oa, FStructure)
        assert oa.feats.get("CASE") == "GEN"

    def test_bili_with_full_gen(self) -> None:
        # ``Ipinambili ng nanay ang pera`` — full GEN actor.
        f, _ = _first("Ipinambili ng nanay ang pera.")
        assert f.feats.get("PRED") == "BUY-WITH <SUBJ, OBJ-AGENT>"

    def test_tahi_with_full_gen(self) -> None:
        # ``Ipinantahi ng nanay ang karayom`` — needle is the
        # instrument SUBJ.
        f, _ = _first("Ipinantahi ng nanay ang karayom.")
        assert f.feats.get("PRED") == "SEW-WITH <SUBJ, OBJ-AGENT>"


# === Parse-level: ika- reason ============================================


class TestIkaParse:
    """Reason applicative: SUBJ = REASON; OBJ-AGENT = the actor."""

    def test_sulat_with_full_gen(self) -> None:
        f, _ = _first("Ikinasulat ng bata ang gutom.")
        assert f.feats.get("PRED") == "WRITE-FOR-REASON <SUBJ, OBJ-AGENT>"

    def test_kain_reason_reading_available(self) -> None:
        # ``Ikinakain ng bata ang gutom`` is ambiguous — the
        # surface ``ikinakain`` overlaps with the IPFV bare-i-
        # CONVEY reading. Verify the REASON reading is among the
        # parses.
        result = _has_pred(
            "Ikinakain ng bata ang gutom.",
            "EAT-FOR-REASON <SUBJ, OBJ-AGENT>",
        )
        assert result is not None


# === LMT diagnostics: clean across all new readings ======================


class TestLmtClean:

    def test_ipang_no_blocking(self) -> None:
        _, diags = _first("Ipinambili ng nanay ang pera.")
        assert not any(d.is_blocking() for d in diags)
        assert not any(d.kind == "lmt-mismatch" for d in diags)

    def test_ika_no_blocking(self) -> None:
        _, diags = _first("Ikinasulat ng bata ang gutom.")
        assert not any(d.is_blocking() for d in diags)
        assert not any(d.kind == "lmt-mismatch" for d in diags)


# === Regression: nasal_substitute drop pattern still works ==============


class TestRegressionMangPatternStillWorks:
    """The new ``nasal_assim_prefix`` (retain) is distinct from the
    pre-existing ``nasal_substitute`` (drop). Both patterns coexist
    on the same root — ``mamili`` "be a buyer" (mang- AV) and
    ``ipinambili`` "instrument-bought" (ipang- IV-INSTR) both
    derive from ``bili`` with different meanings."""

    def test_mamili_av_still_generated(self) -> None:
        # mang- + bili → m-ili (drop pattern via nasal_substitute) +
        # na- prefix → namili (PFV).
        feats = _morph_features("namili", "AV", "NONE", "PFV")
        assert feats is not None

    def test_ipinambili_iv_instr_separately(self) -> None:
        # ipang- + bili (retain pattern) is independent.
        feats = _morph_features("ipinambili", "IV", "INSTR", "PFV")
        assert feats is not None
