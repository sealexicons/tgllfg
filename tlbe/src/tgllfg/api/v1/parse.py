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

Phase 14.B.6/.7 — **c-node ↔ f-node correspondence.** Each parse carries a
``correspondence`` field: the projection φ mapping c-node ids to the f-node
ids they project to. ``fstruct/unify.py:solve`` returns it for the normal
(solved) path (.6); the synthetic split-path trees in ``pipeline.py`` — which
assemble parses without a single ``solve`` call — compose it from their glued
halves (.7, see ``pipeline._glue_*``). The correspondence keys f-nodes by
Python object identity (``id(fs)``), not ``FStructure.id``, so a glued parse
holding nodes from independently-solved graphs (whose ``.id`` spaces collide)
keeps distinct nodes distinct.
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
    gloss: str | None = Field(
        default=None,
        description=(
            "The terminal's licensing lexical gloss (the root's English "
            "gloss), or null on non-terminals and glossless word classes "
            "(particles / pronouns / unknowns). Lets the inspector gloss "
            "every terminal — including verbs, which carry no LEMMA "
            "equation — without a separate /lex/search lookup."
        ),
    )


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
    correspondence: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Projection φ: c-node id → the f-node id it projects to (including "
            "glued split-path parses). A c-node whose projection is an atomic or "
            "set value, not a distinct f-node, is omitted."
        ),
    )


class FragmentModel(BaseModel):
    span: tuple[int, int]
    c_structure: CStructure
    f_structure: FStructureModel
    a_structure: AStructureModel
    diagnostics: list[DiagnosticModel] = Field(default_factory=list)
    correspondence: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Projection φ: c-node id → the f-node id it projects to (including "
            "glued split-path parses). A c-node whose projection is an atomic or "
            "set value, not a distinct f-node, is omitted."
        ),
    )


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


def serialize_cstructure(root: CNode) -> tuple[CStructure, dict[int, str]]:
    nodes: dict[str, CNodeModel] = {}
    cid_for: dict[int, str] = {}  # id(CNode) → cN, for the φ join

    def visit(c: CNode) -> str:
        cid = f"c{len(nodes)}"
        # Reserve the slot before recursing so ids are DFS pre-order.
        nodes[cid] = CNodeModel(
            id=cid, label=c.label, equations=list(c.equations), gloss=c.gloss
        )
        cid_for[id(c)] = cid
        nodes[cid].children = [visit(ch) for ch in c.children]
        return cid

    root_id = visit(root)
    return CStructure(root=root_id, nodes=nodes), cid_for


def serialize_fstructure(root: FStructure) -> tuple[FStructureModel, dict[int, str]]:
    # Key by Python object identity, not ``fs.id``: a glued parse can hold
    # FStructure objects from independently-solved graphs whose ``.id`` spaces
    # collide (each FGraph counter starts at 0), which would otherwise merge
    # distinct nodes. Object identity keeps distinct nodes distinct while still
    # collapsing genuinely-shared (reentrant) objects. Returns id(fs) → fN for
    # the φ join.
    fid_for: dict[int, str] = {}
    nodes: dict[str, FNodeModel] = {}

    def ensure(fs: FStructure) -> str:
        key = id(fs)
        existing = fid_for.get(key)
        if existing is not None:
            return existing
        fid = f"f{len(fid_for)}"
        fid_for[key] = fid
        # Register before populating feats so reentrant / cyclic refs
        # resolve to this id instead of recursing forever.
        nodes[fid] = FNodeModel(id=fid)
        nodes[fid].feats = {k: _ser_value(v, ensure) for k, v in fs.feats.items()}
        return fid

    root_id = ensure(root)
    return FStructureModel(root=root_id, nodes=nodes), fid_for


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


def _join_correspondence(
    correspondence: dict[int, int] | None,
    cid_for: dict[int, str],
    fid_for: dict[int, str],
) -> dict[str, str]:
    """Join the solver's ``id(CNode) → id(FStructure object)`` map onto the
    serialized cN / fN ids. C-nodes whose projected f-node isn't in the
    serialized f-structure (atoms / sets, or — pre-glue-path — nothing) are
    dropped."""
    if not correspondence:
        return {}
    wire: dict[str, str] = {}
    for cnode_id, c_id in cid_for.items():
        fobj_id = correspondence.get(cnode_id)
        if fobj_id is None:
            continue
        f_id = fid_for.get(fobj_id)
        if f_id is not None:
            wire[c_id] = f_id
    return wire


def _serialize_parse(
    pid: str,
    parse: tuple[CNode, FStructure, AStructure, list[Diagnostic]],
    correspondence: dict[int, int] | None,
) -> ParseModel:
    ctree, fstruct, astruct, diags = parse
    c_structure, cid_for = serialize_cstructure(ctree)
    f_structure, fid_for = serialize_fstructure(fstruct)
    return ParseModel(
        id=pid,
        c_structure=c_structure,
        f_structure=f_structure,
        a_structure=serialize_astructure(astruct),
        diagnostics=serialize_diagnostics(diags),
        correspondence=_join_correspondence(correspondence, cid_for, fid_for),
    )


def _serialize_fragment(fid: str, frag: Fragment) -> FragmentModel:
    c_structure, cid_for = serialize_cstructure(frag.ctree)
    f_structure, fid_for = serialize_fstructure(frag.fstructure)
    return FragmentModel(
        span=frag.span,
        c_structure=c_structure,
        f_structure=f_structure,
        a_structure=serialize_astructure(frag.astructure),
        diagnostics=serialize_diagnostics(frag.diagnostics),
        correspondence=_join_correspondence(frag.correspondence, cid_for, fid_for),
    )


def build_parse_response(
    text: str, result: ParseResult, *, n_best: int, strict: bool
) -> ParseResponse:
    # `correspondences` aligns 1:1 with `parses` when present; treat an absent
    # list (e.g. glued split-path results) as all-None.
    corrs = result.correspondences or [None] * len(result.parses)
    parses = [
        _serialize_parse(f"p{i}", p, corrs[i]) for i, p in enumerate(result.parses)
    ]
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
