# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Shared FastAPI dependencies and DTOs (Phase 13.A).

Common DI / utility code consumed by the versioned route modules under
:mod:`tgllfg.api.v1`. Phase 13.A provides the request principal
(:func:`get_principal`) and the settings dependency alias; the async DB
session dependency lands in Phase 13.C with its first route consumer.
"""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, status

from .settings import Settings, get_settings

#: Settings as a FastAPI dependency — injected into routes / other deps.
SettingsDep = Annotated[Settings, Depends(get_settings)]


@dataclass(frozen=True)
class Principal:
    """The calling principal. ``roles`` gates route access; the ``"*"``
    wildcard (held by the anonymous principal under
    ``AUTH_MODE=anonymous``) satisfies every role check, so the eventual
    role-gate dependency (Phase 13.F) stays uniform across auth modes."""

    subject: str
    roles: frozenset[str]
    is_anonymous: bool


#: Default principal when ``AUTH_MODE=anonymous`` — wildcard roles so
#: every gate passes with auth disabled. Phase 13.F replaces this with a
#: JWT-derived principal under ``AUTH_MODE=keycloak``.
ANONYMOUS = Principal(subject="anonymous", roles=frozenset({"*"}), is_anonymous=True)


def get_principal(settings: SettingsDep) -> Principal:
    """Resolve the request principal.

    ``AUTH_MODE=anonymous`` (the scaffold default) returns
    :data:`ANONYMOUS`. ``AUTH_MODE=keycloak`` is wired in Phase 13.F;
    until then it is an explicit ``501`` rather than a silent allow, so a
    misconfigured deploy fails loudly instead of running unauthenticated.
    """
    if settings.auth_mode == "anonymous":
        return ANONYMOUS
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Keycloak authentication is not implemented until Phase 13.F",
    )
