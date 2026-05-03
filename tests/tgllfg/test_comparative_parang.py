"""Phase 5e Commit 26: comparative ``parang``.

Lifts the Phase 5d Commit 1 deferral. The existing parang entry
covered the evidential reading (``Parang umuulan`` "It seems
like it's raining" — ``parang + clause``). The comparative
reading (``Parang aso ang bata`` "The child is like a dog" —
``parang + bare-N + ang-NP``) is structurally distinct and gets
its own grammar rule in this commit.

### Lex

``parang`` carries an extra ``COMPARATIVE: "YES"`` feature in
``data/tgl/particles.yaml`` (quoted to keep YAML from parsing
``YES`` as a Python boolean — ``_lex_equations`` filters
non-string feats from the f-structure projection). ``tila``
keeps only ``CTRL_CLASS=RAISING_BARE`` (no comparative reading
in standard usage).

### Grammar

A new S rule:

```python
S → V[COMPARATIVE=YES, CTRL_CLASS=RAISING_BARE] N NP[CASE=NOM]
    (↑ PRED) = 'LIKE <SUBJ, OBJ>'
    (↑ OBJ) = ↓2
    (↑ SUBJ) = ↓3
    (↓1 COMPARATIVE) =c 'YES'
```

The constraining equation excludes ``tila`` (the category
matcher is non-conflict — ``V[COMPARATIVE=YES,
CTRL_CLASS=RAISING_BARE]`` would otherwise match ``tila`` by
absorption since tila has CTRL_CLASS=RAISING_BARE without a
COMPARATIVE feature).

### F-structure shape

```
PRED  = 'LIKE <SUBJ, OBJ>'
SUBJ  = the comparee  (the ang-NP)
OBJ   = the standard  (the bare N projecting via N → NOUN)
```

These tests cover:

* ``Parang aso ang bata.`` "The child is like a dog" — the
  canonical comparative.
* Various standard nouns (aso, bata, nanay, libro).
* Proper-noun comparee (``Parang aso si Juan.``).
* Numeral-modified standard (``Parang isang aso ang bata.``).
* Negation composition (``Hindi parang aso ang bata.``).
* Composition with relativization on the SUBJ NP.
* tila does NOT fire the comparative rule (regression).
* Evidential ``parang + clause`` (``Parang kumain ang bata``)
  still parses (regression).
* Evidential ``tila + clause`` still parses (regression).
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.pipeline import parse_text


def _comparative_parse(text: str) -> FStructure | None:
    """Find a parse with PRED='LIKE <SUBJ, OBJ>'."""
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        if f.feats.get("PRED") == "LIKE <SUBJ, OBJ>":
            return f
    return None


# === Comparative parses ===================================================


class TestComparativeParang:
    """``Parang + N + ang-NP`` — comparative predicate
    construction. PRED = 'LIKE <SUBJ, OBJ>', SUBJ = comparee,
    OBJ = standard."""

    def test_canonical(self) -> None:
        # Parang aso ang bata. — "The child is like a dog."
        f = _comparative_parse("Parang aso ang bata.")
        assert f is not None
        subj = f.feats.get("SUBJ")
        obj = f.feats.get("OBJ")
        assert isinstance(subj, FStructure)
        assert isinstance(obj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        assert obj.feats.get("LEMMA") == "aso"

    def test_proper_noun_comparee(self) -> None:
        # Parang aso si Juan. — "Juan is like a dog."
        f = _comparative_parse("Parang aso si Juan.")
        assert f is not None
        subj = f.feats.get("SUBJ")
        obj = f.feats.get("OBJ")
        assert isinstance(subj, FStructure)
        assert isinstance(obj, FStructure)
        assert obj.feats.get("LEMMA") == "aso"

    def test_various_standards(self) -> None:
        """Various standards of comparison."""
        for std, comparee in [
            ("bata", "ang nanay"),
            ("nanay", "ang bata"),
            ("aso", "ang isda"),
        ]:
            f = _comparative_parse(f"Parang {std} {comparee}.")
            assert f is not None, f"failed: Parang {std} {comparee}"
            obj = f.feats.get("OBJ")
            assert isinstance(obj, FStructure)
            assert obj.feats.get("LEMMA") == std

    def test_with_numeral_standard(self) -> None:
        """``Parang isang aso ang bata.`` "The child is like one
        dog." — the numeral ``isang`` precedes the bare N. The
        existing ``isang aso`` form parses as a numeral-modified
        N (not full NP), and the comparative rule absorbs it."""
        f = _comparative_parse("Parang isang aso ang bata.")
        assert f is not None


# === Negation composition =================================================


class TestComparativeWithNegation:

    def test_hindi_parang(self) -> None:
        """``Hindi parang aso ang bata.`` "The child is not like
        a dog." Standard NEG composition with the comparative."""
        f = _comparative_parse("Hindi parang aso ang bata.")
        assert f is not None
        assert f.feats.get("POLARITY") == "NEG"


# === Composition with relativization ======================================


class TestComparativeWithRelativization:

    def test_with_rc_on_subj(self) -> None:
        """``Parang aso ang batang kumain.`` "The child who ate
        is like a dog." The SUBJ NP has an internal RC."""
        f = _comparative_parse("Parang aso ang batang kumain.")
        assert f is not None
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        # The SUBJ has an RC in its ADJ.
        adj = subj.feats.get("ADJ")
        assert adj is not None


# === Tila doesn't fire comparative ========================================


class TestTilaNotComparative:
    """``Tila`` shares CTRL_CLASS=RAISING_BARE with ``parang`` for
    the evidential reading but has no COMPARATIVE feature. The
    constraining equation in the new rule excludes it."""

    def test_tila_with_bare_n_fails(self) -> None:
        """``Tila aso ang bata.`` doesn't fire the comparative rule
        and produces no parse (no other rule shape fits this
        surface)."""
        rs = parse_text("Tila aso ang bata.", n_best=10)
        assert rs == []


# === Existing evidential reading unchanged ================================


class TestEvidentialUnchanged:
    """Phase 5d Commit 1 evidential ``parang + clause`` and
    ``tila + clause`` still parse."""

    def test_parang_clause_evidential(self) -> None:
        """``Parang kumain ang bata.`` "It seems the child ate."
        — evidential reading via the existing Phase 5d Commit 1
        rule, NOT the new comparative rule."""
        rs = parse_text("Parang kumain ang bata.", n_best=10)
        assert rs
        # The PRED should be SEEMS-LIKE (parang's evidential
        # PRED), not LIKE (comparative).
        f = rs[0][1]
        pred = f.feats.get("PRED")
        assert pred is not None and "SEEMS-LIKE" in pred

    def test_tila_clause_evidential(self) -> None:
        """``Tila kumain ang bata.`` — evidential APPARENTLY."""
        rs = parse_text("Tila kumain ang bata.", n_best=10)
        assert rs
        f = rs[0][1]
        pred = f.feats.get("PRED")
        assert pred is not None and "APPARENTLY" in pred


# === LMT diagnostics ======================================================


class TestComparativeLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Parang aso ang bata.",
            "Parang aso si Juan.",
            "Parang nanay ang bata.",
            "Hindi parang aso ang bata.",
            "Parang isang aso ang bata.",
            "Parang aso ang batang kumain.",
        ):
            rs = parse_text(s, n_best=10)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
