# Pilot Model Feasibility

Status: first API model smoke passed; need second same-instance audio-video model

## Purpose

Identify a minimum model panel for testing diagnosis-to-action behavior on
audio-video evidence under textual queries.

## Minimum panel

Pass condition:

- at least 2 models can consume audio and video in the same instance;
- both can return structured JSON-like outputs for diagnosis and action;
- both can process 5 short pilot clips without file-size or duration failures.

Preferred panel:

- 2 closed-source audio-video-capable MLLMs if accessible;
- 2 open-source audio-video-capable MLLMs if feasible on NTU43;
- 1 question-only sanity baseline;
- 1 quality-only route detector.

## Candidate verification table

| Model | Access | Audio input | Video input | Same-instance A/V | Structured output | Limits | Status |
|---|---|---|---|---|---|---|---|
| `qwen3.5-omni-plus` | DashScope API | yes; `audio_tokens` observed | yes; `video_tokens` observed | yes | 5/5 parsed on smoke | short MP4 smoke passed; broader limits still need documentation | first confirmed A/V baseline |
| `qwen3.7-plus` | DashScope API | not confirmed; `audio_tokens=null` in video attempt | yes; `video_tokens` observed | no, not counted yet | 1/1 parsed on video attempt; text probe passed | video/text only under current input path | text/video probe only |

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
- See `results/model_feasibility_smoke.md`.

## Immediate interpretation

The access problem is solved for the first model. The experiment still has not
passed the full model feasibility gate because the minimum panel requires at
least 2 same-instance audio-video models. The next model-feasibility task is to
find a second A/V-capable baseline or explicitly redesign the pilot around a
single-model diagnostic plus non-MLLM controls.

## Kill criteria

Kill or redesign if:

- fewer than 2 models can process audio and video in the same instance;
- structured output parse failure is too high for fair comparison;
- API or local GPU limits make 160 scored instances unrealistic;
- model input APIs force separate audio-only and video-only calls in a way that
  invalidates the diagnosis-to-action setup.

## Decision

Access is configured for the first confirmed audio-video model. Do not scale the
pilot yet: the next gate is confirming a second same-instance audio-video model
or formally redesigning the model panel.
