"""Phase 4 §7.3: Wackernagel 2P clitic placement.

Tagalog clitics (pronominal `ko`, `mo`, `niya`, ... and adverbial
`na`, `pa`, `ba`, `daw`/`raw`, `din`/`rin`, `lang`, `nga`, `pala`,
`kasi`, ...) attach in second position — immediately after the
first prosodic word of the clause. Within the cluster they follow
a fixed order (Schachter & Otanes 1972 §6.7).

This package provides a pre-parse reordering pass: it identifies
clitics in the morph-analyzed token sequence, pulls them to a
canonical post-verbal position, and sorts the cluster by priority.
The Earley parser then sees a normalized token order it can match
with V-initial clausal rules. The reordering is invisible to the
morphology and to the grammar itself — only the pipeline glue
calls it.
"""

from tgllfg.clitics.placement import (
    CliticOrder,
    load_clitic_order,
    reorder_clitics,
)

__all__ = ["CliticOrder", "load_clitic_order", "reorder_clitics"]
