---
formalism_version: v2
last_updated: 2026-05-17
---

# Claims

Claims are divided into positioning claims, evidence-backed internal claims, and
future paper claims. Do not upgrade a claim's strength without linked evidence.

## C001: Benchmark Positioning

- **Statement**: The project should be positioned as a diagnostic benchmark for
  modality triage, cross-modal recovery, and budget-aware routing, not as a
  simple missing-modality robustness method.
- **Strength**: accepted direction.
- **Evidence**:
  - `handoffs/incoming/2026-05-17-diagnostic-benchmark-expert-reply.md`
  - `handoffs/outgoing/2026-05-17-multimodal-diagnostic-benchmark-meeting-literature.md`
- **Boundary**: This is a research-positioning claim, not yet an empirical
  benchmark result.

## C002: Prior Work Boundary

- **Statement**: Missing-modality robustness and missing-modality benchmarks are
  already close prior work, so novelty cannot be claimed as merely studying
  missing modalities.
- **Strength**: literature-backed positioning.
- **Evidence**:
  - MissMAC-Bench and MissBench are close benchmark references.
  - SMIL and related missing-modality methods are close method references.
  - Incoming handoff explicitly warns against novelty phrasing as generic
    missing-modality robustness.
- **Boundary**: This needs a full related-work table before becoming final paper
  prose.

## C003: MELD Boundary

- **Statement**: Existing `exp-001` MELD feature-level runs validate pieces of
  the protocol but should not be used as the main positive benchmark-signal
  result.
- **Strength**: evidence-backed internal claim.
- **Evidence**:
  - `memory/tasks/exp-001.md`
  - `experiments/exp-001-decision-surface-pilot/results.md`
- **Boundary**: MELD may remain a diagnostic or pilot substrate, but current
  results warn that it is text-dominant under the existing setup.

## C004: Main Testable Paper Claim

- **Statement**: Current MLLMs and multimodal models will show systematic
  failures on at least one of diagnosis, localization, recoverability,
  budget-aware routing, or abstention under controlled perceptual defects.
- **Strength**: hypothesis.
- **Evidence**: pending pilot and baseline runs.
- **Boundary**: This must not be asserted as a result until the pilot benchmark
  and baseline suite are run.
