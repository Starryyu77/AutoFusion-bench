"""exp-001 decision-surface pilot runner."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .costs import build_budget_profile, load_cost_table
from .errors import ProtocolError
from .io import parse_simple_yaml, write_csv_records, write_json
from .leakage import (
    GateCheck,
    validate_class_stratified_corruption,
    validate_q_diagnostics,
    validate_q_proxy_table,
)
from .metrics import compute_primary_metrics, decision_rows, summarize_policy_decisions
from .outcomes import OutcomeLookup, assert_outcome_completeness, load_outcome_table
from .policies import evaluate_policies, load_q_policy_map


def run_exp001(
    *,
    config_path: Path,
    cost_table_path: Path,
    outcome_table_path: Path,
    q_policy_map_path: Path,
    q_proxy_table_path: Path,
    q_diagnostics_path: Path,
    corruption_manifest_path: Path,
    output_dir: Path,
    strict_outcomes: bool = True,
) -> dict[str, Any]:
    config = parse_simple_yaml(config_path)
    _validate_config_boundary(config)

    costs = load_cost_table(cost_table_path)
    budget_profile = build_budget_profile(costs)

    outcomes = load_outcome_table(outcome_table_path)
    if strict_outcomes:
        assert_outcome_completeness(outcomes)
    lookup = OutcomeLookup(outcomes)

    gate_checks: list[GateCheck] = [
        GateCheck(
            name="budget_validity_gate",
            passed=True,
            detail=(
                f"p95 spread={budget_profile.spread_ratio:.3f}; "
                f"tight={budget_profile.tight_ms:.3f}ms; loose={budget_profile.loose_ms:.3f}ms"
            ),
        )
    ]
    gate_checks.extend(validate_q_proxy_table(q_proxy_table_path))
    gate_checks.extend(validate_q_diagnostics(q_diagnostics_path))
    gate_checks.extend(validate_class_stratified_corruption(corruption_manifest_path))

    q_policy_map = load_q_policy_map(q_policy_map_path)
    decisions = evaluate_policies(lookup, budget_profile, q_policy_map)
    violations = [decision for decision in decisions if not decision.legal]
    if violations:
        first = violations[0]
        raise ProtocolError(
            "post-mask budget legality contract failed: "
            f"policy={first.policy} condition={first.condition} slice={first.slice} "
            f"selected={first.selected_template}"
        )
    gate_checks.append(
        GateCheck(
            name="post_mask_budget_legality_contract",
            passed=True,
            detail="all executed policy selections are legal under the active budget tier",
        )
    )
    policy_summary = summarize_policy_decisions(decisions)
    metrics = compute_primary_metrics(decisions, lookup)

    summary = {
        "config": {
            "hardware_target": config.get("hardware", {}).get("target"),
            "execution_mode": config.get("execution", {}).get("mode"),
            "dataset_priority": config.get("dataset", {}).get("priority"),
        },
        "budget": {
            "loose_ms": budget_profile.loose_ms,
            "tight_ms": budget_profile.tight_ms,
            "legal_by_budget": {
                key: list(value) for key, value in budget_profile.legal_by_budget.items()
            },
            "spread_ratio": budget_profile.spread_ratio,
            "tav_vs_unimodal_ratio": budget_profile.tav_vs_unimodal_ratio,
            "warnings": list(budget_profile.warnings),
        },
        "metrics": metrics,
        "gates": [
            {"name": check.name, "passed": check.passed, "detail": check.detail}
            for check in gate_checks
        ],
        "status": {
            "protocol_passed": all(check.passed for check in gate_checks),
            "benchmark_signal_passed": bool(
                (metrics["passes_regret_threshold"] and metrics["passes_noise_threshold"])
                or (
                    metrics["kendall_tau_b_clean_loose_vs_degraded_tight"] is not None
                    and metrics["kendall_tau_b_clean_loose_vs_degraded_tight"] <= 0.3
                )
            ),
            "joint_policy_passed": bool(
                metrics["joint_gap_closure"] is not None
                and metrics["joint_gap_closure"] >= 0.3
            ),
        },
    }

    _write_outputs(output_dir, summary, policy_summary, decisions, budget_profile)
    return summary


def _validate_config_boundary(config: dict[str, Any]) -> None:
    target = config.get("hardware", {}).get("target")
    mode = config.get("execution", {}).get("mode")
    if target != "ntu-gpu43":
        raise ProtocolError(f"exp-001 config must target ntu-gpu43, got {target!r}")
    if mode != "direct_ssh_tmux":
        raise ProtocolError(f"exp-001 execution mode must be direct_ssh_tmux, got {mode!r}")


def _write_outputs(
    output_dir: Path,
    summary: dict[str, Any],
    policy_summary: list[dict[str, object]],
    decisions: list[Any],
    budget_profile: Any,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "summary.json", summary)
    write_csv_records(
        output_dir / "gate_checks.csv",
        ("name", "passed", "detail"),
        summary["gates"],
    )
    write_csv_records(
        output_dir / "policy_summary.csv",
        (
            "policy",
            "condition",
            "n",
            "mean_macro_f1",
            "std_macro_f1",
            "pre_mask_illegal_proposal_rate",
            "post_mask_budget_violation_rate",
            "mean_fallback_regret",
        ),
        policy_summary,
    )
    write_csv_records(
        output_dir / "policy_decisions.csv",
        (
            "policy",
            "condition",
            "slice",
            "seed",
            "budget",
            "selected_template",
            "utility",
            "legal",
            "pre_mask_template",
            "pre_mask_illegal",
            "fallback_regret",
        ),
        decision_rows(decisions),
    )
    write_csv_records(
        output_dir / "budget_profile.csv",
        ("budget", "threshold_ms", "legal_templates"),
        (
            {
                "budget": "loose",
                "threshold_ms": budget_profile.loose_ms,
                "legal_templates": "|".join(budget_profile.legal_by_budget["loose"]),
            },
            {
                "budget": "tight",
                "threshold_ms": budget_profile.tight_ms,
                "legal_templates": "|".join(budget_profile.legal_by_budget["tight"]),
            },
        ),
    )
