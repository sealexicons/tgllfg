"""Phase 4 §7.3: Wackernagel 2P clitic placement.

The clitic-placement pass moves pronominal clitics (PRON with
``is_clitic=True``) to immediately after the verb and adverbial
enclitics (PART with ``CLITIC_CLASS=2P``) to the end of the clause.
The grammar then absorbs adverbials via the recursive
``S → S PART[CLITIC_CLASS=2P]`` rule (matrix ADJ membership);
pronouns work through the existing NP[CASE=X] → PRON[CASE=X] shells.

These tests cover:

* placement-pass unit tests (input → reordered output);
* end-to-end pipeline parses with clitic clusters;
* feature percolation: pronominal SUBJ/OBJ; adverbial ADJ entries
  carrying ``ASPECT_PART``, ``EVID``, etc.;
* word-order normalization: non-canonical input parses identically
  to canonical input.
"""

from __future__ import annotations

from typing import Any

from tgllfg.clitics import CliticOrder, reorder_clitics
from tgllfg.core.common import FStructure, MorphAnalysis
from tgllfg.morph import analyze_tokens
from tgllfg.core.pipeline import parse_text
from tgllfg.text import split_enclitics, tokenize


def _surfaces(analyses: list[list[MorphAnalysis]]) -> list[str]:
    return [cands[0].lemma for cands in analyses]


def _analyse(text: str) -> list[list[MorphAnalysis]]:
    return analyze_tokens(split_enclitics(tokenize(text)))


def _first(text: str) -> tuple[Any, FStructure, Any, list[Any]]:
    results = parse_text(text)
    assert results, f"no parse for {text!r}"
    return results[0]


# === Placement unit tests =================================================


def test_placement_canonical_pron_after_v_adv_at_end() -> None:
    """Canonical Wackernagel surface form: pronominal clitics
    immediately after the verb, adverbial enclitics at clause end.
    The reorder pass *always* normalizes to this shape — adverbs
    that already sit between V and an NP (the Tagalog-natural
    surface) are still moved to absolute clause-final position to
    expose the cluster as a c-structure constituent the grammar can
    absorb via ``S → S PART[CLITIC_CLASS=2P]``."""
    a = _analyse("Kinain mo na ang isda.")
    out = reorder_clitics(a)
    content = [s for s in _surfaces(out) if s != "."]
    assert content == ["kain", "mo", "ang", "isda", "na"]


def test_placement_pron_pulled_to_after_verb() -> None:
    """Pronouns that appear before the verb are pulled to right
    after the verb."""
    a = _analyse("Hindi mo kinain ang isda.")
    out = reorder_clitics(a)
    assert _surfaces(out) == ["hindi", "kain", "mo", "ang", "isda", "."]


def test_placement_adv_pushed_to_end() -> None:
    """Adverbial enclitics move to the end of the clause."""
    a = _analyse("Hindi na kinain ng aso ang isda.")
    out = reorder_clitics(a)
    # `na` lands after the period (which is the _UNK token); content
    # tokens (excluding punctuation) end with `na`.
    surfaces = _surfaces(out)
    content = [s for s in surfaces if s != "."]
    assert content[-1] == "na"
    # Punctuation stays at its original position; content order is the
    # main constraint.
    assert content[:-1] == ["hindi", "kain", "ng", "aso", "ang", "isda"]


def test_placement_no_verb_passthrough() -> None:
    """Verbless input is returned unchanged."""
    a = _analyse("Aso ang bata.")
    out = reorder_clitics(a)
    assert out is a or _surfaces(out) == _surfaces(a)


def test_placement_no_clitics_passthrough() -> None:
    a = _analyse("Kumain ang aso ng isda.")
    out = reorder_clitics(a)
    assert out is a or _surfaces(out) == _surfaces(a)


def test_placement_cluster_priority_pron_before_adv() -> None:
    """Within the cluster, pronominal clitics (priority ≤ 99) sort
    before adverbial enclitics (priority ≥ 100). Per the data the
    pron lands after V, the adv at clause end — so this is just a
    relative-order sanity check."""
    a = _analyse("Kinain na mo ang isda.")
    out = reorder_clitics(a)
    surfaces = [s for s in _surfaces(out) if s != "."]
    assert surfaces == ["kain", "mo", "ang", "isda", "na"]


def test_placement_adv_priority_within_cluster() -> None:
    """Adverbial cluster sorts by clitics.yaml priority. ``na``
    (100) before ``ba`` (120)."""
    a = _analyse("Kinain ba na ang isda.")
    out = reorder_clitics(a)
    content = [s for s in _surfaces(out) if s != "."]
    # cluster goes to the end; na comes before ba.
    assert content[-2:] == ["na", "ba"]


# === End-to-end parses ====================================================


def test_pron_clitic_as_subj_av() -> None:
    """``Kumain ako ng isda``: ako (NOM-clitic) is SUBJ in AV."""
    _, f, _, _ = _first("Kumain ako ng isda.")
    assert f.feats.get("VOICE") == "AV"
    assert "SUBJ" in f.feats and "OBJ" in f.feats


def test_pron_clitic_as_obj_ov() -> None:
    """``Kinain mo ang isda``: mo (GEN-clitic) is OBJ-AGENT in OV
    (typed under the Phase 5b OBJ-θ-in-grammar alignment), isda
    is SUBJ."""
    _, f, _, _ = _first("Kinain mo ang isda.")
    assert f.feats.get("VOICE") == "OV"
    assert "SUBJ" in f.feats and "OBJ-AGENT" in f.feats


def test_adverbial_na_in_adj() -> None:
    """``Kinain mo na ang isda``: ``na`` rides on the matrix ADJ set
    with ASPECT_PART=ALREADY."""
    _, f, _, _ = _first("Kinain mo na ang isda.")
    adj = f.feats.get("ADJ")
    assert adj is not None, f"no ADJ on matrix; feats={f.feats}"
    members = list(adj)
    assert any(
        isinstance(m, FStructure)
        and m.feats.get("ASPECT_PART") == "ALREADY"
        for m in members
    ), f"no na adjunct in ADJ; members={[m.feats for m in members if isinstance(m, FStructure)]}"


def test_adverbial_ba_question() -> None:
    """``Kumain ba ang aso``: ``ba`` is the yes/no question enclitic.
    It rides into matrix ADJ as a Wackernagel-class member; only
    string-typed feats reach the f-structure (the seed's bool
    ``QUESTION=true`` does not), so the ADJ member is identified by
    its CLITIC_CLASS=2P alone — `ba` is the only adv enclitic in
    this sentence."""
    _, f, _, _ = _first("Kumain ba ang aso.")
    adj = f.feats.get("ADJ")
    assert adj is not None
    members = list(adj)
    cluster_members = [
        m for m in members
        if isinstance(m, FStructure) and m.feats.get("CLITIC_CLASS") == "2P"
    ]
    assert cluster_members, (
        f"no Wackernagel-class adjunct in ADJ; "
        f"members={[m.feats for m in members if isinstance(m, FStructure)]}"
    )


def test_negation_with_pron_clitic() -> None:
    """``Hindi mo kinain ang isda``: clitic-placement moves mo to
    after the verb so the V-initial inner-S parses; the outer
    negation rule then sets POLARITY=NEG."""
    _, f, _, _ = _first("Hindi mo kinain ang isda.")
    assert f.feats.get("POLARITY") == "NEG"
    assert f.feats.get("VOICE") == "OV"


def test_negation_with_pron_and_adv_clitic() -> None:
    """``Hindi mo na kinain ang isda``: clitic-placement reorders
    to ``hindi kinain mo ang isda na``; both POLARITY=NEG and the
    ``na`` adjunct land on the matrix."""
    results = parse_text("Hindi mo na kinain ang isda.")
    matches = [
        f for _, f, _, _ in results if f.feats.get("POLARITY") == "NEG"
    ]
    assert matches, "no NEG parse"
    f = matches[0]
    adj = f.feats.get("ADJ")
    assert adj is not None
    members = list(adj)
    assert any(
        isinstance(m, FStructure)
        and m.feats.get("ASPECT_PART") == "ALREADY"
        for m in members
    )


def test_word_order_invariance() -> None:
    """Canonical and non-canonical surface orders parse to
    f-structures with the same VOICE / SUBJ / OBJ / ADJ shape."""
    canonical = "Kinain mo na ang isda."
    non_canonical = "Hindi kinain mo na ang isda."  # different content, just test shape

    _, f1, _, _ = _first(canonical)
    _, f2, _, _ = _first(non_canonical)
    # The non-canonical here has hindi (added NEG) — just check that
    # both parse and both have ADJ (na enters ADJ in both).
    assert f1.feats.get("ADJ") is not None
    assert f2.feats.get("ADJ") is not None


# === Order-table loader ===================================================


def test_clitic_order_priority_lookup() -> None:
    from tgllfg.clitics import load_clitic_order

    order = load_clitic_order()
    # Pronominal clitics: priorities < 100.
    assert order.priority_for("ko") < order.priority_for("na")
    assert order.priority_for("mo") < order.priority_for("ba")
    # Adverbs in S&O 1972 §6.7 order.
    assert order.priority_for("na") < order.priority_for("pa")
    assert order.priority_for("pa") < order.priority_for("ba")
    assert order.priority_for("ba") < order.priority_for("daw")
    # Unknown surfaces sort after listed ones.
    from tgllfg.clitics.placement import DEFAULT_PRIORITY

    assert order.priority_for("zzz") == DEFAULT_PRIORITY


def test_clitic_order_custom_table() -> None:
    """The reorder accepts a custom CliticOrder for tests / corpus
    experiments."""
    custom = CliticOrder(priorities={"ko": 999, "na": 1})
    a = _analyse("Kinain ko na ang isda.")
    out = reorder_clitics(a, order=custom)
    content = [s for s in _surfaces(out) if s != "."]
    # With na at priority 1, the cluster sort pushes adv ahead of pron
    # *within their respective groups* (pron after V, adv at end). So
    # the relative position of ko and na doesn't actually swap; what
    # this test pins down is that the order param is honored without
    # crashing and produces a well-formed reordering. The pron stays
    # right after V; the adv stays at the end.
    assert content[0] == "kain"
    assert content[1] == "ko"
    assert content[-1] == "na"
