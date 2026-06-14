# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 13.C: POST /api/v1/parse — node-table serialization.

DB-free: the parser reads the YAML lexicon, not Postgres, so these run in
the fast suite via the TestClient (the compiled grammar is cached, so the
per-test ``api_app`` is cheap). Uses the shared ``api_app`` fixture
(conftest).
"""

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tgllfg.api.v1.parse import serialize_fstructure
from tgllfg.core.common import FStructure


@pytest.fixture
def client(api_app: FastAPI) -> Iterator[TestClient]:
    with TestClient(api_app) as c:
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


def test_serialize_fstructure_distinguishes_colliding_ids() -> None:
    # Phase 14.B.6: two distinct FStructure objects with the same .id (as a
    # glued parse produces from independent graphs) must serialize as two
    # nodes, not be merged. Keys by object identity, not .id.
    child = FStructure(feats={"PRED": "child"}, id=0)
    root = FStructure(feats={"PRED": "root", "SUBJ": child}, id=0)
    model, _ = serialize_fstructure(root)
    assert len(model.nodes) == 2
    subj = model.nodes[model.root].feats["SUBJ"]
    assert isinstance(subj, dict) and subj["$ref"] != model.root


def test_glued_parse_fstructure_not_collapsed(client: TestClient) -> None:
    # Regression for the pre-14.B.6 bug: a colon split-path parse glues
    # f-structures from independently-solved graphs whose .id spaces collide;
    # the serializer must keep distinct nodes distinct (it used to collapse the
    # whole f-structure onto the root).
    resp = client.post(
        "/api/v1/parse", json={"text": "Ang aso ay tumakbo: ang pusa."}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["parses"], "expected a complete (glued) parse"
    fs = body["parses"][0]["f_structure"]
    assert len(fs["nodes"]) > 1, "glued f-structure collapsed to one node"
    app = fs["nodes"][fs["root"]]["feats"].get("APP")
    assert isinstance(app, list) and app, "expected a set-valued APP"
    app_ref = app[0]["$ref"]
    assert app_ref != fs["root"], "APP collapsed onto the root (id collision)"
    assert app_ref in fs["nodes"]


def test_parse_correspondence_maps_cnodes_to_fnodes(client: TestClient) -> None:
    # Phase 14.B.6: the φ correspondence maps c-node ids to the f-node ids they
    # project to (solve-path parse).
    body = client.post("/api/v1/parse", json={"text": "Kumain ang aso."}).json()
    p = body["parses"][0]
    corr = p["correspondence"]
    assert corr, "expected a non-empty correspondence for a solve-path parse"
    c_ids = set(p["c_structure"]["nodes"])
    f_ids = set(p["f_structure"]["nodes"])
    for c_id, f_id in corr.items():
        assert c_id in c_ids, f"correspondence key is not a c-node: {c_id}"
        assert f_id in f_ids, f"correspondence value is not an f-node: {f_id}"
    # The c-structure root projects to the f-structure root.
    assert corr.get(p["c_structure"]["root"]) == p["f_structure"]["root"]


def test_glued_parse_correspondence_composed_from_halves(client: TestClient) -> None:
    # Phase 14.B.7: a glued split-path parse composes its φ correspondence from
    # the two halves' maps plus the synthetic matrix / punct nodes. This input
    # takes the colon-split path, and its pre-half ("Ang aso ay tumakbo") itself
    # rides the ay-fronting split — so it also exercises correspondence
    # composition through the *chained* split.
    body = client.post(
        "/api/v1/parse", json={"text": "Ang aso ay tumakbo: ang pusa."}
    ).json()
    p = body["parses"][0]
    corr = p["correspondence"]
    assert corr, "expected a composed correspondence for a glued parse"
    c_ids = set(p["c_structure"]["nodes"])
    f_ids = set(p["f_structure"]["nodes"])
    for c_id, f_id in corr.items():
        assert c_id in c_ids, f"correspondence key is not a c-node: {c_id}"
        assert f_id in f_ids, f"correspondence value is not an f-node: {f_id}"
    fs = p["f_structure"]
    # The glued matrix c-root projects to the matrix f-root (= the pre-half fs).
    assert corr.get(p["c_structure"]["root"]) == fs["root"]
    # The post-colon half's f-structure (the APP member) is reached by some
    # c-node — proof the post-half's map was unioned in, resolved under object
    # identity (the .6 fix) to a distinct f-node, not collapsed onto the root.
    app = fs["nodes"][fs["root"]]["feats"].get("APP")
    assert isinstance(app, list) and app, "expected a set-valued APP"
    app_ref = app[0]["$ref"]
    assert app_ref != fs["root"]
    assert app_ref in corr.values(), "post-half correspondence not composed in"


def test_appositive_coordination_fnodes_all_map_to_cnodes(client: TestClient) -> None:
    # Phase 14.final.post-9: a colon appositive whose post-half is a comma+at
    # coordination. The appositive glue used to mutate the shared pre-half's
    # APP in place, leaking every spuriously-ambiguous post-half copy into the
    # matrix APP set — only one of which any c-node projected to, leaving the
    # rest φ-orphaned (the inspector couldn't cross-highlight them). After the
    # dedup fix, APP holds exactly the one real coordination, and it *and* its
    # CONJUNCTS members all map back to a c-node.
    text = (
        "Maganda ang panahon dito: ang panahon ng tag-init mula Abril "
        "hanggang Hunyo, at ang panahon ng tag-ulan mula Hulyo hanggang "
        "Oktubre."
    )
    body = client.post("/api/v1/parse", json={"text": text}).json()
    assert body["parses"], "expected a complete (glued) parse"
    p = body["parses"][0]
    fs = p["f_structure"]
    covered = set(p["correspondence"].values())

    app = fs["nodes"][fs["root"]]["feats"].get("APP")
    assert isinstance(app, list) and len(app) == 1, (
        f"APP should hold exactly the one appositive coordination; "
        f"got {0 if app is None else len(app)} (spurious-leak regressed)"
    )
    coord_ref = app[0]["$ref"]
    assert coord_ref in covered, "coordination matrix f-node is φ-orphaned"
    coord = fs["nodes"][coord_ref]
    assert coord["feats"].get("COORD") == "AND"
    conjuncts = coord["feats"].get("CONJUNCTS")
    assert isinstance(conjuncts, list) and len(conjuncts) == 2
    for member in conjuncts:
        assert member["$ref"] in covered, f"conjunct {member['$ref']} is φ-orphaned"


def test_synthetic_coordination_cnode_carries_equations(client: TestClient) -> None:
    # Phase 14.final.post-9: the pipeline-synthesized COORD=AND matrix c-node
    # (and its coordinator leaf) now carry the chart-rule equations they stand
    # in for, so the inspector's c-node popover shows real functional structure
    # instead of "No functional equations".
    text = (
        "Maganda ang panahon dito: ang panahon ng tag-init mula Abril "
        "hanggang Hunyo, at ang panahon ng tag-ulan mula Hulyo hanggang "
        "Oktubre."
    )
    body = client.post("/api/v1/parse", json={"text": text}).json()
    nodes = body["parses"][0]["c_structure"]["nodes"]
    coord = [n for n in nodes.values() if n["label"].startswith("NP[CASE=NOM,COORD=AND]")]
    assert coord, "no synthesized COORD=AND matrix c-node in the serialized tree"
    eqs = coord[0]["equations"]
    assert eqs, "coordination matrix c-node serialized with empty equations"
    joined = " ".join(eqs)
    assert "CONJUNCTS" in joined and "CASE" in joined
    coordinator = [n for n in nodes.values() if n["label"] == "PART[COORD=AND]"]
    assert coordinator and coordinator[0]["equations"], (
        "coordinator leaf serialized with empty equations"
    )
