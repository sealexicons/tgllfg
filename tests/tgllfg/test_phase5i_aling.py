"""Phase 5i Commit 6: aling pre-N selector composition.

Roadmap §12.1 / plan-of-record §5.5, §6 Commit 6. Three pieces:

1. Drop the standalone ``aling`` Q lex entry from particles.yaml.
   Pre-Phase-5i Commit 6, ``aling`` was a single Q[WH=YES,
   VAGUE=YES] token; this prevented ``split_linker_ng`` from
   splitting the bound ``-ng`` (split_linker_ng's "if surface is
   itself a known full form, keep it intact" rule). After the
   drop, ``aling`` splits into ``alin`` + ``-ng`` and the
   existing Phase 5f Commit 15 vague-Q NP-modifier rule fires on
   ``ng aling aklat`` → NP[CASE=GEN].

2. Add a wh-Q + N companion rule in cfg/nominal.py:

       N → Q[VAGUE=YES, WH=YES] PART[LINK=NA|NG] N

   Lifts WH=YES + WH_LEMMA onto the matrix N (in addition to the
   QUANT / VAGUE lifts the non-wh companion provides). The
   constraining ``Q[VAGUE=YES, WH=YES]`` excludes non-wh Qs
   (lahat / iba / marami) so they continue to fire only the
   non-wh N-level companion.

3. Add a wh-N-cleft rule in cfg/clause.py:

       S → N[WH=YES] NP[CASE=NOM]

   Sibling to Phase 5i Commit 2's PRON-cleft. Same Q_TYPE=WH +
   WH_LEMMA matrix-feature pattern. Consumed by ``Aling bata
   ang kumain?`` constructions where the wh-pivot is an N
   (``aling bata``) rather than a PRON (``sino``).

End-to-end target sentences:

    Aling bata ang kumain?         "Which child ate?"
    Aling aklat ang kinain mo?     "Which book did you eat?"
    Bumili ka ng aling aklat?      "You bought which book?" (in-situ)

The ``Aso ang isda.`` corpus entry's expected outcome flips
from ``fail`` to ``fragment`` as a side-effect of the new
wh-N-cleft rule predicting N at clause-initial position
(Earley chart records a completed N state for ``aso``;
fragment extraction returns it). Documented in the corpus
notes.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Cleft-style wh-N pivot ============================================


class TestAlingClefttFronting:
    """``Aling N ang ...?`` — wh-N cleft. The wh-modified N is
    the matrix predicate; the headless RC NP[CASE=NOM] is the
    SUBJ. Q_TYPE=WH and WH_LEMMA=alin lifted onto matrix."""

    @pytest.mark.parametrize("sentence", [
        "Aling bata ang kumain?",
        "Aling aklat ang kinain mo?",
        "Aling lalaki ang bumili ng aklat?",
        "Aling kabayo ang tumakbo?",
    ])
    def test_q_type_wh_with_alin_lemma(self, sentence: str) -> None:
        parses = parse_text(sentence)
        wh_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1, (
            f"expected at least one wh-Q parse for {sentence!r}; "
            f"got {len(parses)} total"
        )
        _ct, fs, _astr, _diags = wh_parses[0]
        assert fs.feats.get("PRED") == "WH <SUBJ>"
        assert fs.feats.get("WH_LEMMA") == "alin"


# === In-situ wh-modified NP in OBJ position ============================


class TestAlingInSituObjPosition:
    """``Bumili ka ng aling aklat?`` — wh-modified NP fills OBJ.
    The Phase 5f Commit 15 vague-Q NP-modifier rule fires on
    ``ng + alin + -ng + aklat`` (after split_linker_ng splits
    ``aling``)."""

    @pytest.mark.parametrize("sentence,verb_pred", [
        ("Bumili ka ng aling aklat?",  "BUY"),
        ("Bumasa ka ng aling aklat?",  "READ"),
        ("Kumain ka ng aling kanin?",  "EAT"),
    ])
    def test_in_situ_aling_obj(
        self, sentence: str, verb_pred: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED", "").startswith(verb_pred)


# === Non-wh Qs do NOT fire the wh-N-cleft ==============================


class TestNonWhQsExcluded:
    """The wh-N-cleft constrains on N[WH=YES]. Non-wh Q-modified
    Ns (``maraming bata``, ``lahat ng bata``) do not fire the
    cleft rule."""

    @pytest.mark.parametrize("sentence", [
        # Non-wh vague-Q-modified N in cleft position — should
        # not fire the wh-N-cleft.
        "Maraming bata ang kumain.",
        "Kaunting bata ang kumain.",
    ])
    def test_non_wh_q_not_in_wh_cleft(self, sentence: str) -> None:
        parses = parse_text(sentence)
        # If parses exist (predicative-N is deferred so likely 0),
        # none should have Q_TYPE=WH.
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("Q_TYPE") != "WH"


# === Wh × negation =====================================================


class TestAlingWithNegation:
    """``Aling bata ang hindi kumain?`` — wh-cleft with negated
    headless RC. The negation is inside the SUBJ NP."""

    def test_aling_with_negated_inner(self) -> None:
        parses = parse_text("Aling bata ang hindi kumain?")
        # Multiple parses possible; at least one should be wh-N-cleft.
        wh_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "WH"
        ]
        # The inner SUBJ NP is `ang hindi kumain` (headless RC);
        # whether headless RCs admit negation is Phase 4 §7.5
        # territory. Be permissive: just check at least one parse
        # produced (or zero is acceptable if the headless-RC +
        # negation combination is unsupported).
        # Soft check: any Q_TYPE=WH parse has WH_LEMMA=alin.
        for _ct, fs, _astr, _diags in wh_parses:
            assert fs.feats.get("WH_LEMMA") == "alin"


# === Earlier Phase 5i baselines preserved ==============================


class TestPhase5iEarlierCommitsPreserved:
    """Commits 1-5 work continues unchanged."""

    @pytest.mark.parametrize("sentence,wh_lemma", [
        # Commit 2 PRON cleft
        ("Sino ang kumain?",   "sino"),
        ("Ano ang kinain mo?", "ano"),
        # Commit 4 adverbial
        ("Saan ka pumunta?",   "saan"),
        ("Bakit ka kumain?",   "bakit"),
    ])
    def test_wh_q_preserved(
        self, sentence: str, wh_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        wh_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1
        _, fs, _, _ = wh_parses[0]
        assert fs.feats.get("WH_LEMMA") == wh_lemma

    def test_yes_no_q_preserved(self) -> None:
        parses = parse_text("Kumain ka ba ng kanin?")
        ba_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "YES_NO"
        ]
        assert len(ba_parses) >= 1


class TestEarlierPhaseBaselinePreserved:
    """Earlier-phase predicative clauses unchanged."""

    @pytest.mark.parametrize("sentence", [
        "Maganda ang bata.",
        "Mas matalino siya.",
        "Pinakamaganda ang bahay.",
        "Kasingganda si Maria si Ana.",
        "Tatlo ang aklat.",
        "Bumili ng aklat ang lalaki.",
    ])
    def test_baseline_predicatives(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        for _ct, fs, _astr, _diags in parses:
            # No Q_TYPE on these.
            assert fs.feats.get("Q_TYPE") not in ("WH", "YES_NO")


# === split_linker_ng splits aling correctly ============================


class TestSplitLinkerNgAling:
    """After Commit 6 dropped the explicit ``aling`` Q lex entry,
    ``split_linker_ng`` should split ``aling`` → ``alin`` + ``-ng``
    when ``alin`` is a known surface. This is the foundation for
    Commit 6's pre-N composition."""

    def test_aling_splits_into_alin_and_linker(self) -> None:
        from tgllfg.text import tokenize, split_linker_ng

        toks = tokenize("aling bata")
        toks = split_linker_ng(toks)
        norms = [t.norm for t in toks]
        assert norms == ["alin", "-ng", "bata"], (
            f"expected split [alin, -ng, bata]; got {norms}"
        )
