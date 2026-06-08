# 2026-05-17 multimodal diagnostic benchmark meeting memory

Updated: 2026-05-18

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

## Explainer artifact

Created a standalone Chinese HTML explainer for the current idea:

`handoffs/outgoing/2026-05-17-diagnostic-benchmark-explainer.html`

The page explains the project as "模型什么时候该读、听、看？" and covers the
positioning, five benchmark task layers, public-data-plus-corruption pipeline,
annotation split, evaluation metrics, and seven-week execution route.

## Proposal artifact

Created a formal proposal version on 2026-05-18:

- `paper/2026-05-18-diagnostic-benchmark-proposal.md`
- `paper/2026-05-18-diagnostic-benchmark-proposal.html`

The proposal is Chinese-first and covers background, related-work gap,
objectives, benchmark design, data and annotation scheme, metrics, baselines,
expected contributions, execution plan, risks, deliverables, and one-sentence
positioning.

Updated the proposal on 2026-05-18 with a references section focused on recent
2024-2026 work:

- peer-reviewed anchors from ACL 2024, EMNLP 2024, JMLR 2024, CVPR 2025,
  Findings ACL 2025, ICCV 2025, and AAAI 2026
- direct 2026 novelty-boundary references around SMCIR, CrossCheck-Bench,
  MissMAC-Bench, MissBench, and UMQ
- AAAI policy / supplementary-material references and Datasheets for Datasets
  as benchmark-release documentation support

## Reference pack artifact

Created a local reference pack on 2026-05-18:

- `paper/reference-pack/pdfs/`: 13 downloaded PDFs for R1-R12 and R15
- `paper/reference-pack/manifest.md`: source URL and SHA-256 mapping
- `paper/reference-pack/web-links/`: web-only records for R13/R14 AAAI pages

The pack intentionally excludes R13/R14 as PDFs because they are conference
policy/documentation pages rather than research papers.

## Expert review handoff

Created a self-contained expert-review handoff on 2026-06-08:

`handoffs/outgoing/2026-06-08-diagnostic-benchmark-expert-review.md`

The handoff asks an external expert to evaluate:

- whether the proposal has real value and innovation
- how it compares with same-period missing-modality, modality-diagnosis,
  dynamic-selection, MLLM-evaluation, and cross-modal-inconsistency work
- what should change in task, data, annotation, baselines, and failure analysis
- what work level would be required for an AAAI-style conference submission

## Expert replies synthesis

Integrated two external expert replies on 2026-06-08:

`reviews/2026-06-08-expert-replies-synthesis.md`

Consensus:

- continue the direction, but reposition it as unreliable multimodal evidence
  governance rather than five parallel new tasks
- do not claim novelty for generic missing modality, modality diagnosis,
  cross-modal recovery, conflict detection, or budget-aware routing
- make the core paper claim the diagnosis-to-action gap: models may diagnose
  unreliable evidence but still route, recover, answer, or abstain incorrectly
- use AVQA / MUSIC-AVQA-style audio-video data as the main substrate, not
  MELD/MOSEI as the main positive benchmark signal
- treat 30-50 source examples only as a pilot; an AAAI-style submission needs a
  larger human-verified benchmark, strong baselines, artifact controls, and a
  clear headline failure finding

## Story reset

Created the revised paper-story document on 2026-06-08:

`paper/2026-06-08-evidence-governance-story.md`

The story is now:

> We are not testing only whether MLLMs answer correctly under damaged
> modalities. We are testing whether they can govern unreliable multimodal
> evidence: diagnose unreliable evidence, judge recoverability, choose the
> correct evidence route under constraint, and abstain when evidence is
> insufficient. The central phenomenon to test is the diagnosis-to-action gap.

This story reset updates the project claim boundary in `claims.md` as C005.
The next step should be a pilot spec for measuring diagnosis-to-action gap, not
another broad proposal rewrite.

## Pilot design handoff

Created a self-contained pilot-design handoff for expert review on 2026-06-08:

`handoffs/outgoing/2026-06-08-diagnosis-to-action-pilot-expert-review.md`

The pilot proposal focuses on:

- validating diagnosis-to-action gap before scaling
- using AVQA / MUSIC-AVQA-style data as the primary substrate
- selecting 30-50 source items and 100-200 scored corruption episodes
- manually annotating recoverability, evidence, oracle route, and abstention
- comparing direct, explicit-diagnosis, two-stage, oracle, and
  stated-diagnosis-then-rule settings
- using conditional action failure and rule lift as the main pilot signals

## Pilot expert replies and v2 update

Integrated two expert replies on the pilot plan on 2026-06-08:

- `reviews/2026-06-08-pilot-expert-replies-synthesis.md`
- `handoffs/outgoing/2026-06-08-diagnosis-to-action-pilot-v2.md`

Main corrections:

- narrow pilot claim to audio-video evidence governance under textual queries
  because AVQA / MUSIC-AVQA question text is not transcript evidence
- add an optional small transcript/caption/ASR subset to test whether full
  text-audio-video evidence governance is feasible for the scaled benchmark
- make diagnosis-action self-inconsistency the primary pilot signal, with
  gold-conditional action failure as supporting evidence
- fix `stated-diagnosis-then-rule` into a within-diagnosis comparison: reuse the
  same frozen model diagnosis for both model action and fixed-rule action
- split action correctness into policy correctness, task execution under oracle
  route, and governed success
- add `modality_necessity` and `corruption_relevance` fields
- make recoverability task-conditioned and evidence-pointer-gated
- reduce routing from a major novelty claim to constrained evidence selection
- add rough go/no-go thresholds for self-inconsistency, conditional action
  failure, rule lift, final-answer masking, artifact controls, and annotation
  agreement

## Diagnosis-to-action pilot execution plan

Created the concrete experiment design draft on 2026-06-08:

`plans/2026-06-08-exp-diagnosis-to-action-pilot.md`

This plan translates expert feedback into an executable two-week pilot:

- primary scope is audio-video evidence governance under textual queries, not
  full text-audio-video validation
- target size is 40 source items and about 160 scored corruption instances
- candidate pool starts from 80-120 source items and filters by modality
  necessity
- main measurements are self-inconsistency, policy action accuracy,
  conditional action failure, within-diagnosis rule lift, and false answer rate
  on unrecoverable cases
- model action and fixed-rule action must use the same frozen diagnosis-only
  output
- pilot includes clean-hard, corrupted-irrelevant, quality-only detector,
  question-only sanity, oracle route, and oracle defect-location controls
- next project action should be `/lab-exp-init` with suggested shortname
  `diag-action-pilot`, after model and dataset feasibility are checked

## ntu-gpu43 readiness for new pilot

Checked `ntu-gpu43` live on 2026-06-08 and saved the snapshot:

`infra/gpu/2026-06-08-ntu-gpu43-pilot-check.md`

Result:

- host is reachable as `ntu-gpu43`, user `s125mdg43_10`
- direct GPU server, not Slurm
- 4 x RTX A5000 24 GB are effectively idle
- `/usr1` has about 2.4T available
- remote repo exists at `/usr1/home/s125mdg43_10/projects/AutoFusion-bench`
  but is behind the current local project state
- MELD exists at `/usr1/home/s125mdg43_10/datasets/MELD`, with annotations,
  official features, and raw media
- for the new diagnosis-to-action pilot, use the server hardware but do not use
  MELD as the main positive substrate; stage AVQA / MUSIC-AVQA-style data for
  the primary pilot and keep MELD only as a diagnostic/control substrate

## Remote proposal / pilot sync

Synced the current local proposal and pilot-planning files to `ntu-gpu43` on
2026-06-08.

Remote root:

`/usr1/home/s125mdg43_10/projects/AutoFusion-bench`

Verified remote paths:

- `plans/2026-06-08-exp-diagnosis-to-action-pilot.md`
- `paper/2026-06-08-evidence-governance-story.md`
- `handoffs/outgoing/2026-06-08-diagnosis-to-action-pilot-v2.md`
- `reviews/2026-06-08-pilot-expert-replies-synthesis.md`
- `infra/gpu/2026-06-08-ntu-gpu43-pilot-check.md`

Important boundary:

> Use `ntu-gpu43` as the execution machine, but proceed with the new
> diagnosis-to-action / AVQA-MUSIC-AVQA audio-video evidence governance pilot.
> Do not restart the old MELD-first experiment as the main line.

## exp-002 initialized

Initialized the active diagnosis-to-action pilot on 2026-06-08:

- Experiment id: `exp-002`
- Shortname: `diag-action-pilot`
- Scope lock: `.lablock/locks/exp-002.scope.lock`
- Experiment folder: `experiments/exp-002-diag-action-pilot/`
- Matrix: `mat-002 evidence-governance-pilot`
- Variable: `var-002 diagnosis_to_action_protocol`
- Variant: `audio_video_textual_query_pilot`

Local experiment assets created:

- `experiments/exp-002-diag-action-pilot/RUNBOOK.md`
- `experiments/exp-002-diag-action-pilot/data/pilot_dataset_feasibility.md`
- `experiments/exp-002-diag-action-pilot/data/pilot_model_feasibility.md`
- `experiments/exp-002-diag-action-pilot/annotations/annotation_guideline_v0.md`
- `experiments/exp-002-diag-action-pilot/prompts/structured_output_schemas.md`
- `experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py`

Immediate next action is Phase 0:

1. sync `exp-002` to `ntu-gpu43`
2. verify dataset feasibility for AVQA / MUSIC-AVQA
3. verify at least 2 audio-video-capable models
4. run a 5-clip structured-output smoke before any large annotation
