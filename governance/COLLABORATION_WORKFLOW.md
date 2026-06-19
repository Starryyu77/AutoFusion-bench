# AutoFusion-Bench 协作工作流

> Status: v1.0
> Date: 2026-06-19
> Scope: Decision Team、Research Execution Team、Human Reviewer、AI Agent、External Expert 在 AutoFusion-Bench 项目中的协作流程。

## 1. 工作流总览

本项目采用 **Decision Team -> Task Card -> Execution Team -> PR Delivery -> AI Audit -> Decision Freeze** 的协作模式。

```text
本地讨论 / 研究判断
  -> Decision Team 写清楚任务
  -> GitHub Issue / task card 下发
  -> 研究人员执行数据和实验工作
  -> PR 交付轻量文件 + Drive 媒体链接
  -> AI Agent 做格式、路径、validator、scorer、风险审计
  -> Decision Team 做 gold / claim / next-step 冻结
```

一句话：

> 我们本地负责判断和审计，执行人员负责完成可交付任务，AI Agent 负责把交付变成可检查证据链。

## 2. 每个任务怎么下发

所有任务都必须先变成 task card。task card 可以放在 GitHub Issue、PR 描述、handoff 文件，或聊天中准备好后复制到 GitHub。

### 2.1 标准 task card

````markdown
# [exp-002] <任务名>

## 背景
这项任务为什么存在。只写和当前任务有关的背景。

## 目标
一句话说明要完成什么。

## 输入
- GitHub 分支：
- 需要看的文件：
- Drive 媒体链接：
- 数据集来源：
- 相关 issue / handoff：

## 你要交付什么
- `path/to/output_1`
- `path/to/output_2`
- 问题清单：打不开的媒体、可疑 gold、需要负责人复核的样本。

## 具体步骤
1. ...
2. ...
3. ...

## 必须通过的检查
```bash
python3 experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py --kind annotations <file>
```

## 完成标准
- 输出文件存在；
- validator 通过；
- 媒体路径能对应到 Drive 或本地 media map；
- 不确定样本已标成 review/adjudicate；
- PR 描述写清楚做了什么、没做什么、还卡在哪里。

## 禁止事项
- 不提交大视频到 GitHub；
- 不改研究问题；
- 不改 metric 定义；
- 不把 generator metadata 当 gold；
- 不把 partial / unclear 样本硬标成 headline accept。
````

### 2.2 任务大小

一个任务最好 1-3 天能完成。不要下发“把整个实验做完”这种不可审计任务。

推荐任务粒度：

| 任务 | 研究人员交付 | Decision Team 审核 |
|---|---|---|
| 候选 source 筛查 | candidate CSV、推荐 source、reject reason | 是否符合研究 bucket 和 clean-source gate |
| corruption 生成 | corrupted media、corruption manifest、Drive 链接 | corruption 是否任务相关、是否可审计 |
| 人工标注 | annotator JSONL、uncertainty list | 是否可进入 gold freeze |
| 争议裁决 | adjudication notes、修正后 JSONL | headline rows 是否可 defend |
| 模型运行 | raw outputs、parse report、failed rows | 模型设置是否可比较 |
| scorer | metrics、per-instance result | 指标是否支持 claim |
| 误差分析 | failure cases、risk notes | 是否支持扩展到下一阶段 |

## 3. GitHub 和 Drive 的分工

### 3.1 GitHub 放什么

GitHub 只放轻量、可审计、可 diff 的文件：

- source manifest；
- corruption manifest；
- annotation draft/export/gold；
- CSV 审核表；
- scorer 输出；
- prompts；
- scripts；
- results markdown；
- governance / roadmap / handoff。

### 3.2 Drive 放什么

Drive 放 GitHub 不应该承载的东西：

- clean MP4；
- corrupted MP4；
- 原始数据压缩包；
- 按 source 分包的媒体 zip；
- 专家/执行人员需要下载但不适合进 Git 的大文件。

### 3.3 GitHub 与 Drive 必须互相可追踪

如果 Drive 有媒体包，GitHub 中必须有对应 manifest 或说明，至少能查到：

- `source_id`
- `instance_id`
- 媒体文件名；
- Drive 文件夹或文件链接；
- 当前媒体是否完整；
- 哪个 task / PR 产生了该媒体。

## 4. PR 交付流程

研究人员完成任务后必须开 PR。PR 不只是代码合并请求，也是实验交付单。

### 4.1 PR 描述模板

```markdown
## 任务来源
- Issue / task card:

## 本次交付
-

## 修改文件
-

## Drive 媒体
-

## 自检结果
- validator:
- media check:
- scorer:

## 需要 Decision Team 复核
-

## 明确没有做
-
```

### 4.2 PR 审核顺序

1. **文件边界检查**：没有大视频、API key、`.env`、环境目录；
2. **路径检查**：manifest 中的路径能映射到本地或 Drive；
3. **schema 检查**：JSONL / CSV 能被 validator 读取；
4. **人工语义检查**：source / answerability / recoverability / route 是否合理；
5. **scorer 检查**：accepted rows 能进入 scorer；
6. **claim 检查**：PR 描述没有把草稿结果说成论文结论。

AI Agent 可以负责 1、2、3、5 的初步审计。Decision Team 负责 4、6 和最终 merge 判断。

## 5. 当前 exp-002 的任务链

### Stage A: 40-row corrupted instance 复核

输入：

- `experiments/exp-002-diag-action-pilot/results/mini_pilot_corrupted_instance_review.zh.md`
- `experiments/exp-002-diag-action-pilot/annotations/mini_pilot.corrupted_instance_review.csv`
- Drive mini-pilot media folder

研究人员任务：

- 复看 40 条 corrupted instances；
- 优先处理 partial / oracle-route / unclear；
- 输出 annotator export；
- 列出需要 Decision Team 裁决的样本。

AI Agent 任务：

- 验证 JSONL；
- 合并 annotator export；
- 生成 disagreement/adjudication summary；
- 检查 scorer 需要的字段是否齐全。

Decision Team 任务：

- 冻结 headline rows；
- 生成 `mini_pilot.gold.jsonl`；
- 决定哪些样本只做风险分析，不进主表。

### Stage B: Mini-pilot model run

研究人员任务：

- 在指定环境运行模型；
- 保存 raw outputs；
- 记录失败行、parse error、模型输入限制。

AI Agent 任务：

- 检查 prompt/schema 是否一致；
- 运行 adapter；
- 运行 scorer；
- 生成 metrics 和 per-instance summary。

Decision Team 任务：

- 判断结果是否支持 diagnosis-to-action gap；
- 决定是否扩到 40-source pilot；
- 决定是否调整数据集选择。

### Stage C: 40-source pilot

只有 Stage A/B 通过后才能进入。

进入条件：

- mini-pilot 不是由坏样本主导；
- annotation 标准可执行；
- 模型输出可解析；
- 指标能反映 diagnosis/action 分离；
- Drive/GitHub/服务器文件链路清楚。

## 6. AI Agent 接手协议

AI Agent 每次接手项目时，先读：

1. `AGENTS.md`
2. `governance/EXPERIMENT_CONSTITUTION.md`
3. `governance/COLLABORATION_WORKFLOW.md`
4. `governance/REPOSITORY_STRUCTURE.md`
5. `governance/ROADMAP.md`
6. `memory/tasks/exp-002.md`

如果涉及 annotation，再读：

1. `skills/autofusion-annotation/SKILL.md`
2. `skills/autofusion-annotation/references/data_spec.md`

AI Agent 默认先做只读审计：

```bash
git status --short --branch
git log -1 --oneline
```

然后检查当前任务涉及的 manifest、annotation、results 和 Drive 链接。

AI Agent 可以主动做：

- 生成 task card；
- 生成 PR review checklist；
- JSONL/CSV validation；
- media path resolution；
- scorer；
- metrics summary；
- risk table；
- handoff 文档。

AI Agent 不可以主动做：

- 冻结 gold；
- 改 claim；
- 扩实验规模；
- 改数据集主线；
- 把媒体放 GitHub；
- 删除 server-only 文件；
- 跳过人类复核把 unclear 样本变成 accept。

## 7. Decision Team 本地工作方式

Decision Team 可以在本地做：

- proposal / story / paper outline；
- 专家回复整合；
- task card；
- annotation 标准；
- 小规模 smoke；
- validator/scorer dry run；
- PR 审计；
- gold freeze；
- claim freeze；
- roadmap 更新。

Decision Team 不应在本地长期保留：

- 大视频；
- 原始全量数据集；
- 未索引压缩包；
- 多个实验人员的本地中间产物；
- 不知道来源的 `产物/`、`output/`、`tmp/`。

外部交付进入本地后，必须在一次整理中归入：

- active experiment；
- Drive；
- archive；
- delete candidate。

## 8. 每周监控节奏

每周或每个 PR 合并前更新一次状态表。

| 模块 | 负责人 | 状态 | 当前产物 | blocker | 下一步 |
|---|---|---|---|---|---|
| source review |  | todo / doing / review / frozen |  |  |  |
| corruption |  | todo / doing / review / frozen |  |  |  |
| annotation |  | todo / doing / review / frozen |  |  |  |
| model run |  | todo / doing / review / frozen |  |  |  |
| scorer |  | todo / doing / review / frozen |  |  |  |
| paper story |  | todo / doing / review / frozen |  |  |  |

状态表可以放在：

- GitHub Project / Issue；
- PR 描述；
- `memory/tasks/exp-002.md`。

不要重复维护多套互相冲突的状态表。

## 9. 交付合格标准

一个任务只有同时满足下面条件，才算交付：

- GitHub PR 中有轻量产物；
- Drive 中有媒体或说明；
- manifest 能追踪媒体；
- validator 通过；
- 不确定样本被显式标出；
- PR 描述写明未完成事项；
- AI Agent 审计没有发现结构性问题；
- Decision Team 明确接受或要求修改。

## 10. 最短转发版

给研究人员：

> 我们这边是 Decision Team，负责研究设计、标准制定、gold 冻结和最终审计。你主要负责执行：数据、source 筛选、corruption、标注、模型运行。每个任务会通过 GitHub Issue/task card 给你，里面会写清楚输入、输出路径、Drive 媒体、检查命令和完成标准。你交付时开 PR，只放 manifest、JSON/CSV、审核说明和结果表；视频和大文件放 Drive。不确定样本不要硬判，标成需要复核。

给 AI Agent：

> 先读宪法、工作流、Roadmap 和 `memory/tasks/exp-002.md`。默认本地是 Decision Team 工作区。你的职责是审计、验证、整理和生成任务/结果文件，不要替人类冻结 gold，不要改 claim，不要扩大实验，不要把媒体放进 GitHub。
