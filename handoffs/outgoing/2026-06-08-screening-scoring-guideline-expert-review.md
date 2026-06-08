# Handoff: 人工筛查与评分标准专家审阅

> 生成日期：2026-06-08。
> 目的：给外部专家独立审阅，不要求专家访问本地仓库或上下文。

## 0. 我们希望专家回答什么

我们正在准备一个多模态大模型 benchmark / evaluation 方向的论文。今天我们为
pilot 设计了一套 **人工筛查与评分标准**。我们认为这部分不是工程细节，而是整篇
文章的关键贡献之一：如果这个标准不严谨，后续所有模型结果都会站不住。

请专家重点判断：

1. 这套人工筛查与评分标准是否有学术价值，还是过于复杂？
2. `modality_necessity`、`corruption_relevance`、`recoverability`、
   `recovery_source`、`oracle_policy_action` 这些标签是否定义清楚？
3. 我们对 recoverability 的硬规则是否合理：
   **不能指出证据位置，就不能标为 recoverable**。
4. source screening 的剔除标准是否足以排除 question-only、prior-only、
   答案歧义、证据不清的样本？
5. model-output scoring 是否能支撑论文主 claim，尤其是
   diagnosis-to-action consistency？
6. 如果要写成 AAAI 风格的 benchmark paper，人工标注一致性、adjudication、
   质量控制需要做到什么程度？
7. 审稿人最可能质疑这套标准的哪些部分？我们应该如何修改？
8. 在正式扩展到 40 source / 160 corrupted instances 前，这套标准是否可以冻结
   为 v0？

## 1. 项目背景

### 1.1 当前论文故事

我们现在不想把工作写成普通的 missing modality robustness。已有工作已经研究了
模态缺失或模态损坏后模型性能下降的问题。我们现在更窄地关注：

> 多模态大模型也许能诊断出证据哪里坏了，但它不一定能根据这个诊断采取正确行动。

我们把这个现象叫做 **diagnosis-to-action gap**。

典型例子：

- 模型说 audio muted / unusable，但回答时仍然依赖 audio。
- 模型说 video corrupted，但没有切换到可用的 audio evidence。
- 模型说 evidence insufficient，但仍然高置信给答案。
- 模型检测到 audio-video conflict，但既没有仲裁，也没有拒答。

因此，我们的 benchmark 不能只看 final answer accuracy。它必须标注：

- 哪个模态可用；
- 损坏是否与当前问题相关；
- 损坏后是否还能从另一个模态恢复；
- 理想系统应该选哪个 evidence route；
- 什么时候应该 abstain；
- 模型是否出现“诊断正确但行动错误”。

### 1.2 Pilot 范围

第一版 pilot 的范围是：

> textual query 下的 audio-video evidence governance。

这里的 question text 是任务 query，不是可损坏的 text evidence。也就是说，第一版
pilot 不声称完整验证 text-audio-video 三模态证据治理。后续如果加入 transcript /
caption / ASR，才可以扩展为完整 text-audio-video evidence governance。

### 1.3 数据与模型现状

主数据候选：

- AVQA / MUSIC-AVQA 风格的 audio-video QA 数据。

理由：

- 有 raw audio-video 和自然语言问题；
- 比 MELD / MOSEI 这类情感数据更不容易被 text dominance 掩盖；
- 更自然地产生 audio-necessary、video-necessary、audio-video complementary、
  conflict / temporal mismatch 等样本。

当前 feasibility：

- AVQA 风格 metadata 和一小批 sample videos 已经能在服务器上 staged。
- 5 个 source clips 做了 smoke。
- 5 个 corrupted media instances 保留了 audio/video streams。
- 两个 Qwen-family 音视频模型完成 5-clip smoke：
  `qwen3.5-omni-plus` 和 `qwen3-omni-flash`。
- `qwen3.7-plus` 可作为 video/text control，但本次没有确认它消耗 audio tokens，
  所以不计入 same-instance audio-video model。

注意：这些只是 access / format smoke，不是论文结果。

## 2. 为什么原始数据集标签不够

AVQA / MUSIC-AVQA 这类原始数据通常有题目和答案，但没有我们论文需要的
“损坏以后应该怎么办”的标签。

| 标签 / 信息 | 原始数据通常有吗 | 对我们是否足够 |
|---|---:|---:|
| raw audio / video | 有 | 足够 |
| question | 有 | 足够 |
| choices / gold answer | 有 | 足够 |
| Sound / View / Both 粗类型 | 有些有 | 只能作为 hint |
| 我们生成的损坏类型 | 原始没有，但脚本知道 | 机械 metadata，不能直接当 gold |
| 损坏后是否还能答 | 没有 | 需要人工核查 |
| 能否从另一个模态恢复 | 没有 | 需要人工核查 |
| 应该使用哪个模态 route | 没有 | 需要人工核查 |
| 是否应该拒答 | 没有 | 需要人工核查 |
| 模型是否诊断对但行动错 | 没有 | 需要我们评分 |

所以人工工作不是重新标整个数据集，而是补一层 benchmark gold：

> controlled corruption 之后，证据是否仍可用、是否可恢复、应该采取什么行动。

## 3. 标准整体结构

我们把人工筛查与评分分成三层：

| 层次 | 对象 | 目标 |
|---|---|---|
| Source screening | 原始干净视频和原题 | 判断这个 source 是否适合进入 pilot |
| Corrupted-instance labeling | 生成损坏后的实例 | 标注 recoverability、oracle route、abstention |
| Model-output scoring | 模型输出 | 评分诊断、路由、拒答、最终答案和自洽性 |

这个拆分很重要：一个原始 source 在 clean dataset 中可能没问题，但某个 corruption
variant 可能变得 ambiguous。模型也可能诊断对了，但行动仍然错。

## 4. Stage A: Source Screening

### A1. 标注者看到什么

每个 source item 需要查看：

- 原始视频画面；
- 原始音频；
- question；
- choices；
- 原始 gold answer；
- 数据集原始 coarse type，如 `Sound`、`View`、`Both`，如果有。

### A2. Source 通过标准

一个 source 可以进入 pilot，当且仅当：

- gold answer 可以由 audio 或 video evidence 支持；
- 不是明显 question-only / prior-only / common-sense-only；
- 原始 audio/video 质量足够正常；
- gold answer 不明显错误；
- 标注者能指出至少一个证据来源。

### A3. Source 剔除标准

剔除 source，如果出现任一情况：

- 只看 question 和 choices 就能高置信答对；
- gold answer 可疑，或多个选项都合理；
- 原始 audio/video 已经严重损坏；
- 相关证据无法定位；
- 问题过度依赖常识或数据集偏置；
- 标注者无法判断主要证据来自哪个模态。

### A4. Source Modality Necessity Schema

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

解释：

- `audio_sufficient=true`：只听 audio 就能支持 gold answer。
- `video_sufficient=true`：只看 video 就能支持 gold answer。
- `audio_video_joint_required=true`：单独 audio / video 都不够，需要结合。
- `text_question_only=true`：通常应剔除。
- 如果无法稳定判断，进入 `adjudicate` 或剔除。

## 5. Stage B: Corrupted-Instance Labeling

一个 corrupted instance 是：

> source item + 一种 controlled corruption。

例如 audio mute、video blur、audio shift、cross-modal replacement。

### B1. 标注者看到什么

标注者可以看到：

- corrupted media；
- question 和 choices；
- 原始 gold answer；
- corruption generator metadata，如 affected modality、corruption type、
  severity、location。

关键规则：

> generator metadata 只是机械记录，不自动等于 gold。最终标签必须根据当前问题和证据判断。

例子：脚本把 video blur 了，但问题问 main sound source。此时 video corruption
可能是 `answer_irrelevant`，而不是自动 `answer_relevant`。

### B2. Modality Status

| 标签 | 定义 |
|---|---|
| `clean` | 模态可用 |
| `corrupted` | 模态损坏但仍部分可用 |
| `missing` | 模态基本不可用，如全静音 |
| `conflicting` | 该模态与另一个模态冲突 |
| `irrelevant` | 模态存在，但与当前问题无关 |
| `not_applicable` | 本 pilot 中不是证据模态 |

本 pilot 中 question text 通常是 `not_applicable`，因为它是 task query，不是 evidence。

### B3. Corruption Relevance

| 标签 | 定义 |
|---|---|
| `answer_relevant` | 损坏影响当前问题的可答性或 evidence route |
| `answer_irrelevant` | 损坏存在，但不影响当前问题 |
| `unclear` | 标注者无法稳定判断 |

如果两个标注者都认为 `unclear`，该样本不进入主测试集。

### B4. Recoverability

Recoverability 是本标准最关键的标签，必须是 task-conditioned。

| 标签 | 定义 | 正确行为 |
|---|---|---|
| `recoverable` | 损坏后，另一个可用模态有足够 task-relevant evidence 支持 gold answer，且标注者能指出证据 | 使用恢复模态回答 |
| `partially_recoverable` | 另一个模态有弱线索，但不足以高置信支持 gold answer | 低置信或拒答，取决于风险策略 |
| `unrecoverable` | 损坏后，没有可用模态能支持 gold answer | 拒答 |

硬规则：

> 不能指出 evidence pointer，就不能标 `recoverable`。

这个规则是为了避免“感觉能恢复”变成 gold。

### B5. Oracle Policy Action

Oracle policy action 定义：

> 理想 evidence-governance 系统在这个 corrupted instance 上应该怎么做。

Schema：

```json
{
  "selected_route": ["audio"],
  "abstain": false,
  "expected_answer": "gold answer or null",
  "risk_level": "normal|cautious"
}
```

规则：

- `recoverable`：`abstain=false`，route 指向足够支持答案的模态。
- `partially_recoverable`：默认 `abstain=true`；如果接近充分，标
  `risk_level=cautious` 并进入 adjudication。
- `unrecoverable`：`abstain=true`，`expected_answer=null`。
- `answer_irrelevant` corruption：不应因为存在无关损坏而拒答。

### B6. Corrupted Instance Gold Record 示例

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

## 6. Stage C: Model-Output Scoring

评分不只看 final answer，而是拆成 parse、diagnosis、action、consistency。

### C1. Parse / Schema

| 指标 | 定义 |
|---|---|
| `parse_ok` | JSON 是否可解析 |
| `schema_ok` | 是否包含必需字段 |
| `invalid_field_count` | 非法枚举值数量 |

如果 `parse_ok=false`，诊断和行动分数记 0，但保留 raw output。

### C2. Diagnosis Score

| 指标 | 定义 |
|---|---|
| `audio_status_hit` | audio 状态是否匹配 gold |
| `video_status_hit` | video 状态是否匹配 gold |
| `diagnosis_macro_hit` | audio/video 状态平均命中 |
| `corruption_relevance_hit` | corruption relevance 是否匹配 |
| `recoverability_hit` | recoverability 是否匹配 |
| `recovery_source_hit` | recovery source 集合是否匹配 |
| `evidence_pointer_hit` | evidence pointer 是否落在可接受范围 |

pilot 初版定位可先用 `hit / miss / not_scorable`，正式版再加 temporal IoU。

### C3. Action Score

| 指标 | 定义 |
|---|---|
| `route_hit` | selected_route 是否匹配 oracle |
| `abstain_hit` | abstain 是否匹配 oracle |
| `answer_hit` | 非拒答时答案是否等于 gold answer |
| `governed_success` | route、abstain、answer 同时正确 |
| `false_answer_on_unrecoverable` | gold unrecoverable 但模型仍回答 |

### C4. Diagnosis-to-Action Consistency

核心错误类型：

| 类型 | 定义 |
|---|---|
| `diagnosis_wrong_action_wrong` | 诊断错，行动也错 |
| `diagnosis_wrong_action_right` | 诊断错但碰巧行动对 |
| `diagnosis_right_action_right` | 诊断对，行动也对 |
| `diagnosis_right_action_wrong` | 诊断对，但行动错 |

核心指标：

```text
conditional_action_failure =
  count(diagnosis_right_action_wrong) / count(diagnosis_right)
```

这个指标回答：

> 如果模型已经知道证据哪里坏了，它为什么仍然选错路线、硬答或不拒答？

### C5. Fixed-Rule Comparison

对同一条 frozen diagnosis，比较：

- model action from frozen diagnosis；
- fixed rule action from the same frozen diagnosis。

如果 fixed rule 明显优于 model action，说明失败不仅是 diagnosis，而是模型没有稳定地把
diagnosis 转化成 policy。

## 7. Annotation Quality Control

拟定流程：

1. 至少双标 50 条 corrupted instances。
2. 自动比较关键字段：
   - `source_decision`
   - `corruption_relevance`
   - `recoverability`
   - `recovery_source`
   - `oracle_policy_action.abstain`
   - `oracle_policy_action.selected_route`
3. 不一致样本进入 adjudication。
4. 裁决后仍不清楚的样本进入 ambiguous split，不进主测试集。

需要报告：

- recoverability agreement；
- route agreement；
- abstention agreement；
- adjudication rate；
- rejection rate。

当前最低建议：

- recoverability agreement: `kappa >= 0.4`；
- preferred: `kappa >= 0.6`。

请专家判断这个阈值是否过低、过高，或者是否应该换别的一致性指标。

## 8. Pilot 规模与人工工作量

第一版 pilot 计划：

- source screening: 80-120 个 candidate source items；
- final source items: 约 40 个；
- corruption variants: 每个 source 约 4 个；
- scored instances: 约 160 条；
- double annotation: 至少 50 条 corrupted instances；
- adjudication: 预计 20-40 条，取决于分歧率。

预估工作量：

- 如果每条 corrupted instance 需要 1-2 分钟，160 条约 3-6 小时；
- source screening 另计，但 pilot 规模仍可控。

## 9. 已知风险与当前缓解

### 风险 1：把数据集粗类型当成 gold

缓解：

- `Sound` / `View` / `Both` 只作为 hint；
- 人工筛查重新确认 modality necessity。

### 风险 2：把 corruption metadata 当成 gold

缓解：

- generator metadata 只记录机械改动；
- `corruption_relevance` 和 `recoverability` 由人工任务条件化判断。

### 风险 3：recoverability 主观性太强

缓解：

- evidence-pointer gate；
- 双标和 adjudication；
- ambiguous split。

### 风险 4：任务被 trivial quality detector 解决

缓解：

- 加 corrupted-but-irrelevant controls；
- 加 clean-hard controls；
- 加 quality-only route detector baseline；
- 如果简单质量检测器接近 oracle，则不能声称该 benchmark 测到了高级 evidence
  governance。

### 风险 5：action correctness 和 answer accuracy 混淆

缓解：

- 分开 policy action correctness、task execution correctness、governed success；
- 单独报告 false answer on unrecoverable。

### 风险 6：标准过重，难以扩展

缓解：

- pilot 小规模；
- 规则和模型只生成候选标签；
- 人工核查集中在最关键的 benchmark gold 字段。

## 10. 需要专家重点审的问题

### A. 概念有效性

1. 这套标准是否真的测到了 evidence governance under degradation？
2. 它是否和普通 missing-modality robustness 有清楚区别？
3. `diagnosis_right_action_wrong` 是否适合作为核心现象？

### B. 标签定义

4. `recoverable` / `partially_recoverable` / `unrecoverable` 是否可操作？
5. 是否应该保留 `partially_recoverable`，还是改成二分类更稳？
6. evidence-pointer gate 是否过严？会不会排除 diffuse evidence 的合理样本？
7. `irrelevant` 是否应该作为 modality status，还是只放在
   `corruption_relevance` 里？

### C. Oracle Policy

8. `oracle_policy_action` 的定义是否防得住审稿质疑？
9. 如果某个模态轻微损坏但仍有用，`selected_route` 是否允许包含该模态？
10. `partially_recoverable` 默认拒答是否合理？

### D. Scoring

11. diagnosis score 和 action score 是否拆得足够清楚？
12. `governed_success` 对 pilot 来说是否过严？
13. conditional action failure 是否适合做 headline metric？
14. pilot 规模下应报告 raw rates、confidence intervals、paired comparison、
    McNemar-style tests，还是其他统计？

### E. Annotation Quality

15. pilot 双标 50 条是否够？
16. route set 和 abstention 应该用什么 agreement metric？
17. adjudicated examples 是否可以留在 main split？
18. AAAI 风格 benchmark 至少需要什么 agreement 阈值？

### F. Paper Contribution

19. 这套 annotation / scoring standard 本身是否能构成 benchmark 贡献的一部分？
20. 它相对现有 robust multimodal / missing modality benchmark 的新意在哪里？
21. 在 benchmark 变大之前，我们不能 claim 什么？
22. 正式扩展前还需要哪些 baselines 或 controls？

## 11. 当前决策点

我们需要决定是否冻结这套 v0 标准，然后开始：

1. 做 annotation sheet；
2. 筛 80-120 个 source candidates；
3. 标 160 条左右 corrupted instances；
4. 实现 scorer；
5. 跑 `qwen3.5-omni-plus` 和 `qwen3-omni-flash`；
6. 分析 diagnosis-to-action failures。

请专家判断：在开始这些工作前，这套标准是否还需要大改。

## 12. 希望专家输出格式

建议专家按以下格式反馈：

1. 总体判断：accept / minor revision / major revision / reject。
2. 这套标准最强的三个点。
3. 最薄弱或最危险的三个点。
4. 对标签定义的具体修改建议。
5. 对 scoring metrics 的具体修改建议。
6. 对 annotation agreement / adjudication 的建议。
7. 如果目标是 AAAI 风格 benchmark paper，这套标准是否足够支撑。
8. 建议加入哪些 failure cases 或 controls。
