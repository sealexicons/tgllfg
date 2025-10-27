# tgllfg/lmt.py

from . import AStructure, FStructure

def apply_lmt(f: FStructure) -> AStructure:
    pred = (f.feats.get("PRED") or "").split()[0]  # "EAT <...>" -> "EAT"

    # Heuristic: PV if agent realized as OBL-AG alongside SUBJ pivot
    if "SUBJ" in f.feats and "OBL-AG" in f.feats:
        roles = ["AGENT", "PATIENT"]          # θ-roles
        mapping = {"PATIENT": "SUBJ", "AGENT": "OBL-AG"}
    else:
        roles = ["ACTOR"]
        mapping = {"ACTOR": "SUBJ"}

    return AStructure(pred=pred, roles=roles, mapping=mapping)
