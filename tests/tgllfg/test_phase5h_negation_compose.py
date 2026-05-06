"""Phase 5h Commit 8: negation × Phase 5h composition.

Roadmap §12.1 / plan-of-record §6 Commit 8. Tests-only commit; no
new grammar / lex / morphology. Negation (Phase 4 §7.2 hindi rule,
tightened in Phase 5h Commit 3) composes with every Phase 5h
construction unchanged because each construction's matrix output
is a well-formed S that the hindi-negation rule wraps.

This file fills coverage gaps left by per-Commit test files:

* ``hindi pareho`` / ``hindi magkaiba`` / ``hindi magkapareho``
  (equative-identity predicates × negation — Commit 2 added the
  predicates; this file adds the negation tests).
* ``hindi pinakamaganda`` / ``hindi napakaganda`` (Phase 5h
  Commit 1 morphology × negation).
* Integration smoke tests covering the full Phase 5h surface:
  intensifier × kaysa × negation, etc.

Per-Commit test files already cover:

* Commit 3 (test_phase5h_comparative.py) —
  ``Hindi mas matalino siya``.
* Commit 4 (test_phase5h_kaysa.py) —
  ``Hindi mas matalino siya kaysa kay Maria``.
* Commit 5 (test_phase5h_intensifiers.py) —
  ``Hindi sobrang mainit ang tubig`` and 4 others.
* Commit 6 (test_phase5h_equative_two_np.py) —
  ``Hindi kasingganda si Maria si Ana``.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Equative-identity predicates × negation ===========================


class TestNegationEquativeIdentity:
    """The Phase 5h Commit 2 equative-identity predicates (pareho /
    magkapareho / magkaiba) compose with hindi via the existing
    Phase 4 negation rule."""

    @pytest.mark.parametrize("sentence,adj_lemma", [
        ("Hindi pareho ang aklat.",        "pareho"),
        ("Hindi pareho ang aklat ko.",     "pareho"),
        ("Hindi magkapareho ang aklat.",   "magkapareho"),
        ("Hindi magkaiba ang aklat.",      "magkaiba"),
        ("Hindi magkaiba ang sapatos.",    "magkaiba"),
    ])
    def test_hindi_equative_identity(
        self, sentence: str, adj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got 0"
        )
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("PRED") == "ADJ <SUBJ>"
            assert fs.feats.get("ADJ_LEMMA") == adj_lemma
            assert fs.feats.get("POLARITY") == "NEG"


# === Phase 5h Commit 1 morphology × negation ==========================


class TestNegationMorphologicalDegree:
    """Phase 5h Commit 1 productive cells (pinaka-, napaka-) and
    Commit 2 cells (kasing-, sing-) compose with hindi: the cells
    produce ADJ surfaces; the predicative-adj clause rule fires;
    the hindi rule wraps the resulting S."""

    @pytest.mark.parametrize("sentence,adj_lemma", [
        # Phase 5h Commit 1: pinaka-
        ("Hindi pinakamaganda ang bahay.",   "ganda"),
        ("Hindi pinakamatalino siya.",       "talino"),
        ("Hindi pinakamabilis ang kabayo.",  "bilis"),
        # Phase 5h Commit 1: napaka-
        ("Hindi napakaganda ang bahay.",     "ganda"),
        ("Hindi napakatalino siya.",         "talino"),
        ("Hindi napakaliit ang bahay.",      "liit"),
        # Phase 5h Commit 2: kasing- / sing-
        ("Hindi kasingganda ang bahay.",     "ganda"),
        ("Hindi singganda ang bahay.",       "ganda"),
    ])
    def test_hindi_morphological_degree(
        self, sentence: str, adj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "ADJ <SUBJ>"
        assert fs.feats.get("ADJ_LEMMA") == adj_lemma
        assert fs.feats.get("POLARITY") == "NEG"


# === Canonical "Hindi masyado" — Tagalog "not very" ====================


class TestHindiMasyadoCanonical:
    """``Hindi masyadong X`` is the canonical Tagalog "not very X"
    construction. Plan §1 calls this out explicitly: "Interaction
    with negation (hindi masyado 'not very')". This is a sanity
    suite that asserts the f-structure for the canonical surface."""

    @pytest.mark.parametrize("sentence,adj_lemma", [
        ("Hindi masyadong mainit ang tubig.",  "init"),
        ("Hindi masyadong maganda ang bata.",  "ganda"),
        ("Hindi masyadong malakas ang lalaki.", "lakas"),
        ("Hindi masyadong matalino siya.",     "talino"),
        ("Hindi masyadong malaki ang bahay.",  "laki"),
    ])
    def test_hindi_masyado_predicative(
        self, sentence: str, adj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "ADJ <SUBJ>"
        assert fs.feats.get("ADJ_LEMMA") == adj_lemma
        assert fs.feats.get("POLARITY") == "NEG"


# === Integration: full Phase 5h surface composes with negation ========


class TestNegationFullPhase5hSurface:
    """End-to-end smoke tests covering every Phase 5h construction
    type composing with negation."""

    def test_negation_of_kaysa_comparative(self) -> None:
        """``Hindi mas matalino si Ana kaysa kay Maria.`` —
        full chain: negation × comparative-mas × kaysa standard."""
        parses = parse_text("Hindi mas matalino si Ana kaysa kay Maria.")
        assert len(parses) >= 1
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("PRED") == "ADJ <SUBJ>"
            assert fs.feats.get("ADJ_LEMMA") == "talino"
            assert fs.feats.get("POLARITY") == "NEG"

    def test_negation_of_equative_two_np(self) -> None:
        """``Hindi kasingganda ng bahay mo ang bahay ko.`` —
        full chain: negation × equative two-NP frame."""
        parses = parse_text("Hindi kasingganda ng bahay mo ang bahay ko.")
        equative_parses = [
            (ct, fs, ast, diags) for (ct, fs, ast, diags) in parses
            if any(
                hasattr(m, "feats")
                and m.feats.get("ROLE") == "EQUATIVE_STANDARD"
                for m in (fs.feats.get("ADJUNCT") or set())
            )
        ]
        assert len(equative_parses) >= 1
        _ct, fs, _astr, _diags = equative_parses[0]
        assert fs.feats.get("ADJ_LEMMA") == "ganda"
        assert fs.feats.get("POLARITY") == "NEG"

    def test_negation_of_intensified_predicate(self) -> None:
        """``Hindi sobrang malakas ang lalaki.`` —
        negation × intensifier-ADJ wrapper."""
        parses = parse_text("Hindi sobrang malakas ang lalaki.")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "ADJ <SUBJ>"
        assert fs.feats.get("ADJ_LEMMA") == "lakas"
        assert fs.feats.get("POLARITY") == "NEG"

    def test_negation_of_comparative_q_in_obj(self) -> None:
        """``Hindi bumili ng mas maraming aklat ang lalaki.`` —
        negation × comparative-Q × NP-modifier."""
        parses = parse_text(
            "Hindi bumili ng mas maraming aklat ang lalaki."
        )
        assert len(parses) >= 1
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("PRED", "").startswith("BUY")
            assert fs.feats.get("POLARITY") == "NEG"


# === Phase 4 hindi rule still fires on its own ========================


class TestHindiBaselinePreserved:
    """The Phase 4 hindi-negation rule's tightening in Phase 5h
    Commit 3 (`(↓1 POLARITY) =c 'NEG'`) must not break the
    canonical `hindi`-only use. Sanity check: the Phase 5g
    bare-ma- predicative under negation still parses."""

    @pytest.mark.parametrize("sentence,adj_lemma", [
        ("Hindi maganda ang bata.",   "ganda"),
        ("Hindi matalino siya.",      "talino"),
        ("Hindi mabilis ang kabayo.", "bilis"),
        ("Hindi mainit ang tubig.",   "init"),
        ("Hindi malakas ang lalaki.", "lakas"),
    ])
    def test_phase5g_baseline_negation(
        self, sentence: str, adj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "ADJ <SUBJ>"
        assert fs.feats.get("ADJ_LEMMA") == adj_lemma
        assert fs.feats.get("POLARITY") == "NEG"
