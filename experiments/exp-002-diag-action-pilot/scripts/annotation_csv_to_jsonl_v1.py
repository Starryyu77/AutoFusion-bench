#!/usr/bin/env python3
"""Convert a filled v1 annotation CSV into scorer-ready JSONL."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


HEADLINE_FIELDS = [
    "modality_quality_audio",
    "modality_quality_video",
    "modality_task_relevance_audio",
    "modality_task_relevance_video",
    "cross_modal_relation",
    "corruption_relevance",
    "corruption_effect",
    "post_corruption_answerability",
    "cross_modal_recoverability",
    "main_answerability",
]

HEADLINE_ANSWERABILITY = {"answerable", "unanswerable"}
HEADLINE_CONFIDENCE = {"high", "medium"}


def read_jsonl(path: Path) -> dict[str, dict[str, Any]]:
    rows = {}
    if not path:
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                row = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            rows[str(row["instance_id"])] = row
    return rows


def parse_json_cell(value: str, field: str, row_number: int) -> Any:
    value = (value or "").strip()
    if value == "":
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"row {row_number}: {field} is not valid JSON: {exc}") from exc


def parse_bool(value: str, field: str, row_number: int) -> bool:
    lowered = (value or "").strip().lower()
    if lowered in {"true", "yes", "1"}:
        return True
    if lowered in {"false", "no", "0", ""}:
        return False
    raise ValueError(f"row {row_number}: {field} must be true/false, got {value!r}")


def clean(value: str | None) -> str:
    return (value or "").strip()


def derive_instance_decision(annotation: dict[str, Any]) -> str:
    review_status = annotation.get("review_status")
    if review_status in {"accept", "reject", "adjudicate"}:
        return review_status

    source_decision = annotation.get("source_decision", "adjudicate")
    if source_decision == "reject":
        return "reject"
    if source_decision != "accept":
        return "adjudicate"
    if review_status == "rejected":
        return "reject"
    if review_status != "reviewed":
        return "adjudicate"
    main_answerability = annotation.get("main_answerability")
    if main_answerability not in HEADLINE_ANSWERABILITY:
        return "reject"
    if annotation.get("annotation_confidence") not in HEADLINE_CONFIDENCE:
        return "adjudicate"
    if annotation.get("risk_sensitive") is True:
        return "adjudicate"
    post_answerability = annotation.get("post_corruption_answerability")
    if main_answerability == "answerable" and post_answerability != "answerable":
        return "adjudicate"
    if main_answerability == "unanswerable" and post_answerability != "unanswerable":
        return "adjudicate"
    oracle = annotation.get("oracle_policy_action") or {}
    acceptable_routes = oracle.get("acceptable_routes") or []
    preferred_route = oracle.get("preferred_route") or []
    if main_answerability == "answerable" and not acceptable_routes:
        return "adjudicate"
    if main_answerability == "unanswerable":
        if oracle.get("abstain") is not True:
            return "adjudicate"
        if acceptable_routes or preferred_route:
            return "adjudicate"
    return "accept"


def normalize_oracle_policy(annotation: dict[str, Any]) -> dict[str, Any]:
    oracle = annotation.setdefault("oracle_policy_action", {})
    main_answerability = annotation.get("main_answerability")
    post_answerability = annotation.get("post_corruption_answerability")
    if main_answerability == "unanswerable" and oracle.get("abstain") is True:
        oracle["answerability"] = "unanswerable"
        oracle["expected_answer"] = None
    elif main_answerability == "answerable" and post_answerability == "answerable":
        oracle["answerability"] = "answerable"
    return annotation


def row_to_annotation(
    row: dict[str, str],
    base: dict[str, Any] | None,
    row_number: int,
) -> dict[str, Any]:
    base = base or {}
    review_status = clean(row.get("review_status")) or base.get("review_status", "needs_human_review")
    choices = parse_json_cell(row.get("choices_json", ""), "choices_json", row_number)
    recovery_source = parse_json_cell(
        row.get("recovery_source_json", ""), "recovery_source_json", row_number
    )
    recovery_audio_time = parse_json_cell(
        row.get("recovery_audio_time_json", ""), "recovery_audio_time_json", row_number
    )
    recovery_video_time = parse_json_cell(
        row.get("recovery_video_time_json", ""), "recovery_video_time_json", row_number
    )
    acceptable_routes = parse_json_cell(
        row.get("acceptable_routes_json", ""), "acceptable_routes_json", row_number
    )
    preferred_route = parse_json_cell(
        row.get("preferred_route_json", ""), "preferred_route_json", row_number
    )
    disallowed_routes = parse_json_cell(
        row.get("disallowed_routes_json", ""), "disallowed_routes_json", row_number
    )

    annotation = {
        "instance_id": clean(row.get("instance_id")),
        "source_id": clean(row.get("source_id")),
        "source_dataset": clean(row.get("source_dataset")),
        "question": clean(row.get("question")),
        "choices": choices if choices is not None else base.get("choices", []),
        "modalities_presented": base.get("modalities_presented", ["audio", "video"]),
        "gold_answer": clean(row.get("gold_answer")) or None,
        "review_status": review_status,
        "source_decision": clean(row.get("source_decision")) or base.get("source_decision", "adjudicate"),
        "question_only_blind": {
            "answerable_without_media": clean(
                row.get("question_only_answerable_without_media")
            ),
            "blind_confidence": clean(row.get("question_only_blind_confidence")),
            "blind_answer": clean(row.get("question_only_blind_answer")),
        },
        "source_modality_necessity": {
            "audio": clean(row.get("source_audio_relevance")),
            "video": clean(row.get("source_video_relevance")),
            "audio_video_joint_required": clean(row.get("source_audio_video_joint_required")),
        },
        "source_evidence_note": clean(row.get("source_evidence_note")),
        "generator_hint": base.get(
            "generator_hint",
            {
                "affected_modality": clean(row.get("generator_affected_modality")),
                "corruption_type": clean(row.get("generator_corruption_type")),
                "severity": clean(row.get("generator_severity")),
                "corruption_relevance": clean(row.get("generator_corruption_relevance")),
            },
        ),
        "media": base.get(
            "media",
            {
                "source_video_path": clean(row.get("source_video_path")),
                "corrupted_video_path": clean(row.get("corrupted_video_path")),
            },
        ),
        "modality_quality_status": {
            "audio": clean(row.get("modality_quality_audio")),
            "video": clean(row.get("modality_quality_video")),
        },
        "modality_task_relevance": {
            "audio": clean(row.get("modality_task_relevance_audio")),
            "video": clean(row.get("modality_task_relevance_video")),
        },
        "cross_modal_relation": clean(row.get("cross_modal_relation")),
        "defect_location": base.get(
            "defect_location",
            {"text_span": None, "audio_time": None, "video_time": None, "frame_range": None},
        ),
        "corruption_relevance": clean(row.get("corruption_relevance")),
        "corruption_effect": clean(row.get("corruption_effect")),
        "post_corruption_answerability": clean(row.get("post_corruption_answerability")),
        "cross_modal_recoverability": clean(row.get("cross_modal_recoverability")),
        "main_answerability": clean(row.get("main_answerability")),
        "risk_sensitive": parse_bool(row.get("risk_sensitive", ""), "risk_sensitive", row_number),
        "recovery_source": recovery_source or [],
        "recovery_evidence": {
            "audio_time": recovery_audio_time,
            "video_time": recovery_video_time,
            "note": clean(row.get("recovery_note")),
        },
        "oracle_policy_action": {
            "acceptable_routes": acceptable_routes or [],
            "preferred_route": preferred_route or [],
            "disallowed_routes": disallowed_routes or [],
            "abstain": parse_bool(row.get("oracle_abstain", ""), "oracle_abstain", row_number),
            "answerability": clean(row.get("oracle_answerability")),
            "expected_answer": clean(row.get("oracle_expected_answer")) or None,
            "risk_level": clean(row.get("oracle_risk_level")),
        },
        "annotation_confidence": clean(row.get("annotation_confidence")),
        "annotator_notes": clean(row.get("annotator_notes")),
    }
    annotation = normalize_oracle_policy(annotation)
    annotation["instance_decision"] = derive_instance_decision(annotation)
    return annotation


def strict_errors(annotation: dict[str, Any], row_number: int) -> list[str]:
    errors = []
    prefix = f"row {row_number} ({annotation.get('instance_id')}):"
    if annotation["review_status"] == "needs_human_review":
        errors.append(f"{prefix} review_status is still needs_human_review")
    if annotation.get("instance_decision") == "accept":
        if annotation.get("source_decision") != "accept":
            errors.append(f"{prefix} accepted row must have source_decision=accept")
        for field in HEADLINE_FIELDS:
            if field == "modality_quality_audio":
                value = annotation["modality_quality_status"]["audio"]
            elif field == "modality_quality_video":
                value = annotation["modality_quality_status"]["video"]
            elif field == "modality_task_relevance_audio":
                value = annotation["modality_task_relevance"]["audio"]
            elif field == "modality_task_relevance_video":
                value = annotation["modality_task_relevance"]["video"]
            else:
                value = annotation.get(field)
            if value in {"", "unclear"}:
                errors.append(f"{prefix} accepted row has unresolved {field}")
        if annotation["main_answerability"] == "answerable":
            routes = annotation["oracle_policy_action"]["acceptable_routes"]
            if not routes:
                errors.append(f"{prefix} answerable row must have acceptable routes")
        if annotation["main_answerability"] == "unanswerable":
            if not annotation["oracle_policy_action"]["abstain"]:
                errors.append(f"{prefix} unanswerable row must set oracle_abstain=true")
    return errors


def convert(args: argparse.Namespace) -> int:
    base_rows = read_jsonl(args.base_jsonl) if args.base_jsonl else {}
    annotations = []
    errors = []

    with args.input_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row_number, row in enumerate(reader, start=2):
            try:
                instance_id = clean(row.get("instance_id"))
                annotation = row_to_annotation(row, base_rows.get(instance_id), row_number)
                if args.strict_gold:
                    errors.extend(strict_errors(annotation, row_number))
                annotations.append(annotation)
            except ValueError as exc:
                errors.append(str(exc))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with args.output_jsonl.open("w", encoding="utf-8") as handle:
        for annotation in annotations:
            handle.write(json.dumps(annotation, ensure_ascii=False) + "\n")
    print(f"wrote {len(annotations)} rows: {args.output_jsonl}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", required=True, type=Path)
    parser.add_argument("--output-jsonl", required=True, type=Path)
    parser.add_argument("--base-jsonl", type=Path)
    parser.add_argument(
        "--strict-gold",
        action="store_true",
        help="Fail if rows still contain unresolved labels for accepted gold rows.",
    )
    return convert(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
