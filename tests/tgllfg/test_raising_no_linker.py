"""Phase 5d Commit 1: additional evidential raising verbs.

Phase 5c Commit 5 seeded ``mukha`` and ``baka`` as
``CTRL_CLASS=RAISING`` raising verbs that take a bound `-ng`
linker between V and the embedded S (``Mukhang kumakain ang
bata``). Phase 5d adds two more evidential raising verbs that
DO NOT take a linker in standard Tagalog:

* ``parang`` "seems like" — ``Parang kumakain ang bata`` (no `-ng`)
* ``tila`` "apparently" — ``Tila kumakain ang bata`` (no `-ng`)

These carry a distinct ``CTRL_CLASS=RAISING_BARE`` value rather
than reusing ``CTRL_CLASS=RAISING``, because the parser's
non-conflict feature matcher would otherwise let a bare-raising
wrap rule cross-fire on ``mukhang`` / ``bakang`` sentences
(producing a duplicate parse alongside the linked-raising one).
A new grammar rule ``S → V[CTRL_CLASS=RAISING_BARE] S`` covers
the no-linker form; the existing ``mukha`` / ``baka`` linked
rule is unchanged.

These tests cover:

* parang and tila parsing as raising verbs with PRED
  ``SEEMS-LIKE`` / ``APPARENTLY``.
* Various embedded-clause shapes: AV intransitive, AV
  transitive, OV transitive.
* Structure-shared SUBJ (matrix.SUBJ ≡ XCOMP.SUBJ).
* Inner negation in the embedded clause.
* No spurious ``lmt-mismatch`` diagnostics.
* The ``mukha`` / ``baka`` linked-raising parses still produce
  exactly 1 result (no duplicate from the new bare rule).
* The CTRL_CLASS=RAISING vs RAISING_BARE distinction is
  observable in the morph analysis.

The third deferred raising-like word, ``yata`` "supposedly", is
NOT added as a raising verb — it's already analyzed as a
Wackernagel 2P clitic (``EPISTEMIC=PRESUMABLY``) under the §7.3
clitic-placement pass and behaves syntactically as an enclitic,
not a clause-initial verb.
"""

from __future__ import annotations

from tgllfg.core.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.core.pipeline import parse_text
from tgllfg.text import tokenize


def _first(text: str) -> tuple[FStructure, list]:
    rs = parse_text(text)
    assert rs, f"no parse for {text!r}"
    _, f, _, diags = rs[0]
    return f, diags


# === Morph: parang / tila carry CTRL_CLASS=RAISING_BARE =================


class TestRaisingBareMorph:

    def test_parang_is_raising_bare_verb(self) -> None:
        toks = tokenize("parang")
        ml = analyze_tokens(toks)
        verb_analyses = [a for a in ml[0] if a.pos == "VERB"]
        assert verb_analyses, "parang should have a VERB analysis"
        ctrl_classes = [a.feats.get("CTRL_CLASS") for a in verb_analyses]
        assert "RAISING_BARE" in ctrl_classes

    def test_tila_is_raising_bare_verb(self) -> None:
        toks = tokenize("tila")
        ml = analyze_tokens(toks)
        verb_analyses = [a for a in ml[0] if a.pos == "VERB"]
        assert verb_analyses
        ctrl_classes = [a.feats.get("CTRL_CLASS") for a in verb_analyses]
        assert "RAISING_BARE" in ctrl_classes

    def test_mukha_keeps_ctrl_class_raising(self) -> None:
        # mukha continues to use CTRL_CLASS=RAISING (linker-taking).
        toks = tokenize("mukha")
        ml = analyze_tokens(toks)
        verb_analyses = [a for a in ml[0] if a.pos == "VERB"]
        assert verb_analyses
        ctrl_classes = [a.feats.get("CTRL_CLASS") for a in verb_analyses]
        assert "RAISING" in ctrl_classes
        assert "RAISING_BARE" not in ctrl_classes


# === Parse-level: parang / tila as raising verbs ========================


class TestParangParse:

    def test_av_intransitive_embedded(self) -> None:
        f, _ = _first("Parang umalis ang bata.")
        assert f.feats.get("PRED") == "SEEMS-LIKE <XCOMP> SUBJ"
        xc = f.feats.get("XCOMP")
        assert isinstance(xc, FStructure)
        assert xc.feats.get("PRED") == "ALIS <SUBJ>"

    def test_av_transitive_embedded(self) -> None:
        f, _ = _first("Parang kumakain ang bata ng isda.")
        xc = f.feats.get("XCOMP")
        assert isinstance(xc, FStructure)
        assert xc.feats.get("PRED") == "EAT <SUBJ, OBJ>"

    def test_ov_embedded(self) -> None:
        # OV embedded — the raised SUBJ is the patient pivot.
        f, _ = _first("Parang kinain ng aso ang isda.")
        xc = f.feats.get("XCOMP")
        assert isinstance(xc, FStructure)
        assert xc.feats.get("VOICE") == "OV"


class TestTilaParse:

    def test_av_intransitive_embedded(self) -> None:
        f, _ = _first("Tila umalis ang bata.")
        assert f.feats.get("PRED") == "APPARENTLY <XCOMP> SUBJ"
        xc = f.feats.get("XCOMP")
        assert isinstance(xc, FStructure)
        assert xc.feats.get("PRED") == "ALIS <SUBJ>"

    def test_av_transitive_embedded(self) -> None:
        f, _ = _first("Tila kumakain ang bata ng isda.")
        xc = f.feats.get("XCOMP")
        assert isinstance(xc, FStructure)
        assert xc.feats.get("PRED") == "EAT <SUBJ, OBJ>"


# === Structure-sharing across the raising boundary ======================


class TestRaisingBareBinding:

    def test_parang_subj_shared(self) -> None:
        f, _ = _first("Parang kumakain ang bata.")
        m_subj = f.feats.get("SUBJ")
        xc = f.feats.get("XCOMP")
        assert isinstance(m_subj, FStructure)
        assert isinstance(xc, FStructure)
        x_subj = xc.feats.get("SUBJ")
        assert isinstance(x_subj, FStructure)
        assert m_subj.id == x_subj.id

    def test_tila_subj_shared(self) -> None:
        f, _ = _first("Tila kumakain ang bata.")
        m_subj = f.feats.get("SUBJ")
        xc = f.feats.get("XCOMP")
        assert isinstance(m_subj, FStructure) and isinstance(xc, FStructure)
        assert m_subj.id == xc.feats["SUBJ"].id  # type: ignore[union-attr]


# === Inner negation under bare-raising ==================================


class TestBareRaisingNegation:

    def test_parang_inner_neg(self) -> None:
        # ``Parang hindi kumakain ang bata`` — "the child seems
        # not to be eating".
        f, _ = _first("Parang hindi kumakain ang bata.")
        xc = f.feats.get("XCOMP")
        assert isinstance(xc, FStructure)
        assert xc.feats.get("POLARITY") == "NEG"
        # Matrix not negated.
        assert f.feats.get("POLARITY") != "NEG"

    def test_tila_inner_neg(self) -> None:
        f, _ = _first("Tila hindi umalis ang bata.")
        xc = f.feats.get("XCOMP")
        assert isinstance(xc, FStructure)
        assert xc.feats.get("POLARITY") == "NEG"


# === LMT clean ===========================================================


class TestBareRaisingLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Parang kumakain ang bata.",
            "Tila kumakain ang bata.",
            "Parang kinain ng aso ang isda.",
            "Tila umalis ang bata.",
        ):
            _, diags = _first(s)
            assert not any(d.is_blocking() for d in diags), (
                f"unexpected blocking diags on {s!r}: "
                f"{[d.kind for d in diags]}"
            )

    def test_no_lmt_mismatch(self) -> None:
        for s in (
            "Parang kumakain ang bata.",
            "Tila kumakain ang bata.",
        ):
            _, diags = _first(s)
            assert not any(d.kind == "lmt-mismatch" for d in diags)


# === Regression: linked-raising still produces exactly 1 parse ==========


class TestLinkedRaisingNoDuplicate:
    """The bare-raising rule must NOT cross-fire on mukha / baka
    sentences. With CTRL_CLASS=RAISING vs RAISING_BARE split, the
    matcher can't conflate the two; mukhang / bakang produce
    exactly one full parse."""

    def test_mukhang_one_parse(self) -> None:
        rs = parse_text("Mukhang kumakain ang bata.", n_best=10)
        assert len(rs) == 1, (
            f"expected exactly 1 parse for 'Mukhang kumakain ang "
            f"bata.', got {len(rs)}"
        )

    def test_bakang_one_parse(self) -> None:
        rs = parse_text("Bakang umuwi ang bata.", n_best=10)
        assert len(rs) == 1


# === Disambiguation: yata stays a clitic, not a raising verb ============


class TestYataStaysClitic:
    """``yata`` is documented as a Wackernagel 2P clitic
    (`EPISTEMIC=PRESUMABLY`); it is NOT a raising verb in this
    grammar even though it shares the evidential semantics. The
    test pins this behaviour: yata's morph analyses don't include
    a CTRL_CLASS=RAISING(_BARE) reading."""

    def test_yata_is_2p_clitic(self) -> None:
        toks = tokenize("yata")
        ml = analyze_tokens(toks)
        # At least one PART analysis; no VERB-raising analysis.
        positions = [a.pos for a in ml[0]]
        assert "PART" in positions
        ctrl_classes = [
            a.feats.get("CTRL_CLASS") for a in ml[0]
        ]
        assert "RAISING" not in ctrl_classes
        assert "RAISING_BARE" not in ctrl_classes
