# Results: exp-002

## Current status

Status: Phase 0 media smoke passed; Qwen-family model panel passed smoke.

The first-pilot model panel is now Qwen-only:

- `qwen3.5-omni-plus` as the main same-instance audio-video MLLM;
- `qwen3-omni-flash` as the second same-instance audio-video MLLM;
- `qwen3.7-plus` as a video/text control, not counted as audio-video.

## Phase 0 checklist

- [x] Remote repo synced after exp-002 initialization.
- [x] AVQA metadata staged on `ntu-gpu43`.
- [x] AVQA matched-video subset confirmed stageable from Hugging Face.
- [ ] Full dataset source selected.
- [ ] Dataset source staged or confirmed stageable on `ntu-gpu43`.
- [ ] At least 80-120 candidate source clips inspectable.
- [x] At least 2 audio-video-capable models verified in the Qwen family.
- [x] Five-clip media smoke completed.
- [x] Five-clip diagnosis prompt pack completed.
- [x] Five-clip model-call smoke completed for Qwen A/V panel.

## Phase 0 dataset notes

AVQA metadata can be downloaded on `ntu-gpu43`. The practical Hugging Face
package currently exposes 9,982 MP4 files that match 10,028 QA rows. A 15-video
sample balanced across `Sound`, `View`, and `Both` downloaded successfully, and
all sample MP4 files were readable through the existing `.deps/opencv` path.

Media smoke result:

- project-local `imageio-ffmpeg` installed under `.deps/audio` on `ntu-gpu43`
- 5 source MP4 files had audio+video streams
- 5 corrupted MP4 outputs retained audio+video streams
- corruption manifest passed schema validation

Model smoke result:

- DashScope/OpenAI-compatible client access was confirmed on `ntu-gpu43`.
- `qwen3.7-plus` text probe passed.
- `qwen3.7-plus` accepted a 1-clip video diagnosis request, but the response
  usage reported `video_tokens` and no `audio_tokens`; do not count it yet as a
  same-instance audio-video model.
- `qwen3.5-omni-plus` processed all 5 corrupted MP4 smoke instances with both
  audio and video tokens observed and 5/5 JSON parse success.
- `qwen3-omni-flash` processed all 5 corrupted MP4 smoke instances with both
  audio and video tokens observed and 5/5 JSON parse success.
- `qwen3.5-omni-flash` was attempted but the stream call stalled before a first
  row completed; it is deferred unless needed.

Current blocker:

- expert review of the screening/scoring standard recommended minor revision
  before freezing; this has been incorporated into
  `annotations/screening_scoring_guideline_v1.md`.
- annotation sheet and scorer scripts are not implemented yet, so the current
  model results are access/format evidence rather than scored research
  evidence.

## Boundary

MELD is not the main positive substrate for this experiment. It may be used only
as a diagnostic/control reference if needed.
