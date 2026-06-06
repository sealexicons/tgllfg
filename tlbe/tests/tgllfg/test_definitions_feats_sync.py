# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 12.final: definitions.md documents every binary feat.

``docs/definitions.md`` is the source of truth for feat glosses; this
gate asserts every atom in ``core/feats.py:BINARY_FEATS`` appears as a
table-row key (``| FEAT |``) there, so a feat added to the registry
without a glossary entry fails CI. The complementary
``test_phase5n_c4_feats_audit`` gates the binary-vs-enum *count* in
``feats-binary-audit.md``.
"""

from pathlib import Path

from tgllfg.core.feats import BINARY_FEATS

_DEFINITIONS = Path(__file__).resolve().parents[2] / "docs" / "definitions.md"


def test_every_binary_feat_documented() -> None:
    text = _DEFINITIONS.read_text(encoding="utf-8")
    missing = sorted(
        f for f in BINARY_FEATS
        if f"| {f} |" not in text and f"| `{f}` |" not in text
    )
    assert not missing, (
        "docs/definitions.md (the feat source of truth) is missing "
        f"glossary entries for: {missing}"
    )
