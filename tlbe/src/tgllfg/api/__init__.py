# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""tgllfg REST API package (Phase 13).

The FastAPI application factory and its building blocks. Endpoints are
versioned under ``/api/v1`` (:mod:`tgllfg.api.v1`); shared dependency /
utility code lives in :mod:`tgllfg.api.deps`; app startup is in
:mod:`tgllfg.api.app`. Liveness/readiness probes are intentionally
unversioned (:mod:`tgllfg.api.health`).
"""

from .app import create_app
from .openapi import OPENAPI_PATH, render_openapi, write_openapi

__all__ = ["OPENAPI_PATH", "create_app", "render_openapi", "write_openapi"]
