# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-8.2: audit-corpus ``dahil``-ZPF cleanup +
plural personal-name case-markers + survey-correction.

Second implementation sub-PR in the post-8.[1-5] arc. **Survey
misdiagnosis correction**: the post-8 survey
(`docs/phase-10-j-post-8-survey.md` Cluster E) claimed the
PAG-AARAL/sent-4 ZPF was due to a missing clause-final
``dahil``-SubordClause-without-comma rule. That diagnosis was
wrong — the chart already has ``S → S SubordClause``
(``subordination.py:166``, Phase 5l Commit 2 rule (b),
"Post-matrix attachment (no comma)"). PAG-AARAL/sent-4 actually
ZPFs for unrelated reasons (``magkamali`` paradigm gap +
V[ma]+V[INF] control with ``_UNK`` inner verb), both routing to
post-10 / post-8.5.

Repurposed scope (anti-deferral lift from "no real gap" to
"audit-corpus ``dahil``-ZPF cleanup"): a broader probe of the
wave-2/3 ``dahil``-bearing ZPF residue surfaced six small,
tractable lex/feat gaps that compound to block 1 wave-2 closure
+ a productive PERS-PL construction class affecting many
audit-corpus sentences.

Lex changes:

1. ``data/tgl/verbs.yaml``:

   * ``away`` (quarrel) — adds ``feats: {AV_ABSOL: true}``.
     Probe-confirmed ``Nag-away sila.`` ZPF'd pre-PR. Audit-
     corpus reach: wave-2 rg-intermediate sent-1762.
   * ``hubad`` (undress) — adds ``feats: {AV_ABSOL: true}``.
     Probe-confirmed ``Naghubad siya.`` ZPF'd pre-PR. Audit-
     corpus reach: wave-2 ramos1971 sent-88 ``Naghubad siya
     dahil sa init.``

2. ``data/tgl/particles.yaml``:

   * ``sina`` (PERS-NOM-PL marker) — ``DET[CASE=NOM, MARKER=SINA,
     HUMAN=true, NUM=PL]``. Parallel to ``si`` (PERS-NOM-SG).
   * ``nina`` (PERS-GEN-PL marker) — ``ADP[CASE=GEN, MARKER=NINA,
     HUMAN=true, NUM=PL]``. Parallel to ``ni`` (PERS-GEN-SG).
   * ``kina`` (PERS-DAT-PL marker) — ``ADP[CASE=DAT, MARKER=KINA,
     HUMAN=true, NUM=PL]``. Parallel to ``kay`` (PERS-DAT-SG).

   All three were surprising pre-PR ``_UNK`` omissions —
   ``sina X (at Y...)`` / ``nina X`` / ``kina X`` are basic
   productive Tagalog (R&G 1981 §3.2; S&O 1972 §3.1). The
   existing chart rule
   ``NP[CASE=NOM] → DET[CASE=NOM] N`` admits them once lex'd;
   the N daughter for the coord case
   ``sina Marina at Ester`` builds via the existing
   ``N → N PART[at] N`` proper-noun-coord rule, so no chart
   work needed.

3. ``data/tgl/nouns.yaml``:

   * ``tsismis`` NOUN ("gossip, rumor"; Sp. ``chismes``) —
     surfaced by wave-2 rg-intermediate sent-1762.
   * ``marina`` NOUN PERSON FEMALE — same wave-2 sentence's
     proper noun (``Ester`` already lex'd; ``Marina`` was the
     missing half).

4. ``src/tgllfg/morph/analyzer.py`` — placeholder-letter
   analyzer fallback (``_PLACEHOLDER_LETTER_RE``):

   The 6 most common pedagogical / variable placeholder
   letters in both cases — A/B/C + X/Y/Z and a/b/c + x/y/z —
   get a bare ``NOUN`` analysis with only the LEMMA feat
   (no SUBCLASS). R&G 1981 Intermediate uses uppercase
   A/B as anonymous dialogue-speaker labels (150+ / 142+
   occurrences); math / logic / abstract-example contexts
   use X/Y/Z and lowercase x/y/z as variables; enumerated-
   list labels use lowercase a/b/c. They compose as ``N``
   via the standard ``NP[CASE=X] → DET[CASE=X] N`` rule
   once recognised but commit to no semantic class (could
   substitute for a thing, an event, etc.). **Additive**:
   appended alongside any existing analyses (e.g., ``Y`` has
   a specific ``PART[MINUTE_OP=Y]`` time-formatting use; the
   placeholder NOUN is added on top, chart picks whichever
   composes).

   **Excludes ``G``** (Tagalog honorific ``G.`` = "Ginoong" /
   "Mr.", e.g., ``Ano ang ginawa ni G. Santos?`` in
   ``test_phase9b_proper_names``) — handled by the existing
   ``_UNK``-drop + structural composition path, NOT as a
   placeholder. Other single letters (D/E/F/I/J/K/...) remain
   ``_UNK`` for now; extend the regex on demand when corpus
   surfaces new patterns.

The combined fixes close wave-2 ramos1971 sent-88 (``Naghubad
siya dahil sa init.``) directly. The wave-2 rg-int sent-1762
(``Nag-away sina Marina at Ester dahil sa tsismis.``) closes
via the cumulative effect of ALL three lex additions + the
sina/nina/kina particles — no single fix is sufficient. Wave-2
``Ano ang kinain ni B kina Mr. at Mrs. Neelon?`` (sent-638)
parses via the placeholder fallback for ``B`` + the new ``kina``
marker.

Anti-deferral: the user invoked anti-deferral discipline on
``sina X at Y`` PERS-NOM-PL coord (initially flagged for
deferral as "a separate construction class"). The probe showed
the gap was 4 small lex additions plus the chart rule already
in place — clearly tractable in-PR.

Design discussion (placeholder approach): the user flagged that
the initial ``A`` / ``B`` lex-as-PERSON approach was wrong on
two axes — (a) A/B can substitute for a thing/event, not just
a person; (b) the lex approach doesn't scale to 26 letters and
multiple alphabets (I/J/K, X/Y/Z, …). The analyzer fallback
addresses both — no SUBCLASS, uniform across all uppercase
single letters.

Deferred to follow-ons (documented but NOT addressed):

* PAG-AARAL/sent-4 ``Ayaw nilang magbukas ng bibig dahil
  natatakot magkamali.`` — ``magkamali`` paradigm cell +
  V[ma]+V[INF] control routing to post-10 / post-8.5.
* wave-2 rc1990 sent-644 / sent-645 (``Binaha ang Maynila, dahil
  sa umulan nang malakas.``) — ``umulan nang malakas`` (V +
  nang-Adv) interaction; deeper.
* wave-2 rc1990 sent-703 ``Umuwi na si Oscar, dahil pagod na
  siya.`` — inner-clause ``na``-clitic across comma+dahil
  boundary; clitic-placement issue.

Reference: post-7.5 / post-7.6 / post-8.1 AV_ABSOL family;
post-7.7 N-coord defensive gates.
"""

from tgllfg.core.pipeline import parse_text


class TestAwayAvAbsol:
    """post-8.2: ``away`` AV_ABSOL — bare V[AV]+NP[NOM] license
    for the quarrel/fight-without-explicit-OBJ construction."""

    def test_nag_away_sila_bare(self) -> None:
        """``Nag-away sila.`` — pre-8.2 ZPF (away was TR without
        AV_ABSOL; bare AV reading missing the OBJ slot)."""
        parses = parse_text("Nag-away sila.", n_best=2)
        assert len(parses) >= 1

    def test_nag_away_with_dahil_sa_tsismis(self) -> None:
        """``Nag-away sila dahil sa tsismis.`` — composes away
        AV_ABSOL + tsismis NOUN + clause-final ``dahil sa NP``
        (PP[REASON], post-7.2)."""
        parses = parse_text("Nag-away sila dahil sa tsismis.", n_best=2)
        assert len(parses) >= 1


class TestHubadAvAbsol:
    """post-8.2: ``hubad`` AV_ABSOL — bare V[AV] license for
    self-directed undress reading."""

    def test_naghubad_siya_bare(self) -> None:
        """``Naghubad siya.`` — pre-8.2 ZPF (hubad was TR without
        AV_ABSOL)."""
        parses = parse_text("Naghubad siya.", n_best=2)
        assert len(parses) >= 1

    def test_naghubad_dahil_sa_init(self) -> None:
        """``Naghubad siya dahil sa init.`` — wave-2 ramos1971
        sent-88. **Audit-corpus closure.** Composes hubad
        AV_ABSOL + clause-final ``dahil sa NP``."""
        parses = parse_text("Naghubad siya dahil sa init.", n_best=2)
        assert len(parses) >= 1

    def test_naghubad_with_explicit_obj_preserved(self) -> None:
        """Anti-regression: ``Naghubad siya ng damit.`` still
        parses (explicit ng-OBJ frame unaffected by AV_ABSOL
        addition)."""
        parses = parse_text("Naghubad siya ng damit.", n_best=2)
        assert len(parses) >= 1


class TestPersPlMarkers:
    """post-8.2: ``sina`` / ``nina`` / ``kina`` PERS-NOM/GEN/DAT
    PL markers. Parallel to si / ni / kay; admit via existing
    chart rules once lex'd."""

    def test_sina_bare(self) -> None:
        """``Kumain sina Maria.`` — sina + single name."""
        parses = parse_text("Kumain sina Maria.", n_best=2)
        assert len(parses) >= 1

    def test_sina_at_coord(self) -> None:
        """``Kumain sina Maria at Juan.`` — sina + N-coord
        (via existing ``N → N PART[at] N`` proper-noun coord)."""
        parses = parse_text("Kumain sina Maria at Juan.", n_best=2)
        assert len(parses) >= 1

    def test_sina_marina_at_ester(self) -> None:
        """``Nag-away sina Marina at Ester.`` — uses all of:
        away AV_ABSOL, sina marker, Marina NOUN, Ester NOUN
        (Ester pre-existing), at-coord."""
        parses = parse_text("Nag-away sina Marina at Ester.", n_best=2)
        assert len(parses) >= 1

    def test_sina_marina_at_ester_dahil_sa_tsismis(self) -> None:
        """``Nag-away sina Marina at Ester dahil sa tsismis.`` —
        wave-2 rg-intermediate sent-1762. **Audit-corpus
        closure.** Cumulative effect of away AV_ABSOL + sina +
        Marina + tsismis."""
        parses = parse_text(
            "Nag-away sina Marina at Ester dahil sa tsismis.", n_best=2
        )
        assert len(parses) >= 1

    def test_nina_gen_coord(self) -> None:
        """``Nakita ko nina Pedro at Maria ang pelikula.`` —
        nina-marked GEN coord."""
        parses = parse_text(
            "Nakita ko nina Pedro at Maria ang pelikula.", n_best=2
        )
        assert len(parses) >= 1

    def test_kina_dat(self) -> None:
        """``Pumunta siya kina Maria.`` — kina-marked DAT."""
        parses = parse_text("Pumunta siya kina Maria.", n_best=2)
        assert len(parses) >= 1


class TestPlaceholderLetters:
    """post-8.2: ``_PLACEHOLDER_LETTER_RE`` analyzer fallback for
    single-uppercase-letter placeholders (R&G A/B dialogue labels,
    math X/Y/Z variables, etc.). Emits bare NOUN with only LEMMA;
    no PERSON / PLACE subclass commitment."""

    def test_b_placeholder_in_sentence(self) -> None:
        """``Ano ang sinabi ni B?`` — R&G dialogue-label style.
        The placeholder fallback admits B as bare NOUN."""
        parses = parse_text("Ano ang sinabi ni B?", n_best=2)
        assert len(parses) >= 1

    def test_a_b_in_same_sentence(self) -> None:
        """``Bakit hindi napansin ni B si A?`` — wave-2 rg-int
        sent-116 pattern with both A and B as placeholders."""
        parses = parse_text("Bakit hindi napansin ni B si A?", n_best=2)
        assert len(parses) >= 1

    def test_xyz_math_placeholders(self) -> None:
        """X / Y / Z math-variable usage. Y has a pre-existing
        ``PART[MINUTE_OP=Y]`` analysis — the additive fallback
        still admits the placeholder NOUN reading."""
        for letter in ("X", "Y", "Z"):
            text = f"Ano ang sinabi ni {letter}?"
            parses = parse_text(text, n_best=2)
            assert len(parses) >= 1, f"placeholder {letter} should parse: {text}"

    def test_c_placeholder_in_sentence(self) -> None:
        """``C`` rounds out the A/B/C trio (third dialogue-speaker
        if R&G ever uses one)."""
        parses = parse_text("Ano ang sinabi ni C?", n_best=2)
        assert len(parses) >= 1

    def test_g_remains_unk_for_honorific(self) -> None:
        """``G`` is **excluded** from the placeholder set —
        ``G.`` is the Tagalog honorific ``Ginoong`` ("Mr."), not
        a placeholder. ``Ano ang ginawa ni G. Santos?`` parses
        via the existing ``_UNK``-drop path (preserves Phase 9b
        test). If we lex'd G as placeholder, ``G Santos`` would
        try to compose structurally and fail (no N-N compound
        rule)."""
        parses = parse_text("Ano ang ginawa ni G. Santos?", n_best=2)
        assert len(parses) >= 1, "G. Santos must still parse via _UNK-drop"

    def test_other_letters_remain_unk(self) -> None:
        """Letters outside A/B/C/X/Y/Z (e.g., D, E, F, I, J, K)
        remain ``_UNK``. Regex restriction is intentional —
        extend on demand when the corpus surfaces new patterns."""
        # `Kumain si I.` would parse if I were a placeholder; the
        # regex excludes I (potential English code-switch pronoun).
        parses = parse_text("Kumain si I.", n_best=2)
        assert len(parses) == 0, "I is excluded from placeholder set"

    def test_lowercase_placeholders_match(self) -> None:
        """Lowercase a/b/c/x/y/z are ALSO placeholders (regex
        case-insensitive). Math conventions use lowercase x/y/z,
        enumerated lists use a/b/c."""
        for letter in ("a", "b", "c", "x", "y", "z"):
            text = f"Ano ang sinabi ni {letter}?"
            parses = parse_text(text, n_best=2)
            assert len(parses) >= 1, f"lowercase placeholder '{letter}' should parse: {text}"

    def test_codeswitch_a_la_still_zpfs(self) -> None:
        """``Kahit a la 'ako Tarzan'.`` (PAG-AARAL/sent-12 code-
        switch) still ZPFs even though lowercase `a` is now a
        valid placeholder — the rest of the sentence (`la`,
        Tarzan, quote marks) keeps it from composing. Validates
        that giving lowercase `a` a NOUN reading doesn't open
        spurious parses for code-switch material."""
        parses = parse_text("Kahit a la 'ako Tarzan'.", n_best=2)
        assert len(parses) == 0, "code-switch `a la` must not parse"

    def test_kinain_ni_b_kina_neelon_regression_target(self) -> None:
        """``Ano ang kinain ni B kina Mr. at Mrs. Neelon?`` —
        wave-2 rg-int sent-638. **Regression-fix target**: pre-PR
        parsed via ``_UNK`` drop of ``kina``; post-PR composes
        structurally via the placeholder fallback for B + the
        new ``kina`` PERS-DAT-PL marker."""
        parses = parse_text(
            "Ano ang kinain ni B kina Mr. at Mrs. Neelon?", n_best=2
        )
        assert len(parses) >= 1


class TestAntiRegression:
    """post-8.2: existing SG personal-marker constructions + AV_ABSOL
    family preserved."""

    def test_si_singular_preserved(self) -> None:
        """``Kumain si Maria.`` — singular si still parses."""
        parses = parse_text("Kumain si Maria.", n_best=2)
        assert len(parses) >= 1

    def test_ni_singular_preserved(self) -> None:
        """``Nakita ko ang aklat ni Pedro.`` — singular ni
        possessive."""
        parses = parse_text("Nakita ko ang aklat ni Pedro.", n_best=2)
        assert len(parses) >= 1

    def test_kay_singular_preserved(self) -> None:
        """``Pumunta siya kay Maria.`` — singular kay DAT."""
        parses = parse_text("Pumunta siya kay Maria.", n_best=2)
        assert len(parses) >= 1

    def test_existing_av_absol_kuwento_preserved(self) -> None:
        """``Nagkuwento ako sa kapatid ko.`` — post-7.6 closure."""
        parses = parse_text("Nagkuwento ako sa kapatid ko.", n_best=2)
        assert len(parses) >= 1

    def test_existing_av_absol_sunod_preserved(self) -> None:
        """``Sumunod ka sa iyong magulang.`` — post-8.1 closure."""
        parses = parse_text("Sumunod ka sa iyong magulang.", n_best=2)
        assert len(parses) >= 1
