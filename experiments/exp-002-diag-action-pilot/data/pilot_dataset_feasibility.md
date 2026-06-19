# Pilot Dataset Feasibility

Status: partial pass

## Purpose

Select the first audio-video QA substrate for `exp-002`. The dataset must
support the diagnosis-to-action pilot, not the old MELD-first feature-level
decision surface.

## Candidate sources checked

### AVQA

Official project:

- Website: https://mn.cs.tsinghua.edu.cn/avqa/
- GitHub: https://github.com/AlyssaYoung/AVQA

Current notes:

- AVQA is an audio-visual question answering dataset over real-life videos.
- The official site describes raw videos and QA annotations.
- The official GitHub points to dataset download links and preprocessing code.
- The official site says raw videos are based on VGG-Sound clips and annotations
  include train/test QA files.

Practical candidate:

- Hugging Face package: https://huggingface.co/datasets/juyil/AVQA-videos

Current notes:

- This package claims to bundle AVQA videos and official train/val annotations.
- It lists 56,666 clips and 57,335 QA rows.
- It exposes `question_relation`, which may help bootstrap modality necessity
  filtering into Sound / View / Both buckets.
- It is labeled non-commercial research only and still inherits YouTube /
  VGGSound copyright caveats, so publication use must cite and document the
  provenance carefully.

Phase 0 action:

- [x] Verify metadata download feasibility on `ntu-gpu43`.
- [x] Verify sample video download feasibility from files that actually exist in
  the Hugging Face package.
- [x] Inspect `question_relation` distribution.
- [x] Check sample video frame readability.
- [x] Check audio stream readability with ffmpeg or equivalent tooling.
- [ ] Inspect 20 examples across `question_relation`.

### MUSIC-AVQA

Official project:

- GitHub: https://github.com/GeWu-Lab/MUSIC-AVQA
- Homepage: https://gewu-lab.github.io/MUSIC-AVQA/

Current notes:

- MUSIC-AVQA is an audio-visual QA dataset for musical performance videos.
- The official GitHub describes 45,867 QA pairs over 9,288 videos and more than
  150 hours.
- Download links include raw videos and annotations.

Phase 0 action:

- Verify whether raw videos and annotations can be downloaded from available
  links.
- Inspect whether music-only domain is too narrow for the first pilot.
- Check whether audio-necessary and visual-necessary buckets are easier to
  annotate than in generic AVQA.

## Feasibility criteria

Pass if at least one candidate satisfies:

- raw synchronized audio-video media is accessible;
- QA annotation includes video id, question, choices or answer;
- 80-120 source candidates can be sampled for manual inspection;
- at least 40 final items can be selected after question-only / prior-only
  filtering;
- expected storage fits comfortably under `/usr1`;
- license/provenance can be documented for research use.

Kill or redesign if:

- no candidate can be legally staged;
- raw media is unavailable and only precomputed features exist;
- most examples are solvable from question text or dataset priors;
- modality necessity cannot be determined reliably;
- clips are too long or too large for model API limits.

## Phase 0 commands

Remote check template:

```bash
ssh ntu-gpu43 '
  cd /usr1/home/s125mdg43_10/projects/AutoFusion-bench &&
  mkdir -p /usr1/home/s125mdg43_10/datasets/diag-action-pilot &&
  df -h /usr1
'
```

Do not launch a full download until the chosen source, license boundary, and
storage target are confirmed.

## AVQA Phase 0 observations on NTU43

Checked on 2026-06-08 under:

```text
/usr1/home/s125mdg43_10/datasets/diag-action-pilot/
```

Downloaded metadata only:

```text
/usr1/home/s125mdg43_10/datasets/diag-action-pilot/AVQA-videos-meta
```

Metadata counts:

| Split | Rows | View | Sound | Both |
|---|---:|---:|---:|---:|
| train | 40,425 | 80 | 199 | 40,146 |
| val | 16,910 | 26 | 64 | 16,820 |

Actual Hugging Face package file listing observed:

- total repo files listed: 9,986
- listed MP4 files: 9,982

Annotation rows whose `video_name` matched an actual listed MP4:

- matched QA rows: 10,028
- matched unique videos: 9,982
- relation distribution:
  - `Both`: 9,973
  - `Sound`: 33
  - `View`: 22

Interpretation:

- The practical AVQA package is usable for a pilot, but it is not a full 56k
  video mirror in this environment.
- `Sound` and `View` are sparse among matched videos; we should oversample them
  and manually verify modality necessity.
- `Both` is abundant and can support complementary / conflict / temporal
  mismatch buckets.

Sample downloaded:

```text
/usr1/home/s125mdg43_10/datasets/diag-action-pilot/AVQA-videos-sample-existing
```

Sample composition:

- 5 `Sound` examples
- 5 `View` examples
- 5 `Both` examples

Video frame smoke:

- all 15 sample MP4 files were readable with OpenCV from `.deps/opencv`
- observed frame rates were about 25-30 FPS
- observed resolutions ranged from 360x288 to 1280x720

Current tooling gap:

- no system `ffprobe` / `ffmpeg` CLI found
- plain Python environment lacks `cv2`
- `.deps/opencv` provides `cv2`
- `torchaudio` import failed due a binary symbol mismatch
- `soundfile`, `librosa`, `pyav`, and `imageio_ffmpeg` are missing

Implication:

> The original system image lacks audio tooling, but the experiment now has a
> project-local `imageio-ffmpeg` install under `.deps/audio`. Use that path for
> Phase 0 and pilot corruption generation unless a better shared environment is
> installed.

## Media smoke result

5 source examples were selected and validated:

```text
experiments/exp-002-diag-action-pilot/data/smoke_source_items.jsonl
```

5 corruption examples were generated and validated:

```text
experiments/exp-002-diag-action-pilot/data/smoke_corruption_manifest.jsonl
```

Probe output:

```text
experiments/exp-002-diag-action-pilot/outputs/media_smoke/probe_results.jsonl
```

Result:

- all 5 source MP4 files contained both audio and video streams
- all 5 corrupted MP4 outputs retained both audio and video streams
- corruption families covered audio mute, video blur, audio shift, irrelevant
  video blur, and conflict-like audio replacement

## Decision

AVQA is a viable first dataset candidate for the pilot, subject to audio-tooling
setup and manual modality-necessity inspection.

MUSIC-AVQA remains a backup or complementary candidate and has not yet been
staged.

## 2026-06-18 mini-pilot handoff update

A junior handoff package has been normalized into the experiment folder:

- `data/mini_pilot_source_items.jsonl`
- `data/mini_pilot_corruption_manifest.jsonl`
- `annotations/mini_pilot.draft.jsonl`
- `annotations/mini_pilot.local.jsonl`
- `data/media/mini_pilot/`

The batch contains 10 clean sources and 40 corrupted instances. Source balance:

- 8 AVQA-derived sources;
- 2 MUSIC-AVQA-derived sources;
- 2 audio-necessary;
- 2 video-necessary;
- 2 audio-video joint;
- 2 corrupted-irrelevant controls;
- 2 cross-modal conflict candidates.

Current interpretation:

- The handoff is a useful 10-source mini-pilot draft.
- It is not yet evidence that AVQA alone is sufficient as the main substrate.
- Source-level labels are still candidate labels because clean-source acceptance
  and modality necessity have not been human-adjudicated.
- The next decision gate is source-level screening: accept, reject, or
  adjudicate each clean source before using the 40 corrupted instances for model
  scoring.
