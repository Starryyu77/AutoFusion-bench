#!/usr/bin/env python3
"""Build proxy action rows from frozen exp-002 v1 diagnoses."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


MODALITIES = ("audio", "video")
GOOD_QUALITY = {"clean", "corrupted_usable"}
GOOD_RELEVANCE = {"necessary", "sufficient", "supportive"}


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


def healthy_relevant_route(diagnosis: dict[str, Any]) -> list[str]:
    quality = diagnosis.get("modality_quality_status") or {}
    relevance = diagnosis.get("modality_task_relevance") or {}
    route = [
        modality
        for modality in MODALITIES
        if quality.get(modality) in GOOD_QUALITY and relevance.get(modality) in GOOD_RELEVANCE
    ]
    if route:
        return route
    return [modality for modality in MODALITIES if quality.get(modality) in GOOD_QUALITY]


def choose_model_implied_route(diagnosis: dict[str, Any]) -> tuple[list[str], bool, str]:
    answerability = diagnosis.get("post_corruption_answerability")
    recoverability = diagnosis.get("cross_modal_recoverability")
    if answerability == "unanswerable" or recoverability == "unrecoverable":
        return [], True, "diagnosis says the instance is not recoverably answerable"

    recovery_source = normalize_route(diagnosis.get("recovery_source"))
    if recovery_source:
        return recovery_source, False, "selected the model-reported recovery source"

    route = healthy_relevant_route(diagnosis)
    if route:
        return route, False, "selected healthy task-relevant modalities from diagnosis"
    return [], True, "no healthy task-relevant route was available in diagnosis"


def choose_fixed_rule_route(diagnosis: dict[str, Any]) -> tuple[list[str], bool, str]:
    answerability = diagnosis.get("post_corruption_answerability")
    recoverability = diagnosis.get("cross_modal_recoverability")
    if answerability in {"unanswerable", "partially_answerable", "unclear"}:
        return [], True, "fixed rule abstains unless answerability is clear"
    if recoverability in {"unrecoverable", "partially_recoverable", "unclear"}:
        return [], True, "fixed rule abstains unless recoverability is clear"

    recovery_source = normalize_route(diagnosis.get("recovery_source"))
    if recovery_source:
        return recovery_source, False, "fixed rule selects the explicit recovery source"

    quality = diagnosis.get("modality_quality_status") or {}
    relevance = diagnosis.get("modality_task_relevance") or {}
    for modality in MODALITIES:
        if quality.get(modality) in GOOD_QUALITY and relevance.get(modality) == "sufficient":
            return [modality], False, "fixed rule selects one sufficient healthy modality"

    route = healthy_relevant_route(diagnosis)
    if route:
        return route, False, "fixed rule selects healthy task-relevant modalities"
    return [], True, "fixed rule found no acceptable route"


def build_action(diagnosis: dict[str, Any], policy: str) -> dict[str, Any]:
    if policy == "model-implied":
        selected_route, abstain, rationale = choose_model_implied_route(diagnosis)
        risk_policy = "normal"
    elif policy == "fixed-rule":
        selected_route, abstain, rationale = choose_fixed_rule_route(diagnosis)
        risk_policy = "cautious"
    else:
        raise ValueError(f"unknown policy: {policy}")

    return {
        "instance_id": diagnosis["instance_id"],
        "model": diagnosis["model"],
        "diagnosis_source_id": diagnosis.get("diagnosis_source_id")
        or f"{diagnosis['model']}:{diagnosis['instance_id']}",
        "selected_route": selected_route,
        "abstain": abstain,
        "answer": None,
        "confidence": diagnosis.get("confidence", "low"),
        "risk_policy": risk_policy,
        "action_rationale": rationale,
        "action_builder_metadata": {
            "builder": "build_smoke_actions_v1",
            "policy": policy,
            "answer_field": "null_to_avoid_gold_leakage",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--diagnoses", required=True, type=Path)
    parser.add_argument("--policy", choices=["model-implied", "fixed-rule"], required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    actions = [build_action(row, args.policy) for row in read_jsonl(args.diagnoses)]
    write_jsonl(args.output, actions)
    print(f"built {args.policy} actions: {len(actions)}")
    print(f"wrote: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
