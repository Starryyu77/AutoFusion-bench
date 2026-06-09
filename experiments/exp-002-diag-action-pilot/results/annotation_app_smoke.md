# Annotation App Smoke Test

Date: 2026-06-09

## Purpose

Verify that the reusable AutoFusion annotation website can be configured
locally, serve the frontend/API, import a draft sheet, display multiple media
items, save annotation edits, export scorer-compatible JSONL, and preserve the
existing scorer contract.

## Commands

```bash
cd experiments/exp-002-diag-action-pilot/annotation_app
./scripts/check_config.py
.venv/bin/python scripts/check_config.py --require-runtime-deps
npm run build
.venv/bin/python scripts/smoke_test.py
```

Scorer compatibility:

```bash
cd experiments/exp-002-diag-action-pilot/annotation_app/backend
../.venv/bin/python -m app.cli --db /private/tmp/exp002_annotation_fixture2.sqlite import-sheet \
  --sheet ../../fixtures/scoring_v1_annotations.jsonl \
  --annotator fixture-smoke
../.venv/bin/python -m app.cli --db /private/tmp/exp002_annotation_fixture2.sqlite export \
  --output /private/tmp/exp002_annotation_fixture2_export.jsonl

cd /Users/starryyu/2026/AutoFusion-bench
python3 experiments/exp-002-diag-action-pilot/scripts/score_v1_metrics.py \
  --annotations /private/tmp/exp002_annotation_fixture2_export.jsonl \
  --diagnoses experiments/exp-002-diag-action-pilot/fixtures/scoring_v1_diagnoses.jsonl \
  --actions experiments/exp-002-diag-action-pilot/fixtures/scoring_v1_model_actions.jsonl \
  --fixed-rule-actions experiments/exp-002-diag-action-pilot/fixtures/scoring_v1_fixed_rule_actions.jsonl \
  --per-instance-jsonl /private/tmp/exp002_annotation_fixture2_per_instance.jsonl \
  --metrics-csv /private/tmp/exp002_annotation_fixture2_metrics.csv \
  --metrics-md /private/tmp/exp002_annotation_fixture2_metrics.md
```

## Observed Result

`scripts/smoke_test.py` passed with:

```json
{
  "frontend_assets": 2,
  "instances": 5,
  "media_items_first_instance": 4,
  "validator": "ok"
}
```

The smoke test adds temporary `media.items[]` entries for extra audio and image
media, confirming that the app can show source/corrupted media plus additional
audio/image evidence entries in one page.

The scorer compatibility run preserved:

| metric | value |
|---|---:|
| `headline_n` | 3 |
| `policy_action_accuracy` | 0.666667 |
| `conditional_policy_failure` | 0.500000 |
| `rule_lift` | 0.333333 |

## Conclusion

The annotation app is usable as the reusable AutoFusion annotation entrypoint
for draft JSONL import, local review, multi-media evidence display, JSONL
export, validator handoff, merge/adjudication, and current scorer compatibility.

