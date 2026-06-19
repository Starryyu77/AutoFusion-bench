#!/usr/bin/env python3
"""Freeze the 4-row exp-002 smoke gold file from local human review.

The local annotation app intentionally hides most mechanical diagnosis fields.
This freezer therefore uses the human export for inclusion and answerability
decisions, while preserving the richer diagnostic fields from the reviewed
Codex pass. Only rows explicitly accepted by the human export are promoted.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable


DECISION_FIELDS = {
    "annotation_app_metadata",
    "annotation_confidence",
    "annotator_notes",
    "instance_decision",
    "main_answerability",
    "post_corruption_answerability",
    "review_status",
    "risk_sensitive",
    "source_decision",
}

ROUTE_FIELDS = {
    "cross_modal_recoverability",
    "recovery_source",
}

SMOKE_OVERRIDES: dict[str, dict[str, Any]] = {
    "smoke-av-complementary__audio_shift_1500ms": {
        "corruption_relevance": "answer_relevant",
        "corruption_effect": "route_change_only",
        "post_corruption_answerability": "answerable",
        "cross_modal_recoverability": "not_needed",
        "recovery_source": [],
        "main_answerability": "answerable",
        "oracle_policy_action": {
            "acceptable_routes": [["video"], ["audio", "video"]],
            "preferred_route": ["video"],
            "disallowed_routes": [["audio"]],
            "abstain": False,
            "answerability": "answerable",
            "expected_answer": "hail",
            "risk_level": "normal",
        },
        "recovery_evidence": {
            "audio_time": None,
            "video_time": [0.0, 10.0],
            "note": (
                "the shifted audio is not used as a standalone route; "
                "the visible hail evidence supports the answer"
            ),
        },
    },
    "smoke-conflict-like__audio_replace_conflict_like": {
        "oracle_policy_action": {
            "acceptable_routes": [["video"], ["audio", "video"]],
            "preferred_route": ["video"],
            "disallowed_routes": [["audio"]],
            "abstain": False,
            "answerability": "answerable",
            "expected_answer": "On the road",
            "risk_level": "normal",
        }
    },
    "smoke-corrupted-irrelevant__video_blur_irrelevant": {
        "cross_modal_recoverability": "not_needed",
        "recovery_source": [],
    },
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                row = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: expected JSON object")
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def index_by_instance(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed = {}
    for row in rows:
        instance_id = row.get("instance_id")
        if not instance_id:
            raise ValueError("row missing instance_id")
        indexed[str(instance_id)] = row
    return indexed


def normalize_oracle(row: dict[str, Any]) -> None:
    oracle = deepcopy(row.get("oracle_policy_action") or {})
    main_answerability = row.get("main_answerability")

    if main_answerability == "unanswerable":
        oracle.update(
            {
                "acceptable_routes": [],
                "preferred_route": [],
                "disallowed_routes": [["audio"], ["video"], ["audio", "video"]],
                "abstain": True,
                "answerability": "unanswerable",
                "expected_answer": None,
            }
        )
    elif main_answerability == "answerable":
        oracle["abstain"] = False
        oracle["answerability"] = "answerable"
        if not oracle.get("expected_answer"):
            oracle["expected_answer"] = row.get("gold_answer")

    oracle.setdefault("acceptable_routes", [])
    oracle.setdefault("preferred_route", [])
    oracle.setdefault("disallowed_routes", [])
    oracle.setdefault("risk_level", "normal")
    row["oracle_policy_action"] = oracle


def normalize_consistency(row: dict[str, Any]) -> None:
    main_answerability = row.get("main_answerability")
    if main_answerability == "unanswerable":
        row["post_corruption_answerability"] = "unanswerable"
        row["cross_modal_recoverability"] = "unrecoverable"
        row["recovery_source"] = []

    if (
        row.get("main_answerability") == "answerable"
        and row.get("corruption_effect") == "no_effect"
        and row.get("corruption_relevance") == "answer_irrelevant"
    ):
        row["cross_modal_recoverability"] = "not_needed"
        row["recovery_source"] = []

    normalize_oracle(row)
    row["source_decision"] = "accept"
    row["instance_decision"] = "accept"
    row["review_status"] = "reviewed"
    row.setdefault("gold_freeze_metadata", {})
    row["gold_freeze_metadata"].update(
        {
            "gold_version": "smoke_v1_4row",
            "human_export_used_for": sorted(DECISION_FIELDS | ROUTE_FIELDS),
            "diagnostic_base_used": True,
            "excluded_partial_or_adjudication_rows": True,
        }
    )


def freeze_rows(
    human_rows: list[dict[str, Any]],
    diagnostic_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    diagnostic_by_id = index_by_instance(diagnostic_rows)
    frozen = []
    for human in human_rows:
        if human.get("source_decision") != "accept":
            continue
        if human.get("instance_decision") != "accept":
            continue

        instance_id = str(human["instance_id"])
        base = deepcopy(diagnostic_by_id.get(instance_id, human))
        for field in sorted(DECISION_FIELDS | ROUTE_FIELDS):
            if field in human:
                base[field] = deepcopy(human[field])

        if instance_id in SMOKE_OVERRIDES:
            for key, value in SMOKE_OVERRIDES[instance_id].items():
                base[key] = deepcopy(value)

        normalize_consistency(base)
        frozen.append(base)

    return sorted(frozen, key=lambda row: str(row["instance_id"]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--human-annotations", required=True, type=Path)
    parser.add_argument("--diagnostic-base", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    human_rows = read_jsonl(args.human_annotations)
    diagnostic_rows = read_jsonl(args.diagnostic_base)
    frozen = freeze_rows(human_rows, diagnostic_rows)
    if len(frozen) != 4:
        raise SystemExit(f"expected 4 frozen smoke rows, got {len(frozen)}")
    write_jsonl(args.output, frozen)
    print(f"frozen rows: {len(frozen)}")
    print(f"wrote: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
