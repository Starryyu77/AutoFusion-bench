# Action From Frozen Diagnosis Prompt v1

You are making a final decision for an unreliable audio-video QA instance.

You receive:

- one corrupted video with audio;
- a textual question and multiple-choice options;
- a frozen diagnosis JSON produced earlier by the same model.

Use the frozen diagnosis as the evidence-governance state. Do not rewrite the
diagnosis. Your job is to decide which modality route to use, whether to
abstain, and what final answer to return.

Return only JSON with this schema:

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

Rules:

- `selected_route` must contain only `"audio"` and/or `"video"`.
- If the frozen diagnosis says the instance is `unanswerable` or
  `unrecoverable`, set `abstain=true`, `selected_route=[]`, and `answer=null`.
- If the frozen diagnosis says the corrupted evidence is answerable, select the
  smallest route that is sufficient according to the diagnosis and the media.
- If `recovery_source` is non-empty, prefer that route unless the media makes it
  clearly unusable.
- If `cross_modal_recoverability=not_needed`, use the clean or usable modality
  that is sufficient for the question.
- If you do not have enough evidence for one option, abstain instead of
  guessing.
- When `abstain=false`, `answer` must exactly match one of the provided choices.
- When `abstain=true`, `answer` must be null.
- Keep `action_rationale` under 30 words.
