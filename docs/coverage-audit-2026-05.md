# Coverage audit — Wave 1 (rg81 transcriptions + R&B 1986)

> **Status:** Wave 1 pilot snapshot (2026-05-14). See
> ``.claude/plans/tgllfg-harvest-audit.md`` for the plan-of-record
> and ``.claude/plans/tgllfg-phase-8.md`` for the Phase 8
> remediation stub. Wave 2 (R&G Intermediate + R&C 1990 +
> Ramos 1971) and Wave 3 (S&O 1972 + R&G Conversational) follow.

## Headline

- **118** sentences harvested from
  ``transcriptions/rg81-excerpts.md`` (four chapters; ANG PAMILYA
  "Uncorrected continuation" subsection skipped per user
  directive 2026-05-14).
- **11 / 118 (9.3 %)** parse cleanly; **107 / 118 (90.7 %)**
  zero-parse, of which 82 produce a partial fragment and 25
  produce no fragment.
- **194** verb-base entries harvested from R&B 1986; **51 %** of
  R&B's documented bases appear in ``data/tgl/verbs.yaml``.

The 9 % parse rate against the 7306-fast-test parser is a much
sharper coverage signal than the 99.6 % parse rate against the
curated coverage corpus — confirming the (long-standing)
hypothesis that the curated corpus is biased toward constructions
the grammar already handles. Failures cluster into a small
number of named gaps; see §3 for the breakdown.

## 1. Wave 1 sources

- ``data/tgl/references/transcriptions/rg81-excerpts.md`` — hand-
  transcribed excerpts from Ramos & Goulet 1981 *Intermediate
  Tagalog*, four chapters:
  - ANG MANOK (51 sentences) — the famous benchmark essay; 7
    R&G simples + the combined essay-paragraph; closed in Phase
    5n.A as a curated fixture. The other 43 sentences of the
    chapter are out-of-curated-scope.
  - ANG PAG-AARAL NG ISANG WIKA (13 sentences, sentence-tokenized
    from 4 paragraphs).
  - PANAHON (41 sentences) — descriptive prose, 10 paragraphs.
  - ANG PAMILYA (13 sentences) — corrected portion only; the
    ``### Uncorrected continuation`` subsection is excluded.
  - Talasalitan (vocabulary) tables are excluded (lexical
    reference only, not parse fixtures).
- ``data/tgl/references/HandbokOfTagalogVerbs.txt`` — Ramos &
  Bautista 1986 *Handbook of Tagalog Verbs*; used for verb-base
  inventory only. The OCR scatters paradigm-cell forms across
  lines, so per-cell extraction is deferred; this run captures
  headword + affix-class-signature + gloss triples only.

## 2. Sentence-parse bucket distribution

Total: **118**.

| Bucket | Count | Share |
| --- | ---: | ---: |
| zero-parse-fragment | 82 | 69.5 % |
| zero-parse-no-fragment | 25 | 21.2 % |
| parse-success-1 | 10 | 8.5 % |
| parse-success-N | 1 | 0.8 % |

### Per-chapter breakdown

| Chapter | parse-success-1 | parse-success-N | zero-parse-frag | zero-parse-no-frag | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| ANG MANOK | 10 | 1 | 33 | 7 | 51 |
| PANAHON | 0 | 0 | 30 | 11 | 41 |
| ANG PAG-AARAL NG ISANG WIKA | 0 | 0 | 10 | 3 | 13 |
| ANG PAMILYA | 0 | 0 | 9 | 4 | 13 |

ANG MANOK is the only chapter that yields any clean parses
(the 11 R&G simples that Phase 5n.A explicitly closed). The
other three chapters yield zero clean parses — they exercise
naturalistic discourse-level prose that the current grammar
does not cover end-to-end.

## 3. Failure-cluster analysis

Heuristic clustering of the 107 zero-parse rows, ranked by
count. The "unclassified" bucket (50 sentences) is dominated by
**lex-missing verb bases** — the most common single failure
mode in Wave 1.

<!-- markdownlint-disable MD013 -->

| Cluster | Count | Class | Notes |
| --- | ---: | --- | --- |
| Lex-missing verb base | ~50 | **lex** | See §4 for the candidate list. |
| Long-sentence (≥ 12 tokens) | 24 | **multi-cause** | PANAHON descriptive prose; likely a mix of lex + construction-class failures compounding across the sentence. |
| ay-inverted predicate | 12 | **construction** | Complex inversion + nominalized SUBJ; some land in `ay`-fronted SubordClause (Phase 5l) but topic-`ay` over complex nominal predicates does not. |
| pinaka- superlative form | 4 | **lex** | `pinakaubod` "core-most", `pinakapuno` "head-most", `pinakamatibay` "strongest". Phase 5h closed productive `pinaka-` on Q heads (L40); same form on N heads is not wired. |
| papaka- causative IPFV | 4 | **paradigm** | `papakainin` "will be fed (it, by him)" — A2F + OV future; pa- causative + reduplication + -in OV. Likely a paradigm-cell gap or affix-class composition issue. |
| comma-fronted topic NP | 3 | **construction** | `Isang araw, ...` "One day, ..."; comma-fronted temporal/locative NP topic. The `ay`-inverted form is covered (Phase 5l C7) but the comma-only variant is not. |
| kanyang-class possessor | 3 | **construction** | Phase 5n.A C25 closed the canonical `kanyang aklat` form; combinations with cleft-style `ay` may still fail. |
| existential `may` + V-headed clause | 3 | **construction** | `May binalak siya`, `May naisip ang mama`. Existential `may` selecting a verb-headed nominalization rather than a simple NP. |
| naka- aptative with KITA-class stem | 2 | **paradigm/lex** | `nakita` "saw" emits PRED `'KITA'`, then the matrix expects `KITA <SUBJ, OBJ>` and a-structure fails completeness. The `kita`/`nakita` lex pair may have wrong PRED registration. |
| mga-DEM (plural demonstrative) | 1 | **construction** | `mga ito` "these". Phase 7a.A closed `mga` + N; `mga` + DEM PRON is the same shape with PRON head; not currently wired. |
| bago- as new-adj predicate | 1 | **construction** | `Bagong ani ang palay` "the rice is newly harvested". Diagnostic: `(↓1 LEMMA) =c 'ng'` constraining-form fails — the linker shape from `bago` doesn't match the rule's LEMMA gate. |
| TIME_FRAME path-undefined | 1 | **construction** | Phase 5f temporal infrastructure has a feature gate that the rule expects but the surface does not introduce. |
| APPROX/UNIV constraint-failed | 1 | **construction** | Similar feature-gate-undefined pattern from Phase 5f / 5n.A. |

<!-- markdownlint-enable MD013 -->

### Diagnostic-kind histogram (for the 107 zero-parses)

| Diagnostic kind | Count |
| --- | ---: |
| (no diagnostic captured — all fragments suppressed) | 73 |
| constraint-failed | 28 |
| completeness-failed | 2 |
| existential-failed | 2 |
| atom-mismatch | 2 |

The 73 "no-diagnostic" rows aren't truly silent — the parser
emits diagnostics on each chart edge that died — but my
bucketer only inspects the first fragment's diagnostics, and 73
sentences produced no Earley fragment large enough to inspect.
A richer Wave 2 bucketer should walk all blocked edges, not
just the largest fragment.

## 4. Probable lex gaps (verbs)

Inflected verb forms in the failed transcriptions that
correspond to bases **likely missing** from
``data/tgl/verbs.yaml``. (List is hand-curated from the
failed-sentence trace; not from the strip-to-base heuristic,
which is too noisy.)

| Base | Surface in transcription | Gloss | Frequency in fail set |
| --- | --- | --- | ---: |
| `tanim` | nagtatanim | plant (verb) | 2 |
| `tuka` | tinutuka | peck | 1 |
| `pasok` | ipinasok | put in / enter | 1 |
| `balak` | binalak | plan (verb) | 2 |
| `bunot` | nagbubunot | uproot / pull out | 1 |
| `sapit` | sumapit | arrive | 1 |
| `dungaw` | dumungaw | look out (window) | 1 |
| `putak` | pumutak | cackle / cluck | 1 |
| `bintang` | pinagbintangan | accuse | 1 |
| `taba` | tumaba | become fat | 1 |
| `gulay` | (NP, no verb) | vegetables | (lex-missing N) |
| `palay` | (NP) | unhusked rice | (lex-missing N) |
| `damo` | (NP) | grass / weeds | (lex-missing N) |
| `itlog` | (NP) | egg | (lex-missing N) |
| `tasa` | (NP) | cup | (lex-missing N) |
| `manok` | (NP) | chicken | (lex-missing N) |
| `bahay` | (NP) | house | (lex-missing N — likely covered, verify) |
| `bukid` | (NP) | farm / field | (lex-missing N — likely covered, verify) |

Verb-base lex gaps from §4 will lift the parse rate in ANG MANOK
significantly — most of the 33 zero-parse-fragment rows in that
chapter are AV/OV transitives whose only blocker is a missing
verb entry. Closing all 10 verb bases above plus the 7 noun
bases would likely move ANG MANOK from 11/51 → ~40/51.

## 5. R&B 1986 verb-base inventory

Extracted: **194** entries (one per `(base, gloss)` pair —
polysemous bases produce multiple rows). **147** distinct bases.

### Lex coverage

- In our lex: **99** (51.0 %)
- Not in our lex: **95** (49.0 %)

### Top 25 missing-from-lex R&B bases

(Sorted alphabetically by `base`. Glosses and affix classes post-
OCR-cleanup; see "Caveats" below for the cleanup rules.)

| Base | Gloss (R&B) | Affix class (R&B) |
| --- | --- | --- |
| `aksaya` | waste | mag- -in -an |
| `alaala` | remember | -um- -in |
| `alaala` | worry | mag- -in |
| `alaga` | take care of | mag- -an |
| `asa` | expect, rely on | -um- -an |
| `asso` | converse with | maki- |
| `away` | start a quarrel with | -um- -in |
| `away` | quarrel with each other | mag- |
| `balita` | report | mag- i- -an |
| `balita` | hear as rumor | maka- ma- -an |
| `buhay` | have life, live | ma- |
| `dilig` | water | mag- -in / -an |
| `dinig` | hear | maka- ma- |
| `galit` | use | -um- -in -an |
| `gamot` | cure / heal | -um- / mag- -in ipang- |
| `ganap` | perform | -um- -in / -an |
| `ganap` | occur, take place | -in |
| `gasta` | spend | -um- -in -an / pag- -an ika- |
| `gulat` | be surprised | ma- ika- |
| `gulo` | be disorderly | ika- |
| `gutom` | be hungry | ma- ika- |
| `haba` | lengthen | -an |
| `hinga` | breathe | -um- |
| `hinto` | stop | -an |
| `ibig` | love | -um- -in |

Note: `asso` is almost certainly an OCR mis-extraction; the
source headword is probably `USAP` "converse with" (the `maki-`
affix-class signature is consistent with `makipag-usap`).
Headword-level OCR mis-extractions like this are tracked under
"Caveats" below.

Several R&B-missing bases are already implied by §4's
transcription-failure list (`balak`, `tanim`, …) — converging
evidence that those gaps are real.

### Caveats on the R&B inventory

- The headword extractor catches ~147 distinct bases out of
  R&B's estimated ~300-500 total — many headwords are missed
  because they sit mid-page or have OCR-noisy capitalization.
  A revised Wave-2 extractor should scan for `<headword>` +
  next-line slot-header signature, not just isolated all-caps
  lines.
- OCR confuses `-um-` with `-urn-` (m → rn) for some entries;
  affix-class strings need normalization before downstream use.
- ALA(A)LA-style headwords with optional-letter parens are
  canonicalized to ``alaala`` (paren stripped) — this loses
  the distinction R&B encodes between ``alaala`` (memory) and
  ``alala`` (worry). Wave 2 should emit both surface keys.
- A few headwords arrive OCR-mangled at the extractor (e.g.
  `asso` is almost certainly source `USAP` "converse with").
  Wave 2 should add a fuzzy-headword-recovery pass keyed on
  the paradigm-form lines that follow the headword.
- **Gloss / affix-class OCR cleanup applied** (commit follows
  this report): `»` and `*` in R&B glosses both render the
  source's italicized comma; the patterns `dor`, `sendr`,
  `changer`, `selfr`, `lifer`, `expectf` render `do,`, `send,`,
  `change,`, `self,`, `life,`, `expect,` respectively (italic
  comma reads as `r` or `f` after specific letter contexts);
  `ì` in `pulì` and `ó` in `cióse` both render `l` (italic-l
  with serif noise). Spacing around `/` separators is
  normalized to ` / `. Wave 2 should extend the cleanup table
  if new OCR patterns surface.

## 6. Wave 1 conclusions

- **Lex gaps account for most of the failures** in the
  transcribed chapters. Closing the ~10 obvious verb-base gaps
  plus ~7 noun-base gaps from §4 is the highest-ROI first move.
- **A handful of construction-class gaps recur** — pinaka- on
  N heads, comma-fronted topics, mga + DEM, existential
  `may` + V-headed nominal, papakainin-style A2F+OV future.
  These are addressable as discrete Phase 8 sub-PRs.
- **Long descriptive prose (PANAHON-style) reveals
  compositional brittleness** — even where individual
  constructions are covered, chaining several across a 15-25
  token sentence trips multiple sub-failures. A "stress-test
  long-sentence" benchmark might be worth adding once the lex
  and discrete-construction gaps close.
- **The curated coverage corpus over-represents already-handled
  constructions** — the 99.6 % parse rate against
  `coverage_corpus.yaml` is real, but it doesn't reflect
  naturalistic-text coverage. Wave 2 + Wave 3 will quantify how
  much the curated-corpus bias overstates real coverage.

## 7. Next steps

1. Eyeball the Wave 1 cluster table; promote concrete clusters
   to Phase 8 sub-PRs (see ``.claude/plans/tgllfg-phase-8.md``).
2. Begin Wave 2 harvest: R&G Intermediate + R&C 1990 +
   Ramos 1971 Dictionary. Update extractor module to handle
   each source's structure.
3. Refine bucketer to walk all blocked edges, not just the
   largest fragment; the 73 no-diagnostic rows should
   produce useful diagnostics.
4. Wave 3 go/no-go decision after Wave 2.
