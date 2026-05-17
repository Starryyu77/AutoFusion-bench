# AutoFusion-Bench

AutoFusion-Bench is being reframed as a benchmark for **modality triage,
cross-modal recovery, and budget-aware modality routing** in multimodal large
language models.

The project should not be positioned as simply improving performance on public
datasets. The intended AAAI contribution is to use public raw multimodal data as
the substrate, then add a new benchmark layer: controlled perceptual defects,
human-verified recoverability and evidence labels, and cost-aware routing
evaluation.

## Research Question

When text, audio, and video inputs vary in quality and inference budget is
limited, can a model decide:

- which modalities are usable,
- where each modality is damaged,
- whether missing information can be recovered from another modality,
- which modality subset should be used under a budget, and
- when the evidence is insufficient and the model should abstain?

## Current Positioning

Do not claim novelty as "missing modality robustness." That space already has
close prior work. The novelty target is narrower and stronger:

> Evaluate whether MLLMs can explicitly perform modality triage: identify which
> modality is broken, localize the defect, determine recoverability, choose the
> healthy modality to compensate, and route under budget-constrained inference.

## Benchmark Layer

The first benchmark version should use public raw datasets with text/audio/video
alignment, then generate controlled corruptions and structured labels.

Core subtasks:

1. **T1 Modality health diagnosis** - detect usable, corrupted, missing, or
   conflicting modalities.
2. **T2 Defect localization** - locate text spans, audio timestamps, and video
   frame/time regions affected by corruption.
3. **T3 Cross-modal recovery** - decide whether damaged information can be
   recovered and from which modality evidence.
4. **T4 Budget-aware routing** - select a valid modality subset under a cost
   budget.
5. **T5 Final task / abstention** - answer the downstream task or abstain when
   evidence is unrecoverable.

## Current Claim Boundary

Existing `exp-001` MELD feature-level work remains useful historical evidence:
it validated parts of the reliability-budget protocol, but MELD was
text-dominant and should not be treated as the main positive benchmark result.
The next direction is a richer diagnostic benchmark layer, not another broad
MELD tuning loop.

## Repository Map

- `handoffs/incoming/` - external or user-provided reviews and accepted
  direction-setting notes.
- `handoffs/outgoing/` - outgoing summaries and handoff packets.
- `data/` - dataset substrate selection and corruption-generation notes.
- `evals/` - benchmark task, metric, and baseline protocol notes.
- `lit/` - literature positioning.
- `experiments/` - historical and active experiment folders.
- `formalism.md` - current benchmark definitions and scoring.
- `claims.md` - candidate claims and evidence boundaries.
- `PROJECT.md` - current project snapshot.
