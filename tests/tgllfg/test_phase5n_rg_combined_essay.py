"""Phase 5n.A Commit 8 — R&G "Ang Manok" combined essay-paragraph (§18 L64).

R&G "Ang Manok" (Ramos & Goulet 1981, *Intermediate Tagalog*, p. 482)
combines the seven simple sentences (#1-#7) into one nested
sentence:

    ``May isang mamang matanda na nakatirang mag-isa sa maliit na
    bahay na nasa tuktok ng mataas na bundok sa bukid.``
    "There was an old man who lived alone in a small house on top
    of a high mountain in the country."

The integration target landed in Phase 5n.A Commits 5–8:

* Commit 5 — ``mag-isa`` ADV tokenizer hyphen-split
* Commit 6 — ``nakatira`` resultative ``naka-`` ADJ paradigm
* Commit 7 — ``mama`` NOUN lex + PRON-internal depictive rule
              (``NP[CASE=NOM] → PRON[CASE=NOM] PART[LINK=NG]
              ADV[MAGISA=YES]``)
* Commit 8 — three additional rules (this commit):
  - ADJ-internal depictive (``ADJ → ADJ PART[LINK=N{A,G}]
    ADV[MAGISA=YES]``) for ``nakatirang mag-isa`` as a complex
    ADJ inside an N-modifier or RC body.
  - N-level RC wrap (``N → N PART[LINK=N{A,G}] S_GAP``) so the
    existential ``may`` (which takes an N daughter, not NP) can
    compose with an RC.
  - nasa-headed S_GAP variants (``S_GAP → PART[LOC_EXISTENTIAL=YES]
    N`` and ``S_GAP → PART[LOC_EXISTENTIAL=YES] N NP[CASE=GEN]``)
    so a locative-existential ``nasa`` clause can be the body of
    an RC.

Closure note: the combined essay parses with multiple readings due
to genuine RC-attachment ambiguity in the deeply nested structure;
test asserts ``>= 1`` rather than pinning a specific count.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === The combined essay-paragraph =========================================


COMBINED_ESSAY = (
    "May isang mamang matanda na nakatirang mag-isa sa maliit na "
    "bahay na nasa tuktok ng mataas na bundok sa bukid."
)


class TestCombinedEssayParses:
    """The R&G p. 482 combined essay-paragraph parses as one S."""

    @pytest.mark.slow
    def test_combined_essay_parses(self) -> None:
        parses = parse_text(COMBINED_ESSAY)
        assert len(parses) >= 1, (
            "R&G combined essay-paragraph regressed to 0-parse — "
            "Phase 5n.A Commits 5-8 chain may have been broken; "
            "check ADJ-with-depictive / N-level RC / nasa-S_GAP "
            "rules in cfg/nominal.py and cfg/extraction.py"
        )


# === ADJ-internal depictive composition ===================================


class TestAdjInternalDepictive:
    """The ``ADJ → ADJ PART[LINK=N{A,G}] ADV[MAGISA=YES]`` rule lets
    ``nakatirang mag-isa`` parse as a complex ADJ that the existing
    Phase 5g Commit 2 ``N → N PART[LINK=N{A,G}] ADJ`` post-N
    modifier rule consumes."""

    @pytest.mark.parametrize("sentence", [
        "May mamang nakatirang mag-isa.",
        "May mamang nakatirang mag-isa sa bahay.",
        "May isang mamang matanda na nakatirang mag-isa.",
        "May isang mamang matanda na nakatirang mag-isa sa bahay.",
    ])
    def test_n_with_adj_depictive_modifier(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === nasa-headed RC body via new S_GAP variant =============================


class TestNasaHeadedRcBody:
    """The ``S_GAP → PART[LOC_EXISTENTIAL=YES] N [NP[CASE=GEN]]`` rules
    let a nasa locative-existential clause function as an RC body
    when the head N is the implied SUBJ of the locative-existential."""

    @pytest.mark.parametrize("sentence", [
        "May bahay na nasa bundok.",
        "May bahay na nasa tuktok ng bundok.",
        "May maliit na bahay na nasa bundok.",
        "May maliit na bahay na nasa tuktok ng bundok.",
        "May maliit na bahay na nasa tuktok ng mataas na bundok.",
    ])
    def test_existential_with_nasa_rc(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === Regression: existing parses unchanged =================================


class TestPhase5jBaselineUnchanged:
    """The new rules must not break existing parses. Spot-check
    the Phase 5j locative-existential matrix forms (``Nasa bundok
    ang bahay``, ``Nasa tuktok ng bundok ang bahay``) and the
    existing existential-with-N-modifier forms (``May bahay``,
    ``May maliit na bahay``)."""

    @pytest.mark.parametrize("sentence", [
        "Nasa bundok ang bahay.",
        "Nasa tuktok ng bundok ang bahay.",
        "Nasa tuktok ng mataas na bundok ang bahay.",
        "May bahay.",
        "May bahay sa bundok.",
        "May maliit na bahay.",
        "May maliit na bahay sa bukid.",
    ])
    def test_phase5j_baseline_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
