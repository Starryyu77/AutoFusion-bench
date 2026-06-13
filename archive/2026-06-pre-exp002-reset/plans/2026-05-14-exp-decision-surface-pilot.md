---
created: 2026-05-14
status: design
parent: none
target_exp_id: exp-001
review_status: conditional_go_after_modifications
---

# Design: decision-surface-pilot

## Hypothesis (one sentence)

If AutoFusion-Bench's 2x2 reliability-budget surface is meaningful, then a frozen feature-level tri-modal template registry will show a measurable degraded-tight decision gap: the feasible oracle will beat the best single-axis policy by >= 3 macro-F1 points and >= 1.5 x pooled standard error within 60 GPU-hours after data preparation on `ntu-gpu43`.

## Primary intervention

Replace a clean-only evaluation surface with a frozen 2x2 reliability-budget decision surface:

- reliability regime: `clean`, `degraded`
- budget tier: `loose`, `tight`
- policy action: choose a fusion template from a frozen registry, with explicit distinction between pre-mask proposals and post-mask legal execution

This is not yet a new model intervention. It is the first benchmark-protocol validation experiment.

## Planned bundle

- Prepare one fresh tri-modal dataset, preferably MELD if acquisition is clean; use MOSEI/MOSI only as a protocol-only fallback.
- Run a <= 2 GPU-hour modality-diversity smoke before the full pilot.
- Use feature-level evaluation first. Do not claim end-to-end deployment latency in this experiment.
- Freeze a 7-template tri-modal registry: `T`, `A`, `V`, `T+A`, `T+V`, `A+V`, `T+A+V`.
- Profile each template for p50 latency, p95 latency, and peak memory on `ntu-gpu43` before outcome evaluation.
- Define loose/tight budget tiers from the cost table only, before reading task outcomes.
- Evaluate policy families: `random_legal`, `clean_best`, `static_full`, `budget_only`, `reliability_only`, `joint`, and `feasible_oracle`.
- Produce an offline outcome table with 4 main condition cells x 4 degraded slices x 7 templates x 3 seeds where applicable.

## Naming

- Suggested shortname: `decision-surface-pilot`
- Variable ID: `var-001` (proposed)
- Canonical variable: `evaluation_surface`
- Variant value: `reliability_budget_2x2`
- Paper label: `Reliability-budget decision surface`
- Matrix ID: `mat-001` (proposed)
- Matrix slug: `decision-surface-protocol-validation`

## Proposed registry delta

```yaml
# .lablock/variables.yaml
variables:
  - var_id: var-001
    canonical_name: evaluation_surface
    paper_label: Reliability-budget decision surface
    code_keys:
      - evaluation.surface
      - protocol.condition_grid
    type: categorical
    role: independent_variable
    allowed_values:
      - clean_only
      - reliability_budget_2x2

# .lablock/matrices.yaml
matrices:
  - matrix_id: mat-001
    slug: decision-surface-protocol-validation
    research_question: Does a reliability-budget condition grid reveal fusion-template decision failures that clean-only or single-axis evaluation hides?
    primary_variable: evaluation_surface
    controlled_axes:
      - dataset
      - template_registry
      - feature_extractor
      - seeds
      - hardware_target
      - budget_definition
      - reliability_proxy_boundary
    likely_paper_target: pilot diagnostic table
```

## Controlled variables

- hardware_target=`ntu-gpu43`
- gpu_type=`NVIDIA RTX A5000 24GB`
- execution_mode=`direct_ssh_tmux`
- work_root=`/usr1/home/s125mdg43_10/projects/AutoFusion-bench`
- old_asset_reuse=`false`
- dataset_priority=`MELD_first`
- fallback_dataset=`MOSEI_or_MOSI_protocol_only`
- modality_set=`text,audio,video`
- template_registry=`T,A,V,T+A,T+V,A+V,T+A+V`
- feature_level=`true`
- reliability_regimes=`clean,degraded`
- degraded_slices=`degraded_text,degraded_audio,degraded_video,mixed_degraded`
- budget_tiers=`loose,tight`
- policy_families=`random_legal,clean_best,static_full,budget_only,reliability_only,joint,feasible_oracle`
- seeds=`3`
- cost_metrics=`p50_latency,p95_latency,peak_memory`
- budget_definition_source=`cost_table_only_before_task_outcomes`

## Condition design

Main cells:

- `clean_loose`
- `clean_tight`
- `degraded_loose`
- `degraded_tight`

The `degraded` cell must contain modality-specific slices:

- `degraded_text`
- `degraded_audio`
- `degraded_video`
- `mixed_degraded`

Corruption assignment must be class-stratified. The goal is not just to make scores drop under noise; it is to create interpretable modality-specific template-choice pressure.

## Budget definition

Before outcome evaluation, profile all 7 templates using the exact inference path used in evaluation.

Budget-validity gate:

- require `max_template_p95 / min_template_p95 >= 1.5`
- prefer `p95(T+A+V) >= 1.25 * max(p95(T), p95(A), p95(V))`

Budget tiers:

- `loose = 1.05 * max_t p95_cost(t)`, so all templates are legal
- `tight` is the smallest p95 threshold such that all unimodal templates are legal, at least one bimodal template is legal, and `T+A+V` is illegal

If feature-level profiling cannot make `T+A+V` illegal under tight, do not run this as a budget experiment. Either add encoder-inclusive profiling or rename the pilot as a feature-head routing pilot.

## Policy definitions

- `random_legal`: randomly select from the current legal template set.
- `clean_best`: select the best template on clean-loose validation; in tight cells, fallback to the best clean-loose legal template.
- `static_full`: prefer `T+A+V`; in tight cells, fallback to the best legal validation template.
- `budget_only`: select the highest validation-utility template from the current legal set; do not use `q(x)`.
- `reliability_only`: use `q(x)` to propose a template without budget mask; record illegal proposals, then fallback to the nearest legal template and report fallback regret.
- `joint`: use both `q(x)` and the legal mask; fit only on train/validation, never on test outcome table.
- `feasible_oracle`: post-hoc upper bound over legal templates; analysis only, not deployable.

## Reliability proxy boundary

Allowed in `q(x)`:

- observed missingness mask
- post-corruption signal statistics
- confidence or entropy from frozen unimodal encoders
- face detection confidence
- estimated SNR
- feature norm or uncertainty proxy

Forbidden in `q(x)`:

- clean/degraded condition label
- affected modality label unless directly observable as missingness
- corruption severity parameter used by the generator
- corruption random seed
- ground-truth class label
- test-set template outcomes
- oracle-selected template

Leakage checks:

- `q_only_task_classifier`: train a cheap classifier from `q(x)` to task label; suspiciously high task performance blocks interpretation.
- `q_shuffle_control`: shuffle `q(x)` within the same condition cell; joint policy should degrade relative to unshuffled `q(x)`.
- `class_stratified_corruption_check`: verify corruption assignment is class-stratified.

## Evaluation

- Primary: `best_single_axis_oracle_regret_dt`.
- Definition: `Utility(feasible_oracle, degraded_tight) - max Utility(policy, degraded_tight)` over `{clean_best, static_full, budget_only, reliability_only}`.
- Positive signal threshold: `>= 3 macro-F1 points` and `>= 1.5 x pooled standard error`.
- Secondary: per-policy oracle regret.
- Secondary: worst single-axis regret.
- Secondary: Kendall tau-b between clean-loose and degraded-tight template rankings.
- Secondary: `pre_mask_illegal_proposal_rate`.
- Secondary: `post_mask_budget_violation_rate`.
- Secondary: `fallback_regret`.
- Secondary: rank inversion index across the 4 main cells and degraded slices.
- Secondary: `joint_gap_closure = (Regret(best_single_axis) - Regret(joint)) / Regret(best_single_axis)`.
- Secondary: total GPU-hours after dataset preparation.
- Seeds: 3, report mean +/- std and pooled standard error where used.

## Predictions

- If H1: `best_single_axis_oracle_regret_dt >= 3` macro-F1 points and `>= 1.5 x pooled SE`; degraded-tight ranking diverges from clean-loose with Kendall tau-b <= 0.3; `reliability_only` has nontrivial pre-mask illegal proposal rate under tight; `joint` closes >= 30% of the best-single-axis oracle gap with post-mask violation <= 1%.
- If H0: clean-loose ranking predicts degraded-tight with Kendall tau-b >= 0.7; `best_single_axis_oracle_regret_dt < 1.5` macro-F1 points or below noise threshold; single-axis policies show no meaningful budget or reliability blind spots.
- Surprise: `T+A+V` remains legal and best under the tight budget in all cells, or the reliability proxy makes the joint policy nearly oracle-perfect; either outcome means the benchmark surface is too easy, too cheap, or leaky.

## Kill criteria

- Dataset acquisition/preparation blocks for more than 1 calendar day without a confirmed path to MELD or a declared fallback.
- MELD modality-diversity smoke fails: neither `T+A+V` beats `T` by >= 1.5 macro-F1 on clean-loose validation, nor A/V/bimodal templates become useful in text-degraded validation, nor template ranking changes across any modality-specific degraded slice.
- Server setup smoke exceeds 4 GPU-hours or cannot run a single template forward pass.
- Feature extraction or loader shape/split contracts remain unresolved after 12 wall-clock hours.
- Budget-validity gate fails and no encoder-inclusive profiling fallback is approved.
- Outcome table generation exceeds 60 GPU-hours after dataset preparation.
- Calendar time exceeds 3 days after dataset preparation.
- Tight budget is defined after seeing task outcomes.
- Post-mask legality filter permits an over-budget executed template.
- Seed instability exceeds 5 macro-F1 points for most templates and prevents ranking interpretation.
- Leakage checks show `q(x)` exposes label, condition, severity, or test outcome information strongly enough to invalidate policy comparison.

## Success criteria

Protocol success:

- Complete server snapshot, dataset manifest, split hashes, corruption manifest, template registry, and budget tier definitions.
- Complete measured cost table with p50 latency, p95 latency, and peak memory for every template.
- Complete outcome table for all main condition cells, degraded slices, 7 templates, and 3 seeds.
- Pass budget-validity and leakage gates.

Benchmark-signal success:

- `best_single_axis_oracle_regret_dt >= 3` macro-F1 points and `>= 1.5 x pooled SE`, or Kendall tau-b between clean-loose and degraded-tight rankings <= 0.3.

Joint-policy success:

- `joint_gap_closure >= 30%`.
- `post_mask_budget_violation_rate <= 1%`.

The pilot can still be useful if protocol and benchmark-signal success pass but joint-policy success fails; that outcome means the benchmark is informative but the joint reference policy needs work.

## Probes (optional)

- `server_snapshot` | `bash ~/.codex/skills/ntu-gpu43-operator/scripts/live-snapshot.sh ntu-gpu43` | verify this is direct GPU43, not Slurm, and record GPU/storage state.
- `old_asset_absence` | check that old `MultiBench`, `AutoFusion_Workspace`, `Orthogonal_ELM_Transformers`, and `projects/oelm` paths are absent | prevent accidental reuse of stale experiments.
- `split_manifest_contract` | verify train/val/test split hashes before training | avoid silent split drift.
- `budget_validity_gate` | assert template p95 cost spread and tight-budget legality rules before outcome evaluation | prevent pseudo-budget experiments.
- `budget_legality_contract` | assert executed template measured cost <= active budget tier | prevent invalid policy metrics.
- `reliability_proxy_boundary_check` | assert forbidden fields are absent from `q(x)` | prevent direct leakage.
- `q_only_task_classifier` | train a cheap classifier from `q(x)` to task label | detect label leakage through reliability proxies.
- `q_shuffle_control` | shuffle `q(x)` within condition cell and re-evaluate joint policy | detect unused or overly dominant proxy/budget shortcuts.
- `class_stratified_corruption_check` | verify corruption assignment is class-stratified | prevent q-to-label correlation through corruption imbalance.

## Suggested CLI invocation

```bash
lablock exp-init decision-surface-pilot \
  --parent=none \
  --hypothesis="A frozen feature-level tri-modal reliability-budget surface reveals a degraded-tight decision gap: feasible oracle beats the best single-axis policy by >=3 macro-F1 points and >=1.5x pooled SE within 60 GPU-hours after data preparation on ntu-gpu43." \
  --config="hardware.target=ntu-gpu43,hardware.gpu_type=RTX_A5000_24GB,execution.mode=direct_ssh_tmux,work_root=/usr1/home/s125mdg43_10/projects/AutoFusion-bench,dataset.priority=MELD_first,dataset.fallback=MOSEI_or_MOSI_protocol_only,protocol.feature_level=true,protocol.reliability_regimes=clean|degraded,protocol.degraded_slices=degraded_text|degraded_audio|degraded_video|mixed_degraded,protocol.budget_tiers=loose|tight,protocol.templates=T|A|V|TA|TV|AV|TAV,protocol.policies=random_legal|clean_best|static_full|budget_only|reliability_only|joint|feasible_oracle,protocol.seeds=3,protocol.primary_metric=best_single_axis_oracle_regret_dt,protocol.budget_definition=cost_table_only_before_outcomes" \
  --control-added="plans/2026-05-14-exp-decision-surface-pilot.md,infra/gpu/2026-05-14-ntu-gpu43-cleanup.md,handoffs/incoming/2026-05-14-decision-surface-pilot-review.md" \
  --control-modified="evaluation_surface,dataset_manifest,corruption_manifest,template_registry,cost_table,outcome_table,policy_diagnostics,reliability_proxy_boundary,leakage_checks" \
  --matrix-id="mat-001" \
  --variable-id="var-001" \
  --canonical-variable="evaluation_surface" \
  --variant-value="reliability_budget_2x2" \
  --paper-label="Reliability-budget decision surface" \
  --file-invariant="infra/gpu/2026-05-14-ntu-gpu43-cleanup.md:server cleanup and execution boundary" \
  --kill="dataset acquisition blocks >1 day,MELD modality-diversity smoke fails,setup smoke exceeds 4 GPU-hours,budget-validity gate fails,outcome table exceeds 60 GPU-hours after data prep,calendar exceeds 3 days after data prep,tight budget defined after task outcomes,post-mask legality permits over-budget execution,seed instability exceeds 5 macro-F1 points for most templates,leakage checks invalidate q" \
  --success="protocol artifacts complete,cost table complete,outcome table complete,budget-validity and leakage gates pass,best_single_axis_oracle_regret_dt >=3 macro-F1 and >=1.5x pooled SE or Kendall tau-b <=0.3,joint_gap_closure >=30%,post_mask_budget_violation_rate <=1%" \
  --stage
```

## What's next

- Run `/lab-review --as=reviewer2 plans/2026-05-14-exp-decision-surface-pilot.md` if another review pass is needed.
- If this conditional-go version is accepted, run the suggested `lablock exp-init` command and continue with folder-isolated execution via `/lab-exp-run`.
