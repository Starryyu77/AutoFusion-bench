# Local Annotation Export Validation

Date: 2026-06-09

Validated file:

`experiments/exp-002-diag-action-pilot/annotations/pilot_annotations.local.jsonl`

## Validation

Command:

```bash
python3 experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py \
  --kind annotations \
  experiments/exp-002-diag-action-pilot/annotations/pilot_annotations.local.jsonl
```

Result:

```text
ok: experiments/exp-002-diag-action-pilot/annotations/pilot_annotations.local.jsonl (annotations)
```

## Export Summary

- rows: 5
- `review_status`: 5 reviewed
- `instance_decision`: 5 reject
- `main_answerability`: 5 exclude_from_main
- `annotation_confidence`: 5 low
- `risk_sensitive`: 5 true

Per-row decisions:

| instance_id | instance_decision | post_corruption_answerability | cross_modal_recoverability | preferred_route | confidence | risk_sensitive |
|---|---|---|---|---|---|---|
| smoke-audio-necessary__audio_mute | reject | unclear | unclear | [] | low | true |
| smoke-av-complementary__audio_shift_1500ms | reject | answerable | not_needed | ["audio"] | low | true |
| smoke-conflict-like__audio_replace_conflict_like | reject | answerable | not_needed | ["video"] | low | true |
| smoke-corrupted-irrelevant__video_blur_irrelevant | reject | partially_answerable | unrecoverable | ["audio"] | low | true |
| smoke-video-necessary__video_blur | reject | partially_answerable | recoverable | ["video"] | low | true |

## Interpretation

This export proves that the local annotation app can export a validator-compatible
5-row JSONL file. It should not be treated as final gold for headline scoring.
All five rows are low-confidence, risk-sensitive, and excluded from the main
answerability split.

The annotation app export path now derives scorer-facing `instance_decision`
conservatively. A row enters headline scoring only when it is reviewed,
answerable or unanswerable, high/medium confidence, and not risk-sensitive.
This prevents a row saved as `reviewed` from being accidentally interpreted as a
main-table gold row.

## Next Action

Use this file as a local smoke export only. For `smoke_annotations_v1.gold.jsonl`,
redo or adjudicate the five rows under the simplified required-field protocol
and require at least one clear answerable or unanswerable row with high/medium
confidence and `risk_sensitive=false`.
