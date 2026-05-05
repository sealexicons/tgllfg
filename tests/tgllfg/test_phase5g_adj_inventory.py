"""Phase 5g Commit 4: lex inventory expansion (~30 adjectives).

Roadmap §12.1 calls for a ~30–50 high-frequency adjective inventory
covering size / shape / colour / evaluative / sensory / quality
dimensions. Phase 5g Commit 1 seeded 6 entries (``ganda``,
``talino``, ``tanda``, ``liit``, ``taas``, ``bilis``); Commit 4
expands to 30 by adding 24 entries.

Adjective dimensions covered (Phase 5g — colour deferred because
common Tagalog colour terms ``puti`` / ``itim`` / ``pula`` /
``dilaw`` etc. are bare adjectives that don't take ``ma-``;
they need a separate paradigm or a non-paradigmatic ADJ-class
treatment, which lands in Phase 5h or a dedicated commit):

* **Size**: ``laki``, ``liit``, ``taas``, ``baba``, ``haba``,
  ``ikli``, ``lapad``, ``kapal``, ``nipis``  (9)
* **Quality**: ``ganda``, ``talino``, ``tanda``, ``bilis``,
  ``bait``, ``sipag``, ``tamad``, ``tapang``, ``lakas``,
  ``hina``, ``linis``  (11)
* **Sensory**: ``init``, ``lamig``, ``sarap``, ``ingay``,
  ``bango``, ``baho``  (6)
* **Evaluative**: ``saya``, ``lungkot``, ``yaman``, ``hirap``  (4)

Eight roots also exist in ``verbs.yaml`` as INTR "be X" stative
verbs or as TR/INTR verbs with a distinct sense (``baba`` "go
down, descend", ``linis`` "clean (TR)"). The Phase 5g additive
policy leaves verbs.yaml untouched; the ADJ entries produce the
``ma + root`` surface that the verbal paradigm doesn't generate.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import FStructure, Token
from tgllfg.morph import Analyzer, load_morph_data
from tgllfg.core.pipeline import parse_text


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === Per-dimension inventory tables =====================================

SIZE = [
    ("laki",  "malaki",  "big, large"),
    ("liit",  "maliit",  "small"),
    ("taas",  "mataas",  "high, tall"),
    ("baba",  "mababa",  "low"),
    ("haba",  "mahaba",  "long"),
    ("ikli",  "maikli",  "short (in length)"),
    ("lapad", "malapad", "wide, broad"),
    ("kapal", "makapal", "thick"),
    ("nipis", "manipis", "thin"),
]

QUALITY = [
    ("ganda",  "maganda",  "beautiful"),
    ("talino", "matalino", "intelligent"),
    ("tanda",  "matanda",  "old"),
    ("bilis",  "mabilis",  "quick, fast"),
    ("bait",   "mabait",   "kind, well-behaved"),
    ("sipag",  "masipag",  "diligent, industrious"),
    ("tamad",  "matamad",  "lazy"),
    ("tapang", "matapang", "brave"),
    ("lakas",  "malakas",  "strong"),
    ("hina",   "mahina",   "weak"),
    ("linis",  "malinis",  "clean"),
]

SENSORY = [
    ("init",  "mainit",  "hot"),
    ("lamig", "malamig", "cold"),
    ("sarap", "masarap", "delicious, tasty"),
    ("ingay", "maingay", "noisy"),
    ("bango", "mabango", "fragrant"),
    ("baho",  "mabaho",  "smelly, foul"),
]

EVALUATIVE = [
    ("saya",    "masaya",    "happy, joyful"),
    ("lungkot", "malungkot", "sad"),
    ("yaman",   "mayaman",   "wealthy, rich"),
    ("hirap",   "mahirap",   "poor, difficult"),
]

ALL_INVENTORY = SIZE + QUALITY + SENSORY + EVALUATIVE


# === Per-dimension surface coverage =====================================


class TestSizeDimension:
    @pytest.mark.parametrize("root,surface,_gloss", SIZE)
    def test_surface_analyzes_as_adj(
        self, root: str, surface: str, _gloss: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        adj = [a for a in out if a.pos == "ADJ"]
        assert len(adj) == 1
        assert adj[0].lemma == root
        assert adj[0].feats.get("PREDICATIVE") == "YES"
        assert adj[0].feats.get("LEMMA") == root


class TestQualityDimension:
    @pytest.mark.parametrize("root,surface,_gloss", QUALITY)
    def test_surface_analyzes_as_adj(
        self, root: str, surface: str, _gloss: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        adj = [a for a in out if a.pos == "ADJ"]
        assert len(adj) == 1
        assert adj[0].lemma == root


class TestSensoryDimension:
    @pytest.mark.parametrize("root,surface,_gloss", SENSORY)
    def test_surface_analyzes_as_adj(
        self, root: str, surface: str, _gloss: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        adj = [a for a in out if a.pos == "ADJ"]
        assert len(adj) == 1
        assert adj[0].lemma == root


class TestEvaluativeDimension:
    @pytest.mark.parametrize("root,surface,_gloss", EVALUATIVE)
    def test_surface_analyzes_as_adj(
        self, root: str, surface: str, _gloss: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        adj = [a for a in out if a.pos == "ADJ"]
        assert len(adj) == 1
        assert adj[0].lemma == root


# === Inventory totals ====================================================


class TestInventoryTotals:
    """Sanity checks on the full lexicon shape after Commit 4."""

    def test_thirty_adj_roots(self) -> None:
        data = load_morph_data()
        adj_roots = [r for r in data.roots if r.pos == "ADJ"]
        assert len(adj_roots) == 30, (
            f"expected 30 ADJ roots in adjectives.yaml; got {len(adj_roots)}"
        )

    def test_all_inventory_lemmas_present(self) -> None:
        data = load_morph_data()
        adj_lemmas = {r.citation for r in data.roots if r.pos == "ADJ"}
        expected = {entry[0] for entry in ALL_INVENTORY}
        missing = expected - adj_lemmas
        extra = adj_lemmas - expected
        assert not missing, f"missing ADJ lemmas: {sorted(missing)}"
        assert not extra, f"unexpected ADJ lemmas: {sorted(extra)}"


# === Multi-POS coexistence (Phase 5g additive policy) ====================
#
# Eight roots in the inventory also have VERB entries in verbs.yaml.
# Phase 5g doesn't touch verbs.yaml; both analyses coexist.


COEXIST_ROOTS = [
    # (root, adj_surface, an existing verbal_surface that shouldn't disappear)
    ("ganda",   "maganda",  "gumanda"),     # AV PFV inchoative
    ("bilis",   "mabilis",  "bumilis"),     # AV PFV inchoative
    ("lakas",   "malakas",  "lumakas"),     # AV PFV inchoative
    ("yaman",   "mayaman",  "yumaman"),     # AV PFV inchoative
    ("ingay",   "maingay",  "ingay"),       # bare not generated; check verbal forms exist
]


class TestVerbalCoexistence:
    """For roots shared between adjectives.yaml and verbs.yaml,
    both POS analyses are produced. The ADJ surface is the
    productive ``ma + root``; the verbal surfaces are the ``um-`` /
    ``mag-`` / ``ma-`` paradigm forms (typically ``gumanda``,
    ``naganda``, ``magaganda`` etc.). The two surface families
    don't collide because the bare ``ma + root`` form is not
    produced by the verbal paradigm — verbal NVOL ``ma`` cells
    always reduplicate or use ``na-`` prefix (PFV NVOL: naganda;
    IPFV NVOL: nagaganda; CTPL NVOL: magaganda)."""

    @pytest.mark.parametrize("root,adj_surface,verb_surface", COEXIST_ROOTS[:4])
    def test_inchoative_um_form_still_parses(
        self, root: str, adj_surface: str, verb_surface: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(verb_surface))
        verbs = [a for a in out if a.pos == "VERB"]
        assert any(a.lemma == root for a in verbs), (
            f"verbal surface {verb_surface!r} for root {root!r} "
            f"should still produce a VERB analysis after Phase 5g"
        )

    @pytest.mark.parametrize("root,adj_surface,_verb_surface", COEXIST_ROOTS)
    def test_adj_surface_only_adj(
        self, root: str, adj_surface: str, _verb_surface: str
    ) -> None:
        # The bare ``ma + root`` surface is ADJ-only — no verbal
        # paradigm cell produces this form.
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(adj_surface))
        verbs = [a for a in out if a.pos == "VERB"]
        adj = [a for a in out if a.pos == "ADJ"]
        assert verbs == [], (
            f"adj surface {adj_surface!r} should produce no VERB "
            f"analysis; got {[(a.pos, a.lemma) for a in out]}"
        )
        assert len(adj) == 1


# === Integration: full-sentence parse for one adj per dimension ==========


class TestSentenceIntegration:
    """Sample one adjective per dimension and verify a complete
    predicative-adj sentence parse using the Phase 5g Commit 3
    rule. This pins the inventory expansion to the existing
    grammar-rule layer."""

    @pytest.mark.parametrize("text,expected_lemma", [
        # SIZE
        ("Malaki ang bahay.",   "laki"),
        ("Mababa ang bundok.",  "baba"),
        # QUALITY
        ("Mabait ang bata.",    "bait"),
        ("Masipag ang nanay.",  "sipag"),
        ("Matapang ang lalaki.", "tapang"),
        ("Malinis ang aklat.",  "linis"),
        # SENSORY
        ("Mainit ang kape.",    "init"),
        ("Malamig ang tubig.",  "lamig"),
        ("Masarap ang isda.",   "sarap"),
        # EVALUATIVE
        ("Masaya ang bata.",    "saya"),
        ("Mahirap ang trabaho.", "hirap"),
    ])
    def test_parses_with_correct_adj_lemma(
        self, text: str, expected_lemma: str
    ) -> None:
        parses = parse_text(text, n_best=1)
        assert parses, f"no parse for {text!r}"
        f = parses[0][1]
        assert f.feats.get("PRED") == "ADJ <SUBJ>"
        assert f.feats.get("ADJ_LEMMA") == expected_lemma
        assert f.feats.get("PREDICATIVE") == "YES"
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("CASE") == "NOM"
