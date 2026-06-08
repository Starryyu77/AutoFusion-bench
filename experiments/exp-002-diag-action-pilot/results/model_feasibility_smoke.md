# Model Feasibility Smoke

Status: Qwen-family audio-video panel passed smoke

Checked on: 2026-06-08

## Prepared input

The 5-clip prompt pack was built at:

```text
outputs/model_smoke_prompt_pack.jsonl
```

It contains corrupted media path, question, answer choices, gold answer for
later scoring, bucket, corruption type, affected modality, and the
diagnosis-only prompt template:

```text
prompts/diagnosis_only_prompt_v0.md
```

## DashScope / Qwen access check

DashScope access was tested on `ntu-gpu43` without storing credentials in the
repository.

| Model | Check | Result | Interpretation |
|---|---|---:|---|
| `qwen3.7-plus` | text probe | passed | API credentials and OpenAI-compatible client work |
| `qwen3.7-plus` | 1-clip video diagnosis smoke | passed parse | accepts video input, but current usage reports no audio tokens |
| `qwen3.5-omni-plus` | 5-clip audio-video diagnosis smoke | passed parse | consumes both audio and video tokens in the same instance |
| `qwen3-omni-flash` | 5-clip audio-video diagnosis smoke | passed parse | consumes both audio and video tokens in the same instance |
| `qwen3.5-omni-flash` | 5-clip audio-video diagnosis smoke | inconclusive | stream call stalled before first row completed; interrupted |

Local output files:

```text
outputs/qwen37_text_probe.jsonl
outputs/qwen37_plus_video_smoke_attempt.jsonl
outputs/qwen35_omni_video_smoke.jsonl
outputs/qwen3_omni_flash_video_smoke.jsonl
outputs/qwen3_omni_flash_video_smoke_attempt.jsonl
```

The first successful audio-video model smoke is `qwen3.5-omni-plus`, not
`qwen3.7-plus`. The `qwen3.7-plus` video attempt reported `video_tokens` but
`audio_tokens=null`, so it should not be counted yet as a same-instance
audio-video model for this pilot.

The second successful audio-video model smoke is `qwen3-omni-flash`. This makes
the first pilot a Qwen-family model panel rather than a single-model smoke.

## Smoke results

| Model | Instances | Status OK | JSON parsed | Audio tokens | Video tokens | Notes |
|---|---:|---:|---:|---|---|---|
| `qwen3.5-omni-plus` | 5 | 5 | 5 | present in all 5 | present in all 5 | first valid A/V smoke |
| `qwen3-omni-flash` | 5 | 5 | 5 | present in all 5 | present in all 5 | second valid Qwen A/V smoke |
| `qwen3.7-plus` | 1 | 1 | 1 | not reported | present | video/text probe only for now |
| `qwen3.5-omni-flash` | 5 attempted | 0 completed | 0 | not scored | not scored | deferred after long no-output wait |

Observed `qwen3.5-omni-plus` usage:

- prompt tokens per instance: 5,454 to 6,550;
- audio tokens per instance: 58 to 72;
- video tokens per instance: 4,842 to 5,942;
- completion tokens per instance: 226 to 267.

Observed `qwen3-omni-flash` usage:

- prompt tokens per instance: 5,475 to 6,562;
- audio tokens per instance: 113 to 136;
- video tokens per instance: 4,842 to 5,942;
- completion tokens per instance: 211 to 237.

## Qualitative audit

This is an access and format smoke, not a research result.

Useful signals:

- `qwen3.5-omni-plus` can process the prepared corrupted MP4 files and return
  structured diagnosis JSON.
- `qwen3-omni-flash` can also process the same prepared corrupted MP4 files and
  return structured diagnosis JSON.
- The audio-mute case was diagnosed as audio missing and unrecoverable.
- The corrupted-irrelevant visual blur control was diagnosed as answer
  irrelevant and recoverable from audio.

Issues found:

- The model sometimes fills the inner JSON `model` field with unrelated names
  such as `gpt-4o`, `Qwen-Omni`, or the prompt name. Evaluation must use the
  outer logged model name, not the model self-report field.
- Defect localization is coarse and sometimes inconsistent; this confirms that
  location scoring should be separate from high-level diagnosis scoring.
- Some smoke buckets expose task-conditioned ambiguity. For example, an
  apparently visual animal question can be partly recoverable from cowbell
  audio, while an audio replacement may be irrelevant for a location question.
  This reinforces the need for human-verified `modality_necessity` and
  `corruption_relevance` labels instead of treating generator metadata as final
  ground truth.

## Decision

The previous access blocker is removed, and the first-pilot model panel can
proceed as a Qwen-only panel:

- keep `qwen3.5-omni-plus` as the first confirmed same-instance audio-video
  MLLM baseline;
- keep `qwen3-omni-flash` as the second confirmed same-instance audio-video
  MLLM baseline;
- keep `qwen3.7-plus` as a text/video probe unless a different input mode shows
  real audio consumption;
- do not rely on `qwen3.5-omni-flash` unless its stalled stream behavior is
  resolved;
- revise the prompt/schema so the model does not need to self-report model
  identity;
- add a scoring script that separates parse success, high-level diagnosis,
  relevance/recoverability, localization, and action consistency.
