# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

# tgllfg/text/__init__.py

from .clitics import (
    split_apostrophe_t,
    split_apostrophe_y,
    split_enclitics,
    split_linker_ng,
)
from .multiword import merge_hyphen_compounds
from .tokenizer import tokenize

__all__ = [
    "merge_hyphen_compounds",
    "split_apostrophe_t",
    "split_apostrophe_y",
    "split_enclitics",
    "split_linker_ng",
    "tokenize",
]
