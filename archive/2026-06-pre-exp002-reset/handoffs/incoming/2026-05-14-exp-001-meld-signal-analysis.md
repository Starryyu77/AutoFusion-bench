# Incoming Reply: exp-001 MELD signal analysis

Source: external analysis pasted by user on 2026-05-14.

## Verbatim reply

根据 2026-05-14 的 exp-001 handoff 文档，我的判断是：**不要把当前 MELD cv2 run 当正结果；但 exp-001 还不该停止。下一轮应该只改 producer，优先换成冻结语义视觉特征，而不是先改 metric 或放宽阈值。**

## 结论：问题最可能出在“当前 MELD producer + text dominance”，其次是 degradation 不够硬，不是 protocol 崩了

当前证据很清楚：两个 full run 都 **protocol pass / benchmark signal fail / joint policy pass**，raw-stats regret=0.848，cv2-stats regret=0.740，均显著低于 3 macro-F1 目标；small-sample smoke 的 3.420 没有在 full run 上复现，所以不能当证据。

我会按可能性这样排序：

| 排名 | 可能原因 | 判断 |
| -: | --- | --- |
| 1 | **MELD + 当前特征组合过度 text-dominant** | 最可能 |
| 2 | **cv2_stats 视觉 producer 语义太弱** | 同样很可能，且更容易先验证 |
| 3 | **degradation 设计没有造成足够 rank inversion** | 很可能，但不应先动 |
| 4 | **primary metric 本身太粗/太严格** | 有影响，但不是第一嫌疑 |
| 5 | audio producer 弱 | 可能，但优先级低于视觉 |

关键证据是 cv2 run 已经让 budget gate 变得健康：p95 spread=41.887，tight=4.176ms，loose=10.241ms，tight 只允许 `T|A|V|TV`，TAV-vs-unimodal p95 ratio=2.336，且 warnings=[]。也就是说，**成本面已经有有效差异**；但 feasible oracle 在 `degraded_tight` 只到 24.550，best single-axis `budget_only` 已到 23.810，差距只有 0.740。

这说明不是“预算约束没生效”。问题是：**合法模板之间的效用排序没有被 degradation 拉开**。换句话说，surface 有了，但 surface 上没有足够大的决策坑。

## 1. 负结果更像哪类问题？

**主要不是 metric 失败，而是当前 producer 没制造出足够的模态互补性。**

cv2 run 的 `reliability_only` 在 `degraded_tight` 下很差，只有 15.302，而且有 `pre_mask_illegal_proposal_rate=0.500`；这说明 reliability-only 的盲点确实被暴露了。可是 `budget_only` 已经达到 23.810，离 feasible oracle 的 24.550 很近。

这意味着当前 full run 的真实结构是：

```text
budget-only 已经足够接近 oracle
joint 有提升，但不是 benchmark-level gap
reliability-only 明显失败
clean/static 也失败
```

所以 benchmark 不是完全没信号；它有 policy-diagnostic signal。但它没有达到你定义的 **benchmark-signal positive**：即 oracle 相对最佳 single-axis policy 的大 regret。

我会把原因拆成两个层面：

**第一层：MELD/text dominance。** raw-stats run 的 template mean 显示，`T` 在 clean_loose 是 34.708，在 degraded_tight 仍是 23.810；`TV` 是第二强，但 degraded_tight 只有 19.439；`A/V/AV` 明显弱。也就是说，文本单模态已经很强，非文本模态没有形成足够替代价值。

**第二层：cv2_stats 没有提供语义视觉信息。** cv2_stats 提供的是颜色、HSV、纹理、histogram、motion、metadata 等统计特征；这些能扩大 cost spread，但不一定能捕捉情绪、人物表情、语境或行为。文档本身也指出：cv2_stats “adds measurable budget spread but not useful visual discrimination”。

因此我不会先怪 metric。metric 现在做的事情是合理的：只有当 reliability-budget 条件导致模板排序明显反转时，它才给出正信号。当前 `kendall_tau_b=0.619`、`rank_inversion_index=0.190`，说明 rank inversion 不够强。

## 2. 是否 invalidate exp-001？

**不 invalidate exp-001。invalidate 的是“当前 MELD raw/cv2 producer 足以产生 paper-level benchmark signal”这个版本。**

理由：

第一，实验 contract 本身跑通了。数据、cost table、outcome table、q_policy_map、q_proxy_table、q_diagnostics、corruption_manifest 都生成了；cv2 run 的 gate checks 包括 budget validity、reliability proxy boundary、q-only task classifier、q shuffle control、class-stratified corruption、post-mask legality 都为 True。

第二，policy behavior 不是全平的。`reliability_only`、`clean_best/static_full`、`random_legal` 在 degraded_tight 下都有明显差异；只是最佳 single-axis `budget_only` 太接近 oracle。

第三，small-sample smoke 给过 positive signal，但 full run 不复现。这更像是小样本方差或子集偶然 rank inversion，而不是整体 formalism 被推翻。

所以我的 go/no-go 是：

```text
GO: 继续 exp-001。
NO-GO: 不继续当前 cv2_stats/raw_stats producer 作为正结果路线。
NO-GO: 不改 claim，不放宽成“已发现 benchmark gap”。
```

## 3. 最有信息量的下一 run 是什么？

**下一 run：换成冻结语义视觉 producer，其他全部不动。**

不要先换 dataset，不要先改 metric，不要先做更硬 corruption。原因是你现在最需要区分的是：

```text
是 cv2_stats 太弱？
还是 MELD 本身太 text-dominant？
还是 degradation/metric 设计不对？
```

只替换视觉 producer 是最小且诊断性最强的动作。具体标准如下：

```text
保持：
- MELD split
- 7 templates: T/A/V/TA/TV/AV/TAV
- 2x2 reliability-budget surface
- policies
- seeds=3
- degradation manifest
- primary metric
- budget legality contract

只替换：
- video=cv2_stats
改为：
- video=frozen semantic visual embeddings
```

建议用 **frame-level frozen CLIP/ViT 或 VideoMAE 类 embedding，utterance-level mean/attention-free pooling**。这仍然是 feature-level，不是 end-to-end MELD encoder training。成本 profiling 需要明确标成 **feature extraction cost** 或 **cached-feature decision cost**，不能混成 deployment latency claim。

判读逻辑很简单：

| 新 run 结果 | 结论 |
| --- | --- |
| primary regret 上升到接近/超过 3，Kendall tau 下降，rank inversion 上升 | 之前主要是 visual producer 弱 |
| V/TV/AV/TAV 有提升，但 regret 仍 <3，T 仍统治 degraded_tight | MELD/text dominance 是主因 |
| 语义视觉增强后仍无 rank inversion，且 targeted corruption 前后差异不大 | 再怀疑 degradation 设计或 dataset |
| budget-only 仍贴近 oracle，但 joint/oracle surface 有稳定分层 | primary metric 可能需要 pairing，而不是替换 |

这一步比“直接换数据集”更好，因为它保留最大可比性；比“先改 corruption”更好，因为当前的非文本模态还不够强，硬 corruption 可能只会把实验变成“text ablation stress test”，不能证明 fusion decision surface；比“先改 metric”更好，因为 metric 在当前结果下并没有明显坏掉。

## 4. 3 macro-F1 阈值该不该放松？

**paper-level positive threshold 保持 3 macro-F1，不要放松。pilot triage 可以新增一个二级诊断门槛，但不能替代主门槛。**

当前 cv2 run 的 0.740 macro-F1 虽然超过 1.5×SE：0.740 / 0.215 ≈ 3.44，但绝对效应太小，不能支撑“benchmark exposes a meaningful decision gap”的主 claim。文档原始 hypothesis 要求 `>=3 macro-F1` 且 `>=1.5x pooled SE`，或者 Kendall tau-b <=0.3；当前 cv2 的 Kendall tau-b=0.619，也没有过 secondary route。

我建议这样处理：

```text
Primary positive:
- best_single_axis_oracle_regret_dt >= 3.0
- and >= 1.5x pooled SE
保持不变。

Pilot triage signal:
- regret >= 1.0
- or Kendall tau-b <= 0.5
- or rank_inversion_index >= 0.30
- plus joint_gap_closure >= 30%
仅用于决定是否继续同一路线，不用于 positive claim。
```

也就是说，**3-F1 不放松为正结果标准；但可以新增 triage label**：

```text
positive
negative-but-diagnostic
negative-and-uninformative
```

当前 cv2 run 应归类为：

```text
negative-but-diagnostic
```

因为 gates pass、joint pass、policy differences 存在，但主 benchmark signal fail。

## 5. 我会做的一个最小修改

**唯一修改：把 `cv2_stats` 替换为冻结语义视觉 embedding producer。**

精确定义如下：

```text
exp-001-meld-semvis-v1

Text:
- unchanged: official text_glove_average_emotion.pkl

Audio:
- unchanged: official_concat
  audio_embeddings_feature_selection_emotion.pkl + audio_emotion.pkl

Video:
- replace cv2_stats with frozen semantic visual embedding
- sample K frames per utterance video, e.g. 8 or 16
- encode each frame with a frozen image/video encoder
- aggregate to one utterance-level vector by mean pooling
- no supervised visual fine-tuning
- no architecture search
- keep same sklearn-style template heads

Protocol:
- same splits: train 9989 / validation 1109 / test 2610
- same 7 templates
- same degradation manifest initially
- same policies
- same seeds
- same success criteria

Report:
- template means per condition
- degraded_tight oracle vs best single-axis
- Kendall tau-b clean_loose vs degraded_tight
- rank_inversion_index
- budget legal set
- whether TV/AV/TAV become meaningfully competitive
```

为什么这一步最小：它只动一个 producer，不动 benchmark formalism，不动 policy set，不动 metric，不动 dataset。
为什么它最有信息量：如果 semantic V 仍然不能让 `TV/AV/TAV` 在 degraded slices 里变得有用，那基本可以判定 MELD/text dominance 或 degradation design 是主问题；如果它能明显增加 rank inversion，那就说明当前失败主要是 producer weakness。

## 具体决策建议

我的建议是：

```text
GO for one more exp-001 iteration.
Route: MELD + frozen semantic visual features.
Do not claim current cv2 run positive.
Do not relax 3-F1 primary threshold.
Do not switch dataset yet.
Do not change primary metric yet.
Do not harden corruption before proving non-text modalities are semantically useful.
```

下一轮结束后的分叉规则：

```text
Case A:
semantic visual run regret >= 3.0 and Kendall tau improves/downshifts
=> exp-001 has positive MELD feature-level result.

Case B:
semantic visual run regret 1.0-3.0, rank inversion improves, joint remains strong
=> keep MELD as diagnostic; consider paired primary signal, but still no positive claim.

Case C:
semantic visual run regret <1.0, budget-only still near oracle, T remains dominant
=> stop MELD as primary benchmark-signal dataset; move to a less text-dominant dataset or create targeted text-degradation stress test.

Case D:
semantic visual improves V/TV/AV but oracle gap still small because budget-only tracks oracle
=> then inspect metric design; specifically whether feasible oracle and budget_only share too much validation utility information.
```

Bottom line: **当前问题最可能在 producer/dataset interaction，不在 exp-001 protocol。下一步不是“调阈值”或“换理论”，而是跑一个冻结语义视觉 producer 的 controlled rerun。**
