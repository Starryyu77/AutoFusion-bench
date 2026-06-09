# 本地标注网站安装和启动

## 1. clone repo

```bash
git clone <REPO_URL> AutoFusion-bench
cd AutoFusion-bench
```

## 2. 进入标注网站目录

```bash
cd experiments/exp-002-diag-action-pilot/annotation_app
```

## 3. 检查本机环境

```bash
./scripts/check_config.py
```

如果缺 Python / Node / npm，先安装对应依赖。

## 4. 配置媒体路径

复制配置文件：

```bash
cp .env.example .env
```

编辑 `.env`：

```text
AUTOFUSION_REPO_ROOT=/absolute/path/to/AutoFusion-bench
ANNOTATION_DB_PATH=/absolute/path/to/AutoFusion-bench/experiments/exp-002-diag-action-pilot/annotation_app/state/annotations.sqlite
ANNOTATION_MEDIA_MAP=/usr1/home/s125mdg43_10/datasets=/absolute/path/to/local/datasets;/usr1/home/s125mdg43_10/projects/AutoFusion-bench=/absolute/path/to/AutoFusion-bench
ANNOTATION_HOST=127.0.0.1
ANNOTATION_PORT=8000
```

如果媒体文件已经在 repo 里面，`ANNOTATION_MEDIA_MAP` 可以先不改。
如果页面显示 `media missing`，再让负责人给你本地媒体目录和映射关系。

## 5. 安装依赖

```bash
./scripts/bootstrap_local.sh
```

## 6. 严格检查

```bash
.venv/bin/python scripts/check_config.py --require-runtime-deps
```

## 7. 跑 smoke test

```bash
.venv/bin/python scripts/smoke_test.py
```

这一步必须通过。如果失败，把错误截图或日志发给负责人。

## 8. 启动网站

```bash
./scripts/run_local.sh
```

打开：

```text
http://127.0.0.1:8000
```

## 9. 导入 draft sheet

如果负责人给你的 mini-pilot sheet 是：

```text
experiments/exp-002-diag-action-pilot/annotations/mini_pilot.draft.jsonl
```

在网页里导入它，或用 CLI 导入：

```bash
cd experiments/exp-002-diag-action-pilot/annotation_app/backend
../.venv/bin/python -m app.cli \
  --db ../state/annotations.sqlite \
  import-sheet \
  --sheet ../../annotations/mini_pilot.draft.jsonl \
  --annotator <your_name>
```

## 10. 导出标注结果

网页里导出，或用 CLI：

```bash
cd experiments/exp-002-diag-action-pilot/annotation_app/backend
../.venv/bin/python -m app.cli \
  --db ../state/annotations.sqlite \
  export \
  --output ../../annotations/mini_pilot.<your_name>.jsonl
```

## 11. 验证导出

回到 repo 根目录：

```bash
cd /absolute/path/to/AutoFusion-bench
python3 experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py \
  --kind annotations \
  experiments/exp-002-diag-action-pilot/annotations/mini_pilot.<your_name>.jsonl
```

必须看到：

```text
ok: ... (annotations)
```
