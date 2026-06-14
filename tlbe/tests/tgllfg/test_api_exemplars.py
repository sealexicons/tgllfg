# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 14.final.post-6: GET /api/v1/exemplars — picker-shaped corpus.

DB-free: the route reads the exemplar corpus off disk, so the test points
``get_exemplars_dir`` at a tiny temp corpus and asserts the grouping,
ordering, and filtering — no Postgres, no real (licensed) exemplars.
"""

import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tgllfg.api.v1.exemplars import get_exemplars_dir


def _write(directory: Path, name: str, records: list[dict]) -> None:
    with (directory / name).open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


@pytest.fixture
def exemplars_client(api_app: FastAPI, tmp_path: Path) -> Iterator[TestClient]:
    # wave3 file written first, but canonical wave order must put wave1 first.
    _write(
        tmp_path,
        "wave3-so1972.jsonl",
        [
            {"source": "so1972", "locator": "page-10/sent-2", "text_normalized": "B"},
            {"source": "so1972", "locator": "page-10/sent-10", "text_normalized": "J"},
            {"source": "so1972", "locator": "page-2/sent-1", "text_normalized": "A"},
            # marked ungrammatical → skipped
            {
                "source": "so1972",
                "locator": "page-10/sent-1",
                "text_normalized": "x",
                "marked_ungrammatical": True,
            },
        ],
    )
    _write(
        tmp_path,
        "wave1-exemplars.jsonl",
        [
            {"source": "rg81", "locator": "ANG MANOK/sent-1", "text_normalized": "first"},
            {"source": "rg81", "locator": "loose", "text_normalized": "noslash"},
            # empty text → skipped
            {"source": "rg81", "locator": "ANG MANOK/sent-2", "text_normalized": ""},
        ],
    )
    # An affix-only / textless file yields no pickable sentences → absent source.
    _write(
        tmp_path,
        "wave1-rb86-verbs.jsonl",
        [{"source": "rb86", "locator": "page-10/ABOT", "base": "abot", "gloss": "reach"}],
    )
    api_app.dependency_overrides[get_exemplars_dir] = lambda: tmp_path
    with TestClient(api_app) as client:
        yield client
    api_app.dependency_overrides.clear()


def test_sources_in_canonical_wave_order_skipping_empty(
    exemplars_client: TestClient,
) -> None:
    body = exemplars_client.get("/api/v1/exemplars").json()
    # wave1 before wave3 (canonical, not file-write order); the textless
    # wave1-rb86-verbs source is absent.
    assert [s["source"] for s in body["sources"]] == ["wave1-exemplars", "wave3-so1972"]


def test_section_and_sentence_grouping_with_fallback(
    exemplars_client: TestClient,
) -> None:
    body = exemplars_client.get("/api/v1/exemplars").json()
    w1 = body["sources"][0]
    # No-slash locator falls back to an empty section; sections natural-sorted.
    assert [sec["section"] for sec in w1["sections"]] == ["", "ANG MANOK"]
    loose = w1["sections"][0]["sentences"]
    assert [(s["locator"], s["sentence"]) for s in loose] == [("loose", "loose")]
    # Empty-text sent-2 dropped; sent-1 carries its normalized text.
    angmanok = w1["sections"][1]["sentences"]
    assert [(s["sentence"], s["text"]) for s in angmanok] == [("sent-1", "first")]


def test_natural_ordering_and_ungrammatical_filter(
    exemplars_client: TestClient,
) -> None:
    body = exemplars_client.get("/api/v1/exemplars").json()
    w3 = body["sources"][1]
    # page-2 before page-10 numerically (not lexically).
    assert [sec["section"] for sec in w3["sections"]] == ["page-2", "page-10"]
    page10 = w3["sections"][1]["sentences"]
    # sent-1 was marked ungrammatical (skipped); sent-2 before sent-10.
    assert [s["sentence"] for s in page10] == ["sent-2", "sent-10"]


def test_requires_no_query_and_returns_200(exemplars_client: TestClient) -> None:
    assert exemplars_client.get("/api/v1/exemplars").status_code == 200
