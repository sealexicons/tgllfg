"""Phase 5b — embedded-clause LMT validation.

The :func:`tgllfg.lmt.apply_lmt_with_check` wrapper now recursively
runs :func:`tgllfg.lmt.lmt_check` on every embedded f-structure in
``XCOMP`` / ``COMP`` slots that has its own ``PRED``, in addition
to the matrix. Embedded-clause diagnostics carry the f-structure
path so the user can see where they came from.

This was an "Open issues" item in :file:`docs/lmt.md` after Phase 5;
Phase 5b lifts it.
"""

from __future__ import annotations

from typing import Any

from tgllfg.common import AStructure, FStructure, LexicalEntry
from tgllfg.fstruct import Diagnostic
from tgllfg.lmt.check import (
    _retag_diagnostics,
    _walk_xcomp_subs,
    apply_lmt_with_check,
)
from tgllfg.pipeline import parse_text


def _first(text: str) -> tuple[Any, FStructure, AStructure, list[Diagnostic]]:
    results = parse_text(text)
    assert results, f"no parse for {text!r}"
    return results[0]


# === End-to-end: control verbs walk into XCOMP ===========================


class TestControlVerbsXcompWalk:
    """Real parses of control / causative sentences. The recursive
    embedded-clause check runs on each XCOMP without firing
    spurious diagnostics — engine and grammar agree at every
    embedded level after the Phase 5b OBJ-θ-in-grammar
    alignment."""

    def test_psych_control_xcomp_clean(self) -> None:
        # "Gusto kong kumain" — matrix WANT <SUBJ, XCOMP>, embedded
        # EAT <SUBJ>. Both layers should validate without
        # diagnostics.
        _, _f, _, diags = _first("Gusto kong kumain.")
        assert not any(d.is_blocking() for d in diags)
        assert not any(d.kind == "lmt-mismatch" for d in diags)

    def test_intransitive_control_xcomp_clean(self) -> None:
        _, _f, _, diags = _first("Pumayag siyang kumain.")
        assert not any(d.is_blocking() for d in diags)
        assert not any(d.kind == "lmt-mismatch" for d in diags)

    def test_intransitive_control_with_transitive_xcomp(self) -> None:
        # "Pumayag siyang kumain ng isda" — embedded EAT <SUBJ, OBJ>.
        # The XCOMP's OBJ slot should validate too.
        _, f, _, diags = _first("Pumayag siyang kumain ng isda.")
        assert not any(d.is_blocking() for d in diags)
        # Confirm the XCOMP shape is what we're checking.
        xc = f.feats.get("XCOMP")
        assert isinstance(xc, FStructure)
        assert xc.feats.get("PRED") == "EAT <SUBJ, OBJ>"

    def test_transitive_control_xcomp_clean(self) -> None:
        # "Pinilit ng nanay ang batang kumain ng isda" — matrix
        # FORCE <SUBJ, OBJ-AGENT, XCOMP>, embedded EAT <SUBJ, OBJ>.
        _, _f, _, diags = _first("Pinilit ng nanay ang batang kumain ng isda.")
        assert not any(d.is_blocking() for d in diags)
        assert not any(d.kind == "lmt-mismatch" for d in diags)

    def test_indirect_causative_xcomp_clean(self) -> None:
        _, _f, _, diags = _first("Nagpakain ang nanay na kumain.")
        assert not any(d.is_blocking() for d in diags)
        assert not any(d.kind == "lmt-mismatch" for d in diags)


# === Walk helper =========================================================


class TestWalkXcompSubs:
    """Unit tests for :func:`_walk_xcomp_subs`."""

    def test_no_xcomp_yields_nothing(self) -> None:
        f = FStructure(feats={"PRED": "EAT <SUBJ, OBJ>"}, id=1)
        assert list(_walk_xcomp_subs(f, set())) == []

    def test_single_xcomp_yielded(self) -> None:
        sub = FStructure(feats={"PRED": "EAT <SUBJ>"}, id=2)
        f = FStructure(feats={"PRED": "WANT <SUBJ, XCOMP>", "XCOMP": sub}, id=1)
        results = list(_walk_xcomp_subs(f, set()))
        assert len(results) == 1
        sub_f, path = results[0]
        assert sub_f is sub
        assert path == ("XCOMP",)

    def test_xcomp_without_pred_skipped(self) -> None:
        # An XCOMP value that doesn't have its own PRED (e.g., a
        # placeholder structure) is skipped — there's nothing to
        # check against an embedded lex entry.
        sub = FStructure(feats={"VOICE": "AV"}, id=2)
        f = FStructure(feats={"PRED": "WANT", "XCOMP": sub}, id=1)
        assert list(_walk_xcomp_subs(f, set())) == []

    def test_nested_xcomp_yielded_in_order(self) -> None:
        # matrix → XCOMP → XCOMP. Both nested levels should yield.
        inner = FStructure(feats={"PRED": "RUN <SUBJ>"}, id=3)
        middle = FStructure(
            feats={"PRED": "AGREE <SUBJ, XCOMP>", "XCOMP": inner}, id=2
        )
        f = FStructure(
            feats={"PRED": "WANT <SUBJ, XCOMP>", "XCOMP": middle}, id=1
        )
        results = list(_walk_xcomp_subs(f, set()))
        assert len(results) == 2
        assert results[0] == (middle, ("XCOMP",))
        assert results[1] == (inner, ("XCOMP", "XCOMP"))

    def test_seen_dedup_prevents_revisit(self) -> None:
        # Reentrant XCOMP (e.g., control SUBJ-sharing) — same node
        # should not be yielded twice.
        shared = FStructure(feats={"PRED": "EAT <SUBJ>"}, id=2)
        f = FStructure(
            feats={
                "PRED": "WANT <SUBJ, XCOMP>",
                "XCOMP": shared,
                "COMP": shared,
            },
            id=1,
        )
        results = list(_walk_xcomp_subs(f, set()))
        # Only the first key encountered yields; the second sees
        # the id in `seen` and skips.
        assert len(results) == 1


# === Diagnostic retagging ================================================


class TestRetagDiagnostics:

    def test_path_prefixed_to_message_and_path_field(self) -> None:
        d = Diagnostic(kind="lmt-mismatch", message="example diag")
        retagged = _retag_diagnostics([d], ("XCOMP",))
        assert len(retagged) == 1
        rd = retagged[0]
        assert rd.path == ("XCOMP",)
        assert rd.message.startswith("[XCOMP]")
        assert "example diag" in rd.message
        # Other fields preserved.
        assert rd.kind == d.kind

    def test_nested_path_prefixed(self) -> None:
        d = Diagnostic(kind="lmt-mismatch", message="example", path=("OBJ",))
        retagged = _retag_diagnostics([d], ("XCOMP", "XCOMP"))
        rd = retagged[0]
        # Path concatenated.
        assert rd.path == ("XCOMP", "XCOMP", "OBJ")
        assert rd.message.startswith("[XCOMP.XCOMP]")


# === Synthetic embedded mismatch surfaces with path tag ==================


class TestSyntheticEmbeddedMismatch:
    """Construct a matrix f-structure whose XCOMP has a PRED that
    matches a synthetic lex entry whose intrinsic profile produces
    a different governable-GF set than the XCOMP's actual feats.
    The recursive check should surface an ``lmt-mismatch`` tagged
    with the ``XCOMP`` path."""

    def test_xcomp_mismatch_carries_xcomp_path(self) -> None:
        # Matrix lex: psych control with EXPERIENCER + COMPLEMENT.
        matrix_le = LexicalEntry(
            lemma="zzz",
            pred="ZZZ <SUBJ, XCOMP>",
            a_structure=["EXPERIENCER", "COMPLEMENT"],
            morph_constraints={"VOICE": "AV"},
            gf_defaults={"EXPERIENCER": "SUBJ", "COMPLEMENT": "XCOMP"},
            intrinsic_classification={
                "EXPERIENCER": (False, False),
                "COMPLEMENT": (None, None),
            },
        )
        # Embedded XCOMP lex: predicts SUBJ + OBJ-PATIENT but the
        # f-structure's XCOMP has bare OBJ. Mismatch fires from
        # the embedded check.
        embedded_le = LexicalEntry(
            lemma="qqq",
            pred="QQQ <SUBJ, OBJ-PATIENT>",
            a_structure=["AGENT", "PATIENT"],
            morph_constraints={"VOICE": "AV"},
            gf_defaults={"AGENT": "SUBJ", "PATIENT": "OBJ-PATIENT"},
            intrinsic_classification={
                "AGENT": (False, False),
                "PATIENT": (True, True),
            },
        )

        # Construct the f-structure with an XCOMP that has bare OBJ.
        embedded_f = FStructure(feats={
            "PRED": "QQQ <SUBJ, OBJ-PATIENT>",
            "VOICE": "AV",
            "SUBJ": FStructure(feats={"PRED": "S"}, id=10),
            "OBJ": FStructure(feats={"PRED": "O"}, id=11),
        }, id=2)
        matrix_f = FStructure(feats={
            "PRED": "ZZZ <SUBJ, XCOMP>",
            "VOICE": "AV",
            "SUBJ": FStructure(feats={"PRED": "S"}, id=10),
            "XCOMP": embedded_f,
        }, id=1)

        # Synthesize lex_items containing both entries (PRED-keyed
        # matching is enough for find_matrix_lex_entry).
        from tgllfg.common import MorphAnalysis
        ma_matrix = MorphAnalysis(lemma="zzz", pos="VERB", feats={"VOICE": "AV"})
        ma_embedded = MorphAnalysis(lemma="qqq", pos="VERB", feats={"VOICE": "AV"})
        lex_items = [
            [(ma_matrix, matrix_le)],
            [(ma_embedded, embedded_le)],
        ]

        astructure, diagnostics = apply_lmt_with_check(matrix_f, lex_items)

        # Matrix is fine (engine and f-structure agree).
        # Embedded fires lmt-mismatch with path=("XCOMP",).
        embedded_mismatches = [
            d for d in diagnostics
            if d.kind == "lmt-mismatch" and d.path == ("XCOMP",)
        ]
        assert len(embedded_mismatches) == 1
        diag = embedded_mismatches[0]
        assert "XCOMP" in diag.message
        # The detail still carries expected/actual for the embedded
        # lex's prediction.
        expected = diag.detail.get("expected")
        actual = diag.detail.get("actual")
        assert isinstance(expected, list)
        assert isinstance(actual, list)
        assert "OBJ-PATIENT" in expected
        assert "OBJ" in actual

    def test_xcomp_without_pred_silently_skipped(self) -> None:
        # An XCOMP value with no PRED (e.g., a stub) doesn't trigger
        # a recursive check. The matrix lex has XCOMP in its
        # PRED/profile so matrix coherence is OK; the recursion
        # then skips the PRED-less stub.
        matrix_le = LexicalEntry(
            lemma="zzz",
            pred="ZZZ <SUBJ, XCOMP>",
            a_structure=["AGENT", "COMPLEMENT"],
            morph_constraints={"VOICE": "AV"},
            gf_defaults={"AGENT": "SUBJ", "COMPLEMENT": "XCOMP"},
            intrinsic_classification={
                "AGENT": (False, False),
                "COMPLEMENT": (None, None),
            },
        )
        empty_xcomp = FStructure(feats={"VOICE": "AV"}, id=2)  # no PRED
        f = FStructure(feats={
            "PRED": "ZZZ <SUBJ, XCOMP>",
            "VOICE": "AV",
            "SUBJ": FStructure(feats={"PRED": "S"}, id=10),
            "XCOMP": empty_xcomp,
        }, id=1)
        from tgllfg.common import MorphAnalysis
        ma = MorphAnalysis(lemma="zzz", pos="VERB", feats={"VOICE": "AV"})
        lex_items = [[(ma, matrix_le)]]
        _astr, diags = apply_lmt_with_check(f, lex_items)
        assert diags == []
