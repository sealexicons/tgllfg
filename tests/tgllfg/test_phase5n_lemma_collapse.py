"""Phase 5n.A Commit 4 — orthographic-variant collapse extension (§18 L74).

Phase 5j Commit 7 introduced the ``MorphAnalysis.lemma = feats.get(
"LEMMA", surface)`` collapse for the ``particles`` branch of
``_build_index`` so that orthographic variants (e.g.,
``surface: pwede, feats: {LEMMA: puwede}``) route to one canonical
``LexicalEntry`` rather than duplicating entries per spelling.

Phase 5n.A Commit 4 extends the same mechanic to the four other lex
branches:

* **pronouns** — synthetic ``surface: nya, feats: {LEMMA: niya}``
  yields an analysis with ``lemma=niya``.
* **nouns** — synthetic ``citation: kwarto, feats: {LEMMA: kuwarto}``
  yields a NOUN analysis at index ``kwarto`` with ``lemma=kuwarto``.
* **adjectives (bare-root)** — synthetic non-productive ADJ entry
  with a LEMMA feat picks up the canonical lemma.
* **adjectives (paradigm)** — synthetic ma_adj root with a LEMMA
  feat: every derived ``ma+root`` surface carries the canonical
  ``lemma``.
* **verbs (paradigm)** — synthetic verb root with a LEMMA feat:
  every inflected cell carries the canonical ``lemma``.

Tests use synthetic ``MorphData`` rather than mutating the seed YAML.
The Phase 5j Commit 7 PART pattern is also regression-tested to
confirm no behavioural change there.
"""

from __future__ import annotations

from tgllfg.core.common import Token
from tgllfg.morph import (
    AdjectiveCell,
    Analyzer,
    MorphData,
    Operation,
    Particle,
    Pronoun,
    Root,
    VerbalCell,
)


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === Pronouns ============================================================


class TestPronounLemmaCollapse:
    """A pronoun entry with a ``LEMMA`` feat that differs from its
    surface yields an analysis whose ``lemma`` field reflects the
    canonical name."""

    def test_pronoun_with_lemma_feat_collapses(self) -> None:
        data = MorphData(
            pronouns=[
                Pronoun(
                    surface="nya",
                    feats={
                        "PERS": "3", "NUM": "SG", "CASE": "GEN",
                        "LEMMA": "niya",
                    },
                    is_clitic=True,
                )
            ]
        )
        analyzer = Analyzer(data)
        out = analyzer.analyze_one(_tok("nya"))
        prons = [a for a in out if a.pos == "PRON"]
        assert len(prons) == 1
        assert prons[0].lemma == "niya", (
            f"expected lemma=niya, got {prons[0].lemma!r}"
        )
        # The feats dict still carries LEMMA (not consumed by the
        # collapse) so the grammar's ``(↑ LEMMA) = ↓ LEMMA`` works.
        assert prons[0].feats.get("LEMMA") == "niya"

    def test_pronoun_without_lemma_feat_uses_surface(self) -> None:
        data = MorphData(
            pronouns=[
                Pronoun(
                    surface="ako",
                    feats={"PERS": "1", "NUM": "SG", "CASE": "NOM"},
                )
            ]
        )
        analyzer = Analyzer(data)
        out = analyzer.analyze_one(_tok("ako"))
        prons = [a for a in out if a.pos == "PRON"]
        assert len(prons) == 1
        assert prons[0].lemma == "ako"


# === Nouns ===============================================================


class TestNounLemmaCollapse:
    """A noun root with a ``LEMMA`` feat that differs from its
    citation yields an analysis whose ``lemma`` field reflects the
    canonical name. The index key is the surface (citation), so a
    lookup of the variant spelling returns the canonical lemma."""

    def test_noun_with_lemma_feat_collapses(self) -> None:
        data = MorphData(
            roots=[
                Root(
                    citation="kwarto",
                    pos="NOUN",
                    gloss="room (variant spelling)",
                    feats={"LEMMA": "kuwarto"},
                )
            ]
        )
        analyzer = Analyzer(data)
        out = analyzer.analyze_one(_tok("kwarto"))
        nouns = [a for a in out if a.pos == "NOUN"]
        assert len(nouns) == 1
        assert nouns[0].lemma == "kuwarto"
        assert nouns[0].feats.get("LEMMA") == "kuwarto"

    def test_noun_without_lemma_feat_uses_citation(self) -> None:
        data = MorphData(
            roots=[
                Root(
                    citation="aklat",
                    pos="NOUN",
                    gloss="book",
                )
            ]
        )
        analyzer = Analyzer(data)
        out = analyzer.analyze_one(_tok("aklat"))
        nouns = [a for a in out if a.pos == "NOUN"]
        assert len(nouns) == 1
        assert nouns[0].lemma == "aklat"
        # The default LEMMA fallback fires when no feat is declared.
        assert nouns[0].feats.get("LEMMA") == "aklat"


# === Adjectives — bare-root ==============================================


class TestAdjectiveBareRootLemmaCollapse:
    """A non-productive ADJ entry (``affix_class: []``) with a
    ``LEMMA`` feat collapses on the bare citation."""

    def test_adj_bare_root_with_lemma_feat_collapses(self) -> None:
        data = MorphData(
            roots=[
                Root(
                    citation="pareo",
                    pos="ADJ",
                    gloss="same/alike (variant spelling)",
                    affix_class=[],
                    feats={
                        "EQUATIVE": True,
                        "COMP_DEGREE": "EQUATIVE",
                        "LEMMA": "pareho",
                    },
                )
            ]
        )
        analyzer = Analyzer(data)
        out = analyzer.analyze_one(_tok("pareo"))
        adjs = [a for a in out if a.pos == "ADJ"]
        assert len(adjs) == 1
        assert adjs[0].lemma == "pareho"
        # PREDICATIVE=YES still set intrinsically.
        assert adjs[0].feats.get("PREDICATIVE") is True
        # Per-root EQUATIVE feat survives.
        assert adjs[0].feats.get("EQUATIVE") is True

    def test_adj_bare_root_without_lemma_feat_uses_citation(self) -> None:
        data = MorphData(
            roots=[
                Root(
                    citation="pareho",
                    pos="ADJ",
                    affix_class=[],
                    feats={"EQUATIVE": True},
                )
            ]
        )
        analyzer = Analyzer(data)
        out = analyzer.analyze_one(_tok("pareho"))
        adjs = [a for a in out if a.pos == "ADJ"]
        assert len(adjs) == 1
        assert adjs[0].lemma == "pareho"


# === Adjectives — paradigm-derived =======================================


class TestAdjectiveParadigmLemmaCollapse:
    """A productive ADJ root with a LEMMA feat: every derived
    ``ma+root`` surface carries the canonical lemma."""

    def test_adj_paradigm_with_lemma_feat_collapses(self) -> None:
        data = MorphData(
            roots=[
                Root(
                    citation="ganda_alt",  # synthetic alternate citation
                    pos="ADJ",
                    affix_class=["ma_adj"],
                    feats={"LEMMA": "ganda"},
                )
            ],
            adjective_cells=[
                AdjectiveCell(
                    affix_class="ma_adj",
                    operations=[Operation(op="prefix", value="ma")],
                ),
            ],
        )
        analyzer = Analyzer(data)
        out = analyzer.analyze_one(_tok("maganda_alt"))
        adjs = [a for a in out if a.pos == "ADJ"]
        assert len(adjs) == 1
        assert adjs[0].lemma == "ganda", (
            f"derived surface should carry canonical lemma 'ganda' "
            f"(via root.feats.LEMMA), got {adjs[0].lemma!r}"
        )

    def test_adj_paradigm_without_lemma_feat_uses_citation(self) -> None:
        data = MorphData(
            roots=[
                Root(
                    citation="ganda",
                    pos="ADJ",
                    affix_class=["ma_adj"],
                )
            ],
            adjective_cells=[
                AdjectiveCell(
                    affix_class="ma_adj",
                    operations=[Operation(op="prefix", value="ma")],
                ),
            ],
        )
        analyzer = Analyzer(data)
        out = analyzer.analyze_one(_tok("maganda"))
        adjs = [a for a in out if a.pos == "ADJ"]
        assert len(adjs) == 1
        assert adjs[0].lemma == "ganda"


# === Verbs — paradigm-derived ============================================


class TestVerbParadigmLemmaCollapse:
    """A verb root with a LEMMA feat: every inflected cell carries
    the canonical lemma."""

    def test_verb_paradigm_with_lemma_feat_collapses(self) -> None:
        data = MorphData(
            roots=[
                Root(
                    citation="kwento",  # variant spelling
                    pos="VERB",
                    transitivity="TR",
                    affix_class=["mag"],
                    feats={"LEMMA": "kuwento"},
                )
            ],
            paradigm_cells=[
                VerbalCell(
                    voice="AV",
                    aspect="PFV",
                    mood="IND",
                    transitivity="",
                    affix_class="mag",
                    operations=[Operation(op="prefix", value="nag")],
                ),
            ],
        )
        analyzer = Analyzer(data)
        out = analyzer.analyze_one(_tok("nagkwento"))
        verbs = [a for a in out if a.pos == "VERB"]
        assert len(verbs) == 1
        assert verbs[0].lemma == "kuwento", (
            f"derived inflected surface should carry canonical lemma "
            f"'kuwento' (via root.feats.LEMMA), got {verbs[0].lemma!r}"
        )
        assert verbs[0].feats.get("VOICE") == "AV"
        assert verbs[0].feats.get("ASPECT") == "PFV"

    def test_verb_paradigm_without_lemma_feat_uses_citation(self) -> None:
        data = MorphData(
            roots=[
                Root(
                    citation="kuwento",
                    pos="VERB",
                    transitivity="TR",
                    affix_class=["mag"],
                )
            ],
            paradigm_cells=[
                VerbalCell(
                    voice="AV",
                    aspect="PFV",
                    mood="IND",
                    transitivity="",
                    affix_class="mag",
                    operations=[Operation(op="prefix", value="nag")],
                ),
            ],
        )
        analyzer = Analyzer(data)
        out = analyzer.analyze_one(_tok("nagkuwento"))
        verbs = [a for a in out if a.pos == "VERB"]
        assert len(verbs) == 1
        assert verbs[0].lemma == "kuwento"


# === Particle regression =================================================


class TestParticleLemmaCollapseStillWorks:
    """The Phase 5j Commit 7 mechanic for particles must still
    fire — Commit 4 only adds new branches; it doesn't change the
    particles branch."""

    def test_particle_with_lemma_feat_collapses(self) -> None:
        data = MorphData(
            particles=[
                Particle(
                    surface="pwede",
                    pos="VERB",
                    feats={"CTRL_CLASS": "MODAL", "LEMMA": "puwede"},
                ),
            ]
        )
        analyzer = Analyzer(data)
        out = analyzer.analyze_one(_tok("pwede"))
        # Particle entries with pos=VERB land in the particles index;
        # the surface 'pwede' should yield an analysis with
        # lemma='puwede'.
        with_canonical = [a for a in out if a.lemma == "puwede"]
        assert len(with_canonical) == 1, (
            f"particle pwede with LEMMA=puwede should produce one "
            f"analysis with lemma=puwede; got {[a.lemma for a in out]}"
        )

    def test_particle_without_lemma_feat_uses_surface(self) -> None:
        data = MorphData(
            particles=[
                Particle(
                    surface="bukas",
                    pos="ADV",
                    feats={"ADV_TYPE": "TIME"},
                )
            ]
        )
        analyzer = Analyzer(data)
        out = analyzer.analyze_one(_tok("bukas"))
        # ADV particles auto-set LEMMA=surface (Phase 5e Commit 3),
        # so the canonical lemma equals the surface.
        adv = [a for a in out if a.pos == "ADV"]
        assert len(adv) == 1
        assert adv[0].lemma == "bukas"


# === No-op regression on real lex =======================================


class TestNoOpOnRealLex:
    """The change is a no-op when no LEMMA feat differs from the
    surface/citation. Use the actual seed lex to confirm a sample
    of analyses still produce the expected canonical lemma."""

    def test_real_pronoun_ako_lemma(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("ako"))
        prons = [a for a in out if a.pos == "PRON"]
        assert len(prons) == 1
        assert prons[0].lemma == "ako"

    def test_real_noun_aklat_lemma(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("aklat"))
        nouns = [a for a in out if a.pos == "NOUN"]
        assert any(a.lemma == "aklat" for a in nouns)

    def test_real_verb_kumain_lemma(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("kumain"))
        verbs = [a for a in out if a.pos == "VERB"]
        assert any(a.lemma == "kain" for a in verbs)

    def test_real_adj_maganda_lemma(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("maganda"))
        adjs = [a for a in out if a.pos == "ADJ"]
        assert any(a.lemma == "ganda" for a in adjs)
