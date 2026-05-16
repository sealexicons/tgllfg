"""Phase 9.G: particles + discourse-markers lex pass.

12 audit-attested entries in ``particles.yaml`` + 1 NOUN
(``halip``) in ``nouns.yaml``:

Discourse interjections (INTERJ=true, extends Phase 8.D2):
  aba    — interjection "ah!, oh!"
  ha     — sentence-final tag / discourse particle
  heto   — deictic "here it is" (alternate of `eto`)

Locative existential:
  narito  — LOC_EXISTENTIAL / DEIXIS=PROX ("is here")

D→R-sandhi DAT/DEM variants (LEMMA pointers):
  rito   → dito  (DAT/PROX, post-d→r-sandhi spelling)
  roon   → doon  (DAT/DIST)

Temporal adverbs (extends kahapon/ngayon/bukas/mamaya):
  noon    — ADV_TYPE=TIME / DEIXIS_TIME=PAST
  kagabi  — ADV_TYPE=TIME / DEIXIS_TIME=PAST

Manner DEM variant:
  ganoon  — orthographic variant of existing `ganon`

Discourse markers:
  muna   — 2P clitic, ADV=FIRST ("for now / yet")
  sige   — sentence-initial DISCOURSE=GO_AHEAD
  tuloy  — sentence-medial DISCOURSE=SO

NOUN addition:
  halip  — "alternative, substitute" (used in `sa halip na X`)
"""

from __future__ import annotations

import pytest

PARTICLE_SURFACES = [
    "aba", "ha", "heto",
    "narito",
    "rito", "roon",
    "noon", "kagabi",
    "ganoon",
    "muna", "sige", "tuloy",
]


@pytest.fixture(scope="module")
def morph_data():
    from tgllfg.morph.loader import load_morph_data
    return load_morph_data()


@pytest.fixture(scope="module")
def analyzer(morph_data):
    from tgllfg.morph.analyzer import Analyzer
    return Analyzer(morph_data)


# ---- Registration -------------------------------------------------

class TestParticleRegistration:

    @pytest.fixture
    def particles(self, morph_data):
        return {p.surface: p for p in morph_data.particles}

    @pytest.mark.parametrize("surface", PARTICLE_SURFACES)
    def test_particle_registered(self, particles, surface: str) -> None:
        assert surface in particles, f"missing particle: {surface}"

    def test_muna_is_2p_clitic(self, particles) -> None:
        p = particles["muna"]
        assert p.is_clitic
        assert p.clitic_class == "2P"

    def test_sige_is_sentence_initial(self, particles) -> None:
        p = particles["sige"]
        assert p.feats.get("DISCOURSE_POS") == "SENTENCE_INITIAL"

    def test_rito_lemma_points_at_dito(self, particles) -> None:
        # post-d→r-sandhi variant pointer
        assert particles["rito"].feats.get("LEMMA") == "dito"

    def test_roon_lemma_points_at_doon(self, particles) -> None:
        assert particles["roon"].feats.get("LEMMA") == "doon"

    def test_ganoon_lemma_points_at_ganon(self, particles) -> None:
        # orthographic variant
        assert particles["ganoon"].feats.get("LEMMA") == "ganon"

    def test_narito_loc_existential(self, particles) -> None:
        p = particles["narito"]
        assert p.feats.get("LOC_EXISTENTIAL") is True
        assert p.feats.get("DEIXIS") == "PROX"

    def test_aba_ha_heto_are_interj(self, particles) -> None:
        for surf in ("aba", "ha", "heto"):
            assert particles[surf].feats.get("INTERJ") is True

    def test_noon_kagabi_are_past_time(self, particles) -> None:
        for surf in ("noon", "kagabi"):
            p = particles[surf]
            assert p.feats.get("ADV_TYPE") == "TIME"
            assert p.feats.get("DEIXIS_TIME") == "PAST"


# ---- N root (halip) ----------------------------------------------

class TestHalipNoun:

    @pytest.fixture
    def noun_roots(self, morph_data):
        idx: dict[str, list] = {}
        for r in morph_data.roots:
            if r.pos == "NOUN":
                idx.setdefault(r.citation, []).append(r)
        return idx

    def test_halip_registered(self, noun_roots) -> None:
        assert "halip" in noun_roots
        r = noun_roots["halip"][0]
        assert r.source == "audit-corpus"


# ---- Surface unblocking ------------------------------------------

class TestSurfaceUnblocking:

    @pytest.mark.parametrize("surface", PARTICLE_SURFACES + ["halip"])
    def test_surface_analyzable(self, analyzer, surface: str) -> None:
        assert analyzer.is_known_surface(surface), (
            f"9.G expected unblock failed: {surface!r}"
        )


# ---- Audit-corpus parse smoke ------------------------------------

class TestAuditCorpusSmoke:
    """Audit-context smoke parses for particles where grammar
    coverage is already in place. Other particles (``narito`` /
    ``noon`` / ``kagabi`` / ``sige`` / ``heto`` as predicate /
    sentence-medial ADV) are lex-added but require construction-
    class rules to form clauses — deferred to 9.O / construction
    sub-PRs. See module docstring."""

    @pytest.mark.parametrize("sentence", [
        # rito (post-sandhi DAT/PROX) — DEM-pos rule already covers
        "Pumunta sila rito.",
        # roon (post-sandhi DAT/DIST)
        "Pumunta sila roon.",
        # muna (2P clitic, ADV=FIRST) — 2P clitic rule covers
        "Sumulat muna siya.",
        "Bumili muna siya ng aklat.",
        # aba (sentence-initial INTERJ — Phase 8.D2 rule covers)
        "Aba, kumain ako.",
        # ha (sentence-internal INTERJ — used in audit predicative)
        # — note: only the INTERJ feat is asserted; positional
        # consumption depends on construction-class work.
    ])
    def test_parse(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"no parse: {sentence!r}"


# ---- No-regression sanity ----------------------------------------

class TestNoRegression:
    """Existing particle and DEM parses still work."""

    @pytest.mark.parametrize("sentence", [
        "Pumunta sila dito.",        # dito (canonical PROX) still works
        "Pumunta sila doon.",        # doon (canonical DIST) still works
        "Oo, kumain ako.",           # oo INTERJ — pre-existing Phase 8.D2
        "Sumulat na siya.",          # na 2P clitic — pre-existing
    ])
    def test_existing_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"regression: {sentence!r}"
