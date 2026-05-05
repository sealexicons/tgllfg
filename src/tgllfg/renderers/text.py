# tgllfg/renderers/text.py

"""Pretty-printers for c-, f-, and a-structures (text / JSON output).

The f-structure renderer walks the graph projection produced by
:mod:`tgllfg.fstruct`. Sub-f-structures appear as nested ``FStructure``
objects and set values appear as ``frozenset``s of projected values.
Reentrancy (the same canonical node reachable by two paths) is
detected by ``FStructure.id`` and rendered as a back-reference on
second visit.

Future renderer formats (GraphViz dot, HTML, …) live in sibling
modules under :mod:`tgllfg.renderers`; this module owns the
text / JSON output flavour.
"""

from __future__ import annotations

import json
from typing import Any

from ..core.common import AStructure, CNode, FStructure


def render_c(node: CNode, indent: int = 0) -> str:
    s = "  " * indent + f"({node.label}\n"
    for ch in node.children:
        s += render_c(ch, indent + 1)
    if not node.children:
        s += "  " * (indent + 1) + "•\n"
    s += "  " * indent + ")\n"
    return s


def render_f(fstruct: FStructure) -> str:
    return json.dumps(_to_json(fstruct, set()), ensure_ascii=False, indent=2)


def render_a(astr: AStructure) -> str:
    return json.dumps(
        {
            "PRED": astr.pred,
            "roles": astr.roles,
            "role_to_GF": astr.mapping,
        },
        ensure_ascii=False,
        indent=2,
    )


def _to_json(value: Any, seen: set[int]) -> Any:
    if isinstance(value, FStructure):
        if value.id in seen:
            return f"<reentrant id={value.id}>"
        seen.add(value.id)
        return {k: _to_json(v, seen) for k, v in value.feats.items()}
    if isinstance(value, frozenset):
        # JSON has no set type; emit as a list, sorted by repr for
        # stable output.
        items = [_to_json(m, seen) for m in value]
        items.sort(key=lambda x: json.dumps(x, ensure_ascii=False, sort_keys=True))
        return items
    return value
