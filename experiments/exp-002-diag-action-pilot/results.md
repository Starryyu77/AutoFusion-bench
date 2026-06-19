# Results: exp-002

## Current status

Status: Phase 0 media smoke passed; Qwen-family model panel passed smoke; v1
annotation-sheet and scorer smoke are implemented.

The first-pilot model panel is now Qwen-only:

- `qwen3.5-omni-plus` as the main same-instance audio-video MLLM;
- `qwen3-omni-flash` as the second same-instance audio-video MLLM;
- `qwen3.7-plus` as a video/text control, not counted as audio-video.

## Phase 0 checklist

- [x] Remote repo synced after exp-002 initialization.
- [x] AVQA metadata staged on `ntu-gpu43`.
- [x] AVQA matched-video subset confirmed stageable from Hugging Face.
- [ ] Full dataset source selected.
- [ ] Dataset source staged or confirmed stageable on `ntu-gpu43`.
- [ ] At least 80-120 candidate source clips inspectable.
- [x] At least 2 audio-video-capable models verified in the Qwen family.
- [x] Five-clip media smoke completed.
- [x] Five-clip diagnosis prompt pack completed.
- [x] Five-clip model-call smoke completed for Qwen A/V panel.

## Phase 0 dataset notes

AVQA metadata can be downloaded on `ntu-gpu43`. The practical Hugging Face
package currently exposes 9,982 MP4 files that match 10,028 QA rows. A 15-video
sample balanced across `Sound`, `View`, and `Both` downloaded successfully, and
all sample MP4 files were readable through the existing `.deps/opencv` path.

Media smoke result:

- project-local `imageio-ffmpeg` installed under `.deps/audio` on `ntu-gpu43`
- 5 source MP4 files had audio+video streams
- 5 corrupted MP4 outputs retained audio+video streams
- corruption manifest passed schema validation

Model smoke result:

- DashScope/OpenAI-compatible client access was confirmed on `ntu-gpu43`.
- `qwen3.7-plus` text probe passed.
- `qwen3.7-plus` accepted a 1-clip video diagnosis request, but the response
  usage reported `video_tokens` and no `audio_tokens`; do not count it yet as a
  same-instance audio-video model.
- `qwen3.5-omni-plus` processed all 5 corrupted MP4 smoke instances with both
  audio and video tokens observed and 5/5 JSON parse success.
- `qwen3-omni-flash` processed all 5 corrupted MP4 smoke instances with both
  audio and video tokens observed and 5/5 JSON parse success.
- `qwen3.5-omni-flash` was attempted but the stream call stalled before a first
  row completed; it is deferred unless needed.

Current blocker:

- the 5-clip annotation sheet now has a first formal pass at
  `annotations/smoke_annotations_v1.codex_pass.jsonl`, but it is not
  human-adjudicated gold yet.
- the annotator-facing task protocol now lives at
  `annotations/annotation_task_protocol_v1.md`. This should be used as the
  normative annotation procedure before producing gold labels.
- the v1 scorer is implemented and verified with a 3-row fixture. The fixture
  intentionally produces `conditional_policy_failure=0.5`, `policy_action_accuracy=0.666667`,
  and `rule_lift=0.333333`.
- current real Qwen model results are still access/format evidence until the
  smoke or pilot annotation sheet is promoted to gold and action outputs are
  generated.

Smoke annotation pass:

- synced the 5 source/corrupted MP4 pairs from `ntu-gpu43` into local temp
  storage for inspection;
- generated visual contact sheets and ffmpeg volume diagnostics;
- produced `annotations/smoke_annotations_v1.codex_pass.jsonl`;
- produced `annotations/adjudication_notes_smoke_v1.md`;
- validation passed with `validate_jsonl.py --kind annotations`;
- summary: 5 rows, 4 accepted, 1 adjudication, 4 headline-eligible.

Scoring smoke result:

- `scripts/build_annotation_sheet_v1.py` generated the 5-row smoke annotation
  draft JSONL and CSV.
- `scripts/annotation_csv_to_jsonl_v1.py` converts reviewed CSV labels into
  scorer-compatible JSONL and can enforce `--strict-gold` checks.
- `scripts/score_v1_metrics.py` produced:
  - `results/scoring_smoke_per_instance.jsonl`
  - `results/scoring_smoke_metrics.csv`
  - `results/scoring_smoke_metrics.md`
- The scorer computes the headline metric as
  `P(policy_action_correct=false | triage_diagnosis_right=true)` and keeps final
  answer correctness separate from policy action correctness.

4-row smoke gold and real scorer run:

- froze `annotations/smoke_annotations_v1.gold.jsonl` from the local human
  export, using only rows with `source_decision=accept` and
  `instance_decision=accept`;
- intentionally excluded `smoke-video-necessary__video_blur` because it remains
  `partially_answerable` / adjudication-only;
- added `scripts/freeze_smoke_gold_v1.py`,
  `scripts/adapt_smoke_qwen_diagnoses_v1.py`, and
  `scripts/build_smoke_actions_v1.py`;
- adapted the existing `qwen3.5-omni-plus` and `qwen3-omni-flash` smoke
  diagnosis logs to scorer v1 rows;
- generated proxy model-implied actions and fixed-rule actions from the same
  frozen diagnosis rows;
- ran `scripts/score_v1_metrics.py` on the real Qwen smoke outputs.

Outputs:

- `annotations/smoke_annotations_v1.gold.jsonl`
- `results/smoke_v1_real_scoring_per_instance.jsonl`
- `results/smoke_v1_real_scoring_metrics.csv`
- `results/smoke_v1_real_scoring_metrics.md`

Headline metrics:

| Model | Headline n | Health F1 | Recoverability F1 | Policy action accuracy | Conditional policy failure |
|---|---:|---:|---:|---:|---:|
| `qwen3.5-omni-plus` | 4 | 0.896296 | 0.666667 | 1.000000 | 0.000000 |
| `qwen3-omni-flash` | 4 | 0.505952 | 0.477778 | 0.750000 | n/a |

Interpretation:

- this is a real scorer run over real Qwen diagnosis outputs, not only the
  synthetic fixture;
- the action rows are proxy actions derived from diagnosis, not a fresh model
  action-call result;
- `answer` is intentionally `null` in generated actions to avoid leaking gold
  answers, so final-answer execution accuracy is not the target metric of this
  smoke;
- `qwen3.5-omni-plus` has a clearer diagnosis signal than `qwen3-omni-flash` on
  this tiny smoke set, but the sample is too small for a paper claim.

4-row real action run:

- added `prompts/action_from_diagnosis_prompt_v1.md`;
- added `scripts/run_dashscope_real_actions.py`;
- ran real action calls for `qwen3.5-omni-plus` and `qwen3-omni-flash` on the
  4-row smoke gold;
- each call consumed the corrupted media, the question/options, and the frozen
  diagnosis row for the same model;
- both models produced 4/4 parseable action JSON rows;
- no API key is stored in the result files.

Outputs:

- `results/smoke_v1_real_action_logs.qwen35_omni_plus.jsonl`
- `results/smoke_v1_real_action_logs.qwen3_omni_flash.jsonl`
- `results/smoke_v1_real_actions.qwen35_omni_plus.jsonl`
- `results/smoke_v1_real_actions.qwen3_omni_flash.jsonl`
- `results/smoke_v1_real_actions.combined.jsonl`
- `results/smoke_v1_fixed_rule_actions.jsonl`
- `results/smoke_v1_real_action_scoring_per_instance.jsonl`
- `results/smoke_v1_real_action_scoring_metrics.csv`
- `results/smoke_v1_real_action_scoring_metrics.md`

Real-action headline metrics:

| Model | Policy action accuracy | Conditional policy failure | Task accuracy on answerable rows | Governed success |
|---|---:|---:|---:|---:|
| `qwen3.5-omni-plus` | 1.000000 | 0.000000 | 0.666667 | 0.750000 |
| `qwen3-omni-flash` | 0.750000 | n/a | 0.333333 | 0.500000 |

Interpretation:

- the action-stage route/abstention scores match the earlier proxy-action smoke,
  so the proxy path was directionally consistent for this 4-row set;
- real action adds final-answer evidence: both models selected the right visual
  route for `smoke-conflict-like__audio_replace_conflict_like`, but answered
  `street` while the gold answer is `On the road`;
- this is a useful pilot warning: policy action correctness and final answer
  correctness must remain separate metrics.

## Boundary

MELD is not the main positive substrate for this experiment. It may be used only
as a diagnostic/control reference if needed.
