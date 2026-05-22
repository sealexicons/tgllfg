# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 9.E: VERB-base sweep lex pass.

5 new VERB roots, 3 affix_class extensions on existing V roots,
and 2 new NOUN roots (zero-conversion N partners for ``alok`` and
``dala``).

VERB roots added:

* ``alok``    TR  ``[um, mag, in_oblig, an_oblig, maka]`` — offer
* ``hiwa``    TR  ``[um, mag, in_oblig, an_oblig, maka]`` — slice
* ``kilala``  TR  ``[mag, in_oblig, an_oblig, maka]`` — know
* ``tanggi``  INTR ``[um, mag, maka]`` — refuse
* ``yari``    INTR ``[mang_retain, maka]`` — happen (y-initial,
                                              retain pattern)

VERB affix_class extensions:

* ``hanap``   ``[um, in_oblig, an_oblig, maka]`` → adds ``mag``
              (unblocks ``naghanap`` / ``naghahanap``)
* ``tanggap`` ``[um, in_oblig, maka]`` → adds ``mag``
              (unblocks ``nagtatanggap`` etc.)
* ``tigil``   ``[mag, i_oblig, maka]`` → adds ``um``
              (unblocks ``tumigil``)

NOUN roots added (zero-conversion partners):

* ``alok``  N — "offer, proposal" (audit "sa alok ni Viktor")
* ``dala``  N — "load, baggage" (audit "Dala-dala ni Jasmine")

The ``yari`` ``mang_retain`` choice is intentional: ``y`` is a
sonorant so the standard ``mang`` drop-pattern would yield
unattested ``nayari``; the audit-attested ``nangyari`` (PFV) is
produced by the retain pattern instead. The ``mangyari`` (IMP/INF)
form is still missing — no IMP-aspect paradigm cell — deferred
to 9.O / paradigm-cell-add work.
"""

import pytest

NEW_VERB_ROOTS = ["alok", "hiwa", "kilala", "tanggi", "yari"]
EXTENDED_VERBS = ["hanap", "tanggap", "tigil"]
NEW_NOUN_ROOTS = ["alok", "dala"]


@pytest.fixture(scope="module")
def morph_data():
    from tgllfg.morph.loader import load_morph_data
    return load_morph_data()


@pytest.fixture(scope="module")
def analyzer(morph_data):
    from tgllfg.morph.analyzer import Analyzer
    return Analyzer(morph_data)


# ---- VERB-root registration --------------------------------------

class TestNewVerbRoots:

    @pytest.fixture
    def verb_roots(self, morph_data):
        return {r.citation: r for r in morph_data.roots if r.pos == "VERB"}

    @pytest.mark.parametrize("cit", NEW_VERB_ROOTS)
    def test_verb_root_registered(self, verb_roots, cit: str) -> None:
        assert cit in verb_roots, f"missing V root: {cit}"
        assert verb_roots[cit].transitivity in ("TR", "INTR")
        assert verb_roots[cit].affix_class, f"{cit}: empty affix_class"

    def test_alok_affix_class(self, verb_roots) -> None:
        assert set(verb_roots["alok"].affix_class) == {
            "um", "mag", "in_oblig", "an_oblig", "maka"
        }

    def test_yari_uses_mang_retain(self, verb_roots) -> None:
        # ``mang_retain`` is required because ``y`` is sonorant —
        # the ``mang`` drop pattern would yield unattested
        # ``nayari``; ``mang_retain`` yields the audit-attested
        # ``nangyari`` (PFV).
        assert "mang_retain" in verb_roots["yari"].affix_class
        assert "mang" not in verb_roots["yari"].affix_class


# ---- Affix-class extensions --------------------------------------

class TestAffixClassExtensions:

    @pytest.fixture
    def verb_roots(self, morph_data):
        return {r.citation: r for r in morph_data.roots if r.pos == "VERB"}

    def test_hanap_has_mag(self, verb_roots) -> None:
        assert "mag" in verb_roots["hanap"].affix_class

    def test_tanggap_has_mag(self, verb_roots) -> None:
        assert "mag" in verb_roots["tanggap"].affix_class

    def test_tigil_has_um(self, verb_roots) -> None:
        assert "um" in verb_roots["tigil"].affix_class


# ---- NOUN coexistence roots --------------------------------------

class TestNewNounRoots:

    @pytest.fixture
    def noun_roots(self, morph_data):
        idx: dict[str, list] = {}
        for r in morph_data.roots:
            if r.pos == "NOUN":
                idx.setdefault(r.citation, []).append(r)
        return idx

    @pytest.mark.parametrize("cit", NEW_NOUN_ROOTS)
    def test_noun_root_registered(self, noun_roots, cit: str) -> None:
        assert cit in noun_roots, f"missing N root: {cit}"
        r = noun_roots[cit][0]
        assert r.source == "audit-corpus"
        assert r.subclass == []
        assert r.gloss


# ---- Surface unblocking ------------------------------------------

class TestSurfaceUnblocking:
    """Each lex change unblocks specific audit-attested surfaces."""

    @pytest.mark.parametrize("surface", [
        # alok V — um-AV-PFV/CTPL/IPFV
        "umalok", "umaalok", "aalok",
        # alok V — mag-AV-PFV/CTPL/IPFV
        "nagalok", "nagaalok", "magalok",
        # hiwa V — um-AV-PFV; in-OV-PFV
        "humiwa", "hiniwa",
        # kilala V — mag/in/an family
        "kinilala", "nakakilala", "magkikilala",
        # tanggi V — um-AV-PFV/IPFV
        "tumanggi", "tumatanggi",
        # yari V — mang_retain-AV-PFV
        "nangyari",
        # hanap V — mag (extension)
        "naghanap", "naghahanap",
        # tanggap V — mag (extension)
        "nagtanggap",
        # tigil V — um (extension)
        "tumigil", "tumitigil",
        # alok / dala N bare surfaces (citation-only)
        "alok", "dala",
    ])
    def test_surface_analyzable(self, analyzer, surface: str) -> None:
        assert analyzer.is_known_surface(surface), (
            f"9.E expected unblock failed: {surface!r}"
        )


# ---- Audit-corpus parse smoke ------------------------------------

class TestAuditCorpusSmoke:
    """Sample sentences from the audit corpus exercising the new
    V roots / extensions. Each tests an audit-attested surface plus
    a minimal sentence that should parse end-to-end."""

    @pytest.mark.parametrize("sentence", [
        # alok V and N
        "Tumanggi siya sa alok.",
        # tanggi (um-AV) — INTR, no OBJ needed
        "Tumanggi siya.",
        # tigil (um-AV) — INTR (per existing entry)
        "Tumigil siya.",
        # nangyari (yari mang_retain PFV) — INTR
        "Ano ang nangyari?",
        # hanap mag-AV extension — TR, supplies OBJ
        "Naghanap siya ng aklat.",
        # tanggap mag-AV extension — TR
        "Nagtanggap siya ng regalo.",
        # iyak (already in lex; sanity check) — INTR
        "Umiyak siya.",
        # hiwa um-AV — TR, supplies OBJ
        "Humiwa siya ng tinapay.",
        # kilala mag/in (PFV)
        "Kinilala niya ako.",
    ])
    def test_parse(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"no parse: {sentence!r}"


# ---- No-regression sanity ----------------------------------------

class TestNoRegression:
    """Pre-existing inflected surfaces still parse cleanly."""

    @pytest.mark.parametrize("sentence", [
        "Tumawag siya.",            # tawag um-AV
        "Lumakad siya.",            # lakad um-AV-PFV (INTR)
        "Nagluto siya ng gulay.",   # luto mag-AV (TR)
        "Bumili siya ng aklat.",    # bili um-AV (TR)
        "Sumulat siya.",            # 9.C N–V pair
    ])
    def test_existing_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"regression: {sentence!r}"
