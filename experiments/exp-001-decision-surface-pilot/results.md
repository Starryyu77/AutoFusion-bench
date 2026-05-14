# Results: exp-001

Status: protocol runner implemented; empirical MELD run not started.

## 2026-05-14 protocol fixture smoke

Command:

```bash
python -m autofusion_bench.exp001.run_decision_surface_pilot \
  --config experiments/exp-001-decision-surface-pilot/config.yaml \
  --fixture-smoke
```

Observed local output:

```text
best_single_axis_oracle_regret_dt=7.000
best_single_axis_policy=clean_best
joint_gap_closure=1.0
protocol_passed=True
benchmark_signal_passed=True
joint_policy_passed=True
```

Interpretation: this is a fixture smoke only. It validates the implemented
budget gate, policy evaluation, leakage checks, and metric reporting. It is not
an empirical AutoFusion-Bench result and must not be cited as benchmark evidence.

## Implemented artifacts

- `autofusion_bench.exp001.run_decision_surface_pilot`
- cost-table budget-validity gate
- complete outcome-table validation
- policy evaluator for all exp-001 planned policies
- primary metric `best_single_axis_oracle_regret_dt`
- `pre_mask_illegal_proposal_rate`, `post_mask_budget_violation_rate`, and
  `fallback_regret`
- reliability-proxy boundary check
- q-only and q-shuffle diagnostic ingestion
- class-stratified corruption-manifest check
- local fixture and unit tests

## Remaining before empirical run

- sync/clone repo to `ntu-gpu43`
- acquire or stage MELD
- implement data/model producer for feature extraction and template-head
  evaluation
- generate real cost, outcome, q-proxy, q-diagnostic, and corruption manifest
  files
- run the analysis runner on measured tables

## 2026-05-14 ntu-gpu43 fixture smoke

Server path:

```text
/usr1/home/s125mdg43_10/projects/AutoFusion-bench
```

Remote commit:

```text
0fb34e3
```

Remote checks:

```bash
python3 -m unittest tests.test_exp001_protocol
python3 -m autofusion_bench.exp001.run_decision_surface_pilot \
  --config experiments/exp-001-decision-surface-pilot/config.yaml \
  --fixture-smoke
```

Observed fixture output matched local smoke:

```text
best_single_axis_oracle_regret_dt=7.000
best_single_axis_policy=clean_best
joint_gap_closure=1.0
protocol_passed=True
benchmark_signal_passed=True
joint_policy_passed=True
```

Interpretation: server code bring-up is complete. This is still a fixture smoke,
not a MELD empirical result.

## 2026-05-14 MELD staging progress

Staged on `ntu-gpu43`:

```text
/usr1/home/s125mdg43_10/datasets/MELD/annotations
/usr1/home/s125mdg43_10/datasets/MELD/official/MELD.Features.Models.tar.gz
/usr1/home/s125mdg43_10/datasets/MELD/official/features
```

Observed annotation row counts:

```text
dev_sent_emo.csv: 1110 lines
test_sent_emo.csv: 2611 lines
train_sent_emo.csv: 9990 lines
```

Official feature tarball:

```text
size: 880M
sha256: 59131c6904ab1272912c6ebec7873524e6f90bce842b333bc27f02411718b2c3
```

Inspection: official feature tarball contains text/audio/bimodal feature pickles
and model weights, but no visual feature pickles. `MELD.Raw.tar.gz` download was
started in remote tmux session `meld_raw_download` to support the first complete
tri-modal producer path via raw MP4 file-stat visual features.

Raw staging completed:

```text
raw archive size: 10878146150 bytes
raw archive sha256: a56b4407d574195cbce470d86f9c9d72fcfea59b0e34502ecd4babee4a5c613e
raw root: /usr1/home/s125mdg43_10/datasets/MELD/official/raw/MELD.Raw
mp4 files observed: 15908
```

This is dataset staging progress only. No empirical outcome table has been
generated yet.

## 2026-05-14 producer plumbing smoke

Remote command:

```bash
python3 -m autofusion_bench.exp001.run_meld_table_producer \
  --annotations-dir /usr1/home/s125mdg43_10/datasets/MELD/annotations \
  --features-dir /usr1/home/s125mdg43_10/datasets/MELD/official/features \
  --video-source annotation_proxy \
  --output experiments/exp-001-decision-surface-pilot/outputs/meld-producer-plumbing-smoke \
  --seeds 0 \
  --max-train-samples 700 \
  --max-eval-samples 280
```

Observed:

```text
records={'train': 700, 'validation': 280, 'test': 280}
feature_sources={
  'text': '.../text_glove_average_emotion.pkl',
  'audio': '.../audio_embeddings_feature_selection_emotion.pkl',
  'video': 'annotation_proxy_not_empirical_visual'
}
```

Interpretation: producer plumbing can read staged MELD annotations and official
text/audio features and can emit all six table schemas. This output is not
benchmark evidence because visual features came from `annotation_proxy`.

## 2026-05-14 full MELD raw-stats producer

Producer command:

```bash
python3 -m autofusion_bench.exp001.run_meld_table_producer \
  --annotations-dir /usr1/home/s125mdg43_10/datasets/MELD/annotations \
  --features-dir /usr1/home/s125mdg43_10/datasets/MELD/official/features \
  --raw-root /usr1/home/s125mdg43_10/datasets/MELD/official/raw/MELD.Raw \
  --video-source raw_stats \
  --output experiments/exp-001-decision-surface-pilot/outputs/meld-producer \
  --seeds 0,1,2
```

Producer output:

```text
records={'train': 9989, 'validation': 1109, 'test': 2610}
feature_sources={
  'text': '.../text_glove_average_emotion.pkl',
  'audio': '.../audio_embeddings_feature_selection_emotion.pkl',
  'video': 'raw_stats:/usr1/home/s125mdg43_10/datasets/MELD/official/raw/MELD.Raw'
}
```

Generated measured tables:

```text
cost_table.csv: 8 lines
outcome_table.csv: 421 lines
q_policy_map.csv: 6 lines
q_proxy_table.csv: 3720 lines
q_diagnostics.csv: 3 lines
corruption_manifest.csv: 3720 lines
```

Analysis command consumed those six tables and completed:

```text
protocol_passed=True
benchmark_signal_passed=False
joint_policy_passed=True
best_single_axis_oracle_regret_dt=0.848
best_single_axis_policy=clean_best
pooled_standard_error=0.215
kendall_tau_b_clean_loose_vs_degraded_tight=0.810
joint_gap_closure=1.0
```

Budget gate:

```text
p95 spread=12.666
tight=2.064 ms
loose=2.342 ms
tight legal templates=T|A|V|TA|TV|AV
TAV illegal under tight
warning: TAV-vs-unimodal p95 ratio=1.080 < preferred 1.250
```

Leakage and legality gates passed:

```text
q_only_task_classifier=18.62 <= 40.0
q_shuffle_control=1.29 >= 0.5
post_mask_budget_violation_rate=0
```

Template means on test:

```text
clean_loose: T=34.708, TV=32.860, TAV=20.832, TA=19.882, AV=10.527, A=10.278, V=8.211
degraded_tight: T=23.810, TV=19.439, TA=16.159, TAV=13.868, A=9.063, AV=6.538, V=5.494
```

Interpretation:

- The protocol runner and full measured-table producer are functional.
- This first raw-stats feature-level MELD run does not pass the benchmark-signal
  criterion because `best_single_axis_oracle_regret_dt` is far below 3 F1 and
  clean-vs-degraded ranking remains similar.
- The likely cause is text dominance plus weak visual signal from raw file-stat
  features. This result should not be used as a positive AutoFusion-Bench claim.
- Next experimental step should improve the visual/audio feature producer or
  switch to a stronger visual feature source before treating MELD as the paper
  pilot.
