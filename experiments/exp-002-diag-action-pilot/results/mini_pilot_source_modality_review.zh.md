# Mini-Pilot Source 模态类型审核表（中文版）

日期：2026-06-18

状态：负责人已同意最终建议标签，source-level 模态标签已冻结。

注意：这里冻结的是 10 个 clean source 的模态类型，不代表 40 条 corrupted instance 已经成为 scorer gold。

## 已冻结标签统计

| 最终标签 | 中文含义 | 数量 |
|---|---|---:|
| `audio_only` | 只需要音频 | 2 |
| `audio_video_joint` | 需要音频+视频共同判断 | 2 |
| `audio_video_joint_conflict_candidate` | 音频+视频联合/冲突候选 | 2 |
| `video_only` | 只需要视频 | 2 |
| `video_only_control` | 视频主导的无关污染对照 | 2 |

## 10 个 Source 的冻结结论

| source_id | 原候选桶 | 冻结后的最终标签 | 中文解释 | 主要证据 | 是否需要音频+视频 | 状态 |
|---|---|---|---|---|---|---|
| `src_001` | `audio_necessary` | `audio_only` | 只需要音频 | audio | 否 | 已冻结 |
| `src_002` | `audio_necessary` | `audio_only` | 只需要音频 | audio | 否 | 已冻结 |
| `src_003` | `video_necessary` | `video_only` | 只需要视频 | video | 否 | 已冻结 |
| `src_004` | `video_necessary` | `video_only` | 只需要视频 | video | 否 | 已冻结 |
| `src_005` | `audio_video_joint` | `audio_video_joint` | 需要音频+视频共同判断 | audio+video | 是 | 已冻结 |
| `src_006` | `audio_video_joint` | `audio_video_joint` | 需要音频+视频共同判断 | audio+video | 是 | 已冻结 |
| `src_007` | `corrupted_irrelevant_control` | `video_only_control` | 视频主导的无关污染对照 | video | 否 | 已冻结 |
| `src_008` | `corrupted_irrelevant_control` | `video_only_control` | 视频主导的无关污染对照 | video | 否 | 已冻结 |
| `src_009` | `cross_modal_conflict` | `audio_video_joint_conflict_candidate` | 音频+视频联合/冲突候选 | audio+video | 是 | 已冻结 |
| `src_010` | `cross_modal_conflict` | `audio_video_joint_conflict_candidate` | 音频+视频联合/冲突候选 | audio+video | 是 | 已冻结 |

## 逐条结论

### src_001：只需要音频

- 数据集：`AVQA_HF_sample`
- 原候选桶：`audio_necessary`
- 问题：What are the people doing in the video?
- 标准答案：Practice oral skills
- 冻结标签：`audio_only`（只需要音频）
- 主要证据模态：`audio`
- 音频单独是否足够：`true`
- 视频单独是否足够：`false`
- 是否需要音频+视频共同判断：`false`
- 状态：已由负责人确认并冻结。

### src_002：只需要音频

- 数据集：`AVQA_HF_sample`
- 原候选桶：`audio_necessary`
- 问题：What is the source of the sound in the video?
- 标准答案：police car
- 冻结标签：`audio_only`（只需要音频）
- 主要证据模态：`audio`
- 音频单独是否足够：`true`
- 视频单独是否足够：`false`
- 是否需要音频+视频共同判断：`false`
- 状态：已由负责人确认并冻结。

### src_003：只需要视频

- 数据集：`AVQA_HF_sample`
- 原候选桶：`video_necessary`
- 问题：What is the source of the sound in the video?
- 标准答案：Birdsong
- 冻结标签：`video_only`（只需要视频）
- 主要证据模态：`video`
- 音频单独是否足够：`false`
- 视频单独是否足够：`true`
- 是否需要音频+视频共同判断：`false`
- 状态：已由负责人确认并冻结。

### src_004：只需要视频

- 数据集：`AVQA_HF_sample`
- 原候选桶：`video_necessary`
- 问题：What are the people doing in the video?
- 标准答案：Bowling
- 冻结标签：`video_only`（只需要视频）
- 主要证据模态：`video`
- 音频单独是否足够：`false`
- 视频单独是否足够：`true`
- 是否需要音频+视频共同判断：`false`
- 状态：已由负责人确认并冻结。

### src_005：需要音频+视频共同判断

- 数据集：`MUSIC-AVQA`
- 原候选桶：`audio_video_joint`
- 问题：Is the first sound coming from the right instrument?
- 标准答案：yes
- 冻结标签：`audio_video_joint`（需要音频+视频共同判断）
- 主要证据模态：`audio+video`
- 音频单独是否足够：`false`
- 视频单独是否足够：`false`
- 是否需要音频+视频共同判断：`true`
- 状态：已由负责人确认并冻结。

### src_006：需要音频+视频共同判断

- 数据集：`MUSIC-AVQA`
- 原候选桶：`audio_video_joint`
- 问题：How many instruments in the video did not sound from beginning to end?
- 标准答案：one
- 冻结标签：`audio_video_joint`（需要音频+视频共同判断）
- 主要证据模态：`audio+video`
- 音频单独是否足够：`false`
- 视频单独是否足够：`false`
- 是否需要音频+视频共同判断：`true`
- 状态：已由负责人确认并冻结。

### src_007：视频主导的无关污染对照

- 数据集：`AVQA_HF_sample`
- 原候选桶：`corrupted_irrelevant_control`
- 问题：What animal appears in the video?
- 标准答案：fish
- 冻结标签：`video_only_control`（视频主导的无关污染对照）
- 主要证据模态：`video`
- 音频单独是否足够：`false`
- 视频单独是否足够：`true`
- 是否需要音频+视频共同判断：`false`
- 状态：已由负责人确认并冻结。

### src_008：视频主导的无关污染对照

- 数据集：`AVQA_HF_sample`
- 原候选桶：`corrupted_irrelevant_control`
- 问题：What numbers appear in the video?
- 标准答案：twenty-seven
- 冻结标签：`video_only_control`（视频主导的无关污染对照）
- 主要证据模态：`video`
- 音频单独是否足够：`false`
- 视频单独是否足够：`true`
- 是否需要音频+视频共同判断：`false`
- 状态：已由负责人确认并冻结。

### src_009：音频+视频联合/冲突候选

- 数据集：`AVQA_HF_sample`
- 原候选桶：`cross_modal_conflict`
- 问题：What is the source of the sound in the video?
- 标准答案：a car
- 冻结标签：`audio_video_joint_conflict_candidate`（音频+视频联合/冲突候选）
- 主要证据模态：`audio+video`
- 音频单独是否足够：`false`
- 视频单独是否足够：`false`
- 是否需要音频+视频共同判断：`true`
- 状态：已由负责人确认并冻结。

### src_010：音频+视频联合/冲突候选

- 数据集：`AVQA_HF_sample`
- 原候选桶：`cross_modal_conflict`
- 问题：What are the people doing in the video?
- 标准答案：Performing oral skills
- 冻结标签：`audio_video_joint_conflict_candidate`（音频+视频联合/冲突候选）
- 主要证据模态：`audio+video`
- 音频单独是否足够：`false`
- 视频单独是否足够：`false`
- 是否需要音频+视频共同判断：`true`
- 状态：已由负责人确认并冻结。

## 下一步

接下来进入 40 条 corrupted instance 的正式审核。每条 corrupted instance 还需要确认污染后是否可答、是否可恢复、应选择哪个路线、是否拒答、是否能进入主测评，以及 `instance_decision`。冻结 source 标签不等于冻结 corrupted-instance gold。
