# Related-Work 定位（2026-06-19）

> 状态：Decision-Team 定位草稿。在 2026-06-08 故事文档的 related-work 表基础上，
> 补入 2026-06-19 文献扫描发现的新工作。
> 目的：在扩大 pilot 之前，钉死可辩护的新颖性内核，并对最接近的已有工作画清边界。

## 0. 可辩护内核（只说这一句）

我们**不**声称首个 missing-modality / 首个 modality-diagnosis / 首个 abstention /
首个 AV-robustness benchmark。这次 2026-06-19 扫描**唯一找不到对应物**的主张是：

> 我们把模型对不可靠音视频证据的**诊断**与它基于该诊断的**行动**解耦，
> 并用条件指标 `P(policy_action_wrong | diagnosis_right)`，
> 加上"固定规则消费模型自己冻结的诊断"这一对照，来度量二者的断裂。

其余一切（diagnosis、recoverability、routing、abstention、AV corruption）都定位为
**行动层所依赖的零件**，而不是独立的新颖性。

## 1. 边界表

| 领域 | 代表工作 | 它们覆盖了什么 | 我们的边界 |
|---|---|---|---|
| **Know-but-not-act gap**（现象上最贴脸） | Hidden in Plain Sight (arXiv 2506.00258) | MLLM 具备感知/推理能力，却不去暴露"静默出错"的输入；text/image 下的"推理能力 vs 行为顺从"断裂 | 同一现象，但我们把它定位到**音视频受损证据**、配上显式的 **route/recover/abstain 行动层**和条件 gap 指标，而非靠 clarifying-question 恢复 |
| **共识被打破下的校准 abstention**（标注上最贴脸） | OMD-Bench (arXiv 2603.27187) | 打破模态共识；逐样本人工标注"模态是否足够/该不该拒答"；calibrated abstention | 我们补上完整链 diagnose→**recoverability**→route→act，度量的是"违背自己诊断去行动"，而不只是 abstention 校准 |
| **AV 可信度 / 鲁棒性** | AVTrustBench (arXiv 2501.02135)；DAVE (arXiv 2503.09321) | AVTrust：600K AV QA，adversarial + compositional + modality-dependency，扰动下的响应校准。DAVE：强制两模态都必要，把误差拆成原子子类 | 不声称 AV-robustness 新颖性；**复用 DAVE 式的"模态必要性过滤"**作为构念效度门，测的是行动而非聚合准确率/校准 |
| **AVQA 鲁棒/去偏底座** | FortisAVQA + MAVEN (arXiv 2504.00487)；MUSIC-AVQA-v2 去偏 (arXiv 2310.06238) | FortisAVQA：改写问题 + head/tail 分布漂移以消语言捷径；MUSIC-AVQA-v2：去偏的答案分布 | 缓解我们 shortcut 风险的候选底座；作为数据来源引用，不是我们的贡献 |
| **跨模态冲突 / 不一致** | MMIR (arXiv 2502.16033)；CrossCheck-Bench (arXiv 2511.21717)；XModBench (arXiv 2510.15148) | 检测/裁决 image-text 冲突与跨模态一致性 | 我们针对的是时序 AV 退化 + recoverability + **检测之后的行动**，而非把冲突检测作为终点 |
| **AVQA 选择性回答** | Knowing When to Answer (arXiv 2602.04924) | 面向可靠 AVQA 的自适应置信度精炼（何时回答） | abstention 只是我们 policy 中的一个动作；我们还测 route + recovery 以及诊断-行动耦合 |
| **信任 / 不确定性评估** | FESTA (arXiv 2509.16648)；带早停 abstention 的 LLM cascade | 基于采样的信任分；成本敏感的 abstention | 它们是方法/分数，不是 evidence-governance 的评测 protocol |
| **Missing-modality 鲁棒性**（沿用旧笔记—待核实） | MissMAC-Bench, MissBench, UMQ, SMCIR | 缺失/噪声模态下的最终任务鲁棒性，或样本级诊断+恢复 | 我们评的是显式治理行为 + 行动，而非最终任务鲁棒性 |
| **预算化模态选择**（沿用—待核实） | MOSEL, MMR-Bench, AdaLLaVA | 成本约束下的模型/模态选择 | routing 是我们的行动层，绑定到诊断出的可靠性，用 regret + 诊断-行动一致性来评 |
| **AV/Video MLLM 评测** | Video-MME；AVHBench (arXiv 2410.18325) | 大范围视频/AV 理解或幻觉 | 我们针对不可靠证据 + 诊断到行动，而非泛能力 |

## 2. 最威胁 framing 的两篇

1. **Hidden in Plain Sight (2506.00258)** 已经在 MLLM 上证明了"能力 vs 顺从"的断裂。
   它既是"该现象真实且重要"的最佳引用，也是最强的"你不是第一个"风险。
   防御：它是 text/image、单轮、无 AV corruption、无 route/recover 行动层、无条件 gap 指标。
   我们必须把它当 motivation 引用，并明确写出我们新增了什么。
2. **OMD-Bench (2603.27187)** 已经有人工"模态是否足够/该不该拒答"标注且会打破模态共识。
   防御：它以 abstention 校准为中心；不评 recoverability routing，也不评"违背自己诊断"的 gap，
   且（现已核实，见 §5）没有 frozen-diagnosis 固定规则对照。

如果有 reviewer 把这两篇拼起来，就会落到我们附近。所以 headline **必须**是
条件分解 + 固定规则对照，而不是"我们在受损 AV 上测 abstention"。

## 3. 核实状态

- 本次会话已直接核实全文/abstract：DAVE (2503.09321)、Hidden in Plain Sight (2506.00258)、
  **OMD-Bench (2603.27187)**、**AVI-Bench (2606.07643)** 全文（见 §5）。
- 搜索列表里见到标题 + arXiv id，但未打开 abstract：AVTrustBench、
  FortisAVQA/MAVEN、MUSIC-AVQA-v2 去偏、MMIR、CrossCheck-Bench、XModBench、
  Knowing-When-to-Answer、FESTA、AVHBench。
- 沿用自旧项目笔记、**本次未重新查到**，论文引用前需核实：MissMAC-Bench、MissBench、
  UMQ、SMCIR、MOSEL、MMR-Bench、AdaLLaVA。

## 4. 论文 related-work 冻结前要做的事

- ~~打开并核实 OMD-Bench / AVI-Bench 全文~~ —— 2026-06-19 已完成，见 §5。
- 重新核实或删掉"沿用旧笔记"的条目。
- 确认这些工作里是否有谁评"基于陈述诊断去行动"；若没有，明确把它写成 gap。

## 5. OMD-Bench / AVI-Bench 全文核实（2026-06-19）

### OMD-Bench (2603.27187, Al Nazi 等；UC Riverside / UMBC / QCRI)——最近的邻居，但不构成核心碰撞

已核实范围：**三模态**（video + audio + **text**，三者都作为证据），27 anchor / 255 个基础 QA /
析因 `2^3 = 8` 种污染条件 → 4,080 instance。污染 = **语义替换**（把某模态替换成*另一个* anchor
的内容以制造冲突/失谐），用于评 (a) 更少混淆的模态依赖归因，(b) **calibrated abstention**，
并带人工逐样本"模态是否足够 / 是否该拒答"标注。10 个 omni 模型，zero-shot + CoT。

- **真实重叠：**人工 suffice/abstain 标注；隔离模态贡献的受控污染；over-/under-abstention 发现
  （与我们的 `false_answer` / `false_abstention` 指标重叠）。
- **已确认的缺口——我们的可辩护内核仍成立：**没有"可从另一模态恢复"的标注；没有 evidence
  **routing** 动作；没有 diagnosis-to-action gap / `conditional_policy_failure`；
  没有 frozen-diagnosis 固定规则对照。它的终点是 abstention *校准*（置信 vs 正确），
  不是*与自己陈述的诊断一致地行动*。它的污染是*替换*，不是真实同步媒体上的感知*退化*
  （blur/occlusion/noise/mute）。
- **战略含义：**OMD-Bench 已经做了我们**推迟**到 Phase 7 的三模态（text 作证据）污染设计。
  未来的 text extension **不要**讲成"首个三模态证据 benchmark"；用 退化-vs-替换 和
  行动-vs-校准 来区分。论文以 CPF + rule_lift 打头，**不是** abstention 率。

### AVI-Bench (2606.07643, Wang 等；2026-06-01)——低威胁，非竞品

已核实范围：一个认知启发的 AV **能力** benchmark，覆盖 perception / understanding / reasoning，
外加 AVI-Bench-PriSe（低语义刺激上的原始 AV 感知，测泛化），配四级 AVI 分类。
无 不可靠证据 / 污染治理 / abstention / diagnosis-to-action 内容。

- **处置：**归入"广义 omni-MLLM AV 评测"桶，与 Video-MME / AVHBench 并列。顺带引 OMD-Bench
  牵出的 omni 评测邻居：OmniBench、AV-Odyssey、WorldSense、UNO-Bench。
