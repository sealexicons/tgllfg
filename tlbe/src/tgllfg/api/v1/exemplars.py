# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""``GET /api/v1/exemplars`` — corpus exemplars for the parse picker (14.final.post-6).

Serves the naturalistic-tier corpus (``data/tgl/exemplars/``) as a
pre-structured, slimmed payload shaped for the ``tlfe`` exemplar picker:
each source (a tracked ``.jsonl``) is grouped ``source → section →
sentence``, every sentence carrying only ``{locator, sentence, text}``
(the normalized text). The per-exemplar gloss / OCR-provenance fields and
the licensed reference PDFs are dropped — only what the picker needs to
populate the input crosses the wire.

The section / sentence split is the locator's last ``/`` (``page-2/numbered/sent-1``
→ section ``page-2/numbered``, sentence ``sent-1``); a locator with no ``/``
falls back to an empty section carrying the whole locator as the sentence.

Reuses the Phase 12.F audit loader (:func:`tgllfg.audit.common.load_tasks`),
so the same filtering applies — ``marked_ungrammatical`` / ``ignore`` and
text-less entries are skipped, ``text_normalized`` preferred — and the
affix-only ``wave1-rb86-verbs`` (no pickable text) drops out. The index is
built once per exemplars dir (``lru_cache``): the corpus is static in the
deployed image.
"""

import asyncio
import re
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ...audit.common import WAVE_FILES, default_exemplars_dir, load_tasks
from ..deps import require_role

exemplars_router = APIRouter(tags=["exemplars"])


class ExemplarSentence(BaseModel):
    locator: str  # full locator, e.g. "ANG MANOK/sent-1"
    sentence: str  # the trailing locator segment, e.g. "sent-1"
    text: str  # normalized exemplar text


class ExemplarSection(BaseModel):
    section: str  # locator minus its trailing segment, e.g. "ANG MANOK" ("" if none)
    sentences: list[ExemplarSentence]


class ExemplarSource(BaseModel):
    source: str  # the tracked .jsonl / wave id, e.g. "wave1-exemplars"
    sections: list[ExemplarSection]


class ExemplarsResponse(BaseModel):
    sources: list[ExemplarSource]


def _natural_key(s: str) -> str:
    """Sort key ordering embedded numbers numerically (so ``page-2`` <
    ``page-13`` and ``sent-1`` < ``sent-10``): zero-pad each digit run to a
    fixed width. Returning a plain string keeps the key trivially — and
    type-cleanly — comparable."""
    return re.sub(r"\d+", lambda m: m.group().zfill(12), s.lower())


@lru_cache(maxsize=4)
def _build_index(exemplars_dir: str) -> ExemplarsResponse:
    """Group the corpus into source → section → sentence, ordered for the
    picker: sources in canonical wave order, sections + sentences by
    :func:`_natural_key`. Empty sources (no pickable text) never appear,
    since :func:`load_tasks` drops their text-less entries."""
    by_source: dict[str, dict[str, list[ExemplarSentence]]] = {}
    for wave_id, _src, locator, text in load_tasks(Path(exemplars_dir)):
        section, sep, sentence = locator.rpartition("/")
        if not sep:  # no "/" → the whole locator is the sentence label
            section, sentence = "", locator
        by_source.setdefault(wave_id, {}).setdefault(section, []).append(
            ExemplarSentence(locator=locator, sentence=sentence, text=text)
        )
    wave_order = {wave_id: i for i, (wave_id, _fn) in enumerate(WAVE_FILES)}
    sources: list[ExemplarSource] = []
    for wave_id in sorted(by_source, key=lambda w: wave_order.get(w, len(WAVE_FILES))):
        sections = [
            ExemplarSection(
                section=section,
                sentences=sorted(
                    by_source[wave_id][section], key=lambda s: _natural_key(s.sentence)
                ),
            )
            for section in sorted(by_source[wave_id], key=_natural_key)
        ]
        sources.append(ExemplarSource(source=wave_id, sections=sections))
    return ExemplarsResponse(sources=sources)


def get_exemplars_dir() -> Path:
    """The corpus directory; overridable in tests / via ``$TGLLFG_EXEMPLARS_DIR``."""
    return default_exemplars_dir()


ExemplarsDirDep = Annotated[Path, Depends(get_exemplars_dir)]


@exemplars_router.get(
    "/exemplars",
    response_model=ExemplarsResponse,
    summary="List corpus exemplars for the parse picker",
    dependencies=[Depends(require_role("parser:read"))],
)
async def list_exemplars(exemplars_dir: ExemplarsDirDep) -> ExemplarsResponse:
    # Disk read + grouping runs off the event loop; cached per dir thereafter.
    return await asyncio.to_thread(_build_index, str(exemplars_dir))
