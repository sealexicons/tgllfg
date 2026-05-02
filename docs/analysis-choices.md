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
omitted from `affix_class` with a comment in `roots.yaml` flagging
the gap.

### Citation policy

Per-verb citations live as YAML comments in `data/tgl/roots.yaml`
referencing R&B 1986 page numbers. The Ramos 1971 dictionary OCR
and the R&B 1986 PDF live under `data/tgl/dictionaries/`
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

```
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

`data/tgl/clitic_order.yaml` tabulates priorities for known
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

* No verb-host: verbless fragments fall through unchanged. The
  placement pass is verb-anchored.
* SOC mood (e.g. `magkape tayo`) requires the `tayo` 1pl-incl
  pronoun in pivot position with mag-class morphology. SOC stays
  inventory-only (Phase 4 §7.2) until §7.6 / §7.7 wire it up.
* Three-way clitic ambiguity (e.g. some pronouns can be NOM or
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

```
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

```
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

```
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

```
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

```
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

```
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

```
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

* **Truly unbounded control chains** (more than ~5 deep): the
  parser explores them, but the test corpus exercises 4-deep at
  most. If future corpus pressure shows runaway parser cost on
  arbitrarily deep chains, a chart-pruning heuristic — not
  functional uncertainty — would be the right response.
* **Long-distance relativization** through nested XCOMP/COMP
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

```
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

```
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

```
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

```
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

```
$ tgllfg parse "Kumain ang aso ng isda."
Parse #1:
  PRED: EAT <SUBJ, OBJ>
  VOICE: AV
  ASPECT: PFV
...
```

On failure, default mode emits fragments:

```
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

* Lex entry has one voice-independent profile per role (e.g.,
  `kain` always has `AGENT [-o]`, `PATIENT [-r]`).
* Voice morphology adds the SUBJ-promotion stamp at parse time.

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

* `ACTOR` is needed because the synthesizer fallback emits
  `[ACTOR]` when transitivity is unspecified; folding to AGENT
  would lose the "voice-independent intransitive" signal.
* `CONVEYED` behaves like `THEME` in the truth table, but voice-
  marked differently in IV — keeping the role distinct lets each
  lex entry document which thematic flavor it expects.
* `CAUSER` / `CAUSEE` / `EVENT` participate in causative frames
  whose mapping diverges from monoclausal transitives; they
  carry distinct intrinsic-classification profiles.
* `COMPLEMENT` is XCOMP-bound and never appears in the truth
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

| Engine source | Surfaced? | Routing |
|---|---|---|
| Step 6 `subject-condition-failed` (lex profile has no SUBJ candidate) | dropped | The structural `lfg_well_formed` downstream catches the case where the f-structure also lacks SUBJ. If the f-structure has SUBJ, the parse is structurally OK and shouldn't be suppressed for an internal lex inconsistency. |
| Step 7 `lmt-biuniqueness-violated` (two roles → same GF) | yes | Always a real lex contradiction; surfaced as-is (blocking by absence from `NON_BLOCKING_KINDS`). |

`lmt_check` adds two more diagnostic emitters of its own:

| Condition | Routing |
|---|---|
| Engine predicts SUBJ for some role but the f-structure lacks SUBJ | **Blocking** (`subject-condition-failed`) |
| GF-set difference excluding SUBJ slot (the OBJ ⇄ OBJ-θ noise) | Informational (`lmt-mismatch`) |

The reverse SUBJ disagreement (f-structure has SUBJ but engine
didn't predict one) means a buggy lex profile but a valid parse
— stays informational via the general `lmt-mismatch`. Blocking
the parse for a lex-internal inconsistency would be wrong.

### Out-of-scope (deferred)

* **Multi-GEN-NP applicative / causative frames.** A 3-arg
  `ipinaggawa niya ng silya ang kapatid` profile cleanly
  produces `OBJ-AGENT`, `OBJ-PATIENT`, `SUBJ` from the engine,
  but no Phase 4 BASE entry emits them and the grammar rules
  need a second-GEN-NP slot. Phase 5b.
* **Multi-OBL semantic disambiguation.** When two `OBL-θ` roles
  compete for two sa-NPs, positional matching is the placeholder.
  **Update (Phase 5c):** lifted in Phase 5c §8 follow-on Commit 6
  via lemma-keyed semantic-class lookup (see the entry below).
* **Embedded-clause LMT.** `lmt_check` only validates the matrix
  f-structure. Embedded XCOMP/COMP clauses have their own PRED
  and could be recursively checked; not wired.
* **`OBJ-θ` in the grammar.** The Phase 4 grammar emits bare `OBJ`
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

```
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

```
MAKE-FOR <SUBJ, OBJ-AGENT, OBJ-PATIENT>
```

Completeness checks the f-structure has all three governables;
coherence checks no extras. The pre-existing two-arg lex entry
(`MAKE-FOR <SUBJ, OBJ>`, no PATIENT) coexists — sentences without
a second ng-NP fall through to it because the three-arg's
completeness check fails when OBJ-PATIENT is absent.

### Scope

The multi-GEN-NP frames lifted in Phase 5b so far:

* **IV-BEN applicatives** (`gawa`, `sulat`, `bili`) — Commit 1.
  Pivot is BENEFICIARY; non-pivot ng-NPs are AGENT and PATIENT,
  bound positionally to `OBJ-AGENT` and `OBJ-PATIENT`.
* **pa-OV-direct causatives** (`kain`, `basa`, `inom`) — Commit 2.
  Pivot is CAUSEE; non-pivot ng-NPs are CAUSER and PATIENT,
  bound to `OBJ-CAUSER` and `OBJ-PATIENT`. The grammar matches
  `V[VOICE=OV, CAUS=DIRECT]` specifically so plain OV transitives
  (CAUS=NONE) don't spuriously trip the multi-GEN rule.

Still deferred:

* **DV three-argument constructions** (rarer): would need a
  third ng-NP for a non-RECIPIENT theme. No current Phase 4
  BASE entry has the shape.
* **Magpa-AV-indirect three-argument** would require the embedded
  XCOMP to take its own arguments — the matrix only has CAUSER
  and EVENT, so multi-GEN doesn't apply at the matrix level.

The Phase 5b deferral list also includes:

* **Multi-OBL semantic disambiguation** for sa-NPs — out of
  scope here (this commit is GEN-only).
* **OV/DV control complements** — separate problem (controller
  binds embedded AGENT, not embedded SUBJ).
* **OBJ-θ in the grammar** — the Phase 4 grammar emits bare
  `OBJ` for non-AV ng-non-pivots while the LMT engine produces
  typed `OBJ-θ`. Aligning the two would eliminate the
  informational `lmt-mismatch` noise but touches every per-voice
  grammar rule.
* **Raising verbs**, **`ipang-` / `ika-` applicatives**,
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

```
NP[CASE=NOM] → DET[CASE=NOM] Q NP[CASE=GEN]
NP[CASE=GEN] → ADP[CASE=GEN] Q NP[CASE=GEN]
NP[CASE=DAT] → ADP[CASE=DAT] Q NP[CASE=GEN]
```

Equations:

```
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

* `ang aklat ng bata` (possessive) — DET + N + NP[GEN], parsed
  by the Phase 4 §7.8 NP-internal possessive rule. Without a Q
  in position 2, only the possessive rule fires.
* `ang lahat ng bata` (partitive) — DET + Q + NP[GEN], parsed by
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

* After a VERB (`Kinain mo ang isda`): `mo` is the OBJ-AGENT
  clitic — moved to the post-V cluster (unchanged behaviour).
* After a PART (`Hindi mo kinain ang isda`): pre-V clitic, also
  moved to the post-V cluster (unchanged behaviour).
* After a NOUN (`ang isda ko`): possessive — left in place
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

* **Pronominal possessor inside a relative clause head.** A noun
  followed by a linker + RC (`aklat na binasa`) followed by a
  pronoun would compete with the RC's own SUBJ-binding; the
  parser would need to decide whether `ko` belongs to the head
  noun or the relative clause. Not exercised by the current
  corpus.
* **Possessive linker variant** (`aklat kong binasa` —
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
|---|---|
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

```
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

```
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

```
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

Two seed nouns were added to ``data/tgl/roots.yaml`` to give the
new applicatives natural test fixtures: ``karayom`` "needle"
(instrument) and ``gutom`` "hunger" (canonical reason).

### Out-of-scope (still deferred)

* **Multi-GEN-NP IV-INSTR / IV-REASON frames.** Three-argument
  variants where AGENT, PATIENT, and INSTRUMENT/REASON are all
  GEN/NOM-marked at once (parallel to Phase 5b §7.7 multi-GEN
  IV-BEN). Not seeded; the 2-arg shape covers the common cases.
* **Other ipang- senses.** ``pang-`` also forms purpose nominals
  (``pambili`` "for buying / shopping") and abilitative-like
  derivations. Only the instrumental applicative IV reading is
  seeded here.
* **AV instrumental ``mang-`` retain readings.** Some bases
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

```
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

```
SEEM <XCOMP> SUBJ      mukha   a_structure=[COMPLEMENT]
MIGHT <XCOMP> SUBJ     baka    a_structure=[COMPLEMENT]
```

Only one thematic role (COMPLEMENT, the proposition) — SUBJ is
non-thematic and bears no theta role. The matching intrinsic
profile ``_RAISING`` has the single COMPLEMENT entry with
``(None, None)`` (XCOMP-stipulated, off the truth table).

**(c) Grammar wrap rule.** A new pattern in
:file:`src/tgllfg/cfg/grammar.py`:

```
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
the latter pre-existing in :file:`data/tgl/roots.yaml`; ``mukha``
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

```
Mukhang kumakain ang bata.            — "the child seems to be eating"
Mukhang kumain ang bata.               (PFV embedded)
Mukhang kinakain ng aso ang isda.     — OV embedded; matrix.SUBJ = isda
Mukhang kumakain ang bata ng isda.    — embedded AV transitive with OBJ
Mukhang hindi kumakain ang bata.      — inner negation in XCOMP
Bakang umuwi ang bata.                — "the child might leave"
```

### Out-of-scope (still deferred)

* **Raising chains** (raising matrix embedding another raising
  matrix — ``Mukhang bakang umuwi ang bata``). The wrap rule's
  right-hand S admits any complete clause, so this should
  technically work; not exercised by the corpus and not
  separately tested.
* **Other raising verbs.** Tagalog has a small closed class —
  ``parang``, ``tila``, ``yata`` are also raising-like. Only
  ``mukha`` and ``baka`` are seeded.
* **Raising under control** (a control verb embedding a raising
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

```
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

* **Richer noun ontology.** The seed lemma tables are
  intentionally small (a dozen entries each). Real disambiguation
  for an open-domain corpus would consult a richer noun
  semantics resource.
* **Case-by-case override.** No mechanism for a lex entry to
  override the classifier's preferences (e.g., a verb whose
  ``OBL-RECIP`` semantically prefers PLACE rather than
  ANIMATE — rare but possible).
* **Three-or-more sa-NPs in one clause.** Tagalog rarely
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

```
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

```
S → V[CTRL_CLASS=RAISING_BARE] S
   (↑ XCOMP) = ↓2
   (↑ SUBJ) = (↑ XCOMP SUBJ)
```

The existing ``CTRL_CLASS=RAISING`` linked rule is unchanged.
``mukha`` / ``baka`` keep ``RAISING``; ``parang`` / ``tila``
get ``RAISING_BARE``. No cross-firing, no duplicate parses.

### Lex entries

```
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

* **Comparative ``parang``** ("X is like Y"). The existing
  raising entry covers the evidential reading
  (``parang + clause``). The comparative reading
  (``parang + NP``) is structurally distinct and needs a
  separate grammar rule. Deferred until corpus pressure shows
  comparative coverage matters.
* **Linker-optional ``parang``** dialect form (``Parang
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

```
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

```
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

```
Pinakainan ng nanay ang bata.    "mother fed the child"
Pinabasahan ng nanay ang bata.   "mother read [aloud] to the child"
Pinainuman ng nanay ang bata.    "mother gave the child a drink"
Pinakakainan ng nanay ang bata.  IPFV
Pakakainan ng nanay ang bata.    CTPL
```

### Out-of-scope (still deferred)

* **Three-argument pa-DV** (with overt PATIENT alongside
  CAUSER and LOCATION/RECIPIENT). Multi-GEN-NP DV variants
  parallel Phase 5b's pa-OV-direct three-arg pattern; not
  exercised by the current corpus.
* **Other less-common causative variants** (``ka-...-an``
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

```
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

```
(↑) = ↓1                  -- head NP's f-structure becomes the matrix
(↑ DEIXIS) = ↓3 DEIXIS    -- copy deixis from the modifier
```

The PRED stays the head noun's PRED — the demonstrative
modifies, doesn't supplant. Compare with Phase 4 §7.8's
standalone-demonstrative rule, which uses ``(↑) = ↓1`` to
share with the demonstrative directly (no head noun) and adds
``(↑ PRED) = 'PRO'`` so completeness passes.

### Surface variants enabled

```
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

* **Pre-modifier demonstrative with linker** (``itong batang``
  "this child" — modifier-first variant). Tagalog admits both
  orders; only post-modifier is wired. Pre-modifier would need
  parallel rules in the reverse direction.
* **Demonstrative as modifier of a relativized head**
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

The Phase 5b multi-GEN-NP rules in :file:`cfg/grammar.py` are
voice-restricted to ``V[VOICE=IV]`` without an APPL constraint:

```
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

```
bili IV-INSTR  : BUY-WITH        <SUBJ, OBJ-AGENT, OBJ-PATIENT>
tahi IV-INSTR  : SEW-WITH        <SUBJ, OBJ-AGENT, OBJ-PATIENT>
kain IV-REASON : EAT-FOR-REASON  <SUBJ, OBJ-AGENT, OBJ-PATIENT>
sulat IV-REASON: WRITE-FOR-REASON <SUBJ, OBJ-AGENT, OBJ-PATIENT>
```

The 2-arg variants from Phase 5c Commit 4 are unchanged; both
forms coexist in BASE. The lex entry that matches a given parse
is determined by NP count:

* 2 NPs (1 ng-NP + 1 ang-NP) → 2-arg PRED
* 3 NPs (2 ng-NPs + 1 ang-NP) → 3-arg PRED via multi-GEN

### Sentences enabled

```
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

* **DV three-argument constructions.** Phase 5b's
  multi-GEN rules are IV-only. DV multi-GEN
  (``Sinulatan ng nanay ng letra ang anak``
  "mother wrote (a letter) to the child") would need
  parallel DV multi-GEN rules. Not exercised by corpus.
* **Multi-GEN-NP under embedded control.** Crosses with
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

* **OBJ-θ in any voice** (the ``ng``-marked non-pivot in AV, or
  the ``ng``-marked actor in non-AV).
* **DAT-marked obliques** (locatives, recipients,
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

```
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

```
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

* AV OBJ-fronting: ``Ng isda ay kumain si Maria`` (eat-AV with
  OBJ topicalized).
* Non-AV OBJ-AGENT-fronting: ``Ni Maria ay kinain ang isda``
  (eat-OV with actor topicalized); ditto for DV (``Ng bata ay
  kinainan ang nanay``) and IV (CONVEY / INSTR / REASON variants).
* DAT OBL-fronting: ``Sa bahay ay kumain si Maria``,
  ``Sa bahay ay kinain ni Maria ang isda``.
* Negation under fronting (each gap-category recurses through
  ``PART[POLARITY=NEG]``).

### Out-of-scope (still deferred)

* **Multi-GEN-NP ay-fronting.** Phase 5b multi-GEN constructions
  (IV-BEN three-arg, pa-OV-direct three-arg) have two GEN-NPs
  filling typed OBJ-AGENT and OBJ-PATIENT positionally. Fronting
  one of the two would require a different gap shape — the
  remaining GEN-NP's binding is no longer purely positional. Not
  exercised by corpus.
* **AdvP / PP fronting.** ``Kahapon ay tumakbo si Maria``
  (temporal AdvP), ``Para sa bata ay binili niya ang aklat``
  (PP). Out of scope until the categorial inventory expands
  (§7.8 / Phase 6).
* **Pa-OV (CAUS=DIRECT) actor-fronting.** Would need a parallel
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

```
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

```
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

```
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

* ``Lumakad ang bata kong kinain.`` — possessive-linker RC in SUBJ
  position with 1SG ``ko``.
* ``Kumain ang bata ng libro kong binasa.`` — possessive-linker RC
  in OBJ position.
* All three vowel-final GEN pronouns: ``ko`` (1SG), ``mo`` (2SG),
  ``niya`` (3SG).
* OV / IV verbs in the RC; DV variants follow the same shape.
* Negation under the construction
  (``Lumakad ang bata kong hindi kinain.``).

### Out-of-scope (still deferred)

* **Consonant-final pronouns** with the standalone ``na`` linker
  (``aklat namin na binasa`` "the book that we read", with 1PL.EXCL
  ``namin``). The current commit handles only ``-ng`` (vowel-final
  PRON + bound linker). A parallel rule with ``PART[LINK=NA]``
  would be additive.
* **Non-pronominal possessors with linker** (``aklat ng batang
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

```
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

```
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

* Raising chains: 5 variants (linked-linked, linked-bare,
  bare-linked, bare-bare; both NA and NG linker variants where
  applicable).
* Raising under control: PSYCH (gusto / ayaw / kaya) and INTRANS
  (pumayag) with both linked and bare raising matrices.
* Raising chains under control: 4-level XCOMP (``Gusto kong
  mukhang bakang kumakain``) with all four SUBJ slots structurally
  identical (Python-id equality verified by tests).

### Out-of-scope (still deferred)

* **Control under raising.** A raising verb embedding a control
  matrix (``Mukhang gusto ng batang kumain`` "It seems the child
  wants to eat"). Composes via the existing ``S → V[RAISING] PART
  S`` rule with ``S`` being a control-S; needs no new rule but
  hasn't been pinned with tests in this commit.
* **TRANS control + raising.** ``Pinilit ng nanay ang batang
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

* ``OBJ-CAUSER`` — the agent / instigator (who causes the event).
* ``OBJ-PATIENT`` — the patient (in the 3-arg pa-OV form;
  optional in the 2-arg form and absent in pa-DV).
* ``SUBJ`` — the causee (pa-OV) or location/recipient (pa-DV).

Under control, the matrix verb's controller binds the embedded
``OBJ-CAUSER`` (the caused-event actor):

```
Gusto niyang pakakainin ang bata.   "She wants to feed the child."
   gusto.SUBJ === XCOMP.OBJ-CAUSER  (id-equal)
   gusto.SUBJ.LEMMA = niya
   XCOMP.PRED      = CAUSE-EAT <SUBJ, OBJ-CAUSER>
   XCOMP.SUBJ      = bata           (the causee)
```

### Four new S_XCOMP rules

```
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

* pa-OV under PSYCH control: ``Gusto niyang pakakainin ang bata``
  ("she wants to feed the child"); 3-arg variants with overt
  patient.
* pa-OV under INTRANS control: ``Pumayag siyang pakakainin ang
  bata``.
* pa-OV under TRANS control: ``Pinilit ng nanay ang batang
  pakakainin ang aso`` ("mom forced the child to feed the dog");
  the forcee (matrix.SUBJ) is the controller, NOT the forcer
  (matrix.OBJ-AGENT).
* pa-DV under PSYCH and INTRANS control.
* SUBJ control identity: the embedded ``OBJ-CAUSER`` is the same
  Python f-structure as the matrix controller — verified by
  Python-id equality in tests.

### Out-of-scope (still deferred)

* **3-arg pa-DV under control.** The Phase 5d Commit 2 pa-...-an
  cells are 2-arg only (``CAUSE-EAT-AT <SUBJ, OBJ-CAUSER>``); a
  3-arg pa-DV with overt patient would need a new lex profile,
  not just a new S_XCOMP rule.
* **Nested pa-causatives under control.** A pa-OV control
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

```
S_XCOMP → V[VOICE=IV, APPL=CONVEY] NP[CASE=NOM]
```

The ``APPL=CONVEY`` filter only matched the bare ``i-`` reading
(conveyance, e.g. ``ibibili`` "buy as conveyance"). The IV-BEN
(``ipag-``), IV-INSTR (``ipang-``), IV-REASON (``ika-``)
applicatives carry ``APPL=BEN`` / ``INSTR`` / ``REASON``
respectively, so the rule never fired for them. Commit 9 drops
the APPL filter:

```
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

```
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

* IV-BEN under PSYCH / INTRANS / TRANS control: 2-arg
  (``Gusto kong ipaggagawa ang kapatid``) and 3-arg (``Gusto kong
  ipaggagawa ng silya ang kapatid``).
* IV-INSTR under control: 2-arg + 3-arg.
* IV-REASON 3-arg under PSYCH control (PFV form ``ikinakain``;
  the CTPL form ``ikakain`` resolves as IV-CONVEY in the current
  paradigms).
* SUBJ control identity verified by Python-id equality between
  matrix controller and embedded ``OBJ-AGENT``.

### Out-of-scope (still deferred)

* **IV-REASON CTPL paradigm gap.** The CTPL form ``ikakain``
  analyses as IV-CONVEY rather than IV-REASON in the current
  morph paradigms. Tests use the PFV form ``ikinakain`` to
  exercise IV-REASON 3-arg under control. Resolving the paradigm
  ambiguity would need a paradigms.yaml or analyzer change beyond
  Commit 9's scope.
* **IV multi-GEN under nested (long-distance) control.** The
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

```
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

* PRON after the **matrix V** — that's the regular Wackernagel
  cluster position; placement is a no-op (preceding V === first V).
* PRON after a **non-first V** — the PRON belongs to that
  embedded V's clause (RC, control complement, etc.), not to the
  matrix V. Suppress the move so the embedded clause's grammar
  rules can absorb it.

After the fix:

```
Tumakbo ang batang kinain ko
   pre-reorder:  takbo ang bata -ng kain ko
   post-reorder: takbo ang bata -ng kain ko    ← ko stays after kain
   parses=1                                     ← OV S_GAP ✓
```

### Competing readings

The plan §9.1 entry flags "pronominal possessor inside relative
clause head" — the construction can in principle have two
readings:

* **RC-actor reading** — the pronoun is the gap-filler inside
  the RC (OV / DV / IV bind it to ``OBJ-AGENT``).
* **Possessor reading** — the pronoun is a possessor on the head
  NP (the existing NP-internal possessive rule).

For OV / DV / IV-RC, only the RC-actor reading is structurally
available because the non-AV S_GAP frames require a GEN-NP after
the V. The possessor reading would need an empty S_GAP (V alone
without a GEN-NP), which the existing rules don't admit. So the
parse is unique.

For AV-RC, both readings parse:

* Reading A: AV-transitive RC where the pronoun is bare ``OBJ``
  (``Tumakbo ang batang kumain ko`` "the child who-ate-me ran").
* Reading B: AV-intransitive RC plus pronominal possessor on the
  head NP (``my child who ate ran``).

Tests cover both by walking the parse list and finding each
shape. The ranker is left to its existing heuristics — pragmatic
disambiguation between the two AV-RC readings depends on the verb
and is not a structural concern.

### What this lifts

* Pronominal RC-actor in OV / DV / IV relativization
  (``Tumakbo ang batang kinain ko``).
* All three vowel-final GEN pronouns (ko / mo / niya).
* Bound ``-ng`` linker (vowel-final head) and standalone ``na``
  linker (consonant-final head).
* RCs nested inside OBJ NPs (``Kumain ang aso ng batang kinain
  ko``) — placement still keeps the pronoun in the embedded RC
  because the Wackernagel logic is per-token, not per-NP.
* AV-RC ambiguity (RC-with-OBJ vs head-possessor) preserved as
  competing parses.

### Out-of-scope (still deferred)

* **`na` linker disambiguation after PRON.** ``Tumakbo ang bata
  ko na nakita`` (possessor + RC) — the placement pass currently
  treats the standalone ``na`` after PRON as the 2P aspectual
  clitic and moves it to clause-end. Resolving this requires
  extending :func:`disambiguate_homophone_clitics` to look at the
  following token (if VERB, ``na`` is the linker). Not pursued
  in Commit 10.
* **Multi-pronoun RCs.** A single matrix sentence with both a
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

```
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

* 2-arg pa-OV actor-fronting:
  ``Ng nanay ay pinakain ang bata.``
* 3-arg pa-OV actor-fronting (both NP orders):
  ``Ng nanay ay pinakain ang bata ng kanin.``
  ``Ng nanay ay pinakain ng kanin ang bata.``
* 2-arg pa-DV actor-fronting:
  ``Ng nanay ay pinakainan ang bata.``
* All three pa-OV anchor verbs (kain / basa / inom) and three
  pa-DV anchor verbs (kain / basa / inom).
* IPFV aspect on the embedded V (``pinakakain``).
* Inner negation under fronting
  (``Ng nanay ay hindi pinakain ang bata.``).

### Out-of-scope (still deferred)

* **3-arg pa-DV actor-fronting.** Blocked on the 3-arg pa-DV
  lex profile; lifts as a follow-on once that lands (plan §10.1
  Group D).
* **Pa-OV / pa-DV actor-fronting under embedded control.** The
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

* 3-arg IV with OBJ-AGENT extracted (OBJ-PATIENT retained):
  ``Ng nanay ay ipinaggawa ang kapatid ng silya``.
* 3-arg multi-GEN with OBJ-PATIENT extracted (in either IV with
  OBJ-AGENT retained, or pa-OV-direct with OBJ-CAUSER retained):
  ``Ng silya ay ipinaggawa ang kapatid ng nanay``,
  ``Ng kanin ay pinakain ng nanay ang bata``.

### S_GAP_OBJ_AGENT IV 3-arg additions

The Phase 5d Commit 5 ``S_GAP_OBJ_AGENT`` rules covered only
2-arg shapes (V plus a single NOM pivot, optionally with a DAT
adjunct). Two IV-only 3-arg variants are added:

```
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

```
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

```
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

* ``S_GAP_OBJ_AGENT`` 3-arg: gap = OBJ-AGENT, retained = OBJ-PATIENT.
* ``S_GAP_OBJ_PATIENT`` IV: gap = OBJ-PATIENT, retained = OBJ-AGENT.

Both rules fire and both wrap rules above succeed (with their
respective constraining equations). The result is two parses for
the same surface, distinguished by which fronted-NP role binds:

* ``Ng nanay ay ipinaggawa ang kapatid ng silya`` admits both
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

* IV-BEN / IV-INSTR / IV-REASON 3-arg with AGENT fronted
  (``Ng nanay ay ipinaggawa ang kapatid ng silya``,
  ``Ng nanay ay ipinambili ang pera ng isda``,
  ``Ng bata ay ikinasulat ang gutom ng isda``).
* IV 3-arg with PATIENT fronted
  (``Ng silya ay ipinaggawa ang kapatid ng nanay``).
* pa-OV-direct 3-arg with PATIENT fronted
  (``Ng kanin ay pinakain ng nanay ang bata``).
* Both inner NP orders (NOM-GEN and GEN-NOM after the V).
* Inner negation under fronting.

### Out-of-scope (still deferred)

* **DV 3-arg multi-GEN ay-fronting.** Blocked on Group D's "DV
  three-argument constructions" item — DV multi-GEN rules
  themselves don't yet exist. Lifts as a follow-on once that
  Group D commit lands.
* **3-arg multi-GEN ay-fronting under embedded control.**
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

* ``ADV`` — closed-class temporal adverbs. Seeded with four
  entries: ``kahapon`` "yesterday" (DEIXIS_TIME=PAST), ``ngayon``
  "now/today" (PRES), ``bukas`` "tomorrow" (FUT), ``mamaya``
  "later" (FUT). Each carries ``ADV_TYPE=TIME`` for grammar-rule
  matching.
* ``PREP`` — compound preposition heads that subcategorise for a
  sa-NP complement. Seeded with four entries: ``para``
  (PREP_TYPE=BENEFICIARY), ``tungkol`` (TOPIC), ``mula`` (SOURCE),
  ``dahil`` (REASON). Each PREP carries ``LEMMA`` (set
  automatically by the analyzer for ADV / PREP particles, mirroring
  the noun-LEMMA pattern from Phase 5c §8 follow-on Commit 6) so
  the head's lemma percolates through ``AdvP → ADV`` and
  ``PP → PREP NP[CASE=DAT]`` to the matrix TOPIC.

### Two new non-terminals

```
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

```
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

* Make the inner S the matrix's f-structure (``(↑) = ↓3``).
* Set the matrix's ``TOPIC`` to the fronted phrase.
* Add the fronted phrase to the matrix's ``ADJ`` set, preserving
  adjunct semantics alongside the topic-marking.

The inner S is a complete clause with no gap — AdvP / PP are
sentential modifiers, not arguments of any voice/aspect frame,
so there's nothing to extract from the inner clause's GF
inventory. This contrasts with the NP ay-fronting rules
(``S → NP[CASE=*] PART[LINK=AY] S_GAP_*``) which do require a
gap-category for the extracted argument.

### Why ADJ instead of ADJUNCT

Two non-governable set-valued attributes coexist in the f-structure:

* ``ADJUNCT`` holds DAT-NPs (sa-NPs) as collected by the parser's
  ``↓N ∈ (↑ ADJUNCT)`` equations. The Phase 5 LMT
  ``oblique_classifier`` post-processes this set into typed
  ``OBL-θ`` slots (LOC / RECIP / etc.).
* ``ADJ`` holds quantifier-floats (Phase 4 §7.8), 2P clitic
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

* ``Kahapon ay tumakbo si Maria`` — only the AdvP wrap rule
  matches (``kahapon`` as ADV); the NP-fronting rules require an
  NP, which a bare adverb without a DET cannot form.
* ``Para sa bata ay binili niya ang libro`` — both the PP wrap
  rule (``para`` as PREP heading a PP) and the DAT-NP wrap rule
  (``sa bata`` as a fronted DAT-NP, ignoring ``para``) could
  fire. The existing DAT-NP rule requires a single ``NP[CASE=DAT]``
  not preceded by anything; the surface has ``para sa bata``
  which contains an extra PREP token, so the DAT-NP-only rule
  doesn't extend across it. The PP wrap rule wins.

### What this lifts

* Temporal-AdvP ay-fronting:
  ``Kahapon ay tumakbo si Maria.``
  ``Ngayon ay kumakain ang bata.``
  ``Bukas ay tutulog si Maria.``
  ``Mamaya ay tutulog si Maria.``
* PP ay-fronting across all four seeded prepositions:
  ``Para sa bata ay binili niya ang libro.``
  ``Tungkol sa nanay ay sumulat ang bata.``
  ``Mula sa bahay ay tumakbo si Maria.``
  ``Dahil sa gutom ay kumain ang bata.``
* Inner-clause negation under both forms.
* Inner-clause transitive frames (AV and OV).

### Out-of-scope (still deferred)

* **Non-fronted AdvP / PP placement.** Clause-final or
  unmarked-sentential-adjunct placement of AdvP / PP
  (``Tumakbo si Maria kahapon``, ``Binili niya ang libro
  para sa bata``) — keeps AdvP / PP out of the matrix's
  post-V argument frames. Adding bare placement would interact
  with §7.3 Wackernagel-cluster placement and §7.8 quantifier-
  float and is left as a separate commit. The bare-AdvP /
  bare-PP usage is more frequent than the ay-fronted form, so
  this is a real gap; landing it as a separate commit keeps the
  scope reviewable.
* **Multi-word AdvPs.** ``kahapon ng umaga`` "yesterday morning"
  needs an ``AdvP → ADV NP[CASE=GEN]`` rule.
* **AdvP / PP modifying inner NPs.** ``ang aklat para sa bata``
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

* Both PRONs end up in distinct f-structure slots (different
  ``FStructure.id``s).
* The matrix-cluster PRON binds to the matrix V's appropriate
  role (matrix.OBJ in the synthesized AV-NVOL ``nakita`` case;
  matrix.SUBJ in AV-tr cases).
* The embedded RC-actor PRON binds inside the RC (the RC is an
  ADJ member of its head NP; the PRON fills the RC's
  OBJ-AGENT) — not at the matrix level.
* Negation under either the matrix or the RC composes
  independently.

### Identification by structural position, not LEMMA / PERS

Pronouns in Tagalog don't carry a grammar-visible LEMMA (the
analyzer doesn't add one for the PRON path), and PERS rides on
``feats`` as an integer which the pipeline's lex-equation
derivation drops (only string-valued feats become lex
equations). The two PRONs in a multi-pronoun RC are therefore
**indistinguishable at the f-structure level** beyond:

* Their structural position (matrix slot vs ADJ-RC slot).
* Their CASE / NUM features (which are string-valued and
  percolate).

Tests rely on structural position plus CASE / NUM. This is
sufficient for "composition pinning" but doesn't directly
distinguish 1sg vs 2sg vs 3sg. Adding string-valued PERS to the
analyzer is a small follow-up that would let downstream
consumers identify pronouns by person; out of scope for this
commit.

### What this lifts

Three matrix-PRON / RC-PRON orderings explicitly tested:

* ``Nakita ko ang batang kinain niya.`` (1sg + 3sg)
* ``Nakita mo ang batang kinain niya.`` (2sg + 3sg)
* ``Nakita niya ang batang kinain ko.`` (3sg + 1sg)

Plus AV-matrix variant
(``Kumain ako ng batang kinain niya.``) and inner-NEG
composition (``Nakita ko ang batang hindi kinain niya.``).

### Out-of-scope (still deferred)

* **3+ pronouns in a single sentence.** Matrix + RC1 + RC2 with
  three distinct PRONs (``Nakita ko ang batang kinain mo ng
  isdang nahuli niya``) — the recursion is structurally
  available but combinatorially explodes the parse forest;
  stress-test deferred until corpus pressure justifies.
* **PERS exposure as string-valued feat.** Would let tests and
  downstream consumers distinguish 1sg / 2sg / 3sg pronouns at
  the f-structure level. Trivial analyzer addition; deferred
  to a separate engineering follow-up.

