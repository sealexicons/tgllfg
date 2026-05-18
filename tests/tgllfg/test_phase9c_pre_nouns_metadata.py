"""Phase 9.C.pre: nouns.yaml metadata schema + migration tests.

Refactor sub-PR — no parser behavior change. Tests cover:

* Schema validation: bad subclass / source / loan values fail-fast.
* Field plumbing: loader reads the new fields from real entries.
* Migration sanity: gloss bare, metadata in structured fields.
* Polysemy split: ``amerikana`` resolves to two distinct entries.
* New entries: ``pinoy`` / ``pinay`` registered with REGISTER=COLLOQUIAL.
* Orthographic variants: ``blas`` carries ``[bias]`` OCR variant;
  ``tita``/``tito`` carry ``[tiya]``/``[tiyo]`` spelling variants.
* No regressions on existing parses (sanity sample).
"""

from __future__ import annotations

from pathlib import Path

import pytest


# ---- Schema-validation tests --------------------------------------

class TestSchemaValidation:
    """Loader-level validation — typos in subclass / source / loan
    raise ValueError with a clear message."""

    @staticmethod
    def _load_from_yaml_text(text: str):
        """Helper: write text to a temp file, parse via _load_roots."""
        import tempfile
        from tgllfg.morph.loader import _load_roots
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False,
        ) as f:
            f.write(text)
            path = Path(f.name)
        try:
            return _load_roots(path)
        finally:
            path.unlink()

    def test_valid_subclass_loads(self) -> None:
        roots = self._load_from_yaml_text(
            "- citation: foo\n"
            "  pos: NOUN\n"
            "  subclass: [PERSON, MALE]\n"
        )
        assert len(roots) == 1
        assert roots[0].subclass == ["PERSON", "MALE"]

    def test_bad_subclass_atom_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown subclass atom"):
            self._load_from_yaml_text(
                "- citation: foo\n"
                "  pos: NOUN\n"
                "  subclass: [BOGUS]\n"
            )

    def test_two_named_entity_tags_raises(self) -> None:
        with pytest.raises(ValueError, match="at most one named-entity"):
            self._load_from_yaml_text(
                "- citation: foo\n"
                "  pos: NOUN\n"
                "  subclass: [PERSON, PLACE]\n"
            )

    def test_two_gender_tags_raises(self) -> None:
        with pytest.raises(ValueError, match="at most one gender"):
            self._load_from_yaml_text(
                "- citation: foo\n"
                "  pos: NOUN\n"
                "  subclass: [MALE, FEMALE]\n"
            )

    def test_valid_source_loads(self) -> None:
        roots = self._load_from_yaml_text(
            "- citation: foo\n"
            "  pos: NOUN\n"
            "  source: S&O-1972\n"
        )
        assert roots[0].source == "S&O-1972"

    def test_bad_source_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown source"):
            self._load_from_yaml_text(
                "- citation: foo\n"
                "  pos: NOUN\n"
                "  source: 'Bogus-Source'\n"
            )

    def test_valid_loan_loads(self) -> None:
        roots = self._load_from_yaml_text(
            "- citation: foo\n"
            "  pos: NOUN\n"
            "  loan: SPANISH\n"
        )
        assert roots[0].loan == "SPANISH"

    def test_bad_loan_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown loan"):
            self._load_from_yaml_text(
                "- citation: foo\n"
                "  pos: NOUN\n"
                "  loan: BOGUSIAN\n"
            )

    def test_orth_variants_field_removed(self) -> None:
        """Phase 9.X.pre-1.21: ``orth_variants`` was removed.
        Lingering YAML usage must raise so future contributors
        notice and migrate to ``feats: {LEMMA: <canonical>}`` on a
        separate variant root entry."""
        with pytest.raises(ValueError, match="'orth_variants' field was removed"):
            self._load_from_yaml_text(
                "- citation: foo\n"
                "  pos: NOUN\n"
                "  orth_variants: [foo-alt]\n"
            )

    def test_subclass_must_be_list(self) -> None:
        with pytest.raises(ValueError, match="'subclass' must be a list"):
            self._load_from_yaml_text(
                "- citation: foo\n"
                "  pos: NOUN\n"
                "  subclass: 'PERSON'\n"
            )

    def test_empty_new_fields_load_as_defaults(self) -> None:
        """Entries without new fields load with empty defaults."""
        roots = self._load_from_yaml_text(
            "- citation: foo\n"
            "  pos: NOUN\n"
            "  gloss: foo-gloss\n"
        )
        assert roots[0].subclass == []
        assert roots[0].source == ""
        assert roots[0].loan == ""


# ---- Real-entry plumbing tests ------------------------------------

class TestRealEntryFields:
    """The migrated nouns.yaml entries carry the expected new fields."""

    @pytest.fixture
    def roots_by_cit(self):
        from tgllfg.morph.loader import load_morph_data
        m = load_morph_data()
        idx: dict[str, list] = {}
        for r in m.roots:
            idx.setdefault(r.citation, []).append(r)
        return idx

    def test_ben_subclass_and_source(self, roots_by_cit) -> None:
        ben = roots_by_cit["ben"][0]
        assert ben.subclass == ["PERSON", "MALE"]
        assert ben.source == "S&O-1972"
        assert ben.gloss == "Ben"  # bare, no parenthetical

    def test_pilipinas_place(self, roots_by_cit) -> None:
        r = roots_by_cit["pilipinas"][0]
        assert r.subclass == ["PLACE"]
        assert r.source == "audit-corpus"
        assert r.gloss == "Philippines"

    def test_relos_loan(self, roots_by_cit) -> None:
        r = roots_by_cit["relos"][0]
        assert r.loan == "SPANISH"
        assert r.source == "S&O-1972"
        assert "loan" not in r.gloss.lower()

    def test_blas_subclass_and_no_ocr_variant(self, roots_by_cit) -> None:
        """``blas`` subclass / gloss check. The original
        ``orth_variants: [bias]`` annotation from 9.C.pre was
        dropped in Phase 9.H after user-verified PDF eyeball
        (``data/tgl/references/scans/blas.png``) confirmed
        ``Bias`` is an OCR artifact, not a real spelling
        variant — the fix landed at-source in the R&C 1990
        extracted text rather than in lex. Phase 9.X.pre-1.21
        removed the ``orth_variants`` field entirely (was loader-
        validated dead code; canonical mechanism is per-variant
        root with ``feats: {LEMMA: <canonical>}``)."""
        b = roots_by_cit["blas"][0]
        assert b.subclass == ["PERSON", "MALE"]
        assert "OCR" not in b.gloss

    def test_ama_register_formal(self, roots_by_cit) -> None:
        r = roots_by_cit["ama"][0]
        assert r.feats.get("REGISTER") == "FORMAL"
        assert r.gloss == "father"

    def test_inay_register_affective(self, roots_by_cit) -> None:
        r = roots_by_cit["inay"][0]
        assert r.feats.get("REGISTER") == "AFFECTIVE"
        assert r.gloss == "mother"

    def test_eskwela_register_and_synonym(self, roots_by_cit) -> None:
        r = roots_by_cit["eskwela"][0]
        assert r.feats.get("REGISTER") == "COLLOQUIAL"
        assert "paaralan" in r.synonyms
        assert "cf." not in r.gloss
        assert r.gloss == "school"


# ---- Nationality-noun gender-neutrality + amerikana-as-clothing ---

class TestNationalityNouns:
    """Spanish-loan nationality nouns where the etymological gender
    has bleached (pilipino, amerikano) get `[NATIONAL]` only — no
    MALE tag. The feminine form (pilipina, pinay) keeps FEMALE when
    it's genuinely gender-marked usage."""

    @pytest.fixture
    def roots_by_cit(self):
        from tgllfg.morph.loader import load_morph_data
        m = load_morph_data()
        idx: dict[str, list] = {}
        for r in m.roots:
            idx.setdefault(r.citation, []).append(r)
        return idx

    def test_pilipino_gender_neutral(self, roots_by_cit) -> None:
        r = roots_by_cit["pilipino"][0]
        assert r.subclass == ["NATIONAL"]

    def test_amerikano_gender_neutral(self, roots_by_cit) -> None:
        # Per GT: "American" (ADJ) / "US citizen" (N); not gender-marked
        # in common usage.
        r = roots_by_cit["amerikano"][0]
        assert r.subclass == ["NATIONAL"]

    def test_amerikana_clothing_only(self, roots_by_cit) -> None:
        """Single amerikana entry — clothing item (per GT:
        coat / overcoat / two-piece suit). The 'American woman' sense
        was dropped — speculative without audit-corpus pressure."""
        amerikanas = roots_by_cit["amerikana"]
        assert len(amerikanas) == 1
        r = amerikanas[0]
        assert r.loan == "SPANISH"
        assert r.subclass == []  # not a NATIONAL — it's an item


# ---- New entries (pinoy / pinay) ----------------------------------

class TestPinoyPinay:
    """Pinoy/Pinay colloquial-register NATIONAL nouns."""

    @pytest.fixture
    def roots_by_cit(self):
        from tgllfg.morph.loader import load_morph_data
        m = load_morph_data()
        return {r.citation: r for r in m.roots
                if r.citation in ("pinoy", "pinay")}

    def test_pinoy_present(self, roots_by_cit) -> None:
        assert "pinoy" in roots_by_cit
        r = roots_by_cit["pinoy"]
        assert r.subclass == ["NATIONAL"]
        assert r.feats.get("REGISTER") == "COLLOQUIAL"
        assert r.source == "ref-grammar"

    def test_pinay_present(self, roots_by_cit) -> None:
        assert "pinay" in roots_by_cit
        r = roots_by_cit["pinay"]
        assert r.subclass == ["NATIONAL", "FEMALE"]
        assert r.feats.get("REGISTER") == "COLLOQUIAL"

    def test_pinoy_pinay_parse(self) -> None:
        from tgllfg.core.pipeline import parse_text
        # Both should parse as N-pivot equational predicates.
        assert len(parse_text("Pinoy siya.", n_best=2)) >= 1
        assert len(parse_text("Pinay si Maria.", n_best=2)) >= 1


# ---- Orthographic-variant tests -----------------------------------

class TestOrthVariants:
    """Phase 9.X.pre-1.21: orthographic-variant pointers migrated
    from the dead ``orth_variants`` metadata field to the
    analyzer-honored ``feats: {LEMMA: <canonical>}`` mechanism on
    a separate variant root entry. Each variant has citation =
    variant surface and ``feats.LEMMA`` pointing at the canonical
    citation."""

    @pytest.fixture
    def roots_by_cit(self):
        from tgllfg.morph.loader import load_morph_data
        m = load_morph_data()
        return {r.citation: r for r in m.roots}

    def test_tita_tiya_pointer(self, roots_by_cit) -> None:
        # tita is canonical; tiya is a separate variant root that
        # points at tita via feats.LEMMA.
        assert "tita" in roots_by_cit
        tiya = roots_by_cit["tiya"]
        assert tiya.feats.get("LEMMA") == "tita"

    def test_tito_tiyo_pointer(self, roots_by_cit) -> None:
        assert "tito" in roots_by_cit
        tiyo = roots_by_cit["tiyo"]
        assert tiyo.feats.get("LEMMA") == "tito"

    def test_blas_no_bias_ocr_variant(self, roots_by_cit) -> None:
        """``blas`` does NOT have a ``bias`` variant pointer.
        9.C.pre originally added ``bias`` to ``blas.orth_variants``
        on the assumption that ``Bias`` was a spelling variant;
        9.H confirmed via PDF scan that it's an OCR artifact and
        dropped the annotation. The audit-corpus source text was
        hand-corrected instead. Post-9.X.pre-1.21 migration the
        check is that no root with citation ``bias`` exists
        pointing at ``blas`` via feats.LEMMA."""
        bias = roots_by_cit.get("bias")
        assert bias is None or bias.feats.get("LEMMA") != "blas"


# ---- No-regression sanity sample ----------------------------------

class TestNoRegression:
    """Migration didn't break existing audit-corpus parses."""

    @pytest.mark.parametrize("sentence", [
        # Phase 9.B closures
        "Si David ang dumating.",
        "Pumunta siya sa Pilipinas.",
        "Hindi ba siya Pilipino?",
        # Phase 8 proper-name closures
        "Pumunta si Ben.",
        "Si Maria ang dumating.",
        # Time-marker entries (alasdies etc. — feats: {SEM_CLASS: TIME})
        "Alas singko.",
        # Register-marked entries (ama / inay etc.)
        "Si Inay ang dumating.",
        "Eskwela siya.",
    ])
    def test_no_regression(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"regression on {sentence!r}"
