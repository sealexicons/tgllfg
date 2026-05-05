"""Phase 5e Commit 3: AdvP / PP ay-fronting.

Phase 4 §7.4's "Out-of-scope" list flagged AdvP / PP ay-fronting as
"deferred until the categorial inventory expands". This commit adds
the smallest categorial expansion that lifts the deferral:

* Two new POS values seeded in ``data/tgl/particles.yaml``:
  - ``ADV`` — temporal adverbs (kahapon, ngayon, bukas, mamaya).
  - ``PREP`` — compound preposition heads (para, tungkol, mula, dahil).
* Two new non-terminals: ``AdvP`` (single ADV word) and ``PP``
  (PREP + sa-NP complement).
* Two new ay-fronting wrap rules:
  - ``S → AdvP PART[LINK=AY] S``
  - ``S → PP   PART[LINK=AY] S``
  Both rules make the fronted phrase BOTH the matrix TOPIC and a
  member of the matrix's ADJ set; the inner clause is a complete S
  with no gap (AdvP / PP isn't an argument of any voice/aspect frame).

Sentences enabled:

* ``Kahapon ay tumakbo si Maria.`` "Yesterday, Maria ran."
* ``Ngayon ay kumakain ang bata.`` "Now the child is eating."
* ``Para sa bata ay binili niya ang libro.``
  "For the child she bought the book."
* ``Tungkol sa nanay ay sumulat ang bata.``
  "About mother the child wrote."
"""

from __future__ import annotations

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _first(text: str) -> FStructure:
    rs = parse_text(text)
    assert rs, f"no parse for {text!r}"
    return rs[0][1]


def _find_topic(text: str, *, pred: str, topic_lemma: str) -> FStructure | None:
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        if f.feats.get("PRED") != pred:
            continue
        topic = f.feats.get("TOPIC")
        if isinstance(topic, FStructure) and topic.feats.get("LEMMA") == topic_lemma:
            return f
    return None


# === AdvP ay-fronting ====================================================


class TestAdvPFronting:
    """Single-word temporal adverb fronted via ``ay``. The AdvP
    becomes both the matrix TOPIC and a member of the matrix's
    ADJ set."""

    def test_kahapon_intransitive(self) -> None:
        f = _first("Kahapon ay tumakbo si Maria.")
        assert f.feats.get("PRED") == "TAKBO <SUBJ>"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "kahapon"
        assert topic.feats.get("ADV_TYPE") == "TIME"
        assert topic.feats.get("DEIXIS_TIME") == "PAST"
        # SUBJ is overt.
        subj = f.feats["SUBJ"]
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "maria"

    def test_kahapon_topic_in_adj(self) -> None:
        """The fronted AdvP is also a member of ADJ — adjunct
        semantics is preserved alongside the topic-marking."""
        f = _first("Kahapon ay tumakbo si Maria.")
        topic = f.feats["TOPIC"]
        adj = f.feats.get("ADJ")
        assert adj is not None
        adj_ids = {m.id for m in adj}  # type: ignore[union-attr]
        assert isinstance(topic, FStructure)
        assert topic.id in adj_ids

    def test_ngayon_present_transitive(self) -> None:
        f = _first("Ngayon ay kumakain ang bata.")
        # `kain` AV-intr lex entry: PRED ``EAT <SUBJ>``.
        assert f.feats.get("PRED") == "EAT <SUBJ>"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "ngayon"
        assert topic.feats.get("DEIXIS_TIME") == "PRES"
        assert f.feats.get("ASPECT") == "IPFV"

    def test_bukas_future(self) -> None:
        f = _first("Bukas ay tutulog si Maria.")
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "bukas"
        assert topic.feats.get("DEIXIS_TIME") == "FUT"

    def test_mamaya_future(self) -> None:
        f = _first("Mamaya ay tutulog si Maria.")
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "mamaya"

    def test_advp_with_negation(self) -> None:
        """Inner negation under AdvP fronting composes."""
        f = _first("Kahapon ay hindi tumakbo si Maria.")
        assert f.feats.get("PRED") == "TAKBO <SUBJ>"
        assert f.feats.get("POLARITY") == "NEG"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "kahapon"

    def test_advp_with_transitive_inner(self) -> None:
        f = _first("Kahapon ay kumain ang aso ng isda.")
        assert f.feats.get("PRED") == "EAT <SUBJ, OBJ>"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "kahapon"


# === PP ay-fronting ======================================================


class TestPpFronting:
    """PP (PREP + sa-NP) fronted via ``ay``. The PP's f-structure
    inherits PREP_TYPE from its PREP head and exposes the sa-NP
    as ``OBJ``."""

    def test_para_beneficiary(self) -> None:
        f = _first("Para sa bata ay binili niya ang libro.")
        assert f.feats.get("VOICE") == "OV"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("PREP_TYPE") == "BENEFICIARY"
        # PP exposes its sa-NP complement as OBJ.
        pp_obj = topic.feats.get("OBJ")
        assert isinstance(pp_obj, FStructure)
        assert pp_obj.feats.get("LEMMA") == "bata"

    def test_para_in_adj(self) -> None:
        f = _first("Para sa bata ay binili niya ang libro.")
        topic = f.feats["TOPIC"]
        adj = f.feats.get("ADJ")
        assert adj is not None
        adj_ids = {m.id for m in adj}  # type: ignore[union-attr]
        assert isinstance(topic, FStructure)
        assert topic.id in adj_ids

    def test_tungkol_topic(self) -> None:
        f = _first("Tungkol sa nanay ay sumulat ang bata.")
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("PREP_TYPE") == "TOPIC"
        pp_obj = topic.feats.get("OBJ")
        assert isinstance(pp_obj, FStructure)
        assert pp_obj.feats.get("LEMMA") == "nanay"

    def test_dahil_reason(self) -> None:
        f = _first("Dahil sa gutom ay kumain ang bata.")
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("PREP_TYPE") == "REASON"
        pp_obj = topic.feats.get("OBJ")
        assert isinstance(pp_obj, FStructure)
        assert pp_obj.feats.get("LEMMA") == "gutom"

    def test_mula_source(self) -> None:
        f = _first("Mula sa bahay ay tumakbo si Maria.")
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("PREP_TYPE") == "SOURCE"
        pp_obj = topic.feats.get("OBJ")
        assert isinstance(pp_obj, FStructure)
        assert pp_obj.feats.get("LEMMA") == "bahay"

    def test_pp_with_negation(self) -> None:
        f = _first("Para sa bata ay hindi binili niya ang libro.")
        assert f.feats.get("POLARITY") == "NEG"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("PREP_TYPE") == "BENEFICIARY"

    def test_pp_with_av_inner(self) -> None:
        # AV inner clause: ``Para sa bata ay kumain ang nanay``.
        f = _first("Para sa bata ay kumain ang nanay.")
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("PREP_TYPE") == "BENEFICIARY"
        # SUBJ is the AV pivot.
        subj = f.feats["SUBJ"]
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "nanay"


# === Discrimination ======================================================


class TestDiscrimination:
    """The new wrap rules don't cross-fire with existing
    NP-fronting rules: AdvP / PP is structurally distinct from
    NP[CASE=NOM/GEN/DAT]."""

    def test_advp_is_not_np(self) -> None:
        """``Kahapon ay tumakbo si Maria`` should NOT parse as
        NOM-NP fronting (kahapon as a bare N would need a DET)."""
        rs = parse_text("Kahapon ay tumakbo si Maria.", n_best=10)
        for _, f, _, _ in rs:
            topic = f.feats.get("TOPIC")
            if isinstance(topic, FStructure):
                # The topic must be the AdvP (with ADV_TYPE), not
                # an NP — NPs don't carry ADV_TYPE.
                if topic.feats.get("LEMMA") == "kahapon":
                    assert topic.feats.get("ADV_TYPE") == "TIME"

    def test_pp_does_not_attach_as_dat_np_topic(self) -> None:
        """``Para sa bata ay ...`` should route through the new PP
        wrap rule, not through the existing
        ``S → NP[CASE=DAT] PART[LINK=AY] S_GAP_OBL`` rule
        (which would treat ``sa bata`` as the topic, ignoring
        ``para``)."""
        rs = parse_text("Para sa bata ay binili niya ang libro.", n_best=10)
        # At least one parse should have PREP_TYPE on the topic (the
        # PP analysis).
        seen_pp_topic = False
        for _, f, _, _ in rs:
            topic = f.feats.get("TOPIC")
            if isinstance(topic, FStructure) and topic.feats.get("PREP_TYPE"):
                seen_pp_topic = True
                break
        assert seen_pp_topic


# === Regression: existing ay-fronting rules still work ==================


class TestRegression:
    """The new wrap rules must not affect existing ay-fronting
    parses (Phase 4 §7.4 + Phase 5d Commit 5 + Phase 5e Commits 1-2)."""

    def test_subj_pivot_unchanged(self) -> None:
        f = _first("Si Maria ay tumakbo.")
        assert f.feats.get("PRED") == "TAKBO <SUBJ>"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "maria"
        # SUBJ-fronting NPs do NOT have ADV_TYPE / PREP_TYPE.
        assert "ADV_TYPE" not in topic.feats
        assert "PREP_TYPE" not in topic.feats

    def test_obj_fronting_unchanged(self) -> None:
        f = _first("Ng isda ay kumain si Maria.")
        assert f.feats.get("PRED") == "EAT <SUBJ, OBJ>"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "isda"

    def test_obl_fronting_unchanged(self) -> None:
        f = _first("Sa bahay ay kumain si Maria.")
        assert f.feats.get("PRED") == "EAT <SUBJ>"
        topic = f.feats["TOPIC"]
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "bahay"


# === LMT diagnostics ====================================================


class TestLmtDiagnostics:
    """The new constructions produce no blocking LMT diagnostics."""

    def test_no_blocking_advp(self) -> None:
        rs = parse_text("Kahapon ay tumakbo si Maria.", n_best=5)
        for _, _f, _c, diags in rs:
            blocking = [d for d in diags if d.kind != "lmt-mismatch"]
            assert blocking == [], f"unexpected blocking diags: {blocking}"

    def test_no_blocking_pp(self) -> None:
        rs = parse_text("Para sa bata ay binili niya ang libro.", n_best=5)
        for _, _f, _c, diags in rs:
            blocking = [d for d in diags if d.kind != "lmt-mismatch"]
            assert blocking == [], f"unexpected blocking diags: {blocking}"
