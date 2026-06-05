# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Paired surface↔analysis assertions across the seed verb lexicon.

Each entry is ``(root, voice, aspect, expected_surface)`` for a cell
the root participates in (per its ``affix_class``). The full table
gives ~300 paired assertions covering the kain/bili anchors plus 25+
additional verbs spanning the diversity of affix classes — -um-/mag-
alternations, mang- distributive (with nasal substitution), maka-
abilitative, intransitives, vowel-initial roots, and consonant-
initial roots that exercise the standard sandhi.

Citations: Ramos & Bautista 1986 (R&B), Schachter & Otanes 1972 (S&O)
verbal chart, and Kroeger 1993 ch. 4. Where R&B and S&O attest a form
in a different shape, the form here matches R&B (the more recent and
more comprehensively paradigmatized source) and the discrepancy is
recorded in ``docs/analysis-choices.md``.
"""

import pytest

from tgllfg.core.common import Token
from tgllfg.morph import Analyzer, generate_form, load_morph_data


# === Paired assertion table ==============================================
#
# Format: (root, voice, aspect, expected_surface).
# Mood is IND for everything except maka- (ABIL) — checked separately.

# -- -um- class transitives ----------------------------------------------

UM_PARADIGM_FORMS = [
    # kain — eat
    ("kain", "AV", "PFV",  "kumain"),
    ("kain", "AV", "IPFV", "kumakain"),
    ("kain", "AV", "CTPL", "kakain"),
    ("kain", "OV", "PFV",  "kinain"),
    ("kain", "OV", "IPFV", "kinakain"),
    ("kain", "OV", "CTPL", "kakainin"),
    ("kain", "DV", "PFV",  "kinainan"),
    ("kain", "DV", "IPFV", "kinakainan"),
    ("kain", "DV", "CTPL", "kakainan"),
    ("kain", "IV", "PFV",  "ikinain"),
    ("kain", "IV", "IPFV", "ikinakain"),
    ("kain", "IV", "CTPL", "ikakain"),
    # bili — buy (vowel-final, exercises hiatus sandhi on -in/-an)
    ("bili", "AV", "PFV",  "bumili"),
    ("bili", "AV", "IPFV", "bumibili"),
    ("bili", "AV", "CTPL", "bibili"),
    ("bili", "OV", "PFV",  "binili"),
    ("bili", "OV", "IPFV", "binibili"),
    ("bili", "OV", "CTPL", "bibilihin"),
    ("bili", "DV", "PFV",  "binilihan"),
    ("bili", "DV", "IPFV", "binibilihan"),
    ("bili", "DV", "CTPL", "bibilihan"),
    ("bili", "IV", "PFV",  "ibinili"),
    ("bili", "IV", "IPFV", "ibinibili"),
    ("bili", "IV", "CTPL", "ibibili"),
    # inom — drink
    ("inom", "AV", "PFV",  "uminom"),
    ("inom", "AV", "IPFV", "umiinom"),
    ("inom", "AV", "CTPL", "iinom"),
    ("inom", "OV", "PFV",  "ininom"),
    ("inom", "OV", "IPFV", "iniinom"),
    # NB: o→u stem-vowel raising on suffixation is now applied
    # the engine doesn't model this Phase 2 root-specific rule, so
    # automatically (Phase 2C sandhi rule).
    ("inom", "OV", "CTPL", "iinumin"),
    # basa — read
    ("basa", "AV", "PFV",  "bumasa"),
    ("basa", "AV", "IPFV", "bumabasa"),
    ("basa", "AV", "CTPL", "babasa"),
    ("basa", "OV", "PFV",  "binasa"),
    ("basa", "OV", "IPFV", "binabasa"),
    ("basa", "OV", "CTPL", "babasahin"),
    ("basa", "DV", "PFV",  "binasahan"),
    ("basa", "DV", "IPFV", "binabasahan"),
    ("basa", "DV", "CTPL", "babasahan"),
    # gawa — do, make
    ("gawa", "AV", "PFV",  "gumawa"),
    ("gawa", "AV", "IPFV", "gumagawa"),
    ("gawa", "AV", "CTPL", "gagawa"),
    ("gawa", "OV", "PFV",  "ginawa"),
    ("gawa", "OV", "IPFV", "ginagawa"),
    # Phase 9.X.pre-4.2: gawa OV/CTPL/IND surface flipped from
    # `gagawahin` (h-epenthesis default) to `gagawin` after the
    # `a_deletion` sandhi flag was added to the gawa root.
    ("gawa", "OV", "CTPL", "gagawin"),
    # gamit — use
    ("gamit", "AV", "PFV",  "gumamit"),
    ("gamit", "AV", "IPFV", "gumagamit"),
    ("gamit", "AV", "CTPL", "gagamit"),
    ("gamit", "OV", "PFV",  "ginamit"),
    ("gamit", "OV", "IPFV", "ginagamit"),
    ("gamit", "OV", "CTPL", "gagamitin"),
    # tawag — call
    ("tawag", "AV", "PFV",  "tumawag"),
    ("tawag", "AV", "IPFV", "tumatawag"),
    ("tawag", "AV", "CTPL", "tatawag"),
    ("tawag", "OV", "PFV",  "tinawag"),
    ("tawag", "OV", "IPFV", "tinatawag"),
    ("tawag", "OV", "CTPL", "tatawagin"),
    # bilang — count
    ("bilang", "AV", "PFV",  "bumilang"),
    ("bilang", "AV", "IPFV", "bumibilang"),
    ("bilang", "AV", "CTPL", "bibilang"),
    ("bilang", "OV", "PFV",  "binilang"),
    ("bilang", "OV", "IPFV", "binibilang"),
    ("bilang", "OV", "CTPL", "bibilangin"),
    # putol — cut
    ("putol", "AV", "PFV",  "pumutol"),
    ("putol", "AV", "IPFV", "pumuputol"),
    ("putol", "AV", "CTPL", "puputol"),
    ("putol", "OV", "PFV",  "pinutol"),
    ("putol", "OV", "IPFV", "pinuputol"),
    # Same o→u raising as inom (puputol → puputul- before -in).
    ("putol", "OV", "CTPL", "puputulin"),
]

# -- mag- class verbs ----------------------------------------------------

MAG_PARADIGM_FORMS = [
    # linis — clean (mag- only in seed; OV requires sonorant -in- → ni-,
    # deferred to Phase 2C).
    ("linis", "AV", "PFV",  "naglinis"),
    ("linis", "AV", "IPFV", "naglilinis"),
    ("linis", "AV", "CTPL", "maglilinis"),
    # bigay — give
    ("bigay", "AV", "PFV",  "nagbigay"),
    ("bigay", "AV", "IPFV", "nagbibigay"),
    ("bigay", "AV", "CTPL", "magbibigay"),
    # luto — cook
    ("luto", "AV", "PFV",  "nagluto"),
    ("luto", "AV", "IPFV", "nagluluto"),
    ("luto", "AV", "CTPL", "magluluto"),
    # hatid — bring, deliver
    ("hatid", "AV", "PFV",  "naghatid"),
    ("hatid", "AV", "IPFV", "naghahatid"),
    ("hatid", "AV", "CTPL", "maghahatid"),
    # bayad — pay
    ("bayad", "AV", "PFV",  "nagbayad"),
    ("bayad", "AV", "IPFV", "nagbabayad"),
    ("bayad", "AV", "CTPL", "magbabayad"),
    # bihis — dress
    ("bihis", "AV", "PFV",  "nagbihis"),
    ("bihis", "AV", "IPFV", "nagbibihis"),
    ("bihis", "AV", "CTPL", "magbibihis"),
    # tayo — build
    ("tayo", "AV", "PFV",  "nagtayo"),
    ("tayo", "AV", "IPFV", "nagtatayo"),
    ("tayo", "AV", "CTPL", "magtatayo"),
    # ipon — collect (Phase 10.Y: vowel-initial root → hyphenated mag/nag prefix)
    ("ipon", "AV", "PFV",  "nag-ipon"),
    ("ipon", "AV", "IPFV", "nag-iipon"),
    ("ipon", "AV", "CTPL", "mag-iipon"),
    # trabaho — work
    ("trabaho", "AV", "PFV",  "nagtrabaho"),
    # Phase 9.X.c6: trabaho gets sandhi_flags: [cluster_redup] to
    # preserve the Cr- onset in CV-redup (audit-attested
    # ``nagtratrabaho`` over the cluster-stripped ``nagtatrabaho``;
    # both are real Tagalog, the cluster variant matches the audit).
    ("trabaho", "AV", "IPFV", "nagtratrabaho"),
    ("trabaho", "AV", "CTPL", "magtratrabaho"),
    # hintay — wait
    ("hintay", "AV", "PFV",  "naghintay"),
    ("hintay", "AV", "IPFV", "naghihintay"),
    ("hintay", "AV", "CTPL", "maghihintay"),
    # palit — change
    ("palit", "AV", "PFV",  "nagpalit"),
    ("palit", "AV", "IPFV", "nagpapalit"),
    ("palit", "AV", "CTPL", "magpapalit"),
    # punas — wipe
    ("punas", "AV", "PFV",  "nagpunas"),
    ("punas", "AV", "IPFV", "nagpupunas"),
    ("punas", "AV", "CTPL", "magpupunas"),
]

# -- -um/mag alternations ------------------------------------------------

UM_MAG_PARADIGM_FORMS = [
    # sulat — write (both -um- and mag- AV)
    ("sulat", "AV", "PFV",  "sumulat"),
    ("sulat", "AV", "IPFV", "sumusulat"),
    ("sulat", "AV", "CTPL", "susulat"),
    ("sulat", "OV", "PFV",  "sinulat"),
    ("sulat", "OV", "IPFV", "sinusulat"),
    ("sulat", "OV", "CTPL", "susulatin"),
    # sayaw — dance
    ("sayaw", "AV", "PFV",  "sumayaw"),
    ("sayaw", "AV", "IPFV", "sumasayaw"),
    ("sayaw", "AV", "CTPL", "sasayaw"),
    # balik — return (AV with both -um- and mag-)
    ("balik", "AV", "PFV",  "bumalik"),
    ("balik", "AV", "IPFV", "bumabalik"),
    ("balik", "AV", "CTPL", "babalik"),
    # akyat — climb
    ("akyat", "AV", "PFV",  "umakyat"),
    ("akyat", "AV", "IPFV", "umaakyat"),
    ("akyat", "AV", "CTPL", "aakyat"),
    ("akyat", "OV", "PFV",  "inakyat"),
    ("akyat", "OV", "IPFV", "inaakyat"),
    ("akyat", "OV", "CTPL", "aakyatin"),
    # lipat — transfer
    ("lipat", "AV", "PFV",  "lumipat"),
    ("lipat", "AV", "IPFV", "lumilipat"),
    ("lipat", "AV", "CTPL", "lilipat"),
    # tawid — cross
    ("tawid", "AV", "PFV",  "tumawid"),
    ("tawid", "AV", "IPFV", "tumatawid"),
    ("tawid", "AV", "CTPL", "tatawid"),
]

# -- mang- distributive --------------------------------------------------

MANG_PARADIGM_FORMS = [
    # bili — shop (mang- + bili → mamili series)
    ("bili", "AV", "PFV",  "namili"),
    ("bili", "AV", "IPFV", "namimili"),
    ("bili", "AV", "CTPL", "mamimili"),
    # kuha — gather (mang- + kuha → manguha; k → ng)
    ("kuha", "AV", "PFV",  "nanguha"),
    ("kuha", "AV", "IPFV", "nangunguha"),
    ("kuha", "AV", "CTPL", "mangunguha"),
    # tahi — sew distributively (mang- + tahi → nanahi; t → n)
    ("tahi", "AV", "PFV",  "nanahi"),
    ("tahi", "AV", "IPFV", "nananahi"),
    ("tahi", "AV", "CTPL", "mananahi"),
    # putol — cut up (mang- + putol → namutol; p → m)
    ("putol", "AV", "PFV",  "namutol"),
    ("putol", "AV", "IPFV", "namumutol"),
    ("putol", "AV", "CTPL", "mamumutol"),
]

# -- maka- abilitative (MOOD=ABIL) ---------------------------------------

MAKA_PARADIGM_FORMS = [
    ("kain",  "AV", "PFV",  "nakakain"),
    ("kain",  "AV", "IPFV", "nakakakain"),
    ("kain",  "AV", "CTPL", "makakakain"),
    ("bili",  "AV", "PFV",  "nakabili"),
    ("bili",  "AV", "IPFV", "nakabibili"),
    ("bili",  "AV", "CTPL", "makabibili"),
    ("tulog", "AV", "PFV",  "nakatulog"),
    ("tulog", "AV", "IPFV", "nakatutulog"),
    ("tulog", "AV", "CTPL", "makatutulog"),
    ("sulat", "AV", "PFV",  "nakasulat"),
    ("sulat", "AV", "IPFV", "nakasusulat"),
    ("sulat", "AV", "CTPL", "makasusulat"),
    ("basa",  "AV", "PFV",  "nakabasa"),
    ("basa",  "AV", "IPFV", "nakababasa"),
    ("basa",  "AV", "CTPL", "makababasa"),
]

# -- Intransitives -------------------------------------------------------

INTR_PARADIGM_FORMS = [
    # takbo — run
    ("takbo", "AV", "PFV",  "tumakbo"),
    ("takbo", "AV", "IPFV", "tumatakbo"),
    ("takbo", "AV", "CTPL", "tatakbo"),
    # alis — depart (vowel-initial)
    ("alis", "AV", "PFV",  "umalis"),
    ("alis", "AV", "IPFV", "umaalis"),
    ("alis", "AV", "CTPL", "aalis"),
    # dating — arrive. /d/ → /r/ intervocalic (Phase 2C; declared on
    # the root via sandhi_flags=[d_to_r]). PFV "dumating" keeps /d/
    # because it's adjacent to /m/ (not vowel-bracketed); IPFV and
    # CTPL surface the /r/.
    ("dating", "AV", "PFV",  "dumating"),
    ("dating", "AV", "IPFV", "dumarating"),
    ("dating", "AV", "CTPL", "darating"),
    # tawa — laugh
    ("tawa", "AV", "PFV",  "tumawa"),
    ("tawa", "AV", "IPFV", "tumatawa"),
    ("tawa", "AV", "CTPL", "tatawa"),
    # iyak — cry
    ("iyak", "AV", "PFV",  "umiyak"),
    ("iyak", "AV", "IPFV", "umiiyak"),
    ("iyak", "AV", "CTPL", "iiyak"),
    # lakad — walk
    ("lakad", "AV", "PFV",  "lumakad"),
    ("lakad", "AV", "IPFV", "lumalakad"),
    ("lakad", "AV", "CTPL", "lalakad"),
    # tulog — sleep. "natulog" is the ma- non-volitional PFV which
    # the engine doesn't yet model (Phase 2C); the canonical mag-
    # forms are asserted here.
    ("tulog", "AV", "PFV",  "nagtulog"),
    ("tulog", "AV", "IPFV", "nagtutulog"),
    ("tulog", "AV", "CTPL", "magtutulog"),
]


# -- ma- non-volitional (MOOD=NVOL) --------------------------------------
#
# Phase 2C: ma- AV class for non-volitional / accidental / stative
# readings, distinct from maka- abilitative (MOOD=ABIL). The realis
# carries the na- prefix (PFV/IPFV) and the irrealis carries ma-
# (CTPL); both pattern with cv-redup in IPFV/CTPL.

MA_NVOL_PARADIGM_FORMS = [
    ("tulog", "AV", "PFV",  "natulog"),
    ("tulog", "AV", "IPFV", "natutulog"),
    ("tulog", "AV", "CTPL", "matutulog"),
]


# -- Sonorant-initial roots: realis -in- → ni- prefix --------------------
#
# Phase 2C: when a non-AV cell applies the realis -in- infix to a
# sonorant-initial base (m, n, ng, l, r, w, y, h), the infix surfaces
# as a ni- prefix instead.

SONORANT_NI_PARADIGM_FORMS = [
    ("linis", "OV", "PFV",  "nilinis"),
    ("linis", "OV", "IPFV", "nililinis"),
    ("linis", "OV", "CTPL", "lilinisin"),
    ("linis", "DV", "PFV",  "nilinisan"),
    ("linis", "DV", "IPFV", "nililinisan"),
    ("linis", "DV", "CTPL", "lilinisan"),
]


# -- /d/ → /r/ intervocalic alternation ----------------------------------
#
# Phase 2C: per-root opt-in via sandhi_flags=[d_to_r]. Catches
# stem-internal d→r in reduplication (dadating → darating) and stem-
# suffix-boundary d→r (lakadin → lakarin). PFV "dumating" keeps /d/
# because position is /m_a/, not vowel-vowel.

D_TO_R_PARADIGM_FORMS = [
    # dating exercises stem-internal d→r in cv-redup.
    ("dating", "AV", "IPFV", "dumarating"),
    ("dating", "AV", "CTPL", "darating"),
    # bayad exercises stem-suffix-boundary d→r on -an attachment.
    ("bayad", "DV", "CTPL", "babayaran"),
    # dama: stem-internal d→r in CV-redup carries through CTPL.
    ("dama", "AV", "IPFV", "dumarama"),
    ("dama", "AV", "CTPL", "darama"),
]


# -- Phase 4 §7.2: RECPFV (recent-perfective) ----------------------------
#
# ka- + CV-redup of the root, no infix or voice-marking suffix. Uniform
# across um / mag / ma affix-classes.

RECPFV_PARADIGM_FORMS = [
    ("kain",   "AV", "RECPFV", "kakakain"),
    ("bili",   "AV", "RECPFV", "kabibili"),
    ("basa",   "AV", "RECPFV", "kababasa"),
    ("sulat",  "AV", "RECPFV", "kasusulat"),
    ("linis",  "AV", "RECPFV", "kalilinis"),
    ("tulog",  "AV", "RECPFV", "katutulog"),
    ("gawa",   "AV", "RECPFV", "kagagawa"),
    ("bigay",  "AV", "RECPFV", "kabibigay"),
]


# -- Phase 2C bulk verb scale-up — AV PFV/IPFV/CTPL ----------------------
#
# Three-cell coverage for ~50 newly-seeded verbs. Class chosen per
# verb based on its primary affix-class membership; non-AV cells are
# tested below in PHASE2C_NON_AV_FORMS where the engine generates
# stable surfaces.

PHASE2C_UM_AV_FORMS = [
    ("abot",   "AV", "PFV",  "umabot"),
    ("abot",   "AV", "IPFV", "umaabot"),
    ("abot",   "AV", "CTPL", "aabot"),
    ("buhat",  "AV", "PFV",  "bumuhat"),
    ("buhat",  "AV", "IPFV", "bumubuhat"),
    ("buhat",  "AV", "CTPL", "bubuhat"),
    ("higop",  "AV", "PFV",  "humigop"),
    ("higop",  "AV", "IPFV", "humihigop"),
    ("higop",  "AV", "CTPL", "hihigop"),
    ("kagat",  "AV", "PFV",  "kumagat"),
    ("kagat",  "AV", "IPFV", "kumakagat"),
    ("kagat",  "AV", "CTPL", "kakagat"),
    ("lunok",  "AV", "PFV",  "lumunok"),
    ("lunok",  "AV", "IPFV", "lumulunok"),
    ("lunok",  "AV", "CTPL", "lulunok"),
    ("piga",   "AV", "PFV",  "pumiga"),
    ("piga",   "AV", "IPFV", "pumipiga"),
    ("piga",   "AV", "CTPL", "pipiga"),
    ("pukol",  "AV", "PFV",  "pumukol"),
    ("pukol",  "AV", "IPFV", "pumupukol"),
    ("pukol",  "AV", "CTPL", "pupukol"),
    ("sigaw",  "AV", "PFV",  "sumigaw"),
    ("sigaw",  "AV", "IPFV", "sumisigaw"),
    ("sigaw",  "AV", "CTPL", "sisigaw"),
    ("subo",   "AV", "PFV",  "sumubo"),
    ("subo",   "AV", "IPFV", "sumusubo"),
    ("subo",   "AV", "CTPL", "susubo"),
    ("tanong", "AV", "PFV",  "tumanong"),
    ("tanong", "AV", "IPFV", "tumatanong"),
    ("tanong", "AV", "CTPL", "tatanong"),
    ("tikim",  "AV", "PFV",  "tumikim"),
    ("tikim",  "AV", "IPFV", "tumitikim"),
    ("tikim",  "AV", "CTPL", "titikim"),
    ("tira",   "AV", "PFV",  "tumira"),
    ("tira",   "AV", "IPFV", "tumitira"),
    ("tira",   "AV", "CTPL", "titira"),
    ("hampas", "AV", "PFV",  "humampas"),
    ("hampas", "AV", "IPFV", "humahampas"),
    ("hampas", "AV", "CTPL", "hahampas"),
    ("higit",  "AV", "PFV",  "humigit"),
    ("higit",  "AV", "IPFV", "humihigit"),
    ("higit",  "AV", "CTPL", "hihigit"),
    ("hingi",  "AV", "PFV",  "humingi"),
    ("hingi",  "AV", "IPFV", "humihingi"),
    ("hingi",  "AV", "CTPL", "hihingi"),
    ("punta",  "AV", "PFV",  "pumunta"),
    ("punta",  "AV", "IPFV", "pumupunta"),
    ("punta",  "AV", "CTPL", "pupunta"),
    ("daan",   "AV", "PFV",  "dumaan"),
    ("daan",   "AV", "IPFV", "dumadaan"),
    ("daan",   "AV", "CTPL", "dadaan"),
    ("baba",   "AV", "PFV",  "bumaba"),
    ("baba",   "AV", "IPFV", "bumababa"),
    ("baba",   "AV", "CTPL", "bababa"),
    ("labas",  "AV", "PFV",  "lumabas"),
    ("labas",  "AV", "IPFV", "lumalabas"),
    ("labas",  "AV", "CTPL", "lalabas"),
    ("tindig", "AV", "PFV",  "tumindig"),
    ("tindig", "AV", "IPFV", "tumitindig"),
    ("tindig", "AV", "CTPL", "titindig"),
    ("layo",   "AV", "PFV",  "lumayo"),
    ("layo",   "AV", "IPFV", "lumalayo"),
    ("layo",   "AV", "CTPL", "lalayo"),
    ("uwi",    "AV", "PFV",  "umuwi"),
    ("uwi",    "AV", "IPFV", "umuuwi"),
    ("uwi",    "AV", "CTPL", "uuwi"),
    ("ngiti",  "AV", "PFV",  "ngumiti"),
    ("ngiti",  "AV", "IPFV", "ngumingiti"),
    ("ngiti",  "AV", "CTPL", "ngingiti"),
    ("nguya",  "AV", "PFV",  "ngumuya"),
    ("nguya",  "AV", "IPFV", "ngumunguya"),
    ("nguya",  "AV", "CTPL", "ngunguya"),
]


PHASE2C_MAG_AV_FORMS = [
    # Phase 10.Y: vowel-initial roots → hyphenated mag/nag prefix
    ("aral",    "AV", "PFV",  "nag-aral"),
    ("aral",    "AV", "IPFV", "nag-aaral"),
    ("aral",    "AV", "CTPL", "mag-aaral"),
    ("ayos",    "AV", "PFV",  "nag-ayos"),
    ("ayos",    "AV", "IPFV", "nag-aayos"),
    ("ayos",    "AV", "CTPL", "mag-aayos"),
    ("bisita",  "AV", "PFV",  "nagbisita"),
    ("bisita",  "AV", "IPFV", "nagbibisita"),
    ("bisita",  "AV", "CTPL", "magbibisita"),
    ("handa",   "AV", "PFV",  "naghanda"),
    ("handa",   "AV", "IPFV", "naghahanda"),
    ("handa",   "AV", "CTPL", "maghahanda"),
    ("isip",    "AV", "PFV",  "nag-isip"),
    ("isip",    "AV", "IPFV", "nag-iisip"),
    ("isip",    "AV", "CTPL", "mag-iisip"),
    ("kuwento", "AV", "PFV",  "nagkuwento"),
    ("kuwento", "AV", "IPFV", "nagkukuwento"),
    ("kuwento", "AV", "CTPL", "magkukuwento"),
    ("maneho",  "AV", "PFV",  "nagmaneho"),
    ("maneho",  "AV", "IPFV", "nagmamaneho"),
    ("maneho",  "AV", "CTPL", "magmamaneho"),
    ("usap",    "AV", "PFV",  "nag-usap"),
    ("usap",    "AV", "IPFV", "nag-uusap"),
    ("usap",    "AV", "CTPL", "mag-uusap"),
    ("balak",   "AV", "PFV",  "nagbalak"),
    ("balak",   "AV", "IPFV", "nagbabalak"),
    ("balak",   "AV", "CTPL", "magbabalak"),
    ("hamon",   "AV", "PFV",  "naghamon"),
    ("hamon",   "AV", "IPFV", "naghahamon"),
    ("hamon",   "AV", "CTPL", "maghahamon"),
    ("tapon",   "AV", "PFV",  "nagtapon"),
    ("tapon",   "AV", "IPFV", "nagtatapon"),
    ("tapon",   "AV", "CTPL", "magtatapon"),
    ("butas",   "AV", "PFV",  "nagbutas"),
    ("butas",   "AV", "IPFV", "nagbubutas"),
    ("butas",   "AV", "CTPL", "magbubutas"),
    ("baon",    "AV", "PFV",  "nagbaon"),
    ("baon",    "AV", "IPFV", "nagbabaon"),
    ("baon",    "AV", "CTPL", "magbabaon"),
]


PHASE2C_MA_NVOL_FORMS = [
    ("gising",  "AV", "PFV",  "nagising"),
    ("gising",  "AV", "IPFV", "nagigising"),
    ("gising",  "AV", "CTPL", "magigising"),
    ("upo",     "AV", "PFV",  "naupo"),
    ("upo",     "AV", "IPFV", "nauupo"),
    ("upo",     "AV", "CTPL", "mauupo"),
    ("higa",    "AV", "PFV",  "nahiga"),
    ("higa",    "AV", "IPFV", "nahihiga"),
    ("higa",    "AV", "CTPL", "mahihiga"),
    ("dapa",    "AV", "PFV",  "nadapa"),
    ("dapa",    "AV", "IPFV", "nadadapa"),
    ("dapa",    "AV", "CTPL", "madadapa"),
    ("kita",    "AV", "PFV",  "nakita"),
    ("kita",    "AV", "IPFV", "nakikita"),
    ("kita",    "AV", "CTPL", "makikita"),
    # Phase 5n.A Commit 1: gulat / galit pruned — moved to ADJ
    # (``magulat`` / ``magalit`` are now ma_adj surfaces, not verbal
    # NVOL forms). See data/tgl/adjectives.yaml Body/condition section.
    ("takot",   "AV", "PFV",  "natakot"),
    ("takot",   "AV", "IPFV", "natatakot"),
    ("takot",   "AV", "CTPL", "matatakot"),
    ("lungkot", "AV", "PFV",  "nalungkot"),
    ("lungkot", "AV", "IPFV", "nalulungkot"),
    ("lungkot", "AV", "CTPL", "malulungkot"),
    ("saya",    "AV", "PFV",  "nasaya"),
    ("saya",    "AV", "IPFV", "nasasaya"),
    ("saya",    "AV", "CTPL", "masasaya"),
    ("inis",    "AV", "PFV",  "nainis"),
    ("inis",    "AV", "IPFV", "naiinis"),
    ("inis",    "AV", "CTPL", "maiinis"),
    ("sira",    "AV", "PFV",  "nasira"),
    ("sira",    "AV", "IPFV", "nasisira"),
    ("sira",    "AV", "CTPL", "masisira"),
]


PHASE2C_MANG_AV_FORMS = [
    # /d/ → /n/ via nasal substitution.
    ("dukot",   "AV", "PFV",  "nanukot"),
    ("dukot",   "AV", "IPFV", "nanunukot"),
    ("dukot",   "AV", "CTPL", "manunukot"),
    # /k/ → /ng/ via nasal substitution.
    ("kabit",   "AV", "PFV",  "nangabit"),
    ("kabit",   "AV", "IPFV", "nangangabit"),
    ("kabit",   "AV", "CTPL", "mangangabit"),
]


# -- Selected non-AV cells from the bulk additions ------------------------
#
# Spot-checks for OV/DV/IV cells where the expected surface is stable.
# Includes a sonorant ni- exemplar (nguya) and the o→u suffix-attachment
# raising for o-final stems.

PHASE2C_B_UM_AV_FORMS = [
    ("hawak",  "AV", "PFV",  "humawak"),
    ("hawak",  "AV", "IPFV", "humahawak"),
    ("hawak",  "AV", "CTPL", "hahawak"),
    ("pisil",  "AV", "PFV",  "pumisil"),
    ("pisil",  "AV", "IPFV", "pumipisil"),
    ("pisil",  "AV", "CTPL", "pipisil"),
    ("tulak",  "AV", "PFV",  "tumulak"),
    ("tulak",  "AV", "IPFV", "tumutulak"),
    ("tulak",  "AV", "CTPL", "tutulak"),
    ("bunot",  "AV", "PFV",  "bumunot"),
    ("bunot",  "AV", "IPFV", "bumubunot"),
    ("bunot",  "AV", "CTPL", "bubunot"),
    ("saksak", "AV", "PFV",  "sumaksak"),
    ("saksak", "AV", "IPFV", "sumasaksak"),
    ("saksak", "AV", "CTPL", "sasaksak"),
    ("itak",   "AV", "PFV",  "umitak"),
    ("itak",   "AV", "IPFV", "umiitak"),
    ("itak",   "AV", "CTPL", "iitak"),
    ("salok",  "AV", "PFV",  "sumalok"),
    ("salok",  "AV", "IPFV", "sumasalok"),
    ("salok",  "AV", "CTPL", "sasalok"),
    ("hagis",  "AV", "PFV",  "humagis"),
    ("hagis",  "AV", "IPFV", "humahagis"),
    ("hagis",  "AV", "CTPL", "hahagis"),
    ("hatak",  "AV", "PFV",  "humatak"),
    ("hatak",  "AV", "IPFV", "humahatak"),
    ("hatak",  "AV", "CTPL", "hahatak"),
    ("tunaw",  "AV", "PFV",  "tumunaw"),
    ("tunaw",  "AV", "IPFV", "tumutunaw"),
    ("tunaw",  "AV", "CTPL", "tutunaw"),
    ("bayo",   "AV", "PFV",  "bumayo"),
    ("bayo",   "AV", "IPFV", "bumabayo"),
    ("bayo",   "AV", "CTPL", "babayo"),
    ("halo",   "AV", "PFV",  "humalo"),
    ("halo",   "AV", "IPFV", "humahalo"),
    ("halo",   "AV", "CTPL", "hahalo"),
    ("sundo",  "AV", "PFV",  "sumundo"),
    ("sundo",  "AV", "IPFV", "sumusundo"),
    ("sundo",  "AV", "CTPL", "susundo"),
    ("tiklop", "AV", "PFV",  "tumiklop"),
    ("tiklop", "AV", "IPFV", "tumitiklop"),
    ("tiklop", "AV", "CTPL", "titiklop"),
    ("sipsip", "AV", "PFV",  "sumipsip"),
    ("sipsip", "AV", "IPFV", "sumisipsip"),
    ("sipsip", "AV", "CTPL", "sisipsip"),
    ("utang",  "AV", "PFV",  "umutang"),
    ("utang",  "AV", "IPFV", "umuutang"),
    ("utang",  "AV", "CTPL", "uutang"),
    ("hiram",  "AV", "PFV",  "humiram"),
    ("hiram",  "AV", "IPFV", "humihiram"),
    ("hiram",  "AV", "CTPL", "hihiram"),
    ("tugon",  "AV", "PFV",  "tumugon"),
    ("tugon",  "AV", "IPFV", "tumutugon"),
    ("tugon",  "AV", "CTPL", "tutugon"),
    ("pasa",   "AV", "PFV",  "pumasa"),
    ("pasa",   "AV", "IPFV", "pumapasa"),
    ("pasa",   "AV", "CTPL", "papasa"),
]


PHASE2C_B_MAG_AV_FORMS = [
    ("lagay",    "AV", "PFV",  "naglagay"),
    ("lagay",    "AV", "IPFV", "naglalagay"),
    ("lagay",    "AV", "CTPL", "maglalagay"),
    ("patong",   "AV", "PFV",  "nagpatong"),
    ("patong",   "AV", "IPFV", "nagpapatong"),
    ("patong",   "AV", "CTPL", "magpapatong"),
    ("timpla",   "AV", "PFV",  "nagtimpla"),
    ("timpla",   "AV", "IPFV", "nagtitimpla"),
    ("timpla",   "AV", "CTPL", "magtitimpla"),
    ("lutas",    "AV", "PFV",  "naglutas"),
    ("lutas",    "AV", "IPFV", "naglulutas"),
    ("lutas",    "AV", "CTPL", "maglulutas"),
    ("kuskos",   "AV", "PFV",  "nagkuskos"),
    ("kuskos",   "AV", "IPFV", "nagkukuskos"),
    ("kuskos",   "AV", "CTPL", "magkukuskos"),
    ("giling",   "AV", "PFV",  "naggiling"),
    ("giling",   "AV", "IPFV", "naggigiling"),
    ("giling",   "AV", "CTPL", "maggigiling"),
    ("hubad",    "AV", "PFV",  "naghubad"),
    ("hubad",    "AV", "IPFV", "naghuhubad"),
    ("hubad",    "AV", "CTPL", "maghuhubad"),
    ("buhos",    "AV", "PFV",  "nagbuhos"),
    ("buhos",    "AV", "IPFV", "nagbubuhos"),
    ("buhos",    "AV", "CTPL", "magbubuhos"),
    ("saing",    "AV", "PFV",  "nagsaing"),
    ("saing",    "AV", "IPFV", "nagsasaing"),
    ("saing",    "AV", "CTPL", "magsasaing"),
    ("taas",     "AV", "PFV",  "nagtaas"),
    ("taas",     "AV", "IPFV", "nagtataas"),
    ("taas",     "AV", "CTPL", "magtataas"),
    ("dagdag",   "AV", "PFV",  "nagdagdag"),
    ("dagdag",   "AV", "IPFV", "nagdadagdag"),
    ("dagdag",   "AV", "CTPL", "magdadagdag"),
    ("bawas",    "AV", "PFV",  "nagbawas"),
    ("bawas",    "AV", "IPFV", "nagbabawas"),
    ("bawas",    "AV", "CTPL", "magbabawas"),
    ("balot",    "AV", "PFV",  "nagbalot"),
    ("balot",    "AV", "IPFV", "nagbabalot"),
    ("balot",    "AV", "CTPL", "magbabalot"),
    ("salita",   "AV", "PFV",  "nagsalita"),
    ("salita",   "AV", "IPFV", "nagsasalita"),
    ("salita",   "AV", "CTPL", "magsasalita"),
    ("sabi",     "AV", "PFV",  "nagsabi"),
    ("sabi",     "AV", "IPFV", "nagsasabi"),
    ("sabi",     "AV", "CTPL", "magsasabi"),
    ("tinda",    "AV", "PFV",  "nagtinda"),
    ("tinda",    "AV", "IPFV", "nagtitinda"),
    ("tinda",    "AV", "CTPL", "magtitinda"),
    ("ingat",    "AV", "PFV",  "nag-ingat"),
    ("ingat",    "AV", "IPFV", "nag-iingat"),
    ("ingat",    "AV", "CTPL", "mag-iingat"),
    ("asikaso",  "AV", "PFV",  "nag-asikaso"),
    ("asikaso",  "AV", "IPFV", "nag-aasikaso"),
    ("asikaso",  "AV", "CTPL", "mag-aasikaso"),
    ("tagal",    "AV", "PFV",  "nagtagal"),
    ("tagal",    "AV", "IPFV", "nagtatagal"),
    ("tagal",    "AV", "CTPL", "magtatagal"),
    ("pahinga",  "AV", "PFV",  "nagpahinga"),
    ("pahinga",  "AV", "IPFV", "nagpapahinga"),
    ("pahinga",  "AV", "CTPL", "magpapahinga"),
]


PHASE2C_B_MA_NVOL_FORMS = [
    # Phase 5n.A Commit 1: gutom / ginaw / hilo / bingi / bulag pruned
    # — moved to ADJ. The ma_adj surfaces (``magutom`` / ``maginaw``
    # / ``mahilo`` / ``mabingi`` / ``mabulag``) are now in
    # data/tgl/adjectives.yaml; the verbal NVOL forms are no longer
    # produced.
    ("pagod",  "AV", "PFV",  "napagod"),
    ("pagod",  "AV", "IPFV", "napapagod"),
    ("pagod",  "AV", "CTPL", "mapapagod"),
    ("uhaw",   "AV", "PFV",  "nauhaw"),
    ("uhaw",   "AV", "IPFV", "nauuhaw"),
    ("uhaw",   "AV", "CTPL", "mauuhaw"),
    ("init",   "AV", "PFV",  "nainit"),
    ("init",   "AV", "IPFV", "naiinit"),
    ("init",   "AV", "CTPL", "maiinit"),
    ("pawis",  "AV", "PFV",  "napawis"),
    ("pawis",  "AV", "IPFV", "napapawis"),
    ("pawis",  "AV", "CTPL", "mapapawis"),
    ("taka",   "AV", "PFV",  "nataka"),
    ("taka",   "AV", "IPFV", "natataka"),
    ("taka",   "AV", "CTPL", "matataka"),
]


PHASE2C_B_NON_AV_FORMS = [
    # /h/-initial: -in- infix surfaces normally (not ni-).
    ("hawak",  "OV", "PFV",  "hinawak"),
    ("hawak",  "OV", "CTPL", "hahawakin"),
    ("hagis",  "OV", "PFV",  "hinagis"),
    ("hatak",  "OV", "PFV",  "hinatak"),
    ("halo",   "OV", "CTPL", "hahaluhin"),       # o→u raising
    ("hubad",  "OV", "PFV",  "hinubad"),
    # o→u raising on suffix attachment.
    ("bunot",  "OV", "CTPL", "bubunutin"),
    ("bayo",   "OV", "CTPL", "babayuhin"),
    ("sundo",  "OV", "CTPL", "susunduhin"),
    ("tiklop", "OV", "CTPL", "titiklupin"),
    ("balot",  "OV", "CTPL", "babalutin"),
    # /a/-final: standard h-epenthesis.
    ("kuskos", "DV", "CTPL", "kukuskusan"),
    ("buhos",  "DV", "CTPL", "bubuhusan"),
    ("dagdag", "DV", "CTPL", "dadagdagan"),
    ("bawas",  "DV", "CTPL", "babawasan"),
    ("taas",   "DV", "CTPL", "tataasan"),
    # IV variants on lagay/patong.
    ("lagay",  "IV", "PFV",  "inilagay"),
    ("patong", "IV", "PFV",  "ipinatong"),
    # sabi DV: regular -an attachment over h-epenthesis.
    ("sabi",   "DV", "CTPL", "sasabihan"),
]


PHASE2C_C_AV_FORMS = [
    # -um- AV PFV/IPFV/CTPL across the Commit-3b additions.
    ("lapit",   "AV", "PFV",  "lumapit"),
    ("lapit",   "AV", "IPFV", "lumalapit"),
    ("lapit",   "AV", "CTPL", "lalapit"),
    ("tabi",    "AV", "PFV",  "tumabi"),
    ("tabi",    "AV", "IPFV", "tumatabi"),
    ("tabi",    "AV", "CTPL", "tatabi"),
    ("tabas",   "AV", "PFV",  "tumabas"),
    ("tabas",   "AV", "IPFV", "tumatabas"),
    ("tabas",   "AV", "CTPL", "tatabas"),
    ("sukat",   "AV", "PFV",  "sumukat"),
    ("sukat",   "AV", "IPFV", "sumusukat"),
    ("sukat",   "AV", "CTPL", "susukat"),
    ("unawa",   "AV", "PFV",  "umunawa"),
    ("unawa",   "AV", "IPFV", "umuunawa"),
    ("unawa",   "AV", "CTPL", "uunawa"),
    ("awit",    "AV", "PFV",  "umawit"),
    ("awit",    "AV", "IPFV", "umaawit"),
    ("awit",    "AV", "CTPL", "aawit"),
    ("dakot",   "AV", "PFV",  "dumakot"),
    ("dakot",   "AV", "IPFV", "dumadakot"),
    ("dakot",   "AV", "CTPL", "dadakot"),
    ("pukpok",  "AV", "PFV",  "pumukpok"),
    ("pukpok",  "AV", "IPFV", "pumupukpok"),
    ("pukpok",  "AV", "CTPL", "pupukpok"),
    ("tuloy",   "AV", "PFV",  "tumuloy"),
    ("tuloy",   "AV", "IPFV", "tumutuloy"),
    ("tuloy",   "AV", "CTPL", "tutuloy"),
    ("silip",   "AV", "PFV",  "sumilip"),
    ("silip",   "AV", "IPFV", "sumisilip"),
    ("silip",   "AV", "CTPL", "sisilip"),
    ("saksi",   "AV", "PFV",  "sumaksi"),
    ("saksi",   "AV", "IPFV", "sumasaksi"),
    ("saksi",   "AV", "CTPL", "sasaksi"),
    ("urong",   "AV", "PFV",  "umurong"),
    ("urong",   "AV", "IPFV", "umuurong"),
    ("urong",   "AV", "CTPL", "uurong"),
    ("usad",    "AV", "PFV",  "umusad"),
    ("usad",    "AV", "IPFV", "umuusad"),
    ("usad",    "AV", "CTPL", "uusad"),
    ("dukit",   "AV", "PFV",  "dumukit"),
    ("dukit",   "AV", "IPFV", "dumudukit"),
    ("dukit",   "AV", "CTPL", "dudukit"),
    # mag- AV
    ("ihaw",    "AV", "PFV",  "nag-ihaw"),
    ("ihaw",    "AV", "IPFV", "nag-iihaw"),
    ("ihaw",    "AV", "CTPL", "mag-iihaw"),
    ("dasal",   "AV", "PFV",  "nagdasal"),
    ("dasal",   "AV", "IPFV", "nagdadasal"),
    ("dasal",   "AV", "CTPL", "magdadasal"),
    ("tiis",    "AV", "PFV",  "nagtiis"),
    ("tiis",    "AV", "IPFV", "nagtitiis"),
    ("tiis",    "AV", "CTPL", "magtitiis"),
    ("dali",    "AV", "PFV",  "nagdali"),
    ("dali",    "AV", "IPFV", "nagdadali"),
    ("dali",    "AV", "CTPL", "magdadali"),
    ("labag",   "AV", "PFV",  "naglabag"),
    ("labag",   "AV", "IPFV", "naglalabag"),
    ("labag",   "AV", "CTPL", "maglalabag"),
    ("lihim",   "AV", "PFV",  "naglihim"),
    ("lihim",   "AV", "IPFV", "naglilihim"),
    ("lihim",   "AV", "CTPL", "maglilihim"),
    ("paypay",  "AV", "PFV",  "nagpaypay"),
    ("paypay",  "AV", "IPFV", "nagpapaypay"),
    ("paypay",  "AV", "CTPL", "magpapaypay"),
    # ma- non-volitional state predicates.
    ("galing",  "AV", "PFV",  "nagaling"),
    ("galing",  "AV", "IPFV", "nagagaling"),
    ("galing",  "AV", "CTPL", "magagaling"),
    ("tuto",    "AV", "PFV",  "natuto"),
    ("tuto",    "AV", "IPFV", "natututo"),
    ("tuto",    "AV", "CTPL", "matututo"),
    # Phase 5n.A Commit 1: yaman / lakas / bilis / ganda slimmed to
    # affix_class: [um] (inchoative ``yumaman`` / ``lumakas`` /
    # ``bumilis`` / ``gumanda`` retained); the ma-NVOL forms
    # (``nayaman`` / ``nalakas`` / ``nabilis`` / ``naganda``) are no
    # longer produced — the ma-adjective surfaces (``mayaman`` /
    # ``malakas`` / ``mabilis`` / ``maganda``) ride the ma_adj cell
    # in adjectives.yaml. Also pruned: tigang / tibay (full removal,
    # moved to adjectives.yaml).
    ("bigat",   "AV", "PFV",  "nabigat"),
    ("bigat",   "AV", "IPFV", "nabibigat"),
    ("bigat",   "AV", "CTPL", "mabibigat"),
    ("dunong",  "AV", "PFV",  "nadunong"),
    ("dunong",  "AV", "IPFV", "nadudunong"),
    ("dunong",  "AV", "CTPL", "madudunong"),
    ("sigla",   "AV", "PFV",  "nasigla"),
    ("sigla",   "AV", "IPFV", "nasisigla"),
    ("sigla",   "AV", "CTPL", "masisigla"),
    ("dami",    "AV", "PFV",  "nadami"),
    ("dami",    "AV", "IPFV", "nadadami"),
    ("dami",    "AV", "CTPL", "madadami"),
    ("tamis",   "AV", "PFV",  "natamis"),
    ("tamis",   "AV", "IPFV", "natatamis"),
    ("tamis",   "AV", "CTPL", "matatamis"),
    # Inchoative -um- forms for the slimmed inchoative-attested roots:
    ("ganda",   "AV", "PFV",  "gumanda"),
    ("ganda",   "AV", "IPFV", "gumaganda"),
    ("ganda",   "AV", "CTPL", "gaganda"),
    ("bilis",   "AV", "PFV",  "bumilis"),
    ("bilis",   "AV", "IPFV", "bumibilis"),
    ("bilis",   "AV", "CTPL", "bibilis"),
    ("lakas",   "AV", "PFV",  "lumakas"),
    ("lakas",   "AV", "IPFV", "lumalakas"),
    ("lakas",   "AV", "CTPL", "lalakas"),
    ("yaman",   "AV", "PFV",  "yumaman"),
    ("yaman",   "AV", "IPFV", "yumayaman"),
    ("yaman",   "AV", "CTPL", "yayaman"),
]


PHASE2C_C_NON_AV_FORMS = [
    # OV cells from the new transitives — including o→u raising and
    # the lihim sonorant ni- variant.
    ("tabas",   "OV", "PFV",  "tinabas"),
    ("tabas",   "OV", "CTPL", "tatabasin"),
    ("sukat",   "OV", "PFV",  "sinukat"),
    ("sukat",   "OV", "CTPL", "susukatin"),
    ("dakot",   "OV", "CTPL", "dadakutin"),         # o→u raising
    ("pukpok",  "OV", "CTPL", "pupukpukin"),        # o→u raising
    ("dukit",   "OV", "PFV",  "dinukit"),
    ("ihaw",    "OV", "PFV",  "inihaw"),
    ("lihim",   "OV", "PFV",  "nilihim"),           # sonorant ni-
    ("lihim",   "OV", "IPFV", "nililihim"),         # sonorant ni- + redup
    ("paypay",  "OV", "PFV",  "pinaypay"),
    ("saksi",   "OV", "CTPL", "sasaksihin"),        # h-epenthesis on /i/-final
]


PHASE2C_NON_AV_FORMS = [
    ("abot",    "OV", "PFV",  "inabot"),
    ("abot",    "OV", "CTPL", "aabutin"),     # o→u raising
    ("buhat",   "OV", "PFV",  "binuhat"),
    ("buhat",   "IV", "PFV",  "ibinuhat"),
    ("kagat",   "OV", "PFV",  "kinagat"),
    ("kagat",   "OV", "CTPL", "kakagatin"),
    ("pukol",   "OV", "PFV",  "pinukol"),
    ("pukol",   "OV", "CTPL", "pupukulin"),    # o→u raising
    ("hampas",  "OV", "PFV",  "hinampas"),     # /h/ takes -in- infix
    ("higit",   "OV", "PFV",  "hinigit"),
    ("aral",    "OV", "PFV",  "inaral"),
    ("aral",    "OV", "CTPL", "aaralin"),
    ("handa",   "OV", "PFV",  "hinanda"),
    ("handa",   "DV", "CTPL", "hahandahan"),
    ("isip",    "OV", "PFV",  "inisip"),
    ("isip",    "OV", "CTPL", "iisipin"),
    ("nguya",   "OV", "PFV",  "ninguya"),       # sonorant ni- (ng)
    ("nguya",   "OV", "IPFV", "ningunguya"),    # ng-digraph in CV-redup + ni-
    ("dukot",   "OV", "PFV",  "dinukot"),
    ("kita",    "OV", "PFV",  "kinita"),
    ("kabit",   "DV", "CTPL", "kakabitan"),
]


# === Test parametrization ================================================

ALL_PAIRED_FORMS = (
    UM_PARADIGM_FORMS
    + MAG_PARADIGM_FORMS
    + UM_MAG_PARADIGM_FORMS
    + MANG_PARADIGM_FORMS
    + MAKA_PARADIGM_FORMS
    + INTR_PARADIGM_FORMS
    + MA_NVOL_PARADIGM_FORMS
    + SONORANT_NI_PARADIGM_FORMS
    + D_TO_R_PARADIGM_FORMS
    + PHASE2C_UM_AV_FORMS
    + PHASE2C_MAG_AV_FORMS
    + PHASE2C_MA_NVOL_FORMS
    + PHASE2C_MANG_AV_FORMS
    + PHASE2C_NON_AV_FORMS
    + PHASE2C_B_UM_AV_FORMS
    + PHASE2C_B_MAG_AV_FORMS
    + PHASE2C_B_MA_NVOL_FORMS
    + PHASE2C_B_NON_AV_FORMS
    + PHASE2C_C_AV_FORMS
    + PHASE2C_C_NON_AV_FORMS
    + RECPFV_PARADIGM_FORMS
)


@pytest.fixture(scope="module")
def analyzer() -> Analyzer:
    return Analyzer.from_default()


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


@pytest.mark.parametrize("root,voice,aspect,surface", ALL_PAIRED_FORMS)
def test_surface_analyses_to_expected(
    root: str,
    voice: str,
    aspect: str,
    surface: str,
    analyzer: Analyzer,
) -> None:
    """The surface form analyses back to a record with the expected
    lemma, voice, and aspect — one of the n-best for this surface."""
    out = analyzer.analyze_one(_tok(surface))
    matches = [
        a for a in out
        if a.pos == "VERB"
        and a.lemma == root
        and a.feats.get("VOICE") == voice
        and a.feats.get("ASPECT") == aspect
    ]
    assert matches, (
        f"no analysis matching ({root!r}, {voice}, {aspect}) for "
        f"surface {surface!r}; analyses={out}"
    )


@pytest.mark.parametrize("root,voice,aspect,surface", ALL_PAIRED_FORMS)
def test_generation_produces_expected_surface(
    root: str,
    voice: str,
    aspect: str,
    surface: str,
) -> None:
    """The reverse direction: generate from (root, cell) and confirm
    we land on the same surface."""
    data = load_morph_data()
    root_obj = next((r for r in data.roots if r.citation == root), None)
    assert root_obj is not None, f"root {root!r} not in seed lexicon"
    candidates = [
        c for c in data.paradigm_cells
        if c.voice == voice and c.aspect == aspect
        and (not c.transitivity or c.transitivity == root_obj.transitivity)
        and (not c.affix_class or c.affix_class in root_obj.affix_class)
    ]
    assert candidates, (
        f"no paradigm cell for ({root!r}, {voice}, {aspect}) given "
        f"affix_class={root_obj.affix_class}"
    )
    surfaces = {generate_form(root_obj, c) for c in candidates}
    assert surface in surfaces, (
        f"expected {surface!r} for ({root!r}, {voice}, {aspect}); "
        f"engine generated {sorted(surfaces)}"
    )


# === Mood verification for maka- =========================================

@pytest.mark.parametrize("root,voice,aspect,_surface", MAKA_PARADIGM_FORMS)
def test_maka_forms_carry_mood_abil(
    root: str,
    voice: str,
    aspect: str,
    _surface: str,
    analyzer: Analyzer,
) -> None:
    out = analyzer.analyze_one(_tok(_surface))
    matches = [
        a for a in out
        if a.pos == "VERB"
        and a.lemma == root
        and a.feats.get("MOOD") == "ABIL"
    ]
    assert matches, (
        f"maka- form {_surface!r} did not carry MOOD=ABIL; "
        f"analyses={out}"
    )


# === Coverage statistics =================================================

def test_seed_lexicon_size() -> None:
    """Track lexicon scale; trigger if it shrinks unexpectedly.

    Phase 5n.A Commit 1 (be-X-root pruning, §18 L35) intentionally
    removed 9 pure-adjectival VERB entries (bingi / bulag / galit /
    ginaw / gulat / gutom / hilo / tibay / tigang) — they migrated
    to adjectives.yaml. The verb threshold drops from 200 to 195
    accordingly. Slimming ganda / bilis / lakas / yaman to
    ``affix_class: [um]`` does not change the entry count.
    """
    data = load_morph_data()
    verbs = [r for r in data.roots if r.pos == "VERB"]
    nouns = [r for r in data.roots if r.pos == "NOUN"]
    assert len(verbs) >= 195, f"verb count regressed: {len(verbs)}"
    assert len(nouns) >= 145, f"noun count regressed: {len(nouns)}"


def test_paired_assertion_count() -> None:
    """At least 600 paired assertions — Phase 2C complete; plan §5.4
    morphology coverage target (200 verbs / 150 nouns / 500 assertions)
    met across the three Phase 2C commits."""
    assert len(ALL_PAIRED_FORMS) >= 600
