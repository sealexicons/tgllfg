# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-12.15: exemplar ``ignore`` schema + default-skip
serialization.

Regression guard for the curator-level skip mechanism that handles
PAG-AARAL/sent-12 (``Kahit a la 'ako Tarzan, ikaw Jane'.``) — the
Tarzan/Jane clichéd code-switch quotation that R&G 1981 cites as a
"broken-language" rhetorical example. The audit pipeline filters
``ignore: true`` exemplars out of both the totals and the regression-
gate so curated meta-out-of-scope sentences don't affect coverage
metrics.

Two coordinated changes in this slice:

* ``scripts/harvest_exemplars.py``:
  - ``Exemplar`` dataclass extended with optional ``ignore: bool =
    False`` + ``ignore_reason: str | None = None`` fields.
  - ``_IGNORED_EXEMPLARS`` registry maps ``(source, locator)`` to a
    short reason string; applied at extract-time.
  - ``_asdict_drop_defaults`` serializer skips optional fields whose
    value equals the dataclass default — keeps wave-N .jsonl files
    free of redundant ``"ignore": false, "ignore_reason": null`` on
    every non-ignored record.

* ``tgllfg.audit.load_tasks`` (Phase 12.F; formerly
  ``scripts/audit_corpus.py:_load_tasks``):
  - filters ``ex.get("ignore")`` (parallel to the existing
    ``marked_ungrammatical`` filter), so ignored entries don't reach
    the parser pool and don't appear in ``parse-results.jsonl``.
"""

import json
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(_SCRIPTS_DIR))

import harvest_exemplars as he  # type: ignore[import-not-found]  # noqa: E402


class TestExemplarSchemaIgnoreFields:
    """The ``Exemplar`` dataclass exposes ``ignore`` + ``ignore_reason``
    as optional fields defaulting to ``False`` / ``None``."""

    def test_default_ignore_is_false(self) -> None:
        ex = he.Exemplar(
            source="x", locator="x/1",
            text_raw="X", text_normalized="X",
            has_gloss=False, gloss_en=None,
            marked_ungrammatical=False,
            ocr_quality="transcription",
        )
        assert ex.ignore is False
        assert ex.ignore_reason is None

    def test_explicit_ignore_overrides_default(self) -> None:
        ex = he.Exemplar(
            source="x", locator="x/1",
            text_raw="X", text_normalized="X",
            has_gloss=False, gloss_en=None,
            marked_ungrammatical=False,
            ocr_quality="transcription",
            ignore=True,
            ignore_reason="test reason",
        )
        assert ex.ignore is True
        assert ex.ignore_reason == "test reason"


class TestIgnoreOverridesRegistry:
    """``_IGNORED_EXEMPLARS`` maps ``(source, locator) → reason`` and
    is applied at extract time via ``_apply_ignore_overrides``."""

    def test_panahon_sent_12_in_registry(self) -> None:
        """The PAG-AARAL/sent-12 Tarzan/Jane cliché is registered."""
        key = (
            "rg81/transcriptions",
            "ANG PAG-AARAL NG ISANG WIKA/sent-12",
        )
        assert key in he._IGNORED_EXEMPLARS
        # Reason mentions both 'code-switch' and 'cliché' for
        # findability via grep on future curator decisions.
        reason = he._IGNORED_EXEMPLARS[key]
        assert "code-switch" in reason
        assert "cliché" in reason

    def test_apply_ignore_overrides_matched(self) -> None:
        ex = he.Exemplar(
            source="rg81/transcriptions",
            locator="ANG PAG-AARAL NG ISANG WIKA/sent-12",
            text_raw="Kahit a la 'ako Tarzan, ikaw Jane'.",
            text_normalized="Kahit a la 'ako Tarzan, ikaw Jane'.",
            has_gloss=False, gloss_en=None,
            marked_ungrammatical=False,
            ocr_quality="transcription",
        )
        out = he._apply_ignore_overrides(ex)
        assert out.ignore is True
        assert out.ignore_reason is not None
        assert "code-switch" in out.ignore_reason

    def test_apply_ignore_overrides_unmatched_is_noop(self) -> None:
        ex = he.Exemplar(
            source="rg81/transcriptions",
            locator="ANG MANOK/sent-1",
            text_raw="X", text_normalized="X",
            has_gloss=False, gloss_en=None,
            marked_ungrammatical=False,
            ocr_quality="transcription",
        )
        out = he._apply_ignore_overrides(ex)
        assert out.ignore is False
        assert out.ignore_reason is None


class TestAsdictDropDefaults:
    """``_asdict_drop_defaults`` drops fields whose value equals the
    dataclass-declared default (preserving required fields and
    non-default optional fields)."""

    def test_default_optional_fields_dropped(self) -> None:
        ex = he.Exemplar(
            source="x", locator="x/1",
            text_raw="X", text_normalized="X",
            has_gloss=False, gloss_en=None,
            marked_ungrammatical=False,
            ocr_quality="transcription",
        )
        d = he._asdict_drop_defaults(ex)
        # Required fields present
        assert "source" in d
        assert "locator" in d
        assert "marked_ungrammatical" in d  # required, no default
        # Optional fields with default values OMITTED
        assert "ignore" not in d
        assert "ignore_reason" not in d

    def test_non_default_optional_fields_kept(self) -> None:
        ex = he.Exemplar(
            source="x", locator="x/1",
            text_raw="X", text_normalized="X",
            has_gloss=False, gloss_en=None,
            marked_ungrammatical=False,
            ocr_quality="transcription",
            ignore=True,
            ignore_reason="reason",
        )
        d = he._asdict_drop_defaults(ex)
        assert d["ignore"] is True
        assert d["ignore_reason"] == "reason"

    def test_parse_record_default_factory_fields_dropped(self) -> None:
        """``ParseRecord`` has list/dict ``default_factory`` fields —
        the helper compares against a fresh factory call."""
        rec = he.ParseRecord(
            locator="x", text="X",
            bucket="parse-success-1",
            n_parses=1, n_fragments=0,
            # oov_tokens / diag_summary / diag_kinds / latency_s
            # take their default-factory / default values.
        )
        d = he._asdict_drop_defaults(rec)
        # Required fields present
        assert d["bucket"] == "parse-success-1"
        assert d["n_parses"] == 1
        # default values OMITTED
        assert "oov_tokens" not in d         # default_factory=list
        assert "diag_summary" not in d        # default=""
        assert "diag_kinds" not in d          # default_factory=dict
        assert "latency_s" not in d           # default=0.0

    def test_parse_record_non_default_fields_kept(self) -> None:
        rec = he.ParseRecord(
            locator="x", text="X",
            bucket="zero-parse-fragment",
            n_parses=0, n_fragments=3,
            oov_tokens=["foo"],
            diag_summary="bar",
            diag_kinds={"constraint-failed": 1},
            latency_s=0.5,
        )
        d = he._asdict_drop_defaults(rec)
        assert d["oov_tokens"] == ["foo"]
        assert d["diag_summary"] == "bar"
        assert d["diag_kinds"] == {"constraint-failed": 1}
        assert d["latency_s"] == 0.5


class TestAuditCorpusLoadTasksFilter:
    """``tgllfg.audit.load_tasks`` filters out ``ignore: true`` entries
    (parallel to ``marked_ungrammatical`` filtering). Phase 12.F moved
    this from ``scripts/audit_corpus.py:_load_tasks``."""

    def test_ignored_entry_filtered_from_tasks(self, tmp_path) -> None:
        # Phase 12.F moved the audit logic into ``tgllfg.audit``;
        # ``load_tasks`` now takes the corpus dir as an argument (no
        # module-global ``EXEMPLARS`` / ``WAVE_FILES`` to patch).
        from tgllfg.audit import load_tasks

        # Build a 3-entry .jsonl: 1 normal, 1 marked_ungrammatical,
        # 1 ignore=true. Verify only the normal one reaches the task
        # list.
        rec_normal = {
            "source": "s",
            "locator": "loc-normal",
            "text_normalized": "Normal sentence.",
        }
        rec_ungrammatical = {
            "source": "s",
            "locator": "loc-ungram",
            "text_normalized": "*Ungrammatical.",
            "marked_ungrammatical": True,
        }
        rec_ignored = {
            "source": "s",
            "locator": "loc-ignored",
            "text_normalized": "Curator-skipped.",
            "ignore": True,
            "ignore_reason": "test",
        }

        # ``load_tasks`` reads ``<wave>.jsonl`` from the given dir; name
        # the fixture after a real wave id and filter to it.
        wave_path = tmp_path / "wave1-exemplars.jsonl"
        with wave_path.open("w") as f:
            for r in (rec_normal, rec_ungrammatical, rec_ignored):
                f.write(json.dumps(r) + "\n")

        tasks = load_tasks(tmp_path, wave_filter={"wave1-exemplars"})

        # Only the normal one survives (ungrammatical + ignored dropped).
        assert len(tasks) == 1
        assert tasks[0][2] == "loc-normal"
