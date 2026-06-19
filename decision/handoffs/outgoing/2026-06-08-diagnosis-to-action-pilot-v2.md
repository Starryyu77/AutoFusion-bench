# Handoff: Diagnosis-to-Action Pilot Design v2

> Generated 2026-06-08 after expert review of the first pilot draft.  
> This is a revised, self-contained pilot plan for discussion and expert audit.

## 1. Revised pilot claim

The pilot should not claim to validate full text-audio-video evidence
governance. With AVQA / MUSIC-AVQA as the primary substrate, the honest pilot
claim is:

> This pilot tests whether the diagnosis-to-action gap is observable in
> audio-video evidence governance under textual queries.

The scaled benchmark may later expand to full text-audio-video evidence
governance by adding transcript, subtitle, caption, or ASR-derived text evidence.

## 2. Core hypothesis

The pilot tests:

> MLLMs may diagnose unreliable audio-video evidence, but fail to act correctly
> on their own diagnosis.

This is the **diagnosis-to-action gap**.

The cleanest version is self-inconsistency:

> A model states that a modality is damaged, conflicting, or insufficient, but
> then selects an action inconsistent with that stated diagnosis.

Examples:

- The model says audio is unusable but still selects audio as necessary
  evidence.
- The model says evidence is insufficient but still answers confidently.
- The model says video is frozen or occluded but ignores available audio
  evidence.
- The model detects audio-video conflict but neither arbitrates nor abstains.

Gold oracle labels still matter, but the primary pilot signal should be
**model self-inconsistency**, because it is less vulnerable to disputes about
human oracle recoverability.

## 3. Pilot scale

- 40 source items as the default target.
- 4 corruption episodes per source item.
- About 160 scored instances.
- Every scored instance manually inspected.

Acceptable range:

- 30-50 source items;
- 100-200 scored instances.

This is not a paper-scale benchmark. It is a go/no-go test for whether the
diagnosis-to-action gap exists and is worth scaling.

## 4. Dataset plan

### Main substrate: AVQA / MUSIC-AVQA-style data

Use audio-video QA data where answer evidence genuinely depends on audio and/or
video.

Preferred source families:

- AVQA;
- MUSIC-AVQA;
- similar audio-video reasoning datasets with raw audio/video and questions.

Rationale:

- avoids MELD/MOSEI text dominance;
- naturally exposes audio neglect and video degradation;
- supports temporal mismatch and audio-video complementarity;
- better aligned with evidence governance than affective final-label datasets.

### Text-evidence feasibility subset

Because AVQA-style question text is a task instruction, not a corruptible text
evidence channel, the pilot should add one small optional subset if feasible:

- TVQA / How2QA-style subtitle examples;
- caption-bearing video examples;
- ASR transcript generated from AVQA-style audio;
- any small source where transcript/subtitle is an evidence modality.

Target:

- 10-20 source items or 20-40 scored instances.

Purpose:

- test whether text over-trust and transcript/caption corruption are feasible;
- decide whether the scaled benchmark should claim full text-audio-video
  evidence governance.

If this subset is not feasible, the pilot report must explicitly state that the
pilot validates audio-video governance only.

## 5. Source-item buckets

Do not randomly sample. Select by modality necessity.

Target allocation:

| Bucket | Source items | Episodes per item | Purpose |
|---|---:|---:|---|
| Audio-necessary | 10 | 3-4 | Test audio neglect. |
| Video-necessary | 10 | 3-4 | Test visual degradation and route choice. |
| Audio-video complementary | 10 | 3-4 | Test recoverability and evidence selection. |
| Conflict-prone / temporal-mismatch-prone | 8 | 3-4 | Test evidence governance under inconsistency. |
| Clean-hard / corrupted-irrelevant control | 5-8 | 2-3 | Test false alarms and over-triage. |

Before final selection, start from 80-120 candidate items and label:

```json
"modality_necessity": {
  "text_question_only": false,
  "audio_sufficient": false,
  "video_sufficient": false,
  "audio_video_joint_required": true,
  "human_confidence": "high"
}
```

Do not overrepresent source items solvable by question text, dataset priors, or
visual common sense alone.

## 6. Corruption episode mix

Use a balanced corruption mix:

| Family | Share | Examples |
|---|---:|---|
| Simple missing / severe degradation | 20% | mute key audio, freeze key frames |
| Mild / medium degradation | 20% | background noise, blur, low light, low bitrate |
| Temporal mismatch | 20% | shift audio relative to video; shift frames |
| Cross-modal conflict | 20% | audio cue and video cue imply different answers |
| Clean-hard / corrupted-irrelevant controls | 20% | no corruption but difficult; corrupt an irrelevant modality |

Cross-modal conflict should be present but not dominate. Conflict is a crowded
area because MMIR / CrossCheck-Bench are close; in this pilot, conflict is used
to stress action consistency, not to claim a new conflict benchmark.

Each corruption should record:

```json
{
  "corruption_id": "...",
  "affected_modality": "audio|video|text|cross_modal",
  "corruption_type": "...",
  "severity": "mild|medium|severe",
  "location": {
    "text_span": null,
    "audio_time": [0.0, 0.0],
    "video_time": [0.0, 0.0],
    "frame_range": null
  },
  "corruption_relevance": "answer_relevant|answer_irrelevant|unclear",
  "generator_family": "...",
  "seed": 0
}
```

## 7. Artifact controls

Include these in the pilot, not only the scaled benchmark:

- multiple noise sources / occlusion styles / mismatch types;
- realistic corruptions where possible;
- `clean-hard` controls;
- `corrupted-but-irrelevant` controls;
- a low-level `quality_only_route` detector baseline.

The quality-only baseline should use simple features:

- audio silence/noise/clipping proxy;
- video blur/freeze/brightness/motion proxy;
- text deletion / ASR confidence if text evidence exists.

If a trivial detector approaches oracle behavior, the corruption design is too
shallow.

## 8. Annotation schema v2

Each scored instance should include:

```json
{
  "instance_id": "...",
  "source_dataset": "AVQA_or_MUSIC_AVQA_or_text_subset",
  "question": "...",
  "modalities_presented": ["audio", "video"],
  "gold_answer": "...",
  "modality_necessity": {
    "text_question_only": false,
    "audio_sufficient": true,
    "video_sufficient": false,
    "audio_video_joint_required": false,
    "human_confidence": "high"
  },
  "modality_status": {
    "text": "not_applicable|clean|corrupted|conflicting|irrelevant",
    "audio": "clean|corrupted|missing|conflicting|irrelevant",
    "video": "clean|corrupted|missing|conflicting|irrelevant"
  },
  "defect_location": {
    "text_span": null,
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
    "note": "short natural language rationale"
  },
  "oracle_policy_action": {
    "selected_route": ["audio", "video"],
    "abstain": false
  },
  "oracle_route_rationale": "...",
  "annotation_confidence": "high|medium|low"
}
```

If a text-evidence subset is added, `modalities_presented` can include `text`,
and `recovery_source` may include text.

## 9. Recoverability v2

Recoverability must be task-conditioned:

| Label | Definition |
|---|---|
| recoverable | Given the corrupted instance and the question, another available clean modality contains sufficient task-relevant evidence to support the gold answer, and annotators can point to that evidence. |
| partially_recoverable | Another modality provides plausible but insufficient or indirect task-relevant evidence; a cautious model should lower confidence or abstain depending on risk policy. |
| unrecoverable | No available modality contains sufficient task-relevant evidence after corruption; correct behavior is abstention. |

Rule:

> If annotators cannot point to evidence, do not label the instance
> `recoverable`.

Add a model-relative check:

> For recoverable cases, test whether models can answer from the recovery
> modality under clean oracle-route conditions. This estimates whether human
> recoverability is also model-accessible.

## 10. Policy action vs task execution

Split action correctness into three layers:

### A. Policy action correctness

Does the model choose the right evidence action?

```text
policy_correct = route_correct AND abstention_correct AND no_budget_violation
```

### B. Task execution correctness

Can the model answer when given the correct route?

```text
answer_correct_given_oracle_route
```

### C. Governed success

Does the model both choose the right action and answer correctly?

```text
governed_success = policy_correct AND final_answer_correct
```

This prevents us from calling an answer failure a diagnosis-to-action failure.

## 11. Prompting and within-diagnosis rule lift

Use structured outputs for all action settings. Avoid comparing free-form
answers to structured rules.

### Settings

1. **Direct structured decision**
   - Model chooses route, answer, and abstain flag in one structured response.
2. **Diagnosis-only**
   - Model outputs modality status, defect notes, recoverability, and evidence.
   - It does not output final answer.
3. **Model action from frozen diagnosis**
   - Feed the model's own diagnosis back to it.
   - Ask it to choose route, answer, or abstain.
4. **Fixed rule from frozen diagnosis**
   - Apply deterministic action rules to the exact same model diagnosis.
5. **Oracle route**
   - Give gold route; model answers or abstains.
6. **Oracle defect-location**
   - Give gold defect location; model judges recoverability and action.
7. **Abstention-calibrated**
   - Explicitly instruct the model to abstain when evidence is insufficient.

Rule lift is now:

```text
RuleLift = Score(fixed_rule(model_diagnosis)) - Score(model_action(model_diagnosis))
```

This is a within-diagnosis comparison. The only intended difference is whether
the action is chosen by the model or by a fixed rule.

Report parsing failure rate for structured outputs.

## 12. Primary metrics

Keep the pilot main table small.

Primary metrics:

| Metric | Purpose |
|---|---|
| Diagnosis macro-F1 | Does the model identify unreliable evidence? |
| Recoverability macro-F1 | Does it know whether evidence can be recovered? |
| Policy action accuracy | Are route and abstention decisions correct? |
| Self-inconsistency rate | Does the model act against its own diagnosis? |
| Conditional action failure | Is action wrong when diagnosis is correct against gold? |
| Rule lift | Can fixed rules use stated diagnosis better than the model does? |
| False answer rate on unrecoverable | Does the model answer when it should abstain? |

Secondary metrics:

- final answer accuracy;
- defect-location hit rate;
- recovery-source accuracy;
- evidence hit rate;
- route regret;
- budget violation;
- false abstention;
- coverage-risk curve.

The story should not lead with final answer accuracy.

## 13. Diagnosis-to-action error taxonomy

Classify each model failure:

| Case | Interpretation |
|---|---|
| diagnosis wrong, action wrong | diagnosis / perception failure |
| diagnosis correct, route wrong | diagnosis-to-routing gap |
| diagnosis correct, route correct, answer wrong | task execution failure |
| diagnosis correct, recoverability wrong | evidence recovery judgment failure |
| diagnosis correct, abstention wrong | risk-policy failure |
| final answer correct, diagnosis/action wrong | final-answer masking |
| self-inconsistent action | model acts against its own stated diagnosis |

Produce 10-15 qualitative cases across these types.

## 14. Pilot go/no-go thresholds

These are rough pilot thresholds, not final paper claims.

Continue and scale if:

- self-inconsistency appears in at least 2 models and at least 10 qualitative
  cases;
- conditional action failure exceeds 25-30% on at least one meaningful subset;
- rule lift improves at least 5-10 points on a key subset;
- final-answer masking affects at least 15-20% of correct-answer cases;
- unrecoverable false-answer rate is materially higher than false-abstention
  rate;
- quality-only detector does not approach oracle behavior;
- recoverability annotation reaches at least moderate agreement.

Redesign or pivot if:

- most errors come from obvious synthetic artifacts;
- most source items are solvable from question/text priors;
- annotators cannot agree on recoverability;
- oracle route and full multimodal behavior are almost identical;
- frontier models are near oracle across both diagnosis and action;
- audio-capable model access is too limited after verification.

## 15. Model panel feasibility

Expert reviewers suggest that there may now be enough audio-video-capable MLLMs
to run this pilot, including closed-source and open-source candidates. This must
be verified before execution.

Pilot requirement:

- at least 2 closed-source models if accessible;
- at least 2 open-source models if feasible;
- at least 2 models that can process audio and video in the same instance.

Before implementation, verify:

- exact input modalities supported;
- audio/video synchronization behavior;
- video frame sampling policy;
- audio sampling rate and duration limits;
- structured-output reliability;
- API cost and rate limits.

Do not build the final claim around models whose audio-video input path is not
confirmed.

## 16. Expected deliverables

- `pilot_source_items.csv`
- `pilot_modality_necessity.jsonl`
- `pilot_corruption_manifest.jsonl`
- `pilot_annotations.jsonl`
- `annotation_guideline_v0.md`
- `model_diagnoses.jsonl`
- `model_actions.jsonl`
- `fixed_rule_actions.jsonl`
- `pilot_metrics.csv`
- `qualitative_failures.md`
- `go_no_go_memo.md`

## 17. Expert-review questions for this v2

1. Is it correct to narrow the pilot to audio-video evidence governance under
   textual queries?
2. Is the optional transcript/caption subset necessary for the pilot, or only
   for the scaled benchmark?
3. Does self-inconsistency deserve to be the primary headline over
   gold-conditional action failure?
4. Is the within-diagnosis rule-lift design clean enough?
5. Are the go/no-go thresholds reasonable for a 100-200 instance pilot?
6. Should cross-modal conflict be reduced further to avoid overlap with
   MMIR/CrossCheck-Bench?
7. What is the minimum model panel needed before this pilot is meaningful?

## 18. Current recommendation

Run the v2 pilot as:

- primary: 40 AVQA / MUSIC-AVQA-style source items;
- optional: 10-20 text-evidence source items if feasible;
- 4 corruption episodes per main item;
- 160 main scored instances;
- balanced corruption mix with controls;
- diagnosis-only prompt, model-action prompt from frozen diagnosis, fixed-rule
  action from frozen diagnosis, oracle route, oracle defect-location, and
  abstention-calibrated settings;
- primary analysis: self-inconsistency, policy action accuracy, rule lift, and
  false-answer rate on unrecoverable cases.

If this shows a robust diagnosis-to-action gap that is not explained by
synthetic artifacts, text/question priors, or label ambiguity, then scale. If
not, do not build the large benchmark yet.
