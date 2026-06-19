# ENACT 核心研究 Proposal

> Status: v1.0 core reference
> Date: 2026-06-19
> Project name: **ENACT**
> Backronym: **EvideNce-to-ACTion**
> Working repository: `AutoFusion-bench`
> Role: 本文件是接下来开展数据构建、标注、模型实验、论文写作和任务下发的核心参考文档。

## 0. 一句话

**ENACT** 要评估的是：

> 当音频/视频证据不可靠时，多模态大模型是否能把自己对证据的诊断付诸正确行动。

英文 tagline：

> Do multimodal LLMs **enact** their own diagnosis of unreliable audio-visual evidence?

核心现象：

```text
diagnosis-to-action gap
```

中文解释：

> 模型可能知道某个模态坏了、证据不足、或者信息需要从另一模态恢复，但它后续仍然选错证据路线、该拒答时硬答，或者没有按自己的诊断行动。

核心指标：

```text
conditional_policy_failure = P(policy_action_correct=false | triage_diagnosis_right=true)
rule_lift = policy_acc(fixed_rule_on_frozen_diagnosis) - policy_acc(model_action)
```

## 1. 研究 Story

### 1.1 现实问题

真实世界里的多模态输入往往不是干净的。音频可能被静音、加噪、错位，或者被无关声音干扰；视频可能被模糊、遮挡、冻结、低光处理，或者和音频不同步。更重要的是，不同问题对模态的依赖不一样：

- 有些问题只需要音频，例如“这个声音来自哪里？”
- 有些问题只需要视频，例如“画面里的人在做什么？”
- 有些问题必须音频和视频一起看，例如“第一个声音是否来自画面中的正确乐器？”
- 有些污染其实和当前问题无关，例如问题只需要视频，但音频被加噪。

所以，一个可靠的多模态系统不应该只追求最后答案。它应该先判断：

1. 哪些证据可靠，哪些证据坏了；
2. 坏掉的证据是否和当前问题相关；
3. 缺失信息能不能从另一模态恢复；
4. 应该使用 audio、video、audio+video，还是拒答；
5. 最终答案是否建立在正确证据路线上。

这就是 ENACT 的 evidence-to-action 研究故事。

### 1.2 现有评测为什么不够

很多已有工作测的是：

> 模态缺失或噪声条件下，最终答案准确率下降多少？

这类评测很有价值，但它容易把不同失败混在一起：

- 模型完全没看懂音频/视频；
- 模型看懂了，但不知道哪个模态可靠；
- 模型知道某个模态坏了，但仍然使用它；
- 模型 route 选对了，但最终任务执行错；
- 模型本应拒答，却硬答；
- 模型答对了，但过程依赖了错误证据。

ENACT 的重点不是单独证明模型“答错了”，而是把失败拆开，专门问：

> 模型诊断正确之后，行动是否也正确？

### 1.3 ENACT 的核心主张

ENACT 的主张是：

> 多模态大模型的可靠性问题不只是感知问题，也是不可靠证据下的行动治理问题。

换句话说，我们要区分两种能力：

| 能力 | 问题 |
|---|---|
| 证据诊断 | 模型是否知道 audio/video 哪个坏了、是否相关、是否可恢复？ |
| 证据行动 | 模型是否基于该诊断正确 route、recover、answer 或 abstain？ |

如果模型诊断对了但行动错了，就是 diagnosis-to-action gap。

### 1.4 为什么叫 ENACT

ENACT 的词义是 “to enact”，即把决定付诸行动。这直接对应本项目的核心问题：

> 模型是否能把自己对证据的诊断付诸正确行动？

Backronym 是：

```text
EvideNce-to-ACTion
```

命名边界：

- 对外名称使用 **ENACT**；
- 仓库名暂时保留 `AutoFusion-bench`，避免投稿前改仓库名带来额外 churn；
- 旧名 AutoFusion-Bench 不再作为论文/benchmark 名，因为它容易被误解为 fusion 方法。

## 2. 研究问题

### RQ1: Diagnosis

给定一个受污染的 audio-video QA 样本，模型能否判断：

- 哪个模态被污染；
- 污染类型是什么；
- 污染严重程度如何；
- 污染是否影响当前问题；
- 当前证据是否足以回答？

### RQ2: Recoverability

当一个模态受损时，模型能否判断：

- 信息是否能从另一个模态恢复；
- 是否其实不需要恢复，因为污染的是无关模态；
- 是否应判定为不可恢复并拒答？

### RQ3: Action

模型能否把诊断转化为正确行动：

- 选择正确 route：audio / video / audio+video；
- 在证据不足时 abstain；
- 在可恢复时使用健康模态；
- 不继续依赖自己刚刚诊断为不可靠的模态；
- 最终答案与所选证据路线一致。

### RQ4: Gap Decomposition

如果模型失败，我们要区分失败发生在哪一层：

- diagnosis wrong；
- diagnosis right but policy action wrong；
- policy action right but final answer wrong；
- should abstain but answered；
- should answer but abstained；
- irrelevant corruption false alarm。

## 3. 预期贡献

ENACT 的贡献不是一个新融合模型，而是一个新的 evaluation protocol。

### C1. 问题定义

定义 **evidence-to-action evaluation**：

```text
unreliable evidence
  -> evidence diagnosis
  -> recoverability judgment
  -> route / answer / abstain
  -> final task result
```

### C2. Benchmark Layer

基于公开音视频问答数据构建 benchmark layer：

- clean source；
- controlled corruption；
- human/adjudicated gold；
- diagnosis/action prompts；
- fixed-rule control；
- scorer。

### C3. 核心指标

除 final accuracy 外，重点报告：

- `conditional_policy_failure`；
- `rule_lift`；
- policy action accuracy；
- false-answer@unanswerable；
- governed success；
- final answer accuracy。

### C4. 失败类型学

系统分析现有 MLLM 在不可靠音视频证据下的失败模式：

- audio neglect；
- visual over-trust；
- irrelevant-corruption false alarm；
- diagnosis correct but route wrong；
- route correct but answer wrong；
- unrecoverable case hard answer；
- corruption artifact shortcut。

## 4. 数据集构建计划

ENACT 不是直接使用一个现成数据集刷指标，而是在公开数据上构建 benchmark layer。

### 4.1 两层数据结构

每条数据分两层：

```text
Clean Source
  -> Corrupted Instance
```

Clean source 包含：

- 原始视频；
- 音频；
- 问题；
- 标准答案；
- source dataset；
- modality role。

Corrupted instance 包含：

- clean source id；
- 污染后媒体；
- corruption modality；
- corruption type；
- severity；
- seed；
- gold annotation。

### 4.2 数据来源策略

当前数据策略：

| 用途 | 数据来源 | 原因 |
|---|---|---|
| 主实验 joint / conflict | DAVE | 更适合找真正需要 audio+video 的样本 |
| 单模态 / 无关污染控制 | AVQA / AVQA-videos | 已有 pipeline 资产，适合 audio-only、video-only、control |
| 备选 | FortisAVQA、MUSIC-AVQA v2 | 若 DAVE/AVQA 不够，再补充 |

重要决策：

> AVQA 不再作为主实验底座。AVQA 太容易出现 shortcut，因此降级为 pipeline/control。

### 4.3 Source Gate

每个 clean source 必须经过筛查：

1. 不看媒体，只看问题/选项，是否能猜出答案；
2. 只听音频，是否能答；
3. 只看视频，是否能答；
4. audio+video 是否确实更可靠；
5. 原始音视频是否清楚；
6. 答案是否唯一；
7. 是否存在常识依赖过强或歧义。

source 标签包括：

```text
audio_only
video_only
audio_video_joint
conflict_candidate
irrelevant_control
clean_hard_control
```

### 4.4 Corruption 设计

每个 source 生成 3-4 个 corrupted instances。

| 类型 | 例子 |
|---|---|
| Audio corruption | audio_mute、audio_noise、audio_shift |
| Video corruption | video_blur、video_occlusion、video_freeze、low_light |
| Cross-modal corruption | temporal_mismatch、audio-video conflict |
| Control corruption | 污染与问题无关的模态 |

硬规则：

- `audio_mute` 必须是有音轨但静音，不是删除音轨；
- 所有 corrupted media 保持 audio+video 容器一致；
- corruption metadata 是 hint，不是 gold；
- 不允许模型靠“没有音轨”这种 artifact 解题。

### 4.5 Human Gold

脚本知道加了什么污染，但不知道污染后应该怎么答。以下字段必须人工审核或裁决：

| 字段 | 含义 |
|---|---|
| `answerability` | 污染后还能不能答 |
| `recoverability` | 能否从另一模态恢复 |
| `preferred_route` | 应该使用 audio / video / audio+video |
| `should_abstain` | 是否应该拒答 |
| `headline_inclusion` | 是否进入主测评 |
| `reason` | 裁决理由 |

## 5. 实验计划

### 5.1 总体阶段

| 阶段 | 时间 | 目标 | 产出 | 决策 |
|---|---|---|---|---|
| P0 Smoke | 已完成 | 打通媒体、标注、模型、scorer | 4-row smoke gold + scorer | 已证明流程能跑 |
| P1 Substrate Gate | 06/19-06/25 | DAVE+AVQA 数据底座重建 | source screening + corruption + annotation sheet | 判断样本是否站得住 |
| P2 Gate 1 | 06/26-07/06 | 跑 mini-pilot 模型实验 | mini gold + diagnosis/action/fixed-rule/scorer | 判断是否扩规模 |
| P3 Paper-scale Pilot | 07/07-07/18 | 40 source / 160 instance | 主表 + 错误分析 | 判断是否冲 AAAI |
| P4 Writing | 07/18-07/28 | 完成投稿稿 | paper + supp + code | 投稿或转后备 |

AAAI-27 官方时间线：摘要 2026-07-21，全文 2026-07-28，补充材料和代码 2026-07-31，均为 UTC-12；会议 2027-02-16 至 2027-02-23，Montréal, Canada。来源：AAAI-27 official page, `https://aaai.org/conference/aaai/aaai-27/`。

### 5.2 第一周：Substrate Gate

第一周的目标不是出模型结果，而是确认数据底座不虚。

交付：

- 20-30 个 DAVE 候选；
- 8-10 个 DAVE joint/conflict source；
- 2-4 个 AVQA control source；
- 约 40-50 条 corrupted instances；
- source screening report；
- corruption manifest；
- annotation sheet；
- Gate 1 checklist。

通过标准：

- 样本不能 question-only 猜出；
- joint/conflict 样本不能只靠单模态完成；
- control 样本能解释其控制作用；
- corruption 不制造明显 artifact shortcut；
- 人工审核任务可执行。

### 5.3 第二周：Gate 1 实验

第二周正式看现象是否存在。

步骤：

1. 冻结 `mini_pilot.gold.jsonl`；
2. 跑 model diagnosis；
3. 跑 model action；
4. 跑 fixed-rule action；
5. 跑 scorer；
6. 输出 failure cases。

通过标准：

- 存在清晰 diagnosis-to-action failure case；
- `CPF` 有存在性信号；
- `rule_lift >= 0` 或 fixed rule 至少不比 model action 更差；
- gold label 能解释；
- 模型输出 parse 稳定；
- 没有明显 shortcut。

### 5.4 论文级 Pilot

若 Gate 1 通过，扩到：

```text
40 clean source
约 160 corrupted instances
2-4 个模型
```

推荐组成：

| 类型 | Clean source | Corrupted instances |
|---|---:|---:|
| DAVE audio-video joint | 16 | 64 |
| DAVE conflict / alignment | 8 | 32 |
| AVQA audio-only | 5 | 20 |
| AVQA video-only | 5 | 20 |
| AVQA irrelevant-control | 4 | 16 |
| clean-hard control | 2 | 8 |
| 合计 | 40 | 160 |

### 5.5 模型面板

首发模型：

- `qwen3.5-omni-plus`；
- `qwen3-omni-flash`。

预算允许再加：

- 其他 audio-video capable MLLM；
- text/video-only 模型只能做控制，不进入 audio-video 主面板。

### 5.6 主表设计

论文主表不以 final accuracy 为唯一中心。

主表列：

| Column | 含义 |
|---|---|
| Model | 模型 |
| Setting | direct / diagnosis→model action / diagnosis→fixed rule / oracle |
| Diagnosis F1 | 诊断是否正确 |
| Policy Acc | route / abstain / recover 行动是否正确 |
| CPF | 诊断对时行动错的概率 |
| Rule Lift | fixed rule 相对 model action 的提升 |
| False Answer | 该拒答时硬答 |
| Governed Success | 诊断、行动、答案整体合理 |
| Final Acc | 最终答案正确率 |

切分表：

- by modality bucket；
- by corruption type；
- by answerability/recoverability；
- by model family。

## 6. 研究边界

### 6.1 不能声称什么

当前不能声称：

- ENACT 是首个 missing-modality benchmark；
- ENACT 是首个 modality diagnosis benchmark；
- ENACT 是首个 cross-modal conflict benchmark；
- ENACT 是首个 abstention benchmark；
- ENACT 提出新融合模型；
- AVQA smoke 结果支持论文结论；
- 4-row 或 10-source 小样本能给出稳定比例结论；
- 我们已经解决三模态 text-audio-video evidence governance。

### 6.2 可以声称什么

在实验完成且数据质量达标后，可以声称：

- ENACT 定义并评估 evidence-to-action gap；
- ENACT 将 diagnosis 与 action 解耦；
- ENACT 使用 CPF 与 rule_lift 衡量“按自己诊断行动”的能力；
- ENACT 在真实同步音视频感知退化下评估模型，而不是只做语义替换或缺失模态；
- ENACT 通过 route / abstain / recoverability / final answer 分解 MLLM 失败模式。

### 6.3 数据边界

- DAVE 是主实验 joint/conflict source；
- AVQA 只做 pipeline/control，不做主结论；
- FortisAVQA、MUSIC-AVQA v2 是备选；
- 所有 source 必须经过 source gate；
- 所有 gold 必须人工审核或裁决；
- generator metadata 只能作为 hint。

### 6.4 实验边界

- 不把模型 parse failure 混入能力结论；
- 不把 route 正确但 answer 错与 route 错混为一类；
- 不把 partial/unclear 样本硬塞进 headline；
- 不把 clean-hard 失败解释成 corruption 失败；
- 不把小样本 CPF 数值写成稳定发现。

### 6.5 仓库与协作边界

- 本地仓库是 Decision Team 工作区；
- 大媒体不进 GitHub；
- 执行任务通过 task card / PR 交付；
- AI Agent 可以准备 validator、scorer、审计和文档，但不能替代人类做 gold freeze 或 claim freeze；
- 任何数据集切换、指标更改、headline inclusion 改动都必须进入 decision note 或 proposal 更新。

### 6.6 伦理与诚信边界

- 不伪造引用；
- 不伪造数据；
- 不把 AI 生成文字当未经核验的论文正文；
- 每个数字可追溯到 scorer 输出；
- 每个 gold label 可追溯到 annotation / adjudication；
- AAAI AI 政策和作者责任必须遵守。

## 7. 工作分工

| 角色 | 负责 |
|---|---|
| Decision Team | 研究判断、gold freeze、claim freeze、最终审计 |
| Research Execution Team | 数据下载、source screening、corruption、标注、模型运行 |
| Human Reviewer | source gate、answerability、recoverability、route、abstain 裁决 |
| AI Agent | task card、validator、scorer、PR 审计、风险样本汇总、文档维护 |
| External Expert | 审核创新性、边界、发表风险 |

## 8. 本文件之后的立即行动

1. 把所有对外文档统一称为 ENACT；
2. 在组会上确认 DAVE 主实验 + AVQA control 的数据策略；
3. 给执行同学下发第一周 source screening task；
4. 产出 DAVE 候选表、source gate 表、corruption manifest；
5. 进入 Gate 1 mini-pilot；
6. 用 Gate 1 决定是否扩到 40-source / 160-instance。

## 9. 必读配套文件

| 文件 | 用途 |
|---|---|
| `START_HERE.zh.md` | 项目负责人入口 |
| `decision/proposals/2026-06-19-naming-decision-ENACT.zh.md` | ENACT 命名决定 |
| `decision/plans/exp-002/2026-06-19-experiment-plan.zh.md` | 实验计划 |
| `decision/plans/exp-002/2026-06-19-substrate-derisk.zh.md` | 数据底座去风险 |
| `paper/tables/2026-06-19-headline-metric-and-main-table.zh.md` | 主表与指标 |
| `decision/literature/2026-06-19-related-work-positioning.zh.md` | 相关工作边界 |
| `governance/2026-06-19-experiment-constitution-v2.zh.md` | 宪法与边界 |
| `governance/COLLABORATION_WORKFLOW.md` | 协作和任务下发 |
| `experiments/exp-002-diag-action-pilot/README.md` | 当前实验入口 |

## 10. 核心判断

ENACT 的成败不取决于数据量是否最大，而取决于：

1. 样本是否真的需要正确的证据治理；
2. gold 是否可靠；
3. 模型是否出现可解释的 diagnosis-to-action gap；
4. CPF / rule_lift 是否能比 final accuracy 提供新信息；
5. 失败案例是否能支撑一个清楚、克制、可 defend 的论文 story。
