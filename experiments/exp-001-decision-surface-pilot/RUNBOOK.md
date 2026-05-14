# exp-001 Runbook

Status: protocol runner and MELD producers implemented. Full `raw_stats` and
`cv2_stats` runs are benchmark-signal negative; the next controlled rerun is
`semvis_clip`.

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

## Current implementation gap

The runner consumes measured tables. The remaining experiment work is the
semantic visual producer rerun on `ntu-gpu43`:

- keep MELD splits, templates, policies, metric, and degradation manifest fixed
- replace only `video_source=cv2_stats` with `video_source=semvis_clip`
- generate real cost, outcome, q-proxy, q-diagnostic, and corruption manifest files
- run the analysis command on the generated files

## MELD staging

Official sources:

- annotations: `declare-lab/MELD`
- feature/model tarball: `MELD.Features.Models.tar.gz`
- raw tarball: `MELD.Raw.tar.gz`

Recommended staging root on `ntu-gpu43`:

```text
/usr1/home/s125mdg43_10/datasets/MELD
```

Stage annotations and feature tarball:

```bash
python3 -m autofusion_bench.exp001.stage_meld \
  --root /usr1/home/s125mdg43_10/datasets/MELD \
  --features \
  --extract \
  --no-check-certificate
```

The official feature/model tarball contains text and audio feature pickles, but
does not contain visual feature pickles. For the first complete tri-modal
producer path, also stage raw MELD and use `--video-source raw_stats`:

```bash
python3 -m autofusion_bench.exp001.stage_meld \
  --root /usr1/home/s125mdg43_10/datasets/MELD \
  --raw \
  --extract \
  --extract-nested-raw \
  --no-check-certificate
```

## MELD table producer

Producer output directory:

```text
experiments/exp-001-decision-surface-pilot/outputs/meld-producer
```

Raw-stat visual producer:

```bash
python3 -m autofusion_bench.exp001.run_meld_table_producer \
  --annotations-dir /usr1/home/s125mdg43_10/datasets/MELD/annotations \
  --features-dir /usr1/home/s125mdg43_10/datasets/MELD/official/features \
  --raw-root /usr1/home/s125mdg43_10/datasets/MELD/official/raw/MELD.Raw \
  --video-source raw_stats \
  --output experiments/exp-001-decision-surface-pilot/outputs/meld-producer \
  --seeds 0,1,2
```

Improved decoded-video producer:

```bash
PYTHONPATH=.deps/opencv python3 -m autofusion_bench.exp001.run_meld_table_producer \
  --annotations-dir /usr1/home/s125mdg43_10/datasets/MELD/annotations \
  --features-dir /usr1/home/s125mdg43_10/datasets/MELD/official/features \
  --raw-root /usr1/home/s125mdg43_10/datasets/MELD/official/raw/MELD.Raw \
  --video-source cv2_stats \
  --audio-source official_concat \
  --output experiments/exp-001-decision-surface-pilot/outputs/meld-producer-cv2 \
  --seeds 0,1,2
```

Frozen semantic visual producer:

```bash
PYTHONPATH=.deps/opencv python3 -m autofusion_bench.exp001.run_meld_table_producer \
  --annotations-dir /usr1/home/s125mdg43_10/datasets/MELD/annotations \
  --features-dir /usr1/home/s125mdg43_10/datasets/MELD/official/features \
  --raw-root /usr1/home/s125mdg43_10/datasets/MELD/official/raw/MELD.Raw \
  --video-source semvis_clip \
  --audio-source official_concat \
  --semvis-model openai/clip-vit-base-patch32 \
  --semvis-frame-count 8 \
  --semvis-batch-frames 64 \
  --semvis-device auto \
  --output experiments/exp-001-decision-surface-pilot/outputs/meld-producer-semvis \
  --seeds 0,1,2
```

`semvis_clip` samples frames from each utterance video, encodes them with a
frozen CLIP image encoder, L2-normalizes frame embeddings, and mean-pools to one
utterance-level visual vector. It is still a feature-level producer: the current
cost table is the cached-feature template-head decision cost, not an end-to-end
deployment latency claim.

Cost profiling uses up to 1024 validation rows per template to reduce Python and
BLAS overhead noise. Small smoke subsets can still fail the budget-validity gate;
use them only to verify producer plumbing, not to judge the budget surface.

Then run the exp-001 analysis runner over the measured tables:

```bash
python3 -m autofusion_bench.exp001.run_decision_surface_pilot \
  --config experiments/exp-001-decision-surface-pilot/config.yaml \
  --cost-table experiments/exp-001-decision-surface-pilot/outputs/meld-producer/cost_table.csv \
  --outcome-table experiments/exp-001-decision-surface-pilot/outputs/meld-producer/outcome_table.csv \
  --q-policy-map experiments/exp-001-decision-surface-pilot/outputs/meld-producer/q_policy_map.csv \
  --q-proxy-table experiments/exp-001-decision-surface-pilot/outputs/meld-producer/q_proxy_table.csv \
  --q-diagnostics experiments/exp-001-decision-surface-pilot/outputs/meld-producer/q_diagnostics.csv \
  --corruption-manifest experiments/exp-001-decision-surface-pilot/outputs/meld-producer/corruption_manifest.csv \
  --output experiments/exp-001-decision-surface-pilot/outputs/meld-analysis
```

`annotation_proxy` exists only for producer plumbing smoke. Do not cite outputs
from `--video-source annotation_proxy` as benchmark evidence.
