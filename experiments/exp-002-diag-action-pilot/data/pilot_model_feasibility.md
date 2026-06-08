# Pilot Model Feasibility

Status: Qwen-family audio-video model panel passed smoke

## Purpose

Identify a minimum model panel for testing diagnosis-to-action behavior on
audio-video evidence under textual queries.

## Minimum panel

Pass condition:

- at least 2 models can consume audio and video in the same instance;
- both can return structured JSON-like outputs for diagnosis and action;
- both can process 5 short pilot clips without file-size or duration failures.

Preferred panel for the first pilot:

- 2 Qwen-family closed-source audio-video-capable MLLMs through DashScope;
- 1 Qwen visual/text model as a modality-control baseline;
- 1 question-only sanity baseline;
- 1 quality-only route detector.

Cross-vendor models are optional external validation, not required for the first
pilot.

## Candidate verification table

| Model | Access | Audio input | Video input | Same-instance A/V | Structured output | Limits | Status |
|---|---|---|---|---|---|---|---|
| `qwen3.5-omni-plus` | DashScope API | yes; `audio_tokens` observed | yes; `video_tokens` observed | yes | 5/5 parsed on smoke | short MP4 smoke passed; broader limits still need documentation | first confirmed A/V baseline |
| `qwen3-omni-flash` | DashScope API | yes; `audio_tokens` observed | yes; `video_tokens` observed | yes | 5/5 parsed on smoke | short MP4 smoke passed; broader limits still need documentation | second confirmed Qwen A/V baseline |
| `qwen3.7-plus` | DashScope API | not confirmed; `audio_tokens=null` in video attempt | yes; `video_tokens` observed | no, not counted yet | 1/1 parsed on video attempt; text probe passed | video/text only under current input path | text/video probe only |
| `qwen3.5-omni-flash` | DashScope API | not scored | not scored | inconclusive | 5-clip attempt interrupted after long no-output wait | stream call stalled before first row completed | defer unless needed |

## Required checks

For each model, record:

- exact model name and version/date;
- whether audio and video can be submitted together;
- whether video is sampled by frames, uploaded as video, or preprocessed;
- max audio/video duration;
- file size limit;
- whether timestamps can be referenced;
- structured-output parse rate over 5 clips;
- cost per 160-instance pilot estimate;
- failure modes.

## Five-clip smoke

The first smoke should include:

- 1 audio-necessary clip;
- 1 video-necessary clip;
- 1 audio-video complementary clip;
- 1 corrupted-irrelevant control;
- 1 unrecoverable or conflict-like case.

Output files:

- `outputs/model_feasibility_smoke.jsonl`
- `results/model_feasibility_smoke.md`

Current status:

- `outputs/model_smoke_prompt_pack.jsonl` has been created for the 5 media smoke
  instances.
- DashScope API access was tested without storing credentials in the repository.
- `qwen3.7-plus` text probe passed.
- `qwen3.7-plus` accepted one video diagnosis instance and returned parseable
  JSON, but reported no audio tokens, so it is not counted as a same-instance
  audio-video model yet.
- `qwen3.5-omni-plus` processed all 5 smoke instances with both audio and video
  tokens observed and 5/5 structured JSON parse success.
- `qwen3-omni-flash` processed all 5 smoke instances with both audio and video
  tokens observed and 5/5 structured JSON parse success.
- A `qwen3.5-omni-flash` 5-clip attempt stalled before the first row completed
  and was interrupted; it is not part of the first pilot panel.
- See `results/model_feasibility_smoke.md`.

## Immediate interpretation

The first-pilot model panel can proceed as a Qwen-family panel:

- main A/V model: `qwen3.5-omni-plus`;
- second A/V model: `qwen3-omni-flash`;
- visual/text control: `qwen3.7-plus`.

The next task is no longer model access. The next task is implementing scoring
and tightening the prompt/schema for the 160-instance pilot.

## Kill criteria

Kill or redesign if:

- fewer than 2 models can process audio and video in the same instance;
- structured output parse failure is too high for fair comparison;
- API or local GPU limits make 160 scored instances unrealistic;
- model input APIs force separate audio-only and video-only calls in a way that
  invalidates the diagnosis-to-action setup.

## Decision

The Qwen-only first pilot is acceptable and passes the minimum same-instance
audio-video model gate. Scale only after implementing scorer scripts and
human-verifying the smoke/pilot labels.
