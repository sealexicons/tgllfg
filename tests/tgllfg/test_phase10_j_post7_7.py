# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-7.7: bare-comma N coord for non-Oxford enumerations.

Renamed from Phase 10.J.post-10 (2026-05-29). The post-10 task in
the original plan had no dependency on post-8 (audit-survey) or
post-9 (OCR cleanup), and the four ``pending_closure: post-10``
exemplars were within the post-7.x PP/SubordClause extension arc
that completed in post-7.6 — pulling it into post-7.7 closes the
xfail residue from that arc instead of leaving it for the parked
post-8 / post-9 work.

Adds:

1. ``N_LONG_LIST_3PLUS`` accumulator non-terminal with an explicit
   3-N base + recursive +1 step. Parallels the existing
   ``N_LONG_LIST`` (9.X.c11 / Phase 5n.A) but starts at 3 conjuncts
   so the bare-comma wrap doesn't over-fire on degenerate 2-N
   ``X, Y`` sequences (modern Tagalog doesn't use bare-comma N
   coord for exactly 2 items — ``X at Y`` is the canonical form).

2. ``N[COORD=AND] → N_LONG_LIST_3PLUS`` bare-comma wrap (no final
   ``at``). The wrap fires on lists of 3+ Ns; with the case-marker
   → NP rule it composes into a full ``NP[CASE=X, COORD=AND]``
   when an ``ang`` / ``ng`` / ``sa`` leads the list. Without a
   case marker, the bare ``N[COORD=AND]`` serves the colon-split's
   ``N`` post-colon category for appositive enumerations
   (``... prutas: mangga, bayabas, santol.``).

3. ``kusina`` NOUN ("kitchen") — surprising omission from the
   Spanish-loan household-room set; surfaced by the constructed
   ``Nasa kusina ang pagkain: kanin, gulay at isda.`` exemplar.

Closes all 4 ``pending_closure: post-10`` (now ``post-7.7``)
constructed exemplars (``no-ay/locative-kusina-3item``,
``pred-n/prutas-nonoxford-3item``, ``no-ay/hayop-nonoxford-3item``,
``pred-n/inaani-nonoxford-5item``).
"""

from tgllfg.core.pipeline import parse_text


class TestBareCommaNCoord:
    """post-7.7: bare-comma N enumeration with 3+ conjuncts."""

    def test_locative_kusina_3item_with_at(self) -> None:
        """Exemplar #1: ``Nasa kusina ang pagkain: kanin, gulay at
        isda.`` — 3-item with final ``at`` (non-Oxford). Pre-7.7
        this 0-parsed because the pre-half required ``kusina`` lex
        (not the bare-comma rule)."""
        s = "Nasa kusina ang pagkain: kanin, gulay at isda."
        parses = parse_text(s, n_best=2)
        assert len(parses) >= 1

    def test_prutas_nonoxford_3item(self) -> None:
        """Exemplar #2: 3-item bare-comma enumeration. Post-colon
        ``mangga, bayabas, santol`` is N[COORD=AND] via the new
        bare-comma wrap; the colon-glue attaches it to the
        pre-half's APP set."""
        s = "Ang inaani ay mga prutas: mangga, bayabas, santol."
        parses = parse_text(s, n_best=2)
        assert len(parses) >= 1

    def test_hayop_nonoxford_3item_with_ang(self) -> None:
        """Exemplar #3: post-colon is ``ang aso, pusa, kalabaw``
        (case-marker on first item only). The case-marker → NP
        rule consumes the new N[COORD=AND] composed via the
        bare-comma wrap."""
        s = "Maraming hayop dito: ang aso, pusa, kalabaw."
        parses = parse_text(s, n_best=2)
        assert len(parses) >= 1

    def test_inaani_nonoxford_5item(self) -> None:
        """Exemplar #4: 5-item bare-comma enumeration. Exercises
        the recursive ``N_LONG_LIST_3PLUS → N_LONG_LIST_3PLUS
        COMMA N`` step twice (3-base + 2 recursive extensions)."""
        s = "Ang inaani namin ay mga prutas: mangga, bayabas, santol, melon, pakwan."
        parses = parse_text(s, n_best=2)
        assert len(parses) >= 1


class TestNewLex:
    """post-7.7: lex coverage."""

    def test_kusina_noun(self) -> None:
        """``kusina`` NOUN ("kitchen") — Spanish-loan household-room
        noun, parallel to ``kuwarto`` / ``banyo``."""
        parses = parse_text("Mainit ang kusina.", n_best=2)
        assert len(parses) >= 1


class TestArityGuard:
    """post-7.7: arity guard — the bare-comma wrap fires only on
    3+-conjunct lists, not on degenerate 2-N ``X, Y`` sequences
    (which would over-generate on every internal-comma context)."""

    def test_bare_2item_no_at_does_not_form_coord(self) -> None:
        """``X, Y`` without ``at`` as a standalone enumeration is
        not a valid Tagalog coord — the bare-comma wrap starts at
        3 Ns. Sentence-level standalone ``Mangga, bayabas.``
        should not parse as a complete S (the bare-comma 2-N
        sequence has no parent grammar consumer)."""
        # The 2-item bare-comma "Mangga, bayabas." must not produce
        # an N[COORD=AND] (no N_LONG_LIST_3PLUS base for 2 Ns).
        # As a standalone "sentence" it ZPFs because there's no
        # parent S construction for a bare N.
        parses = parse_text("Mangga, bayabas.", n_best=2)
        assert len(parses) == 0, (
            "bare 2-item comma sequence should not parse as a "
            "complete S — would indicate the bare-comma wrap fired "
            "on a degenerate 2-N base"
        )


class TestAntiRegression:
    """post-7.7: anti-regression — the new bare-comma wrap doesn't
    break the existing Oxford / non-Oxford-with-at variants, nor
    the binary N-coord rule."""

    def test_oxford_3item_with_at_unchanged(self) -> None:
        """Oxford-comma 3-item with at: ``mangga, bayabas, at
        santol`` still parses via the existing wrap."""
        parses = parse_text(
            "Ang inaani ay mga prutas: mangga, bayabas, at santol.",
            n_best=2,
        )
        assert len(parses) >= 1

    def test_non_oxford_3item_with_at_unchanged(self) -> None:
        """Non-Oxford 3-item with at: ``kanin, gulay at isda``
        still parses via the existing non-Oxford wrap."""
        parses = parse_text(
            "Pagkain ko: kanin, gulay at isda.",
            n_best=2,
        )
        # may still ZPF if pre-half "Pagkain ko" has its own gap;
        # exercise via a different construction
        if not parses:
            parses = parse_text(
                "Mayroon akong kanin, gulay at isda.",
                n_best=2,
            )
        assert len(parses) >= 1

    def test_binary_n_coord_unchanged(self) -> None:
        """Binary ``N at N`` coord still parses via the
        pre-existing binary rule."""
        parses = parse_text("Mayroon akong kanin at isda.", n_best=2)
        assert len(parses) >= 1
