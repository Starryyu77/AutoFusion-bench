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
- `source_decision`: 4 accept, 1 adjudicate
- `review_status`: 5 reviewed
- `instance_decision`: 5 adjudicate
- `main_answerability`: 4 answerable, 1 unanswerable
- `post_corruption_answerability`: 2 answerable, 2 partially_answerable, 1 unanswerable
- `annotation_confidence`: 3 medium, 2 high
- `risk_sensitive`: 5 true

Per-row decisions:

| instance_id | source_decision | instance_decision | post_corruption_answerability | cross_modal_recoverability | preferred_route | confidence | risk_sensitive |
|---|---|---|---|---|---|---|---|
| smoke-audio-necessary__audio_mute | accept | adjudicate | unanswerable | unrecoverable | ["audio"] | medium | true |
| smoke-av-complementary__audio_shift_1500ms | accept | adjudicate | answerable | not_needed | ["video"] | high | true |
| smoke-conflict-like__audio_replace_conflict_like | accept | adjudicate | answerable | not_needed | ["video"] | high | true |
| smoke-corrupted-irrelevant__video_blur_irrelevant | adjudicate | adjudicate | partially_answerable | unrecoverable | ["audio"] | medium | true |
| smoke-video-necessary__video_blur | accept | adjudicate | partially_answerable | recoverable | ["video"] | medium | true |

## Interpretation

This export proves that the local annotation app can export a validator-compatible
5-row JSONL file. This version is substantially closer to usable gold than the
previous local export: 4/5 clean sources are accepted, all rows have high or
medium confidence, and `main_answerability` is no longer uniformly
`exclude_from_main`.

It still should not be treated as final gold for headline scoring. All five rows
remain `risk_sensitive=true`, so the conservative export logic keeps
`instance_decision=adjudicate`. One row still has `source_decision=adjudicate`.

The annotation app export path now derives scorer-facing `instance_decision`
conservatively. A row enters headline scoring only when its clean source is
accepted, it is reviewed, it is answerable or unanswerable, it has high/medium
confidence, and it is not risk-sensitive.
This prevents a row saved as `reviewed` from being accidentally interpreted as a
main-table gold row.

## Next Action

Use this file as a near-gold smoke export, not final headline gold. Required
fixes before promotion:

1. For `smoke-audio-necessary__audio_mute`, align the unanswerable policy:
   set `oracle_abstain=true`, clear acceptable/preferred routes, and clear
   expected answer if the correct action is refusal.
2. For any rows that are now clear enough for headline scoring, set
   `risk_sensitive=false`.
3. Resolve `smoke-corrupted-irrelevant__video_blur_irrelevant` clean-source
   status: either promote to `source_decision=accept` or keep it adjudicated.
4. Rows with `post_corruption_answerability=partially_answerable` should remain
   qualitative/adjudication unless the annotator can make them clearly
   `answerable` or `unanswerable`.
