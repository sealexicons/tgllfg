# tgllfg/renderers.py

import json

def render_c(node, indent=0):
    s = "  "*indent + f"({node.label}\n"
    for ch in node.children:
        s += render_c(ch, indent+1)
    if not node.children:
        s += "  "*(indent+1) + "•\n"
    s += "  "*indent + ")\n"
    return s

def render_f(fstruct):
    return json.dumps(fstruct.feats, ensure_ascii=False, indent=2)

def render_a(astr):
    return json.dumps({
        "PRED": astr.pred,
        "roles": astr.roles,
        "role_to_GF": astr.mapping
    }, ensure_ascii=False, indent=2)
