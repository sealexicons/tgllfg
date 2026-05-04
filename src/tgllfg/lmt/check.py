# tgllfg/lmt/check.py

"""Phase 5 §8 — pipeline-facing LMT check.

The :func:`lmt_check` function is the replacement for
:func:`tgllfg.lmt.legacy.apply_lmt`: it runs the Bresnan–Kanerva
engine on the lex entry's intrinsic profile and compares the
predicted role-to-GF mapping against the parsed f-structure.

Diagnostic policy:

* **Blocking** — Subject-slot mismatch (LMT predicts SUBJ but the
  f-structure lacks one) and engine-emitted biuniqueness violations
  (two roles mapping to the same GF in the lex profile). These
  surface through ``subject-condition-failed`` and
  ``lmt-biuniqueness-violated`` respectively, both already
  blocking by absence from
  :data:`tgllfg.fstruct.NON_BLOCKING_KINDS`.

* **Informational** — non-SUBJ GF set differences (e.g., the
  Phase 4 grammar emits bare ``OBJ`` while the engine predicts
  ``OBJ-θ`` for non-AV ng-non-pivots). These surface as
  ``lmt-mismatch``, kept in ``NON_BLOCKING_KINDS`` so the parse
  survives.

The engine's ``subject-condition-failed`` (no role maps to SUBJ in
the lex profile) is intentionally **dropped** when surfacing: if
the f-structure lacks SUBJ too, :func:`tgllfg.fstruct.lfg_well_formed`
already emits a structural ``subject-condition-failed`` downstream;
if the f-structure has SUBJ (lex profile says no, grammar says
yes), the parse is structurally OK and shouldn't be suppressed.

The legacy heuristic remains available via
:func:`tgllfg.lmt.legacy.apply_lmt` for the synthesizer-fallback
path (verbs whose lex entry can't be located post-solve).
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence

from ..common import AStructure, FStructure, LexicalEntry, MorphAnalysis
from ..fstruct import Diagnostic
from ..fstruct.checks import is_governable_gf, parse_pred_template
from .common import intrinsics_for, stipulated_gfs_for
from .legacy import apply_lmt
from .oblique_classifier import classify_oblique_slots
from .principles import compute_mapping


def find_matrix_lex_entry(
    f: FStructure,
    lex_items: Sequence[Sequence[tuple[MorphAnalysis, LexicalEntry | None]]],
) -> LexicalEntry | None:
    """Return the :class:`LexicalEntry` that drove the matrix verb's
    parse, by matching the f-structure's PRED + percolated features
    against each candidate's ``pred`` + ``morph_constraints``.

    Only morph features that the grammar percolates to the matrix
    f-structure are considered (see ``cfg/_helpers.py``
    ``_VERB_PERCOLATION``: PRED, VOICE, ASPECT, MOOD, LEX-ASTRUCT).
    Constraints on non-percolated features (TR, APPL, CAUS,
    CTRL_CLASS) live on the V's sub-projection and aren't visible
    here; we ignore them and rely on (PRED, VOICE) plus
    most-specific-wins to disambiguate. This is sufficient for the
    Phase 4 BASE because applicative / causative variants differ in
    PRED template (e.g., ``MAKE`` vs ``MAKE-FOR``, ``EAT`` vs
    ``CAUSE-EAT``).

    Returns ``None`` when no candidate matches.
    """
    pred = f.feats.get("PRED")
    if pred is None:
        return None
    candidates: list[LexicalEntry] = []
    for cand_list in lex_items:
        for _ma, le in cand_list:
            if le is None or le.pred != pred:
                continue
            # Match on visible constraints only.
            visible_constraints = {
                k: v
                for k, v in le.morph_constraints.items()
                if k in f.feats
            }
            if all(
                f.feats.get(k) == v for k, v in visible_constraints.items()
            ):
                candidates.append(le)
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    # Defense in depth: prefer the entry with the most
    # morph_constraints (most specific) when the visible-constraints
    # match leaves multiple candidates.
    return max(candidates, key=lambda le: len(le.morph_constraints))


def _governable_gfs(f: FStructure) -> set[str]:
    """The governable GF feature names present on `f` (top-level)."""
    return {k for k in f.feats if is_governable_gf(k)}


def lmt_check(
    f: FStructure, lex_entry: LexicalEntry
) -> tuple[AStructure, list[Diagnostic]]:
    """Run the Bresnan–Kanerva engine on `lex_entry`'s intrinsic
    profile and compare the predicted GFs against `f`'s governable
    features.

    Returns ``(astructure, diagnostics)``. ``astructure`` is built
    from the engine's role-to-GF map (matches the legacy
    :func:`apply_lmt` return shape so :func:`tgllfg.renderers.render_a`
    keeps working). Diagnostics include any from the engine itself
    (Subject Condition, biuniqueness — see :func:`compute_mapping`)
    plus an ``lmt-mismatch`` record if the engine's GF set differs
    from the f-structure's. Mismatch is informational; the pipeline
    keeps the parse.
    """
    pred_str = lex_entry.pred
    pred_name = pred_str.split()[0] if pred_str else ""

    frame = intrinsics_for(lex_entry)
    stipulated = stipulated_gfs_for(lex_entry)
    result = compute_mapping(
        frame, stipulated_gfs=stipulated, pred_name=pred_name
    )

    diagnostics: list[Diagnostic] = []

    # Reclassify ADJUNCT sa-NPs into typed OBL-θ slots before the
    # GF-set comparison so the comparison reflects the post-classify
    # state.
    diagnostics.extend(classify_oblique_slots(f, result.mapping))

    expected_gfs = set(result.mapping.values())
    # Phase 5c §7.6 follow-on (Commit 5): raising verbs declare
    # non-thematic GFs in their PRED template (outside ``<...>``).
    # The BK engine only maps thematic roles, so the engine's
    # mapping doesn't include the non-thematic SUBJ. Add it here
    # so the comparison treats the f-structure's SUBJ as expected
    # (it IS expected — required by the lex's PRED — just not
    # via thematic-role mapping).
    try:
        tmpl = parse_pred_template(pred_str)
        expected_gfs.update(tmpl.non_thematic)
    except ValueError:
        pass
    actual_gfs = _governable_gfs(f)

    # Surface engine-emitted biuniqueness violations as blocking.
    # ``compute_mapping`` emits ``lmt-biuniqueness-violated`` when
    # the lex profile has two roles mapping to the same GF — always
    # a real lex contradiction, so the parse should surface the
    # inconsistency rather than silently produce a misleading
    # mapping.
    for engine_diag in result.diagnostics:
        if engine_diag.kind == "lmt-biuniqueness-violated":
            diagnostics.append(engine_diag)
        # The engine's ``subject-condition-failed`` (no role mapped
        # to SUBJ in the lex profile) is intentionally dropped here.
        # If the f-structure also lacks SUBJ, ``lfg_well_formed``
        # downstream emits a structural ``subject-condition-failed``;
        # if it has SUBJ, the parse is structurally OK and
        # shouldn't be suppressed for a lex-profile inconsistency.

    # SUBJ-slot mismatch is structural — promote to blocking via
    # ``subject-condition-failed``. Fires when the LMT engine
    # predicts SUBJ for some role but the f-structure has no SUBJ
    # feature; the post-classify f-structure is the one being
    # checked, so OBL-θ classification has already happened.
    expected_has_subj = "SUBJ" in expected_gfs
    actual_has_subj = "SUBJ" in actual_gfs
    if expected_has_subj and not actual_has_subj:
        diagnostics.append(Diagnostic(
            kind="subject-condition-failed",
            message=(
                f"LMT predicts SUBJ for {pred_str!r} but f-structure "
                f"has no SUBJ feature"
            ),
            detail={
                "expected": sorted(expected_gfs),
                "actual": sorted(actual_gfs),
                "pred": pred_str,
            },
        ))

    # Non-SUBJ GF set differences stay informational — primarily
    # the Phase 4 grammar's bare ``OBJ`` vs the engine's typed
    # ``OBJ-θ`` for non-AV ng-non-pivots. The parse survives so
    # downstream callers see both the grammar's bindings and the
    # engine's typed prediction.
    if expected_gfs != actual_gfs:
        diagnostics.append(Diagnostic(
            kind="lmt-mismatch",
            message=(
                f"LMT-derived GFs {sorted(expected_gfs)} ≠ f-structure "
                f"governable GFs {sorted(actual_gfs)} (PRED={pred_str!r})"
            ),
            detail={
                "expected": sorted(expected_gfs),
                "actual": sorted(actual_gfs),
                "pred": pred_str,
            },
        ))

    astructure = AStructure(
        pred=pred_name,
        roles=list(lex_entry.a_structure),
        mapping={role.value: gf for role, gf in result.mapping.items()},
    )
    return astructure, diagnostics


def _walk_xcomp_subs(
    f: FStructure, seen: set[int]
) -> Iterator[tuple[FStructure, tuple[str, ...]]]:
    """Yield ``(sub_f, path)`` for every embedded f-structure in
    ``XCOMP`` / ``COMP`` slots that has its own ``PRED``.

    The path is the sequence of feature names from the matrix to
    the embedded f-structure (e.g., ``("XCOMP",)`` for a
    one-deep XCOMP, ``("XCOMP", "XCOMP")`` for two-deep). ``seen``
    deduplicates by canonical-node id so reentrant XCOMPs (control
    SUBJ-sharing) are visited exactly once.
    """
    if f.id in seen:
        return
    seen.add(f.id)
    for key in ("XCOMP", "COMP"):
        sub = f.feats.get(key)
        if not isinstance(sub, FStructure):
            continue
        if sub.id in seen:
            continue
        if "PRED" not in sub.feats:
            continue
        yield sub, (key,)
        for nested, nested_path in _walk_xcomp_subs(sub, seen):
            yield nested, (key,) + nested_path


def _retag_diagnostics(
    diagnostics: list[Diagnostic], path: tuple[str, ...]
) -> list[Diagnostic]:
    """Return copies of `diagnostics` with `path` prefixed to each
    diagnostic's ``path`` field, so embedded-clause diagnostics
    surface their location in the f-structure."""
    out: list[Diagnostic] = []
    for d in diagnostics:
        out.append(Diagnostic(
            kind=d.kind,
            message=f"[{'.'.join(path)}] {d.message}",
            path=path + d.path,
            equation=d.equation,
            cnode_label=d.cnode_label,
            detail=d.detail,
        ))
    return out


def apply_lmt_with_check(
    f: FStructure,
    lex_items: Sequence[Sequence[tuple[MorphAnalysis, LexicalEntry | None]]],
) -> tuple[AStructure, list[Diagnostic]]:
    """Pipeline-facing wrapper: locate the matrix lex entry by
    f-structure features, run :func:`lmt_check` on the matrix, then
    recursively run :func:`lmt_check` on every embedded f-structure
    in ``XCOMP`` / ``COMP`` slots that has its own ``PRED``. Fall
    back to the legacy heuristic when no matrix lex entry can be
    located.

    Embedded-clause diagnostics carry the f-structure path
    (e.g., ``XCOMP``) so the user can see where the diagnostic came
    from. The recursion walks unique f-structures only — the
    structure-shared SUBJ between matrix and XCOMP (control verbs)
    doesn't trigger a redundant check.

    The fallback path keeps the synthesizer-driven parses
    (verbs absent from :data:`BASE`) producing an :class:`AStructure`
    even though the LMT bridge has nothing to read intrinsics from.
    No diagnostics are emitted on the fallback — the synthesizer's
    own intrinsics already match its ``gf_defaults``, so the legacy
    heuristic and the engine agree by construction.
    """
    le = find_matrix_lex_entry(f, lex_items)
    if le is None:
        return apply_lmt(f), []
    astructure, diagnostics = lmt_check(f, le)

    # Recursively check embedded XCOMP/COMP sub-f-structures. Pass
    # an empty ``seen`` set; ``_walk_xcomp_subs`` handles the
    # cycle-prevention itself (it adds f.id on entry).
    for sub_f, path in _walk_xcomp_subs(f, set()):
        sub_le = find_matrix_lex_entry(sub_f, lex_items)
        if sub_le is None:
            continue
        _sub_astr, sub_diags = lmt_check(sub_f, sub_le)
        diagnostics.extend(_retag_diagnostics(sub_diags, path))

    return astructure, diagnostics
