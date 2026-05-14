---
id: exp-001
parent: null
status: planned
created: '2026-05-14'
hypothesis: >-
  A frozen feature-level tri-modal reliability-budget surface reveals a
  degraded-tight decision gap: feasible oracle beats the best single-axis policy
  by >=3 macro-F1 points and >=1.5x pooled SE within 60 GPU-hours after data
  preparation on ntu-gpu43.
related_claims: []
forked_from: null
fork_reason: null
drift_commit: null
naming:
  matrix_id: mat-001
  variable_id: var-001
  canonical_variable: evaluation_surface
  variant_value: reliability_budget_2x2
  paper_label: Reliability-budget decision surface
---
# exp-001: decision-surface-pilot

## Hypothesis

A frozen feature-level tri-modal reliability-budget surface reveals a degraded-tight decision gap: feasible oracle beats the best single-axis policy by >=3 macro-F1 points and >=1.5x pooled SE within 60 GPU-hours after data preparation on ntu-gpu43.

## What changed

- Added: plans/2026-05-14-exp-decision-surface-pilot.md
- Added: infra/gpu/2026-05-14-ntu-gpu43-cleanup.md
- Added: handoffs/incoming/2026-05-14-decision-surface-pilot-review.md
- Modified: evaluation_surface
- Modified: dataset_manifest
- Modified: corruption_manifest
- Modified: template_registry
- Modified: cost_table
- Modified: outcome_table
- Modified: policy_diagnostics
- Modified: reliability_proxy_boundary
- Modified: leakage_checks

## Naming

- Matrix: mat-001
- Variable ID: var-001
- Canonical variable: evaluation_surface
- Variant value: reliability_budget_2x2
- Paper label: Reliability-budget decision surface

## Success criteria

- protocol artifacts complete
- cost table complete
- outcome table complete
- budget-validity and leakage gates pass
- best_single_axis_oracle_regret_dt >=3 macro-F1 and >=1.5x pooled SE or Kendall tau-b <=0.3
- joint_gap_closure >=30%
- post_mask_budget_violation_rate <=1%

## Kill criteria

- dataset acquisition blocks >1 day
- MELD modality-diversity smoke fails
- setup smoke exceeds 4 GPU-hours
- budget-validity gate fails
- outcome table exceeds 60 GPU-hours after data prep
- calendar exceeds 3 days after data prep
- tight budget defined after task outcomes
- post-mask legality permits over-budget execution
- seed instability exceeds 5 macro-F1 points for most templates
- leakage checks invalidate q
