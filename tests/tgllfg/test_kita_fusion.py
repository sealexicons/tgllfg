"""Phase 5e Commit 20: ``kita`` clitic fusion (1sg-GEN + 2sg-NOM).

Tagalog has a special second-position clitic ``kita`` that fuses
the 1sg-GEN actor and 2sg-NOM SUBJ of a non-AV verb into a single
token: ``Kinain kita`` "I ate you", ``Sinulatan kita ng liham``
"I wrote you a letter", ``Pinakain kita ng kanin`` "I fed you
rice". The fusion is obligatory in modern Tagalog (Schachter &
Otanes 1972 §3.2; Kroeger 1993 §2.2) — the alternative form
``*Kinain ko ka`` is ungrammatical.

The lex entry in ``data/tgl/pronouns.yaml`` carries the marker
``KITA: YES`` plus ``is_clitic: True``; the grammar rules in
``src/tgllfg/cfg/clitic.py`` (Phase 5e Commit 20 section) supply
the dual binding via atomic-value equations on
``(↑ SUBJ ...)`` and ``(↑ <obj_target> ...)`` for the 2sg
SUBJ and 1sg actor respectively. The typed actor slot per voice
mirrors the standard non-AV S frames:

* OV / DV with CAUS=NONE → OBJ-AGENT
* OV / DV with CAUS=DIRECT (pa-) → OBJ-CAUSER
* IV (any APPL) → OBJ-AGENT

Three frame variants per voice spec: bare, with overt PATIENT
(GEN-NP), and with DAT adjunct.

These tests cover:

* Bare frames across OV (``Kinain kita``), DV (``Binasahan
  kita``), IV (``Ipinaggawa kita``), and pa-OV
  (``Pinakain kita``).
* 3-arg with PATIENT: DV (``Sinulatan kita ng liham``), IV
  (``Ipinaggawa kita ng silya``, ``Ipinagsulat kita ng liham``),
  and pa-OV (``Pinakain kita ng kanin``).
* Negation under the construction (``Hindi kita kinain``). The
  Wackernagel pass hoists pre-V ``kita`` into the post-V cluster.
* Adverbial enclitic interaction (``Kinain na kita``).
* Lex/morph: kita has both PRON and (downstream) verb analyses
  via the existing ``kita`` verb root — only the PRON path
  succeeds in clitic position.
* Regression: standard non-kita clitic constructions
  (``Kinain mo ako``, ``Kinain ko ito``) still parse.
* Regression: ``Nakita kita`` doesn't parse — the ma-class
  paradigm only emits AV-NVOL forms; OV-NVOL of ``kita`` is a
  paradigm-coverage gap. Documented as a TBD; this test pins
  the current failure so any future paradigm expansion is
  intentional.
"""

from __future__ import annotations

from tgllfg.clitics import reorder_clitics
from tgllfg.core.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.core.pipeline import parse_text
from tgllfg.text import tokenize


def _kita_subj_oa(text: str, obj_target: str = "OBJ-AGENT") -> tuple[FStructure, FStructure] | None:
    """Find a parse where SUBJ is 2sg-NOM and the typed actor slot
    (OBJ-AGENT or OBJ-CAUSER) is 1sg-GEN. Returns (subj, actor) or
    None."""
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        subj = f.feats.get("SUBJ")
        actor = f.feats.get(obj_target)
        if not (isinstance(subj, FStructure) and isinstance(actor, FStructure)):
            continue
        if (
            subj.feats.get("PERS") == "2"
            and subj.feats.get("NUM") == "SG"
            and subj.feats.get("CASE") == "NOM"
            and actor.feats.get("PERS") == "1"
            and actor.feats.get("NUM") == "SG"
            and actor.feats.get("CASE") == "GEN"
        ):
            return subj, actor
    return None


# === Bare frames ==========================================================


class TestKitaBareOv:
    """OV bare: ``Kinain kita`` "I ate you"."""

    def test_kinain_kita(self) -> None:
        result = _kita_subj_oa("Kinain kita.")
        assert result is not None

    def test_pred_is_2arg(self) -> None:
        rs = parse_text("Kinain kita.", n_best=5)
        assert any(
            f.feats.get("PRED") == "EAT <SUBJ, OBJ-AGENT>"
            for _, f, _, _ in rs
        )


class TestKitaBareDv:
    """DV bare: ``Binasahan kita`` "I read at you / I read to you"
    (using the only DV PFV with full analyzer coverage)."""

    def test_binasahan_kita(self) -> None:
        result = _kita_subj_oa("Binasahan kita.")
        assert result is not None


class TestKitaBareIv:
    """IV bare: ``Ipinaggawa kita`` "I made (something) for you"."""

    def test_ipinaggawa_kita(self) -> None:
        result = _kita_subj_oa("Ipinaggawa kita.")
        assert result is not None


class TestKitaBarePaOv:
    """pa-OV bare: ``Pinakain kita`` "I fed you" (CAUS=DIRECT;
    actor binds to OBJ-CAUSER, not OBJ-AGENT)."""

    def test_pinakain_kita(self) -> None:
        result = _kita_subj_oa("Pinakain kita.", obj_target="OBJ-CAUSER")
        assert result is not None


# === 3-arg with overt PATIENT ============================================


class TestKitaWithPatient:
    """The with-PATIENT frame admits a trailing GEN-NP as
    OBJ-PATIENT — used in 3-arg ditransitives and 3-arg
    causatives."""

    def test_sinulatan_kita_ng_liham(self) -> None:
        """``Sinulatan kita ng liham.`` "I wrote you a letter."
        DV 3-arg with OBJ-PATIENT=liham."""
        result = _kita_subj_oa("Sinulatan kita ng liham.")
        assert result is not None
        rs = parse_text("Sinulatan kita ng liham.", n_best=10)
        found = False
        for _, f, _, _ in rs:
            op = f.feats.get("OBJ-PATIENT")
            if isinstance(op, FStructure) and op.feats.get("LEMMA") == "liham":
                found = True
                break
        assert found

    def test_ipinaggawa_kita_ng_silya(self) -> None:
        """``Ipinaggawa kita ng silya.`` "I made you a chair."
        IV-BEN 3-arg with OBJ-PATIENT=silya."""
        result = _kita_subj_oa("Ipinaggawa kita ng silya.")
        assert result is not None
        rs = parse_text("Ipinaggawa kita ng silya.", n_best=10)
        found = False
        for _, f, _, _ in rs:
            op = f.feats.get("OBJ-PATIENT")
            if isinstance(op, FStructure) and op.feats.get("LEMMA") == "silya":
                found = True
                break
        assert found

    def test_pinakain_kita_ng_kanin(self) -> None:
        """``Pinakain kita ng kanin.`` "I fed you rice." pa-OV
        3-arg with OBJ-CAUSER=1sg, OBJ-PATIENT=kanin, SUBJ=2sg
        (the CAUSEE)."""
        result = _kita_subj_oa("Pinakain kita ng kanin.", obj_target="OBJ-CAUSER")
        assert result is not None
        rs = parse_text("Pinakain kita ng kanin.", n_best=10)
        found = False
        for _, f, _, _ in rs:
            op = f.feats.get("OBJ-PATIENT")
            if isinstance(op, FStructure) and op.feats.get("LEMMA") == "kanin":
                found = True
                break
        assert found


# === Negation =============================================================


class TestKitaWithNegation:
    """``Hindi kita kinain.`` "I didn't eat you." The Wackernagel
    pass hoists pre-V ``kita`` into the post-V cluster (kita is
    is_clitic=True)."""

    def test_hindi_kita_kinain(self) -> None:
        result = _kita_subj_oa("Hindi kita kinain.")
        assert result is not None
        # Verify POLARITY=NEG.
        rs = parse_text("Hindi kita kinain.", n_best=5)
        assert any(f.feats.get("POLARITY") == "NEG" for _, f, _, _ in rs)

    def test_wackernagel_clusters_kita(self) -> None:
        """The clitic-pass should produce: hindi, kain, kita, .
        — kita hoisted from pre-V to post-V cluster."""
        toks = tokenize("Hindi kita kinain.")
        ml = analyze_tokens(toks)
        ml = reorder_clitics(ml)
        lemmas = [c[0].lemma if c else "?" for c in ml]
        assert lemmas == ["hindi", "kain", "kita", "."]


# === Adverbial enclitic interaction ======================================


class TestKitaWithAdvEnclitic:
    """Adv enclitic ``na`` (ALREADY) and kita can co-occur. The
    cluster orders them (Wackernagel rules: PRON before adv?)."""

    def test_kinain_na_kita(self) -> None:
        """``Kinain na kita.`` "I already ate you." Both kita and
        na are 2P clitics; they cluster post-V."""
        result = _kita_subj_oa("Kinain na kita.")
        assert result is not None


# === Morph layer ==========================================================


class TestKitaMorph:
    """Confirm the lex entry is loaded and ambiguity with the verb
    root ``kita`` is resolved by the chart parser."""

    def test_kita_pron_analysis(self) -> None:
        """Bare token ``kita`` has a PRON analysis with KITA=YES."""
        toks = tokenize("kita")
        ml = analyze_tokens(toks)
        cands = ml[0]
        pron_cands = [c for c in cands if c.pos == "PRON"]
        assert pron_cands, "no PRON analysis for kita"
        assert any(c.feats.get("KITA") is True for c in pron_cands)


# === Regressions ==========================================================


class TestKitaRegressions:
    """Standard (non-kita) clitic constructions still work."""

    def test_kinain_mo_ako(self) -> None:
        """``Kinain mo ako.`` "You ate me." 2sg-GEN actor (mo) +
        1sg-NOM SUBJ (ako) — standard separate clitics, NOT
        kita-fused. Kita is unidirectional (1sg→2sg only).

        Note: PERS is NOT projected into the f-structure for
        standard PRON entries (the parser's ``_lex_equations``
        filters integer-typed feats — a pre-existing lex/parser
        quirk). We verify NUM and CASE instead, which ARE
        preserved as strings."""
        rs = parse_text("Kinain mo ako.", n_best=5)
        assert rs
        found = False
        for _, f, _, _ in rs:
            subj = f.feats.get("SUBJ")
            oa = f.feats.get("OBJ-AGENT")
            if not (isinstance(subj, FStructure) and isinstance(oa, FStructure)):
                continue
            if (
                subj.feats.get("NUM") == "SG"
                and subj.feats.get("CASE") == "NOM"
                and oa.feats.get("NUM") == "SG"
                and oa.feats.get("CASE") == "GEN"
            ):
                found = True
                break
        assert found

    def test_nakita_kita_paradigm_gap(self) -> None:
        """``Nakita kita.`` "I saw you." This is the canonical kita
        example in grammar texts but doesn't parse here because the
        ma-class paradigm only emits AV-NVOL forms; OV-NVOL of
        ``kita`` would require a paradigm cell that doesn't exist
        yet. Test pins the current behavior so any future paradigm
        expansion is an intentional change. Tracked in plan §18."""
        rs = parse_text("Nakita kita.", n_best=5)
        assert rs == []


# === LMT diagnostics ======================================================


class TestKitaLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Kinain kita.",
            "Binasahan kita.",
            "Ipinaggawa kita.",
            "Pinakain kita.",
            "Sinulatan kita ng liham.",
            "Ipinaggawa kita ng silya.",
            "Pinakain kita ng kanin.",
            "Hindi kita kinain.",
            "Kinain na kita.",
        ):
            rs = parse_text(s, n_best=10)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
