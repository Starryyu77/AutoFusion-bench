# Smoke Annotation v1 Adjudication Notes

Status: codex first-pass, not final gold

Date: 2026-06-09

## Scope

This file records the first formal pass over the 5-row smoke annotation task
using `annotation_task_protocol_v1.md`.

The pass used:

- synced source and corrupted MP4 files from `ntu-gpu43`;
- contact sheets generated from source and corrupted videos;
- ffprobe/ffmpeg volume diagnostics;
- existing source/corruption manifests as hints only.

This is not yet a double-annotated gold set. It should be treated as
`codex_pass` and reviewed by a human annotator before being renamed or promoted
to `smoke_annotations_v1.gold.jsonl`.

## Row-Level Decisions

### 1. `smoke-audio-necessary__audio_mute`

- Decision: `accept`
- Main answerability: `unanswerable`
- Rationale: corrupted audio is effectively silent (`mean_volume=-91 dB`);
  visual evidence does not identify a cricket-like sound source.
- Oracle action: abstain.

### 2. `smoke-video-necessary__video_blur`

- Decision: `accept`
- Main answerability: `answerable`
- Rationale: video is blurred but still shows cattle legs/body and cowbell.
  The corruption lowers confidence but does not make the item unanswerable.
- Oracle route: prefer video; audio is supportive but not sufficient for the
  "animal eating grass" question.

### 3. `smoke-av-complementary__audio_shift_1500ms`

- Decision: `adjudicate`
- Main answerability: `exclude_from_main`
- Rationale: visual frames strongly indicate hail, but the item is meant to test
  whether a 1.5s audio shift matters for a global "main source of sound" question.
  This should not enter headline scoring until a human listener decides whether
  the misalignment is answer-relevant, merely a detectable defect, or irrelevant.

### 4. `smoke-corrupted-irrelevant__video_blur_irrelevant`

- Decision: `accept`
- Main answerability: `answerable`
- Rationale: the question asks for the sound source. Video blur is task
  irrelevant; audio remains clean.
- Caveat: a human listener should confirm the turkey audio identity before final
  gold promotion.

### 5. `smoke-conflict-like__audio_replace_conflict_like`

- Decision: `accept`
- Main answerability: `answerable`
- Rationale: the location is visually apparent as road/street. Replaced audio is
  task-irrelevant for this question.
- Note: this overrides the source manifest's coarse `Both`/joint hint.

## Promotion Criteria

Before using these labels as final smoke gold:

1. a human annotator should listen to rows 3 and 4;
2. row 3 should be adjudicated explicitly;
3. accepted rows should pass `validate_jsonl.py --kind annotations`;
4. any promoted file should be named `smoke_annotations_v1.gold.jsonl`.
