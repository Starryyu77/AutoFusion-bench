# Evidence Governance Story

> Drafted: 2026-06-08  
> Purpose: absorb expert feedback and reset the paper story before designing the next experiment.

## 0. 一句话版本

我们不是要证明“多模态模型在坏模态下还能答题”，而是要测试：

> 当 text/audio/video 证据不可靠时，MLLM 是否能先判断哪些证据坏了，再据此选择正确行动：换用别的模态、节省预算、恢复信息，或者在证据不足时拒答。

最核心的论文故事是：

> Existing MLLMs may diagnose unreliable multimodal evidence, but fail to act on that diagnosis.

也就是 **diagnosis-to-action gap**。

## 1. 为什么旧故事不够

旧故事是：

> 我们做一个 benchmark，评估 modality triage、cross-modal recovery、budget-aware routing、abstention。

这个说法方向对，但太平铺。专家反馈指出：这些单独看都已经有很近的已有工作。

| 旧卖点 | 问题 |
|---|---|
| 模态缺失 / 噪声鲁棒性 | MissMAC-Bench、MissBench、UMQ 已经很近 |
| 样本级模态诊断 | SMCIR 已经做 sample-specific modality diagnosis + recovery |
| 跨模态冲突检测 | MMIR、CrossCheck-Bench 已经做 diagnostic conflict benchmark |
| 预算化 routing | MOSEL、Efficient Modality Selection、AdaLLaVA、MMR-Bench 已经有相邻路线 |
| 视频 / 音视频 MLLM 评测 | Video-MME、AVHBench 等已经覆盖大规模视频或音视频评测 |

所以不能再讲成：

> 我们第一次做模态诊断 / 第一次做缺失模态 / 第一次做预算路由。

这会被 reviewer 很快打掉。

## 2. 新故事：从多模态融合变成证据治理

新的中心问题不是“模型能不能融合多模态”，而是：

> 模型能不能治理不可靠的多模态证据？

这里的 **evidence governance** 包括四件事：

1. **Diagnose**: 哪些证据坏了、缺失了、冲突了？
2. **Judge recoverability**: 坏掉的信息能不能从其他模态补回来？
3. **Act under constraint**: 在预算有限时，该用哪些证据？
4. **Abstain**: 如果证据不可恢复，能不能不硬答？

这个 framing 的好处是：它把已有子任务连接成一条因果链。

```text
unreliable evidence
  -> diagnosis
  -> recoverability judgment
  -> route / answer / abstain
```

我们的创新点不在链条中的某一个节点，而在：

> 现有 benchmark 很少同时测试模型是否能把“知道哪里坏了”转化成“正确行动”。

## 3. 核心现象：diagnosis-to-action gap

论文最应该追求的 headline finding 是：

> 模型可能知道某个模态坏了，但仍然错误使用它、错误相信它、错误省略其他模态，或者在证据不可恢复时继续硬答。

这就是 **diagnosis-to-action gap**。

具体可测的现象包括：

- final answer 正确，但 diagnosis 错；
- diagnosis 正确，但 route 错；
- diagnosis 正确，但 recoverability 判断错；
- 模型知道证据冲突，但仍然输出高置信答案；
- 模型知道某模态坏了，却仍然把预算花在该模态上；
- text 被破坏或冲突时，模型仍然过度相信 text；
- audio 是关键证据时，模型仍然忽略 audio；
- 一个简单的 `stated diagnosis + fixed rule` pipeline 反而比模型自己的 end-to-end decision 更好。

最后一条尤其重要。它可以把故事变成：

> The bottleneck is not only perception or diagnosis, but using diagnosis to make decisions.

## 4. 新论文题目方向

旧题目：

> When to Read, Listen, or Watch? A Diagnostic Benchmark for Modality Triage, Cross-Modal Recovery, and Budget-Aware Routing in MLLMs

这个题目还能用，但专家担心 "AutoFusion" 容易让人以为是 fusion method。新题目可以更直接：

1. **EvidenceTriage-Bench: Can Multimodal LLMs Act on Unreliable Text-Audio-Video Evidence?**
2. **TriageMM: Benchmarking Evidence Governance in Multimodal Large Language Models**
3. **When Knowing Is Not Acting: Diagnosing the Evidence-to-Action Gap in Multimodal LLMs**
4. **AutoFusion-Bench: Diagnosing Evidence Triage in Multimodal LLMs**

建议工作名可以暂时保留 `AutoFusion-Bench`，但论文 title / abstract 里要出现 `EvidenceTriage` 或 `Evidence Governance`。

## 5. 新 problem statement

正式写法可以是：

> Multimodal large language models are increasingly deployed on text, audio, and video inputs, but real-world evidence is often unreliable: transcripts may contain ASR errors, audio may be noisy or misaligned, and video may be occluded or temporally corrupted. Existing benchmarks often evaluate whether models remain accurate under degraded or missing modalities. We ask a different question: can models govern unreliable multimodal evidence? Specifically, can they diagnose which evidence is unreliable, determine whether missing information is recoverable from other modalities, choose a cost-aware evidence route, and abstain when the available evidence is insufficient?

中文理解：

> 我们不是问坏模态下模型最终准不准，而是问模型是否知道证据出了什么问题，并能不能基于这个判断做正确决策。

## 6. 新 contribution claims

投稿时贡献建议写成四条。

### Contribution 1: 新问题定义

> We formulate unreliable multimodal evidence governance as a benchmark problem.

注意：不要说首创 missing-modality，不要说首创 modality diagnosis。说的是我们把 diagnosis、recoverability、route、abstention 放在同一个 evidence-governance protocol 下。

### Contribution 2: 新 benchmark protocol 和标注层

> We construct a benchmark protocol over corrupted text-audio-video inputs with human-verified recoverability, evidence location, oracle route, and abstention labels.

这里真正值钱的是：

- recoverability;
- evidence pointer;
- oracle route;
- abstention;
- artifact controls;
- generator metadata 和 human label 分离。

### Contribution 3: 新评测指标：diagnosis-to-action gap

> We evaluate not only final answers and diagnosis quality, but also whether models act correctly on their stated diagnosis.

主指标或主分析应该包括：

- diagnosis score;
- action score;
- diagnosis-action consistency;
- routing regret;
- false answer rate on unrecoverable cases;
- performance of `stated diagnosis + fixed rule` vs end-to-end decision.

### Contribution 4: 系统性发现

这是实验后才能写成结果，现在只能写成 hypothesis：

> We hypothesize that current MLLMs show a diagnosis-to-action gap: they may identify unreliable evidence but still route, recover, answer, or abstain incorrectly.

论文里必须用实验把这句话变成有数字的 finding。

## 7. 论文结构建议

### Introduction

故事线：

1. MLLMs can read, listen, and watch.
2. But real-world multimodal evidence is unreliable and costly.
3. Existing benchmarks mostly reward final answers or isolated robustness.
4. Correct deployment requires evidence governance: diagnose, recover, route, abstain.
5. We introduce a benchmark to test whether models can act on unreliable evidence.
6. We reveal a diagnosis-to-action gap.

Intro 里不要一开始讲“我们有五个任务”。先讲痛点和 gap。

### Related Work

不要防守式堆引用，而是画边界：

| Area | Representative work | What they cover | Our boundary |
|---|---|---|---|
| Missing-modality robustness | MissMAC-Bench, MissBench, UMQ | performance under missing/noisy modalities | we evaluate evidence governance and action under recoverability/abstention |
| Sample-level diagnosis/recovery | SMCIR | method for modality diagnosis and recovery on affective datasets | we benchmark MLLM explicit evidence decisions and downstream actions |
| Conflict benchmark | MMIR, CrossCheck-Bench | image-text conflict detection / compositional failures | we focus on text-audio-video degradation plus action: route/recover/abstain |
| Budgeted modality selection | MOSEL, Efficient Modality Selection, MMR-Bench | model/modality selection under cost | routing is part of our action layer, tied to diagnosed evidence reliability |
| MLLM video/audio-video eval | Video-MME, AVHBench | broad video/audio-video understanding or hallucination | we target unreliable evidence and diagnosis-to-action consistency |

### Benchmark

不要写成 T1-T5 平铺。改成两条 track：

#### Track A: Evidence Triage

- modality status;
- defect type;
- defect location;
- recoverability;
- recovery source and evidence pointer.

#### Track B: Decision Under Evidence Constraint

- selected route;
- answer;
- abstention;
- budget/risk tradeoff.

### Data Construction

重点写：

- primary substrate: AVQA / MUSIC-AVQA-style audio-video data;
- secondary substrate: filtered affective data only as control/generalization;
- modality necessity filtering;
- controlled corruption plus natural corruption;
- generator-family holdout;
- clean-hard and corrupted-irrelevant controls;
- human verified labels.

### Experiments

实验要服务故事，主表不要太散。

建议主结果顺序：

1. Final-answer benchmarks hide governance errors.
2. Models show diagnosis-to-action gap.
3. Recoverability and abstention are hardest.
4. Text over-trust and audio neglect are common.
5. Simple diagnosis-rule pipeline can beat end-to-end decision in some settings.
6. Artifact-control results show the benchmark is not solved by trivial quality detectors.

## 8. 不能再说的话

以下表述建议禁止：

- "first benchmark for missing modalities"
- "first modality diagnosis benchmark"
- "first cross-modal recovery benchmark"
- "first budget-aware multimodal routing benchmark"
- "modality triage is unexplored"
- "we introduce a new multimodal fusion method"
- "MELD/MOSEI results demonstrate the main benchmark signal"

改成：

- "we introduce a benchmark protocol for unreliable multimodal evidence governance"
- "we evaluate the coupling between evidence diagnosis and downstream action"
- "we study whether MLLMs can act on diagnosed evidence degradation"
- "we use recoverability and abstention labels to distinguish route switching from refusal"

## 9. Reviewer 最可能问什么

### Q1: 这不就是 missing-modality benchmark 吗？

回答：

> No. Missing-modality benchmarks usually measure final-task robustness under missing or noisy inputs. Our benchmark asks whether the model knows which evidence is unreliable, whether the lost cue is recoverable elsewhere, what evidence route should be used under budget, and whether the model should abstain. The core object is evidence-governance behavior, not only final accuracy.

### Q2: SMCIR 已经做 modality diagnosis + recovery 了，你们新在哪？

回答：

> SMCIR is a method for sample-specific diagnosis and cross-modal enhancement. We do not claim modality diagnosis itself is new. Our contribution is an evaluation protocol for general MLLMs with explicit semantic outputs and downstream evidence actions: route, answer, or abstain. We measure whether diagnosis leads to correct action.

### Q3: CrossCheck / MMIR 已经做 conflict benchmark 了，你们新在哪？

回答：

> They study inconsistency and conflict reasoning, mostly in image-text settings. We target corrupted text-audio-video evidence, including temporal audio/video degradation, recoverability, and cost-aware action. Our primary measure is not only conflict detection, but whether the model acts correctly after detecting evidence problems.

### Q4: Budget routing 已经有人做了，你们新在哪？

回答：

> Routing is not claimed as an independent novelty. It is the action layer used to test whether evidence diagnosis changes downstream behavior. Our key metric is not just route accuracy, but route regret and diagnosis-action consistency under unreliable evidence.

### Q5: 你们是不是 synthetic artifact benchmark？

回答必须靠实验设计支撑：

> We include natural corruption splits, generator-family holdout, clean-hard controls, corrupted-irrelevant controls, and trivial quality-detector baselines. Human labels are separated from generator metadata.

## 10. 最终故事版本

如果只留一个版本，我建议这样讲：

> Modern multimodal LLMs can read, listen, and watch, but real-world multimodal evidence is often unreliable. A transcript can be wrong, audio can be noisy, video can be occluded, and modalities can conflict. Existing benchmarks mostly ask whether the model still gets the final answer right. AutoFusion-Bench instead asks whether the model can govern unreliable evidence: diagnose what is unreliable, decide whether the missing cue is recoverable from another modality, choose what evidence to use under budget, and abstain when the evidence is insufficient. The central finding we aim to test is a diagnosis-to-action gap: models may recognize unreliable evidence but fail to act on that recognition.

中文口语版：

> 我们不是考模型“最后答得对不对”，而是考模型“知不知道该信谁，以及知道以后会不会做正确选择”。如果模型知道音频坏了但还相信音频，知道证据不够但还硬答，那就是现有 benchmark 看不到的问题。

## 11. 下一步才进入实验设计

故事定下来后，实验设计应该只服务这条主线：

1. 数据必须能产生非平凡证据选择，不能 text-only 就能解。
2. 标注必须能区分 recoverable / unrecoverable。
3. baseline 必须能测 diagnosis-to-action gap。
4. failure analysis 必须围绕模型是否正确行动，而不是只列 T1-T5 分数。

因此下一份文档应该是：

> pilot spec for diagnosis-to-action gap.

它应该定义：

- 30-50 source items;
- AVQA / MUSIC-AVQA primary substrate;
- 100-200 corruption episodes;
- recoverability / evidence / route / abstention schema;
- direct vs diagnosis vs stated-diagnosis-then-rule baselines;
- go/no-go criteria.
