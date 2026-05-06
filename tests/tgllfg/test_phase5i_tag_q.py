"""Phase 5i Commit 7: tag question `di ba?`.

Roadmap §12.1 / plan-of-record §5.6, §6 Commit 7. New clause
rule in cfg/clause.py:

    S → S PART[NEG_TAG=YES] PART[QUESTION=YES, CLITIC_CLASS=2P]

The sentence-final tag ``di ba`` is the canonical Tagalog tag-
question marker, asking the addressee to confirm the preceding
statement. ``di`` is the colloquial shortening of ``hindi``
(negation; PART[NEG_TAG=YES] from Phase 5i Commit 1); ``ba`` is
the yes/no Q clitic (PART[QUESTION=YES, CLITIC_CLASS=2P] —
Phase 4 §7.3 + Phase 5i Commit 5 Q_TYPE lift).

Together they form a fixed sentence-final tag with QUESTION +
NEG_TAG semantics. The matrix carries Q_TYPE=TAG (distinct from
Commit 5's YES_NO and Commit 2 / 4 / 6's WH).

End-to-end target sentences:

    Maganda ang bata, di ba?           "The child is beautiful, isn't it?"
    Kumain ang aso ng isda, di ba?     "The dog ate fish, didn't it?"
    Mas matalino si Maria, di ba?      "Maria's smarter, isn't she?"
    Hindi maganda ang bata, di ba?     (negation × tag; POLARITY=NEG)

The yes/no ba-Q rule (Phase 5i Commit 5) and the tag-Q rule
both match `ba` in tag position; the matrix-Q_TYPE clash
(YES_NO vs TAG) leaves only the tag reading as the surviving
parse.

**Out of scope this commit**:

* Elided-SUBJ form (``Maganda, di ba?`` "Beautiful, isn't it?")
  needs an ADJ-only predicative without a SUBJ NP[CASE=NOM] —
  defer to Phase 5i follow-on if corpus pressure surfaces.
* Combined ``ba ... di ba?`` (yes/no + tag in same sentence)
  has ambiguous ba placement; defer.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Tag-Q on various S types =========================================


class TestTagQOnVariousS:
    """The tag wraps any well-formed S unchanged: predicative-adj,
    verbal, comparative, intensifier, etc."""

    @pytest.mark.parametrize("sentence,expected_pred_prefix", [
        ("Maganda ang bata, di ba?",         "ADJ"),
        ("Kumain ang aso ng isda, di ba?",   "EAT"),
        ("Bumili ng aklat ang lalaki, di ba?", "BUY"),
        ("Mas matalino si Maria, di ba?",    "ADJ"),
        ("Pinakamaganda ang bahay, di ba?",  "ADJ"),
        ("Sobrang maganda ang bata, di ba?", "ADJ"),
    ])
    def test_q_type_tag(
        self, sentence: str, expected_pred_prefix: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got 0"
        )
        # Find the tag-Q parse.
        tag_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "TAG"
        ]
        assert len(tag_parses) >= 1
        _ct, fs, _astr, _diags = tag_parses[0]
        assert (fs.feats.get("PRED") or "").startswith(
            expected_pred_prefix
        )


# === Tag-Q without comma also parses ==================================


class TestTagQNoComma:
    """The comma is orthographic — stripped pre-parse. The tag
    construction parses with or without the comma."""

    def test_no_comma(self) -> None:
        parses = parse_text("Maganda ang bata di ba?")
        tag_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "TAG"
        ]
        assert len(tag_parses) >= 1


# === Negation × tag ===================================================


class TestNegationPlusTag:
    """Negation composes with the tag construction. ``Hindi maganda
    ang bata, di ba?`` "It's not beautiful, is it?" — POLARITY=NEG
    on matrix + Q_TYPE=TAG."""

    @pytest.mark.parametrize("sentence", [
        "Hindi maganda ang bata, di ba?",
        "Hindi kumain ang aso, di ba?",
    ])
    def test_negation_plus_tag(self, sentence: str) -> None:
        parses = parse_text(sentence)
        tag_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "TAG"
        ]
        assert len(tag_parses) >= 1
        _ct, fs, _astr, _diags = tag_parses[0]
        assert fs.feats.get("POLARITY") == "NEG"


# === di alone or ba alone do NOT fire the tag rule ===================


class TestPartialTagNotMatched:
    """The tag rule requires BOTH PART[NEG_TAG=YES] AND
    PART[QUESTION=YES] adjacent. ``Maganda ang bata di.`` (just
    ``di`` without ``ba``) and ``Maganda ang bata ba?`` (just ``ba``
    — would be yes/no Q, not tag) do not produce Q_TYPE=TAG."""

    def test_di_alone(self) -> None:
        # `Maganda ang bata di.` — `di` without `ba` doesn't form a
        # tag.
        parses = parse_text("Maganda ang bata di.")
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("Q_TYPE") != "TAG"

    def test_ba_alone_is_yes_no(self) -> None:
        # `Maganda ba ang bata?` — just `ba`, would be yes/no Q.
        parses = parse_text("Maganda ba ang bata?")
        # Should be Q_TYPE=YES_NO, not TAG.
        for _ct, fs, _astr, _diags in parses:
            qt = fs.feats.get("Q_TYPE")
            assert qt != "TAG"


# === Tag and other Q types are mutually exclusive on matrix ===========


class TestQTypeUniqueness:
    """The matrix Q_TYPE is a single flag (TAG | YES_NO | WH).
    Sanity check: tag-Q sentences don't accidentally also have
    Q_TYPE=YES_NO or Q_TYPE=WH."""

    def test_tag_q_only_q_type(self) -> None:
        parses = parse_text("Maganda ang bata, di ba?")
        tag_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "TAG"
        ]
        assert len(tag_parses) >= 1
        _ct, fs, _astr, _diags = tag_parses[0]
        assert fs.feats.get("Q_TYPE") == "TAG"
        # WH_LEMMA should not be set.
        assert fs.feats.get("WH_LEMMA") is None


# === Phase 5i earlier-commit baselines preserved ======================


class TestPhase5iBaselinePreserved:
    """The new tag-Q rule must not perturb earlier Phase 5i
    constructions: cleft (Commit 2), in-situ (Commit 3),
    adverbial (Commit 4), yes/no (Commit 5), aling (Commit 6)."""

    @pytest.mark.parametrize("sentence,q_type", [
        ("Sino ang kumain?",          "WH"),
        ("Saan ka pumunta?",          "WH"),
        ("Bakit ka kumain?",          "WH"),
        ("Aling bata ang kumain?",    "WH"),
        ("Kumain ka ba ng kanin?",    "YES_NO"),
        ("Maganda ba ang bata?",      "YES_NO"),
    ])
    def test_phase5i_q_types_preserved(
        self, sentence: str, q_type: str
    ) -> None:
        parses = parse_text(sentence)
        matching = [
            p for p in parses if p[1].feats.get("Q_TYPE") == q_type
        ]
        assert len(matching) >= 1


class TestEarlierPhaseBaselinePreserved:
    """Earlier-phase declarative clauses unchanged — no phantom
    Q_TYPE=TAG."""

    @pytest.mark.parametrize("sentence", [
        "Maganda ang bata.",
        "Mas matalino siya.",
        "Pinakamaganda ang bahay.",
        "Kasingganda si Maria si Ana.",
        "Kumain ang aso ng isda.",
        "Hindi maganda ang bata.",
    ])
    def test_no_phantom_tag(self, sentence: str) -> None:
        parses = parse_text(sentence)
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("Q_TYPE") != "TAG"
