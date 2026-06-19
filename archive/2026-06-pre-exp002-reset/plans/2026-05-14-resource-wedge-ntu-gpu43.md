---
created: 2026-05-14
status: proposed
---

# Plan: Resource Wedge for AutoFusion-Bench on ntu-gpu43

## Reframing

The real question is not yet "how do we run the whole benchmark?" It is:

> Can we cheaply prove that the reliability-budget surface produces different legal fusion-template decisions before spending compute on a full two-dataset benchmark?

This matters because AutoFusion-Bench is a decision benchmark, not a new NAS/router method. The first resource plan should therefore buy an outcome table, a cost table, and a falsifiable blind-spot signal with the smallest credible action space.

Working confirmation from the user: initialize the research plan, estimate resources first, and target `ntu-gpu43` as the execution server. This plan assumes that `ntu-gpu43` is acceptable for pilot and mainline runs unless a later live check finds contention or missing data licenses.

Hidden premises to challenge:

- The proposal's preferred main datasets, MELD and Hateful Memes, are ready to run on the server. A live read-only check did not find MELD or Hateful Memes assets. Older AutoFusion, MultiBench, DynMM, and MOSEI/MOSI experiment assets were intentionally deleted on 2026-05-14 because they belonged to prior experiments rather than this repo.
- The budget axis will automatically be meaningful on RTX A5000. It may not be; if all templates are legal under tight latency/memory budgets, the benchmark needs stricter budget tiers or a more expensive template registry.
- Reliability proxies are safe policy inputs. Some proxies may leak corruption severity too directly and turn the problem into a synthetic-regime classifier.

Alternative framings:

- Feature-level decision benchmark first: use cached or easily generated features to validate the fusion-template decision protocol. This is cheaper and cleaner, but claims must not imply end-to-end deployment latency.
- End-to-end budget benchmark first: include encoder cost, fusion cost, and routing overhead from the start. This supports stronger systems claims but is slower and more fragile because data ingestion and preprocessing become part of the critical path.

## Live Server Facts

Checked on 2026-05-14, Asia/Singapore time:

- Host target: `ntu-gpu43`, hostname `gpu43`, user `s125mdg43_10`.
- Execution model: direct server, not Slurm. `squeue`, `sacctmgr`, and `sinfo` are unavailable.
- GPUs: 4 x NVIDIA RTX A5000, each about 24 GB VRAM.
- Current GPU state at check time: near-idle, with about 0.8-2.2 GB used per GPU and 0% utilization.
- Storage before cleanup: `/usr1` had about 3.3 TB free; root `/` had about 174 GB free and should not hold datasets/checkpoints.
- Storage after cleanup: `/usr1` has about 3.5 TB free; root `/` still has about 174 GB free.
- Removed obsolete prior-experiment assets: `/usr1/home/s125mdg43_10/MultiBench`, `/usr1/home/s125mdg43_10/AutoFusion_Workspace`, `/usr1/home/s125mdg43_10/AutoFusion_Advanced`, `/usr1/home/s125mdg43_10/autofusion_all`, `/usr1/home/s125mdg43_10/DynMM`, `/usr1/home/s125mdg43_10/Orthogonal_ELM_Transformers`, `/usr1/home/s125mdg43_10/datasets/Orthogonal_ELM_Transformers`, `/usr1/home/s125mdg43_10/projects/oelm`, plus old experiment/log/result folders and temporary shell-marker files.
- Not found in quick server search: MELD and Hateful Memes assets.
- Left untouched because they appear unrelated or may support other work: `projects/7207ass2_fiqa_aspect`, `projects/p2_scienceqa`, `.cache`, `.local`, `.vscode-server`, and `.trae-server`.

Operational implication: run under `/usr1/home/s125mdg43_10/projects/AutoFusion-bench` or another `/usr1` project path, use `tmux` or managed background jobs, pin GPUs with `CUDA_VISIBLE_DEVICES`, and avoid putting environments, datasets, or outputs on `/` or `/tmp`.

## Hypotheses

1. **H1**: On a feature-level tri-modal pilot, the Kendall rank correlation between clean-loose template ranking and degraded-tight template ranking will be <= 0.3, showing a measurable rank inversion under joint reliability-budget stress.
2. **H2**: Under tight budget, a reliability-only policy will exceed the budget in >= 20% of evaluation cases, while a joint reliability-budget policy will keep budget violation rate <= 1% with <= 2 macro-F1 points utility loss against the feasible-template oracle.
3. **H3**: A one-dataset pilot outcome table with 7 fusion templates, 4 reliability-budget anchor cells, and 3 seeds can be completed on `ntu-gpu43` within 60 GPU-hours and 3 calendar days after fresh dataset acquisition/preparation is complete.
4. **H4**: A second modality family, preferably image-text, will preserve an oracle feasible regret gap of >= 3 AUROC points for at least one single-axis policy, ruling out the possibility that the effect is only a tri-modal affective-data artifact.

## Implementation Alternatives

### For H1

- Option A: fresh feature-level pilot on the first accessible tri-modal dataset, preferably MELD if data can be obtained cleanly, otherwise MOSEI/MOSI as a protocol-only fallback. Effort: 25-60 GPU-hours plus dataset acquisition/preparation, 2-4 calendar days on 1-4 A5000 GPUs. Risk: a MOSEI/MOSI fallback is not the proposal's preferred MELD dataset and supports protocol validation, not final paper coverage. Information value: fastest way to test whether the decision-table machinery and rank inversion metric produce a nontrivial signal.
- Option B: MELD feature-level ingestion plus template table. Effort: 60-120 GPU-hours, 3-5 calendar days after data is available. Risk: missing assets, audio/video preprocessing, and label/split alignment may dominate. Information value: stronger alignment with the proposed main tri-modal dataset.
- Option C: MELD end-to-end encoder-plus-fusion benchmark. Effort: 120-250 GPU-hours, 5-10 calendar days. Risk: 24 GB A5000 VRAM may constrain batch size and encoder choices; latency profiles may be noisy. Information value: supports a stronger budget claim that includes encoder cost.

### For H2

- Option A: Static cost profiling over cached feature tensors and fusion heads. Effort: 5-10 GPU-hours, 0.5-1 calendar day. Risk: cannot claim end-to-end latency. Information value: enough to define tight/loose budget tiers and test budget violation rate.
- Option B: Per-template measured latency and peak-memory profiling with encoders included. Effort: 30-80 GPU-hours, 2-4 calendar days per dataset. Risk: preprocessing and dataloader variance may obscure template cost differences. Information value: makes budget legality more defensible.
- Option C: Stress-test budget thresholds by sweeping synthetic latency/memory caps over the same outcome table. Effort: 2-5 GPU-hours, same day. Risk: less realistic if not anchored to measured hardware profiles. Information value: tells whether the benchmark has a meaningful budget axis before committing to expensive profiling.

### For H3

- Option A: One-dataset pilot with 7 templates, 4 anchor cells, 3 seeds, feature-level budget. Effort: 25-60 GPU-hours, 2-3 calendar days, about 20-80 GB new storage. Risk: only validates feasibility and signal shape. Information value: best information-per-cost wedge.
- Option B: Two-dataset feature-level package, tri-modal plus image-text. Effort: 120-250 GPU-hours, 5-9 calendar days, about 100-300 GB new storage if features are cached. Risk: Hateful Memes access and feature extraction may block. Information value: enough for a serious internal review of the benchmark story.
- Option C: Full paper-intended package with MELD and Hateful Memes, including encoder profiling and policy diagnostics. Effort: 250-600 GPU-hours, 10-18 calendar days on 4 x A5000 if data access is smooth. Risk: not safe to promise before dataset ingestion and first profiling pass. Information value: likely enough to decide whether the benchmark is paper-viable.

### For H4

- Option A: Hateful Memes feature extraction with frozen text and image encoders, then evaluate template decisions over image-only, text-only, late fusion, and cross-attention style fusion. Effort: 80-160 GPU-hours, 4-7 calendar days. Risk: dataset access, OCR/text preprocessing, and cross-modal template comparability. Information value: strongest second-family validation if assets are obtained cleanly.
- Option B: Use an already available image-text dataset as a temporary proxy if Hateful Memes access blocks. Effort: 40-100 GPU-hours, 2-5 calendar days. Risk: may weaken the conflict/moderation story. Information value: keeps the second-modality-family test alive.
- Option C: Defer image-text and do only tri-modal pilot plus a formal resource audit. Effort: 25-60 GPU-hours, 2-3 calendar days. Risk: cannot rule out affective-only artifact. Information value: acceptable only as a first LabLock experiment, not as a paper result package.

## Resource Estimate

Recommended first wedge:

| Scope | GPU-hours | Calendar time on ntu-gpu43 | Extra storage | Claim boundary |
|---|---:|---:|---:|---|
| Server setup + reproducibility smoke | 0-4 | 0.5 day | <5 GB | Environment readiness only |
| Fresh one-dataset feature-level pilot | 25-60 after data prep | 2-4 days | 20-100 GB | Protocol and signal validation |
| MELD feature-level main dataset | 60-120 | 3-5 days | 50-150 GB | Main tri-modal benchmark evidence |
| Hateful Memes feature-level second family | 80-160 | 4-7 days | 50-150 GB | Cross-family validation |
| Full feature-level two-dataset package | 120-250 | 5-9 days | 100-300 GB | Strong internal review package |
| End-to-end encoder-inclusive package | 250-600 | 10-18 days | 200-600 GB | Stronger budget legality claim |

`ntu-gpu43` is suitable for the first wedge and likely suitable for a feature-level paper package. It is less safe for a large end-to-end VLM-style benchmark if the selected encoders exceed 24 GB VRAM or if all four GPUs are shared.

## Recommendation

Start with **H3 Option A plus H1 Option A**: a fresh one-dataset feature-level pilot that builds the exact offline outcome-table, measured cost-table, oracle, and policy diagnostic pipeline. Prefer MELD if dataset acquisition is clean; use MOSEI/MOSI only as a protocol-only fallback. This remains the narrowest wedge, but after cleanup it requires explicit data preparation rather than reusing old server assets.

Do not treat the pilot as the final paper dataset. If the pilot fails to show rank inversion, budget infeasibility, or oracle headroom, the benchmark contract needs redesign before spending compute on MELD/Hateful Memes. If the pilot succeeds, move to MELD as the first main dataset and Hateful Memes as the second-family validation.

## Open Questions

- Are MELD and Hateful Memes already licensed/downloadable for this account, or must data acquisition be part of the first experiment?
- Should the first official benchmark claim be feature-level, end-to-end, or explicitly two-tiered?
- Which reliability proxies are allowed without leaking synthetic corruption labels too directly?
- What is the final frozen template registry for MELD and for Hateful Memes, and are all templates comparable in training budget?
- What minimum blind-spot effect size is paper-worthy: 2 macro-F1/AUROC points, 3 points, 5 points, or a normalized regret threshold?

## What's Next

- Run `/lab-plan-exp H3-option-A` to design the first resource-validation experiment.
- Or run `/lab-taste` if the main issue is whether this benchmark story is strong enough before spending compute.
- Or run `/lab-review --as=reviewer2` on this plan before committing `ntu-gpu43` resources.
