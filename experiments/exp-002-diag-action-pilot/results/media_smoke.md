# Media Smoke Result

Status: passed

Checked on: 2026-06-08

## What was tested

The smoke used 5 AVQA examples:

- 1 audio-necessary item
- 1 video-necessary item
- 1 audio-video complementary item
- 1 corrupted-irrelevant control
- 1 conflict-like item

Files:

- `data/smoke_source_items.jsonl`
- `data/smoke_corruption_manifest.jsonl`
- `outputs/media_smoke/probe_results.jsonl`
- `outputs/model_smoke_prompt_pack.jsonl`

## Audio/video toolchain

Installed on `ntu-gpu43` under the project-local dependency folder:

```text
.deps/audio/imageio_ffmpeg/
```

The active ffmpeg binary is:

```text
/usr1/home/s125mdg43_10/projects/AutoFusion-bench/.deps/audio/imageio_ffmpeg/binaries/ffmpeg-linux64-v4.2.2
```

This avoids system package changes.

## Source media probe

All 5 source MP4 files had both video and audio streams.

| Source id | Expected bucket | Probe |
|---|---|---|
| `smoke-audio-necessary` | audio necessary | audio+video present |
| `smoke-video-necessary` | video necessary | audio+video present |
| `smoke-av-complementary` | audio-video complementary | audio+video present |
| `smoke-corrupted-irrelevant` | corrupted-irrelevant control | audio+video present |
| `smoke-conflict-like` | conflict-like | audio+video present |

## Corruption outputs

All 5 corrupted MP4 files were generated and retained both audio and video
streams.

| Instance | Corruption | Probe |
|---|---|---|
| `smoke-audio-necessary__audio_mute` | audio mute | audio+video present |
| `smoke-video-necessary__video_blur` | video blur | audio+video present |
| `smoke-av-complementary__audio_shift_1500ms` | audio shift | audio+video present |
| `smoke-corrupted-irrelevant__video_blur_irrelevant` | irrelevant video blur | audio+video present |
| `smoke-conflict-like__audio_replace_conflict_like` | replace audio with another clip | audio+video present |

## Validation

`data/smoke_source_items.jsonl` passed:

```bash
python3 experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py \
  --kind source-items \
  experiments/exp-002-diag-action-pilot/data/smoke_source_items.jsonl
```

`data/smoke_corruption_manifest.jsonl` passed:

```bash
python3 experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py \
  --kind corruption-manifest \
  experiments/exp-002-diag-action-pilot/data/smoke_corruption_manifest.jsonl
```

## Interpretation

The Phase 0 media pipeline is now viable:

- AVQA sample videos can be downloaded.
- The server can probe audio and video streams.
- The server can generate basic answer-relevant and answer-irrelevant
  corruptions.
- Corruption manifests can be produced in the expected schema.

This does not yet validate model behavior or annotation quality.
