"""CLI for producing exp-001 measured tables from staged MELD assets."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .errors import ProtocolError
from .meld_producer import ProducerInputs, produce_meld_tables


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    seeds = tuple(int(seed.strip()) for seed in args.seeds.split(",") if seed.strip())
    try:
        summary = produce_meld_tables(
            ProducerInputs(
                annotations_dir=Path(args.annotations_dir),
                features_dir=Path(args.features_dir) if args.features_dir else None,
                raw_root=Path(args.raw_root) if args.raw_root else None,
                output_dir=Path(args.output),
                seeds=seeds,
                video_source=args.video_source,
                audio_source=args.audio_source,
                feature_cache_dir=Path(args.feature_cache_dir)
                if args.feature_cache_dir
                else Path(args.output) / "feature-cache",
                max_train_samples=args.max_train_samples,
                max_eval_samples=args.max_eval_samples,
            )
        )
    except ProtocolError as exc:
        print(f"MELD table producer failed: {exc}", file=sys.stderr)
        return 2
    print("MELD table producer complete")
    print(f"output_dir={args.output}")
    print(f"records={summary['records']}")
    print(f"feature_sources={summary['feature_sources']}")
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Produce exp-001 MELD measured tables.")
    parser.add_argument(
        "--annotations-dir",
        default="/usr1/home/s125mdg43_10/datasets/MELD/annotations",
    )
    parser.add_argument(
        "--features-dir",
        default="/usr1/home/s125mdg43_10/datasets/MELD/official/features",
    )
    parser.add_argument("--raw-root", default=None)
    parser.add_argument(
        "--video-source",
        choices=("pickle", "raw_stats", "cv2_stats", "annotation_proxy"),
        default="pickle",
        help="Use pickle for visual pickles, cv2_stats for decoded MP4 frame features, raw_stats for file-stat features, or annotation_proxy only for smoke.",
    )
    parser.add_argument(
        "--audio-source",
        choices=("official_full", "official_concat"),
        default="official_concat",
        help="official_concat adds full utterance-level audio embeddings plus dialogue-sequence audio features when complete.",
    )
    parser.add_argument("--feature-cache-dir", default=None)
    parser.add_argument(
        "--output",
        default="experiments/exp-001-decision-surface-pilot/outputs/meld-producer",
    )
    parser.add_argument("--seeds", default="0,1,2")
    parser.add_argument("--max-train-samples", type=int, default=None)
    parser.add_argument("--max-eval-samples", type=int, default=None)
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
