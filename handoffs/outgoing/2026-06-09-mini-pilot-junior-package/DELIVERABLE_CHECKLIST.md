# Mini-Pilot 交付检查清单

交付前逐项打勾。

## 环境

- [ ] 已从 GitHub clone 最新仓库。
- [ ] `annotation_app` 能启动。
- [ ] `scripts/smoke_test.py` 通过。
- [ ] 媒体文件能在网页中播放；如果不能，已记录 `media missing`。

## Source Screening

- [ ] 已检查 10 个 clean source。
- [ ] 每个 source 都做了 question-only blind pass。
- [ ] 每个 source 都看/听了 clean media。
- [ ] 不合格 source 没有强行进入主测评。
- [ ] `source_screening_sheet.filled.csv` 已填写。

## Corrupted Instance Annotation

- [ ] 约 40 个 corrupted instances 都已 review。
- [ ] 每条都有 `source_decision`。
- [ ] 每条都有 `post_corruption_answerability`。
- [ ] 每条都有 `main_answerability`。
- [ ] 每条都有 `oracle_policy_action`。
- [ ] 每条都有 `annotation_confidence`。
- [ ] 不确定样本已标成 `adjudicate` 或 `exclude_from_main`。

## JSONL Export

- [ ] 已导出 `annotations/mini_pilot.<your_name>.jsonl`。
- [ ] 已运行 validator。
- [ ] validator 输出是 `ok`。
- [ ] validator 输出保存到 `results/mini_pilot_annotation_validation.<your_name>.md`。

## Adjudication Report

- [ ] 已填写 `adjudication_report.filled.md`。
- [ ] 所有 `adjudicate` 样本都有原因。
- [ ] 所有疑似 gold answer 错误的样本都有记录。
- [ ] 所有媒体打不开的样本都有记录。

## 不要提交这些

- [ ] 不要提交 API key。
- [ ] 不要提交 `.venv/`。
- [ ] 不要提交 `node_modules/`。
- [ ] 不要提交临时浏览器下载文件。
