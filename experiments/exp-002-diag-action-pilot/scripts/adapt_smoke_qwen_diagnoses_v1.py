#!/usr/bin/env python3
"""Adapt legacy Qwen smoke diagnosis logs to exp-002 scorer v1 rows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


MODALITIES = ("audio", "video")
VALID_QUALITY = {"clean", "corrupted_usable", "corrupted_unusable", "missing", "not_applicable"}
VALID_RELEVANCE = {"necessary", "sufficient", "supportive", "irrelevant", "unclear"}
VALID_RECOVERABILITY = {
    "recoverable",
    "partially_recoverable",
    "unrecoverable",
    "not_needed",
    "unclear",
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


def normalize_route(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return []
    return [modality for modality in MODALITIES if modality in value]


def normalize_time_field(value: Any) -> Any:
    if value == []:
        return None
    return value


def map_quality(status: Any, modality: str, recovery_source: list[str], recoverability: str) -> str:
    raw = str(status or "unclear").strip().lower()
    if raw in VALID_QUALITY:
        return raw
    if raw == "corrupted":
        if modality in recovery_source or recoverability in {"recoverable", "partially_recoverable"}:
            return "corrupted_usable"
        return "corrupted_unusable"
    if raw == "irrelevant":
        return "clean"
    if raw in {"absent", "muted", "silent"}:
        return "missing"
    return "clean" if raw == "normal" else "corrupted_unusable" if raw == "unusable" else "clean"


def map_relevance(
    old_status: Any,
    quality: str,
    modality: str,
    recovery_source: list[str],
    corruption_relevance: str,
    recoverability: str,
) -> str:
    raw = str(old_status or "").strip().lower()
    if raw in VALID_RELEVANCE:
        return raw
    if raw == "irrelevant":
        return "irrelevant"
    if modality in recovery_source:
        return "sufficient"
    if quality in {"missing", "corrupted_unusable"} and corruption_relevance == "answer_relevant":
        return "necessary"
    if recoverability == "unrecoverable" and quality == "clean":
        return "irrelevant"
    if quality == "clean":
        return "supportive"
    return "unclear"


def map_recoverability(value: Any) -> str:
    raw = str(value or "unclear").strip().lower()
    if raw in VALID_RECOVERABILITY:
        return raw
    if raw == "partial":
        return "partially_recoverable"
    return "unclear"


def infer_answerability(recoverability: str) -> str:
    if recoverability == "unrecoverable":
        return "unanswerable"
    if recoverability == "partially_recoverable":
        return "partially_answerable"
    if recoverability in {"recoverable", "not_needed"}:
        return "answerable"
    return "unclear"


def infer_effect(
    recoverability: str,
    recovery_source: list[str],
    corruption_relevance: str,
    answerability: str,
) -> str:
    if answerability == "unanswerable":
        return "makes_unanswerable"
    if corruption_relevance == "answer_irrelevant":
        return "no_effect"
    if recovery_source:
        return "route_change_only"
    if answerability == "partially_answerable":
        return "confidence_drop"
    if recoverability == "recoverable":
        return "route_change_only"
    return "unclear"


def infer_relation(instance_id: str, quality: dict[str, str]) -> str:
    if "audio_shift" in instance_id:
        return "misaligned"
    if "conflict" in instance_id:
        return "conflicting"
    if all(quality.get(modality) == "clean" for modality in MODALITIES):
        return "consistent"
    return "unclear"


def adapt_row(row: dict[str, Any]) -> dict[str, Any]:
    parsed = row.get("parsed_json") if row.get("parsed_ok") else {}
    if not isinstance(parsed, dict):
        parsed = {}

    instance_id = str(row.get("instance_id") or parsed.get("instance_id") or "")
    model = str(row.get("model") or row.get("outer_model") or "unknown")
    recovery_source = normalize_route(parsed.get("recovery_source"))
    recoverability = map_recoverability(parsed.get("recoverability"))
    old_status = parsed.get("modality_status") or {}
    if not isinstance(old_status, dict):
        old_status = {}

    quality = {
        modality: map_quality(old_status.get(modality), modality, recovery_source, recoverability)
        for modality in MODALITIES
    }
    quality["text"] = "not_applicable"

    corruption_relevance = str(parsed.get("corruption_relevance") or "unclear")
    if corruption_relevance not in {"answer_relevant", "answer_irrelevant", "unclear"}:
        corruption_relevance = "unclear"
    answerability = infer_answerability(recoverability)
    effect = infer_effect(recoverability, recovery_source, corruption_relevance, answerability)
    relevance = {
        modality: map_relevance(
            old_status.get(modality),
            quality[modality],
            modality,
            recovery_source,
            corruption_relevance,
            recoverability,
        )
        for modality in MODALITIES
    }
    relevance["text"] = "not_applicable"

    defect_location = parsed.get("defect_location") or {}
    if not isinstance(defect_location, dict):
        defect_location = {}
    recovery_evidence = parsed.get("recovery_evidence") or {}
    if not isinstance(recovery_evidence, dict):
        recovery_evidence = {}

    return {
        "instance_id": instance_id,
        "model": model,
        "prompt_setting": row.get("prompt_setting"),
        "diagnosis_source_id": f"{model}:{instance_id}:adapted-v1",
        "modality_quality_status": quality,
        "modality_task_relevance": relevance,
        "cross_modal_relation": infer_relation(instance_id, quality),
        "defect_location": {
            "audio_time": normalize_time_field(defect_location.get("audio_time")),
            "video_time": normalize_time_field(defect_location.get("video_time")),
            "frame_range": normalize_time_field(defect_location.get("frame_range")),
            "region_note": defect_location.get("region_note"),
        },
        "corruption_relevance": corruption_relevance,
        "corruption_effect": effect,
        "post_corruption_answerability": answerability,
        "cross_modal_recoverability": recoverability,
        "recovery_source": recovery_source,
        "recovery_evidence": {
            "audio_time": normalize_time_field(recovery_evidence.get("audio_time")),
            "video_time": normalize_time_field(recovery_evidence.get("video_time")),
            "note": recovery_evidence.get("note") or "",
        },
        "confidence": parsed.get("confidence") if parsed.get("confidence") in {"high", "medium", "low"} else "low",
        "adapter_metadata": {
            "adapter": "adapt_smoke_qwen_diagnoses_v1",
            "source_prompt_setting": row.get("prompt_setting"),
            "source_parsed_ok": bool(row.get("parsed_ok")),
            "source_schema": "diagnosis_only_v0",
            "target_schema": "diagnosis_only_v1",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    adapted = []
    for input_path in args.input:
        adapted.extend(adapt_row(row) for row in read_jsonl(input_path))
    write_jsonl(args.output, adapted)
    print(f"adapted rows: {len(adapted)}")
    print(f"wrote: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
