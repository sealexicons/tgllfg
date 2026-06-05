# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-7.5: ``tungo sa`` GOAL-PP head fronting +
clause-final + post-half closures.

Adds:

1. ``tungo`` PREP lemma routes through the fronted-PP-comma split.
   ``_FRONTED_PP_LEMMA_TYPES`` (post-7.4) extended with
   ``tungo → GOAL``. Existing rows: ``dahil`` / ``dahilan`` → REASON
   (post-2 / post-7.2); ``mula`` → SOURCE (post-7.4).

2. ``S → PP[PREP_TYPE=GOAL] PUNCT[PUNCT_CLASS=COMMA] S`` chart
   rule added to the 9.X.c13 fronted-PP-comma loop in discourse.py
   (which previously covered REASON + SOURCE). Mirrors the existing
   variants — fronted PP becomes matrix TOPIC + ADJ-set member.
   ``tungo``'s polysemy (NOUN "destination" + PREP[PREP_TYPE=GOAL])
   is disambiguated at the PP-build site (extraction.py): the GOAL
   PP requires a sa-NP complement, which the bare-NOUN reading
   can't satisfy.

3. Lex extensions for the inner-clause vocabulary in the post-7.5
   constructed exemplars:

   - ``maneho`` VERB gains ``feats: {AV_ABSOL: true}`` so
     ``Nagmaneho si Pedro.`` "Pedro drove [a vehicle, implicit]"
     parses without an overt OBJ. Pragmatically natural Filipino
     motion-verb usage; parallel to the AV_ABSOL on ``luto`` /
     ``trabaho`` / ``hirap``.
   - ``hangganan`` NOUN ("border, boundary, frontier"). Standard
     Filipino noun used in S&O / R&G adjunct narratives.

The clause-final ``S → S PP[PREP_TYPE=GOAL]`` rule was already in
place (added 9.X.c29 ahead of post-7.5).

Closes all 4 ``pending_closure: post-7.5`` constructed exemplars
(``tungo-sa/paaralan``, ``tungo-sa/hangganan-bayan``,
``tungo-sa/malayong-bayan``, ``tungo-sa/paaralan-postv``).
"""

from tgllfg.core.pipeline import parse_text


class TestTungoSaPp:
    """post-7.5: ``tungo sa`` GOAL-PP fronted + clause-final + glue."""

    def test_tungo_sa_paaralan_fronted(self) -> None:
        """Canonical GOAL-PP fronting closure."""
        s = "Tungo sa paaralan, naglakad ang mga bata."
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        topic = fs.feats.get("TOPIC")
        assert topic is not None, "expected TOPIC on matrix"
        assert topic.feats.get("PREP_TYPE") == "GOAL", (
            f"expected PREP_TYPE=GOAL on TOPIC, got "
            f"{topic.feats.get('PREP_TYPE')}"
        )

    def test_tungo_sa_hangganan_fronted(self) -> None:
        """GOAL-PP with possessive-NP inside (``hangganan ng bayan``).
        Exercises the post-7.5 ``hangganan`` NOUN add + ``maneho``
        ``AV_ABSOL: true`` feat."""
        s = "Tungo sa hangganan ng bayan, nagmaneho si Pedro."
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1

    def test_tungo_sa_malayong_bayan_fronted(self) -> None:
        """GOAL-PP with ADJ-LINK-N modifier inside (``malayong
        bayan`` "distant town")."""
        s = "Tungo sa malayong bayan, tumakbo ang kabayo."
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        topic = fs.feats.get("TOPIC")
        assert topic is not None
        assert topic.feats.get("PREP_TYPE") == "GOAL"

    def test_tungo_sa_paaralan_clause_final(self) -> None:
        """Clause-final ``tungo sa paaralan`` — exercises the
        9.X.c29 GOAL clause-final S→S PP rule (pre-existing)."""
        s = "Naglakad ang mga bata tungo sa paaralan."
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        adjunct = fs.feats.get("ADJUNCT")
        assert adjunct is not None, "expected ADJUNCT on matrix"


class TestNewLex:
    """post-7.5: lex coverage for the constructed exemplars."""

    def test_maneho_av_absol(self) -> None:
        """``maneho`` VERB gains AV_ABSOL=true so ``Nagmaneho si
        Pedro.`` parses without an overt OBJ. Without the flag the
        AV form's TR=TR root transitivity would demand a GEN-OBJ."""
        parses = parse_text("Nagmaneho si Pedro.", n_best=2)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        assert fs.feats.get("VOICE") == "AV"

    def test_maneho_with_obj_unchanged(self) -> None:
        """Anti-regression: ``Nagmaneho si Pedro ng kotse.`` (with
        explicit OBJ) still parses — AV_ABSOL=true is the
        absolutive-licensing flag, not a constraint."""
        parses = parse_text("Nagmaneho si Pedro ng kotse.", n_best=2)
        assert len(parses) >= 1

    def test_hangganan_noun(self) -> None:
        """``hangganan`` NOUN admits ``ang hangganan`` SUBJ."""
        parses = parse_text("Malayo ang hangganan.", n_best=2)
        assert len(parses) >= 1


class TestAntiRegression:
    """post-7.5 anti-regression: the GOAL addition doesn't break
    existing fronted-PP-comma constructions."""

    def test_dahil_fronted_reason_unchanged(self) -> None:
        """REASON fronted-PP still closes (post-2)."""
        parses = parse_text(
            "Dahil sa init ng araw, panay ang tulo ng pawis ng tao.",
            n_best=2,
        )
        assert len(parses) >= 1

    def test_mula_fronted_source_unchanged(self) -> None:
        """SOURCE fronted-PP (post-7.4) still closes."""
        parses = parse_text(
            "Mula sa Maynila, naglakbay kami sa Cebu.",
            n_best=2,
        )
        assert len(parses) >= 1

    def test_tungo_noun_reading_unchanged(self) -> None:
        """``tungo`` polysemy: NOUN ("destination") reading still
        available — the post-7.5 PREP-as-GOAL routing through the
        fronted-PP-comma split only fires on the
        ``tungo + sa + NP`` shape; bare ``ang tungo`` etc. still
        routes to the NOUN reading."""
        # Bare NOUN reading: 'tungo' = "direction, destination"
        # appears in S&O 1972 sentences like 'Ang tungo ay malayo.'
        parses = parse_text("Malayo ang tungo.", n_best=2)
        assert len(parses) >= 1
