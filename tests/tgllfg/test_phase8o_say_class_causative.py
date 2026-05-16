"""Phase 8.O: AV-CAUS-INDIRECT SAY-class reported clause.

Audit-named construction (R&C 1990 Wave 2). The ``magpa-`` /
``nagpa-`` causative form of ``sabi`` "say" carries SAY_CLASS=true
and admits a finite-clause complement introduced by ``na``:

    Nagpasabi si Maria na kumain si Juan.
        "Maria sent word that Juan ate."
    Nagpasabi si Gina na kakain siya ng hapunan dito.
        (R&C 1990 sent-892 with OCR fix siua→siya)
    Nagpasabi si Emmanuel na magdala ka ng mga aklat sa party.
        (R&C 1990 sent-899 with CDs→aklat normalization)

Phase 5n.A Commit 26 closed the OV-SAY reported-clause variant
(``Sinabi niya na pumunta si Maria.`` — OBJ-AGENT GEN-PRON +
``na``-clause as SUBJ). 8.O adds the parallel AV-CAUS-INDIRECT
form with the reported clause bound to OBJ (the TR-class
[AGENT, THEME] mapping in AV puts THEME → OBJ).

New rule in ``cfg/clause.py`` adjacent to the existing OV-SAY
rule:

    S → V[VOICE=AV, CAUS=INDIRECT, SAY_CLASS]
        NP[CASE=NOM]
        PART[LINK=NA]
        S
      (↑ SUBJ) = ↓2
      (↑ OBJ)  = ↓4
      (↓1 SAY_CLASS) =c true
      (↓1 CAUS)      =c 'INDIRECT'
      (↓3 LINK)      =c 'NA'

Lex additions per the OOV-resolve-in-subPR directive:
* ``gina`` / ``emmanuel`` proper-name NOUNs (R&C 1990 corpus)
* ``hapunan`` "dinner" common-noun
* ``boss`` (English loan)
* ``party`` (English loan)
"""

from __future__ import annotations

import pytest


def _has_sabi_with_obj_comp(parses):
    """True iff at least one parse has PRED starting with 'SABI'
    and an OBJ that's a clause (PRED-bearing f-structure)."""
    for _ct, f, _astr, _diags in parses:
        pred = str(f.feats.get("PRED", ""))
        if not pred.startswith("SABI"):
            continue
        obj = f.feats.get("OBJ")
        if obj is None or not hasattr(obj, "feats"):
            continue
        # Reported clause as OBJ has its own PRED
        if obj.feats.get("PRED") is not None:
            return True
    return False


class TestPhase8oNagpasabiBaseShape:
    """Minimal SAY-class causative + na-clause shape parses."""

    @pytest.mark.parametrize("sentence", [
        "Nagpasabi si Maria na kumain si Juan.",
        "Nagpasabi si Juan na umalis si Maria.",
        # IPFV
        "Nagpapasabi si Juan na umalis si Maria.",
        # CTPL
        "Magpapasabi si Juan na uuwi si Maria.",
        # With OBJ in embedded clause
        "Nagpasabi si Maria na bumili siya ng aklat.",
    ])
    def test_nagpasabi_na_clause_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse for {sentence!r}"
        assert _has_sabi_with_obj_comp(parses)


class TestPhase8oFstructureShape:
    """Confirm the f-structure has CAUSER → SUBJ and the reported
    clause → OBJ."""

    def test_subj_and_obj_binding(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Nagpasabi si Maria na kumain si Juan.", n_best=2,
        )
        assert parses
        f = parses[0][1]
        assert str(f.feats.get("PRED")).startswith("SABI")
        subj = f.feats.get("SUBJ")
        assert subj is not None
        assert str(subj.feats.get("LEMMA")) == "maria"
        obj = f.feats.get("OBJ")
        assert obj is not None
        # OBJ is the reported clause — its PRED is the embedded V's
        obj_pred = str(obj.feats.get("PRED", ""))
        assert "EAT" in obj_pred or "KAIN" in obj_pred, (
            f"OBJ.PRED unexpected: {obj_pred!r}"
        )


class TestPhase8oAuditClosures:
    """Direct audit-hit closures (with OCR/acronym normalization
    where needed). Each cites its R&C 1990 source sentence."""

    def test_sent_892_with_ocr_fix(self) -> None:
        """R&C 1990 sent-892 ``Nagpasabi si Gina na kakain siua
        na hapunan dito.`` — verbatim has OCR-bogus ``siua`` for
        ``siya``; the normalized form parses verbatim with the
        new lex adds (gina, hapunan)."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Nagpasabi si Gina na kakain siya ng hapunan dito.", n_best=2,
        )
        assert len(parses) >= 1

    def test_sent_899_with_acronym_swap(self) -> None:
        """R&C 1990 sent-899 ``Nagpasabi si Emmanuel na magdala
        ka ng mga CDs sa party.`` — verbatim has English-acronym
        ``CDs`` which isn't registered (acronyms outside scope).
        The clean form (with `aklat` substituted for `CDs`)
        parses with the new lex adds (emmanuel, party)."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Nagpasabi si Emmanuel na magdala ka ng mga aklat sa party.",
            n_best=2,
        )
        assert len(parses) >= 1


class TestPhase8oLexLoadable:
    """Each new lex add is loadable + indexed correctly."""

    @pytest.mark.parametrize("name", [
        "gina", "emmanuel", "hapunan", "boss", "party",
    ])
    def test_lex_indexed(self, name: str) -> None:
        from tgllfg.morph.analyzer import _get_default
        a = _get_default()
        assert a.is_known_surface(name), f"{name!r} not indexed"


class TestPhase8oOutOfScope:
    """Audit candidates that remain zero-parse — each blocked by
    an orthogonal gap not in 8.O scope. Pin each; flip when the
    named follow-on sub-PR closes it."""

    def test_sent_909_papasok_intr_polysemy(self) -> None:
        """R&C 1990 sent-909 ``Nagpasabi ang boss ko na hindi
        siya papasok sa trabaho.`` — verbatim parses through 8.O's
        new rule but fails on the embedded clause: ``papasok`` is
        morph-classed TR but used semantically intransitive
        ("will enter / will come to work"). Same TR/INTR polysemy
        pattern pinned in Phase 8.I for ``alala``. Lex
        (boss, trabaho) is in place; flip when the
        TR/INTR-polysemy lex-design sub-PR lands."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Nagpasabi ang boss ko na hindi siya papasok sa trabaho.",
            n_best=2,
        )
        assert len(parses) == 0, (
            "pasok INTR polysemy closed — flip if the relevant "
            "lex-design sub-PR landed."
        )

    def test_sent_899_verbatim_cds_acronym(self) -> None:
        """R&C 1990 sent-899 verbatim with ``CDs`` acronym —
        intentionally not registered. English acronyms are
        outside the project's lex-design scope (see Phase 8.A
        / 8.N conventions). Substituted-form parses (see
        ``test_sent_899_with_acronym_swap``)."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Nagpasabi si Emmanuel na magdala ka ng mga CDs sa party.",
            n_best=2,
        )
        assert len(parses) == 0, (
            "CDs registered — but English-acronym registration "
            "is intentionally out of scope."
        )


class TestPhase8oRegressions:
    """Existing parses are unaffected by the new SAY-class
    AV-CAUS-INDIRECT rule + lex adds."""

    @pytest.mark.parametrize("sentence", [
        # Phase 5n.A C26 OV-SAY reported clause
        "Sinabi niya na pumunta si Maria.",
        # Phase 8.F may + V-headed
        "May nakita siya.",
        # Phase 8.H AV-CAUS-INDIRECT flat 3-arg
        "Nagpapakain sila ng kendi sa kanila.",
        # Phase 8.H papakainin
        "Papakainin niya ang manok.",
        # Plain AV transitive
        "Kumain si Juan ng tinapay.",
    ])
    def test_regression_holds(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"regression on {sentence!r}"
