"""Phase 5f Commit 5: multiplicative ratios.

Two productive forms (S&O 1972 §4.5):

* Native ``maka-`` prefix on cardinals (``makalawa`` "twice",
  ``makatlo`` "thrice", ``makaapat`` "four times") — frequency
  adverbs that attach as clause-level ADJUNCTs.
* Periphrastic ``[CARDINAL]ng beses`` / ``[CARDINAL]ng ulit``
  (``dalawang beses`` "twice", ``tatlong ulit`` "three times")
  — cardinal-modified frequency NOUN.

Plus Spanish-borrowed ``doble`` / ``triple`` — lexical
multipliers for technical / commercial register.

This commit lands:

* Lex (data/tgl/roots.yaml): ``beses``, ``ulit`` (NOUN with
  ``SEM_CLASS=FREQUENCY``); ``doble``, ``triple`` (NOUN with
  ``SEM_CLASS=MULTIPLIER``).
* Lex (data/tgl/particles.yaml): 10 ``maka-`` cardinals
  (``makaisa`` ... ``makasampu``) as ADV with
  ``ADV_TYPE=FREQUENCY`` and ``MULTIPLIER_VALUE``.
* Grammar (src/tgllfg/cfg/grammar.py): one new rule
  ``S → S AdvP`` constraining to ``ADV_TYPE=FREQUENCY``,
  attaching the AdvP to the matrix's ADJUNCT set. Closes part
  of the Phase 5e Commit 3 deferral on bare AdvP placement —
  scoped to FREQUENCY adverbs only.

Tests cover:

* Morph: each ``maka-`` cardinal analyses with pos=ADV,
  ADV_TYPE=FREQUENCY, and the right MULTIPLIER_VALUE.
* Sweep: all 10 ``maka-`` cardinals × intransitive verb in
  clause-final position.
* Composition: ``maka-`` adverb with negation
  (``Hindi kumain ng makalawa`` — wait, this likely doesn't
  make sense; use ``Hindi tumakbo si Juan makalawa``); with
  pivot in different positions.
* ``beses`` / ``ulit`` analyse as NOUN with
  SEM_CLASS=FREQUENCY (lex-only check; full periphrastic
  adverbial use is deferred).
* ``doble`` / ``triple`` analyse as NOUN with SEM_CLASS=MULTIPLIER.
* Negative (per §11.2): ``*Tumakbo ako kahapon`` — the new
  rule is FREQUENCY-only so TIME adverbs (``kahapon``) still
  do NOT compose as bare adjuncts (the Phase 5e Commit 3
  deferral remains in force for non-FREQUENCY adverb types).
* Regression: existing constructions are unaffected.

Out of scope (deferred to follow-on):

* Bare-frequency-N as clause-final ADJUNCT
  (``Tumakbo ako dalawang beses``) — needs SEM_CLASS to
  percolate through the cardinal-NP-modifier rules + a
  ``S → S N`` rule constraining on ``SEM_CLASS=FREQUENCY``
  (parallel to the maka- ADV rule landed here). Currently
  ``dalawang beses`` parses as a cardinal-modified N but
  doesn't attach as a sentential adjunct.
* Topicalized frequency-N (``Dalawang beses akong tumakbo``)
  — depends on the bare-frequency-N rule landing first.
* The narrative idiom ``Nang isang beses, pumunta kami sa
  Maynila`` "Once, we went to Manila" — narrow lexical idiom,
  separate follow-on. Do NOT confuse with a productive
  ``nang + NUM + beses`` rule (which would overgenerate;
  ``*nang dalawang beses`` etc. are unnatural).
* Pre-verbal ``maka-`` with linker (``makalawang nakakain ang
  bata``) — would need ADV-PART-V composition; clause-final
  attachment is the simpler and more common case.
* Bare AdvP attachment for non-FREQUENCY adverb types
  (TIME / SPATIAL / MANNER) — kept deferred per the Phase 5e
  Commit 3 note.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import tokenize


def _maka_cards() -> list[tuple[str, str]]:
    """Yield (surface, multiplier_value)."""
    return [
        ("makaisa",   "1"),
        ("makalawa",  "2"),
        ("makatlo",   "3"),
        ("makaapat",  "4"),
        ("makalima",  "5"),
        ("makaanim",  "6"),
        ("makapito",  "7"),
        ("makawalo",  "8"),
        ("makasiyam", "9"),
        ("makasampu", "10"),
    ]


def _adjuncts(text: str) -> list[FStructure]:
    """Return the ADJUNCT members from the first parse, if any."""
    rs = parse_text(text)
    if not rs:
        return []
    _, f, _, _ = rs[0]
    adj = f.feats.get("ADJUNCT")
    if adj is None:
        return []
    members = list(adj) if isinstance(adj, (set, frozenset, list)) else [adj]
    return [m for m in members if isinstance(m, FStructure)]


# === Morph layer: maka- cardinals =========================================


class TestMakaCardinalMorph:
    """Each maka- cardinal analyses with pos=ADV and the right
    ADV_TYPE / MULTIPLIER_VALUE features."""

    def test_all_maka_cardinals_analyze(self) -> None:
        for lemma, value in _maka_cards():
            toks = tokenize(lemma)
            ml = analyze_tokens(toks)
            cands = ml[0]
            adv_cands = [c for c in cands if c.pos == "ADV"]
            assert adv_cands, f"no ADV analysis for {lemma}"
            ma = adv_cands[0]
            assert ma.feats.get("ADV_TYPE") == "FREQUENCY", (
                f"{lemma}: ADV_TYPE expected 'FREQUENCY', got "
                f"{ma.feats.get('ADV_TYPE')!r}"
            )
            assert ma.feats.get("MULTIPLIER_VALUE") == value, (
                f"{lemma}: MULTIPLIER_VALUE expected {value!r}, got "
                f"{ma.feats.get('MULTIPLIER_VALUE')!r}"
            )


# === Frequency / multiplier nouns =========================================


class TestFrequencyMultiplierNouns:
    """beses / ulit / doble / triple analyse as NOUN with the
    right SEM_CLASS feature."""

    def test_beses_is_frequency_noun(self) -> None:
        toks = tokenize("beses")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "NOUN"]
        assert cands
        assert cands[0].feats.get("SEM_CLASS") == "FREQUENCY"

    def test_ulit_is_frequency_noun(self) -> None:
        toks = tokenize("ulit")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "NOUN"]
        assert cands
        assert cands[0].feats.get("SEM_CLASS") == "FREQUENCY"

    def test_doble_is_multiplier_noun(self) -> None:
        toks = tokenize("doble")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "NOUN"]
        assert cands
        assert cands[0].feats.get("SEM_CLASS") == "MULTIPLIER"

    def test_triple_is_multiplier_noun(self) -> None:
        toks = tokenize("triple")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "NOUN"]
        assert cands
        assert cands[0].feats.get("SEM_CLASS") == "MULTIPLIER"


# === maka- as clause-final ADJUNCT ========================================


class TestMakaAsClauseFinalAdjunct:
    """maka- frequency adverbs attach to the matrix's ADJUNCT set
    via the new ``S → S AdvP[FREQUENCY]`` rule."""

    def test_kumain_ako_makalawa(self) -> None:
        # ``Kumain ako makalawa.`` "I ate twice."
        adjuncts = _adjuncts("Kumain ako makalawa.")
        assert any(
            a.feats.get("ADV_TYPE") == "FREQUENCY"
            and a.feats.get("MULTIPLIER_VALUE") == "2"
            for a in adjuncts
        ), "no FREQUENCY adjunct with MULTIPLIER_VALUE=2"

    def test_tumakbo_siya_makasampu(self) -> None:
        adjuncts = _adjuncts("Tumakbo siya makasampu.")
        assert any(
            a.feats.get("ADV_TYPE") == "FREQUENCY"
            and a.feats.get("MULTIPLIER_VALUE") == "10"
            for a in adjuncts
        )

    def test_kumain_ang_bata_makatlo(self) -> None:
        # Full NOM-NP SUBJ + maka- frequency.
        adjuncts = _adjuncts("Kumain ang bata makatlo.")
        assert any(
            a.feats.get("ADV_TYPE") == "FREQUENCY"
            and a.feats.get("MULTIPLIER_VALUE") == "3"
            for a in adjuncts
        )


# === Sweep all 10 maka- cardinals =========================================


class TestAllMakaCardinalsSweep:
    """Each of the 10 maka- cardinals attaches as ADJUNCT in a
    standard intransitive AV clause."""

    def test_each_maka_in_adjunct(self) -> None:
        for surface, value in _maka_cards():
            text = f"Tumakbo ako {surface}."
            adjuncts = _adjuncts(text)
            assert any(
                a.feats.get("ADV_TYPE") == "FREQUENCY"
                and a.feats.get("MULTIPLIER_VALUE") == value
                for a in adjuncts
            ), f"no FREQUENCY adjunct with MULTIPLIER_VALUE={value} for {text!r}"


# === Composition with negation ============================================


class TestMakaWithNeg:
    """maka- frequency adverb composes with the matrix-NEG rule."""

    def test_hindi_tumakbo_siya_makalawa(self) -> None:
        # ``Hindi tumakbo si Juan makalawa.`` "Juan didn't run twice."
        rs = parse_text("Hindi tumakbo si Juan makalawa.", n_best=10)
        assert rs
        # Find a parse with POLARITY=NEG and a FREQUENCY adjunct.
        found = False
        for _, f, _, _ in rs:
            if f.feats.get("POLARITY") != "NEG":
                continue
            adj = f.feats.get("ADJUNCT")
            if adj is None:
                continue
            members = list(adj) if isinstance(adj, (set, frozenset, list)) else [adj]
            for m in members:
                if (isinstance(m, FStructure)
                        and m.feats.get("ADV_TYPE") == "FREQUENCY"
                        and m.feats.get("MULTIPLIER_VALUE") == "2"):
                    found = True
                    break
            if found:
                break
        assert found, "no NEG + FREQUENCY-adjunct parse"


# === Negative fixtures (per §11.2) ========================================


class TestMakaNegative:

    def test_time_adv_still_doesnt_compose_bare(self) -> None:
        # ``*Tumakbo ako kahapon.`` — the new rule is restricted to
        # ADV_TYPE=FREQUENCY by the constraining equation
        # ``(↓2 ADV_TYPE) =c 'FREQUENCY'``. Time adverbs (kahapon —
        # ADV_TYPE=TIME) still do NOT compose as bare clause-final
        # adjuncts (the Phase 5e Commit 3 deferral on time / spatial /
        # manner adverb placement remains in force).
        rs = parse_text("Tumakbo ako kahapon.", n_best=5)
        # Either no parse, or no parse with kahapon as ADJUNCT.
        for _, f, _, _ in rs:
            adj = f.feats.get("ADJUNCT")
            if adj is None:
                continue
            members = list(adj) if isinstance(adj, (set, frozenset, list)) else [adj]
            for m in members:
                if isinstance(m, FStructure) and m.feats.get("LEMMA") == "kahapon":
                    raise AssertionError(
                        "kahapon (TIME adverb) attached as ADJUNCT — "
                        "FREQUENCY-only restriction failed"
                    )

    def test_two_freq_adverbs_compose(self) -> None:
        # The new rule is recursive (S → S AdvP), so two FREQUENCY
        # AdvPs would in principle stack. This is grammatically odd
        # (saying "twice thrice") but not syntactically blocked.
        # Documented behaviour, not a defect — note here for
        # transparency.
        rs = parse_text("Tumakbo ako makalawa makatlo.", n_best=5)
        # We don't assert a particular outcome — just verify it
        # doesn't crash.
        assert isinstance(rs, list)


# === Regression ===========================================================


class TestMakaRegressions:
    """Existing constructions are unaffected by the new lex / rule."""

    def test_av_intransitive_unchanged(self) -> None:
        rs = parse_text("Tumakbo ako.")
        assert rs
        f = rs[0][1]
        assert f.feats.get("PRED") == "TAKBO <SUBJ>"

    def test_predicative_cardinal_unchanged(self) -> None:
        # ``Tatlo ang anak ko.`` — Phase 5f Commit 4.
        rs = parse_text("Tatlo ang anak ko.", n_best=5)
        assert rs
        assert any(
            f.feats.get("PRED") == "CARDINAL <SUBJ>"
            for _, f, _, _ in rs
        )

    def test_cardinal_np_modifier_unchanged(self) -> None:
        # ``Kumain ako ng tatlong isda.`` — Phase 5f Commit 1.
        rs = parse_text("Kumain ako ng tatlong isda.", n_best=5)
        assert rs
        assert any(
            isinstance(obj := f.feats.get("OBJ"), FStructure)
            and obj.feats.get("CARDINAL_VALUE") == "3"
            for _, f, _, _ in rs
        )


# === LMT diagnostics clean ================================================


class TestMakaLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Kumain ako makalawa.",
            "Tumakbo ako makasampu.",
            "Kumain ang bata makatlo.",
            "Tumakbo siya makaapat.",
            "Hindi tumakbo si Juan makalawa.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
