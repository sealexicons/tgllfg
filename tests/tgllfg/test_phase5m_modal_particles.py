"""Phase 5m Commit 4: modal / mood particles ``siguro`` / ``marahil``.

Roadmap §12.1 / plan-of-record §5.1. Adds the sentence-initial
sentential-ADV rule in ``cfg/discourse.py``:

    S → PART S
        (↑) = ↓2
        ↓1 ∈ (↑ ADJUNCT)
        (↓1 DISCOURSE_POS) =c 'SENTENCE_INITIAL'

The PART daughter must carry ``DISCOURSE_POS=SENTENCE_INITIAL``,
which is set on Phase 5m lex entries:

* Modal / mood: ``siguro`` (EPISTEMIC=PROBABLY), ``marahil``
  (EPISTEMIC=PROBABLY, REGISTER=FORMAL).
* Discourse connectives (Commits 10, 11): ``samakatuwid``,
  ``gayunpaman``, and the multi-word virtuals ``gayon din`` /
  ``ganon din`` / ``bukod dito``.

The rule projects the inner S's f-structure (PRED, SUBJ, OBJ,
ASPECT, …) to the matrix via ``(↑) = ↓2``; the sentence-initial
PART joins the matrix's ADJUNCT set as a daughter member,
carrying its own marker feat (EPISTEMIC / DISCOURSE). No matrix-
level lift of EPISTEMIC / DISCOURSE — those stay on the ADJUNCT
member because they're inherently adjunct-scoped (contrast with
Phase 5l Rule C / Phase 5m Rule D which lift COUNTERFACTUAL /
REGISTER to matrix because those are clausal-mood properties).

Coverage in this commit covers ``siguro`` and ``marahil`` only;
Commits 10/11 add tests for the discourse-connective uses.

Plan-of-record §9.1 Q2 deferral: clause-medial use
(``Pumupunta siguro siya``) is attested but rare. NOT covered by
this rule (which gates on DISCOURSE_POS=SENTENCE_INITIAL).
Closure path is a polysemous 2P-clitic entry; revisit during
Phase 5n inventory pass.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Siguro sentence-initial ==========================================


SIGURO_CASES = [
    ("Siguro pumupunta siya.", "PUNTA"),
    ("Siguro kumakain ang bata.", "EAT"),
    ("Siguro kakain si Maria.", "EAT"),
]


def _adjunct_with_lemma(fs, lemma: str):
    adj = fs.feats.get("ADJUNCT") or []
    for m in adj:
        if hasattr(m, "feats") and m.feats.get("LEMMA") == lemma:
            return m
    return None


class TestSiguroSentenceInitial:
    """``Siguro`` lifts as a sentence-initial ADJUNCT carrying
    EPISTEMIC=PROBABLY. The matrix S's PRED comes from the inner
    S (not from siguro)."""

    @pytest.mark.parametrize("sent,pred_prefix", SIGURO_CASES)
    def test_siguro_lifts_as_adjunct(
        self, sent: str, pred_prefix: str,
    ) -> None:
        parses = parse_text(sent)
        assert len(parses) >= 1, f"expected ≥1 parse for {sent!r}"
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith(pred_prefix)
        siguro = _adjunct_with_lemma(fs, "siguro")
        assert siguro is not None, (
            f"expected an ADJUNCT member with LEMMA='siguro' for "
            f"{sent!r}; got ADJUNCT={fs.feats.get('ADJUNCT')!r}"
        )
        assert siguro.feats.get("EPISTEMIC") == "PROBABLY"
        assert siguro.feats.get("DISCOURSE_POS") == "SENTENCE_INITIAL"

    def test_matrix_lacks_epistemic_feat(self) -> None:
        """EPISTEMIC stays on the ADJUNCT member; it does NOT lift
        to the matrix S (contrast with COUNTERFACTUAL / REGISTER
        which DO lift)."""
        parses = parse_text("Siguro pumupunta siya.")
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("EPISTEMIC") is None


# === Marahil sentence-initial =========================================


MARAHIL_CASES = [
    ("Marahil pumupunta siya.", "PUNTA"),
    ("Marahil kumakain ang bata.", "EAT"),
]


class TestMarahilSentenceInitial:
    """``Marahil`` carries the same EPISTEMIC=PROBABLY as siguro
    plus REGISTER=FORMAL (formal-register near-synonym)."""

    @pytest.mark.parametrize("sent,pred_prefix", MARAHIL_CASES)
    def test_marahil_lifts_as_adjunct(
        self, sent: str, pred_prefix: str,
    ) -> None:
        parses = parse_text(sent)
        assert len(parses) >= 1, f"expected ≥1 parse for {sent!r}"
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith(pred_prefix)
        marahil = _adjunct_with_lemma(fs, "marahil")
        assert marahil is not None
        assert marahil.feats.get("EPISTEMIC") == "PROBABLY"
        assert marahil.feats.get("REGISTER") == "FORMAL"
        assert marahil.feats.get("DISCOURSE_POS") == "SENTENCE_INITIAL"


# === Composition with negation =========================================


class TestModalParticleWithNegation:
    """Sentence-initial modal particles compose with the existing
    Phase 4 negation grammar — the inner S can include ``hindi``."""

    def test_siguro_hindi_compose(self) -> None:
        """``Siguro hindi kakain ang bata.`` "Maybe the child won't
        eat." — siguro + hindi + V + NP[CASE=NOM]."""
        parses = parse_text("Siguro hindi kakain ang bata.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("POLARITY") == "NEG"
        siguro = _adjunct_with_lemma(fs, "siguro")
        assert siguro is not None

    def test_marahil_hindi_compose(self) -> None:
        parses = parse_text("Marahil hindi kakain ang bata.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("POLARITY") == "NEG"
        marahil = _adjunct_with_lemma(fs, "marahil")
        assert marahil is not None


# === Selectional restriction ==========================================


class TestSelectionalRestriction:
    """The sentence-initial-PART rule constrains on
    ``(↓1 DISCOURSE_POS) =c 'SENTENCE_INITIAL'``, so PARTs without
    that feat (linkers, polarity, 2P clitics) don't form
    sentential-ADV adjuncts. Verifies via known-non-firing PARTs."""

    def test_polarity_part_does_not_fire_as_sentence_initial(
        self,
    ) -> None:
        """``hindi`` is PART[POLARITY=NEG] without DISCOURSE_POS;
        the existing Phase 4 negation rule is what fires on
        ``Hindi kumain ang bata``, NOT the new Phase 5m rule.
        Verified by checking that no ADJUNCT carrying LEMMA=hindi
        appears (Phase 4 negation lifts POLARITY to matrix instead)."""
        parses = parse_text("Hindi kumakain ang bata.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # Negation lifts POLARITY=NEG to matrix.
        assert fs.feats.get("POLARITY") == "NEG"
        # And ``hindi`` is NOT in ADJUNCT — it's the negation head.
        adj = fs.feats.get("ADJUNCT") or []
        for m in adj:
            if hasattr(m, "feats"):
                assert m.feats.get("LEMMA") != "hindi"


# === Single-parse / non-double-fire ===================================


class TestSingleParse:
    """Sentences with sentence-initial siguro / marahil produce
    exactly one parse — no spurious ambiguity from interactions
    with other clause-level rules."""

    def test_siguro_single_parse(self) -> None:
        parses = parse_text("Siguro pumupunta siya.")
        assert len(parses) == 1

    def test_marahil_single_parse(self) -> None:
        parses = parse_text("Marahil kumakain ang bata.")
        assert len(parses) == 1
