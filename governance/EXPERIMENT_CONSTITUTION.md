# AutoFusion-Bench Experiment Constitution

> Status: Draft v0.1  
> Date: 2026-06-13  
> Purpose: define the working rules for experiments, files, archives, GitHub, and server space before repository cleanup.

## 1. Current Research North Star

The active project is:

> A benchmark / evaluation protocol for unreliable multimodal evidence governance, centered on whether multimodal large language models can turn evidence diagnosis into correct actions.

The active empirical hypothesis is:

> MLLMs may diagnose unreliable audio-video evidence but fail to route, answer, recover, or abstain correctly based on that diagnosis.

This is the **diagnosis-to-action gap**.

## 2. Claim Boundary

We must not claim:

- first missing-modality benchmark;
- first modality-diagnosis benchmark;
- first cross-modal conflict benchmark;
- a new multimodal fusion method;
- paper-level finding from 4-row smoke results.

We may claim, after sufficient evidence:

- we evaluate unreliable evidence governance as a diagnosis-to-action protocol;
- we separate evidence diagnosis, policy action, abstention, and final task execution;
- we test whether models act consistently on their own stated diagnosis;
- we analyze diagnosis-to-action failures under controlled audio-video evidence corruption.

## 3. Active Experiment

The active experiment is:

```text
experiments/exp-002-diag-action-pilot/
```

Scope:

- audio-video evidence governance under textual queries;
- AVQA / AVQA-videos first;
- MUSIC-AVQA as backup;
- MELD / MOSI / MOSEI / IEMOCAP are not main substrates for the current positive claim.

The active near-term target is:

```text
10 clean source items -> about 40 corrupted instances -> annotation -> Qwen panel -> scorer
```

The next scale target is:

```text
40 clean source items -> about 160 scored instances
```

## 4. Required Experiment Contract

Every active experiment must have:

- `hypothesis.md`
- `RUNBOOK.md`
- `config.yaml`
- `data/`
- `annotations/`
- `prompts/`
- `scripts/`
- `results.md`
- `results/`

Every annotation batch must follow:

```text
skills/autofusion-annotation/references/data_spec.md
```

Every experiment must keep outputs inside its own experiment folder. No shared top-level `outputs/`, `runs/`, `wandb/`, or checkpoint directories.

## 5. Gold Label Rule

Generated corruption metadata is a hint, not gold.

Examples:

- If a script mutes audio, the script can record that audio was muted.
- The script cannot decide whether that audio was necessary for the question.
- The script cannot decide whether video can recover the answer.
- The script cannot decide whether the row belongs in headline scoring.

Human or adjudicated labels are required for:

- clean-source acceptance;
- answerability after corruption;
- recoverability;
- oracle route;
- abstention;
- headline inclusion.

## 6. Metric Rule

Final answer accuracy is not the primary metric.

Primary governance metrics include:

- diagnosis macro-F1;
- recoverability macro-F1;
- policy action accuracy;
- conditional policy failure:

```text
P(policy_action_correct=false | triage_diagnosis_right=true)
```

- self-inconsistency rate;
- rule lift;
- false answer rate on unanswerable rows;
- governed success.

Policy action correctness and final-answer correctness must remain separate.

## 7. Active Workspace Rule

The active workspace should contain only:

1. current experiment files;
2. current project docs;
3. reusable tools;
4. current paper/story docs;
5. current handoffs;
6. lightweight memory and governance docs.

Historical material should be moved to `archive/` after approval.

Reproducible local artifacts should be deleted after approval, not archived.

## 8. Archive Rule

Archive means:

> The material is historically useful but not needed for the current execution path.

Archive candidates include:

- exp-001 code and experiment files;
- old May 2026 plans, decisions, handoffs, and reviews;
- old proposal HTML/Markdown/CSS;
- old reference pack manifests;
- old GPU setup notes not needed for current exp-002.

Archive does not mean:

- deleting evidence;
- losing reproducibility;
- moving active exp-002 assets;
- moving LabLock generated state manually.

## 9. Delete Rule

Delete candidates are reproducible local artifacts:

- `node_modules/`;
- `.venv/`;
- `dist/`;
- `__pycache__/`;
- `.DS_Store`;
- temporary outputs that are superseded by committed `results/`.

Before deleting, ensure:

- the dependency can be reinstalled;
- the result is either reproduced or not needed;
- no active script expects the local artifact path.

## 10. GitHub Rule

GitHub should represent a clean collaboration state.

Before pushing:

- ensure local `main` is intentional;
- decide whether cleanup happens on `main` or a `codex/repo-governance-cleanup` branch;
- avoid pushing large untracked PDFs/zips unless explicitly approved;
- do not push API keys, local `.env`, `.venv`, `node_modules`, or dataset media.

## 11. Server Rule

The server should not be treated as a dumping ground.

Server directories should mirror the same conceptual structure:

- active repo checkout;
- dataset cache outside Git;
- experiment-local outputs;
- archived historical runs in one archive root;
- no duplicated stale repo copies without an index.

Before server cleanup:

- regain SSH access;
- record current server git status;
- record current server size hotspots;
- confirm whether any files exist only on the server;
- sync or archive before deleting.

## 12. Documentation Rule

Current truth should live in files, not chat.

Canonical current docs:

- `governance/EXPERIMENT_CONSTITUTION.md`
- `governance/ROADMAP.md`
- `governance/2026-06-13-repo-audit.md`
- `handoffs/outgoing/2026-06-13-autofusion-project-overview.md`
- `memory/tasks/exp-002.md`

Top-level docs should be updated to point to these after approval:

- `README.md`
- `PROJECT.md`
- `INDEX.md`
- `claims.md`

## 13. Stop Conditions

Do not proceed with cleanup if:

- GitHub and local history differ in a way we have not decided how to handle;
- server SSH is down and the cleanup decision depends on server-only files;
- a file is old but still referenced by active scripts/tests;
- archival would move LabLock-managed files without understanding consequences;
- the user has not approved the cleanup category.

