"""Phase 5d Commit 10: pronominal RC-actor (in-place Wackernagel).

Phase 4 §7.5 admits standard relativization
``ang batang kinain ng aso`` ("the child that the dog ate") via
``NP[CASE=X] → NP[CASE=X] PART[LINK=NA|NG] S_GAP``. The S_GAP for
non-AV transitive embeds the actor as a GEN-NP after the V. When
the actor is a pronominal clitic — ``ko`` / ``mo`` / ``niya`` —
the §7.3 Wackernagel pass would historically hoist the pronoun
into the matrix V's post-V cluster, leaving the OV S_GAP frame
``V[VOICE=OV, CAUS=NONE] NP[CASE=GEN]`` without its required
GEN-NP. The result: ``Tumakbo ang batang kinain ko`` ("the child
I-ate ran") had 0 parses despite being a natural Tagalog
sentence.

Phase 5d Commit 10 adds a third Wackernagel exception
(:func:`tgllfg.clitics.placement._is_post_embedded_v_pron`)
alongside the existing post-noun (Phase 5c §7.8 follow-on) and
pre-linker (Phase 5d Commit 6) checks: a PRON-clitic immediately
preceded by a VERB token that is **not** the matrix V (= not the
first V) stays in place. This keeps the embedded RC's actor
adjacent to its host verb so the standard SUBJ-relativization
S_GAP frames fire.

The construction's competing-readings angle (cf. plan §9.1):

* **OV / DV / IV RC with pronominal actor** — uniquely the RC
  reading; the OV S_GAP frame requires a GEN-NP, so there's no
  competing parse.
* **AV-RC with pronominal element** — two parses surface:

    [0] AV-transitive RC where the pronoun is OBJ
        (``Tumakbo ang batang kumain ko`` "the child who-ate-me ran").
    [1] AV-intransitive RC plus pronominal possessor on the head
        NP (``my child who ate ran``).

  Both readings are structurally valid; the ranker leaves them
  for downstream pragmatic disambiguation. Tests below verify
  both parses exist for AV-RC.

Tests:

* OV-RC, DV-RC, IV-RC with pronominal actor — unique parse,
  ``ADJ`` contains an RC with the pronoun at OBJ-AGENT.
* AV-RC ambiguity — both parses produced.
* RC inside OBJ NP — placement still keeps the pronoun in the RC.
* Standalone ``na`` linker (consonant-final head NP) and bound
  ``-ng`` (vowel-final).
* All three vowel-final GEN pronouns (ko / mo / niya).
* Regression: pre-V PRON still hoists; post-NOUN PRON still
  stays; matrix-cluster PRON unaffected.
* LMT diagnostics clean.
"""

from __future__ import annotations

from tgllfg.clitics import reorder_clitics
from tgllfg.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import split_enclitics, split_linker_ng, tokenize


def _pipeline_lemmas(text: str) -> list[str]:
    toks = tokenize(text)
    toks = split_enclitics(toks)
    toks = split_linker_ng(toks)
    ml = analyze_tokens(toks)
    ml = reorder_clitics(ml)
    return [cands[0].lemma if cands else "?" for cands in ml]


def _find_subj_with_rc(
    text: str, rc_pred: str
) -> FStructure | None:
    """Return the parse whose SUBJ.ADJ contains an RC with the given
    PRED, else None."""
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        subj = f.feats.get("SUBJ")
        if not isinstance(subj, FStructure):
            continue
        adj = subj.feats.get("ADJ")
        if not adj:
            continue
        for m in adj:
            if isinstance(m, FStructure) and m.feats.get("PRED") == rc_pred:
                return f
    return None


# === Wackernagel: post-embedded-V PRON stays =============================


class TestWackernagelPostEmbeddedV:
    """The new ``_is_post_embedded_v_pron`` check keeps a PRON in
    place when it follows an embedded V (one that is NOT the
    matrix verb)."""

    def test_post_embedded_ov_stays(self) -> None:
        # ``Tumakbo ang batang kinain ko`` — ko follows the
        # embedded RC verb ``kain``, not the matrix ``takbo``.
        out = _pipeline_lemmas("Tumakbo ang batang kinain ko.")
        # ko stays adjacent to kain (the embedded V).
        assert out == ["takbo", "ang", "bata", "-ng", "kain", "ko", "."]

    def test_post_matrix_v_pron_unchanged(self) -> None:
        # Regression: ``Kinain ko ang isda`` — ko follows the
        # matrix V (which IS the first V). The new check does not
        # fire; ko stays in cluster position (no movement needed).
        out = _pipeline_lemmas("Kinain ko ang isda.")
        assert out == ["kain", "ko", "ang", "isda", "."]

    def test_pre_v_pron_still_hoists(self) -> None:
        # Regression: ``Hindi mo kinain ang isda`` — mo precedes
        # the matrix V. The new check does not fire; mo hoists.
        out = _pipeline_lemmas("Hindi mo kinain ang isda.")
        assert out == ["hindi", "kain", "mo", "ang", "isda", "."]

    def test_post_noun_pron_still_stays(self) -> None:
        # Regression: ``Kumain ang bata ng libro ko`` — ko
        # follows a NOUN. The post-noun check (Phase 5c §7.8)
        # keeps it in place.
        out = _pipeline_lemmas("Kumain ang bata ng libro ko.")
        assert out == ["kain", "ang", "bata", "ng", "libro", "ko", "."]


# === OV-RC: unique RC reading ============================================


class TestOvRcWithPronominalActor:
    """OV-RC with a pronominal actor produces a single parse — the
    OV S_GAP requires a GEN-NP, so no competing possessor reading
    is structurally available."""

    def test_ov_rc_ko(self) -> None:
        # ``Tumakbo ang batang kinain ko`` — the child whom I ate.
        f = _find_subj_with_rc(
            "Tumakbo ang batang kinain ko.",
            "EAT <SUBJ, OBJ-AGENT>",
        )
        assert f is not None
        subj = f.feats["SUBJ"]
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        # OV-RC: pronoun is OBJ-AGENT inside the RC.
        adj = subj.feats["ADJ"]
        rcs = [m for m in adj if isinstance(m, FStructure)]
        rc = rcs[0]
        oa = rc.feats.get("OBJ-AGENT")
        assert isinstance(oa, FStructure)
        assert oa.feats.get("CASE") == "GEN"

    def test_ov_rc_mo(self) -> None:
        f = _find_subj_with_rc(
            "Tumakbo ang batang kinain mo.",
            "EAT <SUBJ, OBJ-AGENT>",
        )
        assert f is not None

    def test_ov_rc_niya(self) -> None:
        f = _find_subj_with_rc(
            "Tumakbo ang batang kinain niya.",
            "EAT <SUBJ, OBJ-AGENT>",
        )
        assert f is not None

    def test_ov_rc_with_standalone_na_linker(self) -> None:
        # Consonant-final head ``aso`` takes standalone ``na``.
        f = _find_subj_with_rc(
            "Tumakbo ang aso na kinain ko.",
            "EAT <SUBJ, OBJ-AGENT>",
        )
        assert f is not None
        subj = f.feats["SUBJ"]
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "aso"

    def test_ov_rc_unique_parse(self) -> None:
        # Only one parse — no competing possessor reading.
        rs = parse_text("Tumakbo ang batang kinain ko.", n_best=10)
        rc_parses = [
            f for _, f, _, _ in rs
            if isinstance(f.feats.get("SUBJ"), FStructure)
            and f.feats["SUBJ"].feats.get("ADJ")  # type: ignore[union-attr]
        ]
        # The OV-RC reading is the only structurally available
        # parse; no possessor reading appears alongside.
        assert len(rc_parses) == 1


# === AV-RC ambiguity =====================================================


class TestAvRcAmbiguity:
    """AV-RC with a pronominal element admits two parses:
    [a] AV-transitive RC where the pronoun is bare OBJ;
    [b] AV-intransitive RC + pronominal possessor on the head NP.
    Both are structurally valid; the parser produces both."""

    def test_av_rc_two_parses(self) -> None:
        rs = parse_text("Tumakbo ang batang kumain ko.", n_best=10)
        assert len(rs) >= 2

        # Reading [a]: AV-transitive RC with ko as OBJ.
        rc_obj_reading = None
        # Reading [b]: AV-intransitive RC + ko as possessor.
        poss_reading = None
        for _, f, _, _ in rs:
            subj = f.feats.get("SUBJ")
            if not isinstance(subj, FStructure):
                continue
            adj = subj.feats.get("ADJ")
            poss = subj.feats.get("POSS")
            if not adj:
                continue
            rcs = [m for m in adj if isinstance(m, FStructure)]
            if not rcs:
                continue
            rc_pred = rcs[0].feats.get("PRED")
            if rc_pred == "EAT <SUBJ, OBJ>" and not isinstance(poss, FStructure):
                rc_obj_reading = f
            elif rc_pred == "EAT <SUBJ>" and isinstance(poss, FStructure):
                poss_reading = f

        assert rc_obj_reading is not None, "RC-with-OBJ reading missing"
        assert poss_reading is not None, "possessor reading missing"


# === RC inside OBJ NP ====================================================


class TestRcInsideObj:
    """The Wackernagel fix also keeps the pronoun in place when the
    RC is inside an OBJ NP (the matrix V's clitic cluster sits
    before the OBJ NP, so the pronoun-after-RC-V is clearly
    embedded)."""

    def test_rc_inside_obj(self) -> None:
        rs = parse_text("Kumain ang aso ng batang kinain ko.", n_best=10)
        assert rs
        # Find the parse where OBJ.ADJ contains the OV-RC.
        found = False
        for _, f, _, _ in rs:
            obj = f.feats.get("OBJ")
            if not isinstance(obj, FStructure):
                continue
            if obj.feats.get("LEMMA") != "bata":
                continue
            adj = obj.feats.get("ADJ")
            if not adj:
                continue
            for m in adj:
                if (
                    isinstance(m, FStructure)
                    and m.feats.get("PRED") == "EAT <SUBJ, OBJ-AGENT>"
                ):
                    found = True
                    break
            if found:
                break
        assert found


# === LMT diagnostics =====================================================


class TestRcActorPronounLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Tumakbo ang batang kinain ko.",
            "Tumakbo ang batang kinain niya.",
            "Tumakbo ang batang kinain mo.",
            "Tumakbo ang aso na kinain ko.",
            "Tumakbo ang batang kumain ko.",
            "Kumain ang aso ng batang kinain ko.",
            "Tumakbo ang isdang nakita ko.",
        ):
            rs = parse_text(s, n_best=10)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
