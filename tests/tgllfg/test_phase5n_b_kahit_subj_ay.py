# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.B Commit 20: pre-V kahit-X SUBJ ay-fronted (§18 L100).

Closes §18.1 deferral L100. Target sentences:

    Kahit sino ay kumain.    "Anyone ate."
    Kahit ano ay kumain.     "Anything ate."
    Kahit alin ay kumain.    "Whichever (one) ate."

This commit is **tests-only — no grammar changes**. The closure
emerges from composition of existing infrastructure:

  * Phase 5m Commit 8 IndefPRON rule
    (``PRON → PART[LEMMA=kahit] PRON[WH=YES]``) builds an
    indefinite ``kahit + wh-PRON`` PRON with feats
    ``INDEF=YES``, ``WH=YES``, ``LEMMA={sino,ano,alin}``,
    ``ADJUNCT={kahit CONC}``.

  * The standard ``NP[CASE=NOM] → PRON[CASE=NOM]`` shell wraps
    it as a NOM-NP.

  * The Phase 4 ay-fronting rule
    (``S → NP[CASE=NOM] PART[ay] S_GAP``) admits any NOM-NP as
    fronted SUBJ.

The three rules compose without modification — ``Kahit sino ay
kumain.`` already parses with the correct f-structure
(SUBJ={LEMMA=sino, INDEF=YES, WH=YES, CASE=NOM,
ADJUNCT={kahit}}). No new rule is needed.

Per plan-of-record §4.2 Commit 20: "indef-PRON-as-fronted-topic
rule" is one path to close L100; the existing composition is
equivalent and avoids adding a parallel rule that would create
ambiguity. The non-``ay`` form (``Kahit sino kumain.``) remains
deferred per §18.2 line 100 — closure path is via the
canonical ``ay``-form, validated here.

Out of scope: ``kahit saan`` / ``kahit kailan`` ay-fronted —
these are wh-ADVs (LOCATION/TIME), not PRONs, and aren't
SUBJ-eligible in Tagalog. Their ay-fronted use would be an
ADJUNCT-fronting construction (a separate analytical commitment;
not pinned by L100). Phase 5n.B C19 closed the clause-final
ADJUNCT use of those forms.
"""

import pytest

from tgllfg.core.pipeline import parse_text


# === Each kahit-PRON × ay-fronted SUBJ ================================


class TestKahitPronAyFronted:
    """Each kahit + wh-PRON ay-fronted form parses with the
    correct SUBJ semantics."""

    @pytest.mark.parametrize("sentence,subj_lemma", [
        ("Kahit sino ay kumain.",   "sino"),
        ("Kahit ano ay kumain.",    "ano"),
        ("Kahit alin ay kumain.",   "alin"),
        ("Kahit sino ay tumakbo.",  "sino"),
        ("Kahit sino ay pumunta.",  "sino"),
    ])
    def test_kahit_pron_ay_fronted(
        self, sentence: str, subj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma
        assert subj.feats.get("INDEF") == "YES"
        assert subj.feats.get("WH") is True
        assert subj.feats.get("CASE") == "NOM"
        # The kahit particle rides as ADJUNCT inside the SUBJ.
        adj = subj.feats.get("ADJUNCT")
        assert adj is not None
        assert any(
            getattr(m, "feats", {}).get("LEMMA") == "kahit"
            and getattr(m, "feats", {}).get("COMP_TYPE") == "CONC"
            for m in adj
        )


# === Transitive V regression ==========================================


class TestKahitWithTransitiveV:
    """The kahit-X SUBJ composition works with transitive verbs
    too — ay-fronting doesn't constrain on verb arity."""

    def test_kahit_ano_with_obj(self) -> None:
        # ``Kahit ano ay nakakain ng bata.`` lit. "anything ay-is-
        # eaten by-the-child"
        parses = parse_text("Kahit ano ay nakakain ng bata.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "ano"
        assert subj.feats.get("INDEF") == "YES"


# === Non-ay form remains deferred =====================================


class TestNonAyFormParsesColloquial:
    """The non-``ay`` form (``Kahit sino kumain.``) was deferred
    by Phase 5n.B C20 — closure path expected via the canonical
    ``ay``-form.

    **Phase 7a.F closure (2026-05-14):** the non-``ay`` form is
    now admitted via a new rule
    (``S → NP[CASE=NOM] S_GAP`` gated on ``INDEF=YES``) with
    explicit ``REGISTER='COLLOQUIAL'`` tagging on the matrix —
    downstream consumers can filter colloquial parses. The
    canonical ``ay``-fronted form still parses without the
    REGISTER tag (formal register).
    """

    @pytest.mark.parametrize("sentence", [
        "Kahit sino kumain.",
        "Kahit ano kumain.",
        "Kahit alin kumain.",
    ])
    def test_non_ay_form_parses_colloquial(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert parses, (
            f"{sentence!r} should parse via Phase 7a.F kahit-X "
            f"no-ay colloquial rule"
        )
        colloquial = [
            p for p in parses
            if p[1].feats.get("REGISTER") == "COLLOQUIAL"
        ]
        assert colloquial, (
            f"{sentence!r} should produce at least one parse with "
            f"REGISTER=COLLOQUIAL (the Phase 7a.F no-ay variant)"
        )


# === Phase 5m C8 IndefPRON regression =================================


class TestPhase5mIndefPronUnchanged:
    """The Phase 5m C8 IndefPRON rule continues to fire as
    expected — kahit-X works in canonical post-V SUBJ position
    too (not just ay-fronted)."""

    def test_kahit_sino_post_v_subj(self) -> None:
        # ``Kumain kahit sino.`` — post-V SUBJ
        parses = parse_text("Kumain kahit sino.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "sino"
        assert subj.feats.get("INDEF") == "YES"
