"""Phase 5k Commit 1: coordinator + punctuation + negative-conjunct
lex inventory.

Roadmap §12.1 / plan-of-record §4.1-§4.4. Ten new lex entries
across three clusters:

* **Coordinators** (``data/tgl/particles.yaml``): ``at`` (additive),
  ``o`` (disjunctive), ``pero`` / ``ngunit`` / ``subalit``
  (adversatives), ``kaya`` (consequence — PART entry alongside
  the existing Phase 4 §7.6 PSYCH verb of the same surface).
* **Punctuation**: ``,`` as PUNCT[PUNCT_CLASS=COMMA] for the
  multi-conjunct (Oxford comma + ``at``) and asymmetric coord
  rules in Commits 4 / 8.
* **Negative-conjunct PARTs**: ``kundi`` (BUT_NOT), ``pati``
  (ALSO_INCL), ``lamang`` (formal of ``lang``, 2P enclitic
  ADV=ONLY) — added opportunistically; their main constructions
  (correlative coord ``hindi lang … kundi pati``, etc.) are
  deferred to Phase 5l or a Phase 5k follow-on (see plan-of-
  record §1 / §9.2).

This commit is lex-only — no grammar / analyzer code changes.
The Phase 5k coord grammar rules (Commits 3-7) constrain on
``COORD=AND`` / ``COORD=OR`` / etc. to fire on these surfaces.

Pre-state (verified 2026-05-07): ``at`` / ``o`` / ``pero`` /
``ngunit`` / ``subalit`` / ``naman`` / ``kundi`` / ``pati`` /
``lamang`` were all ``_UNK``; ``kaya`` was VERB[CTRL_CLASS=PSYCH]
only (the new PART entry adds the COORD=SO reading alongside).
Per the §3 reconnaissance, no Phase 5k-target coord sentences
parse today (they all return 0 parses); the only flip-risk
surface for the phase is the ``kaya`` polysemy in Commit 7,
not Commit 1.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import Token
from tgllfg.morph import Analyzer


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === Coordinators ====================================================


COORDINATORS = [
    # (surface, coord_value, lemma)
    ("at",      "AND", "at"),
    ("o",       "OR",  "o"),
    ("pero",    "BUT", "pero"),
    ("ngunit",  "BUT", "ngunit"),
    ("subalit", "BUT", "subalit"),
]


class TestCoordinatorParts:
    """Each non-polysemous coordinator indexes as PART with
    COORD=<value> + LEMMA feats."""

    @pytest.mark.parametrize("surface,coord,lemma", COORDINATORS)
    def test_indexed_as_coord_part(
        self, surface: str, coord: str, lemma: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        coords = [
            a for a in out
            if a.pos == "PART" and a.feats.get("COORD") == coord
        ]
        assert len(coords) == 1, (
            f"expected exactly one COORD={coord} PART analysis for "
            f"{surface!r}; got "
            f"{[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )

    @pytest.mark.parametrize("surface,coord,lemma", COORDINATORS)
    def test_carries_coord_and_lemma(
        self, surface: str, coord: str, lemma: str
    ) -> None:
        analyzer = Analyzer.from_default()
        part = next(
            a for a in analyzer.analyze_one(_tok(surface))
            if a.pos == "PART" and a.feats.get("COORD") is not None
        )
        assert part.feats.get("COORD") == coord
        assert part.feats.get("LEMMA") == lemma


# === `kaya` polysemy: VERB[PSYCH] + PART[COORD=SO] ===================


class TestKayaPolysemy:
    """``kaya`` carries TWO analyses: the existing Phase 4 §7.6
    VERB[CTRL_CLASS=PSYCH] (be able to / can do) and the new Phase
    5k PART[COORD=SO] (so / therefore). Same precedent as Phase 5j
    ``kailangan`` (V[MODAL] vs NOUN), Phase 5h ``pareho``
    (predicative-ADJ vs Q-floated), Phase 5i ``alin`` / ``ilan``."""

    def test_verb_psych_reading_present(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("kaya"))
        psych_verbs = [
            a for a in out
            if a.pos == "VERB" and a.feats.get("CTRL_CLASS") == "PSYCH"
        ]
        assert len(psych_verbs) == 1, (
            f"expected exactly one VERB[CTRL_CLASS=PSYCH] analysis "
            f"for 'kaya'; got "
            f"{[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )

    def test_part_coord_so_reading_present(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("kaya"))
        coord_parts = [
            a for a in out
            if a.pos == "PART" and a.feats.get("COORD") == "SO"
        ]
        assert len(coord_parts) == 1, (
            f"expected exactly one PART[COORD=SO] analysis for "
            f"'kaya'; got "
            f"{[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )

    def test_both_readings_returned(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("kaya"))
        pos_set = {a.pos for a in out}
        # Both must be present; no other readings expected.
        assert "VERB" in pos_set
        assert "PART" in pos_set


# === Punctuation =====================================================


class TestCommaPunct:
    """The structural comma indexes as PUNCT[PUNCT_CLASS=COMMA] so
    the multi-conjunct (Commit 4) and asymmetric (Commit 8) coord
    rules can consume it as a daughter. Without this entry it falls
    through as ``_UNK`` and gets silently dropped by
    ``_strip_non_content``, hiding its structural role."""

    def test_comma_indexed_as_punct(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(","))
        puncts = [
            a for a in out
            if a.pos == "PUNCT" and a.feats.get("PUNCT_CLASS") == "COMMA"
        ]
        assert len(puncts) == 1, (
            f"expected exactly one PUNCT[PUNCT_CLASS=COMMA] analysis; "
            f"got {[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )

    def test_comma_carries_lemma(self) -> None:
        analyzer = Analyzer.from_default()
        punct = next(
            a for a in analyzer.analyze_one(_tok(","))
            if a.pos == "PUNCT"
        )
        assert punct.feats.get("LEMMA") == ","
        assert punct.feats.get("PUNCT_CLASS") == "COMMA"


# === Negative-conjunct / additive PARTs ==============================


class TestKundi:
    """``kundi`` "but not / except" — PART[COORD=BUT_NOT]. Used in
    correlative coord ``hindi lang … kundi pati`` (deferred to
    Phase 5l or a 5k follow-on). Lex entry added now for
    opportunistic composition."""

    def test_kundi_indexed_as_coord_part(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("kundi"))
        coords = [
            a for a in out
            if a.pos == "PART" and a.feats.get("COORD") == "BUT_NOT"
        ]
        assert len(coords) == 1
        assert coords[0].feats.get("LEMMA") == "kundi"


class TestPati:
    """``pati`` "also / including" — PART[ADV=ALSO_INCL]. Used in
    correlative coord and inclusive-coord constructions. Lex-only."""

    def test_pati_indexed_as_part(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("pati"))
        parts = [
            a for a in out
            if a.pos == "PART" and a.feats.get("ADV") == "ALSO_INCL"
        ]
        assert len(parts) == 1
        assert parts[0].feats.get("LEMMA") == "pati"


class TestLamang:
    """``lamang`` "only" — formal of ``lang``. Same shape: PART[ADV=
    ONLY], 2P enclitic. The existing ``lang`` enclitic continues
    to handle the colloquial register; ``lamang`` covers the formal
    register identically."""

    def test_lamang_indexed_as_clitic_part(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("lamang"))
        parts = [
            a for a in out
            if a.pos == "PART" and a.feats.get("ADV") == "ONLY"
        ]
        assert len(parts) == 1
        assert parts[0].feats.get("LEMMA") == "lamang"
        assert parts[0].feats.get("is_clitic") is True
        assert parts[0].feats.get("CLITIC_CLASS") == "2P"


# === Cross-cluster: COORD value disambiguation =======================


class TestCoordValuesAreDistinct:
    """Each coordinator carries a distinct COORD value so the
    Commits 3-7 grammar rules can use category-pattern matching
    (``PART[COORD=AND]`` vs ``PART[COORD=OR]`` etc.) to fire
    selectively. No cross-fire: ``at`` doesn't match the disjunctive
    rule, ``o`` doesn't match the additive, etc."""

    def test_at_is_and_only(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("at"))
        coord_parts = [
            a for a in out
            if a.pos == "PART" and a.feats.get("COORD") is not None
        ]
        coord_values = {a.feats.get("COORD") for a in coord_parts}
        assert coord_values == {"AND"}

    def test_o_is_or_only(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("o"))
        coord_parts = [
            a for a in out
            if a.pos == "PART" and a.feats.get("COORD") is not None
        ]
        coord_values = {a.feats.get("COORD") for a in coord_parts}
        assert coord_values == {"OR"}

    def test_adversatives_share_but(self) -> None:
        """``pero`` / ``ngunit`` / ``subalit`` all share COORD=BUT
        — three lexical surfaces, one coord value. The Commit 6
        adversative rule fires uniformly on PART[COORD=BUT]."""
        analyzer = Analyzer.from_default()
        for surface in ("pero", "ngunit", "subalit"):
            out = analyzer.analyze_one(_tok(surface))
            coord_parts = [
                a for a in out
                if a.pos == "PART" and a.feats.get("COORD") == "BUT"
            ]
            assert len(coord_parts) == 1, (
                f"expected {surface!r} to carry COORD=BUT; "
                f"got {[(a.pos, dict(a.feats)) for a in out]}"
            )

    def test_kaya_part_is_so_only_among_part_readings(self) -> None:
        """The PART reading of ``kaya`` is COORD=SO only; the
        VERB[PSYCH] reading carries no COORD. The Commit 7
        consequence-coord rule fires on PART[COORD=SO]
        specifically, leaving the verbal reading available for
        psych-control contexts."""
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("kaya"))
        coord_parts = [
            a for a in out
            if a.pos == "PART" and a.feats.get("COORD") is not None
        ]
        coord_values = {a.feats.get("COORD") for a in coord_parts}
        assert coord_values == {"SO"}
