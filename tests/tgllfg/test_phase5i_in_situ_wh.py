"""Phase 5i Commit 3: in-situ wh-PRON in case-marked NP positions.

Roadmap §12.1 / plan-of-record §5.2, §6 Commit 3. Two new NP
shell rules in ``cfg/nominal.py``:

    NP[CASE=GEN] → ADP[CASE=GEN] PRON[WH=YES]
    NP[CASE=DAT] → ADP[CASE=DAT] PRON[WH=YES]

The Phase 5i Commit 1 wh-PRONs (``sino`` / ``ano`` / ``alin`` /
``kanino``) carry their lex-declared CASE; the cleft-style
fronting (Commit 2) consumes them in NOM-pivot position. In-situ
wh appears in case-marked argument position, requiring an ADP
wrapper:

    Kumain ka ng ano?      "You ate (some) what?"      (informal echo)
    Bumili ka ng ano?      "You bought (some) what?"
    Sumulat ka kay kanino? "You wrote to whom?"

The matrix gets a synthesized PRED (``'WH-PRO'``); the matrix's
WH and WH_LEMMA features lift from the PRON daughter for
downstream consumers. Matrix-level Q_TYPE percolation onto the
clausal S is deferred — it requires either a post-parse
f-structure walk or a defining equation in every V-headed S
frame; gated on corpus pressure.

Out-of-scope here:

* ``Kinain mo ang ano?`` (NOM-marked in-situ wh) — needs a
  parallel ``NP[CASE=NOM] → DET[CASE=NOM] PRON[WH=YES]`` shell.
  Less common; defer to Phase 5i follow-on if corpus surfaces.
* ``Pumunta ka sa saan?`` (ADP + wh-ADV) — ``saan`` already
  encodes locative; ``sa saan`` is redundant. Skip.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === In-situ wh in OBJ (ng-NP) =========================================


class TestInSituWhInObj:
    """Wh-PRON appears in OBJ position via ``ng + wh`` wrapper.
    Phase 4 transitive AV frame admits NP[CASE=GEN] as OBJ; the
    new shell produces this NP shape from ``ng + ano``."""

    @pytest.mark.parametrize("sentence,verb_pred", [
        ("Kumain ka ng ano?",  "EAT"),
        ("Bumili ka ng ano?",  "BUY"),
        ("Bumasa ka ng ano?",  "READ"),
        ("Kumain si Maria ng ano?", "EAT"),
    ])
    def test_in_situ_wh_obj(
        self, sentence: str, verb_pred: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got 0"
        )
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED", "").startswith(verb_pred)


# === In-situ wh in DAT/OBL (sa/kay-NP) =================================


class TestInSituWhInDat:
    """Wh-PRON appears in DAT/OBL position via ``sa/kay + wh``
    wrapper. ``kanino`` is the lex-DAT wh ("to whom"); ``sino`` /
    ``ano`` / ``alin`` can also fill DAT slots through the new
    shell."""

    def test_kanino_in_dat_wrapper(self) -> None:
        """``Sumulat ka kay kanino?`` — kay+kanino as DAT-NP."""
        parses = parse_text("Sumulat ka kay kanino?")
        assert len(parses) >= 1


# === Matrix-level wh feats are accessible =============================


class TestWhFeatLift:
    """The new shell rules lift ``WH`` and ``WH_LEMMA`` onto the
    matrix NP so consumers can identify wh-NPs without traversing
    into the PRON daughter."""

    def test_wh_feature_on_matrix_np(self) -> None:
        """Walk the f-structure tree of ``Kumain ka ng ano?`` and
        find a sub-f-structure with WH=YES + WH_LEMMA=ano."""
        parses = parse_text("Kumain ka ng ano?")
        assert len(parses) >= 1
        from tgllfg.core.common import FStructure
        _ct, fs, _astr, _diags = parses[0]

        def find_wh_fstructs(f, seen=None):
            if seen is None:
                seen = set()
            if not isinstance(f, FStructure):
                return []
            if id(f) in seen:
                return []
            seen.add(id(f))
            results = []
            if f.feats.get("WH") == "YES":
                results.append(f)
            for v in f.feats.values():
                if isinstance(v, FStructure):
                    results.extend(find_wh_fstructs(v, seen))
                elif isinstance(v, frozenset):
                    for m in v:
                        if isinstance(m, FStructure):
                            results.extend(find_wh_fstructs(m, seen))
            return results

        wh_fs = find_wh_fstructs(fs)
        assert len(wh_fs) >= 1, (
            f"expected at least one f-structure with WH=YES; "
            f"feats={fs.feats}"
        )
        # The first one's WH_LEMMA should be 'ano'.
        assert any(
            f.feats.get("WH_LEMMA") == "ano" for f in wh_fs
        ), (
            f"expected WH_LEMMA=ano on a wh f-structure; "
            f"got {[f.feats.get('WH_LEMMA') for f in wh_fs]}"
        )


# === Cleft-style fronting (Commit 2) still works ======================


class TestCleftStyleStillWorks:
    """The new in-situ shells must not perturb the Commit 2 cleft-
    style wh-fronting. Sanity check on the Commit 2 targets."""

    @pytest.mark.parametrize("sentence,wh_lemma", [
        ("Sino ang kumain?",   "sino"),
        ("Ano ang kinain mo?", "ano"),
        ("Alin ang kinain mo?","alin"),
    ])
    def test_cleft_unchanged(
        self, sentence: str, wh_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        wh_parses = [
            p for p in parses
            if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1
        _ct, fs, _astr, _diags = wh_parses[0]
        assert fs.feats.get("WH_LEMMA") == wh_lemma


# === Non-wh PRONs do not fire the in-situ shells =====================


class TestNonWhPronsExcluded:
    """The ``(↓2 WH) =c 'YES'`` constraint prevents non-wh PRONs
    (siya / ako / ka) from firing the in-situ shells. ``Kumain ka
    ng siya?`` is ungrammatical and should not parse via the new
    rules. (Other rules might admit it for fragmentary reasons,
    but no parse should have a ``WH-PRO`` PRED on the OBJ NP.)"""

    @pytest.mark.parametrize("sentence", [
        "Kumain ka ng siya.",
        "Bumili ka ng ako.",
    ])
    def test_non_wh_pron_does_not_form_wh_np(
        self, sentence: str
    ) -> None:
        parses = parse_text(sentence)
        # If any parse exists, no f-structure should have
        # WH-PRO synthesized as a PRED in any sub-structure.
        from tgllfg.core.common import FStructure

        def has_wh_pro(f, seen=None):
            if seen is None:
                seen = set()
            if not isinstance(f, FStructure):
                return False
            if id(f) in seen:
                return False
            seen.add(id(f))
            if f.feats.get("PRED") == "WH-PRO":
                return True
            for v in f.feats.values():
                if isinstance(v, FStructure):
                    if has_wh_pro(v, seen):
                        return True
                elif isinstance(v, frozenset):
                    for m in v:
                        if isinstance(m, FStructure):
                            if has_wh_pro(m, seen):
                                return True
            return False

        for _ct, fs, _astr, _diags in parses:
            assert not has_wh_pro(fs), (
                f"unexpected WH-PRO synthesized for {sentence!r}; "
                f"feats={fs.feats}"
            )


# === Phase 4 / 5g / 5h baselines unchanged =============================


class TestBaselinePreserved:
    """Phase 4 / 5g / 5h NP-from-ADP+N rules continue to fire on
    NOUN-headed NPs unchanged — the new wh-shells take a PRON
    daughter, not N, so the existing rules are not displaced."""

    @pytest.mark.parametrize("sentence,verb_pred", [
        ("Kumain ang aso ng isda.",       "EAT"),
        ("Bumili ng aklat ang lalaki.",   "BUY"),
        ("Sumulat ang nanay sa anak.",    "WRITE"),
    ])
    def test_baseline_np_shells_unchanged(
        self, sentence: str, verb_pred: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        # Should produce normal PRED, not WH-PRO anywhere.
        for _ct, fs, _astr, _diags in parses:
            # No matrix-level WH=YES.
            assert fs.feats.get("WH") != "YES"
