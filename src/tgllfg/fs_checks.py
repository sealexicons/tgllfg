# tgllfg/fs_checks.py

from . import CNode, FStructure

def lfg_well_formed(_f: FStructure, _ctree: CNode):
    # Uniqueness: each attribute has one value; Completeness/Coherence: subcat satisfied.
    # Prototype: always OK but return a hook for diagnostics
    return True, []
