# Headline Metric and Main Table Design (2026-06-19)

> Status: Decision-Team draft. Locks the irreplaceable headline metric and
> the main-table shape so experiments serve one story, not five scattered
> scores. Consistent with the v1 scorer fields and the screening/scoring
> guideline (Stage C).

## 0. The one number that must be ours

Final-answer accuracy and even diagnosis-F1 are covered by prior work. The
metric that encodes our contribution and that the 2026-06-19 scan could not
find elsewhere:

```text
conditional_policy_failure (CPF) = P(policy_action_correct = false | triage_diagnosis_right = true)
```

Read as: **given the model correctly diagnosed the evidence, how often does it
still act wrong** (wrong route, answers when it should abstain, uses the
modality it just called broken). CPF > 0 with meaningful n is the
diagnosis-to-action gap, in one number.

Paired with one control metric:

```text
rule_lift = policy_action_accuracy(fixed_rule_on_frozen_diagnosis) - policy_action_accuracy(model_action)
```

`rule_lift > 0` means a trivial rule using the model's *own* diagnosis beats
the model's own action — i.e. the bottleneck is acting on diagnosis, not
producing it. That single comparison reframes the paper from "another broken-AV
dataset" to "models know but don't act."

## 1. Metric stack (report all; headline is CPF + rule_lift)

| Layer | Metric | Why it is here |
|---|---|---|
| Parse | parse_success_rate | input-contract / fairness guard, per model |
| Diagnosis | health_macro_F1, recoverability_macro_F1 | can the model *diagnose*? (not novel alone) |
| Action | policy_action_accuracy | does it pick an acceptable route / abstain correctly? |
| **Gap (headline)** | **conditional_policy_failure** | acts wrong *despite* correct diagnosis |
| **Gap (headline)** | **rule_lift** | fixed-rule-on-own-diagnosis vs model action |
| Consistency | self_inconsistency_rate | says X broken, then routes to X / uses it |
| Safety | false_answer_rate_on_unanswerable | answers when gold = abstain |
| | false_abstention_on_answerable | abstains when answerable (over-caution) |
| Outcome | answerable_task_accuracy | final answer on answerable rows only |
| | governed_success | route acceptable AND (answer right OR correctly abstained) |

Rule already fixed (C006): **policy-action correctness and final-answer
correctness stay separate** — route-correct-but-answer-wrong is task execution
failure, not a diagnosis-to-action failure.

## 2. Main table shape (mock)

Rows = systems; columns lead with the gap, not accuracy.

| System | Parse | Health F1 | Recov F1 | Policy acc | **CPF ↓** | **rule_lift** | False-ans@unans ↓ | Governed succ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Direct answer (no diagnosis) | | n/a | n/a | n/a | n/a | n/a | | |
| Model diagnosis → model action | | | | | **x** | — | | |
| Model diagnosis → fixed rule (control) | | (same frozen) | (same frozen) | | — | **+y** | | |
| Oracle route / oracle abstain (ceiling) | | 1.0 | 1.0 | 1.0 | 0 | — | 0 | |

The story is the gap between rows 2 and 3 (rule_lift) and the non-zero CPF in
row 2.

## 3. What each experiment row must prove (order = narrative)

1. Final-answer benchmarks hide governance errors → direct-answer row looks
   "fine" on answerable but fails @unanswerable.
2. Models show a diagnosis-to-action gap → CPF > 0 on rows where diagnosis is
   right.
3. A fixed rule on the model's own diagnosis matches or beats model action →
   rule_lift ≥ 0.
4. Abstention / recoverability are the hardest sub-skills → low recov F1,
   high false-answer@unanswerable.
5. The benchmark is not solved by trivial artifact detection → irrelevant-
   corruption control and clean-hard control behave as designed.

## 4. Two design risks the metric forces us to handle

- **Denominator size.** CPF conditions on "diagnosis right," a subset of the
  headline rows. On the mini-pilot (~17 headline candidates, many trivial),
  the CPF denominator may be ~3-6 rows — too small for a number, fine for
  go/no-go. Treat mini-pilot CPF as *existence evidence* ("interpretable
  diagnose-right-act-wrong cases exist"), and reserve the reported CPF value
  for the 40-source / ~160-instance pilot. Target: ≥ ~30 diagnosis-right rows
  in the denominator before quoting a rate.
- **Headline triviality.** If gold keeps only obvious unanswerable→abstain and
  single-route rows, CPF collapses to ~0 and gives a false no-go. The headline
  set must retain enough **non-trivial-action** rows: recoverable-via-other-
  modality and conflict cases. This couples directly to the gold-freeze plan:
  prioritize *resolving* (not excluding) the conflict and recoverable rows.

## 5. Controls that must ship with the main table

- irrelevant-corruption control (corruption on an answer-irrelevant modality):
  model should *not* false-alarm / change route.
- clean-hard control (clean but genuinely hard): separates "hard task" from
  "broken evidence."
- generator-metadata-as-baseline: a detector using only generator metadata
  should NOT solve the task → proves human labels add signal.
- oracle route / oracle abstention: ceiling rows.
