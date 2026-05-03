# Diagnostics

Linguistic diagnostics that drive the analytical decisions
recorded in `docs/analysis-choices.md`. That doc records the
*decisions*; this one records the *evidence* — the example
sentences that pass or fail, the references cited, and the
parser's current handling.

This is a v0 draft (Phase 5f prep). It covers four areas where
diagnostics are load-bearing for current or imminent analytical
choices: subjecthood, objecthood, `sa`-NP argumenthood, and
control vs raising. As Phase 5g–5m add adjectives, comparison,
existentials, and indefinites, this doc grows section by section.

## References

- **Kroeger 1993** — Paul Kroeger, *Phrase Structure and
  Grammatical Relations in Tagalog*. CSLI Publications.
  Chapters 2–3 are the source for subjecthood / objecthood
  diagnostics; chapter 5 for relativization.
- **S&O 1972** — Paul Schachter and Fe Otanes, *Tagalog
  Reference Grammar*. University of California Press.
- **R&B 1986** — Teresita Ramos and Maria Lourdes Bautista,
  *Handbook of Tagalog Verbs*. University of Hawaii Press.
- **R&G 1981** — Teresita Ramos and Rosalina Goulet,
  *Intermediate Tagalog: Developing Cultural Awareness Through
  Language*. University Press of Hawaii.

## 1. Subjecthood

The pivot of a Tagalog clause — the NP marked with `ang` /
`si` (NOM case) — passes every standard subjecthood diagnostic.
The non-pivot `ng`-agent of a non-AV clause passes none of
them. This is the core evidence behind the project's case → GF
mapping: NOM → SUBJ, regardless of voice. (See
`analysis-choices.md` §1 for the decision and §66 for the
summary; this section gives the example sentences.)

### 1.1 Reflexive binding (Kroeger 1993 §2.2)

The reflexive `sarili niya` "his/her self" is bound by the
SUBJ — the `ang`-NP — across all voices. The non-pivot
`ng`-NP cannot bind a reflexive even when it is the agent.

- AV: `Nakita ng bata ang sarili niya sa salamin.`
  "The child saw himself in the mirror." Binder = `ang sarili
  niya` (SUBJ); the `ng bata` is OBJ-AGENT. The reading is
  available because the SUBJ is `sarili`, which corefers with
  the OBJ-AGENT possessor `niya`.
- OV: `Sinaktan ng bata ang sarili niya.` "The child hurt
  himself." Same pattern; the reflexive is the SUBJ pivot, the
  agent is the `ng`-NP.

The diagnostic is that the binder slot is always the pivot,
not the `ng`-NP — confirmed by the ungrammaticality of
constructions where the `ng`-NP is intended as the binder and
the `ang`-NP is the bound element.

**Parser status.** Reflexive binding is currently a docs-only
analysis. The `sarili` lex entry parses; the unifier does not
enforce the binding constraint. Phase 6 (FU) is the natural
point to add a constraining equation roughly of the form
`(↑ SUBJ INDEX) =c (↑ OBJ POSS INDEX)` once `INDEX` features
exist on PRON / NOUN heads.

### 1.2 Quantifier float (`lahat`)

The floated quantifier `lahat` "all" attaches to the SUBJ
across voices. Phase 4 §7.8 implements this as a wrap rule;
test coverage is in `tests/tgllfg/test_quantifier_float.py`.

- AV: `Lahat sila kumain.` "All of them ate." (`sila` SUBJ;
  `lahat` floats off it.)
- OV: `Lahat ng isda kinain ng bata.` Ungrammatical for the
  intended reading "the child ate all of the fish" — `lahat`
  cannot float off the `ng`-OBJ-AGENT. The grammatical form
  uses the partitive `lahat ng isda` as an NP-internal
  modifier.

### 1.3 Relativization (Kroeger 1993 ch. 5)

Only the SUBJ can be relativized in canonical AV / non-AV
clauses (the famous SUBJ-only constraint). The relativization
gap sits at the pivot position; voice morphology selects which
thematic role the pivot is.

- `ang batang kumain ng isda` "the child who ate fish" —
  AV, gap at SUBJ (the eater).
- `ang isdang kinain ng bata` "the fish that the child ate" —
  OV, gap at SUBJ (the eaten).
- `*ang batang kinain ng isda` would mean "the child that the
  fish ate" (intending `bata` as the OV agent) — ungrammatical
  for the intended reading because `bata` would be the
  `ng`-NP, not the pivot.

Phase 6 will lift the SUBJ-only restriction across nested
XCOMP / COMP via FU (§13.3); the SUBJ-only constraint stays
in force at the bottom of the path.

## 2. Objecthood: OBJ vs OBJ-θ vs OBL

The non-AV `ng`-agent is **OBJ-AGENT** (a typed OBJ), not
OBL-AG. See `analysis-choices.md` §1 for the rejection of
OBL-AG. The diagnostics here distinguish core arguments
(OBJ / OBJ-θ) from adjuncts.

### 2.1 The `ng`-agent is a core argument

The `ng`-agent of a non-AV clause cannot be omitted without
shifting the reading (it becomes an unspecified pro), and it
participates in voice alternation — the same role surfaces as
`ang` (SUBJ) in AV and as `ng` (OBJ-AGENT) in non-AV.

Compare:

- OV: `Kinain ng bata ang isda.` "The child ate the fish."
  Drop `ng bata` → `Kinain ang isda.` "The fish was eaten /
  someone ate the fish." The agent is silent but still
  present (an unspecified-actor reading), not absent.
- AV: `Kumain ang bata ng isda.` Same thematic structure;
  voice morphology promotes `bata` to SUBJ.

The pivot-alternation test is the cleanest: if an NP can be
the SUBJ in some voice of the same lex frame, it is a core
argument in every voice.

### 2.2 Word order

Core arguments hold fixed slots in the post-verbal cluster
(immediately after the verb in the canonical order; see Phase
4 §7.8). True obliques scramble more freely.

- `Kinain ng bata ang isda sa kusina.` — canonical V-OBJ-SUBJ-
  ADJUNCT.
- `Kinain ng bata sa kusina ang isda.` — marked but acceptable
  (locative scrambled forward).
- `*Kinain sa kusina ng bata ang isda.` — degraded: scrambling
  the locative ahead of the OBJ-AGENT is harder than scrambling
  it past the SUBJ.

Word-order rigidity is a weaker diagnostic than voice
alternation but corroborates it.

## 3. `sa`-NP: argument vs adjunct

The most fragile classification in the grammar. `sa` covers
locative, goal, recipient, beneficiary-ish, and possessor-ish
functions, and the same surface form may be either a core
argument (OBJ-θ under DV) or an adjunct (locative under AV /
OV / IV) depending on the lex frame and voice. The LMT
classifier (`src/tgllfg/lmt/classify.py`) defaults `sa`-NPs to
ADJUNCT and promotes them to typed obliques based on voice
morphology + lex SEM_CLASS. This is conservative — over-
attribution to ADJUNCT, no false rejection — and Phase 5j /
5l will tighten it with lex-frame-driven classification.

### 3.1 `sa`-NP as OBJ-θ (recipient / goal under DV)

The `sa`-NP of a DV clause is the recipient / goal **and** the
canonical pivot — i.e., it can also surface as the `ang`-NP
under DV voice morphology.

- DV (recipient as `sa`-NP): `Nagbigay ako ng libro sa bata.`
  "I gave a book to the child."
- DV (recipient as SUBJ): `Binigyan ko ng libro ang bata.`
  Same role, same lex frame; voice morphology promotes the
  recipient to pivot.

Because `bata` can be the SUBJ in some voice of `bigay`,
`sa bata` in the non-DV form is OBJ-θ (recipient), not
ADJUNCT. The lex frame of `bigay` "give" subcategorizes for
a recipient slot; the `sa`-NP fills it.

### 3.2 `sa`-NP as ADJUNCT (locative under AV / OV)

When the `sa`-NP is a true locative — a free modifier the lex
frame does not subcategorize for — it is an ADJUNCT. The
pivot-alternation test fails:

- `Kumain ang bata sa kusina.` "The child ate in the kitchen."
  `sa kusina` is freely droppable: `Kumain ang bata.` is
  fully grammatical with no semantic loss.
- There is no DV form `*Kainin sa kusina ang isda` for "eat
  the fish in the kitchen" — the locative is not a core
  argument of `kain` "eat" and cannot be promoted to pivot.

### 3.3 The classifier's role and Phase 5j/5l direction

The current classifier uses (a) voice morphology and (b) the
`sa`-NP's `SEM_CLASS` feature (`PLACE`, `ANIMATE`, …) to
default-classify. Phase 5j / 5l should add lex-frame-driven
classification: verbs like `bigay`, `bili`, `pakita` carry an
explicit `<RECIPIENT>` slot in their lex frame, and the
classifier promotes the `sa`-NP to OBJ-θ when that slot is
present.

A negative-fixture discipline applies: AV clauses with
`sa`-recipients should not parse with the recipient as ADJUNCT
when the lex frame demands OBJ-θ. Add `*` fixtures showing
the under-classification when the new lex-frame logic lands.

## 4. Control vs raising

Both subject-control (verbs like `gusto` "want") and raising
(verbs like `tila` "seem") yield surface `V V NP` with the
upper V's apparent subject being the lower V's subject. The
linguistically meaningful distinction is **whether the upper
verb assigns a thematic role to its surface subject**.

### 4.1 Subject-control: thematic role on the upper verb

The control verb assigns a thematic role to its SUBJ; the
SUBJ is also the SUBJ of the embedded XCOMP (Phase 5c §7.6
control / linker-XCOMP machinery).

- `Gusto kong kumain ng isda.` "I want to eat the fish."
  `ko` is the experiencer of `gusto` AND the agent of
  `kumain`. Both roles are thematic; structure-sharing is
  between two thematically-active SUBJ slots.

Diagnostic: replace the SUBJ with a non-thematic placeholder.
For control verbs this should be ungrammatical or strongly
marked. Tagalog has no productive expletive subjects, so the
diagnostic runs through the SUBJ-less form: `Gusto-ng
umulan` "wanting to rain" is at best marginal — `gusto`
demands an experiencer SUBJ. (Phase 5c §7.6 test corpus
confirms via the control test fixtures.)

### 4.2 Raising: no thematic role on the upper verb

The raising verb does not assign a thematic role to its SUBJ;
the SUBJ is purely a syntactic placeholder for the embedded
clause's SUBJ (Phase 5d Commit 7).

- `Tila siya kumain ng isda.` "He seems to have eaten the
  fish." `siya` is the agent of `kumain`; `tila` does not
  assign a role to `siya`. The semantic content of `tila` is
  the proposition.

Diagnostic: weather / propositional subjects survive raising.
`Tila-ng umulan` "it seems to be raining" is fully
grammatical — the SUBJ slot of `tila` is theta-empty.

### 4.3 Idiom-chunk preservation (deferred)

The classic English diagnostic is idiom-chunk preservation:
`the cat is out of the bag` (idiom) survives raising
(`the cat seems to be out of the bag`) but not control
(`*the cat wants to be out of the bag`). Phase 5d Commit 7
deferred this for Tagalog because the idiom inventory in
standard reference grammars is too small to give a clean test
bed. Mark as TBD; revisit when corpus-driven idiom inventory
exists.

## 5. Open / future diagnostics

Diagnostics that are not yet enforced by the parser but should
be added as the relevant phases land. Each entry is a hook
for a future implementation commit.

- **Pivot-alternation test for `sa`-NP** (Phase 5j / 5l).
  Parse the AV form and the DV form of the same lex frame;
  compare the GF assignment of the `sa`-NP. Currently a
  manual check; should become an automated diagnostic helper
  in `tests/tgllfg/diagnostics/`.
- **Reflexive binding** (Phase 6). The `sarili` reflexive's
  binding domain is currently docs-only. Phase 6 FU is the
  natural point to add a binding equation; until then,
  reflexive sentences parse but the binding is not checked.
- **Floated-quantifier number agreement** (Phase 5g+). `lahat`
  floats to the SUBJ, but the floated Q's interpretation
  should also enforce that the SUBJ's `NUM` features are
  PL / collective. Currently the float lifts; the agreement
  is implicit.
- **Adjective class — paradigm-absence diagnostic** (Phase 5g).
  The analytical commitment in plan §12.1 is `POS=ADJ +
  [PREDICATIVE+]`. The diagnostic for the commitment is the
  morphological-paradigm absence: if `ma-` adjectives were
  stative VERBs they would inflect for aspect
  (`*pumagmaganda`), voice (`*magagaganda`), and mood
  (`*magpamaganda`) — they don't. Add a negative-fixture test
  in Phase 5g asserting these forms do not parse as VERB
  analyses.
- **Existential clause-typing** (Phase 5j). Plan §12.4
  commits `may` / `wala` / `nasa` to a separate
  `S_EXISTENTIAL` clause-type family rather than the V-headed
  S frame. The diagnostic: existentials lack voice morphology
  (`*nag-may`, `*may-in`, `*may-an`) — they cannot enter the
  voice paradigm. Add a negative-fixture test in Phase 5j.
- **Idiom-chunk preservation for raising** (deferred until
  corpus-driven idiom inventory). See §4.3.
