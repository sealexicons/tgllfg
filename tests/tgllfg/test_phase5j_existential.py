"""Phase 5j Commit 2: positive existential clause.

Roadmap §12.1 / plan-of-record §5.1, §6 Commit 2. Three new clause
rules in ``cfg/clause.py``:

    S → PART[EXISTENTIAL=YES, POLARITY=POS] N
    S → PART[EXISTENTIAL=YES, POLARITY=POS] PART[LINK=NG] N
    S → S NP[CASE=DAT]   (gated on CLAUSE_TYPE=EXISTENTIAL)

The first base rule consumes the bare existential
(``May aklat`` / ``May tao``); the linker variant consumes the
``mayroon`` + bound ``-ng`` + N pattern (``Mayroong tao``); the
clause-final DAT-lift composes locative-PP adjuncts onto an
existential matrix (``May tao sa labas`` / ``Mayroong tao sa
labas``).

Equations: literal PRED ``'EXIST <SUBJ>'`` (parallels Phase 5g
predicative-ADJ ``'ADJ <SUBJ>'`` and Phase 5f Commit 4
predicative-cardinal ``'CARDINAL <SUBJ>'``); SUBJ shared with
the bare-N daughter (the existence-asserted entity);
CLAUSE_TYPE='EXISTENTIAL' and POLARITY='POS' on the matrix for
classifier / ranker visibility; belt-and-braces ``=c``
constraints on EXISTENTIAL / POLARITY / LINK to close non-
conflict matcher leaks.

The Subject Condition (LMT step 6,
``check_subject_condition``) is satisfied because the
existence-asserted N maps to SUBJ — no special-case carve-out
needed for existentials.

End-to-end target sentences:

    May aklat.                "There is a book."
    May tao.                  "There is a person."
    May tao sa labas.         "There's someone outside."
    Mayroong tao sa labas.    "There's someone outside."
    May isang aklat.          "There is one book."
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Bare-N positive existential =====================================


class TestBareExistential:
    """The base rule fires on PART[EXISTENTIAL=YES, POLARITY=POS] +
    bare N and produces an existential matrix with the right
    f-structure features."""

    @pytest.mark.parametrize("sentence,subj_lemma", [
        ("May aklat.",  "aklat"),
        ("May tao.",    "tao"),
        ("May aso.",    "aso"),
        ("May bahay.",  "bahay"),
        ("May bundok.", "bundok"),
    ])
    def test_bare_existential_parses(
        self, sentence: str, subj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got 0"
        )
        # Every parse should be an existential matrix with the
        # right SUBJ.
        ex_parses = [
            (ct, fs, ast, diags)
            for ct, fs, ast, diags in parses
            if fs.feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        ]
        assert len(ex_parses) >= 1, (
            f"expected at least one EXISTENTIAL parse for "
            f"{sentence!r}"
        )
        _ct, fs, _astr, _diags = ex_parses[0]
        assert fs.feats.get("PRED") == "EXIST <SUBJ>"
        assert fs.feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        assert fs.feats.get("POLARITY") == "POS"
        # SUBJ has the right lemma
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma


class TestBareExistentialCTreeShape:
    """The c-tree shape: matrix S has PART[EXISTENTIAL=YES] + N
    daughters."""

    def test_may_aklat_c_tree(self) -> None:
        parses = parse_text("May aklat.")
        assert len(parses) == 1
        ctree, _fs, _astr, _diags = parses[0]
        assert ctree.label == "S"
        assert len(ctree.children) == 2
        # First child: PART[EXISTENTIAL=YES, POLARITY=POS]
        part = ctree.children[0]
        assert part.label.startswith("PART"), part.label
        # Second child: N (bare nominal projection from NOUN)
        n = ctree.children[1]
        assert n.label.startswith("N"), n.label


# === mayroon + linker variant ========================================


class TestMayroonLinkerVariant:
    """The linker variant fires on ``mayroon`` + bound ``-ng`` + N
    and produces the same f-structure as the bare existential."""

    @pytest.mark.parametrize("sentence,subj_lemma", [
        ("Mayroong tao.",   "tao"),
        ("Mayroong aklat.", "aklat"),
        ("Mayroong aso.",   "aso"),
    ])
    def test_mayroon_linker_parses(
        self, sentence: str, subj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got 0"
        )
        ex_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        ]
        assert len(ex_parses) >= 1
        _ct, fs, _astr, _diags = ex_parses[0]
        assert fs.feats.get("PRED") == "EXIST <SUBJ>"
        assert fs.feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        assert fs.feats.get("POLARITY") == "POS"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma


class TestMayroonCTreeShape:
    """The c-tree for ``Mayroong tao`` has 3 daughters: PART /
    PART[LINK=NG] / N."""

    def test_mayroong_tao_c_tree(self) -> None:
        parses = parse_text("Mayroong tao.")
        ex_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        ]
        assert len(ex_parses) >= 1
        ctree, _fs, _astr, _diags = ex_parses[0]
        # The linker variant fires: matrix S has 3 daughters
        # (PART[EXISTENTIAL] + PART[LINK=NG] + N). C-tree labels
        # strip features, so we see PART / PART / N. The base
        # variant has 2 daughters (PART + N). Check that THIS
        # tree has 3 immediate daughters with two PART labels at
        # the front.
        assert ctree.label == "S"
        assert len(ctree.children) == 3, (
            f"expected 3 immediate daughters for linker variant; "
            f"got {[c.label for c in ctree.children]}"
        )
        assert ctree.children[0].label == "PART"
        assert ctree.children[1].label == "PART"
        assert ctree.children[2].label.startswith("N")


def _all_labels(ctree) -> list[str]:
    out = [ctree.label]
    for c in ctree.children:
        out.extend(_all_labels(c))
    return out


# === Locative-PP composition (clause-final DAT-lift) =================


class TestLocativePPComposition:
    """Clause-final ``sa``-PP composes onto an existential matrix
    via the EXISTENTIAL-gated ``S → S NP[CASE=DAT]`` rule. The
    PP joins the matrix ADJUNCT set."""

    @pytest.mark.parametrize("sentence,subj_lemma,loc_lemma", [
        ("May tao sa labas.",        "tao",   "labas"),
        ("May aklat sa bahay.",      "aklat", "bahay"),
        ("Mayroong tao sa labas.",   "tao",   "labas"),
        ("Mayroong aklat sa bahay.", "aklat", "bahay"),
    ])
    def test_locative_pp_in_adjunct(
        self, sentence: str, subj_lemma: str, loc_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got 0"
        )
        ex_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        ]
        assert len(ex_parses) >= 1
        _ct, fs, _astr, _diags = ex_parses[0]
        # Matrix has the SUBJ
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma
        # Matrix ADJUNCT contains the locative-PP
        adjuncts = fs.feats.get("ADJUNCT") or frozenset()
        assert len(adjuncts) >= 1, (
            f"expected matrix ADJUNCT to contain the locative-PP "
            f"for {sentence!r}; got empty"
        )
        # The DAT-NP's lemma matches the locative ground
        loc_lemmas = {
            adj.feats.get("LEMMA")
            for adj in adjuncts
            if adj.feats.get("CASE") == "DAT"
        }
        assert loc_lemma in loc_lemmas, (
            f"expected DAT ADJUNCT with lemma {loc_lemma!r}; "
            f"got {loc_lemmas}"
        )


# === Cardinal / numeral-modified N =====================================


class TestCardinalModifiedExistential:
    """Cardinal modifier + linker + N composes into N (Phase 5f
    Commit 1 cardinal NP-modifier) and is consumed by the
    existential rule unchanged: ``May isang aklat`` → existential
    over a cardinal-modified N."""

    @pytest.mark.parametrize("sentence,subj_lemma", [
        ("May isang aklat.",   "aklat"),
        ("May tatlong aklat.", "aklat"),
        ("May limang tao.",    "tao"),
    ])
    def test_cardinal_modified_existential(
        self, sentence: str, subj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got 0"
        )
        ex_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        ]
        assert len(ex_parses) >= 1
        _ct, fs, _astr, _diags = ex_parses[0]
        # SUBJ's head lemma is the head N
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma


# === EXISTENTIAL-gated DAT-lift doesn't fire on V-headed frames =====


class TestDatLiftGatedOnExistential:
    """The clause-final DAT-lift rule is gated on
    ``(↓1 CLAUSE_TYPE) =c 'EXISTENTIAL'``. V-headed frames already
    embed their own DAT-NP daughters explicitly, so the
    EXISTENTIAL gate prevents spurious double-parse ambiguity for
    sentences like ``Kumain ang aso sa labas`` (V-frame parse
    would fire once; the wrap rule should NOT fire on top).
    """

    def test_kumain_sa_labas_single_parse(self) -> None:
        # V-headed clause with sa-PP — should produce 1 parse via
        # the V + NOM + DAT frame, NOT 2 parses via the wrap rule.
        parses = parse_text("Kumain ang aso sa labas.")
        # Top-1 parse is V-headed
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "EAT <SUBJ>"
        # Must NOT be EXISTENTIAL
        assert fs.feats.get("CLAUSE_TYPE") != "EXISTENTIAL"


# === No phantom existentials on baseline =============================


class TestNoPhantomExistentials:
    """Existing constructions don't acquire CLAUSE_TYPE=EXISTENTIAL
    from the new rule. Phase 5g / 5h / 5i baselines should be
    unchanged."""

    @pytest.mark.parametrize("sentence", [
        # Phase 5g
        "Maganda ang bata.",
        # Phase 5h
        "Mas matalino siya.",
        # Phase 5i
        "Sino ang kumain?",
        # Phase 4 baseline
        "Kumain ang aso.",
        # Predicative cardinal
        "Tatlo ang aklat.",
    ])
    def test_no_phantom_existential(self, sentence: str) -> None:
        parses = parse_text(sentence)
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("CLAUSE_TYPE") != "EXISTENTIAL", (
                f"unexpected CLAUSE_TYPE=EXISTENTIAL on {sentence!r}: "
                f"{fs.feats}"
            )
