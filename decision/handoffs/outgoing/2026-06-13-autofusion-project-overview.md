# AutoFusion-Bench 项目总览

> 日期：2026-06-13  
> 目的：给组内同学、学弟和外部专家快速理解当前项目要做什么、为什么值得做、准备怎么实施、现在实验做到哪一步。

## 0. 一句话概括

我们想做的不是一个新的多模态融合模型，也不是简单在已有数据集上刷准确率。

我们准备做一个面向多模态大模型的 benchmark / evaluation protocol，核心问题是：

> 当音频、视频或文本证据不可靠时，模型能不能先判断证据哪里出了问题，再基于这个判断做正确行动：换用其他模态、选择合适证据路线、回答，或者在证据不足时拒答？

当前最核心的研究假设是：

> 多模态大模型可能能诊断出某个模态坏了，但不一定能根据这个诊断做正确决策。

我们把这个现象称为 **diagnosis-to-action gap**。

## 1. 项目目标：准备做什么

### 1.1 总目标

项目目标是构建一个用于评估多模态大模型 **证据治理能力** 的 benchmark。

这里的“证据治理”不是泛泛地问模型最终答对没有，而是把推理过程拆成一条更接近真实使用场景的链：

```text
多模态输入存在缺陷
  -> 诊断哪个模态可靠 / 不可靠
  -> 判断缺失信息是否能从其他模态恢复
  -> 选择应该看的模态组合
  -> 给出答案或拒答
```

因此我们关心五类能力：

1. **证据诊断**：模型是否知道 audio / video / text 哪个模态坏了、缺失了、冲突了。
2. **可恢复性判断**：坏掉的信息是否还能从另一个模态找回来。
3. **证据路由**：模型是否会选择正确的证据路线，例如只看 audio、只看 video、看 audio+video，或者拒答。
4. **风险控制 / 拒答**：当证据不可恢复时，模型是否能不硬答。
5. **最终任务执行**：在证据路线正确的情况下，模型最终答案是否正确。

### 1.2 当前 pilot 的收窄目标

专家反馈后，我们把第一阶段目标收窄为：

> 先验证 **audio-video evidence governance under textual queries**，也就是在“问题文本是任务指令、音视频是证据”的场景下，模型是否存在 diagnosis-to-action gap。

这意味着当前 pilot 不强行声称已经覆盖完整 text-audio-video 三模态证据治理。AVQA 风格任务里的 text 主要是 question，不是可被污染的证据模态。后续如果加入字幕、ASR transcript、caption 或 TVQA / How2QA 风格数据，才更适合声称完整 text-audio-video evidence governance。

### 1.3 论文目标

如果 pilot 结果成立，目标论文可以定位为 AAAI / ACL / EMNLP / NeurIPS Datasets and Benchmarks 方向的 evaluation / benchmark paper。

更合适的论文故事不是：

> 我们提出一个 missing modality benchmark。

而是：

> 我们提出一个评估多模态大模型是否能把“证据诊断”转化为“正确行动”的 benchmark protocol，并系统分析 diagnosis-to-action gap。

## 2. 项目背景：这个 story 怎么讲

### 2.1 为什么这个问题重要

多模态大模型正在被用来处理文字、声音、视频等输入。但现实中的多模态输入经常不可靠：

- 音频可能静音、噪声大、和视频错位，或者被替换成误导音频；
- 视频可能模糊、遮挡、冻结、低光、关键帧缺失；
- 文本可能来自 ASR 或 caption，存在漏词、错词、截断或和音视频冲突；
- 有些任务只需要一个模态，有些任务必须跨模态互补。

在这种情况下，一个可靠系统不应该只追求“猜对答案”。它还应该知道：

- 哪些证据可信；
- 哪些证据不可信；
- 还能不能从其他模态补回来；
- 是否需要节省推理预算；
- 是否应该拒答。

这就是我们说的 **evidence governance**。

### 2.2 和已有工作的区别

已有相关工作很多，所以 novelty 不能写成“第一次研究模态缺失”或“第一次做多模态鲁棒性”。我们的边界应当更精确。

| 已有方向 | 已有工作通常关心什么 | 我们要补的缺口 |
|---|---|---|
| Missing modality / noisy modality robustness | 模态缺失或噪声下最终任务性能下降多少 | 不只看最终性能，还看模型是否知道证据坏在哪里，并据此行动 |
| Multimodal conflict detection | 图文或多模态证据是否冲突 | 冲突只是缺陷类型之一，我们更关心冲突诊断之后是否 route / abstain 正确 |
| Modality selection / budgeted inference | 预算限制下选择哪些模态或模型 | 我们把选择行为和证据可靠性、可恢复性、拒答绑定起来 |
| 大规模视频 / 音视频理解评测 | 模型是否理解视频、声音、长视频内容 | 我们关注证据损坏后的诊断和行动一致性 |

所以这篇工作的核心卖点不是“多模态坏了还能不能答”，而是：

> 模型是否能治理不可靠证据，并把诊断结果落实到正确决策。

### 2.3 最核心的可发表发现

我们希望通过实验验证下面这些现象：

- 模型能说出 audio 被破坏，但仍然选择 audio 作为关键证据；
- 模型能说 evidence insufficient，但仍然高置信输出答案；
- 模型能诊断出 video 被遮挡，却没有改用可用 audio；
- 模型 route 选对了，但最终答案仍错，说明 policy action 和 task execution 需要分开评估；
- 一个固定规则系统使用模型自己的 diagnosis，有时可能比模型自己的 action 更稳。

如果这些现象在扩大样本后稳定出现，就是论文最有价值的 story。

## 3. 实施方案：准备怎么做

### 3.1 数据路线

当前主数据路线是 **AVQA / AVQA-videos**，备选是 **MUSIC-AVQA**。

具体链接：

- 项目 GitHub：https://github.com/Starryyu77/AutoFusion-bench
- AVQA 官方项目页：http://mn.cs.tsinghua.edu.cn/avqa/
- AVQA 原作者 GitHub：https://github.com/AlyssaYoung/AVQA
- AVQA-videos Hugging Face 打包版：https://huggingface.co/datasets/juyil/AVQA-videos

选择 AVQA 风格数据的原因：

- 它天然是 audio-video QA，问题文本是任务指令，音视频是证据；
- 适合测试 audio-only、video-only、audio+video 互补；
- 可以构造音频静音、视频模糊、音视频错位、跨模态冲突等 corruption；
- 相比 MELD / MOSI / MOSEI 这类情感数据，更不容易被文本主导。

当前明确边界：

- **MELD / CMU-MOSI / CMU-MOSEI / IEMOCAP 不作为本轮主数据**；
- 它们最多作为 diagnostic / control reference；
- 本轮必须使用原始同步音视频 MP4，不能只用 precomputed features。

### 3.2 数据构造流程

第一阶段 mini-pilot 计划：

1. 先准备 80-120 个候选 clean source；
2. 从中筛出 10 个高质量 clean source；
3. 每个 source 做 3-4 个 corruption；
4. 得到约 40 条 corrupted instances；
5. 用本地标注网站进行人工筛查和标注；
6. 跑 diagnosis、action、fixed-rule、scorer；
7. 如果信号成立，再扩到 40 source / 160 instances。

后续正式 pilot 计划：

- 40 个 clean source；
- 每个 source 约 4 个 corruption episode；
- 总计约 160 个 scored instances；
- 每条都需要人工检查；
- 按 source bucket 和 corruption family 平衡。

Source bucket 建议：

| Bucket | 目标 | 目的 |
|---|---|---|
| Audio-necessary | 答案主要靠声音 | 测 audio neglect |
| Video-necessary | 答案主要靠画面 | 测 visual degradation 和 route choice |
| Audio-video complementary | 音频和视频互补 | 测 recoverability 和证据选择 |
| Conflict / temporal mismatch | 适合构造冲突或错位 | 测 evidence governance under inconsistency |
| Clean-hard / corrupted-irrelevant control | 原样本难或污染无关模态 | 测 false alarm 和过度 triage |

Corruption family 建议：

| Family | 示例 |
|---|---|
| Simple missing / severe degradation | audio mute、key frame freeze |
| Mild / medium degradation | background noise、blur、low light |
| Temporal mismatch | audio shift、frame shift |
| Cross-modal conflict | audio cue 和 video cue 指向不同答案 |
| Corrupted-irrelevant control | 污染一个对当前问题不重要的模态 |

### 3.3 标注和 gold label 设计

我们不把 corruption script 生成的 metadata 直接当作 gold label。原因是：

- 脚本知道“我给 audio 加噪了”，但不知道这个噪声对当前问题是否真的重要；
- 某个模态被破坏，不等于答案不可恢复；
- 某些看似 video question 的样本，可能 audio 也能提供间接线索；
- 原始数据集本身可能有不清楚或需要常识经验的样本。

因此人工标注的重点不是重复填写“哪个模态被脚本破坏了”，而是判断任务层面的证据关系：

- clean source 是否真的支持 gold answer；
- corrupted 后是否还能回答；
- 如果能回答，应该依赖 audio、video、audio+video，还是其他证据；
- 如果不能回答，是否应该拒答；
- 是否能指出证据位置或简短理由；
- 这条样本是否适合进入 headline scoring。

关键标签包括：

- `source_decision`: clean source 是否合格；
- `instance_decision`: corrupted instance 是否进入主测评；
- `post_corruption_answerability`: 污染后 answerable / unanswerable / partially answerable；
- `recoverability`: recoverable / partially recoverable / unrecoverable；
- `oracle_policy_action`: 正确 route 和是否 abstain；
- `annotation_confidence`: high / medium / low。

### 3.4 模型实验设计

实验不只跑一个 end-to-end prompt。核心是把 diagnosis 和 action 拆开。

主要设置：

1. **Diagnosis-only**  
   模型只输出证据状态、缺陷、可恢复性，不输出最终答案。

2. **Model action from frozen diagnosis**  
   把同一个模型刚才的 diagnosis 再喂回模型，让它选择 route、abstain 和 final answer。

3. **Fixed rule from frozen diagnosis**  
   对同一份 frozen diagnosis 应用固定规则，生成 route / abstain。这样可以测试：模型的诊断信息是否足够被规则利用。

4. **Direct structured decision**  
   模型直接从 corrupted media 输出 route、answer、abstain，用作 end-to-end 对照。

5. **Oracle route / oracle defect-location**  
   给模型 gold route 或 gold defect-location，判断错误来自 perception、routing，还是 task execution。

### 3.5 评价指标

主指标不应只看 final answer accuracy。

当前重点指标：

| 指标 | 含义 |
|---|---|
| Diagnosis macro-F1 | 模型是否诊断对证据状态 |
| Recoverability macro-F1 | 模型是否判断对可恢复性 |
| Policy action accuracy | route 和 abstain 是否正确 |
| Conditional policy failure | `P(policy_action_correct=false | triage_diagnosis_right=true)` |
| Self-inconsistency rate | 模型是否违背自己的 diagnosis |
| Rule lift | 固定规则使用模型 diagnosis 是否比模型 action 更好 |
| False answer on unanswerable | 该拒答时模型是否硬答 |
| Governed success | route / abstain 正确且最终答案正确 |

特别注意：

> Policy action correctness 和 final-answer correctness 必须分开。  
> route 选对但答案答错，是 task execution failure，不应该直接算成 diagnosis-to-action failure。

## 4. 实验情况：目前做到哪一步

### 4.1 已完成的工程和实验

当前已经完成了 exp-002 的 smoke 链路，证明从数据、媒体、标注、模型调用到 scorer 是可以跑通的。

已完成内容：

- 在 `ntu-gpu43` 上同步了项目；
- AVQA metadata 和 15-video sample 已经 staged；
- 5 个 source MP4 和 5 个 corrupted MP4 验证保留 audio+video streams；
- DashScope / OpenAI-compatible client 可用，未把 API key 写入 repo；
- `qwen3.5-omni-plus` 和 `qwen3-omni-flash` 都完成 5-clip audio-video diagnosis smoke；
- 两个模型均观察到 audio 和 video tokens；
- 5/5 输出可解析 JSON；
- `qwen3.7-plus` 可处理 video/text，但没有确认 audio token，因此暂时只作为 video/text control；
- 本地 annotation app 已实现并通过 smoke test；
- annotation sheet generator、validator、CSV converter、scorer 已实现；
- 4-row smoke gold 已冻结；
- real action prompt 已跑通；
- fixed-rule action 和 real model action 都可以进入 scorer。

### 4.2 当前 smoke gold

当前 headline smoke gold 有 4 行。

原来有 5 条 smoke annotation，但其中 `smoke-video-necessary__video_blur` 仍是 partial / adjudication-only，因此没有进入 headline scoring。

这点很重要：我们没有把不确定样本硬塞进主结果。

### 4.3 当前模型和结果

当前 model panel：

- `qwen3.5-omni-plus`：主 audio-video MLLM；
- `qwen3-omni-flash`：第二个 audio-video MLLM；
- `qwen3.7-plus`：video/text control，暂不算完整 audio-video。

4-row real-action smoke 结果：

| Model | Policy action accuracy | Conditional policy failure | Task accuracy on answerable rows | Governed success |
|---|---:|---:|---:|---:|
| `qwen3.5-omni-plus` | 1.000000 | 0.000000 | 0.666667 | 0.750000 |
| `qwen3-omni-flash` | 0.750000 | n/a | 0.333333 | 0.500000 |

解释：

- 这是 smoke，不是论文结论；
- 样本只有 4 行，不能据此声称模型普遍存在或不存在 diagnosis-to-action gap；
- 但它证明了我们的 scorer 和 action protocol 可以跑通；
- `qwen3.5-omni-plus` 在这个小集合上表现更稳定；
- `qwen3-omni-flash` 的 diagnosis 和 action 都更弱；
- 两个模型在一个 conflict-like case 中都选对了 visual route，但最终把 `On the road` 答成了 `street`，说明 route correctness 和 final answer correctness 必须分开。

### 4.4 当前实验得到的谨慎结论

现在能说的结论：

1. **技术链路已经打通**：媒体 corruption、annotation sheet、annotation app、model diagnosis、real action、fixed-rule action、scorer 都能运行。
2. **Qwen Omni 路线可作为第一批模型面板**：至少两个 Qwen-family 模型能处理 same-instance audio-video。
3. **标注标准必须保留 clean-source gate**：公共 AVQA 样本不能默认当作可靠 gold，原始样本不清楚时必须排除。
4. **policy action 和 final answer 必须分离**：已有 smoke case 显示 route 正确但答案错误。
5. **还没有足够证据写 paper finding**：4-row smoke 只能证明协议可行，不能作为主实验结论。

## 5. 后续计划：大致安排

### Phase 1：10-source mini-pilot

目标：

- 学弟准备 80-120 个候选 source；
- 从中选出 10 个高质量 clean source；
- 每个 source 做 3-4 个 corruption；
- 得到约 40 条 corrupted instances；
- 用 annotation app 完成人工筛查和首轮标注；
- 跑 Qwen panel 的 diagnosis + real action + fixed rule + scorer。

成功标准：

- source selection 不被 question-only shortcut 主导；
- annotation label 能稳定填写；
- 至少出现若干可解释的 action failure / self-inconsistency / task execution failure；
- quality-only baseline 不能简单解决 route 选择。

### Phase 2：40-source pilot

目标：

- 扩到 40 source / 约 160 scored instances；
- 平衡 audio-necessary、video-necessary、audio-video complementary、conflict、control；
- 至少 2 个 audio-video-capable closed-source model；
- 如果可行，加入 1-2 个 open-source audio-video model；
- 输出主指标表和 qualitative case taxonomy。

成功标准：

- 至少一个核心 subset 上出现稳定 diagnosis-to-action gap；
- conditional policy failure 或 self-inconsistency 有足够样本支撑；
- rule lift 有解释价值；
- recoverability 标注一致性达到可接受水平；
- 结果不是由明显 synthetic artifact 或低级质量检测器解释。

### Phase 3：扩展 text evidence subset

目标：

- 加入小规模 subtitle / transcript / ASR / caption 证据；
- 测试 text corruption、ASR error、caption conflict；
- 判断是否可以把论文从 audio-video governance 扩展到 text-audio-video evidence governance。

如果这个 subset 做不扎实，论文就应诚实写成 audio-video evidence governance under textual queries，不强行扩大 claim。

### Phase 4：论文与 benchmark release

目标：

- 固化 benchmark protocol；
- 整理数据构造脚本、corruption generator、annotation guideline、datasheet；
- 完成 main table、ablation、error taxonomy；
- 准备 paper draft 和 supplementary；
- 明确哪些数据可以 release，哪些只能 release metadata / scripts / derived annotations。

## 6. 当前分工建议

### 学弟负责

- 下载和整理 AVQA / AVQA-videos；
- 准备 80-120 个候选 clean source；
- 筛 10 个 mini-pilot source；
- 整理 source items 和 corruption manifest；
- 跑本地 annotation website；
- 导出 validator/scorer-compatible JSONL；
- 记录媒体打不开、gold answer 可疑、corruption 效果不明显的样本。

### 我们负责

- 定义 benchmark story 和 evaluation protocol；
- 决定哪些样本进入 headline scoring；
- 维护 annotation schema、scorer、prompt、runner；
- 跑模型实验和统计指标；
- 做 error analysis 和 paper writing；
- 控制 novelty claim，避免讲成普通 missing-modality benchmark。

## 7. 当前风险

| 风险 | 影响 | 应对 |
|---|---|---|
| AVQA 样本可能能靠 question / common sense 猜 | benchmark 被 shortcut 破坏 | 加 question-only gate 和 clean-source gate |
| corruption 太人工 | 模型可能只学会低级质量检测 | 加 realistic corruption、generator-family holdout、quality-only baseline |
| recoverability 标注主观 | reviewer 质疑 gold label | 要求 evidence pointer、复核、agreement / adjudication |
| audio-video 模型支持不足 | 模型面板不够 | 先用 Qwen Omni，后续验证更多模型 |
| 样本太小 | 不能写论文结论 | smoke 只作协议验证，真正结论等 40-source pilot |
| story 和已有工作太近 | novelty 不够 | 主打 diagnosis-to-action gap 和 evidence governance，而不是 missing modality |

## 8. 当前最重要的下一步

现在不要急着写大论文，也不要急着扩全量。

最重要的下一步是：

> 完成 10-source / 40-instance mini-pilot，并验证 diagnosis-to-action gap 是否真的出现。

具体执行顺序：

1. 学弟按 junior brief 准备 AVQA 候选源；
2. 我们审查 10 个 clean source 是否合格；
3. 生成 40 条 corruption instances；
4. 用 annotation app 完成人工标注；
5. 跑 Qwen diagnosis；
6. 跑 real action from frozen diagnosis；
7. 跑 fixed-rule action；
8. 用 scorer 输出 metrics；
9. 做 qualitative failure analysis；
10. 决定是否扩到 40-source pilot。

如果 mini-pilot 没有出现明显 gap，就应调整 corruption、source bucket 或故事线，而不是盲目扩大数据。

