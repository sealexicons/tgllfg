# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

# tgllfg/fstruct/__init__.py

from .checks import (
    PredTemplate,
    is_governable_gf,
    lfg_well_formed,
    parse_pred_template,
)
from .equations import (
    AltFeature,
    Atom,
    Base,
    ConstrainingEquation,
    DefiningEquation,
    Designator,
    Down,
    Equation,
    ExistentialConstraint,
    Feature,
    NegEquation,
    NegExistentialConstraint,
    ParseError,
    PathElement,
    PlusAltFeature,
    PlusFeature,
    Right,
    SetMembership,
    StarAltFeature,
    StarFeature,
    Up,
    Value,
    parse_equation,
    unparse,
)
from .graph import (
    NON_BLOCKING_KINDS,
    AtomValue,
    ComplexValue,
    DiagKind,
    Diagnostic,
    FGraph,
    FValue,
    NodeId,
    SetValue,
    Snapshot,
)
from .fu import (
    resolve_regex_for_read,
)
from .unify import (
    SolveResult,
    build_f_structure,
    precheck_defining_subtree,
    solve,
)

__all__ = [
    # equations AST
    "AltFeature",
    "Atom",
    "Base",
    "ConstrainingEquation",
    "DefiningEquation",
    "Designator",
    "Down",
    "Equation",
    "ExistentialConstraint",
    "Feature",
    "NegEquation",
    "NegExistentialConstraint",
    "ParseError",
    "PathElement",
    "PlusAltFeature",
    "PlusFeature",
    "Right",
    "SetMembership",
    "StarAltFeature",
    "StarFeature",
    "Up",
    "Value",
    "parse_equation",
    "unparse",
    # graph
    "AtomValue",
    "ComplexValue",
    "DiagKind",
    "Diagnostic",
    "FGraph",
    "FValue",
    "NodeId",
    "NON_BLOCKING_KINDS",
    "SetValue",
    "Snapshot",
    # unifier orchestration
    "SolveResult",
    "build_f_structure",
    "precheck_defining_subtree",
    "solve",
    # FU evaluation (Phase 6.B)
    "resolve_regex_for_read",
    # well-formedness
    "PredTemplate",
    "is_governable_gf",
    "lfg_well_formed",
    "parse_pred_template",
]
