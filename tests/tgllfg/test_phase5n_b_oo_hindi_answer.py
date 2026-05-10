"""Phase 5n.B Commit 17: standalone Oo. / Hindi. answer clauses
(§18 L97).

Closes §18.1 deferral L97 by adding affirmative / negative
answer-clause PRON entries:

    Oo.      "Yes."         (PRON[INTERJ=YES, ANSWER=AFFIRM])
    Hindi.   "No."          (PRON[INTERJ=YES, ANSWER=NEG])
    Oo po.   "Yes (polite)."
    Hindi po. "No (polite)."
    Oo ho.   "Yes (colloquial-polite)."
    Hindi ho. "No (colloquial-polite)."

Three changes:

* ``data/tgl/pronouns.yaml``: add ``oo`` and ``hindi`` PRON
  entries with ``INTERJ="YES"``, ``ANSWER`` ∈ {AFFIRM, NEG}.
  ``oo`` was previously unlex'd. ``hindi`` keeps its existing
  PART[POLARITY=NEG] entry in ``particles.yaml`` (used by the
  hindi-wrap negation rule); the new PRON entry is parallel,
  not a replacement. Rule context disambiguates the two readings.

* ``cfg/clause.py``: relax the Phase 5m C3 fragment-answer
  rule's ANSWER constraint from ``=c 'AFFIRM'`` to existential
  ``(↑ ANSWER)``, admitting both AFFIRM and NEG answers
  uniformly. CLAUSE_TYPE='FRAGMENT_ANSWER' tags both readings;
  the ANSWER feat itself distinguishes AFFIRM vs NEG for
  downstream consumers.

* ``tests/tgllfg/test_phase5m_politeness_clitic.py``: lift the
  Oo po. / Hindi po. pin from TestFragmentHostDeferredPron
  (the L96 PRON-host path closes here as a side-effect — the
  2P-clitic absorption rule composes on top of the new
  fragment-answer parse).

Disambiguation: ``hindi`` has both PART (negation) and PRON
(answer) entries. The fragment-answer rule fires on a single
PRON with no trailing tokens; hindi-wrap (``S → PART[NEG] S``)
requires an inner S as second daughter. The two paths are
mutually exclusive on token count.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


def _answer_parse(text: str):
    """Return the parse with CLAUSE_TYPE='FRAGMENT_ANSWER', or
    None."""
    parses = parse_text(text, n_best=10)
    for p in parses:
        if p[1].feats.get("CLAUSE_TYPE") == "FRAGMENT_ANSWER":
            return p
    return None


# === Standalone Oo. / Hindi. =========================================


class TestStandaloneAnswers:
    """Bare ``Oo.`` and ``Hindi.`` parse as fragment-answer
    clauses with the appropriate ANSWER feat."""

    @pytest.mark.parametrize("sentence,answer", [
        ("Oo.",     "AFFIRM"),
        ("Hindi.",  "NEG"),
    ])
    def test_standalone_answer(
        self, sentence: str, answer: str
    ) -> None:
        result = _answer_parse(sentence)
        assert result is not None
        _ct, fs, _astr, _diags = result
        assert fs.feats.get("ANSWER") == answer
        assert fs.feats.get("INTERJ") == "YES"
        # No REGISTER on the bare PRONs (only opo / oho carry REGISTER).
        assert fs.feats.get("REGISTER") is None


# === Answer + 2P-politeness clitic ====================================


class TestAnswerWithPoliteClitic:
    """The existing Phase 5m clitic-absorption rule attaches
    po / ho on top of the fragment-answer parse, lifting REGISTER
    to the matrix while preserving ANSWER."""

    @pytest.mark.parametrize("sentence,answer,register", [
        ("Oo po.",     "AFFIRM",  "POLITE"),
        ("Hindi po.",  "NEG",     "POLITE"),
        ("Oo ho.",     "AFFIRM",  "COLLOQUIAL_POLITE"),
        ("Hindi ho.",  "NEG",     "COLLOQUIAL_POLITE"),
    ])
    def test_answer_with_clitic(
        self, sentence: str, answer: str, register: str
    ) -> None:
        result = _answer_parse(sentence)
        assert result is not None
        _ct, fs, _astr, _diags = result
        assert fs.feats.get("ANSWER") == answer
        assert fs.feats.get("REGISTER") == register


# === Existing opo / oho regression ===================================


class TestPhase5mOpoOhoUnchanged:
    """The pre-existing ``opo`` / ``oho`` PRON entries (Phase 5m C3)
    continue to fire — relaxing the AFFIRM constraint to existential
    didn't disturb them."""

    @pytest.mark.parametrize("sentence,register", [
        ("Opo.", "POLITE"),
        ("Oho.", "COLLOQUIAL_POLITE"),
    ])
    def test_opo_oho(self, sentence: str, register: str) -> None:
        result = _answer_parse(sentence)
        assert result is not None
        _ct, fs, _astr, _diags = result
        assert fs.feats.get("ANSWER") == "AFFIRM"
        assert fs.feats.get("REGISTER") == register


# === Hindi-wrap negation regression ==================================


class TestHindiNegationUnchanged:
    """Multi-token sentences with hindi as negation (e.g.,
    ``Hindi kumain ang aso.``) continue to parse via the
    PART-headed hindi-wrap rule. The new PRON entry doesn't
    cross-fire because the fragment-answer rule requires a
    single-PRON matrix with no trailing tokens."""

    @pytest.mark.parametrize("sentence", [
        "Hindi kumain ang aso.",
        "Hindi pumunta si Maria.",
    ])
    def test_hindi_negation(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        # No fragment-answer parse — these are V-headed clauses.
        frag = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "FRAGMENT_ANSWER"
        ]
        assert len(frag) == 0


# === Salamat (C16) regression =======================================


class TestSalamatFragmentUnchanged:
    """The Phase 5n.B C16 NOUN-host fragment path
    (``Salamat po.``) uses CLAUSE_TYPE='FRAGMENT' (no ANSWER)
    and remains distinct from the new C17 PRON-host path
    (CLAUSE_TYPE='FRAGMENT_ANSWER' with ANSWER set)."""

    def test_salamat_po_unchanged(self) -> None:
        parses = parse_text("Salamat po.")
        frag = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "FRAGMENT"
        ]
        assert len(frag) >= 1
        _ct, fs, _astr, _diags = frag[0]
        # No ANSWER on the NOUN-host path.
        assert fs.feats.get("ANSWER") is None
        assert fs.feats.get("REGISTER") == "POLITE"
