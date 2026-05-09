"""Phase 5n.A Commit 1 — Be-X-root verbal-paradigm pruning (§18 L35).

Audits the post-pruning state of nine pure-adjectival roots (``bingi``
"deaf", ``bulag`` "blind", ``galit`` "angry", ``ginaw`` "cold",
``gulat`` "surprised", ``gutom`` "hungry", ``hilo`` "dizzy", ``tibay``
"durable", ``tigang`` "parched") that were previously typed as
``VERB[INTR]`` with ``affix_class: [ma, maka]`` in
``data/tgl/verbs.yaml`` — a pre-Phase-5g configuration that conflicted
with the Phase 5g §12.1 commitment that ``ma-`` adjectives are POS=ADJ
rather than stative VERB.

Phase 5n.A Commit 1 removes the verbal entries entirely and adds the
roots to ``data/tgl/adjectives.yaml`` under a new "Body / condition"
section, opting into the productive ``ma_adj`` paradigm cell. The
inchoative-attested roots ``ganda`` / ``bilis`` / ``lakas`` / ``yaman``
are slimmed in ``verbs.yaml`` to ``affix_class: [um]`` so the only
verbal reading is the inchoative; the prior ``ma-NVOL`` cells
(``naganda``, ``mayaman``, ``nalakas``, etc.) no longer fire as VERB.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import Token
from tgllfg.morph import Analyzer


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === Pruned roots — the nine moved-to-ADJ entries =========================

PRUNED_ROOTS = [
    # (root, ma_adj_surface, gloss)
    ("bingi",  "mabingi",  "deaf"),
    ("bulag",  "mabulag",  "blind"),
    ("galit",  "magalit",  "angry"),
    ("ginaw",  "maginaw",  "cold (feeling cold)"),
    ("gulat",  "magulat",  "surprised, startled"),
    ("gutom",  "magutom",  "hungry"),
    ("hilo",   "mahilo",   "dizzy"),
    ("tibay",  "matibay",  "durable, sturdy"),
    ("tigang", "matigang", "parched, dry"),
]


class TestPrunedRootsAreNowAdj:
    """The nine pure-adjectival roots produce ADJ surfaces via the
    ``ma_adj`` cell, parallel to ``ganda`` → ``maganda``."""

    @pytest.mark.parametrize("root,surface,_gloss", PRUNED_ROOTS)
    def test_ma_surface_is_adj(
        self, root: str, surface: str, _gloss: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        adj_analyses = [a for a in out if a.pos == "ADJ"]
        assert adj_analyses, (
            f"expected an ADJ analysis for {surface!r}; "
            f"got {[(a.pos, a.lemma) for a in out]}"
        )
        assert any(a.lemma == root for a in adj_analyses), (
            f"ADJ analysis for {surface!r} should have lemma {root!r}; "
            f"got {[a.lemma for a in adj_analyses]}"
        )

    @pytest.mark.parametrize("root,surface,_gloss", PRUNED_ROOTS)
    def test_ma_surface_carries_predicative(
        self, root: str, surface: str, _gloss: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        adj = next(a for a in out if a.pos == "ADJ" and a.lemma == root)
        assert adj.feats.get("PREDICATIVE") == "YES", (
            f"ADJ {surface!r} should carry PREDICATIVE=YES; feats={adj.feats}"
        )


# === Stale verbal surfaces no longer fire as VERB =========================

STALE_VERBAL_SURFACES = [
    # (surface, root) — the AV-PFV / IPFV / CTPL forms produced by the
    # old [ma, maka] paradigm; should no longer analyse as VERB after
    # Commit 1.
    ("nabingi",   "bingi"),
    ("nabibingi", "bingi"),
    ("mabibingi", "bingi"),
    ("nabulag",   "bulag"),
    ("nabubulag", "bulag"),
    ("mabubulag", "bulag"),
    ("nagalit",   "galit"),
    ("nagagalit", "galit"),
    ("magagalit", "galit"),
    ("naginaw",   "ginaw"),
    ("nagiginaw", "ginaw"),
    ("magiginaw", "ginaw"),
    ("nagulat",   "gulat"),
    ("nagugulat", "gulat"),
    ("magugulat", "gulat"),
    ("nagutom",   "gutom"),
    ("nagugutom", "gutom"),
    ("magugutom", "gutom"),
    ("nahilo",    "hilo"),
    ("nahihilo",  "hilo"),
    ("mahihilo",  "hilo"),
    ("natibay",   "tibay"),
    ("natitibay", "tibay"),
    ("matitibay", "tibay"),
    ("natigang",  "tigang"),
    ("natitigang", "tigang"),
    ("matitigang", "tigang"),
]


class TestStaleVerbalSurfacesDontFireAsVerb:
    """Surfaces from the old ``[ma, maka]`` paradigm should no longer
    produce VERB analyses for the pruned root after Commit 1."""

    @pytest.mark.parametrize("surface,root", STALE_VERBAL_SURFACES)
    def test_no_verb_analysis_with_pruned_lemma(
        self, surface: str, root: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        verb_analyses = [
            a for a in out if a.pos == "VERB" and a.lemma == root
        ]
        assert verb_analyses == [], (
            f"surface {surface!r} should no longer produce a VERB "
            f"analysis with lemma {root!r}; got "
            f"{[(a.pos, a.lemma, a.feats.get('VOICE'), a.feats.get('ASPECT')) for a in verb_analyses]}"
        )


# === Slimmed inchoative roots — ma-NVOL forms gone, -um- retained ========

SLIMMED_ROOTS = [
    # (root, um_surface_pfv, um_surface_ipfv, um_surface_ctpl,
    #  stale_ma_surface_pfv)
    ("ganda", "gumanda", "gumaganda", "gaganda", "naganda"),
    ("bilis", "bumilis", "bumibilis", "bibilis", "nabilis"),
    ("lakas", "lumakas", "lumalakas", "lalakas", "nalakas"),
    ("yaman", "yumaman", "yumayaman", "yayaman", "nayaman"),
]


class TestSlimmedInchoativeRoots:
    """``ganda`` / ``bilis`` / ``lakas`` / ``yaman`` retain the
    inchoative ``-um-`` reading (``gumanda`` etc.) but the prior
    ``ma-NVOL`` cells (``naganda`` etc.) no longer fire as VERB."""

    @pytest.mark.parametrize(
        "root,um_pfv,um_ipfv,um_ctpl,_stale_ma", SLIMMED_ROOTS
    )
    def test_inchoative_um_pfv_still_parses(
        self, root: str, um_pfv: str,
        um_ipfv: str, um_ctpl: str, _stale_ma: str,
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(um_pfv))
        verbs = [a for a in out if a.pos == "VERB" and a.lemma == root]
        assert any(
            a.feats.get("VOICE") == "AV"
            and a.feats.get("ASPECT") == "PFV"
            for a in verbs
        ), (
            f"inchoative -um- PFV {um_pfv!r} should still parse as "
            f"VERB[lemma={root}, VOICE=AV, ASPECT=PFV]; got "
            f"{[(a.lemma, a.feats.get('VOICE'), a.feats.get('ASPECT')) for a in verbs]}"
        )

    @pytest.mark.parametrize(
        "root,um_pfv,um_ipfv,um_ctpl,_stale_ma", SLIMMED_ROOTS
    )
    def test_inchoative_um_ipfv_still_parses(
        self, root: str, um_pfv: str,
        um_ipfv: str, um_ctpl: str, _stale_ma: str,
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(um_ipfv))
        verbs = [a for a in out if a.pos == "VERB" and a.lemma == root]
        assert any(
            a.feats.get("VOICE") == "AV"
            and a.feats.get("ASPECT") == "IPFV"
            for a in verbs
        )

    @pytest.mark.parametrize(
        "root,um_pfv,um_ipfv,um_ctpl,_stale_ma", SLIMMED_ROOTS
    )
    def test_inchoative_um_ctpl_still_parses(
        self, root: str, um_pfv: str,
        um_ipfv: str, um_ctpl: str, _stale_ma: str,
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(um_ctpl))
        verbs = [a for a in out if a.pos == "VERB" and a.lemma == root]
        assert any(
            a.feats.get("VOICE") == "AV"
            and a.feats.get("ASPECT") == "CTPL"
            for a in verbs
        )

    @pytest.mark.parametrize(
        "root,_um_pfv,_um_ipfv,_um_ctpl,stale_ma", SLIMMED_ROOTS
    )
    def test_stale_ma_nvol_pfv_no_longer_verb(
        self, root: str, _um_pfv: str,
        _um_ipfv: str, _um_ctpl: str, stale_ma: str,
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(stale_ma))
        verb_analyses = [
            a for a in out if a.pos == "VERB" and a.lemma == root
        ]
        assert verb_analyses == [], (
            f"slimmed root {root!r}: stale ma-NVOL surface {stale_ma!r} "
            f"should no longer produce a VERB analysis with lemma {root!r}"
        )

    @pytest.mark.parametrize(
        "root,_um_pfv,_um_ipfv,_um_ctpl,_stale_ma", SLIMMED_ROOTS
    )
    def test_ma_adj_surface_still_works(
        self, root: str, _um_pfv: str,
        _um_ipfv: str, _um_ctpl: str, _stale_ma: str,
    ) -> None:
        # The ma_adj cell in adjectives.yaml continues to produce
        # ``maganda`` / ``mabilis`` / ``malakas`` / ``mayaman`` ADJ
        # analyses (Phase 5g infrastructure, untouched by Commit 1).
        analyzer = Analyzer.from_default()
        ma_surface = "ma" + root
        out = analyzer.analyze_one(_tok(ma_surface))
        adj_analyses = [a for a in out if a.pos == "ADJ"]
        assert any(a.lemma == root for a in adj_analyses), (
            f"ma_adj surface {ma_surface!r} should still produce an "
            f"ADJ analysis with lemma {root!r}"
        )
