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
- `source_decision`: 5 accept
- `review_status`: 5 reviewed
- `instance_decision`: 4 accept, 1 adjudicate
- `main_answerability`: 4 answerable, 1 unanswerable
- `post_corruption_answerability`: 3 answerable, 1 partially_answerable, 1 unanswerable
- `annotation_confidence`: 3 medium, 2 high
- `risk_sensitive`: 5 false

Per-row decisions:

| instance_id | source_decision | instance_decision | post_corruption_answerability | cross_modal_recoverability | preferred_route | confidence | risk_sensitive |
|---|---|---|---|---|---|---|---|
| smoke-audio-necessary__audio_mute | accept | accept | unanswerable | unrecoverable | [] | medium | false |
| smoke-av-complementary__audio_shift_1500ms | accept | accept | answerable | not_needed | ["video"] | high | false |
| smoke-conflict-like__audio_replace_conflict_like | accept | accept | answerable | not_needed | ["video"] | high | false |
| smoke-corrupted-irrelevant__video_blur_irrelevant | accept | accept | answerable | not_needed | ["audio"] | medium | false |
| smoke-video-necessary__video_blur | accept | adjudicate | partially_answerable | recoverable | ["video"] | medium | false |

## Interpretation

This export proves that the local annotation app can export a validator-compatible
5-row JSONL file. This version is substantially closer to usable gold than the
previous local export: all 5 clean sources are accepted, all rows have high or
medium confidence, all rows are no longer risk-sensitive, and 4/5 rows now
enter headline scoring as `instance_decision=accept`.

The file is still not a fully adjudicated 5-row gold set. One row remains
adjudication-only because it is still `partially_answerable`. We intentionally
keep `smoke-video-necessary__video_blur` out of headline scoring for now: the
clean and corrupted clips appear answerable only with some experience/common
sense, rather than with fully clear visual evidence.

The annotation app export path now derives scorer-facing `instance_decision`
conservatively. A row enters headline scoring only when its clean source is
accepted, it is reviewed, it is answerable or unanswerable, it has high/medium
confidence, and it is not risk-sensitive.
This prevents a row saved as `reviewed` from being accidentally interpreted as a
main-table gold row.

## Next Action

Use this file as a partial smoke gold export: 4 rows can enter headline scoring,
while 1 row remains an adjudication/qualitative case. Do not promote
`smoke-video-necessary__video_blur` to headline gold unless a later adjudicator
decides the visual evidence is clear enough without relying mainly on common
sense.
