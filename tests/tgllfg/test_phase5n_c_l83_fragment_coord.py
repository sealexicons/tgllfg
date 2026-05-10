"""Phase 5n.C Commit 5 — L83 standalone NP-coord fragment.

Closes §18 L83 (standalone NP-coord without verbal head). The new
rule in ``cfg/clause.py`` admits ``Si Maria, hindi si Juan.`` (the
bare asymmetric-coord-NP fragment, with no verb) as a complete
matrix S marked with ``CLAUSE_TYPE=FRAGMENT`` and a synthetic
``PRED='NP-FRAG <SUBJ>'`` predicate over the asymmetric coord-NP.

Daughter pattern is restricted to ``NP[CASE=NOM, COORD=BUT_NOT]``.
``COORD=BUT_NOT`` is set only by Phase 5k Commit 8's asymmetric
NP-coord rule (sole producer in the grammar), so the L83 rule
serves as a structural discriminator without a new feat. Bare
singular NPs (``Si Maria.``), AND-coord NPs (``Si Maria at si
Juan.``), and OR-coord NPs (``Si Maria o si Juan.``) do not match
and continue to 0-parse as sentences.

Design appendix: ``docs/analysis-choices.md`` Phase 5n.C Commit 4.
Reference: Schachter & Otanes 1972 §10.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Fragment-S parses for asymmetric coord-NP =========================


class TestFragmentSParses:
    """``Si Maria, hindi si Juan.`` and similar asymmetric-coord-NP
    fragments parse as complete matrix S with CLAUSE_TYPE=FRAGMENT."""

    @pytest.mark.parametrize("sentence,first,second", [
        ("Si Maria, hindi si Juan.", "maria", "juan"),
        ("Si Pedro, hindi si Lola.", "pedro", "lola"),
        ("Si Juan, hindi si Maria.", "juan", "maria"),
    ])
    def test_canonical_fragment(
        self, sentence: str, first: str, second: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"L83 fragment-S should parse: {sentence!r}"
        )
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("CLAUSE_TYPE") == "FRAGMENT"
        assert fs.feats.get("PRED") == "NP-FRAG <SUBJ>"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "BUT_NOT"
        assert subj.feats.get("CASE") == "NOM"
        # Conjunct lemmas — the asymmetric coord stores both in
        # CONJUNCTS, with the second carrying POLARITY=NEG.
        conjuncts = subj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        lemmas = {c.feats.get("LEMMA") for c in conjuncts}
        assert lemmas == {first, second}


# === Bare singular NP rejected ==========================================


class TestBareSingularRejected:
    """The L83 rule's daughter pattern ``NP[CASE=NOM, COORD=BUT_NOT]``
    requires the asymmetric coord shape. Bare singular NPs lack
    COORD=BUT_NOT and continue to 0-parse as sentences — the L96 /
    L97 fragment-host opt-in mechanism for individual lex items is
    the only path for non-coord bare nominals to parse as sentences."""

    @pytest.mark.parametrize("sentence", [
        "Si Maria.",
        "Si Juan.",
        "Si Pedro.",
    ])
    def test_bare_proper_name_zero_parse(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 0, (
            f"bare proper-name NP must not parse as a sentence: "
            f"{sentence!r}"
        )


# === AND-coord and OR-coord fragments rejected =========================


class TestSymmetricCoordFragmentsRejected:
    """The L83 rule restricts to ``COORD=BUT_NOT``. Bare AND-coord
    and OR-coord NPs do not match — symmetric coord-NP fragments
    are not attested as canonical sentence fragments in Tagalog
    (per S&O 1972 §10). If corpus pressure later surfaces a use
    case, a separate rule with explicit AND / OR discriminators
    can be added."""

    @pytest.mark.parametrize("sentence", [
        "Si Maria at si Juan.",
        "Si Pedro at si Lola.",
        "Si Maria o si Juan.",
        "Si Pedro o si Lola.",
    ])
    def test_symmetric_coord_zero_parse(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 0, (
            f"symmetric coord-NP fragment must not parse: "
            f"{sentence!r}"
        )


# === hindi + bare NP not enough =========================================


class TestHindiPlusNpNotFragment:
    """``Hindi si Juan.`` is just ``hindi`` + a bare NP — it is NOT
    an asymmetric coord-NP (which requires the 4-daughter shape
    ``NP COMMA hindi NP``). Phase 5k Commit 8's rule doesn't fire
    here, so no COORD=BUT_NOT is built, so the L83 rule doesn't
    fire either."""

    @pytest.mark.parametrize("sentence", [
        "Hindi si Juan.",
        "Hindi si Maria.",
    ])
    def test_hindi_plus_np_zero_parse(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 0, (
            f"hindi + bare NP must not parse as fragment: "
            f"{sentence!r}"
        )


# === Phase 5k Commit 8 V-headed asymmetric coord unchanged =============


class TestVHeadedAsymmetricCoordUnaffected:
    """The Phase 5k Commit 8 asymmetric NP-coord rule continues to
    fire inside V-headed S frames (``Kumain si Maria, hindi si
    Juan.``). The new L83 rule adds an additional path (the
    fragment-S without verbal head); both paths can compose for
    the same coord-NP without competing on V-headed surfaces."""

    @pytest.mark.parametrize("sentence,verb_pred", [
        ("Kumain si Maria, hindi si Juan.", "EAT <SUBJ>"),
        ("Tumakbo si Pedro, hindi si Lola.", "TAKBO <SUBJ>"),
    ])
    def test_v_headed_asymmetric_coord(
        self, sentence: str, verb_pred: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"V-headed asymmetric coord should parse: {sentence!r}"
        )
        _ct, fs, _astr, _diags = parses[0]
        # V-headed S has the verb's PRED, NOT the synthetic NP-FRAG
        # PRED — the V-headed S rule fires; the L83 rule doesn't
        # produce a competing matrix because the surface has more
        # tokens than just an NP.
        assert fs.feats.get("PRED") == verb_pred
        assert fs.feats.get("CLAUSE_TYPE") != "FRAGMENT"
        # The SUBJ is the asymmetric coord-NP (Phase 5k Commit 8
        # output, unchanged).
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "BUT_NOT"


# === L78 wide-scope hindi unaffected ====================================


class TestL78WideScopeHindiUnaffected:
    """The Phase 5n.C Commit 2 wide-scope-hindi rule (which fires on
    AND/OR coord-NP SUBJ in pre-V position) is structurally
    distinct from L83 — its coord daughter is ``COORD=AND/OR``,
    not ``BUT_NOT``. The two rules don't compete."""

    @pytest.mark.parametrize("sentence", [
        "Hindi si Maria at si Juan kumain.",
        "Hindi si Maria o si Juan kumain.",
    ])
    def test_l78_unchanged(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # L78 produces NEG_SCOPE=WIDE, NOT CLAUSE_TYPE=FRAGMENT —
        # they're distinct constructions.
        assert fs.feats.get("NEG_SCOPE") == "WIDE"
        assert fs.feats.get("CLAUSE_TYPE") != "FRAGMENT"


# === Top-1 uniqueness =================================================


class TestNoAmbiguityBlowup:
    """The L83 fragment-S rule doesn't create new ambiguity for
    asymmetric-coord surfaces — the canonical fragment surface
    has exactly one parse, and V-headed surfaces continue to
    parse via the V-headed S path only."""

    def test_fragment_unique_parse(self) -> None:
        parses = parse_text("Si Maria, hindi si Juan.")
        assert len(parses) == 1

    def test_v_headed_unique_parse(self) -> None:
        parses = parse_text("Kumain si Maria, hindi si Juan.")
        assert len(parses) == 1
