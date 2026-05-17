# exp-001 组会交接文档

> 生成时间：2026-05-15。用途：组会沟通、任务交接、后续实验讨论。

## 0. 先说结论

我们已经把 AutoFusion-Bench 的第一个 pilot 实验 `exp-001` 跑到了端到端可复现状态。MELD 数据、特征生成、六张输入表、预算检查、泄漏检查、策略评估、远端运行路径都已经打通。

但当前结果不能作为主正结果。默认 MELD 路线是 `negative-but-diagnostic`：它说明协议能跑、问题能被诊断，但没有产生足够强的 benchmark signal。最后一轮 `text_stress` 诊断确实制造了明显的模板排序反转，但主指标的效用差距仍然很小。

最准确的结论是：

```text
exp-001 验证了 feature-level reliability-budget protocol 是可执行的。
MELD 可以作为 protocol validation / diagnostic case。
MELD 当前不适合作为 AutoFusion-Bench 的主 paper-level positive evidence。
下一步应该停止继续调 MELD，转向更非文本主导、天然更依赖多模态的数据集。
```

## 1. 这个实验在做什么

项目目标不是单纯提高 MELD 分类分数。我们真正关心的是一个 benchmark 问题：

```text
当输入模态可靠性变化，并且推理预算有限时，
不同 fusion template 的选择是否会出现可测、可解释、可复现的差异？
```

也就是说，我们要验证：只看干净数据表现、只看预算、只看可靠性、或者固定使用某个融合模板，这些策略在某些场景下会不会明显不如“预算内最优可行模板”。

如果这个差距足够大，就说明 AutoFusion-Bench 的 reliability-budget decision surface 是有意义的。

## 2. 为什么先做 exp-001

完整 benchmark 会很大：多个数据集、多个可靠性等级、多个预算等级、更多融合模板。我们没有一开始就跑完整版本，而是先做一个最小但有解释力的 pilot。

`exp-001` 的定位是：

```text
实验名：decision-surface-pilot
数据集：MELD
层级：feature-level
目标：验证 2x2 reliability-budget surface 是否能产生模板选择信号
```

这一步的目标是回答：

1. 表结构和 runner 能不能跑通；
2. 预算是否合法能不能只由 cost table 决定；
3. degradation 是否真的改变模板排序；
4. feasible oracle 是否明显超过最佳 single-axis policy；
5. joint policy 能不能在不看 test outcome 的前提下接近 oracle。

它不是最终论文完整实验，也不是端到端部署延迟实验。

## 3. 当前实验设置

### 3.1 数据集

当前使用 MELD，完整规模是：

```text
train: 9989
validation: 1109
test: 2610
```

远端位置：

```text
服务器：ntu-gpu43
仓库：/usr1/home/s125mdg43_10/projects/AutoFusion-bench
数据：/usr1/home/s125mdg43_10/datasets/MELD
```

MELD 官方特征包里有文本和音频特征，但没有直接可用的视觉特征。因此我们实现了几版视觉 producer：`raw_stats`、`cv2_stats`、`semvis_clip`。

### 3.2 重要边界：当前只是 feature-level

当前实验只在 feature-level 上做模板选择评估：

- 不训练端到端多模态 encoder；
- 不声称端到端部署延迟；
- 预算表测的是缓存特征后的 template head 推理开销；
- 视觉语义特征来自 frozen CLIP；
- 模板分类头是 sklearn 风格的 logistic classifier。

这个边界非常重要。组会里如果有人问“这是不是部署 latency”，答案是：不是。当前只能说是 feature-level template-routing budget。

### 3.3 可靠性和预算格子

主实验是 2x2：

```text
clean_loose
clean_tight
degraded_loose
degraded_tight
```

`clean` 只有一个 slice：

```text
clean
```

`degraded` 内部有四个 slice：

```text
degraded_text
degraded_audio
degraded_video
mixed_degraded
```

这样做是为了避免只做“整体加噪”，而是让每个模态都可能成为低可靠模态，从而测试模板选择是否真的需要变化。

### 3.4 模板注册表

固定 7 个模板：

```text
T
A
V
TA
TV
AV
TAV
```

这里的 `T/A/V` 分别是文本、音频、视频。`TA/TV/AV/TAV` 是对应模态组合。

我们没有引入复杂 cross-attention 或更大的模型，因为当前实验目标不是架构搜索，而是验证 benchmark protocol。

### 3.5 策略列表

当前评估 7 类策略：

```text
random_legal
clean_best
static_full
budget_only
reliability_only
joint
feasible_oracle
```

含义如下：

| 策略 | 含义 |
|---|---|
| `random_legal` | 在当前预算允许的模板里随机选 |
| `clean_best` | 在 clean-loose validation 上选最优模板，测试时固定用 |
| `static_full` | 优先用 `TAV`，如果 tight 下非法就 fallback |
| `budget_only` | 只看预算合法集合，不使用可靠性信息 |
| `reliability_only` | 根据可靠性先提出模板，不先看预算；如果非法再 fallback |
| `joint` | 同时看可靠性和预算合法集合，只用 train/validation 信息 |
| `feasible_oracle` | 事后上界，只用于分析，不是可部署策略 |

## 4. 主指标怎么定义

主指标看 degraded-tight 下，feasible oracle 比最佳 single-axis policy 高多少：

```text
best_single_axis_oracle_regret_dt =
  Utility(feasible_oracle, degraded_tight)
  - max Utility(policy, degraded_tight)
    over {clean_best, static_full, budget_only, reliability_only}
```

正结果门槛是：

```text
>= 3.0 macro-F1 points
并且 >= 1.5 x pooled standard error
```

还有一个辅助排序信号：

```text
Kendall tau-b(clean_loose, degraded_tight) <= 0.3
```

解释结果时必须区分四件事：

| 类型 | 含义 |
|---|---|
| protocol pass | 协议、表、gate、runner 能跑通 |
| joint policy pass | joint policy 表现满足参考标准 |
| primary regret positive | oracle 对最佳单轴策略有足够 macro-F1 差距 |
| rank-signal positive | clean 到 degraded 的模板排序发生明显反转 |

这四个不能混为一谈。

## 5. 已实现的工程链路

核心代码：

```text
autofusion_bench/exp001/run_decision_surface_pilot.py
autofusion_bench/exp001/run_meld_table_producer.py
autofusion_bench/exp001/meld_producer.py
tests/test_exp001_protocol.py
```

每个 producer 会生成六张表：

```text
cost_table.csv
outcome_table.csv
q_policy_map.csv
q_proxy_table.csv
q_diagnostics.csv
corruption_manifest.csv
```

runner 会消费这六张表，然后输出：

```text
summary.json
budget_profile.csv
gate_checks.csv
policy_summary.csv
policy_decisions.csv
```

已经验证通过的 gate：

```text
budget_validity_gate
reliability_proxy_boundary_check
q_only_task_classifier
q_shuffle_control
class_stratified_corruption_check
post_mask_budget_legality_contract
```

所以当前不是“代码没跑通”的问题，而是“这个数据集和当前退化设置有没有足够 benchmark signal”的问题。

## 6. 四轮 MELD 实验

我们总共完成了四条 MELD feature-level 路线：

| 轮次 | 文本 | 音频 | 视频 | 目的 |
|---|---|---|---|---|
| `raw_stats` | 官方文本特征 | 官方音频特征 | 原始 MP4 文件统计 | 最小真实三模态链路 |
| `cv2_stats` | 同上 | `official_concat` | OpenCV 解码统计 | 增强视觉统计和预算差异 |
| `semvis_clip` | 同上 | `official_concat` | frozen CLIP 语义视觉特征 | 检查语义视觉是否改善结果 |
| `semvis_clip + text_stress` | 同上 | `official_concat` | frozen CLIP | 最后一轮诊断：强行打破文本主导 |

`semvis_clip` 的做法：

```text
模型：openai/clip-vit-base-patch32
每个 utterance video 抽帧：8 帧
聚合：每帧 CLIP embedding 归一化后 mean pooling
训练：不 fine-tune
缓存：feature-cache/*.pkl
```

`text_stress` 的做法：

```text
默认 degradation profile 不变；
新增 degradation_profile=text_stress；
在所有 degraded slices 中额外压制文本特征；
目的只是诊断 MELD 的 text dominance，不是默认 corruption profile。
```

## 7. 总结果

| 轮次 | Protocol | Benchmark signal | Joint policy | 主 regret | Kendall tau-b | Rank inversion | 解释 |
|---|---:|---:|---:|---:|---:|---:|---|
| `raw_stats` | pass | fail | pass | 0.848 | 0.810 | 未强调 | 工程链路成功，但视觉信号弱 |
| `cv2_stats` | pass | fail | pass | 0.740 | 0.619 | 0.190 | budget gate 健康，但 oracle gap 很小 |
| `semvis_clip` | pass | fail | pass | 1.869 | 0.905 | 0.048 | 语义视觉有帮助，但 T 仍主导 |
| `semvis_clip + text_stress` | pass | rank 通过 | pass | 0.350 | -0.048 | 0.524 | 排序反转强，但效用差距小 |

默认 MELD 路线没有通过主正结果门槛：

```text
raw_stats regret:   0.848
cv2_stats regret:   0.740
semvis_clip regret: 1.869
目标:               >= 3.0
```

最后的 `text_stress` 虽然让 runner 显示 `benchmark_signal_passed=True`，但它通过的是辅助排序信号，不是主效用差距：

```text
best_single_axis_oracle_regret_dt=0.350
kendall_tau_b=-0.048
rank_inversion_index=0.524
```

## 8. 最新一轮 text_stress 详细结果

远端运行信息：

```text
host: ntu-gpu43
run commit: 40ef3b8
latest recorded commit: fd8b3f6
tmux: exp001_textstress_0515
producer: outputs/meld-producer-semvis-text-stress
analysis: outputs/meld-analysis-semvis-text-stress
log: logs/semvis-text-stress-20260515-090459.log
```

分析结果：

```text
protocol_passed=True
benchmark_signal_passed=True
joint_policy_passed=True

best_single_axis_oracle_regret_dt=0.350
best_single_axis_policy=reliability_only
feasible_oracle_degraded_tight_macro_f1=13.862
best_single_axis_degraded_tight_macro_f1=13.512
joint_degraded_tight_macro_f1=13.833
joint_gap_closure=0.916
pooled_standard_error=0.0208
kendall_tau_b_clean_loose_vs_degraded_tight=-0.048
rank_inversion_index=0.524
```

预算结果：

```text
p95 spread=2.860
tight=18.346 ms
loose=25.233 ms
tight legal templates=T|A|V|TV
loose legal templates=T|A|V|TA|TV|AV|TAV
TAV-vs-unimodal p95 ratio=1.306
warnings=[]
```

模板均值：

```text
clean_loose:
  T=34.708
  TV=28.954
  TAV=21.869
  TA=18.635
  V=16.758
  AV=16.250
  A=11.979

degraded_tight:
  V=13.158
  TV=12.401
  TA=11.679
  AV=11.287
  TAV=11.131
  A=10.746
  T=9.282
```

这一轮的核心解释：

- `T` 从 clean-loose 第一名变成 degraded-tight 最后一名；
- degraded-tight 下最优模板变成 `V`；
- 说明 text dominance 确实被打破了；
- rank inversion 很明显；
- 但 feasible oracle 只比最佳 single-axis policy 高 `0.350`；
- 所以它是“排序信号阳性”，不是“主效用差距阳性”。

## 9. 科学解释

我们现在已经知道：

1. **协议链路成立。**  
   表结构、预算 gate、可靠性 gate、policy evaluator、远端运行都可用。

2. **MELD 默认设置明显文本主导。**  
   在默认 `semvis_clip` 中，`T` 在 clean-loose 和 degraded-tight 都是第一。

3. **语义视觉有帮助，但不足以自然产生主效用差距。**  
   `cv2_stats` 到 `semvis_clip`，主 regret 从 `0.740` 提升到 `1.869`，但仍低于 `3.0`。

4. **强 text stress 可以制造排序反转。**  
   `text_stress` 让 `T` 掉到 degraded-tight 最后，`V` 成为第一。

5. **排序反转不等于主效用差距。**  
   `text_stress` 的 oracle gap 只有 `0.350`。

最准确的中英文结论分别是：

```text
中文：
exp-001 已经证明 feature-level reliability-budget protocol 可以端到端运行。
MELD 能作为诊断案例说明 text dominance 和 rank inversion 问题。
但 MELD 当前不能作为 AutoFusion-Bench 主 paper-level utility-gap 正结果。

English technical version:
exp-001 validates the feature-level protocol. MELD is diagnostic, not sufficient
primary benchmark evidence under the current setup. The text-stress run is
secondary-rank-signal positive but primary-regret negative.
```

## 10. 不能怎么说

不要说：

```text
MELD 已经证明 AutoFusion-Bench 能暴露强 reliability-budget decision gap。
```

不要说：

```text
semvis_clip 是 positive benchmark evidence。
```

不要说：

```text
text_stress 是自然 corruption 下的主结果。
```

可以说：

```text
MELD 上 protocol 已经跑通；
默认 producer 下没有足够 benchmark signal；
强 text-stress 能制造 rank inversion，但 primary oracle gap 仍不足；
因此 MELD 适合作为 protocol-validation / diagnostic case，
不适合作为当前主正结果。
```

## 11. 组员可能会问的问题

### Q1. 这个实验到底在证明什么？不是做 MELD 分类吗？

不是。MELD 分类只是用来测 utility。我们真正测的是：在可靠性变化和预算约束下，fusion template 的选择是否有明显决策面。

### Q2. 为什么不直接看 joint policy 的分数？

因为 benchmark 首先要证明“存在有意义的选择问题”。如果 feasible oracle 和最佳单轴策略差距很小，即使 joint 很好，也说明这个数据集或退化设置没有制造足够的决策空间。

### Q3. 为什么 text_stress 已经 benchmark_signal_passed=True，还不能当主正结果？

因为它是靠辅助排序指标通过，不是靠主指标。主 regret 只有 `0.350`，远低于 `3.0`。它说明排序反转存在，但不说明有足够大的效用收益。

### Q4. 这是不是说明 AutoFusion-Bench 失败？

不是。它说明协议有效，但 MELD 不是理想主数据集。失败的是“当前 MELD + 当前默认退化足以产生主正结果”这个假设。

### Q5. 为什么不继续调 MELD？

我们已经按控制变量顺序做了：

```text
raw visual -> cv2 stats -> semantic visual -> stronger text degradation
```

如果继续调 MELD，很容易变成为了让 MELD 过线而搜索 corruption。现在更合理的是保留 MELD 为 diagnostic case，然后换更天然多模态依赖的数据集。

### Q6. 为什么不放宽 3 macro-F1 门槛？

3-F1 是主 paper-level positive claim 的边界。`1.869` 或 `0.350` 可以做诊断，但不能当主正结果。我们可以新增 triage label，但不应该把门槛改到刚好过线。

### Q7. budget claim 稳不稳？

feature-level budget claim 是成立的，但必须写窄。我们测的是 cached-feature template-head cost，不是端到端部署 latency。`cv2_stats` 和 `text_stress` 的 budget gate 比较健康；默认 `semvis_clip` 有一个 `TAV` vs unimodal ratio warning，需要作为 caveat。

### Q8. q(x) 有没有泄漏？

当前 q proxy 禁止 label、condition、severity、oracle template、test outcome 等字段。我们还做了 q-only classifier 和 q-shuffle control。full runs 的 gate 都通过。但以后如果增加 q features，要继续遵守这个边界。

### Q9. feasible oracle 是不是作弊？

它本来就是 post-hoc upper bound，只用于分析，不是可部署策略。它的作用是衡量这个 reliability-budget cell 中理论上有多大可选择空间。

### Q10. 下一步是不是该换模型？

不建议先换模型。当前更像是数据集和退化条件没有自然制造足够多模态决策面。下一步应该先做新数据集的 signal scout。

## 12. 建议下一步

我建议组会接受以下路线：

```text
接受 exp-001 作为成功的 protocol validation。
不把 MELD 作为主 positive benchmark evidence。
停止在 MELD 上做 broad tuning。
保留 MELD 作为 diagnostic case。
启动下一轮 dataset-signal scout。
补 formalism.md，把现在隐含在代码里的协议写成正式定义。
```

### 12.1 新数据集 scout 应该怎么做

不要直接大跑完整 benchmark。先做便宜的 signal check：

```text
For each candidate dataset:
  1. 检查数据是否真的多模态完整；
  2. 训练/评估 T, A, V, TAV 的 validation 表现；
  3. 看非文本模态是否有实际贡献；
  4. 加 modality-specific degradation；
  5. 看模板排序是否自然反转；
  6. 只有通过 smoke，才跑完整 7-template policy table。
```

候选数据集应该优先满足：

- label 不能主要靠 text alone 解决；
- audio/video 有实质信号；
- 存在自然的 cross-modal conflict 或 modality-specific failure；
- 数据获取和处理成本可控；
- 如果不是三模态，要明确这是 protocol variant。

### 12.2 formalism.md 需要补什么

当前 `formalism.md` 还是空壳，应该补：

- template registry；
- budget legal set；
- reliability-budget cells；
- degraded slices；
- feasible oracle；
- single-axis policies；
- primary regret；
- rank signal；
- protocol pass、benchmark-signal pass、joint-policy pass 的区别。

## 13. 建议分工

| 角色 | 任务 |
|---|---|
| 数据集 scout 负责人 | 找候选数据集，检查模态完整性，设计便宜 smoke |
| 协议/formalism 负责人 | 把 exp-001 的协议写进 `formalism.md` |
| producer 负责人 | 文档化当前 MELD producer，准备迁移到新数据集 |
| analysis 负责人 | 整理四轮结果表，明确每个 pass/fail 的含义 |
| paper framing 负责人 | 把 MELD 写成 diagnostic case，不写成主正结果 |

## 14. 组会需要拍板的三件事

1. 是否接受当前结论：MELD 只作为诊断和 protocol validation，不作为主正结果。
2. 下一步先开新数据集 scout，还是先集中补 formalism 和写作框架。
3. 如果开新数据集 scout，候选数据集、最低通过标准、负责人是谁。

我的建议是：

```text
接受当前 exp-001 结论。
停止继续调 MELD。
把 MELD 结果整理为 diagnostic case。
马上启动新数据集 scout。
同时补 formalism.md，避免协议只存在于代码和聊天里。
```

## 15. 相关文件

主要记录：

```text
experiments/exp-001-decision-surface-pilot/results.md
memory/tasks/exp-001.md
decisions/2026-05-15-exp001-text-stress-result.md
decisions/2026-05-15-exp001-final-meld-diagnostic-iteration.md
```

主要代码：

```text
autofusion_bench/exp001/run_decision_surface_pilot.py
autofusion_bench/exp001/run_meld_table_producer.py
autofusion_bench/exp001/meld_producer.py
tests/test_exp001_protocol.py
```

远端输出：

```text
/usr1/home/s125mdg43_10/projects/AutoFusion-bench/
  experiments/exp-001-decision-surface-pilot/outputs/
    meld-producer
    meld-analysis
    meld-producer-cv2
    meld-analysis-cv2
    meld-producer-semvis-profile1024
    meld-analysis-semvis-profile1024
    meld-producer-semvis-text-stress
    meld-analysis-semvis-text-stress
```
