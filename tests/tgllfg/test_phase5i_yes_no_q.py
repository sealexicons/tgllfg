"""Phase 5i Commit 5: yes/no Q_TYPE lift for ``ba``.

Roadmap §12.1 / plan-of-record §5.4, §6 Commit 5.

The Phase 4 §7.3 ``ba`` 2P clitic ("yes/no question marker")
already absorbed into the matrix's ADJ set via the recursive
``S → S PART[CLITIC_CLASS=2P]`` rule. Phase 5i Commit 5 lifts a
matrix-level ``Q_TYPE: YES_NO`` flag so downstream consumers
(ranker / classifier / corpus tools) have a uniform clausal-Q-
type marker (YES_NO / WH / TAG) without traversing into the
ADJ adjunct set.

Implementation: split the existing single absorption rule into
two parallel rules:

* Rule A (generic 2P clitics — ``na``, ``pa``, ``daw``, ``rin``,
  ``lang``, ``nga``, ``pala``, ``kasi``, ...): adds
  ``¬ (↓2 QUESTION)`` to exclude ``ba``.
* Rule B (``ba`` only): matches PART[CLITIC_CLASS=2P, QUESTION=YES]
  and lifts ``(↑ Q_TYPE) = 'YES_NO'``.

The two-rule split is cleaner than a single rule with
``(↑ Q_TYPE) = ↓2 Q_TYPE`` defining-equation lift: the latter
creates an empty FStructure on the matrix when the daughter
lacks Q_TYPE (perturbing f-structure rendering for ~20 baseline
entries with non-ba 2P clitics).

The ``ba`` lex feat ``QUESTION: true`` (Python boolean) is
changed to ``QUESTION: "YES"`` (string) so the category-pattern
matcher can match ``PART[QUESTION=YES]`` (patterns store
feature values as strings; PyYAML parses ``YES`` as a string
in YAML 1.2, but ``true`` as a boolean — pre-Phase-5i ``ba``
used the boolean form which the matcher couldn't pin via
category-pattern syntax).

Baseline recaptured for ~5 ba-bearing baseline entries that
acquired the new Q_TYPE matrix feature (additive: same parse,
plus the Q_TYPE flag).
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Q_TYPE=YES_NO on matrix when ba is present =======================


class TestBaQTypeLift:
    """The matrix S of any ba-bearing clause carries Q_TYPE=YES_NO."""

    @pytest.mark.parametrize("sentence", [
        "Kumain ka ba ng kanin?",
        "Kumain ba si Maria ng kanin?",
        "Maganda ba ang bata?",
        "Pinakamaganda ba ang bahay?",
        "Mas matalino ba si Maria?",
        "Mas matalino ba si Maria kaysa kay Juan?",
        "Sobrang maganda ba ang bata?",
    ])
    def test_q_type_yes_no_on_matrix(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got 0"
        )
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("Q_TYPE") == "YES_NO", (
                f"expected Q_TYPE=YES_NO on {sentence!r}; "
                f"got {fs.feats.get('Q_TYPE')!r}"
            )


# === Negation × ba ====================================================


class TestNegationPlusBa:
    """``Hindi ba X?`` and ``X ba ang Y?`` patterns under negation
    should still produce Q_TYPE=YES_NO on the matrix."""

    @pytest.mark.parametrize("sentence", [
        "Hindi ba maganda ang bata?",
        "Hindi ba kumain ang bata?",
    ])
    def test_negation_plus_ba(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        ba_q_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "YES_NO"
        ]
        assert len(ba_q_parses) >= 1, (
            f"expected at least one Q_TYPE=YES_NO parse for "
            f"{sentence!r}; got {[p[1].feats for p in parses]}"
        )
        # Polarity should be NEG.
        for _ct, fs, _astr, _diags in ba_q_parses:
            assert fs.feats.get("POLARITY") == "NEG"


# === Other 2P clitics do NOT lift Q_TYPE ==============================


class TestOther2PCliticsNoQType:
    """The Phase 5i Commit 5 split keeps the generic Rule A (for
    non-question 2P clitics) free of the Q_TYPE lift. Sentences
    with na / pa / daw / rin / lang / nga should NOT acquire
    Q_TYPE=YES_NO."""

    @pytest.mark.parametrize("sentence", [
        "Kumain na ang bata.",
        "Kumain pa ang bata.",
        "Kumain daw ang bata.",
        "Maganda na ang bata.",
        "Mas matalino na siya.",
    ])
    def test_no_q_type_on_non_ba_clitics(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("Q_TYPE") != "YES_NO"
            # Q_TYPE should be None / unset.
            assert fs.feats.get("Q_TYPE") is None


# === Wh-fronting Q_TYPE unchanged =====================================


class TestWhFrontingQTypeUnchanged:
    """The Phase 5i Commit 2 / 4 wh-fronting rules still produce
    Q_TYPE=WH (not YES_NO). The ba lift doesn't perturb wh-Q."""

    @pytest.mark.parametrize("sentence,wh_lemma", [
        ("Sino ang kumain?",   "sino"),
        ("Ano ang kinain mo?", "ano"),
        ("Saan ka pumunta?",   "saan"),
        ("Bakit ka kumain?",   "bakit"),
    ])
    def test_wh_q_type_preserved(
        self, sentence: str, wh_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        wh_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1
        _, fs, _, _ = wh_parses[0]
        assert fs.feats.get("WH_LEMMA") == wh_lemma


# === Wh × ba combination ==============================================


class TestWhWithBa:
    """``Sino ba ang kumain?`` "Who is it that ate?" — wh-cleft
    with the ba clitic. The ba lift adds Q_TYPE=YES_NO; the
    cleft sets Q_TYPE=WH. Both equations write to the matrix's
    Q_TYPE — unification clash means at least one of the parses
    fails. The construction's status in modern Tagalog is
    contested (some sources accept; others prefer separate
    sentences or `ba` outside the wh-cleft). For Phase 5i, accept
    that one or both parses fire; assert that any successful parse
    has a coherent Q_TYPE."""

    def test_sino_ba_ang_kumain(self) -> None:
        # No specific assertion on parse count — the construction
        # may parse with one Q_TYPE winning, or fail entirely on
        # unification clash. Just verify any parse that does fire
        # has a single coherent Q_TYPE.
        parses = parse_text("Sino ba ang kumain?")
        for _ct, fs, _astr, _diags in parses:
            qt = fs.feats.get("Q_TYPE")
            assert qt in (None, "WH", "YES_NO")


# === Phase 4 / 5g / 5h baseline preservation =========================


class TestBaselinePreserved:
    """Phase 4 / 5g / 5h baselines unchanged. Sanity check on a
    few high-frequency constructions that don't involve ba."""

    @pytest.mark.parametrize("sentence", [
        "Maganda ang bata.",
        "Kumain ang aso ng isda.",
        "Mas matalino siya.",
        "Pinakamaganda ang bahay.",
        "Kasingganda si Maria si Ana.",
        "Sobrang maganda ang bata.",
    ])
    def test_no_phantom_q_type(self, sentence: str) -> None:
        """The Q_TYPE lift must not give phantom Q_TYPE values to
        non-Q-clitic constructions."""
        parses = parse_text(sentence)
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("Q_TYPE") is None, (
                f"unexpected Q_TYPE on {sentence!r}: "
                f"{fs.feats.get('Q_TYPE')!r}"
            )
