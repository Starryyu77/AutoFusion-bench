"""Policy evaluation for the exp-001 offline outcome table."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from statistics import mean

from .constants import (
    CONDITION_BUDGET,
    POLICIES,
    SINGLE_AXIS_POLICIES,
    TEMPLATE_MODALITIES,
    TEMPLATES,
)
from .costs import BudgetProfile
from .errors import ProtocolError
from .io import read_csv_records
from .outcomes import OutcomeLookup


@dataclass(frozen=True)
class PolicyDecision:
    policy: str
    condition: str
    slice: str
    seed: int
    budget: str
    selected_template: str
    utility: float
    legal: bool
    pre_mask_template: str = ""
    pre_mask_illegal: bool = False
    fallback_regret: float = 0.0


def load_q_policy_map(path: Path) -> dict[str, str]:
    rows = read_csv_records(path)
    required = {"slice", "proposed_template"}
    if rows and not required.issubset(rows[0]):
        missing = sorted(required - set(rows[0]))
        raise ProtocolError(f"q policy map missing columns: {missing}")
    mapping: dict[str, str] = {}
    for row in rows:
        slice_name = row["slice"].strip()
        template = row["proposed_template"].strip()
        if template not in TEMPLATES:
            raise ProtocolError(f"q policy map proposes unknown template: {template}")
        mapping[slice_name] = template
    return mapping


def evaluate_policies(
    lookup: OutcomeLookup,
    budget_profile: BudgetProfile,
    q_policy_map: dict[str, str],
) -> list[PolicyDecision]:
    decisions: list[PolicyDecision] = []
    for condition, slice_name, seed in lookup.test_keys():
        budget = CONDITION_BUDGET[condition]
        legal = budget_profile.legal_by_budget[budget]
        for policy in POLICIES:
            decision = _evaluate_policy(
                policy=policy,
                lookup=lookup,
                condition=condition,
                slice_name=slice_name,
                seed=seed,
                budget=budget,
                legal_templates=legal,
                q_policy_map=q_policy_map,
            )
            decisions.append(decision)
    return decisions


def _evaluate_policy(
    *,
    policy: str,
    lookup: OutcomeLookup,
    condition: str,
    slice_name: str,
    seed: int,
    budget: str,
    legal_templates: tuple[str, ...],
    q_policy_map: dict[str, str],
) -> PolicyDecision:
    if policy == "random_legal":
        values = [
            lookup.utility("test", condition, slice_name, template, seed)
            for template in legal_templates
        ]
        selected = "|".join(legal_templates)
        utility = mean(values)
        return PolicyDecision(policy, condition, slice_name, seed, budget, selected, utility, True)

    if policy == "clean_best":
        selected = _clean_best(lookup, legal_templates)
        return _selected_decision(
            policy, lookup, condition, slice_name, seed, budget, selected, legal_templates
        )

    if policy == "static_full":
        selected = "TAV" if "TAV" in legal_templates else _clean_best(lookup, legal_templates)
        return _selected_decision(
            policy, lookup, condition, slice_name, seed, budget, selected, legal_templates
        )

    if policy == "budget_only":
        selected = _budget_only(lookup, legal_templates, budget)
        return _selected_decision(
            policy, lookup, condition, slice_name, seed, budget, selected, legal_templates
        )

    if policy == "reliability_only":
        proposed = q_policy_map.get(slice_name)
        if proposed is None:
            raise ProtocolError(f"q policy map has no proposal for slice={slice_name}")
        pre_mask_illegal = proposed not in legal_templates
        if pre_mask_illegal:
            selected = _nearest_legal_template(proposed, legal_templates)
        else:
            selected = proposed
        selected_utility = lookup.utility("test", condition, slice_name, selected, seed)
        proposed_utility = lookup.utility("test", condition, slice_name, proposed, seed)
        return PolicyDecision(
            policy=policy,
            condition=condition,
            slice=slice_name,
            seed=seed,
            budget=budget,
            selected_template=selected,
            utility=selected_utility,
            legal=selected in legal_templates,
            pre_mask_template=proposed,
            pre_mask_illegal=pre_mask_illegal,
            fallback_regret=proposed_utility - selected_utility if pre_mask_illegal else 0.0,
        )

    if policy == "joint":
        selected = _joint_template(lookup, legal_templates, slice_name)
        return _selected_decision(
            policy, lookup, condition, slice_name, seed, budget, selected, legal_templates
        )

    if policy == "feasible_oracle":
        selected = max(
            legal_templates,
            key=lambda template: lookup.utility("test", condition, slice_name, template, seed),
        )
        return _selected_decision(
            policy, lookup, condition, slice_name, seed, budget, selected, legal_templates
        )

    raise ProtocolError(f"unknown policy: {policy}")


def _selected_decision(
    policy: str,
    lookup: OutcomeLookup,
    condition: str,
    slice_name: str,
    seed: int,
    budget: str,
    selected: str,
    legal_templates: tuple[str, ...],
) -> PolicyDecision:
    utility = lookup.utility("test", condition, slice_name, selected, seed)
    return PolicyDecision(
        policy=policy,
        condition=condition,
        slice=slice_name,
        seed=seed,
        budget=budget,
        selected_template=selected,
        utility=utility,
        legal=selected in legal_templates,
    )


def _clean_best(lookup: OutcomeLookup, legal_templates: tuple[str, ...] = TEMPLATES) -> str:
    return max(
        legal_templates,
        key=lambda template: lookup.mean_utility(
            split="validation",
            condition="clean_loose",
            slice_name="clean",
            template=template,
        ),
    )


def _budget_only(lookup: OutcomeLookup, legal_templates: tuple[str, ...], budget: str) -> str:
    budget_conditions = (
        ("clean_loose", "degraded_loose")
        if budget == "loose"
        else ("clean_tight", "degraded_tight")
    )
    return max(
        legal_templates,
        key=lambda template: lookup.mean_utility(
            split="validation", template=template, budget_conditions=budget_conditions
        ),
    )


def _joint_template(lookup: OutcomeLookup, legal_templates: tuple[str, ...], slice_name: str) -> str:
    return max(
        legal_templates,
        key=lambda template: lookup.mean_utility(
            split="validation", template=template, slice_name=slice_name
        ),
    )


def _nearest_legal_template(proposed: str, legal_templates: tuple[str, ...]) -> str:
    proposed_modalities = TEMPLATE_MODALITIES[proposed]

    def score(template: str) -> tuple[int, int, int]:
        modalities = TEMPLATE_MODALITIES[template]
        overlap = len(proposed_modalities.intersection(modalities))
        size_penalty = -abs(len(proposed_modalities) - len(modalities))
        # Stable registry-order tie-breaker favors simpler earlier templates.
        registry_score = -TEMPLATES.index(template)
        return (overlap, size_penalty, registry_score)

    return max(legal_templates, key=score)

