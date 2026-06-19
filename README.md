# AutoFusion-Bench

AutoFusion-Bench is currently being organized around one research question:

> Can multimodal large language models act correctly on their own diagnosis of unreliable multimodal evidence?

The active project is not a new fusion model and not a generic missing-modality robustness benchmark. The current goal is to build and validate a benchmark protocol for **unreliable multimodal evidence governance**, centered on the **diagnosis-to-action gap**.

## Current Story

Real multimodal inputs are often unreliable:

- audio can be muted, noisy, shifted, or replaced;
- video can be blurred, occluded, frozen, or temporally misaligned;
- text evidence, when present, can be incomplete, erroneous, or conflicting;
- some tasks require audio, some require video, and some require both.

A reliable MLLM should not only answer the final question. It should also:

1. diagnose which evidence is reliable or unreliable;
2. judge whether missing information is recoverable from another modality;
3. choose the right evidence route under budget or risk constraints;
4. abstain when evidence is insufficient;
5. execute the final task when the selected evidence is sufficient.

The key hypothesis is:

> MLLMs may diagnose unreliable evidence but still route, answer, recover, or abstain incorrectly based on that diagnosis.

## Active Experiment

The active experiment is:

```text
experiments/exp-002-diag-action-pilot/
```

Scope:

- audio-video evidence governance under textual queries;
- AVQA / AVQA-videos as the first substrate;
- MUSIC-AVQA as backup;
- Qwen Omni models as the first verified audio-video model panel;
- MELD / MOSI / MOSEI / IEMOCAP are not the current main positive substrate.

Current near-term target:

```text
10 clean source items -> about 40 corrupted instances -> annotation -> model diagnosis/action -> scorer
```

Next scale target:

```text
40 clean source items -> about 160 scored instances
```

## Current Status

The exp-002 smoke chain is running end to end:

- AVQA metadata and a 15-video sample were staged on `ntu-gpu43`;
- 5 source MP4 files and 5 corrupted MP4 files retained audio and video streams;
- `qwen3.5-omni-plus` and `qwen3-omni-flash` processed same-instance audio-video smoke cases;
- local annotation app, annotation validator, scorer, diagnosis prompt, action prompt, and fixed-rule action path are implemented;
- a 4-row smoke gold set is frozen;
- real-action smoke scoring has run.

These smoke results prove the protocol can run. They are not paper-level findings.

## Canonical Docs

- [Project overview](handoffs/outgoing/2026-06-13-autofusion-project-overview.md)
- [Experiment constitution](governance/EXPERIMENT_CONSTITUTION.md)
- [Roadmap](governance/ROADMAP.md)
- [Repository audit](governance/2026-06-13-repo-audit.md)
- [Active experiment runbook](experiments/exp-002-diag-action-pilot/RUNBOOK.md)
- [Annotation workflow spec](skills/autofusion-annotation/references/data_spec.md)

## Repository Organization

| Path | Role |
|---|---|
| `experiments/exp-002-diag-action-pilot/` | Active diagnosis-to-action pilot. |
| `skills/autofusion-annotation/` | Reusable annotation workflow and schema contract. |
| `governance/` | Experiment constitution, cleanup policy, and roadmap. |
| `handoffs/outgoing/` | Current project overview, junior brief, and expert handoffs. |
| `paper/2026-06-08-evidence-governance-story.md` | Current paper story after expert feedback. |
| `reviews/` | Expert feedback synthesis and review notes. |
| `archive/2026-06-pre-exp002-reset/` | Historical exp-001 / May 2026 material moved out of the active workspace. |

## Cleanup Boundary

Historical exp-001 / MELD materials and older May 2026 planning files have been moved under:

```text
archive/2026-06-pre-exp002-reset/
```

Large old reference packs are stored locally under:

```text
archive/2026-06-pre-exp002-reset/local-only/
```

That local-only directory is intentionally ignored by Git.

## Links

- Project GitHub: https://github.com/Starryyu77/AutoFusion-bench
- AVQA official project page: http://mn.cs.tsinghua.edu.cn/avqa/
- AVQA original GitHub: https://github.com/AlyssaYoung/AVQA
- AVQA-videos Hugging Face package: https://huggingface.co/datasets/juyil/AVQA-videos
