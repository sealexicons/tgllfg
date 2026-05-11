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

from tgllfg.core.feats import BINARY_FEATS

from .paradigms import (
    AdjectiveCell,
    MorphData,
    Operation,
    Particle,
    Pronoun,
    Root,
    SandhiRule,
    VerbalCell,
)


# Phase 5n.C.4 Commit 4: canonicalize binary feat values to Python
# ``bool``. YAML 1.1 coerces unquoted ``YES`` / ``NO`` to bool already,
# but quoted ``"YES"`` / ``"NO"`` remains a string — leaving the
# runtime view inconsistent across the lex YAML files. This pass
# closes the gap by normalizing both forms to ``True`` / ``False`` for
# feats in ``BINARY_FEATS``. Enum feats (``INDEF``, ``PRED``,
# ``Q_TYPE``, etc.) keep their literal string value, including the
# legacy ``"YES"`` enum tags on ``INDEF`` / ``PRED``.
def _canonicalize_binary_feats(feats: dict[str, Any]) -> dict[str, Any]:
    out = dict(feats)
    for key, value in list(out.items()):
        if key not in BINARY_FEATS:
            continue
        if value is True or value == "YES":
            out[key] = True
        elif value is False or value == "NO":
            out[key] = False
    return out

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
        # The seed lexicon is split by POS: verbs.yaml first (so the
        # paradigm-generating VERB roots get indexed in their original
        # order), then nouns.yaml, then adjectives.yaml. Together they
        # reproduce the iteration order of the pre-split
        # data/tgl/roots.yaml plus the Phase 5g adjective additions.
        roots=(
            _load_roots(base / "verbs.yaml")
            + _load_roots(base / "nouns.yaml")
            + _load_roots(base / "adjectives.yaml")
            # Phase 5n.C.3 Commit 3 (§18 L31): NUM-pos roots for the
            # cardinal numerals. These drive the ``tig_distrib``
            # paradigm cell (and any future ``base_pos: NUM``
            # paradigms). Bare-NUM lookup continues to come from
            # ``particles.yaml``; the NUM-roots are paradigm inputs
            # only — they are NOT indexed as bare surfaces.
            + _load_roots(base / "numerals.yaml")
        ),
        paradigm_cells=_load_paradigm_cells(base / "paradigms.yaml"),
        adjective_cells=_load_adjective_cells(base / "adj_paradigms.yaml"),
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
        sandhi_flags_raw = rec.get("sandhi_flags", [])
        if not isinstance(sandhi_flags_raw, list):
            raise ValueError(f"{where}: 'sandhi_flags' must be a list")
        feats_raw = rec.get("feats", {})
        if not isinstance(feats_raw, dict):
            raise ValueError(f"{where}: 'feats' must be a mapping")
        synonyms_raw = rec.get("synonyms", [])
        if not isinstance(synonyms_raw, list):
            raise ValueError(f"{where}: 'synonyms' must be a list")
        out.append(Root(
            citation=_require(rec, "citation", where),
            pos=_require(rec, "pos", where),
            gloss=rec.get("gloss", ""),
            transitivity=rec.get("transitivity", ""),
            affix_class=list(affix_class_raw),
            sandhi_flags=list(sandhi_flags_raw),
            feats=_canonicalize_binary_feats(feats_raw),
            synonyms=list(synonyms_raw),
        ))
    return out


def _load_paradigm_cells(path: Path) -> list[VerbalCell]:
    out: list[VerbalCell] = []
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
        feats_raw = rec.get("feats", {})
        if not isinstance(feats_raw, dict):
            raise ValueError(f"{where}: 'feats' must be a mapping")
        # Phase 5n.C.3 Commit 1: ``base_pos`` discriminates verbal vs
        # non-verbal paradigm cells. VERB cells (the legacy default)
        # still require ``voice`` and ``aspect``; NOUN / ADJ / PRON
        # cells are non-verbal derivations and skip those fields.
        base_pos = rec.get("base_pos", "VERB")
        if base_pos == "VERB":
            voice = _require(rec, "voice", where)
            aspect = _require(rec, "aspect", where)
        else:
            voice = rec.get("voice", "")
            aspect = rec.get("aspect", "")
        out.append(VerbalCell(
            base_pos=base_pos,
            pos=rec.get("pos", ""),
            voice=voice,
            aspect=aspect,
            mood=rec.get("mood", "IND"),
            transitivity=rec.get("transitivity", ""),
            affix_class=rec.get("affix_class", ""),
            operations=operations,
            notes=rec.get("notes", ""),
            feats=_canonicalize_binary_feats(feats_raw),
        ))
    return out


def _load_adjective_cells(path: Path) -> list[AdjectiveCell]:
    out: list[AdjectiveCell] = []
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
        feats_raw = rec.get("feats", {})
        if not isinstance(feats_raw, dict):
            raise ValueError(f"{where}: 'feats' must be a mapping")
        out.append(AdjectiveCell(
            affix_class=rec.get("affix_class", ""),
            operations=operations,
            notes=rec.get("notes", ""),
            feats=_canonicalize_binary_feats(feats_raw),
        ))
    return out


def _load_particles(path: Path) -> list[Particle]:
    out: list[Particle] = []
    for i, rec in enumerate(_read_yaml(path)):
        where = f"{path}[{i}]"
        out.append(Particle(
            surface=_require(rec, "surface", where),
            pos=_require(rec, "pos", where),
            feats=_canonicalize_binary_feats(rec.get("feats", {})),
            is_clitic=bool(rec.get("is_clitic", False)),
            clitic_class=rec.get("clitic_class", ""),
        ))
    return out


def _load_pronouns(path: Path) -> list[Pronoun]:
    out: list[Pronoun] = []
    for i, rec in enumerate(_read_yaml(path)):
        where = f"{path}[{i}]"
        affix_class_raw = rec.get("affix_class", [])
        if not isinstance(affix_class_raw, list):
            raise ValueError(f"{where}: 'affix_class' must be a list")
        out.append(Pronoun(
            surface=_require(rec, "surface", where),
            feats=_canonicalize_binary_feats(rec.get("feats", {})),
            is_clitic=bool(rec.get("is_clitic", False)),
            affix_class=list(affix_class_raw),
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
