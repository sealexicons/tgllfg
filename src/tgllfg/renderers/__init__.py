# tgllfg/renderers/__init__.py

"""Pretty-printers for c-, f-, and a-structures.

Re-exports the current text / JSON renderers from :mod:`tgllfg.renderers.text`.
Future output formats (GraphViz dot, HTML, etc.) live in sibling
modules and may be re-exported here as they land.
"""

from .text import render_a, render_c, render_f

__all__ = ["render_a", "render_c", "render_f"]
