---
name: autofusion-annotation
description: "Use this skill for AutoFusion-Bench annotation work: organizing multimodal data, preparing draft annotation sheets, running the local annotation website, validating exports, merging annotators, and handing off annotation tasks to humans or AI agents."
---

# AutoFusion Annotation

Use this only inside the AutoFusion-Bench repo. The goal is to make every
AutoFusion annotation task follow the same contract instead of inventing a new
annotation method per experiment.

## Required Context

Before changing data or instructions:

1. Read `skills/autofusion-annotation/references/data_spec.md`.
2. Read the active experiment `RUNBOOK.md` or `memory/tasks/<exp-id>.md` if it
   exists.
3. Keep generator metadata separate from human/adjudicated gold labels.

## Canonical Tool

Use the local annotation app:

`experiments/exp-002-diag-action-pilot/annotation_app/`

It is currently stored under `exp-002`, but it is the AutoFusion project-level
annotation tool. Future AutoFusion experiments should reuse it by importing
their own draft JSONL sheets.

Recommended setup:

```bash
cd experiments/exp-002-diag-action-pilot/annotation_app
./scripts/check_config.py
./scripts/bootstrap_local.sh
./scripts/run_local.sh
```

Strict runtime check after bootstrap:

```bash
.venv/bin/python scripts/check_config.py --require-runtime-deps
```

End-to-end smoke:

```bash
.venv/bin/python scripts/smoke_test.py
```

Docker is optional only; do not make Docker the only documented path.

## Workflow

For every AutoFusion annotation batch:

1. Organize files under one experiment folder using the data spec.
2. Create or verify a draft annotation JSONL marked `needs_human_review`.
3. Run `scripts/smoke_test.py` before asking annotators to use the website.
4. Import the draft sheet into local SQLite through the app or CLI.
5. Export `annotations/<batch>.<annotator>.jsonl`.
6. Validate export with `scripts/validate_jsonl.py --kind annotations`.
7. If multiple annotators exist, merge exports and inspect disagreement report.
8. Only use validated/adjudicated JSONL as scorer input.
9. Update the experiment runbook and project memory with paths and status.

## Guardrails

- Do not use unverified generator hints as gold labels.
- Do not write annotation outputs to shared top-level `outputs/`.
- Do not change `score_v1_metrics.py` input shape unless the schema spec is
  explicitly revised.
- Preserve `source_id`, `instance_id`, media paths, and annotator identity.
- If media are missing locally, document the `ANNOTATION_MEDIA_MAP` needed to
  resolve them.
