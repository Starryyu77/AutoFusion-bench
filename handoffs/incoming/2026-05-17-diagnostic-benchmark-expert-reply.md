# Incoming Handoff: diagnostic benchmark direction

> Received from the user on 2026-05-17. This is the accepted direction for the
> next AutoFusion-Bench framing pass.

我读完后的判断是：**你们现在最适合做的不是“单纯在别人数据集上刷性能”，而是用公开原始多模态数据作为底座，自己定义一个新的 Benchmark 层：多模态感知缺陷诊断 + 跨模态信息补偿 + 预算受限下的模态选择/路由。**

你们文档里最核心的问题其实已经很清楚：在多模态输入质量变化、推理预算有限时，系统应该选择什么模态组合，并且是否能测出这种选择能力。文档里一开始就提到 text、audio、video 三个模态的 7 种组合，以及什么时候只用文本、什么时候用 text+video、什么时候用三模态融合的问题。后面又进一步把问题扩展为：模型要先判断音频、视频、文本是否有缺失或噪声，再判断能不能从其他模态中找回缺失信息。

## 1. 如果想发 AAAI，只在别人数据集上改进是否可行？

**可行，但取决于你所谓的“改进”是什么。**

如果只是拿 CMU-MOSI、MOSEI、IEMOCAP、MELD 这类已有数据集，做一些普通噪声增强，然后说模型涨了几个点，这个对 AAAI 风险很高。原因不是“不能用别人数据集”，而是贡献太容易被认为只是 engineering 或 incremental。AAAI 的主会议强调 substantial, original research and practices，关键词里也明确包含 ML: Evaluation and Analysis、ML: Multimodal Learning，所以 benchmark / evaluation paper 是有 fit 的，但它必须有清楚的新问题、新协议、新标注或新分析，而不是简单复现实验。([AAAI][1])

我建议你们把问题分成三档：

| 方案 | AAAI 风险 | 我的判断 |
|---|---:|---|
| **A. 只在别人数据集上改模型** | 中高 | 除非方法非常新、理论或实验非常强，否则不建议作为主线。 |
| **B. 用别人原始数据，但自己构造缺陷、标注、任务和评测协议** | 中低 | 最适合你们。严格来说这已经是在做自己的 Benchmark。 |
| **C. 完全自己采集图片/音频/视频/文本数据** | 中 | 原创性强，但周期、标注、伦理、版权、质量控制成本都高。 |

所以回答第一个问题：**可以不从零采集数据，但不能只是“改别人的数据集”。你们需要把公开数据集变成一个新的 benchmark：新的任务定义、新的缺陷生成协议、新的跨模态补偿标签、新的评价指标、新的 baseline suite。**

你们文档里其实也倾向这个路线：一方面提到需要找开源的多模态数据，而且要有原始数据；另一方面也意识到如果数据太少，工作量和创新性都不够。

需要注意的是，这个方向已有非常接近的工作。例如 2026 年的 MissMAC-Bench 已经在 robust multimodal affective computing 里针对 missing modality 问题提出了 benchmark，包含 fixed / random missing protocols，并在 4 个数据集上做了实验。([arXiv][2]) AAAI-21 的 SMIL 也已经研究 severely missing modality，并在 MM-IMDb、CMU-MOSI、avMNIST 上验证。([AAAI][3])

这意味着你们不能把 novelty 写成“我们研究多模态缺失”。这个已经不够了。你们应该把 novelty 写成：

> 现有 missing modality 工作主要测试模型在缺失模态下的最终任务性能；我们进一步评估多模态大模型是否能显式完成 **modality triage**：识别哪个模态坏了、坏在哪里、是否可恢复、应当调用哪个健康模态补偿、在预算有限时应选择哪些模态完成推理。

这个定位会比“缺失模态鲁棒性”更像一个新的 Benchmark。

## 2. 如果要自己做数据集，具体怎么做？

不建议从零采集。建议采用 **public raw datasets + controlled corruption + human-verified annotation + benchmark protocol** 的方式。

### 第一步：确定 Benchmark 的任务定义

你们的 Benchmark 不应该只是情感分类或缺失检测，而应该拆成五个子任务：

| 子任务 | 模型要回答什么 | 例子 |
|---|---|---|
| **T1 模态健康诊断** | 哪些模态可用？哪些损坏？损坏类型是什么？ | text 被截断，audio 有强噪声，video 面部遮挡 |
| **T2 缺陷定位** | 损坏发生在哪个时间段、文本 span、视频帧区间？ | audio 3.2-5.1s 噪声过大 |
| **T3 跨模态补偿** | 缺失信息能否从其他模态找回？从哪里找？ | text 缺失的情绪线索可从 audio prosody 找回 |
| **T4 预算受限模态路由** | 给定成本限制，应调用哪些模态？ | 只用 audio+text，不调用 video |
| **T5 最终任务表现 / abstention** | 最终答案是什么？如果不可恢复，是否能拒答？ | emotion = sad；或输出 unrecoverable |

文档里已经有 T1 和 T3 的雏形：先问视频、音频、文本是否可用，如果不可用原因是什么，再寻找不同信息之间的关联。你们也讨论过“图片/视频遮挡但可由音频判断”的场景，这正好是跨模态补偿。

### 第二步：选择基础数据集

优先选有 **原始视频、音频、文本/转录、标签** 的数据。可以先从情感分析和情绪识别入手，因为这类数据天然有 text-audio-video 对齐。

可选底座包括：

| 类型 | 候选数据 |
|---|---|
| Multimodal Sentiment Analysis | CMU-MOSI、CMU-MOSEI |
| Multimodal Emotion Recognition | IEMOCAP、MELD |
| 中文或跨语言扩展 | CH-SIMS、CH-SIMS v2、M3ED 等可调研 |
| 视频理解 / 音频中心理解 | 如果想跳出情感任务，可加 audio-centric video understanding 数据 |

MissMAC-Bench 也使用了 CMU-MOSI、CMU-MOSEI、IEMOCAP、MELD 这四类任务数据，所以你们如果继续用这些数据，必须在任务设计上和它区分开：不要只做 missing protocol，要做“缺陷诊断-证据定位-模态选择-跨模态恢复”。([arXiv][2])

### 第三步：构造缺陷，而不是随机加噪

你们应该把“缺陷”设计成可控、可解释、可标注的类型。建议按模态设计：

| 模态 | 缺陷类型 | 可控参数 |
|---|---|---|
| Text | 截断、span deletion、ASR 错词、语义替换、矛盾文本、时间错位 | 删除比例、span 位置、是否保留关键词 |
| Audio | 加噪、静音、clipping、低码率、speaker overlap、prosody masking、时间错位 | SNR、持续时间、噪声类型、位置 |
| Video | 面部遮挡、关键帧丢失、blur、低光、freeze frame、裁剪、object/face masking | 遮挡比例、帧区间、位置 |
| Image/frame | blur、遮挡、crop、低分辨率、缺失 | 区域、比例、severity |
| Cross-modal | 文本和音频冲突、音频与视频错位、一个模态损坏但另一个可恢复 | conflict type、recoverability |

关键是：**每个缺陷必须有 ground-truth metadata**。例如你用脚本把 audio 的 4.0-6.0 秒加噪，那么 corruption type、time span、severity 都是自动生成的 gold label，不需要人工标。人工主要标的是“这个缺失信息是否能从其他模态恢复”以及“应从哪个模态、哪个片段恢复”。

### 第四步：样本设计用 factorial matrix，但不要全组合爆炸

三个模态 text/audio/video 有 7 种非空输入组合。文档里也提到三模态可能有 7 种组合。但如果你再乘以缺陷类型、严重程度、任务类型，会爆炸。建议用 fractional factorial design：

| 维度 | 建议取值 |
|---|---|
| 模态状态 | clean、single corrupted、double corrupted、all corrupted |
| 缺陷严重度 | mild、medium、severe |
| 可恢复性 | recoverable、partially recoverable、unrecoverable |
| 跨模态关系 | complementary、conflicting、redundant |
| 预算设置 | low-cost、medium-cost、full-modality |

初版不要追求太大。比较合理的 AAAI 版本可以是：

- 3-4 个基础数据集；
- 1,000-2,000 个原始 clips；
- 每个 clip 生成 5-8 个 controlled corruption variants；
- 总 benchmark instances 约 8k-15k；
- 其中 2k-4k 做高质量 human-verified test set；
- 其余作为 dev / analysis / optional training set。

规模不一定最大，但必须保证协议清晰、标注可靠、baseline 完整。

## 3. 数据标定和 Benchmark 该怎么设计？

### 3.1 标注不要一上来就“让大模型全自动标”

你们文档里提到：先人工标一部分，再用大模型微调或自动标注其他数据。这个思路可以用，但要改成更严谨的版本：

**推荐流程：**

1. **规则脚本生成可验证标签**
   缺陷类型、缺陷位置、严重程度、受损模态，这些都由 corruption generator 自动记录。

2. **人工标 gold seed set**
   人工标“是否可恢复、从哪个模态恢复、证据位置、最终答案、是否应拒答”。

3. **LLM 只做候选标注，不直接当 gold**
   可以让模型生成初标，但必须经过人工抽检、冲突检测和 adjudication。AAAI 对生成式 AI 的政策要求作者对内容真实性、抄袭和准确性负责，而且 AI 系统不能作为论文作者或可引用来源。([AAAI][4])

4. **主动学习扩展**
   让多个模型或规则系统标注，优先人工复核 disagreement cases、low-confidence cases、severe corruption cases。

5. **报告标注质量**
   至少报告 inter-annotator agreement、人工复核比例、错误率估计、冲突裁决流程。

这点非常重要。Benchmark 论文最怕 reviewers 质疑 ground truth 不可靠。你们可以用自动化降低成本，但不能让“ChatGPT 标的”成为未验证真值。

### 3.2 推荐的 annotation schema

每条样本最好保存成结构化 JSON。核心字段如下：

```json
{
  "sample_id": "...",
  "source_dataset": "CMU-MOSEI",
  "modalities": ["text", "audio", "video"],
  "original_label": {
    "task": "sentiment",
    "value": 1.4
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
  "oracle_routing": ["audio", "text"],
  "evidence": [
    {
      "modality": "audio",
      "time": [3.1, 4.7],
      "reason": "prosody indicates negative affect"
    }
  ],
  "gold_answer": "...",
  "abstention_label": false
}
```

这个 schema 的好处是：它不只是 final label，而是能评估模型的中间推理能力。

### 3.3 Benchmark 的问题模板

你们文档里提到“要先设计一套问题，然后才知道标什么”，这个判断是对的。我建议每条样本至少生成四类问题：

**A. Diagnosis Question**

> 给定 text/audio/video，判断每个模态是否可用。如果不可用，请说明损坏类型、严重程度和位置。

**B. Recovery Question**

> 如果 text 中某段信息缺失，请判断是否能从 audio 或 video 中恢复；如果可以，请指出依据来自哪个模态和哪个时间段。

**C. Routing Question**

> 在最多只能使用两个模态的情况下，为了完成情绪识别/情感判断，应该选择哪些模态？为什么？

**D. Final Task Question**

> 在当前损坏条件下，判断该样本的情绪/情感/事件/动作。如果证据不足，请输出不可判断。

这比单纯问“情绪是什么”更强，因为你们测的是大模型是否知道 **该看什么、该忽略什么、该从哪里补信息**。

### 3.4 评价指标

不要只用 Accuracy / F1。建议分层评估：

| 能力 | 指标 |
|---|---|
| 模态损坏检测 | per-modality F1、macro-F1 |
| 缺陷类型识别 | classification accuracy / macro-F1 |
| 严重程度判断 | weighted kappa、MAE |
| 缺陷定位 | text span F1、temporal IoU |
| 跨模态补偿 | source modality accuracy、evidence hit rate、span/time IoU |
| 模态路由 | oracle route match、cost-normalized utility、regret |
| 最终任务 | Acc / F1 / MAE / Corr，取决于情感分类还是回归 |
| 鲁棒性 | clean-to-corrupted performance drop |
| 拒答能力 | coverage-risk curve、false abstention / false answer rate |

对于预算受限模态选择，可以定义一个综合分：

```text
Score = TaskPerformance - lambda * Cost
```

其中 Cost 可以是输入 token 数、视频帧数、音频秒数、推理延迟或 API 成本。这样能把你们文档里“推理预算有限”的点真正落成可评测指标。

### 3.5 你们的 Benchmark 应该和已有 missing-modality 工作拉开差异

已有工作通常关心：“模态缺失时最终任务性能下降多少？”你们应该关心：

1. 模型是否知道哪个模态坏了；
2. 模型是否知道坏在哪里；
3. 模型是否知道还能不能从其他模态补回来；
4. 模型是否能选择最低成本的有效模态组合；
5. 模型是否能在不可恢复时拒答。

这五点合起来才是你们的核心卖点。文档里也已经有“一个模态不好、另外两个完好；两个模态不好、一个完好；三个模态都不完好”的设计想法。

## 推荐的论文定位

我建议第一篇不要写成：

> We improve multimodal fusion under missing modalities.

而应该写成：

> We introduce a benchmark for evaluating modality triage and cross-modal recovery in multimodal large language models under perceptual degradation and budget-constrained inference.

中文就是：

> 我们提出一个用于评估多模态大模型在感知缺陷下进行模态诊断、跨模态恢复和预算化模态路由能力的 Benchmark。

这样和传统 missing modality / robust multimodal learning 区分更清楚。

## 具体执行路线

**第 1 周：文献和数据筛选**

把已有工作分成三类调研：missing modality、robust multimodal sentiment/emotion、multimodal LLM evaluation。重点检查 MissMAC-Bench、SMIL、MISA、MM-Align、multimodal prompt learning with missing modalities 等。你们需要明确写出：别人做的是 final-task robustness，你们做的是 modality triage + evidence-grounded recovery + cost-aware routing。

**第 2 周：定义 taxonomy 和 corruption generator**

先固定 text/audio/video 三模态，不要一开始加入太多图片任务。写出缺陷 taxonomy，并实现可复现的 corruption scripts。AAAI 的补充材料说明鼓励提供复现实验所需的软件和数据，reproducibility checklist 也要求说明 preprocessing code 和实验代码，所以你们的 corruption generator 最好从一开始就按可发布标准写。([AAAI][5])

**第 3-4 周：做 gold annotation pilot**

先选 200-300 条原始 clips，生成 1,000-2,000 条 corrupted instances。人工标 recoverability、evidence、oracle routing、final answer。这个阶段的目标不是规模，而是验证标注规范是否可操作。

**第 5-6 周：扩展数据 + 基线实验**

扩展到 8k-15k instances。基线包括：

- unimodal baselines：text-only、audio-only、video-only；
- full multimodal baseline：全模态输入；
- corrupted multimodal baseline：不做诊断直接输入；
- oracle routing baseline：用 gold route；
- learned routing baseline：让模型自己选模态；
- MLLM prompting baseline：直接问大模型；
- task-specific robust fusion baseline：已有 missing modality 方法。

**第 7 周：误差分析和论文主表**

主表不要只放最终任务性能。应该按 defect type、severity、recoverability、budget level 分表。AAAI 评审会更容易接受“这个 Benchmark 揭示了现有模型的系统性失败模式”，而不是只看一个总分。

## 我的最终建议

你们应该采用 **B 路线：公开原始数据 + 自己构建 Benchmark 层**。这既避免从零采集的巨大成本，又能形成真正属于你们的贡献。

第一篇 AAAI 的主贡献应是：

1. 新 benchmark：多模态感知缺陷、跨模态恢复、预算化路由；
2. 新标注：缺陷位置、可恢复性、证据来源、oracle modality routing；
3. 新评测协议：fixed/random corruption、single/double/all corrupted modalities、cost-aware evaluation；
4. 系统实验：多种 MLLM 和传统多模态模型的失败模式分析；
5. 可复现资产：corruption scripts、annotation guideline、benchmark card、datasheet。

数据文档建议按 Datasheets for Datasets 的思路写清楚 motivation、composition、collection / generation process、recommended uses 等信息；这类文档化能增强 benchmark 论文的可信度。([arXiv][6])

另外，系统提示我之前有些上传文件已经过期；我这次只基于当前这份《多模态模型数据集研讨.txt》和最新可查的线上资料来判断。

[1]: https://aaai.org/aaai-publications/aaai-conference-proceedings/ "AAAI Conference Proceedings - AAAI"
[2]: https://arxiv.org/html/2602.00811v1 "MissMAC-Bench: Building Solid Benchmark for Missing Modality Issue in Robust Multimodal Affective Computing"
[3]: https://cdn.aaai.org/ojs/16330/16330-13-19824-1-2-20210518.pdf "SMIL: Multimodal Learning with Severely Missing Modality"
[4]: https://aaai.org/conference/aaai/aaai-26/policies-for-aaai-26-authors/ "Policies for AAAI-26 Authors - AAAI"
[5]: https://aaai.org/conference/aaai/aaai-26/supplementary-material/ "AAAI-26 Supplementary Material - AAAI"
[6]: https://arxiv.org/abs/1803.09010 "[1803.09010] Datasheets for Datasets"

