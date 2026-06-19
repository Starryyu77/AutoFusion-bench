# 2026-05-17 多模态诊断式 Benchmark 会议总结与文献初判

> 2026-05-17 update: the incoming review in
> `handoffs/incoming/2026-05-17-diagnostic-benchmark-expert-reply.md` is now the
> accepted direction-setting handoff. The concise project position is route B:
> public raw multimodal datasets + controlled corruption + human-verified
> annotation + benchmark protocol.

## 结论先行

今天讨论出来的方向，建议先定义为：

> 面向多模态大模型的“模态可用性诊断、跨模态信息补全、预算约束下模态调用/融合选择”Benchmark。

它和仓库里已有的 exp-001 有亲缘关系：都关心 reliability / budget / modality choice。但今天的新想法更像一个面向 MLLM 的数据集与诊断任务，而不是继续在 MELD feature table 上调一个融合决策面。不要把它强行并入之前的 Memory 项目；也不要把它窄化成“改 fusion 架构”。

文献初判：已经有人做了很多相邻问题，包括 missing modality、noisy modality、missing-modality benchmark、动态模态选择、MLLM 跨模态不一致检测。但我还没有看到完全覆盖以下四点的标准 benchmark：

1. 每条样本显式标注 text / audio / video 的可用性、缺失/噪声/偏差类型和位置。
2. 标注缺失信息能否从其他模态补回，以及从哪个模态、哪个时间段/文本 span 补回。
3. 要求模型在推理预算有限时选择应该调用哪些模态或融合模板，而不是默认全模态输入。
4. 以 MLLM 诊断、证据定位、路由决策和最终任务表现共同评估，而不只是训练一个鲁棒分类器。

因此，AAAI 方向可以成立，但必须把创新点落在“诊断式数据标注 + 可恢复性标签 + 预算路由评估协议 + MLLM baseline”上；单纯说“多模态缺失/加噪声 benchmark”不够新。

## 会议总结

### 1. 研究问题从“架构搜索”转向“模态调用决策”

最开始的问题是：当一个样本有 text、audio、video 三种模态，而每种模态质量会变化、推理预算有限时，系统应该选择哪一种融合模板或模态组合。三模态有 7 种非空组合：T、A、V、TA、TV、AV、TAV。会议里逐渐形成的共识是，不要先把核心放在 cross-attention、gated fusion、MoE、Transformer 结构变体或 NAS 上，而是先问：

- 什么时候只需要文本？
- 什么时候需要文本加视频？
- 什么时候必须三模态一起用？
- 什么时候某个模态虽然存在，但应该被弃用？
- 当一个模态缺失或被噪声污染时，模型能否知道该去哪个其他模态找补充信息？

这更像“教会模型调用哪些模态”，类似工具调用中的“什么时候调用浏览器/图片/外部工具”，而不是单纯的神经网络结构搜索。

### 2. Benchmark 应该测的是感知缺失诊断与跨模态补全

会议里反复强调：多模态模型要先判断每个模态是否可用、哪里有缺失或偏差，再决定如何协作。可测能力包括：

- 模态可用性判断：text/audio/video 是否完整、是否有噪声、是否遮挡、是否截断。
- 缺失位置描述：文本缺了哪一段，音频哪段不可用，视频哪几帧或哪个目标被遮挡。
- 跨模态补全：文本缺失的信息能否从音频语气或视频表情补回来；视频缺失的信息能否从文本或音频补回来。
- 不可恢复判断：如果多个模态都损毁，模型应该输出不可用或证据不足，而不是硬猜。
- 预算下选择：在有限预算下，模型应该调用最有信息量的模态组合，而不是默认全模态。

### 3. 标注前必须先设计问题体系

会议中明确提到，不能直接开始标注；要先定义 Benchmark 中要标哪些信息。建议的问题层级是：

- Q1：每个模态有什么感知问题？
- Q2：问题的类型和严重程度是什么？
- Q3：缺失内容是否可由其他模态恢复？
- Q4：若可恢复，应该从哪个模态、哪个片段找证据？
- Q5：在给定预算下，应选择哪组模态或哪种融合策略？
- Q6：基于可用信息，最终任务答案是什么？

现有的 mild / severe 数据处理可以继续用，但它只解决“怎么制造缺陷”，还没有解决“标注什么、如何评估模型是否理解缺陷”。

### 4. 标注策略：人工种子 + 自动扩展 + 人工复核

会议中认为全人工标注 text/audio/video 会非常重。比较现实的路线是：

- 先人工标一小批高质量种子样本。
- 用大模型生成候选诊断标签、缺失描述、可恢复性标签和证据位置。
- 通过人工复核、规则校验、双模型交叉检查来扩展。
- 后续如果 Benchmark 站住，再用 RL / SFT / routing policy 去提升模型在该 Benchmark 上的表现。

这个顺序很重要：先有 Benchmark，再谈方法；先证明现有 MLLM 在这个能力上不稳定，再提出 AutoFusion / routing / reinforcement 方法。

### 5. 近期行动节奏

会议里给出的节奏是：

- 这一周到下周三：调研相关文献和可用数据集，确定问题设计。
- 6 月或 6 月上旬：开始数据集标注和自动化扩展。
- 吴伟加入后：接入 ChatGPT API 和其他多模态模型，在 Benchmark 上测试表现。
- 如果 Benchmark 有清晰缺口和有效 baseline，就开始写 AAAI 论文。

## 文献调研

### A. 低质量多模态融合已经是明确研究方向

`Multimodal Fusion on Low-quality Data: A Comprehensive Survey` 把低质量多模态问题分成 noisy、incomplete、imbalanced、quality-varying 四类。这和我们的想法高度相关，因为我们不是只做“缺失模态”，还关心噪声、质量变化、模态贡献不均衡和样本级动态选择。

参考：https://arxiv.org/abs/2404.18947

对我们的影响：论文动机不能写成“没人研究低质量多模态”。正确写法应该是：已有工作研究低质量数据下的鲁棒融合，但缺少面向 MLLM 的、样本级、可解释的“诊断-补全-路由”评估协议。

### B. Missing modality 方法很多，但大多是模型方法，不是我们想要的诊断式数据集

代表工作：

- SMIL, AAAI 2021：研究训练/测试阶段模态严重缺失，用 Bayesian meta-learning 处理 missing modality。
  来源：https://ojs.aaai.org/index.php/AAAI/article/view/16330
- MissModal, TACL / EMNLP 2023：通过表示对齐提升 multimodal sentiment analysis 在缺失模态下的鲁棒性。
  来源：https://transacl.org/index.php/tacl/article/view/5491
- Multimodal Prompt Learning with Missing Modalities, ACL 2024：用 generative / missing-signal / missing-type prompts 生成缺失模态特征并学习模态内外信息。
  来源：https://arxiv.org/abs/2407.05374
- SMCIR, AAAI 2026：做 sample-specific modality diagnosis 和 cross-modal enhancement，用 entropy、modality similarity、mutual information 检测缺失和严重程度。
  来源：https://ojs.aaai.org/index.php/AAAI/article/view/39102
- UMQ, 2026 arXiv：把 noisy 和 missing 都视为统一的 modality-quality 问题，用质量估计、增强和 quality-aware MoE routing 处理。
  来源：https://arxiv.org/abs/2603.02695

对我们的影响：这些工作证明“缺失/噪声模态”不是空白，但它们多是 feature-level 模型补全或鲁棒融合。我们的差异应放在 Benchmark 任务定义：不仅预测情绪/类别，还要求模型说清楚“哪里坏了、能从哪里补、预算下用哪些模态”。

### C. Missing-modality benchmark 已经出现，必须避开重复

代表工作：

- MissMAC-Bench, 2026 arXiv：为 robust multimodal affective computing 建立 missing modality 评估，强调完整/不完整输入的统一模型、固定和随机缺失模式。
  来源：https://arxiv.org/abs/2602.00811
- MissBench, 2026 arXiv：关注 imbalanced missing rates，在四个 sentiment / emotion 数据集上定义 shared / imbalanced missing-rate protocols，并提出 MEI、MLI 诊断指标。
  来源：https://arxiv.org/abs/2603.09874
- MultiBench, NeurIPS Datasets and Benchmarks 2021：统一多个多模态任务，评估泛化、复杂度、missing/noisy modality robustness。
  来源：https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/file/37693cfc748049e45d87b8c7d8b9aacd-Paper-round1.pdf
- LUMA, SIGIR 2025：构造 text / image / audio 多模态不确定性数据集，可控制噪声和 OOD。
  来源：https://arxiv.org/abs/2406.09864

对我们的影响：如果只做“不同模态缺失率 + accuracy/F1”，会撞上这些工作。我们的 Benchmark 必须有更细的标签和任务结构：可用性诊断、证据定位、跨模态恢复、预算路由、不可恢复拒答。

### D. 动态模态选择和预算约束也有人做过

代表工作：

- Efficient Modality Selection in Multimodal Learning, JMLR 2024：在 cardinality constraint 下选择最有用的模态子集，给出理论和 greedy selection。
  来源：https://jmlr.org/papers/v25/23-0439.html
- AdaLLaVA, 2025：MLLM 推理时根据输入和 latency budget 动态重配置，在 accuracy / latency tradeoff 下运行。
  来源：https://huggingface.co/papers/2503.10905
- Dynamic Modality Scheduling, 2025 arXiv：用 confidence、uncertainty、semantic consistency 做样本级 modality weighting。
  来源：https://arxiv.org/abs/2506.12724

对我们的影响：预算/选择不是全新问题。新意应该是把“选择”建立在可解释的感知质量诊断和跨模态可恢复性上，而不是只做子集选择理论或 latency scheduler。

### E. MLLM 跨模态不一致检测是相邻但不同的线

代表工作：

- MMIR, 2025 arXiv / ACL Findings：检测网页、幻灯片、海报等 layout-rich 内容中的 visual-text semantic mismatches。
  来源：https://arxiv.org/abs/2502.16033
- CrossCheck-Bench, AAAI 2026：评估 MLLM 解析 image-text conflict 的能力。
  来源：https://ojs.aaai.org/index.php/AAAI/article/view/39788

对我们的影响：这条线支持我们写“现有 MLLM 缺少稳定的跨模态冲突和不一致处理能力”。但它们多集中在 image-text / document layout，不是 text-audio-video 的时序多模态感知缺失、证据补全和预算路由。

### F. 可用数据集候选

优先考虑有原始多模态数据、可做可控退化、并能支持证据定位的数据集。

- MELD：text/audio/video，多人对话情绪识别，约 13k utterances；已有 raw media。但仓库 exp-001 已经证明 MELD 在 feature-level 任务上文本主导，适合作为诊断集，不一定适合作为主正结果。
  来源：https://arxiv.org/abs/1810.02508
- CMU-MOSEI / CMU-MOSI：经典 text/audio/visual sentiment / emotion 数据集，CMU-MOSEI 是大规模 multimodal language dataset。
  来源：https://aclanthology.org/P18-1208/
- MUSIC-AVQA：audio-video QA，45k+ QA，天然要求音画协同和时序理解；如果补充 transcript 或问题文本，可作为非情感类主数据集候选。
  来源：https://arxiv.org/abs/2203.14072
- SONIC-O1：真实长视频 audio-video MLLM benchmark，有 QA、summarization、temporal localization 和 human-verified annotations；可参考其任务组织方式，但它不是缺失/补全 benchmark。
  来源：https://vectorinstitute.github.io/sonic-o1/
- AVQA / MUSIC-AVQA-R / M3ED / IEMOCAP：可作为扩展或对照，但需要逐一确认原始视频、音频、文本、许可和下载稳定性。

## AAAI 论文可以怎么起步

### 最小可行题目

建议题目暂定：

> When to Read, Listen, or Watch? A Diagnostic Benchmark for Budget-Aware Multimodal Modality Use under Perceptual Degradation

中文内部表述：

> 模型什么时候该读文本、听音频、看视频？一个面向感知缺失和预算约束的多模态诊断 Benchmark。

### 任务定义

每条样本由原始三模态输入和一个可控退化版本组成：

- `text`: transcript / caption / OCR / utterance text
- `audio`: waveform or audio clip
- `video`: frames / video clip
- `degradation`: 哪些模态被截断、遮挡、加噪、静音、错位、丢帧或语义扰动
- `budget`: 允许调用的模态数、token/audio/video processing cost、或模板 cost 上限

模型需要输出：

- `availability`: 每个模态是否可用
- `defect_type`: 缺失、噪声、遮挡、错位、冲突、不可判定
- `defect_location`: 文本 span、音频时间戳、视频时间戳/区域
- `recoverability`: 能否从其他模态补回
- `recovery_source`: 从哪个模态、哪个片段补回
- `route`: 给定预算下选择哪组模态
- `answer`: 任务答案
- `evidence`: 支撑 route 和 answer 的证据

### 标注 schema

建议先做 5 个一级标签：

1. `ModalityAvailability`: complete / partial / corrupted / missing / conflicting。
2. `DefectType`: text truncation, ASR error, audio noise, audio mute, video occlusion, video blur, frame drop, temporal misalignment, cross-modal conflict。
3. `Recoverability`: recoverable / partially recoverable / unrecoverable。
4. `RecoveryMap`: broken modality -> source modality -> evidence span/timestamp。
5. `BudgetRoute`: cheapest sufficient route、best route under budget、oracle route。

### 评估指标

建议不要只用最终任务 accuracy。至少需要：

- 诊断准确率：modality-level F1、defect-type F1。
- 位置准确率：text span F1、audio/video temporal IoU。
- 可恢复性判断：recoverability accuracy / macro-F1。
- 证据质量：evidence exact match、span overlap、LLM-judge 只作为辅助。
- 路由质量：oracle regret、cost-normalized utility、budget violation rate。
- 最终任务：accuracy / macro-F1 / MAE，依数据集任务而定。
- 拒答能力：unrecoverable case 上的 abstention precision / recall。

### Baseline 设计

至少要有：

- `text_only`, `audio_only`, `video_only`
- `all_modalities`
- `random_legal_route`
- `static_best_route`
- `budget_only_route`
- `quality_only_route`
- `joint_quality_budget_route`
- `oracle_route`
- MLLM zero-shot / CoT / structured prompt
- 可选：MissModal / prompt-learning / SMCIR 类特征补全方法作为传统模型 baseline

### 数据规模建议

AAAI 目标下，不建议只做 200 条 toy examples。现实路线：

- Pilot：200-500 条，验证 schema、标注一致性和模型失败模式。
- Main v1：2k-5k 条，高质量人工复核，至少 2 个数据源。
- Main v2：10k+ 条可通过程序退化 + LLM 辅助标注扩展，但必须保留人工验证 split。

如果资源紧，宁可先把 2k 条做深，包含 evidence / recoverability / route 标签，也不要做 50k 条只有 missing mask 的浅数据。

## 如果被认为“已经有人做过”，我们的改进点

如果审稿人把我们归到 MissBench / MissMAC-Bench / MultiBench / missing-modality robustness 这条线，建议从以下角度区分：

1. 从 missing mask 到 diagnostic evidence：别人多评估缺哪一个模态，我们标注缺失在哪里、为什么坏、证据从哪里补。
2. 从模型鲁棒性到模型自知能力：不仅看分类结果，也看模型能否识别自己该不该信某个模态。
3. 从全模态输入到预算调用：把模态使用看成 MLLM 的工具调用/路由问题。
4. 从情感分类到跨任务 benchmark：情感识别可以是第一站，但最好加入 AVQA 或真实长视频 QA，避免被说成又一个 MSA missing-modality benchmark。
5. 从 feature-level 补全到 raw-modality MLLM evaluation：接入 GPT / Gemini / Qwen-Omni / VideoLLaMA 等模型，评估真实输入，而不只是预提取特征。
6. 从单一缺失到组合退化：支持单模态坏、双模态坏、三模态全坏、跨模态冲突、时间错位。
7. 从 task metric 到 decision metric：引入 oracle regret、cost-normalized utility、budget violation rate。

## 推荐下一步

### 这周内

1. 冻结题目边界：不要写“多模态融合架构搜索”，写“多模态感知缺失诊断与预算路由 Benchmark”。
2. 做一个 1 页 taxonomy：defect type、recoverability、route label、answer task。
3. 选 2 个候选数据集做可行性检查：一个情感类，优先 CMU-MOSEI/MELD；一个非情感类，优先 MUSIC-AVQA/AVQA。
4. 抽 30 条样本，人工标完整 schema，计算标注耗时和一致性。

### 两周内

1. 做 200 条 pilot。
2. 跑 GPT / Gemini / Qwen-Omni / VideoLLaMA 类模型的 structured prompt baseline。
3. 看三个信号：
   - 模型是否能诊断模态缺陷？
   - 模型是否能找对补全来源？
   - 预算路由是否明显优于 static/full/simple baseline？

### 一个月内

1. 扩到 2k+ 样本。
2. 加强人工复核 split。
3. 做 baseline 表、错误分析、消融。
4. 若模型普遍失败且 oracle route 有明显收益，即可开始 AAAI 主文。

## 当前风险

- 新颖性风险：missing modality benchmark 已有，必须强调 diagnostic / recoverability / budget routing。
- 数据风险：MELD 可能太文本主导；仓库已有实验显示它更适合做诊断证据，不一定能做主正结果。
- 标注风险：缺失位置和跨模态补全证据很贵，必须用程序退化保留 ground-truth，并用人工验证语义可恢复性。
- MLLM 接入风险：audio/video/text 真三模态 API 能力、成本和一致性需要早测。
- AAAI 风险：纯数据集如果没有强 baseline、强错误分析、清楚的开放协议，会被认为只是工程收集。

## 一句话建议

这个方向可以做，但要把论文卖点从“我们也做 missing/noisy modality”改成：

> 我们提出第一个面向多模态大模型的诊断式 Benchmark，用来评估模型在感知退化下是否知道哪些模态可信、缺失信息能否跨模态补回，以及在预算约束下应该调用哪些模态。
