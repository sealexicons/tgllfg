"""Phase 9.J: catch-all final OOV pass.

13 audit-attested entries closing the remaining top-30 OOV after
9.A-9.I lex-sweep block:

6 proper-name N entries (all subclass: [PERSON, MALE], all freq 4):
  alan / amado / jose / marco / mario / oscar

4 zero-conversion N entries (existing V/ADJ root coexists; bare-
form analyzability via the N-V pair pattern from 9.D):
  dating  — "arrival; newcomer"   (V root in verbs.yaml)
  ganda   — "beauty"               (ADJ root + V root)
  hirap   — "difficulty, hardship" (ADJ root)
  ibig    — "wish, desire"         (V root)

1 bare-form ADJ root:
  luma   — "old"                   (affix_class: [])
                                    Unblocks ``luma`` bare AND
                                    ``lumang`` (= luma + linker -ng)
                                    via split_linker_ng decomposition.

1 colloquial DEM-DIST contraction:
  yon    — DET, LEMMA: iyon        (audit "Mabuti naman 'yon")
"""

from __future__ import annotations

import pytest

PROPER_NAMES = ["alan", "amado", "jose", "marco", "mario", "oscar"]
N_COEXISTENCE = ["dating", "ganda", "hirap", "ibig"]


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


# ---- Proper-name N registration ----------------------------------

class TestProperNames:

    @pytest.mark.parametrize("cit", PROPER_NAMES)
    def test_proper_registered(self, noun_roots, cit: str) -> None:
        assert cit in noun_roots, f"missing proper-name: {cit}"
        r = noun_roots[cit][0]
        assert r.subclass == ["PERSON", "MALE"]
        assert r.source == "audit-corpus"


# ---- N-coexistence entries ---------------------------------------

class TestNCoexistence:

    @pytest.mark.parametrize("cit", N_COEXISTENCE)
    def test_n_registered(self, noun_roots, cit: str) -> None:
        assert cit in noun_roots
        r = noun_roots[cit][0]
        assert r.source == "audit-corpus"


# ---- luma ADJ ----------------------------------------------------

class TestLumaAdj:

    def test_luma_registered_as_bare_adj(self, morph_data) -> None:
        adj_roots = {r.citation: r for r in morph_data.roots if r.pos == "ADJ"}
        assert "luma" in adj_roots
        r = adj_roots["luma"]
        assert r.affix_class == []  # bare-form ADJ
        assert r.gloss == "old"


# ---- yon DET -----------------------------------------------------

class TestYonDem:

    def test_yon_registered_as_dem_dist(self, morph_data) -> None:
        particles = {p.surface: p for p in morph_data.particles}
        assert "yon" in particles
        p = particles["yon"]
        assert p.pos == "DET"
        assert p.feats.get("CASE") == "NOM"
        assert p.feats.get("DEIXIS") == "DIST"
        assert p.feats.get("DEM") is True
        assert p.feats.get("LEMMA") == "iyon"


# ---- Surface unblocking ------------------------------------------

class TestSurfaceUnblocking:

    @pytest.mark.parametrize("surface", PROPER_NAMES + N_COEXISTENCE
                             + ["luma", "yon"])
    def test_surface_analyzable(self, analyzer, surface: str) -> None:
        assert analyzer.is_known_surface(surface), (
            f"9.J expected unblock failed: {surface!r}"
        )


# ---- Audit-corpus parse smoke ------------------------------------

class TestAuditCorpusSmoke:
    """Audit sentences confirmed parseable post-9.J. Other audit
    sentences (Sinipa ni Marco / Nag-uusap si Jose / Ang ganda ng
    isno / Ang ibig sabihin) still fail due to pre-existing
    grammar gaps (TR-without-OBJ, emphatic ADJ-fronting, sabihin
    OV-INF) deferred to 9.O."""

    @pytest.mark.parametrize("sentence", [
        # Oscar proper-name closure (audit "Hinahanap mo ba si Oscar...")
        "Hinahanap mo ba si Oscar?",
        # dating N-coexistence (audit "Ikaw ba ang bagong dating?")
        "Ang bagong dating ay maganda.",
        # hirap N-coexistence (audit "malaking hirap")
        "Malaki ang hirap.",
        # luma + linker (audit "lumang diyaryo")
        "Lumang aklat ito.",
        # yon DEM (audit context; tested without 2P-clitic naman
        # — naman+DEM-bare composition is a pre-existing grammar
        # gap that also blocks canonical "Mabuti naman iyon.")
        "Maganda yon.",
        # Sanity: proper-name still works for the other 5
        "Dumating si Mario.",
        "Dumating si Amado.",
    ])
    def test_parse(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"no parse: {sentence!r}"


# ---- No-regression ----------------------------------------------

class TestNoRegression:
    """Pre-existing parses for related forms still work."""

    @pytest.mark.parametrize("sentence", [
        # maganda still parses (ma_adj derivation; bare ganda N is a
        # 9.J addition that coexists)
        "Maganda ang aklat.",
        # mahirap still parses (ma_adj on hirap ADJ root)
        "Mahirap ang buhay.",
        # iyon (canonical) still parses
        "Maganda iyon.",
        # 9.B Maria still works
        "Dumating si Maria.",
        # 9.E V-root still works (kilala -> kinilala inflected)
        "Kinilala niya ako.",
    ])
    def test_existing_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"regression: {sentence!r}"
