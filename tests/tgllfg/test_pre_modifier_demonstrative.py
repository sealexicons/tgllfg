"""Phase 5e Commit 16: pre-modifier demonstrative with linker.

Phase 5d Commit 3 added the post-modifier construction
(``ang batang ito`` "this child"). The pre-modifier variant
(``itong bata`` "this child") was deferred — it uses the
mirror-image structure: the demonstrative comes first and
serves as the determiner (replacing ``ang`` / ``ng`` / ``sa``),
followed by the linker, followed by the head N. PROX dems
(``ito`` / ``nito`` / ``dito``) are vowel-final and take the
bound ``-ng`` linker (``itong`` is split by ``split_linker_ng``
into ``ito`` + ``-ng``); MED dems (``iyan`` / ``niyan`` /
``diyan``) and DIST dems (``iyon`` / ``niyon`` / ``doon``) are
consonant-final and take the standalone ``na`` linker.

Phase 5e Commit 16 lifts the deferral with six new grammar
rules (3 cases × 2 linker variants):

```
NP[CASE=NOM] → DET[CASE=NOM, DEM=YES] PART[LINK=…] N
NP[CASE=GEN] → ADP[CASE=GEN, DEM=YES] PART[LINK=…] N
NP[CASE=DAT] → ADP[CASE=DAT, DEM=YES] PART[LINK=…] N
```

Each rule shares the demonstrative's f-structure with the
matrix via ``(↑) = ↓1`` (CASE / MARKER / DEIXIS percolate
because the dem itself carries them); the head's PRED + LEMMA
project from N via ``(↑ PRED) = ↓3 PRED`` and
``(↑ LEMMA) = ↓3 LEMMA``.

A 5th left-context exception was added to
``disambiguate_homophone_clitics``: when ``na`` is preceded
by a DEM-DET / DEM-ADP, prefer the linker reading (otherwise
the Wackernagel pass would hoist ``na`` into the post-V
cluster as the aspectual ``ALREADY`` enclitic and the new
rule could never fire for MED / DIST dems).

These tests cover:

* All three deixis values (PROX / MED / DIST) in NOM, GEN,
  and DAT positions.
* PROX uses bound ``-ng``; MED / DIST use standalone ``na``.
* Pre + post stacking on the same N (``itong batang ito``).
* Regression: standalone-dem NPs, bare-NP, post-modifier
  rule, and the ``na`` ALREADY enclitic (after V) all still
  parse.
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


# === NOM-headed: itong / iyan na / iyon na N =============================


class TestNomHeadedPreModifier:

    def test_itong_bata_prox(self) -> None:
        # ``itong`` = ito + -ng; bound linker. PROX.
        f, _ = _first("Kumain itong bata.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("DEIXIS") == "PROX"
        assert subj.feats.get("CASE") == "NOM"

    def test_iyan_na_bata_med(self) -> None:
        # MED — consonant-final dem takes standalone ``na`` linker.
        f, _ = _first("Kumain iyan na bata.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("DEIXIS") == "MED"
        assert subj.feats.get("CASE") == "NOM"

    def test_iyon_na_bata_dist(self) -> None:
        # DIST — consonant-final dem with standalone ``na``.
        f, _ = _first("Kumain iyon na bata.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("DEIXIS") == "DIST"
        assert subj.feats.get("CASE") == "NOM"

    def test_itong_babae_prox_vowel_final_head(self) -> None:
        # Vowel-final head ``babae`` — same bound linker on the dem.
        f, _ = _first("Kumain itong babae.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "babae"
        assert subj.feats.get("DEIXIS") == "PROX"


# === GEN-headed: nitong / niyan na / niyon na N ===========================


class TestGenHeadedPreModifier:

    def test_nitong_bata_prox(self) -> None:
        # OV — the GEN-marked pre-mod dem is the OBJ-AGENT.
        f, _ = _first("Kinain nitong bata ang isda.")
        oa = f.feats.get("OBJ-AGENT")
        assert isinstance(oa, FStructure)
        assert oa.feats.get("LEMMA") == "bata"
        assert oa.feats.get("DEIXIS") == "PROX"
        assert oa.feats.get("CASE") == "GEN"

    def test_niyan_na_bata_med(self) -> None:
        f, _ = _first("Kinain niyan na bata ang isda.")
        oa = f.feats.get("OBJ-AGENT")
        assert isinstance(oa, FStructure)
        assert oa.feats.get("DEIXIS") == "MED"

    def test_niyon_na_bata_dist(self) -> None:
        f, _ = _first("Kinain niyon na bata ang isda.")
        oa = f.feats.get("OBJ-AGENT")
        assert isinstance(oa, FStructure)
        assert oa.feats.get("DEIXIS") == "DIST"


# === DAT-headed: ditong / diyan na / doon na N ============================


class TestDatHeadedPreModifier:

    def test_ditong_palengke_prox(self) -> None:
        # PROX — DAT pre-mod dem in OBL-LOC position.
        rs = parse_text("Lumakad ang bata ditong palengke.", n_best=10)
        assert rs
        for _, f, _, _ in rs:
            v = f.feats.get("OBL-LOC")
            if (
                isinstance(v, FStructure)
                and v.feats.get("DEIXIS") == "PROX"
            ):
                assert v.feats.get("LEMMA") == "palengke"
                assert v.feats.get("CASE") == "DAT"
                return
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
        assert False, "no parse with PROX dem on DAT NP"

    def test_doon_na_palengke_dist(self) -> None:
        # DIST — DAT pre-mod with standalone ``na``.
        rs = parse_text("Lumakad ang bata doon na palengke.", n_best=10)
        assert rs
        found = False
        for _, f, _, _ in rs:
            v = f.feats.get("OBL-LOC")
            if (
                isinstance(v, FStructure)
                and v.feats.get("DEIXIS") == "DIST"
            ):
                found = True
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


# === Multiple modifiers / pre + post stacking ============================


class TestMultipleDemModifiers:

    def test_pre_mod_subj_post_mod_obj(self) -> None:
        # ``Kumain itong bata ng isdang niyan`` —
        # "this child ate that fish" (PROX SUBJ pre-mod, MED OBJ post-mod).
        rs = parse_text(
            "Kumain itong bata ng isdang niyan.", n_best=5
        )
        assert rs
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
        assert False, "no parse with SUBJ=PROX (pre-mod) and OBJ=MED (post-mod)"

    def test_pre_and_post_mod_same_head(self) -> None:
        # ``itong batang ito`` — pre + post-mod on same head.
        # Common in real Tagalog (R&B 1986 examples).
        f, _ = _first("Kumain itong batang ito.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        # Both pre-mod and post-mod set DEIXIS=PROX; matrix value is PROX.
        assert subj.feats.get("DEIXIS") == "PROX"


# === Regression: existing constructions still work ======================


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
        assert subj.feats.get("DEIXIS") is None

    def test_post_modifier_dem_still_works(self) -> None:
        f, _ = _first("Kumain ang batang ito.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("DEIXIS") == "PROX"

    def test_aspectual_na_after_verb_still_clitic(self) -> None:
        # ``Kumain na ang bata.`` — ``na`` is the ALREADY clitic
        # after the verb, hoisted into the post-V cluster. The new
        # DEM-DET disambiguation branch must NOT misclassify this
        # as a linker (the prev token is the VERB, not a DEM).
        f, _ = _first("Kumain na ang bata.")
        adj = f.feats.get("ADJ")
        assert adj is not None
        found_already = any(
            isinstance(m, FStructure)
            and m.feats.get("ASPECT_PART") == "ALREADY"
            for m in adj
        )
        assert found_already, "expected ASPECT_PART=ALREADY on ADJ member"


# === LMT clean ===========================================================


class TestPreModifierDemLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Kumain itong bata.",
            "Kumain iyan na bata.",
            "Kumain iyon na bata.",
            "Kinain nitong bata ang isda.",
            "Kinain niyon na bata ang isda.",
        ):
            _, diags = _first(s)
            assert not any(d.is_blocking() for d in diags), (
                f"unexpected blocking diags on {s!r}: "
                f"{[d.kind for d in diags]}"
            )

    def test_no_lmt_mismatch(self) -> None:
        for s in (
            "Kumain itong bata.",
            "Kinain nitong bata ang isda.",
        ):
            _, diags = _first(s)
            assert not any(d.kind == "lmt-mismatch" for d in diags)
