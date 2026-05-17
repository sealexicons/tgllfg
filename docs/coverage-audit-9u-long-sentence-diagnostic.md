# Phase 9.U — Long-sentence diagnostic deep-dive (B4)

> **Status:** Phase 9.U diagnostic; no grammar/lex changes. Categorizes
> the 9–12-word audit-failure pile into root-cause clusters and assigns
> each cluster to a closure follow-on (9.V, 9.W, or 9.X.pre-1) per the
> Phase 9 plan-of-record §3.5 (Bucket B4).

## 1. Methodology

The Phase 9 plan-of-record §3.5 directs B4 sub-PRs to "pick a length-
bucket (9–12, 13–20) and a specific shape, then diagnose root cause."
9.U is the first B4 entry — diagnostic only — and the bucket choice is
**9–12 words** (per plan §3.5 first-bucket suggestion).

Methodology:

1. **Filter** the audit's `wave1+2+3` parse-results JSONL to sentences
   where `bucket` ∈ {`zero-parse-fragment`, `zero-parse-no-fragment`,
   `tokenizer-fail`} AND whitespace-token-count ∈ [9, 12].
2. **Partition** by `oov_tokens` presence: NO-OOV (all-known-vocab —
   pure cascade) vs. WITH-OOV (lex-pressure-driven cascade).
3. **For each NO-OOV failure**, re-run through the parser, inspect
   diagnostics, propose a root cause, and group into clusters.
4. **For WITH-OOV**, characterize the OOV distribution to judge
   whether closures cluster on a few lemmas (a focused lex sweep) or
   spread thinly across a long tail (no B1 reopen warranted).
5. **Map** each cluster to a follow-on sub-PR per the plan.

## 2. Length-bucket distribution (full corpus, 2327 sentences)

```text
   2 words:    4
   3 words:  175  ████████
   4 words:  593  █████████████████████████████
   5 words:  515  █████████████████████████
   6 words:  378  ██████████████████
   7 words:  251  ████████████
   8 words:  179  ████████
   9 words:  102  █████
  10 words:   60  ███
  11 words:   33  █
  12 words:   13
  13–25 words: 24
```

The 9–12 word bucket has 208 sentences total; 200 (96.2%) are
failures (vs the 84.1% corpus-wide failure rate at the 15.94% seeded
baseline). The bucket is failure-skewed.

## 3. Partition of 200 9–12-word failures

| Subset | Count | Share |
| --- | ---: | ---: |
| **NO-OOV (pure cascade)** | 12 | 6.0% |
| **WITH-OOV (lex pressure ± cascade)** | 188 | 94.0% |

Bucket subtype: 157 (78.5%) `zero-parse-fragment` (partial coverage,
chart yields fragments); 43 (21.5%) `zero-parse-no-fragment` (chart
admits nothing at all).

Diagnostic-kind histogram (9–12 word failures only):

| Diagnostic | Count |
| --- | ---: |
| `constraint-failed` | 484 |
| `existential-failed` | 74 |
| `lmt-mismatch` | 41 |
| `completeness-failed` | 34 |
| `coherence-failed` | 20 |
| `neg-existential-failed` | 18 |
| `atom-mismatch` | 2 |

## 4. NO-OOV failure pile (12 sentences) — root-cause clusters

All 12 sentences are listed below with cluster assignment and proposed
closure target.

### Cluster B — sentence-initial topic/subord + COMMA + main S

5 sentences. The matrix S has a comma-separated dislocated head
(SubordClause / PP / NP / ADV) followed by the matrix clause. The
existing rule

```text
S → SubordClause PART[LINK=AY] S       (cfg/subordination.py:366)
```

handles the `ay`-linked variant (`Kung uulan ay hindi ako pupunta.`)
but not the COMMA-linked variant. The fronted-ADV `ay`-link
counterpart (`Kahapon ay ...`) is also missing — only NP-pivot
ay-fronting exists.

1. `wave1 :: ANG PAMILYA/sent-1` — `Una sa lahat, ang isang
   Pilipino ay bahagi ng kanyang pamilya.`
   Shape: NP/PP-topic + COMMA + S (S inner is itself ay-fronted).
2. `wave2-rc1990 :: Ch5/Transition Phrases/sent-661` — `Bago ko
   malimutan, nakita mo ba si Jonathan sa miting?`
   Shape: SubordClause[TEMP_BEFORE] + COMMA + S.
3. `wave3-so1972 :: page-447/sent-689` — `Kahapon ay sumulat ng
   liham kay Maria si Juan.`
   Shape: ADV[ADV_TYPE=TIME] + ay + S (ay-link variant of cluster B).
4. `wave3-so1972 :: page-480/sent-767` — `Kung dinadalaw ko siya,
   palagi akong nagdadala ng regalo.`
   Shape: SubordClause[COND] + COMMA + S.

**Closure target: 9.V** — single construction class. Three rule
shapes:

```text
S → SubordClause PUNCT[COMMA] S                # COMMA variant of sub:366
S → NP[CASE=NOM] PUNCT[COMMA] S                # fronted NP/PP topic
S → ADV[ADV_TYPE=TIME] PART[LINK=AY] S         # fronted-ADV ay-pattern
```

Both shapes carry `(↑ TOPIC) = ↓1` and `↓1 ∈ (↑ ADJUNCT)`, matching
the existing subord-ay rule's f-structure shape.

### Cluster E — AV-CAUS reporting verb with na-S OBJ

1 sentence.

`wave2-rc1990 :: Ch5/Exercises/sent-866` — `Nagpasabi ang boss ko
na hindi siya papasok sa trabaho.` Diagnostic:
`completeness-failed: PRED 'SABI' requires 'OBJ' but it is not
present`.

`nagpasabi` is the AV-CAUS form of `sabi` "say". The `na-S` clause
("that he won't come to work") should bind as OBJ (the
quoted/reported content), but the current `sabi` lex profile expects
NP-OBJ. Verified: even `Nagsabi ang boss ko na hindi siya papasok
sa trabaho.` (replacing `nagpasabi` with plain `nagsabi`) fails — the
gap is the SAY-class na-S complement profile, not the CAUS layer.

**Closure target: 9.W** — new SAY-class lex profile admitting `na-S`
as OBJ (parallels Phase 8.H's `_AV_CAUS_INDIRECT_FLAT` shape: one
new intrinsic profile, one matrix rule, and lex updates for the
reporting-verb roots `sabi` / `tanong` / `salita`).

### Cluster A/H — compound time NP / pag-temporal subord

3 sentences. Two related shapes:

- (sent 5) `wave2-rg-intermediate :: page-13/prose/sent-53` — `Kasi
  ho puno na ang mga bus pag tanghali na.`
  Shape: matrix S + `pag` + bare-N[SEM_CLASS=TIME] + `na`.
- (sent 6) `wave3-so1972 :: page-441/sent-676` — `Sila rin ay sasayaw
  ng pandanggo bukas ng gabi.`
  Shape: compound time NP `bukas ng gabi` "tomorrow evening".
- (sent 7) `wave3-so1972 :: page-541/sent-962` — duplicate of
  sent-676.

For sent-53: `pag tanghali na` "when it's noon" is a bare-N temporal
subordinate (`pag` is COMP_TYPE=COND per particles.yaml:1666, but in
this construction it carries a temporal sense and admits a bare-N
predicate complement instead of a full S body).

For sent-676/962: `bukas ng gabi` is a compound time NP — fronted-ADV
`bukas` "tomorrow" + linker `ng` + bare-N `gabi` "evening" with a
specific-time-of-day reading. Verified: stripping `ng gabi` still
fails (`Sila rin ay sasayaw ng pandanggo bukas.` → 0) because the
matrix-final `bukas`-ADV isn't a recognized adjunct shape either —
this case has TWO gaps stacked.

**Closure target: 9.W** — three rules:

- `SubordClause → PART[COMP_TYPE=COND, LEMMA=pag]
  N[SEM_CLASS=TIME] PART[LEMMA=na]` — the `pag tanghali na` bare-N
  predicate body.
- `AdvP → ADV[ADV_TYPE=TIME, DEIXIS_TIME=FUT] PART[LINK=NG]
  N[SEM_CLASS=TIME]` — the `bukas ng gabi` compound.
- `S → S AdvP[ADV_TYPE=TIME]` clause-final attachment scoped via
  SEM_CLASS — currently FREQUENCY+INDEF only (discourse.py:155, 186);
  expand to TIME.

If 9.W gets crowded, split clusters A/H + E into two separate
sub-PRs — clusters are independent.

### Cluster G — PANAHON clitic-merger `'y`

1 sentence.

`wave1 :: PANAHON/sent-18` — `Mangyari'y mahirap talagang kumilos
kapag nasa tuktok ang araw.` Shape: clitic-`'y` ay-merger after
C-final root.

`Mangyari'y` is the phonologically-reduced `mangyari + ay` —
analogous to `Maria't` for `Maria at`. The existing Phase 5n.C.2
gapping pre-pass (`text/clitics.py`) handles `'t` but not `'y`.

**Closure target: 9.X (PANAHON cluster)** — this is one of the
24-row PANAHON cluster items; close it as part of the dedicated
PANAHON diagnostic+closure sub-PR, not 9.U-cascade follow-ons.

### Defer — embedded quotes / parentheticals / 3-conj N coord

3 sentences. Each has a construction outside the cascade scope
established by Phase 9 ≥80% target — punctuation-delimited
inline-disambiguation forms and unusual coord shapes.

- (sent 8) `wave1 :: ANG PAMILYA/sent-5` — `Ang pinakaubod ng
  pamilyang Pilipino ay ang ama, ina at mga anak.`
  Defer rationale: 3-conj `N , N at N` coord. Phase 5n.A L85 closes
  4-conj; the 3-conj-with-Oxford-comma variant lands cleanly in
  Phase 9.Z regression fixture if/when it surfaces broadly.
- (sent 9) `wave2-rc1990 :: Ch5/Exercise/sent-735` — `Sumulat si
  Derek kay Marvin bago ito (si Marvin) umalis.`
  Defer rationale: parenthetical disambiguator `(si Marvin)` —
  extra-grammatical annotation, not a real construction class.
- (sent 10) `wave2-rg-intermediate :: page-198/numbered/sent-1372`
  — `Bakit raw ang buhay sa Amerika ay 'mahirap na masarap?'`
  Defer rationale: embedded quote — single-quote-bracketed
  predicate within a wh-question.

### Cluster summary

| Cluster | Sents | Closure |
| --- | ---: | --- |
| **B — fronted topic + COMMA / ay + S** | 4+1ay | **9.V** |
| **E — SAY-class V + na-S OBJ** | 1 | **9.W (or split)** |
| **A/H — compound time NP / pag-temporal** | 2 (3 incl. duplicate) | **9.W (or split)** |
| **G — PANAHON `'y` clitic** | 1 | **9.X (PANAHON cluster)** |
| **Defer — quotes / parentheticals / 3-conj** | 3 | Phase 9.Z fixture or later |

Direct yield (9.V + 9.W combined): ≥ 7 of 12 NO-OOV closures (58%);
generalization potential extends to shorter sentences (the same
construction classes will close some <9-word failures too — not
quantified here, but the `xwave-report` 242 NO-real-OOV pile is a
likely upper bound).

## 5. WITH-OOV failure pile (188 sentences) — characterization

### OOV-multiplicity

| OOV tokens / sent | Sentences |
| ---: | ---: |
| 1 | 27 |
| 2 | 56 |
| 3 | 55 |
| 4 | 27 |
| 5 | 14 |
| 6 | 3 |
| 7 | 4 |
| 8+ | 2 |

Median: 3 OOV tokens per sentence; 70.7% have ≥ 2 OOVs.

### Top-30 most-frequent OOV tokens in this bucket

```text
gawin                       6   |   how                         2
dindo                       4   |   buhat                       2
bill                        4   |   new                         2
nanalo                      4   |   york                        2
pag-aaral                   3   |   digna                       2
the                         3   |   angela                      2
is                          3   |   inihulog                    2
pinaalis                    3   |   roberta                     2
dan                         3   |   faye                        2
esper                       3   |   and                         2
naging                      3   |   helen                       2
jimmy                       3   |   nina                        2
maling                      2   |   bert                        2
maging                      2   |   nanghuli                    2
rig                         2   |   pinaranas                   2
mike                        2   |
```

Composition: proper names (Dindo, Dan, Esper, Jimmy, Mike, Digna,
Angela, Roberta, Faye, Helen, Nina, Bert, Bill); English code-switch
fragments (the, is, how, new, york, and); paradigm-cell or imperative
forms of known roots (gawin = OV irregular of `gawa`; pinaalis,
naging, maging, maling, pinaranas, inihulog — all derived forms of
known roots — would close if the missing paradigm cell were wired).

### Single-OOV-token failures (27 sentences)

The most likely-to-close-with-one-lex-add subset. Composition (manual
classification, see `/tmp/9u_oov_dist.log`):

- **Common Tagalog lex gap (~12):** `gitna` "middle", `ibabaw` "top",
  `halaga` "value", `ilaw` "light", `masama` "bad", `samantalang`
  "while", `iksamen` "exam" (loan), `Maghimagas` "have dessert",
  plus 4 more.
- **Paradigm-cell gap (root present) (~8):** `Natawa` (magka-AV of
  `tawa`), `bibilhin` (OV-future of `bili`), `Ibigay` (i-OV
  imperative of `bigay`), `pinaniniwalaan` (LV-progressive of
  `paniwala`), `nagbibilang` (AV-progressive of `bilang`),
  `inihulog` (i-OV-PFV of `hulog`), `matutuyo` (ma-future of
  `tuyo`), `maaliw` (ma-AV of `aliw`).
- **OCR / typo artifact (4):** `Bako` → `Bago`, `tirvdahan` →
  `tindahan`, `siua` → `siya`, `Sunudat` → `Sumulat`.
- **Proper name / loan / punct (3):** `Digna`, `CDs`, `etc`.

**Observation: B1 was officially closed at 9.J, but the audit shows
~20 likely-one-add closures remain in 9–12 word sentences.** These
are not "B1 leftovers" in the procedural sense (the B1 sweep
exhausted top-frequency OOV tokens) but represent the natural tail
where length × per-token-OOV-prob creates compound coverage gaps.

### Recommendation on OOV-blocked tail

Two options, in order of plan-of-record alignment:

1. **No 9.X.pre-1 lex sweep.** Treat the 9–12 OOV tail as Phase 9.Z's
   regression-fixture domain — when 9.Z sources naturalistic-tier
   exemplars, it'll surface the highest-yield lex adds organically.
   **Recommended** unless 9.V/9.W audit pins surface OOV blockers
   (per user directive 2026-05-17 — inline lex resolution in subPR
   if blocking).
2. Insert **9.X.pre-1** as a small lex+paradigm sub-PR closing the
   ~12 common-Tagalog single-OOV gaps (`gitna` / `ibabaw` / `halaga`
   / `ilaw` / `masama` / `samantalang` / `iksamen` / `Maghimagas` +
   the 3 OCR fixes in the harvest extractor). Expected yield: ~10–15
   direct sentence closures across all length buckets (not just
   9-12), since these are common words. **Defer**: if 9.V/9.W
   surface enough of these as in-scope blockers, no separate sub-PR
   needed.

## 6. Recommended follow-on sub-PRs

**9.V (Bucket B4) — Cluster B.** Sentence-initial fronted topic +
COMMA/ay + main S. Three rules: `S → SubordClause PUNCT[COMMA] S`,
`S → NP[CASE=NOM] PUNCT[COMMA] S`, `S → ADV[ADV_TYPE=TIME]
PART[LINK=AY] S`. Effort: high (~3-5 commits). Direct yield in
9-12 bucket: 4 sents (sent-1, sent-661, sent-689, sent-767).
Generalization: any short fronted ADV / kung-S / pag-S / bago-S /
pagkatapos-S / topic-NP across all length buckets.

**9.W (Bucket B4) — Clusters E + A/H.** SAY-class V + na-S OBJ
profile (Cluster E); compound time NP + pag-temporal subord
(Cluster A/H). Effort: high (~4-6 commits) — may split into two
sub-PRs if scope conflicts. Direct yield in 9-12 bucket: 3 sents
(sent-866, sent-676/962, sent-53).

**9.X (Bucket B5) — PANAHON cluster.** 24-row diagnostic + closure
(per plan §3.6). Closes Cluster G as one entry. Effort: high
(~3-5 commits). Direct 9-12 yield: 1 sent (PANAHON/sent-18); full
PANAHON yield assessed separately within 9.X.

**9.X.pre-1 (optional).** Common-Tagalog single-OOV closures
(`gitna`, `ibabaw`, `halaga`, `ilaw`, `masama`, `samantalang`,
etc.). Effort: small (~1-2 commits). Expected yield: ~10-15
across all length buckets, not just 9-12. **Defer this unless
9.V/9.W audit pins surface OOV blockers** that warrant inline
resolution per the user's no-deferrals directive.

Deferred: sent-3 (3-conj `N , N at N` coord), sent-5
(parenthetical disambiguator), sent-7 (embedded quote). All routed
to Phase 9.Z regression fixture (parse-or-pin per future surface).

## 7. Reproduction

```bash
# Extract 9-12 failure pile + per-corpus + diag-kind histogram
python /tmp/probe_9u_bucket.py    # writes /tmp/9u_failures.jsonl

# Inspect 12 NO-OOV failures
python /tmp/probe_9u_no_oov.py    # writes /tmp/9u_no_oov.log

# Verify each cluster against current grammar
hatch run python /tmp/probe_9u_cascade_verify.py

# OOV-distribution + single-OOV pile
python /tmp/probe_9u_oov_dist.py  # writes /tmp/9u_oov_dist.log
```

Probes are checked into `/tmp` per the project's pre-authorized scratch
convention; they read from `data/tgl/exemplars/wave*-parse-results.jsonl`
and reproduce all tables above. Re-run after each B4 sub-PR ships to
track the 9–12 bucket's pile size + cluster shifts.
