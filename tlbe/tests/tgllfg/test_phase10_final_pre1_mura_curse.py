# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.final.pre-1 — curse-root ``mura`` smoke.

Closes the conditional 10.final.pre-1 plan row by adding (and
verifying) two new lexical entries:

  - ``mura`` (NOUN, ``nouns.yaml``) — "profanity, curse word".
  - ``mura`` (VERB, ``verbs.yaml``) — "to curse, swear at" — under
    affix_class ``[mag, in_oblig, pag_gerund]``.

The 10.H.post-1 retraction of the curse-VERB is reversed by the
2026-06-03 multi-speaker native-informant panel (Tagalog + Waray
speakers + a linguist/language engineer), who confirmed both AV
(mag-) and OV (-in/-hin) paradigms plus the ``pagmumura`` gerund.

The existing ADJ ``mura`` "cheap, young/tender" in
``adjectives.yaml`` is intentionally unchanged — it is a
semantically unrelated homophonous root (per the expert
recommendation: mura₁ ADJ-CHEAP vs mura₂ N/V root-CURSE). POS-level
disambiguation keeps the three lex entries cleanly separated; no
surface-string collision arises because the ADJ's ``adj_redup``
``mura-mura`` ("rather cheap") and the curse paradigm's inflected
forms occupy disjoint surface namespaces (the curse paradigm
always carries verbal affixation or pag- gerund prefixation).
"""

import pytest

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import Analyzer
from tgllfg.text.tokenizer import Token


@pytest.fixture(scope="module")
def analyzer() -> Analyzer:
    return Analyzer.from_default()


def _analyze(analyzer: Analyzer, surface: str) -> list:
    """Helper: feed a single surface through the morph analyzer."""
    tok = Token(surface=surface, norm=surface.lower(), start=0, end=len(surface))
    return analyzer.analyze_one(tok)


# === VERB paradigm — affix_class [mag, in_oblig, pag_gerund] ============


class TestMuraCurseVerbParadigm:
    """All 8 inflected VERB surfaces (4 AV mag- + 4 OV -in) listed
    in the informant paradigm resolve to lemma=mura with POS=VERB
    and the expected voice/aspect signature.

    AV (mag class):  magmura / nagmura / nagmumura / magmumura
    OV (-in class):  murahin / minura / minumura / mumurahin
    """

    @pytest.mark.parametrize("surface,voice,aspect", [
        # AV mag- class
        ("magmura",    "AV", "CTPL"),
        ("nagmura",    "AV", "PFV"),
        ("nagmumura",  "AV", "IPFV"),
        ("magmumura",  "AV", "CTPL"),
        # OV -in/-hin class
        ("murahin",    "OV", "CTPL"),
        ("minura",     "OV", "PFV"),
        ("minumura",   "OV", "IPFV"),
        ("mumurahin",  "OV", "CTPL"),
    ])
    def test_curse_verb_surface_resolves(
        self, analyzer: Analyzer,
        surface: str, voice: str, aspect: str,
    ) -> None:
        out = _analyze(analyzer, surface)
        verb_matches = [
            a for a in out
            if a.lemma == "mura" and a.pos == "VERB"
            and a.feats.get("VOICE") == voice
        ]
        assert verb_matches, (
            f"{surface}: no VERB analysis to mura with voice={voice}; "
            f"got: {[(a.lemma, a.pos, a.feats.get('VOICE'), a.feats.get('ASPECT')) for a in out]}"
        )
        # At least one of the voice-matching analyses must carry
        # the expected aspect (paradigm cells can produce multiple
        # aspect-tagged variants for the same surface).
        aspect_matches = [a for a in verb_matches if a.feats.get("ASPECT") == aspect]
        assert aspect_matches, (
            f"{surface}: VERB analyses found but none carry aspect={aspect}; "
            f"got aspects: {sorted({a.feats.get('ASPECT') for a in verb_matches})}"
        )


# === pag- gerund (deverbal nominalization) ==============================


class TestMuraCurseGerund:
    """``pag_gerund`` opt-in produces ``pagmura`` (PFV) +
    ``pagmumura`` (IPFV / C-initial intensive) as nominalized
    deverbals — the informant explicitly cited ``pagmumura``
    "swearing, cursing" as a related verbal-noun form."""

    @pytest.mark.parametrize("surface", ["pagmura", "pagmumura"])
    def test_gerund_is_nominalized_noun(
        self, analyzer: Analyzer, surface: str,
    ) -> None:
        out = _analyze(analyzer, surface)
        gerund_matches = [
            a for a in out
            if a.lemma == "mura" and a.pos == "NOUN"
            and a.feats.get("NOMINALIZED") is True
        ]
        assert gerund_matches, (
            f"{surface}: no nominalized-NOUN analysis to mura; "
            f"got: {[(a.lemma, a.pos, a.feats.get('NOMINALIZED')) for a in out]}"
        )


# === NOUN sense — bare ``mura`` ========================================


class TestMuraCurseNounSurface:
    """Bare ``mura`` resolves to AT LEAST one NOUN analysis with
    lemma=mura (the new curse-NOUN entry). Coexists with the
    existing ADJ analysis; both are licit."""

    def test_bare_mura_yields_noun(self, analyzer: Analyzer) -> None:
        out = _analyze(analyzer, "mura")
        noun_matches = [a for a in out if a.lemma == "mura" and a.pos == "NOUN"]
        assert noun_matches, (
            "bare `mura`: no NOUN analysis to lemma=mura; "
            f"got: {[(a.lemma, a.pos) for a in out]}"
        )

    def test_bare_mura_also_yields_adj(self, analyzer: Analyzer) -> None:
        """Regression sentry — the curse-NOUN add does NOT displace
        the existing ADJ ``mura`` "cheap" entry. Both surface."""
        out = _analyze(analyzer, "mura")
        adj_matches = [a for a in out if a.lemma == "mura" and a.pos == "ADJ"]
        assert adj_matches, (
            "bare `mura`: ADJ analysis missing — the curse add "
            "must NOT displace the existing ADJ entry; "
            f"got: {[(a.lemma, a.pos) for a in out]}"
        )


# === End-to-end parses — user-listed curse-sense sentences ==============


class TestMuraCurseSentenceParses:
    """The four sentence examples from the 2026-06-03 informant
    summary parse end-to-end via the lex+chart pipeline."""

    @pytest.mark.parametrize("sentence,note", [
        # NOUN — curse-sense
        ("Masama ang kanyang mga mura.",
         "His/her profanities are offensive."),
        ("Narinig ko ang kanyang mura.",
         "I heard his/her curse."),
        # VERB — OV PFV with NOM pronoun pivot
        ("Minura niya ako.",
         "He/she cursed at me."),
        # VERB — AV negated imperative (huwag + clitic + INF)
        ("Huwag kang magmura.",
         "Don't swear."),
    ])
    def test_curse_sentence_parses(self, sentence: str, note: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"no parse for: {sentence!r} (informant gloss: {note!r})"
        )


# === ADJ regression — existing "cheap" parses unchanged =================


class TestMuraAdjSentencesUnchanged:
    """The scalar-ADJ examples from the informant summary continue
    to parse, confirming the curse adds don't break the ADJ path.
    These are the canonical-Tagalog scalar-ADJ uses that 10.H.post-1
    captured (S&O 1972 contrast with ``mahal``)."""

    @pytest.mark.parametrize("sentence", [
        "Mura ang isda ngayon.",
    ])
    def test_adj_sentence_still_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, f"no parse for ADJ-sense sentence: {sentence!r}"


# === Disambiguation sentry — POS-level separation =======================


class TestMuraHomophoneSeparation:
    """The three lex entries (ADJ-CHEAP, NOUN-CURSE, VERB-CURSE)
    share lemma=mura but are distinguished at the POS level. The
    morph index returns ADJ + NOUN entries for the bare surface
    (the VERB root surfaces only inflected, so it does not appear
    here — which is the correct paradigm-class behavior)."""

    def test_bare_mura_yields_distinct_pos_set(self, analyzer: Analyzer) -> None:
        out = _analyze(analyzer, "mura")
        mura_analyses = [a for a in out if a.lemma == "mura"]
        pos_set = {a.pos for a in mura_analyses}
        # Bare-surface set must include both ADJ and NOUN; VERB
        # surfaces only inflected so it is correctly absent here.
        assert "ADJ" in pos_set, f"bare `mura`: ADJ missing — got POS={pos_set}"
        assert "NOUN" in pos_set, f"bare `mura`: NOUN missing — got POS={pos_set}"

    def test_inflected_curse_surfaces_do_not_polyparse_as_adj(
        self, analyzer: Analyzer,
    ) -> None:
        """Curse-paradigm surfaces (``magmura`` / ``minura`` /
        ``murahin`` etc.) must NOT also surface as ADJ-redup forms.
        The ADJ's ``adj_redup`` only produces ``mura-mura`` (hyphen-
        joined redup); the curse paradigm's affix-prefixed /
        suffixed forms do not collide."""
        for surface in ("magmura", "minura", "murahin", "nagmumura"):
            out = _analyze(analyzer, surface)
            adj_matches = [a for a in out if a.lemma == "mura" and a.pos == "ADJ"]
            assert not adj_matches, (
                f"{surface}: unexpected ADJ analysis to lemma=mura; "
                f"got: {[(a.lemma, a.pos, a.feats.get('VOICE')) for a in out if a.lemma == 'mura']}"
            )


# === Companion-fix sentence smoke (anti-deferral closures) ==============


class TestHuwagAddresseeAdjPred:
    """Phase 10.final.pre-1 Variant A — huwag-imperative with
    explicit addressee NOM-PRON + linker + predicative ADJ.
    Closes the surface variant ``Huwag kang ADJ.`` that surfaced
    while testing the curse-`mura` paradigm (``Huwag kang
    malungkot.`` "Don't be sad.")."""

    @pytest.mark.parametrize("sentence,note", [
        ("Huwag kang malungkot.", "huwag + ka-ng + malungkot (sad)"),
        ("Huwag kang masama.",     "huwag + ka-ng + masama (bad/evil)"),
        ("Huwag kang takot.",      "huwag + ka-ng + takot (afraid) — new lex"),
        ("Huwag kang mura.",       "huwag + ka-ng + mura (cheap polysemy; "
                                   "ADJ-PRED reading)"),
    ])
    def test_huwag_adj_pred_parses(self, sentence: str, note: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, f"no parse for: {sentence!r} ({note})"


class TestHuwagOvImperative:
    """Phase 10.final.pre-1 Variant B — huwag-imperative with
    GEN-actor + linker + inner S (OV/DV/IV head). Closes the
    negated-OV-imperative shape ``Huwag mong murahin si X.``
    that surfaces as the negation of the positive OV imperative
    ``Murahin mo siya.``."""

    @pytest.mark.parametrize("sentence,note", [
        ("Huwag mong murahin si Maria.",
         "huwag + mo-ng + OV `Don't curse Maria.`"),
        ("Huwag mong kainin iyan.",
         "huwag + mo-ng + OV `Don't eat that.` (canonical DEM)"),
        ("Huwag mong kainin yan.",
         "huwag + mo-ng + OV `Don't eat that.` (colloquial yan — "
         "new lex entry orthovariant)"),
    ])
    def test_huwag_ov_imperative_parses(self, sentence: str, note: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, f"no parse for: {sentence!r} ({note})"

    def test_positive_ov_imperative_still_parses(self) -> None:
        """Regression sentry — the new huwag-wrap rule does NOT
        displace the existing positive OV imperative shape
        ``Murahin mo siya.``."""
        parses = parse_text("Murahin mo siya.")
        assert len(parses) >= 1


class TestBawalModalPredicate:
    """Phase 10.final.pre-1 lex add — ``bawal`` "forbidden,
    prohibited" as a bare-predicative ADJ. ``Bawal ang mura.``
    "Cursing is forbidden." was the example cited in the original
    10.final.pre-1 plan row for the curse-NOUN sense; this test
    confirms both the lex add lands and the predicative-ADJ +
    NOM-NP composition works end-to-end."""

    @pytest.mark.parametrize("sentence", [
        "Bawal ang mura.",          # bare curse-NOUN as SUBJ
        "Bawal ang pagmumura.",     # gerund NOUN as SUBJ
        "Bawal ang aklat.",         # any-NOUN smoke
    ])
    def test_bawal_predicate_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, f"no parse for: {sentence!r}"


class TestNarinigComplementClause:
    """Phase 10.final.pre-1 lex update — ``dinig`` flipped to
    ``transitivity: TR`` + ``feats: {AV_ABSOL: true}`` mirroring
    the parallel ``kita`` "see" entry. Closes the GEN-perceiver +
    NOM-perceived ma-perception shape that the informant's
    ``Narinig ko ang kanyang mura.`` requires. The audit-corpus
    bonus closure ``Narinig kong darating si Pedro sa Sabado.``
    (wave5-zamar2023 page-55/sent-1) uses the same construction
    with a complement-clause perceived object."""

    @pytest.mark.parametrize("sentence", [
        "Narinig ko siya.",                              # simple
        "Narinig ko ang sigaw.",                         # NOM-NP
        "Narinig kong darating si Pedro sa Sabado.",     # +S_XCOMP (audit closure)
    ])
    def test_narinig_two_arg_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, f"no parse for: {sentence!r}"
