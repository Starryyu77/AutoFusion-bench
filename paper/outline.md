# Paper Outline

Working title:

> When to Read, Listen, or Watch? Benchmarking Modality Triage and Cross-Modal
> Recovery under Budget-Constrained Multimodal Inference

## Target Contribution

1. A benchmark layer built on public raw multimodal data.
2. Controlled text/audio/video perceptual corruptions with reproducible
   metadata.
3. Human-verified recoverability, evidence, abstention, and oracle-routing
   labels.
4. A layered evaluation suite for diagnosis, localization, recovery, routing,
   final task performance, and abstention.
5. A baseline study covering MLLMs and traditional robust multimodal methods.

## Suggested Structure

1. Introduction: why final-task robustness is not enough.
2. Related Work: missing modality, robust multimodal learning, MLLM evaluation,
   dynamic modality selection.
3. Benchmark Design: source datasets, corruption taxonomy, annotation schema,
   and datasheet.
4. Tasks and Metrics: T1-T5 and cost-normalized routing.
5. Baselines: unimodal, full multimodal, routing, oracle, MLLM prompting, and
   robust-fusion methods.
6. Results: aggregate and sliced analysis.
7. Error Analysis: diagnosis failures, recovery failures, budget failures, and
   abstention failures.
8. Limitations and Ethics: source dataset limits, generated corruptions,
   annotator reliability, and API/model constraints.

