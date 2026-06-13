# exp-001 ntu-gpu43 bring-up

Date: 2026-05-14

## Scope

Bring the checked-in exp-001 protocol runner onto `ntu-gpu43` and verify that the
repository can execute the fixture smoke on the server.

This was not a MELD run and did not use GPU training.

## GitHub sync

Local `main` was pushed to:

```text
https://github.com/Starryyu77/AutoFusion-bench.git
```

Remote commit used on `ntu-gpu43`:

```text
0fb34e3
```

## Server path

```text
/usr1/home/s125mdg43_10/projects/AutoFusion-bench
```

The repo was cloned fresh because the path was absent in the live snapshot.

## Live snapshot summary

Observed identity:

```text
host: gpu43
user: s125mdg43_10
home: /usr1/home/s125mdg43_10
```

Observed tools:

```text
python3: Python 3.8.10
git: git version 2.25.1
tmux: present
slurm: missing
```

Observed storage:

```text
/usr1: 7.3T size, 3.5T available
/: 879G size, 174G available
```

Observed GPU state at snapshot:

```text
GPU0: busy, about 8937 MiB used, about 91% util
GPU1: mostly idle, about 822 MiB used
GPU2: mostly idle, about 823 MiB used
GPU3: mostly idle, about 1373 MiB used
```

`projects/AutoFusion-bench` was absent before clone. Old project assets remained
absent: `MultiBench`, `AutoFusion_Workspace`, `AutoFusion_Advanced`,
`Orthogonal_ELM_Transformers`, `datasets/Orthogonal_ELM_Transformers`, and
`projects/oelm`.

## Remote verification

Command:

```bash
cd /usr1/home/s125mdg43_10/projects/AutoFusion-bench
python3 -m unittest tests.test_exp001_protocol
```

Result:

```text
Ran 2 tests in 0.006s
OK
```

Command:

```bash
cd /usr1/home/s125mdg43_10/projects/AutoFusion-bench
python3 -m autofusion_bench.exp001.run_decision_surface_pilot \
  --config experiments/exp-001-decision-surface-pilot/config.yaml \
  --fixture-smoke
```

Result:

```text
best_single_axis_oracle_regret_dt=7.000
best_single_axis_policy=clean_best
joint_gap_closure=1.0
protocol_passed=True
benchmark_signal_passed=True
joint_policy_passed=True
```

Remote git state after smoke:

```text
## main...origin/main
```

## Next step

Implement the real MELD data/model producer that emits the six measured tables
consumed by the exp-001 analysis runner.

