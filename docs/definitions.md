# Definitions

Two reference tables for the tgllfg codebase: abbreviations used in
code, comments, tests, and other docs; and the source texts behind
each algorithm or analytical decision the engine implements.

## 1. Acronyms and abbreviations

Grouped by category for readability; alphabetical within each
group.

### LFG framework

| Abbrev   | Expansion                                | Notes                                                                                              |
|----------|------------------------------------------|----------------------------------------------------------------------------------------------------|
| ADJ      | Adjunct                                  | Set-valued, non-governable f-structure attribute. Synonym of ADJUNCT in the code.                  |
| ADJUNCT  | Adjunct                                  | Long form used in equations (`↓ ∈ (↑ ADJUNCT)`).                                                   |
| ANTECEDENT | Quantifier antecedent                  | Phase 4 §7.8 — binding feature on a floated quantifier; `(↓ ANTECEDENT) = (↑ SUBJ)` links *lahat* to the SUBJ. |
| AVM      | Attribute-Value Matrix                   | The shape of an f-structure.                                                                       |
| a-structure | Argument structure                    | The thematic-role list a verb projects (e.g. `[AGENT, PATIENT]`).                                  |
| CFG      | Context-Free Grammar                     | The c-structure layer of LFG; productions live in `src/tgllfg/cfg/grammar.py`.                     |
| COMP     | Clausal complement                       | Closed sentential argument; governable.                                                            |
| c-structure | Constituent structure                 | Phrase-structure tree produced by the parser.                                                      |
| f-structure | Functional structure                  | AVM produced by unification; carries grammatical functions.                                        |
| FOCUS    | Focus                                    | Discourse function; non-governable in the LFG sense.                                               |
| GF       | Grammatical Function                     | SUBJ, OBJ, OBL-θ, ADJ, etc. (Distinct from "Goal Focus" in S&O — disambiguated by context.)        |
| [±r, ±o] | Bresnan–Kanerva intrinsic features       | The feature pair that drives LMT mapping. `r` = restricted (cannot be SUBJ); `o` = objective (object-like). Truth table in `docs/lmt.md`. |
| LEX-ASTRUCT | Lexical a-structure                   | F-structure attribute carrying the verb's role list, used by LMT.                                  |
| LFG      | Lexical-Functional Grammar               | The formalism the parser implements.                                                               |
| LINK     | Linker                                   | Phase 4 §7.5 — `na` / `-ng` allomorphs that join a head NP to its relative clause or modifier.     |
| LMT      | Lexical Mapping Theory                   | Maps thematic roles to GFs via [±r, ±o] features. Implemented in Phase 5 §8 — see `docs/lmt.md`.   |
| OBJ      | Object                                   | Governable GF; second core argument in transitives.                                                |
| OBJ-θ    | Typed object                             | OBJ-GOAL, OBJ-RECIPIENT, etc. Generic prefix `OBJ-` is recognised as governable.                   |
| OBL      | Oblique                                  | Governable GF prefix; OBL-LOC, OBL-GOAL, OBL-BEN.                                                  |
| OBL-AG   | Oblique agent                            | Demoted-agent analysis used in older "passive" treatments of non-AV. Rejected; see §1 of this doc. |
| OBL-BEN  | Benefactive oblique                      | Typed OBL-θ; assigned by the LMT engine when a sa-NP role's intrinsics are `[+r, -o]` and the role is `BENEFICIARY`. |
| OBL-GOAL | Goal oblique                             | Typed OBL-θ; LMT engine assigns it for `GOAL` roles with `[+r, -o]` intrinsics.                    |
| OBL-INSTR | Instrumental oblique                    | Typed OBL-θ; LMT engine assigns it for `INSTRUMENT` roles. No current Phase 4 BASE entry emits one. |
| OBL-LOC  | Locative oblique                         | Typed OBL-θ; LMT engine assigns it for `LOCATION` roles. Used by motion verbs (e.g. `lakad`).      |
| OBL-RECIP | Recipient oblique                       | Typed OBL-θ; LMT engine assigns it for `RECIPIENT` roles in non-DV voices.                         |
| OBL-θ    | Typed oblique                            | Generic prefix `OBL-` is recognised as governable; specific suffixes follow `Role.gf_suffix` (LOC, BEN, INSTR, RECIP, GOAL, …). |
| PRED     | Predicate                                | F-structure attribute holding the predicate template (e.g. `EAT <SUBJ, OBJ>`).                     |
| Q        | Quantifier                               | POS for floated quantifiers (`lahat`, `iba`); Phase 4 §7.8.                                        |
| QUANT    | Quantifier feature                       | F-structure attribute on a floated quantifier (e.g. *lahat*); Phase 4 §7.8.                        |
| REL-PRO  | Relative pronoun                         | Constraining-equation target for SUBJ-only relativization (Phase 4 §7.5).                          |
| SUBJ     | Subject                                  | Governable GF; corresponds to the *ang*-NP pivot in Tagalog.                                       |
| TOPIC    | Topic                                    | Non-governable discourse function; targeted by *ay*-inversion (Phase 4 §7.4).                      |
| XCOMP    | Open complement                          | Sentential complement with shared SUBJ (control verbs).                                            |

### Tagalog voice / focus inventory

| Abbrev | Expansion                  | Tradition          | Notes                                                                          |
|--------|----------------------------|--------------------|--------------------------------------------------------------------------------|
| AF     | Actor Focus                | Schachter & Otanes | Maps to AV in Kroeger's reduction.                                             |
| AV     | Actor Voice                | Kroeger 1993       | Pivot is the actor; `-um-` / `mag-` / `mang-` / `maka-` / `ma-` AV affix classes. |
| BF     | Benefactive Focus          | Schachter & Otanes | Maps to IV with APPL=BEN.                                                      |
| CF     | Causative Focus            | Schachter & Otanes | Maps to AV with CAUS=DIRECT for the bare `pa-` form; biclausal otherwise.      |
| DF     | Directional Focus          | Schachter & Otanes | Maps to DV.                                                                    |
| DV     | Dative Voice               | Kroeger 1993       | Pivot is the locative / source / recipient; `-an` suffix.                      |
| GF     | Goal Focus                 | Schachter & Otanes | Maps to OV. (Disambiguated from "Grammatical Function" by context.)            |
| IF     | Instrumental Focus         | Schachter & Otanes | Maps to IV with APPL=INSTR.                                                    |
| IV     | Instrumental Voice         | Kroeger 1993       | Pivot is the conveyed / instrument / benefactive; `i-` prefix.                 |
| LF     | Locative Focus             | Schachter & Otanes | Maps to DV.                                                                    |
| OV     | Objective Voice            | Kroeger 1993       | Pivot is the patient / theme; `-in` suffix or realis `-in-` infix.             |
| PF     | Patient Focus              | Older terminology  | Synonym of GF; maps to OV.                                                     |
| PV     | Patient Voice              | Older terminology  | Synonym of OV. The codebase migrated to OV in Phase 2.                         |
| RF     | Reason Focus               | Schachter & Otanes | Maps to IV with APPL=REASON.                                                   |

### Aspect / mood / polarity

| Abbrev   | Expansion                  | Notes                                                                                              |
|----------|----------------------------|----------------------------------------------------------------------------------------------------|
| ABIL     | Abilitative mood           | `maka-` class (e.g. `nakakain` "was able to eat").                                                 |
| ASPECT   | Aspect feature             | F-structure attribute taking PFV / IPFV / CTPL / RECPFV.                                           |
| CTPL     | Contemplative aspect       | "Future" / irrealis. CV-redup without realis `-in-`.                                               |
| IMP      | Imperative mood            | Phase 4 §7.2.                                                                                      |
| IND      | Indicative mood            | The default mood feature value.                                                                    |
| IPFV     | Imperfective aspect        | "Progressive". CV-redup + realis `-in-` infix.                                                     |
| IRREALIS | Irrealis                   | Aspectual feature opposing REALIS; CTPL is irrealis.                                               |
| MOOD     | Mood feature               | F-structure attribute taking IND / IMP / ABIL / NVOL / SOC.                                        |
| NEG      | Negation                   | F-structure attribute set by `hindi` / `huwag` (Phase 4 §7.2).                                     |
| NVOL     | Non-volitional mood        | `ma-` non-volitional class (e.g. `natulog` "happened to fall asleep").                             |
| PFV      | Perfective aspect          | "Past / completed". Realis `-in-` without CV-redup.                                                |
| POL      | Polarity                   | NEG vs. affirmative.                                                                               |
| REALIS   | Realis                     | Aspectual feature opposing IRREALIS; PFV/IPFV are realis.                                          |
| RECPFV   | Recent perfective          | "Just-completed" aspect (`katatapos`-style); Phase 4 §7.2.                                         |
| SOC      | Social mood                | "Common" or social-deontic mood; Phase 4 §7.2.                                                     |
| STAT     | Stative                    | Subset of NVOL / `ma-` semantics (e.g. *natulog*).                                                 |
| TR       | Transitivity               | Lemma feature taking TR (transitive) / INTR (intransitive); from `verbs.yaml`.                     |
| INTR     | Intransitive               | Value of TR.                                                                                       |

### Case / nominal features

| Abbrev   | Expansion                  | Notes                                                                                              |
|----------|----------------------------|----------------------------------------------------------------------------------------------------|
| 2P       | Second-position (clitic)   | Clitic class for Wackernagel placement. (Phase 4 §7.3.)                                            |
| CASE     | Case feature               | F-structure attribute taking NOM / GEN / DAT.                                                      |
| CLUSV    | Clusivity                  | INCL / EXCL on first-person plural pronouns.                                                       |
| DAT      | Dative case                | *sa*-marker (`sa`, `kay`).                                                                         |
| DEIXIS   | Deixis                     | PROX / MED / DIST on demonstratives.                                                               |
| DEM      | Demonstrative flag         | `YES` / `NO` (Phase 4 §7.8) — gates the standalone-NP rule for demonstratives like *ito* / *iyan*. |
| DET      | Determiner                 | POS for *ang* / *ng* (when functioning as common-noun marker), demonstratives.                     |
| DIST     | Distal                     | *iyon* / *yon*.                                                                                    |
| EXCL     | Exclusive (clusivity)      | `kami` (1pl-excl).                                                                                 |
| GEN      | Genitive case              | *ng* / *ni* marker.                                                                                |
| HUMAN    | Human feature              | Triggers personal-name case markers (*si*/*ni*/*kay*) over common-noun markers.                    |
| INCL     | Inclusive (clusivity)      | `tayo` (1pl-incl).                                                                                 |
| MED      | Medial                     | *iyan* / *yan*.                                                                                    |
| NOM      | Nominative case            | *ang* / *si* marker. SUBJ in the four-voice mapping.                                               |
| NUM      | Number                     | SG / PL.                                                                                           |
| PERS     | Person                     | 1 / 2 / 3.                                                                                         |
| PL       | Plural                     |                                                                                                    |
| POSS     | Possessor                  | F-structure attribute holding the possessor NP (Phase 4 §7.8 NP-internal possessive `bata ng nanay`). |
| PROX     | Proximal                   | *ito* / *ire*.                                                                                     |
| SG       | Singular                   |                                                                                                    |

### Theta roles (a-structure)

| Abbrev      | Expansion                | Used in                                                                                       |
|-------------|--------------------------|-----------------------------------------------------------------------------------------------|
| ACTOR       | Actor                    | AV intransitive (e.g. *kumain ang aso*). Generic role name when AGENT/PATIENT distinction isn't needed. |
| AGENT       | Agent                    | The volitional doer in transitive predicates.                                                 |
| BEN         | Beneficiary              | Pivot in `ipag-` IV-BEN applicative (e.g. *ipinaggawa*); typed `OBL-BEN` otherwise.           |
| CAUSEE      | Causee                   | The forced participant in `pa-` direct (monoclausal) causatives; pivot in *pinakain ang bata*. Surfaces as embedded SUBJ in `magpa-` indirect causatives. |
| CAUSER      | Causer                   | The instigator in causatives. SUBJ in `magpa-` indirect (matrix); `OBJ-CAUSER` (typed OBJ-θ) in `pa-` direct. |
| COMPLEMENT  | Open-complement target   | The XCOMP-bound argument of control verbs (gusto, payag, pilit, utos). Off the [±r, ±o] truth table. |
| CONVEYED    | Conveyed                 | The object conveyed in IV (e.g. *liham* in *isinulat ang liham*).                             |
| EVENT       | Caused event             | XCOMP-bound argument of `magpa-` indirect causatives. Off the [±r, ±o] truth table.           |
| EXPERIENCER | Experiencer              | Mental subject of psych control verbs (gusto, ayaw, kaya). GEN-marked but maps to SUBJ — see `docs/lmt.md`. |
| GOAL        | Goal                     | The endpoint / recipient in DV. Used by the synthesizer fallback for DV; Phase 4 BASE entries use RECIPIENT instead. |
| INSTR       | Instrument               | The instrument argument; typed `OBL-INSTR`. No current Phase 4 BASE entry emits one.          |
| LOC         | Location                 | The location argument; typed `OBL-LOC` for motion verbs (e.g. `lakad`).                       |
| PATIENT     | Patient                  | The undergoer in transitive predicates; pivot in OV.                                          |
| REASON      | Reason / cause           | Phase 5 LMT — would be typed `OBL-REASON`. No current Phase 4 BASE entry emits one (pending `ika-` reason applicative). |
| RECIPIENT   | Recipient                | DV pivot for verbs like *sulat* (e.g. *sinulatan ang ina*). Alternate label for GOAL.         |
| STIMULUS    | Stimulus                 | Plan §8.1 role for the cause of a mental state. No current Phase 4 BASE entry emits one.      |
| THEME       | Theme                    | Generic patient-like role used for semantic underspecification.                               |

### Argument-structure secondary features

| Abbrev   | Expansion                          | Values                                       | Notes                                            |
|----------|------------------------------------|----------------------------------------------|--------------------------------------------------|
| APPL     | Applicative                        | `INSTR`, `BEN`, `REASON`, `CONVEY`, `∅`      | Subset of voice that an applicative selects.     |
| CAUS     | Causative                          | `DIRECT`, `INDIRECT`, `∅`                    | `pa-` direct vs biclausal indirect.              |
| CTRL_CLASS | Control class                    | `PSYCH`, `INTRANS`, `TRANS`, `NONE`          | Phase 4 §7.6 — discriminates control-verb subtypes for the SUBJ-binding equation. |

### Affix-class labels (`verbs.yaml` `affix_class:`)

| Label      | Expansion                                                                                  |
|------------|--------------------------------------------------------------------------------------------|
| an_oblig   | -an obligatory: takes the `-an` DV suffix.                                                 |
| in_oblig   | -in obligatory: takes the `-in` OV suffix and the realis `-in-` infix.                     |
| i_oblig    | i- obligatory: takes the `i-` IV prefix.                                                   |
| ma         | ma- non-volitional / stative AV class (MOOD=NVOL).                                         |
| mag        | mag- AV class (e.g. *naglinis*).                                                           |
| maka       | maka- abilitative AV class (MOOD=ABIL).                                                    |
| mang       | mang- distributive AV class with nasal substitution.                                       |
| um         | -um- AV class (e.g. *kumain*).                                                             |

### Per-root sandhi flags (`verbs.yaml` `sandhi_flags:`)

| Flag                  | Effect                                                                                                |
|-----------------------|-------------------------------------------------------------------------------------------------------|
| d_to_r                | Apply intervocalic /d/ → /r/ post-processor (e.g. *dadating* → *darating*).                           |
| high_vowel_deletion   | Delete a stem-final /i/ or /u/ before a vowel-initial suffix (e.g. *bili* + *-in* → *bilhin*).        |

### Engineering / project

| Abbrev   | Expansion                                | Notes                                                                                              |
|----------|------------------------------------------|----------------------------------------------------------------------------------------------------|
| API      | Application Programming Interface        |                                                                                                    |
| AST      | Abstract Syntax Tree                     | Used in equation-language documentation.                                                           |
| AVM      | Attribute-Value Matrix                   | (Listed under LFG too.)                                                                            |
| CI       | Continuous Integration                   | GitHub Actions runs the test suite on PR.                                                          |
| CLI      | Command-Line Interface                   | The `tgllfg` entry point shipped with the package.                                                 |
| CSV      | Comma-Separated Values                   | Used by `tgllfg lex import`.                                                                       |
| DB       | Database                                 | The Postgres-backed lexicon (Phase 3).                                                             |
| EBNF     | Extended Backus–Naur Form                | The equation-language grammar is documented in EBNF.                                               |
| FK       | Foreign Key                              |                                                                                                    |
| FST      | Finite-State Transducer                  | Considered for Phase 2 morphology; rejected for the rule cascade due to macOS install friction.    |
| GIN      | Generalized Inverted Index               | PostgreSQL index type used for trigram and FTS columns.                                            |
| HTTP     | Hypertext Transfer Protocol              |                                                                                                    |
| IPA      | International Phonetic Alphabet          |                                                                                                    |
| ISO      | International Organization for Standardization | Used in `language.iso_code`.                                                                  |
| JSON     | JavaScript Object Notation               |                                                                                                    |
| JSONB    | JSON binary                              | PostgreSQL JSON column type used for AVMs and lists.                                               |
| MORPH    | Morphology                               | The rule-cascade morphological analyzer / generator (Phase 2 / 2C).                                |
| MR       | Merge Request                            | Synonym for PR in some shops; user uses both.                                                      |
| OCR      | Optical Character Recognition            | Used to ingest dictionary scans during Phase 2C scale-up.                                          |
| ORM      | Object-Relational Mapper                 | SQLAlchemy 2.x.                                                                                    |
| OS       | Operating System                         |                                                                                                    |
| PDF      | Portable Document Format                 |                                                                                                    |
| PK       | Primary Key                              |                                                                                                    |
| POS      | Part of Speech                           | VERB / NOUN / ADJ / DET / ADP / PART / PRON / etc.                                                 |
| PR       | Pull Request                             |                                                                                                    |
| RHS      | Right-Hand Side                          | Of a CFG rule.                                                                                     |
| LHS      | Left-Hand Side                           | Of a CFG rule.                                                                                     |
| SA       | SQLAlchemy                               | Common shorthand in code comments.                                                                 |
| SQL      | Structured Query Language                |                                                                                                    |
| TBD      | To Be Determined                         |                                                                                                    |
| TSV      | Tab-Separated Values                     | Alternative to CSV for `tgllfg lex import`.                                                        |
| UTF-8    | Unicode Transformation Format (8-bit)    | Default encoding for YAML and CSV inputs.                                                          |
| UUID     | Universally Unique Identifier            | UUID v4 (`gen_random_uuid()` from `pgcrypto`).                                                     |
| WF       | Well-Formedness                          | Refers to the LFG well-formedness checks (completeness, coherence, subject condition).             |
| YAML     | YAML Ain't Markup Language               |                                                                                                    |

### Source-text shorthand

| Abbrev | Expansion                                                                                  |
|--------|--------------------------------------------------------------------------------------------|
| K      | Kroeger 1993, *Phrase Structure and Grammatical Relations in Tagalog*.                     |
| R71    | Ramos 1971, *Tagalog Dictionary*.                                                          |
| R&B    | Ramos & Bautista 1986, *Handbook of Tagalog Verbs*.                                        |
| S&O    | Schachter & Otanes 1972, *Tagalog Reference Grammar*.                                      |

## 2. References — algorithms, processes, and analytical decisions

The reference texts behind each computational or linguistic
component. Citations follow author-year; full bibliographic details
appear in the bottom section.

### Parsing and unification

| Component                              | Where                                          | Reference(s)                                    |
|----------------------------------------|------------------------------------------------|-------------------------------------------------|
| Earley chart parser                    | `src/tgllfg/parse/earley.py`                   | Earley 1970.                                    |
| Predict / Scan / Complete operations   | `src/tgllfg/parse/earley.py`                   | Earley 1970; Aycock & Horspool 2002.            |
| Retroactive complete (for ε-rules)     | `src/tgllfg/parse/earley.py`                   | Aycock & Horspool 2002.                         |
| Packed forest representation           | `src/tgllfg/parse/earley.py:PackedForest`      | Tomita 1986; Billot & Lang 1989.                |
| Backpointer-based tree extraction      | `src/tgllfg/parse/earley.py:_iter_histories`   | Tomita 1986.                                    |
| Union-find disjoint-set                | `src/tgllfg/fstruct/graph.py:FGraph`           | Galler & Fischer 1964; Tarjan 1975.             |
| Path compression / union by rank       | `src/tgllfg/fstruct/graph.py`                  | Tarjan 1975.                                    |
| Occurs-check                           | `src/tgllfg/fstruct/graph.py`                  | Robinson 1965; Knight 1989 §2.4.                |
| Two-pass unification (defining → constraining) | `src/tgllfg/fstruct/unify.py:solve`    | Kaplan & Bresnan 1982 §3.6.                     |
| Equation-language EBNF                 | `src/tgllfg/fstruct/equations.py`              | Kaplan & Bresnan 1982 (notation); Bresnan 2001 ch. 4. |

### LFG semantics

| Component                              | Where                                          | Reference(s)                                    |
|----------------------------------------|------------------------------------------------|-------------------------------------------------|
| Defining vs. constraining equations    | `src/tgllfg/fstruct/equations.py`              | Kaplan & Bresnan 1982 §3.6.                     |
| Set membership for ADJUNCT             | `src/tgllfg/fstruct/equations.py:SetMembership` | Bresnan 2001 ch. 4.                             |
| Completeness check                     | `src/tgllfg/fstruct/checks.py:_check_completeness` | Kaplan & Bresnan 1982 §4; Bresnan 2001 ch. 4.   |
| Coherence check                        | `src/tgllfg/fstruct/checks.py:_check_coherence` | Kaplan & Bresnan 1982 §4; Bresnan 2001 ch. 4.   |
| Subject condition                      | `src/tgllfg/fstruct/checks.py:_check_subject_condition` | Bresnan 2001 ch. 5.                       |
| Governable GF inventory                | `src/tgllfg/fstruct/checks.py:_BARE_GOVERNABLE` | Bresnan 2001 ch. 4.                             |
| Bresnan–Kanerva LMT engine             | `src/tgllfg/lmt/principles.py`                 | Bresnan & Kanerva 1989; plan §8.2.              |
| sa-NP → typed OBL-θ classifier         | `src/tgllfg/lmt/oblique_classifier.py`         | Plan §8 (post-solve mutation rationale in `docs/analysis-choices.md`). |
| Pipeline LMT integration               | `src/tgllfg/lmt/check.py`                      | Plan §8.2 (diagnostic policy in `docs/lmt.md`). |
| LMT defensive fallback (Phase 4 heuristic) | `src/tgllfg/lmt/legacy.py:apply_lmt`       | Voice-aware role-to-GF mapping; preserved for the no-lex-entry edge case. |

### Morphology and phonology

| Component                              | Where                                          | Reference(s)                                    |
|----------------------------------------|------------------------------------------------|-------------------------------------------------|
| Rule-cascade morphology                | `src/tgllfg/morph/analyzer.py`                 | Koskenniemi 1983 (two-level model conceptually; the cascade is a project-level simplification). |
| CV-reduplication                       | `src/tgllfg/morph/sandhi.py:cv_reduplicate`    | Schachter & Otanes 1972 §3.7; Marantz 1982.     |
| First-CV onset (incl. `ng` digraph)    | `src/tgllfg/morph/sandhi.py:first_cv`          | Schachter & Otanes 1972 §1.5.                   |
| Vowel-hiatus repair (h-epenthesis)     | `src/tgllfg/morph/sandhi.py:attach_suffix`     | Schachter & Otanes 1972 §4.21.                  |
| High-vowel deletion variant            | `src/tgllfg/morph/sandhi.py:attach_suffix`     | Schachter & Otanes 1972 §4.21.                  |
| Stem-vowel raising (o → u)             | `src/tgllfg/morph/sandhi.py:_raise_final_o`    | Schachter & Otanes 1972 §4.21; R&B 1986 paradigm tables. |
| /d/ → /r/ intervocalic                 | `src/tgllfg/morph/sandhi.py:d_to_r_intervocalic` | Schachter & Otanes 1972 §3.5.                  |
| Sonorant-initial -in- → ni-            | `src/tgllfg/morph/sandhi.py:infix_after_first_consonant` | Schachter & Otanes 1972 §5.20.        |
| Nasal substitution (mang-/pang-/nang-) | `src/tgllfg/morph/sandhi.py:nasal_substitute`  | Schachter & Otanes 1972 §3.5; Kroeger 1993 §4.4. |
| Affix infixation (after first C)       | `src/tgllfg/morph/sandhi.py:infix_after_first_consonant` | Schachter & Otanes 1972 §5.20–5.30.   |

### Tagalog grammar

| Component                              | Where                                          | Reference(s)                                    |
|----------------------------------------|------------------------------------------------|-------------------------------------------------|
| Four-voice analysis (AV/OV/DV/IV)      | `src/tgllfg/cfg/grammar.py`                    | Kroeger 1993 chs. 1, 4.                         |
| Subjecthood diagnostics                | `docs/analysis-choices.md` §1                  | Kroeger 1993 chs. 2–3.                          |
| Objecthood diagnostics                 | `docs/analysis-choices.md` §1                  | Kroeger 1993 chs. 2–3.                          |
| OBJ-uniform analysis (ng-non-pivot → OBJ) | `src/tgllfg/cfg/grammar.py`                 | Kroeger 1993 ch. 2; vs. older OBL-AG analysis (Schachter & Otanes 1972 ch. 5). |
| `mang-` distributive paradigm          | `data/tgl/paradigms.yaml`                      | Kroeger 1993 §4.4.                              |
| `maka-` abilitative                    | `data/tgl/paradigms.yaml`                      | Kroeger 1993 §4.5.                              |
| `ma-` non-volitional / stative         | `data/tgl/paradigms.yaml`                      | Schachter & Otanes 1972 §5.27; Kroeger 1993 §4.5. |
| Affix-class membership per verb        | `data/tgl/verbs.yaml`                          | Ramos & Bautista 1986 (per-verb index).         |
| Verb paradigm tables                   | `tests/tgllfg/test_morph_paradigms.py`         | Ramos & Bautista 1986; Schachter & Otanes 1972 ch. 5. |
| Ang-NP as pivot / SUBJ                 | `src/tgllfg/cfg/grammar.py`                    | Kroeger 1993 chs. 2–3.                          |
| Voice-alias mapping (S&O ↔ Kroeger)    | `data/tgl/voice_aliases.yaml`                  | Kroeger 1993 §1.3 (reduction); Schachter & Otanes 1972 §§5.20–5.30 (focus inventory). |
| Wackernagel 2P clitic placement        | `src/tgllfg/clitics/` (Phase 4 §7.3)           | Wackernagel 1892; Schachter & Otanes 1972 ch. 6; Kroeger 1993 §3.2. |
| *Ay*-inversion / topicalization        | `src/tgllfg/cfg/grammar.py` (Phase 4 §7.4)     | Schachter & Otanes 1972 §6.5; Kroeger 1993 §3.6. |
| SUBJ-only relativization               | `src/tgllfg/cfg/grammar.py` (Phase 4 §7.5)     | Kroeger 1993 ch. 5; Bresnan 2001 ch. 5.         |
| Equi / functional control              | `src/tgllfg/cfg/grammar.py` (Phase 4 §7.6)     | Bresnan 1982 ("Control and Complementation"); Kroeger 1993 §6.1. |
| Subject-to-subject raising             | `src/tgllfg/cfg/grammar.py` (Phase 4 §7.6)     | Bresnan 2001 ch. 12; Kroeger 1993 §6.2.         |
| `pa-` causative                        | `src/tgllfg/cfg/grammar.py` (Phase 4 §7.7)     | Schachter & Otanes 1972 §5.30; Kroeger 1993 §4.5. |

### Database / engineering

| Component                              | Where                                          | Reference(s)                                    |
|----------------------------------------|------------------------------------------------|-------------------------------------------------|
| Alembic migration framework            | `alembic/`                                     | Alembic documentation; SQLAlchemy 2.x docs.     |
| Trigram indexing for fuzzy lemma lookup | `alembic/versions/0001_baseline.py`           | PostgreSQL `pg_trgm` extension docs.            |
| Full-text search via `tsvector`        | `alembic/versions/0001_baseline.py`            | PostgreSQL FTS docs.                            |
| UUID v4 PK generation                  | `alembic/versions/0001_baseline.py`            | PostgreSQL `pgcrypto.gen_random_uuid()` docs.   |
| Async SQLAlchemy + asyncpg             | `src/tgllfg/lex/`                              | SQLAlchemy 2.x async docs; asyncpg docs.        |
| Testcontainers-based test isolation    | `tests/tgllfg/conftest.py`                     | testcontainers-python docs.                     |
| Property-based testing                 | various test files                             | Hypothesis docs.                                |

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
- **Earley 1970.** Earley, Jay. 1970. "An Efficient Context-Free Parsing
  Algorithm." *Communications of the ACM* 13(2): 94–102.
- **Galler & Fischer 1964.** Galler, Bernard A. and Michael J. Fischer. 1964.
  "An Improved Equivalence Algorithm." *Communications of the ACM* 7(5):
  301–303.
- **Kaplan & Bresnan 1982.** Kaplan, Ronald M. and Joan Bresnan. 1982.
  "Lexical-Functional Grammar: A Formal System for Grammatical
  Representation." In Bresnan 1982: 173–281.
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
  staged under `data/tgl/dictionaries/`, gitignored.)
- **Ramos & Bautista 1986.** Ramos, Teresita V. and Maria Lourdes
  Bautista. 1986. *Handbook of Tagalog Verbs: Inflections, Modes, and
  Aspects*. University of Hawaii Press. (User holds a purchased
  electronic copy under `data/tgl/dictionaries/`, gitignored. Cited
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
