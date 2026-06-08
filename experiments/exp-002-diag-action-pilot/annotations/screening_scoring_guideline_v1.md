# Manual Screening and Scoring Guideline v1

Status: ready-for-pilot-freeze-after-team-review

This v1 guideline revises v0 after expert review. The main change is conceptual
separation:

- quality status is separated from task relevance;
- post-corruption answerability is separated from cross-modal recoverability;
- policy action correctness is separated from final-answer correctness.

## 1. Purpose

This guideline defines the manual screening, annotation, and scoring standard
for `exp-002`, a pilot on audio-video evidence governance under textual
queries.

The original AVQA / MUSIC-AVQA-style datasets provide audio/video, question,
choices, and gold answer. They do not provide the benchmark gold layer needed
for our task:

- whether the clean source truly needs audio/video evidence;
- whether a generated corruption affects the current question;
- whether the corrupted instance remains answerable;
- whether the answer can be recovered from another modality;
- which evidence route is acceptable or preferred;
- when the model should abstain;
- whether the model diagnosed correctly but acted incorrectly.

## 2. Units

| Unit | Object | Purpose |
|---|---|---|
| Source screening | clean source video/audio and original question | decide whether the source belongs in the pilot |
| Corrupted-instance labeling | one source plus one corruption episode | label answerability, recoverability, oracle policy, and ambiguity |
| Model-output scoring | one model output | score diagnosis, policy action, answer execution, and consistency |

## 3. Stage A: Source Screening

### A1. Annotator inputs

For each source item, annotators inspect:

- clean video;
- clean audio;
- question;
- choices;
- original gold answer;
- original coarse type, such as `Sound`, `View`, or `Both`, if available.

Dataset coarse types are hints only. They are not gold labels for this pilot.

### A2. Question-only blind pass

Before viewing media evidence, run a question-only blind check:

```json
{
  "answerable_without_media": "yes|no|unclear",
  "blind_confidence": "high|medium|low",
  "blind_answer": "..."
}
```

Rules:

- If `answerable_without_media=yes`, `blind_confidence=high`, and the blind
  answer matches gold, reject from the main split.
- If blind confidence is medium or the answer is plausible but uncertain, place
  in a control/adjudication pool.
- If blind confidence is low, the source can proceed to media inspection.

### A3. Accept criteria

Accept a source only if:

- the gold answer is supported by audio and/or video evidence;
- the answer is not primarily question-only, prior-only, or common-sense-only;
- original audio/video quality is sufficiently usable;
- gold answer is not obviously wrong;
- annotators can point to at least one evidence source.

### A4. Reject criteria

Reject a source if any condition holds:

- question + choices alone give a high-confidence answer;
- gold answer is questionable or multiple choices are reasonable;
- original audio/video is already severely damaged;
- relevant evidence cannot be located;
- the question depends too much on common sense or dataset bias;
- annotators cannot decide which modality provides the main evidence.

### A5. Source modality necessity

Use this source-level schema:

```json
{
  "source_decision": "accept|reject|adjudicate",
  "question_only_blind": {
    "answerable_without_media": "yes|no|unclear",
    "blind_confidence": "high|medium|low",
    "blind_answer": "..."
  },
  "source_modality_necessity": {
    "audio": "sufficient|necessary|supportive|irrelevant|unclear",
    "video": "sufficient|necessary|supportive|irrelevant|unclear",
    "audio_video_joint_required": "yes|no|unclear"
  },
  "primary_evidence_modality": ["audio"],
  "evidence_note": "short evidence note",
  "human_confidence": "high|medium|low"
}
```

Definitions:

- `sufficient`: the modality alone can support the gold answer.
- `necessary`: the modality is required for the answer under the clean source.
- `supportive`: the modality helps but is not enough alone.
- `irrelevant`: the modality does not help answer the current question.
- `unclear`: annotator cannot reliably decide.

## 4. Stage B: Corrupted-Instance Labeling

Each corrupted instance is one accepted source plus one controlled corruption
episode.

### B1. Annotator inputs

Annotators may see:

- corrupted media;
- question and choices;
- original gold answer;
- corruption generator metadata: affected modality, corruption type, severity,
  and mechanical location.

Generator metadata is not gold. It records what was mechanically changed. The
gold label is task-conditioned and evidence-based.

### B2. Quality status

Quality describes whether the signal is technically usable, not whether it is
useful for the current question.

```json
"modality_quality_status": {
  "audio": "clean|corrupted_usable|corrupted_unusable|missing|not_applicable",
  "video": "clean|corrupted_usable|corrupted_unusable|missing|not_applicable"
}
```

Definitions:

- `clean`: no meaningful degradation.
- `corrupted_usable`: degraded but still usable for at least some evidence.
- `corrupted_unusable`: present but effectively unusable for evidence.
- `missing`: absent or equivalent to absent, such as full silence.
- `not_applicable`: not a presented evidence modality.

Do not use `irrelevant` as quality status.

### B3. Task relevance

Task relevance describes whether a modality matters for the current question.

```json
"modality_task_relevance": {
  "audio": "necessary|sufficient|supportive|irrelevant|unclear",
  "video": "necessary|sufficient|supportive|irrelevant|unclear"
}
```

A modality can be both `corrupted_usable` and `irrelevant`. Quality and
relevance must be scored separately.

### B4. Cross-modal relation

```json
"cross_modal_relation": "consistent|conflicting|misaligned|not_applicable|unclear"
```

Definitions:

- `consistent`: audio and video do not conflict.
- `conflicting`: modalities imply incompatible answers.
- `misaligned`: temporal mismatch or synchronization problem.
- `not_applicable`: only one evidence modality is relevant.
- `unclear`: annotator cannot decide.

### B5. Corruption relevance and effect

Keep coarse relevance:

```json
"corruption_relevance": "answer_relevant|answer_irrelevant|unclear"
```

Add effect:

```json
"corruption_effect": "no_effect|route_change_only|confidence_drop|makes_unanswerable|creates_conflict|unclear"
```

Definitions:

- `no_effect`: corruption does not affect answer or route.
- `route_change_only`: answer remains supported, but route should change.
- `confidence_drop`: answer may remain possible, but evidence confidence drops.
- `makes_unanswerable`: corruption removes required support.
- `creates_conflict`: corruption produces cross-modal conflict.
- `unclear`: annotators cannot reliably decide.

### B6. Answerability and cross-modal recoverability

Separate post-corruption answerability from cross-modal recovery.

```json
"post_corruption_answerability": "answerable|partially_answerable|unanswerable|unclear",
"cross_modal_recoverability": "recoverable|partially_recoverable|unrecoverable|not_needed|unclear",
"main_answerability": "answerable|unanswerable|exclude_from_main",
"risk_sensitive": false
```

Definitions:

- `post_corruption_answerability=answerable`: the corrupted instance still has
  enough evidence to support the gold answer.
- `partially_answerable`: there is weak or indirect evidence, but not enough for
  high-confidence headline scoring.
- `unanswerable`: no available evidence supports the gold answer after
  corruption.
- `cross_modal_recoverability=recoverable`: another modality supplies enough
  evidence to support the gold answer.
- `not_needed`: no cross-modal recovery is needed because the same modality is
  still sufficient or the corruption is irrelevant.

Hard rule:

> If annotators cannot point to evidence, do not label the instance
> `recoverable`.

Partial cases should remain in annotation and qualitative analysis, but they do
not enter headline hard scoring. Use:

- `main_answerability=answerable` for clear answerable cases;
- `main_answerability=unanswerable` for clear abstention-required cases;
- `main_answerability=exclude_from_main` for partial, unclear, or highly
  policy-dependent cases.

### B7. Recovery source and evidence

```json
"recovery_source": ["audio", "video"],
"recovery_evidence": {
  "audio_time": null,
  "video_time": null,
  "note": "short evidence note"
}
```

Rules:

- `recovery_source` is empty when cross-modal recovery is not needed or not
  possible.
- Evidence can be diffuse, but annotators must describe the relevant segment or
  explain why the evidence is global.
- For diffuse evidence, use the full clip span and add `note`.

### B8. Oracle policy action

Use acceptable routes, not only exact route match:

```json
"oracle_policy_action": {
  "acceptable_routes": [["audio"], ["video"]],
  "preferred_route": ["audio"],
  "disallowed_routes": [],
  "abstain": false,
  "answerability": "answerable|unanswerable|partial",
  "expected_answer": "...",
  "risk_level": "normal|cautious"
}
```

Rules:

- `acceptable_routes`: routes that provide sufficient evidence.
- `preferred_route`: minimum or clearest route for this instance.
- `disallowed_routes`: routes that would rely on unusable or misleading
  evidence.
- If `main_answerability=unanswerable`, set `abstain=true` and
  `expected_answer=null`.
- If `main_answerability=exclude_from_main`, do not use abstention as a hard
  headline correctness target.
- Mildly corrupted but usable modalities can appear in acceptable routes if
  they still support the answer.

### B9. Corrupted-instance v1 record

```json
{
  "instance_id": "...",
  "source_id": "...",
  "instance_decision": "accept|reject|adjudicate",
  "modality_quality_status": {
    "audio": "missing",
    "video": "clean"
  },
  "modality_task_relevance": {
    "audio": "necessary",
    "video": "irrelevant"
  },
  "cross_modal_relation": "not_applicable",
  "corruption_relevance": "answer_relevant",
  "corruption_effect": "makes_unanswerable",
  "post_corruption_answerability": "unanswerable",
  "cross_modal_recoverability": "unrecoverable",
  "main_answerability": "unanswerable",
  "risk_sensitive": false,
  "recovery_source": [],
  "recovery_evidence": {
    "audio_time": null,
    "video_time": null,
    "note": "the question requires the sound source and the audio is muted"
  },
  "oracle_policy_action": {
    "acceptable_routes": [],
    "preferred_route": [],
    "disallowed_routes": [["audio"], ["audio", "video"]],
    "abstain": true,
    "answerability": "unanswerable",
    "expected_answer": null,
    "risk_level": "normal"
  },
  "annotation_confidence": "high"
}
```

## 5. Stage C: Model-Output Scoring

Scoring is separated into parse quality, diagnosis quality, policy action, task
execution, and diagnosis-to-action consistency.

### C1. Parse policy

Parse policy depends on prompt setting:

| Setting | Parse rule |
|---|---|
| direct answer | extract answer / abstain only |
| explicit diagnosis | strict JSON |
| two-stage diagnose-route-answer | strict JSON |
| diagnosis-only frozen | strict JSON |
| stated-diagnosis-then-rule | strict JSON diagnosis; rule consumes parsed fields |

Use a deterministic parser, such as first JSON block extraction. Do not manually
repair outputs case by case.

Always report parse failure rate.

### C2. Diagnosis-right levels

Define three denominators:

```text
health_diagnosis_right:
  modality_quality_status correct

triage_diagnosis_right:
  modality_quality_status + corruption_relevance/effect correct

full_diagnosis_right:
  modality_quality_status + corruption_relevance/effect
  + post_corruption_answerability/cross_modal_recoverability
  + recovery_source correct
```

Headline conditional policy failure uses `triage_diagnosis_right`.

### C3. Diagnosis metrics

| Metric | Meaning |
|---|---|
| `health_diagnosis_macro_F1` | quality/status diagnosis |
| `corruption_effect_macro_F1` | no effect / route change / unanswerable / conflict |
| `recoverability_macro_F1` | answerability and recovery judgment |
| `recovery_source_F1` | recovery source set |
| `evidence_pointer_hit` | evidence pointer within accepted tolerance |

For pilot, evidence pointer can be `hit / miss / not_scorable`. For larger
benchmark, add temporal IoU.

### C4. Policy action metrics

Do not mix final answer correctness into policy action correctness.

| Metric | Definition |
|---|---|
| `route_acceptable` | model route is in acceptable routes |
| `route_preferred` | model route equals preferred route |
| `route_disallowed` | model route uses a disallowed route |
| `abstain_hit` | abstain matches oracle abstain on headline cases |
| `policy_action_correct` | route acceptable + abstain correct |

### C5. Task execution and governed success

| Metric | Definition |
|---|---|
| `task_execution_correct` | answer is correct under oracle/preferred route |
| `governed_success` | policy action correct and final answer correct |
| `false_answer_on_unanswerable` | model answers when headline gold is unanswerable |
| `false_abstention_on_answerable` | model abstains when headline gold is answerable |

`governed_success` is useful but should not be the headline metric for pilot
because it conflates perception, policy, and QA ability.

### C6. Diagnosis-to-action consistency

Core cases:

| Case | Meaning |
|---|---|
| `diagnosis_wrong_policy_wrong` | diagnosis wrong, policy wrong |
| `diagnosis_wrong_policy_right` | diagnosis wrong but policy accidentally right |
| `diagnosis_right_policy_right` | diagnosis right and policy right |
| `diagnosis_right_policy_wrong` | diagnosis right but policy wrong |

Headline:

```text
conditional_policy_failure =
  count(diagnosis_right_policy_wrong under triage_diagnosis_right)
  / count(triage_diagnosis_right)
```

Auxiliary:

```text
P(policy_action incorrect | health_diagnosis_right)
P(policy_action incorrect | full_diagnosis_right)
```

### C7. Fixed-rule comparison

For every frozen diagnosis output:

1. feed the same parsed diagnosis to model action prompt;
2. feed the same parsed diagnosis to a fixed rule;
3. compare policy action correctness.

```text
RuleLift =
  Score(fixed_rule(model_diagnosis)) - Score(model_action(model_diagnosis))
```

This tests whether the model can convert diagnosis into policy.

## 6. Pilot Main Metrics

The pilot main table should use six core metrics:

| Metric | Purpose |
|---|---|
| `health_diagnosis_macro_F1` | model knows modality quality/status |
| `recoverability_macro_F1` | model knows answerability / recovery |
| `policy_action_accuracy` | route + abstain |
| `conditional_policy_failure` | headline diagnosis-to-action gap |
| `rule_lift` | fixed rule from frozen diagnosis |
| `false_answer_on_unanswerable` | reliability failure |

Appendix / secondary metrics:

- final answer accuracy;
- governed success;
- route regret;
- budget violation;
- evidence pointer hit;
- parse failure rate;
- false abstention on answerable;
- per-corruption-family breakdown.

## 7. Annotation Quality Control

For the 160-instance pilot:

- double annotate at least 80 instances;
- preferably double annotate all 160 instances;
- adjudicate all disagreements on headline fields;
- remove unresolved ambiguous instances from the main split.

Report:

| Item | Pilot expectation |
|---|---|
| recoverability / answerability agreement | kappa or AC1 >= 0.5 to continue; below 0.4 requires definition rewrite |
| abstention agreement | kappa or MCC >= 0.6 |
| route agreement | exact match + Jaccard + per-modality F1 |
| evidence pointer | tolerance-hit / temporal IoU, not kappa |
| adjudication rate | >30% indicates guideline is unclear |
| ambiguous split | do not use in headline metrics |

Also report raw agreement and macro-F1 between annotators. Do not rely only on
Cohen's kappa when category distribution is imbalanced.

## 8. Pilot Instance Quotas

Use forced quotas rather than relying on natural occurrence:

| Type | Target count | Purpose |
|---|---:|---|
| clean-hard | 15-20 | false alarms |
| corrupted-but-irrelevant | 20-25 | over-triage / unnecessary abstention |
| audio necessary + audio missing | 15-20 | unrecoverable abstention |
| audio necessary + video recoverable | 10-15 | cross-modal recovery |
| video necessary + video degraded usable | 10-15 | corrupted but usable |
| audio-video jointly required | about 20 | route completeness |
| temporal mismatch | about 20 | alignment reasoning |
| cross-modal conflict | about 20 | conflict detection and policy |
| prior-only trap | about 10 | question/choice bias |
| partial recoverability | 10-15 | risk-sensitive / qualitative only |

Especially include:

- corrupted but still usable;
- corrupted but irrelevant;
- clean but hard.

Otherwise models may learn a shallow policy: any corruption means route change
or abstention.

## 9. Statistical Reporting

For the 160-instance pilot:

- report raw counts and percentages;
- report bootstrap 95% confidence intervals;
- use paired bootstrap for same-instance setting comparisons;
- McNemar-style tests can be supporting evidence, not the central claim;
- include 3-5 qualitative cases for every key conclusion.

Pilot claims should focus on:

- nontrivial failure existence;
- interpretability;
- artifact control;
- annotation feasibility;
- whether scaling is justified.

## 10. Freeze Criteria for v1

Freeze this guideline for annotation-sheet and scorer implementation only after:

- the team agrees on the v1 split fields;
- annotation sheet contains v1 schema;
- scorer design uses `conditional_policy_failure`, not final answer mixed into
  action failure;
- partial cases are excluded from headline hard scoring;
- double-annotation target is set to at least 80/160, preferably 160/160.

## 11. AAAI-Style Scaling Note

The v1 standard can support a pilot and can become part of the eventual
benchmark contribution, but the 40-source / 160-instance pilot is not enough for
a full AAAI benchmark paper.

For a full benchmark paper, target:

- at least 1k-2k corrupted instances, preferably 3k+;
- at least two data families, including one with real text evidence;
- high-proportion double annotation and adjudication;
- recoverability / abstention agreement >= 0.6, preferably >= 0.7;
- at least 5-8 MLLMs or audio-video models;
- baselines: unimodal, full multimodal, oracle route, quality-only,
  static route, stated-diagnosis-rule;
- controls: clean-hard, corrupted-irrelevant, natural corruption, quality
  detector.
