"""Pre-parse Wackernagel-cluster reordering.

Algorithm
---------

1. Scan the morph-analyzed token sequence for the **placement
   anchor** — by default the first verb token ("V token"). When no
   verb is present (Phase 5e Commit 22 lift of the Phase 4 §7.3
   verbless-fragment deferral), fall back to the first non-clitic,
   non-punctuation, non-``PART[POLARITY=NEG]`` token. This covers
   verbless predicate constructions like ``Maganda na ka``
   "You are beautiful already" (adj-pred + adv enclitic + 2sg-NOM
   clitic), where ``maganda`` serves as the predicate anchor and
   the cluster is built post-anchor exactly as in the verbed case.
2. Collect every other token whose primary analysis carries
   ``is_clitic=True`` (any analysis among its candidates). These are
   pronominal clitics (``PRON``) and adverbial enclitics (``PART``).
   **Exception** (Phase 5c §7.8 follow-on): a pronominal clitic
   immediately following a NOUN is the possessor of that noun
   (``ang libro ko``), not a clause-level clitic. Such tokens are
   left in place so the grammar's NP-internal possessive rule
   binds them as ``POSS``.
3. Remove the remaining clitics from their original positions,
   leaving a cluster-free skeleton.
4. Insert all moved clitics immediately after the anchor, sorted
   by the priority loaded from ``data/tgl/clitic_order.yaml``.
   Clitics not in the priority table sort after the listed ones
   (priority = ``DEFAULT_PRIORITY``).

Tokens that are not clitics keep their original relative order.
Words preceding the anchor (e.g. the negation particle ``hindi``)
are unaffected — they remain ahead of the anchor. Any non-possessor
clitic appearing before the anchor is hoisted out and lands in the
post-anchor cluster, which is the desired Wackernagel surface form.

If the input sentence has neither a verb nor any other anchor
candidate (e.g., the input is empty, all clitics, or only
punctuation), no reordering is performed.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import yaml

from tgllfg.common import MorphAnalysis

DEFAULT_PRIORITY: int = 999

_DEFAULT_DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "tgl"


@dataclass(frozen=True)
class CliticOrder:
    """Priority table for clitic surfaces. Lower priority sorts
    earlier in the cluster."""

    priorities: Mapping[str, int]

    def priority_for(self, surface: str) -> int:
        return self.priorities.get(surface.lower(), DEFAULT_PRIORITY)


def load_clitic_order(data_dir: Path | None = None) -> CliticOrder:
    """Load the priority table from ``clitic_order.yaml``."""
    base = Path(data_dir) if data_dir is not None else _DEFAULT_DATA_DIR
    path = base / "clitic_order.yaml"
    if not path.exists():
        return CliticOrder(priorities={})
    with path.open(encoding="utf-8") as fh:
        loaded = yaml.safe_load(fh) or []
    if not isinstance(loaded, list):
        raise ValueError(f"{path}: expected top-level list")
    priorities: dict[str, int] = {}
    for i, rec in enumerate(loaded):
        if "surface" not in rec or "priority" not in rec:
            raise ValueError(
                f"{path}[{i}]: clitic_order entry must have 'surface' and 'priority'"
            )
        priorities[str(rec["surface"]).lower()] = int(rec["priority"])
    return CliticOrder(priorities=priorities)


# Module-level cached instance — loaded once.
_default_order: CliticOrder | None = None


def _get_default_order() -> CliticOrder:
    global _default_order
    if _default_order is None:
        _default_order = load_clitic_order()
    return _default_order


def _is_clitic_token(cands: list[MorphAnalysis]) -> bool:
    """A token is treated as a clitic if any of its candidate analyses
    declares ``is_clitic=True``."""
    return any(ma.feats.get("is_clitic") is True for ma in cands)


def _is_verb_token(cands: list[MorphAnalysis]) -> bool:
    return any(ma.pos == "VERB" for ma in cands)


def _is_neg_part(cands: list[MorphAnalysis]) -> bool:
    """``PART[POLARITY=NEG]`` — ``hindi`` / ``huwag``. These sit
    pre-predicate and don't serve as the placement anchor."""
    return any(
        ma.pos == "PART" and ma.feats.get("POLARITY") == "NEG"
        for ma in cands
    )


def _is_punct_token(cands: list[MorphAnalysis]) -> bool:
    return any(ma.pos == "PUNCT" for ma in cands)


def _find_verbless_anchor(
    analyses: list[list[MorphAnalysis]],
) -> int | None:
    """Phase 5e Commit 22: find the placement anchor for verbless
    inputs. The anchor is the first token that's not a clitic, not
    ``PART[POLARITY=NEG]``, and not punctuation. This covers
    NOUN/ADJ/ADP predicate heads (``Maganda na ka``,
    ``Bata ka``, ``Dito siya``) and lets the same cluster machinery
    used for verbed clauses apply uniformly.

    Returns ``None`` if no anchor is found (input is empty, all
    clitics, or only punctuation / NEG particles). Caller falls
    back to no-op."""
    for i, cands in enumerate(analyses):
        if not cands:
            continue
        if _is_clitic_token(cands):
            continue
        if _is_neg_part(cands):
            continue
        if _is_punct_token(cands):
            continue
        return i
    return None


def _surface_for_priority(cands: list[MorphAnalysis]) -> str:
    """The surface used to look up priority. Use the first analysis's
    lemma — clitics have a stable canonical form (``mo``, ``na``, etc.)
    even when the grammar would treat them with multiple senses."""
    if not cands:
        return ""
    return cands[0].lemma


def _is_pron_clitic(cands: list[MorphAnalysis]) -> bool:
    return any(
        ma.feats.get("is_clitic") is True and ma.pos == "PRON" for ma in cands
    )


def _is_adv_clitic(cands: list[MorphAnalysis]) -> bool:
    return any(
        ma.feats.get("is_clitic") is True and ma.pos == "PART" for ma in cands
    )


def _is_post_noun_pron(
    analyses: list[list[MorphAnalysis]], i: int
) -> bool:
    """True if ``analyses[i]`` is a pronominal clitic immediately
    preceded by a NOUN-reading token.

    Phase 5c §7.8 follow-on: in the pronominal possessive form
    (``ang libro ko`` / ``ang aklat mo`` / etc.) the GEN pronoun
    is the possessor of the head noun, NOT a clause-level
    argument. The §7.3 Wackernagel pass would otherwise hoist
    the pronoun out of its post-N possessive position into the
    post-V cluster, where the grammar reads it as an OBJ /
    OBJ-AGENT clitic instead. Suppressing the move here keeps
    the pronoun in place so the existing
    ``NP[CASE=X] → NP[CASE=X] NP[CASE=GEN]`` possessive rule fires.
    """
    if i == 0:
        return False
    if not _is_pron_clitic(analyses[i]):
        return False
    prev_pos = {ma.pos for ma in analyses[i - 1]}
    return "NOUN" in prev_pos or "N" in prev_pos


def _is_pre_linker_pron(
    analyses: list[list[MorphAnalysis]], i: int
) -> bool:
    """True if ``analyses[i]`` is a pronominal clitic immediately
    followed by a bound ``-ng`` linker (``LINK=NG`` PART).

    Phase 5d Commit 6: in the possessive-linker RC form
    (``aklat kong binasa`` "the book that I read") the pronoun is
    the possessor of the head noun AND the actor of the relative
    clause's non-AV verb. The pronoun was tokenized as part of a
    fused ``Vng`` form (``kong`` / ``mong`` / ``niyang``) and
    ``split_linker_ng`` separated it into PRON + ``-ng`` PART.
    The §7.3 Wackernagel pass would otherwise pull the pronoun
    into the post-V cluster, leaving the orphan ``-ng`` linker
    floating and breaking the construction. Suppressing the move
    keeps PRON adjacent to its linker so the new
    ``NP → NP PRON PART[LINK=NG] S_GAP_NA`` wrap rule fires.

    Note: this also fires for ``isda kong kinain`` (head noun
    without its own linker) — which is the same construction.
    Both are kept in place uniformly.
    """
    if not _is_pron_clitic(analyses[i]):
        return False
    if i + 1 >= len(analyses):
        return False
    next_cands = analyses[i + 1]
    return any(
        ma.pos == "PART" and ma.feats.get("LINK") == "NG"
        for ma in next_cands
    )


def _is_post_embedded_v_pron(
    analyses: list[list[MorphAnalysis]], i: int, matrix_v_idx: int
) -> bool:
    """True if ``analyses[i]`` is a pronominal clitic immediately
    preceded by a VERB token that is NOT the matrix verb.

    Phase 5d Commit 10: in constructions with a relative clause
    (``Tumakbo ang batang kinain ko`` "the child I-ate ran"), the
    pronoun ``ko`` is an argument of the embedded RC verb
    ``kinain`` (the OV-actor / OBJ-AGENT), not a clause-level
    argument of the matrix ``tumakbo``. Without this check the
    Wackernagel pass would hoist ``ko`` into the matrix's post-V
    cluster, breaking the RC analysis (the OV S_GAP frame requires
    a GEN-NP after the V).

    The check distinguishes this from the regular Wackernagel case
    where the PRON sits in the matrix V's post-V cluster: there
    the preceding VERB token IS the matrix verb. Only suppress the
    move when the preceding VERB is some other (embedded) V.
    """
    if i == 0:
        return False
    if not _is_pron_clitic(analyses[i]):
        return False
    prev_pos = {ma.pos for ma in analyses[i - 1]}
    if "VERB" not in prev_pos:
        return False
    return (i - 1) != matrix_v_idx


def disambiguate_homophone_clitics(
    analyses: list[list[MorphAnalysis]],
) -> list[list[MorphAnalysis]]:
    """Disambiguate homophone tokens that carry both clitic and
    non-clitic analyses (notably ``na``, which is both the aspectual
    second-position enclitic ``ALREADY`` and the standalone linker).

    The decision is left-context-driven:

    * If the preceding content token is a NOUN, the surface here is
      almost certainly the linker (``aklat na binasa``, ``bata na
      malaki``). Drop the clitic analyses so placement leaves the
      token in place and the grammar's relativization rules see the
      linker reading.
    * If the preceding token is a VERB (or PRON in cluster position),
      the surface here is the aspectual / Wackernagel enclitic
      (``kumain na``, ``kinain mo na``). Drop the linker analyses so
      placement moves the token to the cluster. **Exception** for
      Phase 4 §7.10: when the PRON is preceded by a control verb
      (``CTRL_CLASS != NONE``), the PRON is the experiencer / pivot
      and the following ``na`` is the linker introducing XCOMP
      (``Kaya namin na kumain``). Preserve linker readings in that
      case.
    * Otherwise (sentence-initial, after a clitic, after punctuation),
      leave both readings in place — the parser will pick whichever
      yields a complete f-structure, or the placement pass's own
      cluster-slot filter will resolve it.

    Returns a new list; analyses lists are not mutated in place.
    """
    out: list[list[MorphAnalysis]] = []
    for i, cands in enumerate(analyses):
        has_clitic = any(ma.feats.get("is_clitic") is True for ma in cands)
        has_non_clitic = any(ma.feats.get("is_clitic") is not True for ma in cands)
        if not (has_clitic and has_non_clitic):
            out.append(cands)
            continue
        prev = analyses[i - 1] if i > 0 else None
        prev_pos = (
            {ma.pos for ma in prev} if prev is not None else set()
        )
        if "NOUN" in prev_pos or "N" in prev_pos:
            out.append([ma for ma in cands if ma.feats.get("is_clitic") is not True])
        elif prev is not None and any(
            ma.pos in ("DET", "ADP") and ma.feats.get("DEM") is True
            for ma in prev
        ):
            # Phase 5e Commit 16 (corrected in Commit 17):
            # demonstrative DET/ADP followed by ``na`` is the linker
            # for pre-modifier dem (``iyan na bata`` / ``iyon na
            # bata`` / ``niyan na isda``) and for the dem-on-RC
            # construction (``batang ito na kumain``). The dem
            # carries CASE/MARKER/DEIXIS; the following ``na``
            # introduces the head N or the relative-clause body —
            # never the aspectual ``ALREADY``. PROX dems take the
            # bound ``-ng`` linker, which is unambiguously a linker
            # (no clitic homophone), so this branch matters only for
            # the MED / DIST surface forms.
            #
            # Note on the boolean check: morph entries set
            # ``DEM: YES`` in particles.yaml, which YAML parses as
            # the Python boolean ``True``. The Phase 5e Commit 16
            # version of this branch compared against the literal
            # string ``"YES"`` and silently never fired; the parses
            # that appeared to work in the MED / DIST cases were
            # actually fallbacks (clitic-pass moved the ``na`` to
            # clause-final and the bare-NP rule absorbed
            # ``DET[DEM=YES] N`` directly). The corrected check
            # uses ``is True`` so the branch fires as designed.
            out.append([ma for ma in cands if ma.feats.get("is_clitic") is not True])
        elif "VERB" in prev_pos or "PRON" in prev_pos:
            # Three left-context exceptions where ``na`` should be
            # the linker rather than the aspectual clitic:
            #
            # 1. Control verb directly followed by ``na`` (Phase 5c
            #    §7.6 follow-on, Commit 3): a control verb's lex
            #    requires an XCOMP introduced by a linker, so
            #    ``na`` after ``pumayag`` / ``gusto`` etc. is the
            #    linker — never the aspectual ``ALREADY``. Without
            #    this, nested-control sentences like
            #    ``Gusto kong pumayag na kumain`` lose the linker
            #    and don't parse.
            # 2. PRON preceded by a control verb (Phase 4 §7.10):
            #    ``Kaya namin na kumain`` — psych control with
            #    consonant-final pronominal experiencer; the
            #    following ``na`` is the linker introducing XCOMP.
            # 3. PRON preceded by a NOUN (NP-internal possessive)
            #    + ``na`` + VERB (Phase 5e Commit 6, lifting Phase
            #    5d Commit 10's deferral): ``bata ko na nakita``
            #    "child of-mine which-saw" — the PRON is the head
            #    NP's possessor, the ``na`` is the linker
            #    introducing the RC. Look at BOTH sides:
            #    PRON-after-NOUN preceding AND VERB (or NEG+VERB)
            #    following. The look-ahead skips
            #    PART[POLARITY=NEG] so ``bata ko na hindi kinain``
            #    works too.
            is_ctrl_verb = "VERB" in prev_pos and any(
                ma.pos == "VERB"
                and ma.feats.get("CTRL_CLASS") not in (None, "NONE")
                for ma in analyses[i - 1]
            )
            prev_prev = analyses[i - 2] if i >= 2 else None
            is_ctrl_pron_seq = (
                "PRON" in prev_pos
                and prev_prev is not None
                and any(
                    ma.pos == "VERB"
                    and ma.feats.get("CTRL_CLASS") not in (None, "NONE")
                    for ma in prev_prev
                )
            )
            is_post_noun_pron_with_v_following = (
                "PRON" in prev_pos
                and prev_prev is not None
                and any(ma.pos in ("NOUN", "N") for ma in prev_prev)
                and _next_content_is_verb(analyses, i)
            )
            if (
                is_ctrl_verb
                or is_ctrl_pron_seq
                or is_post_noun_pron_with_v_following
            ):
                out.append([
                    ma for ma in cands if ma.feats.get("is_clitic") is not True
                ])
            else:
                out.append([
                    ma for ma in cands if ma.feats.get("is_clitic") is True
                ])
        else:
            out.append(cands)
    return out


def _next_content_is_verb(
    analyses: list[list[MorphAnalysis]], i: int
) -> bool:
    """Look ahead from position ``i + 1``, skipping
    ``PART[POLARITY=NEG]`` tokens (negation typically precedes the V
    it negates), and return True if the first non-NEG content token
    is a VERB.

    Used by :func:`disambiguate_homophone_clitics` to decide whether
    ``na`` after a post-noun PRON is the linker (introducing an RC
    / clausal complement) rather than the 2P aspectual clitic.
    """
    look = i + 1
    while look < len(analyses):
        cands = analyses[look]
        poss = {ma.pos for ma in cands}
        is_neg_part = any(
            ma.pos == "PART" and ma.feats.get("POLARITY") == "NEG"
            for ma in cands
        )
        if "VERB" in poss:
            return True
        if is_neg_part and "VERB" not in poss:
            look += 1
            continue
        return False
    return False


def reorder_clitics(
    analyses: list[list[MorphAnalysis]],
    order: CliticOrder | None = None,
) -> list[list[MorphAnalysis]]:
    """Return a new analyses list with clitics moved to canonical
    Wackernagel positions and sorted by priority.

    Two cluster positions:

    * **Pronominal clitics** (``PRON`` with ``is_clitic=True``,
      e.g. ``ako``, ``ko``, ``mo``, ``niya``) move to immediately
      after the verb. They appear in NP-argument slots in the
      grammar via the existing ``NP[CASE=X] → PRON[CASE=X]`` rules.
    * **Adverbial enclitics** (``PART`` with ``is_clitic=True`` and
      ``clitic_class=2P``, e.g. ``na``, ``pa``, ``ba``, ``daw``)
      move to the end of the clause. The grammar absorbs them via a
      recursive ``S → S PART[CLITIC_CLASS=2P]`` rule that adds them
      as members of the matrix's ``ADJ`` set.

    Within each group, clitics are sorted by the priority table
    loaded from ``data/tgl/clitic_order.yaml``. Clitics not in the
    table sort after listed ones (priority = ``DEFAULT_PRIORITY``).

    Tokens that are not clitics keep their relative order. The
    leading host (e.g. the negation particle ``hindi``) keeps its
    sentence-initial position. If the input has no verb token, the
    input is returned unchanged; if there are no clitics, the input
    is returned unchanged (identity, not a copy).
    """
    if not analyses:
        return analyses

    analyses = disambiguate_homophone_clitics(analyses)

    # Phase 5e Commit 22: anchor selection. The first VERB takes
    # precedence (verbed clauses). If no VERB exists, fall back to
    # the first non-clitic, non-NEG-PART, non-punct token (verbless
    # predicate constructions like ``Maganda na ka``). If neither
    # exists, no reordering.
    verb_idx: int | None = None
    for i, cands in enumerate(analyses):
        if _is_verb_token(cands):
            verb_idx = i
            break
    anchor_idx: int | None = (
        verb_idx if verb_idx is not None else _find_verbless_anchor(analyses)
    )
    if anchor_idx is None:
        return analyses

    pron_indices = [
        i for i, cands in enumerate(analyses)
        if i != anchor_idx
        and _is_pron_clitic(cands)
        and not _is_post_noun_pron(analyses, i)
        and not _is_pre_linker_pron(analyses, i)
        and not _is_post_embedded_v_pron(analyses, i, anchor_idx)
    ]
    adv_indices = [
        i for i, cands in enumerate(analyses)
        if i != anchor_idx and _is_adv_clitic(cands)
    ]
    if not pron_indices and not adv_indices:
        return analyses

    if order is None:
        order = _get_default_order()

    pron_indices.sort(
        key=lambda i: (order.priority_for(_surface_for_priority(analyses[i])), i)
    )
    adv_indices.sort(
        key=lambda i: (order.priority_for(_surface_for_priority(analyses[i])), i)
    )

    def _filter_pron(cands: list[MorphAnalysis]) -> list[MorphAnalysis]:
        # Tokens in the cluster keep only their clitic-flavored
        # analyses. This avoids having a homophonous non-clitic
        # reading (e.g. ``na`` as a linker rather than the aspectual
        # enclitic) ride into the cluster slot through the grammar's
        # non-conflict feature matcher.
        return [m for m in cands if m.feats.get("is_clitic") is True and m.pos == "PRON"]

    def _filter_adv(cands: list[MorphAnalysis]) -> list[MorphAnalysis]:
        return [m for m in cands if m.feats.get("is_clitic") is True and m.pos == "PART"]

    clitic_set = set(pron_indices) | set(adv_indices)
    result: list[list[MorphAnalysis]] = []
    for i, cands in enumerate(analyses):
        if i in clitic_set:
            continue
        result.append(cands)
        if i == anchor_idx:
            for j in pron_indices:
                result.append(_filter_pron(analyses[j]))
    for j in adv_indices:
        result.append(_filter_adv(analyses[j]))
    return result


__all__ = [
    "CliticOrder",
    "DEFAULT_PRIORITY",
    "load_clitic_order",
    "reorder_clitics",
]
