"""Backend resolution for the parser's morphological lexicon.

``resolve_morph_data()`` is the single entry point the analyzer
should call when constructing itself. The backend is chosen from
``TGLLFG_LEX_BACKEND``:

* ``yaml`` (default): read the on-disk YAML under ``data/tgl/``.
  Identical to the legacy ``morph.loader.load_morph_data()`` path.
* ``db``: connect to ``DATABASE_URL`` (or the explicit argument),
  build a :class:`LexCache`, and project it through
  :func:`cache_to_morph_data`. Requires the schema to be migrated
  and seeded.

The async DB path is wrapped in ``asyncio.run`` so callers stay
synchronous; ``aload_morph_data_from_url`` is also exported for
contexts that already have an event loop.
"""

from __future__ import annotations

import asyncio
import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from tgllfg.lex.adapter import cache_to_morph_data
from tgllfg.lex.cache import build_cache
from tgllfg.lex.seed import _ensure_async_url
from tgllfg.morph.loader import load_morph_data
from tgllfg.morph.paradigms import MorphData

BACKEND_ENV = "TGLLFG_LEX_BACKEND"
DATABASE_URL_ENV = "DATABASE_URL"


async def aload_morph_data_from_url(database_url: str, iso_code: str = "tgl") -> MorphData:
    """Async load of ``MorphData`` from a Postgres lexicon URL."""
    engine = create_async_engine(_ensure_async_url(database_url), future=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with sessionmaker() as session:
            cache = await build_cache(session)
    finally:
        await engine.dispose()
    return cache_to_morph_data(cache, iso_code=iso_code)


def load_morph_data_from_url(database_url: str, iso_code: str = "tgl") -> MorphData:
    """Synchronous wrapper around :func:`aload_morph_data_from_url`."""
    return asyncio.run(aload_morph_data_from_url(database_url, iso_code))


def resolve_morph_data() -> MorphData:
    """Pick a backend per ``TGLLFG_LEX_BACKEND`` and return the
    fully-loaded :class:`MorphData`.

    Defaults to the YAML backend so the demo and offline contexts
    work without any database. Switching to the DB backend requires
    ``DATABASE_URL`` to be set.
    """
    backend = os.environ.get(BACKEND_ENV, "yaml").lower()
    if backend == "yaml":
        return load_morph_data()
    if backend == "db":
        url = os.environ.get(DATABASE_URL_ENV)
        if not url:
            raise RuntimeError(
                f"{BACKEND_ENV}=db but {DATABASE_URL_ENV} is unset; "
                "set it to a Postgres connection URL or switch the backend."
            )
        return load_morph_data_from_url(url)
    raise RuntimeError(
        f"Unknown {BACKEND_ENV}={backend!r}; expected 'yaml' or 'db'."
    )


__all__ = [
    "BACKEND_ENV",
    "DATABASE_URL_ENV",
    "aload_morph_data_from_url",
    "load_morph_data_from_url",
    "resolve_morph_data",
]
