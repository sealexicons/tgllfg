# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Shared FastAPI dependencies and DTOs (Phase 13.A).

Common DI / utility code consumed by the versioned route modules under
:mod:`tgllfg.api.v1`. Phase 13.A provides the request principal
(:func:`get_principal`) and the settings dependency alias; the async DB
session dependency lands in Phase 13.C with its first route consumer.
"""

from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..lex import AsyncLexRepository
from .auth import keycloak_issuer, verify_keycloak_token
from .settings import Settings


def get_request_settings(request: Request) -> Settings:
    """The running app's settings (set by the factory on ``app.state``) so
    DI consumers agree with ``app.state`` / the lifespan instead of
    re-reading the env via the cached :func:`get_settings`."""
    return request.app.state.settings


#: Settings as a FastAPI dependency — the *running app's* settings.
SettingsDep = Annotated[Settings, Depends(get_request_settings)]


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


async def get_principal(request: Request, settings: SettingsDep) -> Principal:
    """Resolve the request principal.

    ``AUTH_MODE=anonymous`` returns :data:`ANONYMOUS` (wildcard roles, so
    every role gate passes — the dev bypass). ``AUTH_MODE=keycloak``
    validates the ``Authorization: Bearer`` access token against the realm
    (local JWKS verification — RS256 signature + iss / aud / exp) and
    builds a principal from its ``realm_access.roles``.
    """
    if settings.auth_mode == "anonymous":
        return ANONYMOUS
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing or malformed bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    claims = await verify_keycloak_token(
        token,
        jwks_cache=request.app.state.jwks_cache,
        issuer=keycloak_issuer(settings),
        audience=settings.keycloak_audience,
    )
    roles = claims.get("realm_access", {}).get("roles", [])
    return Principal(
        subject=str(claims.get("sub", "")),
        roles=frozenset(roles),
        is_anonymous=False,
    )


PrincipalDep = Annotated[Principal, Depends(get_principal)]


def require_role(role: str) -> Callable[..., Principal]:
    """A route dependency that requires ``role``. The anonymous principal's
    ``"*"`` wildcard satisfies any role, so ``AUTH_MODE=anonymous`` keeps
    every route open."""

    def _require(principal: PrincipalDep) -> Principal:
        if "*" in principal.roles or role in principal.roles:
            return principal
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"requires role: {role}"
        )

    return _require


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Yield an :class:`AsyncSession` from the lifespan-built sessionmaker
    (``app.state.sessionmaker``, set in :mod:`tgllfg.api.app`)."""
    sessionmaker = request.app.state.sessionmaker
    async with sessionmaker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_repo(session: SessionDep) -> AsyncLexRepository:
    """The async lexicon repository, bound to the request's DB session."""
    return AsyncLexRepository(session)


RepoDep = Annotated[AsyncLexRepository, Depends(get_repo)]
