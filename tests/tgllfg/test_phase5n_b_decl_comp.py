"""Phase 5n.B Commit 13: declarative-COMP factive embedding (§18 L56).

Closes §18.1 deferral L56 by adding a declarative-COMP path
parallel to the existing indirect-Q (Phase 5i C8 + 5n.B C11)
path under KNOW-class predicates:

    Alam kong kumain ang aso.       "I know that the dog ate."
    Akala kong kumain si Maria.     "I thought Maria ate."
    Naaalala kong pumunta siya.     "I remember that she went."

Two new rule additions in ``cfg/control.py``:

  (1) ``S_DECL_COMP → S`` (sibling to ``S_INTERROG_COMP``):
      lifts the inner S's f-structure and adds
      ``COMP_TYPE='DECLARATIVE'``.

  (2) ``S → V[CTRL_CLASS=KNOW] NP[CASE=GEN] PART[LINK=NA/NG]
      S_DECL_COMP``: matrix wrap consuming a GEN-NP experiencer,
      a bound linker (``-ng`` after vowel-final hosts; ``na``
      after consonant-final hosts), and the embedded declarative
      clause. Two rule variants — one per linker. The
      ``(↓3 LINK) =c '<link>'`` constraint locks down the
      non-conflict matcher leak.

Disambiguation from INTERROG-COMP: the linker token sits in a
different position from the ``kung`` complementizer (and carries
distinct feats), so the two paths are mutually exclusive.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


def _matrix_pred(text: str, prefix: str):
    """Return the parse whose matrix PRED starts with ``prefix``,
    or None if no such parse exists."""
    parses = parse_text(text, n_best=10)
    for p in parses:
        if (p[1].feats.get("PRED") or "").startswith(prefix):
            return p
    return None


# === Each KNOW-class predicate × declarative-COMP ====================


class TestDeclarativeCompPerPredicate:
    """All five KNOW-class predicates (alam + the 4 added in
    Phase 5n.B C12) take a declarative ``-ng``-linked
    complement. The matrix COMP carries
    ``COMP_TYPE='DECLARATIVE'``."""

    @pytest.mark.parametrize("sentence,pred_prefix", [
        ("Alam kong kumain ang aso.",       "KNOW"),
        ("Akala kong kumain si Maria.",     "BELIEVE"),
        ("Isip kong kumain ang bata.",      "THINK"),
        ("Naririnig kong pumunta siya.",    "HEAR"),
        ("Naaalala kong tumakbo si Juan.",  "REMEMBER"),
    ])
    def test_decl_comp_parses(
        self, sentence: str, pred_prefix: str
    ) -> None:
        result = _matrix_pred(sentence, pred_prefix)
        assert result is not None, (
            f"{sentence!r} did not produce a parse with PRED "
            f"starting with {pred_prefix!r}"
        )
        _ct, fs, _astr, _diags = result
        comp = fs.feats.get("COMP")
        assert comp is not None
        assert comp.feats.get("COMP_TYPE") == "DECLARATIVE", (
            f"expected COMP_TYPE='DECLARATIVE'; got {comp.feats.get('COMP_TYPE')!r}"
        )


# === Other GEN pronouns (3S, 2S) ====================================


class TestDeclarativeCompPerPronoun:
    """The matrix wrap admits any GEN-NP — not just 1S ``ko/kong``.
    Validate with 3S ``niya/niyang`` and 2S ``mo/mong``."""

    @pytest.mark.parametrize("sentence", [
        "Alam niyang kumain ang aso.",     # 3S niyang
        "Alam mong kumain ang aso.",       # 2S mong
    ])
    def test_other_gen_pronouns(self, sentence: str) -> None:
        result = _matrix_pred(sentence, "KNOW")
        assert result is not None
        _ct, fs, _astr, _diags = result
        comp = fs.feats.get("COMP")
        assert comp is not None
        assert comp.feats.get("COMP_TYPE") == "DECLARATIVE"


# === Disambiguation from INTERROG-COMP ==============================


class TestNoCrossFiring:
    """The DECL-COMP path requires a linker (``-ng`` or ``na``);
    the INTERROG-COMP path requires the ``kung`` complementizer.
    Sentences in either path produce a single parse — no
    cross-firing."""

    def test_interrog_q_unique_parse(self) -> None:
        """Wh indirect-Q gets a single INTERROG parse, not also
        DECLARATIVE — the DECL-COMP rule's
        ``(↓3 LINK) =c 'NG/NA'`` constraint blocks ``kung`` from
        filling the PART slot."""
        parses = parse_text("Alam ko kung sino ang kumain.")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        comp = fs.feats.get("COMP")
        assert comp is not None
        assert comp.feats.get("COMP_TYPE") == "INTERROG"

    def test_decl_comp_unique_parse(self) -> None:
        """The DECL-COMP path produces a single parse — no
        cross-firing into INTERROG (which would require a kung
        complementizer that's not present)."""
        parses = parse_text("Alam kong kumain ang aso.")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        comp = fs.feats.get("COMP")
        assert comp is not None
        assert comp.feats.get("COMP_TYPE") == "DECLARATIVE"


# === Phase 5i / 5n.B C11 / 5n.B C12 regression ======================


class TestExistingPathsUnchanged:
    """The C13 additions don't disturb existing KNOW-class paths
    (Phase 5i C8 wh-indirect-Q, 5n.B C11 yes/no indirect-Q, 5n.B
    C12 other KNOW-class predicates with INTERROG-COMP)."""

    def test_wh_interrog_unchanged(self) -> None:
        result = _matrix_pred("Alam ko kung sino ang kumain.", "KNOW")
        assert result is not None
        _ct, fs, _astr, _diags = result
        comp = fs.feats.get("COMP")
        assert comp is not None
        assert comp.feats.get("COMP_TYPE") == "INTERROG"

    def test_yes_no_interrog_unchanged(self) -> None:
        result = _matrix_pred("Alam ko kung kumain ang aso.", "KNOW")
        assert result is not None
        _ct, fs, _astr, _diags = result
        comp = fs.feats.get("COMP")
        assert comp is not None
        assert comp.feats.get("COMP_TYPE") == "INTERROG"
        assert comp.feats.get("COMP_QTYPE") == "YES_NO"

    def test_c12_predicate_with_interrog_comp(self) -> None:
        """A 5n.B C12 predicate (akala) still takes INTERROG-COMP
        with kung."""
        result = _matrix_pred("Akala ko kung sino ang kumain.", "BELIEVE")
        assert result is not None
        _ct, fs, _astr, _diags = result
        comp = fs.feats.get("COMP")
        assert comp is not None
        assert comp.feats.get("COMP_TYPE") == "INTERROG"
