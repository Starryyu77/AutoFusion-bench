#!/usr/bin/env python3
"""Run DashScope OpenAI-compatible smoke calls for exp-002."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path

from openai import OpenAI


BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def encode_video(path: Path) -> str:
    with path.open("rb") as handle:
        return base64.b64encode(handle.read()).decode("utf-8")


def parse_json_object(text: str) -> tuple[bool, dict | None, str]:
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


def build_text(row: dict) -> str:
    choices = "\n".join(f"- {choice}" for choice in row["choices"])
    return (
        f"{row['prompt']}\n\n"
        f"Instance ID: {row['instance_id']}\n"
        f"Question: {row['question']}\n"
        f"Choices:\n{choices}\n\n"
        "Return JSON only. Set the model field to the model name you are using."
    )


def run_video_smoke(args: argparse.Namespace) -> int:
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        print("DASHSCOPE_API_KEY is not set", file=sys.stderr)
        return 2

    client = OpenAI(api_key=api_key, base_url=args.base_url)
    rows = read_jsonl(args.prompt_pack)[: args.limit]
    outputs = []
    for row in rows:
        media_path = Path(row["media_path"])
        if not media_path.is_absolute():
            media_path = args.repo_root / media_path
        base64_video = encode_video(media_path)
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
                                "video_url": {"url": f"data:;base64,{base64_video}"},
                            },
                            {"type": "text", "text": build_text(row)},
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
            outputs.append(
                {
                    "instance_id": row["instance_id"],
                    "source_id": row["source_id"],
                    "model": args.model,
                    "prompt_setting": row["prompt_setting"],
                    "media_path": str(media_path),
                    "response_text": response_text,
                    "parsed_ok": parsed_ok,
                    "parse_error": parse_error,
                    "parsed_json": parsed_json,
                    "usage": usage,
                    "status": "ok",
                }
            )
            print(f"{row['instance_id']}: parsed_ok={parsed_ok}")
        except Exception as exc:
            outputs.append(
                {
                    "instance_id": row["instance_id"],
                    "source_id": row["source_id"],
                    "model": args.model,
                    "prompt_setting": row["prompt_setting"],
                    "media_path": str(media_path),
                    "response_text": response_text,
                    "parsed_ok": False,
                    "parse_error": str(exc),
                    "parsed_json": None,
                    "usage": usage,
                    "status": "error",
                }
            )
            print(f"{row['instance_id']}: error={exc}", file=sys.stderr)

    write_jsonl(args.output, outputs)
    print(f"wrote {len(outputs)} rows: {args.output}")
    return 0 if all(row["status"] == "ok" for row in outputs) else 1


def run_text_probe(args: argparse.Namespace) -> int:
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        print("DASHSCOPE_API_KEY is not set", file=sys.stderr)
        return 2
    client = OpenAI(api_key=api_key, base_url=args.base_url)
    completion = client.chat.completions.create(
        model=args.model,
        messages=[
            {"role": "system", "content": "You are a concise assistant."},
            {"role": "user", "content": "请用一句话回答：你是谁？"},
        ],
        temperature=0,
    )
    text = completion.choices[0].message.content
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {
                "model": args.model,
                "status": "ok",
                "response_text": text,
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(text)
    print(f"wrote: {args.output}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=BASE_URL)
    subparsers = parser.add_subparsers(dest="command", required=True)

    text = subparsers.add_parser("text-probe")
    text.add_argument("--model", required=True)
    text.add_argument("--output", required=True, type=Path)
    text.set_defaults(func=run_text_probe)

    video = subparsers.add_parser("video-smoke")
    video.add_argument("--model", required=True)
    video.add_argument("--prompt-pack", required=True, type=Path)
    video.add_argument("--output", required=True, type=Path)
    video.add_argument("--repo-root", default=Path("."), type=Path)
    video.add_argument("--limit", default=5, type=int)
    video.set_defaults(func=run_video_smoke)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
