# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Keycloak JWT validation (Phase 13.F).

**Local** verification: the realm JWKS is fetched once (via ``httpx2``)
and cached — re-fetched on an unknown ``kid`` (key rotation) — then
access tokens are verified offline with ``pyjwt`` (RS256 signature +
``iss`` / ``aud`` / ``exp``). No per-request round-trip to Keycloak.
"""

import asyncio
from typing import Any

import httpx2
import jwt
from fastapi import HTTPException, status
from jwt import PyJWK

from .settings import Settings


def keycloak_issuer(settings: Settings) -> str:
    base = (settings.keycloak_server_url or "").rstrip("/")
    return f"{base}/realms/{settings.keycloak_realm}"


def keycloak_jwks_uri(settings: Settings) -> str:
    return f"{keycloak_issuer(settings)}/protocol/openid-connect/certs"


class JwksCache:
    """Caches a realm's signing keys; re-fetches on an unknown ``kid``
    (key rotation). Concurrency-safe (single-flight refresh)."""

    def __init__(self, jwks_uri: str) -> None:
        self._jwks_uri = jwks_uri
        self._keys: dict[str, PyJWK] = {}
        self._lock = asyncio.Lock()

    async def signing_key(self, kid: str) -> PyJWK:
        key = self._keys.get(kid)
        if key is not None:
            return key
        async with self._lock:
            if kid in self._keys:  # filled while waiting for the lock
                return self._keys[kid]
            await self._refresh()
        key = self._keys.get(kid)
        if key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="unknown token signing key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return key

    async def _refresh(self) -> None:
        async with httpx2.AsyncClient(timeout=5.0) as client:
            resp = await client.get(self._jwks_uri)
            resp.raise_for_status()
        self._keys = {k["kid"]: PyJWK.from_dict(k) for k in resp.json().get("keys", [])}


async def verify_keycloak_token(
    token: str, *, jwks_cache: JwksCache, issuer: str, audience: str
) -> dict[str, Any]:
    """Verify a Keycloak access token (RS256 + iss/aud/exp) and return its
    claims; raise 401 on any verification failure, 503 if the JWKS can't be
    fetched."""
    try:
        kid = jwt.get_unverified_header(token).get("kid", "")
        signing_key = await jwks_cache.signing_key(kid)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=audience,
            issuer=issuer,
            options={"require": ["exp", "iss", "aud", "sub"]},
        )
    except HTTPException:
        raise
    except httpx2.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="auth backend unavailable",
        ) from exc
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
