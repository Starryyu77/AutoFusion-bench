# Model Feasibility Smoke

Status: blocked on model access

Checked on: 2026-06-08

## What is ready

The 5-clip prompt pack has been built:

```text
outputs/model_smoke_prompt_pack.jsonl
```

It contains:

- corrupted media path;
- question;
- answer choices;
- gold answer for later scoring;
- bucket;
- corruption type;
- affected modality;
- diagnosis-only prompt template.

Prompt template:

```text
prompts/diagnosis_only_prompt_v0.md
```

## Access check

No model API credentials were found in the remote runtime environment:

| Credential | Status |
|---|---|
| `OPENAI_API_KEY` | missing |
| `ANTHROPIC_API_KEY` | missing |
| `GOOGLE_API_KEY` | missing |
| `GEMINI_API_KEY` | missing |
| `DASHSCOPE_API_KEY` | missing |
| `HF_TOKEN` | missing |
| `HUGGINGFACE_HUB_TOKEN` | missing |

The remote Python environment has client packages installed for OpenAI,
Anthropic, and Google Generative AI, but package availability is not enough to
run the smoke without credentials.

## Local/open-source check

The remote environment has `transformers`, but does not currently have the
extra utilities expected by common open-source audio-video MLLM pipelines:

| Package | Status |
|---|---|
| `transformers` | installed |
| `qwen_vl_utils` | missing |
| `decord` | missing |

No local audio-video MLLM checkpoint has been selected or staged.

## Decision

The media and prompt-pack smoke passed, but the actual model smoke is blocked
until at least one of these is provided:

- an API key for an audio-video-capable MLLM;
- a confirmed local audio-video MLLM checkpoint and its required runtime;
- an explicit decision to run the first model smoke on another machine.

Minimum target remains:

- at least 2 models that can consume audio and video in the same instance;
- structured diagnosis JSON over the 5 prepared smoke instances.
