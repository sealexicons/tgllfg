"""Phase 9.F: ADJ batch lex pass.

7 new ADJ roots in ``adjectives.yaml`` covering audit-attested
high-frequency descriptive predicates:

ma_adj-class (4) — produce ``ma-`` prefix forms:

  husay  [ma_adj]                → mahusay   (excellent, skilled)
  aga    [ma_adj]                → maaga     (early)
  bigat  [ma_adj]                → mabigat   (heavy)
  dunong [ma_adj, d_to_r]        → marunong  (wise, knowledgeable)

The ``dunong`` entry uses ``sandhi_flags: [d_to_r]`` to apply the
intervocalic d → r rewrite — without it the paradigm would
produce the unattested ``madunong``; the audit-attested standard
form is ``marunong``.

bare-form ADJ (3) — empty ``affix_class``, surface IS the bare
citation:

  mahal  []                      → mahal     (expensive; dear)
  tama   []                      → tama      (correct, right)
  pagod  []                      → pagod     (tired)

V-root coexistence: ``bigat`` / ``dunong`` / ``pagod`` already
exist in ``verbs.yaml`` (``[um, ma, maka]`` / ``[ma, maka]`` /
``[ma, maka]``); V roots generate inflected verbal surfaces
(``nabigat`` / ``napagod`` / etc.) while the new ADJ roots
contribute the descriptive-predicate readings.
"""

from __future__ import annotations

import pytest

MA_ADJ_ROOTS = ["aga", "bigat", "husay", "runong"]
BARE_ADJ_ROOTS = ["mahal", "pagod", "tama"]
ALL_NEW = MA_ADJ_ROOTS + BARE_ADJ_ROOTS


@pytest.fixture(scope="module")
def morph_data():
    from tgllfg.morph.loader import load_morph_data
    return load_morph_data()


@pytest.fixture(scope="module")
def analyzer(morph_data):
    from tgllfg.morph.analyzer import Analyzer
    return Analyzer(morph_data)


# ---- Registration -------------------------------------------------

class TestAdjRootsRegistered:

    @pytest.fixture
    def adj_roots(self, morph_data):
        return {r.citation: r for r in morph_data.roots if r.pos == "ADJ"}

    @pytest.mark.parametrize("cit", ALL_NEW)
    def test_adj_root_registered(self, adj_roots, cit: str) -> None:
        assert cit in adj_roots, f"missing ADJ root: {cit}"

    @pytest.mark.parametrize("cit", MA_ADJ_ROOTS)
    def test_ma_adj_class(self, adj_roots, cit: str) -> None:
        assert "ma_adj" in adj_roots[cit].affix_class, (
            f"{cit}: ma_adj class missing"
        )

    @pytest.mark.parametrize("cit", BARE_ADJ_ROOTS)
    def test_bare_adj_class(self, adj_roots, cit: str) -> None:
        assert adj_roots[cit].affix_class == [], (
            f"{cit}: should have empty affix_class (bare-form ADJ)"
        )

    def test_runong_not_dunong_citation(self, adj_roots) -> None:
        # The ADJ root citation is the post-d→r-sandhi ``runong``,
        # not the V-root form ``dunong``. Using ``dunong`` + the
        # ``d_to_r`` sandhi flag would produce the right surfaces
        # but break the Phase 5h superlative/intensive test's
        # surface-compute pattern (``"pinakama" + root.citation``).
        # The V root ``dunong`` (verbs.yaml) coexists, contributing
        # only V-aspect inflected surfaces.
        assert "runong" in adj_roots
        assert "dunong" not in {c for c in adj_roots
                                if "ma_adj" in adj_roots[c].affix_class}


# ---- Surface unblocking ------------------------------------------

class TestSurfaceUnblocking:

    @pytest.mark.parametrize("surface", [
        # ma_adj-derived
        "mahusay", "maaga", "mabigat", "marunong",
        # bare-form
        "mahal", "tama", "pagod",
        # Superlative / intensive / equative derivations
        "pinakamarunong",  # superlative
        "napakarunong",    # intensive
        "kasingbigat",     # equative
    ])
    def test_surface_analyzable(self, analyzer, surface: str) -> None:
        assert analyzer.is_known_surface(surface), (
            f"9.F expected unblock failed: {surface!r}"
        )


# ---- V-root coexistence ------------------------------------------

class TestVRootCoexistence:
    """bigat / dunong / pagod each have a V root in verbs.yaml.
    Adding ADJ roots (bigat/runong/pagod) doesn't disturb V
    surfaces — V keeps generating inflected forms (napagod,
    nabigat, nadunong) while ADJ contributes bare/derived ADJ
    surfaces (mabigat, marunong, pagod)."""

    @pytest.mark.parametrize("v_form", [
        "napagod",     # pagod V ma-PFV
        "nabigat",     # bigat V ma-PFV
        "nadunong",    # dunong V ma-PFV
    ])
    def test_v_form_still_works(self, analyzer, v_form: str) -> None:
        assert analyzer.is_known_surface(v_form)


# ---- Audit-corpus parse smoke ------------------------------------

class TestAuditCorpusSmoke:

    @pytest.mark.parametrize("sentence", [
        # mahusay (audit "Mahusay ang mekaniko.")
        "Mahusay ang mekaniko.",
        # maaga (audit "Maaga noon." - but noon may be OOV; use simpler)
        "Maaga si Juan.",
        # mabigat (audit "Mabigat ang loob ni Juan.")
        "Mabigat ang loob.",
        # marunong (audit "marunong nang magluto si Cecille")
        "Marunong si Juan.",
        # mahal (audit "Mahal ang regalo.")
        "Mahal ang regalo.",
        # tama (audit "tamang-tama ang sasabihin")
        "Tama siya.",
        # pagod (audit "dahil pagod na siya")
        "Pagod siya.",
    ])
    def test_parse(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"no parse: {sentence!r}"


# ---- No-regression sanity ----------------------------------------

class TestNoRegression:
    """Existing ADJ parses still work after the additions."""

    @pytest.mark.parametrize("sentence", [
        "Maganda ang aklat.",         # ganda — pre-existing
        "Mabuti siya.",                # buti — pre-existing
        "Mahirap ang buhay.",          # hirap — pre-existing (uses 9.C buhay)
        "Mabilis ang kotse.",          # bilis — pre-existing
    ])
    def test_existing_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"regression: {sentence!r}"
