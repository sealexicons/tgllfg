# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.C.4 Commit 12 — unit tests for the LexicalEntry YAML loader.

Exercises :func:`tgllfg.core.lexicon_loader.load_lex_entries` against
synthetic YAML fixtures written to a tmp directory. Covers:

* Auto-filled ``morph_constraints``: VOICE / CAUS / APPL / TR.
* ``transitive: false`` omits TR.
* IV gets ``APPL: CONVEY``; other voices get ``APPL: NONE``.
* ``extra_constraints`` overrides + extends the auto-filled set.
* Named intrinsic profiles resolve from :mod:`tgllfg.core.lexicon`.
* Inline ``intrinsic_classification`` parses the ``+`` / ``-`` / ``~``
  token alphabet.
* Per-record validation errors surface with file path + index.
"""

from pathlib import Path

import pytest
import yaml

from tgllfg.core import lexicon as _lex
from tgllfg.core.lexicon_loader import load_lex_entries


def _write(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(records), encoding="utf-8")


# === Empty-directory + missing-file cases ================================


def test_returns_empty_when_directory_missing(tmp_path: Path) -> None:
    out = load_lex_entries(tmp_path / "does_not_exist")
    assert out == {}


def test_returns_empty_when_files_missing(tmp_path: Path) -> None:
    """Empty directory (the four expected YAML files are absent) is
    a non-error — the loader returns an empty mapping."""
    out = load_lex_entries(tmp_path)
    assert out == {}


def test_returns_empty_on_null_yaml(tmp_path: Path) -> None:
    """A YAML file containing only comments parses to ``None`` —
    treated as empty."""
    (tmp_path / "intransitive_av.yaml").write_text(
        "# placeholder; no entries yet\n", encoding="utf-8"
    )
    out = load_lex_entries(tmp_path)
    assert out == {}


# === Auto-filled morph_constraints =======================================


def test_av_intransitive_auto_constraints(tmp_path: Path) -> None:
    _write(
        tmp_path / "intransitive_av.yaml",
        [
            {
                "lemma": "kain",
                "voice": "AV",
                "pred": "EAT <SUBJ>",
                "a_structure": ["ACTOR"],
                "gf_defaults": {"ACTOR": "SUBJ"},
                "transitive": False,
                "intrinsic": "AV_INTR_ACTOR",
            }
        ],
    )
    out = load_lex_entries(tmp_path)
    assert list(out.keys()) == ["kain"]
    entry = out["kain"][0]
    assert entry.lemma == "kain"
    assert entry.pred == "EAT <SUBJ>"
    assert entry.a_structure == ["ACTOR"]
    assert entry.gf_defaults == {"ACTOR": "SUBJ"}
    # TR omitted on intransitive; APPL=NONE on AV; CAUS=NONE default.
    assert entry.morph_constraints == {
        "VOICE": "AV",
        "CAUS": "NONE",
        "APPL": "NONE",
    }
    assert entry.intrinsic_classification == _lex._AV_INTR_ACTOR


def test_av_transitive_default(tmp_path: Path) -> None:
    _write(
        tmp_path / "plain_transitive.yaml",
        [
            {
                "lemma": "kain",
                "voice": "AV",
                "pred": "EAT <SUBJ, OBJ>",
                "a_structure": ["AGENT", "PATIENT"],
                "gf_defaults": {"AGENT": "SUBJ", "PATIENT": "OBJ"},
                "intrinsic": "AV_TR_AGENT_PATIENT",
            }
        ],
    )
    entry = load_lex_entries(tmp_path)["kain"][0]
    assert entry.morph_constraints == {
        "VOICE": "AV",
        "CAUS": "NONE",
        "APPL": "NONE",
        "TR": "TR",
    }


def test_iv_gets_appl_convey(tmp_path: Path) -> None:
    _write(
        tmp_path / "applicative.yaml",
        [
            {
                "lemma": "sulat",
                "voice": "IV",
                "pred": "WRITE <SUBJ, OBJ-AGENT>",
                "a_structure": ["AGENT", "CONVEYED"],
                "gf_defaults": {"CONVEYED": "SUBJ", "AGENT": "OBJ-AGENT"},
                "intrinsic": "IV_TR_AGENT_CONVEYED",
            }
        ],
    )
    entry = load_lex_entries(tmp_path)["sulat"][0]
    assert entry.morph_constraints == {
        "VOICE": "IV",
        "CAUS": "NONE",
        "APPL": "CONVEY",
        "TR": "TR",
    }


def test_morph_constraints_override_replaces_autofill(tmp_path: Path) -> None:
    """``morph_constraints`` as a top-level field replaces the
    auto-filled CAUS / APPL / TR entirely — the loader emits
    exactly the listed keys plus VOICE. Used by BEN / INSTR /
    REASON applicatives that under-specify for a looser match."""
    _write(
        tmp_path / "applicative.yaml",
        [
            {
                "lemma": "bili",
                "voice": "IV",
                "pred": "BUY-FOR <SUBJ, OBJ-AGENT>",
                "a_structure": ["AGENT", "BENEFICIARY"],
                "gf_defaults": {
                    "BENEFICIARY": "SUBJ", "AGENT": "OBJ-AGENT"
                },
                "morph_constraints": {"APPL": "BEN"},
                "intrinsic": "IV_BEN_AGENT_BENEFICIARY",
            }
        ],
    )
    entry = load_lex_entries(tmp_path)["bili"][0]
    # No CAUS, no TR — the looser-match shape.
    assert entry.morph_constraints == {"VOICE": "IV", "APPL": "BEN"}


def test_morph_constraints_and_extra_constraints_are_mutually_exclusive(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "applicative.yaml",
        [
            {
                "lemma": "x",
                "voice": "IV",
                "pred": "X <SUBJ, OBJ-AGENT>",
                "a_structure": ["AGENT", "BENEFICIARY"],
                "gf_defaults": {
                    "BENEFICIARY": "SUBJ", "AGENT": "OBJ-AGENT"
                },
                "morph_constraints": {"APPL": "BEN"},
                "extra_constraints": {"MOOD": "SOC"},
            }
        ],
    )
    with pytest.raises(ValueError, match="mutually exclusive"):
        load_lex_entries(tmp_path)


def test_morph_constraints_voice_must_agree(tmp_path: Path) -> None:
    _write(
        tmp_path / "applicative.yaml",
        [
            {
                "lemma": "x",
                "voice": "IV",
                "pred": "X <SUBJ, OBJ-AGENT>",
                "a_structure": ["AGENT", "BENEFICIARY"],
                "gf_defaults": {
                    "BENEFICIARY": "SUBJ", "AGENT": "OBJ-AGENT"
                },
                "morph_constraints": {"VOICE": "OV", "APPL": "BEN"},
            }
        ],
    )
    with pytest.raises(ValueError, match="disagrees with the voice field"):
        load_lex_entries(tmp_path)


def test_extra_constraints_overrides_and_extends(tmp_path: Path) -> None:
    """``extra_constraints`` adds MOOD/CAUS/APPL keys and overrides
    the auto-filled defaults — mirrors the existing ``_entry()`` +
    bespoke LexicalEntry constructions."""
    _write(
        tmp_path / "applicative.yaml",
        [
            {
                "lemma": "kain",
                "voice": "AV",
                "pred": "EAT-TOGETHER <SUBJ>",
                "a_structure": ["ACTOR"],
                "gf_defaults": {"ACTOR": "SUBJ"},
                "transitive": False,
                "extra_constraints": {"MOOD": "SOC"},
                "intrinsic": "AV_INTR_ACTOR",
            },
            {
                "lemma": "bili",
                "voice": "IV",
                "pred": "BUY <SUBJ, OBJ-AGENT>",
                "a_structure": ["AGENT", "BENEFICIARY"],
                "gf_defaults": {
                    "BENEFICIARY": "SUBJ", "AGENT": "OBJ-AGENT"
                },
                "extra_constraints": {"APPL": "BEN"},
                "intrinsic": "IV_BEN_AGENT_BENEFICIARY",
            },
        ],
    )
    out = load_lex_entries(tmp_path)
    assert out["kain"][0].morph_constraints == {
        "VOICE": "AV",
        "CAUS": "NONE",
        "APPL": "NONE",
        "MOOD": "SOC",
    }
    # APPL overridden from default CONVEY to BEN.
    assert out["bili"][0].morph_constraints["APPL"] == "BEN"


# === Inline intrinsic_classification =====================================


def test_inline_intrinsic_classification(tmp_path: Path) -> None:
    _write(
        tmp_path / "intransitive_av.yaml",
        [
            {
                "lemma": "someverb",
                "voice": "AV",
                "pred": "FOO <SUBJ>",
                "a_structure": ["EXPERIENCER"],
                "gf_defaults": {"EXPERIENCER": "SUBJ"},
                "transitive": False,
                "intrinsic_classification": {
                    "EXPERIENCER": ["-", "-"],
                },
            }
        ],
    )
    entry = load_lex_entries(tmp_path)["someverb"][0]
    assert entry.intrinsic_classification == {"EXPERIENCER": (False, False)}


def test_inline_intrinsic_supports_none_tilde(tmp_path: Path) -> None:
    """``~`` maps to Python ``None`` — used for XCOMP-stipulated
    roles like EVENT in the indirect-causative profile."""
    _write(
        tmp_path / "causative.yaml",
        [
            {
                "lemma": "kain",
                "voice": "AV",
                "pred": "MAKE-EAT <SUBJ, XCOMP>",
                "a_structure": ["CAUSER", "EVENT"],
                "gf_defaults": {"CAUSER": "SUBJ", "EVENT": "XCOMP"},
                "extra_constraints": {"CAUS": "INDIRECT"},
                "intrinsic_classification": {
                    "CAUSER": ["-", "-"],
                    "EVENT": ["~", "~"],
                },
            }
        ],
    )
    entry = load_lex_entries(tmp_path)["kain"][0]
    assert entry.intrinsic_classification == {
        "CAUSER": (False, False),
        "EVENT": (None, None),
    }


# === Validation errors ===================================================


def test_missing_required_field_raises(tmp_path: Path) -> None:
    _write(
        tmp_path / "intransitive_av.yaml",
        [{"lemma": "kain", "voice": "AV", "pred": "EAT <SUBJ>"}],
    )
    with pytest.raises(ValueError, match="missing required field 'a_structure'"):
        load_lex_entries(tmp_path)


def test_illegal_voice_raises(tmp_path: Path) -> None:
    _write(
        tmp_path / "intransitive_av.yaml",
        [
            {
                "lemma": "k",
                "voice": "XV",
                "pred": "X <SUBJ>",
                "a_structure": ["A"],
                "gf_defaults": {"A": "SUBJ"},
            }
        ],
    )
    with pytest.raises(ValueError, match="voice 'XV' not in"):
        load_lex_entries(tmp_path)


def test_both_intrinsic_forms_rejected(tmp_path: Path) -> None:
    _write(
        tmp_path / "intransitive_av.yaml",
        [
            {
                "lemma": "k",
                "voice": "AV",
                "pred": "X <SUBJ>",
                "a_structure": ["A"],
                "gf_defaults": {"A": "SUBJ"},
                "intrinsic": "AV_INTR_AGENT",
                "intrinsic_classification": {"A": ["-", "-"]},
            }
        ],
    )
    with pytest.raises(ValueError, match="at most one of intrinsic"):
        load_lex_entries(tmp_path)


def test_unknown_intrinsic_name_raises(tmp_path: Path) -> None:
    _write(
        tmp_path / "intransitive_av.yaml",
        [
            {
                "lemma": "k",
                "voice": "AV",
                "pred": "X <SUBJ>",
                "a_structure": ["A"],
                "gf_defaults": {"A": "SUBJ"},
                "intrinsic": "NO_SUCH_PROFILE",
            }
        ],
    )
    with pytest.raises(ValueError, match="unknown intrinsic profile"):
        load_lex_entries(tmp_path)


def test_gf_defaults_must_match_a_structure_exactly(tmp_path: Path) -> None:
    _write(
        tmp_path / "intransitive_av.yaml",
        [
            {
                "lemma": "k",
                "voice": "AV",
                "pred": "X <SUBJ>",
                "a_structure": ["AGENT"],
                "gf_defaults": {"AGENT": "SUBJ", "ORPHAN": "OBJ"},
            }
        ],
    )
    with pytest.raises(ValueError, match="must match a_structure"):
        load_lex_entries(tmp_path)


def test_bad_inline_token_rejected(tmp_path: Path) -> None:
    _write(
        tmp_path / "intransitive_av.yaml",
        [
            {
                "lemma": "k",
                "voice": "AV",
                "pred": "X <SUBJ>",
                "a_structure": ["AGENT"],
                "gf_defaults": {"AGENT": "SUBJ"},
                "intrinsic_classification": {"AGENT": ["yes", "no"]},
            }
        ],
    )
    with pytest.raises(ValueError, match="tokens"):
        load_lex_entries(tmp_path)


# === Source-declaration ordering preserved ===============================


def test_per_lemma_entries_keep_declaration_order(tmp_path: Path) -> None:
    """Multiple entries for the same lemma keep their declared order
    — important for the analyzer's first-match-wins selection."""
    _write(
        tmp_path / "plain_transitive.yaml",
        [
            {
                "lemma": "kain",
                "voice": "AV",
                "pred": "EAT <SUBJ>",
                "a_structure": ["ACTOR"],
                "gf_defaults": {"ACTOR": "SUBJ"},
                "transitive": False,
                "intrinsic": "AV_INTR_ACTOR",
            },
            {
                "lemma": "kain",
                "voice": "AV",
                "pred": "EAT <SUBJ, OBJ>",
                "a_structure": ["AGENT", "PATIENT"],
                "gf_defaults": {"AGENT": "SUBJ", "PATIENT": "OBJ"},
                "intrinsic": "AV_TR_AGENT_PATIENT",
            },
        ],
    )
    entries = load_lex_entries(tmp_path)["kain"]
    assert [e.pred for e in entries] == [
        "EAT <SUBJ>",
        "EAT <SUBJ, OBJ>",
    ]


# === Cross-file ordering: intransitive → plain → applicative → causative → control


def test_files_concatenate_in_canonical_order(tmp_path: Path) -> None:
    _write(
        tmp_path / "causative.yaml",
        [
            {
                "lemma": "kain",
                "voice": "OV",
                "pred": "FEED <SUBJ, OBJ-CAUSER>",
                "a_structure": ["CAUSER", "CAUSEE"],
                "gf_defaults": {"CAUSEE": "SUBJ", "CAUSER": "OBJ-CAUSER"},
                "extra_constraints": {"CAUS": "DIRECT"},
                "intrinsic": "OV_CAUS_DIRECT",
            }
        ],
    )
    _write(
        tmp_path / "intransitive_av.yaml",
        [
            {
                "lemma": "kain",
                "voice": "AV",
                "pred": "EAT <SUBJ>",
                "a_structure": ["ACTOR"],
                "gf_defaults": {"ACTOR": "SUBJ"},
                "transitive": False,
                "intrinsic": "AV_INTR_ACTOR",
            }
        ],
    )
    entries = load_lex_entries(tmp_path)["kain"]
    # intransitive_av.yaml is read before causative.yaml regardless of
    # alphabetical filesystem order.
    assert entries[0].pred == "EAT <SUBJ>"
    assert entries[1].pred == "FEED <SUBJ, OBJ-CAUSER>"
