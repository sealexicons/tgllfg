"""Load :class:`LexicalEntry` records from the per-voice YAML tree
under ``data/tgl/lexicon/``.

Phase 5n.C.4 Commit 12: the loader the spec doc
(``docs/lex-yaml-schema.md``) calls for. C13–C16 progressively
move entries out of the in-Python ``BASE`` dict in
:mod:`tgllfg.core.lexicon` into the four YAML files this module
reads. While the migration is in flight, callers continue to
consume the ``BASE`` dict directly; the loader's parity-tested
output rides alongside until C16 swaps the dependency.

Public API:

* :func:`load_lex_entries` — returns ``dict[str, list[LexicalEntry]]``
  keyed by lemma, with per-lemma entries in source-declaration order.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tgllfg.core import lexicon as _lex
from tgllfg.core.common import FeatureValue, LexicalEntry


# Default location: ``<repo-root>/data/tgl/lexicon`` resolved relative
# to this source file so the package works whether installed editable
# or not. Mirrors :mod:`tgllfg.morph.loader` conventions.
_DEFAULT_DATA_DIR = (
    Path(__file__).resolve().parents[3] / "data" / "tgl" / "lexicon"
)


# File read order — matches docs/lex-yaml-schema.md §"File layout".
_FILES_IN_ORDER: tuple[str, ...] = (
    "intransitive_av.yaml",
    "plain_transitive.yaml",
    "applicative.yaml",
    "causative.yaml",
    "control.yaml",
)


_LEGAL_VOICES: frozenset[str] = frozenset({"AV", "OV", "DV", "IV", "BV", "LV"})

# Required fields per record.
_REQUIRED_FIELDS: tuple[str, ...] = (
    "lemma",
    "voice",
    "pred",
    "a_structure",
    "gf_defaults",
)


# Inline-intrinsic value tokens. Maps to the corresponding bool / None.
_INTRINSIC_TOKENS: dict[str, bool | None] = {
    "+": True,
    "-": False,
    "~": None,
}


def load_lex_entries(
    data_dir: Path | None = None,
) -> dict[str, list[LexicalEntry]]:
    """Load every LexicalEntry from ``data_dir`` (default:
    ``<repo>/data/tgl/lexicon``). Files are read in the order listed
    in ``_FILES_IN_ORDER``; entries within a file preserve their
    declaration order. Missing files are tolerated (returns empty
    for that file); missing directory returns the empty mapping."""
    base = Path(data_dir) if data_dir is not None else _DEFAULT_DATA_DIR
    out: dict[str, list[LexicalEntry]] = {}
    if not base.is_dir():
        return out
    for filename in _FILES_IN_ORDER:
        path = base / filename
        for entry in _load_file(path):
            out.setdefault(entry.lemma, []).append(entry)
    return out


def _load_file(path: Path) -> list[LexicalEntry]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as fh:
        loaded = yaml.safe_load(fh)
    if loaded is None:
        return []
    if not isinstance(loaded, list):
        raise ValueError(
            f"{path}: expected top-level list, got {type(loaded).__name__}"
        )
    out: list[LexicalEntry] = []
    for i, rec in enumerate(loaded):
        where = f"{path}[{i}]"
        out.append(_parse_record(rec, where))
    return out


def _parse_record(rec: Any, where: str) -> LexicalEntry:
    if not isinstance(rec, dict):
        raise ValueError(f"{where}: expected mapping, got {type(rec).__name__}")
    for key in _REQUIRED_FIELDS:
        if key not in rec:
            raise ValueError(f"{where}: missing required field {key!r}")

    lemma = _require_str(rec, "lemma", where)
    voice = _require_str(rec, "voice", where)
    if voice not in _LEGAL_VOICES:
        raise ValueError(
            f"{where}: voice {voice!r} not in {sorted(_LEGAL_VOICES)}"
        )
    pred = _require_str(rec, "pred", where)

    a_structure_raw = rec["a_structure"]
    if not isinstance(a_structure_raw, list) or not all(
        isinstance(r, str) for r in a_structure_raw
    ):
        raise ValueError(f"{where}: a_structure must be a list of strings")
    a_structure: list[str] = list(a_structure_raw)

    gf_defaults_raw = rec["gf_defaults"]
    if not isinstance(gf_defaults_raw, dict):
        raise ValueError(f"{where}: gf_defaults must be a mapping")
    gf_defaults: dict[str, str] = {}
    for k, v in gf_defaults_raw.items():
        if not isinstance(k, str) or not isinstance(v, str):
            raise ValueError(
                f"{where}: gf_defaults keys + values must be strings; "
                f"got {k!r}: {v!r}"
            )
        gf_defaults[k] = v
    if set(gf_defaults.keys()) != set(a_structure):
        raise ValueError(
            f"{where}: gf_defaults keys {sorted(gf_defaults.keys())!r} "
            f"must match a_structure {a_structure!r} exactly"
        )

    transitive = rec.get("transitive", True)
    if not isinstance(transitive, bool):
        raise ValueError(
            f"{where}: transitive must be bool; got {type(transitive).__name__}"
        )

    extra_constraints_raw = rec.get("extra_constraints", {})
    if not isinstance(extra_constraints_raw, dict):
        raise ValueError(f"{where}: extra_constraints must be a mapping")
    extra_constraints: dict[str, FeatureValue] = {}
    for k, v in extra_constraints_raw.items():
        if not isinstance(k, str):
            raise ValueError(
                f"{where}: extra_constraints keys must be strings; got {k!r}"
            )
        extra_constraints[k] = v

    explicit_constraints_raw = rec.get("morph_constraints")
    if explicit_constraints_raw is not None:
        if not isinstance(explicit_constraints_raw, dict):
            raise ValueError(
                f"{where}: morph_constraints must be a mapping"
            )
        if extra_constraints:
            raise ValueError(
                f"{where}: morph_constraints (full override) and "
                f"extra_constraints (extends auto-fill) are mutually "
                f"exclusive"
            )

    has_intrinsic = "intrinsic" in rec
    has_inline = "intrinsic_classification" in rec
    if has_intrinsic and has_inline:
        raise ValueError(
            f"{where}: at most one of intrinsic / "
            f"intrinsic_classification may be set"
        )
    intrinsic: dict[str, tuple[bool | None, bool | None]] = {}
    if has_intrinsic:
        intrinsic = _resolve_intrinsic(rec["intrinsic"], where)
    elif has_inline:
        intrinsic = _parse_inline_intrinsic(
            rec["intrinsic_classification"], where
        )

    morph_constraints: dict[str, FeatureValue] = {}
    if explicit_constraints_raw is not None:
        # Full override: replace the auto-fill entirely. Used by
        # applicative entries (BEN / INSTR / REASON) authored as
        # bare LexicalEntry(...) in BASE that intentionally
        # under-specify CAUS / TR for a looser match.
        for k, v in explicit_constraints_raw.items():
            if not isinstance(k, str):
                raise ValueError(
                    f"{where}: morph_constraints keys must be strings; "
                    f"got {k!r}"
                )
            morph_constraints[k] = v
        if morph_constraints.get("VOICE", voice) != voice:
            raise ValueError(
                f"{where}: morph_constraints['VOICE'] = "
                f"{morph_constraints['VOICE']!r} disagrees with the "
                f"voice field {voice!r}"
            )
        morph_constraints["VOICE"] = voice
    else:
        morph_constraints["VOICE"] = voice
        morph_constraints["CAUS"] = "NONE"
        morph_constraints["APPL"] = "CONVEY" if voice == "IV" else "NONE"
        if transitive:
            morph_constraints["TR"] = "TR"
        morph_constraints.update(extra_constraints)

    return LexicalEntry(
        lemma=lemma,
        pred=pred,
        a_structure=a_structure,
        morph_constraints=morph_constraints,
        gf_defaults=gf_defaults,
        intrinsic_classification=intrinsic,
    )


def _require_str(rec: dict[str, Any], key: str, where: str) -> str:
    v = rec[key]
    if not isinstance(v, str):
        raise ValueError(
            f"{where}: field {key!r} must be a string; got "
            f"{type(v).__name__}"
        )
    return v


def _resolve_intrinsic(
    name: Any, where: str
) -> dict[str, tuple[bool | None, bool | None]]:
    """Look up a named intrinsic-profile constant in
    :mod:`tgllfg.core.lexicon` by its public symbol (the constant
    name with the leading underscore stripped: ``AV_TR_AGENT_PATIENT``
    resolves to ``_AV_TR_AGENT_PATIENT``)."""
    if not isinstance(name, str):
        raise ValueError(
            f"{where}: intrinsic must be a symbolic name; got "
            f"{type(name).__name__}"
        )
    constant = getattr(_lex, f"_{name}", None)
    if constant is None:
        raise ValueError(
            f"{where}: unknown intrinsic profile {name!r}; expected one "
            f"of the named constants in tgllfg.core.lexicon (see "
            f"docs/lex-yaml-schema.md §'Intrinsic profile references')"
        )
    if not isinstance(constant, dict):
        raise ValueError(
            f"{where}: intrinsic {name!r} resolved to "
            f"{type(constant).__name__}, expected dict"
        )
    return dict(constant)


def _parse_inline_intrinsic(
    raw: Any, where: str
) -> dict[str, tuple[bool | None, bool | None]]:
    """Parse the inline ``intrinsic_classification`` form:

    .. code-block:: yaml

        intrinsic_classification:
          AGENT: ["+", "+"]
          PATIENT: ["-", "-"]
          EVENT: ["~", "~"]
    """
    if not isinstance(raw, dict):
        raise ValueError(
            f"{where}: intrinsic_classification must be a mapping"
        )
    out: dict[str, tuple[bool | None, bool | None]] = {}
    for role, pair in raw.items():
        if not isinstance(role, str):
            raise ValueError(
                f"{where}: intrinsic_classification role must be a "
                f"string; got {role!r}"
            )
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError(
                f"{where}: intrinsic_classification[{role!r}] must be "
                f"a 2-element list of tokens; got {pair!r}"
            )
        r_tok, o_tok = pair
        if r_tok not in _INTRINSIC_TOKENS or o_tok not in _INTRINSIC_TOKENS:
            raise ValueError(
                f"{where}: intrinsic_classification[{role!r}] tokens "
                f"must be each one of '+', '-', '~'; got {pair!r}"
            )
        out[role] = (_INTRINSIC_TOKENS[r_tok], _INTRINSIC_TOKENS[o_tok])
    return out


__all__ = ["load_lex_entries"]
