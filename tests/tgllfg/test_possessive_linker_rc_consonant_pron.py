"""Phase 5e Commit 18: possessive-linker RC with consonant-final PRON.

Phase 5d Commit 6 lifted the possessive-linker RC construction
(``aklat kong binasa`` "the book that I read") for the three
**vowel-final** GEN pronouns ``ko`` / ``mo`` / ``niya``, which fuse
with the bound linker into a single ``Vng`` surface (``kong`` /
``mong`` / ``niyang``) and are split back apart by
:func:`tgllfg.text.split_linker_ng`.

The four **consonant-final** GEN pronouns — ``natin`` (1pl-INCL),
``namin`` (1pl-EXCL), ``ninyo`` (2pl), ``nila`` (3pl) — cannot fuse
with ``-ng`` (Tagalog phonotactics) and instead surface with the
standalone ``na`` linker: ``aklat namin na binasa``, ``aklat nila
na binasa``, etc.

The wrap rule is the same dual-binding shape as Commit 6 — the
pronoun is both the head NP's ``POSS`` and the embedded RC's
``OBJ-AGENT``. Phase 5e Commit 18 extends the rule loop to also
admit ``PART[LINK=NA]`` so the standalone-linker variant fires.

Two enabling pieces were already in place from prior commits:

* The §7.3 Wackernagel pass keeps a post-NOUN PRON in place via
  ``_is_post_noun_pron`` (Phase 5c §7.8 lift) — this works for
  consonant-final pronouns without modification.
* The post-PRON ``na`` is preserved as the linker (rather than
  hoisted as the 2P ``ALREADY`` clitic) by the third left-context
  exception in ``disambiguate_homophone_clitics`` (Phase 5e Commit
  6) — fires whenever PRON-after-NOUN is followed by VERB (or
  NEG + VERB).

These tests cover:

* All four consonant-final pronouns in SUBJ position
  (``Lumakad ang bata namin na binasa``).
* Selected consonant-final pronouns in OBJ position
  (``Kumain ang bata ng libro nila na binasa``).
* OV (default in basic tests) plus IV bare (``ipinaggawa``),
  IV + DAT adjunct (``ipinagsulat sa kapatid``), and DV
  (``binasahan``) — the three non-AV voice classes admitted by
  ``S_GAP_NA``. Phase 5d Commit 6 only exercised OV; this
  commit also pins DV / IV (the existing rule supports them but
  was never tested).
* Consonant-final HEAD NPs (``kapatid namin na binasa``) — the
  surface that most clearly motivates the lift, since neither
  the head nor the PRON can take the bound ``-ng`` linker.
* Negation under the construction.
* POSS and OBJ-AGENT id-equality (the dual-binding signature).
* Vowel-final PRON + standalone ``na`` (``aklat ko na kinain``)
  also parses through the new LINK=NA branch — both linker
  variants carry the same f-equations.
* Regression: standard pronominal possessive
  (``ng libro namin``) and standard ``na``-linker relativization
  with overt NOUN actor still work (the latter strengthened to
  verify the RC's OBJ-AGENT is the overt NOUN, not a pronoun).
* LMT diagnostics clean.
"""

from __future__ import annotations

from tgllfg.clitics import reorder_clitics
from tgllfg.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import split_enclitics, split_linker_ng, tokenize


def _pipeline_lemmas(text: str) -> list[str]:
    """Run the full pre-parse pipeline and return token lemmas."""
    toks = tokenize(text)
    toks = split_enclitics(toks)
    toks = split_linker_ng(toks)
    ml = analyze_tokens(toks)
    ml = reorder_clitics(ml)
    return [cands[0].lemma if cands else "?" for cands in ml]


def _find_node_with_rc_and_poss(
    text: str, slot: str
) -> tuple[FStructure, FStructure, FStructure] | None:
    """Find a parse where ``f.feats[slot]`` has both POSS and an ADJ
    containing an RC. Returns (matrix, slot_node, poss_node) or None."""
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        node = f.feats.get(slot)
        if not isinstance(node, FStructure):
            continue
        poss = node.feats.get("POSS")
        adj = node.feats.get("ADJ")
        if isinstance(poss, FStructure) and adj:
            rcs = [m for m in adj if isinstance(m, FStructure) and "PRED" in m.feats]
            if rcs:
                return f, node, poss
    return None


# === Wackernagel: consonant-final PRON stays in place =====================


class TestWackernagelConsonantFinal:
    """Consonant-final GEN pronouns following a NOUN stay in place
    via the existing ``_is_post_noun_pron`` exception (Phase 5c §7.8
    lift). No new placement code is needed for Commit 18 — only the
    wrap rule is extended."""

    def test_namin_post_noun_stays(self) -> None:
        out = _pipeline_lemmas("Lumakad ang bata namin na binasa.")
        assert "namin" in out
        idx = out.index("namin")
        assert out[idx - 1] == "bata"
        # The standalone `na` follows directly (preserved as linker
        # by disambiguate_homophone_clitics, not hoisted as ALREADY).
        assert out[idx + 1] == "na"

    def test_ninyo_post_noun_stays(self) -> None:
        out = _pipeline_lemmas("Lumakad ang bata ninyo na binasa.")
        idx = out.index("ninyo")
        assert out[idx + 1] == "na"

    def test_nila_post_noun_stays(self) -> None:
        out = _pipeline_lemmas("Lumakad ang bata nila na binasa.")
        idx = out.index("nila")
        assert out[idx + 1] == "na"

    def test_natin_post_noun_stays(self) -> None:
        out = _pipeline_lemmas("Lumakad ang bata natin na binasa.")
        idx = out.index("natin")
        assert out[idx + 1] == "na"


# === Construction in SUBJ position ========================================


class TestPossessiveLinkerNaSubj:
    """``Lumakad ang bata <PRON> na binasa`` — head NP is matrix
    SUBJ; the consonant-final pronoun is its possessor and the
    RC's actor."""

    def test_namin_1pl_excl(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata namin na binasa.", "SUBJ"
        )
        assert result is not None
        _, subj, poss = result
        assert subj.feats.get("LEMMA") == "bata"
        assert poss.feats.get("CASE") == "GEN"
        assert poss.feats.get("NUM") == "PL"
        assert poss.feats.get("CLUSV") == "EXCL"

    def test_natin_1pl_incl(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata natin na binasa.", "SUBJ"
        )
        assert result is not None
        _, _, poss = result
        assert poss.feats.get("NUM") == "PL"
        assert poss.feats.get("CLUSV") == "INCL"

    def test_ninyo_2pl(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata ninyo na binasa.", "SUBJ"
        )
        assert result is not None
        _, _, poss = result
        assert poss.feats.get("NUM") == "PL"
        # 2pl carries no CLUSV feature (only 1pl does).
        assert poss.feats.get("CLUSV") is None

    def test_nila_3pl(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata nila na binasa.", "SUBJ"
        )
        assert result is not None
        _, _, poss = result
        assert poss.feats.get("NUM") == "PL"
        assert poss.feats.get("CLUSV") is None

    def test_poss_and_obj_agent_share_node(self) -> None:
        """The defining structural property: POSS and the RC's
        OBJ-AGENT bind to the SAME f-structure (id-equality)."""
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata namin na binasa.", "SUBJ"
        )
        assert result is not None
        _, subj, poss = result
        adj = subj.feats["ADJ"]
        rcs = [m for m in adj if isinstance(m, FStructure)]
        assert rcs, "no RC in ADJ"
        rc = rcs[0]
        oa = rc.feats.get("OBJ-AGENT")
        assert isinstance(oa, FStructure)
        assert oa is poss

    def test_rc_is_ov(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata namin na binasa.", "SUBJ"
        )
        assert result is not None
        _, subj, _ = result
        adj = subj.feats["ADJ"]
        rcs = [m for m in adj if isinstance(m, FStructure)]
        assert any(rc.feats.get("VOICE") == "OV" for rc in rcs)


# === Construction in OBJ position =========================================


class TestPossessiveLinkerNaObj:
    """``Kumain ang bata ng libro <PRON> na binasa`` — head NP is
    the AV-OBJ; the pronoun is its possessor and the RC's actor."""

    def test_namin_obj_position(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Kumain ang bata ng libro namin na binasa.", "OBJ"
        )
        assert result is not None
        _, obj, poss = result
        assert obj.feats.get("LEMMA") == "libro"
        assert poss.feats.get("NUM") == "PL"
        assert poss.feats.get("CLUSV") == "EXCL"

    def test_nila_obj_position(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Kumain ang bata ng libro nila na binasa.", "OBJ"
        )
        assert result is not None
        _, obj, poss = result
        adj = obj.feats["ADJ"]
        rcs = [m for m in adj if isinstance(m, FStructure)]
        assert rcs
        rc = rcs[0]
        oa = rc.feats.get("OBJ-AGENT")
        assert isinstance(oa, FStructure)
        assert oa is poss

    def test_ninyo_obj_position(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Kumain ang bata ng libro ninyo na binasa.", "OBJ"
        )
        assert result is not None


# === IV / DV non-AV variants ==============================================


class TestPossessiveLinkerNaNonAvVoices:
    """The S_GAP_NA frame admits OV / DV / IV non-AV verbs (Phase 5d
    Commit 6). Phase 5d's tests only exercised OV; this commit
    pins DV and IV so the wrap rule's voice variation is exercised
    end-to-end with consonant-final pronouns."""

    def test_iv_bare_ipinaggawa(self) -> None:
        """``Lumakad ang bata namin na ipinaggawa.`` — IV-BEN
        (`ipag-` of `gawa`). Bare frame: no overt patient, no DAT
        adjunct."""
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata namin na ipinaggawa.", "SUBJ"
        )
        assert result is not None
        _, subj, _ = result
        adj = subj.feats["ADJ"]
        rcs = [m for m in adj if isinstance(m, FStructure)]
        assert any(rc.feats.get("VOICE") == "IV" for rc in rcs)

    def test_iv_with_dat_adjunct_ipinagsulat(self) -> None:
        """``Lumakad ang bata namin na ipinagsulat sa kapatid.`` —
        IV-BEN (`ipag-` of `sulat`) with a DAT adjunct
        (``sa kapatid``). Exercises the second S_GAP_NA IV rule
        ``[v_cat, NP[CASE=DAT]]``."""
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata namin na ipinagsulat sa kapatid.", "SUBJ"
        )
        assert result is not None
        _, subj, _ = result
        adj = subj.feats["ADJ"]
        rcs = [m for m in adj if isinstance(m, FStructure)]
        assert any(rc.feats.get("VOICE") == "IV" for rc in rcs)

    def test_dv_bare_binasahan(self) -> None:
        """``Lumakad ang bata namin na binasahan.`` — DV PFV of
        `basa` (the only DV form with full analyzer coverage in
        the seed lexicon). The S_GAP_NA DV frame is the same shape
        as OV: bare ``[v_cat]`` with the actor extracted as
        ``OBJ-AGENT`` and the head NP as the NOM-pivot SUBJ."""
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata namin na binasahan.", "SUBJ"
        )
        assert result is not None
        _, subj, _ = result
        adj = subj.feats["ADJ"]
        rcs = [m for m in adj if isinstance(m, FStructure)]
        assert any(rc.feats.get("VOICE") == "DV" for rc in rcs)


# === Consonant-final HEAD NP ==============================================


class TestPossessiveLinkerNaConsonantFinalHead:
    """The construction generalizes across head-noun shapes. With
    a consonant-final head (e.g., ``kapatid``) plus a consonant-
    final PRON, neither the head nor the PRON can take the bound
    ``-ng`` linker, so the standalone ``na`` linker is the only
    option. This is the surface that most clearly motivates the
    Commit 18 lift — there's no `-ng`-fused alternative."""

    def test_kapatid_namin(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Lumakad ang kapatid namin na binasa.", "SUBJ"
        )
        assert result is not None
        _, subj, poss = result
        assert subj.feats.get("LEMMA") == "kapatid"
        assert poss.feats.get("CASE") == "GEN"
        assert poss.feats.get("NUM") == "PL"
        assert poss.feats.get("CLUSV") == "EXCL"

    def test_kapatid_nila(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Lumakad ang kapatid nila na binasa.", "SUBJ"
        )
        assert result is not None
        _, subj, _ = result
        assert subj.feats.get("LEMMA") == "kapatid"


# === Negation under the construction ======================================


class TestPossessiveLinkerNaNegation:

    def test_negated_rc(self) -> None:
        # ``Lumakad ang bata namin na hindi binasa.`` — RC is
        # negated. The S_GAP_NA frame's NEG-recursion handles this
        # and the disambiguator's _next_content_is_verb skips
        # PART[POLARITY=NEG] when validating the post-PRON `na`
        # context.
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata namin na hindi binasa.", "SUBJ"
        )
        assert result is not None
        _, subj, _ = result
        adj = subj.feats["ADJ"]
        rcs = [m for m in adj if isinstance(m, FStructure)]
        assert rcs
        rc = rcs[0]
        assert rc.feats.get("POLARITY") == "NEG"


# === Vowel-final PRON + standalone `na` (also lifted) =====================


class TestVowelFinalPronStandaloneNa:
    """Vowel-final pronouns also admit the standalone-``na`` linker
    variant (in addition to the fused ``-ng`` form). Phase 5d
    Commit 6 only covered the fused form; the LINK=NA branch
    introduced in Commit 18 lifts ``aklat ko na kinain`` too —
    both linker variants carry the same f-equations."""

    def test_ko_with_standalone_na(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata ko na kinain.", "SUBJ"
        )
        assert result is not None
        _, subj, poss = result
        assert subj.feats.get("LEMMA") == "bata"
        assert poss.feats.get("CASE") == "GEN"
        assert poss.feats.get("NUM") == "SG"

    def test_mo_with_standalone_na(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata mo na kinain.", "SUBJ"
        )
        assert result is not None

    def test_niya_with_standalone_na(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata niya na kinain.", "SUBJ"
        )
        assert result is not None


# === Regressions ==========================================================


class TestPossessiveLinkerNaRegressions:

    def test_standard_pronominal_possessive_consonant_final(self) -> None:
        # ``Kumain ang bata ng libro namin.`` — standard pronominal
        # possessive (no RC). Must still produce a parse with
        # OBJ.POSS = namin's f-structure.
        rs = parse_text("Kumain ang bata ng libro namin.", n_best=10)
        assert rs
        found = False
        for _, f, _, _ in rs:
            obj = f.feats.get("OBJ")
            if not isinstance(obj, FStructure):
                continue
            if obj.feats.get("LEMMA") != "libro":
                continue
            poss = obj.feats.get("POSS")
            if (
                isinstance(poss, FStructure)
                and poss.feats.get("CASE") == "GEN"
                and poss.feats.get("NUM") == "PL"
            ):
                found = True
                break
        assert found

    def test_standard_na_relativization(self) -> None:
        # ``Tumakbo ang batang kumain ng isda.`` — standard SUBJ-
        # relativization with NOUN actor in the RC. The new wrap
        # rule should not interfere.
        rs = parse_text("Tumakbo ang batang kumain ng isda.", n_best=10)
        assert rs
        found = False
        for _, f, _, _ in rs:
            subj = f.feats.get("SUBJ")
            if not isinstance(subj, FStructure):
                continue
            adj = subj.feats.get("ADJ")
            if not adj:
                continue
            for m in adj:
                if (
                    isinstance(m, FStructure)
                    and m.feats.get("PRED") == "EAT <SUBJ, OBJ>"
                ):
                    found = True
                    break
            if found:
                break
        assert found

    def test_standard_na_relativization_with_overt_actor(self) -> None:
        """``Tumakbo ang bata na kinain ng aso.`` — RC with overt
        GEN actor (``ng aso``, not extracted). Must parse via the
        existing S_GAP wrap, NOT via the new S_GAP_NA wrap (which
        requires the GEN slot to be empty). Verify by finding a
        parse where the RC's OBJ-AGENT is ``aso`` (the NOUN), not
        a pronoun-shaped fstruct."""
        rs = parse_text("Tumakbo ang bata na kinain ng aso.", n_best=10)
        assert rs
        found = False
        for _, f, _, _ in rs:
            subj = f.feats.get("SUBJ")
            if not isinstance(subj, FStructure):
                continue
            adj = subj.feats.get("ADJ")
            if not adj:
                continue
            for m in adj:
                if not isinstance(m, FStructure):
                    continue
                if m.feats.get("PRED") != "EAT <SUBJ, OBJ-AGENT>":
                    continue
                oa = m.feats.get("OBJ-AGENT")
                if isinstance(oa, FStructure) and oa.feats.get("LEMMA") == "aso":
                    found = True
                    break
            if found:
                break
        assert found, "no parse with RC.OBJ-AGENT=aso (overt actor)"

    def test_phase5d_commit6_vowel_final_ng_unchanged(self) -> None:
        # Regression for the original Phase 5d Commit 6 form.
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata kong kinain.", "SUBJ"
        )
        assert result is not None
        _, subj, poss = result
        assert subj.feats.get("LEMMA") == "bata"
        assert poss.feats.get("NUM") == "SG"


# === Regression: POSS-EXTRACTED guard blocks hybrid parses ================


class TestPossessiveExtractedGuard:
    """The Phase 5e Commit 18 wrap rule marks its output with
    ``POSS-EXTRACTED=YES``; the standard NP-internal possessive
    rule has a ``¬ (↑ POSS-EXTRACTED)`` guard that blocks it from
    firing on such NPs. Without this guard, surfaces like ``bata
    ko na kinain ng aso`` produced a spurious parse where the
    NP-poss rule extended the wrap-rule output by binding
    ``ng aso`` as POSS, unifying it with the already-bound
    PRON POSS into a hybrid fstruct (``ko`` lacks LEMMA so
    ``aso``'s LEMMA wins; CASE=GEN matches; the hybrid is then
    also OBJ-AGENT via the dual binding). The guard rejects this
    NP-poss extension on wrap-rule outputs.

    These regressions cover both linker variants:
    """

    def test_na_form_no_hybrid_parse(self) -> None:
        """``Tumakbo ang bata ko na kinain ng aso.`` — NO parse
        should have POSS unifying ``ko`` (PRON) and ``aso`` (NOUN)
        into a hybrid fstruct."""
        rs = parse_text("Tumakbo ang bata ko na kinain ng aso.", n_best=15)
        assert rs
        for _, f, _, _ in rs:
            subj = f.feats.get("SUBJ")
            if not isinstance(subj, FStructure):
                continue
            poss = subj.feats.get("POSS")
            if not isinstance(poss, FStructure):
                continue
            # The hybrid parse had POSS.LEMMA == "aso" (from the
            # post-V GEN-NP) AND POSS.NUM == "SG" (from the PRON ko).
            # The legitimate parses have either no LEMMA on POSS (just
            # ko's PERS/NUM/CASE) or LEMMA but no POSS dual-binding to
            # OBJ-AGENT.
            adj = subj.feats.get("ADJ")
            if not adj:
                continue
            for m in adj:
                if not isinstance(m, FStructure):
                    continue
                oa = m.feats.get("OBJ-AGENT")
                if not (isinstance(oa, FStructure) and oa is poss):
                    continue
                # Found a parse where POSS = OBJ-AGENT (dual-binding).
                # That parse must NOT also have LEMMA=aso (which would
                # mean ko was unified with aso).
                assert poss.feats.get("LEMMA") != "aso", (
                    f"hybrid PRON-NOUN POSS detected: {poss.feats}"
                )

    def test_ng_form_no_hybrid_parse(self) -> None:
        """``Tumakbo ang bata kong kinain ng aso.`` — same regression
        for the original Phase 5d Commit 6 ``-ng`` linker form, which
        had the same latent bug before the Commit 18 guard."""
        rs = parse_text("Tumakbo ang bata kong kinain ng aso.", n_best=15)
        assert rs
        for _, f, _, _ in rs:
            subj = f.feats.get("SUBJ")
            if not isinstance(subj, FStructure):
                continue
            poss = subj.feats.get("POSS")
            if not isinstance(poss, FStructure):
                continue
            adj = subj.feats.get("ADJ")
            if not adj:
                continue
            for m in adj:
                if not isinstance(m, FStructure):
                    continue
                oa = m.feats.get("OBJ-AGENT")
                if not (isinstance(oa, FStructure) and oa is poss):
                    continue
                assert poss.feats.get("LEMMA") != "aso", (
                    f"hybrid PRON-NOUN POSS detected: {poss.feats}"
                )

    def test_intended_overt_actor_parse_still_present(self) -> None:
        """The legitimate parse (POSS=ko PRON, OBJ-AGENT=aso NOUN,
        distinct fstructs) must still be produced. The guard removes
        only the spurious hybrid, not the intended reading."""
        for text in (
            "Tumakbo ang bata ko na kinain ng aso.",
            "Tumakbo ang bata kong kinain ng aso.",
        ):
            rs = parse_text(text, n_best=15)
            assert rs, f"no parse for {text!r}"
            found = False
            for _, f, _, _ in rs:
                subj = f.feats.get("SUBJ")
                if not isinstance(subj, FStructure):
                    continue
                poss = subj.feats.get("POSS")
                adj = subj.feats.get("ADJ")
                if not (isinstance(poss, FStructure) and adj):
                    continue
                # Look for a parse with POSS=PRON (no LEMMA) AND
                # an RC whose OBJ-AGENT is the NOUN aso (distinct).
                for m in adj:
                    if not isinstance(m, FStructure):
                        continue
                    oa = m.feats.get("OBJ-AGENT")
                    if (
                        isinstance(oa, FStructure)
                        and oa.feats.get("LEMMA") == "aso"
                        and oa is not poss
                    ):
                        found = True
                        break
                if found:
                    break
            assert found, f"intended POSS=PRON, OBJ-AGENT=NOUN parse not found for {text!r}"

    def test_legitimate_iterated_possessive_unaffected(self) -> None:
        """The guard on the standard NP-poss rule must not block
        legitimate right-associative iterated possessives like
        ``libro ng bata ng pamilya`` (libro.POSS=bata,
        bata.POSS=pamilya). The standard NP-poss rule doesn't set
        POSS-EXTRACTED, so the guard fires only on dual-binding
        wrap-rule outputs."""
        rs = parse_text("Tumakbo ang libro ng bata ng pamilya.", n_best=10)
        assert rs
        found = False
        for _, f, _, _ in rs:
            subj = f.feats.get("SUBJ")
            if not isinstance(subj, FStructure):
                continue
            poss1 = subj.feats.get("POSS")
            if not isinstance(poss1, FStructure):
                continue
            poss2 = poss1.feats.get("POSS")
            if (
                isinstance(poss2, FStructure)
                and poss1.feats.get("LEMMA") == "bata"
                and poss2.feats.get("LEMMA") == "pamilya"
            ):
                found = True
                break
        assert found, "iterated possessive libro.POSS=bata.POSS=pamilya not produced"


# === LMT diagnostics ======================================================


class TestPossessiveLinkerNaLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Lumakad ang bata namin na binasa.",
            "Lumakad ang bata natin na binasa.",
            "Lumakad ang bata ninyo na binasa.",
            "Lumakad ang bata nila na binasa.",
            "Lumakad ang bata ko na kinain.",
            "Kumain ang bata ng libro namin na binasa.",
            "Lumakad ang bata namin na hindi binasa.",
        ):
            rs = parse_text(s, n_best=10)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
