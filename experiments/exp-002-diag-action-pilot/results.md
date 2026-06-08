# Results: exp-002

## Current status

Status: Phase 0 media smoke passed; first API model smoke passed.

The first same-instance audio-video model smoke has been produced with
`qwen3.5-omni-plus`. The minimum model panel is still incomplete because the
pilot needs at least 2 same-instance audio-video models before scaling.

## Phase 0 checklist

- [x] Remote repo synced after exp-002 initialization.
- [x] AVQA metadata staged on `ntu-gpu43`.
- [x] AVQA matched-video subset confirmed stageable from Hugging Face.
- [ ] Full dataset source selected.
- [ ] Dataset source staged or confirmed stageable on `ntu-gpu43`.
- [ ] At least 80-120 candidate source clips inspectable.
- [ ] At least 2 audio-video-capable models verified.
- [x] Five-clip media smoke completed.
- [x] Five-clip diagnosis prompt pack completed.
- [x] Five-clip model-call smoke completed for first A/V model.

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

Current blocker:

- only 1 same-instance audio-video model has been confirmed; the Phase 0 model
  panel gate requires at least 2 before scaling.
- the 5-clip smoke found task-conditioned label ambiguity, so generator
  metadata must be verified by human labels for `modality_necessity` and
  `corruption_relevance`.

## Boundary

MELD is not the main positive substrate for this experiment. It may be used only
as a diagnostic/control reference if needed.
