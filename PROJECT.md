# AutoFusion-Bench Project Snapshot

> Last refreshed: 2026-06-13

## One-line Goal

Build a benchmark protocol for evaluating whether multimodal large language models can govern unreliable audio-video evidence: diagnose evidence defects, judge recoverability, choose the right evidence route, and abstain when evidence is insufficient.

## Active Hypothesis

MLLMs may show a **diagnosis-to-action gap**:

> They can sometimes identify that a modality is damaged, conflicting, or insufficient, but still make an incorrect downstream action such as choosing the wrong route, answering when they should abstain, or ignoring recoverable evidence.

## Active Scope

The current pilot is intentionally scoped to:

- audio-video evidence governance under textual queries;
- AVQA / AVQA-videos first;
- MUSIC-AVQA as backup;
- Qwen Omni models as the first verified model panel;
- no paper-level claim from the 4-row smoke result.

The project should not currently claim full text-audio-video evidence governance unless a real text-evidence substrate, such as subtitles, ASR transcripts, or captions, is added and validated.

## Active Experiment

```text
experiments/exp-002-diag-action-pilot/
```

Current target:

1. prepare 80-120 candidate AVQA-style clean source items;
2. select 10 high-quality source items for a mini-pilot;
3. generate about 40 corrupted instances;
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

Observed in smoke:

- `qwen3.5-omni-plus`: policy action accuracy 1.0, governed success 0.75 on the 4-row smoke gold;
- `qwen3-omni-flash`: policy action accuracy 0.75, governed success 0.5 on the same smoke gold;
- both models selected the right visual route in one conflict-like case but produced a final answer mismatch, reinforcing that policy action correctness and final answer correctness must remain separate.

Boundary:

- This is protocol evidence, not a paper-level finding.
- The next meaningful evidence gate is the 10-source / 40-instance mini-pilot.

## Current Canonical Files

- `governance/EXPERIMENT_CONSTITUTION.md`
- `governance/ROADMAP.md`
- `governance/2026-06-13-repo-audit.md`
- `handoffs/outgoing/2026-06-13-autofusion-project-overview.md`
- `handoffs/outgoing/2026-06-09-mini-pilot-junior-brief.md`
- `memory/tasks/exp-002.md`
- `experiments/exp-002-diag-action-pilot/RUNBOOK.md`

## Next Actions

1. Finish local repository cleanup on `codex/repo-governance-cleanup`.
2. Decide how to synchronize local branch state with GitHub.
3. Restore `ntu-gpu43` SSH access and audit the server checkout before server cleanup.
4. Have the junior collaborator prepare AVQA candidate sources.
5. Run the 10-source / 40-instance mini-pilot.
6. Use the result to decide whether to scale to 40 sources / 160 scored instances.
