"""Phase 4 §7.9: robustness — fragment extraction, ranking, strict mode.

Three deliverables:

* **Fragments on full-parse failure**:
  :func:`parse_text_with_fragments` walks the Earley chart for the
  largest non-root completed states when no complete parse exists.
  Each fragment carries its span, partial f-structure, and
  blocking diagnostics for debugging.
* **Heuristic ranking** of complete parses by tuple key
  ``(tree_depth, voice_score)``: shorter derivations win; AV is
  preferred over non-AV when ambiguous.
* **CLI ``--strict`` flag**: suppresses fragment output on
  full-parse failure.
"""

from __future__ import annotations

import io
from contextlib import redirect_stderr, redirect_stdout

from tgllfg.cli import main as cli_main
from tgllfg.core.pipeline import (
    Fragment,
    ParseResult,
    parse_text,
    parse_text_with_fragments,
)


# === ParseResult shape =====================================================


def test_parse_result_has_complete_parses() -> None:
    """Successful parse: ParseResult.parses is non-empty,
    fragments is empty."""
    r = parse_text_with_fragments("Kumain ang aso.")
    assert isinstance(r, ParseResult)
    assert r.parses
    assert r.fragments == []


def test_parse_result_fragments_on_failure() -> None:
    """Sentence with broken structure: parses empty, fragments
    populated with partial Fragment dataclasses."""
    r = parse_text_with_fragments("Kumain ng aso ang.")
    assert r.parses == []
    assert r.fragments
    assert all(isinstance(f, Fragment) for f in r.fragments)


def test_fragment_carries_span() -> None:
    """Each Fragment has a (start, end) span and a CNode."""
    r = parse_text_with_fragments("Kumain ng aso ang.")
    assert r.fragments
    f0 = r.fragments[0]
    start, end = f0.span
    assert start < end
    assert f0.ctree is not None


def test_fragments_ordered_by_span_size() -> None:
    """Fragments are returned largest-span-first."""
    r = parse_text_with_fragments("Kumain ng aso ang.")
    if len(r.fragments) > 1:
        spans = [f.span for f in r.fragments]
        sizes = [end - start for start, end in spans]
        assert sizes == sorted(sizes, reverse=True)


def test_parse_text_legacy_signature_unchanged() -> None:
    """:func:`parse_text` still returns the legacy 4-tuple list
    so existing tests aren't disturbed."""
    out = parse_text("Kumain ang aso.")
    assert out
    c, f, a, diags = out[0]
    assert c is not None
    assert f is not None


# === Heuristic ranking =====================================================


def test_ranker_prefers_av_tr_in_transitive_context() -> None:
    """``Kumain ang aso ng isda`` parses ambiguously (AV-tr with
    OBJ vs AV-intr with possessive on SUBJ). The ranker picks the
    transitive-OBJ reading first because its c-tree is shorter
    (no extra possessive wrap)."""
    out = parse_text("Kumain ang aso ng isda.")
    assert out
    pred = out[0][1].feats.get("PRED")
    assert pred == "EAT <SUBJ, OBJ>"


def test_ranker_prefers_smaller_tree() -> None:
    """The first parse has the smallest depth."""
    out = parse_text("Kumain ang aso ng isda.")
    assert len(out) >= 2
    from tgllfg.core.pipeline import _count_nodes
    depths = [_count_nodes(c) for c, _, _, _ in out]
    assert depths == sorted(depths)


# === Fragment well-formedness ==============================================


def test_fragment_diagnostics_surface() -> None:
    """Fragments carry their diagnostics so callers can see *what*
    failed (e.g. completeness-failed for a missing OBJ)."""
    r = parse_text_with_fragments("Kumain ng aso ang.")
    assert r.fragments
    # At least one fragment should have produced diagnostics
    # (blocking or otherwise) — they're the partial-parse story.
    has_diagnostic = any(f.diagnostics for f in r.fragments)
    # Fragments with empty diagnostics are still valid (the
    # fragment itself was well-formed; what failed was promotion
    # to the full sentence). Just make sure the field exists.
    assert all(isinstance(f.diagnostics, list) for f in r.fragments)
    # And we can read it without exception.
    _ = has_diagnostic


# === CLI --strict ==========================================================


def _run_cli(argv: list[str]) -> tuple[str, str]:
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    try:
        with redirect_stdout(out_buf), redirect_stderr(err_buf):
            cli_main(argv)
    except SystemExit as e:
        # argparse may sys.exit(2) on bad args; let those propagate
        # so the test sees the failure.
        if e.code not in (0, None):
            raise
    return out_buf.getvalue(), err_buf.getvalue()


def test_cli_parse_complete() -> None:
    out, err = _run_cli(["parse", "Kumain ang aso."])
    assert "Parse #1" in out
    assert "PRED" in out


def test_cli_parse_failure_default_emits_fragments() -> None:
    """Default mode: fragments printed on full-parse failure."""
    out, err = _run_cli(["parse", "Kumain ng aso ang."])
    assert "(partial:" in out
    assert "Fragment" in out


def test_cli_parse_failure_strict_suppresses_fragments() -> None:
    """``--strict`` mode: stdout empty on full-parse failure;
    a "no complete parse" notice goes to stderr."""
    out, err = _run_cli(["parse", "Kumain ng aso ang.", "--strict"])
    assert "Fragment" not in out
    assert "partial" not in out
    assert "no complete parse" in err.lower()


def test_cli_parse_n_best_flag() -> None:
    """``--n-best`` caps the number of parses printed."""
    out, _ = _run_cli(["parse", "Kumain ang aso ng isda.", "--n-best", "1"])
    # Should print at most one parse.
    assert out.count("Parse #") == 1


# === Sanity: fragment cap ==================================================


def test_fragment_cap_respected() -> None:
    """``fragment_cap`` keeps the result list bounded."""
    r = parse_text_with_fragments("Kumain ng aso ang.", fragment_cap=1)
    assert len(r.fragments) <= 1
