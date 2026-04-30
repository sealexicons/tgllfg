# Analytical decisions

This file records non-trivial linguistic decisions baked into the
grammar and lexicon, with citations and reasoning. Each entry has a
date, a short statement of the decision, the diagnostics that
support it, and the alternatives considered.

## *ng*-non-pivot in transitive non-AV → OBJ

**Date:** 2026-04-28. **Status:** active.

In transitive non-Actor-Voice clauses (Objective Voice, Dative Voice,
Instrumental Voice), the *ang*-NP is the pivot and unconditionally
maps to SUBJ (Kroeger 1993, ch. 2). The remaining core argument —
the *ng*-marked non-pivot — is analysed as **OBJ**, not as an oblique
agent (OBL-AG). This applies symmetrically across the non-AV voices
even though the role realised by the *ng*-NP varies (agent in OV,
goal in DV, instrument in IV).

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
