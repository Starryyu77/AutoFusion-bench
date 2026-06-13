# Cleanup Log: 2026-06-13

> Branch: `codex/repo-governance-cleanup`
> Purpose: move historical material out of the active workspace, keep current exp-002 assets visible, and remove reproducible local caches.

## 1. Archive Root

Created:

```text
archive/2026-06-pre-exp002-reset/
```

Added archive index:

```text
archive/2026-06-pre-exp002-reset/README.md
```

## 2. Archived Tracked Historical Material

Moved to archive:

- `experiments/exp-001-decision-surface-pilot/`
- `autofusion_bench/exp001/`
- `tests/test_exp001_protocol.py`
- `decisions/2026-05-*`
- `plans/2026-05-*`
- `handoffs/incoming/2026-05-*`
- `handoffs/outgoing/2026-05-*`
- `infra/gpu/2026-05-14-*`
- `memory/tasks/exp-001.md`
- `memory/tasks/2026-05-17-multimodal-diagnostic-benchmark.md`

Also archived old untracked broad-diagnostic handoff/proposal files:

- `handoffs/outgoing/2026-05-17-diagnostic-benchmark-explainer.html`
- `handoffs/outgoing/2026-06-08-diagnostic-benchmark-expert-review.md`
- `paper/2026-05-18-diagnostic-benchmark-proposal.html`
- `paper/2026-05-18-diagnostic-benchmark-proposal.md`
- `paper/proposal.css`

## 3. Local-only Archive

Moved large old reference-pack material to:

```text
archive/2026-06-pre-exp002-reset/local-only/paper/
```

This includes:

- `autofusion-bench-reference-pack-2026-05-18.zip`
- old reference-pack PDFs and manifests.

This folder is intentionally ignored by Git.

## 4. Deleted Rebuildable Local Artifacts

Deleted:

- exp-001 archived `__pycache__/`;
- exp-001 archived ignored `outputs/`;
- active annotation app `.venv/`;
- active annotation app frontend `node_modules/`;
- active annotation app frontend `dist/`;
- Python `__pycache__/` folders;
- generated junior-package folder;
- `.DS_Store` files.

Not deleted:

- `experiments/exp-002-diag-action-pilot/outputs/`
- annotation app `.env`
- annotation app local `state/`

Reason: active exp-002 outputs and local annotation state may still be useful for immediate smoke/debug traceability. They remain ignored by Git.

## 5. Top-level Docs Rewritten

Updated:

- `README.md`
- `PROJECT.md`
- `INDEX.md`
- `claims.md`

These now point to the current evidence-governance / diagnosis-to-action gap story, exp-002, and governance docs.

## 6. Git Ignore Tightened

Updated `.gitignore` to ignore:

- `experiments/**/.env`
- `experiments/**/node_modules/`
- `experiments/**/dist/`
- `archive/**/local-only/`
- `archive/**/*.zip`

## 7. Remaining External Blocker

Server cleanup is not done.

The previous read-only scan failed:

```text
ssh ntu-gpu43 -> Operation timed out
```

Server cleanup remains blocked until SSH access is restored and server-only files are audited.
