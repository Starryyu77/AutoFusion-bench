# Results: exp-001

Status: full MELD feature-level runs completed; protocol passed, but the current
MELD producers do not pass the benchmark-signal criterion.

## 2026-05-14 protocol fixture smoke

Command:

```bash
python -m autofusion_bench.exp001.run_decision_surface_pilot \
  --config experiments/exp-001-decision-surface-pilot/config.yaml \
  --fixture-smoke
```

Observed local output:

```text
best_single_axis_oracle_regret_dt=7.000
best_single_axis_policy=clean_best
joint_gap_closure=1.0
protocol_passed=True
benchmark_signal_passed=True
joint_policy_passed=True
```

Interpretation: this is a fixture smoke only. It validates the implemented
budget gate, policy evaluation, leakage checks, and metric reporting. It is not
an empirical AutoFusion-Bench result and must not be cited as benchmark evidence.

## Implemented artifacts

- `autofusion_bench.exp001.run_decision_surface_pilot`
- cost-table budget-validity gate
- complete outcome-table validation
- policy evaluator for all exp-001 planned policies
- primary metric `best_single_axis_oracle_regret_dt`
- `pre_mask_illegal_proposal_rate`, `post_mask_budget_violation_rate`, and
  `fallback_regret`
- reliability-proxy boundary check
- q-only and q-shuffle diagnostic ingestion
- class-stratified corruption-manifest check
- local fixture and unit tests

## Remaining before empirical run

- sync/clone repo to `ntu-gpu43`
- acquire or stage MELD
- implement data/model producer for feature extraction and template-head
  evaluation
- generate real cost, outcome, q-proxy, q-diagnostic, and corruption manifest
  files
- run the analysis runner on measured tables

This checklist was completed on 2026-05-14 for the first raw-stats producer and
the later decoded-video/audio-concat producer. It remains here as historical
bring-up context.

## 2026-05-14 ntu-gpu43 fixture smoke

Server path:

```text
/usr1/home/s125mdg43_10/projects/AutoFusion-bench
```

Remote commit:

```text
0fb34e3
```

Remote checks:

```bash
python3 -m unittest tests.test_exp001_protocol
python3 -m autofusion_bench.exp001.run_decision_surface_pilot \
  --config experiments/exp-001-decision-surface-pilot/config.yaml \
  --fixture-smoke
```

Observed fixture output matched local smoke:

```text
best_single_axis_oracle_regret_dt=7.000
best_single_axis_policy=clean_best
joint_gap_closure=1.0
protocol_passed=True
benchmark_signal_passed=True
joint_policy_passed=True
```

Interpretation: server code bring-up is complete. This is still a fixture smoke,
not a MELD empirical result.

## 2026-05-14 MELD staging progress

Staged on `ntu-gpu43`:

```text
/usr1/home/s125mdg43_10/datasets/MELD/annotations
/usr1/home/s125mdg43_10/datasets/MELD/official/MELD.Features.Models.tar.gz
/usr1/home/s125mdg43_10/datasets/MELD/official/features
```

Observed annotation row counts:

```text
dev_sent_emo.csv: 1110 lines
test_sent_emo.csv: 2611 lines
train_sent_emo.csv: 9990 lines
```

Official feature tarball:

```text
size: 880M
sha256: 59131c6904ab1272912c6ebec7873524e6f90bce842b333bc27f02411718b2c3
```

Inspection: official feature tarball contains text/audio/bimodal feature pickles
and model weights, but no visual feature pickles. `MELD.Raw.tar.gz` download was
started in remote tmux session `meld_raw_download` to support the first complete
tri-modal producer path via raw MP4 file-stat visual features.

Raw staging completed:

```text
raw archive size: 10878146150 bytes
raw archive sha256: a56b4407d574195cbce470d86f9c9d72fcfea59b0e34502ecd4babee4a5c613e
raw root: /usr1/home/s125mdg43_10/datasets/MELD/official/raw/MELD.Raw
mp4 files observed: 15908
```

This is dataset staging progress only. No empirical outcome table has been
generated yet.

## 2026-05-14 producer plumbing smoke

Remote command:

```bash
python3 -m autofusion_bench.exp001.run_meld_table_producer \
  --annotations-dir /usr1/home/s125mdg43_10/datasets/MELD/annotations \
  --features-dir /usr1/home/s125mdg43_10/datasets/MELD/official/features \
  --video-source annotation_proxy \
  --output experiments/exp-001-decision-surface-pilot/outputs/meld-producer-plumbing-smoke \
  --seeds 0 \
  --max-train-samples 700 \
  --max-eval-samples 280
```

Observed:

```text
records={'train': 700, 'validation': 280, 'test': 280}
feature_sources={
  'text': '.../text_glove_average_emotion.pkl',
  'audio': '.../audio_embeddings_feature_selection_emotion.pkl',
  'video': 'annotation_proxy_not_empirical_visual'
}
```

Interpretation: producer plumbing can read staged MELD annotations and official
text/audio features and can emit all six table schemas. This output is not
benchmark evidence because visual features came from `annotation_proxy`.

## 2026-05-14 full MELD raw-stats producer

Producer command:

```bash
python3 -m autofusion_bench.exp001.run_meld_table_producer \
  --annotations-dir /usr1/home/s125mdg43_10/datasets/MELD/annotations \
  --features-dir /usr1/home/s125mdg43_10/datasets/MELD/official/features \
  --raw-root /usr1/home/s125mdg43_10/datasets/MELD/official/raw/MELD.Raw \
  --video-source raw_stats \
  --output experiments/exp-001-decision-surface-pilot/outputs/meld-producer \
  --seeds 0,1,2
```

Producer output:

```text
records={'train': 9989, 'validation': 1109, 'test': 2610}
feature_sources={
  'text': '.../text_glove_average_emotion.pkl',
  'audio': '.../audio_embeddings_feature_selection_emotion.pkl',
  'video': 'raw_stats:/usr1/home/s125mdg43_10/datasets/MELD/official/raw/MELD.Raw'
}
```

Generated measured tables:

```text
cost_table.csv: 8 lines
outcome_table.csv: 421 lines
q_policy_map.csv: 6 lines
q_proxy_table.csv: 3720 lines
q_diagnostics.csv: 3 lines
corruption_manifest.csv: 3720 lines
```

Analysis command consumed those six tables and completed:

```text
protocol_passed=True
benchmark_signal_passed=False
joint_policy_passed=True
best_single_axis_oracle_regret_dt=0.848
best_single_axis_policy=clean_best
pooled_standard_error=0.215
kendall_tau_b_clean_loose_vs_degraded_tight=0.810
joint_gap_closure=1.0
```

Budget gate:

```text
p95 spread=12.666
tight=2.064 ms
loose=2.342 ms
tight legal templates=T|A|V|TA|TV|AV
TAV illegal under tight
warning: TAV-vs-unimodal p95 ratio=1.080 < preferred 1.250
```

Leakage and legality gates passed:

```text
q_only_task_classifier=18.62 <= 40.0
q_shuffle_control=1.29 >= 0.5
post_mask_budget_violation_rate=0
```

Template means on test:

```text
clean_loose: T=34.708, TV=32.860, TAV=20.832, TA=19.882, AV=10.527, A=10.278, V=8.211
degraded_tight: T=23.810, TV=19.439, TA=16.159, TAV=13.868, A=9.063, AV=6.538, V=5.494
```

Interpretation:

- The protocol runner and full measured-table producer are functional.
- This first raw-stats feature-level MELD run does not pass the benchmark-signal
  criterion because `best_single_axis_oracle_regret_dt` is far below 3 F1 and
  clean-vs-degraded ranking remains similar.
- The likely cause is text dominance plus weak visual signal from raw file-stat
  features. This result should not be used as a positive AutoFusion-Bench claim.
- Next experimental step should improve the visual/audio feature producer or
  switch to a stronger visual feature source before treating MELD as the paper
  pilot.

## 2026-05-14 decoded-video producer improvement

Implemented producer changes:

```text
video_source=cv2_stats
audio_source=official_concat
```

`cv2_stats` decodes real MELD MP4 frames with OpenCV and computes frame-level
color, HSV, texture, histogram, motion, and metadata statistics. It uses a
feature cache under the producer output directory. If a raw MP4 is corrupt or
not decodable, that sample falls back to padded raw file-stat features so one bad
video cannot invalidate the whole table.

`official_concat` keeps the full utterance-level official audio feature and adds
the official dialogue-sequence audio feature when it covers every requested
utterance.

Remote dependency setup:

```text
/usr1/home/s125mdg43_10/projects/AutoFusion-bench/.deps/opencv
opencv-python-headless==4.10.0.84
```

Small-sample decoded-video smoke:

```bash
PYTHONPATH=.deps/opencv python3 -m autofusion_bench.exp001.run_meld_table_producer \
  --annotations-dir /usr1/home/s125mdg43_10/datasets/MELD/annotations \
  --features-dir /usr1/home/s125mdg43_10/datasets/MELD/official/features \
  --raw-root /usr1/home/s125mdg43_10/datasets/MELD/official/raw/MELD.Raw \
  --video-source cv2_stats \
  --audio-source official_concat \
  --output experiments/exp-001-decision-surface-pilot/outputs/meld-producer-cv2-smoke \
  --seeds 0 \
  --max-train-samples 700 \
  --max-eval-samples 280
```

Smoke result:

```text
records={'train': 700, 'validation': 280, 'test': 280}
feature_sources={
  'text': '.../text_glove_average_emotion.pkl',
  'audio': '.../audio_embeddings_feature_selection_emotion.pkl+.../audio_emotion.pkl',
  'video': 'cv2_stats:/usr1/home/s125mdg43_10/datasets/MELD/official/raw/MELD.Raw'
}
```

Smoke analysis result:

```text
protocol_passed=True
benchmark_signal_passed=True
joint_policy_passed=True
best_single_axis_oracle_regret_dt=3.420
joint_gap_closure=0.950
```

Interpretation: decoded-video/audio-concat producer is promising on a small
sample, but this is still a smoke result. It is not the final exp-001 empirical
result.

Full decoded-video producer was started on `ntu-gpu43`, but the local SSH
connection dropped with:

```text
No route to host
Broken pipe
```

At last verified progress, the cv2 feature cache contained `7750` records. A
later foreground run hit one corrupt MP4 (`dia125_utt3.mp4`) and the producer was
patched to tolerate such files. The final full decoded-video run has not yet
been confirmed because `gpu43.dynip.ntu.edu.sg` temporarily stopped resolving
from this machine. Resume by pulling latest `main` on `ntu-gpu43` and rerunning
the full `cv2_stats` producer command; existing cache should allow continuation.

## 2026-05-14 full MELD decoded-video/audio-concat producer

After DNS recovered, `ntu-gpu43` was reachable again:

```text
host: gpu43
user: s125mdg43_10
time: 2026-05-14 16:58 +08
```

Remote repo was fast-forwarded to `5666227`. The full decoded-video producer had
already completed before the local DNS failure was confirmed. The existing full
producer output was therefore used, and a duplicate tmux rerun was stopped after
verifying that all six runner input tables were present.

Producer output:

```text
output: /usr1/home/s125mdg43_10/projects/AutoFusion-bench/experiments/exp-001-decision-surface-pilot/outputs/meld-producer-cv2
records={'train': 9989, 'validation': 1109, 'test': 2610}
seeds=[0, 1, 2]
text=official text_glove_average_emotion.pkl
audio=official audio_embeddings_feature_selection_emotion.pkl + audio_emotion.pkl
video=cv2_stats over raw MELD MP4 files
```

Generated measured tables:

```text
cost_table.csv: 8 lines
outcome_table.csv: 421 lines
q_policy_map.csv: 6 lines
q_proxy_table.csv: 3720 lines
q_diagnostics.csv: 3 lines
corruption_manifest.csv: 3720 lines
```

Analysis output:

```text
output: /usr1/home/s125mdg43_10/projects/AutoFusion-bench/experiments/exp-001-decision-surface-pilot/outputs/meld-analysis-cv2
protocol_passed=True
benchmark_signal_passed=False
joint_policy_passed=True
best_single_axis_oracle_regret_dt=0.740
best_single_axis_policy=budget_only
feasible_oracle_degraded_tight_macro_f1=24.550
best_single_axis_degraded_tight_macro_f1=23.810
joint_degraded_tight_macro_f1=24.269
joint_gap_closure=0.620
pooled_standard_error=0.215
kendall_tau_b_clean_loose_vs_degraded_tight=0.619
rank_inversion_index=0.190
```

Budget gate:

```text
p95 spread=41.887
tight=4.176 ms
loose=10.241 ms
tight legal templates=T|A|V|TV
loose legal templates=T|A|V|TA|TV|AV|TAV
TAV-vs-unimodal p95 ratio=2.336
warnings=[]
```

Gate checks:

```text
budget_validity_gate=True
reliability_proxy_boundary_check=True
q_only_task_classifier=True
q_shuffle_control=True
class_stratified_corruption_check=True
post_mask_budget_legality_contract=True
```

Policy summary highlights:

```text
degraded_tight feasible_oracle=24.550
degraded_tight budget_only=23.810
degraded_tight joint=24.269
degraded_tight reliability_only=15.302
degraded_tight clean_best=11.487
degraded_tight static_full=11.487
degraded_tight random_legal=13.132
reliability_only degraded_tight pre_mask_illegal_proposal_rate=0.500
post_mask_budget_violation_rate=0 for executed policies
```

Interpretation:

- This is a real full MELD feature-level run with decoded video statistics and
  concatenated official audio features.
- It passes protocol, budget-validity, leakage-boundary, q-diagnostic,
  corruption-stratification, and post-mask legality gates.
- It still does not pass the benchmark-signal criterion. The primary regret is
  only `0.740` macro-F1 points, far below the required `3.0`, although it is
  above the pooled-SE noise check.
- The small-sample smoke signal did not survive the full run. The full result
  should be recorded as operational success but benchmark-signal negative.
- This producer should not be used as a positive AutoFusion-Bench result. The
  next experimental step should improve the semantic visual/audio feature
  producer or the modality-specific corruption design rather than trying to
  frame `cv2_stats` as the final paper evidence.

## 2026-05-14 full MELD semantic-visual producer

Implemented and ran the controlled semantic visual rerun requested after the
external results review.

Producer:

```text
video_source=semvis_clip
semvis_model=openai/clip-vit-base-patch32
semvis_frame_count=8
audio_source=official_concat
records={'train': 9989, 'validation': 1109, 'test': 2610}
seeds=[0, 1, 2]
```

The first full semantic producer completed and generated all six tables, but the
analysis runner rejected its original 128-row cached-feature head profile:

```text
budget-validity gate failed: cannot define tight tier from cost table with all
unimodal legal, at least one bimodal legal, and TAV illegal
```

This was caused by unstable p95 timing in the small 128-row profiling batch. The
profiler was changed to use up to 1024 validation rows, then the producer was
rerun while reusing the completed semantic feature cache. The accepted output is:

```text
producer: /usr1/home/s125mdg43_10/projects/AutoFusion-bench/experiments/exp-001-decision-surface-pilot/outputs/meld-producer-semvis-profile1024
analysis: /usr1/home/s125mdg43_10/projects/AutoFusion-bench/experiments/exp-001-decision-surface-pilot/outputs/meld-analysis-semvis-profile1024
```

Generated measured tables:

```text
cost_table.csv: 8 lines
outcome_table.csv: 421 lines
q_policy_map.csv: 6 lines
q_proxy_table.csv: 3720 lines
q_diagnostics.csv: 3 lines
corruption_manifest.csv: 3720 lines
```

Analysis output:

```text
protocol_passed=True
benchmark_signal_passed=False
joint_policy_passed=True
best_single_axis_oracle_regret_dt=1.869
best_single_axis_policy=clean_best
feasible_oracle_degraded_tight_macro_f1=25.679
best_single_axis_degraded_tight_macro_f1=23.810
joint_degraded_tight_macro_f1=25.679
joint_gap_closure=1.000
pooled_standard_error=0.215
kendall_tau_b_clean_loose_vs_degraded_tight=0.905
rank_inversion_index=0.048
```

Budget gate:

```text
p95 spread=4.011
tight=18.341 ms
loose=23.033 ms
tight legal templates=T|A|V|TA|TV
loose legal templates=T|A|V|TA|TV|AV|TAV
TAV-vs-unimodal p95 ratio=1.140
warning: preferred TAV-vs-unimodal cost separation not met: 1.140 < 1.250
```

Gate checks:

```text
budget_validity_gate=True
reliability_proxy_boundary_check=True
q_only_task_classifier=True
q_shuffle_control=True
class_stratified_corruption_check=True
post_mask_budget_legality_contract=True
```

Policy summary highlights:

```text
degraded_tight feasible_oracle=25.679
degraded_tight joint=25.679
degraded_tight clean_best=23.810
degraded_tight budget_only=23.810
degraded_tight reliability_only=19.443
degraded_tight static_full=23.810
degraded_tight random_legal=15.770
reliability_only degraded_tight pre_mask_illegal_proposal_rate=0.250
post_mask_budget_violation_rate=0 for executed policies
```

Template means on test:

```text
clean_loose: T=34.708, TV=28.958, TAV=21.883, TA=18.765, V=16.758, AV=16.250, A=11.979
degraded_tight: T=23.810, TV=17.176, TA=13.958, TAV=13.257, V=13.158, AV=11.287, A=10.746
```

Runtime notes:

- Full semantic CLIP feature extraction completed on `ntu-gpu43` with
  `CUDA_VISIBLE_DEVICES=2`.
- One corrupt MELD MP4 produced `moov atom not found`; the semantic producer
  tolerated it by assigning a zero semantic visual vector.
- The sklearn logistic heads emitted convergence warnings under semantic visual
  features. The run completed and is interpretable as a feature-level diagnostic
  result, but the warnings should be mentioned if this line is revisited.

Interpretation:

- Semantic visual features increased the oracle gap from `0.740` in the cv2 run
  to `1.869`, so the earlier producer was indeed too weak.
- The result is still below the 3 macro-F1 positive threshold and Kendall tau-b
  remains high (`0.905`), with very low rank inversion (`0.048`).
- `T` remains the dominant template in both clean-loose and degraded-tight; MELD
  still appears strongly text-dominant under this feature-level setup.
- This run is `negative-but-diagnostic`, not a positive AutoFusion-Bench result.
  It supports the interpretation that semantic visual features help, but not
  enough to make MELD a strong primary benchmark-signal dataset under the
  current degradation design.

## 2026-05-15 final MELD semvis text-stress diagnostic

Decision source:

```text
decisions/2026-05-15-exp001-final-meld-diagnostic-iteration.md
```

Implemented diagnostic change:

```text
video_source=semvis_clip
audio_source=official_concat
degradation_profile=text_stress
```

The `text_stress` profile preserves the existing 7-template registry, MELD
splits, policies, seeds, primary metric, and feature-level boundary. It adds
text suppression to all degraded slices so the final MELD diagnostic can test
whether the prior failures were mainly caused by text dominance. It is a
diagnostic stress run, not a replacement default corruption profile.

Remote run:

```text
host: ntu-gpu43
commit: 40ef3b8
tmux: exp001_textstress_0515
launcher: experiments/exp-001-decision-surface-pilot/run_semvis_text_stress_gpu43.sh
producer: outputs/meld-producer-semvis-text-stress
analysis: outputs/meld-analysis-semvis-text-stress
log: logs/semvis-text-stress-20260515-090459.log
```

Producer output:

```text
records={'train': 9989, 'validation': 1109, 'test': 2610}
feature_sources={
  'text': '.../text_glove_average_emotion.pkl',
  'audio': '.../audio_embeddings_feature_selection_emotion.pkl+.../audio_emotion.pkl',
  'video': 'semvis_clip:openai/clip-vit-base-patch32:f8:.../MELD.Raw'
}
```

Generated measured tables:

```text
cost_table.csv: present
outcome_table.csv: present
q_policy_map.csv: present
q_proxy_table.csv: present
q_diagnostics.csv: present
corruption_manifest.csv: present
```

Analysis output:

```text
protocol_passed=True
benchmark_signal_passed=True
joint_policy_passed=True
best_single_axis_oracle_regret_dt=0.350
best_single_axis_policy=reliability_only
feasible_oracle_degraded_tight_macro_f1=13.862
best_single_axis_degraded_tight_macro_f1=13.512
joint_degraded_tight_macro_f1=13.833
joint_gap_closure=0.916
pooled_standard_error=0.0208
kendall_tau_b_clean_loose_vs_degraded_tight=-0.048
rank_inversion_index=0.524
```

Budget gate:

```text
p95 spread=2.860
tight=18.346 ms
loose=25.233 ms
tight legal templates=T|A|V|TV
loose legal templates=T|A|V|TA|TV|AV|TAV
TAV-vs-unimodal p95 ratio=1.306
warnings=[]
```

Gate checks:

```text
budget_validity_gate=True
reliability_proxy_boundary_check=True
q_only_task_classifier=True
q_shuffle_control=True
class_stratified_corruption_check=True
post_mask_budget_legality_contract=True
```

Policy summary highlights:

```text
degraded_tight feasible_oracle=13.862
degraded_tight joint=13.833
degraded_tight reliability_only=13.512
degraded_tight budget_only=12.401
degraded_tight random_legal=11.397
degraded_tight clean_best=9.282
degraded_tight static_full=9.282
reliability_only degraded_tight pre_mask_illegal_proposal_rate=0.250
post_mask_budget_violation_rate=0 for executed policies
```

Template means on test:

```text
clean_loose:
  T=34.708
  TV=28.954
  TAV=21.869
  TA=18.635
  V=16.758
  AV=16.250
  A=11.979

degraded_tight:
  V=13.158
  TV=12.401
  TA=11.679
  AV=11.287
  TAV=11.131
  A=10.746
  T=9.282
```

Degraded-tight slice means:

```text
degraded_text:
  V=16.758, TAV=16.650, AV=16.250, TV=15.474, TA=13.427, A=11.979, T=9.282
degraded_audio:
  V=16.758, TV=15.474, T=9.282, A=9.282, TA=9.282, AV=9.282, TAV=9.282
degraded_video:
  TA=13.427, A=11.979, AV=9.986, TAV=9.312, T=9.282, V=9.282, TV=9.282
mixed_degraded:
  TA=10.580, V=9.835, A=9.743, AV=9.628, TV=9.373, T=9.282, TAV=9.280
```

Runtime notes:

- The producer completed, then the launcher failed only at analysis invocation
  because the script used `--output-dir` instead of the runner's `--output`.
  Analysis was rerun manually with the correct flag and completed successfully.
  The launcher has been patched to use `--output`.
- The sklearn logistic heads again emitted convergence warnings.

Interpretation:

- This final MELD diagnostic does break text dominance: `T` falls from first in
  clean-loose to last in degraded-tight, Kendall tau-b becomes `-0.048`, and the
  rank inversion index rises to `0.524`.
- It does not produce a meaningful primary utility gap: feasible oracle is only
  `0.350` macro-F1 above the best single-axis policy.
- Therefore this run should be read as secondary-rank-signal positive but
  primary-regret negative. It confirms that the previous negative results were
  strongly tied to text dominance and degradation strength, but it still should
  not be overclaimed as the main paper-level utility-gap evidence.
