from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py"


def run_validator(kind: str, path: str) -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--kind", kind, path],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_exp002_smoke_source_items_contract() -> None:
    run_validator(
        "source-items",
        "experiments/exp-002-diag-action-pilot/data/smoke_source_items.jsonl",
    )


def test_exp002_smoke_corruption_manifest_contract() -> None:
    run_validator(
        "corruption-manifest",
        "experiments/exp-002-diag-action-pilot/data/smoke_corruption_manifest.jsonl",
    )


def test_exp002_smoke_gold_annotation_contract() -> None:
    run_validator(
        "annotations",
        "experiments/exp-002-diag-action-pilot/annotations/smoke_annotations_v1.gold.jsonl",
    )
