# Analytical decisions

This file records non-trivial linguistic decisions baked into the
grammar and lexicon, with citations and reasoning. Each entry has a
date, a short statement of the decision, the diagnostics that
support it, and the alternatives considered.

## *ng*-non-pivot in transitive non-AV → typed OBJ-θ

**Date:** 2026-04-28 (Phase 4); refined 2026-05-01 (Phase 5b).
**Status:** active.

In transitive non-Actor-Voice clauses (Objective Voice, Dative Voice,
Instrumental Voice), the *ang*-NP is the pivot and unconditionally
maps to SUBJ (Kroeger 1993, ch. 2). The remaining core argument —
the *ng*-marked non-pivot — is analysed as a **core OBJ**, not as
an oblique agent (OBL-AG). This applies symmetrically across the
non-AV voices even though the role realised by the *ng*-NP varies
(agent in OV / DV / IV-CONVEY / IV-BEN, causer in pa-OV-direct).

**Phase 5b refinement: typed OBJ-θ in the grammar.** Phase 4
emitted the binding as bare `OBJ`; Phase 5 added a typed `OBJ-θ`
prediction at the LMT engine layer (e.g., `OBJ-AGENT` for OV's
demoted agent, `OBJ-CAUSER` for pa-OV-direct's demoted causer).
The Phase 4 grammar was updated in Phase 5b to emit the typed
form directly (`(↑ OBJ-AGENT) = ↓N` rather than `(↑ OBJ) = ↓N`),
eliminating the informational `lmt-mismatch` that Phase 5 surfaced
on every non-AV transitive parse. AV transitives keep bare `OBJ`
because PATIENT/THEME `[-r, +o]` maps to bare `OBJ` in the BK
truth table.

### Rationale

Three independent lines of evidence support OBJ over OBL-AG.

**1. Subjecthood is monolithic.** Kroeger's central argument
(1993, chs. 2–3) is that subjecthood diagnostics — reflexive binding,
controller of equi, quantifier float, raising, possessor extraction
— pick out the *ang*-NP and only the *ang*-NP, regardless of voice.
This is incompatible with the older "passive" analysis on which
non-AV clauses would have an underlying agent SUBJ that gets
demoted to oblique in surface; if that were correct, agent-oriented
diagnostics would target the *ng*-NP in OV. They do not. The
*ang*-NP is uniformly the SUBJ, so the *ng*-NP is uniformly
*not* the SUBJ.

**2. The *ng*-NP behaves like a core argument, not an oblique.** It
participates in voice alternations (its role is what voice
morphology selects); it shows fixed positional behaviour relative
to the verb in the post-verbal cluster (unlike *sa*-marked
obliques, which float more freely); it can host secondary
predication. Obliques in Tagalog are typically *sa*-marked
(locatives, recipients, benefactives) and pattern differently on
all three counts.

**3. The analysis composes with LMT.** Bresnan–Kanerva-style
Lexical Mapping Theory expects each core argument to map to one of
SUBJ, OBJ, OBJ-θ. Under the OBL-AG analysis, transitive OV would
have arguments mapping to {SUBJ, OBL-AG} and no OBJ — leaving the
PRED template `EAT <SUBJ, OBJ>` either inconsistent with the
mapping (a coherence violation) or requiring two PRED templates
per voice, which the data does not motivate. Under the OBJ
analysis, transitive OV maps cleanly to {SUBJ, OBJ}, and the PRED
template stays voice-invariant.

### Subjecthood and objecthood diagnostics (summary)

The fuller diagnostic table belongs in a future
`docs/diagnostics.md`; this section lists the data-points that drive
the SUBJ / OBJ assignment.

**Subjecthood (selects the *ang*-NP):**

- Reflexive binding: only the *ang*-NP can antecede a reflexive.
- Equi (control): the missing argument of an XCOMP is identified
  with the matrix *ang*-NP, regardless of voice.
- Quantifier float: floated quantifiers attach to the *ang*-NP.
- Relativization: only the *ang*-NP can be relativized (the famous
  SUBJ-only constraint, Kroeger 1993 ch. 5).
- Raising: subject-to-subject raising verbs (*mukha*, *baka*) raise
  the embedded *ang*-NP into the matrix *ang*-NP slot.
- Possessor extraction: the possessor of the *ang*-NP can be
  extracted; the possessor of the *ng*-NP cannot.

**Objecthood (selects the *ng*-non-pivot in transitive OV/DV/IV):**

- Voice alternation: the role realised by the *ng*-NP is exactly
  the role the voice affix demotes from pivot status. This is what
  voice alternation means; it picks out a core argument.
- Secondary predication: depictive secondary predicates can target
  the *ng*-NP under controlled conditions, paralleling object
  control behaviour in English.
- Word order: the *ng*-NP holds a fixed slot in the post-verbal
  cluster, immediately after the verb in the canonical order; true
  obliques scramble.

### Alternatives considered

- **OBL-AG (the older "passive analysis").** Rejected for the
  reasons in §1 above — Kroeger's evidence against treating non-AV
  as a passive is direct and overwhelming. Earlier drafts of this
  grammar carried an OBL-AG analysis as a placeholder; this entry
  records its retirement.

- **Per-voice GF assignment** (e.g. OBJ in OV, OBJ-θ in DV, OBL in
  IV). Rejected because the diagnostics in §2 are uniform across
  the non-AV voices: there is no syntactic correlate of the role
  difference. The role is a thematic property captured in
  a-structure, not a c-/f-structure property.

- **No core argument; *ng*-NP as adjunct.** Rejected because of the
  voice-alternation evidence: a phrase whose presence and
  realisation are governed by voice morphology is by definition
  not an adjunct.

### Open follow-ups

- Phase 4 needs to extend this to **DV** (Dative Voice / `i-` ?
  no — `-an`) and **IV** (Instrumental Voice / `i-`). The grammar
  rules are not yet written.
- A few post-2000 LFG-Tagalog references (Manueli; Mercado) bear
  on the OBJ-θ vs OBJ question for DV and IV specifically. To be
  added to the citations once the literature review for those
  voices completes.

### Citations

- Kroeger, Paul. 1993. *Phrase Structure and Grammatical Relations
  in Tagalog*. CSLI Publications. Chapters 2–3 (subjecthood,
  objecthood diagnostics) and chapter 5 (relativization).
- Schachter, Paul and Fe Otanes. 1972. *Tagalog Reference Grammar*.
  University of California Press. Surface morphology and the
  finer-grained "focus" labels (AF / GF / LF / BF / IF / RF / CF)
  that the `voice_alias` table maps onto Kroeger's four-voice
  system.
- Bresnan, Joan. 2001. *Lexical-Functional Syntax*. Blackwell.
  Background on LMT and the SUBJ/OBJ/OBJ-θ inventory.

## Phase 2 morphology scope and limitations

**Date:** 2026-04-28. **Status:** Phase 2C complete (2026-04-30).

The Phase 2 rule-cascade morphology engine
(`src/tgllfg/morph/`) covers AV / OV / DV / IV across PFV / IPFV /
CTPL plus the AV variants in `mag-`, `mang-` (with nasal
substitution), `maka-` (abilitative, `MOOD: ABIL`), and `ma-`
(non-volitional, `MOOD: NVOL`). After the three-commit Phase 2C
scale-up, the seed under `data/tgl/` covers **200 verb roots and
148 nouns** with **645 paired surface↔analysis assertions** in
`tests/tgllfg/test_morph_paradigms.py`. Plan §5.4's target of 200
verbs / 150 nouns / 500 assertions is met (nouns 2 short of 150 —
within acceptable margin).

### Phase 2C: phonological rules added

The five rules previously documented as "not modelled" were
implemented in Phase 2C (commit on `feature/phase-2c-morph-scaleup`).
They appear in either the engine's automatic pipeline or as per-root
opt-in flags:

1. **Stem-vowel raising** `o → u` on suffixation. Automatic. The
   final-syllable /o/ in the stem raises to /u/ when a suffix is
   attached: `inom + -in → inumin`; `putol + -in → putulin`.
2. **/d/ → /r/ intervocalic alternation**. Per-root opt-in via
   `sandhi_flags: [d_to_r]`. Applied as a post-processor after all
   operations: `dating + cv-redup → darating`; `bayad + -an →
   bayaran`. Roots currently flagged: `dating`, `lakad`, `bayad`.
3. **High-vowel deletion variant** of suffixation. Per-root opt-in
   via `sandhi_flags: [high_vowel_deletion]`. When set, a
   high-vowel-final stem deletes its final vowel rather than taking
   the formal h-epenthesis: `bili + -in → bilhin`. Default is the
   formal h-epenthesis form.
4. **Sonorant-initial -in- → ni-** prefix variant. Automatic. When
   the realis `-in-` infix targets a base beginning with a sonorant
   (m, n, ng-as-/ŋ/, l, r, w, y, h), it surfaces as the `ni-` prefix:
   `linis + OV PFV → nilinis` (rather than `linilis`).
5. **`ma-` non-volitional / stative class** (`MOOD: NVOL`). New
   `affix_class: ma` paradigm cells: `tulog → natulog / natutulog
   / matutulog`. Distinct from `maka-` abilitative (`MOOD: ABIL`).

These rules are also threaded through the Phase 3 DB-backed loader:
migration 0003 adds `lemma.sandhi_flags JSONB` and the seed +
adapter round-trip the flags so the DB-backend analyzer behaves
identically to the YAML-backend one.

### Affix-class lexicon convention

Each verb root carries an `affix_class` list listing the paradigm
patterns it participates in (`um`, `mag`, `mang`, `maka`,
`in_oblig`, `an_oblig`, `i_oblig`). Generation only fires for cells
whose `affix_class` is in the root's list, so a `-um-` only verb
does not produce ungrammatical `mag-` or `mang-` forms. R&B 1986's
back-of-book index summarises each verb's affix-class membership
(e.g. `eat káin (-um-/ -in/ -an) 126`), and the seed encodes these
directly. Where R&B records additional classes the engine doesn't
yet support (`ipag-`, `ipang-`, `magpa-`, `ika-`, `magka-`,
`pag- -an`, `ma-`, `maki-`, `magsi-`), the unsupported entries are
omitted from `affix_class` with a comment in `verbs.yaml` flagging
the gap.

### Citation policy

Per-verb citations live as YAML comments in `data/tgl/verbs.yaml`
referencing R&B 1986 page numbers. The Ramos 1971 dictionary OCR
and the R&B 1986 PDF live under `data/tgl/references/`
(gitignored) for grep-verification during seed authoring; the
binaries are not redistributed. Schachter & Otanes 1972 and Kroeger
1993 are cited by section number in commit messages.

## Phase 3 schema deviations from plan §6.2

**Date:** 2026-04-29. **Status:** active.

The Phase 3 lexicon schema (Alembic migrations 0001 + 0002) follows
plan §6.2 verbatim for all 13 originally-listed tables. Two
deviations were introduced in migration 0002 to host data the seed
YAML carries but §6.2 doesn't have a slot for:

1. **`lemma.transitivity` (TEXT) and `lemma.affix_class` (JSONB).**
   Per-root lexical properties read by the analyzer (TR/INTR; the
   list of paradigm patterns the root participates in: um, mag,
   mang, maka, in_oblig, an_oblig, i_oblig). §6.2 documents these
   as living in `lex_entry.morph_constraints`, but `lex_entry` also
   requires `pred_template` / `a_structure` / `intrinsic_classification`
   which are properly authored LFG predicates (Phase 4+). Putting
   transitivity and affix_class on `lemma` keeps `lex_entry`
   reserved for predicates that have actually been worked out.

2. **`paradigm_cell` table.** §6.2's `paradigm` /
   `paradigm_slot` / `affix` triple describes affix inventories
   abstractly (one slot fills with one affix per position). The
   seed YAML `paradigms.yaml` describes paradigm cells
   *operationally* — an ordered list of CV-redup / infix / suffix /
   prefix / nasal-substitute operations per
   (voice, aspect, mood, transitivity, affix_class) cell. Those are
   at different levels of description and don't reduce to each
   other, so they coexist: §6.2's tables for the abstract view (used
   later for richer LFG morphology), `paradigm_cell` for the
   operational view the analyzer actually executes.

Plan §6.2 explicitly notes "Names below are illustrative; finalized
in migration." These deviations are within that latitude.

## Phase 4 §7.1: voice and case extensions

**Date:** 2026-04-30. **Status:** active.

Phase 4 generalises the OBJ analysis of §1 (originally written up
for OV transitives) to all four Kroeger voices, and lays the
secondary-feature inventory (`APPL`, `CAUS`) the §7.7 applicatives
and causatives commit will populate.

### Grammar shape

The Phase 4 grammar is V-initial and **flat**: `S → V (NP)*`. There
is no VP intermediate node. Sentential rules vary by:

- the verb's voice (`AV` / `OV` / `DV` / `IV`);
- the case of each post-verbal NP (`NOM` / `GEN` / `DAT`);
- the order of `NP[NOM]` and `NP[GEN]` (Tagalog freely permits either).

Case-to-GF mapping is **uniform across voices**: NOM → SUBJ, GEN →
OBJ, DAT → ADJUNCT (as a non-governable set member). The voice
feature percolates from the verb but does not affect the case-to-GF
mapping at the c-structure level — voice's syntactic effect lives in
which thematic role the pivot bears, which is encoded in the
lex_entry's role-to-GF mapping (Phase 5 LMT will compute this from
intrinsic classification + voice).

### OBJ-uniform extended to DV / IV

The §1 analysis (ng-non-pivot in transitive non-AV → OBJ) is
extended verbatim to DV and IV. In a DV transitive
(`Sinulatan ng bata ang ina`), the pivot recipient is SUBJ and the
ng-NP agent is OBJ. In an IV transitive
(`Isinulat ng bata ang liham`), the pivot conveyed is SUBJ and the
ng-NP agent is OBJ. The §1 diagnostics (subjecthood is monolithic;
ng-NP behaves like a core argument; the analysis composes with LMT)
hold uniformly across the four voices.

**Outstanding lit review:** Manueli; Mercado bear specifically on
the OBJ-θ vs OBJ question for DV and IV (whether the ng-non-pivot
should be typed as a thematic-OBJ — OBJ-GOAL, OBJ-CONVEYED — or as
a bare OBJ). The Phase 4 implementation commits to the bare-OBJ
analysis; this can be revisited if the lit review motivates a
typed-OBJ analysis. The grammar's `(↑ OBJ) = ↓N` equation is
trivially upgradable to `(↑ OBJ-θ) = ↓N` once the typing decision
is made.

### Sa-NPs: ADJUNCT for now, OBL-X under Phase 5 LMT

`sa`-marked NPs (`NP[CASE=DAT]`) are attached as members of the
matrix f-structure's `ADJUNCT` set. Phase 4 does **not** classify
them as `OBL-LOC`, `OBL-GOAL`, or `OBL-BEN` — the classification
depends on the verb's argument structure and is properly an LMT
concern. Phase 5 will reclassify ADJUNCT members as typed OBL-X
based on the verb's intrinsic classification. The well-formedness
check treats ADJUNCT as non-governable, so this punt does not
introduce false-positive coherence failures.

### APPL / CAUS feature inventory

Phase 4 §7.1 fixes the secondary-feature inventory:

- `APPL ∈ {INSTR, BEN, REASON, CONVEY, ∅}` — applicative type.
- `CAUS ∈ {DIRECT, INDIRECT, ∅}` — `pa-` causative variants.

No Phase 4 grammar rule consumes these yet; lexical entries may
carry them, and §7.7 (applicatives & causatives) will introduce the
rules that route them through the f-structure.

### Voice alias seed

The §6.2 `voice_alias` table is seeded from
`data/tgl/voice_aliases.yaml` with the Schachter-Otanes ↔ Kroeger
mapping (AF→AV, GF/PF→OV, LF/DF→DV, BF→IV+BEN, IF→IV+INSTR,
RF→IV+REASON, CF→AV+CAUS=DIRECT). The CF entry is partial: the
biclausal indirect-causative frame is captured as XCOMP (Phase 4
§7.6) rather than a single (VOICE, APPL, CAUS) triple.

## Phase 4 §7.2: aspect, mood, polarity

**Date:** 2026-04-30. **Status:** active.

### Aspect inventory expanded to {PFV, IPFV, CTPL, RECPFV}

The recent-perfective ("just-completed") aspect is added to the
inventory. Morphology is uniform across affix classes: ``ka-`` +
CV-reduplication of the root, no infix or voice suffix.

- AV-um: ``kakakain`` (just ate), ``kabibili`` (just bought).
- AV-mag: ``kasusulat``, ``kalilinis``.
- AV-ma: ``katutulog`` (just fell asleep).

`RECPFV` cells exist for the three productive AV affix-classes (um,
mag, ma). Non-AV RECPFV is rare in modern Tagalog and is deferred to
a Phase 5 / scale-up commit.

Citations: Schachter & Otanes 1972 §5.31; Ramos & Bautista 1986
paradigm tables (RECPFV column).

### Mood inventory expanded to {IND, IMP, ABIL, NVOL, SOC}

`IND`, `ABIL`, and `NVOL` are already populated by Phase 2C
morphology (default IND, abilitative `maka-`, non-volitional `ma-`).
Phase 4 §7.2 adds `IMP` (imperative) and `SOC` (social) as
recognised values; their morphological / particle triggers are
partial in this commit:

- `IMP` is borne by the `huwag` particle's f-structure (lex feats
  POLARITY=NEG, MOOD=IMP) but is **not** lifted to the matrix MOOD
  in this commit (see "Phase 4 §7.2 limitation" below).
- `SOC` requires §7.3 clitics (the social `tayo` 1pl-incl pivot)
  and is left as inventory only.

### Polarity from `hindi` and `huwag`

Clausal negation is added with a single grammar rule:

```text
S → PART[POLARITY=NEG] S
   (↑) = ↓2
   (↑ POLARITY) = 'NEG'
```

The matrix S inherits the inner clause's f-structure wholesale and
overlays POLARITY=NEG. Both `hindi` (declarative-negation, just
POLARITY=NEG) and `huwag` (imperative-negation, POLARITY=NEG +
MOOD=IMP on the particle) match this rule. POLARITY=NEG appears at
the top of the matrix f-structure, above any per-voice projections.

**Phase 4 §7.2 limitation: huwag's MOOD=IMP is not lifted to
matrix.** The full-inheritance equation `(↑) = ↓2` propagates the
inner verb's MOOD=IND to the matrix, and overlaying MOOD=IMP from
the particle would clash with that IND. Resolving the clash
requires either (a) selectively projecting individual GFs from the
inner clause (which creates phantom OBJ slots for intransitive
inner clauses, tripping coherence) or (b) a richer feature
architecture distinguishing predicate-mood from clausal-mood. Both
are out of scope for §7.2; the imperative-mood lifting is
revisitable in §7.3 (clitics often co-occur with imperatives) or
§7.6 (control / raising). The huwag particle's own f-structure
does carry MOOD=IMP, accessible via the c-tree.

### Lexicon fallback for verbs not in the in-process BASE

Phase 4 introduces `_synthesize_verb_entry` in `src/tgllfg/lexicon.py`:
when the morph engine recognises a verb (any of the 200 seeded
roots) but no hand-authored entry exists in `BASE`, the lookup
synthesises a voice-aware default `LexicalEntry`. The synthesised
PRED is the lemma in upper case; argument-structure and GF defaults
match `lmt.apply_lmt`'s per-voice mapping. This avoids empty-PRED
f-structures for the 194 seeded verbs not in the Phase 4 anchor set
and keeps the well-formedness checks meaningful across the corpus.
The hand-authored anchor entries (kain, bili, basa, sulat, gawa,
tapon) take precedence; fallback applies only to lemmas absent from
`BASE`.

## Phase 4 §7.3: Wackernagel 2P clitic placement

**Date:** 2026-04-30. **Status:** active.

### Pre-parse reordering as the implementation strategy

Plan §7.3 specifies a pre-parse reordering pass that "exposes the
cluster as a constituent" so the parser sees a normalized order.
The Phase 4 implementation lives in `src/tgllfg/clitics/`, called
between morph analysis and lexicon lookup in
`src/tgllfg/pipeline.py:parse_text`.

### Two cluster destinations

The pass distinguishes two clitic groups:

1. **Pronominal clitics** (`PRON` with `is_clitic=True`): `ako`,
   `ka`, `ko`, `mo`, `niya`, ... Move to immediately after the
   verb. They appear in NP-argument slots through the existing
   `NP[CASE=X] → PRON[CASE=X]` shells; no new grammar rule.
2. **Adverbial enclitics** (`PART` with `clitic_class="2P"`):
   `na`, `pa`, `ba`, `daw`/`raw`, `din`/`rin`, `lang`, `nga`,
   `pala`, `kasi`, ... Move to the **end** of the clause. The
   grammar absorbs them via a recursive
   `S → S PART[CLITIC_CLASS=2P]` rule with `↓2 ∈ (↑ ADJ)`,
   placing each enclitic into the matrix's ADJ set as a
   sub-f-structure carrying its own feature contributions
   (ASPECT_PART, EVID, etc.).

The end-of-clause placement for adverbials is a c-structure
simplification — Wackernagel's 2P semantics (clitic IMMEDIATELY
after the host) is preserved at the *abstract* level by the
single-rule absorption (the cluster is a constituent of S), but
the concrete c-structure puts adverbs at clause-final position
because the recursive `S → S PART` rule is the simplest CFG
shape that admits arbitrary cluster size without combinatorial
rule explosion.

### Order within the cluster

`data/tgl/clitics.yaml` tabulates priorities for known
clitics, following Schachter & Otanes 1972 §6.7. Priorities are
integers, lower-sorts-first. Pronouns occupy priority < 100; the
adverbial cluster is 100-200, internally ordered as
`na < pa < ba < daw/raw < din/rin < lang < nga < pala < kasi <
man < yata`. Unknown surfaces sort after listed ones at
`DEFAULT_PRIORITY=999`.

### Filtering ambiguous-clitic analyses in the cluster

The morph analyzer can produce both clitic and non-clitic readings
for a homophonous surface (notably `na` as either the linker
particle or the aspectual enclitic; `daw` / `raw` are usually
unambiguous). Once a token is selected for cluster placement
(any analysis carries `is_clitic=True`), the placement pass
filters its candidates to only the clitic-flavored analyses. This
prevents the linker reading from riding into the cluster slot
through the grammar's non-conflict feature matcher and producing
a phantom parse with an empty ADJ entry.

### Boolean feats are placement-only

`is_clitic=True` is added to the morph analyzer's feature dict
as a boolean. Because the pipeline's lex-equation derivation only
emits string-valued feats as LFG equations (and the category-
pattern builder only carries string features), `is_clitic` is
invisible to the grammar — exactly what we want, since 2P
membership is a placement concern, not a category-feature concern.
The `clitic_class` field is exposed as `CLITIC_CLASS` (string) so
the grammar's adverbial-cluster rule can match
`PART[CLITIC_CLASS=2P]` while ignoring linker `PART` tokens.

### Out-of-scope for this commit

- No verb-host: verbless fragments fall through unchanged. The
  placement pass is verb-anchored.
- SOC mood (e.g. `magkape tayo`) requires the `tayo` 1pl-incl
  pronoun in pivot position with mag-class morphology. SOC stays
  inventory-only (Phase 4 §7.2) until §7.6 / §7.7 wire it up.
- Three-way clitic ambiguity (e.g. some pronouns can be NOM or
  GEN depending on context) is approximated by the morph
  analyzer's per-form indexing; `kita` (1sg-GEN + 2sg-NOM
  fusion) is left to a future commit.

## Phase 4 §7.4: ay-inversion

**Date:** 2026-04-30. **Status:** active.

### SUBJ-gapped inner clause (S_GAP)

Both ay-inversion and relativization (§7.5) need an inner clause
shape with the NOM-NP missing — the SUBJ slot becomes the gap that
the outer construction binds. We introduce a single ``S_GAP``
non-terminal whose rules duplicate the regular S frames except they
omit the NOM NP:

```text
S_GAP → V[VOICE=AV]                          (intransitive AV)
S_GAP → V NP[CASE=GEN]                       (transitive any voice)
S_GAP → V NP[CASE=GEN] NP[CASE=DAT]          (with DAT adjunct)
S_GAP → PART[POLARITY=NEG] S_GAP             (recursive negation)
```

Each frame binds its missing SUBJ to ``REL-PRO`` via
``(↑ SUBJ) = (↑ REL-PRO)``. ``S_GAP`` is never a top-level start
symbol, so a top-level S_GAP would have an unbound REL-PRO and fail
completeness — this is the structural mechanism keeping S_GAP
reachable only via wrap rules.

### Wrap rule and TOPIC binding

```text
S → NP[CASE=NOM] PART[LINK=AY] S_GAP
   (↑) = ↓3
   (↑ TOPIC) = ↓1
   (↓3 REL-PRO) = ↓1
   (↓3 REL-PRO) =c (↓3 SUBJ)
```

The matrix ``S`` shares its f-structure with the inner clause
(``(↑) = ↓3``) and overlays a TOPIC. The displaced NP fills the
inner clause's REL-PRO via full identity — no cycle here because
the inner clause IS the matrix and the head sits at TOPIC, not
inside an ADJ that reaches back. The constraining equation
``(↓3 REL-PRO) =c (↓3 SUBJ)`` is vacuous today (S_GAP has only
SUBJ-gapped frames) but pins SUBJ-only fronting structurally.

### Out-of-scope

- **Non-pivot ay-fronting**: ``Kanya ay binili ang aklat`` (a
  GEN-NP topic) and similar are deferred to §7.8. The §7.4 rule
  only takes ``NP[CASE=NOM]``.
- **AdvP / PP fronting**: ``Kahapon ay tumakbo si Maria``
  (temporal AdvP). Out of scope until the categorial inventory
  expands (§7.8).

## Phase 4 §7.5: relativization

**Date:** 2026-04-30. **Status:** active.

### Anaphoric REL-PRO (not full identity)

The canonical LFG analysis of relativization shares the head NP's
f-structure with the relative clause's REL-PRO via full identity:
``(↓3 REL-PRO) = ↓1``. Combined with the standard practice of
hanging the RC off the head's ADJ set
(``↓3 ∈ (↑ ADJ)``), this produces a **cyclic** f-structure: head
NP ⊇ ADJ ⊇ RC ⊇ REL-PRO = head NP. LFG formalism admits cyclic
f-structures (XLE supports them), but our unifier's occurs-check
rejects any unification that would create one.

Phase 4 §7.5 deviates from full identity in favour of **anaphoric
sharing**: the head NP's salient atomic features (``PRED``,
``CASE``) are copied onto REL-PRO via per-path equations. REL-PRO
is then a separate f-structure that *resembles* the head but isn't
identical to it.

```text
NP[CASE=X] → NP[CASE=X] PART[LINK=NA|NG] S_GAP
   (↑) = ↓1
   ↓3 ∈ (↑ ADJ)
   (↓3 REL-PRO PRED) = (↓1 PRED)
   (↓3 REL-PRO CASE) = (↓1 CASE)
   (↓3 REL-PRO) =c (↓3 SUBJ)
```

The RC's SUBJ is bound to REL-PRO inside ``S_GAP``, so SUBJ in the
RC inherits PRED/CASE from the head. The constraining equation
holds trivially today and rules out non-SUBJ S_GAP frames once they
arrive (e.g. for §7.6 long-distance binding via XCOMP).

This anaphoric move is reversible: when the unifier learns to
support cyclic f-structures (the canonical LFG convention), the
two path-equation copies can be replaced with a single
``(↓3 REL-PRO) = ↓1`` and the analysis becomes structure-sharing.
The constraint and the SUBJ-only restriction remain unchanged.

### Linker `na` / `-ng` allomorphy

Tagalog's linker is realised in two surface shapes:

- **Standalone ``na``** after consonant-final hosts:
  ``aklat na binasa``, ``bata na malaki``.
- **Bound ``-ng``** glued to vowel-final hosts:
  ``batang kumain``, ``librong binasa``, ``niyang kinain``.

The bound form is split off at pre-morph time by
:func:`tgllfg.text.split_linker_ng`, which emits a synthetic
``-ng`` token (using the surface ``-ng`` so the morph index hits
the dedicated linker entry rather than the standalone genitive
``ng``). The split is **informed by the morph index**: a
``Vng``-final surface that is itself a known full form (122
verb-class members like ``bumibilang``, ``darating``,
``katatanong``, ``ipinatong``, ...) is left intact; only when the
full surface is unknown AND the stem is a known noun / verb /
pronoun does the split fire. This also protects short closed-class
words like ``ang``: the stem ``a`` is unknown, so ``ang`` stays
intact.

### Homophone `na` disambiguation

Surface ``na`` is ambiguous between the linker (PART, ``LINK=NA``)
and the second-position aspectual enclitic (PART,
``CLITIC_CLASS=2P``, ``ASPECT_PART=ALREADY``). Both readings ride
into morph analysis, but Wackernagel placement (Phase 4 §7.3)
needs a single answer per token — placement moves clitics to the
cluster slot, while the linker stays put.

The disambiguator
:func:`tgllfg.clitics.disambiguate_homophone_clitics` runs first in
the placement pass and uses left-context:

- After ``NOUN``: drop clitic readings, keep the linker (e.g.
  ``aklat na ...``).
- After ``VERB`` / ``PRON``: drop the linker, keep the clitic
  (e.g. ``kumain na``, ``mo na``).
- Otherwise: leave both readings; the parser's grammar match
  resolves it.

The placement pass's existing cluster-slot filter (PRON/PART must
have ``is_clitic=True`` to ride a cluster slot) is preserved as a
second line of defence.

### SUBJ-only restriction

Tagalog's well-known SUBJ-only restriction on relativization
(Kroeger 1993) falls out structurally: ``S_GAP`` only admits frames
where the NOM-NP slot is missing — i.e., the gap is SUBJ. Attempts
to relativize a non-SUBJ argument (e.g.,
``*ang batang kinain ang isda`` to relativize the agent of OV) fail
at the parser level because the inner clause would contain a
NOM-NP, which no S_GAP rule admits.

The constraining equation ``(↓3 REL-PRO) =c (↓3 SUBJ)`` provides
a redundant check today and becomes load-bearing under §7.6
non-SUBJ gap shapes.

### Out-of-scope

- **Long-distance relativization** (``ang batang gusto kong
  makain``): requires XCOMP/COMP path traversal in the constraint
  ``(↑ REL-PRO) =c (↑ {COMP|XCOMP}* SUBJ)``. Functional
  uncertainty isn't yet supported by the unifier; defer to a later
  commit (§7.6 control & raising introduces XCOMP, but the FU
  machinery itself is its own follow-up).
- **Resumptive pronouns** in RCs (rare in modern Tagalog) and
  **headless / free relatives** (``ang kumain``).
- **Non-restrictive RCs** with intonational/orthographic separation.

## Phase 4 §7.6: control (raising deferred)

**Date:** 2026-04-30. **Status:** active.

### Three control patterns, one control equation

Three control verb classes are seeded; all three use SUBJ-control
over an XCOMP complement clause via the same equation
``(↑ SUBJ) = (↑ XCOMP REL-PRO)``. The classes differ only in
which case-marked NP fills the matrix SUBJ slot:

- **Psych** (``gusto`` "want", ``ayaw`` "dislike", ``kaya``
  "be able"): GEN-marked experiencer is matrix SUBJ. PRED carries
  ``<SUBJ, XCOMP>``. Uninflected pseudo-verbs.
- **Intransitive** (``payag`` → ``pumayag``): NOM-marked agent is
  matrix SUBJ; AV-only inflection. PRED ``AGREE <SUBJ, XCOMP>``.
- **Transitive** (``pilit`` → ``pinilit`` OV; ``utos`` →
  ``inutusan`` DV): NOM-marked pivot (forcee / orderee) is matrix
  SUBJ; GEN-marked agent is matrix OBJ. PRED ``FORCE <SUBJ, OBJ,
  XCOMP>``. The pivot, not the agent, controls the embedded gap —
  this is the canonical Tagalog control pattern under the
  OBJ-uniform analysis.

### Psych predicates take GEN-marked SUBJ

``gusto``-class predicates take a GEN-marked experiencer that
fills the matrix SUBJ slot — a deviation from the otherwise-uniform
NOM→SUBJ mapping. Alternative encodings were considered:

- **Clausal SUBJ** (matrix SUBJ = the embedded clause; experiencer
  is OBJ): conflicts with the LFG Subject Condition under our
  current PRED-template + completeness machinery. Workable in
  principle but requires the matrix SUBJ to be a non-thematic
  pointer to XCOMP, which our well-formedness checker would have
  to special-case.
- **Subject Condition exemption** for psych predicates: deviates
  from the LFG checker's uniform behavior, harder to debug.
- **GEN-as-SUBJ deviation**: small, lexicalized, well-attested
  in the Tagalog literature (Kroeger 1993 argues the GEN
  experiencer of psych predicates passes subjecthood diagnostics).
  Picked.

The deviation is one verb class wide and gated by the
``CTRL_CLASS=PSYCH`` lex feature — non-psych predicates retain
the uniform NOM→SUBJ mapping.

### S_XCOMP: AV-restricted SUBJ-gapped clause

The control complement is parsed by a new non-terminal
``S_XCOMP`` whose frames mirror ``S_GAP`` (§7.4 / §7.5) but with
the verb fixed to ``V[VOICE=AV]``. The voice restriction encodes
Tagalog's canonical "controlled = actor → AV pivot" pattern:
under AV the actor is the SUBJ, so binding the gap to REL-PRO
(= matrix's controller) targets the actor.

OV / DV control complements (where the controller binds the
embedded agent / OBJ) — e.g. ``Gusto kong kainin ang isda`` "I
want the fish to be eaten" — are grammatical Tagalog but require
non-SUBJ S_XCOMP frames + matching wrap-rule plumbing. Out of
scope for this commit; revisit when corpus pressure warrants.

### CTRL_CLASS as a discriminating category feature

Each control verb's class rides on its morph analysis as
``CTRL_CLASS ∈ {PSYCH, INTRANS, TRANS}``. The grammar's wrap rules
match ``V[CTRL_CLASS=PSYCH]`` etc. so the rule fires only on the
right verb class.

Because the parser's matcher is non-conflict (shared keys must
agree, missing keys don't conflict), non-control verbs would
**also** match ``V[CTRL_CLASS=PSYCH]`` if they had no CTRL_CLASS
feature at all. The morph analyzer therefore defaults
``CTRL_CLASS=NONE`` on every verb without an explicit value —
the sentinel value conflicts with PSYCH / INTRANS / TRANS at
rule-match time, ruling non-control verbs out structurally.

### Per-root ``feats`` on ``Root``

To carry ``CTRL_CLASS=INTRANS`` / ``TRANS`` on inflected control
verbs (``payag``, ``pilit``, ``utos``), a new
``feats: dict[str, object]`` field is added to
:class:`tgllfg.morph.paradigms.Root`. The analyzer copies these
per-root feats into every generated MorphAnalysis. Uninflected
pseudo-verbs (``gusto`` / ``ayaw`` / ``kaya``) live in
``particles.yaml`` because they have no verbal morphology to drive
the paradigm engine; their CTRL_CLASS comes from the existing
``Particle.feats`` field.

### No cycle — control is structure-sharing

Unlike §7.5 relativization (where head-NP-contains-RC creates a
cyclic f-structure under full identity, forcing the anaphoric
REL-PRO workaround), control's matrix and XCOMP are **sibling**
f-nodes. The shared SUBJ is referenced from both
``matrix.SUBJ`` and ``matrix.XCOMP.SUBJ`` but doesn't
structurally contain either parent — so the unifier's
occurs-check is satisfied. Full identity holds:
``matrix.SUBJ.id == matrix.XCOMP.SUBJ.id``.

### Raising deferred

Tagalog raising verbs (``mukha`` "seem", ``baka`` "might") are
out of scope:

- Lexical disambiguation: ``mukha`` is also a noun ("face");
  ``baka`` is also a noun ("cow"). Reliable disambiguation needs
  context features (clause-initial position, modal-like usage)
  that aren't yet wired up.
- Non-thematic SUBJ: raising verbs have a SUBJ slot that doesn't
  correspond to a thematic role. The PRED template format would
  need extension to mark such args (e.g. ``seem <XCOMP> SUBJ``
  with SUBJ outside the angle-brackets). The completeness checker
  would also need to know about non-thematic args.

Both pieces are tractable but additive — defer until the lex
infrastructure for non-thematic args is needed elsewhere.

**Update (Phase 5c):** lifted in Phase 5c §7.6 follow-on
Commit 5 (see the entry below).

### Out-of-scope (will revisit)

- **OV / DV control complements** (non-SUBJ-gap inside XCOMP).
  **Update (Phase 5c):** lifted in Phase 5c §7.6 follow-on (see
  the entry below).
- **Long-distance control** through nested XCOMP (functional
  uncertainty in the unifier). **Update (Phase 5c):** finite-depth
  nested control lifted in Phase 5c §7.6 follow-on Commit 3 (see
  the entry below) — finite chains don't need functional
  uncertainty, just explicit S_XCOMP variants where a control
  verb is itself the head.
- **Embedded-clause complementizer choice**: complement could be
  introduced by ``na`` instead of ``-ng`` after vowel-final
  pronoun hosts; the current implementation accepts both via the
  per-link wrap-rule pair, but we don't enforce a single canonical
  choice per construction.

## Phase 5c §7.6 follow-on: non-AV control complements

**Date:** 2026-04-30. **Status:** active. Phase 4 §7.6 restricted
``S_XCOMP`` to AV; the canonical "controlled = actor" pattern
trivially identifies the actor with SUBJ under AV. Phase 5c lifts
the restriction so the actor's *typed* GF (``OBJ-AGENT`` under
non-AV, per the Phase 5b OBJ-θ-in-grammar alignment) is the
gap-binding target.

### Three new ``S_XCOMP`` variants

```text
S_XCOMP → V[VOICE=OV, CAUS=NONE] NP[CASE=NOM]
   (↑ SUBJ) = ↓2
   (↑ OBJ-AGENT) = (↑ REL-PRO)

S_XCOMP → V[VOICE=DV] NP[CASE=NOM]
   (↑ SUBJ) = ↓2
   (↑ OBJ-AGENT) = (↑ REL-PRO)

S_XCOMP → V[VOICE=IV, APPL=CONVEY] NP[CASE=NOM]
   (↑ SUBJ) = ↓2
   (↑ OBJ-AGENT) = (↑ REL-PRO)
```

The matrix wrap rules don't change — ``(↑ SUBJ) = (↑ XCOMP REL-PRO)``
binds the matrix controller to the embedded REL-PRO regardless of
the embedded voice. Composing the two equations gives
``matrix.SUBJ = matrix.XCOMP.OBJ-AGENT`` for non-AV embedded
clauses, mirroring the AV identity ``matrix.SUBJ = matrix.XCOMP.SUBJ``.

### Why ``OBJ-AGENT`` is the controllee

In Tagalog non-AV clauses, the actor is realised as the GEN-marked
ng-non-pivot. Under Phase 5b's OBJ-θ-in-grammar alignment that
slot is typed ``OBJ-AGENT`` (verbs whose actor role is AGENT) or
``OBJ-CAUSER`` (verbs of direct causation). The embedded clauses
admitted by these new rules are non-causative non-AV verbs
(``CAUS=NONE`` / ``APPL=CONVEY``), so ``OBJ-AGENT`` is the right
target. ``OBJ-CAUSER`` for pa-OV embedded under control is a
narrower follow-on if ever wanted; deferred until corpus pressure
warrants it (the construction "I forced him to feed-cause the
child" is rare and cumbersome even in fluent speech).

### Aspect independence preserved

Embedded aspect is fully independent of matrix: PFV (``kinain``),
IPFV (``kinakain``), and CTPL (``kakainin``) all parse under
psych or transitive control. The CTPL form is the canonical
"infinitive-like" form in fluent speech (Schachter & Otanes 1972
§5.16); the current grammar admits all three.

### Inner negation composes

The recursive ``S_XCOMP → PART[POLARITY=NEG] S_XCOMP`` rule is
voice-agnostic, so ``Gusto kong hindi kakainin ang isda`` ("I
don't want to eat the fish") parses with the embedded OV clause
carrying ``POLARITY=NEG``.

### Phase 5b embedded-clause LMT check stays clean

The new construction surfaces no spurious ``lmt-mismatch``
diagnostics: the embedded lex entry's intrinsic profile (e.g.,
``EAT <SUBJ, OBJ-AGENT>`` for OV ``kain``) predicts ``{SUBJ,
OBJ-AGENT}``, and the grammar emits exactly that pair under the
new rules. Engine and grammar agree at every embedded level.

### Out-of-scope (still deferred)

- **pa-OV (CAUS=DIRECT) embedded under control** — would route
  REL-PRO to ``OBJ-CAUSER``. Rare and not exercised by corpus.
- **IV-BEN multi-GEN embedded under control** — interaction
  between control and Phase 5b multi-GEN frames. Two-GEN slots
  inside a controlled clause aren't seeded; deferred.
- **Embedded-clause complementizer choice** (``na`` vs ``-ng``):
  unchanged from Phase 4 §7.6.

## Phase 5c §7.6 follow-on: long-distance (nested) control

**Date:** 2026-05-01. **Status:** active. The Phase 4 §7.6
deferral list flagged "Long-distance control through nested
XCOMP" and tied it to "functional uncertainty in the unifier."
That framing was overcautious: *finite-depth* nested control —
chains where a control verb is the head of another control
verb's XCOMP — is a finite enumeration of grammar rules, not an
unbounded path expression. Phase 5c Commit 3 lifts the deferral
without touching the unifier.

### Six new ``S_XCOMP`` variants

Three control classes (PSYCH / INTRANS / TRANS), each with both
linker variants (NA / NG):

```text
S_XCOMP → V[CTRL_CLASS=PSYCH]  PART[LINK=…] S_XCOMP
S_XCOMP → V[CTRL_CLASS=INTRANS] PART[LINK=…] S_XCOMP
S_XCOMP → V[CTRL_CLASS=TRANS]   NP[CASE=GEN] PART[LINK=…] S_XCOMP
```

Each rule binds its own SUBJ to its own REL-PRO (the gap),
chains its XCOMP slot to the inner clause, and propagates the
controller from its SUBJ to the inner XCOMP's REL-PRO. Composing
these equations across depth N gives a single f-node shared
across SUBJ slots at every AV level. No functional uncertainty
is needed because the depth is fixed by the surface tokens.

The SUBJ-NP that the matrix wrap rules require (PSYCH's GEN
experiencer, INTRANS's NOM agent, TRANS's NOM forcee) is absent
when the verb is nested — that NP is the gap. The TRANS rule's
GEN-NP forcer remains overt because it's the controller, not
the controllee.

### Composition with Phase 5c Commit 1's non-AV embedded

When the innermost S_XCOMP is non-AV (Phase 5c Commit 1), the
embedded actor is OBJ-AGENT, not SUBJ. The nested control rules
keep chaining at SUBJ level until the OV / DV / IV variant is
reached; at that level the controller routes to OBJ-AGENT via
Commit 1's rules. Sentence:

```text
Gusto kong pumayag na kakainin ang isda.
```

f-structure chain: ``matrix.SUBJ === XCOMP.SUBJ ===
XCOMP.XCOMP.OBJ-AGENT``. The innermost SUBJ is the OV pivot
(``ang isda``, the patient) — a different f-node, distinct from
the chain-shared controller.

### Disambiguator extension for ``na`` after a control verb

The placement pass's ``disambiguate_homophone_clitics`` left-
context rule is extended: when ``na`` directly follows a verb
with ``CTRL_CLASS != NONE``, treat it as the linker (not the
aspectual ALREADY clitic). Without this, ``Gusto kong pumayag na
kumain`` would have ``na`` (after ``pumayag``, an INTRANS
control verb) read as the aspectual clitic and moved to clause-
end, stripping the linker and breaking the nested wrap rule.

The check generalises the existing rule for "PRON preceded by a
control verb" (`Kaya namin na kumain`, Phase 4 §7.10): both
patterns have a control verb in the immediate left context that
needs a linker for its XCOMP.

### Negation composes at any level

The recursive ``S_XCOMP → PART[POLARITY=NEG] S_XCOMP`` rule is
voice- and depth-agnostic, so negation works at the outer,
middle, or innermost level:

```text
Hindi gusto kong pumayag na kumain.   (outer NEG on matrix)
Gusto kong hindi pumayag na kumain.   (middle NEG on AGREE)
Gusto kong pumayag na hindi kumain.   (inner NEG on EAT)
```

### Phase 5b embedded-clause LMT walker descends to all levels

The recursive ``apply_lmt_with_check`` walker visits every
XCOMP/COMP that has its own PRED. With nested control producing
2-, 3-, and 4-deep chains, the walker now exercises depths it
couldn't reach before. All levels validate cleanly: each control
verb's intrinsic profile predicts ``{SUBJ, XCOMP}`` (PSYCH /
INTRANS) or ``{SUBJ, OBJ-AGENT, XCOMP}`` (TRANS), matching the
grammar's emitted GFs at every depth.

### Out-of-scope (still deferred)

- **Truly unbounded control chains** (more than ~5 deep): the
  parser explores them, but the test corpus exercises 4-deep at
  most. If future corpus pressure shows runaway parser cost on
  arbitrarily deep chains, a chart-pruning heuristic — not
  functional uncertainty — would be the right response.
- **Long-distance relativization** through nested XCOMP/COMP
  (§7.5 + §7.6 cross-cutting deferral). That construction
  genuinely needs functional uncertainty (a relativization gap
  inside an XCOMP at unbounded depth) — distinct from the
  control case.

## Phase 4 §7.7: applicatives + pa-causatives

**Date:** 2026-04-30. **Status:** active.

### APPL / CAUS feature inventory populated

The §7.1 secondary-feature inventory (``APPL ∈ {INSTR, BEN, REASON,
CONVEY, NONE}``, ``CAUS ∈ {DIRECT, INDIRECT, NONE}``) is now
populated by the morphology and lexicon. ``NONE`` is the sentinel
value emitted by the analyzer for non-applicative / non-causative
verbs — the same pattern as §7.6's ``CTRL_CLASS=NONE``. Without the
sentinel, the parser's non-conflict matcher would let an
``V[APPL=BEN]`` rule fire on any plain verb.

### Per-cell ``feats`` on ParadigmCell

Phase 4 §7.6 added per-root ``feats``. §7.7 generalises to per-cell
``feats``: a paradigm cell can declare ``APPL=BEN`` or
``CAUS=DIRECT`` (etc.) and those feature values ride into every
generated MorphAnalysis. Cell-level feats override root-level feats
on the same key — the cell is the more specific source (one root
can generate forms across multiple applicative variants).

### Benefactive applicative ``ipag-`` (APPL=BEN)

A single applicative variant is implemented in this commit. Three
new IV cells under ``affix_class: ipag``:

- PFV: ``ipinaggawa`` ← ``[prefix("pag"), infix("in"), prefix("i")]``
- IPFV: ``ipinaggagawa`` ← ``[cv_redup, prefix("pag"), infix("in"), prefix("i")]``
- CTPL: ``ipaggagawa`` ← ``[cv_redup, prefix("pag"), prefix("i")]``

Lex entries for ``gawa-BEN`` / ``sulat-BEN`` / ``bili-BEN`` carry
``MAKE-FOR <SUBJ, OBJ>`` etc., with ``morph_constraints={VOICE:
IV, APPL: BEN}``. The bare ``i-`` IV cells are now annotated
``APPL=CONVEY`` so they discriminate against the new BEN forms.

The patient role (the thing made / written / bought) is **omitted**
from the 2-arg PRED — Tagalog's full benefactive frame
(``Ipinaggawa ng nanay ang anak ng kanin``) admits two GEN-NPs,
which our existing grammar doesn't support. Multi-GEN-NP frames
deferred to a later commit (Phase 5 LMT will reclassify them as
typed obliques).

### ``ipang-`` instrumental and ``ika-`` reason — deferred

Both require homorganic-nasal place-assimilation (``pang-`` + b →
``pam-``; + d → ``pan-``; + k → ``pang-``). Our existing
``nasal_substitute`` op replaces the base's first consonant rather
than prepending an assimilated nasal, so it doesn't produce
``ipinambili`` (instrument-bought) from ``bili``. Either a new
phonological op or per-base-class cell duplication is needed.
Deferred until Phase 5 corpus pressure warrants the extra work.

**Update (Phase 5c):** lifted in Phase 5c §7.7 follow-on Commit 4
(see the entry below).

### Direct (monoclausal) causative ``pa-...-in`` (CAUS=DIRECT)

Three new OV cells under ``affix_class: pa_in``:

- PFV: ``pinakain`` ← ``[prefix("pa"), infix("in")]``
- IPFV: ``pinakakain`` ← ``[cv_redup, prefix("pa"), infix("in")]``
- CTPL: ``pakakainin`` ← ``[cv_redup, prefix("pa"), suffix("in")]``

Lex entries: ``CAUSE-EAT <SUBJ, OBJ>`` for ``kain``, etc. SUBJ is
the causee (NOM-marked pivot); OBJ is the causer (GEN-marked agent
of causing). Single-clause; the embedded eventuality is folded
into the matrix's PRED (no XCOMP). The food / patient is again
omitted from the 2-arg PRED.

### Indirect (biclausal) causative ``magpa-`` (CAUS=INDIRECT)

Three new AV cells under ``affix_class: magpa``:

- PFV: ``nagpakain`` ← ``[prefix("pa"), prefix("nag")]``
- IPFV: ``nagpapakain`` ← ``[prefix("pa"), cv_redup, prefix("nag")]``
- CTPL: ``magpapakain`` ← ``[prefix("pa"), cv_redup, prefix("mag")]``

Note the IPFV / CTPL reduplication targets the ``pa-`` prefix
(``papakain``), not the root cv. This is encoded by ordering
``prefix("pa")`` before ``cv_redup`` in the ops list (the existing
AV IPFV cells reduplicate root cv by ordering ``cv_redup`` first).

Cells declare ``CTRL_CLASS=INTRANS`` so the §7.6 intransitive
control wrap rule fires:

```text
S → V[CTRL_CLASS=INTRANS] NP[CASE=NOM] PART[LINK] S_XCOMP
```

The matrix has ``CAUSE-EAT <SUBJ, XCOMP>`` (causer = SUBJ; caused
event = XCOMP). The causee is realised as the controlled SUBJ
inside the XCOMP — Tagalog's biclausal causative composes
seamlessly with the existing control infrastructure.

### Existing ``_entry`` helper tightened

The lexicon's ``_entry`` helper now adds ``CAUS=NONE`` (and
``APPL=NONE`` for non-IV voices, ``APPL=CONVEY`` for IV) to every
constructed BASE entry's ``morph_constraints``. Without this,
existing ``kain`` AV-tr / OV entries would spuriously match the
new causative forms (``nagpakain`` / ``pinakain``) because the
non-conflict matcher ignores feature keys absent from one side.

### Out-of-scope (deferred)

- **``ipang-`` instrumental**, **``ika-`` reason**: need
  homorganic-nasal sandhi.
- **Multi-GEN-NP frames** (full applicative / causative argument
  structures with both agent and patient as GEN-marked): need
  grammar rule extensions and disambiguation.
- **LMT-driven OBL-X classification** of the demoted oblique:
  Phase 5 territory per the original plan §7.7.
- **``pa-...-an`` DV causative** and other less-common applicative
  affix variants.

## Phase 4 §7.8: demonstratives, possessives, quantifier float

**Date:** 2026-04-30. **Status:** active.

### Demonstrative pronouns and DEIXIS percolation

The 9 demonstrative entries in ``particles.yaml`` (3 deixis ×
3 cases) gain a ``DEM=YES`` feature so a single per-case
standalone-NP rule can select them:

```text
NP[CASE=X] → DET[CASE=X, DEM=YES]      (NOM forms ito/iyan/iyon)
NP[CASE=X] → ADP[CASE=X, DEM=YES]      (GEN/DAT forms nito/dito/...)
   (↑) = ↓1
   (↑ PRED) = 'PRO'
```

This admits ``Kumain ito`` "This ate", ``Kinain iyan ng aso``
"The dog ate that one", etc. PRED is synthesized as ``'PRO'`` so
the demonstrative-as-NP passes completeness when it serves as
SUBJ / OBJ.

Non-demonstrative DET / ADP entries (``ang``, ``si``, ``ng``,
``sa``, ``ni``, ``kay``) get ``DEM=NO`` defaulted by the analyzer.
Without the sentinel, the parser's non-conflict matcher would
let plain ``ang`` match ``DET[CASE=NOM, DEM=YES]`` and form a
spurious bare NP.

The existing ``NP[CASE=X] → DET[CASE=X] N`` rule's equation list
is also updated to ``(↑) = ↓1, (↑ PRED) = ↓2 PRED`` so DET
features (CASE, MARKER, DEIXIS for demonstratives) percolate into
the NP's f-structure. Previously the rule only set CASE explicitly
and DEIXIS was lost.

### NP-internal possessive

A per-case rule attaches a GEN-NP possessor on the head NP:

```text
NP[CASE=X] → NP[CASE=X] NP[CASE=GEN]
   (↑) = ↓1
   (↑ POSS) = ↓2
```

``Kinain ng aso ang isda ng bata`` "The dog ate the child's fish":
the matrix SUBJ is ``isda`` with ``POSS = bata``.

The rule is recursive — multi-level possession (``isda ng bata ng
pamilya``) chains as left-associative POSS layers. It also
introduces structural ambiguity: a sequence like ``ang batang
kumain ng isda`` (relativized head with RC) parses both as
relativization (``ng isda`` is OBJ inside the RC) AND as
possession (``ng isda`` is possessor of the RC-modified head).
Both are valid LFG-wise; the existing §7.5 relativization tests
were updated to use ``n_best=10`` and pick the relativization
parse explicitly.

### Pronominal possessive — deferred

The pronominal possessive form (``ang aklat ko`` "my book")
conflicts with the §7.3 Wackernagel clitic placement, which
moves pronominal clitics to immediately after the verb. Without
context-aware placement (e.g. "don't move ``ko`` when it follows
a noun head"), the pronominal possessive surfaces as an agent /
SUBJ clitic instead. Out of scope for this commit; revisit when
context-aware placement is wired up.

**Update (Phase 5c):** lifted in Phase 5c §7.8 follow-on (see
the entry below).

### Quantifier float

Two quantifiers are seeded as ``Q`` (a new POS):

- ``lahat`` "all" (``QUANT=ALL``)
- ``iba`` "other" (``QUANT=OTHER``)

A single recursive rule attaches a floated quantifier to the
clause-final position as a matrix ADJ member:

```text
S → S Q
   (↑) = ↓1
   ↓2 ∈ (↑ ADJ)
   (↓2 ANTECEDENT) = (↑ SUBJ)
```

``Kumain ang bata lahat`` "All the children ate" produces an ADJ
member with ``QUANT=ALL`` and ``ANTECEDENT`` bound to the matrix
SUBJ — this is the canonical LFG analysis of floating
quantifiers (Bresnan 2001 §6.6).

### Pre-NP partitive (``lahat ng bata``) — deferred

The pre-NP partitive form requires a new ``QP`` non-terminal and
its own grammar rule (the quantifier heads a sub-NP that admits
a partitive ``ng``-NP). Out of scope for this commit; the floated
form is the more common surface pattern and exercises the
binding mechanism.

**Update (Phase 5b):** lifted in Phase 5b §7.8 follow-on. The
implementation chose a flat 3-child rule rather than a separate
``QP`` non-terminal — see the §7.8 follow-on entry below.

## Phase 4 §7.9: robustness — fragments, ranking, --strict

**Date:** 2026-04-30. **Status:** active.

### ParseResult / Fragment dataclasses

The legacy :func:`parse_text` is preserved unchanged (returning a
list of 4-tuples) for backward compatibility with the 41+ existing
test sites that destructure the tuple shape. Phase 4 §7.9 adds a
sibling :func:`parse_text_with_fragments` that returns a
:class:`ParseResult` with two fields:

- ``parses`` — complete parses (the same 4-tuple list, ranked).
- ``fragments`` — :class:`Fragment` instances when no complete
  parse exists. Each fragment carries a span, partial CNode,
  partial f-structure, and the diagnostics that prevented
  promotion.

At most one of the two fields is non-empty: a successful parse
suppresses fragment output (the user wanted a parse and got one).
:func:`parse_text` is now a thin wrapper around
:func:`parse_text_with_fragments` that just returns ``.parses``.

### Fragment extraction algorithm

The Earley chart already carries every completed sub-derivation —
the parser builds them while exploring rules. :class:`PackedForest`
is extended with a ``chart`` attribute (the full per-column dict
of states) and an ``iter_fragments()`` method that walks the chart
for non-root completed states (``state.dot == len(rule.rhs)`` and
``not (start == 0 and end == n)``).

Fragments are ranked by (decreasing span size, ascending start
column, alphabetical category) and deduplicated by
``(label, start, end)`` so a single (label, span) yields one
fragment CNode, not the cartesian product of all sub-history
combinations. This keeps fragment output bounded and useful for
debugging without dominating the result list.

### Heuristic parse ranking

Complete parses are sorted by a tuple key
``(depth, voice_score)`` — smaller is better:

1. ``depth`` — total CNode count. Shorter derivations win, which
   resolves the new §7.8 possessive-vs-relativization ambiguity
   (the possessive wrap nests one extra layer) and the AV-tr vs
   AV-intr-with-possessive ambiguity in transitive contexts.
2. ``voice_score`` — 0 if the leftmost-spine V leaf is AV, 1
   otherwise. Tagalog AV is the most-frequent voice; when the
   same surface ambiguates AV vs non-AV (e.g. ``mag-`` /
   ``-um-`` syncretism), prefer AV.

The plan §7.9 also calls for a "lex specificity" component
(prefer hand-authored BASE entries over the synthesized fallback).
A heuristic over PRED templates was prototyped but dropped — it
mis-classified hand-authored short PREDs (``EAT``, ``BUY``) as
synthesized. Reliable distinction needs marking on the
LexicalEntry itself; deferred until the BASE / synthesizer split
is more deterministic.

The ranker walks all candidates returned by ``forest.iter_trees``
(no early ``best_k`` truncation), sorts, and only then truncates
to ``n_best``. This fixes a latent bug where ``best_k(5)`` could
discard a valid parse that survived past position 5 in the
forest's enumeration order.

### CLI: ``tgllfg parse`` with ``--strict``

A new ``parse`` subcommand prints a parse summary:

```text
$ tgllfg parse "Kumain ang aso ng isda."
Parse #1:
  PRED: EAT <SUBJ, OBJ>
  VOICE: AV
  ASPECT: PFV
...
```

On failure, default mode emits fragments:

```text
$ tgllfg parse "Kumain ng aso ang."
(partial: 2 fragment(s))
Fragment #1 [tokens 1..3]: NP[CASE=GEN]
Fragment #2 [tokens 2..3]: N
```

``--strict`` suppresses fragment output: empty stdout, brief
notice to stderr, exit 0 (Unix-tool convention: no match → no
output, but exit cleanly).

### Diagnostic ``cnode_label`` — partial

The plan §7.9 calls for diagnostics to "name the offending
equation and c-structure path". Equation strings are already
populated by :mod:`tgllfg.fstruct.unify`. The ``cnode_label``
field on :class:`tgllfg.fstruct.graph.Diagnostic` is a placeholder
note in the existing checks code — populating it requires a
node-id → c-tree-node mapping during well-formedness checks.
Deferred to a follow-up; the equation strings already give
enough handle for v1 debugging.

### Out-of-scope (deferred)

- **Statistical reranker** trained on a gold corpus. The plan
  explicitly marks this as a v1 follow-up.
- **All-fragments mode**: extracting fragments even when no
  non-root rule completes (e.g. for ``aso ang isda`` with no
  verb, the parser predicts no rules so no completions exist).
  Would require changing the parser's prediction strategy.
- **Path-rendering on diagnostics**: ``cnode_label`` placeholder
  remains TODO.

## Phase 5 §8: Lexical Mapping Theory

**Status:** active. The `tgllfg.lmt` package replaces the Phase 4
voice-aware heuristic with a Bresnan & Kanerva 1989 `[±r, ±o]`
engine. End-user docs live in `docs/lmt.md`; this section records
the analytical decisions taken during implementation.

### `OBJ-θ` upgrade for non-AV ng-non-pivots

The Phase 4 §7.1 OBJ-uniform analysis maps the *ng*-non-pivot in
OV / DV / IV transitives to bare `OBJ` (see "*ng*-non-pivot in
transitive non-AV → OBJ" earlier in this file). Phase 5 retains
that surface analysis in the **grammar** (the `(↑ OBJ) = ↓N`
equations are unchanged) but the **LMT engine** produces typed
`OBJ-θ` (e.g., `OBJ-AGENT` for OV's demoted ng-AGENT).

The divergence is intentional. The LMT engine reads the lex
entry's per-role `[±r, ±o]` profile; for OV-AGENT that profile is
`[+r, +o]`, which the truth table maps to `OBJ-θ`. To produce bare
`OBJ` instead, the OV-AGENT profile would have to be `[-r, +o]` —
but that would also make AGENT SUBJ-eligible, and step 4 would
pick AGENT for SUBJ instead of PATIENT. The pivot-respecting
profile demands `[+r, +o]` for non-pivot ng-NPs, which produces
`OBJ-θ`.

The disagreement between the engine's `OBJ-θ` and the grammar's
bare `OBJ` surfaces as informational `lmt-mismatch`. A future
rewrite could change the grammar to emit `(↑ OBJ-θ) = ↓N` per
voice/verb class and align the two sides; for now the AStructure
carries the typed prediction while the f-structure carries the
bare-OBJ binding.

### Per-voice intrinsic profiles, not voice-merge

Plan §8.2 step 2 says "voice morphology supplies additional
[±r, ±o] constraints — for Tagalog, the voice affix marks the
argument promoted to SUBJ." A clean reading would be:

- Lex entry has one voice-independent profile per role (e.g.,
  `kain` always has `AGENT [-o]`, `PATIENT [-r]`).
- Voice morphology adds the SUBJ-promotion stamp at parse time.

We tried this. It doesn't work for Tagalog: with one
voice-independent profile, step 4 picks the same SUBJ regardless
of voice, because the (`r`, `o`) features are the same. The voice
constraint would have to be powerful enough to flip patient roles
between `[-r]` (OV pivot) and `[+r]` (AV non-pivot) — which is
the same as just storing per-voice profiles directly.

Phase 3 already gives every voice-affixed verb form its own
`lex_entry` row (`kumain` AV-tr, `kinain` OV-tr, etc.). Phase 5
attaches the per-voice intrinsic profile to those rows. The
runtime engine consumes the profile as-is and treats step 2 as a
no-op. `apply_voice_constraints` is preserved as a hook in case
future voice systems need it.

### Role inventory augmentation

Plan §8.1 lists 10 textbook roles (AGENT, PATIENT, THEME, GOAL,
RECIPIENT, BENEFICIARY, INSTRUMENT, LOCATION, EXPERIENCER,
STIMULUS). Phase 4 §7 added `ACTOR` (intransitive AV pivot),
`CONVEYED` (IV-pivot for transferred entities), `CAUSER` /
`CAUSEE` / `EVENT` (causative frames), and `COMPLEMENT`
(open-complement target for control verbs). Phase 5 keeps these
as augmentation rather than folding them into the textbook
inventory:

- `ACTOR` is needed because the synthesizer fallback emits
  `[ACTOR]` when transitivity is unspecified; folding to AGENT
  would lose the "voice-independent intransitive" signal.
- `CONVEYED` behaves like `THEME` in the truth table, but voice-
  marked differently in IV — keeping the role distinct lets each
  lex entry document which thematic flavor it expects.
- `CAUSER` / `CAUSEE` / `EVENT` participate in causative frames
  whose mapping diverges from monoclausal transitives; they
  carry distinct intrinsic-classification profiles.
- `COMPLEMENT` is XCOMP-bound and never appears in the truth
  table — keeping it distinct simplifies the stipulated-GF
  bypass.

Each augmentation carries its own row in
`tgllfg.lmt.common._DEFAULT_INTRINSICS` so the bootstrap path
produces correct defaults.

### Sa-NP OBL-θ classification — post-solve mutation

§7.1 deferred the question of how sa-NPs become typed
`OBL-LOC` / `OBL-GOAL` / `OBL-BEN` / `OBL-INSTR` slots. Phase 5
implements this as a post-solve mutation in
`tgllfg.lmt.oblique_classifier`:

1. The grammar continues to bind every `NP[CASE=DAT]` into
   `(↑ ADJUNCT)` via the existing equations.
2. After `solve()` returns the f-structure, the LMT engine
   produces a mapping; for each role mapped to `OBL-θ`, the
   classifier moves a sa-NP member of `ADJUNCT` into the typed
   slot.
3. `lfg_well_formed` then runs on the post-classify f-structure;
   completeness/coherence checks see the typed slots.

Why not rewrite the grammar instead: §7.5 relativization, §7.3
clitic placement, §7.4 ay-inversion, and §7.8 quantifier float
all consume the parser's c-tree and the same
`↓N ∈ (↑ ADJUNCT)` equations. Rewriting to emit `OBL-X` directly
would require duplicating each rule per verb-class and fighting
the non-conflict matcher. Post-solve mutation contains the blast
radius.

Multi-OBL semantic disambiguation (which sa-NP is `BEN` vs `LOC`
in a 3-arg sentence) is out of scope. The classifier matches in
stable order — a-structure for roles, `FStructure.id` for sa-NPs
— and emits an informational `lmt-mismatch` on cardinality
mismatch.

### Diagnostic promotion policy

The engine emits diagnostics from steps 6 and 7. The pipeline
filters them:

<!-- markdownlint-disable MD013 -->
| Engine source | Surfaced? | Routing |
| --- | --- | --- |
| Step 6 `subject-condition-failed` (lex profile has no SUBJ candidate) | dropped | The structural `lfg_well_formed` downstream catches the case where the f-structure also lacks SUBJ. If the f-structure has SUBJ, the parse is structurally OK and shouldn't be suppressed for an internal lex inconsistency. |
| Step 7 `lmt-biuniqueness-violated` (two roles → same GF) | yes | Always a real lex contradiction; surfaced as-is (blocking by absence from `NON_BLOCKING_KINDS`). |
<!-- markdownlint-enable MD013 -->

`lmt_check` adds two more diagnostic emitters of its own:

| Condition | Routing |
| --- | --- |
| Engine predicts SUBJ for some role but the f-structure lacks SUBJ | **Blocking** (`subject-condition-failed`) |
| GF-set difference excluding SUBJ slot (the OBJ ⇄ OBJ-θ noise) | Informational (`lmt-mismatch`) |

The reverse SUBJ disagreement (f-structure has SUBJ but engine
didn't predict one) means a buggy lex profile but a valid parse
— stays informational via the general `lmt-mismatch`. Blocking
the parse for a lex-internal inconsistency would be wrong.

### Out-of-scope (deferred)

- **Multi-GEN-NP applicative / causative frames.** A 3-arg
  `ipinaggawa niya ng silya ang kapatid` profile cleanly
  produces `OBJ-AGENT`, `OBJ-PATIENT`, `SUBJ` from the engine,
  but no Phase 4 BASE entry emits them and the grammar rules
  need a second-GEN-NP slot. Phase 5b.
- **Multi-OBL semantic disambiguation.** When two `OBL-θ` roles
  compete for two sa-NPs, positional matching is the placeholder.
  **Update (Phase 5c):** lifted in Phase 5c §8 follow-on Commit 6
  via lemma-keyed semantic-class lookup (see the entry below).
- **Embedded-clause LMT.** `lmt_check` only validates the matrix
  f-structure. Embedded XCOMP/COMP clauses have their own PRED
  and could be recursively checked; not wired.
- **`OBJ-θ` in the grammar.** The Phase 4 grammar emits bare `OBJ`
  for non-AV ng-non-pivots; the engine's typed `OBJ-θ` is
  surfaced via the AStructure and the diagnostic detail. A future
  rewrite to `(↑ OBJ-θ) = ↓N` would eliminate the
  `lmt-mismatch` noise.

## Phase 5b §7.7 follow-on: multi-GEN-NP applicative frames

**Status:** active. Phase 4 §7.7 deferred three-argument
applicative / causative frames where the demoted-from-pivot
oblique surfaces as a second `ng`-marked NP. Phase 5b lifts that
deferral incrementally: this section records the choices for the
IV-BEN scope; pa-OV-direct multi-GEN follows the same pattern and
will lift in a subsequent commit.

### Word-order convention: first ng-NP = AGENT, second = PATIENT

Tagalog admits free order among non-pivot ng-NPs but a strong
post-V positional preference: the agentive role sits closer to
the verb than the patient. Schachter & Otanes 1972 §6.5 describes
the `actor first, then goal` ordering as the unmarked Tagalog
post-verbal pattern; Kroeger 1993 §3.3 confirms it for
three-argument constructions.

The Phase 5b grammar rules encode this positional convention
directly:

```text
S → V[VOICE=IV] NP[NOM] NP[GEN] NP[GEN]
   ↳ (↑ SUBJ) = ↓2, (↑ OBJ-AGENT) = ↓3, (↑ OBJ-PATIENT) = ↓4
S → V[VOICE=IV] NP[GEN] NP[NOM] NP[GEN]
   ↳ (↑ SUBJ) = ↓3, (↑ OBJ-AGENT) = ↓2, (↑ OBJ-PATIENT) = ↓4
S → V[VOICE=IV] NP[GEN] NP[GEN] NP[NOM]
   ↳ (↑ SUBJ) = ↓4, (↑ OBJ-AGENT) = ↓2, (↑ OBJ-PATIENT) = ↓3
```

The pivot `ang`-NP is the BENEFICIARY (the IV-BEN promotion
target); the two `ng`-NPs are AGENT and PATIENT in surface order.
A sentence with the ng-NPs in the *opposite* semantic order
(PATIENT before AGENT) would parse with reversed bindings —
this is a known limitation that semantic disambiguation
(animacy, definiteness, prior context) could fix. Phase 5b's
positional binding is the placeholder.

### Typed OBJ-θ slots

Both ng-NPs map to typed `OBJ-θ` GFs (`OBJ-AGENT` and
`OBJ-PATIENT`). The LMT engine produces these directly from each
role's `[+r, +o]` intrinsic profile. The two GFs are distinct
fully-qualified strings under
`tgllfg.fstruct.checks.is_governable_gf`, so biuniqueness
(LMT step 7) doesn't flag them as a clash.

The lex entry's PRED template is upgraded to typed form:

```text
MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>
```

Completeness checks the f-structure has all three governables;
coherence checks no extras. The pre-existing two-arg lex entry
(`MAKE-FOR <SUBJ, OBJ>`, no PATIENT) coexists — sentences without
a second ng-NP fall through to it because the three-arg's
completeness check fails when OBJ-PATIENT is absent.

### Scope

The multi-GEN-NP frames lifted in Phase 5b so far:

- **IV-BEN applicatives** (`gawa`, `sulat`, `bili`) — Commit 1.
  Pivot is BENEFICIARY; non-pivot ng-NPs are AGENT and PATIENT,
  bound positionally to `OBJ-AGENT` and `OBJ-PATIENT`.
- **pa-OV-direct causatives** (`kain`, `basa`, `inom`) — Commit 2.
  Pivot is CAUSEE; non-pivot ng-NPs are CAUSER and PATIENT,
  bound to `OBJ-CAUSER` and `OBJ-PATIENT`. The grammar matches
  `V[VOICE=OV, CAUS=DIRECT]` specifically so plain OV transitives
  (CAUS=NONE) don't spuriously trip the multi-GEN rule.

Still deferred:

- **DV three-argument constructions** (rarer): would need a
  third ng-NP for a non-RECIPIENT theme. No current Phase 4
  BASE entry has the shape.
- **Magpa-AV-indirect three-argument** would require the embedded
  XCOMP to take its own arguments — the matrix only has CAUSER
  and EVENT, so multi-GEN doesn't apply at the matrix level.

The Phase 5b deferral list also includes:

- **Multi-OBL semantic disambiguation** for sa-NPs — out of
  scope here (this commit is GEN-only).
- **OV/DV control complements** — separate problem (controller
  binds embedded AGENT, not embedded SUBJ).
- **OBJ-θ in the grammar** — the Phase 4 grammar emits bare
  `OBJ` for non-AV ng-non-pivots while the LMT engine produces
  typed `OBJ-θ`. Aligning the two would eliminate the
  informational `lmt-mismatch` noise but touches every per-voice
  grammar rule.
- **Raising verbs**, **`ipang-` / `ika-` applicatives**,
  **pronominal possessive**, **long-distance relativization** —
  all unchanged from the Phase 4 deferral inventory.

## Phase 5b §7.8 follow-on: pre-NP partitive

**Status:** active. Lifts the §7.8 deferral noted earlier in this
file ("Pre-NP partitive (`lahat ng bata`) — deferred"). Sentences
like ``Kumain ang lahat ng bata`` ("All of the children ate")
now parse with the quantifier riding inside the NP rather than
floated to clause-final.

### Flat 3-child rule, no `QP` non-terminal

The §7.8 deferral note suggested a `QP` non-terminal. The
implementation chose a flat 3-child NP rule instead:

```text
NP[CASE=NOM] → DET[CASE=NOM] Q NP[CASE=GEN]
NP[CASE=GEN] → ADP[CASE=GEN] Q NP[CASE=GEN]
NP[CASE=DAT] → ADP[CASE=DAT] Q NP[CASE=GEN]
```

Equations:

```text
(↑) = ↓1                  -- outer marker supplies CASE / MARKER
(↑ PRED) = ↓3 PRED        -- head supplied by inner NP[GEN]
(↑ QUANT) = ↓2 QUANT      -- Q's QUANT atom rides on the NP
```

A separate `QP` non-terminal would have been more decomposable
but adds a layer for no immediate gain — the flat rule reuses the
existing `NP[CASE=GEN]` non-terminal as the partitive complement.

### Quantifier surfaces as a feature on the NP

The partitive's quantifier rides as a `QUANT` atom on the resulting
NP's f-structure (matching the floated-quantifier convention,
where the floated Q's f-structure carries `QUANT` from particles.yaml).
Reading off "all" vs "some" from a parse means inspecting
``np.feats["QUANT"]``.

### Inner NP[GEN] is structurally separate, not the head

The equations don't structure-share the outer NP with the inner
NP[GEN] — only the inner's PRED is borrowed. The inner NP[GEN]
keeps `CASE=GEN`, `MARKER=NG`, and any features of its own; the
outer NP[X] gets `CASE=X`, `MARKER=ANG/NG/SA`, plus the borrowed
PRED and a fresh `QUANT`. This avoids the structure-sharing
conflict that `(↑) = ↓3` would create (outer's CASE would be
forced to GEN by the inner).

### Possessive vs partitive disambiguation

Both surface forms `DET X NP[GEN]` and `DET Q NP[GEN]` exist:

- `ang aklat ng bata` (possessive) — DET + N + NP[GEN], parsed
  by the Phase 4 §7.8 NP-internal possessive rule. Without a Q
  in position 2, only the possessive rule fires.
- `ang lahat ng bata` (partitive) — DET + Q + NP[GEN], parsed by
  the new partitive rule. The Q is gated by POS=Q.

The two rules don't compete because Q vs N is an unambiguous POS
distinction.

### Floated quantifier unchanged

The pre-existing `S → S Q` floated-quantifier rule (`Kumain ang
bata lahat`) is unaffected. It operates at the S level (Q is a
sister of the matrix clause), not within an NP. Both surfaces
parse cleanly without competing.

## Phase 5c §7.8 follow-on: pronominal possessive

**Date:** 2026-05-01. **Status:** active. Lifts the §7.8 deferral
noted earlier in this file ("Pronominal possessive — deferred").
Sentences like ``Kumain ang bata ng libro ko`` ("The child ate my
book") now parse with `ko` bound as the OBJ's `POSS`, rather
than being hoisted into the post-V cluster as a clause-level
clitic.

### Single-line fix in the Wackernagel pass

The Phase 4 §7.3 placement pass moved every PRON token with
`is_clitic=True` into the post-V cluster regardless of left
context. Phase 5c adds a small context-aware exception: when a
PRON-clitic immediately follows a NOUN-reading token, it stays in
place. The fix lives in `src/tgllfg/clitics/placement.py` as a
new helper `_is_post_noun_pron(analyses, i)` consulted when
collecting `pron_indices` in `reorder_clitics`.

The grammar's existing NP-internal possessive rule
(`NP[CASE=X] → NP[CASE=X] NP[CASE=GEN]`, plus the standing
`NP[CASE=GEN] → PRON[CASE=GEN]`) does the rest: with the pronoun
left in its post-noun position, it parses as an `NP[GEN]`
modifier and rides into the head's f-structure as `POSS`.

### Why "after a NOUN" is the right boundary

The same surface form (`ko`, `mo`, `niya`, `namin`, `ninyo`,
`nila`) serves both as a clause-level clitic argument and as an
NP-internal possessor. The disambiguating signal is left context:

- After a VERB (`Kinain mo ang isda`): `mo` is the OBJ-AGENT
  clitic — moved to the post-V cluster (unchanged behaviour).
- After a PART (`Hindi mo kinain ang isda`): pre-V clitic, also
  moved to the post-V cluster (unchanged behaviour).
- After a NOUN (`ang isda ko`): possessive — left in place
  (the new behaviour).

The check mirrors the existing `disambiguate_homophone_clitics`
left-context pattern (`"NOUN" in prev_pos or "N" in prev_pos`),
which already disambiguates `na` between linker and aspectual
clitic by left context.

### One-clitic-moves-one-stays composes

`Kinain mo ang isda ko` exercises both decisions in one
sentence: `mo` is post-V (moves into cluster, indeed it's the
OBJ-AGENT of the OV verb), `ko` is post-NOUN `isda` (stays as
possessor). The placement pass evaluates each clitic
independently against its own left context, so the two outcomes
compose without interference. NEG (`Hindi kumain ang bata ng
libro ko`) and adverbial enclitics (`Kumain na ang bata ng libro
ko`) behave the same way: their movement is independent of the
post-noun pronoun's stay-in-place.

### Structural ambiguity is resolved by parse ranking

`Kumain ang bata ng libro ko` is structurally ambiguous: `ng
libro` could attach as OBJ (with `ko` as its possessor) or as
possessor of the SUBJ `bata` (with `ko` then attaching at a
deeper level). The parser produces both readings and Phase 4 §7.9
ranking picks one. The tests assert that **at least one** parse
has the desired structure (OBJ-with-pronominal-possessor),
mirroring how Phase 4 §7.8 tests for `ng`-NP possessive
ambiguity already work.

### Out-of-scope (still deferred)

- **Pronominal possessor inside a relative clause head.** A noun
  followed by a linker + RC (`aklat na binasa`) followed by a
  pronoun would compete with the RC's own SUBJ-binding; the
  parser would need to decide whether `ko` belongs to the head
  noun or the relative clause. Not exercised by the current
  corpus.
- **Possessive linker variant** (`aklat kong binasa` —
  pronoun + linker `-ng` to introduce a relative clause). This
  is a distinct construction needing its own grammar rule;
  deferred.

## Phase 5c §7.7 follow-on: ipang- instrumental and ika- reason

**Date:** 2026-05-01. **Status:** active. Lifts the §7.7 deferral
("ipang- instrumental and ika- reason — deferred") noted earlier
in this file. Sentences like ``Ipinambili ng nanay ang pera``
("money is what mother bought-with") and ``Ikinasulat ng bata
ang gutom`` ("hunger is the reason the child wrote") now parse.

### New sandhi op: ``nasal_assim_prefix``

The Phase 4 deferral note correctly identified the missing piece:
``nasal_substitute`` (the existing op for ``mang-`` / ``nang-`` /
``pang-`` AV distributives) DROPS the base's first consonant
(``bili`` → ``mili``, then ``mang-`` head + ``mili`` →
``mamili`` "be a buyer"). The instrumental applicative ``ipang-``
needs the RETAIN pattern: ``pang-`` + ``bili`` → ``pambili`` →
``pinambili`` → ``ipinambili``.

Phase 5c adds ``nasal_assim_prefix(prefix, base)`` to
:mod:`tgllfg.morph.sandhi`. It requires an ``ng``-final prefix
and prepends it to the base, place-assimilating the prefix's
final nasal to the base's first consonant per the standard
table:

| Base initial | Assimilated prefix end |
| --- | --- |
| `b`, `p` | `m` (bilabial) |
| `t`, `d`, `s` | `n` (alveolar) |
| `k`, `g` | `ng` (velar — vacuous) |
| vowel / sonorant | `ng` (no assimilation site) |

The base's initial consonant is **retained**, distinguishing this
op from ``nasal_substitute`` (drop). Both patterns coexist on the
same root in modern Tagalog with different meanings: ``mamili``
"be a buyer" (``mang-`` AV, drop) vs ``ipinambili`` "instrument-
bought" (``ipang-`` IV-INSTR, retain).

### Three IV-INSTR cells (ipang-, APPL=INSTR)

Operations follow the ipag- shape with ``nasal_assim_prefix("pang")``
in place of ``prefix("pag")``:

```text
PFV:  nasal_assim_prefix("pang") → infix("in") → prefix("i")
IPFV: cv_redup → nasal_assim_prefix("pang") → infix("in") → prefix("i")
CTPL: cv_redup → nasal_assim_prefix("pang") → prefix("i")
```

Surface forms for ``bili``: ``ipinambili`` (PFV), ``ipinambibili``
(IPFV), ``ipambibili`` (CTPL). For ``tahi``: ``ipinantahi``,
``ipinantatahi``, ``ipantatahi``.

### Three IV-REASON cells (ika-, APPL=REASON)

The ``ka-`` prefix has no nasal sandhi; cells are parametrically
identical to ipag- with ``"ka"`` substituted for ``"pag"``:

```text
PFV:  prefix("ka") → infix("in") → prefix("i")
IPFV: cv_redup → prefix("ka") → infix("in") → prefix("i")
CTPL: cv_redup → prefix("ka") → prefix("i")
```

Surface forms for ``kain``: ``ikinakain`` (PFV), ``ikinakakain``
(IPFV), ``ikakakain`` (CTPL). For ``sulat``: ``ikinasulat`` etc.

### Lex entries: 2-arg pivot-rotation profile

Mirrors the existing IV-BEN choice. The pivot rotates to
``INSTRUMENT`` (ipang-) or ``REASON`` (ika-); the agent demotes
to ``OBJ-AGENT``. The patient (what was bought / sewn / eaten /
written) is omitted from the 2-arg PRED — multi-GEN-NP
extensions can be added if corpus pressure warrants, mirroring
Phase 5b §7.7 follow-on for IV-BEN.

```text
BUY-WITH        <SUBJ, OBJ-AGENT>   bili IV-INSTR
SEW-WITH        <SUBJ, OBJ-AGENT>   tahi IV-INSTR
EAT-FOR-REASON  <SUBJ, OBJ-AGENT>   kain IV-REASON
WRITE-FOR-REASON <SUBJ, OBJ-AGENT>  sulat IV-REASON
```

Intrinsic profiles: ``AGENT [+r, +o]`` (demoted to OBJ-AGENT) +
``INSTRUMENT [-r, -o]`` or ``REASON [-r, -o]`` (the pivot).

### New ``REASON`` role in :class:`tgllfg.lmt.Role`

Added to the Tagalog augmentation section of the Role enum, with
default intrinsic ``(r=None, o=False)`` mirroring ``INSTRUMENT``.
Inserted into ``ROLE_HIERARCHY`` between ``INSTRUMENT`` and
``STIMULUS``.

### Surface ambiguity preserved

``ikinakain`` is genuinely homophonous in Tagalog: it's both the
IPFV of bare ``i-`` (CONVEY reading) and the PFV of ``ika-``
(REASON reading). The morph analyzer produces both analyses; the
parser explores both and the matching lex entry is selected per
parse. ``Ikinakain ng bata ang gutom`` admits both readings; the
test asserts the REASON parse is among the n-best (mirroring how
Commit 2's pronominal-possessive tests handle structural
ambiguity).

### Existing nouns added: ``karayom``, ``gutom``

Two seed nouns were added to ``data/tgl/nouns.yaml`` to give the
new applicatives natural test fixtures: ``karayom`` "needle"
(instrument) and ``gutom`` "hunger" (canonical reason).

### Out-of-scope (still deferred)

- **Multi-GEN-NP IV-INSTR / IV-REASON frames.** Three-argument
  variants where AGENT, PATIENT, and INSTRUMENT/REASON are all
  GEN/NOM-marked at once (parallel to Phase 5b §7.7 multi-GEN
  IV-BEN). Not seeded; the 2-arg shape covers the common cases.
- **Other ipang- senses.** ``pang-`` also forms purpose nominals
  (``pambili`` "for buying / shopping") and abilitative-like
  derivations. Only the instrumental applicative IV reading is
  seeded here.
- **AV instrumental ``mang-`` retain readings.** Some bases
  admit a retain-pattern AV variant alongside the drop variant
  (``mambili`` retain vs ``mamili`` drop). The drop pattern is
  the documented default; retain readings would need per-base
  flagging. Deferred.

## Phase 5c §7.6 follow-on: raising verbs

**Date:** 2026-05-01. **Status:** active. Lifts the §7.6
"Raising deferred" item: ``mukha`` "seem" and ``baka`` "might"
now parse with structure-shared SUBJ between matrix and
embedded XCOMP.

### Three pieces

**(a) PRED-template extension for non-thematic args.**
:class:`tgllfg.fstruct.checks.PredTemplate` gains separate
``thematic`` and ``non_thematic`` tuples; ``governables``
remains the canonical union (used by completeness / coherence).
The parser :func:`parse_pred_template` recognises trailing
non-thematic args after the closing ``>``:

```text
SEEM <XCOMP> SUBJ      → thematic=("XCOMP",) non_thematic=("SUBJ",)
EAT <SUBJ, OBJ>        → thematic=("SUBJ","OBJ") non_thematic=()  (existing case)
RAIN <> SUBJ           → thematic=() non_thematic=("SUBJ",)        (0-thematic future-proofing)
```

The completeness check (:func:`_check_completeness`) iterates
over ``governables`` so non-thematic args are required just like
thematic ones. The coherence check (:func:`_check_coherence`)
allows them by membership in the same union. Subject Condition
fires unchanged (still requires SUBJ if any args).

**(b) ``CTRL_CLASS=RAISING`` lex entries.** ``mukha`` and
``baka`` are seeded under :file:`data/tgl/particles.yaml` as
closed-class, uninflected pseudo-verbs (mirroring the §7.6
psych control entries). Lex entries in :data:`tgllfg.lexicon.BASE`:

```text
SEEM <XCOMP> SUBJ      mukha   a_structure=[COMPLEMENT]
MIGHT <XCOMP> SUBJ     baka    a_structure=[COMPLEMENT]
```

Only one thematic role (COMPLEMENT, the proposition) — SUBJ is
non-thematic and bears no theta role. The matching intrinsic
profile ``_RAISING`` has the single COMPLEMENT entry with
``(None, None)`` (XCOMP-stipulated, off the truth table).

**(c) Grammar wrap rule.** A new pattern in
:file:`src/tgllfg/cfg/control.py`:

```text
S → V[CTRL_CLASS=RAISING] PART[LINK=…] S
   (↑ XCOMP) = ↓3
   (↑ SUBJ) = (↑ XCOMP SUBJ)
```

The right-hand S is a complete embedded clause (with its own
SUBJ — distinct from the control case where the embedded clause
has a SUBJ-gap inside ``S_XCOMP``). The raising binding
``(↑ SUBJ) = (↑ XCOMP SUBJ)`` lifts the embedded SUBJ to the
matrix.

### Disambiguation by syntactic position

Both surfaces are also nouns (``mukha`` "face", ``baka`` "cow",
the latter pre-existing in :file:`data/tgl/nouns.yaml`; ``mukha``
added alongside Commit 5). The morph analyzer returns both
candidates per token. The grammar's wrap-rule pattern is
distinctive: it requires a ``V[CTRL_CLASS=RAISING]`` token in
clause-initial position followed by a linker plus an embedded
S. The noun reading has no syntactic place to fit when this
pattern matches; conversely, when the surface appears mid-clause
(``Kumain ang baka`` "the cow ate"), the verb reading has no
wrap rule to apply to and the noun reading wins. No pre-parse
disambiguation is needed.

### LMT bridge: non-thematic SUBJ added to expected GFs

:func:`tgllfg.lmt.lmt_check` now consults the lex entry's PRED
template and unions the non-thematic args into ``expected_gfs``
before the actual-vs-expected comparison. The BK engine maps
only thematic roles, so without this addition raising verbs would
fire a spurious ``lmt-mismatch`` (engine produces ``{XCOMP}``
but f-structure has ``{XCOMP, SUBJ}``).

### Coexistence with control

Raising and control structures share the matrix wrap-rule shape
(matrix V + linker + embedded clause) but differ in two ways:

1. The embedded clause: control uses ``S_XCOMP`` (SUBJ-gap);
   raising uses full ``S`` (overt SUBJ).
2. The matrix SUBJ: control's matrix SUBJ comes from a thematic
   role (mapped via LMT); raising's matrix SUBJ is non-thematic
   and structure-shared with embedded SUBJ.

The grammar uses ``CTRL_CLASS`` as the discriminating feature so
control and raising rules don't accidentally cross-fire.

### Sentences enabled

```text
Mukhang kumakain ang bata.            — "the child seems to be eating"
Mukhang kumain ang bata.               (PFV embedded)
Mukhang kinakain ng aso ang isda.     — OV embedded; matrix.SUBJ = isda
Mukhang kumakain ang bata ng isda.    — embedded AV transitive with OBJ
Mukhang hindi kumakain ang bata.      — inner negation in XCOMP
Bakang umuwi ang bata.                — "the child might leave"
```

### Out-of-scope (still deferred)

- **Raising chains** (raising matrix embedding another raising
  matrix — ``Mukhang bakang umuwi ang bata``). The wrap rule's
  right-hand S admits any complete clause, so this should
  technically work; not exercised by the corpus and not
  separately tested.
- **Other raising verbs.** Tagalog has a small closed class —
  ``parang``, ``tila``, ``yata`` are also raising-like. Only
  ``mukha`` and ``baka`` are seeded.
- **Raising under control** (a control verb embedding a raising
  matrix). The infrastructure composes, but the construction
  isn't exercised.

## Phase 5c §8 follow-on: multi-OBL semantic disambiguation

**Date:** 2026-05-01. **Status:** active. Lifts the §8 deferral
"Multi-OBL semantic disambiguation": when two ``OBL-θ`` roles
compete for two sa-NPs, the classifier now prefers a lemma-class
match before falling back to positional order. ``Nagbigay ang
nanay ng libro sa eskwela sa bata`` (LOC-RECIP surface order)
gets the same f-structure as ``Nagbigay ang nanay ng libro sa
bata sa eskwela`` (RECIP-LOC order): bata ends up in
``OBL-RECIP``, eskwela in ``OBL-LOC``.

### LEMMA percolation through the noun lex

The noun analyzer was previously hardcoded to construct
``MorphAnalysis(feats={})`` — discarding any per-root features
that nouns might declare. Phase 5c changes this to
``MorphAnalysis(feats={**r.feats, "LEMMA": r.citation})`` so
every noun's MorphAnalysis carries its citation form as
``LEMMA`` (always set), plus any extra ``feats`` declared on
the root.

The grammar's ``N → NOUN`` rule gains
``(↑ LEMMA) = ↓1 LEMMA``; the per-case ``NP[CASE=X] → DET/ADP[…]
N`` rules gain ``(↑ LEMMA) = ↓2 LEMMA``. As a result, every
NP-projection's f-structure now has a ``LEMMA`` attribute
identifying its head noun.

### Lemma-keyed semantic classification

The classifier consults two small tables in
:mod:`tgllfg.lmt.oblique_classifier`:

```python
_PLACE_LEMMAS = {"palengke", "eskwela", "bahay", "simbahan",
                 "tindahan", "parke"}
_ANIMATE_LEMMAS = {"bata", "nanay", "tatay", "lalaki", "babae",
                   "anak", "kapatid", "kaibigan", "tao", ...}
```

The helper ``_semantic_class(np)`` reads ``np.feats["LEMMA"]``
and returns ``"PLACE"``, ``"ANIMATE"``, or ``None`` (unknown).
``_gf_prefers_class(gf)`` maps ``OBL-LOC`` / ``OBL-GOAL`` →
PLACE, ``OBL-RECIP`` / ``OBL-BEN`` → ANIMATE, others → None
(positional only).

### Greedy match with positional fallback

When two or more ``OBL-θ`` roles and two or more sa-NPs are
present, the classifier walks roles in a-structure order:

1. For each role with a semantic preference: find the first
   un-consumed sa-NP whose class matches; assign and consume.
   If no match, defer the role to the positional pass.
2. Positional pass: walk remaining sa-NPs in id order,
   assigning to deferred roles in their a-structure order.

This means: when classes match cleanly, semantic order wins
regardless of surface position. When classes don't match
(e.g., two PLACE sa-NPs vying for OBL-LOC + OBL-GOAL),
positional fills the slots — which is the right fallback since
without semantic distinguishability we can't do better.

### Recursive multi-DAT not chosen; per-frame multi-DAT instead

A natural-looking option was a recursive ``S → S NP[CASE=DAT]``
rule that would let any clause take arbitrary trailing sa-NPs.
This was tried but produces duplicate parses for single-sa-NP
sentences (the recursive rule overlaps the per-frame rules).
Phase 5c instead adds explicit ``V[VOICE=AV] NP[NOM] NP[GEN]
NP[DAT] NP[DAT]`` (and the GEN-NOM permutation) so the new
``GIVE`` ditransitive lex entry has a grammar slot to attach to
without rule conflicts elsewhere.

### Sample lex entry: bigay AV ditransitive

```text
GIVE <SUBJ, OBJ, OBL-RECIP, OBL-LOC>
  a_structure = [AGENT, THEME, RECIPIENT, LOCATION]
  intrinsic   = AGENT  (False, False)   → SUBJ
                THEME  (False, True)    → OBJ
                RECIPIENT (True, False) → OBL-RECIP
                LOCATION  (True, False) → OBL-LOC
```

Two OBL-θ slots; the classifier disambiguates the two trailing
sa-NPs.

### Out-of-scope (still deferred)

- **Richer noun ontology.** The seed lemma tables are
  intentionally small (a dozen entries each). Real disambiguation
  for an open-domain corpus would consult a richer noun
  semantics resource.
- **Case-by-case override.** No mechanism for a lex entry to
  override the classifier's preferences (e.g., a verb whose
  ``OBL-RECIP`` semantically prefers PLACE rather than
  ANIMATE — rare but possible).
- **Three-or-more sa-NPs in one clause.** Tagalog rarely
  sustains more than two sa-NPs at the matrix level; not
  exercised by the corpus.

## Phase 5d Commit 1: parang / tila — bare-raising verbs

**Date:** 2026-05-01. **Status:** active. Extends the §7.6
raising work with two more evidential raising verbs that don't
take a linker between V and the embedded clause.

### Linker-taking vs bare-raising split

Phase 5c Commit 5's raising verbs (``mukha``, ``baka``) take a
bound `-ng` linker (``Mukhang kumakain ang bata`` —
``mukha + -ng + S``). Phase 5d's two new verbs are surface-
adjacent to the embedded S without any linker:

```text
Parang kumakain ang bata.   "the child seems to be eating"
Tila kumakain ang bata.     "the child apparently is eating"
```

The standard Tagalog form has no `-ng` after ``parang`` or
``tila``; some dialect / register variation exists, but the
linker-less pattern is the dominant usage.

### CTRL_CLASS split prevents cross-firing

The naive approach — keep ``CTRL_CLASS=RAISING`` for all four
verbs and add a no-linker wrap rule alongside the existing
linked rule — produces a duplicate parse on ``mukhang`` /
``bakang`` sentences. Root cause: the ``S → PART[POLARITY=NEG]
S`` negation rule's ``PART[POLARITY=NEG]`` constraint matches
the linker `-ng` (which has ``LINK=NG`` but no ``POLARITY``)
under the parser's non-conflict feature matcher. With both a
linked and a bare raising rule, both derivations succeed and
produce identical f-structures.

To prevent the cross-firing, ``parang`` and ``tila`` carry
``CTRL_CLASS=RAISING_BARE`` instead of ``CTRL_CLASS=RAISING``.
The new wrap rule constrains the V to ``RAISING_BARE``
specifically:

```text
S → V[CTRL_CLASS=RAISING_BARE] S
   (↑ XCOMP) = ↓2
   (↑ SUBJ) = (↑ XCOMP SUBJ)
```

The existing ``CTRL_CLASS=RAISING`` linked rule is unchanged.
``mukha`` / ``baka`` keep ``RAISING``; ``parang`` / ``tila``
get ``RAISING_BARE``. No cross-firing, no duplicate parses.

### Lex entries

```text
parang : SEEMS-LIKE  <XCOMP> SUBJ   CTRL_CLASS=RAISING_BARE
tila   : APPARENTLY  <XCOMP> SUBJ   CTRL_CLASS=RAISING_BARE
```

Same intrinsic profile as ``mukha`` / ``baka``
(``_RAISING`` — only COMPLEMENT thematic role; SUBJ
non-thematic via the PRED template's post-`>` arg).

### ``yata`` is NOT a raising verb here

The third deferred raising-like word, ``yata`` "supposedly", was
called out in the Phase 5c §7.6 deferral list. It is not added
as a raising verb in Phase 5d: ``yata`` is already analyzed as
a Wackernagel 2P clitic (``EPISTEMIC=PRESUMABLY``,
``is_clitic=true``, ``CLITIC_CLASS=2P``). Its surface
distribution patterns with enclitic adverbs, not with
clause-initial verbs. Treating it as a raising verb would
duplicate analyses and break the §7.3 clitic-placement pass.

### Out-of-scope (still deferred)

- **Comparative ``parang``** ("X is like Y"). The existing
  raising entry covers the evidential reading
  (``parang + clause``). The comparative reading
  (``parang + NP``) is structurally distinct and needs a
  separate grammar rule. Deferred until corpus pressure shows
  comparative coverage matters.
- **Linker-optional ``parang``** dialect form (``Parang
  umuulan`` vs ``Parang ng umuulan`` — the latter is
  non-standard but attested). Single-form-per-verb is the
  current commitment.

## Phase 5d Commit 2: pa-...-an DV causative

**Date:** 2026-05-01. **Status:** active. Lifts the §7.7
deferral of "``pa-...-an`` DV causative and other less-common
causative variants" (the half left after Phase 5c Commit 4
lifted ``ipang-`` / ``ika-``). Surface forms like
``pinakainan`` "fed-at" / "fed-to" now parse with a typed
``CAUSE-EAT-AT <SUBJ, OBJ-CAUSER>`` PRED.

### Three pa_an DV cells

Parametrically identical to the existing pa-...-in OV cells
with ``-an`` substituted for ``-in`` in the suffix slot:

```text
PFV   pa-…-an  prefix("pa") → infix("in") → suffix("an")
                ⇒ pinakainan, pinabasahan, pinainuman
IPFV  pa-…-an  cv_redup → prefix("pa") → infix("in") → suffix("an")
                ⇒ pinakakainan, pinababasahan, pinaiinuman
CTPL  pa-…-an  cv_redup → prefix("pa") → suffix("an")  (no -in- infix)
                ⇒ pakakainan, pababasahan, paiinuman
```

The existing sandhi (vowel-hiatus h-epenthesis on
``basa+an → basahan``; high-vowel-style alternation on
``inom+an → inuman``) cascades through unchanged.

### Voice rule split: DV gets a CAUS=DIRECT variant

The existing voice_specs entry for plain DV (``("DV",
"OBJ-AGENT", [])``) had no CAUS constraint, which would let it
cross-fire on the new DV CAUS=DIRECT forms. Phase 5d Commit 2
gives DV the same CAUS-discriminated split that OV already
had:

```python
voice_specs = [
    ("AV", "OBJ", []),
    ("OV", "OBJ-AGENT", [("CAUS", "NONE")]),
    ("OV", "OBJ-CAUSER", [("CAUS", "DIRECT")]),
    ("DV", "OBJ-AGENT", [("CAUS", "NONE")]),    # plain DV (was no constraint)
    ("DV", "OBJ-CAUSER", [("CAUS", "DIRECT")]), # NEW: pa-DV
    ("IV", "OBJ-AGENT", []),
]
```

The plain-DV constraint addition prevents pa-DV forms from
spuriously firing the OBJ-AGENT-binding plain-DV rule. Existing
plain-DV tests (``Sinulatan ng bata ang nanay``) continue to
parse against the now-constrained rule.

### Lex entries: 2-arg pivot-rotation profile

```text
kain DV CAUS=DIRECT : CAUSE-EAT-AT   <SUBJ, OBJ-CAUSER>
basa DV CAUS=DIRECT : CAUSE-READ-AT  <SUBJ, OBJ-CAUSER>
inom DV CAUS=DIRECT : CAUSE-DRINK-AT <SUBJ, OBJ-CAUSER>
```

Intrinsic profile ``_DV_CAUS_DIRECT``:

- ``CAUSER (True, True)`` → ``OBJ-CAUSER`` (typed [+r, +o])
- ``LOCATION (False, False)`` → ``SUBJ`` (the pivot, [-r, -o])

The role label is ``LOCATION`` because Tagalog's DV subsumes
locative + recipient + dative under one voice. For ``Pinakainan
ng nanay ang bata``, the pivot ``bata`` is read as a recipient
rather than a strict location — both fit under DV's umbrella.

### Multi-arg variants out of scope

Three-argument pa-DV with explicit PATIENT (parallel to
Phase 5b's pa-OV-direct three-arg) is not seeded; the 2-arg
shape covers the canonical recipient-pivot reading. The
infrastructure (multi-GEN-NP grammar rules) exists if a future
corpus requires it.

### Sentences enabled

```text
Pinakainan ng nanay ang bata.    "mother fed the child"
Pinabasahan ng nanay ang bata.   "mother read [aloud] to the child"
Pinainuman ng nanay ang bata.    "mother gave the child a drink"
Pinakakainan ng nanay ang bata.  IPFV
Pakakainan ng nanay ang bata.    CTPL
```

### Out-of-scope (still deferred)

- **Three-argument pa-DV** (with overt PATIENT alongside
  CAUSER and LOCATION/RECIPIENT). Multi-GEN-NP DV variants
  parallel Phase 5b's pa-OV-direct three-arg pattern; not
  exercised by the current corpus.
- **Other less-common causative variants** (``ka-...-an``
  reciprocal, ``magpa-...-an`` distributive, etc.). The
  §7.7 plan mentioned "pa-...-an and other less-common
  causative variants"; the others remain deferred.

## Phase 5d Commit 3: post-modifier demonstrative with linker

**Date:** 2026-05-01. **Status:** active. Lifts the §7.8
deferral on "Standalone demonstrative-as-modifier with linker"
noted in `docs/coverage.md`. Sentences like ``Kumain ang
batang ito`` ("this child ate") now parse with the
demonstrative's deixis percolated to the matrix NP's
f-structure.

### Six grammar rules (3 cases × 2 linker variants)

```text
NP[CASE=NOM] → NP[CASE=NOM] PART[LINK=…] DET[CASE=NOM, DEM=YES]
NP[CASE=GEN] → NP[CASE=GEN] PART[LINK=…] ADP[CASE=GEN, DEM=YES]
NP[CASE=DAT] → NP[CASE=DAT] PART[LINK=…] ADP[CASE=DAT, DEM=YES]
```

The demonstrative agrees in case with the head NP. NOM-marked
demonstratives are ``DET`` (``ito``, ``iyan``, ``iyon``);
GEN-marked are ``ADP`` (``nito``, ``niyan``, ``niyon``);
DAT-marked are ``ADP`` (``dito``, ``diyan``, ``doon``). The
case-typed pattern in the rule's third child enforces
agreement at the parser level — cross-case combinations
(`ng batang ito` with NOM-dem after GEN-head) don't fire any
post-modifier rule and the dem reading is rejected.

### Equations: matrix shares head, DEIXIS percolates

```text
(↑) = ↓1                  -- head NP's f-structure becomes the matrix
(↑ DEIXIS) = ↓3 DEIXIS    -- copy deixis from the modifier
```

The PRED stays the head noun's PRED — the demonstrative
modifies, doesn't supplant. Compare with Phase 4 §7.8's
standalone-demonstrative rule, which uses ``(↑) = ↓1`` to
share with the demonstrative directly (no head noun) and adds
``(↑ PRED) = 'PRO'`` so completeness passes.

### Surface variants enabled

```text
ang batang ito       (NOM PROX)
ang batang iyan      (NOM MED)
ang batang iyon      (NOM DIST)
ng batang nito       (GEN PROX, in OV pivot or possessor)
ng batang niyon      (GEN DIST)
sa palengkeng dito   (DAT PROX)
sa palengkeng doon   (DAT DIST)
```

Multiple modifiers per clause compose freely
(``Kumain ang batang ito ng isdang niyan`` "this child ate
that fish").

### Out-of-scope (still deferred)

- **Pre-modifier demonstrative with linker** (``itong batang``
  "this child" — modifier-first variant). Tagalog admits both
  orders; only post-modifier is wired. Pre-modifier would need
  parallel rules in the reverse direction.
- **Demonstrative as modifier of a relativized head**
  (``ang batang ito na kumain`` "this child who ate"). The
  RC's linker would compete with the dem-modifier's linker;
  needs ranker-policy refinement.

## Phase 5d Commit 4: multi-GEN-NP IV-INSTR / IV-REASON

**Date:** 2026-05-01. **Status:** active. Lifts the §7.7
follow-on Out-of-scope item "Multi-GEN-NP IV-INSTR / IV-REASON
frames" left after Phase 5c Commit 4. Three-argument IV-INSTR /
IV-REASON sentences with overt PATIENT alongside AGENT and
INSTRUMENT/REASON now parse with typed OBJ-AGENT and
OBJ-PATIENT slots.

### Lex-only commit (no grammar change)

The Phase 5b multi-GEN-NP rules in :file:`cfg/clause.py` are
voice-restricted to ``V[VOICE=IV]`` without an APPL constraint:

```text
S → V[VOICE=IV] NP[CASE=NOM] NP[CASE=GEN] NP[CASE=GEN]
   (↑ SUBJ) = ↓2
   (↑ OBJ-AGENT) = ↓3
   (↑ OBJ-PATIENT) = ↓4
```

(Plus two permutations: GEN-NOM-GEN and GEN-GEN-NOM.) These
rules fire for IV-INSTR (``APPL=INSTR``) and IV-REASON
(``APPL=REASON``) verbs alongside IV-BEN (``APPL=BEN``) — no
new grammar rules needed. Phase 5d Commit 4 is a lex-only
extension: four new 3-arg lex entries plus two new intrinsic
profiles.

### Two new intrinsic profiles

```python
_IV_INSTR_AGENT_PATIENT_INSTRUMENT = {
    "AGENT":      (True, True),    # → OBJ-AGENT
    "PATIENT":    (True, True),    # → OBJ-PATIENT
    "INSTRUMENT": (False, False),  # → SUBJ (pivot)
}
_IV_REASON_AGENT_PATIENT_REASON = {
    "AGENT":   (True, True),
    "PATIENT": (True, True),
    "REASON":  (False, False),
}
```

Both AGENT and PATIENT are [+r, +o] → typed OBJ-θ, parallel to
Phase 5b's IV-BEN three-arg pattern.

### Four new lex entries

```text
bili IV-INSTR  : BUY-WITH        <SUBJ, OBJ-AGENT, OBJ-PATIENT>
tahi IV-INSTR  : SEW-WITH        <SUBJ, OBJ-AGENT, OBJ-PATIENT>
kain IV-REASON : EAT-FOR-REASON  <SUBJ, OBJ-AGENT, OBJ-PATIENT>
sulat IV-REASON: WRITE-FOR-REASON <SUBJ, OBJ-AGENT, OBJ-PATIENT>
```

The 2-arg variants from Phase 5c Commit 4 are unchanged; both
forms coexist in BASE. The lex entry that matches a given parse
is determined by NP count:

- 2 NPs (1 ng-NP + 1 ang-NP) → 2-arg PRED
- 3 NPs (2 ng-NPs + 1 ang-NP) → 3-arg PRED via multi-GEN

### Sentences enabled

```text
Ipinambili ng nanay ng isda ang pera.
  "money is what mother bought (fish) with"
  AGENT=nanay, PATIENT=isda, INSTRUMENT=pera (pivot)

Ipinantahi ng nanay ng isda ang karayom.
  "needle is what mother sewed (fish) with"

Ikinakain ng bata ng isda ang gutom.
  "hunger is the reason the child ate fish"

Ikinasulat ng bata ng isda ang gutom.
  "hunger is the reason the child wrote (about) fish"
```

### Structural ambiguity (expected)

Each 3-NP sentence admits at least one structural ambiguity:
``ng nanay ng isda`` could be parsed as a possessive ("mother's
fish") via the existing NP-internal possessive rule, with the
whole construct as a single GEN-NP filling OBJ-AGENT in the
2-arg lex. Both parses surface in the n-best output. The tests
assert AT LEAST ONE parse has the multi-GEN-binding structure,
mirroring Phase 5b's IV-BEN ambiguity handling.

### Out-of-scope (still deferred)

- **DV three-argument constructions.** Phase 5b's
  multi-GEN rules are IV-only. DV multi-GEN
  (``Sinulatan ng nanay ng letra ang anak``
  "mother wrote (a letter) to the child") would need
  parallel DV multi-GEN rules. Not exercised by corpus.
- **Multi-GEN-NP under embedded control.** Crosses with
  Phase 5c Commits 1 / 3; tracked separately as a §9.1 item
  (Phase 5d Commit 9 in the proposed ordering).

## Phase 5d Commit 5: non-pivot ay-fronting

**Date:** 2026-05-01. **Status:** active.

Phase 4 §7.4 admitted only SUBJ-pivot ay-fronting via the wrap rule
``S → NP[CASE=NOM] PART[LINK=AY] S_GAP``. The §7.4 "Out-of-scope"
section explicitly listed non-pivot ay-fronting (``Kanya ay binili
ang aklat``, ``Sa bahay ay kumain si Maria``) as deferred to §7.8.
Phase 5d Commit 5 lifts that deferral.

S&O 1972 §6 and Kroeger 1993 describe topicalization-style
ay-fronting of:

- **OBJ-θ in any voice** (the ``ng``-marked non-pivot in AV, or
  the ``ng``-marked actor in non-AV).
- **DAT-marked obliques** (locatives, recipients,
  beneficiaries — the ``sa``-NP).

The fronted phrase carries its case marker into clause-initial
position; the inner clause has a gap at the position the phrase
came from.

### Three new gap-category non-terminals

The Phase 4 design used a single ``S_GAP`` non-terminal whose
binding equation is ``(↑ SUBJ) = (↑ REL-PRO)``. To extend to
non-SUBJ extraction we add three new non-terminals paralleling
``S_GAP``, each with its own binding to a different inner-clause GF
(or set, for OBL):

```text
S_GAP_OBJ → V[VOICE=AV] NP[CASE=NOM]
   (↑ SUBJ) = ↓2
   (↑ OBJ) = (↑ REL-PRO)

S_GAP_OBJ_AGENT → V[VOICE=OV, CAUS=NONE] NP[CASE=NOM]
   (↑ SUBJ) = ↓2
   (↑ OBJ-AGENT) = (↑ REL-PRO)
   (DV / IV variants parallel)

S_GAP_OBL → V[VOICE=AV] NP[CASE=NOM] NP[CASE=GEN]
   (↑ SUBJ) = ↓2
   (↑ OBJ) = ↓3
   (↑ REL-PRO) ∈ (↑ ADJUNCT)
   (with-DAT and non-AV variants parallel)
```

Each gap-category also has a ``PART[POLARITY=NEG]`` recursion to
allow ``Ng isda ay hindi kumain si Maria`` and similar negated
fronted constructions.

The voice / feature constraints on each frame's V token follow the
existing ``S_GAP`` pattern: OV / DV require ``CAUS=NONE`` to keep
pa-OV / pa-DV (CAUS=DIRECT) out of the actor-extraction path, where
the typed OBJ-θ slot would be ``OBJ-CAUSER`` rather than
``OBJ-AGENT``. IV is admitted without an APPL constraint so any
applicative variant (CONVEY / INSTR / REASON) can have its actor
fronted.

### Three new wrap rules

```text
S → NP[CASE=GEN] PART[LINK=AY] S_GAP_OBJ
S → NP[CASE=GEN] PART[LINK=AY] S_GAP_OBJ_AGENT
S → NP[CASE=DAT] PART[LINK=AY] S_GAP_OBL
```

Each wrap rule mirrors the existing SUBJ-fronting rule's shape:
``(↑) = ↓3`` shares the matrix and inner f-structures, ``(↑ TOPIC)
= ↓1`` overlays the topic, and ``(↓3 REL-PRO) = ↓1`` makes the
fronted NP fill REL-PRO. The case-marker contrast on the fronted
NP (NOM vs GEN vs DAT) plus the inner V's voice / features
disambiguate which gap-category the parser uses, with no spurious
cross-firing.

The OBJ and OBJ-AGENT wrap rules carry constraining equations
``(↓3 REL-PRO) =c (↓3 OBJ)`` / ``(↓3 REL-PRO) =c (↓3 OBJ-AGENT)``
mirroring the SUBJ-fronting rule's vacuous-but-symmetry-preserving
constraint. The OBL wrap rule omits the constraining equation
because ADJUNCT is a set, not a scalar GF.

### What this lifts

- AV OBJ-fronting: ``Ng isda ay kumain si Maria`` (eat-AV with
  OBJ topicalized).
- Non-AV OBJ-AGENT-fronting: ``Ni Maria ay kinain ang isda``
  (eat-OV with actor topicalized); ditto for DV (``Ng bata ay
  kinainan ang nanay``) and IV (CONVEY / INSTR / REASON variants).
- DAT OBL-fronting: ``Sa bahay ay kumain si Maria``,
  ``Sa bahay ay kinain ni Maria ang isda``.
- Negation under fronting (each gap-category recurses through
  ``PART[POLARITY=NEG]``).

### Out-of-scope (still deferred)

- **Multi-GEN-NP ay-fronting.** Phase 5b multi-GEN constructions
  (IV-BEN three-arg, pa-OV-direct three-arg) have two GEN-NPs
  filling typed OBJ-AGENT and OBJ-PATIENT positionally. Fronting
  one of the two would require a different gap shape — the
  remaining GEN-NP's binding is no longer purely positional. Not
  exercised by corpus.
- **AdvP / PP fronting.** ``Kahapon ay tumakbo si Maria``
  (temporal AdvP), ``Para sa bata ay binili niya ang aklat``
  (PP). Out of scope until the categorial inventory expands
  (§7.8 / Phase 6).
- **Pa-OV (CAUS=DIRECT) actor-fronting.** Would need a parallel
  ``S_GAP_OBJ_CAUSER`` non-terminal. Skipped to keep the commit
  small; trivially additive when needed.

## Phase 5d Commit 6: possessive-linker RC variant

**Date:** 2026-05-01. **Status:** active.

The Phase 4 §7.5 relativization rule
(``NP[CASE=X] → NP[CASE=X] PART[LINK=NA|NG] S_GAP``) handles the
canonical form ``aklat na binasa ko`` ("the book that I read"),
where the actor stays inside the RC as a GEN-NP. Tagalog has a
stylistic variant where the pronominal actor is hoisted out of the
RC and surfaces as a possessor of the head NP, joined by the bound
``-ng`` linker:

```text
aklat   ko       -ng        binasa
head    POSS     LINK=NG    RC-V (no overt actor)
        = RC's OBJ-AGENT
```

The pronoun plays a dual role: head-NP possessor *and* RC actor.
Phase 5d Commit 6 admits this form with three additive pieces.

### Pre-parse: keep PRON adjacent to its bound linker

:func:`tgllfg.text.split_linker_ng` separates ``kong`` / ``mong``
/ ``niyang`` into ``ko`` / ``mo`` / ``niya`` (PRON) plus a
synthetic ``-ng`` (PART). The §7.3 Wackernagel pass would
otherwise hoist the PRON into the post-V cluster, leaving the
``-ng`` linker orphaned. A new helper
:func:`tgllfg.clitics.placement._is_pre_linker_pron` detects a
PRON-clitic immediately followed by a ``LINK=NG`` PART and skips
the move — alongside the existing
:func:`_is_post_noun_pron` check from Phase 5c §7.8.

### Grammar: S_GAP_NA (no-overt-actor)

A new gap-category for SUBJ-gapped non-AV verbs without an overt
GEN-NP actor:

```text
S_GAP_NA → V[VOICE=OV, CAUS=NONE]                  (1)
S_GAP_NA → V[VOICE=OV, CAUS=NONE] NP[CASE=DAT]     (1+adjunct)
S_GAP_NA → V[VOICE=DV, CAUS=NONE]                  (parallel)
S_GAP_NA → V[VOICE=IV]                             (parallel)
S_GAP_NA → PART[POLARITY=NEG] S_GAP_NA             (negation)
```

Each frame binds ``(↑ SUBJ) = (↑ REL-PRO)`` like the original
``S_GAP``. The actor (``OBJ-AGENT``) is left unbound at this level
— the wrap rule supplies it externally.

The voice / feature constraints follow ``S_GAP``: OV / DV require
``CAUS=NONE`` to keep pa-OV / pa-DV out of the actor-extraction
path; IV is admitted without an APPL constraint so any IV
applicative can host the construction.

### Grammar: possessive-linker wrap rule

```text
NP[CASE=X] → NP[CASE=X] PRON[CASE=GEN] PART[LINK=NG] S_GAP_NA
   (↑) = ↓1
   (↑ POSS) = ↓2
   ↓4 ∈ (↑ ADJ)
   (↓4 OBJ-AGENT) = ↓2
   (↓4 REL-PRO PRED) = (↓1 PRED)
   (↓4 REL-PRO CASE) = (↓1 CASE)
   (↓4 REL-PRO) =c (↓4 SUBJ)
```

The dual-binding equations ``(↑ POSS) = ↓2`` and ``(↓4 OBJ-AGENT)
= ↓2`` make the head NP's possessor *the same f-structure* as the
RC's actor — id-identity, not just feature-equality. REL-PRO
sharing follows the standard relativization pattern (anaphoric:
PRED + CASE atomic-path copies).

Three head-case variants (NOM / GEN / DAT) cover the construction
in any NP position. PRON-only (not GEN-NP-only) restricts the
match to pronominal possessors — non-pronominal genitives fall
through to the standard relativization analysis.

### What this lifts

- ``Lumakad ang bata kong kinain.`` — possessive-linker RC in SUBJ
  position with 1SG ``ko``.
- ``Kumain ang bata ng libro kong binasa.`` — possessive-linker RC
  in OBJ position.
- All three vowel-final GEN pronouns: ``ko`` (1SG), ``mo`` (2SG),
  ``niya`` (3SG).
- OV / IV verbs in the RC; DV variants follow the same shape.
- Negation under the construction
  (``Lumakad ang bata kong hindi kinain.``).

### Out-of-scope (still deferred)

- **Consonant-final pronouns** with the standalone ``na`` linker
  (``aklat namin na binasa`` "the book that we read", with 1PL.EXCL
  ``namin``). The current commit handles only ``-ng`` (vowel-final
  PRON + bound linker). A parallel rule with ``PART[LINK=NA]``
  would be additive.
- **Non-pronominal possessors with linker** (``aklat ng batang
  binasa`` analogue). Surface-ambiguous with the existing standard
  relativization plus possessive parses; not pursued in this
  commit.

## Phase 5d Commit 7: raising chains + raising under control

**Date:** 2026-05-01. **Status:** active.

Two related constructions that compose existing infrastructure
rather than introducing new analytical commitments. The Phase 5c
§7.6 follow-on Commit 5 introduced raising verbs at the ``S`` level
(``S → V[CTRL_CLASS=RAISING] PART[LINK] S`` and the bare-RAISING
variant); Phase 5d Commit 1 added two more bare-raising lex entries
(parang / tila). With those rules in place:

### Raising chains compose for free

A raising matrix can embed another raising clause because the
existing rules accept any ``S`` as the embedded clause — including
another raising-S. SUBJ structure-shares through every layer via
the ``(↑ SUBJ) = (↑ XCOMP SUBJ)`` equation:

```text
Mukhang bakang kumakain ang bata.   "It seems the child might be eating."
=  S[SEEM]
     XCOMP = S[MIGHT]
                XCOMP = S[EAT]
                          SUBJ = bata
                MIGHT.SUBJ === bata
     SEEM.SUBJ === MIGHT.SUBJ === bata
```

All four chain shapes work uniformly: linked-linked
(mukha + baka), linked-bare (mukha + parang), bare-linked
(parang + mukha), bare-bare (parang + tila). No grammar change
needed — Commit 7 only adds tests that pin the behaviour.

### Raising under control needs new S_XCOMP variants

Control verbs require an ``S_XCOMP`` complement (SUBJ-gapped). The
Phase 5c raising rules sit at ``S`` only, so a sentence like
``Gusto kong mukhang kumakain`` ("I want to seem to be eating") had
0 parses — there was no ``S_XCOMP`` rule that could host the
mukhang+inner-clause shape.

Commit 7 adds ``S_XCOMP``-level raising rules paralleling the
``S`` ones:

```text
S_XCOMP → V[CTRL_CLASS=RAISING] PART[LINK=NA|NG] S_XCOMP
   (↑ XCOMP) = ↓3
   (↑ SUBJ) = (↑ XCOMP SUBJ)        — raising structure-share
   (↑ SUBJ) = (↑ REL-PRO)           — S_XCOMP convention

S_XCOMP → V[CTRL_CLASS=RAISING_BARE] S_XCOMP
   (↑ XCOMP) = ↓2
   (↑ SUBJ) = (↑ XCOMP SUBJ)
   (↑ SUBJ) = (↑ REL-PRO)
```

The three identifications at this level — ``XCOMP``, raising
structure-share, and ``REL-PRO`` = ``SUBJ`` — compose so that the
matrix control wrap rule's ``(↑ SUBJ) = (↑ XCOMP REL-PRO)``
propagates the controller through the raising chain into the
innermost action's SUBJ. The chain composes naturally because
``S_XCOMP`` recurses through itself: a raising-S_XCOMP can embed
another raising-S_XCOMP (chain-under-control case).

### What this lifts

- Raising chains: 5 variants (linked-linked, linked-bare,
  bare-linked, bare-bare; both NA and NG linker variants where
  applicable).
- Raising under control: PSYCH (gusto / ayaw / kaya) and INTRANS
  (pumayag) with both linked and bare raising matrices.
- Raising chains under control: 4-level XCOMP (``Gusto kong
  mukhang bakang kumakain``) with all four SUBJ slots structurally
  identical (Python-id equality verified by tests).

### Out-of-scope (still deferred)

- **Control under raising.** A raising verb embedding a control
  matrix (``Mukhang gusto ng batang kumain`` "It seems the child
  wants to eat"). Composes via the existing ``S → V[RAISING] PART
  S`` rule with ``S`` being a control-S; needs no new rule but
  hasn't been pinned with tests in this commit.
- **TRANS control + raising.** ``Pinilit ng nanay ang batang
  mukhang umuwi`` is structurally available via
  ``V[CTRL_CLASS=TRANS] NP[GEN] NP[NOM] PART[LINK] S_XCOMP`` plus
  the new raising-S_XCOMP, but corpus exposure is low.

## Phase 5d Commit 8: pa-OV / pa-DV (CAUS=DIRECT) under control

**Date:** 2026-05-01. **Status:** active.

Phase 5c §7.6 follow-on Commit 1 added non-AV ``S_XCOMP`` rules
that route ``REL-PRO`` to ``OBJ-AGENT`` for OV / DV / IV embedded
clauses. Those rules deliberately required ``CAUS=NONE`` to keep
them out of the actor-extraction path for monoclausal direct
causatives, where the typed actor slot is ``OBJ-CAUSER`` rather
than ``OBJ-AGENT``. Phase 5d Commit 8 fills in the parallel
``CAUS=DIRECT`` variants.

### The pa-causative shape under control

In a monoclausal direct causative (Phase 4 §7.7 + Phase 5d Commit 2):

- ``OBJ-CAUSER`` — the agent / instigator (who causes the event).
- ``OBJ-PATIENT`` — the patient (in the 3-arg pa-OV form;
  optional in the 2-arg form and absent in pa-DV).
- ``SUBJ`` — the causee (pa-OV) or location/recipient (pa-DV).

Under control, the matrix verb's controller binds the embedded
``OBJ-CAUSER`` (the caused-event actor):

```text
Gusto niyang pakakainin ang bata.   "She wants to feed the child."
   gusto.SUBJ === XCOMP.OBJ-CAUSER  (id-equal)
   gusto.SUBJ.LEMMA = niya
   XCOMP.PRED      = CAUSE-EAT <SUBJ, OBJ-CAUSER>
   XCOMP.SUBJ      = bata           (the causee)
```

### Four new S_XCOMP rules

```text
S_XCOMP → V[VOICE=OV, CAUS=DIRECT] NP[CASE=NOM]
   (↑ SUBJ) = ↓2
   (↑ OBJ-CAUSER) = (↑ REL-PRO)             — 2-arg pa-OV

S_XCOMP → V[VOICE=OV, CAUS=DIRECT] NP[CASE=NOM] NP[CASE=GEN]
   (↑ SUBJ) = ↓2
   (↑ OBJ-PATIENT) = ↓3
   (↑ OBJ-CAUSER) = (↑ REL-PRO)             — 3-arg pa-OV (NOM-GEN)

S_XCOMP → V[VOICE=OV, CAUS=DIRECT] NP[CASE=GEN] NP[CASE=NOM]
   (↑ SUBJ) = ↓3
   (↑ OBJ-PATIENT) = ↓2
   (↑ OBJ-CAUSER) = (↑ REL-PRO)             — 3-arg pa-OV (GEN-NOM)

S_XCOMP → V[VOICE=DV, CAUS=DIRECT] NP[CASE=NOM]
   (↑ SUBJ) = ↓2
   (↑ OBJ-CAUSER) = (↑ REL-PRO)             — 2-arg pa-DV
```

The ``V[VOICE=X, CAUS=DIRECT]`` filter mirrors the existing top-
level pa-causative rules' filter (Phase 5b multi-GEN frames at
line 1255, voice_specs at line 1130) so the same lex entries fire
in both contexts.

### Embedded form selection

The embedded verb appears in the **CTPL** (contemplative) aspect,
not perfective: ``pakakainin`` (cv-redup + pa- + -in) per the
Phase 4 §7.7 paradigms.yaml ``pa_in`` cells. The matrix verb's
control wrap rule supplies the linker (``-ng`` after vowel-final
matrix V).

### What this lifts

- pa-OV under PSYCH control: ``Gusto niyang pakakainin ang bata``
  ("she wants to feed the child"); 3-arg variants with overt
  patient.
- pa-OV under INTRANS control: ``Pumayag siyang pakakainin ang
  bata``.
- pa-OV under TRANS control: ``Pinilit ng nanay ang batang
  pakakainin ang aso`` ("mom forced the child to feed the dog");
  the forcee (matrix.SUBJ) is the controller, NOT the forcer
  (matrix.OBJ-AGENT).
- pa-DV under PSYCH and INTRANS control.
- SUBJ control identity: the embedded ``OBJ-CAUSER`` is the same
  Python f-structure as the matrix controller — verified by
  Python-id equality in tests.

### Out-of-scope (still deferred)

- **3-arg pa-DV under control.** The Phase 5d Commit 2 pa-...-an
  cells are 2-arg only (``CAUSE-EAT-AT <SUBJ, OBJ-CAUSER>``); a
  3-arg pa-DV with overt patient would need a new lex profile,
  not just a new S_XCOMP rule.
- **Nested pa-causatives under control.** A pa-OV control
  complement embedding another control structure should compose
  via the existing nested-S_XCOMP rules (Phase 5c Commit 3) but
  hasn't been pinned with tests in this commit.

## Phase 5d Commit 9: IV applicative multi-GEN under control

**Date:** 2026-05-01. **Status:** active.

Phase 5b §7.7 follow-on lifted top-level multi-GEN-NP applicative
frames for IV-BEN; Phase 5c §7.7 / 5d Commit 4 added IV-INSTR /
IV-REASON 2-arg + 3-arg lex. All three live at the ``S`` level.
The Phase 5c §7.6 follow-on Commit 1 control complement
(``S_XCOMP``) IV variant had two limitations Commit 9 fixes:

### A. Drop APPL=CONVEY filter

The original 2-arg IV S_XCOMP rule was

```text
S_XCOMP → V[VOICE=IV, APPL=CONVEY] NP[CASE=NOM]
```

The ``APPL=CONVEY`` filter only matched the bare ``i-`` reading
(conveyance, e.g. ``ibibili`` "buy as conveyance"). The IV-BEN
(``ipag-``), IV-INSTR (``ipang-``), IV-REASON (``ika-``)
applicatives carry ``APPL=BEN`` / ``INSTR`` / ``REASON``
respectively, so the rule never fired for them. Commit 9 drops
the APPL filter:

```text
S_XCOMP → V[VOICE=IV] NP[CASE=NOM]
   (↑ SUBJ) = ↓2
   (↑ OBJ-AGENT) = (↑ REL-PRO)
```

The actor binds to ``OBJ-AGENT`` uniformly across all four IV
applicatives (Phase 5b OBJ-θ-in-grammar alignment), so a single
rule suffices. ``V[VOICE=IV]`` (no APPL) parallels the existing
top-level voice_specs / S_GAP entries which never had an APPL
filter.

### B. Add 3-arg IV under control

Phase 5b multi-GEN frames have three NPs at the top level
(pivot + AGENT + PATIENT). Under control the AGENT is the gap,
leaving SUBJ + GEN-PATIENT — a new shape Commit 9 admits in two
NP orders:

```text
S_XCOMP → V[VOICE=IV] NP[CASE=NOM] NP[CASE=GEN]
   (↑ SUBJ) = ↓2
   (↑ OBJ-PATIENT) = ↓3
   (↑ OBJ-AGENT) = (↑ REL-PRO)

S_XCOMP → V[VOICE=IV] NP[CASE=GEN] NP[CASE=NOM]
   (↑ SUBJ) = ↓3
   (↑ OBJ-PATIENT) = ↓2
   (↑ OBJ-AGENT) = (↑ REL-PRO)
```

Free post-V order parallels the top-level multi-GEN frames'
treatment.

### What this lifts

- IV-BEN under PSYCH / INTRANS / TRANS control: 2-arg
  (``Gusto kong ipaggagawa ang kapatid``) and 3-arg (``Gusto kong
  ipaggagawa ng silya ang kapatid``).
- IV-INSTR under control: 2-arg + 3-arg.
- IV-REASON 3-arg under PSYCH control (PFV form ``ikinakain``;
  the CTPL form ``ikakain`` resolves as IV-CONVEY in the current
  paradigms).
- SUBJ control identity verified by Python-id equality between
  matrix controller and embedded ``OBJ-AGENT``.

### Out-of-scope (still deferred)

- **IV-REASON CTPL paradigm gap.** The CTPL form ``ikakain``
  analyses as IV-CONVEY rather than IV-REASON in the current
  morph paradigms. Tests use the PFV form ``ikinakain`` to
  exercise IV-REASON 3-arg under control. Resolving the paradigm
  ambiguity would need a paradigms.yaml or analyzer change beyond
  Commit 9's scope.
- **IV multi-GEN under nested (long-distance) control.** The
  Phase 5c Commit 3 nested-S_XCOMP rules compose with the new
  3-arg IV S_XCOMP rule in principle but aren't pinned with
  tests in this commit.

## Phase 5d Commit 10: pronominal RC-actor (in-place Wackernagel)

**Date:** 2026-05-01. **Status:** active.

Phase 4 §7.5 admits standard relativization (``ang batang kinain
ng aso``) via ``NP[CASE=X] → NP[CASE=X] PART[LINK=NA|NG] S_GAP``.
The S_GAP frame for non-AV transitive (``V[VOICE=X] NP[CASE=GEN]``)
embeds the actor as a GEN-NP after the V. When the actor is
pronominal — ``ko`` / ``mo`` / ``niya`` — the §7.3 Wackernagel
pass would historically hoist the pronoun into the matrix V's
post-V cluster, leaving the OV S_GAP frame without its required
GEN-NP and breaking the parse:

```text
Tumakbo ang batang kinain ko    ("the child I-ate ran")
   pre-reorder:  takbo ang bata -ng kain ko
   post-reorder: takbo ko ang bata -ng kain     ← ko hoisted into matrix cluster
   parses=0                                       ← OV S_GAP needs ng-NP after kain
```

### Third Wackernagel exception: post-embedded-V PRON

Commit 10 adds :func:`tgllfg.clitics.placement._is_post_embedded_v_pron`
alongside the existing post-noun (Phase 5c §7.8 follow-on) and
pre-linker (Phase 5d Commit 6) checks: a PRON-clitic immediately
preceded by a VERB token that is **not** the matrix verb (= not
the first V) stays in place. The check distinguishes two cases:

- PRON after the **matrix V** — that's the regular Wackernagel
  cluster position; placement is a no-op (preceding V === first V).
- PRON after a **non-first V** — the PRON belongs to that
  embedded V's clause (RC, control complement, etc.), not to the
  matrix V. Suppress the move so the embedded clause's grammar
  rules can absorb it.

After the fix:

```text
Tumakbo ang batang kinain ko
   pre-reorder:  takbo ang bata -ng kain ko
   post-reorder: takbo ang bata -ng kain ko    ← ko stays after kain
   parses=1                                     ← OV S_GAP ✓
```

### Competing readings

The plan §9.1 entry flags "pronominal possessor inside relative
clause head" — the construction can in principle have two
readings:

- **RC-actor reading** — the pronoun is the gap-filler inside
  the RC (OV / DV / IV bind it to ``OBJ-AGENT``).
- **Possessor reading** — the pronoun is a possessor on the head
  NP (the existing NP-internal possessive rule).

For OV / DV / IV-RC, only the RC-actor reading is structurally
available because the non-AV S_GAP frames require a GEN-NP after
the V. The possessor reading would need an empty S_GAP (V alone
without a GEN-NP), which the existing rules don't admit. So the
parse is unique.

For AV-RC, both readings parse:

- Reading A: AV-transitive RC where the pronoun is bare ``OBJ``
  (``Tumakbo ang batang kumain ko`` "the child who-ate-me ran").
- Reading B: AV-intransitive RC plus pronominal possessor on the
  head NP (``my child who ate ran``).

Tests cover both by walking the parse list and finding each
shape. The ranker is left to its existing heuristics — pragmatic
disambiguation between the two AV-RC readings depends on the verb
and is not a structural concern.

### What this lifts

- Pronominal RC-actor in OV / DV / IV relativization
  (``Tumakbo ang batang kinain ko``).
- All three vowel-final GEN pronouns (ko / mo / niya).
- Bound ``-ng`` linker (vowel-final head) and standalone ``na``
  linker (consonant-final head).
- RCs nested inside OBJ NPs (``Kumain ang aso ng batang kinain
  ko``) — placement still keeps the pronoun in the embedded RC
  because the Wackernagel logic is per-token, not per-NP.
- AV-RC ambiguity (RC-with-OBJ vs head-possessor) preserved as
  competing parses.

### Out-of-scope (still deferred)

- **`na` linker disambiguation after PRON.** ``Tumakbo ang bata
  ko na nakita`` (possessor + RC) — the placement pass currently
  treats the standalone ``na`` after PRON as the 2P aspectual
  clitic and moves it to clause-end. Resolving this requires
  extending :func:`disambiguate_homophone_clitics` to look at the
  following token (if VERB, ``na`` is the linker). Not pursued
  in Commit 10.
- **Multi-pronoun RCs.** A single matrix sentence with both a
  matrix-cluster PRON and an embedded RC-actor PRON
  (``Nakita ko ang batang kinain niya`` "I saw the child she
  ate"). The two pronouns are at different positions and the
  Wackernagel logic handles them independently, but this hasn't
  been pinned with tests.

## Phase 5e Commit 1: pa-OV / pa-DV (CAUS=DIRECT) actor-fronting

**Date:** 2026-05-01. **Status:** active.

Phase 5d Commit 5 added three gap-category non-terminals
(``S_GAP_OBJ``, ``S_GAP_OBJ_AGENT``, ``S_GAP_OBL``) plus three
matching ay-fronting wrap rules, lifting the §7.4 deferral on
non-pivot ay-fronting for OBJ-θ and DAT-marked obliques. The
``S_GAP_OBJ_AGENT`` non-terminal admits non-AV transitive
fronting only when the V carries ``CAUS=NONE``. The constraint
deliberately excluded pa-OV / pa-DV (CAUS=DIRECT) — under
monoclausal direct causation the actor's typed GF is
``OBJ-CAUSER`` rather than ``OBJ-AGENT``, so a different gap
category is needed. Phase 5e Commit 1 fills in the parallel
extraction path.

### One new gap-category, one new wrap rule

```text
S_GAP_OBJ_CAUSER → V[VOICE=OV, CAUS=DIRECT] NP[CASE=NOM]
   (↑ SUBJ) = ↓2
   (↑ OBJ-CAUSER) = (↑ REL-PRO)
S_GAP_OBJ_CAUSER → V[VOICE=OV, CAUS=DIRECT] NP[CASE=NOM] NP[CASE=GEN]
   (↑ SUBJ) = ↓2
   (↑ OBJ-PATIENT) = ↓3
   (↑ OBJ-CAUSER) = (↑ REL-PRO)
S_GAP_OBJ_CAUSER → V[VOICE=OV, CAUS=DIRECT] NP[CASE=GEN] NP[CASE=NOM]
   (↑ SUBJ) = ↓3
   (↑ OBJ-PATIENT) = ↓2
   (↑ OBJ-CAUSER) = (↑ REL-PRO)
S_GAP_OBJ_CAUSER → V[VOICE=DV, CAUS=DIRECT] NP[CASE=NOM]
   (↑ SUBJ) = ↓2
   (↑ OBJ-CAUSER) = (↑ REL-PRO)
(plus +DAT-adjunct variants for pa-OV-2arg and pa-DV; recursive
 PART[POLARITY=NEG] for inner negation)

S → NP[CASE=GEN] PART[LINK=AY] S_GAP_OBJ_CAUSER
   (↑) = ↓3
   (↑ TOPIC) = ↓1
   (↓3 REL-PRO) = ↓1
   (↓3 REL-PRO) =c (↓3 OBJ-CAUSER)
```

The fronted GEN-NP is the ``CAUSER`` (demoted from actor under
pa-causation). The 3-arg pa-OV variants leave both the NOM
pivot (``CAUSEE``) and the GEN ``OBJ-PATIENT`` overt inside the
inner clause, mirroring Phase 5d Commit 8's S_XCOMP pattern and
the top-level Phase 5b multi-GEN-NP frame ordering.

### Disambiguation against S_GAP_OBJ_AGENT

The two gap-categories ``S_GAP_OBJ_AGENT`` (Commit 5) and the
new ``S_GAP_OBJ_CAUSER`` both attach to the same wrap-rule
shape ``NP[CASE=GEN] PART[LINK=AY] S_GAP_*``. The parser
explores both, but the inner V's CAUS feature picks a unique
winner: CAUS=DIRECT routes only to ``S_GAP_OBJ_CAUSER``;
CAUS=NONE routes only to ``S_GAP_OBJ_AGENT``. The parser's
non-conflict feature matcher means each gap-category's V
filter must be **explicit** about CAUS to avoid cross-firing
on a missing-feature catch-all; both gap-categories already
carry their CAUS constraint, so no new sentinel is needed.

### Why pa-DV stays 2-arg

Phase 5d Commit 2 introduced pa-DV (``pa-...-an``) with the
2-arg PRED ``CAUSE-EAT-AT <SUBJ, OBJ-CAUSER>`` only — a 3-arg
pa-DV variant with overt patient is enumerated as a separate
deferral in plan §10.1 Group D ("Three-argument top-level
pa-DV"). Phase 5e Commit 1 doesn't add a 3-arg pa-DV gap-
category for the same reason: there's no lex profile for it
to attach to. When the 3-arg pa-DV lex lands (Group D commit),
its S_GAP_OBJ_CAUSER frame is a one-line addition.

### What this lifts

- 2-arg pa-OV actor-fronting:
  ``Ng nanay ay pinakain ang bata.``
- 3-arg pa-OV actor-fronting (both NP orders):
  ``Ng nanay ay pinakain ang bata ng kanin.``
  ``Ng nanay ay pinakain ng kanin ang bata.``
- 2-arg pa-DV actor-fronting:
  ``Ng nanay ay pinakainan ang bata.``
- All three pa-OV anchor verbs (kain / basa / inom) and three
  pa-DV anchor verbs (kain / basa / inom).
- IPFV aspect on the embedded V (``pinakakain``).
- Inner negation under fronting
  (``Ng nanay ay hindi pinakain ang bata.``).

### Out-of-scope (still deferred)

- **3-arg pa-DV actor-fronting.** Blocked on the 3-arg pa-DV
  lex profile; lifts as a follow-on once that lands (plan §10.1
  Group D).
- **Pa-OV / pa-DV actor-fronting under embedded control.** The
  Phase 5d Commit 8 S_XCOMP pa-causative rules embed under
  control, but the *fronted* form under control would need a
  matching ``S_XCOMP_GAP_OBJ_CAUSER`` or similar. Composition
  not exercised by corpus.

## Phase 5e Commit 2: multi-GEN-NP ay-fronting

**Date:** 2026-05-01. **Status:** active.

Phase 5b multi-GEN-NP frames bind two GEN-marked non-pivots
positionally to typed ``OBJ-θ`` slots: in IV (any APPL) the first
ng-NP is ``OBJ-AGENT`` and the second is ``OBJ-PATIENT``; in
pa-OV-direct it's ``OBJ-CAUSER`` and ``OBJ-PATIENT``. Phase 5d
Commit 5 added ay-fronting only for non-3-arg shapes (no second
GEN). Phase 5e Commit 1 added 3-arg pa-OV with the CAUSER fronted
(``S_GAP_OBJ_CAUSER`` 3-arg). Phase 5e Commit 2 fills in the
remaining 3-arg multi-GEN extractions:

- 3-arg IV with OBJ-AGENT extracted (OBJ-PATIENT retained):
  ``Ng nanay ay ipinaggawa ang kapatid ng silya``.
- 3-arg multi-GEN with OBJ-PATIENT extracted (in either IV with
  OBJ-AGENT retained, or pa-OV-direct with OBJ-CAUSER retained):
  ``Ng silya ay ipinaggawa ang kapatid ng nanay``,
  ``Ng kanin ay pinakain ng nanay ang bata``.

### S_GAP_OBJ_AGENT IV 3-arg additions

The Phase 5d Commit 5 ``S_GAP_OBJ_AGENT`` rules covered only
2-arg shapes (V plus a single NOM pivot, optionally with a DAT
adjunct). Two IV-only 3-arg variants are added:

```text
S_GAP_OBJ_AGENT → V[VOICE=IV] NP[CASE=NOM] NP[CASE=GEN]
   (↑ SUBJ) = ↓2
   (↑ OBJ-PATIENT) = ↓3
   (↑ OBJ-AGENT) = (↑ REL-PRO)
S_GAP_OBJ_AGENT → V[VOICE=IV] NP[CASE=GEN] NP[CASE=NOM]
   (↑ SUBJ) = ↓3
   (↑ OBJ-PATIENT) = ↓2
   (↑ OBJ-AGENT) = (↑ REL-PRO)
```

The voice is restricted to IV because only IV multi-GEN frames
have a non-CAUSER second GEN-NP. The 2-arg rules are unchanged.

### S_GAP_OBJ_PATIENT — new gap-category

A single new non-terminal handles PATIENT-extraction across
both 3-arg multi-GEN voice families. The retained-GEN binding
is voice-conditioned:

```text
S_GAP_OBJ_PATIENT → V[VOICE=IV] NP[CASE=NOM] NP[CASE=GEN]
   (↑ SUBJ) = ↓2
   (↑ OBJ-AGENT) = ↓3
   (↑ OBJ-PATIENT) = (↑ REL-PRO)
S_GAP_OBJ_PATIENT → V[VOICE=IV] NP[CASE=GEN] NP[CASE=NOM]
   (↑ SUBJ) = ↓3
   (↑ OBJ-AGENT) = ↓2
   (↑ OBJ-PATIENT) = (↑ REL-PRO)
S_GAP_OBJ_PATIENT → V[VOICE=OV, CAUS=DIRECT] NP[CASE=NOM] NP[CASE=GEN]
   (↑ SUBJ) = ↓2
   (↑ OBJ-CAUSER) = ↓3
   (↑ OBJ-PATIENT) = (↑ REL-PRO)
S_GAP_OBJ_PATIENT → V[VOICE=OV, CAUS=DIRECT] NP[CASE=GEN] NP[CASE=NOM]
   (↑ SUBJ) = ↓3
   (↑ OBJ-CAUSER) = ↓2
   (↑ OBJ-PATIENT) = (↑ REL-PRO)
S_GAP_OBJ_PATIENT → PART[POLARITY=NEG] S_GAP_OBJ_PATIENT
   (↑) = ↓2  (↑ POLARITY) = 'NEG'
```

The wrap rule:

```text
S → NP[CASE=GEN] PART[LINK=AY] S_GAP_OBJ_PATIENT
   (↑) = ↓3
   (↑ TOPIC) = ↓1
   (↓3 REL-PRO) = ↓1
   (↓3 REL-PRO) =c (↓3 OBJ-PATIENT)
```

### Structural ambiguity: both readings parse

For an inner-clause shape like ``ipinaggawa ang kapatid ng silya``
(IV-BEN with one retained GEN), two gap-categories match the
same shape:

- ``S_GAP_OBJ_AGENT`` 3-arg: gap = OBJ-AGENT, retained = OBJ-PATIENT.
- ``S_GAP_OBJ_PATIENT`` IV: gap = OBJ-PATIENT, retained = OBJ-AGENT.

Both rules fire and both wrap rules above succeed (with their
respective constraining equations). The result is two parses for
the same surface, distinguished by which fronted-NP role binds:

- ``Ng nanay ay ipinaggawa ang kapatid ng silya`` admits both
  AGENT-fronted (TOPIC=nanay=AGENT, silya=PATIENT) and
  PATIENT-fronted (TOPIC=nanay=PATIENT, silya=AGENT) readings.
  Animacy makes the first natural; the second is structurally
  available.

This mirrors Tagalog's tolerance for the corresponding role
ambiguity in non-fronted multi-GEN frames (the Phase 5b
positional convention is just the unmarked default; lexical
semantics resolves the actual binding). Tests pin the natural
reading via a TOPIC-PRED-GF triple filter.

### Discrimination by voice + CAUS

The two voice/feature combinations on ``S_GAP_OBJ_PATIENT`` are
mutually exclusive (IV vs OV-CAUS=DIRECT), so a single inner
clause never matches both branches of ``S_GAP_OBJ_PATIENT`` —
the f-structure is unambiguous about *which* GF the retained
GEN-NP fills (OBJ-AGENT under IV, OBJ-CAUSER under pa-OV-direct).
Cross-voice contamination is structurally impossible.

### What this lifts

- IV-BEN / IV-INSTR / IV-REASON 3-arg with AGENT fronted
  (``Ng nanay ay ipinaggawa ang kapatid ng silya``,
  ``Ng nanay ay ipinambili ang pera ng isda``,
  ``Ng bata ay ikinasulat ang gutom ng isda``).
- IV 3-arg with PATIENT fronted
  (``Ng silya ay ipinaggawa ang kapatid ng nanay``).
- pa-OV-direct 3-arg with PATIENT fronted
  (``Ng kanin ay pinakain ng nanay ang bata``).
- Both inner NP orders (NOM-GEN and GEN-NOM after the V).
- Inner negation under fronting.

### Out-of-scope (still deferred)

- **DV 3-arg multi-GEN ay-fronting.** Blocked on Group D's "DV
  three-argument constructions" item — DV multi-GEN rules
  themselves don't yet exist. Lifts as a follow-on once that
  Group D commit lands.
- **3-arg multi-GEN ay-fronting under embedded control.**
  Crosses with Phase 5d Commits 7 / 8 / 9; not exercised by the
  current corpus.

## Phase 5e Commit 3: AdvP / PP ay-fronting

**Date:** 2026-05-01. **Status:** active.

Phase 4 §7.4's "Out-of-scope" list flagged ``Kahapon ay tumakbo
si Maria`` (temporal AdvP) and ``Para sa bata ay binili niya ang
aklat`` (PP) as deferred until "the categorial inventory expands".
Phase 5e Commit 3 lifts the deferral with the smallest categorial
expansion sufficient to host the construction.

### Two new POS values

In :file:`data/tgl/particles.yaml`:

- ``ADV`` — closed-class temporal adverbs. Seeded with four
  entries: ``kahapon`` "yesterday" (DEIXIS_TIME=PAST), ``ngayon``
  "now/today" (PRES), ``bukas`` "tomorrow" (FUT), ``mamaya``
  "later" (FUT). Each carries ``ADV_TYPE=TIME`` for grammar-rule
  matching.
- ``PREP`` — compound preposition heads that subcategorise for a
  sa-NP complement. Seeded with four entries: ``para``
  (PREP_TYPE=BENEFICIARY), ``tungkol`` (TOPIC), ``mula`` (SOURCE),
  ``dahil`` (REASON). Each PREP carries ``LEMMA`` (set
  automatically by the analyzer for ADV / PREP particles, mirroring
  the noun-LEMMA pattern from Phase 5c §8 follow-on Commit 6) so
  the head's lemma percolates through ``AdvP → ADV`` and
  ``PP → PREP NP[CASE=DAT]`` to the matrix TOPIC.

### Two new non-terminals

```text
AdvP → ADV
   (↑) = ↓1

PP → PREP NP[CASE=DAT]
   (↑) = ↓1
   (↑ OBJ) = ↓2
```

The AdvP rule is a single-child lift — closed-class single-word
adverbs don't need internal structure. The PP rule heads with the
PREP and exposes the sa-NP complement as ``OBJ`` (analogous to
how a clause's V exposes its arguments). The PP's f-structure
inherits ``PREP_TYPE`` and ``LEMMA`` from its head.

### Two new ay-fronting wrap rules

```text
S → AdvP PART[LINK=AY] S
   (↑) = ↓3
   (↑ TOPIC) = ↓1
   ↓1 ∈ (↑ ADJ)

S → PP PART[LINK=AY] S
   (↑) = ↓3
   (↑ TOPIC) = ↓1
   ↓1 ∈ (↑ ADJ)
```

Both rules:

- Make the inner S the matrix's f-structure (``(↑) = ↓3``).
- Set the matrix's ``TOPIC`` to the fronted phrase.
- Add the fronted phrase to the matrix's ``ADJ`` set, preserving
  adjunct semantics alongside the topic-marking.

The inner S is a complete clause with no gap — AdvP / PP are
sentential modifiers, not arguments of any voice/aspect frame,
so there's nothing to extract from the inner clause's GF
inventory. This contrasts with the NP ay-fronting rules
(``S → NP[CASE=*] PART[LINK=AY] S_GAP_*``) which do require a
gap-category for the extracted argument.

### Why ADJ instead of ADJUNCT

Two non-governable set-valued attributes coexist in the f-structure:

- ``ADJUNCT`` holds DAT-NPs (sa-NPs) as collected by the parser's
  ``↓N ∈ (↑ ADJUNCT)`` equations. The Phase 5 LMT
  ``oblique_classifier`` post-processes this set into typed
  ``OBL-θ`` slots (LOC / RECIP / etc.).
- ``ADJ`` holds quantifier-floats (Phase 4 §7.8), 2P clitic
  particles (Phase 4 §7.3), and now AdvP / PP fronted topics.
  The classifier doesn't touch ADJ.

Putting AdvP / PP in ``ADJ`` keeps them out of the
oblique-classifier's purview (they're not sa-NPs); they're
modifier-class adjuncts, not GF-typed obliques.

### Discrimination against existing fronting rules

The new wrap rules use ``AdvP`` and ``PP`` non-terminals as
their first child, distinct from the existing ``NP[CASE=NOM/GEN/DAT]``
fronts. The parser's matcher selects the rule based on the
non-terminal type plus child features, so cross-firing is
structurally impossible:

- ``Kahapon ay tumakbo si Maria`` — only the AdvP wrap rule
  matches (``kahapon`` as ADV); the NP-fronting rules require an
  NP, which a bare adverb without a DET cannot form.
- ``Para sa bata ay binili niya ang libro`` — both the PP wrap
  rule (``para`` as PREP heading a PP) and the DAT-NP wrap rule
  (``sa bata`` as a fronted DAT-NP, ignoring ``para``) could
  fire. The existing DAT-NP rule requires a single ``NP[CASE=DAT]``
  not preceded by anything; the surface has ``para sa bata``
  which contains an extra PREP token, so the DAT-NP-only rule
  doesn't extend across it. The PP wrap rule wins.

### What this lifts

- Temporal-AdvP ay-fronting:
  ``Kahapon ay tumakbo si Maria.``
  ``Ngayon ay kumakain ang bata.``
  ``Bukas ay tutulog si Maria.``
  ``Mamaya ay tutulog si Maria.``
- PP ay-fronting across all four seeded prepositions:
  ``Para sa bata ay binili niya ang libro.``
  ``Tungkol sa nanay ay sumulat ang bata.``
  ``Mula sa bahay ay tumakbo si Maria.``
  ``Dahil sa gutom ay kumain ang bata.``
- Inner-clause negation under both forms.
- Inner-clause transitive frames (AV and OV).

### Out-of-scope (still deferred)

- **Non-fronted AdvP / PP placement.** Clause-final or
  unmarked-sentential-adjunct placement of AdvP / PP
  (``Tumakbo si Maria kahapon``, ``Binili niya ang libro
  para sa bata``) — keeps AdvP / PP out of the matrix's
  post-V argument frames. Adding bare placement would interact
  with §7.3 Wackernagel-cluster placement and §7.8 quantifier-
  float and is left as a separate commit. The bare-AdvP /
  bare-PP usage is more frequent than the ay-fronted form, so
  this is a real gap; landing it as a separate commit keeps the
  scope reviewable.
- **Multi-word AdvPs.** ``kahapon ng umaga`` "yesterday morning"
  needs an ``AdvP → ADV NP[CASE=GEN]`` rule.
- **AdvP / PP modifying inner NPs.** ``ang aklat para sa bata``
  ("the book for the child") embeds the PP inside an NP rather
  than at the clausal level. Different attachment site.

## Phase 5e Commit 4: multi-pronoun RC composition pinning

**Date:** 2026-05-01. **Status:** active.

Phase 5d Commit 10's deferral list flagged "Multi-pronoun RCs" —
a single matrix sentence with both a matrix-cluster PRON and an
embedded RC-actor PRON, e.g. ``Nakita ko ang batang kinain niya``
("I saw the child she ate"). The Wackernagel logic from
Commit 10 (specifically
:func:`tgllfg.clitics.placement._is_post_embedded_v_pron`)
already handled the two pronouns independently per-token: the
post-matrix-V PRON (``ko``) goes into the matrix V's cluster,
the post-embedded-V PRON (``niya``) stays in place as the RC's
actor. The construction was structurally available but not
pinned with tests.

This commit is **test-only** — no grammar / placement / lex
changes. It pins the composition with explicit assertions:

- Both PRONs end up in distinct f-structure slots (different
  ``FStructure.id``s).
- The matrix-cluster PRON binds to the matrix V's appropriate
  role (matrix.OBJ in the synthesized AV-NVOL ``nakita`` case;
  matrix.SUBJ in AV-tr cases).
- The embedded RC-actor PRON binds inside the RC (the RC is an
  ADJ member of its head NP; the PRON fills the RC's
  OBJ-AGENT) — not at the matrix level.
- Negation under either the matrix or the RC composes
  independently.

### Identification by structural position, not LEMMA / PERS

Pronouns in Tagalog don't carry a grammar-visible LEMMA (the
analyzer doesn't add one for the PRON path), and PERS rides on
``feats`` as an integer which the pipeline's lex-equation
derivation drops (only string-valued feats become lex
equations). The two PRONs in a multi-pronoun RC are therefore
**indistinguishable at the f-structure level** beyond:

- Their structural position (matrix slot vs ADJ-RC slot).
- Their CASE / NUM features (which are string-valued and
  percolate).

Tests rely on structural position plus CASE / NUM. This is
sufficient for "composition pinning" but doesn't directly
distinguish 1sg vs 2sg vs 3sg. Adding string-valued PERS to the
analyzer is a small follow-up that would let downstream
consumers identify pronouns by person; out of scope for this
commit.

### What this lifts

Three matrix-PRON / RC-PRON orderings explicitly tested:

- ``Nakita ko ang batang kinain niya.`` (1sg + 3sg)
- ``Nakita mo ang batang kinain niya.`` (2sg + 3sg)
- ``Nakita niya ang batang kinain ko.`` (3sg + 1sg)

Plus AV-matrix variant
(``Kumain ako ng batang kinain niya.``) and inner-NEG
composition (``Nakita ko ang batang hindi kinain niya.``).

### Out-of-scope (still deferred)

- **3+ pronouns in a single sentence.** Matrix + RC1 + RC2 with
  three distinct PRONs (``Nakita ko ang batang kinain mo ng
  isdang nahuli niya``) — the recursion is structurally
  available but combinatorially explodes the parse forest;
  stress-test deferred until corpus pressure justifies.
- **PERS exposure as string-valued feat.** Would let tests and
  downstream consumers distinguish 1sg / 2sg / 3sg pronouns at
  the f-structure level. Trivial analyzer addition; deferred
  to a separate engineering follow-up.

## Phase 5e Commit 5: headless / free relatives

**Date:** 2026-05-01. **Status:** active.

Phase 4 §7.5's "Out-of-scope" list flagged headless / free
relatives (``ang kumain`` "the one who ate") as deferred. A
headless RC is a relative clause used directly as an NP, with
no overt head noun — the "head" is interpreted as a
phonologically null PRO that's identified with the gap-filler
(REL-PRO).

### Three additive grammar rules

```text
NP[CASE=NOM] → DET[CASE=NOM, DEM=NO] S_GAP
NP[CASE=GEN] → ADP[CASE=GEN, DEM=NO] S_GAP
NP[CASE=DAT] → ADP[CASE=DAT, DEM=NO] S_GAP

   (↑ PRED) = 'PRO'
   (↑ CASE) = '<case>'
   (↑ MARKER) = ↓1 MARKER
   ↓2 ∈ (↑ ADJ)
   (↓2 REL-PRO PRED) = 'PRO'
   (↓2 REL-PRO CASE) = '<case>'
   (↓2 REL-PRO) =c (↓2 SUBJ)
```

Each rule is a single-line addition mirroring the Phase 4 §7.8
standalone-demonstrative analysis (PRED='PRO' for the implicit
head) plus the §7.5 head-initial-relativization equation
pattern (S_GAP attaches as ADJ; REL-PRO inherits PRED='PRO' and
CASE).

### DEM=NO discrimination prevents cross-firing

The new rules constrain ``DEM=NO`` on the determiner so they
don't fire on standalone demonstratives (``ito`` / ``iyan`` /
``iyon`` carry ``DEM=YES``). The Phase 4 §7.8 standalone-
demonstrative rule continues to handle ``Kumain iyon.`` ("That
one ate."); the headless-RC rule handles ``Tumakbo ang
tumakbo.`` ("The one who ran ran."). The two never compete on
the same surface because their initial-determiner POS×DEM
combinations are disjoint.

### Synthesizer-fallback limitation: AV-tr RC needs overt OBJ

The synthesizer-fallback path (Phase 4 §7.2,
:func:`_synthesize_verb_entry`) emits exactly ONE entry per
voice for verbs not in BASE: AV-tr produces ``<SUBJ, OBJ>`` (no
intransitive variant). So ``ang umiinom`` (a headless RC where
the inner V is ``inom`` AV-IPFV, with no BASE entry) needs an
overt OBJ to satisfy completeness — ``ang umiinom ng tubig`` is
fine, but bare ``ang umiinom`` is not. Hand-authored AV-intr
entries (``kain``, ``bili``) admit the bare form
(``ang kumain``); intrinsically intransitive verbs
(``takbo``, ``tulog``) also admit the bare form. The limitation
is a synthesizer scope issue, not a headless-RC issue.

### What this lifts

- AV-INTR-RC: ``Tumakbo ang tumakbo.``, ``Tumakbo ang natulog.``
- AV-tr-RC with overt OBJ: ``Tumakbo ang kumain ng isda.``,
  ``Kumain ang kumain ng isda.``
- OV-tr-RC (patient pivot): ``Tumakbo ang kinain ng aso.``
- Headless RC in non-SUBJ position:
  ``Nakita ko ang tumakbo.`` (OBJ-position headless RC).
- Inner negation under headless RC:
  ``Tumakbo ang hindi kumain ng isda.``

The construction composes with the existing Phase 4 §7.8 NP-
internal possessive (``ang kumain ng bata`` could mean either
"the one who ate the child" with `ng bata` as OBJ, OR "the
child's-eating(-thing)" with `ng bata` as POSS — both readings
are linguistically valid and both surface in n-best output).

### Out-of-scope (still deferred)

- **Headless RC with synthesized AV-intransitive verb.** Verbs
  with TR=TR but no hand-authored intransitive AV BASE entry
  (e.g., ``inom`` AV without overt OBJ) don't form a valid
  bare headless RC because completeness fails. A synthesizer
  enhancement that emits both ``<SUBJ>`` and ``<SUBJ, OBJ>``
  variants for TR-marked AV verbs would lift this; deferred
  as an engineering follow-up.
- **Headless RC modifying another NP.** ``ang aklat ng kumain``
  (a possessive structure where the possessor is itself a
  headless RC) might admit interesting parses; not exercised.

## Phase 5e Commit 6: ``na`` linker disambiguation after PRON

**Date:** 2026-05-01. **Status:** active.

Phase 5d Commit 10's deferral list flagged ``Tumakbo ang bata ko
na nakita`` (NP-internal possessor + linker + RC). The
:func:`tgllfg.clitics.placement.disambiguate_homophone_clitics`
pass historically treated post-PRON ``na`` as the 2P aspectual
clitic ``ALREADY`` (CLITIC_CLASS=2P) and moved it to clause-end,
breaking the linker / RC parse.

This commit adds a third left-context exception in the
disambiguator (alongside the two existing control-verb cases),
plus a small look-ahead helper.

### The new exception

``disambiguate_homophone_clitics`` already had two left-context
exceptions where post-VERB / post-PRON ``na`` is the linker;
Phase 5e Commit 6 adds a third (item 3 below):

1. ``V[CTRL_CLASS!=NONE]`` directly preceding (Phase 5c §7.6
   follow-on Commit 3) — ``Gusto na kumain``.
2. PRON preceding, the PRON's prev being ``V[CTRL_CLASS!=NONE]``
   (Phase 4 §7.10) — ``Kaya namin na kumain``.
3. PRON preceding, the PRON's prev being NOUN (i.e., the PRON
   is an NP-internal possessor), AND the next content token
   after ``na`` is a VERB (or NEG + VERB) — Phase 5e Commit 6.

### Look-ahead through PART[POLARITY=NEG]

A small helper :func:`_next_content_is_verb` looks at the next
position; if it's a ``PART[POLARITY=NEG]`` token (``hindi`` /
``huwag``) and not a VERB, it skips one position and looks
again. Returns True only if the first non-NEG content token is
a VERB. This makes ``Tumakbo ang bata ko na hindi kumain`` work
(NEG-RC under the new disambiguation).

### Why look at both sides?

The trigger condition is **bilateral**: NOUN before PRON before
``na`` before VERB. The simpler "PRON before ``na`` before VERB"
pattern would fire in too many cases — for instance,
``Kumain mo na ang isda`` has post-V PRON ``mo`` followed by
``na`` followed by DET ``ang`` (not VERB), so that case is
unaffected. But ``Kumain mo na nakita`` would
spuriously trigger if we only looked right (V + PRON + na + V),
even though the natural reading there is the 2P clitic ``mo na``
followed by an awkward second clause. Requiring NOUN preceding
the PRON narrows the trigger to the genuine NP-internal-
possessive pattern, which is the only context where ``na`` after
a post-noun PRON unambiguously introduces an RC.

### Synthesizer-fallback caveat

The deferral note's example ``Tumakbo ang bata ko na nakita``
uses ``nakita`` (kita NVOL form). ``kita`` is TR-only in the
seed lexicon, so the synthesizer fallback emits only
``KITA <SUBJ, OBJ>`` — the bare RC ``nakita`` (no overt OBJ)
fails completeness. The disambiguation fix from this commit is
correct, but the corpus tests for the construction use verbs
that have hand-authored AV-intransitive BASE entries
(``kain``, ``bili``, etc.) or are intrinsically intransitive
(``takbo``, ``tulog``). Adding bare-AV-intr synthesizer
fallback for TR verbs is the same engineering follow-up flagged
in Phase 5e Commit 5 (headless / free relatives) and is
deferred to a separate commit.

### What this lifts

- ``Tumakbo ang bata ko na kumain.`` "My child who ate ran."
- ``Tumakbo ang bata mo na kumain.`` (2sg-GEN possessor)
- ``Tumakbo ang bata niya na kumain.`` (3sg-GEN possessor)
- ``Tumakbo ang bata ko na kumain ng isda.`` (transitive RC).
- ``Tumakbo ang bata ko na kinain ng aso.`` (OV RC).
- ``Tumakbo ang bata ko na hindi kumain.`` (NEG-RC under
  the construction).

### Out-of-scope (still deferred)

- **Bare-AV-intr synthesizer fallback.** As above — needed to
  lift the original ``Tumakbo ang bata ko na nakita`` example
  where the RC's V is a TR verb without a hand-authored
  intransitive entry.
- **Other possessive markers + na linker.** ``aklat ng bata na
  nakita`` (non-pronominal possessor) — the existing
  NP-internal possessive plus relativization rules already
  handle this without disambiguation issues; not exercised
  here.

## Phase 5e Commit 7: resumptive pronouns in RCs (reclassification)

**Date:** 2026-05-01. **Status:** active. Documentation-only
commit; no grammar / lex / morph changes.

The Phase 4 §7.5 "Out-of-scope" note flagged "Resumptive
pronouns in RCs (rare in modern Tagalog)" as deferred, and
plan §10.1 Group B carried it forward as a Phase 5e candidate.
On investigation, the construction does not have a stable,
corpus-attested syntactic shape in modern written Tagalog, and
attempting to implement it without that grounding would mean
guessing at form. Phase 5e Commit 7 reclassifies the item to
plan §18 (genuinely v1-out-of-scope) and pins the rationale
here.

### Why Tagalog doesn't really use resumptive RCs

Resumptive pronouns are a cross-linguistic strategy where a
pronoun fills the relativized position instead of leaving a
gap (English colloquial: "the man who I saw him"). Tagalog has
two structural alternatives that obviate the resumptive option:

1. **Voice alternation** is the canonical strategy for
   non-SUBJ relativization. The SUBJ-only restriction (Kroeger
   1993 §5; Schachter & Otanes 1972 §5.16) means only the
   ang-NP can be relativized, but voice alternation lets the
   speaker pick which thematic role becomes the ang-NP. To
   relativize the agent of a "patient-pivot" event, switch to
   AV and the agent becomes the SUBJ:
   ``Ang batang kumain ng isda.`` "The child who ate the fish."
   (AV; bata is SUBJ=actor.) The OV form
   ``*Ang batang kinain ang isda.`` "The child who-ate the fish"
   (with bata as the agent of OV) is rejected by the SUBJ-only
   restriction and is the construction a resumptive pronoun
   would otherwise repair.
2. **Restructuring with a relative clause that itself is the
   matrix** (focus / cleft constructions) — ``Ang bata ang
   kumain ng isda.`` "It's the child who ate the fish."

Both strategies are productive, well-documented, and present
in the corpus. Resumptive pronouns aren't.

### What the corpus shows

The Phase 4 §7.10 reference corpus (818 sentences originally,
now 859 with the Phase 5e additions) contains zero
unambiguously-resumptive RC examples. The seeded R&G 1981
fixtures (20 sentences) and the classic / S&O / Kroeger
fixtures (12 sentences) likewise don't include any. The
deferral note's "rare in modern Tagalog" flag accurately
captures this.

### What it would take to lift

A meaningful implementation would need:

1. A corpus showing the construction at non-trivial frequency.
2. Agreement on its syntactic shape — typically:
   ``NP[CASE=X] → NP[CASE=X] PART[LINK] S_RES`` where
   ``S_RES`` is a *non-gapped* clause containing a coreferent
   pronoun that's functionally identified with the head.
3. Decision on how to identify the coreferent pronoun: by
   pragmatic / discourse-anaphora resolution (out of scope
   per §18 sentence-level tooling) or by an explicit
   ``REL-PRO`` binding equation that's lex-licensed.

None of these conditions hold. Reclassifying to §18 is the
honest call.

### Where it lives now

- Plan §10.1 Group B has a parenthetical noting the
  reclassification and a pointer to §10.2 / §18.
- Plan §10.2 ("Items not enumerated above") gains the
  resumptive item alongside the other genuinely-out-of-scope
  Phase 5e items (unbounded control chains, 3+ sa-NPs,
  non-restrictive RCs).
- Plan §18 gains a new bullet articulating the why.
- This `docs/analysis-choices.md` section pins the rationale
  with citations.

### Out-of-scope (still deferred)

The reclassification doesn't itself defer anything new —
resumptive pronouns were already deferred at §7.5 and §10.1.
The change is administrative: moving an item from
"additive Phase 5e candidate" to "v1-out-of-scope".

## Phase 5e Commit 8: control / raising composition pinning

**Date:** 2026-05-01. **Status:** active. Test-only commit; no
grammar / lex / morph changes.

Phase 5d Commit 7's deferral list flagged two raising / control
compositions as available structurally but not pinned with
tests:

- **Control under raising** — a raising matrix embedding a
  control clause as its non-gap S complement. The Phase 5c §7.6
  Commit 5 raising rule
  ``S → V[CTRL_CLASS=RAISING] PART[LINK] S`` admits any
  complete S as the inner clause, including a control-S.
- **TRANS control + raising** — a TRANS control verb
  (``pinilit``) whose XCOMP is itself a raising-S_XCOMP. The
  Phase 5d Commit 7 ``S_XCOMP``-level raising rules made this
  composition available; this commit pins it.

### Composition shapes

**Control under raising:**

```text
Mukhang gusto ng batang kumain.
S[SEEM]
  XCOMP = S[WANT, PSYCH-control]
            SUBJ = bata (GEN-experiencer)
            XCOMP = S_XCOMP[EAT]
                      SUBJ = bata (REL-PRO bound)
  SUBJ = bata (raising structure-share)
```

All three SUBJ slots (mukha.SUBJ, gusto.SUBJ, kumain.SUBJ) end
up sharing one f-node id — verified by Python-id equality in
tests. The raising binding equation
``(↑ SUBJ) = (↑ XCOMP SUBJ)`` lifts gusto's SUBJ to mukha's
SUBJ, and gusto's existing control equation
``(↑ SUBJ) = (↑ XCOMP REL-PRO)`` chains into kain.

**TRANS control + raising:**

```text
Pinilit ng nanay ang batang mukhang umuwi.
S[FORCE]
  OBJ-AGENT = nanay
  SUBJ = bata
  XCOMP = S_XCOMP[SEEM, raising]
            SUBJ = bata (raising shares)
            XCOMP = S_XCOMP[UWI]
                      SUBJ = bata (REL-PRO bound)
```

Three SUBJ slots again share one f-node id. The Phase 5d
Commit 7 ``S_XCOMP`` raising rule (with its own
``(↑ SUBJ) = (↑ REL-PRO)`` plus
``(↑ SUBJ) = (↑ XCOMP SUBJ)``) composes seamlessly with the
TRANS-control wrap rule's
``(↑ SUBJ) = (↑ XCOMP REL-PRO)``.

### What this lifts (pins, really)

- Control under linked raising (mukha / baka):
  ``Mukhang gusto ng batang kumain.``,
  ``Bakang gusto ng batang kumain.``,
  ``Mukhang pumayag ang batang kumain.``
- Control under bare raising (parang / tila):
  ``Parang gusto ng batang kumain.``,
  ``Tila gusto ng batang kumain.``
- TRANS control + raising in XCOMP:
  ``Pinilit ng nanay ang batang mukhang umuwi.``,
  ``Pinilit ng nanay ang batang parang umuwi.``
- Negation at the middle level
  (``Mukhang hindi gusto ng batang kumain``) and at the
  innermost level
  (``Mukhang gusto ng batang hindi kumain``).

### Out-of-scope (still deferred)

- **Psych control over a raising-S at the S level**
  (``Gusto kong mukhang kumain ang aso``). The structure puts a
  raising-S inside an ``S_XCOMP`` slot; the outermost layer is
  ``gusto``'s control wrap rule expecting an ``S_XCOMP``, but
  the raising rule expects its inner clause to be a complete
  ``S`` (with overt SUBJ). Resolving the conflict needs either
  a new control-over-raising-S wrap rule shape or the inner
  raising-S to admit a SUBJ-gap variant. Not exercised by the
  current corpus and not pursued in this commit.

## Phase 5e Commit 9: nested-control composition with multi-arg embedded clauses

**Date:** 2026-05-01. **Status:** active. Test-only commit; no
grammar / lex / morph changes.

Phase 5d Commits 8 and 9's deferral lists flagged two
compositions as available structurally but not pinned with
tests:

- **Nested pa-causatives under control.** Phase 5c §7.6 Commit
  3 added nested-S_XCOMP rules — a control verb's XCOMP is
  itself another control verb whose XCOMP is the action.
  Phase 5d Commit 8 added pa-OV (CAUS=DIRECT) S_XCOMP rules
  (the embedded actor's typed slot is ``OBJ-CAUSER``). Stacked,
  they produce 3-level controller chains where the innermost
  is a pa-OV.
- **IV multi-GEN under nested control.** Phase 5d Commit 9
  added 3-arg IV S_XCOMP rules (gap = OBJ-AGENT,
  retained = OBJ-PATIENT). When stacked under the Commit 3
  nested-control infrastructure, the controller chains to the
  embedded ``OBJ-AGENT`` while ``OBJ-PATIENT`` stays overt as a
  GEN-NP.

### Composition shapes

**Nested pa-OV under control** (3 levels, gap routes to
OBJ-CAUSER):

```text
Gusto kong pumayag na pakakainin ang bata.
S[WANT, PSYCH]
  SUBJ = ko (GEN experiencer)
  XCOMP = S_XCOMP[AGREE, INTRANS]
            SUBJ = ko (REL-PRO bound)
            XCOMP = S_XCOMP[CAUSE-EAT, pa-OV]
                      SUBJ = bata (the causee)
                      OBJ-CAUSER = ko (REL-PRO bound; the gap)
```

Three slots — matrix.SUBJ, XCOMP.SUBJ, XCOMP.XCOMP.OBJ-CAUSER —
share one f-node id via Python-id equality. The pa-OV's pivot
(``ang bata`` = causee) is a separate f-node.

The 3-arg variant ``Gusto kong pumayag na pakakainin ang bata
ng kanin`` adds an overt ``OBJ-PATIENT = kanin`` while
preserving the OBJ-CAUSER gap binding.

**IV multi-GEN under nested control** (3 levels, gap routes to
OBJ-AGENT):

```text
Gusto kong pumayag na ipaggagawa ang silya ng nanay.
S[WANT, PSYCH]
  SUBJ = ko
  XCOMP = S_XCOMP[AGREE, INTRANS]
            SUBJ = ko
            XCOMP = S_XCOMP[MAKE-FOR, IV-BEN 3-arg]
                      SUBJ = silya (the BEN pivot)
                      OBJ-PATIENT = nanay (overt GEN)
                      OBJ-AGENT = ko (REL-PRO bound; the gap)
```

Both compositions reuse existing rules — no engine, grammar, or
lex changes. The Phase 5b ``apply_lmt_with_check`` recursive
walker validates each embedded f-structure against its own
intrinsic profile, so all three levels of LMT-coherence checks
pass cleanly.

### Out-of-scope (still deferred)

- **Pa-DV under nested control.** Phase 5d Commit 2 introduced
  pa-DV (``pa-...-an``) at S level, and Phase 5d Commit 8 added
  pa-DV under single-level control. Pa-DV under *nested* control
  (e.g., ``Gusto kong pumayag na pakakainan ang bata``) should
  compose via the existing rules but isn't pinned here. Adding
  it would mirror the pa-OV pattern.
- **3-arg pa-DV** — separate Phase 5e Commit 10 item.
  Currently the lex profile is 2-arg only, so 3-arg pa-DV under
  nested control is doubly blocked.
- **4+ levels of nesting.** Phase 5c Commit 3 covers 4 levels;
  composing pa-OV / IV-3arg innermost with 4+ levels of control
  hasn't been pinned.

## Phase 5e Commit 10: 3-arg pa-DV (with overt PATIENT)

**Date:** 2026-05-01. **Status:** active.

Phase 5d Commit 2 introduced pa-DV (``pa-...-an``) at the matrix
level with a 2-arg PRED ``CAUSE-X-AT <SUBJ, OBJ-CAUSER>`` —
mirroring the pa-OV 2-arg shape but with the pa-DV pivot
(LOCATION / recipient / dative) at SUBJ. Phase 5d Commit 8 added
pa-DV under control at 2-arg. The 3-arg pa-DV variant (with
overt PATIENT) was deferred in both commits because the lex
profile didn't admit a third argument and a new intrinsic
profile was needed.

Phase 5e Commit 10 fills in the pa-DV symmetry to match Phase
5b's pa-OV-direct 3-arg coverage:

### New intrinsic profile

```python
_DV_CAUS_DIRECT_THREE_ARG = {
    "CAUSER":   (True, True),     # → OBJ-CAUSER
    "PATIENT":  (True, True),     # → OBJ-PATIENT
    "LOCATION": (False, False),   # → SUBJ (the pivot)
}
```

Mirrors ``_OV_CAUS_DIRECT_THREE_ARG`` but with LOCATION at
SUBJ instead of CAUSEE. The role label is LOCATION because
Tagalog's DV broadly subsumes locative + recipient + dative
under one voice; for animate-pivot tests like ``ang bata`` the
reading is recipient.

### Three new BASE entries (kain / basa / inom DV CAUS=DIRECT 3-arg)

```text
CAUSE-EAT-AT   <SUBJ, OBJ-CAUSER, OBJ-PATIENT>   kain DV CAUS=DIRECT
CAUSE-READ-AT  <SUBJ, OBJ-CAUSER, OBJ-PATIENT>   basa DV CAUS=DIRECT
CAUSE-DRINK-AT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>   inom DV CAUS=DIRECT
```

Both 2-arg and 3-arg entries coexist for each verb; lex lookup
chooses based on NP count.

### New top-level multi-GEN-NP pa-DV grammar rules

Three permutations parallel to the Phase 5b multi-GEN-NP pa-OV
rules:

```text
S → V[VOICE=DV, CAUS=DIRECT] NP[CASE=NOM] NP[CASE=GEN] NP[CASE=GEN]
   ↳ SUBJ=NOM (LOCATION), OBJ-CAUSER=1st GEN, OBJ-PATIENT=2nd GEN
S → V[VOICE=DV, CAUS=DIRECT] NP[CASE=GEN] NP[CASE=NOM] NP[CASE=GEN]
S → V[VOICE=DV, CAUS=DIRECT] NP[CASE=GEN] NP[CASE=GEN] NP[CASE=NOM]
```

The first ng-NP is CAUSER (the agentive instigator), the second
is PATIENT, per the Phase 5b positional convention.

### S_XCOMP additions for 3-arg pa-DV under control

```text
S_XCOMP → V[VOICE=DV, CAUS=DIRECT] NP[CASE=NOM] NP[CASE=GEN]
   ↳ SUBJ=NOM, OBJ-PATIENT=GEN, OBJ-CAUSER=REL-PRO (gap)
S_XCOMP → V[VOICE=DV, CAUS=DIRECT] NP[CASE=GEN] NP[CASE=NOM]
```

Mirrors the pa-OV variants in Phase 5d Commit 8.

### S_GAP_OBJ_CAUSER and S_GAP_OBJ_PATIENT additions for ay-fronting

- ``S_GAP_OBJ_CAUSER`` gains 3-arg pa-DV variants (NOM-GEN /
  GEN-NOM with retained OBJ-PATIENT) — lifts the deferral
  flagged in Phase 5e Commit 1.
- ``S_GAP_OBJ_PATIENT``'s ``patient_gap_specs`` gains
  ``("V[VOICE=DV, CAUS=DIRECT]", "OBJ-CAUSER")`` — lets pa-DV
  3-arg PATIENT-fronting use the same gap-category as IV /
  pa-OV.

### Sentences enabled

- Top-level 3-arg pa-DV across all three NP-order permutations:
  ``Pinakainan ng nanay ng kanin ang bata.`` "Mother fed rice
  to the child."
- 3-arg pa-DV under control:
  ``Gusto kong pakakainan ang bata ng kanin.`` "I want to feed
  rice to the child."
- 3-arg pa-DV ay-fronting (CAUSER-fronted, PATIENT retained):
  ``Ng nanay ay pinakainan ang bata ng kanin.``
- 3-arg pa-DV ay-fronting (PATIENT-fronted, CAUSER retained):
  ``Ng kanin ay pinakainan ng nanay ang bata.``

### Composition with embedded control

Single-level pa-DV under control works (PSYCH and INTRANS
classes). Nested pa-DV under control composes via the same
Phase 5c §7.6 Commit 3 nested-S_XCOMP rules that pa-OV uses,
though it isn't separately pinned with tests in this commit.

### Out-of-scope (still deferred)

- **Nested 3-arg pa-DV under multi-level control** — like the
  pa-OV nested cases pinned in Phase 5e Commit 9, but with
  3-arg pa-DV innermost. Should compose; not pinned.
- **Other less-common DV causative variants** (``ka-...-an``
  reciprocal, ``magpa-...-an`` distributive) — separate Phase
  5e Group D items. Not lifted by this commit.

## Phase 5e Commit 11: 3-argument plain DV (CAUS=NONE)

**Date:** 2026-05-02. **Status:** active.

Phase 5b's multi-GEN-NP rules were IV-only; Phase 5d Commit 4
added IV-INSTR / IV-REASON 3-arg variants; Phase 5e Commit 10
added pa-DV (CAUS=DIRECT) 3-arg. The remaining gap was **plain
DV (CAUS=NONE) ditransitives** like ``Sinulatan ng nanay ng
liham ang anak`` "Mother wrote a letter to the child", where
the AGENT and PATIENT are GEN-marked non-pivots and the
RECIPIENT is the NOM-marked DV pivot. Phase 5e Commit 11 fills
this in.

### New intrinsic profile

```python
_DV_TR_AGENT_PATIENT_RECIPIENT_THREE_ARG = {
    "AGENT":     (True, True),    # → OBJ-AGENT
    "PATIENT":   (True, True),    # → OBJ-PATIENT
    "RECIPIENT": (False, False),  # → SUBJ (the DV pivot)
}
```

Mirrors ``_DV_CAUS_DIRECT_THREE_ARG`` from Phase 5e Commit 10
but with AGENT instead of CAUSER and RECIPIENT instead of
LOCATION. Both choices are role-naming conventions; under the
LMT engine they map to the same typed OBJ-θ slots.

### New BASE entry

```text
WRITE-TO <SUBJ, OBJ-AGENT, OBJ-PATIENT>   sulat DV CAUS=NONE 3-arg
```

The "-TO" PRED suffix mirrors the pa-DV "-AT" convention so the
3-arg variant is distinguishable from the existing 2-arg
``WRITE <SUBJ, OBJ-AGENT>`` form (whose PRED stays bare for
backward compatibility with existing tests). Both lex profiles
coexist; lex lookup chooses based on NP count.

### Three top-level multi-GEN-NP grammar rules

Parallel to the Phase 5b pa-OV-direct and Phase 5e Commit 10
pa-DV rules, with ``V[VOICE=DV, CAUS=NONE]`` matching plain
(non-causative) DV:

```text
S → V[VOICE=DV, CAUS=NONE] NP[CASE=NOM] NP[CASE=GEN] NP[CASE=GEN]
   ↳ SUBJ=NOM (RECIPIENT), OBJ-AGENT=1st GEN, OBJ-PATIENT=2nd GEN
S → V[VOICE=DV, CAUS=NONE] NP[CASE=GEN] NP[CASE=NOM] NP[CASE=GEN]
S → V[VOICE=DV, CAUS=NONE] NP[CASE=GEN] NP[CASE=GEN] NP[CASE=NOM]
```

The first ng-NP is AGENT, the second is PATIENT — same Phase 5b
positional convention.

### Why only sulat for now

DV ditransitives are a relatively narrow construction in
Tagalog. ``sulat`` (write) is the canonical example because the
RECIPIENT pivot is animate (``ang anak``) and the PATIENT
(``ng liham``) is a typical written object. Other DV verbs
(``kain``, ``inom``, ``basa``) admit 2-arg DV readings (place
pivot or recipient pivot) but rarely surface with overt
PATIENT in the GEN slot — those constructions tend to use the
pa-DV form (the Phase 5e Commit 10 pattern) instead. Adding
3-arg plain-DV entries for the other anchors would be lex-only
and is deferred until corpus pressure justifies.

### Sentences enabled

- ``Sinulatan ng nanay ng liham ang anak.`` (GEN-GEN-NOM)
- ``Sinulatan ang anak ng nanay ng liham.`` (NOM-GEN-GEN)
- ``Sinulatan ng nanay ang anak ng liham.`` (GEN-NOM-GEN)
- IPFV aspect (``Sinusulatan ng nanay ng liham ang anak``)
- Negation under matrix (``Hindi sinulatan ng nanay ng liham
  ang anak``)

### Coexistence with the 2-arg reading

When the surface includes the GEN-GEN cluster, the parser
admits both the 3-arg reading (with overt OBJ-PATIENT) and a
2-arg reading where ``ng nanay ng liham`` is parsed as a
possessive ``mother's letter`` filling OBJ-AGENT. Both are
linguistically valid; the n-best list contains both. Tests
assert the 3-arg reading is among the parses.

### Out-of-scope (still deferred)

- **Plain DV 3-arg under control / ay-fronting.** The
  multi-arg-under-control patterns from Phase 5e Commits 9 and
  10 don't yet have plain-DV variants. Adding them mirrors the
  pa-OV / pa-DV approach.
- **3-arg plain DV for other anchor verbs.** Lex-only
  extensions; deferred until corpus pressure justifies.

## Phase 5e Commit 12: mag-...-an reciprocal / social

**Date:** 2026-05-02. **Status:** active.

Plan §10.1 Group D originally flagged ``ka-...-an`` as the
"reciprocal causative" affix. Investigation against
Schachter & Otanes 1972 §5.27, Ramos 1971, and R&B 1986
confirmed that the **well-attested reciprocal pattern is
``mag-...-an``**, not ``ka-...-an``. Tagalog ``ka-...-an`` is
more typically a noun-deriving pattern (``kahirapan``
"poverty", ``kasamahan`` "companionship") and isn't a verbal
voice/applicative. Phase 5e Commit 12 implements the attested
form (``mag-...-an``) under that name; the speculative
``ka-...-an`` is dropped from the deferral list.

### Construction

S&O 1972 §5.27 documents ``mag-...-an`` as the canonical
reciprocal / social form: an action performed cooperatively or
mutually by a plural SUBJ. The construction is a member of the
broader "social mood" inventory that Phase 4 §7.2 left as
inventory-only; this commit lifts it.

Examples:

- ``Nagkainan sila.`` "They ate together."
- ``Nagkakainan sila.`` IPFV.
- ``Magkakainan sila.`` CTPL.
- ``Nagbilihan sila.`` "They exchanged in trade."

### Implementation

**New affix class ``mag_an``** with three paradigm cells in
``data/tgl/paradigms.yaml``. Each cell carries
``feats: {MOOD: SOC, RECP: YES}``:

```text
PFV:  prefix("nag")  → suffix("an")            → nagkainan
IPFV: cv_redup → prefix("nag")  → suffix("an") → nagkakainan
CTPL: cv_redup → prefix("mag")  → suffix("an") → magkakainan
```

**Lex entries** for ``kain`` and ``bili`` reciprocal:

```text
EAT-TOGETHER  <SUBJ>   kain  AV MOOD=SOC
BUY-EXCHANGE  <SUBJ>   bili  AV MOOD=SOC
```

**Affix-class registration**: ``mag_an`` added to ``kain``'s
and ``bili``'s ``affix_class`` lists in ``data/tgl/verbs.yaml``.

### Discrimination via MOOD=SOC

The reciprocal lex's ``morph_constraints={..., "MOOD": "SOC"}``
ensures it only matches reciprocal MorphAnalyses (which carry
``MOOD=SOC``). Plain AV-intr lex entries (no MOOD constraint)
match BOTH plain and reciprocal MorphAnalyses under the
parser's non-conflict matcher. This produces a known
ambiguity: ``Nagkainan sila`` admits two parses — one with the
bare ``EAT <SUBJ>`` PRED, one with ``EAT-TOGETHER <SUBJ>``.
Both are well-formed; the natural reading depends on context
and lexical semantics, and tests assert the reciprocal reading
is among the n-best rather than asserting it's the only one.

This mirrors the Phase 5d / Phase 5e ambiguity pattern (e.g.,
multi-GEN-NP frame ambiguity, raising-vs-noun on
``mukha`` / ``baka``): both readings are linguistically valid;
ranker plus pragmatic disambiguation pick.

### Why MOOD=SOC and not a new VOICE feature

Three options were considered for the reciprocal feature:

1. New ``VOICE`` value (e.g., ``RECP``) — rejected: voice in
   Tagalog is a 4-way system (AV/OV/DV/IV) and adding a fifth
   would break the LMT engine's voice-aware mapping.
2. New top-level feature (``RECP=YES``) — partial: works as a
   discriminator but adds a feature with limited scope.
3. ``MOOD=SOC`` — chosen. The Phase 4 §7.2 inventory already
   listed SOC ("social") mood; reciprocal fits squarely under
   the social-mood semantic umbrella. Lifting it from
   inventory-only matches the original §7.2 plan-text intent.

Both ``MOOD=SOC`` and ``RECP=YES`` (boolean) are emitted on the
MorphAnalysis. Only ``MOOD=SOC`` (string-valued) propagates to
the f-structure under the parser's "string feats only" rule.
``RECP`` is informational at the morph level.

### Out-of-scope (still deferred)

- **Reciprocal with overt NP arguments.**
  ``Nagkainan sila ng isda`` "They ate fish together" admits
  the reciprocal SUBJ + an OBJ. The current lex profile is
  intransitive; transitive reciprocal (with a GEN-NP OBJ)
  would need a 2-arg lex profile.
- **Reciprocal under control / ay-fronting / nesting.** The
  reciprocal interacts with the existing control / fronting
  infrastructure but isn't pinned in this commit.
- **Other reciprocal anchor verbs.** Currently only ``kain``
  and ``bili``. ``basa`` reciprocal (``nagbasahan`` "read
  together / read at each other") would be a one-line
  addition.
- **`ka-...-an` re-classification.** The plan §10.1 Group D
  claim that ``ka-...-an`` is a reciprocal causative is
  retracted in this commit. The form is documented as a
  noun-derivation pattern in §18-style territory, but a future
  commit could survey actual ``ka-...-an`` verbal uses (some
  reflexive-like derivations exist in S&O 1972 §5.28); not
  pursued now.

## Phase 5e Commit 13: ``magpa-...-an`` distributive (reclassification)

**Date:** 2026-05-02. **Status:** active. Documentation-only
commit; no grammar / lex / morph / corpus / test changes.

The Phase 5e §10.1 Group D plan note paired ``ka-...-an``
reciprocal with ``magpa-...-an`` distributive as "causative
variants" parallel to ``pa-...-in`` and ``pa-...-an``.
Phase 5e Commit 12 already retired the ``ka-...-an`` claim
(the attested reciprocal pattern is ``mag-...-an``).
Phase 5e Commit 13 retires the ``magpa-...-an`` claim along
the same lines.

### Why this isn't a real form

Investigation against the available sources:

- **S&O 1972 §5.27** documents the Tagalog reciprocal as
  ``mag-...-an``; the distributive (the marker for "everyone
  / each one does X") is the existing ``mang-`` AV prefix
  (Ramos 1971 dictionary classifies it as AV-distributive in
  every paradigm table) and the ``magsi-`` collective form
  (less productive; S&O 1972 §5.27).
- **Ramos 1971 dictionary** organises every voice's paradigm
  as Indicative + Distributive, with the Distributive column
  always labelled ``MANG-`` — never ``magpa-...-an``.
- **R&B 1986 paradigm tables** mention the productive forms
  for each verb's affix-class membership; ``magpa-...-an``
  doesn't appear as a separate paradigm row.

The plan note appears to have been written by analogy with
the ``pa-...-in`` / ``pa-...-an`` causative pair without
external attestation. Tagalog distributive is a separable
construction from causative, marked by ``mang-`` (productive)
or ``magsi-`` (collective).

### Where Tagalog distributive lives now

- **``mang-``**: already implemented as the ``mang`` affix
  class (Phase 2C scale-up; documented in Phase 4 §7.7's
  applicative work). ``namili`` "shopped / went buying";
  ``namamasyal`` "stroll around". The morph analyzer
  generates these correctly via the existing ``nasal_substitute``
  sandhi op.
- **``magsi-``**: attested in S&O 1972 §5.27 but not
  exercised by the Phase 4 §7.10 corpus, the seeded R&G 1981
  fixtures, or the classic / S&O / Kroeger fixtures.
  Implementation would mirror Phase 5e Commit 12's
  ``mag_an`` shape (new affix class with PFV/IPFV/CTPL cells)
  but with ``prefix("nagsi")`` / ``prefix("magsi")`` and no
  suffix. Deferred until corpus pressure justifies — adding
  it now would over-engineer a marginal construction without
  test fixtures to anchor it.

### Where ``magpa-...-an`` lives now

§18 (genuinely v1-out-of-scope), with the explanation pinned
above. Revisit only if a corpus emerges where the construction
appears with non-trivial frequency.

### What this commit changes

Documentation only:

- Plan §10.1 Group D's ``magpa-...-an`` bullet is collapsed
  into a single re-classification note alongside the
  Commit 12 ``ka-...-an`` retraction.
- Plan §10.2 ("Items not enumerated above") gains the
  ``magpa-...-an`` bullet alongside the other reclassified
  items (resumptive pronouns, etc.).
- Plan §18 gains a ``magpa-...-an`` bullet with the why.
- This `docs/analysis-choices.md` section pins the rationale.
- `docs/coverage.md` "What's intentionally not covered" gains
  an entry.

### Out-of-scope (still deferred)

The reclassification doesn't itself defer anything new —
``magpa-...-an`` was already deferred via the Phase 5d
Commit 2 "other less-common causative variants" note. The
change is administrative: moving an item from
"additive Phase 5e candidate" to "v1-out-of-scope-as-named"
and pointing to the actually-attested distributive markers.

## Phase 5e Commit 14: AV mang- retain readings

**Date:** 2026-05-02. **Status:** active.

Schachter & Otanes 1972 §5.27 + Ramos 1971 paradigm tables
note that some bases admit a retain-pattern variant of the
``mang-`` distributive AV alongside the default drop pattern.
The retain pattern keeps the base's first consonant and adds a
homorganic nasal — exactly the same ``nasal_assim_prefix`` op
that Phase 5c §7.7 introduced for the ``ipang-`` IV-INSTR /
``ika-`` IV-REASON applicatives.

The two patterns can carry slightly different semantics
("habitual buyer / shopper" vs "engaging in the buying
activity") or be dialectal variants. Phase 5c §7.7 follow-on
flagged this as deferred; Phase 5e Commit 14 lifts it.

### Two patterns, same lex PRED

Both surface forms route to the same ``BUY <SUBJ>`` lex entry
because the existing AV-intransitive lex doesn't constrain on
the surface pattern. Roughly:

```text
drop:   mang- + bili → mami → mamili / namili / namimili / mamimili
retain: mang- + bili → namb → nambili / nambibili / mambibili
                                                   (no “mambili” form;
                                                    cv-redup is required
                                                    for IPFV / CTPL)
```

### Three new paradigm cells

In ``data/tgl/paradigms.yaml``, a new ``mang_retain`` affix
class with PFV / IPFV / CTPL cells:

```text
PFV:  nasal_assim_prefix("nang")                  → nambili
IPFV: cv_redup → nasal_assim_prefix("nang")       → nambibili
CTPL: cv_redup → nasal_assim_prefix("mang")       → mambibili
```

The cells use ``nasal_assim_prefix`` (retain) where the
existing ``mang`` cells use ``nasal_substitute`` (drop). PFV
prefix is ``"nang"`` (realis); CTPL prefix is ``"mang"``
(irrealis).

### Per-base flagging

The new ``mang_retain`` affix class is per-base. Currently only
``bili`` carries ``mang_retain`` in its
``affix_class`` list (``data/tgl/verbs.yaml``); other roots
that admit the retain pattern (e.g., ``tahi``, ``patay``) can
opt in by adding ``mang_retain`` to their list. Roots without
the flag don't generate retain-pattern surfaces:

```text
nambili    parses (bili HAS mang_retain in affix_class)
nankain    _UNK   (kain has neither mang nor mang_retain)
```

### Why route both forms to the same PRED

The semantic difference between drop and retain forms is
subtle and varies by source. Some sources treat them as
dialectal variants of the same predicate; others assign
slightly different aspectual readings (drop = habitual /
professional; retain = activity-engaged). Without
corpus-grounded distributional evidence to pin a stable
contrast, conflating both forms under ``BUY <SUBJ>`` is
the safer default. A future commit could add per-form
aspectual or pragmatic features if a corpus emerges that
distinguishes them.

### Out-of-scope (still deferred)

- **Other retain-pattern bases.** Currently only ``bili``.
  Other roots historically attested with retain-pattern
  variants (``tahi`` → ``nantahi``, ``patay`` → ``namatay``)
  could opt in via affix-class registration; not pursued here.
- **Per-form aspectual feats.** If corpus pressure reveals a
  systematic semantic contrast between drop and retain
  surfaces, a feature like ``MANG_PATTERN=DROP|RETAIN`` could
  ride on the morph analysis and route to distinct lex PREDs.
- **Retain pattern under control / ay-fronting.** The retain
  form is AV-intransitive; control / fronting compositions
  reuse the existing AV-intr infrastructure and should
  compose, but aren't pinned in this commit.

## Phase 5e Commit 15: other ``ipang-`` senses (reclassification)

**Date:** 2026-05-02. **Status:** active. Documentation-only
commit; no grammar / lex / morph / corpus / test changes.

The Phase 5e §10.1 Group D plan note flagged "Other ``ipang-``
senses" — specifically the purpose-nominal use of ``pang-``
(``pambili`` "for buying / shopping", ``pansulat`` "writing
instrument", ``pangkain`` "food"). These were listed as
additive lex entries that could land as separate noun lex
entries once corpus pressure surfaced specific tokens.

Phase 5e Commit 15 makes the deferral explicit: Phase 5c
§7.7 Commit 4 lifted the **verbal** ``ipang-`` IV-INSTR use of
the same ``pang-`` morpheme, but the **noun-deriving** uses
remain deferred.

### Why this isn't a Phase 5e implementation item

Three architectural / corpus considerations:

1. **They are nouns, not verbs.** The construction uses
   ``pang-`` to derive nouns from verbal roots
   (``bili`` → ``pambili``, ``sulat`` → ``pansulat``). The
   resulting forms function as NP heads or modifiers, not as
   clause heads. Implementing them as a productive paradigm
   would mean adding **nominal**-deriving morphology alongside
   the existing verbal paradigms — a meaningful extension to
   the morph engine.
2. **No corpus fixtures.** Neither the Phase 4 §7.10 reference
   corpus, the seeded R&G 1981 fixtures, nor the classic /
   S&O / Kroeger fixtures contain ``pambili``-like forms in
   testable contexts. Adding speculative noun entries without
   fixtures would bloat the seed without anchoring the
   construction's syntactic distribution.
3. **The lex-only approach is narrow.** The plan note's
   "additional senses can land as separate lex entries"
   suggests the path of least resistance: hand-author
   ``pambili`` etc. as nouns in ``data/tgl/nouns.yaml``.
   That's feasible and could be done one token at a time when
   a corpus surfaces specific cases — but it doesn't merit a
   Phase 5e item by itself.

### What ``ipang-`` already covers

Phase 5c §7.7 Commit 4 lifted the verbal ``ipang-`` IV-INSTR
applicative (``ipinambili`` "instrument-bought";
``ipinantahi`` "needle-sewed"). This is the productive
**verbal** use of ``pang-`` (``i-`` + ``pang-`` + V).
Phase 5e Commit 14 added the AV ``mang-`` retain pattern
(``nambili`` "engaging in buying"), which uses the same
``nasal_assim_prefix`` morphological op.

The remaining ``pang-`` uses (purpose nominals) fall outside
the verbal paradigm because they don't carry voice / aspect /
mood inflection — they're zero-inflected derived nouns.

### What it would take to lift

- **Lex-only path** (when corpus pressure surfaces tokens):
  add each form as a NOUN entry in ``data/tgl/nouns.yaml``,
  e.g., ``- citation: pambili, pos: NOUN, gloss: shopping
  money / for buying``. The existing N rules and NP-formation
  rules absorb them.
- **Productive-derivation path** (more ambitious): a new
  ``pang_n`` morphological class deriving NOUN from VERB
  roots, parallel to (but distinct from) the verbal
  ``ipang`` / ``mang_retain`` classes. This requires deciding
  the derived-noun's lex profile: PRED, SEM_CLASS, possible
  argument-frame inheritance from the source verb, etc.

Both paths are deferred to v1+ when corpus pressure justifies.

### Where it lives now

- Plan §10.1 Group D parenthetical noting the reclassification
  and pointer to §10.2 / §18.
- Plan §10.2 ("Items not enumerated above") gains the
  ``pang-``-purpose-nominals item (sixth item; the plan now
  flags this re-categorisation explicitly).
- Plan §18 gains a bullet articulating the rationale and the
  two implementation paths.
- This `docs/analysis-choices.md` section pins the rationale.

### Out-of-scope (still deferred)

The reclassification doesn't itself defer anything new — the
Phase 5c §7.7 follow-on already noted these as deferred. The
change is administrative: moving the item from "additive Phase
5e candidate" to "v1-out-of-scope as named, with two
implementation paths spelled out".

## Phase 5e Commit 16: pre-modifier demonstrative with linker

**Date:** 2026-05-02. **Status:** active. Lifts the §7.8
deferral on "Pre-modifier demonstrative with linker" noted as
out-of-scope under Phase 5d Commit 3. Sentences like
``Kumain itong bata`` ("this child ate") and
``Kinain nitong bata ang isda`` ("this child ate the fish")
now parse with the demonstrative serving as the determiner
(replacing ``ang`` / ``ng`` / ``sa``) followed by the linker
and the head N.

### Six grammar rules (3 cases × 2 linker variants)

```text
NP[CASE=NOM] → DET[CASE=NOM, DEM=YES] PART[LINK=…] N
NP[CASE=GEN] → ADP[CASE=GEN, DEM=YES] PART[LINK=…] N
NP[CASE=DAT] → ADP[CASE=DAT, DEM=YES] PART[LINK=…] N
```

PROX dems (``ito`` / ``nito`` / ``dito``) are vowel-final and
take the bound ``-ng`` linker — ``itong`` is split by
``split_linker_ng`` into ``ito`` + ``-ng``. MED dems (``iyan``
/ ``niyan`` / ``diyan``) and DIST dems (``iyon`` / ``niyon`` /
``doon``) are consonant-final and take the standalone ``na``
linker. The case-typed pattern in the rule's first child
enforces case agreement at the parser level.

### Equations: matrix shares dem, PRED projects from N

```text
(↑) = ↓1                  -- DET/ADP carries CASE/MARKER/DEIXIS
(↑ PRED) = ↓3 PRED         -- N supplies PRED
(↑ LEMMA) = ↓3 LEMMA
```

Unlike the post-modifier rule (where the head NP carries its
own case marker like ``ang`` and the dem only contributes
DEIXIS), the pre-modifier dem **replaces** the case marker —
the dem itself is the determiner. The head's PRED + LEMMA
project from the bare N (no inner DET); the dem's CASE,
MARKER, DEIXIS, DEM percolate to the matrix NP via the share
equation. This is structurally the mirror of Phase 5d Commit 3.

### Fifth left-context exception in `disambiguate_homophone_clitics`

The standalone ``na`` is homophonous between the LINK=NA
linker and the ASPECT_PART=ALREADY 2P enclitic. The Phase 4 /
5c / 5d disambiguator branched on prev-token POS:

- prev=NOUN/N → linker (already in place);
- prev=VERB/PRON → clitic (with three sub-exceptions);
- otherwise → keep both readings (placement decides).

For pre-modifier dems with MED / DIST (``iyan na bata`` /
``iyon na bata``), prev-token=DET/ADP and DEM=YES. Without an
explicit branch, the "otherwise" case kept both readings, but
``_is_clitic_token`` then sees the clitic reading and the
Wackernagel pass hoists ``na`` into the post-V cluster — the
linker reading dies before the new grammar rule can fire.

Phase 5e Commit 16 adds a fifth branch between the NOUN and
VERB/PRON arms:

```python
elif any(
    ma.pos in ("DET", "ADP") and ma.feats.get("DEM") == "YES"
    for ma in prev
):
    out.append([
        ma for ma in cands
        if ma.feats.get("is_clitic") is not True
    ])
```

When ``na`` follows a DEM-DET (``iyan`` / ``iyon``) or
DEM-ADP (``niyan`` / ``niyon`` / ``diyan`` / ``doon``), the
linker reading wins. The branch is guarded by ``DEM=YES`` so
plain DET / ADP entries (``ang``, ``ng``, ``sa``, ``si``,
``ni``, ``kay``) don't fire — those rarely precede ``na`` in
isolation, but the explicit guard keeps the branch tight.

PROX dems (``ito`` / ``nito`` / ``dito``) take the bound
``-ng`` linker, which has no clitic homophone, so this
disambiguator branch only matters for MED / DIST.

### Surface variants enabled

```text
itong bata           (NOM PROX, vowel-final dem + bound -ng)
iyan na bata         (NOM MED,  consonant-final dem + na)
iyon na bata         (NOM DIST, consonant-final dem + na)
nitong bata          (GEN PROX, in OV-actor or possessor)
niyan na bata        (GEN MED)
niyon na bata        (GEN DIST)
ditong palengke      (DAT PROX, in OBL-LOC or ADJUNCT)
diyan na palengke    (DAT MED)
doon na palengke     (DAT DIST)
```

Pre + post-modifier stacking on the same N (``itong batang
ito``) composes as expected — both rules fire and DEIXIS=PROX
is set consistently. R&B 1986 cites this stacked form as
common in spoken Tagalog.

### Out-of-scope (still deferred)

- **Demonstrative as modifier of a relativized head**
  (``ang batang ito na kumain`` "this child who ate"). The
  RC's linker would compete with the dem-modifier's linker;
  needs ranker-policy refinement. Phase 5e Commit 17.
- **Pre-modifier dem with N-internal modifiers between dem and
  head** (``itong matalinong bata`` "this intelligent child"
  with adjective). The current rule consumes a bare N; it
  doesn't recurse into adjective-modified N projections
  because §7.8 doesn't yet wire NP-internal adjective
  modification. Out of scope here — bundle with the future
  ADJ-modifier item if one is added.

### Why this lands as a pre-modifier-only commit

Both pre- and post-modifier dem-with-linker forms are
attested. Phase 5d Commit 3 implemented post-modifier; the
pre-modifier mirror is structurally simpler (dem replaces
case marker rather than coexisting with it) but interacts
with the ``na``-disambiguation pass in a way that needs the
fifth left-context branch. Bundling pre+post into one commit
would have obscured both interactions; splitting them keeps
each commit's contract self-contained.

## Phase 5e Commit 17: demonstrative on a relativized head

**Date:** 2026-05-02. **Status:** active. Lifts the §7.8 / §7.5
deferral on "Demonstrative as modifier of a relativized head"
noted as out-of-scope under Phase 5d Commit 3. Sentences like
``Tumakbo ang batang ito na kumain`` ("the child who ate ran")
now parse with the post-mod dem and the RC composing through
the existing Phase 5d Commit 3 + Phase 4 §7.5 rules. No new
grammar rules are added.

### Plan note vs. actual diagnosis

The Phase 5d Commit 3 deferral note read:

> The RC's linker would compete with the dem-modifier's linker;
> needs ranker-policy refinement.

Investigation showed the deferral note was inaccurate — the
construction wasn't being mis-ranked, it was failing to parse
at all. The root cause turned out to be a latent bug in the
Phase 5e Commit 16 disambiguator branch for ``na`` after a
demonstrative DET / ADP, not anything to do with rule
competition.

### The bug: boolean DEM compared as a string

Phase 5e Commit 16 added a fifth branch to
``disambiguate_homophone_clitics`` (in
``src/tgllfg/clitics/placement.py``) intended to keep the
standalone ``na`` as a linker when preceded by a
demonstrative DET / ADP. The branch read:

```python
elif prev is not None and any(
    ma.pos in ("DET", "ADP") and ma.feats.get("DEM") == "YES"
    for ma in prev
):
    out.append([ma for ma in cands if ma.feats.get("is_clitic") is not True])
```

The ``DEM`` feature is set in ``data/tgl/particles.yaml`` as

```yaml
- surface: ito
  pos: DET
  feats: {CASE: NOM, DEIXIS: PROX, DEM: YES}
```

PyYAML 1.1-style boolean parsing renders ``YES`` as the Python
boolean ``True`` (not the string ``"YES"``). The string
comparison ``== "YES"`` against ``True`` always returned
False, so the branch never fired. Phase 5e Commit 16's
MED / DIST cases (``Kumain iyan na bata``,
``Kumain iyon na bata``) still parsed only because the
clitic-pass moved the standalone ``na`` to clause-final as the
aspectual ``ALREADY`` enclitic and the bare-NP rule absorbed
the demonstrative DET as a determiner with DEIXIS percolating
to the matrix NP — the f-structure DEIXIS came out right but
the analytical structure was the fallback, not the new
pre-modifier-dem rule.

### Phase 5e Commit 17 fix

The corrected branch compares against the boolean directly:

```python
elif prev is not None and any(
    ma.pos in ("DET", "ADP") and ma.feats.get("DEM") is True
    for ma in prev
):
    out.append([ma for ma in cands if ma.feats.get("is_clitic") is not True])
```

With the branch finally firing, the standalone ``na`` after a
demonstrative is forced to the linker reading. Two
constructions are unblocked:

1. **The Phase 5e Commit 16 MED / DIST pre-modifier dem cases**
   now use the proper ``NP[CASE=NOM] → DET[CASE=NOM, DEM=YES]
   PART[LINK=NA] N`` rule (the Commit 16 grammar addition that
   was supposed to apply but didn't because of this disambiguator
   bug). The fallback path through the bare-NP rule no longer
   fires for this surface — the ``na`` stays in place rather
   than being moved to clause-final as ``ALREADY``.
2. **The dem-on-RC construction** (``ang batang ito na
   kumain``) parses by composing the existing Phase 5d Commit 3
   post-mod-dem rule with the Phase 4 §7.5 RC rule. The post-mod
   dem produces an NP[CASE=NOM] with DEIXIS percolated; the RC
   rule wraps that NP with the ``na`` linker and the SUBJ-gapped
   inner clause. No new grammar rule is needed — only the
   disambiguator fix unblocks the surface order the parser
   needed to see.

### Surface variants enabled

```text
ang batang ito na kumain          (NOM PROX, head-NG-dem-NA-RC)
ang batang iyan na kumain         (NOM MED)
ang batang iyon na kumain         (NOM DIST)
ang lalaki na ito na kumain       (head-NA-dem-NA-RC, two NAs)
ang batang ito na kumain ng isda  (transitive RC)
ng batang nito na kumain          (GEN-headed, OV-actor)
```

The RC body can carry any voice / aspect / argument frame the
existing Phase 4 §7.5 wrap rule supports — the dem on the head
NP is independent of the RC's internal shape.

### Why no new grammar rule is needed

The Phase 5d Commit 3 post-mod-dem rule produces
``NP[CASE=NOM]`` with DEIXIS percolated; the matrix's
f-structure is shared with the head NP's via ``(↑) = ↓1``. The
Phase 4 §7.5 RC wrap rule takes any ``NP[CASE=NOM]`` (or any
case) as the head, regardless of whether the head has DEIXIS or
not. The two rules compose by stacking:

```text
NP[CASE=NOM]
├── NP[CASE=NOM]            (post-mod-dem-d head)
│   ├── NP[CASE=NOM]        (bare ``ang bata``)
│   ├── PART[LINK=NG]       (bound linker)
│   └── DET[CASE=NOM, DEM=YES]  (``ito``)
├── PART[LINK=NA]           (RC linker)
└── S_GAP                   (``kumain``)
```

The disambiguator fix is the only change needed; the rules
were already in place.

### Out-of-scope (still deferred)

- **Pre-modifier dem on a relativized head**
  (``itong batang kumain`` "this child who ate"). Already
  works via the Phase 5e Commit 16 pre-mod-dem rule + Phase 4
  §7.5 RC rule — pinned by a regression test in this commit.
  Not a new construction; included as a regression check.
- **Dem on a relativized head where the RC itself contains a
  dem-modified NP**, e.g., ``ang batang ito na kumain ng
  isdang iyon`` "this child who ate that fish". Composes
  recursively; covered by existing rules. Not pinned in this
  commit (the recursive case is ordinary composition with no
  new analytical content).

## Phase 5e Commit 18: possessive-linker RC with consonant-final PRON

**Date:** 2026-05-02. **Status:** active. Extends Phase 5d
Commit 6's possessive-linker RC construction (``aklat kong
binasa`` "the book that I read") to the four consonant-final
GEN pronouns ``natin`` (1pl-INCL), ``namin`` (1pl-EXCL),
``ninyo`` (2pl), and ``nila`` (3pl).

### The construction

Phase 5d Commit 6 lifted the dual-binding form where a
pronominal RC actor is hoisted out of a non-AV RC and surfaces
as a possessor of the head NP, joined by a linker. Commit 6
covered only the three vowel-final GEN pronouns ``ko`` /
``mo`` / ``niya``, which fuse with the bound linker into a
single ``Vng`` orthographic word (``kong`` / ``mong`` /
``niyang``) and are split back apart by
:func:`tgllfg.text.split_linker_ng`.

The four consonant-final GEN pronouns end in ``n`` and so
cannot fuse with the bound ``-ng`` linker (Tagalog
phonotactics: ``-ng`` only attaches to vowel-final hosts).
Their analogous form uses the **standalone ``na`` linker**
instead:

```text
aklat namin na binasa     "the book that we (excl) read"
aklat natin na binasa     "the book that we (incl) read"
aklat ninyo na binasa     "the book that you (pl) read"
aklat nila na binasa      "the book that they read"
```

The vowel-final pronouns also admit the standalone-``na``
form alongside the fused ``-ng`` form:

```text
aklat ko na kinain       (= aklat kong kinain)
aklat mo na kinain       (= aklat mong kinain)
aklat niya na kinain     (= aklat niyang kinain)
```

Both linker variants carry the same f-equations.

### Enabling pieces already in place

Two of the three required pieces were already present from
prior commits and need no modification for Commit 18:

1. **Wackernagel placement keeps the consonant-final PRON in
   place** via the existing ``_is_post_noun_pron`` exception
   (Phase 5c §7.8 lift, lines 124–143 of
   ``src/tgllfg/clitics/placement.py``). The ``-ng``-linker
   variant needed a separate ``_is_pre_linker_pron`` exception
   (Phase 5d Commit 6) because the Vng-fused form was split
   back apart by ``split_linker_ng`` and the resulting PRON sat
   between two non-NOUN tokens. The standalone-``na`` form
   surfaces as a literal post-NOUN PRON, so the older
   ``_is_post_noun_pron`` rule applies directly.

2. **The post-PRON ``na`` is preserved as the linker** (rather
   than hoisted as the 2P aspectual ``ALREADY`` clitic) by the
   third left-context exception in
   ``disambiguate_homophone_clitics`` (Phase 5e Commit 6, lines
   305–325 of the same file). The branch fires whenever a
   PRON-after-NOUN is followed by a VERB (or NEG + VERB). It
   was originally added for the NP-internal possessive + RC
   case (``bata ko na nakita`` — head NOUN + possessor PRON +
   linker + standard RC), but the same pattern catches the
   Commit 18 dual-binding case.

### The change: extend the wrap rule

The only required change for Commit 18 is one extra iteration
in the wrap-rule loop in ``src/tgllfg/cfg/extraction.py``:

```python
for case in ("NOM", "GEN", "DAT"):
    np_cat = f"NP[CASE={case}]"
    for link in ("NA", "NG"):
        rules.append(Rule(
            np_cat,
            [np_cat, "PRON[CASE=GEN]", f"PART[LINK={link}]", "S_GAP_NA"],
            [
                "(↑) = ↓1",
                "(↑ POSS) = ↓2",
                "↓4 ∈ (↑ ADJ)",
                "(↓4 OBJ-AGENT) = ↓2",
                "(↓4 REL-PRO PRED) = (↓1 PRED)",
                "(↓4 REL-PRO CASE) = (↓1 CASE)",
                "(↓4 REL-PRO) =c (↓4 SUBJ)",
            ],
        ))
```

This mirrors the standard relativization wrap rule a few lines
above (``NP → NP PART[LINK=NA|NG] S_GAP``), which has long
admitted both linker variants in parallel. The dual-binding
``(↑ POSS) = ↓2`` and ``(↓4 OBJ-AGENT) = ↓2`` is unchanged.

### Why no rule competition with the standard RC wrap

The standard relativization wrap rule (``NP[CASE=X] → NP[CASE=X]
PART[LINK=X] S_GAP``) admits both linker variants and could in
principle compete with the Commit 18 wrap rule on surfaces like
``aklat namin na binasa``. It does not, for two reasons:

1. The standard wrap rule consumes 3 daughters (NP + linker +
   ``S_GAP``); the Commit 18 wrap rule consumes 4 daughters (NP
   \+ PRON + linker + ``S_GAP_NA``). The PRON token is part of
   the head NP under the standard rule (consumed by
   ``NP → NP PRON`` for pronominal possessor), but is consumed
   separately under the Commit 18 rule. These are different
   tree shapes, and the parser explores both.

2. ``S_GAP`` requires the actor slot to be filled by an overt
   GEN-NP (or to be the gap itself); ``S_GAP_NA`` explicitly
   has no overt GEN-NP, with the actor (``OBJ-AGENT``) supplied
   externally by the wrap rule. For surfaces without an overt
   GEN-NP after the V, only ``S_GAP_NA`` succeeds. For surfaces
   *with* an overt GEN-NP after the V (``aklat na binasa nila``
   "the book that they read", standard relativization with the
   actor staying inside the RC), only ``S_GAP`` succeeds.

The two analyses surface in different clusters of constructions
and don't generate spurious parses for either.

### Surface variants enabled

```text
lumakad ang bata namin na binasa    (1pl-EXCL, SUBJ position)
lumakad ang bata natin na binasa    (1pl-INCL)
lumakad ang bata ninyo na binasa    (2pl)
lumakad ang bata nila na binasa     (3pl)
kumain ang bata ng libro nila na binasa   (OBJ position)
lumakad ang bata namin na hindi binasa    (RC under inner NEG)
lumakad ang bata ko na kinain       (vowel-final PRON + standalone na)
lumakad ang kapatid namin na binasa (consonant-final HEAD + PRON)
lumakad ang bata namin na binasahan (DV variant)
lumakad ang bata namin na ipinaggawa (IV bare)
lumakad ang bata namin na ipinagsulat sa kapatid (IV + DAT)
```

The id-equality between ``POSS`` and the RC's ``OBJ-AGENT``
(the dual-binding signature) is asserted by
``test_poss_and_obj_agent_share_node`` in
``tests/tgllfg/test_possessive_linker_rc_consonant_pron.py``.

### Non-AV voice coverage

Phase 5d Commit 6's grammar code admitted OV / DV / IV in
``S_GAP_NA`` but its tests only exercised OV. Commit 18 also
pins DV and IV with consonant-final pronouns:

- **OV** — ``binasa`` / ``kinain`` (most common; the canonical
  patient-pivot case where the actor is extracted as POSS).
- **DV** — ``binasahan`` (DV PFV of ``basa`` is the only DV
  form with full analyzer coverage in the seed lexicon; other
  DV PFVs like ``binigyan`` / ``binilhan`` / ``kinanan`` are
  ``_UNK`` to the morph analyzer and would parse only after a
  paradigm-cell expansion).
- **IV** — ``ipinaggawa`` (BEN bare), ``ipinagsulat`` (BEN
  with DAT adjunct ``sa kapatid``). The S_GAP_NA IV frames
  are ``[v_cat]`` (bare) and ``[v_cat, NP[CASE=DAT]]`` (DAT
  adjunct only — no overt GEN-NP, since the actor is the gap).

### POSS-EXTRACTED guard (also fixes a pre-existing Commit 6 spurious parse)

Phase 5d Commit 6 had a latent issue that surfaced cleanly only
once Commit 18's testing was thorough: when the surface combined
the dual-binding wrap rule with an overt GEN-NP after the verb
(e.g., ``Tumakbo ang bata kong kinain ng aso`` "the child of-mine
whom the dog ate ran"), the chart parser produced an extra
"hybrid" parse where the standard NP-internal possessive rule
fired on the wrap-rule output:

```text
[bata ko na kinain]_NP[POSS=ko]  +  ng aso  →
    NP[POSS = unify(ko, aso)]
```

The unification succeeded because ``ko`` (PRON) had no LEMMA /
MARKER and ``aso`` (NOUN) had no PERS / NUM — they're feature-
compatible. The dual binding ``(↑ POSS) = ↓2`` and ``(↓4
OBJ-AGENT) = ↓2`` then made OBJ-AGENT also point to this
hybrid fstruct, so the RC's actor became a strange merger of
``ko``'s pronominal features and ``aso``'s nominal lemma.
Existing tests passed because they used ``_find_…`` helpers
that scanned the n-best list for any parse with the desired
shape — the spurious hybrid was just noise alongside the
intended parses.

Commit 18 fixes this in three pieces:

1. **The wrap rule marks its output**: a new equation
   ``(↑ POSS-EXTRACTED) = 'YES'`` added to the wrap rule's
   equations records that the POSS slot was filled by actor
   extraction (not by an external GEN-NP modifier).

2. **The §7.8 NP-internal possessive rule guards against it**:
   a constraining equation ``¬ (↑ POSS-EXTRACTED)`` rejects
   the rule when applied to an NP whose POSS slot was already
   filled by extraction.

3. **Right-associative iterated possessives are unaffected**:
   the standard NP-poss rule does NOT set POSS-EXTRACTED, so
   stacking it (``aklat ng bata ng pamilya`` → libro.POSS=bata,
   bata.POSS=pamilya) continues to work.

The guard applies symmetrically to both linker variants — it
also removes the same hybrid parse from Phase 5d Commit 6's
``-ng`` form (``bata kong kinain ng aso``). After the fix:

```text
'Tumakbo ang bata ko na kinain ng aso.'   3 parses → 2 parses
'Tumakbo ang bata kong kinain ng aso.'    3 parses → 2 parses
```

The 2 remaining parses are the intended one (POSS=PRON,
OBJ-AGENT=NOUN, distinct fstructs) and a separate analysis
where the RC's actor is gapped differently — both linguistically
sensible. Pinned by ``TestPossessiveExtractedGuard`` in the
Commit 18 test file.

### Lifted in Phase 5e Commit 19

- **Non-pronominal possessors with linker** (``aklat ng batang
  binasa``, ``aklat ni Juan na binasa``). See the next entry.

## Phase 5e Commit 19: possessive-linker RC with non-pronominal possessor

**Date:** 2026-05-02. **Status:** active. Extends Phase 5d
Commit 6 + Phase 5e Commit 18's pronominal possessive-linker RC
construction to **non-pronominal possessors** — common nouns and
proper names. The grammar change is a one-token widening of the
wrap rule's second daughter from ``PRON[CASE=GEN]`` to
``NP[CASE=GEN]``, plus a head-NP existential constraint to keep
the rule from spuriously firing on PRON-headed NPs.

### The construction

The dual-binding shape introduced in Commit 6 (PRON possessor)
extends naturally to NOUN / proper-noun possessors:

```text
aklat ng batang binasa     "the book that the child read"
aklat ng asong kinain      "the book that the dog ate"
aklat ni Juan na binasa    "the book that Juan read"
aklat ni Maria na binasa   "the book that Maria read"
```

In each case the GEN-marked possessor (``ng bata``, ``ng aso``,
``ni Juan``, ``ni Maria``) is BOTH the head NP's POSS AND the
embedded RC's OBJ-AGENT — exactly the same dual binding as the
pronominal cases. The linker variant (``-ng`` bound vs ``na``
standalone) follows the host's phonotactics.

### The grammar change: one-token widening

The Commit 18 wrap rule was:

```python
NP[CASE=X] → NP[CASE=X] PRON[CASE=GEN] PART[LINK=L] S_GAP_NA
```

Widened to:

```python
NP[CASE=X] → NP[CASE=X] NP[CASE=GEN] PART[LINK=L] S_GAP_NA
```

The Phase 4 §7.8 grammar already has ``NP[CASE=GEN] →
PRON[CASE=GEN]`` as a unit rule, so widening from
``PRON[CASE=GEN]`` to ``NP[CASE=GEN]`` is a strict
generalization that subsumes the PRON case. Pronominal
possessors continue to parse via the PRON-to-NP unit rule; NOUN
and proper-noun possessors now also parse directly.

### The head-LEMMA constraint

A new existential constraint ``(↓1 LEMMA)`` is added to the wrap
rule's equations. It fires only when the head NP carries LEMMA in
its f-structure. NOUNs and proper nouns do; PRONs and
headless-RC NPs do not.

**Why the constraint is needed**: without it, the widened
``NP[CASE=GEN]`` slot lets the rule fire on surfaces where it
shouldn't. E.g., ``Kumain ako ng batang kinain niya`` ("I ate the
child that he ate") had a spurious extra parse where ``ako``
(PRON-NOM, no LEMMA) was bound as the head NP and ``ng bata`` was
its dual-bound possessor + RC actor. The intended analysis is
``ako = SUBJ`` and ``ng batang kinain niya = OBJ`` (with internal
standard RC). The constraint blocks the spurious head-binding by
requiring the head NP to be NOUN / proper-noun (LEMMA-bearing).

The constraint is also semantically motivated: the construction
"X with possessor Y where Y is also the actor" only makes sense
with X being a possessable thing, which in Tagalog means a NOUN or
proper noun — pronouns aren't possessable in this shape.

### Surface variants enabled

```text
lumakad ang libro ng batang binasa     (common-noun possessor, NG marker, -ng linker)
lumakad ang libro ng asong kinain      (different head + different verb)
lumakad ang libro ni Juan na binasa    (proper-noun possessor, NI marker, na linker)
kumain ang aso ng libro ng batang binasa   (OBJ-position case)
lumakad ang libro ng batang hindi binasa   (RC under inner NEG)
lumakad ang libro ng batang ipinaggawa     (IV variant)
```

The id-equality between ``POSS`` and the RC's ``OBJ-AGENT``
(the dual-binding signature) is asserted by
``test_poss_and_obj_agent_share_node`` in
``tests/tgllfg/test_possessive_linker_rc_noun.py``.

### Composition with prior commits unchanged

The widening preserves all earlier behavior:

- **Pronominal cases** (Commit 6 / Commit 18) — unchanged. Pinned
  by ``test_pronominal_commit_6_still_works`` and
  ``test_pronominal_commit_18_still_works``.
- **Standard NP-poss + standard relativization** (``libro na
  binasa ng bata``) — unchanged. The wrap rule requires
  ``PART[LINK=L] + S_GAP_NA``, which doesn't fit a surface where
  the actor stays inside the RC; the standard ``S_GAP`` path is
  used instead. Pinned by
  ``test_standard_relativization_with_overt_actor``.
- **Right-associative iterated possessives** (``libro ng bata ng
  pamilya``) — unchanged. The POSS-EXTRACTED guard from Commit 18
  only blocks NP-poss extension on wrap-rule outputs; legitimate
  iterated chains formed by repeated NP-poss applications are
  not marked as POSS-EXTRACTED. Pinned by
  ``test_iterated_npposs_unaffected``.

### Rule competition (none)

Three sources of structural ambiguity to consider, all resolved:

1. **NOUN possessor + RC vs standard NP-poss + standard RC**.
   For ``libro ng batang binasa``, the standard NP-poss + RC
   path requires ``binasa`` (OV) to fit ``S_GAP``, which needs an
   overt GEN actor. Without an actor inside the RC, ``S_GAP``
   fails. Only the new wrap rule succeeds. No competition.
2. **Recursive NP[GEN] possessor**. ``libro ng bata ng pamilya
   na binasa`` (the family-of-the-child read the book) could in
   principle match the wrap rule with the recursive ``ng bata ng
   pamilya`` as the dual-bound possessor. The grammar admits
   this; semantics is "the family is the actor and possessor".
   The intended right-associative reading is preserved; the
   recursive-possessor reading is also produced for chart
   completeness.
3. **PRON-headed NP as the head**. The ``(↓1 LEMMA)`` constraint
   blocks this — see "The head-LEMMA constraint" above.

## Phase 5e Commit 20: kita clitic fusion

**Date:** 2026-05-02. **Status:** active. Adds the special
second-position clitic ``kita`` that fuses the 1sg-GEN actor and
2sg-NOM SUBJ of a non-AV verb into a single token: ``Kinain
kita`` "I ate you", ``Sinulatan kita ng liham`` "I wrote you a
letter", ``Pinakain kita ng kanin`` "I fed you rice", ``Hindi
kita kinain`` "I didn't eat you". The fusion is obligatory in
modern Tagalog (Schachter & Otanes 1972 §3.2; Kroeger 1993
§2.2) — the alternative ``*Kinain ko ka`` is ungrammatical.

### Lex layer

A single new entry in ``data/tgl/pronouns.yaml``:

```yaml
- surface: kita
  feats: {KITA: YES}
  is_clitic: true
```

The lex carries only the marker ``KITA: YES``; the per-argument
person/number/case feats are supplied by grammar equations (the
lex loader doesn't support nested feats, so we can't put both
1sg-GEN and 2sg-NOM bundles in a single PRON entry).

The surface ``kita`` also exists as a verb root in
``data/tgl/verbs.yaml`` (``kita`` = "see, meet"), but the verb
is never used as a bare lemma — it always appears with affixes
(``kumita`` AV, ``kinita`` OV, ``nakita`` NVOL). The morph
analyzer returns the PRON analysis for bare ``kita``, and the
chart parser can also use the verb analysis for affixed forms;
no ambiguity in practice.

### Grammar layer

``src/tgllfg/cfg/clitic.py`` adds a per-voice loop that mirrors
the standard non-AV ``voice_specs`` structure used elsewhere:

```python
kita_voice_specs = [
    ("OV", "OBJ-AGENT", [("CAUS", "NONE")]),
    ("OV", "OBJ-CAUSER", [("CAUS", "DIRECT")]),
    ("DV", "OBJ-AGENT", [("CAUS", "NONE")]),
    ("DV", "OBJ-CAUSER", [("CAUS", "DIRECT")]),
    ("IV", "OBJ-AGENT", []),
]
```

For each ``(voice, obj_target, extras)`` triple, three frame
variants:

1. **Bare** (``V kita``): ``Kinain kita``, ``Binasahan kita``,
   ``Ipinaggawa kita``, ``Pinakain kita``.
2. **With overt PATIENT** (``V kita NP[GEN]``): ``Sinulatan
   kita ng liham``, ``Pinakain kita ng kanin``,
   ``Ipinaggawa kita ng silya``.
3. **With DAT adjunct** (``V kita NP[DAT]``): peripheral
   recipient / location adjuncts.

The dual binding sets atomic values:

```text
(↑ SUBJ PERS)             = '2'
(↑ SUBJ NUM)              = 'SG'
(↑ SUBJ CASE)             = 'NOM'
(↑ <obj_target> PERS)     = '1'
(↑ <obj_target> NUM)      = 'SG'
(↑ <obj_target> CASE)     = 'GEN'
```

The ``<obj_target>`` per voice spec routes the 1sg actor to the
right typed slot:

- OV / DV with ``CAUS=NONE`` → ``OBJ-AGENT`` (plain non-AV
  transitive).
- OV / DV with ``CAUS=DIRECT`` → ``OBJ-CAUSER`` (pa-causatives;
  the 1sg actor is the CAUSER, not the AGENT).
- IV (any APPL) → ``OBJ-AGENT``.

This routing matches the lexicon's expected PRED arity for each
voice. For example, ``Pinakain kita ng kanin`` produces
``CAUSE-EAT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>`` with SUBJ=2sg
(CAUSEE), OBJ-CAUSER=1sg (the one who fed), OBJ-PATIENT=kanin.

### Wackernagel placement

``kita`` is marked ``is_clitic: true`` in the lex, so the
existing §7.3 Wackernagel pass (``src/tgllfg/clitics/placement.py``)
treats it like any pronominal clitic: pre-V occurrences are
hoisted into the post-V cluster. ``Hindi kita kinain`` reorders
to ``hindi kain kita`` after placement, matching the surface
expectation. No new placement code was needed.

### Note on the 'kita' pronoun's atomic-value equations

The kita rule is the first place in the grammar that uses
``(↑ <gf> ATTR) = 'value'`` to *create* the GF f-structure
purely from grammar equations rather than by structure-sharing
with a daughter f-structure (``(↑ <gf>) = ↓N``). The unifier
handles this transparently: the equations create the GF
sub-fstruct on the fly, with each atomic-value equation either
defining or constraining the corresponding feature.

A side benefit: the PRON entry's flat ``feats`` dict
(``{KITA: YES}``) is sufficient lex-side. We don't need a
nested-feats schema (``feats: {SUBJ: {PERS: 2, ...},
OBJ-AGENT: {PERS: 1, ...}}``) to encode the dual binding.

### Surface variants enabled

```text
kinain kita              (OV bare)                   "I ate you"
binasahan kita           (DV bare)                   "I read at you"
ipinaggawa kita          (IV-BEN bare)               "I made (sth) for you"
pinakain kita            (pa-OV bare, CAUSER=1sg)    "I fed you"
sinulatan kita ng liham  (DV 3-arg + PATIENT)        "I wrote you a letter"
ipinaggawa kita ng silya (IV-BEN 3-arg + PATIENT)    "I made you a chair"
pinakain kita ng kanin   (pa-OV 3-arg + PATIENT)     "I fed you rice"
hindi kita kinain        (NEG, kita hoisted)         "I didn't eat you"
kinain na kita           (adv enclitic + kita)       "I already ate you"
```

### Out-of-scope (paradigm coverage gaps)

- **OV-NVOL of ``kita`` (``Nakita kita`` "I saw you")** — the
  canonical example in grammar texts. The current ma-class
  paradigm only emits AV-NVOL forms; ``nakita`` analyses as
  AV-NVOL only. Adding OV-NVOL ma-class cells is a paradigm
  coverage follow-up, not a grammar / kita-fusion limitation.
  Tracked as a TBD alongside the DV PFV gap from Phase 5e
  Commit 18 (see plan §18 entries "DV PFV paradigm coverage
  gap" — analogous form needed for OV-NVOL).
- **PERS feature not propagated through standard PRON entries.**
  Pre-existing parser quirk: ``_lex_equations`` in
  ``src/tgllfg/parse/earley.py`` filters PRON feats to keep only
  string-typed values. ``pronouns.yaml`` encodes ``PERS: 1`` as
  a YAML integer, which gets dropped. This affects every PRON
  in the lexicon (``ako``, ``ko``, ``mo``, etc.), not just
  ``kita``. The kita fusion sidesteps the issue by setting PERS
  via grammar equations as string literals (``'1'``, ``'2'``).
  Lifting the lex/parser filter to allow integer PERS is a
  Phase 5+ engineering follow-up — same shape as the DV / NVOL
  paradigm gaps.

## Phase 5e Commit 21: SOC mood (hortative) with `tayo` 1pl-INCL pivot

**Date:** 2026-05-02. **Status:** active. Lifts the Phase 4 §7.2
``MOOD=SOC`` inventory entry for the hortative case ("let's X").
The SOC mood was already partially lifted by Phase 5e Commit 12
for the ``mag-...-an`` reciprocal; this commit completes the
deferral by adding the bare ``mag-`` + base hortative form.

### The construction

The hortative uses the bare ``mag-`` + base form (no CV-redup,
no realis prefix) with the 1pl-INCL pivot ``tayo``:

```text
Magkape tayo.            "Let's have coffee."        (canonical)
Maglinis tayo ng kuwarto. "Let's clean the room."
Magsayaw tayo.           "Let's dance."
Magkanta tayo.           "Let's sing."
Magpasyal tayo.          "Let's take a walk."
Magsulat tayo ng liham.  "Let's write a letter."
Maglaba tayo ng damit.   "Let's wash clothes."
```

The same morphological surface is also the IMP form for
2nd-person SUBJs (``Maglinis ka`` "Clean!" — addressee
imperative). The IMP variant lifts in a separate commit
(Group G item 3, ``huwag-MOOD lift``); for now, MOOD=SOC is
asserted at the morph level, and other PRON SUBJs that match
the standard AV S frame produce semantically odd but
grammatically well-formed parses (e.g., ``Maglinis ako`` parses
as MOOD=SOC with 1sg SUBJ).

### Paradigm cell

A new cell in ``data/tgl/paradigms.yaml`` between the existing
mag-CTPL/IND cell and the next paradigm section:

```yaml
- voice: AV
  aspect: CTPL
  mood: SOC
  transitivity: ''
  affix_class: mag
  feats: {MOOD: SOC}
  operations:
    - {op: prefix, value: "mag"}
  notes: maglinis, magbigay (mag- + base for hortative SOC; takes 1pl-INCL `tayo` SUBJ)
```

The cell uses ``aspect: CTPL`` (the closest existing aspect to
"irrealis / non-finite") and ``mood: SOC`` to distinguish from
the existing CTPL/IND cell (which adds ``cv_redup`` and
produces ``maglilinis`` etc.). Different surfaces, no shadowing.

The ``operations`` list contains just ``{op: prefix, value:
"mag"}`` — no CV-redup, no realis. For any mag-class root, the
cell emits ``mag-`` + base verbatim.

### Denominal `kape` verb

To support the canonical ``Magkape tayo`` example, ``kape``
(originally a NOUN: "coffee") is also added as a VERB with
``affix_class: [mag]``:

```yaml
- citation: kape
  pos: VERB
  gloss: have coffee
  transitivity: INTR
  affix_class: [mag]
```

This dual NOUN+VERB pattern is already attested in the seed
lexicon (``trabaho``, ``tao``, ``gulay``, ``gutom``, ``salita``
all carry both POS analyses). The mag-NOUN denominal pattern is
productive in Tagalog (``magkape`` "drink coffee", ``magbahay``
"build a house", ``magsasaka`` "be a farmer"); the seed picks
just ``kape`` for the canonical example. Other denominal
mag-verbs lift trivially by adding the same dual entry.

### No new grammar rules needed

The existing AV S frames carry MOOD from V to matrix without
modification:

- ``S → V[VOICE=AV] NP[CASE=NOM]`` (intransitive AV)
- ``S → V[VOICE=AV] NP[CASE=NOM] NP[CASE=GEN]`` (transitive AV
  via the standard ``voice_specs`` loop)
- ``S → V[VOICE=AV] NP[CASE=NOM] NP[CASE=DAT]`` (intransitive
  AV + DAT adjunct)

For ``Magsayaw tayo``, the intransitive frame fires with V
being ``magsayaw`` (V[VOICE=AV, MOOD=SOC]) and SUBJ being
``tayo`` (NP[CASE=NOM]). MOOD=SOC propagates from V to matrix
via the implicit feature inheritance. ``tayo``'s lex feats
(NUM=PL, CLUSV=INCL, CASE=NOM) propagate to SUBJ.

For ``Maglinis tayo ng kuwarto``, the transitive frame fires
similarly with the addition of OBJ=kuwarto.

### The `tayo` constraint is implicit, not enforced

The grammar doesn't constrain SOC to require ``tayo`` as the
SUBJ — any NP[CASE=NOM] would match the AV S frame. So
``Maglinis ako.`` parses as MOOD=SOC with 1sg-NOM SUBJ
(semantically odd: the SOC reading needs 1pl-INCL). This is a
deliberate scope choice for v1: the SOC/IMP mood ambiguity
requires either (a) PRON-PERS-aware grammar rules (the PERS
feature is currently filtered out by the lex/parser quirk noted
in Commit 20's docs) or (b) a richer mood inventory
distinguishing INFINITIVE / NON-FINITE from SOC and IMP. Both
are tractable Phase 5+ extensions. For now, SOC is asserted at
the morph level and the construction works canonically with
``tayo`` (the only context where the SOC reading is canonical).

### Out-of-scope

- **SOC negation with ``huwag``** (``Huwag tayong magkape``
  "Let's not have coffee"). The interaction between ``huwag``'s
  IMP particle and the SOC mood requires the Group G item 3
  huwag-MOOD lift to be in place first. Tracked as a TBD.
- **IMP variant** (``Magkape ka`` "Have coffee!"). Same surface
  form, but PRON SUBJ is 2nd-person. Needs PERS-aware grammar
  rules; see the PERS-filtering note in Commit 20's docs.
- **Other denominal mag-NOUN verbs** (``magtanim`` "plant",
  ``magbahay`` "build a house", ``magkotse`` "drive a car",
  etc.). Each requires adding the noun's dual VERB entry. The
  seed picks just ``kape`` for the canonical example; expanding
  is a small lex-data follow-up driven by corpus pressure.

## Phase 5e Commit 22: verbless clitic placement

**Date:** 2026-05-02. **Status:** active. Lifts the Phase 4 §7.3
verbless-fragment deferral. The Wackernagel placement pass was
verb-anchored: when no VERB token appeared in the input, the
pass returned the analyses unchanged. This left verbless
predicate constructions like ``Maganda na ka`` "You're beautiful
already" or ``Hindi ka maganda`` "You're not beautiful" without
proper clitic placement — even though the cluster ordering rules
themselves don't depend on the anchor being a verb.

### The change: fallback anchor lookup

A new helper ``_find_verbless_anchor`` in
``src/tgllfg/clitics/placement.py`` returns the first token
that's:

- Not a clitic (PRON-clitic or PART-2P-clitic).
- Not ``PART[POLARITY=NEG]`` (``hindi``, ``huwag``).
- Not punctuation.

When no VERB exists, this anchor takes the verb's place in the
cluster machinery. The PRON post-anchor cluster, the adv
enclitic clause-end placement, and the existing post-NOUN /
pre-linker / post-embedded-V exceptions all carry over
unchanged.

When a VERB is present, the verb-anchor wins (existing
behavior). The fallback only fires for genuinely verbless
inputs.

### Anchor selection rationale

The anchor is the first **predicate-like** token. Tagalog
verbless predicates can be:

- **Adjective predicates** — ``Maganda ka.`` "You're
  beautiful" (the predicate-adj construction is Phase 5g; the
  placement-pass change here covers the cluster shape so it's
  ready when 5g lands).
- **Noun predicates** — ``Bata ka.`` "You're a child"
  (equational with NOUN predicate).
- **Locative predicates** — ``Dito ka.`` "You're here" (ADP
  locative dem as predicate).
- **PP / quantifier predicates** — also covered.

Pre-anchor tokens ``hindi`` / ``huwag`` (NEG-PART) are skipped
during anchor lookup, mirroring the verb-anchored behavior
(NEG sits pre-V; the V is the anchor).

### Interaction with the §7.5 ``na``-disambiguator

The Phase 5e Commit 6 ``na``-disambiguator treats post-NOUN
``na`` as the linker rather than the adv enclitic
(``Tumakbo ang bata ko na nakita`` — ``na`` introduces the RC,
not ALREADY). This applies to verbless inputs too — ``Bata na
ka.`` parses with ``na`` as a linker, leaving only ``ka`` as the
PRON-clitic to cluster.

For unambiguous adv-enclitic cases (``Maganda na ka.`` —
``maganda`` is ADJ-_UNK so the disambiguator's NOUN branch
doesn't fire), ``na`` keeps its is_clitic reading and is pulled
to clause-end as expected.

### Surface variants enabled

```text
Maganda na ka.        → maganda ka . na     (PRON cluster + adv at end)
Maganda ba ka.        → maganda ka . ba     (interrogative ba)
Maganda na ka ba.     → maganda ka . na ba  (PRON + 2 advs)
Hindi ka maganda.     → hindi maganda ka .  (NEG + pre-anchor PRON hoist)
Hindi na ka maganda.  → hindi maganda ka . na   (NEG + adv + pre-anchor PRON)
```

Tests pin the cluster shape at the placement layer
(``tests/tgllfg/test_verbless_clitic_placement.py``). End-to-end
parse coverage of these surfaces is gated on Phase 5g
(adjectives) — most verbless predicate constructions need the
predicative-adj clause type to land. The placement-pass change
is intentionally ahead of 5g so the cluster ordering is correct
when 5g composes.

### No corpus change

This commit is a placement-pass-only change. Corpus parse
coverage is unchanged (the verbless surfaces still don't parse
at the grammar level until Phase 5g lands). The 19 new tests
pin behavior at the unit level only.

## Phase 5e Commit 23: non-AV RECPFV (reclassification)

**Date:** 2026-05-02. **Status:** active. Documentation-only
commit; no grammar / lex / morph changes.

The Phase 4 §7.2 "Out-of-scope" note flagged Recent Perfective
as restricted to AV (the existing ``ka-`` + CV-redup paradigm
cells cover only AF / um / mag / ma classes), and plan §10.1
Group G carried "Non-AV RECPFV" forward as a Phase 5e
candidate, claiming non-AV bases were attested with ``kaka-``
\+ redup. On investigation against the *Handbook of Tagalog
Verbs* (Ramos & Schachter; the companion volume to Teresita
Ramos's dictionary), the claim doesn't hold up — every
paradigm entry in the Handbook lists Recent Perfective only
under AF (Actor Focus) and A2F (Actor Focus, mag-class),
never under OF (Object Focus), DF (Directional Focus), IF
(Instrumental Focus), BF (Benefactive Focus), LF (Locative
Focus), or RF (Reason Focus). Phase 5e Commit 23 reclassifies
the item to plan §18 (genuinely v1-out-of-scope) and pins the
rationale here.

### What the Handbook actually shows

A representative entry for the verb ``abot`` "reach for"
(Handbook line 219+ in the OCR):

```text
Indicative AF Inf. umabot; Perf. umabot;
              Imperf. umaabot; Cont. aabot;
              Rec. Perf. kaaabot          ← AV with `-um-`

A2F Inf. mag-abot; Perf. nag-abot;
    Imperf. nag-aabot; Cont. mag-aabot;
    Rec. Perf. kaaabot                    ← AV with `mag-`

OF Inf. abutin; Perf. inabot;
   Imperf. inaabot; Cont. aabutin         ← NO Rec. Perf.

[OF entries for Aptative, Causative, etc. — none with Rec. Perf.]
```

The pattern repeats for every verb the Handbook lists (~200
high-frequency verbs). Recent Perfective is paradigmatically
an AF-only form. The Handbook's analysis matches Schachter &
Otanes 1972 §5.31 ("The recent-perfective formation occurs
primarily with actor-focus verbs") and Kroeger 1993's broader
treatment of Tagalog aspect.

### What the surface ``kaka-V-base`` does in non-AV contexts

The AF Recent Perfective surface (``kakakain``, ``kabibili``,
``kasusulat``, etc.) IS sometimes used in syntactically OV-like
contexts:

```text
Kakakain ko ang isda.   "I just ate the fish."
                         (GEN actor `ko` + NOM patient `ang isda`)
```

Our current parser already produces a parse for these — the
existing AV-RECPFV cell emits ``kakakain`` as
``V[VOICE=AV, ASPECT=RECPFV]``, and the standard AV
transitive S frame admits ``V[AV] + NP[GEN] + NP[NOM]``. The
verb's morphological analysis remains AV; only the syntactic
mapping looks OV-like (the GEN-NP is bound to OBJ and the
NOM-NP to SUBJ in the AV frame). This isn't a bug — it
reflects how Tagalog handles recent-perfective semantics with
overt patient arguments.

### Why we don't add an explicit non-AV RECPFV cell

A genuine non-AV RECPFV form (distinct from the AF surface)
would need ``ka-`` + redup PLUS the OV / DV / IV affix:

```text
OV-RECPFV (hypothetical):  kakakainin   = ka-CV.CV-kain-in
DV-RECPFV (hypothetical):  kakakainan   = ka-CV.CV-kain-an
IV-RECPFV (hypothetical):  ikakakain    = i-ka-CV.CV-kain
```

None of these are documented in the Handbook, S&O 1972, R&G
1981, R&B 1986, or the Ramos dictionary. Adding paradigm cells
that emit them would be guesswork — same shape as the prior
reclassifications (Commit 7 resumptive pronouns, Commit 13
``magpa-...-an`` distributive, Commit 15 noun-deriving
``ipang-`` senses). The reference grammars treat the
recent-perfective as a paradigm gap on the non-AV side, and
the implementation should mirror that.

### Status of plan §10.1 Group G after this commit

Two of three Group G items remain to be addressed:

- **IV-REASON CTPL paradigm gap** (CTPL form ``ikakain``
  analyses as IV-CONVEY rather than IV-REASON; Phase 5d
  Commit 9 deferral). Coming in Commit 24.
- **`huwag`'s MOOD=IMP lifted to matrix** (Phase 4 §7.2
  limitation). Coming in Commit 25.

## Phase 5e Commit 24: IV-REASON CTPL short-form paradigm gap

**Date:** 2026-05-02. **Status:** active. Lifts the Phase 5d
Commit 9 paradigm-gap deferral. Before this commit, the surface
``ikakain`` had only an IV-CONVEY CTPL reading; Tagalog
actually admits both IV-CONVEY and IV-REASON CTPL on this
surface, with IV-REASON being a "short" form of the longer
``ikakakain``.

### Evidence from the Handbook of Tagalog Verbs

The Handbook (Ramos & Schachter; ``data/tgl/references/``)
lists Reason Focus (RF) Cont with two surface variants
separated by ``/`` for vowel-initial roots:

```text
ingay (noise):  RF Cont. ikakaingay / ikaiingay   (line 4120 in OCR)
init (heat):    RF Cont. ikakainit  / ikaiinit    (line 4161 in OCR)
```

The first variant has an extra CV-redup; the second drops it.
The pattern generalizes to consonant-initial bases — for
``kain``, the "long" form is ``ikakakain`` (i + ka + cv-redup
\+ kain = 4 syllables), the "short" form is ``ikakain`` (i + ka
\+ kain, no further redup = 3 syllables).

### The change: a second IV-REASON CTPL paradigm cell

A new cell in ``data/tgl/paradigms.yaml`` between the existing
IV-REASON CTPL cell and the pa-...-in causative section:

```yaml
- voice: IV
  aspect: CTPL
  mood: IND
  transitivity: TR
  affix_class: ika
  feats: {APPL: REASON}
  operations:
    - {op: prefix, value: "ka"}
    - {op: prefix, value: "i"}
  notes: ikakain, ikabili (CTPL "short" form — ka- prefix + i-, no cv-redup)
```

Compared to the existing "long" form cell (operations
``[cv_redup, prefix ka, prefix i]``), this cell omits the
``cv_redup`` step. For ``kain``, both produce different
surfaces — long: ``ikakakain``, short: ``ikakain``.

### Surface coincidence with IV-CONVEY CTPL

For ``kain``, the IV-REASON CTPL "short" form ``ikakain``
coincides with the IV-CONVEY CTPL form (also ``ikakain`` —
``i-`` + cv-redup of ``kain`` = ``ikakain``). The morph
analyzer returns BOTH analyses for the surface; the chart
parser explores both readings.

For other ``ika``-class bases like ``sulat``, the surfaces
differ:

```text
sulat → IV-CONVEY CTPL:        isusulat   (i + cv-redup + sulat)
      → IV-REASON CTPL "short": ikasulat   (i + ka + sulat)
      → IV-REASON CTPL "long":  ikasusulat (i + ka + cv-redup + sulat)
```

So ``ikasulat`` is unambiguously IV-REASON CTPL.

### Affix-class scope

The new cell only fires for roots with ``ika`` in their
``affix_class`` — currently ``kain`` and ``sulat``. Other
verbs (``bili``, ``inom``, ``basa``, etc.) don't get the
IV-REASON forms at all because they lack the ``ika`` class
declaration. Expanding this declaration is a per-verb lex
data follow-up, driven by which verbs corpus pressure
surfaces.

### Parse-level effect

```text
Ikakain ko ang isda.   → 2 parses:
                          PRED=KAIN <SUBJ, OBJ-AGENT>          (CONVEY)
                          PRED=EAT-FOR-REASON <SUBJ, OBJ-AGENT> (REASON)
Ikasulat ko ang liham. → 1 parse with REASON PRED.
Ikakakain ko ang isda. → 1 parse with REASON PRED (long form, regression).
```

### Why we don't add a new ASPECT value

The Handbook's pattern shows the "short" form is still
aspectually CTPL — Cont. is the aspect column. Adding a new
ASPECT (e.g., INF or REASON-SHORT) would conflict with the
paradigm system's structure (aspect × mood × voice × affix
class). The cleaner interpretation: the ``ka-`` prefix carries
the REASON applicative and the rest of the form is shaped by
aspect. The "short" form is a phonologically reduced CTPL
where the CV-redup step is optional / absorbed.

### No new tests for ``bili`` and others

The new cell technically also fires for any ``ika``-class
root, but only ``kain`` and ``sulat`` are currently declared.
``bili`` doesn't have ``ika`` in its affix_class
(``[um, in_oblig, an_oblig, i_oblig, mang, maka, ipag, ipang,
mag_an, mang_retain]``), so ``ikabili`` wouldn't be generated
even after this commit. Adding ``ika`` to ``bili``'s affix
class is a separate lex-data follow-up (R&B 1986 doesn't list
IV-REASON for ``bili``, so we don't pre-emptively add it).

## Phase 5e Commit 25: huwag MOOD=IMP lifted to matrix via CLAUSE-MOOD

**Date:** 2026-05-02. **Status:** active. Lifts the Phase 4
§7.2 limitation where the negation rule's ``(↑) = ↓2``
propagated the inner verb's MOOD=IND, conflicting with the
imperative-particle's MOOD=IMP. The §7.2 docs flagged two
resolution paths: selective GF projection or feature
architecture distinguishing predicate-mood from clausal-mood.
Phase 5e Commit 25 takes the **feature-architecture** path.

### The limitation

Before this commit, ``huwag`` (PART[POLARITY=NEG, MOOD=IMP])
behaved syntactically identically to ``hindi`` (PART[POLARITY=
NEG]) — the matrix's MOOD stayed at IND (inherited from the
inner verb via ``(↑) = ↓2``), with only POLARITY=NEG marking
the negation. The huwag particle's lex-emitted MOOD=IMP sat
on the particle's own f-structure and never reached the
matrix.

### The fix: a CLAUSE-MOOD feature

A new feature ``CLAUSE-MOOD`` is introduced for sentential /
speech-act mood, distinct from the verb's morphological
``MOOD``:

- ``MOOD`` (existing) — the verb's morphological mood. IND
  (default for indicative verb forms), ABIL (maka-
  abilitative), NVOL (ma- non-volitional), SOC (Phase 5e
  Commit 21 hortative and Phase 5e Commit 12 reciprocal).
  Always projected from the verb's lex equations.
- ``CLAUSE-MOOD`` (new) — the sentential / speech-act mood.
  Set to IMP for negative imperatives via ``huwag``. Unset
  for declaratives (the absence is the IND default; we don't
  ceremoniously set CLAUSE-MOOD=IND on every clause).

This corresponds to the LFG-canonical distinction between
predicate-mood and clausal-mood (see Bresnan 2001 §3.5):
verbal morphology projects predicate-mood; particles and
clausal markers contribute clausal-mood.

### Grammar change: split into two NEG rules

The existing single rule ``S → PART[POLARITY=NEG] S`` is split:

```python
# Hindi rule (declarative NEG): restrict to particles WITHOUT MOOD.
rules.append(Rule(
    "S",
    ["PART[POLARITY=NEG]", "S"],
    [
        "(↑) = ↓2",
        "(↑ POLARITY) = 'NEG'",
        "¬ (↓1 MOOD)",
    ],
))

# Huwag rule (imperative NEG): require MOOD=IMP on the particle,
# lift to CLAUSE-MOOD on matrix.
rules.append(Rule(
    "S",
    ["PART[MOOD=IMP, POLARITY=NEG]", "S"],
    [
        "(↑) = ↓2",
        "(↑ POLARITY) = 'NEG'",
        "(↑ CLAUSE-MOOD) = 'IMP'",
        "(↓1 MOOD) =c 'IMP'",
    ],
))
```

The hindi rule's ``¬ (↓1 MOOD)`` constraint excludes huwag
(which has MOOD=IMP). The huwag rule's ``(↓1 MOOD) =c 'IMP'``
constraint excludes hindi — this constraining equation is
needed because the category-pattern matcher
(``compile.py::matches``) is non-conflict (matches if no
disagreement, doesn't require all expected features present),
so ``PART[MOOD=IMP, POLARITY=NEG]`` would also match a
candidate without MOOD by absorption.

### Why feature architecture, not selective projection

The plan's other option, selective GF projection — enumerate
the GFs to copy from the inner clause via ``(↑ X) = (↓2 X)``
while excluding MOOD, then set ``(↑ MOOD) = 'IMP'`` —
technically works. It's rejected here for two reasons:

1. **Phantom GF slots.** The unifier's defining-equation
   semantics use ``_resolve_for_write`` (get-or-create)
   on both LHS and RHS designators. So ``(↑ OBJ-PATIENT) =
   (↓2 OBJ-PATIENT)`` for an intransitive inner clause where
   OBJ-PATIENT is undefined would CREATE both ↑.OBJ-PATIENT
   and ↓2.OBJ-PATIENT as fresh empty fstructs and unify them.
   This pollutes the inner clause's f-structure with phantom
   GF slots that didn't exist before. Tests that assert "OBJ
   is None" would still pass (the empty fstruct isn't
   semantically meaningful), but it's bookkeeping noise.

2. **Better separation of concerns.** CLAUSE-MOOD as a
   distinct feature lets future commits add other clausal
   mood values (DECL for declarative speech-act, INT for
   interrogative, etc.) without touching the verb-MOOD
   projection. The architecture stays clean.

### Surface coverage

```text
Huwag kumain ang bata.        → CLAUSE-MOOD=IMP, POLARITY=NEG, MOOD=IND
Huwag kumain ng isda ang bata.→ CLAUSE-MOOD=IMP, POLARITY=NEG, MOOD=IND
Huwag pa kumain ang bata.     → CLAUSE-MOOD=IMP + adv enclitic (`pa` YET)
Hindi kumain ang bata.        → POLARITY=NEG, MOOD=IND, no CLAUSE-MOOD (unchanged)
Kumain ang bata.              → MOOD=IND, no POLARITY/CLAUSE-MOOD (unchanged)
```

### Out-of-scope (deferred)

- **The control-style imperative** ``Huwag kang kumain.`` (with
  addressee + linker + verb). This is the canonical surface
  for direct imperatives ("Don't (you sg) eat") but requires
  a different wrap rule shape — analogous to a control verb
  taking SUBJ + linker + S_XCOMP. Phase 5e Commit 25 only
  covers the matrix-NEG style ``Huwag kumain ang bata.``;
  the PRON-LINK form is deferred to a separate commit (or
  Phase 5g+ when adjective predication and verbless clause
  shapes mature).
- **Lifting hindi to CLAUSE-MOOD=DECL.** We intentionally
  leave CLAUSE-MOOD unset for declaratives. Adding
  CLAUSE-MOOD=DECL to every clause would be ceremony with no
  current consumer. If a future commit needs to distinguish
  declarative from interrogative or other speech-act moods,
  this is a one-line addition.
- **The huwag clitic interaction with SOC** (``Huwag tayong
  kumain.`` "Let's not eat" — combines NEG-IMP with SOC). The
  IMP / SOC interaction is a paradigm and clausal-mood
  composition question that's separate from the lift here.
  Tracked in plan §10.1 Group F (already lifted at the SOC
  end via Commit 21; the huwag side is distinct).

## Phase 5e Commit 26: comparative ``parang``

**Date:** 2026-05-02. **Status:** active. Lifts the Phase 5d
Commit 1 deferral. The existing ``parang`` lex entry covered
the evidential reading (``Parang umuulan`` "It seems like it's
raining" — ``parang + clause``). The comparative reading
(``Parang aso ang bata`` "The child is like a dog" —
``parang + bare-N + ang-NP``) is structurally distinct and
gets its own grammar rule in this commit.

### Lex change

``parang`` (data/tgl/particles.yaml) gains a ``COMPARATIVE:
"YES"`` feature. The string-quoted value avoids the YAML
boolean trap (``YES`` parses as Python ``True``, which then
gets filtered out by ``_lex_equations`` since it's not a
string — same gotcha that surfaced in Phase 5e Commit 17 with
``DEM`` and Phase 5e Commit 25 with the constraining-equation
match for huwag).

``tila`` keeps only ``CTRL_CLASS=RAISING_BARE`` — no
comparative reading in standard usage. ``Tila aso ang bata``
correctly fails to parse (no rule fits the surface, since the
constraining equation in the comparative rule excludes it).

### Grammar change

A new S rule mirroring the existing Phase 5d Commit 1
evidential rule's category (``V[CTRL_CLASS=RAISING_BARE]``):

```python
S → V[COMPARATIVE=YES, CTRL_CLASS=RAISING_BARE] N NP[CASE=NOM]
    (↑ PRED) = 'LIKE <SUBJ, OBJ>'
    (↑ OBJ) = ↓2
    (↑ SUBJ) = ↓3
    (↓1 COMPARATIVE) =c 'YES'
```

The constraining equation excludes ``tila`` — the category-
pattern matcher (``compile.py::matches``) is non-conflict, so
``V[COMPARATIVE=YES, CTRL_CLASS=RAISING_BARE]`` would also
match ``tila`` (RAISING_BARE without COMPARATIVE) by absorption
without the explicit constraint.

The bare ``N`` daughter projects PRED + LEMMA via the existing
``N → NOUN`` rule, so OBJ ends up with the NOUN's lemma and a
NOUN-style PRED.

### F-structure shape

```text
PRED  = 'LIKE <SUBJ, OBJ>'
SUBJ  = the comparee (the ang-NP)
OBJ   = the standard (the bare N)
```

For ``Parang aso ang bata.``:

```text
PRED = 'LIKE <SUBJ, OBJ>'
SUBJ = {LEMMA: 'bata', CASE: 'NOM', ...}
OBJ  = {LEMMA: 'aso', PRED: 'NOUN(↑ FORM)'}
```

### Why GEN-marked OBJ vs bare N

In Tagalog, a comparative complement isn't marked with ``ng``
(GEN). It's a bare nominal. The existing OBJ slot (which is
typically GEN-marked) is reused here as a structural slot for
the comparison standard, without case-marking constraints.
This is consistent with how comparatives work cross-
linguistically (the standard of comparison often has a
distinct case marking, sometimes none).

An alternative would be a typed slot like ``OBL-LIKE`` or
``COMP-STD``. Reusing OBJ keeps the f-structure schema simple
and avoids introducing yet another GF for one construction.
If future work distinguishes the comparative complement from
ordinary OBJ in semantic-role assignment, switching to a
typed slot is a one-line change.

### Composition

The comparative composes naturally:

- **Negation**: ``Hindi parang aso ang bata.`` — POLARITY=NEG
  is overlaid on the matrix via the standard NEG rule.
- **Relativization on SUBJ**: ``Parang aso ang batang
  kumain.`` — the SUBJ NP can carry an internal RC.

### Out-of-scope (deferred)

- **Adjective-modified standard**: ``Parang asong matalino
  ang bata.`` "The child is like a smart dog." — needs the
  Phase 5g adjective machinery for ``asong matalino``. Not
  parsed here.
- **Determiner-marked standard**: ``Parang ang aso ang
  bata.`` — non-standard surface; the standard form uses bare
  N.
- **Comparative + clause as standard**: ``Parang umiiyak ang
  bata.`` "The child is like (someone who is) crying." This
  is captured by the existing evidential reading
  (``parang + clause``); whether comparative-vs-evidential is
  a separable distinction with overt clauses is a deeper
  semantic question deferred to v1+ pragmatic analysis.
- **``kasing-`` / ``sing-`` equative comparatives**
  (``kasingganda ng aso``). Phase 5h coverage (comparison &
  degree) per plan §12.2.
- **``mas`` / ``pinaka-`` comparatives** (``mas matalino``,
  ``pinakamatalino``). Phase 5h.

## Phase 5f Commit 1: native cardinal NP-internal modifier (1-10)

**Date:** 2026-05-03. **Status:** active. Phase 5f's foundational
commit — items 2-7 of Group A (Spanish cardinals, compound
cardinals, predicative cardinals, multiplicative ratios, decimals,
percentages) and Groups B/C/E/F/H all consume the cardinal
NP-modifier rule once it lands. Refs: plan §11.1 Group A item 1.

### Lex change

Native cardinals 1-10 added to ``data/tgl/particles.yaml`` with
``pos: NUM``:

- Vowel-final (use bound ``-ng`` linker via ``split_linker_ng``):
  ``isa`` (1, NUM=SG), ``dalawa`` (2), ``tatlo`` (3), ``lima`` (5),
  ``pito`` (7), ``walo`` (8), ``sampu`` (10).
- Consonant-final (use standalone ``na`` linker): ``apat`` (4),
  ``anim`` (6), ``siyam`` (9).

Each carries ``CARDINAL: "YES"``, ``CARDINAL_VALUE: "<N>"`` (the
integer as a string), and ``NUM: SG`` (only ``isa``) or
``NUM: PL`` (2-10). The CARDINAL_VALUE quoting matters: PyYAML
parses unquoted integers as Python ``int``, and the
``_lex_equations`` filter in the parser drops non-string atomic
values — same gotcha that surfaced in Phase 5e Commit 17 with
booleans (``DEM: YES`` parsing as Python ``True``).

### Grammar change

**Two-track design** to handle cardinal-modified N at both NP
level (case-marked, the canonical positions) and bare-N level
(parang complements, future predicatives):

- **NP-level cardinal rules** (6 = 3 cases × 2 linker variants).
  Schema:

  ```text
  NP[CASE=X] → DET/ADP[CASE=X] NUM[CARDINAL=YES] PART[LINK=Y] N
  ```

  Equations: case marker shares with NP via ``(↑) = ↓1``
  (CASE/MARKER); head N's PRED + LEMMA percolate; cardinal's NUM
  and CARDINAL_VALUE land on matrix NP. Chained cardinals
  blocked at NP level by ``¬ (↓4 CARDINAL_VALUE)``: the head-N
  daughter cannot itself carry a CARDINAL_VALUE.

- **N-level cardinal rule** (2 = 1 × 2 linker variants):

  ```text
  N → NUM[CARDINAL=YES] PART[LINK=Y] N
  ```

  Used for bare contexts where there's no case marker — the
  parang-comparative standard (``parang isang aso ang bata``,
  Phase 5e Commit 26) is the immediate consumer; Group A item 4
  (predicative cardinals, ``Tatlo ang anak ko``) will be the
  next. The recursive composition is blocked by ``¬ (↓3
  CARDINAL_VALUE)`` on the head-N daughter.

The two-track design produces ambiguity for case-marked
cardinal NPs (the same input can parse via the NP-level rule
directly or via N-level + NP-from-N composition). The NP-level
parse is the cardinal-info-preserving one and is what the
test suite asserts on; the composed N-level parse loses
CARDINAL_VALUE at the NP level (the existing
``NP[CASE=X] → DET/ADP[CASE=X] N`` rule projects only PRED +
LEMMA from N). This redundancy is acceptable — the NP-from-N
projection wasn't widened to pull NUM/CARDINAL_VALUE because
defining equations on undefined paths create empty f-structures
on bare N (a real regression: ``Kumain ang bata.`` would gain a
spurious ``CARDINAL_VALUE: <empty>`` slot on its SUBJ).

### Clitic-pass change

A new branch in ``disambiguate_homophone_clitics``
(``src/tgllfg/clitics/placement.py``) treats standalone ``na``
after a ``NUM[CARDINAL=YES]`` as the linker — parallel to the
Phase 5e Commit 16 DEM-DET/DEM-ADP exception. Without this,
the Wackernagel pass would hoist ``na`` to clause-end as the
ALREADY enclitic and ``apat na isda`` / ``anim na bata`` /
``siyam na aklat`` would never reach the cardinal-NP-modifier
rule.

### Negative fixtures

Per Phase 5f §11.2 negative-fixture convention:

- ``*Kumain ako ng isa bata.`` — missing linker between cardinal
  and N. No rule consumes the ``isa bata`` sequence as an N or
  NP because the cardinal-NP-modifier rule requires a
  ``PART[LINK=Y]`` middle daughter.
- ``*Kumain ako ng tatlong dalawang bata.`` — chained cardinals.
  Blocked by ``¬ (↓4 CARDINAL_VALUE)`` on NP-level rule and
  ``¬ (↓3 CARDINAL_VALUE)`` on N-level rule.

### Out of scope for this commit

- Spanish-borrowed cardinals (``uno``, ``dos``, ``tres``, ...) —
  Group A item 2.
- Compound cardinals (``labing-isa`` 11, ``dalawampu`` 20, ...) —
  Group A item 3.
- Predicative cardinals (``Tatlo ang anak ko``) — Group A item 4
  (consumes the N-level rule added here).
- Multiplicative ratios (``maka-`` + cardinal, ``[CARDINAL]ng
  beses``) — Group A item 5.
- Decimals + percentages — Group A items 6-7.
- Cardinal + dem composition (``itong tatlong bata``) — would
  need either a dem rule extension or an NP-internal cardinal
  modifier inside the dem-headed NP. Not in this commit.

## Phase 5f Commit 2: Spanish-borrowed cardinals 1-10

**Date:** 2026-05-03. **Status:** active. Lex-only addition;
no grammar changes. Refs: plan §11.1 Group A item 2;
Phase 5f Commit 1 (rule infrastructure).

### Lex change

10 entries added to ``data/tgl/particles.yaml`` parallel to
the native-cardinal block from Commit 1:

- Vowel-final (bound ``-ng`` linker): ``uno`` (1, NUM=SG),
  ``kuwatro`` (4), ``singko`` (5), ``siyete`` (7), ``otso``
  (8), ``nuwebe`` (9).
- Consonant-final (standalone ``na`` linker): ``dos`` (2),
  ``tres`` (3), ``sais`` (6), ``dies`` (10).

Each carries the same ``CARDINAL: "YES"``,
``CARDINAL_VALUE: "<N>"``, and ``NUM`` features as the native
cardinals. CARDINAL_VALUE is duplicated across native and
Spanish forms — both ``isa`` and ``uno`` map to "1", both
``dalawa`` and ``dos`` map to "2", etc. — because the value
is a numerical fact, not a register-marker. The choice between
native and borrowed surface is a register decision left to the
producer; the parser accepts both with identical f-structure
output (modulo LEMMA, which encodes the surface stem).

### Why no grammar change

The Phase 5f Commit 1 cardinal-NP-modifier rules are
non-conflict-matched on ``NUM[CARDINAL=YES]`` and
``PART[LINK=NA|NG]``. They fire on any token analyzed as
``NUM`` with ``CARDINAL=YES``, so adding new lex entries with
that signature is sufficient. Same applies to the N-level
companion rule and the ``disambiguate_homophone_clitics``
NUM-CARDINAL branch.

### Out of scope for this commit

- Compound Spanish cardinals (``onse`` 11, ``dose`` 12, ...,
  ``sentimo`` per cents in price expressions, etc.) — Group A
  item 3 (compound cardinals).
- Spanish ordinal forms (``primer``, ``segundo``, ...) — these
  surface in fixed expressions (months, kings, etc.) but are
  not productive in modern Tagalog; out of scope (§18).
- Register-marking on the parsed f-structure (no
  ``ORIGIN: SPANISH`` or ``REGISTER: BORROWED`` feature) —
  the parser's job is structural; sociolinguistic register
  belongs in a downstream layer.

## Phase 5f Commit 3: compound cardinals 11-1000

**Date:** 2026-05-03. **Status:** active. Lex-only addition;
no grammar / morph changes. Refs: plan §11.1 Group A item 3
(compound cardinals); Phase 5f Commit 1 (rule infrastructure).

### Lex change

19 hand-authored single-token compound surfaces added to
``data/tgl/particles.yaml``:

- **Teens (11-19)** — ``labing-`` prefix + 1-9 base with sandhi:
  ``labingisa`` (11), ``labindalawa`` (12), ``labintatlo`` (13),
  ``labingapat`` (14), ``labinlima`` (15), ``labinganim`` (16),
  ``labimpito`` (17), ``labingwalo`` (18), ``labinsiyam`` (19).
- **Decades (20-90)** — base + ``-pu`` / ``-mpu`` / ``na pu``
  with sandhi: ``dalawampu`` (20), ``tatlumpu`` (30),
  ``apatnapu`` (40), ``limampu`` (50), ``animnapu`` (60),
  ``pitumpu`` (70), ``walumpu`` (80), ``siyamnapu`` (90).
- **Hundreds and thousands**: ``sandaan`` (100), ``sanlibo``
  (1000).

All carry ``CARDINAL: "YES"``, ``CARDINAL_VALUE`` (the integer
as a string, e.g., ``"11"``, ``"100"``), and ``NUM: PL`` (no
compound is singular).

### Why hand-authored, not productive morphology

The plan (§11.1 Group A item 3) calls for "either a small
``num_compound`` morph class plus sandhi ops, or a hand-authored
lex of high-frequency forms (likely both — productive paradigm
for the systematic part, lex for the irregulars)." This commit
takes the hand-authored path because:

- The high-frequency compounds (11-19, 20, 30, 40, 50, 60, 70,
  80, 90, 100, 1000) cover the bulk of real-world usage in
  prices, ages, dates, recipe quantities, and clock times.
- The productive morphology has irregular sandhi (``-mpu``
  after vowel-final 1-9 → ``dalawampu`` from ``dalawa``;
  ``na pu`` after consonant-final 4 / 6 / 9 → ``apatnapu``,
  ``animnapu``, ``siyamnapu``) and an irregular vowel mutation
  (``tatlo`` → ``tatlumpu``, ``pito`` → ``pitumpu``, ``walo``
  → ``walumpu``). Encoding these productively requires a small
  morph class and sandhi rules — useful but not required for
  v1 reference-grammar coverage.
- Higher compound numerals (101-999, 1001-9999, etc.) require
  NUM coordination (``isang daan at dalawampu`` 120;
  ``apat na pu`t lima`` 45 with the bound ``'t``) which is
  deferred to the Phase 5k coordination work.

### Why no grammar change

Same reason as Commit 2: the cardinal-NP-modifier rules from
Commit 1 are non-conflict-matched on ``NUM[CARDINAL=YES]`` and
``PART[LINK=NA|NG]``, so any new lex with that signature fires
unchanged. The ``disambiguate_homophone_clitics`` NUM-CARDINAL
branch likewise fires for compounds — the consonant-final
compounds (``labingapat``, ``labinganim``, ``labinsiyam``,
``sandaan``) all use the standalone ``na`` linker and benefit
from the same disambiguation lift.

### Orthography choice

Single-token spellings throughout (``labingisa`` not
``labing-isa``; ``apatnapu`` not ``apat na pu``; ``sandaan``
not ``sang daan``). All three families are attested in modern
Tagalog, but the single-token form is what the existing
tokenizer yields without modification:

- Hyphenated forms (``labing-isa``) tokenize as 3 tokens
  (``labing``, ``-``, ``isa``) — would need a tokenizer
  pre-pass to merge.
- Multi-word forms (``apat na pu``) tokenize as 3 tokens
  and would need NUM-internal grammar rules to compose
  (with productive value calculation: 4 × 10 = 40).

Both are interesting follow-ons but neither is needed to cover
high-frequency v1 compound numerals.

### Out of scope for this commit

- Productive ``labing-`` and ``-pu`` morph paradigms (would
  cover any base 1-9 systematically; useful for testing /
  generation but redundant with the hand-authored lex for
  parsing).
- Hyphenated and multi-word compound variants
  (``labing-isa``, ``apat na pu``).
- Higher compound numerals (101-999, 1001+) requiring
  coordination — deferred to Phase 5k cardinal-coordination
  follow-on.
- Group A item 4 (predicative cardinals) — next commit;
  consumes both simple and compound cardinals via the
  N-level rule already in place.

## Phase 5f Commit 4: predicative cardinal

**Date:** 2026-05-03. **Status:** active. One new S rule;
no lex changes (cardinals from Commits 1-3 are reused). Refs:
plan §11.1 Group A item 4; Phase 5e Commit 26 (parang —
parallel predicative S rule shape); Phase 5d Commit 1
(evidential parang).

### Grammar change

```text
S → NUM[CARDINAL=YES] NP[CASE=NOM]
Equations:
  (↑ PRED) = 'CARDINAL <SUBJ>'
  (↑ SUBJ) = ↓2
  (↑ CARDINAL_VALUE) = ↓1 CARDINAL_VALUE
  (↑ NUM) = ↓1 NUM
```

The cardinal serves as the matrix predicate; the NOM-NP is the
pivot. F-structure shape:

- ``PRED            = 'CARDINAL <SUBJ>'`` (literal)
- CARDINAL_VALUE  = the count from the cardinal
- NUM             = SG (only ``isa`` / ``uno``) or PL (rest)
- SUBJ            = the NOM-NP pivot

The PRED template ``CARDINAL <SUBJ>`` parallels the literal
PRED conventions of the existing predicative S rules
(``LIKE <SUBJ, OBJ>`` for comparative parang; ``SEEM <SUBJ>``
for evidential parang). No VOICE / ASPECT / MOOD: a numeric
predicate isn't a verb and doesn't carry verbal morphology.

### Why NUM-headed S, not NUM-as-V

The plan (§11.1 Group A item 4) offers two analytical paths:
"a NUM-as-V analysis or a small NUM-headed S rule." This
commit takes the **NUM-headed S** path because:

- Cardinals are not verbs — they don't inflect for voice,
  aspect, or mood. Forcing them through a VERB-typed analysis
  would require either duplicate VERB lex entries (clunky) or
  a special VOICE / ASPECT / MOOD = NULL discipline (complex
  and a mismatch with the existing verbal pipeline).
- A single new S rule is the minimal change. It composes
  trivially with the matrix negation rule (``Hindi tatlo ang
  anak ko``) and the verbless clitic-placement pass (Phase 5e
  Commit 22 — NUM qualifies as a content-word anchor for
  PRON-clitic SUBJ pivots like ``sila``, ``kami``, ``tayo``).
- The single rule consumes simple (Commit 1), Spanish-borrowed
  (Commit 2), and compound (Commit 3) cardinals — all match
  ``NUM[CARDINAL=YES]``.

### Composition

Tested compositions:

- PRON-clitic SUBJ: ``Dalawa sila``, ``Lima kami``, ``Tatlo
  tayo``. The verbless clitic pass (Phase 5e Commit 22) treats
  NUM as the content anchor; the PRON-clitic falls into the
  post-anchor cluster (which is its surface position anyway —
  no movement).
- Full NOM-NP SUBJ: ``Tatlo ang anak ko`` (with possessor),
  ``Lima ang isda``, ``Isa ang bata`` (NUM=SG case).
- All cardinal classes: simple (``Lima ang isda``), Spanish
  (``Dos sila``, ``Singko ang isda``), compound (``Dalawampu
  ang bata``, ``Sandaan ang aklat``, ``Sanlibo ang isda``).
- NEG: ``Hindi tatlo ang anak ko`` "I don't have three
  children" — the Phase 4 §7.4 matrix-NEG rule prepends
  ``hindi`` to any matrix S; predicative-cardinal S is no
  exception.

### Negative fixtures

Per Phase 5f §11.2 negative-fixture convention:

- ``*Tatlo.`` standalone — predicative cardinal needs a SUBJ;
  the rule requires NP[CASE=NOM] as the second daughter.
- ``*Tatlo ng anak ko.`` — wrong case. Predicative cardinal
  requires NOM-NP, not GEN-NP. The rule's second daughter
  pattern is ``NP[CASE=NOM]``, not ``NP[CASE=GEN]``.

## Phase 5f Commit 5: multiplicative ratios

**Date:** 2026-05-03. **Status:** active. Lex (NOUN + ADV)
plus one new grammar rule. Refs: plan §11.1 Group A item 5;
S&O 1972 §4.5; Phase 5e Commit 3 (AdvP deferral that this
commit partially closes).

### Lex change

- **Frequency NOUNs** (``data/tgl/nouns.yaml``):
  ``beses`` and ``ulit`` (both with ``SEM_CLASS: FREQUENCY``;
  bidirectional synonyms). Used in periphrastic frequency
  expressions (``dalawang beses`` "twice", ``tatlong ulit``
  "three times") via the existing Phase 5f Commit 1
  cardinal-NP-modifier rule on the head N.
- **Multiplier NOUNs**: ``doble`` and ``triple`` (both with
  ``SEM_CLASS: MULTIPLIER``). Spanish-borrowed; lex-only —
  surface in technical / commercial register.
- **maka-cardinal ADVs** (``data/tgl/particles.yaml``): 10
  hand-authored entries (``makaisa`` ... ``makasampu``) with
  ``pos: ADV``, ``ADV_TYPE: FREQUENCY``, and
  ``MULTIPLIER_VALUE: "<N>"``. Same hand-authored-lex strategy
  as the compound cardinals from Commit 3 — productive
  morphology (``maka-`` + cardinal stem) is real but a
  hand-authored inventory of high-frequency forms is
  sufficient for v1. The ``makaisa`` form is grammatically
  well-formed but semantically rare; ``minsan`` "once /
  sometimes" or the periphrastic ``nang isang beses`` are
  more common in modern usage.

### Grammar change

One new rule (``src/tgllfg/cfg/discourse.py``):

```text
S → S AdvP
Equations:
  (↑) = ↓1                          # share matrix with inner S
  ↓2 ∈ (↑ ADJUNCT)                  # AdvP joins ADJUNCT set
  (↓2 ADV_TYPE) =c 'FREQUENCY'      # constraining: FREQUENCY only
```

Closes part of the Phase 5e Commit 3 deferral on bare AdvP
placement — scoped here to ``ADV_TYPE=FREQUENCY`` only via the
constraining equation. The deferral note explicitly cited
"interactions with the Wackernagel cluster and quantifier-
float" as the reason for keeping bare placement deferred;
FREQUENCY adverbs don't trigger those interactions (they're
clausal modifiers, not noun-phrase or verb-phrase scoped),
so this scoped lift is safe. The TIME / SPATIAL / MANNER
deferral remains in force — those need separate analytical
work.

### Periphrastic ``[CARDINAL]ng beses`` — partially supported

The lex side (``beses`` / ``ulit`` as NOUN with
SEM_CLASS=FREQUENCY) is in place, and ``dalawang beses`` /
``tatlong ulit`` parse correctly as cardinal-modified NPs via
the Phase 5f Commit 1 cardinal-NP-modifier rule. **But** the
adverbial-frequency reading of bare ``dalawang beses``
(``Tumakbo ako dalawang beses`` "I ran twice") is not yet
supported as a clause-final ADJUNCT. The N parses fine
(cardinal-modified NOUN); what's missing is a rule attaching
a SEM_CLASS=FREQUENCY N to the matrix S as ADJUNCT, parallel
to the maka- ADV rule landed in this commit.

The natural Tagalog forms for "X did Y N times" are:

- ``Tumakbo ako dalawang beses.`` — bare frequency-N
  clause-final.
- ``Dalawang beses akong tumakbo.`` — frequency-N
  topicalized (composes with existing ay-fronting machinery
  once the bare-frequency-N is recognised).

The form ``Tumakbo ako ng dalawang beses`` (with the
case-marker ``ng``) is marginal / dispreferred — the
``ng``-marked reading currently parses as a possessor on the
SUBJ pronoun, which is the structurally available analysis but
not the intended frequency reading.

**Important:** ``nang [CARDINAL] beses`` is NOT the standard
periphrastic frequency form. The narrative idiom
``Nang isang beses, pumunta kami sa Maynila`` "Once, we went
to Manila" exists and survives in storytelling register, but
it's a temporal-framing construction (parallel to ``Nang araw
na iyon`` "On that day"), not a productive frequency adverbial:
``*nang dalawang beses``, ``*nang tatlong beses`` are
unnatural. Encoding ``nang isang beses`` properly requires a
narrow lexical idiom, not a generative ``nang + NUM + beses``
rule (which would overgenerate). Deferred to a follow-on
commit.

The proper bare-frequency-N adjunct support is a small
follow-on that needs:

1. SEM_CLASS percolation through the cardinal-NP-modifier
   rules so cardinal-modified ``beses`` carries
   ``SEM_CLASS=FREQUENCY`` to the matrix N (currently only
   PRED + LEMMA + NUM + CARDINAL_VALUE percolate; adding
   SEM_CLASS hits the empty-f-structure issue documented in
   Commit 1's two-track design).
2. A new rule ``S → S N`` constraining on
   ``(↓2 SEM_CLASS) =c 'FREQUENCY'``, parallel to the maka-
   ADV rule in this commit.

Both deferred to a follow-on commit. (S&O 1972 §4.5; user-
provided linguistic note 2026-05-03.)

### Composition

- maka- frequency adverb in clause-final position:
  ``Kumain ako makalawa``, ``Tumakbo siya makasampu``.
- maka- with full NOM-NP SUBJ: ``Kumain ang bata makatlo``.
- maka- with NEG: ``Hindi tumakbo si Juan makalawa``.
- maka- recursive (S → S AdvP fires on its own output):
  ``Tumakbo ako makalawa makatlo`` parses (semantically
  odd but syntactically allowed; not blocked).

### Negative fixtures

Per Phase 5f §11.2 negative-fixture convention:

- ``*Tumakbo ako kahapon.`` — TIME adverbs (kahapon —
  ``ADV_TYPE=TIME``) still do NOT compose as bare clause-final
  adjuncts. The constraining equation
  ``(↓2 ADV_TYPE) =c 'FREQUENCY'`` restricts the new rule to
  FREQUENCY only; the TIME deferral stays.

### Out of scope for this commit

- Bare-frequency-N as clause-final ADJUNCT
  (``Tumakbo ako dalawang beses``) — see "Periphrastic" above.
- Topicalized frequency-N (``Dalawang beses akong tumakbo``)
  — depends on the bare-frequency-N rule landing first.
- The narrative idiom ``Nang isang beses, ...`` — narrow
  lexical idiom, separate follow-on; do NOT generalize to
  ``nang + NUM + beses``.
- Pre-verbal ``maka-`` with linker (``makalawang nakakain``):
  the cited S&O example uses pre-verbal placement with
  linker, but clause-final placement is the more common and
  simpler case; pre-verbal is deferred.
- Bare AdvP attachment for non-FREQUENCY adverb types — kept
  deferred per the Phase 5e Commit 3 note.
- Productive ``maka-`` morphology paradigm — the hand-authored
  10-entry inventory covers v1 needs; productive treatment
  is a follow-on if needed.
- Spanish-borrowed ``doble`` / ``triple`` adverbial use —
  surface in technical register (``Doble ang singil`` "the
  charge is doubled") but the predicative reading isn't
  exercised here. Lex-only addition for now.

## Phase 5f Commit 6: decimals and percentages

**Date:** 2026-05-03. **Status:** active. Lex (``punto``,
``porsiyento``) plus one new grammar rule (decimal NUM) plus
a small parser fix. Refs: plan §11.1 Group A items 6 + 7;
R&G 1981 dialogue corpus; Phase 5f Commits 1, 4 (rule
infrastructure consumed unchanged).

### Lex change

- ``punto`` (``data/tgl/particles.yaml``): PART with
  ``DECIMAL_SEP: "YES"``. Spanish-borrowed decimal separator;
  joins integer and fractional cardinals.
- ``porsiyento`` (``data/tgl/nouns.yaml``): NOUN with
  ``SEM_CLASS: PERCENTAGE``. Spanish-borrowed; Tagalog has no
  native percentage word. Used as the head N of cardinal-
  modified percentage NPs.

### Grammar change (decimal)

```text
NUM[CARDINAL=YES] →
    NUM[CARDINAL=YES] PART[DECIMAL_SEP=YES] NUM[CARDINAL=YES]
Equations:
  (↑) = ↓1                                    # share with integer part
  (↑ FRACTIONAL_VALUE) = ↓3 CARDINAL_VALUE   # record fractional
  (↑ DECIMAL) = 'YES'                         # mark as decimal
  (↓2 DECIMAL_SEP) =c 'YES'                   # constraining
```

The output NUM[CARDINAL=YES] fits the existing predicative-
cardinal rule (Commit 4) and (in principle) the cardinal-NP-
modifier rules (Commit 1) without modification.

The CARDINAL_VALUE on the matrix is the integer part only —
the LFG equation language has no string-concatenation
operator to construct "2.5" from "2" + "." + "5". Downstream
consumers that need the full numeric value combine
``CARDINAL_VALUE`` (integer), ``FRACTIONAL_VALUE``, and the
``DECIMAL=YES`` marker.

The constraining equation ``(↓2 DECIMAL_SEP) =c 'YES'`` is
critical: without it, the non-conflict pattern matcher would
accept any PART (including the linker particles ``-ng`` /
``na``) as the middle daughter — because PART[DECIMAL_SEP=YES]
and PART[LINK=NG] don't share any feature key, so non-conflict
"matching" succeeds. With the constraint, the matcher accepts
the pattern but f-unification rejects parses where the PART
isn't actually ``punto``. Same pattern as the comparative-
parang vs evidential-tila distinction (Phase 5e Commit 26)
and the huwag MOOD constraint (Phase 5e Commit 25).

### Parser fix (side change)

Adding the decimal rule with ``NUM[CARDINAL=YES]`` as LHS made
``NUM`` a non-terminal. The Earley parser's ``_step``
previously dispatched binary — predict for non-terminals, scan
for preterminals. Once NUM became a non-terminal, lex NUM
tokens (``dos``, ``isa``, ``dalawa``, etc.) were never scanned
in NUM-expecting positions, breaking all cardinal use.

The fix (``src/tgllfg/parse/earley.py``): always scan in
addition to predicting. A category can legitimately be both a
non-terminal (rule LHS) and a preterminal (lex POS); both
paths must be explored. For purely non-terminal categories
(``S``, ``NP``, ``PP``, ``AdvP``, ...) the scan call is a
no-op (no matching lex tokens). For ``N``, similarly — it's a
non-terminal (``N → NOUN`` rule) but no lex tokens have
``pos: N`` (they have ``pos: NOUN``), so scan is a no-op
there too. Only ``NUM`` (and any future category that's
both) actually gets dual treatment.

The fix is small (one removed ``else`` clause + comment) but
load-bearing for the architectural shape of the grammar.

### No grammar change (percentages)

``porsiyento`` is a regular NOUN; cardinal-modified percentage
NPs (``dalawampung porsiyento`` "20%", ``sandaan na
porsiyento`` "100%") parse via the existing Phase 5f Commit 1
cardinal-NP-modifier rule without modification. Predicative
percentage use (``Dalawampung porsiyento ang interes``
"the interest is 20%") needs an equational sentence rule
(``S → N NP[CASE=NOM]`` or similar) and is deferred — out of
scope for Group A. The fixtures here exercise the cardinal-
modified-NP-as-OBJ path.

### Out of scope for this commit

- Decimal as NP-modifier (``dos punto singkong libro`` "2.5
  books") — semantically odd and likely not corpus-attested,
  but structurally would work via the existing cardinal-NP-
  modifier rule once SEM_CLASS percolation lands. Not
  exercised here.
- Equational sentences for predicative percentages — needs a
  general N-as-predicate rule; deferred to a future commit.
- Symbolic decimal forms (``2.5``, ``10.75``) — tokenizer
  expansion track; symbolic numerals are §18 out-of-scope.
- Three-term decimals (``dos punto singko punto otso``) —
  not standard usage; rule recursion would technically allow
  it but no test fixtures verify it.

## Phase 5f Commit 7: ordinals 1st-10th

**Date:** 2026-05-03. **Status:** active. Lex (11 entries) plus
6 NP-level ordinal-modifier rules plus constraining-equation
additions to the cardinal rules (Commits 1 + 5/6) plus
disambiguator extension. Refs: plan §11.1 Group B (ordinals);
S&O 1972 §4.4; Phase 5f Commit 1 (parallel rule structure).

### Lex change

11 ordinal entries added to ``data/tgl/particles.yaml`` with
``pos: NUM``, ``ORDINAL: "YES"``, and ``ORDINAL_VALUE``:

- ``una`` (1st, suppletive — not ``*ikaisa``).
- ``ikalawa`` (2nd, with stem truncation: ``ika-`` + ``lawa``,
  not ``*ikadalawa``).
- ``pangalawa`` (2nd alternative, high-frequency colloquial
  variant; S&O 1972 §4.4 footnote).
- ``ikatlo`` (3rd, similar stem truncation: ``ika-`` + ``tlo``).
- ``ikaapat`` (4th), ``ikalima`` (5th), ``ikaanim`` (6th),
  ``ikapito`` (7th), ``ikawalo`` (8th), ``ikasiyam`` (9th),
  ``ikasampu`` (10th).

### Why hand-authored, not productive ``ika-`` morphology

Same reasoning as the Commit 3 compound cardinals: the
hand-authored inventory of 1st-10th covers v1 needs; productive
morphology requires sandhi rules (the ``ikalawa`` / ``ikatlo``
truncations) and a discriminator from the existing IV-CONVEY
``ika-`` paradigm (which produces verbs, not numerals). Both
are deferred follow-ons.

### Why NUM is omitted from ordinal lex

Ordinal value is independent of noun number agreement:

- ``ang unang aklat ko`` "my first book" (singular).
- ``ang unang mga aklat ko`` "my first books" (plural,
  with ``mga`` marker).

Both are grammatical. The matrix NP's NUM is determined by the
head noun (or ``mga`` plural marker), not the ordinal. So the
ordinal lex entries omit NUM, and the ordinal-NP-modifier rule
omits the NUM-projection equation that the cardinal rule has.

### Grammar change

6 new ordinal NP-modifier rules (parallel to the Commit 1
cardinal NP-modifier rules):

```text
NP[CASE=X] → DET/ADP[CASE=X] NUM[ORDINAL=YES] PART[LINK=Y] N
Equations:
  (↑) = ↓1
  (↑ PRED) = ↓4 PRED
  (↑ LEMMA) = ↓4 LEMMA
  (↑ ORDINAL_VALUE) = ↓2 ORDINAL_VALUE
  ¬ (↓4 ORDINAL_VALUE)
  (↓2 ORDINAL) =c 'YES'
```

The constraining equation ``(↓2 ORDINAL) =c 'YES'`` is critical
for cardinal/ordinal disjointness: without it, the non-conflict
pattern matcher would accept CARDINAL=YES NUMs (since they
don't share the ORDINAL key) and create empty ORDINAL_VALUE
fstructs on the matrix NP. Same fix-pattern as Commit 6's
PART[DECIMAL_SEP=YES] constraint.

### Side change: cardinal rules get ``(↓2 CARDINAL) =c 'YES'``

The Commit 1 cardinal NP-modifier rules and N-level rule were
under-constrained — they fired on ANY NUM by non-conflict
matching, including ORDINAL=YES NUMs added in this commit.
Without a fix, ``ang unang aklat`` would have produced a
spurious cardinal parse (with empty NUM and CARDINAL_VALUE
fstructs on the OBJ NP) alongside the correct ordinal parse.
Adding ``(↓2 CARDINAL) =c 'YES'`` to the cardinal NP-modifier
rules and ``(↓1 CARDINAL) =c 'YES'`` to the N-level cardinal
rule restores the cardinal/ordinal disjointness.

### Side change: disambiguator extension

The Phase 5f Commit 1 ``disambiguate_homophone_clitics`` branch
that recognised ``na`` after a ``NUM[CARDINAL=YES]`` is the
linker (not the ALREADY enclitic) is extended to also cover
``NUM[ORDINAL=YES]``: consonant-final ordinals (``ikaapat``,
``ikaanim``, ``ikasiyam``) need the same standalone-``na``-as-
linker treatment as the cardinals (``apat``, ``anim``,
``siyam``).

### Composition

- OBJ position (``Bumili ako ng unang aklat`` "I bought the
  first book"): all 11 ordinals exercised across the sweep.
- SUBJ position (``Tumakbo ang unang aso`` "the first dog
  ran").
- DAT position (``Pumunta ako sa ikatlong kuwarto`` "I went
  to the third room").
- Alternative ``pangalawa`` form parses with the same
  ORDINAL_VALUE=2 as ``ikalawa``.

### Negative fixtures

Per Phase 5f §11.2 negative-fixture convention:

- ``*Bumili ako ng una aklat.`` — missing linker.
- ``*Bumili ako ng unang ikalawang aklat.`` — chained
  ordinals, blocked by ``¬ (↓4 ORDINAL_VALUE)``.

### Out of scope for this commit

- Productive ``ika-`` morphology paradigm (with ``ikalawa`` /
  ``ikatlo`` truncation sandhi).
- Productive ``pang-`` ordinal morphology (the alternative
  variant — only ``pangalawa`` lex'd here).
- Predicative ordinal (``Ikalawa ang anak ko`` "My child is
  the second [one]") — needs a parallel S rule to the
  predicative cardinal rule (Commit 4); deferred.
- Mixed ordinal + cardinal (``ang unang dalawang aklat`` "the
  first two books") — needs an ordinal-of-cardinal stacking
  rule; deferred.
- Higher ordinals (11th+, hundredth, thousandth) — uses
  ``ika-`` + compound cardinal; deferred to a follow-on
  alongside compound-cardinal coordination.

## Phase 5f Commit 8: fractions

**Date:** 2026-05-03. **Status:** active. Lex-only addition
(4 NOUN entries); no grammar changes. Refs: plan §11.1
Group C; S&O 1972 §4.4; Phase 5f Commits 1 + 7 (cardinal /
ordinal NP-modifier rules consumed unchanged); Ramos 1971.

### Lex change

4 NOUN entries added to ``data/tgl/nouns.yaml``:

- ``kalahati`` "half" — native form. SEM_CLASS=FRACTION.
  Bidirectional synonym of ``medya``.
- ``kapat`` "quarter" — native form. SEM_CLASS=FRACTION.
- ``medya`` "half" — Spanish-borrowed; canonical in clock-time
  register (``alas-otso y medya`` "8:30") which Group E will
  exercise. Bidirectional synonym of ``kalahati``.
- ``bahagi`` "part" — head N for the productive
  ``[ORDINAL]ng bahagi`` fraction pattern (``ikatlong bahagi``
  "third part" = 1/3; ``ikaapat na bahagi`` "fourth part"
  = 1/4). SEM_CLASS=PART.

### Why no grammar change

Compositional fractions parse via existing rules:

- ``[CARDINAL]ng kalahati / kapat / medya`` (``dalawang
  kalahati`` 2/2, ``apat na kapat`` 4/4, ``tatlong kapat``
  3/4) uses the Phase 5f Commit 1 cardinal-NP-modifier rule.
- ``[ORDINAL]ng bahagi`` (``ikatlong bahagi``,
  ``ikaapat na bahagi``) uses the Phase 5f Commit 7
  ordinal-NP-modifier rule.

Both rule families fire on any matching CARDINAL=YES /
ORDINAL=YES NUM + linker + N constituent — no need to add
fraction-specific rules.

### `kuwarto` polysemy note

The existing NOUN ``kuwarto`` (glossed "room") also has a
secondary "quarter [of the hour]" reading in clock-time
register (``alas-otso y kuwarto`` "8:15"). The polysemy is
left to context, not split into separate lex entries — the
clock-time construction in Group E will provide the
disambiguating context. This commit doesn't add a separate
``kuwarto`` "quarter" entry to avoid duplicate-surface lex
that the parser would treat as ambiguous on every input.

### Out of scope for this commit

- Mixed numbers (``dalawa't kalahati`` "two and a half" 2½;
  ``apat at kalahati`` "four and a half" 4½; ``isa't kapat``
  "one and a quarter" 1¼). Need the bound ``'t`` clitic
  split (parallel to ``split_linker_ng`` / ``split_enclitics``)
  and a NUM coordination rule. Deferred to Phase 5k
  coordination work per plan §11.1 Group C item 4 — likely
  shareable infrastructure with the other ``'t`` cases.
- Hyphenated ``ikatlong-bahagi`` orthographic variant. The
  unhyphenated ``ikatlong bahagi`` (two tokens, ordinal +
  bahagi) is what the existing tokenizer yields and what this
  commit exercises. The hyphenated form would need a tokenizer
  pre-pass; deferred.
- ``[CARDINAL]ng kuwarto`` clock-time register (``isang
  kuwarto`` "a quarter [of an hour]") — the cardinal+kuwarto
  parse already works syntactically (``kuwarto`` is NOUN); the
  semantic disambiguation between "room" and "quarter [of
  hour]" is a clock-construction concern. Deferred to Group E.

## Phase 5f Commit 9: arithmetic predicates (Group D)

**Date:** 2026-05-03. **Status:** active. 4 PART operators in
lex + 4 S rules. Refs: plan §11.1 Group D; R&B 1986 §3
(glances at this register); S&O 1972 doesn't cover the
arithmetic-predicate register; Phase 5f Commits 1-8 (cardinals
consumed unchanged).

### Lex change

4 PART entries added to ``data/tgl/particles.yaml`` with an
``OP`` feature:

- ``dagdag`` — OP=PLUS. Coexists with the existing ``dagdag``
  VERB root (in ``data/tgl/verbs.yaml``, "add to"); the bare
  uninflected form is _UNK from the verbal pipeline (no
  paradigm cell emits a bare form), so adding the PART entry
  introduces no ambiguity in the verbal use cases (which
  always carry a voice/aspect prefix or infix).
- ``bawas`` — OP=MINUS. Same coexistence story as ``dagdag``.
- ``beses`` — OP=TIMES. **Coexists with the existing**
  ``beses`` **NOUN** with SEM_CLASS=FREQUENCY (Phase 5f
  Commit 5). Both readings now exist in the morph index; the
  PART reading fires in arithmetic-operator positions, the
  NOUN reading in periphrastic-frequency NP positions. Same
  coexistence pattern as ``na`` (LINK vs ASPECT_PART).
- ``hati`` — OP=DIVIDE.

### Grammar change

4 new S rules:

```text
S → NUM[CARDINAL=YES] PART NUM[CARDINAL=YES] PART[LINK=AY] NUM[CARDINAL=YES]
Equations:
  (↑ PRED) = 'ARITHMETIC'
  (↑ OP) = '<OP>'                 # PLUS | MINUS | TIMES
  (↑ OPERAND_1) = ↓1 CARDINAL_VALUE
  (↑ OPERAND_2) = ↓3 CARDINAL_VALUE
  (↑ RESULT) = ↓5 CARDINAL_VALUE
  (↓2 OP) =c '<OP>'                # constraining: right operator
  (↓1 CARDINAL) =c 'YES'
  (↓3 CARDINAL) =c 'YES'
  (↓5 CARDINAL) =c 'YES'
```

3 rules for plus / minus / times. Division has 6 daughters
because ``hati`` takes a ``sa``-marked divisor:

```text
S → NUM[CARDINAL=YES] PART ADP[CASE=DAT] NUM[CARDINAL=YES] PART[LINK=AY] NUM[CARDINAL=YES]
Equations:
  (↑ PRED) = 'ARITHMETIC'
  (↑ OP) = 'DIVIDE'
  (↑ OPERAND_1) = ↓1 CARDINAL_VALUE
  (↑ OPERAND_2) = ↓4 CARDINAL_VALUE
  (↑ RESULT) = ↓6 CARDINAL_VALUE
  (↓2 OP) =c 'DIVIDE'
  ...
```

### Why PRED='ARITHMETIC' (no argument list)

Initial draft used ``'ARITHMETIC <SUBJ>'`` mirroring the
predicative-cardinal rule from Commit 4. But arithmetic
expressions have no conventional SUBJ — there's no NP
argument that maps to SUBJ in the f-structure (the operands
and result are CARDINAL_VALUE features, not NP arguments).
Using ``<SUBJ>`` triggered the LFG Subject Condition and
Completeness checks ("PRED 'ARITHMETIC' requires 'SUBJ' but
it is not present"). Dropping the argument list produces a
valid LFG f-structure: PRED is just a label, no governable GFs
required.

### Why constraining equations on every operand

The pattern matcher is non-conflict — without
``(↓1 CARDINAL) =c 'YES'``, a NUM[ORDINAL=YES] (Phase 5f
Commit 7) could match the ``NUM[CARDINAL=YES]`` daughter
slot. The constraining equations enforce CARDINAL-only at
each operand position. Same fix-pattern as Commit 6's
PART[DECIMAL_SEP=YES] constraint and Commit 7's
NUM[ORDINAL=YES] constraint.

### Out of scope for this commit

- Symbol-form arithmetic (``2 + 3 = 5``, ``10 - 3 = 7``,
  etc.) — tokenizer expansion track; §18 out-of-scope.
- Spanish-borrowed ``multiplikado`` synonym for ``beses``
  (TIMES). Less common than the native form; lex-only
  follow-on if corpus pressure surfaces it.
- Compound expressions (``Dalawa dagdag tatlo dagdag apat ay
  siyam`` "2+3+4=9") — would need a recursive NUMOP rule;
  deferred.
- Decimal operands (``Dos punto singko dagdag isa ay tatlo
  punto singko`` "2.5+1=3.5") — the decimal NUM from Commit
  6 satisfies ``NUM[CARDINAL=YES]`` and CARDINAL_VALUE only
  records the integer part, so this would partially work
  (operand_1=2 not 2.5). Defer until full decimal-value
  representation lands.
- Ordinal arithmetic (no such thing in standard usage; the
  ordinal/cardinal disjointness from Commit 7 prevents it
  structurally).

## Phase 5f Commit 10: clock-time NOUNs (Group E item 1)

**Date:** 2026-05-03. **Status:** active. Lex-only (12 entries);
no grammar changes. Refs: plan §11.1 Group E item 1; R&G 1981;
S&O 1972 §6.13.

### Lex change

12 NOUN entries added to ``data/tgl/nouns.yaml`` for the
Spanish-borrowed clock-time terms:

- ``alauna`` (1 o'clock — special vowel-initial contraction:
  ``ala-`` + ``una`` not ``alas-uno``).
- ``alasdos`` (2), ``alastres`` (3), ``alaskuwatro`` (4),
  ``alassingko`` (5), ``alassais`` (6), ``alassiyete`` (7),
  ``alasotso`` (8), ``alasnuwebe`` (9), ``alasdies`` (10),
  ``alasonse`` (11), ``alasdose`` (12).

Each NOUN with ``SEM_CLASS: TIME`` and ``TIME_VALUE``: the
hour as a string ("1" through "12").

### Why no grammar change

Clock-time NPs use the existing NP-from-N rules (``NP[CASE=DAT]
→ ADP[CASE=DAT] N``) with ``sa`` as the DAT marker. Sentence-
level attachment is via the standard intransitive-AV ADJUNCT
routing. ``Pumunta ako sa alasotso`` "I went at 8 o'clock"
parses with ``alasotso`` as the head N of a sa-marked DAT NP,
attached to the matrix as ADJUNCT.

### Orthography choice: single-token

The standard orthography for clock-time terms is hyphenated
(``ala-una``, ``alas-otso``, ``alas-dose``). The current
tokenizer splits on hyphens (``alas-otso`` → ``alas`` + ``-`` +
``otso``), so the standard orthography would require either:

- A tokenizer pre-pass that recognises and merges
  ``alas?-NUM`` patterns into a single token before morph.
- A grammar rule that consumes ``alas`` + hyphen + cardinal as
  a single TIME constituent.

Both are deferred to a follow-on commit. This commit uses
single-token forms (``alauna`` / ``alasotso`` / etc.) — a real
attested orthographic variant in informal text — that work with
the existing tokenizer unchanged.

### Out of scope for this commit (deferred to follow-on Group E commits)

- Hyphenated orthography (``ala-una`` / ``alas-otso``).
- Time-of-day modifiers (``alasotso ng umaga`` "8 in the
  morning"; ``alasotso ng hapon`` "8 in the afternoon"). Needs
  ``umaga`` / ``hapon`` / ``gabi`` / ``tanghali`` /
  ``madaling-araw`` lex with SEM_CLASS=TIME plus a small
  modifier rule.
- Minute composition: ``alasotso y medya`` 8:30, ``alasotso
  y singko`` 8:05, ``alasotso menos singko`` 7:55. Needs
  ``y`` and ``menos`` PART entries plus a
  ``TIME → CLOCK [y|menos] NUM`` rule.
- Native time deictics: ``kanina`` (earlier today), ``mamaya``
  (later today), ``tanghali`` (noon), ``madaling-araw`` (dawn).
  ``ngayon``, ``bukas``, ``kahapon``, ``mamaya`` already exist
  as ADV; the missing ones plus a uniform SEM_CLASS=TIME tag.
- ``mga`` time approximation (``mga alasotso`` "around 8
  o'clock") — ``mga`` itself isn't in lex yet.

## Phase 5f Commit 11: time-of-day NOUNs + native time deictics (Group E items 2 + 5)

**Date:** 2026-05-03. **Status:** active. Lex-only addition;
no grammar changes. Refs: plan §11.1 Group E items 2 + 5;
S&O 1972 §6.13; Phase 5f Commits 5 + 10.

### Lex change

- **Time-of-day NOUNs** (``data/tgl/nouns.yaml``):
  ``umaga`` (morning), ``tanghali`` (noon / midday),
  ``hapon`` (afternoon). All NOUN with SEM_CLASS=TIME.
  ``gabi`` (night) and ``araw`` (day / sun) already exist as
  plain NOUN entries in nouns.yaml; not modified here to keep
  the diff focused — they compose via existing rules without
  the SEM_CLASS feature.
- **Native time deictics** (``data/tgl/particles.yaml``):
  ``kanina`` (earlier today), ``kamakalawa`` (day before
  yesterday). Both ADV with ADV_TYPE=TIME and
  DEIXIS_TIME=PAST. Parallel structure to the existing
  ``kahapon`` / ``ngayon`` / ``bukas`` / ``mamaya`` ADV entries.

### Why no grammar change

Time-of-day modifier composition (``alasotso ng umaga`` "8 in
the morning") parses via the existing Phase 4 §7.8 NP-internal
possessive rule:

- ``alasotso`` — clock-time NOUN (Phase 5f Commit 10)
- ``ng umaga`` — GEN-NP modifier
- The possessive rule attaches GEN-NP as POSS to the head N

So ``alasotso ng umaga`` parses with ``umaga`` as the
syntactic POSS of ``alasotso``. Semantically it's time-of-day
modification, not possession; the parser delivers the
constituency, the semantic distinction is downstream.

Direct DAT use (``Pumunta ako sa umaga`` "I went in the
morning") parses via the standard intransitive-AV ADJUNCT
routing — ``sa umaga`` is a DAT-NP that attaches as an
adjunct.

### Time deictics: ay-fronting yes, bare clause-final no

The new ADV deictics ``kanina`` / ``kamakalawa`` work in
ay-fronting position (``Kanina ay pumunta ako`` "Earlier today
I went") via the Phase 5e Commit 3 ay-fronting rule, which
accepts AdvPs of any ADV_TYPE.

But bare clause-final TIME-AdvP placement (``Pumunta ako
kanina``) is **still deferred**. The Phase 5f Commit 5
sentential-AdvP rule (``S → S AdvP``) carries the constraining
equation ``(↓2 ADV_TYPE) =c 'FREQUENCY'`` — restricted to
FREQUENCY adverbs only. The TIME / SPATIAL / MANNER deferral
from Phase 5e Commit 3 stays in force because those interact
with the Wackernagel cluster and quantifier-float in ways that
need separate analytical work.

The lex entries are added now so they're available when the
TIME deferral lifts.

### Out of scope for this commit

- Bare clause-final TIME AdvP (``Pumunta ako kanina``) —
  Phase 5e Commit 3 deferral, lifted in a separate commit.
- ``madaling-araw`` "dawn" — hyphenated single-word concept,
  needs tokenizer pre-pass; deferred.
- Updating existing ``gabi`` / ``araw`` / ``bukas`` /
  ``oras`` to add SEM_CLASS=TIME — keep diff focused; they
  compose via existing rules without the feature.
- Minute composition (``alasotso y medya`` 8:30) — needs
  ``y`` and ``menos`` PART entries plus a ``TIME → CLOCK
  [y|menos] NUM`` rule; follow-on commit.
- ``mga`` time approximation (``mga alasotso``) — ``mga``
  isn't yet in lex; needs broader ``mga`` analysis (also
  marks plurals).

## Phase 5f Commit 12: minute composition (Group E item 4)

**Date:** 2026-05-03. **Status:** active. 2 PART operators in
lex + 4 N grammar rules + a side change to ``N → NOUN``. Refs:
plan §11.1 Group E item 4; S&O 1972 §6.13; Phase 5f Commits 5
\+ 8 + 10 + 11.

### Lex change

2 PART operators added to ``data/tgl/particles.yaml``:

- ``y`` — Spanish "and"; PART with MINUTE_OP=Y. Forward-
  counting: ``alasotso y singko`` "8:05".
- ``menos`` — Spanish "minus"; PART with MINUTE_OP=MENOS.
  Backward-counting: ``alasotso menos singko`` "7:55".

### Grammar change

4 new N rules — 2 ops × 2 daughter types:

```text
N → N PART NUM[CARDINAL=YES]                   (cardinal minute)
Equations:
  (↑) = ↓1
  (↑ MINUTE_VALUE) = ↓3 CARDINAL_VALUE
  (↑ MINUTE_OP) = '<OP>'
  (↓1 SEM_CLASS) =c 'TIME'                     (head is clock-time)
  (↓2 MINUTE_OP) =c '<OP>'                     (operator is right one)
  (↓3 CARDINAL) =c 'YES'                       (third is cardinal)

N → N PART N                                   (fractional minute)
Equations:
  (↑) = ↓1
  (↑ MINUTE_FRACTION) = ↓3 LEMMA
  (↑ MINUTE_OP) = '<OP>'
  (↓1 SEM_CLASS) =c 'TIME'
  (↓2 MINUTE_OP) =c '<OP>'
  (↓3 SEM_CLASS) =c 'FRACTION'                 (third is fraction)
```

The output is N (the same category as the head clock-time
NOUN), so the result composes via existing NP-from-N rules
into NP[CASE=DAT] / NP[CASE=NOM] / etc. without any further
grammar additions.

The MINUTE_OP / MINUTE_VALUE / MINUTE_FRACTION features are
on the inner N. The NP-from-N projection only takes PRED +
LEMMA, so these features stay on N and aren't visible at the
NP level (same limitation as cardinal-modified N → NP from
Commit 1). Tests verify parse-success rather than feature-
value access — the rule's internals are correct; if it fires,
the features are set on the inner N.

### Side change: ``N → NOUN`` rule

The minute-composition rule needs ``(↓1 SEM_CLASS) =c 'TIME'``
on the head N. But the existing ``N → NOUN`` rule projected
only ``PRED`` and ``LEMMA`` from NOUN to N — SEM_CLASS / etc.
stayed on the lex token's f-structure and weren't visible at
the N level.

The rule was updated to use full sharing (``(↑) = ↓1``)
instead of explicit per-feature projection. Now SEM_CLASS
(and TIME_VALUE, and any other lex feature on the NOUN)
percolates from NOUN to N. PRED is still set explicitly
(``(↑ PRED) = 'NOUN(↑ FORM)'``) because lex equations don't
provide a PRED for plain nouns (only when a LexicalEntry
with a PRED template is attached, which is rare in the seed
lex). LEMMA percolates automatically via the shared structure.

This change passes the entire existing test suite without
regression — projecting MORE features from NOUN to N is
strictly additive for downstream consumers.

### kuwarto clock-fraction polysemy: deferred

The plan mentioned ``kuwarto`` "quarter (of the hour)" as a
fractional minute (``alasotso y kuwarto`` 8:15). But ``kuwarto``
already exists as a NOUN ("room") in nouns.yaml. Adding a
duplicate ``kuwarto`` entry with SEM_CLASS=FRACTION causes
the morph analyzer to collapse the entries — only the latest
one is returned, shadowing the "room" reading.

Polysemy resolution requires either:

1. Analyzer support for multiple lex entries per (lemma, pos)
   tuple, returning all readings.
2. A dedicated CLOCK-FRACTION sub-class that doesn't conflict
   with the NOUN-room reading.
3. Modifying the existing ``kuwarto`` to add SEM_CLASS=FRACTION
   (loses the SEM-class-based "room" disambiguation but works
   for both readings since SEM_CLASS isn't constrained by
   non-clock rules).

Deferred to a follow-on commit. The minute-composition rule
fires correctly on ``kalahati`` / ``medya`` (FRACTION nouns
without polysemy issues); ``kuwarto`` is the only deferred
case.

### Out of scope for this commit

- ``alasotso y kuwarto`` parsing — see polysemy deferral
  above.
- Chained minute compositions (``*alasotso y singko y dies``)
  — would require recursive composition; not standard usage.
- Symbolic time forms (``8:30``, ``8:05``) — tokenizer
  expansion track; §18 out-of-scope.
- MINUTE_OP / MINUTE_VALUE / MINUTE_FRACTION projection to NP
  — same NP-from-N limitation as cardinal-modifier features
  from Commit 1.

## Phase 5f Commit 13: dates (Group F)

**Date:** 2026-05-03. **Status:** active. 19 NOUN entries +
2 PART entries + 4 grammar rules (3 PP variants + 1 S rule).
Refs: plan §11.1 Group F; S&O 1972 §6.13; Phase 5f Commits 7
(ordinals) + 11 (time deictics).

### Lex change

**Months** (data/tgl/nouns.yaml): 12 Spanish-borrowed month
names (``enero`` ... ``disyembre``) as NOUN with
``SEM_CLASS: MONTH`` and ``MONTH_VALUE`` (1-12).

**Days of week** (data/tgl/nouns.yaml): 7 day-of-week NOUNs
— Spanish-borrowed (``lunes``, ``martes``, ``miyerkules``,
``huwebes``, ``biyernes``, ``sabado``) and native
(``linggo``). All NOUN with ``SEM_CLASS: DAY`` and
``DAY_VALUE`` (1-7). The existing ``linggo`` entry was
updated in place to add SEM_CLASS=DAY (rather than adding a
duplicate, which the morph analyzer collapses — see Phase 5f
Commit 12 kuwarto polysemy memo).

**Temporal-frame PARTs** (data/tgl/particles.yaml):

- ``tuwing`` (every) — PART with ``TIME_FRAME: PERIODIC``.
  Introduces a periodic temporal-frame PP.
- ``noong`` (last / past) — PART with ``TIME_FRAME: PAST``.
  Introduces a past temporal-frame PP.

### Grammar change

**3 PP rules** (gated by SEM_CLASS):

```text
PP → PART N
Equations:
  (↑) = ↓1
  (↑ OBJ) = ↓2
  (↓1 TIME_FRAME)              # existential — PART has TIME_FRAME
  (↓2 SEM_CLASS) =c '<X>'      # X in {DAY, TIME, MONTH}
```

3 rules covering DAY, TIME, MONTH SEM_CLASSes. The
constraining equations gate the rule to genuinely temporal
NOUNs only — ``*tuwing bata`` (no SEM_CLASS) doesn't compose
because the constraining equation fails. Other temporal
SEM_CLASSes (FRACTION, PERCENTAGE, etc.) also don't fire
because they're not in the explicit DAY/TIME/MONTH set.

**1 S rule** for clause-final temporal-frame PP attachment:

```text
S → S PP
Equations:
  (↑) = ↓1
  ↓2 ∈ (↑ ADJUNCT)
  (↓2 TIME_FRAME)              # existential — PP has TIME_FRAME
```

Closes part of the Phase 5e Commit 3 deferral on bare PP
placement — scoped to TIME_FRAME PPs only via the existential
constraint. The existing PREP-PPs (``para sa X``,
``tungkol sa X``, ``mula sa X``, ``dahil sa X``) don't have
TIME_FRAME, so this rule doesn't fire on them — they remain
restricted to ay-fronting position (Phase 5e Commit 3
deferral remains in force for non-TIME_FRAME PPs).

Same scoped-lift pattern as Phase 5f Commit 5's
``S → S AdvP[FREQUENCY]``.

### Date formula (Commit 11)

The formula ``ang ikalimang araw ng Enero`` "the fifth day
of January" composes from existing rules:

- ``ikalimang araw`` — ordinal-NP-modifier rule (Phase 5f
  Commit 7) — ``ikalima`` + ``-ng`` + ``araw`` produces an
  N with ORDINAL_VALUE=5 and LEMMA=araw.
- ``ang ikalimang araw`` — existing ``NP[CASE=NOM] →
  DET[CASE=NOM] N`` rule.
- ``ng Enero`` — existing GEN-NP rule.
- ``ang ikalimang araw ng Enero`` — existing Phase 4 §7.8
  NP-internal possessive rule attaches GEN-NP as POSS.

No new grammar required.

### Out of scope for this commit (date formulas)

- **Day-month abbreviated form** (``Mayo 5``) — needs digit
  tokenization (the one digit-form case the linguistic scope
  can't avoid per plan §11.1 Group F item 4). Tokenizer pre-
  pass is the cleanest fix; deferred.
- **Elided-N date formula** (``ang ikalima ng Enero``
  without ``araw``) — needs an ordinal-as-N rule. Not
  standard in formal Tagalog (the explicit ``araw`` is
  preferred); deferred.
- **Year expressions** (``noong 1990``) — needs digit
  tokenization.
- **MONTH_VALUE / DAY_VALUE projection to PP/NP** — same
  NP-from-N projection limitation as cardinal-modifier
  features.
- **Other temporal SEM_CLASSes for tuwing/noong** —
  e.g., season (``tuwing tag-init`` "every dry season"). Add
  SEM_CLASS=SEASON to the rule's variant list when Group G
  seasons land.

## Phase 5f Commit 13 (bundled): mga time approximation (Group E item 3)

**Date:** 2026-05-03. **Status:** active. 1 PART entry + 1
grammar rule. Refs: plan §11.1 Group E item 3; Phase 5f
Commit 10 (clock-time NOUNs consumed unchanged).

This work landed inside the bundled git Commit 13 (``ec23c55
Phase 5f Commit 13 — mga time approximation (Group E item 3)
\+ dates (Group F)``); originally sequenced as a separate
Commit 14 in the plan but bundled when the mga gap was
identified during Group F work. The plan's Commit-14 slot is
re-used by Group G seasons below.

### Lex change

- ``mga`` PART (data/tgl/particles.yaml) with
  ``PLURAL_MARKER: YES``. The Tagalog plural / approximator
  particle, used for both plural marking on regular nouns
  (``ang mga aklat`` "the books") and approximation on
  temporal / quantitative NPs (``mga alasotso`` "around 8
  o'clock", ``mga sampu`` "around 10"). This commit adds the
  lex entry plus a grammar rule for the time-approximation
  reading only; plural marking and cardinal approximation
  are deferred to follow-on commits.

### Grammar change

```text
N → PART N
Equations:
  (↑) = ↓2                          # share with head N
  (↑ APPROX) = 'YES'                 # add APPROX feature
  (↓1 PLURAL_MARKER) =c 'YES'       # particle is mga
  (↓2 SEM_CLASS) =c 'TIME'          # head is clock-time
```

Output is N (same category as the head clock-time NOUN), so
``sa mga alasotso`` composes via existing NP-from-N rules
into NP[CASE=DAT] without further grammar additions.

### Why TIME-only

The plan note allows DAY / MONTH approximation in principle,
but ``mga Lunes`` / ``mga Pebrero`` are not idiomatic in
standard Tagalog (they would mean "plural Mondays" /
"plural Februarys", not "around Monday" / "around February").
So the approximator rule is restricted to SEM_CLASS=TIME.

Cardinal approximation (``mga sampu`` "around ten") is a
parallel construction with NUM[CARDINAL=YES] daughter; the
plan calls for it as a follow-on.

### Out of scope for this commit (mga time-approximator)

- **Plural marker on regular nouns** (``ang mga aklat`` "the
  books") — needs an NP-internal rule for ``DET PART[mga] N``
  plural marking, plus possibly NUM agreement effects.
  Substantial scope; deferred.
- **Cardinal approximation** (``mga sampu`` "around ten") —
  parallel rule with NUM[CARDINAL=YES] daughter. Lex-only
  follow-on — the rule already exists in shape, just needs
  a NUM variant.
- **DAY / MONTH approximation** — not idiomatic in standard
  Tagalog.
- **APPROX projection to NP** — same NP-from-N projection
  limitation as cardinal-modifier features (Commit 1).

### Side change (Commit 4): `synonyms` lex field + ``aklat`` noun

This commit adds a ``synonyms: list[str]`` field to the ``Root``
dataclass and YAML loader so synonymous lex citations can be
recorded as data (not just comments). Motivated by adding
``aklat`` "book" to ``data/tgl/nouns.yaml`` as the canonical
``Sandaan ang aklat`` example (Ramos 1971: "aklát n. book.
--syn. libró."). Both ``aklat`` and the existing ``libro``
entries get bidirectional ``synonyms`` lists. The field is
backward-compatible (defaults to an empty list) and currently
unused by the parser — it's recorded for downstream tools
(dictionary export, cross-reference, future ranker semantic
similarity).

### Out of scope for this commit (synonyms lex field)

- Cardinal as predicate over a clausal SUBJ
  (``Tatlo na siyang anak ang nakain ng isda`` "the three of
  her children who ate fish are gone") — would need
  embedding-rule extension; not standard usage.
- Predicative-cardinal in subordinate clauses (``Sinabi niya
  na tatlo ang anak ko``) — the linker-XCOMP / linker-COMP
  machinery from Phase 5c §7.6 should compose; not explicitly
  tested here but no expected change to that machinery.
- Number-agreement enforcement (``Tatlo ako`` would be
  semantically odd — "I am three" — but currently parses
  without any agreement check). The matrix NUM (from cardinal)
  and the SUBJ NUM live on different f-structures with no
  unifying equation. Adding agreement is a follow-on; out of
  scope for this commit.

## Phase 5f Commit 14: seasons (Group G)

**Date:** 2026-05-03. **Status:** active. 5 NOUN entries +
1 grammar-rule extension (existing Commit 13 PP rule gains a
SEASON variant). Refs: plan §11.1 Group G; R&B 1986; S&O 1972
§6.13; Phase 5f Commit 13 (temporal-frame PP rule consumed
with one variant added).

Closes Phase 5f §11.1 Group G (seasons) with a deliberately
small footprint — a hand-authored lex of the canonical two-
season system plus three additional ``tag-`` compounds, and
a one-line variant addition to the Phase 5f Commit 13
temporal-frame PP rule.

### Lex change

Five season NOUNs (``data/tgl/nouns.yaml``):

- ``taginit`` — hot / dry season.
- ``tagulan`` — rainy season.
- ``taglamig`` — cold spell (colloquial).
- ``tagaraw`` — sunny period.
- ``taggutom`` — hunger season (figurative).

All NOUN with ``SEM_CLASS: SEASON``. The first two are the
canonical two-season pair; the remaining three are attested
``tag-`` compounds (R&B 1986; S&O 1972 §6.13).

### Why lex-only, not productive ``tag-``

Per plan §11.1 Group G: the productive ``tag-`` morphology
*does* derive nominalisations from a wider set of bases, but
those productive readings are figurative or colloquial
(``tag-pasko`` "Christmas season" — fine; but
``tag-bili`` "buying season" — non-canonical, marketing-only)
and don't form a clean season-naming class. A hand-authored
lex per attested form is more conservative than a productive
class, avoiding the over-coverage that a productive
``tag- + N → SEASON`` rule would introduce.

### Hyphenation: deferred

The canonical orthography is ``tag-init``, ``tag-ulan``, etc.
with an internal hyphen. The current tokenizer
(``src/tgllfg/text/tokenizer.py``: ``\\w+|\\S``) splits hyphens
into three tokens — ``tag-init`` becomes
``[tag, -, init]``. The cleanest fix is a tokenizer pre-pass
that recognises a closed list of canonical hyphenated forms
(or a productive ``tag-`` glue rule) and emits them as single
tokens; that pre-pass is deferred and is the only barrier to
exposing the canonical orthography in the lex.

For now the seed lex stores the single-token forms
(``taginit``, ``tagulan``, ``taglamig``, ``tagaraw``,
``taggutom``) which compose via the standard NOUN path. This
is non-standard orthography but pragmatically equivalent for
parsing.

### Grammar change

The Phase 5f Commit 13 temporal-frame PP rule

```text
PP → PART N
Equations:
  (↑) = ↓1
  (↑ OBJ) = ↓2
  (↓1 TIME_FRAME)              # existential — PART has TIME_FRAME
  (↓2 SEM_CLASS) =c '<X>'      # X in {DAY, TIME, MONTH, SEASON}
```

gains a SEASON variant (the ``for sem_class in (...)`` loop
in ``src/tgllfg/cfg/discourse.py`` extends to four members).
This makes ``tuwing tagulan`` "every rainy season" (PERIODIC)
and ``noong taginit`` "during the dry season" (PAST) parse
via the same machinery as ``tuwing Lunes`` / ``noong
Pebrero``. The clause-final S → S PP rule is consumed
unchanged (it's gated on TIME_FRAME, not SEM_CLASS).

### Composition without new grammar

- ``sa tagulan`` "in the rainy season" — DAT-NP; the existing
  intransitive-ADJUNCT routing handles it. The SEM_CLASS=
  SEASON marking does not disturb this path.
- ``Tuwing tagulan ay pumunta ako.`` — ay-fronting of the new
  PERIODIC SEASON PP composes via the existing ay-fronting
  machinery on PPs (Phase 5e Commit 3).

### Why piggyback on the Commit 13 PP rule

The temporal-frame PP rule was authored with explicit
SEM_CLASS gating precisely to scope clause-final temporal
adjuncts to genuinely temporal NOUNs only (``*tuwing bata``
fails). Adding SEASON to the variant tuple is a one-line
extension — it doesn't change the rule's shape, doesn't
introduce a new f-structure feature, and doesn't open up the
rule to non-temporal heads. The Commit 13 author flagged this
exact follow-on in their "Out of scope" notes ("Add
SEM_CLASS=SEASON to the rule's variant list when Group G
seasons land"); this commit lifts that deferral.

An alternative (a separate season-only PP rule) would have
been wasteful — same rule shape, same constraining equations,
just a different SEM_CLASS literal.

### Negative fixtures (per §11.2)

- ``*Pumunta ako tuwing aklat.`` — ``aklat`` has no
  SEM_CLASS, so the constraining equation fails for all four
  variants (DAY / TIME / MONTH / SEASON). The PP rule does
  not fire and the sentence does not produce a TIME_FRAME PP
  parse.
- ``*Pumunta ako tuwing araw.`` — ``araw`` is an existing
  NOUN (day / sun) with no SEM_CLASS set. Including this
  fixture confirms the gate is constraining (not just
  descriptive): if the gate were missing, ``araw`` would be a
  plausible season-domain head and the rule would over-fire.
- ``aklat`` does not pick up SEM_CLASS=SEASON from anywhere.
  (Sanity check on the lex addition.)

### Out of scope for this commit

- **Hyphenated orthography** (``tag-init``, ``tag-ulan``,
  etc.) — needs the deferred tokenizer pre-pass described
  above.
- **Productive ``tag-`` paradigm** — see "Why lex-only" above.
  Adding a productive class would over-cover figurative /
  colloquial uses.
- **SEM_CLASS=SEASON projection to NP / PP-matrix** — the
  same NP-from-N projection limitation as cardinal-modifier
  features (Commit 1) and MONTH_VALUE / DAY_VALUE on date
  PPs (Commit 13). Tests walk down to the OBJ N to read
  SEM_CLASS rather than expecting it on the matrix
  PP / NP.
- **``mga`` season approximation** (``mga tagulan`` "around
  the rainy season") — not idiomatic; the analogue ``mga
  Pebrero`` is similarly non-idiomatic. Not added.

### Side change: ruff F841 cleanup in test_cardinal_predicative.py

Removed an unused local variable (``f = rs[0][1]`` at
``tests/tgllfg/test_cardinal_predicative.py:253``) that ruff
F841 flagged. The variable was assigned but never read — the
test's actual assertion logic uses a separate ``parse_text``
call below the dead assignment. Pre-existing from Phase 5f
Commit 4 (``ff4de03``). Cleaned up here so ``hatch run check``
passes ahead of the Phase 5f Group EFG PR.

## Phase 5f Commit 15: vague cardinals (Group H1 item 1)

**Date:** 2026-05-03. **Status:** active. 7 Q lex entries +
6 new NP-level grammar rules + 2 new N-level rules + 1 gating
addition on the existing Phase 5b partitive rule + 1 new
disambiguator branch. Refs: plan §11.1 Group H item 1; S&O
1972 §4.7; R&B 1986; Phase 4 §7.8 (existing ``lahat`` /
``iba`` Q-class consumed unchanged); Phase 5b §7.8 follow-on
(existing pre-NP partitive consumed with a vague-blocking
gate); Phase 5f Commit 1 (cardinal-NP-modifier rule consumed
as the structural template).

Opens Group H1 (vague + approximators + numeric comparatives)
with the largest sub-item, vague cardinals. Group H is plan
§11.1's "extensions to §7.8": Phase 4 §7.8 wired only ``lahat``
and ``iba`` as Q-class entries; Group H closes the inventory
gap. The plan §11.1 Group H header summarises the engineering
strategy: "the grammar rule is the Group A cardinal-NP-modifier
rule generalised to any NUM / Q head" — this commit lands the
Q variant of that rule.

### Lex change

Seven Q entries in ``data/tgl/particles.yaml``:

- ``ilan``      — ``Q[QUANT=FEW, VAGUE="YES"]``
- ``marami``    — ``Q[QUANT=MANY, VAGUE="YES"]``
- ``kaunti``    — ``Q[QUANT=FEW, VAGUE="YES"]``
- ``konti``     — ``Q[QUANT=FEW, VAGUE="YES"]``
- ``kakaunti``  — ``Q[QUANT=VERY_FEW, VAGUE="YES"]``
- ``iilan``     — ``Q[QUANT=FEW, VAGUE="YES"]``
- ``karamihan`` — ``Q[QUANT=MOST, VAGUE="YES"]``

The string-quoted ``"YES"`` is essential: bare ``YES`` is
parsed by YAML 1.1 as Python boolean ``True``, which would
not match the ``=c 'YES'`` constraining equation in the new
grammar rules. The existing ``CARDINAL: "YES"`` / ``ORDINAL:
"YES"`` entries follow the same convention — Group A authors
hit the same trap. (Discovered during Commit 15 development.
Worth promoting to a lex-authoring note in plan §11.2 or
docs/diagnostics.md as a recurring pitfall.)

### Why Q, not NUM[VAGUE]?

The plan describes vague cardinals as quantifiers without an
exact value, contrasting them with the precise numeric
cardinals. Two implementations were viable:

1. **NUM[VAGUE=YES]** — a sub-class of NUM. Reuses the
   existing cardinal-NP-modifier rule path with a relaxed
   constraint.
2. **Q[VAGUE=YES]** — a sub-class of Q (the existing class
   for ``lahat`` / ``iba``). Adds a parallel rule with a Q
   daughter.

Option 2 won. Reasons:

- **Semantic alignment.** ``marami`` / ``ilan`` etc. don't
  participate in arithmetic, fractions, ordinals, decimals,
  or any of the constructions in Groups A-D. They quantify
  rather than count. Grouping them with ``lahat`` / ``iba``
  reflects the actual distribution.
- **No NUM features.** Vague cardinals carry no
  CARDINAL_VALUE / ORDINAL_VALUE / NUM (sg/pl). Pretending
  they're NUM and then suppressing those features via
  constraints is more bookkeeping than benefit.
- **Plan endorsement.** §11.1 Group H literally says "any
  NUM / Q head" — both are anticipated. Q is the cleaner
  fit for vague cardinals; NUM remains for cardinals,
  ordinals, fractions, decimals, percentages, multiplicative
  ratios.

Reduplication-derived ``iilan`` (from ``isa``) and ``ka-…-an``
derived ``karamihan`` are listed as attested forms; productive
reduplication / ``ka-…-an`` morphology for vague cardinals is
deferred (out of scope for Group H1). The count-mass
distinction (``marami`` + count vs ``marami`` + mass — both
grammatical, no morphological alternation; S&O 1972 §4.7) is
lex-internal, not a syntactic split, so the lex entry is
uniform.

### Grammar change

**6 NP-level rules** (3 cases × 2 linker variants):

```text
NP[CASE=X] → DET/ADP[CASE=X] Q PART[LINK=NA|NG] N
Equations:
  (↑) = ↓1                          # CASE / MARKER from outer marker
  (↑ PRED) = ↓4 PRED                # head N supplies PRED
  (↑ LEMMA) = ↓4 LEMMA              # ... and LEMMA
  (↑ QUANT) = ↓2 QUANT              # Q lifts QUANT to NP
  (↑ VAGUE) = 'YES'                 # mark NP for downstream consumers
  ¬ (↓4 VAGUE)                      # block chained vague Qs
  (↓2 VAGUE) =c 'YES'               # gate to vague Qs only
```

The constraining equation ``(↓2 VAGUE) =c 'YES'`` is the load-
bearing piece — without it, the non-conflict matcher would
match ``lahat`` / ``iba`` (which have no VAGUE) by absence and
land them in the linker form, over-coverage no plan calls for.
Same fix-pattern as the cardinal rule's
``(↓2 CARDINAL) =c 'YES'`` (Phase 5f Commit 1) and the ordinal
rule's ``(↓2 ORDINAL) =c 'YES'`` (Phase 5f Commit 7).

The chained-vague block ``¬ (↓4 VAGUE)`` mirrors the cardinal
rule's ``¬ (↓4 CARDINAL_VALUE)``: ``*ang maraming kaunting
bata`` ("many few children"?) doesn't compose because the head
N (which is the matrix of the inner vague-Q rule) carries
VAGUE=YES, which the outer rule rejects.

**2 N-level rules** (parang etc.):

```text
N → Q PART[LINK=NA|NG] N
```

Mirrors the Phase 5f Commit 1 N-level cardinal companion. The
Phase 5e Commit 26 ``parang isang aso`` rule selects an N
daughter, so the N-level companion is needed for ``parang
maraming aso`` "like many dogs" to compose. (Not explicitly
tested in this commit — sweep coverage is at NP level — but
the rule mechanically fires.)

### Existing partitive: gating with `¬ (↓2 VAGUE)`

The Phase 5b §7.8 follow-on partitive rule (``DET/ADP Q
NP[GEN]``) had no VAGUE constraint. With the new vague Qs
added, that rule would fire on ``ang marami ng bata`` — a non-
standard surface. The plan H1 description explicitly restricts
vague cardinals to "the linker" form. So the existing
partitive gets a new constraining equation
``¬ (↓2 VAGUE)`` on each of its 3 case variants, scoping the
partitive to non-vague Qs (currently ``lahat`` / ``iba``). The
DAT-NP partitive variant of vague Qs (``marami sa kanila``
"many of them") is a separate construction — DAT-NP, not
GEN-NP — and is deferred.

### Disambiguator: linker after consonant-final vague Q

The pre-parse ``disambiguate_homophone_clitics`` step in
``src/tgllfg/clitics/placement.py`` chooses between the two
readings of ``na``: linker (``LINK=NA``) vs ALREADY clitic
(``CLITIC_CLASS=2P``, ``ASPECT_PART=ALREADY``). The choice is
left-context-driven: NOUN / NUM[CARDINAL=YES, ORDINAL=YES] /
DET[DEM=YES] before ``na`` ⇒ linker; VERB / PRON before
``na`` ⇒ clitic.

Vague Q before ``na`` was previously unhandled — the fall-
through "leave both readings" path didn't help because the
placement pass greedily moves any kept-clitic ``na`` to the
Wackernagel cluster, leaving ``[Q] [N]`` without a linker
between them. The new branch detects ``Q[VAGUE=YES]`` before
``na`` and drops the clitic reading, parallel to the existing
NUM branches. Gated on ``VAGUE=YES`` so the ``lahat`` / ``iba``
distribution (which doesn't use the linker form in Phase 5f
scope) is unaffected.

This affects only the consonant-final vague Qs (``ilan``,
``iilan``, ``karamihan``); vowel-final ones (``marami``,
``kaunti``, ``konti``, ``kakaunti``) use the bound ``-ng``
linker which has no clitic homophone, so ``maraming bata``
splits cleanly via ``split_linker_ng`` regardless of the
disambiguator.

### Negative fixtures (per §11.2)

- ``*ang maraming kaunting bata`` — chained vague Qs blocked by
  ``¬ (↓4 VAGUE)``.
- ``*ang marami ng bata`` — vague-Q in GEN-NP partitive blocked
  by the new ``¬ (↓2 VAGUE)`` gate on the existing Phase 5b
  rule.

### Out of scope for this commit

- **DAT-NP partitive for vague Qs** (``marami sa kanila``
  "many of them") — separate construction; not in Group H1
  scope. Defer.
- **Contracted ``ilang bata`` form** (irregular bound ``-ng``
  on the consonant-final stem ``ilan``) — non-standard
  contraction; would need a tokenizer pre-pass for the
  irregular split. Defer.
- **Float for vague Qs** (``Kumain sila marami``) — the
  existing Phase 4 §7.8 ``S → S Q`` float rule fires on vague
  Qs unmodified, but the binding semantics differ from
  ``lahat`` float (vague selects a subset; ``lahat`` asserts
  about the whole). Mechanically composes; semantically a
  follow-on if corpus pressure surfaces a need.
- **VAGUE projection to outer NPs (POSS, etc.)** — same NP-
  from-N projection limitation as cardinal-modifier features.

## Phase 5f Commit 16: approximators (Group H1 item 2)

**Date:** 2026-05-03. **Status:** active. 2 PART lex entries
\+ 3 new grammar rules. Refs: plan §11.1 Group H item 2; S&O
1972 §4.7; R&B 1986; Phase 5f Commit 13 (mga rule consumed
with parallel NUM extension); Phase 5f Commit 1 (cardinal
NP-modifier rule consumed unchanged; cardinal NUMs flow
through the new wrap rule); Phase 5b (partitive) and Phase 5f
Commit 15 (vague-Q-modifier) consumed unchanged for the Q
wrap. docs/analysis-choices.md "Phase 5f Commit 13 (bundled):
mga" entry — the cardinal-approximation deferral noted there
is lifted in this commit.

### Lex change

Two PART entries in ``data/tgl/particles.yaml``:

- ``halos`` — PART[APPROX="YES"]. "almost / nearly".
- ``humigitkumulang`` — PART[APPROX="YES"]. "approximately /
  more or less". Stored as the single-token form.

Hyphenation note: the canonical orthography is
``humigit-kumulang``. The tokenizer (``\w+|\S``) splits
hyphens, so the canonical surface tokenises as 3 tokens
(``humigit``, ``-``, ``kumulang``) — and ``humigit`` happens
to also analyse as the AV PFV form of the verb root ``higit``
"exceed" (an unrelated coincidence that would create
ambiguous parses if unguarded). The single-token form
``humigitkumulang`` sidesteps both issues. Same pragmatic
precedent as Phase 5f Commit 14 seasons (``taginit`` for
canonical ``tag-init``); the canonical hyphenated form awaits
a tokenizer pre-pass.

The string-quoted ``"YES"`` in the lex entry matters for the
same reason as Phase 5f Commit 15: bare ``YES`` parses as
Python boolean ``True``, which would not match the
``=c 'YES'`` constraining equation. (Same recurring pitfall;
worth mentioning in plan §11.2 / docs/diagnostics.md.)

### Grammar change

Three new rules in ``src/tgllfg/cfg/nominal.py``:

**1. Cardinal-NUM approximator wrap.**

```text
NUM → PART[APPROX=YES] NUM[CARDINAL=YES]
Equations:
  (↑) = ↓2                          # share daughter NUM's f-structure
  (↑ APPROX) = 'YES'                # add APPROX feature
  (↓1 APPROX) =c 'YES'              # gate to APPROX-marked PART
  (↓2 CARDINAL) =c 'YES'            # gate to cardinal NUM
```

The output category is NUM (preserving CARDINAL=YES,
CARDINAL_VALUE, NUM=PL/SG), so the matrix-NP cardinal-
modifier rule (Phase 5f Commit 1) consumes the wrapped NUM
unchanged. ``halos sampu`` "almost ten" produces NUM[CARDINAL=
YES, CARDINAL_VALUE=10, APPROX=YES, NUM=PL]; the cardinal-
modifier rule's ``(↓2 CARDINAL) =c 'YES'`` constraint matches,
the matrix NP gains CARDINAL_VALUE=10, and APPROX rides on
the inner NUM.

**2. Q-approximator wrap.**

```text
Q → PART[APPROX=YES] Q
Equations:
  (↑) = ↓2
  (↑ APPROX) = 'YES'
  (↓1 APPROX) =c 'YES'
```

Output is Q (preserving QUANT, VAGUE), so the existing Phase
5b ``Q + NP[GEN]`` partitive (``halos lahat ng bata`` "almost
all of the children") and the Phase 5f Commit 15 vague-Q-
modifier (``halos maraming bata`` "almost many children")
consume the wrapped Q unchanged. The Q rule has no daughter-
gating constraint beyond ``(↓1 APPROX) =c 'YES'`` — any Q
(lahat / iba / vague) can be wrapped.

**3. Broader mga: extension to cardinal NUMs.**

```text
NUM → PART[PLURAL_MARKER=YES] NUM[CARDINAL=YES]
Equations:
  (↑) = ↓2
  (↑ APPROX) = 'YES'
  (↓1 PLURAL_MARKER) =c 'YES'
  (↓2 CARDINAL) =c 'YES'
```

Parallel to the Phase 5f Commit 13 ``N → PART[mga] N`` rule
(time approximation), this rule extends ``mga`` to cardinal
NUMs. Same lex entry (``mga`` with PLURAL_MARKER=YES); same
APPROX=YES output; different daughter category (NUM not N).

The Commit 13 doc note explicitly flagged this follow-on
("Cardinal approximation (``mga sampu`` "around ten") use the
same ``mga`` lex entry but are separate constructions;
deferred follow-ons"); this commit lifts that deferral. The
in-source comment on the Commit 13 N rule has been updated
to point at the new NUM rule.

### Why three rules, not one with disjunction

The grammar engine doesn't currently support disjunction in
RHS categories or constraining equations. Three flat rules
each gated on a different combination of features is the
cleanest expression. The three are structurally similar (same
shared-fstruct pattern; same APPROX=YES output) but the
gating differs:

| Rule | Daughter PART feature | Daughter content category gate |
| ------ | ------------------------ | -------------------------------- |
| 1 (halos cardinal) | APPROX=YES | CARDINAL=YES on NUM |
| 2 (halos Q) | APPROX=YES | (no gate; any Q) |
| 3 (mga cardinal) | PLURAL_MARKER=YES | CARDINAL=YES on NUM |

A future grammar-engine extension supporting feature-
disjunction in constraining equations (``(↓1 APPROX) =c 'YES'
| (↓1 PLURAL_MARKER) =c 'YES'``) would let rules 1 and 3
collapse into one. Out of scope here.

### Cardinal-NP-modifier rule consumes the wrap unchanged

The matrix-NP cardinal-modifier rule (Phase 5f Commit 1)
specifies ``NUM[CARDINAL=YES]`` as its daughter category. The
wrap rule's output is exactly that category — same surface,
new APPROX feature. So ``halos sampu`` slots in wherever
``sampu`` does:

- ``Bumili ako ng halos sampung aklat.`` — OBJ position.
- ``Kumakain ang halos sampung bata.`` — SUBJ position.
- ``Pumunta ako sa halos sampung bahay.`` — DAT position.
- ``Halos sampu ang aklat ko.`` — predicative position
  (Phase 5f Commit 4 predicative-cardinal rule).

The matrix NP (or matrix predicate clause, in the predicative
case) doesn't lift APPROX from the daughter NUM — same NP-
from-N projection limitation as cardinal-modifier features.
Tests walk down to the inner NUM to verify APPROX=YES.

### Negative fixtures (per §11.2)

- ``*Pumunta ako sa halos bata.`` — ``bata`` is N (not NUM/Q
  with APPROX gating). The wrap rules' constraining equations
  fail; no parse composes ``halos`` as an approximator
  modifier on ``bata``.
- ``*Pumunta ako halos.`` — bare ``halos`` with no NUM/Q
  daughter. The wrap rules require a daughter; without one
  the rule doesn't fire.

### Out of scope for this commit

- **Hyphenated ``humigit-kumulang`` orthography** — needs the
  same tokenizer pre-pass deferred for Phase 5f Commit 14
  seasons.
- **``malapit sa NUM``** "close to N" — multi-word
  approximator with a DAT-NP complement
  (``malapit sa sampu`` "close to ten"). Analytically more
  involved than the simple pre-modifier; the head ``malapit``
  is an adjective and the construction needs an
  ADJ + DAT-NP frame rule. Deferred to a later commit.
- **APPROX percolation to the matrix NP** — same NP-from-N
  projection limitation as cardinal-modifier features
  (Commit 1) and SEASON percolation (Commit 14). Could be
  lifted by extending the Commit 1 / Commit 7 / Commit 15
  NP-modifier rules to lift APPROX explicitly; out of scope
  for this commit.
- **mga DAY / MONTH approximation** — non-idiomatic; flagged
  out-of-scope in Commit 13 and remains so.

## Phase 5f Commit 17: numeric comparatives (Group H1 item 3)

**Date:** 2026-05-03. **Status:** active. 4 PART lex entries
\+ 4 new grammar frame rules. Refs: plan §11.1 Group H item 3
(numeric comparatives) + Group H header (NUM/Q rule
generalisation thesis); S&O 1972 §4.7; R&B 1986; Phase 5f
Commit 1 (cardinal NP-modifier rule consumed unchanged for the
wrapped NUM); existing intransitive negation, the verb-root
``higit`` (consumed unchanged via polysemy), the verb roots
``baba`` and ``higit`` paradigm-generated CTPL forms (consumed
unchanged via polysemy), and the existing ``ADP[CASE=DAT]``
``sa`` (consumed unchanged).

Closes Group H1 (vague + approximators + numeric comparatives)
with the smallest-but-most-idiomatic sub-item: numeric
comparatives. The plan's thesis "These compose existing
constituents (negation hindi, the NEG-headed copula in
bababa / hihigit, DAT-NP sa NUM) plus a small frame rule for
the NUM modifier" is realised as a tagged-PART lex
(``COMP_PHRASE``) plus four parallel frame rules each gated
on a specific lex tag.

### Lex change

Four PART entries in ``data/tgl/particles.yaml``:

- ``higit``    — PART[COMP_PHRASE="HIGIT"]. Solo use: "more (than)".
- ``kulang``   — PART[COMP_PHRASE="KULANG"]. Solo use: "less (than)".
- ``bababa``   — PART[COMP_PHRASE="BABABA"]. Negated-context use:
                 ``hindi bababa`` "no less than / at least".
- ``hihigit``  — PART[COMP_PHRASE="HIHIGIT"]. Negated-context use:
                 ``hindi hihigit`` "no more than / at most".

### Polysemy with verb-form analyses

``higit`` is also a verb root in verbs.yaml (``higit`` "pull,
exceed", VERB; affix_class ``[um, mag, in_oblig, maka]``).
``bababa`` is generated by the paradigm engine as the AV CTPL
of root ``baba`` "descend"; ``hihigit`` is the AV CTPL of root
``higit``. Adding these four surfaces as PART entries here
creates polysemy with the verb / verb-form analyses; the morph
analyzer returns both (different POS), and the parser picks
the analysis that yields a successful parse.

Polysemy via different POS does NOT trigger the analyzer's
duplicate-collapse semantics (which only fires on identical
``(lemma, pos)`` keys — the same trap that hit ``kuwarto`` /
``linggo`` in earlier commits). Verified: tokens for
``bababa`` and ``hihigit`` return both PART (new) and VERB
(existing) analyses; ``higit`` returns only PART (the bare
verb root doesn't surface as a finite form in normal
sentences); ``kulang`` returns only PART (no existing root).

The frame rules require PART daughters at specific positions,
so VERB analyses are eliminated by the rule's POS constraint
in the comparative context. Conversely, when bababa / hihigit
appear as finite verb forms in normal clauses (``Bababa ang
bata.`` "The child will descend."), the VERB analyses fire
via the existing intransitive-AV S rule. Both paths coexist
without interference.

### Why ``COMP_PHRASE`` tags rather than COMP values directly

A simpler-looking design would put COMP=GT on ``higit`` lex,
COMP=LT on ``kulang``, etc., and have rules read the COMP
value off the daughter. But the negated patterns flip
semantics: ``bababa sa N`` alone (uncompounded with hindi)
means "less than N" (LT), but ``hindi bababa sa N`` means "no
less than N" (GE). The lex value would have to be either the
intrinsic semantics or the after-composition semantics; either
choice creates inconsistencies for the other rule (solo vs
negated).

The chosen design — ``COMP_PHRASE`` as an opaque lex tag,
``COMP`` set explicitly by each frame rule — keeps the lex
neutral on the comparator's compositional behaviour and
collects the COMP=value decision into the rule that has full
context (with or without ``hindi``). The four rules become
pleasingly symmetric:

| Rule | Daughters | COMP value |
| ------ | ----------- | ------------ |
| 1 | ``PART[HIGIT] ADP[DAT] NUM[CARDINAL=YES]`` | GT |
| 2 | ``PART[KULANG] ADP[DAT] NUM[CARDINAL=YES]`` | LT |
| 3 | ``PART[NEG] PART[BABABA] ADP[DAT] NUM[CARDINAL=YES]`` | GE |
| 4 | ``PART[NEG] PART[HIHIGIT] ADP[DAT] NUM[CARDINAL=YES]`` | LE |

### Grammar change

Four parallel rules in ``src/tgllfg/cfg/nominal.py``, generated
by two ``for`` loops over ``(comp_lex, comp_value)`` pairs.

**Solo frame** (higit / kulang):

```text
NUM → PART ADP NUM
Equations:
  (↑) = ↓3                              # share inner NUM's f-structure
  (↑ COMP) = '<GT or LT>'               # set explicitly per rule
  (↓1 COMP_PHRASE) =c '<HIGIT or KULANG>'
  (↓2 CASE) =c 'DAT'                    # ``sa`` only
  (↓3 CARDINAL) =c 'YES'                # genuine cardinal NUM
```

**Negated frame** (hindi bababa / hindi hihigit):

```text
NUM → PART PART ADP NUM
Equations:
  (↑) = ↓4
  (↑ COMP) = '<GE or LE>'
  (↓1 POLARITY) =c 'NEG'                # ``hindi`` (existing)
  (↓2 COMP_PHRASE) =c '<BABABA or HIHIGIT>'
  (↓3 CASE) =c 'DAT'
  (↓4 CARDINAL) =c 'YES'
```

The ``(↑) = ↓N`` shared-fstruct on the inner NUM daughter
preserves CARDINAL=YES, CARDINAL_VALUE, NUM=PL/SG. Each rule
adds its specific ``COMP`` value. Output is NUM, so the
matrix-NP cardinal-modifier rule (Phase 5f Commit 1) consumes
the wrapped NUM unchanged — same composition pattern as
Commit 16's halos / mga wraps.

### Frame rules vs deeper compositional analysis

The plan's "small frame rule" framing is deliberate: the
alternative would be to derive ``hindi bababa sa NUM`` from
its parts via standard negation + verb + DAT-NP rules, then
syntactically lift the resulting f-structure into a NUM
modifier. That deeper analysis would expose the underlying
copular / NEG-headed structure but require more grammar (a
clause-as-NUM-modifier embedding, or a multi-stage
construction-grammar lift). The frame-rule approach is
shallower but achieves the goal: parse the four idiomatic
phrases as NUM modifiers, with COMP feature for downstream
consumers (LMT, semantics, normalization).

### Negative fixtures (per §11.2)

- ``*higit sampung aklat`` — frame rule requires the DAT
  marker ``sa`` between the comparator and the NUM standard.
- ``*higit sa bata`` — head is N (not NUM[CARDINAL=YES]); the
  ``(↓ CARDINAL) =c 'YES'`` constraint fails.
- ``*hindi bababa sampung aklat`` — negated frame rule
  requires ``sa`` (parallel to the solo frame).

### Out of scope for this commit

- **Gradable / scalar ``mas``** (without numeric reference,
  e.g., ``mas matalino`` "more intelligent") — Phase 5h
  (gradable adjective comparison). Distinct construction;
  doesn't take a numeric standard.
- **Comparators on Q heads** (``higit sa kalahati`` "more
  than half", ``higit sa lahat`` "more than all") — extending
  the frame rules to admit FRACTION / PERCENTAGE /
  MULTIPLIER / Q daughters is mechanical but additive. Defer.
- **COMP projection to the matrix NP** — the wrapped NUM
  carries COMP, but the matrix NP doesn't lift it (same NP-
  from-N projection limitation as APPROX in Commit 16,
  CARDINAL_VALUE in Commit 1, etc.). Tests verify
  CARDINAL_VALUE preservation; COMP rides on the inner NUM
  for downstream consumers.
- **Compound numeric standards** (``higit sa dalawang
  daan`` "more than two hundred") — the inner NUM standard
  composes via existing compound-cardinal rules, so this
  works mechanically with the frame rules. Not explicitly
  tested but no special handling needed.

## Phase 5f Commit 18: collective numerals (Group H2 item 4)

**Date:** 2026-05-03. **Status:** active. 4 NOUN lex entries
\+ 1 new grammar rule (with 2 linker variants). Refs: plan
§11.1 Group H item 4 (collective numerals); S&O 1972 §4.5;
R&B 1986; Phase 5f Commit 1 (cardinal NP-modifier rule
consumed unchanged for the GEN-complement form and as the
outer modifier for the LINKER-complement form); Phase 4 §7.8
(NP-internal possessive consumed unchanged for the GEN-
complement form); Phase 5f Commit 14 / Commit 16 (single-
token hyphenation precedent for canonical ``daan-daan`` /
``libu-libo`` reduplicated forms).

Opens Group H2 (collective numerals + distributive ``tig-`` +
universal ``bawat`` / ``kada``) with the largest sub-item:
collective numerals.

### Lex change

Four NOUN entries in ``data/tgl/nouns.yaml``:

- ``pares``    — NOUN[MEASURE="YES"]. "pair" (Spanish-borrowed).
- ``dosena``   — NOUN[MEASURE="YES"]. "dozen" (Spanish-borrowed).
- ``daandaan`` — NOUN[MEASURE="YES", COLL_VALUE=HUNDREDS].
                  "hundreds" (canonical orthography
                  ``daan-daan``).
- ``libulibo`` — NOUN[MEASURE="YES", COLL_VALUE=THOUSANDS].
                  "thousands" (canonical ``libu-libo``).

The string-quoted ``"YES"`` on MEASURE follows the same
recurring-pitfall convention as previous Phase 5f commits:
bare ``YES`` parses as Python boolean and fails the
``=c 'YES'`` constraining equation.

Hyphenation note: the canonical orthography for the
reduplicated forms is ``daan-daan`` and ``libu-libo``. The
tokenizer (``\w+|\S``) splits hyphens, so the canonical
surfaces tokenise as 3 tokens. The single-token forms
(``daandaan``, ``libulibo``) follow the same precedent as
seasons (``taginit``) and approximators
(``humigitkumulang``). The hyphenated form awaits a tokenizer
pre-pass.

### Two complement forms: GEN vs LINKER

Tagalog measure phrases admit two structurally distinct
complement forms, with somewhat different head-choice
implications:

**GEN-complement form** (composes via existing rules):

```text
isang pares ng sapatos          "one pair of shoes"
└──────────┬───────┘
           NP[CASE=GEN]
            ├─ NP[CASE=GEN]: ``isang pares`` (head=pares, CV=1)
            └─ NP[CASE=GEN]: ``ng sapatos`` (POSS)
```

The cardinal-modifier rule fires on ``isang pares`` (head=
pares); the NP-internal possessive rule attaches ``ng
sapatos`` as POSS. Head is the measure NOUN.

**LINKER-complement form** (uses the new measure-N rule):

```text
isang dosenang itlog            "one dozen eggs"
└────────────────┬───┘
                  NP[CASE=GEN]
                   ├─ ``isa``   NUM[CARDINAL=YES, CV=1]
                   ├─ ``-ng``    PART[LINK=NG]
                   └─ ``dosenang itlog``   N (via measure-N rule)
                                            ├─ ``dosena`` N[MEASURE=YES]
                                            ├─ ``-ng``     PART[LINK=NG]
                                            └─ ``itlog``   N
                       result: PRED + LEMMA = itlog;
                                MEASURE_HEAD = dosena;
                                MEASURE = YES.
```

The inner measure-N rule produces N with the *measured* N as
the head (PRED + LEMMA = itlog); the measure NOUN's lemma
rides as ``MEASURE_HEAD``. The cardinal-modifier rule
consumes the resulting N unchanged.

This head-choice asymmetry between GEN-form and LINKER-form
reflects a real Tagalog distinction: the GEN form quantifies
the measure ("a pair, of shoes"), while the LINKER form
quantifies the measured ("a dozen eggs"). Both are
grammatical for both lex items; the analysis-choices
implication is that downstream consumers (LMT, semantic
normalisation) must walk both paths.

### Grammar change

A single new rule with 2 linker variants:

```text
N → N PART[LINK=NA|NG] N
Equations:
  (↑ PRED) = ↓3 PRED                # head = measured (right) N
  (↑ LEMMA) = ↓3 LEMMA
  (↑ MEASURE_HEAD) = ↓1 LEMMA       # measure NOUN's lemma rides
  (↑ MEASURE) = 'YES'               # propagate upward
  (↓1 MEASURE) =c 'YES'             # gate to measure NOUNs
  ¬ (↓3 MEASURE)                    # block chained measures
```

The constraining equation ``(↓1 MEASURE) =c 'YES'`` is the
load-bearing piece — without it, the rule would fire on any
``N PART[LINK] N`` sequence (over-generation: ``bata na
aklat`` "child book"?). The ``¬ (↓3 MEASURE)`` block rejects
chained measures (``*isang dosenang dosenang itlog``).

### Why a new measure-N rule rather than just lex

The GEN-complement form composes via existing rules, but the
LINKER-complement form is more idiomatic for native speakers
of Tagalog. Without the measure-N rule, the LINKER form
either fails to parse or composes via accidentally-permissive
fallbacks (e.g., the parser's robustness path treating
``dosenang`` as _UNK and absorbing it). Adding the targeted
rule makes the parse principled and gives downstream
consumers the right structural / featural information.

### Negative fixtures (per §11.2)

- ``*isang batang aklat`` — bata is a regular NOUN with no
  MEASURE feature; the linker-form measure-N rule's gate
  fails, so no comparator-style composition occurs.
- ``*isang dosenang dosenang itlog`` — chained measure NOUNs
  blocked by ``¬ (↓3 MEASURE)``.

### Out of scope for this commit

- **Hyphenated ``daan-daan`` / ``libu-libo``** orthography —
  needs the same tokenizer pre-pass deferred for Phase 5f
  Commit 14 seasons / Commit 16 ``humigit-kumulang``.
- **Productive ``card_redup`` morph class** for higher-order
  reduplicated multiples (``milyong-milyon`` "millions",
  ``bilyong-bilyon`` "billions") — per plan §11.1 Group H
  item 4: lex per attested form; productive class deferred.
- **MEASURE percolation to the matrix NP** — same NP-from-N
  projection limitation as cardinal-modifier features (Commit
  1). Tests walk down to verify CARDINAL_VALUE + LEMMA on the
  matrix NP plus a parse path with the right measure-N inner
  composition.
- **Other measure NOUNs** (``baso`` "cup" → ``isang basong
  tubig`` "one cup of water", ``piraso`` "piece" → ``isang
  pirasong papel`` "one piece of paper", ``tasa`` "cup",
  etc.) — extending the MEASURE lex inventory is additive
  but not in plan §11.1 Group H scope. Defer.

## Phase 5f Commit 19: distributive ``tig-`` (Group H2 item 5)

**Date:** 2026-05-03. **Status:** active. 10 NUM lex entries.
No new grammar rules. Refs: plan §11.1 Group H item 5
(distributive ``tig-``); S&O 1972 §4.5; R&B 1986; Phase 5f
Commit 1 (cardinal NP-modifier rule consumed unchanged via
the ``(↓2 CARDINAL) =c 'YES'`` constraint); Phase 5f Commit 1
disambiguator branch for ``na`` after NUM[CARDINAL=YES]
(consumed unchanged for consonant-final distributives);
Phase 5f Commit 4 (predicative-cardinal rule absorbs
``Tigisa sila.``).

The plan §11.1 Group H thesis ("the Group A cardinal-NP-
modifier rule generalised to any NUM / Q head") collects its
NUM-side dividends here: the distributive NUMs added in this
commit slot directly into the Phase 5f Commit 1 cardinal
NP-modifier rule because the constraint
``(↓2 CARDINAL) =c 'YES'`` is satisfied. No new rule needed.

### Lex change

Ten NUM entries in ``data/tgl/particles.yaml``, all with
``CARDINAL: "YES"``, ``DISTRIB: "YES"``, ``CARDINAL_VALUE``
matching the base stem (1-10), and ``NUM: PL``:

- tigisa, tigdalawa, tigtatlo, tigapat, tiglima, tiganim,
  tigpito, tigwalo, tigsiyam, tigsampu.

Each entry inherits the cardinal value from its base stem so
the existing cardinal NP-modifier rule consumes it; DISTRIB=
YES additionally marks the daughter NUM for downstream
consumers (LMT, semantics, ranker) that distinguish
distributives from regular cardinals.

The string-quoted ``"YES"`` on both CARDINAL and DISTRIB
follows the recurring-pitfall convention.

### Why CARDINAL=YES on distributives?

A distributive numeral semantically denotes a count, just
distributively (one each, two each, ...). Structurally it
behaves exactly like a cardinal — appearing in NP-modifier,
predicative, and other contexts where cardinals appear. The
existing rules' ``(↓ CARDINAL) =c 'YES'`` constraints all fire
on distributives because the morphological + syntactic
distribution is the same. DISTRIB is the additional feature
that downstream consumers can use to detect "each-ness"
without reanalyzing the structure.

The alternative — making distributives a separate POS or a
NUM[CARDINAL=NO, DISTRIB=YES] — would force every consuming
rule to be extended with a parallel DISTRIB branch. That's
needlessly invasive for what's structurally just a flavour
of cardinal.

### Why per-form lex (not productive ``tig_distrib`` morph class)?

Plan §11.1 Group H item 5 explicitly admits both options:
"Either a new ``tig_distrib`` morph class or per-form lex."
Per-form lex covers the 1-10 range used in S&O 1972 §4.5's
canonical examples; productive class would generate:

- Higher cardinals (``tig-sandaan`` "a hundred each", ``tig-
  sanlibo`` "a thousand each").
- Spanish-borrowed bases (``tig-uno``, ``tig-dos``).
- Compound cardinals (``tig-labindalawa`` "twelve each").

These are all real Tagalog forms but adding them is an
additive scope — productive ``tig_distrib`` is a paradigm-
engine extension, not a grammar / lex extension. Per the
established Phase 5f precedent (compound cardinals in
Commit 3, season ``tag-`` compounds in Commit 14, collective
``card_redup`` in Commit 18), productive paradigm extension
is deferred to a separate paradigm-engine pass when corpus
pressure surfaces a need.

### Hyphenation

The canonical orthography is ``tig-isa``, ``tig-dalawa``,
etc. with an internal hyphen. Same tokenizer issue as Phase
5f Commits 14 / 16 / 18: ``\w+|\S`` splits hyphens. Single-
token forms (``tigisa`` etc.) are the pragmatic precedent.
Canonical hyphenated awaits a tokenizer pre-pass.

### Composition with existing rules

The cardinal NP-modifier rule (Phase 5f Commit 1) fires
unchanged on distributives:

```text
NP[CASE=GEN] → ADP[CASE=GEN] NUM[CARDINAL=YES] PART[LINK] N
```

For ``Bumili ako ng tigisang aklat.``:

- ``ng`` ADP[CASE=GEN]
- ``tigisa`` NUM[CARDINAL=YES, DISTRIB=YES, CV=1]
- ``-ng`` PART[LINK=NG]
- ``aklat`` N
- Output: NP[CASE=GEN, LEMMA=aklat, CV=1] (DISTRIB stays on
  the inner NUM — same NP-from-N projection limitation as
  cardinal-modifier features).

Consonant-final distributives (``tigapat``, ``tiganim``,
``tigsiyam``) use the standalone ``na`` linker; the Phase 5f
Commit 1 disambiguator branch for ``na`` after NUM[CARDINAL=
YES] keeps it as the linker (vs the ALREADY clitic). No new
disambiguator branch needed.

The predicative-cardinal rule (Phase 5f Commit 4) also
absorbs distributives: ``Tigisa sila.`` parses as S with
``PRED='CARDINAL <SUBJ>'``, SUBJ=sila, CV=1.

### Negative fixtures (per §11.2)

- ``*Bumili ako ng tigisa.`` — bare distributive NUM without
  a head N. The cardinal-modifier rule requires a 4-daughter
  RHS (DET/ADP NUM LINK N); without the linker + N daughters,
  the OBJ-NP composition fails.

### Out of scope for this commit

- **Productive ``tig_distrib`` morph class** — see "Why per-
  form lex" above. Defer.
- **Distributive predicate construction** (``Tigisang aklat
  sila`` / ``Tigisa silang aklat`` "they each have one
  book") — verbless predicate with a linker-attached
  complement N. Analytically distinct from the NP-modifier
  composition this commit covers; needs a new S frame rule.
  S&O 1972 §4.5 describes the structure; deferred to a
  later commit.
- **DISTRIB percolation to the matrix NP** — same NP-from-N
  projection limitation as MEASURE / APPROX / COMP. Tests
  walk down to verify CARDINAL_VALUE preservation; DISTRIB
  rides on the inner NUM for downstream consumers.
- **Hyphenated ``tig-isa`` / ``tig-dalawa``** — needs the
  same tokenizer pre-pass deferred for Phase 5f Commits 14
  / 16 / 18.

## Phase 5f Commit 20: universal ``bawat`` / ``kada`` (Group H2 item 6)

**Date:** 2026-05-03. **Status:** active. 2 Q lex entries
\+ 4 new grammar rules + 1 gating addition on the existing
Phase 5b partitive rules. Refs: plan §11.1 Group H item 6
(universal ``bawat``); S&O 1972 §4.7; R&B 1986; Phase 4 §7.8
(existing Q-class infrastructure consumed unchanged for the
``QUANT`` projection); Phase 5b §7.8 follow-on (existing pre-
NP partitive consumed with universal-blocking gate); Phase 5f
Commit 15 (vague-Q-modifier rule consumed as the structural
template for the case-marked variants — same shape minus the
linker daughter).

Closes Group H2 (collective + distributive + universal).

### Lex change

Two Q entries in ``data/tgl/particles.yaml``:

- ``bawat`` — Q[QUANT=EVERY, UNIV="YES"]. Native universal.
- ``kada``  — Q[QUANT=EVERY, UNIV="YES"]. Spanish-borrowed
  colloquial synonym.

Same shape; the analyzer returns each as a single Q analysis
(no polysemy with the verb / paradigm-engine since neither
``bawat`` nor ``kada`` is generated by the paradigm engine).

### Three Q-distributions, now all covered

With this commit, Phase 5f has covered the three syntactic
distributions of Q heads in Tagalog:

<!-- markdownlint-disable MD013 -->
| Distribution | Surface example | Rule | Phase |
| -------------- | ------------------ | ------ | ------- |
| Partitive (Q + GEN-NP) | ``ang lahat ng bata`` "all of the children" | ``NP[CASE=X] → DET/ADP Q NP[CASE=GEN]`` | Phase 5b §7.8 follow-on |
| Vague-Q-modifier (Q + linker + N) | ``ang maraming bata`` "many children" | ``NP[CASE=X] → DET/ADP Q PART[LINK] N`` (gated on VAGUE=YES) | Phase 5f Commit 15 |
| Universal (Q + bare N) | ``ang bawat bata`` "every child" | ``NP[CASE=X] → DET/ADP Q N`` (gated on UNIV=YES) | This commit |
<!-- markdownlint-enable MD013 -->

Each Q lex entry has a feature (no feature for partitive Qs;
VAGUE=YES for vague Qs; UNIV=YES for universals) that gates
its rule. The negative gates ``¬ (↓2 VAGUE)`` and
``¬ (↓2 UNIV)`` on the partitive ensure non-partitive Qs
don't accidentally fire there. The constraining equations
``(↓2 VAGUE) =c 'YES'`` and ``(↓2 UNIV) =c 'YES'`` ensure the
respective rules fire only on their target Qs.

### Grammar change

Four new rules in ``src/tgllfg/cfg/nominal.py`` plus a gate
addition on three existing rules.

**3 case-marked NP rules** (NOM / GEN / DAT):

```text
NP[CASE=X] → DET/ADP[CASE=X] Q N
Equations:
  (↑) = ↓1                          # CASE / MARKER from outer marker
  (↑ PRED) = ↓3 PRED                # head N supplies PRED
  (↑ LEMMA) = ↓3 LEMMA              # ... and LEMMA
  (↑ QUANT) = ↓2 QUANT              # Q's QUANT lifts
  (↑ UNIV) = 'YES'                  # mark NP for downstream consumers
  ¬ (↓3 UNIV)                        # block chained universals
  (↓2 UNIV) =c 'YES'                # gate to UNIV Q heads
```

The output NP carries ``UNIV='YES'`` and ``QUANT=EVERY``
(or whatever the lex sets). Unlike the cardinal NP-modifier
rule (Phase 5f Commit 1), there's no PART[LINK] daughter —
universals take a bare N complement.

**1 bare-NOM rule** (for surfaces where bawat itself functions
as the determiner-equivalent):

```text
NP[CASE=NOM] → Q N
Equations:
  (↑ PRED) = ↓2 PRED
  (↑ LEMMA) = ↓2 LEMMA
  (↑ QUANT) = ↓1 QUANT
  (↑ UNIV) = 'YES'
  (↑ CASE) = 'NOM'
  ¬ (↓2 UNIV)
  (↓1 UNIV) =c 'YES'
```

This rule covers ``Bawat bata ay kumakain.`` style surfaces
where bawat starts the sentence without a preceding ang. The
existing Phase 4 §7.4 ay-inversion rule consumes the
resulting NP as TOPIC.

**Gate addition** to the existing Phase 5b ``Q + NP[GEN]``
partitive rules (3 case variants, all extended): each gains
``¬ (↓2 UNIV)`` parallel to the existing ``¬ (↓2 VAGUE)``
gate (Phase 5f Commit 15). Universals only take the bare-N
form; the partitive ``*ang bawat ng bata`` is non-standard.

### Why no linker between Q and N for universals?

Tagalog's universal quantifiers ``bawat`` and ``kada`` are
phonologically and syntactically distinctive: they precede
the head N directly without an intervening linker (S&O 1972
§4.7 records both as "preposed quantifiers" with bare-N
complements). The vague-Q distribution
(``maraming bata``, ``maraming aklat``) requires the linker;
the universal distribution forbids it. This is the exact
distribution that the new rules' shape captures: same
``DET/ADP Q ... N`` skeleton, no linker daughter.

The plan §11.1 Group H item 6 phrasing — "Pre-N quantifier
with the linker; structurally a Q head. Lex (``bawat``) plus
composition with the Group A NP-modifier rule" — is slightly
inaccurate on the linker point; the canonical surfaces
(``bawat bata``, ``kada bata``) don't include a linker. The
implementation here matches the canonical surfaces.

### Negative fixtures (per §11.2)

- ``*ang bawat kada bata`` — chained universals blocked by
  ``¬ (↓3 UNIV)``.
- ``*ang bawat ng bata`` — universal in GEN-NP partitive
  blocked by the new ``¬ (↓2 UNIV)`` gate on the Phase 5b
  partitive rules.

### Out of scope for this commit

- **``bawat isa`` / ``bawat dalawa``** (Q + NUM as quantifier
  over a number) — needs a parallel Q + NUM rule (mirroring
  the Q + N rule but with NUM as the daughter category).
  Additive but not in this commit's scope.
- **Q-quantification over a non-N head** (``bawat sa
  kanila`` "every of them" with a DAT-NP complement) —
  structurally distinct (Q + DAT-NP); deferred.
- **Floated universals** — the existing Phase 4 §7.8
  ``S → S Q`` float rule mechanically fires on UNIV Qs but
  the result isn't natural Tagalog (``Kumakain ang bata
  bawat`` is non-standard). Not explicitly tested or
  documented as supported.

## Phase 5f Commit 21: distributive-possessive ``kani-kaniya`` / ``kanya-kanya`` (Group H3 item 7)

**Date:** 2026-05-04. **Status:** active. 2 Q lex entries +
7 new grammar rules + 1 gating addition on the existing
Phase 5b partitive rules. Refs: plan §11.1 Group H item 7
(distributive-possessive); S&O 1972 §6.13; R&B 1986; Phase 5f
Commit 15 (vague-Q-modifier rule consumed as the structural
template); Phase 5f Commit 20 (universal Q rule's bare-NOM
companion consumed as a structural template); existing PRON-
poss machinery referenced by the plan but not directly
consumed (the construction is Q-based not PRON-based).

Opens Group H3 (the final Phase 5f sub-PR).

### Lex change

Two Q entries in ``data/tgl/particles.yaml``:

- ``kanikaniya`` — Q[QUANT=EACH_OWN, DISTRIB_POSS="YES"].
  Reduplication of ``kaniya`` (alternate form of ``kanya``);
  the i-vowel reflects the reduplication pattern.
- ``kanyakanya`` — Q[QUANT=EACH_OWN, DISTRIB_POSS="YES"]. Full
  reduplication of ``kanya``.

Both forms are functionally equivalent. The two orthographic
variants are both attested in standard Tagalog (R&B 1986).

### Why Q (not PRON)?

The plan §11.1 Group H item 7 describes these as "reduplicated
possessive pronoun with distributive force ... Composes from
existing PRON-poss machinery + the linker." The plan's PRON
framing reflects the morphological etymology (reduplication of
``kanya`` "his/her" / ``kaniya``) — but the syntactic
distribution is Q-like:

- Pre-N quantifier slot (between case-marker and head N).
- Linker required between Q and N.
- Cannot postpose like a possessor (``aklat ko`` "my book"
  works; ``*aklat kanyakanya`` doesn't).
- Can stand alone in NOM with no DET (parallel to ``bawat
  bata``).

The existing PRON-poss machinery is the postposed-possessor
rule (``NP → NP NP[CASE=GEN]``) which fires on a GEN-NP
attaching to an existing NP. The distributive-possessive
construction is the inverse — preposed Q + linker + N. So
the plan's "PRON-poss machinery" reuse is structural in
spirit (the f-structure puts the reduplicated form in a
possessor-like role) but the rule shape is Q-modifier-like.

Implementation choice: treat as Q[DISTRIB_POSS=YES]. The
``DISTRIB_POSS`` feature distinguishes this Q-distribution
from the four already covered (partitive / vague-modifier /
universal / bare-NOM-universal):

| Distribution | Lex feature | Rule | Phase |
| -------------- | -------------- | ------ | ------- |
| Partitive | (none) | ``DET/ADP Q NP[GEN]`` | Phase 5b |
| Vague-modifier | VAGUE=YES | ``DET/ADP Q LINK N`` | Phase 5f Commit 15 |
| Universal | UNIV=YES | ``DET/ADP Q N`` | Phase 5f Commit 20 |
| Bare-NOM universal | UNIV=YES | ``Q N`` | Phase 5f Commit 20 |
| Distributive-possessive | DISTRIB_POSS=YES | ``DET/ADP Q LINK N`` | This commit |
| Bare-NOM distrib-poss | DISTRIB_POSS=YES | ``Q LINK N`` | This commit |

The new distributive-possessive rule shape coincides with the
vague-Q-modifier rule shape (both ``DET/ADP Q LINK N``) but
with different gating constraints. Two parallel rules with
different gates rather than one disjunctive rule.

### Hyphenation

Canonical orthography is ``kani-kaniya`` and ``kanya-kanya``.
Same tokenizer issue as Commits 14 / 16 / 18 / 19: ``\w+|\S``
splits hyphens. Single-token forms (``kanikaniya``,
``kanyakanya``) are the established precedent. Canonical
hyphenated awaits a tokenizer pre-pass.

### Grammar change

Six case-marked NP rules in ``src/tgllfg/cfg/nominal.py`` (3
cases × 2 linker variants):

```text
NP[CASE=X] → DET/ADP[CASE=X] Q PART[LINK=NA|NG] N
Equations:
  (↑) = ↓1                            # CASE / MARKER from outer marker
  (↑ PRED) = ↓4 PRED                  # head N supplies PRED
  (↑ LEMMA) = ↓4 LEMMA
  (↑ QUANT) = ↓2 QUANT                # Q's QUANT lifts (= 'EACH_OWN')
  (↑ DISTRIB_POSS) = 'YES'            # mark NP for downstream consumers
  ¬ (↓4 DISTRIB_POSS)                 # block chained
  (↓2 DISTRIB_POSS) =c 'YES'          # gate to DISTRIB_POSS Q heads
```

Plus 2 bare-NOM rules (NA / NG linker variants) for surfaces
where the distributive-possessive Q functions as the
determiner-equivalent (``Kanyakanyang aklat ay binili
nila.``):

```text
NP[CASE=NOM] → Q PART[LINK=NA|NG] N
Equations:
  (↑ PRED) = ↓3 PRED
  (↑ LEMMA) = ↓3 LEMMA
  (↑ QUANT) = ↓1 QUANT
  (↑ DISTRIB_POSS) = 'YES'
  (↑ CASE) = 'NOM'
  ¬ (↓3 DISTRIB_POSS)
  (↓1 DISTRIB_POSS) =c 'YES'
```

Gate addition on existing Phase 5b ``Q + NP[GEN]`` partitive
rules (3 case variants): each gains ``¬ (↓2 DISTRIB_POSS)``
(parallel to the existing ``¬ (↓2 VAGUE)`` and
``¬ (↓2 UNIV)`` gates from Commits 15 + 20).

### Negative fixtures (per §11.2)

- ``*kanikaniyang kanyakanyang aklat`` — chained
  distributive-possessives blocked by ``¬ (↓4 DISTRIB_POSS)``.
- ``*ng kanyakanya ng aklat`` — DISTRIB_POSS in GEN-NP
  partitive blocked by the new ``¬ (↓2 DISTRIB_POSS)`` gate.

### Out of scope for this commit

- **Standalone use** (``Kanya-kanya na lang.`` "It's each
  one's own now.") — idiomatic; needs separate handling.
- **Productive reduplication of arbitrary pronouns**
  (``akin-akin``, ``inyo-inyo``) — restricted in standard
  Tagalog to 3rd-person; per-form lex sufficient.
- **Generic preposed-possessor construction**
  (``kanyang aklat`` "his/her book", ``aking aklat`` "my
  book") — additive but structurally distinct (PRON[CASE=DAT]
  \+ LINK + N rather than Q + LINK + N). Worth a separate
  commit; defer.
- **Hyphenated ``kani-kaniya`` / ``kanya-kanya``** —
  needs the same tokenizer pre-pass deferred for Commits 14
  / 16 / 18 / 19.

## Phase 5f Commit 22: wholes ``buo`` / ``buong`` (Group H3 item 8)

**Date:** 2026-05-04. **Status:** active. 1 Q lex entry + 8
new grammar rules + 1 gating addition on the existing Phase
5b partitive rules. Refs: plan §11.1 Group H item 8 (wholes);
S&O 1972 §4.7; R&B 1986; Phase 5f Commit 15 (vague-Q-modifier
rule consumed as the structural template); Phase 5f Commit 21
(distributive-possessive bare-NOM rule consumed as a
structural template); Phase 4 split_linker_ng (consumed
unchanged for the bound ``-ng`` form).

### Lex change

One Q entry in ``data/tgl/particles.yaml``:

- ``buo`` — Q[QUANT=WHOLE, WHOLE="YES"]. Citation form,
  vowel-final. The bound ``-ng`` linker form ``buong`` is
  produced by the existing split_linker_ng pre-pass once
  ``buo`` is a known surface in the morph index.

### POS choice: Q rather than ADJ

The plan §11.1 Group H item 8 description — "Pre-N modifier
with linker (``buo`` + ``-ng``); lex (``buo``) plus the
Group A rule" — doesn't specify the POS. Two options:

1. **ADJ**: ``buo`` is an adjective ("whole, entire") that
   modifies a head N via the linker. This would feed an
   adjective-modifier rule (which doesn't yet exist; it
   lands with Phase 5g).
2. **Q**: ``buo`` is a totality quantifier (quantifies over
   the entirety of the entity, not a property like color or
   size). Plan groups it under Group H quantifiers.
   Linker-modifier distribution matches the established Q
   template (Commits 15 / 20 / 21).

This commit chose option 2 (Q). Rationale:

- Semantic role is totality quantification, not property
  attribution. ``buo`` doesn't gradate (``*mas buo`` "more
  whole" is non-canonical) — adjectives typically gradate.
- Plan groups it under Group H, alongside other quantifiers
  (universals, vague, distributives).
- The linker-modifier rule template is already established
  for Q heads (Commits 15 / 20 / 21).
- Predicate-Adj path doesn't exist yet (Phase 5g). Adding
  ``buo`` as ADJ now would require either deferring lex+rule
  to Phase 5g, or adding ad-hoc machinery here.

A future Phase 5g may revisit the Q-vs-ADJ classification of
``buo`` (and similar totality quantifiers like ``ilang``
"some / a few" — already added as Q[VAGUE=YES] in Commit 15)
once the adjective infrastructure exists. For Phase 5f scope,
Q is the cleanest choice.

### Grammar change

Six case-marked NP rules in ``src/tgllfg/cfg/nominal.py`` (3
cases × 2 linker variants):

```text
NP[CASE=X] → DET/ADP[CASE=X] Q PART[LINK=NA|NG] N
Equations:
  (↑) = ↓1
  (↑ PRED) = ↓4 PRED
  (↑ LEMMA) = ↓4 LEMMA
  (↑ QUANT) = ↓2 QUANT
  (↑ WHOLE) = 'YES'
  ¬ (↓4 WHOLE)
  (↓2 WHOLE) =c 'YES'
```

Two bare-NOM rules (NA / NG variants) for surfaces where
``buo`` functions as the determiner-equivalent
(``Buong pamilya ay kumakain.``):

```text
NP[CASE=NOM] → Q PART[LINK=NA|NG] N
Equations:
  (↑ PRED) = ↓3 PRED
  (↑ LEMMA) = ↓3 LEMMA
  (↑ QUANT) = ↓1 QUANT
  (↑ WHOLE) = 'YES'
  (↑ CASE) = 'NOM'
  ¬ (↓3 WHOLE)
  (↓1 WHOLE) =c 'YES'
```

Gate addition: each of the 3 existing Phase 5b ``Q +
NP[GEN]`` partitive rules gains ``¬ (↓2 WHOLE)``. Wholes
only take the linker-N form; ``*ang buo ng bata`` is non-
standard.

The NA linker variant of the new rules is included for
symmetry — ``buo`` is vowel-final so only NG fires in
practice. If a future consonant-final WHOLE entry is added
(unlikely; ``buo`` is the only canonical form), the NA
variant is ready.

### Negative fixtures (per §11.2)

- ``*ang buong buong bata`` — chained wholes blocked by
  ``¬ (↓4 WHOLE)``.
- ``*ang buo ng bata`` — WHOLE in GEN-NP partitive blocked
  by the new ``¬ (↓2 WHOLE)`` gate.

### Out of scope for this commit

- **Predicative use** (``Buo ang bata.`` "The child is
  whole / intact") — would parse via a future predicate-Q
  rule. Defer.
- **Floated ``buo``** (``Kumain ang bata buo``) —
  mechanically fires via the existing Phase 4 §7.8 ``S → S
  Q`` float rule but not idiomatic for ``buo``. Not
  explicitly tested.
- **ADJ-vs-Q reanalysis** — Phase 5g may revisit the
  classification once adjective infrastructure exists.

## Phase 5f Commit 23: dual ``pareho`` / ``kapwa`` (Group H3 item 9; closes Phase 5f)

**Date:** 2026-05-04. **Status:** active. 2 Q lex entries.
NO new grammar rules — both consume the existing Phase 4
§7.8 ``S → S Q`` float rule unchanged. 1 gating addition on
the existing Phase 5b partitive rules. Refs: plan §11.1
Group H item 9 (dual); S&O 1972 §4.7; R&B 1986; Phase 4 §7.8
(existing float rule consumed unchanged); Phase 5b §7.8
follow-on (existing partitive consumed with new dual-blocking
gate).

Closes **Phase 5f**.

### Lex change

Two Q entries in ``data/tgl/particles.yaml``:

- ``pareho`` — Q[QUANT=BOTH, DUAL="YES"]. Native dual.
- ``kapwa``  — Q[QUANT=BOTH, DUAL="YES"]. Formal dual.

### Polysemy with future Phase 5h equative-predicate reading

``pareho`` also has an equative-predicate reading
(``Pareho ang kanilang sapatos.`` "their shoes are the same"),
which belongs in Phase 5h (gradable / equative comparison)
per the plan §11.1 Group H item 9. This commit covers only
the floated-quantifier reading. Following the Phase 5f Commit
17 bababa / hihigit precedent, the equative reading will be
added as a separate ``(lemma, pos)`` entry when Phase 5h
lands — the morph analyzer's different-POS handling supports
the polysemy without collision.

### Float rule consumes unchanged

The existing Phase 4 §7.8 ``S → S Q`` rule:

```text
S → S Q
Equations:
  (↑) = ↓1
  ↓2 ∈ (↑ ADJ)
  (↓2 ANTECEDENT) = (↑ SUBJ)
```

attaches Q at clause-final position as a member of the
matrix's ADJ set with binding to SUBJ. With pareho / kapwa as
Q, the rule fires on:

- ``Kumain sila pareho.`` → ADJ contains pareho
  f-structure (LEMMA, QUANT=BOTH, DUAL=YES); ANTECEDENT →
  matrix SUBJ (sila).
- ``Kumain ang bata kapwa.`` → similar shape.

The matrix's ADJ-member carries the full Q lex f-structure
including DUAL=YES, so downstream consumers (LMT, semantics)
can detect the dual marking via the standard ADJ traversal.

### Gate addition on partitive

Each of the 3 existing Phase 5b ``Q + NP[GEN]`` partitive
rules gains ``¬ (↓2 DUAL)`` (parallel to existing VAGUE /
UNIV / DISTRIB_POSS / WHOLE gates). Duals only float; the
partitive ``*ang pareho ng bata`` is non-standard.

With this commit, the partitive rule has 5 negative gates
(VAGUE / UNIV / DISTRIB_POSS / WHOLE / DUAL). All five are
the canonical Q-feature flavours added in Phase 5f.

### Why no rule for the clause-initial form?

The plan §11.1 Group H item 9 canonical example is ``Pareho
silang kumain.`` "they both ate" — Q clause-initial with
PRON-clitic + linker + V. This surface is structurally
distinct from the float construction and would require a new
S frame rule. Possible structures:

```text
S → Q[DUAL=YES] PRON[NOM] PART[LINK] V
  (↑ PRED) = 'DUAL <SUBJ>'
  (↑ SUBJ) = ↓2
  (↑ DUAL) = 'YES'
  (↑ XCOMP) = ↓4
  (↓4 SUBJ) = (↑ SUBJ)   # control
```

— pareho as predicate-Q with linker-attached XCOMP. But this
is analytically more involved than the float consumption, and
the same proposition is expressed by the clause-final float
form (``Kumain sila pareho.``) which already parses. For
Phase 5f scope, that's adequate. Deferred.

### Negative fixtures (per §11.2)

- ``*ang pareho ng aklat`` — DUAL in GEN-NP partitive
  blocked by new ``¬ (↓2 DUAL)`` gate.
- ``*ang kapwa ng aklat`` — same blocking.

### Out of scope for this commit

- **Clause-initial form** (``Pareho silang kumain.``) — see
  "Why no rule" above.
- **Equative predicate** of ``pareho`` (``Pareho ang
  kanilang sapatos.``) — Phase 5h scope.
- **Number agreement** with the SUBJ — semantically a dual Q
  requires a plural antecedent (``*Kumain siya pareho.`` is
  semantically odd). The float rule's ``ANTECEDENT`` binding
  sets up the link but no agreement check is performed.
  Adding agreement is a follow-on; out of scope for this
  commit.

### Phase 5f close

This commit completes the Phase 5f §11.1 deliverables:

<!-- markdownlint-disable MD013 -->
| Group | Items | Phase 5f Commits | Status |
| ------- | ------- | ------------------- | -------- |
| A | Cardinals (native, Spanish, compound, predicative, multiplicative, decimals/percentages) | 1-6 | merged in PR #12 |
| B | Ordinals 1-10 | 7 | merged in PR #13 |
| C | Fractions | 8 | merged in PR #13 |
| D | Arithmetic predicates | 9 | merged in PR #14 |
| E | Times (clock + time-of-day + deictics + minute composition + mga approximation) | 10-13 | merged in PR #15 |
| F | Dates (months + days + date formula) | 13 | merged in PR #15 |
| G | Seasons | 14 | merged in PR #15 |
| H1 | Vague + approximators + numeric comparatives | 15-17 | merged in PR #16 |
| H2 | Collective + distributive ``tig-`` + universal ``bawat``/``kada`` | 18-20 | merged in PR #17 |
| H3 | Distributive-possessive + wholes + dual | 21-23 | this PR |
<!-- markdownlint-enable MD013 -->

Phase 5f total: ~23 commits across 9 PRs (including the prep
PR #11). Test count: ~3653 (start of 5f) → ~4337 (end of 5f),
+684 unit + parametrized tests. Coverage corpus:
~1085 → ~1212 sentences, 99.5% parse rate maintained
throughout. Next: Phase 5g (gradable adjectives + comparison
\+ degree, plan §12). Per the effort protocol, the cutover
will need a deliberate pause-and-verify before starting.

## Phase 5g Commit 1: ADJ analyzer dispatch + productive ma- derivation

**Date:** 2026-05-05. **Status:** active. New ``AdjectiveCell``
schema, new ``data/tgl/adjectives.yaml`` + ``adj_paradigms.yaml``,
analyzer ``ADJ`` branch + ``_index.adjectives`` table. Refs:
plan §12.1 (analytical commitment); R&G 1981 §12.9
(integration benchmark anchors); S&O 1972 §5; Kroeger 1993 ch. 4.

Opens **Phase 5g** (adjectival modification, plan §12.1).
Adds the analyzer-layer scaffolding for the analytical
commitment that ``ma-`` adjectives are ``POS=ADJ`` with
intrinsic ``[PREDICATIVE+]``, NOT stative VERBs. Grammar-rule
layer follows in Commits 2 / 3 / 5 / 6.

### Schema additions

``src/tgllfg/morph/paradigms.py`` — new ``AdjectiveCell``
dataclass parallel to ``ParadigmCell`` but without
voice / aspect / mood fields. ``MorphData`` gains an
``adjective_cells`` field. (Refactored later this PR into a
proper ``ParadigmCell`` base + ``VerbalCell`` / ``AdjectiveCell``
subclasses — see the next entry.)

``src/tgllfg/morph/loader.py`` — loads ``adjectives.yaml`` into
``MorphData.roots`` (appended after verbs / nouns) and
``adj_paradigms.yaml`` into ``MorphData.adjective_cells``.

``src/tgllfg/morph/analyzer.py`` — ``_Index.adjectives`` table;
``_index_adjective_paradigms(root)`` walks every matching
adjective cell and indexes the generated surface;
``analyze_one`` consults ``_index.adjectives`` between
verb_forms and nouns; ``is_known_surface`` includes the new
table.

### Productive ma- paradigm

``data/tgl/adj_paradigms.yaml`` — single seed cell:

```text
affix_class: ma_adj
operations: [{op: prefix, value: "ma"}]
```

Phase 5h is expected to add ``pinaka-`` superlative,
``napaka-`` intensifier, and ``kasing-`` / ``sing-`` equative
cells using this same dataclass.

The ``ma_adj`` affix class is intentionally distinct from the
verbal ``ma`` affix class — the verbal ``ma-`` non-volitional /
stative paradigm produces ``na-`` (PFV: ``naganda``),
``na-CV-`` (IPFV: ``nagaganda``), ``ma-CV-`` (CTPL:
``magaganda``) but NEVER the bare ``ma + root`` surface that
adjectives use. The two paradigms are non-overlapping,
mirroring the analytical commitment that ``ma-`` adjectives
lack the verbal paradigm.

### Lex inventory (seed)

``data/tgl/adjectives.yaml`` — 6 ADJ roots: ``ganda``,
``talino``, ``tanda``, ``liit``, ``taas``, ``bilis``. Three
of these (``tanda``, ``talino``, ``liit``) are entirely new
lemmas; the other three coexist with their existing VERB
entries in ``verbs.yaml`` — Phase 5g's additive policy doesn't
touch the verbal entries.

### Lemma policy

Lemma is the bare root (``maganda`` → lemma ``ganda``),
paralleling the verbal convention. The bare root surface
itself is intentionally NOT indexed as ADJ — bare ``ganda`` is
a noun ("beauty") and the productive paradigm produces the
adjectival surface.

## Phase 5g refactor: ParadigmCell base class extracted

**Date:** 2026-05-05. **Status:** active. Refactor only — no
new linguistic content. Refs: Phase 5g Commit 1 (introduced
the union); type-system clean-up.

The Commit 1 ``generate_form`` signature used a
``ParadigmCell | AdjectiveCell`` union. The refactor replaces
the union with a proper class hierarchy:

- ``ParadigmCell`` — common base with the four shared fields
  (``affix_class``, ``operations``, ``notes``, ``feats``).
- ``VerbalCell(ParadigmCell)`` — adds voice / aspect / mood /
  transitivity. Voice / aspect default to empty strings to
  satisfy the dataclass-inheritance rule (non-default fields
  can't follow default ones); the YAML loader's ``_require``
  enforces non-empty at parse time.
- ``AdjectiveCell(ParadigmCell)`` — empty subclass; Phase 5g
  needs nothing beyond the base, though Phase 5h's ``napaka-``
  / ``pinaka-`` cells may add fields.

``MorphData.paradigm_cells`` retyped ``list[VerbalCell]``.
Construction sites updated: ``morph/loader.py``,
``lex/adapter.py``, ``tests/test_morph.py``.

## Phase 5g Commit 2: NP-internal ADJ modifier rules + na disambiguator

**Date:** 2026-05-05. **Status:** active. 4 N-level
modifier rules + ``disambiguate_homophone_clitics`` extension.
Refs: plan §12.1; Phase 5e Commit 16 (pre-modifier dem
chain expectation); Phase 4 §7.5 (the linker f-attribute
namespace).

### Grammar rules

Four N-level rules in ``cfg/nominal.py``:

```text
N → ADJ PART[LINK=NA] N      (pre-N, consonant-final adj)
N → ADJ PART[LINK=NG] N      (pre-N, vowel-final adj)
N → N PART[LINK=NA] ADJ      (post-N, consonant-final N)
N → N PART[LINK=NG] ADJ      (post-N, vowel-final N)
```

Each writes the adjective lex daughter to the matrix N's
``ADJ-MOD`` set via ``↓ ∈ (↑ ADJ-MOD)``; the matrix shares
structure with the head N via ``(↑) = ↓3`` (pre-N) or
``(↑) = ↓1`` (post-N). The N-level scope lets the existing
NP-from-N projection case-mark adj-modified Ns freely without
per-case rule explosion.

Multi-modifier composition (``mabilis na magandang bata``)
falls out of right-recursion in the pre-N rules — the
rightmost daughter is N, and an adj-modified N is itself N.

### Why ``ADJ-MOD`` rather than ``ADJ``

This codebase uses the f-attribute ``ADJ`` for clausal
adjuncts (adverbial 2P clitics in ``cfg/clitic.py``,
sentential PP / AdvP fronting in ``cfg/extraction.py``) and
as the host slot for relative clauses on NPs. Lifting the
head N's adjunct set to the matrix NP via
``(↑ ADJ) = ↓2 ADJ`` would pre-create an empty AVM on every
NP whose head N has no modifier (the unifier's
``resolve_path`` defaults to ``ComplexValue``); subsequent
``↓ ∈ (↑ ADJ)`` set-adds (e.g., from the RC wrap rule) then
clash at ``add_to_set`` (FStructure-vs-set type mismatch).

Using a Phase-5g-specific attribute name (``ADJ-MOD``)
sidesteps the clash because no other rule writes to it. The
category ``ADJ`` in the rule's RHS is the lex preterminal POS,
entirely separate from the f-attribute namespace.

### NP-level visibility deferred

The current commit leaves the modifier on the head N's
f-structure but does not propagate it to the matrix NP.
Tests verify rule firing via c-tree shape rather than
f-structure inspection. NP-level lift is filed for a future
commit — the clean fix is for the NP rule to share f-structure
with N (``(↑) = ↓2`` plus explicit DET feature lifts), a
substantial refactor with broad blast radius.

### Disambiguator extension (clitics/placement.py)

Added an ADJ + ``na`` + (NOUN | N | ADJ) right-context branch
to ``disambiguate_homophone_clitics`` selecting the linker
reading. The right-context check distinguishes NP-modifier
contexts (next content is NOUN / N / ADJ) from
predicative-adj clauses (``Maganda na ka`` /
``Maganda na ang bata`` — next content is PRON / DET, those
keep both readings and the placement pass treats ``na`` as
the ALREADY clitic).

Vowel-final adjectives take the bound ``-ng`` linker (no
clitic homophone), so this branch matters only for
consonant-final adjectives.

## Phase 5g Commit 3: predicative adjective clause

**Date:** 2026-05-05. **Status:** active. 1 new clausal rule.
Refs: plan §12.1 analytical commitment; Phase 5e Commit 26
(``parang`` comparative — structural template); Phase 5f
Commit 4 (predicative cardinal — same literal-PRED
convention).

```text
S → ADJ[PREDICATIVE=YES] NP[CASE=NOM]
    (↑ PRED) = 'ADJ <SUBJ>'
    (↑ SUBJ) = ↓2
    (↑ ADJ_LEMMA) = ↓1 LEMMA
    (↑ PREDICATIVE) = 'YES'
    (↓1 PREDICATIVE) =c 'YES'
```

The verbless adj-pred clause that delivers Phase 5g's
user-facing payload — surfaces like ``Maganda ang bata.``
"The child is beautiful." (previously zero parses) now have a
complete sentence parse.

The PRED template ``ADJ <SUBJ>`` parallels other predicative
rules' literal-PRED convention (``CARDINAL <SUBJ>`` for
predicative cardinals, ``LIKE <SUBJ, OBJ>`` for parang). The
adjective's identity is preserved on the matrix S via
``ADJ_LEMMA`` (a Phase-5g-specific attribute name to avoid
overloading plain ``LEMMA`` on a clausal f-structure).
``PREDICATIVE`` is also lifted to the matrix as a clause-type
marker.

The constraining equation ``(↓1 PREDICATIVE) =c 'YES'`` is
belt-and-braces — the rule's RHS already filters on
``ADJ[PREDICATIVE=YES]`` at the category-pattern level — but
makes the analytical commitment explicit and guards against
future lex entries with PREDICATIVE=NO (modifier-only
adjectives, if introduced later).

Composes cleanly with the existing negation rule
(``Hindi maganda ang bata.``), the aspectual ``na`` ALREADY
clitic (``Maganda na ang bata.`` / ``Matanda na siya.``), and
the existing ``NP[CASE=NOM] → PRON[CASE=NOM]`` projection
(``Maganda ka.``, ``Matanda siya.``).

R&G 1981 §12.9 integration benchmark — Phase 5g unblocks 4 of
the 7 simple sentences in roadmap §12.9's "Ang Manok"
benchmark: ``Matanda siya``, ``Maliit ang bahay``, ``Mataas
ang bundok``, plus a modifier-form fixture (``Tumakbo ang
lalaking matanda`` substitutes for OOV ``mamang matanda``).

Out of scope for Phase 5g (deferred):

- **ay-inversion of adj-pred** (``Ang bata ay maganda.``):
  Phase 4 §7.4 ay-fronting was built for V pivots; extending
  to ADJ pivots is a separate commit.
- **Multi-modifier predicate** (``Mabilis at maganda ang
  bata.``): needs Phase 5k coordination.
- **Comparison / intensification** (``Mas maganda ...`` etc.):
  Phase 5h.

## Phase 5g Commit 4: lex inventory expansion to 30 adjectives

**Date:** 2026-05-05. **Status:** active. Lex-only — 24 new
ADJ entries. Refs: plan §12.1 (~30-50 inventory target).

Expanded ``data/tgl/adjectives.yaml`` from 6 (Commit 1) to 30
entries spanning four dimensions:

- **Size** (9): ``laki``, ``liit``, ``taas``, ``baba``,
  ``haba``, ``ikli``, ``lapad``, ``kapal``, ``nipis``.
- **Quality** (11): ``ganda``, ``talino``, ``tanda``, ``bilis``,
  ``bait``, ``sipag``, ``tamad``, ``tapang``, ``lakas``,
  ``hina``, ``linis``.
- **Sensory** (6): ``init``, ``lamig``, ``sarap``, ``ingay``,
  ``bango``, ``baho``.
- **Evaluative** (4): ``saya``, ``lungkot``, ``yaman``,
  ``hirap``.

Eight roots also exist in ``verbs.yaml`` as INTR "be X"
stative verbs or as TR / INTR verbs with a distinct sense
(``baba`` "go down, descend"; ``linis`` "clean (TR)"). The
Phase 5g additive policy leaves verbs.yaml untouched — the
ADJ entries produce the bare ``ma + root`` surface that the
verbal NVOL paradigm doesn't generate (verbal NVOL ``ma``
cells always reduplicate or use ``na-`` prefix).

Colour deferred — common Tagalog colour terms (``puti``,
``itim``, ``pula``, ``dilaw``) are bare adjectives that
don't take ``ma-`` morphology; they need a separate paradigm
or a non-paradigmatic ADJ-class entry, lands separately
(Phase 5h with intensifiers, where ``napaka-`` derivations of
colour terms appear).

## Phase 5g Commit 5: manner-adverb (S-level adjective adjunct)

**Date:** 2026-05-05. **Status:** active. 2 new clausal rules
\+ disambiguator extension to VERB right-context. Refs: plan
§12.1 ("the same lex / linker machinery covers it").

```text
S → ADJ PART[LINK=NA] S
S → ADJ PART[LINK=NG] S
    (↑) = ↓3
    ↓1 ∈ (↑ ADJ)
```

The matrix S shares its f-structure with the inner verbal S,
so VOICE / ASPECT / MOOD / SUBJ / OBJ all percolate to the
matrix; the adjective lex daughter is added to the matrix's
ADJ adjunct set — the same slot that hosts 2P clitic adjuncts
and sentential PP / AdvP fronting.

### Why S-level rather than V-level

The roadmap-natural shape would be ``V → ADJ PART V`` — modify
the verb directly. But ``V`` is currently a lex preterminal:
tokens with ``pos: VERB`` match SCAN against the ``V`` slot in
V-headed clausal frames. Per ``compile.py``, "Categories that
ever appear as a rule LHS are non-terminals; everything else
is a lex preterminal during SCAN." Adding a ``V`` LHS would
promote V to non-terminal and break SCAN for every existing
V-headed rule. The S-level attachment is semantically
equivalent (manner adverbs scope over the verbal proposition;
LFG conventionally permits S-level attachment for adjuncts)
and avoids the preterminal-vs-non-terminal collision.

### Disambiguator extension

The Commit 2 ADJ + ``na`` + content-word linker branch
extended its right-context whitelist to also include VERB.
Helper renamed: ``_next_content_is_n_or_adj`` →
``_next_content_is_n_adj_or_v``. Without the extension, the
placement pass would hoist ``na`` to clause-end as the ALREADY
2P clitic and the manner-adverb composition (``Mabilis na
tumakbo siya.``) would fail.

## Phase 5g Commit 6: dem × adj-modified-N composition + disambiguator extension

**Date:** 2026-05-05. **Status:** active. NO new grammar
rules — empirical verification that the existing dem rules
chain through Phase 5g adj-modifiers. Disambiguator
right-context whitelist extended to DEM-DET. Refs: Phase 5e
Commit 16 (pre-modifier dem); Phase 5d Commit 3 (post-modifier
dem); plan §12.1.

The Phase 5e Commit 16 pre-modifier dem rules
(``NP → DET[DEM=YES] PART[LINK] N``) and the Phase 5d Commit 3
post-modifier dem rules (``NP → NP PART[LINK] DET[DEM=YES]``)
both took bare N (or bare NP) at their head slot. The
Phase 5g Commit 2 modifier rules are right-recursive — an
adj-modified N is itself N — so the dem rules chain through
adj modifiers unchanged. Verified empirically.

### Disambiguator extension

The one disambiguator gap that surfaced: post-modifier dem
on a consonant-final adj head (``ang batang mabait na ito``
"this kind child") has right-context DEM-DET, which the
Commit 5 whitelist (NOUN / N / ADJ / VERB) didn't cover. The
helper was renamed and extended to also admit DET / ADP with
``DEM=YES``:

``_adj_na_right_context_is_linker_target`` — admits NOUN / N
/ ADJ / VERB / DEM-DET. Plain DET (DEM=NO) right contexts
continue to fall through, preserving the predicative-adj
clause's ALREADY-clitic reading.

## Phase 5h Commit 1: pinaka- superlative + napaka- intensive cells

**Date:** 2026-05-05. **Status:** active. Two new cells in
``data/tgl/adj_paradigms.yaml``; no grammar / analyzer code
changes. Refs: plan §4.3, §6 Commit 1.

The Phase 5g ``AdjectiveCell`` schema accepts both new cells
unchanged. Each opts into the same ``affix_class: ma_adj`` filter
as the Phase 5g bare-``ma-`` cell, so every ``ma_adj``-declaring
ADJ root unlocks both new derivations without per-root edits.
Operation-order matters for ``pinaka-``: prefix ``ma`` first,
then prefix ``pinaka``, so the surface is ``pinakamaganda`` (not
``*pinakaganda``). ``napaka-`` attaches to the bare root directly
(``napakaganda``).

Per-cell ``feats`` ride into every generated MorphAnalysis via
the analyzer's existing ``setdefault`` merge: pinaka- surfaces
carry ``COMP_DEGREE: SUPERLATIVE``; napaka- surfaces carry
``COMP_DEGREE: INTENSIVE`` plus a redundant ``INTENSIFIER: YES``
flag for downstream consumers to branch on.

### `core/__init__.py` circular-import fix (folded in)

The PR #23 refactor's ``core/__init__.py`` re-exported the
pipeline submodule, creating a circular import on the morph-first
import path (``from tgllfg.morph import Analyzer`` triggered
``core/__init__.py`` which loaded pipeline which loaded morph
which was mid-init). pytest's collection ordering happened to
avoid it, but bare ``python -c "from tgllfg.morph import X"``
raised ImportError. Dropping the unused pipeline re-export from
``core/__init__.py`` closes the cycle without changing any caller
(the rewrite in PR #23 produced explicit
``from tgllfg.core.pipeline import parse_text`` everywhere).

## Phase 5h Commit 2: kasing-/sing- equative cells + bare-citation indexer + equative-identity lex entries

**Date:** 2026-05-05. **Status:** active. Three pieces, all
additive. Refs: plan §4.2, §4.3, §6 Commit 2.

Two productive cells (``kasing-``, ``sing-`` equative) plus
three lexicalised bare-surface ADJ entries (``pareho``,
``magkapareho``, ``magkaiba``) require an analyzer split: ADJ
roots with non-empty ``affix_class`` go through the existing
``_index_adjective_paradigms`` (productive cells only); roots
with ``affix_class: []`` go through a new
``_index_adjective_bare_root`` that indexes the citation
directly with the root's per-root ``feats``.

### Why a Python-side split rather than a YAML "bare cell"

The legacy ``_affix_class_match`` treats an empty cell's
``affix_class`` as a wildcard ("fires on any root" — preserved
for the pre-affix-class-existed AV/OV/DV/IV paradigms). A YAML
"bare cell" with ``affix_class: ""`` would inappropriately fire
on every root, including the productive ``ma_adj`` family,
generating bare-root surfaces for ``ganda`` / ``talino`` etc. and
breaking the Phase 5g lemma policy (bare roots NOT indexed as
ADJ). The Python-side dispatch on ``r.affix_class`` keeps the
two paths clean.

### `pareho` polysemy

``pareho`` already had a ``Q[QUANT=BOTH, DUAL=YES]`` analysis in
``particles.yaml`` (Phase 5f Commit 23 floated-quantifier reading).
The new ``adjectives.yaml`` entry adds an
``ADJ[PREDICATIVE=YES, EQUATIVE=YES, COMP_DEGREE=EQUATIVE]``
analysis. The analyzer indexes both readings against the same
surface; rule context disambiguates: float-Q
(``Kumain sila pareho``) fires the Phase 4 §7.8 ``S → S Q``
rule; predicative-equative (``Pareho ang aklat``) fires the
Phase 5g predicative-adj clause rule. Established polysemy
pattern (Phase 5f Commit 17 ``bababa`` / ``hihigit`` precedent —
same surface, different POS, rule context disambiguates).

## Phase 5h Commit 3: comparative `mas` PART + ADJ-wrapper rule

**Date:** 2026-05-05. **Status:** active. New PART in
``particles.yaml``; new wrapper rule in ``cfg/nominal.py``;
tightening of the Phase 4 hindi-negation rule. Refs: plan §4.1,
§5.1, §6 Commit 3.

The wrapper ``ADJ → PART[COMP_DEGREE=COMPARATIVE] ADJ`` fires
``mas matalino`` → comparative-ADJ. The wrapped ADJ is itself an
ADJ, so the Phase 5g predicative-adj clause rule and NP-internal
modifier rules consume it unchanged — no new clausal / NP rules.

### Unification-clash semantics

``(↑) = ↓2`` shares the inner ADJ's f-structure with the
wrapped output, then ``(↑ COMP_DEGREE) = 'COMPARATIVE'`` writes
COMPARATIVE. If the inner ADJ already carries SUPERLATIVE
(``pinakamaganda``) / INTENSIVE (``napakaganda``) / EQUATIVE
(``kasingganda``) / CONTRASTIVE (``magkaiba``), unification
fails — ``*mas pinakamaganda`` etc. are correctly rejected.

### hindi-negation rule tightening

The Phase 4 ``S → PART[POLARITY=NEG] S`` rule's category-pattern
filter ``PART[POLARITY=NEG]`` matched any PART without POLARITY
via non-conflict matching. Pre-state probes showed
``Halos kumain ang bata`` and ``Tuwing kumain ang bata`` parsing
with bogus ``POLARITY: NEG``. Adding ``mas`` (PART without
POLARITY) would have created the same leak for
``Mas matalino siya``. Fix: add the explicit
``(↓1 POLARITY) =c 'NEG'`` constraining equation, matching the
Phase 5g Commit 3 belt-and-braces ``=c`` pattern. Closes a
latent bug; no test had been asserting on the phantom NEG
parses.

## Phase 5h Commit 4: kaysa comparison-complement

**Date:** 2026-05-05. **Status:** active. New PART
(``kaysa``) and new clausal rule. Refs: plan §4.1, §5.5, §6
Commit 4.

``S → S PART[COMP_PHRASE=KAYSA] NP[CASE=DAT]`` adjoins the
kaysa-headed phrase to the matrix S's ADJUNCT set with
``ROLE: STANDARD``. ``COMP_PHRASE: KAYSA`` mirrors the Phase 5f
Commit 17 numeric-comparator family (``higit`` / ``kulang`` /
``bababa`` / ``hihigit`` all carry ``COMP_PHRASE`` tags).

### Permissive on inner-S COMP_DEGREE

The rule does NOT constrain the inner S to carry
``COMP_DEGREE: COMPARATIVE``. Tagalog usage typically pairs
``kaysa`` with ``mas``, but bare comparisons
(``Matalino si Maria kaysa kay Juan``) are attested colloquially.
Tightening would need ``COMP_DEGREE`` lifted onto the matrix S
by the Phase 5g predicative-adj clause rule (which currently
keeps it on the ADJ daughter); deferred.

## Phase 5h Commit 5: particle intensifiers + wrappers + na-disambiguator

**Date:** 2026-05-05. **Status:** active. Five new PARTs, three
new wrapper rules, and a disambiguator extension. Refs: plan
§4.1, §5.3-5.4, §6 Commit 5.

Five intensifier PARTs each carry ``INTENSIFIER: YES`` plus a
per-particle ``INTENSITY`` tag (sobra / masyado: EXCESSIVE;
medyo: MODERATE; talaga: EMPHATIC; lubos: COMPLETE). Three
wrapper rules in ``cfg/nominal.py``:

```text
ADJ → PART[INTENSIFIER=YES] PART[LINK=NA] ADJ
ADJ → PART[INTENSIFIER=YES] PART[LINK=NG] ADJ
ADJ → PART[INTENSITY=MODERATE] ADJ      (medyo zero-linker)
```

Belt-and-braces ``=c`` constraints on both PART daughters close
the same kind of non-conflict-matcher leak Commits 3 closed:
without ``(↓2 LINK) =c '<link>'``, ``mas`` would absorb the
``PART[LINK=NA]`` slot and let ``Lubos na mas matalino siya``
parse spuriously.

### Disambiguator extension

The Phase 5g helper
``_adj_na_right_context_is_linker_target`` is renamed
``_na_right_context_is_linker_target`` (right-context-only check;
left-context supplied per caller). A new branch in
``disambiguate_homophone_clitics`` recognises
``PART[INTENSIFIER=YES] + na + ADJ`` as a linker context.
Without this, ``reorder_clitics`` would hoist ``na`` to
clause-final ALREADY-clitic position and break the wrapper-
rule's adjacent PART-PART-ADJ pattern. Vowel-final intensifiers
take the bound ``-ng`` (no clitic homophone), so the branch
matters mainly for consonant-final ``lubos``.

### Double-intensive permitted

``Sobrang napakaganda ang bahay`` writes INTENSIVE onto an
already-INTENSIVE inner ADJ. The unifier accepts identity writes,
so the parse succeeds. Linguistically attested as colloquial
"extra emphasis"; no rule additions needed to support or block.

## Phase 5h Commit 6: equative two-NP standard frames

**Date:** 2026-05-06. **Status:** active. Three new clausal
rules. Refs: plan §5.6, §6 Commit 6.

Three rule variants for the equative ``kasing-X`` standard
construction: NOM+GEN, GEN+NOM, NOM+NOM. The comparee is the
NOM-NP (matrix SUBJ); the standard rides on ADJUNCT with
``ROLE: EQUATIVE_STANDARD`` (distinct from Commit 4's
``ROLE: STANDARD`` — the two ROLE values reflect analytically
separate constructions: kaysa is the oblique standard for graded
comparison, the equative standard sits in the predicate's
argument position).

The constraining ``(↓1 COMP_DEGREE) =c 'EQUATIVE'`` restricts
these rules to equative-marked ADJ heads (``kasing-`` / ``sing-``
\+ ``pareho`` / ``magkapareho``). ``magkaiba`` carries
``COMP_DEGREE: CONTRASTIVE`` (not EQUATIVE), so the two-NP
frames don't fire on it — only the single-NP predicative form
parses for magkaiba.

### Why three rules rather than one

Tagalog freely permits NOM-then-GEN and GEN-then-NOM order. Rule
duplication is preferred over a single permissive rule because
the SUBJ ↔ NP mapping is order-dependent (the comparee is the
NOM-NP regardless of position; the standard is whichever
daughter is non-comparee). DAT-standard variant
(``kasing-X kay Y ang Z``) is marginal in modern Tagalog and is
deferred.

### Structural ambiguity for `Pareho ang aklat ko`

The new NOM+GEN rule introduces a structural ambiguity for
sentences like ``Pareho ang aklat ko.``: GEN-clitic ``ko`` can
be analysed either as an embedded possessor on the SUBJ ang-NP
(Phase 5g predicative-adj reading) or as a separate STANDARD
adjunct (equative-frame reading). Both readings produce the
same matrix-level PRED / ADJ_LEMMA / PREDICATIVE; the f-structure
differs only in whether ADJUNCT carries an EQUATIVE_STANDARD
member. Commit 2's test assertion was relaxed from ``== 1`` to
``>= 1``.

## Phase 5h Commit 7: comparative-Q wrapper rule

**Date:** 2026-05-06. **Status:** active. New rule in
``cfg/nominal.py``; sibling to the Commit 3 ADJ-wrapper. Refs:
plan §5.2, §6 Commit 7.

``Q → PART[COMP_DEGREE=COMPARATIVE] Q[VAGUE=YES]``. The wrapped
Q carries COMPARATIVE on its f-structure (via ``(↑) = ↓2``
share-and-write); the existing Phase 5f Commit 15 vague-Q
NP-modifier rule consumes the wrapped Q unchanged. ``mas
maraming aklat`` parses as a Q-modified NP with a
COMP_DEGREE-marked Q head.

### Why a sibling rule rather than overloading the ADJ-wrapper

The Q and ADJ wrappers have different downstream consumers — Q
feeds the NP-modifier and (deferred) predicative-Q rule; ADJ
feeds the predicative-adj clause rule and the NP-internal
ADJ-modifier rules. Modest rule duplication is preferable to
category-pattern overloading.

### Cardinal exclusion

``Q[VAGUE=YES]`` excludes cardinals (``CARDINAL: YES``), so
``*mas tatlong aklat`` is correctly ungrammatical. Cardinal
comparison goes through the Phase 5f Commit 17 ``COMP_PHRASE``
family (``higit sa N`` / ``kulang sa N``).

## Phase 5h Commit 8: negation × Phase 5h composition tests

**Date:** 2026-05-06. **Status:** active. Tests-only. Refs:
plan §6 Commit 8.

The Phase 4 hindi-negation rule (tightened in Commit 3) wraps
every Phase 5h matrix-S output unchanged — each construction's
matrix output is a well-formed S. The commit's test file fills
coverage gaps left by per-Commit test files (notably:
hindi+pareho/magkaiba/magkapareho, hindi+pinaka-/napaka-, and
the canonical ``Hindi masyadong X`` "not very" construction
called out in plan §1).

## Phase 5i Commit 1: wh-word lex inventory

**Date:** 2026-05-06. **Status:** active. Lex-only — wh-PRONs,
wh-ADVs, wh-Qs, the ``kung`` complementizer, the ``di`` tag
particle, plus a YAML-string conversion on ``ba``'s
``QUESTION`` feature. Refs: plan §4.

Pronominal wh in ``data/tgl/pronouns.yaml``:
``sino`` PRON[WH=YES, CASE=NOM, HUMAN=True];
``ano`` PRON[WH=YES, CASE=NOM]; ``kanino`` PRON[WH=YES,
CASE=DAT, HUMAN=True]; ``alin`` PRON[WH=YES, CASE=NOM].

Adverbial wh in ``data/tgl/particles.yaml``: ``saan``
(LOCATION), ``kailan`` (TIME), ``bakit`` (REASON), ``paano``
(MANNER), ``papaano`` (MANNER doublet) — all
ADV[WH=YES, ADV_TYPE=...].

Quantitative wh in ``data/tgl/particles.yaml``: ``magkano``
Q[WH=YES, QUANT=HOW_MUCH, VAGUE=YES]; ``alin`` (Q-polysemy
partner; the standalone PRON ``alin`` is in pronouns.yaml).
``ilan`` polysemy: pre-existing Q[QUANT=FEW, VAGUE=YES]
(non-wh) plus a new wh entry Q[WH=YES, QUANT=HOW_MANY,
VAGUE=YES] — both kept; rule context disambiguates.

Complementizer ``kung`` PART[COMP_TYPE=INTERROG]; tag particle
``di`` PART[NEG_TAG=YES].

### YAML-string convention for category-pattern matchers

The pre-existing ``ba`` lex entry carried ``QUESTION: true``
(YAML boolean). Category-pattern matchers parse the value as
the string ``"true"`` rather than Python ``True``, so the
pattern ``PART[QUESTION=YES]`` would not have matched.
Converted to ``QUESTION: "YES"`` and updated the morph
test (``test_morph.py:729``). The convention is now uniform:
features used in category-pattern matching live as quoted
strings.

## Phase 5i Commit 2: cleft-style wh-fronting (NOM PRON)

**Date:** 2026-05-06. **Status:** active. 1 new clausal rule.
Refs: plan §5.1; Phase 5e Commit 26 (``parang`` literal-PRED
template); Phase 5f Commit 4 (predicative-cardinal); Phase 5g
Commit 3 (predicative-adj).

```text
S → PRON[WH=YES, CASE=NOM] NP[CASE=NOM]
    (↑ PRED) = 'WH <SUBJ>'
    (↑ SUBJ) = ↓2
    (↑ Q_TYPE) = 'WH'
    (↑ WH_LEMMA) = ↓1 LEMMA
    (↓1 WH) =c 'YES'
```

The canonical Tagalog wh-Q analysis: a verbless cleft with the
wh-PRON as the cleft-pivot and the NOM-NP as a headless RC.
``Sino ang kumain?`` parses with PRED=``WH <SUBJ>``,
WH_LEMMA=sino, SUBJ=the headless RC ``ang kumain``.

### Why literal-PRED rather than a lexicalised wh-PRED

Each wh-PRON's lemma carries the wh-content (sino / ano /
alin); the matrix PRED encodes "this is a wh-Q with one
argument" as a literal template. Consumers (ranker / classifier
/ semantics) read ``WH_LEMMA`` for the specific wh-word.

### Why CASE=NOM in the pattern (excluding kanino)

``kanino`` carries CASE=DAT; the NOM-only cleft excludes it
deliberately. The DAT-pivot cleft was added in Commit 9 as a
separate rule.

## Phase 5i Commit 3: in-situ wh-PRON shells

**Date:** 2026-05-06. **Status:** active. 2 new NP shells in
``cfg/nominal.py``. Refs: plan §5.2.

```text
NP[CASE=GEN] → ADP[CASE=GEN] PRON[WH=YES]
NP[CASE=DAT] → ADP[CASE=DAT] PRON[WH=YES]
```

Each shell binds the PRON daughter to the matrix NP via
``(↑) = ↓2``. The wh-PRON fills an OBJ / ADJUNCT slot in-situ;
the matrix Q_TYPE is NOT lifted (per plan §5.2 deferral).
Consumers detect Q-ness by f-structure inspection — any PRON
with WH=YES inside the c-tree marks the matrix as a question
without an explicit Q_TYPE flag.

### Why no matrix Q_TYPE lift

Lifting Q_TYPE through arbitrary depth (e.g., from inside a
DAT-NP nested in an ADJUNCT set) would require functional-
uncertainty equations or post-pass f-structure inspection.
The pre-state confirms callers can already detect WH=YES on
the embedded PRON; the explicit matrix Q_TYPE is left for a
future commit if corpus pressure surfaces.

## Phase 5i Commit 4: adverbial-wh fronting

**Date:** 2026-05-06. **Status:** active. 1 new clausal rule.
Refs: plan §5.3.

```text
S → ADV[WH=YES] S
    (↑) = ↓2
    (↑ Q_TYPE) = 'WH'
    (↑ WH_LEMMA) = ↓1 LEMMA
    ↓1 ∈ (↑ ADJUNCT)
    (↓1 WH) =c 'YES'
```

Sentence-initial wh-ADV (saan / kailan / bakit / paano /
papaano) marks the matrix as a wh-Q whose interrogated
constituent is an adjunct of the underlying verbal clause.
The wh-ADV adjoins to the matrix S's ADJUNCT set; the inner
S is the residue verbal clause (with its own SUBJ — typically
a 2P clitic like ``ka``).

### ADV_TYPE-derived ROLE percolation

Each wh-ADV's ``ADV_TYPE`` (LOCATION / TIME / REASON / MANNER)
percolates onto the ADJUNCT member's f-structure via the lex
feats. Consumers can read it off the adjunct without
traversing back to the c-tree.

## Phase 5i Commit 5: yes/no Q matrix-feature lift

**Date:** 2026-05-06. **Status:** active. Split the Phase 4
§7.3 2P-clitic absorption rule in ``cfg/clitic.py``. Refs:
plan §5.4; Phase 4 §7.3.

The pre-existing single rule for 2P-clitic absorption fires
on every CLITIC_CLASS=2P PART (ba / pa / na / din / etc.).
Adding ``(↑ Q_TYPE) = ↓2 Q_TYPE`` as a defining equation
would pollute the matrix S's f-structure with empty Q_TYPE
slots for non-Q clitics (cascading to 19+ baseline entries
during Commit 5 development).

The split: two sibling rules with mutually-exclusive
constraints —

1. **Generic absorption** (any 2P clitic except ba):
   ``S → S PART[CLITIC_CLASS=2P]`` with ``¬ (↓2 QUESTION)``.
2. **Ba-only absorption** (yes/no Q-clitic):
   ``S → S PART[CLITIC_CLASS=2P, QUESTION=YES]`` with
   ``(↑ Q_TYPE) = 'YES_NO'`` literal write.

The ba rule fires only when QUESTION=YES on the clitic. The
generic rule's negation constraint excludes ba, preventing
cross-firing. The two-rule split avoids the
defining-equation pollution that a single-rule lift would
create. ``Kumain ka ba ng kanin?`` parses with
Q_TYPE=YES_NO.

## Phase 5i Commit 6: aling pre-N selector + wh-N cleft

**Date:** 2026-05-06. **Status:** active. Three pieces: lex
deletion, new N-level companion rule, new clause-level cleft
rule. Refs: plan §5.5; Phase 5f Commit 15 (vague-Q
NP-modifier — leveraged for aling).

### Drop standalone aling Q lex entry

The Commit 1 plan added ``aling`` Q[WH=YES, VAGUE=YES] as a
unified surface. ``split_linker_ng`` keeps a known full surface
intact rather than splitting; this prevented ``aling bata``
from decomposing into ``alin`` + ``-ng`` + ``bata``. Dropping
the standalone ``aling`` Q entry lets ``split_linker_ng``
fire (``alin`` exists as a known PRON / Q surface) — the
``-ng`` linker becomes a separate token, and the existing
Phase 5f Commit 15 vague-Q NP-modifier rule consumes the
result.

### Wh-Q + N companion rule (cfg/nominal.py)

```text
N → Q[VAGUE=YES, WH=YES] PART[LINK=NA|NG] N
    (↑) = ↓3
    (↑ WH) = 'YES'
    (↑ WH_LEMMA) = ↓1 LEMMA
    (↑ QUANT) = ↓1 QUANT
    (↑ VAGUE) = 'YES'
    (↓2 LINK) =c '...'  (per linker variant)
    (↓1 WH) =c 'YES'
```

Sibling to the existing non-wh vague-Q companion (Phase 5f
Commit 15). The constraint ``Q[VAGUE=YES, WH=YES]`` excludes
non-wh vague Qs (lahat / iba / marami) — they continue to fire
only the non-wh companion.

### Wh-N cleft (cfg/clause.py)

```text
S → N[WH=YES] NP[CASE=NOM]
    (↑ PRED) = 'WH <SUBJ>'
    (↑ SUBJ) = ↓2
    (↑ Q_TYPE) = 'WH'
    (↑ WH_LEMMA) = ↓1 WH_LEMMA
    (↓1 WH) =c 'YES'
```

Sibling to Commit 2 PRON-cleft, but with N (rather than PRON)
at the predicate slot. ``Aling bata ang kumain?`` parses with
WH_LEMMA=alin lifted from the wh-N daughter.

### Aso ang isda. corpus flip side-effect

The wh-N cleft predicts N at clause-initial position. The
Earley chart now records completed N states for any sentence-
initial noun, even non-wh ones. The corpus entry ``Aso ang
isda.`` (a non-wh NP-NP predicative-N construction, deferred
§18) flipped from ``expected: fail`` to ``expected: fragment``
because the chart now has completed N (``aso``) and
NP[CASE=NOM] (``ang isda``) states that fragment extraction
returns. Documented in the corpus entry's notes block.

## Phase 5i Commit 7: tag question ``di ba?``

**Date:** 2026-05-06. **Status:** active. 1 new clausal rule.
Refs: plan §5.6.

```text
S → S PART[NEG_TAG=YES] PART[QUESTION=YES, CLITIC_CLASS=2P]
    (↑) = ↓1
    ↓3 ∈ (↑ ADJ)
    (↑ Q_TYPE) = 'TAG'
    (↓2 NEG_TAG) =c 'YES'
    (↓3 QUESTION) =c 'YES'
```

Single combined rule rather than two sub-rules
(``S → S PART[di]`` + Commit 5 ba-Q rule). The two-rule
alternative would chain (creating Q_TYPE clash on the matrix
when both fire) or each fire independently (leaving ``di``
orphaned if only the ba rule matched). Combining both clitics
into one rule with ``Q_TYPE='TAG'`` cleanly subsumes the
construction.

The yes/no Q-rule (Commit 5) would otherwise match ``ba`` here
and write ``Q_TYPE='YES_NO'``; the matrix-Q_TYPE clash rejects
that parse (TAG ≠ YES_NO at the unifier), leaving only the
tag-Q reading as the surviving parse.

## Phase 5i Commit 8: indirect-Q embedding via kung — COMP not XCOMP

**Date:** 2026-05-06. **Status:** active. New non-terminal +
new wrap rule + new lex entry. Refs: plan §5.7; Phase 4 §7.6
control complement; Phase 5c §7.6 follow-on.

### S_INTERROG_COMP non-terminal

```text
S_INTERROG_COMP → PART[COMP_TYPE=INTERROG] S[Q_TYPE=WH]
    (↑) = ↓2
    (↑ COMP_TYPE) = 'INTERROG'
    (↓1 COMP_TYPE) =c 'INTERROG'
    (↓2 Q_TYPE) =c 'WH'
```

Lifts the inner S f-structure and adds COMP_TYPE=INTERROG.
The belt-and-braces ``=c`` constraints close non-conflict-
matcher leaks on both the complementizer's COMP_TYPE and the
inner clause's Q_TYPE.

### Matrix wrap for KNOW-class predicates

```text
S → V[CTRL_CLASS=KNOW] NP[CASE=GEN] S_INTERROG_COMP
    (↑ SUBJ) = ↓2
    (↑ COMP) = ↓3
    (↓1 CTRL_CLASS) =c 'KNOW'
    (↓3 COMP_TYPE) =c 'INTERROG'
```

Plus verb percolation (PRED / VOICE / ASPECT / MOOD /
LEX-ASTRUCT). The GEN-NP experiencer is matrix SUBJ (the same
NOM→SUBJ deviation as PSYCH); the indirect-Q clause is matrix
COMP. No linker between matrix and complement — ``alam`` is a
stative and ``kung`` is the complementizer.

### Why CTRL_CLASS=KNOW (not PSYCH)

The pre-existing PSYCH wrap requires linker + S_XCOMP open
complement. Adding ``alam`` with CTRL_CLASS=PSYCH would let
the existing PSYCH rule cross-fire (semantically odd:
``Alam kong kumain`` "I want / am-able to eat"). The fresh
KNOW class keeps the indirect-Q wrap mutually exclusive with
the PSYCH open-XCOMP wrap.

### Why COMP rather than XCOMP

The plan-of-record §5.7 used ``XCOMP`` loosely. The actual LFG
slot is ``COMP`` (closed sentential complement) because the
embedded clause has its own SUBJ (the wh-pivot of the
indirect-Q) and there is no SUBJ-control / linker. Using COMP
preserves the f-structure invariant: XCOMP is SUBJ-controlled
by definition; COMP is closed. PRED template ``KNOW <SUBJ,
COMP>`` reflects this; the deviation from the plan's loose
naming is documented in the commit message and here.

## Phase 5i Commit 9: kanino / magkano / ilan-WH integration

**Date:** 2026-05-06. **Status:** active. 3 new clausal rules.
Refs: plan §6 Commit 9 row; Phase 5f Commit 15 (vague-Q
NP-modifier — leveraged for ilan-WH polysemy via Commit 6).

Three sibling rules in ``cfg/clause.py``:

### Predicative-Q cleft

```text
S → Q[WH=YES] NP[CASE=NOM]
    (↑ PRED) = 'WH <SUBJ>'
    (↑ SUBJ) = ↓2
    (↑ Q_TYPE) = 'WH'
    (↑ WH_LEMMA) = ↓1 LEMMA
    (↓1 WH) =c 'YES'
```

Fires on ``magkano`` (HOW_MUCH), ``ilan`` WH-polysemy
(HOW_MANY), and the ``alin`` Q-polysemy partner.

### DAT-pivot cleft

```text
S → PRON[WH=YES, CASE=DAT] NP[CASE=NOM]
    (↑ PRED) = 'WH <SUBJ>'
    (↑ SUBJ) = ↓2
    (↑ Q_TYPE) = 'WH'
    (↑ WH_LEMMA) = ↓1 LEMMA
    (↓1 WH)   =c 'YES'
    (↓1 CASE) =c 'DAT'
```

Sibling to Commit 2 NOM-cleft, with CASE=DAT discriminating
against sino / ano / alin. Targets ``Kanino ang aklat?``
"Whose is the book?".

### DAT-wh fronting

```text
S → PRON[WH=YES, CASE=DAT] S
    (↑) = ↓2
    (↑ Q_TYPE) = 'WH'
    (↑ WH_LEMMA) = ↓1 LEMMA
    ↓1 ∈ (↑ ADJUNCT)
    (↓1 WH)   =c 'YES'
    (↓1 CASE) =c 'DAT'
```

Sibling to Commit 4 adverbial-wh fronting, with PRON.
Targets ``Kanino ka pumunta?`` "To whom did you go?".

### alin polysemy harmless redundancy

``alin`` is lex-polysemous: both PRON[WH=YES, CASE=NOM]
(Commit 1) and Q[WH=YES, VAGUE=YES] (Commit 1 polysemy
partner). ``Alin ang aklat?`` produces two parses post-Commit-9
— one via Commit 2's PRON-cleft, one via Commit 9's Q-cleft —
which share the same f-structure (``PRED='WH <SUBJ>'``,
WH_LEMMA='alin'). Tests admit ``>= 1`` parses to allow the
redundancy.

### Closes Commit 2's TestKaninoNotMatched deferral

Commit 2's PRON-cleft constrained on CASE=NOM, deliberately
excluding kanino (CASE=DAT). The original
``TestKaninoNotMatched::test_kanino_no_cleft_parse`` asserted
zero wh-parses for ``Kanino ang aklat?``. Commit 9's DAT-pivot
cleft closes the deferral; the test was renamed to
``TestKaninoNotMatchedByNomCleft::test_kanino_dat_cleft_fires``
and flipped to assert WH_LEMMA=kanino with at least one
Q_TYPE=WH parse.

### In-situ kanino — no matrix Q_TYPE lift

``Pumunta ka kanino?`` parses today (kanino fills a DAT-NP
ADJUNCT slot via the existing nominal shells). The matrix
does NOT carry Q_TYPE=WH — the in-situ case follows Commit 3's
deferral. Consumers can inspect the ADJUNCT set's wh-PRON
member to detect the Q-ness.

## Phase 5j Commit 1: existential / locative-existential lex inventory

Roadmap §12.1 / plan-of-record §4.1 + §4.3. Three positive-/
negative-existential clause-typers (``may`` / ``mayroon`` /
``wala``) and one locative-existential clause-typer (``nasa``)
added as ``pos: PART`` entries in ``data/tgl/particles.yaml``;
three supporting locative / proper nouns (``labas`` / ``tuktok``
/ ``bukid``) added as ``pos: NOUN`` entries in
``data/tgl/nouns.yaml``.

### Existentials are PART (clause-typing), not V

Per roadmap §12.1: ``may`` / ``mayroon`` / ``wala`` / ``nasa``
are clause-typing predicates, NOT V-headed verbal frames. They
head their own constituent shapes via dedicated grammar rules
(Commits 2-5) rather than slotting into the V-headed S frame
family. The PART-not-V choice keeps them out of the voice /
aspect / control machinery entirely; the existing rules don't
need any guard-clauses for "the V isn't a real verb."

YAML-string ``"YES"`` follows the Phase 5h / 5i category-pattern-
matcher convention (boolean YAML breaks the matchers); LEMMA
explicit on each entry; POS / NEG polarity on the existentials so
the Commits 2 / 3 rules disambiguate via category-pattern matching
rather than a single POS-or-NEG-disjunct rule with later runtime
guards.

### LOC_EXISTENTIAL distinct from EXISTENTIAL

``nasa`` carries ``LOC_EXISTENTIAL: "YES"`` (NOT
``EXISTENTIAL: "YES"``); ``may`` / ``mayroon`` / ``wala`` carry
``EXISTENTIAL: "YES"`` (NOT ``LOC_EXISTENTIAL: "YES"``). The two
clause-types are categorically distinct — Commit 4's locative
rules don't fire on may / wala, and Commits 2 / 3 / 5
existential rules don't fire on nasa. The matrix
``CLAUSE_TYPE`` feature reflects this: ``EXISTENTIAL`` for the
positive / negative / HAVE family; ``LOC_EXISTENTIAL`` for the
nasa family.

## Phase 5j Commit 2: positive existential clause

Roadmap §12.1 / plan-of-record §5.1. Three rules in
``cfg/clause.py``:

```text
S → PART[EXISTENTIAL=YES, POLARITY=POS] N
    (↑ PRED) = 'EXIST <SUBJ>'
    (↑ SUBJ) = ↓2
    (↑ CLAUSE_TYPE) = 'EXISTENTIAL'
    (↑ POLARITY) = 'POS'
    (↓1 EXISTENTIAL) =c 'YES'
    (↓1 POLARITY) =c 'POS'

S → PART[EXISTENTIAL=YES, POLARITY=POS] PART[LINK=NG] N
    (same equations + bound-linker daughter for mayroon)

S → S NP[CASE=DAT]
    (↑) = ↓1
    ↓2 ∈ (↑ ADJUNCT)
    (↓1 CLAUSE_TYPE) =c 'EXISTENTIAL'
```

### PRED uses SUBJ, not THEME

Initially drafted with PRED ``'EXIST <THEME>'`` and a THEME
slot binding the existence-asserted N. The Subject Condition
(LMT step 6, ``check_subject_condition``) requires every
PRED-bearing f-structure to have a SUBJ. Treating the
existence-asserted N as SUBJ satisfies this without a special-
case carve-out for existentials, and matches the codebase's
GF-named-PRED-template convention (mirrors Phase 5g
``'ADJ <SUBJ>'`` and Phase 5f Commit 4
``'CARDINAL <SUBJ>'``). Thematic roles live in the a-structure
projection (Phase 4 architecture).

### Daughter is bare N, not NP[CASE=...]

Tagalog existentials take indefinite bare nominals. ``*May ang
aklat`` is ungrammatical (the ang-determiner forces
definiteness, which clashes with the existential's indefinite-
introducer semantics). Adjective-modified Ns (``May matandang
aklat``) fall out via the Phase 5g NP-internal modifier rules
which project to ``N``. Cardinal-modified Ns (``May isang
aklat``) compose via the Phase 5f Commit 1 cardinal NP-modifier
rule.

### Locative-PP via EXISTENTIAL-gated DAT-lift

The plan §3 anticipated locative-PP composition would "fall
out of the existing Phase 4 §7.7 sa-PP-as-ADJUNCT machinery."
Reconnaissance during Commit 2 showed that machinery is per-
frame embedded in V-headed S rules, not a general clause-final
DAT-NP wrap. Commit 2 added a new wrap rule ``S → S
NP[CASE=DAT]`` gated on ``(↓1 CLAUSE_TYPE) =c 'EXISTENTIAL'``
to compose locative-PP onto existential matrices without
spurious double-parse ambiguity on V-headed clauses (which
already embed their own DAT-NP daughters at frame level).

## Phase 5j Commit 3: negative existential clause

Roadmap §12.1 / plan-of-record §5.2. Two rules in
``cfg/clause.py`` mirror the Commit 2 positive rules with
POLARITY=NEG. ``wala`` is vowel-final and always takes bound
``-ng`` before its complement (``Walang aklat`` is canonical;
``*Wala aklat`` is ungrammatical), so the linker variant is
the primary entry point. The bare-N variant covers ``Wala.``
standalone. The Commit 2 EXISTENTIAL-gated DAT-lift rule
fires on negative matrices unchanged, so locative-PP
composition (``Walang tao sa labas``) requires no new rule.

## Phase 5j Commit 4: locative existential `nasa`

Roadmap §12.1 / plan-of-record §5.3. Two rules in
``cfg/clause.py``:

```text
S → PART[LOC_EXISTENTIAL=YES] N NP[CASE=NOM]
    (↑ PRED) = 'LOC <SUBJ>'
    (↑ SUBJ) = ↓3
    (↑ LOCATION) = ↓2
    (↑ CLAUSE_TYPE) = 'LOC_EXISTENTIAL'
    (↓1 LOC_EXISTENTIAL) =c 'YES'

S → PART[LOC_EXISTENTIAL=YES] N NP[CASE=GEN] NP[CASE=NOM]
    (same + (↓2 POSS) = ↓3 binding for ground possessor)
```

### Two-rule split for optional GEN-NP possessor

The parser's category-pattern matching can't express
"optional" daughters; the alternative would be a recursive
intermediate non-terminal, which is more invasive than
necessary for a phase-local construction. Mirrors the V-headed-
frame convention of explicit per-shape rules.

### LOCATION as feature, not PRED argument

PRED is one-place over the figure (``'LOC <SUBJ>'``). The
locative ground rides on a dedicated ``LOCATION`` feature
(not in the PRED's argument list) because ``nasa`` is
structurally a clause-typer, not a binary predicate over the
LFG GF inventory. This mirrors the Phase 5h Commit 4
``ROLE='STANDARD'`` convention for comparison standards —
features that hold thematic-role data outside the GF mapping.

### R&G "Ang Manok" simples #5 and #7

This commit unblocks two of the three remaining R&G 1981
simple sentences (per roadmap §12.6):

- Simple #5: ``Nasa bundok ang bahay.`` (base form)
- Simple #7: ``Nasa tuktok ng bundok ang bahay.`` (possessor
  variant)

Simples #1 and #3 remain blocked on deferred ``nakatira``
resultative paradigm, ``mag-isa`` ADV hyphen-tokenization, and
``mama`` lex.

## Phase 5j Commit 5: HAVE construction

Roadmap §12.1 / plan-of-record §5.4 + §5.5. Four rules in
``cfg/clause.py`` covering positive / negative × postposed-
possessor / internal-clitic-possessor patterns. F-structure
shape (all four):

```text
PRED = 'EXIST <SUBJ>'
SUBJ = the existence-asserted N
SUBJ POSSESSOR = the possessor-NP / clitic-PRON
CLAUSE_TYPE = 'EXISTENTIAL'
HAVE = 'YES'
POLARITY = 'POS' or 'NEG'
```

### POSSESSOR feature, not OBLIQUE thematic role

Tagalog HAVE is structurally an existential ("exists X
possessed by Y"), not a transitive ("Y has X"). The POSSESSOR
feature on the SUBJ N captures this while keeping the matrix
CLAUSE_TYPE as EXISTENTIAL and the matrix PRED as the literal
``'EXIST <SUBJ>'``. ``(↑ HAVE) = 'YES'`` lifts the HAVE-reading
flag for downstream consumers.

### Internal-clitic rules constrain to PRON

The internal-clitic rules (5b / 5d) constrain the possessor
daughter to PRON (not NP[CASE=NOM]) — full-NP-with-internal-
linker patterns like ``*May Mariang aklat`` are marginal in
modern Tagalog and would compete with NP-internal POSS rules.
The PRON gate avoids this cross-fire.

### POS / NEG asymmetry is surface-level

``may`` is consonant-final and never takes the bound linker;
``wala`` is vowel-final and always takes it before its
complement. Four rules total covering the four combinations.

## Phase 5j Commit 6: modal verbs lex inventory + LexicalEntry

Roadmap §12.1 / plan-of-record §4.2 + §4.4. Six new
``pos: VERB`` entries in ``data/tgl/particles.yaml`` (closed-
class predicates parallel to Phase 4 §7.6 PSYCH and Phase 5i
``alam`` KNOW); one NOUN entry in ``data/tgl/nouns.yaml``
(kailangan polysemy partner); four ``LexicalEntry`` entries
in ``src/tgllfg/core/lexicon.py`` with per-modal PRED
templates (``DAPAT`` / ``PUWEDE`` / ``MAAARI`` / ``KAILANGAN``
``<SUBJ, XCOMP>``).

### CTRL_CLASS=MODAL keeps modals isolated

Modals carry ``CTRL_CLASS=MODAL`` (NOT PSYCH or KNOW or
RAISING) so the Commit 7 modal control wrap can filter to
modals only via ``(↓1 CTRL_CLASS) =c 'MODAL'`` and the
existing PSYCH / KNOW / RAISING wrap rules don't cross-fire.

### Surface-variant collapse via canonical lemma

``puwede`` / ``pwede`` / ``puede`` are three orthographic
variants of one canonical lemma ``puwede``. The variant
collapse mechanic (Commit 7) reads the ``LEMMA`` feat from
particles.yaml as the canonical lemma; ``MorphAnalysis.lemma``
is set to ``feats.get("LEMMA", surface)`` so all three
variants route through a single ``LexicalEntry`` keyed by
``puwede``.

### kailangan polysemy — VERB[MODAL] + NOUN

``kailangan`` indexes as both a VERB[MODAL=YES] (the modal
"need / must") and a NOUN ("need / requirement", as in
``ang kailangan ko`` "what I need"). Two separate lex entries,
one surface, rule context disambiguates — same precedent as
Phase 5h ``pareho`` and Phase 5i ``alin`` / ``ilan``.

### Documented temporary regression: Hindi ka dapat kumain

``Hindi ka dapat kumain.`` (no-linker form) parsed pre-
Commit-6 as ``EAT <SUBJ>`` POLARITY=NEG via silent-dropping
``dapat``. After Commit 6 the strip stops firing and the
sentence returns 0 parses (1→0 regression). The canonical
form requires the linker (``Hindi ka dapat na kumain.``); the
no-linker form is marginal Tagalog and remains 0-parse
post-Commit-7. The previous silent-drop reading was
structurally wrong (the modal was being ignored).

## Phase 5j Commit 7: modal control wrap + orthographic-variant collapse

Roadmap §12.1 / plan-of-record §5.6. Two analytical moves in
this commit.

### Modal control wrap (4 rules)

```text
For link in (NA, NG):
  S → V[CTRL_CLASS=MODAL] NP[CASE=NOM] PART[LINK={link}] S_XCOMP
      (↑ SUBJ) = ↓2
      (↑ XCOMP) = ↓4
      (↑ SUBJ) = (↑ XCOMP REL-PRO)
      (↓1 CTRL_CLASS) =c 'MODAL'
      (↓1 MODAL) =c 'YES'
  S → V[CTRL_CLASS=MODAL] NP[CASE=GEN] PART[LINK={link}] S_XCOMP
      (same equations)
```

Subject control via ``(↑ SUBJ) = (↑ XCOMP REL-PRO)`` — same
shape as the Phase 4 §7.6 PSYCH wrap, distinguished only by
CTRL_CLASS=MODAL.

Two case variants:

- **NOM-actor pattern** (``Dapat akong kumain.``): dapat /
  puwede / maaari take NOM-marked actors.
- **GEN-experiencer pattern** (``Kailangan kong kumain.``):
  kailangan takes a GEN-marked experiencer (parallel to
  PSYCH ``gusto``).

Both rules carry the same equations; the daughter ``CASE``
disambiguates which fires. For modals where both cases are
marginal-but-acceptable, both rules fire and produce parallel
parses — no harm.

### Orthographic-variant collapse mechanic

Phase 5j Commit 6 had to register three separate LexicalEntries
for ``puwede`` / ``pwede`` / ``puede`` because
``MorphAnalysis.lemma`` was set to the surface and
``lookup_lexicon`` keys off the lemma attribute. Commit 7
refactored the morph analyzer's particles indexing branch to
use ``feats.get("LEMMA", surface)`` for the
``MorphAnalysis.lemma`` field. The ``LEMMA`` feat in
particles.yaml names the canonical lemma; variants then route
to a single canonical LexicalEntry through ``lookup_lexicon``.

- Before: 3 LexicalEntries (puwede + pwede + puede) with
          identical bodies.
- After:  1 LexicalEntry (puwede); pwede / puede surfaces
          carry ``LEMMA: puwede`` and route via the morph
          layer.

For the majority of particles where ``LEMMA == surface`` (or no
``LEMMA`` feat is set), the change is a no-op. The mechanism is
now available for any future orthographic-variant family —
saved as a memory-level reminder
(``feedback_orthographic_variants.md``) so future variant
introductions follow the pattern without prompting.

The mechanism currently lives only in the ``particles`` branch
of ``_build_index``. Extending to other categories (pronouns /
nouns / verbs / adjectives) is straightforward but should land
when an actual variant family appears in those data files.

### no-linker form Hindi ka dapat kumain. is permanent 0-parse

The canonical Tagalog modal+complement form requires the
linker (``Hindi ka dapat na kumain.``). The no-linker surface
``Hindi ka dapat kumain.`` is marginal / colloquial and
remains 0-parse post-Commit-7. The Commit 6 test class
``TestNoLinkerModalIsZeroParses`` pins this expectation.

## Phase 5j Commit 8: negation × modal interactions + kailangan polysemy

Roadmap §12.1 / plan-of-record §6 Commit 8. Test-only commit:
no new grammar rules. Verifies that the Phase 4 §7.2 hindi-
wrap composes with the Commit 7 modal control wrap unchanged
and that the kailangan polysemy is correctly disambiguated by
rule context.

### Phase 4 hindi-wrap × non-`ka` NOM-clitic deferral

A pre-existing issue surfaced during Commit 8 testing:
``Hindi ako kumain.`` and ``Hindi siya kumain.`` (with non-``ka``
NOM-clitics) produce 0 parses. By extension,
``Hindi ako dapat na kumain.`` and ``Hindi siya dapat na
kumain.`` also fail. Only the ``ka`` 2P-clitic composes
correctly with the hindi-wrap; ``ako`` / ``siya`` are PRONs
without ``is_clitic=True`` in the lex, and the hindi-wrap
requires the clitic to absorb at the matrix.

This is a Phase 4 §7.2 issue, not Phase 5j-specific. The
Commit 8 tests work around it by using only ``ka`` for the
NOM-actor patterns. Added to plan §9.2 as a Phase 5j follow-on
target.

## Phase 5j Commit 9: R&G "Ang Manok" simples #5 + #7 corpus integration

Roadmap §12.6 / plan-of-record §8. Two corpus entries
(``Nasa bundok ang bahay.`` and ``Nasa tuktok ng bundok ang
bahay.``) and 8 integration tests. End of Phase 5j delivers
5/7 R&G simples (4 from Phase 5g + 2 from Phase 5j); simples
\#1 / \#3 remain blocked on deferred ``nakatira`` resultative
/ ``mag-isa`` hyphen-split / ``mama`` lex. The combined
essay-paragraph (R&G p. 482) needs simples #1 / #3 to land
first; the Phase 5j follow-on closes that.

## Phase 5k Commit 1: coordinator + punctuation lex inventory

Roadmap §12.1 / plan-of-record §4.1-§4.4. Ten new lex entries
in ``data/tgl/particles.yaml`` plus an update to the Phase 5i
tag-Q rule.

### Coordinators are PART-typed clause / NP-typers

Coordinators (``at``, ``o``, ``pero`` / ``ngunit`` / ``subalit``,
``kaya``) are PART-typed lex entries with a ``COORD`` feature
that lifts onto the matrix coord f-structure. Same precedent as
Phase 5j PART-typed clause-typers (``may`` / ``wala`` / ``nasa``)
— closed-class connectives go in ``data/tgl/particles.yaml``,
not as their own lexical category. The matrix coord rules read
``COORD`` from the daughter and mirror it on the matrix, without
introducing a separate coord-PRED.

### `kaya` polysemy: VERB[CTRL_CLASS=PSYCH] + PART[COORD=SO]

Same precedent as Phase 5j ``kailangan`` (V[MODAL] + NOUN),
Phase 5h ``pareho`` (predicative-ADJ + Q-floated), Phase 5i
``alin`` / ``ilan``. Two YAML entries with the same surface;
both readings are returned by the morph layer; rule context
disambiguates without cross-fire (PSYCH wraps with
GEN-experiencer + linker + XCOMP-V; PART[COORD=SO] sits between
two complete S clauses).

### Comma as PUNCT[PUNCT_CLASS=COMMA]

Pre-Phase-5k Commit 1 the comma was ``_UNK`` and silently
dropped by ``_strip_non_content``. Phase 5k makes the comma
structurally meaningful (multi-conjunct, asymmetric, comma-
marked clausal coord, tag-Q boundary) — adding the lex entry
makes it survive the strip. The Phase 5i tag-Q rule was
correspondingly split into a 4-daughter form (with comma) and
the 3-daughter form (no comma); both are admitted because both
orthographic conventions are attested.

## Phase 5k Commit 2: apostrophe-t text-pass

Roadmap §12.1 / plan-of-record §5 (text-pass note), §6 Commit 2.
New ``split_apostrophe_t`` pre-pass in
``src/tgllfg/text/clitics.py``.

### Bound-clitic 't is contracted at after a vowel

The bound clitic ``'t`` post-vowel is the contracted form of
the additive coordinator ``at`` "and": ``Maria't Juan`` =
``Maria at Juan``; ``isa't kalahati`` "one and a half";
``apat na pu't lima`` "45". The tokenizer's ``\\w+|\\S`` regex
splits ``Maria't`` into three tokens (``Maria`` / ``'`` / ``t``);
the new pre-pass collapses any ``[X-vowel-final, ', t]`` triple
into ``[X, at]`` where the synthetic ``at`` token routes to the
Phase 5k Commit 1 PART[COORD=AND] lex entry.

### Vowel-final gate prevents spurious firings

``apat't lima`` is ungrammatical (apat is consonant-final); the
canonical form is ``apat at lima`` or ``apat na pu't lima``
(with intermediate ``na`` linker bringing the ``'`` onto the
vowel-final ``pu``). The vowel-final gate also keeps the pass
from firing on English contractions inside docstrings or future
code-switching contexts.

## Phase 5k Commit 3: binary NP coordination

Roadmap §12.1 / plan-of-record §5.1, §5.2, §6 Commit 3. Six new
rules in ``cfg/coordination.py`` (new module).

### Coord matrix is a fresh f-structure

Neither conjunct IS the matrix coord-NP; both are ELEMENTS of
its CONJUNCTS set via the Phase 5j ``↓N ∈ (↑ SET)`` operator.
No ``(↑) = ↓N`` lift; the matrix carries non-distributive
features (COORD, NUM, CASE) of its own; per-conjunct features
(PRED, LEMMA, MARKER, modifier sets, POSSESSOR) stay on each
conjunct. No PRED on the coord matrix — coordination is
structurally non-predicational.

### CASE agreement via parallel category-pattern daughters

Both conjuncts must share CASE (NOM, GEN, DAT). The rule
``NP[CASE=X] → NP[CASE=X] PART[COORD=Y] NP[CASE=X]`` enforces
this structurally — mismatched-CASE coord sentences fail at
the chart layer with no rule firing. Six rules in total
(3 cases × 2 coord values).

### NUM percolation: AND-forces-PL vs OR-percolates

Additive ``at`` forces NUM=PL on the matrix (semantically
two-or-more); disjunctive ``o`` percolates NUM from the first
conjunct via ``(↑ NUM) = ↓1 NUM``. Reflects the semantic
difference: ``Maria at Juan`` has two referents (plural);
``Maria o Juan`` has one underspecified referent (singular).

## Phase 5k Commit 4: multi-conjunct NP coord (3-flat)

Roadmap §12.1 / plan-of-record §5.3, §6 Commit 4. Six new rules
covering Oxford and non-Oxford comma conventions.

### Both Oxford and non-Oxford forms admitted

``Maria, Juan, at Pedro`` (Oxford comma — 6-daughter form) and
``Maria, Juan at Pedro`` (non-Oxford — 5-daughter form) are
both attested in modern Tagalog written practice. Both rules
produce the same flat 3-element CONJUNCTS set on the matrix.

### Restricted to AND only and to 3 conjuncts

Disjunctive 3-conjunct (``Maria, Juan, o Pedro``) is rare in
Tagalog and deferred to a Phase 5k follow-on. 4+ conjuncts
would compose via the binary rule wrapping a 3-conjunct sub-NP,
producing a NESTED CONJUNCTS structure rather than the flat
4-element set users expect; right-recursive ``NP_COMMA_LIST``
for arbitrary arity is deferred per plan §9.2.

## Phase 5k Commit 5: binary clausal coordination

Roadmap §12.1 / plan-of-record §5.4, §6 Commit 5. Two new
clausal-coord rules + LMT robustness fix.

### Coord matrix has no PRED

Each conjunct clause is its own f-structure (with own PRED,
SUBJ, voice/aspect/mood); the matrix coord-S carries only
CONJUNCTS + COORD. No PRED on the matrix is the canonical LFG
analysis for non-asymmetric coordination — the matrix doesn't
introduce a second-order predication; it merely organizes its
conjuncts.

### LMT robustness on PRED-less matrices

The legacy LMT (``lmt/legacy.py``) previously crashed with
``IndexError`` on PRED-less f-structures (``("" or "").split()[0]``).
Phase 5k Commit 5 extends ``apply_lmt`` to detect the empty-PRED
case and return an empty AStructure (``pred=""``, no roles, no
mapping) rather than crash. This is the canonical fallback for
non-predicational coord matrices; the Phase 5 BK engine isn't
called on them because ``find_matrix_lex_entry`` returns None.

## Phase 5k Commit 6: adversative clausal coordination

Roadmap §12.1 / plan-of-record §5.5, §6 Commit 6. One new
clausal-coord rule (added via the parametrized
``_BINARY_CLAUSAL_COORDS`` tuple).

### Three lex surfaces, one COORD value

``pero`` / ``ngunit`` / ``subalit`` all carry COORD=BUT
(everyday vs formal register). A single rule covers all three
because the lex feature COORD=BUT is what selects the daughter,
not the lemma. This matches the LFG convention of grouping
morphologically-distinct synonyms under a shared functional
value.

## Phase 5k Commit 7: consequence coordination + kaya polysemy

Roadmap §12.1 / plan-of-record §5.6, §6 Commit 7. SO clausal
coord + kaya naman two-word + comma-marked variants for all
four COORD values + naman lex.

### Comma-marked clausal coord made symmetric across COORD values

The comma-marked clausal coord (``Kumain si Maria, at pumunta
si Juan.``) is the more common written form. Pre-Phase-5k
Commit 1 commas were silently dropped; with the Commit 1 lex
they now require structural consumption. Commit 7 adds comma-
marked variants uniformly for AND / OR / BUT / SO so the
parametrization stays symmetric.

### kaya naman as fixed two-word coord

``kaya naman`` is a discourse-emphatic variant of plain
``kaya`` lifting DISCOURSE_EMPH=YES on the matrix.
``naman`` is consumed as a structural daughter (the new rule
shape ``S → S PART[COORD=SO] PART[ADV=ALSO] S``) rather than a
movable enclitic, because the kaya-naman two-word form is
fixed lexicalised.

### naman as non-clitic PART[ADV=ALSO]

``naman`` was ``_UNK`` pre-Commit 7. The plan §4.3 incorrectly
assumed it was already enclitic; the audit caught the gap. Adds
naman as ``pos: PART, feats: {ADV: ALSO, LEMMA: naman}`` —
NON-clitic. Treating naman as a clitic here would trigger
``reorder_clitics`` to pull it into one of the adjacent
matrix-V's post-position, breaking the kaya-naman adjacency.
Free-standing naman (``Kumain naman ako``) is a separate
construction deferred to a follow-on.

### kaya polysemy resolved without cross-fire

The pre-existing PSYCH-VERB ``kaya`` ("be able to") fires only
on ``Kaya <pron>ng V`` (4-token control-wrap shape); the new
PART[COORD=SO] reading fires only when sandwiched between two
complete S clauses. Audit (2026-05-07): all ~16 pre-existing
``kaya`` corpus entries are PSYCH-control 4-token forms; none
match the binary-S-coord shape. Baseline zero-diff confirmed.

## Phase 5k Commit 8: asymmetric NP coord + negation × coord

Roadmap §12.1 / plan-of-record §5.7, §5.8, §6 Commit 8.

### COORD=BUT_NOT distinct from BUT

Asymmetric coord (``Si Maria, hindi si Juan``) is structurally
distinct from symmetric adversative (``X pero Y``): no symmetric
coord PART; ``hindi`` itself fills the connective slot; the
second conjunct is the NEGATED alternative. Marking with
COORD=BUT_NOT (distinct from BUT) makes the asymmetry visible
to downstream consumers.

### Defining (↓4 POLARITY) = 'NEG' on the rejected conjunct

The asymmetric rule sets POLARITY=NEG on the second conjunct's
f-structure as a defining equation, marking the rejected
alternative inside the conjunct itself rather than only on the
matrix. The matrix's COORD=BUT_NOT and the conjunct's
POLARITY=NEG together give downstream consumers two ways to
detect the rejection.

### Negation × clausal coord — local-scoping reading

Phase 4 §7.2 hindi-wrap composes with the inner conjunct S
unchanged (no new rule). ``Hindi kumain si Maria at pumunta si
Juan.`` parses as ``[hindi kumain si Maria] AND [pumunta si
Juan]`` with POLARITY=NEG only on the first conjunct. Cross-
conjunct scoping (``Hindi [si Maria at si Juan] kumain.``
"Neither X nor Y") is a deferred follow-on — the
local-scoping reading is the baseline.

## Phase 5k Commit 9: N-level coord + interaction tests

Roadmap §12.1 / plan-of-record §6 Commit 9.

### N-level coord enables coord × HAVE

The Phase 5j HAVE rules take bare-N as the existence-asserted
daughter (``S → PART[EXISTENTIAL=YES] N NP[CASE=NOM]``); the
Phase 5k Commit 3 NP-level coord rules produce NP[CASE=X], not
bare N. Without N-level coord ``May aklat at lapis si Maria.``
0-parsed because ``aklat at lapis`` couldn't reduce to a single
N. Two new rules (``N → N PART[COORD=Y] N`` for Y ∈ {AND, OR})
restore the composition.

### Bare-N matrix is case-less by design

No CASE on the matrix N — bare N has no case marker. Consumed
by HAVE (which sets EXISTENTIAL/CLAUSE_TYPE on its own matrix)
or by the case-marker → NP projection (``ng aklat at lapis``
"of book and pencil" — single case marker spans coord-N).

## Phase 5l Commit 1: subordinator + sana lex inventory

Roadmap §12.1 / plan-of-record §4.1, §6 Commit 1.

### kung carries two PART entries (INTERROG + COND)

Phase 5i lex'd ``kung`` as ``PART[COMP_TYPE=INTERROG]`` for
indirect-Q embedding. Phase 5l Commit 1 adds a **second** lex
entry ``PART[COMP_TYPE=COND]`` for conditional subordination.
Both surface in the morph analyzer's output for the bare
``kung`` token; the chart picks the right entry from rule
context (sentence-initial / matrix-adjunct vs post-V[ASK]).
Same precedent as Phase 5j ``kailangan`` and Phase 5k ``kaya``
— two lex entries with different feats; rule context
disambiguates without cross-fire.

### para and dahil polysemy by POS

``para`` and ``dahil`` already exist as PREP entries (Phase 5e
Commit 3). Phase 5l adds NEW PART entries with
``COMP_TYPE=PURP`` and ``COMP_TYPE=REAS`` for the S-taking
subordinator readings. Polysemy is resolved by POS — the
chart picks PREP for NP complements, PART for S complements.
Same precedent as Phase 5j ``wala`` (existential PART vs
locative VERB).

### sana as 2P enclitic, not subordinator

``sana`` "would have / hopefully" is a 2P Wackernagel enclitic
that marks the matrix S as counterfactual. Lex'd as
``PART[is_clitic=true, CLITIC_CLASS=2P, COUNTERFACTUAL="YES"]``
(CLITIC_CLASS=2P added in Commit 5 once the lift rule landed);
cluster priority 195 in ``data/tgl/clitics.yaml``.

## Phase 5l Commit 2: matrix attachment + conditional builder

Roadmap §12.1 / plan-of-record §5.1, §6 Commit 2.

### Subord clause as ADJUNCT with f-structure identity overlay

A SubordClause is built by ``SubordClause → PART[COMP_TYPE=X] S``
with ``(↑) = ↓2`` (the SubordClause f-structure IS the inner
S's f-structure) plus ``(↑ SUBORD_TYPE) = '<X>'`` (the
subord-type marker is overlaid). Then the matrix attachment
rules (``S → S SubordClause`` post; ``S → SubordClause
PUNCT[PUNCT_CLASS=COMMA] S`` pre) lift the SubordClause as a
member of the matrix's ``ADJUNCT`` set.

The matrix S's PRED / SUBJ / OBJ all come from its own inner
clause; the SubordClause's f-structure (with its SUBORD_TYPE
marker on top) joins ADJUNCT.

### Pre-matrix and post-matrix produce identical f-structures

Only the c-tree differs (3 daughters vs 2). The Phase 5k comma
lex (``PUNCT[PUNCT_CLASS=COMMA]``) is the structural daughter
for the pre-matrix form; pre-matrix subord without a comma is
not in scope (corpus convention).

### SUBORD_TYPE-agnostic matrix attachment

The two attachment rules reference bare ``SubordClause`` (no
SUBORD_TYPE constraint). Subsequent Phase 5l commits add only
new SubordClause-builder rules; the attachers stay generic and
admit every SUBORD_TYPE family without modification.

## Phase 5l Commit 3: kung polysemy resolution (no rules)

Roadmap §12.1 / plan-of-record §6 Commit 3.

### Disjoint contexts prevent cross-fire

``kung[INTERROG]`` is consumed only by ``cfg/control.py``
``S_INTERROG_COMP`` (which constrains its inner S to
``Q_TYPE=WH``); ``kung[COND]`` is consumed only by
``cfg/subordination.py`` ``SubordClause`` (whose daughter
pattern is ``PART[COMP_TYPE=COND]``). The two paths fire in
disjoint syntactic contexts. There is no known sentence that
produces both a COND and an INTERROG parse.

## Phase 5l Commit 5: counterfactual sana enclitic + Rule C lift

Roadmap §12.1 / plan-of-record §5.6, §6 Commit 5.

### Rule C parallels Rule B (ba Q_TYPE lift)

The Phase 4 §7.3 generic 2P-clitic absorption rule (Rule A)
lands a clitic in the matrix's ADJ set; for clitics whose
feature should ALSO appear at the clause level, a parallel
rule with a literal ``(↑ FEAT) = 'value'`` lift fires
instead. Phase 5i Commit 5 added Rule B for ``ba``
(``(↑ Q_TYPE) = 'YES_NO'``); Phase 5l Commit 5 mirrors this
with **Rule C** for ``sana``
(``(↑ COUNTERFACTUAL) = 'YES'``). Rule A is tightened with
``¬ (↓2 COUNTERFACTUAL)`` so the three rules are mutually
exclusive by precondition.

## Phase 5l Commits 6 / 7: temporal subord builders

Roadmap §12.1 / plan-of-record §5.3, §6 Commits 6 + 7.

### Five temporal SUBORD_TYPE values

Each ``COMP_TYPE=TEMP_<X>`` PART feeds its own SubordClause-
builder rule. Five SUBORD_TYPE values cover the temporal-subord
set: TEMP_BEFORE / TEMP_AFTER / TEMP_WHILE / TEMP_UNTIL /
TEMP_SINCE.

### mula nang is a multi-word lexicalised subordinator

The rule ``SubordClause → PREP[PREP_TYPE=SOURCE]
PART[COMP_TYPE=TEMP_SINCE] S`` reuses the existing Phase 5e
``mula`` PREP entry (PREP_TYPE=SOURCE) — no new lex for
``mula`` — combined with the Commit 1 ``nang`` PART entry.
``PREP_TYPE=SOURCE`` uniquely identifies ``mula`` among the
four Phase 5e PREPs. The chart admits ``mula sa NP`` (PP) and
``mula nang S`` (SubordClause) via different structural shapes
— no interference.

## Phase 5l Commits 8 / 9: PURP and REAS with PREP/PART polysemy

Roadmap §12.1 / plan-of-record §5.4 / §5.5.

### Polysemy resolution by immediate constituent

``para`` (Commit 8) and ``dahil`` (Commit 9) compose with the
right reading per immediate-constituent context: PREP path
takes a DAT-NP; PART path takes an S. No special
disambiguation logic needed beyond the category-pattern
matching.

## Phase 5l Commits 10 / 11: SAY_CLASS / ASK_CLASS lex tagging

Roadmap §12.1 / plan-of-record §5.7, §6 Commits 10 + 11.

### Indirect speech parsing deferred

Plan §1 / §2 assumed the Phase 4 ``na``-linker complement
admits a finite-S complement of report-class verbs
(``Sinabi niya na pumunta si Maria.``). Recon revealed no such
grammar rule exists; the canonical sentence returns 0 parses.
Building the OV-with-na-S complement rule requires non-trivial
interaction work — the said-thing fills the SUBJ slot but is a
finite-S, conflicting with LFG completeness / coherence on the
standard OV a-structure. Deferred to a Phase 5l follow-on or
Phase 6 (functional uncertainty).

Commits 10 / 11 deliver: SAY_CLASS=YES (on ``sabi``) and
ASK_CLASS=YES (on ``tanong``) lex tagging in
``data/tgl/verbs.yaml``, propagating onto inflected forms via
the paradigm engine. The diagnostic feats are available for
any future parsing rule that gates on report / ask class.

### ASK-class reported-Q misanalyzes today

``Tinanong niya kung sino ang kumain.`` parses via the
Phase 5l COND-adjunct path. The correct semantic reading
("He asked who ate") needs the Phase 5i ``S_INTERROG_COMP``
path, which requires ``CTRL_CLASS=KNOW`` on the matrix V;
``tanong`` carries ``CTRL_CLASS=NONE``. Pinned as a known
limitation; flipping
``test_phase5l_reported_q.py::TestReportedQMisanalysisDeferred``
is the trigger for follow-on work.

## Phase 5l Commit 13: ay-fronted SubordClause topic + interactions

Roadmap §12.1 / plan-of-record §5 (extended at sign-off) /
§6 Commit 13.

### Ay-fronted SubordClause as TOPIC + ADJUNCT

The new rule ``S → SubordClause PART[LINK=AY] S`` lifts the
fronted SubordClause as the matrix's TOPIC and adds it as an
ADJUNCT member, parallel to Phase 4 §7.4 NP ay-fronting.

### Interaction coverage without new rules

Subord nesting (depth 2), subord on coord-S matrix, coord-S
inside subord, multiple subords on same matrix, and sana
clitic inside a subord clause all compose without additional
grammar — the matrix-attachment rules from Commit 2 are
SUBORD_TYPE-agnostic and recursive, and the Phase 5k coord
output is an S that the attachers fire on without modification.

## Phase 5l Commit 14: correlative coordination

Roadmap §12.1 / plan-of-record §5 (extended at sign-off) /
§6 Commit 14.

### CORREL=YES distinguishes correlative from asymmetric

The matrix carries ``COORD=BUT_NOT`` (sharing the value used
for Phase 5k asymmetric NP-coord ``X, hindi Y``) plus
``CORREL=YES`` for the kundi-pati forms. ``pati`` is consumed
structurally — its ALSO_INCL marker doesn't propagate onto
the matrix.

### Three rules for three structural variants

(a) Canonical 5-daughter ``S , kundi pati S``; (b) no-comma
4-daughter ``S kundi pati S``; (c) no-pati 4-daughter
``S , kundi S``. Rules (a) and (b) lift CORREL=YES; rule (c)
only lifts COORD=BUT_NOT.

## Phase 5m Commit 1: discourse / register / indefinite lex inventory

Roadmap §12.1 / plan-of-record §4. Twenty-five new lex entries
across ``data/tgl/particles.yaml``, ``data/tgl/pronouns.yaml``,
and ``data/tgl/nouns.yaml``. Eight construction families covered:
politeness 2P clitics, modal/mood particles, discourse connectives
(single- and multi-word components), emphatic post-N particle,
frequency adverbs, negative-indefinite PRON, answer interjections,
and reflexive NOUN. Lex-only commit; no grammar / analyzer changes.

### YAML-boolean trap on PRED feat

The first attempt at lex'ing ``opo`` used ``PRED: "'YES'"`` (5-char
string with literal single-quotes), producing a malformed equation
``(↑ PRED) = ''YES''`` (empty-string ''+ YES + ''). The second
attempt ``PRED: YES`` (no quotes) parsed as Python ``True`` under
PyYAML 1.1, then was filtered out by the lex-equation builder's
string-only filter. The correct form is ``PRED: "YES"`` (3-char
quoted string). Fixed retroactively in Commit 3 for opo / oho /
sinuman.

### paminsan-minsan tokenization

Hyphenated reduplicated forms tokenize as three tokens
(``paminsan`` ``-`` ``minsan``). The parse-pipeline merger collapses
``X-Y`` to ``XY`` for analyzer lookup (Phase 5f Commit 14
``tag-init`` precedent). The Commit 1 lex surface is the joined
form ``paminsanminsan``; the LEMMA preserves the canonical
hyphenated user-visible form.

## Phase 5m Commit 2: politeness po/ho 2P-clitic absorption (Rule D)

Roadmap §12.1 / plan-of-record §5.1. Adds Rule D in
``cfg/clitic.py`` parallel to Rules B (``ba`` Q_TYPE lift) and
C (``sana`` COUNTERFACTUAL lift):

```text
S → S PART[CLITIC_CLASS=2P, REGISTER=POLITE]
    (↑) = ↓1
    ↓2 ∈ (↑ ADJ)
    (↓2 CLITIC_CLASS) =c '2P'
    (↓2 REGISTER) =c 'POLITE'
    (↑ REGISTER) = 'POLITE'
```

A parallel rule fires on ``REGISTER=COLLOQUIAL_POLITE`` for
``ho``. Rule A gains ``¬ (↓2 REGISTER)`` for mutual exclusion.
The four absorption paths (A generic, B ba, C sana, D po/ho) are
disjoint by precondition.

### Plan deviation

Plan §2 had asserted Rule A would lift REGISTER without
modification. That was wrong — Rule A absorbs into ADJ but lifts
no feats. Rule D pattern is the correct mechanic.

### Fragment-host limitation pinned

``Salamat po`` / ``Oo po`` / ``Hindi po`` 0-parse: no Phase 4
fragment-answer matrix-S infrastructure for one-word noun
fragments hosting a 2P clitic. The 2P-clitic absorption rule has
no S to attach to. Pinned in
``test_phase5m_politeness_clitic.py::TestFragmentHostDeferred``;
Phase 5n debt.

## Phase 5m Commit 3: opo/oho fragment-answer interjection rule

Roadmap §12.1 / plan-of-record §1. Adds a new rule in
``cfg/clause.py``:

```text
S → PRON
    (↑) = ↓1
    (↑ INTERJ) =c 'YES'
    (↑ ANSWER) =c 'AFFIRM'
    (↑ CLAUSE_TYPE) = 'FRAGMENT_ANSWER'
```

The PRON's REGISTER (POLITE / COLLOQUIAL_POLITE) percolates to
matrix S via ``(↑) = ↓1``. Selectional restriction is tight —
only INTERJ=YES, ANSWER=AFFIRM PRONs fire (today: only opo /
oho).

### Plan deviation

Plan §1 had said composition would happen via "the existing
fragment-answer mechanism (parallel to oo / hindi PRON entries)".
That was wrong — ``oo`` is not lex'd, ``hindi`` is PART
[POLARITY=NEG] not PRON, and there was no fragment-answer rule.
Built the 5-line rule rather than reduce scope to lex-only
delivery.

### Oo. / Hindi. deferred

Standalone ``Oo.`` / ``Hindi.`` answer clauses 0-parse: ``oo`` is
unlex'd; ``hindi`` is PART, not PRON[INTERJ=YES]. Closure path
needs new PRON entries plus parallel ANSWER=NEG rule for hindi.
Phase 5n debt.

## Phase 5m Commit 4: sentence-initial sentential-ADV rule

Roadmap §12.1 / plan-of-record §5.1. Adds a single rule in
``cfg/discourse.py`` shared between modal/mood particles
(``siguro`` / ``marahil``) and discourse connectives
(``samakatuwid`` / ``gayunpaman``, plus the multi-word virtuals
from Commit 11):

```text
S → PART S
    (↑) = ↓2
    ↓1 ∈ (↑ ADJUNCT)
    (↓1 DISCOURSE_POS) =c 'SENTENCE_INITIAL'
```

The shared ``DISCOURSE_POS=SENTENCE_INITIAL`` gate covers both
EPISTEMIC (modal-mood) and DISCOURSE (connective) families
without proliferating rule shapes.

### EPISTEMIC / DISCOURSE stay on the ADJUNCT member

The rule lifts the ``↓1`` PART into the matrix's ADJUNCT set
without copying its EPISTEMIC / DISCOURSE feat to the matrix.
Contrast with Phase 5l Rule C / Phase 5m Rule D which DO lift
COUNTERFACTUAL / REGISTER — those are clausal-mood properties.
Modal and discourse markers are inherently adjunct-scoped.

### Clause-medial siguro / marahil deferred

``Pumupunta siguro siya.`` (clause-medial epistemic particle) is
attested but rare. Phase 5m's sentence-initial-only analysis
doesn't cover it; Phase 5n inventory pass may add a polysemous
2P-clitic entry.

## Phase 5m Commit 5: frequency adverbs (no new grammar)

Roadmap §12.1 / plan-of-record §1, §4.2. Five new ADV[ADV_TYPE=
FREQUENCY] entries route through the existing Phase 5f Commit 5
sentential-FREQ rule (``S → S AdvP[FREQUENCY]``). New ``FREQ_VALUE``
feat (HIGH / HABITUAL / SOMETIMES / OCCASIONAL) is diagnostic only.

### paminsan-minsan tokenization

Hyphenated; lex'd at the joined form ``paminsanminsan`` so the
merger collapses tokens before lookup. LEMMA preserves the
canonical hyphenated form for downstream consumers.

## Phase 5m Commit 6: reflexive sarili NP composition (no new grammar)

Roadmap §12.1 / plan-of-record §1, §2 (analytical commitment 4).
``sarili`` lex'd as NOUN[SEM_CLASS=REFLEXIVE] in
``data/tgl/nouns.yaml``. Composes as ``D + N + GEN-PRON`` via
existing Phase 4 NP grammar.

### SEM_CLASS stays on the morph layer

Like Phase 5f ``beses`` / ``ulit`` / ``doble``, the SEM_CLASS feat
is available to grammar-rule constraining equations but is NOT
propagated to f-structure. This matches the existing convention.
Pinned in ``TestSemClassReflexiveOnMorph`` as a regression marker.

### Anaphora resolution deferred

Binding ``sarili NIYA`` to its antecedent SUBJ via inside-out
designators is Phase 6 work. Phase 5m only does the c-structure
composition.

## Phase 5m Commit 7: emphatic mismo post-N rule

Roadmap §12.1 / plan-of-record §5.3. Adds one rule in
``cfg/nominal.py``:

```text
NP → NP PART
    (↑) = ↓1
    ↓2 ∈ (↑ ADJUNCT)
    (↓2 EMPHATIC) =c 'YES'
    (↓2 LEMMA) =c 'mismo'
    (↑ EMPHATIC) = 'YES'
```

Distribution: post-NP only — pre-NP attachment is ungrammatical.
The dual constraint (EMPHATIC=YES + LEMMA=mismo) prevents cross-
fire from the existing ``nga`` 2P clitic (also EMPHATIC, but a
different syntactic slot).

## Phase 5m Commit 8: indefinite kahit + wh productive

Roadmap §12.1 / plan-of-record §5.4. Adds two parallel productive
rules in ``cfg/nominal.py``:

```text
PRON → PART[LEMMA=kahit] PRON[WH=YES]   (IndefPRON)
ADV  → PART[LEMMA=kahit] ADV[WH=YES]    (IndefADV)
    (↑) = ↓2
    ↓1 ∈ (↑ ADJUNCT)
    (↑ INDEF) = 'YES'
    (↓1 LEMMA) =c 'kahit'
    (↓2 WH) =c 'YES'
```

The ``LEMMA=kahit`` constraint excludes other CONC particles
(``bagaman``) from firing as indef-builders. The ``WH=YES``
constraint matches the actual lex-feat name (plan §5.4 had said
``Q_TYPE=WH``; corrected here to match the lex).

### Disambiguation with Phase 5l concessive kahit

The chart picks by daughter category: S → SubordClause path
(Phase 5l); PRON / ADV → Indef path (Phase 5m). Deterministic;
no rule cross-fire.

### Two deferrals pinned

- **kahit saan / kahit kailan as clause-level adjuncts**: the
  IndefADV rule produces ADV[INDEF=YES, ADV_TYPE=LOCATION/TIME]
  but no clause-final LOCATION/TIME ADV adjunct rule exists today
  (Phase 5f Commit 5 covers FREQUENCY only). Phase 5n debt.
- **Pre-V kahit-X SUBJ** (``Kahit sino kumain.``): needs an indef-
  PRON-as-fronted-topic rule analogous to Phase 5l SubordClause-
  topic. Phase 5n debt.

## Phase 5m Commit 9: negative-indefinite walang + sinuman

Roadmap §12.1 / plan-of-record §1. Adds a new rule in
``cfg/clause.py`` mirroring the existing Phase 5j ``walang N``
rule with a PRON[INDEF=NEG_INDEF] daughter:

```text
S → PART[EXISTENTIAL=YES, POLARITY=NEG]
    PART[LINK=NG]
    PRON[INDEF=NEG_INDEF]
```

### Plan deviation

Plan §1 had said "Phase 5m only adds the lex entry for sinuman;
no new grammar". That was wrong — the existing Phase 5j ``walang
N`` rule constrains specifically on N daughter and doesn't admit
PRONs. The minimum delta is one new rule.

### Two deferrals pinned

- **Walang sinumang dumating.**: sinuman + bound -ng + V[finite]
  RC complement; needs PRON-headed RC infrastructure. Phase 5n
  debt.
- **Walang ano man.** / **anuman**: productive ``wh-PRON + man``
  indef-builder + ``anuman`` lexicalized contracted form. Phase
  5n debt.

## Phase 5m Commit 10: single-word discourse connectives (no new grammar)

Roadmap §12.1 / plan-of-record §5.1. The Commit 1 lex entries
``samakatuwid`` (DISCOURSE=THEREFORE) and ``gayunpaman``
(DISCOURSE=HOWEVER) feed the Commit 4 sentence-initial PART rule
via the shared DISCOURSE_POS=SENTENCE_INITIAL gate. No new grammar
in this commit.

## Phase 5m Commit 11: multi-word discourse connectives

Roadmap §12.1 / plan-of-record §5.2. Adds three multi-word
lexicalized rules in ``cfg/discourse.py`` building virtual PART
nodes from two-token sequences:

```text
PART → PART[LEMMA=gayon] PART[LEMMA=din]   (DISCOURSE=LIKEWISE)
PART → PART[LEMMA=ganon] PART[LEMMA=din]   (DISCOURSE=LIKEWISE)
PART → PART[LEMMA=bukod] ADP[CASE=DAT, DEIXIS=PROX, DEM=YES]
                                            (DISCOURSE=ALSO)
```

Each emitted virtual PART carries DISCOURSE_POS=SENTENCE_INITIAL
so the Commit 4 rule consumes them. Same precedent as Phase 5l
``mula nang`` (multi-word subordinator).

### Mixed-POS daughters in bukod-dito

``dito`` is the locative DEM (ADP), not a PART. The bukod-dito
rule uses PART + ADP daughters. The dito daughter is identified
via category-pattern constraints rather than a LEMMA equation —
adding LEMMA to the existing dito ADP entry conflicts with the
``(↑ LEMMA) = ↓3 LEMMA`` equation in the Phase 5g pre-mod
demonstrative rule (matrix-LEMMA double-assignment).

### YAML-bool trap on DEM=YES

PyYAML 1.1 parses unquoted ``YES`` as Python ``True``. The
``=c 'YES'`` constraining equation does NOT match a boolean True;
the category-pattern matcher DOES. The bukod-dito rule uses the
category-pattern form ``ADP[CASE=DAT, DEIXIS=PROX, DEM=YES]``.

### gayon din / ganon din architectural deferral

``din`` is a 2P clitic. The Phase 4 §7.3 ``reorder_clitics`` pre-
pass moves it to clause-final position before grammar parsing,
breaking the multi-word rule's adjacency requirement. The 3
grammar rules are landed; closure is a pre-clitic-reorder phrase-
recognition pass that merges ``gayon din`` / ``ganon din`` into
single tokens. Phase 5n debt.

## Phase 5m Commit 12: coverage corpus expansion

Roadmap §12.1 / plan-of-record §7.2. +20 fixtures in
``coverage_corpus.yaml`` sampling each Commit 2-11 family.
Baseline recaptured: 1332 → 1352 top-1 captures (+20); 6 historic
non-parses preserved.

## Phase 5n.A: §18 deferral debt-clearing (overview)

Plan-of-record ``tgllfg-phase-5n.md`` §3. Phase 5n.A closes 17
§18.1 deferrals across phases 5d-5m via 32 commits. The phase
has no thematic unity beyond "close the backlog"; analytical
commitments are recorded per Commit-N below. Five deferrals are
explicitly carried to Phase 5n.B (Phase 5h/5i/5m completions);
five more — L29 DV PFV gap, L77 gapping, L78 cross-conjunct
negation, L83 standalone NP-coord, and the parser non-conflict-
matcher fix unblocking 5+-conjunct flat coord — are bucketed for
Phase 5n.C per user direction.

Two cross-cutting analytical decisions warrant explicit
documentation:

**Drill-down protocol** (per user direction 2026-05-08): no new
deferrals from Phase 5n.A unless the scope is genuinely Phase 6+
infra-dependent. When a commit's targeted closure surfaces an
adjacent issue, the in-commit work expands to cover it. Examples:
Commit 7 surfaced the depictive PRON+linker+ADV rule (added in-
commit); Commit 8 surfaced 3 new rules for the R&G combined
essay paragraph (all added); Commit 17 surfaced the equation-
language-has-no-arithmetic constraint (decided in-commit per
Phase 5f Commit 9 precedent).

**Non-conflict matcher project finding** (Commit 19 / 19a):
the tgllfg Earley parser's category-pattern matcher historically
accepted ``Cat[X=Y]`` daughters that lacked the ``X`` feature
on the candidate, deferring rejection to constraining-equation
unification. This worked for low-arity rules but polluted the
chart at high arity (5+-conjunct flat NP coord 0-parsed despite
correct recursive infrastructure because every binary parse path
ambiguously matched the Phase 5m mismo NP-emphatic rule and got
rejected at unification). **Closed in Phase 6.C (2026-05-12):**
the matcher was replaced with feature-presence-required
(graph-constraint) matching per K&Z 1989 §3 c-structure
faithfulness. Every cfg/ module's LHS feat-set was audited
to advertise the features it supplies; the strict matcher prunes
the spurious binary fanout at predict time. 5+-conjunct flat NP
coord unlocked without any new rules (the recursive
``NP_LONG_LIST_<case>`` infrastructure from Commit 19a composed
unchanged).

The same pattern surfaced in Commit 29 (kita-fusion was firing on
any GEN-PRON via the same non-conflict leak); there the scope
was tractable for an in-commit fix (``(↓2 KITA) =c 'YES'``
constraining equation on all 3 kita rule variants), which
load-bearingly suppressed the Phase 5l COND-adjunct misanalysis
path for ASK-class reported-Q.

## Phase 5n.A Commit 1: Be-X-root verbal-paradigm pruning (§18 L35)

Nine non-verbal "be-X" roots (``bingi``, ``bulag``, ``galit``,
``ginaw``, ``gulat``, ``gutom``, ``hilo``, ``tibay``, ``tigang``)
were removed from ``verbs.yaml`` and re-lex'd in
``adjectives.yaml`` with ``affix_class: [ma_adj]``. Four roots
(``ganda``, ``bilis``, ``lakas``, ``yaman``) stayed in
``verbs.yaml`` slimmed to ``[um]``-only (they admit
``maganda + um → gumanda`` "become beautiful" inchoative use).
The migration removes ~50 spurious verbal-paradigm cells from
the seed lex.

## Phase 5n.A Commit 2: hindi-wrap × non-``ka`` NOM-clitic (§18 L69)

Added ``is_clitic: true`` to the full NOM-PRON inventory
(``ako``, ``tayo``, ``kami``, ``kayo``, ``siya``, ``sila``).
Added a ``_is_pre_ay_pron`` exception to clitic placement so the
ay-inversion path doesn't pull these into the post-``hindi``
position. Generalised ``_find_verbless_anchor`` in
``clitics/placement.py`` to skip ALL PART tokens (not just
NEG-PART) so ``Hindi siguro siya kumain`` etc. anchors correctly.

## Phase 5n.A Commit 3: SAY/ASK paradigm propagation (§18 L91)

Misdiagnosis closure. SAY_CLASS / ASK_CLASS feats already
propagate uniformly through the paradigm engine; the apparent
gap was a test-side oversight. Tests-only commit confirming
the projection.

## Phase 5n.A Commit 4: orthographic-variant LEMMA-collapse extension (§18 L74)

Phase 5j Commit 7 introduced ``MorphAnalysis.lemma = feats.get(
"LEMMA", surface)`` for the particles branch of
``_build_index``. Commit 4 extended the same mechanic to four
other branches: pronouns, nouns, verbs (root + paradigm cells),
adjectives (bare-root + paradigm cells). Synthetic ``MorphData``
tests validate the extension without mutating seed YAML.

## Phase 5n.A Commit 5: mag-isa ADV depictive (§18 L60)

New ADV lex entry ``magisa`` with ``LEMMA: mag-isa, MAGISA:
YES``. The pre-existing ``merge_hyphen_compounds`` pre-pass
collapses ``mag-isa`` → ``magisa`` for analyzer lookup. New
``cfg/nominal.py`` rule
``NP[CASE=NOM] → PRON[CASE=NOM] PART[LINK=NG] ADV[MAGISA=YES]``
attaches the depictive secondary predicate to the SUBJ NP.

## Phase 5n.A Commit 6: naka- resultative ADJ paradigm (§18 L61)

New ``naka_resultative`` cell in ``adj_paradigms.yaml``; 5 new
ADJ entries opting in (``tira``, ``upo``, ``higa``, ``tayo``,
``tabi``). Generates surfaces ``nakatira`` / ``nakaupo`` /
``nakahiga`` / ``nakatayo`` / ``nakatabi`` parsed as
ADJ[NAKA=YES] at predicative position.

## Phase 5n.A Commit 7: mama / R&G simples #1, #3 (§18 L62 + L63)

New PRON entry ``mama`` (vocative / informal address). Added
the depictive PRON+linker+ADV rule needed by R&G simples #1 /
\#3 (one rule discovery in-commit per drill-down protocol).

## Phase 5n.A Commit 8: R&G combined essay (§18 L64)

Combined essay-paragraph parse. Drill-down surfaced 3 new rules
needed for full coverage: ADJ-with-depictive in
``cfg/nominal.py``, N-level RC wrap (``N → N
PART[LINK=N{A,G}] S_GAP``), and nasa-headed S_GAP variant in
``cfg/extraction.py``. All landed in-commit.

## Phase 5n.A Commit 9: maaari polysemous noun reading (§18 L65)

Lex-only addition: ``maaari`` as NOUN ("the possible /
possibility") alongside the existing PART/VERB[MODAL] entries.
Marginal in modern Tagalog; surfaces in formal / written
register (R&G 1981 §10).

## Phase 5n.A Commit 10: existential as RC head (§18 L66)

Tests-only verification. The Commit 8 N-level RC wrap delivered
the required infrastructure; Commit 10 documents the closure.

## Phase 5n.A Commit 11: modal stacking (§18 L67)

New nested-MODAL S_XCOMP rule in ``cfg/control.py``. Admits
``Dapat akong puwedeng kumain.`` "I should be able to eat."
The outer modal's XCOMP is itself a modal-headed S_XCOMP;
PRO fillers for the implicit args.

## Phase 5n.A Commit 12: hindi puwede standalone (§18 L68)

Modal-as-predicate rule in ``cfg/control.py``. Admits
``Hindi puwede.`` as a complete clause with PRO fillers for
SUBJ and XCOMP. Initial design used a literal ``MODAL <SUBJ>``
PRED template but conflicted with the lex's ``PUWEDE <SUBJ,
XCOMP>``; re-designed to provide PRO fillers for both implicit
args without overriding PRED.

## Phase 5n.A Commit 13: modal + sa-PP ADJUNCT in XCOMP (§18 L70)

New 2-daughter S_XCOMP variant in ``cfg/control.py`` admitting
``V[MODAL=YES] + S_XCOMP-with-DAT-PP-adjunct``.

## Phase 5n.A Commit 14: OV embedded V kainin (§18 L72)

New bare-OV cell in ``paradigms.yaml`` with ``MOOD=SOC`` for
``kainin`` / ``bilihin`` / ``inumin`` / ``gawahin``. Admits
``Maaari mong kainin ang isda.`` "You can eat the fish" (modal
\+ bare-OV-in-XCOMP).

## Phase 5n.A Commit 15: correlative ``hindi lang...kundi pati`` (§18 L75)

Tests-only closure. Phase 5l Commit 14 already delivered the
required correlative-coord infrastructure; Commit 15 documents
the closure.

## Phase 5n.A Commit 16: multi-word coord o kaya / at saka / at nang (§18 L76 + L82)

Three new multi-word coord combiner rules in
``cfg/coordination.py``: ``o kaya`` (COORD=OR + UNCERTAIN=YES),
``at saka`` (COORD=AND + SEQUENCE=YES), ``at nang``
(COORD=AND + RESULT=YES). Each composes via a multi-word
lexicalized rule that consumes the two-PART sequence
structurally.

## Phase 5n.A Commit 17: coordinated cardinals (§18 L79)

New NUM coord rule in ``cfg/coordination.py``:
``NUM[CARDINAL=YES] → NUM PART[COORD=AND] NUM`` recording the
operand cardinal values. The combined arithmetic value is NOT
computed — the equation language has no arithmetic operators
(per Phase 5f Commit 9 precedent); operand cardinals are
recorded for downstream consumers.

## Phase 5n.A Commit 18: bukod sa / maliban sa exceptive PP (§18 L80)

New PREP entries ``bukod`` and ``maliban`` in
``particles.yaml``. New clause-final EXCEPTIVE PP rule in
``cfg/discourse.py`` that attaches ``bukod sa NP`` /
``maliban sa NP`` as ADJUNCT[PREP_TYPE=EXCEPTIVE].

## Phase 5n.A Commit 19 / 19a: N-conjunct flat NP coord (§18 L85, L85+)

Commit 19 added explicit 4-conjunct rules (Oxford + non-Oxford
× NOM/GEN/DAT). Commit 19a refactored to a left-recursive
``NP_LONG_LIST_<case>`` non-terminal with base + recursive +
wrap rules. The 4-conjunct case fired via the base + wrap; 5+-
conjunct (L85+) was originally pinned at 0-parse.

**Original root-cause analysis** (per
``project_parser_nonconflict_matcher`` memory, now superseded):
the parser's category-pattern matcher was non-conflict. For
5+-conjunct, every binary parse path (Catalan C(N-1) parses)
ambiguously matched the Phase 5m mismo NP-emphatic rule
``NP → NP PART`` on each NP+PART adjacency, and the constraining
equations rejected them at unification, polluting every parse
path. For 4-conjunct (5 binary parses), at least one survived;
for 5-conjunct (14 binary parses), all 14 failed.

**Closed in Phase 6.C (2026-05-12)**: the matcher swap to
feature-presence-required (graph-constraint) matching prunes
the spurious binary fanout at predict time. The Commit 19a
recursive infrastructure composed unchanged for arbitrary N;
6 / 7-conjunct stress fixtures live in
``tests/tgllfg/test_phase5n_4conj_coord.py``. The matrix
``NP[CASE=X, COORD=AND]`` LHS on the 4+-wrap rules — added in
Phase 6.C C3b alongside the binary / 3-conjunct coord LHS
updates — supplies the COORD feature parents now require.

## Phase 5n.A Commit 20: disjunctive 3-conjunct flat NP coord (§18 L86)

Generalized the Phase 5k Commit 4 3-conjunct rules from AND-
only to AND/OR. Twelve rules total (Oxford + non-Oxford × NOM
/ GEN / DAT × AND / OR). NUM behaviour mirrors the binary forms:
AND forces ``(↑ NUM) = 'PL'``, OR percolates ``(↑ NUM) = ↓1
NUM`` (one underspecified referent).

## Phase 5n.A Commit 21: HAVE-mayroon-with-linker (§18 L87)

Two new clause rules in ``cfg/clause.py``: 5e (positive HAVE,
postposed possessor with linker) and 5f (positive HAVE,
internal clitic possessor with leading linker). Mirrors the
Phase 5j Commit 5c / 5d negative HAVE structure but with POS
polarity. Admits
``Mayroong aklat si Maria.`` and ``Mayroong akong aklat.``

## Phase 5n.A Commit 22: free-standing naman 2P enclitic (§18 L88)

Second ``naman`` lex entry added to ``particles.yaml``: a 2P
clitic with ``ADV: ALSO``, parallel to ``din``/``rin``. The
pre-existing non-clitic ``naman`` (Phase 5k Commit 7, used by
the ``kaya naman`` two-word coord) coexists with the new clitic
entry. Disambiguation: the 2P-clitic absorption rule's
``CLITIC_CLASS=2P`` daughter constraint selects the clitic
entry; the kaya-naman rule's structural context (PART
sandwiched between two complete S clauses with leading
``kaya``) selects the non-clitic entry.

## Phase 5n.A Commit 23: bagamat / 'pag orthographic contractions (§18 L94 + L107)

L94: new ``bagamat`` PART entry with feats
``{COMP_TYPE: CONC, LEMMA: bagaman, REGISTER: FORMAL}``;
the analyzer's MorphAnalysis.lemma collapses to canonical
``bagaman`` via the Phase 5j Commit 7 mechanic.

L107: existing ``pag`` entry's LEMMA updated from ``pag`` →
``kapag`` so all short forms (``pag``, ``'pag``) collapse to
the canonical ``kapag``. The ``'pag`` surface tokenizes as
``'`` + ``pag`` (apostrophe is a non-word char per
``text/tokenizer.py``); the apostrophe is filtered as
non-content and the ``pag`` lex matches the remainder.
Adding a literal ``'pag`` lex entry was rejected — the
tokenizer never yields a single ``'pag`` token.

## Phase 5n.A Commit 24: subord nesting depth-3+ stress fixtures (§18 L95)

Tests-only closure. The Phase 5l subord adjunct attachment
machinery already supports unbounded recursion; Commit 24 adds
explicit stress-test fixtures across depth-2 (5 fixtures one
per COMP_TYPE family), depth-3 (8 fixtures spanning COND ×
{TEMP, PURP, REAS, CONC} matrices and inverses), and depth-4
(2 fixtures with 3 nested subord adjuncts). Depth-4 sentences
parse but the f-structure may flatten one adjunct as a sibling
rather than a strict-nested daughter — acceptable per
plan-of-record §3.4 Commit 24 mitigation.

## Phase 5n.A Commit 25: pang- purpose nominals (§18 L27)

Hand-authored ``pang-`` (and ``pam-``/``pan-`` allomorph)
instrumental / purpose nominals, lex'd as NOUN with a
``PANG_DERIVED: true`` traceability feat. Six entries:
``pambili``, ``pamasahe``, ``pangharang``, ``pangkain``,
``pangsuot``, ``pansulat``. Productive ``pang-`` derivation
engine deferred to L31 (NOUN-root engine). Verified no
crossfire with the existing IV-INSTR ``ipang-`` paradigm
(``ipinambili`` etc.) — POS-typed differently.

## Phase 5n.A Commit 26 / 27: OV-with-na-S indirect-speech (§18 L89)

Commit 26: 12 corpus fixtures spanning OV PFV/IPFV/CTPL of
``sabi`` × clitic-GEN-PRON actors × AV-intransitive /
AV-transitive embeds. Pinned at ``expected: fragment``;
Commit 27 lifts the pin.

Commit 27: new clause rule
``S → V[VOICE=OV, SAY_CLASS=YES] PRON[CASE=GEN] PART[LINK=NA] S``
binding the said-thing to SUBJ via the OV LMT THEME→SUBJ
mapping, and the actor PRON to OBJ-AGENT. Companion change in
``clitics/placement.py``: new ``is_say_class_pron_seq`` branch
in ``disambiguate_homophone_clitics`` so ``na`` between SAY-V
\+ GEN-PRON + V stays as the linker (not the ALREADY clitic).
Without the disambiguator change, ``reorder_clitics`` was
moving ``na`` to clause-final position, breaking the rule's
V-PRON-na-S adjacency.

Gating choices:

- SAY_CLASS=YES on ↓1 — narrow gate preserving Phase 4
  SUBJ-as-NOM-NP default for non-SAY OV verbs.
- PRON[CASE=GEN] (not full NP[CASE=GEN]) — sidesteps the
  N-headed RC-linker ``na`` path which misanalyzes
  ``Sinabi ng lalaki na pumunta si Maria.`` as
  ``[ng lalaki] [na pumunta]``.

## Phase 5n.A Commit 28 / 29: ASK-class reported-Q (§18 L90 + L92)

Commit 28: 18 corpus fixtures spanning ``tanong`` × OV/AV ×
PFV/IPFV/CTPL × wh-PRONs (sino, ano, saan, kailan, bakit,
paano). 10 OV-clitic fixtures pinned at COND-misanalysis
(parsing via the Phase 5l COND-adjunct path with
``SUBORD_TYPE=COND`` instead of the correct
``COMP_TYPE=INTERROG``); 8 AV / full-NP fixtures pinned at
``expected: fragment``. Commit 29 lifts both pin shapes.

Commit 29 lands two coordinated changes:

**Two new clause rules in cfg/control.py** — ASK-class
reported-Q for OV pivot (asked-thing as SUBJ, asker as OBJ-
AGENT) and AV pivot (asker as SUBJ, asked-thing as OBJ). Both
gated on ``(↓1 ASK_CLASS) =c 'YES'``. NP[CASE=X] subsumes
clitic-PRON via the existing ``NP → PRON`` shells, so a single
rule per voice covers both clitic-PRON and full-NP actors.

**kita-fusion non-conflict-matcher leak closure (cfg/clitic.py)**
— added ``(↓2 KITA) =c 'YES'`` constraining equations to all 3
kita rule variants. The rules synthesise SUBJ.PERS=2 /
OBJ-AGENT.PERS=1 without binding ↓2's f-structure, so the
non-conflict matcher was admitting any GEN-PRON via shared-key
absence (no constraint to reject ``niya`` etc.). The spurious
kita-S over ``Tinanong niya`` was the matrix S that the
COND-adjunct rule was attaching to; killing the spurious S
removed the misanalysis path entirely — no need for a guard on
the COND-adjunct rule itself. This was an unanticipated
load-bearing fix that closed L92 without explicit work.

Companion change in ``data/tgl/pronouns.yaml``: ``KITA: YES``
quoted to ``KITA: "YES"`` (string, not boolean) per the
``=c 'YES'`` convention used by ``MODAL: "YES"`` etc. The one
consumer (``test_kita_fusion.py::TestKitaMorph``) updated to
``== "YES"``.

## Phase 5n.A Commit 30: COND vs reported-Q vs indirect-speech disambiguation sweep

Regression-sweep commit. 24 tests across 5 classes
(TestCondAdjunctRegression, TestOtherSubordTypesUnchanged,
TestKnowIndirectQRegression, TestNoCrossPollination,
TestKitaStillFires) verifying the Commit 27 / 29 changes don't
regress existing Phase 5l COND-adjunct uses, Phase 5i KNOW-
class indirect-Q, or other-COMP-TYPE adjunct families, and
confirming no cross-pollination across the SAY / ASK / KNOW
rule families.

Baseline recapture: 1394 → 1410 corpus entries (will grow
again in Commit 31); 1388/1394 captured (6 are intentional
``expected: fragment`` / ``fail`` entries).

## Phase 5n.A Commit 31: coverage corpus expansion + baseline recapture

Per Phase 5m Commit 12 / 5l Commit 15 / 5k Commit 10 precedent.
+16 fixtures across the Commit 5/6/11/12/14/16/17/18/19/20/21/
22/23/24 constructions that didn't get corpus coverage in their
own commits, reaching 52 phase5n entries total (alongside the
36 from Commits 25/26/28). Baseline recaptured: 1394 → 1410
top-1 captures (+16); 1404/1410 captured.

## Phase 5n.C Commit 1: L78 wide-scope hindi over coord-NP — design (NEG_SCOPE feat)

**Date:** 2026-05-10 (Phase 5n.C).
**Status:** design. Implementation lands in Phase 5n.C Commit 2;
fixtures + baseline in Commit 3.

### Decision

A new f-structure feature ``NEG_SCOPE`` (single value: ``WIDE``)
marks the matrix S of a clause where ``hindi`` takes scope over a
coordinated NP. The default reading (no ``NEG_SCOPE`` on the matrix)
is narrow scope, consistent with the existing Phase 4 §7.2
hindi-wrap rule's behaviour. ``NEG_SCOPE`` is set only by the new
wide-scope rule introduced in Commit 2; the existing hindi-wrap rule
in ``cfg/negation.py`` is unchanged.

The new wide-scope rule (Commit 2 implementation forecast) attaches
``hindi`` at the matrix above a coord-NP SUBJ, e.g. for
``Hindi kumain si Maria at si Juan.`` "Neither Maria nor Juan ate":

```text
S → PART[POLARITY=NEG] V NP[CASE=NOM, COORD=AND]
  ↑ = ↓2
  (↑ POLARITY) = 'NEG'
  (↑ NEG_SCOPE) = 'WIDE'
  (↑ SUBJ) = ↓3
  (↓1 POLARITY) =c 'NEG'
  (↓3 COORD) =c 'AND'
```

Mirror rules cover ``COORD=OR`` (semantics: ``¬(M ate ∨ J ate)``;
both AND- and OR-coord yield "neither" semantics under wide-scope
negation, by De Morgan).

The pre-V word order ``Hindi [si Maria at si Juan] kumain.`` is
non-canonical without ay-fronting; if corpus pressure surfaces it,
an ay-fronted variant is added separately. The post-V form is the
canonical L78 surface.

### Why a single feature, not two

Two alternatives were considered:

1. **Two separate boolean features** (``NEG_NARROW`` /
   ``NEG_WIDE``). Rejected — the readings are mutually exclusive
   structurally (the wide-scope rule produces one f-structure;
   the existing narrow-scope hindi-wrap path produces another).
   A single feat captures the disjunction without redundancy.

2. **Three-valued ``NEG_SCOPE`` (``WIDE`` / ``NARROW`` /
   ``UNSPECIFIED``).** Rejected — there is no construction that
   would assert ``UNSPECIFIED`` distinct from "feat absent". The
   narrow reading is the default behaviour of every existing
   hindi-wrap path; absence on the matrix already encodes
   "narrow / not wide / no relevant coord interaction".

Single-value (``WIDE`` only) follows the codebase convention for
binary marker feats: ``EMPHATIC=YES``, ``COUNTERFACTUAL=YES``,
``CARDINAL=YES`` etc. all encode presence-vs-absence rather than
two-valued. ``NEG_SCOPE=WIDE`` is the marker; the absence is the
default narrow reading.

### Interaction with Phase 5k coord-NP head feats

Phase 5k Commit 3 (``cfg/coordination.py:44``) propagates
``COORD``, ``CASE``, ``NUM`` from the daughter conjuncts to the
matrix coord-NP. The new wide-scope hindi rule attaches ABOVE the
matrix coord-NP — its NP daughter is the already-built coord-NP,
and ``NEG_SCOPE=WIDE`` lands on the matrix S, not on the
coord-NP. No conflict: the coord-NP's head feats stay where Phase
5k put them; the matrix S gains a new feat orthogonal to coord-NP
structure.

### Disambiguation from Phase 5k asymmetric coord (Commit 8)

The asymmetric coord rule (Phase 5k Commit 8,
``cfg/coordination.py:493``) handles ``Si Maria, hindi si Juan`` —
``hindi`` in third position acting as the asymmetric connective —
producing ``COORD=BUT_NOT`` on the coord-NP and a defining
``(↓4 POLARITY) = 'NEG'`` on the second conjunct's f-structure.
The new wide-scope rule is structurally distinct: ``hindi`` is at
the matrix left edge (or left edge of the post-V SUBJ slot, not
between two NPs), and the coord-NP carries ``COORD=AND/OR``
(symmetric). No structural overlap; both rules can coexist.

### Disambiguation from existing narrow-scope hindi-wrap

The existing Phase 4 §7.2 hindi-wrap rule (``cfg/negation.py:73``,
``S → PART[POLARITY=NEG] S``) wraps an inner S that already has a
COMPLETE f-structure. When that inner S contains a coord-NP SUBJ,
the wrap produces narrow-scope semantics: ``POLARITY=NEG`` on the
matrix without ``NEG_SCOPE`` set, encoding "the predicate over the
coord-SUBJ is negated as a unit, with the coord internal to that
predicate." Whether this composes with multi-clause coord
(``Hindi kumain si Maria at uminom si Juan.``) is unaffected by
this commit — multi-clause cases remain narrow per the
``cfg/coordination.py:355`` comment.

For surfaces where both wide- and narrow-scope readings are
structurally available (e.g. coord-SUBJ post-V), both parses are
admitted; the wide-scope parse carries ``NEG_SCOPE=WIDE``, the
narrow-scope parse does not. Ranker disambiguation per Phase 4
§7.9 heuristics applies.

### Clitic-pronoun NOM SUBJ exclusion

Per S&O 1972 §10, the wide-scope reading is degraded /
ungrammatical when the coord-NP contains a clitic pronoun
(``siya`` / ``sila`` / ``ako`` / ``ka`` etc.) as a NOM SUBJ inside
the coord. Concretely, ``Hindi kumain si Maria at siya.`` resists
the wide-scope reading; only narrow scope or rephrasing (e.g.
``Hindi sila kumain.`` with a plural pronoun) is natural.

The constraint is enforced structurally: NOM clitic pronouns are
typed as ``PRON[CASE=NOM, CLITIC_CLASS=2P]`` and don't compose
into ``NP[CASE=NOM]`` via the Phase 5k coord rules — they have
their own pronominal-fronting / 2P-clitic absorption paths. So
the wide-scope rule's daughter pattern ``NP[CASE=NOM, COORD=AND]``
already excludes coord-NPs that contain clitic-pronoun conjuncts.
No additional constraining equation is needed for this design.

If corpus pressure later surfaces a non-clitic full-pronoun
(``ako``, ``ikaw`` in stressed form) coord-NP that should still be
excluded, an explicit ``¬ (↓3 PRON_TYPE) = 'PRONOMINAL_COORD'``
constraint can be added; for now the structural restriction
suffices.

### Cross-references

- Phase 5n.C plan-of-record Commits 1–3
  (``.claude/plans/tgllfg-phase-5n-c.md`` §3.1).
- §18 L78 disposition (closes with this commit triple) —
  ``tgllfg-out-of-scope.md``.
- Phase 4 §7.2 narrow-scope hindi-wrap rule —
  ``src/tgllfg/cfg/negation.py:73``.
- Phase 5k Commit 3 binary NP coord head feats —
  ``src/tgllfg/cfg/coordination.py:44``.
- Phase 5k Commit 8 asymmetric NP coord —
  ``src/tgllfg/cfg/coordination.py:493``.
- ``cfg/coordination.py:355`` — multi-clause coord × hindi-wrap
  narrow-scope comment.
- Schachter & Otanes 1972 §10 (clitic-pronoun NOM SUBJ exclusion).
- Ramos & Bautista 1986 ch.18 (negation × coordination).

## Phase 5n.C Commit 4: L83 standalone NP-coord fragment — design (S → NP[COORD=BUT_NOT])

**Date:** 2026-05-10 (Phase 5n.C).
**Status:** design. Implementation lands in Phase 5n.C Commit 5.

### Decision

A new clause rule ``S → NP[CASE=NOM, COORD=BUT_NOT]`` admits the
bare asymmetric-coord-NP fragment ``Si Maria, hindi si Juan.``
"Maria, not Juan" as a complete matrix S, marked with
``CLAUSE_TYPE=FRAGMENT``. The matrix synthesises a one-place
fragment predicate ``PRED='NP-FRAG <SUBJ>'`` and binds the coord-NP
as ``SUBJ``; the coord-NP's existing feats (``COORD=BUT_NOT``,
``CONJUNCTS={Maria, Juan}``, ``CASE=NOM``, ``NUM``) remain on the
SUBJ f-structure unchanged.

The rule's daughter pattern ``NP[CASE=NOM, COORD=BUT_NOT]``
restricts the fragment-S admission to Phase 5k Commit 8's
asymmetric NP-coord output specifically — bare ``Si Maria.``
(no coord) does NOT parse as a sentence under this rule, because
the daughter requires ``COORD=BUT_NOT`` which is set only by the
asymmetric coord rule.

### Mechanism: structural gating, not parser-mode flag

The Phase 5n.C plan-of-record §3.2 originally specified an
``S_FRAG`` non-terminal gated by an explicit ``FRAGMENT=YES``
parser-mode flag (CLI ``--allow-fragments`` or parse-config
option). That design predates Phase 5n.B's L96 / L97 fragment-
clause work, which established **structural / lex-feat gating**
as the established convention for fragment-clause rules:

- L96 (``Salamat.``): ``S → N`` gated on ``FRAGMENT_HOST=YES``
  (set in the lex per-eligible-noun); ``CLAUSE_TYPE=FRAGMENT``
  on the matrix.
- L97 (``Hindi.`` / ``Oo.`` / ``Opo.`` / ``Oho.``): ``S → PRON``
  gated on ``INTERJ=YES`` and existential ``ANSWER`` constraint
  (set in the lex per-eligible-pronoun);
  ``CLAUSE_TYPE=FRAGMENT_ANSWER`` on the matrix.

The L83 rule follows the same pattern but discriminates **on a
constructional feat** (``COORD=BUT_NOT``) rather than a lex feat,
because the asymmetric coord-NP is a built structure, not a
lexical item. ``COORD=BUT_NOT`` is uniquely set by Phase 5k Commit
8 (``cfg/coordination.py:493``) and serves as the natural
discriminator — no new feat needs to be added to the asymmetric
coord rule.

This design ratifies an update to the original plan: the parser-
mode flag is replaced with structural gating, in line with the
established L96 / L97 fragment-rule pattern. Downstream consumers
that wish to filter out fragment-S parses can do so by checking
``CLAUSE_TYPE=FRAGMENT`` on the matrix; no parser-mode plumbing
is required.

### Why ``COORD=BUT_NOT`` and not ``NP_COORD`` generally

A broader rule ``S → NP[CASE=NOM, COORD=AND/OR/BUT_NOT]`` would
admit bare AND-coord and OR-coord NPs as sentences (e.g.,
``Si Maria at si Juan.`` would become a sentence). That over-
generates: bare additive / disjunctive coord-NPs are not
canonical sentence fragments in Tagalog. Only the asymmetric
``X, hindi Y.`` shape is attested as a standalone fragment
(per S&O 1972 §10 contrast-and-rejection construction;
R&B 1986 ch.16).

If corpus pressure later surfaces a bare AND-coord or OR-coord
fragment use case, a separate rule with explicit ``COORD=AND``
/ ``COORD=OR`` discriminators can be added. Each fragment-S
rule should restrict to the most specific structural shape that
licenses the fragment — preserving the ``Si Maria.`` 0-parse
guarantee for non-fragment-host bare NPs.

### Why a synthetic ``PRED='NP-FRAG <SUBJ>'``

The asymmetric coord-NP itself has no ``PRED`` (its conjuncts
each have ``PRED`` from the lex — proper-name PREDs like
``NOUN(↑ FORM)`` — but the coord-NP itself is a CONJUNCTS-
holding f-structure with no head ``PRED``). The fragment-S must
have a ``PRED`` for f-structure well-formedness; the matrix
cannot inherit ``PRED`` via ``(↑) = ↓1`` because the coord-NP
has none.

Synthesising ``PRED='NP-FRAG <SUBJ>'`` introduces a fragment-
predicate with one argument slot (SUBJ), bound to the coord-NP.
This treats the fragment as a degenerate one-place predication
over the coord-NP — semantically a placeholder that downstream
Glue / discourse-semantics work (Phase 6+) can interpret as
"BE", "FOCUS-CONTRAST", or "ASSERT-AND-REJECT" as the
construction's pragmatics dictate. The ``NP-FRAG`` placeholder
is intentionally not tied to a specific semantic operator at
this layer.

The L96 / L97 precedents differ here: their rules use
``(↑) = ↓1`` because the lex-host (``Salamat`` / ``Oo`` /
``Hindi`` etc.) carries its own ``PRED``. L83 is the first
fragment-S rule whose host is a constructed structure without
a head ``PRED``, so synthesis is unavoidable.

### Interaction with Phase 5k asymmetric coord (Commit 8)

The Phase 5k Commit 8 asymmetric NP-coord rule
(``cfg/coordination.py:493``) is unchanged — it continues to fire
inside an S frame (``Kumain si Maria, hindi si Juan.``) with
``COORD=BUT_NOT`` on the coord-NP. The new L83 rule is an
additional path: the same ``COORD=BUT_NOT`` coord-NP can serve
either (a) as the SUBJ of an existing V-headed S, or (b) as the
sole daughter of a fragment-S. Both readings can coexist on
ambiguous surfaces, ranked by Phase 4 §7.9 heuristics; the
fragment reading is naturally lower-ranked because it requires
the synthesis of a fragment-PRED whereas the V-headed S has a
real verbal PRED.

For the bare-NP fragment surface ``Si Maria, hindi si Juan.``
(no V), only the new L83 rule produces a complete parse — the
V-headed S rules don't fire without a V daughter. So the
fragment reading is the unique parse for this surface.

### Why bare ``Si Maria.`` still 0-parses

The L83 rule's daughter pattern is ``NP[CASE=NOM,
COORD=BUT_NOT]``, not ``NP[CASE=NOM]``. Bare singular NPs do
not carry ``COORD=BUT_NOT`` — that feat is set only by Phase 5k
Commit 8's asymmetric NP-coord rule, which requires a comma +
``hindi`` + second NP shape. So ``Si Maria.`` (singular bare
NP) does not match the L83 rule's daughter and continues to
0-parse as a sentence. This preserves the existing grammar's
rejection of bare NPs as sentences.

The L96 / L97 lex-feat-gated rules cover the bare-N / bare-PRON
fragment cases for specific opted-in lex items (``salamat``,
``oo``, ``hindi``, ``opo``, ``oho``); arbitrary bare nouns
(``aklat``, ``bahay``, etc.) and bare proper names
(``Si Maria``) are not opted in and continue to 0-parse.

### Cross-references

- Phase 5n.C plan-of-record Commit 5
  (``.claude/plans/tgllfg-phase-5n-c.md`` §3.2; this design
  appendix is Commit 4).
- §18 L83 disposition (closes with this commit pair) —
  ``tgllfg-out-of-scope.md``.
- Phase 5k Commit 8 asymmetric NP-coord (sole producer of
  ``COORD=BUT_NOT``) —
  ``src/tgllfg/cfg/coordination.py:493``.
- Phase 5m Commit 3 fragment-answer rule (L97 precedent) —
  ``src/tgllfg/cfg/clause.py:2078`` (search "fragment-answer").
- Phase 5n.B Commit 16 fragment-host NOUN rule (L96 precedent) —
  ``src/tgllfg/cfg/clause.py:2134`` (search "fragment-host").
- Schachter & Otanes 1972 §10 (asymmetric contrast construction).
- Ramos & Bautista 1986 ch.16 (NP coordination).

## Phase 5n.C Commit 6: L81 distributive-Q topic — design (DISTRIB scope marker)

**Date:** 2026-05-10 (Phase 5n.C).
**Status:** design. Implementation lands in Phase 5n.C Commit 7.

### Decision

A new clause rule ``S → NP[CASE=NOM] PART[PUNCT_CLASS=COMMA]
V[VOICE=AV]`` admits the surface ``Bawat bata, kumain.`` "Each
child ate" — a fronted universal-Q-NP topic, separated by a comma
from an AV-intransitive verb, producing a distributive-scope
reading. The matrix S carries ``DISTRIB=YES`` to mark the
distributive operator scope; the topic-NP becomes the matrix
``SUBJ`` (filling the AV verb's required argument).

### Analysis chosen: each-distributive operator

The plan-of-record §3.3 outlined two competing analyses:

1. **Distributive coord-elaboration.** Treat ``Bawat bata, kumain.``
   as a coord-style elaboration where the comma is the structural
   separator and the Q-NP is one of the coord daughters. Rejected
   — the surface is not a coord (only one conjunct, not a list);
   the comma is a topicalization marker, not a coord connective.

2. **Each-distributive operator.** Treat the Q-NP as a topic that
   raises to a distributive operator scope position; the inner
   clause carries the predication; the matrix is marked with a
   distributive-scope feat. **Chosen.** Cited basis: S&O 1972 §10
   (quantifier scope); R&B 1986 ch.16 (universal quantification).

The chosen analysis matches the LFG-canonical handling of
quantifier-scope marking (Bresnan 2001 §6 + Dalrymple 2001 §6 on
scope feats). The semantic side — interpreting the operator as a
distributive Glue derivation that scopes universally over the
inner predication — stays as **Phase 6+ Glue work** (out-of-scope
per ``tgllfg-out-of-scope.md`` §5.5 L19; the distributive scope
semantics is part of the broader quantifier-Glue agenda that
Phase 6's FU + LDD work prerequisites).

### Daughter pattern: ``NP[CASE=NOM]`` with UNIV constraining equation

The plan-of-record originally specified ``Q[DISTRIB=YES]`` as the
first daughter. Under the existing lex (``data/tgl/particles.yaml``
Phase 5f Commit 20), ``bawat`` and ``kada`` carry
``feats: {QUANT: EVERY, UNIV: "YES"}`` — **not ``DISTRIB``**. The
``DISTRIB`` feat is reserved in the existing grammar for
distributive cardinals (``tig-isa`` "one each", ``tig-dalawa``
"two each" — Phase 5f Commit 19) and as the matrix-level
distributive-scope marker (``cfg/clause.py:188`` predicative
distributive-cardinal rule sets ``(↑ DISTRIB) = 'YES'``).

To match the existing lex without introducing a new ``DISTRIB``
feat on ``bawat`` / ``kada``, the L81 rule uses a constraining
equation pattern:

```text
S → NP[CASE=NOM] PART[PUNCT_CLASS=COMMA] V[VOICE=AV]
  (↑ PRED) = ↓3 PRED                  -- verb percolation from ↓3
  (↑ VOICE) = ↓3 VOICE
  (↑ ASPECT) = ↓3 ASPECT
  (↑ MOOD) = ↓3 MOOD
  (↑ LEX-ASTRUCT) = ↓3 LEX-ASTRUCT
  (↑ DISTRIB) = 'YES'                 -- matrix scope marker
  (↑ SUBJ) = ↓1                       -- topic-NP fills AV verb's SUBJ
  (↓1 UNIV) =c 'YES'                  -- gates to bawat / kada heads
  (↓2 PUNCT_CLASS) =c 'COMMA'         -- belt-and-braces comma filter
```

The ``(↓1 UNIV) =c 'YES'`` constraining equation gates the rule
to topic-NPs whose head carries ``UNIV=YES`` — i.e., ``bawat`` /
``kada``-headed NPs (the Phase 5f Commit 20 universal-Q + bare-N
rule sets ``(↑ UNIV) = 'YES'`` on the resulting NP). Bare proper-
name topics (``Si Maria, kumain.``) lack ``UNIV`` and don't
match. Non-universal Qs (``lahat``, ``iba``, vague Qs) also lack
``UNIV`` and don't match.

### Why ``(↑ DISTRIB) = 'YES'`` and not a new feat

``DISTRIB=YES`` is already an established matrix-level marker
(Phase 5f Commit 19 predicative distributive cardinals — ``cfg/
clause.py:188``). Using the same feat for L81 keeps the matrix
naming-space consistent: a clause with distributive reading
carries ``DISTRIB=YES`` regardless of whether the distributivity
comes from a distributive numeral (``tig-isa``) or a universal-Q
topic (``bawat``). Downstream consumers can pattern-match on
``DISTRIB=YES`` uniformly. Per ``feedback_terse_feature_names``,
the existing terse feat is preferred over a new
``Q_SCOPE=DISTRIB`` or ``DIST_SCOPE=YES`` synonym.

### Scope: AV-intransitive only for this commit

The rule's third daughter is restricted to ``V[VOICE=AV]`` (no
explicit transitive-frame variants). The canonical S&O 1972 §10
example is ``Bawat isa, kumain.`` (intransitive). Transitive
variants (``Bawat isa, kumain ng kanin.``) would require parallel
rules with V + GEN-NP / V + DAT-NP frames; defer to a follow-on
if corpus pressure surfaces. The intransitive case closes the
core L81 syntactic side per the plan.

### Out of scope: ``Bawat isa, ...`` (Q + NUM)

The canonical ``Bawat isa, kumain.`` example involves ``bawat
isa`` (Q + NUM "each one"). Phase 5f Commit 20 explicitly
deferred Q + NUM composition (``bawat isa`` / ``bawat dalawa`` /
etc.). Without that compositional rule, ``Bawat isa, kumain.``
cannot match the L81 daughter pattern — the front position
expects an ``NP[CASE=NOM]``, but ``bawat isa`` 0-parses as an NP
today.

The L81 commit closes the comma+S syntactic mechanism for
``bawat`` + N forms (``Bawat bata, kumain.``, ``Kada bata,
kumain.``); the Q + NUM piece remains deferred separately. This
matches the disposition pattern from Phase 5f Commit 20: each
piece of the universal-Q feature surface is closed independently
based on linguistic priority.

### Disambiguation from ay-fronting

The existing Phase 4 §7.4 ay-fronting rule already admits
``Bawat bata ay kumain.`` "Every child eats" with the bawat-NP
in topic position. That parse does NOT carry ``DISTRIB=YES`` on
the matrix — ay-fronting is a topicalization mechanism without
intrinsic distributive scope. The L81 comma+S construction is
distinct: the comma marks the distributive-scope reading
explicitly, whereas ay-fronting is a more general
topicalization that doesn't specialize for distributivity.

For surfaces where both are structurally available (e.g., a
bawat-NP with both ``ay`` and a comma — uncommon), the parser
admits both readings; ranking per Phase 4 §7.9 heuristics.

### Disambiguation from Phase 5n.C Commit 5 (L83 fragment-NP-coord)

The L83 fragment-NP-coord rule
(``S → NP[CASE=NOM, COORD=BUT_NOT]``) and the L81 distributive-Q
rule are structurally distinct:

- L83's daughter is a 1-element rule: just the asymmetric
  coord-NP, no comma daughter, no V.
- L81's daughter is a 3-element rule: NP + COMMA + V.

Both have a comma in their input surfaces, but the L83 comma is
*inside* the coord-NP daughter (consumed by Phase 5k Commit 8
which builds ``NP COMMA hindi NP``), while the L81 comma is a
*top-level* daughter of the new clause rule. No structural
overlap; no rule competition.

### Cross-references

- Phase 5n.C plan-of-record Commits 6 + 7
  (``.claude/plans/tgllfg-phase-5n-c.md`` §3.3; this design
  appendix is Commit 6).
- §18 L81 disposition (closes with this commit pair) —
  ``tgllfg-out-of-scope.md``.
- §5.5 L19 quantifier-Glue deferral (Phase 6+ scope semantics) —
  ``tgllfg-out-of-scope.md``.
- Phase 5f Commit 19 predicative distributive-cardinal rule
  (existing ``DISTRIB=YES`` matrix marker convention) —
  ``src/tgllfg/cfg/clause.py:188``.
- Phase 5f Commit 20 universal-Q + bare-N rule (sets
  ``UNIV=YES`` on the resulting NP) —
  ``src/tgllfg/cfg/nominal.py:696``.
- ``data/tgl/particles.yaml:414`` — ``bawat`` / ``kada`` lex
  entries with ``UNIV=YES``.
- Schachter & Otanes 1972 §10 (quantifier scope).
- Ramos & Bautista 1986 ch.16 (universal quantification).

## Phase 5n.C.2 Commit 4: L77 PRED-sharing gapping in coord — design (CONJUNCTS reentrancy)

**Date:** 2026-05-10 (Phase 5n.C.2).
**Status:** design. Implementation lands in Phase 5n.C.2 Commit 5;
this entry documents the analysis decision and the f-structure
shape so the implementing commit is mechanical.

### Decision

The L77 gapping construction (``Kumain si Maria ng kanin at si Juan
ng tinapay.`` "Maria ate rice and Juan bread", canonical per
R&B 1986 ch.18 + S&O 1972 §10) is analysed as **PRED-sharing via
reentrancy across coord-S conjuncts**, in line with Bresnan 2001
§6 (coord) + Dalrymple 2001 §4 (reentrancy in coord).

The matrix S of a gapping construction is a coord with
``COORD=AND`` (or ``COORD=OR``); each conjunct is a sub-f-structure
in the ``CONJUNCTS`` set whose ``PRED`` value is reentrant
to the verb's lex ``PRED``. The first conjunct contributes the
shared verb explicitly; the second (and any subsequent) conjunct
re-binds the verb's PRED + a-structure via reentrancy without an
explicit V daughter in the c-tree.

### Mechanism

The new rule slot in ``src/tgllfg/cfg/coordination.py`` is

```text
S → V[VOICE=AV, ...] NP[CASE=NOM] NP[CASE=GEN] PART[COORD=AND] \
    NP[CASE=NOM] NP[CASE=GEN]
```

with equations roughly:

```text
↓5 ∈ (↑ CONJUNCTS)         # first conjunct (V's frame) added
↓6 ∈ (↑ CONJUNCTS)         # second conjunct's frame added
(↑ COORD)   = 'AND'
(↑ GAPPING) = 'YES'        # matrix marker
(↓1 PRED)   = (↓5 PRED)    # share PRED across conjuncts (reentrancy)
(↓1 PRED)   = (↓6 PRED)    # ditto for the gapped conjunct
(↓5 SUBJ)   = ↓2           # first conjunct's SUBJ = NP[NOM]_1
(↓5 OBJ)    = ↓3           # first conjunct's OBJ  = NP[GEN]_1
(↓6 SUBJ)   = ↓5_NP[NOM]   # second conjunct's SUBJ = NP[NOM]_2
(↓6 OBJ)    = ↓6_NP[GEN]   # second conjunct's OBJ  = NP[GEN]_2
(↓4 COORD)  =c 'AND'
```

(Exact equations land in Commit 5; the equation shapes above are
schematic — the implementing commit picks the precise rule shape
and possibly parameterises over voice / argument-frame variants.)

Parallel rule slots for **DV gapping** (``Tinulungan ni Maria si
Juan at ni Pedro si Lola.``) flip the case-marking pattern to
``NP[CASE=GEN] NP[CASE=NOM]`` (DV: GEN-agent, NOM-pivot) and adapt
the conjunct equations. The DV variant covers the corpus fixtures
pinned in Commit 3 (``tulong`` / ``sulat`` / ``aral``).

### Matrix marker: ``GAPPING=YES``

The matrix S carries an explicit ``GAPPING=YES`` feat to
disambiguate real gapping from the existing spurious recursive
NP-coord parses (see Commit 3 design notes) and from the existing
biclausal coord (``Kumain si Maria at uminom si Juan.`` —
``COORD=AND`` but no shared PRED). Downstream consumers can pattern-
match on ``GAPPING=YES`` to identify the construction; per
``feedback_terse_feature_names`` the marker is a single segment
with the atomic value ``YES``.

The choice of ``GAPPING=YES`` (rather than reusing an existing
feat like ``COORD=GAP`` or layering on ``ELLIPSIS=YES``) reflects
that:

- ``COORD`` already ranges over ``AND`` / ``OR`` / ``BUT`` / ``SO``
  / ``BUT_NOT`` (Phase 5k coord). Adding a ``COORD=GAP`` value
  would mix a structural marker (the gapping mechanism) into
  the conjunction-type feat (the surface connector). Keeping
  ``COORD=AND`` + ``GAPPING=YES`` separate is cleaner.
- ``ELLIPSIS`` would be too broad: gapping is a specific form
  of clausal ellipsis with PRED-sharing; other ellipsis forms
  (sluicing, VP-ellipsis) have different mechanisms and may
  warrant separate markers if ever closed.

### Why PRED-sharing reentrancy and not the alternatives

The §18.2 L77 entry noted three LFG analyses; here is the
disposition for each:

**1. PRED-sharing via reentrancy (chosen).** Bresnan 2001 §6
treats gapping as coord with reentrant PRED across conjunct
f-structures. Dalrymple 2001 §4 elaborates the reentrancy
mechanism. This analysis fits LFG's design space directly:

- No new c-structure machinery — the rule introduces a new
  c-structure shape but uses standard f-structure reentrancy
  for the PRED equality.
- No empty categories — the second conjunct has no V daughter
  in the c-tree, but the f-structure carries the shared PRED
  via the existing reentrancy mechanism.
- Composes cleanly with Phase 5k's ``CONJUNCTS`` set — gapping
  conjuncts populate the same set, just with shared PRED.

**2. Structural ellipsis (rejected).** Would introduce an empty
V category in the second conjunct's c-tree, with a binding
equation tying the empty V to the first conjunct's V. This
adds empty categories to the grammar, which Phase 4 §7.5
(relativization) avoided and which Phase 6 LFG-graph parsing
will further marginalise. Rejected on inventory grounds.

**3. Small-clause coord (rejected).** Would treat each conjunct
as a "small clause" with no projected V — a separate
clause-type from S. Requires a new ``S_SMALL`` non-terminal
and rule slate, plus a separate analysis for how the shared V
distributes over the small-clause conjuncts. Larger
architectural change for the same expressive outcome.
PRED-sharing reentrancy is the lowest-cost path.

### Interaction with Phase 5k coord (CONJUNCTS, COORD propagation)

Phase 5k's NP-coord (``cfg/coordination.py`` lines 78-112) and
clausal coord (``cfg/coordination.py`` lines 350+) both use:

- ``(↑ COORD) = '<value>'`` to set matrix coord type
- ``↓N ∈ (↑ CONJUNCTS)`` to add each conjunct to the set
- ``(↓N COORD) =c '<value>'`` belt-and-braces on the
  conjunction particle

The gapping rule re-uses **all three patterns**. The only
addition is the ``GAPPING=YES`` matrix marker and the
PRED-reentrancy equations. No conflict with Phase 5k: both
mechanisms produce ``COORD=AND`` + ``CONJUNCTS={c1, c2}``;
the difference is whether each conjunct has an independent
PRED (Phase 5k biclausal coord) or a shared reentrant PRED
(gapping).

### Disambiguation from spurious recursive NP-coord

Pre-Commit-5, AV gapping sentences parse spuriously via the
existing recursive ``NP → NP NP[GEN]`` rule; the matrix S has
no ``COORD`` feat on these spurious parses. After Commit 5,
the gapping rule produces an additional real-gapping parse with
``COORD=AND`` + ``GAPPING=YES``. The ranker prefers the real
parse (more meaningful structure; per Phase 4 §7.9 heuristics);
the spurious parse stays admissible but lower-ranked.

The legacy non-conflict matcher was historically the source of
these spurious parses. **Phase 6.C (2026-05-12) replaced it with
the graph-constraint matcher**, which checks feature compatibility
at predict time and prunes the spurious binary fanout before
constraining-equation rejection. The gapping rule's matrix marker
(``COORD=AND`` + ``GAPPING=YES``) continues to keep the real
gapping parse ranked above any residual binary readings.

### Scope: AV+DV 2 and 3 conjunct; OBJ-only gapping deferred

The implementing commit covers the most common gapping shapes:

- **2-conjunct AV transitive** (canonical): ``Kumain si Maria ng
  kanin at si Juan ng tinapay.``
- **3-conjunct AV transitive**: ``Kumain si Maria ng kanin, si
  Juan ng tinapay, at si Lola ng isda.``
- **2-conjunct DV transitive**: ``Tinulungan ni Maria si Juan at
  ni Pedro si Lola.``
- **2-conjunct DV ditransitive**: ``Binigayan ni Maria si Juan
  ng aklat at si Pedro ng panulat.``

Out of scope for Commit 5 (corpus pressure dependent):

- **OBJ-only gapping** (``Kumain si Maria ng kanin at ng
  tinapay.`` — Maria ate rice and bread) — flagged as marginal
  in the plan §4.2 Commit 4 (more clausal coord than gapping;
  per §18.2 deferred-as-unclear).
- **Mixed-voice gapping** (``Kumain si Maria at tinawag ni Juan
  si Pedro.``) — semantically different, the verbs aren't
  shared; this is biclausal coord.
- **Adjunct-only gap** (``Kumain si Maria sa bahay at si Juan
  sa simbahan.``) — adverbial residue rather than argument
  residue; defer to corpus pressure.

### Cross-references

- Phase 5n.C plan-of-record §4.2 Commits 4-7
  (``.claude/plans/tgllfg-phase-5n-c.md``; this design appendix
  is Commit 4 / formerly Commit 5).
- §18 L77 disposition (closes with Commits 3-5) —
  ``.claude/plans/tgllfg-out-of-scope.md``.
- Phase 5k Commit 3 binary NP-coord (CONJUNCTS / COORD pattern
  reused) — ``src/tgllfg/cfg/coordination.py:78-112``.
- Phase 5k clausal-S coord (``S → S PART[COORD=AND] S``,
  parallel pattern) — ``src/tgllfg/cfg/coordination.py:350+``.
- Phase 6.C matcher swap (2026-05-12) — superseded the spurious-
  parse caveat above; the legacy
  ``project_parser_nonconflict_matcher`` memory was deprecated
  in 6.C C7 closing docs.
- Bresnan 2001 ch.16 §3 "Coordination" (PRED-sharing analysis).
- Dalrymple 2001 ch.4 §4 "Coordination and reentrancy".
- Schachter & Otanes 1972 §10 (coord in Tagalog).
- Ramos & Bautista 1986 ch.18 (coord in Tagalog).

## Phase 6.D Commit 1: L47 long-distance relativization via FU — design

**Date:** 2026-05-12. **Status:** active (design commit; grammar /
test lands in 6.D C2-C4).

### Goal

Close §18.1.2 L47 (*long-distance wh-extraction*) by admitting
relativization across an XCOMP chain of arbitrary depth. Today's
Phase 4 §7.5 wrap rule

```text
NP[CASE=X] → NP[CASE=X] PART[LINK=NA|NG] S_GAP
   (↑) = ↓1
   ↓3 ∈ (↑ ADJ)
   (↓3 REL-PRO PRED) = (↓1 PRED)
   (↓3 REL-PRO CASE) = (↓1 CASE)
   (↓3 REL-PRO) =c (↓3 SUBJ)
```

admits depth-1 RCs only: the body is an ``S_GAP`` (a single
SUBJ-gapped clause). Cross-clausal cases like

- *ang batang gustong kumain* "the child who wants to eat"
- *ang batang gustong pumayag na kumain* "the child who wants to
  agree to eat"

0-parse today because no wrap rule admits an ``S_XCOMP`` body
(the SUBJ-gapped clause that the Phase 4 §7.6 + Phase 5c §7.6
follow-on control work produced for control complements). The
underlying per-depth REL-PRO threading inside ``S_XCOMP``
(``cfg/control.py``) already unifies the bottom-of-chain SUBJ
with the matrix REL-PRO; the only missing piece is the outer
wrap that puts an ``S_XCOMP`` body alongside the head NP.

The plan-of-record (``.claude/plans/tgllfg-phase-6.md`` §5.4)
specifies that the binding-equation form should use FU per
Kaplan & Zaenen 1989 §3 (``data/tgl/references/Kaplan-Zaenen-1989-LSS-CStruct-FU.pdf``), so the
extension is K&Z-faithful from the start rather than relying on
the per-depth threading as a load-bearing implementation detail.

### K&Z 1989 §3 adaptation for Tagalog relativization

K&Z 1989 §3 eq. 39 generalizes English topicalization to a
body-bottom regex-path designator

```text
(↑ TOPIC) = (↑ {COMP, XCOMP}* (GF-COMP))
```

reading: ``TOPIC`` is identified with *some* GF reached by zero
or more ``COMP``/``XCOMP`` traversals, with ``GF`` ranging over
the non-COMP grammatical functions (the "bottom"). Body /
bottom calibration:

- **Body** — the regex shape that licenses the path. For
  English topicalization, ``{COMP, XCOMP}*`` lets the gap appear
  inside any nesting of complement clauses.
- **Bottom** — the grammatical function at the foot of the
  path. For SUBJ-only relativization (the well-known Tagalog
  restriction; Kroeger 1993), the bottom is fixed at ``SUBJ``.

Adapting for Tagalog relativization:

```text
(↑ REL-PRO) =c (↑ XCOMP* SUBJ)
```

Body: ``XCOMP*`` (a chain of XCOMP traversals; the matrix
clause's XCOMP daughter chains into the embedded control
complement's XCOMP, etc.). Bottom: ``SUBJ`` (the SUBJ-only
restriction stays at the foot per Kroeger 1993). (The C2 form
above uses constraining ``=c`` rather than defining ``=`` — see
*Implementation note: constraining-form realization* below.)

The plan's eq. form ``(↑ REL-PRO) = (↑ {COMP, XCOMP}* SUBJ)``
generalizes further to admit ``COMP`` (sentential complements,
e.g., reported speech / *na*-clause arguments) in the body.
6.D scopes to ``XCOMP*`` only — see *Out of scope* below.

### C-structure: new S_XCOMP-bodied wrap rule (parallel to S_GAP)

6.D adds a new wrap-rule variant alongside the existing Phase 4
§7.5 wrap. For each of three head cases and two linker variants
(parallel to the existing six S_GAP wraps):

```text
NP[CASE=X] → NP[CASE=X] PART[LINK=NA|NG] S_XCOMP
   (↑) = ↓1
   ↓3 ∈ (↑ ADJ)
   (↓3 REL-PRO PRED) = (↓1 PRED)
   (↓3 REL-PRO CASE) = (↓1 CASE)
   (↓3 REL-PRO) =c (↓3 XCOMP* SUBJ)
```

The atomic-path copies (``PRED`` and ``CASE``) on REL-PRO are
unchanged from the S_GAP wrap (anaphoric sharing — see §7.5
above for the rationale on why we avoid full identity). The
load-bearing change is the **FU gap-binding constraint** on the
last line: ``REL-PRO`` is verified (constraining, ``=c``) to
equal the SUBJ endpoint reached via a regex path of zero-or-
more XCOMP traversals on ``↓3`` (the S_XCOMP daughter). The
K&Z 1989 binding semantics is realized by the combination of
the body's defining-equation reentrancy (S_GAP or S_XCOMP's
``(↑ SUBJ) = (↑ REL-PRO)``) plus this constraining-form check;
see *Implementation note: constraining-form realization* below
for the rationale.

K&Z 1989 §3 minimality (last subsection): when multiple
endpoints exist, the f-structure assigned to a sentence uses
the **shortest-path** endpoint. For the S_XCOMP-bodied wrap,
the XCOMP* enumeration starts at the S_XCOMP f-node and tries
zero iterations (the S_XCOMP's own SUBJ), then one
(``XCOMP SUBJ``), then two (``XCOMP XCOMP SUBJ``), etc. Each
intermediate level's SUBJ is unified with the matrix SUBJ via
the per-depth threading at S_XCOMP rules, so all candidate
endpoints land on the same canonical f-node anyway —
minimality picks the depth-0 endpoint, and the unifier
proceeds. (The FU mechanism is therefore *redundant in steady
state* for control-shared SUBJ chains; its load-bearing role is
to express the architectural commitment that gap binding lives
in the equation language, not in the c-structure recursion.)

### Existing Phase 4 §7.5 wrap: FU generalization of the =c

The plan §5.4 calls for replacing the existing
``(↓3 REL-PRO) =c (↓3 SUBJ)`` constraining equation on the
S_GAP-bodied wrap with an FU path: ``(↓3 REL-PRO) =c
(↓3 XCOMP* SUBJ)``. For a single-clause body (depth 1), the
zero-iteration case of XCOMP* reaches the S_GAP's own SUBJ —
which the S_GAP body already identifies with REL-PRO via
``(↑ SUBJ) = (↑ REL-PRO)``, so the FU equation is vacuous in
this case too. The replacement is **for architectural
consistency**: both wraps (S_GAP body and S_XCOMP body) use
the same FU shape, and the equation documents the standard
LFG analysis rather than the Phase 4 belt-and-braces
constraining check.

### Implementation note: constraining-form realization

The plan-of-record and the K&Z 1989 §3 eq. 39 canonical form
both express the gap binding as a defining-form FU equation:

```text
(↓3 REL-PRO) = (↓3 XCOMP* SUBJ)         ;; K&Z-canonical form
```

This form was attempted first in C2 and surfaced a tgllfg-
unifier orchestration limitation: our two-pass evaluator
processes defining-equations **parent-first** at each c-node,
so the wrap rule's FU equation fires *before* the S_GAP /
S_XCOMP body's ``(↑ SUBJ) = (↑ REL-PRO)`` has run. At that
point, ``↓3.SUBJ`` doesn't exist yet, and the FU resolver
returns ``no endpoint``. 61 regression tests fail as a result.

The fix landed as the **constraining-form realization** above:

```text
(↓3 REL-PRO) =c (↓3 XCOMP* SUBJ)        ;; tgllfg C2 form
```

The constraining-equation pass runs in pass 2 after the entire
defining pass has built the f-structure, so the body's SUBJ
binding has already created the reentrancy by the time the FU
equation evaluates. The K&Z binding semantics is preserved
because the *reentrancy itself* (the gap binding) is created
by the body's defining equation; the wrap's ``=c`` only
verifies that the reentrancy holds along the regex path.

The defining-form FU evaluation is documented as a Phase 7+
unifier extension in
``.claude/plans/tgllfg-out-of-scope.md`` §18.2 ("FU deferred
defining-equation evaluation"). Resolution candidates: re-pass
failed FU defining-equations after the children process, or
schedule FU-on-RHS defining-equations children-first. Revisit
when a construction surfaces that requires defining-form FU
binding — i.e., a case where the FU equation must *create* the
reentrancy because no body equation synthesizes it. Phase 6.F
(``sarili`` inside-out binding) is the most plausible
motivating case if 6.F's binding has to cross levels not
synthesized by per-depth body equations.

### What stays at S_XCOMP (per-depth threading preserved)

The cfg/control.py S_XCOMP rules continue to thread REL-PRO
across the chain via the existing equations
``(↑ SUBJ) = (↑ REL-PRO)`` and ``(↑ SUBJ) = (↑ XCOMP REL-PRO)``
at each depth. This per-depth threading does double duty:

1. **Control structure-sharing** (without relativization): the
   matrix control wrap (``(↑ SUBJ) = (↑ XCOMP REL-PRO)``) plus
   the S_XCOMP body's per-depth equations identify the
   controller (matrix SUBJ / experiencer) with the controllee
   (embedded SUBJ).
2. **Gap propagation** (with relativization): when the matrix
   wrap sets REL-PRO via the new 6.D FU equation, the same
   per-depth equations propagate the head NP's anaphoric
   identity down to the bottom SUBJ.

Removing the per-depth threading would force the FU equation
to do the navigation work for control too — a deeper
refactor that risks breaking existing control tests (1100+
tests at the time of writing). 6.D scopes the refactor to the
relativization wrap; eliminating the per-depth threading is
deferred to opportunistic future cleanup (analogue to the 2
``=c`` belt-and-braces sites the plan §4.2 decision marked for
6.H cleanup).

### Test corpus: depths 1, 2, 3, 4

Parametrized fixtures in
``tests/tgllfg/test_phase6_ldd_relativization.py`` cover:

- **Depth 1** (regression): *ang batang kumain* — single-clause
  RC body. The existing S_GAP wrap fires; the new FU equation
  is vacuous.
- **Depth 2** (NEW): *ang batang gustong kumain* — PSYCH
  matrix + AV inner. The S_XCOMP wrap fires; FU traverses one
  XCOMP to reach the embedded SUBJ.
- **Depth 3** (NEW): *ang batang gustong pumayag na kumain* —
  PSYCH + INTRANS + AV. Three-level chain; FU traverses two
  XCOMP transitions.
- **Depth 4** (NEW): *ang batang gustong pumayag na pumayag na
  kumain* — synthetic four-level chain, parallel to the
  existing 4-deep control test (``test_long_distance_control
  ::TestFourDeep::test_four_deep_chain``).

Each fixture asserts:

- Parse succeeds (≥ 1 parse).
- Bottom-of-chain SUBJ id == matrix-NP head id (REL-PRO
  binding is realized).
- No ``constraint-failed`` or ``lmt-mismatch`` blocking
  diagnostics.

### Negative cases — body restriction

K&Z 1989 §3 eq. 38 (Icelandic adjunct-island analogue) demands
the body restriction *prevent* the path from crossing certain
boundaries. For Tagalog 6.D, the equivalent is **the path
must not cross an ADJUNCT boundary** — the gap must be reached
via XCOMP traversal, not through an ADJ-attached RC body's
SUBJ. The body shape ``XCOMP*`` (not ``{XCOMP, ADJ}*``)
enforces this directly: a SUBJ inside an ADJ daughter is not
in the path's image.

Tested as: an ADJ-attached secondary RC body inside an outer
RC should not host the gap. The negative fixture asserts that
the matrix RC's binding doesn't reach the inner ADJ's SUBJ
(zero parses where the outer head NP would equate the inner
ADJ-clause SUBJ).

### What's not in 6.D scope

- **COMP traversal** (sentential complements, ``na``-clauses
  in object position). The plan's eq. form
  ``(↑ {COMP, XCOMP}* SUBJ)`` generalizes here, but Tagalog
  COMP carries its own SUBJ pivot (not control-shared), so the
  semantics is different — picks a different SUBJ than what's
  shared via control. Defer to corpus pressure / 6.E (free
  relative kung-S as DP, which is the closest cousin
  structurally).
- **Non-SUBJ extraction** (OBJ / OBJ-AGENT / OBJ-CAUSER /
  OBL across XCOMP chains). The Phase 5d Commit 5
  non-pivot ay-fronting infrastructure (S_GAP_OBJ /
  S_GAP_OBJ_AGENT / S_GAP_OBL / S_GAP_OBJ_CAUSER /
  S_GAP_OBJ_PATIENT) is depth-1 today. Lifting to cross-
  clausal would require parallel S_XCOMP_OBJ etc. families
  with FU bindings on the appropriate bottom GFs. Out of 6.D
  scope; tracked as corpus-driven follow-on.
- **Eliminating per-depth REL-PRO threading at S_XCOMP**. The
  K&Z-faithful end state has FU at the matrix wrap doing all
  the chain navigation, with S_XCOMP rules dropping their
  per-depth ``(↑ SUBJ) = (↑ REL-PRO)`` and ``(↑ SUBJ) =
  (↑ XCOMP REL-PRO)`` equations. The control complement
  binding would migrate to FU at the control matrix wrap.
  Deferred — large refactor, no functional gain in steady
  state (FU minimality reduces to the same endpoint the
  per-depth threading already produces).
- **No-FU fallback / non-control depth-2 RCs**. RCs where the
  body has nested *non-control* clauses (e.g., adjunct
  na-clauses, COMP-headed complements) aren't admitted by the
  S_XCOMP-bodied wrap because S_XCOMP only fires on control-
  verb heads. The FU equation enforces this implicitly via
  the XCOMP*-only body.

### Architectural commitments worth carrying forward

- **FU constraining equations on extraction wraps**. From 6.D
  on, the canonical relativization wrap uses
  ``=c (↑ XCOMP* SUBJ)`` rather than ``=c SUBJ``. The K&Z
  defining-form is on the Phase 7+ roadmap; the constraining-
  form realization preserves the K&Z semantics under our two-
  pass orchestration. The same pattern should generalize to
  cross-clausal ay-fronting (when corpus pressure surfaces).
- **K&Z 1989 §3 minimality is load-bearing**. The FU equation
  enumerates multiple endpoints in principle; minimality picks
  shortest-depth. The unifier (``fu.resolve_regex_for_read``)
  guarantees deterministic ordering via the depth-sorted
  endpoint list.
- **No new lex entries for control verbs**. ``gusto`` /
  ``puwede`` / ``maaari`` / ``kailangan`` / ``ayaw`` /
  ``kaya`` etc. carry ``CTRL_CLASS`` and are already wired for
  S_XCOMP composition; the only new infrastructure is the
  matrix wrap variant.

### Cross-references

- Plan-of-record §5.4 (``.claude/plans/tgllfg-phase-6.md``).
- K&Z 1989 §3 eq. 27-39 (``data/tgl/references/Kaplan-Zaenen-1989-LSS-CStruct-FU.pdf``); the
  topicalization template at eq. 39 and the off-path /
  body-bottom discussion at eq. 38.
- Kaplan & Maxwell 1988 — finite-state algorithm underlying
  the resolver in ``src/tgllfg/fstruct/fu.py``.
- Phase 4 §7.5 above — the S_GAP-bodied wrap that 6.D extends.
- Phase 4 §7.6 / Phase 5c §7.6 follow-on — the S_XCOMP
  infrastructure (in ``cfg/control.py``) that 6.D recruits as
  the deep RC body.
- Phase 6.B (``docs/fu-evaluation.md``) — the FU resolver
  implementation; 6.D is the first cfg-side consumer.
- §18.1.2 L47 entry — closed by 6.D.
- Kroeger 1993 — Tagalog SUBJ-only relativization restriction.
- Dalrymple 2001 ch. 14 — secondary reference for FU and LDD.

## Phase 6.E Commit 1: L93 free relative kung-S as DP — design

**Date:** 2026-05-12. **Status:** active (design commit; grammar /
test lands in 6.E C2).

### Goal

Close §18.1.2 L93 (*free relative ``kung sino`` / ``kung ano`` as
DPs*) by admitting a ``kung``-headed wh-clause as a non-COMP NP
argument of a matrix predicate. Today's Phase 5i Commit 8
infrastructure (``cfg/control.py``) parses ``kung sino ang kumain``
as ``S_INTERROG_COMP`` — a closed sentential complement bound to
matrix ``COMP`` only under KNOW-class or ASK-class predicates.
Surfaces where the kung-S fills an OBJ / OBL / SUBJ argument of a
matrix predicate — e.g.,

- *Galit ako sa kung sino ang nag-record.* "I'm angry at whoever
  recorded it." (DAT-OBL on ``galit``)
- *Gusto ko kung sino ang dumating.* "I want whoever came."
  (OBJ on ``gusto`` — non-COMP NP slot)
- *Hindi ko kakausapin kung sino ang mayabang.* "I won't talk to
  whoever is boastful." (OBJ on ``kausap``)

0-parse today because no NP rule admits an ``S_INTERROG_COMP``
daughter. The argument-frame side of the matrix predicate is
already wired for NP arguments (``gusto`` has
``PRED='GUSTO <SUBJ, OBJ>'`` with OBJ as ``NP[CASE=NOM]``); the
only missing piece is the wrap that re-categorizes the
``kung``-headed wh-clause as an NP.

The plan-of-record (``.claude/plans/tgllfg-phase-6.md`` §5.5)
specifies that the wh-pivot-to-matrix binding should be K&Z 1989-
faithful, exploiting the FU resolver landed in Phase 6.B. The
canonical wh-cleft kung-S surfaces don't strictly require FU
(the wh-PRON's LEMMA is fixed at the inner S's ``WH_LEMMA`` feat),
but the FU form documents the standard analysis and accommodates
future in-situ variants.

### K&Z 1989 §3 adaptation for Tagalog free relatives

K&Z 1989 §3 free-relative analysis treats the wh-clause as an
NP whose head is the wh-PRON, with the rest of the clause as an
adjunct-like modifier. The f-structure for *whoever came* is
approximately:

```text
PRED      = 'PRO'                ; the free-relative "the one"
PRON-TYPE = 'FREE-REL'           ; marker
WH_LEMMA  = 'who'                ; the binder's lemma
ADJ       ∋ { PRED = 'COME <SUBJ>',
              SUBJ = ↑ }         ; reentrant with the head
```

Adapting for Tagalog (where the wh-PRON appears inside a
``kung``-headed wh-cleft, not a bare wh-phrase):

```text
NP[CASE=X] → CASE-MARKER[CASE=X] S_INTERROG_COMP[Q_TYPE=WH]
   (↑ PRED)     = 'PRO'
   (↑ CASE)     = '{X}'
   (↑ FREE_REL) = true
   (↑ WH_LEMMA) = ↓2 WH_LEMMA
   ↓2 ∈ (↑ ADJ)
   (↓2 COMP_TYPE) =c 'INTERROG'
   (↓2 Q_TYPE)    =c 'WH'
```

Body: zero traversals — the wh-pivot's ``WH_LEMMA`` is at the top
of the S_INTERROG_COMP under the canonical wh-cleft analysis
(Phase 5i Commit 2). Bottom: ``WH_LEMMA``. The trivially-zero-step
"FU" path is a direct atomic-path copy, not a regex enumeration.

The FU shape generalizes to in-situ wh — e.g., a hypothetical
``kung kumain ng ano si Maria`` "whatever Maria ate of" with
``ano`` at OBJ rather than cleft-pivot — via the regex form

```text
(↑ WH_LEMMA) =c (↓2 {SUBJ, OBJ, OBJ2, OBL-DAT, OBL-LOC}* WH_LEMMA)
```

In-situ wh is not in scope for 6.E (no corpus pressure today;
canonical wh-cleft kung-S is the attested form per S&O 1972 §6).
Documented as a follow-on in *Out of scope* below.

### C-structure: new NP-from-kung-S wrap rule

6.E adds an NP wrap-rule family that consumes
``S_INTERROG_COMP[Q_TYPE=WH]`` as a non-COMP argument. For each of
three head cases (NOM via ``ang``; GEN via ``ng``; DAT via ``sa``),
one rule:

```text
NP[CASE=NOM] → DET[CASE=NOM, DEM=false] S_INTERROG_COMP[Q_TYPE=WH]
NP[CASE=GEN] → ADP[CASE=GEN, DEM=false] S_INTERROG_COMP[Q_TYPE=WH]
NP[CASE=DAT] → ADP[CASE=DAT, DEM=false] S_INTERROG_COMP[Q_TYPE=WH]
```

Equations on each rule:

```text
(↑ PRED)       = 'PRO'
(↑ CASE)       = '{NOM|GEN|DAT}'
(↑ FREE_REL)   = true
(↑ WH_LEMMA)   = ↓2 WH_LEMMA
↓2 ∈ (↑ ADJ)
(↓2 COMP_TYPE) =c 'INTERROG'
(↓2 Q_TYPE)    =c 'WH'
```

The wh-PRON's ``HUMAN`` lex feat — true for *sino*, absent for
*ano* / *alin* — is **not** lifted onto the free-relative NP head
in 6.E. The Phase 5i Commit 2 wh-cleft rule lifts only
``LEMMA → WH_LEMMA`` from the wh-PRON daughter onto the inner S;
``HUMAN`` (and any other lex feats on the PRON) stay on the PRON
node, which is not reachable from the ``S_INTERROG_COMP``'s
f-structure projection. Downstream consumers needing the HUMAN
distinction can dispatch on ``WH_LEMMA`` (``sino``→HUMAN,
``ano``/``alin``→non-HUMAN). A future extension may lift HUMAN at
the Phase 5i C2 rule directly (one-line change there) — see *Out
of scope* below.

The ``DEM=false`` guard parallels the Phase 5e Commit 5 headless-RC
rule: demonstratives (``ito`` / ``iyan`` / ``iyon``) carry
``DEM=true`` and don't compose into free relatives.

### F-structure semantics: free relative as headless NP

The NP's f-structure mirrors the Phase 5e Commit 5 headless-RC
shape (``ang kumain`` "the one who ate"), with two differences:

1. The body is a ``kung``-wrapped wh-cleft (``S_INTERROG_COMP``),
   not a SUBJ-gapped ``S_GAP``.
2. ``FREE_REL=true`` and ``WH_LEMMA=X`` mark the head as a
   free-relative pivot rather than an anaphoric implicit head.

The two paths are deliberately disjoint at the f-structure
boundary: the Phase 5e headless RC has ``FREE_REL=undefined`` and
``WH_LEMMA=undefined``; the 6.E free relative has both set. A
downstream semantic stage (out of scope for 6.E) consumes the
distinction.

### Disambiguation: free relative vs indirect Q

The same surface — ``kung sino ang kumain`` — has two licit
analyses:

- **Indirect Q** (Phase 5i C8): bound as matrix ``COMP`` under
  KNOW-class or ASK-class predicates. *Alam ko kung sino ang
  kumain.* "I know who ate."
- **Free relative** (6.E): bound as a non-COMP NP argument under
  ordinary matrix predicates. *Galit ako sa kung sino ang
  nag-record.* "I'm angry at whoever recorded it."

Disambiguation is **selectional**: the matrix predicate's argument
frame selects either ``COMP`` (KNOW/ASK) or a regular case-marked
NP. The grammar produces both parses where the surface is
genuinely ambiguous (e.g., ``Itinatanong niya kung sino ang kumain``
— "He is asking who ate" / "He is asking the person who ate" —
the latter free-relative reading is awkward but not ill-formed).
The 6.E rule does not gate against KNOW/ASK matrix frames; the
matrix rule's category-pattern admission (which is
``S_INTERROG_COMP``, not ``NP``) blocks the free-relative path
from feeding the indirect-Q COMP slot.

### Implementation note: no FU resolver invocation at depth 0

The ``(↑ WH_LEMMA) = ↓2 WH_LEMMA`` equation is a depth-0 atomic-
path copy. The FU resolver landed in Phase 6.B (``fstruct/fu.py``)
is not invoked at this depth — the equation evaluator's
``_path_features`` resolver handles atomic-path copies directly.
The K&Z 1989 binding semantics is therefore realized as a direct
attribute reference, not as a regex-path enumeration. The FU shape
becomes load-bearing only if the in-situ wh extension (above) is
later authored; documented in *Out of scope* below.

The Phase 6.B FU resolver is therefore *not* a strict prerequisite
for 6.E's canonical scope. The 6.E entry sits under §18.1.2's
"Phase 6 dependent" bucket because the **graph-constraint matcher
tightening** (Phase 6.C) is what makes
``S_INTERROG_COMP[Q_TYPE=WH]`` a tight enough pattern to fire only
on wh-Q kung-S — pre-6.C the matcher's shared-key-absence semantics
admitted the yes/no and bare-declarative variants too, which would
overgenerate free-relative parses.

### Test corpus design (C2 outline)

The C2 test file (``tests/tgllfg/test_phase6_free_relative_kung.py``)
will cover:

**Positive — case variants × wh-PRON variants**:

- DAT-OBL on *galit*: ``Galit ako sa kung sino ang nag-record.``
- GEN on *malay* or similar: ``Walang malay si Juan kung saan
  pumunta si Maria.`` (saan-variant; selectional via *malay*)
- NOM on *gusto*: ``Gusto ko kung sino ang dumating.``
- NOM on a transitive AV: ``Pinakain niya kung sino ang gutom.``

**Positive — wh-PRON paradigm**:

- *sino* (HUMAN, NOM-pivot): "whoever"
- *ano* (non-HUMAN, NOM-pivot): "whatever"
- *alin* (selectional, NOM-pivot): "whichever"
- *saan* (locative): "wherever" — note this requires the
  ``saan``-wh-cleft path (Phase 5i Commit 4); covered if
  wh-locative cleft fires.

**Positive — f-structure assertions**:

- Free-relative NP has ``PRED='PRO'``, ``FREE_REL=true``,
  ``WH_LEMMA=<lemma>``.
- The kung-S sits in ``ADJ`` (single-entry set).
- The kung-S's ``COMP_TYPE='INTERROG'`` and ``Q_TYPE='WH'``.
- For *sino*-class: ``HUMAN=true`` lifts onto the free-relative NP.

**Negative — yes/no and bare-declarative kung-S don't free-relate**:

- ``*Galit ako sa kung kumain si Maria.`` (yes/no kung-S in DAT
  argument slot) — 0-parse expected.
- ``*Galit ako sa kung sino kumain.`` (bare-form kung-S, which is
  S[Q_TYPE=WH] without S_INTERROG_COMP wrap) — admits or rejects
  depending on whether the bare-form rule lifts COMP_TYPE; expected
  0-parse if COMP_TYPE is absent, and the ``=c 'INTERROG'`` guard
  fires.

**Negative — free relative doesn't crossfire into KNOW/ASK COMP**:

- ``Alam ko kung sino ang kumain.`` still parses as Phase 5i C8
  indirect-Q (with kung-S as COMP), and the f-structure has
  ``COMP_TYPE='INTERROG'`` on the COMP slot. The 6.E rule does
  not produce an extra spurious parse here because *alam*'s frame
  ``KNOW <SUBJ, COMP>`` selects ``S_INTERROG_COMP``, not ``NP``.
- ``Tinanong niya kung sino ang kumain.`` (ASK-class) — similar:
  the ASK frame's OBJ-AGENT is the asker, and the asked-thing is
  ``S_INTERROG_COMP`` (matrix OBJ), not an NP. The 6.E rule
  would produce a parallel parse where ``kung sino ang kumain``
  is wrapped as an NP[CASE=NOM] and ``Tinanong niya [NP]`` —
  this is a genuine syntactic ambiguity ("He asked the one who
  ate" — free-rel reading vs. "He asked who ate" — indirect-Q
  reading). Both parses are licit; the test asserts ≥ 1 of each.

### What's in scope for 6.E

- Three NP wrap rules (NOM / GEN / DAT) consuming
  ``S_INTERROG_COMP[Q_TYPE=WH]``.
- Free-relative f-structure marking (``PRED='PRO'``, ``FREE_REL``,
  ``WH_LEMMA``, ``HUMAN`` lift).
- Test corpus across case and wh-PRON variants.
- The Phase 5e Commit 5 headless-RC rule is **not** modified — it
  continues to handle ``ang kumain`` "the one who ate" via S_GAP;
  the 6.E free-relative path is a parallel, disjoint construction.

### Out of scope for 6.E (documented as future work)

- **In-situ wh inside kung-S**. The ``(↑ WH_LEMMA) =c (↓2 {SUBJ,
  OBJ, OBJ2, OBL-*}* WH_LEMMA)`` FU form (above) supports
  hypothetical in-situ wh-Q surfaces, but no canonical Tagalog
  attestation per S&O 1972 / R&B 1986; deferred to corpus pressure.
- **Multiple-wh kung-S**. Surfaces like ``Tutulong ako sa kung sino
  kung ano`` "I'll help whoever with whatever" — multi-wh free
  relatives; not in scope for 6.E. Deferred until corpus pressure.
- **Possessive kung-S**. Surfaces like ``ang aklat ni kung sino``
  "the book of whoever" — kung-S as GEN-possessor. Should fall out
  of the GEN-NP rule if the possessor-position composes with the
  GEN-NP, but not test-covered in 6.E. Verify in 6.J.
- **DAT-pivot wh-PRONs** (``kanino`` "to whom"). The Phase 5i C2
  wh-cleft is NOM-pivot only; ``kanino`` was deferred to a Phase
  5i follow-on. If a *kung kanino* free relative appears in
  corpus, 6.E rule extends straightforwardly once the DAT-pivot
  wh-cleft is authored.
- **Free relative as matrix S argument** (independent S-level
  cleft). E.g., ``Si Juan ang kung sino ang nag-record.`` "Juan
  is the one who recorded it." — the kung-S sits in an
  ``ay``-style equational cleft. The 6.E NP rule produces the NP;
  whether the matrix cleft rule (Phase 5e ay-fronting) accepts
  this NP shape is a downstream verification.
- **HUMAN lift onto the free-relative NP head**. A small Phase 5i
  C2 extension (adding ``(↑ HUMAN) = ↓1 HUMAN`` on the wh-cleft
  rule) would let 6.E lift ``HUMAN`` from the inner S onto the
  matrix free-relative NP. Useful for downstream pronoun
  resolution / binding theory. Not in 6.E scope; downstream
  consumers dispatch on ``WH_LEMMA`` until then.

### Architectural commitments worth carrying forward

- **Free-relative f-structure shape is distinct from indirect Q**.
  ``FREE_REL=true`` marks the free-relative NP head; absent on
  indirect-Q COMP-bound kung-S. Downstream semantic / a-structure
  stages can disambiguate.
- **Selectional disambiguation between free-rel and indirect-Q**.
  No grammar-side gating against KNOW/ASK matrix frames; the
  matrix predicate's argument frame (NP vs. COMP) is the
  selector. Both parses can coexist when the surface is
  genuinely ambiguous.
- **Phase 6.B FU resolver is not load-bearing at depth 0**. The
  6.E rules use direct atomic-path copies, which are evaluated
  by the existing ``_path_features`` resolver. The FU shape is
  documented for in-situ wh extensibility but not invoked under
  canonical wh-cleft surfaces.
- **No new lex entries**. The existing
  ``kung[COMP_TYPE=INTERROG]`` particle and the wh-PRON lex
  entries (``sino`` / ``ano`` / ``alin`` etc.) already carry the
  necessary feats; the 6.E rule consumes them via the existing
  Phase 5i wh-cleft path.

### Cross-references

- Plan-of-record §5.5 (``.claude/plans/tgllfg-phase-6.md``).
- K&Z 1989 §3 (``data/tgl/references/Kaplan-Zaenen-1989-LSS-CStruct-FU.pdf``); free-relative
  analysis discussion.
- Phase 5e Commit 5 above — headless-RC rule that 6.E parallels
  for the free-relative variant.
- Phase 5i Commit 2 above — wh-cleft rule producing the inner
  S[Q_TYPE=WH] f-structure that S_INTERROG_COMP wraps.
- Phase 5i Commit 8 above — KNOW-class indirect-Q wrap that
  6.E disambiguates from.
- Phase 5n.A Commit 29 above — ASK-class indirect-Q wrap;
  6.E coexists with this path under selectional disambiguation.
- §18.1.2 L93 entry — closed by 6.E.
- S&O 1972 §6 — wh-Q analysis underlying the wh-cleft structure
  that 6.E consumes via S_INTERROG_COMP.

### What landed (2026-05-12)

C2 grammar landed three NP wrap rules in
``src/tgllfg/cfg/extraction.py`` matching the design exactly —
one rule per case (NOM via ``DET[CASE=NOM, DEM=false]``; GEN /
DAT via ``ADP[CASE=X, DEM=false]``) with the equation set above.
``FREE_REL`` was added to ``src/tgllfg/core/feats.py``
``BINARY_FEATS`` (50 → 51), with companion bumps to
``docs/feats-binary-audit.md`` and the Phase 5n.C.4 audit-
counter test per the "update both" guard.

C2 tests landed at ``tests/tgllfg/test_phase6_free_relative_kung.py``
— 15 tests across 9 classes covering: basic free-relative
parsing in NOM / GEN / DAT slots; f-structure shape assertions
(``PRED='PRO'``, ``FREE_REL=True``, ``WH_LEMMA`` lifted, kung-S
in ``ADJ``, inner SUBJ as headless RC); the wh-PRON paradigm
(sino / ano / alin); bare-form colloquial kung-S; selectional
disambiguation (alam + tinanong indirect-Q parses regress
unchanged); negative cases (yes/no + bare-declarative kung-S
correctly reject Q_TYPE=WH gate); and regressions (Phase 5e C5
headless RC + Phase 5i C2 wh-cleft Q still parse).

Final 6.E status: 7 150 fast tests + 19 slow + 1 xfail (the
test_kahit_ano_in_obj cross-case-lex carry-forward from 6.C,
unrelated to 6.E). Lint clean (311 source files). No deferrals
introduced; the in-situ wh and DAT-pivot wh-PRON items
itemized in *Out of scope* above carry forward to corpus-
pressure follow-ups, not Phase 6 work.

## Phase 6.F Commit 1: L104 sarili anaphora via binding equation — design

**Date:** 2026-05-12. **Status:** active (design commit; grammar /
test lands in 6.F C2-C3).

### Goal

Close §18.1.2 L104 (*anaphora resolution / binding for
``sarili``*) by adding a binding equation that makes the
reflexive ``sarili``'s antecedent reentrant with its binder.
The Phase 5m Commit 1 / Commit 6 work established the lex
entry (``sarili`` is a NOUN with ``SEM_CLASS=REFLEXIVE``) and
the c-structure composition (``ang sarili NIYA`` parses as a
regular ``D + N + GEN-PRON`` NP via existing Phase 4 grammar).
The Phase 5m closing commits pinned the absence of binding —
``tests/tgllfg/test_phase5m_reflexive_sarili.py::TestAnaphora\
Deferred::test_no_antecedent_reentrancy_today`` asserts
``subj.feats.get("ANTECEDENT") is None``. Phase 6.F flips that
pin: the f-structure of a reflexive NP gets an ``ANTECEDENT``
feat pointing at the binder.

### Tagalog binding theory: actor-binder, not pivot-binder

Tagalog reflexive binding diverges from English-style "SUBJ
binds reflexive in its domain" in a load-bearing way. Per
Kroeger 1993 §2.3 (and the post-Kroeger LFG tradition adopted
in ``project_tgllfg_phase4_status``'s voice commitments), the
reflexive ``sarili`` is bound by the **actor** of the matrix
clause, not by the grammatical pivot (the ``ang``-marked NP /
SUBJ). The actor surfaces at different GFs across voices:

- **AV voice**: actor = ``SUBJ`` (e.g., *Nakita siya ng aso.*
  is structurally OV-like, but plain AV-transitives like
  *Kumain siya ng kanin.* have actor = SUBJ).
- **OV / DV / IV voice**: actor = the non-pivot GEN-marked
  argument. In tgllfg's current paradigm this surfaces as
  ``OBJ`` for plain transitives (*Nakita niya ang sarili
  niya.* has SUBJ = sarili, OBJ = niya) or ``OBJ-AGENT`` for
  multi-argument frames (causatives, applicatives).

The pinned test case *Nakita niya ang sarili niya.* is OV-
patterned: ``ang sarili niya`` is the SUBJ pivot (patient),
``niya`` is the OBJ (actor / binder). The binding identifies
``SUBJ.ANTECEDENT = OBJ``.

### Binding-equation form

The Phase 6.B Commit 5 binding-equation context wires
``_eval_defining_eq`` to support regex-RHS defining
equations: the resolver enumerates endpoints, K&Z 1989 §3
minimality picks the shortest-depth canonical endpoint, and
``graph.unify(lhs_node, target)`` creates the reentrancy
(see ``docs/fu-evaluation.md`` §6.5). This makes the
binding-equation site work out of the box.

The local-domain binding equation:

```text
(↑ SUBJ ANTECEDENT) = (↑ {SUBJ | OBJ | OBJ-AGENT})
```

read: "the ANTECEDENT of the matrix SUBJ is the f-structure
reached by traversing SUBJ, OBJ, or OBJ-AGENT from the matrix
root." The K&Z alternation ``{SUBJ | OBJ | OBJ-AGENT}`` is a
single-step regex path; the resolver evaluates it against the
matrix f-graph, enumerates the GFs that are present, and
picks the shortest path that satisfies the constraint —
crucially, the path must NOT terminate at the reflexive
itself (the self-binding case).

**Cross-clausal extension (XCOMP body)**:

```text
(↑ SUBJ ANTECEDENT) = (↑ XCOMP* {SUBJ | OBJ | OBJ-AGENT})
```

navigates through zero-or-more XCOMP traversals to reach the
binder. Per tgllfg's per-depth REL-PRO threading at
``cfg/control.py`` S_XCOMP rules, the matrix SUBJ is already
structure-shared with the XCOMP body's SUBJ at every depth;
the cross-clausal form picks up the matrix actor (typically
SUBJ in PSYCH-control, OBJ in OV-control) regardless of
embedding depth.

### Where the equation lives: matrix-rule placement

The binding equation is placed on the **matrix S rule** where
the reflexive surfaces as an argument. ↑ in the equation is
the matrix S; the equation accesses ``↑.SUBJ`` (containing
sarili) and ``↑.OBJ`` / ``↑.OBJ-AGENT`` (the binder). This
avoids the inside-out FU pattern (which tgllfg's resolver
doesn't natively support — see *Out of scope* below for the
inside-out-FU stay).

To keep the equation from firing on non-reflexive SUBJs, it's
guarded by a **lemma-or-SEM_CLASS gate** at the f-structure
level — see *Implementation note* below for the tagging
question (lift SEM_CLASS to the outer NP, or gate on LEMMA).

### Self-binding exclusion

The naive alternation ``{SUBJ | OBJ | OBJ-AGENT}`` would
enumerate SUBJ as a valid endpoint at depth 1 — and SUBJ is
the reflexive itself. Unifying ``SUBJ.ANTECEDENT`` with
``SUBJ`` would create a cycle (the ANTECEDENT pointer leads
back to the holder of ANTECEDENT). Per ``fstruct/graph.py``'s
occurs-check, this would be rejected at unify time.

The K&Z 1989 §3 minimality clause picks the *shortest valid*
endpoint. If SUBJ is invalidated by the occurs-check, the
resolver should fall through to OBJ / OBJ-AGENT. **Phase 6.B's
resolver does not currently retry on occurs-check failure** —
the resolver returns endpoints shortest-first and the
``_eval_defining_eq`` site unifies with the first. If that
fails, the equation reports `no endpoint`.

Two paths to fix the self-binding case:

1. **Resolver-side retry**: extend ``resolve_regex_for_read``
   to filter endpoints that would cause cyclic unification.
   Surfaced as a 6.F C2 implementation question; if
   substantial, deferred to a Phase 7+ unifier extension.
2. **Equation-side exclusion**: write the binding as two
   parallel rules that exclude the self-binding case
   syntactically — i.e., the rule that fires when ``sarili``
   is at SUBJ binds to OBJ / OBJ-AGENT only (excluding SUBJ
   from the alternation). For the canonical OV pattern, this
   is just ``(↑ SUBJ ANTECEDENT) = (↑ OBJ)``.

The C2 work will start with path 2 (equation-side exclusion)
because it doesn't require unifier changes; the resolver-side
retry can land in a follow-on if cross-clausal cases need it.

### Tagging the binding site: SEM_CLASS lift vs. LEMMA gate

The Phase 5m lex entry sets ``SEM_CLASS=REFLEXIVE`` on the
NOUN ``sarili``. The c-structure projection lifts this to the
N daughter via ``N → NOUN`` (``(↑) = ↓1``), but the outer
NP's projection ``NP → DET + N`` only lifts ``PRED`` and
``LEMMA`` from the N daughter — ``SEM_CLASS`` stays on the N
node and does **not** appear on the outer NP's f-structure.

The matrix rule's binding-equation gate therefore can't be
``(↑ SUBJ SEM_CLASS) =c 'REFLEXIVE'`` without first lifting
SEM_CLASS through the NP projection. Two options:

- **Option A: Lift SEM_CLASS at the NP projection**. Add
  ``(↑ SEM_CLASS) = ↓2 SEM_CLASS`` to the ``NP → DET + N``
  rule (and parallel D + N rules). Consistent with how
  ``PRED`` / ``LEMMA`` already lift. Cost: minor — modifies a
  rule that fires very often; no expected regressions because
  SEM_CLASS isn't currently consumed downstream of NP.
- **Option B: Gate on LEMMA at the matrix level**. Replace
  the SEM_CLASS gate with ``(↑ SUBJ LEMMA) =c 'sarili'``.
  Narrower (only fires on the exact lemma), but lexically
  brittle — a future ``sariling-katauhan`` "self-personhood"
  multiword reflexive wouldn't compose.

Recommendation: **Option A** (SEM_CLASS lift). The
SEM_CLASS feat is already declared as a meaningful tag in
Phase 5m's planning notes, and lifting it makes downstream
analytics (binding theory, anaphora resolution) more general.

### Sample binding for the pinned test

For *Nakita niya ang sarili niya.* (OV-pattern):

```text
Matrix S f-structure:
   PRED  = 'KITA <SUBJ, OBJ>'
   VOICE = 'AV'         ; per nakita's lex entry
   SUBJ  = ↓3 (ang sarili niya)
       PRED       = 'NOUN(↑ FORM)'
       LEMMA      = 'sarili'
       CASE       = 'NOM'
       SEM_CLASS  = 'REFLEXIVE'   ; lifted at NP projection (Option A)
       POSS       = ↓3.NP[CASE=GEN]   (the inner GEN-PRON niya, id=30)
       ANTECEDENT = ↑.OBJ            ; set by binding equation, id=22
   OBJ   = ↓2 (niya)
       NUM        = 'SG'
       CASE       = 'GEN'
       is_clitic  = true
```

After the binding equation fires, ``SUBJ.ANTECEDENT.id ==
OBJ.id`` — the deferred-test invariant flips from "no
ANTECEDENT" to "ANTECEDENT == OBJ".

### What's in scope for 6.F

- **NP-projection SEM_CLASS lift**: add to the NP-from-D + N
  rule (and parallel rules) so SEM_CLASS surfaces on the
  outer NP's f-structure.
- **Local-domain binding equation** on the canonical
  transitive matrix S rule (V + GEN-NP + NOM-NP):
  ``(↑ SUBJ ANTECEDENT) = (↑ OBJ)`` when SUBJ.SEM_CLASS ==
  REFLEXIVE.
- **Two-rule split or constraining-gate** for the
  SEM_CLASS=REFLEXIVE branch — TBD by the rule-engine's
  preference; the equivalent of a "rule variant fires on
  reflexive SUBJ" pattern.
- **Cross-clausal binding** (sarili across XCOMP boundary
  in PSYCH-control like *Gusto kong makita ang sarili ko.*)
  — the per-depth control threading propagates the binding
  via SUBJ structure-sharing; verified in C3.
- **Pinned-test flip**: ``test_no_antecedent_reentrancy_\
  today`` flips from ``is None`` to ``is not None`` AND
  reentrancy with the binder.
- **Extended test corpus**: sarili at SUBJ (OV), at OBJ
  (AV), with 1sg / 2sg / 3sg / 3pl GEN-PRON possessor
  agreeing with the binder.

### What's out of scope for 6.F (corpus-pressure / Phase 7+)

- **Inside-out FU designators** (``((SUBJ ↑) GF)``-style).
  tgllfg's FU resolver is outside-in only (read regex paths
  from a base node down). Adding inside-out support is a
  Phase 7+ unifier extension. Phase 6.F sidesteps by placing
  binding equations on matrix rules.
- **Resolver-side cyclic-endpoint pruning**. The K&Z 1989 §3
  minimality clause as currently implemented in
  ``resolve_regex_for_read`` returns shortest-first endpoints
  without retrying on occurs-check failure. Phase 6.F C2
  works around via equation-side exclusion of the self-
  binding case. Resolver-side filtering remains Phase 7+.
- **Cross-COMP binding** (binding through a COMP-bound
  na-clause, e.g., *Sinabi niya na nakita niya ang sarili
  niya.*). Tagalog binding theory says reflexives don't
  cross finite-clause boundaries; the resolver should NOT
  enumerate through COMP. Verified absent in the regex path
  (no COMP traversal in the binding path).
- **Reciprocal ``magkakapatid``-style binding** (multi-
  argument reciprocals). Separate construction; not in §18.1.
- **Binding through PP-internal sarili** (e.g., *Tumakbo si
  Maria papunta sa sarili niya.* "Maria ran toward
  herself"). The papunta-PP wraps the sarili NP in an OBL
  GF that the matrix rule doesn't directly see; binding
  through PP-OBL likely needs a separate rule variant or
  the inside-out FU extension. Deferred to corpus pressure.
- **HUMAN feat propagation between binder and bindee**.
  Coherence checks (binder must be HUMAN if reflexive is
  HUMAN, etc.) are downstream of binding; not in scope.

### Architectural commitments worth carrying forward

- **Tagalog binding is actor-not-pivot**. Per Kroeger 1993,
  the reflexive's binder is the actor (SUBJ in AV, OBJ /
  OBJ-AGENT in non-AV). All binding equations in 6.F (and
  Phase 7+ binding rules for ``ibang-tao`` / etc.) follow
  this rule.
- **Binding-equation context (Phase 6.B C5) is the natural
  carrier**. Defining-equation with regex RHS is the K&Z
  binding shape; the resolver enumerates endpoints and the
  unifier creates the reentrancy via ``graph.unify``. 6.F is
  the first Tagalog-grammar consumer of this code path.
- **SEM_CLASS lifts at the NP boundary**. The Phase 5m
  diagnostic-tag claim is generalized to "lifted at NP, used
  by binding gates". Future SEM_CLASS-based gating (e.g., for
  ``walang sinuman`` PRON-headed RCs, ``mismo`` emphatic
  reflexives, etc.) reuses the lifted path.
- **No inside-out FU for 6.F**. The matrix-rule placement
  is sufficient for local-domain binding and works in
  cross-clausal cases via the existing per-depth threading.
  Inside-out FU stays parked as a Phase 7+ unifier extension
  motivated by future binding work (long-distance ``ibang-
  tao``, picture-NP binding) if those surface in corpus.

### Cross-references

- Plan-of-record §5.6 (``.claude/plans/tgllfg-phase-6.md``).
- K&Z 1989 §3 (``data/tgl/references/Kaplan-Zaenen-1989-LSS-CStruct-FU.pdf``); binding-via-FU
  discussion is implicit in their TOPIC = (TOPIC GF) form.
- Phase 5m Commit 1 (``data/tgl/nouns.yaml`` ``sarili`` lex
  entry; ``SEM_CLASS=REFLEXIVE``).
- Phase 5m Commit 6 (``tests/tgllfg/test_phase5m_\
  reflexive_sarili.py``; ``TestAnaphoraDeferred`` pinned
  test for flipping).
- Phase 6.B Commit 5 (``src/tgllfg/fstruct/unify.py``
  ``_eval_defining_eq`` binding-equation context;
  ``docs/fu-evaluation.md`` §6.5).
- Phase 6.D Commit 2 (the per-depth REL-PRO threading at
  S_XCOMP that 6.F reuses for cross-clausal binding).
- Kroeger 1993 §2.3 — Tagalog binding theory: actor binds
  reflexive, not pivot.
- Ramos 1971 — Tagalog binding domains; secondary reference.
- §18.1.2 L104 entry — closed by 6.F.

### What landed (2026-05-12)

C2 grammar landed 24 binding-rule variants in
``src/tgllfg/cfg/control.py``, mirroring the existing transitive
``voice_specs`` loop (6 voice_specs × 2 NP orders × 2 binding
directions). Each variant fires when SUBJ or the obj_target
(``OBJ`` for AV; ``OBJ-AGENT`` for OV / DV / IV plain;
``OBJ-CAUSER`` for the CAUS=DIRECT variants) has
``LEMMA =c 'sarili'``, setting ``ANTECEDENT`` to the matrix
actor's f-structure via the Phase 6.B C5 binding-equation
context (``_eval_defining_eq`` unifies LHS with the shortest-
depth endpoint of the RHS path).

**Implementation note: LEMMA gating, not SEM_CLASS lift**. The
design appendix laid out two gating options. Option A
(SEM_CLASS lift at the NP projection) was attempted first and
surfaced an unifier quirk: ``(↑ SEM_CLASS) = ↓2 SEM_CLASS`` is
not a no-op when ``↓2`` has no SEM_CLASS — the unifier creates
an empty ``FStructure`` node at ``↑.SEM_CLASS`` (verified by
probe: ``Tumakbo ang bata.`` yielded
``SUBJ.SEM_CLASS=FStructure(feats={}, id=25)``). The C2 grammar
took Option B (gate on ``LEMMA =c 'sarili'`` directly) instead,
which is narrower (only fires on the exact lemma) but doesn't
pollute every NP with an empty SEM_CLASS f-node.

C2 tests landed at
``tests/tgllfg/test_phase5m_reflexive_sarili.py`` —
``TestAnaphoraDeferred`` was flipped to
``TestAnaphoraResolution`` with a ``_find_bound_parse`` helper
that finds the bound parse among the 2-parse output (the new
binding rule fires alongside the existing non-binding rule for
sarili surfaces). 4 parametrized tests across the canonical
1sg / 2sg / 3sg / 3pl GEN-PRON variants.

C3 extended the corpus with 7 more tests:

- ``TestSariliAtAVObject`` (3 parametrized): ``Kumain X ng
  sarili X.`` verifies ``(↑ OBJ ANTECEDENT) = (↑ SUBJ)`` — the
  SUBJ-bound direction for true AV transitives.
- ``TestSariliAtOVSubject`` (3 parametrized): ``Kinain X ang
  sarili X.`` verifies ``(↑ SUBJ ANTECEDENT) = (↑ OBJ-AGENT)``
  — the OBJ-AGENT-bound direction for OV pivots.
- ``TestCrossClausalDeferred`` (1 pinned test): ``Gusto kong
  kumain ng sarili ko.`` parses cleanly today but no binding
  fires; recorded as the deferred xfail-style pin (the
  assertion message nudges the future flip).

**Cross-clausal deferral**: the matrix PSYCH-control rule
doesn't see the embedded sarili directly, so the C2 matrix-rule
binding equations don't fire on cross-XCOMP sarili. Resolution
paths recorded as Phase 7+ scope:

1. Inside-out FU designators (substantial unifier extension).
2. Per-XCOMP binding rules traversing from S_XCOMP body up to
   the matrix's binder (voluminous; awaits cross-clausal
   sarili surfacing in corpus).

The TestCrossClausalDeferred pin will detect future enablement
without code changes.

Final 6.F status: 7 161 fast tests + 19 slow + 1 xfail (the
test_kahit_ano_in_obj cross-case-lex carry-forward from 6.C,
unrelated to 6.F). Lint clean (311 source files). No new
deferrals introduced beyond the cross-clausal item already
itemized in *Out of scope* above (and the Phase 7+
inside-out-FU / resolver-side-cyclic-pruning entries from C1).

## Phase 6.G Commit 1: L32 NP-from-N projection widening — design

**Date:** 2026-05-12. **Status:** active (design commit; grammar
/ test lands in 6.G C2-C3).

### Goal

Close §18.1.2 L32 (*NP-from-N projection of modifier features*)
by widening the NP projection so modifier features
(``CARDINAL_VALUE``, ``ORDINAL_VALUE``, ``SEASON``, ``APPROX``,
``COMP``, ``MEASURE``, ``DISTRIB``, ``WHOLE``, plus the
Phase 6.F-deferred ``SEM_CLASS``) lift from inner N (or NUM /
Q) onto the matrix NP.

Per the user's **anti-deferral guidance** for Phase 6.G: this
commit closes L32 **completely**. No partial work pushed to
Phase 7+; the design covers every modifier-feat path. The
``SEM_CLASS`` lift item (deferred from Phase 6.F C2 when the
naive ``(↑ X) = ↓2 X`` lift surfaced an empty-f-node issue) is
folded into 6.G as part of the same fix.

### The empty-f-node problem (Phase 6.F C2 finding)

Probed during Phase 6.F C2: adding ``(↑ SEM_CLASS) = ↓2
SEM_CLASS`` to the simple NP-from-DET+N rule yields
``SUBJ.SEM_CLASS = FStructure(feats={}, id=N)`` on NPs whose
head N has no SEM_CLASS (verified with ``Tumakbo ang bata.``).
The unifier's ``_resolve_for_write`` for an atomic-path RHS
creates a fresh empty f-node when the source path is undefined
— there's no "if-defined-then-lift" short-circuit. The lift
therefore pollutes every NP with empty f-nodes for every
non-applicable modifier feat.

The same issue surfaces if we naively try to lift APPROX,
SEASON, etc. on multi-daughter NP rules. The Phase 5f Commits
1 / 7 / 14 / 16 workaround was to produce NP directly from
each modifier-bearing rule with the specific lift, avoiding
the bare NP-from-DET+N path. That works for the
modifier-bearing NPs but leaves the L32 problem standing for
NPs whose head N is an N-internal composition (e.g.,
``N → NUM[CARDINAL] PART[LINK] N``) that the bare NP rule
consumes.

### Solution: SHARE+SHARE pattern (bidirectional f-structure sharing)

LFG canonically expresses head-sharing via ``(↑) = ↓i``. The
existing NP-from-DET+N rule shares ``↑`` with the DET daughter
(``(↑) = ↓1``), then explicit-lifts PRED + LEMMA from N. The
empty-f-node issue arises only with the **explicit-lift** form,
not the **share** form.

The fix: add ``(↑) = ↓j`` for the modifier-bearing daughter j,
sharing ↑ with both DET (↓1) and N (↓2) simultaneously. ↓1
and ↓2 unify into a single f-structure; any feat defined on
either side propagates to ↑ automatically, *without* creating
empty f-nodes for undefined feats.

For the canonical 3 NP-from-DET/ADP+N rules:

```text
NP[CASE=X] → CASE-MARKER[CASE=X] N
   (↑) = ↓1
   (↑) = ↓2
```

Result: NP gets ``CASE``, ``MARKER``, ``DEM`` from DET (DEIXIS
when demonstrative), plus ``PRED``, ``LEMMA``, ``FORM``,
``SEM_CLASS`` (if set), and any modifier feats on N (when N is
an N-internal composition). No empty f-nodes; the explicit
PRED + LEMMA lifts become redundant and can be dropped.

For multi-daughter modifier-bearing NP rules (cardinal, ordinal,
season, approx, etc.), the same pattern: share ↑ with the
case-marker AND with the modifier-bearing daughter. Lifts that
were necessary because of explicit-lift pollution become
implicit via shared structure. Empty f-nodes never get created
because no explicit ``(↑ X) = ↓j X`` is needed.

### Conflict analysis

Bidirectional sharing unifies the case-marker and modifier
daughters into one f-structure. We must verify no feat
collisions.

- **CASE**: only on DETs/ADPs. N never carries CASE. ✓
- **MARKER**: only on DETs/ADPs. ✓
- **DEM**: morph analyzer default-fills DEM=false on
  non-demonstrative DETs/ADPs (per ``analyzer.py:269``). N
  never carries DEM. ✓
- **DEIXIS**: only on demonstrative DETs (``ito`` / ``iyan``
  / ``iyon``). N never carries DEIXIS. ✓
- **PRED**: N sets via ``(↑ PRED) = 'NOUN(↑ FORM)'``; DET
  doesn't have PRED. ✓
- **LEMMA**: only on N (from NOUN lex entry). DET doesn't
  have LEMMA. ✓
- **FORM**: every N has FORM (the surface form). DETs also
  have FORM. **Potential conflict**: DET FORM = "ang"; N
  FORM = "bata"; they differ. **However**, the existing rule
  uses ``(↑) = ↓1`` which already shares with DET, including
  DET.FORM. If we ALSO share with N, FORM unifies — values
  conflict — unify fails.

The FORM conflict is the only real concern. **Resolution**:
exclude FORM from the shared structure by not advertising it
on either daughter at the NP-projection step. Looking at
NOUN's f-structure: FORM is set via the NOUN lex entry. Looking
at DET's: also set. The conflict is real.

**Two ways out**:

1. **Drop the share with DET, use share with N + explicit
   lifts from DET**. Keep ``(↑) = ↓2`` (share with N),
   add ``(↑ CASE) = ↓1 CASE``, ``(↑ MARKER) = ↓1 MARKER``,
   ``(↑ DEM) = ↓1 DEM``. DEM is a binary feat that the morph
   analyzer always sets on DETs/ADPs, so the lift is safe.
   DEIXIS would have to be either lifted explicitly (empty-f-
   node risk on non-demonstratives) or omitted (lose access at
   NP level).
2. **Use ``(↑) = ↓1`` and ``(↑) = ↓2`` and accept FORM
   collision: only one of DET.FORM and N.FORM wins**. The
   unifier-level "first defined wins" semantics is order-
   dependent and probably broken on equality.

Option 1 is the cleaner approach. **The DEIXIS empty-f-node
risk is acceptable** because DEIXIS is a string atom (PROX /
MED / DIST), not a binary, and downstream consumers can
check for the specific values rather than presence. Or we can
lift DEIXIS only in a dedicated demonstrative-NP rule
variant.

Actually, **re-evaluation**: looking more carefully at the
empty-f-node behavior, the issue arises from
``_resolve_for_write`` creating a fresh node when the source
path is undefined. The behavior is the same for atomic
(string) and bool feats. So **DEIXIS would create the same
empty-node pollution**.

The cleanest path is:

- **Share with N (``(↑) = ↓2``)** to lift all of N's feats
  (including modifier feats via N-internal composition).
- **Explicit-lift only the always-defined DET feats**: CASE,
  MARKER, DEM (the morph analyzer ensures these are present).
- **Drop the DEIXIS lift**: demonstrative NPs use a separate
  rule (Phase 5e Commit 16 dedicated dem-NP rule) which can
  lift DEIXIS itself.

### Audit of currently-failing modifier-feat lifts

Probed against the post-6.F grammar:

<!-- markdownlint-disable MD013 -->
| Feat | On simple NP? | Where set | Phase 6.G action |
| --- | --- | --- | --- |
| ``CARDINAL_VALUE`` | yes (via dedicated cardinal-NP rule) | NUM | no change to dedicated rule; share-with-N picks it up when N is internally cardinal-composed |
| ``ORDINAL_VALUE`` | yes (via dedicated ordinal-NP rule) | NUM | no change to dedicated rule; share-with-N picks it up for N-internal composition |
| ``SEASON`` | **no** | N (lex `tag-init`) | share-with-N closes |
| ``APPROX`` | **no** | NUM-wrapper (via PART[APPROX] + NUM rule) | needs share-with-NUM on the cardinal-NP rule, or lift on the cardinal-NP rule |
| ``COMP`` (comparative) | n/a | comparative-ADJ rule produces predicative-ADJ, not NP modifier | not L32 scope |
| ``MEASURE`` | yes (via dedicated measure-NP rule) | NUM-measure rule | no change |
| ``DISTRIB`` | **no** | NUM-distrib (tig-) wrapper | needs share-with-NUM on the distrib-NP rule |
| ``WHOLE`` | yes (via dedicated whole-NP rule) | Q (buo) | no change |
| ``SEM_CLASS`` | **no** (6.F deferral) | N (sarili, time nouns) | share-with-N closes |
<!-- markdownlint-enable MD013 -->

So Phase 6.G C2 needs to:

1. Update the 3 simple NP-from-DET/ADP+N rules to use
   share-with-N (``(↑) = ↓2``) + explicit lifts for DET feats
   (CASE / MARKER / DEM).
2. Update the cardinal-NP rule to add share-with-NUM (lifts
   APPROX automatically).
3. Update the distrib-NP rule (Phase 5f Commit 19 tig-) to add
   share-with-NUM.
4. Update the Phase 5e Commit 16 demonstrative-NP rule (if
   needed) to handle DEIXIS lift via dedicated structure.

### Implications for existing tests

The plan §5.7 says:

> Tests that walk down to read the modifier on the inner N
> daughter update to read it on the NP (or both — keep
> walk-down compat for one release).

Under the SHARE+SHARE pattern, N's f-structure IS NP's
f-structure (they're unified). Walk-down via the inner N
daughter accesses **the same** f-structure as the outer NP.
Tests that walk down continue to pass without modification.
Phase 6.G C3 adds parallel NP-level assertions; both pass.

**Two tests need updates**:

1. ``tests/tgllfg/test_phase5m_reflexive_sarili.py::TestSem\
   ClassReflexiveOnMorph::test_sem_class_reflexive_not_in_\
   subj_fstructure`` (Phase 5m C6) — pins SEM_CLASS NOT on
   the SUBJ f-structure. Under 6.G's lift, SEM_CLASS WILL be
   on SUBJ. Flip the test to assert ``SEM_CLASS ==
   'REFLEXIVE'`` is present (or rename to
   ``test_sem_class_lifts_to_subj_fstructure``).
2. ``tests/tgllfg/test_approximators.py`` — the line-66-69
   docstring "Tests walk down to the daughter NUM to read
   APPROX" becomes stale. Update the docstring; tests stay.

No other test impacts expected — all existing tests use
walk-down which preserves the same f-structure under unified
sharing.

### What's in scope for 6.G

- 3 simple NP-from-DET/ADP+N rule updates (share-with-N
  pattern; explicit DET-feat lifts).
- Cardinal-NP rule update (share-with-NUM, lifts APPROX).
- Distrib-NP rule update (share-with-NUM, lifts DISTRIB
  marker).
- Per-modifier test parametrization (C3): cardinal, ordinal,
  season, approx, measure, distrib, whole, plus SEM_CLASS.
- Update of the Phase 5m SEM_CLASS pin test.
- "What landed" post-script in this design appendix (C4).

### What's out of scope (genuinely, not deferred)

- **COMP percolation onto NP**. COMP marks predicative
  comparative ADJ surfaces (Phase 5h ``mas matalino``), not
  NP modifiers. The closest case is comparative N use which
  isn't currently in scope.
- **MEASURE on multi-NP coord**. Already-percolating; no
  cross-coord issue surfaced.
- **DEIXIS percolation on bare-NP path**. Demonstrative DETs
  use a dedicated rule (Phase 5e Commit 16); the bare DET
  case has no DEIXIS to lift. The dedicated demonstrative rule
  can be audited in a follow-on if a non-redundant DEIXIS
  access path surfaces.

These items are **structurally not modifier-feat-lift cases**;
listing them clarifies the L32 scope rather than deferring them.

### Architectural commitments worth carrying forward

- **SHARE+SHARE pattern over explicit-lift** for f-structure
  feat propagation across NP-shell daughters. The unifier's
  ``(↑ X) = ↓i X`` is creating-if-absent (verified during
  6.F C2); ``(↑) = ↓i`` is share-without-pollution.
- **N-internal composition propagates naturally**. The
  ``N → NUM PART[LINK] N`` rule (Phase 5f Commit 1) produces
  an N with CARDINAL_VALUE. Under SHARE+SHARE, that N's
  CARDINAL_VALUE surfaces on the matrix NP when the bare
  NP-from-DET+N rule consumes it. Closes a long-standing L32
  case without dedicated rule shapes.
- **DEIXIS access stays at the demonstrative-NP layer**. The
  bare NP-from-DET+N rule lifts CASE / MARKER / DEM but not
  DEIXIS, because non-demonstrative DETs don't have DEIXIS
  and the explicit-lift would create empty f-nodes.
  Demonstrative NPs handle DEIXIS in their dedicated rule.
- **Phase 6.F SEM_CLASS deferral folded in**. The Phase 6.F
  C2 SEM_CLASS-lift item is closed by the same SHARE+SHARE
  pattern; no separate follow-up needed.

### Cross-references

- Plan-of-record §5.7 (``.claude/plans/tgllfg-phase-6.md``).
- Phase 5f Commit 1 (``cfg/nominal.py`` cardinal-NP rule —
  6.G adds share-with-NUM for APPROX lift).
- Phase 5f Commit 7 (ordinal-NP rule — already lifts
  ORDINAL_VALUE).
- Phase 5f Commit 14 (season-NP rule — N-level lex; 6.G
  closes via simple NP rule share-with-N).
- Phase 5f Commit 16 (approximators — 6.G closes the
  documented APPROX percolation limitation).
- Phase 5f Commit 19 (distributive ``tig-`` — 6.G closes
  DISTRIB percolation).
- Phase 6.F C2 (``project_phase6f_progress``; SEM_CLASS lift
  deferral folded into 6.G).
- §18.1.2 L32 entry — closed by 6.G.

### What landed (2026-05-12)

C2 grammar landed via **SHARE+SHARE** on the 3 simple
NP-from-DET/ADP+N rules in ``src/tgllfg/cfg/nominal.py``
(``(↑) = ↓1, (↑) = ↓2``). Implementation note vs the C1
appendix's Option B preference: the appendix favored
share-with-N + explicit DET lifts due to a feared FORM
conflict. Implementation verified FORM isn't set on DET via
equations (only via lex, which doesn't unify), so the simpler
Option A (SHARE+SHARE) was used. Modifier feats from N
(``SEM_CLASS``, ``SEM_CLASS='SEASON'``, plus any N-internal
modifier-composition feats) propagate to NP via structure-
sharing — no empty-f-node pollution.

C2 also addressed an **N-level-RC ambiguity** the SHARE+SHARE
introduced: the Phase 5n.A C8 N-level RC rule's output N
would, when consumed by the simple NP rule, produce a parse
equivalent to the canonical NP-level RC wrap (Phase 4 §7.5).
Resolution: the N-level RC tags its output with ``(↑ N_RC) =
true`` (binary feat; added to ``BINARY_FEATS`` with companion
audit doc + counter bump); the simple NP rule's
``¬ (↓2 N_RC)`` constraint blocks consumption of N-level-RC'd
Ns. Distinguishable at pass-2 because the tag is set by the
N-level RC's own defining equation, while the canonical
NP-level RC path adds ADJ to N via shared-f-structure but
never sets ``N_RC``. The N-level RC stays load-bearing for the
existential bare-N case (``May bahay na nasa bundok``) — the
existential rule consumes bare N directly.

A parallel ``¬ (↓2 CARDINAL_VALUE)`` constraint on the simple
NP rule blocks the N-level cardinal-composition rule (Phase 5f
Commit 1 companion) from feeding the simple NP rule, keeping
the dedicated NP-level cardinal rule as the unique surface
route for case-marked cardinal NPs.

C3 grammar added explicit ``(↑ APPROX) = ↓2 APPROX`` and
``(↑ DISTRIB) = ↓2 DISTRIB`` lifts to the dedicated cardinal-NP
rule (lifts the modifier feats from the inner NUM daughter
when present). The unifier's creating-if-absent semantics
creates empty ``FStructure`` placeholders on bare cardinals
without an APPROX or DISTRIB wrapper; downstream consumers
checking ``is True`` correctly skip the placeholder. The
empty-f-node convention is pinned by the
``TestEmptyFNodeTolerance`` class in C3.

C3 tests landed at ``tests/tgllfg/test_phase6_np_projection.py``
— 13 tests across 6 classes covering: ``SEM_CLASS`` lifts
(REFLEXIVE + SEASON); cardinal modifier feats
(CARDINAL_VALUE, NUM, APPROX, DISTRIB); ORDINAL_VALUE; WHOLE;
the ``¬ CARDINAL_VALUE`` block on the simple NP rule; the
``¬ N_RC`` block + existential RC + canonical NP-level RC
preservation; and the empty-f-node tolerance convention.

C2 also flipped the Phase 5m ``test_sem_class_reflexive_not_in_
subj_fstructure`` pin to ``test_sem_class_reflexive_lifts_to_
subj_fstructure`` — closing the Phase 6.F C2 SEM_CLASS-lift
deferral as part of L32.

Final 6.G status:

- test-fast: 7 174 passed + 1 xfail (~64s) — ``not postgres
  and not slow``.
- test-slow: 19 passed (~19s) — ``slow`` only.
- test-both: 7 174 + 19 = 7 193 total passed + 1 xfail (~66s
  combined).
- check: clean on 312 source files.

No deferrals introduced. Items recorded as out-of-scope (COMP
percolation, MEASURE-on-coord, DEIXIS-on-bare-NP, MEASURE
lex-blocked) are structurally not L32 cases, not deferred
work.

## Phase 6.H Commit 1: L33 floated-Q agreement + L85+ stress + =c cleanup — design

Eighth sub-PR of Phase 6. Three closure threads land together as
the cleanup-and-verify sub-PR before 6.I (L105) and 6.J (closing
docs):

1. **§18.1.2 L33** — floated-Q number agreement. The Phase 4 §7.8
   float rule and the Phase 5f Commit 23 clause-initial dual-Q
   rules attach ``Q[DUAL=true]`` (``pareho`` / ``kapwa``) to NOM
   antecedents without a NUM agreement check; the SG-SUBJ + DUAL-Q
   surfaces overgenerate today.
2. **§18.1.2 L85+ verification stress** — 6.C C6 added 5/6/7-
   conjunct fixtures; the plan calls for 8/9/10-conjunct stress to
   confirm the recursion is truly unbounded.
3. **The 2 explicitly-tagged ``=c`` non-conflict-matcher-leak
   cleanup sites** — ``clause.py:730`` and ``control.py:548`` are
   redundant under the post-6.C strict matcher and ship as the
   final removal of matcher-leak compensation.

After 6.H, §18.1.2 reduces from 2 → 1 (only L105 remains; closes
in 6.I).

### 1. L33 floated-Q number agreement

#### 1.1 Lexical baseline

``pareho`` and ``kapwa`` are lex'd in ``particles.yaml`` as
``Q[QUANT=BOTH, DUAL=true]``. Their semantic precondition is "two-
or-more entities" — the antecedent (matrix SUBJ) must be PL (or
DU; modern Tagalog has no free DU PRONs, so PL is the only
realized NUM that satisfies DUAL semantics).

#### 1.2 The two rule families today

- **Phase 4 §7.8 base float rule** (``cfg/clitic.py:48-52``) —
  single ``S → S Q`` rule attaches *any* Q (DUAL or not, vague or
  not, ``lahat`` or ``pareho``) at clause-final position as a
  member of the matrix's ``ADJ`` set. No NUM constraint.
- **Phase 5f Commit 23 clause-initial dual-Q rules**
  (``cfg/clitic.py:73-140``) — 6 rules (3 AV-arity frames × 2
  linker variants) fire on ``Q[DUAL]`` + ``PRON[CASE=NOM]`` + ``PART
  [LINK]`` + V. ``(↓1 DUAL) =c true`` belt-and-braces present;
  PRON is unconstrained for NUM.

Probe of the current overgeneration:

```text
1  Kumain sila pareho.    PL SUBJ + DUAL Q — should parse ✓
1  Kumain siya pareho.    SG SUBJ + DUAL Q — should ZERO-PARSE ✗
3  Pareho silang kumain.  PL SUBJ + DUAL Q — should parse ✓
3  Pareho siyang kumain.  SG SUBJ + DUAL Q — should ZERO-PARSE ✗
1  Kumain sila kapwa.     PL SUBJ + DUAL Q — should parse ✓
1  Kumain siya kapwa.     SG SUBJ + DUAL Q — should ZERO-PARSE ✗
```

All four ``*siya``-with-DUAL-Q surfaces parse today; L33 is the
fix.

#### 1.3 Design choice: equation-side gating

Two natural designs:

- **Design A — equation-side gating.** Split the base float rule
  into Q (no DUAL) and Q[DUAL=true] variants; add
  ``(↑ SUBJ NUM) =c 'PL'`` to the DUAL variant. Mirror in the
  Phase 5f Commit 23 rules.
- **Design B — lex-side restriction.** Have PRON lex entries
  declare NUM-compatibility with DUAL Q's upstream (e.g., split
  SG / PL PRON variants with disjoint POS). Lex churn across 8+
  pronouns for narrow benefit; rejected.

**Design A is chosen.** Equation-side gating is the K&Z 1989 §3
idiom for agreement constraints (cf. eq. 17 illustrating
subject-verb agreement via constraining equations).

#### 1.4 Constraining vs. defining

The constraint form is a **constraining equation** ``(↑ SUBJ
NUM) =c 'PL'``, not a defining equation ``(↑ SUBJ NUM) = 'PL'``.

- Constraining fires only if ``SUBJ.NUM`` is already set (always
  the case — PRON lex entries set NUM on the SUBJ projection).
- A defining equation would overwrite ``SG`` with ``PL`` and the
  failure would surface as a later unification conflict — same
  observable outcome but worse diagnostic (failure surfaces at
  the wrong site).

#### 1.5 Why no DUAL propagation

The plan-skeleton's pseudo-equation ``(↑ FLOAT DUAL) = (↑
ANTECEDENT DUAL)`` would propagate ``DUAL`` from antecedent to
the float. Two reasons this is not the right shape:

- **No DUAL PRONs to propagate from.** Modern Tagalog has no
  free DU PRON; the historical 1.IN.DU ``kita`` only appears as a
  fused clitic, never as a free PRON. There is nothing on the
  antecedent's NUM-DUAL axis to propagate.
- **Empty-f-node pollution** (the same Phase 6.G issue). The
  unifier's ``(↑ X) = ↓i X`` is creating-if-absent semantics —
  applying it to ``DUAL`` would create empty-FStructure
  placeholders on every non-DUAL Q-antecedent pair. The
  ``TestEmptyFNodeTolerance`` precedent (6.G) accepts the
  convention for binary feats on direct lifts; but here the
  semantically-correct constraint is one-directional (Q→SUBJ),
  not symmetric propagation.

The constraint thus lives on Q's side (the Q[DUAL=true]
requirement triggers the rule variant), and the agreement check
is on the antecedent's NUM only.

#### 1.6 Grammar diff sketch

**Base float rule split** (``cfg/clitic.py:48-52``):

```python
# Q without DUAL — unconstrained NUM
rules.append(Rule(
    "S",
    ["S", "Q"],
    [
        "(↑) = ↓1",
        "↓2 ∈ (↑ ADJ)",
        "(↓2 ANTECEDENT) = (↑ SUBJ)",
        "¬ (↓2 DUAL)",
    ],
))
# Q[DUAL] — antecedent must be PL
rules.append(Rule(
    "S",
    ["S", "Q[DUAL]"],
    [
        "(↑) = ↓1",
        "↓2 ∈ (↑ ADJ)",
        "(↓2 ANTECEDENT) = (↑ SUBJ)",
        "(↓2 DUAL) =c true",
        "(↑ SUBJ NUM) =c 'PL'",
    ],
))
```

**Phase 5f Commit 23 clause-initial dual-Q rules** (``cfg/
clitic.py:73-140``) — append ``(↑ SUBJ NUM) =c 'PL'`` to each of
the 6 variants (the SUBJ slot is already PRON[CASE=NOM] from
↓2).

#### 1.7 Tests

New file: ``tests/tgllfg/test_phase6_floated_q_agreement.py``
covering:

- ``TestFloatRuleDualAgreement`` — float-rule variant (``Kumain
  sila pareho.`` parses, ``*Kumain siya pareho.`` zero-parses);
  parametrized for {``pareho``, ``kapwa``} × {``sila`` /
  ``siya``}.
- ``TestClauseInitialDualAgreement`` — clause-initial variant
  (``Pareho silang kumain.`` parses, ``*Pareho siyang kumain.``
  zero-parses); same parametrization × 2 linker variants × 3
  AV-arity frames.
- ``TestNonDualQUnaffected`` — regression: ``lahat`` /
  ``marami`` / ``konti`` floats compose with both SG and PL
  antecedents (no NUM constraint on non-DUAL Q's).

### 2. L85+ 8/9/10-conjunct stress

Phase 6.C C6 added 5/6/7-conjunct fixtures (``TestFivePlus
ConjunctNomCoord`` + ``TestSixSevenConjunctNomCoord`` in
``tests/tgllfg/test_phase5n_4conj_coord.py``). The plan calls
for 8/9/10-conjunct stress fixtures to confirm the recursion is
truly unbounded.

New class: ``TestEightNineTenConjunctNomCoord``. Each surface
has the form ``Kumain ang X1, ang X2, ..., ang X_{N-1} at ang
XN.``

Vocab: kinship terms from ``data/tgl/nouns.yaml`` (tatay /
nanay / kuya / ate / lolo / lola / tito / tita / pinsan /
kapatid). At 10 conjuncts we exhaust the canonical roster; any
lex gap surfaces as a parse failure and is closed by adding the
lex entry (parallel to the 6/7-conjunct stress pattern).

### 3. =c cleanup

Two sites drop:

#### 3.1 clause.py:730 — predicative-Q ``(↓1 VAGUE) =c true``

```python
rules.append(Rule(
    "S",
    ["Q[VAGUE]", "NP[CASE=NOM]"],
    [
        "(↑ PRED) = 'Q-PREDICATIVE <SUBJ>'",
        # ...
        "(↓1 VAGUE) =c true",   # ← drop
        "¬ (↓1 WH)",
    ],
))
```

The ``Q[VAGUE]`` daughter pattern in the RHS list already gates
``VAGUE=true`` on the candidate under the post-6.C strict
matcher (``expected.keys() ⊆ candidate.keys()`` + shared-key
compat). The ``=c`` is redundant.

#### 3.2 control.py:548 — wh-indirect-Q ``=c COMP_TYPE`` and ``=c Q_TYPE``

```python
rules.append(Rule(
    "S_INTERROG_COMP",
    ["PART[COMP_TYPE=INTERROG]", "S[Q_TYPE=WH]"],
    [
        "(↑) = ↓2",
        "(↑ COMP_TYPE) = 'INTERROG'",
        "(↓1 COMP_TYPE) =c 'INTERROG'",  # ← drop
        "(↓2 Q_TYPE) =c 'WH'",           # ← drop
    ],
))
```

Both ``=c`` are redundant: the PART[COMP_TYPE=INTERROG] and
S[Q_TYPE=WH] daughter patterns gate them under strict matching.

#### 3.3 Scope clarification

The plan-of-record's §4.2 decision is explicit: drop only the
2 sites that are explicitly tagged as "non-conflict-matcher
leak" in the source code. The other ~373 ``=c`` sites are
legitimate semantic gating (voice selection, completeness
conditions, etc.) that survive the parser swap untouched; broad
cleanup is opportunistic future-phase work.

The ``(↓1 DUAL) =c true`` belt-and-braces in the Phase 5f
Commit 23 clause-initial rules (clitic.py:90 / 113 / 138) is
*not* tagged as a non-conflict-matcher leak in source; it is
left in place for 6.H. Future opportunistic cleanup may remove
it (it is redundant under Q[DUAL] daughter + strict matcher).

### 4. Sub-commit ledger (post-design sign-off)

- **C2** — L33: split base float rule + add NUM constraint to
  Phase 5f Commit 23 rules + author L33 tests.
  ``hatch run test-both`` gate.
- **C3** — L85+: 8/9/10-conjunct stress fixtures. ``hatch run
  test-both`` gate (test-only commit; the new fixtures exercise
  the post-6.C recursion).
- **C4** — Drop the 2 ``=c`` leak sites. ``hatch run test-both``
  gate.
- **C5** — Closing docs.

### 5. Out-of-scope items (structurally, not deferred)

- **Other floated Q agreement** — vague-Q's (``marami`` /
  ``konti``) and ``lahat`` compose with SG / mass / collective
  antecedents semantically; no NUM constraint applies.
- **DU NUM** — if a future Phase adds free DU PRONs (e.g.,
  ``kita`` lifted from clitic-only status), the constraint
  becomes ``(↑ SUBJ NUM) =c 'PL' ∨ 'DU'``; current scope is
  PL only.
- **Cross-clausal dual-Q agreement** — the inside-out FU
  designator needed to bind a clause-internal dual-Q to a
  matrix antecedent is Phase 7+ unifier extension (same path
  as the cross-clausal sarili deferral from 6.F).
- **Floated-Q gender / case agreement** — Tagalog Qs have no
  gender; CASE is fixed via the NOM-antecedent restriction
  (DUAL Q's bind NOM-PRONs only).
- **Bracketed-feat tightening of other rules** — additional
  ``=c`` sites that *could* be dropped under the strict matcher
  remain in place; the plan-of-record §4.2 limits 6.H to the 2
  explicitly-tagged sites.

### What landed (2026-05-12)

Phase 6.H landed in 4 numbered commits (C1 design appendix +
C2 L33 grammar + tests + C3 L85+ stress + C4 ``=c`` cleanup) +
C5 closing docs sweep. test-fast: 7 198 passed + 1 xfailed
(~68s). test-slow: 19 passed (~20s). test-both combined:
7 217 + 1 xfailed (~68s). check: clean on 313 source files.

#### L33 — three-variant split, not two

The C1 sketch had a two-variant split on the base float rule
(bare Q vs. Q[DUAL=true] with ``(↑ SUBJ NUM) =c 'PL'``). The
single ``=c 'PL'`` constraint zero-parsed five test-corpus
fixtures using nominal SUBJs (``Kumain ang bata pareho.`` /
``Kumain ang bata kapwa.`` and friends). Tagalog NPs without
``mga`` are number-neutral — the bare NP ``ang bata`` has no
NUM feat in its f-structure, so strict ``=c 'PL'`` fails.

C2 landed a **three-variant split**:

1. Bare Q (no DUAL): unconstrained NUM. Covers ``lahat`` /
   ``marami`` / ``konti``.
2. Q[DUAL=true] + PL antecedent: ``(↑ SUBJ NUM) =c 'PL'``.
   Covers PL pronouns (``sila`` / ``kami`` / ``tayo`` /
   ``kayo``) and PL-marked cardinals (``ang dalawang bata``
   projects NUM=PL).
3. Q[DUAL=true] + NUM-unmarked antecedent: ``¬ (↑ SUBJ NUM)``.
   Covers Tagalog's number-neutral bare NPs.

SG antecedents fail both DUAL variants — variant 2 wants PL,
variant 3 wants NUM-undefined. The Phase 5f Commit 23 clause-
initial rules' SUBJ daughter is already ``PRON[CASE=NOM]``
(pronouns always have NUM set), so only ``(↑ SUBJ NUM) =c
'PL'`` is needed there (no three-variant split).

#### Predicative-ADJ polysemy is structurally out of L33 scope

``pareho`` and ``kapwa`` are polysemous — also lex'd in
``adjectives.yaml`` as ``ADJ[EQUATIVE=true, COMP_DEGREE=
EQUATIVE]`` (Phase 5h Commit 2 equative-identity predicate)
in addition to the Q[DUAL] particle entry. After C2,
``*Pareho siyang kumain.`` still produces 2 parses — both via
the predicative-ADJ rule (``S → ADJ NP``) with ``pareho`` as
the predicate and ``siyang kumain`` as a pronoun-headed RC
NP ("the one who ate is the same"). PRED is ``'ADJ <SUBJ>'``
(literal), not ``'kumain <SUBJ>'``. Structurally distinct
from the Q-floated reading; the L33 fix targets only the
Q-floated path.

The test helpers ``_has_dual_q_reading`` /
``_count_dual_q_parses`` in
``tests/tgllfg/test_phase6_floated_q_agreement.py`` filter
for the Q-floated reading (matrix's ``ADJ`` contains a
``DUAL=true`` Q member). The filter is the right shape:
the predicative-ADJ rule licenses parses like ``Pareho ang
kanilang sapatos.`` "their shoes are the same" legitimately,
and a count-based test would mis-handle the polysemy. Filter
by f-structure shape, not parse count.

Recorded as Out-of-scope item §5 alongside the original five
(other floated Q's, DU NUM, cross-clausal dual-Q agreement,
Q gender / case, broader ``=c`` cleanup).

#### ``mga`` NP-pluralization gap surfaced and formally tracked

L33 closure probing surfaced a pre-existing gap: ``Kumain ang
mga bata.`` zero-parses today. ``mga`` is lex'd as
``PART[PLURAL_MARKER=true]`` (Phase 5f Commit 14
``particles.yaml``) and the NP-internal pluralization rule
(``DET PART[mga] N`` producing NP[NUM=PL]) was deferred at
that time as "substantial scope" (``docs/analysis-choices.md``
Phase 5f Commit 14 design appendix, line 7187).

This gap was documented only in-source until 6.H surfaced it
during L33 probe regression analysis. Phase 6.H C5 closing
docs adds a formal entry to ``.claude/plans/tgllfg-out-of-
scope.md`` §18.1.1 Corpus-deferred. Canonical PL forms parse
fine today via cardinal-NP (``ang dalawang bata``) and PL
pronouns; revisit when corpus pressure surfaces unconstrained
``mga`` NP-pluralization as motivating.

The L33 fix specifically accommodates ``mga``-marked NPs once
the gap closes: variant 2 (``(↑ SUBJ NUM) =c 'PL'``) fires
when the NP projects NUM=PL via ``mga``, parallel to the
cardinal-NP case verified today.

#### Architectural commitments worth carrying forward

- **Rule-split for NUM agreement on number-neutral NPs**. Where
  a constraint should fire on "PL or unmarked" but not "SG",
  split into two rule variants (``=c 'PL'`` + ``¬ NUM``) rather
  than seek a NUM-disjunction operator. The split is
  observably cheap (post-Phase-6.C strict matcher's predict-
  time pruning means non-matching variants don't proliferate
  chart entries).
- **Filter by f-structure shape, not parse count, when
  polysemy is in play**. Lex polysemy (``pareho`` Q vs. ADJ)
  produces multiple legal parses via different rules; a
  count-based agreement test conflates the rule paths. Filter
  on the agreement-relevant f-structure shape (here: ADJ
  set membership of the DUAL Q).
- **Surface deferrals while probing**. The ``mga``
  NP-pluralization gap was tracked only as a source comment
  for ~8 days before L33 probing surfaced it. The closing-docs
  sweep is the right time to fold informal source-comment
  deferrals into the formal §18 inventory.

#### Final 6.H status

- test-fast: 7 198 passed + 1 xfailed (~68s) — ``not postgres
  and not slow``. +24 from 6.G baseline (21 new L33 + 3 new
  L85+ stress).
- test-slow: 19 passed (~20s) — ``slow`` only.
- test-both: 7 198 + 19 = 7 217 total passed + 1 xfailed (~68s
  combined).
- check: clean on 313 source files.

No deferrals introduced. Recorded out-of-scope items (other
floated Q's, DU NUM, cross-clausal dual-Q agreement, Q
gender / case, broader ``=c`` cleanup, predicative-ADJ
polysemy) are structurally not L33 cases. The ``mga``
NP-pluralization gap was promoted from informal source-comment
deferral to formal §18.1.1 Corpus-deferred entry as part of
this sweep.

After 6.H, §18.1.2 inventory shrinks from 2 → 1 (only L105
remains, closes in 6.I). After 6.I + 6.J, §18.1.2 closes
entirely.

## Phase 6.I Commit 1: L105 productive ADV reduplication — design

Ninth sub-PR of Phase 6 (last functional sub-PR before 6.J
cumulative closing docs). Closes §18.1.2 L105 — productive
reduplication of ``paminsan-minsan`` "occasionally" and (the
infrastructure for) other reduplicated ADV stems.

After 6.I, §18.1.2 closes entirely; 6.J ships only cumulative
docs / memory hygiene.

### 1. Lexical baseline

``minsan`` "sometimes / once" is lex'd in ``particles.yaml``
as ``ADV[ADV_TYPE=FREQUENCY, FREQ_VALUE=SOMETIMES, LEMMA=
minsan]``. The reduplicated form ``paminsan-minsan``
"occasionally" is lex'd as a separate **static** entry:

```yaml
- surface: paminsanminsan
  pos: ADV
  feats: {ADV_TYPE: FREQUENCY, FREQ_VALUE: OCCASIONAL,
          LEMMA: paminsan-minsan}
```

The Phase 5f Commit 14 ``merge_hyphen_compounds`` tokenizer
pre-pass collapses ``paminsan-minsan`` (three tokens
``paminsan`` ``-`` ``minsan``) into the single token
``paminsanminsan`` for analyzer lookup. The static entry's
``LEMMA: paminsan-minsan`` carries the canonical hyphenated
form back through.

L105 calls for **productive** derivation: a paradigm cell
that derives ``paminsan-minsan``-class surfaces from base
ADV-FREQUENCY roots, with the productive ``pa-`` prefix and
root reduplication encoding the OCCASIONAL frequency shift.

### 2. Paradigm cell shape

The cell mirrors the Phase 5n.C.3 Commit 9 ``redup_wh_plural``
precedent (closest existing productive-redup pattern). The
ops are ``[prefix "pa", redup_root]`` — the same shape used
by ``redup_intens_adj`` (Phase 5n.C.3 Commit 7) for ADJ
intensives like ``magandaganda``.

```yaml
- base_pos: ADV
  affix_class: adv_redup
  operations:
    - {op: prefix, value: "pa"}
    - {op: redup_root}
  feats: {ADV_TYPE: FREQUENCY, FREQ_VALUE: OCCASIONAL}
  notes: adv_redup — minsan → paminsanminsan (L105)
```

The cell's ``feats`` shifts ``FREQ_VALUE`` from the source's
``SOMETIMES`` to the derived ``OCCASIONAL``. ``ADV_TYPE=
FREQUENCY`` is set explicitly to override any non-FREQUENCY
ADV-base that wires ``affix_class: [adv_redup]`` in the
future (defensive; bare ``minsan`` already has it).

### 3. Particle paradigm dispatch (new infrastructure)

Currently, the paradigm engine dispatches on root POS in
``analyzer.py`` (NOUN / ADJ / NUM / PRON) — particles do
**not** participate. Adding ADV-redup requires:

#### 3.1 ``Particle.affix_class`` field

Add ``affix_class: list[str]`` to the ``Particle`` dataclass
(``morph/paradigms.py:186``) and a loader hook
(``morph/loader.py``) to parse ``affix_class`` from YAML
records. Empty by default — no behavior change for existing
particles.

#### 3.2 ``_index_particle_paradigms`` method

New method on ``MorphologicalAnalyzer`` parallel to
``_index_pronoun_paradigms`` (line 411). Iterates
``self._data.paradigm_cells`` filtering by
``cell.base_pos == particle.pos`` (so a cell with
``base_pos: ADV`` fires only on particles with
``pos: ADV``) and ``_affix_class_match(cell.affix_class,
p.affix_class)``. For each match: synthesize a Root from
the Particle, run ``generate_form``, index the derived
surface into ``self._index.particles`` with the merged
feats.

Dispatch wired from the particle-loading loop (analyzer.py
line 302-308 — the existing ``self._index.particles.
setdefault(...)`` block).

#### 3.3 LEMMA construction for redup_root-final cells

The static entry's ``LEMMA: paminsan-minsan`` preserves the
canonical hyphenated form. Productive derivation needs an
equivalent. Approaches considered:

1. **Hard-code LEMMA in cell.feats**. Wrong shape — the cell
   fires on multiple roots and LEMMA varies per root.
2. **LEMMA template in cell.feats with ``{root}`` placeholder**.
   New mini-DSL; complexity > value for a single use-case
   today.
3. **Compute from surface**. The cell's last op is
   ``redup_root``, which appends ``root.citation`` to the
   prefixed base. The canonical hyphenated LEMMA is the
   prefixed base + ``"-"`` + ``root.citation``. The
   dispatcher tracks the pre-redup_root base by re-applying
   the ops without the trailing ``redup_root`` (or by
   capturing intermediate state in a new
   ``generate_form_with_split`` helper).

**Decision: Option 3** — compute LEMMA from the cell's op
sequence. The dispatcher applies all ops *except* the final
``redup_root`` (if present) to get the pre-redup base, then
LEMMA = ``pre_redup_base + "-" + root.citation``.

For cells that don't end in ``redup_root``, LEMMA defaults
to ``root.citation`` (the source ADV's surface) — the
existing default in ``_index_paradigm_via_base_pos``.

For ``minsan`` + the ``adv_redup`` cell:

- Pre-redup base: ``"pa" + "minsan"`` = ``"paminsan"``.
- Generated surface: ``"paminsan" + "minsan"`` = ``"paminsanminsan"``.
- Canonical LEMMA: ``"paminsan" + "-" + "minsan"`` = ``"paminsan-minsan"``.

Both match the current static entry's behavior.

### 4. Root-side wiring

Modify the existing ``minsan`` lex entry to add
``affix_class: [adv_redup]``:

```yaml
- surface: minsan
  pos: ADV
  affix_class: [adv_redup]
  feats: {ADV_TYPE: FREQUENCY, FREQ_VALUE: SOMETIMES,
          LEMMA: minsan}
```

The bare ``minsan`` analysis continues to index unchanged via
the existing particle-loading loop (the affix_class addition
is purely for paradigm cell matching).

### 5. Static entry removal

After C2's paradigm-engine extension lands and C3's
``minsan`` wiring fires, the static
``paminsanminsan`` entry in ``particles.yaml`` becomes
redundant. C3 removes it and verifies the productive
analyzer output matches the pre-removal static analysis
(same surface, same feats, same LEMMA).

### 6. Other reduplicated ADV stems

The plan title says "Productive redup of ``paminsan-minsan``
and other reduplicated ADV stems". The 6.I lex audit finds
**no other** ADV-FREQUENCY entries with a parallel ``pa-X-X``
form attested in S&O 1972 §3.5, R&B 1986 ch. 4, or the
existing corpus:

- ``madalas`` "often" — no ``pamadalas-madalas`` form.
- ``palagi`` / ``lagi`` "always" — no ``pa-`` redup.
- ``parati`` (synonym of ``palagi``) — already pa-prefixed in
  citation; no further redup.

Other Tagalog ADV redup patterns exist (e.g., ``araw-araw``
"daily" — but this is NOUN-class, not ADV), but they don't
share the ``pa-X-X`` morphology and are out of L105 scope.

The productive ADV-redup infrastructure is therefore
**inventory-of-one** today, but enables future entries via
simple lex-side wiring (``affix_class: [adv_redup]``). The
empty-inventory case is intentional: matching the Phase 6.G
pattern of "productive-paradigm infrastructure even when only
one current entry uses it".

### 7. Sub-commit ledger (post-design sign-off)

- **C2** — Paradigm-engine extension: ``Particle.affix_class``
  field + ``_index_particle_paradigms`` method + LEMMA
  computation for redup_root-final cells + ``adv_redup``
  paradigm cell. No lex changes; the cell fires on no
  current entries (since no particle has ``affix_class:
  [adv_redup]`` yet). Tests verify the engine wiring works.
  ``hatch run test-both`` gate.
- **C3** — Migrate ``minsan`` lex entry: add ``affix_class:
  [adv_redup]``; remove the static ``paminsanminsan`` entry.
  Verify the productive analyzer output equals the
  pre-removal static analysis. Flip
  ``test_paminsan_minsan_single_parse`` to assert via the
  productive mechanism (the surface-level assertion stays;
  add a probe that the new analysis carries the productive
  feats). ``hatch run test-both`` gate.
- **C4** — Closing docs.

### 8. Scope clarifications / out-of-scope items

- **Hyphen-merge tokenizer pre-pass retention**. The
  ``merge_hyphen_compounds`` pre-pass continues to collapse
  ``paminsan-minsan`` → ``paminsanminsan`` at tokenization
  time. The productive paradigm generates the joined form
  ``paminsanminsan`` (no hyphen), so analyzer lookup still
  uses the joined surface. The hyphen-merge pre-pass is
  **not** removed in 6.I — it's still load-bearing for the
  many other hyphen-compound surfaces (``tag-init`` /
  ``daan-daan`` / ``humigit-kumulang`` / ``tig-isa`` /
  ``kani-kaniya`` / ``mag-isa`` / ``magkapareho`` etc.).
- **POS-flipping ADV cells**. The current ``adv_redup`` cell
  outputs ADV (same as base). Future cells could POS-flip
  (e.g., NOUN ``araw-araw`` from NOUN ``araw``), but that's
  out of L105 scope — the dispatch infrastructure supports
  ``cell.pos`` overrides (parallel to ``kani_redup``
  PRON → Q), enabled when needed.
- **Non-FREQUENCY ADV redup**. If a corpus surfaces a non-
  FREQUENCY ADV redup pattern, a parallel cell with different
  ``feats`` lands; the infrastructure supports it.
- **Sandhi on adv_redup**. The current ``minsan`` redup is
  vowel-initial concatenation without sandhi. If a future
  ADV-redup root requires sandhi (e.g., final /d/ → /r/),
  the existing ``d_to_r`` post-processor in ``generate_form``
  handles it via ``root.sandhi_flags``.
- **Productive paradigm for other corpus-attested ADV redup
  forms**. The lex audit found no immediate candidates beyond
  ``paminsan-minsan``; future Tagalog corpus expansion may
  surface more.

### What landed (2026-05-13)

Phase 6.I landed in 4 numbered commits (C1 design appendix +
C2 paradigm-engine extension + C3 lex migration + tests + C4
closing docs). test-fast: 7 200 passed + 1 xfailed (~67s).
test-slow: 19 passed (~20s). test-both combined: 7 219 + 1
xfailed (~67s). check: clean on 313 source files.

#### C2 → C3 — design realized faithfully

The C2 paradigm-engine extension landed as designed (no
expansion of scope):

- ``Particle.affix_class: list[str]`` added with empty-list
  default; existing particles get a no-op field.
- ``_load_particles`` extended to parse ``affix_class`` from
  YAML with list-typed validation.
- ``_index_particle_paradigms`` method added parallel to
  ``_index_pronoun_paradigms``; dispatched from the
  particle-loading loop only when ``p.affix_class`` is
  non-empty (zero overhead for the typical case).
- LEMMA construction for redup_root-final cells builds a
  shallow clone of the cell with the trailing ``redup_root``
  op stripped, re-runs ``generate_form`` to obtain the
  pre-redup base, then sets ``canonical_lemma =
  pre_redup_base + "-" + p.surface``. Other cells fall
  through to ``feats.get("LEMMA", p.surface)``.

The C3 migration produced an analysis identical (byte-for-
byte equal) to the pre-migration static entry:

```python
# Pre-migration (static entry):
MorphAnalysis(
    lemma='paminsan-minsan',
    pos='ADV',
    feats={'ADV_TYPE': 'FREQUENCY',
           'FREQ_VALUE': 'OCCASIONAL',
           'LEMMA': 'paminsan-minsan'}
)
# Post-migration (productive via adv_redup cell):
MorphAnalysis(
    lemma='paminsan-minsan',
    pos='ADV',
    feats={'ADV_TYPE': 'FREQUENCY',
           'FREQ_VALUE': 'OCCASIONAL',
           'LEMMA': 'paminsan-minsan'}
)
```

The downstream parse-pipeline and f-structure see no
difference; the existing parametrized fixture
``("Pumupunta ako paminsan-minsan.", "PUNTA", "paminsan-
minsan", "OCCASIONAL")`` passes via the productive path
without test changes.

#### Test coverage: same-surface assertions + productive-mechanism pins

The original pinned test ``test_paminsan_minsan_single_parse``
stays (single-parse invariant preserved across the migration);
docstring updated to describe the post-6.I mechanism. New
``TestPaminsanMinsanProductive`` class adds 2 explicit
productive-mechanism assertions:

- ``test_productive_analysis_matches_baseline``: the analysis
  carries the canonical hyphenated LEMMA, FREQ_VALUE, and
  ADV_TYPE.
- ``test_bare_minsan_unaffected``: the bare ``minsan``
  SOMETIMES analysis indexes unchanged.

#### Architectural commitments worth carrying forward

- **Particle paradigm dispatch parallels pronoun dispatch**.
  The new ``_index_particle_paradigms`` method follows the
  Phase 5n.C.3 Commit 5 ``_index_pronoun_paradigms``
  pattern — same synthetic-Root construction, same affix-
  class filtering, same per-cell LEMMA-merge logic. Future
  PART-class productive derivations (DET / ADP / Q) can
  reuse the same dispatch infrastructure by setting
  ``base_pos`` on the paradigm cell.
- **LEMMA construction for redup_root-final cells via
  pre-redup-base hyphenation**. The pattern generalizes to
  any future cell ending in ``redup_root`` — no per-cell
  LEMMA template needed. The dispatcher inspects the cell's
  final op and applies the hyphenation rule
  ``pre_redup_base + "-" + root.citation`` automatically.
- **Inventory-of-one infrastructure is fine when the
  infrastructure benefit is clear**. Mirrors the Phase 6.G
  pattern (SHARE+SHARE on 3 simple NP rules, even though
  only L32 closure exercised it initially). Future Tagalog
  corpus expansion can wire additional ADV redup forms via
  lex-side ``affix_class: [adv_redup]`` without paradigm-
  cell changes.

#### Final 6.I status

- test-fast: 7 200 passed + 1 xfailed (~67s) — +2 from 6.H
  baseline (the 2 new productive-mechanism tests in
  ``TestPaminsanMinsanProductive``).
- test-slow: 19 passed (~20s) — slow only.
- test-both: 7 200 + 19 = 7 219 total passed + 1 xfailed
  (~67s combined).
- check: clean on 313 source files.

No deferrals introduced. The structural out-of-scope items
in §8 (hyphen-merge pre-pass retention, POS-flipping ADV
cells, non-FREQUENCY ADV redup, sandhi, other ADV redup
forms) are forward-looking infrastructure capacities, not
deferred L105 work.

After 6.I, **§18.1.2 closes entirely** — all 8 §18.1.2
inventory items (L32 / L33 / L47 / L85+ / L93 / L104 /
L105 / parser non-conflict-matcher) have been resolved
across Phases 6.C through 6.I. Phase 6.J cumulative closing
docs is all that remains.

## Phase 6 cumulative summary (2026-05-13)

Phase 6 delivered the canonical Kaplan & Zaenen 1989 LFG
architecture for tgllfg across 10 sub-PRs (6.A–6.J),
spanning ~3 weeks of implementation. The transition is
complete; §18.1.2 closes entirely.

### Architectural changes (Phase 6.A–6.C)

- **6.A — Atomic unification.** `FGraph.unify` rewritten
  with snapshot/rollback semantics via per-mutation undo
  journal. Hard prerequisite for FU evaluation, which
  enumerates multiple endpoints and requires per-attempt
  rollback on failure. PR #37 (`610ba8f`).
- **6.B — Functional uncertainty.** `_resolve_regex_for_read`
  in `fstruct/fu.py` implements the Kaplan & Maxwell 1988
  FSA traversal with visited-set cycle prevention, K&Z 1989
  §3 minimality clause, off-path constraint evaluation, and
  binding-equation context (regex RHS + reentrant LHS). The
  evaluator supports concatenation, `F*`, `F+`, `F | G`
  alternation; `{F | G}*` Kleene-on-alternation parked as
  Phase 7+ AST extension. PR #38 (`dad22c4`).
- **6.C — Graph-constraint matcher.** `cfg/compile.py:matches`
  switched from "non-conflict" semantics (which silently
  admitted shared-key-absence matches) to strict matching
  (`expected.keys() ⊆ candidate.keys()` + value compat on
  shared keys). The strict matcher is what K&Z 1989 §3
  c-structure faithfulness demands and what makes
  bracketed-feat daughter patterns load-bearing. ~50%
  test-fast wall-time speedup as a side effect (predict-time
  pruning removes spurious binary fanout). PR #39
  (`9bb2ec3`). Closes §18.1.2 non-conflict-matcher +
  L85+ 5+-conjunct flat NP coord.

### §18.1.2 inventory closures (Phase 6.D–6.I)

The seven L-numbered §18.1.2 carry-forwards landed across
six sub-PRs, each picking up one or two related closures:

<!-- markdownlint-disable MD013 -->

| Phase | PR | §18.1.2 closure | Realization |
| --- | --- | --- | --- |
| 6.D | #40 (`4721fc5`) | L47 long-distance wh-extraction | S_XCOMP-bodied RC wrap rules with K&Z 1989 §3 eq. 39 constraining-form binding `(↓3 REL-PRO) =c (↓3 XCOMP* SUBJ)`. |
| 6.E | #41 (`731ad29`) | L93 free relative `kung sino` / `kung ano` as DPs | 3 NP wrap rules consuming `S_INTERROG_COMP[Q_TYPE=WH]` with `FREE_REL=true` head marker. |
| 6.F | #42 (`67ab020`) | L104 `sarili` anaphora binding | 24 binding-rule variants in `cfg/control.py` mirroring the transitive `voice_specs` loop (Kroeger 1993 §2.3 actor-binder); LEMMA-gated. |
| 6.G | #43 (`711aeb4`) | L32 NP-from-N projection of modifier feats | SHARE+SHARE `(↑) = ↓1, (↑) = ↓2` on simple NP rules + explicit APPROX/DISTRIB lifts on cardinal-NP rule; `N_RC` tag-feat blocks N→NP RC double-firing. |
| 6.H | #44 (`3349e2f`) | L33 floated-Q number agreement + L85+ stress + 2 `=c` cleanup | Three-variant base float rule split (bare Q / Q[DUAL]+`=c 'PL'` / Q[DUAL]+`¬ NUM`); 8/9/10-conjunct stress fixtures; 2 explicitly-tagged matcher-leak sites dropped. |
| 6.I | #45 (`a1469af`) | L105 productive ADV reduplication | New `Particle.affix_class` field + `_index_particle_paradigms` analyzer dispatch + `adv_redup` paradigm cell; static `paminsanminsan` migrated to productive derivation from `minsan`. |

<!-- markdownlint-enable MD013 -->

### Cross-cutting architectural commitments

These patterns surfaced during Phase 6 and are worth carrying
forward into future phases:

- **K&Z 1989 §3 c-structure faithfulness**. No phantom NP
  daughters or empty-extraction-site non-terminals; long-
  distance dependencies live in the equation language and
  the unifier, not in c-structure rules.
- **Constraining-form `=c` over defining-form `=` for
  graph-existing endpoints**. The constraining form fires
  only when the path is already defined; gives correct
  diagnostics at the right site and avoids creating-if-absent
  pollution.
- **Rule-split for "PL or undefined" semantics**. Use a
  rule-variant approach (`=c 'PL'` + `¬ NUM`) rather than
  seeking a NUM-disjunction operator. Post-6.C strict-matcher
  predict-time pruning makes rule splits cheap.
- **Tag-feat blocks for N-level-vs-NP-level ambiguity**.
  When SHARE+SHARE introduces ambiguity with companion N-level
  rules, tag the N-level output with a distinct binary feat
  (e.g., `N_RC`) and add `¬ (↓2 N_RC)` to the NP-level rule.
- **Anti-deferral closure pattern**. Fold related deferrals
  into the same fix where infrastructure overlaps (e.g.,
  Phase 6.F C2 SEM_CLASS-lift deferral folded into 6.G L32
  closure).
- **Inventory-of-one infrastructure is fine**. Phase 6.G's
  SHARE+SHARE NP rules and 6.I's `adv_redup` paradigm cell
  each have only one current consumer but enable trivial
  future extension via lex-side wiring.
- **Particle paradigm dispatch parallels pronoun dispatch**.
  Phase 6.I's `_index_particle_paradigms` follows the
  Phase 5n.C.3 Commit 5 `_index_pronoun_paradigms` pattern;
  future PART-class productive derivations reuse the
  infrastructure by setting `base_pos` on the paradigm cell.

### Phase 7+ unifier extensions parked

Items deferred during Phase 6 to a future unifier-extension
phase (see `.claude/plans/tgllfg-out-of-scope.md` §18.1.3):

- **FU deferred defining-equation evaluation** (from 6.D).
  Defining-equations with regex-path RHS evaluate parent-
  first at the c-node's f-graph snapshot during pass 1;
  endpoints introduced by child equations aren't yet visible.
  Phase 6.D worked around by switching the canonical K&Z 1989
  §3 eq. 39 binding form `(↓3 REL-PRO) = (↓3 XCOMP* SUBJ)`
  to constraining form `=c` (evaluates in pass 2 after
  children).
- **FU inside-out designators** (from 6.F). Standard
  Dalrymple 2001 ch. 14 inside-out path designators
  (`((SUBJ ↑) GF)`-style) are not currently supported by
  `resolve_regex_for_read`. Phase 6.F worked around by
  placing sarili binding equations on matrix S rules;
  cross-clausal sarili in XCOMP bodies is the deferred
  motivating case (pinned by `TestCrossClausalDeferred`).
- **FU resolver-side cyclic-endpoint pruning** (from 6.F).
  K&Z 1989 §3 minimality picks the shortest-depth endpoint;
  if the canonical endpoint causes a cyclic unification, the
  resolver currently returns it and `graph.unify` fails.
  Phase 6.F used equation-side exclusion (separate rule
  variants per voice spec) instead.
- **Per-XCOMP binding rules for cross-clausal sarili**
  (from 6.F). Alternative path to inside-out FU; awaits
  cross-clausal sarili surfacing as motivating.
- **`{F | G}*` Kleene on alternation** (from 6.B C6). AST
  extension is well-scoped but not yet motivated by Tagalog
  applications.
- **Conditional-lift mechanism for atomic-path defining
  equations** (from 6.G). The unifier's `(↑ X) = ↓i X` is
  creating-if-absent; for binary-feat lifts on optional
  modifiers, SHARE+SHARE works around but a conditional-lift
  primitive would be cleaner.

### Test counts across Phase 6

- Pre-Phase-6 (6.A entry point): 7 024 fast tests.
- Post-Phase-6 (6.I exit): 7 200 fast + 19 slow + 1 xfail =
  7 219 combined; lint clean on 313 source files.
- Net Phase 6 test-corpus growth: +176 fast tests (+2.5%
  test count) across new construction classes:
  cross-clausal RC (19 tests), free-relative kung-S (15
  tests), sarili binding (parametrized + parametrized cross-
  clausal, ~10 tests), NP-from-N projection (13 tests),
  floated-Q agreement (21 tests), L85+ stress (3 tests),
  productive ADV redup (2 tests), plus FU evaluator property
  tests (Phase 6.B), atomic-unify property tests (Phase 6.A),
  and graph-constraint matcher unit tests (Phase 6.C).

### Performance impact

- Phase 6.A atomic-unify: no measurable regression on the
  green path (rollback only fires on failure).
- Phase 6.B FU evaluator: no measurable regression — FU
  evaluation is bounded by f-graph size (≤ hundreds of nodes
  for canonical Tagalog sentences), not grammar size.
- Phase 6.C strict matcher: ~50% test-fast wall-time
  speedup. The strict matcher prunes spurious binary fanout
  at predict time that the old non-conflict matcher passed
  through to late-fail at the constraining-equation pass.

### Closing carry-forward to Phase 7+

Phase 7 is **not yet planned**. The Phase 7+ unifier
extensions listed above are awaiting either corpus pressure
(cross-clausal sarili / non-XCOMP-controlled COMP traversal)
or a clear architectural motivation (Kleene-on-alternation
construction). The codebase is feature-complete for the
canonical Tagalog construction inventory as covered by S&O
1972, R&B 1986, R&G 1981, and Kroeger 1993.

## Phase 7a.A Commit 1: §18.1.1 #11 NP-internal ``mga`` plural — design

First sub-PR of Phase 7a (corpus-deferred §18.1.1 closures
per ``.claude/plans/tgllfg-phase-7a.md``). Closes
§18.1.1 item 11 — plural marking of regular nouns via the
``mga`` particle. The deferral was promoted from informal
stress-test gap to formal §18.1.1 by Phase 6.H closing
notes; Phase 7a.A closes it via a three-daughter case-
parallel extension of the existing simple-NP rules.

### 1. Lexical baseline

The ``mga`` particle is already lex'd at
``data/tgl/particles.yaml:1114-1116`` with
``PLURAL_MARKER: true``. The entry pre-dates Phase 7a; it
was added by Phase 5f Commit 14 to gate the time-
approximator rule (``N → PART[mga] N[SEM_CLASS=TIME]``).
No lex changes for Phase 7a.A.

### 2. Rule shape

Three case-parallel rules in ``cfg/nominal.py`` extend the
existing simple-NP shells (lines 101-130) with a PART
daughter between the case-marker and head N:

```text
NP[CASE=X] → CASE-MARKER[CASE=X] PART N
   (↑) = ↓1                      share f-struct with case-marker
   (↑) = ↓3                      share f-struct with head N
   (↑ NUM) = 'PL'                set plural number on matrix NP
   (↓2 PLURAL_MARKER) =c true    gate the PART daughter to ``mga``
   ¬ (↓3 N_RC)                   mirror simple-NP exclusion
   ¬ (↓3 CARDINAL_VALUE)         mirror simple-NP exclusion
```

For X ∈ {NOM, GEN, DAT} with CASE-MARKER ∈ {DET, ADP, ADP}
respectively (the same case-marker lex types the simple-NP
rules use).

### 3. Composition with Phase 6.H floated-Q

The new rule's ``(↑ NUM) = 'PL'`` defining equation feeds
the Phase 6.H DUAL-Q variant's ``(↑ SUBJ NUM) =c 'PL'``
constraining equation (``cfg/clitic.py``). This closes the
canonical ``Kumain ang mga bata pareho.`` "The children ate
together" case probed but not closed during Phase 6.H —
the floated-Q rule was correct, but no rule produced a
NUM=PL feat on the matrix subject NP for ``ang mga bata``.

### 4. Negative-existential rationale

The ``¬ (↓3 N_RC)`` and ``¬ (↓3 CARDINAL_VALUE)`` guards
mirror the simple-NP rules' exclusions:

- **N_RC** blocks this rule from consuming an N-level RC's
  output (which would duplicate the canonical NP-level RC
  path; Phase 5n.A C8 / Phase 6.G C1).
- **CARDINAL_VALUE** blocks consuming a cardinal-modified
  N (which would duplicate the dedicated NP-level cardinal-
  modifier rule; Phase 5f Commit 1).

No new binary feats are introduced. Both feats are already
in the binary-feats inventory: ``N_RC`` per Phase 6.G C3
(``core/feats.py BINARY_FEATS``); ``CARDINAL_VALUE`` is a
value-feat used existentially throughout the cardinal-NP
rules.

### 5. Intentional ambiguity with Phase 5f approximator rules

The Phase 5f Commit 14 time-approximator
(``N → PART N[SEM_CLASS=TIME]``) and Phase 5f Commit 16
cardinal-approximator (``NUM[CARDINAL] → PART
NUM[CARDINAL]``) also consume ``mga`` but produce different
outputs (``N`` and ``NUM`` respectively) with ``APPROX=true``
rather than ``NUM=PL``.

- **Non-time, non-cardinal Ns** (``aklat``, ``bata``,
  ``aso``): only the new Phase 7a.A rule fires.
- **Time-class Ns** (clock-times like ``alasotso``): both
  paths fire and produce distinct f-structures (NUM=PL via
  the new rule vs APPROX=true via the time-approximator).
  Both readings are linguistically valid. The coexistence
  is exercised by
  ``test_phase7a_a_mga_plural.py::TestMgaApproximatorCoexistence``.
- **Cardinal NUMs** (``sampu``, ``tatlo``): only the
  cardinal-approximator path fires; the new rule's ↓3
  expects N (not NUM).

The ambiguity for time Ns is accepted — the readings are
genuinely distinct in spoken Tagalog. No disambiguation
policy is added.

### 6. Tests

``tests/tgllfg/test_phase7a_a_mga_plural.py`` covers 11
fixtures across five classes:

- ``TestMgaNPBasicCases`` (5 tests): NOM SUBJ (``Kumain ang
  mga bata.``, ``Tumakbo ang mga aso.``); GEN OBJ (``Bumili
  ako ng mga aklat.``, ``Kumain ang aso ng mga isda.``);
  DAT ADJUNCT (``Pumunta ako sa mga bahay.``).
- ``TestMgaFloatedQ`` (2 tests): ``Kumain ang mga bata
  pareho/kapwa.`` — the Phase 6.H canonical case now closes.
- ``TestMgaApproximatorCoexistence`` (1 test): ``Pumunta
  ako sa mga alasotso.`` — both NUM=PL and APPROX=true
  readings appear.
- ``TestMgaCardinalApproximatorPath`` (1 test): ``Bumili
  ako ng mga sampung aklat.`` — cardinal-approximator path
  unchanged.
- ``TestSimpleNPUnchanged`` (2 tests): ``Kumain ang bata.``
  and ``Bumili ako ng isang aklat.`` regression on simple-NP
  and cardinal-NP paths.

Regression: 7200 → 7211 fast tests; ``hatch run check``
clean; existing ``test_mga_approximation.py`` Phase 5f
tests unaffected (the helper iterates parses and returns
the first ADJUNCT match by lemma, so adding a second
parse doesn't break it).

## Phase 7a.B Commit 1: §18.1.1 item 2 magsi + magpa-an distributive AV — design

Second sub-PR of Phase 7a (corpus-deferred §18.1.1 closures
per ``.claude/plans/tgllfg-phase-7a.md``). Closes §18.1.1
item 2 — two distributive AV affix classes:

1. **``magsi-``** plural-actor AV prefix (`magsikanta` "sing
   (pl.)") — canonically S&O 1972 §5.15.
2. **``magpa-…-an``** causative-reciprocal-distributive
   circumfix (`nagpatawagan` "called one another") —
   reciprocal-distributive subtype only; locative-
   distributive subtype empirically negative (deferred).

### 1. ``magsi-`` plural-actor AV (S&O §5.15)

S&O 1972 §5.15 documents ``magsi-`` as the optional
PLURALIZED AV formation that occurs only with a plural topic.
Canonical examples (S&O Chart 18):

```text
-um- base    →   magsi-       (kumanta → magsikanta)
mag-(+X) base →  magsipag-(+X) (mag-aral → magsipag-aral)
mang- base   →   magsipang-   (mangisda → magsipangisda)
```

Standard 3-aspect AV paradigm:

| Aspect | Form | Surface (`kanta` base) |
| --- | --- | --- |
| PFV | nagsi-V | `nagsikanta` |
| IPFV | nagsisi-V | `nagsisikanta` |
| CTPL | magsisi-V | `magsisikanta` |
| basic | magsi-V | `magsikanta` |

**Phase 7a.B scope:** implements only the ``magsi-``
paradigm (for ``-um-`` verbs). The ``magsipag-`` and
``magsipang-`` variants for ``mag-`` and ``mang-`` verbs
are morphologically distinct paradigm cells; deferred as
follow-on work. The ``-nga-`` infix variant (e.g.,
``mangagsikanta``) is also out of scope — S&O notes it does
not change meaning.

Cells emit ``{DISTRIB: true}``. No CAUS/RECP/MOOD feats
(the construction is pure pluralization, not reciprocal or
causative).

### 2. ``magpa-…-an`` causative-distributive circumfix

The user-source consultation (2026-05-13) claimed two
productive subtypes:

1. **Reciprocal-distributive** (`magpakainan` "feed one
   another"; `nagpatawagan` "called one another";
   `magpahiraman` "lend one another")
2. **Locative-distributive** (`magpinturahan` "paint all
   over"; `magpatakan` "drop onto"; `magpaupuan` "seat
   distributively across loci")

**Empirical verification (2026-05-14, via GT):**

<!-- markdownlint-disable MD013 -->

| Test clause | GT output | Verdict |
| --- | --- | --- |
| `Nagpatawagan sila kahapon.` | "They called each other yesterday." | reciprocal-distributive PRODUCTIVE |
| `Nagpinturahan namin ang bahay.` | "We painted the house." | no locative-distributive sense |
| `Magpatakan natin ng tubig ang mga halaman.` | "Let's water the plants." | no distribution sense |
| `Magpaupuan natin ang mga bisita.` | "Let's seat the guests." | no distribution sense |
| `Nagpalagayan kami ng bulaklak sa mesa.` | "We placed flowers on the table." | no distribution sense |

<!-- markdownlint-enable MD013 -->

**Conclusion:** the reciprocal-distributive reading is
robustly productive (1 / 1 positive); the locative-
distributive reading is empirically NOT distinct from
plain locative-focus / `-an` LV in modern Tagalog
(0 / 3 positive). Phase 7a.B implements only the
reciprocal-distributive reading; the locative-distributive
subtype is dropped from the v1 scope per this evidence.

### 3. ``magpa-…-an`` cell shape

Three aspect cells (PFV/IPFV/CTPL) emit
``{DISTRIB: true, RECP: true, CAUS: INDIRECT, MOOD: SOC}``
— parallel to the existing ``mag_an`` reciprocal-AV cells
(Phase 5e Commit 12; MOOD=SOC + RECP=true) with the
causative ``pa-`` layer added.

| Aspect | Operations | Surface (`tawag` base) |
| --- | --- | --- |
| PFV | suffix `an` + prefix `pa` + prefix `nag` | `nagpatawagan` |
| IPFV | suffix `an` + prefix `pa` + cv_redup + prefix `nag` | `nagpapatawagan` |
| CTPL | suffix `an` + prefix `pa` + cv_redup + prefix `mag` | `magpapatawagan` |

The cv_redup duplicates the ``pa`` outer-prefix (same
pattern as the existing ``magpa`` IPFV/CTPL cells produce
``nagpapakain`` / ``magpapakain``).

### 4. Reference-grammar attestation note

R&B 1986 and S&O 1972 do not explicitly document the
``magpa-…-an`` circumfix as a productive AV paradigm.
S&O's nearest forms (`magpagandahan`, `magpatayan`,
`magpari-parian` on p. 357) are analyzed as ``mag-`` +
derived-nominal-in-``-an``, not as ``magpa-…-an``
circumfix. The Phase 7a.A reciprocal-distributive
implementation is grounded in the user-source consultation
plus the GT-confirmed productivity of ``nagpatawagan``,
not in direct reference-grammar attestation. **Risk
acknowledged**: if a future reference-grammar scan shows
``magpa-…-an`` is genuinely analyzed as ``mag-`` +
derived-nominal, the implementation should be revisited.

### 5. Starter verb sets

**``magsi``** (`-um-` verbs only; per S&O §5.15):

- `kanta` (sing) — S&O canonical example
- `kain` (eat)
- `basa` (read)
- `inom` (drink)
- `sulat` (write)

**``magpa_an``** (verbs licensing causative-reciprocal
reading):

- `kain` (eat) — GT example: `magpakainan` "feed one another"
- `tawag` (call) — GT-confirmed: `nagpatawagan`
- `hiram` (borrow / lend) — `magpahiraman` "lend one another"
- `upo` (sit) — `magpaupuan` "seat one another / share seating"

All four roots are already in ``data/tgl/verbs.yaml``.
The starter set adds the new ``magsi`` / ``magpa_an``
strings to their ``affix_class`` lists; no new lex entries.

### 6. Tests

``tests/tgllfg/test_phase7a_b_distrib_av.py`` covers:

- ``TestMagsiMorphology`` (parametrized over 5 verb bases ×
  3 aspects, 15 tests): verifies the analyzer generates
  ``nagsi-V`` / ``nagsisi-V`` / ``magsisi-V`` surfaces with
  ``DISTRIB=true``.
- ``TestMagpaAnMorphology`` (parametrized over 4 verb bases
  × 3 aspects, 12 tests): verifies the analyzer generates
  ``nagpa-V-an`` / ``nagpapa-V-an`` / ``magpapa-V-an``
  surfaces with ``DISTRIB=true, RECP=true, CAUS=INDIRECT``.
- ``TestMagpaAnReciprocalClause`` (3 tests): parses
  ``Nagpatawagan sila.``, ``Nagpakainan ang mga bata.``,
  ``Magpahiraman tayo ng aklat.``; verifies SUBJ + the
  reciprocal-distributive feats on the verb.
- ``TestExistingParadigmsUnchanged`` (regression, 4 tests):
  ``magpakain``, ``nagkainan``, ``kumain``, ``magkakainan``
  still parse with their pre-Phase-7a.B feats.

## Phase 7a.C Commit 1: §18.1.1 item 3 katatapos raising + Non-AV RECPFV reclassification — design

Third sub-PR of Phase 7a. Two coordinated sub-closures landed
in one sub-PR per the plan-of-record §3.3:

1. **Non-AV RECPFV deferral — reclassify from §18.1.1 to
   §18.1.3** with the strengthened structural rationale
   (extends Phase 5e Commit 23 closure).
2. **`katatapos + V` raising wiring** — the analytic
   alternative for non-AV "just-finished" readings,
   delivering the construction Phase 5e Commit 23 sketched
   but didn't implement.

### 1. Non-AV RECPFV — structural diagnostic (extends Phase 5e Commit 23)

Phase 5e Commit 23 (``analysis-choices.md`` lines 5430-5530)
already documented the paradigm evidence: R&B 1986 (Handbook
of Tagalog Verbs) lists Recent Perfective only under AF /
A2F (both AV-shaped) for every entry; never under OF / DF /
IF / BF / LF / RF. Phase 7a.C adds the **structural
diagnostic** for the gap: recent-perfective forms
independently lack the ``ang``-marked direct pivot that
defines non-AV voices structurally — non-AV columns are
structurally unavailable, not just descriptively absent.

This moves the item from "corpus-deferred (§18.1.1)" to
"permanently out-of-scope (§18.1.3)" in
``.claude/plans/tgllfg-out-of-scope.md``. Forms like
``*kakakainin`` / ``*kakabinasá`` are noncanonical /
do-not-generate; absence of paradigm rules is sufficient.
Revisit only on a primary-source counterexample.

### 2. `katatapos + V` analytic alternative — implementation

For non-AV "just-finished" readings (e.g., "the fish had
just been eaten" with OV pivot), the canonical Tagalog
analytic alternative is ``katatapos + V[non-AV]`` with
matrix raising from the embedded V's SUBJ. Plan-of-record
§3.3 sketches:

```text
S → V[lemma=tapos, ASPECT=RECPFV] V[non-finite]
   (↑ XCOMP) = ↓2
   (↑ SUBJ) = (↑ XCOMP SUBJ)
   (↑ PRED) = 'JUST-FINISHED <XCOMP> SUBJ'
```

**Implementation:** the existing Phase 5d Commit 1 bare-
raising rule (``cfg/control.py:868-875``) is structurally
``S → V[CTRL_CLASS=RAISING_BARE] S``, which is exactly the
shape needed — no new grammar rule required. We wire
``katatapos`` into the raising machinery via two static lex
additions:

- **``data/tgl/particles.yaml``**: new particle entry for
  surface ``katatapos`` with feats ``{CTRL_CLASS:
  RAISING_BARE, LEMMA: tapos, ASPECT: RECPFV}``. Co-exists
  with the morphologically-generated AV-RECPFV analysis
  (``CTRL_CLASS=NONE``) from the existing paradigm cell;
  the parser selects between them by rule fit.
- **``data/tgl/lexicon/control.yaml``**: new lex entry
  ``lemma: tapos`` with ``pred: "JUST-FINISHED <XCOMP>
  SUBJ"``, ``intrinsic: RAISING``, and morph_constraints
  matching the particle entry (CTRL_CLASS / LEMMA /
  ASPECT). Parallel to the existing ``tila``, ``parang``,
  ``mukha``, ``baka`` raising entries.

The PRED template ``JUST-FINISHED <XCOMP> SUBJ`` follows
the existing raising-verb convention (``APPARENTLY <XCOMP>
SUBJ`` for tila, ``SEEMS-LIKE <XCOMP> SUBJ`` for parang) —
thematic args in angle brackets, non-thematic SUBJ outside.

### 3. Verified coverage

The wiring delivers the construction's value:

| Sentence | Inner voice | SUBJ raised from | Parses |
| --- | --- | --- | --- |
| `Katatapos kumain ang aso.` | AV-PFV | `ang aso` | yes |
| `Katatapos kumain ako.` | AV-PFV (PRON) | `ako` | yes |
| `Katatapos kumakain ang bata.` | AV-IPFV | `ang bata` | yes |
| **`Katatapos kainin ko ang isda.`** | **OV-CTPL** | **`ang isda` (OV pivot)** | yes |
| **`Katatapos kinain ng aso ang isda.`** | **OV-PFV** | **`ang isda` (OV pivot)** | yes |
| `Katatapos kumain ang mga bata.` | AV-PFV + Phase 7a.A mga-NP | `ang mga bata` (NUM=PL) | yes |

The OV cases demonstrate the construction's value: the
non-AV pivot (`ang isda`) raises to matrix SUBJ via the
existing structure-sharing equation, delivering the
"non-AV just-finished" reading that the morphological
non-AV RECPFV paradigm doesn't provide (and per §1 above
can't provide structurally).

### 4. Scope limitations

Two surfaces explicitly out of v1 scope (not bugs, just
pre-existing grammar limits):

- **Bare OV embedded without overt GEN actor**
  (``Katatapos kainin ang isda.``): the inner ``kainin
  ang isda`` doesn't parse standalone (Phase 4 §7 OV
  grammar limit — OV CTPL/imperative without GEN actor
  has no clause frame). Future-tense imperative OV needs
  an actor.
- **Linker form** (``Katatapos kong kumain.`` "I had just
  finished eating"): the ``kong`` linker form is a 2nd-
  position GEN clitic between matrix and embedded V — a
  different syntactic shape than ``S → V[RAISING_BARE]
  S``. The linker raising rule (``V[RAISING] + LINK + S``)
  is for ``mukha`` / ``baka`` with ``na`` / ``-ng``
  between matrix V and embedded clause, not between
  matrix V and a clitic.

Both limitations are documented in the test file's scope-
limits class.

### 5. Tests

``tests/tgllfg/test_phase7a_c_recpfv_katatapos.py`` covers
12 fixtures:

- ``TestKatatapasMorphology`` (2 tests): the new RAISING_BARE
  analysis appears in ``analyze_tokens``; the existing AV-
  RECPFV CTRL_CLASS=NONE analysis is preserved.
- ``TestKatatapasRaisingClause`` (6 tests, partly
  parametrized): AV intransitive, AV with NOM pronoun,
  AV-IPFV embedded, two OV cases (parametrized) verifying
  the pivot-raised SUBJ, and the mga-NP interaction
  (Phase 7a.A composition).
- ``TestExistingRaisingUnaffected`` (2 tests): tila /
  parang still produce APPARENTLY / SEEMS-LIKE PRED
  templates.
- ``TestScopeLimits`` (2 tests): explicit pin of the two
  documented scope limitations (OV-no-actor + linker-kong).

Regression: 7242 → 7255 fast pass (+12 new + 1 incidental
from a parametric expansion picking up the new entry); 19
slow pass + 1 xfail unchanged. ``hatch run check`` clean.

### 6. Reference-grammar grounding

Both sub-closures cite established reference-grammar
evidence:

- **Non-AV RECPFV reclassification:** R&B 1986 Handbook
  paradigm evidence (Phase 5e Commit 23); S&O 1972 §5.31
  (recent-perfective formation primarily AV).
- **`katatapos + V` analytic construction:** S&O 1972 §5.13
  documents ``tapos`` recent-perfective forms; the
  raising-bare matrix is parallel to `tila` (S&O §5.18
  sentence-adverb analysis) — same syntactic shape, same
  Phase 5d machinery.

## Phase 7a.D Commit 1: §18.1.1 item 5 wh-ADV linker fronting — design

Fourth sub-PR of Phase 7a (per plan-of-record §3.4). Closes
§18.1.1 item 5 — `paano` linker fronting (`Paanong kumain
ang aso?` "How would the dog eat?"). The plan called out
`paano` specifically, but the new rule is generic over
``ADV[WH]`` and incidentally covers the parallel
``saang`` / ``kailang`` / etc. forms at no additional cost.

### 1. Lexical baseline

`paano` and `papaano` are already lex'd in
``data/tgl/particles.yaml`` with
``{WH: true, ADV_TYPE: MANNER}``. Other wh-ADVs follow the
same shape: ``saan`` (LOCATION), ``kailan`` (TIME), ``bakit``
(REASON). No lex changes for Phase 7a.D.

### 2. Pre-Phase-7a.D state

The Phase 5i Commit 4 adverbial wh rule
(``cfg/clause.py:1549-1559``) handles the **bare** wh-ADV
form:

```text
S[Q_TYPE=WH] → ADV[WH] S
   (↑) = ↓2
   (↑ Q_TYPE) = 'WH'
   (↑ WH_LEMMA) = ↓1 LEMMA
   ↓1 ∈ (↑ ADJUNCT)
   (↓1 WH) =c true
```

Verified: ``Paano kumain ang aso?`` parses today (1 parse)
via this rule. The gap is the **linker-bound** form:
``Paanong kumain ang aso?`` zero-parses today.

### 3. Rule shape (new)

Two parallel variants (one per linker atom):

```text
S[Q_TYPE=WH] → ADV[WH] PART[LINK=NA] S
S[Q_TYPE=WH] → ADV[WH] PART[LINK=NG] S
   (↑) = ↓3
   (↑ Q_TYPE) = 'WH'
   (↑ WH_LEMMA) = ↓1 LEMMA
   ↓1 ∈ (↑ ADJUNCT)
   (↓1 WH) =c true
```

Equations mirror the bare variant exactly except daughter
indices shift by one (S=↓3 vs ↓2). Generic over ``ADV[WH]``
— the new rule covers paano, papaano, saan, kailan, bakit
when followed by NA or NG linker.

### 4. Deviations from plan-of-record §3.4

The plan sketched (proposed but revised in implementation):

```text
S[Q_TYPE=WH] → PART[wh-MANNER, LEMMA=paano] PART[LINK] S
   (↑ ASK_MANNER) = true
   (↓1 ADV_TYPE) =c 'WH-MANNER'
```

Three changes from the plan:

1. **Generic `ADV[WH]` instead of `PART[LEMMA=paano]`.** The
   existing Phase 5i bare-wh rule is already generic; the
   linker variant mirrors it. The new rule incidentally
   covers ``saang`` / ``kailang`` / etc., which were a
   parallel gap not separately tracked in §18.1.1.
2. **`(↓1 WH) =c true` instead of `(↓1 ADV_TYPE) =c
   'WH-MANNER'`.** The existing convention uses bare
   `ADV_TYPE` atoms (`MANNER`, `LOCATION`, etc.); the plan's
   `WH-MANNER` compound atom would break the established
   pattern. The bare-wh rule uses `(↓1 WH) =c true` and the
   linker variant does the same.
3. **`(↑ ASK_MANNER) = true` dropped.** No parallel
   `ASK_*` feats exist for the other wh-types
   (`ASK_LOCATION` for saan, `ASK_TIME` for kailan, etc.);
   adding one paano-specific atom would be inconsistent.
   Downstream consumers dispatch on `WH_LEMMA` when they
   need to distinguish question types — same convention as
   Phase 5i.

### 5. Verified coverage

| Sentence | wh-ADV | Linker | Parses |
| --- | --- | --- | --- |
| `Paano kumain ang aso?` | paano | — (bare) | yes (Phase 5i) |
| `Paanong kumain ang aso?` | paano | -ng (NG) | yes (new) |
| `Paano na kumain ang aso?` | paano | na (NA) | yes (new + Phase 5i mixed parses) |
| `Saang kumain ang aso?` | saan | -ng | yes (new, incidental) |
| `Kailang kumain ang aso?` | kailan | -ng | yes (new, incidental) |

### 6. Tests

``tests/tgllfg/test_phase7a_d_wh_linker_fronting.py`` covers
15 fixtures:

- ``TestNGLinkerWhAdvFronting`` (10 tests, partly
  parametrized): -ng linker variant for paano (3 sentences)
  / saan / kailan. Verifies Q_TYPE=WH, WH_LEMMA, ADJUNCT
  membership, ADV_TYPE=MANNER propagation on paano, and
  inner-S verbal PRED percolation.
- ``TestNALinkerWhAdvFronting`` (2 tests, parametrized):
  na linker variant for paano / saan. Pins at-least-one
  wh-Q reading (na is also an enclitic, so multiple
  parses are admissible).
- ``TestBareWhAdvUnaffected`` (3 tests, parametrized): the
  Phase 5i bare wh-ADV rule still produces wh-Q parses
  for paano, saan, bakit.

Regression: 7255 → 7270 fast pass (+15 new). No baseline
regressions. ``hatch run check`` clean.

## Phase 7a.E Commit 1: §18.1.1 items 6 + 7 modal-rule variants — design

Fifth sub-PR of Phase 7a (per plan-of-record §3.5 + §3.6).
Closes §18.1.1 items 6 + 7 — two coordinated modal-construction
extensions of the Phase 5j Commit 7 modal-control rule.

### 1. Pre-Phase-7a.E modal-control state

Phase 5j Commit 7 (``cfg/control.py:488-524``) added the canonical
modal-control rule for `dapat` / `puwede` / `maaari` / `kailangan`
with two case variants (NOM-actor, GEN-experiencer) × two linker
variants (NA, NG):

```text
S → V[CTRL_CLASS=MODAL] NP[CASE={NOM|GEN}] PART[LINK={NA|NG}] S_XCOMP
   (↑ SUBJ) = ↓2
   (↑ XCOMP) = ↓4
   (↑ SUBJ) = (↑ XCOMP REL-PRO)
```

This works for clitic-NP SUBJ (``Dapat akong kumain.`` "I should
eat"). The matrix NP slot is between modal and linker; clitic
placement absorbs the GEN clitic + linker as `kong` etc.

Phase 5j Commit 7 also deliberately left ``Hindi ka dapat
kumain.`` (no-linker) at 0 parses to avoid the silent-drop
ambiguity. The test
``test_phase5j_modal_lex.py::TestNoLinkerModalIsZeroParses``
pinned this 0-parse behavior with an explicit instruction
"verify the matrix-PRED shape and update this test" if the
no-linker variant gets added.

### 2. §3.5 — Full-NP SUBJ inside embedded clause

**Surface:** ``Dapat na kumain si Maria.`` "Maria should eat."

The canonical Tagalog word order for full-NP SUBJ is
verb-initial inside the embedded clause: `modal | linker |
[V + NP]`. The Phase 5j rule's matrix NP slot (between modal
and linker) requires the marked / rare order
``Dapat si Maria na kumain.``; for the canonical order, no rule
existed.

**New rules** (two variants, NA / NG linker):

```text
S → V[CTRL_CLASS=MODAL] PART[LINK={NA|NG}] S
   (↑ XCOMP) = ↓3
   (↑ SUBJ) = (↑ XCOMP SUBJ)
   (↓1 CTRL_CLASS) =c 'MODAL'
   (↓1 MODAL) =c true
```

Structure-share `(↑ SUBJ) = (↑ XCOMP SUBJ)` unifies the matrix
SUBJ slot with the embedded clause's SUBJ. The matrix's lex
PRED (``DAPAT <SUBJ, XCOMP>``) keeps SUBJ thematic — same
control semantics as Phase 5j, just with a different surface
distribution of the SUBJ NP.

### 3. §3.6 — No-linker colloquial

**Surface:** ``Hindi ka dapat kumain.`` (clitic-NP); ``Dapat
kumain si Maria.`` (full-NP).

Colloquial Tagalog drops the linker between modal and embedded
V. Pre-Phase-7a.E this surface zero-parsed (Phase 5j Commit 7's
deliberate gap). Phase 7a.E §3.6 admits the surface with
explicit ``REGISTER='COLLOQUIAL'`` tagging on the matrix —
downstream consumers can filter colloquial parses, addressing
Phase 5j Commit 7's silent-drop ambiguity concern.

**New rules** (two variants — clitic-NP via S_XCOMP, full-NP
via S):

```text
S → V[CTRL_CLASS=MODAL] NP[CASE=NOM] S_XCOMP
   (↑ SUBJ) = ↓2
   (↑ XCOMP) = ↓3
   (↑ SUBJ) = (↑ XCOMP REL-PRO)
   ...
   (↑ REGISTER) = 'COLLOQUIAL'

S → V[CTRL_CLASS=MODAL] S
   (↑ XCOMP) = ↓2
   (↑ SUBJ) = (↑ XCOMP SUBJ)
   ...
   (↑ REGISTER) = 'COLLOQUIAL'
```

The clitic-NP variant mirrors the Phase 5j rule minus the
linker daughter; the full-NP variant mirrors the §3.5 rule
minus the linker. Both tag the matrix with
``REGISTER='COLLOQUIAL'``.

### 4. Phase 5j Commit 7 test update

The deliberately-pinned 0-parse test in
``test_phase5j_modal_lex.py::TestNoLinkerModalIsZeroParses`` is
updated to ``TestNoLinkerModalIsColloquialParses`` per the
test's own embedded instructions ("If you're seeing parses
here, the modal control wrap may have been extended to a
no-linker variant — verify the matrix-PRED shape and update
this test."). The new assertion verifies the matrix carries
``REGISTER='COLLOQUIAL'``, satisfying Phase 5j Commit 7's
silent-drop-avoidance constraint by making the colloquial
status explicit.

### 5. Verified coverage

| Sentence | Variant | Parses |
| --- | --- | --- |
| `Dapat akong kumain.` | Phase 5j clitic-NP + linker (regression) | yes |
| `Dapat na kumain si Maria.` | §3.5 full-NP + NA linker | yes |
| `Pwedeng kumain si Maria.` | §3.5 full-NP + NG linker | yes |
| `Maaaring kumain si Maria.` | §3.5 full-NP + NG linker | yes |
| `Hindi ka dapat kumain.` | §3.6 clitic-NP no-linker | yes (REGISTER=COLLOQUIAL) |
| `Dapat kumain si Maria.` | §3.6 full-NP no-linker | yes (REGISTER=COLLOQUIAL) |
| `Hindi dapat kumain si Maria.` | §3.6 full-NP no-linker + negation | yes (REGISTER=COLLOQUIAL) |
| `Hindi ka dapat na kumain.` | Phase 5j clitic-NP + linker (regression) | yes (formal) |

### 6. Tests

``tests/tgllfg/test_phase7a_e_modal_variants.py`` covers 10
fixtures across 3 classes:

- ``TestFullNPModalLinker`` (4 tests, parametrized):
  parses `Dapat na kumain si Maria.`, `Pwedeng kumain si
  Maria.`, `Maaaring kumain si Maria.`, `Dapat na kumain
  ang bata.` (mix of personal-name and full-NP SUBJ).
  Verifies modal PRED + correct SUBJ binding.
- ``TestNoLinkerColloquialModal`` (3 tests): three no-linker
  surfaces (`Hindi ka dapat kumain.`, `Dapat kumain si
  Maria.`, `Hindi dapat kumain si Maria.`). Each verifies at
  least one parse with REGISTER=COLLOQUIAL.
- ``TestPhase5jModalRegression`` (3 tests, parametrized):
  Phase 5j canonical clitic + linker forms still parse,
  with at least one non-COLLOQUIAL (formal) reading.

Plus the updated
``test_phase5j_modal_lex.py::TestNoLinkerModalIsColloquialParses``
test (1 fixture, was 0-parses).

Regression: 7270 → 7280 fast pass (+10 new fixtures in 7a.E
test file; the Phase 5j test update is in place not added).
``hatch run check`` clean.

## Phase 7a.F Commit 1: §18.1.1 item 8 kahit-X no-`ay` colloquial — design

Sixth sub-PR of Phase 7a (per plan-of-record §3.7). Closes
§18.1.1 item 8 — pre-V kahit-X SUBJ in non-``ay`` form
(``Kahit sino kumain.`` "Anyone could eat"). Phase 5n.B
Commit 20 closed the canonical ``ay``-fronted form; this
variant drops the ``ay`` for the colloquial register.

### 1. Pre-Phase-7a.F state

Phase 4 §7.4 has the ay-fronted rule
(``cfg/extraction.py:764-773``):

```text
S → NP[CASE=NOM] PART[LINK=AY] S_GAP
   (↑) = ↓3
   (↑ TOPIC) = ↓1
   (↓3 REL-PRO) = ↓1
   (↓3 REL-PRO) =c (↓3 SUBJ)
```

Phase 5n.B Commit 20 was a TESTS-ONLY commit that pinned
kahit-X compatibility with this rule (``Kahit sino ay
kumain.`` parses 1× via the generic ay-rule; the kahit-X
PRON carries ``INDEF=YES`` from the Phase 5m C8 IndefPRON
rule). The no-ay form (``Kahit sino kumain.``) zero-parsed
and was pinned by three deferred-test classes across the
codebase:

- ``test_phase5n_b_kahit_subj_ay.py::TestNonAyFormDeferred``
- ``test_phase5m_indefinite_kahit.py::TestKahitFrontedSubjectDeferred``
- ``test_phase5n_b_bare_indirect_q.py::TestKahitXExcluded``

### 2. New rule

```text
S → NP[CASE=NOM] S_GAP
   (↑) = ↓2
   (↑ TOPIC) = ↓1
   (↓2 REL-PRO) = ↓1
   (↓2 REL-PRO) =c (↓2 SUBJ)
   (↓1 INDEF) =c 'YES'
   (↑ REGISTER) = 'COLLOQUIAL'
```

Mirrors the Phase 4 §7.4 ay-fronted rule above exactly except:

- **Drops the ``PART[LINK=AY]`` daughter** — daughter
  indices shift by one (S_GAP is ↓2 instead of ↓3).
- **Gates the NP daughter to ``INDEF=YES``** — preventing
  overgeneration on bare-NP pre-V SUBJ (which colloquial
  Tagalog disallows; only indefinite-NP fronting is
  admissible without ``ay``).
- **Adds ``(↑ REGISTER) = 'COLLOQUIAL'``** — downstream
  consumers can filter colloquial parses.

``INDEF=YES`` is the feat the Phase 5m Commit 8 IndefPRON
rule (``PRON → PART PRON`` with ``(↓1 LEMMA) =c 'kahit'``)
sets on kahit-X compositions. Any future indefinite
construction that compositionally sets ``INDEF=YES`` will
also license this colloquial fronting.

### 3. Test updates across three files

Three pre-Phase-7a.F deferred-test classes had to be
rewritten to reflect the closure:

- ``test_phase5n_b_kahit_subj_ay.py``:
  ``TestNonAyFormDeferred`` →
  ``TestNonAyFormParsesColloquial`` — asserts parse +
  ``REGISTER='COLLOQUIAL'``.
- ``test_phase5m_indefinite_kahit.py``:
  ``TestKahitFrontedSubjectDeferred`` →
  ``TestKahitFrontedSubjectColloquial`` — same.
- ``test_phase5n_b_bare_indirect_q.py``:
  ``TestKahitXExcluded`` →
  ``TestKahitXExcludedFromBareIndirectQ`` — preserves the
  Phase 5n.B C10 bare-indirect-Q rule's ``¬ (↓1 INDEF)``
  exclusion (kahit-X still doesn't trigger that rule's
  wh-Q reading); asserts the surviving parse comes from
  the Phase 7a.F rule (TOPIC binding) not the bare-indirect-Q
  rule (which would have no TOPIC).

### 4. Verified coverage

| Sentence | Variant | REGISTER |
| --- | --- | --- |
| `Kahit sino ay kumain.` | Phase 5n.B C20 ay-fronted | formal |
| `Kahit sino kumain.` | §7a.F no-ay | COLLOQUIAL |
| `Kahit ano kumain.` | §7a.F no-ay | COLLOQUIAL |
| `Kahit alin kumain.` | §7a.F no-ay | COLLOQUIAL |
| `Kahit sino kumakain.` | §7a.F no-ay + AV-IPFV | COLLOQUIAL |
| `Kahit sino bumili ng aklat.` | §7a.F no-ay + AV-trans | COLLOQUIAL |
| `Kumain kahit sino.` | Phase 5m C8 post-V SUBJ | n/a (formal) |

### 5. Tests

``tests/tgllfg/test_phase7a_f_kahit_no_ay.py`` covers 15
fixtures across 4 classes:

- ``TestKahitNoAyColloquial`` (10 tests, parametrized): five
  no-ay surfaces (sino / ano / alin × AV intransitive +
  AV-IPFV + AV-transitive). Each verifies REGISTER=
  COLLOQUIAL and TOPIC.LEMMA bound to the kahit-X PRON,
  with INDEF=YES propagation.
- ``TestAyFrontedFormUnaffected`` (3 tests, parametrized):
  Phase 5n.B C20 ay-fronted forms still parse without the
  COLLOQUIAL tag (formal).
- ``TestPostVSubjUnaffected`` (1 test): Phase 5m C8 post-V
  SUBJ form (`Kumain kahit sino.`) unchanged.
- ``TestBareNPDoesNotFront`` (1 test): the INDEF=YES gate
  works — bare proper-noun pre-V SUBJ doesn't trigger the
  COLLOQUIAL rule.

Plus 3 in-place test class renames across the three pre-
existing deferred-test files.

Regression: 7280 → 7295 fast pass (+15 new). No baseline
regressions. ``hatch run check`` clean.

## Phase 7a.G Commit 1: §18.1.1 item 10 kahit-X in non-NOM slots — design

Seventh sub-PR of Phase 7a (per plan-of-record §3.8). Closes
§18.1.1 item 10 — kahit-X wh-PRONs in non-NOM argument slots
(GEN-OBJ, DAT-OBL/recipient).

### 1. Pre-Phase-7a.G state

The Phase 6.C C3d case-parameterized IndefPRON rules
(``cfg/nominal.py:1967-1979``) produce ``PRON[INDEF=YES,
CASE=X]`` for X ∈ {NOM, GEN, DAT} but only fire when the
daughter wh-PRON's lex CASE matches the matrix output CASE.
``sino`` / ``ano`` / ``alin`` are lex'd as CASE=NOM only —
so the GEN / DAT C3d variants never fire on them, leaving
``kahit ano`` etc. unable to fill non-NOM slots. The Phase
6.C C3f xfail (``test_kahit_ano_in_obj``) pinned this gap.

### 2. Lex-variant approach attempted and abandoned

Plan §3.8 option (a) — adding GEN / DAT lex variants of
``sino`` / ``ano`` / ``alin`` to ``data/tgl/pronouns.yaml``
— was attempted first. **Result: collision.** The morph
analyzer indexes pronouns by surface key
(``morph/analyzer.py:174``: ``pronouns: dict[str,
MorphAnalysis]``), so multiple entries with the same surface
collide and only one survives. NOM-position regressions
result.

Switched to plan §3.8 option (b): "an any-case wh-indef
projection rule".

### 3. NP-level projection rule

Two new rules in ``cfg/nominal.py``, parallel to the Phase
5i Commit 3 in-situ wh-PRON shell rules (``cfg/nominal.py:
172-193``) but with the ADP daughter replaced by a bare PART
gated to ``kahit``:

```text
NP[CASE=GEN, WH=true] → PART PRON[WH]
NP[CASE=DAT, WH=true] → PART PRON[WH]
   (↑ PRED) = 'WH-PRO'
   (↑ INDEF) = 'YES'
   (↑ WH) = ↓2 WH
   (↑ LEMMA) = ↓2 LEMMA
   (↑ WH_LEMMA) = ↓2 LEMMA
   ↓1 ∈ (↑ ADJUNCT)
   (↓1 LEMMA) =c 'kahit'
   (↓2 WH) =c true
   (↓2 CASE) =c 'NOM'
```

The bare PRON daughter doesn't have a CASE constraint at the
category level; the constraining equation
``(↓2 CASE) =c 'NOM'`` gates to NOM-source wh-PRONs only.
The matrix's CASE is set by the LHS atom (GEN or DAT). The
``(↓2 CASE) =c 'NOM'`` constraint prevents kanino (which is
lex'd CASE=DAT) from triggering this rule — it's already
handled by the existing Phase 6.C C3d DAT-IndefPRON rule.

### 4. Empirical validation (GT 2026-05-14)

The three target surfaces all produce canonical OBJ-reading
GT translations:

| Sentence | GT output | Reading |
| --- | --- | --- |
| `Kumain siya kahit ano.` | "He will eat anything." | kahit ano = anything (OBJ) |
| `Kumain siya kahit sino.` | "He ate anyone." | kahit sino = anyone (OBJ) |
| `Kumain siya kahit alin.` | "He ate whatever." | kahit alin = whatever (OBJ) |

The OBJ reading is canonical in modern Tagalog. Phase 7a.G
delivers this reading.

### 5. Over-generation and filter guidance

The new rule introduces **3 parses** for each `Kumain siya
kahit ano.`-style surface (was 0 pre-Phase-7a.G):

- **Parse [a]: ``PRED='EAT <SUBJ>'`` with ADJUNCT-bound
  kahit-X.** A non-canonical clause-level adjunct reading
  ("he ate, whatever-his-choice"). Activated as a side effect
  of the new NP-projection rule being available.
- **Parse [b]: ``PRED='EAT <SUBJ, OBJ>'`` with
  ``OBJ.INDEF=YES`` and ``OBJ.LEMMA`` set to the wh-PRON
  lemma.** The canonical OBJ reading (matches GT).
- **Parse [c]: ``PRED='EAT <SUBJ>'`` with no overt OBJ or
  ADJUNCT.** A residual / packed-forest artifact; the
  kahit-X surface doesn't connect to any matrix role.
  Investigation deferred; downstream filters trivially
  exclude it.

**Downstream filter (recommended for ranker / classifier /
consumer that wants only the canonical OBJ reading):**

```python
def is_canonical_indef_obj_parse(parses, wh_lemma):
    for parse in parses:
        obj = parse.fs.feats.get("OBJ")
        if (
            isinstance(obj, FStructure)
            and obj.feats.get("INDEF") == "YES"
            and obj.feats.get("LEMMA") == wh_lemma
            and obj.feats.get("WH") is True
        ):
            return parse
    return None
```

Filtering on ``OBJ.INDEF=YES`` and ``OBJ.LEMMA == <wh_lemma>``
and ``OBJ.WH is True`` uniquely picks the canonical reading
across all surfaces tested. The Phase 7a.G test file
``tests/tgllfg/test_phase7a_g_kahit_non_nom.py`` uses this
same discriminator via the ``_obj_indef_parse`` helper.

### 6. Tests

``tests/tgllfg/test_phase7a_g_kahit_non_nom.py`` covers 10
fixtures across 4 classes:

- ``TestKahitXInOBJ`` (5 tests, parametrized): five OBJ-
  position surfaces (ano/sino/alin × kumain / bumili).
  Each verifies the canonical OBJ-INDEF reading exists via
  the ``_obj_indef_parse`` filter helper.
- ``TestKaninoUnchanged`` (1 test): the NOM-source gate
  ``(↓2 CASE) =c 'NOM'`` works — ``kahit kanino`` stays at
  1 parse (the existing Phase 6.C C3d DAT-IndefPRON rule
  handles it; the new rule doesn't double-fire).
- ``TestNOMFormsRegression`` (3 tests, parametrized):
  Phase 5m C8 / Phase 7a.F / Phase 5n.B C20 NOM-position
  kahit-X surfaces unaffected.
- ``TestKahitSaanUnchanged`` (1 test): the IndefADV path
  for `saan` is unaffected (the new rule has PRON[WH]
  daughter; saan is ADV).

Plus an in-place flip of ``test_phase5m_indefinite_kahit.py::
TestKahitAnoAsObject`` from xfail to passing test (the Phase
6.C C3f xfail).

Regression: 7295 → 7306 fast pass (+10 new + 1 xfail
flipped). No baseline regressions. ``hatch run check`` clean.

## Phase 7a.H Commit 1: §18.1.1 item 1 resumptive pronouns — reclassify to §18.1.3

Eighth sub-PR of Phase 7a (combined with 7a.I + 7a.J per
user directive). Closes §18.1.1 item 1 — resumptive pronouns
in relative clauses — by reclassifying to §18.1.3 with
strengthened rationale.

**Pre-Phase-7a.H rationale (Phase 5e Commit 7):**
"Modern Tagalog uses voice alternation (Kroeger 1993 §5)
as the canonical strategy for non-SUBJ relativization;
resumptive pronouns are marginal in written Tagalog and lack
a corpus-attested stable form across S&O 1972, Ramos 1971,
R&B 1986, R&G 1981. Revisit if a resumptive-rich corpus
emerges."

**Phase 7a.H closure (per plan-of-record §3.9):**
strengthened with the **observation that Phase 6.D L47
already implements the canonical voice-alternation strategy
via FU `(↓3 XCOMP* SUBJ) =c <ant>`** — the mainstream LFG
mechanism (functional identification with a gap,
voice-morphology-licensed). The construction's deferral is
**not corpus-deficiency-soluble**: the typological premise
(Tagalog uses resumptive relativization) is factually
incorrect for canonical Tagalog. The canonical mechanism is
already in place. Revisit only on substantial corpus
pressure from non-canonical / colloquial sources.

Move from §18.1.1 (corpus-deferred) to §18.1.3 (other
future work).

Docs-only commit; markdownlint clean.

## Phase 7a.I Commit 2: §18.1.1 item 9 tila modal-particle — reclassify to §18.1.3

Closes §18.1.1 item 9 — modal-particle reading of `tila` —
by reclassifying to §18.1.3.

**Pre-Phase-7a.I rationale (Phase 5m planning sign-off):**
"Recommended NO at Phase 5m planning sign-off (§9.1 Q6);
existing Phase 5d raising-verb analysis covers canonical
use. Revisit only if non-clausal `tila` ellipsis surfaces
in corpus."

**Phase 7a.I closure (per plan-of-record §2.2):** confirms
the reclassification with the S&O 1972-grounded analysis:

> S&O 1972 canonically treats `tila` as an initial sentence
> adverb meaning "it seems," parallel to `baka` "maybe," and
> attests it with a sentential complement/environment (*Tila
> magkakaroon ng parti bukas* "It seems there's going to be
> a party tomorrow"). Kroeger 1993 (accessible dissertation
> text) does not address `tila` directly. No current evidence
> from the core grammars requires a productive non-clausal
> `tila` rule.

**Implementation policy:**

- Current `RAISING_BARE` analysis (`particles.yaml:550-552`;
  Phase 5d Commit 1) **retained as engineering approximation**
  for clausal `tila` strings.
- Do **not** add a second modal-particle adjunct variant in
  v1 — would create parse ambiguity without commensurate
  coverage gain.
- A future cleanup may prefer an `ADJUNCT/MODAL` analysis
  over raising if the grammar is refactored (S&O's category
  label is `ADV`, not `V`); tracked as a Phase 7+
  engineering-decision parking-lot item.
- Standalone `Tila.` / `Tila siya.` / `Tila lang.` treated as
  ellipsis / discourse fragments unless non-colloquial corpus
  or grammar evidence shows them to be productive.

**Structural diagnostic for future revisit:** the question
is not "is the post-`tila` material non-clausal" but "is the
post-`tila` material an independently licensed
clause/predicate." If yes, current coverage suffices. If
`tila` productively combines with DP/particle-only material
without recoverable ellipsis, the modal-particle variant
becomes justified.

Move from §18.1.1 (corpus-deferred) to §18.1.3 (other
future work).

Docs-only commit; markdownlint clean.

## Phase 7a.J Commit 3: §18.1.1 item 4 statistical disambiguation — reclassify to §18.1.3

Closes §18.1.1 item 4 — statistical disambiguation over the
packed forest — by reclassifying to §18.1.3.

**Pre-Phase-7a.J rationale (Phase 4 §7.9):** "Phase 4 §7.9
ships a heuristic ranker; a small neural ranker trained on a
gold corpus would replace it. Blocked on a larger gold corpus
than currently exists; revisit when ~5k+ disambiguated parses
are available."

**Phase 7a.J closure (per plan-of-record §2.1; user directive
2026-05-13):** confirms the reclassification on the grounds
that closure requires **~5k+ gold-disambiguated parses — a
downstream-tooling problem (corpus authoring + ML), not a
Tagalog-grammar problem**. The Phase 4 §7.9 heuristic ranker
covers v1 use cases. The blocking dependency is corpus
authoring at scale, which is independently a §18.1.3 item
(see "Corpus authoring at scale"), not a grammar coverage
gap.

Move from §18.1.1 (corpus-deferred) to §18.1.3 (other
future work).

Docs-only commit; markdownlint clean.

## Phase 7a Cumulative Summary

Phase 7a complete 2026-05-14. **§18.1.1 closes entirely**
— all 11 corpus-deferred items either closed with new
grammar / lex rules or reclassified to §18.1.3 with
strengthened rationale. Phase 7a delivered across 11
sub-PRs (7a.A–7a.K):

### Sub-PR ledger

<!-- markdownlint-disable MD013 -->

| Sub-PR | Closes | Mechanism |
| --- | --- | --- |
| 7a.A | §18.1.1 #11 — `mga` plural marker | 3 case-parallel NP-internal rules; `NUM=PL` on matrix NP |
| 7a.B | §18.1.1 #2 — magsi + magpa-an | 6 paradigm cells; 7 verb-entry affix_class updates |
| 7a.C | §18.1.1 #3 — non-AV RECPFV | Reclassify §18.1.3 + `katatapos+V` raising-from-XCOMP wiring |
| 7a.D | §18.1.1 #5 — `paano` wh-MANNER linker | 2 wh-ADV linker-fronting rules (`cfg/clause.py`) |
| 7a.E | §18.1.1 #6+7 — modal full-NP + no-linker | 4 modal-rule variants; `REGISTER=COLLOQUIAL` |
| 7a.F | §18.1.1 #8 — kahit-X no-`ay` | 1 ay-fronting variant; 3 in-place test renames |
| 7a.G | §18.1.1 #10 — kahit-X non-NOM | 2 any-case NP-projection rules; xfail flipped |
| 7a.H | §18.1.1 #1 — resumptive pronouns | Reclassify §18.1.3 (Phase 6.D L47 already canonical) |
| 7a.I | §18.1.1 #9 — `tila` modal-particle | Reclassify §18.1.3 (S&O sentence-adverb classification) |
| 7a.J | §18.1.1 #4 — statistical disambiguation | Reclassify §18.1.3 (downstream-tooling problem) |
| 7a.K | Closing docs | This entry + `docs/definitions.md` sweep |

<!-- markdownlint-enable MD013 -->

7a.H + 7a.I + 7a.J combined into a single bundled PR per user
directive 2026-05-14.

### Test count growth

| Phase end | Fast tests | Slow tests | xfail |
| --- | --- | --- | --- |
| Phase 6.J close | 7174 | 19 | 1 |
| Phase 7a.A close | 7211 | 19 | 1 |
| Phase 7a.B close | 7242 | 19 | 1 |
| Phase 7a.C close | 7255 | 19 | 1 |
| Phase 7a.D close | 7270 | 19 | 1 |
| Phase 7a.E close | 7280 | 19 | 1 |
| Phase 7a.F close | 7295 | 19 | 1 |
| Phase 7a.G close | 7306 | 19 | 0 (Phase 6.C C3f flipped) |
| Phase 7a.[HIJ] close | 7306 | 19 | 0 (docs-only) |
| Phase 7a.K close | 7306 | 19 | 0 |

Phase 7a adds **+132 fast tests** over Phase 6.J close
and flips the **Phase 6.C C3f xfail** to passing.

### New feats / atoms introduced

- `ASPECT_TYPE` enum, atom `JUST_FINISHED` (Phase 7a.C —
  matrix lift from `katatapos + V` raising).
- `REGISTER` atom `COLLOQUIAL` (Phase 7a.E §3.6 + Phase
  7a.F — new value on the existing REGISTER feat that
  already had POLITE / COLLOQUIAL_POLITE / LITERARY for
  Phase 5m politeness).

No new binary feats. All other Phase 7a uses (DISTRIB,
RECP, MOOD=SOC, INDEF=YES, NUM=PL) were existing feats
established by prior phases.

### New affix classes

- `magsi` (Phase 7a.B) — plural-actor AV pluralizer; 3
  aspect cells.
- `magpa_an` (Phase 7a.B) — reciprocal-distributive
  causative circumfix; 3 aspect cells.

### Phase 7a closing-status / parking-lot items

These were considered during Phase 7a planning but
explicitly deferred for cause:

- **Locative-distributive subtype of `magpa-…-an`** (Phase
  7a.B): GT-confirmed NOT productive (0/3 positive vs 1/1
  for reciprocal-distributive). Implementation scope-cut to
  reciprocal-distributive only.
- **`magsipag-` / `magsipang-` variants of magsi** (Phase
  7a.B): S&O §5.15 documents these for `mag-` / `mang-`
  base classes; deferred. Phase 7a.B closes only the simpler
  `magsi` for `-um-` verbs.
- **OV bare-no-actor `Katatapos kainin ang isda.`** (Phase
  7a.C): zero-parses today because the inner `kainin ang
  isda` doesn't parse standalone (pre-existing OV grammar
  limit). Not a Phase 7a.C issue.
- **Linker-form `Katatapos kong kumain.`** (Phase 7a.C):
  different syntactic construction (2nd-position GEN clitic
  between matrix and embedded V); not routed through
  `RAISING_BARE`. Out of v1 scope.
- **`tila` ADJUNCT/MODAL refactor** (Phase 7a.I): S&O's
  category label is `ADV`, not `V`; a future grammar refactor
  may prefer `ADJUNCT/MODAL` over the current `RAISING_BARE`
  engineering approximation. Tracked as a Phase 7+
  engineering-decision parking-lot item.
- **Kahit-X OBJ over-generation** (Phase 7a.G): each
  OBJ-position kahit-X surface produces 3 parses (canonical
  OBJ + ADJUNCT + residual artifact). Downstream filter
  recipe (`OBJ.INDEF=YES + LEMMA + WH`) documented in the
  Phase 7a.G design entry; consumers can pick the canonical
  reading. Investigation of the 3rd "residual" parse
  deferred to future cleanup.

### Carry-forward to Phase 7+

§18.1.3 (other-future-work-dependent) carries forward **17
items in three groups**:

- **6 pre-Phase-6 scope-expansion tracks** (in §18.1.3 since
  the v1 plan): Glue semantics and meaning representations;
  wider Philippine-type coverage (Cebuano / Hiligaynon /
  Ilokano); richer noun ontology for OBL semantic
  disambiguation; all-fragments mode; sentence-level tooling
  (discourse / anaphora / information-structure beyond
  TOPIC / FOCUS); no-comma asymmetric coordination.
- **7 Phase 6+ unifier extensions** parked at Phase 6 close:
  FU regex-path set-complement; FU defining-on-regex-LHS;
  FU Kleene-on-alternation (`{F | G}*` / `{F | G}+`); FU
  deferred defining-equation evaluation; FU inside-out
  designators; FU resolver-side cyclic-endpoint pruning;
  per-XCOMP binding rules for cross-clausal sarili.
- **4 Phase 7a-added reclassifications** (moved from §18.1.1
  by Phase 7a.C / 7a.H / 7a.I / 7a.J with strengthened
  rationale): Non-AV RECPFV morphological paradigm;
  resumptive pronouns in relative clauses; modal-particle
  reading of `tila`; statistical disambiguation over the
  packed forest.

Phase 7 is **not yet planned**. The codebase is
feature-complete for the canonical Tagalog construction
inventory across S&O 1972, R&B 1986, R&G 1981, R&C 1990,
and Kroeger 1993. The 17 §18.1.3 items remain awaiting
either corpus pressure or clear architectural motivation.

## Phase 8.X: DEM-pivot + non-wh PRON-pivot predicational clauses

The three-wave coverage audit (PRs #56-#59) surfaced an
unexpected near-miss: `Ito ang tatay ko.` "This is my dad."
and `Ito ang bahay ko.` "This is my house." — both textbook
`DEM ang NP-POSS` predications — produced zero parses on
the Wave 3 sample. Diagnostic probing also showed
`Ako ang guro.` "I am the teacher." failing the same way,
even though the simpler `Doktor ako.` "I am a doctor."
(Phase 5n.B Commit 2 predicative-N rule) works.

### Root cause

Two separate gaps in concert:

1. **No clause rule existed for DEM-as-predicate or non-wh
   PRON-as-predicate.** The Phase 5g predicative-ADJ rule
   (`Maganda ang aklat.`), the Phase 5n.B predicative-N rule
   (`Aklat ito.` — N pivot, DEM-as-subject), the Phase 5n.B
   predicative-Q rule, and the Phase 5i wh-PRON cleft rule
   together covered ADJ / Q / N / wh-PRON pivots — but no rule
   accepted a DEM-marked DET or a non-wh NOM PRON as the left
   daughter of an `S → X NP[CASE=NOM]` clause.
2. **The Wackernagel clitic-placement pass hoisted the
   sentence-initial PRON.** Phase 5n.A Commit 2 marked
   `ako` / `siya` / `tayo` / `kami` / `kayo` /
   `sila` with `is_clitic: true` (to fix `Hindi ako
   kumain`). The placement pass therefore moves a
   sentence-initial NOM-PRON to second position, **even when
   that NOM-PRON is functioning as the predicate of a
   PRON-pivot cleft**. After reorder, `Ako ang guro.`
   becomes `ang ako guro`, which no rule covers.

### Resolution

Two new clause rules in `cfg/clause.py` (sibling to the
predicative-N rule):

- `S → DET[CASE=NOM, DEM] NP[CASE=NOM]` — DEM-pivot.
  `(↑ PRED) = 'BE-DEM <SUBJ>'`; lifts `DEIXIS` from the
  demonstrative (PROX / MED / DIST). DEM_LEMMA is *not* lifted
  — see "Carve-out" below.
- `S → PRON[CASE=NOM] NP[CASE=NOM]` — non-wh PRON-pivot.
  `(↑ PRED) = 'BE-PRON <SUBJ>'`; lifts `NUM` and `CLUSV`
  from the pronoun. PRON_LEMMA and PERS are *not* lifted —
  same reason. Gated by `¬ (↓1 WH)` to keep the Phase 5i
  wh-PRON cleft as the canonical wh path.

One new placement-side companion in `clitics/placement.py`:
`_is_pre_ang_pred_pron` — sibling of `_is_pre_ay_pron`.
Suppresses Wackernagel hoisting when a NOM PRON-clitic is
immediately followed by a NOM determiner (`ang` / `si`),
preserving sentence-initial position so the new PRON-pivot
rule can fire on the natural left-to-right surface.

### Carve-out: PRON_LEMMA / DEM_LEMMA / PERS not lifted

The non-wh PRON entries in `data/tgl/pronouns.yaml` do not
register `LEMMA` as a feature (only the wh-PRON `sino`
does — that's why the Phase 5i wh-cleft can lift
`WH_LEMMA`). The DEM determiner entries likewise omit
`LEMMA`. Additionally, `PERS` in those entries is
registered as a Python `int` (`PERS: 1`), and integer
feature values do not currently propagate from morph analysis
to f-structure (only string atoms and bools do — `NUM`,
`CLUSV`, `CASE`, and `is_clitic` flow through).

Rather than touch the entire pronouns + DET lexicon (which
would be a broader change with cross-cutting implications),
8.X uses the features that *do* propagate. `DEIXIS` uniquely
identifies the demonstrative (PROX = ito, MED = iyan, DIST =
iyon); `NUM` + `CLUSV` jointly distinguish 1sg / 2sg / 3sg
/ 1pl-inclusive / 1pl-exclusive / 2pl / 3pl up to person. The
lemma / PERS carve-out is recorded here so a future
engineering pass (re-enabling integer-feat propagation, or
adding `LEMMA` to the relevant YAML entries) can revisit and
extend the rules' equation set.

### Phase 8 coverage impact

Re-running `scripts/harvest_exemplars.py parse` on the same
Wave 3 sample (seed=42, 500 per source):

| Source | Before 8.X | After 8.X |
| --- | ---: | ---: |
| S&O 1972 | 36 / 500 (7.2%) | 40 / 500 (8.0%) |
| R&G Conversational | 71 / 500 (14.2%) | 75 / 500 (15.0%) |

Aggregate cumulative naturalistic baseline (Waves 1+2+3,
2220 sents): **7.4% → 7.8%**. Modest but in the predicted
direction; the +8 clean parses are the DEM-pivot and
PRON-pivot sentences in the Wave 3 sample.

### Partial closure of Phase 8.S

Phase 8.S (pronominal-pivot clefts, surfaced in the Wave 3
audit) listed three example sentences:

- `Tayo ang lumakad.` — PRON pivot + V-headed ang-NP
  subject. *Still failing.* The pivot subject is a VP-
  nominalization (`ang lumakad` "the one who walked"), which
  requires a separate NP-projection from a tensed V. Remains
  in 8.S scope.
- `Akin ang tinapay.` — DAT-PRON possessive pivot. *Still
  failing.* The PRON here is in DAT case (`akin`, not
  `ako`), and the construction is semantically possessive
  ("the bread is mine"), not equational. Remains in 8.S scope.
- `Ako ang guro.` *(probed during 8.X)* — non-wh NOM-PRON
  + ang-NP[N]. **Closed by 8.X.**

Phase 8.S is now narrowed to the V-pivot subset (`Tayo ang
lumakad`) and the DAT-PRON possessive-pivot subset (`Akin
ang tinapay`).

### Out-of-scope follow-ons surfaced

Two related construction patterns also surfaced as failing
during 8.X probing but are explicitly out of 8.X scope:

- `Ito ay aklat.` — `ay`-inverted DEM-pivot. Needs a
  parallel extension to the Phase 4 §7.4 `ay`-fronting rule
  family. Phase 8 follow-on candidate.
- `Si Juan ito.` — proper-noun-NP-pivot + DEM-subject. The
  N-pivot rule accepts bare `N` (`Doktor ito.` works); the
  `si`-marked proper-NP doesn't reduce to bare N, so the
  rule doesn't fire. Phase 8 follow-on candidate.

(Both follow-on candidates closed in Phase 8.Y immediately
below — per the anti-deferral principle, surfaced gaps are
closed rather than left as new deferrals.)

## Phase 8.Y: ay-inverted N-pivot + Si-NP-pivot two-NP equational

Phase 8.Y closes the two near-misses surfaced during 8.X
probing (the "Out-of-scope follow-ons surfaced" entries in the
Phase 8.X writeup above). Per the anti-deferral principle —
when corpus pressure or diagnostic probing surfaces a gap,
close it rather than queueing a "Phase 8 follow-on candidate"
— both were promoted into Phase 8.Y as one bundled PR.

### Rule 1: ay-inverted N-pivot

`Ito ay aklat.` "This is a book.", `Ako ay guro.` "I am a
teacher.", `Iyon ay bahay ko.` "That is my house." — the
ay-fronted mirror of the Phase 5n.B N-pivot rule
(`S → N NP[CASE=NOM]`). The Phase 4 §7.4 ay-fronting family
covers V-headed clauses (`S_GAP`), predicative-ADJ clauses
(`S_GAP_PREDADJ`), and SubordClause topics; this rule adds
the N-headed-predicate variant without a parallel
`S_GAP_PREDN` gap non-terminal — the equation set is small
enough that direct construction is simpler than threading a
gap clause.

Shape (mirrors the N-pivot rule with SUBJ bound to the
fronted ↓1):

```text
S → NP[CASE=NOM] PART[LINK=AY] N
    (↑ PRED)        = 'BE-N <SUBJ>'
    (↑ SUBJ)        = ↓1
    (↑ TOPIC)       = ↓1
    (↑ N_LEMMA)     = ↓3 LEMMA
    (↑ PREDICATIVE) = true
    ¬ (↓3 WH)
```

SUBJ and TOPIC both reference the fronted NP (ay-fronting
is topicalization in LFG terms; both gf and discourse
function point to the same node).

### Rule 2: Si-NP pivot two-NP equational

`Si Juan ito.` "This is Juan.", `Si Maria iyan.`, `Si Pedro
iyon.`, `Si Juan ang doktor.` "Juan is the doctor." — the
Phase 5n.B N-pivot rule docstring explicitly defers two-NP
equational to corpus pressure, and the Wave 3 audit surfaced
`Si Juan ito.` as a zero-parse. The Si-pivot variant is
closed here.

Shape:

```text
S → NP[CASE=NOM] NP[CASE=NOM]
    (↓1 MARKER)     =c 'SI'
    (↑ PRED)        = 'BE-NP <SUBJ>'
    (↑ SUBJ)        = ↓2
    (↑ PRED-NP)     = ↓1
    (↑ PREDICATIVE) = true
```

The constraining equation `(↓1 MARKER) =c 'SI'` restricts the
pivot to si-marked proper-noun NPs. The fully-general ang-pivot
variant (`Ang lalaki ang doktor.`) was NOT in the audit zero-
parse list and has known parse-ambiguity interactions with
pseudo-cleft (`Ang nanay ang nagluto.`); leaving it deferred
is consistent with the original Phase 5n.B intent. If corpus
pressure surfaces it, the rule generalizes by dropping the
MARKER constraint.

### Rule-2 syntax note

The initial draft of Rule 2 used a category-level feature
constraint `NP[CASE=NOM, MARKER=SI]`. That form did not
match — the parser's non-conflict feature matcher uses a
limited set of "indexed" features for category dispatch, and
`MARKER` is not in that set. Converting to an explicit `=c`
constraining equation in the body resolved the match. Pattern
to remember for future rule additions: **use `=c` constraint
equations for restricting on features outside the indexed
dispatch set**, not category brackets.

### Carve-outs (intentionally not closed in 8.Y)

- `Ito ay aklat ko.` — ay-inverted N-pivot with possessor-
  modified N. The possessor rule binds at NP level
  (`NP[CASE=NOM] → NP[CASE=NOM] NP[CASE=GEN]`), so `aklat ko`
  is NP, not N. Widening 8.Y Rule 1's right daughter from
  `N` to `NP[CASE=NOM]` would converge it with two-NP
  equational; a clean closure needs an N-level possessor rule.
  Not in the Wave 3 audit zero-parse list (was my own probe
  extrapolation during 8.X); leaving deferred until corpus
  pressure or a dedicated N-modifier-inventory refactor.
- `Ang lalaki ang doktor.` — *originally listed as carve-out;
  closed in Phase 8.Z below.* User verified the natural reading
  ("The man is the doctor."), and probing for 8.Z confirmed
  pseudo-cleft is itself zero-parsing under the pre-existing
  grammar, so the disambiguation concern was hypothetical.

### Coverage impact

Re-running the seed=42 Wave 3 parse sample (500 sentences per
source):

| Source | After 8.X | After 8.Y |
| --- | ---: | ---: |
| S&O 1972 | 40 / 500 (8.0%) | 40 / 500 (8.0%) |
| R&G Conversational | 75 / 500 (15.0%) | 77 / 500 (15.4%) |

Modest: +2 sentences (both in R&G Conversational; the
audit sample contains few `Si X DEM` and `X ay N` shapes by
chance). The cumulative naturalistic baseline (Waves 1+2+3,
2220 sents) moves from 7.8% to 7.9%.

The small numerical bump reflects how thinly distributed
these particular constructions are in the corpus — they're
real Tagalog patterns, but not high-frequency in pedagogical
or descriptive prose. The motivation for closing them is
correctness against the surfaced gaps, not parse-rate
optimization.

## Phase 8.Z: generalize 8.Y Rule 2 to ang-pivot equational

Drops the `(↓1 MARKER) =c 'SI'` gate from the Phase 8.Y
two-NP equational rule. The user verified `Ang lalaki ang
doktor.` "The man is the doctor." as the natural reading
(Google Translate produces the equational gloss; native-
speaker check by user confirms). The 8.Y carve-out citing
"parse-ambiguity with pseudo-cleft" was unjustified by the
actual parser state — diagnostic probing for 8.Z confirmed
pseudo-cleft (`Ang lalaki ang nagluto.`) was itself zero-
parsing under the pre-existing grammar, so the gate was
preventing closure of one construction class without benefit
to another. Per the anti-deferral principle (Phase 5n debt-
clearing precedent), the gate is removed.

### Rule shape (post-8.Z)

```text
S → NP[CASE=NOM] NP[CASE=NOM]
    (↑ PRED)        = 'BE-NP <SUBJ>'
    (↑ SUBJ)        = ↓2
    (↑ PRED-NP)     = ↓1
    (↑ PREDICATIVE) = true
    ¬ (↓1 WH)
```

### Two-step closure: WH gate added

A naive removal of the SI gate caused a regression cascade:
wh-PRON cleft sentences (`Sino ang kumain?`, `Ano ang kinain
mo?`) gained a spurious BE-NP parse alongside the canonical
wh-cleft parse. The reason: wh-PRONs (`Sino`, `Ano`, `Alin`)
are PRON[WH=true, CASE=NOM], which wraps to NP[CASE=NOM] via
the bare-PRON NP rule (`NP[CASE=NOM] → PRON[CASE=NOM]` in
`cfg/nominal.py`). So the new rule fires on `[Sino] [ang
kumain]` with both daughters as NP[NOM], producing a
duplicate parse.

Fix: add `¬ (↓1 WH)` to the rule body. This keeps wh-PRONs
routed exclusively through the Phase 5i Commit 2 wh-PRON
cleft rule (`S → PRON[WH, CASE=NOM] NP[CASE=NOM]`). The same
constraint was used by Phase 8.X on the non-wh PRON-pivot
rule.

### Coverage impact

Re-running the seed=42 Wave 3 parse sample (500 sentences
per source):

| Source | After 8.Y | After 8.Z |
| --- | ---: | ---: |
| S&O 1972 | 40 / 500 (8.0%) | 41 / 500 (8.2%) |
| R&G Conversational | 77 / 500 (15.4%) | 78 / 500 (15.6%) |

Cumulative naturalistic baseline (Waves 1+2+3, 2220 sents):
7.9% → 8.0%. The shift includes some sentences that moved
from `parse-success-1` to `parse-success-N` — the new rule
introduces ambiguity for sentences whose surface admits both
an existing parse and the new equational parse. The
ambiguity is structurally real (the surfaces are equational-
compatible); disambiguation is a downstream concern.

### Still zero-parsing

`Ang lalaki ang nagluto.` (pseudo-cleft equational reading)
remains zero-parsing post-8.Z. The blocker is the headless-
RC `ang nagluto` not wrapping to NP[CASE=NOM] under the
current Phase 5e Commit 5 free-relative rule's gating —
investigated during 8.Z probing, confirmed as a separate
gap class, out of 8.Z scope. Tracked as a follow-on near-
miss for future work (anti-deferral note: this one is a
distinct construction gap, not a re-deferral of the equa-
tional case 8.Z closed).
