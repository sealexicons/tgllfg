"""Phase 9.H: Loan + Spanish-time follow-on lex pass.

Spanish-time finalization audit: the existing ``alas`` family
(``alauna``, ``alasdos`` ... ``alasdose``) is already complete
at 12 entries — no additions needed there.

This sub-PR delivers two batches:

9 new Spanish-loan NOUN entries (all freq >= 2 in post-9.G OOV
TSV):

  avenida    "avenue"                  (Spanish "avenida")
  bakasyon   "vacation"                (Spanish "vacación")
  bangko     "bank"                    (Spanish "banco")
  botika     "pharmacy"                (Spanish "botica")
  braso      "arm"                     (Spanish "brazo")
  empleyado  "employee"                (Spanish "empleado")
  kalye      "street"                  (Spanish "calle")
  klase      "class; classroom"        (Spanish "clase")
  litson     "roast pig, lechon"       (Spanish "lechón")

1 orth-variant entry (separate citation pointing at the
canonical LEMMA — mirrors the 9.C.pre ``tiya``/``tiyo`` pattern):

  eskuwela  → LEMMA: eskwela  (standard / colloquial spelling pair)

The orth-variants mechanism: ``orth_variants`` on the canonical
entry is documentation-only (loaded into ``Root.orth_variants``
but not surface-indexed). For the variant surface to be
analyzable, a SEPARATE citation entry with ``feats: {LEMMA:
<canonical>}`` is required. The 9.C.pre additions already
followed this pattern (``tiya``/``tiyo`` / ``pinoy``/``pinay``);
``eskuwela`` was listed in ``orth_variants`` but not added as
a separate citation — fixed here.

Note: a similar gap existed for ``bias`` (listed as
``orth_variants: [bias]`` on the canonical ``blas`` in 9.C.pre),
but user-verified against the R&C 1990 page-160 scan
(``data/tgl/references/scans/blas.png``) that ``Bias`` is a
confirmed OCR artifact, not a real spelling variant. The fix
landed at-source (hand-correction of
``data/tgl/references/901132785-Modern-Tagalog.txt``); the
``orth_variants: [bias]`` annotation was also dropped from
the ``blas`` entry.
"""

from __future__ import annotations

import pytest

NEW_LOANS = [
    "avenida", "bakasyon", "bangko", "botika", "braso",
    "empleyado", "kalye", "klase", "litson",
]
ORTH_VARIANTS = [
    ("eskuwela", "eskwela"),
]


@pytest.fixture(scope="module")
def morph_data():
    from tgllfg.morph.loader import load_morph_data
    return load_morph_data()


@pytest.fixture(scope="module")
def analyzer(morph_data):
    from tgllfg.morph.analyzer import Analyzer
    return Analyzer(morph_data)


@pytest.fixture(scope="module")
def noun_roots(morph_data):
    idx: dict[str, list] = {}
    for r in morph_data.roots:
        if r.pos == "NOUN":
            idx.setdefault(r.citation, []).append(r)
    return idx


# ---- Spanish-loan registration ------------------------------------

class TestLoanEntries:

    @pytest.mark.parametrize("cit", NEW_LOANS)
    def test_loan_registered(self, noun_roots, cit: str) -> None:
        assert cit in noun_roots, f"missing N: {cit}"
        r = noun_roots[cit][0]
        assert r.source == "audit-corpus"
        assert r.loan == "SPANISH"
        assert r.subclass == []


# ---- Orth-variant entries ----------------------------------------

class TestOrthVariants:

    @pytest.mark.parametrize("variant,canonical", ORTH_VARIANTS)
    def test_variant_has_lemma_pointer(
        self, noun_roots, variant: str, canonical: str,
    ) -> None:
        assert variant in noun_roots, f"missing variant: {variant}"
        r = noun_roots[variant][0]
        assert r.feats.get("LEMMA") == canonical, (
            f"{variant} LEMMA={r.feats.get('LEMMA')!r}, expected {canonical!r}"
        )

    @pytest.mark.parametrize("variant,canonical", ORTH_VARIANTS)
    def test_canonical_still_registered(
        self, noun_roots, variant: str, canonical: str,
    ) -> None:
        # The canonical entry should remain — variants are additive.
        assert canonical in noun_roots, f"canonical {canonical} missing"


# ---- Spanish-time completeness audit ------------------------------

class TestAlasFamilyComplete:
    """Verify the alas family covers 1..12 (one entry per hour
    plus alauna for 1). No new additions in 9.H — this is a
    completeness pin against regression."""

    ALAS_FAMILY = [
        "alauna",       # 1
        "alasdos",      # 2
        "alastres",     # 3
        "alaskuwatro",  # 4
        "alassingko",   # 5
        "alassais",     # 6
        "alassiyete",   # 7
        "alasotso",     # 8
        "alasnuwebe",   # 9
        "alasdies",     # 10
        "alasonse",     # 11
        "alasdose",     # 12
    ]

    @pytest.mark.parametrize("cit", ALAS_FAMILY)
    def test_alas_form_present(self, noun_roots, cit: str) -> None:
        assert cit in noun_roots, f"missing alas-family entry: {cit}"


# ---- Surface unblocking ------------------------------------------

class TestSurfaceUnblocking:

    @pytest.mark.parametrize("surface", NEW_LOANS + ["eskuwela"])
    def test_surface_analyzable(self, analyzer, surface: str) -> None:
        assert analyzer.is_known_surface(surface), (
            f"9.H expected unblock failed: {surface!r}"
        )


# ---- Audit-corpus parse smoke ------------------------------------

class TestAuditCorpusSmoke:

    @pytest.mark.parametrize("sentence", [
        # litson — audit context "Gusto ng bisita ang litson."
        # ; smoke version uses ang-pivot since `gusto` predicate
        # has pre-existing coverage issues.
        "Mabuti ang litson.",
        # klase — audit "May mga batang palabasang-palabasa sa klase."
        "Mabuti ang klase.",
        # kalye — audit "naglalaro sa tubig na umaapaw sa kalye."
        "Maganda ang kalye.",
        # bakasyon — audit "Ito ang mga buwan ng bakasyon."
        "Maganda ang bakasyon.",
        # botika — audit "Inihulog ni Roberta ang sulat sa botika..."
        "Pumunta siya sa botika.",
        # bangko — audit "manghiram ng pera sa bangko."
        "Pumunta siya sa bangko.",
        # braso — audit "Ilan ang braso niya?"
        "Mabigat ang braso.",
        # empleyado — audit "Nahuli ang empleyado sa trabaho."
        "Dumating ang empleyado.",
        # eskuwela — audit "(Pupunta ako) sa eskuwela."
        "Pumunta siya sa eskuwela.",
    ])
    def test_parse(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"no parse: {sentence!r}"


# ---- No-regression sanity ----------------------------------------

class TestNoRegression:

    @pytest.mark.parametrize("sentence", [
        "Pumunta siya sa eskwela.",   # canonical eskwela still works
        "Dumating si Blas.",           # canonical blas still works
        "Mabuti ang bisita.",          # existing 9.D Spanish loan
    ])
    def test_existing_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"regression: {sentence!r}"
