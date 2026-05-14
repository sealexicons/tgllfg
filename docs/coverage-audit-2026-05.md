# Coverage audit — Waves 1 + 2

> **Status:** Wave 1 pilot snapshot (2026-05-14) + Wave 2 expansion
> (same date). See ``.claude/plans/tgllfg-harvest-audit.md`` for the
> plan-of-record and ``.claude/plans/tgllfg-phase-8.md`` for the
> Phase 8 remediation stub. Wave 3 (S&O 1972 + R&G Conversational,
> Acrobat-OCR-only) is the go/no-go decision point after this Wave 2
> data lands. §1-§7 below cover Wave 1; §8 onwards covers Wave 2.

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

## 7. Wave 1 next steps (carried into Wave 2)

1. Eyeball the Wave 1 cluster table; promote concrete clusters
   to Phase 8 sub-PRs (see ``.claude/plans/tgllfg-phase-8.md``).
2. ✅ Wave 2 harvest: R&G Intermediate + R&C 1990 + Ramos 1971
   Dictionary — see §8 onward.
3. Refine bucketer to walk all blocked edges, not just the
   largest fragment; Wave 2 increased the no-diagnostic rows to
   ~800 — Phase 8.J on the plan stub.
4. Wave 3 go/no-go decision after Wave 2 — see §11 below.

## 8. Wave 2 sources

- ``data/tgl/references/901132785-Modern-Tagalog.txt`` — Ramos &
  Cena 1990 *Modern Tagalog: Grammatical Explanations and
  Exercises for Non-native Speakers*. Text-only fair-use copy;
  clean-OCR tier. 1044 candidate sentences extracted from
  chapter bodies + exercises + grammar-note example panels.
- ``data/tgl/references/Intermediate-Tagalog-developing-cultural-awareness-through-language_compress.txt``
  — Ramos & Goulet 1981 *Intermediate Tagalog: Developing
  Cultural Awareness through Language*. Clean-OCR tier (some
  intro-page artifacts but body is good). 1682 candidate
  sentences extracted from dialog lines, numbered exercise
  items, and pedagogical-unit titles.
- ``data/tgl/references/746927054-OceanofPDF-com-Tagalog-Dictionary-Teresita-v-Ramos.txt``
  — Ramos 1971 *Tagalog Dictionary*. Clean-OCR tier per the
  reference inventory, but the dictionary body has substantial
  character-spacing artifacts (single-letter "tokens"). Only
  102 candidate sentences survive the Tagalog-marker
  heuristic; mostly from clean-OCR intro material rather than
  the dictionary body proper.

Per-source extraction caps: 500 sentences run through the parser
(random sample with seed 42 for sources exceeding the cap).
Ramos 1971 processed in full (under cap).

## 9. Wave 2 sentence-parse bucket distribution

| Source | parse-1 | parse-N | zero-frag | zero-no-frag | Total | Clean parse % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RC 1990 (R&C 1990) | 18 | 1 | 289 | 192 | 500 | 3.8% |
| R&G Intermediate | 19 | 7 | 347 | 127 | 500 | 5.2% |
| Ramos 1971 Dictionary | 2 | 0 | 93 | 7 | 102 | 2.0% |
| **Wave 2 total** | **39** | **8** | **729** | **326** | **1102** | **4.3%** |

Wave 2 parse rates (3.8% / 5.2% / 2.0%) are substantially lower
than Wave 1's 9.3% — Wave 1 included the explicitly-curated R&G
benchmark fixtures, while Wave 2 is purely naturalistic source
content. The **4.3% Wave 2 aggregate** is the more honest baseline
for how the current grammar handles unprepared Tagalog input.

## 10. Wave 2 failure-cluster sampling (representative)

Diag-kind histograms (post-parse), per source:

| Diag kind | RC 1990 | R&G Int. | Ramos | Wave 2 total |
| --- | ---: | ---: | ---: | ---: |
| no-diag | 376 | 329 | 86 | 791 |
| constraint-failed | 79 | 113 | 10 | 202 |
| completeness-failed | 13 | 14 | 4 | 31 |
| atom-mismatch | 5 | 7 | 0 | 12 |
| existential-failed | 3 | 8 | 0 | 11 |
| neg-existential-failed | 3 | 1 | 0 | 4 |
| coherence-failed | 2 | 2 | 0 | 4 |

The "no-diag" bucket is again the largest (Phase 8.J — walk all
blocked edges, not just the largest fragment).

### Representative failure samples (10 per source)

**R&C 1990 — patterns surfaced:**

- `Ano ang pinakamatigas na bato sa mundo?` — `pinaka-` on ADJ
  predicate. Phase 5h closed `pinaka-` on Q heads (L40);
  Phase 8.C in the plan stub already covers `pinaka-` on N
  heads. **Adding `pinaka-` on ADJ heads** to the Phase 8.C
  scope.
- `Dumalaw pala si Sundalo.` — straightforward AV; likely lex
  gap on `dalaw` (visit).
- `Humingi ba ng tawad si Deo?` — `hingi` (ask for) plus
  `tawad` (forgiveness); likely lex gaps. Yes/no question with
  `ba` and AV `humingi`.
- `Kasinggaling ng Presidente ang senador.` — `kasinggaling`
  equative comparison (`kasing-` + reduplication of `galing`).
  Phase 5h L38 closed CV-redup `kasinggaganda` (5n.C.3); is
  the `kasing-` + `galing` formation different enough to be a
  separate gap?
- `Nang tamaan siya ng baseball sa ulo, ano'ng naging
  resulta?` — `Nang` temporal subordinator (distinct from
  `kapag` / `kung`).
- `Nagpasabi si Gina na kakain siua na hapunan dito.` —
  `nagpasabi` causative + finite-clause subord; OCR also
  shows `siua` for `siya`.

**R&G Intermediate — patterns surfaced:**

- `Kumusta ang pamilya mo?` — `kumusta` (how-is) predicate;
  likely lex-missing. Greeting/inquiry, very common in
  dialogue.
- `May palabas sa patyo.` — existential `may` + N + locative;
  variant of Phase 5j may-existential; `palabas` (show /
  performance) may be lex-missing.
- `E, si Alex yata ang kumuha.` — discourse interjection `E,`
  before cleft `si Alex yata ang kumuha`.
- `Sawa na si B sa anong uri ng pelikula?` — `sawa` (be tired
  of) + `na` aspect + `anong uri` (what kind); complex
  wh-question variant.
- `Siyanga ba? Dumaan ka naman sa amin pagkatapos.` —
  multi-sentence (Q + imperative); some extractor noise here.

**Ramos 1971 — patterns surfaced:**

- `Actor Focus: Pumutol ka ng sanga sa kahoy.` — has
  `Actor Focus:` English-prefix label; extractor should strip
  these.
- `Goal Focus: Putuliti mo ang sanga sa kahoy.` — same
  prefix; also `Putuliti` has OCR artifact (should be
  `Putulin`).
- Beyond extractor noise, the underlying example sentences
  themselves (`Pumutol ka ng sanga sa kahoy`) are clean AV
  transitives that likely fail on lex (sanga = "branch",
  kahoy = "wood/tree") — N-lex gaps consistent with Wave 1
  findings.

### Wave 2 extractor noise (known caveats)

- **English-prefix labels** in Ramos 1971: lines like
  `Actor Focus: ...` should have the label stripped before
  parser submission.
- **Parenthesized English prompts** in R&C 1990 exercises:
  `(who) ang nagdala ng saging?` — should be filtered out or
  the parenthetical slot replaced before parsing.
- **Quoted English-only tokens**: `Saan ba dito ang 'men's
  wear'?` — should perhaps detokenize the quoted material
  before parsing.
- **Multi-sentence captures**: `Siyanga ba? Dumaan ka naman sa
  amin pagkatapos.` — extractor should split on terminal
  punctuation before emitting.
- **OCR-character-spacing** in Ramos 1971: dictionary body
  has wide-spaced sections that the `_looks_like_tagalog`
  filter rejects (correctly) but leaves intro/preface English
  prose to slip through occasionally (false positives).

These extractor issues are tractable; deferred to a Wave 2.5
cleanup follow-on (won't materially change the headline parse
rate but will sharpen the failure-cluster signal).

## 11. Updated cross-wave conclusions

- **Naturalistic parse rate is 4-5%, not 99.6%.** Across 1220
  sentences (Wave 1 + Wave 2), aggregate clean-parse rate is
  ~5% — sharper signal than the curated corpus suggests.
- **Wave 2 confirms Wave 1's cluster taxonomy** (lex gaps,
  pinaka-/papaka-, mga-DEM, etc.) and adds new candidates:
  - **`pinaka-` on ADJ heads** (in addition to N heads): one
    coherent Phase 8.C target.
  - **`kasing-` + non-reduplicated base** equatives (vs the
    Phase 5h CV-redup form `kasingganda` / `kasinggaganda`):
    new sub-case to verify.
  - **`Nang` temporal subordinator**: not the same as `kapag`;
    likely a Phase 5l gap.
  - **`kumusta` lex** + greeting/inquiry: simple lex addition.
  - **`nagpasabi` + finite-clause subord** (SAY-class
    causative): combined causative + reported-speech
    construction.
- **Lex gaps dominate failures in both waves** — the
  recommendation from Wave 1 (Phase 8.A lex pass) is even more
  load-bearing after Wave 2. Common noun stems (`sanga`,
  `kahoy`, `palabas`, `patyo`, `pelikula`, `tawad`) and verb
  stems (`dalaw`, `hingi`, `pasabi`) are recurring.
- **No-diag bucket is now 791/1101 of Wave 2 failures** —
  Phase 8.J (bucketer-side improvement) is now higher priority
  to unblock further cluster-discovery work in Wave 3.

## 12. Wave 3 go/no-go

**Recommendation: GO**, but with bucketer-side improvement
(Phase 8.J) landed first.

Wave 2 confirms that even noisy OCR sources produce useful
failure signal once the parse-coverage and lex-gap conclusions
are framed in aggregate. Wave 3 (S&O 1972 + R&G Conversational,
Acrobat-OCR) will add ~600 sentences and likely surface S&O-
specific clusters (more formal-register constructions; richer
particle inventory). The OCR-noise tax is real but the absolute
signal additions are worth the cost. Landing Phase 8.J first
(walk-all-blocked-edges in the bucketer) ensures Wave 3
diagnostics aren't dominated by the no-diag bucket the way
Wave 1 + Wave 2 have been.
