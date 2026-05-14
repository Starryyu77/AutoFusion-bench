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
        choices=("pickle", "raw_stats", "annotation_proxy"),
        default="pickle",
        help="Use pickle for real visual features, raw_stats for raw MP4 file-stat features, or annotation_proxy only for smoke.",
    )
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

