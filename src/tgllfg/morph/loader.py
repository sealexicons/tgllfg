# tgllfg/morph/loader.py

"""Load the seed YAML lexicon under ``data/tgl/`` into a
:class:`tgllfg.morph.paradigms.MorphData` instance.

The on-disk format is one YAML file per data class — keeping each
file small so the linguist editing one paradigm doesn't see noise
from the rest. The loader is permissive about missing files (a
brand-new project may not yet have, say, ``sandhi.yaml``) but
strict about per-record shape: a malformed entry raises
``ValueError`` with the file path and record index in the message.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .paradigms import (
    MorphData,
    Operation,
    ParadigmCell,
    Particle,
    Pronoun,
    Root,
    SandhiRule,
)

# Default location: <repo-root>/data/tgl. Resolved relative to this
# source file so the package works whether installed editable or not.
_DEFAULT_DATA_DIR = (
    Path(__file__).resolve().parents[3] / "data" / "tgl"
)


def load_morph_data(data_dir: Path | None = None) -> MorphData:
    """Load the seed YAML lexicon. Missing files yield empty lists for
    that data class; missing directories yield an empty ``MorphData``
    so callers can see clear "no data" failures instead of crashes."""
    base = Path(data_dir) if data_dir is not None else _DEFAULT_DATA_DIR
    if not base.is_dir():
        return MorphData()

    return MorphData(
        roots=_load_roots(base / "roots.yaml"),
        paradigm_cells=_load_paradigm_cells(base / "paradigms.yaml"),
        particles=_load_particles(base / "particles.yaml"),
        pronouns=_load_pronouns(base / "pronouns.yaml"),
        sandhi_rules=_load_sandhi_rules(base / "sandhi.yaml"),
    )


def _read_yaml(path: Path) -> list[dict[str, Any]]:
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
    return loaded


def _require(record: dict[str, Any], key: str, where: str) -> Any:
    if key not in record:
        raise ValueError(f"{where}: missing required field {key!r}")
    return record[key]


def _load_roots(path: Path) -> list[Root]:
    out: list[Root] = []
    for i, rec in enumerate(_read_yaml(path)):
        where = f"{path}[{i}]"
        affix_class_raw = rec.get("affix_class", [])
        if not isinstance(affix_class_raw, list):
            raise ValueError(f"{where}: 'affix_class' must be a list")
        out.append(Root(
            citation=_require(rec, "citation", where),
            pos=_require(rec, "pos", where),
            gloss=rec.get("gloss", ""),
            transitivity=rec.get("transitivity", ""),
            affix_class=list(affix_class_raw),
        ))
    return out


def _load_paradigm_cells(path: Path) -> list[ParadigmCell]:
    out: list[ParadigmCell] = []
    for i, rec in enumerate(_read_yaml(path)):
        where = f"{path}[{i}]"
        ops_raw = rec.get("operations", [])
        if not isinstance(ops_raw, list):
            raise ValueError(f"{where}: 'operations' must be a list")
        operations = [
            Operation(op=_require(o, "op", f"{where}.operations[{j}]"),
                      value=o.get("value", ""))
            for j, o in enumerate(ops_raw)
        ]
        out.append(ParadigmCell(
            voice=_require(rec, "voice", where),
            aspect=_require(rec, "aspect", where),
            mood=rec.get("mood", "IND"),
            transitivity=rec.get("transitivity", ""),
            affix_class=rec.get("affix_class", ""),
            operations=operations,
            notes=rec.get("notes", ""),
        ))
    return out


def _load_particles(path: Path) -> list[Particle]:
    out: list[Particle] = []
    for i, rec in enumerate(_read_yaml(path)):
        where = f"{path}[{i}]"
        out.append(Particle(
            surface=_require(rec, "surface", where),
            pos=_require(rec, "pos", where),
            feats=dict(rec.get("feats", {})),
            is_clitic=bool(rec.get("is_clitic", False)),
            clitic_class=rec.get("clitic_class", ""),
        ))
    return out


def _load_pronouns(path: Path) -> list[Pronoun]:
    out: list[Pronoun] = []
    for i, rec in enumerate(_read_yaml(path)):
        where = f"{path}[{i}]"
        out.append(Pronoun(
            surface=_require(rec, "surface", where),
            feats=dict(rec.get("feats", {})),
            is_clitic=bool(rec.get("is_clitic", False)),
        ))
    return out


def _load_sandhi_rules(path: Path) -> list[SandhiRule]:
    out: list[SandhiRule] = []
    for i, rec in enumerate(_read_yaml(path)):
        where = f"{path}[{i}]"
        out.append(SandhiRule(
            description=_require(rec, "description", where),
            pattern=rec.get("pattern", ""),
            replacement=rec.get("replacement", ""),
            context=rec.get("context", ""),
        ))
    return out


__all__ = ["load_morph_data"]
