# exp-001 Runbook

Status: protocol runner implemented; empirical MELD run not started.

## Local protocol smoke

This command validates the runner against checked-in fixture data. The fixture is
not empirical evidence.

```bash
python -m autofusion_bench.exp001.run_decision_surface_pilot \
  --config experiments/exp-001-decision-surface-pilot/config.yaml \
  --fixture-smoke
```

Expected output includes:

```text
best_single_axis_oracle_regret_dt=7.000
protocol_passed=True
benchmark_signal_passed=True
joint_policy_passed=True
```

Fixture outputs are written under:

```text
experiments/exp-001-decision-surface-pilot/outputs/fixture-smoke/
```

`outputs/` is gitignored.

## Unit tests

```bash
python -m unittest tests.test_exp001_protocol
```

## Real-run input contract

The real exp-001 analysis command requires these files:

```text
cost_table.csv
outcome_table.csv
q_policy_map.csv
q_proxy_table.csv
q_diagnostics.csv
corruption_manifest.csv
```

Run shape:

```bash
python -m autofusion_bench.exp001.run_decision_surface_pilot \
  --config experiments/exp-001-decision-surface-pilot/config.yaml \
  --cost-table <cost_table.csv> \
  --outcome-table <outcome_table.csv> \
  --q-policy-map <q_policy_map.csv> \
  --q-proxy-table <q_proxy_table.csv> \
  --q-diagnostics <q_diagnostics.csv> \
  --corruption-manifest <corruption_manifest.csv> \
  --output experiments/exp-001-decision-surface-pilot/outputs/<run-id>
```

## Schemas

`cost_table.csv`

```text
template,p50_ms,p95_ms,peak_memory_mb
```

Required templates:

```text
T,A,V,TA,TV,AV,TAV
```

`outcome_table.csv`

```text
split,condition,slice,template,seed,macro_f1
```

Valid splits:

```text
validation,test
```

Valid conditions:

```text
clean_loose,clean_tight,degraded_loose,degraded_tight
```

Clean conditions must use `slice=clean`. Degraded conditions must use:

```text
degraded_text,degraded_audio,degraded_video,mixed_degraded
```

`q_policy_map.csv`

```text
slice,proposed_template
```

Additional metadata columns are allowed.

`q_proxy_table.csv`

Must omit forbidden fields: labels, clean/degraded condition, affected modality
labels unless directly observable as missingness, corruption severity, random
seed, test outcomes, and oracle-selected template.

`q_diagnostics.csv`

```text
check,value,threshold,passed,notes
```

Required checks:

```text
q_only_task_classifier
q_shuffle_control
```

`corruption_manifest.csv`

```text
split,label,degraded_slice
```

The runner verifies that degraded-slice assignment is class-stratified for each
split and label.

## Gate order

1. Validate config boundary: `ntu-gpu43` and `direct_ssh_tmux`.
2. Validate 7-template cost table.
3. Build budget tiers from p95 cost table only.
4. Enforce budget-validity gate:
   - `max_template_p95 / min_template_p95 >= 1.5`
   - all unimodal templates legal under tight
   - at least one bimodal template legal under tight
   - `TAV` illegal under tight
5. Validate complete validation/test outcome table.
6. Validate reliability-proxy boundary and leakage diagnostics.
7. Evaluate policies and enforce post-mask legality.
8. Report `best_single_axis_oracle_regret_dt`, Kendall tau-b, fallback regret,
   illegal proposal rate, and joint gap closure.

## Next implementation gap

The runner consumes measured tables. The remaining work is the data/model
producer on `ntu-gpu43`:

- clone/sync the repo to `/usr1/home/s125mdg43_10/projects/AutoFusion-bench`
- acquire or stage MELD
- build feature extraction and template-head training
- generate real cost, outcome, q-proxy, q-diagnostic, and corruption manifest
  files
- run this analysis command on the generated files

