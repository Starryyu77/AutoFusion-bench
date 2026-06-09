# 给学弟的任务书：AutoFusion-Bench Mini-Pilot 标注

## 你要做什么

我们在做一个多模态 benchmark，核心问题是：

> 当音频/视频被污染、缺失或冲突时，模型能不能判断应该看哪个模态，什么时候该拒答，最后能不能答对。

你这次不需要训练模型，也不需要跑大模型 API。你负责的是人工标注：

- 判断 clean source 本身是不是可用；
- 判断 corrupted 后还能不能回答；
- 判断应该用 audio、video、audio+video，还是应该 abstain；
- 标出 final answer；
- 把不确定样本放进 adjudication，不要硬标。

## 你需要 clone 的仓库

从 GitHub clone 主仓库：

```bash
git clone <REPO_URL> AutoFusion-bench
cd AutoFusion-bench
```

如果你不知道 `<REPO_URL>`，问项目负责人要。不要自己新建仓库。

## 你要使用哪个网站

标注网站在仓库里：

```text
experiments/exp-002-diag-action-pilot/annotation_app/
```

启动方法见本包的：

```text
LOCAL_WEBSITE_SETUP.md
```

## 你要标多少

mini-pilot 目标：

- 10 个 clean source；
- 每个 source 约 4 个 corrupted instances；
- 总计约 40 个 corrupted instances。

bucket 尽量覆盖：

| Bucket | 目标数量 | 含义 |
|---|---:|---|
| audio necessary | 2 source | 答案主要靠音频 |
| video necessary | 2 source | 答案主要靠视频 |
| audio/video complementary | 2 source | 音频和视频互补 |
| corrupted irrelevant control | 2 source | 污染了一个无关模态 |
| conflict / temporal mismatch | 2 source | 音视频冲突或错位 |

## 每个样本怎么判断

严格按这个顺序：

1. 只看问题和选项，不看媒体。
2. 看 clean source，判断原始样本是否真的支持 gold answer。
3. 看 corrupted media，判断污染后是否还能回答。
4. 判断应该用哪个 route。
5. 判断是否应该 abstain。
6. 填 confidence 和 notes。

不要先入为主相信数据集原始标签。公开数据集也会有噪声。

## 什么样的样本可以进入主测评

必须同时满足：

- `source_decision=accept`
- `instance_decision=accept`
- `main_answerability=answerable` 或 `unanswerable`
- `annotation_confidence=high` 或 `medium`
- `risk_sensitive=false`

如果你觉得“可能能答，但不确定”，不要硬标成 `answerable`。用：

- `main_answerability=exclude_from_main`
- `instance_decision=adjudicate`
- 在 notes 里写原因。

## 哪些东西不用你反复填

这些是 generator 已知信息，通常不用你重新判断：

- 这条 corruption 是 audio mute 还是 video blur；
- severity 是 mild/medium/severe；
- 机械上污染了 audio 还是 video；
- 时间段如果 generator 已经给了，可以当提示。

但如果你发现 generator metadata 明显错了，要在 notes 里写出来。

## 你最后要交什么

请交付四类文件：

1. 标注网站导出的 JSONL：

```text
experiments/exp-002-diag-action-pilot/annotations/mini_pilot.<your_name>.jsonl
```

2. validator 结果：

```text
experiments/exp-002-diag-action-pilot/results/mini_pilot_annotation_validation.<your_name>.md
```

3. clean source 筛查表：

```text
handoffs/outgoing/2026-06-09-mini-pilot-junior-package/templates/source_screening_sheet.filled.csv
```

4. 争议/不确定样本报告：

```text
handoffs/outgoing/2026-06-09-mini-pilot-junior-package/templates/adjudication_report.filled.md
```

## 交付前必须跑

```bash
python3 experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py \
  --kind annotations \
  experiments/exp-002-diag-action-pilot/annotations/mini_pilot.<your_name>.jsonl
```

如果 validator 不通过，先修到通过再交付。
