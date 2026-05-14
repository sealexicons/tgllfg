# Definitions

<!-- markdownlint-disable-file MD013 -->
<!-- This file is dominated by reference tables whose Notes column
     exceeds the 120-char line-length limit. Markdown table rows
     must be on a single line, so MD013 is disabled file-wide. -->

Two reference tables for the tgllfg codebase: abbreviations used in
code, comments, tests, and other docs; and the source texts behind
each algorithm or analytical decision the engine implements.

## 1. Acronyms and abbreviations

Grouped by category for readability; alphabetical within each
group.

### LFG framework

| Abbrev | Expansion | Notes |
| ---------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| ADJ | Adjunct | Set-valued, non-governable f-structure attribute. Synonym of ADJUNCT in the code. |
| ADJUNCT | Adjunct | Long form used in equations (`↓ ∈ (↑ ADJUNCT)`). |
| ANTECEDENT | Quantifier antecedent | Phase 4 §7.8 — binding feature on a floated quantifier; `(↓ ANTECEDENT) = (↑ SUBJ)` links *lahat* to the SUBJ. Also used for Phase 6.F reflexive `sarili` binding (`(↑ SUBJ ANTECEDENT) = (↑ obj_target)` per Kroeger 1993 §2.3 actor-binder). |
| AltFeature | Alternation in regex-path | Phase 6.B equation AST — `{F \| G}` element of a regex path. Used with `StarFeature` / `PlusFeature` for FU body / bottom partition. |
| atomic unify | Snapshot/rollback unification | Phase 6.A — `FGraph.unify` records mutations into an undo journal; on failure rewinds to pre-call state. Prerequisite for FU evaluation (enumerating multiple endpoints requires per-attempt rollback). |
| binding equation | Reentrancy-introducing equation | Phase 6.B C5 — an equation whose RHS is a regex path on an existing f-graph and whose LHS is a fresh designator; the unifier resolves the RHS endpoint then `graph.unify(lhs, endpoint)`. Used for Phase 6.D LDD relativization, Phase 6.F `sarili` binding. |
| ConstrainingEquation | `=c` equation kind | Equation `(path) =c value` — succeeds only if `path` is already defined and unifies with `value`. AST node in `fstruct/equations.py`; evaluated in pass 2 after defining equations have run. K&Z 1989 idiom for agreement / selectional gating. |
| DefiningEquation | `=` equation kind | Equation `(path) = value` — sets `path` to `value` (creating-if-absent semantics; unifies if already present). AST node in `fstruct/equations.py`; evaluated in pass 1. |
| NegEquation | `≠` equation kind | Equation `(path) ≠ value` — strict-undefined-fails semantics (requires `path` defined AND not equal to `value`). AST node in `fstruct/equations.py`. Phase 6.H exploration documents the strict-failure behavior; for "undefined OR ≠ value" semantics use `NegExistentialConstraint` in a separate rule variant. |
| NegExistentialConstraint | `¬` existential | Equation `¬ (path)` — succeeds iff `path` is undefined. AST node in `fstruct/equations.py`. Used heavily in Phase 6.H L33 (three-variant float rule split) and across cfg/ rules where "feat absent" is the discriminator. |
| SetMembership | `∈` equation kind | Equation `(designator) ∈ (path)` — adds the LHS designator to the set-valued attribute named by the RHS path. AST node in `fstruct/equations.py`; used for ADJ / ADJUNCT / CONJUNCTS membership (Bresnan 2001 ch. 4). |
| S_GAP | Subject-gap RC body | Non-terminal for Phase 4 §7.5 SUBJ-only relative clause body — depth-1 RC where the gap is the embedded SUBJ. Consumed by the matrix RC wrap rule with `(↑ REL-PRO) =c (↓3 SUBJ)`. |
| S_XCOMP | XCOMP-bodied RC body | Non-terminal for Phase 6.D long-distance RC body — RC whose embedded clause has a control chain (XCOMP path) to the gap site. Consumed by the LDD RC wrap rule with FU binding `(↓3 REL-PRO) =c (↓3 XCOMP* SUBJ)`. |
| S_INTERROG_COMP | Indirect-Q complement | Non-terminal for Phase 5i / 5n.B `kung`-headed wh / yes-no indirect-question complement. Phase 6.E reuses it as the daughter of NP wrap rules to produce free relatives. |
| NP_LONG_LIST_NOM | Left-recursive coord NP | Non-terminal for Phase 5n.A 4+-conjunct flat NOM coordination. Combined with the 4+-wrap rule produces flat `CONJUNCTS` sets of arbitrary arity; Phase 6.C strict matcher unblocks 5+-conjunct; Phase 6.H stress-tests through 10 conjuncts. |
| AVM | Attribute-Value Matrix | The shape of an f-structure. |
| a-structure | Argument structure | The thematic-role list a verb projects (e.g. `[AGENT, PATIENT]`). |
| CFG | Context-Free Grammar | The c-structure layer of LFG; productions live in seven per-area modules under `src/tgllfg/cfg/` (`nominal`, `clause`, `clitic`, `negation`, `extraction`, `control`, `discourse`); `cfg/grammar.py` composes them. |
| COMP | Clausal complement | Closed sentential argument; governable. |
| c-structure | Constituent structure | Phrase-structure tree produced by the parser. |
| f-structure | Functional structure | AVM produced by unification; carries grammatical functions. |
| FOCUS | Focus | Discourse function; non-governable in the LFG sense. |
| FREE_REL | Free-relative marker | Phase 6.E — binary feat (in `BINARY_FEATS`) set by the free-relative NP wrap rules when a `kung`-headed wh-clause functions as an NP argument. §18.1.2 L93. |
| FU | Functional Uncertainty | Kaplan & Zaenen 1989 §3 — regex-path designators on f-structures (`↑ COMP* OBJ`, `↑ XCOMP* SUBJ`). The unifier evaluates these against the live f-graph via finite-state traversal (Kaplan & Maxwell 1988). Phase 6.B implementation. |
| GF | Grammatical Function | SUBJ, OBJ, OBL-θ, ADJ, etc. (Distinct from "Goal Focus" in S&O — disambiguated by context.) |
| graph-constraint matcher | Strict category matcher | Phase 6.C — `cfg/compile.py:matches` requires `expected.keys() ⊆ candidate.keys()` plus value compat on shared keys. Replaces the pre-6.C "non-conflict" matcher which silently admitted shared-key-absence matches. K&Z 1989 §3 c-structure faithfulness. |
| [±r, ±o] | Bresnan–Kanerva intrinsic features | The feature pair that drives LMT mapping. `r` = restricted (cannot be SUBJ); `o` = objective (object-like). Truth table in `docs/lmt.md`. |
| LEX-ASTRUCT | Lexical a-structure | F-structure attribute carrying the verb's role list, used by LMT. |
| LFG | Lexical-Functional Grammar | The formalism the parser implements. |
| LINK | Linker | Phase 4 §7.5 — `na` / `-ng` allomorphs that join a head NP to its relative clause or modifier. |
| LMT | Lexical Mapping Theory | Maps thematic roles to GFs via [±r, ±o] features. Implemented in Phase 5 §8 — see `docs/lmt.md`. |
| N_RC | N-level RC tag | Phase 6.G — binary feat (in `BINARY_FEATS`) set by the Phase 5n.A N-level relative clause rule. Distinguishes N-level RCs (which feed the bare-N existential `May` construction) from NP-level RCs to prevent simple NP-rule double-firing under SHARE+SHARE. §18.1.2 L32. |
| off-path constraint | Local FU constraint | Phase 6.B C4 — `(↑ XCOMP*<(→ TENSE) =c 'PAST'> SUBJ)` restricts FU traversal to intermediate nodes satisfying the bracketed predicate. Per K&Z 1989, the constraint fires at each intermediate node. |
| OBJ | Object | Governable GF; second core argument in transitives. |
| OBJ-θ | Typed object | OBJ-GOAL, OBJ-RECIPIENT, etc. Generic prefix `OBJ-` is recognised as governable. |
| OBL | Oblique | Governable GF prefix; OBL-LOC, OBL-GOAL, OBL-BEN. |
| OBL-AG | Oblique agent | Demoted-agent analysis used in older "passive" treatments of non-AV. Rejected; see §1 of this doc. |
| OBL-BEN | Benefactive oblique | Typed OBL-θ; assigned by the LMT engine when a sa-NP role's intrinsics are `[+r, -o]` and the role is `BENEFICIARY`. |
| OBL-GOAL | Goal oblique | Typed OBL-θ; LMT engine assigns it for `GOAL` roles with `[+r, -o]` intrinsics. |
| OBL-INSTR | Instrumental oblique | Typed OBL-θ; LMT engine assigns it for `INSTRUMENT` roles. No current Phase 4 BASE entry emits one. |
| OBL-LOC | Locative oblique | Typed OBL-θ; LMT engine assigns it for `LOCATION` roles. Used by motion verbs (e.g. `lakad`). |
| OBL-RECIP | Recipient oblique | Typed OBL-θ; LMT engine assigns it for `RECIPIENT` roles in non-DV voices. |
| OBL-θ | Typed oblique | Generic prefix `OBL-` is recognised as governable; specific suffixes follow `Role.gf_suffix` (LOC, BEN, INSTR, RECIP, GOAL, …). |
| PlusFeature | One-or-more in regex-path | Phase 6.B equation AST — `F+` element of a regex path. Mirrors `StarFeature` but excludes the zero-traversal case. |
| PRED | Predicate | F-structure attribute holding the predicate template (e.g. `EAT <SUBJ, OBJ>`). |
| Q | Quantifier | POS for floated quantifiers (`lahat`, `iba`); Phase 4 §7.8. |
| QUANT | Quantifier feature | F-structure attribute on a floated quantifier (e.g. *lahat*); Phase 4 §7.8. |
| REL-PRO | Relative pronoun | Constraining-equation target for SUBJ-only relativization (Phase 4 §7.5). Extended in Phase 6.D to use FU body `XCOMP*` for cross-clausal LDD: `(↓3 REL-PRO) =c (↓3 XCOMP* SUBJ)`. §18.1.2 L47. |
| StarFeature | Zero-or-more in regex-path | Phase 6.B equation AST — `F*` element of a regex path. The unifier's FSA traversal enumerates well-formed paths matching the regex, K&Z 1989 §3 minimality clause picks the shortest endpoint. |
| SUBJ | Subject | Governable GF; corresponds to the *ang*-NP pivot in Tagalog. |
| TOPIC | Topic | Non-governable discourse function; targeted by *ay*-inversion (Phase 4 §7.4). |
| XCOMP | Open complement | Sentential complement with shared SUBJ (control verbs). |
| XCOMP\* | XCOMP body (FU) | Phase 6.D — the zero-or-more `XCOMP` traversal in the LDD relativization binding `(↓3 REL-PRO) =c (↓3 XCOMP* SUBJ)`. Per K&Z 1989 §3 eq. 39 (English topicalization). Calibrated to `XCOMP*` (not `{COMP, XCOMP}*`) for Tagalog where COMP carries its own SUBJ pivot, not control-shared. |

### Tagalog voice / focus inventory

| Abbrev | Expansion | Tradition | Notes |
| -------- | ---------------------------- | -------------------- | -------------------------------------------------------------------------------- |
| AF | Actor Focus | Schachter & Otanes | Maps to AV in Kroeger's reduction. |
| AV | Actor Voice | Kroeger 1993 | Pivot is the actor; `-um-` / `mag-` / `mang-` / `maka-` / `ma-` AV affix classes. |
| BF | Benefactive Focus | Schachter & Otanes | Maps to IV with APPL=BEN. |
| CF | Causative Focus | Schachter & Otanes | Maps to AV with CAUS=DIRECT for the bare `pa-` form; biclausal otherwise. |
| DF | Directional Focus | Schachter & Otanes | Maps to DV. |
| DV | Dative Voice | Kroeger 1993 | Pivot is the locative / source / recipient; `-an` suffix. |
| GF | Goal Focus | Schachter & Otanes | Maps to OV. (Disambiguated from "Grammatical Function" by context.) |
| IF | Instrumental Focus | Schachter & Otanes | Maps to IV with APPL=INSTR. |
| IV | Instrumental Voice | Kroeger 1993 | Pivot is the conveyed / instrument / benefactive; `i-` prefix. |
| LF | Locative Focus | Schachter & Otanes | Maps to DV. |
| OV | Objective Voice | Kroeger 1993 | Pivot is the patient / theme; `-in` suffix or realis `-in-` infix. |
| PF | Patient Focus | Older terminology | Synonym of GF; maps to OV. |
| PV | Patient Voice | Older terminology | Synonym of OV. The codebase migrated to OV in Phase 2. |
| RF | Reason Focus | Schachter & Otanes | Maps to IV with APPL=REASON. |

### Aspect / mood / polarity

| Abbrev | Expansion | Notes |
| ---------- | ---------------------------- | ---------------------------------------------------------------------------------------------------- |
| ABIL | Abilitative mood | `maka-` class (e.g. `nakakain` "was able to eat"). |
| ASPECT | Aspect feature | F-structure attribute taking PFV / IPFV / CTPL / RECPFV. |
| ASPECT_TYPE | Enum sub-aspect | Phase 7a.C: `JUST_FINISHED` lifted to matrix by `katatapos + V` raising-from-XCOMP (`Katatapos kainin ang isda.` "The fish had just been eaten"). Distinguishes the analytic "just-finished" matrix from a synthetic ASPECT=RECPFV form. |
| CTPL | Contemplative aspect | "Future" / irrealis. CV-redup without realis `-in-`. |
| IMP | Imperative mood | Phase 4 §7.2. |
| IND | Indicative mood | The default mood feature value. |
| IPFV | Imperfective aspect | "Progressive". CV-redup + realis `-in-` infix. |
| IRREALIS | Irrealis | Aspectual feature opposing REALIS; CTPL is irrealis. |
| MOOD | Mood feature | F-structure attribute taking IND / IMP / ABIL / NVOL / SOC. |
| NEG | Negation | F-structure attribute set by `hindi` / `huwag` (Phase 4 §7.2). |
| NVOL | Non-volitional mood | `ma-` non-volitional class (e.g. `natulog` "happened to fall asleep"). |
| PFV | Perfective aspect | "Past / completed". Realis `-in-` without CV-redup. |
| POL | Polarity | NEG vs. affirmative. |
| REALIS | Realis | Aspectual feature opposing IRREALIS; PFV/IPFV are realis. |
| RECPFV | Recent perfective | "Just-completed" aspect (`katatapos`-style); Phase 4 §7.2. |
| SOC | Social mood | "Common" or social-deontic mood; Phase 4 §7.2. |
| STAT | Stative | Subset of NVOL / `ma-` semantics (e.g. *natulog*). |
| TR | Transitivity | Lemma feature taking TR (transitive) / INTR (intransitive); from `verbs.yaml`. |
| INTR | Intransitive | Value of TR. |

### Case / nominal features

| Abbrev | Expansion | Notes |
| ---------- | ---------------------------- | ---------------------------------------------------------------------------------------------------- |
| 2P | Second-position (clitic) | Clitic class for Wackernagel placement. (Phase 4 §7.3.) |
| CASE | Case feature | F-structure attribute taking NOM / GEN / DAT. |
| CLUSV | Clusivity | INCL / EXCL on first-person plural pronouns. |
| DAT | Dative case | *sa*-marker (`sa`, `kay`). |
| DEIXIS | Deixis | PROX / MED / DIST on demonstratives. |
| DEM | Demonstrative flag | `YES` / `NO` (Phase 4 §7.8) — gates the standalone-NP rule for demonstratives like *ito* / *iyan*. |
| DET | Determiner | POS for *ang* / *ng* (when functioning as common-noun marker), demonstratives. |
| DIST | Distal | *iyon* / *yon*. |
| EXCL | Exclusive (clusivity) | `kami` (1pl-excl). |
| GEN | Genitive case | *ng* / *ni* marker. |
| HUMAN | Human feature | Triggers personal-name case markers (*si*/*ni*/*kay*) over common-noun markers. |
| INCL | Inclusive (clusivity) | `tayo` (1pl-incl). |
| MED | Medial | *iyan* / *yan*. |
| NOM | Nominative case | *ang* / *si* marker. SUBJ in the four-voice mapping. |
| NUM | Number | SG / PL. |
| PERS | Person | 1 / 2 / 3. |
| PL | Plural | |
| POSS | Possessor | F-structure attribute holding the possessor NP (Phase 4 §7.8 NP-internal possessive `bata ng nanay`). |
| PROX | Proximal | *ito* / *ire*. |
| SG | Singular | |

### Theta roles (a-structure)

| Abbrev | Expansion | Used in |
| ------------- | -------------------------- | ----------------------------------------------------------------------------------------------- |
| ACTOR | Actor | AV intransitive (e.g. *kumain ang aso*). Generic role name when AGENT/PATIENT distinction isn't needed. |
| AGENT | Agent | The volitional doer in transitive predicates. |
| BEN | Beneficiary | Pivot in `ipag-` IV-BEN applicative (e.g. *ipinaggawa*); typed `OBL-BEN` otherwise. |
| CAUSEE | Causee | The forced participant in `pa-` direct (monoclausal) causatives; pivot in *pinakain ang bata*. Surfaces as embedded SUBJ in `magpa-` indirect causatives. |
| CAUSER | Causer | The instigator in causatives. SUBJ in `magpa-` indirect (matrix); `OBJ-CAUSER` (typed OBJ-θ) in `pa-` direct. |
| COMPLEMENT | Open-complement target | The XCOMP-bound argument of control verbs (gusto, payag, pilit, utos). Off the [±r, ±o] truth table. |
| CONVEYED | Conveyed | The object conveyed in IV (e.g. *liham* in *isinulat ang liham*). |
| EVENT | Caused event | XCOMP-bound argument of `magpa-` indirect causatives. Off the [±r, ±o] truth table. |
| EXPERIENCER | Experiencer | Mental subject of psych control verbs (gusto, ayaw, kaya). GEN-marked but maps to SUBJ — see `docs/lmt.md`. |
| GOAL | Goal | The endpoint / recipient in DV. Used by the synthesizer fallback for DV; Phase 4 BASE entries use RECIPIENT instead. |
| INSTR | Instrument | The instrument argument; typed `OBL-INSTR`. No current Phase 4 BASE entry emits one. |
| LOC | Location | The location argument; typed `OBL-LOC` for motion verbs (e.g. `lakad`). |
| PATIENT | Patient | The undergoer in transitive predicates; pivot in OV. |
| REASON | Reason / cause | Phase 5 LMT — would be typed `OBL-REASON`. No current Phase 4 BASE entry emits one (pending `ika-` reason applicative). |
| RECIPIENT | Recipient | DV pivot for verbs like *sulat* (e.g. *sinulatan ang ina*). Alternate label for GOAL. |
| STIMULUS | Stimulus | Plan §8.1 role for the cause of a mental state. No current Phase 4 BASE entry emits one. |
| THEME | Theme | Generic patient-like role used for semantic underspecification. |

### Argument-structure secondary features

| Abbrev | Expansion | Values | Notes |
| ---------- | ------------------------------------ | ---------------------------------------------- | -------------------------------------------------- |
| APPL | Applicative | `INSTR`, `BEN`, `REASON`, `CONVEY`, `∅` | Subset of voice that an applicative selects. |
| ASK_CLASS | Verbal-ask class | `ASK`, `∅` | Phase 5n ASK-class predicates (`tanong`); take indirect-Q complements. |
| CAUS | Causative | `DIRECT`, `INDIRECT`, `∅` | `pa-` direct vs biclausal indirect. |
| CTRL_CLASS | Control class | `PSYCH`, `INTRANS`, `TRANS`, `NONE`, `MODAL`, `KNOW` | Phase 4 §7.6 — discriminates control-verb subtypes for the SUBJ-binding equation. Phase 5i adds `KNOW` for indirect-Q embedders. |
| SAY_CLASS | Verbal-say class | `SAY`, `∅` | Reporter-class predicates (`sabi`); Phase 5n reported-Q work. |

### Quantifier / modifier / discourse feats (Phase 5–6)

F-structure attributes added across Phases 5 and 6 for quantifier
semantics, modifier projection, and discourse / register tracking.
Most are binary (`true` / absent) — see `core/feats.py:BINARY_FEATS`
for the canonical list (52 entries as of Phase 6.G).

| Abbrev | Type | Notes |
| -------------- | ---------------- | ---------------------------------------------------------------------------------------------------- |
| ADV_TYPE | Enum | `FREQUENCY`, `MANNER`, `TIME`, etc. Classifies adverb subtype for grammar rule dispatch. |
| APPROX | Binary | Approximator-wrap marker; lifts from inner NUM to NP via Phase 6.G cardinal-NP rule. |
| CARDINAL | Binary | Marks cardinal-numeral surfaces (vs. ordinal). |
| CARDINAL_VALUE | Numeric-string | The cardinal's numeric payload (e.g. `'2'` for `dalawa`). Lifts to matrix NP via Phase 5f cardinal-NP rule. |
| COMP_DEGREE | Enum | `COMPARATIVE`, `SUPERLATIVE`, `EQUATIVE`, `INTENSIFIER`, `CONTRASTIVE`. Phase 5h comparison morphology. |
| COMP_TYPE | Enum | `INTERROG`, `YES_NO_INTERROG`, `DECL`. Phase 5i / 5n.B sentential-complement type. |
| COUNTERFACTUAL | Binary | Phase 5l `sana` counterfactual lift. |
| DEPICTIVE | Binary | Phase 5n.A depictive-secondary-predicate marker. |
| DISTRIB | Binary | Distributive marker (e.g. `tig-isa` "one each"); lifts via Phase 5n.C.3 / Phase 6.G. |
| DISCOURSE_EMPH | Binary | Phase 5m discourse emphasis (e.g. `nga`). |
| DUAL | Binary | Dual-Q marker on `pareho` / `kapwa`; gates Phase 6.H L33 number agreement. |
| EQUATIVE | Binary | Phase 5h equative-identity ADJ marker (`pareho` ADJ polysemy partner to Q[DUAL]). |
| FRAGMENT_HOST | Binary | Phase 5m fragment-answer host eligibility. |
| FREE_REL | Binary | Phase 6.E free-relative DP marker (kung-S as NP argument). |
| FREQ_VALUE | Enum | `HIGH`, `HABITUAL`, `SOMETIMES`, `OCCASIONAL`. Phase 5m / 6.I frequency-adverb value. |
| KITA | Binary | Phase 5e Commit 20 fused 1SG.GEN+2SG.NOM portmanteau clitic; gates the kita-fusion rule family. |
| MAGISA | Binary | Phase 5n.A `mag-isa` "alone" manner-adverb marker. |
| MEASURE | Binary | Measure-NP marker (e.g. `kilo`); reserved feat, no current corpus surfaces. |
| MIRATIVE | Binary | Phase 5m mirative discourse marker. |
| MODAL | Binary | Phase 5j modal-Q marker (e.g. `puwede` / `maaari`). |
| N_RC | Binary | Phase 6.G tag-feat on N-level RC output; blocks N→NP RC double-firing under SHARE+SHARE. |
| ORDINAL | Binary | Marks ordinal numerals (`ika-` series). |
| ORDINAL_VALUE | Numeric-string | The ordinal's numeric payload (e.g. `'1'` for `una`). Lifts via Phase 5f ordinal-NP rule. |
| PANG_DERIVED | Binary | Phase 5c `pang-` purpose-nominal marker. |
| PLURAL_MARKER | Binary | Phase 5f `mga` PART marker; gates time-NP / cardinal-NP approximation rules. |
| PREDICATIVE | Binary | Phase 5g / 5n.B predicative ADJ / Q clause marker (e.g. `Marami ang aklat`). |
| Q_LEMMA | String | Phase 5n.B predicative-Q lemma lifted from the Q daughter (parallel to ADJ_LEMMA). |
| Q_TYPE | Enum | `WH`, `YES_NO`, `TAG`. Phase 5i clausal-question-type marker. |
| QUESTION | Binary | Phase 5i question-marker on `ba`; lifts to matrix `Q_TYPE=YES_NO`. |
| RECP | Binary | Reciprocal-construction marker. |
| REGISTER | Enum | `POLITE`, `COLLOQUIAL_POLITE`, `LITERARY` (Phase 5m politeness register), `COLLOQUIAL` (Phase 7a.E §3.6 no-linker modal + Phase 7a.F kahit-X no-ay — colloquial-register matrix marker that downstream consumers can filter on). |
| RESULTATIVE | Binary | Phase 5n.A `naka-` resultative stative-locative marker. |
| SEM_CLASS | Enum | `REFLEXIVE` (`sarili`), `SEASON` (`tag-`-prefixed), `TIME` (clock), etc. Lifts to NP via Phase 6.G SHARE+SHARE. |
| UNIV | Binary | Phase 5m universal-quantifier marker (`kahit-X` family). |
| VAGUE | Binary | Phase 5h vague-Q marker (`marami` / `konti` / `kakaunti`); gates predicative-Q clause rule. |
| WH | Binary | wh-Q / wh-PRON marker. Phase 5i. |
| WHOLE | Binary | Phase 5l `buong` / `lahat ng N` whole-NP marker; lifts via dedicated whole-NP rule. |
| WH_LEMMA | String | Phase 6.E free-relative head wh-lemma lifted from the kung-S daughter. |

### Affix-class labels (`verbs.yaml` `affix_class:`)

| Label | Expansion |
| ------------ | -------------------------------------------------------------------------------------------- |
| an_oblig | -an obligatory: takes the `-an` DV suffix. |
| in_oblig | -in obligatory: takes the `-in` OV suffix and the realis `-in-` infix. |
| i_oblig | i- obligatory: takes the `i-` IV prefix. |
| ma | ma- non-volitional / stative AV class (MOOD=NVOL). |
| mag | mag- AV class (e.g. *naglinis*). |
| maka | maka- abilitative AV class (MOOD=ABIL). |
| mang | mang- distributive AV class with nasal substitution. |
| magsi | Phase 7a.B — plural-actor AV pluralizer (S&O 1972 §5.15). 3 aspect cells (`nagsi-V`, `nagsisi-V`, `magsisi-V`); fires on `-um-` verbs. Emits `DISTRIB=true`. |
| magpa_an | Phase 7a.B — reciprocal-distributive causative AV circumfix. 3 aspect cells (`nagpa-V-an`, `nagpapa-V-an`, `magpapa-V-an`). Emits `{MOOD: SOC, RECP: true, DISTRIB: true}`. Locative-distributive subtype dropped per GT-empirical evidence; reciprocal-distributive reading only. |
| um | -um- AV class (e.g. *kumain*). |

### Non-verbal paradigm-cell labels (`paradigms.yaml` `affix_class:`)

Phase 5n.C.3 introduced `base_pos` on `ParadigmCell` so paradigm
cells fire on non-VERB roots (NOUN / ADJ / NUM / PRON). Phase 6.I
extends the same machinery to PART (via `Particle.affix_class`).

| Label | Base | Notes |
| -------------------- | ------ | ---------------------------------------------------------------------------------------------- |
| adv_redup | ADV | Phase 6.I (§18.1.2 L105) — productive `pa-X-X` ADV-FREQUENCY reduplication. `[prefix pa, redup_root]`; LEMMA computed as pre-redup base + `-` + root citation. |
| card_redup | NOUN | Phase 5n.C.3 — cardinal-NUM reduplication for `libulibo` (`libo` "1000" → "thousands"). |
| kani_redup | PRON | Phase 5n.C.3 Commit 5 — distributive-possessive 3rd-DAT pronoun → Q (`kanya` → `kanyakanya`). |
| kasing_redup_adj | ADJ | Phase 5n.C.3 Commit 8 (§18 L38) — CV-redup equative variant (`kasinggaganda`). |
| redup_intens_adj | ADJ | Phase 5n.C.3 Commit 7 (§18 L37) — reduplicated intensive ADJ (`magandaganda` "rather beautiful"). |
| redup_wh_plural | PRON | Phase 5n.C.3 Commit 9 (§18 L49) — wh-PRON plural redup (`anoano` / `sinosino`). |
| tag_season | NOUN | Phase 5f Commit 14 — season N from a root (`init` → `tag-init` with `SEM_CLASS=SEASON`). |
| tig_distrib | NUM | Phase 5n.C.3 Commit 4 — distributive `tig-` cardinal (`tigisa` "one each"). |

### Paradigm operation kinds (`paradigms.yaml` `op:`)

| Op | Effect |
| ------------------ | --------------------------------------------------------------------------------------------------- |
| `cv_redup` | First-CV reduplication (Phase 2C / 4). E.g., `ganda` → `gaganda`. |
| `full_redup` | Whole-base reduplication with `o`→`u` raising on the first copy (Phase 5n.C.3 Commit 2). |
| `kani_redup` | 3rd-DAT pronoun reduplication: 2-syl full redup; 3-syl truncates first copy to 2 syllables. |
| `redup_root` | Append the original `root.citation` to the current base (post-prefix). Phase 5n.C.3 Commit 6. |
| `infix` | Insert affix after the first consonant (e.g., `-um-`, `-in-`). |
| `prefix` | Prepend a string (e.g., `ma-`, `pa-`, `pinaka-`). |
| `suffix` | Append a string with optional high-vowel deletion (e.g., `-an`, `-in`). |
| `nasal_substitute` | Replace stem-initial obstruent with homorganic nasal (`mang-` distributive). |
| `nasal_assim_prefix` | Prepend a nasal prefix with homorganic assimilation (`mang-` / `pang-` / `nang-`). |

### Per-root sandhi flags (`verbs.yaml` `sandhi_flags:`)

| Flag | Effect |
| ----------------------- | ------------------------------------------------------------------------------------------------------- |
| d_to_r | Apply intervocalic /d/ → /r/ post-processor (e.g. *dadating* → *darating*). |
| high_vowel_deletion | Delete a stem-final /i/ or /u/ before a vowel-initial suffix (e.g. *bili* + *-in* → *bilhin*). |

### Engineering / project

| Abbrev | Expansion | Notes |
| ---------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| API | Application Programming Interface | |
| AST | Abstract Syntax Tree | Used in equation-language documentation. |
| AVM | Attribute-Value Matrix | (Listed under LFG too.) |
| CI | Continuous Integration | GitHub Actions runs the test suite on PR. |
| CLI | Command-Line Interface | The `tgllfg` entry point shipped with the package. |
| CSV | Comma-Separated Values | Used by `tgllfg lex import`. |
| DB | Database | The Postgres-backed lexicon (Phase 3). |
| EBNF | Extended Backus–Naur Form | The equation-language grammar is documented in EBNF. |
| FK | Foreign Key | |
| FST | Finite-State Transducer | Considered for Phase 2 morphology; rejected for the rule cascade due to macOS install friction. |
| GIN | Generalized Inverted Index | PostgreSQL index type used for trigram and FTS columns. |
| HTTP | Hypertext Transfer Protocol | |
| IPA | International Phonetic Alphabet | |
| ISO | International Organization for Standardization | Used in `language.iso_code`. |
| JSON | JavaScript Object Notation | |
| JSONB | JSON binary | PostgreSQL JSON column type used for AVMs and lists. |
| MORPH | Morphology | The rule-cascade morphological analyzer / generator (Phase 2 / 2C). |
| MR | Merge Request | Synonym for PR in some shops; user uses both. |
| OCR | Optical Character Recognition | Used to ingest dictionary scans during Phase 2C scale-up. |
| OOV | Out-Of-Vocabulary | A surface form the morph analyzer can't analyze — falls through to `pos='_UNK'`. The Phase 8 coverage audit (`docs/coverage-audit-2026-05.md`) reports OOV inventories per source as a lex-gap signal. Probed by `oov_probe` in `scripts/harvest_exemplars.py`; Phase 8.Q corrected the probe to apply `split_linker_ng` before reporting, removing false positives on clitic-glued surfaces (`akong` = `ako` + `-ng`, etc.). |
| ORM | Object-Relational Mapper | SQLAlchemy 2.x. |
| OS | Operating System | |
| PDF | Portable Document Format | |
| PK | Primary Key | |
| POS | Part of Speech | VERB / NOUN / ADJ / DET / ADP / PART / PRON / etc. |
| PR | Pull Request | |
| RHS | Right-Hand Side | Of a CFG rule. |
| LHS | Left-Hand Side | Of a CFG rule. |
| SA | SQLAlchemy | Common shorthand in code comments. |
| SQL | Structured Query Language | |
| TBD | To Be Determined | |
| TSV | Tab-Separated Values | Alternative to CSV for `tgllfg lex import`. |
| UTF-8 | Unicode Transformation Format (8-bit) | Default encoding for YAML and CSV inputs. |
| UUID | Universally Unique Identifier | UUID v4 (`gen_random_uuid()` from `pgcrypto`). |
| WF | Well-Formedness | Refers to the LFG well-formedness checks (completeness, coherence, subject condition). |
| YAML | YAML Ain't Markup Language | |
| BINARY_FEATS | Binary-feat allowlist | Phase 5n.C.4 — `frozenset[str]` in `src/tgllfg/core/feats.py` enumerating the 52 f-structure features whose values are strictly Boolean (`true` / `false`). Gates the compiler's `[FEAT]` shorthand and validates YAML / equation usage. Audit doc at `docs/feats-binary-audit.md`. |
| bool sentinel | YES/NO → Boolean migration | Phase 5n.C.4 Commits 2–8 — replaced the legacy `"YES"` / `"NO"` string sentinels for binary feats with Python `bool`. ~250 tests swept from `== "YES"` to `is True`. Legacy aliases rejected post-C8. |
| lemma_sense | Per-sense feat row | Phase 5n.C.4 — DB-schema child table indexed by `(lemma_id, sense_index)` and joined via `LexEntry.lemma_sense_id`. Closes §18 L34 (long-standing polysemy across `kuwarto` ROOM vs. FRACTION etc.). |

### Source-text shorthand

| Abbrev | Expansion |
| -------- | -------------------------------------------------------------------------------------------- |
| K | Kroeger 1993, *Phrase Structure and Grammatical Relations in Tagalog*. |
| R71 | Ramos 1971, *Tagalog Dictionary*. |
| R&B | Ramos & Bautista 1986, *Handbook of Tagalog Verbs*. |
| R&C | Ramos & Cena 1990, *Modern Tagalog: Grammatical Explanations and Exercises for Non-native Speakers*. |
| R&G | Ramos & Goulet 1981 — *Conversational Tagalog* (PALI 25) and *Intermediate Tagalog: Developing Cultural Awareness through Language*. |
| S&O | Schachter & Otanes 1972, *Tagalog Reference Grammar*. |
| K&Z | Kaplan & Zaenen 1989, "Long-Distance Dependencies, Constituent Structure, and Functional Uncertainty". |

### Coverage audit / harvest

Terms used in the Phase 8 audit work (`docs/coverage-audit-2026-05.md`, `.claude/plans/tgllfg-harvest-audit.md`, Phase 8 plan).

| Term | Notes |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Wave 1 | First audit wave (PR #56): R&G hand-transcriptions (`rg81-excerpts.md`) + R&B 1986 verb-base inventory. 118 sentences. |
| Wave 2 | Second audit wave (PR #56): R&C 1990 + R&G Intermediate + Ramos 1971 Dictionary. ~1100 sentences. |
| Wave 3 | Third audit wave (PR #59): S&O 1972 + R&G Conversational, both via `pdftotext -layout` from Acrobat-OCR'd PDFs. 1000 sentences (500/source). |
| clitic-glue / clitic-fused | A surface form whose underlying analysis is `base + clitic` (typically the bound `-ng` linker on vowel-final hosts: `akong` = `ako` + `-ng`, `magandang` = `maganda` + `-ng`). Handled by `split_linker_ng` in `src/tgllfg/text/clitics.py`. Phase 8.Q showed the audit's "clitic-fused-token cluster" was a probe artifact, not a parser gap. |
| `-ng` linker | The bound enclitic linker for vowel-final hosts (consonant-final hosts take the free particle `na`). Phase 4 §7.5 splits it via `split_linker_ng` before morph analysis. |
| word-fusion | OCR or transcription artifact where two separate words run together as one surface (`bibilhinko` = `bibilhin` + `ko`). Distinct from clitic-glue (which is natural Tagalog cliticization). |
| DEM-pivot | A predicational clause whose pivot (predicate-position daughter) is a demonstrative determiner: `Ito ang aklat.` "This is the book." Phase 8.X closure. |
| PRON-pivot | A predicational clause whose pivot is a (non-wh) personal pronoun: `Ako ang guro.` "I am the teacher." Phase 8.X closure (N-headed-pivot-NP subset); V-pivot variant (`Tayo ang lumakad.`) remains in Phase 8.S. |
| two-NP equational | A predicational clause whose pivot AND subject are both full NPs: `Si Juan ito.` (Si-pivot, Phase 8.Y) / `Ang lalaki ang doktor.` (ang-pivot, Phase 8.Z). PRED = `'BE-NP <SUBJ>'`. |
| pseudo-cleft | A focus-marked clause of the form `<NP> ang <V-headed-NP>` where the V-headed NP is a headless relative ("the one who Xed"). E.g., `Ang nanay ang nagluto.` "It's the mother who cooked." / "The mother is the one who cooked." Currently zero-parsing in tgllfg (the headless RC doesn't wrap to NP[CASE=NOM]); Phase 8 follow-on. |
| ay-fronting / ay-inverted | The Phase 4 §7.4 topicalization construction `<NP> ay <S>` where the fronted NP is the topic (and typically SUBJ). Examples: `Ako ay kumain.` (V-clause; works), `Ito ay aklat.` (N-pred; Phase 8.Y). |
| naturalistic baseline | The clean-parse rate against unprepared reference-grammar text. As of Phase 8.Z: 7.4% → 8.0% on 2220 sentences across Waves 1+2+3, vs 99.6% on the curated `coverage_corpus.yaml`. |

## 2. References — algorithms, processes, and analytical decisions

The reference texts behind each computational or linguistic
component. Citations follow author-year; full bibliographic details
appear in the bottom section.

### Parsing and unification

| Component | Where | Reference(s) |
| ---------------------------------------- | ------------------------------------------------ | ------------------------------------------------- |
| Earley chart parser | `src/tgllfg/parse/earley.py` | Earley 1970. |
| Predict / Scan / Complete operations | `src/tgllfg/parse/earley.py` | Earley 1970; Aycock & Horspool 2002. |
| Retroactive complete (for ε-rules) | `src/tgllfg/parse/earley.py` | Aycock & Horspool 2002. |
| Packed forest representation | `src/tgllfg/parse/earley.py:PackedForest` | Tomita 1986; Billot & Lang 1989. |
| Backpointer-based tree extraction | `src/tgllfg/parse/earley.py:_iter_histories` | Tomita 1986. |
| Union-find disjoint-set | `src/tgllfg/fstruct/graph.py:FGraph` | Galler & Fischer 1964; Tarjan 1975. |
| Path compression / union by rank | `src/tgllfg/fstruct/graph.py` | Tarjan 1975. |
| Occurs-check | `src/tgllfg/fstruct/graph.py` | Robinson 1965; Knight 1989 §2.4. |
| Two-pass unification (defining → constraining) | `src/tgllfg/fstruct/unify.py:solve` | Kaplan & Bresnan 1982 §3.6. |
| Atomic unification (snapshot / rollback) | `src/tgllfg/fstruct/graph.py:FGraph.unify` | Per-mutation undo journal; on failure the graph rewinds to its pre-call state. |
| Functional uncertainty (regex-path evaluation) | `src/tgllfg/fstruct/fu.py:resolve_regex_for_read` | Kaplan & Zaenen 1989 §3 / Kaplan & Maxwell 1988; FSA traversal with visited-set; K&Z minimality clause picks shortest endpoint. |
| Off-path constraints in FU | `src/tgllfg/fstruct/fu.py` (Phase 6.B C4) | K&Z 1989 §3 — bracketed predicates `<…>` evaluated at intermediate nodes during FSA traversal. |
| Binding equations (FU with reentrancy) | `src/tgllfg/fstruct/unify.py` (Phase 6.B C5) | Equations whose RHS is a regex path on the existing graph and whose LHS is a fresh designator; unifier resolves the RHS endpoint then `graph.unify(lhs, endpoint)`. Used by Phase 6.D LDD relativization, Phase 6.F `sarili` binding. |
| Graph-constraint category matcher | `src/tgllfg/cfg/compile.py:matches` (Phase 6.C) | Strict matcher: `expected.keys() ⊆ candidate.keys()` plus value compat on shared keys. Replaces the pre-6.C "non-conflict" matcher that silently admitted shared-key-absence matches. K&Z 1989 §3 c-structure faithfulness. |
| Particle paradigm dispatch | `src/tgllfg/morph/analyzer.py:_index_particle_paradigms` (Phase 6.I) | Iterates `paradigm_cells` with `base_pos` matching the particle's `pos` against particles with non-empty `affix_class`. Parallels Phase 5n.C.3 Commit 5 `_index_pronoun_paradigms`. |
| Equation-language EBNF | `src/tgllfg/fstruct/equations.py` | Kaplan & Bresnan 1982 (notation); Bresnan 2001 ch. 4. |

### LFG semantics

| Component | Where | Reference(s) |
| ---------------------------------------- | ------------------------------------------------ | ------------------------------------------------- |
| Defining vs. constraining equations | `src/tgllfg/fstruct/equations.py` | Kaplan & Bresnan 1982 §3.6. |
| Set membership for ADJUNCT | `src/tgllfg/fstruct/equations.py:SetMembership` | Bresnan 2001 ch. 4. |
| Completeness check | `src/tgllfg/fstruct/checks.py:_check_completeness` | Kaplan & Bresnan 1982 §4; Bresnan 2001 ch. 4. |
| Coherence check | `src/tgllfg/fstruct/checks.py:_check_coherence` | Kaplan & Bresnan 1982 §4; Bresnan 2001 ch. 4. |
| Subject condition | `src/tgllfg/fstruct/checks.py:_check_subject_condition` | Bresnan 2001 ch. 5. |
| Governable GF inventory | `src/tgllfg/fstruct/checks.py:_BARE_GOVERNABLE` | Bresnan 2001 ch. 4. |
| Bresnan–Kanerva LMT engine | `src/tgllfg/lmt/principles.py` | Bresnan & Kanerva 1989; plan §8.2. |
| sa-NP → typed OBL-θ classifier | `src/tgllfg/lmt/oblique_classifier.py` | Plan §8 (post-solve mutation rationale in `docs/analysis-choices.md`). |
| Pipeline LMT integration | `src/tgllfg/lmt/check.py` | Plan §8.2 (diagnostic policy in `docs/lmt.md`). |
| LMT defensive fallback (Phase 4 heuristic) | `src/tgllfg/lmt/legacy.py:apply_lmt` | Voice-aware role-to-GF mapping; preserved for the no-lex-entry edge case. |

### Morphology and phonology

| Component | Where | Reference(s) |
| ---------------------------------------- | ------------------------------------------------ | ------------------------------------------------- |
| Rule-cascade morphology | `src/tgllfg/morph/analyzer.py` | Koskenniemi 1983 (two-level model conceptually; the cascade is a project-level simplification). |
| CV-reduplication | `src/tgllfg/morph/sandhi.py:cv_reduplicate` | Schachter & Otanes 1972 §3.7; Marantz 1982. |
| First-CV onset (incl. `ng` digraph) | `src/tgllfg/morph/sandhi.py:first_cv` | Schachter & Otanes 1972 §1.5. |
| Vowel-hiatus repair (h-epenthesis) | `src/tgllfg/morph/sandhi.py:attach_suffix` | Schachter & Otanes 1972 §4.21. |
| High-vowel deletion variant | `src/tgllfg/morph/sandhi.py:attach_suffix` | Schachter & Otanes 1972 §4.21. |
| Stem-vowel raising (o → u) | `src/tgllfg/morph/sandhi.py:_raise_final_o` | Schachter & Otanes 1972 §4.21; R&B 1986 paradigm tables. |
| /d/ → /r/ intervocalic | `src/tgllfg/morph/sandhi.py:d_to_r_intervocalic` | Schachter & Otanes 1972 §3.5. |
| Sonorant-initial -in- → ni- | `src/tgllfg/morph/sandhi.py:infix_after_first_consonant` | Schachter & Otanes 1972 §5.20. |
| Nasal substitution (mang-/pang-/nang-) | `src/tgllfg/morph/sandhi.py:nasal_substitute` | Schachter & Otanes 1972 §3.5; Kroeger 1993 §4.4. |
| Affix infixation (after first C) | `src/tgllfg/morph/sandhi.py:infix_after_first_consonant` | Schachter & Otanes 1972 §5.20–5.30. |

### Tagalog grammar

| Component | Where | Reference(s) |
| ---------------------------------------- | ------------------------------------------------ | ------------------------------------------------- |
| Four-voice analysis (AV/OV/DV/IV) | `src/tgllfg/cfg/clause.py` | Kroeger 1993 chs. 1, 4. |
| Subjecthood diagnostics | `docs/analysis-choices.md` §1 | Kroeger 1993 chs. 2–3. |
| Objecthood diagnostics | `docs/analysis-choices.md` §1 | Kroeger 1993 chs. 2–3. |
| OBJ-uniform analysis (ng-non-pivot → OBJ) | `src/tgllfg/cfg/clause.py` | Kroeger 1993 ch. 2; vs. older OBL-AG analysis (Schachter & Otanes 1972 ch. 5). |
| `mang-` distributive paradigm | `data/tgl/paradigms.yaml` | Kroeger 1993 §4.4. |
| `maka-` abilitative | `data/tgl/paradigms.yaml` | Kroeger 1993 §4.5. |
| `ma-` non-volitional / stative | `data/tgl/paradigms.yaml` | Schachter & Otanes 1972 §5.27; Kroeger 1993 §4.5. |
| Affix-class membership per verb | `data/tgl/verbs.yaml` | Ramos & Bautista 1986 (per-verb index). |
| Verb paradigm tables | `tests/tgllfg/test_morph_paradigms.py` | Ramos & Bautista 1986; Schachter & Otanes 1972 ch. 5. |
| Ang-NP as pivot / SUBJ | `src/tgllfg/cfg/clause.py` | Kroeger 1993 chs. 2–3. |
| Voice-alias mapping (S&O ↔ Kroeger) | `data/tgl/voice_aliases.yaml` | Kroeger 1993 §1.3 (reduction); Schachter & Otanes 1972 §§5.20–5.30 (focus inventory). |
| Wackernagel 2P clitic placement | `src/tgllfg/clitics/` (Phase 4 §7.3) | Wackernagel 1892; Schachter & Otanes 1972 ch. 6; Kroeger 1993 §3.2. |
| `hindi`-wrap (sentential negation) | `src/tgllfg/cfg/negation.py` (Phase 4 §7.2) | Schachter & Otanes 1972 §6.4; recursive `S → PART[POLARITY=NEG] S` clause-wrap. Sets `POL=NEG` on the matrix. |
| `kita`-fusion (1SG.GEN+2SG.NOM portmanteau) | `src/tgllfg/cfg/clitic.py` (Phase 5e Commit 20) | Schachter & Otanes 1972 §3.2; Kroeger 1993 §2.2. Three-frame rule family with synthetic SUBJ + 1sg-actor projection from the `kita` atomic-feat carrier. |
| Hyphen-merge tokenizer pre-pass | `src/tgllfg/text/multiword.py:merge_hyphen_compounds` (Phase 5f Commit 14) | Collapses canonical hyphenated surfaces (`tag-init`, `mag-isa`, `paminsan-minsan`, `tig-isa`, `humigit-kumulang`, `kani-kaniya`, `daan-daan`, `magkapareho`, etc.) into single tokens for analyzer lookup; the LEMMA feat preserves the user-visible hyphenated form. Still load-bearing post Phase 6.I (generalized to support productive ADV-redup paradigm output). |
| *Ay*-inversion / topicalization | `src/tgllfg/cfg/extraction.py` (Phase 4 §7.4) | Schachter & Otanes 1972 §6.5; Kroeger 1993 §3.6. |
| SUBJ-only relativization | `src/tgllfg/cfg/extraction.py` (Phase 4 §7.5) | Kroeger 1993 ch. 5; Bresnan 2001 ch. 5. |
| Long-distance relativization via FU | `src/tgllfg/cfg/extraction.py` (Phase 6.D — §18.1.2 L47) | Kaplan & Zaenen 1989 §3 eq. 39 (English topicalization adapted to Tagalog XCOMP body); 6 S_XCOMP-bodied wrap variants with constraining-form `=c (↓3 XCOMP* SUBJ)`. |
| Free relative `kung sino` / `kung ano` as DP | `src/tgllfg/cfg/extraction.py` (Phase 6.E — §18.1.2 L93) | 3 NP wrap rules consume `S_INTERROG_COMP[Q_TYPE=WH]` as non-COMP NP arguments with `FREE_REL=true` head marker; selectional disambiguation from indirect-Q via matrix predicate's argument frame. |
| Reflexive `sarili` anaphora binding | `src/tgllfg/cfg/control.py` (Phase 6.F — §18.1.2 L104) | Kroeger 1993 §2.3 actor-binder theory; 24 binding-rule variants (6 voice_specs × 2 NP orders × 2 binding directions) with `ANTECEDENT` reentrancy; LEMMA-gated via `=c 'sarili'`. |
| NP-from-N modifier projection | `src/tgllfg/cfg/nominal.py` (Phase 6.G — §18.1.2 L32) | SHARE+SHARE pattern `(↑) = ↓1, (↑) = ↓2` on simple NP rules to propagate modifier feats (SEM_CLASS, APPROX, DISTRIB) onto matrix NP; `N_RC` tag-feat blocks N-level-RC duplication. |
| Floated-Q number agreement | `src/tgllfg/cfg/clitic.py` (Phase 6.H — §18.1.2 L33) | Three-variant base float rule split: bare Q (no DUAL) / Q[DUAL] + `=c 'PL'` / Q[DUAL] + `¬ NUM`. Agreement-by-constraining-equation idiom per Kroeger 1993 §3. |
| Productive ADV reduplication | `data/tgl/paradigms.yaml` + `morph/analyzer.py` (Phase 6.I — §18.1.2 L105) | New `adv_redup` paradigm cell + `_index_particle_paradigms` analyzer dispatch; `Particle.affix_class` field added. LEMMA construction for `redup_root`-final cells: pre-redup base hyphenated with root citation. References Schachter & Otanes 1972 §3.5; R&B 1986 ch. 4. |
| Equi / functional control | `src/tgllfg/cfg/control.py` (Phase 4 §7.6) | Bresnan 1982 ("Control and Complementation"); Kroeger 1993 §6.1. |
| Subject-to-subject raising | `src/tgllfg/cfg/control.py` (Phase 4 §7.6) | Bresnan 2001 ch. 12; Kroeger 1993 §6.2. |
| `pa-` causative | `src/tgllfg/cfg/clause.py` (Phase 4 §7.7) | Schachter & Otanes 1972 §5.30; Kroeger 1993 §4.5. |

### Database / engineering

| Component | Where | Reference(s) |
| ---------------------------------------- | ------------------------------------------------ | ------------------------------------------------- |
| Alembic migration framework | `alembic/` | Alembic documentation; SQLAlchemy 2.x docs. |
| Trigram indexing for fuzzy lemma lookup | `alembic/versions/0001_baseline.py` | PostgreSQL `pg_trgm` extension docs. |
| Full-text search via `tsvector` | `alembic/versions/0001_baseline.py` | PostgreSQL FTS docs. |
| UUID v4 PK generation | `alembic/versions/0001_baseline.py` | PostgreSQL `pgcrypto.gen_random_uuid()` docs. |
| Async SQLAlchemy + asyncpg | `src/tgllfg/lex/` | SQLAlchemy 2.x async docs; asyncpg docs. |
| Testcontainers-based test isolation | `tests/tgllfg/conftest.py` | testcontainers-python docs. |
| Property-based testing | various test files | Hypothesis docs. |

## 3. Bibliography

Full citations for the works referenced above. Project-internal docs
(`docs/analysis-choices.md`, `docs/lexicon.md`, this file) cross-reference
these entries.

- **Aycock & Horspool 2002.** Aycock, John and R. Nigel Horspool. 2002.
  "Practical Earley Parsing." *The Computer Journal* 45(6): 620–630.
- **Billot & Lang 1989.** Billot, Sylvie and Bernard Lang. 1989. "The
  Structure of Shared Forests in Ambiguous Parsing." *ACL '89*.
- **Bloomfield 1917.** Bloomfield, Leonard. 1917. *Tagalog Texts with
  Grammatical Analysis*. University of Illinois.
- **Bresnan 1982.** Bresnan, Joan, ed. 1982. *The Mental Representation of
  Grammatical Relations*. MIT Press. (Includes Bresnan's "Control and
  Complementation" chapter.)
- **Bresnan 2001.** Bresnan, Joan. 2001. *Lexical-Functional Syntax*.
  Blackwell.
- **Bresnan & Kanerva 1989.** Bresnan, Joan and Jonni Kanerva. 1989.
  "Locative Inversion in Chichewa: A Case Study of Factorization in
  Grammar." *Linguistic Inquiry* 20(1): 1–50.
- **Dalrymple 2001.** Dalrymple, Mary. 2001. *Lexical Functional
  Grammar*. Academic Press (Syntax and Semantics 34). Modern
  LFG reference; ch. 14 covers functional uncertainty + LDD.
  Cited for Phase 6.B FU semantics and Phase 6.F inside-out
  designator deferral.
- **Earley 1970.** Earley, Jay. 1970. "An Efficient Context-Free Parsing
  Algorithm." *Communications of the ACM* 13(2): 94–102.
- **Galler & Fischer 1964.** Galler, Bernard A. and Michael J. Fischer. 1964.
  "An Improved Equivalence Algorithm." *Communications of the ACM* 7(5):
  301–303.
- **Kaplan & Bresnan 1982.** Kaplan, Ronald M. and Joan Bresnan. 1982.
  "Lexical-Functional Grammar: A Formal System for Grammatical
  Representation." In Bresnan 1982: 173–281.
- **Kaplan & Maxwell 1988.** Kaplan, Ronald M. and John T. Maxwell.
  1988. "An Algorithm for Functional Uncertainty." *Proceedings of
  COLING-88*. Provides the FSA-based satisfiability algorithm
  underlying Phase 6.B's FU evaluator (`src/tgllfg/fstruct/fu.py`).
- **Kaplan & Zaenen 1989.** Kaplan, Ronald M. and Annie Zaenen.
  1989. "Long-Distance Dependencies, Constituent Structure, and
  Functional Uncertainty." In Mark Baltin and Anthony Kroch (eds.),
  *Alternative Conceptions of Phrase Structure*, University of
  Chicago Press. Reprinted in Mary Dalrymple et al. (eds.) 1995,
  *Formal Issues in Lexical-Functional Grammar*, CSLI Lecture
  Notes. The foundational FU paper; §3 specifies the regex-path
  designators, decidability proofs, and minimality clause that
  Phase 6.B implements. PDF in `data/tgl/references/Kaplan-Zaenen-1989-LSS-CStruct-FU.pdf`
  (gitignored).
- **Knight 1989.** Knight, Kevin. 1989. "Unification: A Multidisciplinary
  Survey." *ACM Computing Surveys* 21(1): 93–124.
- **Koskenniemi 1983.** Koskenniemi, Kimmo. 1983. *Two-Level Morphology: A
  General Computational Model for Word-Form Recognition and
  Production*. University of Helsinki.
- **Kroeger 1993.** Kroeger, Paul. 1993. *Phrase Structure and Grammatical
  Relations in Tagalog*. CSLI Publications.
- **Manueli (TBD).** Cited in `docs/analysis-choices.md` §1 as
  bearing on the OBJ-θ vs OBJ question for DV/IV; full reference to be
  added once the literature review completes.
- **Marantz 1982.** Marantz, Alec. 1982. "Re Reduplication." *Linguistic
  Inquiry* 13(3): 435–482.
- **Mercado (TBD).** Cited in `docs/analysis-choices.md` §1 as
  bearing on the OBJ-θ vs OBJ question for DV/IV; full reference to be
  added once the literature review completes.
- **Ramos 1971.** Ramos, Teresita V. 1971. *Tagalog Dictionary*. University
  of Hawaii Press. (User holds a purchased copy; an electronic copy is
  staged under `data/tgl/references/`, gitignored.)
- **Ramos & Bautista 1986.** Ramos, Teresita V. and Maria Lourdes
  Bautista. 1986. *Handbook of Tagalog Verbs: Inflections, Modes, and
  Aspects*. University of Hawaii Press. (User holds a purchased
  electronic copy under `data/tgl/references/`, gitignored. Cited
  inline in `data/tgl/verbs.yaml` as "R&B" with page numbers.)
- **Robinson 1965.** Robinson, J. A. 1965. "A Machine-Oriented Logic
  Based on the Resolution Principle." *Journal of the ACM* 12(1): 23–41.
- **Schachter & Otanes 1972.** Schachter, Paul and Fe T. Otanes. 1972.
  *Tagalog Reference Grammar*. University of California Press.
- **Tarjan 1975.** Tarjan, Robert E. 1975. "Efficiency of a Good but Not
  Linear Set Union Algorithm." *Journal of the ACM* 22(2): 215–225.
- **Tomita 1986.** Tomita, Masaru. 1986. *Efficient Parsing for Natural
  Language: A Fast Algorithm for Practical Systems*. Kluwer.
- **Wackernagel 1892.** Wackernagel, Jacob. 1892. "Über ein Gesetz der
  indogermanischen Wortstellung." *Indogermanische Forschungen* 1:
  333–436.
