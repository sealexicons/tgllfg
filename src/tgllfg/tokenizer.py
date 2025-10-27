# tgllfg/tokenizer.py

import re
from . import Token

_WORD = re.compile(r"\w+|\S")

def tokenize(s: str):
    out = []
    for m in _WORD.finditer(s.strip()):
        t = m.group(0)
        out.append(Token(surface=t, norm=t.lower(), start=m.start(), end=m.end()))
    return out
