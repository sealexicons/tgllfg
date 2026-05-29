# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 9.B: proper-name + place-name + nationality-noun lex pass.

Bucket B1.A of the Phase 9 plan — the highest-yield-per-effort lex
pass (proper-name registration is mechanically simple and unlocks
many audit-corpus rows whose only blocker is the OOV name).

21 new NOUN entries (per `data/tgl/nouns.yaml` 273 → 294):

Personal names (Western, audit-corpus): ``bob``, ``damian``,
``david``, ``derek``, ``fred``, ``jasmine``, ``joe``, ``lisa``,
``manny``, ``manuel``, ``marvin``, ``rosa``.

Place names: ``amerika``, ``maynila``, ``pilipinas``.

Surname: ``santos``.

Nationality / language nouns: ``amerikana`` (Spanish-loan
clothing item / American woman), ``amerikano`` (American
national), ``ingles`` (English language), ``pilipino`` (Filipino
national), ``tagalog`` (Tagalog language).

Direct audit-corpus closures observed by re-running parse over
the 31 candidate rows (rows whose only real-OOV blockers are in
the new lex set): **13 direct closures** (42%), spread across
all six wave sources. Residual 18 rows blocked by orthogonal
gaps (N-appositive proper-name attachment per 8.I/9.P,
pedagogical-frame `Sentence:`/`Question:` prefixes per 9.M,
multi-clause SUBJ binding, OCR noise) and pinned out-of-scope.
"""

import pytest


class TestPhase9bLexLoadable:
    """Each new name is indexed by the morphology analyzer."""

    @pytest.mark.parametrize("name", [
        # Personal names
        "david", "rosa", "bob", "joe", "derek", "marvin", "manuel",
        "fred", "manny", "damian", "jasmine", "lisa",
        # Surname
        "santos",
        # Place names
        "pilipinas", "maynila", "amerika",
        # Nationality / language
        "pilipino", "tagalog", "amerikano", "amerikana", "ingles",
    ])
    def test_indexed(self, name: str) -> None:
        from tgllfg.morph.analyzer import _get_default
        a = _get_default()
        assert a.is_known_surface(name), f"{name!r} not indexed"


class TestPhase9bMinimalShapes:
    """Each new name parses in a minimal subject / oblique shape."""

    @pytest.mark.parametrize("sentence", [
        # Personal names in Si NP-pivot
        "Si Joe ang umalis.",
        "Si Jasmine ang dumating.",
        "Si Damian ang dumating.",
        "Si Manuel ang dumating.",
        "Si Marvin ang dumating.",
        "Si Bob ang dumating.",
        "Si Fred ang dumating.",
        "Si Manny ang dumating.",
        "Si Derek ang dumating.",
        "Si Lisa ang dumating.",
        "Si David ang dumating.",
        "Si Rosa ang dumating.",
        # Personal names as ang-gated SUBJ
        "Kumain si David.",
        "Kumain si Bob.",
        "Kumain si Damian.",
        # Place names in DAT oblique
        "Pumunta si Joe sa Maynila.",
        "Pumunta si Bob sa Amerika.",
        "Pumunta siya sa Pilipinas.",
        # Place names as ang-pivot
        "Ang Pilipinas ay maganda.",
        # Nationality / language as Si-pivot equational
        "Pilipino siya.",
        "Amerikano si Joe.",
        "Amerikana si Lisa.",
        "Tagalog ang sinabi niya.",
        "Ingles ang sinabi niya.",
    ])
    def test_minimal_shape_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse for {sentence!r}"


class TestPhase9bAuditClosures:
    """Direct audit-corpus closures. Each cites the locator from
    the cross-wave audit (post-9.A baseline)."""

    @pytest.mark.parametrize("sentence", [
        # Ch5-Some Changes/Predicate Subject/sent-1027 (R&C 1990)
        "Ano ang binili ni David?",
        # page-173/dialog/sent-1222 (R&G Intermediate)
        "Nakita mo na ba si Manuel?",
        # page-224/numbered/sent-1571 (R&G Intermediate)
        "Ginagawa ba ito ng mga Amerikano?",
        # page-27/prose/sent-71 (R&G Intermediate)
        "Hindi ba siya Pilipino?",
        # page-97/numbered/sent-426 (R&G Intermediate)
        "Ano ang ginawa ni G. Santos?",
        # page-52/prose/sent-157 (R&G Intermediate)
        "Ano ang edad ni Bob?",
        # page-52/numbered/sent-159 (R&G Intermediate)
        "Pupunta ba si Bob sa party?",
        # page-27/prose/sent-72 (R&G Intermediate)
        "Hindi ka ba Pilipino?",
        # page-60/prose/sent-224 (R&G Intermediate)
        "Ito ang nanay ni Fred.",
        # page-27/prose/sent-70 (R&G Intermediate)
        "Hindi ba Pilipino si Fred?",
        # page-28/prose/sent-74 (R&G Intermediate).
        # The source PDF prints this under a "Question:" pedagogical
        # label retained verbatim in the test pre-9.X.c26. With c26's
        # ``:`` PUNCT classification, the label no longer parses as a
        # silent prefix (the colon was _UNK before and got stripped);
        # drop it — the sentence proper is the yes-no Q after the
        # colon.
        "Amerikano ba si Fred?",
        # page-124/sent-135 (R&G Conversational)
        "Pinili niya ako at si Joe.",
        # page-91/sent-94 (R&G Conversational; verbatim 'SI' caps)
        "Bumili SI Rosa ng bigas.",
    ])
    def test_audit_closure(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse for audit closure {sentence!r}"


class TestPhase9bRegressions:
    """Existing proper-name parses unchanged."""

    @pytest.mark.parametrize("sentence", [
        # Phase 8.I Betty, Blas
        "Ano ang nakita ni Blas?",
        # Phase 8.L Mary, John, Karla, Frank
        "Hindi kasingtalino ni Mary si John.",
        # Phase 8.O Gina, Emmanuel
        "Nagpasabi si Gina na uuwi siya.",
        # Phase 8.T Ben
        "Pumunta si Ben.",
        # Phase 7+ Maria
        "Si Maria ang dumating.",
    ])
    def test_regression_holds(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"regression on {sentence!r}"


class TestPhase9bOutOfScope:
    """Residual 9.B-candidate rows that don't close on lex alone —
    each blocked by an orthogonal grammar/feat gap. Pin each;
    flip when the named follow-on sub-PR closes it."""

    def test_pamilyang_pilipino_n_modifier_chain(self) -> None:
        """ANG PAMILYA/sent-5 ``Ang pinakaubod ng pamilyang Pilipino
        ay ang ama, ina at mga anak.`` — was 9.B-blocked by the
        absence of an ay-fronted two-NP equational chart rule; closed
        in Phase 10.J.post-6 by adding ``S → NP[CASE=NOM]
        PART[LINK=AY] NP[CASE=NOM]`` (parallel to the bare two-NP
        equational of Phase 8.Y/8.Z). The post-`ay` half
        ``ang ama, ina at mga anak`` was already an NP[CASE=NOM]
        with COORD=AND (Oxford-comma + ``at`` final via 9.X.c5
        NP-comma-at coord); the missing piece was the ay-fronted
        equational glue."""
        from tgllfg.core.pipeline import parse_text
        s = ("Ang pinakaubod ng pamilyang Pilipino ay "
             "ang ama, ina at mga anak.")
        parses = parse_text(s, n_best=2)
        assert len(parses) >= 1, "10.J.post-6 closure"
        _ctree, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "BE-NP <SUBJ>"
        assert fs.feats.get("PREDICATIVE") is True
        # TOPIC bound to SUBJ (the fronted ``Ang pinakaubod...``).
        topic = fs.feats.get("TOPIC")
        subj = fs.feats.get("SUBJ")
        assert topic is not None and subj is not None
        assert topic.id == subj.id, "TOPIC == SUBJ for ay-fronting"

    def test_lisa_appositive_kay_ben(self) -> None:
        """page-237/numbered/sent-1695 ``Sasama ba si Lisa kay Ben?``
        — closes in 9.B lex but the audit version blocks. Probe
        confirms still failing — likely Q-particle ``ba`` + DAT-PRON
        ``kay`` interaction. Pin until 9.U."""
        from tgllfg.core.pipeline import parse_text
        s = "Sasama ba si Lisa kay Ben?"
        # If this starts parsing post-9.B, that's a positive
        # surprise — flip to TestPhase9bClosedIn9b
        assert len(parse_text(s, n_best=2)) == 0

    def test_kamag_anak_oov(self) -> None:
        """page-238/sent (R&G Intermediate) ``Kamag-anak siya ng
        mga Santos.`` — santos is now indexed, but ``kamag-anak``
        ("relative") remains OOV. Phase 9.C common-noun batch."""
        from tgllfg.core.pipeline import parse_text
        s = "Kamag-anak siya ng mga Santos."
        assert len(parse_text(s, n_best=2)) == 0


class TestPhase9bSurnameAsSantosOnly:
    """Confirm `santos` parses in surname position even though
    `kamag-anak` blocks the audit verbatim."""

    def test_santos_as_surname_in_simple_shape(self) -> None:
        from tgllfg.core.pipeline import parse_text
        # G. Santos parses as a multi-part proper-noun shape
        # (the G. abbreviation is handled by mistakable-N path).
        parses = parse_text("Ano ang ginawa ni G. Santos?", n_best=3)
        assert len(parses) >= 1
