"""Phase 5h Commit 7: comparative-Q wrapper rule.

Roadmap §12.1 / plan-of-record §5.2, §6 Commit 7.

The Phase 5h Commit 3 ``mas`` PART (lex feat
``COMP_DEGREE: COMPARATIVE``) wraps a vague-Q head to produce a
comparative-Q. The new rule in ``cfg/nominal.py``:

    Q → PART[COMP_DEGREE=COMPARATIVE] Q[VAGUE=YES]

Equations: ``(↑) = ↓2`` (share inner Q's f-structure — PRED, LEMMA,
QUANT, VAGUE all percolate); ``(↑ COMP_DEGREE) = 'COMPARATIVE'``
writes COMPARATIVE onto the matrix; ``(↓1 COMP_DEGREE) =c
'COMPARATIVE'`` and ``(↓2 VAGUE) =c 'YES'`` are belt-and-braces
constraints (matching the Phase 5h Commit 3 / 5 leak-closing
pattern).

The wrapped Q rides into the existing Phase 5f Commit 15 vague-Q
NP-modifier rule (``NP → Q[VAGUE=YES] PART[LINK] N``) unchanged:
``mas maraming aklat`` parses as a Q-modified NP with a
COMP_DEGREE-marked Q head.

Restricting to ``Q[VAGUE=YES]`` keeps ``*mas tatlong aklat``
ungrammatical — cardinals carry ``CARDINAL: YES`` not ``VAGUE: YES``,
so the rule's category-pattern + ``=c`` constraint does not fire on
them. Cardinal comparison goes through the Phase 5f Commit 17
``COMP_PHRASE`` family (``higit sa N`` / ``kulang sa N``).

**Out of scope this commit**: predicative-Q clause (``Mas marami
ang aklat.`` "There are more books.") — the grammar lacks a
predicative-Q clause rule analogous to the Phase 5f Commit 4
predicative-cardinal rule. Adding one is a separate (deferred)
analytical decision; corpus-pressure dependent.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === NP-modifier composition: mas + Q[VAGUE] + linker + N =============


class TestComparativeQNpModifierObjPosition:
    """Comparative-Q NPs in OBJ position (ng-NP after a transitive
    AV verb). Multiple parses are expected from existing Phase 4
    case-order ambiguity (NP[GEN] / NP[NOM] freely orderable); we
    assert at least one parse exists with the right verbal PRED."""

    @pytest.mark.parametrize("sentence,verb_pred", [
        ("Bumili ng mas maraming aklat ang lalaki.",  "BUY"),
        ("Bumili ng mas kaunting aklat ang bata.",    "BUY"),
        ("Bumili ng mas maraming kanin ang lalaki.",  "BUY"),
        ("Bumili ng mas konting kanin ang bata.",     "BUY"),
    ])
    def test_mas_q_in_obj_np(
        self, sentence: str, verb_pred: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got 0"
        )
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED", "").startswith(verb_pred)
        assert fstruct.feats.get("POLARITY") is None


class TestComparativeQNpModifierSubjPosition:
    """Comparative-Q NPs in SUBJ position (ang-NP)."""

    @pytest.mark.parametrize("sentence,verb_pred", [
        ("Kumain ang mas maraming bata.",     "EAT"),
        ("Tumakbo ang mas maraming kabayo.",  "TAKBO"),
        ("Kumain ang mas kaunting bata.",     "EAT"),
    ])
    def test_mas_q_in_subj_np(
        self, sentence: str, verb_pred: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED", "").startswith(verb_pred)


# === Composition with Phase 5h Commit 4 kaysa ==========================


class TestComparativeQPlusKaysa:
    """The wrapped comparative-Q NP composes with the Phase 5h
    Commit 4 kaysa comparison-complement: ``Bumili ng mas maraming
    aklat ang lalaki kaysa sa babae`` "the man bought more books
    than the woman did"."""

    def test_mas_q_plus_kaysa(self) -> None:
        parses = parse_text(
            "Bumili ng mas maraming aklat ang lalaki kaysa sa babae."
        )
        assert len(parses) >= 1
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED", "").startswith("BUY")


# === Cardinal exclusion: mas does not wrap CARDINAL Q heads ===========


class TestNoMasOverCardinal:
    """The ``Q[VAGUE=YES]`` constraint prevents the wrapper from firing
    on cardinals (which carry ``CARDINAL: YES`` not ``VAGUE: YES``).
    ``*mas tatlo`` / ``*mas tatlong aklat`` are ungrammatical;
    cardinal comparison lives in the Phase 5f Commit 17
    ``COMP_PHRASE`` family (``higit sa N`` / ``kulang sa N``)."""

    @pytest.mark.parametrize("sentence", [
        "Bumili ng mas tatlong aklat ang lalaki.",
        "Bumili ng mas dalawang aklat ang lalaki.",
        "Kumain ang mas tatlong bata.",
    ])
    def test_mas_cardinal_rejected(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 0, (
            f"expected zero parses for {sentence!r} (cardinal "
            f"shouldn't take mas); got {len(parses)}"
        )


# === Multiple vague Q heads supported ==================================


class TestComparativeQAllVagueHeads:
    """All vague-Q heads (Phase 5f Commit 15) admit the wrapper:
    marami / kaunti / konti / kakaunti / ilan / iilan."""

    @pytest.mark.parametrize("q_surface,linker_form", [
        ("marami",   "maraming"),
        ("kaunti",   "kaunting"),
        ("konti",    "konting"),
        ("kakaunti", "kakaunting"),
    ])
    def test_each_vague_q_admits_wrapper(
        self, q_surface: str, linker_form: str
    ) -> None:
        sentence = f"Bumili ng mas {linker_form} aklat ang lalaki."
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r} "
            f"(vague-Q {q_surface}); got 0"
        )


# === Composition with negation =========================================


class TestComparativeQWithNegation:
    """Negation composes with comparative-Q: ``Hindi bumili ng mas
    maraming aklat ang lalaki`` "the man didn't buy more books"."""

    def test_hindi_plus_mas_q(self) -> None:
        parses = parse_text(
            "Hindi bumili ng mas maraming aklat ang lalaki."
        )
        assert len(parses) >= 1
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("POLARITY") == "NEG"
        assert fstruct.feats.get("PRED", "").startswith("BUY")


# === Phase 5h Commit 3 (mas + ADJ) baseline preserved ==================


class TestPhase5hCommit3BaselinePreserved:
    """The Phase 5h Commit 3 mas + ADJ wrapper continues to work —
    the new Q-wrapper is a sibling rule, not an overload, so ADJ
    targets aren't perturbed."""

    @pytest.mark.parametrize("sentence,adj_lemma", [
        ("Mas matalino siya.",         "talino"),
        ("Mas mabilis ang kabayo.",    "bilis"),
        ("Mas maganda ang bahay.",     "ganda"),
    ])
    def test_mas_adj_predicative_unchanged(
        self, sentence: str, adj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 1
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED") == "ADJ <SUBJ>"
        assert fstruct.feats.get("ADJ_LEMMA") == adj_lemma


# === Existing vague-Q NP-modifier (no mas) preserved ===================


class TestVagueQNpModifierUnchanged:
    """The Phase 5f Commit 15 vague-Q NP-modifier rule (without
    mas) continues to fire as before."""

    @pytest.mark.parametrize("sentence,verb_pred", [
        ("Bumili ng maraming aklat ang lalaki.",  "BUY"),
        ("Kumain ang maraming bata.",             "EAT"),
        ("Bumili ng kaunting aklat ang bata.",    "BUY"),
    ])
    def test_vague_q_np_modifier_unchanged(
        self, sentence: str, verb_pred: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ctree, fstruct, _astr, _diags = parses[0]
        assert fstruct.feats.get("PRED", "").startswith(verb_pred)
