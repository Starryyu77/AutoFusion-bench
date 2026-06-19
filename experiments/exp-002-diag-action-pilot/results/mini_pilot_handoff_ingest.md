# Mini-Pilot Handoff Ingest

Date: 2026-06-18

## Summary

The junior handoff package has been normalized into the `exp-002` experiment
folder as a 10-source / 40-instance mini-pilot draft.

Active files:

- `data/mini_pilot_source_items.jsonl`
- `data/mini_pilot_corruption_manifest.jsonl`
- `annotations/mini_pilot.draft.jsonl`
- `annotations/mini_pilot.draft.csv`
- `annotations/mini_pilot.local.jsonl`
- `data/media/mini_pilot/clean/`
- `data/media/mini_pilot/corrupted/`
- `data/raw_handoffs/2026-06-18-junior-package/产物.zip`

Media and raw handoff files are local-only and ignored by Git.

## Batch Shape

- 10 clean source videos.
- 40 corrupted videos.
- 8 AVQA-derived sources.
- 2 MUSIC-AVQA-derived sources.
- Source buckets are balanced:
  - 2 audio-necessary;
  - 2 video-necessary;
  - 2 audio-video joint;
  - 2 corrupted-irrelevant controls;
  - 2 cross-modal conflict candidates.

Corruption families:

- 20 video corruptions.
- 20 audio corruptions.
- Corruption types include video occlusion, video blur, audio noise, and audio
  mute.

## Validation

The following files pass the existing JSONL validator:

- `data/mini_pilot_source_items.jsonl`
- `data/mini_pilot_corruption_manifest.jsonl`
- `annotations/mini_pilot.draft.jsonl`
- `annotations/mini_pilot.local.jsonl`

All 250 media references in the JSONL files resolve to existing local files
after path normalization.

MP4 stream check:

- 50 MP4 files checked.
- 45 MP4 files contain both audio and video streams.
- 5 `audio_mute` MP4 files contain only a video stream:
  - `src_001__音频静音.mp4`
  - `src_004__音频静音.mp4`
  - `src_006__音频静音.mp4`
  - `src_007__音频静音.mp4`
  - `src_010__音频静音.mp4`

This is acceptable only if the intended corruption is true audio removal. If
the model protocol should always receive an audio-video container, regenerate
these five files with an explicit silent audio track.

## Current Gold Status

This batch is not gold yet.

Reasons:

- `mini_pilot.local.jsonl` has 40 rows, but only 2 rows are marked `reviewed`.
- 38 rows are still `needs_human_review`.
- `source_decision` is absent for all 40 rows.
- `instance_decision` is absent for all 40 rows.
- source-level modality necessity is still marked as candidate / pending review.

Under the experiment constitution, these rows must not enter headline scorer
tables until clean-source acceptance, post-corruption answerability,
recoverability, oracle route, abstention, confidence, and headline inclusion are
human-reviewed or adjudicated.

## Next Required Gate

Run source-level screening before model calls:

1. Inspect all 10 clean videos.
2. Decide `source_decision=accept|reject|adjudicate`.
3. Confirm whether each source is question-only guessable.
4. Confirm whether audio alone is sufficient.
5. Confirm whether video alone is sufficient.
6. Confirm whether audio-video joint evidence is truly required.
7. Reject or adjudicate ambiguous sources before reviewing corrupted instances.

Only accepted clean sources should proceed to the 40-instance corrupted review.
