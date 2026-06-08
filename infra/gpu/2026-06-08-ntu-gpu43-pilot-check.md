---
created: 2026-06-08
status: live-check
host: ntu-gpu43
---

# ntu-gpu43 Pilot Readiness Check

## Summary

`ntu-gpu43` is currently reachable and suitable as the execution server for the
next AutoFusion-Bench pilot, but the remote checkout is behind the current local
research plan and must be synchronized before starting a new experiment.

The server is the same direct GPU host used for the prior MELD exp-001 runs. It
is not a Slurm cluster.

## Live facts checked on 2026-06-08

- Hostname: `gpu43`
- User: `s125mdg43_10`
- GPU: 4 x NVIDIA RTX A5000, 24 GB each
- Current GPU usage:
  - GPU0: 12 MiB, 0%
  - GPU1: 12 MiB, 0%
  - GPU2: 12 MiB, 0%
  - GPU3: 562 MiB, 0%
- `/usr1`: 7.3T total, 4.6T used, 2.4T available
- Existing remote repo:
  - `/usr1/home/s125mdg43_10/projects/AutoFusion-bench`
  - current remote commit: `fd8b3f6`
  - untracked remote dirs: `.deps/`, `.venv/`
- Existing MELD data:
  - `/usr1/home/s125mdg43_10/datasets/MELD`
  - size: 33G
  - annotations dir exists
  - official features dir exists
  - official raw `MELD.Raw` dir exists
  - raw media / csv file count at maxdepth 3: 15911
- Existing tmux session:
  - `fiqa7207`, left untouched

## Interpretation

This host is ready for a small pilot from a hardware and storage perspective.
Use `/usr1/home/s125mdg43_10/projects/AutoFusion-bench` as the project root and
avoid writing datasets, checkpoints, or environments under `/` or `/tmp`.

However, the new diagnosis-to-action pilot should not use MELD as the main
positive substrate. Current project claim boundaries treat MELD as a diagnostic
or control substrate because prior exp-001 results showed text dominance. The
new pilot should primarily use AVQA / MUSIC-AVQA-style audio-video QA data, with
MELD retained only for environment reuse, comparison, or a side diagnostic if
needed.

## Required before launch

1. Sync the remote repo to the current local research plan and experiment code.
2. Create a new LabLock experiment folder for `diag-action-pilot`.
3. Stage AVQA / MUSIC-AVQA-style source data under `/usr1`.
4. Keep MELD paths available for control/diagnostic work, not as the main paper
   signal.
5. Start runs in a named tmux session and pin GPUs with `CUDA_VISIBLE_DEVICES`.

## Useful known paths

```text
Remote repo:
/usr1/home/s125mdg43_10/projects/AutoFusion-bench

Existing MELD root:
/usr1/home/s125mdg43_10/datasets/MELD

MELD annotations:
/usr1/home/s125mdg43_10/datasets/MELD/annotations

MELD official features:
/usr1/home/s125mdg43_10/datasets/MELD/official/features

MELD raw media:
/usr1/home/s125mdg43_10/datasets/MELD/official/raw/MELD.Raw
```
