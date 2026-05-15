#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/usr1/home/s125mdg43_10/projects/AutoFusion-bench}"
EXP_DIR="experiments/exp-001-decision-surface-pilot"
DATA_ROOT="/usr1/home/s125mdg43_10/datasets/MELD"

PRODUCER_OUT="${PRODUCER_OUT:-${EXP_DIR}/outputs/meld-producer-semvis-text-stress}"
ANALYSIS_OUT="${ANALYSIS_OUT:-${EXP_DIR}/outputs/meld-analysis-semvis-text-stress}"
CACHE_DIR="${CACHE_DIR:-${EXP_DIR}/outputs/meld-producer-semvis/feature-cache}"
LOG_DIR="${EXP_DIR}/logs"
LOG_FILE="${LOG_FILE:-${LOG_DIR}/semvis-text-stress-$(date +%Y%m%d-%H%M%S).log}"

cd "$ROOT"
mkdir -p "$LOG_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "[exp-001] semvis text-stress diagnostic run"
echo "root=$ROOT"
echo "producer_out=$PRODUCER_OUT"
echo "analysis_out=$ANALYSIS_OUT"
echo "cache_dir=$CACHE_DIR"
echo "log_file=$LOG_FILE"
echo "commit=$(git rev-parse --short HEAD)"
date

export PYTHONPATH="${PYTHONPATH:-.deps/opencv}"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-2}"

python3 -m autofusion_bench.exp001.run_meld_table_producer \
  --annotations-dir "${DATA_ROOT}/annotations" \
  --features-dir "${DATA_ROOT}/official/features" \
  --raw-root "${DATA_ROOT}/official/raw/MELD.Raw" \
  --video-source semvis_clip \
  --audio-source official_concat \
  --output "$PRODUCER_OUT" \
  --feature-cache-dir "$CACHE_DIR" \
  --seeds 0,1,2 \
  --semvis-model openai/clip-vit-base-patch32 \
  --semvis-frame-count 8 \
  --semvis-batch-frames 64 \
  --semvis-device cuda:0 \
  --degradation-profile text_stress

python3 -m autofusion_bench.exp001.run_decision_surface_pilot \
  --config "${EXP_DIR}/config.yaml" \
  --cost-table "${PRODUCER_OUT}/cost_table.csv" \
  --outcome-table "${PRODUCER_OUT}/outcome_table.csv" \
  --q-policy-map "${PRODUCER_OUT}/q_policy_map.csv" \
  --q-proxy-table "${PRODUCER_OUT}/q_proxy_table.csv" \
  --q-diagnostics "${PRODUCER_OUT}/q_diagnostics.csv" \
  --corruption-manifest "${PRODUCER_OUT}/corruption_manifest.csv" \
  --output-dir "$ANALYSIS_OUT"

echo "[exp-001] semvis text-stress diagnostic complete"
date
