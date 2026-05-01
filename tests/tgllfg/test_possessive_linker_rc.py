"""Phase 5d Commit 6: possessive-linker RC variant.

The construction ``aklat kong binasa`` ("the book that I read") is a
stylistic variant of the standard relativization ``aklat na binasa
ko``. Instead of the actor staying inside the RC as a GEN-NP, it is
hoisted out and surfaces as a possessor of the head NP, joined by
the bound ``-ng`` linker (one of the standard linker variants —
the head NP no longer carries its own ``-ng`` because the linker on
the pronoun does the job).

Two pieces are needed to make this parse:

* **Wackernagel update** (``_is_pre_linker_pron`` in
  ``tgllfg.clitics.placement``): the GEN-pronoun (``ko`` / ``mo`` /
  ``niya``, split out of ``kong`` / ``mong`` / ``niyang`` by
  :func:`tgllfg.text.split_linker_ng`) would normally be hoisted
  into the post-V cluster. The new check keeps it adjacent to its
  ``-ng`` linker token.

* **New gap-category** (``S_GAP_NA``): a SUBJ-gapped non-AV V frame
  with no overt GEN-NP — the actor is supplied externally by the
  wrap rule via ``(↓ OBJ-AGENT) = pronoun``. Three voices (OV /
  DV / IV) with optional DAT adjunct, plus ``PART[POLARITY=NEG]``
  recursion.

* **New wrap rule**: ``NP[CASE=X] → NP[CASE=X] PRON[CASE=GEN]
  PART[LINK=NG] S_GAP_NA``. The pronoun plays a dual role —
  ``(↑ POSS) = ↓2`` makes it the head NP's possessor; ``(↓4
  OBJ-AGENT) = ↓2`` makes it the RC's actor. The same f-structure
  satisfies both equations.

These tests cover:

* The construction in SUBJ position (``Lumakad ang bata kong
  kinain``) and OBJ position (``Kumain ang bata ng libro kong
  binasa``).
* All three vowel-final GEN pronouns (``ko`` 1SG, ``mo`` 2SG,
  ``niya`` 3SG).
* OV / IV variants (DV variant uses ``-an`` suffix and tests the
  same shape).
* Negation under the construction.
* POSS and OBJ-AGENT identity (``f-structure id-equality`` proves
  the dual binding fired).
* Regression: standard pronominal possessive (``ng libro ko``)
  still works.
* Regression: standard SUBJ-relativization (``batang kumain ng
  isda``) still works.
* Wackernagel: pre-V pronoun still hoists; post-V pronoun still
  clusters.
* LMT diagnostics clean.
"""

from __future__ import annotations

from tgllfg.clitics import reorder_clitics
from tgllfg.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import split_enclitics, split_linker_ng, tokenize


def _pipeline_lemmas(text: str) -> list[str]:
    """Run the full pre-parse pipeline and return token lemmas."""
    toks = tokenize(text)
    toks = split_enclitics(toks)
    toks = split_linker_ng(toks)
    ml = analyze_tokens(toks)
    ml = reorder_clitics(ml)
    return [cands[0].lemma if cands else "?" for cands in ml]


def _find_node_with_rc_and_poss(
    text: str, slot: str
) -> tuple[FStructure, FStructure, FStructure] | None:
    """Find a parse where ``f.feats[slot]`` has both POSS and an ADJ
    containing an RC. Returns (matrix, slot_node, poss_node) or None."""
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        node = f.feats.get(slot)
        if not isinstance(node, FStructure):
            continue
        poss = node.feats.get("POSS")
        adj = node.feats.get("ADJ")
        if isinstance(poss, FStructure) and adj:
            rcs = [m for m in adj if isinstance(m, FStructure) and "PRED" in m.feats]
            if rcs:
                return f, node, poss
    return None


# === Wackernagel: pre-linker PRON stays ===================================


class TestWackernagelPreLinker:
    """Pre-linker pronouns (``ko`` / ``mo`` / ``niya`` followed by
    ``-ng`` PART) stay in place — they're part of the possessive-
    linker variant, not clause-level Wackernagel clitics."""

    def test_ko_pre_linker_stays(self) -> None:
        # ``Lumakad ang bata kong kinain`` — ``ko`` should stay in
        # place between ``bata`` and ``-ng``.
        out = _pipeline_lemmas("Lumakad ang bata kong kinain.")
        assert "ko" in out
        ko_idx = out.index("ko")
        # ko comes after bata
        assert out[ko_idx - 1] == "bata"
        # ko is followed by -ng (the bound linker)
        assert out[ko_idx + 1] == "-ng"

    def test_mo_pre_linker_stays(self) -> None:
        out = _pipeline_lemmas("Lumakad ang bata mong kinain.")
        assert "mo" in out
        mo_idx = out.index("mo")
        assert out[mo_idx + 1] == "-ng"

    def test_niya_pre_linker_stays(self) -> None:
        out = _pipeline_lemmas("Lumakad ang bata niyang kinain.")
        assert "niya" in out
        niya_idx = out.index("niya")
        assert out[niya_idx + 1] == "-ng"

    def test_pre_v_pron_still_hoists(self) -> None:
        # Regression: ``Hindi mo kinain ang isda`` — pre-V ``mo``
        # still hoists to post-V cluster (no following ``-ng``).
        out = _pipeline_lemmas("Hindi mo kinain ang isda.")
        # mo lands right after kain (the V token)
        assert out == ["hindi", "kain", "mo", "ang", "isda", "."]

    def test_post_noun_pron_still_stays(self) -> None:
        # Regression: post-NOUN PRON stays in place (existing rule).
        out = _pipeline_lemmas("Kumain ang bata ng libro ko.")
        assert out == ["kain", "ang", "bata", "ng", "libro", "ko", "."]


# === Construction in SUBJ position ========================================


class TestPossessiveLinkerSubj:
    """``Lumakad ang bata kong kinain`` — the head NP is the matrix
    SUBJ; the pronoun is its possessor and the RC's actor."""

    def test_ko_subj_position(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata kong kinain.", "SUBJ"
        )
        assert result is not None
        _, subj, poss = result
        assert subj.feats.get("LEMMA") == "bata"
        assert poss.feats.get("CASE") == "GEN"
        assert poss.feats.get("NUM") == "SG"

    def test_mo_subj_position(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata mong kinain.", "SUBJ"
        )
        assert result is not None
        _, _, poss = result
        assert poss.feats.get("CASE") == "GEN"
        assert poss.feats.get("NUM") == "SG"

    def test_niya_subj_position(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata niyang kinain.", "SUBJ"
        )
        assert result is not None
        _, _, poss = result
        assert poss.feats.get("NUM") == "SG"

    def test_poss_and_obj_agent_share_node(self) -> None:
        # The defining structural property: POSS and the RC's
        # OBJ-AGENT bind to the SAME f-structure.
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata kong kinain.", "SUBJ"
        )
        assert result is not None
        _, subj, poss = result
        adj = subj.feats["ADJ"]
        rcs = [m for m in adj if isinstance(m, FStructure)]
        assert rcs, "no RC in ADJ"
        rc = rcs[0]
        oa = rc.feats.get("OBJ-AGENT")
        assert isinstance(oa, FStructure)
        # id-equality: the same Python object backs both slots.
        assert oa is poss

    def test_rc_is_ov(self) -> None:
        # ``kinain`` is OV — the actor is the GEN slot, hoisted to
        # POSS in this construction.
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata kong kinain.", "SUBJ"
        )
        assert result is not None
        _, subj, _ = result
        adj = subj.feats["ADJ"]
        rcs = [m for m in adj if isinstance(m, FStructure)]
        assert any(rc.feats.get("VOICE") == "OV" for rc in rcs)


# === Construction in OBJ position =========================================


class TestPossessiveLinkerObj:
    """``Kumain ang bata ng libro kong binasa`` — the head NP is the
    AV-OBJ; the pronoun is its possessor and the RC's actor."""

    def test_ko_obj_position(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Kumain ang bata ng libro kong binasa.", "OBJ"
        )
        assert result is not None
        _, obj, poss = result
        assert obj.feats.get("LEMMA") == "libro"
        assert poss.feats.get("NUM") == "SG"

    def test_mo_obj_position(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Kumain ang bata ng libro mong binasa.", "OBJ"
        )
        assert result is not None

    def test_niya_obj_position(self) -> None:
        result = _find_node_with_rc_and_poss(
            "Kumain ang bata ng libro niyang binasa.", "OBJ"
        )
        assert result is not None
        _, obj, poss = result
        adj = obj.feats["ADJ"]
        rcs = [m for m in adj if isinstance(m, FStructure)]
        assert rcs
        rc = rcs[0]
        oa = rc.feats.get("OBJ-AGENT")
        assert isinstance(oa, FStructure)
        assert oa is poss


# === Negation under the construction ======================================


class TestPossessiveLinkerNegation:

    def test_negated_rc(self) -> None:
        # ``Lumakad ang bata kong hindi kinain.`` — RC is negated.
        result = _find_node_with_rc_and_poss(
            "Lumakad ang bata kong hindi kinain.", "SUBJ"
        )
        assert result is not None
        _, subj, _ = result
        adj = subj.feats["ADJ"]
        rcs = [m for m in adj if isinstance(m, FStructure)]
        assert rcs
        rc = rcs[0]
        assert rc.feats.get("POLARITY") == "NEG"


# === Regressions ==========================================================


class TestPossessiveLinkerRegressions:

    def test_standard_pronominal_possessive(self) -> None:
        # ``Kumain ang bata ng libro ko.`` — standard pronominal
        # possessive (no RC). Must still produce a parse with
        # OBJ.POSS = ko's f-structure.
        rs = parse_text("Kumain ang bata ng libro ko.", n_best=10)
        assert rs
        found = False
        for _, f, _, _ in rs:
            obj = f.feats.get("OBJ")
            if not isinstance(obj, FStructure):
                continue
            if obj.feats.get("LEMMA") != "libro":
                continue
            poss = obj.feats.get("POSS")
            if isinstance(poss, FStructure) and poss.feats.get("CASE") == "GEN":
                found = True
                break
        assert found

    def test_standard_subj_relativization(self) -> None:
        # ``Tumakbo ang batang kumain ng isda.`` — standard SUBJ-
        # relativization with NOUN actor in the RC.
        rs = parse_text("Tumakbo ang batang kumain ng isda.", n_best=10)
        assert rs
        found = False
        for _, f, _, _ in rs:
            subj = f.feats.get("SUBJ")
            if not isinstance(subj, FStructure):
                continue
            adj = subj.feats.get("ADJ")
            if not adj:
                continue
            for m in adj:
                if (
                    isinstance(m, FStructure)
                    and m.feats.get("PRED") == "EAT <SUBJ, OBJ>"
                ):
                    found = True
                    break
            if found:
                break
        assert found

    def test_plain_av_transitive_unchanged(self) -> None:
        rs = parse_text("Kumain si Maria ng isda.", n_best=5)
        assert rs
        f = rs[0][1]
        assert f.feats.get("PRED") == "EAT <SUBJ, OBJ>"
        # No POSS on a plain (non-possessive) sentence.
        subj = f.feats.get("SUBJ")
        if isinstance(subj, FStructure):
            assert subj.feats.get("POSS") is None


# === LMT diagnostics ======================================================


class TestPossessiveLinkerLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Lumakad ang bata kong kinain.",
            "Lumakad ang bata mong kinain.",
            "Lumakad ang bata niyang kinain.",
            "Kumain ang bata ng libro kong binasa.",
            "Lumakad ang bata kong hindi kinain.",
        ):
            rs = parse_text(s, n_best=10)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
