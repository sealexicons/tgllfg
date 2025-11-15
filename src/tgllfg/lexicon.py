# tgllfg/lexicon.py

from . import MorphAnalysis, LexicalEntry

BASE = {
    "kain": [
        LexicalEntry(
            lemma="kain",
            pred="EAT <SUBJ>",                 # intransitive template (Actor Voice common)
            a_structure=["ACTOR"],
            morph_constraints={"VOICE":"AV"},
            gf_defaults={"ACTOR":"SUBJ"}
        ),
        LexicalEntry(
            lemma="kain",
            pred="EAT <SUBJ, OBJ>",            # transitive template (Patient Voice common)
            a_structure=["AGENT","PATIENT"],
            morph_constraints={"VOICE":"PV","TR":"TR"},
            gf_defaults={"PATIENT":"SUBJ","AGENT":"OBL-AG"}
        )
    ]
}

def lookup_lexicon(mlist: list[list[MorphAnalysis]]) -> list[list[tuple[MorphAnalysis, LexicalEntry|None]]]:
    out: list[list[tuple[MorphAnalysis, LexicalEntry|None]]] = []
    for cand_list in mlist:
        pairs: list[tuple[MorphAnalysis, LexicalEntry|None]] = []
        for ma in cand_list:
            if ma.pos == "VERB" and ma.lemma in BASE:
                # pick entries compatible with morphology
                for le in BASE[ma.lemma]:
                    ok = all(ma.feats.get(k)==v for k,v in le.morph_constraints.items())
                    if ok:
                        pairs.append((ma, le))
            else:
                pairs.append((ma, None))
        out.append(pairs)
    return out
