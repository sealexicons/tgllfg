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


def _entry(
    lemma: str,
    voice: str,
    pred: str,
    a_structure: list[str],
    gf_defaults: dict[str, str],
    *,
    transitive: bool = True,
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
    )


BASE: dict[str, list[LexicalEntry]] = {
    # kain — eat. Anchor of the OV percolation tests; carries the
    # legacy AV-intransitive template plus the Phase 4 AV-TR / OV-TR
    # additions.
    "kain": [
        # AV intransitive: actor pivot, no OBJ ("Kumain ang aso").
        # Note: morph_constraints omits TR so this entry also matches
        # MorphAnalyses for verbs declared TR in roots.yaml — the
        # grammar's intransitive S → V NP[NOM] rule is what restricts
        # use of this template to the 2-token surface.
        _entry(
            "kain", "AV", "EAT <SUBJ>",
            ["ACTOR"],
            {"ACTOR": "SUBJ"},
            transitive=False,
        ),
        # AV transitive: actor pivot, patient as ng-NP=OBJ.
        _entry(
            "kain", "AV", "EAT <SUBJ, OBJ>",
            ["AGENT", "PATIENT"],
            {"AGENT": "SUBJ", "PATIENT": "OBJ"},
        ),
        # OV transitive: patient pivot, agent as ng-NP=OBJ.
        _entry(
            "kain", "OV", "EAT <SUBJ, OBJ>",
            ["AGENT", "PATIENT"],
            {"PATIENT": "SUBJ", "AGENT": "OBJ"},
        ),
    ],
    # bili — buy. Phase 4 §7.10: AV-intransitive entry added so
    # "Bumili siya sa palengke" parses without an explicit patient.
    "bili": [
        _entry(
            "bili", "AV", "BUY <SUBJ>",
            ["AGENT"],
            {"AGENT": "SUBJ"},
            transitive=False,
        ),
        _entry(
            "bili", "AV", "BUY <SUBJ, OBJ>",
            ["AGENT", "THEME"],
            {"AGENT": "SUBJ", "THEME": "OBJ"},
        ),
        _entry(
            "bili", "OV", "BUY <SUBJ, OBJ>",
            ["AGENT", "THEME"],
            {"THEME": "SUBJ", "AGENT": "OBJ"},
        ),
    ],
    # basa — read. Phase 4 §7.10: AV-intransitive added.
    "basa": [
        _entry(
            "basa", "AV", "READ <SUBJ>",
            ["AGENT"],
            {"AGENT": "SUBJ"},
            transitive=False,
        ),
        _entry(
            "basa", "AV", "READ <SUBJ, OBJ>",
            ["AGENT", "THEME"],
            {"AGENT": "SUBJ", "THEME": "OBJ"},
        ),
        _entry(
            "basa", "OV", "READ <SUBJ, OBJ>",
            ["AGENT", "THEME"],
            {"THEME": "SUBJ", "AGENT": "OBJ"},
        ),
    ],
    # sulat — write. Demonstrates all four voices: AV (actor pivot),
    # OV (theme pivot), DV (recipient pivot, ``sinulatan``), IV
    # (conveyed pivot, ``isinulat``). Phase 4 §7.10: AV-intransitive
    # added for "Sumulat si Juan kay Maria" patterns where the
    # patient is unspecified.
    "sulat": [
        _entry(
            "sulat", "AV", "WRITE <SUBJ>",
            ["AGENT"],
            {"AGENT": "SUBJ"},
            transitive=False,
        ),
        _entry(
            "sulat", "AV", "WRITE <SUBJ, OBJ>",
            ["AGENT", "THEME"],
            {"AGENT": "SUBJ", "THEME": "OBJ"},
        ),
        _entry(
            "sulat", "OV", "WRITE <SUBJ, OBJ>",
            ["AGENT", "THEME"],
            {"THEME": "SUBJ", "AGENT": "OBJ"},
        ),
        _entry(
            "sulat", "DV", "WRITE <SUBJ, OBJ>",
            ["AGENT", "RECIPIENT"],
            {"RECIPIENT": "SUBJ", "AGENT": "OBJ"},
        ),
        _entry(
            "sulat", "IV", "WRITE <SUBJ, OBJ>",
            ["AGENT", "CONVEYED"],
            {"CONVEYED": "SUBJ", "AGENT": "OBJ"},
        ),
    ],
    # gawa — do, make.
    "gawa": [
        _entry(
            "gawa", "AV", "MAKE <SUBJ, OBJ>",
            ["AGENT", "PATIENT"],
            {"AGENT": "SUBJ", "PATIENT": "OBJ"},
        ),
        _entry(
            "gawa", "OV", "MAKE <SUBJ, OBJ>",
            ["AGENT", "PATIENT"],
            {"PATIENT": "SUBJ", "AGENT": "OBJ"},
        ),
    ],
    # tapon — throw away. mag- AV class (no -um-); naturally takes IV
    # for the conveyed-theme reading ("itinapon ang basura"). i_oblig
    # is added to its affix_class in roots.yaml so the IV form
    # generates.
    "tapon": [
        _entry(
            "tapon", "AV", "THROW <SUBJ, OBJ>",
            ["AGENT", "THEME"],
            {"AGENT": "SUBJ", "THEME": "OBJ"},
        ),
        _entry(
            "tapon", "OV", "THROW <SUBJ, OBJ>",
            ["AGENT", "THEME"],
            {"THEME": "SUBJ", "AGENT": "OBJ"},
        ),
        _entry(
            "tapon", "IV", "THROW <SUBJ, OBJ>",
            ["AGENT", "CONVEYED"],
            {"CONVEYED": "SUBJ", "AGENT": "OBJ"},
        ),
    ],
    # ===== Phase 4 §7.6: control verbs =====================================
    #
    # Three control patterns, all sharing SUBJ-control over an XCOMP
    # complement: the matrix SUBJ binds the embedded SUBJ via
    # ``(↑ SUBJ) = (↑ XCOMP REL-PRO)``. The patterns differ in which
    # case-marked NP fills the matrix SUBJ slot.
    #
    # Psych predicates (gusto / ayaw / kaya): GEN experiencer is
    # matrix SUBJ. PRED carries SUBJ + XCOMP only (no OBJ). The
    # ``CTRL_CLASS=PSYCH`` constraint matches the entries seeded
    # under ``particles.yaml`` (uninflected pseudo-verbs).
    "gusto": [
        LexicalEntry(
            lemma="gusto",
            pred="WANT <SUBJ, XCOMP>",
            a_structure=["EXPERIENCER", "COMPLEMENT"],
            morph_constraints={"CTRL_CLASS": "PSYCH"},
            gf_defaults={"EXPERIENCER": "SUBJ", "COMPLEMENT": "XCOMP"},
        ),
    ],
    "ayaw": [
        LexicalEntry(
            lemma="ayaw",
            pred="DISLIKE <SUBJ, XCOMP>",
            a_structure=["EXPERIENCER", "COMPLEMENT"],
            morph_constraints={"CTRL_CLASS": "PSYCH"},
            gf_defaults={"EXPERIENCER": "SUBJ", "COMPLEMENT": "XCOMP"},
        ),
    ],
    "kaya": [
        LexicalEntry(
            lemma="kaya",
            pred="ABLE <SUBJ, XCOMP>",
            a_structure=["EXPERIENCER", "COMPLEMENT"],
            morph_constraints={"CTRL_CLASS": "PSYCH"},
            gf_defaults={"EXPERIENCER": "SUBJ", "COMPLEMENT": "XCOMP"},
        ),
    ],
    # Intransitive control (payag → pumayag, pumapayag, papayag):
    # AV-only, NOM-NP is matrix SUBJ. AGREE <SUBJ, XCOMP>.
    "payag": [
        LexicalEntry(
            lemma="payag",
            pred="AGREE <SUBJ, XCOMP>",
            a_structure=["AGENT", "COMPLEMENT"],
            morph_constraints={"VOICE": "AV", "CTRL_CLASS": "INTRANS"},
            gf_defaults={"AGENT": "SUBJ", "COMPLEMENT": "XCOMP"},
        ),
    ],
    # Transitive control (pilit, utos): pivot is forcee/orderee
    # (matrix SUBJ in OV / DV), GEN-NP is forcer/orderer (matrix
    # OBJ). 3-arg PRED ``<SUBJ, OBJ, XCOMP>``.
    "pilit": [
        LexicalEntry(
            lemma="pilit",
            pred="FORCE <SUBJ, OBJ, XCOMP>",
            a_structure=["AGENT", "PATIENT", "COMPLEMENT"],
            morph_constraints={"VOICE": "OV", "CTRL_CLASS": "TRANS"},
            gf_defaults={
                "PATIENT": "SUBJ",
                "AGENT": "OBJ",
                "COMPLEMENT": "XCOMP",
            },
        ),
    ],
    "utos": [
        LexicalEntry(
            lemma="utos",
            pred="ORDER <SUBJ, OBJ, XCOMP>",
            a_structure=["AGENT", "RECIPIENT", "COMPLEMENT"],
            morph_constraints={"VOICE": "DV", "CTRL_CLASS": "TRANS"},
            gf_defaults={
                "RECIPIENT": "SUBJ",
                "AGENT": "OBJ",
                "COMPLEMENT": "XCOMP",
            },
        ),
    ],
}


# ===== Phase 4 §7.7: applicative & causative entries appended to BASE =====
#
# Each applicative / causative variant is constrained to a
# specific (VOICE, APPL|CAUS) combination so it pairs with the
# corresponding morph cell. The patient role is omitted from
# 2-arg PRED templates — multi-GEN-NP frames are out of scope for
# this commit (see docs/analysis-choices.md "Phase 4 §7.7").
#
# These entries are appended to existing BASE keys (kain, bili,
# gawa, basa, inom, sulat) so the lex lookup picks them up
# alongside the verbs' standard voice entries; the
# ``morph_constraints`` discriminate which variant matches a given
# MorphAnalysis at lookup time.

# Benefactive applicatives (ipag-): SUBJ = beneficiary, OBJ = agent
# (the GEN-marked actor of the doing).
BASE["gawa"].append(LexicalEntry(
    lemma="gawa",
    pred="MAKE-FOR <SUBJ, OBJ>",
    a_structure=["AGENT", "BENEFICIARY"],
    morph_constraints={"VOICE": "IV", "APPL": "BEN"},
    gf_defaults={"BENEFICIARY": "SUBJ", "AGENT": "OBJ"},
))
BASE["sulat"].append(LexicalEntry(
    lemma="sulat",
    pred="WRITE-FOR <SUBJ, OBJ>",
    a_structure=["AGENT", "BENEFICIARY"],
    morph_constraints={"VOICE": "IV", "APPL": "BEN"},
    gf_defaults={"BENEFICIARY": "SUBJ", "AGENT": "OBJ"},
))
BASE["bili"].append(LexicalEntry(
    lemma="bili",
    pred="BUY-FOR <SUBJ, OBJ>",
    a_structure=["AGENT", "BENEFICIARY"],
    morph_constraints={"VOICE": "IV", "APPL": "BEN"},
    gf_defaults={"BENEFICIARY": "SUBJ", "AGENT": "OBJ"},
))

# Direct (monoclausal) causatives (pa-...-in OV): SUBJ = causee
# (the pivot, NOM-marked), OBJ = causer (GEN-marked agent of
# causing). Single-clause; the embedded eventuality is folded into
# the matrix's PRED.
BASE["kain"].append(LexicalEntry(
    lemma="kain",
    pred="CAUSE-EAT <SUBJ, OBJ>",
    a_structure=["CAUSER", "CAUSEE"],
    morph_constraints={"VOICE": "OV", "CAUS": "DIRECT"},
    gf_defaults={"CAUSEE": "SUBJ", "CAUSER": "OBJ"},
))
BASE["basa"].append(LexicalEntry(
    lemma="basa",
    pred="CAUSE-READ <SUBJ, OBJ>",
    a_structure=["CAUSER", "CAUSEE"],
    morph_constraints={"VOICE": "OV", "CAUS": "DIRECT"},
    gf_defaults={"CAUSEE": "SUBJ", "CAUSER": "OBJ"},
))
BASE.setdefault("inom", []).append(LexicalEntry(
    lemma="inom",
    pred="CAUSE-DRINK <SUBJ, OBJ>",
    a_structure=["CAUSER", "CAUSEE"],
    morph_constraints={"VOICE": "OV", "CAUS": "DIRECT"},
    gf_defaults={"CAUSEE": "SUBJ", "CAUSER": "OBJ"},
))

# Indirect (biclausal) causatives (magpa- AV): SUBJ = causer,
# XCOMP = caused event. Re-uses §7.6 control infrastructure
# (CTRL_CLASS=INTRANS) so the existing intransitive control wrap
# rule fires. The causee surfaces as a controlled SUBJ inside the
# XCOMP.
BASE["kain"].append(LexicalEntry(
    lemma="kain",
    pred="CAUSE-EAT <SUBJ, XCOMP>",
    a_structure=["CAUSER", "EVENT"],
    morph_constraints={
        "VOICE": "AV", "CAUS": "INDIRECT", "CTRL_CLASS": "INTRANS",
    },
    gf_defaults={"CAUSER": "SUBJ", "EVENT": "XCOMP"},
))
BASE["basa"].append(LexicalEntry(
    lemma="basa",
    pred="CAUSE-READ <SUBJ, XCOMP>",
    a_structure=["CAUSER", "EVENT"],
    morph_constraints={
        "VOICE": "AV", "CAUS": "INDIRECT", "CTRL_CLASS": "INTRANS",
    },
    gf_defaults={"CAUSER": "SUBJ", "EVENT": "XCOMP"},
))
BASE["inom"].append(LexicalEntry(
    lemma="inom",
    pred="CAUSE-DRINK <SUBJ, XCOMP>",
    a_structure=["CAUSER", "EVENT"],
    morph_constraints={
        "VOICE": "AV", "CAUS": "INDIRECT", "CTRL_CLASS": "INTRANS",
    },
    gf_defaults={"CAUSER": "SUBJ", "EVENT": "XCOMP"},
))


def _synthesize_verb_entry(ma: MorphAnalysis) -> LexicalEntry:
    """Phase 4 fallback for verbs not in :data:`BASE`. Synthesizes a
    voice-aware ``LexicalEntry`` from the morph analysis so any
    verb the morph engine recognises produces a complete
    f-structure (PRED, a-structure, GF defaults).

    The synthesized PRED is the lemma in upper case; argument
    structure follows the verb's transitivity (TR → 2-arg, INTR →
    1-arg) and voice. Per-voice GF defaults match ``lmt.apply_lmt``
    so a-structure mapping is consistent with hand-authored entries.
    """
    pred_name = ma.lemma.upper()
    voice = ma.feats.get("VOICE")
    is_tr = ma.feats.get("TR") == "TR"

    if not is_tr:
        return LexicalEntry(
            lemma=ma.lemma,
            pred=f"{pred_name} <SUBJ>",
            a_structure=["ACTOR"],
            morph_constraints={},
            gf_defaults={"ACTOR": "SUBJ"},
        )

    pred = f"{pred_name} <SUBJ, OBJ>"
    if voice == "AV":
        return LexicalEntry(
            lemma=ma.lemma, pred=pred,
            a_structure=["AGENT", "PATIENT"],
            morph_constraints={},
            gf_defaults={"AGENT": "SUBJ", "PATIENT": "OBJ"},
        )
    if voice == "DV":
        return LexicalEntry(
            lemma=ma.lemma, pred=pred,
            a_structure=["AGENT", "GOAL"],
            morph_constraints={},
            gf_defaults={"GOAL": "SUBJ", "AGENT": "OBJ"},
        )
    if voice == "IV":
        return LexicalEntry(
            lemma=ma.lemma, pred=pred,
            a_structure=["AGENT", "CONVEYED"],
            morph_constraints={},
            gf_defaults={"CONVEYED": "SUBJ", "AGENT": "OBJ"},
        )
    # OV or unknown voice: patient pivot (the OV-shaped fallback).
    return LexicalEntry(
        lemma=ma.lemma, pred=pred,
        a_structure=["AGENT", "PATIENT"],
        morph_constraints={},
        gf_defaults={"PATIENT": "SUBJ", "AGENT": "OBJ"},
    )


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
                if not matched:
                    pairs.append((ma, _synthesize_verb_entry(ma)))
            else:
                pairs.append((ma, None))
        out.append(pairs)
    return out
