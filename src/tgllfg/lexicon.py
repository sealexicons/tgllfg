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
    matches both transitively-marked and bare verb analyses."""
    constraints: dict[str, object] = {"VOICE": voice}
    if transitive:
        constraints["TR"] = "TR"
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
    # bili — buy. Two voices for Commit 1 (AV-TR, OV-TR); the IV
    # benefactive ("ibinili ng X kay Y") needs a 3-arg PRED frame and
    # is deferred to Phase 5 LMT.
    "bili": [
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
    # basa — read.
    "basa": [
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
    # (conveyed pivot, ``isinulat``).
    "sulat": [
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
}


def lookup_lexicon(
    mlist: list[list[MorphAnalysis]],
) -> list[list[tuple[MorphAnalysis, LexicalEntry | None]]]:
    """Pair each MorphAnalysis with the compatible LexicalEntry(s) from
    ``BASE``. Returns one list per token in lattice form.

    Compatibility rule: every key in the entry's ``morph_constraints``
    must equal the corresponding feature on the MorphAnalysis. Missing
    features on the analysis are not matched (so an entry constrained
    on ``TR=TR`` won't match an analysis without a TR feature)."""
    out: list[list[tuple[MorphAnalysis, LexicalEntry | None]]] = []
    for cand_list in mlist:
        pairs: list[tuple[MorphAnalysis, LexicalEntry | None]] = []
        for ma in cand_list:
            if ma.pos == "VERB" and ma.lemma in BASE:
                for le in BASE[ma.lemma]:
                    if all(ma.feats.get(k) == v for k, v in le.morph_constraints.items()):
                        pairs.append((ma, le))
            else:
                pairs.append((ma, None))
        out.append(pairs)
    return out
