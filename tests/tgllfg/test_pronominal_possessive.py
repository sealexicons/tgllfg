"""Phase 5c §7.8 follow-on: pronominal possessive.

Phase 4 §7.8 deferred ``ang aklat ko`` ("my book") because the
§7.3 Wackernagel pass moved the pronominal clitic ``ko`` out of
its post-noun possessive position into the post-V cluster, where
the grammar read it as an OBJ / OBJ-AGENT clitic. Phase 5c lifts
that deferral via a small context-aware fix to
:func:`tgllfg.clitics.reorder_clitics`: a pronominal clitic
immediately following a NOUN-reading token is left in place so
the existing ``NP[CASE=X] → NP[CASE=X] NP[CASE=GEN]`` possessive
rule can bind it as ``POSS``.

These tests cover:

* Placement unit tests: PRON-after-NOUN stays put;
  PRON-after-PART/VERB still moves; existing post-V clitic
  patterns unaffected.
* Parse-level: pronominal possessor on AV-OBJ (``ng libro ko``),
  on OV-pivot SUBJ (``ang isda ko``), all three persons singular
  and plural.
* Combinations: multiple clitics in one sentence (one moves, one
  stays); NEG + possessor; adverbial enclitic + possessor.
"""

from __future__ import annotations

from tgllfg.clitics import reorder_clitics
from tgllfg.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import tokenize


def _surfaces(analyses: list[list]) -> list[str]:
    return [cands[0].lemma if cands else "?" for cands in analyses]


def _reorder(text: str) -> list[str]:
    toks = tokenize(text)
    ml = analyze_tokens(toks)
    return _surfaces(reorder_clitics(ml))


def _find_obj_with_poss(text: str) -> FStructure | None:
    """Return the first parse's OBJ if its POSS is an FStructure
    with CASE=GEN, else None. Walks the n-best list — the parser
    produces multiple readings under structural ambiguity (whether
    the GEN-NP attaches as OBJ or as possessor of SUBJ); we want
    the parse where ``ng libro ko`` forms a possessive OBJ."""
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        obj = f.feats.get("OBJ")
        if isinstance(obj, FStructure):
            poss = obj.feats.get("POSS")
            if isinstance(poss, FStructure) and poss.feats.get("CASE") == "GEN":
                return obj
    return None


def _find_subj_with_pron_poss(text: str) -> FStructure | None:
    """Return the first parse's SUBJ if its POSS is the pronoun
    f-structure (CASE=GEN, NUM set, no MARKER since pronouns
    don't carry det markers). Distinguishes the pronoun-possessor
    case from a recursive ng-NP possessor."""
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        subj = f.feats.get("SUBJ")
        if isinstance(subj, FStructure):
            poss = subj.feats.get("POSS")
            if (
                isinstance(poss, FStructure)
                and poss.feats.get("CASE") == "GEN"
                and poss.feats.get("NUM") is not None
                and poss.feats.get("MARKER") is None
            ):
                return subj
    return None


# === Placement-pass unit tests ===========================================


class TestPlacementContextAware:
    """The pre-parse Wackernagel pass should leave a PRON-clitic
    in place when it immediately follows a NOUN."""

    def test_post_noun_pron_stays(self) -> None:
        # ``Kumain ang bata ng libro ko`` — `ko` follows `libro`
        # (NOUN), so it stays at its original position, not pulled
        # into the post-V cluster.
        out = _reorder("Kumain ang bata ng libro ko.")
        assert out == ["kain", "ang", "bata", "ng", "libro", "ko", "."]

    def test_post_noun_pron_stays_in_pivot(self) -> None:
        # ``Kinain ng aso ang isda ko`` — `ko` follows `isda` (NOUN).
        out = _reorder("Kinain ng aso ang isda ko.")
        assert out == ["kain", "ng", "aso", "ang", "isda", "ko", "."]

    def test_pre_v_pron_still_moves(self) -> None:
        # Regression: pre-V pronominal clitic still hoists into
        # the post-V cluster (preceded by PART, not NOUN).
        out = _reorder("Hindi mo kinain ang isda.")
        assert out == ["hindi", "kain", "mo", "ang", "isda", "."]

    def test_post_v_pron_still_clusters(self) -> None:
        # Regression: ``Kinain mo ang isda`` — `mo` immediately
        # after V is already in cluster position; placement leaves
        # it there. NOUN-after-PRON ordering doesn't trigger the
        # new rule (the rule fires on NOUN BEFORE PRON).
        out = _reorder("Kinain mo ang isda.")
        assert out == ["kain", "mo", "ang", "isda", "."]

    def test_one_clitic_moves_one_stays(self) -> None:
        # ``Kinain mo ang isda ko`` — `mo` is post-V (clusters,
        # no change), `ko` is post-NOUN `isda` (stays as possessor).
        out = _reorder("Kinain mo ang isda ko.")
        assert out == ["kain", "mo", "ang", "isda", "ko", "."]


# === Parse-level: 1SG / 2SG / 3SG GEN pronouns as possessor ==============


class TestPronominalPossessorAvObj:
    """Pronominal possessor on an AV-OBJ. ``ng libro X`` where X is
    any GEN pronoun should produce an OBJ with POSS = the pronoun's
    f-structure. The structurally-ambiguous parse where ``ng libro``
    instead attaches as possessor of SUBJ also surfaces; we just
    require at least one parse with the desired structure."""

    def test_ko_first_person_singular(self) -> None:
        obj = _find_obj_with_poss("Kumain ang bata ng libro ko.")
        assert obj is not None
        assert obj.feats["POSS"].feats.get("NUM") == "SG"

    def test_mo_second_person_singular(self) -> None:
        obj = _find_obj_with_poss("Kumain ang bata ng libro mo.")
        assert obj is not None
        assert obj.feats["POSS"].feats.get("NUM") == "SG"

    def test_niya_third_person_singular(self) -> None:
        obj = _find_obj_with_poss("Kumain ang bata ng libro niya.")
        assert obj is not None
        assert obj.feats["POSS"].feats.get("NUM") == "SG"

    def test_namin_first_person_plural_excl(self) -> None:
        obj = _find_obj_with_poss("Kumain ang bata ng libro namin.")
        assert obj is not None
        assert obj.feats["POSS"].feats.get("NUM") == "PL"

    def test_ninyo_second_person_plural(self) -> None:
        obj = _find_obj_with_poss("Kumain ang bata ng libro ninyo.")
        assert obj is not None
        assert obj.feats["POSS"].feats.get("NUM") == "PL"

    def test_nila_third_person_plural(self) -> None:
        obj = _find_obj_with_poss("Kumain ang bata ng libro nila.")
        assert obj is not None
        assert obj.feats["POSS"].feats.get("NUM") == "PL"


class TestPronominalPossessorOvPivot:
    """Pronominal possessor on the OV-pivot SUBJ."""

    def test_ko_on_ov_pivot(self) -> None:
        # ``Kinain ng aso ang isda ko`` — `isda` is the OV pivot
        # (NOM SUBJ); `ko` is its possessor.
        subj = _find_subj_with_pron_poss("Kinain ng aso ang isda ko.")
        assert subj is not None
        assert subj.feats["POSS"].feats.get("NUM") == "SG"
        assert subj.feats["POSS"].feats.get("CASE") == "GEN"

    def test_niya_on_ov_pivot(self) -> None:
        subj = _find_subj_with_pron_poss("Kinain ng aso ang isda niya.")
        assert subj is not None
        assert subj.feats["POSS"].feats.get("NUM") == "SG"


# === Combinations: clitic + possessor =====================================


class TestClitcPlusPossessor:
    """One pronoun moves, the other stays — both decisions made
    in the placement pass independently."""

    def test_ov_clitic_agent_plus_pronominal_possessor(self) -> None:
        # ``Kinain mo ang isda ko`` — `mo` moves to post-V cluster
        # (it IS the OBJ-AGENT clitic for the OV verb), `ko` stays
        # as possessor of `isda`.
        rs = parse_text("Kinain mo ang isda ko.")
        assert rs
        _, f, _, _ = rs[0]
        # mo as OBJ-AGENT (clause-level argument)
        obj_agent = f.feats.get("OBJ-AGENT")
        assert isinstance(obj_agent, FStructure)
        assert obj_agent.feats.get("CASE") == "GEN"
        # ko as possessor of pivot SUBJ
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        poss = subj.feats.get("POSS")
        assert isinstance(poss, FStructure)
        assert poss.feats.get("NUM") == "SG"

    def test_neg_plus_possessor(self) -> None:
        # ``Hindi kumain ang bata ng libro ko`` — `hindi` at
        # sentence-initial; `ko` stays as possessor.
        obj = _find_obj_with_poss("Hindi kumain ang bata ng libro ko.")
        assert obj is not None

    def test_adv_clitic_plus_possessor(self) -> None:
        # ``Kumain na ang bata ng libro ko`` — `na` moves to
        # clause-end; `ko` stays as possessor.
        obj = _find_obj_with_poss("Kumain na ang bata ng libro ko.")
        assert obj is not None
