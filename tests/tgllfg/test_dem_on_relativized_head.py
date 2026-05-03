"""Phase 5e Commit 17: demonstrative on a relativized head.

Phase 5d Commit 3 added post-modifier demonstrative
(``ang batang ito`` "this child"). Phase 4 §7.5 has long
admitted relativization (``ang batang kumain`` "the child
that ate"). The combination — a post-modifier demonstrative on
the head of a relative clause (``ang batang ito na kumain``
"this child who ate") — was deferred under Phase 5d Commit 3
out-of-scope as needing "ranker-policy refinement".

Investigation in Phase 5e Commit 17 showed the deferral note
was inaccurate: the construction wasn't being mis-ranked, it
was failing to parse at all. The root cause was a latent bug
in the Phase 5e Commit 16 disambiguator branch for ``na``
after a demonstrative DET / ADP — the branch compared
``DEM=='YES'`` against the morph-analysis value, but the
particles.yaml entries set ``DEM: YES`` which YAML parses as
the Python boolean ``True``. The string comparison silently
never fired; the Phase 5e Commit 16 MED / DIST cases that
appeared to work were doing so via a fallback (the clitic-pass
moved the standalone ``na`` to clause-final as the aspectual
``ALREADY`` enclitic, and the bare-NP rule absorbed the
DEM-DET as a determiner with DEIXIS percolating).

Phase 5e Commit 17 corrects the comparison to
``ma.feats.get("DEM") is True``. With the disambiguator
branch firing as designed, the standalone ``na`` after a
demonstrative is forced to the linker reading (clitic readings
dropped), the clitic-pass leaves it in place, and the
existing Phase 5d Commit 3 post-mod-dem rule composes with the
existing Phase 4 §7.5 RC rule without any new grammar rules.
The dem-on-RC construction parses correctly across all three
deixis values.

These tests cover:

* Basic dem-on-RC with all three deixis values (PROX / MED /
  DIST).
* Both linker variants on the post-mod dem (bound ``-ng`` for
  PROX, standalone ``na`` for MED / DIST), plus the RC's
  ``na`` linker that follows.
* GEN-headed dem-on-RC (in OV-actor / possessor position).
* RC body variants — intransitive AV, transitive AV with OBJ.
* Regression: Phase 5e Commit 16 MED / DIST pre-mod dem cases
  must now use the proper pre-mod-dem rule (no ``ASPECT_PART
  =ALREADY`` ADJ member from the old fallback).
* Regression: Phase 5d Commit 3 post-mod dem alone still
  parses; Phase 4 §7.5 RC alone still parses; ``na`` ALREADY
  clitic still works after a VERB (clitic-pass disambiguator
  unchanged for VERB-prefix cases).
* LMT diagnostics clean.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.pipeline import parse_text


def _first(text: str) -> tuple[FStructure, list]:
    rs = parse_text(text)
    assert rs, f"no parse for {text!r}"
    _, f, _, diags = rs[0]
    return f, diags


def _has_rc_adj(subj: FStructure) -> bool:
    """True if SUBJ has at least one ADJ member that looks like a
    relative clause (carries a verb's PRED + VOICE + ASPECT)."""
    adj = subj.feats.get("ADJ")
    if adj is None:
        return False
    for m in adj:
        if (
            isinstance(m, FStructure)
            and m.feats.get("PRED") is not None
            and m.feats.get("VOICE") is not None
        ):
            return True
    return False


# === NOM dem-on-RC: head is SUBJ ========================================


class TestNomDemOnRC:

    def test_batang_ito_na_kumain_prox(self) -> None:
        # ``Tumakbo ang batang ito na kumain.``
        # "the child who ate ran" — head=bata, DEIXIS=PROX, RC=kumain
        f, _ = _first("Tumakbo ang batang ito na kumain.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("DEIXIS") == "PROX"
        assert subj.feats.get("CASE") == "NOM"
        assert _has_rc_adj(subj), "expected RC as ADJ on SUBJ"

    def test_batang_iyan_na_kumain_med(self) -> None:
        # MED — post-mod dem with bound ``-ng`` (after vowel-final
        # bata) takes the linker variant ``-ng``; ``iyan`` is
        # consonant-final though, so the post-mod ``-ng`` doesn't
        # apply between bata and iyan; the linker is the bound
        # ``-ng`` after bata, then ``iyan`` is the dem, then ``na``
        # is the RC linker.
        f, _ = _first("Tumakbo ang batang iyan na kumain.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("DEIXIS") == "MED"
        assert _has_rc_adj(subj)

    def test_batang_iyon_na_kumain_dist(self) -> None:
        f, _ = _first("Tumakbo ang batang iyon na kumain.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("DEIXIS") == "DIST"
        assert _has_rc_adj(subj)

    def test_consonant_final_head_na_dem_na_rc(self) -> None:
        # ``ang lalaki na ito na kumain`` — vowel-final head with
        # standalone ``na`` for the post-mod-dem linker, then
        # another ``na`` for the RC. Both ``na`` tokens must
        # survive disambiguation (the second is post-DEM-DET ``ito``
        # → linker reading; the first is post-NOUN ``lalaki`` →
        # linker reading).
        f, _ = _first("Tumakbo ang lalaki na ito na kumain.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "lalaki"
        assert subj.feats.get("DEIXIS") == "PROX"
        assert _has_rc_adj(subj)

    def test_transitive_rc_with_dem(self) -> None:
        # ``ang batang ito na kumain ng isda`` —
        # "this child who ate fish".
        f, _ = _first("Tumakbo ang batang ito na kumain ng isda.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("DEIXIS") == "PROX"
        # Verify the RC is transitive AV by checking for OBJ in the
        # RC's f-structure.
        adj = subj.feats.get("ADJ")
        assert adj is not None
        rc_with_obj = False
        for m in adj:
            if isinstance(m, FStructure) and m.feats.get("OBJ") is not None:
                rc_with_obj = True
                break
        assert rc_with_obj, "expected RC ADJ member with OBJ"


# === GEN dem-on-RC: head is OV-actor ====================================


class TestGenDemOnRC:

    def test_ng_batang_nito_na_kumain_in_ov_actor(self) -> None:
        # ``Kinain ng batang nito na kumain ang isda``
        # "the fish was eaten by this child who ate"
        # The OV-actor (OBJ-AGENT) is ``ng batang nito`` modified
        # by a relative clause ``na kumain``. ``nito`` is the
        # GEN-marked PROX dem (case-agreed with the GEN-marked
        # head ``ng bata``); the RC's linker is ``na`` after the
        # consonant-final ADP ``nito``.
        rs = parse_text(
            "Kinain ng batang nito na kumain ang isda.",
            n_best=10,
        )
        assert rs
        for _, f, _, _ in rs:
            oa = f.feats.get("OBJ-AGENT")
            if (
                isinstance(oa, FStructure)
                and oa.feats.get("LEMMA") == "bata"
                and oa.feats.get("DEIXIS") == "PROX"
                and _has_rc_adj(oa)
            ):
                return
        assert False, "no parse with GEN-headed dem-on-RC"


# === Phase 5e Commit 16 MED / DIST regression ===========================


class TestPreModDemNotViaFallback:
    """Phase 5e Commit 16 added a pre-modifier dem rule for MED /
    DIST (``iyan na bata`` / ``iyon na bata``). The disambiguator
    branch that supports this rule was buggy in Phase 5e Commit 16
    (compared against the wrong type) and only got fixed in
    Phase 5e Commit 17. These tests pin that the pre-mod dem rule
    is now firing as designed — there should be no
    ``ASPECT_PART=ALREADY`` ADJ member from the old fallback
    (clitic-pass moving ``na`` to clause-final)."""

    def test_iyan_na_bata_no_already_adj(self) -> None:
        f, _ = _first("Kumain iyan na bata.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("DEIXIS") == "MED"
        # The matrix's ADJ should NOT carry ASPECT_PART=ALREADY
        # (which it would if the fallback were firing).
        adj = f.feats.get("ADJ")
        if adj is not None:
            for m in adj:
                if isinstance(m, FStructure):
                    assert m.feats.get("ASPECT_PART") != "ALREADY", (
                        "old fallback (ALREADY clitic absorbed) is "
                        "still firing; pre-mod-dem rule should be "
                        "consuming the ``na`` as linker"
                    )

    def test_iyon_na_bata_no_already_adj(self) -> None:
        f, _ = _first("Kumain iyon na bata.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("DEIXIS") == "DIST"
        adj = f.feats.get("ADJ")
        if adj is not None:
            for m in adj:
                if isinstance(m, FStructure):
                    assert m.feats.get("ASPECT_PART") != "ALREADY"


# === Regression: existing constructions still work ======================


class TestRegression:

    def test_post_modifier_dem_alone_still_works(self) -> None:
        # Phase 5d Commit 3 baseline.
        f, _ = _first("Kumain ang batang ito.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("DEIXIS") == "PROX"

    def test_rc_alone_still_works(self) -> None:
        # Phase 4 §7.5 baseline.
        f, _ = _first("Tumakbo ang batang kumain.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        assert _has_rc_adj(subj)

    def test_aspectual_na_after_verb_still_clitic(self) -> None:
        # The disambiguator's VERB-prefix branch is unchanged;
        # ``na`` after the matrix V is still the ALREADY clitic.
        f, _ = _first("Kumain na ang bata.")
        adj = f.feats.get("ADJ")
        assert adj is not None
        found_already = any(
            isinstance(m, FStructure)
            and m.feats.get("ASPECT_PART") == "ALREADY"
            for m in adj
        )
        assert found_already, "expected ASPECT_PART=ALREADY on ADJ member"

    def test_pre_modifier_dem_with_rc_still_works(self) -> None:
        # ``itong batang kumain`` — Phase 5e Commit 16 + Phase 4 §7.5.
        # Pre-mod dem composes with RC; verified working in
        # Phase 5e Commit 16 (PROX uses bound ``-ng`` linker, no
        # disambiguator dependency).
        f, _ = _first("Tumakbo itong batang kumain.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("DEIXIS") == "PROX"
        assert _has_rc_adj(subj)


# === LMT clean ===========================================================


class TestDemOnRCLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Tumakbo ang batang ito na kumain.",
            "Tumakbo ang batang iyan na kumain.",
            "Tumakbo ang batang iyon na kumain.",
            "Tumakbo ang batang ito na kumain ng isda.",
            "Tumakbo ang lalaki na ito na kumain.",
        ):
            _, diags = _first(s)
            assert not any(d.is_blocking() for d in diags), (
                f"unexpected blocking diags on {s!r}: "
                f"{[d.kind for d in diags]}"
            )

    def test_no_lmt_mismatch(self) -> None:
        for s in (
            "Tumakbo ang batang ito na kumain.",
            "Tumakbo ang batang ito na kumain ng isda.",
        ):
            _, diags = _first(s)
            assert not any(d.kind == "lmt-mismatch" for d in diags)
