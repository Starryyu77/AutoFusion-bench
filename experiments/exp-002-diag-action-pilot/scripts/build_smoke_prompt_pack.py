#!/usr/bin/env python3
"""Build prompt-pack JSONL for the exp-002 5-clip model smoke."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-items", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--prompt-template", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    source_by_id = {row["source_id"]: row for row in read_jsonl(args.source_items)}
    manifest = read_jsonl(args.manifest)
    prompt_template = args.prompt_template.read_text(encoding="utf-8")

    rows = []
    for item in manifest:
        source = source_by_id[item["source_id"]]
        rows.append(
            {
                "instance_id": item["instance_id"],
                "source_id": item["source_id"],
                "prompt_setting": "diagnosis_only_v0",
                "media_path": item["corrupted_video_path"],
                "question": source["question"],
                "choices": source["choices"],
                "gold_answer": source["gold_answer"],
                "bucket": source["bucket"],
                "corruption_type": item["corruption_type"],
                "affected_modality": item["affected_modality"],
                "corruption_relevance": item["corruption_relevance"],
                "prompt": prompt_template,
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} prompt-pack rows: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
