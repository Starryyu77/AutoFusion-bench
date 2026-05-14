---
type: other
created: 2026-05-14
exp_id: exp-001
change_id: null
---

# Decision: exp-001 conditional-go review updates

Date: 2026-05-14

## Context

An external design review of `plans/2026-05-14-exp-decision-surface-pilot.md` returned a conditional-go recommendation: the pilot direction is valid, but the experiment should not run as originally drafted.

## Decision

Accept the reviewer's six blocking concerns before creating `exp-001`:

- add `clean_best` and `static_full` baselines
- split pre-mask illegal proposals from post-mask executed budget violations
- add a feature-level budget-validity gate before outcome evaluation
- make degraded conditions modality-specific
- replace `max_oracle_feasible_regret_points` with `best_single_axis_oracle_regret_dt`
- write hard reliability-proxy information boundaries and leakage checks

Also split success criteria into protocol success, benchmark-signal success, and joint-policy success.

## Rationale

Without these changes, a completed pilot could be hard to interpret: it might not directly test clean-only blind spots, could report meaningless budget violation rates after legality filtering, could use a pseudo-budget with no measurable cost spread, or could leak degradation/label information through `q(x)`.

## Status

Applied to the draft design file. No `scope.lock` has been created yet.
