---
type: other
created: 2026-05-14
exp_id: exp-001
change_id: null
---

# Decision: exp-001 semantic visual rerun

Date: 2026-05-14

## Context

The full MELD `raw_stats` and `cv2_stats + official_concat` runs both completed
and passed protocol, budget-validity, leakage-boundary, q-diagnostic,
corruption-stratification, and post-mask legality checks. Both failed the
benchmark-signal criterion:

- `raw_stats`: `best_single_axis_oracle_regret_dt=0.848`
- `cv2_stats + official_concat`: `best_single_axis_oracle_regret_dt=0.740`

The external results review classified this as negative-but-diagnostic rather
than a protocol failure.

## Decision

Continue `exp-001` for one controlled rerun, but do not treat the current MELD
`cv2_stats` result as a positive benchmark result.

The next run should change only the visual producer:

- keep MELD splits
- keep the 7-template registry: `T`, `A`, `V`, `TA`, `TV`, `AV`, `TAV`
- keep the 2x2 reliability-budget surface
- keep the existing policies
- keep seeds at 3
- keep the existing degradation manifest for the first semantic rerun
- keep the primary metric and the 3 macro-F1 positive threshold
- replace `video_source=cv2_stats` with a frozen semantic visual embedding
  producer

Working run label:

```text
exp-001-meld-semvis-v1
```

## Rationale

The current `cv2_stats` run has a healthy cost surface:

```text
p95 spread=41.887
tight legal templates=T|A|V|TV
TAV-vs-unimodal p95 ratio=2.336
warnings=[]
```

But feasible oracle only reaches `24.550` macro-F1 in `degraded_tight`, while
the best single-axis policy (`budget_only`) reaches `23.810`. This means the
cost axis is valid, but the legal templates do not separate enough in utility.

The most likely causes are current producer weakness and MELD/text dominance,
not a failed protocol. A frozen semantic visual producer is the smallest change
that can distinguish those causes without changing the formalism, dataset,
metric, policy set, or corruption contract.

## Guardrails

- Do not relax the 3 macro-F1 positive threshold for paper-level claims.
- Do not switch datasets before this controlled producer rerun.
- Do not harden corruption before checking whether non-text modalities become
  semantically useful.
- Do not frame the current `cv2_stats` result as positive.
- Keep the feature-level claim boundary unless a separate encoder-inclusive
  profiling path is implemented.

## Triage labels for interpretation

The primary positive standard remains:

```text
best_single_axis_oracle_regret_dt >= 3.0
and >= 1.5x pooled SE
```

For internal triage only, classify future runs as:

- `positive`: primary standard met, or secondary Kendall route clearly met.
- `negative-but-diagnostic`: gates pass and policy differences exist, but
  primary benchmark-signal standard fails.
- `negative-and-uninformative`: gates pass/fail in a way that prevents useful
  interpretation, or all policies collapse without interpretable separation.

The current full `cv2_stats` run is `negative-but-diagnostic`.

## Branching rule after semantic visual rerun

- If semantic visual regret reaches `>=3.0` and rank inversion improves, treat
  exp-001 as having a positive MELD feature-level result.
- If regret is `1.0-3.0` with improved rank inversion, keep MELD as diagnostic
  but do not claim positive benchmark signal.
- If regret remains `<1.0` and text remains dominant, stop using MELD as the
  primary benchmark-signal dataset for exp-001 and consider a less
  text-dominant dataset or a targeted text-degradation stress test.
- If semantic visual improves `V`/`TV`/`AV` but `budget_only` still tracks oracle
  closely, inspect whether the primary metric needs a paired diagnostic rather
  than replacing the primary metric.
