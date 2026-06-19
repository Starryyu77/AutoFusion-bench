---
type: pilot-expert-reply-synthesis
target: decision/handoffs/outgoing/2026-06-08-diagnosis-to-action-pilot-expert-review.md
created: 2026-06-08
sources:
  - /Users/starryyu/.codex/attachments/4513bf3e-ac9f-40cd-880c-c0b8fa45be07/pasted-text.txt
  - /Users/starryyu/.codex/attachments/9182ae21-8c6e-4d16-ad5b-324f076a7c6a/pasted-text.txt
---

# Pilot Expert Replies Synthesis

## Executive read

Both pilot-review replies agree that the story and pilot are mostly aligned:
the design now targets **diagnosis-to-action gap** rather than a flat T1-T5
benchmark. The reviewers do not recommend changing direction. They recommend a
more precise pilot claim and several measurement fixes before execution.

The most important revision is:

> The pilot should not claim to validate full text-audio-video evidence
> governance if the main substrate is AVQA / MUSIC-AVQA. Those datasets mainly
> provide audio-video evidence under a textual query; the question text is not
> the same as transcript/caption evidence.

Therefore, the pilot should be framed as:

> audio-video evidence governance under textual queries, with a small optional
> transcript/caption subset to probe whether the full text-audio-video claim is
> feasible for the scaled benchmark.

## Consensus revisions

### 1. Narrow the pilot claim

Do not write:

> The pilot evaluates text-audio-video evidence governance.

Write:

> The pilot tests whether diagnosis-to-action gap is observable in
> audio-video evidence governance under textual queries. A small
> transcript/caption subset may be added to test whether text evidence should
> enter the scaled benchmark.

Rationale:

- AVQA / MUSIC-AVQA questions are text, but they are task instructions, not
  corruptible evidence channels like transcript/subtitle/caption.
- Corrupting a question can change the task rather than corrupt evidence.
- The text over-trust story requires a real text-evidence channel.

### 2. Add a text-evidence decision point

The scaled benchmark can still target text-audio-video evidence governance, but
the pilot should explicitly decide how to support text evidence.

Options:

- keep pilot audio-video only and state that text evidence is deferred;
- add a small transcript/caption subset;
- use TVQA / How2QA-style data with subtitle or transcript evidence;
- generate ASR transcript for AVQA-style videos and treat it as an auxiliary
  evidence channel.

Recommendation for pilot:

> Main signal: AVQA / MUSIC-AVQA audio-video governance.  
> Small feasibility subset: transcript/caption/ASR evidence if available.

### 3. Make self-inconsistency the headline gap

The reviewers warn that gold recoverability and oracle route are partly
model-relative. Humans may judge a cue recoverable from another modality, but a
specific model may not be able to extract that cue. Therefore, the cleanest
headline should not rely only on "action incorrect vs human oracle."

Primary gap:

> diagnosis-action self-inconsistency: the model states that evidence is
> damaged or insufficient, but then chooses an action inconsistent with its own
> stated diagnosis.

Examples:

- model says audio is unusable but selects an audio route;
- model says evidence is insufficient but still answers confidently;
- model says video is occluded but ignores available audio recovery evidence;
- model detects conflict but refuses neither arbitration nor abstention.

Gold-based conditional action failure remains useful, but should be supporting
evidence.

### 4. Fix rule lift with within-diagnosis design

The original pilot listed `two-stage diagnose -> route -> answer` and
`stated-diagnosis-then-rule` as separate settings. This creates prompt and
format confounds.

The revised design must reuse the same diagnosis:

1. Run a **diagnosis-only** prompt and freeze the model's structured diagnosis.
2. Feed the same diagnosis to:
   - the model's own action head / action prompt;
   - a fixed external rule.
3. Compare action outcomes.

This makes rule lift a within-diagnosis comparison:

```text
RuleLift = Score(fixed_rule(model_diagnosis)) - Score(model_action(model_diagnosis))
```

The only intended difference is who maps diagnosis to action.

### 5. Split action correctness

Action failure must not be confused with task-answer failure. Add three layers:

- **Policy action correctness**: route + abstention + budget behavior.
- **Task execution correctness**: answer correctness when oracle route is given.
- **Governed success**: policy action and final answer are both correct.

This separates:

- diagnosis failure;
- diagnosis-to-route gap;
- route-to-answer failure;
- abstention calibration failure.

### 6. Add modality necessity and corruption relevance to schema

The pilot needs explicit fields:

```json
"modality_necessity": {
  "text_question_only": false,
  "audio_sufficient": true,
  "video_sufficient": false,
  "audio_video_joint_required": false,
  "human_confidence": "high"
}
```

and:

```json
"corruption_relevance": "answer_relevant|answer_irrelevant|unclear"
```

These fields make oracle route and recoverability easier to defend, and they
support over-triage analysis on corrupted-but-irrelevant cases.

### 7. Make recoverability task-conditioned

Recoverability should be defined for the current question/answer pair, not for
all information in the corrupted modality.

Revised definition:

> Given the corrupted instance and the question, another available clean
> modality contains sufficient task-relevant evidence to support the gold
> answer, and annotators can point to that evidence.

If annotators cannot point to evidence, the label should not be `recoverable`.

### 8. Reduce routing's contribution weight

The toy route-cost model `text=1, audio=2, video=3` is acceptable for pilot, but
it is not a realistic budget model. The pilot should call this:

> constrained evidence selection

rather than a full cost-aware inference routing contribution.

Routing should serve the evidence-governance story:

- unnecessary evidence use;
- corrupted evidence use;
- missed necessary evidence;
- route regret;
- abstention under insufficient evidence.

### 9. Quantify go/no-go thresholds

The pilot should avoid vague "clear gap" judgments. Add rough thresholds:

- self-inconsistency appears in at least two models and at least 10 qualitative
  cases;
- conditional action failure exceeds 25-30% on at least one meaningful subset;
- rule lift improves at least 5-10 points on a key subset;
- final-answer masking affects at least 15-20% of correct-answer cases;
- unrecoverable false-answer rate is materially higher than false-abstention
  rate;
- quality-only detector does not approach oracle behavior;
- recoverability annotation reaches at least moderate agreement.

These are pilot decision thresholds, not final paper claims.

### 10. Keep the strong parts

The reviewers explicitly support:

- Track A / Track B design;
- stated-diagnosis-then-rule, after within-diagnosis correction;
- artifact-control set: natural corruption, clean-hard, corrupted-irrelevant,
  quality-only detector;
- modality-necessity filtering;
- go/no-go pilot before large benchmark;
- oracle route and oracle defect-location prompts.

## Updated pilot decision

Proceed with a revised pilot, but change the target from:

> full text-audio-video evidence governance

to:

> audio-video evidence governance under textual queries, plus a small
> text-evidence feasibility subset if available.

The primary headline should be:

> diagnosis-action self-inconsistency and within-diagnosis rule lift.

Gold-label conditional failure remains useful, but the paper should not depend
only on human oracle recoverability/route labels.
