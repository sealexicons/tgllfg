# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-12.14: comma closes an embedded RC for clitic-anchor
purposes.

Regression guard for the ``_enclosing_anchor_for_clitic`` comma-reset
fix that closes PANAHON/sent-36 (``Puno pa rin ang mga patubigan sa
bukid kaya pagkaani ng palay na itinanim noong Hunyo, sisimulan na ang
ikalawang pagtatanim.``).

Pre-fix behavior: a 2P clitic (``na`` / ``rin`` / ``ba`` / ``nga``)
appearing in a post-comma main clause was mis-routed by
``_enclosing_anchor_for_clitic`` to a V inside the just-closed
pre-comma RC. Specifically, when matrix_anchor was an earlier V (e.g.,
``kaya`` PSYCH-VERB reading) and an intervening ``na``-linker opened
an inner RC, the function left ``last_boundary`` pointing inside the
RC even when a comma had subsequently closed the RC. The clitic was
then queued as an inner-adv clitic and flushed at the comma — placing
it *inside* the closed RC, breaking the chart's RC + comma + S
structure.

Post-fix behavior: a comma between the linker and the candidate clitic
resets ``last_boundary``. The function falls back to the matrix anchor
(or whatever the post-comma context resolves to), the clitic anchors
correctly to the matrix, and ``reorder_clitics`` places it at
clause-final via the ``S → S PART[CLITIC_CLASS=2P]`` rule.
"""

import pytest

from tgllfg.core.pipeline import parse_text_with_fragments


@pytest.mark.parametrize("sent", [
    # PANAHON/sent-36 target
    "Puno pa rin ang mga patubigan sa bukid kaya pagkaani ng palay "
    "na itinanim noong Hunyo, sisimulan na ang ikalawang pagtatanim.",
    # Same shape with each 2P clitic
    "Puno ang patubigan kaya pagkaani ng palay na itinanim, "
    "sisimulan na ang pagtatanim.",
    "Puno ang patubigan kaya pagkaani ng palay na itinanim, "
    "sisimulan rin ang pagtatanim.",
    "Puno ang patubigan kaya pagkaani ng palay na itinanim, "
    "sisimulan nga ang pagtatanim.",
    "Puno ang patubigan kaya pagkaani ng palay na itinanim, "
    "sisimulan ba ang pagtatanim.",
])
def test_comma_closes_rc_for_clitic_anchor(sent: str) -> None:
    r = parse_text_with_fragments(sent, max_tree_iterations=5000)
    assert len(r.parses) >= 1, (
        f"Expected ≥1 parse for {sent!r}; got {len(r.parses)}"
    )


@pytest.mark.parametrize("sent", [
    # Working baselines — no RC, no clitic, isolated cases
    # — all already worked pre-fix; serve as anti-regression for the
    # un-affected paths.
    "Puno ang patubigan kaya pagkaani ng palay, sisimulan na ang "
    "pagtatanim.",
    "Pagkaani ng palay na itinanim noong Hunyo, sisimulan na ang "
    "ikalawang pagtatanim.",
    "Puno ang patubigan kaya pagkaani ng palay na itinanim noong "
    "Hunyo, sisimulan ang pagtatanim.",
])
def test_comma_boundary_no_regression_pre_fix_working(sent: str) -> None:
    r = parse_text_with_fragments(sent, max_tree_iterations=5000)
    assert len(r.parses) >= 1, (
        f"Expected ≥1 parse for {sent!r}; got {len(r.parses)}"
    )
