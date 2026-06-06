# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""OpenAPI schema generation (Phase 13.D).

:func:`render_openapi` is the committed ``openapi.json`` content —
``create_app().openapi()`` as indented JSON in FastAPI's natural key
order (``openapi`` / ``info`` / ``paths`` / ``components`` …),
deterministic for a pinned FastAPI (the dict is built by insertion order;
the schema depends only on the routes + Pydantic DTOs, not on settings /
env). The ``tgllfg openapi`` CLI + the ``openapi-sync`` CI gate consume
it; the Phase 14 frontend codegens a typed client from the committed file.
"""

import json
from pathlib import Path

from .app import create_app

#: Top-level (repo-root) ``openapi.json`` — the API contract shared by the
#: backend (producer) and the frontend (consumer). ``parents[4]``:
#: ``src/tgllfg/api/openapi.py`` → src → tgllfg → tlbe → repo root.
OPENAPI_PATH = Path(__file__).resolve().parents[4] / "openapi.json"


def render_openapi() -> str:
    """The canonical ``openapi.json`` text: ``app.openapi()`` rendered as
    2-space-indented JSON in natural key order, with a trailing newline.
    (No key sorting — FastAPI's order keeps ``openapi`` / ``info`` first.)
    """
    return json.dumps(create_app().openapi(), indent=2) + "\n"


def write_openapi() -> Path:
    """(Re)write :data:`OPENAPI_PATH` from :func:`render_openapi`."""
    OPENAPI_PATH.write_text(render_openapi(), encoding="utf-8")
    return OPENAPI_PATH
