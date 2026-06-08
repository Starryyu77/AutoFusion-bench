---
type: screening-scoring-guideline-expert-reply-synthesis
target: handoffs/outgoing/2026-06-08-screening-scoring-guideline-expert-review.md
created: 2026-06-08
source:
  - /Users/starryyu/.codex/attachments/39a15d6e-e8f0-4f04-ae6f-7e04127e99a9/pasted-text.txt
decision: minor revision before freeze
---

# Screening / Scoring Guideline Expert Reply Synthesis

## Executive read

The expert's verdict is:

> minor revision before freeze

The direction is correct and not overcomplicated. The three-layer design is
accepted:

- source screening;
- corrupted-instance labeling;
- model-output scoring.

The evidence-pointer gate for recoverability is also accepted and should be
kept:

> If annotators cannot point to evidence, do not label the instance
> recoverable.

The main requested changes are not about changing the project story. They are
about separating concepts that were mixed in v0 and would otherwise create
reviewer risk.

## Strong points to keep

### 1. Three-layer design

The source / corrupted-instance / model-output split is necessary. It separates
whether a clean source is usable, whether a corrupted instance remains
answerable, and whether a model acts consistently on its own diagnosis.

### 2. Evidence-pointer-gated recoverability

Recoverability should stay task-conditioned and evidence-backed. Human intuition
without a pointer is not enough.

### 3. Diagnosis-to-action scoring

The core paper phenomenon remains strong:

> models may diagnose unreliable evidence but fail to convert that diagnosis
> into correct policy action.

Frozen-diagnosis fixed-rule comparison should remain because it isolates the
diagnosis-to-policy step.

## Required v1 revisions

### 1. Split quality status from task relevance

v0 used `modality_status` values such as:

```text
clean / corrupted / missing / conflicting / irrelevant / not_applicable
```

The expert warns that `irrelevant` is not a quality status. A modality can be
both corrupted and irrelevant for the current task. v1 should split:

```json
"modality_quality_status": {
  "audio": "clean|corrupted_usable|corrupted_unusable|missing|not_applicable",
  "video": "clean|corrupted_usable|corrupted_unusable|missing|not_applicable"
},
"modality_task_relevance": {
  "audio": "necessary|sufficient|supportive|irrelevant|unclear",
  "video": "necessary|sufficient|supportive|irrelevant|unclear"
},
"cross_modal_relation": "consistent|conflicting|misaligned|not_applicable|unclear"
```

### 2. Split answerability from cross-modal recoverability

v0 used `recoverability` for several different cases. The expert recommends:

```json
"post_corruption_answerability": "answerable|partially_answerable|unanswerable|unclear",
"cross_modal_recoverability": "recoverable|partially_recoverable|unrecoverable|not_needed|unclear"
```

This distinguishes:

- corrupted but still usable same-modality evidence;
- answerable through another modality;
- partially answerable cases;
- fully unanswerable cases.

### 3. Move partial cases out of headline scoring

Keep `partially_recoverable` for annotation and analysis, but do not use it as
hard headline gold. v1 should derive:

```json
"main_answerability": "answerable|unanswerable|exclude_from_main"
```

Partial cases should go to cautious / risk-sensitive / ambiguous analysis.

### 4. Add question-only blind screening

v1 should explicitly test whether a source can be answered from question and
choices alone:

```json
"question_only_blind": {
  "answerable_without_media": "yes|no|unclear",
  "blind_confidence": "high|medium|low",
  "blind_answer": "..."
}
```

High-confidence blind-correct examples should be removed from the main split.

### 5. Add corruption effect

`corruption_relevance` is useful but too coarse. v1 should add:

```json
"corruption_effect": "no_effect|route_change_only|confidence_drop|makes_unanswerable|creates_conflict|unclear"
```

This supports failure analysis: no effect, route change, confidence drop,
unanswerable, or conflict.

### 6. Allow multiple acceptable routes

Exact route match is too strict. v1 should replace a single route with:

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

Scoring should distinguish:

- `route_acceptable`;
- `route_preferred`;
- `route_disallowed`.

### 7. Define diagnosis-right levels

The denominator of conditional failure is unstable if `diagnosis_right` is too
broad or too narrow. v1 should define:

```text
health_diagnosis_right:
  modality quality/status correct

triage_diagnosis_right:
  modality quality/status + corruption relevance/effect correct

full_diagnosis_right:
  modality quality/status + corruption relevance/effect
  + answerability/recoverability + recovery source correct
```

Headline:

```text
conditional_policy_failure =
  P(policy_action_correct = false | triage_diagnosis_right = true)
```

### 8. Separate policy action from final answer correctness

Headline action correctness should not include final answer correctness. v1
should report:

- `policy_action_correct`: route acceptable + abstain correct;
- `task_execution_correct`: answer correct under oracle/preferred route;
- `governed_success`: policy correct + answer correct.

The headline diagnosis-to-action gap should use policy action, not final answer.

### 9. Parse failure policy by setting

Strict JSON parse should apply to structured settings, not every setting:

- direct answer: only extract answer / abstain;
- explicit diagnosis: strict JSON;
- two-stage diagnose-route-answer: strict JSON;
- diagnosis-only frozen: strict JSON;
- stated-diagnosis-then-rule: strict JSON diagnosis.

Always report parse failure rate.

### 10. Strengthen annotation quality control

For the 160-instance pilot:

- double annotate at least 80/160, ideally 160/160;
- `recoverability` agreement should reach at least kappa/AC1 >= 0.5 to
  continue; if below 0.4, rewrite definitions;
- abstention agreement should reach kappa/MCC >= 0.6;
- route agreement should report exact match, Jaccard, and per-modality F1;
- evidence pointer should use tolerance-hit / temporal IoU, not kappa;
- adjudication rate above 30% indicates the guideline is still unclear;
- ambiguous examples should not enter the main headline split.

For AAAI-style benchmark scale, aim for recoverability and abstention agreement
>= 0.6, preferably >= 0.7.

## Revised pilot instance quotas

The expert recommends forced quotas in the 160-instance pilot:

| Type | Suggested count | Purpose |
|---|---:|---|
| clean-hard | 15-20 | false alarm |
| corrupted-but-irrelevant | 20-25 | over-triage / unnecessary abstention |
| audio necessary + audio missing | 15-20 | unrecoverable abstention |
| audio necessary + video recoverable | 10-15 | cross-modal recovery |
| video necessary + video degraded usable | 10-15 | corrupted but usable |
| audio-video jointly required | 20 | route completeness |
| temporal mismatch | 20 | alignment reasoning |
| cross-modal conflict | 20 | conflict detection and action |
| prior-only trap | 10 | question/choice bias |
| partial recoverability | 10-15 | risk-sensitive / qualitative only |

## Main metrics after revision

Pilot main table should focus on six metrics:

| Metric | Purpose |
|---|---|
| `health_diagnosis_macro_F1` | quality/status diagnosis |
| `recoverability_macro_F1` | answerability / recovery judgment |
| `policy_action_accuracy` | route + abstain |
| `conditional_policy_failure` | headline diagnosis-to-action gap |
| `rule_lift` | fixed rule from frozen diagnosis |
| `false_answer_on_unanswerable` | reliability failure |

Move to appendix:

- final answer accuracy;
- governed success;
- route regret;
- budget violation;
- evidence pointer hit;
- parse failure rate;
- false abstention on answerable;
- per-corruption-family breakdown.

## Statistical reporting

Pilot scale should avoid overclaiming significance. Report:

- raw count + percentage;
- bootstrap 95% confidence interval;
- paired bootstrap for same-instance setting comparisons;
- McNemar-style tests only as supporting evidence;
- 3-5 qualitative cases for each key conclusion.

## AAAI implication

The revised standard can support a pilot and can become part of a benchmark
contribution, but 40 source / 160 corrupted instances is not enough for a full
AAAI benchmark paper.

AAAI-style benchmark target should eventually include:

- at least 1k-2k corrupted instances, preferably 3k+;
- at least two data families, including one with real text evidence;
- high-proportion double annotation and adjudication;
- at least 5-8 models;
- baselines including unimodal, full, oracle, quality-only, static route, and
  stated-diagnosis-rule;
- controls such as clean-hard, corrupted-irrelevant, natural corruption, and
  quality detector.

## Decision for the project

Adopt the expert's recommendation:

> revise v0 into v1, then freeze v1 for annotation sheet and scorer
> implementation.

Do not proceed with v0 unchanged.
