# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 8.H: AV-CAUS-INDIRECT flat 3-arg matrix wrap.

Diagnostic outcome of the plan-of-record's "papaka- ... -in
paradigm-cell composition gap" hypothesis: the actual audit-hit
blocker is NOT a missing paradigm cell, but a missing **matrix
grammar rule** + **flat-3-arg lex profile** for the
``magpa-``-headed AV causative.

The biclausal-control profile already exists
(``intrinsic: AV_CAUS_INDIRECT`` in
``data/tgl/lexicon/causative.yaml``) for sentences with an
overt embedded V (``Nagpakain ako kumain ng kanin sa kanila.``).
But the audit hit (S&O 1972 page 410 sent-593) uses the
monoclausal flat form:

    Nagpapakain sila ng kendi sa kanila.
        "They are feeding them candy."

with the embedded event's arguments (PATIENT ``ng kendi`` +
CAUSEE ``sa kanila``) surfacing as matrix NP daughters and no
S_XCOMP daughter. The flat form needs:

* A flat-3-arg lex profile that maps PATIENT → OBJ and
  CAUSEE → OBL-CAUSEE (instead of EVENT → XCOMP);
* A matrix grammar rule that consumes the three NP daughters
  in NOM-GEN-DAT order.

This sub-PR delivers both:

* New ``_AV_CAUS_INDIRECT_FLAT`` intrinsic profile in
  ``tgllfg.core.lexicon`` (CAUSER → SUBJ, PATIENT → OBJ via
  the [+o, −r] truth-table cell, CAUSEE → OBL-CAUSEE via the
  [+r, −o] cell).
* New lex entry for ``kain`` in
  ``data/tgl/lexicon/causative.yaml`` with
  ``intrinsic: AV_CAUS_INDIRECT_FLAT`` and PRED
  ``CAUSE-EAT <SUBJ, OBJ, OBL-CAUSEE>``.
* New clause rule in ``cfg/clause.py`` for the audit-shape
  NOM-GEN-DAT ordering.
* ``kendi`` proper-noun lex (Spanish/English loan; OOV resolved
  per the OOV-resolve-in-subPR directive).

The plan-of-record's named ``papakainin niya ang manok.``
target form is NOT in the audit corpus (verified via grep)
and is the prefix-redup variant of the ``pakakainin`` form
(which DOES parse via the existing ``pa_in`` paradigm cell —
Phase 5n.C.4 Commit 16). Pinning that variant as a future
paradigm-cell add (low audit pressure).
"""

import pytest


def _has_av_caus_flat_parse(parses):
    """True iff at least one parse carries PRED ``CAUSE-X <SUBJ,
    OBJ, OBL-CAUSEE>`` with all three GFs populated."""
    for _ct, f, _astr, _diags in parses:
        pred = str(f.feats.get("PRED", ""))
        if "OBL-CAUSEE" not in pred:
            continue
        if (
            f.feats.get("SUBJ") is not None
            and f.feats.get("OBJ") is not None
            and f.feats.get("OBL-CAUSEE") is not None
        ):
            return True
    return False


class TestPhase8hAuditClosure:
    """The S&O 1972 page 410 sent-593 monoclausal-flat shape
    parses (without the ``nang nagpapakain`` reduplication
    idiom, which is a separate construction)."""

    def test_audit_shape_with_kendi(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Nagpapakain sila ng kendi sa kanila.", n_best=3,
        )
        assert len(parses) >= 1
        assert _has_av_caus_flat_parse(parses)

    def test_flat_3arg_with_known_lex(self) -> None:
        """Sanity check the new lex profile + grammar rule with
        a Phase 5 baseline noun (``manok`` for the candy, ``nanay``
        for the recipient)."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Nagpakain ako ng kanin sa nanay.", n_best=3,
        )
        assert len(parses) >= 1


class TestPhase8hPapakaininPrefixRedup:
    """The plan-of-record named target ``papakainin niya ang
    manok.`` closes via a new prefix-redup CTPL OV-CAUS-DIRECT
    paradigm cell. S&O 1972 §10.4 and tagalog.com both attest
    ``papakainin`` and ``pakakainin`` as equivalent CTPL OV
    future-tense forms (GT renders both as "to be fed"). The
    two variants share the same lex profile so they yield the
    same f-structure."""

    @pytest.mark.parametrize("surface", [
        "papakainin",   # prefix-redup variant
        "pakakainin",   # root-redup variant (Phase 5n.C.4 C16)
    ])
    def test_both_ctpl_variants_parse(self, surface: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(f"{surface.capitalize()} niya ang manok.", n_best=3)
        assert len(parses) >= 1, (
            f"{surface!r} should parse as CTPL OV CAUS=DIRECT"
        )

    def test_papakainin_matches_pakakainin_pred(self) -> None:
        """Both CTPL variants share the same lex profile so their
        f-structure PRED is identical."""
        from tgllfg.core.pipeline import parse_text
        p1 = parse_text("Papakainin niya ang manok.", n_best=2)
        p2 = parse_text("Pakakainin niya ang manok.", n_best=2)
        assert p1 and p2
        assert str(p1[0][1].feats.get("PRED")) == str(p2[0][1].feats.get("PRED"))


class TestPhase8hFstructureShape:
    """Confirm the flat-3-arg parse f-structure has CAUSER as
    SUBJ, PATIENT as OBJ, CAUSEE as OBL-CAUSEE."""

    def test_arg_binding(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Nagpapakain sila ng kendi sa kanila.", n_best=3,
        )
        flat = [
            (ct, f, astr, diags)
            for ct, f, astr, diags in parses
            if "OBL-CAUSEE" in str(f.feats.get("PRED", ""))
        ]
        assert flat, "no flat-3-arg parse found"
        _, f, _, _ = flat[0]
        # CAUSER → SUBJ (sila — pronoun 3pl NOM)
        subj = f.feats.get("SUBJ")
        assert subj is not None
        assert str(subj.feats.get("CASE")) == "NOM"
        # PATIENT → OBJ (ng kendi — NOUN GEN)
        obj = f.feats.get("OBJ")
        assert obj is not None
        assert str(obj.feats.get("LEMMA")) == "kendi"
        assert str(obj.feats.get("CASE")) == "GEN"
        # CAUSEE → OBL-CAUSEE (sa kanila — PRON DAT)
        causee = f.feats.get("OBL-CAUSEE")
        assert causee is not None
        assert str(causee.feats.get("CASE")) == "DAT"


class TestPhase8hBiclausalUnchanged:
    """The pre-existing biclausal AV-CAUS-INDIRECT analysis
    (``intrinsic: AV_CAUS_INDIRECT``, PRED ``CAUSE-EAT <SUBJ,
    XCOMP>``) is unaffected — both profiles coexist via the
    LMT most-specific-wins matcher."""

    def test_biclausal_profile_loadable(self) -> None:
        from tgllfg.core.lexicon import _AV_CAUS_INDIRECT
        # Biclausal profile still has EVENT (not the flat
        # PATIENT/CAUSEE pair)
        assert "EVENT" in _AV_CAUS_INDIRECT
        assert "PATIENT" not in _AV_CAUS_INDIRECT

    def test_flat_profile_loadable(self) -> None:
        from tgllfg.core.lexicon import _AV_CAUS_INDIRECT_FLAT
        assert "PATIENT" in _AV_CAUS_INDIRECT_FLAT
        assert "CAUSEE" in _AV_CAUS_INDIRECT_FLAT
        assert "CAUSER" in _AV_CAUS_INDIRECT_FLAT


class TestPhase8hLexLoadable:
    """The new ``kendi`` lex add and the new ``kain`` causative
    flat entry are both loadable + indexed correctly."""

    def test_kendi_indexed(self) -> None:
        from tgllfg.morph.analyzer import _get_default
        a = _get_default()
        assert a.is_known_surface("kendi")


class TestPhase8hOutOfScope:
    """Audit candidates that remain zero-parse — each blocked by
    an orthogonal construction-class or paradigm-cell gap not in
    8.H scope. Pin each; flip when the named follow-on sub-PR
    closes it."""

    def test_nang_v_duplicate_idiom_closed_in_9t(self) -> None:
        """``Nagpapakain sila nang nagpapakain ng kendi sa
        kanila.`` (S&O 1972 page 410 sent-593 verbatim) — the
        ``nang V-DUPLICATE`` "X-ing while X-ing" idiom.

        Phase 9.T.4 closes this via two new S-rules in
        cfg/clause.py: (1) a 1-arg AV-intransitive shape
        (``V[VOICE=AV] PART V[VOICE=AV] NP[CASE=NOM]``) for
        ``Tumawa nang tumawa si Juan.`` etc., and (2) a 3-arg
        AV-CAUS-INDIRECT-FLAT shape matching this pin verbatim.
        The duplicate-V matching is enforced via
        ``(↓X LEMMA) = (↓1 LEMMA)`` and aspect-match equations."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Nagpapakain sila nang nagpapakain ng kendi sa kanila.",
            n_best=2,
        )
        assert len(parses) >= 1, (
            "nang V-DUPLICATE pin should parse post-9.T.4"
        )


    def test_two_arg_av_caus_indirect_closed_in_9t(self) -> None:
        """``Nagpakain siya ng kendi.`` — 2-arg AV-CAUS-INDIRECT
        (CAUSER + PATIENT, no overt CAUSEE).

        Phase 9.T.3 closes this via a new lex profile
        ``_AV_CAUS_INDIRECT_2ARG`` in core/lexicon.py + a
        matching ``kain`` lex entry in causative.yaml + a new
        2-daughter S-rule in cfg/clause.py
        (``V[VOICE=AV, CAUS=INDIRECT] NP[CASE=NOM] NP[CASE=GEN]``).
        The CAUSEE is implicit/recoverable but not syntactically
        realized; PRED template drops the OBL-CAUSEE slot."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Nagpakain siya ng kendi.", n_best=2)
        assert len(parses) >= 1


class TestPhase8hRegressions:
    """Existing parses are unaffected by the new flat profile +
    matrix rule + lex adds."""

    @pytest.mark.parametrize("sentence", [
        # Phase 8.F regression
        "May nakita siya.",
        # Phase 8.I regression
        "Naalala niya si Nancy.",
        # Phase 5n.C.4 C16 OV-CAUS-DIRECT
        "Pinakain niya ang manok.",
        "Pakakainin niya ang manok.",
        # Plain AV transitive
        "Kumain si Juan ng tinapay.",
        # Plain intransitive
        "Kumain si Juan.",
    ])
    def test_regression_holds(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"regression on {sentence!r}"
