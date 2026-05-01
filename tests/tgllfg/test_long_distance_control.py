"""Phase 5c §7.6 follow-on (Commit 3): long-distance control.

Phase 4 §7.6 deferred nested-XCOMP control chains, citing
"functional uncertainty in the unifier" as a prerequisite. In
practice, *finite-depth* control chains don't need functional
uncertainty — they need explicit ``S_XCOMP`` rules where a
control verb is itself the head of an embedded clause (its SUBJ
becomes the gap). Phase 5c Commit 3 adds 6 such rules (3 control
classes × 2 link variants); composing the per-level binding
equations across depth N gives a single f-node shared across all
SUBJ slots.

A second piece is required: the homophone disambiguator's
left-context rule for ``na`` is extended so that ``na`` directly
following a control verb is the linker (not the aspectual clitic
ALREADY). Without this, the placement pass would strip the
linker and the nested wrap rule couldn't fire.

These tests cover:

* 2-deep, 3-deep, 4-deep AV control chains with control-binding
  propagation.
* 3-deep chain with non-AV (OV) innermost — the controllee
  routes to ``OBJ-AGENT`` per Phase 5c Commit 1.
* Matrix transitive control + nested intransitive control.
* Negation at any level (outer, middle, inner).
* Phase 5b's recursive embedded-clause LMT walker descends to all
  levels and fires no spurious diagnostics.
* Disambiguator unit test for the new ``na``-after-control-verb
  rule.
"""

from __future__ import annotations

from tgllfg.clitics.placement import disambiguate_homophone_clitics
from tgllfg.common import FStructure, MorphAnalysis
from tgllfg.pipeline import parse_text


def _first(text: str) -> tuple[FStructure, list]:
    rs = parse_text(text)
    assert rs, f"no parse for {text!r}"
    _, f, _, diags = rs[0]
    return f, diags


def _xcomp_chain_ids(f: FStructure) -> list[int]:
    """Return the SUBJ f-node ids walking down the XCOMP chain
    starting at `f`, capped at depth 6."""
    ids: list[int] = []
    cur = f
    for _ in range(7):
        s = cur.feats.get("SUBJ")
        ids.append(s.id if isinstance(s, FStructure) else -1)
        xc = cur.feats.get("XCOMP")
        if not isinstance(xc, FStructure):
            break
        cur = xc
    return ids


# === 2-deep chains =======================================================


class TestTwoDeep:

    def test_psych_embeds_intrans(self) -> None:
        # ``Gusto kong pumayag na kumain`` —
        # "I want to agree to eat".
        # Matrix WANT <SUBJ, XCOMP>; middle AGREE <SUBJ, XCOMP>;
        # innermost EAT <SUBJ>.
        f, _ = _first("Gusto kong pumayag na kumain.")
        assert f.feats.get("PRED") == "WANT <SUBJ, XCOMP>"
        xc = f.feats["XCOMP"]
        assert isinstance(xc, FStructure)
        assert xc.feats.get("PRED") == "AGREE <SUBJ, XCOMP>"
        inner = xc.feats["XCOMP"]
        assert isinstance(inner, FStructure)
        assert inner.feats.get("PRED") == "EAT <SUBJ>"

    def test_intrans_embeds_psych_was_already_supported(self) -> None:
        # Sanity check that the matrix-intrans + nested-psych
        # case continues to work: ``Pumayag siyang gustong
        # kumain``. The matrix wrap rule is INTRANS; the nested
        # rule is the new PSYCH variant.
        f, _ = _first("Pumayag siyang gustong kumain.")
        ids = _xcomp_chain_ids(f)
        assert len(ids) == 3
        assert len(set(ids)) == 1, f"chain not unified: {ids}"

    def test_chain_binding_identifies_subj_across_levels(self) -> None:
        # Matrix.SUBJ === XCOMP.SUBJ === XCOMP.XCOMP.SUBJ for
        # an AV chain (no OV-routing detour).
        f, _ = _first("Gusto kong pumayag na kumain.")
        ids = _xcomp_chain_ids(f)
        assert len(ids) == 3
        assert len(set(ids)) == 1


# === 3-deep chains =======================================================


class TestThreeDeep:

    def test_psych_intrans_av_transitive(self) -> None:
        # ``Gusto kong pumayag na kumain ng isda`` — innermost
        # is AV-transitive; ``ng isda`` is OBJ.
        f, _ = _first("Gusto kong pumayag na kumain ng isda.")
        ids = _xcomp_chain_ids(f)
        assert len(ids) == 3
        assert len(set(ids)) == 1
        # Innermost has bare OBJ (AV).
        inner = f.feats["XCOMP"].feats["XCOMP"]  # type: ignore[union-attr]
        assert isinstance(inner, FStructure)
        assert isinstance(inner.feats.get("OBJ"), FStructure)

    def test_psych_intrans_ov_innermost_routes_obj_agent(self) -> None:
        # ``Gusto kong pumayag na kakainin ang isda`` — innermost
        # is OV. Per Phase 5c Commit 1, the controllee at the OV
        # level is OBJ-AGENT (the eater), not SUBJ (the patient
        # pivot). Chain: matrix.SUBJ === XCOMP.SUBJ ===
        # XCOMP.XCOMP.OBJ-AGENT.
        f, _ = _first("Gusto kong pumayag na kakainin ang isda.")
        m_subj = f.feats["SUBJ"]
        assert isinstance(m_subj, FStructure)
        xc1 = f.feats["XCOMP"]
        assert isinstance(xc1, FStructure)
        xc2 = xc1.feats["XCOMP"]
        assert isinstance(xc2, FStructure)
        oa = xc2.feats.get("OBJ-AGENT")
        assert isinstance(oa, FStructure)
        assert m_subj.id == xc1.feats["SUBJ"].id == oa.id  # type: ignore[union-attr]
        # Innermost SUBJ is the patient pivot — distinct id.
        assert xc2.feats["SUBJ"].id != m_subj.id  # type: ignore[union-attr]

    def test_matrix_trans_nested_intrans(self) -> None:
        # ``Pinilit ng nanay ang batang pumayag na kumain`` —
        # matrix is OV transitive control (forcer=nanay,
        # forcee=bata); nested is intransitive control. The
        # forcee bata propagates through the chain as the eater.
        f, _ = _first("Pinilit ng nanay ang batang pumayag na kumain.")
        ids = _xcomp_chain_ids(f)
        assert len(ids) == 3
        assert len(set(ids)) == 1

    def test_nested_trans_with_overt_forcer(self) -> None:
        # ``Gusto kong pinilit ng nanay na kumain`` — nested
        # transitive control under psych. The forcer (ng nanay)
        # remains overt in the nested S_XCOMP; the forcee (matrix
        # SUBJ ko) is the gap.
        f, _ = _first("Gusto kong pinilit ng nanay na kumain.")
        xc = f.feats["XCOMP"]
        assert isinstance(xc, FStructure)
        # Nested OBJ-AGENT (forcer = nanay) is overt.
        oa = xc.feats.get("OBJ-AGENT")
        assert isinstance(oa, FStructure)
        assert oa.feats.get("CASE") == "GEN"
        ids = _xcomp_chain_ids(f)
        assert len(set(ids)) == 1


# === 4-deep ==============================================================


class TestFourDeep:

    def test_four_deep_chain(self) -> None:
        # ``Gusto kong pumayag na pumayag na kumain`` — synthetic
        # 4-level chain (psych → intrans → intrans → AV).
        # Verifies the rules compose without a fixed-depth limit.
        f, _ = _first("Gusto kong pumayag na pumayag na kumain.")
        ids = _xcomp_chain_ids(f)
        assert len(ids) == 4
        assert len(set(ids)) == 1


# === Negation under nested control ======================================


class TestNegationInChain:

    def test_outer_negation(self) -> None:
        # ``Hindi gusto kong pumayag na kumain`` — outer NEG.
        # POLARITY=NEG on matrix only.
        f, _ = _first("Hindi gusto kong pumayag na kumain.")
        assert f.feats.get("POLARITY") == "NEG"
        xc = f.feats["XCOMP"]
        assert isinstance(xc, FStructure)
        assert xc.feats.get("POLARITY") != "NEG"

    def test_middle_negation(self) -> None:
        # ``Gusto kong hindi pumayag na kumain`` — NEG on middle
        # (the AGREE clause).
        f, _ = _first("Gusto kong hindi pumayag na kumain.")
        assert f.feats.get("POLARITY") != "NEG"
        xc = f.feats["XCOMP"]
        assert isinstance(xc, FStructure)
        assert xc.feats.get("POLARITY") == "NEG"

    def test_inner_negation(self) -> None:
        # ``Gusto kong pumayag na hindi kumain`` — NEG on inner
        # EAT clause.
        f, _ = _first("Gusto kong pumayag na hindi kumain.")
        xc = f.feats["XCOMP"]
        assert isinstance(xc, FStructure)
        inner = xc.feats["XCOMP"]
        assert isinstance(inner, FStructure)
        assert inner.feats.get("POLARITY") == "NEG"


# === Phase 5b embedded-clause LMT walker descends to all levels =========


class TestEmbeddedLmtCleanAcrossDepth:
    """Phase 5b's apply_lmt_with_check recursively descends every
    XCOMP/COMP that has its own PRED. With the Phase 5c Commit 3
    nested-control rules creating multi-level XCOMP chains, the
    walker now visits 2, 3, and 4 levels deep — each must pass
    LMT cleanly, with no spurious mismatch diagnostics."""

    def test_two_deep_clean(self) -> None:
        _, diags = _first("Gusto kong pumayag na kumain.")
        assert not any(d.is_blocking() for d in diags)
        assert not any(d.kind == "lmt-mismatch" for d in diags)

    def test_three_deep_av_clean(self) -> None:
        _, diags = _first("Gusto kong pumayag na kumain ng isda.")
        assert not any(d.is_blocking() for d in diags)
        assert not any(d.kind == "lmt-mismatch" for d in diags)

    def test_three_deep_ov_innermost_clean(self) -> None:
        _, diags = _first("Gusto kong pumayag na kakainin ang isda.")
        assert not any(d.is_blocking() for d in diags)
        assert not any(d.kind == "lmt-mismatch" for d in diags)

    def test_four_deep_clean(self) -> None:
        _, diags = _first("Gusto kong pumayag na pumayag na kumain.")
        assert not any(d.is_blocking() for d in diags)
        assert not any(d.kind == "lmt-mismatch" for d in diags)


# === Disambiguator: na after control verb is the linker =================


class TestDisambiguatorNaAfterCtrlVerb:
    """Unit test for the extended left-context rule in
    `disambiguate_homophone_clitics`: ``na`` directly following a
    control verb (`CTRL_CLASS != NONE`) is the linker, never the
    aspectual ALREADY clitic."""

    def test_na_after_intrans_ctrl_verb_is_linker(self) -> None:
        ctrl_verb = MorphAnalysis(
            lemma="payag",
            pos="VERB",
            feats={"CTRL_CLASS": "INTRANS", "VOICE": "AV"},
        )
        link_na = MorphAnalysis(lemma="na", pos="PART", feats={"LINK": "NA"})
        clitic_na = MorphAnalysis(
            lemma="na",
            pos="PART",
            feats={"is_clitic": True, "ASPECT_PART": "ALREADY"},
        )
        analyses = [
            [ctrl_verb],
            [link_na, clitic_na],
        ]
        out = disambiguate_homophone_clitics(analyses)
        # Only the linker reading survives.
        assert len(out[1]) == 1
        assert out[1][0].feats.get("LINK") == "NA"

    def test_na_after_psych_ctrl_verb_is_linker(self) -> None:
        ctrl_verb = MorphAnalysis(
            lemma="gusto", pos="VERB", feats={"CTRL_CLASS": "PSYCH"}
        )
        link_na = MorphAnalysis(lemma="na", pos="PART", feats={"LINK": "NA"})
        clitic_na = MorphAnalysis(
            lemma="na",
            pos="PART",
            feats={"is_clitic": True, "ASPECT_PART": "ALREADY"},
        )
        analyses = [[ctrl_verb], [link_na, clitic_na]]
        out = disambiguate_homophone_clitics(analyses)
        assert len(out[1]) == 1
        assert out[1][0].feats.get("LINK") == "NA"

    def test_na_after_non_ctrl_verb_is_clitic(self) -> None:
        # Regression: ``na`` after a non-control verb (`Kumain
        # na`) is still the aspectual clitic ALREADY.
        plain_verb = MorphAnalysis(
            lemma="kain",
            pos="VERB",
            feats={"VOICE": "AV", "CTRL_CLASS": "NONE"},
        )
        link_na = MorphAnalysis(lemma="na", pos="PART", feats={"LINK": "NA"})
        clitic_na = MorphAnalysis(
            lemma="na",
            pos="PART",
            feats={"is_clitic": True, "ASPECT_PART": "ALREADY"},
        )
        analyses = [[plain_verb], [link_na, clitic_na]]
        out = disambiguate_homophone_clitics(analyses)
        # Only the clitic reading survives.
        assert len(out[1]) == 1
        assert out[1][0].feats.get("is_clitic") is True
