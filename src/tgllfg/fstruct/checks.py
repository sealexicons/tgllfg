# tgllfg/fs_checks.py

"""LFG well-formedness conditions over solved f-structures.

Three classical conditions land here. **Uniqueness** is enforced
upstream by the unifier in :mod:`tgllfg.fgraph` (every atom-mismatch
or type-mismatch is a uniqueness violation in the textbook sense and
already produces a diagnostic). The others are checked here:

* **Completeness** — every governable grammatical function named in
  a PRED's argument list must be present in the f-structure that
  bears that PRED.
* **Coherence** — every governable grammatical function present in
  an f-structure must be named in that f-structure's PRED argument
  list. Adjuncts (``ADJ``) and discourse functions (``TOPIC``,
  ``FOCUS``) are exempt by definition.
* **Subject Condition** — every PRED-bearing f-structure with at
  least one governable argument has a SUBJ. The plan (§4.4) notes
  that LMT properly enforces this in Phase 5; the diagnostic
  surface lives here so failures are debuggable in the meantime.

Governable GFs are: SUBJ, OBJ, COMP, XCOMP, and any feature whose
name starts with ``OBJ-`` or ``OBL-`` (the typed
object/oblique slots from Bresnan–Kanerva LMT).
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from ..core.common import CNode, FStructure
from .graph import Diagnostic


# === PRED templates =======================================================

@dataclass(frozen=True)
class PredTemplate:
    """Decomposition of a PRED string.

    ``name`` is the predicate name (everything before the optional
    angle-bracketed argument list). ``thematic`` is the tuple of
    governable GFs corresponding to thematic roles — args INSIDE
    ``<...>``. ``non_thematic`` is the tuple of governable GFs
    selected by the predicate but bearing no thematic role —
    args OUTSIDE ``<...>`` (Phase 5c §7.6 follow-on Commit 5,
    raising verbs).

    ``governables`` is the canonical union ``thematic +
    non_thematic`` and is what completeness / coherence checks
    use, since both are syntactically required arguments. The
    distinction matters for the LMT engine, which only maps
    thematic roles via the BK truth table.
    """
    name: str
    governables: tuple[str, ...]
    thematic: tuple[str, ...] = ()
    non_thematic: tuple[str, ...] = ()


def parse_pred_template(s: str) -> PredTemplate:
    """Parse a PRED string of the form ``NAME``, ``NAME <a, b, ...>``,
    or (Phase 5c) ``NAME <a, b, ...> c, d, ...`` for raising verbs
    where the trailing args after ``>`` are non-thematic (selected
    structurally but bearing no thematic role).

    Permissive on the name component: anything up to the optional
    angle-bracket section is taken as the name, including the
    placeholder ``NOUN(↑ FORM)`` produced by the toy ``N → NOUN``
    rule. Argument lists are comma-separated; surrounding whitespace
    is stripped.
    """
    s = s.strip()
    if "<" not in s:
        return PredTemplate(s, (), (), ())
    idx = s.index("<")
    name = s[:idx].strip()
    rest = s[idx + 1:]
    if ">" not in rest:
        raise ValueError(
            f"malformed PRED template (missing closing '>'): {s!r}"
        )
    end = rest.index(">")
    body = rest[:end].strip()
    tail = rest[end + 1:].strip()
    thematic: tuple[str, ...] = ()
    if body:
        thematic = tuple(a.strip() for a in body.split(","))
        if any(not a for a in thematic):
            raise ValueError(f"malformed PRED template (empty arg): {s!r}")
    non_thematic: tuple[str, ...] = ()
    if tail:
        non_thematic = tuple(a.strip() for a in tail.split(","))
        if any(not a for a in non_thematic):
            raise ValueError(
                f"malformed PRED template (empty non-thematic arg): {s!r}"
            )
    governables = thematic + non_thematic
    return PredTemplate(name, governables, thematic, non_thematic)


# === Governable GFs =======================================================

# Bare governable function names. Typed forms (OBJ-θ, OBL-θ) are
# matched by prefix in :func:`is_governable_gf`.
_BARE_GOVERNABLE: frozenset[str] = frozenset({
    "SUBJ", "OBJ", "COMP", "XCOMP",
})


def is_governable_gf(name: str) -> bool:
    """True iff `name` is a governable grammatical function in
    Bresnan–Kanerva LMT terms. ``ADJ``, ``TOPIC``, ``FOCUS``, and
    feature attributes (CASE, VOICE, ...) all return False."""
    if name in _BARE_GOVERNABLE:
        return True
    return name.startswith("OBJ-") or name.startswith("OBL-")


# === Walking f-structures =================================================

def _walk_fstructures(
    f: FStructure, seen: set[int] | None = None
) -> Iterator[tuple[FStructure, tuple[str, ...]]]:
    """Yield ``(node, path_from_root)`` for every f-structure
    reachable from `f`, deduplicated by canonical node id so reentrancy
    is visited once."""
    if seen is None:
        seen = set()
    yield from _walk(f, (), seen)


def _walk(
    f: FStructure,
    path: tuple[str, ...],
    seen: set[int],
) -> Iterator[tuple[FStructure, tuple[str, ...]]]:
    if f.id in seen:
        return
    seen.add(f.id)
    yield f, path
    for feat, value in f.feats.items():
        if isinstance(value, FStructure):
            yield from _walk(value, path + (feat,), seen)
        elif isinstance(value, frozenset):
            for member in value:
                if isinstance(member, FStructure):
                    yield from _walk(member, path + (feat,), seen)


# === The three checks ====================================================

def lfg_well_formed(
    f: FStructure, ctree: CNode | None = None
) -> tuple[bool, list[Diagnostic]]:
    """Check completeness, coherence, and the subject condition over
    every PRED-bearing f-structure reachable from `f`. Returns
    ``(well_formed, diagnostics)``; ``well_formed`` is True iff
    ``diagnostics`` is empty (these checks emit only on failure).

    The `ctree` is accepted for the legacy signature but currently
    unused; the §4.5 follow-up will populate the diagnostic
    ``cnode_label`` field by keeping a node-id → c-node mapping.
    """
    diagnostics: list[Diagnostic] = []
    for node, path in _walk_fstructures(f):
        pred = node.feats.get("PRED")
        if not isinstance(pred, str):
            continue
        try:
            template = parse_pred_template(pred)
        except ValueError as e:
            diagnostics.append(Diagnostic(
                kind="parse-error",
                message=f"malformed PRED template: {e}",
                path=path,
                detail={"pred": pred},
            ))
            continue
        diagnostics.extend(_check_completeness(node, template, path))
        diagnostics.extend(_check_coherence(node, template, path))
        diagnostics.extend(_check_subject_condition(node, template, path))
    return (not diagnostics), diagnostics


def _check_completeness(
    f: FStructure, pred: PredTemplate, path: tuple[str, ...]
) -> list[Diagnostic]:
    out: list[Diagnostic] = []
    for gf in pred.governables:
        if gf not in f.feats:
            out.append(Diagnostic(
                kind="completeness-failed",
                message=(
                    f"PRED {pred.name!r} requires {gf!r} but it is not "
                    f"present in the f-structure"
                ),
                path=path,
                detail={"pred": pred.name, "missing": gf},
            ))
    return out


def _check_coherence(
    f: FStructure, pred: PredTemplate, path: tuple[str, ...]
) -> list[Diagnostic]:
    out: list[Diagnostic] = []
    args = set(pred.governables)
    for feat in f.feats:
        if feat == "PRED":
            continue
        if not is_governable_gf(feat):
            continue
        if feat not in args:
            out.append(Diagnostic(
                kind="coherence-failed",
                message=(
                    f"governable GF {feat!r} is present but PRED "
                    f"{pred.name!r} does not name it"
                ),
                path=path,
                detail={"pred": pred.name, "extra": feat},
            ))
    return out


def _check_subject_condition(
    f: FStructure, pred: PredTemplate, path: tuple[str, ...]
) -> list[Diagnostic]:
    # 0-ary predicates (the placeholder noun PRED, idiomatic
    # weather-verb-style 0-place predicates, etc.) are exempt; the
    # condition only fires when the predicate selects arguments.
    if not pred.governables:
        return []
    if "SUBJ" in f.feats:
        return []
    return [Diagnostic(
        kind="subject-condition-failed",
        message=(
            f"PRED {pred.name!r} has arguments but the f-structure has "
            f"no SUBJ"
        ),
        path=path,
        detail={"pred": pred.name},
    )]


__all__ = [
    "PredTemplate",
    "parse_pred_template",
    "is_governable_gf",
    "lfg_well_formed",
]
