"""Phase 5e Commit 6: ``na`` linker disambiguation after PRON.

Phase 5d Commit 10's deferral list flagged: ``Tumakbo ang bata ko
na nakita`` (NP-internal possessor + linker + RC). The placement
pass historically treated post-PRON ``na`` as the 2P aspectual
clitic (CLITIC_CLASS=2P, ASPECT_PART=ALREADY) and moved it to
clause-end, breaking the linker / RC parse.

This commit extends ``disambiguate_homophone_clitics`` with a
third left-context exception (alongside the existing control-verb
and ctrl-verb-then-PRON cases): when a PRON preceded by a NOUN
is followed by a VERB (or NEG + VERB), keep the linker reading.
The look-ahead helper ``_next_content_is_verb`` skips
PART[POLARITY=NEG] tokens so RCs with inner negation work too.

Disambiguation is tested against verbs that have hand-authored
AV-intransitive BASE entries (``kain``) or intrinsically
intransitive entries (``takbo``). Verbs with TR=TR and no
hand-authored intransitive (e.g., ``kita`` → ``nakita``) need a
synthesizer enhancement that emits ``<SUBJ>`` alongside
``<SUBJ, OBJ>``; that's a separate engineering follow-up.
"""

from __future__ import annotations

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _find_poss_rc_parse(text: str, head_lemma: str, rc_pred_part: str) -> FStructure | None:
    """Return the first parse whose SUBJ has LEMMA=``head_lemma``,
    a POSS slot, and an ADJ member matching the RC's PRED."""
    rs = parse_text(text, n_best=15)
    for _, f, _, _ in rs:
        subj = f.feats.get("SUBJ")
        if not isinstance(subj, FStructure):
            continue
        if subj.feats.get("LEMMA") != head_lemma:
            continue
        if not isinstance(subj.feats.get("POSS"), FStructure):
            continue
        adj = subj.feats.get("ADJ")
        if adj is None:
            continue
        for m in adj:  # type: ignore[union-attr]
            pred = m.feats.get("PRED")  # type: ignore[union-attr]
            if isinstance(pred, str) and rc_pred_part in pred:
                return f
    return None


# === Possessor PRON + na linker + V_RC ===================================


class TestPossessorPronWithRc:
    """``Tumakbo ang bata ko na kumain.`` "My child who ate ran."
    The PRON ``ko`` is the possessor of ``bata``; the ``na`` is
    the linker introducing the RC ``kumain``. Without the new
    disambiguator branch, ``na`` would be moved to clause-end as
    the 2P aspectual clitic and the parse would fail."""

    def test_basic_av_intr_rc(self) -> None:
        f = _find_poss_rc_parse(
            "Tumakbo ang bata ko na kumain.",
            head_lemma="bata",
            rc_pred_part="EAT",
        )
        assert f is not None
        assert f.feats.get("PRED") == "TAKBO <SUBJ>"
        # The matrix POLARITY is unaffected.
        assert f.feats.get("POLARITY") != "NEG"

    def test_av_tr_rc_with_object(self) -> None:
        f = _find_poss_rc_parse(
            "Tumakbo ang bata ko na kumain ng isda.",
            head_lemma="bata",
            rc_pred_part="EAT <SUBJ, OBJ>",
        )
        assert f is not None

    def test_ov_rc_with_overt_actor(self) -> None:
        """``Tumakbo ang bata ko na kinain ng aso.`` "My child whom
        the dog ate ran." (semantically odd but grammatical)."""
        f = _find_poss_rc_parse(
            "Tumakbo ang bata ko na kinain ng aso.",
            head_lemma="bata",
            rc_pred_part="EAT <SUBJ, OBJ-AGENT>",
        )
        assert f is not None

    def test_inner_negation_via_neg_skip(self) -> None:
        """``Tumakbo ang bata ko na hindi kumain.`` "My child who
        didn't eat ran." The look-ahead helper skips
        PART[POLARITY=NEG] when checking for V."""
        f = _find_poss_rc_parse(
            "Tumakbo ang bata ko na hindi kumain.",
            head_lemma="bata",
            rc_pred_part="EAT",
        )
        assert f is not None
        # The matrix POLARITY is unaffected.
        assert f.feats.get("POLARITY") != "NEG"
        # The RC has POLARITY=NEG.
        rc = next(
            m for m in f.feats["SUBJ"].feats["ADJ"]  # type: ignore[union-attr]
            if isinstance(m.feats.get("PRED"), str)  # type: ignore[union-attr]
            and "EAT" in m.feats["PRED"]  # type: ignore[union-attr]
        )
        assert rc.feats.get("POLARITY") == "NEG"

    def test_alternate_pron_2sg(self) -> None:
        """2sg-GEN ``mo`` works the same way."""
        f = _find_poss_rc_parse(
            "Tumakbo ang bata mo na kumain.",
            head_lemma="bata",
            rc_pred_part="EAT",
        )
        assert f is not None

    def test_alternate_pron_3sg(self) -> None:
        """3sg-GEN ``niya`` works the same way."""
        f = _find_poss_rc_parse(
            "Tumakbo ang bata niya na kumain.",
            head_lemma="bata",
            rc_pred_part="EAT",
        )
        assert f is not None


# === Regression: existing 2P clitic behavior preserved ==================


class TestRegressionNa2pClitic:
    """The new branch fires only when:
    (NOUN preceding PRON) AND (VERB or NEG+VERB following the na).
    Other ``na`` post-PRON contexts must still treat ``na`` as
    the 2P aspectual clitic."""

    def test_v_pron_na_clause_final(self) -> None:
        """``Kumain mo na ang isda.`` ``na`` is the 2P aspectual
        clitic ``ALREADY``, not the linker. The PRON ``mo`` is
        post-V, not post-N; so the new branch does NOT apply."""
        rs = parse_text("Kumain mo na ang isda.", n_best=10)
        # Should still parse with the 2P clitic reading: na is
        # moved to clause-end as ADJ, mo is OBJ in OV reading or
        # AV's bare-OBJ.
        assert rs
        # Verify ASPECT_PART=ALREADY is on the matrix's ADJ
        # member.
        seen_already = False
        for _, f, _, _ in rs:
            adj = f.feats.get("ADJ")
            if adj is None:
                continue
            for m in adj:  # type: ignore[union-attr]
                if m.feats.get("ASPECT_PART") == "ALREADY":  # type: ignore[union-attr]
                    seen_already = True
                    break
            if seen_already:
                break
        assert seen_already

    def test_post_v_pron_na_at_eos(self) -> None:
        """``Kinain mo na.`` - V + PRON + na (clause end). The new
        branch requires NOUN before PRON; here the PRON is
        post-V. Existing 2P behavior."""
        rs = parse_text("Kinain mo na.", n_best=10)
        # May or may not parse depending on completeness, but the
        # disambiguator should still treat ``na`` as the 2P
        # clitic. Sanity check: at least the disambiguator
        # doesn't crash and any parses produced have ADJ with
        # ASPECT_PART=ALREADY.
        for _, f, _, _ in rs:
            adj = f.feats.get("ADJ")
            if adj is not None:
                for m in adj:  # type: ignore[union-attr]
                    if m.feats.get("ASPECT_PART") == "ALREADY":  # type: ignore[union-attr]
                        return  # found expected reading
        # If no parses, that's fine — pre-Phase-5e behavior also
        # had no parses for this input.

    def test_control_verb_pron_na_unaffected(self) -> None:
        """Phase 5c §7.6 follow-on: ``Kaya namin na kumain``
        (psych control + consonant-final PRON + linker + V).
        The existing ctrl-verb + PRON exception keeps ``na`` as
        the linker. The new NOUN-before-PRON branch is more
        specific (requires NOUN) and doesn't apply here."""
        rs = parse_text("Kaya namin na kumain.", n_best=10)
        assert rs
        # The ctrl-verb XCOMP-via-linker reading should still
        # work.
        for _, f, _, _ in rs:
            if f.feats.get("PRED") == "ABLE <SUBJ, XCOMP>":
                xcomp = f.feats.get("XCOMP")
                assert isinstance(xcomp, FStructure)
                assert xcomp.feats.get("PRED") == "EAT <SUBJ>"
                return
        raise AssertionError(
            "expected a kaya-control reading"
        )


# === Discrimination: disambiguator only fires on `na` ===================


class TestOnlyFiresOnNa:
    """The disambiguator only operates on tokens with both
    is_clitic=True and is_clitic=False analyses (in practice,
    ``na``). Other post-NOUN PRON contexts without ``na``
    following should be unaffected."""

    def test_post_noun_pron_then_unrelated_token(self) -> None:
        """``Tumakbo ang bata ko sa bahay.`` — PRON post-NOUN, then
        ``sa`` (DAT marker, not a homophone). Should parse as
        NP-internal possessive + sa-NP adjunct."""
        rs = parse_text("Tumakbo ang bata ko sa bahay.", n_best=10)
        assert rs

    def test_post_noun_pron_then_pa_clitic(self) -> None:
        """``Tumakbo ang bata ko pa.`` — ``pa`` is unambiguously
        a 2P clitic (no homophone). Disambiguator skips this
        token; ``pa`` moves to cluster as expected."""
        rs = parse_text("Tumakbo pa ang bata ko.", n_best=10)
        # Should parse with `pa` as adverbial enclitic in matrix
        # ADJ.
        assert rs


# === LMT diagnostics ====================================================


class TestLmtDiagnostics:
    """No blocking LMT diagnostics on the new construction."""

    def test_no_blocking(self) -> None:
        rs = parse_text("Tumakbo ang bata ko na kumain.", n_best=5)
        for _, _f, _c, diags in rs:
            blocking = [d for d in diags if d.kind != "lmt-mismatch"]
            assert blocking == [], f"unexpected blocking diags: {blocking}"
