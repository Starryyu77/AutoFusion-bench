# AutoFusion-Bench 研究 Proposal

> Date: 2026-06-19
> Status: Decision Team proposal v0.1
> Purpose: 讲清楚当前研究问题、为什么值得做、我们准备怎么做，以及后续可以探索哪些方向。

## 0. 一句话概括

我们要研究的问题不是“多模态模型在坏模态下还能不能答对题”，而是：

> 当音频、视频等证据不可靠时，多模态大模型能不能先判断证据哪里出了问题，再基于这个判断做正确行动：选择可信模态、恢复信息、回答，或者在证据不足时拒答？

我们把这个能力称为 **unreliable multimodal evidence governance**，把模型“诊断对了但行动错了”的现象称为 **diagnosis-to-action gap**。

## 1. 研究背景

多模态大模型正在被用于处理视频、音频、图像和文本输入。但真实场景里的多模态证据通常并不干净：

- 音频可能静音、噪声大、错位，或者被其他声音误导；
- 视频可能模糊、遮挡、低光、冻结，或者关键区域不可见；
- 文本可能只是问题指令，也可能来自 ASR / subtitle / caption，存在漏词、错词或和音视频冲突；
- 有些问题只需要音频，有些只需要视频，有些必须音频和视频一起看；
- 有些污染虽然存在，但对当前问题其实不重要。

所以，一个可靠的多模态系统不应该只追求最终答案。它还应该知道：

1. 哪些证据可靠；
2. 哪些证据坏了；
3. 坏掉的信息是否可以从其他模态补回来；
4. 当前应该看 audio、video、audio+video，还是拒答；
5. 最终答案是否真的被可信证据支持。

这就是本项目的核心动机。

## 2. 核心研究问题

### RQ1: 模型能否诊断不可靠证据？

给定一个 corrupted audio-video QA instance，模型是否能判断：

- 哪个模态被破坏；
- 破坏类型是什么；
- 破坏是否和当前问题有关；
- 当前证据是否足以支持回答。

这里的重点不是脚本是否知道自己加了什么噪声，而是模型是否能在任务语境下理解证据可靠性。

### RQ2: 模型能否判断可恢复性？

当某个模态受损后，模型是否知道缺失信息能不能从其他模态恢复？

例子：

- audio 静音后，如果问题必须依赖声音，应该不可恢复；
- video 轻度遮挡后，如果 audio 仍然能提供答案线索，可能可恢复；
- 污染的是无关模态时，模型不应该过度报警。

### RQ3: 模型能否把诊断转化为正确行动？

这是本项目最核心的问题。

模型即使诊断出“audio 被污染”，也可能仍然选择 audio 作为证据；即使说“证据不足”，也可能继续高置信回答。我们要评估：

- route 是否正确；
- abstain 是否正确；
- 是否选择了受损模态；
- 是否违反自己的诊断；
- 是否在不可恢复时硬答。

### RQ4: 诊断、行动和最终答案之间的错误如何分解？

最终答案错，不一定说明模型不会诊断；route 选对但答案错，也不等于 policy action 错。

因此我们要拆开评估：

- diagnosis failure；
- recoverability failure；
- policy action failure；
- abstention failure；
- task execution failure。

这个错误分解本身就是 benchmark 的价值。

## 3. 我们的研究假设

当前最重要的假设是：

> 多模态大模型可能具备一定证据诊断能力，但不稳定地把诊断结果转化为正确行动。

我们希望通过实验观察几类现象：

- 模型能指出 audio / video 被污染，但仍然使用该模态；
- 模型能说证据不足，但仍然输出答案；
- 模型 route 正确，但 final answer 错；
- 模型 final answer 正确，但 diagnosis / route 是错的；
- 一个简单规则系统使用模型自己的 diagnosis，可能比模型自己的 action 更稳。

如果这些现象在扩大样本后稳定出现，就可以形成论文主发现。

## 4. 预期贡献

### Contribution 1: 问题定义

我们把不可靠多模态证据下的模型行为定义为一个 evidence governance 问题，而不是普通 missing modality robustness。

核心链条是：

```text
unreliable evidence
  -> evidence diagnosis
  -> recoverability judgment
  -> route / answer / abstain
```

### Contribution 2: Benchmark protocol

我们基于公开原始音视频 QA 数据，构造受控 corrupted instances，并增加 human-verified label：

- clean source 是否合格；
- corrupted 后是否可答；
- 是否可恢复；
- oracle evidence route；
- 是否应该拒答；
- 是否进入 headline scoring。

### Contribution 3: 诊断到行动的评估指标

我们不仅看 final answer accuracy，还看：

- diagnosis macro-F1；
- recoverability macro-F1；
- policy action accuracy；
- conditional policy failure；
- self-inconsistency；
- false answer on unanswerable；
- governed success；
- rule lift。

其中核心指标是：

```text
conditional_policy_failure = P(policy_action_correct=false | triage_diagnosis_right=true)
```

### Contribution 4: 系统性分析

如果 pilot 结果成立，我们将分析不同模型在不同证据损坏类型下的失败模式：

- audio neglect；
- visual over-trust；
- false alarm on irrelevant corruption；
- over-answering under insufficient evidence；
- route-correct but answer-wrong；
- diagnosis-correct but action-wrong。

## 5. 当前实验路线

### 5.1 当前主线

当前阶段聚焦：

> audio-video evidence governance under textual queries

也就是说，文本主要是问题指令，音频和视频是证据来源。

这比一开始声称完整 text-audio-video evidence governance 更稳，因为 AVQA 风格任务里的 text 不是可污染证据，而是 query。只有当后续引入 subtitle / ASR / caption / transcript 作为 evidence 时，才适合扩展到完整 text-audio-video。

### 5.2 数据底座

当前优先数据：

- AVQA / AVQA-videos；
- MUSIC-AVQA / MUSIC-AVQA v2.0 / FortisAVQA 作为补充候选。

本轮不把 MELD / CMU-MOSI / CMU-MOSEI / IEMOCAP 作为主数据，因为这些数据容易被文本或情感标签主导，不适合当前 audio-video evidence governance 主线。

### 5.3 当前 mini-pilot

当前已有：

- 10 个 clean source；
- 40 条 corrupted instances；
- source-level modality label 已冻结；
- corrupted-instance review 已进入正式审核草案；
- 当前 triage 包括 17 条 headline candidate、13 条 partial 裁决、3 条 oracle route 修复、1 条 unclear、6 条 exclude。

下一步是冻结 `mini_pilot.gold.jsonl`，再跑模型 diagnosis、real action、fixed-rule control 和 scorer。

## 6. 可探索方向

### Direction A: 主线 benchmark

目标：完成一个小而严谨的 benchmark protocol。

重点问题：

- 40-source / 160-instance 是否足够支撑主发现；
- source bucket 是否平衡；
- corrupted instance 是否覆盖 answer-relevant 和 answer-irrelevant；
- gold label 是否足够可靠；
- 指标是否能清楚区分 diagnosis、action 和 final answer。

这是最适合当前项目的主线。

### Direction B: 数据集扩展

如果 AVQA 中 audio-video complementary 样本太少，可以探索：

- MUSIC-AVQA；
- MUSIC-AVQA v2.0；
- FortisAVQA；
- 其他需要同步音视频证据的 QA 数据。

选择标准不是“数据集名气大”，而是：

- 原始同步媒体可获得；
- 问题不能只靠文本猜；
- 有明确 audio-only、video-only、audio-video joint 样本；
- 可以构造可靠的 corruption；
- 人类能稳定判断 answerability 和 route。

### Direction C: Text evidence extension

后续可以探索完整 text-audio-video evidence governance。

候选方式：

- 加入 ASR transcript；
- 加入 subtitle；
- 加入 caption；
- 引入 TVQA / How2QA 风格数据；
- 构造 text 与 audio/video 冲突。

但这个方向必须等 audio-video 主线跑通后再做。否则容易让任务边界变乱。

### Direction D: Budget-aware routing

我们可以把 route choice 和推理成本联系起来。

例如：

- 只看 audio；
- 只看 video；
- 看 audio+video；
- 先低成本诊断，再决定是否调用高成本 video model；
- 在证据不足时拒答，避免浪费预算。

这个方向适合作为扩展实验或 discussion，不一定作为第一篇主线。

### Direction E: Fixed-rule policy vs model action

这是一个很有潜力的分析方向。

做法：

1. 先让模型输出 diagnosis；
2. 冻结这份 diagnosis；
3. 分别让模型自己做 action，以及让固定规则根据 diagnosis 做 action；
4. 比较二者。

如果固定规则能稳定提升 policy action，说明瓶颈不是“模型不知道证据坏了”，而是“模型不会把诊断用于行动”。

### Direction F: Risk-aware abstention

研究模型在不可恢复或低置信样本上是否会拒答。

可探索指标：

- false answer rate on unanswerable；
- false abstention on answerable；
- coverage-risk curve；
- governed success under risk constraint。

这个方向对实际部署价值强，也容易和普通 final accuracy benchmark 拉开区别。

### Direction G: Error taxonomy

除了主表，还应该做 qualitative taxonomy：

- 音频被污染但模型继续相信音频；
- 视频受损但模型继续相信画面；
- 无关模态污染导致 false alarm；
- 模型知道不可恢复但仍然答；
- 模型 route 对但答案错；
- 模型答案对但证据路线错；
- 模型对 corruption artifact 过拟合。

这会帮助论文从“做了一个数据集”变成“揭示了模型系统性弱点”。

## 7. 实验设计草案

### 7.1 数据构造

正式 pilot 建议：

- 40 个 clean source；
- 每个 source 约 4 个 corrupted instances；
- 总计约 160 scored instances；
- source bucket 尽量平衡：
  - audio-only；
  - video-only；
  - audio-video joint；
  - irrelevant corruption control；
  - conflict / temporal mismatch candidate。

### 7.2 模型设置

至少包含：

- direct answer baseline；
- diagnosis-only；
- model action from frozen diagnosis；
- fixed-rule action from frozen diagnosis；
- oracle route / oracle abstention control。

模型面板先从可用模型开始：

- Qwen Omni 系列；
- 后续可按预算加入其他 audio-video capable MLLMs。

### 7.3 指标

主表不只放 final accuracy。

建议主指标：

- diagnosis accuracy / macro-F1；
- recoverability accuracy / macro-F1；
- policy action accuracy；
- conditional policy failure；
- abstention correctness；
- answerable task accuracy；
- governed success；
- rule lift。

### 7.4 分析维度

结果应按下面维度切分：

- source modality bucket；
- corruption type；
- severity；
- answerability；
- recoverability；
- route type；
- model family。

## 8. 关键风险

### Risk 1: AVQA 样本太简单

如果大量样本只靠 audio 或 video 单模态就能答，或者问题和选项本身就能猜出答案，那么 benchmark 价值会下降。

应对：

- source gate 必须严格；
- question-only 可猜样本直接剔除；
- 必要时引入 MUSIC-AVQA / FortisAVQA。

### Risk 2: 人工标签不稳定

answerability、recoverability、oracle route 都需要人类判断，可能存在分歧。

应对：

- partial / unclear 不进 headline；
- 关键样本做 adjudication；
- 报告 disagreement；
- 保留 risk-sensitive analysis。

### Risk 3: corruption artifact 太明显

如果模型只要看到噪声/模糊就能猜任务意图，benchmark 会变成 artifact detection。

应对：

- 加入 irrelevant corruption control；
- 加入 clean-hard control；
- 让污染是否 answer-relevant 由人工判断；
- 不把 generator metadata 当 gold。

### Risk 4: 模型接口不稳定

不同模型对音频/视频输入支持不一致，可能影响可比性。

应对：

- 记录 token / media consumption；
- 记录 parse success；
- 使用同一批 frozen gold；
- 模型输入失败要单独报告，不混入能力结论。

### Risk 5: 论文 claim 过大

当前主线是 audio-video evidence governance under textual queries，不应过早声称完整 text-audio-video benchmark。

应对：

- 第一篇主线聚焦 audio-video；
- text evidence extension 作为后续方向；
- 所有 claim 经过 Decision Team freeze。

## 9. 阶段性路线

### Phase 1: Mini-pilot gold freeze

目标：

- 完成 40 条 corrupted instance 审核；
- 裁决 partial / unclear / oracle-route；
- 冻结 `mini_pilot.gold.jsonl`。

### Phase 2: Mini-pilot scorer

目标：

- 跑 diagnosis；
- 跑 real action；
- 跑 fixed-rule control；
- 生成 metrics 和 failure cases。

### Phase 3: Go / no-go decision

判断：

- 是否存在清晰 diagnosis-to-action gap；
- 数据质量是否足够；
- 标注成本是否可控；
- 是否需要换或补数据集。

### Phase 4: 40-source pilot

目标：

- 40 clean source；
- 约 160 corrupted instances；
- 至少 2 个 audio-video capable model；
- annotation agreement / adjudication report；
- 主表和错误分析。

### Phase 5: Paper framing

目标：

- 确定题目；
- 固定 contribution；
- 写 benchmark card；
- 写 annotation guideline；
- 写 reproducibility checklist；
- 准备投稿版本。

## 10. 协作方式

本项目采用 Decision Team 和 Research Execution Team 分工。

Decision Team 负责：

- 研究问题；
- 数据边界；
- 标注标准；
- task card；
- gold freeze；
- claim freeze；
- 最终审计。

Research Execution Team 负责：

- 数据下载；
- source screening；
- corruption generation；
- annotation；
- model run；
- 初步结果记录。

AI Agent 负责：

- 文件整理；
- validator；
- scorer；
- PR 审计；
- failure summary；
- handoff。

这保证本地工作区保持为决策和审计空间，而不是杂乱的实验堆场。

## 11. 最终目标

如果 mini-pilot 和 40-source pilot 都成立，最终论文可以定位为：

> 一个面向多模态大模型的 evidence governance benchmark，评估模型在不可靠音视频证据下是否能完成诊断、可恢复性判断、证据路由、拒答和最终回答，并揭示 diagnosis-to-action gap。

它的价值不在于“又做了一个坏模态数据集”，而在于：

> 把模型对不可靠证据的理解能力，与模型基于该理解采取正确行动的能力区分开，并系统测量二者之间的断裂。
