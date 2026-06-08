# Results: exp-002

## Current status

Status: initialized and Phase 0 dataset feasibility started.

No model result has been produced yet.

## Phase 0 checklist

- [x] Remote repo synced after exp-002 initialization.
- [x] AVQA metadata staged on `ntu-gpu43`.
- [x] AVQA matched-video subset confirmed stageable from Hugging Face.
- [ ] Full dataset source selected.
- [ ] Dataset source staged or confirmed stageable on `ntu-gpu43`.
- [ ] At least 80-120 candidate source clips inspectable.
- [ ] At least 2 audio-video-capable models verified.
- [ ] Five-clip structured-output smoke completed.

## Phase 0 dataset notes

AVQA metadata can be downloaded on `ntu-gpu43`. The practical Hugging Face
package currently exposes 9,982 MP4 files that match 10,028 QA rows. A 15-video
sample balanced across `Sound`, `View`, and `Both` downloaded successfully, and
all sample MP4 files were readable through the existing `.deps/opencv` path.

Current blocker for corruption work:

- audio probing/extraction tooling is missing or broken. Install/provide
  ffmpeg/ffprobe or an equivalent Python audio-video backend before building
  audio corruptions.

## Boundary

MELD is not the main positive substrate for this experiment. It may be used only
as a diagnostic/control reference if needed.
