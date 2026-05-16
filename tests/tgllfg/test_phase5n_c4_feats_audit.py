"""Phase 5n.C.4 Commit 2 — BINARY_FEATS audit sanity tests.

Guards the ``BINARY_FEATS`` allowlist against accidental drift: known
binary feats stay in, known enum feats stay out. The full audit lives
at ``docs/feats-binary-audit.md``.
"""

from __future__ import annotations

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
    """The audit doc says 53 binary feats. Drift means update both
    the doc and this assertion together."""
    assert len(BINARY_FEATS) == 53, (
        f"BINARY_FEATS has {len(BINARY_FEATS)} entries; "
        f"docs/feats-binary-audit.md says 53. "
        f"Update both together if the audit changes."
    )


def test_binary_feats_all_upper_underscore() -> None:
    for feat in BINARY_FEATS:
        assert feat.isupper() or "_" in feat, feat
        assert feat.replace("_", "").isalnum(), feat
