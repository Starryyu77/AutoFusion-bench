# AutoFusion-Bench Roadmap

> Status: Draft v0.1
> Date: 2026-06-13
> Purpose: sequence cleanup, project governance, dataset work, and experiments without losing traceability.

## Phase 0: Freeze Rules Before Cleanup

Goal: make cleanup auditable instead of ad hoc.

Deliverables:

- `governance/2026-06-13-repo-audit.md`
- `governance/EXPERIMENT_CONSTITUTION.md`
- `governance/ROADMAP.md`

Decision gates:

- Decide whether cleanup will happen directly on `main` or on a branch such as `codex/repo-governance-cleanup`.
- Decide whether old PDFs/zips go to Git archive, Git LFS, Google Drive, or local-only archive.
- Decide whether to push current local `main` before cleanup. Local is currently ahead of GitHub by 17 commits.

Current status:

- Local scan complete.
- GitHub remote head confirmed.
- Server scan attempted but blocked by SSH timeout.
- Cleanup branch created: `codex/repo-governance-cleanup`.
- First local cleanup pass completed; see `governance/2026-06-13-cleanup-log.md`.

## Phase 1: Top-Level Documentation Reset

Goal: make the repo tell one story.

Update:

- `README.md`
- `PROJECT.md`
- `INDEX.md`
- `claims.md`

New story:

> AutoFusion-Bench evaluates unreliable multimodal evidence governance and diagnosis-to-action gap in MLLMs.

Top-level docs should point readers first to:

- `governance/EXPERIMENT_CONSTITUTION.md`
- `governance/ROADMAP.md`
- `handoffs/outgoing/2026-06-13-autofusion-project-overview.md`
- `experiments/exp-002-diag-action-pilot/`

Do not make `exp-001` appear as the current mainline.

Status: completed in first cleanup pass.

## Phase 1.5: Collaboration Operating Model

Goal: make delegation and review explicit before scaling from mini-pilot to
full pilot.

Canonical workflow:

- `governance/COLLABORATION_WORKFLOW.md`

Operating rule:

> The local workspace is the Decision Team workspace. Decision Team handles
> research judgment, planning, gold freeze, claim freeze, and final audit.
> Research Execution Team handles dataset work, corruption generation,
> annotation, and model runs through GitHub task cards and PRs. AI agents run
> formatting, validator, scorer, PR-summary, and audit checks against the same
> task-card contract.

Required before full 40-source pilot:

- each delegated task has a GitHub Issue or task card;
- every PR states inputs, outputs, validations, unresolved rows, and Drive media
  links;
- no large media is pushed to GitHub;
- `memory/tasks/exp-002.md` records current gate and next owner-facing action.

Status: constitution and collaboration workflow upgraded to v1.0 on 2026-06-19.

## Phase 2: Local Workspace Cleanup Plan

Goal: remove cognitive clutter while preserving traceability.

Proposed archive root:

```text
archive/2026-06-pre-exp002-reset/
```

Move only after approval:

- `experiments/exp-001-decision-surface-pilot/`
- `autofusion_bench/exp001/`
- `tests/test_exp001_protocol.py`
- old `decisions/2026-05-*`
- old `plans/2026-05-*`
- old `handoffs/incoming/2026-05-*`
- old `handoffs/outgoing/2026-05-*`
- old `infra/gpu/2026-05-*`
- old proposal files under `paper/2026-05-18-*`

Do not move yet:

- active exp-002 files;
- `skills/autofusion-annotation/`;
- LabLock generated state;
- `MAP.md`;
- current 2026-06 story/review/plan docs.

Delete only after approval:

- `node_modules/`;
- `.venv/`;
- `dist/`;
- `__pycache__/`;
- `.DS_Store`;
- stale local outputs superseded by committed `results/`.

Status: first cleanup pass completed. Active exp-002 outputs, `.env`, and local annotation state were intentionally left in place.

## Phase 3: GitHub Synchronization

Goal: make GitHub a clean collaboration base.

Current issue:

```text
local main ahead of origin/main by 17 commits
origin/main = a79c3564d8265d82ac2943202d3652f67b9e9f78
local HEAD = e3fe8f3
```

Options:

1. Push current local `main`, then cleanup in a new branch.
2. Create a cleanup branch locally, clean and commit, then push that branch for review.
3. If public history cleanliness matters, create a fresh clean branch with only current mainline files.

Recommendation:

> Use a cleanup branch first. Do not rewrite or force-push until the desired public shape is agreed.

## Phase 4: Server Audit and Cleanup

Goal: make `ntu-gpu43` match the same organization principles.

Blocked now:

```text
ssh ntu-gpu43 -> Operation timed out
```

When SSH recovers, run a read-only audit:

```bash
cd /usr1/home/s125mdg43_10/projects/AutoFusion-bench
git status --short
git rev-parse HEAD
du -sh ./* 2>/dev/null | sort -h
find . -maxdepth 2 -type d | sort
```

Classify server files into:

- active repo;
- dataset cache;
- exp-002 outputs;
- old exp-001 / May 2026 archive;
- local environment caches;
- server-only files that must be synced before deletion.

Do not delete server files until:

- current HEAD is known;
- server-only outputs are identified;
- dataset cache location is documented;
- cleanup target mirrors local/GitHub policy.

## Phase 5: 10-Source Mini-Pilot

Goal: validate the benchmark protocol on a small but real data batch.

Inputs:

- AVQA / AVQA-videos candidate pool;
- junior dataset-prep handoff;
- local annotation app;
- Qwen audio-video model panel.

Target:

- 80-120 candidate clean sources;
- 10 selected high-quality clean sources;
- about 40 corrupted instances;
- human-reviewed annotation export;
- Qwen diagnosis and real action;
- fixed-rule control;
- scorer metrics and qualitative failure notes.

Go / no-go:

- Continue if there are interpretable diagnosis-to-action failures or self-inconsistency cases.
- Redesign if examples are dominated by question-only shortcuts, ambiguous gold answers, or synthetic artifacts.

## Phase 6: 40-Source Pilot

Goal: get a meaningful empirical signal.

Target:

- 40 clean source items;
- about 160 scored instances;
- balanced source buckets;
- balanced corruption families;
- at least 2 audio-video-capable models;
- annotation agreement / adjudication report;
- main metrics table;
- qualitative error taxonomy.

Potential paper signal:

- conditional policy failure on a meaningful subset;
- self-inconsistency;
- rule lift;
- false-answer rate on unrecoverable cases;
- route-correct but answer-wrong separation.

## Phase 7: Text-Evidence Extension

Goal: decide whether the paper can honestly claim full text-audio-video evidence governance.

Candidate sources:

- subtitle datasets;
- ASR transcript from AVQA audio;
- caption-bearing video QA;
- TVQA / How2QA-style subsets.

Proceed only if:

- text evidence is truly evidence, not only question instruction;
- text corruption changes task evidence;
- annotation remains reliable;
- results add signal beyond audio-video governance.

## Phase 8: Paper and Release Preparation

Goal: move from pilot to publishable artifact.

Deliverables:

- benchmark card / datasheet;
- corruption generator documentation;
- annotation guideline;
- source/corruption manifest schema;
- scorer documentation;
- model panel details;
- main tables;
- ablation and controls;
- qualitative failure cases;
- reproducibility checklist.

Release policy:

- release scripts and metadata where allowed;
- release derived annotation labels where licensing allows;
- keep raw media download instructions rather than redistributing restricted videos;
- keep large PDFs, local caches, and API logs out of Git.
