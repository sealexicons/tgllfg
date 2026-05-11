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
    # Phase 5n.A Commit 13 (§18 L70): AV intransitive embedded
    # clause with trailing DAT-NP as ADJUNCT, no overt GEN-OBJ.
    # ``Dapat akong kumain sa labas.`` "I should eat outside" — the
    # embedded ``kumain sa labas`` is AV-intransitive (no OBJ) with
    # the locative ``sa labas`` lifted to ADJUNCT. Mirrors the
    # 3-daughter rule above but without the GEN-OBJ daughter; the
    # locative-PP ADJUNCT lift is structurally identical.
    rules.append(Rule(
        "S_XCOMP",
        ["V[VOICE=AV]", "NP[CASE=DAT]"],
        _eqs(
            "↓2 ∈ (↑ ADJUNCT)",
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
        # Phase 5n.A Commit 11 (§18 L67): MODAL nested control —
        # V[CTRL_CLASS=MODAL] PART S_XCOMP. Parallel to the PSYCH /
        # INTRANS rules above; admits modal stacking (``Dapat akong
        # puwedeng kumain.`` "I should be able to eat") with SUBJ
        # control re-entrant through both layers — outer-modal SUBJ
        # = inner-modal SUBJ = innermost-action SUBJ. The existing
        # Phase 5j Commit 7 matrix modal wrap binds the outer
        # SUBJ NP; this rule lets the inner modal-XCOMP compose.
        rules.append(Rule(
            "S_XCOMP",
            [
                "V[CTRL_CLASS=MODAL]",
                f"PART[LINK={link}]",
                "S_XCOMP",
            ],
            _eqs(
                "(↑ SUBJ) = (↑ REL-PRO)",
                "(↑ XCOMP) = ↓3",
                "(↑ SUBJ) = (↑ XCOMP REL-PRO)",
                "(↓1 CTRL_CLASS) =c 'MODAL'",
                "(↓1 MODAL) =c true",
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

    # --- Phase 5j Commit 7: modal control wrap -----------------------
    #
    # Closed-class modal predicates (Phase 5j Commit 6: dapat /
    # puwede / pwede / puede / maaari / kailangan) take a SUBJ
    # clitic + linker + S_XCOMP. Subject control: matrix SUBJ is
    # structure-shared with the embedded SUBJ via the standard
    # ``(↑ SUBJ) = (↑ XCOMP REL-PRO)`` binding (same shape as the
    # PSYCH wrap above, distinguished only by CTRL_CLASS=MODAL).
    #
    # Two case variants for the matrix SUBJ:
    #
    # * **NOM-actor pattern** (``Dapat akong kumain.`` "I should
    #   eat"): ``dapat`` / ``puwede`` / ``maaari`` take NOM-marked
    #   actors as matrix SUBJ — same shape as the Phase 5c §7.6
    #   intransitive-control wrap.
    # * **GEN-experiencer pattern** (``Kailangan kong kumain.``
    #   "I need to eat"): ``kailangan`` takes a GEN-marked
    #   experiencer (parallel to PSYCH ``gusto`` / ``ayaw`` /
    #   ``kaya``).
    #
    # Both rules carry the ``(↓1 CTRL_CLASS) =c 'MODAL'`` filter so
    # they don't cross-fire on PSYCH (gusto / ayaw / kaya) or
    # KNOW (alam) predicates. The two case variants admit both
    # canonical patterns; for modals where both readings are
    # marginal-but-acceptable (e.g., ``Dapat kong kumain.`` /
    # ``Kailangan akong kumain.``), both rules will fire and produce
    # parallel parses — no harm, since the ranker / classifier
    # can disambiguate downstream by lemma + case combination.
    #
    # **Flip-restoration**: ``Hindi ka dapat kumain.`` (the
    # documented Phase 5j flip-risk surface — see plan §3 / §6)
    # parsed pre-Commit-6 as ``EAT <SUBJ>`` POLARITY=NEG by
    # silently dropping ``dapat``. Commit 6 stopped the silent-
    # drop (1→0 parses regression). This commit's modal control
    # wrap restores the parse path with the proper modal-headed
    # matrix structure (PRED=DAPAT, POLARITY=NEG, XCOMP holding
    # the embedded ``kumain``). The Phase 4 §7.2 hindi-wrap
    # composes onto the matrix S unchanged.
    # Phase 5n.A Commit 12 (§18 L68): modal-as-predicate (no XCOMP).
    # ``Hindi puwede.`` "Not allowed/possible.", ``Hindi dapat.``
    # "Not necessary.", ``Hindi kailangan.`` "Not needed." — bare
    # modals function as impersonal predicates with no embedded V.
    # The PRED template shape ``MODAL <SUBJ>`` mirrors the
    # control-wrap PRED shape, but the SUBJ is implicit (PRO) since
    # there's no overt argument.
    #
    # Single-daughter rule structure: when a modal-headed input has
    # an XCOMP, the multi-daughter modal control wrap below fires
    # instead and consumes the XCOMP material; the bare-modal rule
    # only matches when no XCOMP is present (no overt linker + V or
    # NP + linker + V daughter sequence).
    #
    # Composes with the Phase 4 §7.2 hindi-wrap (S → PART[NEG] S)
    # to yield ``Hindi puwede.``-style sentences.
    # Provide impersonal-PRO fillers for both args declared by the
    # modal's lex PRED (``PUWEDE <SUBJ, XCOMP>`` etc.) so completeness
    # is satisfied. Linguistically: ``Hindi puwede.`` "(it) is not
    # permitted (to do something)" — the SUBJ is the implicit
    # forcee/agent and the XCOMP is the implicit unspecified action.
    rules.append(Rule(
        "S",
        ["V[CTRL_CLASS=MODAL]"],
        _eqs(
            "(↑) = ↓1",
            "(↑ SUBJ PRED) = 'PRO'",
            "(↑ XCOMP PRED) = 'PRO'",
            "(↑ MODAL_STANDALONE) = true",
            "(↓1 CTRL_CLASS) =c 'MODAL'",
            "(↓1 MODAL) =c true",
        ),
    ))

    for link in ("NA", "NG"):
        # NOM-actor variant (dapat / puwede / maaari).
        rules.append(Rule(
            "S",
            [
                "V[CTRL_CLASS=MODAL]",
                "NP[CASE=NOM]",
                f"PART[LINK={link}]",
                "S_XCOMP",
            ],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ XCOMP) = ↓4",
                "(↑ SUBJ) = (↑ XCOMP REL-PRO)",
                "(↓1 CTRL_CLASS) =c 'MODAL'",
                "(↓1 MODAL) =c true",
            ),
        ))
        # GEN-experiencer variant (kailangan; also marginally
        # acceptable for dapat / puwede / maaari in some
        # registers).
        rules.append(Rule(
            "S",
            [
                "V[CTRL_CLASS=MODAL]",
                "NP[CASE=GEN]",
                f"PART[LINK={link}]",
                "S_XCOMP",
            ],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ XCOMP) = ↓4",
                "(↑ SUBJ) = (↑ XCOMP REL-PRO)",
                "(↓1 CTRL_CLASS) =c 'MODAL'",
                "(↓1 MODAL) =c true",
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
    # Phase 5n.B Commit 11 (§18 L54): yes/no indirect-Q variants.
    #
    # ``Alam ko kung kumain ang aso.``     "I know whether the dog
    #                                       ate." (bare declarative)
    # ``Alam ko kung pumunta si Maria.``   "I know whether Maria
    #                                       went." (bare declarative)
    # ``Alam ko kung kumain ba ang aso.``  (with ``ba`` — Q_TYPE=
    #                                       YES_NO inner)
    #
    # Closes §18 L54. Two sibling rules cover the yes/no path:
    #
    #   (a) ``S_INTERROG_COMP → PART[COMP_TYPE=INTERROG]
    #       S[Q_TYPE=YES_NO]`` — with-ba case (the Phase 5i Commit
    #       5 ba-rule sets Q_TYPE=YES_NO on the matrix S).
    #   (b) ``S_INTERROG_COMP → PART[COMP_TYPE=INTERROG] S`` with
    #       ``¬ (↓2 Q_TYPE)`` — bare declarative case (no Q_TYPE).
    #
    # Both lift ``COMP_TYPE=YES_NO_INTERROG`` to mark the matrix
    # COMP as a yes/no interrogative complement. The wh case
    # remains routed through the existing ``S[Q_TYPE=WH]`` rule
    # above with ``COMP_TYPE=INTERROG``.
    #
    # **Why two rules**: the unifier's ``NegEquation`` semantics
    # (per ``fstruct/unify.py:_eval_neg_equation``) is strict:
    # ``≠`` fails when the lhs path is undefined. A single rule
    # with ``(↓2 Q_TYPE) ≠ 'WH'`` would correctly admit
    # Q_TYPE=YES_NO but reject the bare-declarative path (no
    # Q_TYPE). Splitting into two rules — ``=c 'YES_NO'`` and
    # ``¬ (↓2 Q_TYPE)`` — covers both cleanly. The three
    # S_INTERROG_COMP rules (wh / yes-no-with-ba / bare-decl) are
    # mutually exclusive on Q_TYPE.

    # (a) yes/no with ``ba`` — inner S has Q_TYPE=YES_NO.
    # COMP_TYPE='INTERROG' keeps the matrix wrap's
    # ``(↓3 COMP_TYPE) =c 'INTERROG'`` constraint satisfied;
    # ``COMP_QTYPE='YES_NO'`` tags the COMP for downstream
    # consumers needing the yes/no vs wh distinction.
    rules.append(Rule(
        "S_INTERROG_COMP",
        ["PART[COMP_TYPE=INTERROG]", "S[Q_TYPE=YES_NO]"],
        [
            "(↑) = ↓2",
            "(↑ COMP_TYPE) = 'INTERROG'",
            "(↑ COMP_QTYPE) = 'YES_NO'",
            "(↓1 COMP_TYPE) =c 'INTERROG'",
            "(↓2 Q_TYPE) =c 'YES_NO'",
        ],
    ))

    # (b) bare declarative — inner S has no Q_TYPE.
    rules.append(Rule(
        "S_INTERROG_COMP",
        ["PART[COMP_TYPE=INTERROG]", "S"],
        [
            "(↑) = ↓2",
            "(↑ COMP_TYPE) = 'INTERROG'",
            "(↑ COMP_QTYPE) = 'YES_NO'",
            "(↓1 COMP_TYPE) =c 'INTERROG'",
            "¬ (↓2 Q_TYPE)",
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

    # --- Phase 5n.B Commit 13: declarative-COMP factive embedding ---
    #
    # ``Alam kong kumain ang aso.`` "I know that the dog ate."
    # ``Akala kong kumain si Maria.`` "I thought Maria ate."
    # ``Naaalala kong pumunta siya.`` "I remember that she went."
    #
    # Closes §18.1 deferral L56. Parallel to the S_INTERROG_COMP
    # path above (Phase 5i C8 + 5n.B C11) but with a declarative
    # complement: no ``kung`` complementizer, just a bound linker
    # (``-ng`` after vowel-final hosts; ``na`` after consonant-
    # final hosts) between the GEN-NP experiencer and the embedded
    # S. The embedded S is a complete declarative clause with its
    # own SUBJ.
    #
    # ``S_DECL_COMP`` is a sibling non-terminal to S_INTERROG_COMP.
    # The wrapper rule lifts the inner S's f-structure and adds
    # ``COMP_TYPE='DECLARATIVE'`` (parallel to S_INTERROG_COMP's
    # ``COMP_TYPE='INTERROG'``); the matrix wrap then constrains
    # ``(↓4 COMP_TYPE) =c 'DECLARATIVE'`` to lock the path.
    #
    # **Disambiguation from INTERROG-COMP**: the linker token
    # ``PART[LINK=NG/NA]`` vs the kung complementizer
    # ``PART[COMP_TYPE=INTERROG]`` sit in different positions and
    # don't overlap (kung has no LINK feat; -ng / na have no
    # COMP_TYPE feat). The two paths are mutually exclusive.
    rules.append(Rule(
        "S_DECL_COMP",
        ["S"],
        [
            "(↑) = ↓1",
            "(↑ COMP_TYPE) = 'DECLARATIVE'",
        ],
    ))

    for link in ("NA", "NG"):
        rules.append(Rule(
            "S",
            [
                "V[CTRL_CLASS=KNOW]",
                "NP[CASE=GEN]",
                f"PART[LINK={link}]",
                "S_DECL_COMP",
            ],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ COMP) = ↓4",
                "(↓1 CTRL_CLASS) =c 'KNOW'",
                f"(↓3 LINK) =c '{link}'",
                "(↓4 COMP_TYPE) =c 'DECLARATIVE'",
            ),
        ))

    # --- Phase 5n.A Commit 29: ASK-class reported-Q (§18 L90.2 + L92) ---
    #
    # ASK-class verbs (``tanong`` and its inflected forms
    # ``tinanong`` / ``tinatanong`` / ``tatanungin`` / ``nagtanong``
    # / ``nagtatanong`` / ``magtatanong`` / ``tumanong`` /
    # ``tumatanong``) admit a finite-S indirect-Q complement
    # introduced by ``kung``. Unlike KNOW (uninflected pseudo-verb
    # with PRED='KNOW <SUBJ, COMP>'), ASK-class is fully inflected
    # under standard transitive paradigms so the PRED template is
    # 'TANONG <SUBJ, OBJ-AGENT>' for OV and 'TANONG <SUBJ, OBJ>'
    # for AV. The reported-Q complement fills:
    #
    # * **OV pivot**: SUBJ = the asked-thing (S_INTERROG_COMP),
    #   OBJ-AGENT = the asker (clitic GEN-PRON or full GEN-NP).
    #   Mirrors Phase 5n.A Commit 27 SAY-class OV pattern.
    # * **AV pivot**: SUBJ = the asker (NOM-clitic-PRON or full
    #   NOM-NP), OBJ = the asked-thing (S_INTERROG_COMP). The
    #   embedded clause functions as the THEME of the asking,
    #   mapped to OBJ in AV.
    #
    # Example targets (closes §18 L90.2 corpus from Commit 28):
    #
    #   ``Tinanong niya kung sino ang kumain.``  (OV PFV / clitic-actor)
    #   ``Tinanong ng lalaki kung saan...``      (OV PFV / full-NP-actor)
    #   ``Nagtanong siya kung sino ang kumain.`` (AV PFV / clitic-actor)
    #   ``Nagtanong si Maria kung saan...``      (AV PFV / full-NP-actor)
    #
    # Per plan-of-record §3.5 Commit 29, two rule shapes (OV and AV)
    # × two NP types (PRON for clitic, NP for full) = 4 rules.
    # Both clitic-PRON and full-NP actor variants are admitted; the
    # full-NP variant doesn't suffer from the RC-linker crossfire
    # because ``kung`` is structurally distinct from the bare ``-na``
    # linker (the kung-clause has its own SubordClause builder
    # context).
    #
    # The ASK_CLASS=YES gate restricts to ``tanong`` only; other
    # transitive verbs continue to require NOM-NP SUBJ.

    # OV reported-Q. NP[CASE=GEN] subsumes clitic-PRON via the
    # ``NP[CASE=GEN] → PRON[CASE=GEN]`` shell in nominal.py.
    rules.append(Rule(
        "S",
        [
            "V[VOICE=OV, ASK_CLASS]",
            "NP[CASE=GEN]",
            "S_INTERROG_COMP",
        ],
        _eqs(
            "(↑ OBJ-AGENT) = ↓2",
            "(↑ SUBJ) = ↓3",
            "(↓1 ASK_CLASS) =c true",
            "(↓3 COMP_TYPE) =c 'INTERROG'",
        ),
    ))
    # AV reported-Q. NP[CASE=NOM] subsumes clitic-PRON via the
    # ``NP[CASE=NOM] → PRON[CASE=NOM]`` shell in nominal.py.
    rules.append(Rule(
        "S",
        [
            "V[VOICE=AV, ASK_CLASS]",
            "NP[CASE=NOM]",
            "S_INTERROG_COMP",
        ],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ) = ↓3",
            "(↓1 ASK_CLASS) =c true",
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
