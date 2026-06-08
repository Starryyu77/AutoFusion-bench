# Structured Output Schemas

Status: draft, aligned with `annotations/screening_scoring_guideline_v1.md`

All model outputs should be parseable as JSON. Free-form rationales are allowed
only inside bounded string fields.

## Diagnosis-only output

```json
{
  "instance_id": "...",
  "model": "...",
  "modality_quality_status": {
    "text": "not_applicable",
    "audio": "clean|corrupted_usable|corrupted_unusable|missing|not_applicable",
    "video": "clean|corrupted_usable|corrupted_unusable|missing|not_applicable"
  },
  "modality_task_relevance": {
    "text": "not_applicable",
    "audio": "necessary|sufficient|supportive|irrelevant|unclear",
    "video": "necessary|sufficient|supportive|irrelevant|unclear"
  },
  "cross_modal_relation": "consistent|conflicting|misaligned|not_applicable|unclear",
  "defect_location": {
    "audio_time": [0.0, 0.0],
    "video_time": [0.0, 0.0],
    "frame_range": null,
    "region_note": null
  },
  "corruption_relevance": "answer_relevant|answer_irrelevant|unclear",
  "corruption_effect": "no_effect|route_change_only|confidence_drop|makes_unanswerable|creates_conflict|unclear",
  "post_corruption_answerability": "answerable|partially_answerable|unanswerable|unclear",
  "cross_modal_recoverability": "recoverable|partially_recoverable|unrecoverable|not_needed|unclear",
  "recovery_source": ["audio", "video"],
  "recovery_evidence": {
    "audio_time": [0.0, 0.0],
    "video_time": [0.0, 0.0],
    "note": "short evidence note"
  },
  "confidence": "high|medium|low"
}
```

Do not include final answer in diagnosis-only output.

## Action output from frozen diagnosis

```json
{
  "instance_id": "...",
  "model": "...",
  "diagnosis_source_id": "...",
  "selected_route": ["audio", "video"],
  "abstain": false,
  "answer": "...",
  "confidence": "high|medium|low",
  "risk_policy": "normal|cautious",
  "action_rationale": "short rationale"
}
```

`diagnosis_source_id` must reference the exact frozen diagnosis consumed by the
action prompt.

## Direct structured decision

```json
{
  "instance_id": "...",
  "model": "...",
  "modality_quality_status": {
    "text": "not_applicable",
    "audio": "clean|corrupted_usable|corrupted_unusable|missing|not_applicable",
    "video": "clean|corrupted_usable|corrupted_unusable|missing|not_applicable"
  },
  "modality_task_relevance": {
    "text": "not_applicable",
    "audio": "necessary|sufficient|supportive|irrelevant|unclear",
    "video": "necessary|sufficient|supportive|irrelevant|unclear"
  },
  "cross_modal_relation": "consistent|conflicting|misaligned|not_applicable|unclear",
  "post_corruption_answerability": "answerable|partially_answerable|unanswerable|unclear",
  "cross_modal_recoverability": "recoverable|partially_recoverable|unrecoverable|not_needed|unclear",
  "selected_route": ["audio", "video"],
  "abstain": false,
  "answer": "...",
  "confidence": "high|medium|low"
}
```

## Fixed rule output

```json
{
  "instance_id": "...",
  "diagnosis_source_id": "...",
  "selected_route": ["audio"],
  "abstain": false,
  "rule_id": "v0",
  "rule_trace": ["answerable", "selected_acceptable_recovery_source"]
}
```

## Parse failure policy

Record every parse failure with:

- model;
- instance id;
- prompt setting;
- raw output path;
- retry count;
- final parse status.
