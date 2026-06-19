# exp-002 v1 Pilot Metrics

Headline conditional policy failure is:

`P(policy_action_correct=false | triage_diagnosis_right=true)`

Policy action correctness does not include final-answer correctness.

| model | headline_n | health_diagnosis_macro_F1 | recoverability_macro_F1 | policy_action_accuracy | conditional_policy_failure | rule_lift | false_answer_on_unanswerable |
| --- | --- | --- | --- | --- | --- | --- | --- |
| qwen3-omni-flash | 4 | 0.505952 | 0.477778 | 0.750000 |  | 0.000000 | 0.000000 |
| qwen3.5-omni-plus | 4 | 0.896296 | 0.666667 | 1.000000 | 0.000000 | 0.000000 | 0.000000 |

Rule lift is computed as fixed-rule policy action accuracy minus model
policy action accuracy on the same gold/action scoring contract.
