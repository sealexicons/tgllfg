# tgllfg/cfg/clitic.py

"""Clitic absorption rules: 2P enclitics, floated quantifiers, kita fusion.

Holds the rules whose structural signature is "matrix S plus a
clitic / quantifier / enclitic that absorbs into it" rather than
the canonical V-initial argument frame. After the post-Phase-5f
grammar split (see ``docs/refactor-grammar-package.md``) this
module owns:

* Phase 4 §7.8 floated quantifier — ``lahat`` / ``pareho`` /
  ``kapwa`` and similar Q-words that float to the right edge of the
  S, sharing reference with the matrix SUBJ via the ``S → S Q``
  recursive rule.
* Phase 4 §7.3 adverbial enclitics as clausal ADJUNCT members —
  the recursive ``S → S PART[CLITIC_CLASS=2P]`` rule that absorbs
  Wackernagel particles (``na``, ``pa``, ``daw``, ``po``, ``kasi``,
  ...) into the matrix's ``ADJUNCT`` set after the clitics module
  has reordered them into the post-verbal cluster.
* Phase 5e Commit 20 kita clitic fusion — ``V kita`` /
  ``V kita NP`` / ``V kita NP[DAT]`` frames that fuse the 1SG.A +
  2SG.P portmanteau pronoun into the verb's argument structure
  with synthetic SUBJ / OBJ / ADJUNCT mappings.

The composer in :mod:`tgllfg.cfg.grammar` calls this registrar
third, after :mod:`tgllfg.cfg.nominal` and
:mod:`tgllfg.cfg.clause`, and before the negation /
extraction / control / discourse registrars — see the plan's
"Migration strategy" §H.
"""

from __future__ import annotations

from ._helpers import _eqs
from .grammar import Rule


def register_rules(rules: list[Rule]) -> None:
    """Append the clitic-area rules in source order."""
    # --- Phase 4 §7.8: floated quantifier ---
    #
    # ``Kumain ang bata lahat`` ("all the children ate", with
    # ``lahat`` floated to clause-final). The quantifier rides
    # into the matrix's ADJ set as a sub-f-structure carrying
    # ``QUANT``; a binding equation links it to SUBJ. Pre-NP
    # partitive usage (``lahat ng bata``) is deferred — that
    # form needs a QP non-terminal.
    rules.append(Rule(
        "S",
        ["S", "Q"],
        ["(↑) = ↓1", "↓2 ∈ (↑ ADJ)", "(↓2 ANTECEDENT) = (↑ SUBJ)"],
    ))


    # --- Phase 5f closing deferral: clause-initial dual Q ---
    #
    # ``Pareho silang kumain.`` "they both ate" — clause-initial
    # form of the floated dual quantifier (cf. ``Kumain sila
    # pareho.`` which already parses via the float rule above).
    # S&O 1972 §4.7 lists this as the canonical surface for
    # ``pareho`` / ``kapwa`` quantification over a NOM-pronoun
    # subject; the float form is an alternant. The Q binds the
    # PRON via ``ANTECEDENT`` exactly as in the float case.
    #
    # Three variants for AV verb arity (intransitive, transitive,
    # ditransitive). Non-AV variants are deferred — the patient-
    # pivot construction (``Pareho silang kinain ng leon`` "they
    # were both eaten by the lion") is rarer and adds voice
    # interaction beyond the canonical AV registers in the seed
    # corpus.
    for link in ("NA", "NG"):
        # AV intransitive: ``Pareho silang kumain.``
        rules.append(Rule(
            "S",
            [
                "Q[DUAL=YES]",
                "PRON[CASE=NOM]",
                f"PART[LINK={link}]",
                "V[VOICE=AV]",
            ],
            [
                "(↑ PRED) = ↓4 PRED",
                "(↑ VOICE) = ↓4 VOICE",
                "(↑ ASPECT) = ↓4 ASPECT",
                "(↑ MOOD) = ↓4 MOOD",
                "(↑ LEX-ASTRUCT) = ↓4 LEX-ASTRUCT",
                "(↑ SUBJ) = ↓2",
                "↓1 ∈ (↑ ADJ)",
                "(↓1 ANTECEDENT) = (↑ SUBJ)",
                "(↓1 DUAL) =c 'YES'",
            ],
        ))
        # AV transitive: ``Pareho silang kumain ng isda.``
        rules.append(Rule(
            "S",
            [
                "Q[DUAL=YES]",
                "PRON[CASE=NOM]",
                f"PART[LINK={link}]",
                "V[VOICE=AV]",
                "NP[CASE=GEN]",
            ],
            [
                "(↑ PRED) = ↓4 PRED",
                "(↑ VOICE) = ↓4 VOICE",
                "(↑ ASPECT) = ↓4 ASPECT",
                "(↑ MOOD) = ↓4 MOOD",
                "(↑ LEX-ASTRUCT) = ↓4 LEX-ASTRUCT",
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ) = ↓5",
                "↓1 ∈ (↑ ADJ)",
                "(↓1 ANTECEDENT) = (↑ SUBJ)",
                "(↓1 DUAL) =c 'YES'",
            ],
        ))
        # AV ditransitive: ``Pareho silang kumain ng isda sa palengke.``
        rules.append(Rule(
            "S",
            [
                "Q[DUAL=YES]",
                "PRON[CASE=NOM]",
                f"PART[LINK={link}]",
                "V[VOICE=AV]",
                "NP[CASE=GEN]",
                "NP[CASE=DAT]",
            ],
            [
                "(↑ PRED) = ↓4 PRED",
                "(↑ VOICE) = ↓4 VOICE",
                "(↑ ASPECT) = ↓4 ASPECT",
                "(↑ MOOD) = ↓4 MOOD",
                "(↑ LEX-ASTRUCT) = ↓4 LEX-ASTRUCT",
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ) = ↓5",
                "↓6 ∈ (↑ ADJUNCT)",
                "↓1 ∈ (↑ ADJ)",
                "(↓1 ANTECEDENT) = (↑ SUBJ)",
                "(↓1 DUAL) =c 'YES'",
            ],
        ))


    # --- Phase 4 §7.3: adverbial enclitics as clausal ADJ members ---
    #
    # The pre-parse clitic-placement pass moves adverbial enclitics
    # (``na``, ``pa``, ``ba``, ``daw``/``raw``, ``din``/``rin``,
    # ``lang``, ``nga``, ``pala``, ``kasi``, ...) to the end of the
    # sentence in priority order. This recursive rule absorbs each
    # one as a member of the matrix f-structure's ADJ set; the
    # particle's own f-structure (carrying ASPECT_PART, EVID, etc.)
    # rides into ADJ as a sub-structure.
    #
    # ``CLITIC_CLASS=2P`` distinguishes Wackernagel enclitics from
    # the other PART tokens (linkers, the ``hindi`` negation
    # particle).
    # The constraining equation enforces strict CLITIC_CLASS=2P
    # matching: the chart's non-conflict matcher would otherwise
    # accept any PART that simply lacks the CLITIC_CLASS feature
    # (e.g. linker ``na``/``-ng``, decimal ``.`` / ``punto``,
    # arithmetic operators) and absorb them into ADJ at clause-
    # final position. The strict ``=c`` ensures only genuine 2P
    # enclitics fire here. (Tightened 2026-05-04 alongside the
    # digit tokenization closing deferral, which exposed the
    # latent looseness via the new ``.`` PART.)
    # Phase 5i Commit 5: yes/no Q_TYPE lift for ``ba``.
    #
    # Two parallel absorption rules with disjoint pre-conditions:
    #
    # * Rule A (the original Phase 4 §7.3): generic 2P clitics
    #   without QUESTION (na ALREADY, pa STILL, daw REPORT, rin ALSO,
    #   lang, nga, pala, kasi, ...). Constraining ``¬ (↓2 QUESTION)``
    #   excludes ``ba``.
    # * Rule B (Phase 5i Commit 5): ``ba`` (PART[QUESTION=true,
    #   Q_TYPE=YES_NO]) — same shape as Rule A plus a literal
    #   ``(↑ Q_TYPE) = 'YES_NO'`` lift onto the matrix S.
    #
    # The two-rule split is cleaner than a single rule with a
    # defining equation ``(↑ Q_TYPE) = ↓2 Q_TYPE``: the equation
    # creates an empty FStructure on the matrix when ↓2 lacks
    # Q_TYPE, perturbing the f-structure rendering for every
    # non-ba 2P-clitic absorption (baseline test failures across
    # ~20 corpus entries).
    #
    # The lifted matrix-level Q_TYPE pairs with Phase 5i Commits 2
    # / 4 wh-fronting (which set ``Q_TYPE: WH``) so downstream
    # consumers have a uniform clausal-Q-type marker (YES_NO /
    # WH / TAG).
    rules.append(Rule(
        "S",
        ["S", "PART[CLITIC_CLASS=2P]"],
        [
            "(↑) = ↓1",
            "↓2 ∈ (↑ ADJ)",
            "(↓2 CLITIC_CLASS) =c '2P'",
            "¬ (↓2 QUESTION)",
            "¬ (↓2 COUNTERFACTUAL)",
            "¬ (↓2 REGISTER)",
        ],
    ))
    rules.append(Rule(
        "S",
        ["S", "PART[CLITIC_CLASS=2P, QUESTION=YES]"],
        [
            "(↑) = ↓1",
            "↓2 ∈ (↑ ADJ)",
            "(↓2 CLITIC_CLASS) =c '2P'",
            "(↓2 QUESTION) =c 'YES'",
            "(↑ Q_TYPE) = 'YES_NO'",
        ],
    ))
    # Phase 5l Commit 5: Rule C — counterfactual ``sana`` lift.
    #
    # Mirrors Rule B (``ba`` Q_TYPE lift) — same shape with a
    # COUNTERFACTUAL=YES daughter precondition and a literal
    # ``(↑ COUNTERFACTUAL) = 'YES'`` lift onto the matrix S. Rule A
    # is updated above with ``¬ (↓2 COUNTERFACTUAL)`` so the two
    # paths are mutually exclusive.
    rules.append(Rule(
        "S",
        ["S", "PART[CLITIC_CLASS=2P, COUNTERFACTUAL=YES]"],
        [
            "(↑) = ↓1",
            "↓2 ∈ (↑ ADJ)",
            "(↓2 CLITIC_CLASS) =c '2P'",
            "(↓2 COUNTERFACTUAL) =c 'YES'",
            "(↑ COUNTERFACTUAL) = 'YES'",
        ],
    ))
    # Phase 5m Commit 2: Rule D — politeness ``po`` / ``ho`` REGISTER lift.
    #
    # Mirrors Rules B / C — daughter precondition is the politeness
    # REGISTER feat (``POLITE`` for ``po``, ``COLLOQUIAL_POLITE`` for
    # ``ho``); matrix lift is the value-copy ``(↑ REGISTER) = (↓2
    # REGISTER)`` so the matrix S exposes the politeness register at
    # the f-structure top level. Rule A is updated above with
    # ``¬ (↓2 REGISTER)`` so the four paths (Rule A generic, Rule B
    # ba, Rule C sana, Rule D po/ho) are mutually exclusive.
    #
    # Limitation: fragment-host position (``Salamat po``, ``Oo po``)
    # does NOT parse — the matrix S non-terminal requires a finite
    # predicate and there is no Phase 4 fragment-answer infrastructure
    # for sub-S hosts. Pinned in
    # ``test_phase5m_politeness_clitic.py::TestFragmentHostDeferred``;
    # closure depends on adding fragment-answer matrix-S rules
    # (Phase 5n debt-clearing or beyond).
    rules.append(Rule(
        "S",
        ["S", "PART[CLITIC_CLASS=2P, REGISTER=POLITE]"],
        [
            "(↑) = ↓1",
            "↓2 ∈ (↑ ADJ)",
            "(↓2 CLITIC_CLASS) =c '2P'",
            "(↓2 REGISTER) =c 'POLITE'",
            "(↑ REGISTER) = 'POLITE'",
        ],
    ))
    rules.append(Rule(
        "S",
        ["S", "PART[CLITIC_CLASS=2P, REGISTER=COLLOQUIAL_POLITE]"],
        [
            "(↑) = ↓1",
            "↓2 ∈ (↑ ADJ)",
            "(↓2 CLITIC_CLASS) =c '2P'",
            "(↓2 REGISTER) =c 'COLLOQUIAL_POLITE'",
            "(↑ REGISTER) = 'COLLOQUIAL_POLITE'",
        ],
    ))


    # --- Phase 5e Commit 20: kita clitic fusion ---
    #
    # Tagalog has a special second-position clitic ``kita`` that
    # fuses the 1sg-GEN actor and 2sg-NOM SUBJ of a non-AV verb
    # into a single token: ``Kinain kita`` "I ate you",
    # ``Sinulatan kita ng liham`` "I wrote you a letter",
    # ``Pinakain kita ng kanin`` "I fed you rice",
    # ``Hindi kita kinain`` "I didn't eat you" (with kita
    # hoisted to the post-V cluster by the Wackernagel pass).
    # The fusion is obligatory — *``Kinain ko ka`` is
    # ungrammatical in modern Tagalog (Schachter & Otanes 1972
    # §3.2; Kroeger 1993 §2.2).
    #
    # Lex: ``data/tgl/pronouns.yaml`` carries a single entry
    # ``kita`` with feats ``{KITA: YES, is_clitic: True}``. The
    # grammar rules here build out the SUBJ and 1sg-actor
    # f-structures from atomic-value equations, since the lex
    # loader doesn't support nested feats.
    #
    # The dual binding sets:
    #
    # * ``(↑ SUBJ PERS) = '2'``, ``(↑ SUBJ NUM) = 'SG'``,
    #   ``(↑ SUBJ CASE) = 'NOM'`` — the 2sg-NOM SUBJ (CAUSEE
    #   in pa- variants; PATIENT / RECIPIENT / THEME in plain
    #   variants).
    # * ``(↑ <obj_target> PERS) = '1'``, ``(↑ <obj_target> NUM)
    #   = 'SG'``, ``(↑ <obj_target> CASE) = 'GEN'`` — the
    #   1sg-GEN actor. The typed slot follows the same
    #   per-voice spec used by the standard non-AV S frames:
    #   OBJ-AGENT for plain non-AV; OBJ-CAUSER for pa-OV /
    #   pa-DV (CAUS=DIRECT).
    #
    # Three frame variants per voice spec:
    #
    # 1. **Bare** (``V kita``): the simplest case, e.g.
    #    ``Kinain kita`` (OV), ``Binasahan kita`` (DV),
    #    ``Ipinaggawa kita`` (IV-BEN), ``Pinakain kita``
    #    (pa-OV: "I fed you").
    # 2. **With overt PATIENT** (``V kita NP[GEN]``): used by
    #    3-arg DV / IV / pa-OV constructions, e.g.
    #    ``Sinulatan kita ng liham`` "I wrote you a letter",
    #    ``Pinakain kita ng kanin`` "I fed you rice".
    # 3. **With DAT adjunct** (``V kita NP[DAT]``): a peripheral
    #    location / recipient adjunct.
    #
    # Note on paradigm coverage: the canonical example
    # ``Nakita kita`` "I saw you" requires an OV-NVOL form of
    # ``kita`` (na- prefix on the transitive root). The current
    # ma-class paradigm only emits AV-NVOL forms; ``nakita``
    # analyses as AV-NVOL only, so the kita-fusion rule doesn't
    # fire for it. Tracked as a paradigm-coverage TBD alongside
    # the DV PFV gap from Phase 5e Commit 18 (see plan §18).
    kita_voice_specs = [
        # (voice, obj_target, extras) — mirrors the standard
        # voice_specs above so the typed actor-slot per voice
        # matches the lexicon's expected PRED.
        ("OV", "OBJ-AGENT", [("CAUS", "NONE")]),
        ("OV", "OBJ-CAUSER", [("CAUS", "DIRECT")]),
        ("DV", "OBJ-AGENT", [("CAUS", "NONE")]),
        ("DV", "OBJ-CAUSER", [("CAUS", "DIRECT")]),
        ("IV", "OBJ-AGENT", []),
    ]
    kita_subj_eqs = [
        "(↑ SUBJ PERS) = '2'",
        "(↑ SUBJ NUM) = 'SG'",
        "(↑ SUBJ CASE) = 'NOM'",
    ]
    for voice, obj_target, extras in kita_voice_specs:
        feat_strs = [f"VOICE={voice}"] + [f"{k}={v}" for k, v in extras]
        v_cat = f"V[{', '.join(feat_strs)}]"
        actor_eqs = [
            f"(↑ {obj_target} PERS) = '1'",
            f"(↑ {obj_target} NUM) = 'SG'",
            f"(↑ {obj_target} CASE) = 'GEN'",
        ]
        # Bare frame: V kita (no further args). Covers 2-arg
        # constructions and intransitive-feeling causatives.
        #
        # Phase 5n.A Commit 29 added the explicit ``(↓2 KITA) =c
        # 'YES'`` constraining equation to close a non-conflict-
        # matcher leak (per ``project_parser_nonconflict_matcher``):
        # the daughter pattern ``PRON[KITA=YES]`` was admitting any
        # PRON via shared-key absence, since the equations don't
        # bind ↓2's f-structure to anything (the rule literally
        # synthesises SUBJ.PERS=2 and OBJ-AGENT.PERS=1, never
        # touching the PRON's features). Without the =c, the rule
        # fired on ``Tinanong niya.`` etc., producing a bogus S
        # over the V + PRON span — and the Phase 5l COND-adjunct
        # path subsequently misanalyzed ``Tinanong niya kung sino
        # ang kumain.`` as ``[Tinanong niya] [kung-S]``.
        rules.append(Rule(
            "S",
            [v_cat, "PRON[KITA=YES]"],
            _eqs(*kita_subj_eqs, *actor_eqs, "(↓2 KITA) =c 'YES'"),
        ))
        # With-PATIENT frame: V kita NP[GEN]. Covers 3-arg
        # ditransitives and 3-arg pa-causatives (where the GEN-NP
        # is the OBJ-PATIENT — the third role beyond actor and
        # SUBJ).
        rules.append(Rule(
            "S",
            [v_cat, "PRON[KITA=YES]", "NP[CASE=GEN]"],
            _eqs(
                *kita_subj_eqs,
                *actor_eqs,
                "(↑ OBJ-PATIENT) = ↓3",
                "(↓2 KITA) =c 'YES'",
            ),
        ))
        # With-DAT frame: V kita NP[DAT]. The DAT-NP rides into
        # ADJUNCT.
        rules.append(Rule(
            "S",
            [v_cat, "PRON[KITA=YES]", "NP[CASE=DAT]"],
            _eqs(
                *kita_subj_eqs,
                *actor_eqs,
                "↓3 ∈ (↑ ADJUNCT)",
                "(↓2 KITA) =c 'YES'",
            ),
        ))
