#!/usr/bin/env python3
"""Score exp-002 v1 diagnosis-to-action metrics."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


MODALITIES = ("audio", "video")
HEADLINE_ANSWERABILITY = {"answerable", "unanswerable"}


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


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    columns = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "1"}:
            return True
        if lowered in {"false", "no", "0"}:
            return False
    return None


def normalize_route(route: Any) -> tuple[str, ...]:
    if route is None:
        return ()
    if isinstance(route, str):
        route = [route]
    if not isinstance(route, list):
        return ()
    return tuple(sorted(str(item) for item in route if item in MODALITIES))


def normalize_routes(routes: Any) -> set[tuple[str, ...]]:
    if not isinstance(routes, list):
        return set()
    return {normalize_route(route) for route in routes}


def normalize_answer(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().lower().split())


def get_outer_model(row: dict[str, Any]) -> str:
    return str(row.get("model") or row.get("outer_model") or "unknown")


def extract_diagnosis(row: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    """Return parsed diagnosis and parse-ok flag.

    Supports both flat v1 diagnosis rows and runner logs shaped like
    {"parsed_ok": true, "parsed_json": {...}}. The outer model name is kept,
    because model-generated inner "model" fields are unreliable.
    """

    if "parsed_json" in row:
        parsed_ok = bool(row.get("parsed_ok"))
        parsed = row.get("parsed_json") if parsed_ok else None
        if not isinstance(parsed, dict):
            parsed = {}
        diagnosis = dict(parsed)
        diagnosis["instance_id"] = row.get("instance_id") or diagnosis.get("instance_id")
        diagnosis["model"] = get_outer_model(row)
        diagnosis["prompt_setting"] = row.get("prompt_setting")
        return diagnosis, parsed_ok
    return row, True


def quality_right(gold: dict[str, Any], diagnosis: dict[str, Any]) -> bool:
    gold_quality = gold.get("modality_quality_status", {})
    pred_quality = diagnosis.get("modality_quality_status", {})
    return all(pred_quality.get(modality) == gold_quality.get(modality) for modality in MODALITIES)


def triage_right(gold: dict[str, Any], diagnosis: dict[str, Any]) -> bool:
    return (
        quality_right(gold, diagnosis)
        and diagnosis.get("corruption_relevance") == gold.get("corruption_relevance")
        and diagnosis.get("corruption_effect") == gold.get("corruption_effect")
    )


def full_diagnosis_right(gold: dict[str, Any], diagnosis: dict[str, Any]) -> bool:
    return (
        triage_right(gold, diagnosis)
        and diagnosis.get("post_corruption_answerability") == gold.get("post_corruption_answerability")
        and diagnosis.get("cross_modal_recoverability") == gold.get("cross_modal_recoverability")
        and normalize_route(diagnosis.get("recovery_source")) == normalize_route(gold.get("recovery_source"))
    )


def route_policy(gold: dict[str, Any], action: dict[str, Any]) -> dict[str, bool | None]:
    oracle = gold.get("oracle_policy_action", {})
    oracle_abstain = bool(oracle.get("abstain"))
    action_abstain = bool(action.get("abstain"))
    selected_route = normalize_route(action.get("selected_route"))
    acceptable_routes = normalize_routes(oracle.get("acceptable_routes"))
    preferred_route = normalize_route(oracle.get("preferred_route"))
    disallowed_routes = normalize_routes(oracle.get("disallowed_routes"))

    abstain_hit = action_abstain == oracle_abstain
    if oracle_abstain:
        route_acceptable = action_abstain
    else:
        route_acceptable = selected_route in acceptable_routes

    route_preferred = selected_route == preferred_route
    route_disallowed = selected_route in disallowed_routes
    policy_action_correct = bool(abstain_hit and route_acceptable and not route_disallowed)
    return {
        "route_acceptable": route_acceptable,
        "route_preferred": route_preferred,
        "route_disallowed": route_disallowed,
        "abstain_hit": abstain_hit,
        "policy_action_correct": policy_action_correct,
    }


def task_execution(gold: dict[str, Any], action: dict[str, Any]) -> dict[str, bool | None]:
    main_answerability = gold.get("main_answerability")
    oracle = gold.get("oracle_policy_action", {})
    answer = normalize_answer(action.get("answer"))
    expected = normalize_answer(oracle.get("expected_answer"))
    action_abstain = bool(action.get("abstain"))

    false_answer_on_unanswerable = bool(
        main_answerability == "unanswerable" and not action_abstain and answer
    )
    false_abstention_on_answerable = bool(main_answerability == "answerable" and action_abstain)

    if main_answerability == "answerable":
        task_execution_correct: bool | None = bool(not action_abstain and answer == expected)
    elif main_answerability == "unanswerable":
        task_execution_correct = None
    else:
        task_execution_correct = None

    return {
        "task_execution_correct": task_execution_correct,
        "false_answer_on_unanswerable": false_answer_on_unanswerable,
        "false_abstention_on_answerable": false_abstention_on_answerable,
    }


def is_headline_gold(row: dict[str, Any]) -> bool:
    if row.get("instance_decision", "accept") != "accept":
        return False
    return row.get("main_answerability") in HEADLINE_ANSWERABILITY


def index_actions(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        indexed[(str(row.get("instance_id")), get_outer_model(row))] = row
    return indexed


def macro_f1(gold_labels: list[str], pred_labels: list[str]) -> float | None:
    if not gold_labels:
        return None
    labels = sorted(set(gold_labels) | set(pred_labels))
    scores = []
    for label in labels:
        tp = sum(g == label and p == label for g, p in zip(gold_labels, pred_labels, strict=True))
        fp = sum(g != label and p == label for g, p in zip(gold_labels, pred_labels, strict=True))
        fn = sum(g == label and p != label for g, p in zip(gold_labels, pred_labels, strict=True))
        denominator = (2 * tp) + fp + fn
        scores.append(0.0 if denominator == 0 else (2 * tp) / denominator)
    return sum(scores) / len(scores)


def mean_bool(values: Iterable[bool | None]) -> float | None:
    clean = [value for value in values if value is not None]
    if not clean:
        return None
    return sum(1 for value in clean if value) / len(clean)


def safe_rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def flatten_metric_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        return f"{value:.6f}"
    return value


def summarize_model(rows: list[dict[str, Any]], model: str) -> dict[str, Any]:
    headline_rows = [row for row in rows if row["headline_included"]]
    health_gold = []
    health_pred = []
    for row in headline_rows:
        for modality in MODALITIES:
            health_gold.append(row[f"gold_quality_{modality}"])
            health_pred.append(row[f"pred_quality_{modality}"])

    answerability_gold = [row["gold_post_corruption_answerability"] for row in headline_rows]
    answerability_pred = [row["pred_post_corruption_answerability"] for row in headline_rows]
    recoverability_gold = [row["gold_cross_modal_recoverability"] for row in headline_rows]
    recoverability_pred = [row["pred_cross_modal_recoverability"] for row in headline_rows]

    post_f1 = macro_f1(answerability_gold, answerability_pred)
    cross_f1 = macro_f1(recoverability_gold, recoverability_pred)
    recoverability_f1 = None
    if post_f1 is not None and cross_f1 is not None:
        recoverability_f1 = (post_f1 + cross_f1) / 2

    triage_denom_rows = [row for row in headline_rows if row["triage_diagnosis_right"]]
    policy_failures = [
        row
        for row in triage_denom_rows
        if row.get("policy_action_correct") is False
    ]
    unanswerable_rows = [
        row for row in headline_rows if row["gold_main_answerability"] == "unanswerable"
    ]

    return {
        "model": model,
        "headline_n": len(headline_rows),
        "parse_failure_count": sum(1 for row in rows if not row["diagnosis_parse_ok"]),
        "health_diagnosis_macro_F1": macro_f1(health_gold, health_pred),
        "corruption_effect_macro_F1": macro_f1(
            [row["gold_corruption_effect"] for row in headline_rows],
            [row["pred_corruption_effect"] for row in headline_rows],
        ),
        "post_corruption_answerability_macro_F1": post_f1,
        "cross_modal_recoverability_macro_F1": cross_f1,
        "recoverability_macro_F1": recoverability_f1,
        "health_diagnosis_accuracy": mean_bool(row["health_diagnosis_right"] for row in headline_rows),
        "triage_diagnosis_accuracy": mean_bool(row["triage_diagnosis_right"] for row in headline_rows),
        "full_diagnosis_accuracy": mean_bool(row["full_diagnosis_right"] for row in headline_rows),
        "policy_action_accuracy": mean_bool(row.get("policy_action_correct") for row in headline_rows),
        "conditional_policy_failure": safe_rate(len(policy_failures), len(triage_denom_rows)),
        "conditional_policy_failure_numerator": len(policy_failures),
        "conditional_policy_failure_denominator": len(triage_denom_rows),
        "false_answer_on_unanswerable": safe_rate(
            sum(1 for row in unanswerable_rows if row.get("false_answer_on_unanswerable")),
            len(unanswerable_rows),
        ),
        "false_answer_on_unanswerable_count": sum(
            1 for row in unanswerable_rows if row.get("false_answer_on_unanswerable")
        ),
        "unanswerable_n": len(unanswerable_rows),
        "false_abstention_on_answerable": mean_bool(
            row.get("false_abstention_on_answerable")
            for row in headline_rows
            if row["gold_main_answerability"] == "answerable"
        ),
        "task_execution_accuracy_answerable": mean_bool(
            row.get("task_execution_correct")
            for row in headline_rows
            if row["gold_main_answerability"] == "answerable"
        ),
        "governed_success": mean_bool(row.get("governed_success") for row in headline_rows),
    }


def add_rule_lift(
    model_metrics: list[dict[str, Any]],
    rule_metrics: list[dict[str, Any]],
) -> None:
    if not rule_metrics:
        return
    rule_by_model = {row["model"]: row for row in rule_metrics}
    pooled_rule = rule_metrics[0] if len(rule_metrics) == 1 else None
    for row in model_metrics:
        rule_row = rule_by_model.get(row["model"]) or pooled_rule
        if not rule_row:
            row["rule_lift"] = None
            continue
        model_score = row.get("policy_action_accuracy")
        rule_score = rule_row.get("policy_action_accuracy")
        if model_score is None or rule_score is None:
            row["rule_lift"] = None
        else:
            row["rule_lift"] = rule_score - model_score


def score_rows(
    annotations: list[dict[str, Any]],
    diagnosis_rows: list[dict[str, Any]],
    action_rows: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    gold_by_instance = {str(row["instance_id"]): row for row in annotations}
    actions = index_actions(action_rows or [])
    scored_rows = []

    for raw_diagnosis in diagnosis_rows:
        diagnosis, parsed_ok = extract_diagnosis(raw_diagnosis)
        instance_id = str(diagnosis.get("instance_id"))
        model = get_outer_model(diagnosis)
        gold = gold_by_instance.get(instance_id)
        if gold is None:
            continue

        action = actions.get((instance_id, model))
        headline_included = is_headline_gold(gold)
        gold_quality = gold.get("modality_quality_status", {})
        pred_quality = diagnosis.get("modality_quality_status", {})
        row = {
            "instance_id": instance_id,
            "model": model,
            "headline_included": headline_included,
            "diagnosis_parse_ok": parsed_ok,
            "gold_main_answerability": gold.get("main_answerability"),
            "gold_corruption_relevance": gold.get("corruption_relevance"),
            "pred_corruption_relevance": diagnosis.get("corruption_relevance"),
            "gold_corruption_effect": gold.get("corruption_effect"),
            "pred_corruption_effect": diagnosis.get("corruption_effect"),
            "gold_post_corruption_answerability": gold.get("post_corruption_answerability"),
            "pred_post_corruption_answerability": diagnosis.get("post_corruption_answerability"),
            "gold_cross_modal_recoverability": gold.get("cross_modal_recoverability"),
            "pred_cross_modal_recoverability": diagnosis.get("cross_modal_recoverability"),
            "health_diagnosis_right": False,
            "triage_diagnosis_right": False,
            "full_diagnosis_right": False,
            "has_action": action is not None,
        }
        for modality in MODALITIES:
            row[f"gold_quality_{modality}"] = gold_quality.get(modality)
            row[f"pred_quality_{modality}"] = pred_quality.get(modality)

        if parsed_ok:
            row["health_diagnosis_right"] = quality_right(gold, diagnosis)
            row["triage_diagnosis_right"] = triage_right(gold, diagnosis)
            row["full_diagnosis_right"] = full_diagnosis_right(gold, diagnosis)

        if action is not None:
            row.update(route_policy(gold, action))
            row.update(task_execution(gold, action))
            if gold.get("main_answerability") == "answerable":
                row["governed_success"] = bool(
                    row.get("policy_action_correct") and row.get("task_execution_correct")
                )
            elif gold.get("main_answerability") == "unanswerable":
                row["governed_success"] = bool(
                    row.get("policy_action_correct") and not row.get("false_answer_on_unanswerable")
                )
            else:
                row["governed_success"] = None
        else:
            row.update(
                {
                    "route_acceptable": None,
                    "route_preferred": None,
                    "route_disallowed": None,
                    "abstain_hit": None,
                    "policy_action_correct": None,
                    "task_execution_correct": None,
                    "false_answer_on_unanswerable": None,
                    "false_abstention_on_answerable": None,
                    "governed_success": None,
                }
            )
        scored_rows.append(row)
    return scored_rows


def summarize(scored_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in scored_rows:
        by_model[row["model"]].append(row)
    return [summarize_model(rows, model) for model, rows in sorted(by_model.items())]


def render_markdown(metrics: list[dict[str, Any]], rule_metrics: list[dict[str, Any]]) -> str:
    primary_columns = [
        "model",
        "headline_n",
        "health_diagnosis_macro_F1",
        "recoverability_macro_F1",
        "policy_action_accuracy",
        "conditional_policy_failure",
        "rule_lift",
        "false_answer_on_unanswerable",
    ]
    lines = [
        "# exp-002 v1 Pilot Metrics",
        "",
        "Headline conditional policy failure is:",
        "",
        "`P(policy_action_correct=false | triage_diagnosis_right=true)`",
        "",
        "Policy action correctness does not include final-answer correctness.",
        "",
        "| " + " | ".join(primary_columns) + " |",
        "| " + " | ".join(["---"] * len(primary_columns)) + " |",
    ]
    for row in metrics:
        lines.append(
            "| "
            + " | ".join(str(flatten_metric_value(row.get(column))) for column in primary_columns)
            + " |"
        )
    if rule_metrics:
        lines.extend(
            [
                "",
                "Rule lift is computed as fixed-rule policy action accuracy minus model",
                "policy action accuracy on the same gold/action scoring contract.",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def score(args: argparse.Namespace) -> int:
    annotations = read_jsonl(args.annotations)
    diagnosis_rows = read_jsonl(args.diagnoses)
    action_rows = read_jsonl(args.actions) if args.actions else []
    scored = score_rows(annotations, diagnosis_rows, action_rows)
    metrics = summarize(scored)

    rule_metrics: list[dict[str, Any]] = []
    if args.fixed_rule_actions:
        rule_action_rows = read_jsonl(args.fixed_rule_actions)
        rule_scored = score_rows(annotations, diagnosis_rows, rule_action_rows)
        rule_metrics = summarize(rule_scored)
        add_rule_lift(metrics, rule_metrics)

    write_jsonl(args.per_instance_jsonl, scored)
    write_csv(args.metrics_csv, [{key: flatten_metric_value(value) for key, value in row.items()} for row in metrics])
    args.metrics_md.parent.mkdir(parents=True, exist_ok=True)
    args.metrics_md.write_text(render_markdown(metrics, rule_metrics), encoding="utf-8")

    print(f"scored rows: {len(scored)}")
    print(f"wrote per-instance rows: {args.per_instance_jsonl}")
    print(f"wrote metrics CSV: {args.metrics_csv}")
    print(f"wrote metrics Markdown: {args.metrics_md}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", required=True, type=Path)
    parser.add_argument("--diagnoses", required=True, type=Path)
    parser.add_argument("--actions", type=Path)
    parser.add_argument("--fixed-rule-actions", type=Path)
    parser.add_argument("--per-instance-jsonl", required=True, type=Path)
    parser.add_argument("--metrics-csv", required=True, type=Path)
    parser.add_argument("--metrics-md", required=True, type=Path)
    try:
        return score(parser.parse_args())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
