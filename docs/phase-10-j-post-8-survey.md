<!-- Copyright (c) 2025-2026 G & R Associates LLC -->
<!-- SPDX-License-Identifier: MIT OR Apache-2.0 -->

<!-- markdownlint-disable-file MD013 -->

# Phase 10.J.post-8 — wave-1 ZPF residue survey

## Frame

The post-7.[1-7] arc closed all four `pending_closure: post-10`
xfailed exemplars and brought wave-1 PANAHON to **94/123**
deterministic (first zero-xfail Phase 10.J test-both run). The
remaining wave-1 residue is **29 sentences**: 27 ZPF, 1 ZPNF,
1 timeout.

Per the on-resume roadmap, post-8 is a discovery sub-PR — its
deliverable is a triaged residue list plus 1–2 concrete
follow-on candidates with mechanism classes (chart / pipeline-
split / lex / paradigm / tokenizer). No new parser code lands
in this sub-PR.

## Method

For each residue sentence:

1. Read tokens via `Token` → `analyze_tokens` to identify _UNK
   surfaces (lex/paradigm gaps).
2. Run `parse_text` on the original full sentence and on
   progressively-truncated prefixes to identify the minimal
   failing form.
3. Classify the failure into a construction class.

Probes that produced this survey:

* `tmp/probe_post8_wave1_residue.py` — bucket count + ZPF list.
* `tmp/probe_post8_minfail.py` — minimal-failing-prefix probes
  for cluster representatives.
* `tmp/probe_post8_lex.py` — lex-status probe for paradigm /
  redup / tokenizer gap candidates.

## Per-sentence triage

`Loc` = locator; `Cluster` = column letter in the cluster table
below. Status `Z` = ZPF; `N` = ZPNF; `T` = parse-timeout.

| Loc | Status | Cluster | Triage notes |
| --- | --- | --- | --- |
| PAG-AARAL/sent-1 | Z | C, B (multi) | `ay madali sa ilang tao at napakahirap para sa iba` — predicative-ADJ `madali` ay-fronted with ADJ-AND-ADJ post-ay coord (`madali ... at napakahirap`); `napakahirap` (paka-intensive) lex'd as `_UNK` (paradigm) |
| PAG-AARAL/sent-2 | Z | A | `Sino ang nahihirapan at sino ang nadadalian?` — `nadadalian` is `_UNK` (na-CV-X-an LV-pot imperf paradigm gap); doubled Q-ay-fronted `Sino..ang..at sino..ang..` |
| PAG-AARAL/sent-3 | Z | A | `Ang nahihirapan ay mga taong mahiyain at mahina ang loob.` — predicative-ADJ ay-fronted; `mahiyain` and `mahina ang loob` (idiom) |
| PAG-AARAL/sent-4 | Z | E, A | `Ayaw nilang magbukas ng bibig dahil natatakot magkamali.` — clause-final `dahil`-SubordClause without comma + `magkamali` (mag-ka-X paradigm gap) + V[ma]+V[INF] control nesting |
| PAG-AARAL/sent-5 | Z | A | `Ayaw nilang mapintasan ang maling pagbigkas o maling pagsasamasama ng salita.` — `mapintasan` (ma-X-an LV passive), `pagsasamasama` (CV-redup gerund), `pagbigkas` (NOM); plus Ayaw-control |
| PAG-AARAL/sent-6 | Z | B, A | `Hindi sila magsasalita hangga't sa palagay nila ay tamang-tama na ang sasabihin nila.` — `hangga't` apostrophe-attached `'t` (B) + `tamang-tama` (REDUP=FULL intens ADJ; A) + complex inner-S structure |
| PAG-AARAL/sent-7 | N | A | post-10 explicit target — `nadadalian` + `nahihiyang` + `magkamali` all paradigm gaps |
| PAG-AARAL/sent-8 | Z | B, A | `Kahi't balubaluktot, pinipilit nilang magsalita.` — `Kahi't` apostrophe-`'t` (B) + `balubaluktot` (CV-CV-redup ADJ; A) + `baluktot` ADJ lex gap (A) |
| PAG-AARAL/sent-10 | Z | A | `Madali ring matuto ang mga taong mahilig makipagkaibigan.` — `matuto` AV-INTR (might be IN), `mahilig` ADJ → V[INF] control, `makipagkaibigan` (makipag-X-an paradigm gap) |
| PAG-AARAL/sent-11 | Z | D | `Dahil gusto nilang makipagkaibigan sa mga mamamayan ng bayang kanilang binibisita, nagsasalita sila sa salitang banyaga.` — long fronted-`Dahil` SubordClause with multi-PP inner + RC; forest-density |
| PAG-AARAL/sent-12 | Z | OUT | `Kahit a la 'ako Tarzan, ikaw Jane'.` — code-switch (`a la`) + named entities + quoted speech — out-of-scope |
| PAG-AARAL/sent-13 | Z | G | `Anong uring mag-aaral (estudyante) kayo?` — parenthetical clarification `(estudyante)` |
| PANAHON/sent-10 | Z | D | `Sa panahon ding ito dinaraos ang mga piyesta at siyempre pa, ang Mahal na Araw para sa mga Kristiyano.` — long PP-fronted + mid-S `siyempre pa,` discourse marker + NP coord (`ang mga piyesta at ... ang Mahal na Araw`); short variant `Sa panahon ding ito dinaraos ang piyesta.` parses |
| PANAHON/sent-28 | Z | H | `Kasabay ng bagyo ang pagpatak ng tinatawag na 'monsoon'.` — `kasabay ng` PP-headed (ADJ+OBL) construction; `tinatawag na 'X'` RC with quoted complement |
| PANAHON/sent-36 | Z | D | `Puno pa rin ang mga patubigan sa bukid kaya pagkaani ng palay na itinanim noong Hunyo, sisimulan na ang ikalawang pagtatanim.` — long `kaya`-fronted second clause with multi-PP modifiers and inner RC |
| PANAHON/sent-41 | Z | H | `Kaya nga may sinasabing oras Pilipino -- na ang ibig sabihin ay laging huli.` — em-dash + `na S`-clause continuation + idiom `ibig sabihin` |
| PAMILYA/sent-2 | T | D | `Kahit na siya ay doktor, manunulat, siyentipiko o ano pa man, nananatili siyang ama o anak, pamangkin o apo sa loob ng kanyang pamilya.` — long fronted-Kahit-S with bare-comma N enumeration + `ano pa man` quantifier + V-INF + NP-DISJ; forest density past 11s SIGALRM |
| PAMILYA/sent-3 | Z | C | `Dito ay iba ang kanyang katungkulan at ang pagkakaklala sa kanya.` — `Dito ay` AdvP-fronted-ay parses short, but the post-ay `iba ang X at ang Y` is two-`ang`-NP coord (NP-AND-NP) that breaks the parse |
| PAMILYA/sent-4 | Z | C, I | `Sa lahat at oras ay pangunahin sa kanya ang kanyang tungkulin bilang kasapi ng isang pamilya.` — likely OCR (`Sa lahat at oras` should be `Sa lahat ng oras` "at all times"); + `bilang kasapi` ROLE-PP; PP-headed ay-fronted |
| PAMILYA/sent-7 | Z | A | `Siya ang nasusunod at nagpapasya para sa pamilya.` — `nasusunod` (ma-CV-X LV-pot imperf paradigm gap) + V-V coord (`nasusunod at nagpapasya`) |
| PAMILYA/sent-8 | Z | C, K | `Sa kabilang dako ay tungkulin niyang pakainin, bigyan ng matitirhan at pag-aralin ang mga miyembro ng kanyang pamilya.` — PP-headed ay-fronted + multi-V[OV] coord with shared OBJ |
| PAMILYA/sent-9 | Z | I | `Kaya siya ang nagtratrabaho at kumikita ng pera.` — `Kaya siya` discourse + V-V coord (`nagtratrabaho at kumikita`) with shared SUBJ |
| PAMILYA/sent-10 | Z | J | `Ang ina naman ang bahala sa bahay at sa pag-aalaga ng mga bata.` — NP-naman-NP equational + PP-PP coord (`sa bahay at sa pag-aalaga`) post-predicate |
| PAMILYA/sent-11 | Z | I, K | `Siya ang humahawak ng pera ng pamilya at pinagkakasya ito sa panganga-ilangan ng pamilya.` — V-V coord with voice-mismatch (AV `humahawak` + OV `pinagkakasya`); `pinagkakasya` paradigm gap |
| PAMILYA/sent-14 | Z | B, J | `Kasama rin sa pag-aalala ng pamilya ang lolo at lola, ang mga kapatid ng ama at ina, lalo na't ang mga ito'y nakababata.` — `lalo na't` (B), `ito'y` (B), three-way NP enumeration with appositive `lalo na't ang mga ito'y nakababata` (relative-clause-like discourse coord) |
| PAMILYA/sent-15 | Z | B, J | `Kadalasa'y sama-sama sa isang bahay ang lolo at lola, ang ama at ina at ang mga anak.` — `Kadalasa'y` (B), three-way ang-NP coord with bare-comma (J/post-7.7-extension) |
| PAMILYA/sent-16 | Z | B | `Kung minsa'y kapisan din ang wala pang asawang kapatid ng ama o ina.` — `Kung minsa'y` (B); long fronted clause with `pa` clitic in NP + RC + N coord with `o` |
| PAMILYA/sent-17 | Z | B | `Kapag ganitong kumpleto ang pamilya'y tatlong salin-lahi ang nakatira sa iisang bahay.` — `pamilya'y` (B); fronted Kapag-SubordClause + post-`'y` NUM-N-LINKER continuation |
| PAMILYA/sent-18 | Z | A | `Tulung-tulong sila sa mga gawain at sa pahahanap-buhay.` — `Tulung-tulong` CV-redup collaborative ADJ paradigm gap (A); also `pahahanap-buhay` (pag-CV-X-buhay compound) |

## Cluster summary

Sentences are listed under their **primary** cluster (most
sentences have secondary contributors — see triage notes
above). Counts here reflect the primary cluster only;
secondary contributions roll up in the per-cluster sub-PR
scoping.

| Cluster | Wave-1 (primary) | Description |
| --- | --- | --- |
| A — paradigm / redup gaps | 7 + (overlap 5) | `nadadalian`, `nahihirapan` (full-sentence), `nahihiya`, `magkamali`, `mahiyain`, `mapintasan`, `pagsasamasama`, `pagbigkas`, `makipagkaibigan`, `nasusunod`, `pinagkakasya`, `tamang-tama` (INTENS), `balubaluktot`, `baluktot` (ADJ lex), `tulung-tulong`, plus AV_ABSOL gaps on `sunod` (`Sumusunod siya.` ZPFs) and `kilala` (`Nakikilala ko siya.` ZPFs) |
| B — `'y` / `'t` apostrophe contractions | 6 | `Kadalasa'y`, `minsa'y`, `pamilya'y`, `ito'y`, `hangga't`, `Kahi't`, `na't` — all tokenizer-level (currently every form returns `_UNK` from `analyze_tokens`) |
| C — PP / AdvP / two-`ang`-NP coord ay-fronted | 3 + (overlap 2) | `Dito ay iba ang X at ang Y` (PAMILYA sent-3); `Sa kabilang dako ay V[OV]+...` (PAMILYA sent-8); `Sa panahon ding ito V SUBJ at ...` (PANAHON sent-10) — short forms parse; failure point is NP-AND-NP coord at the NP[CASE=NOM] level (post-predicate) |
| D — long-sentence forest-density | 4 | PAG-AARAL/sent-11, PANAHON/sent-10, PANAHON/sent-36, PAMILYA/sent-2 (timeout) — sentences whose canonical parse may exist but exceeds the 5000 cap or 11s SIGALRM |
| E — clause-final SubordClause without comma | 1 | PAG-AARAL/sent-4 (`...dahil natatakot magkamali.`) — c12 currently only has `S → S PP[PREP_TYPE=REASON]`, not `S → S SubordClause[dahil]` |
| F — paka- intensive ADJ | 1 (in sent-1) | `napakahirap` — paka-X paradigm gap (rolls into A) |
| G — parenthetical clarification | 1 | PAG-AARAL/sent-13 `mag-aaral (estudyante)` |
| H — em-dash / quoted complement | 2 | PANAHON/sent-28 (`tinatawag na 'monsoon'`), PANAHON/sent-41 (em-dash + `na S`) |
| I — discourse-fronted + V-V coord | 2 + (overlap) | `Kaya siya...` (PAMILYA sent-9), interactions with K |
| J — NP-naman-NP / PP-AND-PP / 3-way NP coord | 2 + (overlap 2) | PAMILYA/sent-10 (`Ang ina naman ang bahala sa X at sa Y`); PAMILYA/sent-14/15 (three-way ang-NP enumeration with bare-comma — extension of post-7.7) |
| K — V-V coord with voice mismatch | 2 + (overlap) | PAMILYA/sent-8, PAMILYA/sent-11 — multi-V coord with AV/OV/DV voice differences and shared SUBJ |
| OUT — code-switch / named entities | 1 | PAG-AARAL/sent-12 |

## Recommended follow-on sub-PRs

Ordered by expected wave-1 yield × tractability. Each entry
includes its mechanism class (per the structure-first
directive in `tgllfg-phase-10.md` §6) and estimated commit
count.

### post-8.1 — `'y` / `'t` apostrophe-clitic tokenizer expansion

**Class**: tokenizer (`src/tgllfg/text/`) + lex-side `LEMMA`
routing for the truncated stems.

**Mechanism**: in tokenization, recognise the productive
clitic-contraction patterns and split:

* `<stem>'y` → `<stem>` + `ay` (e.g., `pamilya'y` →
  `pamilya ay`; `Kadalasa'y` → `Kadalasan ay` — note the
  pre-clitic `-an → -a` truncation on adverbs like
  `kadalasan` / `minsan`; vowel-final stems pass through
  unchanged).
* `<stem>'t` → `<stem>` + `at` (e.g., `na't` → `na at`;
  `hangga't` → `hangga at` — note `hangga` is already a
  PART entry, parallel to `hanggang`; `Kahi't` → `Kahit`
  truncation needs `Kahit` lemma routing).

The non-trivial part is the `-an → -a` truncation: `Kadalasa`
and `minsa` are not lex; the tokenizer must restore the `-n`
before lookup (or the lex must learn the truncated forms with
`LEMMA: <full-form>` pointers).

**Wave-1 yield**: 4–6 sentences (PAMILYA/sent-14/15/16/17,
likely PAG-AARAL/sent-6, possibly PAG-AARAL/sent-8). Audit
reach across waves 2-5 likely substantial since apostrophe-
contractions are productive in transcribed speech and reference
prose.

**Risk**: tokenization changes touch every parse — needs
careful multi-wave audit. Mid-token apostrophe must not be
confused with apostrophe-as-punctuation (`a la 'ako Tarzan'`
in PAG-AARAL/sent-12).

**Effort**: ~4-6 commits (tokenizer + lex routing + tests +
multi-wave audit).

### post-8.2 — two-`ang`-NP coord at NP[CASE=NOM] level

**Class**: chart rule (`src/tgllfg/cfg/coordination.py` or
`nominal.py`).

**Mechanism**: add binary `NP[CASE=NOM] → NP[CASE=NOM]
PART[COORD=AND] NP[CASE=NOM]`, gated on `¬ (↓1 COORD)` to
prevent nesting in the bare-comma N coord pattern from
post-7.7. Parallel to the existing `N → N PART[at] N` (which
shares one `ang`) but at the NP level (each conjunct has its
own `ang`).

Probe-confirmed: `Iba ang katungkulan at ang pagkakaklala.`
ZPFs. The chart currently composes `ang X at Y` via
`NP → ADP N[COORD=AND]` (shared `ang`) but has no path for
`ang X at ang Y`.

**Wave-1 yield**: 2-3 sentences (PAMILYA/sent-3, PAMILYA/sent-15
likely, plus possibly PANAHON/sent-10's
`ang mga piyesta at ... ang Mahal na Araw`).

**Risk**: chart-state count increase — needs forest-density
audit on sent-16 (§6.2 guard). Defensive `¬ (↓ COORD)` gate
to prevent nesting (lesson from post-7.7).

**Effort**: ~3-5 commits.

### post-8.3 — clause-final `dahil`-SubordClause (no comma)

**Class**: chart rule (`src/tgllfg/cfg/subordination.py` or
`discourse.py`).

**Mechanism**: add `S → S SubordClause[COMP_TYPE=REAS]` (no
comma daughter), parallel to post-7.2's clause-final
`S → S PP[PREP_TYPE=REASON]` but with an `S` daughter inside
the SubordClause rather than an `NP[CASE=DAT]` inside a PP.
Lifts the c12 deferral on bare clause-final dahil-S that was
parked when post-7 added the comma-required fronted variant.

**Wave-1 yield**: 1 (PAG-AARAL/sent-4); audit reach likely
moderate across waves 2/3/5 since `dahil` is the most common
REASON connector.

**Risk**: needs to disambiguate from the c13 fronted-PP-comma
path (which requires the comma) and from the chart's existing
S-coord rules.

**Effort**: ~2-3 commits.

### post-8.4 — `Sumusunod siya.` / `Nakikilala ko siya.` AV_ABSOL gaps

**Class**: lex (`data/tgl/verbs.yaml`).

**Mechanism**: add `feats: {AV_ABSOL: true}` to the canonical
TR verbs that admit absolutive-AV in narrative contexts (the
pattern from post-7.5's `maneho` and post-7.6's `kuwento`).
Probe-confirmed `Sumusunod siya.` and `Nakikilala ko siya.`
both ZPF — the lex has the forms tagged VERB but they fail
to compose into a complete S without an explicit OBJ.

Candidates surfaced by the wave-1 residue (or implied by it):
`sunod` (follow), `kilala` (recognise/know), `pasiya` (decide),
plus any other TR root surfacing in `Sumusunod siya.`-style
positions.

**Wave-1 yield**: 1-2 sentences (PAMILYA/sent-7 partially,
plus interactions with V-V coord that compound the issue).
Audit reach: likely substantial across narrative-heavy waves.

**Risk**: minimal — additive lex, no chart changes.

**Effort**: ~2-3 commits (lex audit + tests + multi-wave
audit).

### post-8.5 — paradigm-cell expansion (extends post-10)

**Class**: paradigm cells (`data/tgl/paradigms.yaml`) + lex
(`data/tgl/verbs.yaml` / `adjectives.yaml`).

**Mechanism**: extend post-10's planned paradigm engineering
beyond just `na-CV-X-an` / `ADJ→V hiya` / `mag-ka-X` to
include the broader set surfaced by this survey:

* `nasusunod` — same family as `nadadalian` (`na-CV-X` LV-pot
  imperf for INTR roots like `sunod`).
* `pinagkakasya` — `pinag-CV-X` OV-pot imperf (or maybe LV?)
  for `kasya`.
* `mapintasan` — `ma-X-an` LV potentive (might be in
  paradigm; check).
* `pagsasamasama` — CV-redup gerund (`pag-CV-sama-sama`).
* `napakahirap` — `paka-X` intensive ADJ.
* `tamang-tama` — `X-X` redup ADJ (REDUP_SEM=INTENS, may be
  in 10.E.2 already).
* `balubaluktot` — `CV-CV-X` ADJ redup (extends 10.E.2).
* `tulung-tulong` — `CV-X` collaborative (overlaps 10.E
  inventory).
* `mahiyain` — `ma-X-in` ADJ "shy by disposition".
* `pagbigkas` — `pag-X` NOM gerund.

Plus `baluktot` ADJ as a lex addition (basic adjective
"crooked, bent" — surprising omission, used as base for
`balubaluktot`).

**Wave-1 yield**: probably 4-6 sentences if all cells land
(PAG-AARAL/sent-2/3/5/8, PAMILYA/sent-7/18). Likely large
audit reach.

**Risk**: each cell is independent engineering work; some may
not be confirmable from references. Likely splits into
sub-PRs (post-10.A, post-10.B, …) — recommend treating
post-8.5 as a scoping document feeding into a post-10 family
of paradigm sub-PRs.

**Effort**: ~6-10 commits (likely split into multiple sub-PRs).

## Out of immediate scope

* **Cluster D — long-sentence forest density** (PAG-AARAL/
  sent-11, PANAHON/sent-10, PANAHON/sent-36, PAMILYA/sent-2):
  these are §6.2 / Phase 9 deferrals — needs rule-budget
  application similar to post-10.I or chart-narrowing. Park
  pending structure-first wins from post-8.1..5 clearing the
  smaller residues.
* **Cluster G — parenthetical clarification** (PAG-AARAL/sent-13):
  productive but low-yield in wave-1; defer to a dedicated
  parenthetical-handling sub-PR aligned with post-9 OCR
  cleanup (the OCR'd refs have many parens).
* **Cluster H — em-dash and quoted complement** (PANAHON/
  sent-28, PANAHON/sent-41): similar — productive in
  reference prose but isolated in wave-1.
* **Cluster OUT — code-switch** (PAG-AARAL/sent-12): defer
  indefinitely — explicit code-switch parsing is a Phase
  10+/Phase 11 scope decision.

## Process notes

This survey is the third "discovery" exit in the Phase 10.J
extension arc (after post-5 spike-decide and post-7 attestation
survey). The pattern that's emerged:

1. **Run a fresh audit** on the post-N-1 tip.
2. **Triage the residue** by minimal-failing-prefix probes
   (the `tmp/probe_post<N>_*.py` family).
3. **Cluster by construction class**, not by sentence — most
   residue sentences are multi-class compound failures, and
   single-cluster sub-PRs payback more reliably.
4. **Score by audit-reach** — paradigm and lex changes
   typically reach further than chart additions; pipeline
   splits typically reach further than chart rules; chart
   rules reach further than feat-narrowings.
5. **Propose follow-on sub-PRs** with mechanism class +
   estimated effort, then let the user direct.

Carry forward into post-9/post-10 work.
