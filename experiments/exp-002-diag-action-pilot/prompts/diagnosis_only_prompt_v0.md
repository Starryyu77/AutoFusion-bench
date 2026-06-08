# Diagnosis-Only Prompt v0

You are evaluating unreliable audio-video evidence under a textual query.

Given one video with audio, a question, and multiple-choice answers, diagnose
whether the audio and video evidence are usable for answering the question.

Do not provide the final answer. Return only JSON with this schema:

```json
{
  "instance_id": "...",
  "model": "...",
  "modality_status": {
    "text": "not_applicable",
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

Rules:

- Treat the question text as the task query, not as corruptible evidence.
- If audio or video is damaged but irrelevant to the question, mark it as
  `irrelevant` or set `corruption_relevance` to `answer_irrelevant`.
- If evidence is insufficient after corruption, set `recoverability` to
  `unrecoverable`.
- If another clean modality contains enough task-relevant evidence, set
  `recoverability` to `recoverable` and cite that modality in
  `recovery_source`.
- Keep notes short and do not include final answer text.
