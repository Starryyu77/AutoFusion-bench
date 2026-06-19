# AutoFusion-Bench 实验大致规划（2026-06-19）

> Status: Decision-Team 规划草稿。把实验设计、数据桶、模型面板、指标、对照与 AAAI-27
> 质量门串成一条线。细节指标见 `paper/tables/2026-06-19-headline-metric-and-main-table.zh.md`，
> 底座见 `decision/plans/exp-002/2026-06-19-substrate-derisk.zh.md`，
> gold 流程见 `decision/plans/exp-002/2026-06-19-gold-freeze-adjudication-plan.zh.md`。

## 0. 一句话

用受控的"真实音视频感知退化"样本，测模型能否按自己对证据的诊断正确行动（route/recover/abstain/answer），
核心读数是 `conditional_policy_failure` 与 `rule_lift`。

## 1. 任务结构（两条 track）

- **Track A — Evidence Triage（诊断）**：模态健康状态、缺陷类型、缺陷是否与问题相关、是否可从另一模态恢复。
- **Track B — Decision under constraint（行动）**：选 route（audio / video / audio+video）、是否 abstain、最终答案。

评测把 A 与 B 解耦：A 对但 B 错 = diagnosis-to-action gap。

## 2. 数据桶设计（每个 source 标一个 modality 角色）

| 桶 | 作用 | 主要来源 |
|---|---|---|
| audio-only necessary | 污染音频→应不可答/拒答；污染视频→无影响 | AVQA（gated） |
| video-only necessary | 对称 | AVQA（gated） |
| audio-video joint | 两模态都必要，污染任一→退化 | **DAVE** 取样 |
| irrelevant-corruption control | 污染无关模态→模型不应误报/改 route | AVQA（gated） |
| conflict / temporal-mismatch | 两模态冲突或错位 | DAVE / AVQA 改造 |
| clean-hard control | 干净但难，分离"任务难"与"证据坏" | AVQA（gated） |

每个 source 配约 4 条 corrupted instance（跨 corruption family + severity）。

## 3. Corruption 家族

audio：mute（=静音轨，非删流）、noise（mild/severe）、shift；
video：blur、occlusion、low-light、freeze（mild/severe）。
所有类型保持相同 video+audio 容器（输入契约一致）。generator metadata 仅作 hint。

## 4. 模型面板

- 首发：`qwen3.5-omni-plus`、`qwen3-omni-flash`（已验证 same-instance 音视频）。
- 预算允许再加：其他 audio-video capable omni-MLLM（按可用性与一致输入契约）。
- `qwen3.x-plus` 仅作 text/video 控制，不计入 audio-video 面板。
- 记录 token / media consumption / parse success；输入失败单独报告，不混入能力结论。

## 5. 系统行（主表的行）

1. direct answer（无诊断）baseline；
2. 模型 diagnosis → 模型 action；
3. 模型 diagnosis（冻结）→ fixed-rule action（对照，出 rule_lift）；
4. oracle route / oracle abstention（上限）。

## 6. 指标与对照

headline：CPF + rule_lift；辅助：diagnosis/recoverability F1、policy acc、self-inconsistency、
false-answer@unanswerable、false-abstention@answerable、answerable-task-acc、governed success。
必备对照：irrelevant-corruption、clean-hard、generator-metadata-only baseline、oracle 上限。
切分维度：modality bucket / corruption type / severity / answerability / recoverability / route / model。

## 7. 分阶段路线（对齐 AAAI-27 质量门）

| 阶段 | 目标 | 产出 | Go/No-Go |
|---|---|---|---|
| P0（已完成） | smoke 链路打通 | 4-row gold + scorer 跑通 | 已过 |
| **P1 mini-pilot（本周，Gate 1）** | 冻结 `mini_pilot.gold.jsonl`（10 src/约 21-23 headline）+ 跑 diagnosis/action/fixed-rule/scorer | mini 指标 + failure cases | **存在可解释 gap（CPF>0、rule_lift≥0、清晰失败案例）且数据质量站得住 → 扩；否则重设计/转后备** |
| **P2 40-source（Gate 2，~7/6）** | 40 src / 约 160 instance，桶与 corruption 平衡，≥2 模型，IAA 达标 | 主表 + 标注一致性报告 | **7/6 前数据完备且质量达标 → 锁 AAAI；否则转 ICLR 2027** |
| P3 controls + 错误分析 | 跑齐对照 + 定性 error taxonomy | 控制结果 + taxonomy | 控制行为符合设计 |
| P4 写作 + 图（Gate 3，~7/18） | 全文 + Fig1（gap 示例）+ 主结果图 + pre-submission-reviewer | 投稿稿 | 草稿扎实 → 7/27 投；否则转后备 |
| P5（可选/后续） | text-evidence 扩展（ASR/subtitle/caption） | 与 OMD-Bench 区分（退化 vs 替换） | 仅在主线跑通后 |

## 8. 标注与质量

source gate（含 question-only 猜测筛查）→ corrupted-instance review（answerability/recoverability/oracle route/abstain）→
adjudication（partial/unclear/conflict）→ gold freeze。partial/unclear 不进 headline 硬打分；冲突/可恢复行优先裁决救回。
关键样本做多标注 + adjudication，报告 disagreement。

## 9. 主要风险与对策（摘要）

- AVQA 太简单 → source gate + DAVE joint 切片（§2、底座文档）。
- 标注不稳 → partial 不进 headline + adjudication + 报告一致性。
- artifact 捷径 → irrelevant-corruption 控制 + 静音轨修复 + generator-metadata baseline。
- mini-pilot n 太小 → CPF 只作存在性证据，数值留到 40-source。
- 新颖性被挤 → headline 收窄到 CPF + rule_lift（见宪法 §1-2）。

## 10. 立即下一步

P1 卡在 gold freeze：回 gold-freeze 方案 §5 的 5 个决定 → 替换静音 MP4 → 冻结 gold → 跑 scorer → Gate 1 判定。
