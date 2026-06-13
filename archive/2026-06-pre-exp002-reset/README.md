# Archive: 2026-06 Pre-exp002 Reset

This archive contains project material that is historically useful but no longer part of the active AutoFusion-Bench execution path.

## Why This Exists

The active project direction is now:

> unreliable multimodal evidence governance and diagnosis-to-action gap in MLLMs.

The active experiment is:

```text
experiments/exp-002-diag-action-pilot/
```

Older exp-001 / MELD / May 2026 planning material was moved here to reduce active workspace noise while preserving traceability.

## Archived Groups

| Archive path | Original role |
|---|---|
| `experiments/exp-001-decision-surface-pilot/` | Historical MELD / decision-surface pilot. |
| `code/autofusion_bench/exp001/` | Historical exp-001 code. |
| `tests/test_exp001_protocol.py` | Historical exp-001 test. |
| `decisions/` | May 2026 decision notes. |
| `plans/` | May 2026 plans. |
| `handoffs/incoming/` | May 2026 incoming/expert direction notes. |
| `handoffs/outgoing/` | May 2026 outgoing handoffs plus old broad diagnostic benchmark handoff. |
| `infra/gpu/` | Old exp-001 GPU setup/cleanup notes. |
| `memory/tasks/` | Historical project-local memory notes. |
| `paper/` | Old May 2026 proposal artifacts. |

## Local-only Materials

Large reference packs were moved under:

```text
local-only/paper/
```

This directory is intentionally ignored by Git. It keeps local access to the old reference pack without pushing large PDFs/zips to GitHub.

## Not Archived

The following were intentionally not archived here:

- active exp-002 experiment files;
- active annotation app source code;
- active scorer / prompt / runner scripts;
- current project overview and junior handoff;
- LabLock generated state;
- reproducible local dependency folders such as `.venv/` and `node_modules/`;
- Python caches and `.DS_Store` files.
