# tgllfg/text/__init__.py

from .clitics import split_enclitics, split_linker_ng
from .tokenizer import tokenize

__all__ = [
    "split_enclitics",
    "split_linker_ng",
    "tokenize",
]
