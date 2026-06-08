#!/usr/bin/env python3
"""Validate exp-002 JSONL files for required top-level fields."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable


REQUIRED_FIELDS = {
    "source-items": {
        "source_id",
        "source_dataset",
        "video_path",
        "question",
        "gold_answer",
        "modality_necessity",
        "bucket",
    },
    "corruption-manifest": {
        "instance_id",
        "source_id",
        "affected_modality",
        "corruption_type",
        "severity",
        "location",
        "corruption_relevance",
        "generator_family",
        "seed",
    },
    "annotations": {
        "instance_id",
        "source_dataset",
        "question",
        "modalities_presented",
        "gold_answer",
        "source_modality_necessity",
        "question_only_blind",
        "modality_quality_status",
        "modality_task_relevance",
        "cross_modal_relation",
        "defect_location",
        "corruption_relevance",
        "corruption_effect",
        "post_corruption_answerability",
        "cross_modal_recoverability",
        "main_answerability",
        "recovery_source",
        "recovery_evidence",
        "oracle_policy_action",
        "annotation_confidence",
    },
    "model-diagnoses": {
        "instance_id",
        "model",
        "modality_quality_status",
        "modality_task_relevance",
        "cross_modal_relation",
        "corruption_relevance",
        "corruption_effect",
        "post_corruption_answerability",
        "cross_modal_recoverability",
        "recovery_source",
        "recovery_evidence",
        "confidence",
    },
    "model-actions": {
        "instance_id",
        "model",
        "diagnosis_source_id",
        "selected_route",
        "abstain",
        "answer",
        "confidence",
        "risk_policy",
        "action_rationale",
    },
}


def iter_jsonl(path: Path) -> Iterable[tuple[int, dict]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: expected object")
            yield line_number, value


def validate(path: Path, kind: str) -> list[str]:
    required = REQUIRED_FIELDS[kind]
    errors: list[str] = []
    rows = 0
    for line_number, row in iter_jsonl(path):
        rows += 1
        missing = sorted(required - set(row))
        if missing:
            errors.append(f"{path}:{line_number}: missing {', '.join(missing)}")
    if rows == 0:
        errors.append(f"{path}: empty JSONL")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--kind", choices=sorted(REQUIRED_FIELDS), required=True)
    args = parser.parse_args()

    if not args.path.exists():
        print(f"{args.path}: file not found", file=sys.stderr)
        return 2

    try:
        errors = validate(args.path, args.kind)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"ok: {args.path} ({args.kind})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
