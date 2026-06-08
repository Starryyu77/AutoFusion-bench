# exp-002 Runbook: Diagnosis-to-Action Pilot

## Status

`exp-002` is initialized as the first diagnosis-to-action pilot. It is scoped to
audio-video evidence governance under textual queries. MELD is not the main
substrate for this experiment.

## Experiment question

Can MLLMs act consistently on their own diagnosis of unreliable audio-video
evidence under textual queries?

## Locked boundary

- Execution machine: `ntu-gpu43`
- Remote root: `/usr1/home/s125mdg43_10/projects/AutoFusion-bench`
- Primary data family: AVQA / MUSIC-AVQA-style audio-video QA
- MELD role: diagnostic/control only, not main positive substrate
- Pilot scale: 40 source items and about 160 scored corruption instances
- Main signal: diagnosis-to-action gap
- Required comparison: model action and fixed rule must consume the same frozen
  diagnosis output

## Phase 0: Feasibility gate

Do this before corruption generation or annotation.

### 0.1 Remote repo sync

On local machine:

```bash
rsync -avR \
  .lablock/locks/exp-002.scope.lock \
  .lablock/variables.yaml \
  .lablock/matrices.yaml \
  experiments/exp-002-diag-action-pilot \
  plans/2026-06-08-exp-diagnosis-to-action-pilot.md \
  reviews/2026-06-08-pilot-expert-replies-synthesis.md \
  handoffs/outgoing/2026-06-08-diagnosis-to-action-pilot-v2.md \
  paper/2026-06-08-evidence-governance-story.md \
  ntu-gpu43:/usr1/home/s125mdg43_10/projects/AutoFusion-bench/
```

### 0.2 Remote health check

```bash
ssh ntu-gpu43 '
  cd /usr1/home/s125mdg43_10/projects/AutoFusion-bench &&
  hostname &&
  nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader &&
  df -h /usr1 &&
  git status --short | sed -n "1,120p"
'
```

Expected:

- 4 x RTX A5000 24 GB visible;
- `/usr1` has enough free storage;
- only expected untracked environment dirs such as `.deps/` and `.venv/`;
- exp-002 files exist.

### 0.3 Dataset feasibility

Fill:

- `data/pilot_dataset_feasibility.md`

Minimum pass:

- one AVQA / MUSIC-AVQA-style source can be legally staged on `ntu-gpu43`;
- at least 80-120 candidate source clips can be inspected;
- raw audio and video are available in synchronized media files;
- QA annotations expose question, answer, and source video id;
- question-only / prior-only leakage risk can be tested.

Recommended first source:

- AVQA video package if download succeeds and licensing is acceptable;
- MUSIC-AVQA if AVQA access blocks or if musical audio-video evidence is
  cleaner for the first pilot.

### 0.4 Model feasibility

Fill:

- `data/pilot_model_feasibility.md`

Minimum pass:

- at least 2 models can process audio and video in the same instance;
- structured output can be parsed reliably;
- a 5-clip smoke run is affordable and within model limits;
- audio/video duration and file size limits are clear.

If fewer than 2 audio-video-capable models are available, kill or redesign the
experiment.

## Phase 1: Source item pool

Deliverables:

- `data/pilot_source_candidates.csv`
- `data/pilot_source_items.csv`
- `annotations/pilot_modality_necessity.jsonl`

Selection rule:

- start from 80-120 candidates;
- select 40 source items;
- avoid question-only-solvable items;
- balance audio-necessary, video-necessary, audio-video complementary,
  conflict/temporal-prone, and clean-hard/control buckets.

## Phase 2: Corruption manifest

Deliverables:

- `scripts/build_corruptions.py`
- `data/pilot_corruption_manifest.jsonl`
- `data/corrupted_media/`

Corruption mix:

- 20% simple missing / severe degradation;
- 20% mild / medium degradation;
- 20% temporal mismatch;
- 20% cross-modal conflict;
- 20% clean-hard / corrupted-irrelevant controls.

Every generated instance must have metadata for affected modality, corruption
type, severity, location, relevance, generator family, and seed.

## Phase 3: Human labels

Deliverables:

- `annotations/annotation_guideline_v0.md`
- `annotations/pilot_annotations.jsonl`
- `annotations/adjudication_notes.md`
- `results/annotation_agreement.md`

Recoverability is task-conditioned. If annotators cannot point to evidence, the
instance is not `recoverable`.

## Phase 4: Model runs

Deliverables:

- `outputs/model_diagnoses.jsonl`
- `outputs/model_actions.jsonl`
- `outputs/oracle_route_outputs.jsonl`
- `outputs/oracle_defect_location_outputs.jsonl`

Prompt settings:

1. Direct structured decision
2. Diagnosis-only
3. Model action from frozen diagnosis
4. Fixed rule from frozen diagnosis
5. Oracle route
6. Oracle defect-location
7. Abstention-calibrated

## Phase 5: Metrics

Deliverables:

- `outputs/fixed_rule_actions.jsonl`
- `results/pilot_metrics.csv`
- `results/pilot_metrics.md`
- `results/qualitative_failures.md`
- `results/go_no_go_memo.md`

Primary metrics:

- diagnosis macro-F1;
- recoverability macro-F1;
- policy action accuracy;
- self-inconsistency rate;
- conditional action failure;
- within-diagnosis rule lift;
- false answer rate on unrecoverable cases.

## Validation helper

Validate JSONL files as they are produced:

```bash
python3 experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py \
  --kind source-items \
  data/pilot_source_items.jsonl
```

Supported kinds:

- `source-items`
- `corruption-manifest`
- `annotations`
- `model-diagnoses`
- `model-actions`

## Go/no-go rule

Scale only if the pilot shows a robust diagnosis-to-action gap that is not
explained by synthetic artifacts, question priors, label ambiguity, or trivial
quality detection.
