"""Phase 5c §7.6 follow-on (Commit 5): raising verbs.

Phase 4 §7.6 deferred raising verbs (``mukha`` "seem", ``baka``
"might") on two counts:

1. The PRED-template format had no notation for non-thematic
   args. Phase 5c adds parser support for args after the closing
   ``>``: ``SEEM <XCOMP> SUBJ`` declares COMPLEMENT as the only
   thematic role and SUBJ as a non-thematic, syntactically required
   arg. ``PredTemplate`` gains separate ``thematic`` /
   ``non_thematic`` fields, with ``governables`` as the union.
2. Lexical disambiguation: ``mukha`` is also a noun ("face") and
   ``baka`` is also a noun ("cow"). Phase 5c relies on the
   distinctive matrix wrap-rule pattern
   (``V[CTRL_CLASS=RAISING]`` + linker + embedded S) to resolve
   the homonymy at parse time — no pre-parse disambiguation
   needed.

These tests cover:

* Parser: ``parse_pred_template`` recognises non-thematic args.
* Morph: ``mukha`` and ``baka`` carry both VERB[CTRL_CLASS=RAISING]
  and NOUN analyses.
* Parse-level: raising sentences with AV / OV / IPFV / negated
  embedded clauses; matrix.SUBJ === XCOMP.SUBJ structure-shared.
* Disambiguation: noun reading wins when ``mukha`` / ``baka``
  isn't clause-initial.
* LMT: no spurious ``lmt-mismatch`` from the non-thematic SUBJ
  (the new lex-entry GF set comparison includes non-thematic args).
* Completeness / coherence: raising verbs satisfy
  ``lfg_well_formed`` despite SUBJ not coming from a thematic role.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.fstruct.checks import (
    PredTemplate,
    lfg_well_formed,
    parse_pred_template,
)
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import tokenize


def _first(text: str) -> tuple[FStructure, list]:
    rs = parse_text(text)
    assert rs, f"no parse for {text!r}"
    _, f, _, diags = rs[0]
    return f, diags


# === PRED-template parser =================================================


class TestPredTemplateNonThematic:

    def test_seem_xcomp_subj(self) -> None:
        t = parse_pred_template("SEEM <XCOMP> SUBJ")
        assert t == PredTemplate(
            "SEEM", ("XCOMP", "SUBJ"), ("XCOMP",), ("SUBJ",)
        )

    def test_might_xcomp_subj(self) -> None:
        t = parse_pred_template("MIGHT <XCOMP> SUBJ")
        assert t.governables == ("XCOMP", "SUBJ")
        assert t.thematic == ("XCOMP",)
        assert t.non_thematic == ("SUBJ",)

    def test_no_thematic_args_only_non_thematic(self) -> None:
        # 0-thematic pattern (e.g., weather verbs): empty <> with
        # required non-thematic SUBJ.
        t = parse_pred_template("RAIN <> SUBJ")
        assert t.thematic == ()
        assert t.non_thematic == ("SUBJ",)
        assert t.governables == ("SUBJ",)


# === Morph: dual analyses for mukha / baka ===============================


class TestRaisingMorph:
    """Both surfaces carry VERB[CTRL_CLASS=RAISING] (from
    particles.yaml) AND NOUN (from roots.yaml). The grammar's
    syntactic constraints pick the right reading per context."""

    def test_mukha_has_verb_and_noun_analyses(self) -> None:
        toks = tokenize("mukha")
        ml = analyze_tokens(toks)
        positions = [a.pos for a in ml[0]]
        assert "VERB" in positions
        assert "NOUN" in positions
        # Verify the VERB analysis carries CTRL_CLASS=RAISING.
        ctrl_classes = [
            a.feats.get("CTRL_CLASS")
            for a in ml[0]
            if a.pos == "VERB"
        ]
        assert "RAISING" in ctrl_classes

    def test_baka_has_verb_and_noun_analyses(self) -> None:
        toks = tokenize("baka")
        ml = analyze_tokens(toks)
        positions = [a.pos for a in ml[0]]
        assert "VERB" in positions
        assert "NOUN" in positions


# === Parse-level: canonical raising sentences =============================


class TestRaisingParse:

    def test_mukha_av_intransitive_embedded(self) -> None:
        # ``Mukhang kumakain ang bata`` — "the child seems to be
        # eating".
        f, _ = _first("Mukhang kumakain ang bata.")
        assert f.feats.get("PRED") == "SEEM <XCOMP> SUBJ"
        xc = f.feats.get("XCOMP")
        assert isinstance(xc, FStructure)
        assert xc.feats.get("PRED") == "EAT <SUBJ>"

    def test_mukha_av_transitive_embedded(self) -> None:
        # ``Mukhang kumakain ang bata ng isda`` — embedded AV
        # transitive (with OBJ).
        f, _ = _first("Mukhang kumakain ang bata ng isda.")
        xc = f.feats.get("XCOMP")
        assert isinstance(xc, FStructure)
        assert xc.feats.get("PRED") == "EAT <SUBJ, OBJ>"

    def test_mukha_ov_embedded(self) -> None:
        # ``Mukhang kinakain ng aso ang isda`` — embedded OV; the
        # raised SUBJ is the patient pivot ``ang isda``.
        f, _ = _first("Mukhang kinakain ng aso ang isda.")
        xc = f.feats.get("XCOMP")
        assert isinstance(xc, FStructure)
        assert xc.feats.get("VOICE") == "OV"

    def test_baka_raising(self) -> None:
        # ``Bakang umuwi ang bata`` — "the child might leave".
        f, _ = _first("Bakang umuwi ang bata.")
        assert f.feats.get("PRED") == "MIGHT <XCOMP> SUBJ"
        xc = f.feats.get("XCOMP")
        assert isinstance(xc, FStructure)
        assert xc.feats.get("PRED") == "UWI <SUBJ>"


# === Structure-sharing: matrix.SUBJ === XCOMP.SUBJ ========================


class TestRaisingBinding:

    def test_subj_shared_between_matrix_and_xcomp(self) -> None:
        f, _ = _first("Mukhang kumakain ang bata.")
        m_subj = f.feats.get("SUBJ")
        xc = f.feats.get("XCOMP")
        assert isinstance(m_subj, FStructure)
        assert isinstance(xc, FStructure)
        x_subj = xc.feats.get("SUBJ")
        assert isinstance(x_subj, FStructure)
        assert m_subj.id == x_subj.id

    def test_baka_subj_shared(self) -> None:
        f, _ = _first("Bakang umuwi ang bata.")
        m_subj = f.feats.get("SUBJ")
        xc = f.feats.get("XCOMP")
        assert isinstance(m_subj, FStructure) and isinstance(xc, FStructure)
        assert m_subj.id == xc.feats["SUBJ"].id  # type: ignore[union-attr]

    def test_ov_embedded_subj_is_pivot(self) -> None:
        # Under OV, the embedded SUBJ is the patient pivot. The
        # raised matrix SUBJ shares with that pivot — so matrix.SUBJ
        # is ``isda``, not ``aso``.
        f, _ = _first("Mukhang kinakain ng aso ang isda.")
        m_subj = f.feats.get("SUBJ")
        xc = f.feats.get("XCOMP")
        assert isinstance(m_subj, FStructure) and isinstance(xc, FStructure)
        assert m_subj.id == xc.feats["SUBJ"].id  # type: ignore[union-attr]


# === Disambiguation by syntactic position =================================


class TestRaisingDisambiguation:
    """Both ``mukha`` and ``baka`` carry homophonous noun and
    verb-raising readings. The verb reading fires only when the
    surrounding wrap-rule pattern matches; otherwise the noun
    reading wins."""

    def test_baka_as_noun_when_mid_sentence(self) -> None:
        # ``Kumain ang baka`` — "the cow ate". `baka` is the SUBJ
        # noun; the raising verb reading has nowhere to go.
        f, _ = _first("Kumain ang baka.")
        assert f.feats.get("PRED") == "EAT <SUBJ>"
        # The matrix isn't a raising structure.
        assert "XCOMP" not in f.feats

    def test_mukha_in_isolation_does_not_force_raising(self) -> None:
        # ``Kumain ng mukha ang bata`` — "the child ate a face"
        # (semantically odd but syntactically clean). `mukha` here
        # is a noun in OBJ.
        rs = parse_text("Kumain ng mukha ang bata.")
        assert rs
        _, f, _, _ = rs[0]
        assert f.feats.get("PRED") == "EAT <SUBJ, OBJ>"


# === LMT: non-thematic SUBJ doesn't fire spurious mismatches ============


class TestRaisingLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Mukhang kumakain ang bata.",
            "Bakang umuwi ang bata.",
            "Mukhang kinakain ng aso ang isda.",
        ):
            _, diags = _first(s)
            assert not any(d.is_blocking() for d in diags), (
                f"unexpected blocking diags on {s!r}: "
                f"{[d.kind for d in diags]}"
            )

    def test_no_lmt_mismatch_diagnostics(self) -> None:
        # The non-thematic SUBJ is added to expected_gfs in
        # lmt_check; no spurious lmt-mismatch should fire.
        for s in (
            "Mukhang kumakain ang bata.",
            "Bakang umuwi ang bata.",
        ):
            _, diags = _first(s)
            assert not any(d.kind == "lmt-mismatch" for d in diags)


# === Completeness / coherence pass through lfg_well_formed ==============


class TestRaisingWellFormed:
    """The PRED ``SEEM <XCOMP> SUBJ`` selects two governable GFs.
    ``lfg_well_formed`` should accept the f-structure where both
    are present (XCOMP from the embedded clause, SUBJ from the
    raising binding)."""

    def test_seem_well_formed(self) -> None:
        f, _ = _first("Mukhang kumakain ang bata.")
        ok, diags = lfg_well_formed(f)
        assert ok, [(d.kind, d.message) for d in diags]

    def test_might_well_formed(self) -> None:
        f, _ = _first("Bakang umuwi ang bata.")
        ok, diags = lfg_well_formed(f)
        assert ok, [(d.kind, d.message) for d in diags]


# === Negation under raising ==============================================


class TestRaisingWithNegation:

    def test_inner_negation_in_xcomp(self) -> None:
        # ``Mukhang hindi kumakain ang bata`` — "the child seems
        # not to be eating". Negation attaches inside the embedded
        # clause via the regular S → PART[NEG] S rule.
        f, _ = _first("Mukhang hindi kumakain ang bata.")
        xc = f.feats.get("XCOMP")
        assert isinstance(xc, FStructure)
        assert xc.feats.get("POLARITY") == "NEG"
