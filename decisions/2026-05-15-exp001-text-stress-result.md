---
type: other
created: 2026-05-15
exp_id: exp-001
change_id: null
---

# Decision: interpret final MELD text-stress diagnostic as rank-positive only

Date: 2026-05-15

Experiment: `exp-001` (`decision-surface-pilot`)

## Context

The final MELD diagnostic iteration was run on `ntu-gpu43` using:

```text
MELD + semvis_clip + degradation_profile=text_stress
```

The run preserved the existing feature-level boundary, 7-template registry,
policy set, seeds, and primary metric. The only diagnostic change was stronger
text suppression across degraded slices.

## Result

The run passed protocol and all gates:

```text
protocol_passed=True
benchmark_signal_passed=True
joint_policy_passed=True
budget_validity_gate=True
reliability_proxy_boundary_check=True
q_only_task_classifier=True
q_shuffle_control=True
class_stratified_corruption_check=True
post_mask_budget_legality_contract=True
```

Key metrics:

```text
best_single_axis_oracle_regret_dt=0.350
best_single_axis_policy=reliability_only
feasible_oracle_degraded_tight_macro_f1=13.862
best_single_axis_degraded_tight_macro_f1=13.512
joint_degraded_tight_macro_f1=13.833
joint_gap_closure=0.916
kendall_tau_b_clean_loose_vs_degraded_tight=-0.048
rank_inversion_index=0.524
```

Template ranking changed substantially:

```text
clean_loose best: T=34.708
degraded_tight best: V=13.158
degraded_tight T=9.282
```

## Decision

Classify this run as:

```text
secondary-rank-signal positive
primary-regret negative
```

This is not the same as the desired primary utility-gap evidence. The run shows
that stronger text degradation can create rank inversion and break MELD text
dominance, but the feasible oracle is only `0.350` macro-F1 above the best
single-axis policy.

## Implication

Do not continue tuning MELD in a broad search loop.

MELD can be retained as a protocol-validation and diagnostic case:

- default semvis run: `negative-but-diagnostic`
- text-stress run: rank inversion appears only after a strong diagnostic stress

For a main benchmark-signal result, the next experiment should move toward a
less text-dominant or more naturally multimodal-dependent dataset, or explicitly
frame MELD text-stress as a stress-test slice rather than the primary evidence.

## Claim boundary

Allowed:

```text
On MELD, AutoFusion-Bench exp-001 runs end to end and the final text-stress
diagnostic produces strong rank inversion, but not a meaningful oracle-vs-best
single-axis utility gap.
```

Not allowed:

```text
MELD provides the primary positive utility-gap evidence for AutoFusion-Bench.
```
