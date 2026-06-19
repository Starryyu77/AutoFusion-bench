# Literature Positioning

The project must acknowledge close prior work and position itself narrowly.

## Related-Work Buckets

1. Missing-modality robustness methods.
2. Missing-modality and low-quality multimodal benchmarks.
3. Robust multimodal sentiment and emotion recognition.
4. Multimodal LLM evaluation.
5. Cross-modal inconsistency and conflict detection.
6. Budgeted or dynamic modality selection.
7. Dataset documentation and benchmark reproducibility.

## Positioning Rule

Do not write:

> We study missing modalities in multimodal learning.

Write:

> We benchmark whether MLLMs can perform modality triage, evidence-grounded
> cross-modal recovery, and budget-aware routing under controlled perceptual
> degradation.

The core distinction is that prior work often measures final-task robustness,
whereas this benchmark explicitly evaluates diagnosis, localization,
recoverability, evidence, routing, and abstention.

