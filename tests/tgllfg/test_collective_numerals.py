"""Phase 5f Commit 18: collective numerals (Group H2 item 4).

Adds 4 ``NOUN[MEASURE=YES]`` lex entries (``pares``, ``dosena``,
``daandaan``, ``libulibo``) and 1 new measure-N grammar rule
(``N → N[MEASURE=YES] PART[LINK] N``) for the linker-complement
form of measure phrases (``isang dosenang itlog`` "one dozen
eggs"). The GEN-complement form (``isang pares ng sapatos``
"one pair of shoes") composes via existing rules — Phase 5f
Commit 1 cardinal NP-modifier + Phase 4 §7.8 NP-internal
possessive — without new grammar.

Lex (data/tgl/nouns.yaml):

* ``pares``    — NOUN[MEASURE="YES"]. "pair" (Spanish-borrowed).
* ``dosena``   — NOUN[MEASURE="YES"]. "dozen" (Spanish-borrowed).
* ``daandaan`` — NOUN[MEASURE="YES", COLL_VALUE=HUNDREDS].
                  "hundreds" (canonical orthography
                  ``daan-daan``; single-token form per
                  Phase 5f Commit 14 / 16 hyphenation
                  precedent).
* ``libulibo`` — NOUN[MEASURE="YES", COLL_VALUE=THOUSANDS].
                  "thousands" (canonical orthography
                  ``libu-libo``).

Grammar (src/tgllfg/cfg/grammar.py):

* ``N → N PART[LINK] N`` (2 rule variants for NA / NG linker)
  with constraining equations:
    (↓1 MEASURE) =c 'YES'      # gate to measure NOUNs
    ¬ (↓3 MEASURE)             # block chained measures
  Output is N (preserving PRED + LEMMA from the measured-N
  daughter; MEASURE_HEAD records the measure NOUN's lemma;
  MEASURE='YES' propagates upward). The matrix-NP cardinal-
  modifier rule (Commit 1) consumes the wrapped N unchanged.

Tests cover:

* Morph: each lemma analyses with pos=NOUN and the right
  MEASURE / COLL_VALUE features.
* GEN-complement form (existing rules): ``isang pares ng
  sapatos``, ``isang dosena ng itlog`` — verify a parse path
  with OBJ.LEMMA=pares/dosena, CARDINAL_VALUE=1, and POSS
  containing the measured N.
* LINKER-complement form (new rule): ``isang dosenang itlog``,
  ``isang pares na sapatos``, ``daandaan na aklat``,
  ``libulibong tao`` — verify the parse exists with
  OBJ.LEMMA=measured-N (the linker-form treats the measured
  N as the head of the inner N projection).
* Negative (per §11.2): ``*isang batang aklat`` (bata has no
  MEASURE feature; the linker-form measure-N rule's gate
  fails). ``*isang dosenang dosenang itlog`` (chained measure
  blocked by ``¬ (↓3 MEASURE)``).
* Regression: bare cardinal NP-modifier (Commit 1), ordinal
  (Commit 7), vague Q (Commit 15), comparator (Commit 17),
  approximator (Commit 16) all unchanged. The new measure-N
  rule scopes via MEASURE gating and doesn't disturb non-
  measure NOUNs.
* LMT diagnostics clean.

Out of scope (deferred follow-on commits):

* Hyphenated ``daan-daan`` / ``libu-libo`` orthography —
  needs the same tokenizer pre-pass deferred for Phase 5f
  Commit 14 seasons / Commit 16 ``humigit-kumulang``.
* Productive ``card_redup`` morph class for higher-order
  reduplicated multiples (``milyong-milyon`` "millions",
  ``bilyong-bilyon`` "billions") — per plan §11.1 Group H
  item 4: lex per attested form; productive class deferred.
* MEASURE percolation to the matrix NP — same NP-from-N
  projection limitation as cardinal-modifier features. Tests
  walk down to verify CARDINAL_VALUE + LEMMA composition
  succeeded.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import tokenize


def _measure_nouns() -> list[tuple[str, dict]]:
    """Yield (lemma, expected_extra_feats)."""
    return [
        ("pares",     {}),
        ("dosena",    {}),
        ("daandaan",  {"COLL_VALUE": "HUNDREDS"}),
        ("libulibo",  {"COLL_VALUE": "THOUSANDS"}),
    ]


def _find_obj_with_lemma(text: str, lemma: str) -> FStructure | None:
    """Find any parse where OBJ has the given LEMMA."""
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        obj = f.feats.get("OBJ")
        if isinstance(obj, FStructure) and obj.feats.get("LEMMA") == lemma:
            return obj
    return None


# === Morph layer ==========================================================


class TestCollectiveMorph:

    def test_all_measure_nouns_analyze(self) -> None:
        for lemma, extra_feats in _measure_nouns():
            toks = tokenize(lemma)
            ml = analyze_tokens(toks)
            cands = [c for c in ml[0] if c.pos == "NOUN"]
            assert cands, f"no NOUN analysis for {lemma!r}"
            ma = cands[0]
            assert ma.feats.get("MEASURE") == "YES", (
                f"{lemma}: MEASURE expected 'YES', got "
                f"{ma.feats.get('MEASURE')!r}"
            )
            for k, v in extra_feats.items():
                assert ma.feats.get(k) == v, (
                    f"{lemma}: {k} expected {v!r}, got "
                    f"{ma.feats.get(k)!r}"
                )


# === GEN-complement form (existing rules) =================================


class TestGenComplementForm:
    """``isang pares ng sapatos`` "one pair of shoes" — composes
    via the existing Phase 5f Commit 1 cardinal NP-modifier rule
    (``isang pares`` as NP, head=pares, CV=1) plus the Phase 4
    §7.8 NP-internal possessive rule (``[isang pares] [ng
    sapatos]`` with POSS=sapatos). No new grammar required for
    this form."""

    def test_isang_pares_ng_sapatos(self) -> None:
        # The matrix has OBJ with LEMMA=pares, CV=1, POSS containing
        # sapatos.
        rs = parse_text(
            "Bumili ako ng isang pares ng sapatos.", n_best=10
        )
        assert rs
        found = False
        for _, f, _, _ in rs:
            obj = f.feats.get("OBJ")
            if not isinstance(obj, FStructure):
                continue
            if (obj.feats.get("LEMMA") == "pares"
                    and obj.feats.get("CARDINAL_VALUE") == "1"):
                poss = obj.feats.get("POSS")
                if (isinstance(poss, FStructure)
                        and poss.feats.get("LEMMA") == "sapatos"):
                    found = True
                    break
        assert found, "no GEN-complement parse for pares + sapatos"

    def test_isang_dosena_ng_itlog(self) -> None:
        rs = parse_text(
            "Bumili ako ng isang dosena ng itlog.", n_best=10
        )
        assert rs
        found = False
        for _, f, _, _ in rs:
            obj = f.feats.get("OBJ")
            if not isinstance(obj, FStructure):
                continue
            if (obj.feats.get("LEMMA") == "dosena"
                    and obj.feats.get("CARDINAL_VALUE") == "1"):
                poss = obj.feats.get("POSS")
                if (isinstance(poss, FStructure)
                        and poss.feats.get("LEMMA") == "itlog"):
                    found = True
                    break
        assert found, "no GEN-complement parse for dosena + itlog"


# === LINKER-complement form (new measure-N rule) ==========================


class TestLinkerComplementForm:
    """``isang dosenang itlog`` "one dozen eggs" — uses the new
    measure-N rule (``N → N[MEASURE=YES] PART[LINK] N``). The
    inner ``dosenang itlog`` produces N with LEMMA=itlog (from
    the measured N) and MEASURE_HEAD=dosena. The matrix-NP
    cardinal-modifier rule (Commit 1) consumes the wrapped N
    unchanged."""

    def test_isang_dosenang_itlog(self) -> None:
        # Linker-form: dosenang itlog → N[LEMMA=itlog, MEASURE=YES,
        # MEASURE_HEAD=dosena], then cardinal-modifier wraps with
        # CV=1.
        obj = _find_obj_with_lemma(
            "Bumili ako ng isang dosenang itlog.", "itlog"
        )
        assert obj is not None
        assert obj.feats.get("CARDINAL_VALUE") == "1"

    def test_isang_pares_na_sapatos(self) -> None:
        # Consonant-final pares + na linker.
        obj = _find_obj_with_lemma(
            "Bumili ako ng isang pares na sapatos.", "sapatos"
        )
        assert obj is not None
        assert obj.feats.get("CARDINAL_VALUE") == "1"

    def test_daandaan_na_aklat(self) -> None:
        # Hundreds — daandaan is consonant-final; uses na linker.
        # No outer cardinal (daandaan inherently denotes "many").
        obj = _find_obj_with_lemma(
            "Bumili ako ng daandaan na aklat.", "aklat"
        )
        assert obj is not None

    def test_libulibong_tao(self) -> None:
        # Thousands — libulibo is vowel-final; uses bound -ng.
        obj = _find_obj_with_lemma(
            "Bumili ako ng libulibong tao.", "tao"
        )
        assert obj is not None


# === Negative fixtures (per §11.2) ========================================


class TestCollectiveNegative:

    def test_non_measure_noun_blocked(self) -> None:
        # ``*isang batang aklat`` — bata is a regular NOUN with no
        # MEASURE feature; the new measure-N rule's gate fails.
        rs = parse_text("Bumili ako ng isang batang aklat.", n_best=10)
        assert rs == [], (
            f"non-measure NOUN composed via measure-N rule: "
            f"got {len(rs)} parses"
        )

    def test_chained_measures_blocked(self) -> None:
        # ``*isang dosenang dosenang itlog`` — chained measure
        # NOUNs blocked by ``¬ (↓3 MEASURE)`` constraint on the
        # measure-N rule. The inner ``dosena -ng itlog`` would
        # have MEASURE=YES, which the outer dosena-application
        # rejects.
        rs = parse_text(
            "Bumili ako ng isang dosenang dosenang itlog.", n_best=10
        )
        for _, f, _, _ in rs:
            obj = f.feats.get("OBJ")
            if (isinstance(obj, FStructure)
                    and obj.feats.get("LEMMA") == "itlog"
                    and obj.feats.get("CARDINAL_VALUE") == "1"):
                # If a parse landed with the chained form, that's
                # the regression. Acceptable: zero parses.
                raise AssertionError(
                    "chained measure NOUNs composed despite gate"
                )


# === Regression ===========================================================


class TestCollectiveRegressions:

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

    def test_possessive_alone_unchanged(self) -> None:
        # ``ang aklat ng bata`` "the child's book" — Phase 4 §7.8
        # NP-internal possessive without measure NOUNs.
        rs = parse_text("Bumili ako ng aklat ng bata.", n_best=5)
        assert rs


# === LMT diagnostics clean ================================================


class TestCollectiveLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Bumili ako ng isang pares ng sapatos.",
            "Bumili ako ng isang dosena ng itlog.",
            "Bumili ako ng isang dosenang itlog.",
            "Bumili ako ng isang pares na sapatos.",
            "Bumili ako ng daandaan na aklat.",
            "Bumili ako ng libulibong tao.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
