"""Phase 5f closing deferral: clause-initial Q-with-clitic predicates.

Two surface patterns, both clause-initial, both expressing what the
existing float-form rules already parse but with the Q / cardinal
fronted (S&O 1972 §4.5 / §4.7 mark these as the canonical surface):

* **Dual** (Phase 5f Commit 23): ``Pareho silang kumain.`` "they
  both ate" / ``Kumain sila pareho.`` (existing float). New rule
  in ``cfg/clitic.py``: ``S → Q[DUAL=YES] PRON[CASE=NOM] PART[LINK]
  V[VOICE=AV]`` with optional GEN / DAT post-V arguments. The Q
  rides as ADJ with ``ANTECEDENT = (↑ SUBJ)``, mirroring the
  float rule.
* **Distributive predicative** (Phase 5f Commit 19):
  ``Tigisang aklat sila.`` "they each have one book" / ``Bumili
  sila ng tigisang aklat.`` (existing NP-modifier float). New rule
  in ``cfg/clause.py``: ``S → NUM[CARDINAL=YES] PART[LINK] N
  NP[CASE=NOM]`` constrained on ``DISTRIB=YES``. The matrix
  predicate is ``CARDINAL <SUBJ, OBJ>`` with the NOM-pivot as SUBJ
  (the possessors) and the bare N as OBJ (the per-possessor count).

Tests cover:

* Dual AV intransitive: ``Pareho`` / ``Kapwa`` × multiple PRON
  surfaces (sila / kami / kayo / tayo).
* Dual AV transitive (with OBJ).
* Dual AV ditransitive (with OBJ + DAT).
* Distributive predicative across cardinals 1-10.
* F-structure shape — Q rides as ADJ with ANTECEDENT linked to
  SUBJ; the distributive predicative carries DISTRIB=YES on the
  matrix.
* Negative: plain (non-DISTRIB) cardinal does NOT fire the
  predicative-distributive rule (``*Isang aklat sila.`` would over-
  generate to a distributive reading without the constraint).
* Float-form regression: the existing clause-final ``pareho`` /
  ``ng tigisang aklat`` parses still produce identical
  f-structures.
"""

from __future__ import annotations

import pytest

from tgllfg.common import FStructure
from tgllfg.pipeline import parse_text


def _matrix(text: str) -> FStructure | None:
    parses = parse_text(text, n_best=1)
    if not parses:
        return None
    return parses[0][1]


def _adj_dual(f: FStructure) -> FStructure | None:
    adj = f.feats.get("ADJ")
    if adj is None:
        return None
    members = list(adj) if isinstance(adj, frozenset) else [adj]
    return next(
        (m for m in members
         if isinstance(m, FStructure) and m.feats.get("DUAL") == "YES"),
        None,
    )


# --- Dual clause-initial -------------------------------------------------


class TestDualIntransitive:
    """``Pareho silang kumain.`` and variants."""

    @pytest.mark.parametrize("text,quant_lemma", [
        ("Pareho silang kumain.", "BOTH"),
        ("Kapwa silang kumain.", "BOTH"),
        ("Pareho kaming kumain.", "BOTH"),
        ("Kapwa kayong kumain.", "BOTH"),
        ("Pareho tayong kumain.", "BOTH"),
    ])
    def test_dual_intransitive(self, text: str, quant_lemma: str) -> None:
        f = _matrix(text)
        assert f is not None, f"no parse for {text!r}"
        assert f.feats.get("PRED") == "EAT <SUBJ>"
        assert f.feats.get("VOICE") == "AV"
        subj = f.feats.get("SUBJ")
        assert subj is not None and subj.feats.get("CASE") == "NOM"
        adj = _adj_dual(f)
        assert adj is not None, "expected DUAL Q in ADJ"
        assert adj.feats.get("QUANT") == quant_lemma
        # ANTECEDENT is reentrant with SUBJ — both feats refer to the
        # same FStructure id by identity (FStructure has eq=False but
        # __hash__ returns id).
        assert adj.feats.get("ANTECEDENT") is subj


class TestDualTransitive:
    """``Pareho silang kumain ng isda.`` — AV transitive with OBJ."""

    def test_dual_av_trans(self) -> None:
        f = _matrix("Pareho silang kumain ng isda.")
        assert f is not None
        assert f.feats.get("PRED") == "EAT <SUBJ, OBJ>"
        obj = f.feats.get("OBJ")
        assert obj is not None
        assert obj.feats.get("LEMMA") == "isda"
        adj = _adj_dual(f)
        assert adj is not None
        assert adj.feats.get("DUAL") == "YES"


class TestDualDitransitive:
    """``Pareho silang bumili ng isda sa palengke.`` — AV ditrans
    with OBJ + DAT."""

    def test_dual_av_ditrans(self) -> None:
        f = _matrix("Pareho silang bumili ng isda sa palengke.")
        assert f is not None
        assert f.feats.get("PRED") == "BUY <SUBJ, OBJ>"
        obj = f.feats.get("OBJ")
        assert obj is not None
        assert obj.feats.get("LEMMA") == "isda"
        adjuncts = f.feats.get("ADJUNCT")
        assert adjuncts, "expected DAT-NP in ADJUNCT"
        members = list(adjuncts) if isinstance(adjuncts, frozenset) else [adjuncts]
        dat_np = next(
            (m for m in members
             if isinstance(m, FStructure) and m.feats.get("CASE") == "DAT"),
            None,
        )
        assert dat_np is not None
        assert dat_np.feats.get("LEMMA") == "palengke"


# --- Distributive predicative -------------------------------------------


class TestDistributivePredicative:
    """``Tigisang aklat sila.`` and variants."""

    @pytest.mark.parametrize("digit_word,value", [
        ("tigisa",     "1"),
        ("tigdalawa",  "2"),
        ("tigtatlo",   "3"),
        ("tigapat",    "4"),
        ("tiglima",    "5"),
        ("tiganim",    "6"),
        ("tigpito",    "7"),
        ("tigwalo",    "8"),
        ("tigsiyam",   "9"),
        ("tigsampu",   "10"),
    ])
    def test_distrib_pred(self, digit_word: str, value: str) -> None:
        # The bound -ng linker is appended via the canonical sandhi
        # (vowel-final → -ng; consonant-final → na). All of tigisa..
        # tigsampu are vowel-final except tigapat / tiganim / tigwalo
        # / tigsiyam (consonant-final).
        if digit_word.endswith(("a", "e", "i", "o", "u")):
            surface_with_link = f"{digit_word}ng"
        else:
            surface_with_link = f"{digit_word} na"
        text = f"{surface_with_link} aklat sila."
        f = _matrix(text)
        assert f is not None, f"no parse for {text!r}"
        assert f.feats.get("PRED") == "CARDINAL <SUBJ, OBJ>"
        assert f.feats.get("CARDINAL_VALUE") == value
        assert f.feats.get("DISTRIB") == "YES"
        subj = f.feats.get("SUBJ")
        assert subj is not None and subj.feats.get("CASE") == "NOM"
        obj = f.feats.get("OBJ")
        assert obj is not None and obj.feats.get("LEMMA") == "aklat"


class TestDistributivePredicativeNegative:
    """The constraining ``(↓1 DISTRIB) =c 'YES'`` keeps the rule
    from firing on plain (non-distributive) cardinals."""

    def test_plain_cardinal_does_not_overgenerate(self) -> None:
        """``Isang aklat sila.`` shouldn't get the distributive
        reading. With the constraint, the rule doesn't fire; any
        parse that exists comes from a different rule (and would
        not carry DISTRIB=YES on the matrix)."""
        f = _matrix("Isang aklat sila.")
        if f is None:
            return  # acceptable — no parse means nothing overgenerates
        assert f.feats.get("DISTRIB") != "YES", (
            f"plain cardinal accidentally fired distributive rule: {f.feats}"
        )


# --- Float-form regression ----------------------------------------------


class TestFloatRegression:
    """The existing float-form parses are unchanged."""

    def test_dual_float_regression(self) -> None:
        f = _matrix("Kumain sila pareho.")
        assert f is not None
        adj = _adj_dual(f)
        assert adj is not None
        assert adj.feats.get("DUAL") == "YES"

    def test_distrib_np_modifier_regression(self) -> None:
        f = _matrix("Bumili sila ng tigisang aklat.")
        assert f is not None
        obj = f.feats.get("OBJ")
        assert obj is not None
        assert obj.feats.get("LEMMA") == "aklat"
        assert obj.feats.get("CARDINAL_VALUE") == "1"
