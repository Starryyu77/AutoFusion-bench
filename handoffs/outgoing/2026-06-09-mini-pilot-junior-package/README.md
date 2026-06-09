# AutoFusion-Bench Mini-Pilot Junior Package

用途：把 `exp-002` 从 4-row smoke 扩展到 10-source / 40-instance mini-pilot。

这个包是给学弟执行用的。目标不是让他设计论文故事，而是让他按统一标准完成：

1. 搭好本地标注网站；
2. 审核 10 个 clean source 是否合格；
3. 标注约 40 个 corrupted instances；
4. 导出 validator-compatible JSONL；
5. 写清楚不确定样本和问题样本。

## 最重要的原则

- 先判断 clean source 是否合格，再判断 corrupted instance。
- generator metadata 只是提示，不是 gold。
- 人工标注重点是：是否还能回答、该选什么 route、是否应该 abstain、最终答案是什么。
- 模型实验由主负责人跑；学弟只交付标注结果和问题报告。
- 不要把 ambiguous / partial 样本强行放进主测评。

## 包内文件

| 文件 | 用途 |
|---|---|
| `README.md` | 本说明 |
| `JUNIOR_TASK.md` | 发给学弟的完整任务书 |
| `ANNOTATION_FIELD_GUIDE.md` | 每个字段怎么填 |
| `LOCAL_WEBSITE_SETUP.md` | 本地标注网站安装和启动 |
| `PROJECT_LEAD_PREP.md` | 负责人给学弟派活前要准备什么 |
| `DELIVERABLE_CHECKLIST.md` | 交付前自检清单 |
| `templates/source_screening_sheet.csv` | 10 个 clean source 的筛查记录模板 |
| `templates/mini_source_items.template.jsonl` | source items JSONL 模板 |
| `templates/mini_corruption_manifest.template.jsonl` | corruption manifest JSONL 模板 |
| `templates/adjudication_report.template.md` | 不确定样本/争议样本报告模板 |

## 推荐执行顺序

1. 让学弟从 GitHub clone `AutoFusion-bench`。
2. 负责人先按 `PROJECT_LEAD_PREP.md` 准备实际 mini-pilot draft sheet。
3. 让学弟阅读本包里的 `JUNIOR_TASK.md`。
4. 让他按 `LOCAL_WEBSITE_SETUP.md` 启动标注网站。
5. 先用 repo 里的 smoke draft 跑通网站导入/导出。
6. 再开始 mini-pilot 的 10-source / 40-instance 标注。
7. 标注后导出 JSONL，并运行 validator。
8. 把导出的 JSONL、筛查表、adjudication report 发回。

## 交付给主负责人的最小文件

学弟最后至少交付：

- `annotations/mini_pilot.<annotator_name>.jsonl`
- `results/mini_pilot_annotation_validation.md`
- `handoffs/.../source_screening_sheet.filled.csv`
- `handoffs/.../adjudication_report.filled.md`

其中 JSONL 必须通过：

```bash
python3 experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py \
  --kind annotations \
  experiments/exp-002-diag-action-pilot/annotations/mini_pilot.<annotator_name>.jsonl
```
