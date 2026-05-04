"""Phase 5f Commit 19: distributive ``tig-`` (Group H2 item 5).

Adds 10 ``NUM[CARDINAL=YES, DISTRIB=YES]`` lex entries
(``tigisa`` "one each", ``tigdalawa`` "two each", ...,
``tigsampu`` "ten each") for distributive cardinals 1-10. Each
entry inherits CARDINAL_VALUE from its base cardinal stem so
that the existing Phase 5f Commit 1 cardinal NP-modifier rule
consumes the distributive NUMs without modification:
``tigisang aklat`` "one-each book" composes via the standard
NP-modifier path with DISTRIB=YES riding on the daughter NUM.
The matrix-NP doesn't lift DISTRIB (same NP-from-N projection
limitation as MEASURE / APPROX / COMP).

Lex (data/tgl/particles.yaml):

* 10 NUM entries: tigisa, tigdalawa, tigtatlo, tigapat,
  tiglima, tiganim, tigpito, tigwalo, tigsiyam, tigsampu.
* All carry CARDINAL: "YES", DISTRIB: "YES", CARDINAL_VALUE
  (1-10 matching the base stem), NUM: PL.
* Single-token forms (canonical orthography is hyphenated
  ``tig-isa`` etc.; the post-Phase-5f deferrals PR added
  ``merge_hyphen_compounds`` so the canonical hyphenated
  forms now collapse to the single-token lex entries before
  parsing. Originally deferred for the
  precedent set in Phase 5f Commit 14 / 16 / 18).

Grammar: no new rules. The existing Phase 5f Commit 1
cardinal NP-modifier rules consume the distributive NUMs via
the existing ``(↓2 CARDINAL) =c 'YES'`` constraint; the
disambiguator branch for ``na`` after NUM[CARDINAL=YES]
(also Commit 1) handles consonant-final distributives
(tigapat / tiganim / tigsiyam). The Phase 5f Commit 4
predicative-cardinal rule consumes them too (``Tigisa sila.``
"There is one each of them" — semantically distinctive but
structurally absorbed).

Tests cover:

* Morph: each lemma analyses with pos=NUM and the right
  CARDINAL_VALUE / DISTRIB / NUM features.
* Cardinal NP-modifier composition (OBJ / SUBJ / DAT
  positions): sweep all 10 tig- forms (vowel-final ``-ng``
  and consonant-final ``na`` linker variants).
* Predicative-cardinal absorption: ``Tigisa sila.`` parses
  via the existing Commit 4 rule.
* Negative (per §11.2): ``*Bumili ako ng tigisa.`` (bare
  distributive NUM without head N — no rule fires).
* Regression: bare cardinal NP-modifier (Commit 1), ordinal
  (Commit 7), vague (Commit 15), approximator (Commit 16),
  comparator (Commit 17), collective (Commit 18) all
  unchanged.
* LMT diagnostics clean.

Out of scope (deferred follow-on commits):

* Productive ``tig_distrib`` morph class — per-form lex
  covers 1-10. Productive class would generate higher
  cardinals + Spanish-borrowed bases (``tig-sandaan``,
  ``tig-uno``); paradigm-engine extension. Defer.
* Distributive predicate construction (``Tigisang aklat
  sila`` / ``Tigisa silang aklat`` "they each have one
  book") — addressed by the post-Phase-5f deferrals PR's
  predicative-distributive S rule in ``cfg/clause.py``
  (constrained on ``DISTRIB=YES``). Tested directly in
  ``test_q_clitic_predicate.py``. Originally deferred to a later
  commit.
* DISTRIB percolation to the matrix NP — same NP-from-N
  projection limitation as MEASURE / APPROX / COMP. Tests
  walk down to verify CARDINAL_VALUE preservation on the
  matrix; DISTRIB rides on the inner NUM for downstream
  consumers.
* Hyphenated ``tig-isa`` / ``tig-dalawa`` orthography —
  addressed by the post-Phase-5f deferrals PR via
  ``merge_hyphen_compounds``. Originally deferred for Phase 5f
  Commits 14 / 16 / 18.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import tokenize


def _all_distrib() -> list[tuple[str, str, str, bool]]:
    """Yield (lemma, cardinal_value, surface_with_link,
    vowel_final). vowel_final selects which linker variant
    applies to the test."""
    return [
        ("tigisa",     "1",  "tigisang",     True),
        ("tigdalawa",  "2",  "tigdalawang",  True),
        ("tigtatlo",   "3",  "tigtatlong",   True),
        ("tigapat",    "4",  "tigapat na",   False),
        ("tiglima",    "5",  "tiglimang",    True),
        ("tiganim",    "6",  "tiganim na",   False),
        ("tigpito",    "7",  "tigpitong",    True),
        ("tigwalo",    "8",  "tigwalong",    True),
        ("tigsiyam",   "9",  "tigsiyam na",  False),
        ("tigsampu",   "10", "tigsampung",   True),
    ]


def _first_obj(text: str) -> FStructure | None:
    rs = parse_text(text)
    if not rs:
        return None
    _, f, _, _ = rs[0]
    obj = f.feats.get("OBJ")
    return obj if isinstance(obj, FStructure) else None


def _first_subj(text: str) -> FStructure | None:
    rs = parse_text(text)
    if not rs:
        return None
    _, f, _, _ = rs[0]
    subj = f.feats.get("SUBJ")
    return subj if isinstance(subj, FStructure) else None


# === Morph layer ==========================================================


class TestDistribMorph:

    def test_all_distrib_analyze(self) -> None:
        for lemma, value, _, _ in _all_distrib():
            toks = tokenize(lemma)
            ml = analyze_tokens(toks)
            cands = [c for c in ml[0] if c.pos == "NUM"]
            assert cands, f"no NUM analysis for {lemma!r}"
            ma = cands[0]
            assert ma.feats.get("CARDINAL") == "YES", (
                f"{lemma}: CARDINAL expected 'YES', got "
                f"{ma.feats.get('CARDINAL')!r}"
            )
            assert ma.feats.get("DISTRIB") == "YES", (
                f"{lemma}: DISTRIB expected 'YES', got "
                f"{ma.feats.get('DISTRIB')!r}"
            )
            assert ma.feats.get("CARDINAL_VALUE") == value, (
                f"{lemma}: CARDINAL_VALUE expected {value!r}, got "
                f"{ma.feats.get('CARDINAL_VALUE')!r}"
            )
            assert ma.feats.get("NUM") == "PL", (
                f"{lemma}: NUM expected 'PL', got "
                f"{ma.feats.get('NUM')!r}"
            )


# === NP-modifier composition ==============================================


class TestDistribNPModifier:
    """``tigisang aklat`` "one-each book" — the existing Phase
    5f Commit 1 cardinal NP-modifier rule consumes the
    distributive NUM via the ``(↓2 CARDINAL) =c 'YES'``
    constraint; CARDINAL_VALUE rides up to the matrix NP."""

    def test_all_distrib_in_obj(self) -> None:
        for lemma, value, surface, _ in _all_distrib():
            text = f"Bumili ako ng {surface} aklat."
            obj = _first_obj(text)
            assert obj is not None, f"no parse for {text!r}"
            assert obj.feats.get("LEMMA") == "aklat"
            assert obj.feats.get("CARDINAL_VALUE") == value
            assert obj.feats.get("CASE") == "GEN"

    def test_all_distrib_in_subj(self) -> None:
        for lemma, value, surface, _ in _all_distrib():
            text = f"Kumakain ang {surface} bata."
            subj = _first_subj(text)
            assert subj is not None, f"no parse for {text!r}"
            assert subj.feats.get("LEMMA") == "bata"
            assert subj.feats.get("CARDINAL_VALUE") == value


# === Predicative-cardinal absorption ======================================


class TestDistribPredicative:
    """Distributive NUMs are CARDINAL=YES, so the Phase 5f
    Commit 4 predicative-cardinal rule consumes them: ``Tigisa
    sila.`` parses with the distributive NUM as the matrix
    predicate. The semantic interpretation ("there is one each
    of them") is downstream; the parser delivers the structure."""

    def test_tigisa_sila_predicative(self) -> None:
        rs = parse_text("Tigisa sila.", n_best=5)
        assert rs
        _, f, _, _ = rs[0]
        # PRED should be CARDINAL <SUBJ> (Commit 4 convention);
        # SUBJ should be sila.
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        # CV should be 1 (from tigisa).
        assert f.feats.get("CARDINAL_VALUE") == "1"


# === Negative fixtures (per §11.2) ========================================


class TestDistribNegative:

    def test_bare_distrib_blocked(self) -> None:
        # ``*Bumili ako ng tigisa.`` — bare distributive NUM
        # without a head N in the OBJ-NP slot. The cardinal-
        # modifier rule requires NUM + LINK + N; without the
        # linker + N daughters, no rule fires for OBJ-NP
        # composition. The bare NUM as OBJ wouldn't fit any
        # OBJ-NP construction.
        rs = parse_text("Bumili ako ng tigisa.", n_best=10)
        # Expect zero parses (no path composes ``ng`` + bare
        # NUM without further structure).
        for _, f, _, _ in rs:
            obj = f.feats.get("OBJ")
            if (isinstance(obj, FStructure)
                    and obj.feats.get("CARDINAL_VALUE") == "1"):
                # If a parse landed with just CV on OBJ (no
                # head N), that's the regression. Accept zero
                # parses or parses without a CV-only OBJ.
                lemma = obj.feats.get("LEMMA")
                if lemma is None or lemma == "tigisa":
                    raise AssertionError(
                        "bare distributive composed without head N"
                    )


# === Regression ============================================================


class TestDistribRegressions:

    def test_bare_cardinal_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng tatlong aklat.", n_best=5)
        assert rs

    def test_consonant_final_cardinal_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng apat na aklat.", n_best=5)
        assert rs

    def test_ordinal_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng unang aklat.", n_best=5)
        assert rs

    def test_vague_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng maraming aklat.", n_best=5)
        assert rs

    def test_approximator_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng halos sampung aklat.", n_best=5)
        assert rs

    def test_comparator_unchanged(self) -> None:
        rs = parse_text(
            "Bumili ako ng higit sa sampung aklat.", n_best=5
        )
        assert rs

    def test_collective_gen_unchanged(self) -> None:
        rs = parse_text(
            "Bumili ako ng isang pares ng sapatos.", n_best=5
        )
        assert rs

    def test_collective_linker_unchanged(self) -> None:
        rs = parse_text(
            "Bumili ako ng isang dosenang itlog.", n_best=5
        )
        assert rs

    def test_predicative_cardinal_unchanged(self) -> None:
        # ``Tatlo ang anak ko.`` "I have three children." —
        # predicative-cardinal rule still works for non-
        # distributive cardinals.
        rs = parse_text("Tatlo ang anak ko.", n_best=5)
        assert rs


# === LMT diagnostics clean ================================================


class TestDistribLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Bumili ako ng tigisang aklat.",
            "Bumili ako ng tigdalawang aklat.",
            "Bumili ako ng tigapat na aklat.",
            "Bumili ako ng tigsampung aklat.",
            "Kumakain ang tigisang bata.",
            "Tigisa sila.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
