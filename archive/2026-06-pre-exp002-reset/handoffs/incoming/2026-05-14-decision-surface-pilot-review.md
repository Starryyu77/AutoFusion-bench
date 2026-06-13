# Incoming Review: decision-surface-pilot-review

Received: 2026-05-14

## Verdict

Conditional go. The reviewer says the pilot direction is right, but the current design should not be run as-is. Six blocking issues should be fixed before `lablock exp-init`.

## Blocking concerns to adopt

1. Add real clean-only baselines:
   - `clean_best`
   - `static_full`

2. Resolve the conflict between legality filtering and budget violation:
   - report `pre_mask_illegal_proposal_rate`
   - report `post_mask_budget_violation_rate`
   - report `fallback_regret`

3. Add a budget-validity gate for the feature-level budget:
   - profile all 7 templates before outcome evaluation
   - require `max_template_p95 / min_template_p95 >= 1.5`
   - prefer `p95(T+A+V) >= 1.25 * max(p95(T), p95(A), p95(V))`
   - define `loose` and `tight` from cost table only, before task outcomes
   - if `T+A+V` cannot be illegal under tight, rename to feature-head routing pilot or add encoder-inclusive profiling

4. Make degraded condition modality-specific:
   - `degraded_text`
   - `degraded_audio`
   - `degraded_video`
   - `mixed_degraded`

5. Replace the primary metric:
   - from `max_oracle_feasible_regret_points`
   - to `best_single_axis_oracle_regret_dt`
   - require `>= 3 macro-F1 points` and `>= 1.5 x pooled standard error`

6. Freeze reliability-proxy information boundaries:
   - allow observed missingness, post-corruption signal stats, frozen encoder confidence/entropy, face detection confidence, estimated SNR, feature norm/uncertainty
   - forbid condition labels, affected modality labels unless directly observed as missingness, generator severity, corruption random seed, ground-truth labels, test outcomes, and oracle-selected templates
   - add q-only task classifier check
   - add q-shuffle control
   - require class-stratified corruption assignment

## Non-blocking improvements to adopt

- Keep 2x2 as the first wedge; do not expand to 3x3 yet.
- Keep 7-template registry; do not turn the pilot into architecture search.
- Keep Kendall tau <= 0.3, but make it secondary.
- Do not require `joint` to be within 2 F1 of oracle as a pilot success condition.
- Add `joint_gap_closure`.
- Add MELD modality-diversity smoke test before the full 7 x 3 pilot.

## Updated recommendation

Go after modifications. The exp-001 goal should be:

> Validate whether a frozen feature-level tri-modal template registry exhibits a measurable decision gap under a 2x2 reliability-budget surface, before scaling to the full AutoFusion-Bench paper package.
