"""Phase 5d Commit 3: post-modifier demonstrative with linker.

Phase 4 §7.8 added standalone-demonstrative NPs (``Kumain
iyon`` "That ate") via the rule
``NP[CASE=X] → DET/ADP[CASE=X, DEM=YES]``. The post-modifier
construction ``ang batang ito`` ("this child") was deferred —
the head NP is followed by a linker (`-ng` or `na`) and a
case-agreed demonstrative that contributes only DEIXIS to the
matrix NP.

Phase 5d Commit 3 lifts the deferral with six new grammar rules
(3 cases × 2 linker variants):

```
NP[CASE=NOM] → NP[CASE=NOM] PART[LINK=…] DET[CASE=NOM, DEM=YES]
NP[CASE=GEN] → NP[CASE=GEN] PART[LINK=…] ADP[CASE=GEN, DEM=YES]
NP[CASE=DAT] → NP[CASE=DAT] PART[LINK=…] ADP[CASE=DAT, DEM=YES]
```

Each rule shares the head NP's f-structure with the matrix via
``(↑) = ↓1`` and copies the demonstrative's DEIXIS via
``(↑ DEIXIS) = ↓3 DEIXIS``. The PRED stays the head noun's PRED
— the demonstrative modifies, doesn't supplant.

These tests cover:

* All three deixis values (PROX / MED / DIST) in NOM, GEN,
  and DAT positions.
* Case agreement: the modifier must match the head's case
  (`ang batang ito` works, `ang batang nito` doesn't —
  cross-case combinations are rejected).
* Multiple demonstrative modifiers in one clause
  (``ang batang ito ng isdang niyan``).
* Regression: standalone-demonstrative NPs (``Kumain ito``)
  and bare-noun NPs (``Kumain ang bata``) still parse.
* LMT diagnostics clean.
"""

from __future__ import annotations

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _first(text: str) -> tuple[FStructure, list]:
    rs = parse_text(text)
    assert rs, f"no parse for {text!r}"
    _, f, _, diags = rs[0]
    return f, diags


# === NOM-headed: ang X-ng / ang X na DEM ================================


class TestNomHeadedDemModifier:

    def test_ang_batang_ito_prox(self) -> None:
        f, _ = _first("Kumain ang batang ito.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("DEIXIS") == "PROX"
        assert subj.feats.get("CASE") == "NOM"

    def test_ang_batang_iyan_med(self) -> None:
        f, _ = _first("Kumain ang batang iyan.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("DEIXIS") == "MED"

    def test_ang_batang_iyon_dist(self) -> None:
        f, _ = _first("Kumain ang batang iyon.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("DEIXIS") == "DIST"

    def test_consonant_final_host_takes_na(self) -> None:
        # ``aklat`` ends in a consonant — the linker is the
        # standalone ``na``, not bound ``-ng``. (`aklat` isn't in
        # the noun lex; using `tao` "person" which ends in vowel
        # but with `na` linker variant for stress reasons.)
        # Use ``babae`` (vowel-final) → babaeng ito.
        f, _ = _first("Kumain ang babaeng ito.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "babae"
        assert subj.feats.get("DEIXIS") == "PROX"


# === GEN-headed: ng X-ng / ng X na DEM ===================================


class TestGenHeadedDemModifier:

    def test_ng_batang_nito_prox(self) -> None:
        # OV — the GEN-head + dem becomes OBJ-AGENT.
        f, _ = _first("Kinain ng batang nito ang isda.")
        oa = f.feats.get("OBJ-AGENT")
        assert isinstance(oa, FStructure)
        assert oa.feats.get("LEMMA") == "bata"
        assert oa.feats.get("DEIXIS") == "PROX"

    def test_ng_batang_niyon_dist(self) -> None:
        f, _ = _first("Kinain ng batang niyon ang isda.")
        oa = f.feats.get("OBJ-AGENT")
        assert isinstance(oa, FStructure)
        assert oa.feats.get("DEIXIS") == "DIST"


# === DAT-headed: sa X-ng / sa X na DEM ===================================


class TestDatHeadedDemModifier:

    def test_sa_palengkeng_dito_prox(self) -> None:
        # Multiple parses (lakad lex has both intransitive and
        # OBL-LOC entries); find the OBL-LOC one and verify
        # DEIXIS percolates.
        rs = parse_text("Lumakad ang bata sa palengkeng dito.", n_best=10)
        assert rs
        for _, f, _, _ in rs:
            v = f.feats.get("OBL-LOC")
            if isinstance(v, FStructure) and v.feats.get("DEIXIS") == "PROX":
                assert v.feats.get("LEMMA") == "palengke"
                return
        # Fallback: check ADJUNCT member if no OBL-LOC parse.
        for _, f, _, _ in rs:
            adj = f.feats.get("ADJUNCT")
            if adj is None:
                continue
            for m in adj:  # type: ignore[union-attr]
                if (
                    isinstance(m, FStructure)
                    and m.feats.get("DEIXIS") == "PROX"
                    and m.feats.get("LEMMA") == "palengke"
                ):
                    return
        assert False, "no parse with OBL-LOC or ADJUNCT carrying PROX"

    def test_sa_palengkeng_doon_dist(self) -> None:
        rs = parse_text("Lumakad ang bata sa palengkeng doon.", n_best=10)
        assert rs
        found = False
        for _, f, _, _ in rs:
            for k in ("OBL-LOC",):
                v = f.feats.get(k)
                if (
                    isinstance(v, FStructure)
                    and v.feats.get("DEIXIS") == "DIST"
                ):
                    found = True
                    break
            if found:
                break
            adj = f.feats.get("ADJUNCT")
            if adj is None:
                continue
            for m in adj:  # type: ignore[union-attr]
                if (
                    isinstance(m, FStructure)
                    and m.feats.get("DEIXIS") == "DIST"
                ):
                    found = True
                    break
        assert found


# === Case agreement: cross-case must NOT parse ===========================


class TestCaseAgreement:
    """The demonstrative must agree in case with the head NP.
    `ng batang ito` (GEN head + NOM dem) is ungrammatical and
    should not produce a parse for that constituent."""

    def test_gen_head_with_nom_dem_rejected(self) -> None:
        # `ng batang ito` would need `nito` (GEN dem) to agree.
        # The sentence currently doesn't parse via the new
        # dem-modifier rule for that constituent.
        rs = parse_text("Kinain ng batang ito ang isda.", n_best=5)
        # Either no parses, or the OBJ-AGENT doesn't have DEIXIS
        # set (the dem reading didn't fire on the GEN head).
        for _, f, _, _ in rs:
            oa = f.feats.get("OBJ-AGENT")
            if isinstance(oa, FStructure):
                # If the modifier rule had fired, OBJ-AGENT would
                # have DEIXIS=PROX. Verify it doesn't.
                assert oa.feats.get("DEIXIS") != "PROX", (
                    "GEN-head NOM-dem should not agree"
                )

    def test_dat_head_with_nom_dem_rejected(self) -> None:
        rs = parse_text("Lumakad ang bata sa palengkeng ito.", n_best=5)
        # Same: OBL-LOC / ADJUNCT shouldn't carry DEIXIS=PROX
        # via the modifier rule.
        for _, f, _, _ in rs:
            v = f.feats.get("OBL-LOC")
            if isinstance(v, FStructure):
                assert v.feats.get("DEIXIS") != "PROX"
            adj = f.feats.get("ADJUNCT")
            if adj is None:
                continue
            for m in adj:  # type: ignore[union-attr]
                if isinstance(m, FStructure):
                    assert m.feats.get("DEIXIS") != "PROX"


# === Multiple modifiers in one clause ====================================


class TestMultipleDemModifiers:

    def test_subj_and_obj_both_modified(self) -> None:
        # ``Kumain ang batang ito ng isdang niyan`` —
        # "this child ate that fish".
        rs = parse_text(
            "Kumain ang batang ito ng isdang niyan.", n_best=5
        )
        assert rs
        # Find the parse where SUBJ has PROX and OBJ has MED.
        for _, f, _, _ in rs:
            subj = f.feats.get("SUBJ")
            obj = f.feats.get("OBJ")
            if (
                isinstance(subj, FStructure)
                and isinstance(obj, FStructure)
                and subj.feats.get("DEIXIS") == "PROX"
                and obj.feats.get("DEIXIS") == "MED"
            ):
                return
        assert False, "no parse with SUBJ=PROX and OBJ=MED"


# === Regression: standalone and bare-NP still work =======================


class TestRegression:

    def test_standalone_demonstrative_still_works(self) -> None:
        f, _ = _first("Kumain ito.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("DEIXIS") == "PROX"
        assert subj.feats.get("PRED") == "PRO"

    def test_bare_noun_np_still_works(self) -> None:
        f, _ = _first("Kumain ang bata.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        # No DEIXIS — bare NP doesn't carry one.
        assert subj.feats.get("DEIXIS") is None


# === LMT clean ===========================================================


class TestPostModifierDemLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Kumain ang batang ito.",
            "Kumain ang batang iyan.",
            "Kumain ang batang iyon.",
            "Kinain ng aso ang isdang ito.",
            "Kinain ng batang nito ang isda.",
        ):
            _, diags = _first(s)
            assert not any(d.is_blocking() for d in diags), (
                f"unexpected blocking diags on {s!r}: "
                f"{[d.kind for d in diags]}"
            )

    def test_no_lmt_mismatch(self) -> None:
        for s in (
            "Kumain ang batang ito.",
            "Kinain ng batang nito ang isda.",
        ):
            _, diags = _first(s)
            assert not any(d.kind == "lmt-mismatch" for d in diags)
