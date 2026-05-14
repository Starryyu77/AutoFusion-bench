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

This is dataset staging progress only. No empirical outcome table has been
generated yet.
