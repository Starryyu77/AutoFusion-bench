# Pilot Model Feasibility

Status: blocked on model access

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
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | pending |

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
- Actual model calls have not run because no remote API key or staged local
  audio-video MLLM is available.
- See `results/model_feasibility_smoke.md`.

## Kill criteria

Kill or redesign if:

- fewer than 2 models can process audio and video in the same instance;
- structured output parse failure is too high for fair comparison;
- API or local GPU limits make 160 scored instances unrealistic;
- model input APIs force separate audio-only and video-only calls in a way that
  invalidates the diagnosis-to-action setup.

## Decision

Blocked until model access is configured. The media and prompt-pack parts of the
5-clip smoke are ready.
