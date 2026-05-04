# tgllfg/cfg/extraction_rules.py

"""Extraction rules: ay-inversion, S_GAP family, relativization, fronting.

Holds every grammar rule that participates in long-distance
dependency analysis — extraction of an argument or adjunct to a
fronted (or relativized) position, with a binding equation linking
the displaced phrase back to the gap. After the post-Phase-5f
grammar split (see ``docs/refactor-grammar-package.md``) this
module owns:

* Phase 4 §7.4 ay-inversion — topic fronting via ``ay``
  (``X ay V ...``), with the topic bound to ``REL-PRO`` of an
  inner ``S_GAP`` whose missing SUBJ is identified with the
  topic.
* Phase 4 §7.5 SUBJ-gapped clauses (``S_GAP``) and relativization
  — the underlying gap nonterminal and the head-noun-plus-RC wrap
  rule that licenses ``aso na tumakbo``-type relative clauses.
* Phase 5d Commit 5 non-pivot ay-fronting (``S_GAP_OBJ``,
  ``S_GAP_OBJ_AGENT``, ``S_GAP_OBL``) and Phase 5e Commit 1
  causative-actor variant (``S_GAP_OBJ_CAUSER``) — gap-category
  variants for non-SUBJ extractions.
* Phase 5e Commit 2 multi-GEN-NP ay-fronting variants
  (``S_GAP_OBJ_AGENT IV``, ``S_GAP_OBJ_PATIENT``) — extends the
  gap categories to 3-argument frames.
* Phase 5d Commit 6 possessive-linker RC gap-category — the
  ``ng``-marked relative-clause variant.
* Phase 5e Commit 3 AdvP / PP categorial inventory + fronting —
  fronts adjunct adverbials and PPs to the left of the matrix
  clause.
* Phase 5e Commit 5 headless / free relatives — relative clauses
  with no overt head noun.
* Phase 5d Commit 6 + Phase 5e Commits 18 & 19 dual-binding wrap
  — the wrap rules that bind ``REL-PRO`` from the displaced
  phrase, including dual-binding cases where the same phrase
  satisfies two gap roles.

The composer in :mod:`tgllfg.cfg.grammar` calls this registrar
fifth, after np / clause / clitic / negation, and before control /
discourse — see the plan's "Migration strategy" §H.
"""

from __future__ import annotations

from ._helpers import _eqs
from .grammar import Rule


def register_rules(rules: list[Rule]) -> None:
    """Append the extraction-area rules in source order."""
    # --- Phase 4 §7.4 + §7.5: SUBJ-gapped clauses (S_GAP) ---
    #
    # ``S_GAP`` is the inner clause of an ay-inversion or a
    # relative clause: a V-initial S with the NOM-marked SUBJ
    # argument absent. The missing SUBJ is bound to ``REL-PRO``
    # via the equation ``(↑ SUBJ) = (↑ REL-PRO)``; an enclosing
    # wrap rule (ay-inversion or NP-relativization) sets REL-PRO
    # to the displaced phrase, which transitively fills SUBJ.
    #
    # These rules duplicate the regular S frames but omit the
    # NOM NP. ``S_GAP`` never appears at the top level (the start
    # symbol is ``S``, not ``S_GAP``); it is reachable only via
    # the wrap rules below.
    rules.append(Rule(
        "S_GAP",
        ["V[VOICE=AV]"],
        _eqs("(↑ SUBJ) = (↑ REL-PRO)"),
    ))
    # S_GAP transitive frames mirror the matrix transitive frames'
    # OBJ-θ-in-grammar split: AV binds the ng-NP to bare OBJ
    # (PATIENT/THEME), non-AV binds to typed OBJ-θ.
    gap_voice_specs = [
        ("AV", "OBJ", []),
        ("OV", "OBJ-AGENT", [("CAUS", "NONE")]),
        ("OV", "OBJ-CAUSER", [("CAUS", "DIRECT")]),
        ("DV", "OBJ-AGENT", []),
        ("IV", "OBJ-AGENT", []),
    ]
    for voice, obj_target, extras in gap_voice_specs:
        feat_strs = [f"VOICE={voice}"] + [f"{k}={v}" for k, v in extras]
        v_cat = f"V[{', '.join(feat_strs)}]"
        rules.append(Rule(
            "S_GAP",
            [v_cat, "NP[CASE=GEN]"],
            _eqs(
                f"(↑ {obj_target}) = ↓2",
                "(↑ SUBJ) = (↑ REL-PRO)",
            ),
        ))
        rules.append(Rule(
            "S_GAP",
            [v_cat, "NP[CASE=GEN]", "NP[CASE=DAT]"],
            _eqs(
                f"(↑ {obj_target}) = ↓2",
                "↓3 ∈ (↑ ADJUNCT)",
                "(↑ SUBJ) = (↑ REL-PRO)",
            ),
        ))

    # Negation inside a SUBJ-gapped clause: ``hindi kumain``
    # under ay-inversion or relativization. The recursion mirrors
    # the regular ``S → PART[POLARITY=NEG] S`` rule so negation
    # composes the same way through gapped clauses.
    rules.append(Rule(
        "S_GAP",
        ["PART[POLARITY=NEG]", "S_GAP"],
        ["(↑) = ↓2", "(↑ POLARITY) = 'NEG'"],
    ))


    # --- Phase 5d Commit 5: non-pivot ay-fronting gap-categories ---
    #
    # Phase 4 §7.4 admitted only SUBJ-pivot ay-fronting via
    # ``S_GAP``. S&O §6 and Kroeger 1993 describe topicalization-
    # style ay-fronting of non-pivot phrases (OBJ-θ in any voice
    # plus DAT-marked obliques). Three new gap-category non-
    # terminals parallel ``S_GAP``, each with its own REL-PRO
    # binding to a different GF in the inner clause:
    #
    #   * ``S_GAP_OBJ``       — AV with bare OBJ extracted.
    #   * ``S_GAP_OBJ_AGENT`` — non-AV with typed OBJ-AGENT
    #     (the actor) extracted; the inner SUBJ pivot is overt.
    #   * ``S_GAP_OBL``       — any voice with a DAT-marked
    #     ADJUNCT member extracted.
    #
    # Like ``S_GAP``, none of these are top-level start symbols;
    # they are reachable only via the corresponding wrap rules
    # added below the existing ay-inversion rule, so an unbound
    # REL-PRO never escapes to the matrix.


    # === S_GAP_OBJ: AV with OBJ extracted ===
    # Inner SUBJ overt; OBJ is the gap. Two frames cover plain
    # AV-transitive and AV-transitive-with-DAT-adjunct shapes.
    rules.append(Rule(
        "S_GAP_OBJ",
        ["V[VOICE=AV]", "NP[CASE=NOM]"],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ) = (↑ REL-PRO)",
        ),
    ))
    rules.append(Rule(
        "S_GAP_OBJ",
        ["V[VOICE=AV]", "NP[CASE=NOM]", "NP[CASE=DAT]"],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "↓3 ∈ (↑ ADJUNCT)",
            "(↑ OBJ) = (↑ REL-PRO)",
        ),
    ))
    rules.append(Rule(
        "S_GAP_OBJ",
        ["PART[POLARITY=NEG]", "S_GAP_OBJ"],
        ["(↑) = ↓2", "(↑ POLARITY) = 'NEG'"],
    ))


    # === S_GAP_OBJ_AGENT: non-AV with OBJ-AGENT extracted ===
    # Inner NOM pivot overt; the GEN-marked actor is the gap,
    # bound to ``OBJ-AGENT`` (the typed slot under Phase 5b's
    # OBJ-θ-in-grammar alignment). The voice-specific extras
    # (CAUS=NONE on OV / DV) discriminate against pa-OV / pa-DV
    # (CAUS=DIRECT) where the typed slot would be ``OBJ-CAUSER``;
    # IV is admitted without an APPL constraint so any IV
    # applicative (-CONVEY / -INSTR / -REASON) can have its
    # actor fronted.
    nonav_obj_agent_specs = [
        ("OV", [("CAUS", "NONE")]),
        ("DV", [("CAUS", "NONE")]),
        ("IV", []),
    ]
    for voice, extras in nonav_obj_agent_specs:
        feat_strs = [f"VOICE={voice}"] + [f"{k}={v}" for k, v in extras]
        v_cat = f"V[{', '.join(feat_strs)}]"
        rules.append(Rule(
            "S_GAP_OBJ_AGENT",
            [v_cat, "NP[CASE=NOM]"],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ-AGENT) = (↑ REL-PRO)",
            ),
        ))
        rules.append(Rule(
            "S_GAP_OBJ_AGENT",
            [v_cat, "NP[CASE=NOM]", "NP[CASE=DAT]"],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "↓3 ∈ (↑ ADJUNCT)",
                "(↑ OBJ-AGENT) = (↑ REL-PRO)",
            ),
        ))
    rules.append(Rule(
        "S_GAP_OBJ_AGENT",
        ["PART[POLARITY=NEG]", "S_GAP_OBJ_AGENT"],
        ["(↑) = ↓2", "(↑ POLARITY) = 'NEG'"],
    ))


    # === S_GAP_OBL: any voice with DAT-marked OBL extracted ===
    # The fronted DAT-NP joins ``ADJUNCT`` via set membership
    # (``(↑ REL-PRO) ∈ (↑ ADJUNCT)``); remaining core arguments
    # stay overt. Both NP orders are admitted to mirror the
    # regular S frames' free post-V order.
    # AV intransitive (DAT was the only adjunct).
    rules.append(Rule(
        "S_GAP_OBL",
        ["V[VOICE=AV]", "NP[CASE=NOM]"],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ REL-PRO) ∈ (↑ ADJUNCT)",
        ),
    ))
    # AV transitive (OBJ retained; DAT extracted).
    rules.append(Rule(
        "S_GAP_OBL",
        ["V[VOICE=AV]", "NP[CASE=NOM]", "NP[CASE=GEN]"],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ) = ↓3",
            "(↑ REL-PRO) ∈ (↑ ADJUNCT)",
        ),
    ))
    rules.append(Rule(
        "S_GAP_OBL",
        ["V[VOICE=AV]", "NP[CASE=GEN]", "NP[CASE=NOM]"],
        _eqs(
            "(↑ SUBJ) = ↓3",
            "(↑ OBJ) = ↓2",
            "(↑ REL-PRO) ∈ (↑ ADJUNCT)",
        ),
    ))
    # Non-AV transitive (OBJ-AGENT retained; DAT extracted) per
    # voice spec, both NP orders.
    nonav_obl_specs = [
        ("OV", "OBJ-AGENT", [("CAUS", "NONE")]),
        ("DV", "OBJ-AGENT", [("CAUS", "NONE")]),
        ("IV", "OBJ-AGENT", []),
    ]
    for voice, obj_target, extras in nonav_obl_specs:
        feat_strs = [f"VOICE={voice}"] + [f"{k}={v}" for k, v in extras]
        v_cat = f"V[{', '.join(feat_strs)}]"
        rules.append(Rule(
            "S_GAP_OBL",
            [v_cat, "NP[CASE=NOM]", "NP[CASE=GEN]"],
            _eqs(
                "(↑ SUBJ) = ↓2",
                f"(↑ {obj_target}) = ↓3",
                "(↑ REL-PRO) ∈ (↑ ADJUNCT)",
            ),
        ))
        rules.append(Rule(
            "S_GAP_OBL",
            [v_cat, "NP[CASE=GEN]", "NP[CASE=NOM]"],
            _eqs(
                "(↑ SUBJ) = ↓3",
                f"(↑ {obj_target}) = ↓2",
                "(↑ REL-PRO) ∈ (↑ ADJUNCT)",
            ),
        ))
    rules.append(Rule(
        "S_GAP_OBL",
        ["PART[POLARITY=NEG]", "S_GAP_OBL"],
        ["(↑) = ↓2", "(↑ POLARITY) = 'NEG'"],
    ))


    # --- Phase 5e Commit 1: pa-OV / pa-DV (CAUS=DIRECT) actor-fronting ---
    #
    # Phase 5d Commit 5's ``S_GAP_OBJ_AGENT`` admits non-AV
    # actor-fronting only when the V carries ``CAUS=NONE`` — the
    # constraint deliberately excludes pa-OV / pa-DV (CAUS=DIRECT)
    # because in monoclausal direct causatives the actor's typed
    # GF is ``OBJ-CAUSER``, not ``OBJ-AGENT``. Phase 5e Commit 1
    # fills in the parallel ``OBJ-CAUSER`` extraction path:
    #
    #   ``Ng nanay ay pinakain ang bata.``
    #     "It was mother who fed the child."
    #   ``Ng nanay ay pinakain ang bata ng kanin.``
    #     "It was mother who fed the child rice." (3-arg pa-OV)
    #   ``Ng nanay ay pinakainan ang bata.``
    #     "It was mother who fed [the food to] the child." (pa-DV)
    #
    # The fronted GEN-NP is the CAUSER (demoted from actor under
    # pa-causation); the inner clause's NOM pivot is the CAUSEE
    # (pa-OV) or LOCATION/RECIPIENT (pa-DV) and stays overt.
    # Wrap-rule disambiguation works the same as the Commit 5
    # cases: the parser explores every ``NP[CASE=GEN] PART[LINK=AY]
    # S_GAP_*`` wrap rule, and only the one whose inner gap-
    # category matches the V's voice + CAUS features produces a
    # valid parse.


    # === S_GAP_OBJ_CAUSER: pa-OV / pa-DV (CAUS=DIRECT) with
    # OBJ-CAUSER extracted ===
    # 2-arg pa-OV (causee pivot + gap-causer); the patient is
    # absent on the surface (lex 2-arg PRED `<SUBJ, OBJ-CAUSER>`).
    rules.append(Rule(
        "S_GAP_OBJ_CAUSER",
        ["V[VOICE=OV, CAUS=DIRECT]", "NP[CASE=NOM]"],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
        ),
    ))
    # 2-arg pa-OV with a DAT adjunct retained.
    rules.append(Rule(
        "S_GAP_OBJ_CAUSER",
        [
            "V[VOICE=OV, CAUS=DIRECT]",
            "NP[CASE=NOM]",
            "NP[CASE=DAT]",
        ],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "↓3 ∈ (↑ ADJUNCT)",
            "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
        ),
    ))
    # 3-arg pa-OV (causee + patient retained, gap-causer); both
    # NP orders mirror the top-level multi-GEN-NP and the
    # Phase 5d Commit 8 S_XCOMP rules.
    rules.append(Rule(
        "S_GAP_OBJ_CAUSER",
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
        "S_GAP_OBJ_CAUSER",
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
    # 2-arg pa-DV (location/recipient pivot + gap-causer); the
    # Phase 5d Commit 2 ``pa-...-an`` lex profile starts at
    # 2-arg. Phase 5e Commit 10 adds the 3-arg variants below.
    rules.append(Rule(
        "S_GAP_OBJ_CAUSER",
        ["V[VOICE=DV, CAUS=DIRECT]", "NP[CASE=NOM]"],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
        ),
    ))
    rules.append(Rule(
        "S_GAP_OBJ_CAUSER",
        [
            "V[VOICE=DV, CAUS=DIRECT]",
            "NP[CASE=NOM]",
            "NP[CASE=DAT]",
        ],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "↓3 ∈ (↑ ADJUNCT)",
            "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
        ),
    ))
    # Phase 5e Commit 10: 3-arg pa-DV ay-fronting (CAUSER
    # extracted, OBJ-PATIENT retained as overt GEN-NP). Both
    # NP orders, mirroring the 3-arg pa-OV variants above.
    rules.append(Rule(
        "S_GAP_OBJ_CAUSER",
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
        "S_GAP_OBJ_CAUSER",
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
    # Negation recursion mirrors the other gap categories.
    rules.append(Rule(
        "S_GAP_OBJ_CAUSER",
        ["PART[POLARITY=NEG]", "S_GAP_OBJ_CAUSER"],
        ["(↑) = ↓2", "(↑ POLARITY) = 'NEG'"],
    ))


    # --- Phase 5e Commit 2: multi-GEN-NP ay-fronting ---
    #
    # Phase 5b multi-GEN-NP frames (IV-BEN / IV-INSTR / IV-REASON
    # 3-arg, pa-OV-direct 3-arg) bind two GEN-marked non-pivots
    # to typed ``OBJ-θ`` slots positionally:
    #
    #   * IV (any APPL): first GEN → OBJ-AGENT, second → OBJ-PATIENT.
    #   * pa-OV CAUS=DIRECT: first GEN → OBJ-CAUSER, second → OBJ-PATIENT.
    #
    # Fronting one of the two GEN-NPs leaves the inner clause
    # with one NOM (pivot) plus one retained GEN-NP. The remaining
    # GEN-NP's binding can no longer be purely positional — it
    # depends on which role was extracted.
    #
    # Phase 5d Commit 5 handled the 2-arg cases (no second GEN
    # in the inner clause) only. Phase 5e Commit 1 added the 3-arg
    # pa-OV ``S_GAP_OBJ_CAUSER`` with OBJ-PATIENT retained
    # (CAUSER fronted). Phase 5e Commit 2 fills in the remaining
    # 3-arg multi-GEN extractions:
    #
    #   * 3-arg IV with OBJ-AGENT extracted (OBJ-PATIENT retained).
    #     New ``S_GAP_OBJ_AGENT`` IV-3arg variants.
    #   * 3-arg multi-GEN with OBJ-PATIENT extracted, in either
    #     IV (OBJ-AGENT retained) or pa-OV-direct (OBJ-CAUSER
    #     retained). New ``S_GAP_OBJ_PATIENT`` non-terminal.
    #
    # When two readings exist for the same surface (e.g.,
    # ``Ng nanay ay ipinaggawa ang kapatid ng silya`` could be
    # AGENT-front + PATIENT-retained OR PATIENT-front +
    # AGENT-retained), both parses surface and the existing
    # ranker plus animacy/lexical semantics resolves; tests
    # accept the natural reading among the n-best.


    # === S_GAP_OBJ_AGENT IV 3-arg variants ===
    # The 2-arg IV S_GAP_OBJ_AGENT rule from Phase 5d Commit 5
    # only matches V[VOICE=IV] NP[NOM] (no second GEN). The
    # 3-arg variant adds a retained OBJ-PATIENT GEN-NP in either
    # post-V order; the gap remains OBJ-AGENT.
    rules.append(Rule(
        "S_GAP_OBJ_AGENT",
        ["V[VOICE=IV]", "NP[CASE=NOM]", "NP[CASE=GEN]"],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ-PATIENT) = ↓3",
            "(↑ OBJ-AGENT) = (↑ REL-PRO)",
        ),
    ))
    rules.append(Rule(
        "S_GAP_OBJ_AGENT",
        ["V[VOICE=IV]", "NP[CASE=GEN]", "NP[CASE=NOM]"],
        _eqs(
            "(↑ SUBJ) = ↓3",
            "(↑ OBJ-PATIENT) = ↓2",
            "(↑ OBJ-AGENT) = (↑ REL-PRO)",
        ),
    ))


    # === S_GAP_OBJ_PATIENT: any 3-arg multi-GEN frame with
    # OBJ-PATIENT extracted ===
    # Two voice/feature combinations are admitted, mirroring the
    # top-level multi-GEN-NP rules:
    #
    #   * V[VOICE=IV] (any APPL): retained GEN-NP is OBJ-AGENT.
    #   * V[VOICE=OV, CAUS=DIRECT]: retained GEN-NP is OBJ-CAUSER.
    #
    # Both NP orders are admitted per voice; PART[POLARITY=NEG]
    # recursion at the bottom handles inner negation.
    # Phase 5e Commit 10 adds pa-DV (CAUS=DIRECT) once the
    # 3-arg pa-DV lex profile lands, so DV mirrors OV here.
    patient_gap_specs = [
        # (voice features, retained-GEN-NP target GF)
        ("V[VOICE=IV]", "OBJ-AGENT"),
        ("V[VOICE=OV, CAUS=DIRECT]", "OBJ-CAUSER"),
        ("V[VOICE=DV, CAUS=DIRECT]", "OBJ-CAUSER"),
    ]
    for v_cat, retained_gf in patient_gap_specs:
        # NOM-GEN order: retained GEN follows pivot.
        rules.append(Rule(
            "S_GAP_OBJ_PATIENT",
            [v_cat, "NP[CASE=NOM]", "NP[CASE=GEN]"],
            _eqs(
                "(↑ SUBJ) = ↓2",
                f"(↑ {retained_gf}) = ↓3",
                "(↑ OBJ-PATIENT) = (↑ REL-PRO)",
            ),
        ))
        # GEN-NOM order: retained GEN before pivot.
        rules.append(Rule(
            "S_GAP_OBJ_PATIENT",
            [v_cat, "NP[CASE=GEN]", "NP[CASE=NOM]"],
            _eqs(
                "(↑ SUBJ) = ↓3",
                f"(↑ {retained_gf}) = ↓2",
                "(↑ OBJ-PATIENT) = (↑ REL-PRO)",
            ),
        ))
    # Negation recursion.
    rules.append(Rule(
        "S_GAP_OBJ_PATIENT",
        ["PART[POLARITY=NEG]", "S_GAP_OBJ_PATIENT"],
        ["(↑) = ↓2", "(↑ POLARITY) = 'NEG'"],
    ))


    # --- Phase 5d Commit 6: possessive-linker RC gap-category ---
    #
    # Construction: ``aklat kong binasa`` ("the book that I read").
    # The pronominal actor of the RC's non-AV verb is hoisted out
    # of the RC and surfaces as a possessor of the head NP, joined
    # by the bound linker ``-ng``. Distinct from standard
    # relativization (``aklat na binasa ko``) where the actor
    # stays inside the RC as a GEN-NP.
    #
    # ``S_GAP_NA`` (no-overt-actor) is a SUBJ-gapped non-AV V
    # frame that takes no GEN-NP. The actor (``OBJ-AGENT`` under
    # Phase 5b OBJ-θ-in-grammar) is supplied externally by the
    # wrap rule via ``(↓N OBJ-AGENT) = pronoun``. Voice / feature
    # constraints follow the existing S_GAP pattern: OV / DV
    # require ``CAUS=NONE`` to keep pa-OV / pa-DV out of the
    # actor-extraction path; IV is admitted without an APPL
    # constraint so any applicative variant can host the
    # construction.
    nonav_na_specs = [
        ("OV", [("CAUS", "NONE")]),
        ("DV", [("CAUS", "NONE")]),
        ("IV", []),
    ]
    for voice, extras in nonav_na_specs:
        feat_strs = [f"VOICE={voice}"] + [f"{k}={v}" for k, v in extras]
        v_cat = f"V[{', '.join(feat_strs)}]"
        rules.append(Rule(
            "S_GAP_NA",
            [v_cat],
            _eqs("(↑ SUBJ) = (↑ REL-PRO)"),
        ))
        rules.append(Rule(
            "S_GAP_NA",
            [v_cat, "NP[CASE=DAT]"],
            _eqs(
                "(↑ SUBJ) = (↑ REL-PRO)",
                "↓2 ∈ (↑ ADJUNCT)",
            ),
        ))
    rules.append(Rule(
        "S_GAP_NA",
        ["PART[POLARITY=NEG]", "S_GAP_NA"],
        ["(↑) = ↓2", "(↑ POLARITY) = 'NEG'"],
    ))


    # --- Phase 4 §7.4: ay-inversion ---
    #
    # ``Si Maria ay kumain ng isda``: the topic phrase moves to
    # clause-initial position, separated from the inner clause by
    # the linker particle ``ay``. The fronted phrase is the SUBJ
    # of the inner clause; per Phase 4 §7.4 scope, only pivot
    # (SUBJ) fronting is admitted. Non-pivot ay-fronting is
    # deferred to §7.8 (``docs/analysis-choices.md`` "Phase 4
    # §7.4: ay-inversion").
    #
    # The wrap rule:
    #   - sets ``TOPIC`` on the matrix f-structure to the fronted
    #     NP;
    #   - sets the inner clause's ``REL-PRO`` to the same NP, so
    #     that S_GAP's ``(↑ SUBJ) = (↑ REL-PRO)`` fills SUBJ;
    #   - constrains REL-PRO to equal SUBJ (vacuous now; pins
    #     SUBJ-only fronting structurally).
    rules.append(Rule(
        "S",
        ["NP[CASE=NOM]", "PART[LINK=AY]", "S_GAP"],
        [
            "(↑) = ↓3",
            "(↑ TOPIC) = ↓1",
            "(↓3 REL-PRO) = ↓1",
            "(↓3 REL-PRO) =c (↓3 SUBJ)",
        ],
    ))


    # --- Phase 5d Commit 5: non-pivot ay-fronting wrap rules ---
    #
    # The fronted NP's case marker disambiguates which gap-
    # category the inner clause uses; the V's voice + features
    # then select the right S_GAP_X frame. The wrap-rule pattern
    # mirrors the SUBJ-fronting rule above: matrix and inner
    # clause share an f-structure, the fronted NP becomes
    # ``TOPIC`` and ``REL-PRO``, and a constraining equation
    # pins the fronted GF in the inner clause (vacuous given
    # each S_GAP_X's binding equation, but kept for symmetry
    # and structural documentation).

    # Non-pivot OBJ-fronting (AV, GEN-marked topic):
    # ``Ng isda ay kumain si Maria.``
    rules.append(Rule(
        "S",
        ["NP[CASE=GEN]", "PART[LINK=AY]", "S_GAP_OBJ"],
        [
            "(↑) = ↓3",
            "(↑ TOPIC) = ↓1",
            "(↓3 REL-PRO) = ↓1",
            "(↓3 REL-PRO) =c (↓3 OBJ)",
        ],
    ))

    # Non-pivot OBJ-AGENT-fronting (non-AV, GEN-marked topic):
    # ``Ni Maria ay kinain ang isda.``
    rules.append(Rule(
        "S",
        ["NP[CASE=GEN]", "PART[LINK=AY]", "S_GAP_OBJ_AGENT"],
        [
            "(↑) = ↓3",
            "(↑ TOPIC) = ↓1",
            "(↓3 REL-PRO) = ↓1",
            "(↓3 REL-PRO) =c (↓3 OBJ-AGENT)",
        ],
    ))

    # Non-pivot OBL-fronting (any voice, DAT-marked topic):
    # ``Sa bahay ay kumain si Maria.`` The fronted phrase joins
    # ADJUNCT via S_GAP_OBL's set-membership equation; no scalar
    # constraining equation since ADJUNCT is a set, not a GF.
    rules.append(Rule(
        "S",
        ["NP[CASE=DAT]", "PART[LINK=AY]", "S_GAP_OBL"],
        [
            "(↑) = ↓3",
            "(↑ TOPIC) = ↓1",
            "(↓3 REL-PRO) = ↓1",
        ],
    ))

    # Phase 5e Commit 1: pa-OV / pa-DV (CAUS=DIRECT) actor-fronting.
    # The fronted GEN-NP is the CAUSER (demoted from actor under
    # pa-causation); the inner clause is a pa-causative S_GAP_OBJ_CAUSER
    # which routes REL-PRO to the typed ``OBJ-CAUSER`` slot.
    # Disambiguation against S_GAP_OBJ_AGENT happens via the inner
    # V's CAUS feature (DIRECT vs NONE), so both wrap rules can
    # coexist without cross-firing.
    rules.append(Rule(
        "S",
        ["NP[CASE=GEN]", "PART[LINK=AY]", "S_GAP_OBJ_CAUSER"],
        [
            "(↑) = ↓3",
            "(↑ TOPIC) = ↓1",
            "(↓3 REL-PRO) = ↓1",
            "(↓3 REL-PRO) =c (↓3 OBJ-CAUSER)",
        ],
    ))

    # Phase 5e Commit 2: multi-GEN-NP ay-fronting — OBJ-PATIENT-
    # extracted variant. The fronted GEN-NP is the PATIENT;
    # the inner clause is a 3-arg multi-GEN frame
    # (S_GAP_OBJ_PATIENT) where the retained GEN-NP binds to
    # OBJ-AGENT (under IV) or OBJ-CAUSER (under pa-OV-direct).
    # Coexists with the OBJ_AGENT and OBJ_CAUSER wrap rules:
    # for a 3-arg multi-GEN inner clause, multiple gap-categories
    # match (e.g., AGENT-front + PATIENT-retained, OR PATIENT-
    # front + AGENT-retained); the resulting parses surface in
    # n-best and the ranker plus lexical semantics picks. The
    # constraining equation pins which fronted GF this wrap rule
    # represents.
    rules.append(Rule(
        "S",
        ["NP[CASE=GEN]", "PART[LINK=AY]", "S_GAP_OBJ_PATIENT"],
        [
            "(↑) = ↓3",
            "(↑ TOPIC) = ↓1",
            "(↓3 REL-PRO) = ↓1",
            "(↓3 REL-PRO) =c (↓3 OBJ-PATIENT)",
        ],
    ))


    # --- Phase 5e Commit 3: AdvP / PP categorial inventory + fronting ---
    #
    # Phase 4 §7.4's ``Out-of-scope`` list flagged AdvP / PP
    # ay-fronting as "deferred until the categorial inventory
    # expands". This commit lifts the deferral with the smallest
    # categorial expansion that unblocks the construction:
    #
    #   * Two new POS values (``ADV``, ``PREP``) seeded in
    #     ``data/tgl/particles.yaml`` for a handful of temporal
    #     adverbs (``kahapon`` / ``ngayon`` / ``bukas`` /
    #     ``mamaya``) and compound prepositions (``para`` /
    #     ``tungkol`` / ``mula`` / ``dahil``).
    #   * Two new non-terminals: ``AdvP`` (single-word) and
    #     ``PP`` (PREP + sa-NP).
    #   * Two new ay-fronting wrap rules.
    #
    # The non-fronted placement of AdvP / PP (clause-final or as
    # an unmarked sentential adjunct) is **not** added in this
    # commit — the scoped goal is ay-fronting only. Adding bare
    # placement would interact with the Phase 4 §7.3 Wackernagel
    # cluster and the Phase 4 §7.8 quantifier-float rule and is
    # deferred to a separate commit.

    # AdvP: a single ADV word lifts to AdvP. ADV is a closed-
    # class POS so a flat single-child rule is sufficient; the
    # AdvP's f-structure inherits the ADV's atomic features
    # (LEMMA, ADV_TYPE, DEIXIS_TIME, ...).
    rules.append(Rule(
        "AdvP",
        ["ADV"],
        _eqs("(↑) = ↓1"),
    ))

    # PP: PREP + NP[CASE=DAT]. The compound prepositions in
    # particles.yaml all subcategorise for a sa-NP complement
    # (``para sa bata``, ``tungkol sa nanay``, ``mula sa
    # Maynila``, ``dahil sa gutom``). The PP's f-structure
    # inherits PREP_TYPE from the head and exposes the
    # complement NP as ``OBJ`` for downstream consumers
    # (analogous to how a clause's V exposes its NP arguments).
    rules.append(Rule(
        "PP",
        ["PREP", "NP[CASE=DAT]"],
        _eqs(
            "(↑) = ↓1",
            "(↑ OBJ) = ↓2",
        ),
    ))

    # ay-fronting an AdvP. The fronted phrase is BOTH the matrix
    # TOPIC and a member of the matrix's ADJ set (sentential
    # adjunct semantics). The inner clause is a complete S
    # (no gap) — AdvP isn't an argument of any voice/aspect
    # frame, so there's nothing to extract from the inner
    # clause's GF inventory.
    rules.append(Rule(
        "S",
        ["AdvP", "PART[LINK=AY]", "S"],
        [
            "(↑) = ↓3",
            "(↑ TOPIC) = ↓1",
            "↓1 ∈ (↑ ADJ)",
        ],
    ))

    # ay-fronting a PP. Same shape as AdvP fronting: matrix
    # TOPIC + ADJ membership. The PP's internal structure (PREP
    # head + sa-NP complement) is independent of the
    # ay-construction.
    rules.append(Rule(
        "S",
        ["PP", "PART[LINK=AY]", "S"],
        [
            "(↑) = ↓3",
            "(↑ TOPIC) = ↓1",
            "↓1 ∈ (↑ ADJ)",
        ],
    ))


    # --- Phase 5e Commit 5: headless / free relatives ---
    #
    # ``ang kumain`` "the one who ate"; ``ang kumain ng isda``
    # "the one who ate fish"; ``ang kinain ng aso`` "the one
    # eaten by the dog". A relative clause used directly as an
    # NP, with no overt head noun. The "head" is a phonologically
    # null PRO interpreted as the gap-filler (REL-PRO).
    #
    # Structure: ``DET[CASE=X, DEM=NO] S_GAP``. The bare case
    # marker (``ang`` / ``ng`` / ``sa`` / ``si`` / ``ni`` /
    # ``kay``) plus a SUBJ-gapped inner clause forms the headless
    # NP. The DEM=NO constraint prevents the rule from firing on
    # demonstratives (``ito`` / ``iyan`` / ``iyon`` etc., which
    # carry DEM=YES); demonstrative NPs use the standalone-
    # demonstrative rule above, not headless RCs.
    #
    # Equations parallel the standalone-demonstrative rule
    # (PRED='PRO' for the implicit head) and the head-initial
    # relativization rule (S_GAP attaches as ADJ; REL-PRO PRED
    # and CASE are anaphorically shared from the head).
    for case in ("NOM", "GEN", "DAT"):
        # NOM uses DET (ang / si); GEN / DAT use ADP
        # (ng / sa / ni / kay).
        head_cat = (
            f"DET[CASE={case}, DEM=NO]"
            if case == "NOM"
            else f"ADP[CASE={case}, DEM=NO]"
        )
        rules.append(Rule(
            f"NP[CASE={case}]",
            [head_cat, "S_GAP"],
            [
                "(↑ PRED) = 'PRO'",
                f"(↑ CASE) = '{case}'",
                "(↑ MARKER) = ↓1 MARKER",
                "↓2 ∈ (↑ ADJ)",
                "(↓2 REL-PRO PRED) = 'PRO'",
                f"(↓2 REL-PRO CASE) = '{case}'",
                "(↓2 REL-PRO) =c (↓2 SUBJ)",
            ],
        ))


    # --- Phase 4 §7.5: relativization ---
    #
    # ``ang batang kumain ng isda`` ("the child that ate fish"):
    # head-initial NP relativization. The head NP is followed by
    # the linker (``na`` after consonant-final hosts, the bound
    # ``-ng`` after vowel-final hosts) and a SUBJ-gapped inner
    # clause. SUBJ-only relativization is the well-known Tagalog
    # restriction (Kroeger 1993): only the ang-NP can be
    # relativized.
    #
    # **Anaphoric REL-PRO** (not structure-sharing). The canonical
    # LFG analysis equates the head NP with the RC's REL-PRO
    # via full identity ``(↓3 REL-PRO) = ↓1``. That creates a
    # cyclic f-structure (head NP ⊇ ADJ ⊇ RC ⊇ REL-PRO = head NP)
    # which our unifier's occurs-check rejects. We instead share
    # the head NP's salient features (``PRED``, ``CASE``) with
    # REL-PRO via individual atomic-path equations, and bind the
    # RC's SUBJ to REL-PRO inside S_GAP. The constraining
    # equation ``(↓3 REL-PRO) =c (↓3 SUBJ)`` still pins the
    # SUBJ-only restriction (vacuous today, non-vacuous under
    # §7.6 non-SUBJ S_GAP frames). Documented in
    # ``docs/analysis-choices.md`` "Phase 4 §7.5".
    #
    # Six wrap rules (3 head cases × 2 linker variants) — the
    # head NP's case percolates to the matrix; both linkers (NA
    # standalone, NG bound enclitic) carry the same f-equations.
    for case in ("NOM", "GEN", "DAT"):
        np_cat = f"NP[CASE={case}]"
        for link in ("NA", "NG"):
            rules.append(Rule(
                np_cat,
                [np_cat, f"PART[LINK={link}]", "S_GAP"],
                [
                    "(↑) = ↓1",
                    "↓3 ∈ (↑ ADJ)",
                    "(↓3 REL-PRO PRED) = (↓1 PRED)",
                    "(↓3 REL-PRO CASE) = (↓1 CASE)",
                    "(↓3 REL-PRO) =c (↓3 SUBJ)",
                ],
            ))


    # --- Phase 5d Commit 6 + Phase 5e Commits 18 & 19:
    # possessive-linker RC wrap rule ---
    #
    # ``aklat kong binasa`` ("the book that I read"): a
    # construction parallel to relativization where the
    # actor of the RC's non-AV verb surfaces as a possessor
    # of the head NP, joined by a linker.
    #
    # **Three lifts of the same construction shape:**
    #
    # * **Phase 5d Commit 6** — vowel-final PRON + bound
    #   ``-ng`` linker (``aklat kong binasa``, fused ``Vng``
    #   form split by ``split_linker_ng``).
    # * **Phase 5e Commit 18** — consonant-final PRON +
    #   standalone ``na`` linker (``aklat namin na binasa``);
    #   plus the LINK=NA variant for vowel-final PRON
    #   (``aklat ko na binasa``).
    # * **Phase 5e Commit 19** — non-pronominal (NOUN /
    #   proper-noun) possessor (``aklat ng batang binasa``,
    #   ``aklat ni Juan na binasa``). Unified with the PRON
    #   case by widening the second daughter from
    #   ``PRON[CASE=GEN]`` to ``NP[CASE=GEN]`` — the
    #   ``NP[CASE=GEN] → PRON[CASE=GEN]`` rule already in the
    #   grammar makes this a strict generalization that
    #   subsumes the PRON case.
    #
    # **Wackernagel placement** — already in place from prior
    # commits and reused unchanged:
    #
    # * Vowel-final PRON + ``-ng``: PRON kept adjacent to its
    #   split-out bound linker by ``_is_pre_linker_pron``
    #   (Phase 5d Commit 6).
    # * Consonant-final PRON + ``na``: PRON kept in place by
    #   the older ``_is_post_noun_pron`` exception (Phase 5c
    #   §7.8 lift).
    # * NOUN possessor: NOUNs aren't clitic-pass-eligible, so
    #   they sit in surface order without help.
    #
    # **``na`` linker disambiguation** — the post-PRON ``na``
    # is preserved as the linker (rather than hoisted as the
    # 2P aspectual ``ALREADY``) by the third left-context
    # exception in ``disambiguate_homophone_clitics`` (Phase
    # 5e Commit 6). Doesn't apply to the NOUN case because
    # the NOUN-then-``na`` sequence is already preserved by
    # the first branch (``na`` after NOUN → linker reading).
    #
    # The possessor plays a dual role: it is the head NP's
    # ``POSS`` AND the RC's ``OBJ-AGENT``. The wrap rule binds
    # both via ``(↑ POSS) = ↓2`` and ``(↓4 OBJ-AGENT) = ↓2``.
    # REL-PRO sharing follows the standard relativization
    # pattern — anaphoric (PRED + CASE atomic-path copies, not
    # full identity) so the unifier's occurs-check stays happy.
    #
    # Six wrap rules: 3 head cases × 2 linker variants.
    #
    # **Constraints**:
    #
    # * ``(↑ LEMMA)`` (existential) requires the head NP to be
    #   NOUN-headed (NOUNs / proper nouns carry LEMMA in their
    #   f-structure; PRONs and headless-RC NPs do not). Without
    #   this guard, the widened ``NP[CASE=GEN]`` second-daughter
    #   slot (Phase 5e Commit 19) would let the rule fire on
    #   surfaces like ``Kumain ako ng batang kinain niya``,
    #   wrongly treating ``ako`` (PRON-NOM) as the possessable
    #   head NP and ``ng bata`` as its dual-bound possessor.
    #   The construction ``possessor + linker + RC`` only makes
    #   sense with a NOUN head; pronouns aren't possessable in
    #   this shape.
    # * The output NP is marked ``POSS-EXTRACTED=YES`` so the
    #   standard NP-poss rule cannot fire on it again — without
    #   this guard, a trailing GEN-NP (e.g., ``ng aso`` in ``bata
    #   ko na kinain ng aso``) would unify with the already-bound
    #   POSS, producing a spurious hybrid POSS=OBJ-AGENT. See
    #   the §7.8 NP-poss rule above for the full comment on the
    #   guard.
    for case in ("NOM", "GEN", "DAT"):
        np_cat = f"NP[CASE={case}]"
        for link in ("NA", "NG"):
            rules.append(Rule(
                np_cat,
                [np_cat, "NP[CASE=GEN]", f"PART[LINK={link}]", "S_GAP_NA"],
                [
                    "(↑) = ↓1",
                    "(↑ POSS) = ↓2",
                    "(↑ POSS-EXTRACTED) = 'YES'",
                    "(↓1 LEMMA)",
                    "↓4 ∈ (↑ ADJ)",
                    "(↓4 OBJ-AGENT) = ↓2",
                    "(↓4 REL-PRO PRED) = (↓1 PRED)",
                    "(↓4 REL-PRO CASE) = (↓1 CASE)",
                    "(↓4 REL-PRO) =c (↓4 SUBJ)",
                ],
            ))
