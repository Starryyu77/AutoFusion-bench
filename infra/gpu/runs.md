# GPU Runs

| Date | Exp | Machine | GPU | Started | Expected | Status |
|---|---|---|---|---|---|---|
| 2026-05-14 | exp-001 | ntu-gpu43 | 4x RTX A5000 24GB; GPU0 busy at snapshot, GPU1-3 mostly idle | not submitted | 3 days after data preparation | local protocol runner implemented; real MELD producer pending |
| 2026-05-14 | exp-001 | ntu-gpu43 | remote fixture smoke only; no GPU training | not submitted | n/a | repo cloned to `/usr1/home/s125mdg43_10/projects/AutoFusion-bench`; remote tests and fixture smoke passed |
| 2026-05-14 | exp-001 | ntu-gpu43 | CPU/sklearn table producer; no GPU training | completed | n/a | MELD annotations/features/raw staged; full raw_stats six-table producer and analysis completed; protocol passed, benchmark signal failed |
| 2026-05-14 | exp-001 | ntu-gpu43 | CPU/OpenCV/sklearn table producer; no GPU training | completed | n/a | DNS recovered; full `cv2_stats + official_concat` producer tables verified; analysis completed with protocol passed, benchmark signal failed (`best_single_axis_oracle_regret_dt=0.740`), joint policy passed |
