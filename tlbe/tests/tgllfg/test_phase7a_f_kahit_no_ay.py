# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 7a.F: kahit-X SUBJ pre-V no-`ay` colloquial (§18.1.1 item 8).

New rule in ``cfg/extraction.py`` (parallel to the Phase 4 §7.4
ay-fronted rule):

    S → NP[CASE=NOM] S_GAP
       (↑) = ↓2
       (↑ TOPIC) = ↓1
       (↓2 REL-PRO) = ↓1
       (↓2 REL-PRO) =c (↓2 SUBJ)
       (↓1 INDEF) =c 'YES'
       (↑ REGISTER) = 'COLLOQUIAL'

Closes the no-``ay`` colloquial variant of pre-V kahit-X SUBJ
fronting (Phase 5n.B C20 closed the canonical ``ay``-fronted
form). Gated to INDEF=YES NPs (set compositionally by the
Phase 5m C8 IndefPRON rule on kahit-X constructions); REGISTER=
COLLOQUIAL distinguishes Phase 7a.F parses from the formal
ay-fronted variant.
"""

import pytest

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


# === Test inventory ====================================================

KAHIT_SUBJ_INVENTORY = [
    # (sentence, subj_lemma)
    ("Kahit sino kumain.",            "sino"),
    ("Kahit ano kumain.",             "ano"),
    ("Kahit alin kumain.",            "alin"),
    ("Kahit sino kumakain.",          "sino"),  # AV-IPFV embedded
    ("Kahit sino bumili ng aklat.",   "sino"),  # AV-trans embedded
]


# === Colloquial no-ay form parses ====================================


class TestKahitNoAyColloquial:
    """The new rule produces 1+ parse for each kahit-X + AV-V
    surface, with REGISTER=COLLOQUIAL and TOPIC bound to the
    fronted kahit-X NP."""

    @pytest.mark.parametrize(
        "sentence,subj_lemma",
        KAHIT_SUBJ_INVENTORY,
    )
    def test_parses_with_colloquial_register(
        self, sentence: str, subj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert parses, f"{sentence!r} should parse"
        colloquial = [
            p for p in parses
            if p[1].feats.get("REGISTER") == "COLLOQUIAL"
        ]
        assert colloquial, (
            f"{sentence!r} should have a REGISTER=COLLOQUIAL parse"
        )

    @pytest.mark.parametrize(
        "sentence,subj_lemma",
        KAHIT_SUBJ_INVENTORY,
    )
    def test_topic_bound_to_kahit_np(
        self, sentence: str, subj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        colloquial = [
            p for p in parses
            if p[1].feats.get("REGISTER") == "COLLOQUIAL"
        ]
        assert colloquial
        fs = colloquial[0][1]
        topic = fs.feats.get("TOPIC")
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == subj_lemma, (
            f"{sentence!r}: TOPIC.LEMMA should be {subj_lemma!r}"
        )
        assert topic.feats.get("INDEF") == "YES"


# === ay-fronted form regression ======================================


class TestAyFrontedFormUnaffected:
    """The Phase 5n.B C20 ay-fronted form still parses without
    the REGISTER=COLLOQUIAL tag (formal register)."""

    @pytest.mark.parametrize(
        "sentence",
        [
            "Kahit sino ay kumain.",
            "Kahit ano ay kumain.",
            "Kahit alin ay kumain.",
        ],
    )
    def test_ay_form_still_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert parses, (
            f"Phase 5n.B C20 ay-fronted form {sentence!r} should "
            f"still parse"
        )
        formal = [
            p for p in parses
            if p[1].feats.get("REGISTER") != "COLLOQUIAL"
        ]
        assert formal, (
            f"{sentence!r} should have at least one formal "
            f"(non-COLLOQUIAL) parse"
        )


# === Post-V SUBJ regression (Phase 5m) =================================


class TestPostVSubjUnaffected:
    """The Phase 5m C8 post-V SUBJ form (`Kumain kahit sino.`)
    is unaffected by the new pre-V rule."""

    def test_post_v_subj(self) -> None:
        parses = parse_text("Kumain kahit sino.")
        assert parses, "Phase 5m post-V kahit-X SUBJ should still parse"
        fs = parses[0][1]
        subj = fs.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "sino"
        assert subj.feats.get("INDEF") == "YES"


# === Negative regression: bare NP (non-INDEF) doesn't front ============


class TestBareNPDoesNotFront:
    """The new rule is gated on INDEF=YES, so bare NPs (e.g.,
    `Si Maria kumain.` without `ay`) should NOT parse via this
    rule. Test that the gating works — only kahit-X (and other
    INDEF=YES) NPs license the colloquial fronting."""

    def test_bare_proper_noun_no_front(self) -> None:
        # `Si Maria kumain.` — proper noun, no ay, no kahit.
        # The matrix INDEF feat is not YES; new rule should not
        # fire.
        parses = parse_text("Si Maria kumain.")
        # If this surface parses via SOME other rule, that's
        # fine; what matters is that it doesn't parse via
        # COLLOQUIAL Phase 7a.F.
        colloquial = [
            p for p in parses
            if p[1].feats.get("REGISTER") == "COLLOQUIAL"
        ]
        assert not colloquial, (
            "Bare proper-noun pre-V SUBJ should NOT trigger the "
            "Phase 7a.F COLLOQUIAL rule (INDEF=YES gate)"
        )
