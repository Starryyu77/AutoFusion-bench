# Annotation Guideline v0

Status: draft

## Scope

This guideline is for the `exp-002` diagnosis-to-action pilot. It labels
audio-video evidence under a textual query. The question text is treated as the
task query, not as corruptible evidence, unless a separate text-evidence subset
is explicitly added.

For the full source-screening, corrupted-instance labeling, model-output
scoring, and adjudication rubric, see
`annotations/screening_scoring_guideline_v0.md`.

## Labels

### Modality necessity

For each source item, label whether the original clean question can be answered
from audio, video, both, or neither.

```json
{
  "text_question_only": false,
  "audio_sufficient": true,
  "video_sufficient": false,
  "audio_video_joint_required": false,
  "human_confidence": "high"
}
```

Reject source items where the answer is likely available from question text,
dataset priors, or general common sense alone.

### Modality status

Allowed values:

- `clean`
- `corrupted`
- `missing`
- `conflicting`
- `irrelevant`
- `not_applicable`

For this pilot, `text` should usually be `not_applicable` because the question
is not an evidence modality.

### Defect location

Annotate the smallest practical location:

- audio time span;
- video time span;
- frame range if available;
- short region note if spatial region matters.

Use `null` when location does not apply.

### Corruption relevance

Allowed values:

- `answer_relevant`
- `answer_irrelevant`
- `unclear`

This label decides whether a model should change its route because of the
corruption.

### Recoverability

Recoverability is task-conditioned:

> Given the corrupted instance and the question, another available clean
> modality contains sufficient task-relevant evidence to support the gold answer,
> and the annotator can point to that evidence.

Allowed values:

- `recoverable`
- `partially_recoverable`
- `unrecoverable`

Rule:

> If the annotator cannot point to evidence, do not label the instance
> `recoverable`.

### Oracle policy action

The oracle policy action contains:

```json
{
  "selected_route": ["audio"],
  "abstain": false
}
```

Set `abstain=true` when available evidence is insufficient or conflict cannot be
resolved.

## Required annotation record

```json
{
  "instance_id": "...",
  "source_dataset": "AVQA_or_MUSIC_AVQA",
  "question": "...",
  "modalities_presented": ["audio", "video"],
  "gold_answer": "...",
  "modality_necessity": {
    "text_question_only": false,
    "audio_sufficient": false,
    "video_sufficient": true,
    "audio_video_joint_required": false,
    "human_confidence": "high"
  },
  "modality_status": {
    "text": "not_applicable",
    "audio": "corrupted",
    "video": "clean"
  },
  "defect_location": {
    "text_span": null,
    "audio_time": [1.2, 3.8],
    "video_time": null,
    "frame_range": null,
    "region_note": null
  },
  "corruption_relevance": "answer_relevant",
  "recoverability": "recoverable",
  "recovery_source": ["video"],
  "recovery_evidence": {
    "audio_time": null,
    "video_time": [1.0, 4.0],
    "note": "visual cue directly identifies the queried event"
  },
  "oracle_policy_action": {
    "selected_route": ["video"],
    "abstain": false
  },
  "oracle_route_rationale": "Audio is corrupted but video contains sufficient evidence.",
  "annotation_confidence": "high"
}
```

## Agreement plan

- Double-annotate at least 50 instances.
- Report agreement for recoverability and oracle policy action.
- Minimum acceptable recoverability agreement: kappa >= 0.4.
- Preferred agreement: kappa >= 0.6.
- Disagreements go into `adjudication_notes.md`.

## Common rejection cases

Reject the instance if:

- the gold answer is ambiguous;
- the relevant evidence cannot be located;
- the question can be answered without audio/video evidence;
- corruption creates an unrealistic artifact that trivially reveals the label;
- the annotator cannot decide whether another modality recovers the answer.
