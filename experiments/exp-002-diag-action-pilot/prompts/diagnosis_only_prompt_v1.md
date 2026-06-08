# Diagnosis-Only Prompt v1

You are evaluating unreliable audio-video evidence under a textual query.

Given one video with audio, a question, and multiple-choice answers, diagnose
whether the audio and video evidence are usable for answering the question.

Do not provide the final answer. Return only JSON with this schema:

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

Rules:

- Treat the question text as the task query, not as corruptible evidence.
- Quality status means signal usability, not task relevance.
- Task relevance means whether a modality matters for the current question.
- Do not mark a modality as irrelevant inside quality status.
- Use `corruption_effect=no_effect` when corruption exists but does not change
  answerability or route.
- Use `post_corruption_answerability=unanswerable` only when available evidence
  cannot support the gold answer.
- Use `cross_modal_recoverability=not_needed` when same-modality evidence is
  still sufficient or when corruption is irrelevant.
- If another modality contains enough evidence to support the gold answer, set
  `cross_modal_recoverability=recoverable` and cite the evidence.
- Keep notes short and do not include final answer text.
