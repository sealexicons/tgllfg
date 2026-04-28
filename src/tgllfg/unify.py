# tgllfg/unify.py

"""F-structure construction by equation evaluation.

This module is the §4.1 evaluator that walks the typed equation AST
produced by :mod:`tgllfg.equations`. The evaluation rules here match
the four equation shapes that the previous regex-based prototype
supported, so existing demos behave identically. Constraining,
existential, set-membership, negative, off-path, and multi-step
equations parse correctly but produce a diagnostic and no f-structure
update; proper unification with reentrancy and graph identity arrives
in §4.2.
"""

from __future__ import annotations

import itertools

from . import CNode, FStructure
from .equations import (
    Atom,
    DefiningEquation,
    Designator,
    Down,
    Equation,
    Feature,
    ParseError,
    Right,
    Up,
    parse_equation,
    unparse,
)

_id_counter = itertools.count(1)


def build_f_structure(root: CNode) -> FStructure:
    """Construct and return the f-structure for the given c-structure node."""
    f, _ = _build_f_for_node(root)
    return f


def _build_f_for_node(node: CNode) -> tuple[FStructure, list[str]]:
    """Recursively construct an f-structure for ``node``.

    Children are evaluated first, then the node-local equations apply.
    A ``(↑) = ↓i`` equation causes this node's f-structure to be
    replaced by the i-th child's; this preserves the prototype's
    "transparent" S-over-VP behaviour.
    """
    diags: list[str] = []

    child_fs: list[FStructure] = []
    for ch in node.children:
        ch_fs, ch_diags = _build_f_for_node(ch)
        child_fs.append(ch_fs)
        diags.extend(ch_diags)

    fs = FStructure(feats={}, id=next(_id_counter))
    up_equals_child_idx: int | None = None

    for eq_str in node.equations:
        try:
            eq = parse_equation(eq_str)
        except ParseError as e:
            diags.append(f"Parse error in equation {eq_str!r}: {e.message}")
            continue

        replace_idx = _evaluate_equation(eq, fs, child_fs, diags)
        if replace_idx is not None:
            up_equals_child_idx = replace_idx

    if up_equals_child_idx is not None:
        return child_fs[up_equals_child_idx], diags

    return fs, diags


def _evaluate_equation(
    eq: Equation,
    fs: FStructure,
    child_fs: list[FStructure],
    diags: list[str],
) -> int | None:
    """Apply one equation. Returns a child index when ``(↑) = ↓i`` should
    cause the caller to substitute this node's f-structure, else ``None``.
    """
    if not isinstance(eq, DefiningEquation):
        diags.append(
            f"§4.1 evaluator: equation form not yet implemented: {unparse(eq)}"
        )
        return None

    lhs, rhs = eq.lhs, eq.rhs

    if _has_unsupported_features(lhs):
        diags.append(
            f"§4.1 evaluator: regular-path/off-path features not yet implemented: "
            f"{unparse(eq)}"
        )
        return None
    if isinstance(rhs, Designator) and _has_unsupported_features(rhs):
        diags.append(
            f"§4.1 evaluator: regular-path/off-path features not yet implemented: "
            f"{unparse(eq)}"
        )
        return None

    if not isinstance(lhs.base, Up):
        diags.append(f"§4.1 evaluator: lhs must be rooted at ↑: {unparse(eq)}")
        return None

    # Form: (↑) = ↓i — promote the i-th child's f-structure.
    if (
        not lhs.path
        and isinstance(rhs, Designator)
        and isinstance(rhs.base, Down)
        and rhs.base.idx is not None
        and not rhs.path
    ):
        idx = rhs.base.idx - 1
        if 0 <= idx < len(child_fs):
            return idx
        diags.append(
            f"(↑)=↓{rhs.base.idx} child index out of range (have {len(child_fs)})"
        )
        return None

    # The remaining supported forms all have lhs of shape (↑ F).
    if len(lhs.path) != 1 or not isinstance(lhs.path[0], Feature):
        diags.append(
            f"§4.1 evaluator: only single-feature lhs paths are supported: "
            f"{unparse(eq)}"
        )
        return None
    feat_name = lhs.path[0].name

    # Form: (↑ F) = 'atom'
    if isinstance(rhs, Atom):
        fs.feats[feat_name] = rhs.value
        return None

    # rhs is a Designator: must be ↓i optionally followed by one feature.
    if not isinstance(rhs.base, Down) or rhs.base.idx is None:
        diags.append(
            f"§4.1 evaluator: rhs designator must be ↓i (1-based): {unparse(eq)}"
        )
        return None
    idx = rhs.base.idx - 1
    if not (0 <= idx < len(child_fs)):
        diags.append(
            f"§4.1 evaluator: child index ↓{rhs.base.idx} out of range "
            f"(have {len(child_fs)})"
        )
        return None

    # Form: (↑ F) = ↓i  — bind the child's f-structure as the value.
    if not rhs.path:
        # Prototype-style reentrancy via dict aliasing. Real reentrancy
        # via node identity arrives in §4.2.
        fs.feats[feat_name] = child_fs[idx].feats
        return None

    # Form: (↑ F) = ↓i F'  — copy a single attribute up.
    if len(rhs.path) == 1 and isinstance(rhs.path[0], Feature):
        rhs_feat = rhs.path[0].name
        fs.feats[feat_name] = child_fs[idx].feats.get(rhs_feat)
        return None

    diags.append(
        f"§4.1 evaluator: only single-feature rhs paths are supported: "
        f"{unparse(eq)}"
    )
    return None


def _has_unsupported_features(d: Designator) -> bool:
    """True if the designator uses constructs the §4.1 evaluator can't
    handle: the → metavariable, regular-path operators, alternation, or
    off-path constraints."""
    if isinstance(d.base, Right):
        return True
    for elem in d.path:
        if not isinstance(elem, Feature):
            return True
        if elem.off_path:
            return True
    return False
