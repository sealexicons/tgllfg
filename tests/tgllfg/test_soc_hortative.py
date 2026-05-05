"""Phase 5e Commit 21: SOC mood (hortative) with `tayo` 1pl-INCL pivot.

Tagalog has a hortative ("let's X") construction using the bare
``mag-`` + base form (no CV-redup, no realis prefix) with the
1pl-INCL pivot ``tayo``: ``Magkape tayo`` "Let's have coffee",
``Maglinis tayo ng kuwarto`` "Let's clean the room",
``Magsayaw tayo`` "Let's dance". The Phase 4 §7.2 mood
inventory already included ``MOOD=SOC`` (social / sociative)
but left it inventory-only; this commit lifts SOC for the
hortative case (Phase 5e Commit 12 already lifted SOC for the
``mag-...-an`` reciprocal).

The lift has two pieces:

* **Paradigm cell** (``data/tgl/paradigms.yaml``): a new
  AV-mag-SOC cell emits ``mag-`` + base (no redup) with
  ``MOOD=SOC`` for any mag-class root. Generates ``maglinis``,
  ``magbigay``, ``magsulat``, ``magsayaw``, ``magkape``, etc.
* **Denominal verb** (``data/tgl/verbs.yaml``): ``kape`` is
  added as a dual NOUN+VERB (mag-class) so the canonical
  example ``Magkape tayo`` parses. The mag-NOUN denominal
  pattern is productive in Tagalog; this commit picks just
  ``kape`` for the seed corpus.

No new grammar rules are needed — the existing AV intransitive
and AV transitive S frames carry MOOD from V to matrix.

These tests cover:

* Intransitive SOC: ``Magsayaw tayo``, ``Magkanta tayo``,
  ``Magpasyal tayo``, ``Magkape tayo``.
* Transitive SOC with overt OBJ: ``Maglinis tayo ng kuwarto``,
  ``Maglaba tayo ng damit``, ``Magsulat tayo ng liham``.
* SOC + adv enclitic: ``Magsayaw tayo na`` "Let's dance
  already".
* SOC + interrogative: ``Magkape tayo ba?`` "Shall we have
  coffee?".
* SOC + DAT adjunct: ``Magsayaw tayo sa kuwarto``.
* Morph: bare mag-form analyses with MOOD=SOC for mag-class
  roots; the SOC form coexists with the existing PFV / IPFV /
  CTPL forms (different surfaces).
* Regression: the PFV form ``naglinis`` still parses with
  MOOD=IND (the new SOC cell doesn't shadow existing forms).
* Regression: ``Kumain tayo.`` (um-class, not mag-class) still
  parses as MOOD=IND with the standard intransitive AV frame —
  the SOC cell only fires for mag-class roots.
"""

from __future__ import annotations

from tgllfg.core.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.core.pipeline import parse_text
from tgllfg.text import tokenize


def _soc_parse(text: str) -> FStructure | None:
    """Find a parse with MOOD=SOC and tayo as SUBJ. Returns the
    matrix f-structure or None."""
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        if f.feats.get("MOOD") != "SOC":
            continue
        subj = f.feats.get("SUBJ")
        if not isinstance(subj, FStructure):
            continue
        if (
            subj.feats.get("NUM") == "PL"
            and subj.feats.get("CLUSV") == "INCL"
            and subj.feats.get("CASE") == "NOM"
        ):
            return f
    return None


# === Intransitive SOC =====================================================


class TestSocIntransitive:
    """Intransitive AV-mag-SOC verbs with the 1pl-INCL pivot
    ``tayo``. PRED is ``<SUBJ>``."""

    def test_magsayaw_tayo(self) -> None:
        f = _soc_parse("Magsayaw tayo.")
        assert f is not None
        assert f.feats.get("PRED") == "SAYAW <SUBJ>"

    def test_magkanta_tayo(self) -> None:
        f = _soc_parse("Magkanta tayo.")
        assert f is not None
        assert f.feats.get("PRED") == "KANTA <SUBJ>"

    def test_magpasyal_tayo(self) -> None:
        f = _soc_parse("Magpasyal tayo.")
        assert f is not None

    def test_magkape_tayo_canonical(self) -> None:
        """``Magkape tayo.`` "Let's have coffee." — the canonical
        example from grammar texts. Uses the new denominal
        mag-NOUN form added in Commit 21."""
        f = _soc_parse("Magkape tayo.")
        assert f is not None
        assert f.feats.get("PRED") == "KAPE <SUBJ>"


# === Transitive SOC with overt OBJ ========================================


class TestSocTransitive:
    """Transitive AV-mag-SOC verbs require an overt OBJ (mag- + TR
    root yields PRED ``<SUBJ, OBJ>``). The standard AV transitive
    S frame fires unchanged; MOOD=SOC propagates from V."""

    def test_maglinis_tayo_ng_kuwarto(self) -> None:
        f = _soc_parse("Maglinis tayo ng kuwarto.")
        assert f is not None
        assert f.feats.get("PRED") == "LINIS <SUBJ, OBJ>"
        obj = f.feats.get("OBJ")
        assert isinstance(obj, FStructure)
        assert obj.feats.get("LEMMA") == "kuwarto"

    def test_maglaba_tayo_ng_damit(self) -> None:
        f = _soc_parse("Maglaba tayo ng damit.")
        assert f is not None
        assert f.feats.get("PRED") == "LABA <SUBJ, OBJ>"

    def test_magsulat_tayo_ng_liham(self) -> None:
        f = _soc_parse("Magsulat tayo ng liham.")
        assert f is not None


# === SOC + clitics ========================================================


class TestSocWithClitics:
    """SOC composes with adverbial enclitics (``na`` ALREADY,
    ``ba`` interrogative)."""

    def test_magsayaw_tayo_na(self) -> None:
        """``Magsayaw tayo na.`` "Let's dance already." — adv
        enclitic ``na`` lands in matrix ADJ."""
        f = _soc_parse("Magsayaw tayo na.")
        assert f is not None

    def test_magkape_tayo_ba(self) -> None:
        """``Magkape tayo ba?`` "Shall we have coffee?" —
        interrogative ``ba`` lands in matrix ADJ."""
        f = _soc_parse("Magkape tayo ba?")
        assert f is not None


# === SOC + DAT adjunct ====================================================


class TestSocWithDat:
    """The intransitive AV S frame admits a DAT adjunct; SOC
    composes."""

    def test_magsayaw_tayo_sa_kuwarto(self) -> None:
        """``Magsayaw tayo sa kuwarto.`` "Let's dance in the
        room." DAT adjunct."""
        f = _soc_parse("Magsayaw tayo sa kuwarto.")
        assert f is not None


# === Morph layer ==========================================================


class TestSocMorph:
    """The new paradigm cell emits the SOC form for any mag-class
    root."""

    def test_mag_soc_forms(self) -> None:
        for tok, expected_lemma in [
            ("maglinis", "linis"),
            ("magbigay", "bigay"),
            ("magsulat", "sulat"),
            ("magluto", "luto"),
            ("magsayaw", "sayaw"),
            ("magkape", "kape"),
        ]:
            toks = tokenize(tok)
            ml = analyze_tokens(toks)
            cands = ml[0]
            soc_cands = [
                ma for ma in cands
                if ma.pos == "VERB" and ma.feats.get("MOOD") == "SOC"
            ]
            assert soc_cands, f"no SOC analysis for {tok}"
            assert soc_cands[0].lemma == expected_lemma


# === Regressions ==========================================================


class TestSocRegressions:
    """Existing IND forms and non-mag-class verbs are unaffected."""

    def test_naglinis_still_pfv_ind(self) -> None:
        """The new SOC cell coexists with the existing PFV cell;
        ``naglinis`` analyses as PFV / IND, not SOC. Different
        surface, no shadowing."""
        toks = tokenize("naglinis")
        ml = analyze_tokens(toks)
        cands = ml[0]
        ind_cands = [
            ma for ma in cands
            if ma.pos == "VERB"
            and ma.feats.get("MOOD") == "IND"
            and ma.feats.get("ASPECT") == "PFV"
        ]
        assert ind_cands

    def test_kumain_tayo_unaffected(self) -> None:
        """``Kumain tayo.`` (um-class, not mag-class) still parses
        as MOOD=IND. The SOC cell only fires for mag-class roots."""
        rs = parse_text("Kumain tayo.", n_best=5)
        assert rs
        f = rs[0][1]
        assert f.feats.get("MOOD") == "IND"
        assert f.feats.get("PRED") == "EAT <SUBJ>"

    def test_kape_noun_still_works(self) -> None:
        """``ang kape ko`` "my coffee" — kape as a NOUN still
        parses. The new VERB entry coexists with the existing
        NOUN entry."""
        rs = parse_text("Kumain ako ng kape.", n_best=5)
        assert rs
        # Some parse should treat kape as a NOUN (the OBJ).
        found = False
        for _, f, _, _ in rs:
            obj = f.feats.get("OBJ")
            if isinstance(obj, FStructure) and obj.feats.get("LEMMA") == "kape":
                found = True
                break
        assert found


# === LMT diagnostics ======================================================


class TestSocLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Magsayaw tayo.",
            "Magkanta tayo.",
            "Magpasyal tayo.",
            "Magkape tayo.",
            "Maglinis tayo ng kuwarto.",
            "Maglaba tayo ng damit.",
            "Magsulat tayo ng liham.",
            "Magsayaw tayo na.",
            "Magsayaw tayo sa kuwarto.",
        ):
            rs = parse_text(s, n_best=10)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
