# Smoke Annotation Pass

Date: 2026-06-09

Status: codex first-pass, not final gold

## Inputs Checked

- Source/corrupted MP4 files were synced from `ntu-gpu43` to local temp storage.
- Visual contact sheets were generated for clean and corrupted clips.
- ffprobe/ffmpeg volume diagnostics were used to check stream presence and
  silence.
- Source/corruption manifests were used as hints only.

## Output Files

- `annotations/smoke_annotations_v1.codex_pass.jsonl`
- `annotations/adjudication_notes_smoke_v1.md`

## Validation

```text
python3 experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py \
  --kind annotations \
  experiments/exp-002-diag-action-pilot/annotations/smoke_annotations_v1.codex_pass.jsonl

ok: experiments/exp-002-diag-action-pilot/annotations/smoke_annotations_v1.codex_pass.jsonl (annotations)
```

## Summary

| Item | Count |
|---|---:|
| rows | 5 |
| accepted rows | 4 |
| adjudication rows | 1 |
| headline-eligible rows | 4 |
| answerable rows | 3 |
| unanswerable rows | 1 |
| exclude-from-main rows | 1 |

## Row Outcomes

| Instance | Decision | Main Answerability | Main Rationale |
|---|---|---|---|
| `smoke-audio-necessary__audio_mute` | accept | unanswerable | audio is effectively silent; visual evidence does not support cricket |
| `smoke-video-necessary__video_blur` | accept | answerable | video blur lowers confidence but cattle evidence remains visible |
| `smoke-av-complementary__audio_shift_1500ms` | adjudicate | exclude_from_main | human listener should decide whether 1.5s shift is answer-relevant |
| `smoke-corrupted-irrelevant__video_blur_irrelevant` | accept | answerable | video blur is irrelevant for sound-source question; audio route remains |
| `smoke-conflict-like__audio_replace_conflict_like` | accept | answerable | visual road/street evidence is sufficient; replaced audio is task-irrelevant |

## Before Gold Promotion

Do not rename this file to gold yet. Before creating
`annotations/smoke_annotations_v1.gold.jsonl`:

1. have a human annotator listen to rows 3 and 4;
2. adjudicate row 3 explicitly;
3. preserve row-level notes in `adjudication_notes_smoke_v1.md`;
4. rerun `validate_jsonl.py --kind annotations` on the promoted gold file.
