# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Application settings (Phase 13.A).

:class:`Settings` is loaded from the environment via ``pydantic-settings``.
Conventional names are read directly (``DATABASE_URL`` — matching the
``tgllfg lex`` CLI and the compose migrate/seed jobs); app-specific knobs
use the ``TGLLFG_`` prefix. Either alias works for each field.
"""

from functools import lru_cache
from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Env-driven service configuration. Extended per bucket — OTel
    (13.E), Keycloak (13.F), CORS — add fields here."""

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", populate_by_name=True
    )

    #: Async SQLAlchemy URL (``postgresql+asyncpg://…``). Shares the
    #: ``DATABASE_URL`` name with the CLI and the compose DB jobs.
    database_url: str = Field(
        default="postgresql+asyncpg://tgllfg:tgllfg@localhost:5432/tgllfg",
        validation_alias=AliasChoices("DATABASE_URL", "TGLLFG_DATABASE_URL"),
    )
    #: ``anonymous`` disables auth and yields a default anonymous
    #: principal (fast local iteration); ``keycloak`` enables JWT
    #: validation (Phase 13.F). Default ``anonymous`` so the scaffold
    #: runs with no auth infrastructure.
    auth_mode: Literal["anonymous", "keycloak"] = Field(
        default="anonymous",
        validation_alias=AliasChoices("TGLLFG_AUTH_MODE", "AUTH_MODE"),
    )
    #: OTLP/gRPC endpoint for traces (e.g. ``http://alloy:4317``). Unset →
    #: tracing is a no-op (Phase 13.E env-gating).
    otel_endpoint: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "OTEL_EXPORTER_OTLP_ENDPOINT", "TGLLFG_OTEL_ENDPOINT"
        ),
    )
    #: ``service.name`` resource attribute for exported traces.
    otel_service_name: str = Field(
        default="tgllfg",
        validation_alias=AliasChoices("OTEL_SERVICE_NAME", "TGLLFG_OTEL_SERVICE_NAME"),
    )
    #: Keycloak base URL (e.g. ``http://keycloak:8080``) for the realm JWKS
    #: + issuer; required when ``auth_mode=keycloak``.
    keycloak_server_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "KEYCLOAK_SERVER_URL", "TGLLFG_KEYCLOAK_SERVER_URL"
        ),
    )
    keycloak_realm: str = Field(
        default="tgllfg",
        validation_alias=AliasChoices("KEYCLOAK_REALM", "TGLLFG_KEYCLOAK_REALM"),
    )
    #: Expected ``aud`` claim (the API client id).
    keycloak_audience: str = Field(
        default="tgllfg-api",
        validation_alias=AliasChoices("KEYCLOAK_AUDIENCE", "TGLLFG_KEYCLOAK_AUDIENCE"),
    )


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide :class:`Settings`, cached. Override via
    ``app.dependency_overrides[get_settings]`` in tests, or pass an
    explicit ``settings`` to :func:`tgllfg.api.create_app`.
    """
    return Settings()
