---
last_updated: 2026-06-13
---

# Claims

Claims are divided into accepted positioning, active hypotheses, smoke evidence, and explicit non-claims. Do not upgrade a claim's strength without linked evidence.

## C001: Active Positioning

- **Statement**: AutoFusion-Bench should be positioned as an evaluation protocol for unreliable multimodal evidence governance and diagnosis-to-action gap in MLLMs.
- **Strength**: accepted current direction.
- **Evidence**:
  - `paper/2026-06-08-evidence-governance-story.md`
  - `decision/handoffs/outgoing/2026-06-13-autofusion-project-overview.md`
  - `governance/EXPERIMENT_CONSTITUTION.md`
- **Boundary**: This is a framing claim, not yet a final empirical paper result.

## C002: Prior Work Boundary

- **Statement**: Novelty should not be claimed as generic missing-modality robustness, modality diagnosis, conflict detection, or budgeted modality selection.
- **Strength**: literature-backed positioning.
- **Evidence**:
  - `paper/reference-pack` was archived locally, but the related-work boundary is summarized in `paper/2026-06-08-evidence-governance-story.md`.
  - `decision/reviews/2026-06-08-expert-replies-synthesis.md`
  - `decision/reviews/2026-06-08-pilot-expert-replies-synthesis.md`
- **Boundary**: The final paper still needs a polished related-work table and up-to-date citation verification.

## C003: Active Pilot Scope

- **Statement**: The first meaningful pilot should test audio-video evidence governance under textual queries, not full text-audio-video evidence governance.
- **Strength**: accepted pilot-scope correction.
- **Evidence**:
  - `decision/handoffs/outgoing/2026-06-08-diagnosis-to-action-pilot-v2.md`
  - `experiments/exp-002-diag-action-pilot/hypothesis.md`
  - `experiments/exp-002-diag-action-pilot/RUNBOOK.md`
- **Boundary**: A future text-evidence subset may extend the claim if subtitles, ASR transcripts, or captions are added as true evidence modalities.

## C004: Main Testable Hypothesis

- **Statement**: MLLMs may diagnose unreliable audio-video evidence but fail to act correctly on that diagnosis.
- **Strength**: active hypothesis.
- **Evidence**:
  - `experiments/exp-002-diag-action-pilot/hypothesis.md`
  - `experiments/exp-002-diag-action-pilot/RUNBOOK.md`
- **Boundary**: This must not be written as a paper finding until the 10-source mini-pilot and larger pilot produce sufficient evidence.

## C005: Smoke Protocol Evidence

- **Statement**: The exp-002 smoke chain can run end to end from media corruption through annotation, diagnosis, action, fixed-rule control, and scoring.
- **Strength**: evidence-backed engineering result.
- **Evidence**:
  - `experiments/exp-002-diag-action-pilot/results.md`
  - `experiments/exp-002-diag-action-pilot/results/smoke_v1_real_action_scoring_metrics.md`
  - `experiments/exp-002-diag-action-pilot/annotations/smoke_annotations_v1.gold.jsonl`
- **Boundary**: The 4-row smoke set is too small for a paper-level model behavior claim.

## C006: Metric Boundary

- **Statement**: Policy action correctness and final-answer correctness must be reported separately.
- **Strength**: accepted metric rule, supported by smoke observation.
- **Evidence**:
  - `experiments/exp-002-diag-action-pilot/results.md`
  - `governance/EXPERIMENT_CONSTITUTION.md`
- **Boundary**: Route-correct but answer-wrong cases indicate task execution failure, not necessarily diagnosis-to-action failure.

## C007: Data Boundary

- **Statement**: AVQA / AVQA-videos is the preferred first substrate; MUSIC-AVQA is backup; MELD / CMU-MOSI / CMU-MOSEI / IEMOCAP are not current main positive substrates.
- **Strength**: accepted execution boundary.
- **Evidence**:
  - `decision/handoffs/outgoing/2026-06-09-mini-pilot-junior-brief.md`
  - `experiments/exp-002-diag-action-pilot/RUNBOOK.md`
  - `governance/EXPERIMENT_CONSTITUTION.md`
- **Boundary**: Affective datasets may remain diagnostic/control references.

## C008: Gold Label Boundary

- **Statement**: Generated corruption metadata is not gold; human or adjudicated labels are required for source acceptance, answerability, recoverability, oracle route, abstention, and headline inclusion.
- **Strength**: accepted annotation rule.
- **Evidence**:
  - `skills/autofusion-annotation/references/data_spec.md`
  - `experiments/exp-002-diag-action-pilot/annotations/screening_scoring_guideline_v1.md`
  - `governance/EXPERIMENT_CONSTITUTION.md`
- **Boundary**: Generator metadata can still be shown as annotator hints and used for mechanical provenance.

## C009: Repository Governance Claim

- **Statement**: Historical exp-001 / MELD and May 2026 material should be archived away from the active workspace, while exp-002 and governance docs remain active.
- **Strength**: active repository policy.
- **Evidence**:
  - `governance/2026-06-13-repo-audit.md`
  - `governance/ROADMAP.md`
  - `archive/2026-06-pre-exp002-reset/README.md`
- **Boundary**: Server cleanup remains blocked until `ntu-gpu43` SSH access is restored and audited.

## Explicit Non-Claims

Do not claim:

- first missing-modality benchmark;
- first modality diagnosis benchmark;
- first cross-modal conflict benchmark;
- a new multimodal fusion method;
- Qwen models generally have or lack a diagnosis-to-action gap based only on 4 smoke rows;
- full text-audio-video evidence governance before a real text-evidence subset is validated.
