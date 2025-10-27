# tgllfg/unify.py

from __future__ import annotations

import itertools
import re
from typing import Tuple, List

from . import CNode, FStructure

# --- Tiny equation grammar (patterns we support in this prototype) ---
FEAT = r"[A-Za-z_][A-Za-z0-9_\-]*"
RE_ATOM = re.compile(
    rf"^\(↑\s+({FEAT})\)\s*=\s*'([^']*)'\s*$"
)
RE_FROM_CHILD_ATTR = re.compile(
    rf"^\(↑\s+({FEAT})\)\s*=\s*↓(\d+)\s+({FEAT})\s*$"
)
RE_FROM_CHILD = re.compile(
    rf"^\(↑\s+({FEAT})\)\s*=\s*↓(\d+)\s*$"
)
RE_UP_EQUALS_CHILD = re.compile(
    r"^\(↑\)\s*=\s*↓(\d+)\s*$"
)

_id_counter = itertools.count(1)

def build_f_structure(root: CNode) -> FStructure:
    """Construct and return the f-structure for the given c-structure node."""
    f, _ = _build_f_for_node(root)
    return f

def _build_f_for_node(node: CNode) -> Tuple[FStructure, List[str]]:
    """
    Build an F-structure for this node.
    Returns (fs, diagnostics). This is a very small evaluator:
    - Creates child f-structures first
    - Applies equations on the current node to compose features / reentrancies
    - Supports a few core equation forms sufficient for the demo
    """
    diags: List[str] = []
    # 1) Build children first
    child_fs: List[FStructure] = []
    for ch in node.children:
        ch_fs, ch_d = _build_f_for_node(ch)
        child_fs.append(ch_fs)
        diags.extend(ch_d)

    # 2) Start a fresh f-structure for this node
    fs = FStructure(feats={}, id=next(_id_counter))

    # 3) Apply equations
    # If we see "(↑)=↓i", we will *replace* fs with that child's f-structure at the end.
    up_equals_child_idx: int | None = None

    for eq in node.equations:
        eq = eq.strip()

        m = RE_UP_EQUALS_CHILD.match(eq)
        if m:
            up_equals_child_idx = int(m.group(1)) - 1
            continue

        m = RE_ATOM.match(eq)
        if m:
            feat, atom = m.group(1), m.group(2)
            fs.feats[feat] = atom
            continue

        m = RE_FROM_CHILD_ATTR.match(eq)
        if m:
            up_feat, idx_s, child_attr = m.group(1), m.group(2), m.group(3)
            idx = int(idx_s) - 1
            if 0 <= idx < len(child_fs):
                fs.feats[up_feat] = child_fs[idx].feats.get(child_attr)
            else:
                diags.append(f"Eq ignored (child index out of range): {eq}")
            continue

        m = RE_FROM_CHILD.match(eq)
        if m:
            up_feat, idx_s = m.group(1), m.group(2)
            idx = int(idx_s) - 1
            if 0 <= idx < len(child_fs):
                # Reentrancy: bind the *child f-structure* as the value
                fs.feats[up_feat] = child_fs[idx].feats
            else:
                diags.append(f"Eq ignored (child index out of range): {eq}")
            continue

        # Unknown equation form — keep going but note it
        diags.append(f"Unrecognized equation (ignored): {eq}")

    # 4) If "(↑)=↓i" occurred, return that child's f-structure instead of fs
    if up_equals_child_idx is not None:
        if 0 <= up_equals_child_idx < len(child_fs):
            return child_fs[up_equals_child_idx], diags
        diags.append(f"(↑)=↓{up_equals_child_idx+1} out of range on node {node.label}")

    return fs, diags
