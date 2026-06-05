# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 7a.D: wh-ADV with linker fronting (§18.1.1 item 5).

New clause rule in ``cfg/clause.py`` (parallel to the Phase 5i
Commit 4 bare wh-ADV rule):

    S → ADV[WH] PART[LINK=NA] S
    S → ADV[WH] PART[LINK=NG] S

Closes the linker-form variant of adverbial wh fronting. The
plan-of-record §3.4 called out ``paano`` specifically, but the
new rule is generic over ``ADV[WH]`` and covers all wh-ADVs
when followed by a linker (``paanong``, ``saang``, ``kailang``,
``paano na``, etc.). Modern Tagalog permits the linker-bound
form across the wh-ADV inventory, with added emphasis or
interrogative-particle force.

End-to-end target sentences:

    Paanong kumain ang aso?    "How would the dog eat?"
    Paanong bumili ang lalaki ng aklat?
    Saang kumain ang aso?      "Where did the dog eat?"
    Kailang kumain ang aso?    "When did the dog eat?"
    Paano na kumain ang aso?   (na-linker variant of paano)

The equation set mirrors the bare wh-ADV rule exactly except
daughter indices shift by one (S=↓3 instead of ↓2). No new feats:
``Q_TYPE=WH`` + ``WH_LEMMA`` identifies the question type;
downstream consumers dispatch on ``WH_LEMMA`` when distinguishing
manner / location / time / reason / etc. The plan's proposed
``(↑ ASK_MANNER) = true`` equation is dropped (no parallel
``ASK_*`` feats exist for other wh-types; a paano-specific atom
would break the existing wh-Q convention).
"""

import pytest

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


# === Test inventory ====================================================

# (sentence, wh_lemma, expected_link)
NG_LINKER_INVENTORY = [
    ("Paanong kumain ang aso?",                 "paano",   "NG"),
    ("Paanong bumili ang lalaki ng aklat?",     "paano",   "NG"),
    ("Saang kumain ang aso?",                   "saan",    "NG"),
    ("Kailang kumain ang aso?",                 "kailan",  "NG"),
]

NA_LINKER_INVENTORY = [
    # `na` linker is the longer form; some of these may have
    # additional readings (e.g., `na` as enclitic "already") so
    # we don't pin exact parse count, only that at least one
    # wh-Q reading exists.
    ("Paano na kumain ang aso?", "paano"),
    ("Saan na kumain ang aso?",  "saan"),
]


def _wh_q_parse(parses: list, wh_lemma: str):
    """Return the first parse whose matrix has Q_TYPE=WH and the
    given WH_LEMMA (filters out non-wh-Q readings of na-ambiguous
    surfaces)."""
    for p in parses:
        fs = p[1]
        if (
            fs.feats.get("Q_TYPE") == "WH"
            and fs.feats.get("WH_LEMMA") == wh_lemma
        ):
            return p
    return None


# === -ng linker (paanong / saang / kailang) ===========================


class TestNGLinkerWhAdvFronting:
    """The -ng linker form is the most natural wh-ADV-linker variant
    in modern Tagalog. Each wh-ADV has a distinct -ng-bound surface
    (paanong, saang, kailang, etc.) and the rule generates the wh-Q
    matrix uniformly."""

    @pytest.mark.parametrize(
        "sentence,wh_lemma,_link",
        NG_LINKER_INVENTORY,
    )
    def test_q_type_wh_on_matrix(
        self, sentence: str, wh_lemma: str, _link: str
    ) -> None:
        parses = parse_text(sentence)
        p = _wh_q_parse(parses, wh_lemma)
        assert p is not None, (
            f"{sentence!r} should produce a wh-Q parse with "
            f"WH_LEMMA={wh_lemma!r}"
        )

    @pytest.mark.parametrize(
        "sentence,wh_lemma,_link",
        NG_LINKER_INVENTORY,
    )
    def test_wh_adv_in_adjunct(
        self, sentence: str, wh_lemma: str, _link: str
    ) -> None:
        parses = parse_text(sentence)
        p = _wh_q_parse(parses, wh_lemma)
        assert p is not None
        adj = p[1].feats.get("ADJUNCT")
        assert isinstance(adj, (set, list, frozenset)), (
            "ADJUNCT should be a set/list"
        )
        adj_lemmas = [
            m.feats.get("LEMMA")
            for m in adj
            if isinstance(m, FStructure)
        ]
        assert wh_lemma in adj_lemmas, (
            f"wh-ADV {wh_lemma!r} should be in matrix ADJUNCT"
        )

    def test_paanong_carries_manner_adv_type(self) -> None:
        # The wh-ADV's ADV_TYPE=MANNER should propagate to the
        # ADJUNCT member's f-struct.
        parses = parse_text("Paanong kumain ang aso?")
        p = _wh_q_parse(parses, "paano")
        assert p is not None
        adj = p[1].feats.get("ADJUNCT")
        for m in adj:
            if (
                isinstance(m, FStructure)
                and m.feats.get("LEMMA") == "paano"
            ):
                assert m.feats.get("ADV_TYPE") == "MANNER"
                return
        pytest.fail("paano ADJUNCT member not found")

    def test_inner_verbal_pred_propagates(self) -> None:
        # Matrix shares the inner S's f-struct via (↑) = ↓3,
        # so the verbal PRED appears on the matrix.
        parses = parse_text("Paanong kumain ang aso?")
        p = _wh_q_parse(parses, "paano")
        assert p is not None
        assert p[1].feats.get("PRED") == "EAT <SUBJ>"


# === na linker (paano na / saan na / etc.) =============================


class TestNALinkerWhAdvFronting:
    """The na-linker form is permitted but may admit additional
    readings (na as enclitic 'already'). We pin only that AT LEAST
    ONE wh-Q reading exists."""

    @pytest.mark.parametrize(
        "sentence,wh_lemma",
        NA_LINKER_INVENTORY,
    )
    def test_at_least_one_wh_q_reading(
        self, sentence: str, wh_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        p = _wh_q_parse(parses, wh_lemma)
        assert p is not None, (
            f"{sentence!r} should produce at least one wh-Q parse "
            f"with WH_LEMMA={wh_lemma!r}"
        )


# === Regression: bare wh-ADV rule still parses =========================


class TestBareWhAdvUnaffected:
    """The Phase 5i Commit 4 bare wh-ADV rule (no linker) is
    unchanged; this PR only adds the linker variants."""

    @pytest.mark.parametrize(
        "sentence,wh_lemma",
        [
            ("Paano ka kumain?", "paano"),
            ("Saan ka pumunta?", "saan"),
            ("Bakit ka kumain?", "bakit"),
        ],
    )
    def test_bare_wh_adv_still_parses(
        self, sentence: str, wh_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        p = _wh_q_parse(parses, wh_lemma)
        assert p is not None, (
            f"Pre-Phase-7a.D bare wh-ADV form {sentence!r} should "
            f"still parse"
        )
