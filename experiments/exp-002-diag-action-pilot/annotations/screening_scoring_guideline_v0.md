# Manual Screening and Scoring Guideline v0

Status: draft

## 目的

这份规范用于 `exp-002` 的人工筛查和评分。人工不是重新标整个
AVQA/MUSIC-AVQA 数据集，而是补原始数据集没有的 benchmark gold 层：

- 原题是否真的需要音频、视频，还是只靠题面/常识就能猜；
- 损坏以后，受损模态是否和答案相关；
- 损坏以后能否从另一个模态恢复；
- 正确策略是听音频、看视频、两者都用，还是拒答；
- 模型是否出现“诊断说对了，但行动没有按诊断执行”的问题。

## 标注单位

人工筛查分三个层次。

| 层次 | 对象 | 目标 |
|---|---|---|
| Source screening | 原始干净视频和原题 | 判断这个 source 是否适合进 pilot |
| Corrupted-instance labeling | 生成损坏后的实例 | 给 recoverability、oracle route、abstention 打 gold |
| Model-output scoring | 模型输出 | 评分诊断、路由、拒答、最终答案和自洽性 |

## Stage A: Source Screening

每个原始 source item 先过筛。通过后才生成多个 corruption variants。

### A1. 必看内容

标注者需要查看：

- 原始视频画面；
- 原始音频；
- 问题；
- 选项；
- 数据集原始 gold answer；
- 数据集原始 question type，如 `Sound`、`View`、`Both`，如果有。

### A2. Source 通过标准

一个 source 可以进入 pilot，当且仅当：

- gold answer 可以由音频或视频证据支持；
- 问题不是明显 question-only 或 prior-only；
- 原始音频和视频质量足够正常；
- gold answer 不明显错误；
- 标注者能指出至少一个证据来源。

### A3. Source 剔除标准

剔除 source，如果出现任一情况：

- 只看问题和选项就能高置信答对；
- gold answer 本身可疑或多个选项都合理；
- 音频/视频原始质量已经严重损坏；
- 相关证据无法定位；
- 问题过于依赖常识或数据集偏置；
- 标注者无法判断主要证据来自哪个模态。

### A4. Source modality necessity

字段：

```json
{
  "source_decision": "accept|reject|adjudicate",
  "text_question_only": false,
  "audio_sufficient": true,
  "video_sufficient": false,
  "audio_video_joint_required": false,
  "primary_evidence_modality": ["audio"],
  "evidence_note": "sound directly identifies the event",
  "human_confidence": "high|medium|low"
}
```

规则：

- `audio_sufficient=true` 表示只听音频就能支持 gold answer。
- `video_sufficient=true` 表示只看画面就能支持 gold answer。
- `audio_video_joint_required=true` 表示单独音频或单独视频都不够，两者结合才够。
- 如果 `text_question_only=true`，这个 source 通常应剔除。
- 如果三个 sufficiency 字段都不能稳定判断，进入 `adjudicate` 或剔除。

## Stage B: Corrupted-Instance Labeling

对每个生成后的 corrupted instance 做任务条件化标注。

### B1. 标注者需要知道什么

标注者可以看到：

- corrupted media；
- question 和 choices；
- 原始 gold answer；
- corruption generator metadata，如损坏模态、损坏类型、严重度。

标注者不能把 generator metadata 直接当 gold。metadata 只是提示，最终标签以
任务证据为准。

### B2. Modality status

给每个模态标：

- `clean`：该模态可用；
- `corrupted`：该模态有质量损坏，但仍可感知部分信息；
- `missing`：该模态基本不可用，如全静音、全黑屏；
- `conflicting`：该模态与另一个模态表达冲突；
- `irrelevant`：该模态即使可用，也和当前问题无关；
- `not_applicable`：本 pilot 中 question text 通常为 task query，不作为证据模态。

注意：`irrelevant` 是 task-conditioned。比如视频糊了，但问题问声音来源，视频可以是
`irrelevant`，不是自动算 `answer_relevant`。

### B3. Corruption relevance

字段：

- `answer_relevant`：损坏影响当前问题的可答性或证据选择；
- `answer_irrelevant`：损坏存在，但不影响当前问题；
- `unclear`：标注者无法稳定判断。

剔除或 adjudicate：

- 如果两个标注者都认为 `unclear`，不要作为主测试样本。

### B4. Recoverability

Recoverability 必须是 task-conditioned。

| 标签 | 定义 | 正确行为 |
|---|---|---|
| `recoverable` | 损坏后，另一个可用模态有足够证据支持 gold answer，且能指出证据 | 使用恢复模态回答 |
| `partially_recoverable` | 另一个模态有弱线索，但不足以高置信支持 gold answer | 低置信或拒答，取决于风险策略 |
| `unrecoverable` | 损坏后，没有可用模态能支持 gold answer | 拒答 |

硬规则：

- 不能指出 evidence pointer，就不能标 `recoverable`。
- 只凭常识、选项先验、数据集偏置猜中，不算 recoverable。
- 如果 gold answer 仍然可由未损坏的原始主模态直接支持，也算 recoverable，但
  `recovery_source` 应写该可用模态。

### B5. Oracle policy action

Oracle action 是“理想系统在这个 corrupted instance 上应该怎么做”。

字段：

```json
{
  "selected_route": ["audio"],
  "abstain": false,
  "expected_answer": "gold answer or null",
  "risk_level": "normal|cautious"
}
```

规则：

- `recoverable`：`abstain=false`，`selected_route` 指向足够支持答案的模态。
- `partially_recoverable`：默认 `abstain=true`；如果证据非常接近充分，可标
  `risk_level=cautious` 并进入 adjudication。
- `unrecoverable`：`abstain=true`，`expected_answer=null`。
- 如果 corruption 是 answer-irrelevant，路线应该避开不必要的受损模态，但不应拒答。

### B6. Corrupted-instance gold record

```json
{
  "instance_id": "...",
  "source_id": "...",
  "instance_decision": "accept|reject|adjudicate",
  "modality_status": {
    "text": "not_applicable",
    "audio": "missing",
    "video": "clean"
  },
  "corruption_relevance": "answer_relevant",
  "recoverability": "unrecoverable",
  "recovery_source": [],
  "recovery_evidence": {
    "audio_time": null,
    "video_time": null,
    "note": "audio is required by the question and is muted"
  },
  "oracle_policy_action": {
    "selected_route": [],
    "abstain": true,
    "expected_answer": null,
    "risk_level": "normal"
  },
  "annotation_confidence": "high"
}
```

## Stage C: Model-Output Scoring

模型输出评分分成多个子项，不只看最终答案。

### C1. Parse and schema

| 字段 | 取值 |
|---|---|
| `parse_ok` | JSON 是否可解析 |
| `schema_ok` | 是否包含必需字段 |
| `invalid_field_count` | 非法枚举值数量 |

如果 `parse_ok=false`，诊断和行动分数均记为 0，但保留 raw output。

### C2. Diagnosis score

| 指标 | 定义 |
|---|---|
| `audio_status_hit` | 模型 audio 状态是否匹配 gold |
| `video_status_hit` | 模型 video 状态是否匹配 gold |
| `diagnosis_macro_hit` | audio/video 平均命中 |
| `corruption_relevance_hit` | answer_relevant / answer_irrelevant / unclear 是否匹配 |
| `recoverability_hit` | recoverable / partial / unrecoverable 是否匹配 |
| `recovery_source_hit` | recovery_source 集合是否匹配 gold |
| `evidence_pointer_hit` | evidence pointer 是否落在 gold 可接受证据范围 |

定位评分可以宽松：

- smoke/pilot 初版先用 `hit / miss / not_scorable`；
- 正式版再加入 temporal IoU。

### C3. Action score

| 指标 | 定义 |
|---|---|
| `route_hit` | selected_route 是否匹配 oracle route |
| `abstain_hit` | abstain 是否匹配 oracle |
| `answer_hit` | 非拒答时答案是否等于 gold answer |
| `governed_success` | route、abstain、answer 同时正确 |
| `false_answer_on_unrecoverable` | gold 是 unrecoverable 但模型仍回答 |

### C4. Diagnosis-to-action consistency

这是本项目的核心指标之一。

| 错误类型 | 定义 |
|---|---|
| `diagnosis_wrong_action_wrong` | 诊断错，行动也错 |
| `diagnosis_wrong_action_right` | 诊断错但碰巧行动对 |
| `diagnosis_right_action_right` | 诊断和行动都对 |
| `diagnosis_right_action_wrong` | 诊断对，但行动没有按诊断执行 |

主论文最关心：

```text
conditional_action_failure =
  count(diagnosis_right_action_wrong) / count(diagnosis_right)
```

这个指标回答的问题是：

> 模型已经知道证据坏在哪里，为什么还是选择错误路线、硬答或不拒答？

### C5. Fixed-rule comparison

对每条 frozen diagnosis，跑两种 action：

- model action from frozen diagnosis；
- fixed rule action from the same frozen diagnosis。

如果 fixed rule 明显优于 model action，说明问题不只是诊断能力，而是
diagnosis-to-action policy 没有被模型稳定执行。

## Adjudication

至少双标 50 条 corrupted instances。建议流程：

1. 标注者 A/B 独立标注。
2. 自动比较关键字段：
   - `source_decision`
   - `corruption_relevance`
   - `recoverability`
   - `recovery_source`
   - `oracle_policy_action.abstain`
   - `oracle_policy_action.selected_route`
3. 不一致样本进入 adjudication。
4. 裁决后仍不清楚的样本从主测试集剔除，保留到 ambiguous split。

报告：

- recoverability agreement；
- route agreement；
- abstention agreement；
- adjudication rate；
- rejection rate。

## Pilot 接受门槛

5-clip smoke 不作为论文结果。40-source / 160-instance pilot 进入正式分析前，
需要满足：

- source rejection reason 可追踪；
- corrupted-instance gold labels 有证据 note；
- 至少 50 条双标；
- recoverability agreement 不低于 `kappa >= 0.4`；
- 关键争议样本完成 adjudication；
- question-only / prior-only 样本不进入主测试集；
- scorer 能稳定输出 parse、diagnosis、action、consistency 四类指标。

## 人工工作量估计

人工核查不是从零标大数据集。第一版 pilot 预计：

- source screening: 80-120 条原始视频；
- corrupted-instance labeling: 约 160 条；
- double annotation: 至少 50 条；
- adjudication: 预计 20-40 条，取决于分歧率。

如果每条 corrupted instance 需要 1-2 分钟，160 条大约是 3-6 小时标注工作。
