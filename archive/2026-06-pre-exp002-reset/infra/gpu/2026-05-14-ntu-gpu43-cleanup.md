---
created: 2026-05-14
status: completed
host: ntu-gpu43
---

# ntu-gpu43 Cleanup Snapshot

## Scope

The cleanup targeted obsolete prior-experiment assets that should not be reused for the new AutoFusion-Bench repo.

## Server Facts

- Host: `ntu-gpu43`
- User: `s125mdg43_10`
- GPUs: 4 x NVIDIA RTX A5000, about 24 GB VRAM each
- Execution model: direct server, not Slurm
- Root filesystem `/`: 879 GB total, 174 GB free after cleanup
- Work filesystem `/usr1`: 7.3 TB total, 3.5 TB free after cleanup

## Removed

- `/usr1/home/s125mdg43_10/MultiBench`
- `/usr1/home/s125mdg43_10/AutoFusion_Workspace`
- `/usr1/home/s125mdg43_10/AutoFusion_Advanced`
- `/usr1/home/s125mdg43_10/autofusion_all`
- `/usr1/home/s125mdg43_10/DynMM`
- `/usr1/home/s125mdg43_10/experiments`
- `/usr1/home/s125mdg43_10/logs`
- `/usr1/home/s125mdg43_10/results`
- `/usr1/home/s125mdg43_10/Orthogonal_ELM_Transformers`
- `/usr1/home/s125mdg43_10/datasets/Orthogonal_ELM_Transformers`
- `/usr1/home/s125mdg43_10/projects/oelm`
- root-level temporary shell marker files such as `EOF`, `PYEOF`, `ENDPATCH`, and old DynMM helper scripts

Approximate removed size from pre-cleanup `du`: 211 GB.

## Left Untouched

- `projects/7207ass2_fiqa_aspect`
- `projects/p2_scienceqa`
- `mwt6126_member_c`
- `.cache`, `.local`, `.vscode-server`, `.trae-server`, and other environment/tooling directories

Reason: these assets are not clearly part of the obsolete AutoFusion/MultiBench experiment family and may support unrelated work or reusable environments.

## Current Implication for AutoFusion-Bench

The new project should treat `ntu-gpu43` as a clean execution target. Do not assume old MOSEI/MOSI/MultiBench assets exist. The first experiment must explicitly create or fetch its dataset, environment, outputs, and logs under a new `/usr1` project path.

The current visible active tmux pane is `fiqa7207`, with cwd under `projects/7207ass2_fiqa_aspect`; it was left untouched.

For future operations, use the global Codex skill `ntu-gpu43-operator`, not `ntu-cluster-operator`, because this host is a direct GPU server rather than a Slurm cluster.
