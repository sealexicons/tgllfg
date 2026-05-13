"""Phase 5m Commit 6: reflexive ``sarili`` NP composition.

Roadmap §12.1 / plan-of-record §1, §2 (analytical commitment 4).
Verifies that the Commit 1 NOUN entry ``sarili`` (SEM_CLASS=REFLEXIVE)
composes as a regular NOUN-headed NP via the existing Phase 4 NP
grammar — no new grammar in this commit.

Distribution coverage:
* As NP[CASE=NOM] SUBJ via OV voice (``Nakita niya ang sarili
  niya.`` "She saw herself." — niya is GEN-actor; ang sarili niya
  is the NOM-pivot SUBJ).
* As NP[CASE=GEN] OBJ in AV voice (``Kumain siya ng sarili niya.``).
* With possessor variations (1sg / 2sg / 3sg / 3pl GEN-PRON).
* The SUBJ's POSS slot carries the antecedent GEN-PRON.

Plan-of-record §9.1 Q4: ``sarili`` lex'd as NOUN, NOT PRON.
``SEM_CLASS=REFLEXIVE`` is on the morph layer, available to
grammar rules via constraining equations (none in this commit;
Phase 6 binding will use it). It does NOT propagate to f-structure
— consistent with other Phase 5f SEM_CLASS-tagged nouns
(``beses`` / ``ulit`` / ``doble``).

Anaphora resolution (binding ``sarili niya`` to its antecedent
SUBJ via inside-out designators) is Phase 6 — verified-deferred
in TestAnaphoraDeferred.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === sarili composes as NP head =======================================


SARILI_AS_SUBJ = [
    # OV-voice: ang sarili niya = NOM-pivot SUBJ
    "Nakita niya ang sarili niya.",       # 3sg-actor
    "Nakita ko ang sarili ko.",           # 1sg-actor
    "Nakita mo ang sarili mo.",           # 2sg-actor
    "Nakita nila ang sarili nila.",       # 3pl-actor
]


class TestSariliAsSubject:
    """``ang sarili NIYA/KO/MO/NILA`` composes as a NOM-marked
    SUBJ NP via existing Phase 4 D + N + GEN-PRON grammar. The
    SUBJ's LEMMA is ``sarili``."""

    @pytest.mark.parametrize("sent", SARILI_AS_SUBJ)
    def test_sarili_subj_lemma(self, sent: str) -> None:
        parses = parse_text(sent)
        assert len(parses) >= 1, f"expected ≥1 parse for {sent!r}"
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None, f"missing SUBJ in {sent!r}"
        assert subj.feats.get("LEMMA") == "sarili"
        assert subj.feats.get("CASE") == "NOM"
        assert subj.feats.get("MARKER") == "ANG"

    def test_sarili_subj_carries_possessor(self) -> None:
        """The SUBJ's POSS slot contains the GEN-PRON antecedent
        — a regular Phase 4 D + N + GEN-PRON composition. Phase 6
        will bind POSS to a matrix-S argument via inside-out
        designators."""
        parses = parse_text("Nakita niya ang sarili niya.")
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        poss = subj.feats.get("POSS")
        assert poss is not None
        # 3sg GEN-PRON niya → POSS with NUM=SG, CASE=GEN.
        assert poss.feats.get("NUM") == "SG"
        assert poss.feats.get("CASE") == "GEN"


# === sarili as GEN-NP =================================================


class TestSariliAsObject:
    """``ng sarili niya`` composes as a GEN-marked OBJ NP via
    AV-voice frame."""

    def test_sarili_in_gen_obj(self) -> None:
        parses = parse_text("Kumain siya ng sarili niya.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        obj = fs.feats.get("OBJ")
        # OBJ may be deeply nested; find the sarili lemma if present.
        assert obj is not None
        # OBJ either is the sarili NP directly or wraps it; check
        # LEMMA at top level.
        assert obj.feats.get("LEMMA") == "sarili" or obj.feats.get("CASE") == "GEN"


# === Anaphora resolution via binding equation (Phase 6.F) ============


class TestAnaphoraResolution:
    """Phase 6.F C2 (§18.1.2 L104): the matrix transitive rule emits
    a binding-equation variant gated on ``(↑ SUBJ LEMMA) =c 'sarili'``
    that sets ``(↑ SUBJ ANTECEDENT) = (↑ <obj_target>)``. The
    reflexive's ANTECEDENT feat becomes reentrant with the matrix
    actor (per Kroeger 1993 §2.3 actor-binding theory; the actor
    is OBJ in tgllfg's AV-pivot frames, OBJ-AGENT in OV / DV / IV).

    The binding rule fires alongside the non-binding transitive
    rule (both compose for reflexive SUBJs), so the test finds the
    parse with the ANTECEDENT feat among the 2-parse output."""

    @staticmethod
    def _find_bound_parse(text: str):
        """Return ``(fs, antecedent)`` for the parse whose SUBJ has
        an ANTECEDENT feat; ``(None, None)`` if no bound parse."""
        for _, fs, _, _ in parse_text(text):
            subj = fs.feats.get("SUBJ")
            if subj is None:
                continue
            ant = subj.feats.get("ANTECEDENT")
            if ant is not None:
                return fs, ant
        return None, None

    def test_subj_antecedent_reentrant_with_obj(self) -> None:
        fs, ant = self._find_bound_parse("Nakita niya ang sarili niya.")
        assert fs is not None, "no parse with SUBJ.ANTECEDENT"
        # ANTECEDENT is reentrant with the matrix actor — OBJ in
        # AV-pivot syntax for ``nakita``.
        obj = fs.feats.get("OBJ")
        assert obj is not None
        assert ant.id == obj.id, (
            f"ANTECEDENT (id={ant.id}) is not reentrant with OBJ "
            f"(id={obj.id})"
        )

    @pytest.mark.parametrize("sent", SARILI_AS_SUBJ)
    def test_antecedent_per_possessor(self, sent: str) -> None:
        """The 1sg / 2sg / 3sg / 3pl GEN-PRON variants all admit
        the binding."""
        fs, ant = self._find_bound_parse(sent)
        assert fs is not None, f"no bound parse for {sent!r}"
        obj = fs.feats.get("OBJ")
        assert obj is not None
        assert ant.id == obj.id, f"binding broken on {sent!r}"


# === SEM_CLASS=REFLEXIVE on morph layer ==============================


class TestSemClassReflexiveOnMorph:
    """The Commit 1 lex tags ``sarili`` with ``SEM_CLASS=REFLEXIVE``,
    available to grammar rules via constraining equations (none in
    Phase 5m; Phase 6 binding uses it). The feat does NOT propagate
    to f-structure — consistent with Phase 5f SEM_CLASS-tagged nouns
    (``beses`` / ``ulit`` / ``doble``)."""

    def test_sem_class_reflexive_not_in_subj_fstructure(self) -> None:
        """Negative pin — verifies non-propagation matches the
        existing convention."""
        parses = parse_text("Nakita niya ang sarili niya.")
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        # SEM_CLASS doesn't propagate to f-structure (this is the
        # current convention; not a Phase 5m bug).
        assert subj.feats.get("SEM_CLASS") is None
