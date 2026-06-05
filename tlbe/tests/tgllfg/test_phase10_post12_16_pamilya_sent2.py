# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-12.16: PAMILYA/sent-2 closure infrastructure.

Regression guard for the multi-layer fix that closes the wave-1 target:

  ``Kahit na siya ay doktor, manunulat, siyentipiko o ano pa man,
    nananatili siyang ama o anak, pamangkin o apo sa loob ng kanyang
    pamilya.``
  "Even if she is a doctor, writer, scientist or whatever, she remains
   a father or son, niece/nephew or grandchild within her family."
   (R&G 1981 PAMILYA — wave-1)

User-provided structural bracketing:
  ``[[Kahit na siya] ay [doktor, manunulat, siyentipiko o ano pa man]],``
  ``[[nananatili siyang] [ama o anak, pamangkin o apo]``
  ``                     [sa loob ng kanyang pamilya]].``

Five coordinated layers:

* **`natili` (manatili / nanatili / nananatili / mananatili)** —
  STAY/REMAIN verb root + discrete-surface COPULA forms (parallel
  to ``maging`` / ``naging`` BECOME-copular discrete-surface lex).
  Required for ``nananatili siyang ama`` "she remains a father".

* **V[COPULA] PRON[NOM] LK N [+ NP[DAT]]** chart rules —
  Wackernagel-N-pred companions to the existing V[COPULA] PRON ADJ
  Wackernagel-ADJ-pred rule. Match the ``nananatili siyang ama``
  shape with an optional locative DAT-adjunct
  (``sa loob ng kanyang pamilya``).

* **N[COORD=OR] → N[COORD=OR] PUNCT[COMMA] N[COORD=OR]** —
  comma-asyndetic join of two binary OR-coord N-pairs. Required for
  ``ama o anak, pamangkin o apo`` (the 4-element role-N coord with
  comma between the two OR pairs).

* **`ano pa man` 3-token NEG_INDEF + idiom NP/N** — extends the
  existing 2-token ``ano man`` indef-builder to admit the ``pa``
  (STILL) clitic between the wh-PRON and ``man``. Direct N / NP
  projections carrying ``IDIOM_NEG_INDEF=true`` (no INDEF binding)
  bypass the NEG_INDEF-in-coord clash so the idiom fits as a
  conjunct alongside concrete N's. BINARY_FEATS 73→74.

* **Clitic-placement skip for `pa` between wh-PRON and `man`** —
  keeps the 3-token idiom intact (without the skip, Wackernagel
  placement hoists ``pa`` to clause-final, separating it from
  ``ano`` and ``man``).

Audit: wave1-exemplars 120 → 121 / 122 (PAMILYA/sent-2 closes —
target). 0 regressions.
"""

import pytest

from tgllfg.core.pipeline import parse_text_with_fragments


@pytest.mark.parametrize("sent", [
    # The full PAMILYA/sent-2 target
    "Kahit na siya ay doktor, manunulat, siyentipiko o ano pa man, "
    "nananatili siyang ama o anak, pamangkin o apo sa loob ng "
    "kanyang pamilya.",
])
def test_pamilya_sent_2_closure(sent: str) -> None:
    r = parse_text_with_fragments(sent, max_tree_iterations=5000)
    assert len(r.parses) >= 1, (
        f"Expected ≥1 parse for PAMILYA/sent-2; got {len(r.parses)}"
    )


@pytest.mark.parametrize("sent", [
    # natili paradigm forms (verbs.yaml ma + ma_inf)
    "Manatili siya.",            # ma_inf SOC bare INF
    "Nanatili siya.",             # ma PFV NVOL
    "Nananatili siya.",           # ma IPFV NVOL
    "Mananatili siya.",           # ma CTPL NVOL
])
def test_natili_paradigm_forms(sent: str) -> None:
    r = parse_text_with_fragments(sent, max_tree_iterations=5000)
    assert len(r.parses) >= 1


@pytest.mark.parametrize("sent", [
    # COPULA + Wackernagel-N-pred
    "Nananatili siyang ama.",
    "Naging siyang doktor.",
    # +DAT locative adjunct
    "Nananatili siyang ama sa pamilya.",
    "Nananatili siyang ama sa loob ng kanyang pamilya.",
])
def test_copula_pron_lk_n_pred(sent: str) -> None:
    r = parse_text_with_fragments(sent, max_tree_iterations=5000)
    assert len(r.parses) >= 1


@pytest.mark.parametrize("sent", [
    # Multi-comma OR coord — two binary OR pairs joined by comma
    "Nananatili siyang ama o anak, pamangkin o apo.",
    "Si Juan ay ama o anak, pamangkin o apo.",
])
def test_multi_comma_or_coord(sent: str) -> None:
    r = parse_text_with_fragments(sent, max_tree_iterations=5000)
    assert len(r.parses) >= 1


@pytest.mark.parametrize("sent", [
    # ``ano pa man`` 3-token NEG_INDEF idiom + bonus ``sino pa man``
    "Walang ano pa man.",       # existential context
    "Walang sino pa man.",       # bonus closure: wh + pa + man on sino
    # In NP-coord
    "Si Juan ay doktor o ano pa man.",
    "Kahit na siya ay doktor o ano pa man, kumain siya.",
    "Kahit na siya ay doktor, manunulat o ano pa man, kumain siya.",
])
def test_ano_pa_man_idiom(sent: str) -> None:
    r = parse_text_with_fragments(sent, max_tree_iterations=5000)
    assert len(r.parses) >= 1
