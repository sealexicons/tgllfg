"""Phase 8.I: naka- aptative PRED-registration (rule out + lex pass).

Diagnostic outcome: the plan-of-record hypothesis ("naka- aptative
emits PRED 'KITA' and matrix expects KITA<SUBJ,OBJ>; either the lex
emits the wrong PRED stem or the paradigm cell needs a-structure
update") was already closed by Phase 8.F (PR #76) — the
``May nakita siya.`` audit-hit shape parses now via the 8.F
existential + V-headed nominalized complement rule with selective
V-feat capture. The PRED-template completeness failure described in
the audit's diag_summary for sent-12 no longer surfaces.

What 8.I lands instead is a targeted lex pass for the remaining
audit-blocked sentences in the ``nakita`` / ``naalala`` family,
per the OOV-resolve-in-subPR directive:

Lex additions in ``data/tgl/verbs.yaml``:

* ``alala`` — orthographic variant of canonical ``alaala``
  (contemporary 4-syllable spelling; LEMMA pointer keeps the
  canonical form).
* ``alaala`` (existing) — affix_class extended with ``ma`` so
  ``naalala`` (AV-NVOL-PFV) derives.
* ``kitil`` — new VERB root "snatch away / cut off"; affix_class
  ``[in_oblig, um, maka]`` so ``nakakitil`` (AV-ABIL-PFV) and
  ``kinitil`` (OV-PFV) derive.
* ``limot`` (existing) — affix_class extended with ``ma`` so
  ``nalimot`` / ``nalilimot`` / ``malilimot`` (AV-NVOL-) derive;
  ``an_oblig`` also added for parallel LF coverage. (Note: the
  ``ma + LF`` combination form ``malimutan`` requires a paradigm
  cell that doesn't exist yet — pinned as a future paradigm
  sub-PR.)

Lex additions in ``data/tgl/nouns.yaml`` (proper-name +
common-noun OOVs blocking audit-hit closure):

* ``betty`` / ``blas`` / ``flor`` / ``jonathan`` / ``minda`` /
  ``nancy`` — Western proper-name NOUNs
* ``miting`` — common noun (Spanish-loan "meeting")
"""

from __future__ import annotations

import pytest


class TestPhase8iAptativePredAlreadyClosed:
    """The Phase 8.F existential + V-headed nominalized complement
    rule already handles the PRED-template case. Confirm regression."""

    @pytest.mark.parametrize("sentence", [
        "May nakita siya.",          # 8.F closure (was sent-12 audit)
        "May binalak siya.",         # 8.F regression
        "May ginagawa ka ba?",       # 8.F regression
    ])
    def test_may_v_headed_unchanged(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"{sentence!r} should parse (8.F)"


class TestPhase8iAlalaOrthVariant:
    """The new ``alala`` orthographic variant + ``ma`` paradigm
    class on ``alaala`` together close the modern-spelling
    ``naalala`` form."""

    @pytest.mark.parametrize("sentence", [
        # Modern 4-syllable spelling (R&C 1990 corpus)
        "Naalala niya si Maria.",
        "Naalala niya si Nancy.",       # direct R&C audit-context
        # Canonical 5-syllable spelling
        "Naalaala niya si Maria.",
    ])
    def test_naalala_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"{sentence!r} should parse"

    def test_alala_canonical_lemma(self) -> None:
        """``alala`` orthographic variant points at canonical
        ``alaala`` via LEMMA feat; downstream consumers see one
        canonical lemma regardless of spelling."""
        from tgllfg.core.common import Token
        from tgllfg.morph.analyzer import _get_default
        a = _get_default()
        for w in ("naalala", "naalaala"):
            t = Token(surface=w, norm=w, start=0, end=len(w))
            analyses = list(a.analyze_one(t))
            assert analyses, f"{w!r} should be a known verb surface"
            lemmas = {m.lemma for m in analyses if m.pos == "VERB"}
            assert "alaala" in lemmas, (
                f"{w!r} should resolve to canonical lemma 'alaala'; "
                f"got {lemmas!r}"
            )


class TestPhase8iKitilRoot:
    """The new ``kitil`` VERB root supports the AV-ABIL-PFV
    ``nakakitil`` "able to cut off" and OV-PFV ``kinitil``."""

    @pytest.mark.parametrize("sentence", [
        "Nakakitil ng damo si Maria.",        # AV ABIL PFV
        "Kinitil ni Maria ang damo.",         # OV PFV
    ])
    def test_kitil_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"{sentence!r} should parse"


class TestPhase8iAuditClosures:
    """Direct audit-hit closures via the lex pass."""

    def test_ano_ang_nakita_ni_blas(self) -> None:
        """``Ano ang nakita ni Blas?`` (R&C 1990 sent-884
        canonical form; OCR variant ``Bias`` documented in
        TestPhase8iOutOfScope)."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Ano ang nakita ni Blas?", n_best=2)
        assert len(parses) >= 1

    def test_naalala_niya_si_nancy(self) -> None:
        """``Naalala niya si Nancy.`` — R&C 1990 sent-512
        context (the audit sentence has OCR-bogus prefix
        ``Example: Napangtti si Ramon, kasi``; the clean form
        of the second clause parses verbatim with the new
        ``alala`` orth-variant + ``ma`` paradigm + ``nancy``
        proper-name lex)."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Naalala niya si Nancy.", n_best=2)
        assert len(parses) >= 1


class TestPhase8iLexLoadable:
    """Each lex add is loadable + indexed correctly."""

    @pytest.mark.parametrize("name", [
        "betty", "blas", "flor", "jonathan", "minda", "nancy",
    ])
    def test_proper_name_indexed(self, name: str) -> None:
        from tgllfg.morph.analyzer import _get_default
        a = _get_default()
        assert a.is_known_surface(name), (
            f"proper name {name!r} not indexed"
        )

    def test_miting_indexed(self) -> None:
        from tgllfg.morph.analyzer import _get_default
        a = _get_default()
        assert a.is_known_surface("miting")


class TestPhase8iOutOfScope:
    """Audit candidates that remain zero-parse — each blocked by
    an orthogonal construction-class or paradigm-cell gap not in
    8.I scope. Pin each; flip when the named follow-on sub-PR
    closes it."""

    def test_n_appositive_proper_name(self) -> None:
        """``Hindi nakita ni Betty ang kaibigan niyang si Flor.``
        (R&G Intermediate sent-113) — blocked by the NP-internal
        appositive ``si Flor`` after ``kaibigan niya + -ng``.
        That's an NP-appositive construction not currently
        supported. Lex (Betty, Flor) is in place; flip when an
        NP-appositive sub-PR lands."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Hindi nakita ni Betty ang kaibigan niyang si Flor.",
            n_best=2,
        )
        assert len(parses) == 0, (
            "N-appositive proper-name attachment closed — flip "
            "if the relevant sub-PR landed."
        )

    def test_nag_aalala_intransitive_use(self) -> None:
        """``Nag-aalala si Minda.`` (R&C 1990 sent-589 context)
        — semantic-intransitive use of TR-classed ``alala``
        ("worry"). Adding an INTR-polysemy variant or making OBJ
        optional is a lex-design decision out of 8.I scope.
        Flip when the ``alala`` polysemy split / OBJ-optional
        sub-PR lands."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Nag-aalala si Minda.", n_best=2)
        assert len(parses) == 0, (
            "alala INTR polysemy closed — flip if the relevant "
            "sub-PR landed."
        )

    def test_malimutan_lf_nvol_form(self) -> None:
        """``Bago ko malimutan, ...`` (R&C 1990 sent-698) —
        ``malimutan`` is the LF-NVOL form (``ma + limot + an``)
        requiring a ``ma_an`` paradigm cell that doesn't exist
        yet. Analogous to Phase 8.B's ``pag_an`` cell add.
        Flip when the paradigm-cell sub-PR lands."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Bago ko malimutan ito.", n_best=2)
        assert len(parses) == 0, (
            "ma_an LF-NVOL cell closed — flip if the relevant "
            "paradigm sub-PR landed."
        )

    def test_bias_ocr_variant_not_added(self) -> None:
        """``Ano ang nakita ni Bias?`` (R&C 1990 sent-884 raw
        OCR) — ``Bias`` is a known OCR artifact of canonical
        ``Blas`` (only the latter is registered). The canonical
        form parses; the OCR variant is intentionally not
        registered."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Ano ang nakita ni Bias?", n_best=2)
        assert len(parses) == 0, (
            "OCR-variant Bias closed — pin would need to be "
            "lifted if OCR-variant registration was added."
        )


class TestPhase8iRegressions:
    """Existing parses are unaffected by the new lex / paradigm-
    class additions."""

    @pytest.mark.parametrize("sentence", [
        # Pre-8.I nakita parses
        "Nakita ko ang aklat.",
        "Hindi ka nakita ng kaibigan mo.",
        "Nakita ni Maria si Juan.",
        # Phase 4 / 5 baseline
        "Kumain si Juan.",
        "Maganda si Maria.",
    ])
    def test_regression_holds(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"regression on {sentence!r}"
