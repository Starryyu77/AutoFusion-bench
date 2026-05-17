# AutoFusion-Bench

> Last refreshed: 2026-05-17

## One-line Goal

Build a diagnostic benchmark for multimodal large language models that tests
modality triage, cross-modal information recovery, and budget-aware modality
routing under controlled text/audio/video perceptual defects.

## Current Hypothesis

Existing multimodal models and MLLMs can often produce a final answer when all
modalities are clean, but they are not reliably able to:

- identify which modality is damaged,
- localize the damaged evidence,
- decide whether the missing information is recoverable from another modality,
- choose the lowest-cost sufficient modality subset, and
- abstain when all available evidence is unrecoverable.

This gap is not captured by standard missing-modality robustness protocols that
mostly measure final-task performance under fixed or random missing patterns.

## Accepted Direction

Use **public raw multimodal datasets + controlled corruption + human-verified
annotation + benchmark protocol**.

This is route B from the accepted incoming handoff:

- Do not start with full self-collection.
- Do not merely modify public datasets and report a few accuracy gains.
- Do construct a new benchmark layer with new tasks, labels, metrics, and
  baseline suite.

Primary incoming handoff:

- `handoffs/incoming/2026-05-17-diagnostic-benchmark-expert-reply.md`

## Benchmark Tasks

| Task | Question |
|---|---|
| T1 Modality health diagnosis | Which modalities are usable, corrupted, missing, or conflicting? |
| T2 Defect localization | Where is the defect: text span, audio time range, or video frame/time region? |
| T3 Cross-modal recovery | Can the damaged information be recovered from another modality, and from where? |
| T4 Budget-aware routing | Under a cost budget, which modality subset should be used? |
| T5 Final task / abstention | What is the task answer, or should the model abstain? |

## Dataset Substrate

Initial candidates should have raw video, raw audio, text/transcripts, and labels.

- Sentiment / emotion: `CMU-MOSI`, `CMU-MOSEI`, `IEMOCAP`, `MELD`
- Chinese or cross-lingual extension: `CH-SIMS`, `CH-SIMS v2`, `M3ED`
- Non-affective extension: audio-centric video understanding or AVQA-style data

MELD remains useful as a diagnostic substrate, but current `exp-001` evidence
warns that it may be too text-dominant for the main positive benchmark signal.

## Annotation Principle

Use scripts for mechanically verifiable labels:

- corrupted modality,
- corruption type,
- severity,
- text span,
- audio timestamp,
- video timestamp / frame region.

Use human verification for semantic labels:

- recoverability,
- recovery source modality,
- evidence span or timestamp,
- oracle routing,
- final answer,
- abstention label.

LLMs may generate candidate annotations, but they must not become unverified
gold labels.

## Evaluation Metrics

Evaluation must be layered rather than only final-task accuracy:

- per-modality corruption F1,
- defect-type macro-F1,
- text span F1 and temporal IoU,
- recoverability macro-F1,
- source-modality accuracy,
- evidence hit rate,
- oracle-route match,
- cost-normalized utility,
- routing regret,
- clean-to-corrupted performance drop,
- coverage-risk and abstention errors.

## Baseline Suite

Minimum baseline families:

- unimodal: text-only, audio-only, video-only,
- full multimodal,
- corrupted multimodal without diagnosis,
- static best route,
- random legal route,
- budget-only route,
- quality-only route,
- joint quality-budget route,
- oracle routing,
- MLLM prompting,
- task-specific robust-fusion or missing-modality methods.

## Current Focus

1. Freeze the taxonomy and annotation schema.
2. Implement a reproducible corruption generator for text/audio/video.
3. Select one affective dataset and one non-affective audio/video dataset for
   feasibility checks.
4. Create a 200-300 clip gold pilot and expand it to 1,000-2,000 corrupted
   instances.
5. Test whether MLLMs fail on diagnosis, recovery, and budget routing before
   scaling to an 8k-15k benchmark.

## Open Risks

- Novelty risk: missing-modality robustness and benchmarks already exist.
- Data risk: common affective datasets may be too text-dominant.
- Annotation risk: recoverability and evidence labels are expensive.
- Reproducibility risk: corruption scripts, datasheets, and annotation
  guidelines must be publishable from the start.
- API risk: true text/audio/video MLLM evaluation may be cost-sensitive and
  model-support dependent.
