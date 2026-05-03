"""Phase 5e Commit 4: multi-pronoun RC composition pinning.

Phase 5d Commit 10's deferral list flagged "Multi-pronoun RCs" — a
single matrix sentence with both a matrix-cluster PRON and an
embedded RC-actor PRON, e.g. ``Nakita ko ang batang kinain niya``
("I saw the child she ate"). The Wackernagel logic from Commit 10
(specifically ``_is_post_embedded_v_pron``) handles the two
pronouns independently per-token, and Phase 4 §7.5 relativization
plus Phase 5d Commit 10's RC-actor placement compose. The
construction was structurally available but not pinned with tests.

This commit pins the composition without grammar / placement
changes — pure test additions verifying:

* Both PRONs end up in distinct f-structure slots (different f-node
  ids).
* The matrix-cluster PRON binds to the matrix V's appropriate role.
* The embedded RC-actor PRON binds inside the RC (in ADJ on the
  head NP), not at the matrix level.
* Negation under either the matrix or the RC composes.

Pronouns in Tagalog don't carry a grammar-visible LEMMA (the
analyzer drops PERS as int per the pipeline's "string-valued feats
only" rule), so identification is done by structural position
plus CASE / NUM matching.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.pipeline import parse_text


def _first(text: str) -> FStructure:
    rs = parse_text(text)
    assert rs, f"no parse for {text!r}"
    return rs[0][1]


def _rc_member(np: FStructure) -> FStructure | None:
    """Return the first ADJ member of ``np`` whose PRED is a typical
    relative clause shape (``EAT <SUBJ, OBJ-AGENT>`` etc.). RCs are
    attached as ADJ members of their head NP per Phase 4 §7.5."""
    adj = np.feats.get("ADJ")
    if adj is None:
        return None
    for m in adj:  # type: ignore[union-attr]
        pred = m.feats.get("PRED")  # type: ignore[union-attr]
        if isinstance(pred, str) and pred not in ("NOUN(↑ FORM)", "PRO"):
            return m  # type: ignore[no-any-return]
    return None


# === Multi-pronoun RC: matrix + embedded =================================


class TestMultiPronounRC:
    """Matrix-cluster PRON + embedded RC-actor PRON in one
    sentence. Both pronouns ride into distinct f-structure
    positions without interfering with each other."""

    def test_matrix_obj_pron_plus_rc_actor_pron(self) -> None:
        """``Nakita ko ang batang kinain niya.`` ("I saw the child
        she ate"). Matrix V is `nakita` (kita NVOL); `ko` is its
        PRON-clitic (1sg-GEN). Inside the SUBJ NP `ang bata`, the
        RC `kinain niya` has `niya` as the OV-agent (3sg-GEN)
        kept in-place by Phase 5d Commit 10's Wackernagel
        exception."""
        f = _first("Nakita ko ang batang kinain niya.")
        # Matrix has a PRON-shape role-NP: NUM=SG, CASE=GEN, no
        # LEMMA / PRED (the synthesized ``nakita`` analyses as
        # AV-NVOL with a GEN OBJ).
        matrix_obj = f.feats.get("OBJ")
        assert isinstance(matrix_obj, FStructure)
        assert matrix_obj.feats.get("CASE") == "GEN"
        assert matrix_obj.feats.get("NUM") == "SG"
        # Matrix SUBJ is `ang bata`.
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        # The RC is an ADJ member of SUBJ.
        rc = _rc_member(subj)
        assert rc is not None
        # The RC's actor (OBJ-AGENT) is the RC's GEN PRON `niya`.
        rc_oa = rc.feats.get("OBJ-AGENT")
        assert isinstance(rc_oa, FStructure)
        assert rc_oa.feats.get("CASE") == "GEN"
        assert rc_oa.feats.get("NUM") == "SG"

    def test_two_prons_distinct_fnodes(self) -> None:
        """The matrix-cluster PRON and the embedded RC-actor PRON
        are distinct f-nodes (different ids); not accidentally
        unified."""
        f = _first("Nakita ko ang batang kinain niya.")
        matrix_obj = f.feats["OBJ"]
        rc = _rc_member(f.feats["SUBJ"])
        assert rc is not None
        rc_oa = rc.feats["OBJ-AGENT"]
        assert isinstance(matrix_obj, FStructure)
        assert isinstance(rc_oa, FStructure)
        assert matrix_obj.id != rc_oa.id

    def test_distinct_clause_preds(self) -> None:
        """Matrix and RC have distinct PRED values — the two
        clauses aren't accidentally merged."""
        f = _first("Nakita ko ang batang kinain niya.")
        matrix_pred = f.feats.get("PRED")
        rc = _rc_member(f.feats["SUBJ"])
        assert rc is not None
        rc_pred = rc.feats.get("PRED")
        assert matrix_pred != rc_pred
        assert isinstance(matrix_pred, str)
        assert isinstance(rc_pred, str)
        # Matrix is a `kita`-flavor PRED; RC is a `kain`-flavor.
        assert "KITA" in matrix_pred
        assert "EAT" in rc_pred or "KAIN" in rc_pred

    def test_av_matrix_with_oj_rc(self) -> None:
        """``Kumain ako ng batang kinain niya.`` AV matrix with OV
        RC. `ako` is matrix SUBJ, `niya` is RC OBJ-AGENT. Both
        in distinct positions."""
        f = _first("Kumain ako ng batang kinain niya.")
        # Matrix has `kain` AV PRED; SUBJ is `ako` (1sg-NOM PRON).
        assert f.feats.get("PRED") == "EAT <SUBJ, OBJ>"
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("CASE") == "NOM"
        # OBJ is the patient NP `ng batang kinain niya` — has a
        # head noun with an RC.
        obj = f.feats.get("OBJ")
        assert isinstance(obj, FStructure)
        assert obj.feats.get("LEMMA") == "bata"
        rc = _rc_member(obj)
        assert rc is not None
        rc_oa = rc.feats.get("OBJ-AGENT")
        assert isinstance(rc_oa, FStructure)
        assert rc_oa.feats.get("CASE") == "GEN"

    def test_matrix_cluster_pron_then_rc_pron_orderings(self) -> None:
        """Several matrix-PRON / RC-PRON orderings parse: 1sg + 3sg,
        2sg + 1sg, etc. The Wackernagel logic handles each pair
        independently."""
        cases = [
            "Nakita ko ang batang kinain niya.",   # 1sg + 3sg
            "Nakita mo ang batang kinain niya.",   # 2sg + 3sg
            "Nakita niya ang batang kinain ko.",   # 3sg + 1sg
        ]
        for s in cases:
            rs = parse_text(s, n_best=10)
            assert rs, f"no parse for {s!r}"
            f = rs[0][1]
            # Both PRONs end up in GEN slots (matrix and RC).
            matrix_obj = f.feats.get("OBJ")
            assert isinstance(matrix_obj, FStructure)
            assert matrix_obj.feats.get("CASE") == "GEN"
            subj = f.feats.get("SUBJ")
            assert isinstance(subj, FStructure)
            rc = _rc_member(subj)
            assert rc is not None, f"RC missing in {s!r}"
            rc_oa = rc.feats.get("OBJ-AGENT")
            assert isinstance(rc_oa, FStructure)
            assert rc_oa.feats.get("CASE") == "GEN"
            assert matrix_obj.id != rc_oa.id


# === Negation composition ================================================


class TestNegationComposition:
    """Inner negation in either the matrix or the RC composes
    with multi-pronoun placement."""

    def test_matrix_neg(self) -> None:
        f = _first("Hindi nakita ko ang batang kinain niya.")
        assert f.feats.get("POLARITY") == "NEG"
        matrix_obj = f.feats.get("OBJ")
        assert isinstance(matrix_obj, FStructure)
        assert matrix_obj.feats.get("CASE") == "GEN"

    def test_rc_internal_neg(self) -> None:
        """``Nakita ko ang batang hindi kinain niya.`` RC has its
        own POLARITY=NEG; matrix is unaffected."""
        f = _first("Nakita ko ang batang hindi kinain niya.")
        # Matrix POLARITY is not NEG (the negation is inside the
        # RC).
        assert f.feats.get("POLARITY") != "NEG"
        rc = _rc_member(f.feats["SUBJ"])
        assert rc is not None
        assert rc.feats.get("POLARITY") == "NEG"


# === LMT diagnostics ====================================================


class TestLmtDiagnostics:
    """Multi-pronoun RCs produce no blocking LMT diagnostics."""

    def test_no_blocking_diagnostics(self) -> None:
        rs = parse_text("Nakita ko ang batang kinain niya.", n_best=5)
        for _, _f, _c, diags in rs:
            blocking = [d for d in diags if d.kind != "lmt-mismatch"]
            assert blocking == [], f"unexpected blocking diags: {blocking}"


# === Regression: single-PRON cases unchanged ============================


class TestRegression:
    """The single-PRON cases (matrix-cluster PRON only, or
    RC-actor PRON only) still parse as in Phase 5d Commit 10."""

    def test_matrix_cluster_pron_only(self) -> None:
        f = _first("Nakita ko ang bata.")
        obj = f.feats.get("OBJ")
        assert isinstance(obj, FStructure)
        assert obj.feats.get("CASE") == "GEN"
        # SUBJ is bata, no RC.
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        assert _rc_member(subj) is None

    def test_rc_actor_pron_only(self) -> None:
        f = _first("Tumakbo ang batang kinain niya.")
        # Matrix V is intransitive; no matrix OBJ.
        assert f.feats.get("PRED") == "TAKBO <SUBJ>"
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        rc = _rc_member(subj)
        assert rc is not None
        rc_oa = rc.feats.get("OBJ-AGENT")
        assert isinstance(rc_oa, FStructure)
        assert rc_oa.feats.get("CASE") == "GEN"
