---
type: other
created: 2026-05-15
exp_id: exp-001
change_id: null
---

# Decision: one final MELD diagnostic iteration for exp-001

Date: 2026-05-15

Experiment: `exp-001` (`decision-surface-pilot`)

## Context

The 2026-05-14 external-style handoff reply for the semantic visual run was
processed and saved at:

```text
handoffs/incoming/2026-05-14-exp-001-semvis-next-step.md
```

The reply agrees with the current repo interpretation:

- `exp-001` protocol validity is intact.
- The full MELD `raw_stats`, `cv2_stats`, and `semvis_clip` runs are
  operationally successful but benchmark-signal negative.
- The latest `semvis_clip` run improves the primary regret from `0.740` to
  `1.869`, but remains below the `3.0` macro-F1 positive threshold.
- `T` remains dominant in both `clean_loose` and `degraded_tight`.
- The result is `negative-but-diagnostic`, not positive benchmark evidence.

## Decision

Keep `exp-001`, but do not claim the current MELD runs as positive
AutoFusion-Bench evidence.

Run at most one more MELD diagnostic iteration:

```text
MELD + semvis_clip + targeted stronger text degradation
```

Everything else should stay as fixed as possible:

- feature-level boundary
- MELD splits
- 7-template registry: `T|A|V|TA|TV|AV|TAV`
- 2x2 reliability-budget surface
- current policy set
- seeds `0,1,2`
- primary metric `best_single_axis_oracle_regret_dt`
- paper-level `3.0` macro-F1 threshold

## Rationale

The semantic visual producer helped but did not break the text-dominant surface.
The remaining highest-information test is whether stronger targeted text
degradation can create modality-specific rank inversion under the same feature
producer and protocol.

This should be treated as a final MELD diagnostic fork, not as a search loop.
If it fails, stop using MELD as the primary benchmark-signal dataset for
`exp-001` and move to a less text-dominant or more naturally multimodal dataset.

## Go criteria

The final MELD diagnostic route can be considered positive only if:

```text
best_single_axis_oracle_regret_dt >= 3.0
and best_single_axis_oracle_regret_dt >= 1.5 x pooled SE
```

or:

```text
Kendall tau-b(clean_loose, degraded_tight) <= 0.3
```

and:

```text
joint_gap_closure >= 30%
post_mask_budget_violation_rate <= 1%
protocol and leakage gates pass
```

## No-go criteria

Stop treating MELD as the primary benchmark-signal dataset if the final
diagnostic run shows:

```text
best_single_axis_oracle_regret_dt < 3.0
T remains stable best template in degraded_tight
rank_inversion_index remains low
```

The current semvis budget warning:

```text
TAV-vs-unimodal p95 ratio = 1.140 < preferred 1.250
```

is recorded as a caveat, not as an invalidation.

## Claim boundary

The current allowable claim is:

```text
exp-001 has completed MELD feature-level protocol validation. The pipeline,
tables, budget gate, leakage checks, and policy evaluator run end to end, but
MELD under the current producers/degradation is benchmark-signal negative.
```

Do not write:

```text
MELD proves AutoFusion-Bench exposes a strong reliability-budget decision gap.
```
