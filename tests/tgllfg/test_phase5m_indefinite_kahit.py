"""Phase 5m Commit 8: indefinite ``kahit`` + wh productive.

Roadmap §12.1 / plan-of-record §5.4. Adds two parallel productive
rules in cfg/nominal.py:

    PRON → PART[LEMMA=kahit] PRON[WH=YES]   (IndefPRON)
        (↑) = ↓2
        ↓1 ∈ (↑ ADJUNCT)
        (↑ INDEF) = 'YES'
        (↓1 LEMMA) =c 'kahit'
        (↓2 WH) =c 'YES'

    ADV → PART[LEMMA=kahit] ADV[WH=YES]    (IndefADV)
        (same shape)

The compositions ``kahit sino`` / ``kahit ano`` produce a PRON
that inherits the wh-PRON's CASE feat and adds INDEF=YES. The
matrix PRON slots into existing NP-projection shells
(``NP[CASE=NOM] → PRON[CASE=NOM]`` etc.) without modification.

Disambiguation with Phase 5l concessive ``kahit S``: daughter
category is the discriminator (S → SubordClause path; PRON / ADV
→ Indef path). Chart is deterministic.

Coverage in this commit:
* ``kahit sino`` as SUBJ in V-initial frames.
* ``kahit ano`` as OBJ in AV-transitive frames.
* INDEF=YES propagates to the matrix NP slot.
* Phase 5l concessive ``Kahit umulan, …`` still parses (rule
  selection by daughter category preserved).

Plan §5.4 deferral surfaces:
* ``kahit saan`` / ``kahit kailan`` as clause-level adjuncts —
  wh-ADVs (saan / kailan) carry ADV_TYPE=LOCATION / TIME. There
  is no clause-final LOCATION/TIME-ADV adjunct rule today (Phase
  5f Commit 5 covers FREQUENCY only). The IndefADV rule produces
  ADV[INDEF=YES, ADV_TYPE=LOCATION/TIME], but no consumer admits
  it clause-finally. Pinned at 0-parse — Phase 5n debt.
* ``Kahit sino kumain.`` (kahit-X as fronted SUBJ before V) —
  needs an indef-PRON-as-fronted-topic rule analogous to Phase
  5l SubordClause-topic. Pinned at 0-parse — Phase 5n debt.

Reference: R&G 1981 §6.6.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === IndefPRON: kahit sino / kahit ano in NP slot =====================


KAHIT_PRON_AS_SUBJ = [
    # (sentence, pred_prefix, indef_lemma)
    ("Kumain kahit sino.",     "EAT",   "sino"),
    ("Pumupunta kahit sino.",  "PUNTA", "sino"),
    ("Tumakbo kahit sino.",    "TAKBO", "sino"),
]


def _find_arg_with_indef(fs, gf: str):
    """Return the GF f-structure if it carries INDEF=YES, else None."""
    arg = fs.feats.get(gf)
    if arg is None or not hasattr(arg, "feats"):
        return None
    if arg.feats.get("INDEF") == "YES":
        return arg
    return None


class TestKahitSinoAsSubject:
    """``kahit sino`` composes as a NOM-PRON SUBJ via the new
    IndefPRON rule + the existing NP[CASE=NOM] → PRON[CASE=NOM]
    shell."""

    @pytest.mark.parametrize(
        "sent,pred_prefix,indef_lemma", KAHIT_PRON_AS_SUBJ,
    )
    def test_kahit_sino_subj(
        self, sent: str, pred_prefix: str, indef_lemma: str,
    ) -> None:
        parses = parse_text(sent)
        assert len(parses) >= 1, f"expected ≥1 parse for {sent!r}"
        # Prefer the first parse where SUBJ has INDEF=YES.
        indef_subjs = [
            (p, _find_arg_with_indef(p[1], "SUBJ")) for p in parses
        ]
        indef_subjs = [(p, s) for p, s in indef_subjs if s is not None]
        assert indef_subjs, (
            f"expected ≥1 parse with INDEF SUBJ for {sent!r}"
        )
        _ct_fs_etc, subj = indef_subjs[0]
        assert subj.feats.get("LEMMA") == indef_lemma
        assert subj.feats.get("WH") == "YES"
        assert subj.feats.get("INDEF") == "YES"


class TestKahitAnoAsObject:
    """``kahit ano`` composes as an OBJ in AV-transitive frames
    (``Kumain siya ng kahit ano`` would be the GEN-marked form;
    the bare-OBJ form here uses NOM marking via the AV-trans
    pattern that admits unmarked NOM-pivot OBJs)."""

    def test_kahit_ano_in_obj(self) -> None:
        """``Kumain siya kahit ano.`` "She ate anything." — has
        multiple parses due to existing AV-trans/intrans
        ambiguity; verify at least one parse has OBJ with
        INDEF=YES, LEMMA=ano."""
        parses = parse_text("Kumain siya kahit ano.")
        assert len(parses) >= 1
        # Find a parse with OBJ having INDEF=YES.
        indef_objs = [
            _find_arg_with_indef(p[1], "OBJ") for p in parses
        ]
        indef_objs = [o for o in indef_objs if o is not None]
        assert indef_objs, (
            "expected ≥1 parse with OBJ.INDEF=YES for "
            "'Kumain siya kahit ano.'"
        )
        obj = indef_objs[0]
        assert obj.feats.get("LEMMA") == "ano"
        assert obj.feats.get("WH") == "YES"


# === Phase 5l concessive preservation =================================


class TestKahitConcessivePreserved:
    """The Phase 5l concessive ``kahit S`` SubordClause path is
    NOT broken by the new Phase 5m indef-builder rules. The
    chart picks by daughter category (S vs PRON/ADV)."""

    def test_kahit_s_concessive_still_parses(self) -> None:
        """``Kahit kumain si Maria, pumunta si Juan.`` "Even if
        Maria ate, Juan went." — still parses via Phase 5l
        SubordClause[CONC]."""
        parses = parse_text("Kahit kumain si Maria, pumunta si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        adj = fs.feats.get("ADJUNCT") or []
        # The SubordClause should appear as an ADJUNCT with
        # SUBORD_TYPE=CONC.
        conc_adjs = [
            m for m in adj
            if hasattr(m, "feats")
            and m.feats.get("SUBORD_TYPE") == "CONC"
        ]
        assert len(conc_adjs) == 1


# === Deferred: IndefADV (kahit saan / kahit kailan) ===================


DEFERRED_INDEF_ADV = [
    "Pumupunta siya kahit saan.",
    "Pumupunta siya kahit kailan.",
    "Tumakbo ang bata kahit saan.",
]


class TestIndefAdvDeferred:
    """``kahit saan`` / ``kahit kailan`` as clause-level adjuncts
    do NOT parse today: the IndefADV rule produces an
    ADV[INDEF=YES, ADV_TYPE=LOCATION/TIME], but there is no
    clause-final LOCATION/TIME ADV adjunct rule (Phase 5f Commit 5
    covers ADV_TYPE=FREQUENCY only).

    Pinned at 0-parse so closure during Phase 5n debt-clearing
    (when the missing clause-level ADV adjunct rules land) flips
    the test detectably.
    """

    @pytest.mark.parametrize("sent", DEFERRED_INDEF_ADV)
    def test_zero_parse_today(self, sent: str) -> None:
        parses = parse_text(sent)
        assert len(parses) == 0, (
            f"{sent!r} parsed unexpectedly — clause-level "
            f"LOCATION/TIME ADV adjunct rule has landed; close "
            f"the deferral and un-pin this test."
        )


# === Deferred: kahit-X as fronted SUBJ ================================


class TestKahitFrontedSubjectDeferred:
    """``Kahit sino kumain.`` (kahit-X as fronted SUBJ before V)
    does NOT parse today: there is no rule that admits an
    indefinite-PRON in pre-V topic position.

    Closure path (Phase 5n or beyond): an indef-PRON-as-topic
    rule analogous to Phase 5l SubordClause-topic
    (``S → SubordClause PART[LINK=AY] S`` with TOPIC + ADJUNCT
    overlay). For indefinite-PRON the ay-fronted form
    (``Kahit sino ay kumain.``) is the canonical structure.
    """

    def test_pre_v_kahit_sino_zero_parse(self) -> None:
        parses = parse_text("Kahit sino kumain.")
        assert len(parses) == 0
