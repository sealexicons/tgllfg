# tgllfg/cfg/control.py

"""Control rules: ``S_XCOMP`` complement, raising, control wrap.

Holds every rule that participates in the matrix-XCOMP control /
raising analysis. After the post-Phase-5f grammar split (see
``docs/refactor-grammar-package.md``) this module owns:

* Phase 4 §7.6 control complement (``S_XCOMP``) — the
  AV-restricted SUBJ-gapped non-terminal that serves as the XCOMP
  of a control verb. The Phase 4 frames are AV-only; the Phase 5c
  follow-on adds non-AV variants where the controllee is the
  actor's typed GF (``OBJ-AGENT`` under the Phase 5b
  OBJ-θ-in-grammar alignment).
* Phase 5d Commit 7 raising inside a control complement — when
  the embedded clause licenses raising, the matrix wrap rule
  inherits the raised argument from the inner ``S_XCOMP``.
* Phase 4 §7.6 control wrap rules — the matrix templates that
  attach an ``S_XCOMP`` to a control verb plus its arguments and
  bind matrix ``SUBJ`` to ``XCOMP REL-PRO``. Discriminated by
  ``CTRL_CLASS ∈ {PSYCH, INTRANS, TRANS}`` carried on the V's
  morph analysis.

The composer in :mod:`tgllfg.cfg.grammar` calls this registrar
sixth, after np / clause / clitic / negation / extraction, and
before discourse — see the plan's "Migration strategy" §H.
"""

from __future__ import annotations

from ._helpers import _eqs
from .grammar import Rule


def register_rules(rules: list[Rule]) -> None:
    """Append the control-area rules in source order."""
    # --- Phase 4 §7.6: control complement (S_XCOMP) ---
    #
    # ``S_XCOMP`` is the SUBJ-gapped clause that serves as the
    # XCOMP of a control verb. The original Phase 4 frames are
    # AV-only: the controllee is the actor, which is SUBJ in AV.
    # Phase 5c §7.6 follow-on adds non-AV variants where the
    # controllee is the actor's *typed* GF — ``OBJ-AGENT`` under
    # the Phase 5b OBJ-θ-in-grammar alignment. The matrix wrap
    # rule's ``(↑ SUBJ) = (↑ XCOMP REL-PRO)`` is unchanged; only
    # the embedded clause's REL-PRO routing differs per voice.
    #
    # AV frames: REL-PRO routes to SUBJ.
    rules.append(Rule(
        "S_XCOMP",
        ["V[VOICE=AV]"],
        _eqs("(↑ SUBJ) = (↑ REL-PRO)"),
    ))
    rules.append(Rule(
        "S_XCOMP",
        ["V[VOICE=AV]", "NP[CASE=GEN]"],
        _eqs("(↑ OBJ) = ↓2", "(↑ SUBJ) = (↑ REL-PRO)"),
    ))
    rules.append(Rule(
        "S_XCOMP",
        ["V[VOICE=AV]", "NP[CASE=GEN]", "NP[CASE=DAT]"],
        _eqs(
            "(↑ OBJ) = ↓2",
            "↓3 ∈ (↑ ADJUNCT)",
            "(↑ SUBJ) = (↑ REL-PRO)",
        ),
    ))
    # Phase 5c §7.6 follow-on: non-AV embedded clauses, where
    # REL-PRO routes to ``OBJ-AGENT`` (the actor's typed GF in
    # OV / DV / IV). The patient / recipient / theme NOM-pivot
    # is overt; the actor is the gap. CAUS=NONE on OV
    # discriminates against pa-OV (CAUS=DIRECT) where the typed
    # slot would be ``OBJ-CAUSER``. IV is admitted without an
    # APPL constraint (Phase 5d Commit 9) so any applicative —
    # CONVEY (bare i-) / BEN (ipag-) / INSTR (ipang-) /
    # REASON (ika-) — fires; the actor is OBJ-AGENT in all
    # variants.
    rules.append(Rule(
        "S_XCOMP",
        ["V[VOICE=OV, CAUS=NONE]", "NP[CASE=NOM]"],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ-AGENT) = (↑ REL-PRO)",
        ),
    ))
    rules.append(Rule(
        "S_XCOMP",
        ["V[VOICE=DV]", "NP[CASE=NOM]"],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ-AGENT) = (↑ REL-PRO)",
        ),
    ))
    rules.append(Rule(
        "S_XCOMP",
        ["V[VOICE=IV]", "NP[CASE=NOM]"],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ-AGENT) = (↑ REL-PRO)",
        ),
    ))
    # Phase 5d Commit 9: IV multi-GEN (3-arg) under control.
    # Phase 5b admitted top-level multi-GEN-NP IV-BEN frames
    # (``Ipinaggawa ng nanay ng silya ang kapatid``) with three
    # NPs: pivot (BENEFICIARY) + AGENT + PATIENT. Under control,
    # the actor (OBJ-AGENT, the agent slot) is the gap; the
    # surface form has SUBJ pivot + GEN-PATIENT and the
    # GEN-AGENT is suppressed. Both NP orders admitted.
    # Generalises across IV-BEN / IV-INSTR / IV-REASON because
    # the existing top-level multi-GEN rules at
    # ``v_iv = "V[VOICE=IV]"`` (no APPL filter) already do.
    rules.append(Rule(
        "S_XCOMP",
        ["V[VOICE=IV]", "NP[CASE=NOM]", "NP[CASE=GEN]"],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ-PATIENT) = ↓3",
            "(↑ OBJ-AGENT) = (↑ REL-PRO)",
        ),
    ))
    rules.append(Rule(
        "S_XCOMP",
        ["V[VOICE=IV]", "NP[CASE=GEN]", "NP[CASE=NOM]"],
        _eqs(
            "(↑ SUBJ) = ↓3",
            "(↑ OBJ-PATIENT) = ↓2",
            "(↑ OBJ-AGENT) = (↑ REL-PRO)",
        ),
    ))
    # Phase 5d Commit 8: pa-OV / pa-DV (CAUS=DIRECT) embedded
    # under control. In monoclausal direct causatives the actor
    # is the typed ``OBJ-CAUSER`` slot (not ``OBJ-AGENT``), so
    # under control the controllee is OBJ-CAUSER. The Phase 5c
    # non-AV S_XCOMP rules above explicitly require ``CAUS=NONE``
    # to keep them out of the actor-extraction path; this block
    # adds the parallel ``CAUS=DIRECT`` variants that route
    # REL-PRO to OBJ-CAUSER.
    #
    # Two-argument pa-OV (causee + gap-causer) — the patient is
    # absent on the surface (lex entry's a-structure permits
    # this).
    rules.append(Rule(
        "S_XCOMP",
        ["V[VOICE=OV, CAUS=DIRECT]", "NP[CASE=NOM]"],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
        ),
    ))
    # Three-argument pa-OV (causee + patient + gap-causer);
    # NP-order is free post-V so both orders.
    rules.append(Rule(
        "S_XCOMP",
        [
            "V[VOICE=OV, CAUS=DIRECT]",
            "NP[CASE=NOM]",
            "NP[CASE=GEN]",
        ],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ-PATIENT) = ↓3",
            "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
        ),
    ))
    rules.append(Rule(
        "S_XCOMP",
        [
            "V[VOICE=OV, CAUS=DIRECT]",
            "NP[CASE=GEN]",
            "NP[CASE=NOM]",
        ],
        _eqs(
            "(↑ SUBJ) = ↓3",
            "(↑ OBJ-PATIENT) = ↓2",
            "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
        ),
    ))
    # Two-argument pa-DV (location/recipient pivot + gap-causer)
    # — Phase 5d Commit 2's pa-...-an cells. Pivot is the
    # location (ang nanay = "to mom"), causer is gap. The
    # patient is absent from the embedded clause's surface.
    rules.append(Rule(
        "S_XCOMP",
        ["V[VOICE=DV, CAUS=DIRECT]", "NP[CASE=NOM]"],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
        ),
    ))
    # Phase 5e Commit 10: three-argument pa-DV under control.
    # Mirrors the three-argument pa-OV S_XCOMP rules above, but
    # with the pa-DV pivot (LOCATION) at NOM and an overt
    # OBJ-PATIENT GEN-NP retained. Both NP orders.
    rules.append(Rule(
        "S_XCOMP",
        [
            "V[VOICE=DV, CAUS=DIRECT]",
            "NP[CASE=NOM]",
            "NP[CASE=GEN]",
        ],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ-PATIENT) = ↓3",
            "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
        ),
    ))
    rules.append(Rule(
        "S_XCOMP",
        [
            "V[VOICE=DV, CAUS=DIRECT]",
            "NP[CASE=GEN]",
            "NP[CASE=NOM]",
        ],
        _eqs(
            "(↑ SUBJ) = ↓3",
            "(↑ OBJ-PATIENT) = ↓2",
            "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
        ),
    ))
    # Phase 5c §7.6 follow-on (Commit 3): nested control
    # complements (long-distance control). When a control verb
    # is itself embedded inside another control verb's XCOMP,
    # its SUBJ is the gap (= the outer controller), so the
    # NOM- or GEN-marked SUBJ NP that the matrix wrap rule
    # would supply is absent. The OBJ-AGENT in TRANS remains
    # overt — it's the controller (forcer/orderer), not the
    # controllee. Each nested S_XCOMP rule:
    #   - binds its own SUBJ to its own REL-PRO (it is the gap);
    #   - chains its XCOMP slot to the inner S_XCOMP;
    #   - propagates the controller from its SUBJ to the inner
    #     XCOMP's REL-PRO.
    # Composing these equations across depth-N gives a single
    # f-node shared across SUBJ slots at every level — finite-
    # depth control without functional uncertainty.
    for link in ("NA", "NG"):
        # PSYCH nested: V[CTRL_CLASS=PSYCH] PART S_XCOMP
        rules.append(Rule(
            "S_XCOMP",
            [
                "V[CTRL_CLASS=PSYCH]",
                f"PART[LINK={link}]",
                "S_XCOMP",
            ],
            _eqs(
                "(↑ SUBJ) = (↑ REL-PRO)",
                "(↑ XCOMP) = ↓3",
                "(↑ SUBJ) = (↑ XCOMP REL-PRO)",
            ),
        ))
        # INTRANS nested: V[CTRL_CLASS=INTRANS] PART S_XCOMP
        rules.append(Rule(
            "S_XCOMP",
            [
                "V[CTRL_CLASS=INTRANS]",
                f"PART[LINK={link}]",
                "S_XCOMP",
            ],
            _eqs(
                "(↑ SUBJ) = (↑ REL-PRO)",
                "(↑ XCOMP) = ↓3",
                "(↑ SUBJ) = (↑ XCOMP REL-PRO)",
            ),
        ))
        # TRANS nested: V[CTRL_CLASS=TRANS] NP[CASE=GEN] PART
        # S_XCOMP. The GEN-NP is the forcer / orderer, mapped
        # to OBJ-AGENT (the typed slot since Phase 5b
        # OBJ-θ-in-grammar). The NOM-marked forcee that the
        # matrix wrap rule would supply is the gap.
        rules.append(Rule(
            "S_XCOMP",
            [
                "V[CTRL_CLASS=TRANS]",
                "NP[CASE=GEN]",
                f"PART[LINK={link}]",
                "S_XCOMP",
            ],
            _eqs(
                "(↑ OBJ-AGENT) = ↓2",
                "(↑ SUBJ) = (↑ REL-PRO)",
                "(↑ XCOMP) = ↓4",
                "(↑ SUBJ) = (↑ XCOMP REL-PRO)",
            ),
        ))
    # Inner negation under control: ``Gusto kong hindi kumain``
    # — the embedded clause is negated. Mirrors the S / S_GAP
    # negation rule shape.
    rules.append(Rule(
        "S_XCOMP",
        ["PART[POLARITY=NEG]", "S_XCOMP"],
        ["(↑) = ↓2", "(↑ POLARITY) = 'NEG'"],
    ))


    # --- Phase 5d Commit 7: raising inside a control complement ---
    #
    # ``Gusto kong mukhang kumakain`` ("I want to seem to be
    # eating"): a control verb's XCOMP is itself a raising
    # structure. The Phase 5c §7.6 follow-on (Commit 5) raising
    # rules sit at the ``S`` level; control complements are at
    # the ``S_XCOMP`` level (SUBJ-gapped). This block adds the
    # ``S_XCOMP``-level raising variants so the matrix control
    # wrap rule's ``(↑ SUBJ) = (↑ XCOMP REL-PRO)`` propagates the
    # controller through the raising chain into the embedded
    # action's SUBJ.
    #
    # Equations compose three identifications at this S_XCOMP
    # level:
    #
    #   * ``(↑ XCOMP) = ↓N`` — the inner clause is the raising
    #     verb's XCOMP.
    #   * ``(↑ SUBJ) = (↑ XCOMP SUBJ)`` — raising structure-share.
    #   * ``(↑ SUBJ) = (↑ REL-PRO)`` — S_XCOMP convention so the
    #     matrix control rule's REL-PRO routing fires.
    #
    # Together: outer.SUBJ = THIS.REL-PRO = THIS.SUBJ
    # = THIS.XCOMP.SUBJ = innermost-action.SUBJ. Recursing
    # through ``S_XCOMP`` lets raising chains compose under
    # control (``Gusto kong mukhang bakang kumakain``).
    for link in ("NA", "NG"):
        rules.append(Rule(
            "S_XCOMP",
            [
                "V[CTRL_CLASS=RAISING]",
                f"PART[LINK={link}]",
                "S_XCOMP",
            ],
            _eqs(
                "(↑ XCOMP) = ↓3",
                "(↑ SUBJ) = (↑ XCOMP SUBJ)",
                "(↑ SUBJ) = (↑ REL-PRO)",
            ),
        ))
    rules.append(Rule(
        "S_XCOMP",
        ["V[CTRL_CLASS=RAISING_BARE]", "S_XCOMP"],
        _eqs(
            "(↑ XCOMP) = ↓2",
            "(↑ SUBJ) = (↑ XCOMP SUBJ)",
            "(↑ SUBJ) = (↑ REL-PRO)",
        ),
    ))


    # --- Phase 4 §7.6: control wrap rules ---
    #
    # Three control patterns, all using SUBJ-control: the matrix
    # SUBJ binds the embedded SUBJ via the wrap rule's
    # ``(↑ SUBJ) = (↑ XCOMP REL-PRO)`` equation. Inside S_XCOMP,
    # the gap is bound by ``(↑ SUBJ) = (↑ REL-PRO)``, so the
    # composition makes matrix.SUBJ = matrix.XCOMP.SUBJ. No
    # cycle — matrix and XCOMP are sibling f-nodes; the shared
    # SUBJ is referenced from both but doesn't contain either.
    #
    # The control verb's class is selected by ``CTRL_CLASS`` on
    # the V token (set by the morph analyzer from the root's
    # per-root feats / from the particles.yaml entry).
    #
    # **Psych predicates** (gusto, ayaw, kaya): GEN-marked
    # experiencer is matrix SUBJ. PRED ``WANT <SUBJ, XCOMP>``.
    # The deviation from the otherwise-uniform NOM→SUBJ mapping
    # is documented in docs/analysis-choices.md "Phase 4 §7.6".
    for link in ("NA", "NG"):
        rules.append(Rule(
            "S",
            [
                "V[CTRL_CLASS=PSYCH]",
                "NP[CASE=GEN]",
                f"PART[LINK={link}]",
                "S_XCOMP",
            ],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ XCOMP) = ↓4",
                "(↑ SUBJ) = (↑ XCOMP REL-PRO)",
            ),
        ))

    # Phase 5i Commit 8: indirect-question embedding under KNOW-
    # class predicates (``alam``). The matrix predicate takes a
    # CLOSED sentential complement (COMP), not an open XCOMP — the
    # embedded clause has its own SUBJ (the wh-pivot of the
    # indirect-Q), so there's no SUBJ-control / linker. The
    # complement itself is an ``S_INTERROG_COMP`` non-terminal:
    # the ``kung`` complementizer plus an embedded wh-Q clause.
    # Roadmap §12.1 / plan-of-record §5.7.
    #
    # Analytical note: the plan-of-record §5.7 used ``XCOMP`` in
    # the LHS / equations loosely (re-using the open-complement
    # name). The actual LFG slot is ``COMP`` because the embedded
    # clause is not subject-controlled — a closed complement, with
    # its own SUBJ. PRED template ``KNOW <SUBJ, COMP>`` reflects
    # this. Documented in docs/analysis-choices.md "Phase 5i §5.7".
    #
    # The S_INTERROG_COMP non-terminal lifts its inner S
    # f-structure (``(↑) = ↓2``) and adds ``COMP_TYPE=INTERROG``;
    # the inner S must already carry ``Q_TYPE=WH`` (from a Phase
    # 5i Commit 2 / 4 / 6 wh-fronting / wh-N-cleft rule). The
    # belt-and-braces ``=c`` constraints lock down both the
    # complementizer's COMP_TYPE and the inner clause's Q_TYPE,
    # closing any non-conflict-matcher leaks.
    rules.append(Rule(
        "S_INTERROG_COMP",
        ["PART[COMP_TYPE=INTERROG]", "S[Q_TYPE=WH]"],
        [
            "(↑) = ↓2",
            "(↑ COMP_TYPE) = 'INTERROG'",
            "(↓1 COMP_TYPE) =c 'INTERROG'",
            "(↓2 Q_TYPE) =c 'WH'",
        ],
    ))
    # Matrix wrap: ``Alam ko + S_INTERROG_COMP``. The GEN-NP
    # experiencer is matrix SUBJ (the same NOM→SUBJ deviation as
    # PSYCH); the indirect-Q clause is matrix COMP. No linker
    # between matrix and complement — ``alam`` is a stative
    # predicate and ``kung`` is the complementizer. The
    # ``CTRL_CLASS=KNOW`` filter keeps gusto / ayaw / kaya from
    # cross-firing into this rule (their CTRL_CLASS=PSYCH is
    # distinct).
    rules.append(Rule(
        "S",
        [
            "V[CTRL_CLASS=KNOW]",
            "NP[CASE=GEN]",
            "S_INTERROG_COMP",
        ],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ COMP) = ↓3",
            "(↓1 CTRL_CLASS) =c 'KNOW'",
            "(↓3 COMP_TYPE) =c 'INTERROG'",
        ),
    ))

    # **Intransitive control** (payag): NOM-marked agent is
    # matrix SUBJ; AV verb. PRED ``AGREE <SUBJ, XCOMP>``.
    for link in ("NA", "NG"):
        rules.append(Rule(
            "S",
            [
                "V[CTRL_CLASS=INTRANS]",
                "NP[CASE=NOM]",
                f"PART[LINK={link}]",
                "S_XCOMP",
            ],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ XCOMP) = ↓4",
                "(↑ SUBJ) = (↑ XCOMP REL-PRO)",
            ),
        ))

    # **Transitive control** (pilit OV, utos DV): NOM-marked
    # pivot is matrix SUBJ (forcee / orderee); GEN-marked agent
    # is matrix OBJ-AGENT (typed under the Phase 5b
    # OBJ-θ-in-grammar alignment). The pivot controls XCOMP.
    # PRED ``FORCE <SUBJ, OBJ-AGENT, XCOMP>``. Both NOM-GEN and
    # GEN-NOM orderings are admitted, mirroring the regular
    # transitive frames' freedom.
    for link in ("NA", "NG"):
        # GEN-NOM order
        rules.append(Rule(
            "S",
            [
                "V[CTRL_CLASS=TRANS]",
                "NP[CASE=GEN]",
                "NP[CASE=NOM]",
                f"PART[LINK={link}]",
                "S_XCOMP",
            ],
            _eqs(
                "(↑ OBJ-AGENT) = ↓2",
                "(↑ SUBJ) = ↓3",
                "(↑ XCOMP) = ↓5",
                "(↑ SUBJ) = (↑ XCOMP REL-PRO)",
            ),
        ))
        # NOM-GEN order
        rules.append(Rule(
            "S",
            [
                "V[CTRL_CLASS=TRANS]",
                "NP[CASE=NOM]",
                "NP[CASE=GEN]",
                f"PART[LINK={link}]",
                "S_XCOMP",
            ],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ-AGENT) = ↓3",
                "(↑ XCOMP) = ↓5",
                "(↑ SUBJ) = (↑ XCOMP REL-PRO)",
            ),
        ))

    # Phase 5c §7.6 follow-on (Commit 5): raising verbs.
    # ``Mukhang kumakain ang bata`` "the child seems to be
    # eating". The matrix has no thematic SUBJ; its SUBJ is
    # structure-shared with the embedded clause's SUBJ. Surface
    # shape: V[CTRL_CLASS=RAISING] + linker + full embedded S
    # (the embedded clause is a complete clause with its own
    # SUBJ — distinct from the control case where the embedded
    # clause has a SUBJ-gap). The raising binding equation
    # ``(↑ SUBJ) = (↑ XCOMP SUBJ)`` lifts the embedded SUBJ to
    # the matrix.
    for link in ("NA", "NG"):
        rules.append(Rule(
            "S",
            [
                "V[CTRL_CLASS=RAISING]",
                f"PART[LINK={link}]",
                "S",
            ],
            _eqs(
                "(↑ XCOMP) = ↓3",
                "(↑ SUBJ) = (↑ XCOMP SUBJ)",
            ),
        ))
    # Phase 5d Commit 1: no-linker raising. ``parang`` and
    # ``tila`` are evidential raising verbs that don't take a
    # following linker (``Parang kumain ang bata``, ``Tila
    # umuulan``). They carry CTRL_CLASS=RAISING_BARE — a
    # distinct value from mukha / baka's CTRL_CLASS=RAISING —
    # so the bare wrap rule below doesn't cross-fire on
    # mukhang / bakang sentences (the existing
    # PART[POLARITY=NEG] negation rule's non-conflict matcher
    # would otherwise let the linker `-ng` slip into a bare-
    # raising parse alongside the linked-raising parse,
    # producing a duplicate). The bare rule's binding mirrors
    # the linked rule's: matrix.SUBJ structure-shares with
    # embedded.SUBJ.
    rules.append(Rule(
        "S",
        ["V[CTRL_CLASS=RAISING_BARE]", "S"],
        _eqs(
            "(↑ XCOMP) = ↓2",
            "(↑ SUBJ) = (↑ XCOMP SUBJ)",
        ),
    ))

    # Transitive frames per voice, two NP orderings each, with and
    # without a trailing sa-oblique (ADJUNCT). The ng-non-pivot
    # binds to a typed ``OBJ-θ`` slot for non-AV voices (per the
    # Phase 5b OBJ-θ-in-grammar alignment); AV keeps bare ``OBJ``
    # because PATIENT/THEME [-r, +o] maps to bare OBJ in the BK
    # truth table. The voice + CAUS feature filter splits plain
    # OV (CAUS=NONE → OBJ-AGENT) from pa-OV-direct (CAUS=DIRECT
    # → OBJ-CAUSER) so each lex entry's PRED template (with its
    # specific role name in the typed OBJ-θ) finds a matching
    # grammar rule.
    voice_specs = [
        # (voice, OBJ-target, extra V-feature constraints)
        ("AV", "OBJ", []),
        ("OV", "OBJ-AGENT", [("CAUS", "NONE")]),
        ("OV", "OBJ-CAUSER", [("CAUS", "DIRECT")]),
        # Phase 5d Commit 2: explicit CAUS=NONE on DV plain
        # mirrors the OV split, preventing cross-firing on the
        # new DV CAUS=DIRECT pa-...-an forms (where the GEN-NP
        # is the CAUSER, not the AGENT).
        ("DV", "OBJ-AGENT", [("CAUS", "NONE")]),
        ("DV", "OBJ-CAUSER", [("CAUS", "DIRECT")]),
        ("IV", "OBJ-AGENT", []),
    ]
    for voice, obj_target, extras in voice_specs:
        feat_strs = [f"VOICE={voice}"] + [f"{k}={v}" for k, v in extras]
        v_cat = f"V[{', '.join(feat_strs)}]"
        # NOM-GEN order
        rules.append(Rule(
            "S",
            [v_cat, "NP[CASE=NOM]", "NP[CASE=GEN]"],
            _eqs("(↑ SUBJ) = ↓2", f"(↑ {obj_target}) = ↓3"),
        ))
        # GEN-NOM order
        rules.append(Rule(
            "S",
            [v_cat, "NP[CASE=GEN]", "NP[CASE=NOM]"],
            _eqs("(↑ SUBJ) = ↓3", f"(↑ {obj_target}) = ↓2"),
        ))
        # NOM-GEN-DAT
        rules.append(Rule(
            "S",
            [v_cat, "NP[CASE=NOM]", "NP[CASE=GEN]", "NP[CASE=DAT]"],
            _eqs(
                "(↑ SUBJ) = ↓2",
                f"(↑ {obj_target}) = ↓3",
                "↓4 ∈ (↑ ADJUNCT)",
            ),
        ))
        # GEN-NOM-DAT
        rules.append(Rule(
            "S",
            [v_cat, "NP[CASE=GEN]", "NP[CASE=NOM]", "NP[CASE=DAT]"],
            _eqs(
                "(↑ SUBJ) = ↓3",
                f"(↑ {obj_target}) = ↓2",
                "↓4 ∈ (↑ ADJUNCT)",
            ),
        ))
