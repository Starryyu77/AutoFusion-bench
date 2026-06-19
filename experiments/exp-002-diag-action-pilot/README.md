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

## Current Batch

Mini-pilot:

- 10 clean source items;
- 40 corrupted instances;
- source-level modality labels frozen;
- corrupted-instance review is still a draft, not scorer gold.

Current review entry:

- `results/mini_pilot_corrupted_instance_review.zh.md`
- `annotations/mini_pilot.corrupted_instance_review.csv`
- `data/mini_pilot_source_items.jsonl`
- `data/mini_pilot_corruption_manifest.jsonl`
- `data/mini_pilot_source_modality_labels.jsonl`

## Current Gate

Before any model run on the 40-row mini-pilot:

1. fix or replace the `audio_mute` media so mute means silent-present audio,
   not missing audio stream;
2. adjudicate partial / unclear / empty-oracle-route rows;
3. freeze `annotations/mini_pilot.gold.jsonl`;
4. run diagnosis, real action, fixed-rule control, and scorer.

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
- `paper/proposal/2026-06-19-evidence-governance-research-proposal.md`
- `paper/tables/2026-06-19-headline-metric-and-main-table.md`

Project-level rules:

- `governance/EXPERIMENT_CONSTITUTION.md`
- `governance/COLLABORATION_WORKFLOW.md`
- `governance/REPOSITORY_STRUCTURE.md`
- `governance/ROADMAP.md`
