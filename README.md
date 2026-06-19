# ENACT

> 如果你是项目负责人、组会汇报人或新加入的执行同学，请先看
> [START_HERE.zh.md](START_HERE.zh.md)。那里是当前项目导航、实验位置和下一步计划。
> 对外项目 / benchmark 名称是 **ENACT**；当前工作仓库仍叫 `AutoFusion-bench`。

ENACT is currently organized around one research question:

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
- DAVE as the main substrate for audio-video joint / conflict cases;
- AVQA / AVQA-videos as pipeline and control substrates;
- FortisAVQA and MUSIC-AVQA v2 as backups;
- Qwen Omni models as the first verified audio-video model panel;
- MELD / MOSI / MOSEI / IEMOCAP are not the current main positive substrate.

Current near-term target:

```text
DAVE+AVQA mini-pilot -> about 40-50 corrupted instances -> annotation -> model diagnosis/action -> scorer
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

- [ENACT core proposal](paper/proposal/2026-06-19-ENACT-core-proposal.zh.md)
- [Naming decision](decision/proposals/2026-06-19-naming-decision-ENACT.zh.md)
- [Project overview](decision/handoffs/outgoing/2026-06-13-autofusion-project-overview.md)
- [Experiment constitution](governance/EXPERIMENT_CONSTITUTION.md)
- [Experiment constitution v2 note](governance/2026-06-19-experiment-constitution-v2.zh.md)
- [Collaboration workflow](governance/COLLABORATION_WORKFLOW.md)
- [Repository structure](governance/REPOSITORY_STRUCTURE.md)
- [Roadmap](governance/ROADMAP.md)
- [AAAI-27 timeline and gates](governance/2026-06-19-aaai27-timeline-and-gates.zh.md)
- [Repository audit](governance/2026-06-13-repo-audit.md)
- [Research proposal](paper/proposal/2026-06-19-evidence-governance-research-proposal.md)
- [Detailed research proposal](paper/proposal/2026-06-19-detailed-research-proposal.zh.md)
- [Experiment plan](decision/plans/exp-002/2026-06-19-experiment-plan.zh.md)
- [Active experiment runbook](experiments/exp-002-diag-action-pilot/RUNBOOK.md)
- [Annotation workflow spec](skills/autofusion-annotation/references/data_spec.md)

## Repository Organization

| Path | Role |
|---|---|
| `governance/` | Constitution, collaboration workflow, roadmap, audit, and repository structure. |
| `decision/` | Decision Team proposals, plans, reviews, literature notes, handoffs, and ops notes. |
| `experiments/exp-002-diag-action-pilot/` | Active diagnosis-to-action pilot. |
| `paper/` | Manuscript-facing proposal, story, tables, and drafts. |
| `skills/autofusion-annotation/` | Reusable annotation workflow and schema contract. |
| `memory/` | Current project status and recovery pointers. |
| `archive/2026-06-pre-exp002-reset/` | Historical exp-001 / May 2026 material moved out of the active workspace. |
| `external/` | Ignored local-only incoming artifacts and Drive mirrors. |

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
