"""Metric aggregation for exp-001."""

from __future__ import annotations

import math
from collections import defaultdict
from statistics import mean, stdev
from typing import Iterable

from .constants import SINGLE_AXIS_POLICIES, TEMPLATES
from .outcomes import OutcomeLookup
from .policies import PolicyDecision


def summarize_policy_decisions(decisions: list[PolicyDecision]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[PolicyDecision]] = defaultdict(list)
    for decision in decisions:
        grouped[(decision.policy, decision.condition)].append(decision)

    rows: list[dict[str, object]] = []
    for (policy, condition), group in sorted(grouped.items()):
        values = [item.utility for item in group]
        rows.append(
            {
                "policy": policy,
                "condition": condition,
                "n": len(values),
                "mean_macro_f1": mean(values),
                "std_macro_f1": stdev(values) if len(values) > 1 else 0.0,
                "pre_mask_illegal_proposal_rate": _rate(
                    item.pre_mask_illegal for item in group if item.policy == "reliability_only"
                ),
                "post_mask_budget_violation_rate": _rate(not item.legal for item in group),
                "mean_fallback_regret": _mean_or_zero(
                    item.fallback_regret for item in group if item.fallback_regret != 0
                ),
            }
        )
    return rows


def compute_primary_metrics(
    decisions: list[PolicyDecision], lookup: OutcomeLookup
) -> dict[str, object]:
    degraded_tight = [
        item for item in decisions if item.condition == "degraded_tight"
    ]
    by_policy: dict[str, list[PolicyDecision]] = defaultdict(list)
    for item in degraded_tight:
        by_policy[item.policy].append(item)

    oracle_values = [item.utility for item in by_policy["feasible_oracle"]]
    policy_means = {
        policy: mean(item.utility for item in by_policy[policy])
        for policy in SINGLE_AXIS_POLICIES
    }
    best_single_axis_policy = max(policy_means, key=policy_means.__getitem__)
    oracle_seed_means = _seed_means(by_policy["feasible_oracle"])
    best_single_axis_seed_means = _seed_means(by_policy[best_single_axis_policy])
    oracle_mean = mean(oracle_values)
    best_single_axis_mean = policy_means[best_single_axis_policy]
    regret = oracle_mean - best_single_axis_mean
    pooled_se = _pooled_standard_error(oracle_seed_means, best_single_axis_seed_means)

    joint_mean = mean(item.utility for item in by_policy["joint"])
    joint_regret = oracle_mean - joint_mean
    gap_closure = None
    if regret > 0:
        gap_closure = (regret - joint_regret) / regret

    tau_b = kendall_tau_b(
        _template_means(lookup, condition="clean_loose", slice_name="clean"),
        _template_means(lookup, condition="degraded_tight", slice_name=None),
    )

    return {
        "primary_metric": "best_single_axis_oracle_regret_dt",
        "best_single_axis_policy": best_single_axis_policy,
        "feasible_oracle_degraded_tight_macro_f1": oracle_mean,
        "best_single_axis_degraded_tight_macro_f1": best_single_axis_mean,
        "best_single_axis_oracle_regret_dt": regret,
        "pooled_standard_error": pooled_se,
        "passes_regret_threshold": regret >= 3.0,
        "passes_noise_threshold": pooled_se == 0 or regret >= 1.5 * pooled_se,
        "joint_degraded_tight_macro_f1": joint_mean,
        "joint_gap_closure": gap_closure,
        "kendall_tau_b_clean_loose_vs_degraded_tight": tau_b,
        "rank_inversion_index": None if tau_b is None else (1 - tau_b) / 2,
    }


def decision_rows(decisions: list[PolicyDecision]) -> list[dict[str, object]]:
    return [
        {
            "policy": item.policy,
            "condition": item.condition,
            "slice": item.slice,
            "seed": item.seed,
            "budget": item.budget,
            "selected_template": item.selected_template,
            "utility": item.utility,
            "legal": item.legal,
            "pre_mask_template": item.pre_mask_template,
            "pre_mask_illegal": item.pre_mask_illegal,
            "fallback_regret": item.fallback_regret,
        }
        for item in decisions
    ]


def kendall_tau_b(
    ranking_a: dict[str, float], ranking_b: dict[str, float]
) -> float | None:
    templates = [template for template in TEMPLATES if template in ranking_a and template in ranking_b]
    concordant = 0
    discordant = 0
    ties_a = 0
    ties_b = 0
    for i, left in enumerate(templates):
        for right in templates[i + 1 :]:
            diff_a = _sign(ranking_a[left] - ranking_a[right])
            diff_b = _sign(ranking_b[left] - ranking_b[right])
            if diff_a == 0 and diff_b == 0:
                continue
            if diff_a == 0:
                ties_a += 1
            elif diff_b == 0:
                ties_b += 1
            elif diff_a == diff_b:
                concordant += 1
            else:
                discordant += 1
    denominator = math.sqrt(
        (concordant + discordant + ties_a) * (concordant + discordant + ties_b)
    )
    if denominator == 0:
        return None
    return (concordant - discordant) / denominator


def _template_means(
    lookup: OutcomeLookup, *, condition: str, slice_name: str | None
) -> dict[str, float]:
    means: dict[str, float] = {}
    for template in TEMPLATES:
        values = [
            row.macro_f1
            for row in lookup.outcomes
            if row.split == "test"
            and row.condition == condition
            and row.template == template
            and (slice_name is None or row.slice == slice_name)
        ]
        if values:
            means[template] = mean(values)
    return means


def _pooled_standard_error(left: list[float], right: list[float]) -> float:
    if len(left) < 2 or len(right) < 2:
        return 0.0
    return math.sqrt((stdev(left) ** 2 / len(left)) + (stdev(right) ** 2 / len(right)))


def _seed_means(decisions: list[PolicyDecision]) -> list[float]:
    by_seed: dict[int, list[float]] = defaultdict(list)
    for decision in decisions:
        by_seed[decision.seed].append(decision.utility)
    return [mean(values) for _, values in sorted(by_seed.items())]


def _sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def _rate(values: Iterable[bool]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(1 for value in values if value) / len(values)


def _mean_or_zero(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return mean(values)
