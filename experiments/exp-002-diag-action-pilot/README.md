# exp-002: Diagnosis-to-Action Pilot

> Status: active
> Role: current experiment workspace for audio-video evidence governance under textual queries.

## Current Question

Can multimodal LLMs act correctly on their own diagnosis of unreliable
audio-video evidence?

The core phenomenon is the **diagnosis-to-action gap**: a model may correctly
diagnose that audio/video evidence is unreliable, but still choose the wrong
route, answer when it should abstain, or rely on the modality it just marked as
broken.

## Existing Batch

Existing AVQA mini-pilot assets:

- 10 clean source items;
- 40 corrupted instances;
- source-level modality labels frozen;
- corrupted-instance review is still a draft, not scorer gold.

This batch is now treated as pipeline/control material. It should not be used
as the main positive evidence for the paper because AVQA is too easy and can
contain shortcut-solvable cases.

## Current Gate-1 Batch

The next meaningful Gate-1 batch should be rebuilt as:

- 8-10 DAVE source items for audio-video joint / conflict cases;
- 2-4 AVQA source items for audio-only, video-only, or irrelevant-corruption
  controls;
- about 40-50 corrupted instances total.

Current review entry:

- `results/mini_pilot_corrupted_instance_review.zh.md`
- `annotations/mini_pilot.corrupted_instance_review.csv`
- `data/mini_pilot_source_items.jsonl`
- `data/mini_pilot_corruption_manifest.jsonl`
- `data/mini_pilot_source_modality_labels.jsonl`

## Current Gate

Before any model run on the Gate-1 mini-pilot:

1. finish source screening and reject question-only / single-modality shortcut
   cases;
2. generate corruption with consistent audio+video containers;
3. adjudicate partial / unclear / empty-oracle-route rows;
4. freeze `annotations/mini_pilot.gold.jsonl`;
5. run diagnosis, real action, fixed-rule control, and scorer.

Gold freeze is a Decision Team action. AI Agent and research executors may
prepare recommendations, validators, and scorer checks, but should not freeze
gold without explicit owner approval.

## Directory Contract

```text
data/          source items, corruption manifests, source modality labels
annotations/   draft, local export, reviewed, and future gold JSONL/CSV
prompts/       diagnosis/action prompts and schemas
scripts/       batch builders, adapters, runners, validators, scorers
results/       reviewed outputs, metrics, per-instance summaries
outputs/       ignored local/model outputs
data/media/    ignored local media
```

Do not put large media, raw dataset packages, API keys, virtualenvs, or
temporary outputs into GitHub.

## Decision Docs

Decision Team planning documents for this experiment live outside the experiment
workspace:

- `decision/plans/exp-002/2026-06-19-gold-freeze-adjudication-plan.md`
- `decision/plans/exp-002/2026-06-19-substrate-derisk.md`
- `decision/plans/exp-002/2026-06-19-experiment-plan.zh.md`
- `paper/proposal/2026-06-19-evidence-governance-research-proposal.md`
- `paper/tables/2026-06-19-headline-metric-and-main-table.md`

Project-level rules:

- `governance/EXPERIMENT_CONSTITUTION.md`
- `governance/COLLABORATION_WORKFLOW.md`
- `governance/REPOSITORY_STRUCTURE.md`
- `governance/ROADMAP.md`
