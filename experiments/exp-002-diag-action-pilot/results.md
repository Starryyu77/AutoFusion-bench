# Results: exp-002

## Current status

Status: Phase 0 media smoke passed; model smoke blocked on model access.

No model result has been produced yet.

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
- [ ] Five-clip model-call smoke completed.

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

Current blocker:

- no remote API key or staged local audio-video MLLM is available, so actual
  model-call smoke has not run.

## Boundary

MELD is not the main positive substrate for this experiment. It may be used only
as a diagnostic/control reference if needed.
