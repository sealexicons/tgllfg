# tgllfg/cfg/extraction.py

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
    # Phase 8.V: SUBJ-gapped AV-INTR clause with a locative
    # DAT-adjunct only. Parallels the matrix S → V[AV] NP[DAT]
    # NP[NOM] rule with the SUBJ slot extracted via REL-PRO
    # binding. Required for the audit hit ``Ni si Juan ay hindi
    # nakapunta doon.`` (S&O 1972 page 640 / sent-1260): the
    # inner S_GAP ``hindi nakapunta doon`` has a DAT-adjunct
    # daughter (``doon``) with no GEN-OBJ — the prior S_GAP
    # frames require either bare V or V + GEN-OBJ.
    rules.append(Rule(
        "S_GAP",
        ["V[VOICE=AV]", "NP[CASE=DAT]"],
        _eqs(
            "↓2 ∈ (↑ ADJUNCT)",
            "(↑ SUBJ) = (↑ REL-PRO)",
        ),
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

    # === Phase 5n.A Commit 8: N-level RC wrap for existential N modifier (§18 L64) =====
    #
    # ``May bahay na nasa bundok.`` "There is a house in the mountain"
    # — the existential rule (Phase 5j Commit 2) takes an ``N`` (not
    # ``NP``) daughter, so the existing NP-level RC wrap rule
    # (``NP[CASE=X] → NP[CASE=X] PART[LINK=N{A,G}] S_GAP``, Phase 4
    # §7.5) doesn't compose: there's no NP for the RC to attach to.
    # This new rule adds an N-level parallel:
    #
    #   N → N PART[LINK=N{A,G}] S_GAP
    #
    # The CASE equation from the NP-level wrap is dropped (N has no
    # CASE — it's case-marked when projected to NP); the PRED binding
    # to REL-PRO and the SUBJ-only constraint are preserved.
    # Required for R&G "Ang Manok" combined essay-paragraph and
    # ``May bahay na nasa bundok`` style sentences.
    #
    # Phase 6.G C2: the produced N is tagged with ``N_RC = true``
    # so the simple NP-from-DET+N rule (``cfg/nominal.py``) can
    # reject it via ``¬ (↓2 N_RC)``. Under the Phase 6.G
    # SHARE+SHARE projection, an N-level-RC'd N consumed by the
    # simple NP rule would produce a parse equivalent to the
    # NP-level RC wrap (Phase 4 §7.5) — the tag prevents that
    # spurious ambiguity. The N-level RC stays load-bearing for the
    # existential bare-N case where the existential rule consumes
    # bare N directly (not through the simple NP path). ``N_RC``
    # is a binary feat (Phase 5n.C.4 bool convention); declared in
    # ``core/feats.py`` BINARY_FEATS.
    for link in ("NA", "NG"):
        rules.append(Rule(
            "N",
            ["N", f"PART[LINK={link}]", "S_GAP"],
            [
                "(↑) = ↓1",
                "↓3 ∈ (↑ ADJ)",
                "(↓3 REL-PRO PRED) = (↓1 PRED)",
                "(↓3 REL-PRO) =c (↓3 SUBJ)",
                "(↑ N_RC) = true",
            ],
        ))

    # === 9.X.c9: pre-N V-attributive RC wrap ============================
    #
    # ``ang natitirang buwan`` "the remaining months" (PANAHON sent-34).
    # ``ang kumakaing bata`` "the eating child".
    #
    # Parallel to the post-N RC wrap directly above
    # (``N → N PART[LINK={NA,NG}] S_GAP``), but with the daughter
    # order reversed: the gapped relative clause precedes the head
    # N, with the linker attaching to the modifier rather than the
    # head. Tagalog admits both orders for N+RC modification
    # (R&G 1981 §6.6); the post-N form was already in the grammar
    # (Phase 5n.A Commit 8 for the existential N-level path, Phase
    # 4 §7.5 for the canonical NP-level path), the pre-N form is
    # added here at the N-level.
    #
    # Rule shape:
    #
    #   N → S_GAP PART[LINK={NA,NG}] N
    #     (↑) = ↓3                       head N supplies PRED, FORM
    #     ↓1 ∈ (↑ ADJ)                  RC joins head N's ADJ set
    #     (↓1 REL-PRO PRED) = (↓3 PRED) REL-PRO points to head
    #     (↓1 REL-PRO) =c (↓1 SUBJ)     gap is SUBJ position
    #
    # **No N_RC tag.** The Phase 6.G C2 ``N_RC=true`` tag on the
    # post-N N-level RC rule (line 154 above) blocks feedback into
    # the simple-NP rule, preventing duplication of the canonical
    # NP-level RC wrap path (extraction.py: ``NP[CASE=X] →
    # NP[CASE=X] PART[LINK] S_GAP``). The pre-N construction has
    # no canonical NP-level parallel — there is no NP-level
    # ``NP[CASE=X] → S_GAP PART[LINK] NP[CASE=X]`` rule because
    # DET attaches to the head, not to the pre-modifier. The
    # N-level pre-N rule is the unique route, so no
    # disambiguation tag is needed; the simple-NP rule consumes
    # the pre-N N normally.
    #
    # Closes PANAHON sent-34 (``May kalamigan ang mga natitirang
    # buwan``) when composed with the existing mga-marked NP rules
    # and the Phase 8 May + N + NP[CASE=NOM] HAVE-construction.
    #
    # Reference: R&G 1981 §6.6 (NP modification: both pre-N and
    # post-N orders); R&G 1981 PANAHON essay.
    for link in ("NA", "NG"):
        rules.append(Rule(
            "N",
            ["S_GAP", f"PART[LINK={link}]", "N"],
            [
                "(↑) = ↓3",
                "↓1 ∈ (↑ ADJ)",
                "(↓1 REL-PRO PRED) = (↓3 PRED)",
                "(↓1 REL-PRO) =c (↓1 SUBJ)",
            ],
        ))


    # === Phase 5n.A Commit 8: nasa-headed gapped clause for RC bodies (§18 L64) =====
    #
    # ``May bahay na nasa bundok.`` "There is a house in the mountain"
    # — the RC body ``nasa bundok`` is a SUBJ-gapped locative-existential
    # clause (Phase 5j Commit 4 ``S → PART[LOC_EXISTENTIAL] N
    # NP[CASE=NOM]`` minus the NOM-NP daughter, with the SUBJ slot
    # filled by REL-PRO bound to the head N). Required for the R&G
    # "Ang Manok" combined essay-paragraph (R&G p. 482, Commit 8
    # integration target).
    #
    # Two variants: bare-N ground (``nasa bundok``) and possessor-of-
    # ground (``nasa tuktok ng bundok``). The shapes mirror the
    # matrix Phase 5j Commit 4 frames in cfg/clause.py exactly,
    # except the NOM-NP SUBJ daughter is replaced with the
    # ``(↑ SUBJ) = (↑ REL-PRO)`` gap binding (per the standard
    # S_GAP convention).
    rules.append(Rule(
        "S_GAP",
        ["PART[LOC_EXISTENTIAL]", "N"],
        [
            "(↑ PRED) = 'LOC <SUBJ>'",
            "(↑ SUBJ) = (↑ REL-PRO)",
            "(↑ LOCATION) = ↓2",
            "(↑ CLAUSE_TYPE) = 'LOC_EXISTENTIAL'",
            "(↓1 LOC_EXISTENTIAL) =c true",
        ],
    ))
    rules.append(Rule(
        "S_GAP",
        ["PART[LOC_EXISTENTIAL]", "N", "NP[CASE=GEN]"],
        [
            "(↑ PRED) = 'LOC <SUBJ>'",
            "(↑ SUBJ) = (↑ REL-PRO)",
            "(↑ LOCATION) = ↓2",
            "(↓2 POSS) = ↓3",
            "(↑ CLAUSE_TYPE) = 'LOC_EXISTENTIAL'",
            "(↓1 LOC_EXISTENTIAL) =c true",
        ],
    ))


    # === Phase 5n.B Commit 3: predicative-ADJ gapped clause for ay-fronting (§18 L39) =====
    #
    # ``Si Maria ay maganda.``
    #     "Maria is beautiful." (ay-fronted predicative-ADJ)
    # ``Si Maria ay mas matalino.``
    #     "Maria is more intelligent." (ay-fronted comparative)
    # ``Si Maria ay mas matalino kaysa kay Juan.``
    #     "Maria is more intelligent than Juan." (ay-fronted
    #     comparative + kaysa-PP)
    # ``Si Maria ay pinakamatalino.``
    #     "Maria is the most intelligent." (ay-fronted superlative)
    # ``Si Maria ay kasingganda ni Ana.``
    #     "Maria is as beautiful as Ana." (ay-fronted equative +
    #     GEN-standard)
    #
    # Closes §18 deferral L39. Phase 4 §7.4 ay-fronting was built
    # for V-pivot clauses (S_GAP); Phase 5g introduced predicative-
    # ADJ clauses, and Phase 5h added comparative / superlative /
    # equative / intensive variants through ADJ wrappers and
    # paradigm-derived ADJ heads. The ADJ-pivot ay-fronting needs a
    # parallel gap non-terminal (``S_GAP_PREDADJ``) that captures
    # the predicative-ADJ residue (the predicative-ADJ S minus its
    # NOM-NP SUBJ daughter) and binds the SUBJ slot to REL-PRO.
    #
    # Two S_GAP_PREDADJ shapes cover the predicative-ADJ residue
    # variants:
    #
    #   1. Bare predicative-ADJ:
    #      ``S_GAP_PREDADJ → ADJ[PREDICATIVE]``
    #      Covers ``maganda`` / ``matanda`` / ``mas matalino`` /
    #      ``pinakamatalino`` / ``kasingganda`` (single-token
    #      paradigm forms and mas/pinaka-wrapped variants).
    #
    #   2. Equative + GEN-standard:
    #      ``S_GAP_PREDADJ → ADJ[COMP_DEGREE=EQUATIVE]
    #                         NP[CASE=GEN]``
    #      Covers ``kasingganda ni Ana``. The equative two-NP
    #      Phase 5h Commit 6 frames build the matrix S directly
    #      with both NP daughters; ay-fronted versions need the
    #      gap variant to admit the GEN-standard alongside the
    #      ADJ residue.
    #
    # **What's NOT in S_GAP_PREDADJ**: the kaysa-PP attachment
    # (``mas matalino kaysa kay Juan``) is already handled by the
    # existing Phase 5h Commit 4 kaysa wrap rule (``S → S
    # PART[KAYSA] NP[CASE=DAT]``), which composes on top of the
    # ay-fronted bare-ADJ S produced by shape (1) + the wrap rule
    # below. Adding a kaysa variant inside S_GAP_PREDADJ would
    # produce spurious ambiguity (two parse paths for the same
    # surface).
    #
    # **Recursive negation** (shape 3): admits ``hindi`` inside
    # the predicative-ADJ residue (``Si Maria ay hindi
    # maganda.``), parallel to the Phase 4 §7.4 S_GAP recursive
    # negation rule above. Without this, the ay-fronted negated
    # predicative-ADJ surface 0-parses.
    #
    # The wrap rule ``S → NP[CASE=NOM] PART[LINK=AY]
    # S_GAP_PREDADJ`` is added below alongside the existing
    # Phase 4 §7.4 V-pivot wrap.
    rules.append(Rule(
        "S_GAP_PREDADJ",
        ["ADJ[PREDICATIVE]"],
        [
            "(↑ PRED) = 'ADJ <SUBJ>'",
            "(↑ SUBJ) = (↑ REL-PRO)",
            "(↑ ADJ_LEMMA) = ↓1 LEMMA",
            "(↑ PREDICATIVE) = true",
            "(↓1 PREDICATIVE) =c true",
        ],
    ))
    rules.append(Rule(
        "S_GAP_PREDADJ",
        ["ADJ[COMP_DEGREE=EQUATIVE]", "NP[CASE=GEN]"],
        [
            "(↑ PRED) = 'ADJ <SUBJ>'",
            "(↑ SUBJ) = (↑ REL-PRO)",
            "(↑ ADJ_LEMMA) = ↓1 LEMMA",
            "(↑ PREDICATIVE) = true",
            "(↓1 PREDICATIVE) =c true",
            "(↓1 COMP_DEGREE) =c 'EQUATIVE'",
            "↓2 ∈ (↑ ADJUNCT)",
            "(↓2 ROLE) = 'EQUATIVE_STANDARD'",
        ],
    ))
    # ``(↓1 POLARITY) =c 'NEG'`` is load-bearing here: without the
    # constraining equation the non-conflict-matcher admits any
    # PART for the first daughter (e.g., ``mas`` PART
    # [COMP_DEGREE=COMPARATIVE]), which then duplicates the
    # ay-fronted comparative parse via this recursive rule. The
    # belt-and-braces ``=c`` closes the leak per the Phase 5n.A
    # ``project_parser_nonconflict_matcher`` finding.
    rules.append(Rule(
        "S_GAP_PREDADJ",
        ["PART[POLARITY=NEG]", "S_GAP_PREDADJ"],
        [
            "(↑) = ↓2",
            "(↑ POLARITY) = 'NEG'",
            "(↓1 POLARITY) =c 'NEG'",
        ],
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

    # --- Phase 8.V: Ni-SUBJ focus negation (``Ni X ay hindi Y``) -------------
    #
    # ``Ni si Juan ay hindi nakapunta doon.``
    #     "Not even Juan went there." (S&O 1972 §7.20 page 640 / sent-1260)
    #
    # Tagalog has a focus-negation construction in which the
    # SUBJ-pivot of a negated AV clause is fronted with a leading
    # ``Ni`` "not even" focus particle, then ``ay`` + the gapped
    # remainder of the clause. Semantically: the focused NP is
    # asserted to be the LEAST EXPECTED bearer of the negated
    # predicate ("not even X, so certainly not anyone else").
    #
    # Structure (mirrors the Phase 4 §7.4 SUBJ-ay-front rule above
    # with a leading PART[FOCUS_NEG] daughter and a POLARITY=NEG
    # gate on the inner S_GAP):
    #
    #   S → PART[FOCUS_NEG=true]  NP[CASE=NOM]  PART[LINK=AY]  S_GAP
    #     (↑) = ↓4
    #     (↑ TOPIC) = ↓2
    #     (↑ FOCUS_NEG) = true
    #     (↓4 REL-PRO) = ↓2
    #     (↓4 REL-PRO) =c (↓4 SUBJ)
    #     (↓4 POLARITY) =c 'NEG'
    #     (↓1 FOCUS_NEG) =c true
    #
    # The POLARITY=NEG gate means the inner clause must be
    # hindi-negated — affirmative ``Ni si Juan ay nakapunta doon.``
    # is structurally blocked (Ni without hindi is not attested in
    # the corpus and S&O 1972 confirms the construction obligatorily
    # pairs with NEG).
    #
    # The FOCUS_NEG=true matrix tag lets downstream consumers (LMT,
    # ranker, classifier) branch on the "not even" reading without
    # walking the c-structure for the Ni daughter. ``ni`` lex is in
    # particles.yaml as a second entry (distinct from the existing
    # GEN proper-name ``ni``) with ``FOCUS_NEG=true``; the two
    # readings disambiguate by the following daughter shape (GEN
    # admits a bare proper-name NOUN, FOCUS_NEG admits a full NP +
    # ay + S_GAP).
    #
    # Out of 8.V scope (pinned for future construction sub-PRs):
    #   * OBJ-focus / non-SUBJ-pivot Ni-X (needs S_GAP_OBJ-style
    #     extraction): ``Ni damit ni sapatos ay hindi nakakabili
    #     ang taong iyon.`` — S&O page 604 / sent-1156.
    #   * OF-voice Ni-AGENT focus: ``Ni si Juan ni si Ben ay hindi
    #     bibilhin iyan.`` — S&O page 604 / sent-1159.
    #   * Paired Ni X ni Y correlative coordination of foci.
    #   * ``Ni hindi V`` (no ``ay``) intensifier-negation — a
    #     distinct construction from the focus-negation here:
    #     ``Ni hindi ko napapansin.`` — R&G Intermediate sent-1828.
    rules.append(Rule(
        "S",
        [
            "PART[FOCUS_NEG=true]",
            "NP[CASE=NOM]",
            "PART[LINK=AY]",
            "S_GAP",
        ],
        [
            "(↑) = ↓4",
            "(↑ TOPIC) = ↓2",
            "(↑ FOCUS_NEG) = true",
            "(↓4 REL-PRO) = ↓2",
            "(↓4 REL-PRO) =c (↓4 SUBJ)",
            "(↓4 POLARITY) =c 'NEG'",
            "(↓1 FOCUS_NEG) =c true",
        ],
    ))


    # --- Phase 9.R: Non-SUBJ Ni-focus (B3.E) -------------------
    #
    # ``Ni ito ay hindi umiinom si Rosa.`` (S&O 1972 page 603 /
    #     sent-1154 — 8.V `test_non_subj_ni_focus` pin)
    #     "Not even this is Rosa drinking." / "Rosa isn't even
    #     drinking this."
    #
    # Extends the Phase 8.V SUBJ-focus Ni-X rule above to non-SUBJ
    # in-clause GFs: OBJ (AV verbs with extractable PATIENT),
    # OBJ-AGENT (non-AV verbs with extractable GEN-actor), and OBL
    # (locative/directional DAT-NPs).
    #
    # Per S&O 1972 §7.20: the ``Ni X`` focus-negation construction
    # admits any in-clause GF as the fronted-and-negated element.
    # 8.V closed the SUBJ-case via ``S_GAP``; this rule family
    # closes the non-SUBJ cases by paralleling 8.V's structure for
    # each existing non-pivot ay-fronting gap category (line 945:
    # GEN+S_GAP_OBJ, line 958: GEN+S_GAP_OBJ_AGENT, line 973:
    # DAT+S_GAP_OBL).
    #
    # **Case marking on the fronted Ni-NP**: in 8.V's SUBJ-focus
    # the fronted NP carries CASE=NOM (matching the SUBJ pivot's
    # native case). For non-SUBJ Ni-focus, audit-attested
    # ``Ni ito ay hindi umiinom si Rosa.`` shows the fronted NP
    # still carries NOM (``ito`` is a NOM-only DEM). Per S&O §7.20,
    # the ``Ni`` particle absorbs the case marker, leaving the
    # fronted NP's morphological case to be supplied by the
    # default (NOM) for non-PP topics. OBL-position keeps DAT
    # because the locative ground retains its ``sa``-PP morphology
    # (``Ni sa bahay`` would still surface as ``sa bahay`` with
    # CASE=DAT).
    #
    # **Disambiguation against 8.V**: the inner-clause non-terminal
    # is what selects between rules:
    # * 8.V fires only on ``S_GAP`` (SUBJ missing) — fails when the
    #   inner has an explicit SUBJ like ``si Rosa``.
    # * 9.R rules fire on ``S_GAP_OBJ`` / ``S_GAP_OBJ_AGENT`` /
    #   ``S_GAP_OBL`` — these tolerate an in-clause SUBJ and have
    #   the relevant non-SUBJ slot missing.
    # The 8.V SUBJ-focus and 9.R non-SUBJ-focus rules are mutually
    # exclusive on the inner-clause shape.
    #
    # All three 9.R rules carry the same FOCUS_NEG / POLARITY=NEG
    # gates as 8.V; the only structural differences are the
    # fronted NP's CASE and the inner gap category.

    # 9.R Rule 1: Ni-OBJ-focus (AV verb with extractable OBJ)
    # ``Ni ito ay hindi umiinom si Rosa.``
    #     "Rosa isn't drinking even this."
    rules.append(Rule(
        "S",
        [
            "PART[FOCUS_NEG=true]",
            "NP[CASE=NOM]",
            "PART[LINK=AY]",
            "S_GAP_OBJ",
        ],
        [
            "(↑) = ↓4",
            "(↑ TOPIC) = ↓2",
            "(↑ FOCUS_NEG) = true",
            "(↓4 REL-PRO) = ↓2",
            "(↓4 REL-PRO) =c (↓4 OBJ)",
            "(↓4 POLARITY) =c 'NEG'",
            "(↓1 FOCUS_NEG) =c true",
        ],
    ))

    # 9.R Rule 2: Ni-OBJ-AGENT-focus (non-AV verb, GEN-actor
    # extracted with Ni absorbing case)
    # ``Ni si Maria ay hindi kinain ang aklat.``
    #     "Not even Maria has the book been eaten by."
    rules.append(Rule(
        "S",
        [
            "PART[FOCUS_NEG=true]",
            "NP[CASE=NOM]",
            "PART[LINK=AY]",
            "S_GAP_OBJ_AGENT",
        ],
        [
            "(↑) = ↓4",
            "(↑ TOPIC) = ↓2",
            "(↑ FOCUS_NEG) = true",
            "(↓4 REL-PRO) = ↓2",
            "(↓4 REL-PRO) =c (↓4 OBJ-AGENT)",
            "(↓4 POLARITY) =c 'NEG'",
            "(↓1 FOCUS_NEG) =c true",
        ],
    ))

    # 9.R Rule 3: Ni-OBL-focus (any voice, locative DAT-NP
    # extracted with Ni preserving the sa-PP morphology)
    # ``Ni sa bahay ay hindi pumunta si Juan.``
    #     "Juan didn't go even to the house."
    # OBL binds to ADJUNCT set (no scalar REL-PRO equation —
    # mirrors the existing non-pivot OBL ay-fronting rule).
    rules.append(Rule(
        "S",
        [
            "PART[FOCUS_NEG=true]",
            "NP[CASE=DAT]",
            "PART[LINK=AY]",
            "S_GAP_OBL",
        ],
        [
            "(↑) = ↓4",
            "(↑ TOPIC) = ↓2",
            "(↑ FOCUS_NEG) = true",
            "(↓4 REL-PRO) = ↓2",
            "(↓4 POLARITY) =c 'NEG'",
            "(↓1 FOCUS_NEG) =c true",
        ],
    ))


    # --- Phase 9.S: Paired Ni X ni Y correlative coordination (B3.E) ---
    #
    # ``Ni si Juan ni si Maria ay hindi kumain.``
    #     "Neither Juan nor Maria ate."
    # ``Ni si Juan ni si Ben ay hindi bibilhin iyan.``
    #     (S&O 1972 p.604 / sent-1159 — 8.V pin)
    #     "Neither Juan nor Ben will that be bought by."
    # ``Ni damit ni sapatos ay hindi nakakabili ang taong iyon.``
    #     (S&O 1972 p.604 / sent-1156)
    #     "Neither clothes nor shoes can that person buy."
    # ``Ni ngayon ni hulas ay hindi ako makakaalis.``
    #     (R&G Conv)
    #     "Neither today nor tomorrow can I leave."
    #
    # Closes the 8.V `test_paired_ni_correlative` pin. Per S&O 1972
    # §7.20, ``Ni X ni Y`` correlatively coordinates two foci, both
    # negated by the matrix's `hindi`. Structurally extends the
    # Phase 8.V SUBJ-focus and Phase 9.R Non-SUBJ-focus rules with
    # a second ``PART[FOCUS_NEG=true] NP[CASE=X]`` daughter inserted
    # before the ``ay`` particle.
    #
    # Four rules — one per gap category (SUBJ + OBJ + OBJ-AGENT +
    # OBL) — mirroring the 8.V + 9.R rule family. The fronted-NP
    # case is NOM for SUBJ / OBJ / OBJ-AGENT (Ni absorbs the case
    # marker), DAT for OBL (sa-PP morphology retained).
    #
    # F-structure shape:
    #
    #   TOPIC          = ↓2 (first conjunct — primary focus)
    #   NI_CONJUNCTS   ⊇ {↓4} (second conjunct rides as set member)
    #   FOCUS_NEG      = true
    #   POLARITY       = 'NEG'
    #   (gap)          binds to ↓2 via REL-PRO
    #
    # The gap binds to the first conjunct's f-structure; semantically
    # the negation distributes over both conjuncts ("neither X nor Y
    # did Z"), but the structural binding pin is the first conjunct
    # to match the LFG convention for ay-fronted topic-gap relations.
    # The second conjunct rides on a NI_CONJUNCTS set so downstream
    # consumers can recover the paired structure.
    #
    # Same POLARITY=NEG and FOCUS_NEG=true gates as 8.V / 9.R; both
    # ↓1 and ↓3 must be ``FOCUS_NEG=true`` particles (the two ``ni``
    # tokens).

    # 9.S Rule 1: Paired-Ni SUBJ-focus
    rules.append(Rule(
        "S",
        [
            "PART[FOCUS_NEG=true]",
            "NP[CASE=NOM]",
            "PART[FOCUS_NEG=true]",
            "NP[CASE=NOM]",
            "PART[LINK=AY]",
            "S_GAP",
        ],
        [
            "(↑) = ↓6",
            "(↑ TOPIC) = ↓2",
            "↓4 ∈ (↑ NI_CONJUNCTS)",
            "(↑ FOCUS_NEG) = true",
            "(↓6 REL-PRO) = ↓2",
            "(↓6 REL-PRO) =c (↓6 SUBJ)",
            "(↓6 POLARITY) =c 'NEG'",
            "(↓1 FOCUS_NEG) =c true",
            "(↓3 FOCUS_NEG) =c true",
        ],
    ))

    # 9.S Rule 2: Paired-Ni OBJ-focus
    rules.append(Rule(
        "S",
        [
            "PART[FOCUS_NEG=true]",
            "NP[CASE=NOM]",
            "PART[FOCUS_NEG=true]",
            "NP[CASE=NOM]",
            "PART[LINK=AY]",
            "S_GAP_OBJ",
        ],
        [
            "(↑) = ↓6",
            "(↑ TOPIC) = ↓2",
            "↓4 ∈ (↑ NI_CONJUNCTS)",
            "(↑ FOCUS_NEG) = true",
            "(↓6 REL-PRO) = ↓2",
            "(↓6 REL-PRO) =c (↓6 OBJ)",
            "(↓6 POLARITY) =c 'NEG'",
            "(↓1 FOCUS_NEG) =c true",
            "(↓3 FOCUS_NEG) =c true",
        ],
    ))

    # 9.S Rule 3: Paired-Ni OBJ-AGENT-focus
    rules.append(Rule(
        "S",
        [
            "PART[FOCUS_NEG=true]",
            "NP[CASE=NOM]",
            "PART[FOCUS_NEG=true]",
            "NP[CASE=NOM]",
            "PART[LINK=AY]",
            "S_GAP_OBJ_AGENT",
        ],
        [
            "(↑) = ↓6",
            "(↑ TOPIC) = ↓2",
            "↓4 ∈ (↑ NI_CONJUNCTS)",
            "(↑ FOCUS_NEG) = true",
            "(↓6 REL-PRO) = ↓2",
            "(↓6 REL-PRO) =c (↓6 OBJ-AGENT)",
            "(↓6 POLARITY) =c 'NEG'",
            "(↓1 FOCUS_NEG) =c true",
            "(↓3 FOCUS_NEG) =c true",
        ],
    ))

    # 9.S Rule 4: Paired-Ni OBL-focus
    rules.append(Rule(
        "S",
        [
            "PART[FOCUS_NEG=true]",
            "NP[CASE=DAT]",
            "PART[FOCUS_NEG=true]",
            "NP[CASE=DAT]",
            "PART[LINK=AY]",
            "S_GAP_OBL",
        ],
        [
            "(↑) = ↓6",
            "(↑ TOPIC) = ↓2",
            "↓4 ∈ (↑ NI_CONJUNCTS)",
            "(↑ FOCUS_NEG) = true",
            "(↓6 REL-PRO) = ↓2",
            "(↓6 POLARITY) =c 'NEG'",
            "(↓1 FOCUS_NEG) =c true",
            "(↓3 FOCUS_NEG) =c true",
        ],
    ))


    # --- Phase 7a.F: kahit-X SUBJ no-`ay` colloquial (§18.1.1 item 8) ---
    #
    # `Kahit sino kumain.` "Anyone could eat" — colloquial Tagalog
    # admits the pre-V kahit-X SUBJ fronting WITHOUT the `ay`
    # particle. Phase 5n.B C20 closed the canonical `ay`-fronted
    # form (`Kahit sino ay kumain.`); this variant drops the
    # `ay` daughter for the colloquial register.
    #
    # The rule mirrors the Phase 4 §7.4 ay-fronted rule above
    # exactly except:
    #   - drops the PART[LINK=AY] daughter (daughter indices
    #     shift: S_GAP becomes ↓2);
    #   - gates the NP daughter to INDEF=YES, preventing
    #     overgeneration on bare-NP SUBJ-fronting (which
    #     colloquial Tagalog disallows; only indefinite-NP
    #     fronting is admissible without `ay`);
    #   - adds (↑ REGISTER) = 'COLLOQUIAL' so downstream
    #     consumers can filter colloquial parses.
    #
    # INDEF=YES is the feat the Phase 5m Commit 8 IndefPRON rule
    # (`PRON → PART PRON` with `(↓1 LEMMA) =c 'kahit'`) sets on
    # kahit-X compositions. Any future indefinite construction
    # that compositionally sets INDEF=YES will also license this
    # colloquial fronting.
    rules.append(Rule(
        "S",
        ["NP[CASE=NOM]", "S_GAP"],
        [
            "(↑) = ↓2",
            "(↑ TOPIC) = ↓1",
            "(↓2 REL-PRO) = ↓1",
            "(↓2 REL-PRO) =c (↓2 SUBJ)",
            "(↓1 INDEF) =c 'YES'",
            "(↑ REGISTER) = 'COLLOQUIAL'",
        ],
    ))

    # --- Phase 5n.B Commit 3: ADJ-pivot ay-fronting wrap (§18 L39) ---
    #
    # ``Si Maria ay maganda.`` "Maria is beautiful."
    # ``Si Maria ay mas matalino kaysa kay Juan.``
    #     "Maria is more intelligent than Juan."
    # ``Si Maria ay pinakamatalino.`` "Maria is the most intelligent."
    # ``Si Maria ay kasingganda ni Ana.``
    #     "Maria is as beautiful as Ana."
    #
    # Closes §18 L39 (ay-inversion of comparative ADJ; carried
    # forward from Phase 5g §10 / Phase 5h §9.2). Parallel to the
    # Phase 4 §7.4 V-pivot ay-fronting rule above, with the inner
    # clause being the new Phase 5n.B Commit 3 ``S_GAP_PREDADJ``
    # gap non-terminal (predicative-ADJ residue with SUBJ slot
    # bound to REL-PRO).
    #
    # The fronted-XP type (NP[CASE=NOM]) is the same as the
    # V-pivot ay-fronting; the disambiguation between the two
    # rules is via the inner-clause non-terminal: ``S_GAP``
    # (V-headed) vs ``S_GAP_PREDADJ`` (predicative-ADJ-headed).
    # Both rules fire only on their respective inner-clause
    # shapes; no cross-firing.
    rules.append(Rule(
        "S",
        ["NP[CASE=NOM]", "PART[LINK=AY]", "S_GAP_PREDADJ"],
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

    # --- Phase 9.W Cluster A/H: compound TIME AdvP -----------------
    #
    # ``bukas ng gabi``      "tomorrow evening"
    # ``kahapon ng gabi``    "yesterday evening"
    # ``ngayong gabi``       (split-linker; handled by tokenizer)
    #
    # Closes S&O 1972 p.441 sent-676 ``Sila rin ay sasayaw ng
    # pandanggo bukas ng gabi.`` "They will also dance the pandango
    # tomorrow evening." The compound combines a deictic-time ADV
    # (``bukas`` / ``kahapon`` / ``ngayon``) with a time-of-day N
    # via the ``ng`` genitive marker. The resulting AdvP refines
    # the deixis at a specific time-of-day; semantically the
    # time-of-day N rides as a TIME-N modifier on the matrix ADV's
    # f-structure, with the head's ADV_TYPE and DEIXIS_TIME
    # percolating.
    #
    # Note: ``ng`` between ADV and N is the GEN case marker
    # (``ADP[CASE=GEN, MARKER=NG]``), not the bound linker ``-ng``
    # (``PART[LINK=NG]``). The literal gloss is "tomorrow of the
    # evening" — a possessive / part-of relation rather than a
    # restrictive modifier.
    #
    # F-structure: matrix is the ADV head (``(↑) = ↓1``); the
    # time-N attaches as ``TIME_N`` slot. ADV_TYPE=TIME on the head
    # is the gate; SEM_CLASS=TIME on the N daughter narrows the
    # rule to time-of-day nouns (gabi / umaga / hapon / tanghali).
    rules.append(Rule(
        "AdvP",
        [
            "ADV[ADV_TYPE=TIME]",
            "NP[CASE=GEN]",
        ],
        _eqs(
            "(↑) = ↓1",
            "(↑ TIME_N) = ↓2",
            "(↓1 ADV_TYPE) =c 'TIME'",
            "(↓2 CASE) =c 'GEN'",
            "(↓2 SEM_CLASS) =c 'TIME'",
        ),
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

    # --- 9.X.c10: ay-fronting a bare DAT-NP as topic adjunct ----
    #
    # ``Sa tag-init ay manaka-naka lamang ang ulan.`` "In summer,
    # the rain is only occasional" (R&G 1981 PANAHON sent-4).
    # ``Sa bahay ay umuwi siya.`` "At home, he went home."
    #
    # Parallel to the AdvP-ay-S and PP-ay-S rules above, but with
    # a bare DAT-NP daughter (``Sa N``, ``Sa NP``) admitting the
    # topic-adjunct reading of sentence-initial sa-PPs. The bare
    # DAT-NP path differs from the PP path: PP is built by the
    # discourse-module rules (``tuwing Lunes``, ``noong Pebrero``
    # — TIME_FRAME PARTs); the canonical ``sa NP`` locative /
    # temporal is built as ``NP[CASE=DAT]`` via ADP+N.
    #
    # The fronted DAT-NP joins ADJ via set-membership and is
    # marked as the matrix's TOPIC. The inner clause is a bare
    # S (no gap) — the DAT-NP is a sentential adjunct, not an
    # extracted OBL argument. The existing OBL-fronting rule
    # (line 1284, ``S → NP[CASE=DAT] PART[LINK=AY] S_GAP_OBL``)
    # handles the case where the DAT-NP IS the inner clause's
    # OBL-θ argument; this rule handles the non-governed
    # adjunct case where the DAT-NP scopes over the clause
    # without filling any subcategorized slot.
    #
    # For sentences where the inner S admits both readings (e.g.,
    # ``Sa parke ay pumunta si Maria.`` — pumunta has OBL-LOC slot),
    # both rules fire and produce distinct parses (governed-OBL vs
    # topic-adjunct). This is the standard PP-attachment ambiguity
    # (parallel to 9.X.c8 NP-internal sa-PP modifier ambiguity);
    # both readings are linguistically valid.
    #
    # Reference: R&G 1981 §7.4 (ay-fronting topic adjuncts); R&G
    # 1981 PANAHON essay (sent-4).
    rules.append(Rule(
        "S",
        ["NP[CASE=DAT]", "PART[LINK=AY]", "S"],
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
    # Structure: ``DET[CASE=X, DEM=false] S_GAP``. The bare case
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
            f"DET[CASE={case}, DEM=false]"
            if case == "NOM"
            else f"ADP[CASE={case}, DEM=false]"
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


    # --- Phase 4 §7.5 + Phase 6.D Commit 2: relativization ---
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
    # RC's SUBJ to REL-PRO inside S_GAP. Documented in
    # ``docs/analysis-choices.md`` "Phase 4 §7.5" / "Phase 6.D
    # Commit 1".
    #
    # **Phase 6.D Commit 2 (2026-05-12) — FU gap binding.** The
    # original Phase 4 §7.5 ``(↓3 REL-PRO) =c (↓3 SUBJ)``
    # constraining equation is generalized to a K&Z 1989 §3
    # eq. 39 FU path
    #
    #     (↓3 REL-PRO) =c (↓3 XCOMP* SUBJ)
    #
    # which navigates the gap via zero-or-more XCOMP traversals.
    # Body: ``XCOMP*`` (control chains); bottom: ``SUBJ``
    # (Kroeger 1993 SUBJ-only). The broader plan-skeleton form
    # ``(↑ {COMP, XCOMP}* SUBJ)`` is narrowed to XCOMP* in 6.D —
    # Tagalog COMP-internal SUBJs aren't reachable under the
    # SUBJ-only restriction, so widening would overgenerate.
    #
    # **Constraining-form realization of the LFG binding.** The
    # design appendix C1 envisioned a defining-form equation
    # (``= (↓3 XCOMP* SUBJ)``), but our two-pass orchestration
    # evaluates defining-equations parent-first — at the time
    # the wrap rule fires, the S_GAP body's
    # ``(↑ SUBJ) = (↑ REL-PRO)`` hasn't run yet, so ↓3.SUBJ
    # doesn't exist and a defining FU resolves to no endpoint.
    # The K&Z 1989 binding is therefore realized as the
    # combination of (a) the S_GAP body's defining equation
    # creating the SUBJ=REL-PRO reentrancy, plus (b) this
    # constraining FU equation verifying that the reentrancy
    # holds along an XCOMP* path. Equivalent K&Z semantics; the
    # deferred-defining-FU mechanism would be a Phase 7+
    # unifier extension.
    #
    # The change is **vacuous at depth 1** (S_GAP body already
    # binds SUBJ=REL-PRO via the body's own
    # ``(↑ SUBJ) = (↑ REL-PRO)`` equation; the constraining FU
    # equation's zero-iteration endpoint reaches the same
    # f-node and the check passes). The FU form is
    # load-bearing under the new S_XCOMP-bodied wrap below,
    # which admits cross-clausal RCs at depths 2+ — the FU
    # path enumerates SUBJ at every level of the XCOMP chain
    # and verifies REL-PRO ≡ at-least-one of them.
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
                    "(↓3 REL-PRO) =c (↓3 XCOMP* SUBJ)",
                ],
            ))

    # --- Phase 6.D Commit 2: S_XCOMP-bodied RC wrap (L47) ---
    #
    # Closes §18.1.2 L47 (long-distance wh-extraction).
    # Cross-clausal relativization at depths 2+: ``ang batang
    # gustong kumain`` ("the child who wants to eat"), ``ang
    # batang gustong pumayag na kumain`` ("the child who wants
    # to agree to eat"), and arbitrarily deeper XCOMP chains.
    #
    # The body is ``S_XCOMP`` (the SUBJ-gapped clause that the
    # Phase 4 §7.6 / Phase 5c §7.6 follow-on control work
    # produces for control complements). ``cfg/control.py``'s
    # per-depth REL-PRO threading already unifies the bottom-of-
    # chain SUBJ with the matrix REL-PRO across any depth; this
    # wrap rule is the outer composer that puts an ``S_XCOMP``
    # body alongside the head NP.
    #
    # The FU constraining equation is identical to the S_GAP
    # wrap above — ``(↓3 REL-PRO) =c (↓3 XCOMP* SUBJ)`` — but
    # here it does real work: ``↓3`` is the S_XCOMP daughter
    # (depth 0 of the chain), and the XCOMP* enumeration
    # reaches the SUBJ at any depth. K&Z 1989 §3 minimality
    # selects endpoints shortest-first; under per-depth control
    # threading every SUBJ along the chain is the same f-node,
    # so the depth-0 endpoint satisfies the check.
    #
    # Design rationale + scope boundaries: ``docs/analysis-
    # choices.md`` "Phase 6.D Commit 1: L47 long-distance
    # relativization via FU — design". See also the
    # constraining-form-realization note on the S_GAP wrap
    # above for why this isn't a defining-form binding.
    for case in ("NOM", "GEN", "DAT"):
        np_cat = f"NP[CASE={case}]"
        for link in ("NA", "NG"):
            rules.append(Rule(
                np_cat,
                [np_cat, f"PART[LINK={link}]", "S_XCOMP"],
                [
                    "(↑) = ↓1",
                    "↓3 ∈ (↑ ADJ)",
                    "(↓3 REL-PRO PRED) = (↓1 PRED)",
                    "(↓3 REL-PRO CASE) = (↓1 CASE)",
                    "(↓3 REL-PRO) =c (↓3 XCOMP* SUBJ)",
                ],
            ))

    # --- Phase 5n.B Commit 21: PRON-headed RC for negative indefinites
    #
    # ``Walang sinumang dumating.``  "Nobody came."
    # ``Walang anumang nakita.``     "Nothing was seen."
    #
    # Closes §18.1 deferral L101. Parallel to the Phase 4 §7.5
    # N-headed relativization above, but with ``PRON`` as the head
    # category instead of NP, gated on ``(↓1 INDEF) =c 'NEG_INDEF'``
    # to keep the rule narrow to negative-indefinite PRONs
    # (``sinuman`` "no one", ``anuman`` "nothing"). Other PRONs
    # (``siya`` / ``ako`` / ``niya`` / ...) lack the INDEF feat and
    # so the rule does not fire on them — they are not naturally
    # RC-headed.
    #
    # The RC body is an ``S_GAP`` (SUBJ-gapped clause) following
    # the Phase 4 §7.5 SUBJ-only-relativization restriction
    # (Kroeger 1993). The gap binds to the head PRON via
    # ``(↓3 REL-PRO) =c (↓3 SUBJ)`` (anaphoric, not structure-
    # sharing — same convention as the N-headed rule).
    #
    # The new rule produces a ``PRON``, so the existing Phase 5m
    # Commit 9 negative-existential rule (``S → PART[EXISTENTIAL=
    # YES, POLARITY=NEG] PART[LINK=NG] PRON[INDEF=NEG_INDEF]``,
    # ``cfg/clause.py``) consumes the relativized PRON without
    # modification — closing the path that the Phase 5m comment
    # ("the relative-clause grammar handles sinumang dumating")
    # had anticipated but not yet implemented.
    # LHS advertises ``INDEF=NEG_INDEF`` so the Phase 5j Commit 9
    # negative-existential rule (which expects
    # ``PRON[INDEF=NEG_INDEF]``) admits this rule's LHS under the
    # Phase 6.C graph-constraint matcher. ``(↑) = ↓1`` already
    # propagates INDEF=NEG_INDEF on the f-graph; the LHS pattern
    # advertises the same so completion sees it.
    for link in ("NA", "NG"):
        rules.append(Rule(
            "PRON[INDEF=NEG_INDEF]",
            [
                "PRON[INDEF=NEG_INDEF]",
                f"PART[LINK={link}]",
                "S_GAP",
            ],
            [
                "(↓1 INDEF) =c 'NEG_INDEF'",
                f"(↓2 LINK) =c '{link}'",
                "(↑) = ↓1",
                "↓3 ∈ (↑ ADJ)",
                # The SUBJ-gap binding constraint enforces that the
                # head PRON fills the RC's SUBJ slot. We omit the
                # REL-PRO PRED/CASE defining-equation copies (used
                # by the N-headed relativization above) because the
                # head's f-structure is already shared with the
                # matrix via ``(↑) = ↓1``; the SUBJ-gap binding
                # picks up the head's identity transitively without
                # a separate REL-PRO copy. Skipping the copies also
                # avoids an empty-FStructure leak when the head's
                # PRED is undefined (a structural concern with
                # PRON heads — though the INDEF=NEG_INDEF gate
                # restricts to sinuman / anuman, both of which do
                # have PREDs, the simpler equation set is more
                # robust).
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


    # --- Phase 6.E Commit 2: free relative kung-S as DP (§18.1 L93) ---
    #
    # ``Galit ako sa kung sino ang nag-record.``
    #     "I'm angry at whoever recorded it."         (DAT-OBL)
    # ``Tumakbo ang kung sino ang gutom.``
    #     "Whoever was hungry ran."                   (NOM-SUBJ)
    # ``Bumili ako ng kung ano ang mura.``
    #     "I bought whatever was cheap."              (GEN-OBJ)
    #
    # Closes §18.1.2 L93. A ``kung``-headed wh-clause functions as a
    # non-COMP NP argument of the matrix predicate — the free-relative
    # reading ("whoever did X" / "whatever was X-ed"). Parallel to the
    # Phase 5e Commit 5 headless / free relative rule above, but the
    # body is a kung-S (``S_INTERROG_COMP``) rather than a SUBJ-gapped
    # ``S_GAP``.
    #
    # **Structure**: ``CASE-MARKER[DEM=false] S_INTERROG_COMP``. The
    # bare case-marker (``ang`` for NOM via ``DET``; ``ng`` for GEN,
    # ``sa`` for DAT via ``ADP``) plus the kung-wrapped wh-cleft forms
    # the free-relative NP. ``DEM=false`` excludes demonstrative DET /
    # ADP entries (``ito`` / ``iyan`` / ``iyon``); the morph analyzer
    # default-fills ``DEM=false`` on non-demonstrative DET / ADP
    # entries so the matcher accepts ``ang`` / ``ng`` / ``sa`` here.
    #
    # **F-structure**: ``PRED='PRO'`` (the free-relative head),
    # ``FREE_REL=true`` (marker for downstream consumers),
    # ``WH_LEMMA`` lifted from the inner S (the wh-pivot's lemma).
    # The kung-S sits in the head NP's ``ADJ`` set as a clausal
    # modifier. ``MARKER`` propagates from the case-marker daughter.
    #
    # The constraining equations on ``↓2`` gate the rule to the
    # **wh-variant** of ``S_INTERROG_COMP`` (Phase 5i Commit 8):
    # ``COMP_TYPE=INTERROG`` plus ``Q_TYPE=WH``. The yes/no-with-ba
    # variant (Phase 5n.B Commit 11) sets ``COMP_QTYPE=YES_NO`` and
    # ``Q_TYPE=YES_NO`` on the f-structure; the bare-declarative
    # variant (Phase 5n.B Commit 11) sets ``COMP_QTYPE=YES_NO`` and
    # has no ``Q_TYPE``. The ``(↓2 Q_TYPE) =c 'WH'`` check fails for
    # both alternative variants, blocking spurious free-relative
    # parses on declarative or yes/no kung-S.
    #
    # **Disambiguation from indirect-Q kung-S** (Phase 5i Commit 8 +
    # Phase 5n.A Commit 29): selectional. The matrix predicate's
    # argument frame selects either ``S_INTERROG_COMP`` (COMP-binding
    # under KNOW-class / ASK-class) or a case-marked ``NP`` (this
    # rule). Both parses coexist on surfaces where the matrix frame
    # admits both shapes — the free-relative path is disjoint from
    # the indirect-Q path at the c-structure boundary.
    #
    # Design rationale + scope: ``docs/analysis-choices.md``
    # "Phase 6.E Commit 1: L93 free relative kung-S as DP — design".
    for case in ("NOM", "GEN", "DAT"):
        head_cat = (
            f"DET[CASE={case}, DEM=false]"
            if case == "NOM"
            else f"ADP[CASE={case}, DEM=false]"
        )
        rules.append(Rule(
            f"NP[CASE={case}]",
            [head_cat, "S_INTERROG_COMP"],
            [
                "(↑ PRED) = 'PRO'",
                f"(↑ CASE) = '{case}'",
                "(↑ FREE_REL) = true",
                "(↑ WH_LEMMA) = ↓2 WH_LEMMA",
                "(↑ MARKER) = ↓1 MARKER",
                "↓2 ∈ (↑ ADJ)",
                "(↓2 COMP_TYPE) =c 'INTERROG'",
                "(↓2 Q_TYPE) =c 'WH'",
            ],
        ))
