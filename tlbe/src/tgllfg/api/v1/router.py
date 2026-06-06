# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""The ``/v1`` aggregating :class:`~fastapi.APIRouter` (Phase 13.A).

Mounted with ``prefix="/api/v1"`` by :func:`tgllfg.api.create_app`. Phase
13.C registers the parse / audit / lex sub-routers here.
"""

from fastapi import APIRouter

v1_router = APIRouter()

# Phase 13.C will register the versioned sub-routers, e.g.:
#   from .parse import parse_router
#   v1_router.include_router(parse_router)
