# Headline 指标与主表设计（2026-06-19）

> 状态：Decision-Team 草稿。锁定不可替代的 headline 指标和主表形态，
> 让实验服务一条故事，而不是散落的五个分数。与 v1 scorer 字段及
> 筛选/打分指南（Stage C）一致。

## 0. 必须属于我们的那个数

Final-answer accuracy、甚至 diagnosis-F1，都已被已有工作覆盖。
能编码我们贡献、且 2026-06-19 扫描在别处找不到的指标是：

```text
conditional_policy_failure (CPF) = P(policy_action_correct = false | triage_diagnosis_right = true)
```

读作：**在模型已经正确诊断证据的前提下，它仍然行动错误的频率**
（选错 route、该拒答却回答、用了自己刚说坏掉的模态）。
CPF > 0 且分母 n 有意义，就是 diagnosis-to-action gap，浓缩成一个数。

配一个对照指标：

```text
rule_lift = policy_action_accuracy(fixed_rule_on_frozen_diagnosis) - policy_action_accuracy(model_action)
```

`rule_lift > 0` 意味着：一个用模型**自己**诊断的简单固定规则，
胜过模型自己的行动——即瓶颈在"基于诊断行动"，不在"产出诊断"。
就这一个对比，把论文从"又一个坏 AV 数据集"重定位成"模型知道却不行动"。

## 1. 指标栈（全部报告；headline 是 CPF + rule_lift）

| 层 | 指标 | 为什么在这 |
|---|---|---|
| Parse | parse_success_rate | 输入契约/公平性护栏，按模型分 |
| Diagnosis | health_macro_F1, recoverability_macro_F1 | 模型能否*诊断*？（单独不新颖） |
| Action | policy_action_accuracy | 是否选了可接受 route / 正确拒答 |
| **Gap（headline）** | **conditional_policy_failure** | 诊断对了仍行动错 |
| **Gap（headline）** | **rule_lift** | 固定规则用自己诊断 vs 模型行动 |
| Consistency | self_inconsistency_rate | 说 X 坏了，却又 route 到 X / 用 X |
| Safety | false_answer_rate_on_unanswerable | gold=abstain 时却回答 |
| | false_abstention_on_answerable | 可答却拒答（过度谨慎） |
| Outcome | answerable_task_accuracy | 仅在可答行上的最终答案 |
| | governed_success | route 可接受 且（答对 或 正确拒答） |

已定规则（C006）：**policy-action 正确性与 final-answer 正确性分开**——
route 对但答案错属于任务执行失败，不算 diagnosis-to-action 失败。

## 2. 主表形态（mock）

行=系统；列以 gap 打头，而非 accuracy。

| 系统 | Parse | Health F1 | Recov F1 | Policy acc | **CPF ↓** | **rule_lift** | False-ans@unans ↓ | Governed succ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 直接回答（无诊断） | | n/a | n/a | n/a | n/a | n/a | | |
| 模型诊断 → 模型行动 | | | | | **x** | — | | |
| 模型诊断 → 固定规则（对照） | | （同一冻结） | （同一冻结） | | — | **+y** | | |
| Oracle route / oracle abstain（上限） | | 1.0 | 1.0 | 1.0 | 0 | — | 0 | |

故事就在第 2 行与第 3 行之间的差（rule_lift），以及第 2 行非零的 CPF。

## 3. 每行实验必须证明什么（顺序=叙事）

1. Final-answer benchmark 掩盖治理错误 → 直接回答行在可答样本上"看着没事"，但 @unanswerable 失败。
2. 模型存在 diagnosis-to-action gap → 在诊断正确的行上 CPF > 0。
3. 用模型自己诊断的固定规则匹配或胜过模型行动 → rule_lift ≥ 0。
4. abstention / recoverability 是最难的子能力 → recov F1 低、false-answer@unanswerable 高。
5. benchmark 不能被 trivial artifact 检测解掉 → irrelevant-corruption 控制与 clean-hard 控制按设计表现。

## 4. 指标逼出来的两个设计风险

- **分母大小。** CPF 条件在"诊断正确"上，是 headline 行的一个子集。在 mini-pilot
  （约 17 条 headline 候选，多数 trivial）上，CPF 分母可能只有约 3-6 行——出数太小，
  做 go/no-go 够用。把 mini-pilot CPF 当作*存在性证据*（"存在可解释的'诊断对-行动错'样本"），
  把可报告的 CPF 数值留到 40-source / 约 160-instance pilot。目标：报告比率前，分母≥约 30 行诊断正确样本。
- **headline 过于 trivial。** 若 gold 只留"明显 unanswerable→abstain"和单一 route 行，
  CPF 会塌到约 0，给出假 no-go。headline 集必须保留足够的**非平凡行动**行：
  可跨模态恢复 与 conflict 样本。这直接耦合到 gold-freeze 方案：优先*裁决救回*（而非排除）
  conflict 与 recoverable 行。

## 5. 必须随主表一起交付的对照

- irrelevant-corruption 控制（污染答案无关的模态）：模型不应误报/改 route。
- clean-hard 控制（干净但确实难）：把"任务难"和"证据坏"分开。
- generator-metadata 当 baseline：只用 generator metadata 的检测器不应解掉任务 → 证明人工标注带来增量。
- oracle route / oracle abstention：上限行。
