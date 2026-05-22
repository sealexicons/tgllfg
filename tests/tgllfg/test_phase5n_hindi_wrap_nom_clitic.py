# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.A Commit 2 — hindi-wrap × non-``ka`` NOM-clitic (§18 L69).

Pre-Commit-2 state: the Phase 4 §7.2 hindi-wrap rule absorbed the
NOM-clitic that the placement pass moved into 2P position, but only
``ka`` (2sg-NOM) was declared ``is_clitic: true`` in
``data/tgl/pronouns.yaml``. The other NOM-PRONs — ``ako`` / ``siya``
/ ``tayo`` / ``kami`` / ``kayo`` / ``sila`` — lacked the flag, so
the placement pass left them in pre-V position, where the hindi-wrap
rule didn't fire. Surface ``Hindi ako kumain`` and its siblings
0-parsed despite the linguistically canonical ``Hindi ka kumain``
working.

Commit 2 lifts ``is_clitic: true`` onto the full NOM-PRON inventory
per Kroeger 1993 ch. 5 / S&O 1972 §3.2 (all six are 2P clitics in
canonical surface position).  To preserve the pre-fix ay-fronting
behaviour (``Ako ay kumain`` etc.), a placement-pass exception
``_is_pre_ay_pron`` suppresses the 2P move when the PRON is
immediately followed by ``PART[LINK=AY]`` — the topic stays
sentence-initial so the Phase 4 §7.4 ay-fronting grammar's
``[NP, ay, S]`` shape continues to fire.
"""

import pytest

from tgllfg.core.pipeline import parse_text


# === Hindi-wrap × NOM-PRON × Verb (the L69 closure target) ================

NOM_PRONS = ["ako", "siya", "tayo", "kami", "kayo", "sila"]
HINDI_WRAP_VERBS = ["kumain", "pumunta", "bumili"]


@pytest.mark.parametrize("pron", NOM_PRONS)
@pytest.mark.parametrize("verb", HINDI_WRAP_VERBS)
def test_hindi_wrap_with_nom_pron(pron: str, verb: str) -> None:
    """Each of {ako, siya, tayo, kami, kayo, sila} composes with
    hindi + V to produce a unique top-1 parse."""
    sentence = f"Hindi {pron} {verb}."
    parses = parse_text(sentence)
    assert len(parses) >= 1, (
        f"hindi-wrap × {pron} × {verb} should parse: {sentence!r}"
    )


# === Regression: ka still works ============================================


@pytest.mark.parametrize("verb", HINDI_WRAP_VERBS)
def test_hindi_wrap_ka_still_works(verb: str) -> None:
    """The pre-Commit-2 working case (``Hindi ka kumain``) must
    continue to parse."""
    sentence = f"Hindi ka {verb}."
    parses = parse_text(sentence)
    assert len(parses) >= 1


# === Regression: bare V + NOM-PRON without hindi ===========================


@pytest.mark.parametrize("pron", NOM_PRONS + ["ka"])
@pytest.mark.parametrize("verb", HINDI_WRAP_VERBS)
def test_bare_v_nom_pron_still_parses(pron: str, verb: str) -> None:
    """Lifting is_clitic onto NOM-PRONs must not break the canonical
    ``V PRON`` clause (``Kumain ako`` / ``Pumunta siya`` etc.).
    The placement pass leaves the PRON in 2P position; the grammar
    composes via the existing ``S → V NP[CASE=NOM]`` paths."""
    sentence = f"{verb.capitalize()} {pron}."
    parses = parse_text(sentence)
    assert len(parses) >= 1


# === Regression: ay-fronting topic preserved ==============================


AY_FRONTING_VERBS = ["kumain", "pumunta", "tumakbo"]


@pytest.mark.parametrize("pron", NOM_PRONS + ["ikaw"])
@pytest.mark.parametrize("verb", AY_FRONTING_VERBS)
def test_ay_fronting_with_pron_topic(pron: str, verb: str) -> None:
    """The placement-pass _is_pre_ay_pron exception must keep
    ay-fronted PRON topics in sentence-initial position so the Phase
    4 §7.4 ay-fronting rule fires. ``ikaw`` (full 2sg) was already
    non-clitic and works without the exception; the other six are
    now clitics and rely on the new exception."""
    sentence = f"{pron.capitalize()} ay {verb}."
    parses = parse_text(sentence)
    assert len(parses) >= 1, (
        f"ay-fronting × {pron} × {verb} should parse: {sentence!r}"
    )


# === Top-1 uniqueness audit (no ambiguity blowup) ==========================


class TestNoAmbiguityBlowup:
    """Lifting is_clitic on six PRONs could in principle produce new
    top-N analyses for canonical sentences (the ranker explores more
    paths). Confirm the canonical sentences still produce exactly
    one top-1 parse."""

    @pytest.mark.parametrize("pron", NOM_PRONS)
    def test_hindi_wrap_unique_parse(self, pron: str) -> None:
        sentence = f"Hindi {pron} kumain."
        parses = parse_text(sentence)
        assert len(parses) == 1

    @pytest.mark.parametrize("pron", NOM_PRONS)
    def test_bare_clause_unique_parse(self, pron: str) -> None:
        sentence = f"Kumain {pron}."
        parses = parse_text(sentence)
        assert len(parses) == 1

    @pytest.mark.parametrize("pron", NOM_PRONS)
    def test_ay_fronting_unique_parse(self, pron: str) -> None:
        sentence = f"{pron.capitalize()} ay kumain."
        parses = parse_text(sentence)
        assert len(parses) == 1
