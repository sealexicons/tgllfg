"""Phase 5n.A Commit 14 — OV embedded V under modal (§18 L72).

Pre-Commit-14 the OV paradigm cells produced only the standard
finite forms (PFV ``kinain``, IPFV ``kinakain``, CTPL ``kakainin``
with CV-redup). The bare-stem ``kainin`` form (``kain + -in``,
no redup) was not generated, so canonical Tagalog imperative /
modal-XCOMP sentences like ``Maaari mong kainin ang isda.`` "I can
eat the fish" 0-parsed.

Phase 5n.A Commit 14 adds the missing bare-OV paradigm cell to
``data/tgl/paradigms.yaml``:

    voice: OV
    aspect: CTPL
    mood: SOC
    transitivity: TR
    affix_class: in_oblig
    operations: [{op: suffix, value: in}]
    feats: {MOOD: SOC}

Mirrors the AV-mag SOC bare-hortative cell (Phase 5e Commit 21):
no CV-redup, no realis infix, just the ``-in`` suffix on the bare
root. The MOOD=SOC tag distinguishes the bare-hortative reading
from the standard CTPL.

Generated surfaces span the existing OV roots:

* ``kain`` (consonant-final) → ``kainin``
* ``bili`` (vowel-final i + h-epenthesis) → ``bilihin``
* ``inom`` (consonant-final + o→u raising) → ``inumin``
* ``gawa`` (vowel-final a + h-epenthesis) → ``gawahin``

Distribution: imperatives (``Kainin mo!`` "Eat it!"), modal-XCOMP
contexts (``Maaari mong kainin ang isda.``), and other dependent
positions where the matrix carries aspect/mood semantics.

The colloquial high-vowel-deletion variants (``bilhin`` for
``bili``, ``gawin`` for ``gawa``) are separate sandhi paths —
deferred until corpus pressure.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import Token
from tgllfg.core.pipeline import parse_text
from tgllfg.morph import Analyzer


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === Bare-OV paradigm surfaces ============================================


BARE_OV_FORMS = [
    # (root, expected bare-OV surface)
    ("kain",  "kainin"),
    ("bili",  "bilihin"),
    ("inom",  "inumin"),
    ("gawa",  "gawahin"),
]


class TestBareOvParadigmSurfaces:
    """Each existing OV root produces the bare-stem form via the
    new SOC cell."""

    @pytest.mark.parametrize("root,surface", BARE_OV_FORMS)
    def test_bare_ov_surface_indexed(
        self, root: str, surface: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        verbs = [
            a for a in out
            if a.pos == "VERB"
            and a.lemma == root
            and a.feats.get("VOICE") == "OV"
        ]
        assert verbs, (
            f"expected VERB[lemma={root}, VOICE=OV] for {surface!r}; "
            f"got {[(a.pos, a.lemma) for a in out]}"
        )

    @pytest.mark.parametrize("root,surface", BARE_OV_FORMS)
    def test_bare_ov_carries_soc_mood(
        self, root: str, surface: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        soc_verbs = [
            a for a in out
            if a.pos == "VERB"
            and a.lemma == root
            and a.feats.get("VOICE") == "OV"
            and a.feats.get("MOOD") == "SOC"
        ]
        assert soc_verbs, (
            f"{surface!r} should carry MOOD=SOC for the bare-OV cell"
        )


# === Modal + bare-OV + ang-NP =============================================


class TestModalWithBareOv:
    """The L72 canonical pattern + variants across modals and roots."""

    @pytest.mark.parametrize("sentence", [
        # Canonical L72 target:
        "Maaari mong kainin ang isda.",
        # Across modals:
        "Puwede mong kainin ang isda.",
        "Dapat mong kainin ang isda.",
        "Kailangan mong kainin ang isda.",
        # Across OV roots:
        "Maaari mong bilihin ang isda.",
        "Maaari mong inumin ang gatas.",
        "Maaari mong gawahin ang trabaho.",
    ])
    def test_modal_with_bare_ov(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === Standalone OV imperatives (bonus from new cell) ======================


class TestBareOvImperatives:
    """The new bare-OV cell also enables the canonical OV imperative
    pattern (no modal): ``Kainin mo!`` "Eat it!" composes directly
    via the existing OV S-frame rules."""

    @pytest.mark.parametrize("sentence", [
        "Kainin mo ang isda.",
        "Bilihin mo ang isda.",
        "Inumin mo ang gatas.",
    ])
    def test_bare_ov_imperative(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === Standard OV regression ===============================================


class TestStandardOvRegression:
    """The existing OV PFV/IPFV/CTPL paradigm cells must continue
    to fire — Commit 14 only adds the SOC variant."""

    @pytest.mark.parametrize("sentence", [
        "Kinain ng bata ang isda.",          # OV PFV
        "Kinakain ng bata ang isda.",        # OV IPFV
        "Kakainin ng bata ang isda.",        # OV CTPL (with redup)
        "Bibilihin ng bata ang isda.",       # OV CTPL bili
    ])
    def test_standard_ov_still_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
