# 2026-05-17 multimodal diagnostic benchmark meeting memory

Updated: 2026-05-17

## Scope

This note indexes the new meeting-derived direction from
`/Users/starryyu/Downloads/多模态模型数据集研讨.txt`.

The user explicitly asked not to force-associate this direction with the
previous Memory project. Treat it as an AutoFusion-Bench research direction that
may be related to exp-001 only through the shared reliability/budget/modality
choice theme.

## Current framing

Working framing:

> A diagnostic benchmark for MLLMs that evaluates modality availability
> diagnosis, cross-modal information recovery, and budget-aware modality
> routing under text/audio/video perceptual degradation.

Do not reduce this to architecture search or generic missing-modality
classification. The meeting shifted away from first modifying fusion
architectures and toward benchmarking whether models know when to read, listen,
watch, combine modalities, or abstain.

## Durable artifact

Detailed meeting summary, literature review, novelty boundary, AAAI starting
plan, and risks were written to:

`handoffs/outgoing/2026-05-17-multimodal-diagnostic-benchmark-meeting-literature.md`

Accepted incoming review and stronger project reset wording were saved to:

`handoffs/incoming/2026-05-17-diagnostic-benchmark-expert-reply.md`

## Literature judgment

Adjacent work is dense:

- low-quality multimodal fusion surveys
- missing-modality robustness methods
- missing-modality benchmarks such as MissBench and MissMAC-Bench
- budgeted or dynamic modality selection
- MLLM cross-modal inconsistency benchmarks

The proposed publishable gap is narrower:

- sample-level defect diagnosis
- evidence localization for missing/degraded content
- recoverability labels mapping a broken modality to compensating evidence in
  another modality
- budget-aware modality/tool routing labels
- MLLM evaluation on raw text/audio/video rather than only feature-level robust
  classifiers

## Recommended next action

Freeze a small taxonomy and run a 30-sample pilot before any broad annotation:

- modality availability
- defect type and severity
- defect location
- recoverability
- recovery source and evidence span/timestamp
- budget route
- final task answer and evidence

Candidate datasets for feasibility check: one affective dataset
(`MELD` or `CMU-MOSEI`) plus one audio-video QA dataset (`MUSIC-AVQA` or
`AVQA`). Existing exp-001 MELD results caution that MELD is likely
text-dominant and should not be assumed to provide the main positive benchmark
signal.

## Accepted route

Use route B:

> public raw multimodal datasets + controlled corruption + human-verified
> annotation + benchmark protocol.

Do not frame the next paper as pure model improvement on existing datasets. Do
not claim novelty as generic missing-modality robustness. The novelty target is
modality triage, evidence-grounded cross-modal recovery, and cost-aware routing
for MLLMs under controlled perceptual degradation.
