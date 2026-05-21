# tgllfg/lexicon.py

"""In-process lexicon — per-voice entries for the Phase 4 anchor verbs.

The DB-backed lexicon (Phase 3) lives in ``src/tgllfg/lex/``; this
module is the in-process fallback the parser uses by default. It
holds ``LexicalEntry`` templates per ``(lemma, voice)`` slot, paired
with a-structure / GF-mapping data that drives LMT.

For Phase 4 §7.1 (voice and case extensions), six anchor verbs are
authored across the four-voice system (Kroeger 1993): kain, bili,
basa, sulat, gawa, tapon. Where a voice slot exists for a verb (per
its R&B 1986 affix-class membership), an entry is supplied with:

* ``pred`` — a 2-argument PRED template ``"VERB <SUBJ, OBJ>"``. Three-
  argument predicates (e.g. *bigay* "give" with recipient + theme +
  agent) are deferred to Phase 5 LMT, where the role-to-GF mapping
  is computed from a-structure plus voice rather than authored.
* ``a_structure`` — semantic role names in canonical order. The role
  name varies by verb (AGENT, ACTOR, RECIPIENT, GOAL, CONVEYED, ...);
  Phase 5 reduces these to a finite ontology.
* ``morph_constraints`` — restrictions on the MorphAnalysis the entry
  matches (``VOICE`` and, where transitivity disambiguates, ``TR``).
* ``gf_defaults`` — the role-to-GF mapping the entry contributes for
  this voice. Per the OBJ-uniform analysis (``docs/analysis-choices.md``
  "ng-non-pivot in transitive non-AV → OBJ"), the *ng*-marked
  argument is OBJ in OV / DV / IV, regardless of its thematic role.
"""

from __future__ import annotations

from .common import LexicalEntry, MorphAnalysis
from .lexicon_loader import load_lex_entries


def _entry(
    lemma: str,
    voice: str,
    pred: str,
    a_structure: list[str],
    gf_defaults: dict[str, str],
    *,
    transitive: bool = True,
    intrinsic_classification: (
        dict[str, tuple[bool | None, bool | None]] | None
    ) = None,
) -> LexicalEntry:
    """Build a LexicalEntry. ``transitive`` defaults to True; when
    False, ``morph_constraints`` omits the TR feature so the entry
    matches both transitively-marked and bare verb analyses.

    Phase 4 §7.7: bare voice entries also constrain ``CAUS=NONE``
    so they don't spuriously match causative forms (``nagpakain``
    has VOICE=AV but CAUS=INDIRECT). For IV entries, the bare
    conveyed-pivot reading is constrained to ``APPL=CONVEY`` —
    benefactive / instrumental applicatives need their own entries
    matching ``APPL=BEN`` / ``APPL=INSTR``.

    Phase 5 §8: ``intrinsic_classification`` is the per-voice
    ``[±r, ±o]`` profile per role (see ``tgllfg.lmt``). When
    omitted the entry's intrinsics fall back to per-role
    Bresnan–Kanerva defaults via :func:`tgllfg.lmt.intrinsics_for`.
    """
    constraints: dict[str, object] = {"VOICE": voice, "CAUS": "NONE"}
    if transitive:
        constraints["TR"] = "TR"
    if voice == "IV":
        constraints["APPL"] = "CONVEY"
    else:
        constraints["APPL"] = "NONE"
    return LexicalEntry(
        lemma=lemma,
        pred=pred,
        a_structure=a_structure,
        morph_constraints=constraints,
        gf_defaults=gf_defaults,
        intrinsic_classification=intrinsic_classification or {},
    )


# === Phase 5 §8 intrinsic profiles =========================================
#
# Per-voice ``[±r, ±o]`` intrinsic profiles for the Phase 4 anchor
# patterns. Keyed by the canonical pattern name; values are the
# intrinsic-classification dicts ready to pass to ``_entry`` /
# ``LexicalEntry``. Each profile pins exactly one role at ``[-r, -o]``
# (the pivot for that voice form); non-pivot ng-NPs are ``[+r, +o]``
# (typed OBJ-θ via the BK truth table) and non-pivot sa-NPs are
# ``[+r, -o]`` (typed OBL-θ).
#
# Multi-GEN-NP frames (3-arg applicatives / causatives) are
# documented in ``tests/tgllfg/test_lmt_voice_mappings.py`` but not
# realized in the BASE entries — Phase 5b (the §7.7 multi-GEN-NP
# deferral) brings them online. The OBL-X reclassification pass
# (sa-marked recipients/locations on motion / ditransitive verbs)
# is implemented in :mod:`tgllfg.lmt.oblique_classifier`; ``lakad``
# below is its first BASE consumer.

# Plain-voice transitive profiles. Same shape regardless of which
# patient-like role is named (PATIENT vs THEME).
_AV_TR_AGENT_PATIENT: dict[str, tuple[bool | None, bool | None]] = {
    "AGENT": (False, False),
    "PATIENT": (False, True),
}
_AV_TR_AGENT_THEME: dict[str, tuple[bool | None, bool | None]] = {
    "AGENT": (False, False),
    "THEME": (False, True),
}
_OV_TR_AGENT_PATIENT: dict[str, tuple[bool | None, bool | None]] = {
    "AGENT": (True, True),
    "PATIENT": (False, False),
}
_OV_TR_AGENT_THEME: dict[str, tuple[bool | None, bool | None]] = {
    "AGENT": (True, True),
    "THEME": (False, False),
}
_DV_TR_AGENT_RECIPIENT: dict[str, tuple[bool | None, bool | None]] = {
    "AGENT": (True, True),
    "RECIPIENT": (False, False),
}
_IV_TR_AGENT_CONVEYED: dict[str, tuple[bool | None, bool | None]] = {
    "AGENT": (True, True),
    "CONVEYED": (False, False),
}

# Intransitive profiles (one role only, the pivot).
_AV_INTR_ACTOR: dict[str, tuple[bool | None, bool | None]] = {
    "ACTOR": (False, False),
}
_AV_INTR_AGENT: dict[str, tuple[bool | None, bool | None]] = {
    "AGENT": (False, False),
}
# Phase 9.X.c36: OV-impersonal absolutive — patient is the sole
# argument and takes SUBJ; the agent is discourse-suppressed.
# Surfaces in headless-RC constructions like ``ang inaani`` "the
# (thing) being harvested" where the AGENT is unexpressed.
_OV_INTR_PATIENT: dict[str, tuple[bool | None, bool | None]] = {
    "PATIENT": (False, False),
}

# Applicative / causative profiles (Phase 4 §7.7). The pivot rotates
# to BENEFICIARY / CAUSEE / CAUSER per voice; AGENT or non-pivot
# CAUSER demotes to OBJ-θ.
_IV_BEN_AGENT_BENEFICIARY: dict[str, tuple[bool | None, bool | None]] = {
    "AGENT": (True, True),
    "BENEFICIARY": (False, False),
}
# Phase 5c §7.7 follow-on: ipang- instrumental and ika- reason
# applicatives. The pivot rotates to INSTRUMENT / REASON; AGENT
# demotes to typed OBJ-AGENT. Same intrinsic shape as IV-BEN.
_IV_INSTR_AGENT_INSTRUMENT: dict[str, tuple[bool | None, bool | None]] = {
    "AGENT": (True, True),
    "INSTRUMENT": (False, False),
}
_IV_REASON_AGENT_REASON: dict[str, tuple[bool | None, bool | None]] = {
    "AGENT": (True, True),
    "REASON": (False, False),
}
# Phase 5b: three-arg IV-BEN with explicit PATIENT in addition to
# AGENT and BENEFICIARY. Both AGENT and PATIENT are [+r, +o] →
# typed OBJ-θ (OBJ-AGENT and OBJ-PATIENT, distinct GFs).
_IV_BEN_AGENT_PATIENT_BENEFICIARY: dict[
    str, tuple[bool | None, bool | None]
] = {
    "AGENT": (True, True),
    "PATIENT": (True, True),
    "BENEFICIARY": (False, False),
}
# Phase 5d Commit 4: three-arg IV-INSTR / IV-REASON variants
# parallel to Phase 5b's three-arg IV-BEN. Both AGENT and
# PATIENT demote to typed OBJ-θ; INSTRUMENT / REASON takes the
# pivot SUBJ slot.
_IV_INSTR_AGENT_PATIENT_INSTRUMENT: dict[
    str, tuple[bool | None, bool | None]
] = {
    "AGENT": (True, True),
    "PATIENT": (True, True),
    "INSTRUMENT": (False, False),
}
_IV_REASON_AGENT_PATIENT_REASON: dict[
    str, tuple[bool | None, bool | None]
] = {
    "AGENT": (True, True),
    "PATIENT": (True, True),
    "REASON": (False, False),
}
_OV_CAUS_DIRECT: dict[str, tuple[bool | None, bool | None]] = {
    "CAUSER": (True, True),
    "CAUSEE": (False, False),
}
# Phase 5d Commit 2: pa-...-an DV causative — pivot is the
# location / recipient of the caused event rather than the
# causee. CAUSER demotes to OBJ-CAUSER; LOCATION takes SUBJ.
_DV_CAUS_DIRECT: dict[str, tuple[bool | None, bool | None]] = {
    "CAUSER": (True, True),
    "LOCATION": (False, False),
}
# Phase 5b: three-arg pa-OV-direct with explicit PATIENT alongside
# CAUSER and CAUSEE-pivot. Both CAUSER and PATIENT are [+r, +o] →
# typed OBJ-θ (OBJ-CAUSER and OBJ-PATIENT, distinct GFs).
_OV_CAUS_DIRECT_THREE_ARG: dict[
    str, tuple[bool | None, bool | None]
] = {
    "CAUSER": (True, True),
    "PATIENT": (True, True),
    "CAUSEE": (False, False),
}
# Phase 5e Commit 10: three-arg pa-DV (pa-...-an) with explicit
# PATIENT alongside CAUSER and LOCATION-pivot. Mirrors the 3-arg
# pa-OV profile but with LOCATION (the recipient / locative) as
# the SUBJ-mapped role rather than CAUSEE. Both CAUSER and PATIENT
# are [+r, +o] → typed OBJ-θ.
_DV_CAUS_DIRECT_THREE_ARG: dict[
    str, tuple[bool | None, bool | None]
] = {
    "CAUSER": (True, True),
    "PATIENT": (True, True),
    "LOCATION": (False, False),
}
# Phase 5e Commit 11: three-arg plain DV (CAUS=NONE) with
# explicit PATIENT alongside AGENT and RECIPIENT-pivot. Mirrors
# the 3-arg pa-DV profile but with AGENT instead of CAUSER and
# RECIPIENT instead of LOCATION (semantically the same — DV's
# broad voice category covers location / recipient / dative —
# but role-named for non-causative DV ditransitives like
# ``Sinulatan ng nanay ng letra ang anak`` "Mother wrote a
# letter to the child").
_DV_TR_AGENT_PATIENT_RECIPIENT_THREE_ARG: dict[
    str, tuple[bool | None, bool | None]
] = {
    "AGENT": (True, True),
    "PATIENT": (True, True),
    "RECIPIENT": (False, False),
}
# Indirect (biclausal) causative: CAUSER pivot, EVENT stipulated as
# XCOMP via gf_defaults — the LMT bridge ``stipulated_gfs_for`` picks
# it up. The EVENT role itself has no [±r, ±o] (off the truth table).
_AV_CAUS_INDIRECT: dict[str, tuple[bool | None, bool | None]] = {
    "CAUSER": (False, False),
    "EVENT": (None, None),
}
# Phase 8.H: flat 3-arg AV-CAUS-INDIRECT companion to the
# biclausal profile above. S&O 1972 §10.4 documents both shapes
# for ``magpa-``: the biclausal-control form ``Nagpakain ako
# kumain ng kanin sa kanila.`` (with overt embedded V) and the
# monoclausal flat form ``Nagpapakain sila ng kendi sa kanila.``
# (audit hit S&O page 410 sent-593) where the embedded event's
# arguments surface as matrix NP daughters. The flat profile
# replaces the XCOMP-stipulated EVENT role with explicit PATIENT
# and CAUSEE thematic roles. PATIENT maps to OBJ (no semantic
# restriction; standard OBJ from the unrestricted-objective
# [+r=False, +o=True] truth-table cell); CAUSEE maps to a typed
# OBL-CAUSEE oblique (CAUSEE is restricted to this oblique slot;
# parallel to OBL-LOC / OBL-RECIP in DV ditransitives).
_AV_CAUS_INDIRECT_FLAT: dict[str, tuple[bool | None, bool | None]] = {
    "CAUSER": (False, False),
    "PATIENT": (False, True),
    "CAUSEE": (True, False),
}
# Phase 9.T.3: 2-arg AV-CAUS-INDIRECT companion to the flat 3-arg
# profile. ``Nagpakain siya ng kendi.`` (8.H pin) — CAUSER + PATIENT
# only, no overt CAUSEE. Structurally identical to a plain TR AV
# (AGENT + PATIENT) at the f-structure level; the semantic
# distinction (CAUSER vs AGENT) surfaces only in the PRED template
# (``CAUSE-EAT`` vs ``EAT``). The CAUSEE is implicit/recoverable
# from context but not syntactically realized.
_AV_CAUS_INDIRECT_2ARG: dict[str, tuple[bool | None, bool | None]] = {
    "CAUSER": (False, False),
    "PATIENT": (False, True),
}

# Control profiles (Phase 4 §7.6). COMPLEMENT is XCOMP-stipulated.
_PSYCH_CONTROL: dict[str, tuple[bool | None, bool | None]] = {
    "EXPERIENCER": (False, False),
    "COMPLEMENT": (None, None),
}
_INTRANS_CONTROL: dict[str, tuple[bool | None, bool | None]] = {
    "AGENT": (False, False),
    "COMPLEMENT": (None, None),
}
_OV_TRANS_CONTROL: dict[str, tuple[bool | None, bool | None]] = {
    "AGENT": (True, True),
    "PATIENT": (False, False),
    "COMPLEMENT": (None, None),
}
_DV_TRANS_CONTROL: dict[str, tuple[bool | None, bool | None]] = {
    "AGENT": (True, True),
    "RECIPIENT": (False, False),
    "COMPLEMENT": (None, None),
}
# Phase 5c §7.6 follow-on (Commit 5): raising verbs declare a
# non-thematic SUBJ outside the angle-bracketed PRED template
# (``SEEM <XCOMP> SUBJ``), so the only thematic role is
# COMPLEMENT (the proposition). The matrix's SUBJ is filled by
# structure-sharing with the embedded XCOMP.SUBJ via the grammar's
# raising binding, NOT by mapping a thematic role.
_RAISING: dict[str, tuple[bool | None, bool | None]] = {
    "COMPLEMENT": (None, None),
}

# Phase 5 §8: motion-verb profile with sa-marked locative argument.
# ACTOR is the AV pivot; LOCATION is OBL-θ via the [+r, -o]
# truth-table cell. The post-solve oblique classifier rewrites
# ADJUNCT members with CASE=DAT into the typed OBL-LOC slot.
_AV_INTR_ACTOR_LOCATION: dict[str, tuple[bool | None, bool | None]] = {
    "ACTOR": (False, False),
    "LOCATION": (True, False),
}

# Phase 5c §8 follow-on (Commit 6): ditransitive AV with two
# OBL-θ slots (RECIPIENT + LOCATION). Exercises the multi-OBL
# semantic-disambiguation pass — when both ``sa nanay`` (animate)
# and ``sa eskwela`` (place) appear, the classifier matches them
# to ``OBL-RECIP`` and ``OBL-LOC`` respectively regardless of
# surface order, by consulting the LEMMA-keyed semantic table.
_AV_DITRANS_AGENT_THEME_RECIP_LOC: dict[
    str, tuple[bool | None, bool | None]
] = {
    "AGENT": (False, False),
    "THEME": (False, True),
    "RECIPIENT": (True, False),
    "LOCATION": (True, False),
}


# Phase 5n.C.4 Commit 16: BASE is now loaded from the YAML
# tree under ``data/tgl/lexicon/`` rather than authored
# inline. Per-entry shape is specified in
# ``docs/lex-yaml-schema.md``; the loader auto-fills
# ``morph_constraints`` for ``_entry()``-style records and
# preserves the looser direct-LexicalEntry shape for the
# BEN / INSTR / REASON applicatives and the pseudo-verb
# control entries.
BASE: dict[str, list[LexicalEntry]] = load_lex_entries()


_SYNTH_DV_PROFILE: dict[str, tuple[bool | None, bool | None]] = {
    "AGENT": (True, True),
    "GOAL": (False, False),
}


def _synthesize_verb_entries(ma: MorphAnalysis) -> list[LexicalEntry]:
    """Phase 4 fallback for verbs not in :data:`BASE`. Synthesizes a
    voice-aware ``LexicalEntry`` (or list thereof) from the morph
    analysis so any verb the morph engine recognises produces a
    complete f-structure (PRED, a-structure, GF defaults).

    The synthesized PRED is the lemma in upper case; argument
    structure follows the verb's transitivity (TR → 2-arg, INTR →
    1-arg) and voice. Per-voice GF defaults match ``lmt.apply_lmt``
    so a-structure mapping is consistent with hand-authored entries.

    Phase 5 §8: every synthesized entry also carries an
    ``intrinsic_classification`` matching its voice profile so the
    LMT engine can map roles to GFs for verbs not in BASE. The
    profiles mirror the per-voice anchor patterns (AV pivot →
    AGENT/ACTOR ``[-r, -o]``; non-AV pivot → patient-like role
    ``[-r, -o]``; non-pivots ``[+r, +o]``).

    Phase 9.O B3.A: when the root carries ``feats: {AV_ABSOL: true}``
    AND the analysis is AV+TR, a *second* entry is synthesized with
    the AV-INTR (``<SUBJ>``-only) shape. The two entries co-exist:
    the parser tries both and picks whichever produces a complete
    parse. Concretely:

      - ``Tumingin siya kay Ben.`` parses via the TR entry (the AV
        oblique ``kay Ben`` slot fills via the existing oblique-NP
        rule; the OBJ slot is satisfied by the implicit pivot SUBJ
        ``siya``... no wait, TR-AV still requires an overt OBJ; in
        practice the TR entry would fail here too and the parse
        comes via the INTR entry with ``kay Ben`` as a free OBL).
      - ``Tumingin siya.`` parses via the INTR entry (1-arg,
        AGENT→SUBJ only).
      - ``Tinitingnan ko ang aklat.`` (OV-IPFV) — voice ≠ AV, so the
        AV_ABSOL flag is irrelevant; only the OV-TR entry is
        synthesized as before.

    Single source of TR/INTR polysemy for AV-absolutive uses,
    closing the 8.I + 8.O + 9.D-named six (``laro`` / ``regalo`` /
    ``sakit`` / ``tanong`` / ``tingin`` — ``tabi`` is already
    INTR-coded) verb roots' AV-absolutive carryover.
    """
    pred_name = ma.lemma.upper()
    voice = ma.feats.get("VOICE")
    is_tr = ma.feats.get("TR") == "TR"
    av_absolutive = bool(ma.feats.get("AV_ABSOL"))

    if not is_tr:
        return [LexicalEntry(
            lemma=ma.lemma,
            pred=f"{pred_name} <SUBJ>",
            a_structure=["ACTOR"],
            morph_constraints={},
            gf_defaults={"ACTOR": "SUBJ"},
            intrinsic_classification=_AV_INTR_ACTOR,
        )]

    # AV keeps bare OBJ; non-AV uses typed OBJ-AGENT per the
    # Phase 5b OBJ-θ-in-grammar alignment.
    if voice == "AV":
        tr_entry = LexicalEntry(
            lemma=ma.lemma, pred=f"{pred_name} <SUBJ, OBJ>",
            a_structure=["AGENT", "PATIENT"],
            morph_constraints={},
            gf_defaults={"AGENT": "SUBJ", "PATIENT": "OBJ"},
            intrinsic_classification=_AV_TR_AGENT_PATIENT,
        )
        if av_absolutive:
            # Phase 9.O B3.A: also synthesize the AV-absolutive
            # (INTR-style) variant — same PRED-name but
            # ``<SUBJ>``-only. Parser picks whichever variant
            # leads to a complete parse.
            intr_entry = LexicalEntry(
                lemma=ma.lemma,
                pred=f"{pred_name} <SUBJ>",
                a_structure=["ACTOR"],
                morph_constraints={},
                gf_defaults={"ACTOR": "SUBJ"},
                intrinsic_classification=_AV_INTR_ACTOR,
            )
            return [tr_entry, intr_entry]
        return [tr_entry]
    pred_non_av = f"{pred_name} <SUBJ, OBJ-AGENT>"
    if voice == "DV":
        dv_tr_entry = LexicalEntry(
            lemma=ma.lemma, pred=pred_non_av,
            a_structure=["AGENT", "GOAL"],
            morph_constraints={},
            gf_defaults={"GOAL": "SUBJ", "AGENT": "OBJ-AGENT"},
            intrinsic_classification=_SYNTH_DV_PROFILE,
        )
        if av_absolutive:
            # Phase 9.V.2: DV-NVOL absolutive synthesizes an INTR
            # variant where the experiencer (AGENT) is the sole
            # argument bound to SUBJ. Parallel to the 9.O AV path
            # above. The ma+root+-an paradigm cell on AV_ABSOL-
            # flagged roots (``malimutan`` / ``nalimutan`` for
            # ``limot``) admits the bare-experiencer reading
            # ``Malimutan ko.`` "I (will) forget (it)" with the
            # patient implicit. Closes 9.U Cluster B sent-661 inner
            # SubordClause body ``ko malimutan``.
            dv_intr_entry = LexicalEntry(
                lemma=ma.lemma,
                pred=f"{pred_name} <SUBJ>",
                a_structure=["AGENT"],
                morph_constraints={},
                gf_defaults={"AGENT": "SUBJ"},
                intrinsic_classification=_AV_INTR_ACTOR,
            )
            return [dv_tr_entry, dv_intr_entry]
        return [dv_tr_entry]
    if voice == "IV":
        return [LexicalEntry(
            lemma=ma.lemma, pred=pred_non_av,
            a_structure=["AGENT", "CONVEYED"],
            morph_constraints={},
            gf_defaults={"CONVEYED": "SUBJ", "AGENT": "OBJ-AGENT"},
            intrinsic_classification=_IV_TR_AGENT_CONVEYED,
        )]
    # OV or unknown voice: patient pivot (the OV-shaped fallback).
    ov_tr_entry = LexicalEntry(
        lemma=ma.lemma, pred=pred_non_av,
        a_structure=["AGENT", "PATIENT"],
        morph_constraints={},
        gf_defaults={"PATIENT": "SUBJ", "AGENT": "OBJ-AGENT"},
        intrinsic_classification=_OV_TR_AGENT_PATIENT,
    )
    if voice == "OV" and av_absolutive:
        # Phase 9.X.c36: OV-impersonal absolutive synthesizes an
        # INTR variant where the patient (SUBJ pivot) is the sole
        # argument and the agent is discourse-suppressed. Parallel
        # to the 9.O AV path and the 9.V DV path above. Surfaces
        # in headless-RC constructions like ``ang inaani`` "the
        # (thing) being harvested" (PANAHON sent-9), where the
        # implicit head fills the patient slot and the agent is
        # unexpressed.
        ov_intr_entry = LexicalEntry(
            lemma=ma.lemma,
            pred=f"{pred_name} <SUBJ>",
            a_structure=["PATIENT"],
            morph_constraints={},
            gf_defaults={"PATIENT": "SUBJ"},
            intrinsic_classification=_OV_INTR_PATIENT,
        )
        return [ov_tr_entry, ov_intr_entry]
    return [ov_tr_entry]


def _synthesize_verb_entry(ma: MorphAnalysis) -> LexicalEntry:
    """Legacy single-entry synthesis wrapper. Returns the first entry
    from :func:`_synthesize_verb_entries`. Retained for tests /
    external callers that pre-date the multi-entry refactor."""
    return _synthesize_verb_entries(ma)[0]


def lookup_lexicon(
    mlist: list[list[MorphAnalysis]],
) -> list[list[tuple[MorphAnalysis, LexicalEntry | None]]]:
    """Pair each MorphAnalysis with the compatible LexicalEntry(s) from
    ``BASE``, falling back to a synthesized entry for verbs not in
    BASE. Returns one list per token in lattice form.

    Compatibility rule for BASE entries: every key in the entry's
    ``morph_constraints`` must equal the corresponding feature on the
    MorphAnalysis. Missing features on the analysis are not matched
    (so an entry constrained on ``TR=TR`` won't match an analysis
    without a TR feature). For verbs absent from BASE,
    :func:`_synthesize_verb_entry` produces a voice-aware default so
    every recognised verb yields a complete f-structure.
    """
    out: list[list[tuple[MorphAnalysis, LexicalEntry | None]]] = []
    for cand_list in mlist:
        pairs: list[tuple[MorphAnalysis, LexicalEntry | None]] = []
        for ma in cand_list:
            if ma.pos == "VERB":
                matched = False
                if ma.lemma in BASE:
                    for le in BASE[ma.lemma]:
                        if all(
                            ma.feats.get(k) == v
                            for k, v in le.morph_constraints.items()
                        ):
                            pairs.append((ma, le))
                            matched = True
                # Phase 4 §7.10: fall back to synthesis when no BASE
                # entry matches the morph analysis. Previously this
                # only fired for lemmas absent from BASE; verbs in
                # BASE without an entry for the current voice would
                # produce no lex item and the parse would fail. The
                # synthesizer gives them voice-aware default
                # gf-mappings so unauthored voices still parse.
                #
                # Phase 9.O B3.A: ``_synthesize_verb_entries`` may
                # return more than one entry (specifically for
                # AV+TR+AV_ABSOL roots, where both the TR and
                # absolutive-INTR shapes are emitted). The caller
                # extends the pair list with every synthesized entry.
                if not matched:
                    for le in _synthesize_verb_entries(ma):
                        pairs.append((ma, le))
            else:
                pairs.append((ma, None))
        out.append(pairs)
    return out
