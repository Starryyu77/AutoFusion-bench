---
created: 2026-06-08
status: design
parent: none
target_exp_id: (will be assigned at /lab-exp-init)
source_docs:
  - reviews/2026-06-08-pilot-expert-replies-synthesis.md
  - handoffs/outgoing/2026-06-08-diagnosis-to-action-pilot-v2.md
---

# Design: Diagnosis-to-Action Pilot

## 一句话实验目标

用 AVQA / MUSIC-AVQA 风格的音视频问答数据构造受控证据损坏，测试多模态大模型是否会出现：

> 模型已经说出某个证据坏了、不足、冲突或不可恢复，但后续行动仍然错误使用该证据、错误回答，或该拒答时不拒答。

这就是本 pilot 要验证的 **diagnosis-to-action gap**。

## 专家意见后的核心改动

这次实验不能再写成“完整 text-audio-video benchmark 已经验证”。如果主数据来自 AVQA / MUSIC-AVQA，文本问题只是 task query，不是 transcript / subtitle / caption 这类可被污染的证据模态。

因此本 pilot 的准确表述是：

> audio-video evidence governance under textual queries.

也就是：在文本问题给定的情况下，模型如何管理不可靠的音频和视频证据。

可选增加一个很小的 transcript / caption / ASR 子集，用来判断未来是否能扩展成完整 text-audio-video evidence governance。这个子集不是 pilot 成败的硬要求。

## Hypothesis

当前 MLLM 可能有一定能力诊断音频或视频证据是否损坏，但不能稳定地把诊断结果转化为正确行动。

更具体地说：

- 模型可能诊断对了，但 route 选错；
- 模型可能知道证据不足，但仍然高置信回答；
- 模型可能检测到音视频冲突，但既不仲裁也不拒答；
- 模型自己的 action 可能不如一个基于其 frozen diagnosis 的简单固定规则。

## Primary experimental object

本实验的主要对象不是一个新模型，而是一套 pilot protocol：

`diagnosis_to_action_pilot_protocol`

它包含：

- source item selection；
- modality necessity labeling；
- controlled corruption；
- human-verified recoverability / route / abstention labels；
- diagnosis-only prompt；
- model action from frozen diagnosis；
- fixed rule from the same frozen diagnosis；
- oracle route / oracle defect-location probes；
- diagnosis-to-action metrics。

这是一组 planned bundle，因为只改其中一个环节不能回答核心问题。

## Scope

### In scope

- 主体数据：AVQA / MUSIC-AVQA 风格的原始音视频问答样本；
- 主体任务：音视频证据治理 under textual query；
- 样本规模：40 个 source items，约 160 个 scored corruption instances；
- 核心现象：self-inconsistency、conditional action failure、rule lift；
- 对照：clean-hard、corrupted-but-irrelevant、quality-only route detector、oracle route。

### Out of scope

- 不声称本 pilot 已经覆盖完整 text-audio-video evidence governance；
- 不把 budget routing 写成主要 novelty，只写成 constrained evidence selection；
- 不用 MELD / MOSEI 作为主正例信号；
- 不把最终答案 accuracy 当成主结果；
- 不在 pilot 阶段追求 paper-scale 数据规模。

## Sample design

先建立 80-120 个候选 source items，再筛到 40 个主样本。不能随机抽样，必须按 modality necessity 选。

| Bucket | Final source items | Episodes per item | 目的 |
|---|---:|---:|---|
| Audio-necessary | 10 | 3-4 | 测 audio neglect 和 audio corruption 下的行动 |
| Video-necessary | 10 | 3-4 | 测 visual evidence degradation 和 route choice |
| Audio-video complementary | 10 | 3-4 | 测跨模态补偿和证据选择 |
| Conflict / temporal-mismatch-prone | 8 | 3-4 | 测冲突和错位下的证据治理 |
| Clean-hard / corrupted-irrelevant control | 5-8 | 2-3 | 测 false alarm 和 over-triage |

筛选时每个 source item 要先标：

```json
{
  "source_id": "...",
  "question": "...",
  "modality_necessity": {
    "text_question_only": false,
    "audio_sufficient": false,
    "video_sufficient": false,
    "audio_video_joint_required": true,
    "human_confidence": "high"
  }
}
```

过滤掉：

- 只靠问题文本或数据集先验就能答的样本；
- 只靠常识或单帧视觉就能答的样本；
- 音频和视频证据位置无法人工确认的样本；
- gold answer 本身歧义较大的样本。

## Corruption design

每个最终 source item 构造约 4 个 corruption episodes，合计约 160 个 scored instances。

| Family | Share | Examples |
|---|---:|---|
| Simple missing / severe degradation | 20% | mute key audio, freeze key frames |
| Mild / medium degradation | 20% | background noise, blur, low light, low bitrate |
| Temporal mismatch | 20% | audio-video shift, frame shift |
| Cross-modal conflict | 20% | audio cue and visual cue imply different answers |
| Clean-hard / corrupted-irrelevant controls | 20% | no corruption but hard; corrupt irrelevant modality |

每次 corruption 必须生成 manifest，不能只保存处理后文件：

```json
{
  "instance_id": "...",
  "source_id": "...",
  "affected_modality": "audio",
  "corruption_type": "background_noise",
  "severity": "medium",
  "location": {
    "audio_time": [3.2, 5.1],
    "video_time": null,
    "frame_range": null
  },
  "corruption_relevance": "answer_relevant",
  "generator_family": "noise_v1",
  "seed": 13
}
```

必须加入 artifact controls：

- 多种噪声、遮挡、错位风格；
- clean-hard controls；
- corrupted-but-irrelevant controls；
- quality-only detector baseline；
- question-only / prior-only sanity check。

如果 quality-only detector 接近 oracle route，说明 corruption 太浅，不能扩展。

## Annotation plan

每个 scored instance 至少需要以下 gold fields：

```json
{
  "instance_id": "...",
  "source_dataset": "AVQA_or_MUSIC_AVQA",
  "question": "...",
  "modalities_presented": ["audio", "video"],
  "gold_answer": "...",
  "modality_necessity": {
    "text_question_only": false,
    "audio_sufficient": true,
    "video_sufficient": false,
    "audio_video_joint_required": false,
    "human_confidence": "high"
  },
  "modality_status": {
    "text": "not_applicable",
    "audio": "clean",
    "video": "corrupted"
  },
  "defect_location": {
    "audio_time": null,
    "video_time": [2.0, 4.4],
    "frame_range": null,
    "region_note": "face/object partially occluded"
  },
  "corruption_relevance": "answer_relevant",
  "recoverability": "recoverable",
  "recovery_source": ["audio"],
  "recovery_evidence": {
    "audio_time": [2.1, 3.9],
    "video_time": null,
    "note": "audio cue is sufficient for the queried event"
  },
  "oracle_policy_action": {
    "selected_route": ["audio"],
    "abstain": false
  },
  "annotation_confidence": "high"
}
```

Recoverability 必须是 task-conditioned：

> 对当前 question 和 gold answer 来说，另一个干净模态是否包含足够证据，并且标注者能指出证据位置。

如果标注者指不出 evidence pointer，不允许标成 `recoverable`。

标注质量建议：

- 所有样本人工检查；
- 至少 50 个 instances 双人复标；
- recoverability / oracle policy action 的 Cohen's kappa 最低目标为 0.4，理想目标为 0.6 以上；
- disagreement cases 进入 adjudication note。

## Model and prompt settings

模型面板要先做可行性验证，不能根据印象假设模型支持音频和视频同实例输入。

执行前必须确认：

- 是否支持 audio + video in one instance；
- 音视频同步处理方式；
- 视频帧采样策略；
- 音频时长、采样率、文件大小限制；
- JSON / structured output 稳定性；
- API 成本、速率限制或本地显存需求。

最低有意义面板：

- 至少 2 个可处理音视频同实例的模型；
- 如果资源允许，再加入 2 个开源模型和 2 个闭源模型；
- 另设 text/question-only 或 metadata-free sanity baseline。

Prompt settings：

1. **Direct structured decision**
   - 一步输出 diagnosis、route、answer、abstain。
2. **Diagnosis-only**
   - 只输出 modality status、defect note、recoverability、evidence，不输出最终答案。
3. **Model action from frozen diagnosis**
   - 把同一个 frozen diagnosis 喂回模型，让它选择 route / answer / abstain。
4. **Fixed rule from frozen diagnosis**
   - 用确定性规则读取同一份 frozen diagnosis，选择 route / abstain。
5. **Oracle route**
   - 给 gold route，让模型只负责执行答题或拒答。
6. **Oracle defect-location**
   - 给 gold defect location，测试 recoverability 和 action。
7. **Abstention-calibrated**
   - 明确要求证据不足时拒答，测试 false answer 是否下降。

关键要求：

> `model action` 和 `fixed rule` 必须使用完全同一份 frozen model diagnosis。否则 rule lift 会混入 prompt 差异。

## Fixed rule sketch

固定规则只读模型自己的 diagnosis，不读 gold label。

建议初版规则：

1. 如果 diagnosis 标记 `recoverability = unrecoverable`，输出 `abstain = true`。
2. 如果某个 modality 被诊断为 corrupted / missing / conflicting，且该 modality 被诊断为 answer-relevant，则不选择它作为 route。
3. 如果 diagnosis 给出 clean recovery source 和 evidence pointer，则选择 recovery source。
4. 如果 diagnosis 标记音视频冲突，且无法指出可信 source，则 abstain。
5. 如果 corruption 被诊断为 answer-irrelevant，则保留原必要 route，不因为低层质量差而过度拒答。
6. 如果 route 超过约束预算，则优先保留被诊断为 sufficient 的最低成本 clean route。

这个规则不是为了做强方法，而是为了证明：

> 同样的诊断信息，一个简单规则都能更一致地行动，而模型自己做不到。

## Evaluation

### Primary metrics

| Metric | Definition | Why it matters |
|---|---|---|
| Diagnosis macro-F1 | modality status / defect coarse class against gold | 模型是否知道证据哪里坏了 |
| Recoverability macro-F1 | recoverable / partial / unrecoverable | 模型是否知道能不能补 |
| Policy action accuracy | route_correct AND abstention_correct AND no budget violation | 模型行动是否正确 |
| Self-inconsistency rate | action contradicts model's own diagnosis | 最干净的 headline gap |
| Conditional action failure | diagnosis correct but policy action wrong | gold-based 支撑证据 |
| Rule lift | fixed_rule(model_diagnosis) - model_action(model_diagnosis) | 诊断到行动的瓶颈 |
| False answer rate on unrecoverable | should abstain but answers | 风险治理能力 |

### Secondary metrics

- final answer accuracy；
- answer_correct_given_oracle_route；
- governed_success；
- defect-location hit rate；
- recovery-source accuracy；
- evidence hit rate；
- route regret；
- budget violation；
- false abstention；
- coverage-risk curve；
- structured-output parse failure rate。

### 核心派生指标

```text
policy_correct = route_correct AND abstention_correct AND no_budget_violation

answer_correct_given_oracle_route =
  final answer correct when gold route is supplied

governed_success =
  policy_correct AND final_answer_correct

RuleLift =
  Score(fixed_rule(model_diagnosis))
  - Score(model_action(model_diagnosis))
```

Score 优先用 `policy action accuracy`，补充报告 `governed_success`。

## Error taxonomy

每个模型至少整理 10-15 个 qualitative failures，覆盖：

| Error type | Meaning |
|---|---|
| diagnosis wrong, action wrong | perception / diagnosis failure |
| diagnosis correct, route wrong | diagnosis-to-routing gap |
| diagnosis correct, route correct, answer wrong | task execution failure |
| diagnosis correct, recoverability wrong | recovery judgment failure |
| diagnosis correct, abstention wrong | risk-policy failure |
| final answer correct, diagnosis/action wrong | final-answer masking |
| self-inconsistent action | acts against stated diagnosis |

特别要找 final answer masking：最终答对了，但诊断或行动其实错了。这个现象能说明只看 accuracy 会掩盖问题。

## Controls and sanity checks

必须保留这些对照，否则 reviewer 会怀疑结果是 artifact：

- **Clean-hard**: 没有 corruption 但任务困难，测试模型是否过度诊断；
- **Corrupted-irrelevant**: 损坏的是无关模态，测试模型是否过度避开；
- **Quality-only route detector**: 只看低层质量特征，不看语义；
- **Question-only baseline**: 只给文本问题，测试数据集先验；
- **Oracle route**: 区分 route/action failure 和 task execution failure；
- **Oracle defect-location**: 测 defect 定位给定后是否还能正确行动；
- **Generator-family holdout**: 如果样本足够，保留一种 corruption style 不参与 prompt examples。

## Predictions

### If H1 is true

- 至少 2 个模型出现 self-inconsistency；
- 至少 10 个清晰 qualitative self-inconsistency cases；
- 至少一个 meaningful subset 上 conditional action failure > 25-30%；
- fixed rule 在同一 frozen diagnosis 上带来 +5-10 point rule lift；
- unrecoverable cases 上 false answer rate 明显高于 false abstention；
- oracle route 能显著区分 action failure 和 task execution failure。

### If H0 is true

- self-inconsistency 很少；
- model action 与 fixed rule 差距接近 0；
- conditional action failure 低；
- oracle route 与直接决策差别很小；
- 模型诊断、route、abstain 都接近 oracle；
- 或者 quality-only detector 已经接近 oracle，说明任务太浅。

### Surprise outcomes

- 前沿模型在 audio-video corruption 下几乎接近 oracle；
- 标注者无法稳定判断 recoverability；
- 大量样本可由 question-only baseline 答对；
- 模型不擅长感知 corruption，但仍能凭先验答对；
- fixed rule 没提升，反而说明模型 action head 已经很好或 diagnosis 字段不可用。

## Kill criteria

这个 pilot 应该在两周内给出 go/no-go，不要无限扩张。

停止或重设计条件：

- 找不到至少 2 个可处理 audio + video 同实例的模型；
- 无法合法获取或处理 AVQA / MUSIC-AVQA 风格 raw audio/video；
- 80-120 个候选样本中，大多数被 question-only / prior-only 解决；
- recoverability 双人标注 kappa < 0.4；
- quality-only detector 接近 oracle policy action；
- 大多数错误来自明显 synthetic artifact；
- structured-output parse failure 高到影响比较；
- pilot 超过 200 scored instances 还没有看见清晰 gap。

## Success criteria

满足以下多数条件，就进入 paper-scale benchmark 扩展：

- self-inconsistency 出现在至少 2 个模型，并有至少 10 个可写进论文的案例；
- conditional action failure 在至少一个核心 bucket 上超过 25-30%；
- rule lift 在核心 subset 上达到 +5-10 points；
- final-answer masking 占正确答案案例的 15-20% 以上；
- unrecoverable false-answer rate 明显高于 false-abstention rate；
- quality-only detector 没有接近 oracle；
- recoverability / oracle action 标注达到至少中等一致性；
- oracle route 能把 action failure 和 task execution failure 分开。

## Execution phases

### Phase 0: Feasibility gate

Deliverables:

- `data/pilot_model_feasibility.md`
- `data/pilot_dataset_feasibility.md`

Work:

- 验证 AVQA / MUSIC-AVQA 或同类数据能否下载、处理和引用；
- 验证模型音视频输入能力；
- 试跑 5 个 clips，确认 structured JSON 能解析；
- 初步估算成本。

Gate:

- 不通过 Phase 0，不进入大规模 corruption 和标注。

### Phase 1: Source item pool

Deliverables:

- `experiments/<exp-id>/data/pilot_source_candidates.csv`
- `experiments/<exp-id>/data/pilot_source_items.csv`
- `experiments/<exp-id>/annotations/pilot_modality_necessity.jsonl`

Work:

- 收集 80-120 个候选 source items；
- 标注 modality necessity；
- 筛到 40 个主样本；
- 可选筛 10-20 个 text-evidence feasibility subset。

### Phase 2: Corruption generator and manifest

Deliverables:

- `experiments/<exp-id>/scripts/build_corruptions.py`
- `experiments/<exp-id>/data/pilot_corruption_manifest.jsonl`
- `experiments/<exp-id>/data/corrupted_media/`

Work:

- 实现 audio/video corruption；
- 记录 affected modality、type、severity、location、relevance、seed；
- 加入 clean-hard 和 corrupted-irrelevant controls；
- 人工 spot-check 每类 corruption。

### Phase 3: Annotation guideline and gold labels

Deliverables:

- `experiments/<exp-id>/annotations/annotation_guideline_v0.md`
- `experiments/<exp-id>/annotations/pilot_annotations.jsonl`
- `experiments/<exp-id>/annotations/adjudication_notes.md`
- `experiments/<exp-id>/results/annotation_agreement.md`

Work:

- 写 recoverability、evidence pointer、oracle route、abstention 规范；
- 标注全部 instances；
- 至少 50 个 instances 双人复标；
- 计算 agreement；
- 裁决 disagreement cases。

### Phase 4: Model runs

Deliverables:

- `experiments/<exp-id>/prompts/`
- `experiments/<exp-id>/outputs/model_diagnoses.jsonl`
- `experiments/<exp-id>/outputs/model_actions.jsonl`
- `experiments/<exp-id>/outputs/oracle_route_outputs.jsonl`
- `experiments/<exp-id>/outputs/oracle_defect_location_outputs.jsonl`

Work:

- 跑 direct structured decision；
- 跑 diagnosis-only 并冻结输出；
- 用同一 frozen diagnosis 跑 model action；
- 跑 oracle route / oracle defect-location probes；
- 记录 parse failure 和重试次数。

### Phase 5: Fixed rule and metrics

Deliverables:

- `experiments/<exp-id>/scripts/apply_fixed_rule.py`
- `experiments/<exp-id>/outputs/fixed_rule_actions.jsonl`
- `experiments/<exp-id>/results/pilot_metrics.csv`
- `experiments/<exp-id>/results/pilot_metrics.md`

Work:

- 在 frozen diagnosis 上应用 deterministic fixed rule；
- 计算 primary / secondary metrics；
- 按 bucket、corruption family、recoverability、model 分解；
- 特别报告 rule lift 和 self-inconsistency。

### Phase 6: Go/no-go memo

Deliverables:

- `experiments/<exp-id>/results/qualitative_failures.md`
- `experiments/<exp-id>/results/go_no_go_memo.md`

Work:

- 写 10-15 个代表性 failure cases；
- 判断是否达到 success criteria；
- 决定 scale、redesign，或 pivot。

## Two-week schedule

| Day | Work |
|---:|---|
| 1-2 | Phase 0: 数据和模型可行性验证 |
| 3-4 | Phase 1: 候选样本池和 modality necessity 筛选 |
| 5-6 | Phase 2: corruption generator 和 manifest |
| 7-9 | Phase 3: annotation guideline、gold labels、agreement |
| 10-11 | Phase 4: model runs |
| 12-13 | Phase 5: fixed rule、metrics、分桶分析 |
| 14 | Phase 6: qualitative failures 和 go/no-go memo |

## If pilot passes: paper-scale expansion

如果 pilot 通过，会议级工作再扩展：

- 从 40 source items 扩到 300-800 source items；
- 从 160 scored instances 扩到 1,500-4,000 scored instances；
- 保留 500-1,000 条高质量 human-verified test set；
- 扩展模型面板到 6-10 个；
- 增加真实 text-evidence subset，才能正式写 text-audio-video；
- 增加 generator-family holdout；
- 完成 datasheet、annotation guideline、corruption scripts、baseline suite。

如果 pilot 不通过，不建议硬做大数据集。应该根据失败原因选择：

- 换数据底座；
- 改 corruption taxonomy；
- 改成更窄的 audio-video self-inconsistency benchmark；
- 或者放弃这个 paper framing。

## Proposed next command

下一步不是直接跑实验，而是用 `/lab-exp-init` 把这个 plan 转成正式实验目录和 `scope.lock`。

建议 shortname：

`diag-action-pilot`

建议实验问题：

> Can MLLMs act consistently on their own diagnosis of unreliable audio-video evidence under textual queries?
