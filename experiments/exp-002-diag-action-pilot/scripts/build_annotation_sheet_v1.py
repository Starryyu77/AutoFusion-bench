#!/usr/bin/env python3
"""Build a v1 human annotation sheet from source and corruption manifests."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Iterable


CSV_COLUMNS = [
    "review_status",
    "source_decision",
    "instance_id",
    "source_id",
    "source_dataset",
    "video_id",
    "video_name",
    "source_video_path",
    "corrupted_video_path",
    "question",
    "choices_json",
    "gold_answer",
    "question_relation",
    "question_type",
    "source_bucket",
    "generator_affected_modality",
    "generator_corruption_type",
    "generator_severity",
    "generator_corruption_relevance",
    "question_only_answerable_without_media",
    "question_only_blind_confidence",
    "question_only_blind_answer",
    "source_audio_relevance",
    "source_video_relevance",
    "source_audio_video_joint_required",
    "source_evidence_note",
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
    "risk_sensitive",
    "recovery_source_json",
    "recovery_audio_time_json",
    "recovery_video_time_json",
    "recovery_note",
    "acceptable_routes_json",
    "preferred_route_json",
    "disallowed_routes_json",
    "oracle_abstain",
    "oracle_answerability",
    "oracle_expected_answer",
    "oracle_risk_level",
    "annotation_confidence",
    "annotator_notes",
]


def read_jsonl(path: Path) -> list[dict]:
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
                raise ValueError(f"{path}:{line_number}: expected object")
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in CSV_COLUMNS})


def source_relevance_hint(source: dict, modality: str) -> str:
    necessity = source.get("modality_necessity", {})
    if necessity.get("audio_video_joint_required") is True:
        return "necessary"
    if modality == "audio" and necessity.get("audio_sufficient") is True:
        return "sufficient"
    if modality == "video" and necessity.get("video_sufficient") is True:
        return "sufficient"
    return "unclear"


def joint_required_hint(source: dict) -> str:
    value = source.get("modality_necessity", {}).get("audio_video_joint_required")
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return "unclear"


def build_annotation_row(source: dict, corruption: dict) -> dict:
    return {
        "instance_id": corruption["instance_id"],
        "source_id": source["source_id"],
        "source_dataset": source.get("source_dataset", ""),
        "question": source.get("question", ""),
        "choices": source.get("choices", []),
        "modalities_presented": ["audio", "video"],
        "gold_answer": source.get("gold_answer"),
        "review_status": "needs_human_review",
        "source_decision": "adjudicate",
        "question_only_blind": {
            "answerable_without_media": "unclear",
            "blind_confidence": "low",
            "blind_answer": "",
        },
        "source_modality_necessity": {
            "audio": source_relevance_hint(source, "audio"),
            "video": source_relevance_hint(source, "video"),
            "audio_video_joint_required": joint_required_hint(source),
        },
        "source_evidence_note": "",
        "generator_hint": {
            "affected_modality": corruption.get("affected_modality"),
            "corruption_type": corruption.get("corruption_type"),
            "severity": corruption.get("severity"),
            "location": corruption.get("location"),
            "corruption_relevance": corruption.get("corruption_relevance"),
            "generator_family": corruption.get("generator_family"),
            "seed": corruption.get("seed"),
        },
        "media": {
            "source_video_path": corruption.get("source_video_path") or source.get("video_path"),
            "corrupted_video_path": corruption.get("corrupted_video_path"),
        },
        "modality_quality_status": {
            "audio": "unclear",
            "video": "unclear",
        },
        "modality_task_relevance": {
            "audio": "unclear",
            "video": "unclear",
        },
        "cross_modal_relation": "unclear",
        "defect_location": corruption.get(
            "location",
            {"text_span": None, "audio_time": None, "video_time": None, "frame_range": None},
        ),
        "corruption_relevance": "unclear",
        "corruption_effect": "unclear",
        "post_corruption_answerability": "unclear",
        "cross_modal_recoverability": "unclear",
        "main_answerability": "exclude_from_main",
        "risk_sensitive": True,
        "recovery_source": [],
        "recovery_evidence": {
            "audio_time": None,
            "video_time": None,
            "note": "",
        },
        "oracle_policy_action": {
            "acceptable_routes": [],
            "preferred_route": [],
            "disallowed_routes": [],
            "abstain": False,
            "answerability": "partial",
            "expected_answer": source.get("gold_answer"),
            "risk_level": "cautious",
        },
        "annotation_confidence": "low",
        "annotator_notes": "",
    }


def build_csv_row(row: dict, source: dict) -> dict:
    source_modality = row["source_modality_necessity"]
    quality = row["modality_quality_status"]
    relevance = row["modality_task_relevance"]
    recovery = row["recovery_evidence"]
    oracle = row["oracle_policy_action"]
    hint = row["generator_hint"]
    media = row["media"]
    blind = row["question_only_blind"]
    return {
        "review_status": row["review_status"],
        "source_decision": row["source_decision"],
        "instance_id": row["instance_id"],
        "source_id": row["source_id"],
        "source_dataset": row["source_dataset"],
        "video_id": source.get("video_id", ""),
        "video_name": source.get("video_name", ""),
        "source_video_path": media.get("source_video_path", ""),
        "corrupted_video_path": media.get("corrupted_video_path", ""),
        "question": row["question"],
        "choices_json": json.dumps(row.get("choices", []), ensure_ascii=False),
        "gold_answer": row.get("gold_answer", ""),
        "question_relation": source.get("question_relation", ""),
        "question_type": source.get("question_type", ""),
        "source_bucket": source.get("bucket", ""),
        "generator_affected_modality": hint.get("affected_modality", ""),
        "generator_corruption_type": hint.get("corruption_type", ""),
        "generator_severity": hint.get("severity", ""),
        "generator_corruption_relevance": hint.get("corruption_relevance", ""),
        "question_only_answerable_without_media": blind["answerable_without_media"],
        "question_only_blind_confidence": blind["blind_confidence"],
        "question_only_blind_answer": blind["blind_answer"],
        "source_audio_relevance": source_modality["audio"],
        "source_video_relevance": source_modality["video"],
        "source_audio_video_joint_required": source_modality["audio_video_joint_required"],
        "source_evidence_note": row["source_evidence_note"],
        "modality_quality_audio": quality["audio"],
        "modality_quality_video": quality["video"],
        "modality_task_relevance_audio": relevance["audio"],
        "modality_task_relevance_video": relevance["video"],
        "cross_modal_relation": row["cross_modal_relation"],
        "corruption_relevance": row["corruption_relevance"],
        "corruption_effect": row["corruption_effect"],
        "post_corruption_answerability": row["post_corruption_answerability"],
        "cross_modal_recoverability": row["cross_modal_recoverability"],
        "main_answerability": row["main_answerability"],
        "risk_sensitive": row["risk_sensitive"],
        "recovery_source_json": json.dumps(row["recovery_source"], ensure_ascii=False),
        "recovery_audio_time_json": json.dumps(recovery["audio_time"], ensure_ascii=False),
        "recovery_video_time_json": json.dumps(recovery["video_time"], ensure_ascii=False),
        "recovery_note": recovery["note"],
        "acceptable_routes_json": json.dumps(oracle["acceptable_routes"], ensure_ascii=False),
        "preferred_route_json": json.dumps(oracle["preferred_route"], ensure_ascii=False),
        "disallowed_routes_json": json.dumps(oracle["disallowed_routes"], ensure_ascii=False),
        "oracle_abstain": oracle["abstain"],
        "oracle_answerability": oracle["answerability"],
        "oracle_expected_answer": oracle["expected_answer"] or "",
        "oracle_risk_level": oracle["risk_level"],
        "annotation_confidence": row["annotation_confidence"],
        "annotator_notes": row["annotator_notes"],
    }


def build(args: argparse.Namespace) -> int:
    sources = read_jsonl(args.source_items)
    corruptions = read_jsonl(args.corruption_manifest)
    sources_by_id = {row["source_id"]: row for row in sources}

    annotation_rows: list[dict] = []
    csv_rows: list[dict] = []
    errors: list[str] = []
    for corruption in corruptions:
        source = sources_by_id.get(corruption.get("source_id"))
        if source is None:
            errors.append(f"{corruption.get('instance_id')}: missing source {corruption.get('source_id')}")
            continue
        annotation_row = build_annotation_row(source, corruption)
        annotation_rows.append(annotation_row)
        csv_rows.append(build_csv_row(annotation_row, source))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    write_jsonl(args.output_jsonl, annotation_rows)
    write_csv(args.output_csv, csv_rows)
    print(f"wrote {len(annotation_rows)} JSONL rows: {args.output_jsonl}")
    print(f"wrote {len(csv_rows)} CSV rows: {args.output_csv}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-items", required=True, type=Path)
    parser.add_argument("--corruption-manifest", required=True, type=Path)
    parser.add_argument("--output-jsonl", required=True, type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    return build(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
