# Incoming Handoff Reply: exp-001-semvis-next-step

> Received/pasted by user on 2026-05-15. This is an external-style analysis of the 2026-05-14 exp-001 semantic visual handoff.

根据 2026-05-14 的最新实验交接文档，当前状态可以整理为以下三部分：**实验进度已完成到 protocol validation + 三轮 full feature-level run；实验结果为全流程可跑通但 benchmark signal 未通过；实验结论是 negative-but-diagnostic，不能作为正向 benchmark evidence。**

# 1. 实验进度

## 1.1 当前实验定位

当前实验是 **AutoFusion-Bench / exp-001：decision-surface-pilot**。目标不是提升 MELD 分类性能，而是验证一个 **reliability-budget fusion-template decision surface** 是否能暴露出真实的模板选择差距。

实验假设是：在 `degraded_tight` 条件下，`feasible_oracle` 应该比最佳 single-axis policy 高出至少 **3 macro-F1 points**，且达到 **1.5× pooled standard error**；或者通过 secondary rank signal，即 `Kendall tau-b(clean_loose, degraded_tight) <= 0.3`。

## 1.2 实验设置已完成

当前实验使用 **MELD** 作为首个验证数据集，完整数据规模为：

```text
train: 9989
validation: 1109
test: 2610
```

实验严格限制在 **feature-level**：当前不训练端到端 multimodal encoder，也不能把实验结果表述为端到端部署延迟证据。实验在 `ntu-gpu43` 上执行，硬件环境包含 RTX A5000，但当前 pipeline 主要是 feature producer + sklearn-style template heads。

实验 surface 与模板注册表已经固定：

```text
Reliability regimes:
- clean
- degraded

Budget tiers:
- loose
- tight

Main cells:
- clean_loose
- clean_tight
- degraded_loose
- degraded_tight

Templates:
- T
- A
- V
- TA
- TV
- AV
- TAV

Policies:
- random_legal
- clean_best
- static_full
- budget_only
- reliability_only
- joint
- feasible_oracle
```

## 1.3 已完成三轮 full run

目前已经完成三轮 full empirical feature-level run：

```text
1. raw_stats
2. cv2_stats
3. semvis_clip
```

三轮都生成了六张真实 runner tables：

```text
cost_table.csv
outcome_table.csv
q_policy_map.csv
q_proxy_table.csv
q_diagnostics.csv
corruption_manifest.csv
```

这说明 protocol runner、gate checks、policy evaluator 的基础工程链路已经跑通。当前问题已经不是 plumbing，而是科学解释和下一步实验设计。

## 1.4 最新进度：semvis_clip controlled rerun 已完成

最新一轮是 `semvis_clip`，只替换视觉 producer：

```text
video_source=semvis_clip
semvis_model=openai/clip-vit-base-patch32
semvis_frame_count=8
audio_source=official_concat
seeds=0,1,2
```

处理方式是：每个 utterance video 采样 8 帧，用 frozen CLIP image encoder 编码，L2-normalize 后 mean-pool 成 utterance-level visual vector。没有 supervised visual fine-tuning，也没有 architecture search。

第一次 semvis run 虽然生成了所有表，但 128-row timing profile 不能定义合格的 tight tier，因此被分析阶段拒绝。之后 profiler 改成最多 1024 条 validation rows，并使用 cached CLIP features 重新跑，最终接受的输出路径为：

```text
producer: outputs/meld-producer-semvis-profile1024
analysis: outputs/meld-analysis-semvis-profile1024
```

# 2. 实验结果

## 2.1 三轮 full run 总表

| Run | Text | Audio | Video | Protocol | Benchmark signal | Joint policy | Primary regret | Kendall tau-b | Rank inversion | 判断 |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `raw_stats` | official GloVe | official audio feature | raw MP4 file/stat features | pass | fail | pass | 0.848 | 0.810 | 未强调 | 工程成功，但视觉信号弱 |
| `cv2_stats` | same | `official_concat` | OpenCV decoded stats | pass | fail | pass | 0.740 | 0.619 | 0.190 | budget gate 健康，但 oracle gap 弱 |
| `semvis_clip` | same | `official_concat` | frozen CLIP image embeddings | pass | fail | pass | 1.869 | 0.905 | 0.048 | 语义视觉有帮助，但仍低于 positive threshold |

三轮共同结论是：**protocol pass，joint policy pass，但 benchmark signal fail。** `semvis_clip` 是目前最好的 producer，但 primary regret 仍只有 1.869，低于 3.0 macro-F1 的正结果门槛。

## 2.2 raw_stats 结果

`raw_stats` 使用 raw MP4 file/path/timing-style stats 作为弱视觉特征。结果如下：

```text
protocol_passed=True
benchmark_signal_passed=False
joint_policy_passed=True
best_single_axis_oracle_regret_dt=0.848
best_single_axis_policy=clean_best
pooled_standard_error=0.215
kendall_tau_b_clean_loose_vs_degraded_tight=0.810
joint_gap_closure=1.000
```

该 run 的主要意义是证明 protocol 能跑通，但视觉特征过弱，且 `T` 仍然在 `clean_loose` 和 `degraded_tight` 中非常强。它不能作为 AutoFusion-Bench 的正向结果。

## 2.3 cv2_stats 结果

`cv2_stats` 使用 OpenCV 解码视频统计特征，包括 color、HSV、texture、histogram、motion、metadata 等，并使用 `official_concat` audio。结果如下：

```text
protocol_passed=True
benchmark_signal_passed=False
joint_policy_passed=True
best_single_axis_oracle_regret_dt=0.740
best_single_axis_policy=budget_only
feasible_oracle_degraded_tight_macro_f1=24.550
best_single_axis_degraded_tight_macro_f1=23.810
joint_degraded_tight_macro_f1=24.269
joint_gap_closure=0.620
pooled_standard_error=0.215
kendall_tau_b_clean_loose_vs_degraded_tight=0.619
rank_inversion_index=0.190
```

这一轮的 budget gate 明显好于 raw_stats：

```text
p95 spread=41.887
tight=4.176 ms
loose=10.241 ms
tight legal templates=T|A|V|TV
loose legal templates=T|A|V|TA|TV|AV|TAV
TAV-vs-unimodal p95 ratio=2.336
warnings=[]
```

但 benchmark signal 仍失败，因为 `budget_only=23.810` 已经非常接近 `feasible_oracle=24.550`，oracle gap 只有 0.740。

## 2.4 semvis_clip 结果

`semvis_clip` 是最新、也最有信息量的一轮。它将视频特征从 OpenCV stats 换成 frozen CLIP semantic visual embeddings。结果如下：

```text
protocol_passed=True
benchmark_signal_passed=False
joint_policy_passed=True
best_single_axis_oracle_regret_dt=1.869
best_single_axis_policy=clean_best
feasible_oracle_degraded_tight_macro_f1=25.679
best_single_axis_degraded_tight_macro_f1=23.810
joint_degraded_tight_macro_f1=25.679
joint_gap_closure=1.000
pooled_standard_error=0.215
kendall_tau_b_clean_loose_vs_degraded_tight=0.905
rank_inversion_index=0.048
```

这一轮相对 cv2_stats 有一个实质改善：

```text
primary regret:
cv2_stats    0.740
semvis_clip  1.869
```

但它仍然没有达到 paper-level positive threshold：

```text
required: >= 3.0 macro-F1
observed: 1.869 macro-F1
```

同时，rank signal 也没有变好。`Kendall tau-b=0.905` 很高，`rank_inversion_index=0.048` 很低，说明 `clean_loose` 到 `degraded_tight` 的模板排序没有发生足够强的反转。

## 2.5 semvis_clip 的 budget gate

semvis_clip 的 budget gate 通过了基本 validity gate，但有 caveat：

```text
p95 spread=4.011
tight=18.341 ms
loose=23.033 ms
tight legal templates=T|A|V|TA|TV
loose legal templates=T|A|V|TA|TV|AV|TAV
TAV-vs-unimodal p95 ratio=1.140
warning: preferred TAV-vs-unimodal cost separation not met: 1.140 < 1.250
```

也就是说，它不是 protocol invalid，但 hard-budget story 比 cv2_stats 弱一些。这个 warning 是一个需要报告的限制，但不足以单独推翻这一轮实验。

## 2.6 semvis_clip 的 policy behavior

在 `degraded_tight` 下：

```text
feasible_oracle=25.679
joint=25.679
clean_best=23.810
budget_only=23.810
reliability_only=19.443
static_full=23.810
random_legal=15.770
reliability_only pre_mask_illegal_proposal_rate=0.250
post_mask_budget_violation_rate=0
```

这里有两个关键信号：

第一，`joint` 达到了 `feasible_oracle`，说明 joint policy evaluator 本身能在当前 utility surface 上选到最优合法模板。

第二，`feasible_oracle` 只比最佳 single-axis policy 高 1.869，说明当前 surface 没有形成足够大的 benchmark-level decision gap。

## 2.7 模板均值结果

semvis_clip 在 test 上的 template means：

```text
clean_loose:
  T=34.708
  TV=28.958
  TAV=21.883
  TA=18.765
  V=16.758
  AV=16.250
  A=11.979

degraded_tight:
  T=23.810
  TV=17.176
  TA=13.958
  TAV=13.257
  V=13.158
  AV=11.287
  A=10.746
```

这组结果最重要的含义是：**T 仍然在 clean_loose 和 degraded_tight 中都是第一名。** 这支持 “MELD 在当前 feature-level 设置下 text-dominant” 的解释。

# 3. 实验结论

## 3.1 Protocol validity：通过

当前实验最明确的正向结论是：

```text
exp-001 的 protocol runner、table generation、gate checks、policy evaluator 已经可用。
```

三轮 full run 都生成了六张 runner tables，且 semvis_clip 的主要 gate checks 均为 True：

```text
budget_validity_gate=True
reliability_proxy_boundary_check=True
q_only_task_classifier=True
q_shuffle_control=True
class_stratified_corruption_check=True
post_mask_budget_legality_contract=True
```

因此，**exp-001 没有被 invalidate**。被否定的不是 protocol，而是 “当前 MELD + 当前 producer/degradation 足以产生 positive benchmark signal” 这个版本。

## 3.2 Benchmark-signal interpretation：失败，但有诊断价值

当前不能声称 AutoFusion-Bench 已经在 MELD 上发现 paper-level benchmark evidence。

原因是三轮 full run 均未达到正结果标准：

```text
raw_stats primary regret:   0.848
cv2_stats primary regret:   0.740
semvis_clip primary regret: 1.869

positive threshold: >= 3.0
```

`semvis_clip` 的结果应标注为：

```text
negative-but-diagnostic
```

它说明 semantic vision 确实带来改善，但改善不足以让 MELD 在当前 degradation design 下成为强 benchmark-signal dataset。

## 3.3 Producer/model limitations：语义视觉有用，但不是决定性修复

当前 producer/model 层面的结论是：

```text
raw visual stats 太弱；
cv2_stats 改善了 budget separation，但没有带来足够视觉语义判别；
semvis_clip 带来更高 primary regret，但仍未打破 text dominance。
```

此外，semvis_clip 存在两个 runtime caveats：

```text
1. 有一个 corrupt MELD MP4，producer 使用 zero semantic vector 继续；
2. sklearn logistic heads 在 semantic visual features 下有 convergence warnings。
```

这些 caveat 需要记录，但当前不应过度解释为失败主因。更大的结构性问题仍是：`T` 在 clean 和 degraded 条件下都保持第一。

## 3.4 Scientific conclusion：主要问题是 MELD/text dominance + degradation 不够形成 rank inversion

目前最合理的解释排序是：

| 排名 | 问题来源 | 判断 |
| -: | --- | --- |
| 1 | **MELD 在当前 feature-level 设置下 text-dominant** | 最可能 |
| 2 | **当前 degradation 没有制造足够 modality-specific rank inversion** | 很可能 |
| 3 | **视觉 producer 从 cv2 到 semvis 有提升，但仍不足** | 已验证有帮助，但非充分 |
| 4 | **classifier/head 稳定性有影响** | 可能，但不应先变成 architecture search |
| 5 | **primary metric 太严格** | 对 pilot 不友好，但不应放松为正结果标准 |
| 6 | **budget warning** | caveat，不是 invalidation |

核心证据是：`semvis_clip` 已经增强了视觉语义信息，但 `T` 仍然是 `clean_loose` 和 `degraded_tight` 的最佳模板；同时 `Kendall tau-b=0.905`、`rank_inversion_index=0.048`，说明模板排序基本没有发生强反转。

## 3.5 当前结果不能怎么说

不能这样表述：

```text
MELD 上已经证明 AutoFusion-Bench 能暴露强 reliability-budget decision gap。
```

也不能这样表述：

```text
semvis_clip run 是 positive benchmark evidence。
```

更准确的表述是：

```text
exp-001 已完成 MELD 上的 feature-level protocol validation。
三轮 producer 均通过 protocol 和 joint-policy checks，但均未通过 benchmark-signal 标准。
semantic visual producer 将 primary regret 从 0.740 提升到 1.869，说明视觉语义信息有帮助；
但 T 模板仍然主导 degraded_tight，且 rank inversion 很弱，因此当前 MELD 设置应归类为 negative-but-diagnostic。
```

## 3.6 当前建议结论

建议：

```text
保留 exp-001。
不把当前 MELD raw/cv2/semvis 结果作为 positive result。
3 macro-F1 paper-level threshold 保持不变。
semvis budget warning 作为 caveat 记录，不作为 invalidation。
MELD 最多再做一轮最小诊断性迭代；如果仍失败，就停止把 MELD 作为 primary benchmark-signal dataset。
```

如果要把下一步也写入结论，建议记录为：

```text
Next run:
MELD + semvis_clip + targeted stronger text degradation，
其他设置尽量不动。

Go:
- best_single_axis_oracle_regret_dt >= 3.0
- and >= 1.5x pooled SE
- or Kendall tau-b <= 0.3
- and joint_gap_closure >= 30%
- and post_mask_budget_violation_rate <= 1%

No-go:
- regret 仍 < 3.0
- T 仍在 degraded_tight 中稳定第一
- rank_inversion_index 仍很低
=> 停止 MELD 作为 primary benchmark-signal dataset，转向更非文本主导或更天然多模态依赖的数据集。
```

# 可直接放进记录的精简版

```text
实验进度：
exp-001 已完成 MELD 上的三轮 full feature-level run：raw_stats、cv2_stats、semvis_clip。三轮均生成六张 runner tables，并通过 protocol / gate / policy evaluator 基础链路。最新 semvis_clip 使用 frozen CLIP ViT-B/32，对每个 utterance video 采样 8 帧并 mean-pool 成 visual embedding。当前实验已从工程验证进入 benchmark-signal 判断阶段。

实验结果：
三轮 run 均 protocol pass、joint policy pass，但 benchmark signal fail。raw_stats primary regret=0.848，cv2_stats=0.740，semvis_clip=1.869，均低于 3.0 macro-F1 positive threshold。semvis_clip 相比 cv2_stats 有改善，但 Kendall tau-b=0.905、rank inversion=0.048，说明 clean_loose 到 degraded_tight 的模板排序没有充分反转。degraded_tight 中 T=23.810，仍高于 TV=17.176、TA=13.958、TAV=13.257、V=13.158、AV=11.287、A=10.746。

实验结论：
当前结果是 negative-but-diagnostic。exp-001 protocol 没有失效；失效的是当前 MELD + 当前 producer/degradation 足以产生 positive benchmark signal 的假设。最可能的问题是 MELD/text dominance 和当前 degradation 不足以制造 modality-specific rank inversion。semantic visual features 有帮助，但不足以突破 T 模板主导。当前结果不能作为 AutoFusion-Bench 的正向 benchmark evidence。3 macro-F1 paper-level threshold 应保持不变；semvis budget warning 是 caveat，不是 invalidation。
```
