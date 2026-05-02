#!/usr/bin/env python3
"""Phase 4 §7.10: generate the coverage corpus.

Produces ``tests/tgllfg/data/coverage_corpus.yaml`` — ~500 Tagalog
sentences tagged with the construction they exercise and the
expected parsing outcome (``parse`` / ``fragment`` / ``fail``).
The corpus drives the §7.10 coverage benchmark; see
:mod:`tests.tgllfg.test_coverage_phase4` for the harness and
``docs/coverage.md`` for the rendered results.

Most sentences are produced by combinatorial expansion across
templates × anchor verbs × NPs. A small set of hand-authored
"classic" examples (drawn from Schachter & Otanes 1972 and
Kroeger 1993) is appended at the end.

Run with::

    hatch run python scripts/generate_coverage_corpus.py

Re-running is idempotent — the YAML file is fully regenerated.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

from tgllfg.morph.analyzer import _get_default

# Where the generated YAML lives.
_OUT = (
    Path(__file__).resolve().parent.parent
    / "tests" / "tgllfg" / "data" / "coverage_corpus.yaml"
)


# === Lexical pools ========================================================

# Anchor verbs with their available voices (from BASE in lexicon.py).
# Each entry: lemma → list of (voice, AV-form, OV-form, DV-form, IV-form, surface).
# We use surface forms directly to avoid round-tripping through morph.

# Verb forms are looked up from the morph engine at corpus-
# generation time so the table stays in sync with paradigms.yaml.
# A reverse-lookup table maps (lemma, voice, aspect) → surface for
# the anchor verbs we use in templates.

def _build_verb_form_index() -> dict[str, dict[str, dict[str, str]]]:
    """Walk the morph engine's pre-generated index and produce a
    nested ``{lemma: {voice: {aspect: surface}}}`` table for the
    anchor verbs."""
    analyzer = _get_default()
    anchor_verbs = {"kain", "bili", "basa", "sulat", "gawa", "tapon"}
    out: dict[str, dict[str, dict[str, str]]] = {}
    for surface, analyses in analyzer._index.verb_forms.items():
        for ma in analyses:
            if ma.lemma not in anchor_verbs:
                continue
            voice = ma.feats.get("VOICE")
            aspect = ma.feats.get("ASPECT")
            appl = ma.feats.get("APPL")
            caus = ma.feats.get("CAUS")
            # Only the bare voice cells (APPL=NONE/CONVEY, CAUS=NONE)
            # — applicative and causative variants live in their
            # own template sections.
            if caus not in (None, "NONE"):
                continue
            if appl not in (None, "NONE", "CONVEY"):
                continue
            if not voice or not aspect or aspect == "RECPFV":
                # RECPFV not used in core templates; skip.
                continue
            out.setdefault(ma.lemma, {}).setdefault(voice, {})[aspect] = surface
    return out


_VERB_FORMS = _build_verb_form_index()


# Intransitive AV verbs (the morph engine generates the same way).
def _build_intr_form_index() -> dict[str, dict[str, str]]:
    analyzer = _get_default()
    intr_verbs = {"takbo", "tulog", "uwi"}
    out: dict[str, dict[str, str]] = {}
    for surface, analyses in analyzer._index.verb_forms.items():
        for ma in analyses:
            if ma.lemma not in intr_verbs:
                continue
            if ma.feats.get("VOICE") != "AV":
                continue
            if ma.feats.get("CAUS") not in (None, "NONE"):
                continue
            aspect = ma.feats.get("ASPECT")
            if not aspect or aspect == "RECPFV":
                continue
            # Prefer IND over NVOL for the corpus.
            if ma.feats.get("MOOD") not in (None, "IND"):
                continue
            out.setdefault(ma.lemma, {})[aspect] = surface
    return out


_INTR_VERBS_RAW = _build_intr_form_index()
# Use the morph-derived versions (kept in same shape as before).
_INTR_VERBS = _INTR_VERBS_RAW

# Intransitive AV verbs (all only have AV).
_INTR_VERBS: dict[str, dict[str, str]] = {
    "takbo": {"PFV": "tumakbo",   "IPFV": "tumatakbo",   "CTPL": "tatakbo"},
    "tulog": {"PFV": "natulog",   "IPFV": "natutulog",   "CTPL": "matutulog"},
    "uwi":   {"PFV": "umuwi",     "IPFV": "umuuwi",      "CTPL": "uuwi"},
}

# NPs (already in the seed lexicon).
_NOM_NPS: list[str] = ["ang aso", "ang bata", "ang nanay", "ang lalaki",
                        "ang babae", "ang ina", "si Maria", "si Juan",
                        "si Pedro"]
_GEN_NPS: list[str] = ["ng aso", "ng bata", "ng nanay", "ng lalaki",
                        "ng isda", "ni Maria", "ni Juan", "ni Pedro"]


def _linker_form(host: str) -> str:
    """Glue ``-ng`` after vowel-final hosts, ``na`` after
    consonant-final hosts. Handles bare nouns and ``ang/si/ni``-
    headed NPs."""
    head_word = host.rstrip(".").split()[-1]
    if head_word and head_word[-1] in "aeiou":
        return host + "ng"
    return host + " na"
_DAT_NPS: list[str] = ["sa aso", "sa bata", "sa nanay", "sa Maria",
                        "kay Juan", "kay Pedro"]

_PRON_NOM: list[str] = ["ako", "ka", "siya", "kami", "kayo", "sila"]
_PRON_GEN: list[str] = ["ko", "mo", "niya", "namin", "ninyo", "nila"]


# === Template-based generation ============================================


def _add(
    out: list[dict[str, Any]],
    text: str,
    construction: str,
    expected: str = "parse",
    *,
    source: str | None = None,
    notes: str | None = None,
) -> None:
    """Append one corpus entry, capitalizing the surface."""
    rec: dict[str, Any] = {
        "text": _capitalize(text),
        "construction": construction,
        "expected": expected,
    }
    if source:
        rec["source"] = source
    if notes:
        rec["notes"] = notes
    out.append(rec)


def _capitalize(s: str) -> str:
    """Capitalize the first letter of the sentence; preserve the
    rest. Append a period if missing."""
    if not s:
        return s
    s = s[0].upper() + s[1:]
    if not s.endswith((".", "?", "!")):
        s += "."
    return s


def _voice_aspect_corpus() -> list[dict[str, Any]]:
    """§7.1 + §7.2: voice × aspect coverage. Generates intransitive
    AV (V + NOM-NP), transitive AV (V + NOM + GEN), and OV/DV/IV
    transitives (with the GEN-marked agent and NOM-marked pivot)."""
    out: list[dict[str, Any]] = []

    # Intransitive AV: V NOM
    for lemma, forms in _INTR_VERBS.items():
        for asp, surface in forms.items():
            for nom in _NOM_NPS[:4]:
                _add(out, f"{surface} {nom}",
                     "voice/aspect: AV-intransitive",
                     "parse")

    # Transitive AV: V NOM GEN
    for lemma in ("kain", "bili", "basa", "sulat", "gawa"):
        for asp in ("PFV", "IPFV", "CTPL"):
            forms = _VERB_FORMS[lemma]
            if "AV" not in forms:
                continue
            verb = forms["AV"][asp]
            for nom in _NOM_NPS[:3]:
                for gen in _GEN_NPS[:3]:
                    _add(out, f"{verb} {nom} {gen}",
                         "voice/aspect: AV-transitive",
                         "parse")

    # OV: V GEN NOM (or NOM GEN — both grammatical)
    for lemma in ("kain", "bili", "basa", "sulat", "gawa", "tapon"):
        for asp in ("PFV", "IPFV", "CTPL"):
            forms = _VERB_FORMS[lemma]
            if "OV" not in forms:
                continue
            verb = forms["OV"][asp]
            for nom in _NOM_NPS[:2]:
                for gen in _GEN_NPS[:2]:
                    _add(out, f"{verb} {gen} {nom}",
                         "voice/aspect: OV-transitive",
                         "parse")

    # DV: V GEN NOM
    for lemma in ("kain", "sulat"):
        for asp in ("PFV", "IPFV", "CTPL"):
            forms = _VERB_FORMS[lemma]
            if "DV" not in forms:
                continue
            verb = forms["DV"][asp]
            for nom in _NOM_NPS[:2]:
                for gen in _GEN_NPS[:2]:
                    _add(out, f"{verb} {gen} {nom}",
                         "voice/aspect: DV-transitive",
                         "parse")

    # IV
    for lemma in ("sulat", "tapon"):
        for asp in ("PFV", "IPFV", "CTPL"):
            forms = _VERB_FORMS[lemma]
            if "IV" not in forms:
                continue
            verb = forms["IV"][asp]
            for nom in _NOM_NPS[:2]:
                for gen in _GEN_NPS[:2]:
                    _add(out, f"{verb} {gen} {nom}",
                         "voice/aspect: IV-transitive",
                         "parse")

    return out


def _negation_corpus() -> list[dict[str, Any]]:
    """§7.2: negation composition with hindi (declarative NEG)."""
    out: list[dict[str, Any]] = []
    for lemma in ("kain", "bili", "basa"):
        for asp in ("PFV", "IPFV"):
            verb = _VERB_FORMS[lemma]["AV"][asp]
            for nom in _NOM_NPS[:3]:
                _add(out, f"hindi {verb} {nom}",
                     "negation: hindi declarative",
                     "parse")
            verb_ov = _VERB_FORMS[lemma]["OV"][asp]
            for nom, gen in zip(_NOM_NPS[:3], _GEN_NPS[:3]):
                _add(out, f"hindi {verb_ov} {gen} {nom}",
                     "negation: hindi + transitive",
                     "parse")
    # huwag (imperative NEG)
    for lemma in ("kain", "basa"):
        verb = _VERB_FORMS[lemma]["AV"]["PFV"]
        for nom in _NOM_NPS[:2]:
            _add(out, f"huwag {verb} {nom}",
                 "negation: huwag imperative",
                 "parse")
    return out


def _clitic_corpus() -> list[dict[str, Any]]:
    """§7.3: Wackernagel clitic placement — pronominal SUBJ /
    OBJ in clitic position; aspectual ``na`` / ``pa`` / ``ba``."""
    out: list[dict[str, Any]] = []
    # AV transitive with clitic SUBJ
    for lemma in ("kain", "bili"):
        for asp in ("PFV", "IPFV"):
            verb = _VERB_FORMS[lemma]["AV"][asp]
            for pron in _PRON_NOM[:4]:
                for gen in _GEN_NPS[:2]:
                    _add(out, f"{verb} {pron} {gen}",
                         "clitic: pron-NOM as SUBJ",
                         "parse")

    # OV transitive with clitic OBJ (ng-marked agent)
    for lemma in ("kain", "basa"):
        for asp in ("PFV", "IPFV"):
            verb = _VERB_FORMS[lemma]["OV"][asp]
            for pron in _PRON_GEN[:4]:
                for nom in _NOM_NPS[:2]:
                    _add(out, f"{verb} {pron} {nom}",
                         "clitic: pron-GEN as OBJ",
                         "parse")

    # Adverbial enclitics
    for lemma in ("kain", "basa"):
        verb = _VERB_FORMS[lemma]["OV"]["PFV"]
        for adv in ("na", "pa", "ba"):
            for nom in _NOM_NPS[:2]:
                _add(out, f"{verb} {adv} {_GEN_NPS[0]} {nom}",
                     f"clitic: adv enclitic {adv}",
                     "parse")

    # Combined pron + adv
    for verb in (_VERB_FORMS["kain"]["OV"]["PFV"],):
        for adv in ("na", "ba"):
            for pron, nom in zip(_PRON_GEN[:3], _NOM_NPS[:3]):
                _add(out, f"{verb} {pron} {adv} {nom}",
                     "clitic: cluster pron + adv",
                     "parse")

    return out


def _ay_inversion_corpus() -> list[dict[str, Any]]:
    """§7.4: ay-inversion. Pivot SUBJ fronting (Phase 4 §7.4) plus
    pa-causative actor-fronting (Phase 5e Commit 1)."""
    out: list[dict[str, Any]] = []
    for lemma in ("kain", "bili", "basa"):
        for asp in ("PFV", "IPFV"):
            verb = _VERB_FORMS[lemma]["AV"][asp]
            for nom in _NOM_NPS[:3]:
                _add(out, f"{nom} ay {verb}",
                     "ay-inversion: SUBJ-fronted intransitive",
                     "parse")
                for gen in _GEN_NPS[:2]:
                    _add(out, f"{nom} ay {verb} {gen}",
                         "ay-inversion: SUBJ-fronted transitive",
                         "parse")
    # Negation under ay
    for nom in _NOM_NPS[:3]:
        _add(out, f"{nom} ay hindi {_VERB_FORMS['kain']['AV']['PFV']}",
             "ay-inversion: with NEG",
             "parse")

    # Phase 5e Commit 1: pa-OV / pa-DV (CAUS=DIRECT) actor-fronting.
    # The fronted GEN-NP is the CAUSER; the inner SUBJ pivot
    # (CAUSEE for pa-OV, LOCATION/RECIPIENT for pa-DV) stays overt.
    for caus_form in ("pinakain", "pinabasa", "pinainom"):
        _add(out, f"ng nanay ay {caus_form} ang bata",
             f"ay-inversion: pa-OV actor-fronting ({caus_form})",
             "parse")
    # 3-arg pa-OV with overt PATIENT.
    _add(out, "ng nanay ay pinakain ang bata ng kanin",
         "ay-inversion: 3-arg pa-OV actor-fronting",
         "parse")
    # pa-DV (pa-...-an) actor-fronting.
    for dv_form in ("pinakainan", "pinabasahan", "pinainuman"):
        _add(out, f"ng nanay ay {dv_form} ang bata",
             f"ay-inversion: pa-DV actor-fronting ({dv_form})",
             "parse")
    # Inner negation under pa-causative actor-fronting.
    _add(out, "ng nanay ay hindi pinakain ang bata",
         "ay-inversion: pa-OV actor-fronting + NEG",
         "parse")

    # Phase 5e Commit 2: multi-GEN-NP ay-fronting. Fronts one of
    # the two GEN-NPs in a Phase 5b 3-arg multi-GEN frame; the
    # other GEN-NP is retained in the inner clause along with the
    # NOM pivot.
    # IV 3-arg with OBJ-AGENT extracted (PATIENT retained).
    _add(out, "ng nanay ay ipinaggawa ang kapatid ng silya",
         "ay-inversion: IV-BEN 3-arg AGENT-fronted",
         "parse")
    _add(out, "ng nanay ay ipinambili ang pera ng isda",
         "ay-inversion: IV-INSTR 3-arg AGENT-fronted",
         "parse")
    _add(out, "ng bata ay ikinasulat ang gutom ng isda",
         "ay-inversion: IV-REASON 3-arg AGENT-fronted",
         "parse")
    # IV 3-arg with OBJ-PATIENT extracted (AGENT retained).
    _add(out, "ng silya ay ipinaggawa ang kapatid ng nanay",
         "ay-inversion: IV-BEN 3-arg PATIENT-fronted",
         "parse")
    _add(out, "ng isda ay ipinambili ang pera ng nanay",
         "ay-inversion: IV-INSTR 3-arg PATIENT-fronted",
         "parse")
    # pa-OV-direct 3-arg with OBJ-PATIENT extracted (CAUSER retained).
    _add(out, "ng kanin ay pinakain ng nanay ang bata",
         "ay-inversion: pa-OV 3-arg PATIENT-fronted",
         "parse")
    _add(out, "ng libro ay pinabasa ng nanay ang bata",
         "ay-inversion: pa-OV 3-arg PATIENT-fronted (basa)",
         "parse")
    # Negation under multi-GEN ay-fronting.
    _add(out, "ng nanay ay hindi ipinaggawa ang kapatid ng silya",
         "ay-inversion: IV-BEN 3-arg AGENT-fronted + NEG",
         "parse")

    # Phase 5e Commit 3: AdvP / PP ay-fronting. Lifts the §7.4
    # "Out-of-scope" item that required a categorial-inventory
    # expansion (ADV / PREP POS, AdvP / PP non-terminals).
    # Temporal AdvP fronting.
    for adv in ("kahapon", "ngayon", "bukas", "mamaya"):
        _add(out, f"{adv} ay tumakbo si Maria",
             f"ay-inversion: AdvP fronted ({adv})",
             "parse")
    # AdvP with negated inner clause.
    _add(out, "kahapon ay hindi tumakbo si Maria",
         "ay-inversion: AdvP fronted + NEG",
         "parse")
    # AdvP with transitive inner.
    _add(out, "kahapon ay kumain ang aso ng isda",
         "ay-inversion: AdvP fronted + transitive inner",
         "parse")
    # PP fronting: para / tungkol / mula / dahil.
    _add(out, "para sa bata ay binili niya ang libro",
         "ay-inversion: PP fronted (para)",
         "parse")
    _add(out, "tungkol sa nanay ay sumulat ang bata",
         "ay-inversion: PP fronted (tungkol)",
         "parse")
    _add(out, "mula sa bahay ay tumakbo si Maria",
         "ay-inversion: PP fronted (mula)",
         "parse")
    _add(out, "dahil sa gutom ay kumain ang bata",
         "ay-inversion: PP fronted (dahil)",
         "parse")
    return out


def _relativization_corpus() -> list[dict[str, Any]]:
    """§7.5: SUBJ-only relativization; both `na` and `-ng` linker
    variants."""
    out: list[dict[str, Any]] = []
    # Vowel-final hosts: -ng linker glued: bata-ng kumain
    for matrix_v in ("tumakbo", "natulog"):
        for rc_lemma in ("kain", "bili", "basa"):
            rc_verb = _VERB_FORMS[rc_lemma]["AV"]["PFV"]
            for head in ("bata", "babae", "lalaki", "ina"):
                for gen in _GEN_NPS[:2]:
                    _add(out, f"{matrix_v} ang {head}ng {rc_verb} {gen}",
                         "relativization: -ng linker, AV RC",
                         "parse")
    # Consonant-final hosts: standalone na linker (libro)
    for matrix_v in ("tumakbo",):
        for rc_lemma in ("basa", "kain"):
            rc_verb = _VERB_FORMS[rc_lemma]["OV"]["PFV"]
            for gen in _GEN_NPS[:2]:
                _add(out, f"{matrix_v} ang libro na {rc_verb} {gen}",
                     "relativization: na linker, OV RC",
                     "parse")
    # OBJ-relativization is rejected (SUBJ-only restriction). The
    # parser does still emit fragments for the partial NP / RC
    # spans, so the expected outcome is ``fragment`` rather than
    # ``fail``.
    for rc_verb in ("kinain", "binili"):
        _add(out, f"tumakbo ang batang {rc_verb} ang isda",
             "relativization: OBJ-rel rejected (SUBJ-only)",
             "fragment",
             notes="Tagalog SUBJ-only restriction; full parse fails, sub-spans surface as fragments")

    # Phase 5e Commit 4: multi-pronoun RC composition. Phase 5d
    # Commit 10's `_is_post_embedded_v_pron` Wackernagel exception
    # plus existing relativization compose to handle a matrix-
    # cluster PRON and an embedded RC-actor PRON in one sentence.
    for matrix_pron, rc_pron in [
        ("ko", "niya"),    # 1sg-GEN matrix + 3sg-GEN RC
        ("mo", "niya"),    # 2sg-GEN matrix + 3sg-GEN RC
        ("niya", "ko"),    # 3sg-GEN matrix + 1sg-GEN RC
    ]:
        _add(out, f"nakita {matrix_pron} ang batang kinain {rc_pron}",
             "relativization: multi-pronoun RC (matrix + embedded)",
             "parse")
    # Inner-NEG inside the RC.
    _add(out, "nakita ko ang batang hindi kinain niya",
         "relativization: multi-pronoun RC + inner NEG",
         "parse")

    # Phase 5e Commit 5: headless / free relatives. ``ang/ng/sa`` +
    # S_GAP forms an NP without an overt head noun; the headless
    # head's PRED is 'PRO' and the gapped clause sits in ADJ.
    _add(out, "tumakbo ang tumakbo",
         "relativization: headless RC (AV-INTR matrix + AV-INTR RC)",
         "parse")
    _add(out, "tumakbo ang kumain ng isda",
         "relativization: headless RC (AV-tr RC)",
         "parse")
    _add(out, "tumakbo ang kinain ng aso",
         "relativization: headless RC (OV-tr RC, patient pivot)",
         "parse")
    _add(out, "nakita ko ang tumakbo",
         "relativization: headless RC in OBJ position",
         "parse")
    _add(out, "tumakbo ang hindi kumain ng isda",
         "relativization: headless RC + inner NEG",
         "parse")

    # Phase 5e Commit 6: ``na`` linker disambiguation after PRON.
    # The PRON ``ko`` / ``mo`` / ``niya`` is the NP-internal
    # possessor of the head NOUN; the standalone ``na`` is the
    # linker introducing the RC, not the 2P aspectual clitic.
    _add(out, "tumakbo ang bata ko na kumain",
         "relativization: post-poss-PRON na linker (1sg)",
         "parse")
    _add(out, "tumakbo ang bata mo na kumain",
         "relativization: post-poss-PRON na linker (2sg)",
         "parse")
    _add(out, "tumakbo ang bata niya na kumain",
         "relativization: post-poss-PRON na linker (3sg)",
         "parse")
    _add(out, "tumakbo ang bata ko na kumain ng isda",
         "relativization: post-poss-PRON na linker + transitive RC",
         "parse")
    _add(out, "tumakbo ang bata ko na kinain ng aso",
         "relativization: post-poss-PRON na linker + OV RC",
         "parse")
    _add(out, "tumakbo ang bata ko na hindi kumain",
         "relativization: post-poss-PRON na linker + NEG-skip",
         "parse")
    return out


def _control_corpus() -> list[dict[str, Any]]:
    """§7.6: control verbs — psych, intransitive, transitive."""
    out: list[dict[str, Any]] = []
    # Psych: gusto, ayaw, kaya — GEN experiencer + complement
    for psych in ("gusto", "ayaw", "kaya"):
        for pron in ("ko", "mo", "niya", "namin", "nila"):
            for verb in ("kumain", "bumili", "natulog"):
                # vowel-final pronouns get -ng linker; CV-final get na
                pn_form = pron + "ng" if pron.endswith(
                    ("a", "e", "i", "o", "u")
                ) else pron + " na"
                _add(out, f"{psych} {pn_form} {verb}",
                     f"control: psych {psych}",
                     "parse")
            _add(out, f"{psych} {pron + 'ng' if pron.endswith(('a','e','i','o','u')) else pron + ' na'} kumain ng isda",
                 f"control: psych {psych} + transitive XCOMP",
                 "parse")

    # Intransitive: pumayag
    for nom in ("siya", "ako", "kami"):
        for verb in ("kumain", "tumakbo", "natulog"):
            pn_form = nom + "ng" if nom.endswith(
                ("a", "e", "i", "o", "u")
            ) else nom + " na"
            _add(out, f"pumayag {pn_form} {verb}",
                 "control: intransitive (pumayag)",
                 "parse")

    # Transitive OV: pinilit. Use the head-aware linker so
    # consonant-final NPs (``ang nanay``) use the standalone ``na``
    # rather than the (ungrammatical) ``nanayng``.
    for forcer in _GEN_NPS[:3]:
        for forcee in _NOM_NPS[:3]:
            _add(out, f"pinilit {forcer} {_linker_form(forcee)} kumain ng isda",
                 "control: transitive OV (pinilit)",
                 "parse")
    # Transitive DV: inutusan
    for orderer in _GEN_NPS[:2]:
        for orderee in ("si Maria", "si Juan"):
            _add(out, f"inutusan {orderer} {orderee} na umuwi",
                 "control: transitive DV (inutusan)",
                 "parse")

    # Negation under control: outer + inner
    for psych in ("gusto", "ayaw"):
        _add(out, f"hindi {psych} kong kumain",
             f"control: outer NEG + {psych}",
             "parse")
        _add(out, f"{psych} kong hindi kumain",
             f"control: inner NEG + {psych}",
             "parse")

    # Phase 5e Commit 8: control / raising composition pinning.
    # Existing Phase 5c §7.6 follow-on Commit 5 (raising at S level)
    # plus Phase 5d Commit 7 (raising at S_XCOMP level) compose
    # naturally; this adds explicit corpus coverage.
    # Control under raising — RAISING (linker form):
    _add(out, "mukhang gusto ng batang kumain",
         "control: control under mukha-raising (psych)",
         "parse")
    _add(out, "mukhang pumayag ang batang kumain",
         "control: control under mukha-raising (intrans)",
         "parse")
    _add(out, "bakang gusto ng batang kumain",
         "control: control under baka-raising (psych)",
         "parse")
    # Control under raising — RAISING_BARE (no linker):
    _add(out, "parang gusto ng batang kumain",
         "control: control under parang-raising (bare)",
         "parse")
    _add(out, "tila gusto ng batang kumain",
         "control: control under tila-raising (bare)",
         "parse")
    # TRANS control + raising in XCOMP:
    _add(out, "pinilit ng nanay ang batang mukhang umuwi",
         "control: TRANS + raising in XCOMP (mukha)",
         "parse")
    _add(out, "pinilit ng nanay ang batang parang umuwi",
         "control: TRANS + raising in XCOMP (parang)",
         "parse")
    # Negation composition:
    _add(out, "mukhang hindi gusto ng batang kumain",
         "control: control under raising + middle NEG",
         "parse")
    _add(out, "mukhang gusto ng batang hindi kumain",
         "control: control under raising + inner NEG",
         "parse")

    # Phase 5e Commit 9: nested-control composition with multi-arg
    # innermost. Phase 5c §7.6 Commit 3 nested-S_XCOMP rules
    # compose with Phase 5d Commit 8 (pa-OV under control) and
    # Commit 9 (IV multi-GEN under control); this adds explicit
    # corpus coverage.
    # Nested pa-OV under control:
    _add(out, "gusto kong pumayag na pakakainin ang bata",
         "control: nested pa-OV under control (psych+intrans)",
         "parse")
    _add(out, "gusto kong pumayag na pakakainin ang bata ng kanin",
         "control: nested 3-arg pa-OV under control",
         "parse")
    _add(out, "pumayag akong gustong pakakainin ang bata",
         "control: nested pa-OV under control (intrans+psych)",
         "parse")
    _add(out, "gusto kong gustong pakakainin ang bata",
         "control: nested pa-OV under psych+psych",
         "parse")
    # IV multi-GEN under nested control:
    _add(out, "gusto kong pumayag na ipaggagawa ang silya ng nanay",
         "control: nested IV-BEN 3-arg under control",
         "parse")
    _add(out, "gusto kong pumayag na ipaggagawa ang kapatid",
         "control: nested IV-BEN 2-arg under control",
         "parse")
    # Negation in nested compositions:
    _add(out, "gusto kong pumayag na hindi pakakainin ang bata",
         "control: nested pa-OV + innermost NEG",
         "parse")
    _add(out, "gusto kong hindi pumayag na pakakainin ang bata",
         "control: nested pa-OV + middle NEG",
         "parse")

    # Phase 5e Commit 10: 3-arg pa-DV (with overt PATIENT). New
    # lex profile + multi-GEN top-level rules + S_XCOMP rules
    # under control + S_GAP_OBJ_CAUSER / S_GAP_OBJ_PATIENT
    # extensions for ay-fronting.
    # Top-level 3-arg pa-DV across the three NP-order permutations:
    _add(out, "pinakainan ng nanay ng kanin ang bata",
         "causative: 3-arg pa-DV (GEN-GEN-NOM)",
         "parse")
    _add(out, "pinakainan ng nanay ang bata ng kanin",
         "causative: 3-arg pa-DV (GEN-NOM-GEN)",
         "parse")
    _add(out, "pinakainan ang bata ng nanay ng kanin",
         "causative: 3-arg pa-DV (NOM-GEN-GEN)",
         "parse")
    # Other anchor verbs:
    _add(out, "pinabasahan ng nanay ng libro ang bata",
         "causative: 3-arg pa-DV (basa)",
         "parse")
    # 3-arg pa-DV under control:
    _add(out, "gusto kong pakakainan ang bata ng kanin",
         "control: 3-arg pa-DV under psych control",
         "parse")
    _add(out, "pumayag akong pakakainan ang bata ng kanin",
         "control: 3-arg pa-DV under intrans control",
         "parse")
    # 3-arg pa-DV ay-fronting:
    _add(out, "ng nanay ay pinakainan ang bata ng kanin",
         "ay-inversion: 3-arg pa-DV CAUSER-fronted",
         "parse")
    _add(out, "ng kanin ay pinakainan ng nanay ang bata",
         "ay-inversion: 3-arg pa-DV PATIENT-fronted",
         "parse")

    # Phase 5e Commit 11: 3-arg plain DV (CAUS=NONE) ditransitives.
    # New intrinsic profile + sulat DV 3-arg lex entry + 3
    # multi-GEN-NP grammar rules.
    _add(out, "sinulatan ng nanay ng liham ang anak",
         "causative: 3-arg DV plain (GEN-GEN-NOM, sulat)",
         "parse")
    _add(out, "sinulatan ang anak ng nanay ng liham",
         "causative: 3-arg DV plain (NOM-GEN-GEN, sulat)",
         "parse")
    _add(out, "sinulatan ng nanay ang anak ng liham",
         "causative: 3-arg DV plain (GEN-NOM-GEN, sulat)",
         "parse")
    # IPFV aspect:
    _add(out, "sinusulatan ng nanay ng liham ang anak",
         "causative: 3-arg DV plain IPFV",
         "parse")
    return out


def _applicative_causative_corpus() -> list[dict[str, Any]]:
    """§7.7: ipag- benefactive applicative + pa-causatives."""
    out: list[dict[str, Any]] = []
    # ipag- benefactive
    for ben_form, ben_lemma in [
        ("ipinaggawa", "gawa"), ("ipinaggagawa", "gawa"), ("ipaggagawa", "gawa"),
        ("ipinagsulat", "sulat"), ("ipinagbili", "bili"),
    ]:
        for gen in _GEN_NPS[:3]:
            for nom in _NOM_NPS[:3]:
                _add(out, f"{ben_form} {gen} {nom}",
                     f"applicative: ipag- benefactive ({ben_lemma})",
                     "parse")
    # pa-...-in monoclausal causative OV
    for caus_form, caus_lemma in [
        ("pinakain", "kain"), ("pinakakain", "kain"), ("pakakainin", "kain"),
        ("pinabasa", "basa"), ("pinainom", "inom"),
    ]:
        for gen in _GEN_NPS[:3]:
            for nom in _NOM_NPS[:3]:
                _add(out, f"{caus_form} {gen} {nom}",
                     f"causative: pa-...-in OV monoclausal ({caus_lemma})",
                     "parse")
    # magpa- biclausal causative AV
    for caus_form, caus_lemma in [
        ("nagpakain", "kain"), ("nagpapakain", "kain"), ("magpapakain", "kain"),
        ("nagpabasa", "basa"), ("nagpainom", "inom"),
    ]:
        for nom in _NOM_NPS[:3]:
            _add(out, f"{caus_form} {nom} na kumain",
                 f"causative: magpa- AV biclausal ({caus_lemma})",
                 "parse")
            _add(out, f"{caus_form} {nom} na kumain ng isda",
                 "causative: magpa- AV biclausal + transitive XCOMP",
                 "parse")
    # ipang- instrumental applicative (Phase 5c §7.7 follow-on
    # Commit 4 lifted the deferral via the new ``nasal_assim_prefix``
    # sandhi op).
    for s in ("ipinambili ng titser ang panulat",):
        _add(out, s, "applicative: ipang- (instrumental, IV-INSTR)", "parse")
    return out


def _demonstrative_possessive_corpus() -> list[dict[str, Any]]:
    """§7.8: demonstratives, possessives, quantifier float."""
    out: list[dict[str, Any]] = []
    # Standalone demonstratives
    for verb in ("kumain", "tumakbo", "natulog"):
        for dem in ("ito", "iyan", "iyon"):
            _add(out, f"{verb} {dem}",
                 "demonstrative: standalone NOM",
                 "parse")
    # Demonstrative as OBJ (GEN)
    for verb in ("kumain", "bumasa"):
        for dem_g in ("nito", "niyan", "niyon"):
            for nom in _NOM_NPS[:2]:
                _add(out, f"{verb} {nom} {dem_g}",
                     "demonstrative: GEN demonstrative as OBJ",
                     "parse")
    # Possessive: ng-NP modifier
    for verb in ("kumain", "bumili"):
        for nom in _NOM_NPS[:3]:
            for gen_owner in ("ng nanay", "ng bata", "ng lalaki"):
                _add(out, f"{verb} {nom} ng isda {gen_owner}",
                     "possessive: ng-NP modifier on OBJ",
                     "parse")
    # Quantifier float
    for verb in ("kumain", "tumakbo"):
        for nom in _NOM_NPS[:3]:
            for q in ("lahat", "iba"):
                _add(out, f"{verb} {nom} {q}",
                     f"quantifier: floated {q}",
                     "parse")
    return out


def _robustness_corpus() -> list[dict[str, Any]]:
    """§7.9: failure cases that should produce fragments."""
    out: list[dict[str, Any]] = []
    # Incomplete NP
    _add(out, "kumain ng aso ang", "robustness: incomplete NP", "fragment")
    # Mid-sentence garbage: xyzqwerty is stripped as _UNK, leaving
    # ``kumain ng aso`` — no NOM-NP, so no full parse, but ng-aso
    # fragments out.
    _add(out, "kumain xyzqwerty ng aso", "robustness: garbage word",
         "fragment",
         notes="xyzqwerty stripped, but residue lacks NOM-NP")
    # No verb
    _add(out, "aso ang isda", "robustness: no verb", "fail",
         notes="no V → no rule predictions; no fragments either")
    # Half-built clause: ng with no following noun → no completed
    # NP rule; no fragments either.
    _add(out, "kumain ng", "robustness: incomplete GEN-NP", "fail",
         notes="ng without N produces no completed NP states")
    return out


def _classic_corpus() -> list[dict[str, Any]]:
    """Hand-authored "classic" Tagalog example sentences from the
    literature. Format: (text, construction, expected, source).

    The Ramos & Goulet 1981 sentences were mined from
    ``data/tgl/dictionaries/intermediate-tagalog-...txt`` (the
    OCR'd companion text of the bundled PDF) by filtering
    candidates whose vocabulary is fully in the seed lexicon.
    Page numbers are omitted — the .txt loses page boundaries in
    OCR. Future enrichment can hand-correlate citations to the
    physical pages."""
    return [
        {"text": "Kumain ang aso ng isda.",
         "construction": "classic: AV transitive (Kroeger)",
         "expected": "parse",
         "source": "Kroeger 1993 §1"},
        {"text": "Kinain ng aso ang isda.",
         "construction": "classic: OV transitive (Kroeger)",
         "expected": "parse",
         "source": "Kroeger 1993 §1"},
        {"text": "Sumulat si Juan kay Maria.",
         "construction": "classic: AV with DAT recipient",
         "expected": "parse",
         "source": "Schachter & Otanes 1972"},
        {"text": "Sinulatan ni Juan si Maria.",
         "construction": "classic: DV — Maria=pivot",
         "expected": "parse",
         "source": "Schachter & Otanes 1972"},
        {"text": "Isinulat ni Juan ang liham.",
         "construction": "classic: IV — liham=pivot",
         "expected": "parse",
         "source": "Schachter & Otanes 1972"},
        {"text": "Gusto kong kumain ng isda.",
         "construction": "classic: psych control (Kroeger)",
         "expected": "parse",
         "source": "Kroeger 1993 §6"},
        {"text": "Pumayag siyang kumain.",
         "construction": "classic: intransitive control",
         "expected": "parse",
         "source": "Schachter & Otanes 1972"},
        {"text": "Pinakain ng nanay ang bata.",
         "construction": "classic: monoclausal causative",
         "expected": "parse",
         "source": "Schachter & Otanes 1972 §5.34"},
        {"text": "Si Maria ay kumain.",
         "construction": "classic: ay-inversion",
         "expected": "parse",
         "source": "Schachter & Otanes 1972"},
        {"text": "Tumakbo ang batang kumain.",
         "construction": "classic: relativization",
         "expected": "parse",
         "source": "Kroeger 1993 §1"},
        {"text": "Kumain na ang aso.",
         "construction": "classic: aspectual na",
         "expected": "parse",
         "source": "Schachter & Otanes 1972 §6.7"},
        {"text": "Hindi kumain ang aso.",
         "construction": "classic: declarative negation",
         "expected": "parse",
         "source": "Schachter & Otanes 1972"},
        # === Ramos & Goulet 1981, Intermediate Tagalog =============
        # Sentences mined from the OCR'd companion .txt by filtering
        # for fully-seed-vocabulary candidates that the Phase 4
        # grammar parses successfully. Source citation is the book
        # as a whole; page-level cross-reference deferred.
        {"text": "Aalis na ako.",
         "construction": "rg: AV-CTPL with na-clitic",
         "expected": "parse",
         "source": "Ramos & Goulet 1981"},
        {"text": "Hindi ka nakita ng kaibigan mo.",
         "construction": "rg: NEG + OV (kita)",
         "expected": "parse",
         "source": "Ramos & Goulet 1981"},
        {"text": "Bumili siya ng bahay.",
         "construction": "rg: AV transitive (bili)",
         "expected": "parse",
         "source": "Ramos & Goulet 1981"},
        {"text": "Kumain ka na ba?",
         "construction": "rg: question with adv enclitics na/ba",
         "expected": "parse",
         "source": "Ramos & Goulet 1981"},
        {"text": "Dumating na siya.",
         "construction": "rg: AV-PFV (dating) with na",
         "expected": "parse",
         "source": "Ramos & Goulet 1981"},
        {"text": "Kumakanta siya.",
         "construction": "rg: AV-IPFV (kanta)",
         "expected": "parse",
         "source": "Ramos & Goulet 1981"},
        {"text": "Nauhaw ang aso.",
         "construction": "rg: AV-PFV NVOL (uhaw)",
         "expected": "parse",
         "source": "Ramos & Goulet 1981"},
        {"text": "Nagdaan na ba ang bus?",
         "construction": "rg: question with na/ba (daan)",
         "expected": "parse",
         "source": "Ramos & Goulet 1981"},
        {"text": "Kumain na ako.",
         "construction": "rg: aspectual na",
         "expected": "parse",
         "source": "Ramos & Goulet 1981"},
        {"text": "Umabot ka ng kanin.",
         "construction": "rg: AV transitive imperative-like (abot)",
         "expected": "parse",
         "source": "Ramos & Goulet 1981"},
        {"text": "Yayaman siya.",
         "construction": "rg: AV-CTPL (yaman)",
         "expected": "parse",
         "source": "Ramos & Goulet 1981"},
        {"text": "Umiyak ang bata.",
         "construction": "rg: AV intransitive (iyak)",
         "expected": "parse",
         "source": "Ramos & Goulet 1981"},
        {"text": "Hindi umiiyak ang bata.",
         "construction": "rg: NEG + AV-IPFV intransitive",
         "expected": "parse",
         "source": "Ramos & Goulet 1981"},
        {"text": "Siya ay tumakbo.",
         "construction": "rg: ay-inversion (takbo)",
         "expected": "parse",
         "source": "Ramos & Goulet 1981"},
        {"text": "Pumunta ka na.",
         "construction": "rg: AV-PFV imperative-like (punta)",
         "expected": "parse",
         "source": "Ramos & Goulet 1981"},
        {"text": "Pupunta ka ba?",
         "construction": "rg: AV-CTPL question (punta)",
         "expected": "parse",
         "source": "Ramos & Goulet 1981"},
        {"text": "Umalis siya.",
         "construction": "rg: AV intransitive (alis)",
         "expected": "parse",
         "source": "Ramos & Goulet 1981"},
        {"text": "Dumating siya.",
         "construction": "rg: AV-PFV (dating)",
         "expected": "parse",
         "source": "Ramos & Goulet 1981"},
        {"text": "Hinuli niya ang manok.",
         "construction": "rg: OV-PFV (huli) + niya",
         "expected": "parse",
         "source": "Ramos & Goulet 1981"},
        {"text": "Nakita niya ang manok.",
         "construction": "rg: OV-PFV NVOL (kita)",
         "expected": "parse",
         "source": "Ramos & Goulet 1981"},
    ]


def _all_corpus() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    out.extend(_voice_aspect_corpus())
    out.extend(_negation_corpus())
    out.extend(_clitic_corpus())
    out.extend(_ay_inversion_corpus())
    out.extend(_relativization_corpus())
    out.extend(_control_corpus())
    out.extend(_applicative_causative_corpus())
    out.extend(_demonstrative_possessive_corpus())
    out.extend(_robustness_corpus())
    out.extend(_classic_corpus())
    return out


def main() -> None:
    corpus = _all_corpus()
    print(f"Generated {len(corpus)} sentences", file=sys.stderr)
    _OUT.parent.mkdir(parents=True, exist_ok=True)
    with _OUT.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(
            corpus, fh,
            default_flow_style=False, allow_unicode=True, sort_keys=False,
        )
    print(f"Wrote {_OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
