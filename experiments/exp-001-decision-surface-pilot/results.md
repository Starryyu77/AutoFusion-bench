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
