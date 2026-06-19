# AutoFusion-Bench 项目入口

> 面向项目负责人、组会汇报、Research Execution Team 和 AI Agent。
> 打开仓库后先看这个文件；不要从散落文件里猜当前状态。

## 1. 现在这个项目到底在做什么

一句话：

> 我们要做一个 benchmark，评估多模态大模型在音频/视频证据不可靠时，能不能把“证据诊断”转化成“正确行动”。

核心现象叫：

```text
diagnosis-to-action gap
```

中文理解：

> 模型可能知道音频/视频哪里坏了，但接下来仍然选错证据路线、该拒答时硬答、或者没有利用可恢复的健康模态。

当前不要把项目讲成：

- 不是普通多模态刷分；
- 不是新融合模型；
- 不是泛泛的 missing-modality robustness；
- 不是 AVQA-only benchmark。

当前应该讲成：

> evidence governance benchmark：看模型是否能诊断证据、判断可恢复性、选择 route、决定回答或拒答，并且把这些行动和最终答案分开评估。

## 2. 当前实验在哪里

唯一 active experiment：

```text
experiments/exp-002-diag-action-pilot/
```

这个目录里放真正的实验执行材料：

| 想找什么 | 位置 |
|---|---|
| 实验入口说明 | `experiments/exp-002-diag-action-pilot/README.md` |
| 实验运行手册 | `experiments/exp-002-diag-action-pilot/RUNBOOK.md` |
| source / corruption manifest | `experiments/exp-002-diag-action-pilot/data/` |
| 标注表和 gold | `experiments/exp-002-diag-action-pilot/annotations/` |
| 结果和 scorer 输出 | `experiments/exp-002-diag-action-pilot/results/` |
| 脚本 | `experiments/exp-002-diag-action-pilot/scripts/` |
| prompts | `experiments/exp-002-diag-action-pilot/prompts/` |
| 标注网站 | `experiments/exp-002-diag-action-pilot/annotation_app/` |

当前已有：

- 5-source smoke：链路已打通；
- 4-row smoke gold：已跑真实 scorer；
- AVQA 10-source / 40-corrupted 草案：可作为 pipeline/control 资产；
- 但 AVQA 太简单，不再作为主实验底座。

## 3. 当前数据集策略

当前决策：

> AVQA 降级为 pipeline/control；主实验 joint/conflict 样本转向 DAVE。

| 用途 | 数据来源 | 作用 |
|---|---|---|
| 主实验 joint / conflict | DAVE | 找真正需要 audio+video 的样本 |
| 单模态和无关污染控制 | AVQA / AVQA-videos | 测 audio-only、video-only、irrelevant-corruption false alarm |
| 备选 | FortisAVQA、MUSIC-AVQA v2 | 当 DAVE/AVQA 不够时补 |

接下来不要继续做 AVQA-only 主结果。

## 4. 接下来一周做什么

第一周目标：

> 重新建立一个更可靠的 mini-pilot 数据底座，证明样本不是太简单、不是单模态就能答。

具体交付：

| 任务 | 交付 |
|---|---|
| DAVE source screening | 20-30 个候选，筛出 8-10 个 audio-video joint/conflict source |
| AVQA control 保留 | 2-4 个 audio-only / video-only / irrelevant-control source |
| 生成 corruption | 总共约 40-50 条 corrupted instances |
| source gate | 记录 question-only、audio-only、video-only 是否可答 |
| annotation sheet | 给人工审核 answerability、recoverability、route、abstain |
| Gate 1 checklist | 判断第二周是否能正式跑模型 |

第一周不是为了出论文结果，而是为了回答：

> 这个 benchmark 到底是不是在测多模态证据治理，还是只是测一个简单数据集上的噪声鲁棒性？

## 5. 第一周之后做什么

第二周进入 Gate 1 实验：

1. 冻结 mini-pilot gold；
2. 跑 Qwen diagnosis；
3. 跑 Qwen model action；
4. 跑 fixed-rule action；
5. 跑 scorer；
6. 看 CPF、rule_lift、policy accuracy、governed success 和 failure cases。

Gate 1 通过条件：

- 有清晰 diagnosis-to-action failure case；
- `CPF = P(action wrong | diagnosis right)` 有存在性信号；
- `rule_lift >= 0`，或 fixed rule 至少不比模型行动更差；
- 数据没有明显 shortcut；
- gold label 能解释清楚；
- 模型输出可 parse。

如果通过，再扩到：

```text
40 clean source -> 约 160 corrupted instances -> 2-4 个模型 -> 主表 + 错误分析
```

如果不通过，就调整数据/指标/任务，不硬冲 AAAI。

## 6. 我想找某类文件，该去哪

| 我想找 | 看这里 |
|---|---|
| 当前项目快照 | `PROJECT.md` |
| 全仓库索引 | `INDEX.md` |
| 项目宪法 / 规则 | `governance/EXPERIMENT_CONSTITUTION.md` 和 `governance/2026-06-19-experiment-constitution-v2.zh.md` |
| 协作工作流 / 怎么分任务 | `governance/COLLABORATION_WORKFLOW.md` |
| AAAI 时间线 | `governance/2026-06-19-aaai27-timeline-and-gates.zh.md` |
| 详细 proposal | `paper/proposal/2026-06-19-detailed-research-proposal.zh.md` |
| 简版 proposal | `paper/proposal/2026-06-19-evidence-governance-research-proposal.md` |
| 实验总计划 | `decision/plans/exp-002/2026-06-19-experiment-plan.zh.md` |
| 数据底座去风险 | `decision/plans/exp-002/2026-06-19-substrate-derisk.zh.md` |
| gold freeze 规则 | `decision/plans/exp-002/2026-06-19-gold-freeze-adjudication-plan.zh.md` |
| 主表和指标设计 | `paper/tables/2026-06-19-headline-metric-and-main-table.zh.md` |
| related work 定位 | `decision/literature/2026-06-19-related-work-positioning.zh.md` |
| 当前实验执行 | `experiments/exp-002-diag-action-pilot/` |
| 标注网站 | `experiments/exp-002-diag-action-pilot/annotation_app/` |

## 7. 文件夹分工

| 目录 | 放什么 | 不放什么 |
|---|---|---|
| `governance/` | 宪法、工作流、路线图、deadline、仓库规则 | 实验输出、大媒体 |
| `decision/` | Decision Team 的计划、文献定位、专家反馈、handoff、ops notes | 模型 raw output、大视频 |
| `experiments/` | 真实实验的 data、annotations、scripts、results | 论文草稿、历史散文档 |
| `paper/` | proposal、story、tables、论文材料 | 执行任务和媒体 |
| `memory/` | 当前状态恢复入口 | 大量讨论稿 |
| `archive/` | 历史材料 | 当前 active 文件 |
| `external/` | 本地 ignored 外部来料 | GitHub 要审计的正式产物 |

## 8. 组会怎么讲

推荐顺序：

1. 讲一句话目标：我们测 diagnosis-to-action gap；
2. 讲为什么 AVQA-only 不够：太简单，容易 shortcut；
3. 讲新数据策略：DAVE 做 joint/conflict，AVQA 做 control；
4. 讲第一周任务：筛 DAVE、保留 AVQA control、生成 corruption、准备 annotation sheet；
5. 讲第二周 Gate 1：gold freeze、跑模型、跑 scorer；
6. 讲通过后扩展：40 source / 160 instances / 2-4 models；
7. 给每个人分一个可交付任务，所有交付走 GitHub PR / task card。

## 9. 当前最重要的边界

- 不再做 AVQA-only 主实验；
- 不把 smoke 当论文结论；
- 不把 generator metadata 当 gold；
- 不把 partial / unclear 硬塞进 headline；
- 不提交大视频进 GitHub；
- 任何 claim freeze 和 gold freeze 都由 Decision Team 决定；
- 第一周先把数据底座站稳，再谈模型结论。
