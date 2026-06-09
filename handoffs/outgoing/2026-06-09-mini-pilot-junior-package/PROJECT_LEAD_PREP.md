# 负责人派活前准备说明

这份文件是给项目负责人看的，不是给学弟的主要任务书。

## 什么时候用这个包

当前 4-row smoke 已经证明：

```text
gold -> diagnosis -> real action -> fixed rule -> scorer
```

链路能跑通。下一步是 10-source / 40-instance mini-pilot，用来判断信号是否稳定。

## 负责人需要先准备什么

在让学弟正式标注前，负责人需要准备：

1. 10 个 clean source；
2. 约 40 个 corrupted media；
3. `mini_source_items.jsonl`；
4. `mini_corruption_manifest.jsonl`；
5. `mini_pilot.draft.jsonl`；
6. 媒体文件路径或 `ANNOTATION_MEDIA_MAP`。

如果这些还没准备好，学弟只能先跑网站 smoke，不能开始正式标注。

## 推荐目录

```text
experiments/exp-002-diag-action-pilot/
  data/
    mini_source_items.jsonl
    mini_corruption_manifest.jsonl
    media/
      clean/
      corrupted/
  annotations/
    mini_pilot.draft.jsonl
    mini_pilot.draft.csv
```

## 从模板开始

复制模板：

```bash
cp handoffs/outgoing/2026-06-09-mini-pilot-junior-package/templates/mini_source_items.template.jsonl \
  experiments/exp-002-diag-action-pilot/data/mini_source_items.jsonl

cp handoffs/outgoing/2026-06-09-mini-pilot-junior-package/templates/mini_corruption_manifest.template.jsonl \
  experiments/exp-002-diag-action-pilot/data/mini_corruption_manifest.jsonl
```

然后把所有 `TODO` 替换成真实 source、question、choices、gold answer 和媒体路径。

## 校验 source 和 manifest

```bash
python3 experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py \
  --kind source-items \
  experiments/exp-002-diag-action-pilot/data/mini_source_items.jsonl

python3 experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py \
  --kind corruption-manifest \
  experiments/exp-002-diag-action-pilot/data/mini_corruption_manifest.jsonl
```

## 生成 draft sheet

```bash
python3 experiments/exp-002-diag-action-pilot/scripts/build_annotation_sheet_v1.py \
  --source-items experiments/exp-002-diag-action-pilot/data/mini_source_items.jsonl \
  --corruption-manifest experiments/exp-002-diag-action-pilot/data/mini_corruption_manifest.jsonl \
  --output-jsonl experiments/exp-002-diag-action-pilot/annotations/mini_pilot.draft.jsonl \
  --output-csv experiments/exp-002-diag-action-pilot/annotations/mini_pilot.draft.csv
```

校验 draft：

```bash
python3 experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py \
  --kind annotations \
  experiments/exp-002-diag-action-pilot/annotations/mini_pilot.draft.jsonl
```

## 交给学弟的内容

给学弟：

- GitHub repo 地址；
- 本 package zip；
- `mini_pilot.draft.jsonl` 的路径；
- 本地媒体目录或路径映射；
- 他的 annotator name，例如 `junior_a`。

告诉他导出文件命名为：

```text
experiments/exp-002-diag-action-pilot/annotations/mini_pilot.junior_a.jsonl
```

## 回收后负责人要做什么

收到学弟导出后先跑：

```bash
python3 experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py \
  --kind annotations \
  experiments/exp-002-diag-action-pilot/annotations/mini_pilot.junior_a.jsonl
```

然后检查：

- `source_decision=accept` 的 source 是否真的可靠；
- `instance_decision=accept` 是否只包含清楚样本；
- partial/unclear 是否被排除主测评；
- route/oracle 是否和 evidence note 一致；
- `adjudication_report` 里是否有需要负责人裁决的样本。
