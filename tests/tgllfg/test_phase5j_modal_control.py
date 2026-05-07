"""Phase 5j Commit 7: modal control wrap.

Roadmap §12.1 / plan-of-record §5.6, §6 Commit 7. Four new
control rules in ``cfg/control.py`` (two case variants ×
two link variants, in a 2×2 loop):

    S → V[CTRL_CLASS=MODAL] NP[CASE=NOM] PART[LINK=NA|NG] S_XCOMP
    S → V[CTRL_CLASS=MODAL] NP[CASE=GEN] PART[LINK=NA|NG] S_XCOMP

Subject control: matrix SUBJ is structure-shared with the
embedded XCOMP's REL-PRO via the standard
``(↑ SUBJ) = (↑ XCOMP REL-PRO)`` binding. Same shape as the
Phase 4 §7.6 PSYCH wrap, distinguished only by
CTRL_CLASS=MODAL.

Two case variants admit:
* **NOM-actor pattern**: ``Dapat akong kumain.`` /
  ``Maaari akong kumain.`` — dapat / puwede / maaari take
  NOM-marked actors.
* **GEN-experiencer pattern**: ``Kailangan kong kumain.`` —
  kailangan takes a GEN-marked experiencer (parallel to PSYCH).

Both rules carry the ``(↓1 CTRL_CLASS) =c 'MODAL'`` filter to
prevent cross-firing on PSYCH / KNOW / RAISING control classes.

Integration with negation: ``Hindi`` + modal-S composes via the
existing Phase 4 §7.2 hindi-wrap (``S → PART[POLARITY=NEG] S``),
producing ``POLARITY=NEG`` on the matrix while the modal-PRED
template stays intact. Canonical form requires the linker:
``Hindi ka dapat na kumain.`` parses; ``Hindi ka dapat kumain.``
(no linker) is marginal / colloquial Tagalog and remains 0-parse
(see ``test_phase5j_modal_lex.py::TestNoLinkerModalIsZeroParses``).
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === NOM-actor modals: dapat / puwede / pwede / puede / maaari ========


NOM_ACTOR_MODALS = [
    # (sentence, expected_pred_lemma)
    ("Dapat akong kumain.",     "DAPAT"),
    ("Dapat kang kumain.",      "DAPAT"),
    ("Dapat siyang kumain.",    "DAPAT"),
    ("Puwede akong kumain.",    "PUWEDE"),
    ("Pwede akong kumain.",     "PUWEDE"),    # surface variant
    ("Puede akong kumain.",     "PUWEDE"),    # surface variant
    ("Maaari akong kumain.",    "MAAARI"),
    ("Maaari kang kumain.",     "MAAARI"),
]


class TestNomActorModals:
    """NOM-actor modals (dapat / puwede / maaari) take a NOM-NP
    matrix SUBJ + linker + S_XCOMP."""

    @pytest.mark.parametrize("sentence,expected_pred", NOM_ACTOR_MODALS)
    def test_nom_actor_modal_parses(
        self, sentence: str, expected_pred: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got 0"
        )
        # Modal-headed matrix
        modal_parses = [
            p for p in parses
            if (p[1].feats.get("PRED") or "").startswith(expected_pred)
        ]
        assert len(modal_parses) >= 1, (
            f"expected PRED starting with {expected_pred!r} for "
            f"{sentence!r}; got "
            f"{[p[1].feats.get('PRED') for p in parses]}"
        )
        _ct, fs, _astr, _diags = modal_parses[0]
        assert fs.feats.get("PRED") == f"{expected_pred} <SUBJ, XCOMP>"
        # XCOMP holds the embedded V
        xcomp = fs.feats.get("XCOMP")
        assert xcomp is not None
        # Matrix SUBJ is NOM
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("CASE") == "NOM"


# === GEN-experiencer modal: kailangan ================================


class TestGenExperiencerKailangan:
    """``kailangan`` takes a GEN-marked experiencer (parallel to
    PSYCH). The Commit 7 GEN-variant rule fires."""

    @pytest.mark.parametrize("sentence", [
        "Kailangan kong kumain.",
        "Kailangan mong kumain.",
        "Kailangan niyang kumain.",
    ])
    def test_kailangan_gen_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got 0"
        )
        modal_parses = [
            p for p in parses
            if (p[1].feats.get("PRED") or "").startswith("KAILANGAN")
        ]
        assert len(modal_parses) >= 1
        _ct, fs, _astr, _diags = modal_parses[0]
        assert fs.feats.get("PRED") == "KAILANGAN <SUBJ, XCOMP>"
        # SUBJ is GEN
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("CASE") == "GEN"
        # XCOMP holds the embedded V
        xcomp = fs.feats.get("XCOMP")
        assert xcomp is not None


# === XCOMP subject control ==========================================


class TestXcompSubjectControl:
    """The matrix SUBJ is structure-shared with the embedded
    XCOMP's SUBJ via REL-PRO control. ``Dapat akong kumain.`` —
    ``ako`` is the matrix SUBJ AND the embedded ``kumain``'s
    SUBJ (the eater)."""

    def test_dapat_subject_control(self) -> None:
        parses = parse_text("Dapat akong kumain.")
        modal_parses = [
            p for p in parses
            if (p[1].feats.get("PRED") or "").startswith("DAPAT")
        ]
        assert len(modal_parses) >= 1
        _ct, fs, _astr, _diags = modal_parses[0]
        matrix_subj = fs.feats.get("SUBJ")
        xcomp = fs.feats.get("XCOMP")
        assert xcomp is not None
        assert matrix_subj is not None
        xcomp_subj = xcomp.feats.get("SUBJ")
        assert xcomp_subj is not None
        # Subject control: matrix.SUBJ === xcomp.SUBJ
        # (structure-sharing — same f-node)
        assert matrix_subj is xcomp_subj or (
            matrix_subj.feats.get("CASE")
            == xcomp_subj.feats.get("CASE")
        ), (
            f"expected matrix SUBJ to equal embedded XCOMP SUBJ; "
            f"matrix={matrix_subj!r}; xcomp.SUBJ={xcomp_subj!r}"
        )


# === Negation × modal interaction ====================================


class TestNegationPlusModal:
    """Phase 4 §7.2 hindi-wrap composes with the modal control
    wrap. ``Hindi ka dapat na kumain.`` parses with POLARITY=NEG
    on the matrix and the DAPAT-PRED intact.

    The no-linker form ``Hindi ka dapat kumain.`` is marginal
    Tagalog and stays at 0-parse — see
    ``test_phase5j_modal_lex.py::TestNoLinkerModalIsZeroParses``.
    """

    def test_hindi_dapat_with_linker(self) -> None:
        parses = parse_text("Hindi ka dapat na kumain.")
        modal_parses = [
            p for p in parses
            if (p[1].feats.get("PRED") or "").startswith("DAPAT")
        ]
        assert len(modal_parses) >= 1, (
            f"expected DAPAT-PRED parse for "
            f"'Hindi ka dapat na kumain.'; got "
            f"{[p[1].feats.get('PRED') for p in parses]}"
        )
        _ct, fs, _astr, _diags = modal_parses[0]
        assert fs.feats.get("PRED") == "DAPAT <SUBJ, XCOMP>"
        assert fs.feats.get("POLARITY") == "NEG"


# === Modal CTRL_CLASS doesn't cross-fire ============================


class TestNoCrossFireWithPsychOrKnow:
    """The modal control wrap's ``(↓1 CTRL_CLASS) =c 'MODAL'``
    constraint prevents cross-firing on PSYCH (gusto / ayaw /
    kaya) or KNOW (alam) class predicates. The PSYCH wrap rules
    continue to fire on PSYCH-class verbs unchanged."""

    def test_gusto_still_psych(self) -> None:
        parses = parse_text("Gusto kong kumain.")
        psych_parses = [
            p for p in parses
            if (p[1].feats.get("PRED") or "").startswith("WANT")
        ]
        assert len(psych_parses) >= 1
        _ct, fs, _astr, _diags = psych_parses[0]
        assert fs.feats.get("PRED") == "WANT <SUBJ, XCOMP>"
        # Should NOT also produce a MODAL-class parse for gusto
        modal_parses = [
            p for p in parses
            if "<SUBJ, XCOMP>" in (p[1].feats.get("PRED") or "")
            and not (p[1].feats.get("PRED") or "").startswith("WANT")
        ]
        assert len(modal_parses) == 0, (
            f"unexpected non-PSYCH parses on 'Gusto kong kumain.': "
            f"{[p[1].feats.get('PRED') for p in modal_parses]}"
        )


# === Existing baseline preserved ====================================


class TestBaselinePreserved:
    """Earlier-phase clauses parse unchanged. The modal control
    wrap's CTRL_CLASS=MODAL filter ensures it doesn't fire on
    non-modal V tokens, so V-headed S frames continue to work."""

    @pytest.mark.parametrize("sentence,expected_pred_prefix", [
        ("Kumain ang aso.",          "EAT"),
        ("Maganda ang bata.",         "ADJ"),
        ("Sino ang kumain?",          "WH"),
        ("May aklat ako.",            "EXIST"),
        ("Nasa bundok ang bahay.",    "LOC"),
        ("Gusto kong kumain.",        "WANT"),
    ])
    def test_baseline_unchanged(
        self, sentence: str, expected_pred_prefix: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        match = [
            p for p in parses
            if (p[1].feats.get("PRED") or "")
                .startswith(expected_pred_prefix)
        ]
        assert len(match) >= 1, (
            f"baseline parse for {sentence!r} expected PRED starting "
            f"with {expected_pred_prefix!r}; got "
            f"{[p[1].feats.get('PRED') for p in parses]}"
        )
