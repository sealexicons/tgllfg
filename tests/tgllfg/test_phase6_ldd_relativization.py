"""Phase 6.D Commit 3: Long-distance relativization via FU (§18 L47).

Phase 4 §7.5 admitted depth-1 RCs only (the relativization wrap
takes an ``S_GAP`` body). Phase 6.D adds a parallel wrap variant
that takes an ``S_XCOMP`` body — the SUBJ-gapped clause that
``cfg/control.py``'s Phase 4 §7.6 + Phase 5c §7.6 follow-on
control rules produce — so a relative clause can recurse through
an XCOMP chain of arbitrary depth. The matrix wrap uses the
K&Z 1989 §3 eq. 39 binding form

    (↓3 REL-PRO) =c (↓3 XCOMP* SUBJ)

realized as a constraining-form FU equation (see the design
appendix in ``docs/analysis-choices.md`` "Phase 6.D Commit 1"
for why ``=c`` rather than the canonical defining-form ``=``).

These tests cover:

* **Depth-1 regression**: `ang batang kumain` parses with the
  S_GAP-bodied wrap; the FU equation reduces to the depth-1
  case at zero iterations. Sanity-checks that the Phase 4 §7.5
  rewrite from `=c (↓3 SUBJ)` to `=c (↓3 XCOMP* SUBJ)` is
  vacuous as the design appendix predicted.
* **Depth-2** (`gusto + AV inner`): the S_XCOMP-bodied wrap
  fires with one XCOMP traversal. PSYCH-control matrix +
  AV-intransitive inner; SUBJ structure-shared across the
  chain.
* **Depth-3** (`gusto + INTRANS-pumayag + AV inner`): two
  XCOMP traversals; three-level control chain.
* **Depth-4** (`gusto + 2× pumayag + AV inner`): three XCOMP
  traversals; the four-level synthetic chain parallel to the
  existing `test_long_distance_control::TestFourDeep`.
* **Head-case variants**: NOM (`ang batang...`), GEN
  (`ng batang...`), DAT (`sa batang...`).
* **Linker variants**: standalone `na` (consonant-final head:
  `ang anak na...`); bound `-ng` (vowel-final head: `ang
  batang...`).
* **Bottom-of-chain identity**: the deepest SUBJ in the RC's
  XCOMP chain shares the head NP's PRED + CASE via the
  anaphoric REL-PRO copies (Phase 4 §7.5 convention).
* **No regressions to control without relativization**: the
  per-depth REL-PRO threading at `cfg/control.py`'s S_XCOMP
  rules stays load-bearing for non-relativization control;
  this test file doesn't exercise that path directly (covered
  by `test_long_distance_control.py`), but the parser-level
  smoke checks below ensure the new wrap rules don't disturb
  plain control parses.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _members(s: object) -> list[FStructure]:
    """Return the FStructure members of a set/frozenset feat value."""
    if not isinstance(s, (set, frozenset, list, tuple)):
        return []
    return [m for m in s if isinstance(m, FStructure)]


def _find_rc_in_lemma(f: FStructure, head_lemma: str) -> FStructure | None:
    """Find an RC inside any NP whose LEMMA is ``head_lemma``.

    Walks the f-structure looking for an NP (any GF / set member)
    with the given LEMMA. Returns the first RC (member of that NP's
    ADJ set) that has a verbal PRED. Returns ``None`` if no RC is
    found — the test should fail in that case.
    """
    seen: set[int] = set()
    stack: list[FStructure] = [f]
    while stack:
        cur = stack.pop()
        if cur.id in seen:
            continue
        seen.add(cur.id)
        if cur.feats.get("LEMMA") == head_lemma:
            adj = cur.feats.get("ADJ")
            for m in _members(adj):
                if "PRED" in m.feats and m.feats.get("VOICE"):
                    return m
        for v in cur.feats.values():
            if isinstance(v, FStructure):
                stack.append(v)
            elif isinstance(v, (set, frozenset)):
                for elem in v:
                    if isinstance(elem, FStructure):
                        stack.append(elem)
    return None


def _bottom_subj_of_chain(rc: FStructure) -> FStructure | None:
    """Walk RC.XCOMP* down to the bottom; return that level's SUBJ."""
    cur = rc
    for _ in range(8):  # depth cap
        xc = cur.feats.get("XCOMP")
        if not isinstance(xc, FStructure):
            break
        cur = xc
    s = cur.feats.get("SUBJ")
    return s if isinstance(s, FStructure) else None


def _xcomp_depth(rc: FStructure) -> int:
    """Number of XCOMP traversals from the RC's top to its bottom."""
    cur = rc
    depth = 0
    for _ in range(8):
        xc = cur.feats.get("XCOMP")
        if not isinstance(xc, FStructure):
            return depth
        cur = xc
        depth += 1
    return depth


def _has_blocking(diags: list) -> bool:
    return any(getattr(d, "kind", "") in ("constraint-failed", "lmt-mismatch")
               for d in diags)


def _find_parse_with_rc(text: str, head_lemma: str) -> tuple[FStructure, list, FStructure]:
    """Return (f, diags, rc) for the first parse whose RC on
    ``head_lemma`` is well-formed (has a PRED). Asserts parse exists."""
    rs = parse_text(text)
    assert rs, f"no parse for {text!r}"
    for _, f, _, diags in rs:
        rc = _find_rc_in_lemma(f, head_lemma)
        if rc is not None:
            return f, diags, rc
    pytest.fail(
        f"no parse with an RC on lemma {head_lemma!r} for {text!r}; "
        f"{len(rs)} parses examined"
    )


# === Depth-1 regression =====================================================


class TestDepthOneRegression:
    """The S_GAP-bodied wrap (Phase 4 §7.5) keeps working under the
    6.D `=c (↓3 XCOMP* SUBJ)` generalization. Zero iterations of the
    Kleene star reach the same SUBJ that `=c (↓3 SUBJ)` referenced."""

    def test_av_intrans_rc(self) -> None:
        f, diags, rc = _find_parse_with_rc(
            "Tumakbo ang batang kumain.", "bata",
        )
        assert _xcomp_depth(rc) == 0
        assert rc.feats.get("PRED") == "EAT <SUBJ>"
        bottom = _bottom_subj_of_chain(rc)
        assert isinstance(bottom, FStructure)
        # Bottom SUBJ inherits head's PRED + CASE via anaphoric
        # REL-PRO copies.
        assert bottom.feats.get("CASE") == "NOM"
        assert not _has_blocking(diags)

    def test_consonant_final_head_na_linker(self) -> None:
        # ``anak`` is consonant-final → standalone ``na`` linker.
        f, diags, rc = _find_parse_with_rc(
            "Tumakbo ang anak na kumain.", "anak",
        )
        assert _xcomp_depth(rc) == 0
        assert rc.feats.get("PRED") == "EAT <SUBJ>"
        assert not _has_blocking(diags)


# === Depth 2 — PSYCH-control + AV inner =====================================


class TestDepthTwo:
    """`ang batang gustong kumain` — `bata` = matrix SUBJ of `gusto`
    (PSYCH-control) = controlled SUBJ of `kumain` (embedded XCOMP, AV).
    One XCOMP traversal in the RC's chain."""

    def test_psych_av_inner(self) -> None:
        f, diags, rc = _find_parse_with_rc(
            "Tumakbo ang batang gustong kumain.", "bata",
        )
        assert _xcomp_depth(rc) == 1
        assert "WANT" in str(rc.feats.get("PRED"))
        # XCOMP holds the embedded AV clause.
        xc = rc.feats["XCOMP"]
        assert isinstance(xc, FStructure)
        assert "EAT" in str(xc.feats.get("PRED"))
        # SUBJ structure-shared across the two levels.
        assert rc.feats["SUBJ"].id == xc.feats["SUBJ"].id  # type: ignore[union-attr]
        # Bottom-of-chain SUBJ has CASE inherited from head NP via
        # REL-PRO.
        bottom = _bottom_subj_of_chain(rc)
        assert isinstance(bottom, FStructure)
        assert bottom.feats.get("CASE") == "NOM"
        assert not _has_blocking(diags)


# === Depth 3 — PSYCH + INTRANS + AV =========================================


class TestDepthThree:
    """`ang batang gustong pumayag na kumain` — three-level chain:
    WANT (matrix) → AGREE (XCOMP-1) → EAT (XCOMP-2). All SUBJs
    structure-shared via per-depth control threading."""

    def test_psych_intrans_av(self) -> None:
        f, diags, rc = _find_parse_with_rc(
            "Tumakbo ang batang gustong pumayag na kumain.", "bata",
        )
        assert _xcomp_depth(rc) == 2
        assert "WANT" in str(rc.feats.get("PRED"))
        xc1 = rc.feats["XCOMP"]
        assert isinstance(xc1, FStructure)
        assert "AGREE" in str(xc1.feats.get("PRED"))
        xc2 = xc1.feats["XCOMP"]
        assert isinstance(xc2, FStructure)
        assert "EAT" in str(xc2.feats.get("PRED"))
        # All three SUBJs unified.
        ids = {
            rc.feats["SUBJ"].id,    # type: ignore[union-attr]
            xc1.feats["SUBJ"].id,   # type: ignore[union-attr]
            xc2.feats["SUBJ"].id,   # type: ignore[union-attr]
        }
        assert len(ids) == 1, f"chain SUBJs not unified: {ids}"
        assert not _has_blocking(diags)


# === Depth 4 — synthetic four-level chain ===================================


class TestDepthFour:
    """`ang batang gustong pumayag na pumayag na kumain` — synthetic
    four-level chain (parallel to
    test_long_distance_control::TestFourDeep::test_four_deep_chain).
    Verifies the new wrap rule composes with the existing per-depth
    threading without a fixed-depth limit."""

    def test_four_deep_synthetic(self) -> None:
        f, diags, rc = _find_parse_with_rc(
            "Tumakbo ang batang gustong pumayag na pumayag na kumain.",
            "bata",
        )
        assert _xcomp_depth(rc) == 3
        # All four SUBJs structure-shared.
        cur = rc
        ids = set()
        for _ in range(4):
            s = cur.feats.get("SUBJ")
            assert isinstance(s, FStructure)
            ids.add(s.id)
            xc = cur.feats.get("XCOMP")
            if not isinstance(xc, FStructure):
                break
            cur = xc
        assert len(ids) == 1, f"chain SUBJs not unified at depth 4: {ids}"
        assert not _has_blocking(diags)


# === Head-case variants =====================================================


class TestHeadCaseVariants:
    """The wrap rule has 6 variants (3 cases × 2 linkers). NOM and
    GEN are exercised here; DAT is checked in a separate test
    because the head NP lands in ADJUNCT, not SUBJ."""

    def test_nom_head_depth_2(self) -> None:
        # NOM head: `ang batang gustong tumakbo`
        _f, diags, rc = _find_parse_with_rc(
            "Tumakbo ang batang gustong kumain.", "bata",
        )
        bottom = _bottom_subj_of_chain(rc)
        assert isinstance(bottom, FStructure)
        assert bottom.feats.get("CASE") == "NOM"
        assert not _has_blocking(diags)

    def test_gen_head_depth_2(self) -> None:
        # GEN head: `... ng batang gustong tumakbo`
        _f, diags, rc = _find_parse_with_rc(
            "Kumain ang aso ng batang gustong tumakbo.", "bata",
        )
        assert _xcomp_depth(rc) == 1
        bottom = _bottom_subj_of_chain(rc)
        assert isinstance(bottom, FStructure)
        assert bottom.feats.get("CASE") == "GEN"
        assert not _has_blocking(diags)

    def test_dat_head_depth_2(self) -> None:
        # DAT head: `... sa batang gustong tumakbo`. Head NP lands
        # in ADJUNCT[0], not SUBJ.
        _f, diags, rc = _find_parse_with_rc(
            "Kumain ang aso sa batang gustong tumakbo.", "bata",
        )
        assert _xcomp_depth(rc) == 1
        bottom = _bottom_subj_of_chain(rc)
        assert isinstance(bottom, FStructure)
        assert bottom.feats.get("CASE") == "DAT"
        assert not _has_blocking(diags)


# === Linker variants ========================================================


class TestLinkerVariants:
    """Both linker shapes admit cross-clausal RCs."""

    def test_ng_bound_linker_depth_2(self) -> None:
        # `bata` is vowel-final → bound `-ng` linker, split pre-parse.
        _f, diags, rc = _find_parse_with_rc(
            "Tumakbo ang batang gustong kumain.", "bata",
        )
        assert _xcomp_depth(rc) == 1
        assert not _has_blocking(diags)

    def test_na_standalone_linker_depth_2(self) -> None:
        # `anak` is consonant-final → standalone `na` linker.
        _f, diags, rc = _find_parse_with_rc(
            "Tumakbo ang anak na gustong kumain.", "anak",
        )
        assert _xcomp_depth(rc) == 1
        assert "WANT" in str(rc.feats.get("PRED"))
        xc = rc.feats["XCOMP"]
        assert isinstance(xc, FStructure)
        assert "EAT" in str(xc.feats.get("PRED"))
        assert not _has_blocking(diags)


# === Lmt + diagnostics clean across depth ===================================


class TestDiagnosticsCleanAcrossDepth:
    """The new wrap rule + existing per-depth threading must produce
    no blocking diagnostics at any depth, mirroring the
    test_long_distance_control assertions."""

    @pytest.mark.parametrize(
        "text",
        [
            "Tumakbo ang batang kumain.",
            "Tumakbo ang batang gustong kumain.",
            "Tumakbo ang batang gustong pumayag na kumain.",
            "Tumakbo ang batang gustong pumayag na pumayag na kumain.",
        ],
    )
    def test_no_blocking_diagnostics(self, text: str) -> None:
        rs = parse_text(text)
        assert rs, f"no parse for {text!r}"
        # Pick the parse with an RC for diagnostic check.
        for _, f, _, diags in rs:
            if _find_rc_in_lemma(f, "bata"):
                assert not _has_blocking(diags), (
                    f"blocking diags for {text!r}: "
                    f"{[(d.kind, d.message[:60]) for d in diags]}"
                )
                return
        pytest.fail(f"no RC-bearing parse for {text!r}")
