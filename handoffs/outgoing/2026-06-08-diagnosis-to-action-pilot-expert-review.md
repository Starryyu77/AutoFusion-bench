# Handoff: Diagnosis-to-Action Pilot Design

> Generated 2026-06-08. Self-contained pilot-design draft for expert review.

## 1. Why this pilot exists

We have revised the paper story after expert feedback. The work should not be
framed as "another missing-modality robustness benchmark" or as five independent
new tasks. The sharper story is:

> Multimodal LLMs may diagnose unreliable multimodal evidence, but fail to act
> correctly on that diagnosis.

We call this the **diagnosis-to-action gap**.

The goal of this pilot is not to produce a paper-scale dataset. It is a
go/no-go experiment that tests whether this story is real enough to scale.

The pilot should answer:

1. Do current MLLMs show nontrivial failures in evidence diagnosis,
   recoverability judgment, routing, answering, or abstention?
2. More specifically, do they ever diagnose evidence degradation correctly but
   still take the wrong action?
3. Are these failures caused by real multimodal evidence reasoning problems, or
   just obvious synthetic corruption artifacts?
4. Are recoverability, evidence location, oracle route, and abstention labels
   feasible for humans to annotate consistently?

If this pilot does not show a clear and interpretable diagnosis-to-action gap,
we should sharpen the task or pivot before building a large benchmark.

## 2. Short project story for this pilot

Modern MLLMs can read text, listen to audio, and watch video. Existing
benchmarks often ask whether they can answer correctly. In real settings,
however, evidence quality varies by sample: a transcript may be wrong, audio may
be noisy or misaligned, video may be occluded, and modalities may conflict.

The right behavior is not always "use all modalities." Sometimes the model
should ignore a corrupted modality, switch to another modality, spend less
budget, or abstain because the missing evidence is unrecoverable.

This pilot tests whether MLLMs can govern unreliable evidence:

```text
unreliable evidence
  -> diagnose what is unreliable
  -> judge whether information is recoverable
  -> choose evidence route / answer / abstain
```

The pilot's central measurement is:

> When the model knows what is wrong, does it act accordingly?

## 3. Unit definitions

We use three terms:

- **Source item**: one original data item, such as an audio-video QA example or
  multimodal clip with a question/label.
- **Corruption episode**: one controlled modification of a source item, such as
  muting the audio, freezing video frames, deleting transcript content, or
  creating cross-modal conflict.
- **Scored instance**: one model-facing evaluation sample produced from a
  source item plus a corruption episode.

Pilot scale:

- 30-50 source items.
- 3-4 corruption episodes per source item.
- 100-200 scored instances.

This is large enough to reveal failure patterns but small enough to manually
inspect every sample.

## 4. Dataset substrate proposal

### Primary substrate: AVQA / MUSIC-AVQA-style data

The primary pilot substrate should be an audio-video QA dataset, ideally:

- AVQA;
- MUSIC-AVQA;
- a similar audio-video reasoning dataset with raw video, raw audio, and
  natural-language questions.

Reason:

- We need examples where audio and video genuinely matter.
- Affective datasets such as MELD/MOSEI are likely text-dominant and too close
  to existing missing-modality affective computing benchmarks.
- AVQA-style data makes audio neglect, video occlusion, temporal mismatch, and
  audio-video recoverability easier to test.

### Secondary substrate: filtered affective/control data

Optional secondary substrate:

- IEMOCAP or carefully filtered MOSEI.

Use only if we can filter for examples where audio or video genuinely changes
the answer. MELD should not be the main pilot substrate; it may be used as a
control split or appendix-style stress case.

### Open design issue for expert review

AVQA-style datasets usually provide a natural-language question, audio, and
video. The question is text, but it is not the same as transcript evidence. If
our paper claims text-audio-video evidence governance, we need to decide:

- Is question text sufficient as the text channel for the pilot?
- Do we need transcript/caption-bearing datasets to truly test text as an
  evidence modality?
- Should the pilot first focus on audio-video evidence governance and reserve
  text-transcript corruption for a later dataset?

My current recommendation:

> Use AVQA/MUSIC-AVQA as the primary pilot even if the text channel is mostly
> question text, because it is better to validate audio-video diagnosis-action
> failures on non-text-dominant data than to force a text-heavy dataset. Add a
> small transcript/caption subset only if it is feasible.

## 5. Source-item selection

The pilot should not sample randomly. We should first select examples with
nontrivial modality dependence.

Target source-item buckets:

| Bucket | Meaning | Why include |
|---|---|---|
| Audio-necessary | Answer depends mainly on sound. | Tests whether models ignore audio. |
| Video-necessary | Answer depends mainly on visual evidence. | Tests video degradation and route choice. |
| Audio-video complementary | Audio and video together disambiguate the answer. | Tests recoverability and route selection. |
| Conflict-prone | Audio/video/text can be made inconsistent. | Tests evidence governance under conflict. |
| Text/control | Text alone is sufficient or misleading. | Tests text over-trust and provides control. |

Selection procedure for the pilot:

1. Start with 80-120 candidate source items.
2. Manually or semi-automatically label modality necessity:
   - audio needed;
   - video needed;
   - audio+video needed;
   - text/question-only solvable;
   - unclear.
3. Keep 30-50 items that span the first four buckets.
4. Do not overrepresent text-only-solvable cases.

For a later benchmark, this should become a formal modality-necessity filtering
stage using unimodal baselines and human review. For pilot, careful manual
selection is acceptable.

## 6. Corruption episode design

The pilot should include both obvious and subtle degradation, but avoid making
all failures trivially detectable.

### Episode families

| Family | Example corruption | Intended test |
|---|---|---|
| A1 Audio missing | mute the key audio segment | Can the model know audio is unavailable and switch/abstain? |
| A2 Audio degraded | noise, low bitrate, clipping, overlapping sound | Can the model distinguish weak audio from usable audio? |
| A3 Audio temporal mismatch | shift or replace audio segment | Can the model detect audio-video misalignment? |
| V1 Video missing/frozen | freeze key frames or remove visual segment | Can the model avoid relying on broken visual evidence? |
| V2 Video degraded | blur, low light, occlusion, crop | Can the model localize visual degradation? |
| V3 Video temporal mismatch | shift frames relative to audio | Can the model detect temporal inconsistency? |
| T1 Text/transcript corruption | ASR-like error, deletion, contradiction, if transcript exists | Can the model avoid over-trusting text? |
| X1 Cross-modal conflict | audio says one thing, video implies another | Can the model detect conflict and decide action? |
| X2 Corrupted but irrelevant | corrupt a modality that is not needed for answer | Tests over-triage and unnecessary abstention. |
| X3 Clean but hard | no corruption, but evidence is difficult | Tests false alarms. |

Each corruption episode should record mechanical metadata:

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
  "generator_family": "...",
  "seed": 0
}
```

### Artifact-control requirements

Even in the pilot, we should include artifact defenses:

- do not use only one noise type or one occlusion shape;
- include at least a few natural or realistic corruptions, such as real ASR
  errors, realistic background noise, real low-light/blur cases, or naturally
  hard videos;
- include `clean-but-hard` controls;
- include `corrupted-but-irrelevant` controls;
- include at least one simple low-level quality detector baseline, even if
  rough.

If a trivial detector solves diagnosis, then the pilot is not measuring the
right phenomenon.

## 7. Human annotation schema

The pilot should manually verify the labels that are central to the paper
story.

### Required labels

```json
{
  "instance_id": "...",
  "source_dataset": "AVQA_or_MUSIC_AVQA",
  "question": "...",
  "modalities_presented": ["text", "audio", "video"],
  "gold_answer": "...",
  "modality_status": {
    "text": "clean|corrupted|missing|conflicting|irrelevant|not_applicable",
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
  "recoverability": "recoverable|partially_recoverable|unrecoverable",
  "recovery_source": ["text", "audio", "video"],
  "recovery_evidence": {
    "text_span": null,
    "audio_time": [0.0, 0.0],
    "video_time": [0.0, 0.0],
    "note": "short natural language rationale"
  },
  "oracle_route": ["audio", "video"],
  "abstention_label": false,
  "annotation_confidence": "high|medium|low"
}
```

### Recoverability definitions

| Label | Definition |
|---|---|
| recoverable | The lost or corrupted target information is clearly available from another clean modality, and an annotator can point to evidence. |
| partially_recoverable | Another modality provides weak or indirect evidence, but not enough for a high-confidence answer. |
| unrecoverable | After corruption, no available modality supports the answer; the correct behavior is abstention. |

### Oracle route definition

The oracle route is the minimum sufficient modality subset under the active
budget.

For pilot, define simple route costs:

```text
text = 1
audio = 2
video = 3
```

Example:

- if audio alone is enough and budget allows audio, oracle route = `[audio]`;
- if audio is corrupted but video contains the recoverable cue, oracle route =
  `[video]`;
- if audio+video are both needed, oracle route = `[audio, video]`;
- if no available route can support the answer, abstention_label = true.

We can refine the cost model later. The pilot only needs a consistent rule that
forces route decisions.

## 8. Model evaluation design

### Models

Pilot target:

- 2 closed-source MLLMs if accessible;
- 2 open-source MLLMs if feasible;
- at least one model that can use audio+video, not only image/video frames.

If true audio+video+text models are hard to access, we should record this as a
feasibility risk. The pilot can still start with the best available models, but
the paper story will be weaker if only one or two models truly process audio.

### Prompting / decision settings

Run the same instance under these settings:

1. **Direct answer**
   - Model sees available modalities and answers the task.
2. **Explicit diagnosis**
   - Model first outputs modality status and defect notes, then answers.
3. **Two-stage diagnose -> route -> answer**
   - Model diagnoses, selects route, then answers or abstains.
4. **Diagnosis with evidence citation**
   - Model must cite evidence span/time/region.
5. **Abstention-calibrated prompt**
   - Model is explicitly told to abstain when evidence is insufficient.
6. **Oracle route prompt**
   - Model is given the gold route and only needs to answer/abstain.
7. **Oracle defect-location prompt**
   - Model is given defect location and must decide recoverability/action.
8. **Stated-diagnosis-then-rule**
   - Model states diagnosis; a fixed external rule maps diagnosis to route or
     abstention.

The last setting is essential. It tests whether the model's own stated
diagnosis is useful, even if the model fails to act on it directly.

## 9. Baselines

Minimum pilot baselines:

1. `text_only`
2. `audio_only`
3. `video_only`
4. `full_multimodal`
5. `random_legal_route`
6. `static_best_route`
7. `oracle_route`
8. `quality_only_route`
9. `stated_diagnosis_then_rule`

Quality-only route can be simple in pilot:

- audio quality score from silence/noise/clipping proxy;
- video quality score from blur/freeze/brightness proxy;
- text quality score from deletion/ASR confidence when applicable.

This baseline is important because it tells us whether the benchmark is
solvable by low-level quality detection rather than multimodal reasoning.

## 10. Metrics

Pilot metrics should be few and directly tied to the story.

### Track A: Evidence triage

- modality diagnosis macro-F1;
- defect-location hit rate;
- recoverability macro-F1;
- recovery-source accuracy;
- evidence hit rate.

### Track B: Decision under evidence constraint

- final answer accuracy;
- abstention false answer rate on unrecoverable cases;
- false abstention rate on recoverable cases;
- oracle-route match;
- route regret;
- budget violation rate.

### Diagnosis-to-action metrics

These are the most important:

1. **Conditional action failure**

```text
P(action incorrect | diagnosis correct)
```

If this is high, the model can diagnose but cannot act.

2. **Diagnosis-action consistency**

Whether the selected route and abstention decision are consistent with the
model's own stated diagnosis.

3. **Rule lift**

```text
Score(stated_diagnosis_then_rule) - Score(model_end_to_end_action)
```

If rule lift is positive, the model's diagnosis contains useful information
that its own action policy fails to exploit.

4. **Final-answer masking**

Cases where final answer is correct but diagnosis/action is wrong.

This shows why final-answer benchmarks overestimate reliability.

## 11. Qualitative failure taxonomy

The pilot should produce 10-15 qualitative cases, grouped by failure type:

- final answer correct, evidence diagnosis wrong;
- diagnosis correct, route wrong;
- diagnosis correct, abstention wrong;
- recoverability confused with unrecoverability;
- text over-trusted despite text conflict or ASR error;
- audio ignored despite audio being necessary;
- video trusted despite occlusion/freeze/misalignment;
- model detects conflict but still answers with high confidence;
- trivial quality-detector solves the case, meaning it is not a good benchmark
  item.

These examples will tell us whether the paper story is vivid enough.

## 12. Pilot go/no-go criteria

| Observation | Decision |
|---|---|
| Clear nontrivial diagnosis-to-action gap | Continue and scale benchmark. |
| Rule lift is positive on meaningful subsets | Strong evidence for the story. |
| Final answer hides diagnosis/action errors | Good benchmark motivation. |
| Most failures are obvious synthetic artifacts | Redesign corruption. |
| Most source items are solvable by text/question alone | Change data or filter harder. |
| Recoverability labels have low annotator agreement | Rewrite label definitions. |
| Oracle route and full multimodal behavior are nearly identical | Downweight routing, emphasize recoverability and abstention. |
| Frontier models are near oracle across diagnosis/action | Sharpen task or pivot. |
| Audio-capable model access is too limited | Narrow paper to video-text-temporal governance or delay audio claims. |

## 13. Expected pilot deliverables

The pilot should produce:

- `pilot_source_items.csv`;
- `pilot_corruption_manifest.jsonl`;
- `pilot_annotations.jsonl`;
- `annotation_guideline_v0.md`;
- `model_outputs.jsonl`;
- `pilot_metrics.csv`;
- `qualitative_failures.md`;
- a short go/no-go memo.

The go/no-go memo should answer:

1. Is the diagnosis-to-action gap visible?
2. Which dataset/source bucket produced the clearest failures?
3. Which labels were hardest to annotate?
4. Which corruptions looked artificial?
5. What should change before scaling?

## 14. Questions for expert review

Please review this pilot design and answer:

1. Is the pilot aligned with the revised evidence-governance story?
2. Is AVQA/MUSIC-AVQA the right primary substrate, or do we need a dataset with
   stronger text/transcript evidence?
3. Are the corruption episodes realistic enough, or are they likely to create
   artifacts?
4. Are the recoverability and oracle-route labels well-defined enough for pilot
   annotation?
5. Is `stated-diagnosis-then-rule` a good way to isolate diagnosis-to-action
   gap?
6. Which metrics should be primary, and which should be appendix-only?
7. What would make the pilot convincing enough to scale?
8. What would make you recommend pivoting?

## 15. My current recommendation

Start with this pilot rather than a large benchmark:

- 40 source items from AVQA/MUSIC-AVQA-style data;
- 4 corruption episodes per item;
- 160 scored instances;
- manual annotation of recoverability, evidence, oracle route, and abstention;
- 2 closed-source and 2 open-source MLLMs if possible;
- direct, explicit diagnosis, two-stage, oracle route, oracle defect-location,
  and stated-diagnosis-then-rule settings;
- report conditional action failure and rule lift as the main pilot metrics.

If this shows a diagnosis-to-action gap that is not explained by artifact or
text dominance, then scale. If not, do not build a large benchmark yet.
