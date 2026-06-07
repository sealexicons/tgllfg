# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 13.C.2: GET /api/v1/lex/search — pg_trgm fuzzy lemma lookup.

The HTTP layer is tested DB-free by overriding the repo dependency with a
fake (on the shared ``api_app`` fixture); the pg_trgm query itself is
tested against a real Postgres 17 testcontainer (postgres-marked).
"""

import asyncio
from collections.abc import AsyncIterator, Iterator
from uuid import uuid4

import pytest
import pytest_asyncio
from alembic import command
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer  # type: ignore[import-untyped]

from tgllfg.api.deps import get_repo
from tgllfg.lex import build_alembic_config
from tgllfg.lex.repo import AsyncLexRepository, LemmaMatch


# --- DB-free route tests (fake repo) ----------------------------------


class _FakeRepo:
    async def search_lemmas(
        self, query: str, *, limit: int | None = None, offset: int | None = None
    ) -> list[LemmaMatch]:
        return [
            LemmaMatch(
                id=uuid4(), language_id=uuid4(), citation_form="aso",
                pos="NOUN", gloss="dog", score=1.0,
            ),
            LemmaMatch(
                id=uuid4(), language_id=uuid4(), citation_form="asong",
                pos="NOUN", gloss=None, score=0.5,
            ),
        ]

    async def count_lemma_matches(self, query: str) -> int:
        return 2


@pytest.fixture
def client(api_app: FastAPI) -> Iterator[TestClient]:
    api_app.dependency_overrides[get_repo] = _FakeRepo
    with TestClient(api_app) as c:
        yield c


def test_lex_search_returns_matches(client: TestClient) -> None:
    resp = client.get("/api/v1/lex/search", params={"q": "aso"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["query"] == "aso"
    assert body["total"] == 2
    assert body["limit"] is None  # omitted → no cap (all matches)
    assert body["offset"] is None
    assert [m["citation_form"] for m in body["matches"]] == ["aso", "asong"]
    assert body["matches"][0]["score"] == 1.0


def test_lex_search_requires_q(client: TestClient) -> None:
    assert client.get("/api/v1/lex/search").status_code == 422
    assert client.get("/api/v1/lex/search", params={"q": ""}).status_code == 422


def test_lex_search_limit_range(client: TestClient) -> None:
    base = {"q": "a"}
    assert client.get("/api/v1/lex/search", params={**base, "limit": 0}).status_code == 422
    assert client.get("/api/v1/lex/search", params={**base, "limit": 999}).status_code == 422


# --- pg_trgm query test (real Postgres) -------------------------------


@pytest_asyncio.fixture
async def migrated_engine(
    postgres_container: PostgresContainer,
) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(postgres_container.get_connection_url(), future=True)
    sm = async_sessionmaker(engine, expire_on_commit=False)
    async with sm() as session:
        await session.execute(text("DROP SCHEMA public CASCADE"))
        await session.execute(text("CREATE SCHEMA public"))
        await session.execute(text("DROP EXTENSION IF EXISTS pg_trgm"))
        await session.execute(text("DROP EXTENSION IF EXISTS pgcrypto"))
        await session.commit()
    cfg = build_alembic_config(postgres_container.get_connection_url())
    await asyncio.to_thread(command.upgrade, cfg, "head")
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.mark.postgres
async def test_search_lemmas_trgm(migrated_engine: AsyncEngine) -> None:
    sm = async_sessionmaker(migrated_engine, expire_on_commit=False)
    async with sm() as session:
        await session.execute(
            text("INSERT INTO language (iso_code, name) VALUES ('tgl', 'Tagalog')")
        )
        lang = (
            await session.execute(text("SELECT id FROM language WHERE iso_code = 'tgl'"))
        ).scalar_one()
        for cf in ("aso", "asong", "pusa", "bahay"):
            await session.execute(
                text(
                    "INSERT INTO lemma (language_id, citation_form, pos) "
                    "VALUES (:lang, :cf, 'NOUN')"
                ),
                {"lang": lang, "cf": cf},
            )
        await session.commit()

        repo = AsyncLexRepository(session)
        matches = await repo.search_lemmas("aso", limit=10)
        forms = [m.citation_form for m in matches]
        assert "aso" in forms
        assert matches[0].citation_form == "aso"  # exact match → highest similarity
        assert "pusa" not in forms  # dissimilar, below the trgm threshold
        assert all(m.score > 0 for m in matches)

        # pagination: count is the unpaginated total; omitting limit returns
        # all matches; offset skips the top hit.
        total = await repo.count_lemma_matches("aso")
        assert total == len(forms)
        assert len(await repo.search_lemmas("aso")) == total
        paged = await repo.search_lemmas("aso", limit=10, offset=1)
        assert matches[0].citation_form not in {p.citation_form for p in paged}
