# AutoFusion-Bench Mini-Pilot 数据准备与标注说明

这份文档可以直接发给学弟。

## 1. 你的主要任务

你后面主要负责 **数据集准备和第一轮人工筛查**，不是训练模型，也不是写论文故事。

我们要把当前 4 条 smoke 扩展成一个小规模 mini-pilot：

- 先准备 80-120 个候选 clean source；
- 从里面筛出 10 个高质量 clean source；
- 每个 source 做约 4 个 corrupted versions；
- 得到约 40 条 corrupted instances；
- 用本地标注网站做人工筛查和标注；
- 导出可以被 scorer 读取的 JSONL。

最终目标是让我们判断：这个 benchmark 设计在更多样本上是否真的能暴露模型的诊断、路由、拒答和最终答案问题。

## 2. 你要下载什么数据集

优先数据集：**AVQA / AVQA-videos**。

我们需要的是音视频问答数据，必须包含：

- 原始同步音视频 MP4；
- question；
- answer choices；
- gold answer；
- video id 或 video name；
- 最好有粗粒度 question relation，例如 Sound / View / Both。

推荐顺序：

1. **AVQA / AVQA-videos**：当前首选，适合 audio-video QA；
2. **MUSIC-AVQA**：备选，如果 AVQA 下载受阻，或者我们想做音乐场景；
3. 不要用 **MELD / CMU-MOSI / CMU-MOSEI / IEMOCAP** 作为本轮主数据；
4. 不要只下载 precomputed features，我们需要原始 MP4。

注意：你不一定要下载全量数据。mini-pilot 阶段只需要能筛出 80-120 个候选 source，并最终保留 10 个高质量 source。

## 3. 数据准备的目标结构

你最终需要准备这些文件：

```text
experiments/exp-002-diag-action-pilot/
  data/
    mini_source_candidates.csv
    mini_source_items.jsonl
    mini_corruption_manifest.jsonl
    media/
      clean/
      corrupted/
  annotations/
    mini_pilot.draft.jsonl
    mini_pilot.draft.csv
```

其中：

- `mini_source_candidates.csv`：80-120 个候选 source 的筛查表；
- `mini_source_items.jsonl`：最终选中的 10 个 clean source；
- `mini_corruption_manifest.jsonl`：约 40 条 corrupted instances 的记录；
- `media/clean/`：10 个 clean MP4；
- `media/corrupted/`：约 40 个 corrupted MP4；
- `mini_pilot.draft.jsonl`：导入标注网站的输入文件。

## 4. 10 个 clean source 怎么选

不要随机选。要按类型平衡：

| 类型 | 目标数量 | 说明 |
|---|---:|---|
| audio necessary | 2 | 答案主要靠声音 |
| video necessary | 2 | 答案主要靠画面 |
| audio/video complementary | 2 | 音频和视频互补 |
| corrupted irrelevant control | 2 | 污染一个无关模态，测试模型会不会被干扰 |
| conflict / temporal mismatch | 2 | 适合做音视频冲突或时间错位 |

每个 clean source 必须满足：

- 原始视频和音频都能正常打开；
- 问题不能只靠文本和选项猜出来；
- gold answer 能被原始媒体明确支持；
- 能说清楚答案主要来自 audio、video，还是 audio+video；
- 不依赖过强的常识猜测。

如果原始样本本身就不清楚，直接丢掉，不要为了凑数量保留。

## 5. 每个 source 做什么 corruption

每个 clean source 做 3-4 个 corruption 即可，不要全组合爆炸。

优先 corruption 类型：

- audio mute：音频静音；
- audio noise：音频加噪；
- audio shift：音频时间错位；
- video blur：视频模糊；
- video occlusion：遮挡关键区域；
- audio replace / conflict-like：替换成可能误导的音频；
- irrelevant corruption：污染一个对当前问题不重要的模态。

每条 corruption 都要记录：

- `instance_id`
- `source_id`
- `affected_modality`
- `corruption_type`
- `severity`
- `location`
- `corruption_relevance`
- `source_video_path`
- `corrupted_video_path`

重要：generator metadata 只是机械记录，不等于 gold label。真正是否影响答案，要通过人工标注判断。

## 6. 本地标注网站怎么跑

```bash
git clone <REPO_URL> AutoFusion-bench
cd AutoFusion-bench/experiments/exp-002-diag-action-pilot/annotation_app
./scripts/bootstrap_local.sh
.venv/bin/python scripts/smoke_test.py
./scripts/run_local.sh
```

打开：

```text
http://127.0.0.1:8000
```

如果页面显示媒体找不到，需要配置 `ANNOTATION_MEDIA_MAP`，把远程路径映射到你本地的媒体目录。

## 7. 怎么生成标注输入文件

当你准备好：

- `data/mini_source_items.jsonl`
- `data/mini_corruption_manifest.jsonl`

之后运行：

```bash
cd AutoFusion-bench
python3 experiments/exp-002-diag-action-pilot/scripts/build_annotation_sheet_v1.py \
  --source-items experiments/exp-002-diag-action-pilot/data/mini_source_items.jsonl \
  --corruption-manifest experiments/exp-002-diag-action-pilot/data/mini_corruption_manifest.jsonl \
  --output-jsonl experiments/exp-002-diag-action-pilot/annotations/mini_pilot.draft.jsonl \
  --output-csv experiments/exp-002-diag-action-pilot/annotations/mini_pilot.draft.csv
```

然后校验：

```bash
python3 experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py \
  --kind annotations \
  experiments/exp-002-diag-action-pilot/annotations/mini_pilot.draft.jsonl
```

看到 `ok` 后，再导入网站标注。

## 8. 每条样本怎么标

按这个顺序：

1. 先只看问题和选项，不看媒体，判断是不是光靠文本就能猜出来；
2. 看 clean source，判断原始媒体是否真的支持 gold answer；
3. 看 corrupted media，判断污染后是否还能回答；
4. 判断可靠系统应该选择哪个 route：`audio`、`video`、`audio+video`，还是拒答；
5. 填最终答案；如果证据不够，就拒答；
6. 填 confidence 和 notes。

硬规则：

- clean source 不清楚，就不要让它进入主测评；
- corrupted 后只是“好像能答”，就标成需要复核；
- 如果你不能指出证据来源，不要标成 recoverable；
- 不要为了凑数量把模糊样本硬标成 accept。

## 9. 你最后交付什么

请交付：

```text
data/mini_source_candidates.csv
data/mini_source_items.jsonl
data/mini_corruption_manifest.jsonl
annotations/mini_pilot.draft.jsonl
annotations/mini_pilot.<your_name>.jsonl
```

再附一个简单问题列表，写清楚：

- 哪些 source 被丢掉了，为什么；
- 哪些样本媒体打不开；
- 哪些 gold answer 可疑；
- 哪些 corrupted instance 需要负责人复核；
- 哪些 corruption 做出来后效果不明显。

交付前必须跑：

```bash
python3 experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py \
  --kind source-items \
  experiments/exp-002-diag-action-pilot/data/mini_source_items.jsonl

python3 experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py \
  --kind corruption-manifest \
  experiments/exp-002-diag-action-pilot/data/mini_corruption_manifest.jsonl

python3 experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py \
  --kind annotations \
  experiments/exp-002-diag-action-pilot/annotations/mini_pilot.<your_name>.jsonl
```

三个都看到 `ok` 再交付。

## 10. 不要做什么

- 不要把 MELD 当成本轮主数据；
- 不要只下载 feature 文件；
- 不要保留 clean source 本身就不清楚的样本；
- 不要把 partial / unclear 样本强行标成主测评；
- 不要把 API key 写进文件；
- 不要提交 `.venv/` 或 `node_modules/`。
