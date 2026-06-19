# Research Proposal: AutoFusion-Bench

## 题目

**When to Read, Listen, or Watch? A Diagnostic Benchmark for Modality Triage, Cross-Modal Recovery, and Budget-Aware Routing in Multimodal Large Language Models**

中文题目：

**模型什么时候该读、听、看？面向多模态大模型的模态分诊、跨模态恢复与预算化路由 Benchmark**

## 摘要

多模态大模型通常被默认输入尽可能多的模态，例如文本、音频和视频。然而在真实场景中，不同模态的质量并不稳定：文本可能被截断，音频可能存在噪声或静音，视频可能发生遮挡、模糊或关键帧缺失。同时，推理预算也经常受限，模型不能总是无成本地读取所有模态。现有 missing-modality 或 robust multimodal learning 工作多关注“缺失模态下最终任务性能是否下降”，但较少系统评估模型是否知道哪个模态坏了、坏在哪里、是否能从其他模态补回信息，以及在预算有限时应该调用哪些模态。

本项目拟提出 **AutoFusion-Bench**：一个基于公开原始多模态数据构建的新 benchmark 层，用于评估多模态大模型在感知退化下的 **modality triage**、**cross-modal recovery** 和 **budget-aware routing** 能力。我们不从零采集大规模数据，而是选择具有原始 text/audio/video 的公开数据集作为底座，通过可复现脚本生成受控缺陷，并结合人工验证标注 recoverability、evidence、oracle route 和 abstention 标签。Benchmark 将包含五个任务层：模态健康诊断、缺陷定位、跨模态补偿、预算受限模态路由、最终任务表现或拒答。我们将评估多种 MLLM 与传统多模态 baseline，分析它们在不同缺陷类型、严重程度、可恢复性和预算条件下的系统性失败模式。

目标论文定位为 AAAI benchmark / evaluation paper。核心贡献不是“在已有数据集上刷分”，而是提出一个新的诊断式评测协议，揭示现有模型是否真正知道该读什么、听什么、看什么，以及什么时候应该不使用某个模态。

## 1. 背景与动机

多模态学习的常见假设是：更多模态通常带来更强的感知能力。因此，许多模型默认融合所有可用输入，例如 text + audio + video。但这个假设在真实场景中并不总成立。

第一，模态质量会随样本动态变化。同一条数据中，文本可能完整但语音噪声严重；另一条数据中，视频可能被遮挡但音频语气仍然提供关键信息。第二，不同模态之间并非总是冗余关系，有时是互补关系，有时甚至存在冲突。第三，推理预算有限时，全模态输入可能成本过高，模型需要判断哪些模态是必要的、哪些可以跳过。

因此，一个更贴近真实使用的问题是：

> 当 text、audio、video 的质量发生变化，且推理预算有限时，模型是否能判断哪个模态可信、缺失信息能否从其他模态补回，以及应该调用哪些模态完成任务？

这不是单纯的 missing modality robustness，也不是普通的多模态融合架构改进。它更接近一个“模态调用决策”问题：模型需要像调用工具一样决定什么时候读文本、什么时候听音频、什么时候看视频、什么时候使用两种或三种模态，以及什么时候应该拒答。

## 2. 相关工作与研究缺口

已有研究覆盖了若干相邻方向：

- **Missing modality robustness**：研究训练或测试阶段部分模态缺失时，模型如何保持最终任务性能，例如 ACL 2024 的 multimodal prompt learning 工作，以及 AAAI 2026 的 sample-specific modality diagnosis / cross-modal enhancement 工作 [R2, R8]。
- **Missing-modality benchmark**：例如 MissMAC-Bench 和 MissBench，它们分别从 unified missing-modality protocol、shared / imbalanced missing-rate protocol 和 modality equity 等角度推进 robust multimodal affective computing 评测 [R10, R11]。
- **Low-quality multimodal fusion**：近期综述将低质量多模态问题总结为 noisy、incomplete、imbalanced、quality-varying 等类型，并说明真实系统中的模态质量会动态变化 [R1]。
- **Dynamic modality selection / budgeted inference**：JMLR 2024、EMNLP 2024 和 ICCV 2025 的相关工作已经讨论了 modality selection、inference serving 和 latency-budget-aware adaptive inference [R3, R4, R7]。
- **MLLM evaluation and cross-modal inconsistency**：Video-MME 评估 MLLM 的视频、字幕和音频综合理解能力；MMIR 和 CrossCheck-Bench 则显示现有 MLLM 在跨模态不一致和冲突解析上仍有明显缺口 [R5, R6, R9]。

这些工作说明“多模态缺失/噪声”“动态模态选择”和“跨模态冲突检测”本身都不是空白。因此，本项目不能把 novelty 写成“我们研究 missing modality”。我们的研究缺口应定义为：

> 现有工作多评估缺失或低质量模态下的最终任务性能；我们进一步评估多模态大模型是否能显式完成 modality triage：识别哪个模态坏了、坏在哪里、是否可恢复、应从哪个健康模态补偿，以及在预算有限时应选择哪些模态。

这个缺口要求新的数据标注、新的任务定义和新的评价指标，而不只是对已有数据集做噪声增强。

## 3. 研究目标

本项目目标是构建一个新的多模态诊断式 Benchmark，用于回答以下研究问题：

1. **模态健康诊断**：模型能否判断 text、audio、video 中哪些模态可用、损坏、缺失或冲突？
2. **缺陷定位**：模型能否指出缺陷发生在文本 span、音频时间段、视频帧区间或区域？
3. **跨模态补偿**：当某个模态缺失关键信息时，模型能否判断该信息是否能从其他模态恢复，并指出证据来源？
4. **预算化路由**：在限制只能使用一个或两个模态，或限制 token / audio seconds / video frames / API cost 的情况下，模型能否选择最低成本且足够的模态组合？
5. **拒答能力**：当所有可用模态都不足以支持判断时，模型能否输出 unrecoverable / abstain，而不是硬猜？

## 4. Benchmark 设计

### 4.1 输入与模态组合

每条原始样本包含三类核心模态：

- `T`: text / transcript / caption
- `A`: audio waveform / audio clip
- `V`: video / frames

三模态的非空组合共有七种：

```text
T, A, V, TA, TV, AV, TAV
```

Benchmark 不默认全模态输入，而是要求模型在样本级判断应该使用哪个组合。

### 4.2 五个任务层

| 任务 | 名称 | 模型要输出什么 |
|---|---|---|
| T1 | Modality Health Diagnosis | 每个模态是否 clean / corrupted / missing / conflicting |
| T2 | Defect Localization | 缺陷位置：文本 span、音频时间戳、视频帧或区域 |
| T3 | Cross-Modal Recovery | 是否可从其他模态恢复，恢复来源和证据位置 |
| T4 | Budget-Aware Routing | 给定预算下应选择的模态组合 |
| T5 | Final Task / Abstention | 最终答案，或证据不足时拒答 |

### 4.3 缺陷类型

缺陷应由可复现脚本生成，而不是随机、不可解释地加噪。

| 模态 | 缺陷类型 | 可控参数 |
|---|---|---|
| Text | 截断、span deletion、ASR 错词、语义替换、矛盾文本、时间错位 | 删除比例、span 位置、关键词是否保留 |
| Audio | 加噪、静音、clipping、低码率、speaker overlap、prosody masking、时间错位 | SNR、持续时间、噪声类型、位置 |
| Video | 面部遮挡、关键帧丢失、blur、低光、freeze frame、crop、object/face masking | 遮挡比例、帧区间、区域 |
| Cross-modal | 文本与音频冲突、音频与视频错位、一个模态损坏但另一个可恢复 | conflict type、recoverability |

每个 corruption operator 都必须输出 metadata，包括受损模态、缺陷类型、严重程度、位置和随机种子。

### 4.4 数据来源

不建议从零采集大规模数据。建议采用：

> public raw multimodal datasets + controlled corruption + human-verified annotation + benchmark protocol

候选数据集包括：

- Multimodal sentiment / emotion: `CMU-MOSI`, `CMU-MOSEI`, `IEMOCAP`, `MELD`
- 中文或跨语言扩展: `CH-SIMS`, `CH-SIMS v2`, `M3ED`
- 非情感类扩展: audio-centric video understanding 或 AVQA-style 数据集

初版建议至少包含一个情感/情绪类数据集和一个非情感类音视频理解数据集。原因是：SMCIR、MissMAC-Bench、MissBench 和 UMQ 已经在 multimodal affective computing / multimodal sentiment analysis 上建立了很近的参照系 [R8, R10, R11, R12]；如果只使用 CMU-MOSEI / MELD / IEMOCAP，审稿人可能认为该工作只是另一个 multimodal sentiment analysis missing-modality benchmark。

## 5. 标注方案

### 5.1 机械生成标签

以下标签由 corruption generator 自动生成，可作为机械 gold：

- corrupted modality
- corruption type
- severity
- text span
- audio timestamp
- video timestamp / frame region
- random seed
- generator version

### 5.2 人工验证标签

以下标签需要人工验证：

- recoverability: `recoverable`, `partially_recoverable`, `unrecoverable`
- recovery source modality: `T`, `A`, `V`, `TA`, `TV`, `AV`
- evidence location: text span / audio timestamp / video time or region
- oracle route under budget
- final answer under corrupted input
- abstention label

LLM 可以生成候选标注，但不能直接作为 gold label。所有用于 test set 的语义标签必须经过人工复核或冲突裁决。

### 5.3 样本 schema

```json
{
  "sample_id": "cmu_mosei_00042_v3",
  "source_dataset": "CMU-MOSEI",
  "modalities": ["text", "audio", "video"],
  "original_label": {
    "task": "sentiment",
    "value": -1.4
  },
  "corruption": {
    "text": {
      "status": "corrupted",
      "type": "span_deletion",
      "severity": "medium",
      "span": [12, 25]
    },
    "audio": {
      "status": "clean"
    },
    "video": {
      "status": "corrupted",
      "type": "face_occlusion",
      "severity": "mild",
      "time": [3.2, 5.8]
    }
  },
  "recoverability": "recoverable",
  "recovery_source": {
    "modality": "audio",
    "time": [3.1, 4.7]
  },
  "oracle_route": ["audio", "video"],
  "gold_answer": "negative affect",
  "abstention_label": false
}
```

## 6. 评价指标

Benchmark 不应只报告最终任务 accuracy / F1。建议分层评估：

| 能力 | 指标 |
|---|---|
| 模态损坏检测 | per-modality F1, macro-F1 |
| 缺陷类型识别 | classification accuracy, defect-type macro-F1 |
| 严重程度判断 | weighted kappa, MAE |
| 缺陷定位 | text span F1, temporal IoU, frame/region IoU |
| 跨模态补偿 | source modality accuracy, recoverability F1, evidence hit rate |
| 模态路由 | oracle route match, budget violation rate, routing regret |
| 最终任务 | accuracy, macro-F1, MAE, correlation, task-specific score |
| 拒答能力 | coverage-risk curve, false abstention rate, false answer rate |

对于预算约束，可以定义成本归一化效用：

```text
Score = TaskPerformance - lambda * Cost
```

其中 `Cost` 可以是 input token 数、音频秒数、视频帧数、推理延迟、显存占用或 API 成本。不同 leaderboard 必须明确使用哪一种 cost model。

## 7. Baseline 设计

最低 baseline suite 应包括：

1. `text_only`
2. `audio_only`
3. `video_only`
4. `full_multimodal`
5. `corrupted_multimodal_no_diagnosis`
6. `random_legal_route`
7. `static_best_route`
8. `budget_only_route`
9. `quality_only_route`
10. `joint_quality_budget_route`
11. `oracle_route`
12. MLLM structured prompting baseline
13. task-specific robust fusion / missing-modality methods

主表不应只比较最终任务性能，还应展示不同模型在 T1-T5 各层能力上的差异。

## 8. 预期贡献

本项目预期形成五类贡献：

1. **新 Benchmark**：面向多模态大模型的模态分诊、跨模态恢复和预算化路由评测。
2. **新标注层**：缺陷位置、可恢复性、证据来源、oracle route 和 abstention。
3. **新评测协议**：single / double / all corrupted modalities，fixed / random corruption，cost-aware evaluation。
4. **系统实验**：评估 MLLM 与传统多模态方法在不同缺陷类型、严重程度、可恢复性和预算下的失败模式。
5. **可复现资产**：corruption scripts、annotation guideline、benchmark card、datasheet 和 baseline code。

## 9. 执行计划

### 第 1 周：文献与数据筛选

- 完成 missing modality、robust multimodal learning、MLLM evaluation、dynamic modality selection、cross-modal inconsistency detection 的 related-work matrix。
- 检查候选数据集的 raw data、license、下载方式和模态对齐质量。
- 选定一个情感/情绪类数据集和一个非情感类数据集作为 pilot。

### 第 2 周：Taxonomy 与 corruption generator

- 冻结 text/audio/video 缺陷 taxonomy。
- 实现可复现 corruption generator。
- 抽取 30 条样本做端到端检查。

### 第 3-4 周：Gold annotation pilot

- 选择 200-300 条原始 clips。
- 生成 1,000-2,000 条 corrupted instances。
- 人工标注 recoverability、evidence、oracle route、final answer 和 abstention。
- 统计标注耗时、冲突率和初步一致性。

### 第 5-6 周：扩展数据与 baseline

- 扩展到 8k-15k instances。
- 跑 unimodal、full multimodal、oracle route、MLLM prompting 和已有 robust-fusion baseline。
- 分析模型是否在 T1-T5 上表现出系统性弱点。

### 第 7 周：论文主表与错误分析

- 按 defect type、severity、recoverability、budget level 分表。
- 总结模型失败模式：信错模态、找错证据、漏掉可恢复信息、选择过贵路线、不该拒答或该拒答时硬猜。
- 决定 AAAI 投稿版本的主线、数据规模和 claim boundary。

## 10. 风险与应对

| 风险 | 说明 | 应对 |
|---|---|---|
| 新颖性风险 | SMCIR、CrossCheck-Bench、MissMAC-Bench、MissBench、UMQ 等已有相近问题 [R8-R12] | 明确聚焦 modality triage + evidence-grounded recovery + cost-aware routing |
| 数据风险 | MELD / MOSEI 可能文本主导 | 加入非情感类音视频理解数据，避免只做 MSA benchmark |
| 标注风险 | recoverability 和 evidence 标签成本高 | 先做 200-300 clips gold pilot，验证 schema 后再扩展 |
| 自动标注风险 | LLM 生成标签可能不可靠 | LLM 只做候选标注，test set 必须人工验证 |
| 预算风险 | MLLM 多模态 API 成本高 | 先用小规模 pilot 和开源模型确定失败模式 |
| 复现风险 | 数据处理和缺陷生成不透明 | 从第一版开始发布 corruption scripts、metadata schema 和 datasheet |

## 11. 交付物

项目阶段性交付物包括：

- `benchmark_taxonomy.md`: 缺陷类型、可恢复性和路由标签定义。
- `corruption_generator`: text/audio/video corruption scripts。
- `annotation_guideline.md`: 人工标注规范和例子。
- `benchmark_schema.json`: 每条样本的结构化格式。
- `pilot_dataset`: 1k-2k 条 human-verified pilot instances。
- `baseline_suite`: unimodal、full、routing、oracle、MLLM prompting baseline。
- `benchmark_card` / `datasheet`: 数据构成、生成过程、用途和限制。
- AAAI paper draft。

## 12. 一句话定位

> AutoFusion-Bench 不是另一个 missing-modality robustness benchmark；它评估多模态大模型在感知退化和预算受限时，是否知道该信哪个模态、该从哪里补信息、该调用哪些模态，以及什么时候应该拒答。

## References

以下是 proposal 当前最应该引用的近年核心文献。除 Datasheets for Datasets 作为数据集文档化方法论保留外，主叙事优先围绕 2024-2026 的会议、期刊、AAAI 近邻工作和 arXiv 新近 benchmark 展开。正式论文版本可以继续补充经典数据集论文和更完整的 related work。

### Low-quality / missing-modality multimodal learning

[R1] Zhang et al. **Multimodal Fusion on Low-quality Data: A Comprehensive Survey**. arXiv 2024.
<https://arxiv.org/abs/2404.18947>

[R2] Guo, Jin, and Zhao. **Multimodal Prompt Learning with Missing Modalities for Sentiment Analysis and Emotion Recognition**. ACL 2024.
<https://aclanthology.org/2024.acl-long.94/>

[R3] Hu, Xu, Moon, Yadwadkar, and Akella. **MOSEL: Inference Serving Using Dynamic Modality Selection**. EMNLP 2024.
<https://aclanthology.org/2024.emnlp-main.501/>

[R4] He et al. **Efficient Modality Selection in Multimodal Learning**. JMLR 2024.
<https://jmlr.org/papers/v25/23-0439.html>

[R5] Fu et al. **Video-MME: The First-Ever Comprehensive Evaluation Benchmark of Multi-modal LLMs in Video Analysis**. CVPR 2025.
<https://arxiv.org/abs/2405.21075>

[R6] Yan et al. **Multimodal Inconsistency Reasoning (MMIR): A New Benchmark for Multimodal Reasoning Models**. Findings of ACL 2025.
<https://arxiv.org/abs/2502.16033>

[R7] Xu et al. **Learning to Inference Adaptively for Multimodal Large Language Models**. ICCV 2025.
<https://arxiv.org/abs/2503.10905>

### 2026 close competitors / direct novelty boundary

[R8] Chen et al. **Sample-specific Modality Diagnosis and Cross-modal Enhancement for Incomplete Multimodal Representations**. AAAI 2026.
<https://ojs.aaai.org/index.php/AAAI/article/view/39102>

[R9] Tian et al. **CrossCheck-Bench: Diagnosing Compositional Failures in Multimodal Conflict Resolution**. AAAI 2026.
<https://ojs.aaai.org/index.php/AAAI/article/view/39788>

[R10] Lin et al. **MissMAC-Bench: Building Solid Benchmark for Missing Modality Issue in Robust Multimodal Affective Computing**. arXiv 2026.
<https://arxiv.org/abs/2602.00811>

[R11] Pham et al. **MissBench: Benchmarking Multimodal Affective Analysis under Imbalanced Missing Modalities**. arXiv 2026.
<https://arxiv.org/abs/2603.09874>

[R12] **Addressing Missing and Noisy Modalities in One Solution: Unified Modality-Quality Framework for Low-quality Multimodal Data**. arXiv 2026.
<https://arxiv.org/abs/2603.02695>

### Policy / documentation references for benchmark release

[R13] AAAI. **Policies for AAAI-26 Authors**. 2026.
<https://aaai.org/conference/aaai/aaai-26/policies-for-aaai-26-authors/>

[R14] AAAI. **AAAI-26 Supplementary Material**. 2026.
<https://aaai.org/conference/aaai/aaai-26/supplementary-material/>

[R15] Gebru et al. **Datasheets for Datasets**. CACM 2021 / arXiv 2018.
<https://arxiv.org/abs/1803.09010>
