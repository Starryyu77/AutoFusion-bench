#!/usr/bin/env python3
"""Run exp-002 audio/video toolchain smoke and create corruption examples."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def ffmpeg_path() -> str:
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def probe_media(ffmpeg: str, path: Path) -> dict:
    proc = run([ffmpeg, "-hide_banner", "-i", str(path), "-f", "null", "-"])
    stderr = proc.stderr
    return {
        "path": str(path),
        "returncode": proc.returncode,
        "has_video": "Video:" in stderr,
        "has_audio": "Audio:" in stderr,
        "stderr_head": "\n".join(stderr.splitlines()[:12]),
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def make_audio_mute(ffmpeg: str, source: Path, output: Path) -> list[str]:
    return [
        ffmpeg,
        "-y",
        "-i",
        str(source),
        "-af",
        "volume=0",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "28",
        "-c:a",
        "aac",
        "-max_muxing_queue_size",
        "9999",
        "-shortest",
        str(output),
    ]


def make_video_blur(ffmpeg: str, source: Path, output: Path) -> list[str]:
    return [
        ffmpeg,
        "-y",
        "-i",
        str(source),
        "-vf",
        "boxblur=12:1",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "28",
        "-c:a",
        "copy",
        "-max_muxing_queue_size",
        "9999",
        str(output),
    ]


def make_audio_shift(ffmpeg: str, source: Path, output: Path) -> list[str]:
    return [
        ffmpeg,
        "-y",
        "-i",
        str(source),
        "-af",
        "adelay=1500|1500",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "28",
        "-c:a",
        "aac",
        "-max_muxing_queue_size",
        "9999",
        "-shortest",
        str(output),
    ]


def make_audio_replace(ffmpeg: str, video_source: Path, audio_source: Path, output: Path) -> list[str]:
    return [
        ffmpeg,
        "-y",
        "-i",
        str(video_source),
        "-i",
        str(audio_source),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-max_muxing_queue_size",
        "9999",
        "-shortest",
        str(output),
    ]


def corruption_for(row: dict, rows: list[dict], media_out: Path, ffmpeg: str) -> tuple[str, list[str], dict]:
    source = Path(row["video_path"])
    source_id = row["source_id"]
    bucket = row["bucket"]
    output = media_out / f"{source_id}.mp4"

    if bucket == "audio_necessary":
        return "audio_mute", make_audio_mute(ffmpeg, source, output), {
            "affected_modality": "audio",
            "severity": "severe",
            "corruption_relevance": "answer_relevant",
        }
    if bucket == "video_necessary":
        return "video_blur", make_video_blur(ffmpeg, source, output), {
            "affected_modality": "video",
            "severity": "medium",
            "corruption_relevance": "answer_relevant",
        }
    if bucket == "audio_video_complementary":
        return "audio_shift_1500ms", make_audio_shift(ffmpeg, source, output), {
            "affected_modality": "cross_modal",
            "severity": "medium",
            "corruption_relevance": "answer_relevant",
        }
    if bucket == "corrupted_irrelevant_control":
        return "video_blur_irrelevant", make_video_blur(ffmpeg, source, output), {
            "affected_modality": "video",
            "severity": "medium",
            "corruption_relevance": "answer_irrelevant",
        }

    audio_source = next(Path(candidate["video_path"]) for candidate in rows if candidate["bucket"] == "audio_necessary")
    return "audio_replace_conflict_like", make_audio_replace(ffmpeg, source, audio_source, output), {
        "affected_modality": "cross_modal",
        "severity": "severe",
        "corruption_relevance": "answer_relevant",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-items", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--probe-output", required=True, type=Path)
    args = parser.parse_args()

    ffmpeg = ffmpeg_path()
    rows = read_jsonl(args.source_items)
    media_out = args.output_dir / "corrupted_media"
    media_out.mkdir(parents=True, exist_ok=True)

    probes: list[dict] = []
    manifest: list[dict] = []
    for row in rows:
        source_path = Path(row["video_path"])
        source_probe = probe_media(ffmpeg, source_path)
        probes.append({"source_id": row["source_id"], "kind": "source", **source_probe})
        if not source_probe["has_audio"] or not source_probe["has_video"]:
            raise RuntimeError(f"{source_path} must contain both audio and video")

        corruption_type, cmd, metadata = corruption_for(row, rows, media_out, ffmpeg)
        proc = run(cmd)
        output_path = media_out / f"{row['source_id']}.mp4"
        output_probe = probe_media(ffmpeg, output_path)
        probes.append(
            {
                "source_id": row["source_id"],
                "kind": "corrupted",
                "corruption_type": corruption_type,
                **output_probe,
            }
        )
        if proc.returncode != 0 or not output_probe["has_video"] or not output_probe["has_audio"]:
            raise RuntimeError(
                f"corruption failed for {row['source_id']}: returncode={proc.returncode}\n{proc.stderr}"
            )
        manifest.append(
            {
                "instance_id": f"{row['source_id']}__{corruption_type}",
                "source_id": row["source_id"],
                "source_video_path": row["video_path"],
                "corrupted_video_path": str(output_path),
                "affected_modality": metadata["affected_modality"],
                "corruption_type": corruption_type,
                "severity": metadata["severity"],
                "location": {
                    "text_span": None,
                    "audio_time": None,
                    "video_time": None,
                    "frame_range": None,
                },
                "corruption_relevance": metadata["corruption_relevance"],
                "generator_family": "media_smoke_v0",
                "seed": 0,
            }
        )

    write_jsonl(args.probe_output, probes)
    write_jsonl(args.manifest, manifest)
    print(f"ffmpeg={ffmpeg}")
    print(f"wrote probes: {args.probe_output}")
    print(f"wrote manifest: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
