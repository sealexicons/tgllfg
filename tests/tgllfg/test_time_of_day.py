"""Phase 5f Commit 11: time-of-day NOUNs + native time deictics
(Group E items 2 + 5).

Lex-only addition. 5 new entries:

* Time-of-day NOUNs (data/tgl/nouns.yaml):
  - ``umaga`` (morning), ``tanghali`` (noon), ``hapon``
    (afternoon). All NOUN with SEM_CLASS=TIME.
* Native time deictics (data/tgl/particles.yaml):
  - ``kanina`` (earlier today), ``kamakalawa`` (day before
    yesterday). Both ADV with ADV_TYPE=TIME, DEIXIS_TIME=PAST.

Time-of-day modifiers compose via the existing Phase 4 §7.8
NP-internal possessive rule: ``alasotso ng umaga`` "8 in the
morning" parses as a clock-time NOUN with the time-of-day
NOUN attached as POSS. Syntactically it's the possessive
construction; semantically it's time-of-day modification.

Time-of-day NOUNs also work as DAT-NP adjuncts directly
(``Pumunta ako sa umaga`` "I went in the morning") via the
existing intransitive ADJUNCT routing.

The native time deictics ``kanina`` / ``kamakalawa`` are added
as ADV (parallel to existing ``kahapon`` / ``ngayon`` /
``bukas`` / ``mamaya``). Bare-AdvP-as-clause-final-ADJUNCT is
currently FREQUENCY-only (Phase 5f Commit 5; the TIME
deferral from Phase 5e Commit 3 stays in force), so these new
deictics work in ay-fronting position but not yet as bare
clause-final adjuncts. Tests verify the morph + ay-fronting
path; bare-clause-final use is a follow-on.

Tests cover:

* Morph: each new entry analyses with the right pos and
  features.
* Time-of-day modifier composition (POSS construction):
  ``alasotso ng umaga``, ``alasotso ng hapon``,
  ``alastres ng tanghali``.
* Time-of-day NOUN as direct DAT adjunct: ``Pumunta ako sa
  umaga``, ``Kumain ako sa hapon``.
* Native time deictics in ay-fronting position:
  ``Kanina ay pumunta ako`` "earlier today I went".
* Negative (per §11.2): ``*Pumunta ako kanina`` (bare
  TIME-AdvP at clause-end is still deferred — should not
  parse with kanina attached as ADJUNCT until the TIME
  deferral lifts).
* Regression: cardinals, ordinals, fractions, arithmetic,
  clock-times all unchanged.
"""

from __future__ import annotations

from tgllfg.core.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.core.pipeline import parse_text
from tgllfg.text import tokenize


def _adjunct_with_lemma(text: str, lemma: str) -> FStructure | None:
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        adj = f.feats.get("ADJUNCT")
        if adj is None:
            continue
        members = (
            list(adj) if isinstance(adj, (set, frozenset, list)) else [adj]
        )
        for m in members:
            if isinstance(m, FStructure) and m.feats.get("LEMMA") == lemma:
                return m
    return None


# === Morph layer ==========================================================


class TestTimeOfDayMorph:

    def test_umaga(self) -> None:
        toks = tokenize("umaga")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "NOUN"]
        assert cands
        assert cands[0].feats.get("SEM_CLASS") == "TIME"

    def test_tanghali(self) -> None:
        toks = tokenize("tanghali")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "NOUN"]
        assert cands
        assert cands[0].feats.get("SEM_CLASS") == "TIME"

    def test_hapon(self) -> None:
        toks = tokenize("hapon")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "NOUN"]
        assert cands
        assert cands[0].feats.get("SEM_CLASS") == "TIME"

    def test_kanina_adv(self) -> None:
        toks = tokenize("kanina")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "ADV"]
        assert cands
        assert cands[0].feats.get("ADV_TYPE") == "TIME"
        assert cands[0].feats.get("DEIXIS_TIME") == "PAST"

    def test_kamakalawa_adv(self) -> None:
        toks = tokenize("kamakalawa")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "ADV"]
        assert cands
        assert cands[0].feats.get("ADV_TYPE") == "TIME"
        assert cands[0].feats.get("DEIXIS_TIME") == "PAST"


# === Time-of-day modifier (POSS construction) =============================


class TestTimeOfDayModifier:
    """``alasotso ng umaga`` "8 in the morning" parses as a
    clock-time NOUN with the time-of-day NOUN as POSS via the
    Phase 4 §7.8 NP-internal possessive rule. Syntactically it's
    the possessive construction; semantically it's time-of-day
    modification."""

    def test_alasotso_ng_umaga(self) -> None:
        adj = _adjunct_with_lemma(
            "Pumunta ako sa alasotso ng umaga.", "alasotso"
        )
        assert adj is not None, "no DAT adjunct"
        poss = adj.feats.get("POSS")
        assert isinstance(poss, FStructure)
        assert poss.feats.get("LEMMA") == "umaga"

    def test_alasotso_ng_hapon(self) -> None:
        adj = _adjunct_with_lemma(
            "Pumunta ako sa alasotso ng hapon.", "alasotso"
        )
        assert adj is not None
        poss = adj.feats.get("POSS")
        assert isinstance(poss, FStructure)
        assert poss.feats.get("LEMMA") == "hapon"

    def test_alastres_ng_tanghali(self) -> None:
        adj = _adjunct_with_lemma(
            "Pumunta ako sa alastres ng tanghali.", "alastres"
        )
        assert adj is not None
        poss = adj.feats.get("POSS")
        assert isinstance(poss, FStructure)
        assert poss.feats.get("LEMMA") == "tanghali"

    def test_alasdose_ng_gabi(self) -> None:
        # gabi (night) is an existing NOUN entry without
        # SEM_CLASS=TIME, but the syntactic POSS construction
        # still composes — gabi is a valid GEN-NP head.
        adj = _adjunct_with_lemma(
            "Pumunta ako sa alasdose ng gabi.", "alasdose"
        )
        assert adj is not None
        poss = adj.feats.get("POSS")
        assert isinstance(poss, FStructure)
        assert poss.feats.get("LEMMA") == "gabi"


# === Time-of-day NOUN as DAT adjunct ======================================


class TestTimeOfDayAsDatAdjunct:

    def test_pumunta_sa_umaga(self) -> None:
        adj = _adjunct_with_lemma("Pumunta ako sa umaga.", "umaga")
        assert adj is not None
        assert adj.feats.get("CASE") == "DAT"

    def test_kumain_sa_hapon(self) -> None:
        adj = _adjunct_with_lemma("Kumain ako sa hapon.", "hapon")
        assert adj is not None
        assert adj.feats.get("CASE") == "DAT"

    def test_pumunta_sa_tanghali(self) -> None:
        adj = _adjunct_with_lemma("Pumunta ako sa tanghali.", "tanghali")
        assert adj is not None
        assert adj.feats.get("CASE") == "DAT"


# === Native time deictics in ay-fronting position =========================


class TestTimeDeicticsAyFronting:
    """The Phase 5e Commit 3 ay-fronting wrap rule
    (``S → AdvP PART[LINK=AY] S``) accepts AdvPs of any type.
    The Phase 5f Commit 5 bare-AdvP-as-clause-final-ADJUNCT
    rule is FREQUENCY-only. So the new TIME deictics
    (``kanina``, ``kamakalawa``) work in ay-fronting position
    but not as bare clause-final adjuncts (yet)."""

    def test_kanina_ay_pumunta(self) -> None:
        # ``Kanina ay pumunta ako.`` "Earlier today I went."
        rs = parse_text("Kanina ay pumunta ako.", n_best=10)
        assert rs, "no parse"
        # The matrix should have kanina as a TOPIC / ADJ member.
        found = False
        for _, f, _, _ in rs:
            topic = f.feats.get("TOPIC")
            if isinstance(topic, FStructure) and topic.feats.get("LEMMA") == "kanina":
                found = True
                break
        assert found, "no ay-fronting parse with kanina as TOPIC"

    def test_kamakalawa_ay_kumain(self) -> None:
        rs = parse_text("Kamakalawa ay kumain ako.", n_best=10)
        assert rs
        found = False
        for _, f, _, _ in rs:
            topic = f.feats.get("TOPIC")
            if isinstance(topic, FStructure) and topic.feats.get("LEMMA") == "kamakalawa":
                found = True
                break
        assert found, "no ay-fronting parse with kamakalawa as TOPIC"


# === Negative fixtures (per §11.2) ========================================


class TestTimeOfDayNegative:

    def test_bare_kanina_clause_final_doesnt_attach(self) -> None:
        # ``Pumunta ako kanina.`` — bare TIME AdvP at clause-end.
        # The Phase 5f Commit 5 sentential-AdvP rule is restricted
        # to ADV_TYPE=FREQUENCY only; the TIME deferral from
        # Phase 5e Commit 3 stays in force. So kanina should NOT
        # attach as a clause-final ADJUNCT until the deferral
        # lifts.
        rs = parse_text("Pumunta ako kanina.", n_best=10)
        for _, f, _, _ in rs:
            adj = f.feats.get("ADJUNCT")
            if adj is None:
                continue
            members = (
                list(adj) if isinstance(adj, (set, frozenset, list)) else [adj]
            )
            for m in members:
                if isinstance(m, FStructure) and m.feats.get("LEMMA") == "kanina":
                    raise AssertionError(
                        "kanina attached as clause-final ADJUNCT — "
                        "TIME deferral from Phase 5e Commit 3 should "
                        "still be in force"
                    )


# === Regression ===========================================================


class TestTimeOfDayRegressions:

    def test_clock_time_alone_unchanged(self) -> None:
        rs = parse_text("Pumunta ako sa alasotso.", n_best=5)
        assert rs

    def test_cardinal_unchanged(self) -> None:
        rs = parse_text("Kumain ako ng tatlong isda.", n_best=5)
        assert rs

    def test_arithmetic_unchanged(self) -> None:
        rs = parse_text("Dalawa dagdag tatlo ay lima.", n_best=5)
        assert any(
            f.feats.get("PRED") == "ARITHMETIC"
            for _, f, _, _ in rs
        )

    def test_kahapon_ay_fronting_unchanged(self) -> None:
        # Existing TIME deictic kahapon should still work in
        # ay-fronting position (Phase 5e Commit 3).
        rs = parse_text("Kahapon ay pumunta ako.", n_best=5)
        assert rs


# === LMT diagnostics clean ================================================


class TestTimeOfDayLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Pumunta ako sa alasotso ng umaga.",
            "Pumunta ako sa alasotso ng hapon.",
            "Pumunta ako sa alastres ng tanghali.",
            "Pumunta ako sa umaga.",
            "Kumain ako sa hapon.",
            "Kanina ay pumunta ako.",
            "Kamakalawa ay kumain ako.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
