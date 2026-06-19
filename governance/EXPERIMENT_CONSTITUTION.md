# AutoFusion-Bench 必须遵守的项目宪法

> Status: v1.0
> Date: 2026-06-19
> Scope: AutoFusion-Bench 本地仓库、GitHub 仓库、服务器执行副本、Google Drive 媒体包，以及参与该项目的人类研究人员和 AI Agent。

## 0. 最高约定

本地仓库的角色是 **Decision Team 工作区**。

这意味着：

- 本地主要用于研究判断、方案讨论、实验设计、任务拆解、文档审计、gold 冻结、论文 claim 决策；
- 本地可以做小规模 smoke、格式验证、scorer 验证和最终审计；
- 本地不作为大规模实验执行区，不作为数据集堆场，不作为临时媒体仓库；
- 具体实验执行、数据下载、数据筛选、corruption 生成、批量标注和服务器运行，默认交给 Research Execution Team 完成；
- AI Agent 负责把决策、任务、审核、验证和交付流程固化成文件，但不能替代人类做关键 gold 判断和论文 claim 冻结。

如果后续任务和这条约定冲突，以本宪法为准。

## 1. 当前研究主线

当前项目主线是：

> 构建一个评估多模态大模型在不可靠音视频证据下，是否能把“证据诊断”转化为“正确行动”的 benchmark / evaluation protocol。

当前核心假设是：

> 多模态大模型可能能诊断出证据有问题，但不一定能据此正确选择证据路线、回答、恢复或拒答。

这个现象称为 **diagnosis-to-action gap**。

## 2. Claim 边界

现在不能声称：

- 我们是第一个 missing-modality benchmark；
- 我们是第一个 modality diagnosis benchmark；
- 我们是第一个 cross-modal conflict benchmark；
- 我们提出了新的多模态融合模型；
- 4-row smoke 或 10-source mini-pilot draft 已经支持论文级结论。

在足够证据后，可以声称：

- 我们把 unreliable evidence governance 定义为 diagnosis-to-action protocol；
- 我们拆分评估 evidence diagnosis、policy action、abstention 和 final answer；
- 我们测试模型是否能按照自己的诊断采取一致行动；
- 我们分析受控音视频证据损坏下的 diagnosis-to-action failure。

## 3. 当前 active experiment

唯一 active experiment 是：

```text
experiments/exp-002-diag-action-pilot/
```

当前 scope：

- audio-video evidence governance under textual queries；
- AVQA / AVQA-videos 优先；
- MUSIC-AVQA / MUSIC-AVQA v2.0 / FortisAVQA 仅作为补充候选；
- MELD / CMU-MOSI / CMU-MOSEI / IEMOCAP 不作为本轮主数据；
- 当前 mini-pilot 是 10 clean source + 40 corrupted instances；
- 下一阶段目标是 40 clean source + about 160 scored instances。

任何新实验、换数据集、扩规模、换主 claim，都必须先经过 Decision Team 讨论并写入 Roadmap 或 decision note。

## 4. 项目角色

| 角色 | 允许做什么 | 不允许做什么 |
|---|---|---|
| Decision Team | 研究判断、任务拆解、标准制定、gold freeze、claim freeze、最终审计 | 把本地变成大规模实验运行区或媒体堆场 |
| Research Execution Team | 数据下载、source 筛选、corruption、批量标注、服务器模型运行、初步结果记录 | 擅自改研究问题、指标、gold 标准或 headline inclusion 规则 |
| Human Reviewer / Adjudicator | 审核 source gate、answerability、recoverability、oracle route、abstention | 把不确定样本硬标成 accept |
| AI Agent | 任务卡、文件整理、validator、scorer、PR 摘要、风险样本汇总、审计报告 | 替代人类冻结 gold、扩大 claim、把大媒体放进 Git |
| External Expert | 审核 proposal、实验标准、创新性和发表风险 | 代替日常执行人员做数据清洗 |

## 5. 仓库空间规则

GitHub 仓库只放可审计的轻量产物。

允许放入 GitHub：

- 代码和脚本；
- manifest；
- JSONL / CSV；
- 标注规范；
- 审核报告；
- scorer 输出；
- 论文故事和 proposal；
- governance / roadmap / memory。

禁止放入 GitHub：

- 大视频；
- 原始数据集压缩包；
- API key；
- `.env`；
- `.venv/`；
- `node_modules/`；
- `dist/`；
- 临时缓存；
- 未说明来源的大型二进制文件。

大媒体和原始包只能放：

- Google Drive；
- 服务器 dataset cache；
- 被 `.gitignore` 排除的本地 media/raw handoff 目录。

## 6. 目录职责

当前目录应按下面方式理解和维护：

| 路径 | 角色 |
|---|---|
| `governance/` | 宪法、工作流、路线图、仓库审计，是项目规则入口 |
| `decision/` | Decision Team 的 proposal、plan、review、literature、handoff、ops notes |
| `memory/tasks/exp-002.md` | 当前状态、恢复入口、下一步 gate |
| `experiments/exp-002-diag-action-pilot/` | 当前唯一 active experiment |
| `paper/` | 当前论文故事、proposal、表格设计、草稿和 claim 组织 |
| `skills/autofusion-annotation/` | annotation workflow 的可复用规范和数据 contract |
| `archive/` | 历史有价值但不在当前执行路径的材料 |
| `external/` | 本地 ignored 外部材料入口，不进入 GitHub |

顶层不得继续堆放临时“产物”目录。外部发来的材料要先进入被忽略的 raw handoff 区，再按本宪法整理进 active experiment 或 Drive。

## 7. Annotation 和 Gold Label 规则

generator metadata 只是 hint，不是 gold。

脚本可以知道：

- 哪个模态被加噪；
- 哪段时间被遮挡；
- corruption 类型和 severity；
- 文件路径和 seed。

脚本不能决定：

- clean source 是否真的支持 gold answer；
- corruption 后是否还能回答；
- 是否能从另一个模态恢复；
- oracle route 应该是什么；
- 是否应该拒答；
- 是否进入 headline scoring。

这些必须由 human review / adjudication 决定。

任何 annotation batch 必须遵守：

```text
skills/autofusion-annotation/references/data_spec.md
```

## 8. 指标规则

Final answer accuracy 不是唯一主指标，也不能单独支撑论文 story。

必须分开评估：

- diagnosis correctness；
- recoverability correctness；
- policy action correctness；
- abstention correctness；
- final answer correctness；
- self-inconsistency；
- rule lift；
- governed success。

核心指标包括：

```text
conditional_policy_failure = P(policy_action_correct=false | triage_diagnosis_right=true)
```

policy action 正确但 final answer 错，和 policy action 本身错，是两类不同失败，不能混在一起。

## 9. 任务下发规则

所有执行任务必须由 Decision Team 转成 task card 或 GitHub Issue。

任务卡必须说明：

- 目标；
- 输入；
- 输出路径；
- Drive 媒体链接；
- 验证命令；
- 完成标准；
- 不要做什么；
- 需要负责人复核的情况。

没有 task card 的实验执行，不进入主线。

## 10. PR 和审计规则

研究人员交付必须走 PR。

PR 必须包含：

- 对应 task card / issue；
- 修改文件列表；
- 验证命令和结果；
- Drive 媒体链接；
- 未解决问题；
- 需要 Decision Team 裁决的样本或 claim。

AI Agent 可以帮助审计 PR，但最终 merge / gold freeze / claim freeze 必须由 Decision Team 决定。

## 11. Server 规则

服务器是 Execution Team 的运行环境，不是无索引文件仓库。

服务器目录也必须遵守：

- active repo checkout；
- dataset cache outside Git；
- experiment-local outputs；
- old runs archive root；
- no duplicated stale repo copies without index。

服务器清理前必须先做只读审计：

- git status；
- 当前 HEAD；
- 空间热点；
- server-only 文件；
- 数据集 cache 位置；
- 是否有未同步结果。

## 12. Stop Conditions

遇到以下情况必须暂停推进：

- source 本身不清楚，却被当成 gold；
- annotation 中 partial / unclear 被硬塞进 headline；
- Drive 媒体和 GitHub manifest 对不上；
- 大视频或 API key 准备进入 Git；
- 执行人员改变了任务定义但没有通过 Decision Team；
- AI Agent 准备冻结 gold 或扩大 claim；
- 本地/GitHub/服务器状态不同步且影响当前结论；
- 实验结论超过样本规模和标注质量能支持的范围。

## 13. 当前下一步

当前项目应先完成：

1. 按本宪法整理 GitHub 工作区；
2. 用 `governance/COLLABORATION_WORKFLOW.md` 下发 40-row corrupted instance 复核任务；
3. 冻结 `mini_pilot.gold.jsonl`；
4. 跑 mini-pilot model + scorer；
5. 由 Decision Team 判断是否扩展到 40-source pilot。
