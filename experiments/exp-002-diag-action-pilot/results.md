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

- the 5-clip annotation sheet exists as
  `annotations/smoke_annotation_sheet_v1.draft.{jsonl,csv}`, but it is a draft
  review sheet, not human-adjudicated gold.
- the annotator-facing task protocol now lives at
  `annotations/annotation_task_protocol_v1.md`. This should be used as the
  normative annotation procedure before producing gold labels.
- the v1 scorer is implemented and verified with a 3-row fixture. The fixture
  intentionally produces `conditional_policy_failure=0.5`, `policy_action_accuracy=0.666667`,
  and `rule_lift=0.333333`.
- current real Qwen model results are still access/format evidence until the
  smoke or pilot annotation sheet is manually reviewed and action outputs are
  generated.

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

## Boundary

MELD is not the main positive substrate for this experiment. It may be used only
as a diagnostic/control reference if needed.
