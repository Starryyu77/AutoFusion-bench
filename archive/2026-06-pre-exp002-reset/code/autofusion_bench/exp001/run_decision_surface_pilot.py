"""CLI entrypoint for exp-001.

Example:
    python -m autofusion_bench.exp001.run_decision_surface_pilot \
      --config experiments/exp-001-decision-surface-pilot/config.yaml \
      --fixture-smoke
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .errors import ProtocolError
from .runner import run_exp001


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    repo_root = Path.cwd()
    exp_dir = repo_root / "experiments" / "exp-001-decision-surface-pilot"
    fixture_dir = exp_dir / "fixtures"

    if args.fixture_smoke:
        cost_table = fixture_dir / "cost_table.csv"
        outcome_table = fixture_dir / "outcome_table.csv"
        q_policy_map = fixture_dir / "q_policy_map.csv"
        q_proxy_table = fixture_dir / "q_proxy_table.csv"
        q_diagnostics = fixture_dir / "q_diagnostics.csv"
        corruption_manifest = fixture_dir / "corruption_manifest.csv"
        output_dir = exp_dir / "outputs" / "fixture-smoke"
    else:
        cost_table = Path(args.cost_table)
        outcome_table = Path(args.outcome_table)
        q_policy_map = Path(args.q_policy_map)
        q_proxy_table = Path(args.q_proxy_table)
        q_diagnostics = Path(args.q_diagnostics)
        corruption_manifest = Path(args.corruption_manifest)
        output_dir = Path(args.output)

    try:
        summary = run_exp001(
            config_path=Path(args.config),
            cost_table_path=cost_table,
            outcome_table_path=outcome_table,
            q_policy_map_path=q_policy_map,
            q_proxy_table_path=q_proxy_table,
            q_diagnostics_path=q_diagnostics,
            corruption_manifest_path=corruption_manifest,
            output_dir=output_dir,
            strict_outcomes=not args.allow_incomplete_outcomes,
        )
    except ProtocolError as exc:
        print(f"exp-001 protocol failed: {exc}", file=sys.stderr)
        return 2

    metrics = summary["metrics"]
    status = summary["status"]
    print("exp-001 protocol run complete")
    print(f"output_dir={output_dir}")
    print(
        "best_single_axis_oracle_regret_dt="
        f"{metrics['best_single_axis_oracle_regret_dt']:.3f}"
    )
    print(f"best_single_axis_policy={metrics['best_single_axis_policy']}")
    print(f"joint_gap_closure={metrics['joint_gap_closure']}")
    print(f"protocol_passed={status['protocol_passed']}")
    print(f"benchmark_signal_passed={status['benchmark_signal_passed']}")
    print(f"joint_policy_passed={status['joint_policy_passed']}")
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run exp-001 decision-surface protocol analysis.")
    parser.add_argument("--config", required=True, help="Path to exp-001 config.yaml")
    parser.add_argument(
        "--fixture-smoke",
        action="store_true",
        help="Run the checked-in protocol fixture. This is not empirical evidence.",
    )
    parser.add_argument("--cost-table", help="CSV with template,p50_ms,p95_ms,peak_memory_mb")
    parser.add_argument("--outcome-table", help="CSV with split,condition,slice,template,seed,macro_f1")
    parser.add_argument("--q-policy-map", help="CSV mapping proxy slices to proposed templates")
    parser.add_argument("--q-proxy-table", help="CSV of q(x) proxy fields for leakage-boundary check")
    parser.add_argument("--q-diagnostics", help="CSV of q-only and q-shuffle diagnostics")
    parser.add_argument("--corruption-manifest", help="CSV corruption assignment manifest")
    parser.add_argument("--output", default="experiments/exp-001-decision-surface-pilot/outputs/run")
    parser.add_argument("--log-dir", help="Accepted for launcher compatibility; logs are not written here yet.")
    parser.add_argument(
        "--allow-incomplete-outcomes",
        action="store_true",
        help="Allow partial outcome tables for early bring-up. Full exp-001 should not use this.",
    )
    args = parser.parse_args(argv)
    if not args.fixture_smoke:
        missing = [
            name
            for name in (
                "cost_table",
                "outcome_table",
                "q_policy_map",
                "q_proxy_table",
                "q_diagnostics",
                "corruption_manifest",
            )
            if getattr(args, name) is None
        ]
        if missing:
            parser.error(f"missing required arguments outside --fixture-smoke: {', '.join(missing)}")
    return args


if __name__ == "__main__":
    raise SystemExit(main())

