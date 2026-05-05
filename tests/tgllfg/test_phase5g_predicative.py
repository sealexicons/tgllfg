"""Phase 5g Commit 3: predicative-adj clause rule.

Adds the verbless adj-pred clause rule:

    S → ADJ[PREDICATIVE=YES] NP[CASE=NOM]

The matrix S's PRED is the literal template ``ADJ <SUBJ>`` (parallel
to the predicative-cardinal's ``CARDINAL <SUBJ>`` and parang's
``LIKE <SUBJ, OBJ>``); the adjective's identity is preserved on the
matrix via ``ADJ_LEMMA``. The intrinsic ``PREDICATIVE=YES`` from
the analyzer's ADJ indexer satisfies the rule's category-pattern
constraint and the constraining equation.

These tests cover:

* Each seed adjective parses as predicate, with ang-NP or PRON SUBJ.
* F-structure shape: PRED, SUBJ, ADJ_LEMMA, PREDICATIVE.
* R&G 1981 §12.9 integration-benchmark sentences (4 of 7 simple
  sentences this phase unblocks).
* Composition with the negation rule (``Hindi maganda ang bata``).
* Composition with the aspectual ``na`` ALREADY clitic
  (``Maganda na ang bata`` / ``Matanda na siya``).
* PRON SUBJ via the existing ``NP[CASE=NOM] → PRON[CASE=NOM]``
  projection (``Maganda ka``, ``Matanda siya``).

Out of scope for this commit (deferred): ay-inversion of adj-pred
(``Ang bata ay maganda`` — Phase 4 §7.4 ay-fronting infrastructure
was built for V pivots; extending to ADJ pivots is a separate
commit).
"""

from __future__ import annotations

import pytest

from tgllfg.common import FStructure
from tgllfg.pipeline import parse_text


# === Helpers ==============================================================


def _first_parse(text: str) -> FStructure | None:
    parses = parse_text(text, n_best=1)
    if not parses:
        return None
    return parses[0][1]


# (predicate-surface, expected-adj-lemma, subj-text)
SEED_ADJ_PRED = [
    ("Maganda",  "ganda",  "ang bata"),
    ("Matalino", "talino", "ang bata"),
    ("Matanda",  "tanda",  "siya"),
    ("Maliit",   "liit",   "ang bahay"),
    ("Mataas",   "taas",   "ang bundok"),
    ("Mabilis",  "bilis",  "ako"),
]


# === Core: each seed adj parses as predicate ==============================


class TestSeedPredicates:

    @pytest.mark.parametrize("pred,lemma,subj", SEED_ADJ_PRED)
    def test_parses(self, pred: str, lemma: str, subj: str) -> None:
        text = f"{pred} {subj}."
        f = _first_parse(text)
        assert f is not None, f"no parse for {text!r}"

    @pytest.mark.parametrize("pred,lemma,subj", SEED_ADJ_PRED)
    def test_pred_template(self, pred: str, lemma: str, subj: str) -> None:
        text = f"{pred} {subj}."
        f = _first_parse(text)
        assert f is not None
        assert f.feats.get("PRED") == "ADJ <SUBJ>"

    @pytest.mark.parametrize("pred,lemma,subj", SEED_ADJ_PRED)
    def test_adj_lemma_preserved(self, pred: str, lemma: str, subj: str) -> None:
        text = f"{pred} {subj}."
        f = _first_parse(text)
        assert f is not None
        assert f.feats.get("ADJ_LEMMA") == lemma

    @pytest.mark.parametrize("pred,lemma,subj", SEED_ADJ_PRED)
    def test_predicative_marker(self, pred: str, lemma: str, subj: str) -> None:
        text = f"{pred} {subj}."
        f = _first_parse(text)
        assert f is not None
        assert f.feats.get("PREDICATIVE") == "YES"


# === SUBJ shape: NP vs PRON ==============================================


class TestSubjectShape:
    """The rule accepts both NOM-NP (``NP[CASE=NOM] → DET[CASE=NOM] N``)
    and NOM-PRON (``NP[CASE=NOM] → PRON[CASE=NOM]``) projections via
    the same ``NP[CASE=NOM]`` slot."""

    def test_ang_np_subject(self) -> None:
        f = _first_parse("Maganda ang bata.")
        assert f is not None
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("CASE") == "NOM"
        assert subj.feats.get("MARKER") == "ANG"

    def test_pron_subject_3sg(self) -> None:
        f = _first_parse("Matanda siya.")
        assert f is not None
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("CASE") == "NOM"
        assert subj.feats.get("NUM") == "SG"

    def test_pron_subject_1sg(self) -> None:
        f = _first_parse("Mabilis ako.")
        assert f is not None
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("CASE") == "NOM"
        assert subj.feats.get("NUM") == "SG"

    def test_pron_subject_2sg(self) -> None:
        f = _first_parse("Maganda ka.")
        assert f is not None
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("CASE") == "NOM"
        assert subj.feats.get("NUM") == "SG"


# === R&G 1981 §12.9 integration benchmark ================================


class TestRamosGouletBenchmark:
    """Roadmap §12.9 names ``Matanda siya``, ``Maliit ang bahay``,
    ``Mataas ang bundok`` as Phase-5g-unblocked sentences from the
    R&G 1981 "Ang Manok" essay's seven simples. Phase 5g delivers
    these three; the remaining four require Phase 5j existentials
    (``May`` / ``Nasa``) and Phase 5g manner-adverb (``mag-isa``,
    ``nakatira``) — see §12.9 for the full breakdown."""

    def test_matanda_siya(self) -> None:
        f = _first_parse("Matanda siya.")
        assert f is not None
        assert f.feats.get("ADJ_LEMMA") == "tanda"

    def test_maliit_ang_bahay(self) -> None:
        f = _first_parse("Maliit ang bahay.")
        assert f is not None
        assert f.feats.get("ADJ_LEMMA") == "liit"
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bahay"

    def test_mataas_ang_bundok(self) -> None:
        f = _first_parse("Mataas ang bundok.")
        assert f is not None
        assert f.feats.get("ADJ_LEMMA") == "taas"
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bundok"


# === Composition: negation ===============================================


class TestNegation:
    """The ``S → PART[POLARITY=NEG] S`` rule (Phase 4 §7.3 / Phase 5e
    Commit 25) recursively negates any S, including the new
    predicative-adj S. POLARITY=NEG rides onto the matrix."""

    def test_hindi_maganda_ang_bata(self) -> None:
        f = _first_parse("Hindi maganda ang bata.")
        assert f is not None
        assert f.feats.get("POLARITY") == "NEG"
        assert f.feats.get("PRED") == "ADJ <SUBJ>"
        assert f.feats.get("ADJ_LEMMA") == "ganda"
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"

    def test_hindi_matanda_siya(self) -> None:
        f = _first_parse("Hindi matanda siya.")
        assert f is not None
        assert f.feats.get("POLARITY") == "NEG"
        assert f.feats.get("ADJ_LEMMA") == "tanda"


# === Composition: aspectual ALREADY clitic ===============================


class TestAspectualNa:
    """The 2P aspectual clitic ``na`` (ALREADY) lands in the matrix
    S's ADJ adjunct set via the existing Phase 4 §7.3 clitic
    machinery. The disambiguator's Phase 5g ADJ + ``na`` + (NOUN | ADJ)
    branch fires only when the right-context cues an NP-modifier
    composition; predicative-adj contexts (right context = DET, PRON,
    or clause-end) preserve both readings, and the placement pass
    treats ``na`` as the clitic."""

    def test_maganda_na_ang_bata(self) -> None:
        f = _first_parse("Maganda na ang bata.")
        assert f is not None
        adj = f.feats.get("ADJ")
        assert adj is not None
        # The aspectual `na` rides as a 2P clitic in the matrix's
        # ADJ adjunct set.
        members = list(adj) if isinstance(adj, frozenset) else []
        assert any(
            isinstance(m, FStructure)
            and m.feats.get("ASPECT_PART") == "ALREADY"
            for m in members
        )

    def test_matanda_na_siya(self) -> None:
        f = _first_parse("Matanda na siya.")
        assert f is not None
        adj = f.feats.get("ADJ")
        assert adj is not None
        members = list(adj) if isinstance(adj, frozenset) else []
        assert any(
            isinstance(m, FStructure)
            and m.feats.get("ASPECT_PART") == "ALREADY"
            for m in members
        )


# === Negative: bare ADJ without SUBJ shouldn't form an S =================


class TestNegative:
    """The rule requires both daughters: ADJ alone does not form an S."""

    def test_bare_adj_no_parse(self) -> None:
        # ``Maganda.`` "Beautiful." (no subject — fragment) — should
        # not parse as S. (The orthographic terminator strip in
        # _strip_non_content removes the period.)
        parses = parse_text("Maganda.")
        assert parses == [], (
            f"bare ADJ without SUBJ should not form S; got {len(parses)} parses"
        )
