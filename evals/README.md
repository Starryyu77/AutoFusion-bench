# Evaluation Plan

AutoFusion-Bench evaluates intermediate multimodal reasoning decisions, not only
final-task performance.

## Task Layers

1. Modality health diagnosis.
2. Defect localization.
3. Cross-modal recovery.
4. Budget-aware routing.
5. Final task answer or abstention.

## Baseline Families

- `text_only`
- `audio_only`
- `video_only`
- `full_multimodal`
- `corrupted_multimodal_no_diagnosis`
- `static_best_route`
- `random_legal_route`
- `budget_only_route`
- `quality_only_route`
- `joint_quality_budget_route`
- `oracle_route`
- MLLM structured prompting baselines
- task-specific robust-fusion or missing-modality baselines

## Reporting Slices

Main tables should be sliced by:

- source dataset,
- defect modality,
- defect type,
- defect severity,
- recoverability,
- budget level,
- single/double/all-corrupted modality state.

Do not report only one aggregate accuracy table.

