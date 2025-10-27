# tgllfg/fs_checks.py

def lfg_well_formed(f, ctree):
    # Uniqueness: each attribute has one value; Completeness/Coherence: subcat satisfied.
    # Prototype: always OK but return a hook for diagnostics
    return True, []
