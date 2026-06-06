# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 13.F: Keycloak JWT authn/authz on the API routes.

DB-free: an RSA keypair signs test access tokens and a fake JWKS cache
returns the public key (no httpx2 fetch). The app runs in keycloak mode,
so `/parse` (which requires `parser:read`) enforces a valid token + role
across the cases below.
"""

import json
import time
from collections.abc import Iterator

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from jwt import PyJWK
from jwt.algorithms import RSAAlgorithm

from tgllfg.api import create_app
from tgllfg.api.settings import Settings

_KID = "test-key"
_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_ISSUER = "http://kc.test/realms/tgllfg"
_AUDIENCE = "tgllfg-api"
_BODY = {"text": "Kumain ang aso."}


def _public_jwk() -> PyJWK:
    data = json.loads(RSAAlgorithm.to_jwk(_PRIVATE_KEY.public_key()))
    data.update({"kid": _KID, "alg": "RS256", "use": "sig"})
    return PyJWK.from_dict(data)


class _FakeJwks:
    async def signing_key(self, kid: str) -> PyJWK:
        return _public_jwk()


def _token(*, roles: list[str], exp_delta: int = 300, aud: str = _AUDIENCE) -> str:
    now = int(time.time())
    claims = {
        "sub": "user-123",
        "iss": _ISSUER,
        "aud": aud,
        "exp": now + exp_delta,
        "iat": now,
        "realm_access": {"roles": roles},
    }
    return jwt.encode(claims, _PRIVATE_KEY, algorithm="RS256", headers={"kid": _KID})


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def kc_client() -> Iterator[TestClient]:
    app = create_app(
        settings=Settings(
            database_url="postgresql+asyncpg://t:t@localhost:5432/t",
            auth_mode="keycloak",
            keycloak_server_url="http://kc.test",
            keycloak_realm="tgllfg",
            keycloak_audience=_AUDIENCE,
        )
    )
    # Injected before TestClient enters, so the lifespan keeps it (no real
    # JWKS fetch).
    app.state.jwks_cache = _FakeJwks()
    with TestClient(app) as client:
        yield client


def test_valid_token_with_role_allows(kc_client: TestClient) -> None:
    headers = _bearer(_token(roles=["parser:read"]))
    resp = kc_client.post("/api/v1/parse", json=_BODY, headers=headers)
    assert resp.status_code == 200


def test_missing_token_is_401(kc_client: TestClient) -> None:
    assert kc_client.post("/api/v1/parse", json=_BODY).status_code == 401


def test_malformed_token_is_401(kc_client: TestClient) -> None:
    resp = kc_client.post("/api/v1/parse", json=_BODY, headers=_bearer("not-a-jwt"))
    assert resp.status_code == 401


def test_token_without_required_role_is_403(kc_client: TestClient) -> None:
    headers = _bearer(_token(roles=["lex:read"]))
    resp = kc_client.post("/api/v1/parse", json=_BODY, headers=headers)
    assert resp.status_code == 403


def test_expired_token_is_401(kc_client: TestClient) -> None:
    headers = _bearer(_token(roles=["parser:read"], exp_delta=-10))
    resp = kc_client.post("/api/v1/parse", json=_BODY, headers=headers)
    assert resp.status_code == 401


def test_wrong_audience_is_401(kc_client: TestClient) -> None:
    headers = _bearer(_token(roles=["parser:read"], aud="other-api"))
    resp = kc_client.post("/api/v1/parse", json=_BODY, headers=headers)
    assert resp.status_code == 401
