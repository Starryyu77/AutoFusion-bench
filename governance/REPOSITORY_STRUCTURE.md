# AutoFusion-Bench 仓库结构重设计

> Status: Design v0.2, first migration executed
> Date: 2026-06-19
> Purpose: 重新设计本地仓库和 GitHub 仓库结构，让 Decision Team、人类研究人员和 AI Agent 都能低成本协作。

## 1. 当前问题

现在仓库显得乱，不是因为文件数量本身，而是因为几类材料混在同一层：

- Decision Team 的研究判断、proposal、review、roadmap；
- Research Execution Team 的数据、标注、corruption、模型运行输出；
- AI Agent 需要读的规则、状态和恢复入口；
- 给专家/学弟/外部协作者的 handoff；
- 历史实验、旧 proposal、旧计划；
- 本地临时产物和大媒体。

结果是：

- 人类不知道“当前该看哪几个文件”；
- AI Agent 接手时要扫很多历史材料；
- GitHub 上看起来像多个项目混在一起；
- active experiment 和 archive 的边界不够直观；
- 本地 Decision Team 工作区被执行产物污染。

## 2. 设计原则

新的结构只服务一个目标：

> 让本地/GitHub 成为清晰的 Decision Team + collaboration hub，而不是实验堆场。

原则：

1. 顶层目录数量要少，每个目录职责单一；
2. 当前项目状态必须有唯一入口；
3. active experiment 必须和历史 archive 分开；
4. 大媒体和原始数据不进入 GitHub；
5. 给人看的 proposal、给执行人员的 task、给 Agent 的 workflow 要分层；
6. 迁移必须分阶段，不能一次性乱移动导致引用断裂；
7. 文件移动后必须更新 README、Roadmap、memory 和 handoff 指针。

## 3. 目标顶层结构

建议最终顶层结构如下：

```text
AutoFusion-bench/
  README.md
  AGENTS.md
  CLAUDE.md
  LICENSE
  pytest.ini

  governance/
  decision/
  experiments/
  paper/
  src/
  tools/
  tests/
  memory/
  archive/

  external/        # ignored, local-only
```

### 3.1 `governance/`

项目规则和审计入口。

保留：

```text
governance/
  EXPERIMENT_CONSTITUTION.md
  COLLABORATION_WORKFLOW.md
  ROADMAP.md
  REPOSITORY_STRUCTURE.md
  2026-*-repo-audit.md
  2026-*-cleanup-log.md
```

谁看：

- Decision Team；
- AI Agent；
- 新加入的研究人员。

用途：

- 先定规则，再移动文件；
- 判断哪些文件能进 GitHub；
- 判断哪些文件应该 archive；
- 判断什么事情需要 Decision Team freeze。

### 3.2 `decision/`

Decision Team 的研究判断材料。

目标结构：

```text
decision/
  handoffs/
  literature/
  ops/
  plans/
  reviews/
```

迁移来源：

| 当前目录 | 目标目录 |
|---|---|
| `plans/` | `decision/plans/` |
| `reviews/` | `decision/reviews/` |
| `lit/` | `decision/literature/` |
| `handoffs/` | `decision/handoffs/` |
| `infra/gpu/` | `decision/ops/gpu/` |
| 顶层散落 proposal | `paper/proposal/` |

职责：

- 放研究判断；
- 放专家意见整合；
- 放给学弟/专家/Agent 的 handoff；
- 不放模型输出；
- 不放大媒体；
- 不放 annotation export。

### 3.3 `experiments/`

只放 active 或明确可复现实验。

当前唯一 active experiment：

```text
experiments/exp-002-diag-action-pilot/
```

每个 experiment 内部必须保持：

```text
experiments/<exp-id>-<name>/
  README.md              # 该实验的当前入口，后续补
  RUNBOOK.md
  hypothesis.md
  config.yaml
  data/
  annotations/
  prompts/
  scripts/
  results.md
  results/
```

规则：

- 不在顶层创建 `outputs/`；
- 不在顶层创建 `runs/`；
- 不把大媒体提交到 Git；
- 每个实验自己管理 data/annotations/results；
- 不再把新实验散落到 `data/`、`evals/`、`models/` 顶层目录。

### 3.4 `paper/`

论文和投稿材料。

目标结构：

```text
paper/
  proposal/
  drafts/
  figures/
  tables/
  notes/
```

当前 proposal：

```text
paper/proposal/2026-06-19-evidence-governance-research-proposal.md
```

规则：

- paper 放写作材料，不放执行任务；
- expert review 放 `decision/reviews/`；
- task brief 放 `decision/handoffs/`；
- scorer raw output 放 experiment results，不放 paper。

### 3.5 `src/`

可复用 Python 包。

当前：

```text
autofusion_bench/
```

建议后续迁移：

```text
src/autofusion_bench/
```

迁移前要先检查 import、tests 和 packaging，不能直接移动。

### 3.6 `tools/`

项目工具和可复用 app。

建议目标：

```text
tools/
  annotation_app/
  skills/
```

当前 `skills/autofusion-annotation/` 可以先保留，等 active experiment 稳定后再决定是否迁移。annotation app 目前在 exp-002 内部，因为它和当前实验绑定较深，暂时不移动。

### 3.7 `memory/`

项目状态和恢复入口。

保留：

```text
memory/
  README.md
  tasks/exp-002.md
```

规则：

- 只记录当前状态、gate、恢复入口；
- 不写长 proposal；
- 不放临时讨论；
- 不替代 governance 和 paper。

### 3.8 `archive/`

历史材料统一归档。

规则：

- 旧实验、旧 proposal、旧 handoff、旧计划进入 archive；
- archive 不是垃圾桶，必须还能解释为什么归档；
- 可再生成的缓存不归档，直接删除；
- 大型 local-only archive 保持 ignored，不进 GitHub。

### 3.9 `external/`

本地临时交付入口，必须 ignored。

目标：

```text
external/
  incoming/
  drive-mirror/
  raw-packages/
```

作用：

- 存放别人发来的 zip；
- 临时解压媒体；
- 和 Google Drive 对齐；
- 不进入 GitHub。

这可以替代当前顶层 `产物/` 这种不可解释目录。

## 4. 当前目录迁移状态

### 4.1 已完成整理

| 原位置 | 当前处理 |
|---|---|
| 顶层重复 proposal | 已从 Git 视图移出；正式版本在 `paper/proposal/` |
| `lit/` | 已迁到 `decision/literature/` |
| `plans/` | 已迁到 `decision/plans/` |
| `reviews/` | 已迁到 `decision/reviews/` |
| `handoffs/` | 已迁到 `decision/handoffs/` |
| `infra/gpu/` | 已迁到 `decision/ops/gpu/` |
| `data/`, `models/`, `evals/`, `derivations/` | 顶层占位 README 已归档到 `archive/2026-06-pre-exp002-reset/root-placeholders/` |
| `产物/` | 不再使用；新外部材料进入 ignored `external/incoming/` |

### 4.2 暂时不要动

| 当前 | 原因 |
|---|---|
| `experiments/exp-002-diag-action-pilot/` | 当前 active experiment，先不能大规模移动 |
| `skills/autofusion-annotation/` | 已被 AGENTS.md 和 annotation workflow 引用 |
| `.lablock/` | LabLock 管理，不手动整理 |
| `MAP.md`, `experiments/matrix.md` | 项目规则禁止手动编辑 |
| `archive/2026-06-pre-exp002-reset/` | 已经是 cleanup 归档结果 |

### 4.3 需要审计后再动

| 当前 | 问题 |
|---|---|
| `autofusion_bench/` | 若迁到 `src/`，需要改 import 和 tests |
| `paper/` 下旧故事稿 | 暂保留为 paper-facing story；如进入正式论文写作再迁入 `paper/drafts/` |

## 5. 推荐迁移阶段

### Phase 0: Freeze current rules

已完成：

- `governance/EXPERIMENT_CONSTITUTION.md`
- `governance/COLLABORATION_WORKFLOW.md`
- `governance/REPOSITORY_STRUCTURE.md`

### Phase 1: Create new skeleton

新建但不立即迁移所有文件：

```text
decision/proposals/
decision/plans/
decision/reviews/
decision/literature/
decision/handoffs/
external/incoming/
paper/proposal/
paper/tables/
paper/figures/
```

Status: partially done on 2026-06-19. `decision/`, `paper/proposal/`,
`paper/tables/`, and ignored `external/` now exist. Empty future-only
subfolders such as `paper/figures/` may be added when needed.

### Phase 2: Move Decision Team documents

移动轻量文档：

- `lit/` -> `decision/literature/`
- `plans/` -> `decision/plans/`
- `reviews/` -> `decision/reviews/`
- `handoffs/` -> `decision/handoffs/`
- `infra/gpu/` -> `decision/ops/gpu/`
- loose proposal -> `paper/proposal/`

移动后必须更新：

- `README.md`
- `PROJECT.md`
- `INDEX.md`
- `governance/ROADMAP.md`
- `memory/tasks/exp-002.md`

Status: first pass done on 2026-06-19. `lit/`, `plans/`, `reviews/`,
`handoffs/`, and `infra/gpu/` were removed from the top-level view and their
current files were moved under `decision/`. Active exp-002 data and result
folders were not moved.

### Phase 3: Clean root

目标顶层只保留：

```text
README.md
AGENTS.md
CLAUDE.md
LICENSE
pytest.ini
governance/
decision/
experiments/
paper/
src/ or autofusion_bench/
tools/ or skills/
tests/
memory/
archive/
external/    # ignored
```

Status: partially done. Top-level placeholder `data/`, `models/`, `evals/`,
and `derivations/` README files were archived under
`archive/2026-06-pre-exp002-reset/root-placeholders/`. Package/code migration
from `autofusion_bench/` to `src/` is not yet executed.

### Phase 4: Active experiment README

给 exp-002 加一个简洁入口：

```text
experiments/exp-002-diag-action-pilot/README.md
```

说明：

- 当前目标；
- 当前 batch；
- 重要输入；
- 重要输出；
- 下一步；
- 谁负责执行；
- 哪些目录 ignored。

Status: done on 2026-06-19.

### Phase 5: Server mirror

服务器结构跟随同一逻辑：

```text
repo checkout
dataset cache outside Git
external media / raw packages outside Git
experiment-local outputs
archive root
```

不要让服务器成为第二个混乱版本。

## 6. 对人类协作的好处

整理后，你只需要看：

1. `README.md`：项目入口；
2. `governance/EXPERIMENT_CONSTITUTION.md`：规则；
3. `governance/COLLABORATION_WORKFLOW.md`：怎么协作；
4. `governance/ROADMAP.md`：当前阶段；
5. `paper/proposal/`：研究提案；
6. `experiments/exp-002-diag-action-pilot/README.md`：当前实验。

不会再需要从十几个顶层目录里猜哪个是当前主线。

## 7. 对 AI Agent 协作的好处

AI Agent 接手时固定读：

1. `AGENTS.md`
2. `governance/EXPERIMENT_CONSTITUTION.md`
3. `governance/COLLABORATION_WORKFLOW.md`
4. `governance/REPOSITORY_STRUCTURE.md`
5. `governance/ROADMAP.md`
6. `memory/tasks/exp-002.md`
7. 当前 task card

这样 Agent 不需要扫描全仓来猜边界，也不容易把 archive 当 active state。

## 8. Remaining Cleanup Recommendations

第一轮迁移已经完成，但不要立刻继续大规模移动 active experiment 或
package code。

建议后续另开小 PR 处理：

1. 如果需要，将 `autofusion_bench/` 迁到 `src/autofusion_bench/`，但要先更新 imports/tests；
2. 如果需要，把 `skills/autofusion-annotation/` 和 annotation app 抽成 `tools/`，但不要在 exp-002 gold freeze 前做；
3. 检查 `claims.md` / `formalism.md` / LabLock 相关文件是否应该保留在 root；
4. 等 server audit 恢复后，让服务器目录镜像同一结构。

这些后续项都可能影响 import、LabLock 或实验执行路径，不应和本次轻量文档迁移混在同一个 PR。
