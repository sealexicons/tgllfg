"""Phase 5k Commit 7: consequence coordination + kaya polysemy.

Roadmap §12.1 / plan-of-record §5.6, §6 Commit 7. Two new
clausal-coord rules (added via the existing
_BINARY_CLAUSAL_COORDS parametrization extended with "SO" plus
its comma-marked variant) + two ``kaya naman`` rules (no-comma
and comma-marked):

    S → S PART[COORD=SO] S
    S → S PUNCT[COMMA] PART[COORD=SO] S
    S → S PART[COORD=SO] PART[ADV=ALSO] S
    S → S PUNCT[COMMA] PART[COORD=SO] PART[ADV=ALSO] S

Plus comma-variants for AND / OR / BUT (added uniformly in this
commit because the comma-marked clausal-coord form
(``Kumain si Maria, at pumunta si Juan.``) is the more common
written form for clausal coordination, and was previously
0-parsed because the new comma lex (Phase 5k Commit 1) requires
structural consumption).

``kaya`` polysemy:
  * Existing PRE-Phase-5k VERB[CTRL_CLASS=PSYCH] reading
    (``Kaya kong kumain.`` "I can eat") — still parses unchanged.
  * NEW PART[COORD=SO] reading (``Pumunta siya, kaya kumain
    ako.`` "He came, so I ate") — fires only when sandwiched
    between two complete S clauses.

The two readings never cross-fire because their rule contexts
are structurally distinct: PSYCH control is V-headed with
GEN-experiencer + linker + XCOMP-V (4-token form
``Kaya <pron>ng V``); coord is S-headed with two complete
S clauses on either side.

``kaya naman`` is a discourse-emphatic variant lifted to the
matrix as DISCOURSE_EMPH=YES.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Plain kaya consequence ==========================================


class TestKayaConsequence:
    """``kaya`` between two clauses yields COORD=SO with two
    conjuncts. Both no-comma and comma-marked forms parse."""

    @pytest.mark.parametrize("sentence", [
        "Pumunta siya kaya kumain ako.",
        "Pumunta siya, kaya kumain ako.",
        "Kumain ako kaya tumakbo si Juan.",
        "Kumain ako, kaya tumakbo si Juan.",
    ])
    def test_kaya_yields_so_coord(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got 0"
        )
        coord_parses = [
            p for p in parses if p[1].feats.get("COORD") == "SO"
        ]
        assert len(coord_parses) >= 1
        _ct, fs, _astr, _diags = coord_parses[0]
        assert fs.feats.get("COORD") == "SO"
        conjuncts = fs.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2

    def test_no_pred_on_so_matrix(self) -> None:
        parses = parse_text("Pumunta siya kaya kumain ako.")
        coord_parses = [
            p for p in parses if p[1].feats.get("COORD") == "SO"
        ]
        _ct, fs, _astr, _diags = coord_parses[0]
        assert fs.feats.get("PRED") is None
        assert fs.feats.get("SUBJ") is None


# === kaya naman two-word variant ====================================


class TestKayaNaman:
    """``kaya naman`` is a discourse-emphatic variant of plain
    ``kaya``. The two-word sequence is a fixed lexicalised form
    (NOT an enclitic-absorbed pattern). The rule lifts
    DISCOURSE_EMPH=YES to the matrix to distinguish from plain
    ``kaya``."""

    @pytest.mark.parametrize("sentence", [
        "Pumunta siya kaya naman kumain ako.",
        "Pumunta siya, kaya naman kumain ako.",
    ])
    def test_kaya_naman_yields_so_with_emph(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        emph_parses = [
            p for p in parses
            if p[1].feats.get("COORD") == "SO"
            and p[1].feats.get("DISCOURSE_EMPH") == "YES"
        ]
        assert len(emph_parses) >= 1, (
            f"expected at least one COORD=SO + DISCOURSE_EMPH=YES "
            f"parse for {sentence!r}; got "
            f"{[(p[1].feats.get('COORD'), p[1].feats.get('DISCOURSE_EMPH')) for p in parses]}"
        )
        _ct, fs, _astr, _diags = emph_parses[0]
        conjuncts = fs.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2

    def test_plain_kaya_does_not_carry_emph(self) -> None:
        """``Pumunta siya kaya kumain ako.`` (plain kaya without
        naman) carries COORD=SO but NOT DISCOURSE_EMPH=YES."""
        parses = parse_text("Pumunta siya kaya kumain ako.")
        coord_parses = [
            p for p in parses if p[1].feats.get("COORD") == "SO"
        ]
        _ct, fs, _astr, _diags = coord_parses[0]
        assert fs.feats.get("DISCOURSE_EMPH") is None


# === kaya polysemy: PSYCH control reading preserved =================


class TestKayaPsychPreserved:
    """The pre-existing Phase 4 §7.6 VERB[CTRL_CLASS=PSYCH]
    ``kaya`` ("be able to") reading still parses unchanged. The
    new PART[COORD=SO] entry doesn't cross-fire on PSYCH-control
    contexts."""

    def test_psych_kaya_still_parses(self) -> None:
        parses = parse_text("Kaya kong kumain.")
        # Should produce the PSYCH-control reading.
        assert len(parses) >= 1
        psych_parses = [
            p for p in parses
            if (p[1].feats.get("PRED") or "").startswith("ABLE")
        ]
        assert len(psych_parses) >= 1
        _ct, fs, _astr, _diags = psych_parses[0]
        # PRED=ABLE <SUBJ, XCOMP>; SUBJ=ko (1sg.GEN-experiencer);
        # XCOMP=kumain
        assert (fs.feats.get("PRED") or "").startswith("ABLE")
        assert fs.feats.get("XCOMP") is not None
        # COORD must NOT be set on the PSYCH reading.
        assert fs.feats.get("COORD") is None

    def test_psych_kaya_with_transitive_xcomp(self) -> None:
        parses = parse_text("Kaya kong kumain ng isda.")
        psych_parses = [
            p for p in parses
            if (p[1].feats.get("PRED") or "").startswith("ABLE")
        ]
        assert len(psych_parses) >= 1


class TestNoCrossFireBetweenReadings:
    """The PSYCH-control reading and the consequence-coord reading
    are structurally distinct contexts; neither admits the other."""

    def test_kaya_no_so_coord_in_psych_context(self) -> None:
        """``Kaya kong kumain.`` (PSYCH form) does NOT produce a
        COORD=SO parse — there are no two S clauses sandwiching
        ``kaya``."""
        parses = parse_text("Kaya kong kumain.")
        for p in parses:
            assert p[1].feats.get("COORD") != "SO", (
                f"unexpected COORD=SO parse for PSYCH form: {p[1].feats}"
            )

    def test_kaya_no_psych_in_coord_context(self) -> None:
        """``Pumunta siya kaya kumain ako.`` (coord form) does NOT
        produce a PRED=ABLE parse — the PSYCH wrap doesn't
        compose across two complete clauses."""
        parses = parse_text("Pumunta siya kaya kumain ako.")
        for p in parses:
            pred = p[1].feats.get("PRED") or ""
            assert not pred.startswith("ABLE"), (
                f"unexpected PSYCH-control reading on coord form: "
                f"{p[1].feats}"
            )


# === Comma-variants for all clausal coords =========================


class TestCommaVariantsAcrossCoords:
    """The comma-marked clausal-coord form is added uniformly for
    all four COORD values in Commit 7. ``Kumain si Maria, at /
    o / pero / kaya pumunta si Juan.`` all parse."""

    @pytest.mark.parametrize("conj,coord_value", [
        ("at",      "AND"),
        ("o",       "OR"),
        ("pero",    "BUT"),
        ("ngunit",  "BUT"),
        ("kaya",    "SO"),
    ])
    def test_comma_form_parses(self, conj: str, coord_value: str) -> None:
        sentence = f"Kumain si Maria, {conj} pumunta si Juan."
        parses = parse_text(sentence)
        coord_parses = [
            p for p in parses if p[1].feats.get("COORD") == coord_value
        ]
        assert len(coord_parses) >= 1, (
            f"expected at least one COORD={coord_value} parse for "
            f"{sentence!r}; got "
            f"{[p[1].feats.get('COORD') for p in parses]}"
        )

    def test_comma_form_c_tree_has_punct(self) -> None:
        """Comma-form has a 4-daughter c-tree at the coord-S
        level: S + PUNCT[COMMA] + PART + S."""
        parses = parse_text("Kumain si Maria, at pumunta si Juan.")
        coord_parses = [
            p for p in parses if p[1].feats.get("COORD") == "AND"
        ]
        ctree, _fs, _astr, _diags = coord_parses[0]
        assert ctree.label == "S"
        assert len(ctree.children) == 4
        assert ctree.children[1].label.startswith("PUNCT")
        assert ctree.children[2].label.startswith("PART")
