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

## Phase 5e Commit 5: headless / free relatives

**Date:** 2026-05-01. **Status:** active.

Phase 4 §7.5's "Out-of-scope" list flagged headless / free
relatives (``ang kumain`` "the one who ate") as deferred. A
headless RC is a relative clause used directly as an NP, with
no overt head noun — the "head" is interpreted as a
phonologically null PRO that's identified with the gap-filler
(REL-PRO).

### Three additive grammar rules

```
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

* AV-INTR-RC: ``Tumakbo ang tumakbo.``, ``Tumakbo ang natulog.``
* AV-tr-RC with overt OBJ: ``Tumakbo ang kumain ng isda.``,
  ``Kumain ang kumain ng isda.``
* OV-tr-RC (patient pivot): ``Tumakbo ang kinain ng aso.``
* Headless RC in non-SUBJ position:
  ``Nakita ko ang tumakbo.`` (OBJ-position headless RC).
* Inner negation under headless RC:
  ``Tumakbo ang hindi kumain ng isda.``

The construction composes with the existing Phase 4 §7.8 NP-
internal possessive (``ang kumain ng bata`` could mean either
"the one who ate the child" with `ng bata` as OBJ, OR "the
child's-eating(-thing)" with `ng bata` as POSS — both readings
are linguistically valid and both surface in n-best output).

### Out-of-scope (still deferred)

* **Headless RC with synthesized AV-intransitive verb.** Verbs
  with TR=TR but no hand-authored intransitive AV BASE entry
  (e.g., ``inom`` AV without overt OBJ) don't form a valid
  bare headless RC because completeness fails. A synthesizer
  enhancement that emits both ``<SUBJ>`` and ``<SUBJ, OBJ>``
  variants for TR-marked AV verbs would lift this; deferred
  as an engineering follow-up.
* **Headless RC modifying another NP.** ``ang aklat ng kumain``
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
exceptions where post-VERB / post-PRON ``na`` is the linker:

1. ``V[CTRL_CLASS!=NONE]`` directly preceding (Phase 5c §7.6
   follow-on Commit 3) — ``Gusto na kumain``.
2. PRON preceding, the PRON's prev being ``V[CTRL_CLASS!=NONE]``
   (Phase 4 §7.10) — ``Kaya namin na kumain``.

Phase 5e Commit 6 adds a third:

3. PRON preceding, the PRON's prev being NOUN (i.e., the PRON
   is an NP-internal possessor), AND the next content token
   after ``na`` is a VERB (or NEG + VERB).

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

* ``Tumakbo ang bata ko na kumain.`` "My child who ate ran."
* ``Tumakbo ang bata mo na kumain.`` (2sg-GEN possessor)
* ``Tumakbo ang bata niya na kumain.`` (3sg-GEN possessor)
* ``Tumakbo ang bata ko na kumain ng isda.`` (transitive RC).
* ``Tumakbo ang bata ko na kinain ng aso.`` (OV RC).
* ``Tumakbo ang bata ko na hindi kumain.`` (NEG-RC under
  the construction).

### Out-of-scope (still deferred)

* **Bare-AV-intr synthesizer fallback.** As above — needed to
  lift the original ``Tumakbo ang bata ko na nakita`` example
  where the RC's V is a TR verb without a hand-authored
  intransitive entry.
* **Other possessive markers + na linker.** ``aklat ng bata na
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

* Plan §10.1 Group B has a parenthetical noting the
  reclassification and a pointer to §10.2 / §18.
* Plan §10.2 ("Items not enumerated above") gains the
  resumptive item alongside the other genuinely-out-of-scope
  Phase 5e items (unbounded control chains, 3+ sa-NPs,
  non-restrictive RCs).
* Plan §18 gains a new bullet articulating the why.
* This `docs/analysis-choices.md` section pins the rationale
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

* **Control under raising** — a raising matrix embedding a
  control clause as its non-gap S complement. The Phase 5c §7.6
  Commit 5 raising rule
  ``S → V[CTRL_CLASS=RAISING] PART[LINK] S`` admits any
  complete S as the inner clause, including a control-S.
* **TRANS control + raising** — a TRANS control verb
  (``pinilit``) whose XCOMP is itself a raising-S_XCOMP. The
  Phase 5d Commit 7 ``S_XCOMP``-level raising rules made this
  composition available; this commit pins it.

### Composition shapes

**Control under raising:**

```
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

```
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

* Control under linked raising (mukha / baka):
  ``Mukhang gusto ng batang kumain.``,
  ``Bakang gusto ng batang kumain.``,
  ``Mukhang pumayag ang batang kumain.``
* Control under bare raising (parang / tila):
  ``Parang gusto ng batang kumain.``,
  ``Tila gusto ng batang kumain.``
* TRANS control + raising in XCOMP:
  ``Pinilit ng nanay ang batang mukhang umuwi.``,
  ``Pinilit ng nanay ang batang parang umuwi.``
* Negation at the middle level
  (``Mukhang hindi gusto ng batang kumain``) and at the
  innermost level
  (``Mukhang gusto ng batang hindi kumain``).

### Out-of-scope (still deferred)

* **Psych control over a raising-S at the S level**
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

* **Nested pa-causatives under control.** Phase 5c §7.6 Commit
  3 added nested-S_XCOMP rules — a control verb's XCOMP is
  itself another control verb whose XCOMP is the action.
  Phase 5d Commit 8 added pa-OV (CAUS=DIRECT) S_XCOMP rules
  (the embedded actor's typed slot is ``OBJ-CAUSER``). Stacked,
  they produce 3-level controller chains where the innermost
  is a pa-OV.
* **IV multi-GEN under nested control.** Phase 5d Commit 9
  added 3-arg IV S_XCOMP rules (gap = OBJ-AGENT,
  retained = OBJ-PATIENT). When stacked under the Commit 3
  nested-control infrastructure, the controller chains to the
  embedded ``OBJ-AGENT`` while ``OBJ-PATIENT`` stays overt as a
  GEN-NP.

### Composition shapes

**Nested pa-OV under control** (3 levels, gap routes to
OBJ-CAUSER):

```
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

```
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

* **Pa-DV under nested control.** Phase 5d Commit 2 introduced
  pa-DV (``pa-...-an``) at S level, and Phase 5d Commit 8 added
  pa-DV under single-level control. Pa-DV under *nested* control
  (e.g., ``Gusto kong pumayag na pakakainan ang bata``) should
  compose via the existing rules but isn't pinned here. Adding
  it would mirror the pa-OV pattern.
* **3-arg pa-DV** — separate Phase 5e Commit 10 item.
  Currently the lex profile is 2-arg only, so 3-arg pa-DV under
  nested control is doubly blocked.
* **4+ levels of nesting.** Phase 5c Commit 3 covers 4 levels;
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

```
CAUSE-EAT-AT   <SUBJ, OBJ-CAUSER, OBJ-PATIENT>   kain DV CAUS=DIRECT
CAUSE-READ-AT  <SUBJ, OBJ-CAUSER, OBJ-PATIENT>   basa DV CAUS=DIRECT
CAUSE-DRINK-AT <SUBJ, OBJ-CAUSER, OBJ-PATIENT>   inom DV CAUS=DIRECT
```

Both 2-arg and 3-arg entries coexist for each verb; lex lookup
chooses based on NP count.

### New top-level multi-GEN-NP pa-DV grammar rules

Three permutations parallel to the Phase 5b multi-GEN-NP pa-OV
rules:

```
S → V[VOICE=DV, CAUS=DIRECT] NP[CASE=NOM] NP[CASE=GEN] NP[CASE=GEN]
   ↳ SUBJ=NOM (LOCATION), OBJ-CAUSER=1st GEN, OBJ-PATIENT=2nd GEN
S → V[VOICE=DV, CAUS=DIRECT] NP[CASE=GEN] NP[CASE=NOM] NP[CASE=GEN]
S → V[VOICE=DV, CAUS=DIRECT] NP[CASE=GEN] NP[CASE=GEN] NP[CASE=NOM]
```

The first ng-NP is CAUSER (the agentive instigator), the second
is PATIENT, per the Phase 5b positional convention.

### S_XCOMP additions for 3-arg pa-DV under control

```
S_XCOMP → V[VOICE=DV, CAUS=DIRECT] NP[CASE=NOM] NP[CASE=GEN]
   ↳ SUBJ=NOM, OBJ-PATIENT=GEN, OBJ-CAUSER=REL-PRO (gap)
S_XCOMP → V[VOICE=DV, CAUS=DIRECT] NP[CASE=GEN] NP[CASE=NOM]
```

Mirrors the pa-OV variants in Phase 5d Commit 8.

### S_GAP_OBJ_CAUSER and S_GAP_OBJ_PATIENT additions for ay-fronting

* ``S_GAP_OBJ_CAUSER`` gains 3-arg pa-DV variants (NOM-GEN /
  GEN-NOM with retained OBJ-PATIENT) — lifts the deferral
  flagged in Phase 5e Commit 1.
* ``S_GAP_OBJ_PATIENT``'s ``patient_gap_specs`` gains
  ``("V[VOICE=DV, CAUS=DIRECT]", "OBJ-CAUSER")`` — lets pa-DV
  3-arg PATIENT-fronting use the same gap-category as IV /
  pa-OV.

### Sentences enabled

* Top-level 3-arg pa-DV across all three NP-order permutations:
  ``Pinakainan ng nanay ng kanin ang bata.`` "Mother fed rice
  to the child."
* 3-arg pa-DV under control:
  ``Gusto kong pakakainan ang bata ng kanin.`` "I want to feed
  rice to the child."
* 3-arg pa-DV ay-fronting (CAUSER-fronted, PATIENT retained):
  ``Ng nanay ay pinakainan ang bata ng kanin.``
* 3-arg pa-DV ay-fronting (PATIENT-fronted, CAUSER retained):
  ``Ng kanin ay pinakainan ng nanay ang bata.``

### Composition with embedded control

Single-level pa-DV under control works (PSYCH and INTRANS
classes). Nested pa-DV under control composes via the same
Phase 5c §7.6 Commit 3 nested-S_XCOMP rules that pa-OV uses,
though it isn't separately pinned with tests in this commit.

### Out-of-scope (still deferred)

* **Nested 3-arg pa-DV under multi-level control** — like the
  pa-OV nested cases pinned in Phase 5e Commit 9, but with
  3-arg pa-DV innermost. Should compose; not pinned.
* **Other less-common DV causative variants** (``ka-...-an``
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

```
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

```
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

* ``Sinulatan ng nanay ng liham ang anak.`` (GEN-GEN-NOM)
* ``Sinulatan ang anak ng nanay ng liham.`` (NOM-GEN-GEN)
* ``Sinulatan ng nanay ang anak ng liham.`` (GEN-NOM-GEN)
* IPFV aspect (``Sinusulatan ng nanay ng liham ang anak``)
* Negation under matrix (``Hindi sinulatan ng nanay ng liham
  ang anak``)

### Coexistence with the 2-arg reading

When the surface includes the GEN-GEN cluster, the parser
admits both the 3-arg reading (with overt OBJ-PATIENT) and a
2-arg reading where ``ng nanay ng liham`` is parsed as a
possessive ``mother's letter`` filling OBJ-AGENT. Both are
linguistically valid; the n-best list contains both. Tests
assert the 3-arg reading is among the parses.

### Out-of-scope (still deferred)

* **Plain DV 3-arg under control / ay-fronting.** The
  multi-arg-under-control patterns from Phase 5e Commits 9 and
  10 don't yet have plain-DV variants. Adding them mirrors the
  pa-OV / pa-DV approach.
* **3-arg plain DV for other anchor verbs.** Lex-only
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

* ``Nagkainan sila.`` "They ate together."
* ``Nagkakainan sila.`` IPFV.
* ``Magkakainan sila.`` CTPL.
* ``Nagbilihan sila.`` "They exchanged in trade."

### Implementation

**New affix class ``mag_an``** with three paradigm cells in
``data/tgl/paradigms.yaml``. Each cell carries
``feats: {MOOD: SOC, RECP: YES}``:

```
PFV:  prefix("nag")  → suffix("an")            → nagkainan
IPFV: cv_redup → prefix("nag")  → suffix("an") → nagkakainan
CTPL: cv_redup → prefix("mag")  → suffix("an") → magkakainan
```

**Lex entries** for ``kain`` and ``bili`` reciprocal:

```
EAT-TOGETHER  <SUBJ>   kain  AV MOOD=SOC
BUY-EXCHANGE  <SUBJ>   bili  AV MOOD=SOC
```

**Affix-class registration**: ``mag_an`` added to ``kain``'s
and ``bili``'s ``affix_class`` lists in ``data/tgl/roots.yaml``.

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

* **Reciprocal with overt NP arguments.**
  ``Nagkainan sila ng isda`` "They ate fish together" admits
  the reciprocal SUBJ + an OBJ. The current lex profile is
  intransitive; transitive reciprocal (with a GEN-NP OBJ)
  would need a 2-arg lex profile.
* **Reciprocal under control / ay-fronting / nesting.** The
  reciprocal interacts with the existing control / fronting
  infrastructure but isn't pinned in this commit.
* **Other reciprocal anchor verbs.** Currently only ``kain``
  and ``bili``. ``basa`` reciprocal (``nagbasahan`` "read
  together / read at each other") would be a one-line
  addition.
* **`ka-...-an` re-classification.** The plan §10.1 Group D
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

* **S&O 1972 §5.27** documents the Tagalog reciprocal as
  ``mag-...-an``; the distributive (the marker for "everyone
  / each one does X") is the existing ``mang-`` AV prefix
  (Ramos 1971 dictionary classifies it as AV-distributive in
  every paradigm table) and the ``magsi-`` collective form
  (less productive; S&O 1972 §5.27).
* **Ramos 1971 dictionary** organises every voice's paradigm
  as Indicative + Distributive, with the Distributive column
  always labelled ``MANG-`` — never ``magpa-...-an``.
* **R&B 1986 paradigm tables** mention the productive forms
  for each verb's affix-class membership; ``magpa-...-an``
  doesn't appear as a separate paradigm row.

The plan note appears to have been written by analogy with
the ``pa-...-in`` / ``pa-...-an`` causative pair without
external attestation. Tagalog distributive is a separable
construction from causative, marked by ``mang-`` (productive)
or ``magsi-`` (collective).

### Where Tagalog distributive lives now

* **``mang-``**: already implemented as the ``mang`` affix
  class (Phase 2C scale-up; documented in Phase 4 §7.7's
  applicative work). ``namili`` "shopped / went buying";
  ``namamasyal`` "stroll around". The morph analyzer
  generates these correctly via the existing ``nasal_substitute``
  sandhi op.
* **``magsi-``**: attested in S&O 1972 §5.27 but not
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

* Plan §10.1 Group D's ``magpa-...-an`` bullet is collapsed
  into a single re-classification note alongside the
  Commit 12 ``ka-...-an`` retraction.
* Plan §10.2 ("Items not enumerated above") gains the
  ``magpa-...-an`` bullet alongside the other reclassified
  items (resumptive pronouns, etc.).
* Plan §18 gains a ``magpa-...-an`` bullet with the why.
* This `docs/analysis-choices.md` section pins the rationale.
* `docs/coverage.md` "What's intentionally not covered" gains
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

```
drop:   mang- + bili → mami → mamili / namili / namimili / mamimili
retain: mang- + bili → namb → nambili / nambibili / mambibili
                                                   (no “mambili” form;
                                                    cv-redup is required
                                                    for IPFV / CTPL)
```

### Three new paradigm cells

In ``data/tgl/paradigms.yaml``, a new ``mang_retain`` affix
class with PFV / IPFV / CTPL cells:

```
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
``affix_class`` list (``data/tgl/roots.yaml``); other roots
that admit the retain pattern (e.g., ``tahi``, ``patay``) can
opt in by adding ``mang_retain`` to their list. Roots without
the flag don't generate retain-pattern surfaces:

```
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

* **Other retain-pattern bases.** Currently only ``bili``.
  Other roots historically attested with retain-pattern
  variants (``tahi`` → ``nantahi``, ``patay`` → ``namatay``)
  could opt in via affix-class registration; not pursued here.
* **Per-form aspectual feats.** If corpus pressure reveals a
  systematic semantic contrast between drop and retain
  surfaces, a feature like ``MANG_PATTERN=DROP|RETAIN`` could
  ride on the morph analysis and route to distinct lex PREDs.
* **Retain pattern under control / ay-fronting.** The retain
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
   ``pambili`` etc. as nouns in ``data/tgl/roots.yaml``.
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

* **Lex-only path** (when corpus pressure surfaces tokens):
  add each form as a NOUN entry in ``data/tgl/roots.yaml``,
  e.g., ``- citation: pambili, pos: NOUN, gloss: shopping
  money / for buying``. The existing N rules and NP-formation
  rules absorb them.
* **Productive-derivation path** (more ambitious): a new
  ``pang_n`` morphological class deriving NOUN from VERB
  roots, parallel to (but distinct from) the verbal
  ``ipang`` / ``mang_retain`` classes. This requires deciding
  the derived-noun's lex profile: PRED, SEM_CLASS, possible
  argument-frame inheritance from the source verb, etc.

Both paths are deferred to v1+ when corpus pressure justifies.

### Where it lives now

* Plan §10.1 Group D parenthetical noting the reclassification
  and pointer to §10.2 / §18.
* Plan §10.2 ("Items not enumerated above") gains the
  ``pang-``-purpose-nominals item (sixth item; the plan now
  flags this re-categorisation explicitly).
* Plan §18 gains a bullet articulating the rationale and the
  two implementation paths.
* This `docs/analysis-choices.md` section pins the rationale.

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

```
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

```
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

* prev=NOUN/N → linker (already in place);
* prev=VERB/PRON → clitic (with three sub-exceptions);
* otherwise → keep both readings (placement decides).

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

```
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

* **Demonstrative as modifier of a relativized head**
  (``ang batang ito na kumain`` "this child who ate"). The
  RC's linker would compete with the dem-modifier's linker;
  needs ranker-policy refinement. Phase 5e Commit 17.
* **Pre-modifier dem with N-internal modifiers between dem and
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

```
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

```
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

* **Pre-modifier dem on a relativized head**
  (``itong batang kumain`` "this child who ate"). Already
  works via the Phase 5e Commit 16 pre-mod-dem rule + Phase 4
  §7.5 RC rule — pinned by a regression test in this commit.
  Not a new construction; included as a regression check.
* **Dem on a relativized head where the RC itself contains a
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

```
aklat namin na binasa     "the book that we (excl) read"
aklat natin na binasa     "the book that we (incl) read"
aklat ninyo na binasa     "the book that you (pl) read"
aklat nila na binasa      "the book that they read"
```

The vowel-final pronouns also admit the standalone-``na``
form alongside the fused ``-ng`` form:

```
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
in the wrap-rule loop in ``src/tgllfg/cfg/grammar.py``:

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
   + PRON + linker + ``S_GAP_NA``). The PRON token is part of
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

```
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

* **OV** — ``binasa`` / ``kinain`` (most common; the canonical
  patient-pivot case where the actor is extracted as POSS).
* **DV** — ``binasahan`` (DV PFV of ``basa`` is the only DV
  form with full analyzer coverage in the seed lexicon; other
  DV PFVs like ``binigyan`` / ``binilhan`` / ``kinanan`` are
  ``_UNK`` to the morph analyzer and would parse only after a
  paradigm-cell expansion).
* **IV** — ``ipinaggawa`` (BEN bare), ``ipinagsulat`` (BEN
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

```
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

```
'Tumakbo ang bata ko na kinain ng aso.'   3 parses → 2 parses
'Tumakbo ang bata kong kinain ng aso.'    3 parses → 2 parses
```

The 2 remaining parses are the intended one (POSS=PRON,
OBJ-AGENT=NOUN, distinct fstructs) and a separate analysis
where the RC's actor is gapped differently — both linguistically
sensible. Pinned by ``TestPossessiveExtractedGuard`` in the
Commit 18 test file.

### Lifted in Phase 5e Commit 19

* **Non-pronominal possessors with linker** (``aklat ng batang
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

```
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

```
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

* **Pronominal cases** (Commit 6 / Commit 18) — unchanged. Pinned
  by ``test_pronominal_commit_6_still_works`` and
  ``test_pronominal_commit_18_still_works``.
* **Standard NP-poss + standard relativization** (``libro na
  binasa ng bata``) — unchanged. The wrap rule requires
  ``PART[LINK=L] + S_GAP_NA``, which doesn't fit a surface where
  the actor stays inside the RC; the standard ``S_GAP`` path is
  used instead. Pinned by
  ``test_standard_relativization_with_overt_actor``.
* **Right-associative iterated possessives** (``libro ng bata ng
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
``data/tgl/roots.yaml`` (``kita`` = "see, meet"), but the verb
is never used as a bare lemma — it always appears with affixes
(``kumita`` AV, ``kinita`` OV, ``nakita`` NVOL). The morph
analyzer returns the PRON analysis for bare ``kita``, and the
chart parser can also use the verb analysis for affixed forms;
no ambiguity in practice.

### Grammar layer

``src/tgllfg/cfg/grammar.py`` adds a per-voice loop that mirrors
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

```
(↑ SUBJ PERS)             = '2'
(↑ SUBJ NUM)              = 'SG'
(↑ SUBJ CASE)             = 'NOM'
(↑ <obj_target> PERS)     = '1'
(↑ <obj_target> NUM)      = 'SG'
(↑ <obj_target> CASE)     = 'GEN'
```

The ``<obj_target>`` per voice spec routes the 1sg actor to the
right typed slot:

* OV / DV with ``CAUS=NONE`` → ``OBJ-AGENT`` (plain non-AV
  transitive).
* OV / DV with ``CAUS=DIRECT`` → ``OBJ-CAUSER`` (pa-causatives;
  the 1sg actor is the CAUSER, not the AGENT).
* IV (any APPL) → ``OBJ-AGENT``.

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

```
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

* **OV-NVOL of ``kita`` (``Nakita kita`` "I saw you")** — the
  canonical example in grammar texts. The current ma-class
  paradigm only emits AV-NVOL forms; ``nakita`` analyses as
  AV-NVOL only. Adding OV-NVOL ma-class cells is a paradigm
  coverage follow-up, not a grammar / kita-fusion limitation.
  Tracked as a TBD alongside the DV PFV gap from Phase 5e
  Commit 18 (see plan §18 entries "DV PFV paradigm coverage
  gap" — analogous form needed for OV-NVOL).
* **PERS feature not propagated through standard PRON entries.**
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

```
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

* ``S → V[VOICE=AV] NP[CASE=NOM]`` (intransitive AV)
* ``S → V[VOICE=AV] NP[CASE=NOM] NP[CASE=GEN]`` (transitive AV
  via the standard ``voice_specs`` loop)
* ``S → V[VOICE=AV] NP[CASE=NOM] NP[CASE=DAT]`` (intransitive
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

* **SOC negation with ``huwag``** (``Huwag tayong magkape``
  "Let's not have coffee"). The interaction between ``huwag``'s
  IMP particle and the SOC mood requires the Group G item 3
  huwag-MOOD lift to be in place first. Tracked as a TBD.
* **IMP variant** (``Magkape ka`` "Have coffee!"). Same surface
  form, but PRON SUBJ is 2nd-person. Needs PERS-aware grammar
  rules; see the PERS-filtering note in Commit 20's docs.
* **Other denominal mag-NOUN verbs** (``magtanim`` "plant",
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

* Not a clitic (PRON-clitic or PART-2P-clitic).
* Not ``PART[POLARITY=NEG]`` (``hindi``, ``huwag``).
* Not punctuation.

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

* **Adjective predicates** — ``Maganda ka.`` "You're
  beautiful" (the predicate-adj construction is Phase 5g; the
  placement-pass change here covers the cluster shape so it's
  ready when 5g lands).
* **Noun predicates** — ``Bata ka.`` "You're a child"
  (equational with NOUN predicate).
* **Locative predicates** — ``Dito ka.`` "You're here" (ADP
  locative dem as predicate).
* **PP / quantifier predicates** — also covered.

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

```
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
+ redup. On investigation against the *Handbook of Tagalog
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

```
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

```
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

```
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

* **IV-REASON CTPL paradigm gap** (CTPL form ``ikakain``
  analyses as IV-CONVEY rather than IV-REASON; Phase 5d
  Commit 9 deferral). Coming in Commit 24.
* **`huwag`'s MOOD=IMP lifted to matrix** (Phase 4 §7.2
  limitation). Coming in Commit 25.

## Phase 5e Commit 24: IV-REASON CTPL short-form paradigm gap

**Date:** 2026-05-02. **Status:** active. Lifts the Phase 5d
Commit 9 paradigm-gap deferral. Before this commit, the surface
``ikakain`` had only an IV-CONVEY CTPL reading; Tagalog
actually admits both IV-CONVEY and IV-REASON CTPL on this
surface, with IV-REASON being a "short" form of the longer
``ikakakain``.

### Evidence from the Handbook of Tagalog Verbs

The Handbook (Ramos & Schachter; ``data/tgl/dictionaries/``)
lists Reason Focus (RF) Cont with two surface variants
separated by ``/`` for vowel-initial roots:

```
ingay (noise):  RF Cont. ikakaingay / ikaiingay   (line 4120 in OCR)
init (heat):    RF Cont. ikakainit  / ikaiinit    (line 4161 in OCR)
```

The first variant has an extra CV-redup; the second drops it.
The pattern generalizes to consonant-initial bases — for
``kain``, the "long" form is ``ikakakain`` (i + ka + cv-redup
+ kain = 4 syllables), the "short" form is ``ikakain`` (i + ka
+ kain, no further redup = 3 syllables).

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

```
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

```
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

* ``MOOD`` (existing) — the verb's morphological mood. IND
  (default for indicative verb forms), ABIL (maka-
  abilitative), NVOL (ma- non-volitional), SOC (Phase 5e
  Commit 21 hortative and Phase 5e Commit 12 reciprocal).
  Always projected from the verb's lex equations.
* ``CLAUSE-MOOD`` (new) — the sentential / speech-act mood.
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

```
Huwag kumain ang bata.        → CLAUSE-MOOD=IMP, POLARITY=NEG, MOOD=IND
Huwag kumain ng isda ang bata.→ CLAUSE-MOOD=IMP, POLARITY=NEG, MOOD=IND
Huwag pa kumain ang bata.     → CLAUSE-MOOD=IMP + adv enclitic (`pa` YET)
Hindi kumain ang bata.        → POLARITY=NEG, MOOD=IND, no CLAUSE-MOOD (unchanged)
Kumain ang bata.              → MOOD=IND, no POLARITY/CLAUSE-MOOD (unchanged)
```

### Out-of-scope (deferred)

* **The control-style imperative** ``Huwag kang kumain.`` (with
  addressee + linker + verb). This is the canonical surface
  for direct imperatives ("Don't (you sg) eat") but requires
  a different wrap rule shape — analogous to a control verb
  taking SUBJ + linker + S_XCOMP. Phase 5e Commit 25 only
  covers the matrix-NEG style ``Huwag kumain ang bata.``;
  the PRON-LINK form is deferred to a separate commit (or
  Phase 5g+ when adjective predication and verbless clause
  shapes mature).
* **Lifting hindi to CLAUSE-MOOD=DECL.** We intentionally
  leave CLAUSE-MOOD unset for declaratives. Adding
  CLAUSE-MOOD=DECL to every clause would be ceremony with no
  current consumer. If a future commit needs to distinguish
  declarative from interrogative or other speech-act moods,
  this is a one-line addition.
* **The huwag clitic interaction with SOC** (``Huwag tayong
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

```
PRED  = 'LIKE <SUBJ, OBJ>'
SUBJ  = the comparee (the ang-NP)
OBJ   = the standard (the bare N)
```

For ``Parang aso ang bata.``:

```
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

* **Negation**: ``Hindi parang aso ang bata.`` — POLARITY=NEG
  is overlaid on the matrix via the standard NEG rule.
* **Relativization on SUBJ**: ``Parang aso ang batang
  kumain.`` — the SUBJ NP can carry an internal RC.

### Out-of-scope (deferred)

* **Adjective-modified standard**: ``Parang asong matalino
  ang bata.`` "The child is like a smart dog." — needs the
  Phase 5g adjective machinery for ``asong matalino``. Not
  parsed here.
* **Determiner-marked standard**: ``Parang ang aso ang
  bata.`` — non-standard surface; the standard form uses bare
  N.
* **Comparative + clause as standard**: ``Parang umiiyak ang
  bata.`` "The child is like (someone who is) crying." This
  is captured by the existing evidential reading
  (``parang + clause``); whether comparative-vs-evidential is
  a separable distinction with overt clauses is a deeper
  semantic question deferred to v1+ pragmatic analysis.
* **``kasing-`` / ``sing-`` equative comparatives**
  (``kasingganda ng aso``). Phase 5h coverage (comparison &
  degree) per plan §12.2.
* **``mas`` / ``pinaka-`` comparatives** (``mas matalino``,
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

* Vowel-final (use bound ``-ng`` linker via ``split_linker_ng``):
  ``isa`` (1, NUM=SG), ``dalawa`` (2), ``tatlo`` (3), ``lima`` (5),
  ``pito`` (7), ``walo`` (8), ``sampu`` (10).
* Consonant-final (use standalone ``na`` linker): ``apat`` (4),
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

* **NP-level cardinal rules** (6 = 3 cases × 2 linker variants).
  Schema:

  ```
  NP[CASE=X] → DET/ADP[CASE=X] NUM[CARDINAL=YES] PART[LINK=Y] N
  ```

  Equations: case marker shares with NP via ``(↑) = ↓1``
  (CASE/MARKER); head N's PRED + LEMMA percolate; cardinal's NUM
  and CARDINAL_VALUE land on matrix NP. Chained cardinals
  blocked at NP level by ``¬ (↓4 CARDINAL_VALUE)``: the head-N
  daughter cannot itself carry a CARDINAL_VALUE.

* **N-level cardinal rule** (2 = 1 × 2 linker variants):

  ```
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

* ``*Kumain ako ng isa bata.`` — missing linker between cardinal
  and N. No rule consumes the ``isa bata`` sequence as an N or
  NP because the cardinal-NP-modifier rule requires a
  ``PART[LINK=Y]`` middle daughter.
* ``*Kumain ako ng tatlong dalawang bata.`` — chained cardinals.
  Blocked by ``¬ (↓4 CARDINAL_VALUE)`` on NP-level rule and
  ``¬ (↓3 CARDINAL_VALUE)`` on N-level rule.

### Out of scope for this commit

* Spanish-borrowed cardinals (``uno``, ``dos``, ``tres``, ...) —
  Group A item 2.
* Compound cardinals (``labing-isa`` 11, ``dalawampu`` 20, ...) —
  Group A item 3.
* Predicative cardinals (``Tatlo ang anak ko``) — Group A item 4
  (consumes the N-level rule added here).
* Multiplicative ratios (``maka-`` + cardinal, ``[CARDINAL]ng
  beses``) — Group A item 5.
* Decimals + percentages — Group A items 6-7.
* Cardinal + dem composition (``itong tatlong bata``) — would
  need either a dem rule extension or an NP-internal cardinal
  modifier inside the dem-headed NP. Not in this commit.

## Phase 5f Commit 2: Spanish-borrowed cardinals 1-10

**Date:** 2026-05-03. **Status:** active. Lex-only addition;
no grammar changes. Refs: plan §11.1 Group A item 2;
Phase 5f Commit 1 (rule infrastructure).

### Lex change

10 entries added to ``data/tgl/particles.yaml`` parallel to
the native-cardinal block from Commit 1:

* Vowel-final (bound ``-ng`` linker): ``uno`` (1, NUM=SG),
  ``kuwatro`` (4), ``singko`` (5), ``siyete`` (7), ``otso``
  (8), ``nuwebe`` (9).
* Consonant-final (standalone ``na`` linker): ``dos`` (2),
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

* Compound Spanish cardinals (``onse`` 11, ``dose`` 12, ...,
  ``sentimo`` per cents in price expressions, etc.) — Group A
  item 3 (compound cardinals).
* Spanish ordinal forms (``primer``, ``segundo``, ...) — these
  surface in fixed expressions (months, kings, etc.) but are
  not productive in modern Tagalog; out of scope (§18).
* Register-marking on the parsed f-structure (no
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

* **Teens (11-19)** — ``labing-`` prefix + 1-9 base with sandhi:
  ``labingisa`` (11), ``labindalawa`` (12), ``labintatlo`` (13),
  ``labingapat`` (14), ``labinlima`` (15), ``labinganim`` (16),
  ``labimpito`` (17), ``labingwalo`` (18), ``labinsiyam`` (19).
* **Decades (20-90)** — base + ``-pu`` / ``-mpu`` / ``na pu``
  with sandhi: ``dalawampu`` (20), ``tatlumpu`` (30),
  ``apatnapu`` (40), ``limampu`` (50), ``animnapu`` (60),
  ``pitumpu`` (70), ``walumpu`` (80), ``siyamnapu`` (90).
* **Hundreds and thousands**: ``sandaan`` (100), ``sanlibo``
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

* The high-frequency compounds (11-19, 20, 30, 40, 50, 60, 70,
  80, 90, 100, 1000) cover the bulk of real-world usage in
  prices, ages, dates, recipe quantities, and clock times.
* The productive morphology has irregular sandhi (``-mpu``
  after vowel-final 1-9 → ``dalawampu`` from ``dalawa``;
  ``na pu`` after consonant-final 4 / 6 / 9 → ``apatnapu``,
  ``animnapu``, ``siyamnapu``) and an irregular vowel mutation
  (``tatlo`` → ``tatlumpu``, ``pito`` → ``pitumpu``, ``walo``
  → ``walumpu``). Encoding these productively requires a small
  morph class and sandhi rules — useful but not required for
  v1 reference-grammar coverage.
* Higher compound numerals (101-999, 1001-9999, etc.) require
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

* Hyphenated forms (``labing-isa``) tokenize as 3 tokens
  (``labing``, ``-``, ``isa``) — would need a tokenizer
  pre-pass to merge.
* Multi-word forms (``apat na pu``) tokenize as 3 tokens
  and would need NUM-internal grammar rules to compose
  (with productive value calculation: 4 × 10 = 40).

Both are interesting follow-ons but neither is needed to cover
high-frequency v1 compound numerals.

### Out of scope for this commit

* Productive ``labing-`` and ``-pu`` morph paradigms (would
  cover any base 1-9 systematically; useful for testing /
  generation but redundant with the hand-authored lex for
  parsing).
* Hyphenated and multi-word compound variants
  (``labing-isa``, ``apat na pu``).
* Higher compound numerals (101-999, 1001+) requiring
  coordination — deferred to Phase 5k cardinal-coordination
  follow-on.
* Group A item 4 (predicative cardinals) — next commit;
  consumes both simple and compound cardinals via the
  N-level rule already in place.

## Phase 5f Commit 4: predicative cardinal

**Date:** 2026-05-03. **Status:** active. One new S rule;
no lex changes (cardinals from Commits 1-3 are reused). Refs:
plan §11.1 Group A item 4; Phase 5e Commit 26 (parang —
parallel predicative S rule shape); Phase 5d Commit 1
(evidential parang).

### Grammar change

```
S → NUM[CARDINAL=YES] NP[CASE=NOM]
Equations:
  (↑ PRED) = 'CARDINAL <SUBJ>'
  (↑ SUBJ) = ↓2
  (↑ CARDINAL_VALUE) = ↓1 CARDINAL_VALUE
  (↑ NUM) = ↓1 NUM
```

The cardinal serves as the matrix predicate; the NOM-NP is the
pivot. F-structure shape:

* PRED            = 'CARDINAL <SUBJ>' (literal)
* CARDINAL_VALUE  = the count from the cardinal
* NUM             = SG (only ``isa`` / ``uno``) or PL (rest)
* SUBJ            = the NOM-NP pivot

The PRED template ``CARDINAL <SUBJ>`` parallels the literal
PRED conventions of the existing predicative S rules
(``LIKE <SUBJ, OBJ>`` for comparative parang; ``SEEM <SUBJ>``
for evidential parang). No VOICE / ASPECT / MOOD: a numeric
predicate isn't a verb and doesn't carry verbal morphology.

### Why NUM-headed S, not NUM-as-V

The plan (§11.1 Group A item 4) offers two analytical paths:
"a NUM-as-V analysis or a small NUM-headed S rule." This
commit takes the **NUM-headed S** path because:

* Cardinals are not verbs — they don't inflect for voice,
  aspect, or mood. Forcing them through a VERB-typed analysis
  would require either duplicate VERB lex entries (clunky) or
  a special VOICE / ASPECT / MOOD = NULL discipline (complex
  and a mismatch with the existing verbal pipeline).
* A single new S rule is the minimal change. It composes
  trivially with the matrix negation rule (``Hindi tatlo ang
  anak ko``) and the verbless clitic-placement pass (Phase 5e
  Commit 22 — NUM qualifies as a content-word anchor for
  PRON-clitic SUBJ pivots like ``sila``, ``kami``, ``tayo``).
* The single rule consumes simple (Commit 1), Spanish-borrowed
  (Commit 2), and compound (Commit 3) cardinals — all match
  ``NUM[CARDINAL=YES]``.

### Composition

Tested compositions:

* PRON-clitic SUBJ: ``Dalawa sila``, ``Lima kami``, ``Tatlo
  tayo``. The verbless clitic pass (Phase 5e Commit 22) treats
  NUM as the content anchor; the PRON-clitic falls into the
  post-anchor cluster (which is its surface position anyway —
  no movement).
* Full NOM-NP SUBJ: ``Tatlo ang anak ko`` (with possessor),
  ``Lima ang isda``, ``Isa ang bata`` (NUM=SG case).
* All cardinal classes: simple (``Lima ang isda``), Spanish
  (``Dos sila``, ``Singko ang isda``), compound (``Dalawampu
  ang bata``, ``Sandaan ang aklat``, ``Sanlibo ang isda``).
* NEG: ``Hindi tatlo ang anak ko`` "I don't have three
  children" — the Phase 4 §7.4 matrix-NEG rule prepends
  ``hindi`` to any matrix S; predicative-cardinal S is no
  exception.

### Negative fixtures

Per Phase 5f §11.2 negative-fixture convention:

* ``*Tatlo.`` standalone — predicative cardinal needs a SUBJ;
  the rule requires NP[CASE=NOM] as the second daughter.
* ``*Tatlo ng anak ko.`` — wrong case. Predicative cardinal
  requires NOM-NP, not GEN-NP. The rule's second daughter
  pattern is ``NP[CASE=NOM]``, not ``NP[CASE=GEN]``.

## Phase 5f Commit 5: multiplicative ratios

**Date:** 2026-05-03. **Status:** active. Lex (NOUN + ADV)
plus one new grammar rule. Refs: plan §11.1 Group A item 5;
S&O 1972 §4.5; Phase 5e Commit 3 (AdvP deferral that this
commit partially closes).

### Lex change

* **Frequency NOUNs** (``data/tgl/roots.yaml``):
  ``beses`` and ``ulit`` (both with ``SEM_CLASS: FREQUENCY``;
  bidirectional synonyms). Used in periphrastic frequency
  expressions (``dalawang beses`` "twice", ``tatlong ulit``
  "three times") via the existing Phase 5f Commit 1
  cardinal-NP-modifier rule on the head N.
* **Multiplier NOUNs**: ``doble`` and ``triple`` (both with
  ``SEM_CLASS: MULTIPLIER``). Spanish-borrowed; lex-only —
  surface in technical / commercial register.
* **maka-cardinal ADVs** (``data/tgl/particles.yaml``): 10
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

One new rule (``src/tgllfg/cfg/grammar.py``):

```
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

* ``Tumakbo ako dalawang beses.`` — bare frequency-N
  clause-final.
* ``Dalawang beses akong tumakbo.`` — frequency-N
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

* maka- frequency adverb in clause-final position:
  ``Kumain ako makalawa``, ``Tumakbo siya makasampu``.
* maka- with full NOM-NP SUBJ: ``Kumain ang bata makatlo``.
* maka- with NEG: ``Hindi tumakbo si Juan makalawa``.
* maka- recursive (S → S AdvP fires on its own output):
  ``Tumakbo ako makalawa makatlo`` parses (semantically
  odd but syntactically allowed; not blocked).

### Negative fixtures

Per Phase 5f §11.2 negative-fixture convention:

* ``*Tumakbo ako kahapon.`` — TIME adverbs (kahapon —
  ``ADV_TYPE=TIME``) still do NOT compose as bare clause-final
  adjuncts. The constraining equation
  ``(↓2 ADV_TYPE) =c 'FREQUENCY'`` restricts the new rule to
  FREQUENCY only; the TIME deferral stays.

### Out of scope for this commit

* Bare-frequency-N as clause-final ADJUNCT
  (``Tumakbo ako dalawang beses``) — see "Periphrastic" above.
* Topicalized frequency-N (``Dalawang beses akong tumakbo``)
  — depends on the bare-frequency-N rule landing first.
* The narrative idiom ``Nang isang beses, ...`` — narrow
  lexical idiom, separate follow-on; do NOT generalize to
  ``nang + NUM + beses``.
* Pre-verbal ``maka-`` with linker (``makalawang nakakain``):
  the cited S&O example uses pre-verbal placement with
  linker, but clause-final placement is the more common and
  simpler case; pre-verbal is deferred.
* Bare AdvP attachment for non-FREQUENCY adverb types — kept
  deferred per the Phase 5e Commit 3 note.
* Productive ``maka-`` morphology paradigm — the hand-authored
  10-entry inventory covers v1 needs; productive treatment
  is a follow-on if needed.
* Spanish-borrowed ``doble`` / ``triple`` adverbial use —
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

* ``punto`` (``data/tgl/particles.yaml``): PART with
  ``DECIMAL_SEP: "YES"``. Spanish-borrowed decimal separator;
  joins integer and fractional cardinals.
* ``porsiyento`` (``data/tgl/roots.yaml``): NOUN with
  ``SEM_CLASS: PERCENTAGE``. Spanish-borrowed; Tagalog has no
  native percentage word. Used as the head N of cardinal-
  modified percentage NPs.

### Grammar change (decimal)

```
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

* Decimal as NP-modifier (``dos punto singkong libro`` "2.5
  books") — semantically odd and likely not corpus-attested,
  but structurally would work via the existing cardinal-NP-
  modifier rule once SEM_CLASS percolation lands. Not
  exercised here.
* Equational sentences for predicative percentages — needs a
  general N-as-predicate rule; deferred to a future commit.
* Symbolic decimal forms (``2.5``, ``10.75``) — tokenizer
  expansion track; symbolic numerals are §18 out-of-scope.
* Three-term decimals (``dos punto singko punto otso``) —
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

* ``una`` (1st, suppletive — not ``*ikaisa``).
* ``ikalawa`` (2nd, with stem truncation: ``ika-`` + ``lawa``,
  not ``*ikadalawa``).
* ``pangalawa`` (2nd alternative, high-frequency colloquial
  variant; S&O 1972 §4.4 footnote).
* ``ikatlo`` (3rd, similar stem truncation: ``ika-`` + ``tlo``).
* ``ikaapat`` (4th), ``ikalima`` (5th), ``ikaanim`` (6th),
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

* ``ang unang aklat ko`` "my first book" (singular).
* ``ang unang mga aklat ko`` "my first books" (plural,
  with ``mga`` marker).

Both are grammatical. The matrix NP's NUM is determined by the
head noun (or ``mga`` plural marker), not the ordinal. So the
ordinal lex entries omit NUM, and the ordinal-NP-modifier rule
omits the NUM-projection equation that the cardinal rule has.

### Grammar change

6 new ordinal NP-modifier rules (parallel to the Commit 1
cardinal NP-modifier rules):

```
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

* OBJ position (``Bumili ako ng unang aklat`` "I bought the
  first book"): all 11 ordinals exercised across the sweep.
* SUBJ position (``Tumakbo ang unang aso`` "the first dog
  ran").
* DAT position (``Pumunta ako sa ikatlong kuwarto`` "I went
  to the third room").
* Alternative ``pangalawa`` form parses with the same
  ORDINAL_VALUE=2 as ``ikalawa``.

### Negative fixtures

Per Phase 5f §11.2 negative-fixture convention:

* ``*Bumili ako ng una aklat.`` — missing linker.
* ``*Bumili ako ng unang ikalawang aklat.`` — chained
  ordinals, blocked by ``¬ (↓4 ORDINAL_VALUE)``.

### Out of scope for this commit

* Productive ``ika-`` morphology paradigm (with ``ikalawa`` /
  ``ikatlo`` truncation sandhi).
* Productive ``pang-`` ordinal morphology (the alternative
  variant — only ``pangalawa`` lex'd here).
* Predicative ordinal (``Ikalawa ang anak ko`` "My child is
  the second [one]") — needs a parallel S rule to the
  predicative cardinal rule (Commit 4); deferred.
* Mixed ordinal + cardinal (``ang unang dalawang aklat`` "the
  first two books") — needs an ordinal-of-cardinal stacking
  rule; deferred.
* Higher ordinals (11th+, hundredth, thousandth) — uses
  ``ika-`` + compound cardinal; deferred to a follow-on
  alongside compound-cardinal coordination.

## Phase 5f Commit 8: fractions

**Date:** 2026-05-03. **Status:** active. Lex-only addition
(4 NOUN entries); no grammar changes. Refs: plan §11.1
Group C; S&O 1972 §4.4; Phase 5f Commits 1 + 7 (cardinal /
ordinal NP-modifier rules consumed unchanged); Ramos 1971.

### Lex change

4 NOUN entries added to ``data/tgl/roots.yaml``:

* ``kalahati`` "half" — native form. SEM_CLASS=FRACTION.
  Bidirectional synonym of ``medya``.
* ``kapat`` "quarter" — native form. SEM_CLASS=FRACTION.
* ``medya`` "half" — Spanish-borrowed; canonical in clock-time
  register (``alas-otso y medya`` "8:30") which Group E will
  exercise. Bidirectional synonym of ``kalahati``.
* ``bahagi`` "part" — head N for the productive
  ``[ORDINAL]ng bahagi`` fraction pattern (``ikatlong bahagi``
  "third part" = 1/3; ``ikaapat na bahagi`` "fourth part"
  = 1/4). SEM_CLASS=PART.

### Why no grammar change

Compositional fractions parse via existing rules:

* ``[CARDINAL]ng kalahati / kapat / medya`` (``dalawang
  kalahati`` 2/2, ``apat na kapat`` 4/4, ``tatlong kapat``
  3/4) uses the Phase 5f Commit 1 cardinal-NP-modifier rule.
* ``[ORDINAL]ng bahagi`` (``ikatlong bahagi``,
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

* Mixed numbers (``dalawa't kalahati`` "two and a half" 2½;
  ``apat at kalahati`` "four and a half" 4½; ``isa't kapat``
  "one and a quarter" 1¼). Need the bound ``'t`` clitic
  split (parallel to ``split_linker_ng`` / ``split_enclitics``)
  and a NUM coordination rule. Deferred to Phase 5k
  coordination work per plan §11.1 Group C item 4 — likely
  shareable infrastructure with the other ``'t`` cases.
* Hyphenated ``ikatlong-bahagi`` orthographic variant. The
  unhyphenated ``ikatlong bahagi`` (two tokens, ordinal +
  bahagi) is what the existing tokenizer yields and what this
  commit exercises. The hyphenated form would need a tokenizer
  pre-pass; deferred.
* ``[CARDINAL]ng kuwarto`` clock-time register (``isang
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

* ``dagdag`` — OP=PLUS. Coexists with the existing ``dagdag``
  VERB root (in ``data/tgl/roots.yaml``, "add to"); the bare
  uninflected form is _UNK from the verbal pipeline (no
  paradigm cell emits a bare form), so adding the PART entry
  introduces no ambiguity in the verbal use cases (which
  always carry a voice/aspect prefix or infix).
* ``bawas`` — OP=MINUS. Same coexistence story as ``dagdag``.
* ``beses`` — OP=TIMES. **Coexists with the existing**
  ``beses`` **NOUN** with SEM_CLASS=FREQUENCY (Phase 5f
  Commit 5). Both readings now exist in the morph index; the
  PART reading fires in arithmetic-operator positions, the
  NOUN reading in periphrastic-frequency NP positions. Same
  coexistence pattern as ``na`` (LINK vs ASPECT_PART).
* ``hati`` — OP=DIVIDE.

### Grammar change

4 new S rules:

```
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

```
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

* Symbol-form arithmetic (``2 + 3 = 5``, ``10 - 3 = 7``,
  etc.) — tokenizer expansion track; §18 out-of-scope.
* Spanish-borrowed ``multiplikado`` synonym for ``beses``
  (TIMES). Less common than the native form; lex-only
  follow-on if corpus pressure surfaces it.
* Compound expressions (``Dalawa dagdag tatlo dagdag apat ay
  siyam`` "2+3+4=9") — would need a recursive NUMOP rule;
  deferred.
* Decimal operands (``Dos punto singko dagdag isa ay tatlo
  punto singko`` "2.5+1=3.5") — the decimal NUM from Commit
  6 satisfies ``NUM[CARDINAL=YES]`` and CARDINAL_VALUE only
  records the integer part, so this would partially work
  (operand_1=2 not 2.5). Defer until full decimal-value
  representation lands.
* Ordinal arithmetic (no such thing in standard usage; the
  ordinal/cardinal disjointness from Commit 7 prevents it
  structurally).

## Phase 5f Commit 10: clock-time NOUNs (Group E item 1)

**Date:** 2026-05-03. **Status:** active. Lex-only (12 entries);
no grammar changes. Refs: plan §11.1 Group E item 1; R&G 1981;
S&O 1972 §6.13.

### Lex change

12 NOUN entries added to ``data/tgl/roots.yaml`` for the
Spanish-borrowed clock-time terms:

* ``alauna`` (1 o'clock — special vowel-initial contraction:
  ``ala-`` + ``una`` not ``alas-uno``).
* ``alasdos`` (2), ``alastres`` (3), ``alaskuwatro`` (4),
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

* A tokenizer pre-pass that recognises and merges
  ``alas?-NUM`` patterns into a single token before morph.
* A grammar rule that consumes ``alas`` + hyphen + cardinal as
  a single TIME constituent.

Both are deferred to a follow-on commit. This commit uses
single-token forms (``alauna`` / ``alasotso`` / etc.) — a real
attested orthographic variant in informal text — that work with
the existing tokenizer unchanged.

### Out of scope for this commit (deferred to follow-on Group E
commits)

* Hyphenated orthography (``ala-una`` / ``alas-otso``).
* Time-of-day modifiers (``alasotso ng umaga`` "8 in the
  morning"; ``alasotso ng hapon`` "8 in the afternoon"). Needs
  ``umaga`` / ``hapon`` / ``gabi`` / ``tanghali`` /
  ``madaling-araw`` lex with SEM_CLASS=TIME plus a small
  modifier rule.
* Minute composition: ``alasotso y medya`` 8:30, ``alasotso
  y singko`` 8:05, ``alasotso menos singko`` 7:55. Needs
  ``y`` and ``menos`` PART entries plus a
  ``TIME → CLOCK [y|menos] NUM`` rule.
* Native time deictics: ``kanina`` (earlier today), ``mamaya``
  (later today), ``tanghali`` (noon), ``madaling-araw`` (dawn).
  ``ngayon``, ``bukas``, ``kahapon``, ``mamaya`` already exist
  as ADV; the missing ones plus a uniform SEM_CLASS=TIME tag.
* ``mga`` time approximation (``mga alasotso`` "around 8
  o'clock") — ``mga`` itself isn't in lex yet.

## Phase 5f Commit 11: time-of-day NOUNs + native time deictics (Group E items 2 + 5)

**Date:** 2026-05-03. **Status:** active. Lex-only addition;
no grammar changes. Refs: plan §11.1 Group E items 2 + 5;
S&O 1972 §6.13; Phase 5f Commits 5 + 10.

### Lex change

* **Time-of-day NOUNs** (``data/tgl/roots.yaml``):
  ``umaga`` (morning), ``tanghali`` (noon / midday),
  ``hapon`` (afternoon). All NOUN with SEM_CLASS=TIME.
  ``gabi`` (night) and ``araw`` (day / sun) already exist as
  plain NOUN entries in roots.yaml; not modified here to keep
  the diff focused — they compose via existing rules without
  the SEM_CLASS feature.
* **Native time deictics** (``data/tgl/particles.yaml``):
  ``kanina`` (earlier today), ``kamakalawa`` (day before
  yesterday). Both ADV with ADV_TYPE=TIME and
  DEIXIS_TIME=PAST. Parallel structure to the existing
  ``kahapon`` / ``ngayon`` / ``bukas`` / ``mamaya`` ADV entries.

### Why no grammar change

Time-of-day modifier composition (``alasotso ng umaga`` "8 in
the morning") parses via the existing Phase 4 §7.8 NP-internal
possessive rule:

* ``alasotso`` — clock-time NOUN (Phase 5f Commit 10)
* ``ng umaga`` — GEN-NP modifier
* The possessive rule attaches GEN-NP as POSS to the head N

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

* Bare clause-final TIME AdvP (``Pumunta ako kanina``) —
  Phase 5e Commit 3 deferral, lifted in a separate commit.
* ``madaling-araw`` "dawn" — hyphenated single-word concept,
  needs tokenizer pre-pass; deferred.
* Updating existing ``gabi`` / ``araw`` / ``bukas`` /
  ``oras`` to add SEM_CLASS=TIME — keep diff focused; they
  compose via existing rules without the feature.
* Minute composition (``alasotso y medya`` 8:30) — needs
  ``y`` and ``menos`` PART entries plus a ``TIME → CLOCK
  [y|menos] NUM`` rule; follow-on commit.
* ``mga`` time approximation (``mga alasotso``) — ``mga``
  isn't yet in lex; needs broader ``mga`` analysis (also
  marks plurals).

## Phase 5f Commit 12: minute composition (Group E item 4)

**Date:** 2026-05-03. **Status:** active. 2 PART operators in
lex + 4 N grammar rules + a side change to ``N → NOUN``. Refs:
plan §11.1 Group E item 4; S&O 1972 §6.13; Phase 5f Commits 5
+ 8 + 10 + 11.

### Lex change

2 PART operators added to ``data/tgl/particles.yaml``:

* ``y`` — Spanish "and"; PART with MINUTE_OP=Y. Forward-
  counting: ``alasotso y singko`` "8:05".
* ``menos`` — Spanish "minus"; PART with MINUTE_OP=MENOS.
  Backward-counting: ``alasotso menos singko`` "7:55".

### Grammar change

4 new N rules — 2 ops × 2 daughter types:

```
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
already exists as a NOUN ("room") in roots.yaml. Adding a
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

* ``alasotso y kuwarto`` parsing — see polysemy deferral
  above.
* Chained minute compositions (``*alasotso y singko y dies``)
  — would require recursive composition; not standard usage.
* Symbolic time forms (``8:30``, ``8:05``) — tokenizer
  expansion track; §18 out-of-scope.
* MINUTE_OP / MINUTE_VALUE / MINUTE_FRACTION projection to NP
  — same NP-from-N limitation as cardinal-modifier features
  from Commit 1.

## Phase 5f Commit 13: dates (Group F)

**Date:** 2026-05-03. **Status:** active. 19 NOUN entries +
2 PART entries + 4 grammar rules (3 PP variants + 1 S rule).
Refs: plan §11.1 Group F; S&O 1972 §6.13; Phase 5f Commits 7
(ordinals) + 11 (time deictics).

### Lex change

**Months** (data/tgl/roots.yaml): 12 Spanish-borrowed month
names (``enero`` ... ``disyembre``) as NOUN with
``SEM_CLASS: MONTH`` and ``MONTH_VALUE`` (1-12).

**Days of week** (data/tgl/roots.yaml): 7 day-of-week NOUNs
— Spanish-borrowed (``lunes``, ``martes``, ``miyerkules``,
``huwebes``, ``biyernes``, ``sabado``) and native
(``linggo``). All NOUN with ``SEM_CLASS: DAY`` and
``DAY_VALUE`` (1-7). The existing ``linggo`` entry was
updated in place to add SEM_CLASS=DAY (rather than adding a
duplicate, which the morph analyzer collapses — see Phase 5f
Commit 12 kuwarto polysemy memo).

**Temporal-frame PARTs** (data/tgl/particles.yaml):

* ``tuwing`` (every) — PART with ``TIME_FRAME: PERIODIC``.
  Introduces a periodic temporal-frame PP.
* ``noong`` (last / past) — PART with ``TIME_FRAME: PAST``.
  Introduces a past temporal-frame PP.

### Grammar change

**3 PP rules** (gated by SEM_CLASS):

```
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

```
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

### Date formula

The formula ``ang ikalimang araw ng Enero`` "the fifth day
of January" composes from existing rules:

* ``ikalimang araw`` — ordinal-NP-modifier rule (Phase 5f
  Commit 7) — ``ikalima`` + ``-ng`` + ``araw`` produces an
  N with ORDINAL_VALUE=5 and LEMMA=araw.
* ``ang ikalimang araw`` — existing ``NP[CASE=NOM] →
  DET[CASE=NOM] N`` rule.
* ``ng Enero`` — existing GEN-NP rule.
* ``ang ikalimang araw ng Enero`` — existing Phase 4 §7.8
  NP-internal possessive rule attaches GEN-NP as POSS.

No new grammar required.

### Out of scope for this commit

* **Day-month abbreviated form** (``Mayo 5``) — needs digit
  tokenization (the one digit-form case the linguistic scope
  can't avoid per plan §11.1 Group F item 4). Tokenizer pre-
  pass is the cleanest fix; deferred.
* **Elided-N date formula** (``ang ikalima ng Enero``
  without ``araw``) — needs an ordinal-as-N rule. Not
  standard in formal Tagalog (the explicit ``araw`` is
  preferred); deferred.
* **Year expressions** (``noong 1990``) — needs digit
  tokenization.
* **MONTH_VALUE / DAY_VALUE projection to PP/NP** — same
  NP-from-N projection limitation as cardinal-modifier
  features.
* **Other temporal SEM_CLASSes for tuwing/noong** —
  e.g., season (``tuwing tag-init`` "every dry season"). Add
  SEM_CLASS=SEASON to the rule's variant list when Group G
  seasons land.

## Phase 5f Commit 13 (bundled): mga time approximation (Group E item 3)

**Date:** 2026-05-03. **Status:** active. 1 PART entry + 1
grammar rule. Refs: plan §11.1 Group E item 3; Phase 5f
Commit 10 (clock-time NOUNs consumed unchanged).

This work landed inside the bundled git Commit 13 (``ec23c55
Phase 5f Commit 13 — mga time approximation (Group E item 3)
+ dates (Group F)``); originally sequenced as a separate
Commit 14 in the plan but bundled when the mga gap was
identified during Group F work. The plan's Commit-14 slot is
re-used by Group G seasons below.

### Lex change

* ``mga`` PART (data/tgl/particles.yaml) with
  ``PLURAL_MARKER: YES``. The Tagalog plural / approximator
  particle, used for both plural marking on regular nouns
  (``ang mga aklat`` "the books") and approximation on
  temporal / quantitative NPs (``mga alasotso`` "around 8
  o'clock", ``mga sampu`` "around 10"). This commit adds the
  lex entry plus a grammar rule for the time-approximation
  reading only; plural marking and cardinal approximation
  are deferred to follow-on commits.

### Grammar change

```
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

### Out of scope for this commit

* **Plural marker on regular nouns** (``ang mga aklat`` "the
  books") — needs an NP-internal rule for ``DET PART[mga] N``
  plural marking, plus possibly NUM agreement effects.
  Substantial scope; deferred.
* **Cardinal approximation** (``mga sampu`` "around ten") —
  parallel rule with NUM[CARDINAL=YES] daughter. Lex-only
  follow-on — the rule already exists in shape, just needs
  a NUM variant.
* **DAY / MONTH approximation** — not idiomatic in standard
  Tagalog.
* **APPROX projection to NP** — same NP-from-N projection
  limitation as cardinal-modifier features (Commit 1).

### Side change (Commit 4): `synonyms` lex field + ``aklat`` noun

This commit adds a ``synonyms: list[str]`` field to the ``Root``
dataclass and YAML loader so synonymous lex citations can be
recorded as data (not just comments). Motivated by adding
``aklat`` "book" to ``data/tgl/roots.yaml`` as the canonical
``Sandaan ang aklat`` example (Ramos 1971: "aklát n. book.
--syn. libró."). Both ``aklat`` and the existing ``libro``
entries get bidirectional ``synonyms`` lists. The field is
backward-compatible (defaults to an empty list) and currently
unused by the parser — it's recorded for downstream tools
(dictionary export, cross-reference, future ranker semantic
similarity).

### Out of scope for this commit

* Cardinal as predicate over a clausal SUBJ
  (``Tatlo na siyang anak ang nakain ng isda`` "the three of
  her children who ate fish are gone") — would need
  embedding-rule extension; not standard usage.
* Predicative-cardinal in subordinate clauses (``Sinabi niya
  na tatlo ang anak ko``) — the linker-XCOMP / linker-COMP
  machinery from Phase 5c §7.6 should compose; not explicitly
  tested here but no expected change to that machinery.
* Number-agreement enforcement (``Tatlo ako`` would be
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

Five season NOUNs (``data/tgl/roots.yaml``):

* ``taginit`` — hot / dry season.
* ``tagulan`` — rainy season.
* ``taglamig`` — cold spell (colloquial).
* ``tagaraw`` — sunny period.
* ``taggutom`` — hunger season (figurative).

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

```
PP → PART N
Equations:
  (↑) = ↓1
  (↑ OBJ) = ↓2
  (↓1 TIME_FRAME)              # existential — PART has TIME_FRAME
  (↓2 SEM_CLASS) =c '<X>'      # X in {DAY, TIME, MONTH, SEASON}
```

gains a SEASON variant (the ``for sem_class in (...)`` loop
in ``src/tgllfg/cfg/grammar.py`` extends to four members).
This makes ``tuwing tagulan`` "every rainy season" (PERIODIC)
and ``noong taginit`` "during the dry season" (PAST) parse
via the same machinery as ``tuwing Lunes`` / ``noong
Pebrero``. The clause-final S → S PP rule is consumed
unchanged (it's gated on TIME_FRAME, not SEM_CLASS).

### Composition without new grammar

* ``sa tagulan`` "in the rainy season" — DAT-NP; the existing
  intransitive-ADJUNCT routing handles it. The SEM_CLASS=
  SEASON marking does not disturb this path.
* ``Tuwing tagulan ay pumunta ako.`` — ay-fronting of the new
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

* ``*Pumunta ako tuwing aklat.`` — ``aklat`` has no
  SEM_CLASS, so the constraining equation fails for all four
  variants (DAY / TIME / MONTH / SEASON). The PP rule does
  not fire and the sentence does not produce a TIME_FRAME PP
  parse.
* ``*Pumunta ako tuwing araw.`` — ``araw`` is an existing
  NOUN (day / sun) with no SEM_CLASS set. Including this
  fixture confirms the gate is constraining (not just
  descriptive): if the gate were missing, ``araw`` would be a
  plausible season-domain head and the rule would over-fire.
* ``aklat`` does not pick up SEM_CLASS=SEASON from anywhere.
  (Sanity check on the lex addition.)

### Out of scope for this commit

* **Hyphenated orthography** (``tag-init``, ``tag-ulan``,
  etc.) — needs the deferred tokenizer pre-pass described
  above.
* **Productive ``tag-`` paradigm** — see "Why lex-only" above.
  Adding a productive class would over-cover figurative /
  colloquial uses.
* **SEM_CLASS=SEASON projection to NP / PP-matrix** — the
  same NP-from-N projection limitation as cardinal-modifier
  features (Commit 1) and MONTH_VALUE / DAY_VALUE on date
  PPs (Commit 13). Tests walk down to the OBJ N to read
  SEM_CLASS rather than expecting it on the matrix
  PP / NP.
* **``mga`` season approximation** (``mga tagulan`` "around
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

* ``ilan``      — ``Q[QUANT=FEW, VAGUE="YES"]``
* ``marami``    — ``Q[QUANT=MANY, VAGUE="YES"]``
* ``kaunti``    — ``Q[QUANT=FEW, VAGUE="YES"]``
* ``konti``     — ``Q[QUANT=FEW, VAGUE="YES"]``
* ``kakaunti``  — ``Q[QUANT=VERY_FEW, VAGUE="YES"]``
* ``iilan``     — ``Q[QUANT=FEW, VAGUE="YES"]``
* ``karamihan`` — ``Q[QUANT=MOST, VAGUE="YES"]``

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

* **Semantic alignment.** ``marami`` / ``ilan`` etc. don't
  participate in arithmetic, fractions, ordinals, decimals,
  or any of the constructions in Groups A-D. They quantify
  rather than count. Grouping them with ``lahat`` / ``iba``
  reflects the actual distribution.
* **No NUM features.** Vague cardinals carry no
  CARDINAL_VALUE / ORDINAL_VALUE / NUM (sg/pl). Pretending
  they're NUM and then suppressing those features via
  constraints is more bookkeeping than benefit.
* **Plan endorsement.** §11.1 Group H literally says "any
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

```
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

```
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

* ``*ang maraming kaunting bata`` — chained vague Qs blocked by
  ``¬ (↓4 VAGUE)``.
* ``*ang marami ng bata`` — vague-Q in GEN-NP partitive blocked
  by the new ``¬ (↓2 VAGUE)`` gate on the existing Phase 5b
  rule.

### Out of scope for this commit

* **DAT-NP partitive for vague Qs** (``marami sa kanila``
  "many of them") — separate construction; not in Group H1
  scope. Defer.
* **Contracted ``ilang bata`` form** (irregular bound ``-ng``
  on the consonant-final stem ``ilan``) — non-standard
  contraction; would need a tokenizer pre-pass for the
  irregular split. Defer.
* **Float for vague Qs** (``Kumain sila marami``) — the
  existing Phase 4 §7.8 ``S → S Q`` float rule fires on vague
  Qs unmodified, but the binding semantics differ from
  ``lahat`` float (vague selects a subset; ``lahat`` asserts
  about the whole). Mechanically composes; semantically a
  follow-on if corpus pressure surfaces a need.
* **VAGUE projection to outer NPs (POSS, etc.)** — same NP-
  from-N projection limitation as cardinal-modifier features.

## Phase 5f Commit 16: approximators (Group H1 item 2)

**Date:** 2026-05-03. **Status:** active. 2 PART lex entries
+ 3 new grammar rules. Refs: plan §11.1 Group H item 2; S&O
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

* ``halos`` — PART[APPROX="YES"]. "almost / nearly".
* ``humigitkumulang`` — PART[APPROX="YES"]. "approximately /
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

Three new rules in ``src/tgllfg/cfg/grammar.py``:

**1. Cardinal-NUM approximator wrap.**

```
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

```
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

```
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
|------|------------------------|--------------------------------|
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

* ``Bumili ako ng halos sampung aklat.`` — OBJ position.
* ``Kumakain ang halos sampung bata.`` — SUBJ position.
* ``Pumunta ako sa halos sampung bahay.`` — DAT position.
* ``Halos sampu ang aklat ko.`` — predicative position
  (Phase 5f Commit 4 predicative-cardinal rule).

The matrix NP (or matrix predicate clause, in the predicative
case) doesn't lift APPROX from the daughter NUM — same NP-
from-N projection limitation as cardinal-modifier features.
Tests walk down to the inner NUM to verify APPROX=YES.

### Negative fixtures (per §11.2)

* ``*Pumunta ako sa halos bata.`` — ``bata`` is N (not NUM/Q
  with APPROX gating). The wrap rules' constraining equations
  fail; no parse composes ``halos`` as an approximator
  modifier on ``bata``.
* ``*Pumunta ako halos.`` — bare ``halos`` with no NUM/Q
  daughter. The wrap rules require a daughter; without one
  the rule doesn't fire.

### Out of scope for this commit

* **Hyphenated ``humigit-kumulang`` orthography** — needs the
  same tokenizer pre-pass deferred for Phase 5f Commit 14
  seasons.
* **``malapit sa NUM``** "close to N" — multi-word
  approximator with a DAT-NP complement
  (``malapit sa sampu`` "close to ten"). Analytically more
  involved than the simple pre-modifier; the head ``malapit``
  is an adjective and the construction needs an
  ADJ + DAT-NP frame rule. Deferred to a later commit.
* **APPROX percolation to the matrix NP** — same NP-from-N
  projection limitation as cardinal-modifier features
  (Commit 1) and SEASON percolation (Commit 14). Could be
  lifted by extending the Commit 1 / Commit 7 / Commit 15
  NP-modifier rules to lift APPROX explicitly; out of scope
  for this commit.
* **mga DAY / MONTH approximation** — non-idiomatic; flagged
  out-of-scope in Commit 13 and remains so.

## Phase 5f Commit 17: numeric comparatives (Group H1 item 3)

**Date:** 2026-05-03. **Status:** active. 4 PART lex entries
+ 4 new grammar frame rules. Refs: plan §11.1 Group H item 3
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

* ``higit``    — PART[COMP_PHRASE="HIGIT"]. Solo use: "more (than)".
* ``kulang``   — PART[COMP_PHRASE="KULANG"]. Solo use: "less (than)".
* ``bababa``   — PART[COMP_PHRASE="BABABA"]. Negated-context use:
                 ``hindi bababa`` "no less than / at least".
* ``hihigit``  — PART[COMP_PHRASE="HIHIGIT"]. Negated-context use:
                 ``hindi hihigit`` "no more than / at most".

### Polysemy with verb-form analyses

``higit`` is also a verb root in roots.yaml (``higit`` "pull,
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
|------|-----------|------------|
| 1 | ``PART[HIGIT] ADP[DAT] NUM[CARDINAL=YES]`` | GT |
| 2 | ``PART[KULANG] ADP[DAT] NUM[CARDINAL=YES]`` | LT |
| 3 | ``PART[NEG] PART[BABABA] ADP[DAT] NUM[CARDINAL=YES]`` | GE |
| 4 | ``PART[NEG] PART[HIHIGIT] ADP[DAT] NUM[CARDINAL=YES]`` | LE |

### Grammar change

Four parallel rules in ``src/tgllfg/cfg/grammar.py``, generated
by two ``for`` loops over ``(comp_lex, comp_value)`` pairs.

**Solo frame** (higit / kulang):

```
NUM → PART ADP NUM
Equations:
  (↑) = ↓3                              # share inner NUM's f-structure
  (↑ COMP) = '<GT or LT>'               # set explicitly per rule
  (↓1 COMP_PHRASE) =c '<HIGIT or KULANG>'
  (↓2 CASE) =c 'DAT'                    # ``sa`` only
  (↓3 CARDINAL) =c 'YES'                # genuine cardinal NUM
```

**Negated frame** (hindi bababa / hindi hihigit):

```
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

* ``*higit sampung aklat`` — frame rule requires the DAT
  marker ``sa`` between the comparator and the NUM standard.
* ``*higit sa bata`` — head is N (not NUM[CARDINAL=YES]); the
  ``(↓ CARDINAL) =c 'YES'`` constraint fails.
* ``*hindi bababa sampung aklat`` — negated frame rule
  requires ``sa`` (parallel to the solo frame).

### Out of scope for this commit

* **Gradable / scalar ``mas``** (without numeric reference,
  e.g., ``mas matalino`` "more intelligent") — Phase 5h
  (gradable adjective comparison). Distinct construction;
  doesn't take a numeric standard.
* **Comparators on Q heads** (``higit sa kalahati`` "more
  than half", ``higit sa lahat`` "more than all") — extending
  the frame rules to admit FRACTION / PERCENTAGE /
  MULTIPLIER / Q daughters is mechanical but additive. Defer.
* **COMP projection to the matrix NP** — the wrapped NUM
  carries COMP, but the matrix NP doesn't lift it (same NP-
  from-N projection limitation as APPROX in Commit 16,
  CARDINAL_VALUE in Commit 1, etc.). Tests verify
  CARDINAL_VALUE preservation; COMP rides on the inner NUM
  for downstream consumers.
* **Compound numeric standards** (``higit sa dalawang
  daan`` "more than two hundred") — the inner NUM standard
  composes via existing compound-cardinal rules, so this
  works mechanically with the frame rules. Not explicitly
  tested but no special handling needed.

## Phase 5f Commit 18: collective numerals (Group H2 item 4)

**Date:** 2026-05-03. **Status:** active. 4 NOUN lex entries
+ 1 new grammar rule (with 2 linker variants). Refs: plan
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

Four NOUN entries in ``data/tgl/roots.yaml``:

* ``pares``    — NOUN[MEASURE="YES"]. "pair" (Spanish-borrowed).
* ``dosena``   — NOUN[MEASURE="YES"]. "dozen" (Spanish-borrowed).
* ``daandaan`` — NOUN[MEASURE="YES", COLL_VALUE=HUNDREDS].
                  "hundreds" (canonical orthography
                  ``daan-daan``).
* ``libulibo`` — NOUN[MEASURE="YES", COLL_VALUE=THOUSANDS].
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

```
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

```
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

```
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

* ``*isang batang aklat`` — bata is a regular NOUN with no
  MEASURE feature; the linker-form measure-N rule's gate
  fails, so no comparator-style composition occurs.
* ``*isang dosenang dosenang itlog`` — chained measure NOUNs
  blocked by ``¬ (↓3 MEASURE)``.

### Out of scope for this commit

* **Hyphenated ``daan-daan`` / ``libu-libo``** orthography —
  needs the same tokenizer pre-pass deferred for Phase 5f
  Commit 14 seasons / Commit 16 ``humigit-kumulang``.
* **Productive ``card_redup`` morph class** for higher-order
  reduplicated multiples (``milyong-milyon`` "millions",
  ``bilyong-bilyon`` "billions") — per plan §11.1 Group H
  item 4: lex per attested form; productive class deferred.
* **MEASURE percolation to the matrix NP** — same NP-from-N
  projection limitation as cardinal-modifier features (Commit
  1). Tests walk down to verify CARDINAL_VALUE + LEMMA on the
  matrix NP plus a parse path with the right measure-N inner
  composition.
* **Other measure NOUNs** (``baso`` "cup" → ``isang basong
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

* tigisa, tigdalawa, tigtatlo, tigapat, tiglima, tiganim,
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

* Higher cardinals (``tig-sandaan`` "a hundred each", ``tig-
  sanlibo`` "a thousand each").
* Spanish-borrowed bases (``tig-uno``, ``tig-dos``).
* Compound cardinals (``tig-labindalawa`` "twelve each").

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

```
NP[CASE=GEN] → ADP[CASE=GEN] NUM[CARDINAL=YES] PART[LINK] N
```

For ``Bumili ako ng tigisang aklat.``:
* ``ng`` ADP[CASE=GEN]
* ``tigisa`` NUM[CARDINAL=YES, DISTRIB=YES, CV=1]
* ``-ng`` PART[LINK=NG]
* ``aklat`` N
* Output: NP[CASE=GEN, LEMMA=aklat, CV=1] (DISTRIB stays on
  the inner NUM — same NP-from-N projection limitation as
  cardinal-modifier features).

Consonant-final distributives (``tigapat``, ``tiganim``,
``tigsiyam``) use the standalone ``na`` linker; the Phase 5f
Commit 1 disambiguator branch for ``na`` after NUM[CARDINAL=
YES] keeps it as the linker (vs the ALREADY clitic). No new
disambiguator branch needed.

The predicative-cardinal rule (Phase 5f Commit 4) also
absorbs distributives: ``Tigisa sila.`` parses as S with
PRED='CARDINAL <SUBJ>', SUBJ=sila, CV=1.

### Negative fixtures (per §11.2)

* ``*Bumili ako ng tigisa.`` — bare distributive NUM without
  a head N. The cardinal-modifier rule requires a 4-daughter
  RHS (DET/ADP NUM LINK N); without the linker + N daughters,
  the OBJ-NP composition fails.

### Out of scope for this commit

* **Productive ``tig_distrib`` morph class** — see "Why per-
  form lex" above. Defer.
* **Distributive predicate construction** (``Tigisang aklat
  sila`` / ``Tigisa silang aklat`` "they each have one
  book") — verbless predicate with a linker-attached
  complement N. Analytically distinct from the NP-modifier
  composition this commit covers; needs a new S frame rule.
  S&O 1972 §4.5 describes the structure; deferred to a
  later commit.
* **DISTRIB percolation to the matrix NP** — same NP-from-N
  projection limitation as MEASURE / APPROX / COMP. Tests
  walk down to verify CARDINAL_VALUE preservation; DISTRIB
  rides on the inner NUM for downstream consumers.
* **Hyphenated ``tig-isa`` / ``tig-dalawa``** — needs the
  same tokenizer pre-pass deferred for Phase 5f Commits 14
  / 16 / 18.

## Phase 5f Commit 20: universal ``bawat`` / ``kada`` (Group H2 item 6)

**Date:** 2026-05-03. **Status:** active. 2 Q lex entries
+ 4 new grammar rules + 1 gating addition on the existing
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

* ``bawat`` — Q[QUANT=EVERY, UNIV="YES"]. Native universal.
* ``kada``  — Q[QUANT=EVERY, UNIV="YES"]. Spanish-borrowed
  colloquial synonym.

Same shape; the analyzer returns each as a single Q analysis
(no polysemy with the verb / paradigm-engine since neither
``bawat`` nor ``kada`` is generated by the paradigm engine).

### Three Q-distributions, now all covered

With this commit, Phase 5f has covered the three syntactic
distributions of Q heads in Tagalog:

| Distribution | Surface example | Rule | Phase |
|--------------|------------------|------|-------|
| Partitive (Q + GEN-NP) | ``ang lahat ng bata`` "all of the children" | ``NP[CASE=X] → DET/ADP Q NP[CASE=GEN]`` | Phase 5b §7.8 follow-on |
| Vague-Q-modifier (Q + linker + N) | ``ang maraming bata`` "many children" | ``NP[CASE=X] → DET/ADP Q PART[LINK] N`` (gated on VAGUE=YES) | Phase 5f Commit 15 |
| Universal (Q + bare N) | ``ang bawat bata`` "every child" | ``NP[CASE=X] → DET/ADP Q N`` (gated on UNIV=YES) | This commit |

Each Q lex entry has a feature (no feature for partitive Qs;
VAGUE=YES for vague Qs; UNIV=YES for universals) that gates
its rule. The negative gates ``¬ (↓2 VAGUE)`` and
``¬ (↓2 UNIV)`` on the partitive ensure non-partitive Qs
don't accidentally fire there. The constraining equations
``(↓2 VAGUE) =c 'YES'`` and ``(↓2 UNIV) =c 'YES'`` ensure the
respective rules fire only on their target Qs.

### Grammar change

Four new rules in ``src/tgllfg/cfg/grammar.py`` plus a gate
addition on three existing rules.

**3 case-marked NP rules** (NOM / GEN / DAT):

```
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

```
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

* ``*ang bawat kada bata`` — chained universals blocked by
  ``¬ (↓3 UNIV)``.
* ``*ang bawat ng bata`` — universal in GEN-NP partitive
  blocked by the new ``¬ (↓2 UNIV)`` gate on the Phase 5b
  partitive rules.

### Out of scope for this commit

* **``bawat isa`` / ``bawat dalawa``** (Q + NUM as quantifier
  over a number) — needs a parallel Q + NUM rule (mirroring
  the Q + N rule but with NUM as the daughter category).
  Additive but not in this commit's scope.
* **Q-quantification over a non-N head** (``bawat sa
  kanila`` "every of them" with a DAT-NP complement) —
  structurally distinct (Q + DAT-NP); deferred.
* **Floated universals** — the existing Phase 4 §7.8
  ``S → S Q`` float rule mechanically fires on UNIV Qs but
  the result isn't natural Tagalog (``Kumakain ang bata
  bawat`` is non-standard). Not explicitly tested or
  documented as supported.

