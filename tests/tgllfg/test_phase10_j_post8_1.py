# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-8.1: AV_ABSOL gaps on sunod / kilala TR verbs.

First implementation sub-PR in the post-8.[1-5] arc opened by the
post-8 wave-1 ZPF residue survey (PR #160, `a0ae515`,
`docs/phase-10-j-post-8-survey.md`). Renumbered from post-8.4 to
post-8.1 on 2026-05-30 to lead the post-8 implementation order
as the smallest tractable lex sub-PR — validates the survey's
probe-derived AV_ABSOL claim with a multi-wave audit before the
larger chart / paradigm sub-PRs (post-8.2 / post-8.3 / post-8.4).

Two lex changes in ``data/tgl/verbs.yaml``:

1. ``sunod`` (follow, obey) — adds ``feats: {AV_ABSOL: true}``.
   Survey probe confirmed ``Sumusunod siya.`` ZPF despite
   ``sumusunod`` being lex'd as VERB AV-IPFV. The natural
   absolutive reading "He follows / is following [an implicit
   lead]" needs AV_ABSOL to license the bare V[AV]+NP[CASE=NOM]
   frame. Audit-corpus reach: wave-2 ramos1971 sent-160
   ``Sumunod ka sa iyong magulang.`` "Obey your parent" — the
   ``sa`` complement here is directional/locative goal, not the
   OBJ argument; absolutive AV is the canonical reading.

2. ``kilala`` (know, recognize) — adds ``ma`` to ``affix_class``
   AND ``feats: {AV_ABSOL: true}``. The ``ma`` addition is the
   primary lex extension: before this PR, kilala had
   ``[mag, in_oblig, an_oblig, maka]`` (4 classes), so the
   canonical ``nakilala`` / ``nakikilala`` / ``makikilala``
   ma-NVOL forms — the surface every Tagalog speaker uses for
   "recognize" — were ``_UNK``. Adding ``ma`` brings kilala to
   the same 5-class set as ``alala`` (``[um, mag, ma, in_oblig,
   maka]``). ``AV_ABSOL: true`` then licenses the bare absolutive
   reading on those new cells. Audit-corpus reach: 5+ sentences
   across waves 2/3/5 use the ``nakilala ko siya`` /
   ``nakilala ko ang X`` shape:

   * wave-2 rg-intermediate sent-126:
     ``Hindi mo siya nakilala kaagad.``
   * wave-3 so1972 sent-786 / sent-1076:
     ``Nang makita ko siya, nakilala ko siya agad.``
   * wave-5 zamar2023 page-54/sent-2:
     ``Nakilala ko ang gurong nagtuturo ng klaseng Matematika.``

Recognition is inherently potentive in Tagalog (an unwilled
cognitive act), so the ``ma-`` (non-volitional) paradigm is the
canonical voice family — not the volitional ``mag-`` /
``-um-``.

Deferred to post-8.5 (broader paradigm-cell expansion):
``sundin`` / ``sundan`` OV/LV forms (need medial-vowel-syncope
sandhi for ``sunod → sund-`` before suffix; engine extension,
not a lex feat) and ``kilalanin`` (n-epenthesis variant of
``kilalahin``; optional additive sandhi flag).

Closes 4 new unattributed exemplars under
``unattributed/av-absol/`` (``sunod/sumusunod-bare``,
``sunod/sumunod-imperative-sa-obl``,
``kilala/nakikilala-bare-pron``, ``kilala/nakilala-perfective``).

Reference: post-7.5 (``maneho`` AV_ABSOL), post-7.6
(``kuwento`` AV_ABSOL), post-7.1 (``sagot`` AV_ABSOL),
post-7.2 (``hirap`` AV_ABSOL).
"""

from tgllfg.core.pipeline import parse_text


class TestSunodAvAbsol:
    """sunod AV_ABSOL — bare V[AV]+NP[CASE=NOM] license."""

    def test_sumusunod_siya_bare(self) -> None:
        """``Sumusunod siya.`` — bare V[AV]-IPFV + NOM-pronoun.
        Pre-8.1 this ZPF'd because sunod lacked AV_ABSOL."""
        parses = parse_text("Sumusunod siya.", n_best=2)
        assert len(parses) >= 1

    def test_sumunod_siya_pfv(self) -> None:
        """``Sumunod siya.`` — bare V[AV]-PFV variant."""
        parses = parse_text("Sumunod siya.", n_best=2)
        assert len(parses) >= 1

    def test_susunod_siya_ctpl(self) -> None:
        """``Susunod siya.`` — bare V[AV]-CTPL variant."""
        parses = parse_text("Susunod siya.", n_best=2)
        assert len(parses) >= 1

    def test_sumunod_ka_sa_obl(self) -> None:
        """``Sumunod ka sa iyong magulang.`` — wave-2 ramos1971
        sent-160. AV with NOM-pivot ``ka`` and a sa-OBL goal/
        directional. The OBJ (what's being followed) is
        unspecified — absolutive AV reading. **Audit-corpus
        closure.**"""
        parses = parse_text("Sumunod ka sa iyong magulang.", n_best=2)
        assert len(parses) >= 1


class TestKilalaMaAndAvAbsol:
    """kilala ``ma`` affix_class + AV_ABSOL — admits the ma-NVOL
    paradigm (``nakikilala`` / ``nakilala`` / ``makikilala``)
    and licenses bare absolutive readings."""

    def test_nakikilala_ko_siya(self) -> None:
        """``Nakikilala ko siya.`` "I recognize him." — bare AV
        with ko (GEN-1SG) + siya (NOM-3SG). Pre-8.1 ``nakikilala``
        was ``_UNK`` (no ma in affix_class)."""
        parses = parse_text("Nakikilala ko siya.", n_best=2)
        assert len(parses) >= 1

    def test_nakilala_ko_siya_pfv(self) -> None:
        """``Nakilala ko siya.`` "I recognized him." — PFV
        variant. Same shape as wave-3 so1972 sent-786/1076 inner
        clause."""
        parses = parse_text("Nakilala ko siya.", n_best=2)
        assert len(parses) >= 1

    def test_makikilala_ko_siya_ctpl(self) -> None:
        """``Makikilala ko siya.`` "I will recognize him." —
        CTPL variant."""
        parses = parse_text("Makikilala ko siya.", n_best=2)
        assert len(parses) >= 1

    def test_hindi_mo_siya_nakilala_kaagad(self) -> None:
        """``Hindi mo siya nakilala kaagad.`` "You did not
        recognize him quickly." — wave-2 rg-intermediate sent-126.
        **Audit-corpus closure.** Note the Wackernagel-clitic
        order (``mo siya nakilala``) — clitics raise to second
        position after negation."""
        parses = parse_text("Hindi mo siya nakilala kaagad.", n_best=2)
        assert len(parses) >= 1


class TestAntiRegression:
    """post-8.1: existing AV_ABSOL verbs preserved + sunod/kilala
    with explicit OBJ still parse + DUAL-Q / control patterns
    intact."""

    def test_existing_av_absol_maneho(self) -> None:
        """``Nagmaneho si Pedro.`` — post-7.5 closure preserved."""
        parses = parse_text("Nagmaneho si Pedro.", n_best=2)
        assert len(parses) >= 1

    def test_existing_av_absol_kuwento(self) -> None:
        """``Nagkuwento ako sa kapatid ko.`` — post-7.6 closure
        preserved."""
        parses = parse_text("Nagkuwento ako sa kapatid ko.", n_best=2)
        assert len(parses) >= 1

    def test_existing_av_absol_sagot(self) -> None:
        """``Sumagot siya.`` — post-7.1 closure preserved."""
        parses = parse_text("Sumagot siya.", n_best=2)
        assert len(parses) >= 1

    def test_kilala_with_explicit_ang_obj(self) -> None:
        """``Nakikilala niya ang lalaki.`` — kilala with explicit
        ang-OBJ still parses (AV-NOM-pivot frame). Validates that
        AV_ABSOL adds a frame without removing the standard
        canonical-OBJ one."""
        parses = parse_text("Nakikilala niya ang lalaki.", n_best=2)
        assert len(parses) >= 1
