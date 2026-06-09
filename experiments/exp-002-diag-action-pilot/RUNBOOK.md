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
- `annotations/screening_scoring_guideline_v0.md`
- `annotations/screening_scoring_guideline_v1.md`
- `annotations/annotation_task_protocol_v1.md`
- `annotations/smoke_annotation_sheet_v1.draft.jsonl`
- `annotations/smoke_annotation_sheet_v1.draft.csv`
- `annotations/pilot_annotations.local.jsonl`
- `annotations/pilot_annotations.jsonl`
- `annotations/adjudication_notes.md`
- `results/annotation_agreement.md`
- `results/pilot_annotation_local_validation.md`

Use `screening_scoring_guideline_v1.md` for the current annotation standard.
The v0 files are traceability drafts only. Recoverability is task-conditioned.
If annotators cannot point to evidence, the instance is not `recoverable`.
Headline scoring should use answerable vs unanswerable cases; partial cases go
to risk-sensitive or ambiguous analysis.

Use `annotation_task_protocol_v1.md` as the annotator-facing task protocol. It
defines the required annotation order, allowed values, adjudication triggers,
headline inclusion rules, and the 5-clip smoke annotation gate.

Build the draft annotation sheet from source and corruption manifests:

```bash
python3 experiments/exp-002-diag-action-pilot/scripts/build_annotation_sheet_v1.py \
  --source-items experiments/exp-002-diag-action-pilot/data/smoke_source_items.jsonl \
  --corruption-manifest experiments/exp-002-diag-action-pilot/data/smoke_corruption_manifest.jsonl \
  --output-jsonl experiments/exp-002-diag-action-pilot/annotations/smoke_annotation_sheet_v1.draft.jsonl \
  --output-csv experiments/exp-002-diag-action-pilot/annotations/smoke_annotation_sheet_v1.draft.csv
```

The generated smoke sheet is not gold. It uses generator metadata only as hints
and marks rows as `needs_human_review`.

If an annotator edits the CSV directly, convert it back to scorer-compatible
JSONL with:

```bash
python3 experiments/exp-002-diag-action-pilot/scripts/annotation_csv_to_jsonl_v1.py \
  --input-csv experiments/exp-002-diag-action-pilot/annotations/smoke_annotation_sheet_v1.reviewed.csv \
  --base-jsonl experiments/exp-002-diag-action-pilot/annotations/smoke_annotation_sheet_v1.draft.jsonl \
  --output-jsonl experiments/exp-002-diag-action-pilot/annotations/smoke_annotations_v1.gold.jsonl \
  --strict-gold
```

`--strict-gold` should fail if accepted rows still contain unresolved headline
fields.

### 3.1 Local annotation app

A configurable local review app lives at:

`experiments/exp-002-diag-action-pilot/annotation_app/`

The reusable AutoFusion annotation skill and human/AI data spec live at:

`skills/autofusion-annotation/`

Use it when manual review needs synchronized media playback, bbox evidence,
audio/video time spans, and less error-prone v1 field editing than a CSV sheet.
It stores local progress in SQLite and exports scorer-compatible JSONL.
Docker is optional; the default setup path is local Python venv + npm so each
annotator can map their own local media directory.

The current local 5-row website export is:

`annotations/pilot_annotations.local.jsonl`

It passes the annotation validator and is now a partial smoke gold export. Two
rows enter headline scoring with `instance_decision=accept`; three rows remain
adjudication-only. Remaining blockers are one source-level adjudication row, one
partially answerable row, and the unanswerable audio-mute row whose oracle
policy still selects audio instead of abstaining.
See `results/pilot_annotation_local_validation.md`.

Website `review_status=reviewed` means only that the row has been inspected. A
row enters scorer headline tables only when exported as `instance_decision=accept`,
which requires `source_decision=accept`, reviewed status,
`main_answerability=answerable|unanswerable`, high/medium confidence, and
`risk_sensitive=false`.

Clean-source gate rule: if the original uncorrupted media does not clearly
support the gold answer, reject or adjudicate the source before reasoning about
the corrupted instance. This prevents dataset noise from being mistaken for
model failure under corruption.

Check local configuration:

```bash
cd experiments/exp-002-diag-action-pilot/annotation_app
./scripts/check_config.py
```

Recommended first setup:

```bash
cp .env.example .env
# edit AUTOFUSION_REPO_ROOT, ANNOTATION_DB_PATH, and ANNOTATION_MEDIA_MAP
./scripts/bootstrap_local.sh
.venv/bin/python scripts/check_config.py --require-runtime-deps
.venv/bin/python scripts/smoke_test.py
./scripts/run_local.sh
```

Open `http://127.0.0.1:8000`. Docker remains available via
`docker compose up --build` when the annotator prefers a container.

Latest reusable smoke evidence is recorded at:

`experiments/exp-002-diag-action-pilot/results/annotation_app_smoke.md`

For CLI-only smoke:

```bash
cd experiments/exp-002-diag-action-pilot/annotation_app/backend
python3 -m app.cli --db ../state/smoke.sqlite import-sheet \
  --sheet ../../annotations/smoke_annotation_sheet_v1.draft.jsonl \
  --annotator local-smoke
python3 -m app.cli --db ../state/smoke.sqlite export \
  --output ../../annotations/pilot_annotations.local-smoke.jsonl
python3 ../../scripts/validate_jsonl.py \
  --kind annotations \
  ../../annotations/pilot_annotations.local-smoke.jsonl
```

For multiple local annotator exports, use:

```bash
python3 -m app.cli merge \
  --annotations ../../annotations/pilot_annotations.annotator_a.jsonl ../../annotations/pilot_annotations.annotator_b.jsonl \
  --output ../../annotations/pilot_annotations.merged.jsonl \
  --report ../../results/annotation_disagreements.md
```

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
- `results/pilot_per_instance.jsonl`
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

Run v1 scorer:

```bash
python3 experiments/exp-002-diag-action-pilot/scripts/score_v1_metrics.py \
  --annotations experiments/exp-002-diag-action-pilot/annotations/pilot_annotations.jsonl \
  --diagnoses experiments/exp-002-diag-action-pilot/outputs/model_diagnoses.jsonl \
  --actions experiments/exp-002-diag-action-pilot/outputs/model_actions.jsonl \
  --fixed-rule-actions experiments/exp-002-diag-action-pilot/outputs/fixed_rule_actions.jsonl \
  --per-instance-jsonl experiments/exp-002-diag-action-pilot/results/pilot_per_instance.jsonl \
  --metrics-csv experiments/exp-002-diag-action-pilot/results/pilot_metrics.csv \
  --metrics-md experiments/exp-002-diag-action-pilot/results/pilot_metrics.md
```

Scoring smoke fixture:

```bash
python3 experiments/exp-002-diag-action-pilot/scripts/score_v1_metrics.py \
  --annotations experiments/exp-002-diag-action-pilot/fixtures/scoring_v1_annotations.jsonl \
  --diagnoses experiments/exp-002-diag-action-pilot/fixtures/scoring_v1_diagnoses.jsonl \
  --actions experiments/exp-002-diag-action-pilot/fixtures/scoring_v1_model_actions.jsonl \
  --fixed-rule-actions experiments/exp-002-diag-action-pilot/fixtures/scoring_v1_fixed_rule_actions.jsonl \
  --per-instance-jsonl experiments/exp-002-diag-action-pilot/results/scoring_smoke_per_instance.jsonl \
  --metrics-csv experiments/exp-002-diag-action-pilot/results/scoring_smoke_metrics.csv \
  --metrics-md experiments/exp-002-diag-action-pilot/results/scoring_smoke_metrics.md
```

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
