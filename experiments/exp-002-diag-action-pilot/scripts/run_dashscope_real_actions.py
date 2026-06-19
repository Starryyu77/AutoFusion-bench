#!/usr/bin/env python3
"""Run real action calls from frozen exp-002 diagnoses through DashScope."""

from __future__ import annotations

import argparse
import base64
import getpass
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable

from openai import OpenAI


BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
ROUTE = ("audio", "video")


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


def encode_video(path: Path) -> str:
    with path.open("rb") as handle:
        return base64.b64encode(handle.read()).decode("utf-8")


def parse_json_object(text: str) -> tuple[bool, dict[str, Any] | None, str]:
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    candidate = fenced.group(1) if fenced else text
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start < 0 or end < start:
        return False, None, "no_json_object"
    try:
        value = json.loads(candidate[start : end + 1])
    except json.JSONDecodeError as exc:
        return False, None, f"json_decode_error:{exc}"
    if not isinstance(value, dict):
        return False, None, "json_not_object"
    return True, value, "ok"


def normalize_route(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return []
    return [item for item in ROUTE if item in value]


def normalize_action(
    parsed: dict[str, Any] | None,
    *,
    instance_id: str,
    model: str,
    diagnosis_source_id: str,
    choices: list[str],
) -> dict[str, Any] | None:
    if not isinstance(parsed, dict):
        return None

    abstain = bool(parsed.get("abstain"))
    answer = parsed.get("answer")
    if abstain:
        answer = None
    elif answer not in choices:
        answer = str(answer).strip() if answer is not None else None

    confidence = parsed.get("confidence")
    if confidence not in {"high", "medium", "low"}:
        confidence = "low"

    risk_policy = parsed.get("risk_policy")
    if risk_policy not in {"normal", "cautious"}:
        risk_policy = "cautious"

    return {
        "instance_id": instance_id,
        "model": model,
        "diagnosis_source_id": diagnosis_source_id,
        "selected_route": normalize_route(parsed.get("selected_route")),
        "abstain": abstain,
        "answer": answer,
        "confidence": confidence,
        "risk_policy": risk_policy,
        "action_rationale": str(parsed.get("action_rationale") or "")[:500],
        "action_runner_metadata": {
            "runner": "run_dashscope_real_actions",
            "raw_model_field": parsed.get("model"),
            "schema": "action_from_diagnosis_v1",
        },
    }


def build_prompt_text(prompt: str, annotation: dict[str, Any], diagnosis: dict[str, Any]) -> str:
    choices = "\n".join(f"- {choice}" for choice in annotation["choices"])
    diagnosis_json = json.dumps(diagnosis, ensure_ascii=False, sort_keys=True)
    return (
        f"{prompt}\n\n"
        f"Instance ID: {annotation['instance_id']}\n"
        f"Question: {annotation['question']}\n"
        f"Choices:\n{choices}\n\n"
        f"Frozen diagnosis JSON:\n{diagnosis_json}\n\n"
        "Return JSON only. Set the model field to the model name you are using."
    )


def get_media_path(annotation: dict[str, Any], repo_root: Path) -> Path:
    media = annotation.get("media") or {}
    path_value = media.get("corrupted_video_path")
    if not path_value:
        raise ValueError(f"{annotation['instance_id']}: missing corrupted_video_path")
    media_path = Path(path_value)
    if not media_path.is_absolute():
        media_path = repo_root / media_path
    if not media_path.exists():
        raise ValueError(f"{annotation['instance_id']}: media not found: {media_path}")
    return media_path


def run_actions(args: argparse.Namespace) -> int:
    api_key = getpass.getpass("") if args.api_key_stdin else os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        print("DASHSCOPE_API_KEY is not set", file=sys.stderr)
        return 2

    prompt = args.prompt.read_text(encoding="utf-8")
    annotations = {str(row["instance_id"]): row for row in read_jsonl(args.annotations)}
    diagnoses = [
        row
        for row in read_jsonl(args.diagnoses)
        if row.get("model") == args.model and str(row.get("instance_id")) in annotations
    ]
    diagnoses = sorted(diagnoses, key=lambda row: str(row["instance_id"]))[: args.limit]
    if not diagnoses:
        print(f"no diagnoses found for model={args.model}", file=sys.stderr)
        return 2

    client = OpenAI(api_key=api_key, base_url=args.base_url, timeout=args.timeout)
    raw_rows: list[dict[str, Any]] = []
    action_rows: list[dict[str, Any]] = []

    for diagnosis in diagnoses:
        instance_id = str(diagnosis["instance_id"])
        annotation = annotations[instance_id]
        media_path = get_media_path(annotation, args.repo_root)
        response_text = ""
        usage = None
        try:
            completion = client.chat.completions.create(
                model=args.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "video_url",
                                "video_url": {"url": f"data:;base64,{encode_video(media_path)}"},
                            },
                            {"type": "text", "text": build_prompt_text(prompt, annotation, diagnosis)},
                        ],
                    }
                ],
                modalities=["text"],
                stream=True,
                stream_options={"include_usage": True},
                temperature=0,
            )
            for chunk in completion:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    content = getattr(delta, "content", None)
                    if content:
                        response_text += content
                else:
                    usage_obj = getattr(chunk, "usage", None)
                    if usage_obj is not None:
                        usage = usage_obj.model_dump() if hasattr(usage_obj, "model_dump") else str(usage_obj)
            parsed_ok, parsed_json, parse_error = parse_json_object(response_text)
            action = normalize_action(
                parsed_json,
                instance_id=instance_id,
                model=args.model,
                diagnosis_source_id=str(diagnosis.get("diagnosis_source_id") or f"{args.model}:{instance_id}"),
                choices=list(annotation["choices"]),
            )
            if action is not None:
                action_rows.append(action)
            raw_rows.append(
                {
                    "instance_id": instance_id,
                    "model": args.model,
                    "diagnosis_source_id": diagnosis.get("diagnosis_source_id"),
                    "media_path": str(media_path),
                    "response_text": response_text,
                    "parsed_ok": parsed_ok,
                    "parse_error": parse_error,
                    "parsed_json": parsed_json,
                    "normalized_action": action,
                    "usage": usage,
                    "status": "ok",
                }
            )
            print(f"{args.model} {instance_id}: parsed_ok={parsed_ok}")
        except Exception as exc:
            raw_rows.append(
                {
                    "instance_id": instance_id,
                    "model": args.model,
                    "diagnosis_source_id": diagnosis.get("diagnosis_source_id"),
                    "media_path": str(media_path),
                    "response_text": response_text,
                    "parsed_ok": False,
                    "parse_error": str(exc),
                    "parsed_json": None,
                    "normalized_action": None,
                    "usage": usage,
                    "status": "error",
                }
            )
            print(f"{args.model} {instance_id}: error={exc}", file=sys.stderr)

    write_jsonl(args.output, raw_rows)
    write_jsonl(args.actions_output, action_rows)
    print(f"wrote raw rows: {args.output}")
    print(f"wrote actions: {args.actions_output}")
    expected = len(diagnoses)
    if len(action_rows) != expected:
        return 1
    return 0 if all(row["status"] == "ok" and row["parsed_ok"] for row in raw_rows) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--model", required=True)
    parser.add_argument("--annotations", required=True, type=Path)
    parser.add_argument("--diagnoses", required=True, type=Path)
    parser.add_argument("--prompt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--actions-output", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path("."), type=Path)
    parser.add_argument("--limit", default=4, type=int)
    parser.add_argument("--timeout", default=120.0, type=float)
    parser.add_argument(
        "--api-key-stdin",
        action="store_true",
        help="Read API key from hidden stdin instead of DASHSCOPE_API_KEY.",
    )
    return run_actions(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
