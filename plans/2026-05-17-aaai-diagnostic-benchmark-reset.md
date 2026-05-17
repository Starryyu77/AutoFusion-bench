# Plan: AAAI Diagnostic Benchmark Reset

Date: 2026-05-17

## Decision

Adopt route B:

> public raw multimodal datasets + controlled corruption + human-verified
> annotation + new benchmark protocol.

Do not make the first paper a generic model-improvement paper on existing
datasets.

## Week 1: Literature and Data Feasibility

- Build a related-work matrix for:
  - missing-modality methods,
  - robust multimodal sentiment/emotion,
  - multimodal LLM evaluation,
  - dynamic modality selection,
  - cross-modal inconsistency detection.
- Check raw-data availability and license constraints for:
  - `CMU-MOSEI` / `CMU-MOSI`,
  - `IEMOCAP`,
  - `MELD`,
  - `CH-SIMS` / `CH-SIMS v2` / `M3ED`,
  - one AVQA-style non-affective dataset.

Exit gate:

- choose one affective substrate and one non-affective substrate for pilot.

## Week 2: Taxonomy and Corruption Generator

- Freeze text/audio/video defect taxonomy.
- Implement reproducible corruptions:
  - text span deletion / truncation / contradiction / time shift,
  - audio noise / mute / clipping / overlap / time shift,
  - video occlusion / blur / frame drop / freeze / crop.
- Emit corruption metadata as mechanical gold labels.

Exit gate:

- 30 sample clips can be corrupted and inspected end to end.

## Weeks 3-4: Gold Annotation Pilot

- Select 200-300 raw clips.
- Generate 1,000-2,000 corrupted instances.
- Human-label:
  - recoverability,
  - recovery source,
  - evidence location,
  - oracle route,
  - final answer,
  - abstention label.
- Measure annotation time and disagreement.

Exit gate:

- annotation schema is stable enough to scale.

## Weeks 5-6: Expansion and Baselines

- Expand toward 8k-15k instances if the pilot works.
- Run baseline suite:
  - unimodal,
  - full multimodal,
  - corrupted multimodal without diagnosis,
  - oracle routing,
  - learned or prompted routing,
  - MLLM structured prompting,
  - existing missing-modality methods where practical.

Exit gate:

- models show measurable failures beyond final-task accuracy.

## Week 7: Paper Tables and Error Analysis

- Report by defect type, severity, recoverability, modality state, and budget.
- Emphasize systematic failure modes:
  - wrong modality trusted,
  - defect not localized,
  - recoverable information missed,
  - expensive route chosen when cheaper route suffices,
  - failure to abstain.

Exit gate:

- decide AAAI paper viability.

