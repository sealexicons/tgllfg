# tgllfg/lmt.py

from . import AStructure, FStructure

# Apply lexical mapping theory to produce an A-Structure from F-Structure.
# This is the §4.2-vintage heuristic; Phase 5 replaces it with a real
# Bresnan–Kanerva-style LMT that maps from a-structure plus voice
# morphology rather than reading off a finished f-structure.
def apply_lmt(f: FStructure) -> AStructure:
    pred = (f.feats.get("PRED") or "").split()[0]  # "EAT <...>" -> "EAT"

    # Heuristic: OV when agent surfaces as OBJ alongside the SUBJ pivot
    # (the ng-non-pivot-as-OBJ analysis; see docs/analysis-choices.md).
    if "SUBJ" in f.feats and "OBJ" in f.feats:
        roles = ["AGENT", "PATIENT"]          # θ-roles
        mapping = {"PATIENT": "SUBJ", "AGENT": "OBJ"}
    else:
        roles = ["ACTOR"]
        mapping = {"ACTOR": "SUBJ"}

    return AStructure(pred=pred, roles=roles, mapping=mapping)
