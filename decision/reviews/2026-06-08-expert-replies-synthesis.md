---
type: expert-reply-synthesis
target: decision/handoffs/outgoing/2026-06-08-diagnostic-benchmark-expert-review.md
created: 2026-06-08
sources:
  - /Users/starryyu/.codex/attachments/643d8091-1437-4a03-83db-370039f1c115/pasted-text.txt
  - /Users/starryyu/.codex/attachments/c7356dc2-ca04-4c59-8407-1cedb3f27b86/pasted-text.txt
---

# Expert Replies Synthesis: Diagnostic Benchmark

## Executive read

Both expert replies converge on the same answer:

> The direction is worth continuing, but the current proposal must be
> repositioned. It should not claim novelty as generic modality diagnosis,
> missing-modality robustness, cross-modal recovery, or budget-aware routing.
> The publishable core is narrower: unreliable multimodal evidence governance,
> especially the gap between diagnosing unreliable evidence and acting correctly
> on that diagnosis.

The current project is **promising but risky**. It becomes weak if framed as
five known subproblems packaged together. It becomes much stronger if framed as
a benchmark for whether MLLMs can turn evidence-quality judgments into correct
downstream decisions: route selection, recovery judgment, and abstention.

## Strong consensus

### 1. Keep the project, but change the center of gravity

The experts do not recommend abandoning the project. They recommend narrowing
the story.

Old framing:

> Modality triage + cross-modal recovery + budget-aware routing as five parallel
> benchmark layers.

Better framing:

> Evidence governance under unreliable text/audio/video inputs: can a model
> diagnose unreliable evidence, decide whether information is recoverable, take
> the right low-cost action, and abstain when evidence is insufficient?

This makes the benchmark about the chain from **diagnosis to action**, not just
about listing diagnostic tasks.

### 2. The true novelty is not any single task

The experts agree that individual pieces are already crowded:

- sample-level modality diagnosis and cross-modal enhancement: SMCIR
- missing-modality benchmarks: MissMAC-Bench, MissBench
- low-quality / missing-noisy unified multimodal frameworks: UMQ
- cross-modal inconsistency benchmarks: MMIR, CrossCheck-Bench
- dynamic modality selection / budgeted inference: MOSEL, Efficient Modality
  Selection, AdaLLaVA, MMR-Bench
- video/audio-video MLLM evaluation: Video-MME, AVHBench
- abstention / over-rejection adjacent concerns: CSR-Bench

Therefore, we should stop treating T1, T2, T3, T4, or T5 as independently new.
The novelty must come from the **coupling**:

> A model may know a modality is damaged but still use it, spend budget on it,
> fail to recover from another modality, or answer when it should abstain.

This is the proposed "diagnosis-to-action gap" or "detection-to-action gap."

### 3. The main sellable result needs to be a sharp failure mode

Both replies imply that a benchmark paper will only be convincing if it has a
clear headline result, for example:

- final-answer accuracy is high, but evidence-governance accuracy is low;
- models correctly diagnose damaged evidence but route to the wrong modality;
- models know a modality is unreliable but still answer instead of abstaining;
- a simple "stated diagnosis + fixed rule" pipeline beats the model's own
  end-to-end decision;
- text is over-trusted even when text is the corrupted or conflicting modality;
- audio is ignored even when audio is the necessary evidence.

The strongest proposed money figure is:

> Compare model diagnosis quality with model action quality. If diagnosis is
> correct but routing/abstention is wrong, the benchmark exposes a gap that
> final-task accuracy does not measure.

## Revised contribution claim

Recommended claim:

> We introduce a diagnostic benchmark for unreliable text-audio-video evidence.
> Unlike standard missing-modality or final-answer benchmarks, it evaluates
> whether MLLMs can govern degraded multimodal evidence: diagnose which evidence
> is unreliable, localize the defect, judge cross-modal recoverability, select a
> sufficient low-cost evidence route, and abstain when evidence is unrecoverable.
> Experiments reveal a diagnosis-to-action gap: models may identify unreliable
> evidence but fail to act on that diagnosis.

Avoid saying:

- first benchmark for missing/noisy modalities;
- first modality diagnosis benchmark;
- first cross-modal conflict benchmark;
- first budget-aware multimodal routing benchmark;
- first work on cross-modal recovery;
- modality triage is unexplored.

Safer wording:

> To our knowledge, existing benchmarks do not jointly evaluate evidence health
> diagnosis, defect localization, cross-modal recoverability, cost-aware
> evidence-route selection, and abstention over corrupted text-audio-video
> inputs.

Even this should be written as a protocol contribution, not a sweeping "first."

## Task-design changes

### Collapse five equal tasks into two tracks

Both experts warn that T1-T5 as equal parallel tasks looks like a kitchen-sink
benchmark. The revised structure should be:

#### Track A: Evidence Triage

Core diagnostic layer:

- modality health diagnosis;
- defect localization;
- recoverability judgment;
- recovery source and evidence pointer.

This is where the benchmark should spend most annotation quality.

#### Track B: Decision Under Evidence Constraint

Downstream action layer:

- selected modality route under budget;
- final answer;
- abstention decision;
- risk under budget.

Routing should not be the main novelty by itself. It should be a way to test
whether diagnosis leads to correct action.

### Reduce T2 and T3 overclaiming

T2 localization is useful, but should not be the main novelty because grounding
and localization are mature areas.

T3 should not be framed as generating or reconstructing a missing modality. That
puts us directly into SMCIR's method territory. It should instead be framed as a
human-verified property:

> Is the missing or damaged information recoverable from another available
> modality, and where is the evidence?

Recoverability is valuable because it determines whether the correct action is
route switching or abstention.

## Dataset strategy

### Do not use MELD/MOSEI as the main positive substrate

Both experts strongly warn against a MELD/MOSEI-first paper. Reasons:

- the affective datasets are often text-dominant;
- missing-modality affective computing is already crowded;
- our own exp-001 MELD evidence suggests text dominance;
- a MELD/MOSEI-only benchmark will look like another robust multimodal
  sentiment benchmark.

Recommended role:

- MELD: appendix, diagnostic stress test, or control split;
- selected MOSEI / IEMOCAP: secondary affective substrate if filtered for
  genuine audio/video contribution.

### Make AVQA / MUSIC-AVQA-style data the main substrate

Both replies recommend a non-text-dominant audio-video QA or audio-video
reasoning dataset as the primary substrate. Candidate families:

- AVQA;
- MUSIC-AVQA;
- Pano-AVQA or similar audio/video understanding datasets.

The benchmark should include at least one dataset where answers genuinely
depend on audio and video, not just transcript text.

### Add modality necessity filtering

Before constructing corruptions, filter examples by unimodal and multimodal
necessity:

- remove or mark text-only-solvable examples as a control split;
- keep examples where audio-only, video-only, or audio+video evidence is
  necessary;
- prioritize cases with genuine complementarity or conflict;
- keep high-value cases where route choice changes the answer/cost tradeoff.

This filtering directly addresses the text-dominance risk.

## Annotation priorities

The experts agree that annotation cost is only worth it if we annotate the hard
labels:

- evidence location;
- recoverability;
- recovery source;
- oracle route under budget;
- abstention label.

If we only annotate corrupted modality, severity, and final answer, the
benchmark is too close to existing work.

Recommended recoverability definitions:

| Label | Operational meaning |
|---|---|
| recoverable | Another clean modality clearly contains the lost target information, and annotators can point to evidence. |
| partially_recoverable | Another modality provides weak or indirect evidence, but not enough for high-confidence answer. |
| unrecoverable | After corruption, no available modality supports the answer; correct behavior is abstention. |

Suggested localization cost control:

- text: span labels required;
- audio: timestamp interval required;
- video: timestamp / frame interval required;
- video bounding box / region: high-quality subset only, around 10-20%.

Annotation quality must include:

- double annotation on test set;
- adjudication procedure;
- inter-annotator agreement for recoverability and route labels;
- tolerance rules for span/time agreement;
- public annotation guideline.

## Corruption-artifact defense

Both experts flag synthetic corruption artifacts as a major rejection risk. The
benchmark must prove models are not merely detecting generator signatures.

Required defenses:

- use multiple corruption families rather than one template;
- include natural corruption split: real ASR errors, real low-quality audio,
  real occlusion/blur/freeze or difficult video;
- use generator-family holdout for test;
- include clean-but-hard controls;
- include corrupted-but-irrelevant controls;
- include trivial detector baselines using low-level quality signals;
- separate generator metadata from human gold labels.

If a trivial low-level detector solves diagnosis, then the benchmark is testing
artifact detection rather than multimodal evidence reasoning.

## Baseline requirements

### Must-have baseline groups

1. Basic modality baselines:
   - text-only;
   - audio-only;
   - video-only;
   - full clean multimodal;
   - full corrupted multimodal.

2. Oracle and naive decision baselines:
   - random legal route;
   - static best route;
   - oracle route;
   - oracle abstention;
   - corrupted-metadata oracle upper bound.

3. Quality-aware baselines:
   - ASR confidence / WER proxy;
   - audio SNR / silence / clipping detector;
   - video blur / brightness / freeze / motion detector;
   - quality-only route;
   - quality + budget route;
   - learned small gating model.

4. MLLM prompting baselines:
   - direct answer;
   - explicit diagnosis prompt;
   - two-stage diagnose -> route -> answer;
   - diagnosis with evidence citation;
   - self-consistency / majority vote;
   - abstention-calibrated prompt;
   - oracle route prompt;
   - oracle defect-location prompt.

5. Critical new baseline:
   - stated-diagnosis-then-rule.

The stated-diagnosis-then-rule baseline is central: ask the model to state the
diagnosis, then apply a fixed rule to choose route or abstention. If this beats
the model's own end-to-end decision, it isolates the diagnosis-to-action gap.

## Pilot design

The 30-50 instance pilot is not a paper result. It is a go/no-go test.

Recommended pilot:

- 30-50 original clips or QA items;
- 3-4 corruption episodes per source item;
- 100-200 scored corrupted instances;
- cover text, audio, video, and cross-modal conflict;
- include at least one AVQA-style dataset;
- include one affective/control dataset only if filtered;
- evaluate 2 closed-source MLLMs and 2 open-source MLLMs if possible;
- include 3 simple baselines;
- hand-label recoverability, evidence location, oracle route, and abstention;
- produce 10-15 qualitative failure cases.

Pilot go/no-go criteria:

| Observation | Decision |
|---|---|
| Clear, interpretable failures in diagnosis/recovery/routing/abstention | Continue and scale. |
| Failures come mainly from obvious synthetic artifacts | Redesign corruptions. |
| Most examples are solvable by text-only | Change data or apply stronger modality necessity filtering. |
| Annotators disagree heavily on recoverability | Rewrite labels and guideline. |
| Oracle route and full multimodal are nearly identical | Downweight routing; focus on recoverability/abstention. |
| Frontier models are near oracle on all tracks | Sharpen task or pivot. |

## Minimum AAAI-style work package

The experts differ slightly in scale estimates, but agree that 30-50 examples
are only a pilot. A credible conference submission needs a substantially larger
package.

Minimum credible version:

- 2 source dataset families, preferably one AVQA/audio-video QA and one
  affective or event/video-understanding dataset;
- 800-1,200 corrupted episodes at the absolute low end;
- 1,500-4,000 human-verified instances for a more credible benchmark;
- 20-30% unrecoverable / abstention cases;
- 20-30% cross-modal conflict or misalignment cases;
- balanced corruption families and severity levels;
- held-out corruption families;
- 5-8 or more MLLMs, including closed-source and open-source models;
- at least 5-8 non-MLLM or task-specific baselines;
- structured prompting variants and oracle prompts;
- annotation quality report with IAA;
- public corruption scripts, metadata schema, annotation guideline, and
  datasheet;
- a clear headline failure finding.

More ambitious AAAI version:

- 2-3 dataset families;
- 3,000-6,000 corrupted episodes;
- 10k+ layer-level labels;
- 6-10 MLLMs;
- 8-12 baseline / prompting variants;
- qualitative failure taxonomy.

## Updated project decision

Recommended next decision:

> Reposition AutoFusion-Bench as EvidenceTriage / Evidence Governance benchmark.
> The core claim should be the diagnosis-to-action gap under unreliable
> text/audio/video evidence. Routing remains part of the action layer, not the
> independent novelty.

Possible naming:

- EvidenceTriage-Bench;
- TriageMM;
- AutoFusion-Bench: Diagnosing Evidence Triage in Multimodal LLMs.

The name "AutoFusion" may imply a fusion method. If the paper is a benchmark,
EvidenceTriage-Bench or TriageMM may communicate the contribution more clearly.

## Immediate action plan

1. Rewrite the proposal's problem statement around unreliable evidence
   governance and diagnosis-to-action gap.
2. Add an explicit related-work boundary table against SMCIR, MMIR,
   CrossCheck-Bench, MMR-Bench, MissMAC-Bench, MissBench, UMQ, MOSEL,
   Efficient Modality Selection, Video-MME, CSR-Bench, and AVHBench.
3. Redesign task structure into Track A: Evidence Triage and Track B: Decision
   Under Evidence Constraint.
4. Select AVQA or MUSIC-AVQA as the primary pilot substrate.
5. Add modality necessity filtering before corruption generation.
6. Write a pilot spec for 30-50 source items and 100-200 scored corrupted
   episodes.
7. Define recoverability and abstention labels before writing large-scale
   corruption scripts.
8. Include artifact-defense controls in the pilot, not as an afterthought.
9. Test the diagnosis-to-action gap using direct prompting, explicit diagnosis,
   two-stage prompting, oracle-route prompting, and stated-diagnosis-then-rule.
10. Decide go/no-go based on whether failures are nontrivial, interpretable,
    and not explainable by synthetic artifacts or text dominance.

## Bottom line

The proposal still has a viable path, but the old version is too broad and too
close to existing subfields. The revised project should not claim that modality
diagnosis, recovery, or routing is new. It should claim that current benchmarks
do not test whether MLLMs can **act correctly on unreliable multimodal evidence**.

The strongest final paper would show:

> MLLMs can sometimes identify unreliable evidence, yet fail to route, recover,
> or abstain correctly. This diagnosis-to-action gap is especially visible in
> raw audio/video temporal settings and is missed by final-answer benchmarks.
