#!/usr/bin/env python3
"""Select five AVQA clips for the exp-002 media smoke."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SMOKE_PLAN = [
    ("smoke-audio-necessary", "Sound", "audio_necessary"),
    ("smoke-video-necessary", "View", "video_necessary"),
    ("smoke-av-complementary", "Both", "audio_video_complementary"),
    ("smoke-corrupted-irrelevant", "Sound", "corrupted_irrelevant_control"),
    ("smoke-conflict-like", "Both", "conflict_like"),
]


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def modality_necessity(relation: str) -> dict:
    if relation == "Sound":
        return {
            "text_question_only": False,
            "audio_sufficient": True,
            "video_sufficient": False,
            "audio_video_joint_required": False,
            "human_confidence": "pending_manual_review",
        }
    if relation == "View":
        return {
            "text_question_only": False,
            "audio_sufficient": False,
            "video_sufficient": True,
            "audio_video_joint_required": False,
            "human_confidence": "pending_manual_review",
        }
    return {
        "text_question_only": False,
        "audio_sufficient": False,
        "video_sufficient": False,
        "audio_video_joint_required": True,
        "human_confidence": "pending_manual_review",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection-jsonl", required=True, type=Path)
    parser.add_argument("--media-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    rows = read_jsonl(args.selection_jsonl)
    used_video_names: set[str] = set()
    selected: list[dict] = []
    for smoke_id, relation, bucket in SMOKE_PLAN:
        match = None
        for row in rows:
            video_name = row["video_name"]
            video_path = args.media_root / f"{video_name}.mp4"
            if (
                row.get("question_relation") == relation
                and video_name not in used_video_names
                and video_path.exists()
            ):
                match = row
                break
        if match is None:
            raise RuntimeError(f"no available {relation} sample for {smoke_id}")
        used_video_names.add(match["video_name"])
        choices = match.get("multi_choice", [])
        answer_index = match.get("answer")
        gold_answer = choices[answer_index] if isinstance(answer_index, int) and answer_index < len(choices) else answer_index
        selected.append(
            {
                "source_id": smoke_id,
                "source_dataset": "AVQA_HF_sample",
                "video_id": match.get("video_id"),
                "video_name": match["video_name"],
                "video_path": str(args.media_root / f"{match['video_name']}.mp4"),
                "question": match["question_text"],
                "choices": choices,
                "answer_index": answer_index,
                "gold_answer": gold_answer,
                "question_relation": match.get("question_relation"),
                "question_type": match.get("question_type"),
                "modality_necessity": modality_necessity(relation),
                "bucket": bucket,
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in selected:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(selected)} smoke source items: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
