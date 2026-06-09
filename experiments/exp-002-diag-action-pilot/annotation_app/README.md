# exp-002 本地多媒体标注网站

这个工具只服务 `exp-002-diag-action-pilot` 的本地人工审核链路：

1. 导入 `annotations/*.draft.jsonl`。
2. 在网页里看 clean/corrupted 媒体、勾选 v1 字段、记录时间段和 bbox。
3. 保存到本机 SQLite。
4. 导出 scorer 兼容的 `annotations/pilot_annotations.<annotator>.jsonl`。
5. 多个标注者导出后可 merge，生成 disagreement/adjudication 报告。

它不接云端、不做共享数据库、不改变 `score_v1_metrics.py` 的输入契约。
Docker 只是可选封装；推荐先用本地 Python venv + npm 跑通，因为更容易让每个标注者按自己的媒体目录配置。

AutoFusion 标注数据组织规范见：

`skills/autofusion-annotation/references/data_spec.md`

## 本地配置检查

先跑：

```bash
cd experiments/exp-002-diag-action-pilot/annotation_app
./scripts/check_config.py
```

这个检查会确认：

- Python 版本是否满足本地运行；
- `node` / `npm` 是否可用；
- repo root、sample sheet、SQLite state 目录是否可访问；
- `ANNOTATION_MEDIA_MAP` 是否格式正确；
- 前端 build 是否已经生成。

如果需要显式配置媒体路径：

```bash
cp .env.example .env
```

然后编辑 `.env`：

```bash
AUTOFUSION_REPO_ROOT=/path/to/AutoFusion-bench
ANNOTATION_DB_PATH=/path/to/AutoFusion-bench/experiments/exp-002-diag-action-pilot/annotation_app/state/annotations.sqlite
ANNOTATION_MEDIA_MAP=/usr1/home/s125mdg43_10/datasets=/path/to/local/datasets;/usr1/home/s125mdg43_10/projects/AutoFusion-bench=/path/to/AutoFusion-bench
ANNOTATION_HOST=127.0.0.1
ANNOTATION_PORT=8000
```

媒体找不到时，页面仍可标注字段，并会显示 `media missing`。

## 推荐：本地 venv + npm 运行

第一次配置：

```bash
cd experiments/exp-002-diag-action-pilot/annotation_app
./scripts/bootstrap_local.sh
```

严格检查 venv 内 runtime 依赖：

```bash
.venv/bin/python scripts/check_config.py --require-runtime-deps
```

端到端 smoke test：

```bash
.venv/bin/python scripts/smoke_test.py
```

启动：

```bash
./scripts/run_local.sh
```

打开：

```text
http://127.0.0.1:8000
```

这个路径会：

- 建 `.venv/`；
- 安装后端 `FastAPI` / `uvicorn`；
- 安装前端 npm 依赖；
- build 前端静态文件；
- 用 FastAPI 同时服务 API 和前端页面。

## 可选：Docker 运行

在本目录执行：

```bash
docker compose up --build
```

打开：

```text
http://127.0.0.1:8000
```

默认挂载：

- repo root -> `/repo`
- SQLite state -> `/state/annotations.sqlite`
- media root -> `/media`

如果本机数据目录对应远程 `/usr1/home/s125mdg43_10/datasets`，用：

```bash
MEDIA_ROOT=/path/to/local/datasets docker compose up --build
```

如果路径前缀不同，显式设置：

```bash
ANNOTATION_MEDIA_MAP="/usr1/home/s125mdg43_10/datasets=/media/datasets;/usr1/home/s125mdg43_10/projects/AutoFusion-bench=/repo" \
MEDIA_ROOT=/path/to/local/media-root \
docker compose up --build
```

## 后端 CLI smoke

不启动网页也可以验证导入/导出：

```bash
cd experiments/exp-002-diag-action-pilot/annotation_app/backend

python3 -m app.cli \
  --db ../state/smoke.sqlite \
  import-sheet \
  --sheet ../../annotations/smoke_annotation_sheet_v1.draft.jsonl \
  --annotator local-smoke

python3 -m app.cli \
  --db ../state/smoke.sqlite \
  export \
  --output ../../annotations/pilot_annotations.local-smoke.jsonl
```

导出后用现有 validator 检查：

```bash
python3 ../../scripts/validate_jsonl.py \
  --kind annotations \
  ../../annotations/pilot_annotations.local-smoke.jsonl
```

如果已经跑过 `bootstrap_local.sh`，也可以用 venv 内 Python：

```bash
../.venv/bin/python -m app.cli --db ../state/smoke.sqlite summary
```

## 多标注者合并

```bash
cd experiments/exp-002-diag-action-pilot/annotation_app/backend

python3 -m app.cli merge \
  --annotations \
    ../../annotations/pilot_annotations.annotator_a.jsonl \
    ../../annotations/pilot_annotations.annotator_b.jsonl \
  --output ../../annotations/pilot_annotations.merged.jsonl \
  --report ../../results/annotation_disagreements.md
```

合并只比较 v1 headline/quality/recovery/oracle-route 相关字段；有分歧的实例会被标记为 `needs_adjudication`。

## 页面字段

右侧表单按 `screening_scoring_guideline_v1.md` 分组：

- source screening
- corrupted-instance labeling
- answerability and recovery
- oracle policy action
- QC notes

时间段写入 `recovery_evidence.audio_time` / `recovery_evidence.video_time`，并保留 `annotation_app_time_spans` 扩展列表。bbox 写入 `defect_location.bboxes`。这些扩展字段不会影响现有 scorer。

媒体字段支持两种形态：

- 兼容旧 sheet 的 `media.source_video_path` / `media.corrupted_video_path`；
- 支持多媒体同页展示的 `media.items[]`，每个 item 包含 `label`、`role`、`modality`、`path`。
