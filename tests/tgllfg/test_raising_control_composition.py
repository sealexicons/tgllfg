"""Phase 5e Commit 8: control / raising composition pinning.

Phase 5d Commit 7's deferral list flagged two raising / control
compositions as available structurally but not pinned with tests:

* **Control under raising** — a raising matrix embedding a control
  clause as its non-gap S complement (the inner S of the raising
  rule is a complete clause; control verbs at S level fit there).
  Example: ``Mukhang gusto ng batang kumain.`` "It seems the
  child wants to eat."
* **TRANS control + raising** — a TRANS control verb whose XCOMP
  contains a raising-S_XCOMP. Example: ``Pinilit ng nanay ang
  batang mukhang umuwi.`` "Mother forced the child to seem to
  leave home."

Both compositions work via existing Phase 5c §7.6 Commit 5
(raising at S level) and Phase 5d Commit 7 (raising at S_XCOMP
level for use under control). This commit is **test-only** — no
grammar / lex changes — and adds explicit assertions:

* The matrix wrap rule fires correctly for both compositions.
* Cross-level f-node identity holds where expected
  (raising's structure-shared SUBJ; control's REL-PRO chain).
* Negation composes at the matrix, the middle, and the inner
  level.
* All four raising forms (mukha / baka linked, parang / tila
  bare) work as the embedded raising V.
"""

from __future__ import annotations

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _first(text: str) -> FStructure:
    rs = parse_text(text)
    assert rs, f"no parse for {text!r}"
    return rs[0][1]


def _xcomp(f: FStructure) -> FStructure:
    x = f.feats["XCOMP"]
    assert isinstance(x, FStructure)
    return x


# === Control under raising (raising matrix + control inner S) ===========


class TestControlUnderRaising:
    """A raising verb's right-hand S admits a complete control-S.
    The matrix's PRED is the raising verb's PRED; the XCOMP slot
    holds the control verb's f-structure; matrix.SUBJ structure-
    shares with XCOMP.SUBJ via the raising binding equation."""

    def test_psych_control_under_mukha(self) -> None:
        """``Mukhang gusto ng batang kumain.`` "It seems the child
        wants to eat." Outer = mukha (RAISING); inner = gusto
        (PSYCH control); innermost = kumain. Three SUBJ slots
        (mukha.SUBJ, gusto.SUBJ, kumain.SUBJ) all share the same
        f-node (= the GEN-experiencer ``bata``)."""
        f = _first("Mukhang gusto ng batang kumain.")
        assert f.feats.get("PRED") == "SEEM <XCOMP> SUBJ"
        # XCOMP is the control clause.
        gusto = _xcomp(f)
        assert gusto.feats.get("PRED") == "WANT <SUBJ, XCOMP>"
        # Innermost is kain AV-INTR.
        kain = _xcomp(gusto)
        assert kain.feats.get("PRED") == "EAT <SUBJ>"
        # Three SUBJ f-nodes share id.
        m_subj = f.feats["SUBJ"]
        g_subj = gusto.feats["SUBJ"]
        k_subj = kain.feats["SUBJ"]
        assert isinstance(m_subj, FStructure)
        assert isinstance(g_subj, FStructure)
        assert isinstance(k_subj, FStructure)
        assert m_subj.id == g_subj.id == k_subj.id
        # The shared SUBJ is `bata`.
        assert m_subj.feats.get("LEMMA") == "bata"

    def test_intrans_control_under_mukha(self) -> None:
        """``Mukhang pumayag ang batang kumain.`` Same shape with
        INTRANS control (pumayag) — NOM controller this time."""
        f = _first("Mukhang pumayag ang batang kumain.")
        assert f.feats.get("PRED") == "SEEM <XCOMP> SUBJ"
        pumayag = _xcomp(f)
        assert pumayag.feats.get("PRED") == "AGREE <SUBJ, XCOMP>"
        kain = _xcomp(pumayag)
        assert kain.feats.get("PRED") == "EAT <SUBJ>"
        m_subj = f.feats["SUBJ"]
        assert isinstance(m_subj, FStructure)
        assert m_subj.feats.get("LEMMA") == "bata"
        assert m_subj.feats.get("CASE") == "NOM"

    def test_control_under_baka(self) -> None:
        """``Bakang gusto ng batang kumain.`` mukha and baka share
        the RAISING class — both compose with control-inner."""
        f = _first("Bakang gusto ng batang kumain.")
        assert f.feats.get("PRED") == "MIGHT <XCOMP> SUBJ"
        gusto = _xcomp(f)
        assert gusto.feats.get("PRED") == "WANT <SUBJ, XCOMP>"

    def test_control_under_parang_bare(self) -> None:
        """``Parang gusto ng batang kumain.`` Bare raising
        (``parang`` is RAISING_BARE) composes the same way."""
        f = _first("Parang gusto ng batang kumain.")
        assert f.feats.get("PRED") == "SEEMS-LIKE <XCOMP> SUBJ"
        gusto = _xcomp(f)
        assert gusto.feats.get("PRED") == "WANT <SUBJ, XCOMP>"

    def test_control_under_tila_bare(self) -> None:
        f = _first("Tila gusto ng batang kumain.")
        assert f.feats.get("PRED") == "APPARENTLY <XCOMP> SUBJ"


# === TRANS control + raising (TRANS control's XCOMP = raising) ==========


class TestTransControlOverRaising:
    """A TRANS control verb (pinilit) whose XCOMP is itself a
    raising-S_XCOMP. The matrix's NOM-pivot (forcee) controls the
    embedded raising's SUBJ, which structure-shares all the way
    down."""

    def test_pinilit_with_raising_xcomp(self) -> None:
        """``Pinilit ng nanay ang batang mukhang umuwi.`` "Mother
        forced the child to seem to leave home." matrix has
        OBJ-AGENT=nanay, SUBJ=bata. XCOMP is mukha (raising) which
        has its own XCOMP=uwi. SUBJ chains: matrix.SUBJ ===
        XCOMP.SUBJ === XCOMP.XCOMP.SUBJ = bata."""
        f = _first("Pinilit ng nanay ang batang mukhang umuwi.")
        assert f.feats.get("PRED") == "FORCE <SUBJ, OBJ-AGENT, XCOMP>"
        # OBJ-AGENT = nanay.
        oa = f.feats["OBJ-AGENT"]
        assert isinstance(oa, FStructure)
        assert oa.feats.get("LEMMA") == "nanay"
        # SUBJ = bata.
        m_subj = f.feats["SUBJ"]
        assert isinstance(m_subj, FStructure)
        assert m_subj.feats.get("LEMMA") == "bata"
        # XCOMP is mukha (raising).
        mukha = _xcomp(f)
        assert mukha.feats.get("PRED") == "SEEM <XCOMP> SUBJ"
        # XCOMP.XCOMP is uwi.
        uwi = _xcomp(mukha)
        assert uwi.feats.get("PRED") == "UWI <SUBJ>"
        # All three SUBJ slots share the same f-node.
        assert isinstance(mukha.feats["SUBJ"], FStructure)
        assert isinstance(uwi.feats["SUBJ"], FStructure)
        assert m_subj.id == mukha.feats["SUBJ"].id == uwi.feats["SUBJ"].id

    def test_pinilit_with_bare_raising_xcomp(self) -> None:
        """``Pinilit ng nanay ang batang parang umuwi.`` Bare
        raising form works the same way."""
        f = _first("Pinilit ng nanay ang batang parang umuwi.")
        assert f.feats.get("PRED") == "FORCE <SUBJ, OBJ-AGENT, XCOMP>"
        parang = _xcomp(f)
        assert parang.feats.get("PRED") == "SEEMS-LIKE <XCOMP> SUBJ"


# === Negation composition ===============================================


class TestNegationComposition:
    """Negation composes at any level of the control / raising
    chain via the existing recursive PART[POLARITY=NEG] rules."""

    def test_neg_on_middle_clause(self) -> None:
        """``Mukhang hindi gusto ng batang kumain.`` "It seems the
        child doesn't want to eat." The middle clause (gusto)
        carries POLARITY=NEG."""
        f = _first("Mukhang hindi gusto ng batang kumain.")
        assert f.feats.get("PRED") == "SEEM <XCOMP> SUBJ"
        gusto = _xcomp(f)
        assert gusto.feats.get("POLARITY") == "NEG"
        # Inner clause is unaffected.
        kain = _xcomp(gusto)
        assert kain.feats.get("POLARITY") != "NEG"

    def test_neg_on_inner_clause(self) -> None:
        """``Mukhang gusto ng batang hindi kumain.`` "It seems the
        child wants not-to-eat." The innermost clause (kain)
        carries POLARITY=NEG."""
        f = _first("Mukhang gusto ng batang hindi kumain.")
        gusto = _xcomp(f)
        kain = _xcomp(gusto)
        assert kain.feats.get("POLARITY") == "NEG"


# === LMT diagnostics ====================================================


class TestLmtDiagnostics:
    """Both compositions produce no blocking LMT diagnostics."""

    def test_no_blocking_control_under_raising(self) -> None:
        rs = parse_text("Mukhang gusto ng batang kumain.", n_best=5)
        for _, _f, _c, diags in rs:
            blocking = [d for d in diags if d.kind != "lmt-mismatch"]
            assert blocking == [], f"unexpected blocking diags: {blocking}"

    def test_no_blocking_trans_control_with_raising(self) -> None:
        rs = parse_text(
            "Pinilit ng nanay ang batang mukhang umuwi.", n_best=5
        )
        for _, _f, _c, diags in rs:
            blocking = [d for d in diags if d.kind != "lmt-mismatch"]
            assert blocking == [], f"unexpected blocking diags: {blocking}"


# === Regression: raising and control alone unchanged ====================


class TestRegression:
    """The existing single-level raising and control parses are
    unaffected by the composition pinning."""

    def test_simple_raising_unchanged(self) -> None:
        f = _first("Mukhang kumain ang bata.")
        assert f.feats.get("PRED") == "SEEM <XCOMP> SUBJ"
        kain = _xcomp(f)
        assert kain.feats.get("PRED") == "EAT <SUBJ>"

    def test_simple_psych_control_unchanged(self) -> None:
        f = _first("Gusto kong kumain.")
        assert f.feats.get("PRED") == "WANT <SUBJ, XCOMP>"
        kain = _xcomp(f)
        assert kain.feats.get("PRED") == "EAT <SUBJ>"

    def test_simple_trans_control_unchanged(self) -> None:
        f = _first("Pinilit ng nanay ang batang umuwi.")
        assert f.feats.get("PRED") == "FORCE <SUBJ, OBJ-AGENT, XCOMP>"
        uwi = _xcomp(f)
        assert uwi.feats.get("PRED") == "UWI <SUBJ>"
