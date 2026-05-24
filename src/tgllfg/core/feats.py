# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Catalogue of f-structure feats by value-shape.

``BINARY_FEATS`` is the set of feat names that carry strictly
boolean values — i.e., the only meaningful values are
"true" and "false" (currently encoded as the string sentinels
``"YES"`` / ``"NO"``; Phase 5n.C.4 migrates to Python ``bool``).

The set is consumed by:

* the grammar compiler (``tgllfg.cfg.compile``) to license the
  ``[X]`` shorthand for ``[X=true]`` only on binary feats,
* the YAML loader (``tgllfg.morph.loader``) and tests, to validate
  that ``YES`` / ``NO`` (or ``true`` / ``false``) only appear under
  feats in this set.

Enum-valued feats (e.g., ``PRED``, ``INDEF``, ``Q_TYPE``, ``CASE``,
``NUM``) are *not* in this set even when they happen to take ``YES``
as one of their enum values. See ``docs/feats-binary-audit.md`` for
the full audit and the migration plan.
"""

BINARY_FEATS: frozenset[str] = frozenset(
    {
        "APPROX",
        "ASK_CLASS",
        "AV_ABSOL",
        "CARDINAL",
        "CF",
        "CLOCK_MARKER",
        "COMPARATIVE",
        "COPULA",
        "CORREL",
        "COUNTERFACTUAL",
        "DECIMAL",
        "DECIMAL_SEP",
        "DEM",
        "DEPICTIVE",
        "DIGIT_FORM",
        "DISCOURSE_EMPH",
        "DISTRIB",
        "DISTRIB_POSS",
        "DUAL",
        "ELLIPSIS",
        "EMPHATIC",
        "EQUATIVE",
        "EXISTENTIAL",
        "EXTRACTED",
        "FOCUS_NEG",
        "FRAGMENT_HOST",
        "FREE_REL",
        "GAPPING",
        "HAVE",
        "HUMAN",
        "IMPERSONAL",
        "INTENSIFIER",
        "INTERJ",
        "KA_PRED",
        "KASING_N",
        "KITA",
        "LOC_EXISTENTIAL",
        "MAGISA",
        "MEASURE",
        "MGA_INTERNAL",
        "MIRATIVE",
        "MODAL",
        "MODAL_STANDALONE",
        "N_RC",
        "NEG_TAG",
        "ORDINAL",
        "ORTHOGRAPHIC_TERMINATOR",
        "POLITE_MARKER",
        "PANG_DERIVED",
        "PLURAL_MARKER",
        "PREDICATIVE",
        "QUESTION",
        "RECP",
        "RESULTATIVE",
        "SAY_CLASS",
        "SEQUENCE",
        "STATIVE_PRED",
        "SYMBOLIC",
        "UNCERTAIN",
        "UNIV",
        "VAGUE",
        "WH",
        "WHOLE",
    }
)


__all__ = ["BINARY_FEATS"]
