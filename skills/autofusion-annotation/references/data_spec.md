# AutoFusion Annotation Data and Workflow Spec

Status: v1 for AutoFusion-Bench local annotation website.

This specification is for humans and AI agents. It defines how AutoFusion
experiments must organize multimodal annotation data so the shared annotation
website, validators, merge step, and scorers can be reused.

## 1. Scope

Use this spec only for AutoFusion-Bench annotation work. It covers:

- source item metadata;
- corruption or review instance metadata;
- draft annotation sheets;
- local media path mapping;
- annotator exports;
- merge/adjudication outputs;
- validation and scorer handoff.

It does not define a general public annotation platform.

## 2. Directory Contract

Each experiment keeps its data under its own experiment folder:

```text
experiments/<exp-id>-<shortname>/
  data/
    <batch>_source_items.jsonl
    <batch>_corruption_manifest.jsonl
    media/
      ...
  annotations/
    <batch>.draft.jsonl
    <batch>.draft.csv
    <batch>.<annotator>.jsonl
    <batch>.merged.jsonl
    adjudication_notes.md
  results/
    annotation_disagreements.md
    annotation_agreement.md
```

For `exp-002`, existing names such as `smoke_source_items.jsonl`,
`smoke_corruption_manifest.jsonl`, and `smoke_annotation_sheet_v1.draft.jsonl`
remain valid.

Do not put run outputs, checkpoints, media caches, or annotation exports in a
shared top-level `outputs/` directory.

## 3. Source Items

`data/<batch>_source_items.jsonl` is one JSON object per clean source item.

Required fields:

```json
{
  "source_id": "stable-source-id",
  "source_dataset": "AVQA_HF_sample",
  "question": "...",
  "choices": ["..."],
  "gold_answer": "...",
  "bucket": "audio_necessary",
  "modality_necessity": {
    "text_question_only": false,
    "audio_sufficient": true,
    "video_sufficient": false,
    "audio_video_joint_required": false,
    "human_confidence": "pending_manual_review"
  }
}
```

Recommended fields:

- `video_id`, `video_name`, `question_relation`, `question_type`;
- `video_path` for clean synchronized AV media;
- `media.items` when clean evidence is split across multiple files.

Source-level modality fields are hints until human reviewed.
For annotation exports, `source_decision` records the human source gate:
`accept`, `reject`, or `adjudicate`. A corrupted instance must not enter
headline scoring unless its clean source is accepted first.

## 4. Corruption Manifest

`data/<batch>_corruption_manifest.jsonl` is one JSON object per reviewed
instance.

Required fields:

```json
{
  "instance_id": "stable-source-id__corruption-name",
  "source_id": "stable-source-id",
  "affected_modality": "audio|video|text|cross_modal|none",
  "corruption_type": "audio_mute",
  "severity": "mild|medium|severe|none",
  "location": {
    "text_span": null,
    "audio_time": null,
    "video_time": null,
    "frame_range": null
  },
  "corruption_relevance": "answer_relevant|answer_irrelevant|unclear",
  "generator_family": "media_smoke_v0",
  "seed": 0
}
```

Recommended media fields:

```json
{
  "source_video_path": "/path/or/remote/path/source.mp4",
  "corrupted_video_path": "experiments/<exp>/data/media/corrupted.mp4"
}
```

Generator metadata is never gold. It is a hint shown to annotators.

## 5. Draft Annotation Sheet

The website imports draft annotation JSONL. For exp-002, generate it with:

```bash
python3 experiments/exp-002-diag-action-pilot/scripts/build_annotation_sheet_v1.py \
  --source-items experiments/<exp>/data/<batch>_source_items.jsonl \
  --corruption-manifest experiments/<exp>/data/<batch>_corruption_manifest.jsonl \
  --output-jsonl experiments/<exp>/annotations/<batch>.draft.jsonl \
  --output-csv experiments/<exp>/annotations/<batch>.draft.csv
```

If a future AutoFusion experiment creates draft rows directly, it must satisfy
the same annotation validator:

```bash
python3 experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py \
  --kind annotations \
  experiments/<exp>/annotations/<batch>.draft.jsonl
```

Draft rows must use:

```json
{
  "review_status": "needs_human_review",
  "source_decision": "adjudicate"
}
```

`source_decision=adjudicate` is the safe default. Annotators promote it to
`accept` only after the clean source media clearly supports the gold answer.

## 6. Media Contract

Each annotation row may include the legacy two-slot media object:

```json
{
  "media": {
    "source_video_path": "/remote/or/local/source.mp4",
    "corrupted_video_path": "experiments/<exp>/data/media/corrupted.mp4"
  }
}
```

For richer pages with video, audio, and images, add `media.items`:

```json
{
  "media": {
    "source_video_path": "...",
    "corrupted_video_path": "...",
    "items": [
      {
        "label": "clean_video",
        "role": "source",
        "modality": "video",
        "path": "experiments/<exp>/data/media/source.mp4"
      },
      {
        "label": "clean_audio",
        "role": "source",
        "modality": "audio",
        "path": "experiments/<exp>/data/media/source.wav"
      },
      {
        "label": "reference_frame",
        "role": "evidence",
        "modality": "image",
        "path": "experiments/<exp>/data/media/frame_0001.jpg"
      }
    ]
  }
}
```

Path rules:

- repo-relative paths are preferred for files committed or staged inside the
  repo tree;
- absolute remote paths are allowed only when paired with `ANNOTATION_MEDIA_MAP`;
- missing media must not block field annotation.

Example mapping:

```text
/usr1/home/s125mdg43_10/datasets=/path/to/local/datasets;/usr1/home/s125mdg43_10/projects/AutoFusion-bench=/path/to/AutoFusion-bench
```

## 7. Annotator Export

Each annotator exports:

```text
experiments/<exp>/annotations/<batch>.<annotator>.jsonl
```

Every export must pass:

```bash
python3 experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py \
  --kind annotations \
  experiments/<exp>/annotations/<batch>.<annotator>.jsonl
```

The website may add extensions:

- `annotation_app_metadata`;
- `recovery_evidence.annotation_app_time_spans`;
- `defect_location.bboxes`;
- `annotation_app_disagreements`.

These extensions are allowed and must not break existing scorers.

## 8. Merge and Adjudication

When multiple annotators label the same batch:

```bash
cd experiments/exp-002-diag-action-pilot/annotation_app/backend
../.venv/bin/python -m app.cli merge \
  --annotations \
    ../../../../experiments/<exp-id>-<shortname>/annotations/<batch>.annotator_a.jsonl \
    ../../../../experiments/<exp-id>-<shortname>/annotations/<batch>.annotator_b.jsonl \
  --output ../../../../experiments/<exp-id>-<shortname>/annotations/<batch>.merged.jsonl \
  --report ../../../../experiments/<exp-id>-<shortname>/results/annotation_disagreements.md
```

Rows with disagreement are marked `needs_adjudication`. Use the report and the
website to adjudicate before scorer handoff.

## 9. Website Setup and Smoke Test

Recommended local setup:

```bash
cd experiments/exp-002-diag-action-pilot/annotation_app
./scripts/check_config.py
./scripts/bootstrap_local.sh
.venv/bin/python scripts/check_config.py --require-runtime-deps
.venv/bin/python scripts/smoke_test.py
./scripts/run_local.sh
```

Docker may be used, but it is optional.

## 10. AI-Agent Rules

When an AI agent prepares an AutoFusion annotation batch, it must:

1. Use this data spec instead of inventing a new annotation workflow.
2. Keep generated corruption metadata as hints, not gold.
3. Generate stable `source_id` and `instance_id` values.
4. Prefer repo-relative media paths, or document `ANNOTATION_MEDIA_MAP`.
5. Run `scripts/smoke_test.py` before handing the website to humans.
6. Validate every exported annotation JSONL.
7. Write status and output paths back to the experiment runbook or memory.
