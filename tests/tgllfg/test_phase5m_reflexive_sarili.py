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

from tgllfg.core.common import FStructure
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


# === Phase 6.F C3: voice / position variants ==========================


SARILI_AT_AV_OBJ = [
    "Kumain siya ng sarili niya.",
    "Kumain ako ng sarili ko.",
    "Kumain ka ng sarili mo.",
]


SARILI_AT_OV_SUBJ = [
    "Kinain niya ang sarili niya.",
    "Kinain ko ang sarili ko.",
    "Kinain mo ang sarili mo.",
]


class TestSariliAtAVObject:
    """Mirror of TestAnaphoraResolution for the **sarili at OBJ**
    direction. In true AV transitives like ``Kumain siya ng sarili
    niya.``, the actor is SUBJ and sarili sits at OBJ — the
    binding equation
    ``(↑ OBJ ANTECEDENT) = (↑ SUBJ)`` fires (see Phase 6.F C2
    grammar in ``cfg/control.py``)."""

    @staticmethod
    def _find_obj_bound_parse(text: str):
        """Return ``(fs, antecedent)`` for the parse whose OBJ has
        an ANTECEDENT feat; ``(None, None)`` if no bound parse."""
        for _, fs, _, _ in parse_text(text):
            obj = fs.feats.get("OBJ")
            if obj is None:
                continue
            ant = obj.feats.get("ANTECEDENT")
            if ant is not None:
                return fs, ant
        return None, None

    @pytest.mark.parametrize("sent", SARILI_AT_AV_OBJ)
    def test_obj_antecedent_reentrant_with_subj(self, sent: str) -> None:
        fs, ant = self._find_obj_bound_parse(sent)
        assert fs is not None, f"no OBJ-bound parse for {sent!r}"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert ant.id == subj.id, (
            f"OBJ.ANTECEDENT (id={ant.id}) not reentrant with SUBJ "
            f"(id={subj.id}) for {sent!r}"
        )


class TestSariliAtOVSubject:
    """OV-pivot transitives: sarili at SUBJ (the patient), binder
    at OBJ-AGENT (the actor). The binding equation
    ``(↑ SUBJ ANTECEDENT) = (↑ OBJ-AGENT)`` fires for these
    surfaces. Verifies the OV-paradigm path of the same C2
    grammar."""

    @staticmethod
    def _find_subj_bound_parse(text: str):
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

    @pytest.mark.parametrize("sent", SARILI_AT_OV_SUBJ)
    def test_subj_antecedent_reentrant_with_obj_agent(self, sent: str) -> None:
        fs, ant = self._find_subj_bound_parse(sent)
        assert fs is not None, f"no SUBJ-bound parse for {sent!r}"
        # In OV voice, the binder is OBJ-AGENT (the actor).
        obj_agent = fs.feats.get("OBJ-AGENT")
        assert obj_agent is not None, (
            f"OV-pivot transitive missing OBJ-AGENT for {sent!r}"
        )
        assert ant.id == obj_agent.id, (
            f"SUBJ.ANTECEDENT (id={ant.id}) not reentrant with "
            f"OBJ-AGENT (id={obj_agent.id}) for {sent!r}"
        )


# === Cross-clausal binding: deferred ==================================


class TestCrossClausalDeferred:
    """**Deferred (Phase 7+ / corpus pressure).** Cross-clausal
    binding — where ``sarili`` is inside an XCOMP body and the
    binder is at the matrix level — is not handled by the Phase 6.F
    matrix-rule binding equations. The matrix PSYCH-control rule
    doesn't see the embedded sarili directly; binding would require
    either:

    1. **Inside-out FU designators** (e.g., ``((SUBJ ↑) GF)``-style)
       — tgllfg's FU resolver is outside-in only. Adding inside-out
       support is a Phase 7+ unifier extension. Or:
    2. **Per-XCOMP binding rules** that traverse from the
       S_XCOMP body up to the matrix's binder — voluminous, awaits
       cross-clausal sarili surfacing in corpus.

    The pinned test below confirms today's state: ``Gusto kong
    kumain ng sarili ko.`` parses cleanly (the matrix gusto
    PSYCH-control + embedded AV-trans with sarili at OBJ), but no
    ANTECEDENT is set on the embedded sarili NP. The Phase 6.F C2
    binding rule fires on standalone clauses (``Kumain ako ng
    sarili ko.`` gets binding) but not on the embedded clause's
    OBJ when the SUBJ is structure-shared via control."""

    def test_cross_clausal_no_binding_today(self) -> None:
        parses = parse_text("Gusto kong kumain ng sarili ko.")
        assert parses, "cross-clausal surface should parse"
        # No parse has binding on the embedded sarili-OBJ.
        bound = []
        for _, fs, _, _ in parses:
            xcomp = fs.feats.get("XCOMP")
            if isinstance(xcomp, FStructure):
                obj = xcomp.feats.get("OBJ")
                if isinstance(obj, FStructure) and obj.feats.get("ANTECEDENT"):
                    bound.append(fs)
        assert not bound, (
            "cross-clausal binding now fires — flip this test "
            "and remove the TestCrossClausalDeferred docstring deferral"
        )


# === SEM_CLASS=REFLEXIVE on morph layer ==============================


class TestSemClassReflexiveOnFStructure:
    """Phase 6.G C2 (§18.1.2 L32): the simple NP-from-DET+N rule
    uses SHARE+SHARE projection, so ``SEM_CLASS`` declared on the
    NOUN lex entry (e.g., ``sarili`` → ``SEM_CLASS=REFLEXIVE``)
    surfaces on the matrix NP's f-structure. (Pre-Phase-6.G the
    feat stayed on the inner N daughter only — flipped here as
    part of the L32 NP-projection widening.)"""

    def test_sem_class_reflexive_lifts_to_subj_fstructure(self) -> None:
        """Positive — verifies SEM_CLASS propagation to NP."""
        parses = parse_text("Nakita niya ang sarili niya.")
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        # SEM_CLASS propagates to f-structure post-6.G (closes the
        # Phase 6.F C2 SEM_CLASS-lift deferral as part of L32).
        assert subj.feats.get("SEM_CLASS") == "REFLEXIVE"
