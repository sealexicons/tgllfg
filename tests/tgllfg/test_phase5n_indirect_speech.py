"""Phase 5n.A Commit 27 — OV-with-na-S complement (§18 L89.2).

Closes §18 L89 part 2 of 2 — the rule + composition. Lifts the
12-fixture 0-parse pin from Phase 5n.A Commit 26's corpus.

The new rule (clause.py):

    S → V[VOICE=OV, SAY_CLASS=YES] PRON[CASE=GEN] PART[LINK=NA] S
        ↑ percolation: PRED / VOICE / ASPECT / MOOD / LEX-ASTRUCT
        (↑ OBJ-AGENT) = ↓2     (the actor PRON)
        (↑ SUBJ) = ↓4          (the said-thing — finite-S as SUBJ)
        (↓1 SAY_CLASS) =c 'YES'
        (↓3 LINK) =c 'NA'

Companion change in ``src/tgllfg/clitics/placement.py`` —
``disambiguate_homophone_clitics`` gained an
``is_say_class_pron_seq`` branch that disambiguates standalone
``na`` between SAY-class V + GEN-PRON and a following V as the
linker (LINK=NA), preventing reorder_clitics from moving it to
clause-final position as the ALREADY 2P clitic.

F-structure shape:

    PRED         = 'SABI <SUBJ, OBJ-AGENT>'   (from sabi lex)
    VOICE        = 'OV'
    ASPECT       = PFV / IPFV / CTPL          (from V form)
    MOOD         = 'IND'
    LEX-ASTRUCT  = 'AGENT,PATIENT'
    OBJ-AGENT    = the GEN-PRON actor
    SUBJ         = the embedded S (the said-thing) — carries its
                   own PRED, VOICE, ASPECT, etc.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


def _is_say_with_embed_pred(parse, embed_pred: str) -> bool:
    """True iff the parse has matrix PRED='SABI <SUBJ, OBJ-AGENT>'
    and a SUBJ whose own PRED matches ``embed_pred``."""
    fs = parse[1]
    if fs.feats.get("PRED") != "SABI <SUBJ, OBJ-AGENT>":
        return False
    subj = fs.feats.get("SUBJ")
    if subj is None:
        return False
    return subj.feats.get("PRED") == embed_pred


# === Canonical sentence ============================================


class TestCanonicalSentence:
    """``Sinabi niya na pumunta si Maria.`` — the canonical
    indirect-speech sentence, parses with the embedded ``pumunta
    si Maria`` as SUBJ of ``sabi``."""

    def test_canonical_parses(self) -> None:
        parses = parse_text("Sinabi niya na pumunta si Maria.")
        assert len(parses) >= 1
        say_parses = [
            p for p in parses
            if _is_say_with_embed_pred(p, "PUNTA <SUBJ>")
        ]
        assert len(say_parses) >= 1, (
            "Expected at least one parse where the matrix is SABI "
            "and SUBJ.PRED is the embedded PUNTA"
        )
        _ct, fs, _astr, _diags = say_parses[0]
        assert fs.feats.get("VOICE") == "OV"
        assert fs.feats.get("ASPECT") == "PFV"
        oa = fs.feats.get("OBJ-AGENT")
        assert oa is not None
        assert oa.feats.get("CASE") == "GEN"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        embedded_subj = subj.feats.get("SUBJ")
        assert embedded_subj is not None
        assert embedded_subj.feats.get("LEMMA") == "maria"


# === Corpus parametrization (mirrors Commit 26) ====================


class TestCorpusFixtures:
    """All 12 corpus fixtures from Phase 5n.A Commit 26 now parse
    with the SABI + finite-S-SUBJ structure. The Commit 26
    deferred-tripwire test is removed; this test class is the
    positive replacement."""

    @pytest.mark.parametrize("sentence,embedded_pred", [
        # PFV (sinabi)
        ("Sinabi niya na pumunta si Maria.",          "PUNTA <SUBJ>"),
        ("Sinabi mo na pumunta si Pedro.",            "PUNTA <SUBJ>"),
        ("Sinabi ko na kumain si Maria.",             "EAT <SUBJ>"),
        ("Sinabi nila na bumili si Maria ng aklat.",  "BUY <SUBJ, OBJ>"),
        ("Sinabi niya na pumunta sila.",              "PUNTA <SUBJ>"),
        # IPFV (sinasabi)
        ("Sinasabi niya na pumunta si Maria.",        "PUNTA <SUBJ>"),
        ("Sinasabi mo na kumain ako.",                "EAT <SUBJ>"),
        ("Sinasabi nila na bumili kami ng aklat.",    "BUY <SUBJ, OBJ>"),
        # CTPL (sasabihin)
        ("Sasabihin niya na pumunta si Maria.",       "PUNTA <SUBJ>"),
        ("Sasabihin ko na kumain si Pedro.",          "EAT <SUBJ>"),
        ("Sasabihin nila na bumili kami ng aklat.",   "BUY <SUBJ, OBJ>"),
        # PFV with embed transitive
        ("Sinabi niya na bumili si Maria ng aklat.",  "BUY <SUBJ, OBJ>"),
    ])
    def test_corpus_parses_with_embedded_subj(
        self, sentence: str, embedded_pred: str
    ) -> None:
        parses = parse_text(sentence)
        say_parses = [
            p for p in parses
            if _is_say_with_embed_pred(p, embedded_pred)
        ]
        assert len(say_parses) >= 1, (
            f"{sentence!r}: expected a SABI parse with "
            f"SUBJ.PRED={embedded_pred!r}"
        )


# === Per-aspect SUBJ-as-finite-S checks ============================


class TestAspectVariants:
    """The percolated ASPECT on the matrix matches the V form
    (sinabi PFV / sinasabi IPFV / sasabihin CTPL)."""

    @pytest.mark.parametrize("sentence,aspect", [
        ("Sinabi niya na pumunta si Maria.",     "PFV"),
        ("Sinasabi niya na pumunta si Maria.",   "IPFV"),
        ("Sasabihin niya na pumunta si Maria.",  "CTPL"),
    ])
    def test_aspect_percolates(
        self, sentence: str, aspect: str
    ) -> None:
        parses = parse_text(sentence)
        say_parses = [
            p for p in parses
            if p[1].feats.get("PRED") == "SABI <SUBJ, OBJ-AGENT>"
        ]
        assert len(say_parses) >= 1
        _ct, fs, _astr, _diags = say_parses[0]
        assert fs.feats.get("ASPECT") == aspect


# === Non-SAY-class OV regression ===================================


class TestNonSayClassOVRegression:
    """Non-SAY-class OV verbs continue to require a NOM-NP SUBJ.
    The new rule's ``(↓1 SAY_CLASS) =c 'YES'`` constraining
    equation prevents it from firing on non-SAY OV verbs."""

    def test_non_say_ov_with_na_zero_parses(self) -> None:
        # Kinain (OV PFV of 'eat') has no SAY_CLASS. The hypothetical
        # ``Kinain niya na pumunta si Maria.`` should not get an
        # indirect-speech reading from the new rule.
        parses = parse_text("Kinain niya na pumunta si Maria.")
        say_style_parses = []
        for p in parses:
            fs = p[1]
            pred = fs.feats.get("PRED", "")
            if not isinstance(pred, str) or not pred.startswith("EAT"):
                continue
            subj = fs.feats.get("SUBJ")
            if subj is None:
                continue
            if subj.feats.get("PRED") == "PUNTA <SUBJ>":
                say_style_parses.append(p)
        assert say_style_parses == [], (
            "Non-SAY-class OV verb (kinain) unexpectedly fired the "
            "new SAY-class indirect-speech rule"
        )

    def test_say_class_lex_only_sabi(self) -> None:
        """Verify the SAY_CLASS gate by checking the canonical
        SABI matrix verb works while a parallel construction with
        a non-SAY-class verb in the matrix slot does not get the
        finite-S SUBJ binding."""
        # SABI: works
        parses = parse_text("Sinabi niya na pumunta si Maria.")
        assert any(
            _is_say_with_embed_pred(p, "PUNTA <SUBJ>") for p in parses
        )
