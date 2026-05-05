# tgllfg/cli/__init__.py

"""Top-level ``tgllfg`` CLI dispatcher (package).

Re-exports ``main`` from :mod:`tgllfg.cli.main` so the console-script
entry point ``tgllfg = "tgllfg.cli:main"`` resolves without change
across the cli.py → cli/ refactor.
"""

from .main import main

__all__ = ["main"]
