# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""``GET /api/v1/lex/search`` — fuzzy lemma lookup (Phase 13.C.2).

Trigram (pg_trgm) similarity search over lemma citation forms, served
through the async lexicon repository (:class:`AsyncLexRepository`). The
first DB-backed route — it consumes the ``get_repo`` dependency, which in
turn yields a request-scoped ``AsyncSession`` (:mod:`tgllfg.api.deps`).
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from ..deps import RepoDep, require_role

lex_router = APIRouter(tags=["lex"])


class LemmaMatchModel(BaseModel):
    id: str
    language_id: str
    citation_form: str
    pos: str
    gloss: str | None = None
    score: float


class LexSearchResponse(BaseModel):
    query: str
    total: int
    limit: int | None
    offset: int | None
    matches: list[LemmaMatchModel]


@lex_router.get(
    "/lex/search",
    response_model=LexSearchResponse,
    summary="Fuzzy lemma search",
    dependencies=[Depends(require_role("lex:read"))],
)
async def lex_search(
    repo: RepoDep,
    q: str = Query(min_length=1, description="Fuzzy query against lemma citation forms."),
    limit: int | None = Query(
        None, ge=1, le=100, description="Max matches to return; omit to return all."
    ),
    offset: int | None = Query(
        None, ge=0, description="Matches to skip; omit to start from the top."
    ),
) -> LexSearchResponse:
    total = await repo.count_lemma_matches(q)
    matches = await repo.search_lemmas(q, limit=limit, offset=offset)
    return LexSearchResponse(
        query=q,
        total=total,
        limit=limit,
        offset=offset,
        matches=[
            LemmaMatchModel(
                id=str(mt.id),
                language_id=str(mt.language_id),
                citation_form=mt.citation_form,
                pos=mt.pos,
                gloss=mt.gloss,
                score=mt.score,
            )
            for mt in matches
        ],
    )
