# ENACT 项目宪法 v2.0

> Status: v2.0（在 v1.0 基础上演进；v1.0 见 `governance/EXPERIMENT_CONSTITUTION.md`）
> Date: 2026-06-19
> Project name: **ENACT**（working repo: `AutoFusion-bench`）
> 变更动因：本日完成文献核实（OMD-Bench / AVI-Bench 等）、锁定 headline 指标、
> 确定数据底座去风险方案、确定目标 venue（AAAI-27）与质量门、纳入 Vibe Research 诚信规则。
> Scope: 本地仓库、GitHub、服务器执行副本、Drive 媒体包，以及所有人类研究者与 AI Agent。

## 0. 最高约定（沿用 v1.0）

本地仓库是 **Decision Team 工作区**：用于研究判断、方案、实验设计、任务拆解、审计、
gold 冻结、claim 冻结。大规模数据下载 / corruption / 批量标注 / 服务器跑模型默认交给
Research Execution Team。AI Agent 固化流程，但不替人类做 gold 判断与 claim 冻结。
任务与本宪法冲突时，以本宪法为准。

## 1. 研究主线与可辩护内核（v2 收窄）

主线不变：评估 MLLM 在不可靠音视频证据下能否把"证据诊断"转化为"正确行动"
（**diagnosis-to-action gap**）。

v2 明确**唯一不可替代的内核**（文献核实后，别处找不到对应物）：

> 把模型对证据的**诊断**与它基于该诊断的**行动**解耦，用
> `conditional_policy_failure = P(policy_action_correct=false | triage_diagnosis_right=true)`
> 加上"固定规则消费模型自己冻结的诊断"（rule_lift）这一对照来度量二者断裂；
> 污染是真实同步媒体上的**感知退化**（blur/occlusion/noise/mute），非语义替换。

所有对外表述围绕这一条；diagnosis / recoverability / routing / abstention 一律定位为
"行动层所依赖的零件"，不单独宣称首创。

## 2. Claim 边界（v2 更新，依文献核实）

**不能声称**：

- 首个 missing-modality / modality-diagnosis / cross-modal conflict / AV-robustness / abstention benchmark；
- 首个三模态（含 text 证据）证据 benchmark —— **OMD-Bench (2603.27187) 已占该位**；
- 提出了新的多模态融合模型；
- 4-row smoke 或 mini-pilot draft 已支持论文级结论。

**最近邻居与边界**（详见 `decision/literature/2026-06-19-related-work-positioning.zh.md`）：

- OMD-Bench：三模态、语义替换冲突、abstention 校准 + 人工 suffice/abstain 标注。我们的边界 = 感知退化 + recoverability/route 行动层 + CPF/rule_lift（按自己诊断行动），非校准。
- Hidden in Plain Sight (2506.00258)：text/image 的 know-but-not-act，引为现象 motivation。
- AVI-Bench (2606.07643)：能力评测，低威胁，归"广义 AV 评测"桶。

**叙事纪律**：论文以 **CPF + rule_lift 打头，不以 abstention 率打头**（abstention 发现与 OMD-Bench 重叠）。

## 3. Active experiment 与数据底座法（v2 新增底座law）

唯一 active experiment：`experiments/exp-002-diag-action-pilot/`。
当前 scope：audio-video evidence governance under textual queries。

**数据底座法**（应对"AVQA 太简单/可猜"风险，详见 `decision/plans/exp-002/2026-06-19-substrate-derisk.zh.md`）：

- AVQA 供单模态桶 + irrelevant-corruption 控制，但 source gate **必须加纯文本 question-only 猜测筛查**，可猜样本剔除；
- audio-video-joint / conflict 桶应引入 **DAVE 取样**（"两模态都必要"由构造保证）；
- FortisAVQA / MUSIC-AVQA-v2 作有据备份；
- 任何换/补数据集须经 Decision Team 并写入 plan。

## 4. 指标法（v2 强化）

Final answer accuracy 不是唯一主指标。必须分开报告：diagnosis / recoverability /
policy action / abstention / final answer 正确性、self-inconsistency、rule_lift、governed success。

**双 headline 指标**：

```text
conditional_policy_failure = P(policy_action_correct=false | triage_diagnosis_right=true)
rule_lift = policy_acc(fixed_rule_on_frozen_diagnosis) - policy_acc(model_action)
```

新增两条硬规则：

1. **policy action 正确 ≠ final answer 正确**，两类失败分开报告（沿用 v1 C006）。
2. **headline 集必须保留足够"非平凡行动"行**（可跨模态恢复 + conflict），否则 CPF 趋零会给出假 no-go。冲突/可恢复行优先**裁决救回**而非排除。
3. **输入契约一致性**：所有 corruption 类型必须保持相同 video+audio 容器；`audio_mute` = 有音轨但静音（非删音轨），杜绝"无音轨"成为 artifact 捷径。

## 5. Venue 与诚信法（v2 新增）

**目标 venue：AAAI-27 主技术轨**（摘要 2026-07-21、全文 2026-07-28、补充材料和代码 2026-07-31，均为 UTC-12；会议 2027-02 蒙特利尔）。
**策略：主轨为目标 + 明确后备**，用质量门决定冲刺 or 转后备（详见 `governance/2026-06-19-aaai27-timeline-and-gates.zh.md`）。
后备阶梯：ICLR 2027（~9月）→ NeurIPS 2027 Evaluations & Datasets（~明年5月）。

**AAAI AI 政策合规**：LLM 生成正文被禁（除非作为实验分析）；编辑/润色作者本人文字允许；
AI 不能当作者或可引用来源。本项目模型输出属实验内容（允许），agent 润色你写的 prose（允许）。

**Vibe Research 六条诚信规则**（不可协商）：

1. AI 仅做机械加速（检索整理、代码调试、语言润色）。
2. 想法/问题/设计/技术路线/实验方案/核心结论/新颖性必须你拥有且能独立解释。
3. 每段 AI 产物逐行/逐句核验（代码要跑、数字要溯源、文字对照真实结果）。
4. 不伪造引用：每条引用你亲自查到并读过（含 positioning §3 待核实清单）。
5. 不伪造数据/结果/流程，不洗稿。
6. 遵守 venue / 学校 AI 披露规定。

## 6. 角色（沿用 v1.0）

Decision Team（研究判断 / gold·claim freeze / 审计）；Research Execution Team（数据/corruption/标注/服务器跑模型）；
Human Reviewer/Adjudicator（source gate / answerability / recoverability / oracle route / abstention）；
AI Agent（task card / validator / scorer / PR 摘要 / 风险样本 / 审计，**不**替人冻结 gold 或扩 claim）；
External Expert（审 proposal / 标准 / 创新性 / 发表风险）。

## 7. 仓库空间与目录（沿用 v1.0，反映本次重组）

GitHub 只放轻量可审计产物（代码 / manifest / JSONL·CSV / 标注规范 / 审核报告 / scorer 输出 / proposal / governance）。
禁止：大视频、原始数据集压缩包、API key、`.env`、`.venv/`、`node_modules/`、`dist/`、缓存、来源不明的大二进制。
大媒体只放 Drive / 服务器 cache / gitignored 本地 media。

当前目录（本次已重组到位）：`governance/`（宪法/工作流/路线图）、`decision/`（proposals / plans / literature / reviews / handoffs / ops）、
`paper/`（proposal / tables / drafts）、`experiments/exp-002-.../`、`skills/autofusion-annotation/`、`archive/`、`external/`（gitignored）。

## 8. Annotation 与 Gold（沿用 v1.0）

generator metadata 只是 hint，不是 gold。clean source 是否支持答案 / 污染后可答性 / 可恢复性 /
oracle route / 是否拒答 / 是否进 headline，**必须人工 review/adjudication**。
任何 batch 遵守 `skills/autofusion-annotation/references/data_spec.md`。

## 9. 任务下发 / PR / 服务器（沿用 v1.0）

执行任务必须经 Decision Team 转 task card / GitHub Issue（含目标/输入/输出/Drive链接/验证命令/完成标准/禁做项/复核点）。
交付走 PR（含 task card / 改动列表 / 验证结果 / Drive链接 / 未解决项 / 待裁决样本）。merge·gold·claim freeze 由 Decision Team 决定。
服务器清理前先只读审计。

## 10. Stop Conditions（v2 扩充）

遇下列情况暂停：source 不清却当 gold；partial/unclear 硬塞 headline；Drive 与 manifest 对不上；
大视频/API key 将进 Git；执行人擅改任务定义；AI Agent 准备冻结 gold 或扩 claim；本地/GitHub/服务器状态不同步且影响结论；
结论超出样本规模与标注质量；**为赶 AAAI deadline 牺牲数据质量 —— 触发即转后备 venue，不硬投（守 Rule 5）**。

## 11. 当前下一步

1. 回 `decision/plans/exp-002/2026-06-19-gold-freeze-adjudication-plan.zh.md` §5 的 5 个决定；
2. 替换 5 个静音 MP4、冻结 `mini_pilot.gold.jsonl`；
3. 跑 diagnosis / real action / fixed-rule / scorer → Gate 1 判定；
4. 按 AAAI-27 时间线与质量门推进或转后备。
