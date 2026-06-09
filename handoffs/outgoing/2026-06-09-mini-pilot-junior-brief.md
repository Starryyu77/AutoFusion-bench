# AutoFusion-Bench Mini-Pilot 标注说明

这份文档可以直接发给学弟。

## 你要做什么

我们要把当前 4 条 smoke 扩展成一个小规模 mini-pilot：

- 10 个 clean source；
- 每个 source 大约 4 个 corrupted versions；
- 总计约 40 条 corrupted instances。

你不需要训练模型，也不需要跑大模型 API。你只负责人工标注：

- 原始 clean source 是否真的支持 gold answer；
- corrupted 后是否还能回答；
- 可靠系统应该用 audio、video、audio+video，还是应该拒答；
- 如果可以回答，最终答案是什么；
- 如果不确定，标成需要复核，不要硬填。

## 你需要下载什么数据集

如果你只是做标注：**不需要下载全量数据集**。

你只需要：

1. 从 GitHub clone 我们的 `AutoFusion-bench` 仓库；
2. 拿到负责人给你的 mini-pilot 媒体包，里面应该包含：
   - 10 个 clean source MP4；
   - 约 40 个 corrupted MP4；
   - `mini_pilot.draft.jsonl` 标注输入文件。

如果负责人还没给你媒体包，你不能正式开始标注，只能先把网站跑通。

如果你被要求帮忙准备数据，优先使用 **AVQA 风格的音视频问答数据**，不是 MELD。当前项目优先路线是：

- 首选：AVQA / AVQA-videos，要求有原始 MP4、问题、选项、gold answer、video id；
- 备选：MUSIC-AVQA，如果 AVQA 获取受阻，或者我们想先做音乐场景；
- 不要用：MELD、CMU-MOSI、CMU-MOSEI、IEMOCAP 作为这次 mini-pilot 主数据；
- 不要只下载 precomputed features，我们需要原始同步音视频 MP4。

mini-pilot 选样尽量覆盖：

| 类型 | 数量 |
|---|---:|
| 答案主要靠 audio | 2 个 source |
| 答案主要靠 video | 2 个 source |
| audio/video 互补 | 2 个 source |
| 污染的是无关模态 | 2 个 source |
| 音视频冲突或时间错位 | 2 个 source |

## 启动标注网站

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

如果页面显示媒体找不到，让负责人给你本地媒体目录，并配置 `ANNOTATION_MEDIA_MAP`。

## 导入标注文件

负责人应该给你：

```text
experiments/exp-002-diag-action-pilot/annotations/mini_pilot.draft.jsonl
```

在网页里导入它，然后逐条标注。

## 每条样本怎么标

按这个顺序：

1. 先只看问题和选项，不看媒体，判断是不是光靠文本就能猜出来。
2. 看 clean source，判断原始媒体是否真的支持 gold answer。
3. 看 corrupted media，判断污染后是否还能回答。
4. 判断可靠系统应该选择哪个 route：`audio`、`video`、`audio+video`，还是拒答。
5. 填最终答案；如果证据不够，就拒答。
6. 填 confidence 和 notes。

最重要的规则：

- clean source 不清楚，就不要让这条进入主测评；
- corrupted 后只是“好像能答”，就标成需要复核；
- 如果你不能指出证据来源，不要标成 recoverable；
- 不要为了凑数量把模糊样本硬标成 accept。

## 常见选择

如果音频被静音，问题问声音来源：

- 应该拒答；
- route 为空；
- final answer 为空；
- 写明原因：音频缺失，视频不能支持声音来源答案。

如果视频被模糊，但问题问声音来源：

- 通常仍可回答；
- route 选 audio；
- final answer 填 gold answer；
- 写明视频污染不影响当前问题。

如果音频错位，但视频能清楚回答：

- route 选 video；
- 如果 audio 会误导，可以把 audio 作为不推荐路线；
- final answer 填视频支持的答案。

如果 clean source 本身就不清楚：

- 不要继续硬标；
- 标成 reject 或 adjudicate；
- notes 里写清楚为什么。

## 你最后交付什么

只交两个东西：

1. 网站导出的标注 JSONL：

```text
experiments/exp-002-diag-action-pilot/annotations/mini_pilot.<your_name>.jsonl
```

2. 一个简单的问题列表，可以直接写在消息里：

```text
哪些样本看不清、听不清、gold answer 可疑、需要负责人复核。
```

交付前必须运行：

```bash
cd AutoFusion-bench
python3 experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py \
  --kind annotations \
  experiments/exp-002-diag-action-pilot/annotations/mini_pilot.<your_name>.jsonl
```

看到 `ok` 再交付。

## 不要做什么

- 不要下载全量 AVQA，除非负责人明确让你做数据准备；
- 不要使用 MELD 作为这次主数据；
- 不要把 API key 写进文件；
- 不要提交 `.venv/` 或 `node_modules/`；
- 不要把不确定样本强行标成主测评样本。
