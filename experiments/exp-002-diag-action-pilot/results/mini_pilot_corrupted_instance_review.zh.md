# Mini-Pilot 40 条 Corrupted Instance 正式审核草案

日期：2026-06-18

状态：进入 corrupted-instance 正式审核阶段。此文件是审核草案，不是最终 scorer gold。

## 当前结论

10 个 clean source 的模态标签已经冻结。现在要审核的是 40 条污染样本：污染后是否可答、是否可恢复、应选什么路线、是否拒答、是否进入主测评。

## 审核状态统计

| 状态 | 中文解释 | 数量 |
|---|---|---:|
| `exclude_from_main` | 不进入主测评 | 6 |
| `headline_candidate_after_review` | 主测评候选，人工确认后可进入 gold | 17 |
| `needs_adjudication_oracle_route` | oracle 路线不完整，需要修正 | 3 |
| `needs_adjudication_partial` | 部分可答/部分可恢复，需要裁决 | 13 |
| `needs_adjudication_unclear` | 存在 unclear 字段，需要裁决 | 1 |

解释：

- `headline_candidate_after_review`：字段看起来可以进主测评，但仍需要人工复看媒体和路线，确认后才能设为 `instance_decision=accept`。
- `needs_adjudication_partial`：存在 `partially_answerable` 或 `partially_recoverable`，需要裁决，不建议直接进主表。
- `needs_adjudication_unclear`：存在 `unclear` 字段，必须裁决。
- `needs_adjudication_oracle_route`：可答但 oracle route 为空或不完整，必须修路线。
- `exclude_from_main`：不进入主测评，可保留作定性分析。

## 按 Source 汇总

| source_id | source 标签 | headline 候选 | partial/unclear/route 裁决 | exclude |
|---|---|---:|---:|---:|
| `src_001` | `audio_only` | 1 | 3 | 0 |
| `src_002` | `audio_only` | 2 | 2 | 0 |
| `src_003` | `video_only` | 3 | 1 | 0 |
| `src_004` | `video_only` | 4 | 0 | 0 |
| `src_005` | `audio_video_joint` | 0 | 2 | 2 |
| `src_006` | `audio_video_joint` | 1 | 1 | 2 |
| `src_007` | `video_only_control` | 1 | 2 | 1 |
| `src_008` | `video_only_control` | 2 | 2 | 0 |
| `src_009` | `audio_video_joint_conflict_candidate` | 1 | 3 | 0 |
| `src_010` | `audio_video_joint_conflict_candidate` | 2 | 1 | 1 |

## 40 条逐行审核表

| instance_id | source 标签 | 污染 | 主状态 | 可答性 | 可恢复性 | oracle 路线 | 审核状态 | 建议处理 |
|---|---|---|---|---|---|---|---|---|
| `src_001__视频轻度遮挡` | `audio_only` | video:video_occlusion:mild | answerable | partially_answerable | partially_recoverable | `audio` | `needs_adjudication_partial` | adjudicate |
| `src_001__视频重度模糊` | `audio_only` | video:video_blur:severe | answerable | partially_answerable | recoverable | `audio` | `needs_adjudication_unclear` | adjudicate |
| `src_001__音频轻度加噪` | `audio_only` | audio:audio_noise:mild | answerable | answerable | partially_recoverable | `audio` | `needs_adjudication_partial` | adjudicate |
| `src_001__音频静音` | `audio_only` | audio:audio_mute:severe | unanswerable | unanswerable | unrecoverable | `` | `headline_candidate_after_review` | accept_after_review |
| `src_002__视频轻度遮挡` | `audio_only` | video:video_occlusion:mild | answerable | answerable | recoverable | `audio` | `headline_candidate_after_review` | accept_after_review |
| `src_002__视频重度遮挡` | `audio_only` | video:video_occlusion:severe | answerable | partially_answerable | partially_recoverable | `audio` | `needs_adjudication_partial` | adjudicate |
| `src_002__音频轻度加噪` | `audio_only` | audio:audio_noise:mild | answerable | answerable | recoverable | `video` | `headline_candidate_after_review` | accept_after_review |
| `src_002__音频重度加噪` | `audio_only` | audio:audio_noise:severe | answerable | answerable | partially_recoverable | `video` | `needs_adjudication_partial` | adjudicate |
| `src_003__视频重度模糊` | `video_only` | video:video_blur:severe | answerable | answerable | partially_recoverable | `audio` | `needs_adjudication_partial` | adjudicate |
| `src_003__视频重度遮挡` | `video_only` | video:video_occlusion:severe | answerable | answerable | unrecoverable | `audio` | `headline_candidate_after_review` | accept_after_review |
| `src_003__音频轻度加噪` | `video_only` | audio:audio_noise:mild | answerable | answerable | recoverable | `video` | `headline_candidate_after_review` | accept_after_review |
| `src_003__音频重度加噪` | `video_only` | audio:audio_noise:severe | answerable | answerable | unrecoverable | `video` | `headline_candidate_after_review` | accept_after_review |
| `src_004__视频轻度模糊` | `video_only` | video:video_blur:mild | answerable | answerable | not_needed | `video` | `headline_candidate_after_review` | accept_after_review |
| `src_004__视频重度遮挡` | `video_only` | video:video_occlusion:severe | answerable | answerable | unrecoverable | `video` | `headline_candidate_after_review` | accept_after_review |
| `src_004__音频重度加噪` | `video_only` | audio:audio_noise:severe | answerable | answerable | not_needed | `video` | `headline_candidate_after_review` | accept_after_review |
| `src_004__音频静音` | `video_only` | audio:audio_mute:severe | answerable | answerable | unrecoverable | `video` | `headline_candidate_after_review` | accept_after_review |
| `src_005__视频轻度模糊` | `audio_video_joint` | video:video_blur:mild | answerable | answerable | recoverable | `` | `needs_adjudication_oracle_route` | adjudicate |
| `src_005__视频重度遮挡` | `audio_video_joint` | video:video_occlusion:severe | exclude_from_main | unanswerable | unrecoverable | `` | `exclude_from_main` | reject |
| `src_005__音频轻度加噪` | `audio_video_joint` | audio:audio_noise:mild | answerable | answerable | partially_recoverable | `` | `needs_adjudication_oracle_route` | adjudicate |
| `src_005__音频重度加噪` | `audio_video_joint` | audio:audio_noise:severe | exclude_from_main | partially_answerable | unrecoverable | `` | `exclude_from_main` | reject |
| `src_006__视频轻度模糊` | `audio_video_joint` | video:video_blur:mild | exclude_from_main | unclear | unclear | `` | `exclude_from_main` | reject |
| `src_006__视频重度遮挡` | `audio_video_joint` | video:video_occlusion:severe | unanswerable | unanswerable | unrecoverable | `` | `headline_candidate_after_review` | accept_after_review |
| `src_006__音频重度加噪` | `audio_video_joint` | audio:audio_noise:severe | answerable | partially_answerable | partially_recoverable | `` | `needs_adjudication_oracle_route` | adjudicate |
| `src_006__音频静音` | `audio_video_joint` | audio:audio_mute:severe | exclude_from_main | unanswerable | unrecoverable | `` | `exclude_from_main` | reject |
| `src_007__视频轻度遮挡` | `video_only_control` | video:video_occlusion:mild | answerable | partially_answerable | unrecoverable | `video` | `needs_adjudication_partial` | adjudicate |
| `src_007__视频重度模糊` | `video_only_control` | video:video_blur:severe | exclude_from_main | unanswerable | unrecoverable | `` | `exclude_from_main` | reject |
| `src_007__音频重度加噪` | `video_only_control` | audio:audio_noise:severe | answerable | answerable | partially_recoverable | `video` | `needs_adjudication_partial` | adjudicate |
| `src_007__音频静音` | `video_only_control` | audio:audio_mute:severe | answerable | answerable | unrecoverable | `video` | `headline_candidate_after_review` | accept_after_review |
| `src_008__视频轻度模糊` | `video_only_control` | video:video_blur:mild | answerable | answerable | partially_recoverable | `video` | `needs_adjudication_partial` | adjudicate |
| `src_008__视频轻度遮挡` | `video_only_control` | video:video_occlusion:mild | answerable | answerable | unrecoverable | `video` | `headline_candidate_after_review` | accept_after_review |
| `src_008__音频轻度加噪` | `video_only_control` | audio:audio_noise:mild | answerable | answerable | partially_recoverable | `video` | `needs_adjudication_partial` | adjudicate |
| `src_008__音频重度加噪` | `video_only_control` | audio:audio_noise:severe | answerable | answerable | unrecoverable | `video` | `headline_candidate_after_review` | accept_after_review |
| `src_009__视频轻度模糊` | `audio_video_joint_conflict_candidate` | video:video_blur:mild | answerable | answerable | partially_recoverable | `video` | `needs_adjudication_partial` | adjudicate |
| `src_009__视频重度模糊` | `audio_video_joint_conflict_candidate` | video:video_blur:severe | unanswerable | unanswerable | unrecoverable | `` | `headline_candidate_after_review` | accept_after_review |
| `src_009__音频轻度加噪` | `audio_video_joint_conflict_candidate` | audio:audio_noise:mild | answerable | answerable | partially_recoverable | `video` | `needs_adjudication_partial` | adjudicate |
| `src_009__音频重度加噪` | `audio_video_joint_conflict_candidate` | audio:audio_noise:severe | answerable | partially_answerable | partially_recoverable | `video` | `needs_adjudication_partial` | adjudicate |
| `src_010__视频轻度模糊` | `audio_video_joint_conflict_candidate` | video:video_blur:mild | answerable | answerable | recoverable | `audio` | `headline_candidate_after_review` | accept_after_review |
| `src_010__视频重度遮挡` | `audio_video_joint_conflict_candidate` | video:video_occlusion:severe | answerable | answerable | unrecoverable | `audio` | `headline_candidate_after_review` | accept_after_review |
| `src_010__音频轻度加噪` | `audio_video_joint_conflict_candidate` | audio:audio_noise:mild | answerable | answerable | partially_recoverable | `audio` | `needs_adjudication_partial` | adjudicate |
| `src_010__音频静音` | `audio_video_joint_conflict_candidate` | audio:audio_mute:severe | exclude_from_main | unanswerable | unrecoverable | `` | `exclude_from_main` | reject |

## 需要优先人工看的样本

### oracle 路线不完整，需要修正

- `src_005__视频轻度模糊`：Is the first sound coming from the right instrument? / gold=yes / issues=answerable_non_abstain_empty_preferred_route / 建议：需要负责人裁决；若不能明确升级为 answerable/unanswerable 且路线清楚，则不进入主测评。
- `src_005__音频轻度加噪`：Is the first sound coming from the right instrument? / gold=yes / issues=answerable_non_abstain_empty_preferred_route / 建议：需要负责人裁决；若不能明确升级为 answerable/unanswerable 且路线清楚，则不进入主测评。
- `src_006__音频重度加噪`：How many instruments in the video did not sound from beginning to end? / gold=one / issues=answerable_non_abstain_empty_preferred_route / 建议：需要负责人裁决；若不能明确升级为 answerable/unanswerable 且路线清楚，则不进入主测评。

### 存在 unclear 字段，需要裁决

- `src_001__视频重度模糊`：What are the people doing in the video? / gold=Practice oral skills / issues=unclear_field / 建议：需要负责人裁决；若不能明确升级为 answerable/unanswerable 且路线清楚，则不进入主测评。

### 部分可答/部分可恢复，需要裁决

- `src_001__视频轻度遮挡`：What are the people doing in the video? / gold=Practice oral skills / issues=partial_answerability_or_recoverability / 建议：需要负责人裁决；若不能明确升级为 answerable/unanswerable 且路线清楚，则不进入主测评。
- `src_001__音频轻度加噪`：What are the people doing in the video? / gold=Practice oral skills / issues=partial_answerability_or_recoverability / 建议：需要负责人裁决；若不能明确升级为 answerable/unanswerable 且路线清楚，则不进入主测评。
- `src_002__视频重度遮挡`：What is the source of the sound in the video? / gold=police car / issues=partial_answerability_or_recoverability / 建议：需要负责人裁决；若不能明确升级为 answerable/unanswerable 且路线清楚，则不进入主测评。
- `src_002__音频重度加噪`：What is the source of the sound in the video? / gold=police car / issues=partial_answerability_or_recoverability / 建议：需要负责人裁决；若不能明确升级为 answerable/unanswerable 且路线清楚，则不进入主测评。
- `src_003__视频重度模糊`：What is the source of the sound in the video? / gold=Birdsong / issues=partial_answerability_or_recoverability / 建议：需要负责人裁决；若不能明确升级为 answerable/unanswerable 且路线清楚，则不进入主测评。
- `src_007__视频轻度遮挡`：What animal appears in the video? / gold=fish / issues=partial_answerability_or_recoverability / 建议：需要负责人裁决；若不能明确升级为 answerable/unanswerable 且路线清楚，则不进入主测评。
- `src_007__音频重度加噪`：What animal appears in the video? / gold=fish / issues=partial_answerability_or_recoverability / 建议：需要负责人裁决；若不能明确升级为 answerable/unanswerable 且路线清楚，则不进入主测评。
- `src_008__视频轻度模糊`：What numbers appear in the video? / gold=twenty-seven / issues=partial_answerability_or_recoverability / 建议：需要负责人裁决；若不能明确升级为 answerable/unanswerable 且路线清楚，则不进入主测评。
- `src_008__音频轻度加噪`：What numbers appear in the video? / gold=twenty-seven / issues=partial_answerability_or_recoverability / 建议：需要负责人裁决；若不能明确升级为 answerable/unanswerable 且路线清楚，则不进入主测评。
- `src_009__视频轻度模糊`：What is the source of the sound in the video? / gold=a car / issues=partial_answerability_or_recoverability / 建议：需要负责人裁决；若不能明确升级为 answerable/unanswerable 且路线清楚，则不进入主测评。
- `src_009__音频轻度加噪`：What is the source of the sound in the video? / gold=a car / issues=partial_answerability_or_recoverability / 建议：需要负责人裁决；若不能明确升级为 answerable/unanswerable 且路线清楚，则不进入主测评。
- `src_009__音频重度加噪`：What is the source of the sound in the video? / gold=a car / issues=partial_answerability_or_recoverability / 建议：需要负责人裁决；若不能明确升级为 answerable/unanswerable 且路线清楚，则不进入主测评。
- `src_010__音频轻度加噪`：What are the people doing in the video? / gold=Performing oral skills / issues=partial_answerability_or_recoverability / 建议：需要负责人裁决；若不能明确升级为 answerable/unanswerable 且路线清楚，则不进入主测评。

### 不进入主测评

- `src_005__视频重度遮挡`：Is the first sound coming from the right instrument? / gold=yes / issues=exclude_from_main / 建议：保留作定性分析或丢弃；正式 gold 中设 instance_decision=reject。
- `src_005__音频重度加噪`：Is the first sound coming from the right instrument? / gold=yes / issues=exclude_from_main / 建议：保留作定性分析或丢弃；正式 gold 中设 instance_decision=reject。
- `src_006__视频轻度模糊`：How many instruments in the video did not sound from beginning to end? / gold=one / issues=exclude_from_main / 建议：保留作定性分析或丢弃；正式 gold 中设 instance_decision=reject。
- `src_006__音频静音`：How many instruments in the video did not sound from beginning to end? / gold=one / issues=exclude_from_main / 建议：保留作定性分析或丢弃；正式 gold 中设 instance_decision=reject。
- `src_007__视频重度模糊`：What animal appears in the video? / gold=fish / issues=exclude_from_main / 建议：保留作定性分析或丢弃；正式 gold 中设 instance_decision=reject。
- `src_010__音频静音`：What are the people doing in the video? / gold=Performing oral skills / issues=exclude_from_main / 建议：保留作定性分析或丢弃；正式 gold 中设 instance_decision=reject。

## 下一步

1. 先复核 `needs_adjudication_oracle_route` 和 `needs_adjudication_unclear`。
2. 再处理 `needs_adjudication_partial`：能明确升级为 answerable/unanswerable 的才进入主测评，否则保留为定性分析。
3. 对 `headline_candidate_after_review` 逐条快速复看媒体和路线；确认后设置 `review_status=reviewed`、`risk_sensitive=false`、`instance_decision=accept`。
4. 对 `exclude_from_main` 设置 `instance_decision=reject` 或保留在单独分析表中。
5. 完成后生成 `mini_pilot.gold.jsonl`，再跑模型 diagnosis/action/scorer。
