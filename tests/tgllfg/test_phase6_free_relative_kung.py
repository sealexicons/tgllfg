# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 6.E Commit 2: Free relative kung-S as DP (§18.1 L93).

A ``kung``-headed wh-clause functions as a non-COMP NP argument
of a matrix predicate — the free-relative reading "whoever did
X" / "whatever was X-ed". Three new NP wrap rules (NOM via
``ang``; GEN via ``ng``; DAT via ``sa``) admit
``CASE-MARKER[DEM=false] S_INTERROG_COMP`` as ``NP[CASE=X]``,
with the constraining equation ``(↓2 Q_TYPE) =c 'WH'`` gating
the rule to the wh-variant of S_INTERROG_COMP (excluding
Phase 5n.B C11's yes/no-with-ba and bare-declarative variants).

F-structure shape on the free-relative NP head:

    PRED      = 'PRO'           ; the free-relative head marker
    CASE      = X               ; matrix-determined
    FREE_REL  = True            ; binary marker
    WH_LEMMA  = inner.WH_LEMMA  ; lifted from the wh-cleft inside
    ADJ       ∋ { kung-S }      ; the kung-wrapped wh-cleft

These tests cover:

* **Basic free-relative parsing** — depth-1 positive cases with
  sino/ano in NOM/GEN/DAT slots; the kung-S sits in ADJ.
* **F-structure assertions** — the rule produces ``PRED='PRO'``,
  ``FREE_REL=True``, ``WH_LEMMA`` lifted, and the inner kung-S
  has ``COMP_TYPE='INTERROG'`` and ``Q_TYPE='WH'``.
* **Wh-PRON paradigm** — sino, ano, alin all admit free-relative
  composition through the Phase 5i C2 wh-cleft.
* **Bare-form kung-S** — colloquial bare-form (Phase 5n.B C10:
  ``kung sino kumain``) also produces S_INTERROG_COMP[Q_TYPE=WH]
  and composes into the free-relative rule.
* **Selectional disambiguation** — KNOW-class (alam) and
  ASK-class (tanong) indirect-Q parses still fire; the
  free-relative rule does not crossfire into COMP slots
  because the matrix rules require ``S_INTERROG_COMP`` directly,
  not ``NP``.
* **Negative cases** — yes/no kung-S and bare-declarative kung-S
  don't free-relate (``Q_TYPE=WH`` gate fails).
* **Regressions** — the Phase 5e Commit 5 headless RC continues
  to parse; the Phase 5i C2 wh-cleft Q continues to parse.
"""

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _members(s: object) -> list[FStructure]:
    """Return the FStructure members of a set/frozenset feat value."""
    if not isinstance(s, (set, frozenset, list, tuple)):
        return []
    return [m for m in s if isinstance(m, FStructure)]


def _walk(f: FStructure, depth: int = 6) -> list[FStructure]:
    """Walk the f-structure breadth-first, returning every reachable
    FStructure node up to ``depth`` levels deep."""
    out: list[FStructure] = []
    seen: set[int] = set()
    frontier: list[tuple[FStructure, int]] = [(f, 0)]
    while frontier:
        cur, d = frontier.pop(0)
        if cur.id in seen or d > depth:
            continue
        seen.add(cur.id)
        out.append(cur)
        for v in cur.feats.values():
            if isinstance(v, FStructure):
                frontier.append((v, d + 1))
            else:
                for m in _members(v):
                    frontier.append((m, d + 1))
    return out


def _find_free_rel(f: FStructure) -> FStructure | None:
    """Find the first FStructure node with ``FREE_REL=True`` reachable
    from ``f``. Returns None if none found."""
    for node in _walk(f):
        if node.feats.get("FREE_REL") is True:
            return node
    return None


def _kung_s_adj(fr: FStructure) -> FStructure | None:
    """Given a free-relative NP head, return the kung-S in its ADJ set
    (the one with COMP_TYPE='INTERROG'). Returns None if not found."""
    for m in _members(fr.feats.get("ADJ")):
        if m.feats.get("COMP_TYPE") == "INTERROG":
            return m
    return None


def _has_blocking(diags: list) -> bool:
    return any(
        getattr(d, "kind", "") in ("constraint-failed", "lmt-mismatch")
        for d in diags
    )


# === Basic free-relative parsing ============================================


class TestBasicFreeRelative:
    """Three case-marker variants × canonical wh-cleft inside kung."""

    def test_dat_obl_sino(self) -> None:
        # ``Galit ako sa kung sino ang nag-record.`` — DAT-OBL on
        # an oblique slot. We use ``pumunta`` here because ``galit``
        # ADJ-predicative doesn't parse in the current grammar
        # (separate issue, not 6.E scope).
        rs = parse_text("Pumunta ako sa kung sino ang dumating.")
        assert rs, "no parse"
        fr_parses = [p for p in rs if _find_free_rel(p[1])]
        assert fr_parses, "no parse with FREE_REL=True"
        _, f, _, diags = fr_parses[0]
        fr = _find_free_rel(f)
        assert fr is not None
        assert fr.feats.get("CASE") == "DAT"
        assert fr.feats.get("PRED") == "PRO"
        assert fr.feats.get("FREE_REL") is True
        assert fr.feats.get("WH_LEMMA") == "sino"
        assert not _has_blocking(diags)

    def test_nom_subj_sino(self) -> None:
        # ``Tumakbo ang kung sino ang gutom.`` — kung-S as NOM-SUBJ
        # of an intransitive matrix verb. The matrix predicate
        # composes with the free-relative NP.
        rs = parse_text("Tumakbo ang kung sino ang gutom.")
        assert rs, "no parse"
        fr_parses = [p for p in rs if _find_free_rel(p[1])]
        assert fr_parses, "no parse with FREE_REL=True"
        _, f, _, diags = fr_parses[0]
        fr = _find_free_rel(f)
        assert fr is not None
        assert fr.feats.get("CASE") == "NOM"
        assert fr.feats.get("PRED") == "PRO"
        assert fr.feats.get("FREE_REL") is True
        assert fr.feats.get("WH_LEMMA") == "sino"
        assert not _has_blocking(diags)

    def test_gen_obj_ano(self) -> None:
        # ``Bumili ako ng kung ano ang dumating.`` — kung-S as
        # GEN-OBJ on an AV transitive. The free-relative NP fills
        # the GEN-OBJ slot.
        rs = parse_text("Bumili ako ng kung ano ang dumating.")
        assert rs, "no parse"
        fr_parses = [p for p in rs if _find_free_rel(p[1])]
        assert fr_parses, "no parse with FREE_REL=True"
        _, f, _, diags = fr_parses[0]
        fr = _find_free_rel(f)
        assert fr is not None
        assert fr.feats.get("CASE") == "GEN"
        assert fr.feats.get("PRED") == "PRO"
        assert fr.feats.get("FREE_REL") is True
        assert fr.feats.get("WH_LEMMA") == "ano"
        assert not _has_blocking(diags)


# === F-structure shape assertions ===========================================


class TestFStructureShape:
    """The kung-S sits as ADJ on the free-relative NP head; the
    inner kung-S has COMP_TYPE='INTERROG' + Q_TYPE='WH'."""

    def test_kung_s_in_adj(self) -> None:
        rs = parse_text("Pumunta ako sa kung sino ang dumating.")
        _, f, _, _ = [p for p in rs if _find_free_rel(p[1])][0]
        fr = _find_free_rel(f)
        assert fr is not None
        kung_s = _kung_s_adj(fr)
        assert kung_s is not None, "kung-S not in ADJ"
        assert kung_s.feats.get("COMP_TYPE") == "INTERROG"
        assert kung_s.feats.get("Q_TYPE") == "WH"
        # The kung-S is the wh-cleft (PRED='WH <SUBJ>') wrapped.
        pred = kung_s.feats.get("PRED")
        assert pred is not None and "WH" in str(pred)

    def test_inner_subj_is_headless_rc(self) -> None:
        # The inner wh-cleft's SUBJ is a headless-RC NP — e.g.,
        # ``ang dumating`` "the one who came".
        rs = parse_text("Pumunta ako sa kung sino ang dumating.")
        _, f, _, _ = [p for p in rs if _find_free_rel(p[1])][0]
        fr = _find_free_rel(f)
        assert fr is not None
        kung_s = _kung_s_adj(fr)
        assert kung_s is not None
        inner_subj = kung_s.feats.get("SUBJ")
        assert isinstance(inner_subj, FStructure)
        # Headless RC: PRED='PRO', CASE=NOM.
        assert inner_subj.feats.get("PRED") == "PRO"
        assert inner_subj.feats.get("CASE") == "NOM"


# === Wh-PRON paradigm ======================================================


class TestWhPronParadigm:
    """sino / ano / alin all admit free-relative composition through
    the Phase 5i C2 wh-cleft."""

    def test_sino_human(self) -> None:
        rs = parse_text("Tumakbo ang kung sino ang gutom.")
        fr_parses = [p for p in rs if _find_free_rel(p[1])]
        assert fr_parses
        _, f, _, _ = fr_parses[0]
        fr = _find_free_rel(f)
        assert fr is not None
        assert fr.feats.get("WH_LEMMA") == "sino"

    def test_ano_non_human(self) -> None:
        rs = parse_text("Bumili ako ng kung ano ang dumating.")
        fr_parses = [p for p in rs if _find_free_rel(p[1])]
        assert fr_parses
        _, f, _, _ = fr_parses[0]
        fr = _find_free_rel(f)
        assert fr is not None
        assert fr.feats.get("WH_LEMMA") == "ano"

    def test_alin_selectional(self) -> None:
        rs = parse_text("Bumili ako ng kung alin ang dumating.")
        fr_parses = [p for p in rs if _find_free_rel(p[1])]
        assert fr_parses
        _, f, _, _ = fr_parses[0]
        fr = _find_free_rel(f)
        assert fr is not None
        assert fr.feats.get("WH_LEMMA") == "alin"


# === Bare-form colloquial kung-S ===========================================


class TestBareFormKungS:
    """Phase 5n.B Commit 10's bare-form colloquial wh-Q
    (``Sino kumain.`` without ``ang``) also produces
    S[Q_TYPE=WH], and the S_INTERROG_COMP wrap composes the
    same way into a free-relative."""

    def test_bare_form_sino(self) -> None:
        rs = parse_text("Pumunta ako sa kung sino kumain.")
        fr_parses = [p for p in rs if _find_free_rel(p[1])]
        assert fr_parses, "bare-form free-relative not admitted"
        _, f, _, diags = fr_parses[0]
        fr = _find_free_rel(f)
        assert fr is not None
        assert fr.feats.get("CASE") == "DAT"
        assert fr.feats.get("WH_LEMMA") == "sino"
        assert not _has_blocking(diags)


# === Selectional disambiguation ============================================


class TestSelectionalDisambiguation:
    """The free-relative rule is selectional — it produces ``NP``,
    not ``S_INTERROG_COMP``. KNOW-class (alam) and ASK-class
    (tanong) matrix rules require ``S_INTERROG_COMP`` directly,
    so the free-relative path does not crossfire into their
    COMP slots. The indirect-Q reading still parses normally."""

    def test_alam_indirect_q_still_parses(self) -> None:
        # ``Alam ko kung sino ang kumain.`` — Phase 5i C8
        # indirect-Q under KNOW-class.
        rs = parse_text("Alam ko kung sino ang kumain.")
        assert rs, "Phase 5i C8 indirect-Q broken"
        # The matrix S has COMP with COMP_TYPE='INTERROG' (not an
        # NP-bound free-relative).
        any_comp_interrog = False
        for _, f, _, _ in rs:
            comp = f.feats.get("COMP")
            if isinstance(comp, FStructure):
                if comp.feats.get("COMP_TYPE") == "INTERROG":
                    any_comp_interrog = True
                    break
        assert any_comp_interrog, "no COMP-bound indirect-Q parse"

    def test_tinanong_indirect_q_still_parses(self) -> None:
        # ``Tinanong niya kung sino ang kumain.`` — Phase 5n.A C29
        # ASK-class reported-Q.
        rs = parse_text("Tinanong niya kung sino ang kumain.")
        assert rs, "Phase 5n.A C29 ASK-class indirect-Q broken"


# === Negative cases =========================================================


class TestNegativeYesNoKungS:
    """Yes/no kung-S (with ``ba`` — Phase 5n.B C11) doesn't free-
    relate: its inner clause has Q_TYPE='YES_NO', not 'WH', so the
    ``=c 'WH'`` gate fails."""

    def test_yes_no_no_free_relative(self) -> None:
        # ``Pumunta ako sa kung kumain ba si Maria.`` — yes/no
        # kung-S as DAT slot. No matrix predicate accepts a
        # yes/no kung-S as a non-COMP slot; free-relative path
        # rejects because Q_TYPE='YES_NO' ≠ 'WH'. 0-parse expected.
        rs = parse_text("Pumunta ako sa kung kumain ba si Maria.")
        # We assert no FREE_REL parses (≥0 total parses allowed —
        # the matrix might produce something else, but no FR).
        fr_parses = [p for p in rs if _find_free_rel(p[1])]
        assert not fr_parses, (
            f"yes/no kung-S spuriously free-related: "
            f"{len(fr_parses)} parses with FREE_REL"
        )


class TestNegativeBareDeclKungS:
    """Bare-declarative kung-S (Phase 5n.B C11) doesn't free-relate:
    its inner clause has no Q_TYPE feat at all (¬ Q_TYPE), so the
    ``=c 'WH'`` gate fails."""

    def test_bare_decl_no_free_relative(self) -> None:
        # ``Pumunta ako sa kung kumain si Maria.`` — bare-decl
        # kung-S as DAT slot. Same expectation as yes/no.
        rs = parse_text("Pumunta ako sa kung kumain si Maria.")
        fr_parses = [p for p in rs if _find_free_rel(p[1])]
        assert not fr_parses, (
            f"bare-decl kung-S spuriously free-related: "
            f"{len(fr_parses)} parses with FREE_REL"
        )


# === Regressions ============================================================


class TestRegressions:
    """The 6.E rule doesn't disturb adjacent constructions."""

    def test_headless_rc_still_parses(self) -> None:
        # Phase 5e Commit 5 headless RC.
        rs = parse_text("Tumakbo ang kumain.")
        assert rs, "Phase 5e C5 headless RC broken"

    def test_wh_cleft_q_still_parses(self) -> None:
        # Phase 5i Commit 2 wh-cleft Q.
        rs = parse_text("Sino ang kumain?")
        assert rs, "Phase 5i C2 wh-cleft broken"
