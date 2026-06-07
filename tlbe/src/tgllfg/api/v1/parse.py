# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""``POST /api/v1/parse`` — parse a Tagalog sentence (Phase 13.C).

Mirrors the ``tgllfg parse`` CLI over HTTP. The hard part is serializing
the **f-structure graph**: ``FStructure.feats`` holds atoms, nested
``FStructure``s, and frozensets of them, with reentrancy from
structure-sharing / functional uncertainty — a naive recursive dump
would loop or duplicate. So the wire format is a **node table + ID
references**: c-nodes get stable ``c{n}`` ids (DFS pre-order), f-nodes
get stable ``f{n}`` ids (first-visit), and a feat that points at another
f-node serializes as ``{"$ref": "fN"}`` (each f-node expanded once →
cycles safe).

Phase 12.G / §4 breadcrumb — **c-node ↔ f-node correspondence deferred
to Phase 14.** The map "which c-node projects which f-node" comes from
``fstruct/unify.py:solve``'s ``nid_for`` (id(CNode) → NodeId, where
``graph.find`` maps to the canonical ``FStructure.id``), which the
pipeline discards; the synthetic split-path trees in ``pipeline.py``
also assemble parses without a single ``solve`` call. Threading it out
is invasive on the parse hot path, and §4 says to design it against the
inspector's *real* need. This endpoint lays the stable-ID foundation the
correspondence will attach to (an additive ``correspondence`` field) when
the Phase 14 inspector consumes it.
"""

import asyncio
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ...core.common import AStructure, CNode, FStructure
from ...core.pipeline import Fragment, ParseResult, parse_text_with_fragments
from ...fstruct import Diagnostic

from ..deps import require_role
from ..telemetry import TracerDep, traced

parse_router = APIRouter(tags=["parse"])


# --- request -----------------------------------------------------------


class ParseRequest(BaseModel):
    text: str = Field(min_length=1, description="The Tagalog sentence to parse.")
    n_best: int = Field(
        5, ge=1, le=50, description="Cap on the number of complete parses returned."
    )
    strict: bool = Field(
        False,
        description=(
            "Suppress fragment output when no complete parse is found "
            "(mirrors `tgllfg parse --strict`)."
        ),
    )


# --- response DTOs (Pydantic 2) ---------------------------------------


class CNodeModel(BaseModel):
    id: str
    label: str
    children: list[str] = Field(default_factory=list)
    equations: list[str] = Field(default_factory=list)


class CStructure(BaseModel):
    root: str
    nodes: dict[str, CNodeModel]


class FNodeModel(BaseModel):
    id: str
    # Feat values are scalars (str/int/bool), an f-node reference
    # ``{"$ref": "fN"}``, or a list of such (a set-valued attribute).
    feats: dict[str, Any] = Field(default_factory=dict)


class FStructureModel(BaseModel):
    root: str
    nodes: dict[str, FNodeModel]


class AStructureModel(BaseModel):
    pred: str
    roles: list[str]
    mapping: dict[str, str]


class DiagnosticModel(BaseModel):
    id: str
    kind: str
    message: str
    path: list[str] = Field(default_factory=list)
    equation: str | None = None
    cnode_label: str | None = None
    blocking: bool = False
    detail: dict[str, Any] = Field(default_factory=dict)


class ParseModel(BaseModel):
    id: str
    c_structure: CStructure
    f_structure: FStructureModel
    a_structure: AStructureModel
    diagnostics: list[DiagnosticModel] = Field(default_factory=list)


class FragmentModel(BaseModel):
    span: tuple[int, int]
    c_structure: CStructure
    f_structure: FStructureModel
    a_structure: AStructureModel
    diagnostics: list[DiagnosticModel] = Field(default_factory=list)


class ParseMeta(BaseModel):
    n_best: int
    parse_count: int
    fragment_count: int


class ParseResponse(BaseModel):
    text: str
    parses: list[ParseModel] = Field(default_factory=list)
    fragments: list[FragmentModel] = Field(default_factory=list)
    meta: ParseMeta


# --- serialization -----------------------------------------------------


def _member_sort_key(m: object) -> str:
    """Deterministic ordering for set members: f-nodes first (by id),
    then atoms, so set-valued feats serialize stably across runs."""
    if isinstance(m, FStructure):
        return f"0:{m.id:020d}"
    return f"1:{m!r}"


def _ser_value(value: object, ensure: Callable[[FStructure], str]) -> Any:
    if isinstance(value, FStructure):
        return {"$ref": ensure(value)}
    if isinstance(value, (frozenset, set)):
        return [_ser_value(m, ensure) for m in sorted(value, key=_member_sort_key)]
    if value is None or isinstance(value, (str, int, float)):  # bool ⊂ int
        return value
    return str(value)


def serialize_cstructure(root: CNode) -> CStructure:
    nodes: dict[str, CNodeModel] = {}

    def visit(c: CNode) -> str:
        cid = f"c{len(nodes)}"
        # Reserve the slot before recursing so ids are DFS pre-order.
        nodes[cid] = CNodeModel(id=cid, label=c.label, equations=list(c.equations))
        nodes[cid].children = [visit(ch) for ch in c.children]
        return cid

    root_id = visit(root)
    return CStructure(root=root_id, nodes=nodes)


def serialize_fstructure(root: FStructure) -> FStructureModel:
    id_map: dict[int, str] = {}
    nodes: dict[str, FNodeModel] = {}

    def ensure(fs: FStructure) -> str:
        existing = id_map.get(fs.id)
        if existing is not None:
            return existing
        fid = f"f{len(id_map)}"
        id_map[fs.id] = fid
        # Register before populating feats so reentrant / cyclic refs
        # resolve to this id instead of recursing forever.
        nodes[fid] = FNodeModel(id=fid)
        nodes[fid].feats = {k: _ser_value(v, ensure) for k, v in fs.feats.items()}
        return fid

    root_id = ensure(root)
    return FStructureModel(root=root_id, nodes=nodes)


def serialize_astructure(a: AStructure) -> AStructureModel:
    return AStructureModel(pred=a.pred, roles=list(a.roles), mapping=dict(a.mapping))


def serialize_diagnostics(diags: list[Diagnostic]) -> list[DiagnosticModel]:
    return [
        DiagnosticModel(
            id=f"d{i}",
            kind=str(d.kind),
            message=d.message,
            path=list(d.path),
            equation=d.equation,
            cnode_label=d.cnode_label,
            blocking=d.is_blocking(),
            detail={
                k: (v if isinstance(v, (str, int, float, bool)) else str(v))
                for k, v in d.detail.items()
            },
        )
        for i, d in enumerate(diags)
    ]


def _serialize_parse(
    pid: str, parse: tuple[CNode, FStructure, AStructure, list[Diagnostic]]
) -> ParseModel:
    ctree, fstruct, astruct, diags = parse
    return ParseModel(
        id=pid,
        c_structure=serialize_cstructure(ctree),
        f_structure=serialize_fstructure(fstruct),
        a_structure=serialize_astructure(astruct),
        diagnostics=serialize_diagnostics(diags),
    )


def _serialize_fragment(fid: str, frag: Fragment) -> FragmentModel:
    return FragmentModel(
        span=frag.span,
        c_structure=serialize_cstructure(frag.ctree),
        f_structure=serialize_fstructure(frag.fstructure),
        a_structure=serialize_astructure(frag.astructure),
        diagnostics=serialize_diagnostics(frag.diagnostics),
    )


def build_parse_response(
    text: str, result: ParseResult, *, n_best: int, strict: bool
) -> ParseResponse:
    parses = [_serialize_parse(f"p{i}", p) for i, p in enumerate(result.parses)]
    # Fragments only surface on full-parse failure, and `strict` suppresses
    # them entirely (mirrors the CLI). parse_text_with_fragments already
    # returns fragments only when `parses` is empty.
    fragments = (
        []
        if (strict and not result.parses)
        else [_serialize_fragment(f"frag{i}", fr) for i, fr in enumerate(result.fragments)]
    )
    return ParseResponse(
        text=text,
        parses=parses,
        fragments=fragments,
        meta=ParseMeta(
            n_best=n_best, parse_count=len(parses), fragment_count=len(fragments)
        ),
    )


# --- route -------------------------------------------------------------


@parse_router.post(
    "/parse",
    response_model=ParseResponse,
    summary="Parse a Tagalog sentence",
    dependencies=[Depends(require_role("parser:read"))],
)
async def parse(req: ParseRequest, tracer: TracerDep) -> ParseResponse:
    # The parser is synchronous and CPU-bound; offload it to a worker
    # thread so it doesn't block the event loop. The `parse` compute span
    # segments parse-compute from any DB I/O (SQLAlchemy auto-spans) in a
    # trace; it's a no-op when tracing is off.
    with traced(tracer, "parse", n_best=req.n_best, text_len=len(req.text)):
        result = await asyncio.to_thread(
            parse_text_with_fragments, req.text, n_best=req.n_best
        )
    return build_parse_response(req.text, result, n_best=req.n_best, strict=req.strict)
