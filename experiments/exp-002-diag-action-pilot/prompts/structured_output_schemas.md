# Structured Output Schemas

Status: draft

All model outputs should be parseable as JSON. Free-form rationales are allowed
only inside bounded string fields.

## Diagnosis-only output

```json
{
  "instance_id": "...",
  "model": "...",
  "modality_status": {
    "text": "not_applicable|clean|corrupted|missing|conflicting|irrelevant",
    "audio": "clean|corrupted|missing|conflicting|irrelevant",
    "video": "clean|corrupted|missing|conflicting|irrelevant"
  },
  "defect_location": {
    "audio_time": [0.0, 0.0],
    "video_time": [0.0, 0.0],
    "frame_range": null,
    "region_note": null
  },
  "corruption_relevance": "answer_relevant|answer_irrelevant|unclear",
  "recoverability": "recoverable|partially_recoverable|unrecoverable",
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
  "modality_status": {
    "text": "not_applicable",
    "audio": "clean|corrupted|missing|conflicting|irrelevant",
    "video": "clean|corrupted|missing|conflicting|irrelevant"
  },
  "recoverability": "recoverable|partially_recoverable|unrecoverable",
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
  "rule_trace": ["recoverability_recoverable", "selected_clean_recovery_source"]
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
