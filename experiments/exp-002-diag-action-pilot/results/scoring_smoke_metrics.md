# exp-002 v1 Pilot Metrics

Headline conditional policy failure is:

`P(policy_action_correct=false | triage_diagnosis_right=true)`

Policy action correctness does not include final-answer correctness.

| model | headline_n | health_diagnosis_macro_F1 | recoverability_macro_F1 | policy_action_accuracy | conditional_policy_failure | rule_lift | false_answer_on_unanswerable |
| --- | --- | --- | --- | --- | --- | --- | --- |
| qwen-test | 3 | 0.500000 | 1.000000 | 0.666667 | 0.500000 | 0.333333 | 0.000000 |

Rule lift is computed as fixed-rule policy action accuracy minus model
policy action accuracy on the same gold/action scoring contract.
