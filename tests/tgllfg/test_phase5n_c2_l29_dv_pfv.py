"""Phase 5n.C.2 Commit 2 — L29 DV PFV high-frequency verbs.

Closes the §18.1 L29 DV PFV paradigm-coverage gap surfaced during
Phase 5e Commit 18 review. Each canonical DV PFV sentence exercises
the existing DV PFV paradigm cell (``data/tgl/paradigms.yaml``
line 286: ``-in-`` infix + ``-an`` suffix) on a high-frequency verb.

Pattern: ``<DV-PFV-V> ni <agent> si <pivot>`` per S&O 1972 §10 +
R&B 1986 chs.5/7. The agent is GEN-marked; the pivot is NOM-marked
(``si Juan``). DV pivots are semantically dative/locative/recipient.

Commit 2 of Phase 5n.C.2 bundles the verbs.yaml affix-class expansion
and the tripwire flip: ``bigay`` and ``tanong`` gain ``an_oblig``;
``usap`` is retagged INTR → TR + ``an_oblig`` (the pre-declared
``in_oblig`` was inadvertently blocked by the transitivity filter,
so both OV and DV cycles activate). The previously pinned tripwire
in ``TestPinnedDVPFVMissingAnOblig`` is flipped here to positive
coverage; the original 0-parse test was removed once Commit 2's
verbs.yaml changes landed.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Canonical DV PFV — all 8 verbs now parse =============================


@pytest.mark.parametrize("sentence,verb_lemma,pred", [
    ("Inaralan ni Maria si Juan.",  "aral",   "ARAL <SUBJ, OBJ-AGENT>"),
    ("Binasahan ni Maria si Juan.", "basa",   "BASA <SUBJ, OBJ-AGENT>"),
    ("Binilihan ni Maria si Juan.", "bili",   "BILI <SUBJ, OBJ-AGENT>"),
    ("Ginawahan ni Maria si Juan.", "gawa",   "GAWA <SUBJ, OBJ-AGENT>"),
    ("Tinulungan ni Maria si Juan.", "tulong", "TULONG <SUBJ, OBJ-AGENT>"),
    # Three previously deferred (verbs.yaml updated in Commit 2):
    ("Binigayan ni Maria si Juan.",  "bigay",  "BIGAY <SUBJ, OBJ-AGENT>"),
    ("Tinanungan ni Maria si Juan.", "tanong", "TANONG <SUBJ, OBJ-AGENT>"),
    ("Inusapan ni Maria si Juan.",   "usap",   "USAP <SUBJ, OBJ-AGENT>"),
])
def test_dv_pfv_canonical(
    sentence: str, verb_lemma: str, pred: str
) -> None:
    """Canonical DV PFV with V + GEN-agent + NOM-pivot."""
    parses = parse_text(sentence)
    assert len(parses) >= 1, f"expected ≥1 parse for {sentence!r}"
    _ct, fs, _astr, _diags = parses[0]
    assert fs.feats.get("VOICE") == "DV"
    assert fs.feats.get("ASPECT") == "PFV"
    assert fs.feats.get("PRED") == pred, (
        f"PRED mismatch for {sentence!r}: "
        f"expected {pred!r}, got {fs.feats.get('PRED')!r}"
    )


# === Argument-role mapping ===============================================


@pytest.mark.parametrize("sentence", [
    "Inaralan ni Maria si Juan.",
    "Binigayan ni Maria si Juan.",
    "Tinanungan ni Maria si Juan.",
    "Inusapan ni Maria si Juan.",
])
def test_dv_pfv_role_mapping(sentence: str) -> None:
    """DV PFV maps NOM-pivot → SUBJ and GEN-agent → OBJ-AGENT."""
    parses = parse_text(sentence)
    assert len(parses) >= 1
    _ct, fs, _astr, _diags = parses[0]
    subj = fs.feats.get("SUBJ")
    assert subj is not None
    # NOM-pivot is `si Juan` — proper-noun NP with CASE=NOM.
    assert subj.feats.get("CASE") == "NOM"
    assert subj.feats.get("LEMMA") == "juan"
    obj_agent = fs.feats.get("OBJ-AGENT")
    assert obj_agent is not None
    assert obj_agent.feats.get("CASE") == "GEN"
    assert obj_agent.feats.get("LEMMA") == "maria"


# === Aspect cycle: PFV / IPFV / CTPL =====================================


@pytest.mark.parametrize("sentence,verb_lemma,aspect", [
    # PFV (already covered by `test_dv_pfv_canonical`).
    # IPFV: -in- + cv-redup + -an
    ("Tinatanungan ni Maria si Juan.", "tanong", "IPFV"),
    ("Inuusapan ni Maria si Juan.",    "usap",   "IPFV"),
    # CTPL: cv-redup + -an (no -in-).
    ("Tatanungan ni Maria si Juan.",   "tanong", "CTPL"),
    ("Uusapan ni Maria si Juan.",      "usap",   "CTPL"),
])
def test_dv_aspect_cycle(
    sentence: str, verb_lemma: str, aspect: str
) -> None:
    """The IPFV / CTPL DV cells fire on the newly-an_oblig'd verbs
    too — the existing cv-redup paradigm cells (paradigms.yaml lines
    296 / 307) gain coverage transparently."""
    parses = parse_text(sentence)
    assert len(parses) >= 1, f"expected ≥1 parse for {sentence!r}"
    _ct, fs, _astr, _diags = parses[0]
    assert fs.feats.get("VOICE") == "DV"
    assert fs.feats.get("ASPECT") == aspect
