# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 13.C: POST /api/v1/parse — node-table serialization.

DB-free: the parser reads the YAML lexicon, not Postgres, so these run
in the fast suite via the TestClient (lifespan warms the grammar once).
"""

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tgllfg.api import create_app
from tgllfg.api.settings import Settings


def _make_app() -> FastAPI:
    return create_app(
        settings=Settings(
            database_url="postgresql+asyncpg://t:t@localhost:5432/t",
            auth_mode="anonymous",
        )
    )


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    with TestClient(_make_app()) as c:
        yield c


def _check_refs(value: object, node_ids: set[str]) -> None:
    if isinstance(value, dict) and "$ref" in value:
        assert value["$ref"] in node_ids, f"dangling f-node ref: {value['$ref']}"
    elif isinstance(value, list):
        for member in value:
            _check_refs(member, node_ids)


def test_parse_known_sentence(client: TestClient) -> None:
    resp = client.post("/api/v1/parse", json={"text": "Kumain ang aso."})
    assert resp.status_code == 200
    body = resp.json()
    assert body["text"] == "Kumain ang aso."
    assert body["meta"]["parse_count"] == len(body["parses"])
    assert body["parses"], "expected at least one complete parse"

    p = body["parses"][0]

    # c-structure node table is internally consistent (every child id resolves).
    cs = p["c_structure"]
    assert cs["root"] in cs["nodes"]
    for node in cs["nodes"].values():
        for child in node["children"]:
            assert child in cs["nodes"]

    # f-structure node table: root resolves and every $ref points at a node.
    fs = p["f_structure"]
    assert fs["root"] in fs["nodes"]
    node_ids = set(fs["nodes"])
    for node in fs["nodes"].values():
        for value in node["feats"].values():
            _check_refs(value, node_ids)

    # a-structure carries a PRED.
    assert p["a_structure"]["pred"]


def test_parse_validation_empty_text(client: TestClient) -> None:
    assert client.post("/api/v1/parse", json={"text": ""}).status_code == 422


def test_parse_validation_nbest_range(client: TestClient) -> None:
    s = "Kumain ang aso."
    assert client.post("/api/v1/parse", json={"text": s, "n_best": 0}).status_code == 422
    assert client.post("/api/v1/parse", json={"text": s, "n_best": 99}).status_code == 422


def test_parse_strict_suppresses_fragments(client: TestClient) -> None:
    # Under strict, fragment output is suppressed when there is no
    # complete parse (mirrors `tgllfg parse --strict`).
    resp = client.post("/api/v1/parse", json={"text": "zzzqqq wxyz", "strict": True})
    assert resp.status_code == 200
    assert resp.json()["fragments"] == []


def test_openapi_lists_parse_route(client: TestClient) -> None:
    schema = client.get("/api/openapi.json").json()
    assert "/api/v1/parse" in schema["paths"]
