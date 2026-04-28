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
