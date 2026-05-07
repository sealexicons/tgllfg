"""Phase 5j Commit 6: modal lex inventory + LexicalEntry.

Roadmap §12.1 / plan-of-record §4.2 + §4.4, §6 Commit 6. Six new
PART entries in ``data/tgl/particles.yaml`` (all closed-class
``pos: VERB`` like the Phase 4 §7.6 PSYCH predicates and the
Phase 5i ``alam`` KNOW predicate) and one new NOUN entry in
``data/tgl/nouns.yaml`` (``kailangan`` polysemy partner). Plus
four ``LexicalEntry`` entries in ``src/tgllfg/core/lexicon.py``
with PRED template ``MODAL <SUBJ, XCOMP>``-style and
``CTRL_CLASS=MODAL`` morph_constraints.

* ``dapat``    — obligation ("should / must")
* ``puwede`` / ``pwede`` / ``puede`` — permission /
  possibility ("can / may"). Three orthographic variants
  collapsed to one canonical lemma ``puwede``.
* ``maaari``   — possibility / permission (formal)
* ``kailangan`` — necessity ("need / must"). Polysemous with
  the noun reading ("need / requirement").

This commit is lex-only — no grammar rules added. The Phase 5j
Commit 7 modal control wrap (``S → V[MODAL=YES] NP[CASE=NOM]
PART[LINK] V[CTRL_VOICE=ANY]``) consumes these entries.

**Documented temporary regression** (the Phase 5j flip-risk):
``Hindi ka dapat kumain.`` parsed pre-Commit-6 as ``EAT <SUBJ>``
with POLARITY=NEG by silently dropping ``dapat`` (the parser's
``_strip_non_content`` skipping the ``_UNK``-only token). After
Commit 6 lands modal lex, the strip stops firing on ``dapat``
and the residue ``Hindi ka kumain.`` no longer composes via the
existing rules — the sentence returns 0 parses. Commit 7's
modal control wrap restores the parse path with the proper
modal-headed matrix structure.

Tests verify only the lex layer in this commit; parse-layer
tests for the modal control wrap land in Commit 7.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import Token
from tgllfg.morph import Analyzer


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === Modal surface inventory ==========================================


MODAL_SURFACES = [
    # (surface, canonical_lemma)
    ("dapat",     "dapat"),
    ("puwede",    "puwede"),
    ("pwede",     "puwede"),    # surface variant collapses to puwede
    ("puede",     "puwede"),    # surface variant collapses to puwede
    ("maaari",    "maaari"),
    ("kailangan", "kailangan"),  # polysemous — also a NOUN
]


class TestModalLex:
    """Each modal surface indexes as VERB[MODAL=YES,
    CTRL_CLASS=MODAL] with the right canonical LEMMA."""

    @pytest.mark.parametrize("surface,canonical_lemma", MODAL_SURFACES)
    def test_indexed_as_modal_verb(
        self, surface: str, canonical_lemma: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        modals = [
            a for a in out
            if a.pos == "VERB" and a.feats.get("MODAL") == "YES"
        ]
        assert len(modals) == 1, (
            f"expected exactly one modal VERB analysis for "
            f"{surface!r}; got "
            f"{[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )

    @pytest.mark.parametrize("surface,canonical_lemma", MODAL_SURFACES)
    def test_carries_modal_and_ctrl_class(
        self, surface: str, canonical_lemma: str
    ) -> None:
        analyzer = Analyzer.from_default()
        modal = next(
            a for a in analyzer.analyze_one(_tok(surface))
            if a.pos == "VERB" and a.feats.get("MODAL") == "YES"
        )
        assert modal.feats.get("MODAL") == "YES"
        assert modal.feats.get("CTRL_CLASS") == "MODAL"
        assert modal.feats.get("LEMMA") == canonical_lemma


# === puwede / pwede / puede surface-variant collapse ================


class TestPuwedeSurfaceVariants:
    """``puwede`` / ``pwede`` / ``puede`` are three orthographic
    variants of one canonical modal lemma. All three index with
    ``LEMMA=puwede`` so the Commit 7 control wrap fires uniformly
    regardless of input spelling."""

    @pytest.mark.parametrize("surface", ["puwede", "pwede", "puede"])
    def test_all_three_collapse_to_puwede(self, surface: str) -> None:
        analyzer = Analyzer.from_default()
        modals = [
            a for a in analyzer.analyze_one(_tok(surface))
            if a.pos == "VERB" and a.feats.get("MODAL") == "YES"
        ]
        assert len(modals) == 1
        assert modals[0].feats.get("LEMMA") == "puwede"


# === kailangan polysemy =============================================


class TestKailanganPolysemy:
    """``kailangan`` has two readings: VERB[MODAL=YES] (the modal
    "need / must") and NOUN ("need / requirement", as in ``ang
    kailangan ko`` "what I need"). Both indexed by the analyzer;
    rule context disambiguates."""

    def test_kailangan_has_both_readings(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("kailangan"))
        modals = [a for a in out if a.pos == "VERB"]
        nouns = [a for a in out if a.pos == "NOUN"]
        assert len(modals) == 1, (
            f"expected one VERB reading; got {len(modals)}"
        )
        assert len(nouns) == 1, (
            f"expected one NOUN reading; got {len(nouns)}"
        )

    def test_kailangan_modal_carries_modal_flag(self) -> None:
        analyzer = Analyzer.from_default()
        modal = next(
            a for a in analyzer.analyze_one(_tok("kailangan"))
            if a.pos == "VERB"
        )
        assert modal.feats.get("MODAL") == "YES"
        assert modal.feats.get("CTRL_CLASS") == "MODAL"

    def test_kailangan_noun_has_no_modal_flag(self) -> None:
        analyzer = Analyzer.from_default()
        noun = next(
            a for a in analyzer.analyze_one(_tok("kailangan"))
            if a.pos == "NOUN"
        )
        assert noun.feats.get("MODAL") is None
        assert noun.feats.get("CTRL_CLASS") is None
        assert noun.feats.get("LEMMA") == "kailangan"


# === MODAL CTRL_CLASS does not cross-fire with PSYCH / KNOW ========


class TestModalCtrlClassDistinct:
    """Modals carry CTRL_CLASS=MODAL, NOT CTRL_CLASS=PSYCH or
    CTRL_CLASS=KNOW. This keeps the existing PSYCH wrap rules
    (gusto / ayaw / kaya control + linker-XCOMP) and KNOW wrap
    rules (alam indirect-Q embedding) from cross-firing on modal
    surfaces. The Commit 7 modal control wrap will use
    ``V[CTRL_CLASS=MODAL]`` to filter to modals only.
    """

    @pytest.mark.parametrize("modal_surface", [
        "dapat", "puwede", "maaari", "kailangan",
    ])
    def test_modal_ctrl_class_is_not_psych(
        self, modal_surface: str
    ) -> None:
        analyzer = Analyzer.from_default()
        modal = next(
            a for a in analyzer.analyze_one(_tok(modal_surface))
            if a.pos == "VERB" and a.feats.get("MODAL") == "YES"
        )
        assert modal.feats.get("CTRL_CLASS") != "PSYCH"

    @pytest.mark.parametrize("modal_surface", [
        "dapat", "puwede", "maaari", "kailangan",
    ])
    def test_modal_ctrl_class_is_not_know(
        self, modal_surface: str
    ) -> None:
        analyzer = Analyzer.from_default()
        modal = next(
            a for a in analyzer.analyze_one(_tok(modal_surface))
            if a.pos == "VERB" and a.feats.get("MODAL") == "YES"
        )
        assert modal.feats.get("CTRL_CLASS") != "KNOW"


# === Commit 7 watchpoint: documented temporary regression ==========


class TestNoLinkerModalIsZeroParses:
    """``Hindi ka dapat kumain.`` (no explicit linker between
    ``dapat`` and ``kumain``) parsed pre-Commit-6 as ``EAT
    <SUBJ>`` POLARITY=NEG via silent-dropping ``dapat``. Post-
    Commit-6 the strip stops firing and the sentence returns 0
    parses — and **stays at 0** post-Commit-7 too, because the
    canonical Tagalog modal+complement form requires the linker
    (``Hindi ka dapat na kumain.``). The no-linker form is
    marginal / colloquial and not supported by the Phase 5j
    Commit 7 modal control wrap (which requires
    ``PART[LINK=NA|NG]`` between the modal V and the embedded
    S_XCOMP).

    This test pins the post-Commit-6 / post-Commit-7 0-parse
    behavior. The **with-linker** counterpart
    ``Hindi ka dapat na kumain.`` parses correctly post-Commit-7
    — covered by Phase 5j Commit 7 tests
    (``test_phase5j_modal_control.py``).
    """

    def test_no_linker_form_is_zero_parses(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Hindi ka dapat kumain.")
        assert len(parses) == 0, (
            "Hindi ka dapat kumain. (no linker) should have 0 "
            "parses — the canonical form requires the linker "
            "(Hindi ka dapat NA kumain.). If you're seeing "
            "parses here, the modal control wrap may have been "
            "extended to a no-linker variant — verify the "
            "matrix-PRED shape and update this test."
        )
