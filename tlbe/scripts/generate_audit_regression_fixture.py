# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 9.Z: naturalistic-tier regression fixture generator.

Reads existing per-wave parse-results.jsonl files from
``data/tgl/exemplars/``, samples N positive (parse-success-*) cases
proportionally across waves, and emits
``tests/tgllfg/data/audit_regression_fixture.yaml``.

The fixture serves as the canonical regression baseline for
audit-corpus closures: each entry asserts that the named sentence
parses with at least the expected number of trees. The per-sub-PR
test files (test_phase9*.py etc.) test the specific construction a
sub-PR added; this fixture tests that those closures *persist* across
all future churn — a single canonical baseline that survives the
inevitable refactor/delete cycle of per-sub-PR tests.

Re-run after Wave 4+ audits land or after major construction-class
PRs change the audit corpus shape. Uses a fixed seed (42) so
re-runs over identical input produce identical fixture output;
generator is idempotent.

The audit exemplars themselves (``wave*-parse-results.jsonl``) are
gitignored — they're derived from licensed PDFs. This fixture's
checked-in YAML captures the surface text + locator + wave/source
metadata directly, so the regression test runs cleanly on a fresh
clone even without the source corpora present.
"""

import json
import random
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
EXEMPLARS_DIR = REPO_ROOT / "data" / "tgl" / "exemplars"
FIXTURE_PATH = (
    REPO_ROOT / "tests" / "tgllfg" / "data" / "audit_regression_fixture.yaml"
)

# (wave, source-label, parse-results filename) per audit corpus.
# Matches the ``_XWAVE_SOURCES`` list in scripts/harvest_exemplars.py.
WAVE_SOURCES: list[tuple[int, str, str]] = [
    (1, "rg81", "wave1-parse-results.jsonl"),
    (2, "rc1990", "wave2-rc1990-parse-results.jsonl"),
    (2, "rg-int", "wave2-rg-intermediate-parse-results.jsonl"),
    (2, "ramos", "wave2-ramos1971-parse-results.jsonl"),
    (3, "so1972", "wave3-so1972-parse-results.jsonl"),
    (3, "rg-conv", "wave3-rg-conversational-parse-results.jsonl"),
    (4, "kroeger1991", "wave4-kroeger1991-parse-results.jsonl"),
]

TARGET_SAMPLE_TOTAL = 50
SAMPLING_SEED = 42


@dataclass
class _SourceSample:
    wave: int
    source: str
    locator: str
    text: str
    n_parses: int


def _load_positives(path: Path) -> list[dict]:
    """Read a parse-results JSONL file; return records whose bucket
    is ``parse-success-1`` or ``parse-success-N`` (i.e., audit-
    corpus closures, not failure pile)."""
    out: list[dict] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r.get("bucket") in ("parse-success-1", "parse-success-N"):
                out.append(r)
    return out


def _sample_proportionally(
    by_source: dict[tuple[int, str], list[dict]],
    target_total: int,
    rng: random.Random,
) -> list[_SourceSample]:
    """Sample ``target_total`` records distributed proportionally
    across the per-source closure counts. Each source gets at least
    one sample if its closure count is ≥1 (so under-represented
    waves like Wave 1 / Wave 4 still appear). Sample ordering is
    determined by the RNG (fixed seed); output is sorted
    deterministically by wave then locator before YAML emission."""
    sizes = {k: len(v) for k, v in by_source.items()}
    total_pool = sum(sizes.values())
    if total_pool == 0:
        return []

    samples: list[_SourceSample] = []
    for key, recs in by_source.items():
        if not recs:
            continue
        n = max(1, round(len(recs) / total_pool * target_total))
        n = min(n, len(recs))
        for r in rng.sample(recs, n):
            samples.append(_SourceSample(
                wave=key[0],
                source=key[1],
                locator=r["locator"],
                text=r["text"],
                n_parses=r["n_parses"],
            ))
    return samples


def main() -> int:
    by_source: dict[tuple[int, str], list[dict]] = {}
    for wave, src, fname in WAVE_SOURCES:
        path = EXEMPLARS_DIR / fname
        if not path.exists():
            print(f"  (skip {fname}; not found — run 'parse' first)")
            continue
        by_source[(wave, src)] = _load_positives(path)

    rng = random.Random(SAMPLING_SEED)
    samples = _sample_proportionally(
        by_source, TARGET_SAMPLE_TOTAL, rng,
    )
    samples.sort(key=lambda s: (s.wave, s.source, s.locator))

    fixture: dict = {
        "metadata": {
            "phase": "9.Z",
            "sampling_seed": SAMPLING_SEED,
            "target_sample_total": TARGET_SAMPLE_TOTAL,
            "actual_sample_count": len(samples),
            "source": (
                "audit parse-results from "
                "data/tgl/exemplars/wave*-parse-results.jsonl"
            ),
        },
        "samples": [
            {
                "wave": s.wave,
                "source": s.source,
                "locator": s.locator,
                "text": s.text,
                "expected_parses_ge": 1,
            }
            for s in samples
        ],
    }

    FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with FIXTURE_PATH.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(
            fixture, fh,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
        )
    print(
        f"  → {FIXTURE_PATH.relative_to(REPO_ROOT)} "
        f"({len(samples)} samples)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
