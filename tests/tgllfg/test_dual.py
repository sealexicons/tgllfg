"""Phase 5f Commit 23: dual ``pareho`` / ``kapwa`` (Group H3 item 9).

Closes Phase 5f. Adds 2 ``Q[DUAL="YES", QUANT=BOTH]`` lex
entries (``pareho``, ``kapwa``); both consume the existing
Phase 4 §7.8 ``S → S Q`` float rule unchanged for the clause-
final use:

  Kumain sila pareho.   "they both ate"
  Kumain sila kapwa.    "they both ate" (formal)

The existing Phase 5b ``Q + NP[GEN]`` partitive rules gain
``¬ (↓2 DUAL)`` so dual Qs only float (the partitive
``*ang pareho ng bata`` is non-standard).

Lex (data/tgl/particles.yaml):

* ``pareho`` — Q[QUANT=BOTH, DUAL="YES"]. Native dual /
  "alike" Q.
* ``kapwa``  — Q[QUANT=BOTH, DUAL="YES"]. More formal dual Q.

Polysemy: ``pareho`` also has an equative-predicate reading
(``Pareho ang kanilang sapatos.`` "their shoes are the same"),
which belongs in Phase 5h. Following the Phase 5f Commit 17
bababa / hihigit precedent, that reading will be added as a
separate (lemma, pos) entry when Phase 5h lands.

Grammar: no new rules. The existing Phase 4 §7.8 ``S → S Q``
float rule consumes pareho / kapwa unchanged. The existing
Phase 5b ``Q + NP[GEN]`` partitive rules gain a ``¬ (↓2
DUAL)`` gate (parallel to existing VAGUE / UNIV / DISTRIB_POSS
/ WHOLE gates).

Tests cover:

* Morph: pareho + kapwa analyse as Q with DUAL="YES" +
  QUANT=BOTH.
* Float (clause-final): ``Kumain sila pareho.``,
  ``Kumain sila kapwa.``, ``Kumain ang bata pareho.``,
  ``Kumain ang bata kapwa.``. The matrix S has the dual Q in
  ADJ with QUANT=BOTH + DUAL=YES.
* Negative (per §11.2): ``*ang pareho ng aklat`` (dual in
  GEN-NP partitive blocked by new gate).
* Regression: lahat float, lahat partitive, vague linker,
  universal bawat, distributive-possessive, wholes, cardinal
  all unchanged.
* LMT diagnostics clean.

Out of scope (deferred follow-on commits):

* Clause-initial form (``Pareho silang kumain.`` "they both
  ate") — addressed by the post-Phase-5f deferrals PR's
  clause-initial-dual S rule in ``cfg/clitic.py``
  (with AV intransitive / transitive / ditransitive variants).
  Tested directly in ``test_q_clitic_predicate.py``.
* Equative predicate (``Pareho ang kanilang sapatos.``) —
  Phase 5h scope.
"""

from __future__ import annotations

from tgllfg.core.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.core.pipeline import parse_text
from tgllfg.text import tokenize


def _duals() -> list[str]:
    return ["pareho", "kapwa"]


def _adj_dual(text: str) -> FStructure | None:
    """Find the float ADJ-member with DUAL=YES."""
    rs = parse_text(text, n_best=5)
    for _, f, _, _ in rs:
        adj = f.feats.get("ADJ")
        if adj is None:
            continue
        members = (
            list(adj) if isinstance(adj, (set, frozenset, list)) else [adj]
        )
        for m in members:
            if isinstance(m, FStructure) and m.feats.get("DUAL") == "YES":
                return m
    return None


# === Morph layer ==========================================================


class TestDualMorph:

    def test_all_duals_analyze(self) -> None:
        for lemma in _duals():
            toks = tokenize(lemma)
            ml = analyze_tokens(toks)
            cands = [c for c in ml[0] if c.pos == "Q"]
            assert cands, f"no Q analysis for {lemma!r}"
            ma = cands[0]
            assert ma.feats.get("DUAL") == "YES", (
                f"{lemma}: DUAL expected 'YES', got "
                f"{ma.feats.get('DUAL')!r}"
            )
            assert ma.feats.get("QUANT") == "BOTH"


# === Float (clause-final) =================================================


class TestDualFloat:
    """``Kumain sila pareho.`` "they both ate" — the existing
    Phase 4 §7.8 ``S → S Q`` float rule consumes the dual Q
    unchanged. The matrix S has the dual Q in ADJ with
    QUANT=BOTH + DUAL=YES; ANTECEDENT binds to SUBJ."""

    def test_pareho_float_with_pron_subj(self) -> None:
        adj = _adj_dual("Kumain sila pareho.")
        assert adj is not None
        assert adj.feats.get("QUANT") == "BOTH"
        assert adj.feats.get("DUAL") == "YES"

    def test_kapwa_float_with_pron_subj(self) -> None:
        adj = _adj_dual("Kumain sila kapwa.")
        assert adj is not None
        assert adj.feats.get("QUANT") == "BOTH"
        assert adj.feats.get("DUAL") == "YES"

    def test_pareho_float_with_nominal_subj(self) -> None:
        # ``Kumain ang bata pareho.`` "the children both ate"
        # (semantically requires plural antecedent — bata is SG
        # by default but the construction parses regardless).
        rs = parse_text("Kumain ang bata pareho.", n_best=5)
        assert rs
        _, f, _, _ = rs[0]
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        adj = _adj_dual("Kumain ang bata pareho.")
        assert adj is not None
        assert adj.feats.get("DUAL") == "YES"

    def test_kapwa_float_with_nominal_subj(self) -> None:
        adj = _adj_dual("Kumain ang bata kapwa.")
        assert adj is not None
        assert adj.feats.get("DUAL") == "YES"


# === Negative fixtures (per §11.2) ========================================


class TestDualNegative:

    def test_dual_partitive_blocked(self) -> None:
        # ``*ang pareho ng aklat`` — dual in GEN-NP partitive
        # blocked by new ``¬ (↓2 DUAL)`` gate.
        rs = parse_text("Bumili ang pareho ng aklat.", n_best=10)
        assert rs == [], (
            f"DUAL partitive not blocked: got {len(rs)} parses"
        )

    def test_kapwa_partitive_blocked(self) -> None:
        rs = parse_text("Bumili ang kapwa ng aklat.", n_best=10)
        assert rs == [], (
            f"DUAL kapwa partitive not blocked: got {len(rs)} parses"
        )


# === Regression ===========================================================


class TestDualRegressions:

    def test_lahat_float_unchanged(self) -> None:
        rs = parse_text("Kumain ang bata lahat.", n_best=5)
        assert rs
        _, f, _, _ = rs[0]
        adj = f.feats.get("ADJ")
        assert adj is not None
        members = (
            list(adj) if isinstance(adj, (set, frozenset, list)) else [adj]
        )
        # Lahat should still produce a QUANT=ALL ADJ-member.
        found = False
        for m in members:
            if (isinstance(m, FStructure)
                    and m.feats.get("QUANT") == "ALL"):
                found = True
                break
        assert found, "lahat-float regressed (no QUANT=ALL ADJ)"

    def test_lahat_partitive_unchanged(self) -> None:
        rs = parse_text("Kumakain ang lahat ng bata.", n_best=5)
        assert rs

    def test_vague_linker_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng maraming aklat.", n_best=5)
        assert rs

    def test_universal_unchanged(self) -> None:
        rs = parse_text("Kumakain ang bawat bata.", n_best=5)
        assert rs

    def test_distrib_poss_unchanged(self) -> None:
        rs = parse_text(
            "Bumili ako ng kanyakanyang aklat.", n_best=5
        )
        assert rs

    def test_whole_unchanged(self) -> None:
        rs = parse_text("Kumakain ang buong bata.", n_best=5)
        assert rs

    def test_cardinal_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng tatlong aklat.", n_best=5)
        assert rs


# === LMT diagnostics clean ================================================


class TestDualLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Kumain sila pareho.",
            "Kumain sila kapwa.",
            "Kumain ang bata pareho.",
            "Kumain ang bata kapwa.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
