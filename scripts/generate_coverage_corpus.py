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
    """§7.4: ay-inversion. Limited to pivot SUBJ fronting (per the
    implementation; non-pivot deferred)."""
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
    # Out-of-scope: ipang- (deferred — homorganic nasal sandhi)
    for s in ("ipinambili ng titser ang panulat",):
        _add(out, s, "applicative: ipang- (deferred)", "fail")
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
    literature. Format: (text, construction, expected, source)."""
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
