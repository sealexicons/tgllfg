# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.A Commit 7 — mama NOUN lex + R&G "Ang Manok" simples #1 / #3 (§18 L62 + L63).

R&G "Ang Manok" (Ramos & Goulet 1981, *Intermediate Tagalog*, p. 482)
is a benchmark essay-paragraph composed of seven simple sentences.
Two were blocked at end of Phase 5j:

    #1: ``May isang mamang nakatira sa isang bahay sa bukid.``
        "There was an old man who lived in a house in the country."
    #3: ``Nakatira siyang mag-isa sa bahay.``
        "He lived alone in the house."

§18 listed three blockers — ``mag-isa`` ADV (Commit 5),
``nakatira`` resultative paradigm (Commit 6), and ``mama`` NOUN lex
(this commit). Audit during Commit 7 surfaced a fourth dimension:
the R&G #3 sentence requires a depictive secondary-predicate
composition rule (``NP[CASE=NOM] → PRON[CASE=NOM] PART[LINK=NG]
ADV[MAGISA=YES]``) — the ``siyang mag-isa`` constituent is an NP
with PRON head and depictive ADV modifier. The §18 entry didn't
mention this; per the anti-deferral discipline, the rule lands here
in Commit 7 alongside the ``mama`` lex addition.

R&G simple #2 (``Matanda siya.``), #4 (``Maliit ang bahay.``),
#5 (``Nasa bundok ang bahay.``), #6 (``Mataas ang bundok.``), and
#7 (``Nasa tuktok ng bundok ang bahay.``) parsed cleanly already —
regression tests are bundled here for the R&G coverage net.

The combined essay-paragraph (R&G p. 482 single-sentence form) is
Commit 8's target — pinned at 0-parse here pending that commit.
"""

from tgllfg.core.common import Token
from tgllfg.core.pipeline import parse_text
from tgllfg.morph import Analyzer


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === mama NOUN lex (L62) ==================================================


class TestMamaNounLex:
    """The new ``mama`` NOUN entry parses as a NOUN with the
    expected gloss-class behavior."""

    def test_mama_analyzes_as_noun(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("mama"))
        nouns = [a for a in out if a.pos == "NOUN"]
        assert any(a.lemma == "mama" for a in nouns), (
            f"mama should be indexed as NOUN; got "
            f"{[(a.pos, a.lemma) for a in out]}"
        )

    def test_mama_in_simple_sentence(self) -> None:
        """``Kumain ang mama.`` "The man ate." parses as a simple
        AV intransitive with NOM-NP SUBJ headed by ``mama``."""
        parses = parse_text("Kumain ang mama.")
        assert len(parses) >= 1

    def test_mama_as_obj(self) -> None:
        """``Nakita ko ang mama.`` "I saw the man." parses as an
        OV transitive with NOM-NP OBJ headed by ``mama``."""
        parses = parse_text("Nakita ko ang mama.")
        assert len(parses) >= 1


# === R&G simple #1 (L63) =================================================


class TestRgSimple1:
    """``May isang mamang nakatira sa isang bahay sa bukid.``
    "There was an old man who lived in a house in the country.""

    Composes: existential ``may`` (Phase 5j Commit 2) + cardinal
    ``isang`` + linker + ``mamang`` (mama + linker) + ``nakatira``
    (Commit 6 ADJ resultative or VERB ABIL) + locative ``sa``-PP
    + locative ``sa``-PP."""

    def test_rg_simple_1_parses(self) -> None:
        parses = parse_text(
            "May isang mamang nakatira sa isang bahay sa bukid."
        )
        assert len(parses) >= 1


# === R&G simple #3 (L63) =================================================


class TestRgSimple3:
    """``Nakatira siyang mag-isa sa bahay.`` "He lived alone in the
    house."

    Composes: ``nakatira`` (Commit 6 ADJ resultative) + ``siyang
    mag-isa`` (Commit 7 depictive secondary-predicate rule) + ``sa
    bahay`` (locative PP)."""

    def test_rg_simple_3_parses(self) -> None:
        parses = parse_text("Nakatira siyang mag-isa sa bahay.")
        assert len(parses) >= 1

    def test_simple_3_components(self) -> None:
        """Component sentences that exercise just the new depictive
        rule, without the locative PP."""
        for s in (
            "Nakatira siyang mag-isa.",
            "Nakaupo siyang mag-isa.",
            "Nakahiga siyang mag-isa.",
        ):
            parses = parse_text(s)
            assert len(parses) >= 1, (
                f"depictive mag-isa with naka- ADJ should parse: {s!r}"
            )


# === R&G simples #2, #4, #5, #6, #7 (regression) ==========================


class TestOtherRgSimplesUnchanged:
    """The other five R&G "Ang Manok" simples parsed before Commit 7;
    they must continue to parse."""

    def test_simple_2_matanda_siya(self) -> None:
        assert len(parse_text("Matanda siya.")) >= 1

    def test_simple_4_maliit_ang_bahay(self) -> None:
        assert len(parse_text("Maliit ang bahay.")) >= 1

    def test_simple_5_nasa_bundok_ang_bahay(self) -> None:
        assert len(parse_text("Nasa bundok ang bahay.")) >= 1

    def test_simple_6_mataas_ang_bundok(self) -> None:
        assert len(parse_text("Mataas ang bundok.")) >= 1

    def test_simple_7_nasa_tuktok_ng_bundok(self) -> None:
        assert len(parse_text("Nasa tuktok ng bundok ang bahay.")) >= 1


# === Combined essay-paragraph — see test_phase5n_rg_combined_essay.py =====
#
# Phase 5n.A Commit 8 lands the integrated combined essay parse
# via three new rules: ADJ-with-depictive (``ADJ → ADJ
# PART[LINK=N{A,G}] ADV[MAGISA=YES]``), N-level RC wrap
# (``N → N PART[LINK=N{A,G}] S_GAP``), and nasa-headed S_GAP variants.
# Tests live in test_phase5n_rg_combined_essay.py.


# === Depictive rule — narrow scoping audit ===============================


class TestDepictiveRuleScopedToMagIsa:
    """The new depictive rule
    (``NP[CASE=NOM] → PRON[CASE=NOM] PART[LINK=NG] ADV[MAGISA=YES]``)
    is gated on ``MAGISA=YES`` to keep it narrow. Sibling depictive
    constructions (``siyang mabilis``, ``siyang madalas``) remain
    0-parses, deferred until corpus pressure surfaces."""

    def test_siyang_mabilis_still_zero_parse(self) -> None:
        """``Tumakbo siyang mabilis.`` would be the depictive
        secondary predicate with manner-ADJ ``mabilis``. Not in
        Phase 5n.A scope; pinned to detect when the rule
        generalizes."""
        parses = parse_text("Tumakbo siyang mabilis.")
        assert len(parses) == 0

    def test_siyang_madalas_still_zero_parse(self) -> None:
        """``Nakatira siyang madalas.`` would be PRON+linker+
        FREQ-ADV depictive. Out of scope; pinned."""
        parses = parse_text("Nakatira siyang madalas.")
        assert len(parses) == 0
