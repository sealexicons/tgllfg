"""Phase 5f Commit 8: fractions.

Lex-only addition. Adds half / quarter / part NOUN entries to
``data/tgl/nouns.yaml``:

* ``kalahati`` "half" — native form, SEM_CLASS=FRACTION.
* ``kapat`` "quarter" — native form, SEM_CLASS=FRACTION.
* ``medya`` "half" — Spanish-borrowed; canonical in clock-time
  register (``alas-otso y medya`` "8:30"), bidirectional
  synonym of ``kalahati``.
* ``bahagi`` "part" — head N for the productive ``[ORDINAL]ng
  bahagi`` fraction pattern.

Compositional fractions parse via the existing Phase 5f
Commit 1 cardinal-NP-modifier rules (cardinal + linker + N) and
Commit 7 ordinal-NP-modifier rules (ordinal + linker + N) — no
new grammar required.

Tests cover:

* Morph: each fraction NOUN analyses with the right SEM_CLASS.
* Compositional fractions with cardinals:
  - ``dalawang kalahati`` 2 halves (vowel-final + -ng)
  - ``tatlong kalahati`` 3 halves
  - ``apat na kapat`` 4 quarters (consonant-final + na)
  - ``tatlong kapat`` 3 quarters (3/4)
  - ``isang kalahati`` 1 half (NUM=SG cardinal)
* Compositional with ordinals: ``ikalawang bahagi`` (2nd part),
  ``ikatlong bahagi`` (3rd part = 1/3), ``ikaapat na bahagi``
  (4th part = 1/4).
* Spanish ``medya`` parses as NOUN with FRACTION SEM_CLASS;
  bidirectional synonymy with ``kalahati`` recorded in lex.
* ``bahagi`` parses as PART SEM_CLASS NOUN.
* Negative (per §11.2): ``*Bumili ako ng dalawa kalahati`` (no
  linker between cardinal and fraction noun).
* Regression: cardinals (Commits 1-6) and ordinals (Commit 7)
  unchanged.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import tokenize


def _first_obj(text: str) -> FStructure | None:
    rs = parse_text(text)
    if not rs:
        return None
    _, f, _, _ = rs[0]
    obj = f.feats.get("OBJ")
    return obj if isinstance(obj, FStructure) else None


def _any_obj(text: str, predicate) -> FStructure | None:
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        obj = f.feats.get("OBJ")
        if isinstance(obj, FStructure) and predicate(obj):
            return obj
    return None


# === Morph layer ==========================================================


class TestFractionMorph:
    """Each fraction NOUN analyses with the right SEM_CLASS."""

    def test_kalahati(self) -> None:
        toks = tokenize("kalahati")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "NOUN"]
        assert cands
        assert cands[0].feats.get("SEM_CLASS") == "FRACTION"

    def test_kapat(self) -> None:
        toks = tokenize("kapat")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "NOUN"]
        assert cands
        assert cands[0].feats.get("SEM_CLASS") == "FRACTION"

    def test_medya(self) -> None:
        toks = tokenize("medya")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "NOUN"]
        assert cands
        assert cands[0].feats.get("SEM_CLASS") == "FRACTION"

    def test_bahagi(self) -> None:
        toks = tokenize("bahagi")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "NOUN"]
        assert cands
        assert cands[0].feats.get("SEM_CLASS") == "PART"


# === Compositional fractions with cardinals ===============================


class TestCardinalFractions:
    """``dalawang kalahati`` (2/2), ``apat na kapat`` (4/4),
    ``tatlong kapat`` (3/4) — composes from cardinal-NP-modifier
    + fraction NOUN."""

    def test_dalawang_kalahati(self) -> None:
        # 2 halves — vowel-final cardinal + -ng linker.
        obj = _any_obj(
            "Bumili ako ng dalawang kalahati.",
            lambda o: (o.feats.get("CARDINAL_VALUE") == "2"
                       and o.feats.get("LEMMA") == "kalahati"),
        )
        assert obj is not None

    def test_tatlong_kalahati(self) -> None:
        obj = _any_obj(
            "Bumili ako ng tatlong kalahati.",
            lambda o: (o.feats.get("CARDINAL_VALUE") == "3"
                       and o.feats.get("LEMMA") == "kalahati"),
        )
        assert obj is not None

    def test_apat_na_kapat(self) -> None:
        # 4 quarters (= 4/4 = 1) — consonant-final cardinal + na
        # linker.
        obj = _any_obj(
            "Bumili ako ng apat na kapat.",
            lambda o: (o.feats.get("CARDINAL_VALUE") == "4"
                       and o.feats.get("LEMMA") == "kapat"),
        )
        assert obj is not None

    def test_tatlong_kapat(self) -> None:
        # 3 quarters = 3/4.
        obj = _any_obj(
            "Bumili ako ng tatlong kapat.",
            lambda o: (o.feats.get("CARDINAL_VALUE") == "3"
                       and o.feats.get("LEMMA") == "kapat"),
        )
        assert obj is not None

    def test_isang_kalahati(self) -> None:
        # NUM=SG cardinal + fraction.
        obj = _any_obj(
            "Bumili ako ng isang kalahati.",
            lambda o: (o.feats.get("CARDINAL_VALUE") == "1"
                       and o.feats.get("LEMMA") == "kalahati"),
        )
        assert obj is not None

    def test_anim_na_kapat(self) -> None:
        # 6 quarters — consonant-final cardinal.
        obj = _any_obj(
            "Bumili ako ng anim na kapat.",
            lambda o: (o.feats.get("CARDINAL_VALUE") == "6"
                       and o.feats.get("LEMMA") == "kapat"),
        )
        assert obj is not None


# === Compositional fractions with ordinals ================================


class TestOrdinalFractions:
    """``ikalawang bahagi`` (2nd part = 1/2),
    ``ikatlong bahagi`` (3rd part = 1/3),
    ``ikaapat na bahagi`` (4th part = 1/4) — composes from
    ordinal-NP-modifier + ``bahagi`` PART NOUN."""

    def test_ikalawang_bahagi(self) -> None:
        # 2nd part = 1/2.
        obj = _any_obj(
            "Bumili ako ng ikalawang bahagi.",
            lambda o: (o.feats.get("ORDINAL_VALUE") == "2"
                       and o.feats.get("LEMMA") == "bahagi"),
        )
        assert obj is not None

    def test_ikatlong_bahagi(self) -> None:
        # 3rd part = 1/3 — the canonical fractional form.
        obj = _any_obj(
            "Bumili ako ng ikatlong bahagi.",
            lambda o: (o.feats.get("ORDINAL_VALUE") == "3"
                       and o.feats.get("LEMMA") == "bahagi"),
        )
        assert obj is not None

    def test_ikaapat_na_bahagi(self) -> None:
        # 4th part = 1/4 — consonant-final ordinal + na linker.
        obj = _any_obj(
            "Bumili ako ng ikaapat na bahagi.",
            lambda o: (o.feats.get("ORDINAL_VALUE") == "4"
                       and o.feats.get("LEMMA") == "bahagi"),
        )
        assert obj is not None

    def test_ikalimang_bahagi(self) -> None:
        # 5th part = 1/5.
        obj = _any_obj(
            "Bumili ako ng ikalimang bahagi.",
            lambda o: (o.feats.get("ORDINAL_VALUE") == "5"
                       and o.feats.get("LEMMA") == "bahagi"),
        )
        assert obj is not None


# === Spanish-borrowed medya ===============================================


class TestMedyaSpanish:
    """``medya`` "half" is Spanish-borrowed; canonical in clock-
    time register but also general."""

    def test_dalawang_medya(self) -> None:
        obj = _any_obj(
            "Bumili ako ng dalawang medya.",
            lambda o: (o.feats.get("CARDINAL_VALUE") == "2"
                       and o.feats.get("LEMMA") == "medya"),
        )
        assert obj is not None

    def test_isang_medya(self) -> None:
        obj = _any_obj(
            "Bumili ako ng isang medya.",
            lambda o: (o.feats.get("CARDINAL_VALUE") == "1"
                       and o.feats.get("LEMMA") == "medya"),
        )
        assert obj is not None


# === Negative fixtures (per §11.2) ========================================


class TestFractionNegative:

    def test_no_linker_fails(self) -> None:
        # ``*Bumili ako ng dalawa kalahati.`` — missing linker
        # between cardinal and fraction noun.
        rs = parse_text("Bumili ako ng dalawa kalahati.", n_best=5)
        if rs:
            assert all(
                any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), "ungrammatical *dalawa kalahati produced a non-blocking parse"


# === Regression ===========================================================


class TestFractionRegressions:
    """Existing constructions are unaffected by the new lex."""

    def test_cardinal_unchanged(self) -> None:
        rs = parse_text("Kumain ako ng tatlong isda.", n_best=5)
        assert rs

    def test_ordinal_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng unang aklat.", n_best=5)
        assert rs

    def test_predicative_cardinal_unchanged(self) -> None:
        rs = parse_text("Tatlo ang anak ko.", n_best=5)
        assert any(
            f.feats.get("PRED") == "CARDINAL <SUBJ>"
            for _, f, _, _ in rs
        )


# === LMT diagnostics clean ================================================


class TestFractionLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Bumili ako ng dalawang kalahati.",
            "Bumili ako ng apat na kapat.",
            "Bumili ako ng tatlong kapat.",
            "Bumili ako ng isang kalahati.",
            "Bumili ako ng ikatlong bahagi.",
            "Bumili ako ng ikaapat na bahagi.",
            "Bumili ako ng dalawang medya.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
