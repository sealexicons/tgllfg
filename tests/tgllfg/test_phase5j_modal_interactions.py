"""Phase 5j Commit 8: negation × modal interactions + kailangan polysemy.

Roadmap §12.1 / plan-of-record §6 Commit 8. No new grammar rules
— this commit's tests verify that the Phase 4 §7.2 hindi-wrap
composes with the Commit 7 modal control wrap unchanged, and
that the kailangan polysemy (VERB[MODAL] vs NOUN) is correctly
disambiguated by rule context.

Coverage:

* **Negation × modal**: ``Hindi ka dapat na kumain.`` /
  ``Hindi ko kailangang kumain.`` / etc. Negation lifts
  POLARITY=NEG onto the modal-headed matrix; the
  modal-PRED template stays intact.
* **Modal + transitive embedded V**: ``Dapat akong kumain ng
  kanin.`` — the embedded AV-transitive verb composes via
  the existing S_XCOMP shells; the matrix's modal-PRED keeps
  XCOMP holding the transitive PRED.
* **kailangan polysemy**: ``Kailangan kong kumain.`` (VERB[MODAL]
  reading) vs ``Maganda ang kailangan ko.`` (NOUN reading inside
  a NOM-NP). Same surface, two structurally distinct parses;
  rule context disambiguates.

Pre-existing Phase 4 §7.2 hindi-wrap issue (not Phase 5j-
specific): ``Hindi ako/siya kumain.`` (with non-``ka``
NOM-clitic) fails to parse. This affects ``Hindi ako dapat na
kumain.`` and similar by extension. Deferred — see plan §9.2
``Phase 4 hindi-wrap × non-ka NOM-clitic``.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Negation × NOM-actor modals (with ka clitic) ====================


class TestNegationNomActorModal:
    """``Hindi ka <modal> na <V>.`` parses with POLARITY=NEG on the
    matrix and the modal-PRED template intact."""

    @pytest.mark.parametrize("sentence,expected_pred", [
        ("Hindi ka dapat na kumain.",   "DAPAT"),
        ("Hindi ka puwedeng kumain.",   "PUWEDE"),
        ("Hindi ka pwedeng kumain.",    "PUWEDE"),
        ("Hindi ka maaaring kumain.",   "MAAARI"),
    ])
    def test_neg_modal_ka_clitic(
        self, sentence: str, expected_pred: str
    ) -> None:
        parses = parse_text(sentence)
        modal_parses = [
            p for p in parses
            if (p[1].feats.get("PRED") or "").startswith(expected_pred)
        ]
        assert len(modal_parses) >= 1, (
            f"expected {expected_pred}-PRED parse for {sentence!r}; "
            f"got {[p[1].feats.get('PRED') for p in parses]}"
        )
        _ct, fs, _astr, _diags = modal_parses[0]
        assert fs.feats.get("PRED") == f"{expected_pred} <SUBJ, XCOMP>"
        assert fs.feats.get("POLARITY") == "NEG"
        # XCOMP intact
        xcomp = fs.feats.get("XCOMP")
        assert xcomp is not None


# === Negation × GEN-experiencer kailangan ===========================


class TestNegationKailangan:
    """``Hindi <gen-clitic> kailangang <V>.`` — kailangan is the
    one modal that takes GEN-marked experiencer; negation composes
    via the same hindi-wrap."""

    @pytest.mark.parametrize("sentence", [
        "Hindi ko kailangang kumain.",
        "Hindi mo kailangang kumain.",
        # niya without bound -ng (the modal already supplies the
        # linker via kailangang); the bound-niyang form is rejected
        # because of the double-linker placement.
        "Hindi niya kailangang kumain.",
    ])
    def test_neg_kailangan_gen_clitic(self, sentence: str) -> None:
        parses = parse_text(sentence)
        modal_parses = [
            p for p in parses
            if (p[1].feats.get("PRED") or "").startswith("KAILANGAN")
        ]
        assert len(modal_parses) >= 1, (
            f"expected KAILANGAN-PRED parse for {sentence!r}; got "
            f"{[p[1].feats.get('PRED') for p in parses]}"
        )
        _ct, fs, _astr, _diags = modal_parses[0]
        assert fs.feats.get("PRED") == "KAILANGAN <SUBJ, XCOMP>"
        assert fs.feats.get("POLARITY") == "NEG"
        # SUBJ is GEN
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("CASE") == "GEN"


# === Modal + transitive embedded V ===================================


class TestModalTransitiveEmbeddedV:
    """The embedded XCOMP can be a transitive AV verb with its
    own GEN-NP OBJ. The matrix's modal-PRED stays intact; the
    XCOMP carries the transitive PRED + OBJ."""

    @pytest.mark.parametrize("sentence,expected_pred", [
        ("Dapat akong kumain ng kanin.",     "DAPAT"),
        ("Maaari akong kumain ng kanin.",    "MAAARI"),
        ("Kailangan kong kumain ng kanin.",  "KAILANGAN"),
        ("Puwede akong kumain ng kanin.",    "PUWEDE"),
    ])
    def test_modal_transitive_xcomp(
        self, sentence: str, expected_pred: str
    ) -> None:
        parses = parse_text(sentence)
        modal_parses = [
            p for p in parses
            if (p[1].feats.get("PRED") or "").startswith(expected_pred)
        ]
        assert len(modal_parses) >= 1
        _ct, fs, _astr, _diags = modal_parses[0]
        # Matrix: modal PRED
        assert fs.feats.get("PRED") == f"{expected_pred} <SUBJ, XCOMP>"
        # XCOMP: transitive PRED with OBJ
        xcomp = fs.feats.get("XCOMP")
        assert xcomp is not None
        xcomp_pred = xcomp.feats.get("PRED")
        assert "EAT" in (xcomp_pred or "")
        assert "<SUBJ, OBJ>" in (xcomp_pred or ""), (
            f"expected transitive XCOMP PRED for {sentence!r}; "
            f"got {xcomp_pred}"
        )
        xcomp_obj = xcomp.feats.get("OBJ")
        assert xcomp_obj is not None
        assert xcomp_obj.feats.get("LEMMA") == "kanin"


# === kailangan VERB[MODAL] vs NOUN polysemy =========================


class TestKailanganPolysemyDisambiguation:
    """``kailangan`` indexes as both VERB[MODAL=YES, CTRL_CLASS=
    MODAL] and NOUN. Rule context disambiguates: the VERB reading
    drives modal control wraps; the NOUN reading drives ``ang
    kailangan ko`` "what I need" inside an NP."""

    def test_kailangan_modal_reading(self) -> None:
        """``Kailangan kong kumain.`` — VERB[MODAL] reading fires
        the modal control wrap."""
        parses = parse_text("Kailangan kong kumain.")
        modal_parses = [
            p for p in parses
            if (p[1].feats.get("PRED") or "").startswith("KAILANGAN")
        ]
        assert len(modal_parses) >= 1
        _ct, fs, _astr, _diags = modal_parses[0]
        assert fs.feats.get("PRED") == "KAILANGAN <SUBJ, XCOMP>"
        # XCOMP is the embedded V
        xcomp = fs.feats.get("XCOMP")
        assert xcomp is not None

    def test_kailangan_noun_reading_in_subject_np(self) -> None:
        """``Maganda ang kailangan ko.`` — NOUN reading appears
        inside the subject NP (``ang kailangan ko`` "what I
        need"). The matrix is a predicative-ADJ clause (Phase 5g
        Commit 3)."""
        parses = parse_text("Maganda ang kailangan ko.")
        adj_parses = [
            p for p in parses
            if (p[1].feats.get("PRED") or "").startswith("ADJ")
        ]
        assert len(adj_parses) >= 1
        _ct, fs, _astr, _diags = adj_parses[0]
        # Matrix is predicative-adj
        assert fs.feats.get("PRED") == "ADJ <SUBJ>"
        # SUBJ is the NOUN-headed NP with kailangan inside
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "kailangan"
        # NOT a modal-headed parse
        modal_parses = [
            p for p in parses
            if (p[1].feats.get("PRED") or "").startswith("KAILANGAN")
        ]
        assert len(modal_parses) == 0, (
            f"unexpected KAILANGAN-modal parse for "
            f"'Maganda ang kailangan ko.': "
            f"{[p[1].feats.get('PRED') for p in modal_parses]}"
        )


# === Surface-variant uniformity =====================================


class TestSurfaceVariantsProduceUniformPred:
    """The Commit 7 orthographic-variant collapse mechanism
    routes ``puwede`` / ``pwede`` / ``puede`` through the single
    canonical LexicalEntry. All three negation forms produce the
    same PUWEDE PRED template."""

    @pytest.mark.parametrize("sentence", [
        "Hindi ka puwedeng kumain.",
        "Hindi ka pwedeng kumain.",
    ])
    def test_puwede_variants_produce_uniform_pred(
        self, sentence: str
    ) -> None:
        parses = parse_text(sentence)
        modal_parses = [
            p for p in parses
            if (p[1].feats.get("PRED") or "").startswith("PUWEDE")
        ]
        assert len(modal_parses) >= 1
        _ct, fs, _astr, _diags = modal_parses[0]
        assert fs.feats.get("PRED") == "PUWEDE <SUBJ, XCOMP>"
        assert fs.feats.get("POLARITY") == "NEG"


# === Cross-construction baseline =====================================


class TestCrossConstructionBaseline:
    """Earlier-phase non-modal constructions don't acquire modal
    PRED templates from this commit. The ``(↓1 CTRL_CLASS) =c
    'MODAL'`` constraint on the modal control wrap prevents
    PSYCH / KNOW / RAISING predicates from cross-firing."""

    @pytest.mark.parametrize("sentence,expected_pred_prefix", [
        ("Gusto kong kumain.",     "WANT"),       # PSYCH
        ("Alam ko kung sino ang kumain.",  "KNOW"),  # KNOW
        ("Mukhang kumakain ang bata.", "SEEM"),   # RAISING
    ])
    def test_non_modal_predicates_unchanged(
        self, sentence: str, expected_pred_prefix: str
    ) -> None:
        parses = parse_text(sentence)
        match_parses = [
            p for p in parses
            if (p[1].feats.get("PRED") or "")
                .startswith(expected_pred_prefix)
        ]
        assert len(match_parses) >= 1, (
            f"expected {expected_pred_prefix}-PRED parse for "
            f"{sentence!r}; got "
            f"{[p[1].feats.get('PRED') for p in parses]}"
        )
