# Repository Audit: 2026-06-13

> Scope: local repository, GitHub remote state, and attempted server check for `ntu-gpu43`.
> This is a scan report only. No cleanup, deletion, or archival move has been performed.
> Cleanup was later executed on branch `codex/repo-governance-cleanup`; see `governance/2026-06-13-cleanup-log.md`.

## 1. Current State Summary

The repository currently mixes three different layers:

1. **Active mainline**: `exp-002` diagnosis-to-action pilot for unreliable audio-video evidence governance under textual queries.
2. **Historical work**: `exp-001` MELD / decision-surface pilot and older May 2026 direction-setting documents.
3. **Local/untracked materials and runtime artifacts**: old proposal HTML/Markdown/reference packs, local dependency folders, caches, and generated packages.

The current main research story is no longer the broad May 2026 "modality triage + cross-modal recovery + budget routing" framing. After expert feedback, the active story is:

> Evidence governance and diagnosis-to-action gap: can MLLMs act correctly on their own diagnosis of unreliable multimodal evidence?

## 2. Git / Remote State

Local branch:

```text
main e3fe8f3 [origin/main: ahead 17]
```

GitHub remote:

```text
origin https://github.com/Starryyu77/AutoFusion-bench.git
origin/main = a79c3564d8265d82ac2943202d3652f67b9e9f78
```

Implication:

- Local `main` contains 17 commits not yet pushed to GitHub.
- Do not reorganize GitHub until we decide whether to push the current local main as-is, create a cleanup branch, or squash/rewrite a cleaner public state.

## 3. Server State

Attempted read-only SSH scan:

```text
ssh ntu-gpu43 ...
```

Result:

```text
ssh: connect to host gpu43.dynip.ntu.edu.sg port 22: Operation timed out
```

Implication:

- The server repository was not audited in this pass.
- Server cleanup must be a separate P0 gate after SSH connectivity is restored.
- Do not assume the server matches either local `main` or GitHub `origin/main`.

## 4. Local Size Hotspots

Top-level sizes from the local scan:

| Path | Approx size | Interpretation |
|---|---:|---|
| `paper/` | 90M | Mostly untracked reference pack PDFs/zip. Not needed in active workspace. |
| `experiments/` | 72M | Active `exp-002` plus ignored local annotation app dependencies. |
| `handoffs/` | 308K | Many historical handoffs; small but cognitively noisy. |
| `autofusion_bench/` | 308K | Mostly `exp001` code, now historical. |
| `memory/` | 64K | Project-local memory; keep active `exp-002`, archive old task notes later. |

Large local files over 5M:

| File | Size | Status / recommendation |
|---|---:|---|
| `paper/autofusion-bench-reference-pack-2026-05-18.zip` | 43M | Untracked; move to archive or external storage, not active workspace. |
| `paper/reference-pack/pdfs/R06-mmir-findings-acl2025.pdf` | 12M | Untracked reference material; archive/external storage. |
| `paper/reference-pack/pdfs/R08-smcir-aaai2026.pdf` | 12M | Untracked reference material; archive/external storage. |
| `annotation_app/frontend/node_modules/.../esbuild` | 9.5M each | Ignored local dependency cache; delete after confirming app can reinstall. |

## 5. Active Mainline: Keep in Working Tree

These files/directories are required for the current project direction:

| Path | Reason |
|---|---|
| `experiments/exp-002-diag-action-pilot/` | Active experiment: diagnosis-to-action pilot. |
| `skills/autofusion-annotation/` | Reusable annotation workflow and data contract. |
| `memory/tasks/exp-002.md` | Current state and next action truth source. |
| `handoffs/outgoing/2026-06-13-autofusion-project-overview.md` | Current self-contained project overview. |
| `handoffs/outgoing/2026-06-09-mini-pilot-junior-brief.md` | Current junior dataset-prep handoff. |
| `paper/2026-06-08-evidence-governance-story.md` | Current paper story after expert feedback. |
| `reviews/2026-06-08-pilot-expert-replies-synthesis.md` | Basis for pilot narrowing. |
| `reviews/2026-06-08-screening-scoring-guideline-expert-reply-synthesis.md` | Basis for annotation/scoring standard. |
| `plans/2026-06-08-exp-diagnosis-to-action-pilot.md` | Current exp-002 execution plan. |
| `infra/gpu/2026-06-08-ntu-gpu43-pilot-check.md` | Current server/gpu note for exp-002. |
| `AGENTS.md` | Repo instructions, LabLock and annotation workflow rules. |
| `.gitignore` | Needed, but should be tightened for local dependency artifacts. |

## 6. Keep but Update

These are conceptually useful but stale relative to the current story:

| Path | Issue | Recommendation |
|---|---|---|
| `README.md` | Still describes broad modality triage / recovery / budget routing. | Rewrite around evidence governance and diagnosis-to-action gap. |
| `PROJECT.md` | Last refreshed 2026-05-17; pre-exp-002 story. | Replace with current 2026-06-13 snapshot. |
| `INDEX.md` | Static map points to May direction-setting as primary. | Update to make exp-002 and governance docs first-class. |
| `claims.md` | Contains useful claim boundaries but still has older claim order. | Keep, update C004/C005/C006 around current pilot results and boundary. |
| `formalism.md` | May still be useful, but needs check against exp-002 scorer. | Review before keeping as normative. |

## 7. Archive Candidates

These are not useless, but should no longer occupy the active workspace once an archive plan is approved.

### 7.1 Historical experiment line

| Path | Recommendation |
|---|---|
| `experiments/exp-001-decision-surface-pilot/` | Move under `archive/2026-06-pre-exp002-reset/experiments/`. |
| `autofusion_bench/exp001/` | Move under archive with exp-001, or keep only if tests require it until tests are retired. |
| `tests/test_exp001_protocol.py` | Archive with exp-001 after confirming no active CI depends on it. |
| `memory/tasks/exp-001.md` | Archive or retain as historical memory only. |
| `.lablock/locks/exp-001.scope.lock` and `.lablock/changes/exp-001.changes.log` | LabLock-managed; do not manually move until LabLock policy is checked. |

### 7.2 Old decision / plan / review material

| Path group | Recommendation |
|---|---|
| `decisions/2026-05-*` | Archive as historical exp-001 / early-project decisions. |
| `plans/2026-05-*` | Archive except if directly cited by current overview. |
| `handoffs/incoming/2026-05-*` | Archive after preserving the accepted direction summary. |
| `handoffs/outgoing/2026-05-*` | Archive; keep only the current project overview active. |
| `infra/gpu/2026-05-*` | Archive old GPU setup/cleanup notes. |

### 7.3 Old proposal and reference pack

| Path | Recommendation |
|---|---|
| `paper/2026-05-18-diagnostic-benchmark-proposal.*` | Archive. Current story is `2026-06-08-evidence-governance-story.md`. |
| `paper/proposal.css` | Archive with old proposal HTML. |
| `paper/autofusion-bench-reference-pack-2026-05-18.zip` | Move out of active repo; ideally external storage or archive folder ignored by Git. |
| `paper/reference-pack/` | Move out of active repo; keep a manifest link if needed. |

## 8. Delete / Rebuild Candidates

These should generally not be archived because they are reproducible local artifacts:

| Path | Recommendation |
|---|---|
| `experiments/exp-002-diag-action-pilot/annotation_app/frontend/node_modules/` | Delete locally after confirming `npm install`/bootstrap works. |
| `experiments/exp-002-diag-action-pilot/annotation_app/.venv/` | Delete locally after confirming bootstrap works. |
| `experiments/exp-002-diag-action-pilot/annotation_app/frontend/dist/` | Delete locally unless needed for deployment. |
| `experiments/**/__pycache__/`, `tests/__pycache__/` | Delete locally. |
| `.DS_Store` files | Delete locally. |
| `experiments/*/outputs/` | Keep only if containing irreplaceable results; otherwise delete or move selected outputs into experiment `results/`. |

## 9. Proposed Archive Root

Use one root for historical but possibly useful project material:

```text
archive/
  2026-06-pre-exp002-reset/
    README.md
    experiments/
    code/
    handoffs/
    plans/
    decisions/
    reviews/
    paper/
    infra/
```

Rules:

- `archive/` is for traceable historical material, not caches.
- `archive/` should include an index explaining why each group was archived.
- Large PDFs/zips should preferably go to Drive or external storage, with only a manifest kept in Git.
- Do not archive `.lablock/state/*`, `MAP.md`, or other generated LabLock state manually.

## 10. Recommended Decision Before Cleanup

Before moving files, decide these policy questions:

1. Should GitHub receive the current local `main` first, or should cleanup happen on a separate branch before pushing?
2. Should old reference PDFs/zips live in Git, Git LFS, Drive, or a non-Git local archive?
3. Should `exp-001` be fully archived, or kept temporarily until tests are rewritten around exp-002?
4. Should top-level docs be rewritten before or after archival moves?
5. Should server cleanup wait until local/GitHub cleanup is merged, then mirror the cleaned state?
