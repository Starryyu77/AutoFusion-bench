# Annotation Task Protocol v1

Status: ready for 5-clip smoke annotation

This protocol is the annotator-facing version of
`screening_scoring_guideline_v1.md`. Use it when assigning manual annotation
work. The longer guideline explains the research rationale; this document tells
annotators exactly what to do.

## 1. Annotation Goal

For each corrupted audio-video QA instance, decide only the fields that require
human judgment:

1. whether the current question still has enough evidence after corruption;
2. whether missing information can be recovered from another modality;
3. which route a reliable system should use, or whether it should abstain;
4. whether the sample is clear enough for headline scoring.

Do not spend annotation time re-entering mechanical facts that are already known
from the corruption generator, such as "audio was muted" or "video blur was
applied." Those fields should be auto-prefilled. Human annotators only override
them when the generated metadata is wrong or when the mechanical corruption has
a different task-conditioned effect than expected.

The annotation target is not model preference. The target is an evidence-backed
gold label for scoring model behavior.

## 2. Files

For the 5-clip smoke task:

- annotator input CSV:
  `annotations/smoke_annotation_sheet_v1.draft.csv`
- machine-readable draft JSONL:
  `annotations/smoke_annotation_sheet_v1.draft.jsonl`
- expected adjudicated output:
  `annotations/smoke_annotations_v1.gold.jsonl`

Annotators may edit the CSV. The adjudicated CSV should then be converted to
JSONL before scorer use.

## 3. Required Annotation Order

Follow this order for every row. Do not skip the blind pass.

### Step 1: Question-only blind pass

Look only at the question, choices, and gold answer. Do not view or listen to
the media.

Fill:

- `question_only_answerable_without_media`: `yes|no|unclear`
- `question_only_blind_confidence`: `high|medium|low`
- `question_only_blind_answer`: free text

Rules:

- If the answer is obvious from question and choices alone with high
  confidence, set `review_status=reject` or send to adjudication.
- If unsure, use `unclear` and continue to media inspection.

### Step 2: Clean source evidence check

Inspect the original clean media if available.

Fill:

- `source_audio_relevance`
- `source_video_relevance`
- `source_audio_video_joint_required`
- `source_evidence_note`

Allowed relevance values:

- `necessary`: required to support the gold answer.
- `sufficient`: enough alone to support the gold answer.
- `supportive`: useful but not enough alone.
- `irrelevant`: not useful for the current question.
- `unclear`: cannot decide reliably.

For the 5-clip smoke task, these fields can be treated as prefilled hints. Only
edit them when the hint is visibly wrong or when source evidence is ambiguous.
Reject or adjudicate the source if the clean gold answer is unsupported,
ambiguous, or primarily prior-only.

### Step 3: Corrupted media quality

Inspect the corrupted media.

Fill:

- `modality_quality_audio`
- `modality_quality_video`

Allowed quality values:

- `clean`: no meaningful degradation.
- `corrupted_usable`: degraded but still usable for at least some evidence.
- `corrupted_unusable`: present but effectively unusable for evidence.
- `missing`: absent or equivalent to absent, such as full silence.
- `not_applicable`: not a presented evidence modality.

This is mostly an auto/prefilled field because the generator knows whether it
muted audio, blurred video, shifted audio, or replaced audio. Human annotators
should only correct it if the actual media does not match the generator record.
Do not write `irrelevant` as a quality value. Relevance is a separate field.

### Step 4: Task relevance after corruption

Fill:

- `modality_task_relevance_audio`
- `modality_task_relevance_video`
- `cross_modal_relation`

Allowed task relevance values:

- `necessary`
- `sufficient`
- `supportive`
- `irrelevant`
- `unclear`

Allowed cross-modal relation values:

- `consistent`: modalities do not conflict.
- `conflicting`: modalities imply incompatible answers.
- `misaligned`: temporal mismatch or synchronization problem.
- `not_applicable`: only one evidence modality matters.
- `unclear`: cannot decide.

This is a human judgment field because relevance depends on the question. A
modality can be `corrupted_usable` and `irrelevant` at the same time.

### Step 5: Corruption effect

Fill:

- `corruption_relevance`
- `corruption_effect`

Allowed `corruption_relevance`:

- `answer_relevant`
- `answer_irrelevant`
- `unclear`

Allowed `corruption_effect`:

- `no_effect`: corruption does not affect answer or route.
- `route_change_only`: answer remains supported, but route should change.
- `confidence_drop`: answer may remain possible, but evidence confidence drops.
- `makes_unanswerable`: corruption removes required support.
- `creates_conflict`: corruption creates incompatible evidence.
- `unclear`: cannot decide.

Generator metadata tells us what was changed, but not whether the change matters
for this question. The human decision here is usually only: no effect, confidence
drop, route change, unanswerable, or conflict.

### Step 6: Answerability and recovery

Fill:

- `post_corruption_answerability`
- `cross_modal_recoverability`
- `main_answerability`
- `risk_sensitive`

Allowed `post_corruption_answerability`:

- `answerable`
- `partially_answerable`
- `unanswerable`
- `unclear`

Allowed `cross_modal_recoverability`:

- `recoverable`
- `partially_recoverable`
- `unrecoverable`
- `not_needed`
- `unclear`

Hard rule:

> If you cannot point to evidence, do not label the instance `recoverable`.

Set `main_answerability`:

- `answerable`: clear evidence supports the gold answer.
- `unanswerable`: evidence is insufficient and the system should abstain.
- `exclude_from_main`: partial, unclear, ambiguous, or highly policy-dependent.

Set `risk_sensitive=true` when the case is borderline, ambiguous, or useful only
for qualitative analysis.

### Step 7: Recovery evidence

Fill:

- `recovery_source_json`
- `recovery_audio_time_json`
- `recovery_video_time_json`
- `recovery_note`

Use JSON syntax in route/time fields, for example:

```json
["audio"]
```

```json
[1.2, 4.8]
```

If evidence is global across the clip, use the full clip span and explain in
`recovery_note`.

### Step 8: Oracle policy action

Fill:

- `acceptable_routes_json`
- `preferred_route_json`
- `disallowed_routes_json`
- `oracle_abstain`
- `oracle_answerability`
- `oracle_expected_answer`
- `oracle_risk_level`

Route fields must be JSON:

```json
[["audio"], ["audio", "video"]]
```

Rules:

- If `main_answerability=unanswerable`, set `oracle_abstain=true`,
  `acceptable_routes_json=[]`, and `oracle_expected_answer=` empty.
- If `main_answerability=answerable`, set at least one acceptable route.
- `preferred_route_json` should be the clearest or lowest-cost sufficient route.
- `disallowed_routes_json` should include routes that rely on unusable or
  misleading evidence.
- `oracle_answerability` should be `answerable`, `unanswerable`, or `partial`.

### Step 9: Confidence and notes

Fill:

- `annotation_confidence`: `high|medium|low`
- `annotator_notes`: short free text

In the website, use:

- `review_status=reviewed` when the row has been inspected;
- `review_status=needs_adjudication` when confidence is low or when two
  reasonable labels would lead to different scorer outcomes;
- `review_status=rejected` when the row should not be used.

Saving a row as `reviewed` does not by itself put it into headline scoring. On
export, the app derives the scorer-facing `instance_decision` conservatively:

- `accept`: reviewed, `main_answerability=answerable|unanswerable`,
  `annotation_confidence=high|medium`, and `risk_sensitive=false`;
- `reject`: rejected rows, or reviewed rows with
  `main_answerability=exclude_from_main`;
- `adjudicate`: low-confidence, risk-sensitive, incomplete, or explicitly
  adjudication-needed rows.

## 4. Adjudication Rules

Send a row to adjudication if any condition holds:

- question-only answer is plausible with medium or high confidence;
- clean source evidence is ambiguous;
- the corrupted instance is only partially answerable;
- cross-modal recovery depends on weak or indirect evidence;
- acceptable routes are not obvious;
- annotators disagree on `main_answerability`, `oracle_abstain`, or
  `acceptable_routes_json`.

Adjudicated rows should record a short reason in `annotator_notes`.

## 5. Headline Inclusion Rules

Only rows with these properties enter headline scoring:

- `instance_decision=accept`
- `main_answerability=answerable|unanswerable`
- `annotation_confidence=high|medium`
- `risk_sensitive=false`
- no unresolved `unclear` in headline fields

Rows with `main_answerability=exclude_from_main` remain useful for qualitative
analysis but should not drive the main paper claim.

## 6. Smoke Annotation Task

For the current 5-row smoke:

1. Make two copies of `smoke_annotation_sheet_v1.draft.csv`, one per annotator.
2. Each annotator fills all rows independently.
3. Compare disagreements on:
   - `main_answerability`
   - `cross_modal_recoverability`
   - `acceptable_routes_json`
   - `oracle_abstain`
4. Adjudicate into a single gold sheet.
5. Convert the adjudicated CSV into
   `annotations/smoke_annotations_v1.gold.jsonl`.
6. Validate the JSONL before running model scoring.

## 7. Minimum Pilot Quality Gate

Before scaling to 40 source / 160 corrupted instances, the smoke annotation
should show:

- annotators can fill the fields without changing the schema;
- no more than 1-2 of 5 rows require unresolved adjudication;
- the conversion to gold JSONL passes validation;
- scorer can run on the gold labels without manual patching.

If this fails, fix the annotation protocol before running more model calls.
