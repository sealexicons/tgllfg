# tgllfg/text/__init__.py

from .clitics import split_enclitics, split_linker_ng
from .multiword import merge_hyphen_compounds
from .tokenizer import tokenize

__all__ = [
    "merge_hyphen_compounds",
    "split_enclitics",
    "split_linker_ng",
    "tokenize",
]
