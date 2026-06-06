# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Version 1 of the tgllfg REST API.

Aggregating router for all ``/api/v1`` endpoints; the concrete route modules
(``parse`` / ``audit`` / ``lex``) are registered in Phase 13.C.
"""

from .router import v1_router

__all__ = ["v1_router"]
