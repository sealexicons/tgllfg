# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.C.4 Commit 2 — BINARY_FEATS audit sanity tests.

Guards the ``BINARY_FEATS`` allowlist against accidental drift: known
binary feats stay in, known enum feats stay out. The full audit lives
at ``docs/feats-binary-audit.md``.
"""

import pytest

from tgllfg.core.feats import BINARY_FEATS


_KNOWN_BINARY = (
    "WH",
    "CARDINAL",
    "DISTRIB",
    "DUAL",
    "QUESTION",
    "HUMAN",
    "KITA",
    "MIRATIVE",
    "PANG_DERIVED",
    "RESULTATIVE",
    "COUNTERFACTUAL",
    "EQUATIVE",
    "EXCLAM",
)

_KNOWN_ENUM = (
    "PRED",       # LFG predicate name; takes literal predicate strings
    "INDEF",      # enum: YES | NEG_INDEF
    "Q_TYPE",     # enum: YES_NO | WH | TAG
    "NUM",        # enum: SG | PL | DU
    "CASE",       # enum: NOM | GEN | DAT
    "ASPECT",     # enum: PFV | IPFV | PROSP | IRR
    "MOOD",       # enum: IND | IMP | SUB | SOC
    "VOICE",      # enum: AV | OV | DV | IV | BV | LV
    "REGISTER",   # enum: POLITE | COLLOQUIAL_POLITE | LITERARY
    "CARDINAL_VALUE",  # numeric-string payload
    "REDUP",      # enum: FULL | (CV reserved for future)  — Phase 10.B
    "REDUP_SEM",  # enum: DISTR | FREQ | QUANT | ITER | ATTEN | INTENS | CASUAL — Phase 10.B/10.D/10.E.3.post-1
)


@pytest.mark.parametrize("feat", _KNOWN_BINARY)
def test_known_binary_feats_are_listed(feat: str) -> None:
    assert feat in BINARY_FEATS, (
        f"{feat!r} is documented as binary but missing from "
        f"BINARY_FEATS — see docs/feats-binary-audit.md"
    )


@pytest.mark.parametrize("feat", _KNOWN_ENUM)
def test_known_enum_feats_are_excluded(feat: str) -> None:
    assert feat not in BINARY_FEATS, (
        f"{feat!r} is documented as enum but appears in BINARY_FEATS "
        f"— the migration would corrupt its enum semantics"
    )


def test_binary_feats_count_matches_audit() -> None:
    """The audit doc said 55 binary feats. Phase 9.O.3 adds
    ``STATIVE_PRED`` → 56. Phase 9.O.4 adds ``AV_ABSOL`` → 57.
    Phase 9.O.5 adds ``POLITE_MARKER`` → 58. Phase 9.X.c11 adds
    ``MGA_INTERNAL`` → 59. Phase 9.X.c19 adds ``KA_PRED`` → 60.
    Phase 9.X.c22 adds ``ELLIPSIS`` → 61. Phase 9.X.c49 adds
    ``IMPERSONAL`` → 62. Phase 9.X.post-2 adds ``COPULA`` → 63.
    Phase 10.E.1 adds ``EXCLAM`` → 64. Phase 10.G adds
    ``LEXICALIZED`` → 65. Phase 10.J.post-8.5.2 adds
    ``DISPOSITION`` → 66 (ma-X-in dispositional ADJ cell).
    Phase 10.J.post-8.5.5 adds ``COLLABORATIVE`` → 67
    (v_collab_redup cell — tulong → tulung-tulong).
    Drift means update both the doc and this assertion together."""
    assert len(BINARY_FEATS) == 67, (
        f"BINARY_FEATS has {len(BINARY_FEATS)} entries; "
        f"docs/feats-binary-audit.md says 67. "
        f"Update both together if the audit changes."
    )


def test_binary_feats_all_upper_underscore() -> None:
    for feat in BINARY_FEATS:
        assert feat.isupper() or "_" in feat, feat
        assert feat.replace("_", "").isalnum(), feat
