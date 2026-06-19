# AutoFusion-Bench 详细研究 Proposal（2026-06-19, v1.0）

> Status: Decision-Team 详版 proposal，取代 2026-06-19 v0.1（`paper/proposal/2026-06-19-evidence-governance-research-proposal.md`）。
> Superseded by: `paper/proposal/2026-06-19-ENACT-core-proposal.zh.md`。
> 对外项目 / benchmark 名称已改为 **ENACT**；本文件保留为历史详版草案。
> 已纳入本日文献核实、headline 指标锁定、数据底座去风险、AAAI-27 时间线与质量门。
> 目标 venue：AAAI-27 主技术轨（全文 2026-07-28，补充材料和代码 2026-07-31），主轨为目标 + 明确后备。
> 配套文档：`decision/literature/`、`paper/tables/`、`decision/plans/exp-002/`、
> `governance/2026-06-19-aaai27-timeline-and-gates.zh.md`、`governance/2026-06-19-experiment-constitution-v2.zh.md`。

---

## 0. 摘要（一段话）

多模态大模型正被部署到充满不可靠证据的真实音视频场景：音频可能静音/噪声/错位，视频可能模糊/遮挡/冻结，
而有些问题只靠音频、有些只靠视频、有些必须二者。一个可靠的系统不应只追求最终答案，还应能**诊断**哪些证据可靠、
判断缺失信息能否**从另一模态恢复**、在约束下选择**证据路线**、并在证据不足时**拒答**。我们提出 AutoFusion-Bench，
一个评估 MLLM 能否在不可靠音视频证据下**把诊断转化为正确行动**的 benchmark protocol。其核心、也是与已有工作区分开的
不可替代点，是把"诊断"与"行动"解耦，并用条件指标
`conditional_policy_failure = P(行动错 | 诊断对)` 与"固定规则消费模型自己冻结诊断"的 `rule_lift` 对照，
系统度量 **diagnosis-to-action gap**。

## 1. 研究背景与动机

真实多模态证据通常不干净。音频可能静音、噪声大、与画面错位，或被无关声音误导；视频可能模糊、遮挡、低光、冻结；
即便文本存在（ASR/字幕/caption），也可能漏词、错词或与音视频冲突。同时，模态必要性是**任务相关**的：
同一段视频，"画面里在做什么"可能必须看视频，"声源是什么"可能必须听音频，而有些污染对当前问题其实无关。

因此可靠的多模态系统应当具备一条**证据治理**因果链：

```text
unreliable evidence -> evidence diagnosis -> recoverability judgment -> route / answer / abstain
```

现有 benchmark 大多奖励最终答案，或单独测某个环节（鲁棒性、冲突检测、abstention 校准）。
很少有人测：模型**知道证据坏了之后，会不会做出与该判断一致的正确行动**。这正是本项目的动机。

## 2. 核心研究问题

- **RQ1 诊断**：给定 corrupted audio-video QA instance，模型能否判断哪个模态坏了、坏在哪、是否与问题相关、证据是否足以回答？
- **RQ2 可恢复性**：某模态受损后，模型能否判断缺失信息可否从另一模态恢复（含"污染的是无关模态、不该报警"的情形）？
- **RQ3 行动**（最核心）：模型能否把诊断转化为正确行动——选对 route、该拒答时拒答、不使用自己刚判坏的模态、不在不可恢复时硬答？
- **RQ4 错误分解**：把 diagnosis / recoverability / policy action / abstention / task execution 的失败拆开，定位瓶颈在哪。

## 3. 研究假设

> 多模态大模型可能具备一定证据诊断能力，但**不稳定地**把诊断转化为正确行动。

可观测现象：能指出某模态被污染却仍使用它；说证据不足却仍高置信回答；route 对但答案错；答案对但 route/诊断错；
一个用模型自身诊断的简单固定规则反而比模型自己的端到端行动更稳。若这些现象在扩样后稳定出现，即构成论文主发现。

## 4. 与已有工作的关系（定位）

详见 `decision/literature/2026-06-19-related-work-positioning.zh.md`（含核实状态）。要点：

- **最近邻居 OMD-Bench (arXiv 2603.27187)**：三模态、用"语义替换"制造冲突、测 abstention 校准 + 人工 suffice/abstain 标注。
  我们的边界 = **真实感知退化**（非替换）+ recoverability/route 行动层 + **按自己诊断行动**（非校准）。
- **Hidden in Plain Sight (2506.00258)**：text/image 的"知道却不行动"，作为现象 motivation 引用。
- **AVTrustBench (2501.02135) / DAVE (2503.09321)**：AV 可信度/诊断；DAVE 的"两模态都必要"构造被我们复用为构念效度门。
- **AVI-Bench (2606.07643)**：AV 能力评测，低威胁。

**不可替代内核**：解耦诊断与行动 + CPF + rule_lift + 真实感知退化底座。**叙事以 CPF + rule_lift 打头，不以 abstention 率打头**（后者与 OMD-Bench 重叠）。

## 5. 预期贡献

1. **问题定义**：把不可靠音视频证据下的模型行为定义为 evidence governance（diagnose→recover→route/answer/abstain），区别于普通 missing-modality robustness。
2. **Benchmark protocol**：基于公开音视频 QA，构造受控感知退化样本，附人工核验标签（source 合格性、污染后可答性、可恢复性、oracle route、是否拒答、是否进 headline）。
3. **诊断到行动评测指标**：除 final accuracy 外，给出 diagnosis/recoverability F1、policy action acc、self-inconsistency、false-answer@unanswerable、governed success，**核心为 `conditional_policy_failure` 与 `rule_lift`**。
4. **系统性失败分析**：audio neglect、visual over-trust、无关污染 false alarm、不可恢复仍硬答、route 对答案错、对 corruption artifact 过拟合等错误类型学。

## 6. Benchmark 设计

**两条 track**：Track A 诊断（模态健康/缺陷类型/相关性/可恢复性）；Track B 行动（route / abstain / answer）。评测把二者解耦。

**数据桶**（每个 source 标 modality 角色）：audio-only necessary、video-only necessary、audio-video joint、
irrelevant-corruption control、conflict/temporal-mismatch、clean-hard control。每 source 约 4 条 corrupted instance。

**Corruption 家族**：audio = mute（**有音轨但静音，非删流**）/noise/shift；video = blur/occlusion/low-light/freeze；含 mild/severe。
所有类型保持相同 video+audio 容器（输入契约一致），杜绝"无音轨"成为捷径。generator metadata 仅作 hint。

**标注流程**：source gate（含纯文本 question-only 猜测筛查）→ corrupted-instance review → adjudication（partial/unclear/conflict）→ gold freeze。
partial/unclear 不进 headline 硬打分；冲突/可恢复行优先裁决救回（保证 headline 含足够"非平凡行动"行）。
所有 batch 遵守 `skills/autofusion-annotation/references/data_spec.md`。

## 7. 评测指标

**双 headline**：

```text
conditional_policy_failure (CPF) = P(policy_action_correct=false | triage_diagnosis_right=true)
rule_lift = policy_acc(fixed_rule_on_frozen_diagnosis) - policy_acc(model_action)
```

**完整栈**：parse_success、health/recoverability macro-F1、policy_action_acc、self_inconsistency、
false_answer@unanswerable、false_abstention@answerable、answerable_task_acc、governed_success。

**硬规则**：policy action 正确 ≠ final answer 正确（分开报告）；CPF 报告需分母≥约 30 诊断正确行，否则只作存在性证据。

**对照**：irrelevant-corruption（不应误报）、clean-hard（分离难度与坏证据）、generator-metadata-only baseline（应解不掉）、oracle route/abstention（上限）。

## 8. 实验设计

**模型面板**：首发 `qwen3.5-omni-plus`、`qwen3-omni-flash`；预算允许再加其他 audio-video capable omni-MLLM；`qwen3.x-plus` 仅作 text/video 控制。
记录 token/media consumption、parse success；输入失败单独报告。

**系统行**：① direct answer baseline；② 模型 diagnosis→模型 action；③ 模型 diagnosis（冻结）→ fixed-rule action（出 rule_lift）；④ oracle 上限。

**切分维度**：modality bucket / corruption type / severity / answerability / recoverability / route / model family。

## 9. 数据底座与去风险

详见 `decision/plans/exp-002/2026-06-19-substrate-derisk.zh.md`。核心判断：**不整体换底座**。AVQA（加 question-only 猜测筛查）供单模态桶 + irrelevant 控制；
**DAVE 取样**供 joint/conflict 桶（"两模态都必要"由构造保证）；FortisAVQA / MUSIC-AVQA-v2 作有据备份。

## 10. 分阶段路线与 AAAI-27 时间线

详见 `governance/2026-06-19-aaai27-timeline-and-gates.zh.md` 与 `decision/plans/exp-002/2026-06-19-experiment-plan.zh.md`。

- P0 smoke（已过）→ **P1 mini-pilot gold + scorer（本周 = Gate 1）** → **P2 40-source（Gate 2，~7/6）** → P3 controls+taxonomy → **P4 写作+图（Gate 3，~7/18）→ 7/28 投，7/31 交补充材料/代码** → P5（可选）text-evidence 扩展。
- **质量门决定冲刺 or 转后备**：Gate 1 无清晰信号 → 重设计/转后备；Gate 2 数据未达标 → 转 ICLR 2027；Gate 3 草稿单薄 → 转后备。
- 后备阶梯：ICLR 2027（~9月）→ NeurIPS 2027 Evaluations & Datasets（~明年5月，benchmark 理想归宿）。

## 11. 关键风险与对策

| 风险 | 对策 |
|---|---|
| AVQA 太简单 / 可猜 | source gate + question-only 筛查 + DAVE joint 切片 |
| 人工标签不稳 | partial/unclear 不进 headline + adjudication + 报告一致性 |
| corruption artifact 太明显 | irrelevant-corruption 控制 + 静音轨修复 + generator-metadata baseline |
| mini-pilot n 太小 | CPF 只作存在性证据，数值留到 40-source |
| 新颖性被挤（OMD-Bench 等） | headline 收窄到 CPF + rule_lift；text 扩展不称"首个三模态" |
| 模型接口不稳 | 记录 token/parse，统一 frozen gold，失败单独报告 |
| 赶 deadline 牺牲质量 | 触发质量门即转后备，不硬投（守 Rule 5） |

## 12. 协作与诚信

Decision Team（判断/freeze/审计）＋ Research Execution Team（数据/corruption/标注/跑模型）＋ AI Agent（validator/scorer/审计，不替人 freeze）。
**Vibe Research 六条诚信规则**（见 `governance/2026-06-19-experiment-constitution-v2.zh.md` §5）：AI 仅机械加速；研究判断你拥有；逐行/逐句核验；不伪造引用；不伪造数据；遵守 AAAI AI 披露。
**AAAI 合规**：模型输出属实验内容（允许）；agent 润色你写的正文（允许）；正文你写、引用你查证。

## 13. 成功标准与论文定位

成功 = 在 ≥40 source / ~160 instance、≥2 模型上，观察到**稳定、可解释的 diagnosis-to-action gap**（CPF 有意义且非零，rule_lift≥0，错误类型学清晰），且数据质量与标注一致性达标。

最终定位：

> 一个面向 MLLM 的 evidence governance benchmark：把模型"理解证据不可靠"的能力与"基于该理解正确行动"的能力区分开，并系统测量二者之间的断裂。
