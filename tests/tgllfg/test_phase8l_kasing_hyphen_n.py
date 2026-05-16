"""Phase 8.L Commit 4: hyphen-joined ``Kasing-edad`` + pro-drop frame.

Two related fixes:

1. **Multiword pre-pass left-flanker carve-out**
   (``src/tgllfg/text/clitics.py:split_linker_ng``).

   The Phase 4 §7.5 ``-ng`` linker splitter eagerly peels ``-ng``
   off vowel+ng-final hosts. For ``Kasing-edad si Maria.`` that
   shaves ``Kasing`` into ``Kasi`` + ``-ng``, leaving the
   downstream :func:`merge_hyphen_compounds` looking at
   ``Kasi`` / ``-`` / ``edad`` — neither the literal join
   (``kasiedad``) nor the n-restored form is a known surface, so
   the merge fails and the parse fails too.

   The carve-out lookahead: when a vowel+ng-final token is
   immediately followed by ``-`` + alphabetic AND the literal
   join is a known surface, defer to the hyphen-merge pass
   instead of splitting. The kani-kaniyang case (right-flanker
   linker) is unaffected — the right flanker doesn't see the
   next-`-` lookahead.

2. **Subject-pro-drop equative + GEN-standard frame**
   (``src/tgllfg/cfg/clause.py``).

   Tagalog drops the NOM subject when contextually clear. The
   audit hit ``Kasing-edad pala ni Nadette.`` (R&G Intermediate
   page 238) reads "(She's) the same age, no less, as Nadette"
   with implicit subject. The new rule:

     S → ADJ[COMP_DEGREE=EQUATIVE] NP[CASE=GEN]
       (↑ PRED)            = 'ADJ <SUBJ>'
       (↑ SUBJ PRED)       = 'PRO'   ← synthesized null SUBJ
       (↑ ADJ_LEMMA)       = ↓1 LEMMA
       (↑ INTENS/DISTRIB/KASING_N) = ↓1 ...   ← standard lifts
       ↓2 ∈ (↑ ADJUNCT)
       (↓2 ROLE)           = 'EQUATIVE_STANDARD'

   Mirrors the two-NP equative rules in the same file with the
   NOM-comparee slot pro-dropped. PRED is still
   ``ADJ <SUBJ>`` so LMT's arg-binding pass finds the SUBJ slot
   bound (by PRO).
"""

from __future__ import annotations

import pytest


class TestPhase8lHyphenJoinedKasing:
    """``Kasing-edad`` (hyphen) parses identically to ``Kasingedad``
    (solid) once the left-flanker carve-out lands."""

    @pytest.mark.parametrize("solid,hyphen", [
        ("Kasingedad si Maria.",       "Kasing-edad si Maria."),
        ("Kasingedad ni Maria.",       "Kasing-edad ni Maria."),
        ("Kasingedad si Maria si Ana.",
                                       "Kasing-edad si Maria si Ana."),
    ])
    def test_hyphen_matches_solid(
        self, solid: str, hyphen: str,
    ) -> None:
        from tgllfg.core.pipeline import parse_text
        ps = parse_text(solid, n_best=2)
        ph = parse_text(hyphen, n_best=2)
        assert len(ps) >= 1, f"solid form {solid!r} did not parse"
        assert len(ph) >= 1, f"hyphen form {hyphen!r} did not parse"
        # Both reach the same ADJ_LEMMA + KASING_N flagging
        assert str(ps[0][1].feats.get("ADJ_LEMMA")) == "edad"
        assert str(ph[0][1].feats.get("ADJ_LEMMA")) == "edad"
        assert ps[0][1].feats.get("KASING_N") is True
        assert ph[0][1].feats.get("KASING_N") is True


class TestPhase8lProDropEquative:
    """Subject-pro-drop + GEN-standard equative parses."""

    @pytest.mark.parametrize("sentence", [
        # ADJ-base kasing- (no NOUN-derivation): bare
        "Kasingganda ni Maria.",
        # ADJ-base kasing- with discourse particle pala
        "Kasingganda pala ni Maria.",
        # NOUN-base kasing_n_eq (the audit-named shape)
        "Kasingedad ni Maria.",
        "Kasingedad pala ni Maria.",
        # Hyphen-joined NOUN-base
        "Kasing-edad ni Maria.",
        "Kasing-edad pala ni Maria.",
    ])
    def test_pro_drop_equative_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse for {sentence!r}"
        f = parses[0][1]
        subj = f.feats.get("SUBJ")
        assert subj is not None, f"SUBJ not synthesized for {sentence!r}"
        # The PRO SUBJ has PRED='PRO'
        assert str(subj.feats.get("PRED")) == "PRO", (
            f"{sentence!r}: SUBJ.PRED expected 'PRO', got "
            f"{subj.feats.get('PRED')!r}"
        )
        # The GEN-NP is on the matrix ADJUNCT with role STANDARD
        adjunct = f.feats.get("ADJUNCT")
        assert adjunct is not None
        roles = {
            str(m.feats.get("ROLE")) for m in adjunct
            if hasattr(m, "feats")
        }
        assert "EQUATIVE_STANDARD" in roles


class TestPhase8lLeftFlankerCarveOut:
    """The left-flanker carve-out fires only when the literal join
    is a known surface — non-canonical hyphenated compounds (e.g.,
    ``foo-bar``) are still passed through to the existing fall-
    through behavior."""

    def test_kasing_edad_merges(self) -> None:
        from tgllfg.text import (
            tokenize, split_linker_ng,
            merge_hyphen_compounds, split_apostrophe_t,
        )
        toks = tokenize("Kasing-edad si Maria.")
        toks = split_apostrophe_t(toks)
        toks = split_linker_ng(toks)
        toks = merge_hyphen_compounds(toks)
        norms = [t.norm for t in toks]
        assert "kasingedad" in norms, (
            f"expected 'kasingedad' in merged norms; got {norms!r}"
        )

    def test_kani_kaniyang_still_works(self) -> None:
        """Regression: right-flanker linker-split + canonical join
        for ``kani-kaniyang`` should still produce
        ``kanikaniya`` + ``-ng``."""
        from tgllfg.text import (
            tokenize, split_linker_ng,
            merge_hyphen_compounds, split_apostrophe_t,
        )
        toks = tokenize("kani-kaniyang aklat")
        toks = split_apostrophe_t(toks)
        toks = split_linker_ng(toks)
        toks = merge_hyphen_compounds(toks)
        norms = [t.norm for t in toks]
        assert "kanikaniya" in norms, (
            f"kani-kaniyang regression — norms={norms!r}"
        )
        assert "-ng" in norms, (
            f"kani-kaniyang regression — -ng linker missing from "
            f"norms={norms!r}"
        )
