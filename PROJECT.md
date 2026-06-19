# AutoFusion-Bench Project Snapshot

> Last refreshed: 2026-06-19

## One-line Goal

Build a benchmark protocol for evaluating whether multimodal large language models can govern unreliable audio-video evidence: diagnose evidence defects, judge recoverability, choose the right evidence route, and abstain when evidence is insufficient.

## Active Hypothesis

MLLMs may show a **diagnosis-to-action gap**:

> They can sometimes identify that a modality is damaged, conflicting, or insufficient, but still make an incorrect downstream action such as choosing the wrong route, answering when they should abstain, or ignoring recoverable evidence.

## Active Scope

The current pilot is intentionally scoped to:

- audio-video evidence governance under textual queries;
- DAVE for audio-video joint / conflict cases;
- AVQA / AVQA-videos for pipeline validation and control cases;
- FortisAVQA and MUSIC-AVQA v2 as backups;
- Qwen Omni models as the first verified model panel;
- no paper-level claim from the 4-row smoke result.

The project should not currently claim full text-audio-video evidence governance unless a real text-evidence substrate, such as subtitles, ASR transcripts, or captions, is added and validated.

## Active Experiment

```text
experiments/exp-002-diag-action-pilot/
```

Current target:

1. screen 20-30 DAVE candidates and select 8-10 true audio-video joint / conflict source items;
2. keep 2-4 AVQA control source items from existing assets;
3. generate about 40-50 corrupted instances;
4. annotate source quality, post-corruption answerability, recoverability, oracle route, and abstention;
5. run diagnosis-only prompts;
6. run model action from frozen diagnosis;
7. run fixed-rule action from the same frozen diagnosis;
8. score diagnosis, policy action, false answer, and governed success.

## Current Evidence

Completed:

- AVQA metadata and a 15-video sample staged on `ntu-gpu43`;
- 5 source/corrupted MP4 smoke pairs validated for audio and video streams;
- `qwen3.5-omni-plus` and `qwen3-omni-flash` verified on same-instance audio-video smoke inputs;
- local annotation app implemented and smoke-tested;
- annotation sheet generator, validator, scorer, diagnosis prompt, action prompt, and fixed-rule path implemented;
- 4-row smoke gold frozen;
- real-action smoke run completed.
- AVQA 10-source / 40-corrupted draft exists, but AVQA is now treated as pipeline/control rather than the main positive substrate.

Observed in smoke:

- `qwen3.5-omni-plus`: policy action accuracy 1.0, governed success 0.75 on the 4-row smoke gold;
- `qwen3-omni-flash`: policy action accuracy 0.75, governed success 0.5 on the same smoke gold;
- both models selected the right visual route in one conflict-like case but produced a final answer mismatch, reinforcing that policy action correctness and final answer correctness must remain separate.

Boundary:

- This is protocol evidence, not a paper-level finding.
- The next meaningful evidence gate is a DAVE+AVQA mini-pilot, roughly
  10-12 source items and 40-50 corrupted instances.

## Current Canonical Files

- `governance/EXPERIMENT_CONSTITUTION.md`
- `START_HERE.zh.md`
- `governance/2026-06-19-experiment-constitution-v2.zh.md`
- `governance/COLLABORATION_WORKFLOW.md`
- `governance/REPOSITORY_STRUCTURE.md`
- `governance/ROADMAP.md`
- `governance/2026-06-13-repo-audit.md`
- `decision/handoffs/outgoing/2026-06-13-autofusion-project-overview.md`
- `decision/handoffs/outgoing/2026-06-09-mini-pilot-junior-brief.md`
- `paper/proposal/2026-06-19-evidence-governance-research-proposal.md`
- `paper/proposal/2026-06-19-detailed-research-proposal.zh.md`
- `decision/plans/exp-002/2026-06-19-experiment-plan.zh.md`
- `memory/tasks/exp-002.md`
- `experiments/exp-002-diag-action-pilot/RUNBOOK.md`

## Next Actions

1. Review and merge the dedicated cleanup PR from `codex/repo-structure-cleanup`.
2. After merge, treat `governance/`, `decision/`, `experiments/`, `paper/`, `memory/`, and `archive/` as the default workspace layout.
3. Restore `ntu-gpu43` SSH access and audit the server checkout before server cleanup.
4. Have the execution team screen DAVE candidates and retain AVQA controls.
5. Build the DAVE+AVQA mini-pilot and run Gate 1.
6. Use the result to decide whether to scale to 40 sources / 160 scored instances.
