# tgllfg/clitics.py

# Handle enclitic cluster ordering (e.g., =na, =pa, =ba, =din/rin, =yata, etc.)
# Prototype: leave as-is but split tokens like "kainin=pa" or "kainin pa" → ["kainin","pa"]
from . import Token

ENCLITICS = {"na", "pa", "ba", "din", "rin", "yata", "man", "daw", "raw", "lang"}

def split_enclitics(tokens: list[Token]) -> list[Token]:
    out: list[Token] = []
    for t in tokens:
        if "=" in t.surface:
            base, after = t.surface.split("=", 1)
            out.append(Token(base, base.lower(), t.start, t.start+len(base)))
            if after in ENCLITICS:
                out.append(Token(after, after.lower(), t.start+len(base)+1, t.end))
        else:
            out.append(t)
    return out
